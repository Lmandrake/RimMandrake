# Greentide sheet — enactment (2026-10-07)

Source: `Transient/biome_ffar/greentide_sheet_2026-10-05.decisions.json` (owner rows = those with `at`).

## Status
- [x] decisions read
- [x] install / purge
- [ ] regen queued
- [ ] names / descriptions / tiers / cuts
- [ ] def changes
- [ ] validate + selftests
- [ ] commits

## Log
### Part 1 — install / purge (done)
- decisions md5 26a48c1b…, 51 owner rows; copy at infrastructure/state/art_rulings/2026-10-07_greentide_sheet_2026-10-05.decisions.json
- ingest (--defer-redo-jobs): 102 rulings, 112 rejected-ingame, 24 purges, 3 refused (VFEI2_Swarmling S/E/N live in TheRot, kept on the Miasma sheet — never purge in-use).
- Installed via ledger ruling ids: AA_BloodShrimp B (S/E/N, BloodShrimpArtOverride, restores the 2026-09-13 render); fish RM_Dubbol/Karrun/Lozh/Saava/Uvva/Zeev B
  (new Things/Item/Fish/<def>.png, defs repointed off borrowed vanilla plant sprites; RUT_ twins untouched); RM_Thalquith B, RM_Zhorrel B, RM_YearningFruit B (replace _a);
  RM_Greatbole A, RM_Kaddrath A (had NO texture at all before).
- Already current (pick = in game): Brakkel, Cundral, Dhollock, Ghemmel, Gorbeleth, Illurin, Maddrick, Mirrelbole, Mourvel, Nemmer, Phorrik, Quathis, Sarnstilt, Sarquin, Thurrock, Tumbel, Veluthar, Wollick, Yammeth, Dalgo, Fambaa(+D/E/F), Gelagrub, Shiro; redo-row picks (Beldon C/D, Dragonsnake D, Klorslug_j B, Mott_m B/C, ShiroTrap_i B/_j C, Hawkbat_j F/flying G, PekoPeko_m D/flying E) are the in-game bytes.
- NOT installed: Plant_Grass B / Plant_TallGrass B — single render for a ReGrowth AssetBundle Graphic_Random folder (Things/Plant/RG_Grass) used planet-wide; queued as realistic variant regen anchored on B instead, wiring is a follow-up.
