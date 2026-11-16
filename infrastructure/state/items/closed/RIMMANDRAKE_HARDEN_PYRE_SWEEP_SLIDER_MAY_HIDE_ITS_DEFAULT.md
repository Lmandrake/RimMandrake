## spec
Problem against the test (Pyrelands 0.1.0, bar inv_settings_gate; blind challenge cycle 2, miss_of 1). No inv_settings_gate
decider checked that a Mod Settings slider's range holds its shipped default; a range that excludes it moves the value the
first time the window draws. Planted fault S_DOUSING_SLIDER_EXCLUDES_DEFAULT (blackRainDousing slider 50..100, default 40)
stayed green in T_SETTINGS_SWEEP_OFFLINE, T_SETTINGS_SCREENS and T_SITE. Today all 17 sliders hold their defaults (lane 1).
Fixed in the test: fact sliders and one mutant.

## verify
python3 design/concepts/Pyrelands/version/blind_challenge/cycle_2/lane2/catch_check.py S_DOUSING_SLIDER_EXCLUDES_DEFAULT src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py exits 0.

## criteria
Acceptance test: that catch_check run, 1 pass (rc 1 on the parent 85c4d61bee, watched; rc 0 on b7b77c929e).

## refs
file: src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py
