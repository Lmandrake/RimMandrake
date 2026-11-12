# Phase WRAPUP: end the ticket

The Whittle phase for the item below has finished (its exit code and log tail are below: 0 the stop checker passed,
1 incomplete after the allowed runs, 2 BLOCKED or STOP). Keep this phase short (under 20 minutes).

1. Read `$WHITTLE_DIR/DONE.md`, `JUDGE.md`, `NOTES.md`, any `BLOCKED.md`, and `rimflow show <ID>`.
2. Decide the ending, one of:
   - **closed**: every criterion is true with evidence on disk and the judge ended `would show: yes`. Close it with
     `rimflow close <ID> --sha <the literal sha that carries the work> ...` (read `close --help`: an operational or
     live item may need `--live` or run evidence). If the item still needs a step only another lane can do, do not
     close: hand it on with a note (`rimflow note`) and `rimflow reassign <ID> --to BENCH --per-ruling
     CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`, and call the ending parked.
   - **parked**: an owner question stands. It is in `$WC_DIR/OWNER_QUESTIONS.md` (write it there now if the Whittle did
     not) and noted on the item. Give the item back to BENCH as above.
   - **dropped**: the item is wrong, duplicated or no longer wanted: `rimflow drop <ID> --why "..."` (or supersede per
     `deciding-and-superseding` when another item carries it).
   - **failed**: the work is unfinished and no owner question explains it. Note on the item what was tried and the next
     step (`rimflow note`), give it back to BENCH. If its last 3 runs are non-pass, note that it needs a Test Pilot
     (`rimflow pilot <ID>` names the route), so the next pick takes it in pilot mode.
3. Release the bridge if this lane holds it: `rimflow bridge who`, then `rimflow bridge release` (with
   `--host stevedesktop` in the SteveDesktop lane). Leave the game running unless your lane file says otherwise.
4. Commit everything of this round with explicit paths (the Whittle directory, your ledger shard, OWNER.jsonl if
   written, any source changes the Whittle left uncommitted that belong to the item) and `./publish`. Uncommitted
   files that do not belong to the item: list them in progress.md and leave them.
5. Release the shared claim: `python3 infrastructure/whittle_claude/wc.py unclaim $RIMFLOW_SEAT <ID>`.
6. Append one dated paragraph to `$WC_DIR/progress.md`: the ending, the sha, the evidence paths, and what the next
   round should know (a blockage you met, a harness fault you fixed).

Your FINAL line of output must be exactly:
`RESULT <ID> closed|parked|dropped|failed sha=<published sha or none>`
