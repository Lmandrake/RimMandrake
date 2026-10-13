# BENCH live sitting 2026-10-13b (pass 8, ratchet pilot final run) — PARTIAL, STOPPED BY THE OWNER

**Stopped on owner order at ~21:44 PDT** (relayed by the coordinator): *"Do not do this long run now. Go back to building and testing things you can directly measure. No more long runs, ok?"* The Pyrelands main run was killed mid-chain (after scorchfruit_fire_born); no long split, embergrass_regrow, burn_line or fresh_burn ran. The pilot item stays open.

Pass HEAD **dbe92f0c92** for GSS run 2, FlowWorks v2 and river (`claude_sha.txt`); the Pyrelands rerun also carried the uncommitted `validation.py` vitals fix (committed with this file). Run 1 of GSS was at 9427afc8ff. `git archive` at `D:\Luke\dev\_rmscratch\bench_live_20261013b`.
Tier: 23 mods (ratchet_pilot + mandrake.rm.patches), Steam launch, twice (relaunched once to deploy the companion fix). Owner list restored, md5 ee01dae9e30d121c78d88e474dacd8e8 (matches the before-copy). Game down, bridge released.
Deploy: every plan in sync except game-only extras (8 old FlowWorks result JSONs, `RM_FE_QuickgrassA.png`), not applied. JawaBench companion: in sync at start, then rebuilt and deployed with the fix below (`build.py --gm --apply`, game down). TEST profile renewed 06:00Z -> 2026-10-13T18:00Z.
Vitals monitor (`jawa/vitals arm`, 240 min) armed as an observer for every suite; watched from the TPS JSONL on disk (`vitals_rows_run*.jsonl`) and a Monitor on `bridge_calls.jsonl`.

## Tally
| suite | result |
|---|---|
| GSS proof_all run 1 (9427afc8ff) | 105 PASS / 1 FAIL: **Z_log_budget FAIL** "Accessing TicksAbs but gameStartAbsTick is not set yet". HARNESS: the armed vitals monitor's `Emit` read `TicksAbs` during a load. Fixed in dbe92f0c92 (read only while Playing); not counted. |
| GSS proof_all run 2 (dbe92f0c92) | **106/106 PASS**, 469 s (`proof_all_20261012T211410.json`) |
| FlowWorks validation_v2 | **61/61 PASS**, GREEN, 14105 ticks, 295 s (`v2_20261013b.json`) |
| FlowWorks river extension | **17 PASS / 3 UNMEASURED / 0 FAIL** (`ext_river.json`): returns_home, panning_draws_stock, flood_refill, same three as passes 4-7. SITE presumed; now filed: `FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY` |
| Pyrelands site build (new builder) | fixture p8a, tile 5, season set before mapgen (ticksGameNoon 730000), food cache 108 MealSurvivalPack in 11 stacks read back; gate B did not refuse the run |
| Pyrelands main, try 1 | crashed after animal_distribution_correct: `validation._vitals` returned None after a FAIL row (upstream_failed), `vitals_damage(pre, None)` -> AttributeError. HARNESS, fixed (`_vitals(force=True)` for the after-read). Log `pyre_main_A_crash_vitals_none.log` |
| Pyrelands main, try 2 (reloaded p8a) — **partial, killed** | **17 PASS / 1 FAIL**, then stopped: mapgen_log_clean, plant_distribution_correct, grass_chokes_ground, **ruins_scorched PASS**, fulgurite_armed_only, biome_def_wiring, **ground_deep_ash PASS (0.919 of 55999)**, ash_fertile_when_watered, ash_drift_common, ash_dusting, scorch_fruit_seed, ashfall_accumulates, ashfall_darkens_drifts, cinderfall_distinct, blackrain_reads, cannot_ordinary_rain, scorchfruit_fire_born PASS; **animal_distribution_correct FAIL** (10 wild animals: 9 RSW_Gizka + 1 RM_Flamefang, bar >= 12; pass 7 map C had 16) — untraced, `PYRE_ANIMALS_DIAGNOSE_TEN_IS_NOT_TWELVE`. Not reached: scorchfruit_produces onward, burrowers, furnace chains, long split. |
| selftests | run_selftests GREEN: 349 PASS / 0 FAIL / 68 SKIPPED of 417 |

## Section H (criterion 3 as changed by the owner's card)
1. GSS 0 FAIL 0 UNMEASURED: **MET** at dbe92f0c92 (106/106).
2. v2 0/0: **MET** (61/61). River 0 FAIL: **MET**; its 3 UNMEASURED are SITE-classed and now have a filed item.
3. Pyrelands 0 FAIL, every non-PASS INFERRED or a labelled gap with an item: **NOT MET** — the run was stopped; 1 FAIL (animal_distribution_correct) and the rest of the suite never ran.
4-6: not re-judged this pass (open as in pass 7).
Also not strictly one HEAD: the Pyrelands rows ran with a harness-only `validation.py` change on top of dbe92f0c92.
**RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP stays open.**

## Disturbances (owner rule: every threat logged + a test-environment item)
| threat / disturbance | where | action | item filed |
|---|---|---|---|
| TicksAbs log error from the armed vitals monitor (GSS log budget red) | GSS run 1 load | fixed dbe92f0c92, GSS rerun 106/106; the error still fired once at the next session's first load (outside GSS's tap) | `TESTENV_VITALS_REPAIR_TICKSABS_SECOND_SOURCE` |
| GSS fixture buildings (RM_AerialMast, Battery, PowerConduit) latched as hostile "(Hive)" structures | GSS runs 1 and 2 | false positive, logged; rows unaffected | `TESTENV_VITALS_HARDEN_FIXTURES_ARE_NOT_HIVES` |
| every load/new game latched as an UNDECLARED clock discontinuity | all suites | false positive, logged | `TESTENV_VITALS_HARDEN_LOADS_ARE_NOT_JUMPS` |
| Anomaly "Fallen monolith" letter | GSS runs 1-2, Pyrelands site | logged; no damage seen | `TESTENV_MONOLITH_HARDEN_UNINVITED_GUEST` |
| colonist Cait hurt 1 -> 0.92 | v2 quicktest map 04:24Z | logged; v2 still 61/61 (no damage to a row) | `TESTENV_INJURY_HARDEN_WHO_HURT_CAIT` |
| dormant insect Hive + GlowPod | FlowWorks river site map | logged; river rows unaffected | `TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS` |
| "Seasonal flooding" ThreatSmall letter | river site map 04:29Z | logged | `TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY` |
| Hernan, brogg, thozzik (+ brullith) died of ToxicBuildup; Stout, Vargas Starving; Jysell hurt — while the suite read "3 colonists, damage []" | Pyrelands site map 04:35-04:42Z | logged; run then stopped by the owner. The suite's vitals and the food top-up see only 3 of the 6 colonists | `TESTENV_TOXIC_HARDEN_SITE_POISONS_ITS_GUESTS`, `PYRE_SITE_VITALS_REPAIR_HALF_THE_COLONY` |
| stranded in-flight markers (my bridge-polling watcher held marker files open on Windows) | bridge client | watcher replaced by a disk-only tail; markers reconciled; `_inflight_clear` now retries (dbe92f0c92) | fixed, no item |

## Harness defects found and fixed this sitting (no mod source edited)
- JawaBench vitals `Emit` read `TicksAbs` during loads (dbe92f0c92; a second source remains, item above).
- `rimbridge_client._inflight_clear` gave up on a Windows sharing violation, stranding markers that refuse later calls (dbe92f0c92).
- Pyrelands `validation._comp` crashed on a FAIL row (after-read returned None) — fixed with this commit.

## Items
- `PYRE_SITE_CLOCK_REPAIR_ASH_EXPIRES_FIRST`: A1 met (site born at mid-Summer, ruins_scorched measured and PASS) — closed.
- `PYRE_RUINS_ASH_DIAGNOSE_TEN_THEN_TWO`: cause was the old clock jump expiring loose ash; ruins_scorched PASS on the new builder's fresh site — closed.
- `PYRE_SITE_FOOD_REPAIR_COLONY_STARVES`: food cache stocked and read back, but A1 NOT met — two colonists Starving and three dead of ToxicBuildup on the site; the top-up sees 3 of 6 colonists. Left open.
- `PYRE_SITE_TEMP_REPAIR_PROBE_HIT_ROCK`: gate B did not refuse map p8a, but its evidence is not in the result JSON; left open (one fixture only).
- `PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE`: not reached (run stopped). Left open.
- Long-duration ruling: `PYRE_REGROW_BUILD_A_WEEK_IN_MINUTES` filed (compressed-constant regrow row).
