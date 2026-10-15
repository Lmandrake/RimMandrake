# BENCH live round 6 — ratchet pilot close-out, 2026-10-15

ROUND HEAD **902b565c93** (5e368279bf + manifest rebuild; no mod-folder change). git archive -> `/home/mandrake/.seat-tmp/BENCH/r6_export`,
copied (minus Transient) to `D:\Luke\dev\_rmscratch\bench_live_20261015_r6`; every bridge run is from that export.

## 0. Bridge + manifest
`rimflow bridge take` (BENCH). `modcheck/required_checks.py` rebuilt: hash be9f005c61e5a4df, 157 mods, 29 north_star_bar + 237 must_show +
3685 script_check + 111 checkout_row; `works/breach_wash_no_room_keeps_catch` listed. Committed 902b565c93.

## 1. Deploy + launch
Plans from the export (`deploy/plan_*.txt`): GSS, LuminousPigment, SWBestiary, UtinniPatches, WeatherSuite, MandrakePatches,
PyrelandsMechanics in sync; FlowWorks 2 (`RimMandrakeFlowWorks.dll` + srchash: the A2 hook cc964dd4a4) -> applied, md5 repo = game
5ed44af479a8; composed biomes 0 drift. Only `-` lines (game-side extras, kept, as r5). Re-plans 0 `~`/`+`. dll_source_stamp: all
MATCH (FlowWorks, GSS, FireEcologyHook, PyrelandsMechanics). Companion `build.py --gm --apply`: identical to deployed.
Owner list md5 ee01dae9 (550 active) copied to `cfgsafe/ModsConfig.owner_pre_r6.xml`; `modset_builder --tier ratchet_pilot --apply`
from the bench clone -> 22 active, before-copy `deployed/config/ModsConfig.before-tier-ratchet_pilot.xml`.
`launch_ready.py` (Steam) READY pid 8320, 22 mods, 89 s, first_exception none. Census 399/400 jawa tools registered: `jawa/revoke`
MISSING (unexpected subset, not used by any suite here; recorded, not chased).

## 2. Criterion 3 — Pyrelands heat guard + full suite
Fixture `NS_Pyrelands_site_1_417df172fdb5_r6` (r5's, tile 5, 56.7 C) reloads clean at 902b565c93.
- **Heat-guard proof** (item command verbatim, `live/pyre/pyre_heat_guard.log`): `scorchfruit_spoils_fast` **PASS (scored)**;
  0 GOVERNOR_STOP / downed; 33 guard passes, max cleared severity 0.0982 (< 0.20); `firehawk_carries_ember` PASS, not restarted;
  `scorchfruit_produces` (exempt) no guard note; `scorchfruit_fire_born` UNMEASURED there only because plant_census was not in the
  chain list. -> TESTENV_SITE_HEAT_HARDEN_COOKS_BY_ROW3 verified + closed.
- **Full suite** (`live/pyre/pyre_suite.sh`, r5's piece split, one fixture reload per piece; `C3_tally.txt`): **36 rows, 34 PASS /
  0 FAIL**; `embergrass_regrows` INFERRED (compressed 0.1 d override: 256 -> 0 -> 34 -> 71, shipped constant restored);
  `furnacebeast_warmth` tool gap (STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY, open). `herd_follows_two_day_old_burn` UNMEASURED in p4:
  the burn line sampled the fulgurite row's leftover DryThunderstorm fires (177 burning, centre 176,141) instead of burn B; re-run
  alone on a fresh reload (p4b) -> PASS. SITE/HARNESS -> filed TESTENV_STORM_FIRES_HARDEN_DECOY_BURN.
- `modcheck floor --all`: Pyrelands VALIDATED 21/21, bar met (`floor_all.txt`).

## 3. Criterion 4 — weir A2 no-room proof
`river_site.py` -> map 9, tile 60146 (TemperateForest, river current 2803), 3 colonists, site/reset problems none.
`extension_proof.py --live --site river --chains works`: **11/11 PASS** in 13.9 s (`live/river/ext_works.json`).
`breach_wash_no_room_keeps_catch`: `NOROOM asked=555 held=1 spawned=1 atOld=1 unitsBefore=10 unitsAfter=10 breaching=True` — bar met.
-> WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST A2 verified L2 -> done.

## 4. TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL (+ criteria 1-2 re-proved at this HEAD)
`proof_all.py --live --no-shots` (`live/gss/`), 6 fresh quicktests:
| attempt | result |
|---|---|
| 1a | P1 SITE: 100x400 map (`gss_fogguard_1a_100x400.log`) |
| 1b | preflight GovernorStop: Megaspider present at arm in p2c_control_noise's 600-tick advance, before P3 |
| 1c, 3a | preflight GovernorStop: dormant Hive threat_structure present at arm, same advance |
| **map 1** | 110/110 PASS; P3 PASS, fogTriggersDisarmed found 2 (RectTrigger + SignalAction_Letter) verified, AfterQuiet verified, hostilePawnsLeft []; vitals: 0 hostile_arrival / letter after P3 |
| **map 2** | 110/110 PASS; same P3 readback; 0 arrivals / letters after P3 |
| **map 3** | 110/110 PASS, P3 PASS (same readback) — but ThreatBig "Area revealed" at tick 15831 (32 ticks after the noon pin) then hostile_arrival RM_LivingBolt + 2 Mech_CentipedeGunner at 15868 (`vitals_map3.json` seq 149-152). No damage, rows not disturbed |
Bar "no hostile arrival after P3" **FAILS on map 3** -> verify partial, item stays OPEN with a NEXT note (fogged mechs survive
destroy_bulk and wake on a later reveal; presumed, unproven). Arrival-origin probe (r5 script, fresh map, no reveal, 8000 governed
ticks): 0 arrivals (`live/probes/arrival_origin_r6_1.json`) — the arrivals need a reveal. Preflight aborts -> filed
TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM (the control-noise advance runs before P3's sweep).
Criterion 1 at 902b565c93: 3 x 110/110. Criterion 2 at 902b565c93: v2 `--fresh-map` **GREEN 61/61** (310.8 s, `live/v2/`); river
extension (fresh river map 10) 20 PASS / 0 FAIL / 1 UNMEASURED (flood_refill, owed by design); swept/returns_home stopped by
FlowWorks' own bruise hazard on the swept colonist (Bruise/Torso, RM_MapComponent_RiverCurrent.cs:442) -> restarted -> PASS;
filed TESTENV_SWEPT_BRUISE_HARDEN_OWN_HAZARD (same disturbance in r4).

## 5. Criterion 5 — code review + nightly selftests
Changed files = r5's 87 + 12 changed since 38d3744bc9 (`c5_files.txt`, 93 unique): `code_review_status.py check` **93/93 CLEAN**
(`c5_status.txt`).
Nightly sweep 03:00 PDT (`Transient/selftests_nightly.log`, ran on the bench tree during this round): **PASS 427/435, FAIL 5,
SKIPPED 3 -> RED**. Re-run now: `selftest_handoff.py` passes (0 failures); still failing:
- `Utils/selftest_lint_harmony_targets.py` — FlowWorks: patch classes in `FlowWorks/Source/Superdeep/RM_CliffMask.cs` (e.g.
  `RM_Patch_ConnectivitySource_Allocate`, L393/L426) carry no `[PatchFeature]` (pilot mod).
- `Utils/northstar_driver/selftest_lint_calls.py` — 3 companion tools in source missing from the snapshot (`jawa/health`,
  `jawa/health_profile`, `jawa/storyteller_comps`).
- `Utils/art/selftest_subject.py` — probe bluedesert_dorrak found for RM_Dorrak (2b).
- `rimflow/selftest_reader_invariant.py` — t_real_ledger_projects_as_before: bridge/game/errors differ.
Not fixed here (other seats' / claimable work).

## 6. Restore + MODSET_MARKER_REPAIR_RESTORES_YESTERDAY
Tier list saved (`ModsConfig.tier_at_teardown.xml`, md5 b1064499); `Player.902b565c93.log` kept. Game killed by PID 8320
(taskkill), gone. `modset_builder --restore` -> **ee01dae9, 550 active, verified** (`restore.txt`). Owed sequence on a SCRATCH config
dir with the module's own functions (`modset_scratch_proof.txt`): apply x2 / hand-restore / re-apply / --restore -> ee01dae9 and
the refusals (newer owner list + stale marker, changed before-copy, --restore-full clears marker) **9/9 OK**; live config untouched.
-> MODSET_MARKER_REPAIR_RESTORES_YESTERDAY verified + closed. `./game --why ... down`; bridge released.

## 7. Section H judgement at ONE HEAD 902b565c93 (22 mods)
1 **MET** (3 x 110/110) · 2 **MET** (v2 61/61; river 0 FAIL, the UNMEASURED is by design) · 3 **MET** (36 rows, 34 PASS / 0 FAIL;
embergrass INFERRED, furnacebeast_warmth labelled tool gap with STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY; floor Pyrelands VALIDATED)
· 4 **machine half MET**: WEIR_WASH A2 done; no PYRE_/CANAL_/POND_/WEIR_/ANIMA_/RIVER_SITE_ item open except
POND_ELEVATION_BUILD_LAKES_RUN_DEEP (FOUNDRY, proposed, owner-deferred); PYRELANDS_GRASS_SATURATION_1 still waits on the owner's
look (BLOCKED, needs owner) · 5 **NOT MET**: code review 93/93 CLEAN but the nightly is RED 427/435 (4 still failing, one is the
FlowWorks harmony-target lint) · 6 owner-only. **Not all of 1-5 met -> pilot left open, no 'all met' note.**
