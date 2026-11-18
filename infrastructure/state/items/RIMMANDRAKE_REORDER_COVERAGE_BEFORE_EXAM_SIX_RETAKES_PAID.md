## spec

The build that follows `RIMMANDRAKE_DECIDE_COVERAGE_LOOK_BEFORE_EXAM_SIX_EXAMS_RETAKEN`. That item's decision event
(2026-11-16T01:50:04Z, tsn 1794793804486811354) reads *"DECISION: yes. NEXT: a builder files and builds the
stage-order change with its acceptance test (stage machine order, exam_gate, locked-change chain), after the first
three guard tickets."* 🔴 **That event is a DELEGATED evidence-for-ask decision taken by an agent under
`RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME`, not the owner's own words** — it reached him in a
digest; he has not ruled on the order himself. His 2026-11-14 card kept both the Exam and the coverage judge as gates
before a lock and said nothing about which comes first.

**What to build.** The coverage judge looks before the Designer exam. The exam is then taken ONCE, on the tree the
judge signs, and again only if the exam itself changes the tree.

The measurement that bought the decision, from the Designer run records and each `stage.json`, 2026-11-04 to 11-15:
13 of 16 exam runs passed; 3 of 14 coverage looks signed; six exam retakes followed a coverage refusal. The cheap
check that usually refuses should run first.

**The counter-evidence is UNMEASURED and must be settled by this build, not assumed away.**
`maturation_autonomy.exam_gate` (line 369; wired at line 638 as `fx_exam`) makes the coverage judge SKIP when the exam
does not pass. Somebody wanted that order. Before reordering, read why, and say in the commit message whether the
judge's reading leans on an exam-passed tree. If it does, the reorder needs the owner, not a builder: stop and say so
with the evidence.

Three things move together, so the acceptance test must cover all three:
1. **The stage machine's order** — `designer_stage.py` `STAGES = (0, 1, 2, 3, 4, 5)` with
   `STAGE_NAMES = {... 4: "Exam", 5: "Lock"}`. The coverage look is today after the exam; where exactly it sits in
   the machine is to be read, not guessed.
2. **`exam_gate`** — a judge that skips on a not-passed exam cannot run first. Whatever replaces it must keep the
   four answers apart: a tree the exam has not yet READ is not a tree the exam FAILED, and neither is a gate that
   could not run. A gate that cannot run says "did not run" and lets the work through
   (`standing_rulings.md`, A refusal carries its path to pass).
3. **The locked-change chain** — an exam that changes the tree after the judge signed invalidates that signature;
   the chain must then ask for one more look, and must not silently keep a stale signature.

## refs

file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/maturation_autonomy.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md

## verify

python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_maturation_autonomy

## criteria

- A1: a concept whose coverage look refuses never takes an exam on that tree (the six measured retakes become zero).
- A2: a concept whose coverage look signs takes exactly one exam on the signed tree.
- A3: an exam that CHANGES the tree after a signature asks for another look; the old signature is not reused.
- A4: a coverage gate that could not run is recorded as "did not run" and lets the work through — never as a refusal,
  never as a pass.

## acceptance

Acceptance test: a new case in `selftest_designer_stage.py` (or a selftest file beside it) driving the stage machine
through all four criteria with fixed stage dicts, watched FAILING on the base commit before the fix, with the failing
output quoted in the commit message. A1 and A2 fail on base by construction (the order is the other way round); A3
and A4 are the ones that must be written carefully, because they are the regressions a reorder can introduce.

The builder does not edit this acceptance section; a clause believed wrong goes to the Conductor with the evidence.
