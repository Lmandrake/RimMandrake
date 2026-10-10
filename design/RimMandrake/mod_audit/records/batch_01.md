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

