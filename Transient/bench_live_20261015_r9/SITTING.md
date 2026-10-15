# BENCH live round 9 — river site proofs at 709bc61812, 2026-10-15

ROUND HEAD **709bc61812** (= origin/main; Part A: 120ea8085d ferry crossing search + river_site loadedMaps/profile order).

## 0. Part A (offline)
- Full-file review of `river_site.py` + `selftest_river_site.py` (bd825f2d56). Found and fixed: `loaded_maps` crashed on a
  non-dict `details`; the map-only quiet-site profile ran BEFORE the site was re-made current (it acts on the current map), now
  after the read-back. Selftest: direct `loaded_maps` checks (details-nested, top-level, can-fail: non-dict / success / None)
  and the profile sees the site current. 0 failures.
- ferry_rope (r8 UNMEASURED "two banks"): HARNESS/SITE, the probe's finder. `SpawnFerry` tried ONE line (first weir site's
  first adjacent water cell, across the flow both ways); any blocked far-bank cell (a tree is PassThroughOnly -> not Standable),
  >60 cells or off-map ended it. River ~33 cells (edges W 32/E 35) < ferryMaxSpan 40, so a rope is possible. New
  `FindFerryCrossing`: every moving-water cell a start, shortest crossing with two post-taking banks within ferryMaxSpan;
  a miss prints `starts/offMap/tooWide/blockedBank`. Measurement unchanged. Also ProofBreach now removes its own potato stack.
  C# selftest 325/325 (new case `FerryProof_searches_every_crossing_within_the_rope_span`); rivers + extensions selftests pass.
- Filed TESTENV_FERRY_ROPE_HARDEN_WIDE_RIVER_BANKS. Commits 120ea8085d (code + DLL), 709bc61812 (4 CLEAN marks + ledger), published.

## 1. Bridge + export
`rimflow bridge take --for "BENCH live round 9: river site proofs"` (was FREE). git archive 709bc61812 -> `/home/mandrake/.seat-tmp/BENCH/r9_export`,
copied (minus Transient, conversations) to `D:\Luke\dev\_rmscratch\bench_live_20261015_r9`.

## 2. Deploy + launch (ratchet_pilot tier)
Plans (`deploy/plan_*.txt`): FlowWorks 2 `~` (the new DLL + srchash) + 8 old result-JSON `-`; SWBestiary 3 `-`; GSS, LuminousPigment,
MandrakePatches, PyrelandsMechanics, UtinniPatches, WeatherSuite in sync. `--mod FlowWorks --apply`: 2 files, VERIFIED in sync.
`dll_source_stamp.py check`: 0 non-MATCH. Companion `build.py --gm --apply` (ext4 export): identical to deployed.
Owner list md5 ee01dae9 (550 active) -> `cfgsafe/ModsConfig.owner_pre_r9.xml`; `modset_builder --tier ratchet_pilot --apply` -> 22 active.
Previous Player.log kept as `Player.prev_session.log`. `launch_ready.py --profile minimal`: READY pid 11776, 22 mods, 116 s,
first_exception null (`launch.txt`).

## 3. TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ (river_site + extension_proof river x2)
Fresh quicktest (`probes/fresh_map.py`): tile 60861, mapId 0, Playing. `river_site.py` (`live/river/river_site_1.log`, rc 0): 9 rejected
(fast=0 etc.), site **tile 60146 mapId 9** (current 3539, fast 947, size 1.89, moving water S 15 / N 14), map_info tile 60146 equal.
**`loaded maps:` printed = uid 0 (home) + uid 9 (site) only**, site problems [], quiet receipt clean (error None). Independent read
(`probes/setmap_probe_1.txt`, the `details.loadedMaps` refusal) agrees.
`extension_proof --live --site river` run 1 (`ext_river_1.json`/`.log`, 37.6 s): **20 PASS / 1 UNMEASURED / 0 FAIL**, aborted None,
run_validity CLEAN, 0 findings, no GOVERNOR_STOP. UNMEASURED = `placer/flood_refill` (owed, by design).
-> verify partial (the read-back works live; 1 of 2 runs). Run 2 not done: round stopped (section 5).

## 4. TESTENV_FERRY_ROPE_HARDEN_WIDE_RIVER_BANKS (works/ferry_rope on the river site)
On run 1 (DLL 120ea8085d): **`works/ferry_rope` PASS** `FERRY paired=True rope=3 ropeExempt=True a=(117,0,92) b=(115,0,92)`;
**`ferry_rope_undrafted` PASS** `ROPEPATH onRope=0 offRope=300 guided=True` (r8: both skipped on UNMEASURED "two banks").
But rope=3 = a crossing of ONE water cell: shortest-wins chose a side trickle, not the main current. Fixed offline in **861b31c03e**
(the longest crossing within ferryMaxSpan wins; C# selftest 325/325 incl. the can-fail on it). NOT deployed or run: the game copy
still holds the 120ea8085d DLL. River here is size 1.89, not the wide 2.5 one. -> verify partial, kept open.

## 5. Restore + teardown
Coordinator STOP before Part B finished (owner back, testing method under review). Tier list saved (`ModsConfig.tier_at_teardown.xml`),
`Player.709bc61812.log` kept. Game killed by PID 11776 (taskkill), gone. `modset_builder --restore` -> **ee01dae9, 550 active, verified**
(`restore.txt`). `./game --why ... down`; bridge released (FREE).

## 6. Ledger
Filed TESTENV_FERRY_ROPE_HARDEN_WIDE_RIVER_BANKS (BENCH, doing). Verify partial + NEXT notes on it and on
TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ; nothing closed. Claimable, not taken: the two NEXTs above; the shrine-pawn holding
mechanism (r8, unproven).
