# Texture gaps 20261010 (ART_TEXTURE_GAPS_FOLLOWUP_1)

Instrument: `src/RimMandrake/Utils/art/texture_gap_lint.py` (+ `texture_gap_allowlist.json`, `selftest_texture_gap_lint.py`).
Census: 2999 texPaths; 2691 resolve in src, 272 in an active donor/base bundle, 19 UNRESOLVED (vanilla-layout paths the index cannot show; not claimed missing), 16 gaps.

Fixed: AA_Swarmling redirect removed from TheRot RotSpecies_NamesAndSizes.xml (donor art draws until a regen).

Gaps needing new art / a decision (all allowlisted, shrink-only):
- RM_Braskeen: owner ruled REDO ("less cartoonish"); renders v2 await his pick.
- RM_Ismerrow: sheet row is pick A (prefill only, no typed note); `miasma_ismerrow_a` exists, not installed. Question: install A?
- KOTOR_SmallCrystal (Buildings/Crystal_Formations/small_dyeable): own render owed.
- Things/Filth/CrawlSmear (RM_Traces_Spike); RM_Dakkra_rest; RM_AssayFlecks Flecks_Light/Heavy; 5 RM_Dewfall *_dew.
- RUT_FungalSoil icon: texPath BMT_Caverns/Terrains/MycelialSoil, but Biomes! Caverns is NOT in the active list (its header comment is false). Question: copy TheRot's RotSporeKit/Terrains/MycelialSoil.png into FungalSoilTrade as the icon?
- 3 BMT_Caverns Dessicated patches: inert (donor absent).
