# TESTPILOT_FIX_RESOLVE_AFTER_CRASHED_PASS

Blind GPT review F5 of src/RimMandrake/Utils/arena/testpilot.py, probe p_crash_before_resolve. Evidence /mnt/d/ClaudeWork/rimmandrake/arena_testpilot/gpt_blind/ (gpt_round2.md, probes.py, probes_out.txt).

## spec
test() saves the final evidence and clears in_flight, then calls _crashed() and _resolve(). A pilot that dies in
that gap leaves the candidate `testing` with every scenario counted: the next pilot finds nothing valuable, excludes
the loaded candidate from `need`, and idles forever. Same gap after a second game crash skips the M5 quarantine.
Fix: result finalisation is recoverable. Pilot.wake() reconciles durable evidence into candidate state before any
scheduling: for every open (queued/testing) candidate it re-runs the crash count (_crashed) and the resolve
(_resolve). Both are idempotent (a terminal state is never left), so a wake after a clean pass changes nothing.

## criteria
- A1 L0: selftest t_resolve_after_crashed_pass: a pilot killed between the final PASS and _resolve leaves the candidate testing; the next pilot's wake resolves it pass with no reload and no test (red before the fix)
- A2 L0: the same test kills the pilot between a second crash record and _crashed: the next wake quarantines the item
