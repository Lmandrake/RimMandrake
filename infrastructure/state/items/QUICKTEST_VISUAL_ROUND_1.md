# QUICKTEST_VISUAL_ROUND_1
One throwaway map answers every spawn-and-look left in the queue

Created by CHECK 2026-08-21. A quicktest map costs ~90 seconds
(`skills/rimworld-debug-testing`); two items were each waiting for their own.

## spec

**Absorbed, every clause carried:**

| absorbed | what must be seen |
|---|---|
| `GRIMTERRA_JUVENILES_RENDER_1` | a juvenile GRiNDTerra tortoise and a juvenile pinkbird DRAW, instead of throwing at every spawn |
| `ASH_STORM_OVER_PYRELANDS_1` | an ash storm over a stormy-savanna tile: grey sky, labelled correctly, with no volcano text in the description |

🔑 **Two more items belong in the SAME window and are deliberately NOT absorbed**, because
each carries a clause a shared round would blur:

- `RAKATA_SLEEPERS_LOOK_RIGHT_1` — also carries an encounter-difficulty regression clause,
  which is not a look.
- `PHYTOKIN_BARK_EAST_LOOK_1` — its outcome decides whether a deployed mod ships or is
  retired, which is a bigger consequence than the round.

⇒ **Run all four in one map.** Absorbing only the two that are purely "spawn it and look"
keeps the other two answerable on their own terms.

## verify

Create one dev quicktest map through the bridge, spawn each subject, look, and record
what was seen — a description per subject, not "no errors".

⚠️ **Hash every screenshot.** `rimworld/screenshot_cell_rect` photographs the TOP WINDOW,
not the map: four `success: true` calls once returned four byte-identical PNGs of the
Debug log (`skills/rimbridge/references/traps.md`). Identical hashes mean you photographed
the same window twice, not that the subjects look alike.

## criteria

- ✅ **PASS** when both absorbed subjects have been seen and described from one map.
- ❌ **FAIL** if either draws magenta, throws, or cannot be spawned.
- ⛔ **NOT in scope:** anything about the campaign. This is a scratch map and nothing on
  it is kept.
