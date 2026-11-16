# RIMMANDRAKE_LAND_DESIGNER_WORK_HARVEST_STRANDED_TWICE

Designer harvest lands the run's own concept-folder work, not only stage.json. Caused by RIMMANDRAKE_RETAKE_GELATINOUSSLIME_EXAM_FAILING_ITS_GATE.

## spec
designer_stage.land_state (the Designer harvest's landing, DESIGNER_STAGE_FIX_COMMIT_ITS_OWN_STATE) lands only stage.json,
park_summary.md and result files. A Designer run's own work in design/concepts/<Mod>/ (record.json, tree.json, sheet.md,
scenes.json, floor.json, plan.md, root.md, exam.json, exam_control/, exam_evidence/) stays in the run's clone (the bench
seat clone). GelatinousSlime twice: stage 3's six artifacts (landed by hand in 5f3e54eac7 after a rejected close read them
missing) and stage 4's exam.json + exam_control/ + exam_evidence/ (stage.json recorded exam hash 6051e7..., origin/main had
no exam.json, so the gate read "no exam.json and no exam_waived" and the dispatch filed an exam retake).
Fix: land_state also lands every file under the concept folder that the clone itself changed (git status: modified or
untracked, existing on disk), so nothing it did not change is reverted over a peer's newer copy.
## verify
python3 src/RimMandrake/rimflow/selftest_designer_stage_land.py
## criteria
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_designer_stage_land.py` prints "all passed" (exit 0).
Watched red on base 0bce220281 with the new case: 3 failed (record.json, exam.json/exam_evidence not landed).
