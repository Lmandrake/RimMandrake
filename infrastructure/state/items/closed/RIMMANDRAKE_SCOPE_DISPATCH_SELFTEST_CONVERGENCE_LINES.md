# RIMMANDRAKE_SCOPE_DISPATCH_SELFTEST_CONVERGENCE_LINES

## spec
`selftest_maturation_dispatch.py` is RED on origin/main 2826ca6878 (and on 8586d42006), with one failing check:
"a Stage 3 filing that hit a lock retries on the next tick, no stop, no Needs Conductor line". It fails with
`['ExplosiveKnockback Stage 3 (Offline build) DIVERGING, open rising: open 6 -> 5 -> 6 ...']`.

Cause, two commits that each pass on their own:
- 899aeb728f (convergence) makes `tick()` call `maturation_convergence.annotate_reading(root, rd)`
  (maturation_dispatch.py ~1296). That appends one Needs Conductor line per DIVERGING stage of every mod under
  `root/design/concepts`.
- 455fb5eec8 (launch retry) asserts `not r1["needs_conductor"]` (selftest line ~431). Its temp root carries the
  ExplosiveKnockback fixtures pinned at FIXTURE_SHA, and their offline_build rounds really do read DIVERGING.

So this is not a live-data leak: the fixture root is right, and the assertion is broader than its subject (FlowWorks's
launch retry). Fix it without weakening anything. Either give `tick` an fx hook that stubs convergence in this check,
or assert that no line names FlowWorks AND add a separate positive check that the EK convergence line is there.

Evidence: D:\ClaudeWork\rimmandrake\harden_dispatch\st_d2a_merged.txt, st_md_head.txt (it fails with HEAD's
maturation_autonomy too).

## acceptance
`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_dispatch` reads GREEN on origin/main.
The check still fails if FlowWorks's retry writes a Needs Conductor line (mutate it once and watch it go red).
