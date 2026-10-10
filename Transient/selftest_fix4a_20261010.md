# selftest fix4a 2026-10-10

Cause (all 6): the wrappers ran `dotnet.exe run --project \\wsl.localhost\...` from an ext4 clone; MSBuild
fails MSB3030 (withSupportedRuntime.config "not found", UNC write/read race). Not a SettingsKit regression:
the retrofit commits did not touch these paths. Before: 6 FAIL (build). After: abyss_brood 127/127,
aftermath 18/18, colony_visibility 36/36, furnace_warmth 5/5, lore_stages 18/18, precious_caves 45/45.
Fix: stage on D: via winbuild.stage_build, then `dotnet run --no-build` on the staged csproj. No check changed.
