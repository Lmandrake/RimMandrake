# RIMMANDRAKE_GUARD_PYRE_DESCRIPTION_MILLENNIA_HALF_UNCHECKED

T_DEFS_OFFLINE checked engineered but not burned for millennia

## spec
Leaf biome_text_says_engineered: the player learns the savanna was genetically engineered AND has burned for millennia. Dropping 'for millennia' from the description stayed green. Fixed: fact biome_text_burned_for_millennia and a mutant.

## verify
Acceptance test: python3 design/concepts/Pyrelands/version/blind_challenge/cycle_3/lane2/catch.py desc_millennia_dropped T_DEFS_OFFLINE: rc 1 on 912c1ee157, rc 0 at the fix.

## criteria
The named command passes at the fix sha; the planted fault (lane2/planted_faults.json) is caught.

## refs
file: src/RimMandrake/Pyrelands/selftest_pyrelands_defs_offline.py
