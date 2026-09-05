#!/usr/bin/env bash
# Serve the creature_art dataset's FiftyOne App at http://127.0.0.1:5151
# from WSL; WSL2 forwards localhost, so open that URL in Windows.
#
# ALWAYS in its own memory scope -- FiftyOne's DB + web app must never share
# the agent seat's cgroup (a heavy child there has killed a window).
set -euo pipefail
PORT="${1:-5151}"
exec systemd-run --user --scope -q \
  -p MemoryMax=6G -p MemorySwapMax=1G -p OOMPolicy=continue \
  -- /home/mandrake/.venvs/fiftyone/bin/fiftyone app launch creature_art \
       --port "$PORT" --address 0.0.0.0 --remote
