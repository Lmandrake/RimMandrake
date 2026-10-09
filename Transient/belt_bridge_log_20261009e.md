# belt bridge log 20261009e

Skeleton. Started Fri Oct  9 15:43:01 PDT 2026

## Steps
- 15:5x killed game PID 31248, deployed compose biomes (TerminalBiomes dir folded into Biomes)
- 16:0x tier acc_biomes applied, relaunched, bridge up in 60s (21 config errors baseline)
- Deploy: TerminalBiomes is composed into Biomes now: `deploy_custom_mods.py --compose biomes --apply` (26 files incl. other uncommitted DLL rebuilds in tree), game killed by PID, tier acc_biomes, steam relaunch, bridge up 60s, start_debug_game_ready.
- Map: biome_map(114501,"RM_SeabedFloor_GreySea",layer RM_SeabedLayer,surface_biome RM_GreySea,parent RM_SeabedSite); ship = set_substructure_batch 10x10 + spawn_batch GravEngine (no tank/thruster needed for the proof).
- CRUST_NEVER_STRANDS_1 A2 PASS on the real seabed floor: ProofState (args "0") crustDays=0.00 gate=accepted; ProofAdvance 16 -> rime=82 crust=33 gate=Salt crust jackets...; ProofTearFree -> crustRemoved=33 crust=0 gate=accepted tearFreeOffered=True.
- HAZARD_CLOCK_INSPECT_LINES_1 A2 PARTIAL: engine inspect line now present on seabed floor ("Crust still on the deck: 33 cell(s)" -> 0 after tear-free). Lamp burn line and twilight well line NOT read (Twilight not loaded this pass).
- GREY_TWILIGHT_SEABED_BIOME_GATE_1 A1 PASS (Grey gate); A2 PARTIAL (Twilight arm not exercised).
- HAZARD_CLOCK lamp line PASS on seabed Grey floor ('Burning steadily for 1 hour' -> 2 hours, WoodFiredGenerator grid + build_batch StandingLamp PlayerColony). Well line unread.
- CHILL_SUIT_SHELTER_RULE_1 warm arm PASS (real Chill floor, 9x8 roofed granite room, WoodFiredGenerator grid + 5 real Heaters, wearer DRAFTED in room, redrafted each 500t): ComfyTemperatureMin stayed -140 (charged) for 24,482 ticks at room temp 7..21C, > the 15,000-tick cold drain budget (maxChargeTicks 15000). Earlier cold-room runs depleted at ~15,000t exactly; a run where the wearer left the room accounted to ~15,000 cold ticks with ~4,000 warm in-room ticks undrained. Scripts Transient/belt_e_chill_warm.py, belt_e_chill_charger.py.
- Traps: an undrafted wearer walks out of the room and the "warm" arm silently becomes outdoor; pawn_get(pawn=id)["pawns"][0] is right but the no-arg listing omits scene pawns; power_net forcePowerOn=False does NOT switch a heater off.
- NOT shown: charger-behind-wall = no recharge, same-room charger recharges (suit never depleted in a warm run; heater cannot be held off). Needs a cold deplete phase with heaters unbuilt, then heaters added.
- Stop ~45 min. Bridge released. Game left UP on tier acc_biomes (15 mods), debug map dropped.
