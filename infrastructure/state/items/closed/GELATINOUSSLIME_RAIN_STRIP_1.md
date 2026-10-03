# GELATINOUSSLIME_RAIN_STRIP_1 — strip ordinary rain from the Slime in the campaign (both tiers), and retarget the donor-only ops

**Campaign tier** (`src/RimUtinni/UtinniPatches/Patches/`). Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §1 (c), §2 mark 8, §4 row 0b, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT). Underlying ruling: sheet `the_slime.md` §6 ban 2 (*"No meteorological rain… a water-rain weather def is a
violation (R-H1)"*), campaign law.

## What exists

- `RM_GelatinousSlime` carries vanilla `Rain` 8 and `FoggyRain` 6 (right for generated planets; its weather
  header says R-H1 is campaign-only). **No campaign patch strips them.** The twin `RUT_Slime` carries `Rain` 8.
  Ban 2 is broken in both tiers today.
- Campaign ops carrying Slime rulings target only the donor `AB_GelatinousSuperorganism`:
  `AncientDangerGenSteps_AmbientDoctrine.xml` (shrine denial), `BiomeNames_Ashkarr.xml`,
  `BiomeDescriptions_Ashkarr.xml`, `FishTypesStrip_NoFishBiomes.xml`.

## spec

1. A campaign patch removing `Rain` and `FoggyRain` from `RM_GelatinousSlime/baseWeatherCommonalities`, and
   `Rain` from `RUT_Slime` while the twin carries the world. Slime rain stays. Guard with
   `PatchOperationConditional`/`FindMod`, never `MayRequire` on an `<Operation>` (inert in 1.6).
2. Retarget the shrine denial onto `RM_GelatinousSlime` (keep the donor op until the donor retires).
3. The label/description ops are redundant (our def carries both): listed on `BIOME_TIER_CLEANUP_1`.
4. The free mod is not edited.

## criteria

- Live on the campaign list: `RM_GelatinousSlime`'s weather commonalities contain no `Rain`/`FoggyRain`;
  on a free-only list they still do.
- `validate_patch.py` with `--defs` and `--live` on the new patch: every op matches.
