#!/usr/bin/env bash
# Choose which host speaker the robot's voice plays on.
#
#   scripts/audio-output.sh                 # list outputs and the current choice
#   scripts/audio-output.sh bluetooth       # first Bluetooth output (bluez)
#   scripts/audio-output.sh default         # follow the host's default output
#   scripts/audio-output.sh <name|text>     # output whose name/description matches
#
# Writes AUDIO_SINK to the repository's .env and recreates animation-compositor
# (the service that plays the voice) if it is running.
set -euo pipefail

cd "$(dirname "$0")/.."
ENV_FILE=.env

# "node.name<TAB>description" for every output (sink) PipeWire knows about.
list_sinks() {
    pw-dump 2>/dev/null | python3 -c '
import json, sys
for o in json.load(sys.stdin):
    p = (o.get("info") or {}).get("props") or {}
    if p.get("media.class") == "Audio/Sink":
        print(p.get("node.name", ""), p.get("node.description", ""), sep="\t")
'
}

current=$(grep -E '^AUDIO_SINK=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2- || true)

if [ $# -eq 0 ]; then
    echo "Outputs (use the name, or any part of the name/description):"
    list_sinks | while IFS=$'\t' read -r name desc; do
        mark=" "; [ "$name" = "$current" ] && mark="*"
        printf ' %s %-70s %s\n' "$mark" "$name" "$desc"
    done
    echo
    echo "Current AUDIO_SINK: ${current:-<empty> (host default output)}"
    exit 0
fi

case "$1" in
    -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    default|"") target="" ;;
    bluetooth|bt) target=$(list_sinks | awk -F'\t' '$1 ~ /^bluez_output/ {print $1; exit}')
        if [ -z "$target" ]; then
            echo "No Bluetooth output connected. Pair/connect the speaker first." >&2
            exit 1
        fi ;;
    *) target=$(list_sinks | awk -F'\t' -v q="$1" 'tolower($1) == tolower(q) {print $1; exit}')
        if [ -z "$target" ]; then
            matches=$(list_sinks | awk -F'\t' -v q="$1" 'index(tolower($0), tolower(q)) {print $1}')
            count=$(printf '%s' "$matches" | grep -c . || true)
            if [ "$count" -eq 1 ]; then
                target=$matches
            elif [ "$count" -gt 1 ]; then
                echo "\"$1\" matches several outputs; be more specific:" >&2
                printf '  %s\n' $matches >&2
                exit 1
            else
                echo "No output matches \"$1\". Run $0 to list them." >&2
                exit 1
            fi
        fi ;;
esac

touch "$ENV_FILE"
if grep -qE '^AUDIO_SINK=' "$ENV_FILE"; then
    sed -i "s|^AUDIO_SINK=.*|AUDIO_SINK=$target|" "$ENV_FILE"
else
    printf '\n# Speaker for the robot voice (scripts/audio-output.sh)\nAUDIO_SINK=%s\n' "$target" >> "$ENV_FILE"
fi
echo "Set AUDIO_SINK=${target:-<empty> (host default output)}"

dc() {
    if docker info >/dev/null 2>&1; then
        docker compose "$@"
    else
        sg docker -c "docker compose $*"  # user not in the docker group yet
    fi
}
if dc ps --status running --services 2>/dev/null | grep -qx animation-compositor; then
    echo "Recreating animation-compositor ..."
    dc up -d --no-deps --force-recreate animation-compositor  # config-file changes alone do not trigger a recreate
else
    echo "animation-compositor not running; the next 'docker compose up -d' uses it."
fi
