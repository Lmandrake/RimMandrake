# LONGSHADE_RULED_CONTENT_1 — build the Long Shade content the 2026-09-27 sitting ruled

Authority: `design/Jawa/worldbuilding/biomes/long_shade_bedazzle_2026-09-27.md`
**§ Rulings** (all 12 questions ruled same day; that section beats §7's
recommendations where they differ). Sitting: `LONGSHADE_DESIGN_SITTING_1`.

## spec — ruled and buildable now

1. **Tier move, all 14 rows** (§2b of the doc): the invented-name animals leave
   `UtinniPatches/Patches/WildAnimals_LongShade.xml` for `RM_LongShade` proper,
   defNames renamed `RM_`; labels unchanged until the batch-4c naming sitting.
   The shade whale renames to **`RM_Gloomcast`** (owner's own coinage, ruled).
2. **Ultracactus is ours**: `RSW_Ultracactus` → `RM_Ultracactus`, moves out of
   the Utinni patch into the free mod; existing art carries over.
3. **Standalone forage**: new `RM_UltracactusPad` item as `RM_LongShade`'s
   `foragedFood` (pure XML) — closes the standalone-inert forage hole
   (`DESERT_FORAGEDFOOD_INERT_1`'s mechanism one tier down). Art job filed
   (`RM_UltracactusPad`, artpipe 2026-09-27).
4. **Roster cuts per the multi-homing rulings**: gizka and kreetle OUT of the
   Long Shade (gizka's homes are Pyrelands+Stillsand per the 2026-09-14 ruling;
   kreetle's one home is the Stillsand); the dead `AA_SandLion` import row out
   of `rosters/desert.json`. Kudda and truffle mole OUT of the Stillsand's
   wiring (their one home is the Long Shade) — ⚠️ coordinate the
   `RUT_ExtremeDesert`/Stillsand side with `STILLSAND_DESIGN_SITTING_1`'s
   propagation, don't race it.
5. **Dewback IN** as herd/mount: measure its predator flag first (the roster
   suspects flag noise), slow it under the pursuit ban (≤4.4, the wraid
   treatment). **Blurrg OUT** — do not wire it here.
6. **`RM_Dewfringe`** — shade-boundary rim plant, growth gated to shade-line
   adjacency via `RM_MapComponent_ShadeGrid` (shipped; ~50 lines on the
   Leachmoss spawn-gate pattern). Hard ceiling ruled: pale, rim-only, never
   green in quantity. Art job filed.

## ⛔ NOT in this item — gated on the owner's review sheet

The five invented fillers (sollak, gennok, tebbra, dakkra, pirrik) and the
qorrax (ex-cephalope) def work: their art is in the pipe and the owner ruled
"show me what you make for review" — defs land after his sheet verdicts.
Deep-sand terrain is `DEEP_SAND_WALKABLE_TERRAIN_1`.

## verify

Standalone `RM_LongShade` on a minimal list: 16+ fauna incl. herds/pack stock,
forage works (foragedFood resolves), no RSW_/JOE_ reference remains in the free
mod, validate_patch.py clean.

## criteria

The free-tier Long Shade meets Q11a's "rich enough to stand alone" bar without
the Star Wars layer loaded.
