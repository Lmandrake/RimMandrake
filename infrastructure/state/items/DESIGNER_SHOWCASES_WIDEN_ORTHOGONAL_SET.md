# DESIGNER_SHOWCASES_WIDEN_ORTHOGONAL_SET

## Owner, 2026-11-05 (verbatim, in OWNER.jsonl on this item)
"Maybe it might be good to add the idea of multiple showcases then that are as orthogonal as possible. The Other
showcases (if present) should feature ONLY very different functionality compared to the prior ones, until efficient
coverage is had."
Asked about the Designer designing only the one first-judged scene (FlowWorks: the moat sequence).

## Built
- Doctrine: src/RimMandrake/rimflow/roles/designer_scene_contract.md "The showcase set" (stage 0 and stage 3 packets);
  designer_write.md, designer.md stage table, designer_lock.md step 4.
- Numbers: src/RimMandrake/rimflow/showcase_rules.json, max_overlap 0.25, min_new_after_first 3, UNMEASURED.
- Checks: designer_stage.py showcase_table (stage 3 and stage 5 refuse), `designer_stage.py showcases <dir>`.
- Selftests: selftest_designer_stage.py refusals_showcases + stage 3 / stage 5 integration.

## Owed
- Calibrate the two numbers on the first two concepts reaching stage 3 (FlowWorks first); record in showcase_rules.json.
  Filed as `SHOWCASE_RULES_TUNE_AWAITING_STAGE_THREE` (2026-11-05: FlowWorks still at stage 2).
- The event deliberately does not name the FlowWorks concept item: owner events naming it wake its stage 2 (waiting
  on his turn-2 answers). Stage 3 reads the rule from its packet.

## Watch out
- Coverage unit = record.json inventory capability (not leaves); "very different in play" is judged by exam/owner, not code.
- GPT review (2026-11-04, fixed): greedy is checked against every later showcase, not adjacent counts; a BUILT
  capability scoped out is still a unit (covered via coverage_rest only); showcase 1 must name a record.json owner
  decision whose OWNER source it shares, so an unrelated real OWNER event does not pass. Declined: a code check that
  `exercises` matches the scenes semantically (exam and owner judge it).
