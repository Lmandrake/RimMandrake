# Fresh-model broadening

A separate fresh Opus print process reviewed the initial deficient code. The preserved call receipt records neutral cwd, read-only tools, empty strict MCP, no settings, no persistence and input SHA256.

## Exact question

Read /home/mandrake/rm/scratch/BENCH/fw-drain/whittle/fw-drain-restring-proof/STATEMENT.md and NOTES.md, /home/mandrake/rm/scratch/BENCH/fw-drain/src/RimMandrake/GimmeSomeSlack/validation_aerial.py M15e/M15f, AerialProbe.cs, RestringJob.cs, ConduitStyleProbe.cs in its Source/Aerial directory, and /home/mandrake/rm/scratch/BENCH/fw-drain/infrastructure/state/live_proofs/GSS_RESTRING_FIX_STYLES_UNRECONCILED.txt. This is an offline L0 proof-tooling repair, no game access. What adversarial cases would expose a false PASS in an actual colonist-job style-join proof and its fresh-row command? Broaden beyond the obvious. Propose the most revealing focused fake-bridge production-path scenarios, including colonist return/draft safety, malformed data, bounded completion, and stale receipts. Read-only review. Do not write files. Return concrete test suggestions.

## Exact reply

I found one blocking problem and a set of smaller gaps where the row could still pass falsely. All of this is from reading the files; I didn't run anything or write any files.

## Where things stand

- **M15f doesn't use the colonist job yet.** Lines 439–462 of `validation_aerial.py` rejoin the span with the instant `restring:` verb (line 450). That contradicts the first and second points of STATEMENT.md.
- **The existing selftest fails against the current code.** `selftest_gss_restring_proof.py:113-118` expects `restringjob:2` and forbids `restring:`. That's the right check, but the production code doesn't do that yet.
- **The selftest doesn't call the real code.** It copies the text between two comment markers and runs the copy (`:102-109`). If the markers move, or M15f starts using `nets`, `one_net` or `real` (defined inside the live function at `validation_aerial.py:247-257`), the test checks a copy or crashes. Move M15f into a module-level function like `m15f_restring_one_look(B, rows, i2, i3)`. Have the live function call it, and add a test that confirms it does.
- **There's no A1 command.** The `.txt` file only has A2, and its comment still says A1 "has no row yet".

## Suggested fake-bridge scenarios

Every scenario below must produce FAIL or UNMEASURED, never PASS, unless it says otherwise.

### 1. Did the actual job do the rejoin?
1. **Golden path:** cut works, two looks, `restringjob` succeeds, ticks pass, the job finishes, then one look. The result should be PASS, with no `restring:` sent anywhere in the M15f block (cleanup included) and `restringjob:<i2>` sent exactly once.
2. **Something else rejoins the span:** `restringjob` succeeds, but the span comes back without the job finishing (simulate the watchdog, or a leftover `restring:`), so `jobsDone` doesn't go up.
3. **Counter left over from M15e:** `jobsDone` and `spansRestrung` start at 5 and stay at 5 while `cut` drops to 0. The current fake reports these as absolute values (`int(completed)`), so it can't catch this. The proof must check that each counter went up during M15f.
4. **Job ends but a roof refuses the splice:** `jobsDone` goes up by 1, the mark clears, `spansRestrung` stays the same, `cut` stays at 1.
5. **The job never starts:** `restringjob` reports `success:true, by:"Human7"`, but the pawn never gets `RM_RestringSpan` (poll `colonists`). The probe ignores what `TryTakeOrderedJob` returns (`AerialProbe.cs:121`). Have it report a `"taken"` field and fail when that's false. A source check on the C# is a fair offline test.
6. **Pawn ID mismatch:** `by` uses the `ThingID` form ("Human7") while `colonists` uses numeric `id`s. Feed a `by` that matches no listed pawn.
7. **Another colonist grabs the job first:** `restringorder` places the mark, then 5 ticks pass before `restringjob`, so a scheduled pawn can reserve it. `restringjob` then fails with "no free colonist" and the row must be UNMEASURED, even if the span later reads as rejoined.

### 2. Was it really "the only joining span"?
8. **`cut:` returns `done:false`,** but stale reads still show two looks. Nothing checks `done` today.
9. **The two sides were never separate:** before the job, members at M2 and M3 already share one `run` id in `cstyles`, for example because a ground conduit joins them. Require different `run` ids before and the same `run` id after.
10. **Nets join but runs don't:** after the job the nets read as one but the `run` ids are still different. Also require `counters.linkBridges` to go up between the split read and the joined read. That proves `Patch_Restring_Bridge` ran.
11. **Wrong span restored:** the census shows the `i2` link to some other anchor as Up, while `i2↔i3` stays Cut.

### 3. Is it really "one style"?
12. **Same look, different colour:** after the job both sides read `Modern` but with different `colour` or `rawStyle`. `look_of` only compares the look, so this passes today. Compare `(look, colour)` or `rawStyle`.
13. **Both sides reset to default:** after the job both read `Scrapper` or the default look. They're equal but neither original style survived. Require the joined look to be one of the two looks from before.
14. **Only the masts were checked:** M2 and M3 match, but another member of the run (M1, a conduit, or the lamp's `runLook`) keeps the losing look, or the restrung span's cord `pieces` keep the old look. Check every member with the joined `run` id.
15. **Two members on one cell disagree:** `look_of` takes the first one. Require exactly one member per cell, or all members there to agree.
16. **Restyle did nothing:** `crestyle` returns `success:true, changed:0`. Require `changed > 0` for both sides.
17. **Unprocessed queue:** `counters.pending > 0` in either the split or the joined `cstyles` read. Treat that as an unreliable reading (UNMEASURED).

### 4. Colonist return and draft safety
18. **Splicer downed by the live half:** the cut leaves M2's half live because of the battery, and the work target falls back to touching M2. Fake the pawn as `downed:true` with no job, the mark still on and `cut:1`. The row must not pass, and the harness must not use `restring:` to clean up before the row's result is recorded.
19. **Pawns start drafted:** they all begin drafted because M15e drafts them (line 437). Confirm the job is still taken, or that the row says UNMEASURED with a reason if it isn't. Don't let a silent no-op look like a successful job.
20. **Return home on every path** (PASS, FAIL, UNMEASURED, timeout, exception): the `by` pawn gets `tp` and `draft` after the result is recorded. Use try/finally. Also check that the teleport-home happens before M15f's `cut:`, so the cord never falls on someone. That was the 2026-11-06 downing.
21. **Missing home position:** `colonists` returns `pos: null` for the splicer. Skip the teleport without crashing, and still record the result.
22. **Leftover mark:** `restringjob` places the mark even when it fails (`AerialProbe.cs:114` runs before `:120`). After a failure, cleanup must remove the mark so no scheduled colonist splices the span later.

### 5. Bounded completion
23. **Ticks don't advance** (`B.ticks` does nothing, e.g. the game is paused). The loop stops at its limit and the row isn't PASS.
24. **Job never finishes:** the poll limit is hit, so cancel the job and remove the mark. Then a tick later, the fake completes the job. Later reads must not change the recorded result, and that late completion must not count.
25. **Job ends early:** the pawn's job goes to `None` while `cut` is still 1. Fail fast instead of waiting out the whole limit.
26. **Finished just past the limit:** completion lands at poll 13 against a limit of 12. Assert it's a FAIL, which checks that the limit really is enforced.

### 6. Malformed data
27. **Bools where integers belong:** `cut: false` and `jobsDone: true`. In Python `False == 0` and `True > False`, so the current checks (`:421`, `:427`) accept them. Use the strict integer check that `real()` already does.
28. **String booleans:** `done: "false"` or `designated: "no"`. Both are truthy, so require `is True` / `is False`.
29. **Broken `members`:** missing, `null`, not a list, entries missing `x`/`z`, or coordinates as strings. Looks of `None`, `""`, a number, or a different case (`"industrial"`).
30. **Unparseable or failed replies:** non-JSON (`{"success":False,"raw":…}`) or `success:false` with stale fields still present. Any reply with `success` not exactly `True` must stop the row from passing.

### 7. Stale replies from the probe
31. **Serial read fails:** in `ap()`, the first `get serial` returns no value, so `before` is `None` and any real serial counts as changed. `ap()` then returns the `result` left by an earlier run (`:69-81`). Fake a failed first get with an old `cstyles`/`restringstate` result in place, and `ap()` must reject it.
32. **Serial race:** a request that timed out earlier gets answered between reading the serial and setting the new request. Match the `cmd` echo. Because `restringstate:<i2>` uses the same command string in M15e and M15f, the echo can't tell them apart. Also require the serial to go up by exactly 1, or add a game tick or nonce to each reply, and require `st1.tick > st0.tick ≥` the job's start tick.
33. **Joined read comes before the job finished:** the fake returns the joined `cstyles` with a tick earlier than the job's completion.

### 8. Tests for the A1 command
Feed the checker part of the command sample JSON files.

34. **Freshness:** missing file; file older than 1800 s; file with a future modification time (a negative age passes `<1800`); a stale file that survives because `rm -f` failed on `/mnt/d`. Checking against a start time recorded before the run, or a run nonce, is stronger than the 30-minute window.
35. **Row content:** `rows` missing or not a list; non-dict entries; two M15f rows where the first is PASS (`r[0]` takes it); status `"pass"` in lowercase; PASS with kind `HARNESS`; JSON cut off partway.
36. **Old-format PASS:** an M15f PASS row whose evidence has no job fields (`by`, counter increases, `run` ids, `linkBridges`). This is exactly what today's instant-verb M15f would produce. Require those fields in the row's evidence or a schema version, not just `status`.
37. **The command file:** both `live-proof A1:` and `A2:` parse, and `proof_budget` still reads `--max-seconds 900`. A1 and A2 both delete and rewrite the same `aerial.json`, so either run one live session and check both rows, or give them separate output files. Also update the stale "A1 has no row yet" comment.

### 9. Leave the approved art alone
38. **Cleanup on FAIL:** today it only restyles M2's side (`:461`). If the runs didn't join, M3's side stays `Industrial` in the save. Cleanup must restore both sides, run from `finally`, and report when the restore fails. This follows from the "approved art must remain unchanged" note in NOTES.md.

**If you only do a few:** #2, #3, #9/#10, #12, #18, #24, #27, #31 and #36 are the most likely to catch a false PASS that the current fake can't.

## Implemented revealing cases and results

The final focused suite directly calls the production helper and checks its call from the live flow with AST inspection. It tests counter deltas from a pre-existing value of five, a successful job request without a running job, mismatched worker identity using the inspected pawn_get contract, colour-only disagreement, style-run disagreement, malformed numeric/boolean payloads, reciprocal exact-pair span state, a stale or future result, duplicate rows, an old instant-path PASS lacking job schema, raw-log retention and the twelfth/thirteenth completion boundary. Both sides receive default-style restoration in finally, and colonist parking failure stops the later flow.

The exact command and actual outputs are in evidence/offline_validation.md. The final run passed both selected test files, including 16 focused unittest methods and their subcases. Zero cached or skipped tests supplied the result. The original direct-bypass path produced RED.

The initial review proposed a fixed surviving input style. The implementation accepts either style or any equal nonempty full style produced by the job, following the user’s instruction against an arbitrary winner. Generic probe transport changes and compiled-source changes are outside this unit. The helper requires matching command echoes for its readings. Failed jobs leave colonists returned and drafted, which cancels their current job through the existing teleport contract.

Raw envelope and provenance are evidence/broaden_raw.json and evidence/broaden_call.json. Every test is offline instrumentation. Separate L2 gameplay acceptance remains open.
