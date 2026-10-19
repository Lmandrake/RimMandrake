#!/bin/sh
# usage: logdelta.sh <startByte> <outfile>  -> prints new size and distinct exception lines in the delta
L="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
MEASURE_ALLOW_SCAN=1 tail -c +"$1" "$L" > "$2"
echo "size=$(MEASURE_ALLOW_SCAN=1 wc -c < "$L") lines=$(wc -l < "$2")"
for s in AreaManager Area_Hive VehiclePathingSystem PathingHelper "Exception spawning loaded thing" "Could not instantiate" "Root level exception" "Exception ticking"; do printf '%s=%s ' "$s" "$(grep -c "$s" "$2")"; done; echo
grep -n "Exception\|^Error" "$2" | cut -c1-200 | sort -t: -k2 -u | sort -n | head -${3:-12}
