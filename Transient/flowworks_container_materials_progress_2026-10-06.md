# FlowWorks container materials progress 2026-10-06

- started: search for RM_Bottle/barrel/bucket defs
- 23:34 filed FLOWWORKS_CONTAINER_MATERIALS_1 (owner-said), item prose written
- 23:36 defs stuffable (bottle Leathery/Stony/Metallic, barrel Woody/Metallic), 6 recipes, C# MakeContainer carries stuff at 6 sites; XML validated 0 errors
- 23:42 DLL built (0 err); selftests 212/213, the 1 failure is UtinniPatches dump (RUT_MindstoneMatrix not in dump), unrelated
- 23:44 art: queued fwart_RM_Bottle_Stuffable_v1 + fwart_RM_Barrel_Stuffable_v1 (greyscale, owner_note); held glass render NOT installed; art comments updated

## rulings 23:45

Decisions taken by question card 2026-10-06 23:45: (1) buckets stuffable wood/metal/leather;
(2) material changes what a container holds — leather refuses hot/boiling and acid, glass+metal
hold anything, per-material capacity multipliers (plasteel barrels hold more); (3) any stone bottle
is labelled "glass"; (4) contained liquid's colour tints the container, empty shows material colour.

- started rulings pass
- 23:58 buckets stuffable (Woody/Metallic/Leathery), 3 recipes RM_Make_Bucket_{Wood,Metal,Leather}; XML 0 errors; queued fwart_RM_Bucket_Stuffable_v1
- 00:20 ruling 2 built: RM_ContainerMaterialMath (Verse-free) + RM_ContainerMaterialsExtension rules on bottle/bucket/barrel bases; LiquidDef.hot (boiling) + IsAcid; fill/drain/pour sites material-aware with JobFailReason; DLL 0 err; FlowWorks selftest 117/117 (6 new)
- 00:45 rulings 3+4 built: RM_CompContainerMaterial (stone reads 'glass'; filled shows LiquidDef.color via ForceColor, empty/dirty show stuff colour; inspect line for refusals); 15 liquid colours in generator; FlowWorks selftest 119/119; run_selftests 214/214
- 00:55 card 00:04: wooden buckets/barrels refuse acid, hold hot (XML holdsAcid=false); selftest 120/120
