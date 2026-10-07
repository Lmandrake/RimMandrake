# Load errors fix 2026-10-07

- started
- scoping done; fixing Thurrock/DryAirBlower/textures
- 07:33 Thurrock comp (Secondary subclass) + DryAirBlower ticker: published 9f77e21e2 (DLL built, not deployed: game running)
- 07:45 art installed: Thurrock x3, Urraveth Wrapped+Bare x10, Borehulk east/north; queued jobs: RM_Borehulk_v2_south, item_yearningfruitharvested_v1, item_sweetlinetoken_v1 (Transient/load_errors_art_jobs_2026-10-07.json)
- 07:55 extra fixes: LiquidHose invalid fields, Ollathrix labelPlural patch, Hwelgrue race wildness, Arc damage int, SteamCatch DefOf default, impassable shot flags (blower, pumping station, liquid works). Earlier Thurrock/blower commit was orphaned by a peer reset; re-applied
