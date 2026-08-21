#!/bin/sh
# board_loop.sh — REP's board publisher. Keeps every seat's queue view current.
#
#     ./src/RimMandrake/Utils/board_loop.sh &          8 h, then stops
#     BOARD_LOOP_HOURS=4 ./src/RimMandrake/Utils/board_loop.sh &
#
# 🔴 WHY THIS EXISTS. `queue/*.md` are GENERATED and only `render.py --overwrite-queues`
# publishes them. Nothing else runs it. On 2026-08-21 they sat frozen for 2h17m while
# four seats filed 24 items into views nobody was regenerating, and no seat could tell.
# The board is REP's, so publishing it is REP's.
#
# ⏱️ 60 s is the cadence render.py documents: ~400 ms, 0.67% of one core.
#
# ⚠️ RUN IT DETACHED, or the harness kills it when the turn ends:
#     setsid nohup ./src/RimMandrake/Utils/board_loop.sh >/dev/null 2>&1 </dev/null &
# A plain background `&` does NOT survive — measured 2026-08-21, twice.
#
# ⚠️ It is BOUNDED on purpose. An unattended loop with no end is how a machine ends up
# running something nobody remembers starting. Restart it when it lapses; the log says
# when it began and when it stopped.
cd "$(dirname "$0")/../../.." || exit 1
LOG=infrastructure/state/derived/board_loop.log
mkdir -p infrastructure/state/derived
HOURS=${BOARD_LOOP_HOURS:-8}
END=$(( $(date +%s) + HOURS * 3600 ))
echo "$(date -Is) board loop start (${HOURS}h bound, pid $$)" >> "$LOG"
while [ "$(date +%s)" -lt "$END" ]; do
  python3 src/RimMandrake/rimflow/render.py --overwrite-queues >/dev/null 2>>"$LOG" \
    || echo "$(date -Is) render FAILED" >> "$LOG"
  sleep 60
done
echo "$(date -Is) board loop end" >> "$LOG"
