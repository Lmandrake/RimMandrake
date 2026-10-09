# Cauldron audit fixes 2026-10-09

Audit: `Transient/cauldron_independent_audit_2026-10-09.md` (15 FAIL). Owner notes: `Transient/biome_ffar/cauldron_sheet_2026-10-04.decisions.json`.
AA_GiantCrownedSilkie (UNMEASURED) left alone: owner question.

| FAIL row | Fix | Evidence |
|---|---|---|
| AA_Radyak | Renamed **ossrith**; new description written from the redo render E (bone-white plated hide, skull face, green crystal spine ridge; uranium-crystal harvest kept since the donor comp is unchanged). ThingDef label+description, PawnKindDef label, calf label/plural. Block appended to `src/RimUtinni/UtinniPatches/Patches/Cauldron_Rename.xml`. | validate_patch: Op 7/8 and all nested ops 1 match each in Races_Radyak.xml, 0 errors. |
| AA_InfectedAerofleet | New description per his note: footless floating ball of gas, an unfortunate visitor that drifted into the Contagion and got infected (`Contagion_Rename.xml`, label "blistered bulloo" kept). | validate_patch Contagion_Rename.xml 0 errors. Also owes the biomes deploy (finding 2) for the move. |
| Silooth (def) | Adult drawSize 3 to **8.0** (juvenile stage 2 to 5, shadows scaled, larva untouched): `src/RimStarWars/SWBestiary/Patches/Silooth/Silooth_Warbeast.xml`. Acid spit: the donor already gave it `SW_AcidSpew`, but that def has no `aiCanUse` (defaults false, so Ability.AICanTargetNow refuses and a wild silooth never spits). New `RSW_SiloothAcidSpit` (`Defs/AbilityDefs/RSW_SiloothAcidSpit.xml`), a copy with aiCanUse true, range 12.9, 24 cells of vanilla Proj_Acid, swapped into the PawnKindDef. | validate_patch: all 7 ops 1 match in Races_Animal_SW.xml, 0 errors (7 advisory "not wrapped" warnings: the donor is a hard dependency of SWBestiary). RimSage: Ability.cs:398, AbilityDef.aiCanUse default false, JobGiver_AIFightEnemy reads AICastableAbilities. Manhunter does not cast abilities. |
