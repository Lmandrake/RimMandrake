# Live round 2026-10-19d (FOUNDRY, 536-mod donor-free list, home map RM_Cauldron AREAFIX2 save)

A2 L1 PASS: jawa/get_defs resolved 71/71 donor-port defs (every def in src/**/*DonorPorts*.xml plus the
port commits; typed ThingDef/TerrainDef/WeatherDef/HediffDef/IncidentDef/ThoughtDef), 0 notFound. a2_raw.json, ports_list.json.

A3 L2 PARTIAL: quicktest-style scratch tile maps (l1_donor_off_round.py mapgen) - plants AND animals on all 7, but each map
logs ONE GenStep NRE in MineralsFramework.ThingDef_StaticMineral.settlementDistProbFactor (other mod; same as 2026-10-18).
 TheRot 8 animals/1306 plants; TheForge 4/6586; Miasma 20/6980; TheSump 2/47 (+CombatAI NRE on a Molp-Lok settlement pawn
 at tile 376, other mod); RustCathedral 5/3969; Cauldron 0/1740 at -2.9C (cold outlier), 4/6867 at 30C; RUT_TheRot 4/5254.
 Roster probe: RM_Bileworm absent from RM_Cauldron and RM_Miasma rosters (known). mapgen1/2/3 json.

B UNMEASURED/partial: 26 of 26 TileMutatorDef/LandmarkDef ports resolve live (b_mutators_raw.json, shortHash included).
 Comparison with the ported save IDs and port_table.md predicted hashes NOT done: neither port_table.md nor any
 *PORTED_MUTATORS* save exists (and no _AREAFIX2 copy of one).

C PARTIAL: both weather suites are in the 536 running mods; PlanetGeometryDef RUT_WS_AshkarrGeometry resolves (full type name).
 Terminator front: maps on terminator-band tiles (MapInTerminatorBand True) carry permanent RM_WS_TerminatorFront, maps off it do not
 (~60 scratch maps, c_geo_*.json). Natural weather: fresh unlocked maps roll varied weathers (Clear/Rain/Fog/Windy/SnowHard/RM_SheenFall).
 UNMEASURED: nightside geothermal zero and aurora - MapInNightsideBand was False on every sampled tile (0 of ~90), and
 ComputeDensity/ArcFromSubstellar cannot be called via static_call (PlanetTile unsupported). Either this save's world has no
 tile past arc 117 or the band is unreachable; unresolved.
