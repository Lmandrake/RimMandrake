# FEVERWOOD_TIER_LEAKS_FIX_1 — the Fever Wood's donor-only campaign patches move onto `RM_FeverWood`, and three borrowed ports leave its campaign roster

Caused by `FEVERWOOD_SCORING_SITTING_1` (turn 1). Campaign tier, `src/RimUtinni/UtinniPatches/Patches/`. Design:
`feverwood_bedazzle_review_2026-10-02.md` §1 (a) and (b), §3 (last row), §4 row 0, §8. Ruling: **build first:
land the decided work plus the giant's story** (decision taken by question card 2026-10-02 11:12 PDT), whose
option text includes *"judge the three borrowed slugs and beetle out of this campaign roster (they stay in
their other homes)"*. Same family as the Rot's `ROT_TIER_LEAKS_FIX_1`.

## spec

1. **The ancient-danger block (the one that changes play).** `AncientDangerGenSteps_AmbientDoctrine.xml`
   adds `preventGenSteps/ScatterShrines` (DENY) only to `COMIGO_GreaterSwamp_Tropical` (the donor, l.351–369).
   `RM_FeverWood` carries no `preventGenSteps`, so once the planet is painted with `RM_FeverWood`, ancient
   dangers generate where today's donor tiles refuse them. Fix: `RM_FeverWood` refuses them too. Preferred:
   the free def declares `<preventGenSteps><li>ScatterShrines</li></preventGenSteps>` itself if the sheet's
   no-ancient-danger stance is the free biome's too (it is the place's doctrine, not IP); otherwise a sibling
   op in the same campaign file targeting `RM_FeverWood` with the same Conditional add-or-append shape, guarded
   by `PatchOperationFindMod`/`Conditional`, never `<Operation MayRequire=…>`.
2. **The Ashkarr label and description** (`BiomeNames_Ashkarr.xml`, `BiomeDescriptions_Ashkarr.xml`): the
   Fever Wood entries gain a second op on `RM_FeverWood` beside the donor op (campaign wording on the free
   def when the campaign is loaded).
3. **The no-fish strip** (`FishTypesStrip_NoFishBiomes.xml`, on the donor's abstract parent): read the loaded
   `RM_FeverWood.fishTypes`; if it is non-empty (inherited or defaulted), strip it the same way. If it is
   already empty, record that and do nothing.
4. **The three Biomes! Team ports leave the Fever Wood campaign roster:** remove the `RSW_GlowSlug` 0.5,
   `RSW_JewelBeetle` 0.2 and `RSW_AcidSlug` 0.05 rows from `WildAnimals_FeverWood.xml` (l.74/78/82 and the
   header list l.42–44). They are invented (Q11a), their descriptions place them elsewhere, and the ratified free
   cast fills each slot (`FEVERWOOD_RM_CAST_COMPLETION_1`: grolth for the acid slug). ⛔ **Their other homes
   are untouched** (the Webwork, the Lantern Deeps): this is this biome's own sitting row, never an eviction
   sweep (2026-09-22 ruling). The seven canon rows (urusai, nuna, gelagrub, convor, longtail gorg,
   whisperbird, fambaa) and the hydenock, jogan, chak-root stay.
5. **Guards:** replace the top-level `<Operation … MayRequire=…>` on all three ops of
   `WildAnimals_FeverWood.xml` with `PatchOperationFindMod` (inert in 1.6, `PATCH_MAYREQUIRE_GUARD_INERT_1`).

Depends on: nothing. The free-text canon scrub and the ten `RUT_` defs are `BIOME_TIER_CLEANUP_1`'s (b) and
(c) (see its 2026-10-02 additions); the dianoga over the limbs is `FEVERWOOD_DIANOGA_GIANT_MAP_1`.

## criteria

- With the campaign loaded: `jawa/get_defs` `BiomeDef/RM_FeverWood` (`success`, `foundCount` 1): loaded
  `preventGenSteps` contains `ScatterShrines`; loaded `label` equals the Ashkarr label the donor carries.
- With the free mod alone, if spec 1 chose the free declaration: the same read still contains `ScatterShrines`.
- Loaded `RM_FeverWood.wildAnimals`, parsed as elements: no `RSW_GlowSlug`, `RSW_JewelBeetle`, `RSW_AcidSlug`;
  all seven canon rows present. Loaded `RM_Webwork` / `RM_LanternDeeps` (and any other biome that cast them
  before) still hold each of the three at its prior commonality (diff against a pre-change def read).
- Loaded `RM_FeverWood.fishTypes` is empty.
- Offline parse of every file touched: no `<Operation>` node carries `MayRequire`.
