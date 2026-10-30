rimworld/get_game_info carries NO key naming the loaded save (measured 2026-10-30; keys: status, ticksGame, mapCount, selectedPawns, operation, state). To identify the map, read jawa/world_info_get (info.name + info.seedString) and compare with the save's <world><info> (canon start save: Ash'karr / safety). arena_lane's canary does this since 4fd0b4adf5.
home: .claude/skills/rimbridge
