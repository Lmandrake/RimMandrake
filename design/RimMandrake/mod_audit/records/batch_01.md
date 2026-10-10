# Mod audit batch 01: frameworks_libraries (29 mods)

Stage-1 assessor record. Template per RUBRIC.md section 7. Facts: facts/mod_facts.jsonl 2026-10-10.

### Prepatcher (`zetrith.prepatcher`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Zetrith/Prepatcher (github, MIT)
**Adds:** content: none (def_total 0) / functionality: Library plus mod manager that patches the game's own assemblies at startup (before Harmony); bundles Harmony 2.4.2 and PrepatcherAPI 1.2.0 (description). 5 DLLs: 0Harmony, 0PrepatcherAPI, 0PrepatcherDataAssembly, PrepatcherImpl, Prestarter / art: none (1 texture, 5.8 MB est)
**Why:** Four universe mods carry a prepatcher flag in their DLLs (adaptive.storage.framework, redmattis.betterprerequisites, oskarpotocki.vanillafactionsexpanded.core, krkr.rule56), and VFE Core is the base of the Vanilla Expanded family, so removing Prepatcher risks the load of a large part of the list. It is a neutral engine-level library with no gameplay content (brief section 4 tests 1-2). The dependants edge is NOT in modDependencies (dependants is empty), so the reliance is INFERRED from DLL flags, which are string presence, not proof the code path runs. Our own mods do not name it (no src/ or design/ reference found).
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · complexity 3 (Prepatcher + Harmony, 5 DLLs, edits assemblies at startup) · size 1 (6.33 MB) · maintenance 1 (source verified, last push 2026-02-04) · tps U (startup IL patching; per-mod TPS UNMEASURED)
**Holds it in / exit:** DLL prepatcher flag in adaptive.storage.framework (which our mandrake.rsw.armoury requires), VFE Core, Better Prerequisites, krkr.rule56: flags only, not About.xml dependencies -> None
**Open:** Confirm by decompile which of the four flag-bearing DLLs actually call PrepatcherAPI; the About.xml dependants list is empty.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Harmony (`brrainz.harmony`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/pardeike/HarmonyRimWorld (github, MIT)
**Adds:** content: none (def_total 0) / functionality: The runtime patching library every Harmony mod calls (dll_flags harmony); load-order position 2 / art: none
**Why:** 294 universe mods list it as a dependency, 31 of them ours (e.g. mandrake.rm.aftermath, .bazaar, .biomes, .explosivegrowth). Removing it removes every Harmony mod. No replacement is conceivable. (RUBRIC worked example 1, re-derived.)
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · tps U (it is the patch mechanism; cost lands on the patching mods) · size 1 (5.46 MB) · maintenance 1 (source verified, last push 2026-08-16)
**Holds it in / exit:** 294 dependants incl. 31 of ours (dependants_ours) -> None
**Open:** none
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### ludeon.rimworld (`ludeon.rimworld`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (none, None)
**Adds:** content: Base game Core: 6,103 declared defs (ThingDef 800, BackstoryDef 784, SoundDef 596, ThoughtDef 281, JobDef 195 ...) / functionality: The game / art: in resources.assets (not visible to the header census; 10.6 MB est is only the loose PNGs)
**Why:** Cannot be removed. 40 universe mods depend on it, 39 of them ours, and our patches reference its defs 6,712 times (patched_by_ours_refs; mandrake.rut.pawnflavor 5,088, rut.patches 597, rut.researchretag 519). Brief section 2: vanilla art counts as donor art and is to be replaced over time by our art, but that is a per-def content matter, not a reason to remove Core.
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · size 2 (116 MB loose files; art mostly inside resources.assets) · tps U (session-wide ~8-10 TPS on the 550 list is not attributable to Core vs mods)
**Holds it in / exit:** 39 of our mods list it as dependency; 6,712 xpath defName references from our patches -> None
**Open:** Source is the decompiled engine (RimSage), not a repo.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### ludeon.rimworld.royalty (`ludeon.rimworld.royalty`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (none, None)
**Adds:** content: 717 declared defs (ThingDef 121, QuestScriptDef 61, SoundDef 60, BackstoryDef 59, RecipeDef 52 ...) / functionality: DLC expansion / art: in resources.assets / loose PNGs (10.5 MB est understates)
**Why:** Brief section 2: every DLC is a hard prerequisite, for players too. No hard modDependencies from our mods, but our patches reference its defs 112 times (patched_by_ours_refs: mandrake.rut.pawnflavor 41, rut.patches 38, rsw.patches 17, rm.pyrinth 12) and the Galactic Empire is vanilla Royalty `Empire`, reskinned (memory galactic-empire-is-reskinned-vanilla). Three universe mods require it (spacemoth.showknowntechprints, vanillaracesexpanded.archon, zal.spaceports).
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · size 2 (58.24 MB)
**Holds it in / exit:** patched_by_ours_refs 112; Empire faction is reskinned Royalty Empire -> None
**Open:** Royal permits and psycasting are excluded as PLAYER systems (forbidden_mods); that is a Cherry Picker content cut, not a verdict on the DLC.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### ludeon.rimworld.ideology (`ludeon.rimworld.ideology`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (none, None)
**Adds:** content: 2,005 declared defs (ThoughtDef 433, PreceptDef 179, ThingDef 127, ThingStyleDef 111, SoundDef 98, IdeoIconDef 94 ...) / functionality: DLC expansion / art: in resources.assets / loose PNGs (10.5 MB est understates)
**Why:** Brief section 2: DLC hard prerequisite. Our patches reference its defs 5,802 times (mandrake.rut.pawnflavor 5,712, rsw.jawavoice 30, rut.researchretag 30, rut.patches 17), and 28 universe mods require it. The Jawa ideoligion and comedy layer is built on it (required_mods.md).
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · size 2 (54.48 MB)
**Holds it in / exit:** patched_by_ours_refs 5,802; 28 universe dependants -> None
**Open:** mandrake.rut.pawnflavor makes 5,712 references: batch 16 should confirm that is intentional bulk retheming.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### ludeon.rimworld.biotech (`ludeon.rimworld.biotech`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (none, None)
**Adds:** content: 1,339 declared defs (ThingDef 223, SoundDef 175, GeneDef 139, ThoughtDef 86 ...) / functionality: DLC expansion / art: in resources.assets / loose PNGs (10.5 MB est understates)
**Why:** Brief section 2: DLC hard prerequisite. Two of ours hard-depend (mandrake.rsw.starwarsraces, mandrake.rut.birthhatchdemo) and our patches reference its defs 1,593 times (rut.pawnflavor 1,371, rut.patches 114, researchretag 66). The founders are xenotype pawns. Genetics-lab progression is excluded as a PLAYER system (forbidden_mods), a Cherry Picker cut, not a verdict on the DLC.
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · size 2 (66.07 MB)
**Holds it in / exit:** dependants_ours: mandrake.rsw.starwarsraces, mandrake.rut.birthhatchdemo; patched_by_ours_refs 1,593 -> None
**Open:** none
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### ludeon.rimworld.anomaly (`ludeon.rimworld.anomaly`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (none, None)
**Adds:** content: 1,443 declared defs (ThingDef 204, SoundDef 171, FleckDef 123, EffecterDef 90, HediffDef 72 ...) / functionality: DLC expansion / art: in resources.assets / loose PNGs (10.5 MB est understates)
**Why:** Brief section 2: DLC hard prerequisite, and three of ours hard-depend (mandrake.rsw.sarlacc, mandrake.rut.longhunger, mandrake.rut.shipmemory); our patches reference it 84 times. Its role is contested (brief section 5 item 7): a creature reskin library per 01_campaign.md vs a permanent Assailant war per canon_reintegration_plan.md. The verdict does not depend on which is right because the DLC stays either way; only how much of it is Cherry-Picked does.
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · size 2 (100.12 MB)
**Holds it in / exit:** dependants_ours: mandrake.rsw.sarlacc, mandrake.rut.longhunger, mandrake.rut.shipmemory; patched_by_ours_refs 84 -> None
**Open:** Contradiction section 5.7 left unresolved: storyline at zero vs Assailant war canon.; Is the Anomaly storyline (the Assailant war, entities) in play in the campaign, or only its creatures as a reskin library? This decides how much of it gets Cherry-Picked.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### ludeon.rimworld.odyssey (`ludeon.rimworld.odyssey`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (none, None)
**Adds:** content: 1,606 declared defs (ThingDef 336, PrefabDef 159, SoundDef 131, LayoutRoomDef 115, TileMutatorDef 82, PawnKindDef 60, LandmarkDef 45 ...) / functionality: DLC expansion: gravships, orbit, new layers / art: in resources.assets / loose PNGs (10.5 MB est understates)
**Why:** Brief section 2: DLC hard prerequisite, and the gravship is the campaign's centrepiece. Seven of ours hard-depend (mandrake.rm.biomes, rm.gravshiplanding, rm.keelhoist, rsw.swbestiary, rut.empirepursuit, rut.ishkolandmarks, rut.shipshields); our patches reference its defs 995 times (rut.patches 357, rut.pawnflavor 290, rut.ashkarrlandmarkart 100, rm.biomes 39). RM_SeabedLayer is a planet layer built on its layer system.
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · size 2 (90.62 MB)
**Holds it in / exit:** dependants_ours (7 listed); patched_by_ours_refs 995 -> None
**Open:** none
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Adaptive Storage Framework (`adaptive.storage.framework`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/bbradson/Adaptive-Storage-Framework (github, MIT)
**Adds:** content: 9 defs, all AdaptiveStorage.ContentLabelStyleDef / functionality: Storage display framework: graphics change with contents, contents tab, group tab, finer capacity and temperature control (description). 11 DLLs, Harmony + Prepatcher flags, settings screen / art: 9 MB decoded est (INFERRED); no model pack in this mod
**Why:** Our mandrake.rsw.armoury names it a hard dependency (src/RimStarWars/Armoury/About/About.xml line 49) and its Absorbed_AdditionalMods/kotorcore defs use it (ARMOURY_ABSORBED_FRAMEWORK_DEPS_1; closed item KOTORCORE_ADAPTIVESTORAGE_PARENTNAME_1), and five other universe mods require it (adaptive.ideology.storage, adaptive.primitivestorage, adaptive.simplestorage, sbz.gravshipstorage, sbz.neatstoragefridge). It is display-only, so it does not raise the ceiling, and it supports the overstuffed-ship look the owner asked for (required_mods.md). Fit neutral.
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · complexity 3 (Harmony + Prepatcher flags, 11 DLLs) · interaction 2 (required by mandrake.rsw.armoury; patches lwm.deepstorage (1 op)) · memory 1 (9.4 MB decoded est) · tps U (per-mod TPS unmeasured; storage-building graphic updates not measured)
**Holds it in / exit:** dependants_ours: mandrake.rsw.armoury; 5 other universe dependants; absorbed kotorcore defs inherit from its classes (ParentName risk) -> None
**Open:** The dependent storage packs (adaptive.*, sbz.*) are in other batches; their verdicts decide whether this framework outlives them.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Alien Worlds Framework (`7f.alienworlds`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** dissonant · **Source:** https://codeberg.org/maevi/rimworld-mods (other-git, None)
**Adds:** content: 1 def (AlienWorlds.PlanetTypeDef); no planet types of its own / functionality: Framework for new planet TYPES (altered temperature curves, biome whitelists/blacklists, tidal lock), integrates with Worldbuilder; 1 Harmony DLL; 4 static ctors; patches act in WorldGenStep_Terrain / art: 4 textures, 6 MB on disk, 34.5 MB decoded est (INFERRED)
**Why:** It is a world-generation framework (brief section 4 test 5: dissonant; section 2: no worldgen), yet it is wired into how the campaign's SOURCE world was made. Our src/RimUtinni/UtinniPatches/Patches/JawaWorld_BiomeMix.xml patches the TidallyLocked PlanetTypeDef of `7f.alienworlds.tidallylocked` (its header: kept because it configures the game that produces the source world Ash'karr is painted from), UtinniPatches About.xml forceLoadAfter names both mods (lines 81-82), and tidally_locked_world.md records the mod as worldgen-only (FieldPatcher hooks WorldGenStep_Terrain; nothing recomputes temperature at runtime, so it cannot reach the hand-painted frozen save). Runtime need is therefore nil but the authoring/remake path may still use it, and removing it unguarded breaks UtinniPatches' patch target. Held until the final paint/remake settles whether the source world is ever regenerated (brief section 5.8).
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · interaction 2 (patched by our UtinniPatches via the tidallylocked pack) · complexity 2 (one Harmony DLL, 4 static ctors, hooks worldgen) · memory 2 (34.5 MB decoded est (4 textures)) · maintenance 3 (source_url is a codeberg group page, repo not verified)
**Holds it in / exit:** dependant 7f.alienworlds.tidallylocked (in list); UtinniPatches JawaWorld_BiomeMix.xml + forceLoadAfter; a PlanetTypeDef selection may be scribed into the world: UNMEASURED -> unfiled: ALIENWORLDS_RETIRE_AFTER_PAINT_ONCE (also covers 7f.alienworlds.tidallylocked and the JawaWorld_BiomeMix patch)
**Open:** Does the live campaign save carry an AlienWorlds scribe? A removal needs the save read (rimworld-savegame skill).; Is the source-world generation ever re-run, or is the world only repainted by bridge from here on?; Will the Ash'karr source world ever be regenerated through Alien Worlds (the remake), or is the painted save the only world from now on? If only the painted save, this and its Tidally Locked pack can be retired once the save is confirmed free of them.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Biomes! Framework (`biomesteam.coreframework`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: none (def_total 0) / functionality: Code backbone of the Biomes! team mods (comps, map components; a WaterWalker sub-mod sits in its Source/ per required_mods.md); DLL flags comp_tick, comp_tick_rare, map_component_tick, harmony, settings_screen / art: 1 texture, 2.8 MB est
**Why:** Nothing in the universe depends on it: dependants is empty, and the only Biomes! content pack in the list, biomesteam.biomesfossils, is XML-only (dll_flags empty, dependencies = harmony only) and references the family only through `MayRequire="BiomesTeam.BiomesCore,..."` on trader stock generators; biomesteam.biomescore itself is NOT in the universe, so the framework has no consumer. It carries tick code (map_component_tick, comp_tick) that runs for nobody, and Biomes! biome content is overlapped by our one biome mod `mandrake.rm.biomes` (brief section 2). Retirement cost checked: no defs (def_total 0) so no ParentName risk, no placed Things possible from its own content. Older required_mods.md adopted the whole Biomes! stack as an infrastructure dependency, but that premise (BiomesCore present) no longer holds on the 550 list.
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · tps 1 (map_component_tick and comp_tick flags, but no content to tick) · complexity 3 (Harmony + settings screen + 3 tick flags, 3 static ctors) · maintenance 3 (no source linked (steam-only))
**Holds it in / exit:** no dependants (measured); old adoption note in required_mods.md predates the stack's removal -> None
**Open:** Confirm biomesfossils (batch 8/13) is not meant to be paired with BiomesCore; if the owner wants the Biomes! family, this verdict flips.; biomesfossils shows 51 distinct log errors (BMT_GastropodMeat etc.) possibly because BiomesCore is absent: its own batch should read that.; Do you want any of the Biomes! team family (Core, Caverns, Polluted Lands, Fossils) in the campaign? Today only Fossils is present, with no Biomes! Core, so its framework does nothing.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### BiomesKit (Continued) (`zal.biomeskit`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** dissonant · **Source:** https://github.com/CosmicOdeum/BiomesKit (github, MIT)
**Adds:** content: 1 def (WorldGenStepDef) plus 1 patch op into Core / functionality: Framework for adding biomes to world generation with per-biome decoration controls; 1.6 build carries a BiomesKitWorldGenStep -> LateBiomeWorker (biome assignment at worldgen) and dropped the old BiomesKitWorldLayer (closed item BIOMESKIT_RENDER_LAYER_MISSING_1). Description says it is contained within ReGrowth: Core / art: 2 textures, 4.1 MB est
**Why:** Held by one dependant, zal.comigogreaterswamps (Comigo's Greater Swamps, a donor biome mod that REQUIRES BiomesKit or ReGrowth: Core), and donor biomes are still the world's biome defs until the paint pass (brief section 2 and the_one_map.md; section 5.6). It is a worldgen/biome-assignment framework, which the brief rejects in principle (test 5) and our own mandrake.rm.biomes replaces (test 6). Exit: the one-time paint and donor retirement, BIOME_PAINT_ONCE_AT_THE_END_1; when Comigo's swamps go, this goes (ReGrowth: Core, regrowth.botr.core, is in the list and satisfies the same requirement, per the description).
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · complexity 1 (one small Harmony DLL, 1 static ctor) · maintenance 2 (repo linked is the ORIGINAL by CosmicOdeum (last push 2021-07-19); the 1.6 Continued build's own repo is not in the facts) · interaction 1 (patches Core only)
**Holds it in / exit:** dependant zal.comigogreaterswamps; donor biome defs the live save may still use: UNMEASURED (brief section 5.6) -> BIOME_PAINT_ONCE_AT_THE_END_1
**Open:** Is `BiomesKitWorldGenStep` active in practice or irrelevant once the world is a frozen save? (worldgen-only per closed item.); Continued build has no verified repo.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Float Sub-Menus (`kathanon.floatsubmenu`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/kathanon/RimWorld-FloatSubMenu (github, BSD-3-Clause)
**Adds:** content: none (def_total 0) / functionality: Library that lets mods add sub-menus to float menus (description); one Harmony DLL / art: 1 texture, 2.9 MB est
**Why:** Required by kathanon.searchablemenus (Searchable Menus, a quick-search field for any float menu), which is in the list. A QoL library with no content passes the 7-question test trivially (brief section 4 test 4). It stays exactly as long as Searchable Menus does; that verdict lives in whichever batch holds Searchable Menus. Source verified (BSD-3-Clause, pushed 2025-02-01).
**Problems:** log_noise 0 (0 error occurrences, 0 chatter lines in the 550-mod session) · complexity 2 (one Harmony DLL, no tick flags) · size 1 (0.98 MB) · maintenance 1 (source verified, last push 2025-02-01)
**Holds it in / exit:** dependant kathanon.searchablemenus (in list) -> None
**Open:** Verdict follows kathanon.searchablemenus.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Gravship Exporter (`arcjc007.gravshipexporter`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/JohnCannon87/RimworldCustomShipStart (github, Unlicense)
**Adds:** content: 5 defs (ShipLayoutDefV2 4, SketchResolverDef 1) / functionality: Exports a built gravship as a layout to use as the starting ship of a new Gravship-start scenario; 2 DLLs, Harmony, settings screen, source shipped in the folder (52 .cs) / art: 12 textures, 23 MB est; 56.7 MB on disk incl. 34.7 MB of assemblies
**Why:** The campaign's gravship is 'built and exported' (V1.md chain row 11, done) and only the worldmap, gravship and founders survive the expected remake (memory world-remake-is-the-last-step). BRIDGE_CAPABILITY_ROSTER.md (line 550) records `ShipLayoutDefV2` as this mod's def and verifies the mod active in the owner's list; one universe mod (arcjc007.gravshipcrashes, crashed-gravship POIs) depends on it. Keeping it protects the export/re-import path for the one thing that must survive a remake. Fit is resonant: ship-centred campaign (brief section 1). If the ship layout is ever saved as plain defs of ours it could be KEEP-TEMPORARILY, but no item says so.
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · size 2 (56.67 MB on disk (assemblies 34.73 MB, 31 files: likely several version folders)) · complexity 2 (2 DLLs, Harmony, 0 static ctors) · memory 1 (23.3 MB decoded est) · maintenance 1 (source verified, Unlicense, last push 2025-11-26)
**Holds it in / exit:** V1.md row 11: gravship built and exported; ShipLayoutDefV2 defs may be referenced by the gravship scenario: UNMEASURED; dependant arcjc007.gravshipcrashes -> None
**Open:** Does the shipped gravship scenario reference ShipLayoutDefV2 at load? If so removal breaks the start.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Interaction Bubbles (`jaxe.bubbles`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/Jaxe-Dev/Bubbles (github, None)
**Adds:** content: none (def_total 0) / functionality: Shows speech bubbles for social interactions (text normally only in the log); 1 Harmony DLL, settings screen / art: 5 textures, 2.1 MB est
**Why:** The Jawa comedy layer rests on it: SpeakUp (jpt.speakup, 185 defs) hard-requires it, and our mandrake.rsw.jawavoice (Jawaese lines with a parenthetical English gloss) renders through SpeakUp and Interaction Bubbles (design/validation_walks/RimStarWars/JawaVoice.md, required_mods.md 'anchor of the Jawa comedy layer'). Cosmetic, passes the 7 questions. Resonant: diegetic chatter (brief section 1 tone).
**Problems:** log_noise 0 (0 error occurrences, 0 chatter lines in the 550-mod session) · complexity 2 (one Harmony DLL) · size 1 (0.62 MB) · maintenance 1 (source verified, pushed 2025-08-25 (license not declared))
**Holds it in / exit:** dependant jpt.speakup (in list); mandrake.rsw.jawavoice validation walk assumes it -> None
**Open:** Ours do not list it in dependencies; it arrives via SpeakUp. If JawaVoice should survive a SpeakUp swap, that is a decision for the SpeakUp row.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Map Mode Framework (`nozome.mapmodeframework`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/nozomemu/MapModeFramework (github, MIT)
**Adds:** content: 9 defs (MapModeFramework.MapModeDef) / functionality: Switchable world-map view modes and C# tooling for authors; 1 Harmony DLL, 4 static ctors, source shipped (29 .cs) / art: 16 textures, 10.6 MB est
**Why:** Two real dependencies: jaeger972.factionterritories (faction territory borders, in list) requires it, and our bridge tooling `JawaBenchMapModeTools.cs` (src/RimMandrake/bridgetools/JawaBench.BridgeTools/) drives it to switch and photograph the world view while painting the planet; closed item TERRITORY_ROAD_WEIGHTED_SCALE_1 builds on it. The world map is the painting surface for the one-time paint (brief section 2). Cosmetic view overlays pass the 7 questions.
**Problems:** log_noise 0 (0 error occurrences in the 550-mod session) · complexity 2 (one Harmony DLL, 4 static ctors, settings screen) · interaction 1 (patches Core only; one third-party patch into it) · maintenance 1 (source verified MIT, pushed 2025-07-20)
**Holds it in / exit:** dependant jaeger972.factionterritories; our JawaBenchMapModeTools.cs; patched by dubwise.dubsbadhygiene.lite (1 op) -> None
**Open:** Faction Territories (another batch) decides whether the framework survives into the player build vs authoring only.
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Milky Way (`andromeda.milkyway`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Keullaeseu/Multiplayer-Milky-Way-Patch (github-search, mit)
**Adds:** content: none (def_total 0) / functionality: Described only as 'Framework'; 1 DLL with no flags, 2 static ctors, 6 asset bundles (0.37 MB) / art: 7 textures plus asset bundles; 2.1 MB est (bundles invisible)
**Why:** Required by andromeda.niceresearchtab (Nice Research Tab, a research-window layout overhaul that required_mods.md ADOPTED to fit the three-gate techprint ladder), which is in the list. UI plumbing with no content; passes the 7 questions. KEEP follows the research-tab verdict. Facts' linked repo (`Keullaeseu/Multiplayer-Milky-Way-Patch`, MIT, pushed 2026-10-09) is a name-search match for a multiplayer patch, NOT this mod's repo, so source is treated as unverified.
**Problems:** log_noise 0 (0 error occurrences, 0 chatter lines in the 550-mod session) · complexity 1 (one plain DLL) · size 1 (0.61 MB) · maintenance 2 (source unverified (search match is a different repo))
**Holds it in / exit:** dependant andromeda.niceresearchtab -> None
**Open:** Verdict follows Nice Research Tab (confirm it renders our modded research trees).
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Mines 2.0 (`cain.mineshaft`)
**Verdict:** KEEP (INFERRED) · **Fit:** dissonant · **Source:** https://github.com/ekremyk2/Mine (github, MIT)
**Adds:** content: 4 defs (ThingDef 2, ResearchProjectDef 1, WorkGiverDef 1) plus 6 patch ops / functionality: Mines 2.0: a mine building where pawns excavate ores, extensible to other mods' resources via MinesAutomatedExtension; 2 DLLs, settings screen, source shipped (51 .cs) / art: 5 textures, 4.0 MB est
**Why:** Owner override 2026-08-12 'Mines 2.0 IS LIVE' (desert_world_design.md; the objection is recorded as a watch item). It is referenced by src/RimUtinni/ResearchRetag (forceLoadAfter, 8 patch refs into it) and its compat pack leutiankane.mines2patchouterrim hard-references its C# class unguarded (sw_ownership_survey.md). Tension: an ore-producing bench is an automation ladder that rewards staying still, against the anti-exponential and movement-leash pillars (brief section 2; the 2026-08-30 prior verdict kept it). KEEP stands on the owner's override; the contradiction goes to the owner, not into this verdict.
**Problems:** log_noise 0 (0 error occurrences, 0 chatter lines in the 550-mod session) · interaction 2 (patched by our mandrake.rut.researchretag (8 refs); compat pack hard-references its class) · complexity 1 (2 plain DLLs, no Harmony) · tps 1 (tick-bearing mine building possible; no tick FLAG in facts) · maintenance 1 (source verified MIT, pushed 2025-07-31)
**Holds it in / exit:** owner override 2026-08-12; ResearchRetag forceLoadAfter and 8 patch refs (mandrake.rut.researchretag); dependant leutiankane.mines2patchouterrim (unguarded hard cross-ref) -> None
**Open:** desert_world_design.md watch items: has the mine become a substitute for travelling?; Mines 2.0 was kept by your 2026-08-12 override even though an automated ore bench rewards staying put in a campaign built to keep moving. Do you still want it, or should it go (or be limited by Cherry Picker)?
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### HugsLib (`unlimitedhugs.hugslib`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/UnlimitedHugs/RimworldHugsLibChecker (github-search, other)
**Adds:** content: 6 defs (KeyBindingDef 5, KeyBindingCategoryDef 1) / functionality: Shared library for other mods (settings, logging, update checks, key bindings, scheduling), v12.0.0; 3 DLLs, Harmony, settings screen, 6 static ctors / art: 6 textures, 1.2 MB est
**Why:** Two universe mods list it as a dependency (unlimitedhugs.allowtool, elshender.stackablechunks), and nightmare.core loads after it. Our own mods do not name it (only src/RimMandrake/Utils/selftest_retirement_order.py mentions the id). Neutral infrastructure; KEEP follows Allow Tool and Stackable Chunks (batches 2-5), which are more consequential.
**Problems:** log_noise 1 (0 error occurrences, 3 chatter lines in the 550-mod session) · complexity 2 (3 DLLs, Harmony, 6 static ctors) · maintenance 2 (facts link the HugsLibChecker repo (pushed 2022-05-29), not HugsLib itself; real source unverified) · size 1 (2.35 MB)
**Holds it in / exit:** dependants unlimitedhugs.allowtool, elshender.stackablechunks -> None
**Open:** If both dependants are cut, HugsLib can go (and PUAH/others that use it softly).
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### XML Extensions (`imranfish.xmlextensions`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/15adhami/XmlExtensions (github-search, gpl-3.0)
**Adds:** content: 1 def (MainButtonDef) / functionality: Extends patch operations and provides easy mod settings; while loaded, XML errors print a stack trace (description). 1 Harmony DLL, settings screen, 2 static ctors / art: none significant (1.3 MB est)
**Why:** It is in our own load-health sweep BASE set (src/RimMandrake/Utils/loadsweep/gen_config.py, DECISION_STRINGS.md: 'proven clean 2026-09-01'), gravenwitch.vsrexamined declares it, the KotOR cluster (guy762.mm.kotorcore) declares it as its only hard dependency (sw_ownership_survey.md), and Tribute Demand (the recommended Hutt pay-or-raid beat in required_mods.md) requires it. Its XML-error stack traces help a project whose failure mode is silent XML. The KotOR dependency is on the donor sunset track, which would not remove XML Extensions while other dependants and our tooling remain.
**Problems:** log_noise 1 (0 error occurrences, 3 chatter lines in the 550-mod session) · complexity 2 (one Harmony DLL, settings screen) · maintenance 2 (repo link is a name-search match (15adhami/XmlExtensions, gpl-3.0, pushed 2026-06-18), not a declared link)
**Holds it in / exit:** our loadsweep base list; dependants gravenwitch.vsrexamined; guy762.mm.kotorcore (per sw_ownership_survey); Tribute Demand per required_mods.md (not in facts' dependants: facts edges are a lower bound) -> None
**Open:** Confirm the source repo is the same author (name-match only).
<sub>facts: batch 01 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

