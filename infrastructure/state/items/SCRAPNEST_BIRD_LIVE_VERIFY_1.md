# SCRAPNEST_BIRD_LIVE_VERIFY_1 — live-verify the scrap-nest bird: spawn, nest-building, hoarding, loot

## which NEW mechanism has never been seen

**A wild animal spawning a BUILDING and hauling items into it.** Nothing in
this repo has done that before, and nothing offline can answer it: the think
tree, the job and the carry are all runtime behaviour, and a def check cannot
tell a job giver that fires from one that silently returns null forever.

Everything else about `RSW_ScrapNestBird` is an ordinary 49th-pawnkind case
and was closed offline with `SHRUBLAND_SCRAPNEST_BIRDS_1` — stats, art paths,
egg defs, biome wiring, the nest's own `CompProperties_Spawner`. Do **not**
re-verify those here.

## the three lines a live check owes

**The calls** (`rimbridge`; a minimal-list quicktest map is enough, and the
mod set must include `mandrake.rsw.swbestiary`):

1. `jawa/spawn_pawn` several `RSW_ScrapNestBird` on an open map — several, not
   one, because one bird's behaviour is indistinguishable from RNG.
2. Scatter ~10 `ComponentIndustrial` / `Silver` on the ground within ~20 cells
   of them, well OUTSIDE any home area.
3. Let it run a few in-game hours, then `jawa/list_things` for `RSW_ScrapNest`
   and for the scattered items.

**The expected POSITIVE readings** (never "no error"):

- ≥1 `RSW_ScrapNest` exists on the map that nothing placed but the birds, and
  it is adjacent to standing vegetation (the giver prefers a plant-cover cell
  and only falls back to bare ground).
- At least one scattered item has MOVED and is now within ~2 cells of a nest.
- A selected bird's job report reads **"carrying … back to the nest."** at
  some point — that string is `RSW_HoardScrap`'s own `reportString` and is the
  only unambiguous proof the JobDriver ran rather than the bird wandering.
- Nest count stops at `maxNestsPerMap` (4) and no two nests sit closer than
  18 cells.

**How a pass could be false:**

- 🔴 **Nests appearing is NOT proof the hauling works.** Nest-building is a
  direct `GenSpawn` inside the job giver; the haul is a separate JobDriver.
  Seeing nests and calling it done would verify half the mechanism. The job
  report string is the part that cannot be faked.
- 🔴 **Items near a nest is not proof either** — the nest's own
  `CompProperties_Spawner` puts `ComponentIndustrial` beside it on its own
  every 1–2 days. Only an item you PLACED, identified before and after, proves
  a haul. Place `Silver` (the spawner never makes silver) to remove the
  ambiguity entirely.
- A bird that is hungry, tired, egg-bound, frightened or downed is gated OFF
  by design, so a quiet map can look like a broken mechanic. Spawn well-fed
  birds and keep hostiles away.
- Check the "never steals" guard too, which is the whole reason
  `SCRAPNEST_BIRD_BASE_THEFT_1` is still an open owner card: put a stack
  inside a home area and confirm after several hours that it has NOT moved.

## Watch out

- The running game must have loaded the CURRENT
  `RimMandrakeBeastMechanicsRSW.dll`. The game that was up on 2026-09-20 had
  the old one; the deployed copy is now byte-current, but a session started
  before that deploy will not have the new classes and every check here will
  read as a clean negative.
- `RUT_AridShrubland` carries the bird at commonality 0.45, but a biome with
  zero tiles is the expected mid-migration state — do NOT wait for a wild
  spawn on the campaign map. Spawn them.

## criteria

The four positive readings above are observed and recorded here, or a specific
defect is filed. Whoever proves it closes it.
