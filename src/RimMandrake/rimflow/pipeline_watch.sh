#!/usr/bin/env bash
# pipeline_watch.sh <station> -- one tab of the Pipeline window (launch_fleet.ps1 seat PIPELINE).
# Loops pipeline_watch.py so a renderer crash (or a code update in the clone) never leaves the tab at a bare
# prompt, which launch_fleet's sweep would read as a dead window. Read-only; zero tokens. Ctrl+C twice ends the tab.
here=$(cd "$(dirname "$0")" && pwd)
while true; do
    python3 "$here/pipeline_watch.py" "$1"
    printf '\033[2m(renderer exited %s; restarting in 3 s)\033[0m\n' "$?"
    sleep 3
done
