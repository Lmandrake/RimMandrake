# BIOME_MOD_SPLIT_EXECUTION_1 — carry out the biome mod split

## the ruling

Owner, 2026-09-20, verbatim: *"please make sure that each of our actively converted
biomes is its own mod at the RimMandrake level. Lanterndeep, two deserts, pyrelands, the
rot, etc. only Star Wars creatures become patches applies from the utinni scenario
layer."*

Governed by `BIOME_PAINT_ONCE_AT_THE_END_1` — the planet is painted once, at the end.

## the plan

`design/RimMandrake/biome_mod_architecture.md` (526 lines) is the spec: the full mapping
of 27 painted BiomeDefs to **26 RimMandrake mods** (23 standalone + 2 kits + the Lantern
Deeps injection layer), the RimMandrake-vs-Utinni boundary test, the twin resolutions and
the ordered migration.

## ⛔ BLOCKED on the owner — 10 questions, §7 of the spec

Do not start Phase A without answers. The three that change the most work:

- **Q2 — names.** The two deserts and the shrubland have no ruled names; the spec's
  `RM_DeepDesert` / `RM_ShadowDesert` / `RM_FogShrubland` are the designer's inventions
  and are marked as such.
- **Q5 — `Scarlands` collides with a vanilla 1.6 biome name.** A rename may be forced.
- **Q3 — rename `RM_FE_Pyrelands` → `RM_Pyrelands` now?** Cheapest before the split, not
  after.

Q1 (two kits or 27 mods), Q4 (is FloodedCanyon the Cracked Lands), Q6–Q10 are in the spec.

## what is already established and needs no ruling

- 🔴 **A `workerClass` is inert here.** `BiomeDef.Worker.GetScore` is called only from
  `WorldGenStep_Terrain` (MEASURED, RimSage) — and there is no worldgen. A self-placing
  biome def can never be painted onto the frozen world. This is why `RM_FE_Pyrelands`
  was built beautifully and reached nobody.
- 🔴 **The `tileBiomeDeflate` hazard.** The save stores biomes as a DEFLATE grid of 2-byte
  def shortHashes, so a biome defName change is not a text edit. The spec puts every
  `RUT_` deletion at Phase B step 4 — *after* the one paint and re-save — for this reason.
- **102 `RSW_` fauna entries sit inline across the 26 `RUT_` defs** (50 of them in
  `RUT_Desert`). Under the ruling these all become Utinni-layer patches.
- **Six `mandrake.rut.*` kit mods are biome mechanics filed at the wrong tier**
  (RotSporeKit, RustCathedral ×3, ScarlandsLadder, PyrelandsMechanics) and fold into
  their biome's RimMandrake mod.
- **`RUT_LanternDeeps` already exists as our own def** (178 lines, live in the 618-mod
  dump). ⚠️ An earlier BENCH claim that the Lantern Deeps "rides a donor def" was wrong.
  It remains an **injection layer**, not a painted biome — owner ruling 2026-09-06,
  *"that was a mistake"* — and its sheet is FROZEN.
- **Pyrelands' worker namespace is `RimMandrake.StarWars.FireEcology`**, a tier-grammar
  violation; fix it in the same pass.

## spec

Execute the phases in `biome_mod_architecture.md` §5, in order, once §7 is ruled.

## verify

Every biome in the mapping table ships as its own RimMandrake mod with its own BiomeDef
and its own Mod Settings, no `RUT_` biome def remains, and `run_selftests.py` is green.
⛔ Do not verify against a tile count — see `BIOME_PAINT_ONCE_AT_THE_END_1`.

## criteria

The RimMandrake layer is a set of biomes any RimWorld game could load; the Utinni layer
is the Star Wars cast and this campaign's wiring, and nothing else.
