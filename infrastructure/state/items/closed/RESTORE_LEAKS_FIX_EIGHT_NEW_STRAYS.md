## spec
found-by: LONGSHADE_STAMPEDE_LIVECHECK_1 worker (relentless), 2026-11-03, `run_selftests.py --only selftest_proof_restore_check.py` on a1294d5451.
selftest_proof_restore_check is RED on main: 8 hits outside the filed BASELINE in proof_restore_check.py:
  src/RimMandrake/LeaningScrub/Source/RM_TheLeanProof.cs:250 unrestored-on-throw
  src/RimMandrake/LeaningScrub/repro_stall_move.py:148 unrestored-on-throw; :191 restores-fixed-value
  src/RimMandrake/LuminousPigment/Source/RM_LuminousFamilySettingsProbe.cs:111 unrestored-on-throw
  src/RimMandrake/RimProperty/Source/RM_SettlementVerbsProof.cs:134,174,204,254 unrestored-on-throw
Fix each (restore the READ value on every exit path; pattern in FLOWWORKS_PROOF_POKES_RESTORE_PRIOR) or, if a hit is a false positive, fix the checker's rule with a planted case. Never just add baseline keys.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_proof_restore_check.py is GREEN with the BASELINE unchanged or lowered.
