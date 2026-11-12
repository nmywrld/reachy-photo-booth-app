#!/usr/bin/env bash
# Point the photo booth at the wireless Reachy Mini's current IP.
#
#   scripts/reachy-ip.sh              # find the robot by mDNS (reachy-mini.local)
#   scripts/reachy-ip.sh 10.0.0.42    # use this IP
#   scripts/reachy-ip.sh --no-restart # only update .env
#
# Writes REACHY_HOST to the repository's .env, checks the robot answers, then
# recreates the two services that use it (camera, robot-controller).
# Containers can't resolve mDNS names, so the IP is resolved here on the host.
# Override the name with REACHY_MDNS_NAME=my-robot.local.
set -euo pipefail

cd "$(dirname "$0")/.."
ENV_FILE=.env
NAME="${REACHY_MDNS_NAME:-reachy-mini.local}"
RESTART=1
IP=""

for arg in "$@"; do
    case "$arg" in
        --no-restart) RESTART=0 ;;
        -h|--help) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) IP="$arg" ;;
    esac
done

if [ -z "$IP" ]; then
    echo "Looking up $NAME ..."
    if command -v avahi-resolve >/dev/null 2>&1; then
        IP=$(timeout 5 avahi-resolve -4 -n "$NAME" 2>/dev/null | awk '{print $2}' | head -1 || true)
    fi
    if [ -z "$IP" ]; then
        IP=$(getent ahostsv4 "$NAME" 2>/dev/null | awk '{print $1; exit}' || true)
    fi
    if [ -z "$IP" ]; then
        echo "Could not resolve $NAME. Is the robot on the same network?" >&2
        echo "Pass the IP instead: $0 <robot-ip>  (shown in the Reachy Mini app/dashboard)" >&2
        exit 1
    fi
fi

if ! [[ "$IP" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]]; then
    echo "Not an IPv4 address: $IP" >&2
    exit 1
fi
echo "Robot IP: $IP"

if curl -fsS -m 5 "http://$IP:8000/api/daemon/status" >/dev/null 2>&1; then
    echo "  daemon (port 8000): OK"
else
    echo "  warning: robot daemon not answering at http://$IP:8000" >&2
fi
if curl -fsS -m 5 "http://$IP:8042/health" >/dev/null 2>&1; then
    echo "  reachy_booth app (port 8042): OK"
else
    echo "  warning: reachy_booth app not answering at http://$IP:8042 - start it from the robot dashboard" >&2
fi

touch "$ENV_FILE"
OLD=$(grep -E '^REACHY_HOST=' "$ENV_FILE" | head -1 | cut -d= -f2- || true)
if grep -qE '^REACHY_HOST=' "$ENV_FILE"; then
    sed -i "s/^REACHY_HOST=.*/REACHY_HOST=$IP/" "$ENV_FILE"
else
    printf '\n# Wireless Reachy Mini IP (scripts/reachy-ip.sh)\nREACHY_HOST=%s\n' "$IP" >> "$ENV_FILE"
fi
echo "Set REACHY_HOST=$IP in $ENV_FILE${OLD:+ (was $OLD)}"

if [ "$RESTART" -eq 1 ]; then
    dc() {
        if docker info >/dev/null 2>&1; then
            docker compose "$@"
        else
            sg docker -c "docker compose $*"  # user not in the docker group yet
        fi
    }
    # Only recreate what is already running; a stopped stack picks the new
    # value up on its next `docker compose up -d`.
    RUNNING=$(dc ps --status running --services 2>/dev/null | grep -xE 'camera|robot-controller' | tr '\n' ' ' || true)
    if [ -n "$RUNNING" ]; then
        echo "Recreating: $RUNNING"
        dc up -d --no-deps --force-recreate $RUNNING  # config-file changes alone do not trigger a recreate
    else
        echo "Stack not running; start it with: docker compose up -d"
    fi
fi
