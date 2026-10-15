# TESTSITE_SAVES_BUILD_ONE_CALM_MAP — sitting 2026-10-15

Item: `TESTSITE_SAVES_BUILD_ONE_CALM_MAP` (owner by card 2026-10-15: "Clean saved maps").

## 1. Inventory — how each suite gets its map today
- GSS `proof_all.py --live`: P1 makes a fresh quicktest map (`--no-fresh-map` = current); `calm_map()` (P2c + P3) disarms
  triggers, hostile buildings, non-colonists, unfogs all + re-sweeps.
- FlowWorks `validation_v2.py --live --fresh-map`: up to 4 quicktest rolls (frozen biomes); L1 refuses non-pristine engine / rain.
- FlowWorks rivers: `river_site.py` founds a mild river colony in the current world (>= 2 moving-water edges, fish biome),
  then `extension_proof.py --site river`.
- Pyrelands: already a save (`northstar_site.py --reload-only --tag r6`, fixture `NS_Pyrelands_site_1_417df172fdb5_r6`);
  its `ruins` chain and wildlife census read map content, so only dangers may go.
- r5-r8 hazards were all on fresh maps: mechs/fleshbeasts released by the unfog from shrines (r8 probe: AncientCryptosleepCasket
  + AncientHermeticCrate + Sarcophagus beside every released group), hives/spiders at arm, storm fires, Bumbledrone on a
  leftover candidate map, river into the sea, wide-river ferry banks.

## 2. Design
Full text `design/RimMandrake/test_site_saves_2026-10-15.md`. THREE saves: `calm` shared by GSS + FlowWorks v2 (same needs:
250x250 quicktest home, mild, dry, pristine engine; each clears its own sites; each run is a fresh load); `river` own (plot
repaints cut rivers; v2 needs a pristine engine); `pyrelands` own (50 C is the subject; ruins/wildlife measured -> narrower
`danger` clean profile). Caskets/crates/sarcophagi vanish BEFORE the unfog (Building_Casket.Destroy(Vanish) ->
ClearAndDestroyContents, rimsage 1.6: sleepers destroyed, never dropped). Whole-map unfog + re-sweep; read-back gate before save;
Saves backed up; never overwritten (next _vN).

## 3. Code changes
- NEW `src/RimMandrake/Utils/modcheck/test_site_saves.py` (build/load/check/list; registry `test_site_saves.json`) +
  `selftest_test_site_saves.py` (fake map: order, release-by-unfog, profiles, player-building kept, never-overwrite, load path).
- `proof_all.py`: P1 loads `calm` by default (`--fresh-map` / `--no-fresh-map` / `--site-save`); P1 row carries mapMode + receipt.
- `validation_v2.py`: `--live` loads `calm` (`--fresh-map` / `--current-map` / `--site-save`).
- `extension_proof.py`: `--site river` loads `river` (`--current-map` / `--site-save`).
- Selftests: selftest_test_site_saves 0 fail; selftest_proof_all ALL PASS; v2 offline O-LIVE-NEG PASS + mock GREEN 61/61;
  selftest_extensions PASS; selftest_river_site 0; lint_calls on the new module: 33 literal calls, 0 schema problems.
- Review: test_site_saves.py (found + fixed: `_player` read `factionName`, the colony's own name, so a player turret would
  have been vanished; unchecked post-unfog trigger pass), selftest, extension_proof.py -> clean after commit.
  proof_all.py (930 lines) and validation_v2.py (3.9k lines): diff reviewed only, left DIRTY (no full-file review this sitting).

## 4. Live — bridge, deploy, tier
HELD by the coordinator before Phase 2 (FOUNDRY art deploy with the game down): no deploy / mod-list swap / launch until "go".

## 5. Saves built (BENCH L1, 2026-10-15 08:20-09:55 PDT; evidence `Transient/bench_live_20261015_l1/`)
Deploy from a `git archive` export of **b5c8547e8b** (the tree's uncommitted `JawaBenchPawnKitTools.cs` and Pyrelands Def edits
were not ours and never deployed): 4 mods + composed biomes applied (27 + 12 files; `-` lines = other seats' art + old result
JSONs, kept), companion `build.py --gm --apply`, DLL stamps 0 non-MATCH. Owner list ee01dae9/550 -> ratchet_pilot 22; Steam
launch READY 110 s, first_exception null. Saves folder backed up (`saves_backup_pre/`, .rws gitignored) + the builder's own
backup per build. Every save read back CLEAN (`saves/build_*.json`):
| save | site | read-back |
|---|---|---|
| `RM_TestSite_calm_v1` | tile 116136 AridShrubland 18.6 C, 1st acceptable roll | 19 dangers + 326 ruins vanished, 9486 fogged -> 0, released 0, 0 hostiles/triggers/fires, 3 colonists |
| `RM_TestSite_river_v1` | tile 3247 TemperateForest, current 9117 / fast 4105, river size 2.50, edges S/N/W | 3 dangers + 296 ruins, 1595 fog -> 0, home map dropped, loaded maps = site only |
| `NS_Pyrelands_site_1_417df172fdb5_calm2` | from r6, tile 5 RM_Pyrelands 57.6 C | 9 dangers (MechDropBeacon, SecurityTurret, Sarcophagus), 0 hostiles, **14 wild animals kept** |
Builder fixes (HARNESS/SITE, 0019917f68 + 05b48f9530): (a) vanishing shrine walls released 4 mechs before the unfog guard -> a
second pawn sweep right before the unfog; (b) Anomaly's Fallen monolith (VoidMonolith, hitPoints -1) sits on every new colony
map and failed 2 of 6 rolls' cleans -> `INERT_FIXTURES` (kept: inert until a colonist studies it); a failed clean now re-rolls;
(c) the first Pyrelands build (`..._calm`, kept, never overwritten) vanished all 14 non-colonists incl. the wildlife its
census measures -> the danger profile vanishes hostiles only, by id; rebuilt as tag **calm2**; (d) `_head()` reads `EXPORT_HEAD`
in a git-archive export. River build needed 3 tries (try 1: no fast-lane tile among 6 in that world; try 2: 5 ruins left).

## 6. Proof — load + run per suite (load = save load to Playing; first row = first suite row after start)
| suite | load | start -> first row | total | result |
|---|---|---|---|---|
| GSS proof_all (calm), b5c8547e8b | in P1, ~7 s | 87 s offline gate + 7 s -> P1 | 7m49 (live 382 s) | 109/110: **S9d FAIL, HARNESS** (floor ripple ON since b5c8547e8b draws unroofed strands per frame, never printed) -> S9d sets ripple off, PASS at 8160877246 |
| FlowWorks v2 (calm) run 1 | 8.1 s | 10 s | 4m52 | 56/61: X1-X5 FAIL, **HARNESS** (pit sink clamp ON since b5c8547e8b caps the one-row strip at 0.5) |
| FlowWorks v2 run 2 (X rows clamp OFF) | ~8 s | 9 s | 4m09 | **GREEN 61/61** |
| FW extension river x2 (+swept restart) | 8.9 / 9.1 s | 9 s | 58 s / 55 s | 20 PASS/1 UNM; 19 PASS/2 UNM (swept stopped by an undeclared own-hazard bruise -> restarted: PASS 25 s); flood_refill owed. ferry_rope PASS x2 (rope 51 across size 2.50); 0 hostiles, loaded maps = site only |
| Pyrelands A (16 chains), calm2 | reload 36 s | 8 s | 2m20 | 17 PASS / 1 FAIL scorchfruit_fire_born (21 ScorchFruit back on the map before it, cohort 0); alone after reload: **PASS 25** -> order-dependent, presumed HARNESS |
| Pyrelands B (10 chains) | reload 36 s | 8 s | 2m42 | 15 PASS / 1 FAIL furnace_warmth (**HARNESS**: undrafted colonist walked out of the pen, OffsetFor 0) -> drafted: PASS beside 8.06 / away 0 |
| GSS proof_all at 8160877246 (after relaunch) | ~7 s | 79 s gate + 7 s | 7m24 | 86 PASS / 3 FAIL / 3 UNM: AERIAL_block GovernorStop (colonist Monika downed, health 1, in M15e restring wait; 2/2 repeat), S12a D1 confirmed (peer's new row), **SL2 FAIL: `GssSessionReset` written into the save** (e42ac437f0); `modcheck record` REFUSED: STALE (GSS hash moved under a live peer) |
Long chains not run (owner: no long runs): embergrass_regrow, burn_line, fresh_burn_bonus, scorchfruit_spoils.
Pyrelands auto-recorded RED (partial chains) at d842a6921bf7.
Bar "each suite starts within ~2 min of load": MET everywhere (load 6-9 s; Pyrelands reload 36 s). "No test-env disturbance stops
a row": one did (swept bruise, restarted) -> `TESTENV_SWEPT_BRUISE_REPAIR_SLIPS_ITS_PASS`.

Step-4 proofs (`step4/`): fire_queue_origin 3/3 PASS after declaring the torch's Fire (HARNESS: first run fire_on_map at tick 92);
dig_finds x2 on one map 3/3 + 3/3; climb_proof 12 PASS + 3 owed (CLIMB_step_cost_slow_at_K PASS); heat_dome 2/2 (in B);
burrow_trials 1-3 burrowedAt 250/250/260, colonists alive and standing (trials 2-3 first ran WARM: the reload was refused by the
10 s concurrency window -> runner sleeps 12 s); bottles (FlowWorks at 8160877246): 6 PASS / **bottle_dirty_off FAIL** (a drink
with the dirty stage OFF left no clean empty; presumed MOD, first live run).

## 7. Teardown
Tier list `ModsConfig.tier_at_teardown.xml`, `Player.b5c8547e8b.log` + `Player.8160877246.log` kept. Game killed by PID (25048
for the GSS+FlowWorks redeploy at 8160877246, relaunch READY 107 s; then 29260). `modset_builder --restore` -> **ee01dae9, 550,
verified**. `./game --why ... down`; bridge released.

## 8. Left / NEXT
- `GSS_RESTRING_DIAGNOSE_FIXER_GETS_ZAPPED` — filed; NEXT: read the downed colonist's hediffs in M15e's restring wait (shock from the grounded tail?).
- `GSS_SESSION_RESET_REPAIR_SNEAKS_INTO_SAVES` — filed; NEXT: keep GssSessionReset out of the save (SL2).
- `BOTTLE_DIRTY_OFF_REPAIR_EMPTY_GOES_MISSING` — filed; NEXT: trace the OFF path of the residue doer.
- `TESTENV_SWEPT_BRUISE_REPAIR_SLIPS_ITS_PASS` — filed; NEXT: find why a staged pawn's Bruise at tick 500 read declared=false.
- `PYRE_FIREBORN_DIAGNOSE_TWENTYONE_RETURN` — filed; NEXT: list where the 21 ScorchFruit stood before scorchfruit_fire_born in a full A run.
- GSS criterion 1 is still not re-recorded: GSS is moving under a live peer; record once its run is green at a quiet hash.
- The calm save carries an "Area revealed" letter (arrivalTick 1, from the build's ruin removal); harmless so far.
