# Belt bridge2 20261009g

Scope: GimmeSomeSlack, FlowWorks, Baroque biomes. L0-L3.

## Milestones
- started Fri Oct  9 17:53:15 PDT 2026
- 17:55 killed game, deployed GSS+FlowWorks DLLs + composed Biomes (46 files), relaunching on same 15-mod list
- 17:57 L1 startup log harvested: FlowWorks RM_LiquidHose Graphic_Linked NRE (fixed in src, graphicClass->Graphic_Single+linkType Basic); ~20 Baroque member errors listed for a fix batch
- 17:58 GSS offline 8/8 PASS after fixing stale sprawlCap->loopBudget key in validation.py SHIPPED table; starting GSS --live --fresh-map
- 18:00 GSS --live --fresh-map 38/38 PASS (801 ticks) -> src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261009T180038.json
- 18:05 GSS aerial 22/22 (new M15d diagonal cut, M19m mixed-net tap) -> AERIAL_CUT_POINT_PRECISION_1 + POWER_TAP_MIXED_NET_CONNECT_1 verified done; published 4fca8a132
- 18:12 Baroque L1 fixes in src: LanternDeeps world-incident ops removed (Aurora/Eclipse/SolarFlare), Tollok bleedRate->BloodPumping capMods, SpecimenCabinet category, LureAwning categories, TheChill catch StackCount, LungerFry Graphic_Random. GSS HoseProbe census exposes layReason (H07 fails only in full H0 batch, passes alone). Rebooting to deploy.
- 18:15 published ee8e70ef3 (L1 fixes); relaunch log: XML/world-incident/category/meat/echeveria/Graphic_Linked errors gone. Residue: RUT_FoundrySalvageCache cross-ref+texture, Leather_Chitin/BlackChitin, SweetlineToken+YearningFruitHarvested art (artpipe has yearningfruit+salvagecache art), ash burnedDef (deliberate)
- 18:19 hose H00-H08: batch failures were the lead-out leaving the plot (layReason 'no room for the straight lead-out'); 6-cell margin in design_spec -> 9/9 twice. HOSE_BEND_TRACE A1+A2 verified. published 8b0c5b0e3
- 18:20 GSS probe now exposes spark set (liveEndsAll/sparkSet/OnScreen); added B4c intensity + B4d budget rows; rebooted; running live
- 18:27 ledger published ffb90c65; SPARK_EFFECT_BUDGET done (7da211099). Starting FlowWorks v2 offline+live
- 18:34 FlowWorks v2 live was 49/10: all from keep-last-cell (LIQUID_RECESSION_TOPOLOGY_1) vs an oracle still on the floor rule + E3b's 1-cell pond. Oracle models keep-last; W2R now 2 cells; toggle census 37. Offline+mock green; rerunning live
- LIQUID_RECESSION_TOPOLOGY_1 A1 live probe (Transient/.probe/fw_recede_topology.py, site 60,20): dumbbell pond 3x3+bridge+3x3
  (19 cells, cap 95) drained by a 36-cell channel; receded (60,20),(66,20),(60,22),(66,22),(60,21) = outer corners first,
  8-connected components stayed 1 every batch, bridge (63,21) never receded. PASS.
- FINDING (Transient/.probe/fw_channel_ctrl.py): a 6-cell limited pond (cap 30) feeding an 8-cell channel of depth 1/2/3/4
  drains exactly ~6 units then STOPS every time (stock 24.1, activeCellCount 4): recession removes the pond cells touching
  the channel inlet (edge, far from centroid), cutting the channel off with 80% of the stock stranded; near-inlet channel
  cells left dry. Same in the dumbbell (95 -> 74, channel half empty). Filed as a judgement item.
- 18:49 verified: FLUID_DISABLE A1 (probe, ff4d66e56), FLOWWORKS_SETTINGS_SCOPE A1 (screenshot Transient/belt_g_shots), SETTINGS_SCREEN_KIT A5 FAIL (no search/collapse on FlowWorks screen), GLOW_TANK A1 partial (unseeded). Filed POND_RECESSION_STRANDS_CHANNEL_1, BAROQUE_LOAD_RESIDUE_ERRORS_1.
- 18:50 SUPERDEEP_TARGET probe (live_probes/fw_superdeep_target.py) UNMEASURED: no bridge reader for a non-colonist's job/target, spawned gunner carried an EMP launcher; parked.
- 18:51 Baroque L2: prove_biome_quicktest over 27 surface biomes in batches -> Transient/belt_g_biomes/
- 19:00 27-biome quicktest: 0 genstep errors except RM_RustCathedral GenStep_Terrain NRE -> fixed (forced rocks lacked naturalTerrain), re-regen clean. World-texture misses noted on BAROQUE_LOAD_RESIDUE_ERRORS_1.
- verified: LUMINOUS_PIGMENT_SETTINGS_READOUTS A1, DIVING_SETTINGS_CONTRACT A2, CREATURE_BEHAVIORS_CONFIGERRORS A1 (settings text via rimworld/get_ui_layout includeOffscreen - reads the whole dialog without scrolling).
## Left for the next sitting
- CORD_STATIC_DYNAMIC_HANDOFF_1 A1: needs a per-strand draw counter in GimmeSomeSlackProbe (roofed pin, owner section differs).
- SUPERDEEP_TARGET_VALIDATOR_1 A1: needs a bridge read of a NON-colonist's current job/target (JawaBench tool) and a firearm kind.
- GLOW_TANK A1 seeded variant: no tool to fuel a CompRefuelable; A2 needs a FlowWorks tank + salt water.
- SETTINGS_SCREEN_KIT_1 A5 recorded FAIL: kit Draw() not adopted by any screen.
- Filed: POND_RECESSION_STRANDS_CHANNEL_1, BAROQUE_LOAD_RESIDUE_ERRORS_1.
