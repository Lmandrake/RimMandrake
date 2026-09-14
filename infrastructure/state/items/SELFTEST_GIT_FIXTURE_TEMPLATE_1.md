# SELFTEST_GIT_FIXTURE_TEMPLATE_1 — cut selftest git-fixture spawns ~10x

## spec
`.claude/hooks/selftest_queue_lint.py` (47 cases) and
`.claude/hooks/selftest_warn_unclosed_queue_item.py` (8 cases) each rebuilt an
identical committed base fixture from scratch per case: `git init` + two
`git config` + `git add -A` + `git commit` = 5 spawns × 55 cases = 275
processes, on every pre-commit run of these hooks.

## what changed
Both files now build the identical BASE tree into a template repo ONCE
(module-level `_template_repo()` / `_TEMPLATE`, still via the same 5 git
spawns), then `shutil.copytree` that template into each case's own
throwaway dir — no subprocess — before applying the case's edits/body. Each
copy keeps its own independent `.git` (copytree preserves it), so the hook's
own `git diff HEAD` call still runs against a real repo per case; only the
*setup* spawns were cut. Net: ~275 setup spawns -> ~10 (one template build
per file), the ~10x the item asked for.

`src/RimMandrake/rimflow/selftest_undocumented_work.py` (the third file the
item named) was checked and left unchanged: it already builds ONE repo for
the whole run and grows it with sequential commits (later cases depend on
earlier ones' commit history for the prefix-collision and body-mention
checks) — it was never doing a fresh `git init` per case, so the item's
"~185 spawns" estimate over-attributed to this file; it isn't part of the
fix.

## verify
`python3 .claude/hooks/selftest_queue_lint.py` — 47/47 passed.
`python3 .claude/hooks/selftest_warn_unclosed_queue_item.py` — 8/8 passed.
`python3 src/RimMandrake/rimflow/selftest_undocumented_work.py` — 5/5 passed
(unchanged, confirmed still green).
Full `run_selftests.py` run alongside this work — see commit for result.

## criteria
Both fixed files still pass every case; the shared fixture is built once per
file instead of once per case; no change to test coverage or hook behavior.
