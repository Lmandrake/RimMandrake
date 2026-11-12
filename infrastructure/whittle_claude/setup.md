# Phase SETUP: pick one ticket, claim it, write its Whittle directory

Do these steps in order and keep this phase short (under 20 minutes). You do not build anything here.

**If the last line of the shortlist below starts with `PRE-PICKED:`, wc.py has already done every step of this phase
without a model (the gate, both claims, the Whittle directory, the commit and publish; owner order 2026-11-11 ~20:40
PST: check the tickets deterministically first). Make no tool call at all: your whole answer is the text after
`PRE-PICKED: ` on one line.** Otherwise do the steps below.

1. The clone is already level with origin/main (the loop synced it). The shortlist below is ranked for your lane; it
   already excludes needs=owner items, items another loop claims, and items owned by a seat other than BENCH or you.
2. Take the first item on the shortlist that you can finish in one Whittle (hours, not days). For each candidate, read
   `rimflow show <ID>` (criteria, runs, blocked_reason). Skip it, with one line in progress.md saying why, when:
   it is blocked and the reason still holds; it needs the other machine's game; it duplicates an item already closed;
   or it is a design question only the owner can answer (park that question instead: see common.md, then take the next).
3. Claim it in the shared table: `python3 infrastructure/whittle_claude/wc.py claim $RIMFLOW_SEAT <ID>`. Exit 3 means
   another loop has it: take the next candidate.
4. Claim it in the ledger. If its owner is BENCH:
   `rimflow reassign <ID> --to $RIMFLOW_SEAT --per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`, then
   `rimflow claim <ID>` (or `rimflow start <ID>` when its state needs it: read `--help`).
5. Decide the mode. `python3 infrastructure/whittle_claude/wc.py nonpass <ID>` prints how many of its latest runs are
   non-pass in a row. 3 or more: mode is `pilot` (a Test Pilot sitting: run `rimflow pilot <ID>` and read the brief it
   prints, and the `test-pilot-sitting` skill). Otherwise mode is `whittle`.
6. Write the Whittle directory `whittle/<dir>/` where `<dir>` is the item id in lower case:
   - `STATEMENT.md`: the item's done statement, one bullet per acceptance criterion, each a checkable claim with the
     evidence that would show it (a proof row, a selftest, a log line). Copy the criteria; do not invent new scope.
     For mode pilot, the bullets are the sitting's outcomes: the defect's cause shown by an experiment, the fix or the
     filed finding, and the run that shows it.
   - `NOTES.md`: what you learned while picking (runs so far, the last failure, blockage notes that apply, the proof
     script and site to read first, MOD/SITE/HARNESS classification of past failures where the run log says).
   - `MODE`: one word, `whittle` or `pilot`.
   - `PROMPT.md`: copy `$WC_TEMPLATE/PROMPT.md`, change every `whittle/` path in it to `whittle/<dir>/`, delete the
     leading HTML comment, and fill every angle bracket for this item: what the work is; how to see what the user sees
     (the proof script or selftest that shows each criterion, and where its result lands); what it has by name (the
     run command and the fast check, the logs and past runs, a second model: the `chatgpt-consult` skill); what it may
     not touch (other lanes' games, the owner's mod list on his campaign, anything outside the item). Replace the
     sentence "You are on your own branch; a bad result is thrown away, so try things." with "Work lands on main
     through ./publish: commit what works, keep experiments in scratch." Keep it short.
   Do not write DONE.md or JUDGE_PROMPT.md: the loop lays those templates in after you.
7. Commit `whittle/<dir>/` and your ledger shard (plus OWNER.jsonl if written) with explicit paths and `./publish`.
8. Append one dated line to `$WC_DIR/progress.md`: the item, why it was picked, the mode.

Your FINAL line of output must be exactly one of:
- `PICKED <ID> <dir> <mode>`
- `NONE <one-line reason>` when nothing on the shortlist can be taken this round (you claimed nothing, or you
  unclaimed it: `wc.py unclaim $RIMFLOW_SEAT <ID>` and give the item back to BENCH).
