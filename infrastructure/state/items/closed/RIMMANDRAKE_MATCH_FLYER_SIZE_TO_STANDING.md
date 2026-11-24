## spec
Our flyers shrink (or swell) on takeoff: the flying flip-book is drawn at a size that does not match the standing adult.
RSW_Uvak (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Uvak.xml`) stands at drawSize 3.5 (adult life stage) and
flies at `flyingAnimationDrawSize` 1.0 with `flyingAnimationDrawSizeIsMultiplier` false, an absolute size: in game it would
drop to about 29% of its standing width at takeoff. Found by the Conductor's phone-art prep, 2026-11-14
(`D:\ClaudeWork\rimmandrake\conductor\phone_art_20261114\README.md`, Q1 side note); verified against the def and textures
by the BENCH builder the same day. Most SWBestiary flyers carry the same absolute 1.0 copied whatever their size.

Measured 2026-11-14 (draft check below, 40 flying PawnKindDefs in src/): 24 pass, 15 fail, 1 unresolved.
Ratio = flying drawn width / standing drawn width, where drawn width = draw size x the opaque-width fraction of the
east (else south) texture (frame 1 for flying), so canvas padding is accounted for. Tolerance: 0.75 to 1.5.

```
FAIL RM_Krizzak ratio 1.56
FAIL RSW_Beldon ratio 0.25
FAIL RSW_Bogwing ratio 0.72
FAIL RSW_Brezak ratio 0.20
FAIL RSW_CanCell ratio 0.54
FAIL RSW_Drexl ratio 0.20
FAIL RSW_Hawkbat ratio 0.53
FAIL RSW_PekoPeko ratio 0.30
FAIL RSW_Sacapillar ratio 0.50
FAIL RSW_Screecher ratio 0.45
FAIL RSW_Shyrack ratio 0.48
FAIL RSW_Thranta ratio 0.23
FAIL RSW_Tibidee ratio 0.12
FAIL RSW_Uvak ratio 0.29
FAIL RSW_Whisperbird ratio 0.50
UNRESOLVED RM_Kirruk (vanilla Chicken frames)
```

Krizzak is the one that grows (multiplier 1.6); its designer may judge wide wings worth it, in which case the check
names its exception with the reason. RM_Kirruk flies on vanilla Chicken frames (a vanilla texture, not measurable
offline here): the check must name it, never pass it silently.

Vanilla reference (Core + Odyssey defs, 2026-11-14): every vanilla bird flies at an absolute size of 1.25 to 2.4
against 0.7 to 1.4 standing, so the number itself is not the rule; the drawn body is.

## Acceptance test (draft)
An offline def check (a selftest under `src/RimMandrake/Utils/art/`, run by `run_selftests.py`): for every PawnKindDef of
ours with a flying animation, resolve ParentName, take the adult life stage's bodyGraphicData drawSize and texPath and the
flying frame 1 texture, compute the ratio above, and fail any outside 0.75 to 1.5 or any it cannot measure, unless the
row is in a named exception list with a reason. Seen red on today's tree: 15 fail including RSW_Uvak at 0.29. Planted
mutant: setting RSW_Uvak's flyingAnimationDrawSize to 3.5 makes its row pass; setting a passing flyer's to 0.5 makes it
fail. The draft that produced the table: `D:\ClaudeWork\rimmandrake\helpers\ek_owner_answers_20261114\artB\check_flyer_size.py`
(not tracked; the rule is all written here).

The fix per flyer is a def value (absolute size = standing drawn width over the frame's opaque fraction, or switch to a
multiplier). No live flight test (standing ruling: never live-test a flyer's flight); the size is a def fact.
Watch out: the Uvak wing frames are being re-cut (FLIER_AFTERNOON_EXPERIMENT_PROVE_STILL_TORSO); re-measure after.
