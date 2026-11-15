# RIMMANDRAKE_LAND_JUDGE_SIGNATURE_BEFORE_LOCK_GATE_READS_IT — a covered Lock was refused "no coverage signature on the ledger"

## evidence (2026-11-15)

- rm-coverage-judge-1794753924 judged Graffiti `covered`, `signed: True` (coverage_verdict.json, 14:45:24Z); its ledger note
  (`coverage-signed concept=design/concepts/Graffiti tree=a6eedf87…`, seat CONDUCTOR, ts 14:47:40Z) sits in
  `infrastructure/state/ledger/events/CONDUCTOR.jsonl` of `/home/mandrake/rm/bench` and `/home/mandrake/rm/dispatch` **uncommitted**
  (`git log -S rm-coverage-judge-1794753924` finds it in neither; origin/main lacks it).
- The stage-5 run rm-role-designer-1794753910 was rejected at 14:53:08Z: `gate: no coverage signature on the ledger`
  (`role_launch.stage_close` → `designer_stage.close_run(repo=DS.REPO)` → `CT.gate`).
- At ~15:00Z `CT.gate` on both clones returns no errors: the refusal was transient, and a Lock retry was pressed by hand.

## spec

The signer lands its ledger note (or the gate reads the shard the signer wrote) before the stage-5 run's close runs the gate; a
Lock must never stand on a ledger line only a working tree holds.

## verify

Acceptance test: none offline yet, the race is across two live clones and the Dispatcher's close; the builder writes a selftest
that signs in clone A, closes in clone B without the line, and expects the gate to wait or read it, not refuse.
