# RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME

## spec

The owner, Sun 2026-11-15 ~11:40 PST: "You are repeatedly asking me to rule on whether 0.1.0 is appropriate for a new
mod. So far it is every single time. You must have evidence why 0.1.0 is NOT appropriate to pause to query me from now
on. For ALL questions and choices from now on, Conductor must have evidence why it does not select the obvious answer
before it pauses for the human, alright? This is a RimMandrake-wide ruling for all pausing agents. Let's call it the
Evidence-for-Ask rule."

The rule: an agent that would pause for him takes the obvious answer instead. It logs that answer as a delegated call
(`--per-ruling RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME --why "delegated: evidence-for-ask: ..."`),
which reaches his daily digest (`delegated_digest.py` reads every `delegated:` why). It pauses only with concrete
evidence against the obvious answer, and every ask carries that evidence.

## done (2026-11-15, BENCH)

- 6321db9aac: maturation. A new mod whose concept tree is locked and whose Design Version is not gets VERSION.json
  locked at 0.1.0 by the pipeline (`locked_by: pipeline`, `per_ruling` this item), plus a delegated record in
  `infrastructure/state/delegated/<day>/<Mod>-design-version-0.1.0.json`. It still asks him, quoting the evidence, when
  `maturation_autonomy.version_evidence` finds any: another version in VERSION.json, a state not open, a stage record of
  another version or already passed, a `stage_record_<semver>.json`, or a record.json `version_objection`. Tests in
  selftest_maturation_autonomy / selftest_maturation, watched failing on base 6dcc361c54.
- 12f206a9af: designer_stage. A root (`answers: <ask id>`) or the flagship pick may be approved by a recorded delegated
  Evidence-for-Ask call (speaker conductor, `delegated: "evidence-for-ask"`, source `CONDUCTOR:<tsn>` of an OWNER.jsonl
  event per-ruling this item, why `delegated: evidence-for-ask`, about this concept). An ask with `evidence_against`
  still waits. Hole closed: an owner root now must cite an event of his (ownerSaid or byCard) about this concept;
  before, any `OWNER:<tsn>` passed. The other owner-only kinds and the Lock-stage certification stay his. Tests in
  selftest_designer_stage, watched failing on base. roles/designer.md says so.
- The Contagion root and flagship were NOT applied through it: he certified them himself ~11:55 PST (owner-said note on
  RIMMANDRAKE_ADMIT_CONTAGION_AS_NEXT_BIOME).

## owed

- 2fb89c96e5: docs written: CLAUDE.md (section "The Evidence-for-Ask rule"), standing_rulings.md (new section,
  plus a §Mod Design Versions bullet: a new mod's 0.1.0 is locked by the pipeline), and the lock lines of
  design/specs/2026-11-13-mod-design-versions.md:24 and 2026-11-13-maturation-pipeline.md:172.
- Docs still owed:
  - design/RimMandrake/delegation_policy.md §1/§2: a new mod's first Design Version is 0.1.0 without asking; each §2
    hold of his stays, and its ask carries the evidence. CONFLICT to put to him, not resolve: line 132, "A reserved call
    is asked as a card ... It never times out into a decision", reads against Evidence-for-Ask for any reserved call
    with an obvious answer.
  - maturation-pipeline.md: opening the next version is still "decided with him" (see OWNER_STAGES `passed` below).
  - infrastructure/agents/CHARTER.md, roles/conductor.md and the role files listed below.

## other places that pause for him (listed, not fixed; obvious answer for each)

Code:
- src/RimMandrake/rimflow/maturation_autonomy.py:79-80 OWNER_STAGES `his_walk`: stays his (his live walk is the stage's
  exit by his own words). `passed`: opening the next version is "decided with him"; obvious answer: open the next
  version (minor bump) when the walk's findings name work, else nothing to open.
- maturation_autonomy.py:223, :552 "OWNER HOLD" blocks: a hold he placed stays until he releases it (his own hold).
- src/RimMandrake/rimflow/maturation.py:~479-480 clause `version` (open a new version by hand, cost owner): obvious
  answer: seed the next version's stage record when the old version passed.
- maturation.py:~489 `hold`: a Conductor hold, released by the Conductor; no owner pause needed.
- maturation.py:~505-507 `intake_closed`/`owner_said` "how the waiting mods enter after the first walk is asked of him
  again": obvious answer: the next mod in queue order enters when one reaches his walk.
- maturation.py:~538-544, ~572, ~589 `steward_confirms` (cost owner): the Conductor's own read; obvious answer: the
  steward confirms when every refusal left is named in the record.
- maturation.py:~597 `owner_said` at his walk: stays his.
- maturation.py:~608 `fourth_cycle`: the Conductor decides after three blind cycles; obvious answer: take the
  majority finding and record it delegated.
- src/RimMandrake/rimflow/designer_stage.py:73 OWNER_ONLY `exam_waived`, `floor_disable`, `locked_change`, `waiver`,
  `his_words`: quotations, stay his. `waiting_owner` (designer_stage.py:1150, roles/designer.md:61,76): any ask; obvious
  answer per ask is the Designer's recommended option, so every ask should carry `evidence_against` or not be sent.
- concept_tree.py certify --owner-event (Lock-stage first touch): stays his (his words 2026-11-04).

Docs and roles:
- design/RimMandrake/delegation_policy.md:132 reserved calls asked as a card, never time out (conflict above).
- src/RimMandrake/rimflow/roles/designer_dialogue.md:10, :75, :105 ask him only the gaps / `pass` asks reach him: add
  "and each carries its evidence against the obvious answer".
- roles/designer_grounding.md:45 "Ask him only on a real fork": same.
- roles/designer_write.md:5 "Ask him to approve the root text before this stage": now a delegated root may approve it.
- roles/conductor.md:31 "when he gives no order, ask him rather than guess" (goal cuts): obvious answer: cut the lowest
  ranked goal's work first, as the line itself says.
- roles/conductor.md:76 bring a file to him on his card; :173 skill proposals on a question card: obvious answer:
  accept when nothing argues against it, record delegated.
- roles/innovator.md:60 the proves-itself line on his card: a report, not a pause.
