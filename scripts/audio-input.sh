#!/usr/bin/env bash
# Choose which host microphone speech-to-text records from.
#
#   scripts/audio-input.sh                 # list microphones and the current choice
#   scripts/audio-input.sh default         # follow the host's default input
#   scripts/audio-input.sh bluetooth       # first Bluetooth microphone (bluez)
#   scripts/audio-input.sh <name|text>     # microphone whose name/description matches
#
# Writes AUDIO_SOURCE to the repository's .env and recreates speech-to-text
# if it is running.
set -euo pipefail

cd "$(dirname "$0")/.."
ENV_FILE=.env

# "node.name<TAB>description" for every input (source) PipeWire knows about.
# Monitors of outputs are left out: they record what the speakers play.
list_sources() {
    pw-dump 2>/dev/null | python3 -c '
import json, sys
for o in json.load(sys.stdin):
    p = (o.get("info") or {}).get("props") or {}
    if p.get("media.class") == "Audio/Source" and not p.get("node.name", "").endswith(".monitor"):
        print(p.get("node.name", ""), p.get("node.description", ""), sep="\t")
'
}

host_default() {
    pactl get-default-source 2>/dev/null || true
}

current=$(grep -E '^AUDIO_SOURCE=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2- || true)

if [ $# -eq 0 ]; then
    def=$(host_default)
    echo "Microphones (use the name, or any part of the name/description):"
    list_sources | while IFS=$'\t' read -r name desc; do
        mark=" "; [ "$name" = "$current" ] && mark="*"
        tag=""; [ "$name" = "$def" ] && tag="  (host default)"
        printf ' %s %-60s %s%s\n' "$mark" "$name" "$desc" "$tag"
    done
    echo
    echo "Current AUDIO_SOURCE: ${current:-<empty> (host default input${def:+: $def})}"
    if [ -z "$current" ] && [[ "$def" == *.monitor ]]; then
        echo "warning: that default records the speakers, not a microphone. Pick one: $0 <name>" >&2
    fi
    exit 0
fi

case "$1" in
    -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    default|"") target=""
        case "$(host_default)" in
            *.monitor) echo "warning: the host's default input is $(host_default), which records the speakers, not a microphone." >&2
                       echo "         Pick a microphone instead (run $0 to list them), or change the host default input." >&2 ;;
        esac ;;
    bluetooth|bt) target=$(list_sources | awk -F'\t' '$1 ~ /^bluez_input/ {print $1; exit}')
        if [ -z "$target" ]; then
            echo "No Bluetooth microphone connected. Pair/connect it (headset profile) first." >&2
            exit 1
        fi ;;
    *) target=$(list_sources | awk -F'\t' -v q="$1" 'tolower($1) == tolower(q) {print $1; exit}')
        if [ -z "$target" ]; then
            matches=$(list_sources | awk -F'\t' -v q="$1" 'index(tolower($0), tolower(q)) {print $1}')
            count=$(printf '%s' "$matches" | grep -c . || true)
            if [ "$count" -eq 1 ]; then
                target=$matches
            elif [ "$count" -gt 1 ]; then
                echo "\"$1\" matches several microphones; be more specific:" >&2
                printf '  %s\n' $matches >&2
                exit 1
            else
                echo "No microphone matches \"$1\". Run $0 to list them." >&2
                exit 1
            fi
        fi ;;
esac

touch "$ENV_FILE"
if grep -qE '^AUDIO_SOURCE=' "$ENV_FILE"; then
    sed -i "s|^AUDIO_SOURCE=.*|AUDIO_SOURCE=$target|" "$ENV_FILE"
else
    printf '\n# Microphone for speech-to-text (scripts/audio-input.sh)\nAUDIO_SOURCE=%s\n' "$target" >> "$ENV_FILE"
fi
echo "Set AUDIO_SOURCE=${target:-<empty> (host default input)}"

dc() {
    if docker info >/dev/null 2>&1; then
        docker compose "$@"
    else
        sg docker -c "docker compose $*"  # user not in the docker group yet
    fi
}
if dc ps --status running --services 2>/dev/null | grep -qx speech-to-text; then
    echo "Recreating speech-to-text ..."
    dc up -d --no-deps --force-recreate speech-to-text  # config-file changes alone do not trigger a recreate
else
    echo "speech-to-text not running; the next 'docker compose up -d' uses it."
fi
