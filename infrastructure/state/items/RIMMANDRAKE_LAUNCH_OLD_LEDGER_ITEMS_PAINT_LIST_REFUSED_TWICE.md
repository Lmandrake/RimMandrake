# RIMMANDRAKE_LAUNCH_OLD_LEDGER_ITEMS_PAINT_LIST_REFUSED_TWICE

## spec
`detached_helper.py` refuses a launch when its item is not in `helper_checkpoint.known_items()`. `known_items` reads
only the shard files in `infrastructure/state/ledger/events/`. An old item has its `file` event in the legacy file
`infrastructure/state/ledger/events.jsonl`, from before the ledger was split into shards. So the launch check says that
such an item "is not a ledger item", while `rimflow show` reads it.

The failure that happened, 2026-11-26: the owner lifted his hold on the old game-needs tickets. The Workshop Pipeline
(`list_dispatch.py`) started the onboarding bundle of the home `game:world-map`, led by `BIOME_PAINT_ONCE_AT_THE_END_1`
(filed 2026-09-20). The launch was refused twice (8:04 AM and 8:12 AM PST): `refused: BIOME_PAINT_ONCE_AT_THE_END_1 is
not a ledger item; file it first`. The bundle records are
`D:\ClaudeWork\rimmandrake\dispatcher\work_bundle\bundles\WB-game-world-map-20261126-154837.json` and
`WB-game-world-map-20261126-160433.json`. The lane sends the same refused launch again on each tick.

The fix: `known_items` knows every item that the ledger knows, the legacy file included. Use the ledger's own reader if
one exists; do not write a second parser of the ledger.

## refs
file: src/RimMandrake/rimflow/helper_checkpoint.py
file: src/RimMandrake/rimflow/detached_helper.py

## verify
Acceptance test, 1 pass expected. Seen red at filing (it printed `False`, exit 1, on 2026-11-26 at adeea8e75b and later):

    python3 -c "import sys; sys.path[:0]=['src/RimMandrake/rimflow','src/RimMandrake/Utils']; import helper_checkpoint as HC; k=HC.known_items(); ok='BIOME_PAINT_ONCE_AT_THE_END_1' in k and 'FLYERFRAMES_PROVE_JOINT_SESSION' in k and 'NO_SUCH_ITEM_EVER' not in k; print(ok); sys.exit(0 if ok else 1)"

The selftest of `helper_checkpoint.py` also gets cases on a made ledger folder: an item filed only in the legacy file is
known; an item filed only in a shard is known; an id that no file names is not known; a ledger with no file reads 0
items (the blind reading stays).

## criteria
- A launch of a detached run on an item that has its `file` event only in the legacy file is not refused as unknown.
- An id that the ledger does not hold is still refused.
- The lane's next tick starts the `game:world-map` bundle, or names another cause.
