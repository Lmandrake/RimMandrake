# Relentless verdict machinery: identity-bound, fail-closed (design pass, 2026-11-02)

Item `RELENTLESS_REDESIGN_VERDICT_FAIL_CLOSED`. Conductor's order with the owner's authority
(`CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`). Why: three GPT review rounds on each of relentless_live.py,
live_def_check.py, relentless.py and their selftests kept finding new wrong-verdict and bypass cases of the same few
kinds (lesson `20261102T042108Z-BENCH-review-pattern-relentless-live-tier-3`; rounds r1, r2b, r3a, r6a, r8a). Patching
case by case does not converge. This pass replaces the mechanisms those cases came through.

Rule 6 was built by `RELENTLESS_REDESIGN_VERDICT_FAIL_CLOSED` (relentless.py, `selftest_relentless_verdict_rule6.py`).
Rules 1-5 are item `LIVEVERDICT_REBUILD_ALLOWLIST_MEETS_OPENLANE`: the live-proof lane has grown past the two-tool
allowlist below since this was written, so that item settles the allowlist's shape first.

## The verdict contract

A verdict is one of four words. Only two of them move the ledger.

| word | meaning | ledger |
|---|---|---|
| PASS | the proof ran to its end, said PASS, and the world it measured was the build's world from before it started until after it ended | `rimflow verify --result pass --sha <built sha>` |
| FAIL | the same, and the proof said FAIL | `rimflow verify --result fail` |
| UNMEASURED | anything else: a crash, a timeout, unreadable input, an identity that moved, a child that would not die, a release that failed | a note, never a run |
| REFUSED | the run was not allowed to start (not owed, a flyer, a proof outside the allowlist) | nothing |

**Rule 0 (the only way to a verdict).** PASS or FAIL needs *all* of: an explicit verdict from an allowlisted tool
(rule 3), the identity snapshot equal before and after (rule 1), every proof process gone (rule 4), the bridge released.
Every other path is UNMEASURED by construction: the runner's verdict variable starts as UNMEASURED and only the last
line of the happy path assigns PASS or FAIL. There is no `else: FAIL`.

## Rule 1. Identity binding

`Identity` is one record, taken twice: after the bridge is held and before the proof starts, and after the proof ends
and before the bridge is released. Taking it *after* `bridge take` closes r1#4 (another holder changing the game
between preflight and take).

| field | source | why |
|---|---|---|
| `build` | the item's `built_sha`, resolved once by `git rev-parse --verify <sha>^{commit}` to a full 40-hex id; a non-hex or short or ref spelling is refused | r3a#2: a ref can move |
| `item_built` | the ledger's `built_sha` for the item, re-read | an `implemented` mid-proof re-points the item |
| `mods` | the built commit's game mods: every `src/<tier>/<Mod>/` the commit touches with a shippable path, deletions included | which folders bind the verdict |
| `expected` | `git ls-tree -r -z <build> -- src/<tier>/<Mod>/`: {rel: git blob id} of every shippable file, the whole mod, not only the touched files; each `.xml` passed through the deploy's own folded-id rewrite (`biomes_compose.rewrite_mayrequire` / `rewrite_findmod`, mapping computed from the manifest and About.xml files *at the build sha*, materialised with `git archive`) | r1#2: a stale file the commit did not touch, or a deleted one |
| `deployed` | the mod's game folder, located from the build's compose manifest, never by search: `Mods/<target>/<dest_rel(entry)>/` for a composed member (its `About/` excluded on both sides: the composed root carries the union), else `Mods/<Mod>/`; {rel: git blob id of the bytes} for every shippable file, plus each file's `(size, mtime_ns, ctime_ns)` | r1#1, r2b#7: content, not names or timestamps |
| `process` | `Get-Process RimWorldWin64`: exactly one, `(pid, StartTime UTC to the ms)` parsed as UTC | r1#3 (two games), r1#13 (DST) |
| `loaded` | `jawa/running_mods` (details, no assembly): `[(packageId, folder)]` in load order, and its sha256 | what this process loaded, unlike ModsConfig.xml |

**Pre-proof checks** (any failure = UNMEASURED with its reason):

1. `expected == deployed` as {rel: blob} maps: equal key sets (no extra, no missing file) and equal blob ids. The
   game folder holds exactly the build, whatever the working tree says. This replaces the deploy plan, `--deploy`,
   `changed_since` and mtimes: the plan compared the working tree, never the build.
2. The process started after every deployed file's `max(mtime, ctime)`. Probed 2026-11-02 on drvfs:
   `shutil.copy2` (what deploy_custom_mods.py uses) keeps the source mtime and sets ctime to the copy time, so ctime
   is the deploy moment and an mtime-preserving copy after launch is caught (r1#3 counterexample 1).
3. Every bound mod's game folder is the `folder` of a running mod or lies inside one (a composed bundle). A mod that
   is deployed but not loaded by this process is no measurement (r1#3 counterexample 2).
4. The build ships at least one game file. A build with no game file cannot bind the game to itself: UNMEASURED, not
   the old silent PASS-path that skipped every check (r2b#4). A path with a control character in it is UNMEASURED.

**Post-proof check:** `process`, `loaded`'s hash, `item_built`, the deployed key set and every file's
`(size, mtime_ns, ctime_ns)` equal the pre snapshot. Any write to a deployed file moves ctime, so the stat fingerprint
is enough after a full hash before. Any difference = UNMEASURED (r2b#3: a redeploy and restart during a long proof).

The row records both snapshots' digests (`build`, a sha256 over `expected`, `process`, `loaded` hash) so a verdict on
the ledger can be traced to the exact load it measured.

Instrument check (2026-11-02, `D:\ClaudeWork\rimmandrake\relentless_design_probe\blob_probe2.out`): Graffiti
(standalone) matches HEAD exactly, 77/77 blobs. The composed members ExplosiveGrowth, Miasma, Cauldron and BlueDesert
match except for files changed after their last deploy (e.g. `RM_BloomCrop.xml`, committed 2026-11-01, deployed
2026-10-16 with `harvestYield` 14 against 6). Those are real stale deploys, and the check reports them as UNMEASURED.
A first probe that searched `Mods/*/*/<Mod>` found a false folder (`UtinniPatches/Defs/ExplosiveGrowth`) and missed
the real one (`RimMandrake.Biomes/Biomes/_Kits/ExplosiveGrowth`). That is why the location comes from the manifest.

Limit, written down: mods the build does not touch are not hashed (a whole-list hash would read thousands of files on
/mnt/c per run). They are bound only through `loaded`: same packageIds and folders before and after.

## Rule 2. Fail closed, exit codes mapped explicitly

- **Tool verdict = exit code AND last line.** An allowlisted tool must print `VERDICT PASS|FAIL|UNMEASURED` as its
  last non-empty stdout line and exit 0/1/2 to match. The runner reads both; a mismatch, a missing line, or any other
  exit is UNMEASURED. A Python crash exits 1 with a traceback and no `VERDICT FAIL` line, so it can never read as FAIL
  (r1#7, r2b#2). Tools still wrap `main` in `safe_main` and print with `ascii()` so a surrogate cannot crash a print.
- **Runner:** `run()` is `_run()` inside `try/except BaseException`: any escape writes one UNMEASURED row, attempts the
  release if the bridge was taken, and never calls verify (r1#11). `main` maps PASS 0, FAIL 1, UNMEASURED 2,
  REFUSED 3; `safe_main` maps its own crash to 2.
- **Unreadable inputs:** a malformed `runs.jsonl` row makes the round refuse (it could hide a terminal FAIL and let a
  rerun clear it); unreadable item prose, a non-zero `git` exit, an unparseable `running_mods` reply, an unreadable
  deployed file: UNMEASURED with the reason.
- `live_def_check.py`: malformed records, duplicate JSON keys, contradictory duplicates, a non-bool `found`: UNMEASURED
  (kept from round 2).

## Rule 3. An allowlist of proof tools, not a shell blacklist

A proof is no longer a shell string. The grammar:

```
proof := step ( " && " step )*
step  := "python3" <tool path> <args>
```

- `<tool path>` must be a key of `PROOF_TOOLS`: `src/RimMandrake/Utils/live_def_check.py`,
  `src/RimMandrake/Utils/live_log_check.py`. Adding a tool is a code change to this file, reviewed as grader machinery.
- Tokenised by `shlex.split` (POSIX) and executed as an argv list with `shell=False`. Bash never sees the text, so
  quoting, `$var`, backticks, globs and brace tricks are inert strings (r1#6, r2b#1). A token that is a shell operator
  (`|`, `;`, `&`, `>`, `<`, `||`, `(`, `)`, backtick, `$(`) is refused: the author meant a shell and will not get one.
- `<args>` are validated by the tool's own `proof_parser()` (argparse, `exit_on_error=False`), so an unknown flag is
  refused before anything runs. Each tool also names its `PROOF_FORBIDDEN` flags: `live_log_check --log` (it skips the
  running-game check).
- Steps run in order; the first step that is not PASS decides (FAIL or UNMEASURED); all PASS is PASS.
- The flyer check stays (standing ruling), applied to title, criterion text and proof text.
- `--deploy` is gone: nothing in the live tier runs deploy_custom_mods.py at all, so it cannot be fed `--apply`
  (r1#5).

The one live-proof line in the books today (`live_def_check.py ... && live_log_check.py ...`) parses unchanged.

## Rule 4. Proof children reaped on every exit path

Each step is `Popen(argv, start_new_session=True)`. In a `finally` that runs on exit, timeout and exception alike:
`killpg(pgid, SIGKILL)`, wait for the leader, then poll `killpg(pgid, 0)` until `ProcessLookupError` (up to 5 s). A
group still alive after that makes the run UNMEASURED ("a proof process outlived the proof") and is recorded (r1#10,
r2b#6). The release happens after the reap. Residual risk, written down: a Windows `python.exe` started by a tool is
not in the Linux group; the tools bound it with their own `--timeout` and only read.

## Rule 5. Selftest fakes assert their arguments; mutants each rule kills

- Every fake records `(method, args)` and answers **keyed by its arguments** (`ls_tree[(sha, mod)]`,
  `deployed[mod]`, `running_mods` per call number), so a call with the wrong sha, mod or order gets a wrong answer or a
  `KeyError` that the runner turns into UNMEASURED, not the right answer by accident (r8a#1, #5, #6, #8).
- Each oracle row asserts the call log where the property is about *which* thing was measured: e.g. the identity is
  read after `bridge take` and again before `bridge release`, `verify` names the full built sha.
- Negative rows assert absence of effects, not only an exception: no `verify` call, no close, state unchanged.
- **Mutation check** (`selftest_relentless_live.py --mutants`, also run by default): each mutant is a monkeypatch of
  one design point, and the suite must go red under it:
  - M1 the post-proof identity check returns equal always (rule 1)
  - M2 the pre-proof blob comparison ignores blob ids (rule 1)
  - M3 the tool verdict reads the exit code only (rule 2)
  - M4 `run()` lets exceptions escape (rule 2)
  - M5 the allowlist accepts any tool path (rule 3)
  - M6 steps run with `shell=True` (rule 3)
  - M7 the reaper skips `killpg` (rule 4)
  - M8 the release result is not gated (rule 0)
  A mutant that survives fails the selftest.

## Rule 6. relentless.py: the three open items

1. **Evidence bound to build identity.** `finish()` requires a full 40-hex sha (no short id, no ref). The check
   record binds `{sha, gen, contract hash}` when the checker launches; when its verdict is consumed, the supervisor
   refuses it (checker_lost path, no failure counted against the work) unless the candidate's sha, gen and contract
   hash are unchanged. A FAIL is only charged to the sha the checker actually judged.
2. **Close retries re-check, with a budget.** Each closing attempt already re-reads live and publication. Added: the
   retry count is capped (`close_retry_max`, default 12); exhausting it is `close_stuck`, a failure that hands the
   item back instead of retrying for ever. `ledger_close` treats the item as closed only when the ledger's close names
   the candidate sha (r6a#3). Builder admission is re-run in full (breaker, cap, pause, memory, day budget, excluding
   this item's own reserved place) after the clone is prepared and before the launch (r6a#7).
3. **Deadline enforced on result arrival.** Each run, check and consult persists an absolute `deadline` when it
   launches (`started_at + run_max_s`, `at + check_max_s + launch_grace_s`, `at + help_max_s + launch_grace_s`).
   `finish()`, `verdict()` and `help_answer()` raise `Fenced` when the arrival time is past it, whoever delivers it;
   the tick's read of a walled box verdict passes the tick's own time as the arrival.

## What this replaces

Deleted from relentless_live.py: `refused_deploy`, `deploy_gap`, `plan_sections`, `deployed_paths` (glob),
`Fx.deploy_plan`, `Fx.changed_since`, `Fx.mtime`, the `forbid_re` regex and its rules entry, the `--deploy` flag and
relentless_live_round's `deploy_args`. Added: `src/RimMandrake/rimflow/live_identity.py` (identity snapshot, blob
hashing, process and running-mods reads) and the proof grammar in relentless_live.py.

## GPT design review (2026-11-02), and what changed

One review, `gpt_consult.py`, answer in `D:\ClaudeWork\rimmandrake\relentless_design_probe\design_review.md`.
It returned 13 counterexamples. Each one's disposition:

| # | counterexample | disposition |
|---|---|---|
| 1 | a pre-staged folder renamed into `Mods/<Mod>` after launch keeps old file times | **taken, partly**: the loaded-before check also covers every *directory* of the bound root (a rename or an added/removed entry moves the parent's mtime/ctime) and the root's parent. A swap that preserves directory times too is outside the threat model (the builder works in a walled box with no write to the game folder); written down |
| 2 | an untouched mod (or the composed root) overrides the value the proof reads | **limit, written down**: identity binds the build's own mods plus the running list. What the proof asserts is the criterion author's job, see 5 |
| 3 | `git replace` makes the full sha read another tree | **taken**: every identity git call runs `git --no-replace-objects` with `GIT_*` environment variables removed |
| 4 | a shadow module (`json.py` beside the tool) runs instead of the tool | **taken**: tools run as `<sys.executable> -I` with a scrubbed environment and the repo root as cwd. Before any step, the tool directory and its import closure are scanned, and a file named like a stdlib module refuses the proof. The bridge client runs as `python.exe -I` |
| 5 | an allowlisted proof that proves the wrong thing | **taken, narrow**: a built commit that touches `infrastructure/state/items/` (where the proof line lives) is REFUSED. The proof line's author is the item's filer, not the builder |
| 6 | a stat fingerprint can be kept while bytes change (FileBasicInformation) | **taken**: the post-proof snapshot re-hashes every bound file (a few hundred small files) as well as the stat fingerprint. The hash and stat for one file are read as stat, hash, stat, and a mismatch in between is UNMEASURED |
| 7 | the item moves between the last identity read and `verify` | **taken**: PASS and FAIL both name `--sha <build>`. The ledger counts a run only on the item's built sha, so a moved item is a no-op on the ledger, not a credit. `item_built` is re-read last, immediately before `verify` |
| 8 | `--lo` abbreviation and `--log=x` evade the forbidden-flag check | **taken**: proof parsers use `allow_abbrev=False` with no `fromfile_prefix_chars`. The forbidden check is on the parsed destination (`args.log is not None`), not on the token |
| 9 | a `setsid()` grandchild escapes the process group | **limit, written down**: with 4 in place, the code run is our allowlisted tools, which do not daemonise. A cgroup is out of scope for WSL here |
| 10 | a deadline judged against a time read before a blocking read | **taken**: `finish`/`verdict`/`help_answer` read `now()` themselves at the consuming transition. No caller passes an arrival time |
| 11 | `print("VERDICT FAIL")` and then a crash | **taken**: tools emit their verdict only from `safe_main` after `main` returns, so a crash after the verdict prints `VERDICT UNMEASURED` last. Selftest row added |
| 12 | an unbounded `wait()` in the reaper; a close retry counter lost on restart | **taken**: one monotonic 5 s budget covers kill, wait and probe. `close_tries` is persisted before the attempt is issued. Every effect call is a subprocess with its own timeout |
| 13 | mutants miss the deadline, flag abbreviation, isolation and the re-hash | **taken**: M9 (no deadline at arrival), M10 (`allow_abbrev` default), M11 (no `-I`), M12 (stat-only post check) |
