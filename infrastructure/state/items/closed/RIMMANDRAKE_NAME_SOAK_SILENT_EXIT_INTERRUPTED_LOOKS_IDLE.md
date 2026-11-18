## spec

An instance of the owner's 2026-11-17 global rule — *"No data, failure, an answer of zero, or an answer of 'empty
set' are all different cases and will be differentiated in return values everywhere"* — inside the soak the owner
himself started.

**What happened, measured.** The soak started 2026-11-18T01:29:32Z and was dead by 01:30:00Z: no `prime95.exe` in
`tasklist`, no STOP file, and the log's last line `SOAK INTERRUPTED … steps=0`. Its CONTROL line passed first
(`inject_fatal_seen=1 inject_died_seen=1 heat_seen=1 load_seen=1 load=100 ok=1`), so the instrument was not blind —
the script simply exited. The same thing had happened ~6 h earlier (`SOAK END steps=0 passes_started=1 reason=`, with
an EMPTY reason) and an immediate retry 22 s later ran 32 steps fine.

**The defect, in the code.** `steve_cpu_soak.ps1` line 99: when the loop ends with no `$reason`, the `finally` block
logs `SOAK INTERRUPTED … (script exited without a reason; the next boot or task start resumes)` and the script exits
**0**. So "the soak died 28 seconds in having done nothing" and "the soak is not scheduled to run" and "the soak ran
and found zero faults" all leave a zero exit and a log a reader skims as benign. That is variant 1 of the
four-variant checklist (`infrastructure/state/lessons/20261117T225720Z-UNSEATED-all-nine-silent-failure-instances-found.md`):
the code COMPUTES the "could not look" case — it knows `$reason` is empty — and then drops it from the exit status.

`soak_read.py:120 exit_code()` is the reader and is closer to right (STALLED/NOT_PLANNED → 2, no control → 1), but it
cannot distinguish a soak that exited with `steps=0` and an empty reason from one merely between steps, because the
script never told it apart.

**The fix.** An interrupted soak that completed no steps exits NON-ZERO with a cause-specific code and a named cause,
and the `SOAK END reason=` line never carries an empty value — an unknown cause is written `reason=UNKNOWN: <what was
observed>`, never blank. Keep the four answers apart at both ends: an END on time with zero faults is a measured zero
and stays 0; an interruption with work done is resumable and says so; an interruption with `steps=0` is "could not
look" and must be loud; a planned run that has not started is NOT_PLANNED, not a failure. `soak_read.py` then reports
each distinctly, and the reader's verdict line survives a caller that loses the exit status.

🔴 Read the script again before starting: commit `c62f5f5d2a` changed its defaults to 72 h / resume-after-reboot
AFTER the reading above, so line numbers and the resume path may have moved. The script is 99 lines; read it whole.

## refs

file: src/RimMandrake/Utils/steve_cpu_retest/steve_cpu_soak.ps1
file: src/RimMandrake/Utils/steve_cpu_retest/soak_read.py
file: src/RimMandrake/Utils/steve_cpu_retest/selftest_soak_read.py

## verify

python3 src/RimMandrake/Utils/steve_cpu_retest/selftest_soak_read.py

## criteria

- A1: a log ending `SOAK INTERRUPTED` with `steps=0` reads as a FAILURE with its cause named, never as idle or green.
- A2: a `SOAK END` line never carries an empty `reason=`; an unknown cause is spelled `UNKNOWN: <observation>`.
- A3: a soak that ended on time having found no faults still reads as a measured zero and exits 0.
- A4: a run that was planned but never started reads NOT_PLANNED, distinct from both of the above.

## acceptance

Acceptance test: new cases in `selftest_soak_read.py` feeding four fixed log fixtures — interrupted-with-steps=0,
`reason=` empty, a clean on-time END with zero faults, and planned-but-not-started — asserting a different verdict
and a different exit code for each. Watched FAILING on the base commit (today the first two read as not-a-failure),
with the failing output quoted in the commit message. The PowerShell change is proved by the fixture its own logging
produces, since the script itself only runs on the Windows bench; the live run is recorded UNRUN with its command
until the bench next starts a soak.
