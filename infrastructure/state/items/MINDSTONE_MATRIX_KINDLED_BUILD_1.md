Split from `LANTERNDEEPS_MINDSTONE_GALLERY_BUILD_1` (its "the mindstone head can be made from it" half). The mindstone itself (`RUT_Mindstone`) now exists and is mined only from the Deep gallery (UtinniPatches `RUT_GenStep_MindstoneGallery`).

Spec: `design/Jawa/worldbuilding/creatures/RUT_mechanoid_origin_canon.md` §2b and name rulings N1-N4.

## spec
- Recipe at the Droidworks reassembly harness: `RUT_Mindstone` + a droid head casing -> `RUT_MindstoneMatrix` (replaces the imported personality matrix; processor and databank still imported) -> `RSW_DW_Head_Mindstone`. Campaign tier (RUT_), so the recipe lives in the Utinni layer patched onto the Droidworks bench.
- `RSW_DW_AssembleDroid`'s head filter (which deliberately excludes the mindstone head today) and `DroidAssembly.KindForHeadDef` accept it: SAPIENT format, full needs; the first assembly is the Kindled's first making (an in-play event; nobody in-world knows the route, no lore entry).
- Wipe/spike immunity (RATIFIED): a wipe or spike attempt on a mindstone head fails with text.
- Open for BENCH/owner before building: the stat numbers "owed to B3" (no ruled stats exist; the head's current values are FOUNDRY's placeholder), and which pawnkind the Kindled assemble as (canon: no distinct chassis, body incidental).

## verify
- Mining a gallery vein, then the two recipes, yields a mindstone head; assembling it on a chassis makes a droid that resists a memory wipe with text.
