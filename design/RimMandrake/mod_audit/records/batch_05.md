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

### Tech Level Enforcement (`summersausages2ttv.techlevelenforcement`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (github, MIT; available: yes)
**Adds:** content: 0 declared defs; 12 patch ops that assign guessed <techLevel> (by defName substrings such as Charge/Laser/Beam/Bow) to ThingDefs lacking one; 24 ThingDefs patched · functionality: Harmony DLL + settings: pawns cannot equip items above their faction's tech level unless whitelisted (starting gear, quest rewards, trader purchases); optional trader limiter · art: 9 textures (1.72 MB on disk)
**Why:** The mod's job (stop a faction using gear above its tech level) is a progression gate whose fit with the scenario is undecided: a scavenger crew that survives on salvaged Empire and Rakatan kit may be exactly what it forbids (brief §1 premise, loop 'gather, improve the ship'), yet a qualitative gate also supports 'no arms race'. Its patches are xpath predicates on defName substrings, not defName targets, so they can match OUR weapons wherever <techLevel> is missing, and the edge counters (patches_ours_refs 0) cannot show that. Retained conservatively until the owner rules; no dependant exists.
**Problems:** log_noise 0 (0 error occurrences, 0 distinct, 0 chatter lines in the 550-mod session) · tps 0 (no tick FLAGs in dll_flags; per-mod TPS UNMEASURED) · memory 3 (texture_decoded_mb_est 432.9 (header proxy, not measured)) · complexity 2 (Harmony, dll_count 1, static_ctors 0) · size 2 (disk_mb 79.05) · maintenance 1 (source verified, last push 2026-10-05) · interaction 2 (12 xpath-predicate patches assign techLevel by name substring to any ThingDef lacking one, which can hit our weapons (not visible in patched_by))
**Holds it in / exit:** no dependant; retained only because the fit is an unanswered ruling -> unfiled: TECH_LEVEL_GATE_RULING_1
**Open:** Does our MandrakeJawa faction techLevel make salvaged gear unequippable under this mod? Needs a live equip test (UNMEASURED); Header proxy says 433 MB decoded from 9 textures that total 1.72 MB on disk: implausible, likely very large dimensions; verify before charging memory; Folder is 79 MB mostly because it ships Source/ build output (bin/Debug, MonoMod nupkgs): not loaded at runtime  **Needs owner:** Should Jawa be forbidden from using gear above their faction's tech level (blocking salvaged Empire or ancient kit), or is using found high-tech gear the point of the scavenger campaign?
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

