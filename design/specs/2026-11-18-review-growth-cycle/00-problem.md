# Why the Codex review count rose on the control store: the timeline, read claim by claim

Written by the Conductor (Fable) on 2026-11-18 at 8:28 PM PST, on the owner's order: *"I think you, as Fable, need to
now look DEEPLY at some of these timelines to see 'are the fixes being introduced by sloppy coders, or is it indeed an
ever-growing spec/input domain that's improperly bounded?' Then we design the relevant fix."* This file is the problem
statement for that design. Nothing here is a ruling.

## The timeline (all 2026-11-18, Pacific; from `git log` on `src/RimMandrake/rimflow/control.py`) [measured]

| time | event |
|---|---|
| 10:51 to 11:01 AM | the design is written (`design/specs/2026-11-18-pipeline-control-surface/`): a comparison of architectures with a recommendation |
| 11:53 AM | first commit of `control.py`, 1,823 lines |
| 12:54 PM | every systemd launch site in the pipeline is routed through it: it is live for all runs one hour after it first existed |
| about 4:20 PM | review round one: 8 claims, 7 fixed at 5:30 PM |
| about 5:55 PM | round two: 9 claims, fixed 6:33 PM (+416 / -96 lines with its test file) |
| about 6:50 PM | round three: 11 claims, fixed 7:15 PM (+367 / -58) |
| about 7:35 PM | round four: 15 claims (Codex itself marks 8 as in the lines the last fix wrote, 7 as outside); 5 fixed, 10 untested |
| 8:24 PM | the owner stops the cycle |

21 commits to the file in 8 hours 20 minutes. It grew from 1,823 to 2,789 lines.

## The 43 claims, sorted by what they are about

Sorted by the Conductor from the four round tickets' claim lists (`RIMMANDRAKE_SPLIT_CONTROL_STORE_REVIEW_CLAIMS_EIGHT_UNTRIED`
and the `..._ROUND_TWO_NINE_`, `..._ROUND_THREE_ELEVEN_`, `..._ROUND_FOUR_FIFTEEN_` tickets). The sorting is a reading of
claim text, [guess ~80%] per claim; the two git facts below are measured.

**Group one: holes in the run's life cycle (20 of 43).** Four chains, each about one small state machine, each
continuing round after round:

| chain | what it is | claims by round (1, 2, 3, 4) |
|---|---|---|
| "is this process group dead?" | verifying a kill by reading the cgroup | 1, 1, 2, 1 |
| a run's identity | what names one admission of one run | 2, 1, 1, 0 |
| stopping while the store is locked, and replaying a stop | | 0, 2, 2, 0 |
| two stop orders or two deadlines on one run | timers, reaping, escalation | 1, 1, 3, 2 |

In these chains round N+1 faults the code round N wrote. Measured example: round three's claim that an unreadable
re-read of the cgroup counts as verified death is about the line `(_procs(cg) or [])`, which the round-two fix
`be673ed895` added and which did not exist before it.

**Group two: inputs and tooling nobody bounded (13 of 43).**

| thread | what it is | claims by round |
|---|---|---|
| parsing a `systemd-run` command line | payload arguments read as options, option forms such as `-uNAME`, `--on-timezone-change` | 0, 1, 1, 2 |
| the census that checks our own code routes launches through the store | alias tracking, annotated assignments, a builder inside a builder | 0, 1, 1, 2 |
| paths with spaces or `${...}` in hook commands | round one called this "polish, not a flaw unless a real clone path holds a space"; round three filed it as a defect | 0, 0, 1, 1 |
| how strict the tests are | | 0, 1, 0, 2 |

Measured: the option parser faulted in round four (`_sr_unit`) did not exist until the round-three fix `53cb713db1`
wrote it to answer a round-three claim. The store has 9 launch call sites in 9 files, all written by us in one form.

**Group three: one-off defects (10 of 43)**, several plainly real: `pipe off` saying "no run is live" when it could not
read the runs; the health check reporting OK on a failed check; a run id matched by substring (`rm-probe-1` inside
`rm-probe-10`); a new owner hold with different words not imported after a lift.

**Per round:**

| round | claims | life-cycle chains | unbounded inputs and tooling | one-offs |
|---|---|---|---|---|
| one | 8 | 4 | 0 | 4 |
| two | 9 | 5 | 3 | 1 |
| three | 11 | 8 | 3 | 0 |
| four | 15 | 3 | 7 | 5 |

## What the timeline says

1. **Both readings are true, in sequence.** Rounds two and three rose mostly because fixes left or opened holes in the
   life-cycle chains. Round four rose mostly because the review moved outward into inputs and tooling nobody had
   bounded, while the chains were finally shrinking (8 down to 3).
2. **The fixes were patches, not careless code.** Each fixed the named case and added a branch with its own failure
   paths. One class of mistake recurred at least five times across the rounds: "could not look" read as "nothing
   there" (round one claim 1, round three claim 4, round four claims 4, 11 and 12). That is the estate's own most
   expensive known bug class, and no fix applied it as a rule to the whole file.
3. **The root is one thing: nothing says where the store stops.** The design document chose an architecture. It does
   not list the states a run can be in and the legal moves between them, the failures the store promises to survive
   and the ones it does not, or the forms of input it accepts. (A search of the merged design for "state machine",
   "transition", "out of scope" and "non-goal" finds nothing; the design was not re-read in full for this note.)
   Without that, every reproducible case is in scope, a reviewer can always find one more, and a builder has no
   ground to decline.
4. **The build order made it worse.** A new store that kills processes, locks a database and sets timers went live for
   every run one hour after its first commit, and its design was then completed by review, one case at a time, in
   production, by several runs editing the same file.

## The second reading, by line author (an Opus analyst, 8:35 PM PST)

Report: `D:\ClaudeWork\rimmandrake\conductor\control_review_rounds_real_or_treadmill_20261118.md`. Line authorship is
measured by git; problem-or-polish is the analyst's judgment, its own confidence about 70%; it ran no probes.

| round | claims | problem | polish | about old code | a fix missed a case | a fix added the fault |
|---|---|---|---|---|---|---|
| two | 9 | 2 | 7 | 9 | 0 | 0 |
| three | 11 | 0 | 11 | 3 | 6 | 2 |
| four | 15 | 2 | 13 | 6 | 7 | 2 |

- **The count was not rising.** Round two's review made 15 claims; the ticket's "nine" counted only those about old
  code, and the six about the round-one fix were fixed separately (dd34dd9e36). Counted one way the series is 15, 11,
  15. The "9, 11, 15" in the round-four ticket and in the Conductor's earlier messages compared unlike counts.
- **Real problems stayed flat and mild: 2, 0, 2**, all fixed. All four faults that a fix added are polish.
- **No claim is about tonight's feature code.** Lines written by a review fix draw 14 to 25 claims per 1,000 lines;
  old code draws about 3. Most say a fix missed an edge case or a test could be stricter.
- The two readings agree on the mechanism: from round three on, most claims (8 of 11, then 9 of 15) are about the
  previous round's fix. They differ on weight: the Conductor's sorting above counts the life-cycle chains as real
  holes; the analyst judges nearly all of them unreachable on an ordinary day.

So by the owner's own test (a constant count with a high polish share means the filter goes in), the control store
met the condition before he stopped the cycle.

## Not yet known

- Whether the same pattern holds on the other files reviewed tonight (coverage judge, publish tool, cutover check).
  Only the control store was read claim by claim here.
- Which of the 43 an ordinary day actually reaches. A separate analyst is tracing each faulted line to its author
  (old code, a review fix, or tonight's feature work): `D:\ClaudeWork\rimmandrake\conductor\control_review_rounds_real_or_treadmill_20261118.md`.
