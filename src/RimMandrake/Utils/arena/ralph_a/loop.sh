#!/usr/bin/env bash
# ralph_a loop entry (the supervisor unit's ExecStart). Harness code: runs from OUTSIDE the arm clone.
#   RALPH_A_ROOT       the ralph_a arm clone (required)
#   RALPH_A_CTL        control dir outside git (default /mnt/d/ClaudeWork/rimmandrake/ralph_a)
#   RALPH_A_TASKS      comma-separated frozen task ids, worked in order (required)
#   RALPH_A_MODEL_CMD  the model invocation (argv; prompt on stdin). No default: unset refuses.
#   RALPH_A_RUNWAY_MIN runway floor (default 0.15); RALPH_A_PASS_TIMEOUT_S per-pass kill (default 5400 s)
#   RALPH_A_TESTER_TMP base of the tester's fresh private root (default the system temp dir; never inside
#                      the ctl dir, the clone or the harness checkout); RALPH_A_TESTER_SANDBOX auto|bwrap|none
#                      (bubblewrap; auto uses it when present); RALPH_A_TESTER_HIDE extra :-separated paths hidden
#                      from the tester; RALPH_A_TESTER_ENV_KEEP comma-separated extra env names the tester keeps
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# a missing setting exits 2 (not bash's 127 from ${v:?}): the unit template stops restarting on 2 (RestartPreventExitStatus)
[ -n "${RALPH_A_ROOT:-}" ] || { echo "set RALPH_A_ROOT to the ralph_a arm clone"; exit 2; }
[ -n "${RALPH_A_TASKS:-}" ] || { echo "set RALPH_A_TASKS to the frozen task ids"; exit 2; }
[ -n "${RALPH_A_MODEL_CMD:-}" ] || { echo "set RALPH_A_MODEL_CMD to the model invocation"; exit 2; }
ctl="${RALPH_A_CTL:-/mnt/d/ClaudeWork/rimmandrake/ralph_a}"
mkdir -p "$ctl"
cd "$here" || exit 2                       # never inside the arm clone: the event writer refuses that
top="$(git -C "$RALPH_A_ROOT" rev-parse --show-toplevel 2>/dev/null)" || { echo "not a git clone: $RALPH_A_ROOT"; exit 2; }
[ "$(realpath "$top")" = "$(realpath "$RALPH_A_ROOT")" ] || { echo "RALPH_A_ROOT is not a clone root: $RALPH_A_ROOT"; exit 2; }
release() { (cd "$RALPH_A_ROOT" && python3 src/RimMandrake/rimflow/cli.py bridge release --mine) >/dev/null 2>&1 || true; }
trap release EXIT
exec 9>"$ctl/loop.sh.lock"
flock -n 9 || { echo "another ralph_a loop.sh is running ($ctl/loop.sh.lock)"; exit 3; }
unset RM_ARM
python3 "$here/../ralph_a_loop.py" run --root "$RALPH_A_ROOT" --ctl "$ctl" --tasks "$RALPH_A_TASKS"
