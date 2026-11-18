# RIMMANDRAKE_FIX_LOOK_GRANT_COUNTED_TWICE_COVERED_LOOK_FREE

## spec
Also: look windows were bare timestamps, so a plain release and a grant in the same second shared one account (selftest_coverage_judge_loop caught it); windows are now keyed `grant:<at>` or `release:<at>#<n>`.
Two flaws in the granted coverage look's account (Codex review of slice 1, 2026-11-18): `coverage_judge.reserve_look`
passed the limit (base plus grants) as the account's base, so `control._account` added every `pipe grant` twice; and
`control._account` replaced the store's charges with the caller's refusal count, so a look charged on a `covered`
verdict read as unspent and a second judge could reserve it.

## verify
`python3 src/RimMandrake/rimflow/selftest_control.py` (t_coverage_look).

## criteria
Its two checks ("a grant of one adds exactly one look, never two"; "a look charged on a covered verdict stays spent")
fail on 412cebe4eb (watched 2026-11-18) and pass after the fix.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/coverage_judge.py
file: src/RimMandrake/rimflow/selftest_control.py
