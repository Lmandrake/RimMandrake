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

### Decorative Cliffs (Continued) (`mlie.decorativecliffs`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/DecorativeCliffs (github, MIT; availability yes, MEASURED)
**Adds:** content: 22 defs: ThingDef 20 (buildable decorative cliffs), DesignationCategoryDef 1, settings def 1; functionality: Decorative cliff walls that slow movement and provide cover; XML only; art: 0.55 MB textures + 0.42 MB asset bundle; 14.1 MB decoded estimate
**Why:** Cheap, cover-and-slowdown map-dressing; nothing depends on it, nothing of ours touches it. A desert-canyon scenario benefits from buildable cliff dressing, and we have no plan to build it. Source linked and MIT (emipa606/DecorativeCliffs, pushed 2025-06-15).
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · memory 1 texture_decoded_mb_est 14.1 · maintenance 1 repo MEASURED, MIT, pushed 2025-06-15
**Holds it in / exit:** supplies buildable cliff decor we have not planned -> None
**Open:** none
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Defensive Positions - Forked (`gondragon.defensivepositions`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 16 defs: KeyBindingDef 13, JobDef 1, ThingDef 1; functionality: One-click send-to-battle-station for drafted colonists; small Harmony DLL with map component; art: 0.28 MB textures
**Why:** QoL that required_mods.md line 1336 and 1503 selects (Forked version for 1.6). Passes the ceiling test trivially (brief 4 test 4). Nothing of ours touches it. Folder carries only a 1.6 version.
**Problems:** complexity 2 one Harmony DLL, static_ctors 3 · tps 1 map_component_tick FLAG, tiny content · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo URL verified; shipped DLL only
**Holds it in / exit:** ruled in required_mods.md line 1336 -> None
**Open:** none
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Designator Shapes (`merthsoft.designatorshapes`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/merthsoft/designator-shapes (github, Unlicense; availability yes, MEASURED)
**Adds:** content: 60 defs: DesignatorShapeDef 37, OverlayGroupDef 12, DrawStyleDef 11; functionality: Build, mine and zone in shapes (circles, lines, fills); Harmony DLL + C# source (39 .cs); art: 0.34 MB textures
**Why:** Tooling QoL for the colony-builder, patched by VME memes mods only; Unlicense, pushed 2025-08-17. Nothing ours depends on it, and it is a pure interface aid.
**Problems:** complexity 2 one Harmony DLL, static_ctors 2 · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 repo MEASURED, pushed 2025-08-17 · interaction 1 patches vanilla; alphamemes/vmemese patch it
**Holds it in / exit:** none -> None
**Open:** none
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Dubs Bad Hygiene - Thirst (`dubwise.dubsbadhygiene.thirst`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/Dubwise56/Dubs-Bad-Hygiene (github, None; availability yes, MEASURED)
**Adds:** content: 0 defs and no XML on disk (xml 0.0 MB; textures 0.33 MB only); functionality: Adds the Thirst need on top of Dubs Bad Hygiene Lite; the Thirst need and drinking jobs live in the Lite assembly (our Sarlacc source cites `DubsBadHygiene.Need_Thirst` in the Lite defs), so this add-on is a switch plus art (INFERRED); art: 0.33 MB textures
**Why:** The one piece of Dubs Bad Hygiene the owner accepted: design/Jawa/mods/forbidden_mods.md lines 155-160 (rev. 2026-08-04: THIRST-only ADOPTED), and the thirst liability is built into xenotype heat/thirst design. Our code references it: RimMandrake/FlowWorks RM_ColoredWaterBottles.xml MayRequires Dubwise.DubsBadHygiene.Thirst, and the liquids framework design lists 'DBH Lite + Thirst add-on' as a v1 seam. Water scarcity is the intended mechanical pressure (brief 1).
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 Dubs repo linked, pushed 2026-09-23 (monorepo of Bad Hygiene)
**Holds it in / exit:** FlowWorks MayRequire (RM_ColoredWaterBottles.xml); liquids_framework_design.md v1 seam; Sarlacc breach-flood relies on the Thirst need (MapComponent_SarlaccBreachFlood.cs) -> None
**Open:** Confirm what the add-on file actually enables (it ships no XML).
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Dubs Bad Hygiene Lite (`dubwise.dubsbadhygiene.lite`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/Dubwise56/Dubs-Bad-Hygiene (github, None; availability yes, MEASURED)
**Adds:** content: 246 defs: ThingDef 71, JobDef 27, ResearchProjectDef 22, WorkGiverDef 21, ThoughtDef 17, DubsModOptions 15, SoundDef 11, HediffDef 8; functionality: Toilets, bathing, hygiene needs and moods, drinking jobs and the Thirst need base; 4 DLLs with Harmony and tick flags, 28 static constructors, 22.5 MB; art: 8.1 MB textures; 99.8 MB decoded estimate
**Why:** Thirst runs on Lite, and Thirst is accepted (forbidden_mods.md lines 155-160), so Lite stays while Thirst stays: FlowWorks MayRequires Lite (RM_ColoredWaterBottles.xml), Sarlacc's mechanism is verified against Lite's NeedDefs, and mandrake.rut.researchretag patches 58 of its research defs. Cost is real: 28 static ctors and 4 DLLs, and the 3 log errors are research-view coordinate collisions against our RUT_Tree_Hearth. The full sim stays forbidden; Lite still ships toilets and bathing as default content, which the 2026-08-04 ruling did not fully address.
**Problems:** complexity 3 static_ctors 28 (> 20), 4 DLLs, Harmony · tps 2 comp_tick, comp_tick_rare, map_component_tick FLAGS; plumbing/need ticking on a colony; UNMEASURED · memory 2 texture_decoded_mb_est 99.8 (proxy) · log_noise 1 3 occurrences; 'Config error in ModernFixtures: same research view coords and tab as RR_Furniture (RUT_Tree_Hearth)' · interaction 2 patched_by_ours_refs 58 (researchretag); Dubs uses a RUT tree · size 2 disk_mb 22.54
**Holds it in / exit:** Thirst add-on dependant (dubsbadhygiene.thirst); FlowWorks MayRequire; Sarlacc source; researchretag 58 refs -> None
**Open:** Are Lite's toilets, showers and hygiene need switched off in its settings (DubsModOptions 15)? If not, the forbidden full-sim creeps in through Lite. | NEEDS OWNER: Do you accept Lite's toilets, bathing and hygiene mood effects as the cost of Thirst, or should they be switched off or cut?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Dubs Mint Minimap (`dubwise.dubsmintminimap`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Dubwise56/Dubs-Mint-Minimap (github, None; availability yes, MEASURED)
**Adds:** content: 8 defs (SoundDef 3, KeyBindingDef 2, ThingDef 2); functionality: Adds an on-screen minimap with options and a ping tool; 9 MB DLL; art: 0.79 MB textures
**Why:** UI QoL (brief 4 test 4), Dubs repo linked and pushed 2026-09-21. Named as an active neighbour in the Messy Conduit design (messy_conduit_design_2026-10-02.md 8.9). One caution: a minimap can show terrain the Route-B fog hides; I did not measure it. Nothing ours touches it.
**Problems:** complexity 2 two DLLs, Harmony, static_ctors 8 · size 2 disk_mb 11.32 (9.1 MB assemblies) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 repo MEASURED pushed 2026-09-21
**Holds it in / exit:** none -> None
**Open:** Does the minimap draw fogged or unexplored cells under NWN Real Fog of War?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Engines Unlimited (`nep.enginesunlimited`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 0 defs; 1 patch op (xpath without a defName); ships a 2.9 MB non-standard file; functionality: Removes the limit on how many engines a gravship can use; art: 0.43 MB textures
**Why:** Redundant and wrong-direction. design/Jawa/worldbuilding/gravship_flight_invariants.md (lines 183, 352-362) records that Engines Unlimited patches every thruster to maxSimultaneous 9000 and the live def reads 20 small / 10 large from Bigger Gravships (redmattis.biggergravship, in the list), which patches after all XML: the mod does not survive. Its intent (unlimited engines) also runs against the owner's caps. Retirement: dependants [], no defs, no inheritance. Doc claims were measured live; I re-read none of it.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source · interaction 2 patches every thruster defName-less; overridden by Bigger Gravships
**Holds it in / exit:** none -> None
**Open:** The invariants doc is dated; re-read thruster maxSimultaneous live if the cap matters.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Epochs - Incense (`det.epochsincense`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 8 defs: EffecterDef 2, FleckDef 2, ThingDef 2, ThoughtDef 2; functionality: Incense burners for churches and ritual rooms, with smoke effects and a mood thought; depends on VFE Framework; art: 1.18 MB textures; 15.9 MB decoded estimate
**Why:** Decorative ritual item from a medieval-church-flavoured 'Epochs' mod set; nothing depends on it, and Ta'Baa's theology and Rakata ritual spaces are ours to dress. Under the donor-port ruling its two ThingDefs are portable. Exit: unfiled port or drop, not urgent.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source · memory 1 texture_decoded_mb_est 15.9
**Holds it in / exit:** none; placed incense UNMEASURED -> unfiled: EPOCHS_INCENSE_PORT_OR_DROP
**Open:** none
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Epochs - Pyrinth (`det.epochspyrinth`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 13 defs: ThingDef 11 (ore, torches, heaters, braziers, pylon, blade), EffecterDef 2; functionality: Non-refuelable torches, heaters and braziers from pyrinth ore; the mod absorbed into our tier; art: 1.92 MB textures; 37.1 MB decoded estimate
**Why:** We already built the absorbed copy: src/RimMandrake/Pyrinth (`mandrake.rm.pyrinth`) preserves the defNames verbatim and is explicitly NOT YET DEPLOYABLE because loading both collides (its About, lines 15-17). CRYSTAL_INGEST_EXECUTION_1 is done and gated the Lantern Deeps scatter by patching the live donor def. Holding it in: mandrake.rm.biomes (1 ref), Pyrinth (1 ref) and the Lantern Deeps gate patches; so the donor stays until a retirement item swaps in the absorbed pack.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source · interaction 2 patched_by_ours_refs 2; same-defName collision if the absorbed pack is deployed alongside
**Holds it in / exit:** Lantern Deeps gate patches the LIVE donor (RUT_LanternDeepGatePyrinth.xml); mandrake.rm.biomes and mandrake.rm.pyrinth patched_by refs; absorbed pack dormant by design -> CRYSTAL_INGEST_EXECUTION_1 (done) / unfiled: EPOCHS_PYRINTH_RETIRE_ACTIVATE_RM_PYRINTH
**Open:** Which step flips: remove the donor and activate rm.pyrinth in one load round?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Extra Explosion Effects (`keshash.extraexplosioneffects`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (C# source inside the mod folder, None; availability yes, MEASURED)
**Adds:** content: 12 FleckDefs; one Harmony DLL with C# source (10 .cs); functionality: More explosion visual effects; the Harmony part renders them; art: 0.26 MB textures
**Why:** Cosmetic; ships its C# source in the folder, which makes any later fix ours to carry. Sits beside Better Explosions (nephlite.advexplosions), another explosion visual mod; I did not measure a conflict. Nothing ours touches it.
**Problems:** complexity 2 one Harmony DLL, no static ctors · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 source ships in folder; no repo URL verified · interaction 1 adds flecks; overlaps Better Explosions (not measured)
**Holds it in / exit:** none -> None
**Open:** Pair with Better Explosions: do their flecks double up?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### FancyRats+ (`tyrannidae.fancyratsplus`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 0 declared defs; 16 patch ops (FancyRats 6, Alpha Biomes 5, Core 3); functionality: Re-textures the FancyRats pet-rat mod and wires the variants into Alpha Biomes spawns; requires armoredampharos.fancyrats (in the list); art: 0.94 MB textures; 26.8 MB decoded estimate
**Why:** Art-only retexture of a donor pet-rat mod: no donor art is kept (brief 2, memory no-donor-art-kept), and fancy domestic rats are an Earth-recognizable animal the recognizability rule keeps out of starved desert biomes (brief 4 test 3). It also wires itself into Alpha Biomes, a donor we are retiring (donor_retirement_plan). Retirement cost: nothing depends on it; FancyRats itself is outside this batch and needs its own verdict; placed pet rats in the save are UNMEASURED.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source · interaction 2 patches Alpha Biomes spawns (5 ops), a donor with its own retirement
**Holds it in / exit:** none; requires FancyRats (separate verdict) -> None
**Open:** Verdict for armoredampharos.fancyrats must match; if FancyRats is eliminated this follows. | NEEDS OWNER: Do ordinary-looking pet rats belong in a Star Wars-style desert campaign, or should both FancyRats mods go?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Firefoam poppers aren't ugly! (`realify.firefoam`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 0 declared defs; 1 patch op (Core + Odyssey); functionality: Makes firefoam poppers neutral for beauty instead of -8; art: 0.45 MB textures
**Why:** One-line balance tweak to an Odyssey defence building; nothing depends on it, nothing of ours patches the popper. Odyssey is assumed present (DLC ruling).
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source
**Holds it in / exit:** none -> None
**Open:** none
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Fortifications - Neolithic (`aoba.fortress.neolithic`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 7 ThingDefs; 1 patch op (needs Fortified Features Framework); functionality: Neolithic wooden and earthen fortifications (palisades, ramparts); art: 1.45 MB textures; 13.2 MB decoded estimate
**Why:** Tribal-era defensive structures for camps; the loop is 'land, camp, explore' (brief 1) and the player has hard starts, so cheap wall variety is on-genre and we have no plan to build palisades. 7 defs, no code. Depends on Fortified Features Framework, which is not in this batch. Nothing ours touches it.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source · memory 1 texture_decoded_mb_est 13.2
**Holds it in / exit:** supplies defensive building variety we have not planned -> None
**Open:** none
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Giddy-Up 2 - Continued (`memegoddess.giddyup`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/MemeGoddess/GiddyUp2 (github, None; availability yes, MEASURED)
**Adds:** content: 16 defs: JobDef 4, ConceptDef 3, PawnColumnDef 3, RecipeDef 2, HediffDef 1; 98 patch ops (110 into Core, 23 Odyssey, 8 Ideology, facial-animation and Vehicle Framework); functionality: All-in-one fork of Giddy-Up: pawns ride animals, caravan riding, battle mounts; one Harmony DLL with map_component_tick, 96 .cs files shipped; art: 0.73 MB textures
**Why:** Rideable mounts fit a desert caravan crew (required_mods.md line 1044: Banthas as reflavoured pack animals, 'optional Giddy-Up 2'), and it is a mobility/cargo mod within the guardrail. It is hooked into our animal work: gen_creature_register.py lists GiddyUp.CompOverlay, and src/RimStarWars/SWBestiary/Patches/SeasWaterline/Waterline_Lane1.xml documents that a duplicate (biome, animal) wildBiomes pair made BiomeDef.CommonalityOfAnimal throw ArgumentException, killing GiddyUp.MountUtility.BuildAnimalBiomeCache. That means roster edits can break it. 98 patch ops into vanilla give a broad blast radius.
**Problems:** interaction 2 98 patch ops touching Core pawn/animal defs; BuildAnimalBiomeCache breaks on duplicate biome-animal keys (SWBestiary comment) · complexity 2 one Harmony DLL, static_ctors 3 · tps 1 map_component_tick FLAG; mount logic only · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 repo MEASURED, pushed 2026-09-25
**Holds it in / exit:** our creature register and SWBestiary Waterline patch (cache coupling); Vehicle Framework patches it -> None
**Open:** Which of our creatures should be mountable, and does every one carry the Giddy-Up flags?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Gravship Raids (`sk.gravshipraids`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/AhHanie/Rimworld-Gravship-Raids (github-search name match, mit; availability unverified, INFERRED)
**Adds:** content: 44 defs: GravshipRaidPrefabDef 13, GravshipRaidTemplateDef 11, ThingDef 8, IncidentDef 2, PawnsArrivalModeDef 2, RaidStrategyDef 2, ScenarioDef 2; functionality: Enemy gravship and shuttle raids; if the whole raid is killed, the gravship stays and can be captured; Harmony DLL with map component tick; art: 0.84 MB textures; 5.3 MB decoded estimate
**Why:** required_mods.md line 1287: ADOPTED, thematically perfect for a gravship campaign, with a DECISION flagged: protect the single-authored-hull invariant (#15) by preferring salvage-only on captured enemy hulls. That decision is not recorded as made (no ruling found), so the mod stays but with an open question. Fits the Empire as orbital pursuer (brief 1). Also gets prefab structures (PrefabDefs) into map_content_injection_research.md. Pushed 2026-10-08, source match INFERRED.
**Problems:** complexity 2 one Harmony DLL, static_ctors 3 · tps 1 map_component_tick FLAG during raids; UNMEASURED · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 github-search match pushed 2026-10-08, MIT · interaction 2 adds ScenarioDef x2 and raid strategies; our raid-redesigner/Oracle work may share incidents
**Holds it in / exit:** adopted in required_mods.md; single-hull invariant #15 decision pending -> None
**Open:** Can the player keep a captured enemy gravship (second hull) or only salvage it? | NEEDS OWNER: When a raiding gravship is captured, may you keep and fly it, or only strip it for parts (single-hull rule)?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### High Tech Helmets Give Tox Gas Resistance (`ael.tua.helmetsaddtoxresistance`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 0 declared defs; 8 patch ops into Royalty, Core, Biotech; functionality: Gives high-tech helmets (recon, marine, cataphract) toxic gas resistance; art: 0.11 MB textures
**Why:** Small realism patch; nothing depends on it. One thing to watch: our mandrake.rsw.armoury restretches apparel values and 'loads last', so its helmet numbers may shadow or stack with this patch (not measured).
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source · interaction 1 patches vanilla apparel; Armoury restretch could shadow it
**Holds it in / exit:** none -> None
**Open:** Does Armoury re-set helmet toxResistance after this patch?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Knick Knacks - Let your colonists decorate! (`vaguelysexual.modpackageid.goeshere`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 11 defs: ThingDef 7, JoyGiverDef 2, JobDef 1, JoyKindDef 1; functionality: Knick-knack decorations pawns place themselves as a recreation; 1 Harmony DLL; packageId is a placeholder; art: 0.32 MB textures; 24.7 MB decoded estimate
**Why:** Cosmetic joy source; fits an 'overstuffed' lived-in ship (required_mods.md line 1435 wants clutter). Depends on Harmony and VFE Core patch. Placeholder packageId 'vaguelysexual.modpackageid.goeshere' means no clean MayRequire on it. Nothing ours touches it.
**Problems:** complexity 2 one Harmony DLL; comp_tick and world_component_tick FLAGS · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source · memory 1 texture_decoded_mb_est 24.7
**Holds it in / exit:** none -> None
**Open:** Joy: does a decoration-based joy source bypass recreation scarcity?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Medieval Melee Sounds (`bonible.medievalmeleesounds`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 0 defs (census); 9 patch ops into Core sounds; functionality: Replaces melee hit sounds with Monty Python-style clanging recordings; art: 0.67 MB sounds
**Why:** Comedy sound replacement with Earth/medieval identity; the sword-and-lightsaber frontier tone (brief 1, 4 test 3) wants its own audio. Sound-only: dependants [], no ThingDefs, no placed Things, trivial retirement. Marked card_worthy as audio taste.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source
**Holds it in / exit:** none -> None
**Open:** none | NEEDS OWNER: Keep or cut the Monty Python melee sounds?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Medieval Signs (`mewn.medievalsigns`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** https://github.com/MewnGoddess/Medieval-Signs (github, None; availability yes, MEASURED)
**Adds:** content: Census shows 0 defs (blind spot: content is under a 1.5/ folder, 1 xml); the description lists 14 signboards: inn, flophouse, tavern, stables, armory, archery, library, magic shop, butcher, tailor, quarry, blacksmith, apothecary, shop; functionality: Decorative signboards; art: 1.32 MB textures; 41.1 MB decoded estimate
**Why:** Medieval fantasy signage (inn, tavern, magic shop) is off-genre for the scenario (brief 4 test 3; donor_proper_noun_backlog). A starship crew wants its own signage in Aurebesh style, which may be a small owned item. Retirement: dependants [], placed signs in the save are UNMEASURED so run the save check first.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 repo MEASURED, pushed 2025-08-08 · memory 1 texture_decoded_mb_est 41.1
**Holds it in / exit:** placed signs UNMEASURED -> unfiled: SHIP_SIGNAGE_OWN_SET
**Open:** Is a Star Wars style signage set wanted?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Mercer's Backpacks (Continued) (`mlie.mercerbackpacks`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/emipa606/MercersBackpacks (github, MIT; availability yes, MEASURED)
**Adds:** content: 4 ThingDefs (backpack apparel); asset bundle 0.11 MB; functionality: Backpacks as wearable items, with a more colourful stuff-coloured type; art: 0.33 MB textures; 5.9 MB decoded estimate
**Why:** Scavengers carry gear; backpacks fit the salvage crew. MIT repo (emipa606), pushed 2026-07-24. The unknown is whether they add carry capacity or armour that would break the scarcity pillar; I did not read the stat values. Nothing ours touches it.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 repo MEASURED, MIT, pushed 2026-07-24
**Holds it in / exit:** none -> None
**Open:** What do the backpack stat offsets do to carry capacity?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Darkest Dungeon Incident Sounds (`darkestdungeon.incidentsounds`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 1 SoundDef; 1 patch into Core; functionality: Replaces 12 incident and event notification sounds (letters, comms, death, game start) with Darkest Dungeon stings; art: 0.82 MB sounds
**Why:** An explicit design pick: design/Jawa/mods/required_mods.md lines 1140-1145 ('Event-audio / dread-horn layer (mood, not comedy)') chose this focused Incident Sounds replacer for the raid and threat dread cue, no voiceover, pure audio, passes the 7-question test. My first pass called it off-tone and cut it; that was wrong because I read the name, not the doc. Cost is nil: 1 def, no code.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source
**Holds it in / exit:** design pick in required_mods.md 1140-1145 -> None
**Open:** Does Star Wars Themed Sounds (also a planned pick) overlap the same incident sounds? That mod is not in the 589-mod facts I read.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Metal Pipe (`flangopink.metalpipe`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 11 defs: ThingDef 8, SoundDef 3; functionality: Joke items and sounds: the meme 'metal pipe falling' sound effect; one small Harmony DLL; art: 0.06 MB textures + 0.09 MB sounds
**Why:** Meme gag content; the scenario tone is Firefly/BSG frontier (brief 1, 4 test 3). The 2026-08-30 pass called it trivial flavour; trivial is not fit. Retirement: dependants [], placed Things unlikely but UNMEASURED, no inheritance.
**Problems:** complexity 2 one Harmony DLL, static_ctors 1 · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source
**Holds it in / exit:** none -> None
**Open:** none | NEEDS OWNER: Is a meme-sound gag mod acceptable, or cut?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Metal Pipe Horseshoe Replacement (`flangopink.metalpipehorseshoe`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None; availability no, INFERRED)
**Adds:** content: 1 SoundDef; 2 patch ops into Core; functionality: Replaces the horseshoe-throw sound with the metal-pipe meme sound; art: 0.09 MB sounds
**Why:** Meme sound swap for the horseshoes recreation; the same reasoning as Metal Pipe. Horseshoes are a vanilla joy building; nothing depends on this swap. Retirement trivial: no ThingDefs, no dependants.
**Problems:** complexity 1 XML only (dll_count 0) · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 no repo found (steam-only); XML only so the shipped files are the source
**Holds it in / exit:** none -> None
**Open:** none | NEEDS OWNER: Same card as Metal Pipe.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Mood Chain Reaction (`acutus.moodchainreaction`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (C# source inside the mod folder, None; availability yes, MEASURED)
**Adds:** content: 29 defs: ThoughtDef 11, EffecterDef 5, SoundDef 5, HediffDef 3, AbilityDef 2, MentalStateDef 1, TraitDef 1; functionality: Pawns' moods spread through social relationships; a contagious Belly Laugh ability creates mood cascades; 2 DLLs (game_component_tick), C# source shipped; art: 2.4 MB textures + 1.4 MB sounds; 15.7 MB decoded estimate
**Why:** New 1.6-only mod (folder 1.6). In a crew of about 3-8 aboard one ship (brief 1) a mood-cascade layer gives qualitative, character-driven drama, with no power ladder (brief 4 test 4). Nothing depends on it. Marked card_worthy because cascading mental states could spiral on a six-pawn hard start and nobody has measured it; fit is INFERRED.
**Problems:** complexity 2 2 DLLs, game_component_tick FLAG; no Harmony flag · tps 1 game_component_tick only · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 C# source ships; no repo URL verified
**Holds it in / exit:** none -> None
**Open:** Does chain-reaction mood on 6 founders raise breakdown risk beyond the hard start's intent? | NEEDS OWNER: Do you want pawn moods to spread between crew (contagious laughter, panic), given the six-founder hard start?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### More Faction Interaction (Continued) (`mlie.morefactioninteraction`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/MoreFactionInteraction (github, MIT; availability yes, MEASURED)
**Adds:** content: 59 defs: ThingSetMakerDef 15, IncidentDef 13, RuleDef 13, EventDef 5, TraderKindDef 4, WorldObjectDef 4, GenStepDef 2, LetterDef 2; functionality: Faction-interaction events (tributes, trade caravans, dispatches, faction quests); 2 DLLs with Harmony, map/world ticks; art: 0.22 MB textures
**Why:** Not an ELIMINATE because no fit or duplication proof exists. cherry_picker_killlist.md line 59 ('buys nothing for the faction work; keep only if the interaction content is wanted on its own merits', counting 10 assemblies where this facts record shows 2 DLLs) and required_mods.md line 930 PARKs it ('reward-loop needs pillar audit'). Nothing holds it in; no ruling. Kept for now only because the pillar audit has not run. Exit: unfiled MORE_FACTION_INTERACTION_PILLAR_AUDIT.
**Problems:** complexity 2 2 DLLs, Harmony, static_ctors 2 · tps 1 comp_tick, map and world component tick FLAGS · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 repo MEASURED, MIT, pushed 2026-09-04 · interaction 2 adds incidents and ThingSetMakers (reward loop) beside our Oracle/raid-redesigner plot work
**Holds it in / exit:** nothing depends on it; parked in required_mods.md 930 -> unfiled: MORE_FACTION_INTERACTION_PILLAR_AUDIT
**Open:** Run the pillar audit: which of its 13 incidents give rewards that bypass scarcity? | NEEDS OWNER: Do you want faction tributes, dispatches and reward events, or only our own plot incidents?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Numbers (`mehni.numbers`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/Mehni/kNumbers (github, MIT; availability yes, MEASURED)
**Adds:** content: 109 defs: PawnColumnDef 76, PawnTableDef 23, PawnColumnOptionDef 8, MainButtonDef 2; functionality: Spreadsheet-style overview window of colonist or prisoner stats; 4 DLLs with Harmony and a settings screen; 75 .cs shipped; art: 0.12 MB textures
**Why:** Pure information UI (brief 4 test 4 passes trivially). MIT repo (Mehni/kNumbers), pushed 2025-08-28. required_mods.md line 286-288 recorded a '1.6 Temp Don't Download' caution and a hotkey conflict (Z key), which the 1.6 facts do not show as live. Patched by the Main Button Icons fork (3 refs) and Giddy-Up (1). Nothing ours touches it.
**Problems:** complexity 2 4 DLLs, Harmony, static_ctors 5 · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 repo MEASURED, MIT, pushed 2025-08-28 · size 1 disk_mb 6.28
**Holds it in / exit:** bs.mbifvte and memegoddess.giddyup patch it -> None
**Open:** none
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Posthuman Drift Core Mod (`xylthixlm.races.core`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (C# source inside the mod folder, None; availability yes, MEASURED)
**Adds:** content: 17 defs: StatDef 13, ScenPartDef 3, XylRacesCore.Config 1; 3 patch ops into Ideology; functionality: Shared code and assets for the Posthuman Drift xenotype series; does nothing alone. 2 DLLs, Harmony; art: 0.06 MB textures
**Why:** Only reason it is present: xylthixlm.races.titan (Titan xenotype, 12 defs, in the list) depends on it (dependants field). Our UtinniPatches/Patches/AncientsAreRakata.xml deliberately loads after the Titan and 15 other xenotype-patching mods and Removes/Adds on the xenotypeSet node, so we already manage around this family. Whether the Titan stays is a separate verdict in another batch; this one follows it. Exit: drop with Titan; no item.
**Problems:** complexity 2 2 DLLs, Harmony, static_ctors 1 · log_noise 0 0 error occurrences in the 550-mod session · maintenance 2 C# source ships in folder (0 .cs counted); no repo URL
**Holds it in / exit:** xylthixlm.races.titan (dependant); AncientsAreRakata.xml load-order dependency -> unfiled: POSTHUMAN_DRIFT_TITAN_VERDICT
**Open:** Is a vat-grown stone-giant builder xenotype wanted at all? (Titan's own verdict governs.) | NEEDS OWNER: Do you want the Posthuman Drift Titan xenotype in the campaign?
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Realistic Human Sounds (Continued) (`mlie.realistichumansounds`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/emipa606/RealisticHumanSounds (github, MIT; availability yes, MEASURED)
**Adds:** content: 14 SoundDefs; 1 patch; functionality: Replaces pain, death and combat vocalisations of humanlike pawns with realistic recordings; art: 9.5 MB asset bundle; 0.68 MB textures
**Why:** Adopted pick: required_mods.md lines 1148-1153 ('pawns scream when hurt'), pure audio. The unanswered crux is recorded there: does it fire for non-human xenotypes such as Jawa; no source read has answered it. Two DLLs with Harmony; MIT repo pushed 2026-07-22.
**Problems:** complexity 2 2 DLLs, Harmony, static_ctors 1 · log_noise 0 0 error occurrences in the 550-mod session · size 1 disk_mb 10.26 (9.5 MB bundle) · maintenance 1 repo MEASURED, MIT, pushed 2026-07-22
**Holds it in / exit:** design pick in required_mods.md -> None
**Open:** Does it vocalise for Jawa (non-human bodies)? Not answered anywhere I read.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Rimefeller (`dubwise.rimefeller`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Dubwise56/Rimefeller (github, None; availability yes, MEASURED)
**Adds:** content: 150 defs: TerrainDef 48, ThingDef 38, ResearchProjectDef 15, DesignatorDropdownGroupDef 11, RecipeDef 7, JobDef 5, WorkGiverDef 5, SoundDef 5; functionality: Oil industry: drill oil, pump, crack and refine into chemfuel, plastic, composites, napalm; pipe networks; 3 DLLs with Harmony and tick flags; art: 5.2 MB textures; 88.1 MB decoded estimate
**Why:** required_mods.md lines 565-575 records an owner ruling: adopt, pillar-cleared ONLY as non-buildable, found, un-relocatable oil treasure (an infinite pump is fine if discoverable-only with a bounding threat). That condition is an authoring step: strip the buildable designation. I scanned src/ for DerrickDrill, OilWell and CrudeCracker and found them only in mandrake.rut.researchretag (87 patched refs) and nothing that removes buildability, so the condition is unmet in our repo (INFERRED; the scan found 7 files, sanity ok). While buildable it is the 'large-scale automation / free fuel' system the brief excludes (brief 2). Keep, but the authoring step is owed. liquids_framework_design.md line 267 lists Rimefeller only as a deferred seam, and messy_conduit_design lists it as an active neighbour.
**Problems:** interaction 3 patched_by_ours_refs 91; plus patches CE; the pump outputs chemfuel which loosens the fuel leash (required_mods 565) · complexity 3 3 DLLs, Harmony, static_ctors 16 · tps 2 comp_tick and map_component_tick FLAGS; pipe networks tick; UNMEASURED · memory 2 texture_decoded_mb_est 88.1 (proxy) · size 1 disk_mb 18.04 · log_noise 0 0 error occurrences in the 550-mod session · maintenance 1 repo MEASURED, pushed 2026-10-03
**Holds it in / exit:** researchretag 87 refs, armoury 4 refs (and armoury/researchretag About lists); ruling that it is the found oil treasure -> unfiled: RIMEFELLER_DEBUILDABLE_FOUND_OIL_1
**Open:** Is the de-buildable pass done anywhere (live check of designationCategory on OilWell, DerrickDrill, CrudeCracker)? | NEEDS OWNER: Is Rimefeller still wanted as a found-only oil treasure, with all buildable oil machinery removed? Nothing in the repo does that yet.
<sub>facts: batch 13 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

