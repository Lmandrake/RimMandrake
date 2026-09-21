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

## ✅ UNBLOCKED — all 10 questions ruled 2026-09-21

Every question in §7 of the spec is answered. **Read §7 for the rulings; do not re-derive
them from this item.** The four that changed the plan:

- **Q1 was not a yes/no — it re-scoped the mod list.** Verbatim: *"Umbra is a region not a
  biome. The Propane Lake is an ocean-biome made of propane, definitely its own biome.
  Propane, Grey, Twilight, and Scald biomes can all share one mod with options to
  enable/disable each of these biomes in a spawned game."* ⇒ `RUT_Umbra` leaves the biome
  list entirely (own item: `UMBRA_IS_A_REGION_NOT_A_BIOME_1`); Propane + Grey + Twilight +
  **Scald** ship as ONE `TerminalBiomes` mod with a per-biome settings toggle — so the
  Scald moves OUT of its own row. ⛔ The spec's old `propanelakes`/`terminalseas` pairing
  is dead; §2's three affected rows are already rewritten.
- **Q4 — Flooded Canyon IS the Cracked Lands.** One biome, one mod, campaign label
  "the Cracked Lands". The Cracked Lands gets no row of its own.
- **Q8 — `ashkarrflora` DISSOLVES.** Each plant moves into its biome's RimMandrake mod.
- **Q10 — all seven misfiled creatures move**, one sweep, not a per-creature call.

Q3 is executed already: `RM_FE_Pyrelands` → `RM_Pyrelands`, committed at `84d42c63b`
(0 occurrences remain, 3 C# string literals included, 3 assemblies rebuilt clean).
⚠️ That rename is **built but NOT deployed** — the game was running. Deploy before testing.

## ✅ Names ruled 2026-09-21 — ALL FOUR LANDED. Nothing is waiting on the owner.

- **Row 1, `RUT_ExtremeDesert` → `RM_Stillsand`, "the Stillsand"** (`mandrake.rm.stillsand`).
  Owner picked draft row 1 over the recommendation. The campaign label "the Dune Sea" stays
  a Utinni-tier patch over it.
- **Row 2, `RUT_Desert` → `RM_LongShade`, "the Long Shade"** (`mandrake.rm.longshade`).
- **Row 20, `RUT_Scarlands` → `RM_Warscar`, "Warscar"**, article deliberately dropped —
  ruled and the label shipped on FOUNDRY (`SCARLANDS_RENAME_OURS_1`, closed); the defName
  move is row 20's own migration, `SCARLANDS_STANDALONE_MOD_1`.

- **Row 9, `RUT_AridShrubland` → `RM_LeaningScrub`, "the Leaning Scrub"**
  (`mandrake.rm.leaningscrub`) — the sheet's own gesture, everything leaning sunward in a
  wind that never stops.

### Row 9 took a vegetation ruling first, and it is worth keeping

Put the name to the owner, he
answered with the biome rather than the name: *"I had thought the periodic scrub bushes
would grow big as a man and everywhere else is the low fuzz. No? Please check sheet."*
Checked: `arid_shrubland.md` does NOT say that — it puts the entire canopy at knee height
(§"The two floors": "The fuzz is a canopy at knee height") and makes a biped's wrongness
the biome's whole point ("too large to hide in it, too small to be safe over it"). But §1
opens with *"Sightlines are gone. Cover is everywhere, for everything, all the time"*,
which is only true of a canopy at least shoulder-high. **The sheet contradicts itself, the
owner's instinct found it, and the sheet is frozen** — so it went to him as a card.
🔴 **He ruled the knee-high canopy STANDS**, verbatim: *"'cover everywhere' is interpreted
only for smaller things than you. People stand out. Except for the venomvine, that should
be man-height or more."* The false sentences are DELETED from `arid_shrubland.md` (not
bannered) and the sheet carries the amendment block at `f04723b58`. Nothing else in that
sheet moved.

Every other row can start now.

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
