# SCRUB_SETTINGS_WIRE_MASTER_CANNOT_GREY — Leaning Scrub settings: declare the master switch's dependents

Found by the four-biome readiness audit, `design/RimMandrake/four_biomes_readiness_2026-10-19.md`.

`python3 src/RimMandrake/Utils/settings_audit.py` reports `RimMandrake/LeaningScrub` OK, with the note
*"(6) draws a master switch but declares no SettingDependencies: its dependents cannot grey"*. The
kit from `SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST` is wired into GSS and the Pyrelands only.

## spec
- Declare `RimMandrake.Shared.SettingDependencies` for `RM_LeaningScrubSettings`, the way
  `src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs` (`Masters`) does: the master switch and
  every per-feature toggle that depends on it.
- Add the kit file to the csproj compile set, build with `winbuild.py LeaningScrub`, and commit the DLL
  with its `.srchash`.

## criteria
- `settings_audit.py` shows LeaningScrub `declared` with no notes.
- `selftest_leaningscrub*.py` pass. Seeing it grey in game is part of the next bridge sitting, not this item.
