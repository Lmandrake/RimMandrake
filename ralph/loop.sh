#!/bin/bash
# The Ralph loop on Graffiti (owner 2026-11-06). Each pass is one fresh `claude -p` on ralph/PROMPT.md.
# It stops at ralph/DONE.md, at the token review point, or on the file STOP in the log folder.
cd "$(dirname "$0")/.." || exit 1
LOGS=/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti
EVENTS=$LOGS/events.log
REVIEW_AT=${REVIEW_AT:-20000000}
say() { echo "$(date '+%H:%M:%S PST') $*" >> "$EVENTS"; }

gss_has_game() {   # the Gimme Some Slack loop lets go when its log's last line says GAME_WAIT
  python3 ralph/game_gate.py --held
}

tally() {   # weighted tokens over every pass: input + output + cache writes + cache reads / 10
  python3 ralph/tally.py "$LOGS"
}

n=$(ls "$LOGS"/pass_*.jsonl 2>/dev/null | wc -l)
say "LOOP start, $n passes on record, $(tally) tokens"
while :; do
  [ -e "$LOGS/STOP" ] && { say "LOOP stopped: STOP file"; exit 0; }
  [ -e ralph/DONE.md ] && { say "LOOP DONE_CLAIMED, $(tally) tokens"; exit 0; }
  t=$(tally)
  if [ "$t" -ge "$REVIEW_AT" ]; then say "LOOP PAUSED_FOR_REVIEW at $t tokens"; exit 0; fi
  if [ -e ralph/NEED_GAME ]; then
    if gss_has_game; then
      say "GAME_WAIT: Gimme Some Slack still has the game, no model running, $t tokens"
      while gss_has_game; do
        [ -e "$LOGS/STOP" ] && { say "LOOP stopped: STOP file"; exit 0; }
        sleep 60
      done
      say "GAME_FREE"
    fi
    rm -f ralph/NEED_GAME
  fi
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
  fi
done
