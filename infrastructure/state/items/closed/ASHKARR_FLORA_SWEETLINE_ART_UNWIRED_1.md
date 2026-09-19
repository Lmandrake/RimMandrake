## spec

The prior pass (2026-09-09) correctly refused to pick among the 14 recovered
`RUT_SweetlineTree` candidate renders solo — that is an owner art call,
already documented as such in
`src/RimUtinni/AshkarrFlora/_artsrc/sweetline_orphans_2026-09-06/README.md`
and `TREE_GRAPHICS_OWNERSHIP_1.md` Owed#1 — and blocked on that item instead
of guessing.

## ruling — owner, 2026-09-18, given directly in conversation

Verbatim: *"I absolutely love ALL of them. Please accept them all as
alternative art that it rotates between."* Separately: *"Make that sweetline
tree ten cells wide."* And, confirming he already knew the 14 sources were not
uniform: *"Though they might need to be unified in terms of resolution..."*

This is the ruling the item was blocked waiting for. It answers both open
questions at once: **which** candidates (all 14, not one) and **how they
combine** (rotation, not a single chosen file).

## what was done

- Confirmed the mechanism before naming files: `Graphic_Random`/
  `Graphic_Collection` (engine source, read via RimSage/vanilla Core) calls
  `ContentFinder<Texture2D>.GetAllInFolder(path)`, groups by the filename
  substring **before the first underscore**, and each group with no cardinal
  suffix becomes an independent `Graphic_Single` sub-variant picked per-Thing
  via `thing.thingIDNumber % subGraphics.Length` — stable per individual tree,
  different trees get different variants. That is exactly "rotates between."
  So the 14 finals are named `RUT_SweetlineTreeA.png` .. `RUT_SweetlineTreeN.png`
  — bare letter suffix, **no underscore** before the letter, matching the
  mod's own placeholder naming (`RUT_SweetlineTreeA.png`) rather than
  splitting into 14 separately-keyed groups.
- 7 of 14 sources carried a green chroma-key background (per the README's own
  table); ran `chroma_key.py` on those 7 only. The other 7 already had native
  alpha and were left untouched, per the README's explicit recommendation.
- **Scale normalization.** The 14 sources vary in raw pixel size (1254x1254,
  1536x1024, 1198x1313, 1218x1292) and, more importantly, in how much empty
  padding surrounds the tree relative to canvas — a naive resize-to-canvas
  would have made "14 different ancient trees" read as "14 different overall
  scales" instead. Fix: measured each source's own visible-canopy bounding box
  (alpha >= 32, the same floor `conform_sprite.py` uses to keep a handful of
  near-invisible stray pixels from deciding the scale), then fit each
  (aspect preserved) into one shared target frame on a synthetic reference
  canvas via `conform_sprite.py --no-register`. The target frame's proportion
  (~94% width, ~96% height, small ground-level margin) was not invented —
  measured off four real vanilla tree sprites (`Plant_TreeOak`, `TreePine`,
  `TreeTeak`, `TreeCecropia`) with `validate_sprite.py --describe`: vanilla
  trees fill 90-100% of BOTH canvas dimensions, not just width.
- **Canvas size for "ten cells wide".** The README's own established
  convention for this def is the literal `128 px/cell x cells` formula (it
  used exactly 768x768 for 6.0 cells, no power-of-two rounding). Same formula
  at 10 cells: **1280x1280**. Not subject to the skill's ~1280px generation
  ceiling caveat — these are conforms (crop+scale) of already-rendered art,
  not fresh generations, so upscaling headroom from the sources' native
  ~1.0-1.6 MP doesn't apply.
- `plant.visualSizeRange` `5.0~6.5` -> `7.7~10.0` — same min:max spread ratio
  as the original (5.0/6.5 = 7.7/10.0), not collapsed to a fixed value.
- `graphicData.shadowData` left **unchanged**, deliberately. Checked vanilla
  Core (`Plants_Bases.xml`): `Plant_TreePine`'s `visualSizeRange` max is 50%
  larger than plain `TreeBase`'s (3.0 vs 2.0), yet its shadow `volume` is
  *smaller* (0.15/0.3/0.15 vs 0.2/0.35/0.13) — the shadow ellipsoid tracks the
  trunk's ground footprint, not the canopy's visual size, and vanilla shows no
  scaling relationship between the two. Scaling shadowData by 10/6.5 anyway
  would have been exactly the "ceiling fields break when doubled" trap
  (CLAUDE.md).
- Validated every final: `validate_sprite.py --describe` on all 14 — canvas
  1280x1280, real alpha, corners `[0,0,0,0]` (no chroma spill), 14 distinct
  sha256 (no accidental duplicate files). Built and looked at a contact sheet
  (`Transient`-equivalent scratch, not committed) — consistent scale across
  the set, no fragments, no truncation. `validate_patch.py` against the def
  change with the full live mod set (`--mods-config` + `--defs` covering
  `RimWorld/Data`, `RimWorld/Mods`, and the Workshop content folder): **OK, 0
  errors, 0 warnings**, 634/634 active mods found on disk.

## not done this pass (BELT/no-bridge, deliberately)

- No live spawn / in-game look. `TREE_GRAPHICS_OWNERSHIP_1.md` Owed#2 (spawn
  `RUT_SweetlineTree`, confirm no BetterTrees rescale interference in the
  live log) is unchanged and still open — this pass never touched the bridge,
  `ModsConfig.xml`, or a restart.
- Deployment (`deploy_custom_mods.py --mod AshkarrFlora --apply`) not run —
  writing to the repo is not deploying; that is a separate, bridge-adjacent
  step Owed#2 already names.

## criteria
- [x] All 14 `RUT_SweetlineTree{A..N}.png` exist at a consistent canvas and
      scale, pass `validate_sprite.py`.
- [x] `visualSizeRange` reflects the owner's "ten cells wide" ruling.
- [x] Def change passes `validate_patch.py` against the live mod set.
- [ ] Live spawn confirms art renders and BetterTrees does not rescale it
      (owned by `TREE_GRAPHICS_OWNERSHIP_1.md` Owed#2, still open).
