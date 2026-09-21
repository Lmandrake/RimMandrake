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

## LIVE-VERIFIED 2026-09-21 — all four positive readings, plus the theft guard

Run environment: `shrublandfauna` tier (19 mods, all five DLC), quicktest map,
temperate forest so standing vegetation is everywhere. The deployed
`RimMandrakeBeastMechanicsRSW.dll` was confirmed byte-current before launch
(`deploy_custom_mods.py --mod SWBestiary` → "in sync (2420 files, 96 held)") and
`jawa/get_defs` resolved `ThingDef/RSW_ScrapNestBird`, `ThingDef/RSW_ScrapNest`
and `JobDef/RSW_HoardScrap` — so the "old DLL" caveat in Watch out is discharged.

### 1. Nests the birds built themselves

Start state at `ticksGame` 8,516: **0** `RSW_ScrapNest` on the map, 6 wild
`RSW_ScrapNestBird` at (70,185)±3, Food and Rest forced to 1.0.

By T=15,000 (≈6,500 ticks): **one nest, `RSW_ScrapNest39189` at (74,177)**, and
all six birds on job `RSW_HoardScrap`, three of them "Carrying: Silver". Nothing
else on the map places that def.

Final nest set, all four adjacent to standing vegetation (plants in the
8-neighbourhood, counted with `jawa/list_things group=Plant`):

| nest | cell | adjacent plants | silver on the nest cell |
|---|---|---|---|
| `…39189` | (74,177) | 5 (Grass ×4, Brambles) | 345 |
| `…39658` | (36,204) | 4 (TreePoplar, Brambles, Grass, TallGrass) | 43 |
| `…39659` | (121,187) | 5 (Grass) | 25 |
| `…39660` | (157,193) | 4 (Grass ×2, TallGrass ×2) | 34 |

### 2. Items that MOVED — placed by me, identified before and after

13 × 20 `Silver` stacks were placed on recorded cells (silver is used precisely
because the nest's own `CompProperties_Spawner` never makes it). By T=23,992,
**10 of the 12 non-home stacks were off their cells** and a stack that did not
exist before — `Silver39193` — stood at **(74,177), the nest cell itself**,
holding 198; by T=30,000 it held 220 = 11 × 20. This is the half the item warns
is NOT proved by nests appearing.

### 3. The job report string

An animal's inspect pane only renders the job report for a player-faction pawn,
so one bird was moved with `jawa/set_pawn_faction … player` and read back:

```
inspectString : "Female scrap-nest bird, age 6 of New Arrivals | Egg progress: 6.9% | Carrying silver back to the nest."
job           : "RSW_HoardScrap"
```

`Carrying silver back to the nest.` is `RSW_HoardScrap`'s own `reportString`
with TargetA resolved — the unambiguous proof that `JobDriver_HoardScrap` ran.

### 4. The cap and the spacing

Phase B added 18 more birds across five further sites (24 birds live). Nest count
rose to **exactly 4 and stopped**, holding from T=60,000 to T=90,000 with two of
the six bird sites never getting a nest at all — `maxNestsPerMap` 4. Minimum
pairwise distance between the four nests: **36.5 cells**, against
`minNestSpacing` 18.

### 5. The "never steals" guard — distance-matched control, not just an absence

The first pass put a stack inside a painted Home area (`jawa/paint_area
area=home ops=67,202,7,7`) and it never moved — but a non-home stack 17 cells
from the nest did not move either during that window, so absence alone proved
nothing. Re-run as a paired control:

| stack | cell | in Home? | distance to the bird cluster | outcome |
|---|---|---|---|---|
| `Silver39188` | (70,205) | **yes** | ~6 cells | **still there at T=141,478, i.e. 132,962 ticks (≈2.2 in-game days) after placement** |
| control, 20 Silver | (70,211) | no | ~6 cells | **gone from its cell inside the first 20-second play window** |

Same def, same stack size, same four fresh birds, same window, distance matched.
`IsTakeable`'s `map.areaManager.Home[t.Position]` test is what holds the first
one. The only thing that stopped the birds hauling in the earlier window was the
`Eligible()` gate doing its job — those birds had dropped to Food 0.47 / Rest
0.32 and three of the six were egg-bound, exactly the designed off-switch.

Screenshot:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\SCRAPNEST_BIRD_LIVE_VERIFY_nest.png`

### criteria — met

All four positive readings observed and recorded above, plus the theft guard
under a control. Closing.
