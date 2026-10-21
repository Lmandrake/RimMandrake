# WORLD_MOUNTAINS_REDRAW_PEAKS_NOT_FIELDS

Owner 2026-10-20 (after seeing the soft hills in game): "Mountains look ok, better than the sharp stamp from before, but now they are barely visible. Mountains dont look like mountains they look like farm fields or something. Any chance mountains could actually look like mountains?" and "Can we study the other worldmap graphics mods to see what they do and how they do it? Maybe we just need to get some inspiration."

Context: soft hill atlas (1d9bb09c0, RM_WorldLook.ApplyHills, TerminalBiomes RM_Hills) swapped onto the four vanilla hill materials; vanilla hill quads are a 2x2 atlas with RANDOM ROTATION, so a lit/shaded side cannot follow the sun without a custom mesh/shader. Study of other world-map mods: design/Jawa/worldbuilding/worldmap_mods_study_2026-10-20.md (agent running at filing).

NEXT: read the study, then design peaks that read as mountains (silhouette, lit/shade split along the substellar sun direction, ridge texture, snowcaps where cold), decide whether a rotation-free mesh/shader is needed, build with Mod Settings toggle, preview offline, deploy and judge in game.

## Owner decision by card, 2026-10-20 10:12 PM PDT

Mountains: "Peaks lit toward the sun". Draw each mountain as a cluster of 3-5 peaks with a hard lit/shaded split, turned to face the substellar point (pass a per-tile angle toward the sun instead of the vanilla random rotation, as the study found ReGrowth passes a constant; see design/Jawa/worldbuilding/worldmap_mods_study_2026-10-20.md), snowcaps on cold lit faces, denser cells for Impassable, skip hills on road/river tiles, per-biome hill sets for hero biomes, Mod Settings toggle default on. Offline art first, preview, then deploy and judge in game.

## criteria

- A1 L0: World/RM_Peaks atlases pass `world_peak_decals.py check --src`; Biomes DLL builds with RM_WorldPeaks; Mod Settings toggle `worldSunPeaks` default on
- A2 L1: after a load with the 9ef991aa7 DLL, `RM_WorldPeaks.Info()` reports peaks drawn > 0 and no "[RimMandrake.Biomes] sun-lit peaks" warning in Player.log
- A3 L2: owner looks at Dew Horn and the night-side Crags in game and says whether mountains now read as mountains (offline preview: D:\ClaudeWork\rimmandrake\scratch\peakdecals\dewhorn_before_after.png)

## Built 2026-10-20 (helper)

Built fc14689e9 (+ DLL 9ef991aa7). Not done from the card: per-biome hero sets (the hook exists: World/RM_Peaks/<BiomeDefName>/<Kind>; no art shipped). Peaks are omitted on any tile with a road or river, as the card asked; if ranges look holed along rivers, set `skipRoadsRivers` false. The DLL could not be deployed while the game runs (file locked); textures are deployed.
