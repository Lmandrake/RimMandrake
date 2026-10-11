# Log rotation — art ledger shards (2026-10-11, FOUNDRY)

Owner: *"we will need to rotate logs as needed."*

## Problem
`infrastructure/state/art/events/BENCH.jsonl` was 32,038,133 B, append-only, rewritten in 167 commits
(all since 2026-10-04). 24 MB is the one-time 10-04 backfill; steady growth ≈ 1.29 MB/day, so ~14 days
to the 50 MB per-file rule.

## Design
`art.py rotate <SEAT> (--before ISO | --keep-mb N) [--apply]` (dry run by default) moves a **byte-exact
prefix** of the live shard into write-once `events/archive/<SEAT>.<NNNN>.<from>_<to>.jsonl`
(create-exclusive, fsync'd, ≤ 30 MiB each). It keeps ≥ 50 lines live (union-merge context), refuses if
the shard's last line is torn, and refuses (rolling back) if the live file changed between plan and swap.
`concat(archives, tail) == original` is asserted before anything is written.

## Readers taught
- `artledger.read_events` / `_shard_sig` (cached Index) → `shard_files()`: per seat, archives by seq then the live tail, seats in the old order.
- `art_guard.ledger_at` (pre-push/PreToolUse texture guard) → `ls-tree -r` + `order_shard_names()`; stray files under archive/ raise instead of being skipped.
- `legacy_redo_triage.newer_ledger`, `artpipe/canon_check_labelset.owner_labels` → `shard_files()`.
- `.gitattributes`: unchanged — `events/*.jsonl merge=union` covers the live tails; archives are never modified so need no merge driver. A clone still holding the old full shard that appends and rebases lands tail + its lines (proved with `git merge-file --union`).
- `ledger_lint.py` does **not** read art shards (only `ledger/events` and `code_review`), so nothing to teach and nothing that would refuse a rotation push. ⚠️ It WOULD refuse a rimflow-ledger rotation as NOT_APPEND — rotating those needs a lint rule first.

## Proof
`src/RimMandrake/Utils/art/selftest_rotate.py` on a copy of the real shards: 22/22 PASS — archives+tail byte-identical, `read_events()` and a digest of the whole folded Index identical after a date rotation and again after a size rotation, `art_guard.ledger_at` identical across the rotation commit, earlier archives untouched by a second rotation. Planted defects all caught: old glob reader loses events; tail-before-archive order changes the fold; append between plan and apply refused; stray archive file refused. The 8 existing art selftests still pass.

## Other append-only logs (origin/main, >50 KB, Transient excluded)
| file | bytes | bytes/day by event ts (10-04..10-10 avg) | commits total | commits 7d | days to 50 MB at rate |
|---|---:|---:|---:|---:|---:|
| `infrastructure/state/art/events/BENCH.jsonl` | 32,038,133 | 4,572,967 (24 MB of it one 10-04 backfill; steady 10-05..10-10 ≈ 1.29 MB/day) | 167 | 167 | ~14 at steady rate |
| `design/RimMandrake/mod_audit/facts/mod_facts.jsonl` | 4,056,333 | 0 | 2 | 2 | — |
| `infrastructure/state/ledger/events.jsonl` | 3,889,473 | 0 | 2535 | 0 | — |
| `infrastructure/state/ledger/events/FOUNDRY.jsonl` | 1,945,980 | 146,330 | 1032 | 368 | 328 |
| `design/RimMandrake/mod_audit/MASTER_REGISTRY.jsonl` | 1,753,333 | 0 | 6 | 6 | — |
| `infrastructure/state/code_review/SEED.jsonl` | 1,131,248 | 0 | 1 | 0 | — |
| `infrastructure/state/ledger/events/BENCH.jsonl` | 655,835 | 25,794 | 619 | 212 | 1,913 |
| `infrastructure/state/art/events/FOUNDRY.jsonl` | 360,023 | 51,182 | 36 | 36 | 970 |
| `infrastructure/state/ledger/events/OWNER.jsonl` | 131,082 | 4,626 | 129 | 32 | 10,779 |
| `infrastructure/state/code_review/FOUNDRY.jsonl` | 88,725 | 11,604 | 36 | 31 | 4,301 |

Only the art BENCH shard is near the limit. Largest non-log files (not append logs, listed for scale): AgariluxPrime.png 27.4 MB, a 22.5 MB gif, four world .rws at 11–22 MB, nine GimmeSomeSlack `northstar/matrix_live_*.json` at ~8 MB each (≈ 70 MB of generated output in src/ — a derived-artifact candidate, not a log).

## Applied?
**No.** Dry run (`art.py rotate BENCH --before 2026-10-10T00:00:00`): pure_move=True; would move 57,405 lines into
`archive/BENCH.0001.20261004_20261009.jsonl` (31,076,279 B) and leave 961,854 B / 1,595 lines live.
Not applied because BENCH committed to the shard at 01:09 (`7cf08bf64`), inside the 60-minute quiet window.
NEXT: when BENCH's last art commit is >60 min old, run that command with `--apply` from a fresh clone and commit the archive + BENCH.jsonl together.
