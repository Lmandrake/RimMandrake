# RIMMANDRAKE_CORRECT_PYRE_TEST_TABLE_SAYS_BODY_SIZE_SIX

test_table.json said furnace-beast body size 6 in the def; the def and the bar say 9

## spec
T_DEFS_OFFLINE's observes text (from version/pilot_throwaway/make_test_table.py) said 'furnace-beast body size 6 in the def'; the def holds 9 and leaf furnacebeast_warms says 9. Corrected in both. Polish (a record).

## verify
Acceptance test: grep -c 'body size 6' design/concepts/Pyrelands/version/test_table.json design/concepts/Pyrelands/version/pilot_throwaway/make_test_table.py prints 0 for both (watched print 1 before)

## criteria
The named command passes at the fix sha; the planted fault (lane2/planted_faults.json) is caught.

## refs
file: design/concepts/Pyrelands/version/test_table.json
file: design/concepts/Pyrelands/version/pilot_throwaway/make_test_table.py
