#!/bin/bash
WORKSHOP="/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
OUT="/mnt/d/Luke/dev/Rimworld/Transient/faction_def_owners.txt"
> "$OUT"
for name in VFEI2_PlayerOutpost VFET_WildMen VQE_NewVaultPlayerFaction VFEP_PlayerPirate OuterRim_RogueDroidColony OuterRim_EmpirePlayerFaction OuterRim_RebelPlayerFaction BS_JotunPlayerColony BS_PlayerTribeXenoPlus BS_PlayerColonyXenoPlus; do
  echo "=== $name ===" >> "$OUT"
  find "$WORKSHOP" -iname "*.xml" -newer /dev/null 2>/dev/null -print0 | xargs -0 grep -l "$name" 2>/dev/null >> "$OUT"
done
echo "DONE" >> "$OUT"
