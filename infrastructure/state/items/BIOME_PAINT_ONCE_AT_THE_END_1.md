# BIOME_PAINT_ONCE_AT_THE_END_1 — the worldmap gets painted once, after every biome is a mod

## the ruling

Owner, 2026-09-20, verbatim:

> *"Don't worry about worldmap painting. Once we have all the biomes in mods we will do
> the painting once and for all."*

Given in the same sitting as, and governing, the tier ruling recorded in
`design/RimMandrake/biome_mod_architecture.md`:

> *"please make sure that each of our actively converted biomes is its own mod at the
> RimMandrake level. Lanterndeep, two deserts, pyrelands, the rot, etc. only Star Wars
> creatures become patches applies from the utinni scenario layer."*

## what it decides

1. **Painting is a SINGLE TERMINAL STEP.** Build every biome mod first; paint the planet
   once, at the end. ⛔ No per-biome repaint, ever.
2. 🔑 **No biome's work is gated on its tile count.** A biome mod being "on zero tiles"
   is the expected mid-migration state, not a defect and not a reason to defer anything.
3. ⛔ **Stop citing tile counts as evidence of what is built.** They answer a question
   nobody is asking until the painting pass.

## why this ruling was needed — the trap it closes

`world/ASHKARR_WORLDMAP_tiles.csv` is a **record exported from the savegame**, not the
planet. Its own freeze stamp (`ASHKARR_WORLDMAP_tiles.csv.frozen.json`, 2026-09-07,
owner ruling) says so outright:

> *"This CSV is now EXPORTED FROM THE SAVEGAME … It is a RECORD of the planet, not a
> rival to it. To change the world, change the WORLD and re-export — never edit this
> file and import it back."*

and, from the same stamp, the lesson that had already been paid for once:

> *"Any future live-vs-CSV validate must state which direction it is evidence for."*

🔴 **It was last exported 2026-09-12, and BENCH read it on 2026-09-20 as the state of the
planet.** That produced `PYRELANDS_WRONG_BIOME_DEF_1` — filed on the reading
`ZBiome_Grasslands` 222 tiles / `RM_FE_Pyrelands` 0 — while a committed comment from a
**live** read on 2026-09-19 asserts the exact reverse. Both cannot describe one moment,
and the live world decides. The item's premise was therefore never established.

⇒ Under this ruling the question is moot rather than merely unresolved, which is the
better outcome: nothing downstream should have depended on it.

## what is still true and still owed

- The **offline** half of `PYRELANDS_WRONG_BIOME_DEF_1` was real and landed at `e07eca2d0`:
  the ash storm was being added to a *More Vanilla Biomes* donor def instead of to
  `RM_FE_Pyrelands`, and three files carried false prose about which def the world
  carries. That was a content-wiring defect, independent of any tile count.
- Duplicate defs in **our own source** remain a real defect and are not a world question:
  `RM_Greentide` (123 lines) beside `RUT_Greentide` (287 lines, sheet-derived), and
  `RM_GelatinousSlime` beside `RUT_Slime`. Resolution belongs to the architecture spec.

## verify

Every biome named in `design/RimMandrake/biome_mod_architecture.md` ships as its own
RimMandrake mod with its own BiomeDef and Mod Settings, before any painting is attempted.

## criteria

The planet is painted exactly once, from a settled set of biome mods — and no item in the
queue is blocked on a tile count before then.
