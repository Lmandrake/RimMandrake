## spec
Problem against the test (Pyrelands 0.1.0, bar inv_settings_gate; blind challenge cycle 2, miss_of 1). T_SETTINGS_SWEEP_OFFLINE
checked that each gated switch is read in a FILE that mentions PyrelandsMechanicsGate.On, never that the gate itself reads
"Mod enabled" and the Baroque Biomes toggle "Pyrelands", nor that each mechanic entry postfix consults the gate in its own body.
Planted faults C_GATE_MASTER_BYPASSED, C_GATE_ROSTER_KEY_TYPO, C_FERTILITY_POSTFIX_UNGATED, C_DOUSE_POSTFIX_UNGATED and
C_NO_RAIN_POSTFIX_UNGATED (design/concepts/Pyrelands/version/blind_challenge/cycle_2/lane2/planted_faults.json) left all three inv_settings_gate deciders green
(design/concepts/Pyrelands/version/blind_challenge/cycle_2/lane2/planted_results.jsonl). Fixed in the test: facts gate_wired and entry_gated, five new mutants.

## verify
python3 design/concepts/Pyrelands/version/blind_challenge/cycle_2/lane2/catch_check.py <FAULT> src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py exits 0 for each of the five
faults (rc 1 on the parent 85c4d61bee, rc 0 on the fix b7b77c929e), and the sweep itself passes.

## criteria
Acceptance test: the five catch_check runs above, 5 passes, plus the sweep PASS with 16 of 16 mutants red. Watched failing on
the base 85c4d61bee (all five MISSED, rc 1).

## refs
file: src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py
