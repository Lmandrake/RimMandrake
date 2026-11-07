# Sourced by ralph/steve.sh. A machine reboot drops EVERY game on SteveDesktop, so `reboot` refuses while another
# instance than this wrapper's own is running (owner 2026-11-07: "Don't keep rebooting it."). Test: ralph/reboot_guard_test.sh
# reboot_guard: exit 0 = go ahead, 1 = refused. Needs `on` (runs a command on Steve in this loop's clone); fails closed.
reboot_guard() {
    [ "${STEVE_REBOOT_BOTH:-}" = 1 ] && { echo "reboot: STEVE_REBOOT_BOTH=1, rebooting both games on purpose" >&2; return 0; }
    local own="${RM_GAME_INSTANCE:-a}" out line busy=""
    out=$(on 'python3 src/RimMandrake/Utils/game_instance.py status' 2>/dev/null | tr -d '\r') \
        || { echo "reboot: REFUSED, could not read which games run on SteveDesktop (fails closed). Restart your own game by pid instead: ralph/steve.sh down; ralph/steve.sh up." >&2; return 1; }
    [ -n "$out" ] || { echo "reboot: REFUSED, the instance status was empty (fails closed)." >&2; return 1; }
    while IFS= read -r line; do
        set -- $line
        [ -n "${1:-}" ] && [ "$1" != "$own" ] && [ "${2:-}" = running ] && busy="$busy
  instance $1, pid ${4:-?}, port ${6:-?}"
    done <<< "$out"
    [ -z "$busy" ] && return 0
    echo "reboot: REFUSED, a reboot would drop another game on SteveDesktop:$busy
Restart your own game by pid instead (ralph/steve.sh down; ralph/steve.sh up). To reboot both on purpose: STEVE_REBOOT_BOTH=1 ralph/steve.sh reboot" >&2
    return 1
}
