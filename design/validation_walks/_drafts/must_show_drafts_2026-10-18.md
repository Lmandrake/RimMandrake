# Draft must-show lines for validation walks without them — 2026-10-18

Drafted by agents per owner card 2026-10-12 ("Agents draft from your rulings, you react"; ledger OWNER.jsonl tsn 1791823038517053996). Every line cites its source; tick or strike. DRAFT ONLY: no `## north star` section was edited and nothing was validated. Scope: the 91 walks with no `### must show` (FlowWorks and FlowWorksRivers/RiverSteam skipped: FlowWorks is VALIDATED and under FOUNDRY). Per owner 2026-09-17, walks with no visual surface get no bar. Some lines rest on owner-ratified frozen sheets or card decisions rather than verbatim quotes; those are flagged in-line. Untested live shapes may fail today by design.

# part_00 — candidate `### must show` lines (DRAFT for the owner to react to)

Paths below are relative to `/home/mandrake/rm/bench/`. `B/` = `design/Jawa/worldbuilding/biomes/`, `I/` = `infrastructure/state/items/`. `OWNER.jsonl:N` = line N of `infrastructure/state/ledger/events/OWNER.jsonl`. "sheet" = a frozen definition sheet written "Owner + BENCH ... ratified" (owner-ratified prose, not a verbatim quote; marked where used). No repo file was edited.

## RimMandrake/TerminalBiomes
(the Chill, the Scald, the Twilight Sea, the Grey Sea)

### must show
- [ ] `scald_water_agitation_by_depth` — Scald water shows ripples/bubble agitation that differs by depth: margin calm, shallow a bit agitated, deep constantly agitated (source: owner, `OWNER.jsonl:36` ts 2026-09-25T19:16:03Z SCALD_WATER_AGITATION_FLECKS_1: "margin is calm, shallow has a bit of agitation, and deep has constant agitation")
- [ ] `scald_steam_weather_beautiful` — the Scald steam weather reads as beautiful and interesting, not a flat grey overlay (source: owner, `OWNER.jsonl:29` ts 2026-09-25T17:16:22Z SCALD_STEAM_WEATHER_DESIGN_1: "make the Scald steam weather really beautiful and interesting")
- [ ] `scald_art_not_simple` — Scald stockpile items look as lush and high-res as the rest of our art, with variants where possible (source: owner, `OWNER.jsonl:28` ts 2026-09-25T17:16:22Z SCALD_ART_UPGRADE_WAVE_1: "the art looks very simple compared to our other lucious high-res art")
- [ ] `twilight_golden_light_shafts` — Twilight sea-floor skylights show as literal golden shafts of long beautiful light reaching down to the floor (source: owner, `B/the_twilight_deep_content_2026-09-26.md:98` and `:607`)
- [ ] `twilight_kelp_alien_lustrous` — Twilight seaweeds are wild and alien-looking, in lustrous green and blue-green ("It's a pretty ocean") (source: owner, `B/the_twilight_deep_content_2026-09-26.md:98`, `:247`)
- [ ] `twilight_creatures_luminous` — Twilight creatures carry luminous balls, bladders or bioluminescent patches, so the floor is dim but lit by local illumination plus the moving shaft patches (source: owner, `B/the_twilight_deep_content_2026-09-26.md:98`, `:542`)
- [ ] `twilight_whale_shadow_overhead` — the shadow of the great whale analog passes over the Twilight floor (source: owner, `B/the_twilight_deep_content_2026-09-26.md:649`, "The shadow of the great whale analog would be welcome")
- [ ] `twilight_channels_read_as_riverbeds` — Twilight underwater rivers show as channel patterns in the terrain, like surface riverbeds (source: owner, `B/the_twilight_deep_content_2026-09-26.md:130`)
- [ ] `twilight_waveglass_named_and_looks` — the waveglass reads as the owner-approved look, labelled "waveglass" (source: owner, `OWNER.jsonl:83` ts 2026-09-26T23:40:58Z TWILIGHTSEA_FLOOR_PASS_1: "love what you made but just call it waveglass")
- [ ] `twilight_tethered_cage_farms` — Twilight farms may stand as floating cube or sphere cages on chains to the surface (source: owner, `B/the_twilight_deep_content_2026-09-26.md:1136`)
- [ ] `twilight_no_rain` — no rain falls on the Twilight Sea floor (source: owner, `OWNER.jsonl:856` ts 2026-10-16T19:00:41Z TWILIGHT_SEA_FIX_IT_RAINS_UNDERWATER: "Twilight Sea is a sea floor... no rain.")
- [ ] `grey_sea_has_fish` — fish are visible alive in the Grey Sea (source: owner, `OWNER.jsonl:80` ts 2026-09-26T17:20:50Z GREYSEA_FLOOR_PASS_1: "There should be fish")
- [ ] `grey_hull_crystallized` — a gravship parked on the Grey floor shows crystallized hull and frozen-shut doors (source: owner, `OWNER.jsonl:86` ts 2026-09-27T03:14:12Z TWILIGHTSEA_FLOOR_PASS_1: "The grey sea should crystallize the hull, freeze doors shut")
- [ ] `twilight_ship_sky_panes_on_hull` — Twilight sky panes lie on a parked gravship and need clearing (source: owner, same event `OWNER.jsonl:86`: "twilight drops sky panes on the ship that need to be cleared off")
- [ ] `chill_aurora_over_black_mirror` — the Chill reads as aurora curtains over a black mirror sea with blue flame running on the ice (source: sheet, owner-ratified, `B/the_propane_lakes.md:12`)
- [ ] `scald_cyan_glow_under_steam` — the Scald reads as a sea of fire's making: cyan glow under white steam (source: sheet, owner-ratified, `B/the_scald.md:14` and its `## 9` heading "Cyan glow under white steam")

### cannot show
- [ ] `scald_nothing_cold` — nothing in the Scald reads as cold (source: owner, `B/the_scald_underwater_flora_pass_2026-09-27.md:350`: "No, this is silly. No cold.")
- [ ] `scald_floor_not_barren` — the Scald floor is not barren (source: owner, `B/the_scald_underwater_flora_pass_2026-09-27.md:234`: "it should not be barren")

## RimUtinni/UtinniPatches
### must show
- [ ] `utinni_biome_worldtex_distinct` — each of our biomes' world-map texture is distinct from the others in colour and texture (source: owner, `OWNER.jsonl:1116` ts 2026-10-18T15:13:23Z BIOME_WORLDTEX_BUILD_EVERY_BIOME_A_FACE: "Make each of them distinct from each other in color and texture"). NOTE: owner called these placeholders to be refined later; bar is distinctness only.
- [ ] `utinni_biome_worldtex_matches_description` — each biome's world-map texture is appropriate to that biome's description (source: owner, same event `OWNER.jsonl:1116`: "read each of their descriptions and create something appropriate")

## RimUtinni/FactionSlate
no visual surface — no bar: a pure data patch (zeroes `startingCountAtWorldCreation` on 46 FactionDefs); the one visible effect is the Configure Factions page at fresh worldgen, which is out of scope (no worldgen) and has no owner words on its look.

## RimMandrake/TheRot
### must show
- [ ] `rot_pale_forest_with_heartbeat` — the Rot reads as a pale forest with a heartbeat of rot (source: sheet, owner-ratified, `B/the_rot.md:12`)
- [ ] `rot_giant_maggot_with_tentacles_and_eyespots` — the hwelgrue reads as a huge, slow maggot covered in small wriggling tentacles and eye spots (source: owner, `I/closed/ROT_HWELGRUE_GIANT_BUILD_1.md:7`; `OWNER.jsonl:195` ts 2026-10-02T17:44:23Z ROT_SCORING_SITTING_1: "Like a huge maggot slow maggot covered in small wriggling tentacles and eye spots")
- [ ] `rot_hybrids_from_our_creatures` — thozzik, illoth and brogg read as hybrids of our own creatures from other biomes, not terrain-animal hybrids (source: owner, `OWNER.jsonl:198` ts 2026-10-02T18:56:05Z ROT_RM_CAST_MIGRATION_1; `B/rot_bedazzle_review_2026-10-02.md:571`)

## RimMandrake/Stillsand
### must show
- [ ] `stillsand_huge_skeletons_on_sand` — huge skeletons lie on the sand (source: owner, `I/closed/STILLSAND_SKELETONS_TRACKS_1.md:6`, "Huge skeletons on the sand.")
- [ ] `stillsand_barren_tracks_of_nothing` — the sand around the skeletons shows barren tracks of apparent nothingness (source: owner, `I/closed/STILLSAND_SKELETONS_TRACKS_1.md:6`)
- [ ] `stillsand_rare_rock_has_precious_cave` — a rare rock outcrop is celebrated and almost always shows a precious cave (source: owner, `I/closed/STILLSAND_PRECIOUS_CAVES_1.md:9`)
- [ ] `stillsand_deep_sand_own_terrain` — deep sand pools are their own terrain type, plentiful in the Stillsand (source: owner, `B/stillsand_bedazzle_2026-09-27.md:441`: "They should be an entire terrain type... Muchly in the Stillsand")
- [ ] `stillsand_mirror_beam_attack` — the mirror-crested event creature's ranged attack is drawn as a mechanoid-style beam, from reflection of the sun (source: owner, `I/closed/STILLSAND_EVENT_CREATURES_1.md:29`: "use the beam attack style from mechanics due to reflections")
- [ ] `stillsand_fulgurite_real_not_tube` — fulgurite art looks like real fulgurite from actual lightning striking actual sand, not a simple tube or fantasy image (source: owner, `I/closed/STILLSAND_GLASS_LENS_CHAIN_1.md:87`)
- [ ] `stillsand_palette_varied` — the biome's sprites do not share one uniform palette (source: owner, `B/stillsand_bedazzle_cast_2026-09-30.md:49`: "Your color palette is too uniform per biome. Needs more variety.")

### cannot show
- [ ] `stillsand_not_a_simple_tube` — never a crazy simple tube or other fantasy image for fulgurite (source: owner, `I/closed/STILLSAND_GLASS_LENS_CHAIN_1.md:87`)

## RimMandrake/LongShade
### must show
- [ ] `longshade_perpetual_beautiful_sunset` — the sky and light read as a perpetual, beautiful sunset (source: owner, `I/LONGSHADE_BEDAZZLE_MECHANICS_1.md:11`: "A perpetual beautiful sunset.")
- [ ] `longshade_shade_gear_parasol_tent_shield` — parasols, shade tents and simple shields you can stand behind exist (source: owner, `B/longshade_bedazzle_cast_2026-09-29.md:133`)
- [ ] `longshade_shadespire_dull_green_husks` — the shadespire keeps its interesting husk-like fruits, in dull green without wild colour or frills (source: owner, `I/LONGSHADE_BEDAZZLE_CONTENT_1.md:40`)
- [ ] `longshade_vrekka_darker` — the vrekka is tinted a bit darker (source: owner, `I/LONGSHADE_BEDAZZLE_CONTENT_1.md:42`)
- [ ] `longshade_palette_varied` — sprites do not share one uniform palette (source: owner, `B/longshade_bedazzle_cast_2026-09-29.md:26`, same "palette is too uniform" quote)

## RimMandrake/Greentide
### must show
- [ ] `greentide_choked_with_foliage` — virtually no square is uncovered by lush foliage; the ground reads choked with foliage (source: owner, `I/closed/GREENTIDE_BIOME_DENSITY_1.md:8`)
- [ ] `greentide_understory_blocks_sight` — the understory plants are tall and broad enough that a colonist cannot see over or past them (source: owner, `I/closed/GREENTIDE_UNDERSTORY_PLANT_ROSTER_1.md:30`)
- [ ] `greentide_greatbole_reads_as_wood_blob` — the greatbole landmark is a blob of wood on the map whose outer edge reads as bark (source: owner, `I/closed/GREENTIDE_JUNGLE_TREE_ROSTER_1.md:20`: "a blob of wood on the map, representing a trunk so vast that you can't even see the tree in the game")
- [ ] `greentide_look_and_go_around` — landing on the map, the player looks at it and decides to go around (source: owner's acceptance bar, `B/greentide_risk_reward_2026-09-22.md:244`: "You look at the map when you land and decide to go around.")
- [ ] `greentide_illisk_shoal_of_toothy_fish` — the illisk reads as a shoal of toothy fish (source: owner, `I/closed/GREENTIDE_TERROR_REPLACEMENT_1.md:85`)
- [ ] `greentide_wasps_small_and_numerous` — wasps are very small and numerous, boiling out of hives attached to plants (source: owner, `I/closed/GREENTIDE_WASP_SWARM_1.md:9`)
- [ ] `greentide_steam_not_fog` — the jungle's weather layer reads as steam, not fog (source: owner, `B/the_greentide.md:77`: "Not fog: STEAM")

## RimMandrake/FeverWood
### must show
- [ ] `feverwood_giant_beyond_the_screen` — the Dianoga-class giant is too big to enter the screen; only its tentacles reach in to lash, grab or pull under (source: owner, `B/fever_wood_deep_and_mud_2026-09-23.md:54`)
- [ ] `feverwood_tentacle_sizes_and_types` — tentacles of different sizes and types emerge from the pools, all reading as one great elder being (source: owner, `B/fever_wood_deep_and_mud_2026-09-23.md:118`)
- [ ] `feverwood_placing_tentacle_visible` — a tentacle is occasionally seen coming up to place a new item (source: owner, `B/fever_wood_deep_and_mud_2026-09-23.md:118`: "a rare moment of a tentacle coming up and placing a new item")
- [ ] `feverwood_angry_pool_slender_tentacle` — an angered pool shows a special-looking tentacle, more slender and delicate than the others (source: owner, `B/fever_wood_deep_and_mud_2026-09-23.md:164`)
- [ ] `feverwood_birds_alien_not_parrots` — birds look alien, not parrots: membranous, hairy or weirdly shaped feathers (source: owner, `B/fever_wood_deep_and_mud_2026-09-23.md:420`)
- [ ] `feverwood_birds_swoop_dramatic` — birds are dramatic and beautiful, swooping across the crown (source: owner, `B/fever_wood_deep_and_mud_2026-09-23.md:264`)
- [ ] `feverwood_brathek_larva_not_drill` — the brathek reads as a wood-boring larva that rasps into trees, not a drill head (source: owner, Feverwood sheet 2026-10-08, quoted at `B/fever_wood_fauna_roster_2026-09-23.md:93`)
- [ ] `feverwood_ant_hives_are_dungeons` — ant hives read as dungeons in their own right, full of gross insect symbiotic relationships (source: owner, `I/FEVERWOOD_ANT_HIVE_DUNGEON_1.md:8`)
- [ ] `feverwood_destroyed_crown_does_not_fall` — a destroyed crown tree does not fall (interlocked above) (source: owner, `B/fever_wood_deep_and_mud_2026-09-23.md:366`)

## RimMandrake/Miasma
### must show
- [ ] `miasma_stranded_look_transitional` — surge-stranded creatures look transitional: gills going leathery, fins splaying into feet that do not quite work (source: owner, `B/miasma_fauna_roster_2026-09-23.md:178`)
- [ ] `miasma_scuttlers_in_numbers` — little armored scuttlers appear in uncountable numbers (source: owner, `B/miasma_fauna_roster_2026-09-23.md:65`)
- [ ] `miasma_giant_in_shallows_not_on_land` — the not-so-gentle giant lumbers in water, its creche in the shallows, and does not come onto dry land (source: owner, `B/miasma_fauna_roster_2026-09-23.md:221`)
- [ ] `miasma_muck_colour_gradient` — muck colour, trees and fauna sort along a fresh-to-brine axis across the map (source: owner, `B/miasma_flora_roster_2026-09-23.md:80`)
- [ ] `miasma_rotting_bed_exists` — decay cells become a rotting bed (source: owner, `I/closed/MIASMA_ROTTING_BED_CUISINE_1.md:5`; `OWNER.jsonl:208` ts 2026-10-02T22:56:14Z)

## RimMandrake/Wasteland
### must show
- [ ] `wasteland_just_lost_sunset_lightning` — the light reads as a just-lost sunset flickering with wrathful lightning (source: sheet, owner-ratified, `B/wasteland.md:10`)
- [ ] `wasteland_survivors_ugly_warty` — native life reads as ugly, warty and tough (source: owner, `B/wasteland.md:26`: "ugly warty life that was already tough enough to survive the waste products")
- [ ] `wasteland_middenshell_twenty_cells_wide` — the Middenshell is twenty cells wide (source: owner, `B/wasteland.md:36`)
- [ ] `wasteland_warcasket_primitive_tank` — a warcasket reads as a primitive tank around a person (source: `B/wasteland.md:49`, ruling quote "a primitive tank around a person")
- [ ] `wasteland_no_precipitation` — no snow or any precipitation falls on the Wasteland (source: owner, `OWNER.jsonl:903` ts 2026-10-17T03:35:16Z EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS: "Sump, Wasteland, and Flooded Canyon should NOT be snowing! No precipitation")

## RimMandrake/Scarlands
### must show
- [ ] `warscar_battlefield_still_legible` — the ground reads as a battlefield where the whole story is still legible, except who the enemy was (source: sheet, owner-ratified, `B/the_scarlands.md:15`)
- [ ] `warscar_rainbow_pools_reaction_not_life` — the rainbow pools are bright and pretty but read as reaction and acid, not life (source: owner, verbatim, `B/the_scarlands.md:237`: "The color isn't life, it's reaction and acid.")
- [ ] `warscar_hospice_droids_strange_insides` — the deserter droids are interesting cases whose bodies hold strange features from a slow death (source: owner, `I/WARSCAR_HOSPICE_DESERTERS_1.md:5`)
- [ ] `warscar_jurrox_ultra_gaunt` — the (renamed) jurrox in the Warscar reads as ultra-gaunt, wonderfully grotesque (source: owner, `OWNER.jsonl:698` ts 2026-10-16T12:16:39Z JURROX_MIGRATE_INTO_WARSCAR_GAUNT)

## RimMandrake/TheSump
### must show
- [ ] `sump_black_glass_under_dark_sun` — the tar reads as black glass under a sun that never rises (source: sheet, owner-ratified, `B/the_sump.md:12`)
- [ ] `sump_capstan_ropes_target_in` — the Blackline Capstan turret visibly lassoes an enemy and pulls it toward the turret without moving the turret (source: owner, `I/closed/SUMP_CAPSTAN_TURRET_BUILD_1.md:3`; `OWNER.jsonl:177` ts 2026-10-02T05:01:21Z)
- [ ] `sump_tar_belch_covers_terrain` — a tar pit belches a huge amount of tar out over the local terrain (source: owner, `OWNER.jsonl:1` ts 2026-09-24T13:42:41Z SUMP_TAR_BELCH_EVENT_1)
- [ ] `sump_no_precipitation` — no snow or other precipitation falls on the Sump (source: owner, `OWNER.jsonl:903` ts 2026-10-17T03:35:16Z)

### cannot show
- [ ] `sump_no_normal_life_in_tar` — no live normal creature is dug up from the tar (source: owner, `B/sump_fauna_roster_2026-09-24.md:75`: "Only truly ancient machines or assailants. No normal life can survive otherwise.")

## RimMandrake/BlueDesert
### must show
- [ ] `bluedesert_extremely_blue_from_afar` — the plain reads extremely blue from far away but colourless up close (source: sheet, owner-ratified, `B/the_blue_desert.md:11` and `:289`)
- [ ] `bluedesert_hydrocarbon_flora_only` — the flora are hydrocarbon plants only (source: owner, `B/bluedesert_flora_expansion_pitch_2026-10-02.md:13`: "Only hydrocarbon plants please.")
- [ ] `bluedesert_ice_sand_drift_deep` — ice-sand drift goes deep (source: owner, `B/bluedesert_bedazzle_review_2026-09-28.md:24`: "we need to do testing to make sure it goes deep")
- [ ] `bluedesert_palette_varied` — flora palettes are not uniform (source: owner, `B/bluedesert_flora_expansion_pitch_2026-10-02.md:22`)

## RimMandrake/WeepingStones
### must show
- [ ] `weeping_stone_sweats_on_cold_faces` — stone sweats on its cold faces, with everything alive or built crowding around to drink the wind (source: sheet, owner-ratified, `B/weeping_stones.md:13`)
- [ ] `weeping_rockfinger_long_terrible_shadow` — the rockfinger is scraggly and hardy, rooted on a rim, throwing a long terrible shadow (source: owner, `B/weeping_stones_flora_roster_2026-09-24.md:116`: "long terrible shadows from the rims of tall rocks")
- [ ] `weeping_dewgourd_large_melon` — the dewgourd is a large melon-like gourd (source: owner, `B/weeping_stones_flora_roster_2026-09-24.md:129`)
- [ ] `weeping_oasis_green_eye_in_flat` — a seep oasis is a green eye ringed in open flat nothing, impossibly lush (source: sheet `B/weeping_stones.md:77` and §9, owner-ratified; weaker than a quote)

# part_01 — candidate `### must show` lines (drafts from existing owner rulings; he reacts)

## RimMandrake/Webwork
- [ ] `webwork_jungle_threaded_with_web` — the biome reads as a jungle with web threaded through it, not as a bare silk carpet (source: ledger OWNER.jsonl:419 tsn 1791822902873060194, ownerSaid "Some silk carpet is ok but it should still look like a jungle with web shit through it.")
- [ ] `webwork_cables_main_structure` — thick powerful cables running through are the main web portions, with thinner local webs beside them (source: tsn 1791822902873060194, "Thick powerful cables running through are the main portions with thinner local webs")
- [ ] `webwork_fine_carpet_at_sites_only` — the finer silk carpet appears only at spider "sites", not across the whole floor (source: tsn 1791822902873060194, "the finer carpet where the spiders have “sites” they use")
- [ ] `webwork_canopy_shade_patches` — the trees above cast big shade patches (source: tsn 1791822902873060194, "the trees above should have shade canopy that produces areas of shade ... Big shade patches.")
- [ ] `webwork_sunlit_regions_bright` — sunlit regions shine and are clearly visible against the shade (source: tsn 1791822902873060194, "A bright sunlit regions should shine and be clearly visible.")

## RimMandrake/GelatinousSlime
- [ ] `titanoslime_titanic_green_slime` — a Titanoslime reads as a titanic green slime, far larger than ordinary creatures (source: items/TITANOSLIME_SLIME_BIOME_1.md:8-9, "I am now enchanted by the idea of a titanic green slime. So make one of those too as its own custom creature. The Titanoslime.")
- [ ] `titanoslime_fed_is_larger` — a Titanoslime that has eaten is drawn visibly larger than a fresh one, and stays larger (source: items/TITANOSLIME_SLIME_BIOME_1.md:11 "Is it possible to have a creature that gets larger as it eats?" + items/closed/TITANOSLIME_PERMANENT_GROWTH_LIVE_1.md:5 "growth is PERMANENT, not reversible", owner 2026-09-21)

## RimMandrake/TheForge
- [ ] `forge_open_lava_deadly_hot` — open lava reads as horrible, hot, deadly ground (source: items/FORGE_CYCLE_MECHANICS_1.md:3-5, "The open lava is horrible, hot, deadly.")
- [ ] `forge_steam_plumes_after_rain` — after the torrential rain there are huge plumes of steam (source: items/FORGE_CYCLE_MECHANICS_1.md:6-7, "There should be huge plumes of steam")
- [ ] `forge_vents_become_basalt_pumice` — lava vents are replaced by temporary basalt shingle and pumice chunk after the rain (source: items/FORGE_CYCLE_MECHANICS_1.md:7-8, "transformation of the lava vents to temporary basalt shingle and pumice chunk")
- [ ] `forge_glowing_cracks_before_remelt` — glowing cracks form on the rock covering before it melts back to lava (source: items/FORGE_CYCLE_MECHANICS_1.md:9-10, "Eventually glowing cracks form on the rock covering, and the whole thing melts back into lava again")
- [ ] `forge_rain_floods_low_ground` — torrential rain causes visible flooding (source: items/FORGE_CYCLE_MECHANICS_1.md:5-6, "torrential rains pour down, causing flooding")
- [ ] `dhoggur_swollen_three_times_size_fire` — a provoked dhoggur is drawn about three times as big and spews fire; an unprovoked one is not (source: ledger OWNER.jsonl:822 tsn 1792163490612412095, "if you mess with it, it swells with violent chemical reactions that make it three times as big and spewing fire (firespit)")

## RimUtinni/UtinniShell
- [ ] `shell_ui_helm_of_the_utinni` — the whole UI looks like being at the helm of the Utinni: old and worn, not brown rusted (source: design/Jawa/worldbuilding/ui_shell_spec.md:18-21, "The whole UI should look like you are at the helm of the Utinni. So it can look old and worn but not brown rusted.")
- [ ] `shell_buttons_not_rusty` — buttons are the grey-green gunmetal tech panel, not rusty (source: ui_shell_spec.md:59-60 and items/closed/UI_SHELL_SLICE_BUILD_1.md:43-44, "I love love love the tech panel you made. Rusty buttons are out.")
- [ ] `shell_vector_line_schematic_graphics` — the minimal look leans on vector-line schematic graphics common in Star Wars interfaces (source: ui_shell_spec.md:22-23, owner asked "to lean into the vector-line schematic graphics common in Star Wars interfaces"; sheet paraphrase of his request)
- [ ] `shell_text_legible` — UI text is legible; no Aurebesh-style font that hurts readability (source: ui_shell_spec.md:206 "owner's standing rule — skip a font that hurts readability"; sheet paraphrase)

## RimMandrake/AssailantSalvage
no sourced line found (searched ledger ownerSaid for salvage/assailant/landmine/airlock, items ASSAILANT_SALVAGE_FIRST_SCRIPT_1, SALVAGE_PALETTE.md, warscar cast doc; owner's "lots of wreckage" ruling, OWNER.jsonl:31 SALVAGE_WRECKAGE_EVERYWHERE_1, concerns the wreckage set, not this mod's props)

## RimMandrake/KineticArms
- [ ] `thump_blast_throws_farther_than_mortar` — in an ordered before/after sequence, a thump cannon blast throws a pawn visibly farther than a mortar of equal damage would (source: items/KINETIC_BLAST_WEAPONS_1.md:5-6, owner 2026-10-06 21:40, "Thump cannons throw farther... Kinetic Blast-type attacks")
(no further visual line: the ring fleck and the "moving wall" / "ejection gate" reads are agent text, owner decides, not his words)

## RimMandrake/Pyrinth
no sourced line found (pyrinth appears only in agent-written census/audit text; no ownerSaid or owner quote)

## RimUtinni/UtinniStatues
- [ ] `statues_feature_utinni_gods` — the Utinni statues' art features the Utinni gods and other cultural specifics of the Utinni experience (source: ledger OWNER.jsonl:32 STATUE_ART_EXPANSION_1, ts 2026-09-25T17:16:23Z, "Render specific Utinni art statues that feature the Utinni gods and other cultural specifics to the SW Utinni experience")
- [ ] `statues_flame_at_flame_points` — statue art has points where flames make sense, and a lit flame appears there (source: same event, "art ... that happens to have invisible points where flames would make sense"; the lit-flame half is his framing "tie that in to ... refueling" — flame fuelled by Sump / Helixian gas / manual refuel)
(cannot show: nothing rejected in his words except "The Steel Flame statuary art is a placeholder to replace", event title, agent-written)

## RimMandrake/RustCathedral
- [ ] `cathedral_circuit_board_maze` — the plateau reads as a complex, almost circuit-board maze of walls, structures and designs that scream of meaningful complexity and intention (source: design/Jawa/worldbuilding/biomes/the_rust_cathedral.md:44-46, "(owner)"; frozen sheet quotes him)
- [ ] `cathedral_bolts_dance` — living bolts look component-like and move in complex, strange, dance-like patterns (ordered sequence) (source: the_rust_cathedral.md:117-120, "(owner) ... complex, strange, dance-like patterns for no reason")
- [ ] `cathedral_almost_nothing_alive` — rust-dust drifts against the walls, heat shimmer as standing weather, almost nothing alive (source: the_rust_cathedral.md:44-48; sheet text, owner tag only on the maze phrase, weaker)

## RimMandrake/EnvironmentalHazards
(visual surface: Venomvine, Leachmoss, flame statuary, gas effects; lines below are the Venomvine and statuary ones his words reach)
- [ ] `venomvine_man_height_or_more` — venomvine stands man-height or more, standing out against smaller cover (source: design/RimMandrake/venomvine_design_2026-10-16.md:32-34, 2026-09-21, "Except for the venomvine, that should be man-height or more.")
- [ ] `venomvine_rich_varied_art` — venomvine art is rich and varied, with more than one kind visible, as the strange showpiece (source: venomvine_design_2026-10-16.md:36-37, 2026-09-29, "The art for the venomvine should be especially rich, varied, interesting... its the strange showpiece here."; :40 "I really like the different kinds of venom vine.")
- [ ] `venomvine_dripping_kind_distinct` — a dripping variant that is overproducing venom looks different from the plain vine (source: venomvine_design_2026-10-16.md:37-38, "Maybe one variant of it can be a dripping kind that is overproducing the venom")
- [ ] `venomvine_grows_abundantly_tall_dangerous` — in the Leaning Scrub venomvine is abundant and tall, reading as dangerous (source: ledger OWNER.jsonl:828 tsn 1792167263801507527, "the one plant that grows abundantly tall and dangerous")
- [ ] `venomvine_not_placeholder_graphic` — venomvine forms do not use the shared placeholder graphic (source: venomvine_design_2026-10-16.md:46, 2026-10-08, "STOP USING THIS GRAPHIC AND MAKE VENOMVINE!")
- [ ] `flame_statuary_flame_points` — flame statuary has flames that make sense at its flame points (source: ledger OWNER.jsonl:32 STATUE_ART_EXPANSION_1 ts 2026-09-25T17:16:23Z, "invisible points where flames would make sense"; :34 "the Flame statues")

## RimMandrake/NightsideIce
- [ ] `nightside_ice_dirty_not_blue` — the ice reads as dirty ice (white, with impurities), not pure blue ice (source: design/Jawa/worldbuilding/biomes/nightside_ice.md:52-53, "Not blue: dirty ice (owner's ruling). Ice only turns blue when it is very pure, clean, old and compressed")
- [ ] `nightside_ice_near_empty` — the biome reads as near-empty, almost nothing alive, no lush flora (source: the walk's own [S] "dirty ice, near-empty by design; owner decides" is agent text; owner-side sources: nightside_ice.md "No lush flora of the ordinary kind" sheet text and items/closed/NIGHTSIDEICE_RM_MOD_BUILD_1.md:11-14; sheet text, weak)
- [ ] `nightside_ice_no_snow_underfoot` — the interior shows no precipitation and no snow underfoot (source: nightside_ice.md:56-58 sheet text, "no wind ... and no snow underfoot"; weak, sheet not verbatim)

## RimMandrake/DivingInteraction
- [ ] `twilight_floor_lit_everything` — the Twilight Sea floor is beautiful and lit, with lots of lighted everything (source: ledger OWNER.jsonl:85 TWILIGHTSEA_FLOOR_PASS_1, ts 2026-09-27, "the beautiful lighted Twilight floor with lots of lighted everything")
- [ ] `grey_scald_floors_dark` — the Grey and Scald floors are dark on the bottom (source: OWNER.jsonl:85, "the Grey and Scald (dark on the bottom)")
- [ ] `twilight_floor_no_rain` — the Twilight Sea floor shows no rain (source: ledger OWNER.jsonl:856 tsn 1792177241295043368, "Twilight Sea is a sea floor... no rain.")
- [ ] `grey_sea_hull_crystallized` — on the Grey Sea floor the ship's hull is crystallized and doors are frozen shut (source: OWNER.jsonl:86 ts 2026-09-27, "The grey sea should crystallize the hull, freeze doors shut.")
- [ ] `twilight_sky_panes_on_ship` — on the Twilight floor sky panes sit on the ship and need clearing (source: OWNER.jsonl:86, "twilight drops sky panes on the ship that need to be cleared off")
- [ ] `scald_water_agitation_by_depth` — Scald boiling water shows ripples/bubbles: margin calm, shallow a bit agitated, deep constantly agitated (source: OWNER.jsonl:36 SCALD_WATER_AGITATION_FLECKS_1 ts 2026-09-25, "margin is calm, shallow has a bit of agitation, and deep has constant agitation"; note: may belong to the Scald-water walk rather than this one)
- [ ] `dive_ship_flies_to_sea_floor` — diving shows the ship flying to a new planetary layer, the sea floor, with no hatch (source: OWNER.jsonl:165 SEA_DIVE_HATCH_RETIRE_1 ts 2026-10-02, "Now the ship just flies to a new planetary layer called sea floor.")
- [ ] `dormant_droids_on_floor_not_ship` — dormant droids lie on the sea floor, not inside the ship (source: OWNER.jsonl:50 SEA_DIVE_MAPS_BUILD_1 ts 2026-09-25, "it's just on the sea floor, NOT in the ship")

## RimMandrake/CrackedLands
- [ ] `cracked_flood_plants_visibly_grow` — water-soaked plants visibly get bigger on screen over a sequence (source: design/Jawa/worldbuilding/biomes/the_cracked_lands.md:271-274, 2026-09-06 owner, "water-soaked plants grow VISIBLY — actually getting bigger on screen")
- [ ] `cracked_soaked_plant_intimidating` — near a water-soaked plant the scene reads as threatening ("OMG, what's going to happen?") (source: the_cracked_lands.md:275-276, "'OMG, what's going to happen?' should be the feeling near any water-soaked plant.")
- [ ] `cracked_no_buildings_on_canyon_floor` — no settlement or building stands on the canyon floor (source: the_cracked_lands.md:184-186, owner 2026-09-06, "No structure on the canyon bottom — higher tiers, NEVER the floor")
- [ ] `cracked_no_precipitation` — no rain or snow falls on the canyon (source: ledger OWNER.jsonl:903 tsn 1792208116047391807, "Sump, Wasteland, and Flooded Canyon should NOT be snowing! No precipitation")
- [ ] `cracked_soil_in_shade` — the shaded canyon bottom shows actual soil with plants in it, not sand (source: the_cracked_lands.md:117-118, "Soil in the shade (owner's ruling): actual soil, not just tough plants that grow in sand and shade")

## RimMandrake/LuminousPigment

- [ ] `press_welded_look` — the Deepfire press reads as a press and an alchemical setup welded together. (source: OWNER ownerSaid ts 2026-09-25T21:44:15Z, `infrastructure/state/ledger/events/OWNER.jsonl:44`: "And it should look like a press and an alchemical setup welded together.")
- [ ] `glow_takes_dye_colour` — a coated wall/floor/furniture/worn item glows in the colour of the dye it was painted (the pigment adds only the glow, no colour of its own). (source: OWNER.jsonl:40 ts 2026-09-25T21:32:39Z, his typed message: "colour from the normal dye object, pigment supplies glow")
- [ ] `night_glow_is_ordinary_light` — at night a coated thing lights its surroundings like a normal light, dim and steady, not a special effect. (source: OWNER.jsonl:40 "night visibility = normal lights"; `design/RimMandrake/deepfire_luminous_pigment_spec.md:13-14`)
- [ ] `worn_item_lights_wearer` — a pawn wearing a coated item has a light sphere around them. (source: OWNER.jsonl:40 "personal objects -> light sphere around the pawn")
- [ ] `later_coats_only_brighten` — a second or third coat on the same thing is brighter, not a different or new effect. (source: OWNER.jsonl:44 note text "later coats only brighten"; OWNER.jsonl:40 "extra uses only brighten")

## RimStarWars/BeastLairs

no sourced line found (visual surface: `RSW_BeastNest_Large` 3x3 art; the walk's own [S] "denned-in mound" is an agent line with no owner words behind it)

## RimUtinni/ResearchRetag

no visual surface - no bar (rewrites research tech level, cost, prerequisites and tab assignment; no textures, terrain, pawns or effects)

## RimMandrake/CreatureBehaviors

no visual surface - no bar (shared behaviour engine of ~50 mechanics; its creatures' art belongs to the biome mods that carry them, behaviours in motion are not stills)

## RimMandrake/Warcasket

- [ ] `warcasket_primitive_tank` — the warcasket reads as a primitive tank around a person: bulky, heavy, not a sleek suit. (source: BENCH.jsonl:528, Wasteland sitting, owner typed, "'a primitive tank around a person'"; `design/Jawa/worldbuilding/biomes/wasteland.md:46-47`)
- [ ] `cask_bay_lead_lined_hardpoint` — the cask bay reads as a lead-lined, shielded hardpoint on the ship. (source: FOUNDRY.jsonl:1393, "the lead-lined cask bay (gravship touch) - a shielded hardpoint", recorded as owner-approved at Wasteland sitting turn 2)

## RimStarWars/Shokk

- [ ] `ollathrix_wyyyschokk_body_plan` — the Ollathrix (skinned as Wyyyschokk) is a gigantic spider: a big rounded abdomen behind a head with mandibles, on long jointed clawed legs. (source: `design/RimStarWars/canon_references/wyyyschokk/description.md:43`, `## Must show`, grounded in owner visual correction 2026-09-13)
- [ ] `wyyyschokk_colour_layout` — blue-grey body (not brown), blue-black legs, clustered black eyes. (source: description.md:44, owner ruling 2026-09-13: "blue-grey body, yellow-orange abdomen cross, spiky bristle tufts, blue-black legs, clustered black eyes")
- [ ] `wyyyschokk_abdomen_cross` — a bold yellow-orange cross marking down the centre of the abdomen, the brightest element. (source: description.md:45, owner: "a regen without the abdomen cross fails review")
- [ ] `wyyyschokk_bristle_tufts` — spiky bristle tufts around the rim of the abdomen. (source: description.md:46)
- [ ] `wyyyschokk_not_generic_brown_spider` — NEGATIVE, cannot show: a generic brown hairy spider, or a tarantula without the cross, in all three life stages. (source: description.md:48, the 2026-09-13 brown-spider render is the named negative)

## RimUtinni/VaultDungeons

- [ ] `vault_concentric_rings` — a placed vault reads as concentric rings: breached outer works, a garrison ring (the fight), a core (the payoff). (source: `infrastructure/state/items/closed/VAULT_DUNGEON_CONCEPT_1.md:30-31`; `design/Jawa/worldbuilding/dungeons_arc_spec.md:28` lists the concentric grammar doctrine as RULED. A ruled doctrine, not a verbatim quote)
- [ ] `vault_v3_frozen_rakata_scene` — the type-3 vault shows frozen Rakata still believing a war is on, a scene rather than an encounter. (source: `design/Jawa/reconciled_lore/03_deep_history.md:119`, canon triad, owner 2026-08-15 per VAULT_DUNGEON_CONCEPT_1.md:15-20)

## RimUtinni/DesertFixtures

no sourced line found (visual surface: `RUT_WindowAdobe` texture; the walk's [S] "reads as an adobe-style window" is an agent line, no owner words found)

## RimStarWars/TrophyCraft

no sourced line found (visual surface: fang pendant on the RSW neck layer; no owner words about its look found)

## RimStarWars/GraffitiImperial

- [ ] `imperial_stencil_crossed_cog` — the stencil reads as a crossed-out Imperial cog, an anti-authority mark in the RSW Aurebesh/cog variant. (source: `design/RM_GRAFFITI_SCOPE_WIDENING.md:205-207`, "Anti-authority stencils - RULED 2026-09-25 by card: feature", plus line 1 status "RSW Aurebesh/cog variant")
- [ ] `imperial_stencil_stencil_register` — the art is in the UK stencil register, not wildstyle lettering. (source: `design/RM_GRAFFITI_SCOPE_WIDENING.md:192`, "Art register reference - RULED: NYC subway wildstyle and UK stencil"; Stencil form per line 269)
- [ ] `imperial_stencil_asemic_text` — any tag text is letter-shaped strokes that spell nothing. (source: `design/RM_GRAFFITI_SCOPE_WIDENING.md:251`, fork F5 "ruled: asemic", card 2026-10-09)

## RimMandrake/SolarMirrors

- [ ] `mirror_lights_shadow_patch` — a mirror's beam makes a lit patch inside an otherwise shaded area, reading as light inside a rendered shadow. (source: owner typed 2026-10-04 "I like this. Should be its own RimMandrake mod. Solar Mirrors." at `design/RimMandrake/solar_mirrors_mod_design_2026-10-04.md:5`, on N6 "They throw light into shadows", `design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md:292-293`; item `infrastructure/state/items/SOLAR_MIRRORS_BUILD_1.md:47` A8)
- [ ] `mirror_field_frozen_array` — the ancient Long Shade field reads as an old array of sun-tracking mirrors frozen at the angle they last held. (source: ideation.md:292-293 as accepted by the owner's 2026-10-04 "I like this", chose the full puzzle-map W3)

## RimMandrake/OasisMaker

- [ ] `oasis_placement_green_red` — placing the machine shows a green/red area guide for valid ground (shaded terrain near rocks). (source: owner ruling typed 2026-09-24, `design/RimMandrake/oasis_maker_machines_spec.md:27-33`: "placed near shaded terrain near rocks ... green red area selections. Like placing water based generators.")
- [ ] `oasis_grows_slowly_ring_by_ring` — converted ground spreads outward from the machine in rings over time, not all at once. (source: oasis_maker_machines_spec.md:27 "create oases slowly"; ring ladder in the same spec)
- [ ] `oasis_heart_real_water` — a finished oasis has real shallow-water pool terrain at its heart. (source: oasis_maker_machines_spec.md:6-8, "decision taken by question card"; not his words)

## RimMandrake/ExplosiveGrowth

- [ ] `burst_leaves_ring_of_sprouts` — a dry-biome plant that bursts at peak maturity is gone, with many sprouts surrounding where it stood. (source: OWNER.jsonl:829 ts 2026-10-16T16:21:16Z ownerSaid: "at peak maturity they sometimes burst/die, resulting in many additional sprouts surrounding them")
- [ ] `wet_ground_has_visible_water` — any wet ground in frame is explained by visible water (pipe, hose, spill, channel, river, flood); there is no wet-soil overlay. (source: `design/RimMandrake/explosive_growth_rulings_2026-10-16.md:56`, GM1: "Nothing stays wet for long without an obvious reason.")
- [ ] `rain_leaves_puddles` — after rain stops, puddles mark the wet ground for a few hours. (source: OWNER.jsonl:895 ts 2026-10-17T03:28:21Z, OQ-9 "A few hours, shown by puddles", by card)
- [ ] `riverbank_plants_writhe` — plants on the river's water/mud cells grow and churn continuously. (source: rulings.md:32, W2: "(1) and the plants continuously grow and writhe there"; motion, so judge by a short capture)

## RimUtinni/WasteRun
no visual surface — no bar (quest/letters/goodwill; walk's own [S] says "none; letters and goodwill are readable").

## RimUtinni/UnfinishedLine
no sourced line found (quest chain with a ruin site and wild droids, but every owner ruling found in `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` and the UNFINISHED_LINE_* items is lore/mechanics, none states how the hall or droids must look).

## RimUtinni/ShipMemory
no visual surface — no bar (a hidden-item reveal flag and one letter; the only [S] is menu/letter contents, not textures, terrain, pawns or effects).

## RimUtinni/Rites
no visual surface — no bar (five research projects; the only [S] is a greyed research-tree node, a UI state with no owner words behind it).

## RimUtinni/RestrainingBolts
no visual surface — no bar (a goodwill-cap worker, no art).

## RimUtinni/PawnFlavor
no visual surface — no bar (backstory/trait/def-label text; belongs on the `must read` axis if he wants one).

## RimUtinni/LongHunger
### must show
- [ ] `longhunger_massive_dune_worm` — the Long Hunger reads on screen as a massive dune-style sandworm, not a small prop-sized object (source: owner 2026-09-02 verbatim, "create a NEW massive dune-style sandworm with its own mythos", `infrastructure/state/items/closed/SANDWORM_MYTHOS_BUILD_1.md:3-6`; item records it is a 1x1 building on placeholder art, `SANDWORM_MYTHOS_BUILD_1.md:57-77`, so this bar is expected to fail today)
- [ ] `longhunger_not_krayt_look` — it is visibly a different creature from the Krayt dragon (source: same quote, "Krayt dragons deserve their own treatment", `SANDWORM_MYTHOS_BUILD_1.md:3-6`)

## RimUtinni/LanternDeeps
no sourced line found (the walk is RETIRED, `design/validation_walks/RimUtinni/LanternDeeps.md:2-9`; mod was rebuilt as `RM_LanternDeeps`, and the owner words found in `infrastructure/state/ledger/events/OWNER.jsonl:161-168` are about animals, rites and the hoist, not how the cavern or geode must look).

## RimUtinni/IshkoDarkLandmarks
no sourced line found (three landmark icons are a visual surface, but the only owner words are "Author 2-3 new" in ledger `ISHKO_DARK_LANDMARKS_1` file event, ts 2026-08-31T06:52:44Z, which say nothing about appearance; icons are reused Ash'karr art per `infrastructure/state/items/closed/ISHKO_DARK_LANDMARKS_1.md:35-40`).

## RimUtinni/FallLineArrivals
### must show
- [ ] `fall_lab_rat_is_white` — the rat that arrives is a white lab rat (source: owner verbatim "actual terrestrial rats might be fun to fall from a ship as a white lab rat. That is all. So keep it.", `design/Jawa/worldbuilding/biomes/fall_line.md:218-220`)
- [ ] `fall_lab_rat_falls_from_ship` — the rat is shown arriving from the sky in a pod, not standing on the map as ambient fauna (source: same quote, "fall from a ship"; "as a fall arrival, not as ambient biome fauna", `fall_line.md:222`)
- [ ] `fall_vermin_only_at_wreckage` — in the deep desert, wreck-nest creatures are seen only at or coming from a fallen wreck, not wandering open sand (source: owner verbatim, "arrive with injected content from inhabited from wreckage", `fall_line.md:189-193`)

## RimUtinni/EmpirePursuit
no visual surface — no bar (a forked ScenPart pursuit rule; the walk's [S] says "none of substance").

## RimUtinni/EggReckoning
no sourced line found (the egg and the hatched spider are visible, but the only owner rulings in `src/RimUtinni/EggReckoning/About/About.xml` and `WEBWORK_EGG_RECKONING_QUEST_1.md` are mechanics: hatch window, goodwill, fixed age).

## RimUtinni/DroidRepairJobs
no sourced line found (the walk-in droid and customer are visible, but owner ruling 2, 2026-09-06, quoted at `infrastructure/state/items/closed/DROID_REPAIR_FOR_PROFIT_EVENTS_1.md:11-14`, is about events and part quality, not appearance).


Paths below are relative to `/home/mandrake/rm/bench/`. `file:N` = line number.

## RimUtinni/Doctrine
no visual surface — no bar (XML patches that hide a build-menu entry, keep droid FleshTypes non-organic, scale butcher yield and postfix a crash; no texture, terrain, pawn or effect; the one `[S]` step is a menu-absence check on a third-party building). No owner words about how it should look were found.

## RimUtinni/BirthHatchDemo
no visual surface — no bar (demonstration mod with a placeholder colour tint only; its own walk says "no bespoke art"; the audit marks it ELIMINATE-COMPLETELY, so no bar is worth drafting).

## RimUtinni/Atlas
### must show
- [ ] `atlas_is_ship_shaped_graphic` — the Atlas tab is a graphical display laid out in the shape of the Utinni vessel, not a list or table (source: `design/RimMandrake/utinni_discovery_achievements_design_2026-10-02.md:313`, owner typed 2026-10-02: *"they are arranged in a beautiful graphical display that looks like the utinni vessel."*)
- [ ] `atlas_undiscovered_is_cryptic_riddle` — an undiscovered entry shows as a cryptic riddle card, not its plain answer (source: same file:313, *"Cryptic riddles that you can click on for flip over hints."*)
- [ ] `atlas_click_flips_to_hint` — after clicking a riddle card, the same card shows a hint in its place (source: same file:313, *"click on for flip over hints"*)
- [ ] `atlas_unlocked_offers_lore_clickthrough` — an unlocked entry offers a click-through to its lore (source: same file:316, owner typed: *"you can "click" through to it once you unlock it."*)
### cannot show
- [ ] `atlas_never_pushes_lore` — no prompt, popup or banner forces lore on the player when an entry unlocks (source: same file:316, *"Nothing gets in your way, ignorable if undesired."*)

## RimUtinni/AshkarrWeatherSuite
### must show
- [ ] `nightside_aurora_maximized` — on a nightside-band map the aurora is visibly far brighter and more colourful than vanilla's aurora (source: `design/Jawa/proposals/weather_suite_deep_design.md:40`, owner 2026-09-02: *"Beautiful, and use the Aurora graphic effect but maximized in brightness and color. It should be awesome!"*; restated `infrastructure/state/items/closed/WEATHER_SUITE_SLICE_1.md:182`)
- [ ] `terminator_front_reads_as_storm` — a map in the terminator band shows a standing storm front (lightning, a storm sky) rather than clear weather (source: `design/Jawa/proposals/weather_suite_deep_design.md:36`, owner 2026-09-02: *"I like this! … the turbulence is real"*; weakly sourced — his words approve the storm, not its look; the walk's `[S]` step 11 asks for the storm wall)

## RimStarWars/WeatherSuite
### must show
- [ ] `nightside_aurora_maximized` — a nightside-band map shows an aurora visibly far brighter and more colourful than vanilla's (source: `design/Jawa/proposals/weather_suite_deep_design.md:40`, owner 2026-09-02: *"Beautiful, and use the Aurora graphic effect but maximized in brightness and color. It should be awesome!"*; `infrastructure/state/items/closed/WEATHER_SUITE_SLICE_1.md:182`)
- [ ] `terminator_front_reads_as_storm` — a map in the terminator band shows a standing storm front (source: `design/Jawa/proposals/weather_suite_deep_design.md:36`, *"I like this! … the turbulence is real"*; weakly sourced as above)
(Both lines need a `PlanetGeometryDef` instance, i.e. the RimUtinni tier loaded; on the minimal list the walk proves them inert.)

## RimStarWars/Sarlacc
### must show
- [ ] `sarlacc_swimmer_is_devourer_modelled` — the Stage-I swimmer reads as a Devourer-type creature, not a new invented body (source: `design/Jawa/worldbuilding/sarlacc_native_habitat_draft.md:471`, owner acceptance 2026-09-12: "Stage-I swimmer modeled on Anomaly's **Devourer** (owner's direction)")
- [ ] `sarlacc_swimmer_approaches_below_sand` — a moving swimmer is drawn beneath the sand surface (the submerged sprite), not walking on top of it (source: same file:471, "sub-sand approach, swallow-whole")
- [ ] `sarlacc_roots_visibly_on_map` — a swimmer that has found a seep or run dry is shown anchored in place as the mouth form (source: same file:481, Fork 1: "anchors visibly on the map")
- [ ] `sarlacc_stages_differ_small_mobile_vs_huge_fixed` — the small stage reads as small and mobile, the anchored/cistern stage as huge and fixed (source: same file:21, owner 2026-09-02: *"There should be many Sarlacc's, but they should be semi-permanent when they're really huge. But there are smaller, more mobile ones..."*)
(No `cannot show`: his rejections for this creature — compile-digestion "bizarre and unsettling" — are not visual. Art is Anomaly Devourer placeholders per the mod's own header.)

## RimStarWars/JawaVoice
no visual surface — no bar (assembly-free XML that adds Jawaese text lines to SpeakUp interactions; the experience is TEXT, so a `must read` candidate under north_star_validation_spec section 10, and the bubble itself is Interaction Bubbles' UI). No owner quote on how the lines should read was found beyond `design/V2_DREAMS.md:709` (a measured finding, not his words).

## RimStarWars/JawaRules
### must show
- [ ] `jawa_never_without_hood` — a Jawa is drawn with its hood while swimming, sleeping and in portrait/inspect (source: `infrastructure/state/ledger/events/BENCH.jsonl:196`, filing of owner chat 2026-09-25: "Jawa must never be seen without a hood"; paraphrase, not a verbatim quote; fix is the hood render node in this mod per BENCH.jsonl:198)
- [ ] `world_labels_clear_on_worldmap` — region/sea names on the planet view are clearly readable (not faint, not sunk into the terrain) (source: `infrastructure/state/items/closed/FALL_LINE_MAJOR_REGION_LABEL_1.md:7`, owner 2026-09-20: *"…a major world region with beautiful clear label on worldmap."*; said of one label, applied to labels generally by this draft)
### cannot show
- [ ] `world_labels_not_huge_or_overlapping` — region labels are not drawn across huge arcs of the globe overlapping each other (source: `infrastructure/state/items/closed/WORLD_FEATURE_LABELS_OVERSIZED_1.md:2-3`, owner 2026-09-07: **"the labels are now HUUUGE"**; size is `WORLD_LABEL_SIZE_HIERARCHY_1`'s business more than this mod's)

## RimStarWars/GizkaStowaway
no visual surface — no bar (the mod ships hediffs, a bait item, a thought and Harmony hooks; its own walk says the gizka art and sounds are "owned by the donor mod, not this one". His gizka art rulings live in `design/RimStarWars/canon_references/gizka/description.md` and bind the gizka creature def, not this mod). The `[S]` line "funny then a problem; owner decides" has no sourceable words.

## RimStarWars/BrainWorms
### must show
- [ ] `brainworm_realistic_not_cartoon` — the worm sprite is a realistic, moist, glistening segmented worm with natural lighting, no outlines, no cartoon shading (source: `design/RimStarWars/canon_references/brainworm/description.md:28`, owner 2026-10-08 verbatim: *"That's realistic, not these cartoon versions you keep using."*)
- [ ] `brainworm_body_plan_and_colour` — one legless, eyeless smooth tube, thickest at the head and tapering to a whip-thin tail, mustard-yellow/olive-gold with a dark olive-green back stripe and orange-brown banding on the fore body (source: same file:40-41, canon target per CLAUDE.md "canon is the target (owner, 2026-09-15)")
- [ ] `brainworm_forearm_sized` — the worm is about forearm-length against a pawn (source: same file:60, "Confirmed 2026-10-09 — decision taken by question card": size is forearm-length)
### cannot show
- [ ] `brainworm_not_snake_caterpillar_or_cartoon` — not a snake (no scales, jawed flat head, eyes), not legged, not a cartoon worm with a face, not one flat colour (source: same file:46, the canon Must-show NEGATIVE line; agent-written from images, so lightly sourced)
- [ ] `no_walking_corpse` — a dead host is never shown up and moving under worm control (source: `design/RimStarWars/brain_worm_spec.md:43-44`, owner 2026-09-11 verbatim: *"Never corpse-walker. Too gross."*)
(Art is vanilla stand-ins today per About.xml "ART OWED"; these bars are what the real art owes.)

## RimMandrake/Wreckage
### must show
- [ ] `wrecks_plentiful_where_hostile_or_remote` — a map in a hostile or hard-to-reach biome (sea floors, deep nightside, the Scald) shows many wrecks; the deep nightside is riddled with them (source: `design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md:256-262`, owner 2026-10-03 by card with typed answers: a wreck persists where hostile and inaccessible, *"perfect for the Utinni to visit"*; sea floors *"high density"*)
- [ ] `wrecks_scarce_where_travelled` — a map in an ordinary travelled biome shows few or no wrecks (source: same file:258-259, owner: anything that falls where people live or travel *"is cleaned off the surface within a few decades"*)
- [ ] `scald_wrecks_stand_in_shallows` — the Scald's hull, tank and frame wrecks stand in the shallows (source: `design/Jawa/worldbuilding/biomes/the_scald.md:162`, ruled biome sheet: "Wrecks in the shallows"; ruled doc, not a typed quote)
- [ ] `game_filled_with_wreckage` — across the planet, wreckage is a common sight rather than a rarity (source: `infrastructure/state/ledger/events/OWNER.jsonl:31`, owner 2026-09-25: *"game should be filled with lots of this all over the place given it's salvage focus."*; in tension with the two placement lines above — his later 2026-10-03 placement law refines it, flag for his reaction)

## RimUtinni/AftermathRites
no visual surface — no bar (defs-only data: 8 aftermath rules and 5 alliance pairs read by `mandrake.rm.aftermath`; its own walk says "nothing to look at visually").

## RimUtinni/AshkarrInhabited
no visual surface — no bar (data-only SettlementManifestDef/SecurityProfileDef instances; its own header says "no art/verb/claim logic of its own"; the settlement's look belongs to the `mandrake.rm.inhabited` walk). The `[S]` step "districts and cast placement read correctly against the manifest" has no sourceable owner words.


## RimMandrake/Visibility
no visual surface — no bar (GameComponent dial and raid-points multiplier; ships zero Defs, no art, only a dev-menu action).

## RimMandrake/Traces
- [ ] `signs_of_something_happening` — the shot shows blaster, burn or scorch marks on a wall, or floor scrapings, that read as a sign that something happened here (source: owner quote, `design/RimMandrake/event_trace_props_library_design_2026-10-03.md:3-5`: "a new props library that's all about blaster marks, burn marks, scorch marks, floor scrapings, and other 'signs of something happening.'")
- [ ] `wall_scar_remains_after_repair` — a wall repaired to full HP still shows its blaster scar (source: owner typed ruling 2026-10-03, ledger `infrastructure/state/ledger/events/BENCH.jsonl:1086` tsn 1791070178730227303, and `design/RimMandrake/event_trace_props_library_design_2026-10-03.md:260-261`: "How cool would that be?")
- [ ] `repair_leaves_mend_plate` — a repaired building shows a plain weld-plate mark (source: owner card ruling 2026-10-03, same tsn 1791070178730227303: "Reuse the weld-plate art as the plain repair mark")
- [ ] `broken_door_is_broken_doorway` — a door that was forced shows as a broken doorway, not vanilla's door-just-gone rubble (source: owner card ruling 2026-10-03, same tsn 1791070178730227303: "Broken door leaves a broken doorway")
- [ ] `unvisited_room_gathers_dust_drift` — a long-unvisited room shows drift or dust, and walked-through dust shows prints (source: owner card ruling 2026-10-03, same tsn 1791070178730227303: "Dust drift in both live play and pre-made ruins")

## RimMandrake/TheftHauler
no visual surface — no bar (the verb is a log line, a job and a MinifiedThing; the walk itself says it reuses Droidworks' existing chassis sprite unchanged).

## RimMandrake/TheBazaar
no visual surface — no bar (slice 1 ships no defs, no art and an inert trade-window class; the grid, duel and broker tab are unbuilt and no owner words describe their look).

## RimMandrake/StructureInjections
no visual surface — no bar (engine that replays plans; ships zero Defs; the walk assigns the "looks right" pass to the content packs).

## RimMandrake/StrandedQuest
no visual surface — no bar (pure-XML quest on vanilla nodes; the stranded survivor is a stock SpaceRefugee pawn, no new art).

## RimMandrake/ShipVermin
- [ ] `vermin_spawn_from_wreckage` — a vermin creature is on or beside a ship wreck chunk (source: owner quote, `infrastructure/state/items/closed/WRECKAGE_VERMIN_SPAWN_1.md:3`: "Yes vermin should be able to spawn from wreckage.")
- [ ] `mynock_outside_hull_in_vacuum` — a mynock is shown out in the open/vacuum, not only inside a hull (source: owner quote, `infrastructure/state/items/closed/SHIP_VERMIN_MOD_1.md:3-7`: "some live inside, some can live outside in vaccuum (the mynock for example)")

## RimMandrake/SalvageClaim
no visual surface — no bar (one float-menu order inside RimProperty; the walk records only the menu text).

## RimMandrake/RimDefDump
no visual surface — no bar (research tooling that writes JSON files; nothing renders).

## RimMandrake/RaidRedesigner
no visual surface — no bar (scribed roster of persistent NPCs; zero Defs, no UI).

## RimMandrake/ProximityHatch
- [ ] `egg_hatches_at_you` — an egg beside a pawn has hatched into a creature that is coming at the pawn, while a distant egg is still an egg (source: owner quote, `infrastructure/state/items/closed/EGG_PROXIMITY_HATCH_TRIGGER_1.md:4-5`: "Still need to dev a trigger for eggs that hatch at you on proximity.")

## RimMandrake/Property
no visual surface — no bar (ownership ledger, pure C# API with no rendered UI).

## RimMandrake/PlanetPresetPrime
no visual surface — no bar (a world-creation-page default; the walk says nothing visual).

# part_06 — draft must-show lines (from existing rulings; he reacts)

Ledger events carry a `ts` field (no `tsn`); cited as `OWNER.jsonl:<line> ts <ts>`.

## RimMandrake/Ninefold
no visual surface — no bar (ships no defs or art; satiation/mood are internal numbers, no UI, per the walk's own anti-guessing note).

## RimMandrake/MovingDunes
- [ ] `sand_piles_and_creeps` — Sand on the map visibly piles up against structures and drifts across the map over days instead of staying where it landed. (source: owner spark verbatim, infrastructure/state/items/closed/MOVING_DUNES_ENGINE_1.md:3-4 "it would be fun to have it pile up so much this becomes a moving dune mod..."; pacing "extremely slow", design/MOVING_DUNES_DESIGN.md:128)
- [ ] `sand_banks_at_water` — Where drifting sand meets water it builds a bank on the shore; the sand does not vanish into the lake. (source: owner decision by card 2026-10-07, infrastructure/state/items/MOVINGDUNES_WATER_BANKS_SAND_1.md:7; design/MOVING_DUNES_DESIGN.md:83)
- [ ] `pits_and_cleared_lanes_refill` — A dug pit or cleared lane fills back in with sand over time. (source: design/MOVING_DUNES_DESIGN.md:188 "exactly the owner's 'pits that fill in'")

## RimMandrake/MineShaft
no visual surface — no bar (no Textures folder; the mod generates mining bills from policy defs, the shaft uses existing art; owner's only words are about studying it, mines_mod_assessment_20261011.md:3-4).

## RimMandrake/LoreStages
no visual surface — no bar (engine only: ships no defs and no art; it swaps description text per stage).

## RimMandrake/LoadTracer
no visual surface — no bar (Player.log diagnostic, no player-facing content).

## RimMandrake/KeelHoist
- [ ] `hoist_is_a_ship_part` — The keel hoist stands on the gravship's own structure as a ship fitting. (source: owner, ledger OWNER.jsonl:162 ts 2026-10-01T23:09:54Z "Could be a unique gravship component in this campaign")
- [ ] `no_player_built_site_hoists` — Hoist head-frames at sites (Hutt pit, vault shaft) are already standing in the world; none is on the player's build menu. (source: design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md:95 owner ruling "fixed hoists that come built into sites. Players do not build fixed hoists."; infrastructure/state/items/closed/HOIST_FIXED_SITE_FRAMES_1.md:5)
- [ ] `oubliette_is_sealed_not_enterable` — The Hutt oubliette reads as a sealed map feature the player has no way into. (source: OWNER.jsonl:166 ts 2026-10-02T00:56:19Z "It is a special map feature you can't go into and don't want to.")
- [ ] `hoist_lifts_after_taking_the_site` — Once the site is attacked and taken, the ship's winch can lift the slaves out. (source: same quote, OWNER.jsonl:166 "your shop winch could reach down and lift up the slaves if you attacked the place and took it over")
- [ ] `cable_is_a_drawn_line` — The cable between hoist and target is a drawn line over static sprites, no descent animation. (source: HOIST_FIXED_SITE_FRAMES_1.md:15 citing owner "careful we don't get caught in endless animation development")

## RimMandrake/HugeThings
- [ ] `trunk_small_patch_blocks_walking` — A full-grown huge plant's stem blocks only a small patch (about 2x2 to 4x4 by species); pawns path around it. (source: owner picked option 1 at 2026-10-07 07:17, design/RimMandrake/giant_footprint_design_2026-10-07.md:8-9 "Solid trunk, open canopy — the stem blocks a small patch (~2×2 to 4×4 by species) so pawns path around it")
- [ ] `walk_under_the_cap` — Pawns walk under the canopy cap of a huge plant like a tree canopy. (source: same quote, giant_footprint_design_2026-10-07.md:9-10 "you walk under the cap like a tree canopy")
- [ ] `titanic_tree_trunk_only` — A Titanic tree (12-30+) is seen as its solid trunk only. (source: OWNER.jsonl:1121 ts 2026-10-18T15:30:35Z "Titanic trees should be seen only as the solid trunk")
- [ ] `titan_smashes_built_things` — A titan walking through a base leaves its built walls and thin roofs destroyed behind it. (source: owner card 2026-09-09, infrastructure/state/items/closed/TITANIC_CREATURES_MOD_1.md:11-14 "Thin (constructed) roofs are DESTROYED as the titan passes ... smashes through anything built")
- [ ] `titan_avoids_thick_rock` — A titan is never shown under overhead mountain. (source: TITANIC_CREATURES_MOD_1.md:12-14 "a titan never paths under rock"; infrastructure/state/items/TITAN_ROOF_AVOIDANCE_1.md:6)

## RimMandrake/HostileFlora
- [ ] `gallowroot_waits_rooted` — The gallowroot sits still and reads as a plant, not as a roaming animal. (source: owner choice "It waits, rooted and still", infrastructure/state/items/HOSTILE_MOBILE_PLANTS_1.md:25-28)
- [ ] `gallowroot_leaf_twitch` — If you watch carefully, one of its leaves occasionally twitches. (source: owner verbatim, HOSTILE_MOBILE_PLANTS_1.md:27-28 "a small animation that one of its leaves occasionally twitches if you watch carefully") — walk says art/animation are unbuilt, so expect FAIL until HOSTILE_MOBILE_PLANTS_1 delivers
- [ ] `neighbours_swarm_together` — When one gallowroot is hurt or triggered, the others near it wake and come at the pawn too. (source: owner verbatim, HOSTILE_MOBILE_PLANTS_1.md:48-50 "activates if others of its own kind activate nearby: swarm")

## RimMandrake/GravshipLanding
- [ ] `outdoors_visible_at_landing_picker` — At the gravship landing picker the whole outdoor map is unfogged, not one tiny room. (source: owner 2026-09-12, infrastructure/state/items/closed/GRAVSHIP_LANDING_FOG_REVEAL_1.md:3-5 "fog of war and/or CAI were obscuring the whole map ... so I was forced to land blind and crashed"; ruling line 53 "reveal EVERYTHING OUTDOORS")
- [ ] `roofed_interiors_stay_fogged` — Roofed interiors (mountain, sealed rooms) stay fogged. (source: GRAVSHIP_LANDING_FOG_REVEAL_1.md:53 "roofed interiors stay fogged")
- [ ] `map_looks_good_with_buildings` — With buildings on the map the defogged outdoors looks right. (source: owner verbatim, GRAVSHIP_LANDING_FOG_REVEAL_1.md:58-59 "The defogging worked even with buildings on the map! And the map looks already pretty good.")

## RimMandrake/ExplosiveKnockback
- [ ] `mortar_throws_human_3_cells` — A mortar shell landing beside a human throws them about 3 cells away from the blast, alive. (source: owner Q7 by card 2026-10-06 19:05, design/RimMandrake/explosive_knockback_design_2026-10-06.md:461)
- [ ] `thrown_over_sandbags` — A thrown pawn clears sandbags and barricades. (source: owner Q3 by card, explosive_knockback_design_2026-10-06.md:457)
- [ ] `light_items_and_corpses_thrown` — Light items and corpses are thrown by a blast too. (source: owner Q4 by card, explosive_knockback_design_2026-10-06.md:458)
- [ ] `blasted_into_pit_falls` — A pawn blown into an open or covered pit falls in. (source: OWNER.jsonl:230 ts 2026-10-06T16:27:19Z "Only if they get blown/forced in do they fall."; PIT_SUPERDEEP_COLLAPSE_1 quote at explosive_knockback_design_2026-10-06.md:24-25)
- [ ] `fallen_through_cover_is_broken` — A pit cover something has fallen through, or a blast has hit, is shown broken, no longer covered. (source: owner typed 19:13, explosive_knockback_design_2026-10-06.md:467 "when something falls into a covered pit, of course it is no longer covered"; Q5 line 459)

## RimMandrake/Aftermath
no visual surface — no bar (ships no defs or art; incident-timing engine, per the walk's own "no bespoke art" note).

## RimMandrake/AcousticScanner
no sourced line found. Visual surface exists (sounder building, pulse dust/thump, banded overlay, letter) but his only words are "I like the belly sounder immensely and it should do something in every biome actually. Acoustic scanner." (infrastructure/state/items/GRAVSHIP_ACOUSTIC_SCANNER_1.md:4-5); the dust, hull vibration and banded-overlay description (:11-13) is spec text, not his words, so I did not turn it into a bar.

