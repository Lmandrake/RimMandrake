# WB-game-dungeons-and-wreckage-20261126-171519: onboarding run of game:dungeons-and-wreckage

State: complete (2026-11-26 PST). Every member has its outcome. Lead: FASCINATING_WORLD_JUNK_1 (claimed, ledger 9e9d49f839).

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

| member | outcome | commit | live reading |
|---|---|---|---|
| TILE_STRUCTURE_DESIGNS_1 | done (verify A1 L2) | d6072e1d70 | J20261126T181641Z-910c5c: A1 PASS, 130 terrain, 192 roof, 60 walls as planned, again after 2500 ticks |
| HUTT_SLAVE_PIT_TEST_SITE_1 | done (verify A1-A3 L2) | d57de9a370 (fix), d6072e1d70 (site proof) | J20261126T181716Z-098f55: A2 FAIL, a slave NOTSOLD (red); J20261126T185217Z-d22efe: A1, A2, A3 PASS |
| FASCINATING_WORLD_JUNK_1 | live parts hold; judge part routed; dated wait to 2026-12-03 | 039ac93be3 (roster fix), 28ba1a00f3 (list) | J20261126T203158Z-7dacbd: A1 FAIL, 5 defs in no kind (red); J20261126T210118Z-43bce0: A1, A2 PASS |
| LIQUID_INDUSTRY_SETPIECES_1 | re-homed to mod:FlowWorks, REFUSED BY BUNDLE note | none | none |

- Mod fault found and fixed: an awake colony slave at a buyer pit was a rider, never cargo (vanilla IsColonist is true for
  a secure slave). GoesIntoHolder, HoldsRiderInTransit and DialogHidesPawn now treat a slave at a buyer pit as cargo
  for sale; KeelHoistFuzz red on the planted old rule, green on the fix.
- Lane defect: SteveDesktop proofs jobs staged no map (31 of 162 proof rows on record UNMEASURED with no map). Fixed
  in parallel by PLAYER_START_SITE_1 (e3f4e9f0f0); this run's duplicate fix was dropped before it landed.
- Roster hole found and fixed: Biotech's exostrider remains (a Base_Player step the census never read) and the hermetic
  crate stood in no kind. Kind `fallen_assault_walker` added (delegated design call), the census reads the step, and
  `junk_live_seen.json` pins each live reading for the offline selftest.
- Hidden dependency: a list with StarWarsPatches and no StarWarsRaces generates no colony map (lesson filed). Five
  Workshop mods that StarWarsRaces needs were copied to both Steve games (sync_test_mods.py --only).
- What resumes: a judge's verdict on the junk taste part (a play-zoom screenshot of a fresh map at 039ac93be3 or later,
  and a new roster contact sheet). Nothing else is owed by this bundle.
