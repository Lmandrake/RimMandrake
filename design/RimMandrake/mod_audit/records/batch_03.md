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

