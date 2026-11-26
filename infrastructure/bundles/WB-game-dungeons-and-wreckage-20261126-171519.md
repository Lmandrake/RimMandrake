# WB-game-dungeons-and-wreckage-20261126-171519: onboarding run of game:dungeons-and-wreckage

State: step A done, step C in progress (2026-11-26 PST). Lead: FASCINATING_WORLD_JUNK_1 (claimed, ledger 9e9d49f839).

## Step A, the reality sort (read against the code of 2026-11-26)

| member | class | evidence |
|---|---|---|
| FASCINATING_WORLD_JUNK_1 | keep | Offline built at 29b71f8f34 and 274e6da319 (roster as data, generated cut and re-text patches, Fall Line no-old-junk step); `selftest_junk_roster.py` all pass today. No game has generated a map on this build. Prose status was false ("Phase 3/4 not started"): corrected. |
| HUTT_SLAVE_PIT_TEST_SITE_1 | keep | Offline built at 186d24833d (HUTT_SLAVE_PIT_SITE_BUILD_1). Its live chain `hutt_slave_pit` (src/RimMandrake/KeelHoist/validation.py) reads the sale and the seal UNMEASURED on any player colony map: GateOpen is true where Map.ParentFaction is the player, so keepers never buy. A proof needs a generated Hutt site map. |
| LIQUID_INDUSTRY_SETPIECES_1 | not about this unit | The FlowWorks ticket sweep of 2026-11-22 (design/concepts/FlowWorks/ticket_sweep_2026-11-22.md) kept it for FlowWorks 0.2.0. Re-homed to mod:FlowWorks (ledger home event); REFUSED BY BUNDLE note. |
| TILE_STRUCTURE_DESIGNS_1 | keep | Engine and 21 of 22 promise rows built; its sole bar A1 (live terrain and roof ordering) never ran. The suite's replay chains read only the plan's own counts, never the cells. |

Counts: keep 3, not about this unit 1, done 0, stale 0, duplicate 0, not worth the touch 0.

## Where the live work runs

ArchBig (his Explosive Knockback walk) and ArchSmall (his flyer session) are held for owner sittings. SteveDesktop's
games refuse chain jobs of mods outside the Maturation Pipeline (host_work_switch), and take `--proofs` jobs. So each
kept member gets a proof file `infrastructure/state/live_proofs/<ID>.txt`, and `testq.py ask <ID>` queues it there.
Outcome checks: `src/RimMandrake/Utils/testq/rows_passed.py <ID> <since> proofs/A1 ...` (a done lane job since the
check was written, every row PASS).

## Step C

- FASCINATING_WORLD_JUNK_1: `src/RimStarWars/StarWarsPatches/prove_junk_roster_live.py` (A1 map vs roster, A2 Fall
  Line report); offline `--selftest` passes. Next: lane job, read it, then the judge's look.
- TILE_STRUCTURE_DESIGNS_1: `src/RimMandrake/StructureInjections/prove_plan_ordering_live.py`; offline `--selftest`
  passes. Next: lane job, read it.
- HUTT_SLAVE_PIT_TEST_SITE_1: needs a site-map staging (C# proof or `jawa/world_tile_map_generate`). Next: build it.
