#!/bin/bash
# live_pass.sh: the live pass of RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES on ArchBig, run under
# `game_lock.py run ArchBig`. The FlowWorks mod is unchanged since visit 12 (deploy dry run: in sync), so nothing is
# deployed: the game is restarted on the 13-mod flowworks tier for ten checks, then on fw_gss_sitting for sc_lake_endless.
# Each check's limit is a hang guard: a scene that hangs holds the bridge for good. Measured need: the longest of these
# scenes in visit 12 took 351 s (sc_pawn_height, 46 orders); 1800 s is five times that, and every new scene is shorter.
cd "$(dirname "$0")/../../../../../.."
D=design/concepts/FlowWorks/version/in_game/bundle_shrink_20261125
U=src/RimMandrake/Utils
CS=src/RimMandrake/FlowWorks/northstar/concept_scenes.py
# Run 1 (01:21 PST) stopped nothing (`stop ArchBig` reads the name as a pid), so --apply refused a running game and every
# check ran on the 315-mod list (rows_run1_on_315_mod_list.jsonl). tier() now stops by instance and refuses to go on unless
# ModsConfig holds exactly the tier's list.
tier() {
  echo "== tier $1 $(date +%H:%M:%S)"
  python3 $U/game_instance.py stop --instance ArchBig --for "FlowWorks shrunk scenes live pass: tier $1" \
    --despite-hold "this live pass holds ArchBig (game_lock.py run)" 2>&1 | tail -2
  python3 $U/modset_builder.py --tier "$1" --apply 2>&1 | tail -2
  python3 - "$1" <<'PY' || { echo "TIER NOT APPLIED: stopping the pass"; exit 3; }
import sys, xml.etree.ElementTree as ET
sys.path.insert(0, "src/RimMandrake/Utils")
from game_paths import MODS_CONFIG
n = len(ET.parse(MODS_CONFIG).find("activeMods"))
print("ModsConfig holds %d mods for tier %s" % (n, sys.argv[1]))
sys.exit(0 if n <= 30 else 1)
PY
  python3 $U/game_instance.py launch ArchBig 2>&1 | tail -2
  python3 $D/wait_bridge.py 2>&1 | tail -1
}
scene() {   # scene <test id> <tier>
  python3 $D/run_row.py "$1" --tier "$2" --timeout 1800 -- python.exe -u $CS --scene "scene_${1#sc_}" --out OUT 2>&1 | head -3
}
tier flowworks
for t in sc_walk_reload sc_walk_switch sc_walk_second_order sc_source_draws sc_source_refills sc_sprinkler_pump \
         sc_faucet_drink sc_hole_prison sc_pawn_height; do
  scene $t flowworks
done
# the hung bridge proof stands on the current map: the calm site the last scene reloaded
python3 $D/run_row.py sc_hung_bridge --tier flowworks --site-key site_calm.ok --timeout 1800 -- \
  python.exe -u src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py OUT --only posts,under 2>&1 | head -3
tier fw_gss_sitting
scene sc_lake_endless fw_gss_sitting
echo "== done $(date +%H:%M:%S)"
