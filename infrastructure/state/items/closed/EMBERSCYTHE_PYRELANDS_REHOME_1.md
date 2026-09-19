# EMBERSCYTHE_PYRELANDS_REHOME_1 — rehomed RUT_Emberscythe into the Pyrelands mod

## ruling (owner, 2026-09-19 question card)
Marked "cut" on the Rot sheet, then on the follow-up card ruled MOVE, not cut:
it's Pyrelands fauna that only happened to ship inside RotSporeKit.

## done
`git mv src/RimUtinni/RotSporeKit/Defs/ThingDefs_Races/RUT_Emberscythe.xml` →
`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Emberscythe.xml` — content
unchanged (no donor class/comp/modExtension in it, so no dependency risk moving
mods). `WildAnimals_Pyrelands.xml`'s two comment blocks and
`cast_assignment.csv`'s mod column updated to the new home — they used to claim
"the gate is the BIOME's mod and nothing else" while the def still lived in a
Rot-only mod; that was false until this move, now true. Grepped RotSporeKit for
any remaining reference: none except `build_review_sheet.py`'s hardcoded review
row (an already-generated historical report, not live code — left alone).

`validate_patch.py --live` on both files: 0 errors (the two WARN lines on
`RUT_Emberscythe`'s texPath are pre-existing — vanilla Megascarab art inside a
Unity bundle, not scannable from loose Textures/, unrelated to this move).
`deploy_custom_mods.py --apply` on both mods: RotSporeKit pruned (1 file),
UtinniPatches deployed (2 files: the def + the touched patch) — both VERIFIED
in sync.

## no Rot spawn to remove
Checked: RUT_Emberscythe was never wired into any Rot biome's `wildAnimals` —
only into `WildAnimals_Pyrelands.xml` (0.05, matching the pre-move state). So
"ensure it no longer spawns in the Rot" was already true; nothing to remove
there. It keeps spawning in the Pyrelands, now with the def in the right mod.

## not done
A live restart to confirm the moved def resolves with zero cross-reference
errors — defs are parsed at startup only. Next cold load's log should show
`RUT_Emberscythe` loading clean from UtinniPatches and no dangling-key warning
from `WildAnimals_Pyrelands.xml`.
