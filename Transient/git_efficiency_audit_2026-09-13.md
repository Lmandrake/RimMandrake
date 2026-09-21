# Git efficiency/safety audit — 2026-09-13

Read-only audit for BENCH. Scope: every file matching the git-invocation grep
across `src/`, `infrastructure/`, `skills/`, `.claude/hooks` (28 hits from the
literal grep; see method below). No git, ledger, deploy, or bridge commands
were run; nothing else was touched.

## Method

```
grep -rlE "\bgit (add|commit|status|log|diff|rev-parse|push|pull|ls-files|cat-file|show)\b|subprocess.*['\"]git|Popen.*git|check_output.*git" src/ infrastructure/ skills/ .claude/hooks --include='*.py' --include='*.sh' --include='*.js'
```
returned 28 files. Each was read in full (or to every git call-site) and every
git wrapper's call sites were traced to see whether they fire once per run or
once per item in a loop.

**16 of the 28 were false positives** — the "git" match was prose (a comment,
docstring, or a `print()` string telling a human to run `git diff` by hand),
not an actual `subprocess` invocation:
`src/RimMandrake/bridgetools/build.py`, `src/RimMandrake/rimflow/selftest_cli.py`,
`src/RimMandrake/rimflow/render.py`, `src/RimMandrake/rimflow/model.py`,
`src/RimMandrake/Utils/deploy_custom_mods.py` (confirmed zero `subprocess` calls
anywhere in the file — despite being named SUSPECT HARD in the brief, it does
not invoke git at all), `src/RimMandrake/Utils/gen_pawnkind_roster.py`,
`src/RimMandrake/Utils/refresh.py`, `src/RimMandrake/Utils/worldmap_review.py`,
`src/RimMandrake/Utils/selftest_codebase_health.py`,
`.claude/hooks/block_blanket_git_stage.py` (parses `git ...` command *strings*
for the PreToolUse deny logic; never runs git itself),
`.claude/hooks/selftest_block_canon_contradiction.py`,
`.claude/hooks/selftest_block_blanket_git_stage.py`,
`.claude/hooks/selftest_warn_skill_unwired.py` (these three spawn the *hook
script* as a subprocess for testing; they never spawn git).

Of the remaining 12 that do call git, **most are already correctly batched**
— several carry their own review-history comments documenting an earlier
per-file bottleneck that was already fixed. Confirmed clean, no finding:
`src/RimMandrake/Utils/check_refs.py` (one `git ls-files` pair + one batched
`cat-file --batch-check` for all commit SHAs), `src/RimMandrake/Utils/
codebase_health.py` (`review_verdicts()` explicitly documents replacing 526
per-path `git log` spawns with a zero-git hash comparison, 2026-09-05),
`src/RimMandrake/Utils/codebase_health_publish.py` (2 total git calls per
run), `src/RimMandrake/Utils/project_maturity_dashboard.py` (1 call),
`src/RimMandrake/Utils/modcheck/status.py` (1 call),
`src/RimMandrake/rimflow/cli.py` (`_undocumented_work_warning` and the
`transient` sweep both carry comments documenting a prior per-item fix to
one batched `git log`), `src/RimMandrake/Utils/code_review_status.py` (the
2026-09-05 SCALING REWRITE this file's own docstring describes — `list`/
`check` are now zero-git; `canonical_rels` batches `ls-files` for a whole
path set in one spawn), `.claude/hooks/queue_lint.py`,
`.claude/hooks/warn_unclosed_queue_item.py`, `.claude/hooks/
set_session_title.py` (one child-process call per session start, with a
cheap precheck to skip it entirely once already done).

**4 files have real findings**, below.

## FINDINGS TABLE (most impactful first)

| path:line | pattern | what it does now | concrete fix |
|---|---|---|---|
| `.claude/hooks/selftest_queue_lint.py:80-91` (`run()`, called once per case, ~29 cases in `CASES`) | **S1** | Every test case calls `run()`, which does `tempfile.mkdtemp()` then `git init -q; git config user.email; git config user.name; git add -A; git commit -qm base` — **5 git spawns per case**, ~145 git processes for one selftest file, plus a 6th (python) subprocess to run the hook itself. The committed fixture (`BASE`) is byte-identical across nearly every case. | Build the `BASE` template repo **once** (module scope), then per case `shutil.copytree(template, fresh_tmpdir)` (a filesystem copy — the `.git` dir carries the commit with it, zero additional git spawns) instead of re-running `init`/`config`×2/`add`/`commit`. Cuts ~5 git spawns/case to 0; only the hook-invocation subprocess remains. |
| `.claude/hooks/selftest_warn_unclosed_queue_item.py:41-62` (`setup()`, called once per case, 8 cases) | **S1** | Identical shape to the row above: `tempfile.mkdtemp()` + `git init/config×2/add/commit` per case = **5 git spawns × 8 cases = 40 processes**. | Same fix: one template repo built once, `shutil.copytree` per case. |
| `src/RimMandrake/Utils/migrate_names.py:76-87` (`stage_folders()`) | **S1** + **E2** | `for old, new in sorted(rows["mod"]): subprocess.run(["git", "mv", old, new], ...)` — one `git mv` subprocess **per row**. The live `naming_rename_map.csv` currently carries **71 `mod`-kind rows**, so a real `--apply` run is ~71 serial git spawns, each independently taking `.git/index.lock` on a repo four other agents may be writing to at the same time — 71 chances to collide with a concurrent commit instead of one. | Do the filesystem move in Python (`dst.parent.mkdir(parents=True, exist_ok=True); src.rename(dst)`) for every row, collecting every touched path, then issue **one** batched `git add -A -- <touched paths>` at the end — git's own rename-similarity detection recognizes the old-path-gone/new-path-identical-content pair as a rename without needing 71 separate `git mv` calls. Collapses ~71 git spawns (and 71 index-lock windows) into 1. |
| `src/RimMandrake/Utils/code_review_status.py:783-795` (`cmd_migrate_hashes()`) | **S3** (minor) | `for rel, entry in todo.items(): r = git_bytes(["show", "%s:%s" % (sha, rel)])` — one `git show` per legacy entry needing a backfilled hash. | Could collapse into one `git cat-file --batch` fed every `sha:path` spec at once (same pattern `whats_new.py`'s `prefetch_blobs()` already uses one file over). **Low priority**: `migrate-hashes` is an explicitly one-time backfill tool for pre-2026-09-05 ledger entries, not a recurring hot path — mention only, not worth a dedicated ticket unless it's ever re-run at scale. |
| `src/RimMandrake/rimflow/selftest_undocumented_work.py:53-59` (`_commit()`, called per test case in `main()`) | **S1** (trivial) | `git add`+`git commit` per fixture commit inside a throwaway repo built under a fresh `.rimflow_selftest_undoc/` dir. Only ~3 commits total in the current test, so real cost is small. | Not worth fixing on its own — flagged only because it's the same shape as the two selftest rows above; if those two get a shared "test git fixture" helper, fold this one in too. |

**No E1/E3/E4 findings** — nothing in the git-calling scripts issues a bare
`git commit` with no pathspec, suppresses stderr on `git add`, or stages an
unscoped `-A`/`.`/`-u` against the *real* repo. (`selftest_queue_lint.py` and
`selftest_warn_unclosed_queue_item.py` do call `git add -A`, but always inside
a disposable `tempfile.mkdtemp()` repo, never the shared tree — not a finding
against the taxonomy's intent, which is protecting the shared checkout.)
`migrate_names.py`'s per-row `git mv` is real E2 exposure (see above) because
it runs against the live repo four windows share.

## PROPOSED TICKETS

1. **SELFTEST_GIT_FIXTURE_TEMPLATE_1** — files: `.claude/hooks/
   selftest_queue_lint.py`, `.claude/hooks/selftest_warn_unclosed_queue_item.py`
   (optionally `src/RimMandrake/rimflow/selftest_undocumented_work.py`). Build
   the shared `BASE` fixture repo once per selftest run and `shutil.copytree`
   it per case instead of re-running `git init/config/add/commit` per case.
   Cuts the two hook selftests from ~185 combined git spawns to ~2. Effort:
   small (a few hours) — the fixture-building code is already isolated in one
   helper function in each file.

2. **MIGRATE_NAMES_BATCH_MV_1** — file: `src/RimMandrake/Utils/
   migrate_names.py`. Replace the per-row `git mv` loop in `stage_folders()`
   with filesystem `Path.rename()` + one batched `git add -A -- <paths>`.
   Also closes the E2 index-lock collision exposure on a shared checkout.
   Effort: small — isolated to one function, and the tool is already
   dry-run-first so it's safe to test without touching real folders.

3. **CODE_REVIEW_STATUS_MIGRATE_BATCH_1** — file: `src/RimMandrake/Utils/
   code_review_status.py`, `cmd_migrate_hashes()`. Collapse the per-entry
   `git show sha:path` loop into one `git cat-file --batch` call (same
   pattern already proven in `whats_new.py::prefetch_blobs()`). Effort:
   trivial, low priority — one-time backfill tool, not a recurring cost.

## Highest-value single fix

**SELFTEST_GIT_FIXTURE_TEMPLATE_1.** It's the largest measured process count
(~185 git spawns across the two files) AND it sits directly in the path
CLAUDE.md tells every agent to run before every commit
(`run_selftests.py` → "run every selftest before a commit"), so this cost is
paid on essentially every commit cycle, by every seat, not once. Second:
**MIGRATE_NAMES_BATCH_MV_1** — smaller total spawn count but the only finding
that is also a live-repo safety issue (index.lock collisions against other
agents' concurrent commits), not just wasted time.

## Note on `superpowers:using-git-worktrees`

Per-agent worktrees would structurally prevent the index.lock-collision half
of `MIGRATE_NAMES_BATCH_MV_1`'s exposure (each agent's git operations would
hit its own `.git/worktrees/<name>/index`, not one shared `.git/index`) — but
it does **not** address any of the SLOWNESS findings above (S1 process-spawn
overhead on a slow 9p/drvfs mount is per-subprocess-start cost, unrelated to
whether the index is shared) and doesn't apply to the selftest findings at
all, since those already run against fully disposable `tempfile.mkdtemp()`
repos with no entanglement risk to begin with. Worth adopting for the
*shared-checkout* entanglement class generally, but it is not a substitute
for any of the three tickets above.
