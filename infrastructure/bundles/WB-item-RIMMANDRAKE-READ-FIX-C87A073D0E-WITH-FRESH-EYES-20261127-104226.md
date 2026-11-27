# WB-item-RIMMANDRAKE-READ-FIX-C87A073D0E-WITH-FRESH-EYES-20261127-104226: state

Done (one group, one context, no restart):
- `RIMMANDRAKE_READ_FIX_C87A073D0E_WITH_FRESH_EYES` (fresh read of c87a073d0eba): REAL, fixed.
  - src/RimMandrake/Utils/clone_pack.py: Problem, reason promise-untested. A `one()` that never wrote the hold
    (`hold(root, apply=False)`) passed all 17 selftest checks. The selftest now reads each clone's config: 2 checks red
    on that mutant, green on the real build (189e59caaa). Prose said "exactly when git would have"; git 2.53 packs at
    51 packs (measured), fixed 98926e5ac6. File FLAGGED (67bd122e6b).
  - src/RimMandrake/rimflow/maturation_dispatch.py: FLAGGED before this read; not read again (code_review.md).
- Fault with no ticket, found when publish went red: selftest_detached_reap `a-leftover-child-is-ended-and-the-clone-returned`
  went blind on `tailscaled be-child ssh` (same uid, environ EACCES, root parent): 7 publishes red since 2026-11-24.
  Red test first, fix c25df44d64 (`_parent_of_another_uid` in detached_helper.scan_marked_live). Live reading: 0 blind
  in 148 scans over 30 s on SteveDesktop (before: 11 blind in 90).
Next: nothing.
