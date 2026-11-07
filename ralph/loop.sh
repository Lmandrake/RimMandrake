#!/bin/bash
# The Artisan loop on FlowWorks (owner 2026-11-07). Each pass is one fresh `claude -p` on ralph/PROMPT.md.
# It stops at ralph/DONE.md, at the token review point, on the file STOP in the log folder, or on 2 passes with no commit.
# The game is SteveDesktop's game A (ralph/steve.sh). The GSS loop goes first on it: while rm-ralph-gss-steve runs, or Steve
# does not answer, a pass that needs the game creates ralph/NEED_GAME and retires, and this shell waits, no model running.
cd "$(dirname "$0")/.." || exit 1
export PATH="$PATH:/mnt/c/Windows/System32:/mnt/c/Windows/System32/WindowsPowerShell/v1.0:/mnt/c/Users/Mandrake/AppData/Local/Microsoft/WindowsApps"
export RIMFLOW_SEAT=BENCH
export RM_GAME_INSTANCE=a
LOGS=/mnt/d/ClaudeWork/rimmandrake/ralph_flowworks
EVENTS=$LOGS/events.log
REVIEW_AT=${REVIEW_AT:-20000000}
OFFLINE_AT=${OFFLINE_AT:-4000000}
AHEAD="rm-ralph-gss-steve"   # loops ahead on game A; keep in step with AHEAD in ralph/game_gate.py
say() { echo "$(date '+%H:%M:%S PST') $*" >> "$EVENTS"; }
tally() { python3 ralph/tally.py "$LOGS"; }
ahead_running() { for u in $AHEAD; do systemctl --user is-active --quiet "$u" && return 0; done; return 1; }
game_busy() { ahead_running || ! ralph/steve.sh alive 2>/dev/null; }

n=$(ls "$LOGS"/pass_*.jsonl 2>/dev/null | wc -l)
fails=0; idle=0
say "LOOP start, $n passes on record, $(tally) tokens"
while :; do
  [ -e "$LOGS/STOP" ] && { say "LOOP stopped: STOP file"; exit 0; }
  [ -e ralph/DONE.md ] && { say "LOOP DONE_CLAIMED, $(tally) tokens"; exit 0; }
  t=$(tally)
  if [ "$t" -ge "$REVIEW_AT" ]; then say "LOOP PAUSED_FOR_REVIEW at $t tokens"; exit 0; fi
  if game_busy && [ "$t" -ge "$OFFLINE_AT" ]; then touch ralph/NEED_GAME; fi
  if [ -e ralph/NEED_GAME ]; then
    if game_busy; then
      say "GAME_WAIT: $(ahead_running && echo 'a loop ahead has game A' || echo 'Steve does not answer'), no model running, $t tokens"
      while game_busy; do
        [ -e "$LOGS/STOP" ] && { say "LOOP stopped: STOP file"; exit 0; }
        sleep 60
      done
      say "GAME_FREE: game A is ours and Steve answers"
    fi
    rm -f ralph/NEED_GAME
  fi
  n=$((n + 1))
  f=$(printf '%s/pass_%03d.jsonl' "$LOGS" "$n")
  head0=$(git rev-parse HEAD)
  say "PASS $n start, $t tokens so far"
  timeout 6h claude -p "$(cat ralph/PROMPT.md)" --model opus --effort xhigh --setting-sources project \
    --dangerously-skip-permissions --strict-mcp-config --output-format stream-json --verbose > "$f" 2> "$f.err"
  rc=$?
  say "PASS $n end, rc $rc, $(tally) tokens, head $(git log -1 --format=%h)"
  if [ "$rc" -ne 0 ]; then
    fails=$((fails + 1))
    [ "$fails" -ge 3 ] && { say "LOOP STOPPED: 3 failed passes in a row"; exit 1; }
    sleep 60
  else
    fails=0
    if [ "$(git rev-parse HEAD)" = "$head0" ] && [ ! -e ralph/NEED_GAME ] && [ ! -e ralph/DONE.md ]; then
      idle=$((idle + 1))
      [ "$idle" -ge 2 ] && { say "LOOP STOPPED: 2 passes in a row with no commit"; exit 1; }
    else
      idle=0
    fi
  fi
done
