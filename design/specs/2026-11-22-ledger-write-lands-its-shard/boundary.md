# BOUNDARY: a rimflow write lands the paths it wrote, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/ledger_landing.py` (the one home), its two recorders (`model.append` for a ledger shard,
`cli.py` for item prose) and `cli.py main` (`--publish`). Item: `RIMMANDRAKE_MAKE_LEDGER_NOTE_LAND_ITS_OWN_SHARD_PROSE_STEP`,
candidate 7 of `design/specs/2026-11-22-pipeline-single-source-sweep/report.md`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_ledger_landing.py`.

Before this page, a helper was told in prose which shard to publish after a write: "your seat's shard, and OWNER.jsonl too
after `--per-ruling`, `--owner-said` or `--by-card`". That rule was wrong for 1,260 of the 9,481 OWNER.jsonl events on
2026-11-22 (1,252 `game` stamps, written by `./game --why`, which carry no owner flag), and it never named the item prose
that a card stamp writes or that `close` moves. The CLI knows what it wrote, so it names the paths itself.

## ACCEPTS (the only inputs this is built for)

- **a-rimflow-write.** Any `rimflow` verb, run with or without `--publish`, whose ledger lies inside a git clone with an
  `origin` that `./publish` can land on (a seat clone, a helper clone, or a test's temp clone of a bare repo).

## DOES NOT SURVIVE (not promised)

- **a-ledger-outside-a-clone.** A ledger whose folder is not in a git work tree: `--publish` lands nothing and exits
  `LANDING_FAILED` with the cause.
- **another-writer-in-the-same-shard.** `./publish` commits a whole file. Lines that another process appended to the same
  shard before the landing ride along. They are ledger lines of the same clone, so this is the intended effect.
- **side-files-outside-the-repo.** `fulltext` side files live in agent storage, not in the repo, and are not landed.
- **a-killed-process.** A process killed between the write and the landing leaves the write unpublished; the helper's
  finish step (`detached_helper.py`) still publishes every dirty shard.

## PROMISES (each one is owed a test of the same name)

- **records-the-shard-each-append-wrote.** Every `model.append` records the one file it appended to: OWNER.jsonl for an
  event of seat OWNER (any owner flag, `./game --why`, `--seat OWNER`), the seat's own shard otherwise. A failed or
  refused append records nothing.
- **records-the-item-prose-a-write-made.** A card stamp's prose append, `close`'s move to `items/closed/` and `reopen`'s
  move back are recorded, both paths of a move.
- **publish-lands-exactly-the-written-paths.** With `--publish`, after the verb exits 0, one `./publish -m "ledger: <ID>
  <verb>" <paths>` runs in the ledger's clone, naming exactly the recorded repo paths (sorted, each once; a deleted path
  only when git tracks it). Its `PUBLISHED <sha>` line is printed and the verb's exit code stays 0.
- **a-plain-write-runs-no-git.** Without `--publish`, nothing is published and no git command runs for the landing.
- **a-failed-landing-is-named.** A landing that does not print `PUBLISHED` exits `LANDING_FAILED` (4) and prints one line
  `WRITTEN, NOT PUBLISHED: <cause>; to pass, run in <clone>: ./publish -m ... <paths>`. The write itself stays.
- **a-write-of-nothing-says-so.** `--publish` on a verb that wrote no path prints `nothing to publish: this command wrote
  no ledger or prose path` and keeps the verb's exit code. Nothing is run.
- **a-refused-verb-lands-nothing.** A verb that exits non-zero runs no landing. When it wrote paths before it failed, it
  prints `NOT PUBLISHED (the command exited <rc>): ./publish -m ... <paths>`.
- **matches-every-recorded-event.** For every recorded ledger event, the shard that the new home records on a replay is
  the shard the event lives in (`selftest_ledger_landing.py --all` runs every event in the tree; the selftest runs the
  frozen sample `selftest_ledger_landing_recorded.jsonl`).

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
