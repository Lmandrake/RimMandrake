# Git migration — Phase 5 (2026-10-02)

Plan: `design/RimMandrake/git_workflow_plan_2026-10-01.md` §2.4 rows 5–7, §2.5 lessons, §2.3 artpipe, §4 row 5.

## 1. CODE_REVIEW_STATUS → per-seat append-only records

- Records: `infrastructure/state/code_review/<SEAT>.jsonl`, one JSON line each:
  `{path, sha256, verdict: clean|dirty|pruned, ts, seat, sha, date, cleanCount}`. Current state = last record per
  path ordered by `(ts, seat, file, line)`; identical duplicate lines collapse; a `pruned` record removes the path.
  `.gitattributes`: `infrastructure/state/code_review/*.jsonl merge=union`.
- Seat: `RIMFLOW_SEAT` → `AGENT_SEAT` → session role file → `UNSEATED` (provenance only, so it never refuses a review).
- `code_review_status.py`: CLI unchanged (check / mark-clean / reopen / list / prune / migrate-hashes). `load()` rebuilds
  the old `{path: entry}` dict from records; `save(data)` appends one record per changed path — every write is an
  O_APPEND, nothing is rewritten. Lock moved to `code_review/.lock` (gitignored).
- **Old JSON: removed, not kept frozen.** Its 3,911 entries were migrated into `code_review/SEED.jsonl` and
  `load()` reproduces the JSON dict exactly (verified equal, 3,911/3,911). Every reader already went through
  `CRS.load()` except `probe_png_wellformed.py`, which now does too; UI/doc text in `codebase_health.py`, the health
  tab + artifact template, `project_maturity_dashboard.py`, `block_forged_validation.py`, `rimflow/cli.py` and
  CLAUDE.md now name the records. A frozen copy would only be a stale second answer.
- Selftest `selftest_code_review_status.py` gained case 13: append-only, per-seat shard, cross-shard last-by-ts,
  duplicate collapse, pruned record.
- Append-only lint: `ledger_lint.py` did not exist on origin when this landed (Phase 4 in flight) — **its glob must be
  extended to `infrastructure/state/code_review/*.jsonl`** (see §6).

## 2. LESSONS_INBOX → one file per lesson

- `infrastructure/state/lessons/<utc>-<seat>-<slug>.md`, lesson text only; `lessons/README.md` is the standing header.
  Tool: `src/RimMandrake/Utils/lessons.py` — `add "<text>" [--seat S] [--slug words]` (O_EXCL create, prints the path
  to commit), `render` (→ gitignored `infrastructure/state/LESSONS_INBOX.md`), `list`.
- Split: 169 entries → 169 files; `<utc>` = the line's `git blame` commit time, seat = first BENCH/FOUNDRY/MACBENCH
  named in the text else `UNSEATED` (53 / 79 / 3 / 34). Rendered view's entry set = the old file's, verified by sorted
  diff. Header rewritten to state what IS (old "The 11 entries below" line was false at 169).
- Writers/readers updated: CLAUDE.md § Skills, CHARTER.md lessons line, FOUNDRY.md trap citation (`(filed: lessons)`),
  skills/README.md, `src/RimMandrake/Utils/handoff.py` (+ selftest), `.handoff.json` `lessons_file` → list
  `[lessons/, LESSONS_INBOX.md]`.
- **Lodestar `bin/handoff.py`** (own repo): `lessons_file` may be a path, a directory of lesson files, or a list;
  drain detection walks all of them and skips commits whose subject has `[no-drain]` (the split commit carries it, so
  the last real drain stays 2026-09-23). `docs/HANDOFF.md` updated.

## 3. DIRTY_CODE_REVIEW_STANDING_LOOP_1 table split

**The plan's premise was false — measured: the item has no generated table.** 6,373 lines, 0 table rows, no
generator anywhere in `src/` writes it; all 99 commits are hand-written wave write-ups appended by concurrent review
waves. That append-at-EOF is what conflicted (62 K=5 hits). Fix applied to the real cause: the item keeps its prose
(44 lines: the loop, the pause note, a new "one file per wave" rule); the 6,339 lines of waves 1–35 moved verbatim
to `infrastructure/state/code_review/waves/0000-history-to-2026-09-27.md` (frozen); each new wave is its own file
`code_review/waves/<utc>-<seat>-wave-<n>.md`. Nothing generated, so nothing gitignored here.

## 4. artpipe queue state out of git
(pending)

## 5. X2 replay with the full §2.4–2.5 path set

Same window and per-commit conflict lists as X2/Phase 4 (`replay.jsonl`, merge-tree at base P~K). Non-conflicting
set = Phase 4's (ledger shards union, queue views, health html/json, `codebase_health_last.json`, hub data) **plus**
`CODE_REVIEW_STATUS.json` (now per-seat append-only records), `LESSONS_INBOX.md` (one file per lesson),
`items/DIRTY_CODE_REVIEW_STANDING_LOOP_1.md` (generated table out), `infrastructure/artpipe/{pending,active,done,failed}/`.

| K | frozen `events.jsonl` excluded (takes no writes since 09-23) | strict (frozen file counted) |
|---|---|---|
| 1 | 122 / 3,403 = **3.6%** | 235 = 6.9% |
| 5 | 368 / 3,403 = **10.8%** | 720 = 21.2% |
| 20 | 681 / 3,403 = 20.0% | 1,064 = 31.3% |

**K=5 = 10.8%, under the 13.6% bar.** Untracking the artpipe top-level registry/logs too moves K=5 by 4 commits
(10.7%). Top residual paths at K=5: DLL/`.srchash` pairs (Phase 3's single-writer rule), roster/item docs.
Script: scratchpad `p5_replay.py`.
