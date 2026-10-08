# Greentide sheet — enactment (2026-10-07)

Source: `Transient/biome_ffar/greentide_sheet_2026-10-05.decisions.json` (owner rows = those with `at`).

## Status
- [x] decisions read
- [x] install / purge
- [ ] regen queued
- [x] names / descriptions / tiers / cuts
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
- Explicit "+ variant" plant picks installed as Graphic_Random extras: RM_Cundral B, RM_Thalquith A (kept beside new B), RM_Tumbel B (`_a_b.png`). Default (pre-ticked) variants not installed — redo rows carry every column as default, so defaults are not his intent.
- RSW_Shiro "+ variant" B NOT installed: the row has no decidedAt and purgeTouched, so ingest wrote no ruling to install under (follow-up).

### Part 3 — names / descriptions / cuts (done)
- AA_BloodShrimp: zhirrik -> zrrik (Contagion_Rename.xml, in place); description rewritten around the bite that heals it. The mechanic already exists: donor capacity AA_RegenerativePierce = DamageWorker_Vampiric.
- RM_CanopySwinger -> ookala (ThingDef+PawnKindDef label, new description: elongated, alien climber)
- RM_Dhollock -> dhollollo (labels; About.xml text)
- RSW_Diggerpede -> gristle (RSW_BiomesTeamPort_Races.xml label/kind/lifestage labels, new description)
- VFEI2_Swarmling -> saluksis (new UtinniPatches/Patches/Greentide_Rename.xml, label+description, def-wide)
- RM_Thurrock: description rewritten from its in-game art
- No invented names: every new name is his.
- Cut: RM_Sytheclaw removed from RM_Greentide_Biome.xml wildAnimals only (Pyrelands keeps it; RUT_ twins untouched); roster json evictions + labels updated.
- Tier moves: none asked.
- validate_patch: Greentide_Rename / Contagion_Rename / WildAnimals_Greentide 0 errors (static; live load set is a 15-mod test list so --defs refused); targets confirmed one ThingDef + one PawnKindDef each via measure get.
