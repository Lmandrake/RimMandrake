# Full deploy + restart, 2026-10-06 (owner card 23:28)

- 23:32 start
- 23:33 bridge taken; game (trimmed list, PID 143900) killed
- 23:42 deployed 43 mods (221 files, 53 stale pruned) + composed Biomes (203 files, 15 pruned); KineticArms + FlowWorks held (uncommitted edits); ModsConfig = FULL.LATEST 610 + explosiveknockback = 611
- 23:42 launched via steam -applaunch 294100
- 00:06 load 1 reached bridge token ~00:05 (launch 23:42, ~23 min); killed per coordinator change of plan (more commits landed)
- 00:10 pulled 53186050e; deployed 8 more mods (48 files incl. KineticArms 28, FlowWorks) + Biomes 12 files; ModsConfig 612 (+kineticarms after knockback); relaunching
- 00:29 load 2 bridge token 00:29 (launch 00:10, ~19 min)
- 00:29 612 active after load; FeverWood still names RUT_RootCauseway/RUT_ToxinSealant (only stale pruned copies supplied them) -> 2 cross-ref errors
- 00:46 debug game: Grey Sea (Corrik, Karrud, Maalu) + The Chill (Heemin, Hoolen, Oovanam, Fessu) creatures, 6 catches, 8 plants render with the new art. No magenta, no vanilla cactus or meat. Shots are in Transient/greysea_ingame_2026-10-06/
- jawa/spawn_pawn, spawn_batch and map_info fail on this list: the JawaBench TerrainTools lambda class can't load because GimmeSomeSlack is not in FULL.LATEST. Used the debug-menu Spawn Pawn and rimworld/spawn_thing instead.
- The 4 Chill creatures disappeared with no corpse during a 15000-tick step. The Grey Sea ones did not.
- set_plants refused GlassVeilKelp and all 4 Chill plants on VolcanoSoil (terrain or conditions), so they were placed with spawn_thing.
- Log: Things/Item/RM_GreySea/RM_ElderUnknownWeapon has no texture. FeverWood still names RUT_RootCauseway/RUT_ToxinSealant, which only the pruned stale copies were supplying.
- 00:47 bridge released; game UP on 612-mod list
