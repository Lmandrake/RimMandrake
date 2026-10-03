# WEEPINGSTONES_OASIS_MUTATOR_FLORA_1 — register the Weeping Stones with the Oasis landmark mutator (both tiers) and take the Earth palms out of its pools

Caused by `WEEPINGSTONES_SCORING_SITTING_1` (turn 1). **Free tier** (the `RM_` whitelist and the flora swap) **plus
one campaign patch** (`RUT_` whitelist, palm removal in `OasisMutator_DesertOasis.xml`). Design: `design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §1 (b), (b′),
§4 row 0, §8. Ruling: build first, land what was decided plus the giant's story (decision taken by question card
2026-10-02 12:53 PDT; card text: *take the palms out of every oasis and register the biome with the oasis landmark
properly*). Underlying: sheet §6 bans Earth flora; the owner's 2026-09-09 card used **the date palm** as the example.

## What exists

- `src/RimUtinni/UtinniPatches/Patches/OasisMutator_DesertOasis.xml` whitelists only the donor `ZBiome_DesertOasis`
  into the vanilla `Oasis` TileMutatorDef's `biomeWhitelist` (vanilla: `Desert`, `ExtremeDesert`), and **adds**
  `TreePalma` 3 and `VEE_Plant_DatePalm` 2 to its bonus flora. Its snow-strip and label ops target the donor only.
- Vanilla `Oasis.additionalWildPlants`: `Plant_TreePalm`, `Plant_RatPalm`, `Plant_Grass`, `Plant_GrayGrass`,
  `Plant_Reeds` (patch header's RimSage read). `Plant_Reeds` is a ruled vanilla keep for this biome.
- 186 placed oasis landmarks are saved world state (`OASIS_LANDMARK_PLACEMENT_1`); whether anything re-checks the
  whitelist on them is UNMEASURED live.

## spec

1. Campaign: add `RUT_WeepingStones` beside the donor in the whitelist; **remove** `TreePalma` and
   `VEE_Plant_DatePalm` from the bonus flora.
2. Free: a `mandrake.rm.weepingstones` patch whitelisting `RM_WeepingStones` into `Oasis`.
3. Free: on our biome only, the Oasis mutator's Earth plants (the two palms and the two grasses) are replaced by
   the biome's own blade flora (`RM_WeepingStonesNativeFlora.xml`; `Plant_Reeds` stays). Vanilla deserts keep
   theirs. A per-biome swap on one TileMutatorDef is not plain XML: pick the narrowest mechanism (an `RM_` oasis
   mutator variant for our biome, or a small worker override keyed on a biome extension) and read the 1.6
   TileMutatorWorker source first (RimSage), never assume.
4. Hand the donor-only snow and label ops to `BIOME_TIER_CLEANUP_1` (noted there); harmless, not this item.

## criteria

- Loaded `TileMutatorDef/Oasis.biomeWhitelist` contains `RM_WeepingStones` and `RUT_WeepingStones`.
- Quicktest on a Weeping Stones tile with the Oasis mutator: zero `Plant_TreePalm`, `Plant_RatPalm`, `TreePalma`,
  `VEE_Plant_DatePalm`, `Plant_Grass`, `Plant_GrayGrass` on the map (`jawa/list_things` per def; prove the
  census can see by counting a native blade plant > 0); a vanilla Desert oasis map still grows palms (control).
- `Player.log` clean of the mutator for both biomes.
