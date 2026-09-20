# DEAD_BIOME_DEFS_IN_PROSE_1 — the repaint cleaned the table, not the prose

## what is wrong

The world was repainted onto our own `RUT_*` biome defs. `BIOME_BINDINGS_TABLE_STALE_1`
regenerated the def→sheet **table** (29 rows → 27, closed `ee5b61acf`). It did not
touch the **prose** — the item files, design sheets and specs that name a biome def
in a sentence.

Three were found by accident on 2026-09-20, all in work that was about something
else:

| where | said | actually |
|---|---|---|
| `OCULAR_OVERDRIVE_SITE_1` §spec | site is 3 `AB_OcularForest` tiles | `RUT_Contagion`, **179** tiles |
| `OCULAR_OVERDRIVE_SITE_1` §plot weave | Rust Cathedral is `AB_MechanoidIntrusion` | `RUT_RustCathedral`, **236** tiles |
| `PYRELANDS_WRONG_BIOME_DEF_1` | (the whole item) | content wired to a def with **0** painted tiles |

🔑 **Two of those three were in the SAME FILE**, and the first was corrected hours
before the second was noticed. Finding them one at a time is not working.

## why it matters — it is not the name, it is what rides on it

A dead defName in prose is harmless. **The numbers and facts attached to it are
not.** The Ocular case is the worked example: *"MEASURED 45.5° of arc apart"* was
derived between `AB_OcularForest` and `AB_MechanoidIntrusion` — **both dead**. It
read as a hard measurement and had been sitting there as something to reason from.
It is now marked UNMEASURED against the live pair.

So the sweep is not a find-and-replace. **Every dead-def mention has to be checked
for what was computed from it.**

## the work

1. **Build the dead-def list** from the painted CSV: every biome defName appearing
   in `src/`, `design/` or `infrastructure/state/` prose that is NOT in
   `world/ASHKARR_WORLDMAP_tiles.csv`. The old names are known —
   `AB_*`, `ZBiome_*`, `COMIGO_*`, bare `Desert`/`ExtremeDesert`/`Wasteland`/
   `AridShrubland`/`PoisonForest`/`Scarlands`/`LavaField`/`Volcano`/`BiomeGRimond`/
   `BiomeCypreJungle`.
2. **For each hit, classify before editing:**
   - a live-def rename → correct it, with the live tile count;
   - a NUMBER derived from dead defs (arc, distance, tile count, adjacency) →
     🔴 **mark UNMEASURED, do not recompute silently** — a recomputed number
     wearing the old sentence is worse than a flagged one;
   - a historical statement about what used to be → leave it, it is provenance.
3. ⚠️ **Do not rewrite `items/closed/`** — closed items are the record of what was
   believed at the time.

## Watch out

- 🔴 **`ZBiome_Grasslands` is NOT dead** — 222 painted tiles, the one surviving
  non-`RUT_` def. A regex that kills every non-`RUT_` name will break it.
- ⚠️ A bare name like `Desert` or `Wasteland` appears constantly as an English word.
  Match only inside backticks, def references and `<...>` tags; a blind
  substitution will maul ordinary prose.
- ⚠️ **The biome assignment is redone at the world repaint**
  (`WORLD_REMAKE_FINAL_STEP_1`), so a def with zero tiles is not automatically a
  defect — it may simply not be painted yet. Correcting a NAME is always right;
  concluding "this content is mis-wired" is not, and needs that item read first.
- 🔑 The painted CSV is **one instrument**, and `GRASSLANDS_TILES_CSV_STALE_1` is
  open against it. Good enough to correct names; say so for anything load-bearing.

## verify

No live doc names a biome defName absent from the painted CSV, except as explicit
history. No number in live prose was computed between two dead defs without being
marked UNMEASURED.

## criteria

Nobody reasons from a fact measured about a place that no longer exists.
