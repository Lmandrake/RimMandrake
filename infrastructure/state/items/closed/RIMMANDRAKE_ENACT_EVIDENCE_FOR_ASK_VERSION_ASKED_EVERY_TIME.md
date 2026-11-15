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

## done (2026-11-15, BENCH restart after the ~12:00 PM PST account switch)

- 2fb89c96e5: CLAUDE.md, standing_rulings.md, the two version specs (before the switch).
- f8e409678f: CHARTER §Decisions states the rule once; conductor.md, designer_dialogue.md, designer_grounding.md and
  designer_write.md point at it. Goal order with no order of his: listed as he gave them, logged delegated. A wider
  budget (Operations proposal) is paid, so it stays his with Operations' evidence on the card. New-skill proposals
  stay a discussion: his 2026-10-29 words ask for it, which is the evidence. CHARTER grew 4 lines (its "does not
  grow" note): nothing in it was found to delete for them.
- 2e5513ef60: delegation_policy.md. Evidence-for-Ask is not a timeout: it decides what is reserved (only the seven §2
  lines); a §2 call still waits and its ask carries its evidence (the Conductor's reading, given to him ~12:00 PM PST,
  no objection; not a ruling of his). §1 names the rule; §3 allows `--per-ruling` for this one ruling, with the
  `delegated:` why. The digest now classes these calls `evidence-for-ask` (they were reaching it as `unclassified`).
- c6004c67da: a passed version RESTS (new class `rested`, no owner card, no pause alarm); opening the next version is
  the Conductor's ordering call against the other mods (`maturation.py next-version`). The `version` clause's fix no
  longer says "decided with him".
- e333f1eb5c: `designer_stage.py turns` / his queue line: each sent ask shows its `evidence_against`, or is marked
  "no evidence against the obvious answer: the Conductor takes it delegated". conductor.md: such an ask is the
  Conductor's, never relayed.
- f2c998c131: intake after the first walk asks him nothing. His 2026-11-14 card picked only "Wait for one full pass";
  "asked again then" was our note. His 2026-11-15 order (next most mature biome mod) is the obvious answer. Spec fixed.

## kept as his, with the evidence (no change)

- his walk (`his_walk`, `maturation.py` `owner_said` at Stage 8): the pass is his alone (spec Stage 8).
- OWNER HOLD blocks (maturation_autonomy): his own holds. The one standing today, PyrelandsMechanics, waits on his card
  of 2026-11-13 ("started only after Pyrelands 0.1.0 passes", VERSION.json `owner_words`); `version_evidence` reads
  the same state. Its `blocked_on` lift text ("locks on his word after he reads the entry summary") is older than the
  0.1.0 ruling and could be cut to the card's condition when Pyrelands passes.
- designer_stage OWNER_ONLY quotations (`exam_waived`, `floor_disable`, `locked_change`, `waiver`, `his_words`) and
  concept_tree certify (delegation_policy §2.7): quotations and the reserved first-touch certification.

## not owner pauses (no change)

- maturation.py `hold`, `steward_confirms`, `walk_bars_confirmed`, `fourth_cycle`: Conductor and steward steps that
  steward runs carry (maturation_autonomy STEWARD_ON); `cost="owner"` there labels owner authority, which the Conductor
  holds (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM). Nothing routes on that label.
- roles/innovator.md:60: a report line on his card, not a pause.

## unrun

- The `rested` path and the turn marks on real data: no mod is at `passed` and no Designer turn waits today
  (dry `maturation_dispatch.py tick` and `designer_stage.py turns` on /home/mandrake/rm/bench, 2026-11-15 20:2xZ).
  Fixture tests only.
