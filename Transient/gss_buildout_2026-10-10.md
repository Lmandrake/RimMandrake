# GimmeSomeSlack build-out — 2026-10-10

Owner order: "Stop validating that mod. FULLY BUILD that mod right now ... Get it fully implemented."
Hose reel is OUT of scope (moving to FlowWorks).

## Inventory of unbuilt pieces
1. POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK — the only code stub left in Source/ (TapEvents.Drained had no subscriber).
2. UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS — ALREADY BUILT 2026-10-06 (fc932419a); item filed after the fact. Recorded implemented.
3. CORD_GRAPH_TOPOLOGY_REVISION_1 — perf: DrawMotion per-material rescans (FOUNDRY 10-09 note: topology-rev premise wrong).
4. A9 roof-change double draw / A11 long ripple cord culled by midpoint (render-path PLAUSIBLES).
5. MESSYCONDUIT_CABLE_PILE_LOOK_1 — ALREADY BUILT (8bab86beb, state built); owes only live/owner rows (A2/A3 are hose = out of scope).
7. Aerial "Wire sway" radio: Auto and Always behaved identically (Auto = CPU; spans have no shader path).
8. Design 2.5 drip loops below the insulators: never built. Hanging charms (2.5/2.8/2.9): never built, need SpanCharm art (art paused).
9. Design §5 per-def conduit toggles (which conduit defs become cords): never built.
10. TapEvents.Raise: one throwing subscriber silenced the rest (design pass GS-3 robustness note).
6. Mod Settings read-nowhere census: all 42 core+aerial keys are read in game code (MEASURED by name sweep of Source/ minus SelfTest). None unbuilt.

## Per-piece
| piece | status | files | sha | test |
|---|---|---|---|---|
| power theft goodwill leak | BUILT | Aerial/PowerTheftConsequences.cs, AerialMath.cs, AerialSettings.cs (3 settings), CompPowerTap.cs, Defs/Aerial/RM_PowerTheft.xml, SelfTest/TheftChecks.cs | d455a2d4b | 14 rows, selftest 850/850, gate green |
| cord motion per-material buckets (CORD_GRAPH_TOPOLOGY_REVISION_1, DrawMotion half) | BUILT | Core/DrawOrder.cs MaterialBuckets, RM_MapComponent_CordGraph.cs | 2c5974430 | MotionBucketChecks (200 cases == old scan) |
| aerial sway Auto vs Always | BUILT | AerialMath.WireSwayPrefAllows, RM_MapComponent_Aerial.cs WireSway, AerialSettings.cs | 28802f195 | 4 rows |
| drip loops (design 2.5) | BUILT, default OFF | AerialMath.SpanCurveDrip/ProjectT, SpanMesh, AerialSettings.dripLoops | 5d10fc68a | 6 rows |
| per-def conduit toggles | BUILT, default all ticked | Core/ConduitTargets.cs, ConduitVisuals.RetargetFromSettings, GimmeSomeSlackMod.cs excludedConduits + UI group | 439f1c161 | ConduitTargetChecks 6 rows |
| TapEvents per-handler try | BUILT | Aerial/CompPowerTap.cs | f3d39c680 | Verse-only (live) |
| A9 roof-change double draw | already fixed | 8c59a2cac (CORD_STATIC_DYNAMIC_HANDOFF_1, done): section Sig carries sway/ripple eligibility | - | - |
| A11 long ripple cord culled by midpoint | already fixed | 34f156953 (GPT review #4): AnyInView over every point; Flush recalculates bounds | - | - |
| unroutable dive-through | already built | Core/CordPlanner.cs, Core/CordBuilder.cs | fc932419a | 55 dive rows; census 221->0 |

## Owner flags
- Theft numbers are PROVISIONAL: 2 goodwill per day of caught draining, 12-cell sight range (both Mod Settings sliders). He ruled the shape ("steady, like living too close to a settlement"), not the rate. Caught = a victim-faction humanlike, awake, not downed, not our prisoner, with line of sight.

- Drip loops ship OFF: a look change to spans he reviewed. Turn on in Mod Settings > Overhead power lines to judge.
- Aerial sway: "Auto" now follows the game's plant-sway option and "Always" overrides it (was identical). Reversible.
- Hanging charms (design 2.5/2.8) unbuilt: needs RM_MessyConduit_Jawa_SpanCharm art; art is paused.
- Uninstalled cord styles still show "(art not installed yet)" in the style picker: art-blocked, not code.
- "Unfinished runs spark" (design §5 table; open question 5): unbuilt. Needs his answer (spark every live dead end, or tape deliberate ends) AND taped-cap art. Today every live end sparks; breakReadout turns all sparks off.
- Phase 3 decoration (snow fade, trunk wraps, per-def trunk anchors): optional in the design, art-dependent; unbuilt, his call whether at all.
- Style doc's optional "hide Change style gizmo": not built (optional, cosmetic).
- CORD_GRAPH_TOPOLOGY_REVISION_1 topology-revision half not built (FOUNDRY 10-09 showed the premise wrong).

## Results
- Offline gate (`proof_all.py --offline-gate`): red=[] after every piece; core selftest 871/871 at the end (was 836).
- `run_selftests.py`: 295 PASS / 1 FAIL / 92 SKIP. The FAIL is selftest_ledger_lint "real ledger is clean (worktree vs origin/main)": this bench clone's FOUNDRY shard is behind origin (other agents' dirty tree blocks a pull). It passes ("all passed") in an up-to-date clone. Not GSS.
- Landed via a scratch clone (bench clone push refused by the ledger hook for the same stale-shard reason).

## Lessons
- infrastructure/state/lessons/20261011T064401Z-BENCH-gss-2026-10-10-build-out.md: 4 of 7 "unworked" pieces were already built.
