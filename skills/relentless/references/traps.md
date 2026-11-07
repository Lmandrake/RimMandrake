# Relentless traps

Folded on 2026-11-07 from the lessons in `infrastructure/state/lessons/`. The original files are in git history.
Each line is true as of its date. Lines marked *checked* were read against the code on 2026-11-07. The
pipeline is stopped and its code may change at the owner's sitting, so when a line matters, confirm it.

Contents: [Contract](#setting-the-contract), [Proof spelling](#how-the-box-reads-a-proof),
[What the box can reach](#what-the-box-can-reach), [Finishing](#finishing-and-landing), [Live proofs](#live-proofs),
[Reading endings](#reading-endings), [Workers' environment](#workers-environment),
[Reds that aren't yours](#reds-that-arent-yours), [Operating](#operating), [Changing the supervisor](#changing-the-supervisor),
[Fixed since](#fixed-since-dont-rediscover).

## Setting the contract

- **It freezes at first write.** Decide `--game` clauses, the `--live` line and `live_proofs/<ID>.txt` first,
  name the test file first, and run the exact command green first. A typo in `--proof` or `--live` dooms every
  finish until a redesign. Dated 11-01 to 11-06 across about a dozen items.
- **`contract` accepted a `--proof` naming a script that doesn't exist** (`rimflow/run_selftests.py`; the runner
  is `src/RimMandrake/Utils/run_selftests.py`). Check the path yourself. 11-05.
- **An item whose own text gates it on other work can't succeed by restaffing.** Never finish one on a substitute
  contract: the blind PASS closes the ledger item. Exclude it (`pool_ids_exclude`) or block it. 11-01.
- **A locked contract can be factually unsatisfiable** (`--require-all no_game` over a window holding a GAME_DIED
  job). Don't edit the named instrument to get through; snag `contract_*`. 11-01.
- **A proof-only trap:** once a proof-only worker commits a non-proof-path file naming the item, later proof-only
  finishes read `proof_rework` for good, and restoring the file doesn't help. Put live judges in a proof-path name
  from the start (`prove_*.py`, `*_proof*.py`, `selftest_*`). The exit is `proof_found_defect`. 11-05.
- **An item dated days ahead is re-leased every 6 hours.** `MAX_WAIT_HOURS` caps `snag --wait-hours` (*checked*),
  and nothing ends a wait on a date. Don't file a dated after-count as a live item before its date. 11-07.
- **Don't name the whole FlowWorks stock suite as a proof.** `selftest_flowworks_stock.py` runs 1171 cases in about 8 minutes (past `run_selftests`' 530 s budget with others) and its full run reads UNMEASURED on every clone because `ThirstChecks.cs` needs a decompiled `Pawn_NeedsTracker.cs` under a reference dir that doesn't exist. Prove with `selftest_flowworks_stock.py --only '<CasePrefix>_*'` (~110 s) or `--only <CASE>` (~75 s). But its source-text pins count exact matches (e.g. `CapacityForBeds` sizing sites == 2), so before finish run the full suite directly, not just your cases. These two pull opposite ways; do both: cases as the contract proof, full run by hand before finish.
- **Before trusting or strengthening a proof, grep that its named test still exists at HEAD.** A later item's commit deleted `t_refused_start_is_held` while editing `selftest_relentless.py` and the selftest stayed green, because a missing test is silent. A mutants selftest that names its guarding tests fails by name when one goes.

## How the box reads a proof

`relentless_boxrun.extract` reads a proof as shell commands with prose attached. Only simple `python3`/`python`/`bash`
commands joined by `&&` run. `unrunnable` neither passes nor refuses: finish exits 0 and the box measured nothing.

- **A hyphenated lowercase word ends the command:** `--case abort-mid-chain`, `art.py card-said`. Mid-chain the proof
  is unrunnable; as the last part the word silently drops. Use underscores or plain words. *Checked* against `_WORD_OK`.
- **A bare CamelCase argument is cut:** `winbuild.py FlowWorks`. Name the csproj path. *Checked.*
- **A second positional reads as prose** before a later `&&` part. One positional per part. 11-07.
- **A result verb is prose even inside a path:** `python3 fail.py` is cut at ` fail`. 11-06.
- **`run_selftests.py --no-cache` or `--full` needs `--because`,** or it exits 2 before any test. Omit it. Bare stems in
  `--only` are refused; name file paths. *Checked* for `--because`.
- **`proof_gate` tokenizes without splitting on `.`,** so a path ending a sentence (`...Checks.cs.`) never matches the
  changed path. End a named path with a space or comma. Cost two generations, 11-03.
- **A negated grep in a contract proof (`! grep -q X file`) goes green when the file is unreadable:** grep exits 2, the negation exits 0. Behind the Marker's wall `/mnt/d/ClaudeWork/rimmandrake` is an empty mount, so such a clause proves nothing. Read the file in a selftest, tell masked from lost, and commit a receipt for the removal (`Utils/conductor_log_receipt.py`).

## What the box can reach

Walled, the Marker can't read the following, and a proof that needs them is green for you and denied for it, forever.

- `/home/mandrake/rm` and everything under it, the store, `D:\ClaudeWork`, seat clones, `~/dev` (so
  `agent_storage.py` too). Prove timer freshness through `systemctl --user show`, and art through the committed
  art-ledger events and sheet snapshots.
- `infrastructure/state/items/` and `conversations/`. A proof asking whether an item is live reads ledger events.
  Put a proof's input table beside what it checks. *Checked:* `tree_exclude`.
- `.git`. A proof can't use git, including inside a tool it names (`code_review_since.py`).
- **The contract's reach check reads only the proof's text,** so a named selftest that itself reads `items/` passes
  `contract` and reads UNMEASURED later. Grep it first. 11-05.
- **Ledger and code review are the PARENT commit's** (*checked*: `tree_from_parent`). An event or clean-mark in the
  finished commit reads as missing, and `code_review_status check` reads DIRTY.
- **`RM_DATA_ROOT` is unset there.** Test the store only when `store_root()` resolves. 11-03.
- **`rm/scratch` is an empty tmpfs in the box; the default ledger corpus is absent; pids can't be inspected.** One
  `scratch_reap` selftest hit all three. Iterate with `boxrun`, which runs HEAD, not the working tree. 11-06.
- **A walled unit binds the box's tmp over `/tmp`,** so a fixture a selftest made under `/tmp` is invisible and
  systemd exits 226. Make those fixtures under `HOME`. 11-05.
- **`close_evidence.py` can't write inside the box:** `agent_storage.py` reads Permission denied, so the run prints
  `CLOSE-EVIDENCE WRITE FAILED`. The verdict is unaffected, but no gate sees that run. Seen on at least 7 items, 11-06;
  `RM_CLOSE_EVIDENCE_DIR` overrides the location. One such run reported PASS in 0.3 s against about 90 s plainly, so
  check whether a box result was cached.
- **The evidence receipt failed with `TamperError`** ("HEAD names 143 index rows ... the index has 145") on every item
  for a stretch of 11-06, while finish still exited 0. It's a broken shared index, not a failed proof.
- **A `systemd --user` unit with any mount sandboxing (`InaccessiblePaths` etc.) runs in its own user namespace,** so `readlink /proc/<pid>/cwd` of any process outside it fails (its own children still read) and no unit property lifts that. The Marker's box can never see other processes' cwd: read them outside (offbox adapter `proc_cwds`) and make in-box selftests that walk `/proc` use a fake one.
- **A contract proof that runs a git-reading TOOL (`code_review_since.py`: rev-parse, merge-base) has no git verb in its text,** so the reach gate passes it and the walled box (no `.git`) can never run it. The checker then FAILs on a substituted HEAD-clean clause instead of UNMEASURED, so the `git_history` reach-repair grant never fires (one item bounced 5 times, 8.5M). List such tools in `relentless_rules.json` `reach_git_tools`.

## Finishing and landing

- **Order:** content commit, clean-mark commit, ledger commit, then a final commit naming the item that touches
  something else (a lesson, a test, a `live_proofs` line). Finish on that one.
- **An item whose work landed earlier still needs that fresh commit.**
- **A commit origin/main lacks makes about 37 `selftest_relentless_*` suites crash** through finish's unlanded-commit
  guard. Publish first; that red isn't your code. 11-06.
- **`./publish` leaves the seat shard reordered in the working tree;** the same lines as HEAD. 11-06.
- **A reading-based live line on a pulse-deploy timer** (`rm-ops-watch`) runs new code only after `rm-pulse-update`
  fast-forwards, up to 10 minutes. Wait for deploy HEAD to contain the sha, then one tick, then finish. 11-01.
- **Another item's commit citing your id in its body** could count its files as yours and make you a `bad_candidate`. The
  id belongs in your own subject prefix; cite other items by title where you can. 11-05.
- **The selftest runner can print "not recordable: changed during the run"** for unchanged files. 11-06.
- **A contract clause 'code_review_status CLEAN on <file>' races every other item editing that file,** and a full-file-review item whose proof is 'every listed file CLEAN at HEAD' can't close on hot shared files (`relentless.py`, `ops_watch.py`, `ops_watch_rules.json`, `selftest_relentless*.py`: 4 of 9 were edited within 25 minutes of their clean marks). An item that edits a shared reviewed file lands a fresh clean mark before it finishes; a review item scopes its proof to the commits it names, checking the review record for those bytes.

## Live proofs

- **A line that drives the bridge starts `python.exe` and ends `< /dev/null`.** Under WSL `python3` the bridge is
  unreachable, and every clause FAILs without touching the game. 11-03.
- **`refused_proof` refuses `$`, a backtick, `eval`, a brace group with a comma** (so any inline JSON) and
  `--yes-i-know-this-is-live`. *Checked.* Wrap it in a per-mod plain-argument script, and have the mod's selftest run
  every line through `refused_proof`.
- **Always name mods:** `live-mods: <ModFolder>` in `live_proofs/<ID>.txt`. Otherwise staging derives them from the game
  files the *built* sha touched, so a review-marks commit or a proof-only build stages nothing, and a def
  `MayRequire`d on another mod reads UNMEASURED forever. Lost at least 3 sittings, 11-03.
- **A rider's bad `live-mods` name holds the leading item,** and its churn alarm is charged to the leader. 11-05. Lint:
  `selftest_live_mods_names`.
- **"The running game holds your build" can be false.** A 28-mod list without the mod served one proof. Have a proof
  preflight that its mod's type is loaded and fail by name. 11-03.
- **Terminal FAIL rows stop reruns on that sha** (`relentless_live_round.py`), so a harness FAIL wrongly printed can
  pin an item. A proof must separate preflight refusals. 11-03.
- **Preflight can refuse "cut at 160 chars" while `live_proofs/<ID>.criteria` holds the whole line,** likely because books
  hadn't reached the build's publish. Read `whole_criterion` on the books clone before fixing the criterion. 11-04.
- **A plain-drift deploy plan (rc 1) stamped a not-deployed row `game=None`,** so it read INFRA and the per-game wait
  never held it. Harmless to a game-phase round. 11-04.
- **The flyer gate matched negations:** the words "no flight" held an unrelated item. Word the criterion around it. 11-03.
- **A DefDump matching a save's mod set can vanish** when captures are pruned; decode tiles by the defName's base
  shortHash (`repaint_biomes.py --decode-by-name`). 11-02.
- **`runs.jsonl` look-backs must stop at the item's void row;** `read_rows` returns voids as plain rows. 11-06.
- **Game holds:** a "one live user at a time" hold is usually a `live_iter` hold, with the bridge free. `live_idle_s`
  now lapses it (*checked*). Read `state.json` before blaming the prove.
- **A code-offline-green item can loop on game-side endings,** each routed back to a Builder, who can only strengthen
  the offline proof: `TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` burned 12.2M tokens over 8 generations. Ask what the
  stager couldn't load before re-staffing.
- **A carried sha is a deploy point, never a build to judge.** Carry computes from `offline_green.carried_from`. 11-05.
- **A live promise's `reading=` must be a file the unit itself rewrites every run** (e.g. `store/reading.json`), never a snapshot copied into scratch at verify time: a snapshot goes stale by construction and the deadman reopens the item.
- **A live proof whose load must LACK mods can't use `live-mods:`** (enable-only, folder names). End the proof or its `live_site` step on a `reload needed: ...` line (`relentless_live.asked_reload`) so the game phase restages; `live_site.py --needs/--without` checks the RUNNING list first.
- **A live proof can say what it measured:** print RMOBS rows (`rimflow/live_observe.py emit()`, run id from env `RM_LIVE_RUN_ID`). `relentless_live` judges by those rows before any exit code or verdict line: a valid VIOLATED is a FAIL even under exit 0; an observed None counts only with `absence=true`; a foreign run id or malformed row is INVALID; SATISFIED needs stage 'result'. With no RMOBS rows the regex classifier decides, reads the whole log (not an 8 KB tail), and reads an uncaught AssertionError as UNKNOWN, not a product FAIL.
- **Run proof wrappers in `infrastructure/state/live_proofs/` with `python -B` (or `PYTHONDONTWRITEBYTECODE=1`):** a `__pycache__/` left there makes `selftest_relentless_live_round` `t_proofs_file` crash with IsADirectoryError.
- **A live proof line that reads a recorded verdict (`modcheck_status.json` via `env_verify_check.py`) is unmeasurable in the game lane unless a step there writes it:** one item spent 12 generations and 3.7M tokens because nothing ran `modcheck run Armoury`. When a proof reads a record, name the step that writes it.
- **`relentless contract --live hook=<name>` means a Claude `settings.json` hook;** a git hook takes `once:`. (A companion `[Tool]` committed without `tool_schemas.py --supplement-only` turned the nightly `selftest_lint_calls` red three times; `infrastructure/githooks/pre-commit` now refuses it via `northstar_driver/tool_snapshot_guard.py`.)

## Reading endings

- **`checker_lost` may mean never judged.** Read `.err`: 29 of 29 checks once died in seconds at launch on a denied
  TMPDIR, and a full `/tmp` (18 GB tmpfs, filled by idle mutant copies) cost two generations of proof rewrites.
- **A one-tick window:** a tick imports its code, then merges books during the pass, so a blind_fail right after a
  supervisor fix says nothing against it. Read the unit's start time against the books reflog.
- **"change.diff is empty, still BLOCKED"** on a ledger-only finish is the wall's design, not a lost commit.
- **`attempts.jsonl` rows with `gated` are withheld endings;** a counter must skip them, or one fail counts twice. 11-05.
- **`CHURN_OR_BLIND` reads 24 hours by generation START,** so a fixed cause keeps reopening its item for about a day.
  Split by start hour before calling a reopen a new cause. 11-05.
- **A seat shard repeats a `tsn` on several lines:** 1,754 extra lines of 13,794 on 11-03. `rimflow show` lists one, so raw
  line counts overcount events.
- **An aged `closing` stage means waiting on something outside the item.** Read `tomb_since`: a foreign-seat close
  waits for that seat's tree or `staffing.tomb_max_s`. 11-04.
- **A burst of put-downs naming "could not run tasklist.exe"** is the supervisor's Windows reach for one pass, not the
  items. 11-05.
- **`relentless.activity()` looks at top-level transcript entries:** another session in the clone masks a silent worker,
  and a worker busy only inside a subagent looks silent. A walled judge's transcript isn't under `~/.claude/projects`;
  it's in `<box>/projects/`. 11-04, 11-05.
- **The pool sorts unplaced items oldest-first on purpose.** Before calling "it picks old tickets" a defect, run
  `relentless_head_age.py`. 11-05. Items enrolled in one tick tie by name, so raise order only survives through the
  priority list. 11-01.
- **Most of the needs=owner pile wasn't his** on 11-03: 43 of 61 were tooling holds. Read `hold.reason` before asking.
- **`relentless_packet` word lint, hand-scored on 48 receipts:** 6 of 24 hits false and 6 of 24 non-hits missed. Re-score
  `testdata/relentless_packet_handscored.json` before rejects go live. 11-06.
- **Counting Markers:** 6 of 36 E1 runs read the books unprompted and held both seed PASSes. A shlex-based scan is blind to
  newlines, `$(...)`, `<` and `#`. 11-01.
- **Circling thresholds can't see rerun waste.** In a replay of 22 labelled real runs (`time_ledger.py replay`), two identical-selftest-rerun runs read selftest share 0.47 and 0.55 against `test_share_limit` 0.6 and were missed; lowering to 0.3/8 flagged 10 fine runs. Share can't separate them; the signal is the same test command repeated with no edit between. `may_stop` stays False until a rule catches both with wrongful < 0.05. `items/<ID>/circling.jsonl` holds tree SAMPLES (raw/sub hashes), not verdicts; circling hits are in `store/circling.jsonl` `{item, gen, kind, reading, at}`, and reading the per-item file as a verdict flags every running worker. (Separately, an ArtifactData action batch refuses more than 50 writes; `fleet_refresh` caps a run at 40.)
- **A walled check that can't reach its evidence (ssh, `D:\ClaudeWork` tmpfs, a Windows program) is UNMEASURED, never FAIL.** One item looped to generation 9 and 1.6M tokens on blind FAILs; a census found 5 of 29 blind-checker items with blindness read as FAIL (7 returns), and 22 of 142 `blind_fail` ends (20 items). The Marker says UNMEASURED, `relentless_wall.read_as` re-reads blind-only FAILs, nothing counts a gen/return/approach, and `contract --offbox` readings run supervisor-side outside the wall.
- **A live game ending is a reading, not a diagnosis.** Workers handed 'A1 FAILED on the running game' rebuilt correct mods for many rounds because the brief stated the reading as a verdict. The brief now says 'exited FAIL', lists the ending history, names a clause that stayed red across different code, and refuses finish until the worker records `relentless.py explain` (expected, observed, mechanism, evidence per step, theories ruled out, the open follow-up item for the cause); a CLASSIFY label alone no longer counts. An outside fault is explained with its repair item as the cause, then parked with `snag --class instrument --on <repair item>`, which costs no strike.
- **Read the returned-spend breakdown before retrying anything in a churn alarm:** `relentless.returned_tokens_pct x.by_end`. One alarm at 71% was not one broken test: 24 h by ending/lane was proof_weak/work 11.6%, unmeasured/check 11.1% (blind Markers lacking `.git`, other clones, `~/dev`, `dotnet.exe`, `D:\ClaudeWork`; each pays twice), account_lost/work 10.8% (a rate_limit outage; one item relaunched through gens 8..22) and blind_fail/work 9.1% (workers finishing with a clause undone). Never retry the items.

## Workers' environment

- **Workers share `/tmp`:** name scratch outputs after the item. A fixed `/tmp/st.txt` read another worker's FAILs. 11-04.
  Mutant copies go under `D:\ClaudeWork`, and are deleted after.
- **A long-lived process dies with the worker,** whose whole cgroup scope is killed, `setsid` or not. Make it its own unit:
  `systemd-run --user --unit=<name> --collect`. 11-05.
- **Always pass `subagent_type`.** A builder's spawn was refused three times after an untyped parallel trio was blocked;
  it cleared by itself, cause unproven. 11-07.
- **Anything run from a systemd unit that shells to Windows adds the Windows dirs itself.** An unreadable game is a
  harness gap, never "no game". Ten items were held on the owner this way, 11-02 (fixed by `windows_path`).
- **A scratch tick isn't sealed by `RELENTLESS_ROOT` alone;** the real rules name the box root and `ops_watch_dir`, and a
  spurious alarm landed. Use `selftest_relentless_tick_once.py`'s `sealed_rules()`. 11-04.

## Reds that aren't yours

Measure a baseline from `git archive` of HEAD before blaming your diff. These were dated readings, not standing facts:

- `selftest_relentless.py` went red alone in big parallel batches (`t_breaker_di2`, mutating `RM_OPS_WATCH_DIR`) and passed
  on rerun, about 4 times, 11-03 to 11-05. `selftest_relentless_block` `t_cli` did so once, 11-06. Rerun first.
- `selftest_relentless_codex_five` #16 and `codex_five_b` #4, `selftest_relentless_codex_keeps` #4,
  `selftest_relentless_cause` C7, all red at origin/main on 11-06, independent of the changes that found them. #16 counts
  a string in `inspect.getsource(R.Effects)`, so the bar was stale.
- `selftest_recovery_design_doc` was red on main on 11-05: an item closed in the ledger that its doc called open.
- `selftest_relentless_live_round` read red on a stray `.rerun_job` in `live_proofs/` (`HARNESS_REPAIR_CAUSE_B338C64C`),
  and on old `.txt` files that didn't parse, 11-06. Not cleared when this was written.
- `selftest_relentless_reach_git_grant` row 5 exits 226 when `TMPDIR` is under `/tmp`. Run it with `TMPDIR` under `HOME`.
- Fixtures in `selftest_relentless_game` use full shas; the real ledger keeps 12 characters. A row with a full sha is
  silently unseen.
- Forcing another item to `staging` in that rig doesn't make the game busy; its own step releases it. Write a `showings.json`
  build row, or hold `live/round.lock`.
- `entrypoint_inventory` zero can't see a contract. Before retiring a module it lists, grep `store/items/*/state.json`.
- **Seat environment leaks into selftests.** Under a worker the seat env is set (`AGENT_SEAT`, `RIMFLOW_SEAT`, `RM_ROLE_UNIT`), and these fail on clean HEAD: `selftest_art_ledger_fixes.py` crashes at `git add` (it pins the BUILD shard but the writer follows the seat env; passes with `RIMFLOW_SEAT=BUILD AGENT_SEAT=BUILD`), `selftest_block_frontier` `t_base_reader_tolerates_until` and `selftest_cli` `each_kind_of_authority` (stamp `role_unit`), and `selftest_testq_steward.py` T+10 (files its item `for: RELENTLESS` from the ambient role env). Run them with `env -u AGENT_SEAT -u RIMFLOW_SEAT -u RM_ROLE_UNIT`. The fix is for the test to pin every seat variable it reads.
- **Other reds on clean main, independent of the change under test:** `selftest_contracts` C6 (`import dispatcher` pulls stdlib `_sysconfigdata__linux_x86_64-linux-gnu`, which the allowlist doesn't know); `selftest_l1_donor_off_round.py` 'donor rename names read for the save row' (reads untracked `Transient/phase0_sarlacc_save_renames.md`, so it fails in every fresh clone); `selftest_water_terrains_name_liquid.py` and `selftest_static_game_state.py` (`JawaBenchStallProbe.cs` static `CurTick`); `selftest_metronome` ('round robin covers exactly ops_watch.FAMILIES') and `selftest_priority_list` (AttributeError via `pool()`). Dated readings: confirm on a `git archive` baseline before owning one.
- **Runner and harness flakes read UNMEASURED, not red.** `run_selftests.py --only X` exiting non-zero with zero bytes of output is the runner (it passed under `python3 -u` on an unchanged tree): rerun. Inside `rm-harness.slice` under load a dotnet-built Windows exe selftest can fail with `UtilAcceptVsock ... accept4 failed 110` or rsync 'Cannot allocate memory' (`selftest_sun_heat.py` crashed at its 240 s cap yet passed 55/55 outside the slice in under 3 min). A selftest that runs a Windows-exe child must carry the child's stderr into its FAIL detail, or the runner can't see the interop marker and never reruns (fixed for `selftest_sarlacc_pit_sizes`; the same pattern may remain in `salvage_rule`, `rustcathedral_wornbit`, `ninefold_fuzz`, `solarmirrors`, `slime_suite`, `luminouspigment`, `vexxith_uses`). `selftest_tps_record.py` stages its C# harness into one fixed dir shared by every clone, so two at once fail ('parity harness build FAILED', a mutant 'SURVIVED'): rerun it alone.

## Operating

- **`relentless_seeds.py run` killed by a foreground timeout leaves its `rm-seedcheck-*` unit,** and the next run refuses.
  Stop the unit and rerun; it resumes. `--limit` × case time must fit the call: 6 per 540 s is safe, 9 isn't. 11-06.
- **A hand-made restart unit can look like a dead timer to `timers_guard`.** Use its `pause` verb. 11-06.
- **Books grew 2 GiB of loose objects** over its alternates, which broke `grant_git`'s copy cap. It wants a `git gc`. 11-06.
- **The tick's own cost was the live bottleneck:** serial, uncached `deploy_custom_mods.py` plans per item per tick took it
  to 4-12 minutes, one prove round per 8-10. 11-03.
- **Steward and unowned items.** `claim_holds` reads `claim_ts` only, so an item the supervisor started (no claim) runs the unowned clock under a continuing fault and can reach the T+120 OWNER rung; `steward.retire` now leaves a `doing` item alone, but the clock doesn't. The steward also drops a lane-unstick item as 'recovered by itself' the moment the lane shows RUNNING, even when a helper's published fix did it; the drop is terminal, so the fixer can't close the item with its sha. Before dropping, check for a live claim or lease and for a commit since the brake touching testq or the worker.
- **Before restarting a stopped `rm-` timer, search recent transcripts for why it was stopped.** A live drill that stops a production timer leaves no marker on the unit (a blind check failed on `rm-ops-watch.timer` because a drill stopped it on purpose); restarting early spoils the drill. A driller notes the stop on the ledger.
- **`detached_helper.py launch` takes a pool clone (`~/rm/relentless/clones`, cap 10)** and refuses with `POOL REFUSED` when the pool is 10/10 with none idle. Free a clone or pass `--clone <an existing clone of yours>`; watch the pool before a drain.
- **`books_stale` means files outside the ledger are dirty in the books clone.** Causes seen: a `code_review` shard rewritten as a pure line REORDER of HEAD (same lines; restore HEAD's content; the levelling check should treat a same-set reorder as clean); `Utils/modcheck/test_site_saves.json` rewritten by a live site build run from the books (`BOOKS_RUN_ARTEFACTS` now tolerates and restores it; no selftest covers `level_books`); `Transient/northstar/*.json` outputs and an unpublished `modcheck_status.json` recording. Proofs run from the books must write to scratch, and a modcheck recording made there must be published or discarded by its writer. A levelling exemption (`BOOKS_LEFT_IN_PLACE`) takes effect only after the books level, so the dirt it exempts blocks its own arrival: after landing one, clear the matching dirt in the books clone by hand (move it to backups) and confirm the next tick levels.
- **Closing a `NIGHTLY_COP_FIX_RED_*` item because its tests are green now is undone by the next ops_watch pass:** the alarm reads the last READ night, not HEAD. Time-block the item past the next read (night read 11:00Z, lift 12:30Z) with the evidence in the reason; `relentless_block.sweep` moves a queued item to blocked and back by itself.
- **Read `memory.stat` anon and `RssAnon`, never `VmRSS` or `MemoryPeak`, before calling a process big.** A unit's cgroup `memory.peak` counts page cache: one clone peaked 2.0-3.1 GB with ~0.2 GB anon, and `git read-tree`'s ~2.8 GB VmRSS is mmapped store packs. See `infrastructure/state/facts/clone_memory_peak.md` and `Utils/clone_mem_probe.py`. Tick peaks up to 10.9 GB (Oct 31 to Nov 3) are not yet taken apart.
- **Don't take the bridge with `--owner-said`:** the hold becomes an OWNER hold, the 45-minute rule treats it as his, and Relentless can't take it, so its game items stall (~25 minutes once). An agent takes the bridge as its own seat; if `--owner-said` was used, release with `--owner-said` and confirm 'driver lock: FREE'.

## Changing the supervisor

- **A new alarm kind goes unrouted, or turns `selftest_incident` red on main.** Add the `alarm_routes.json` row in the same
  commit, and run `selftest_incident.py`. A `journal()` alarm must carry `kind`. 11-03, 11-04.
- **A side lane sharing `max_queued` never fires:** the build line ran 25 in turn against a cap of 8. Give it its own cap, and
  after landing, grep the journal for its first enrol. 11-06.
- **Mid-tick, books holds the tick's own unlanded ledger lines,** so `fx.sync()` refuses at each step boundary. Work that needs
  fresh books must `fx.flush()` first; the supervisor's flush sets `RELENTLESS_NO_WAKE=1`. 11-06.
- **Any `subprocess` with `timeout=` in a tick catches `TimeoutExpired`** and returns a retry reason, or the tick crashes. 11-03.
- **Parsing a "not in the running load" list:** two shapes exist, so parse dotted packageIds anywhere. 11-05.
- **Candidate checks read `guard_owed` from the tick's cached ledger view,** which can refuse a commit carrying its own guard. 11-05.
- **Live-tier review pattern:** `relentless-pipeline` skill, `references/verdicts.md`. 11-02.
- **GPT full-file review doesn't converge:** 13, 12, 12, 21, 22 findings over rounds 2-6, mostly new kinds. Clean isn't reachable
  without changing the ruling. A whole-file `gpt_consult --lockdown --effort medium` answers inside 540 s, and its receipt
  covers exact bytes. A HIGH grade can state a false consequence, so trace callers. 11-05, 11-06.
- **Anything that moves a unit's paths must run once behind the real wall.** Fake launches in selftests take no wall. 11-03.
- **A new `ops_watch` family with a `*.blind` target breaks every selftest that stubs the other collectors:** the stub omits the blind key and the pass reads 'collector did not run'. Add the key to `selftest_seats_watch`, `selftest_relentless_watch` and `selftest_ops_ranges` stubs in the same commit.
- **`relentless.py` calls `incident.signal` with a hardcoded `{'incident':{'enabled':True}}`** (and writes its own `told.jsonl`), bypassing the switch in `dispatcher_schedule.json` ('Off: nothing rings'); `replay_watch.told()` was fixed to read the schedule, `relentless.py` was not.
- **`relentless.settle` measures stop/force/quarantine age from the `since` it is given,** so callers must pass the first-stop time, not the run's start: a run ended at its time limit is already past `stop_quarantine_s` (600 s) and is quarantined on the first call without a single stop ('unit ... would not die'). Fixed for stagings (`relentless_game` keeps `stop_since`); the worker call `settle(..., st['started_at'])` in `relentless.py` had the same shape. Staging units reported 'would not die' during a PATH-bug window; watch `settle()` for stage units that outlive their stop.
- **A selftest that calls `steward_pass` must isolate `RIMFLOW_LEDGER`, `RIMFLOW_ITEMS`, `RM_PULSE_STATE` and `TESTQ_STEWARD_WAKE`** even if its green path never escalates (a mutant of it noted on a live item). Check `git status` for ledger shards after a mutation run. A fixture that copies the live `dispatcher_schedule.json` inherits `helper_budget.enabled` and scans real transcripts every tick (289 s down to 2 s in `selftest_idle_bringback`): switch it off in the fixture. A contract proof using `run_selftests --no-cache` must carry `--because` or the runner exits 2.
- **A gate that takes the owner's words must take the Conductor's route too.** `selftest_conductor_authority` censuses (AST) every function testing `owner_said`/`--owner-said` and every file comparing to OWNER; a new one fails unless routed or listed in `OWNER_ONLY` with a reason. A hand-listed selftest missed `model._who_refusal`, `relentless.guard` and `queue_lint`'s OWNER-item lockout.
- **Before adding a store file, grep the store's `p("...")` names on origin/main, not just on your clone:** two helpers building in parallel both chose `<store>/incidents.json` for different records and the merge would have had each overwrite the other.
- **A fixture's exit code is not a measurement** (`python3 /missing.py` exits 2, a measured-looking FAIL): `relentless_incident` requires the instrument's own `FIXTURE_VERDICT: PASS|FAIL` line as well as the exit. A ledger item's `history[-1]` is not a close receipt (every note moves it, which reran the fixtures every sweep); use `Item.done_index`.
- **Game-lane clocks differ:** a `runs.jsonl` row's `at` is its own clock; the lane's `staged_at`/`now` is the supervisor clock (fake in selftests, can differ live). Don't compare a row time to a lane time to mean 'read after the fix'; compare a row to the row the fix was made on (`env_tried` keeps [lane time, row time]).

## Fixed since: don't rediscover

Each read in the code on 2026-11-07 unless noted.

- **A `contract_*` snag goes to redesign at once** (the `wall` branch in `relentless.py`). A build worker used to loop.
- **A finish naming a ledger-only commit is refused up front** (`ledger_only_refusal`). A blind PASS used to be lost to it.
- **A reading older than its commit is "not yet" while within `max_age`** (`live_line.py`), no longer `live_broken`.
- **A reused consult clone's `pushurl` is cleared** on handover (`relentless.py`, `scratch_clone.py`).
- **Checker TMPDIR no longer sits behind the wall** (`relentless_wall.tmp_env`).
- **Bookkeeping-only items close with `--no-code`.** The supervisor picks the newest work commit (`work_sha`).
- **A companion DLL is a `live-companion:` line** in `live_proofs`, and staging handles it. Workshop mods are named by
  packageId, with their dependency closure (`relentless_live_round.py`).
- **Blocked items leave the line** as data (`relentless_block.py`); they used to be restaffed.
- **A `live_iter` hold lapses after `live_idle_s`.**
- **The tick runs from a pinned release** since 11-06, no longer from books.
- **`rebind` takes a proof that can't run** (`RELENTLESS_HARDEN_REBIND_TAKES_DEAD_PROOFS`), and a dead proof is heard when named.
- **Carry judges proofs, deployable mod folders and `.srchash`-listed sources only** (`carry_scope`). 11-05, not re-read.
