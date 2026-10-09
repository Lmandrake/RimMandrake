# Scene harness progress 2026-10-09 (FOUNDRY helper, SCENE_HARNESS_1)

- 00 skeleton; lib `src/RimMandrake/Utils/scenes/scenelib.py` built and committed (room, put, colonist, glow, temp, clear_area teardown). Tool list dump: `Transient/belt_scenes_tools_20261009.txt`.
- Facts measured: rects/cells are strings "x,z,w,h" / "x,z" (dict raises InvalidCastException); `jawa/clear_area dryRun=false` strips roof + destroys things (teardown); `jawa/kill_hostiles` exists; sky_glow_set is not durable.
- Live tier live_20261008b mods: FlowWorks, GimmeSomeSlack, LuminousPigment, Visibility, Watchers, WeatherSuite, Biomes (composed), Utinni patches, alphabiomes, VFE core.

## Results
(filled per scenario below)
