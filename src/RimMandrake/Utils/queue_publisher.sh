#!/bin/sh
# queue_publisher.sh — keeps every seat's queue view current.
#
# ⭐ 2026-08-27: was `queue_publisher.sh`. The status board and its HTTP server were
# removed (owner: the web page never proved useful; git is the provenance), leaving
# the half that was always load-bearing — regenerating queue/*.md — under a name
# that finally says so.
#
#     setsid nohup ./src/RimMandrake/Utils/queue_publisher.sh >/dev/null 2>&1 </dev/null &
#     QUEUE_PUBLISHER_HOURS=4 ./src/RimMandrake/Utils/queue_publisher.sh &     # window length only
#
# 🔴 WHY THIS EXISTS. `queue/*.md` are GENERATED and only `render.py --overwrite-queues`
# publishes them. Nothing else runs it. On 2026-08-21 they sat frozen for 2h17m while
# four seats filed 24 items into views nobody was regenerating, and no seat could tell.
# The board is REP's, so publishing it is REP's.
#
# 🔄 IT RENEWS ITSELF — owner, 2026-08-22: "self-restarting". The 8 h window is still
# real and still logged, but at the end of it the loop re-execs instead of dying, so a
# lapse can no longer happen silently at a time nobody is watching. The bound now buys
# what it was always for — a log line saying the loop is still here and why — without
# costing a frozen view.
#
# ⛔ HOW TO STOP IT, since it no longer stops on its own:
#     touch infrastructure/state/derived/queue_publisher.stop
# It exits within 60 s and clears the flag. `kill <pid>` also works; the stop-file
# exists so a seat that cannot find the pid is not stuck.
#
# ✅ HOW TO TELL IT IS ALIVE, without pgrep (which matches its own wrapper):
#     infrastructure/state/derived/queue_publisher.heartbeat   — rewritten every cycle
# Older than ~2 min means dead. `queue/*.md` mtimes say the same thing.
#
# ⏱️ 60 s is the cadence render.py documents: ~400 ms, 0.67% of one core.
#
# ⚠️ RUN IT DETACHED, or the harness kills it when the turn ends. A plain background
# `&` does NOT survive — measured 2026-08-21, twice.
cd "$(dirname "$0")/../../.." || exit 1
LOG=infrastructure/state/derived/queue_publisher.log
BEAT=infrastructure/state/derived/queue_publisher.heartbeat
STOP=infrastructure/state/derived/queue_publisher.stop
mkdir -p infrastructure/state/derived
HOURS=${QUEUE_PUBLISHER_HOURS:-8}
END=$(( $(date +%s) + HOURS * 3600 ))
echo "$(date -Is) queue publisher start (${HOURS}h window, renews, pid $$)" >> "$LOG"
while [ "$(date +%s)" -lt "$END" ]; do
  if [ -f "$STOP" ]; then
    rm -f "$STOP"
    echo "$(date -Is) board loop STOPPED by stop-file" >> "$LOG"
    exit 0
  fi
  python3 src/RimMandrake/rimflow/render.py --overwrite-queues >/dev/null 2>>"$LOG" \
    || echo "$(date -Is) render FAILED" >> "$LOG"
  date -Is > "$BEAT"

  sleep 60
done
echo "$(date -Is) board loop window elapsed — renewing" >> "$LOG"
exec "$0"
