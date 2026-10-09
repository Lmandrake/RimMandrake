# scenes - cheap live scenes over the bridge

`scenelib.py` is the library, `scenarios.py` the named scenarios (each prints one JSON line of evidence). Run under `python.exe` from the repo
root, never WSL python: `python.exe -u src/RimMandrake/Utils/scenes/scenarios.py chill_pump`. In code: `from scenes import scenelib as S`.

    with S.Scene("x", 100, 100, 9, 9) as sc:      # clears the rect on entry and exit (jawa/clear_area)
        sc.room(); sc.grid(); sc.put("StandingLamp", 5, 2); pid = sc.colonist(4, 6); sc.fuel(pid); S.run(600)

- Maps: `S.biome_map(tile, biome[, layer, surface_biome])` makes a map of any biome (a seabed floor needs `surface_biome` too); `S.drop_map(id, tile)` frees it.
- Build/act/read: `room put grid fuel colonist order power_on heat weather time_of_day` / `glow temp comp inspect find things`; raw `S.call(tool, **p)`.
- Time: `S.run(n)` (play_for at Ultrafast, ~400 ticks/s). `step_game_ticks` is 5-14 ticks/s here. `S.quiet()` stops raids that pause the game.
- Rects/cells are STRINGS "x,z,w,h". Kill pawns with `jawa/damage`, never `destroy_batch`. Pumps/wall items spawned by `spawn_batch` do not join a power net.
- Traps recorded in `Transient/belt_scenes_progress_20261009.md`; one bridge driver at a time; no flyer visual tests.
