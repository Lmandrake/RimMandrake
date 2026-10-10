# Mod audit record: batch 03 (code_tweaks_qol_ui_2)

Assessor: claude-sonnet-5-5 (stage 1). Facts: mod_facts.jsonl 2026-10-10T14:47:38-0700. Template: RUBRIC.md section 7.

### Faction Raid Cooldown (Continued) (`mlie.factionraidcooldown`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/FactionRaidCooldown (github, MIT)
**Adds:** content: none (def_total 0) / functionality: Each enemy-faction pawn death adds 12 h (cap 360 h) to a per-faction cooldown before that faction can raid again; optional cooldown readout on the faction screen. Harmony patch on IncidentWorker_RaidEnemy.FactionCanBeGroupSource (dll_flags: harmony, game_component_tick, settings_screen) / art: two small icons (1.4 MB est)
**Why:** It softens raid cadence: more kills mean fewer raids. The campaign's pressure is meant to be qualitative and story-driven (Empire pursuer, Hutt ledger, Ta'Baa clock; brief section 1 and the pillars in section 2), not tuned by a body-count timer. Our own Aftermath mod already treats it as an obstacle: AftermathRuleRunner.cs sets forced = true with a comment recording a CONFIRMED bypass of exactly this mod's FactionCanBeGroupSource patch, and Aftermath lists it in loadAfter (load order only, not a dependency). So nothing needs it, but the interplay with the Empire escalation design (design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md names it) is undecided; keep until the owner rules on whether raid cadence may be player-influenced.
**Problems:** tps 1 tick FLAGS ['game_component_tick']; small content; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.4 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 2 Aftermath (ours) forced=true bypasses its patch; load-after edge in Aftermath About.xml · complexity 2 dll_count 2, flags ['game_component_tick', 'harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 0.12 · maintenance 2 source verified, last push 2025-08-15 (older than one year); supports_1_6 True
**Holds it in / exit:** Aftermath loadAfter (order only); Aftermath forced=true bypass already coded around it; placed Things in save: none (no defs); a saved per-faction cooldown number lives in a game component (UNMEASURED) -> unfiled: RAID_COOLDOWN_RETIRE_OR_BYPASS_FOR_GOOD
**Open:** Should raid frequency be influenced by player kills at all, given the Empire/Hutt/Ta'Baa pressure model? (brief section 2 pillars; no ruling found)
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Fahrenheit and Celsius (`kosaro.fahrenheitandcelsius`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: none / functionality: Shows both Fahrenheit and Celsius in the temperature display (Harmony postfix) / art: 3 tiny UI textures
**Why:** Pure UI convenience (brief section 4 test 4: cosmetic/QoL/UI passes trivially). 0.07 MB, C# source shipped in the folder, 0 errors in the 550-mod session. Nothing of ours depends on it and nothing conflicts; it supplies a display option we would never build.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 0 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · size 1 disk_mb 0.07 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** no dependants; pure UI -> None
**Open:** none
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Gravship Crashes (`arcjc007.gravshipcrashes`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/JohnCannon87/RimworldGravshipCrashes (github, Unlicense)
**Adds:** content: 8 defs: FactionDef, IncidentDef, PawnKindDef, SitePartDef, TerrainDef, ThingDef, ThingSetMakerDef, WorldObjectDef / functionality: Adds map POIs where crashed gravships (from Gravship Exporter and others) can be found; requires Arcjc007.GravshipExporter; one DLL with a settings screen / art: 10 images (23.5 MB decoded est, INFERRED)
**Why:** Thematically on-brand for a ship-centred game with Hutt discard yards and wrecks, and it is wired into ours: UtinniPatches lists Arcjc007.GravshipCrashes in its About.xml and JawaGroundHulk_Register.xml carries MayRequire="Ludeon.RimWorld.Odyssey,Arcjc007.GravshipCrashes" (patched_by mandrake.rut.patches 1). Its dependency Arcjc007.GravshipExporter is in the universe. Unlicense source, pushed 2025-10-17.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 23.5 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 2 our mods reference it / it references ours 1 times: patched_by {'mandrake.rut.patches': 1} · complexity 2 dll_count 1, flags ['settings_screen'], static_ctors 0 · size 1 disk_mb 4.88 · maintenance 1 source verified, last push 2025-10-17; supports_1_6 True
**Holds it in / exit:** mandrake.rut.patches JawaGroundHulk_Register.xml (MayRequire) and About.xml entry; hard dependency on arcjc007.gravshipexporter -> None
**Open:** Does a random crashed-gravship POI collide with the hand-authored premise of one Rakatan ship? (brief section 1, not a ruling gap, just a design check)
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Gravship Range On Map (`imagitama.rimworldgravshiprangeonmap`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/imagitama/RimWorldGravshipRangeOnMapMod (github, MIT)
**Adds:** content: none / functionality: Always draws the gravship's fuel range on the world map (Harmony) / art: 1 texture
**Why:** Gravship range is the campaign's core planning information (fuel is life, brief section 1) and the mod is a 0.39 MB MIT-licensed UI overlay, last pushed 2025-08-12. Nothing of ours touches it and we have no plan to build the same overlay.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.6 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · size 1 disk_mb 0.39 · maintenance 2 source verified, last push 2025-08-12 (older than one year); supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** Confirm the overlay reads the player gravship range, not a modded fuel model (UNVERIFIED; check once gravship fuel rework lands).
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Guaranteed Ancient Dangers (`arti.shrinez`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: none (def_total 0) / functionality: Raises the 25% chance of an Ancient Danger on a newly generated map to 100% (Harmony); description admits AI-assisted authorship / art: none
**Why:** It forces an extra hazard-and-loot site onto every generated map. The campaign's hand-authored encounters and 'no arms race, qualitative danger' pillar (brief section 2) leave no job for a global switch that makes every landing contain sealed-room loot, and the 'ruin-cheese / reward' exclusions in forbidden_mods.md point the same way. It owns no defs (def_total 0), nothing in the universe depends on it, nothing inherits from it. If extra ancient dangers are wanted they belong in our biome/map content, placed deliberately.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.3 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · size 1 disk_mb 0.23 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** no dependants; no defs, so no placed Things in the save -> None
**Open:** Compatible with Map Designer per its text; irrelevant once removed.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Hunting Traps (`hazn.huntingtraps`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (steam-only, no licence in facts)
**Adds:** content: 3 defs: ThingDef (the trap), ResearchProjectDef, ResearchTabDef / functionality: Small trap that passively catches animals over time; fuelled with kibble or raw plants (comp_tick, comp_tick_rare, settings) / art: 2 small textures
**Why:** Adopted already: mandrake.rut.researchretag lists hazn.huntingtraps and patches its research 4 times (patched_by_ours_refs 4), so the research tab/project is retagged into our tree. A passive food source fits scarcity play if kibble fuel is itself scarce, and it is tiny (0.11 MB). Source is not found in the facts (workshop-only), which is the main risk.
**Problems:** tps 1 tick FLAGS ['comp_tick', 'comp_tick_rare']; small content; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.5 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 2 our mods reference it / it references ours 4 times: patched_by {'mandrake.rut.researchreta · complexity 2 dll_count 1, flags ['comp_tick', 'comp_tick_rare', 'settings_screen'], static_ctors 0 · size 1 disk_mb 0.11 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** mandrake.rut.researchretag patches (4 refs) and About.xml entry; placed traps in the save: UNMEASURED -> None
**Open:** Does a passive trap fit 'no large-scale automation'? (single building, low risk)
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### I will be back (`hailuan.iwbb`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no licence in facts)
**Adds:** content: 2 defs: IncidentDef CBC_Incident ('come back', category Misc, baseChance 250, Map_PlayerHome) and a ThoughtDef (+5 mood, 5 days); folder name ComeBackColony / functionality: A departed companion comes back to the colony (IncidentWork_ComeBack); one DLL / art: 1 texture (0.72 MB)
**Why:** A random 'a former colonist returns' incident at baseChance 250 adds a population-gaining event the campaign does not own: crew is six fixed founders and 3-8 total (brief section 1), recruitment and returns should be scripted. The mod is Steam-only with no source in the facts and no dependants. It is cheap and silent (0 errors), so removal is not urgent; we lack evidence of whether it ever fires usefully (it needs a previously departed pawn).
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 2.9 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags [], static_ctors 0 · size 1 disk_mb 0.75 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** no dependants; incident and thought defs only -> unfiled: RETURNING_COMPANION_INCIDENT_OWN_OR_DROP
**Open:** Does the owner want any random 'colonist returns' event, or only scripted ones?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Ideology symbols as Ideograms (`kxp.ideosymbolsasideograms`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no licence in facts)
**Adds:** content: 316 defs: ThingStyleDef 315 and one StyleCategoryDef (defs_by_type); ideogram variants built from the base-game and VE Ideology icons / functionality: XML only; 2 patch ops into StyleCategoryDef; requires Ideology DLC / art: reuses vanilla ideology icon art as ideogram textures (10.5 MB decoded est)
**Why:** Purely cosmetic (passes brief section 4 test 4) but its whole art source is vanilla/VE ideology icons, and the 2026-10-05 ruling is that no donor art is kept and vanilla counts as donor (brief section 2, memory/no-donor-art-kept). The Jawa clan's ideoligion will want its own ideograms; until it has them this costs nothing (0.89 MB, no code). No dependants; Steam-only, no source in the facts.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 10.5 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 1 dll_count 0, flags [], static_ctors 0 · size 1 disk_mb 0.89 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** no dependants; pawn/ideology style choices in the save: UNMEASURED -> unfiled: JAWA_IDEOGRAM_STYLE_SET_OWN
**Open:** Will the campaign ideoligion ship its own ideograms? (design/Jawa ideology work, not checked here)
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Imprisonment On The Go! (Continued) (`agentblac.makepawnsprisoners`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no licence in facts)
**Adds:** content: 2 defs: a JobDef and a SoundDef / functionality: Lets the player arrest/make prisoners without a bed available ('mass incarceration far from home'); Harmony, settings screen / art: 3 textures (2.2 MB est)
**Why:** Useful for a crew that moves: capture can happen away from a base and the ship supplies beds later. Small (0.75 MB), 0 errors, no overlap with our work found (grep of src/ and design/ for the packageId: 0 hits). It sits near our pit-as-prison idea (CLAUDE.md, a pit becomes a prison room once a bed is in it), which is a different mechanism and not in conflict.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 2.2 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 0.75 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** No source link in facts (Continued fork of Inglix); verify repo before relying on bug fixes.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Incident Disabler (Continued) (`mlie.incidentdisabler`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/emipa606/IncidentDisabler (github, MIT)
**Adds:** content: none (def_total 0) / functionality: Mod-settings list of every incident (vanilla and modded, plus weather) with toggles to disable any during a running game (Harmony, settings screen) / art: 2 small textures
**Why:** Already adopted with a documented reason (design/Jawa/mods/required_mods.md, ADOPTED, source pulled and 1.6 confirmed). It gives the owner a way to silence any incident from the 550-mod list without editing defs, which matters while the list is being tamed. Safe to add/remove mid-game per its description; MIT, pushed 2025-09-25.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.4 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 2, flags ['harmony', 'settings_screen'], static_ctors 2 · size 1 disk_mb 0.12 · maintenance 2 source verified, last push 2025-09-25 (older than one year); supports_1_6 True
**Holds it in / exit:** adopted in required_mods.md; enables disabling incidents of the other 549 mods -> None
**Open:** none
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Infestations Spawn in Darkness 1.6 (`koth.isid`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: none / functionality: Infestations only spawn in the dark (not deep-drill infestations); Harmony, settings screen / art: 1 texture
**Why:** Tiny (0.88 MB, source in the folder), C# only, 0 errors. A mild threat-timing tweak that touches vanilla infestation spawning; the campaign has its own creature/biome threat design but nothing of ours patches infestation spawn, and it does not raise the ceiling (it reduces nuisance). Low stakes; revisit if an infestation reskin lands.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.2 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 0.88 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** Our ship interior counts as roofed ground-infestable space? Infestation behaviour aboard the gravship is not checked here.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Injured Carry (`haecriver.injuredcarry`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: 1 JobDef / functionality: Lets the player order a pawn to carry/rescue an injured pawn even if not downed (Harmony, settings screen) / art: 1 texture
**Why:** Small QoL (0.41 MB, source shipped, 0 errors). It hauls pawns, so it can interact with any mod that changes carrying; a closed ledger item (BRIDGE_INVENTORY_TRANSFER_REFUSES_ALL_1) lists it among six unconfirmed suspects for an inventory-transfer refusal, and that was never resolved (the item says it could not confirm which mod). That is a lead, not a finding: no evidence it is the cause.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.1 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 0.41 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** Was it ever ruled out as the cause of the bridge inventory-transfer refusal? (closed item BRIDGE_INVENTORY_TRANSFER_REFUSES_ALL_1 lines ~78-85)
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Instant Caravan (`ferny.easycaravanformation`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/fernyrepos/Ferny-s-Easy-Caravan-Formation (github, no licence in facts)
**Adds:** content: none (def_total 0) / functionality: Forms caravans instantly (dev-mode 'form caravan instantly') when no hostile pawns are on the tile (Harmony) / art: 1 texture
**Why:** QoL that skips the caravan-loading dialog wait when safe. The campaign is ship-centred and caravans are a side tool, so impact is low; it does bypass preparation time, but only under no-threat conditions and the 7-question test passes QoL trivially (brief section 4 test 4). Its 14.6 MB is mostly shipped assemblies (13.5 MB across 9 files, one flagged DLL) plus 21 source files: heavier than the feature suggests but still small. Nothing of ours touches it.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.2 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony'], static_ctors 0 · size 1 disk_mb 14.59 · maintenance 2 source verified, last push 2025-06-11 (older than one year); supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** If caravans are meant to be scarce, rare, expensive acts in this campaign, is skipping the formation step acceptable?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Interaction-Area Settings (`mlie.interactionareasettings`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/InteractionAreaSettings (github, MIT)
**Adds:** content: none / functionality: Mod-settings to change the interaction area of joy objects (televisions, horseshoe pins): size, offset, same-room requirement / art: 3 small textures
**Why:** Pure tuning of vanilla joy objects, MIT source, pushed 2026-01-16, 0 errors, no tick flags. Nothing to replace; no overlap with ours found.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 3.8 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 2, flags ['settings_screen'], static_ctors 3 · size 1 disk_mb 0.17 · maintenance 1 source verified, last push 2026-01-16; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** none
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Land On Anything (`nep.landonanything`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: none declared (xml 5 files) / functionality: Odyssey gravship: lets the ship land on tiles blocked by buildings, pawns, terrain or roofs (settings screen, Harmony). Defaults are permissive and must be set per the owner ruling / art: 3 small textures (7.9 MB est)
**Why:** Held in by an owner ruling: GRAVSHIP_LANDING_CRUSH_1 records 'We should not have our own mod... Use the one I downloaded' (2026-09-06) and retired our own crush-landing mod in favour of this one, with allowedToSqishRoofs and allowedToLandOnAnyTerrain forced OFF. Its stated requirement (a ship that size must crush small obstacles) is core to the loop. That item is still marked doing: the full behavioural proof was never watched live, so the mod's behaviour on a live gravship is not yet evidence. Requires Odyssey (DLC, assumed).
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 7.9 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 2 DLLs (6 cs / 2 csproj in git), Harmony, settings; 2.88 MB assemblies · size 1 disk_mb 7.48 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** owner ruling GRAVSHIP_LANDING_CRUSH_1; settings in Config/Mod_3545384484_LandOnAnythingMod.xml must keep the two flags OFF -> None
**Open:** Item GRAVSHIP_LANDING_CRUSH_1 is in state doing: has the crush-landing been proven live since 2026-09-06?; The facts show no settings values; confirm the two permissive flags are OFF in the live config (UNMEASURED here).
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Just Leave Already (`timuttie.justleavealready.fork.mitasamodel`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/mitasamodel/Just-Leave-Already (github, no licence in facts)
**Adds:** content: none (xml 2 files) / functionality: Allows pawns/caravans to leave maps at the edges; a fork by mitasamodel (game_component_tick, Harmony, settings) / art: 1 texture
**Why:** Leaving a map by the edge is a plausible away-team action even in a ship campaign, and the facts show a verified repo (mitasamodel/Just-Leave-Already, pushed 2025-08-28), shipped source, 0 errors. A game_component_tick flag is the only perf hint (small). Not duplicated by our work found in src/ (0 hits).
**Problems:** tps 1 tick FLAGS ['game_component_tick']; small content; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 4.7 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['game_component_tick', 'harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 3.78 · maintenance 2 source verified (git in folder), last push 2025-08-28, older than one year by a month
**Holds it in / exit:** no dependants -> None
**Open:** With a gravship home, should a player be able to walk off-map? It is a design question, not an engine one.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Just Put It Over There (`mlie.justputitoverthere`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/JustPutItOverThere (github, MIT)
**Adds:** content: none / functionality: Caravan trade purchases and guest gifts are placed into storage zones instead of dumped on the ground (Harmony) / art: 2 tiny textures
**Why:** MIT, pushed 2026-09-09, 0.12 MB, 0 errors. It relieves hauling after Bazaar-style trades; our Bazaar (mandrake.rm.bazaar) exists but its trade window is a separate mechanism and no interaction was found in patches. Low risk.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 2.5 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · size 1 disk_mb 0.12 · maintenance 1 source verified, last push 2026-09-09; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** Does our Bazaar trade window deliver items through the same method this mod patches (TradeUtility/caravan drop)? Not checked in source.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Keep Converting (`linnun.keepconverting`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: 1 patch op (ThingDef), no defs / functionality: Moral Guide keeps casting Convert on a chosen target whenever off cooldown until success or invalid (Ideology; game_component_tick, Harmony) / art: 4 small textures
**Why:** Ideology QoL (DLC is assumed present). Does not alter mechanics, only auto-repeats an existing ability. Source shipped, 0 errors. The 'fluid ideology' exclusion in forbidden_mods.md is about player progression systems; this removes clicks without raising the ceiling.
**Problems:** tps 1 tick FLAGS ['game_component_tick']; small content; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.1 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['game_component_tick', 'harmony', 'settings_screen'], static_ctors 2 · size 1 disk_mb 0.22 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** none
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Large Outpost (Continued) (`zal.largeoutpost`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, no licence in facts)
**Adds:** content: 5 defs: GenStepDef 2, IncidentDef 1 (GiveQuest_BanditCampLarge), SitePartDef 1 (OutpostLarge), ThingSetMakerDef 1 (Reward_LargeByDropPod, market value 1700-3200 debug params, AIPersonaCore weighting) / functionality: Random world quest like bandit camps but larger, from a faction, rewards by drop pod / art: 7 textures (OutpostLarge, OldCastle, Prisoner site icons; 3.2 MB est)
**Why:** A random faction-quest generator that hands out drop-pod loot worth thousands of silver. The campaign's story pressure is authored (brief section 1), the world is a hand-built frozen map with a fixed faction cast, and the anti-exponential pillar (brief section 2) excludes free reward streams. The site art is a bandit-camp motif ('OldCastle' icon) with no connection to the Jawa setting (brief section 4 test 3). Retirement cost is low but not measured: no dependants, no ParentName chains (5 defs, none abstract per defs_by_type), but a placed site/quest in the save is UNMEASURED. Steam-only, source not found.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 3.2 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags [], static_ctors 0 · size 1 disk_mb 0.15 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** no dependants; placed OutpostLarge world objects/quests in save: UNMEASURED -> None
**Open:** Check the save for OutpostLarge world objects before removal.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Laser Cannon (`arcjc007.lasercannon`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** resonant · **Source:** https://github.com/JohnCannon87/RimworldLaserCannon (github, Unlicense)
**Adds:** content: 5 defs: ThingDef 3, DamageDef 1 (LaserCannonBeam), SoundDef 1 / functionality: 3x3 turret that fires over walls and can shoot down incoming mortar shells (comp_tick, Harmony, settings) / art: 8 textures (11 MB est); 34 MB of assemblies across 28 files
**Why:** Genuinely on theme (a laser turret) and we already depend on it in the data: mandrake.rsw.armoury patches it twice (patched_by_ours_refs 2): Turrets_DamageDoctrine.xml retunes LaserCannonBeam defaultDamage and the doctrine file gates on mods 'Laser Cannon'; Turrets_Renames also exists. About.xml lists it. That is the Absorbed_* pattern's precursor: donor turret, our numbers. The mortar-intercept ability is the one behaviour in the donor's C# we would otherwise lose. Phase-out follows the weapons absorption pattern (WEAPONS_ABSORPTION_WAVE_1 for Eweb etc.), with the interception decided at that time.
**Problems:** tps 1 tick FLAGS ['comp_tick']; small content; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 11.1 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 2 our mods reference it / it references ours 2 times: patched_by {'mandrake.rsw.armoury': 2} · complexity 2 one DLL flagged (settings, Harmony, comp_tick) but 28 assembly files on disk · size 2 disk_mb 51.33, assemblies 34.13 MB in 28 files (likely bundled libs/packages); source tree · maintenance 1 source verified, last push 2025-10-29; supports_1_6 True
**Holds it in / exit:** mandrake.rsw.armoury patches (2 refs) and About.xml list; placed turrets in the save: UNMEASURED -> unfiled: LASERCANNON_ABSORB_INTO_ARMOURY
**Open:** Is the mortar-shoot-down behaviour wanted (it blunts a threat class)? Would an own turret keep it?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Layered Apparel (`costel.layeredapparel`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Keullaeseu/Multiplayer-Layered-Apparel-Patch (github (name-search match), mit)
**Adds:** content: none declared (xml 4 files) / functionality: Cosmetic apparel layers: per-facing offsets/scale/rotation, uniform sets for groups, separate drafted/default lists; two DLLs, Harmony / art: 20 textures (12.1 MB est)
**Why:** Cosmetic and per-pawn, passes the progression tests trivially. The Jawa art register (canon library, 'cosmetic changes need permission because they can break animated faces' in CLAUDE.md) is about our art, not a cosmetic overlay the player may choose. Risk is render interaction with our apparel and gene head/body renders (not checked). The facts' source URL is a name-search match to a Multiplayer patch repo, not the mod's own repo: UNVERIFIED.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 12.1 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 2, flags ['harmony'], static_ctors 3 · size 1 disk_mb 2.83 · maintenance 2 repo only a name-search match (unconfirmed), last push 2026-10-01; supports_1_6 True
**Holds it in / exit:** no dependants; pawn cosmetic data in save: UNMEASURED -> None
**Open:** Find the real source repo; the facts list only an MP patch repo as a name-search match.; Does it conflict with our animated-face/gene renders? Not checked.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### LightsOut (`juanlopez2008.lightsout`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** neutral · **Source:** https://github.com/NathanIkola/LightsOut (github (name-search match), no licence in facts)
**Adds:** content: none declared; 11 patch ops touching 21 ThingDefs (compat for Simple Utilities: Ceiling, More Furniture, VFE Power) / functionality: Pawns switch off lights and appliances in empty rooms (CompGlower/power-trader postfixes, comp_tick, Harmony, settings); 6 static ctors / art: 1 texture
**Why:** Power thrift is on theme (scarcity), but it is a measured antagonist of our own work. Our LuminousPigment mod carries DeepfireLightsOutCompat.cs, a Harmony prefix pair that stops LightsOut from dousing RM_DeepfireLightProxy and RM_DeepfireWornLightProxy (decompiled: any CompGlower thing whose defName contains 'light' is switchable). atmospheric_base_hook_ecosystem.md calls it a 'direct antagonist' of the Atmospheric compositor ('two mods writing the same field on the same tick') and lists a decision owed: detect-and-refuse or retire it. So it is held in by thematic value only and costs us compat code per new light fixture.
**Problems:** tps 2 comp_tick plus postfixes on every CompGlower and power trader on the map; per-mod TPS UNME · memory 1 texture_decoded_mb_est 2.1 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 3 patches the same light fixtures our LuminousPigment and Atmospheric mods drive; our compat · complexity 2 2 DLLs, Harmony, 6 static ctors, 21 ThingDef patches · size 1 disk_mb 2.7 · maintenance 2 repo only a name-search match (unconfirmed), last push 2026-09-12; supports_1_6 True
**Holds it in / exit:** LuminousPigment compat patch exists (DeepfireLightsOutCompat.cs); Atmospheric compositor shares the same fields (design doc, decision owed) -> unfiled: LIGHTS_OUT_DECISION_ATMOSPHERIC_OWNS_LIGHT_STATE
**Open:** Retire it, or require the Atmospheric compositor to detect and defer to it? (atmospheric_base_hook_ecosystem.md says 'owed')
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Linkable Settings (`mlie.linkablesettings`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/LinkableSettings (github, MIT)
**Adds:** content: 1 def (TabulaRasa.UpdateDef: an in-mod update notice type) / functionality: Settings to change any linkable facility's link range, link amount and link type; adds a Room link type and through-wall linking (Harmony, settings) / art: 4 small textures
**Why:** Tuning of vanilla/modded facility linking, MIT source, last push 2026-03-13, 0 errors. Link range/amount sliders can raise the ceiling if the player maxes them, but the defaults are vanilla and it is a settings screen, not a system. No overlap with ours found (no src/ hits).
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 4.2 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 2, flags ['harmony', 'settings_screen'], static_ctors 3 · size 1 disk_mb 0.25 · maintenance 1 source verified, last push 2026-03-13; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** none
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### LiquidSFX (`dorbo.watersfx`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, no licence in facts)
**Adds:** content: 5 SoundDefs / functionality: Ambient sound for rivers, coasts, still water, lava and marsh (settings screen) / art: 3.1 MB of audio, 1 texture (4.7 MB est)
**Why:** Ambient water sound suits a planet with seas, rivers and a lava biome and passes brief section 4 test 4. Our atmospheric/music design docs list it as part of the sound ecosystem the Atmospheric base must coexist with (atmospheric_base_hook_ecosystem.md, music_protocol.md: 'Water ambience by proximity'), so it is known but not depended on. The no-donor-art rule covers art, not audio, but if the Atmospheric mod takes over biome soundscapes this becomes redundant.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 4.7 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['settings_screen'], static_ctors 0 · size 1 disk_mb 4.12 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** no dependants in the universe; listed in atmospheric_base_hook_ecosystem.md as a coexisting sound mod -> unfiled: WATER_AMBIENCE_FOLDED_INTO_ATMOSPHERIC
**Open:** Does the Atmospheric base plan its own water ambience, making this redundant?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Log After Def Error (Continued) (`mlie.logafterdeferror`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/LogAfterDefError (github, MIT)
**Adds:** content: none / functionality: When XML-to-object parsing logs an error, also prints the offending def's details (Harmony, settings) / art: 2 small textures
**Why:** A debugging aid directly useful for a 550-mod list and for our def authoring (silent def loss traps are a recurring theme in CLAUDE.md). MIT, last push 2025-08-17, 0 errors in the session. It is a dev tool, not content, so it matters to the owner's workflow, not to players; if the list ever ships to others it can be dropped.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 3.5 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 2, flags ['harmony', 'settings_screen'], static_ctors 0 · size 1 disk_mb 0.29 · maintenance 2 source verified, last push 2025-08-17 (older than one year); supports_1_6 True
**Holds it in / exit:** owner/agent debugging workflow -> None
**Open:** Dev-only tool: should it be excluded from any player-facing list? (see brief section 5.1, audience)
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Map Designer (`zylle.mapdesigner`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** neutral · **Source:** https://github.com/Zylleon/MapDesigner (github, no licence in facts)
**Adds:** content: 1 TileMutatorDef; 23 XML files in the folder / functionality: Settings GUI for local map generation: mountains, caves, terrain fertility/water/stone types, amounts of plants, animals, ruins, geysers, ore, rock chunks, plus DLC junk toggles (Harmony). Not a debug-action tool (required_mods.md) / art: 18 textures (7.4 MB est)
**Why:** Adopted as a human repair tool for badly generated landed maps (required_mods.md ADOPTED, Workshop 2111424996) and is in our test tier (modset_builder.py names it). But it is a measured, bisected antagonist of our biomes: its startup pass caps BiomeDef.plantDensity at 1.0 and folds the ratio into wildPlantRegrowDays; the Pyrelands declared 1.55 / 9 days and the running game read 1.0 / 5.81 until we added RM_PyrelandsDensityEnforcer to run after it and win (RM_PyrelandsDensityEnforcer.cs, 'BISECTED 2026-09-18'). Every owned biome that sets plantDensity above 1.0 is exposed to the same edit. Our own map-injection / biome map maker design (biome_map_makers_design_2026-10-10.md) is the long-term way to shape local maps, so this should phase out once our content does the job.
**Problems:** log_noise 1 0 error occurrences, 0 distinct, 5 chatter lines in the 550-mod session (mod was in scope) · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 7.4 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 3 it edits BiomeDef.plantDensity / wildPlantRegrowDays of biomes we own with conflicting int · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 1.21 · maintenance 2 source verified, last push 2025-09-14 (older than one year); supports_1_6 True
**Holds it in / exit:** required_mods.md adoption (repair tool); modset_builder.py tier entry; Pyrelands density enforcer exists purely to counter it -> unfiled: MAP_DESIGNER_PLANTDENSITY_CAP_RETIRE_OR_PATCH
**Open:** Keep it as a landed-map repair tool and tolerate the plantDensity cap (enforcers per biome), or drop it? Other owned biomes beyond Pyrelands with density > 1.0 are not checked here.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Map Preview (`m00nl1ght.mappreview`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/m00nl1ght-dev/MapPreview (github, NOASSERTION)
**Adds:** content: none declared (47 xml, a 1.6/Lunar sub-library) / functionality: Generates a preview of the local map terrain on the world map before landing (Lunar library inside the mod; 19 assemblies, 3.74 MB; 6 static ctors) / art: 14 textures (2.9 MB est)
**Why:** For the owner it is an authoring and review aid: our map-injection research lists it as a C# tool for a 'pre-landing preview' and the biome map makers design names it among the live landform mods. For players it previews a map before they land, which spends the 'unexplored world' feel (brief section 1 'scientific expedition crossing an unexplored world'; forbidden_mods.md excludes reward-spoiling info). Last push 2026-10-10, active. Nothing of ours depends on it.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 2.9 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 one DLL flag set empty, but 19 assembly files and 6 static ctors (Lunar library) · size 1 disk_mb 4.36 · maintenance 1 source verified, last push 2026-10-10; supports_1_6 True
**Holds it in / exit:** no dependants; used in the owner's map review (design docs name it) -> unfiled: MAP_PREVIEW_PLAYER_VISIBILITY_DECISION
**Open:** Should players see terrain previews before landing, or only the owner as an authoring aid?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Mass Lovin' (`udon.masslovein`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no licence in facts)
**Adds:** content: 2 JobDefs / functionality: Three or more lovers sharing a bed all take part in lovin' (Harmony) / art: 2 textures (4.9 MB est)
**Why:** Harmless relationship tweak with no overlap in src/. Steam-only, no source in the facts, so bug-fix risk sits with the author. It does nothing for scarcity or the ship loop but costs nothing measurable (0.55 MB, 0 errors). Low-value keep.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 4.9 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · size 1 disk_mb 0.55 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** Is a polyamory-enabling mod wanted for a crew of three to eight? Pure taste; not escalated.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Meaningful Encounters (`sirdarkelf.meaningfulencounters`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: 2 defs: JobDef, WorkGiverDef / functionality: Toggle Interaction on visitors/traders/refugees so wardens socialise with them like prisoners; toggling a hostile marks them for later (world_component_tick, Harmony, settings) / art: 4 textures (5.9 MB est)
**Why:** The Chronicle design explicitly coexists with it: plot_mechanisms_wave.md says it 'lets the player MARK a raider by hand so he recurs... No conflict - ours is automatic, theirs is the player's thumb', and the mod is live in the session. It supports the recurring-characters feel of a travelling crew (Firefly-style, brief section 1). A world_component_tick flag is the only perf hint. C# source is shipped in the folder; 0 errors, 1 chatter line.
**Problems:** log_noise 1 0 error occurrences, 0 distinct, 1 chatter lines in the 550-mod session (mod was in scope) · tps 1 tick FLAGS ['world_component_tick']; small content; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 5.9 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony', 'settings_screen', 'world_component_tick'], static_ctors 1 · size 1 disk_mb 2.27 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** named in plot_mechanisms_wave.md as coexisting -> None
**Open:** none
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Mine Sight (`rabiosus.minesight`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no licence in facts)
**Adds:** content: none / functionality: Highlights mineable ores while the Mine designator is active; hold Shift to designate a whole vein (Harmony, settings) / art: 1 texture
**Why:** UI QoL (brief section 4 test 4). It highlights ore the player can see; it does not reveal hidden ore. 0.42 MB, 0 errors. Source not found in the facts.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.1 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 0.42 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** Check it only highlights visible/known ore, not fogged ore (UNVERIFIED).
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### MinifyEverything (`erdelf.minifyeverything`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, no licence in facts)
**Adds:** content: 1 ThingCategoryDef; patches runtime defs / functionality: At startup marks every building in the def database minifiable (2 DLLs, 13 assembly files, 7.36 MB, Harmony, settings) / art: 1 tiny texture
**Why:** It rewrites the minifiability of every building including ours, so it can make our fixed structures (FlowWorks canal/door-family pieces, biome-kit buildings, anything meant to stay put) movable, and it undoes the 'decide what to leave behind' tension that drives the loop (brief section 1: improve the ship, then decide what to leave behind). It is a runtime def mutation, so interactions with our defs are not visible in patch edges (xpath-based, lower bound). The better pattern is explicit canMinify patches on the things we do want portable. Held in only by being a harmless default for the owner's current play; nothing depends on it.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 0.8 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 2 mutates canMinify on ALL buildings at runtime, including ours; invisible to patch-edge ana · complexity 2 2 DLLs, 13 assembly files (7.36 MB), Harmony, settings; no tick flags · size 1 disk_mb 8.28 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** no dependants; minified things in the save (MinifiedThing instances of non-vanilla buildings): UNMEASURED -> unfiled: MINIFY_ALLOWLIST_PATCH_REPLACES_MINIFYEVERYTHING
**Open:** Does the owner want everything packable (convenience), or should leaving-behind be a real cost? Which of our buildings must NOT be minifiable (pits, canals)?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### MiningCo. Alert speaker (Continued) (`mlie.miningcoalertspeaker`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** neutral · **Source:** https://github.com/emipa606/MiningCoAlertSpeaker (github, MIT)
**Adds:** content: 6 defs: HediffDef 2, SoundDef 2, ResearchProjectDef 1, ThingDef 1 / functionality: Alarm speaker building that warns of raids and has a light signal; MiningCo brand text (XML-heavy: 44 xml files for translations) / art: 6 textures, 2 sounds
**Why:** Adopted 2026-08-08 for 'strong thematic fit' (required_mods.md) and held in by our research retagging: mandrake.rut.researchretag patches it 7 times and lists it in About.xml. But 'MiningCo.' is on the off-lore proper-noun rename backlog (donor_proper_noun_backlog.md: retheme-or-drop undecided, brief section 3), and the alarm itself is a small utility we could make ourselves. Keep it while the retag stays; the exit is the retheme/own-version decision.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.6 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 2 our mods reference it / it references ours 7 times: patched_by {'mandrake.rut.researchreta · complexity 2 dll_count 1, flags [], static_ctors 1 · size 1 disk_mb 0.31 · maintenance 1 source verified, last push 2026-09-29; supports_1_6 True
**Holds it in / exit:** mandrake.rut.researchretag patches (7 refs) and About.xml entry; placed speakers in the save: UNMEASURED -> unfiled: MININGCO_FAMILY_RETHEME_OR_OWN
**Open:** MiningCo. is both ADOPTED (required_mods.md 2026-08-08, 'strong thematic fit') and on the proper-noun rename backlog. Retheme, keep as is, or drop?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### MiningCo. DrillTurret (Continued) (`mlie.miningcodrillturret`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** neutral · **Source:** https://github.com/emipa606/MiningCoDrillTurret (github, MIT)
**Adds:** content: 6 defs: ResearchProjectDef 2, EffecterDef, JobDef, ThingDef, WorkGiverDef / functionality: Turret-like building that automatically drills nearby ores and natural rock; mining mode switch, can be manned, optional low idle power / art: 13 textures, 2 asset bundles (0.04 MB), 1.7 MB est
**Why:** Adopted (required_mods.md ADOPTED under the 'immobile production rule': a fixed resource generator you must leave behind is pillar-safe). Our patches touch it: mandrake.rut.researchretag 12 refs and mandrake.rm.patches 1 ref (MandrakePatches validation walk mentions it). Auto-mining is a mild automation, so its scale must stay bounded. MiningCo. branding is on the rename backlog; the exit is the same MiningCo retheme-or-own decision.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.7 MB (header proxy, INFERRED; assetbundles 0.04 MB unseen) · interaction 2 our mods reference it / it references ours 13 times: patched_by {'mandrake.rut.researchret · complexity 2 dll_count 2, flags ['settings_screen'], static_ctors 1 · size 1 disk_mb 0.5 · maintenance 1 source verified, last push 2026-08-08; supports_1_6 True
**Holds it in / exit:** mandrake.rut.researchretag (12 refs), mandrake.rm.patches (1 ref); placed drill turrets in save: UNMEASURED -> unfiled: MININGCO_FAMILY_RETHEME_OR_OWN
**Open:** Same MiningCo question; also is an auto-mining turret within 'no large-scale automation'? (single unit, owner adopted it)
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### MiningCo. MMS (Continued) (`mlie.miningcomms`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** neutral · **Source:** https://github.com/emipa606/MiningCoMMS (github, MIT)
**Adds:** content: 4 defs: ResearchProjectDef 2, ResearchTabDef 1, ThingDef 1 (Mobile Mineral Sonar) / functionality: A placed sonar building that scans an area and reveals ore; research tab / art: 12 textures: scan-range effect PNGs up to 3200x3200 give a 171.4 MB decoded estimate (INFERRED); 2 asset bundles 0.64 MB
**Why:** Adopted for the same reasons (required_mods.md) and held in by 18 of our patch references (researchretag 12, mandrake.rut.patches 6). It reveals resource locations, which sits close to the 'reward-spoiling info' exclusion (forbidden_mods.md), mitigated by being a fixed building the crew leaves behind. Memory is the notable problem: five scan-range sprites at 640 to 3200 px square are the proxy's 171 MB, medium severity, header-based only. Same MiningCo retheme-or-own exit.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 2 texture_decoded_mb_est 171.4 MB (header proxy, INFERRED; assetbundles 0.64 MB unseen) · interaction 2 our mods reference it / it references ours 18 times: patched_by {'mandrake.rut.researchret · complexity 2 dll_count 2, flags ['settings_screen'], static_ctors 1 · size 1 disk_mb 1.53 · maintenance 1 source verified, last push 2026-01-16; supports_1_6 True
**Holds it in / exit:** mandrake.rut.researchretag (12), mandrake.rut.patches (6); placed sonars in save: UNMEASURED -> unfiled: MININGCO_FAMILY_RETHEME_OR_OWN
**Open:** Is the sonar acceptable as scouting information or too reward-spoiling?; Are the 3200x3200 scan textures loaded at startup (memory) or on use? Not measured.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Modify Tiles at Game Start (`hali.modifylandingtile`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: none (1 xml) / functionality: Adds dev-mode commands to set a tile's biome or landmarks at world generation; C# source shipped (1 file) / art: 1 texture
**Why:** An authoring tool for the one hand-made world: rimworld_worldmap_loadsavecreate.md lists Hali.ModifyLandingTile as ACTIVE in that workflow, and required_mods.md records it as a per-tile ToolWorld dev-action adoption. Players never generate or edit worlds (brief section 2), and the planet is painted once at the end; after that it has no job. Nothing depends on it and it owns no defs.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 4.7 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags [], static_ctors 0 · size 1 disk_mb 0.54 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** world authoring until the final paint pass; no dependants, no defs -> unfiled: WORLD_AUTHORING_TOOLS_RETIRE_AFTER_PAINT_ONCE
**Open:** Retire with the other world-editing tools (Worldbuilder, My Little Planet, Prepare Landing) after the paint pass?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Mood Alerts (`deadmano.moodalerts`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no licence in facts)
**Adds:** content: none (5 xml) / functionality: Alerts for colonists' negative mood debuffs (settings screen) / art: 1 texture (0.65 MB)
**Why:** UI alert (brief section 4 test 4), 0.8 MB, 0 errors, no tick flag. Colonists are a small crew, so a mood alert is useful. Source not found in the facts.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 0 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['settings_screen'], static_ctors 0 · size 1 disk_mb 0.8 · maintenance 2 no source link in facts (steam-only); not confirmed absent; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** none
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### MutatorWorldIcons (`snobi.mutatorworldicons`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/MaxRodin/MutatorWorldIcons (github (name-search match), mit)
**Adds:** content: none; 1 patch op on PlanetLayerDef (Core) / functionality: Draws icons for animal habitats and wild plants (tile mutators) on the world map (Harmony, settings) / art: 2 small textures
**Why:** For the owner it is a useful readback while painting biomes and mutators (our mandrake.rm.seashores is a tile mutator, and other biome-kit tile mutators exist). For a player it shows habitats on the world map before arriving, which is exploration information the scenario treats as earned (brief section 1, section 2 'reward-spoiling info'). Small and quiet (0.1 MB, 0 errors). The repo link is only a name-search match (UNVERIFIED).
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.7 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 0.1 · maintenance 2 repo only a name-search match (unconfirmed), last push 2026-01-12; supports_1_6 True
**Holds it in / exit:** no dependants -> unfiled: WORLD_MAP_INFO_OVERLAYS_PLAYER_VISIBILITY_DECISION
**Open:** Same question as Map Preview: should players see habitat/mutator info before landing?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### My Little Planet (`oblitus.mylittleplanet`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** dissonant · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: none (4 xml) / functionality: Lets world creation pick planet sizes (subcount/subdivisions); C# source shipped; Harmony, settings / art: 1 texture
**Why:** It is a world-creation tool, which the scenario excludes as a player feature (brief section 2, test 5), but it is wired into our authoring: mandrake.rm.planetpresetprime loads after it and reflectively primes MLP's WorldGenRules.subcount, and its validation walk and the alpha_family_source_review note both name it as part of the minimal list. PlanetPresetPrime calls itself dev-ergonomics only. Whether the frozen planet's saved size needs MLP present at load (a tile count outside vanilla sizes) is UNMEASURED; until that is checked, treat it as required for the save.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.2 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 0.35 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** mandrake.rm.planetpresetprime loadAfter and reflective use; saved planet size dependence: UNMEASURED -> unfiled: MY_LITTLE_PLANET_RETIRE_AFTER_PAINT_ONCE
**Open:** Does the saved Ash'karr world need My Little Planet's size to load? Is a remake expected to regenerate anything (brief section 5.8)?
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### No Forced Slowdown (`dingo.noforcedslowdown`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/GooseBehindTheSlaughter/RimWorld.NoForcedSlowdown (github (name-search match), no licence in facts)
**Adds:** content: none (8 xml) / functionality: Disables the automatic time slowdown and control lock when certain events fire (Harmony, settings) / art: 1 texture
**Why:** QoL; the last push of the name-matched repo is 2024-04-16 (UNVERIFIED that it is this mod's repo), but it ships a 1.6 flag and has produced 0 errors. Forced slowdown is an annoyance on a 550-mod list with many events; removing it would only hurt the owner. Small, no overlap.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 2.6 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · size 1 disk_mb 0.33 · maintenance 3 name-search repo last push 2024-04-16 (> 2 years), UNVERIFIED that it is this mod's source
**Holds it in / exit:** no dependants -> None
**Open:** Repo is only a name-search match and stale (2024-04); confirm it still applies on 1.6.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### No Missing Gene Icons (`mlie.nomissinggeneicons`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/NoMissingGeneIcons (github, MIT)
**Adds:** content: none / functionality: At game start generates missing icons for ChemicalDefs so autogenerated drug-addiction and resistance genes do not use the missing-texture icon (Biotech; Harmony) / art: 6 textures (2.9 MB est)
**Why:** Our own mods add chemicals and drugs (CLAUDE.md records drug defs and Biotech gene generation issues in our content), and this mod removes a class of icon errors for every drug the 550-mod list adds. MIT, pushed 2025-06-29, 1 chatter line, 0 errors. No ours-edges in the facts, but its function is exactly the protection a content project needs.
**Problems:** log_noise 1 0 error occurrences, 0 distinct, 1 chatter lines in the 550-mod session (mod was in scope) · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 2.9 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · size 1 disk_mb 0.17 · maintenance 2 source verified, last push 2025-06-29 (older than one year); supports_1_6 True
**Holds it in / exit:** protects our drug/chemical defs from missing-icon errors (inference, no explicit edge) -> None
**Open:** none
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### No Random Apparel on Ideology Edit (`edern.norandomapparelonideoedit`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (in-mod C# source, no licence in facts)
**Adds:** content: none / functionality: Skips automatic apparel generation for ideoligion roles so editing an ideoligion does not freeze on large mod lists (Harmony; C# source shipped) / art: 1 texture
**Why:** Directly addresses a measured cost class of a 550-mod list: ideoligion editing regenerates required apparel across thousands of apparel defs. Source shipped, 0 errors, small. It changes role apparel generation (disabled for roles), so ideo roles will not auto-receive required apparel; that is consistent with a hand-authored Jawa ideoligion.
**Problems:** tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · memory 1 texture_decoded_mb_est 1.2 MB (header proxy, INFERRED; assetbundles 0 MB unseen) · interaction 1 no edges to our mods in patches (lower bound); incompatible_with none · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · size 1 disk_mb 0.29 · maintenance 1 C# source shipped inside the mod folder; supports_1_6 True
**Holds it in / exit:** no dependants -> None
**Open:** The measured freeze on ideo edit is not in the facts; the benefit is stated by the mod author, not measured here.
<sub>facts: batch 03 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

