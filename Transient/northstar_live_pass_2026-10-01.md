# Northstar live pass 2026-10-01

- 17:57 start
- 17:57 read docs; mods: Aftermath Antiquities Droidworks FlowWorks Inhabited JawaIonWeapons Ninefold PawnFlavor Pits(orphaned) Pyrelands ResearchRetag ShipMemory StarWarsRaces StructureInjections; no Graffiti listed
- 17:58 FlowWorks prep done (swap+deploy+compose), Steam launch issued
- 17:58 game up (35s), running FlowWorks
- 17:58 FINDING: python.exe run() dies at modlist_swap (no fcntl on Windows python). Workaround: Transient/ns_wrap.py no-ops swap/deploy/compose/restore; swap+deploy+compose from WSL beforehand, restore from WSL
- 18:00 FlowWorks REFUSED pre-game (validated must-show lines unclaimed; known). Pyrelands: run needs a Playing map first (runner does not start one) -> prove_quicktest_world.py precedes run
- 18:01 Pyrelands (DRAFT checklist) ran: RED(state), 0 surprises, 0 aborts, bland=True all chains; failures = mod-content (RM_FE_Weather_AshFall absent, set_terrain 0 cells) not envelope. Wrapper also stubs rimflow verify (fcntl) and dumps Transient/modcheck/<Mod>_situational_summary.json
- 18:02 JawaIonWeapons RED(state): 0 surprises 0 aborts, bland, chains def_wiring/flesh_buildup PASS; 4 FAILs are content/test (see Transient/ns_summ_JawaIonWeapons.txt); no burn hediffs/missing-pawn error recurrence
- 18:04 ShipMemory RED(state): 0 surprises 0 aborts; 2 PASS, 1 FAIL (no letter after 700 ticks; content)
- Aftermath RED(state): 0 surprises/aborts. FINDING (envelope vs test conflict, control run pending): chain battle_lifecycle_repelled calls jawa/storyteller_fire RaidEnemy -> fired=false canFireNow=false; helpers.storyteller_off sets threatScale=0 + allowBigThreats=False (helpers.py:168-175) so the test's own deliberate raid is blocked. Needs a per-chain allow-threat opt-in.
- Droidworks RED(state): 0 surprises/aborts; 7 PASS chains, fails are content (ChargeNimbus absent, BoltResentment 0, trait extension, module personality, price shift).
- Inhabited RED(state): 0 surprises/aborts; place_and_roster 5 PASS; fate_and_stock stock_dumped FAIL (log tag missing, content) + 3 UNMEASURED upstream.
- Ninefold RED(state): 1 surprise (mental_break in chain mental_break_started = the test's own induced break, i.e. FALSE surprise; recorded with png+sidecar in Transient/modcheck/surprises/20261001T180903, did NOT abort, chain PASS). Other fails content (satiation log tags).
- PawnFlavor RED(state): 0 surprises/aborts; 3 PASS chains; fails are def readbacks (content).
- ResearchRetag GREEN: 2/2 chains PASS, 0 surprises, bland.
- StarWarsRaces RED(state): 0 surprises/aborts; 1 PASS chain; fails content (24 vs 38 genes, namer).
- StructureInjections GREEN: 3/3 chains PASS, 0 surprises.
- 18:17 Antiquities RED(state): 0 surprises/aborts; chain1 UNMEASURED = tick budget enforced (asked 95000, cap 60000, BudgetExceeded) -> legit envelope refusal, suite needs chunking/raised cap; chain2 PASS
- Step d sweep (Transient/ns_sweepcheck*.py): kill by id on spawned Rat: removed as live pawn, neighbour Rat 2 cells away undamaged (no hediffs), fires 0->0, MEASURED. Corpse removal via destroy_batch works when the tracked x,z is the real spawn cell (spawn_pawn row has top-level x,z, NOT position); my first attempt tracked a wrong cell and left a corpse, sweep still reported left=[] (it only re-reads live pawns, never corpses).
- 18:18 CORRECTION: Aftermath control run WITHOUT --situational fails identically (storyteller_fire canFireNow=false at tick 1) -> NOT an envelope false-block; pre-existing. (control summary: Transient/modcheck/Aftermath_control_nonsituational_summary.json)
- NORTHSTAR_BLAND_TILE_1 (claimed, left open): feasible. world_tile_export (csv, 8 MB, ~5 s) -> filter Flat + AridShrubland/Desert + swampiness 0 + 15-30 C -> 89 candidates; world_tile_get(tiles=N) shows mutatorCount/roadCount/riverCount; tile 4375 has 0/0/0. world_tile_map_generate(tile=4375) built map index 1 in seconds (250x250, mapFinalize ok) BUT it arrives with 47 wildlife pawns (Cougar, Megasloth, Rat...) and 16753 things, and no colonists (they stay on map 0). To make it a test map: set_current_map, destroy_bulk factionlessAnimals, colony_found / spawn colonists there. Ruin presence not measured (list_things on map 1 not run). Scripts: Transient/ns_blandtile*.py.
- Game killed, full modlist restored, bridge released.

## Summary
Verdicts (all --situational --policy abort; envelope bland in every chain, 0 aborts fired anywhere):
FlowWorks REFUSED (pre-game, validated must-show unclaimed) | Pits ORPHANED (no mod folder, not run) | Graffiti not in status list |
Pyrelands RED 0 surprises | JawaIonWeapons RED 0 | ShipMemory RED 0 | Aftermath RED 0 | Droidworks RED 0 | Inhabited RED 0 |
Ninefold RED 1 surprise (false: its own induced mental break; recorded, no abort) | PawnFlavor RED 0 | ResearchRetag GREEN 0 |
StarWarsRaces RED 0 | StructureInjections GREEN 0 | Antiquities RED 0 (95000-tick chain UNMEASURED by tick budget, cap 60000).
All REDs are content/test failures, not envelope-caused. Blockers to default: (1) modcheck run cannot run under python.exe at all
(modlist_swap/rimflow import fcntl) -> wrapper Transient/ns_wrap.py; (2) runner never starts a Playing map; (3) validated mods refuse
(shows= unclaimed); (4) no true abort has been exercised live (no real hazard occurred), so abort path is unproven live; (5) Antiquities needs chunking.
