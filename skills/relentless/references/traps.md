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
- **Counting Markers:** 6 of 36 E1 runs read the books unprompted and held both seed PASSes, moving the catch from 88% to
  95%. Report a contaminated drop with the sensitivity beside it. Control false fail was 4 of 9, so a catch rate alone
  says nothing. A shlex-based scan is blind to newlines, `$(...)`, `<` and `#`. 11-01.

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

## Operating

- **`relentless_seeds.py run` killed by a foreground timeout leaves its `rm-seedcheck-*` unit,** and the next run refuses.
  Stop the unit and rerun; it resumes. `--limit` × case time must fit the call: 6 per 540 s is safe, 9 isn't. 11-06.
- **A hand-made restart unit can look like a dead timer to `timers_guard`.** Use its `pause` verb. 11-06.
- **Books grew 2 GiB of loose objects** over its alternates, which broke `grant_git`'s copy cap. It wants a `git gc`. 11-06.
- **The tick's own cost was the live bottleneck:** serial, uncached `deploy_custom_mods.py` plans per item per tick took it
  to 4-12 minutes, one prove round per 8-10. 11-03.

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
- **Live-tier review pattern:** blacklists over shell text are evadable; an uncaught crash reads as FAIL; re-verify build and
  game identity around the proof; unreadable inputs fail closed; fakes that ignore arguments make oracles vacuous. 11-02.
- **GPT full-file review doesn't converge:** 13, 12, 12, 21, 22 findings over rounds 2-6, mostly new kinds. Clean isn't reachable
  without changing the ruling. A whole-file `gpt_consult --lockdown --effort medium` answers inside 540 s, and its receipt
  covers exact bytes. A HIGH grade can state a false consequence, so trace callers. 11-05, 11-06.
- **Anything that moves a unit's paths must run once behind the real wall.** Fake launches in selftests take no wall. 11-03.

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
