# DEPRECATED — the painted lineage of Ash'karr

**Superseded 2026-09-07 by `world/ASHKARR_WORLDMAP_tiles.csv` and
`world/ASHKARR_WORLDMAP_links.csv`, which are now exported from the SAVEGAME.**
Owner's ruling, this date. Nothing in this folder is authoritative about the
planet. It is kept because two weeks of real decisions are recorded in it, and
because the divergence below has to stay legible.

## What these files are

`PAINTED_tiles.csv` and `PAINTED_links.csv` are the last state of
`world/ASHKARR_WORLDMAP_*.csv` before the rebase. They were seeded by
`src/RimMandrake/Utils/ashkarr_paint.py` and then surgically edited for weeks by
`ashkarr_settle.py`, `ashkarr_shore_and_ice.py`, `ashkarr_contagion_summits.py`,
`ashkarr_horrorwastes_dissolve.py`, `ashkarr_three_seas.py` and others.

## What they are NOT

⛔ **They were never a record of the planet.** They are one lineage of a
multi-part worldgen process whose other half — the savegame — was edited
independently, by the bridge, by the debug menu, and by the owner's own hand
while looking at the globe. No script here can reproduce those edits.

The two lineages were treated as one thing for two weeks. They were never the
same planet. Measured 2026-09-07 against `WORLDMAP_V1_original_e.rws`, the last
state the owner inspected and approved:

| field | tiles differing |
|---|---:|
| biome | 5,411 |
| **hilliness** | **7,275** — a third of the planet, in both directions |
| elevation | 787 |
| **road edges** | the links CSV shared only **77** of the save's **1,399** |

## The two failures worth carrying forward

🔴 **1. An importer that only ever adds.** `jawa/world_links_import`'s
`clearFirst: true` clears only the tiles the CSV *names*. Importing the painted
links on top of the save's roads therefore added ~1,300 edges and removed none,
leaving 2,417 live edges in 98 components where the save had 1,399 in 7. The
owner's four-class road design — day roads, dusk roads, night trails and the
dead ancient highway — was never damaged. It was **buried**.

🔴 **2. A verification that could not fail.** The 2026-09-07 worldmap redo
imported this CSV wholesale, flattening the planet (`Impassable` 355 → 56,
`Mountainous` 2,428 → 1,495 — a change nobody asked for), then validated live
against the same CSV and reported *"21,872/21,872 tiles, 0 mismatches"*.

**That was true and meaningless.** A 100% match against the artifact you just
imported proves only that the import worked; it says nothing about whether the
import was wanted. Any validate of live-against-CSV must state which direction it
is evidence for — and after an import, it is evidence for nothing.

## If you need something from here

Take the *decision*, not the file. The road classes and their reasoning live in
`world/_roads/compose.py`; the biome moves live in the `ashkarr_*.py` scripts and
in the biome sheets under `design/Jawa/worldbuilding/biomes/`. Re-derive against
the canonical CSV, which is now the world.
