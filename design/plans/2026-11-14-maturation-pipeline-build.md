# Building the Maturation Pipeline while its design still moves

Item: `RIMMANDRAKE_BUILD_MATURATION_SPINE_WHILE_DESIGN_STILL_MOVES`. Spec: `design/specs/2026-11-13-maturation-pipeline.md`
(the spec wins wherever this plan and it disagree). Written 2026-11-14 by a detached rm-builder, offline.

The owner, 2026-11-14: *"I suspect it would be wise to start a builder on the maturation pipeline even as we develop its
components together now. Just so it's ready faster."*

The rule for this plan: build only what is **settled** (his words, his cards, or a carried ruling, as the spec marks them)
**and** already done by hand in the five hand-runs. Anything that rests on an open question is a **named hand step**: the
program stops, says what a person has to do and why, and records it when it is done. It never guesses.

Stages are named in words. The spec's numbers are kept beside the names because they are his.

| word used here | the spec's stage |
|---|---|
| intake | Intake |
| designer | Stage 1, Designer |
| preflight | Stage 2, Preflight |
| offline build | Stage 3, Offline build (for a built mod: "reconcile") |
| blind challenge | Stages 4 and 5, one stage, tests first |
| in-game acceptance | Stage 6 |
| pre-human check | Stage 7 |
| his walk | Stage 8, his live walk |
| passed | Version passed |

## 1. What already exists as programs (reuse, do not rebuild)

| program | what it does | the spine uses it for |
|---|---|---|
| `src/RimMandrake/Utils/maturation_now.py` | The status page. Reads each mod's `journal.md` ("Stage now", "Waiting on", interventions, dated history), `version/VERSION.json`, `stage.json`, `version/test_table.json`, and the detached-run records; places each mod on the map. | Its readers: `parse_journal`, `stage_from_text`, `parse_interventions`, `gather` (runs placed per stage, with tokens, wall time, dollars and cap). The spine imports them and never re-parses a journal its own way. |
| `src/RimMandrake/rimflow/designer_stage.py` and each mod's `stage.json` | The Designer's inner steps (Read to Lock), its budget charges. | Nothing new: the designer stage keeps its own record. The spine only asks "is the version locked?". |
| each mod's `version/VERSION.json` | Design Version, state (locked), bars, Designer tokens. | The lock test (designer to preflight); the version the record is for. |
| each mod's `version/test_table.json` (made by throwaway `make_test_table.py`, one schema in all four) | Bars, their deciding tests, `every_decider_runnable_today`, `offline_green_today`, `proves_at`. | The offline build exit test. |
| each mod's `version/preflight.json` (made by a throwaway preflight per mod) | Check rows, verdict, refusals, seconds. | Shown in `next`; the preflight to offline build move needs one for this version. |
| `src/RimMandrake/rimflow/refusal_contract.py` | The refusal record shape (clause, evidence, observed, would_pass, smallest_fix, criterion_verdict) and its `check`. | Every refused advance is a verdict in that shape, checked by `refusal_contract.check` before it is printed. |
| `src/RimMandrake/rimflow/detached_helper.py` | Launches a helper in its own unit, from a pool clone, with `--budget-usd` (the spend cap; default 15) and no wall-time limit. | The only way the pipeline launches work: slice 4's `maturation.py launch`, called by the Dispatch step. |
| the journal's `### Conductor interventions` lines (spec §5 item 5) | Holds, releases, re-pins, decisions, bars added. | A hold with no release on the current stage refuses every advance. |

What was retired and is not rebuilt (`design/RimMandrake/retired_loops_2026-11-13.md`): Relentless (`relentless.py`, its
tick, leases and Builder/Judge workers), the Artisan `ralph_*` loops, the Whittle loops. The spine has no tick, no lease, no
"take the next ticket", and no loop that re-runs an agent on its own.

## 2. What the hand-runs actually did (2026-11-14, read from the four journals and ledger notes)

All four advancing mods (Explosive Knockback, FlowWorks, Gimme Some Slack, Pyrelands) did the same rows by hand, each in a
detached rm-builder run:

1. **Journal started** (`design/concepts/<Mod>/journal.md`): the mod as it stands on top, the dated history below,
   `### Conductor interventions` first in the history.
2. **Designer finished by hand**: the bars turned into `version/test_table.json` (one schema in all four), the held look
   statements placed.
3. **Preflight by a throwaway program** per mod (`preflight_ek.py`, `preflight_fw.py`, `preflight_pyre.py`,
   `preflight_throwaway.py`): refusals and run time in `version/preflight.json`. Refusals counted 26, 48, 4 and 17.
4. **Offline build, as "reconcile"**: missing tests built red first, scene entries written UNRUN with their commands, the
   preflight re-run (6, 7, 2 and 0 refusals left). Each run cost about 2.8 to 4.1 million tokens (USD 5 to 11).

Between the rows the Conductor stepped in by hand: holds, releases, re-pins, decisions on his card answers, bars added.
**Nothing yet has entered the blind challenge.** So every stage after offline build is unproven by hand, and stays a hand
step in this plan.

Where each stands (journal "Stage now" lines, read by `maturation_now.py` on 2026-11-14 3:55 PM PST): all four at offline
build, "done as far as offline work can take it". Pyrelands' journal says "Stages 4-5 are next"; the other three wait on
unbuilt behaviour or a question to him.

## 3. The spine

Four things, nothing more:

1. **One record per mod version**, `design/concepts/<Mod>/version/stage_record.json`: the Design Version, the stage it is at
   and since when, every stage change (from, to, when, by whom, why, what was confirmed), the blind-challenge cycle count,
   arrivals at the pre-human check, and spend per stage (tokens, dollars, wall time, its source, measured or estimate).
   It is seeded from the files the hand-runs already wrote. **Nobody retypes state.**
2. **One command that says the next step**: `maturation.py next <Mod>`. It reads the record and the mod's files, runs the
   current stage's exit tests that are settled, names the hand steps that are not, and ends with one imperative NEXT line.
3. **One command that advances**: `maturation.py advance <Mod> --to <stage> --by <seat> --why "..."`. It refuses an
   out-of-order move, a move out of a held stage, a move whose exit tests fail, and a fourth blind cycle with no
   Conductor decision. A refusal is a refusal-contract record: what was observed, what would pass, the smallest fix.
4. **A journal entry per advance**: one dated history entry (what moved, why, what was confirmed, the "Stage now" and
   "Waiting on" lines it replaced) and a new "Stage now" line on top that `maturation_now.py` reads back to the same
   stage. Spend goes in with `maturation.py spend <Mod> --stage <stage> ...`, or is taken from the detached-run records at
   seeding.

### The moves the spine allows (all settled; spec marks in brackets)

Forward, one stage at a time only. Back, only along the roads the spec draws:

| from | back to | spec |
|---|---|---|
| preflight | designer | spec refused [CARRIED, rule 2] |
| blind challenge | blind challenge (a new blind judge: one more cycle) | [HIS] fix in place, new blind judge |
| in-game acceptance | offline build or blind challenge (the lowest stage that can show it) | [CARRIED, rules 2c, 2d] |
| pre-human check | preflight, offline build, blind challenge or in-game acceptance (the stage that made the evidence) | [CARRIED, rule 2] |
| his walk | offline build, blind challenge or in-game acceptance (a Problem) | [CARRIED] |

Which of the allowed lower stages is "the lowest that can show it" is judgment: the caller names it with `--why`.

### The exit tests, stage by stage

| leaving | tested by the program (settled) | hand step, named (and the open question that keeps it a hand step) |
|---|---|---|
| intake | Refused while no mod's record has reached his walk [HIS, card 2026-11-14, decision 8]. | After that, `--owner-said` is required: how waiting mods enter is "asked of him again at that point". |
| designer | `VERSION.json` state is locked and its version is the record's [CARRIED, Design Versions: locked on his word]. | none |
| preflight | A preflight record exists for this version. | If it refuses: `--steward-confirms` saying why the refusals left are offline-build work, not a spec fault. No common preflight program exists yet, and the throwaway ones do not mark which refusals are build work (spec build order item 3). |
| offline build | Every bar in the test table has every deciding test runnable today (`every_decider_runnable_today`), and the table is for this version [HIS by agreement, the lock rule item 3]. | "Every offline check passes" and "the builder's list of what it could not test" are shown, not enforced: both are [PROPOSAL] in the spec's Stage 3 exit row. A bar flagged not runnable that his Stage 8 look (`LOOK_STAGE8`) helps decide needs `--steward-confirms` that its other checks run: the throwaway table scripts disagree on whether that look counts (Pyrelands' leaves it out, Gimme Some Slack's counts it as never runnable). |
| blind challenge, first time | At least one cycle ran. | `--steward-confirms` naming the blind judge's run and verdict: the exit ("every offline bar green, the judge found no Problem") is [PROPOSAL], and no verdict file format exists yet. |
| blind challenge, a 4th cycle | Refused without `--conductor-decision`, which is written as a `CONDUCTOR INTERVENED (stage 4+5, ..., kind decision)` line [HIS, 2026-11-13: "a fourth judge never starts on its own"]. | The decision itself is the Conductor's. Whether a road back from in-game acceptance restarts the count is not ruled; the spine counts per visit and keeps a total. |
| in-game acceptance | none | `--steward-confirms`: no common row format for in-game verdicts exists across mods. |
| pre-human check | Arrivals here are counted (rc.N if open question 13 goes as recommended; the spine says "arrival N", not rc). | `--steward-confirms` naming the fresh reader's verdict. |
| his walk | `--owner-said` is required: "the pass is his alone" [CARRIED]. | The pass record (date, commit, bars, evidence, cost, cycles) is written by hand until the second hand-run says its shape. |
| any stage | Refused while a `kind hold` intervention on this stage has no later `kind release` [RULE, Conductor 2026-11-14, spec §5 item 5]. Refused when the record's version is not `VERSION.json`'s. | none |

### Which stages a program can launch, and which stay hand steps

Launching is slice 4, only through `detached_helper.py launch ... --budget-usd <cap>`.

| stage | launchable by program? | why |
|---|---|---|
| intake | no | Closed by his card until a mod reaches his walk; then it is his question again. |
| designer | no | Arguing with him. The Designer's Exam and coverage judge as gates are open question 7. |
| preflight | partly: the program can run each mod's own throwaway preflight (its path is in `preflight.json`) | A common preflight is spec build order item 3, not yet built. Running costs no tokens, so no cap is needed. |
| offline build | **yes, and it does** [HIS, 2026-11-14 ~9 PM PST]: `maturation_dispatch.py` on `rm-maturation-dispatch.timer` launches one capped builder per mod with build work owed | "So can we wire up Operations/Dispatch such that they do advance on these offline builders? This was pretty inefficient and pointlessly it seems, if I'm reading correctly. As long as we don't have automated loops rejecting/cycling things, we can't get into too much trouble." The program writes the mechanical half of the brief; the Conductor's decisions, when he writes them, go in `version/steward_decisions.md`, and a blank one is a standing default, never a refusal. Guard rails in Slice 4. |
| blind challenge | not yet | Nothing has gone through it by hand. The blind judge's inputs per part are [PROPOSAL]; its verdict format is unwritten. Open questions: what the next judge reads is decided ("All once, then changes"), but the record of "changed files and line items whose inputs changed" is not built. |
| in-game acceptance | no | A live game; Dispatch's game-sharing between mods is not designed; flyers never without him. |
| pre-human check | no | Nothing reached it by hand. |
| his walk | never | His. |

## 4. Slices, in build order

Each slice lands with its offline selftest written at the same time, seen failing before the code and passing after.
Only slice 4 starts helpers on its own, offline builders under its guard rails. Whittle and Relentless stay off.

### Slice 1: the record, `next`, `advance`, `spend`, seeding (this item)

`src/RimMandrake/rimflow/maturation.py` with `seed`, `show`, `next`, `advance`, `spend`. Seeds the four advancing mods
(and Pyrelands Mechanics, held at intake) from their journals, `VERSION.json` and the detached-run records; writes
`version/stage_record.json`; refuses out-of-order moves with refusal-contract records; writes the journal entry per move.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation.py` (exit 0; every check prints PASS).
It covers: seeding from a copy of each real journal lands at the stage `maturation_now.py` reads; a re-seed changes
nothing; an out-of-order move, a held stage, a version mismatch, failing exit tests and a 4th cycle are refused with a
record `refusal_contract.check` accepts; a good move writes the record, one history entry and a "Stage now" line that
`maturation_now.stage_from_text` reads back to the new stage; spend totals per stage; nothing outside the temp tree is
written.

### Slice 2: the status page reads the record

`maturation_now.py` reads `version/stage_record.json` first for the stage, its time and the cycle count, and the journal
only when no record exists; a disagreement between the two goes in "files that disagree". Advance refusals go through
`refusal_contract.submit`, so a stage refused again and again raises `REFUSAL_NOTHING_COULD_EVER_PASS` instead of
looping.

Acceptance test: `python3 src/RimMandrake/Utils/selftest_maturation_now.py` gains a case where the record and the journal
disagree, and `python3 src/RimMandrake/rimflow/selftest_maturation.py --submit` with `RM_REFUSAL_DIR` in a temp dir.

### Slice 3: a common preflight for a mod version

Grown from the four throwaway preflights (`design/concepts/*/version/preflight*.py` and `version/advance_scripts/`):
one program, one row format, each refusal tagged "offline-build work" or "spec fault". Then the preflight exit test
in the spine becomes "no spec-fault refusal", and the `--steward-confirms` hand step there goes away.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_mod_preflight.py`: run on copies of the four mods it gives
the same refusal ids as each mod's recorded `preflight.json` (measured on the base), and planted faults (a missing def,
a bar with no test, an unplaced held statement) are each refused.

### Slice 4: the offline-build brief, capped launch, and the Dispatch step (built 2026-11-14)

[HIS, 2026-11-14 ~9 PM PST] "So can we wire up Operations/Dispatch such that they do advance on these offline builders? This was pretty inefficient and pointlessly it seems, if I'm reading correctly. As long as we don't have automated loops rejecting/cycling things, we can't get into too much trouble."

`maturation.py brief <Mod>` writes the mechanical half of an offline-build brief: mod and version, the refused exit tests,
the bars not runnable with each decider that does not run, the in-game checks that stay UNRUN, the journal's Waiting on
and Next lines, the standing rules a builder needs. The "Steward's decisions" section is `version/steward_decisions.md`
when the Conductor writes one, else a standing default; a blank one does not refuse. `maturation.py launch <Mod>
--budget-usd <cap> --item <ID>` calls `detached_helper.py launch` (cap required, no default; only a mod at the offline
build with build work owed).

`src/RimMandrake/rimflow/maturation_dispatch.py tick --apply` on `rm-maturation-dispatch.timer` (every 60 s, from the
dispatch clone; settings `maturation_dispatch.json`) decides per advancing mod: launch one builder (opus, USD 15; the
item is spawned under RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE as RUNNER, the way ops_watch files,
and published first) when the mod stands at the offline build, its refusals are build work, and no detached run is live
on it. Guard rails: one live builder per mod, at most 2 live on advancing mods (the Conductor's own included); after a
run ends the next starts only if the count of refused bars fell, otherwise, or past USD 60 measured at the stage, or on
a failed launch, it stops on that mod with one "Needs Conductor" line and never tries the same refusals again
(`maturation_dispatch.py clear <Mod> --why` is the Conductor's lift); a hold, a version mismatch, a hand step or any
other stage launches nothing; every exit test passing writes "ready to advance". It never judges, rejects, sends a mod
back or advances it, and never takes the bridge or a game. The Dispatcher's account pick holds it the way it holds a role
launch. Each tick writes `<RM_DISPATCHER_STATE>/maturation/reading.json` and regenerates MATURATION_NOW, whose "Needs
Conductor" list carries the step's lines; ops_watch's `maturation` family reads the reading, and
`OPS_MATURATION_IDLE_ADVANCING_MOD` alarms when a mod at the offline build has had work owed with nothing running on it
for over 60 min.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation.py --launch` (fake `detached_helper`: no cap, a
zero or negative cap, no item, a mod at intake, a mod with no build work refuse; a good one passes cap, model, item and
seat through) and `python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py` (one launch for a mod with build
work and none live; nothing when one is live, when the last run did not reduce the refusals, with no cap, off the list,
at another stage, on a hold, past the ceiling or max_live, on an account hold, in a dry pass; a reducing run lets the
next start; a failed launch is not retried; the idle reading fires on a planted idle mod and ops_watch reads it).

### Not planned yet (waits for a hand-run)

The blind challenge (no mod has entered it), in-game acceptance with Dispatch sharing the two games, the pre-human check,
the pass record. Each gets a slice after one mod has gone through it by hand and its journal says what was boring.

**Spec §8, decision 18 (his card, 2026-11-14):** the entry rule is built (the queue admits only a locked bar's check from a mod version past Stages 4 and 5: `src/RimMandrake/Utils/testq/pipeline_admit.py`). Still to plan, in the Stage 6 slice: a job that writes one line item's in-game verdict to the mod's record on whichever game is free, with the version-and-list check of spec §4 Stage 6. Re-running a passed version on change is planned only after one version has passed.

## 5. The open questions that most block automation, ranked

1. **The blind challenge's verdict format and inputs** (spec Stages 4 and 5 "Order" and "Exit" rows are [PROPOSAL]): no
   mod has entered it, so nothing after offline build can be tested by a program.
2. **A common preflight that tags refusals as build work or spec faults** (spec build order item 3): until it exists the
   preflight exit needs the steward's word.
3. **What "every bar has a check that runs" means for one table schema** ([PROPOSAL] in the Stage 3 exit row for
   "passes"): whether every offline check must also pass, and whether his Stage 8 look counts as a check that must run.
   One common `make_test_table` would settle the second; today it is a hand step.
4. **Does a road back from in-game acceptance reset the three-cycle count?** Not ruled; the spine counts per visit.
5. **What counts as a release candidate** (open question 13): the spine counts arrivals at the pre-human check only.
6. **Dispatch's sharing of the two games** between mods at in-game acceptance: not designed.
