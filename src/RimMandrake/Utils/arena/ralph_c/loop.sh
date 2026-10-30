#!/usr/bin/env bash
# ralph_c builder loop entry (rm-ralph-loop@a1 / @a2: the instance is the member). Harness code: runs OUTSIDE the clone.
#   $1 / RALPH_C_MEMBER   a1 | a2 (required)
#   RALPH_C_ROOT_<A1|A2>  that member's arm clone (required), RALPH_C_TASKS (frozen ids), RALPH_C_AREAS (areas.json)
#   RALPH_C_MODEL_CMD     the model invocation (argv; prompt on stdin). No default: unset refuses.
#   RALPH_C_CTL           control root (default /mnt/d/ClaudeWork/rimmandrake/ralph_c); this member uses <ctl>/<member>
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
member="${1:-${RALPH_C_MEMBER:-}}"
case "$member" in a1|a2) ;; *) echo "member must be a1 or a2, got '$member'"; exit 2;; esac
rootvar="RALPH_C_ROOT_${member^^}"
root="${!rootvar:-}"
[ -n "$root" ] || { echo "set $rootvar to the $member arm clone"; exit 2; }
: "${RALPH_C_TASKS:?set RALPH_C_TASKS to the frozen task ids}"
ctl="${RALPH_C_CTL:-/mnt/d/ClaudeWork/rimmandrake/ralph_c}/$member"
mkdir -p "$ctl"
cd "$here" || exit 2
top="$(git -C "$root" rev-parse --show-toplevel 2>/dev/null)" || { echo "not a git clone: $root"; exit 2; }
[ "$(realpath "$top")" = "$(realpath "$root")" ] || { echo "$rootvar is not a clone root: $root"; exit 2; }
release() { (cd "$root" && python3 src/RimMandrake/rimflow/cli.py bridge release --mine) >/dev/null 2>&1 || true; }
trap release EXIT
exec 9>"$ctl/loop.sh.lock"
flock -n 9 || { echo "another ralph_c $member loop.sh is running ($ctl/loop.sh.lock)"; exit 3; }
unset RM_ARM
python3 "$here/../ralph_c_loop.py" run --member "$member" --root "$root" --ctl "$ctl" --tasks "$RALPH_C_TASKS"
