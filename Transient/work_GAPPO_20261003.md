# GELATINOUSSLIME_GAPPO_FAMILY_1 work 2026-10-03
Started. Choices recorded below.

## Choices
- Census: no gappo in src/ or artpipe (find gappo: 0); the only precursor is RUT_SlimeGrazer (src/RimUtinni, art v1+v2 in artpipe, no ruling in Transient/*.decisions.json).
- New file Defs/ThingDefs_Races/Gappo.xml: RM_GappoLesser (bs 0.25, speed 2.4, herd 6~14, ecoW 0.25), RM_Gappo (grazer's numbers, bs 0.9), RM_GappoGreater (bs 3, speed 0.9, ecoW 2.5, comp RM_CompProperties_GappoChannel). All // INVENTED, non-predator, manhunter 0, SlimeResistantExtension (resistant by identity), one home. No member flies: no flight stats.
- Greater gappo channel (Source/GappoChannel.cs, in csproj): every rare tick the soft slime cell under it (RM_SlimeTerrain tag, not RM_Slime_Liquid) becomes RM_Slime_Hardened and RM_Filth_SlimeSmear on it is destroyed. Toggle SlimeSettings.gappoChannels (default true, checkbox "Greater gappo clears channels"). Channel does not re-soften; nothing in the mod reverts Hardened except what already did.
- Biome: RM_GappoLesser 1.5, RM_Gappo 1.0, RM_GappoGreater 0.3 inline in wildAnimals (INVENTED); "deliberately thin... Spike C" header replaced; visitors kept as trace tail.
- Art: gappo = artpipe rutslimegrazer_v2 (v1 vs v2 unruled by owner; v2 per item spec) copied to Textures/Things/Pawn/Animal/Gappo/RM_Gappo_{south,east,north}.png. Lesser/greater: 6 jobs filed from the turn1 CSV rows (filtered copy); pink until generated.
- validation.py FIELDS + settings_flip gain gappoChannels; northstar_mock DEFAULTS too. Selftest: 46 clean / 22 faults / 0 problems. validate_patch: BiomeDef OK; Gappo.xml only the 6 missing-art texPath errors (lesser/greater PNGs owed).
- check_pseudo_sw_name: "gappo" PASS; the checker fails multi-word labels by design, "lesser/greater gappo" are size qualifiers.
## Not done (blockers)
- RUT_SlimeGrazer def + twin row (src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_SlimeGrazer.xml, BiomeDefs/RUT_Slime.xml line 96) are outside the GelatinousSlime folder: not deleted. Item criteria "no RUT_SlimeGrazer string in src/" still owed; RUT_Ashwallow.xml comment also mentions it.
- No live validation component for the three defs beyond all_defs_resolve (auto-covers via Defs/ scan; defs count raised); no live run (no bridge).
