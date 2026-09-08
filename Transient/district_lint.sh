#!/usr/bin/env bash
# lint + render every district template at its manifest size. Output to stdout;
# a human reads the renders once, then bins them (Transient rule).
#   usage: Transient/district_lint.sh [render]
cd /mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils || exit 1
P=~/.local/venvs/rimlua/bin/python
MODE=${1:-lint}
run() {  # name w h faction tech
  echo "=== $1 ($2x$3, $4/$5)"
  if [ "$MODE" = render ]; then
    $P -m rimplace render "$1" --rect 0,0,$2,$3 --faction "$4" --tech "$5" 2>&1 | grep -vE "^⚠|Falling back|the load you|Rebuild it"
  fi
  $P -m rimplace lint "$1" --rect 0,0,$2,$3 --faction "$4" --tech "$5" 2>&1 | grep -vE "^⚠|Falling back|the load you|Rebuild it"
}
run junkers_scrapyard 30 30 Jawa_Junkers Neolithic
run junkers_dwelling_cluster 22 22 Jawa_Junkers Neolithic
run junkers_cantina_block 16 16 Jawa_Junkers Neolithic
run junkers_depot 18 18 Jawa_Junkers Neolithic
for t in hutt_palace_hall:26:24 hutt_spicehouse:18:16 hutt_holding_pens:20:16 hutt_cistern_court:22:22; do
  IFS=: read -r n w h <<<"$t"; [ -f ../../../design/Jawa/templates/$n.lua ] && run $n $w $h Jawa_HuttCartel Industrial
done
for t in droid_charging_hall:24:20 droid_cracking_works:24:24 droid_battery_bunker:16:14 droid_fabrication_room:20:16; do
  IFS=: read -r n w h <<<"$t"; [ -f ../../../design/Jawa/templates/$n.lua ] && run $n $w $h Jawa_FreeDroidEnclaves Spacer
done
for t in deepwater_cistern_hall:26:22 deepwater_hospital_ward:20:16 deepwater_hydroponics_bay:22:18 deepwater_gate_bastion:24:14; do
  IFS=: read -r n w h <<<"$t"; [ -f ../../../design/Jawa/templates/$n.lua ] && run $n $w $h Jawa_DeepwaterCompact Industrial
done
