# Mod audit batch 05 (code_tweaks_qol_ui_4): 40 mods

Assessor: claude-sonnet-5-5. Facts: `facts/mod_facts.jsonl` generated 2026-10-10T14:47:38-0700. Rubric: `RUBRIC.md`. Brief: `SCENARIO_BRIEF.md`.
Per-mod TPS and memory are UNMEASURED; texture MB are header-based INFERRED proxies. The 550-mod session log (pid 1568) contains every mod below, so `0` log errors is MEASURED.

### Tab-sorting (`mlie.tabsorting`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/TabSorting (github, MIT; available: yes)
**Adds:** content: 10 defs: 9 DesignationCategoryDef (new architect tabs) + 1 IgnoreSettingDef · functionality: C# post-load sorter (Harmony, settings screen) that re-files every building from every mod into Lights/Bedroom/Kitchen/Research/etc. tabs; optional alphabetical sort and manual tab editing · art: 12 small button icons
**Why:** Pure architect-menu organisation: passes the 7-question test trivially (brief §4 test 4). Nothing of ours depends on it (dependants_ours []), but with ~550 mods the build menu needs sorting and we have no plan to build a menu organiser. It re-files OUR buildings too (it sorts by def properties, not by mod), so the tab layout of mandrake.* mods is partly decided by it; that is a UX question for the owner's review passes, not a defect.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 10 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 2.5 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 2, static_ctors 4) · size 1 (disk_mb 0.88) · maintenance 1 (source verified, last push 2026-06-05) · interaction 1 (patches vanilla DesignationCategoryDef only (1 op); re-sorts our buildings at runtime by code (INFERRED, not observed))
**Holds it in / exit:** no dependant; supplies build-menu sorting we have no plan to build -> None
**Open:** It will re-file mandrake.* buildings into its own tabs; check the result in a build-menu screenshot at the next in-game review
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Trade Ships Drop Spot (`smashphil.dropspot`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 1 ThingDef (the drop-spot marker building) · functionality: Harmony DLLs (3): choose where trade ships drop their pods · art: 3 textures
**Why:** Small QoL tool useful on a ship-based colony: the player can keep orbital-trade drops on the pad. No dependant, 0 log errors. Source is not available (steam-only), a maintenance risk, not a reason to drop a 0.26 MB mod; revisit if it breaks on a game update.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 4.7 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 3, static_ctors 1) · size 1 (disk_mb 0.26) · maintenance 3 (no source found (steam-only))
**Holds it in / exit:** no dependant; supplies drop-pod placement we have no plan to build -> None
**Open:** No source found; confirm behaviour with trade drops when the colony is aboard a gravship
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Tradeable Trinkets (Continued) (`mlie.tradeabletrinkets`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/TradeableTrinkets (github, MIT; available: yes)
**Adds:** content: 8 defs: 4 craftable trinket ThingDefs, 1 JobDef, 1 JoyGiverDef, 1 JoyKindDef, 1 ThingCategoryDef · functionality: Craft trinkets as a new joy item; above-average quality sells for profit · art: 20 textures (7.4 MB est) plus 2 asset bundle files
**Why:** Trinkets are a joy item and small trade good; loosely fits a barter setting, but it is donor content with donor art, and the brief says donor art is not kept and content is moving to our own defs (§2 no-donor-art, §3). Not worth REPLACE-NOW: value is tiny and nothing depends on it. Exit is an art/content pass when joy and trade items are reviewed.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 7.4 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 0) · size 1 (disk_mb 0.65) · maintenance 2 (source verified, last push 2025-07-22)
**Holds it in / exit:** no dependant; nothing of ours references it (src search found only the full-mod-list northstar json) -> unfiled: TRINKETS_OWN_JOY_TRADE_ITEMS_1
**Open:** Resale-for-profit of crafted goods is a mild economic loop; no ruling found
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Trading Options Continue (`kearril.tradingoptionscontinue`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 0 defs · functionality: Harmony DLL + settings screen: tune arrival frequency and amounts of caravans, orbital traders, settlement traders and visitors (setting tabs Caravans, Orbital, Settlements, Visitors) · art: 1 icon
**Why:** A direct pressure dial for a thin-trade economy: it sets trader arrival rates per category, which we would otherwise need our own storyteller patch for. The About description is only 'Continued'; function was read from the mod's English ModSettings.xml. No source (steam-only), 0 log errors.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.2 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 0) · size 1 (disk_mb 0.29) · maintenance 3 (no source found (steam-only))
**Holds it in / exit:** no dependant; supplies trader-frequency tuning we have no plan to build -> None
**Open:** Fork of an older Trading Options; no source; check defaults once the storyteller is chosen
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Transparent Substructure (`aelanna.transparentsubstructure`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 5 TerrainDefs (transparent gravship substructure variants) · functionality: Craftable substructure that lets the ground show through; Harmony DLL with 5 static ctors; requires Odyssey · art: 7 textures (4.9 MB est)
**Why:** Odyssey gravship substructure is central to the ship-centred game, so a see-through variant resonates, but this is a tiny cosmetic donor with donor art, and gravship layouts are our own territory (src has substructure work in RimUtinni/ShipShields and UtinniPatches). Kept until we decide whether we own a transparent hull variant; no dependant.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 4.9 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 5) · size 1 (disk_mb 1.03) · maintenance 3 (no source found (steam-only))
**Holds it in / exit:** no dependant; cosmetic only -> unfiled: GRAVSHIP_TRANSPARENT_HULL_OWN_1
**Open:** Does it interact with our gravship layout or RM_SeabedLayer ground rendering? Not tested (UNMEASURED)
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Tribute Demand (`geojak.tributedemand`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (ships-source, no license field; available: yes)
**Adds:** content: 2 defs: 1 IncidentDef (tribute demand raid) + 1 TaleDef · functionality: Hostile group demands items, animals or a colonist as tribute; refuse and a full raid follows; C# source shipped · art: 1 texture
**Why:** A choose-or-fight pressure event, the register the scenario wants: decide what to leave behind, qualitative danger rather than numbers (brief §1, §2). Source is shipped in the folder. Our AftermathRites design considered it but could not verify its IncidentDef name, so no edge exists yet (comment in RM_AftermathRuleDefs.xml). The colonist-as-tribute option needs care with six fixed founders.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.2 (header proxy, not measured)) · complexity 2 (DLL without Harmony flag, dll_count 1, static_ctors 0) · size 1 (disk_mb 0.43) · maintenance 1 (ships its own C# source in the mod folder)
**Holds it in / exit:** no hard dependant; named in our Aftermath design notes as a candidate payload -> None
**Open:** Tribute can demand a colonist: with six fixed founders that is heavy; check settings can disable it; IncidentDef defName not yet verified by our Aftermath work (src/RimUtinni/AftermathRites/Defs/RM_AftermathRuleDefs.xml)
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Triumphant Research (`ferny.triumphantresearch`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/fernyrepos/Triumphant-Research (github, no license field; available: yes)
**Adds:** content: 1 SoundDef; 2 patch ops (Royalty sound) · functionality: C# (Harmony): a popup summarising what each completed research project unlocked; source in folder with git repo · art: 2 textures
**Why:** Pure UI information on research completion; helps a player navigate a large tech tree. Info-only on research unlocks, so it does not fall under the reward-spoiling info ban (brief §2, which concerns map and ruin info). 0 log errors, no dependants. Ships source and has a GitHub repo pushed 2026-09-16.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.2 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 1) · size 1 (disk_mb 6.22) · maintenance 1 (source verified, last push 2026-09-16)
**Holds it in / exit:** no dependant; supplies a research-unlocks popup we have no plan to build -> None
**Open:** none
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Ugh You Got Me (`marvinkosh.ughyougotme`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 0 defs · functionality: Harmony DLL: pawns stop social fighting when badly hurt or in pain; masochists and bloodlusties exempt; lovers may stop · art: 1 texture
**Why:** Small behaviour polish on social fights; no content, 0 log errors. A six-founder crew benefits from fewer fights that injure a founder. Source is not available (steam-only); revisit if a game update breaks it.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.2 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 0) · size 1 (disk_mb 0.53) · maintenance 3 (no source found (steam-only))
**Holds it in / exit:** no dependant; supplies social-fight rules we have no plan to build -> None
**Open:** No source found; risk is maintenance only
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Undraft After Tucking (`madarauchiha.undraftaftertucking`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/MadaraUchiha/UndraftAfterTucking (github-search, wtfpl; available: unverified)
**Adds:** content: 0 defs · functionality: Harmony DLLs (3 files): after a pawn is tucked into bed they are undrafted so medics can work · art: none
**Why:** Tiny QoL fix, no content or art, 0 log errors. The GitHub link in the facts is a name-match search hit (wtfpl, pushed 2025-08-22), not a link the mod declares, so source availability is UNVERIFIED.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.0 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 3, static_ctors 1) · size 1 (disk_mb 2.12) · maintenance 2 (source URL is an unverified name match)
**Holds it in / exit:** no dependant; supplies a one-behaviour fix we have no plan to build -> None
**Open:** Confirm that github.com/MadaraUchiha/UndraftAfterTucking is this mod's repo
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Tech Level Enforcement (`summersausages2ttv.techlevelenforcement`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** none (github, MIT; available: yes)
**Adds:** content: 0 declared defs; 12 patch ops that assign guessed <techLevel> (by defName substrings such as Charge/Laser/Beam/Bow) to ThingDefs lacking one; 24 ThingDefs patched · functionality: Harmony DLL + settings: tech-level gate on equipment, apparel and inventory (disassembles over-tech items), plus a trader stock limiter that hides over-tech goods · art: 9 textures (1.72 MB on disk)
**Why:** Already adopted for its trader stock filter (design/Jawa/mods/required_mods.md: 'Enable Core Enforcement must stay OFF, leave the three Affected Categories ON', decompiled 2026-08-11), which keeps over-tech 'oddities' lateral and supports 'no arms race' (brief §2). The default behaviour is hostile to the scenario (it destroys looted over-tech gear on pickup), so the keep is conditional on that setting staying as documented. No dependants, 0 log errors. Its tech-level patches are xpath predicates on defName substrings, so they can touch OUR weapons that lack <techLevel>; the edge counters (patches_ours_refs 0) cannot show that.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 3 (texture_decoded_mb_est 432.9 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 0) · size 2 (disk_mb 79.05) · maintenance 1 (source verified, last push 2026-10-05) · interaction 2 (12 xpath-predicate patches assign techLevel by name substring to any ThingDef lacking one, which can hit our defs (not visible in patched_by)) · interaction 2 (default config destroys over-tech gear on equip or pickup (itemSaveChance 0); safe only with Core Enforcement OFF)
**Holds it in / exit:** our own docs depend on its trader limiter and a stored settings backup (deployed/config/Mod_3430230860_TechLevelEnforcement.2026-08-11.xml) -> None
**Open:** Verify the stored settings (Core Enforcement OFF) are what the 550-mod session actually loaded; a reset would disassemble looted gear on pickup; Do any of our weapons lacking <techLevel> get a guessed level from its substring patches? Needs a def-level read after load; Header proxy says 433 MB decoded from 9 textures totalling 1.72 MB on disk: implausible, likely huge dimensions; verify before charging memory; 79 MB folder is mostly shipped Source/ build output (bin/Debug, MonoMod nupkgs), not loaded at runtime
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Universal Pregnancy (`universalpregnancy.1trickpwnyta`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/1trickPwnyta/UniversalPregnancy (github, no license field; available: yes)
**Adds:** content: 3 ThoughtDefs; 31 patch ops into Biotech (8 RecipeDef, 6 PawnRelationDef, 5 HediffDef, 3 WorkGiverDef, 3 RitualOutcomeEffectDef, 3 ThingDef, plus precept, research, ritual) · functionality: Removes gender requirements from reproduction, IVF and related relations/rituals so any two partners can conceive; C# source shipped (35 cs), Harmony + settings · art: 2 textures
**Why:** Patches only vanilla Biotech defs (patches_mods ludeon.rimworld.biotech 31; patched_by empty), 0 log errors, GitHub source verified and pushed 2025-11-27. It changes who may reproduce, not how many: it does not raise the ceiling, and the crew is a fixed six with a small cap (brief §1), so population growth is not the lever. Its stated incompatibility is with the Intimacy mod, which is not in the batch universe check here (UNVERIFIED).
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 1 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.8 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 1) · size 1 (disk_mb 0.48) · maintenance 1 (source verified, last push 2025-11-27) · interaction 1 (31 patches target vanilla Biotech defs only)
**Holds it in / exit:** no dependant; supplies relationship/reproduction rules we have no plan to build -> None
**Open:** Stated incompatible with the Intimacy mod; the list holds 'Romance & Intimacy On The Rim' (mianreplicate.romanceandintimacyontherim, FULL.LATEST): whether that is the mod meant is UNVERIFIED; Does our MandrakeJawa xenotype use a gender gene whose reproduction the patch bypasses? Unmeasured
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Vanilla Furniture Expanded - Medical Module (`vanillaexpanded.vfemedical`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 7 defs: 6 ThingDef (medical beds, linkables, color-codable sterile walls) + 1 HediffDef · functionality: XML + one DLL: higher-variety hospital furniture; requires VFE Core · art: 25 textures (22.6 MB est)
**Why:** Furniture-variety donor with donor art; nothing of ours depends on it and the brief says donor art is not kept and content is being moved to our own defs (§2, §3). A ship clinic needs medical beds, but vanilla and our own work can provide them; Tab-sorting references its hospital tab. No urgency to REPLACE: 7 defs, 0 log errors. No source (steam-only); depends on the VFE Core framework which may stay for other reasons.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 22.6 (header proxy, not measured)) · complexity 2 (DLL without Harmony flag, dll_count 1, static_ctors 0) · size 1 (disk_mb 1.56) · maintenance 3 (no source found (steam-only))
**Holds it in / exit:** requires OskarPotocki.VanillaFactionsExpanded.Core (a dependency in the other direction); no dependant on it -> unfiled: SHIP_MEDBAY_FURNITURE_OWN_1
**Open:** Is its sterile-wall colour coding wanted aboard a ship? A taste question, not a ruling gap
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Visit Settlements (`ninagoblin.visitsettlements`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/alt44s/Visit-Settlements (github, no license field; available: yes)
**Adds:** content: 5 defs: 4 HistoryEventDef (theft, mining, vandalism, encroaching penalties) + 1 JobDef · functionality: Harmony DLL (map and world component tick FLAGs): caravans and landed ships can enter friendly settlements without attacking, rent beds, trade, reform a caravan from inside; adds social-consequence history events · art: 7 textures (1.3 MB est)
**Why:** Explicitly ADOPTED for the gravship loop in design/Jawa/mods/required_mods.md '(d) Peaceful town visits': the ship can only land near a settlement, and this gives the enter-without-attacking and consequence surface the loop needs. It is a pillar-clean social-consequence layer (theft and vandalism penalties) rather than a power source. Maintenance is the weak point: source verified but last pushed 2024-08-27 (> 2 years).
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 1 (tick FLAGs map_component_tick, world_component_tick (string presence, not proof); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.3 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 1) · size 1 (disk_mb 0.42) · maintenance 3 (last push 2024-08-27 (> 2 years))
**Holds it in / exit:** adopted in required_mods.md (d); nothing of ours depends on it in code (dependants_ours []) -> None
**Open:** Last push 2024-08-27: confirm it works under 1.6 in the current session (0 log errors suggests it loads)
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Walk the World (`addvans.walktheworld`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 1 WorldObjectDef · functionality: Harmony DLL with a game-component tick: drafted pawns walk to the map edge to enter the neighbouring map, attack or trade with settlements; the map resets when left (terrain and animals respawn) · art: 3 textures (12.2 MB est)
**Why:** Conflicts with the intended travel model: the colony lives aboard the ship and the ship is the only way between places (brief §1 loop, 'ship or nothing' for the sea floor), while this lets pawns walk off one map into the next and 'resets' the map they leave, which would erase a camp or any ship-side work left behind. It also overlaps what Visit Settlements and vanilla caravans/shuttles already give. Kept only until the owner rules because no ruling covers on-foot map-to-map travel and the world has not been remade.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 1 (tick FLAGs game_component_tick (string presence, not proof); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 12.2 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 1) · size 1 (disk_mb 2.18) · maintenance 3 (no source found (steam-only)) · interaction 2 (resets a map when left, which conflicts with persistent gravship camps; no observed test)
**Holds it in / exit:** no dependant; retained only for lack of a ruling -> unfiled: WALK_TO_NEXT_MAP_RULING_1
**Open:** No design doc mentions this mod (searched design/Jawa mods docs and canon): it was never adopted by name; Map-reset on leave would erase gravship camps; untested with the ship (UNMEASURED)  **Needs owner:** Should pawns be able to walk off the map edge into neighbouring maps on foot (the mod resets the map you leave), or does all travel go through the ship and landings?
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Wandering Caravans (`ogliss.g223.wanderingcaravans`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 4 defs: 3 IncidentDefs + 1 WorldObjectDef · functionality: Four DLLs (6.2 MB): off-chance wandering caravans separated from their trade train appear near the colony with potentially valuable inventories · art: 1 texture
**Why:** Owner-greenlit ('sounds awesome, add if no red flags', design/Jawa/mods/required_mods.md line 1345) as the overland lane of nomadic trade, paired with Nomad Friendly Quests. 0 log errors. The upside is free loot, so keep an eye on the settings if scarcity feels loose.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.3 (header proxy, not measured)) · complexity 3 (Harmony, dll_count 4, static_ctors 0) · size 1 (disk_mb 6.5) · maintenance 3 (no source found (steam-only)) · interaction 1 (vanilla incident machinery only; patched_by empty)
**Holds it in / exit:** owner adoption recorded in required_mods.md; no code dependant -> None
**Open:** Built for 1.2 and updated; no source found (steam-only); 4 DLLs for 4 defs is a lot of code for the content
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### We Are United (`sl4vp0wer.weareunited`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 1 JobDef; 2 patch ops (ThingDef) · functionality: DLL + settings: right-click a pawn with a colonist selected to try to recruit a related or homeless pawn ('Ask to unite') with a chance based on relation · art: 2 textures (14.6 MB est)
**Why:** Recruiting extra pawns conflicts with the fixed-founders premise (six fixed MandrakeJawa founders; crew 3-8, brief §1) unless the owner wants relatives to join, and a free recruitment verb raises headcount. No design doc names it. Kept until a recruitment ruling exists; nothing depends on it. No source (steam-only).
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 14.6 (header proxy, not measured)) · complexity 2 (DLL without Harmony flag, dll_count 1, static_ctors 0) · size 1 (disk_mb 0.64) · maintenance 3 (no source found (steam-only))
**Holds it in / exit:** no dependant; retained only for lack of a ruling -> unfiled: CREW_RECRUITMENT_RULING_1
**Open:** Fixed founders: should anyone be recruitable at all?  **Needs owner:** Should the crew ever grow by recruiting related or wandering pawns, or are the six founders the whole crew?
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### What's Missing? (`revolus.whatsmissing`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 0 defs · functionality: Harmony DLL: recipe tooltips highlight which ingredients are missing · art: 1 texture
**Why:** Tiny UI help for a large recipe set; 0 log errors, no content. Steam-only source is a maintenance risk only.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 2.1 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 0) · size 1 (disk_mb 0.24) · maintenance 3 (no source found (steam-only))
**Holds it in / exit:** no dependant; supplies recipe tooltip help we have no plan to build -> None
**Open:** none
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### What's That Mod (`co.uk.epicguru.whatsthatmod`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Epicguru/WhatsThatMod (github, no license field; available: yes)
**Adds:** content: 0 defs · functionality: Two DLLs, settings only: adds the source-mod name to every item, building, animal and recipe tooltip; filterable · art: 1 texture
**Why:** A development attribution aid: with 589 mods it tells the owner which mod a thing comes from, which this audit itself relies on. For players it breaks immersion and exposes donor names, and the audience question (brief §5.1) decides whether it ships. Keep while authoring; drop from any shipped list.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 2.0 (header proxy, not measured)) · complexity 2 (DLL without Harmony flag, dll_count 2, static_ctors 0) · size 1 (disk_mb 0.48) · maintenance 2 (source verified, last push 2025-06-25)
**Holds it in / exit:** no dependant; used for owner attribution during development -> unfiled: WHATS_THAT_MOD_DEV_ONLY_1
**Open:** Ships only if the audience question (brief §5.1) says players see donor names
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Work Tab (`fluffy.worktab`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/JiaRG/WorkTab (github, NOASSERTION; available: yes)
**Adds:** content: 3 PawnColumnDefs · functionality: Fork (JiaRG) of Fluffy's Work Tab: replaces the work-priority table with a richer one; Harmony, game and map tick FLAGs, 4 static ctors · art: 94 textures (29.5 MB est)
**Why:** Universal management UI; with a handful of fixed founders and ship jobs a clear work table matters. Our docs note every pawn's work tab 'is shaped by it' (stat_normalization_audit_2026-09-09.md). 0 log errors, GitHub fork verified (last push 2025-07-24, license NOASSERTION). It touches every pawn's work-type columns, so any WorkTypeDef added by our mods will appear in it.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 1 (tick FLAGs game_component_tick, map_component_tick (string presence, not proof); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 29.5 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 2, static_ctors 4) · size 1 (disk_mb 0.85) · maintenance 2 (source verified, last push 2025-07-24) · interaction 1 (adds columns for every WorkTypeDef incl. ours, via code not patches)
**Holds it in / exit:** no code dependant; UI shared by every pawn in the campaign -> None
**Open:** A fork of the original; the original Fluffy repo may be the supported line
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Worldbuilder (`ferny.worldbuilder`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** neutral · **Source:** https://github.com/fernyrepos/Worldbuilder (github, no license field; available: yes)
**Adds:** content: 8 defs (ScenPartDef 3, SoundDef 2, FeatureDef 1, ThingDef 1, WorldObjectDef 1) · functionality: World customisation editor with Harmony DLL and settings; also draws a typed WB_PlanetName field on world creation that our Utinni patch pre-fills · art: 35 textures (78.4 MB est)
**Why:** An authoring tool for the one hand-made world; players never generate or edit worlds (brief §2). What holds it in: our src/RimUtinni/UtinniPatches/Patches/JawaWorld_Name.xml is written around its planet-name field; hard dependency on VFE Core; 16 static ctors; one measured error (a CannibalPirate ConfigErrors NRE). The owner's own docs disagree on whether it is active (SCENARIO_SETTINGS_SPEC.md says it is NOT in activeMods; FULL.LATEST lists it at 372), so the exit is a ruling and a final-paint timing.
**Problems:** log_noise 1 (1 error occurrences, 1 distinct, 0 chatter lines in the 550-mod session; sample: Exception in ConfigErrors() of CannibalPirate: System.NullReferenceException: Object refer) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 2 (texture_decoded_mb_est 78.4 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 16) · size 1 (disk_mb 19.63) · maintenance 1 (source verified, last push 2026-09-12) · interaction 2 (our UtinniPatches JawaWorld_Name.xml is written around its UI patch (src read); patched_by_ours_refs 0 because the xpath targets Core)
**Holds it in / exit:** JawaWorld_Name.xml comments (it makes the planet name typeable); requires OskarPotocki.VanillaFactionsExpanded.Core; world features in the frozen world: UNMEASURED -> unfiled: WORLDBUILDER_RETIRE_AFTER_PAINT_ONCE
**Open:** design/Jawa/worldbuilding/SCENARIO_SETTINGS_SPEC.md says ferny.Worldbuilder is inactive but FULL.LATEST lists it: doc or list is stale (not resolved here); Incompatible with lucius.worldbuilder.brushtools (facts); that mod is not in this batch universe  **Needs owner:** Once the world is painted and shipped as a savegame, do authoring tools (Worldbuilder, WorldEdit) leave the player's mod list?
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### WorldEdit 2.0 (`funkyshit.mods.worldedit.alpha`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** neutral · **Source:** https://github.com/AlphaLeChat/rimworld-worldedit-2.0 (github-search, no license field; available: unverified)
**Adds:** content: 1 WorldTemplateDef · functionality: Harmony DLL + settings: in-game world editor (tile biome, temperature, rainfall, rivers, roads, features, faction bases) · art: 5 textures
**Why:** Adopted by the owner as the human setup-repair and heavy-authoring tool for the one hand-made world (design/Jawa/mods/required_mods.md, 'WorldEdit 2.0 - ADOPTED'), so it has an authoring job now and none for players, who receive the frozen savegame (brief §2 no worldgen). The facts' source link is a GitHub fork, which required_mods.md warns is low-activity with known bugs (use the Workshop build 3590928058). Which build is the one loaded is the open item.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.5 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 1) · size 1 (disk_mb 4.0) · maintenance 2 (source URL is an unverified name match) · interaction 1 (edits world tiles directly; no def patches)
**Holds it in / exit:** owner adoption as authoring tool (required_mods.md); no code dependant -> unfiled: WORLDBUILDER_RETIRE_AFTER_PAINT_ONCE (shared with Worldbuilder)
**Open:** Source link in facts is a name-match to the fork the docs say to avoid; confirm the loaded build is the Workshop one; Space-layer edits may not work under Odyssey (fork notes)  **Needs owner:** Once the world is painted and shipped as a savegame, do authoring tools (Worldbuilder, WorldEdit) leave the player's mod list?
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Xenotype Spawn Control (`bs.xenotypespawncontrol`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/bbradson/Xenotype-Spawn-Control (github, MIT; available: yes)
**Adds:** content: 0 defs; 1 patch op on PawnKindDef (Biotech xenotype hooks) · functionality: Harmony DLL + settings: per-faction, per-pawnkind and per-meme xenotype spawn rates, random unique xenotypes and hybrids, custom-xenotype overview · art: 6 textures
**Why:** Supplies per-faction xenotype control we would otherwise hand-patch: our force_users_build_spec.md lists it ACTIVE for per-pawnkind and per-faction xenotype forcing through its settings window, and agent_supersession_audit.md names it as a racial-mix tool. It also needs Biotech (always present, brief §2). MIT, GitHub source verified. Note it also adds optional random xenotypes and hybrids, which should stay off for a curated cast.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 9.4 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 1) · size 1 (disk_mb 2.17) · maintenance 2 (source verified, last push 2025-07-13)
**Holds it in / exit:** force_users_build_spec.md lists it ACTIVE for xenotype forcing; no declared dependants -> None
**Open:** Settings live in an in-game window, not authorable XML: where is our chosen configuration stored for fresh installs?
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Yayo's Caravan (Continued) (`mlie.yayoscaravan`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/YayosCaravan (github, MIT; available: yes)
**Adds:** content: 0 defs · functionality: Two DLLs, settings, world component tick FLAG: changes the visual of caravans on the world map (zoom-out modes, animation) · art: 2 textures
**Why:** Cosmetic world-map presentation; a ship-and-caravan game still shows caravans on the map. 0 log errors, GitHub source verified (pushed 2026-05-31, MIT). Nothing of ours depends on it. Cosmetic changes to world visuals need the owner's say, but this is a QoL toggle that can be left off in settings.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 1 (tick FLAGs world_component_tick (string presence, not proof); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.9 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 2, static_ctors 3) · size 1 (disk_mb 0.3) · maintenance 1 (source verified, last push 2026-05-31)
**Holds it in / exit:** no dependant; world-map visual we have no plan to build -> None
**Open:** none
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Yayo's Meteor (Continued) (`mlie.yayosmeteor`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/emipa606/YayosMeteor (github, MIT; available: yes)
**Adds:** content: 2 defs: 1 GameConditionDef + 1 IncidentDef (giant meteor) · functionality: Two DLLs, settings only: a giant meteor drops 7-10 s after the alarm, escape to shelter; may leave a generator; first after 45 days, then once or twice a year · art: 2 textures
**Why:** A rare qualitative hazard, the register the owner described for Natural Disasters ('a world that periodically tries to kill you where you stand is the purest argument for a gravship'), without that mod's ruled-world contradictions (no tectonics, no rain) because it is a single impact event. One thing to check: it can leave a generator, which is free power and could undercut the fuel-is-life pillar (brief §1 'Fuel is life'). MIT, GitHub source verified (pushed 2025-06-22).
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.8 (header proxy, not measured)) · complexity 2 (DLL without Harmony flag, dll_count 2, static_ctors 0) · size 1 (disk_mb 0.27) · maintenance 2 (source verified, last push 2025-06-22) · interaction 1 (vanilla incident/game-condition machinery only)
**Holds it in / exit:** no dependant; supplies a hazard incident we have no plan to build -> None
**Open:** Does the generator reward undercut the fuel pillar? Check the settings for a switch; Is a meteor consistent with the Natural Disasters decline for this planet? That ruling was about eleven disasters, not impacts
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Alien Worlds - Tidally Locked (`7f.alienworlds.tidallylocked`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** resonant · **Source:** https://codeberg.org/azey/rw-tidally-locked-world (other-git, no license field; available: unverified)
**Adds:** content: 1 PlanetTypeDef (AlienWorlds.TidallyLocked.PlanetTypeDef) · functionality: Planet type for the Alien Worlds Framework: sun never sets or rises, frozen nightside, habitable day-side sliver · art: 4 textures (34.5 MB est, planet visuals)
**Why:** Ash'karr is a tidally locked world, and our src/RimUtinni/UtinniPatches/Patches/JawaWorld_BiomeMix.xml patches this very PlanetTypeDef (scoreOffset and biomeBlacklist) 'because it configures the game that produces the SOURCE world Ash'karr is painted from'. patched_by_ours_refs is 2 (mandrake.rut.patches), and both Utinni and StarWars patch mods list it in loadAfter. It generates the planet type used for the source world; players never generate (brief §2), so after the world is frozen it has no job. Hard dependency on 7f.alienworlds, which has its own retirement question.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 34.5 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 0) · size 1 (disk_mb 8.2) · maintenance 2 (source link unverified (no push date)) · interaction 2 (our patches edit its PlanetTypeDef (patched_by_ours_refs 2))
**Holds it in / exit:** our JawaWorld_BiomeMix.xml (patches its def); loadAfter in UtinniPatches and StarWarsPatches About.xml; the active planet type is scribed per save by the framework: removal effect UNMEASURED -> unfiled: TIDALLY_LOCKED_RETIRE_AFTER_WORLD_FREEZE_1
**Open:** Source is on Codeberg (not verified by gh api): source availability UNVERIFIED; If the world is remade at the end, does any remake still need this planet type? (brief §5.8 unresolved)  **Needs owner:** After the world is painted and frozen as a savegame, may the tidally locked planet type and the Alien Worlds framework leave the mod list, or does any remake still need them?
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Belt Extractors - VFE Factory Patch (`groovytaco.beltextractors`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** (C# source inside the mod folder) (ships-source, no license field; available: yes)
**Adds:** content: 0 defs · functionality: Harmony DLL (C# source shipped): conveyor belts pull items from adjacent storage buildings automatically; requires VFE Factory (conveyor belts) · art: 5 textures (10.9 MB est)
**Why:** Automated pulls from storage onto belts are large-scale automation, which the 7-question screen excludes as a player system (brief §2 'large-scale automation, infinite storage'), and it makes the ship's hauling and storage constraints less binding (brief §4 test 4). It declares 0 defs and nothing depends on it (dependants []), so retirement is cheap: no placed Things of its own and no ParentName chain. VFE Factory belts it extends stay. Confidence is INFERRED because placed belts in the save were not checked.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 10.9 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 1) · size 1 (disk_mb 0.75) · maintenance 1 (ships its own C# source in the mod folder)
**Holds it in / exit:** no dependant; its behaviour is code over placed VFE belts: save effect UNMEASURED -> None
**Open:** Is VFE Factory itself wanted on a hand-hauling scavenger ship? Out of scope here, see its own batch  **Needs owner:** Should belts be allowed to pull items out of storage automatically (full automation), or does hauling stay a manual job?
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Faction Territories and Vassalage (`jaeger972.factionterritories`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 6 defs: 3 WorldObjectDef + 2 CaravanIncidentEntryDef + 1 MapModeDef · functionality: Harmony DLL (game and world tick FLAGs), settings, requires Map Mode Framework: draws faction territory regions, factions expand by building settlements, invade rivals, vassal outposts, caravan incidents by territory · art: 1 texture
**Why:** The prior audit graded it 'keep, real mechanism not just a map overlay': factions expand and invade by territory, tying raid frequency to settlement count, and it is a candidate mechanism for vault-dungeon access conflicts (outgrown_audit_2026-08-30.md §3). It runs on the frozen world's existing settlements, so it needs no worldgen. Two other mods patch it (mlie.advancedbiomes 2, gravtide.mod 1). Cost to watch: world and game component ticks, and a hard dependency on NozoMe.MapModeFramework (in the list). Source not found (steam-only).
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 1 (tick FLAGs game_component_tick, world_component_tick (string presence, not proof); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 3.0 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 3) · size 1 (disk_mb 0.79) · maintenance 3 (no source found (steam-only)) · interaction 2 (patched_by mlie.advancedbiomes (2) and gravtide.mod (1); faction expansion may alter the hand-made world's settlements)
**Holds it in / exit:** outgrown_audit_2026-08-30.md keep note; requires nozome.mapmodeframework (in FULL.LATEST); patched by mlie.advancedbiomes and gravtide.mod -> None
**Open:** Faction expansion on a hand-frozen world may add settlements the owner did not place: check the settings (brief §2 evictions/one-map)
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Large Pawns (`neku.largepawns`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 0 defs · functionality: Harmony DLL (map component tick FLAG), settings: pawns with bodySize >= 2.5/4.5/10 occupy 2x2/3x3/4x4 cells with footprint-aware pathing, combat and visuals · art: 1 texture
**Why:** Owner-adopted 2026-08-07 (design/Jawa/mods/required_mods.md), and our RimMandrake HugeThings mod integrates with it deliberately: About.xml loadAfter neku.largepawns, and LargePawnsBridge.cs reflects into its settings to reconcile the size ladder (HugeThings is soft: it works at 1x1 without it). Without it the titans stay one cell. Cost: a map component tick and a reflection surface that a Large Pawns update could break. Source not found (steam-only).
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 5 chatter lines in the 550-mod session) · tps 1 (tick FLAGs map_component_tick (string presence, not proof); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.0 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 2) · size 1 (disk_mb 0.98) · maintenance 3 (no source found (steam-only)) · interaction 2 (our HugeThings rewrites its size ladder through reflection and patches at Priority.Last; a Large Pawns update could break the bridge)
**Holds it in / exit:** HugeThings loadAfter and LargePawnsBridge.cs (src/RimMandrake/HugeThings); owner adoption -> None
**Open:** Our bridge is UNVERIFIED against a running game per its own header; the next load round should test it; Steam-only; version 0.24.16 decompile is what the bridge was written against
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Nice Research Tab (`andromeda.niceresearchtab`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (steam-only, no license field; available: no)
**Adds:** content: 20 defs: 13 FineTune, 4 ExtraCategoryDef, 1 LetterDef, 1 MainButtonDef, 1 MilkyWay.SpriteAnimationDef · functionality: Harmony DLL: rebuilds the research window topology/layout; requires Milky Way (andromeda.milkyway) · art: 48 textures (7.3 MB est)
**Why:** Owner-adopted (required_mods.md), useful for the three-gate research tree. Our src/RimStarWars/Armoury/Patches/Warcasket_BuildPathCut.xml documents that it loads at 450 and our patch at 563, so our relabelled node is what it lays out. patched_by lists jellypowered.survivaltools (5) and meathax.showmeyourtools (1), both in the list. It declares incompatibility with 11 other research-UI mods; none of them is in the universe (checked). Source not found (steam-only).
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 1 (tick FLAGs game_component_tick (string presence, not proof); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 7.3 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 2, static_ctors 1) · size 1 (disk_mb 0.82) · maintenance 3 (no source found (steam-only)) · interaction 2 (our Armoury patch targets the order it loads in; third-party Survival Tools and Show Me Your Tools patch it)
**Holds it in / exit:** owner adoption; Armoury Warcasket patch written around its load position; requires andromeda.milkyway -> None
**Open:** Research Reinvented is also in the list and the docs say both are active: confirm they coexist
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### RimHUD (`jaxe.rimhud`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Jaxe-Dev/RimHUD (github, no license field; available: yes)
**Adds:** content: 0 defs · functionality: Harmony DLL, settings: detailed pawn/creature info HUD in the inspect pane or a floating window with warnings for life-threatening conditions · art: 7 textures
**Why:** Adopted pawn-info UI (required_mods.md); information-dense readouts for a small crew and for creatures. 0 log errors, GitHub source verified (pushed 2025-08-15). Nothing depends on it.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.3 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 1) · size 1 (disk_mb 1.17) · maintenance 2 (source verified, last push 2025-08-15)
**Holds it in / exit:** adopted in required_mods.md; no code dependant -> None
**Open:** Its warnings about 'mental breakdown' and wounds are standard; no ruling needed
<sub>facts: batch 05 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

