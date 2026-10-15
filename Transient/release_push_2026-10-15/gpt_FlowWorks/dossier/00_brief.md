# FlowWorks — consult brief (BENCH, 2026-10-15)

You are reviewing **RimMandrake: FlowWorks** (`mandrake.rm.flowworks`, namespace `RimMandrake.FlowWorks`, one assembly
`RimMandrakeFlowWorks.dll`, RimWorld **1.6**, Harmony, all five DLCs always loaded) shortly before release.
FlowWorks is the project's liquid engine: depth is its primitive. It covers dug canals, pits/superdeep cells, ladders and
the pocket grid, ponds/lakebeds as filled bodies, liquids (water, tar, propane, slime …) and their stock, pumps, tanks
(incl. a 2-cell "tall" tank), pipes and hoses, sluice gates, rivers (weir, ferry rope, river current/swept away, flood
refill, silt), liquid fire/heat, drilling, quarry/placer works, ruins (wrecked liquid-works on maps).

## Design laws (owner rulings — design wins over code; a mismatch is a finding)

1. **Defense is the spine** (then irrigation, industry, terraforming). A channel is a barrier dry, a wade wet, a fire
   trap when flammable, an inescapable pit when it holds slime.
2. **Scarcity is stock, not rate. Conservation of mass everywhere.** Every source has a real volume; filling a canal,
   pumping to a tank, burning all debit the same stock. **The ONE sanctioned destruction**: filling in a canal whose
   displaced liquid finds no room overflows, and that is *disclosed* to the player (`ReportOverflow`) even when the
   feature is off. Any other silent creation or loss of liquid is a bug.
3. **Pulsed spread only — no per-tick fluid sim, ever.** Fill-lowest-first then overflow, on pulses.
4. **LAW 1: we dig down, never build up.** Depth is a property of excavated cells only (D 0..4: shallow, mid, deep,
   SUPERDEEP; F = fill 0..D). No berms, no raised ground.
5. **LAW 2: depth affects MOVEMENT and LIQUID, never sight or shooting** (one ruled shooting exception lives in
   `RM_Patch_SuperdeepShooting`).
6. **A pit is a SUPERDEEP cell, not a building** (item PIT_SUPERDEEP_COLLAPSE_1 is the authority over the long spec).
   "If you're in a superdeep pit, you can't climb out. Period." An enclosed pit is a room usable as a prison; "jump into
   pit" button; a ladder can be lowered/raised like a prison door; covers make involuntary falls; a sluice gate is a door
   openable from outside/above only. Relative-depth rule: a pawn climbs a step of K or less (K by body size; flyers free).
   Pocket grid: slopes never trap; a ladder counts as a way out only where it joins a shallower neighbour component.
7. **Liquid unit contract:** 1 unit = a bottle; bucket 5; barrel 25; one channel level = 5 tank units
   (`RM_PumpMath.TankUnitsPerLevel`). Container material scales capacity via `RM_ContainerMaterialMath.ScaledUnits`, and
   fill and pour must use the same factor.
8. **Natural bodies are filled canals (2026-10-11/12 rulings):** a drained pond keeps its bed (a hollow, not Mud at
   ground level), "one volume per square", and the round trip A → tanks → bigger B → tanks → A must conserve.
9. **Every mod ships superb Mod Settings:** on/off per major feature, defaults = shipped behaviour, all-off degrades
   gracefully. Toggling mid-game must not corrupt state or leak liquid.
10. **Players never generate worlds**; they receive a fixed savegame. Save compatibility across our own versions
    matters; a player will save, reload, reload an earlier save, and run multiple maps (gravship/caravans/quests).
11. Every DLC is assumed present; `MayRequire` on DLC decides nothing.

## Known behaviours and bugs already found (do not re-report unless you see they are NOT fixed)

- **Pawnless CanReach + ladders (fixed b98094a832, live-verified 2026-10-15):** vanilla `Pawn_PathFollower.StartPath`
  runs a PAWNLESS `CanReach` (TraverseMode.PassDoors) before every walk. `RelativeVeto` gave pawnless queries no ladder,
  so surface→laddered pocket and back were vetoed (PatherFailed) for everyone. Now pawnless counts any lowered ladder.
  *Hunt for the same CLASS of bug elsewhere*: any patch that keys behaviour on "the pawn" where vanilla calls pawnless
  (reachability, region/room queries, `TraverseParms` with null pawn, WorkGiver prechecks, AI job scanners).
- **Static session-wide tables keyed by thing/pawn IDs break across reloads** (lesson 2026-10-15): a reload hands out the
  same IDs at the same tick, so "already handled" entries from an earlier map/load refuse the new one. Key per map
  (MapComponent) or clear on load. *Hunt every `static` collection.*
- **Tick-keyed caches hold stale answers** (e.g. a port cache for 60 ticks read "no port" 4 ticks after building).
- **Masks/pocket-grid invalidation** was a past cause of ladder failures (fixed c238935c98/63ecf8e874: masks re-derive on
  generation bump). Region/room/path caches after terrain changes remain a hot spot.
- **Pit reroute across reload to an earlier tick** was fixed (PIT_REROUTE_FIX_TIME_TRAVEL_FORGIVEN).
- **Weir breach wash with no room** lost items (fixed: WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST).
- **Ferry rope** crossing search chose a side trickle (fixed 861b31c03e: longest crossing within `ferryMaxSpan` wins).
- **Swept-away** pawns are bruised by the river current hazard (`RM_MapComponent_RiverCurrent`) — by design.
- **flood_refill** has no live predicate yet (UNMEASURED by design).
- A drained natural pond used to become flat Mud at ground level, losing its shape (POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE
  closed — check the fix holds everywhere a pond is drained or refilled).
- More: the attached `known_behaviours.md` (heads of open + closed ledger items).

## How we debug RimWorld here (so your checks are runnable)

- **Source first.** A live run must be proven needed. Each mod has a functional script (`validation.py` /
  `validation_v2.py` modcheck Suite + `northstar/` runners + a C# `SelfTest` console project that runs pure math offline,
  currently 325/325). Live checks drive a running game through the **RimBridge** GABP bridge plus our JawaBench companion
  tools (`jawa/flowworks_body_report`, `jawa/flowworks_excavation_report`, `flowworks_excavation_drive`, `static_call` of
  a public static method with string args, spawn, tick advance, save/load, map_info, list_letters). A cold load of the
  full list is ~15 min; a 22-mod test tier ~90 s; a quicktest map ~90 s. **Prefer offline checks** (SelfTest case,
  python selftest, def dump query) and cheap live state reads; avoid long game-time runs ("compress, decompose, infer":
  shorten a timing constant via a setting rather than wait days).
- Engine traps we have measured: `Plant` ticks only `TickLong()`; `MayRequire` on a top-level patch `<Operation>` is
  IGNORED; a patch matching nothing logs nothing; a `modExtension` of a missing type discards the def; `Player.log`'s
  FIRST exception matters, not the loudest; a count that is zero/round is a query bug until a sanity probe proves the
  instrument can see; bridge tests step the game a few ticks at a time, so tick-keyed caches show stale state.
- A finding is classed **MOD** (the mod is wrong), **SITE** (test map), or **HARNESS** (tooling). We want MOD findings.

## What we want from you

Hunt for hidden or strange behaviours before release. Concretely, in the code shown:
save/load (`ExposeData`, `PostLoadInit`, missing Scribe fields, version upgrades), **reload of an earlier save in the
same session** (statics, caches, generation counters), static state across games/maps, map removal (`MapRemoved`,
`MapComponent` lifetimes, world components holding map refs), multiple simultaneous maps, pathing/reachability caches,
region/room invalidation after terrain or depth changes, Harmony patches (targets, signatures in 1.6, prefix return
values that skip vanilla, conflicts with common mods: Dubs Bad Hygiene, VE Framework, Combat Extended, Prison Labor,
Performance Optimizer/RocketMan, Multiplayer), per-tick performance (work done every tick, allocations, O(map) scans),
null/destroyed/despawned things, settings toggled mid-game, def errors, map edges/out-of-bounds, **liquid conservation**
(creation or loss outside the one sanctioned overflow), and **design-vs-code mismatches** against the laws above.
