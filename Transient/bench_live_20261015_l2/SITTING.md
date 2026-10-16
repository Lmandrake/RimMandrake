# BENCH live L2: ratchet pilot close-out, 2026-10-15 (12:42-14:25 PDT)

MOD-SOURCE HEAD **536e6c3d01** (= origin/main at start). Only harness files changed during the round, and both are
staleness-exempt northstar/ or validation.py: `FlowWorks/northstar/extensions.py` 0a5f386a45, 89f37d3075, 2024fb4890;
`Pyrelands/validation.py` abbf2f9512, 2bfd2dd38f. git archive 536e6c3d01 went to `/home/mandrake/.seat-tmp/BENCH/l2_export`
and was copied, minus Transient, to `D:\Luke\dev\_rmscratch\bench_live_20261015_l2`. The bridge runs used that export;
the harness fixes were copied in.

## Deploy + launch
Plans are in `deploy/plan_*.txt`. GSS (DLL+srchash), FlowWorks (9), PyrelandsMechanics (DLL+srchash), EmpirePursuit (5)
and the composed biomes (6) were applied. LuminousPigment, MandrakePatches, SWBestiary, UtinniPatches and WeatherSuite
were already in sync. `dll_source_stamp check`: all MATCH. The companion `build.py --gm --apply` built from the export
and deployed. The owner list (ee01dae9, 550 active) is in `cfgsafe/`. `modset_builder --tier ratchet_pilot --apply`
gave 22 mods; `launch_ready` reported READY in 105 s with first_exception null.

## Results
| | result | evidence |
|---|---|---|
| C1 GSS proof_all --live --no-shots, calm save | r6's 110-row set **110/110 PASS**. The 9 rows added since r6: 3 PASS; **S12a FAIL = GSS D1 mixed-looks CONFIRMED** (cosmetic MOD defect, noted on GSS_STYLE_RUN_PROVE_MIXED_LOOKS_SUSPECTED); S12c/S12d/B12/A8 UNMEASURED (scene owed); B13 UNMEASURED SITE (noted on GSS_HOOKUP_CABLE_PROBE_HIDDEN_CONDUIT). modcheck record RED at 52b7c6c9a0fd because of the new rows -> verify **partial** | `live/gss_proof_all_1.json` |
| C2 FlowWorks validation_v2 --live, calm save | **GREEN 61/61**, 291 s | `live/fw_v2_2.json` |
| C2 river extension_proof, river save | **20 PASS / 0 FAIL / 1 UNMEASURED** (flood_refill, owed by design), run_validity CLEAN | `live/ext_river_1.json` |
| C3 Pyrelands north star, calm2 save, r6 pieces | **36 rows, 35 PASS / 0 FAIL**; embergrass_regrows INFERRED (compressed 0.1 d: 256->0->31->71); furnacebeast_warmth now PASS (it was r6's tool gap); floor --all Pyrelands VALIDATED 21/21 | `live/pyre/C3_tally.txt` |
| POND_ELEVATION deep_lake_proof | **6/6 PASS**, plus the owed save/reload row **PASS** (drained-bowl SHAPE hash identical, 17 keys, 0 diffs) -> **closed** | `live/deep_lake_1.json`, `live/deep_lake_reload_1.json` (`live/dl_save_reload.py`) |
| FUEL_MOAT chemfuel + astrofuel | chemfuel **2/2**; astrofuel **3/3** with mandrake.rut.empirepursuit active (23 mods: the tier plus EP, after a relaunch); hitch from a 30x30 / 900-cell detonation: Excavation 0.083 ms/tick, worst tick 1.69 ms, TPS ratio min 0.92 -> **closed** | `live/ext_fuel_5_ep.json`, `live/blast_hitch_30.json` |

## Void runs (HARNESS / TESTENV, not counted)
- v2 attempt 0: the companion test profile (`JawaBench/companion_profile.json`) **expired at 20:00Z mid-run**, and every
  static_call was then refused in the CAMPAIGN profile. I extended it to 01:00Z for the round and restored the original
  at teardown. Attempt 1 cleaned up after the killed run: an indeterminate order_pawn (reconciled), then `--reset-settings`,
  which turned L2 and E1a red. The clean attempt 2 is the counted one.
- fuel astrofuel #1: the muffalo 2 cells from the run was shredded dead and a surprise ended the chain. Moved it to
  3 cells and made it a fixture (0a5f386a45, 89f37d3075).
- fuel #2/#3: EmpirePursuit was deployed but was not in the 22-mod tier list, so the row read "Utinni not loaded".
  Relaunched with EP. #3/#4: EP's queued RaidEnemy, then the killed raiders, ended the chain as surprises. Both are now
  declared as the chain's own acts (2024fb4890).
- Pyrelands p3: furnacebeast_warmth UNMEASURED because the bridge drops an empty-string `result`, so an out-of-range
  sign read as refused (abbf2f9512). A full-file review of validation.py found 3 more harness defects, fixed in
  2bfd2dd38f. p3/p4 were rerun: all PASS.

## Code review
extensions.py was reviewed full-file (sonnet): no certain defects; the one suspected issue in the touched row was fixed.
It is marked CLEAN at 2024fb4890. validation.py was reviewed full-file: 3 defects found and fixed; marked CLEAN at
2bfd2dd38f.

## Owner review save
`RM_pyre_review_20261015` was built by `human_review.py --build --load NS_Pyrelands_site_1_417df172fdb5_calm2` in 56 s,
then saved. The Saves folder was backed up first to `D:\Luke\dev\_rmscratch\bench_live_20261015_l2\saves_backup_pre_review`.
The save stat-diff showed 1 new file and 0 changed. 39 of 41 stations verified. Not verified:
- **9 AFTER THE BURN**: the burned pad's soil did not read as deep ash.
- **16 GROUND COVER MIX**: the ember grass is missing, so the station shows quickgrass only. The second planting
  replaced the first.

The colonists were left drafted (their order to the shelter was refused). Key sheet:
`src/RimMandrake/Pyrelands/review/KEYSHEET.md` (html: `Transient/pyre_human_review/keysheet.html`).

## Teardown
I saved the tier list and both Player.logs, and killed the game by PID. Running `modset_builder --restore` returned
**ee01dae9, 550 active, verified**. The companion profile file is restored. `./game down`, bridge released. Extra save
left behind: `RM_L2_deeplake_reload_check.rws`.

## L2b: review save repaired (14:15-14:25 PDT)
- **16**: `set_plants` clearFirst wipes the whole rect, so the second planting (quick) replaced the first (ember). The
  builder now clears only on a station's first planting. Fix in 2aedbdc9b2 (`human_review.py`); the screenshot shows both grasses.
- **9**: STAGING, not a mod defect. Vanilla `Fire.TryBurnFloor` turns terrain to its burnedDef only on a fire alive for
  >= 7500 ticks, and the build burned for 4000. BURN_TICKS is now 8000. Station 9 reads RM_FE_Ash_Deep 64/64.
- Rebuilt on ratchet_pilot + EmpirePursuit (23 mods): **41/41 stations verified**. Saved over the same name,
  `RM_pyre_review_20261015`. Both the first build and the deep-lake throwaway are backed up in
  `D:\Luke\dev\_rmscratch\bench_live_20261015_l2\saves_backup_pre_review`. `RM_L2_deeplake_reload_check.rws` is deleted
  from Saves.
- KEYSHEET.md regenerated. ModsConfig restored (ee01dae9, verified); companion profile restored; game down; bridge released.

## Owner review walk (2026-10-15)
OWNER MODSCONFIG BACKUP (md5 ee01dae9) is at `/home/mandrake/rm/bench/Transient/bench_live_20261015_l2/ModsConfig.OWNER_BACKUP_before_review_walk.xml` and MUST be restored after his walk (live ModsConfig is the 23-mod ratchet_pilot+EP tier, game left running with the save loaded, paused).
