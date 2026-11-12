# JUDGE: SEA_FLOOR_AND_CATCH_PASS_1 (blind, 2026-11-11, CLAUDE_STEVEDESKTOP_OFFLINE4 judge seat, HEAD 31fa0c1196)

I read STATEMENT.md, NOTES.md, the item file and every file in evidence/. I did not read DONE.md, BROADEN.md or the old JUDGE.md.
There are no images in evidence/. Everything is static or offline: def parses, selftests and validators.

## What I re-ran myself
- `selftest_sea_catch_alive.py`: ALL OK, exit 0. This matches offline_checks.txt.
- `per_sea.py` would not re-run as recorded. It needs a census JSON argument, and the evidence does not say which one. So I could not reproduce per_sea_verdict.txt directly. I spot-checked it against src instead:
  - The description names map to real labels: iridai, shimmer eel, gripping terror and lanternwhale.
  - `RM_Saal` and its body `RM_Noohm` are both labelled "saal".
  - `RM_GrippingTerror` and `RM_Lanternwhale` are in RM_TwilightSea's wildAnimals.
- Status of the items this one depends on (`rimflow show`):
  - `QUICKTEST_RIVER_WATER_MISSING_1` is **done**, so the item's "no live claim while it stands" exemption has lapsed.
  - `SEABED_DESCENT_ASCENT_1` is **built but BLOCKED**, because its live proof (prove_gravship.py) failed to set up.
  - `SEABED_FLOOR_GENERATORS_1` is done.

## The statement line
"Every sea describes BOTH its floor and its catch ... is done as the item file says, shown by fresh evidence."

The item's bar has two parts:
- **criteria:** "Flying the gravship down to a sea's floor shows you the animals its fish descriptions promised, and fishing its shore pulls out the same creatures you dived past on the floor."
- **verify:** for each sea, a shore verdict, a floor the gravship flies down to that is populated, every catch species either paired with a floor animal or given a reason, and validate_patch clean.

How each part stands:

| part | verdict | what shows it |
|---|---|---|
| Every catch species in all four seas has a living floor body wired into the sea's wildAnimals | true | per_sea_verdict.txt shows "rows lacking a living body: none" for all four seas (9/4/14/9 rows). selftest_sea_catch_alive passes against the shipped tree, mutants go red, and my re-run agrees. The non-fish rares (Silver, Chemfuel, salt cameo, lamp black, colo claw corpse) are loot, not species. |
| Every sea's description names both its floor and its catch | true | The four description strings are in per_sea_verdict.txt, the selftest has a "description names floor and catch" case, and the names resolve to real labels. |
| A shore verdict exists per sea | true (as authored) | Each sea has RM_SeaShoreExtension and its terrains exist. Twilight uses vanilla ocean. |
| validate_patch clean on touched XML | true | offline_checks.txt shows 7/7 OK. selftests_fresh_all.txt shows 8/8 PASS, including selftest_seashores (143 s). |
| "a floor the gravship flies down to" | cannot tell | Only static wiring is shown: selftest_seabed_descent_wiring and the audit's arithmetic check of FloorTileOf/SurfaceTileOf. The descent item itself is BLOCKED on its live proof. |
| "populated": animals actually spawn on the floor map | cannot tell | The audit's "~19 / 12.6 / 6.6 / 3 animals" is computed from density, not observed. No generated floor map was ever looked at. |
| Fishing the shore pulls out the same creatures | cannot tell | No fishing zone was placed and nothing was caught. The shore reaching the land map is inferred from code. |

**Overall line: cannot tell.** The evidence shows the defs are authored and consistent. The item's own criteria describe what a player sees, and none of it was observed. The live exemption was conditional on `QUICKTEST_RIVER_WATER_MISSING_1`, which is now closed. The builder's own last commit says "BLOCKED on the live step".

What would settle it, on one save and one sea tile per sea:
- A bridge state read of `Find.CurrentMap.Tile.Layer` before and after a gravship descent.
- A pawn census of the floor map, listing the catch-species bodies by defName.
- On a land tile beside the sea:
  - the RM_SeaCoast mutator,
  - a fishing zone accepted,
  - one catch whose item is in that sea's table.

## Staging and flattery
- Every check is a static parse of the repo's own defs, built by the builder's own scripts. That shows consistency, not behaviour.
- offline_chain_audit.md reports a HIGH finding (F1: the floor layer is never re-mirrored). Its fix is visible only as selftest mutants (ResyncStaleFloors). Nothing has run it on a save.
- The audit also says selftest_seashores and three fuzz tests crashed for environment reasons. The later selftests_fresh_all.txt reruns selftest_seashores green but leaves out the three fuzz tests. Those still have no verdict.

would show: no
