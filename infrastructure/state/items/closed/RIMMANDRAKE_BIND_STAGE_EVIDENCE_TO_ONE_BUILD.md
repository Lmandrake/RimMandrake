# RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD

## spec
What is left: the pass record. When a version passes his walk (Stage 8), it writes the pass record: date, git commit,
bars, evidence, cost, cycles (Design Versions draft §3.7), plus the build identity he walked (mod source sha, deployed
folder hash, the parsed ModsConfig activeMods list in order, game build: the fields
`src/RimMandrake/rimflow/build_match.py identity` prints). Source: skeptical review 2026-11-15
(`D:\ClaudeWork\rimmandrake\conductor\maturation_gpt_review_20261115\claims_checked.md` A12;
`design/RimMandrake/maturation_pipeline.md` §9 "Designed but not built").

Already built elsewhere:
- a3b3dead86b8: read_ingame_exit refuses a visit whose rows name more than one build.
- Item `RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO` (his ruling of 2026-11-17) built the build match at the
  Stage 6 exit (`build_match.py`: a verdict whose mod hash or game build differs from the walk build does not count,
  and its line item is re-run; full-list tests match his walk's list, minimal-list tests their tier's
  `modset_builder.py` list from the same commit). The same ruling made Stage 7 a walk brief with no veto, so there is
  no Stage 7 verdict or reader to build here.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_maturation.py`, new case: the
pass record carries every field above, and a pass with no build identity is refused.
