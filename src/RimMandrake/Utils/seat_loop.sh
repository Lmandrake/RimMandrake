#!/usr/bin/env bash
# seat_loop.sh SEAT CMD... — a seat tile's launch line, wrapped so a seat restart relaunches IN THE SAME TILE.
#
# Runs CMD (the WT profile's own claude_bounded.sh LAUNCH line). When it exits, asks seat_restart.py whether the
# Dispatcher just killed this seat's window for a fresh-per-ticket restart (FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET):
# if so `intile` claims that kill exactly once and execs the relaunch argv in this tile (a fresh interactive window,
# --remote-control, first prompt `seat_restart.py wake`); exit 3 means "no restart: you quit it", and the tile drops
# to a login shell exactly as before. install_wt_seat_profiles.py wraps a seat with this only while the schedule key
# seat_restart.enabled is true and lists the seat.
seat="$1"; shift
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$@"
lastrc=$?                        # 143 = ended by the fleet stop (SIGTERM): the tile closes, see install_wt_seat_profiles.SHELL_TAIL
quick=0
while true; do
  t0=$SECONDS
  python3 "$here/../rimflow/seat_restart.py" intile --seat "$seat"
  rc=$?                           # intile's own 3 = no restart to relaunch; else the relaunched window's exit code
  [ "$rc" -eq 3 ] && break
  lastrc=$rc
  if [ $((SECONDS - t0)) -lt 20 ]; then quick=$((quick + 1)); else quick=0; fi
  [ "$quick" -ge 3 ] && { echo "[seat_loop] 3 quick exits in a row: stopping the relaunch loop"; break; }
done
[ "$lastrc" -eq 143 ] && exit 0
exec "${SHELL:-/bin/bash}" -l
