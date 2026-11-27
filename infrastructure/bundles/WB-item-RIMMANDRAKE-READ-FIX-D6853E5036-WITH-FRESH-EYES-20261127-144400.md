# WB-item-RIMMANDRAKE-READ-FIX-D6853E5036-WITH-FRESH-EYES-20261127-144400

State: done (one member, one group).

| ticket | outcome | commit |
|---|---|---|
| RIMMANDRAKE_READ_FIX_D6853E5036_WITH_FRESH_EYES | fresh read found one Problem, fixed test first, file FLAGGED | b19cc679dd (fix), 090897fb39 (flag) |

The Problem: in `src/RimMandrake/bridgetools/prove_vitals_governor.py`, each blind path (`raise SystemExit("UNMEASURED: ...")`,
`assert r.get("armed")`) exited 1, which the file's own exit contract (and `rimflow` effect checks) read as FAILED, and
it wrote no proof JSON, so rows already measured were lost. Now `blind()` records `run_stopped_could_not_look` UNMEASURED
and `finish()` writes the JSON and exits by the contract. Test `src/RimMandrake/Utils/selftest_vitals_proof_exit_contract.py`
(4 promises; the two cannot-look tests red on the parent, green on the fix). New page
`design/specs/2026-11-27-vitals-proof-exit-contract/boundary.md` (registered in boundary_check.py PAGES); `check` reads CLEAN 4/4.
