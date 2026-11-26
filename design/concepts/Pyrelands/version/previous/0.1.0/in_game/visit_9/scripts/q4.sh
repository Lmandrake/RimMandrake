cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_9
until grep -q "END b3b" $V/evidence/runner.log; do sleep 3; done
bash $V/scripts/runner.sh b4 +script:$V/scripts/off_control_source.py@off_src HOLD_FURNACE=1:+script:$V/scripts/off_control_source.py@off_src_furnace
