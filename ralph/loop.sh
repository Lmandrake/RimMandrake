#!/bin/bash
# The Ralph loop on GimmeSomeSlack (owner 2026-11-06). Each pass is one fresh `claude -p` on ralph/PROMPT.md.
# It stops at ralph/DONE.md, at the token review point, on the file STOP in the log folder, or on 2 passes with no commit.
# Loops ahead in the queue have the one game first: a pass that needs it creates ralph/NEED_GAME and retires, and this shell waits, no model running.
cd "$(dirname "$0")/.." || exit 1
export PATH="$PATH:/mnt/c/Windows/System32:/mnt/c/Windows/System32/WindowsPowerShell/v1.0:/mnt/c/Users/Mandrake/AppData/Local/Microsoft/WindowsApps"
export RIMFLOW_SEAT=BENCH
LOGS=/mnt/d/ClaudeWork/rimmandrake/ralph_gss
EVENTS=$LOGS/events.log
REVIEW_AT=${REVIEW_AT:-20000000}
OFFLINE_AT=${OFFLINE_AT:-4000000}
say() { echo "$(date '+%H:%M:%S PST') $*" >> "$EVENTS"; }
tally() { python3 ralph/tally.py "$LOGS"; }
game_busy() { systemctl --user is-active --quiet rm-ralph-graffiti || systemctl --user is-active --quiet rm-ralph-pyrelands; }

n=$(ls "$LOGS"/pass_*.jsonl 2>/dev/null | wc -l)
say "LOOP start, $n passes on record, $(tally) tokens"
fails=0; idle=0
while :; do
  [ -e "$LOGS/STOP" ] && { say "LOOP stopped: STOP file"; exit 0; }
  [ -e ralph/DONE.md ] && { say "LOOP DONE_CLAIMED, $(tally) tokens"; exit 0; }
  t=$(tally)
  if [ "$t" -ge "$REVIEW_AT" ]; then say "LOOP PAUSED_FOR_REVIEW at $t tokens"; exit 0; fi
  if game_busy && [ "$t" -ge "$OFFLINE_AT" ]; then touch ralph/NEED_GAME; fi
  if [ -e ralph/NEED_GAME ]; then
    if game_busy; then
      say "GAME_WAIT: a loop ahead has the game, no model running, $t tokens"
      while game_busy; do
        [ -e "$LOGS/STOP" ] && { say "LOOP stopped: STOP file"; exit 0; }
        sleep 60
      done
      say "GAME_FREE: loops ahead have ended"
    fi
    rm -f ralph/NEED_GAME
  fi
  head0=$(git rev-parse HEAD)
  n=$((n + 1))
  f=$(printf '%s/pass_%03d.jsonl' "$LOGS" "$n")
  say "PASS $n start, $t tokens so far"
  timeout 6h claude -p "$(cat ralph/PROMPT.md)" --model opus --setting-sources project \
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
