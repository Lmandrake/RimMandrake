# RimMandrake: Warscar (Scarlands) — validation walk
subject: src/RimMandrake/Scarlands  (packageId `mandrake.rm.warscar`)
deps: `mandrake.rm.creaturebehaviors` (modDependencies, plus Odyssey and Harmony). Fold-aware: folded into `mandrake.rm.biomes`, active under the composed name 'RimMandrake: Baroque Biomes' (Biomes.compose.json).
list: a tier carrying Warscar (or the composed biomes mod) + Creature Behaviors, all five DLCs, plain open map (the suite builds its own broken-turret site)
status-hint: SCARLANDS_MECHANICS_2 and the WARSCAR_* items (TURRETS_TRACK, TOTCHAK_WAKES, OLD_TONGUE, HOSPICE_DESERTERS, RAINBOW_POOLS, FREE_TIER_BODY, SETTLING_WEATHER, GEIGER_CHOIR, MARK_TRADE_BUILD, CHATRAK_SNAP_BUILD, LOOSENED_PANEL_BUILD). Script: `src/RimMandrake/Scarlands/validation.py`. NEVER RUN LIVE. Live-UNMEASURED targets are marked (UNMEASURED): the last live run (Transient/modcheck/live_queue/situational_rerun/Scarlands_summary.json) could not judge them without a generated Warscar map.

Sources: `About/About.xml`, `Source/RM_WarscarMod.cs` (settings class RM_WarscarSettings), `RM_CompTurretAim.cs`, `RM_Totchak.cs`, `RM_OldTongue.cs`, `RM_Hospice.cs`, `RM_ReactionPools.cs`, `RM_Chotrix.cs`, `RM_Settling.cs`, `RM_WarDustUses.cs`, `RM_GeigerChoir.cs`, `RM_WarscarMark.cs`, `RM_ChatrakSnap.cs`, `RM_LoosenedPanel.cs`, `MapComponent_WreckLichen.cs`, `Defs/`, items `SCARLANDS_MECHANICS_2` and `WARSCAR_*`.

## must be true
- Every def the mod ships (biome, flora, creatures, hediffs, buildings, items, recipes, research, jobs, sounds, genstep, deserter histories) is loaded in the running game, and the biome's density/difficulty/forage numbers, pawnkind race/combat/eco weights, hediff severities, workgiver priorities and research costs read back equal to the XML. → every_shipped_def_reads_back.every_shipped_def_is_loaded, every_shipped_def_reads_back.shipped_scalar_fields_match_xml
- The old-line turret trio (`RM_OldLineTurret`, `_Gun`, `_Bullet`) resolves live and the aim comp type loaded. → defs_resolve.old_line_defs_resolve
- A broken ancient turret beside a walking pawn has its barrel follow the mover and never fires; with `turretTrackingEnabled` off the tracking line is absent. → tracking.barrel_follows_mover_and_never_fires (UNMEASURED: the mover Goto never confirmed running)
- The Refit gizmo on a broken turret follows `turretRefitEnabled`, and the refit target costs Steel + ComponentSpacer 3 + RM_Etchant 10. → refit_gizmo.refit_gated_by_toggle
- `oldLineDamageFactor` and `oldLineCooldownFactor` scale the old-line turret at game start. → UNCOVERED: applied at startup only, no live reader; a changed value needs a restart
- The old-line turret firing at hostiles and the barrel's drawn angle. → UNCOVERED: needs a raid, power and eyes (owner/FOUNDRY live round, item WARSCAR_TURRETS_TRACK_1 criterion 2; barrel angle is visual)
- Totchak defs resolve; `totchakEnabled` gates them. → totchak_wakes.totchak_defs_resolve
- A totchak starts dormant in a ruin wall, wakes at a demolition inside `totchakWakeRadius`, eats ruin walls before player walls (`totchakEatsPlayerWalls`, `totchakBiteScale`) and lies down after `totchakGrazeDays`. → totchak_wakes.demolition_wake_and_wall_eating_order (UNMEASURED: needs a live Warscar map with ruins)
- Old-tongue defs resolve; `oldTongueEnabled` gates the panels. → old_tongue.old_tongue_defs_resolve
- Reading an inscribed panel needs Intellectual at `oldTongueSkillGate`, unlocks the set flags and swaps the chalk mark; `oldTonguePanelsPerMap` and `oldTongueRevealChance` set the panel placement. → old_tongue.skill_gate_and_set_unlock (UNMEASURED: needs pawns of two skill levels on a live map)
- Hospice defs resolve; `hospiceEnabled` gates them. → hospice.hospice_defs_resolve
- Kneeling chassis rings hold up to `hospiceIntactPerMap` intact chassis; the cradle revives in five stages of `hospiceStageDays`, each risky stage failing at `hospiceFailureChance` (limbs stage may `hospiceLashOut`); the deserter walk-in follows `hospiceWalkInEnabled` and `hospiceWalkInFrequency`. → hospice.five_stage_revival_and_walk_in (UNMEASURED: needs rings on a live map and a cradle job)
- Rainbow-pool defs resolve; `poolsEnabled` gates them. → rainbow_pools.pool_defs_resolve
- Pools (1 to `poolsPerMap`) cycle four phases over `poolCycleHours`; each phase yields its reagent; drawing the bloom burns and builds toxin scaled by `bloomDanger`; with `catalystEnabled` glower crust holds a phase and doubles the yield. → rainbow_pools.pool_phase_cycle_draw_and_catalyst (UNMEASURED: needs pools on a live Warscar map)
- Chotrix defs resolve; `chotrixEnabled` gates them. → chotrix.chotrix_defs_resolve
- A chotrix (up to `chotrixPerMap`) stays invisible, reveals for `chotrixRevealSeconds` when it strikes, ignores a group of two or more and flees. → chotrix.invisible_reveal_on_strike_and_lone_gate (UNMEASURED: needs a live Warscar map)
- A lacquered cloak (`lacquerCloakEnabled`) grants still-and-unseen invisibility while no hostile with sight is within `lacquerSeenRadius`; it persists through save and load. → chotrix.lacquered_cloak_still_invisible_persists_save_load (UNMEASURED: needs an equipped pawn on a live map)
- The free-tier body defs resolve (chatrak, tetchik, pallbearer, scar roach, wreck-lichen, glower, interim donors). → body.body_defs_resolve
- Species and seeder toggles `enableChatrak`, `enableTetchik`, `enablePallbearer`, `enableScarRoach`, `enableInterimDonors` apply at startup; `enableWreckLichenSeeder` places lichen beside ruins only; tetchik spawn only within 6 cells of glower; a butchered chatrak yields undyeable chatrak plate. → body.spawn_gates_and_lichen_placement (UNMEASURED: needs a live Warscar map)
- Settling defs resolve; `settlingEnabled` gates them. → settling.settling_defs_resolve
- Calm below `settlingCalmThreshold` for `settlingCalmHours` starts the Settling; wind above `settlingEndWind` for `settlingEndHours` ends it. → settling.calm_starts_and_wind_ends_the_settling (UNMEASURED: needs forced calm on a live map)
- Settled film lies only on unroofed cells; a roofed pawn takes no toxic buildup and an unroofed one does, scaled by `settlingToxicStrength`. → settling.film_roofed_and_toxic (UNMEASURED: needs live film and two pawns)
- With `liftFrontEnabled` the lift front crosses the map downwind and wipes film and tracks behind it. → settling.lift_front_wipes_film_and_tracks (UNMEASURED: needs a live Settling)
- With `warDustEnabled` a sweep job on a film cell yields `RM_WarDust` (more in crater bowls). → settling.war_dust_sweep (UNMEASURED: needs a live film cell and a pawn)
- With `warDustBlightCureEnabled` a grower carries one war dust to a blighted crop and cures it. → settling.war_dust_cures_blight (UNMEASURED: needs a sown zone with dev Blight and a grower)
- `ordnancePerMap` buried shells are film-free and inspectable after a Settling, and defusing one yields a shell. → settling.buried_ordnance_revealed_and_defusable (UNMEASURED: needs a live Settling)
- Choir defs resolve (ticks, wind on metal, projector hum, pool boil, captured tetchik, tetchik jar and its recipe); `choirEnabled` gates them. → geiger_choir.choir_defs_resolve
- Standing over thick glower ticks faster than bare slag, scaled by `choirTickDensity` and capped by `choirTickVolumeCeiling`; `choirVolume` is the one global volume; `choirReducedRepetition` jitters the clicks. → geiger_choir.tick_tempo_follows_glower_density (UNMEASURED: needs a live map with glower)
- The wind-on-metal layer (`choirWindEnabled`) is silent while the Settling runs and returns after. → geiger_choir.wind_layer_silent_during_settling (UNMEASURED: needs live ruins and a Settling)
- A caravan carrying `RM_TetchikJar` gets a message before a polluted tile (`choirJarWarnings`). → geiger_choir.jar_caravan_warning (UNMEASURED: needs a live world tile and a caravan)
- The Warscar mark defs resolve (`RM_WarscarMark`, `RM_WarscarMarkThought`); `markEnabled` gates them. → warscar_mark.mark_defs_resolve
- A colonist on a Warscar map accrues the mark at `markAccrualPerDay` and it pays the trade offsets (hacking, mech butchery, smelting) when `markTradeBonusesEnabled`. → warscar_mark.mark_accrues_and_pays
- Past 0.5 the mark never fades below 0.25 while `markFloorEnabled`. → warscar_mark.mark_floor_arms
- `markEnabled` off accrues nothing. → warscar_mark.mark_off_accrues_nothing
- Chatrak snap defs resolve (`RM_ChatrakIncubation`, `RM_Chatrak`); `snapEnabled` gates them. → chatrak_snap.snap_defs_resolve
- An armed scaria chatrak climbs the incubation stages: 0.2 incubating (plates hidden), 0.4 plates lifting, 0.7 off its feed, 0.9 circling, 1.0 the snap (permanent manhunter); `snapStageSpeed` scales the climb. → chatrak_snap.snap_stage_0_2, chatrak_snap.snap_stage_0_4, chatrak_snap.snap_stage_0_7, chatrak_snap.snap_stage_0_9, chatrak_snap.snap_stage_1_0
- A clean (not scaria) chatrak is never armed. → chatrak_snap.clean_chatrak_never_armed
- `snapEnabled` off arms nothing; `snapArmingHours` is the arming sweep interval. → chatrak_snap.snap_off_arms_nothing
- Loosened wall panels (up to `loosenedPanelsPerMap`) refuse below a deepening mark. → loosened_panel.below_deepening_is_refused
- At a deepening mark a loosened panel opens onto a sealed crate. → loosened_panel.deepening_opens_onto_a_sealed_crate
- `biomeRarityFactor` (0 = never generates on a new planet; worldgen-affecting) scales the biome's worldgen insertion. → UNCOVERED: worldgen-time only, needs a freshly generated planet (§4 boundary)
- `crossBiomeEnabled`, `crossBiomeEverywhere`, `crossBiomeBiomeList`, `crossBiomeCoverage` are reserved fields, persisted and exposed but wired to no mechanic yet. → UNCOVERED: a no-op by design (RM_WarscarMod.cs header comment), nothing to read
- The projector hum and pool boil sounds, the Warscar look, wind and ambience. → UNCOVERED: visual and audio, judge pass or owner
- The aerosol screen, deserter-hospice follow-ups and open-boast rite are not built. → UNCOVERED: items WARSCAR_AEROSOL_SCREEN_1, WARSCAR_HOSPICE_DESERTERS_1 follow-ups, WARSCAR_OPEN_BOAST_RITE_1 are unbuilt, nothing to test yet

## anti-guessing notes
RULED OUT: "tracking fails when no tracking line shows" — the pawn was never confirmed walking (live run 2026-10-03: curJob '(none)', the wait was a paused read), so no tracking line is expected; the component reports UNMEASURED, not FAIL (validation.py comment).
RULED OUT: "the refit target's cost is a bare row count" — the real shape is THREE rows (Steel + ComponentSpacer 3 + RM_Etchant 10); assert the named rows, not a count (validation.py comment).
RULED OUT: "the refit gizmo can be read from the bridge" — gizmo presence has no bridge reader; the toggle is read back so a dead setting still fails (validation.py comment).
RULED OUT: "a live-map-needed component that cannot run is a failure" — live-map-needed components report UNMEASURED, not FAIL (commit: Scarlands validation: ordered_job params fixed, refit check reads the current cost shape, live-map-needed components report UNMEASURED not FAIL).
RULED OUT: "AddOrReplace patches the turret's tickerType" — AddOrReplace does not exist in vanilla, so tickerType was never set; the turret patch uses PatchOperationConditional (commit: Load-log fixes (set A)).
RULED OUT: "the Settling has a wind direction to read" — 1.6 has no wind direction, the downwind is a fixed seeded one (commit: Warscar: the Settling ...).
RULED OUT: "chatrak trainability Simple" — it does not exist in Core, chatrak trainability is None (commit: Load-log fixes (set C)).
RULED OUT: "a Warscar BiomeDef with few tiles says the mod is broken" — a biome with zero tiles is the expected mid-migration state (CLAUDE.md); no check here reads tiles.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned.
