
## spec
`RUN_SHEET_PER_LOAD_BLOCKS_1` gave `NEXT_RELOAD.md` an index: one row per block, ⏳ PENDING
until scored, and the rule that a scored block moves whole to `NEXT_RELOAD_ARCHIVE.md`.

🔴 **That is discipline, and `CLAUDE.md` is explicit that discipline decays:** *"Single-source
only what a GENERATOR can enforce. Where only discipline enforces it, expect decay."* The index
will be right until the first hurried load and wrong forever after — which is how the file
rotted the previous two times.

**Make it a check:**
1. Read the ⏳ rows out of the index table in `infrastructure/state/NEXT_RELOAD.md`.
2. Read the timestamp of the most recent `game UP` event from
   `infrastructure/state/ledger/events.jsonl`.
3. **Any block whose `deployed` date precedes that load and is still ⏳ is stale** — either it
   was scored and nobody moved it, or it rode a load and nobody looked. Both are worth saying.

⭐ **Wire it where it will be SEEN.** ⚠️ A `warn_*` PreToolUse hook prints to the OWNER's
terminal on exit 1 and **never reaches the agent's tool output** — measured 2026-08-23, and it
is why a budget overrun went unnoticed for a whole session. So either exit 2 (blocking, which an
agent does see) or put it in something a seat already runs, such as `rimflow next`.

## verify
Mark a block ⏳ with a date older than the last `game UP` and confirm the check names it. Then
mark it archived and confirm it goes quiet. **A check that cannot fail on demand is not a check.**

## criteria
- [ ] Stale ⏳ blocks reported automatically, by something a seat already runs.
- [ ] Proven to fire on a deliberately stale row, and to go quiet when fixed.
