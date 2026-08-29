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

## Criteria
- [x] 10 tools written, every signature read from 1.6 source via rimsage, not guessed.
- [x] Builds clean (0 errors, 0 warnings) and deployed — `deployed` confirmed in build.py's
      own output, not inferred.
- [x] No name collision with the existing 253 — grepped before AND after.
- [ ] Each of the 10 proven live per the Verify steps above. Needs bridge/game-up.

--- history ---
