#!/bin/bash
# getshots.sh <prefix> <localdir> : tar the game's screenshots named <prefix>* on Steve and copy them here, unpacked.
set -e
P="$1"; D="$2"; mkdir -p "$D"
SS='/mnt/c/Users/sjlewis/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Screenshots'
cd "$(dirname "$0")/../.."
ralph/steve.sh run "mkdir -p Transient/ralph_fw && cd \"$SS\" && tar cf ~/rm/flowworks/Transient/ralph_fw/shots_$P.tar $P* && echo packed" >/dev/null
ralph/steve.sh fetch "Transient/ralph_fw/shots_$P.tar" "$D" >/dev/null
tar xf "$D/shots_$P.tar" -C "$D" && rm "$D/shots_$P.tar"
ls "$D" | grep "^$P" | wc -l
