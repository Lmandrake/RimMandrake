# RIMMANDRAKE_FIX_PYRE_ABOUT_PROMISES_WORLDGEN_SHIPPED_OFF

Pyrelands About.xml promised new-world placement the shipped switch withholds

## spec
About.xml said the mod 'places itself on newly generated worlds with no other mod required' while biomeGenerationEnabled ships off, labelled unsupported (his card 2026-11-13). Bar inv_art_and_text (descriptions). Fixed: the About text now says new-world placement is an unsupported switch, off by default; T_DEFS_OFFLINE gains fact about_no_worldgen_promise_while_off and a mutant. Found by blind cycle 3 lane 1 (text_fixed_about_does_not_promise_worldgen_that_ships_off); unchanged since cycle 2 (miss_of 2).

## verify
Acceptance test: python3 design/concepts/Pyrelands/version/blind_challenge/cycle_3/lane2/../lane1/blind_lane1_files.py  (rc 1 on 912c1ee157, rc 0 on the fix); python3 design/concepts/Pyrelands/version/blind_challenge/cycle_3/lane2/catch.py about_promises_worldgen_more T_DEFS_OFFLINE (rc 1 before, 0 after). Expected: rc 0 on both at the fix sha; watched fail on 912c1ee157.

## criteria
The named command passes at the fix sha; the planted fault (lane2/planted_faults.json) is caught.

## refs
file: src/RimMandrake/Pyrelands/About/About.xml
file: src/RimMandrake/Pyrelands/selftest_pyrelands_defs_offline.py
