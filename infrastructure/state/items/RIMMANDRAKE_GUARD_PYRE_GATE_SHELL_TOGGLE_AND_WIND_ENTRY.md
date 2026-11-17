# RIMMANDRAKE_GUARD_PYRE_GATE_SHELL_TOGGLE_AND_WIND_ENTRY

T_SETTINGS_SWEEP_OFFLINE missed three ungated mechanics

## spec
Planted faults survived the inv_settings_gate deciders: ShellOn forced true (the Baroque Biomes toggle gates nothing), the furnace-beast heat-immunity prefix ignoring the gate, and MapComponent_BurnLine.WindCarries ignoring the gate. Fixed in selftest_pyrelands_settings_sweep.py: gate_wired checks ShellOn; entry_gated adds the heat-immunity prefix and the WindCarries predicate (gate and its own switch); five mutants added.

## verify
Acceptance test: python3 design/concepts/Pyrelands/version/blind_challenge/cycle_3/lane2/catch.py gate_shellon_always T_SETTINGS_SWEEP_OFFLINE; same for heat_immunity_gate_ignored and wind_ignores_gate. rc 1 (missed) on 912c1ee157, rc 0 (caught) at the fix; 3 runs.

## criteria
The named command passes at the fix sha; the planted fault (lane2/planted_faults.json) is caught.

## refs
file: src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py
