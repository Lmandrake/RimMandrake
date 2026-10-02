# GELATINOUSSLIME_GAPPO_FAMILY_1 — the gappo family: the slime grazer moved to RM_, plus a lesser and a greater gappo

**Free tier**, `mandrake.rm.gelatinousslime`. Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §1 (a) 1 and (b), §3 (filter-feeder row), §4 row 0a, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT). Underlying rulings: sheet `the_slime.md` §4 (owner's rulings on the filter-feeder family, the flying aristocracy, the resistant characters), Q14 of `design/RimMandrake/biome_mod_architecture.md` §7 (by card 2026-09-23: the free def stays donor-free, holes filled with creatures of ours), Q11a (every `RM_` roster rich enough to stand alone).

## What exists

- `RUT_SlimeGrazer` (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_SlimeGrazer.xml`): invented, no canon
  claim, wired **only** to the frozen twin `RUT_Slime` (0.5), deleted with the twin at the repaint. Wrong tier
  under Q11a. Its texPath resolves to nothing: no PNG in `src/`.
- Art: two finished generations in the artpipe, `done/rutslimegrazer_v1_*` and `done/rutslimegrazer_v2_*`
  (`artpipe_state.py find rutslimegrazer`: 20 hits, 2026-10-02). No owner ruling on either found in
  `Transient/*.decisions.json`.
- `RM_GelatinousSlime/wildAnimals`: two rows (`RM_Gelatid` 3.0, `RM_Titanoslime` 0.12).

## spec

1. Port the grazer to `RM_` as the **gappo** (the family's middle size), wiring the `v2` art (show v1/v2 side by
   side in the item's close note; the owner has not ruled between them). Label under the 2026-09-24 slime law
   (a scoop-mouthed solid body takes the -o/-um endings); drafted names passed `check_pseudo_sw_name.py` (§3).
2. Add the **lesser gappo** (a skimming swarm) and the **greater gappo** (slow, bs about 3, a bulk feeder whose
   scoop leaves a clean channel behind it). One stem, three sizes (the oomb precedent). Numbers `// INVENTED`.
3. Wire all three inline on `RM_GelatinousSlime/wildAnimals`; delete `RUT_SlimeGrazer` and its twin row.
4. Correct the BiomeDef's *"deliberately thin… Spike C"* header (Q14 overruled it; the visitors stay as the
   trace tail).
5. Each a one-home species (the Slime only). Resistant by identity (filter-feeders on the body), per sheet §3.

## criteria

- `jawa/get_defs` `ThingDef/RM_<gappo names>` `foundCount` 3; `ThingDef/RUT_SlimeGrazer` `notFound`.
- No `RUT_SlimeGrazer` string left in `src/` (offline parse).
- Art: gappo from the artpipe `v2`; lesser and greater from `gelatinousslime_turn1_2026-10-02.csv`.
