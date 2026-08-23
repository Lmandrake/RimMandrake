#!/bin/sh
# board_loop.sh — REP's board publisher. Keeps every seat's queue view current.
#
#     setsid nohup ./src/RimMandrake/Utils/board_loop.sh >/dev/null 2>&1 </dev/null &
#     BOARD_LOOP_HOURS=4 ./src/RimMandrake/Utils/board_loop.sh &     # window length only
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
#     touch infrastructure/state/derived/board_loop.stop
# It exits within 60 s and clears the flag. `kill <pid>` also works; the stop-file
# exists so a seat that cannot find the pid is not stuck.
#
# ✅ HOW TO TELL IT IS ALIVE, without pgrep (which matches its own wrapper):
#     infrastructure/state/derived/board_loop.heartbeat   — rewritten every cycle
# Older than ~2 min means dead. `queue/*.md` mtimes say the same thing.
#
# ⏱️ 60 s is the cadence render.py documents: ~400 ms, 0.67% of one core.
#
# 🩺 IT ALSO WATCHES THE BOARD. `status_server.py` can wedge with the socket still
# ACCEPTING — `ps` alive, `ss` LISTEN, `curl` 000 — which is how the page was blank for
# an unknown part of 18h44m on 2026-08-23 (BOARD_SERVER_HANGS_SILENTLY_1). This loop is
# the only thing awake when no seat is, so it probes HTTP each cycle and restarts a
# server that is running and not answering, after TWO consecutive failures so a slow
# page does not cost a restart. ⛔ It never starts a server that is ABSENT — a seat or
# the owner may have killed it on purpose — it only says so in the log.
#
# ⚠️ RUN IT DETACHED, or the harness kills it when the turn ends. A plain background
# `&` does NOT survive — measured 2026-08-21, twice.
cd "$(dirname "$0")/../../.." || exit 1
LOG=infrastructure/state/derived/board_loop.log
BEAT=infrastructure/state/derived/board_loop.heartbeat
STOP=infrastructure/state/derived/board_loop.stop
mkdir -p infrastructure/state/derived
HOURS=${BOARD_LOOP_HOURS:-8}
END=$(( $(date +%s) + HOURS * 3600 ))
MUTE=0
echo "$(date -Is) board loop start (${HOURS}h window, renews, pid $$)" >> "$LOG"
while [ "$(date +%s)" -lt "$END" ]; do
  if [ -f "$STOP" ]; then
    rm -f "$STOP"
    echo "$(date -Is) board loop STOPPED by stop-file" >> "$LOG"
    exit 0
  fi
  python3 src/RimMandrake/rimflow/render.py --overwrite-queues >/dev/null 2>>"$LOG" \
    || echo "$(date -Is) render FAILED" >> "$LOG"
  date -Is > "$BEAT"

  # 🩺 board watchdog — see the header. Only a RUNNING-but-mute server is restarted.
  SRVPID=$(ps -eo pid,args | grep -E '[s]tatus_server\.py' | awk '{print $1}' | head -1)
  if [ -z "$SRVPID" ]; then
    MUTE=0
    echo "$(date -Is) board server ABSENT — not started (deliberate kills are respected)" >> "$LOG"
  else
    CODE=$(curl -s -m 10 -o /dev/null -w '%{http_code}' http://localhost:8787/ 2>/dev/null)
    if [ "$CODE" = "200" ]; then
      MUTE=0
    else
      MUTE=$(( MUTE + 1 ))
      echo "$(date -Is) board pid $SRVPID answered '$CODE' (strike $MUTE of 2)" >> "$LOG"
      if [ "$MUTE" -ge 2 ]; then
        echo "$(date -Is) board WEDGED — killing $SRVPID and restarting" >> "$LOG"
        kill "$SRVPID" 2>/dev/null
        sleep 2
        kill -9 "$SRVPID" 2>/dev/null
        setsid nohup python3 src/RimMandrake/Utils/status_server.py >>"$LOG" 2>&1 </dev/null &
        MUTE=0
      fi
    fi
  fi

  sleep 60
done
echo "$(date -Is) board loop window elapsed — renewing" >> "$LOG"
exec "$0"
