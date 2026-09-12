# HEALTH_UNMEASURED_HEADLINE_1

## The bug

`codebase_health.py`'s per-file `classify()` was already correct: when `git
status` cannot be read (`wt_known=False`) or the rimflow ledger cannot be
replayed (`ledger_known=False`), every file is classified `unmeasured`, never
a false `green` or `grey`. What was missing was a RUN-LEVEL claim. Nothing
said, out loud, "this run could not measure anything" — a reader (or a commit
message, e.g. the literal precedent `"1669 green, 0 unmeasured"` this item was
filed against) could see `counts.green == 0` and read it as "the codebase has
zero clean files today", when the true claim is "git access failed, so
nothing was measured at all, and green=0 tells you nothing about the repo".

Trigger observed live 2026-09-12: `git status` on this shared, concurrently-
edited checkout genuinely timed out (>8s) while writing this fix, from real
agent contention — not a hypothetical. `codebase_health.py`'s own `git()` had
no retry, so any transient `.git/index.lock` collision turned into a
permanently-unmeasured run.

## The fix

`src/RimMandrake/Utils/codebase_health.py`:

1. **Bounded retry on `index.lock` only.** `git()` now retries up to
   `GIT_LOCK_RETRIES` (3) times with growing backoff (`0.6s * attempt`,
   ≤3.6s total) but ONLY when the failure's stderr names `index.lock` —
   any other git failure (not a repo, git missing, a real timeout) still
   fails immediately, exactly as before. A collision that clears in the
   next second or two now succeeds instead of poisoning the whole run;
   a genuinely stuck lock still gives up in well under GIT_TIMEOUT*retries.

2. **A new pure function `run_headline(wt_known, ledger_known, counts,
   total_files, istats)`** returns `(measurement_ok, reasons, headline)`.
   `measurement_ok` is `wt_known and ledger_known` — the same two flags
   `classify()` already keys off of, not a count-based heuristic. When ok,
   the headline reads `"OK: measured N files (…)"`; when not, it reads
   `"THE RUN COULD NOT MEASURE: <reasons> — … Do not read counts (including
   green=0) as a health picture; rerun once git is available."`

3. The payload now carries `measurementOk`, `measurementReasons`, and
   `headline`. The CLI prints the headline banner (`!`-bordered) right after
   the file/line count, before the per-status breakdown, on a bad run. The
   embedded HTML page's JS inserts a red banner above the header when
   `DATA.measurementOk === false`.

4. `codebase_health_publish.py` carries `measurementOk`/`headline` through to
   the artifact payload and the hub tab data, and its own `REBUILT …` summary
   line — the exact shape that got pasted into a commit message before —
   prints the honest headline instead of a `red/blue/green/grey/unmeasured`
   breakdown when the run could not measure.

5. `infrastructure/dashboards/hub/make_tab_data.py`'s `health()` now passes
   `measurementOk`/`headline` into `data/health.json` so the hub tab has the
   signal available (the hub shell's own rendering of it is a follow-on, not
   done here — this item's scope was the generator's own headline).

## Test evidence

Offline (`selftest_codebase_health.py`, extended, still 0 git calls):
`run_headline` asserted ok=True on a healthy run, ok=False (with the honest
"COULD NOT MEASURE" text, explicitly warning against reading `green=0` as
fact) when `wt_known=False` alone and when `ledger_known=False` alone.

`git()` retry, via monkeypatched `subprocess.run` (no real repo touched):
- index.lock clears after 2 failed attempts -> 3rd call succeeds (rc=0,
  3 calls, ~1.8s).
- index.lock never clears -> gives up after `GIT_LOCK_RETRIES+1` = 4 calls,
  ~3.6s, never hangs.
- a non-lock git failure (`fatal: not a git repository`) is never retried
  (1 call).

Full-tool end-to-end (`main()`, real repo, only `working_tree_changes()`
monkeypatched):
- **Broken**: `working_tree_changes` forced to return `None` (simulating
  exhausted retries) -> `measurementOk=False`, `green=0`, headline contains
  "COULD NOT MEASURE", CLI prints the `!`-banner.
- **Healthy**: `working_tree_changes` forced to return `set()` (a clean
  tree) -> real run against this repo's real ledger/review log ->
  `measurementOk=True`, `green=1669`, headline `"OK: measured 2305 files
  (1669 clean, 242 dirty, 0 unmeasured)."` — the working case is unbroken.

`python3 src/RimMandrake/Utils/selftest_codebase_health.py` — still ok, all
existing + 3 new assertions pass.
