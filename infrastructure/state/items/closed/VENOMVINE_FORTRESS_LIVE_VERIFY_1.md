# VENOMVINE_FORTRESS_LIVE_VERIFY_1 — quicktest the venomvine fortress body-size barrier in a live game

## what is wrong

`VENOMVINE_FORTRESS_PASSABILITY_1` built the whole mechanism offline:
`RM_VenomvineThicket`, the `RM_CompProperties_BodySizeBarrier` /
`RM_CompBodySizeBarrier` / `RM_MapComponent_BodySizeBarrier` triple, two Harmony
patches, two Mod Settings, and the `RUT_AridShrubland` wiring. It compiles clean,
both def files validate at 0 errors and `run_selftests.py` is 69/69.
**Nothing has been seen running, and nothing has been deployed.**

## why a live check is owed — the one line the gate asks for

🔑 **The NEW mechanism never once observed is "a mod supplies the pathfinder a
`PathRequest.IPathGridCustomizer` so that one pawn's route treats cells as
impassable that another pawn's route does not."** Nothing in this repo has ever
touched RimWorld's pathfinding at all, let alone through 1.6's job-system path
grid. Vanilla drives that interface twice itself (`BreachingGrid.CustomTuning`,
`UsedRectPathGridCustomizer`) and in both cases **synchronously**, from
`FindPathNow`, with a fresh `Allocator.TempJob` array per call. This build hands
a **persistent, shared, mutated-between-requests** array to the **asynchronous**
pawn request queue, which is a use of the interface vanilla never makes.

⚠️ **The failure mode is silent in both directions**, which is what makes it a
live check and not a reasoning exercise:

- Too little: the customizer is attached and the A* ignores it (wrong equality,
  wrong grid length, a cached `MapGridRequest` reused from before the grid was
  populated) — a giant walks straight through a thicket, which reads exactly
  like a thicket nobody happened to walk into.
- Too much: the grid marks cells it should not, and something large is
  quarantined on a map it can no longer cross.

Everything else in the build is ordinary and is NOT what this item is for: the
plant def is a plant def, `RM_CompBodySizeBarrier` is the same register-my-cell
shape as `CompContactVenom` (observed live 2026-09-21), and the biome wiring is
a `wildPlants` entry.

## ⛔ NOT DEPLOYED — do this first

Nothing from this build has reached
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`. The assembly
`RimMandrake.EnvironmentalHazards.dll` was rebuilt in the repo only, and **a
companion/mod DLL cannot be written while the game is running** — the build rode
a game-up session with the bridge held by another window, so it was deliberately
left undeployed.

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod EnvironmentalHazards
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod UtinniPatches
```

(plan first, then `--apply`, with the game DOWN for the first of the two).

## the work

On a quicktest map with all five DLC (`modset_builder.py`, every tier `dlc: True`
since 2026-09-19), a tier carrying `mandrake.rm.environmentalhazards` and
`mandrake.rut.utinnipatches`. A `RUT_AridShrubland` map is the realistic subject,
but the mechanism does not need one — `jawa/set_plants` can paint a solid
`RM_VenomvineThicket` stand on any map, and the arena from
`VENOMVINE_LIVE_VERIFY_1`'s third sitting is the proven staging for it.

1. **The line this item exists for.** Paint a solid thicket band that walls a
   corridor. Order a **muffalo** (BodySize 2.4) from one side to the other and
   record the route `jawa/` reports; order a **colonist** (1.0) on the same
   journey; order a **hare** (0.2). Expected: the colonist and the hare cross
   the band, the muffalo's route goes round it or the job fails — never through.
   ⛔ Do not report a pass from "the muffalo went round": it may simply have
   preferred the detour. The band must be the ONLY cheap way, and the control is
   the same order with `bodySizeBarrierEnabled` turned OFF in Mod Settings,
   which must send the muffalo straight through.
2. **The three bands are three different behaviours, not one.** On the same
   stand, measure per-cell crossing time for hare (0.2, free), colonist (1.0,
   `threadMoveCost` 300 → ~33x a normal step) and muffalo (2.4, blocked). The
   claim is three distinct readings, and the middle one is the one a wrong
   `GetPawnCellBaseCostOverride` postfix would silently drop.
3. **The start-cell carve-out.** Spawn a muffalo INSIDE a stand
   (`jawa/spawn_pawn` onto a planted cell) and order it out. It must leave. If
   it stands still failing to path, the carve-out in
   `RM_MapComponent_BodySizeBarrier.CustomizerFor` is not working and a large
   animal caught by map generation is bricked — the worst outcome this build can
   produce.
4. **Wander rejection.** Leave several muffalo undrafted beside a stand for a
   long window and confirm none of them ends up standing on a thicket cell. This
   is the `RCellFinder` half of the move-cost postfix and it is what keeps a
   blocked animal from generating path requests it can never satisfy.
5. **Small creatures still get scratched.** A hare parked on a thicket cell must
   still take `RM_VenomvineScratch` / `RM_VenomvineVenom` on the 2,500-tick
   clock. "Small enough to pass" must never have become "immune" — the parent
   item's point 3.
6. **The desert form is unchanged.** On a `RUT_Desert` map, a muffalo must cross
   an `RM_Venomvine` stand exactly as it did before this build. That is the
   parent item's own "must not change the desert's own use of the plant", and it
   is a one-order check.
7. **Save/load.** Save with a muffalo mid-detour and a colonist mid-thread, load,
   and confirm both still behave. The grids are NOT saved (every barrier
   re-registers from `PostSpawnSetup`), so this is asking whether registration
   during load actually repopulates them. ⚠️ Stage this on the **player's own
   map** — a bridge-generated map on a factionless settlement is written to the
   save and not restored (MEASURED, `VENOMVINE_LIVE_VERIFY_1`).
8. **Map removal.** Leave/abandon a map that held a stand and confirm no Unity
   native-collection leak warning and no crash. `MapRemoved()` disposing a
   `NativeArray` the pathfinder's jobs could still hold is the one genuinely
   unsafe operation in the build.
9. **Wild spawning.** Generate a `RUT_AridShrubland` map and confirm
   `RM_VenomvineThicket` appears at all, and appears as solid islands rather
   than scattered singles — `wildClusterRadius 8` / `wildClusterWeight 25` are
   authored numbers nobody has ever seen produce a stand. ⚠️ Commonality 0.15 is
   deliberately low, so a single map may carry none; use several maps or raise
   the number temporarily rather than concluding from one.
10. **Log triage.** Grep `Player.log` for
    `body-size-barrier-routing` and `body-size-barrier-move-cost`. Those strings
    appear ONLY when a patch failed to arm — silence is the pass.

## verify

A muffalo's recorded route round a band it would cross with the setting off; a
colonist's and a hare's recorded routes through the same band; three distinct
per-cell crossing times; a muffalo that walks out of a stand it was spawned in.

## criteria

Every step above observed, or the defect it found filed. A step that cannot be
staged is recorded as not-run with the reason MEASURED rather than asserted —
the standard `VENOMVINE_LIVE_VERIFY_1` set.

## RUN 2026-09-21 — 9 of 10 steps observed, the mechanism WORKS

FOUNDRY, bridge held, 19-mod `shrublandfauna` tier (all five DLC), quicktest map
(250×250, TemperateForest, `start_debug_game_ready`) plus four bridge-generated
`RUT_AridShrubland` maps. **Deployed first with the game down**: both
`RimMandrake.EnvironmentalHazards.dll` + `RM_Venomvine.xml` and
`RUT_AridShrubland.xml` report `VERIFIED in sync`, and the repo and game copies
were then md5-compared independently — 3 of 3 MATCH.

🔑 **The unprecedented use is sound.** A persistent, shared,
mutated-between-requests `NativeArray<ushort>` handed to the ASYNCHRONOUS pawn
request queue through `PathRequest.IPathGridCustomizer` routes correctly, stays
correct across a save/load, and disposes on map removal without a single native
collection diagnostic. Neither silent failure mode occurred: it is not a no-op,
and it does not over-block.

### 1 — the line this item exists for ✅ PASS, with the control

Two independent geometries, because "the muffalo went round" is the named false
pass and both stagings remove the round.

**A sealed chamber** (13×13 steel walls, 50,50→62,62) whose ONLY opening is a
3-wide gap in the south wall filled by a 3×3 `RM_VenomvineThicket` band
(55..57, 49..51, 9 plants read back):

| pawn | BodySize | barrier | ended inside the chamber |
|---|---|---|---|
| Hare38590 | 0.2 | ON | **YES** — (58,54) |
| Muffalo38585/86/87 | 2.4 | ON | **0 of 3** |
| Muffalo38585/86/87 | 2.4 | **OFF** | **2 of 3** — (55,51) standing IN the band, (58,54) inside |

**A sealed 1-wide corridor** (z=41, x 44..76, walls at z=40/z=42 and caps at
x=43/x=77, 10-cell band at x 56..65) — there is no detour to prefer:

| run | barrier | furthest x reached |
|---|---|---|
| Muffalo38927 | ON | **55** — one cell short of the band, then retreated to x=44 |
| Muffalo38927 (same pawn, same order) | **OFF** | **74** — crossed all 10 band cells |

⛔ The false pass the item names is closed: with no alternative route at all, the
muffalo still did not enter. The control is the same pawn on the same order with
`bodySizeBarrierEnabled` toggled live through `jawa/mod_settings_field`
(`valueBefore True → valueAfter False`, static field), which is the toggle Mod
Settings writes — no relaunch and no settings-file edit was needed.

⚠️ Recorded, not a defect: every blocked muffalo reported `canReach: true` and
`orderAccepted: true`, then the Goto failed in the pather and the AI fell back to
`Wait_Wander` / `GotoWander`. That is exactly the parent item's judgement call 3
(reachability runs on the Normal grid), observed rather than reasoned.

### 2 — three bands, three distinct readings ✅ PASS

Per-cell ticks, sampled by polling `jawa/list_pawns` position against `ticksGame`
in the sealed corridor. The colonist trace is cell-by-cell and unambiguous:

| pawn | BodySize | band | open ground | in the 10-cell band | mechanism |
|---|---|---|---|---|---|
| Hare38793 | 0.2 | free | ~27 t/cell | **~127 t/cell** | no override; the plant's own `pathCost` 90 |
| Human38811 | 1.0 | thread | ~21 t/cell | **315–336 t/cell** (10 consecutive per-cell deltas) | `threadMoveCost` 300 |
| Muffalo38927 | 2.4 | blocked | — | **never entered** | `custom[index] >= 10000` |

🔑 The middle band is the one a wrong `GetPawnCellBaseCostOverride` postfix would
silently drop, and it is the one measured most precisely: ~16× a normal step, and
distinct from the hare's 127 by a factor of 2.6 on the same cells.

### 3 — the start-cell carve-out ✅ PASS (the worst outcome did not occur)

Three muffalo spawned by `jawa/spawn_pawn` directly ONTO thicket cells
((55,49), (56,50), (57,51) — all three confirmed planted), barrier then set ON,
each ordered to (56,44) outside:

| pawn | spawned on | ended | left the stand |
|---|---|---|---|
| Muffalo38740 | (55,49) | (52,44) | **YES**, fully out, south side |
| Muffalo38741 | (56,50) | (68,47) | **YES**, walked 12 cells away |
| Muffalo38742 | (57,51) | (57,52) | **YES** — stepped off the thicket onto the chamber-interior side |

⛔ None stood still failing to path. `RM_MapComponent_BodySizeBarrier.CustomizerFor`'s
carve-out works. Muffalo38742 could not then cross the band to the ordered cell,
because once it is off a barrier cell it gets a customizer again — the documented
"it cannot path back IN" behaviour, seen directly.

### 4 — wander rejection ✅ PASS, 436 samples

Four UNDRAFTED, factionless muffalo placed at the four corners of a solid 64-cell
`RM_VenomvineThicket` stand (40,58 → 47,65) and left alone for **101,230 game
ticks** (≈1.7 in-game days) at Superfast, position-sampled 436 times against the
64 known stand cells.

**Muffalo standing on a thicket cell: 0 of 436 samples.** The `RCellFinder` half
of the move-cost postfix does its job — `trappedMoveCost` 450 is far over
`RCellFinder`'s 20-tick rejection bar, so a blocked animal never chooses a thicket
cell as a destination and never generates a request it cannot satisfy.

### 5 — small creatures still get scratched ✅ PASS, with a null baseline

Five hares penned individually inside 3×3 steel boxes so none could wander off —
**three on a `RM_VenomvineThicket` cell, two on bare Soil in identical pens** —
and run 17,975 ticks:

| pen | hares | outcome after 17,975 ticks |
|---|---|---|
| on thicket (66,60) (70,60) (74,60) | 3 | **3 of 3 DEAD** (`dead: true`, corpses read back in their pens) |
| on bare Soil (66,66) (70,66) | 2 | **2 of 2 alive**, `hediffs: []`, pain 0.00, bleed 0.000 |

The thicket carries a byte-identical `CompProperties_ContactVenom` block to
`RM_Venomvine` (`RM_VenomvineScratch`, damage 3, `contactIntervalTicks` 2500,
`bodyHeight` Bottom). "Small enough to pass" is emphatically NOT "immune" — the
parent item's point 3 holds. Seen incidentally too: two hares crossing the chamber
band earlier were downed ON thicket cells mid-crossing, and one died there.

### 6 — the desert form is unchanged ✅ PASS

Better than the item's one-order check: the corridor's 10-cell band was replanted
from `RM_VenomvineThicket` to `RM_Venomvine` and NOTHING else changed — same
corridor, same walls, same muffalo, barrier ON.

| band def | barrier | muffalo | per-cell in band |
|---|---|---|---|
| `RM_VenomvineThicket` | ON | blocked at x=55 | — |
| `RM_Venomvine` | ON | **crossed all 10 cells, x74 → x46** | **~73 t/cell** (pathCost 60 + move) |

The desert's own use of the plant is untouched: no block, no thread cost, and the
per-cell number is the plant's plain `pathCost`. A `RUT_Desert` map was not needed
— swapping only the def is a tighter control than swapping the map.

### 7 — save/load ✅ PASS

Saved as `LIVEVERIFY_vvfortress_step7` with a colonist standing mid-band at
(60,41) and a muffalo mid-detour at (56,45). 🔴 Saves folder stat'd before and
after: **exactly one new file** (10,646,497 bytes), **no existing save changed
size** — `saveName` was honoured this time. Reloaded (`ticksGame` 194,364):

- 10 of 10 corridor thicket plants restored, barriers re-registered.
- Colonist ordered on: **324 ticks/cell** through the band (x60→x65), then ~27
  ticks/cell on open ground (x65→x74). Identical to the pre-save reading.
- Muffalo ordered into the chamber: `canReach: true`, never entered, job back to
  `Wait_Wander`. Still blocked.

⇒ The grids are NOT saved and do not need to be: `PostSpawnSetup` registration
during load repopulates them correctly. Staged on the player's own map, per the
item's own warning.

### 8 — map removal ✅ PASS, no leak and no crash

The player's own map — holding two `RM_VenomvineThicket` stands (the 94-cell
corridor/chamber set plus a 64-cell stand) **and an allocated blocked-bucket
`NativeArray<ushort>(62500, Allocator.Persistent)`**, forced into existence by a
BodySize-2.4 path request beforehand — was dropped with `jawa/map_drop`.

- Game **ALIVE** afterwards: `programState: Playing`, `mapCount: 0`,
  `hasCurrentGame: true`. No crash, no hang.
- 400 log messages drained after the drop: **0** lines matching `NativeArray`,
  `Unity.Collections`, `leak`, `deallocat`, `dispos`, `jobhandle`,
  `AtomicSafetyHandle`, `PathFinder`, `PathGrid` or `BodySizeBarrier`. **0**
  non-draw errors.
- Whole-`Player.log` scan for the session: **0** occurrences of `NativeArray` /
  `Unity.Collections` / "A Native Collection has not been disposed".

Corroborated four more times: four bridge-generated maps that each held
registered barriers (one of them a 76-plant stand plus an allocated grid) were
culled by the engine's own `MapDeiniter` path during the session, and the game
survived every one with the same clean log.

⚠️ `jawa/map_drop` threw on SERIALIZING its reply — `Self referencing loop
detected for property 'tile' with type 'RimWorld.Planet.PlanetTile'. Path
'result.removedMap.tile.Tile'`. The drop itself executed correctly. That is a
companion-tool bug, nothing to do with this build; filed as
`BRIDGE_MAP_DROP_SERIALIZATION_LOOP_1`.

### 9 — wild spawning ⛔ NOT RUN — the instrument is disqualified, MEASURED

The wiring IS live and was verified directly: `jawa/biome_probe` on the loaded
`RUT_AridShrubland` reports 7 wildPlants, and `RM_VenomvineThicket` is one of
them at **commonality 0.15** (the lowest of the seven; biome `plantDensity` 0.35).

But the count of stands on a generated map **cannot be measured by the only route
available here**, and a zero would have been a false finding:

| map | how generated | total wild plants | any of the biome's 7 declared wildPlants |
|---|---|---|---|
| quicktest TemperateForest | `start_debug_game_ready` (normal) | **17,904** | n/a |
| 4 × `RUT_AridShrubland` | `jawa/world_tile_map_generate` | **0, 0, 0, 231** | **none** — the 231 were `RUT_Plant_Wick`, `Plant_Potato`, `Plant_Tinctoria`, `Plant_HubbaGourd` |

⇒ Not one of `RUT_Fuzz` (0.9), `Plant_Bush`, `Plant_Brambles`, `Plant_Ripthorn`,
`Plant_HealrootWild` or `Plant_Nysyllin_Wild` appeared either, so 0 thickets is
the instrument, not the def. 🔑 Reporting "the thicket does not spawn wild" from
these maps would have been the `zero-rows-is-a-failure-not-a-footnote` trap
exactly. `wildClusterRadius 8` / `wildClusterWeight 25` remain **UNSEEN**, and
answering that needs a real settlement/caravan-arrival generation on a shrubland
tile — campaign-scale, not a quicktest.

⚠️ Separately MEASURED and worth knowing before anyone authors terrain for this
plant: `RM_VenomvineThicket` is refused by a lot of ground. `jawa/set_plants`
rejected **52 of 100** cells on untouched shrubland-map terrain with "terrain or
conditions cannot support RM_VenomvineThicket", and still **6 of 100** after the
same rect was painted to plain `Soil`.

### 10 — log triage ✅ PASS

`body-size-barrier-routing` / `body-size-barrier-move-cost` appear only when a
patch fails to arm. **0 occurrences in `Player.log`**, checked at session start
and again at session end.

Stronger than silence, both patches were read out of the LIVE Harmony registry:

```
Verse.PathFinder.CreateRequest              prefix   mandrake.rm.environmentalhazards
                                            RM_BodySizeBarrierPatches.CreateRequest_Prefix
Verse.AI.Pawn_PathFollower                  postfix  mandrake.rm.environmentalhazards
  .GetPawnCellBaseCostOverride              RM_BodySizeBarrierPatches.GetPawnCellBaseCostOverride_Postfix
```

⚠️ Noted for whoever touches this next: VEF (`OskarPotocki.VEF`) also prefixes
`PathFinder.CreateRequest` at the same priority 400
(`VEF.Hediffs.PhasingPatches.CreateRequest_Prefix`). Ours only ever fills in a
customizer nobody supplied, so the two coexist — but a future change that
OVERWRITES a supplied customizer would break VEF phasing.

⚠️ The 8 `Could not resolve cross-reference` lines naming `RUT_ScaldVent`,
`RUT_TibannaGas`, `RUT_RoilWeather`, `RUT_DeadCreep`, `RUT_FoundrySalvageCache`,
`RUT_FoundryTowerEntrance`, `RUT_ToxinSealant` and `RUT_Filth_MouseTrack` are the
known `DEPLOY_HOLD.txt` held defs and have nothing to do with this build.

### what was NOT chased

Flyers over a thicket (the prefix's `pawn.Flying` carve-out) — `VENOMVINE_PATHCOST_AND_FLYER_1`
owns that. Two barrier defs with different `blockBodySize` on one map (the
multi-threshold bucket code) — no second def exists to stage it with. A
`RSW_ShrublandGiant` (6.0) run — it is in the same blocked band as the muffalo
(2.4) and the same grid, so it adds no information the muffalo did not give.

⇒ Criteria met: 9 of 10 steps observed, the 10th recorded as not-run with the
reason MEASURED rather than asserted. **CLOSED.**
