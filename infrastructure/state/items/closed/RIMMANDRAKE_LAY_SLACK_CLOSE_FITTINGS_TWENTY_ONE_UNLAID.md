## spec
Gimme Some Slack: the live-end lay (item `RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN`, published 6ecfb14c822b) left 21 of 288 sampled close-fitting poses with no lay, and its builder reported them as poses the conduit grid cannot make without having checked. Owner, 2026-11-16 9:15 PM PST: "WHY DID FABLE STOP IS THERE ARE STILL 21 awkward fitting poses with no lay?! WHY DID IT STOP?" Say what they are, decide by evidence whether the game can produce them, and leave no pose the game can reach unlaid; where one cannot be reached, prove it with a permanent check.

## refs
file: src/RimMandrake/GimmeSomeSlack/Source/Core/CordLiveEnd.cs
file: src/RimMandrake/GimmeSomeSlack/Source/SelfTest/LiveEndSweepChecks.cs
file: src/RimMandrake/GimmeSomeSlack/selftest_gss_live_end_sweep.py

## verify
`python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --geometry` green with the placement family, the challenge cases and the crowding proof in it (on 6ecfb14c822b none of the three exists); `python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_live_end_sweep.py` 8 of 8 (the whole pose family, 13,248 poses); `python3 src/RimMandrake/rimflow/maturation.py certificate GimmeSomeSlack --run` exits 0. Live: `python3 src/RimMandrake/GimmeSomeSlack/northstar/live_stub_joins.py` reads liveUnlaid 0, UNRUN until the bridge is free.

## criteria
- The 21 poses are named and drawn, and each is laid or proved unreachable.
- Every fitting the grid can place beside a cut end is laid to, by the bars' own instruments, in the suite.
- No bar or check loosened; an old check that went red is explained, not edited.
