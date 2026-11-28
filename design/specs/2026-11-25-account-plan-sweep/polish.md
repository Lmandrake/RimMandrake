# Polish beside design/specs/2026-11-25-account-plan-sweep/boundary.md

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- `src/RimMandrake/Utils/account_plan_sweep.py` FLIP_FLOP exempts a spent `from` account, which the page does not say.
- `src/RimMandrake/Utils/account_plan_sweep.py` `stated=STEVE` and a constant `False` branch are dead code.
