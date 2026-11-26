#!/bin/bash
# Pyrelands visit 7 runner (ArchSmall): for each chain, reload the site fixture, then run the northstar driver on it.
# usage: runner.sh <tag> [+]<chain|script:path>[@label] ...   (one result JSON + log per item under evidence/)
# VAR=VAL:item sets VAR for that item only (a planted fault); a leading + skips the site reload (the step runs on the map the previous step left); @label names the outputs
cd "$(dirname "$0")/../../../../../../.."
eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
export RM_HOST_GUARD_GEN=${RM_HOST_GUARD_GEN:-41}
export RM_BRIDGE_LINEAGE=${RM_BRIDGE_LINEAGE:-pv7_visit7}   # one sequential driver: its own finished calls never refuse it
export WSLENV="$WSLENV:RM_HOST_GUARD_GEN:RM_BRIDGE_LINEAGE:PYRE_WALK:PYRE_PLANT_ASHFALL_STRIKE:PYRE_PLANT_NO_RAIN_GATE_OFF:PYRE_PLANT_CONTROL_HAS_SPRAYER:PYRE_PLANT_RING_GAP:PYRE_PLANT_BURNLINE_TOGGLE_IGNORED:PYRE_PLANT_FARHAWK_NO_SEEK:PYRE_PLANT_REGROW_WET_ROOTS_OFF:PYRE_PLANT_VENOM_TEND_WRONG_PATIENT:PYRE_PLANT_RUIN_FOOTPRINT_SOIL:PYRE_PLANT_SCORCHFRUIT_UNBURNED:PYRE_PLANT_FOIL_AT_SITE_DENSITY:PYRE_PLANT_OFFBURN_TOGGLE_IGNORED:AGENT_SEAT:HT_ROOF:LANES_SAVE:LANES_WINDOW:LANES_TILE:LANES_TAG:LINE_RECTS"
export AGENT_SEAT=BENCH
V=design/concepts/Pyrelands/version/in_game/visit_7
E=$V/evidence
TAG=$1; shift
echo "START $TAG $(date '+%F %T')" >> $E/runner.log
for item in "$@"; do
  t0=$(date +%s)
  envp=""
  if [[ $item =~ ^([A-Z_]+=[^:]+):(.*)$ ]]; then envp=${BASH_REMATCH[1]}; item=${BASH_REMATCH[2]}; fi
  c=${item#+}; lab=${c#*@}; c=${c%@*}; [[ $lab == "$item" || $lab == "$c" ]] && lab=${c##*/}
  rl=skipped
  if [[ -e $E/skip_${lab##*/} ]]; then echo "SKIPPED $item ($(cat $E/skip_${lab##*/})) $(date '+%T')" >> $E/runner.log; continue; fi
  if [[ $item != +* ]]; then
  python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint 417df172fdb5e402 --tag visit7 \
      --reload-only --tile 193 --map-id 1 --out Transient/pv7_site_1_reload.json 2>&1 | tr -d '\r' \
      | grep -v "safe.directory\|dubious\|non-local\|add an exception" > $E/reload_${lab##*/}.log
  rl=${PIPESTATUS[0]}
  fi
  if [[ $c == script:* ]]; then
    p=${c#script:}; n=$(basename $lab .py)
    env $envp python.exe $p 2>&1 | tr -d '\r' | grep -v "safe.directory\|dubious\|non-local\|add an exception" > $E/script_$n.log
    rc=${PIPESTATUS[0]}
  else
    env $envp python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py \
        --no-record --chains $c --out $E/pv7_$lab.json 2>&1 | tr -d '\r' \
        | grep -v "safe.directory\|dubious\|non-local\|add an exception" > $E/run_$lab.log
    rc=${PIPESTATUS[0]}
  fi
  echo "DONE ${envp:+$envp:}$item reload_rc=$rl rc=$rc $(( $(date +%s) - t0 ))s $(date '+%T')" >> $E/runner.log
done
echo "END $TAG $(date '+%F %T')" >> $E/runner.log
