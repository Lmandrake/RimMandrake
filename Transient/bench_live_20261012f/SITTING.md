# BENCH live sitting 2026-10-12f (pass 5, owner at work): one pass HEAD across GSS, FlowWorks, Pyrelands, ideo NRE

Harness: `git archive` of ALL of src/ + infrastructure + Transient/modcheck + Transient/northstar from **pass HEAD 90e2783301**
(claude_sha.txt) at `D:\Luke\dev\_rmscratch\bench_live_20261012f`. Owner list md5 ee01dae9e30d121c78d88e474dacd8e8 (ModsConfig.owner_before.xml).
Deploy: UtinniPatches applied (`+ Patches/FixedIdeo_StructureFallback.xml`, `~ RUT_BloomCrop.xml`); FlowWorks, GimmeSomeSlack,
MandrakePatches, PyrelandsMechanics, biomes compose already in sync (plans only `-` leftovers). Tier: 23 mods
(ratchet_pilot_plus_patches), Steam launch, 0 FaceAdjustmentDef lines.

## Tally at pass HEAD
| suite | result | class of non-PASS |
|---|---|---|
| 1 Ideo worldgen NRE (IdeoFoundation_Deity) | **0 hits over 4 quicktest worldgens** (was 3/3 hits per sitting, 10 lines in 20261012d log; same grep sees those 10, so the instrument works) | fix 480611e4df holds |
| 2 GSS proof_all | **106/106 PASS**, 460 s (proof_all_20261012T101318.json) | |
| 3 FlowWorks validation_v2 | **61/61 PASS**, 14467 ticks, 319 s (v2_20261012f.json); oracle fix 38c040c256 confirmed | |
| 3 river extension | run 1 12 PASS / 8 UNMEASURED (weir at x=237, ferry banks off-map, SITE); run 2 on a new world **17 PASS / 3 UNMEASURED / 0 FAIL** (ext_river_2.json) | see below |
| 3 river_site fish row | weir_fish_draws_stock PASS both runs (TemperateForest tiles 14177 / second world) | |
| 4 Pyrelands main (22 PASS / 2 FAIL / 9 UNMEASURED components, of which 4 are skipped-chain placeholders) | plant_distribution_correct PASS (2nd-to-none foreign plants), animal_distribution PASS, mapgen_log PASS | FAIL ground_ash_ladder = retired, not counted; FAIL burrowers_dive = flake, see below |
| 4 Pyrelands long split | **burn_line_present PASS** (waitTicks 120360, 6 free-standing fires, firesBeforeArm 0); embergrass_regrows UNMEASURED CALIBRATING: day3 67/256 = 26.2%, day7 153/256 = 59.8% (targets 25%/60%, unruled) | |

## Non-PASS classes
- river returns_home: SITE (nobody is washed away on the site, SWEPT pending=0).
- river panning_draws_stock / flood_refill: SITE presumed, untraced (`pan=nothing` though sluice washes silver; same on 3 sittings).
- river run 1 ferry_rope chain (4 rows): SITE, weir at the map edge (x=237 of 250); a new world fixed it.
- Pyrelands burrowers_dive: first run FAIL (job samples Flee/Wait, never RM_Burrowed over 1500 ticks); a rerun of `--chains burrowers`
  on a reloaded fixture PASS (samples ShadeDash, ShadeDash, RM_Burrow). It passed 20261012b. Flaky, class UNTRACED
  (MOD or SITE: grazer chose flee over burrow). Filed PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE.
- Pyrelands scorchfruit_spoils_fast (stack vanished by day 1), furnacebeast_warmth (no tool), fulgurite (sand fraction 0), herd_follows
  (no drive): unchanged UNMEASURED.
- Harness note: driver `run --mod Pyrelands` without `--plan src/RimMandrake/Pyrelands/northstar_plan.py` produces an empty run (0 rows).

## State left
Game DOWN (graceful taskkill), ModsConfig = owner list md5 ee01dae9e30d121c78d88e474dacd8e8, bridge released.
