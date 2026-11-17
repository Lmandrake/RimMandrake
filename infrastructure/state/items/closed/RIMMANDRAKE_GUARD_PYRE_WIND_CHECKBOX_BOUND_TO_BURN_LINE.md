# RIMMANDRAKE_GUARD_PYRE_WIND_CHECKBOX_BOUND_TO_BURN_LINE

No decider caught a settings checkbox bound to the wrong field

## spec
Planting ref burnLineEnabled on 'The wind carries the fire' checkbox stayed green in T_SETTINGS_SCREENS and T_SETTINGS_SWEEP_OFFLINE: the switch on screen would toggle the burn line. Fixed: fact checkboxes (every bool setting is the ref of exactly one checkbox) and a mutant in selftest_pyrelands_settings_sweep.py.

## verify
Acceptance test: python3 design/concepts/Pyrelands/version/blind_challenge/cycle_3/lane2/catch.py wind_checkbox_wrong_field T_SETTINGS_SWEEP_OFFLINE: rc 1 on 912c1ee157, rc 0 at the fix.

## criteria
The named command passes at the fix sha; the planted fault (lane2/planted_faults.json) is caught.

## refs
file: src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py
