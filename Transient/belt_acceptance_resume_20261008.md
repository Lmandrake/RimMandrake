Thu Oct  8 14:55:25 UTC 2026
start: resume acceptance sitting
14:59 LuminousPigment ran: 60 PASS, 1 FAIL (styling_lacquer_toggle), rest UNMEASURED; Ninefold-dependent rows unmeasured since Ninefold not loaded in tier. File Transient/acc_green/rerun_LuminousPigment.txt
14:59 LuminousPigment FAIL styling_lacquer_toggle = harness-layer (toggle gates UI only); validation.py now UNMEASURED. Ninefold rows need acc_green_min2 tier.
15:03 game killed, tier acc_green_min2 applied (25 mods), biomes composed+deployed; launching
15:14 game up on min2 (25 mods). LuminousPigment min2: 61 PASS, 1 FAIL stripping_the_garment_darkens_the_pawn (new vs min run; harness state suspected), Ninefold gods rows now measure; Ninefold first run timed out at 280s in ensure_playing_map
15:26 Ninefold fixed in validation.py (research candidate pick, deconstruct designation): research+repair+deconstruct PASS; birth next
15:30 Ninefold birth PASS; all Ninefold green across runs
15:37 LuminousPigment rerun on dirty map polluted (floor_baseline/stripping FAIL = leftovers, tracked=false glowingInDark=false so mod OK); regenerating map via qt.py and rerunning
PyrelandsMechanics rc=0 pass=7 fail=0 ALL_GREEN False FINDINGS 0
Stillsand rc=124 pass=0 fail=0 [stillsand] 08:46:17 zuurrik_below_threshold_dormant PASS 
Stillsand rc=124 pass=60 fail=0 [stillsand] 08:55:42 pour_blooms_on_sand PASS 
16:11 Stillsand full: 56 PASS 5 FAIL (defaults left dirty by my killed run: bloomOnPour False; zuurrik_strips_blood, pour_blooms, beam_burns, eruption). Rerunning those chains after --reset-settings
16:18 Stillsand chains rerun: 46 PASS, FAIL beam_burns_target (MUURROK_BEAM_NO_DAMAGE_1) and eruption_tunnel_then_mound (canFireNow False); zuurrik/pour now pass
16:22 CreatureBehaviors 83P/3F (bridge 30s timeouts in footprints), Greentide 54P/1F (clock stalled, modal?). checking modal
16:28 Greentide swallow PASS with belt_closer.py (closes recurring Dialog_NamePlayerFactionAndSettlement every 2s; stalls clock otherwise)
16:29 CB track_grid: walker_lays_prints FAIL (gravel took 25 prints control), invisible_walker_recorded_flagged FAIL (last print not flagged) -- unresolved, mod-or-harness. min2 tier DONE.
16:30 killed game, deployed WreckedMachines+GimmeSomeSlack, tier acc_l1x applied, launched
16:32 acc_l1x up (31 mods). L1x get_defs: WRECKED_DISTILLATION A1 3/3, WYYYSCHOKK A1 4/4, ACOUSTIC A1 5/5, SHIELD_MODS A1 4/5 (RUT_ShieldGenerator notFound), FALL_LINE A2 2/2, MOD_OPTIONS A1 defs 4/4 (needs settings read)
16:33 ShipShields def failed to load: needs Warscar (in biomes mod); acc_l1x tier lacked mandrake.rm.biomes -> added in modset_builder.py, relaunched
16:36 ShipShields About depended on retired mandrake.rm.warscar (stale Mods/Scarlands stub shadowed it) -> now mandrake.rm.biomes; deployed; relaunch
16:38 acc_l1x get_defs: all 6 resolve (SHIELD 5/5 after About dep fix). ShipShields fixed.
16:38 tier acc_harness applied + launched
16:44 acc_harness results: UnfinishedLine ALL_GREEN(21P); LuminousPigment settings_apply 8P; WreckedMachines 20P 1F(tiers_have_promised_shapes: wreckedRatio/kludgedRatio/refurbishedRatio never read) 1U; Droidworks 21P 1F(protocol_droid MakeTrader no trader) 1U; FallLineArrivals 10P 1F(vermin_burst: ShipVermin not in tier)
16:45 harness tier done (see above). FlowWorks tier applied + launched
16:56 FlowWorks suite ABORT: stale DLL (running assembly sha != repo e8bc2fe88aef, SluiceGate source landed w/o rebuilt DLL). Rebuilding via winbuild
## Final state 2026-10-08 ~10:10 PDT
- FlowWorks tier: DLL was stale vs source (SluiceGate landed unbuilt); rebuilt with winbuild, redeployed, relaunched; sha matched. Run output Transient/acc_green/fw_FlowWorks2.txt: repeated blocks; consistent MOD FAILs in the pulse engine vs oracle (E5 sinks, E6 rain, E2 determinism, G every-cell, E4 scheduled) -- real findings, unresolved.
- Not recorded via rimflow verify: results are mixed harness/mod and no outstanding criterion was cleanly passed this sitting.
