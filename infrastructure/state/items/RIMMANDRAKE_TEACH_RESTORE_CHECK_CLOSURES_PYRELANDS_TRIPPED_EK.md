# RIMMANDRAKE_TEACH_RESTORE_CHECK_CLOSURES_PYRELANDS_TRIPPED_EK

Pipeline defect found by the cycle-5 steward's `maturation.py certificate ExplosiveKnockback --run` (2026-11-16 22:13 PST):
T_RESTORE (`selftest_proof_restore_check.py`, an offline decider of ExplosiveKnockback's `inv_proof_scenes`) went red
on a file outside the mod: `src/RimMandrake/Pyrelands/wind_burn_live.py:56 unrestored-on-throw`, committed 49e11870b4
at 21:44 PST, after the blind judge's 16/16 rerun.

## spec

The script is not a leak: the poke `setf("windCarriesFireEnabled", wind_on)` sits in a nested function `run()`, every
call of which is inside a `try` whose `finally` writes each field's captured prior back (`for f, v in prior.items():
setf(f, v)`). `proof_restore_check.check_py` judged the poke lexically only, so a closure called from a guarded try read
as unguarded. Fix: one level of closures, judged at their call sites in the enclosing function (guarded when there is
at least one call site and each is guarded or in a finally); the guard test is lifted into `_guarded`.

## refs
file: src/RimMandrake/Utils/proof_restore_check.py
file: src/RimMandrake/Utils/selftest_proof_restore_check.py

## criteria

Acceptance test: `python3 src/RimMandrake/Utils/selftest_proof_restore_check.py` -> rc 0. Red before the fix (watched):
the new case "a closure's poke is judged at its call sites" and the repo row (wind_burn_live.py:56) FAIL. The new cases
also pin the other side: the same closure called once after the try, and a closure never called, are still hits.
Planted mutants in the fix (closure always guarded; any call site instead of all) each turned the selftest red.

## verify

`python3 src/RimMandrake/Utils/proof_restore_check.py` prints new=0; `maturation.py certificate ExplosiveKnockback
--run` shows T_RESTORE green.
