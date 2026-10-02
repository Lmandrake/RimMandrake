# Art wiring pass 3 log

(skeleton)
## A. Messy Conduit (8 swapped, same path/name; strips cropped vertically to the cord bbox +1px and LANCZOS-stretched to 128x32 so the cord fills the ribbon like the placeholder; decals kept 128x128 vs placeholder 64x64; seams tile: edge diff < adjacent-column diff; EndFrayed_Live, SparkGlow, PowerStrip, ConduitTransparent stay placeholder (no real render). selftest_messyconduit 102/102.) Compare: Transient/messy_conduit_live_20261002/art_swap_compare.png

## B. Requeued 14 (v2; smelter south v3; hardwood v3; Multi=_south/_east/_north, Single=texPath.png)

| def | source job | dest | validator |
|---|---|---|---|
| RUT_VentSmelter | rut_ventsmelter_v3_south | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_VentSmelter_south.png | PASS 512x512 |
| RUT_VentSmelter | rut_ventsmelter_v2_east | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_VentSmelter_east.png | PASS 512x512 |
| RUT_VentSmelter | rut_ventsmelter_v2_north | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_VentSmelter_north.png | PASS 512x512 |
| RUT_VentForge | rut_ventforge_v2_south | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_VentForge_south.png | PASS 512x512 |
| RUT_VentForge | rut_ventforge_v2_east | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_VentForge_east.png | PASS 512x512 |
| RUT_VentForge | rut_ventforge_v2_north | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_VentForge_north.png | PASS 512x512 |
| RUT_VentKiln | rut_ventkiln_v2_south | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_VentKiln_south.png | PASS 512x512 |
| RUT_VentKiln | rut_ventkiln_v2_east | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_VentKiln_east.png | PASS 512x512 |
| RUT_VentKiln | rut_ventkiln_v2_north | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_VentKiln_north.png | PASS 512x512 |
| RUT_LivingBolt | rut_livingbolt_v2_south | src/RimMandrake/RustCathedral/Textures/Things/Pawn/Animal/RUT_LivingBolt/RUT_LivingBolt_south.png | PASS 256x256 |
| RUT_LivingBolt | rut_livingbolt_v2_east | src/RimMandrake/RustCathedral/Textures/Things/Pawn/Animal/RUT_LivingBolt/RUT_LivingBolt_east.png | PASS 256x256 |
| RUT_LivingBolt | rut_livingbolt_v2_north | src/RimMandrake/RustCathedral/Textures/Things/Pawn/Animal/RUT_LivingBolt/RUT_LivingBolt_north.png | PASS 256x256 |
| RM_GreatboleHardwood | rm_greatbolehardwood_v3 | src/RimMandrake/Greentide/Textures/Things/Item/Resource/RM_GreatboleHardwood.png | PASS 256x256 |
| RUT_SweetlineWool | rut_sweetlinewool_v2 | src/RimUtinni/AshkarrFlora/Textures/Things/Item/Resource/RUT_SweetlineWool.png | PASS 256x256 |

wired 14/14
