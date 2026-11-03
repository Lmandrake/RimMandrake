# C05: do the world generators do anything after world creation? (2026-11-03)

Item `GENERATOR_MODS_PROVE_INERT_AFTER_CREATION`. Owner, C05, 2026-10-10 (`OWNER_RULINGS.md`): *"You must validate that
they don't do anything after world creation. Experiments required."*

Instrument: `python3 src/RimMandrake/Utils/generator_inert_audit.py offline` reads each mod's shipped 1.6 DLL (Harmony
targets from attributes and from manual `Harmony.Patch` calls via an IL walk, classes the engine ticks or saves,
startup constructors) and the canonical start save (`canon.yml` `planet.start_savegame`). Live clause A2:
`python.exe src/RimMandrake/Utils/generator_inert_audit.py live` (`infrastructure/state/live_proofs/GENERATOR_MODS_PROVE_INERT_AFTER_CREATION.txt`).

| mod | verdict | why |
|---|---|---|
| My Little Planet (`oblitus.mylittleplanet`) | **INERT** | one patch, `Page_CreateWorldParams.DoWindowContents` (the Create World page); no runtime class; not in the canonical save's `<modIds>`, no type of it named there |
| Sensible Factions (`boots.sensiblefactions`) | **INERT** | one manual postfix on `WorldGenerator.GenerateWorld`; three developer-mode debug actions only; not in the save. Already retired (`world_remake_reinstate_list.md`, RETIRED-WAVE3) |
| Alien Worlds (`7f.alienworlds`) | **ACTIVE: stays** | patches `World.ExposeData` (writes the planet type into the save), solar output, rainfall curves, world draw layers, geyser counts on new maps; the save lists it |
| Alien Worlds – Tidally Locked (`7f.alienworlds.tidallylocked`) | **ACTIVE: stays** | patches the sun every frame: `GenCelestial` sun position, glow and light, `GenLocalDate.DayPercent`, tile temperatures |
| Faction Territories (`jaeger972.factionterritories`) | **ACTIVE: stays** | 15 ticking/saved classes (expansion, invasions, vassalage game components, world objects), 36 runtime targets; the save names 7 of its types. Whether expansion stays on is the separate C05 question, not inertness |

So only My Little Planet and Sensible Factions can leave the player list; neither is on `ModsConfig.SHIP.RULED_2026-10-20.xml`
now. The other three do things during play and stay; that is already the case on SHIP (owner 2026-10-21 on Alien Worlds: "Obviously.").
The live load (A2) confirms the two INERT ones by loading the canonical save without them.
