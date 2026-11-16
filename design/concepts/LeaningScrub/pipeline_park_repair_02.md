# Park-page coverage routing repair

System item: `RIMMANDRAKE_SHOW_ADVISORY_COVERAGE_WITHOUT_OWNER_FORK`. Triggered while preparing Stage 2 root validation in run `rm-role-designercodex-1794831790`.

`designer_stage.park_summary` ignored `coverage_verdict.json` advisory status. LeaningScrub's retained UNTESTED refusal would have become a binding-looking refusal on the owner page, and flawed-criterion g12 would have appeared as an owner scope question. This contradicted `designer.md` coverage routing and the actual return reason in `lock_review_05.json`.

Permanent fix: preserve the full findings list, label advisory findings, avoid deriving owner asks from them, route flawed/unattainable criteria to the neutral fixer, retain sound calibrated stage-2 owner questions and Stage-3 agent fixes, preserve owner certification, and include the sent ask’s offered scene on the park page. With a sent focused ask, the generic certify/waive/stop menu is omitted. No concept obligation, criterion, gate or verdict changes.

Regression evidence: `selftest_designer_park_advisory.py` had three failures and one pass against the unchanged renderer; all four passed after the patch. The failures reproduced advisory promotion, contract-only advisory loss and a flawed/unattainable criterion sent to the owner. Existing `selftest_designer_park.py` and `selftest_designer_quick_look.py` pass. Fresh reviewer `/root/review_root_validation` independently ran all three suites and returned PASS with no scoped defect.

The patch was made in an isolated sparse clone to preserve pre-existing changes in BENCH's pipeline files. It changes only rendering, not state transitions or the owner-only root-validation requirement. Publication is recorded below after landing. No bridge, game, restart, deploy or mod handoff.

Published: `ae8b1f356bca89b2c3fe8535c77833dbcf2f5a41`. Publication ran 14 green tree checks and35 green pipeline checks.
