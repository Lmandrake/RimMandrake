# Worker notes: GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1

## Status
started

## Tools owed

## Build

## Commit

## Findings so far
- Spec = NEEDED_TOOLS in src/RimMandrake/Utils/northstar_driver/site.py (5 tools).
- Companion DLL is GITIGNORED (.gitignore:82 bridgetools/artifacts/) -> no DLL/.srchash to commit; source only.
- csproj globs .cs (no Compile Include list).
- Graphic_Random.SubGraphicFor uses thing.OverrideGraphicIndex ?? thingIDNumber; Thing.overrideGraphicIndex public + Scribed -> spawn_variant sets it pre-spawn (deterministic, no reroll).
- jawa/mod_inventory exists (ids+order+assembly names); running_mods adds Location+MVID+sha256.
- New file: JawaBench.BridgeTools/JawaBenchNorthstarTools.cs
- build started 08:36:17
- Build (python.exe build.py --gm, plan only): 0 warnings 0 errors; bundle clean; selftest_tool_metadata 1/1 (346 tools, DLL == source). NOT deployed.
- Tools: jawa/thing_graphic, jawa/spawn_variant, jawa/running_mods, jawa/glow_at (GroundGlowAt+PsychGlowAt; GameGlowAt gone in 1.6), jawa/site_state (reads + optional autoHome/storyteller/clearIncidentQueue writes).
## Remains
- Deploy (owner seat, game down: build.py --gm --apply) + live proof on a quicktest map; driver site.py still lists them in NEEDED_TOOLS.
