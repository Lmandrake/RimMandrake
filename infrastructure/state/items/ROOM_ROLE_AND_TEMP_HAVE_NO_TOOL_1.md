WRITTEN AND BUILT 2026-08-26 - it just is not deployed.
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchStatTools.cs` adds **`jawa/room_get`**.
`build.py --gm` succeeds with **0 warnings, 0 errors** and reports no tool removal, so it is purely
additive. The game is running and the OS holds the DLL memory-mapped, so it cannot land until the
next down window - `NEXT_RELOAD.md` sec 22. What to run the moment it does is `NEXT_RELOAD.md` sec 23.

CLOSE THIS ITEM ONLY AFTER THE LIVE TOOL LIST SHOWS THE NAME. A build that compiled is not a tool
the bridge serves, and treating it as one is the same mistake as reading a def instead of the
instance.

---

# ROOM_ROLE_AND_TEMP_HAVE_NO_TOOL_1 — two acceptance criteria have no instrument

`TEMPLATE_ENGINE_ACCEPTANCE_1` criteria 1 and 2 need `Room.Role` and a room's temperature. The
bridge reads neither.

`rimworld/get_cell_info` returns exactly: `x z terrainDefName roofDefName fogged walkable
thingCount designationCount blueprintBuildDefs frameBuildDefs solidThingDefs zone areaCount areas
things designations`. **No room object.** Regex `room` over all 246 live tool names: nothing.
Nothing reads temperature either.

**What to build:** `jawa/room_get` — take a cell or rect, return per room: `Role`, cell count,
`Temperature`, `OpenRoofCount`, `PsychologicallyOutdoors`, and the impressiveness stats. Read
the live `Room` off `map.regionGrid`, never infer it from the plan.

🔑 Needs the game **DOWN** to rebuild the companion. Batch with
`PAWN_STAT_READ_HAS_NO_TOOL_1`, which is the same class of gap on pawns —
`jawa/pawn_stats`. One rebuild should carry both.

Evidence: `infrastructure/state/evidence/template_engine_acceptance_2026-08-26_CHECK.md`
