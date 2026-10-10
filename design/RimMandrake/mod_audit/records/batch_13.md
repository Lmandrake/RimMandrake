# Mod audit record: batch 13 (misc_content_1)

Assessed by Sonnet 5.5 against facts generated 2026-10-10T14:47:38-0700. One section per mod; template per RUBRIC.md section 7.

### [1.6] CAI 5000 - Advanced AI + Fog Of War (continued) (`krkr.rule56`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/kbatbouta/RimWorld-RocketMan (github, EPL-2.0; availability yes, MEASURED)
**Adds:** content: 24 declared defs: ThingDef 6, HyperTextDef 4, RaidTargetCollectionDef 3, DutyDef 3, JobDef 3, ResearchProjectDef 3 (defs_by_type); functionality: Advanced combat AI (pawn/enemy tactics) plus a from-scratch fog of war, by the RocketMan team; unofficial 1.6 port. 448 KB CombatAI.dll with Harmony, Prepatcher and tick flags (dll_flags); art: 35 textures, 16.6 MB on disk, 99.3 MB decoded estimate (INFERRED)
**Why:** Owner ruled fog-of-war Route B (design/Jawa/OPUS5_HANDOFF.md line 179): CAI 5000's combat AI plus NWN Real Fog of War with CAI's own fog OFF; the executing item FOW_ROUTE_B_INTEGRATION_1 is done (rimflow show). Qualitative danger via smarter enemies fits the no-arms-race pillar (brief 1, 4 test 3-4). Nothing else depends on it (dependants []), but 16 of our xpath refs come from mandrake.rut.researchretag, and the ruled campaign design counts on it.
**Problems:** tps 2 tick FLAGS comp_tick, map_component_tick, game_component_tick, world_component_tick plus a per-tick AI/sight engine; per-mod cost UNMEASURED · memory 2 texture_decoded_mb_est 99.3 (proxy) · complexity 3 Harmony + Prepatcher DLL, static_ctors 7 · interaction 2 patched_by_ours_refs 16 (researchretag); incompatible_with lists 7 ids (WallsAreSolid, lineofsightfix, rimthreaded, Multiplayer, ...) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 3 linked repo is the ORIGINAL RocketMan (EPL-2.0, last push 2024-04-22, over 2 years); this fork's own repo not seen; cai_fog_deep_dive says CAI is unlicensed, which disagrees with EPL-2.0 on the linked repo
**Holds it in / exit:** FOW_ROUTE_B_INTEGRATION_1 (done): ruled Route B uses its combat AI; mandrake.rut.researchretag patches its research defs (16 refs) -> None
**Open:** Was the Prepatcher requirement verified present and loading before CAI (load_after lists zetrith.prepatcher)?; Is the linked EPL repo the actual source of this Krkr fork? Confirm before relying on source.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Vehicle Framework (`smashphil.vehicleframework`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/kanid99/Rimworld-AutoSeller-VehicleFramework-Patch (github-search name match, mit; availability unverified, INFERRED)
**Adds:** content: 205 declared defs: VehicleEventDef 36, JobDef 20, PatternDef 15, ThingDef 13, DutyDef 12, WorkGiverDef 10, StatUpgradeCategoryDef 9, HistoryEventDef 8; functionality: Framework for building vehicles (land, sea, air) with its own pathing, upgrades, world-map vehicle caravans; 3 DLLs with Harmony, tick flags and a settings screen; art: 2.2 MB textures + 1.3 MB asset bundle; 49.1 MB decoded estimate (INFERRED)
**Why:** design/Jawa/mods/required_mods.md line 1043 records Vehicle Framework as ADOPTED for player vehicles (mobility and cargo guardrail). Dependants in the universe: gabrieel1482.raidvehicleframework, oskarpotocki.vanillavehiclesexpanded, sarg.alphavehiclesneolithic (dependants field). Our mandrake.rsw.armoury lists it in loadAfter and JawaIonWeapons names SmashPhil.VehicleFramework in its About; our patches (rut.patches 18, rut.doctrine 6) touch its defs (patched_by_ours_refs 24). Removing it would break those dependants.
**Problems:** complexity 3 static_ctors 54 (> 20), Harmony, 3 DLLs · tps 2 comp_tick, map_component_tick, world_component_tick FLAGS; vehicles it spawns add tickers; per-mod UNMEASURED · interaction 2 patched_by_ours_refs 24; incompatible_with majorhoff.rimthreaded · memory 1 texture_decoded_mb_est 49.1 (just under 50; proxy) · log_noise 0 0 error occurrences measured · maintenance 2 source_url is a github-search NAME MATCH to a third-party AutoSeller patch repo, not the framework; real repo unverified
**Holds it in / exit:** dependants: raidvehicleframework, vanillavehiclesexpanded, alphavehiclesneolithic; 24 xpath refs from mandrake.rut.patches / rut.doctrine; mandrake.rsw.armoury loadAfter; JawaIonWeapons About names it -> None
**Open:** Can a water/air Vehicle Framework vehicle reach RM_SeabedLayer or otherwise bypass 'ship or nothing'?; True upstream repo not seen in facts | NEEDS OWNER: Should player-built vehicles (including boats/aircraft) be allowed to move on the sea layer or leave the ship-centred loop, or are only land vehicles wanted?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### [1.1]TO[1.6]MultipleTraders (`04.23.2020`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 7 TraderKindDef (defs_by_type); 22 patch ops (67 into Core, 16 into Better Traders); functionality: Varied orbital and caravan traders; pure data. XML only; art: 0.1 MB textures
**Why:** design/Jawa/mods/required_mods.md lines 984 and 1028 decide MultipleTraders as the heterogeneous-stock lever for the barter substitute, and design/RimMandrake/bazaar_trade_window_design.md line 299 lists it under 'Keep' (we consume vanilla TradeDeal from whatever it generates). Fits the trading/scavenging loop.
**Problems:** complexity 1 XML only (dll_count 0) · interaction 1 patches vanilla and third-party Better Traders defs; none of ours (patches_ours_refs 0) · maintenance 2 no repo found (steam-only) but XML only, so shipped files are the source; 1.6 compatibility note says June 2026 · log_noise 0 0 errors
**Holds it in / exit:** bazaar_trade_window_design.md: 'Keep' list; required_mods.md trade lever decision -> None
**Open:** packageId '04.23.2020' is unusual; any of our patches that need a MayRequire on it would use that literal id
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### [SR]Factional War (fork) (`sr.modrimworld.factionalwarcontinued`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (C# source inside the mod folder, None; availability yes, MEASURED)
**Adds:** content: 23 declared defs: DutyDef 6, IncidentDef 4, GenStepDef 3, SitePartDef 3, WorldObjectDef 3, RaidStrategyDef 1; functionality: 4 incident types where two factions fight and the player is a bystander who may intervene; smarter enemy behaviour (self-treat, finish wounded). 1 Harmony DLL, 62 C# files shipped; art: 0.35 MB textures
**Why:** No ruling names it and nothing in the universe depends on it, so on evidence alone no stronger verdict is supported. It supplies a bystander-war incident class we have no plan to build. Marked card_worthy because random third-party war incidents compete with the authored Empire/Hutt/Ta'Baa pressure (brief 1). Folder holds versions 1.2-1.5 only plus a root Defs folder, so 1.6 loads via fallback (INFERRED); supports_1_6 true comes from the About.
**Problems:** complexity 2 one Harmony DLL, static_ctors 2 · tps 1 no tick flags; incident-time AI only · log_noise 0 0 errors · maintenance 1 C# source ships in folder (62 .cs); no repo URL verified; no 1.6 version folder
**Holds it in / exit:** no dependants; no ruling found -> None
**Open:** Does an extra random-war incident layer belong in a story-paced campaign?; Verify it loads from its 1.5 folder on 1.6 without errors (0 log errors supports yes) | NEEDS OWNER: Do you want random 'two factions are at war, you are a bystander' incidents in this campaign, or should the Empire/Hutt/Ta'Baa pressures be the only big events?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### [ZAV] Glowstone (`zav.glowstoneforked`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 39 defs: ThingDef 23, RecipeDef 14, DesignatorDropdownGroupDef 2; functionality: New mineable ore, glowstone, used for lamps, columns, sculptures; XML only; 17 patch ops (royalty, ideology, Better Traders); art: 0.2 MB textures
**Why:** Harmless, but it is a donor content mod and the standing ruling is 'Everything should be moved to our own thing defs' (DONOR_DEFS_PORT_TO_OURS_1). Nothing depends on it; kikohi.jewelry patches it (2 refs). Our crystals are already built as RimMandrake/Pyrinth, kyber and others; a glowing ore for lamps is a thing we can own. What holds it in: it is naturally placed in mineable layouts (UNMEASURED in save).
**Problems:** complexity 1 XML only · log_noise 0 0 errors · maintenance 2 no repo found; XML only · interaction 1 patches vanilla defs only
**Holds it in / exit:** kikohi.jewelry patches it; placed ore/lamps in save UNMEASURED -> unfiled: ZAV_GLOWSTONE_PORT_OR_DROP_AT_PAINT
**Open:** Is glowstone referenced by any of our biome or mutator XML? (gen_furniture_register only matches the word in a regex)
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Adaptive Ideology Storage (`adaptive.ideology.storage`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: Census def_total 0 is a BLIND SPOT: all 54 xml files sit under a 1.5/ folder (no 1.6 folder), which the scanner did not count; the mod ports Ideology storage containers (barrels, crates, lockers) onto Adaptive Storage Framework; functionality: Buildable storage containers with contents-aware graphics (via ASF); XML only; art: 40.2 MB of textures on disk, 281.2 MB decoded estimate (INFERRED)
**Why:** Pure cosmetic storage skins. required_mods.md line 271 adopts the Adaptive Storage Framework as 'mostly cosmetic denser shelving', and mandrake.rsw.armoury hard-depends on adaptive.storage.framework, so the framework stays; this model pack is separate and carries a 281 MB decoded-texture proxy for a cosmetic. No donor art is kept (brief 4 test 8). Exit: choose which model packs survive or replace the skins with owned art; no item exists yet.
**Problems:** memory 3 texture_decoded_mb_est 281.2 (>250; proxy) from 40.2 MB of files · complexity 1 XML only · maintenance 2 no repo (steam-only); XML only · log_noise 0 0 errors
**Holds it in / exit:** adaptive.storage.framework (kept) is its dependency; placed storage containers in save UNMEASURED -> unfiled: ASF_MODEL_PACKS_KEEP_OR_REPLACE
**Open:** The census shows 0 defs because content is under 1.5/: does the 1.6 game actually load it (log shows 0 errors)? | NEEDS OWNER: Which of the three Adaptive Storage model packs (Ideology, Primitive, Simple) do you want in the finished game, or should storage use our own art?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Adaptive Primitive Storage (`adaptive.primitivestorage`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: Census def_total 0 is a BLIND SPOT: 28 xml files under 1.5/ only; ports LWM Primitive Storage (cellar, storage pit and tent, log piles, weapon rack, woven baskets, clay pots, granary) to ASF; functionality: Primitive (neolithic) storage buildings with contents-aware graphics; XML only; art: 13.8 MB textures, 104.8 MB decoded estimate (INFERRED)
**Why:** Same shape as its two siblings but the most on-genre for scavengers and tribal beginnings (cellars, baskets). Art is Phaneron's retexture, a donor (brief 4 test 8). The ASF framework is held by mandrake.rsw.armoury; this skin pack has no dependants. Phase out when owned primitive storage art exists, or keep if the owner approves it.
**Problems:** memory 2 texture_decoded_mb_est 104.8 (proxy) · complexity 1 XML only · maintenance 2 no repo (steam-only) · log_noise 0 0 errors
**Holds it in / exit:** adaptive.storage.framework dependency (kept); placed storage in save UNMEASURED -> unfiled: ASF_MODEL_PACKS_KEEP_OR_REPLACE
**Open:** Does a Jawa crew living aboard a ship need cellars and storage pits at all? | NEEDS OWNER: Same card as the Ideology storage pack: which ASF model packs stay?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Adaptive Simple Storage (`adaptive.simplestorage`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: Census def_total 0 is a BLIND SPOT: 42 xml files under 1.5/ only; ports JDS Simple Storage (shelves, lockers, crates) to ASF; functionality: Compact storage buildings with contents-aware graphics; XML only; art: 17.4 MB textures, 144.8 MB decoded estimate (INFERRED)
**Why:** A cosmetic storage-skin pack; the most generic of the three and the closest to an item a ship hold would use. The framework is retained by Armoury's hard dependency; this pack has no dependants. Phase out once owned shelving/locker art exists, or the owner keeps it.
**Problems:** memory 2 texture_decoded_mb_est 144.8 (proxy) · complexity 1 XML only · maintenance 2 no repo (steam-only) · log_noise 0 0 errors
**Holds it in / exit:** adaptive.storage.framework dependency (kept); placed shelves in save UNMEASURED -> unfiled: ASF_MODEL_PACKS_KEEP_OR_REPLACE
**Open:** none | NEEDS OWNER: Same card as the Ideology storage pack.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Ali's Grow All Odyssey Plants (`ali.growodysseyplants`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 0 declared defs; 4 patch ops into Odyssey; functionality: Lets Odyssey plants Psilocap, Boomshroom, Night Grass, Willowgill be grown in ground or hydroponics. XML patch only; art: 0.17 MB textures (10.5 MB decoded estimate)
**Why:** Odyssey is a hard prerequisite for every player (CLAUDE.md DLC ruling), tiny XML patch, and farming exotic mushrooms/night plants suits an alien-looking, scarce-resource world. Nothing depends on it; none of our patches touch it. Any plan to own the plants is not filed; the cost of keeping is near zero.
**Problems:** complexity 1 XML only · log_noise 0 0 errors · maintenance 2 no repo (steam-only); XML only
**Holds it in / exit:** supplies a farming option we have no plan to build -> None
**Open:** none
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Ancient Dangers on Campsites and Encounter maps (`vita.campdangers`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (UNVERIFIED) · **Fit:** neutral · **Source:** https://github.com/VitaKaninen/AncientDangersOnCampsitesandEncounterMaps (github-search name match, ; availability unverified, INFERRED)
**Adds:** content: 0 declared defs; 2 patch ops into Core (patch_findmod 'Set Up Camp'); functionality: Lets ancient dangers spawn on encounter maps and Set Up Camp campsites. XML patch only; art: 0.85 MB textures (3.5 MB decoded)
**Why:** Ancient Dangers are Ideology/Anomaly-style map events. The campaign has authored map content and a fixed world; Set Up Camp is required for this to do anything, and I did not find Set Up Camp in this batch's facts (UNVERIFIED whether it is in the list). Keep only while that pairing holds.
**Problems:** complexity 1 XML only · log_noise 0 0 errors · maintenance 1 github-search name match, pushed 2026-03-18; match unverified
**Holds it in / exit:** only active if Set Up Camp is in the list (not checked) -> unfiled: CAMPDANGERS_CHECK_SETUPCAMP_PAIRING
**Open:** Is Set Up Camp (the mod it patches) in the 550 list?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Ancient mining industry (`xmb.ancientminingindustry.mo`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/suancai1234/Ancinet-Mining (github, None; availability yes, MEASURED)
**Adds:** content: 174 defs: KCSG SymbolDef 64, ThingDef 49, KCSG StructureLayoutDef 18, QuestScriptDef 16, GenStepDef 11, SitePartDef 11 (defs_by_type); functionality: Ancient mining facility structures and explorable maps via the KCSG structure generator, with quests, plus a buildable mining-and-screening production line; one Harmony DLL; art: 3.1 MB textures; 109.5 MB decoded estimate (INFERRED)
**Why:** Recorded ADOPTED for exploration with a self-limit: design/Jawa/mods/forbidden_mods.md line 244 and required_mods.md line 442 say the player-buildable production line is a second industrial tree and stays off-limits (the Cherry Picker trimming route, brief 2). Its explorable ruins are salvage/scavenger content (brief 4 test 3). Held in by: mandrake.rut.researchretag (4 refs), mandrake.rsw.armoury (2 refs, plus named in its About list), and the exploration layouts. Not replaceable cheaply (64 symbol and 18 layout defs).
**Problems:** complexity 2 one Harmony DLL; KCSG structures; static_ctors 4 · memory 2 texture_decoded_mb_est 109.5 (proxy) · size 1 disk_mb 14.75 · interaction 2 patched_by_ours_refs 6 · log_noise 0 0 errors · tps 1 comp_tick FLAGS but low content count · maintenance 2 source_url INFERRED (github suancai1234/Ancinet-Mining, unverified, no push date)
**Holds it in / exit:** patched_by_ours: researchretag 4, armoury 2; dependency VFE Core (oskarpotocki.vanillafactionsexpanded.core); ruled adopted with self-limit -> None
**Open:** Has the production line been Cherry-Picker-cut as forbidden_mods says? Check the cut list.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Aqued Dredge Aberrations (`aqued.dredgeaberrations`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 16 defs: HediffDef 7, ThingDef 7, AbilityDef 1, ThingCategoryDef 1; 5 patch ops into Odyssey; functionality: Dredge-inspired aberration hediffs, items and an ability layered on Odyssey fishing; XML only; art: 0.64 MB textures; 19.8 MB decoded estimate
**Why:** A creature-horror flavour pack taken from the video game Dredge, a recognisable external IP in name and theme (brief 4 test 3 recognizability; brief 3). The campaign has its own sea rosters and fishing tradition (CLAUDE.md sea rulings: each sea species owes a floor resident and a catch), so Dredge aberrations would be a rival of owned content. Nothing depends on it. Exit: judge at the sea biomes' sittings and port or drop; no item filed.
**Problems:** complexity 1 XML only · memory 1 texture_decoded_mb_est 19.8 · log_noise 0 0 errors · maintenance 2 no repo (steam-only); XML only
**Holds it in / exit:** no dependants; placed items/hediffs in save UNMEASURED -> unfiled: DREDGE_ABERRATIONS_DROP_AT_SEA_SITTING
**Open:** Which fish/aberration items does it inject into the Odyssey fishing tables, and does that collide with our fishTypes? | NEEDS OWNER: Do you want Dredge-style 'aberrant catch' content in the sea biomes, or only our own creatures?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### AuthenticTantrumNoises (`kshtantrumsounds.mod`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** https://github.com/kshade/AuthenticTantrumNoises (github-search name match, unlicense; availability unverified, INFERRED)
**Adds:** content: 2 defs (EffecterDef 1, SoundDef 1); 1 patch; functionality: Replaces the sound of a colonist tantrum with a real-life angry-child recording; art: 0.45 MB sounds
**Why:** Sound-only gag from an internet meme recording ('Angry German Kid'); it breaks the Firefly/BSG frontier tone (brief 1 tone, brief 4 test 3). Retirement is trivial: dependants [], no placed Things (sound/effecter only, no ThingDef), no inheritance. The 2026-08-30 pass said 'trivial, harmless'; harmless is not a fit argument. Marked card_worthy because tone is a taste call.
**Problems:** complexity 1 XML only · log_noise 0 0 errors · maintenance 1 github-search name match, unlicense, last push 2025-07-18; unverified
**Holds it in / exit:** no dependants -> None
**Open:** none | NEEDS OWNER: Is a real-voice meme tantrum sound acceptable in this game's tone, or cut it?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Better Explosions (`nephlite.advexplosions`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 10 FleckDefs; 27 patch ops each into blues.forge and Core, 4 into Royalty; functionality: Replaces explosion visual effects with better-looking ones. XML only; art: 1.1 MB textures
**Why:** Cosmetic (passes the ceiling test trivially, brief 4 test 4); explosions are common in a raid-pressure game. Nothing depends on it. Overlaps keshash.extraexplosioneffects in this batch, which also adds explosion flecks; I did not measure whether both can apply to the same defs. Nothing of ours is touched (ours refs 0).
**Problems:** complexity 1 XML only · interaction 1 patches vanilla and Blues Forge defs; overlaps Extra Explosion Effects (not measured) · log_noise 0 0 errors · maintenance 2 no repo (steam-only); XML only
**Holds it in / exit:** supplies a visual layer we do not plan to build -> None
**Open:** Do Better Explosions and Extra Explosion Effects both patch the same explosion defs? Check at a load round.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Better Traders (`jm.bettertraders`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/JoshMate/Mod_Rimworld_BetterTraders (github, None; availability yes, MEASURED)
**Adds:** content: 20 TraderKindDefs (defs_by_type); no patches; functionality: Raises trader silver and stock; 'vanilla friendly and gameplay balanced'. XML only; art: 1.1 MB textures
**Why:** design/RimMandrake/bazaar_trade_window_design.md line 299 lists Better Traders as KEEP (it shapes stock and arrivals; our Bazaar trade window consumes vanilla TradeDeal). Patched by 16 of MultipleTraders' ops and by 7 xpath refs from our mods (by_ours 7), plus others (survivaltools, vcooke, VVE). The silver increase touches scarcity (brief 4 test 4 on bypassing scarcity), which is a tuning question, not a verdict reason.
**Problems:** interaction 2 patched_by_ours_refs 7 (our mods patch its trader kinds) · complexity 1 XML only · log_noise 0 0 errors · maintenance 1 github repo linked, last push 2025-10-24
**Holds it in / exit:** patched_by: 04.23.2020 16, survivaltools 14, ... ; ours 7 refs; Bazaar design Keep list -> None
**Open:** Is the extra silver compatible with the scarcity pillar? Tune via its settings if not.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Better Trees (`chaoticenrico.bettertrees`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 3 defs (TreeScaleTemplateDef 1, TreeTextureTemplateDef 1, KeyBindingDef 1); 10 patch ops (Alpha Biomes 7, Ideology, Landmarks); functionality: Framework to retexture, resize and tweak trees; one Harmony DLL with settings screen; art: 5.55 MB textures; 103.6 MB decoded estimate (INFERRED)
**Why:** Two of our mods patch its defs directly: src/RimUtinni/AshkarrFlora and src/RimMandrake/LeaningScrub ship Patches/BetterTrees_SweetlineTree_Immunity.xml against BetterTrees.TreeScaleTemplateDef (RM_SweetlineTree), AshkarrFlora's About names it, and modcheck required_checks.json lists the AshkarrFlora check. So it is a live dependency even though dependants_ours is empty. KEEP until those immunity patches are retired.
**Problems:** interaction 2 our two patches into BetterTrees.TreeScaleTemplateDef; incompatible_with lists 5 mods none of which are in the list (MEASURED against FULL.LATEST) · memory 2 texture_decoded_mb_est 103.6 (proxy) · complexity 2 one Harmony DLL, static_ctors 2 · log_noise 1 0 errors, 7 chatter lines · maintenance 2 no repo (steam-only); DLL present
**Holds it in / exit:** AshkarrFlora and LeaningScrub patches (BetterTrees_SweetlineTree_Immunity.xml); modcheck required_checks.json AshkarrFlora -> None
**Open:** Are there better-trees retextures that fight the 'matte, no outline' art lawset?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Bradson's Main Button Icons (Forked + Expanded) (`bs.mbifvte`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/KarmicBacklash/Main-Button-Icons-for-Vanilla-Textures-Expanded (github, None; availability yes, MEASURED)
**Adds:** content: 0 defs; 63 patch ops across 10+ UI mods (Numbers, Mint Menus, WeaponStats, PrisonLabor, Biotech...); functionality: Adds main-button icons for Vanilla Textures Expanded and adds icons to other UI mods; one small Harmony DLL; 15 .cs shipped; art: 0.84 MB textures; 6.0 MB decoded estimate
**Why:** Pure UI cosmetic that patches Numbers and Mint Menus icons; free to keep, nothing ours touched. Source: github.com/KarmicBacklash repo, last push 2024-11-26 (about 2 years; maintenance 2). Safe.
**Problems:** complexity 2 one Harmony DLL · log_noise 0 0 errors · maintenance 2 repo MEASURED, last push 2024-11-26
**Holds it in / exit:** none -> None
**Open:** none
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Crafting Spot Slave Gear (`heatherathebyne.craftingspotslavegear`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (UNVERIFIED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 0 defs; 2 patch ops into Ideology; functionality: Allows slave collars and body straps to be crafted at crafting spots; art: 0.39 MB textures
**Why:** Slave-collar crafting at crafting spots: Jawa clans in canon are captured/traders of droids; slavery is thematically contested content and the campaign's Ideology has its own precept logic; there is no ruling, and nothing depends on it. Suitable as a low-risk keep only if slavery is part of the scenario, which is not recorded in my sources. Tag KEEP-TEMPORARILY until the owner says whether slave gear belongs.
**Problems:** complexity 1 XML only · log_noise 0 0 errors · maintenance 2 no repo (steam-only); XML only
**Holds it in / exit:** no dependants -> unfiled: SLAVE_GEAR_SCENARIO_DECISION
**Open:** Is slavery in scope? The brief does not say. | NEEDS OWNER: Should enslaved prisoners and slave gear be part of this scenario at all?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Dark Ages : Crypts and Tombs (`van.dacrypts`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (C# source inside the mod folder, None; availability yes, MEASURED)
**Adds:** content: 33 defs: ThingDef 25, ThoughtDef 5, ResearchProjectDef 2; 4 patch ops; functionality: Medieval crypt furniture (burial urns, memorials, mausoleum decor); Dark Ages themed. Folder has 2 DLLs but flags show none; art: 3.84 MB of textures but decoded estimate 301.0 MB (INFERRED, suspiciously large)
**Why:** Medieval Dark Ages grave decor is off-genre for a Jawa scavenger starship (brief 4 test 3; named backlog category 'Dark Ages ... rename backlog' in donor_proper_noun_backlog). Retirement: dependants [], 8 research refs from mandrake.rut.researchretag (those just retag research and can be dropped with it), no inheritance; placed memorials in save UNMEASURED so this needs the save check. 301 MB decoded proxy for a decor mod is the largest memory estimate in this batch.
**Problems:** memory 3 texture_decoded_mb_est 301.0 (> 250; proxy) · interaction 2 patched_by_ours_refs 8 · complexity 1 2 DLLs without Harmony flags · log_noise 0 0 errors · maintenance 2 C# source ships; no repo URL
**Holds it in / exit:** researchretag patches 8 research defs; placed urns/memorials UNMEASURED -> None
**Open:** Check the campaign save for placed crypt furniture before removal. | NEEDS OWNER: Does the 'retheme-or-drop' call on Dark Ages mods (undecided per donor_proper_noun_backlog) go to drop for this one?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Darkest Dungeon Incident Sounds (`darkestdungeon.incidentsounds`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 1 SoundDef; 1 patch into Core; functionality: Replaces incident alert sounds with Darkest Dungeon narrator/horror stings; art: 0.82 MB sounds
**Why:** Audio swap from a recognisable game IP; the setting wants its own sound identity (brief 4 test 3 tone). No dependants, no ThingDefs, no placed Things, trivial retirement. Marked card_worthy since sound taste is the owner's.
**Problems:** complexity 1 XML only · log_noise 0 0 errors · maintenance 2 no repo (steam-only); XML only
**Holds it in / exit:** none -> None
**Open:** none | NEEDS OWNER: Keep or cut the Darkest Dungeon incident sounds (borrowed from another game)?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

