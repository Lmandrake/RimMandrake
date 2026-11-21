# BOUNDARY: the launch's refusal of an item not filed on origin/main, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`origin_check`, `publish_command`, the I6 gate in `_launch`).
Item: `RIMMANDRAKE_FIX_THREE_TOOL_DEFECTS_LESSONS_DID_NOT_STOP`, written 2026-11-19. The helper's clone is made from
origin/main, so an item whose `file` event sits only in this clone's ledger shards (OWNER.jsonl, from `--per-ruling`,
`--owner-said` or `--by-card`, whatever `--seat` said) is refused. The refusal used to say "publish <shard> first";
agents met it seven times after a lesson said what to do (Crystallize 2026-W47, sweeps §5 cluster 1:
`infrastructure/state/lessons/20261108T005209Z-BENCH-detached-helper-py-launch-refuses-item.md` and six more). Each
promise has a test of its name in `src/RimMandrake/rimflow/selftest_detached_helper.py`.

## ACCEPTS (the only inputs this is built for)

- **an-item-on-the-ledger.** An id `launch` already found on the ledger (`helper_checkpoint.known_items`).
- **this-clones-shards.** The working-tree shards under `infrastructure/state/ledger/events/` of the clone the launcher
  runs from (`REPO`), committed or not.

## DOES NOT SURVIVE (not promised)

- **a-filing-in-another-clone.** An item filed only in another clone's shard (the Conductor's bench, say) cannot be
  found from here; the refusal says no local shard holds it and names where to publish from, not which clone that is.
- **a-note-event-only.** Only `file` and `spawn` events file an item; a note that exists only locally is not checked.

## PROMISES (each one is owed a test of the same name)

- **an-unpublished-item-refusal-prints-the-publish-command.** A launch refused because the item is not filed on
  origin/main, while shards in this clone file it, prints one line holding the exact command that passes:
  `to pass, run in <REPO>: ./publish -m "ledger: <ITEM> filed" <shard> [<shard>...]`, naming every local shard that
  files it, OWNER.jsonl included. A failed fetch is named after it, on the same line.
- **an-unpublished-item-refusal-publishes-nothing.** For a caller that is not the owner or the Conductor window (a
  launched run, another seat), the refusal runs no git command but the one fetch and the one search: nothing is
  committed or pushed for the caller, and no clone, unit or run record is made. The Conductor's own launch runs that
  `./publish` itself and goes on (`origin_gate`; design/specs/2026-11-21-never-refuse-the-conductor/boundary.md).
- **an-item-filed-nowhere-here-names-where-to-publish.** When no local shard files the item, the one-line refusal says
  so and names the command to run in the clone that filed it: `./publish -m "ledger: <ITEM> filed"
  infrastructure/state/ledger/events/<SEAT>.jsonl infrastructure/state/ledger/events/OWNER.jsonl`, `<SEAT>` being the
  launch's own `--seat` (the shard a plain `rimflow file` writes) and OWNER.jsonl the one a provenance flag writes.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
