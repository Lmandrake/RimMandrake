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
