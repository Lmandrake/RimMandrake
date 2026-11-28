A pipeline selftest run inside a mod holder run inherits RM_MODLEDGER_WRITER and fails in modledger.append (selftest_resume_voided_blind_judge.py, 2 of 20 red on 2026-11-28); the same test passes 20 of 20 under env -u RM_MODLEDGER_WRITER -u RM_MODLEDGER_TOKEN. Before you blame your change for that red, rerun with the variables unset.
item: RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST
home: NONE
