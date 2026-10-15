#!/bin/bash
# r6 Pyrelands full suite: one fixture reload per piece (r5's piece split; heat-guarded scorchfruit piece)
cd /mnt/d/Luke/dev/_rmscratch/bench_live_20261015_r6
export RM_ALLOW_CONCURRENT_BRIDGE=1 WSLENV=RM_ALLOW_CONCURRENT_BRIDGE
L=Transient/live/pyre
run() { # name chains timeout
  echo "=== $1 $(date -u +%T) $2" >> $L/suite_progress.txt
  timeout 240 python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint 417df172fdb5 --tag r6 --reload-only --tile 5 --work "D:\\Luke\\dev\\_rmscratch\\bench_live_20261015_r5\\sites" 2>&1 | tr -d "\r" | tail -1 | cut -c1-160 >> $L/suite_progress.txt
  timeout $3 python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains "$2" --no-record --out "D:\\Luke\\dev\\_rmscratch\\bench_live_20261015_r6\\Transient\\live\\pyre\\pyre_$1.json" 2>&1 | tr -d '\r' | grep -v "skipped#" > $L/pyre_$1.log
  echo "rc=${PIPESTATUS[0]}" >> $L/suite_progress.txt
  grep -E "^\[pyre\] .* (PASS|FAIL|UNMEASURED|INFERRED|RESTART)|GOVERNOR_STOP|Traceback" $L/pyre_$1.log | cut -c1-260 >> $L/suite_progress.txt
}
#run p1 mapgen_log,plant_census,animal_census,grass_cover,ruins,startup_and_def_wiring,ground_deep_ash 900
#run p2 ash_fertility_watered,ambient_ash_drift,fire_tick_effects,ashfall_weather_accumulation,ashfall_drifts,cinderfall,blackrain,no_ordinary_rain 900
#run p3 plant_census,fire_tick_effects,scorchfruit_fire_born,scorchfruit_produces,scorchfruit_spoils,firehawk,furnace_warmth,furnace_room 1500
#run p4 burrowers,fulgurite,ullai_and_giant,sand_shovel,lightning_breaker 1200
#run p8 burn_line 1500
#run p9 fresh_burn_bonus 1200
#run p10 embergrass_regrow 1500
run p4b ullai_and_giant 600
echo "=== DONE $(date -u +%T)" >> $L/suite_progress.txt
