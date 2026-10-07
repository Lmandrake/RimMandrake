# ART_LEDGER_SEAT_DEFAULT_1

## what was wrong

- `artledger.seat()` read `RIMFLOW_SEAT` / `ART_SEAT` and otherwise fell back to a silent
  `"BENCH"`. A FOUNDRY window exports `AGENT_SEAT=FOUNDRY`, which it ignored, so FOUNDRY's
  art installs were appended to `infrastructure/state/art/events/BENCH.jsonl` (e.g. the
  SALVAGE_WRECKAGE_EVERYWHERE_1 wave-2 install at `9c63abbb5`, 82 lines, each stamped
  `"seat": "BENCH"`).
- The PreToolUse push guards (`block_dll_source_mismatch.py`, `block_unledgered_texture.py`,
  `block_ledger_lint.py`) checked local `HEAD`, not the commit a `git push origin <src>:main`
  actually publishes, so a clean HEAD let a bad commit pushed by sha through. (The git-native
  `--git-pre-push` modes already read the pushed sha from stdin and were correct.)

## what was built

- `seat()` now resolves `RIMFLOW_SEAT` → `ART_SEAT` → `AGENT_SEAT` → this session's
  `.claude/session_roles/$CLAUDE_SESSION_ID`, and raises `NoSeat` at WRITE time otherwise.
  Reads never resolve a seat.
- The three hooks check the refspec SOURCE (`pushed_head()`), falling back to HEAD.
- L0: `selftest_art.py` (refuse with no seat; AGENT_SEAT picks the shard; RIMFLOW_SEAT
  outranks it) and `selftest_block_dll_source_mismatch.py` case 4b (bad commit pushed by sha
  with a clean HEAD is denied; fails on the old hook, passes on the new).

## not done, on purpose: moving the misfiled events

The BENCH shard is NOT rewritten. The art ledger has no move/re-attribute verb, shards are
append-only `merge=union` like the rimflow ledger, BENCH appends to that file concurrently,
and each misfiled event carries `"seat": "BENCH"` inside it, so moving lines would leave a
second lie (wrong `seat` field in FOUNDRY.jsonl) or require editing events in place.
`read_events()` merges every shard and dedups by id, so the misfiling changes no art state —
only attribution. If attribution ever matters, the safe shape is an appended
`reattribute` event (new verb), never a line move.
