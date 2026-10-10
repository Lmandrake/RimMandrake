#!/usr/bin/env bash
# Launch RimWorld through Steam and wait until the bridge of THIS run is up.
# Thin wrapper: the logic, the truth conditions and their selftest live in launch_ready.py
# (LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE, 2026-10-10). The old grep-the-log loop here
# accepted the previous run's marker and its exit code was wrong both ways.
# Exit 0 READY, 2 deadline passed with the process still alive (NOT killed), 1 any failure.
exec python3 "$(dirname "$(readlink -f "$0")")/launch_ready.py" "$@"
