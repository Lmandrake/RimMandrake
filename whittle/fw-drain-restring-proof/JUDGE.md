# Independent fresh judge

The following result is copied exactly from evidence/judge_raw.json. Its complete raw envelope is preserved with SHA256 e350cb7d53cee2b4575949b3e21382158e84de43ce5cb7d3ae73d278bb920b4c. The call provenance and frozen input hash are preserved in evidence/judge_call.json and evidence/judge_input.txt.

No blocking findings: the M15f row now runs the real colonist job and checks the right things, and the A1 command only accepts a fresh, exact pass. This review was read-only: I read the source and the raw evidence, re-ran nothing and attached to no game.

**Bullet 1: real colonist job, not an instant restring**
- The production path `restring_style_job` (`src/RimMandrake/GimmeSomeSlack/validation_aerial.py:190`) is called once from `_run_live` at `:622`. It never sends the instant `restring:` verb.
- **Disconnected before:** it cuts the span between the masts at M2 and M3 and requires the cut to report done. It then requires both anchors to show the link as Cut with different net numbers (`:216-233, :271`). It restyles each side differently and requires different style runs (`:277`) and different styles (`:278`).
- **Job, not instant:** the order is placed with everyone drafted, and must show the order set and exactly one cut span (`:279-280`). `restringjob` (`AerialProbe.cs:115-123`) hands the work giver's own `RM_RestringSpan` job to a colonist through `TryTakeOrderedJob`. The script then requires that, right after the hand-off:
  - the span is still cut and both job counters are unchanged (`:289-290`);
  - the named worker resolves through `jawa/pawn_get`;
  - that worker is one of our colonists, upright, and actually running `RM_RestringSpan` (`:291-302`).
- **Joined after:** completion needs cut 0, the order cleared, and both counters up by exactly one (`:311-313`). Then the link must read Up on both sides with the same net (`:316`), the same style run (`:320`), and equal look, colour and raw style (`:321`). Every other member of that run must match too (`:322-324`).
- **Nonempty styles:** look and raw style must be non-blank strings, colour must be present (null or a string), and run must be an integer (`:244-248`).
- The probe verbs it uses (`restringorder`, `restringjob`, `restringstate`, `cstyles`, `crestyle`, `cprocess`) and the pawn probe's `cmd` echo and `job` field already exist in C#. The original file already used `restringjob` and `cstyles`, so this unit needs no shipping-source change.

**Bullet 2: failure can never pass**
- Every reading must have `success is True` and echo its own command (`:203`). Any exception before `:303` leaves the row UNMEASURED/HARNESS; any after it leaves FAIL/MOD. PASS is only set at `:325`, and a cleanup error forces FAIL/HARNESS and stops the whole run (`:342-347`).
- Missing or malformed setup is rejected: bad anchor ids, no colonist or none upright, duplicate colonists, a missing default style.
- The raw evidence shows this matters. In `red.stdout.txt` the old M15f passed through `restring:2,3` (`'before': ('Modern','Industrial')`, `'restring': True`). The final run, `final_cases.txt`, ran 16 tests, all OK, covering 19 false-pass faults (including a job that completes instantly, a job that never runs, the wrong worker, unequal or empty styles after, and timeout) plus bad or mismatched readings. `final.receipt.json` has rc 0 and covers both selftests.

**Bullet 3: the A1 command**
- `GSS_RESTRING_FIX_STYLES_UNRECONCILED.txt:6` runs `restring_style_proof.py` with `--max-seconds 900 < /dev/null`.
- Each attempt gets its own new directory, and the output file's modification time must fall inside that run, so a stale file can't count.
- `check_result` rejects:
  - an aborted run, or one where the script isn't `validation_aerial.py` or the mode isn't `live`;
  - malformed rows;
  - anything other than exactly one M15f row with status PASS and class MOD;
  - a detail block whose schema is not the integer 1 or whose `jobDef` is not `RM_RestringSpan`.

  Bad JSON raises a `ValueError` subclass, so it is caught. The driver must also exit 0. Stdout, stderr and a receipt are kept for every outcome, including timeouts.
- The proof file and the selftest docstring both say live L2 gameplay acceptance is still open; nothing claims it.

**Restore safety and bounds**
- Colonists are drafted and put back where they started, with a readback check, both before the cut and in `finally`. If one teleport fails it still tries the rest. Styles are reset to the suite default, as the original did, now on both sides.
- Completion is capped at 12 × 250 = 3000 ticks, each probe call waits at most 20 s, and the whole driver has a 900 s timeout.

**Non-blocking residuals**
1. If the job fails or times out after the cut, nothing re-strings the span, so a possibly live cut half stays in the scene. The colonists are drafted and parked, and the M15e block just before it behaves the same way, so this is not a regression. It is still a leftover scene hazard on the failure path.
2. The row can only pass if `jawa/pawn_get` returns `thingId` and `thingIdNumber` for a ThingID string. The bridge tool source does use `thingIdNumber`, but only a live run will confirm it. If it doesn't, the row fails rather than passing falsely.
3. I couldn't recompute the SHA-256 hashes without a shell. The final receipt's hashes match `source_hashes.json`, and nothing I read shows an art or DLL change, but I didn't byte-compare them.

would show: yes
