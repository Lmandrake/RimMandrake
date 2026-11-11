# JUDGE — fw-drain-pump-return

Independent read-only judgment of `STATEMENT.md` against the raw evidence and source. I did not read DONE.md, BROADEN.md, builder notes or verify.py conclusions. I did not attach to the bridge, run the game or use a shell. This file is the only one I wrote. Source is not marked CLEAN.

## Bullet 1 — live liquid_pump chain: Dump → verify effective mode → Pour → level rises; controls measured

Raw readbacks in `evidence/result.json` (chain `liquid_pump`, 4 components, all `execution: ran`, `freshness: fresh`):

- **pump_unpowered_idle** (control): watched 600 ticks, then `PUMP running=False moved=0 pour=False tank=empty:0`. Channel rows hold 20000 dl ×3 (6 levels), unchanged.
- **pump_draws_into_tank** (powered draw): a battery is built and charged, then 800 watched ticks. Reads `PUMP running=True moved=3 ... tank=RM_Liquid_FreshWater:30000`. The channel holds 3334+13333+13333 = 30000 dl (3.0 levels = 6 − 3). Units balance exactly: 3 moves × 10000 units in the tank.
- **pump_off_idles** (disabled control): `liquidPumpEnabled=False` is set and acknowledged. `moved=3 running=False` at tick 1403, and still `moved=3 running=False` after 600 watched ticks (tick 2003).
- **pump_pours_back**: at tick 2003, before any pour request, `ProofTank` replies `TANK mode=Dump effective=Dump liquid=RM_Liquid_FreshWater units=30000` with `success: true` and no error (op_883cb080…). The channel then reads 10000 dl ×3 = 3.0 levels. Only after that does `ProofPump ...;pour` return `running=True pour=True`. 600 watched ticks later (tick 2603) the channel reads 20000 dl ×3 = 6.0 levels. That is a rise of exactly 30000 dl, equal to the tank's contents.

Source: in `extensions.py:3474-3481` the row calls `_tank_set(t, tank, "Dump")`, then `level()`, then `rd("pour")`, then `wait_ticks(600)`, and expects the level to rise. `level()` uses `_water()`, which reads exact decilitres from the batch `dl` field rather than floored `fill` values.

The live run used the earlier `_tank_set`. `readback_comparison.py` rebuilds that version from `git show HEAD`. It shows the old parser wrongly accepted three bad replies: an `effective=DumpPending` prefix, a reply carrying an `error`, and `success:false`. Even so, the real live reply above meets the stricter check on its own: an exact full-token `mode=Dump effective=Dump`, `success:true`, no error. The new `_tank_set` (`extensions.py:2457-2469`) requires a dict, rejects `success is False`, rejects any `error`, and needs a `re.fullmatch` with both groups equal to the requested mode. Module-level `import re` is present (line 37).

`readback-comparison.json` takes the exact live reply from result.json and replays it through the production row's AST (compiled from `liquid_pump` in the current source). The result is PASS, with events in order ProofTank → pour → wait 600. In `readback-cases.json`, all 11 malformed replies (None, {}, a bare string, false-success, error payload, REFUSED, effective=Store, DumpPending, `Dump;`, missing tokens, trailing `actual=Store`) come out UNMEASURED with no pour request or wait. Those offline tests use injected levels, so only the parser path is exercised. That matches the scope given. `extensions-offline.stdout.log` shows selftest_extensions PASS. Its stderr has only a SyntaxWarning in an unrelated docstring in live_session.py.

Run validity: `situational.runValidity` is CLEAN with no visitors, letters or disruptions; 2600 ticks were spent in 6 sweeps; `all_green: true`; acceptance shows 4 PASS. The runner stderr shows the chain PASS=4 FAIL=0 UNMEASURED=0.

Verdict on bullet: **supported.**

## Bullet 2 — fresh, dependency-complete all-DLC game; tier preflight before and after launch; artifact identity; no uninvestigated load/config error

- `preflight-offline.json` (07:21:58Z) is NOT-GREEN. O13 deploy_match came back UNMEASURED because of `WinError 1314` (no symlink privilege). This refusal is preserved, not hidden.
- Harness fix: `biomes_compose.stage_rewritten` (`:315-321`) now falls back to `copy2` only when `winerror == 1314`. Any other symlink error still propagates, and a failed copy still triggers rmtree of the staging dir. `rewrite-old-regression.log` reproduces the old failure. `rewrite-regression.log` and `-windows.log` pass all three cases: the bytes are preserved and are not a symlink, unexpected errors still propagate, and failed fallbacks clean up. This change is in the harness only, not gameplay.
- `preflight-offline-2.json` (07:24:53Z) is GREEN, with O13 "4 mods, 1207 files: deployed == repo byte for byte", O01 game_down, O04 ModsConfig == tier (13 mods), and O14 effective_def_lint clean.
- `launch.log`: bridge up after 31 s. `preflight-live.json` (07:26:53Z) is GREEN. L01 shows pid 50732 started 07:26:09Z, so this is a fresh process. L03 shows 0 config errors, no missing types and no first exception. L04 confirms the running list equals the intended order of 13 mods, read live. `tier.log` and the running list both include Harmony, Core, all five DLC (Royalty, Ideology, Biotech, Anomaly, Odyssey), RimBridgeServer, GimmeSomeSlack, FlowWorks, HugeThings and Patches.
- Artifact identity: in `artifact-identity.json`, all four mod DLLs have source sha256 equal to deployed sha256. In-scene `jawa/type_probe` gives `mvidMatchesFile: true` and `assemblyFileSha256` 1c92c54e…, which equals the FlowWorks source/deployed hash and result.json `env.assembly_sha256`. The wrapper `need()` checks this before running the chain. The companion DLL hash (d76ec2b1…) matches between repo and game, and `companion-recovery.json` shows the embedded hash equals the wanted hash.
- Logs: `log-scan-loaded.json` (sha 8ebe9c30…, 9326 bytes) and `log-scan-after-scene.json` (sha 11389361…, 15825 bytes) both have `hits: []` against Exception / Config error / Could not resolve / Error in / Error while / Failed to. `drive.py` refuses to continue if the loaded scan has hits. `log-final.json` (sha c3ff3f7b…, 28087 bytes) also has `hits: []`.

Verdict on bullet: **supported.**

## Bullet 3 — disposable registered saved site, verified baseline restore, settings restore, canonical saves preserved

From `scene-public.json` and `run_scene.py`:

- `site`: registered site `calm` (`RM_TestSite_calm_v3`), verified, with no problems, hostiles, fires or threat structures. `snapshot` saved it as `WHITTLE_PumpReturn_Begin_20261110T232659.rws`. `baseline_reload` reloaded that snapshot and verified it. `baseline_rect` was taken after the reload: `RECT sha256=7396d930… beds=0`.
- The runner was called without `--site-save`, so it ran on the reloaded disposable snapshot (`site_save: null` in result.json).
- `restore.reload` verified the reload of the same snapshot. `restore.rect` equals `baseline_rect` exactly.
- `settings_before` was read from every `REG.ROWS` entry, including `liquidPumpEnabled`, `tankModesEnabled` and `depthEngineLiveForTests`. In `restore.settings`, every `after` equals `value`. Exactly one setting was changed back: `depthEngineLiveForTests` False (the fixture set it True). `mode_precondition.tankModesEnabled` = True (it was already True before).
- `restore.debug` equals `debug_before` key for key (I compared them by eye). `restore.difficulty` equals `difficulty_before` (threatScale 1.0, allowBigThreats true, …).
- `canonical_after` equals `canonical_before` for both canonical saves (1ff32916…, 1d569ea8…). `saves_changed: []`. `saves_added` contains only the disposable WHITTLE snapshot. A 335-file save backup was kept privately.
- `restore.errors: []`, `restore.status: PASS`, top-level `status: PASS`.
- The `finally` logic was checked in source: each restore step has its own try block, so a failed reload cannot skip the settings, debug, difficulty or saves checks. I confirmed this offline in `failure-cases.json`. When the runner fails (after the fake runner mutated settings, debug and difficulty), restore still brought everything back and status is FAIL. When the reload fails, the settings, debug and difficulty restores still run and restore.status is FAIL.
- `scene-redaction.json` records one literal token replacement with hashes for both the raw and public files. I judged the public extract; no status fields appear to depend on the token.

Verdict on bullet: **supported.**

## Bullet 4 — stopped, stamped down, bridge and driver lock released, including on failure

- `drive.json`: status PASS and `cleanup_errors: []`. The processes ran in order stop-after → stamp-down → bridge-release → bridge-free, each with returncode 0. `bridge_and_lock_free: true`.
- `stop-after.stdout.log`: "game exited", `running_after: false`. `stamp-down.stdout.log`: "game -> DOWN recorded in the ledger". `bridge-release.stdout.log`: "released by BENCH — it is now FREE". `bridge-free.stdout.log`: "driver lock: FREE" and "bridge FREE". `bridge-held.stdout.log` shows both were held by BENCH beforehand.
- Failure path: in `drive.py`, the cleanup runs in `finally` and each step has its own try. Status is forced to FAIL if any cleanup errors or the bridge/lock is not free. `failure-cases.json` `preflight_nonpass_cleanup` injects a live preflight refusal; all four cleanup commands still run, and the result is status FAIL with the bridge/lock free.

Verdict on bullet: **supported.**

## Limitations and observations (not statement failures)

- The parser change was checked only offline, by replaying the one real live reply plus synthetic bad replies. As instructed, that is not a second live run. The live run's own Dump check used the weaker old parser. The real reply happens to meet the strict form, so the live behaviour stands, but the strict parser has never handled a reply inside the game.
- The pour row reads only channel levels. Tank units after the pour, and mode persistence, were not measured (both are out of scope).
- `pump_off_idles` measures the `moved` counter and `running`, not channel water. Channel water is consistent across that window anyway: 30000 dl total at both ticks 1403 and 2003.
- The log-scan patterns are a narrow substring set. `log-final.json` does not list the patterns it used. The full logs are private, so I can confirm the hashes are recorded but cannot check the log contents myself. L03 (0 config errors, no first exception) is an independent check that agrees.
- `stamp-down` warns that the live ModsConfig is still the 13-mod tier list, not the owner's full list. A backup is at `deployed/config/ModsConfig.before-tier-…xml`. The statement does not require restoring ModsConfig, but the owner's mod list still needs restoring (`modset_builder.py --restore`) before they play.
- The disposable snapshot `WHITTLE_PumpReturn_Begin_….rws` is left in the user's Saves folder (this is in `saves_added`; no existing save changed).
- `situational.bland_notes` reports that `restore_colonists` acted 11 times. The note attributes this to earlier chains. Run validity is still CLEAN and no row depends on it.
- `preflight` O09 notes "no .srchash: source provenance unproven" for the companion DLL. That concerns the bridge tool, not gameplay. Its identity was measured by hash.

## Conclusion

Every frozen bullet is backed by raw readbacks and source that agree with each other. The pump-return behaviour (Dump, effective Dump, then Pour, with the level rising by exactly the tank's volume) was measured live alongside powered, unpowered and disabled controls. The later parser tightening is narrow and covered offline against the exact live reply.

would show: yes
