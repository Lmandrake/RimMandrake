# SEA_FLOOR_AND_CATCH_PASS_1: blind judge verdict

Judge: CLAUDE_STEVEDESKTOP_OFFLINE4 (blind; I did not read DONE.md, BROADEN.md or the earlier JUDGE.md), 2026-11-11, at HEAD f74549e3d7.
Read: STATEMENT.md, NOTES.md, the item file `infrastructure/state/items/SEA_FLOOR_AND_CATCH_PASS_1.md` (spec, verify, criteria), and every file in `evidence/`.
I ran `evidence/census.py` and then `evidence/per_sea.py` myself. My scratch is in `D:\ClaudeWork\rimmandrake\judge_sfc\`. The rerun matches `per_sea_verdict.txt` exactly, apart from the sha/def-count header line.
I also ran my own label listing (`labels.txt`, which prints the floor cast and catch rows with their labels per sea).
The evidence contains no images, no video and no game output.

## The statement's one line

> Every sea describes BOTH its floor ... and its catch ...: the floor half is unbuilt across all four seas is done as the item file says, shown by fresh evidence.

**Verdict: false.** The static half holds. The item's own done-condition is a live experience, and nothing in the evidence shows it.

### What the evidence does show (true, statically)
- **Pairing.** Each catch row in all four seas (Scald 9, Grey 4, Twilight 14, Chill 9) has a floor body with the same label in that sea's `wildAnimals`. RM_Saal pairs with RM_Noohm, and both carry the label "saal". I confirmed this with my own parse (`labels.txt`), not only the builder's script. All catch defs are items, not races, so the GREENTIDE bug class is avoided.
- **Descriptions.** Each sea's description names both its floor ("reached only by gravship") and its shore catch. I checked every named species against the defs and found no catch named that is not in the table.
- **Floors wired.** Each sea has an `RM_SeabedFloor_<Sea>`, a generator and the fauna genstep, with floor animal density 2.4 to 4.5. The audit's F1 (floor never re-mirrored on a loaded save) appears fixed: `ResyncStaleFloors` exists at RM_SeabedLayer.cs:264, and the `seabed_descent_wiring` selftest has mutants for it.
- **Shore.** Each sea carries `RM_SeaShoreExtension`, and its shore terrain defs exist.
- **Tests.** `validate_patch.py` is clean on the 5 XML files it lists. The fresh run shows 8/8 selftests GREEN plus a direct `swim_shore_reach` PASS. These are offline, structural tests.

### Why the line is still false
1. **The item's criteria are unproven.** They read: *"Flying the gravship down to a sea's floor shows you the animals its fish descriptions promised, and fishing its shore pulls out the same creatures you dived past on the floor."* The evidence contains no flight, no floor map, no spawned animal, no fishing zone and no catch. The verify clause allowed "authored, not live-proven" only *"while QUICKTEST_RIVER_WATER_MISSING_1 stands"*. That item is now **done** (closed at a8a1b92c2), so the exemption no longer applies.
2. **The flight down is not working yet.** `SEABED_DESCENT_ASCENT_1` is BLOCKED at L0 (`rimflow show`), and none of its A1–A3 live levels has been reached. The verify clause asks for "a floor the gravship flies down to". So far that floor exists only as wiring.
3. **The Chill's fish exist twice.** `RM_TheChillCatch.xml` says the RUT_ catches "now ship here as RM_*Catch". Yet `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_PropaneLakeCatch_Items.xml` still defines RUT_Fessu…RUT_Zhiil and RUT_AuroraGlass, and `RUT_PropaneCatch_Refining.xml` references them. That is a second copy of one sea's fish economy, which the item's "Watch out" forbids. The standing ruling says wrong material is deleted along with its inbound references. Stale comments at RM_TheChill.xml:64 and RM_TheChillFloorLife.xml:24,43 still describe the RUT_ items as the shipped catch.
4. **Coverage of touched files is unproven.** The validate list has 5 files. The evidence never shows that these are all the files this pass touched (for example the catch/race XML, the Twilight patch, the wiring patch).

### Where the evidence flatters
- It is all self-consistency. The builder's own scripts parse the builder's own defs, and selftests check wiring. Nothing shows a player-facing result.
- `offline_chain_audit.md` marks every engine fact as `[engine-assumption]` (RimSage was unavailable). That includes the transpiler's cell argument, which decides whether the shore serves the right sea's table.
- The Twilight shore resolves through `PrimarySeaFor` on vanilla ocean terrain. The audit itself says the edge case of a tile that borders both vanilla Ocean and Twilight is INFERRED.

### What would settle it
- A live run per sea, or at least for the Scald plus one other. It should show the gravship landing on the floor tile (or, since live-testing a flyer's flight is ruled out, a dev-spawned floor map of that sea), the floor's spawned animal list, a fishing zone accepted on a land tile beside the sea, and a catch drawn from that sea's table.
- Deleting the RUT_ Propane catch file and its refining recipe references, and fixing the stale comments.
- Running `validate_patch.py` over the full diff of the pass.

These findings are filed as lesson `infrastructure/state/lessons/20261112T055625Z-CLAUDE_STEVEDESKTOP_OFFLINE4-sea-catch-judge-findings.md`.

would show: no
