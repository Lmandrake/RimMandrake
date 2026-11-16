# Cheap guards at every door (spec, 2026-11-15; nothing here is built)

Item `RIMMANDRAKE_GUARD_PIPELINE_DOORS_CHEAPLY_NO_CEREMONY`. Findings for the owner, two screens:
`D:\ClaudeWork\rimmandrake\conductor\cheap_guards_findings_20261115.md`.

## 1. The order

The owner, 2026-11-15 about 5:10 PM PST: *"Every place we can put a deterministic check to ensure a work item is
properly formed and has the right number and format of inputs, checks, etc. we should have one. Then a light LLM should
scan for the required inputs before any expensive context is loaded, ok? Please review this suggestion at any point in
the pipeline. Let's eliminate this "oops... I spent a $1M tokens on a poorly formulated request because the human
answered a question card." Seriously... this needs to be gone. Do whatever design you need, Fable-level, to leverage
approaches like this to knock out nonsense right now. Tell me what you find, then get this done. I don't mean to create
needless ceremony (and please don't!) Each element must defend precisely what it's protecting against and have evidence
that it actually happens... but when it has... protect cheaply!"*

Earlier the same sitting: *"how do we certify then that it has all the tests needed to pass before we throw it to
judgement? ... No reason to send it in knowing it will fail, right?"*

The rules this spec holds itself to, from the Conductor's brief: a program checks first, at zero model tokens; a light
model scan only where a program cannot judge; every guard names what it protects against and cites a real incident with
its cost; a guard with no incident is not built; a refusal carries evidence, `would_pass` and `smallest_fix`; a guard
that cannot run says "did not run" and lets the work through; every guard is watched rejecting a broken input and is
backtested against the incidents it cites.

## 2. What was measured

Sources, all read on 2026-11-15: the 289 detached-run records in `D:\ClaudeWork\rimmandrake\dispatcher\detached`
(2026-11-01 to 11-15), the 282 run-ended lines of the Conductor log (tokens for 270 runs), the 99 readable Designer run
records in `D:\ClaudeWork\rimmandrake\dispatcher\roles` (2026-11-04 to 11-15, USD 161.59 `[measured]`), every
`design/concepts/*/stage.json` and `version/run_spend.jsonl`, the interventions census
(`design/RimMandrake/pipeline_interventions_census_2026-11-15.md`), the GPT review's checked claims and the Codex second
opinion on the coverage judge. Working tables: `D:\ClaudeWork\rimmandrake\scratch\cheap_guards\`.

Two limits on every dollar below. Only 97 of the 289 detached runs carry dollars (USD 524.38 `[measured]`); the result
files of the rest were written over, though their tokens survive in the log. Where a row says ESTIMATE it is measured
tokens times USD 2.86 per million, the median of the 38 runs that have both numbers (range 1.57 to 15.45).

| Waste class (the malformed input) | Times | Cost | Where it could have stopped | State |
|---|---|---|---|---|
| A Designer run ended with a result a program rejects: no `result.json` (8), a cited file "missing" that origin/main held (4), other form faults (4) | 16 | 2.31M tokens on the 6 measured runs (about USD 6.6 ESTIMATE) plus USD 3.06 of retry runs `[measured]`; 6 runs UNMEASURED | Inside the run, before it ends (the run is still warm) | NEW: Result before exit |
| A steward run was launched to make a move whose own gate, a program, refuses it (Pyrelands advance on a stale flag; Graffiti advance; Pyrelands exam; Knockback re-certify; a coverage judge parked at its ceiling) | 5 | USD 4.56 `[measured]` plus 0.88M tokens (about USD 2.5 ESTIMATE) | At launch, by running that gate first | NEW: Gate first. The Pyrelands flag itself is fixed (`79483e1558`) |
| A fixer was launched for a red test that was already green on origin/main | 8 | 1.38M tokens (about USD 3.8 ESTIMATE; USD 0.29 `[measured]` on one) | At launch, by running the test | NEW: Gate first. The nightly's own route is fixed (`55fdc9d72f`) |
| A blind judge was sent in while a deciding offline test was red (Explosive Knockback cycle 1: `inv_proof_scenes`; Gimme Some Slack cycle 2: two deciding tests the judge found red on a plain rerun) | 2 | 3.42M tokens (about USD 9.8 ESTIMATE) for the first; part of USD 7.95 `[measured]` for the second | Before the judge is launched | NEW: Pre-judgement certificate |
| An in-game visit drove scenes that could not ask their question: FlowWorks visit 1 read 12 of 31 checks UNMEASURED; three rows passed on nothing; Pyrelands 4 of 39; Knockback 5 of 56 | 3 visits | About USD 12.6 ESTIMATE (each visit's cost times its unmeasured share; FlowWorks' USD 21.68 is `[measured]`) | Before the bridge is taken | NEW: Scenes can ask |
| A Designer run at stage 5 only carried a program's answer: "the judge refused, back to stage 3" (7) or "the judge signed, lock" (3) | 10 | USD 8.39 `[measured]` | No run at all | NEW: Stage five by program |
| The exam was retaken after each coverage refusal, though the exam passes and the coverage judge refuses | 6 | USD 18.79 `[measured]` | Stage order | A DECISION, not a guard (section 7) |
| One builder was given 33 bars; it ended waiting on helpers that died with it | 1 | USD 12.88 `[measured]` (the run, the steward, the restore) | Dispatch sizing | IN FLIGHT: `RIMMANDRAKE_SIZE_DISPATCH_BUILDS_THIRTY_THREE_BARS_ONE_RUN` |
| A card's picked option said "needs bigger art"; the brief carried only the label | 1 | USD 3.16 `[measured]` (the run that did half the card) | Card to brief | BUILT today: `card_capture.py`, launch and close refusals |
| A judge's brief and the pipeline's reader disagreed on what "exit met" means | 4 | 5.37M tokens (about USD 15.4 ESTIMATE) plus USD 1.14 `[measured]` | Brief generator | BUILT today (`c269d7039e`, `228cb916de`) |
| A run was launched into a broken place: its clone deleted under it (2), or killed and relaunched within six minutes (7) | 9 | USD 6.79 `[measured]` on four; the rest UNMEASURED | Launch | Clone: BUILT. Kill-and-relaunch: reason never recorded, see section 6 |

**Total: about USD 111 over two weeks, a lower bound** (USD 67 measured, USD 44 estimated from measured tokens).
About USD 34 of it is already fixed or being fixed today. The four new program guards would have stopped about USD 38.
The stage-order decision is worth USD 19. The in-game class (USD 13) is caught in part: how much is UNMEASURED.

Beside that, not counted as waste but exposed to it: the coverage judge has looked 14 times on record and signed three times;
its looks cost 16.7M tokens (about USD 48 ESTIMATE); its brief has never been calibrated
(`judge_calibration.json`: coverage_judge UNTESTED, read by the builder of `RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS`),
and the one round an independent reader audited held 4 noise gaps in 18.

## 3. Doors and guards

One row per door where a model is started. "Built" means the code was read today; "written" means a spec or an open
item and no code.

| Door | Built today | Written, not built | New here |
|---|---|---|---|
| Card answer becomes work | The whole card is stored and stamped on the event; a brief must carry the picked option's description; `close` wants every "needs X" accounted for (`card_capture.py`, `detached_helper.card_refusal`) | A certificate bound to what he saw: `RIMMANDRAKE_BIND_CERTIFICATE_TO_WHAT_HE_SAW`, `RIMMANDRAKE_CARRY_OWNER_CERTIFICATE_THROUGH_HIS_OWN_CARD_EDIT` | Nothing |
| Ticket filed, claimed, started | Name check, thin-ticket lines, proof lint at filing | The 2026-11-12 preflight, three filed tickets, none built | Nothing; section 8 says what stands |
| Helper launch (`detached_helper.launch`) | Refuses an unknown item, one not on origin/main, a bad model, an empty brief, a card brief without the card's words, a held clone | The preflight's shadow run at this door | **Gate first** |
| Designer stage run (`role_launch`, `designer_stage`) | The stage machine validates `result.json` after the run; a per-stage input manifest; the pre-launch coverage judge | Nothing | **Result before exit**, **Stage five by program** |
| Coverage judge look (`coverage_judge.py`) | Spend stop per run; delta looks; late gaps need a reason; a malformed verdict re-asks only its broken rows; a release is spent only after the fixes close | Calibration both ways: `RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS`; stale inputs: `RIMMANDRAKE_REVALIDATE_INPUTS_BEFORE_REFUSAL_STALE_THIRD_STRIKE` | Nothing new; calibration moves up the order |
| Builder launch (Dispatch tick) | Capped runs; no second automatic try; a steward reads a builder that resolved nothing | Run sizing, in flight | Nothing |
| Advance to the blind challenge (`maturation.evaluate`) | Every bar has a registered check with no owed scene parts (`79483e1558`); table version | An advance bound to the exit reading: `RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS` | **Pre-judgement certificate** |
| Blind judge launch | Fixers before the next cycle; a launch that never started is not a spent cycle; the brief agrees with the reader | Nothing | **Pre-judgement certificate**, read by the tick before it launches |
| In-game visit, testq submit | testq preflight (stale swap marker, stale DLL, missing proof line; `selftest_preflight.py`); `selftest_bridge_args.py`; a visit's rows must name one build | Evidence bound to one build: `RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD` | **Scenes can ask**, then the one **light scan** |
| Showing him (Stages 7 and 8) | "Nothing reaches the owner unread" | Stage 7 itself (same item) | Nothing: no incident yet, so no guard |

### 3.1 Result before exit

- **Protects against:** a Designer run that ends without a `result.json` the stage machine accepts, so the whole run is
  rejected after it is paid for.
- **Evidence:** 16 rejected stage runs in eleven days `[measured, each concept's stage.json]`. Eight read "no
  result.json (a closing message is not a result)". Four read "source path ... does not exist" for a file origin/main
  held (the retry runs say so in their own words, twice); each was followed by a paid retry (USD 0.99, 0.79, 1.28).
- **The guard:** a Stop hook on stage-machine runs runs `designer_stage.py check <folder>`, the check the launcher will
  run anyway. If it fails, the run is told why and gets up to two more turns to write the result, while its context is
  still loaded. And `source_errors` asks origin/main before calling a cited path missing.
- **Its cost:** one program call of a second or two; a blocked stop costs the run one short turn.
- **Cannot run:** the hook lets the run end and says "did not run"; after two blocks it lets go.
- **Backtest:** catches the 8 no-result runs and the path rejections that origin held (2 confirmed, 2 probable); does
  not catch the 4 other form faults (wrong stage number, an owner event not found, two unsigned locks).
- **Ticket:** `RIMMANDRAKE_CHECK_DESIGNER_RESULT_BEFORE_EXIT_EIGHT_REJECTED`.

### 3.2 Gate first

- **Protects against:** a paid run whose first act is to run a program that tells it to stop.
- **Evidence:** five steward runs (Pyrelands advance, USD 2.76 `[measured]`: "I did not advance Pyrelands"; Graffiti
  advance, 307,402 tokens: "the move can't pass"; Pyrelands exam, USD 1.80: "the stage machine refuses to open them";
  Knockback re-certify, 255,598 tokens: "certify refused"; a coverage judge that "did not run", 321,409 tokens). And
  eight fixers whose red test already passed on origin/main (seven nightly fix items and one "chunk 3 is already on
  main", 1.38M tokens).
- **The guard:** an item may carry a `## launch-checks` section: `must-pass: <command>` and `must-fail: <command>`.
  `detached_helper.launch` runs them in the run's clone before the unit starts. A `must-pass` that fails refuses the
  launch with the command's own output; a `must-fail` that passes refuses it as "already passes: close or re-scope".
  The programs that file steward and fixer items write the lines themselves (`launch_checks.block_for`), and
  `maturation.py gate <Mod> --to <stage>` is the read-only command an advance uses. Only a declared line can refuse,
  the same rule as the 2026-11-12 preflight.
- **Its cost:** the commands' own run time, capped at 120 s each; zero tokens.
- **Cannot run:** exit 126 or 127, a timeout or an unknown line reads "launch check did not run" and the launch goes
  ahead. The Conductor's bypass is `--skip-launch-checks "<why>"`, recorded on the run.
- **Backtest:** in all five steward runs the thing that refused was a program the run itself called. The ticket builds
  the read-only verb for an advance (two of the five); the exam, certify and judge filers add their line when their
  gate's read-only form is confirmed, so those three are caught only then. Seven of the eight fixers named their test;
  the eighth had no command and is not caught.
- **Ticket:** `RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES`.

### 3.3 Stage five by program

- **Protects against:** paying a Designer run to write down what a program already knows.
- **Evidence:** ten runs, USD 8.39 `[measured]`: seven that ended "no lock: the coverage judge returned not_covered,
  all gaps return to stage 3" (USD 0.55 to 1.00 each) and three that ended "locked" after a signed verdict (USD 0.73
  to 1.29).
- **The guard:** after the pre-launch judge, `designer_stage.program_result` writes the `result.json` such a run would
  have written, and the launcher closes it through the same `close_run` every Designer result passes. A gap that
  returns anywhere but stage 3, an unsigned or malformed verdict, or a verdict on another tree needs a Designer, as
  today.
- **Its cost:** none; it removes a run.
- **Cannot run:** if `close_run` rejects the program's result, the Designer is launched as today.
- **Backtest:** all ten, by their own summaries.
- **Ticket:** `RIMMANDRAKE_CARRY_STAGE_FIVE_BY_PROGRAM_TEN_RELAY_RUNS`.

### 3.4 Scenes can ask

- **Protects against:** taking the bridge and an Opus driver into a visit whose scenes stop, or pass, with nothing to
  test.
- **Evidence:** FlowWorks visit 1 (USD 21.68 `[measured]`): 12 of 31 checks UNMEASURED, "several drafts had passed with
  nothing on the map to test". A 25-line prototype of the second part, run today on that visit's scene file (commit
  `99ff70d91a`), finds three rows that read PASS when every bridge call answers a bare success, and one such row is
  still there on today's main (`SRC_flow_stops_when_empty`) `[measured]`. And today, `maturation.py next Graffiti`
  counts 45 of 47 bars runnable while `Graffiti/validation.py` holds scenes that stop at "MISSING TOOL" for six open
  probe tickets, and `scenes.json` declares none of them `[measured]`.
- **The guard, part 1:** a scene that can reach a `raise ... "MISSING TOOL"` must declare its `owed_parts_item` in
  `scenes.json`; an undeclared one, or one whose item closed while the raise remains, makes its bars not runnable.
  It reuses the owed-parts reading built in `79483e1558`.
- **The guard, part 2:** every scene is run against an empty game (each tool answers "done" and returns no data). A row
  that reads PASS there is vacuous, and its bar is refused at the in-game door.
- **Its cost:** part 1 parses one file; part 2 ran 17 scenes in a few seconds. Zero tokens.
- **Cannot run:** an unparseable file or a harness with no adapter is "did not run" and refuses nothing.
- **Backtest:** part 2 finds the three vacuous FlowWorks rows; it does not find the coating scene that passed with no
  coat, nor the switch test that never switched (both answer correctly on an empty game and wrongly on a real one).
  Those two are what the light scan is for. Which of the 21 UNMEASURED visit rows part 1 would have caught is
  UNMEASURED: the visit records do not split tool faults from site faults.
- **Tickets:** `RIMMANDRAKE_REFUSE_MISSING_TOOL_SCENES_GRAFFITI_READS_READY`,
  `RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED`.

## 4. The pre-judgement certificate

His question, answered as a program. No blind judge and no in-game driver is launched on a mod until
`maturation.py certificate <Mod>` has read, for every bar, every offline test that decides it:

| Clause | What the program reads | Refusal's path to pass |
|---|---|---|
| `registered` | The decider is in the test table with a file that exists and a command; no scene part is owed (the reading built today) | Build the check, or work the owed item |
| `ran_on_this_build` | The recorded run carries a hash of the content of the files the test reads and of the test itself, and that hash is the hash now | `maturation.py certificate <Mod> --run`: the program reruns the offline deciders and stamps them. No tokens |
| `green` | Exit code 0, result PASS, no known-red mark | Fix the mod or the test; the refusal quotes the test's last line |
| `red_seen` | The test has been seen to fail: a planted fault (a patch the program applies, runs and reverses) recorded against the test file as it is now | `maturation.py red-seen <Mod> <TEST> --patch <file>`: seconds, no tokens |

- **Protects against:** judging a mod that a program can already see will not pass, and trusting a test that cannot fail.
- **Evidence:** Explosive Knockback's first blind cycle ended not met because the offline bar `inv_proof_scenes` was red
  when the judge went in (3.42M tokens). Gimme Some Slack's second judge found two deciding tests red on a plain rerun
  (`T_STATICS_CENSUS`, and `T_CORE` failing 3 of 3 runs); that they were red when it went in is `[guess ~80%]`. Pyrelands was sent to advance with 28 of 42 bars not runnable
  because a stored flag said yes (USD 2.76). For `red_seen`: a judge found a Knockback proof gate where "an OR passed
  green", and ten of one judge's planted faults were weakenings of test files that nothing could catch.
- **`red_seen` without ceremony:** it refuses only for a deciding test that is new or edited after the guard lands. Tests
  that exist today are listed once as grandfathered and read "UNPROVEN (grandfathered)" in the certificate's output,
  with their count. No backfill run is ordered. Every builder already shows its test failing first; this records it.
- **Its cost:** reading: under a second. `--run`: the tests' own time (Pyrelands' fuzz 14.5 s; the slowest
  selftest seen in today's runs took 138 s). Zero tokens.
- **Cannot run:** an unreadable test table is "did not run"; the mod goes through and the line is on the status page.
- **Where it sits:** one more clause, `judge_certificate`, in `maturation.evaluate` for the move into the blind challenge
  and the move into the in-game stage, and the Dispatch tick reads it before each judge or visit launch (a mod can go red
  between cycles). For an in-game visit it adds the empty-game clause of section 3.4.
- **Backtest:** refuses Knockback cycle 1 and the two red tests of Gimme Some Slack cycle 2; the Pyrelands flag is
  already refused by `79483e1558`. It does not catch the five test gaps the second and third Gimme Some Slack judges
  found by planting faults a recorded red proof would not have included: a certificate proves a test can fail, not
  that it fails on every fault.
- **Relation to open items:** `RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD` should use the same content hash
  (`judge_certificate.build_id`) for its mod-source part. `RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS` is the other end
  of the same stage: the certificate guards the way in, that item guards the way out.
- **Tickets:** `RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN`, then
  `RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN`.

## 5. The light scan

After every program check above, one place is left where only a reader can tell: **does this scene ask its bar's
question?** FlowWorks visit 1 had a coating scene that passed with no coat ever seen, and a switch test that never
switched the engine off; both run cleanly and answer honestly on an empty game. That is the evidence, and it is one
visit, so this is built last and as an experiment with a stated end.

- **The scan** (`light_scan.py`, one function, reusable at another door only when that door brings its own incident):
  Sonnet (Haiku is banned here); its input is the bar's words and the scene's own function text and nothing else; no
  tools and no file access; a fixed question list in a JSON file; input over 60,000 characters does not run, it is
  never cut; a hard `--max-budget-usd` of 0.25 per scan; the answer is a fixed JSON shape or the scan "did not run".
- **Its output:** a refusal record. A "no" must cite a line of the given input, and carries `would_pass` and
  `smallest_fix`. "Cannot tell" refuses nothing.
- **Its cost:** about USD 1 per mod per visit ESTIMATE (31 scenes of a few thousand tokens), against a visit of USD 20.
- **Kept only if** its backtest, run once by the builder on the two known-bad scenes at `99ff70d91a` and three honest
  scenes of today, flags both bad ones and at most one good one. Otherwise the ticket closes as "tried, not kept" and
  the module is deleted.
- **Ticket:** `RIMMANDRAKE_SCAN_SCENES_AGAINST_BARS_TOGGLE_NEVER_TOGGLED`.

## 6. Considered, rejected

| Idea | Why not |
|---|---|
| A light-model scan of every launch brief | 125 detached launches on 2026-11-15 alone; at USD 0.02 or more each that is USD 2.50 a day. The matching waste is 7 kill-and-relaunch pairs in two weeks, USD 5.45 `[measured]` on two of them, and nobody recorded why any was killed. It would cost more than it has been shown to stop |
| A light-model check that a brief honours its card | The one incident (the furnace-beast's art) is covered by the verbatim rule built today. No second incident |
| A light-model triage of coverage gaps before the fix run | The cure is a calibrated judge, already ticketed. A second model reading the first one's output is ceremony |
| A program that plants faults across a mod before each blind judge | It would have caught more (judges catch 16 of 21 to 41 of 50 by planting), but there is no cheap general mutator; it is a project, not a guard |
| Red proof for every test that exists today | About 80 offline tests to backfill, one probable incident. Grandfathered instead (section 4) |
| A model-id probe at launch | One incident (a run that sat 1071 s on an unrecognised model id); its cost is UNMEASURED |
| A required reason on every kill | Bookkeeping with no cost evidence. Named under UNMEASURED so the next kill is at least noticed |
| Binding every card to the state it was asked on | Two incidents (a card relayed five days late; a Designer asking about gaps a later judge had replaced), cost UNMEASURED. Certificates get it through their own item; other cards wait for a measured case |
| A guard at Stage 7 or his walk | No mod has reached either. No incident, no guard |
| A new "stage preflight" framework | Every guard here is a few functions in a door that already refuses things. A framework would be the ceremony |
| Refusing a thin ticket at filing | His 2026-08-21 ruling: a missing field is not a rejection. The preflight spec keeps filing as warn-only |

## 7. One decision that is not a guard

The Designer takes its exam (stage 4) before the coverage judge looks (stage 5), and a coverage refusal sends the
concept back to stage 3, after which the exam is taken again. On record: 13 of 16 exam runs passed; 3 of 14 coverage
looks signed. Six exam retakes followed a coverage refusal, USD 18.79 `[measured]`. Letting the judge that usually
refuses look first, and taking the exam once on the tree it signs, would have saved most of that. It changes the
Designer's stage order, so it is filed as a decision for the Conductor with this evidence, not built:
`RIMMANDRAKE_DECIDE_COVERAGE_LOOK_BEFORE_EXAM_SIX_EXAMS_RETAKEN`.

## 8. Relation to the 2026-11-12 preflight spec

`design/specs/2026-11-12-ticket-preflight-before-any-token.md` stands. It guards the ticket doors (filing, claim,
start, helper launch, live-queue submit) against references to things that do not exist. This spec guards the stage
doors against work a program can already see will fail. The waste measured here sits at the stage doors, which is why
the first three tickets below come before the preflight's.

What changes in that spec, edited there today: Relentless is retired (2026-11-13), so its "not in Relentless" clauses
and its ticket 11 are dead; the helper-launch door gains the `## launch-checks` block of section 3.2, which the
preflight's shadow run observes like the door's other checks; its group F (acceptance-test sanity) gains "the
acceptance command still fails on origin/main at launch", which is the `must-fail` line. Its three filed tickets are
unchanged and have waited since 2026-11-13 00:25 PST.

## 9. Build order and tickets

Ordered by measured waste stopped per build dollar; build cost is a guess from today's comparable builder runs
(USD 1.3 to 5.3 each). Each ticket's acceptance test is in `src/RimMandrake/rimflow/acceptance/` and was watched failing
on `ed7e3b5389`.

| Order | Ticket | Stops (two weeks) | Build | Acceptance test, on the base |
|---|---|---|---|---|
| first | `RIMMANDRAKE_CHECK_DESIGNER_RESULT_BEFORE_EXIT_EIGHT_REJECTED` | about USD 9.7 and six unmeasured runs | Sonnet or Opus, about USD 3 `[guess]` | `guard_designer_result_accept.py`: 0 of 12 |
| second | `RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES` | about USD 10.9 | Opus, about USD 5 `[guess]` | `guard_launch_checks_accept.py`: 0 of 21 |
| third | `RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN` | about USD 9.8, and his direct question | Opus, about USD 5 `[guess]` | `guard_judge_certificate_accept.py`: 0 of 18 |
| then | `RIMMANDRAKE_REFUSE_MISSING_TOOL_SCENES_GRAFFITI_READS_READY` | Graffiti's first visit, not yet driven | Sonnet, about USD 2 `[guess]` | `guard_scene_stops_accept.py`: 3 of 10 |
| then | `RIMMANDRAKE_CARRY_STAGE_FIVE_BY_PROGRAM_TEN_RELAY_RUNS` | USD 8.39 | Opus, about USD 4 `[guess]` | `guard_stage5_program_accept.py`: 0 of 13 |
| then | `RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS` (open since today) | Unmeasured share of USD 48 of judge looks | already scoped | its own |
| then | `RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED` (after the certificate) | three false passes, one live today | Opus, about USD 4 `[guess]` | `guard_empty_game_accept.py`: 1 of 8 |
| then | `RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN` (after the certificate) | one probable incident | Opus, about USD 4 `[guess]` | `guard_judge_certificate_accept.py --red-seen`: 2 of 28 |
| last | `RIMMANDRAKE_SCAN_SCENES_AGAINST_BARS_TOGGLE_NEVER_TOGGLED` (after the empty game) | two known misses of one visit | Sonnet, about USD 3 `[guess]` | `guard_light_scan_accept.py`: 0 of 14 |
| after these | The preflight's three tickets, then `RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS` and `RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD` | see their own specs | | |

The clauses that pass on the base are the ones that say "refuses nothing" or "the source is restored", true when no
code exists; each ticket names them.

## 10. UNMEASURED

- The dollars of 192 of the 289 detached runs (their result files were written over before the cost read-back existed).
- Why seven runs were killed and relaunched within six minutes.
- Explosive Knockback's Designer loop: 86.5M of its 97.2M tokens are booked under the kind `unmeasured`.
- Which of the 21 UNMEASURED rows of the three first visits were tool faults a program could have seen.
- How much of the coverage judge's refusing is noise, beyond the one audited round.
- Whether a Sonnet scan sees the two semantic misses; the last ticket measures it.
- Whether "source path does not exist" still misfires today; the last one on record is 2026-11-13.
