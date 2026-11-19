# RIMMANDRAKE_ADD_LAUNCH_CHECKS_EXAM_CERTIFY_JUDGE_THREE_UNCAUGHT

## spec
Left over from RIMMANDRAKE_RUN_LAUNCH_CHECKS_FIVE_STEWARDS_HIT_GATES (guard GATE_FIRST,
`design/specs/2026-11-15-cheap-guards-at-every-door.md` §3.2). That item built `launch_checks.py`, the door in
`detached_helper.launch`, `maturation.py gate`, and the block for a `ready` advance steward and a nightly red fixer.
Three of the five cited steward runs are still not caught, because their gate has no confirmed read-only command:
- the Pyrelands exam (RIMMANDRAKE_SIT_PYRELANDS_OWED_EXAM_AND_JUDGE_LOCKED_FIRST, USD 1.80): "the stage machine refuses to open them";
- the Knockback re-certify (RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING, 255,598 tokens): "certify refused";
- the 2026-11-13 07:54Z run that found the coverage judge parked (321,409 tokens).
Also left out on purpose: the `designer_locked` steward (RIMMANDRAKE_ADVANCE_<MOD>_LOCKED_VERSION_TO_PREFLIGHT): its
own steps (`lock-bars`, `next-version`) can turn the gate's `version` clause, so `gate --to preflight` at launch would
refuse a good run. The Graffiti case it cost is already stopped upstream by
RIMMANDRAKE_GATE_DESIGNER_LOCKED_ON_VERSION_FILE_NOT_TREE (the route reads VERSION.json).

For each of the three: find the read-only command that says whether the gate would open (or build one, read-only),
check its exit code both ways (one mod where it opens, one where it refuses), then have the filer that files that
steward item write `launch_checks.block_for`-style `must-pass: <command>` into it (`maturation_autonomy._execute_one`
passes `spec=` to `file_and_publish`; see `advance_checks`).

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_autonomy selftest_launch_checks

## criteria
- each of the three steward kinds is filed with a must-pass line whose command was watched exiting 0 and non-zero;
- or the close note names, per gate, why no read-only form exists.

## acceptance
Acceptance test: none, the read-only command for each gate is not yet identified; finding it and checking it both ways is the work.
