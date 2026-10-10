# selftest fix4b 20261010

Skeleton. Scope: property_fabric, sand_buried_graphic, seashores, skeleton_burial, stun_scaling, sun_heat, track_grid, tool_metadata.

## Findings
All 8 selftests PASS in /home/mandrake/rm/foundry (property_fabric 23/23, sand_buried 10/10, seashores 8/8, skeleton_burial 37/37, stun_scaling 7/7, sun_heat 50/50, track_grid 15/15, tool_metadata 1/1 with the local JawaBench DLL).
The failures reproduced only in a scratchpad clone: dotnet.exe builds fail under the \\wsl.localhost UNC path (MSB3030 / project-not-found). tool_metadata reports UNMEASURED there because the gitignored JawaBench DLL is absent; run `python.exe bridgetools/build.py --gm` to produce it.
No code changed. A winbuild.stage_build conversion was tried and reverted per the coordinator.
