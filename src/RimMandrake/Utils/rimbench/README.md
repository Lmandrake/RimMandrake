# RimBench

Tools for driving a live RimWorld from outside — testing mods, measuring
results, and **printing content onto a map**.

Read `skills/rimbridge/SKILL.md` first. Traps are in
`skills/rimbridge/references/traps.md` and every one cost a real debugging
cycle.

## Layout

| module | does | needs a game? |
|---|---|---|
| `core.py` | session, and **verified mutation** | yes |
| `scatter.py` | procedural distribution maths | **no** — pure geometry |
| `build.py` | rooms, walls, floors, furniture, siting | yes |
| `terrain.py` | natural terrain, floors, capture/restore | yes |
| `formations.py` | crater, wreck, cavern, outpost, geyser field | yes |

`scatter.py` has no dependencies and no knowledge of RimWorld. It is testable
offline, and it is the part most worth reusing.

## The rule

> `success: true` means the tool RAN, not that the game CHANGED.

`Session.mutate()` takes a verifier that reads the world back through an
independent channel and **raises if nothing moved**. That is not paranoia: a
silent no-op once cost 45 wasted calls before anyone noticed.

```python
from rimbench.core import Session

with Session() as s:
    s.god(True)
    tid = s.spawn("Apparel_PlateArmor", 100, 100)   # verified present
    s.set_stuff(tid, "Plasteel", at=(100, 100))     # verified changed
    s.set_quality(tid, "Legendary", at=(100, 100))
    print(s.summary())
```

## Printing content

```python
from rimbench.core import Session
from rimbench.build import Blueprint, furnish_bunkroom
from rimbench import formations

with Session() as s:
    s.god(True)

    bp = Blueprint(s, "bunkhouse")
    bp.room(200, 140, 13, 11, floor="woodplankfloor")
    furnish_bunkroom(bp, 200, 140, 13, 11)
    bp.plan()      # dry-run: free, mutates nothing, prints what would fail
    bp.build()     # then commit

    formations.crater(s, 150, 150, radius=12)
    formations.wreck(s, 120, 90, length=20, rotation=0.7)
    formations.cavern(s, 60, 60, chambers=4)
```

**Always `plan()` before `build()`.** Two workbenches failed in the first live
run purely because they were handed corners with no clearance; a dry-run costs
nothing and turns that into a printed warning.

## What works

Verified: spawn things and pawns, set material and quality, dress and strip
pawns, build any architect structure in rectangles, validate placement, find
legal sites, advance time exactly, screenshot, save.

✅ **Natural terrain IS painted** — soil, gravel, sand, rock and water — through
the `JawaBench.BridgeTools` companion, not through the bridge's own drag-based
`Set terrain (rect)`, which still silently does nothing. That gap closed
2026-08-12 and this file used to say it was the highest-value work remaining.

Everything goes through `TerrainPainter`, which picks the fastest route the
running game offers:

```python
tp = TerrainPainter(s)
tp.capture(cellmap)     # one call, and it REFUSES a partial read
tp.paint_map(cellmap)   # a 977-cell crater: one call
tp.restore()            # exact, verified over every cell
```

🔑 **Call count is the only cost that matters.** A 6×6 rect is 15 ms; the same
411 cells as a dithered crater were 103 calls and 5.15 s. `paint_map` decomposes
once and packs everything into as few `jawa/set_terrain_batch` payloads as the
companion's guards allow — that is the whole reason the batch tools exist. Never
loop a per-cell call.

🔑 **Laying a floor still destroys the vegetation under it,** and is still the
only *proven* destruction primitive. Whether painting terrain also clears plants
is an open question — `src/RimMandrake/bridgetools/prove_capture_restore.py` answers it on the
next load. Until then, do not assume either way.

## Prove it offline first

```bash
python3 src/RimMandrake/Utils/rimbench/selftest.py      # no game, no socket, under a second
```

64 checks over the whole pipeline between "the generator produced a cell map"
and "the bytes leave the client": exact-cover decomposition, multi-terrain
planning, ops round-trip against a port of the C# parser, chunking, guard
headroom, capture round-trip. A game load is 23–30 minutes; none of this needs
one.

## Standalone scripts

* `src/RimMandrake/Utils/rimbridge_lineup.py` — one of every pawn kind in a grid
* `src/RimMandrake/Utils/modset_builder.py` — minimal dependency-complete mod lists
  (`--tier bridge` is 3 mods and loads in seconds)

**Prove new work on the 3-mod tier.** Three suspects instead of five hundred.
