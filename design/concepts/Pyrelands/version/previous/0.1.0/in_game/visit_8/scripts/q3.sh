cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_8
bash $V/scripts/runner.sh tier3 burn_line@burn_line2 +script:$V/scripts/lanes_probe.py || exit 3
export PYRE_WALK=1 PYRE_WALK_ONLY=walk_master_bed_fire_resumes
bash $V/scripts/runner.sh tier3bed walk_season@walk_bed_real PYRE_PLANT_BED_MASTER=left_on:walk_season@walk_bed_left_on PYRE_PLANT_BED_MASTER=left_off:walk_season@walk_bed_left_off
