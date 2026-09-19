# BRIDGE_LORDS_AND_GAPS_TOOLS_1 — 10 new companion tools, owner asked "create 10 more bridge capabilities"

Filed 2026-08-29, FOUNDRY, on a direct owner request during a game-DOWN window — the
right time to write+build+deploy since the DLL can't be touched while RimWorld holds it.

## Spec

Close 10 genuine gaps against `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` and its
successor `infrastructure/state/work/BRIDGE_TOOLS_MEDIUM_REMAINING.md`, verified NOT
already covered by the live 253-tool surface before writing a line (several roster rows
that read as gaps by name — "lord_list", "lord_add_pawns", "set master", "power_net_info",
"minify/uninstall" — turned out already shipped under different names:
`jawa/lord_pawn_move`, `jawa/set_player_settings`, `jawa/power_net`,
`jawa/uninstall_thing`; skipped, not re-built):

New file `JawaBenchLordTools2.cs` (4 tools, GM-gated — same tier as
`jawa/lord_defend_spawn`/`lord_assault_spawn`/`social_cancel`, all of which create or
destroy a live AI group):
- `jawa/lord_destroy` — `LordManager.RemoveLord(Lord)`, the public route (`Lord.Destroy()`
  is private).
- `jawa/lord_set_point` — `LordToil_DefendPoint.SetDefendPoint(IntVec3)` + `UpdateAllDuties()`
  so members re-path immediately instead of on next toil entry.
- `jawa/lord_travel_to` — `LordToil_Travel.SetDestination(IntVec3)` + `UpdateAllDuties()`.
- `jawa/pawns_patrol_route` — new `LordJob_Patrol` class: one `LordToil_Travel` per
  waypoint, ring-transitioned on the `"TravelArrived"` memo `LordToil_Travel` already
  fires. The roster calls this "the single highest-value custom class on the whole
  roster." ⚠️ A cyclic `StateGraph` is legal by every check `ErrorCheck()` runs but no
  shipped `LordJob` contains one — unproven until a live run.

New file `JawaBenchWorldEdit2.cs` (6 tools, ungated — field/grid/thing writes and reads,
not incidents fired at the colony):
- `jawa/set_pawn_gender` — the one field `pawn_get` reads and nothing ever wrote.
- `jawa/set_pollution` — map-level `PollutionGrid.SetPolluted` (distinct from
  `world_tile_set`'s planet-tile pollution scalar); pre-checks `ModsConfig.BiotechActive`
  itself because the engine call silently no-ops without it.
- `jawa/battery_set` — `CompPowerBattery.SetStoredEnergyPct` / `AddEnergy` / `DrawPower`.
- `jawa/wipe_cell` — the refund + pre-query half `build_batch`'s own `wipeExisting` never
  had: `GenSpawn.SpawningWipes` walked manually (to report which things, not just a bool),
  `WipeAndRefundExistingThings`. Destructive default off (`dryRun=true`).
- `jawa/get_gravship_substructure` — `Building_GravEngine.ValidSubstructure` /
  `AllConnectedSubstructure` cell sets + `GetStatValue(StatDefOf.SubstructureSupport)`;
  `jawa/gravship_status` only ever reported the COUNT, not the cells or the budget.
- `jawa/forecast_incidents` — `StorytellerUtility.DebugGetFutureIncidents`, the exact call
  behind the storyteller page's own "test" button. Read-only.

## Verify

Built and deployed clean during this game-DOWN window: `build.py --gm` → 0 errors,
0 warnings; `--gm --apply` → deployed (companion only loads it on RimWorld's next
launch). **Not yet proven live — every one of these ten mechanisms has never been
observed running.** On the next game-up window, at minimum:
1. `jawa/lord_pawn_move` list a live Lord, `jawa/lord_set_point` or `lord_travel_to`
   against it, confirm the read-back point/dest actually moved and a member's duty
   changed.
2. `jawa/pawns_patrol_route` on 2+ scratch pawns, step time past 205 ticks × leg count,
   confirm the ring actually advances rather than stalling on its closing transition —
   the one call in this batch with a genuine "never tested in the engine" flag.
3. `jawa/lord_destroy` on a scratch Lord, confirm `lordsRemaining` drops and freed pawns
   resume individual AI.
4. One read-only spot check each: `set_pawn_gender`, `set_pollution` (Biotech-active
   save), `battery_set`, `wipe_cell` dryRun, `get_gravship_substructure` (Odyssey save),
   `forecast_incidents`.

## Live-verified 2026-08-30, FOUNDRY — ALL 10 PASS

Full 585-mod list, fresh `start_debug_game_ready` quicktest map, bridge live, game
paused throughout except deliberate `step_game_ticks`. ⚠️ Every faction on this
world is Hostile to the player (`faction_relations_get`: 0 non-hostile of 35), so
Lord members were **factionless `OuterRim_BattleDroid`s** (`hostile: false`) in a
`PlayerColony` Lord — no hostile group was created near the colony at any point.
Both surviving colonists alive at the end.

### ⭐ `jawa/pawns_patrol_route` — the flagged unknown is RESOLVED: the ring wraps

This was the one call in the batch carrying *"a cyclic StateGraph is legal by
every check `ErrorCheck()` runs, but no shipped LordJob contains one — unproven
until a live run."*

```
pawns_patrol_route {pawns: 3 droids, faction: PlayerColony,
                    waypoints: "30,30|45,30|45,45|30,45"}
  -> success, LordJob_Patrol, memberCount 3, waypointCount 4, refused []
  -> lord_pawn_move list confirms index 2, 'LordJob_Patrol', 3 members
```
`MakeNewLord` accepted the cyclic graph — no `ErrorCheck` failure, no throw.
Then the pawns were tracked by position across stepped ticks:
```
t=1687  (30,30) (32,29) (33,32)     <- waypoint 1
t=2076  (50,27) (45,36) (40,31)     <- clustered on waypoint 2 (45,30)
t=2473  (33,50) (36,45) (31,48)     <- advanced to waypoint 3/4 (45,45 -> 30,45)
```
🔑 **The decisive reading**: `lord_travel_to` on that Lord reported
`destBefore: {x: 30, z: 30}` — **waypoint 1** — *after* the group had visibly
travelled through waypoints 2 and 3/4. The circuit had come all the way round and
re-armed its first leg. ⇒ **The closing transition fires; the ring does not
stall.** The hypothesis is now a measured fact.

⚠️ **Honest limit, and it is confounded, not a defect found:** the group did not
stay together indefinitely — members separated and eventually walked off the map
edge and despawned (3 → 2 → 0 members, at which point `LordManager` removed the
memberless Lord itself). The subjects were **factionless droids in a player Lord**,
i.e. pawns with no reason to remain on the map, so leaving is what they would do
regardless of the LordJob. This cannot be attributed to `LordJob_Patrol`. A clean
endurance test needs real colonists; **circuit longevity is UNMEASURED**, while
ring advancement is proven.

### ✅ `jawa/lord_set_point`
`lord_defend_spawn` first → Lord index 1, `LordJob_DefendPoint`, `PlayerColony`,
3 members (`GQ-7157`, `VX-8018`, `Bamboo`), `refused: []`. Then:
`lord_set_point {lordIndex: 1, point: "90,160"}` →
`pointBefore {100,152}` → `pointAfter {90,160}`, **`dutiesReissued: true`**.

### ✅ `jawa/lord_travel_to` — works, and refuses correctly
On the patrol Lord: `destBefore {30,30}` → `destAfter {40,40}`,
`dutiesReissued: true`.
On the DefendPoint Lord it **refuses with the real reason**:
*"Lord 1's current toil is LordToil_DefendPoint, not LordToil_Travel. This tool
only retargets a travel destination."* — a precise refusal, not a silent no-op.

### ✅ `jawa/lord_destroy`
`{lordIndex: 1}` → `destroyed: {index 1, loadID 2, job LordJob_DefendPoint,
memberCount 3}`, `lordsRemaining: 1`; independent re-list **2 → 1**.
🔑 **Freed pawns really did resume individual AI**: `lord_pawn_move
{action: detach}` on a former member now answers *"GQ-7157 has no Lord to detach
from."* — proof of removal from the Lord object, not just absence from a listing.
Out-of-range index refuses helpfully, dumping the live Lord table (which also
exposes a `toil` field, e.g. `LordToil_FleshbeastAssault`).

### ✅ `jawa/set_pawn_gender`
Verified through an **independent** `jawa/pawn_get` read, both directions:
`Female → Male → Female`, tool's `genderBefore/genderAfter` matching the
independent read each time. Bad value refused:
*"'Zorp' is not a Gender. Accepted: None, Male, Female"*.

### ✅ `jawa/set_pollution` — Biotech active, real read-modify-write
```
set rect 220,220,6,6 polluted   -> cellsChanged 36, cellsEverPollutable 36,
                                   totalPollutionAfter 36
set the SAME rect polluted again -> cellsChanged 0,  totalPollutionAfter 36   <- idempotent
set the SAME rect clean          -> cellsChanged 36, totalPollutionAfter 0
```
The `cellsChanged: 0` on a re-write is the tell that it reads the live grid rather
than blind-writing.

### ✅ `jawa/battery_set` — and the arithmetic proves it is the ENGINE call
On a freshly built vanilla `Battery` (600 Wd capacity):
```
setPct 0.5   -> 0.0   -> 300.0
add    100   -> 300.0 -> 350.0     <- +50, NOT +100
draw   30    -> 350.0 -> 320.0
setPct 1.0   -> 320.0 -> 600.0
draw   99999 -> 600.0 -> 0.0       <- clamped, as documented
```
🔑 `add 100` yielding **+50** is `CompPowerBattery.AddEnergy` applying
`Props.efficiency` (0.5) internally — a detail a field-write could not reproduce,
and exactly what the tool's own Description predicted.

### ✅ `jawa/wipe_cell`
On a steel wall at 210,211: dryRun → `wouldWipeAnything: true`, `affected` naming
`Wall47170` "Steel wall"; cell **unchanged** afterwards. Then `dryRun: false,
refund: true` → same target, `refunded: true`, and `get_cell_info` shows the cell
**empty**.

### ✅ `jawa/get_gravship_substructure` — proven by transition
Built a bare `GravEngine` at 204,204 → `supportBudget: 4500.0` (from
`StatDefOf.SubstructureSupport`), `validCount: 0`, `connectedCount: 0` — correct
for an engine with no substructure. Then laid a 9x9 substructure patch
(`set_substructure_batch`, `changed: 81`) and re-read:
```
validCount 0 -> 81      connectedCount 0 -> 81      supportBudget 4500.0
connectedCells: [{204,204}, {204,203}, {203,204}, {204,205}, {205,204}, ...]
```
The connected list flood-fills outward from the engine cell — real
`GravshipUtility.GetConnectedSubstructure` traversal, not a cell count.

### ✅ `jawa/forecast_incidents` — read-only, real storyteller roll
`{numTestDays: 10}` → `totalIncidents: 8`, `threatBigCount: 1`, with per-incident
points/faction/target and modded defs present:
`VisitorGroup`, `HeatWave`, `VGE_SpaceDebris`, `RaidEnemy`,
`SrFactionWarContentionSiteGenerate`, `ShipChunkDrop`, `MO_Migration`,
`KingToadPasses`. Nothing fired; no game state changed.

## Criteria
- [x] 10 tools written, every signature read from 1.6 source via rimsage, not guessed.
- [x] Builds clean (0 errors, 0 warnings) and deployed — `deployed` confirmed in build.py's
      own output, not inferred.
- [x] No name collision with the existing 253 — grepped before AND after.
- [x] Each of the 10 proven live per the Verify steps above, each by an
      independent read-back or a before/after transition — not by `success: true`.
      The one genuine unknown in the batch, `pawns_patrol_route`'s cyclic
      StateGraph, is **resolved**: the ring advances and wraps (`destBefore` read
      back as waypoint 1 after a full circuit). Circuit LONGEVITY remains
      unmeasured and is noted as such rather than claimed.

--- history ---
