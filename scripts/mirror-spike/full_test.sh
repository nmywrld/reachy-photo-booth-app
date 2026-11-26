#!/usr/bin/env bash
# Full mirror spike: build image, profile, run the backend/dtype matrix, then the best
# config alone vs. during back-to-back Flux renders. Results -> out/results.jsonl
# Needs the llm and image-generator containers up (docker compose up -d llm image-generator).
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cd "$here"
out="$here/out"; mkdir -p "$out"
res="$out/results.jsonl"; : > "$res"
IN=/work/person.png

docker build -q -t mirror-spike . >/dev/null || { echo "image build failed"; exit 1; }

echo "== profile"
./run.sh --script profile_conv.py 2>&1 | grep -E "TFLOPS|ms|cudnn" | tee "$out/profile.txt"

run() {  # run <label> <bench args...>
  local label=$1; shift
  local log="$out/$label.log"
  ./run.sh --input $IN --tag "_$label" "$@" > "$log" 2>&1
  local line; line=$(grep '^{"backend' "$log" | tail -1)
  if [[ -n "$line" ]]; then
    echo "$line" | tee -a "$res"
  else
    local err; err=$(grep -E "Error|error:" "$log" | tail -1 | cut -c1-200)
    echo "{\"label\": \"$label\", \"failed\": \"${err//\"/\'}\"}" | tee -a "$res"
  fi
}

echo "== matrix"
for b in eager compile trt; do
  for d in fp16 bf16; do run "${b}_${d}_s1" --backend $b --dtype $d --steps 1; done
done

best=$(python3 - "$res" <<'EOF'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if '"fps"' in l]
b = max(rows, key=lambda r: r["fps"])
print(b["backend"], b["dtype"])
EOF
)
read -r bb bd <<<"$best"
echo "== best: $bb $bd"
run "${bb}_${bd}_s2" --backend $bb --dtype $bd --steps 2
for s in 0.35 0.65; do run "${bb}_${bd}_s1_str$s" --backend $bb --dtype $bd --steps 1 --strength $s; done

echo "== concurrent with Flux"
python3 flux_load.py --image person.png --seconds 100000 --steps 20 > "$out/flux_alone.log" 2>&1 &
fp=$!; sleep 90; kill $fp 2>/dev/null; wait $fp 2>/dev/null
echo "flux alone: $(cat "$out/flux_alone.log" | tr '\n' ' ')"
python3 flux_load.py --image person.png --seconds 100000 --steps 20 > "$out/flux_concurrent.log" 2>&1 &
fp=$!; sleep 5
run "${bb}_${bd}_s1_with_flux" --backend $bb --dtype $bd --steps 1 --frames 1200
kill $fp 2>/dev/null; wait $fp 2>/dev/null
echo "flux during mirror: $(cat "$out/flux_concurrent.log" | tr '\n' ' ')"
echo "== done"
