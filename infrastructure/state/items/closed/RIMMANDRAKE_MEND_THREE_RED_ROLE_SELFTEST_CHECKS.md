# RIMMANDRAKE_MEND_THREE_RED_ROLE_SELFTEST_CHECKS

## spec
Three selftest checks were red in the bench clone on 2026-11-17 (~18:10-18:20Z, level with origin), independent of the publish-stuck fix
(784271398b12). The first was also red on a copy of HEAD from before that fix:

1. `selftest_dispatcher` `test_review_t`: "F1: Operations (token_aware) is told its band and budget" (the
   role_launch message no longer carries "Token budget" / "runway" / "does not stop you" together).
2. `selftest_incident`: "no alarm site in the tree is unreadable by the census" names
   `Utils/ops_watch.py:1084 point key Name` and `Utils/ops_watch.py:1090 point key Subscript`.
3. `selftest_incident`: "every role_launch alarm falling through to cause roles is a reviewed fault" reports
   new: ['codex_stop'].

Each is evidence about a recent change, not a check to edit: find the commit that turned it red
(`git log -S` on the message / alarm kind), then either fix the code or file why the check's bar moved.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_dispatcher selftest_incident` reads GREEN.

## criteria
- F1 check passes
- the alarm census reads every ops_watch alarm site
- codex_stop is reviewed (routed or listed) and the fall-through check passes

## refs
file: src/RimMandrake/rimflow/selftest_dispatcher.py
file: src/RimMandrake/rimflow/selftest_incident.py
file: src/RimMandrake/Utils/ops_watch.py
