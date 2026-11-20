## spec

Found in GimmeSomeSlack in-game visit 2 (2026-11-19, game a, tier gimmesomeslack, deployed DLL a00e4619…, source
85f388636e). Row `M8_break_two_ends_live_dead` (check `sc_cut_ends`) read FAIL in 7 of 9 core-block runs this
evening: run 1, m8rep1 to m8rep6 and the probe run FAIL; run 3 and run 4 PASS. Every FAIL reads the same: the west
(battery side) end at (156,153) is listed and live, the east end at (158,153) is missing from the census `ends` list,
and `decals.FrayDead` is 2. This is the symptom of RIMMANDRAKE_MEND_SLACK_DEAD_CUT_END_MISSING_FROM_ENDS (closed
2026-11-17 on 1d580847bd2e, six of six PASS then).

The experiment (`Transient/gss_v2/m8_probe.py`, result `D:\ClaudeWork\scratch\gss_v2\m8_probe.json`): when M8 reads
FAIL, poll and read the census again with NO tick between. The east end (158,153) is then listed, and FrayDead is 3.
It stays listed at +30, +250 and +1000 ticks, after 2 s of real time, and after a `fresh` probe (5 edges, 0
different, 0 missing). So the end is never lost. The first census after `destroy_batch` + `B.ticks(2)` + `poll` reads
the pieces before the rebuild that lays the east piece is published.

Measured, not traced: `RM_MapComponent_CordGraph` says that the public `Rebuild()` is complete for scripted callers
(the probes), but also that "a Build waiting on the graph worker returned the pieces already published". [guess ~70%]
the census ran while the graph worker held the graph, so it read the pieces from before the cut on the east side.
That breaks the promise that a probe reads a complete set. The player sees the dead end one frame or a few frames
later [guess ~80%: no extra tick was needed].

The fix is not known. Either the census (and every probe that reads Pieces) waits until the worker lands, or M8 waits
for `LastPending == 0` before it reads. The second is a check change: the Conductor decides it. The row stays FAIL in
visit 2.

## verify

Acceptance test: `python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots --skip-offline --only core`
on tier gimmesomeslack, five runs in a row, each prints `M8_break_two_ends_live_dead  PASS`. On 85f388636e it printed
FAIL in 6 of 6 core-only runs (m8rep1 to m8rep6, 19:28 to 19:40 PST). An offline test that fails on the old code
first is owed with the fix (for example: a census taken while the worker holds a pending build must list every end of
the finished build).

## criteria

- The first census after a one-cell cut lists both cut ends, the live end and the dead end, in every run.
- No probe that reads Pieces returns a set from before a pending build.

## refs

file: src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs
file: src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackProbe.cs
file: src/RimMandrake/GimmeSomeSlack/validation.py
