#!/bin/bash
# Visit 2 full-list phase (game a, bridge held): his 315-mod list, a cold load, the old-save opening-front read
# (the 2026-10-15 save names full-list mods), a site built on the full list, then sc_walk (walk_season, PYRE_WALK=1).
# Progress lines in Transient/pv2/runner.progress.
export RM_ALLOW_CONCURRENT_BRIDGE=1 PYRE_WALK=1
export WSLENV="${WSLENV:+$WSLENV:}RM_ALLOW_CONCURRENT_BRIDGE:PYRE_WALK"
cd /home/mandrake/rm/relentless/clones/RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO.det
V=design/concepts/Pyrelands/version/in_game/visit_2; E=$V/evidence; P=Transient/pv2/runner.progress
say() { echo "$(date +%T) FULL $*" >> $P; }
say begin
if [ -z "$SKIP_LAUNCH" ]; then   # SKIP_LAUNCH=1: the full list is already loaded (a rerun of the later steps)
python3 src/RimMandrake/Utils/modlist_swap.py --restore --apply > Transient/pv2/full_swap.log 2>&1; say "swap rc=$?"
./game --why "Pyrelands visit 2: sc_walk needs his full list (restored)" down > /dev/null 2>&1
pid=$(python3 src/RimMandrake/Utils/game_instance.py pid a 2>/dev/null | tail -1)
[ -n "$pid" ] && python3 src/RimMandrake/Utils/game_instance.py stop "$pid" --instance a --for "Pyrelands visit 2 full list" > /dev/null 2>&1
for i in $(seq 60); do python3 src/RimMandrake/Utils/game_instance.py pid a 2>/dev/null | grep -q -E '^[0-9]+$' || break; sleep 3; done
python3 src/RimMandrake/Utils/game_instance.py launch a --wait > Transient/pv2/full_launch.log 2>&1; rc=$?; say "launch rc=$rc $(tail -1 Transient/pv2/full_launch.log | cut -c1-160)"
fi
# launch --wait gives up at 600 s; his full list loads for longer (2026-11-21: no port line at 600 s), so wait for the bridge
for i in $(seq 180); do ./game 2>/dev/null | head -1 | grep -q "bridge answers" && break; sleep 10; done
say "bridge $(./game 2>/dev/null | head -1 | cut -c1-80)"
./game --why "Pyrelands visit 2: game a relaunched on his full list" up > /dev/null 2>&1
python3 src/RimMandrake/rimflow/build_match.py identity --mod Pyrelands --full --mod-sha 01853a05a6 > $E/identity_full.json 2> Transient/pv2/identity_full.err; say "identity rc=$?"
python.exe $V/scripts/old_save_read.py > $E/script_old_save_read_full.log 2>&1; say "old_save_read rc=$?"
python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint bf7f9e1fe4 --tag visit2full > Transient/pv2/site_full.log 2>&1; say "site rc=$? $(grep -o 'tile [0-9]* map [0-9]* saved [A-Za-z0-9_]*' Transient/pv2/site_full.log | tail -1)"
python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains walk_season --out $E/pv2_walk_season.json > Transient/pv2/run_walk_season.log 2>&1; say "walk_season rc=$?"
say ALLDONE
