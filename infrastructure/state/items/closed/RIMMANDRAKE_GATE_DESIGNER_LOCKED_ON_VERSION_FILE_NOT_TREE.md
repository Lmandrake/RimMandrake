# RIMMANDRAKE_GATE_DESIGNER_LOCKED_ON_VERSION_FILE_NOT_TREE

## spec

`src/RimMandrake/rimflow/maturation_autonomy.py` `_designer_lane` takes the `designer_locked` steward branch on
`stt == "locked" or (stg == 5 and locked(mod))`. The Designer's `stage.json` status `locked` means the concept-tree
gate passed (coverage signature, Lock stage done); it is not the Design Version lock, which is his word written in
`design/concepts/<Mod>/version/VERSION.json` (`state` locked, `locked_by` owner, `owner_words`). `maturation.py
advance <Mod> --to preflight` checks the VERSION.json lock (clauses `version` and `locked`), so the tick launched a
steward that can only refuse.

Measured 2026-11-15 (steward run RIMMANDRAKE_ADVANCE_GRAFFITI_LOCKED_VERSION_TO_PREFLIGHT): Graffiti's
`stage.json` reads status `locked`, stage 5; `version/VERSION.json` does not exist; `version/stage_record.json`
says version `UNMEASURED`; `maturation.py next Graffiti` refuses on `version` and `locked`.

Fix: take `designer_locked` only when `locked(mod)` (VERSION.json) is true; when `stt == "locked"` and VERSION.json
is absent or unlocked, take the existing `owner` branch ("the lock is his") with its card.

## verify

Acceptance test (fails on base 73ac7fb11c, watched: AssertionError, decision `steward`; passes on a fix, 1 command, 2
asserts):

```
cd src/RimMandrake/rimflow && python3 -c "
import maturation_autonomy as A
r={}; A._designer_lane(r,'Graffiti','UNMEASURED',{'status':'locked','stage':5},lambda m: False)
assert r.get('decision')=='owner', r
r={}; A._designer_lane(r,'Graffiti','0.1.0',{'status':'locked','stage':5},lambda m: True)
assert r.get('decision')=='steward', r; print('ok')"
```

Also add these two cases to `selftest_maturation_autonomy.py`.
