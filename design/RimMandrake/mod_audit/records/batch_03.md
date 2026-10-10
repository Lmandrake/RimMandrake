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

