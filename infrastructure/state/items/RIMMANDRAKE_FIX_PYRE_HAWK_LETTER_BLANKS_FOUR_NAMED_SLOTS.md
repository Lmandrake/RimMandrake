# RIMMANDRAKE_FIX_PYRE_HAWK_LETTER_BLANKS_FOUR_NAMED_SLOTS

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class MOD. Not fixed in
the sitting: the fix rebuilds FireEcologyHook.dll, and one visit judges one build, so every check would rerun on the new
build; the visit's wall time could not hold that.

## spec

The live sighting letter (chain firehawk_first_sighting_letter, 2026-11-20) read: "Fire-hawk is over your colony right
now with a live ember in its beak: A burning sprig of ember grass, snatched from the fire cells to the .\n\nIt is
carrying it to the ember grass, cells to the . ..." The distances and compass points are blank.

Cause (engine source, Verse/GrammarResolverSimple.cs): inside `{...}` the first `_` starts a sub-symbol, as in
`{PAWN_pronoun}`. FireHawkRewards.SendLetter passes `.Named("SOURCE_DIST")`, `"SOURCE_DIR"`, `"TARGET_DIST"`,
`"TARGET_DIR"`. Keyed `RM_FireHawkSightedText` uses `{SOURCE_DIST}` etc. The resolver looks for an argument `SOURCE`
(none) and asks the string `TARGET` for sub-symbol `DIST` (none). Each slot resolves empty, and Log.ErrorOnce "Could not
resolve symbol" fires once.

Fix: rename the four labels without an underscore (SOURCEDIST, SOURCEDIR, TARGETDIST, TARGETDIR) in
Source/FireHawkRewards.cs and Languages/English/Keyed/Pyrelands.xml together.

## verify

The offline test below goes green. Live: the letter text holds two numbers and two compass words.

## criteria

- No `.Named` label with `_` fills a Keyed `{...}` of the same name.
- The live letter names the source and the target distance and direction.

## Acceptance test

`python3 design/concepts/Pyrelands/version/in_game/visit_2/scripts/named_args_resolve.py`. Red now: "4 named
argument(s) with '_' that a Keyed string uses as a whole symbol", exit 1 (seen 2026-11-20 on 396d73530c). Green: "0 ...",
exit 0. Live after the fix: the firehawk_letter_words note's text holds no "cells to the ." (expected pass count 1).

## refs

file: src/RimMandrake/Pyrelands/Source/FireHawkRewards.cs
file: src/RimMandrake/Pyrelands/Languages/English/Keyed/Pyrelands.xml

## launch-checks

must-fail: python3 design/concepts/Pyrelands/version/in_game/visit_2/scripts/named_args_resolve.py

## Stage 6

Needs offline. The in-game check is `firehawk_first_sighting_letter`. Its live command:
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains firehawk_first_sighting_letter`.
The fixer records it UNRUN for Stage 6 with `maturation.py unrun` when it closes this item on the offline test.
(Added by the visit-2 steward run, RIMMANDRAKE_ROUTE_PYRELANDS_VISIT_TWO_FAILURES_BACK.)
