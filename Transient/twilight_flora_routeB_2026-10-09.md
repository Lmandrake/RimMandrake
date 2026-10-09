# TWILIGHTSEA_FLORA_PASS_1 Route B + comps — 2026-10-09 (BENCH helper)

## Status
started
- Reuse found: GenStep_GreySeaFloorDressing (DivingInteraction) = Grey's Route B pattern (adjacency placement after formations). Twilight skylights are NOT placed at mapgen: RM_MapComponent_WellLedger (TerminalBiomes) opens/closes wells at runtime -> gleamfloss/farwick hook into ledger Opened/Closed; tithemoss/tollhorn go in a new TerminalBiomes genstep registered by patch like RM_GenStep_TwilightChannels_Register.xml.
- Plan: (1) RM_GenStep_TwilightFloraDressing (order 905, after Plants) = tithemoss beside wild hoolimbre/noothelm; registered on BOTH Twilight generators (SeaDive + Seabed) by patch; biome gate accepts RM_TwilightSea or RM_SeabedFloor_TwilightSea. (2) WellLedger Opened/Closed hooks -> RM_TwilightWellFlora: gleamfloss on shaft cells (killed at close), farwick bud at end of 4-8 cell run from rim (killed at close), tollhorn 1-3 at rim per opening (accumulates where wells have opened = recurrence ground; judgement call). (3) RM_CompGloamurnBank (IThingGlower, CompTickLong): charges under an open well, lit only while discharging. (4) RM_CompWiltAboveGlow (CompTickLong): Rotting damage when GroundGlowAt(ignoreSky)>0.35. Two settings toggles.
- FLAG (pre-existing, not fixed): WellLedger + channels gate on map.Biome==RM_TwilightSea; seabed-layer floor maps have biome RM_SeabedFloor_TwilightSea, so no wells/channels run on the seabed path.
- wrote C# + defs + genstep + register patch; building
- build OK (0 warn/0 err); validate_patch 0 errors x3; running selftests
- selftests RED 2 FAIL + 1 CRASH of 347, none ours: bridgetools/selftest_tool_metadata (DLL tool surface vs source), UtinniPatches dump (RUT_JawaReturnTow not in load-14 dump), Utils/selftest_memwatch (TypeError). TerminalBiomes selftest PASS.
- Live checks owed: floor map gen shows tithemoss beside hoolimbre/noothelm; well open seeds gleamfloss/farwick bud/tollhorn, close kills floss+buds; gloamurn lights after its well closes; murkspindle under a skylight rots in ~2 days; settings window renders the two new toggles. Not deployed (game running).
