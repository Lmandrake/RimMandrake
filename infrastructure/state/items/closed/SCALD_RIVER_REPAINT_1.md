## ⛔ THE OBVIOUS APPROACH IS A NO-OP — read this before planning anything

**Do NOT "reverse the river links".** Read from the RimWorld source 2026-09-07
(`WorldGrid.OverlayRiver`): a river edge is written **symmetrically** — both
tiles get a `RiverLink` pointing at the other — so **the edge stores no direction
at all.** Swapping the `a`/`b` columns of a links row changes nothing.

## how direction actually works

- Direction is **`SurfaceTile.riverDist`** (int per tile; saved to the world as
  the byte array `tileRiverDistances`).
- `OverlayRiver`'s last line: `toTile.riverDist = Max(toTile.riverDist,
  fromTile.riverDist + 1)`.
- `WorldGenStep_Rivers` seeds its flood-fill from **coastal Ocean tiles** and
  extends upstream ⇒ **riverDist counts hops from the MOUTH: 0 at the mouth,
  rising upstream.**
- `TileMutatorWorker_River`, `_RiverConfluence` and `_RiverIsland` all order a
  tile's links by the neighbour's `riverDist` at map generation. **Lower
  riverDist = downstream.**

## the spec

🔑 **Renumber `riverDist` along the five Scald rivers so the SCALD end holds the
MAXIMUM, not the minimum.** No elevation change. No link edited.

⭐ **This means [R1] costs the painted map nothing** — the Scald can stay at
−350 m, stay an ocean by the engine's rules, and still be the source of the
world's rivers, exactly as the owner ruled.

## measured inputs

`design/Jawa/worldbuilding/data/river_graph_2026-09-07.md` + `.csv` (308
river-linked tiles, 292 river links, from `world/ASHKARR_WORLDMAP_tiles.csv` and
`ASHKARR_WORLDMAP_links.csv`):

- **16 distinct rivers.**
- **5 touch `RUT_TheScald`** — R02, R03, R05, R06, R12. These are the rivers to
  renumber.
- R02 also touches `RUT_TwilightSea` — do not double-count it.
- 9 rivers end in a terminal basin; 2 (R09, R11) reach `RUT_GreySea` without
  touching the Scald and are **out of scope**.

## 🔴 UNMEASURED — the first thing to do, and it needs the live game

**`riverDist` is not in `ASHKARR_WORLDMAP_tiles.csv`, so we do not know what the
frozen world actually holds.** Our rivers were applied by `world/_rivers/apply.py`,
which may never have set it at all — in which case every tile reads 0 and the
renumbering is a fresh authoring job rather than a correction.

Also unconfirmed: **whether the bridge exposes `riverDist` for writing.** Check
the `jawa/world_*` tool list before planning a write; if it does not, this item
needs a companion-DLL tool first (`rimbridge-companion`).

⚠️ `riverDist` is stored as a **byte** — a river longer than 255 hops cannot be
numbered.

## gates

- Blocked on `ASHKARR_RIVER_LEDGER_1` (R18: the ledger is authored first, then
  the repaint runs from a finished spec).
- The frozen world: back up, apply in batches, `world_commit`, and **read back
  with a getter — never trust the write's return value**.
