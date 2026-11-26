cd "$(dirname "$0")/../../../../../../.."; V=design/concepts/Pyrelands/version/in_game/visit_9
until grep -q "END b8\|STOPPED at burn_line" $V/evidence/runner.log; do sleep 5; done
bash $V/scripts/runner.sh b9 firehawk_first_sighting_letter@letter firehawk_crestfeather_yield@crest mapgen_log@mapgen2
