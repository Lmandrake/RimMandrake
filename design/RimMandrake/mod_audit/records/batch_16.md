# Mod audit record: batch 16 (ours_rsw_rut)

### RimStarWars: Structure Injections (`mandrake.rsw.injections`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/StructureInjectionsSW) (ours, in-repo)
**Adds:** content: 37 defs: GenStepDef 18, TileMutatorDef 15, ThingDef 3, SoundDef 1 - one finished structure promise (The Moisture Farm, roster row 1), 43 roster rows open / functionality: XML only; rides mandrake.rm.injections GenStep_RimplacePlan engine; 11 patch ops into mandrake.rm.biomes/droidworks/mlie/rut.patches / art: 7 textures, 2.06 MB on disk
**Why:** Content layer for the structure-injection program, tier-correct (Star Wars flavour over the franchise-free engine, brief §1 tiers). Hard dependency on our engine mod mandrake.rm.injections (dependencies). Nothing retires it; the description says 43 more roster rows are planned. It is not yet placed on any Ash'karr tile (description), so it costs nothing at play today.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 1 (7 textures, texture_decoded_mb_est 8.0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 2.25) · interaction 2 (patches_ours_refs 21, patched_by_ours_refs 0) · maintenance 0 (ours, in this repo (source_kind ours); no external author) · interaction 1 (4 patch refs target mlie.starwarsanimalcollection defs (patches_mods): a donor edge that must be repointed whe)
**Holds it in / exit:** depends on mandrake.rm.injections; wires TileMutators onto biomes via 15 patch refs to mandrake.rm.biomes -> None
**Open:** The 4 mlie.starwarsanimalcollection patch refs: do they name creatures already ported to RSW_ (swbestiary)? A checker should list them.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimUtinni: Structure Injections (`mandrake.rut.injections`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/StructureInjectionsRUT) (ours, in-repo)
**Adds:** content: 124 defs: GenStepDef 33, KCSG.SymbolDef 26, TileMutatorDef 18, ThingDef 10, HistoryEventDef 8, IncidentDef 8 - four campaign promises (Oasis Shrine, Rakatan Trace, Cistern, Toll Gap) / functionality: one small DLL (flags comp_tick, map_component_tick, settings_screen); KCSG symbol-based structures need Vanilla Expanded Core; 9 patch ops incl. 10 refs to Odyssey / art: 2 textures, 0.8 MB on disk
**Why:** Campaign-named structures (Oasis Shrine, Rakatan Trace) pass the RUT test (brief §1: names Ash'karr or this story). Depends on mandrake.rm.injections and on OskarPotocki.VanillaFactionsExpanded.Core, which is in FULL.LATEST and is a framework ours already lean on (brief §2 Q16 allows RM mods to require mods). No overlap with anything we own; the plan is to add more roster rows.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 1 (2 textures, texture_decoded_mb_est 0.4 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s), no Harmony flag, static_ctors 0) · tps 1 (tick flags ['comp_tick', 'map_component_tick']; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.8) · interaction 1 (patch_ops_all 9, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** depends on mandrake.rm.injections; needs VFE Core for KCSG.SymbolDef -> None
**Open:** The DLL carries tick FLAGS (comp_tick, map_component_tick) in a mod described as pure structure placement: what does it tick? Not verified.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimMandrake: Utinni — Inhabited (Ash'karr) (`mandrake.rut.inhabited`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/AshkarrInhabited) (ours, in-repo)
**Adds:** content: 8 defs: SecurityProfileDef 4, SettlementManifestDef 4 - the Junkers pilot settlement manifest (The Claim Jump, tile 16905) / functionality: data-only; the engine is mandrake.rm.inhabited (SETTLEMENT_VISIT_LOOP_1) / art: none
**Why:** Pure data (0.02 MB) for the inhabited-settlement engine, naming a real Ash'karr settlement. Keeping it costs nothing and it is the campaign half of an engine we own. Names a tile (16905, ZBiome_Badlands) and a donor biome def, which the paint pass may move; that is a content edit, not a reason to drop the mod (brief §2: paint once at the end).
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.02) · interaction 0 (patch_ops_all 0, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** depends on mandrake.rm.inhabited -> None
**Open:** Manifest names tile 16905 / ZBiome_Badlands: will the paint pass re-seat it? Not resolved here (brief §2 paint once).
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Jawa Rules (local) (`mandrake.rsw.jawarules`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/JawaRules) (ours, in-repo)
**Adds:** content: 0 defs; two code rules: Jawa may not sow (they harvest and cut but never plant), plus a second colony rule / functionality: one Harmony DLL (1 static ctor) + settings screen; 2 patch ops into armoury and starwarsraces / art: none
**Why:** Two rules a def cannot express (description), written as one small assembly so a load failure is attributable. Our own patches target it (patched_by none) and it targets only our mods (patches_mods armoury, starwarsraces). Fits the scenario directly. Retire only if the Jawa xenotype stops carrying the rules.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s) with Harmony, static_ctors 1) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.05) · interaction 2 (patches_ours_refs 4, patched_by_ours_refs 0) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** patches mandrake.rsw.armoury and mandrake.rsw.starwarsraces (4 refs) -> None
**Open:** Tier: packageId is rsw but the rule is Jawa-colony-specific ("Jawa Rules", DECIDE ruling); the brief §1 RUT test ("names this clan") would put it in RUT. Tier choice left to the owner.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Jawa Scavenger Events (`mandrake.rut.scavengerevents`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/ScavengerEvents) (ours, in-repo)
**Adds:** content: 8 defs: IncidentDef 7, ThoughtDef 1 - Migration, SurvivalPod, PodCrash, ShipBreak, Thanksgiving, Insects, Stroke / functionality: one DLL of IncidentWorkers (settings screen); ported behaviour of Mo'Events from a decompile, own defNames and letter text / art: none
**Why:** It exists to retire a donor: the description states mlie.moevents was RETIRED 2026-09-29 and removed from FULL.LATEST. Measured: mlie.moevents is not in ModsConfig.FULL.LATEST.xml. No remaining dependency on the donor, no Harmony, XML plus one DLL. MIT attribution to Mlie is recorded in the description.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s), no Harmony flag, static_ctors 0) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.04) · interaction 0 (patch_ops_all 0, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** replaces the retired donor mlie.moevents (absent from FULL.LATEST, MEASURED) -> None
**Open:** Storyteller threat odds: do 7 new baseChance incidents interact with the "no arms race, qualitative danger" pillar? Not assessed.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Empire Pursuit — Survey Shadow (`mandrake.rut.empirepursuit`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/EmpirePursuit) (ours, in-repo)
**Adds:** content: 7 defs: RUT_EmpireRungDef 6, ScenPartDef 1 - an orbital Empire pursuer scenario part (survey shadow) / functionality: one Harmony DLL (map_component_tick, 2 static ctors); fork of Ruthless Faction Pursuit (GPLv3, Matathias) with credit; only the mechanoid-pursuit half kept / art: none
**Why:** The Empire as orbital pursuer is one of the campaign's three pressures (brief §1, 01_campaign). Already forked and trimmed (Omni Pursuit dropped); the donor itself is not in FULL.LATEST (matathias.ruthlessfactionpursuit absent, MEASURED). Obligation: GPLv3 and the author asked for credit; the description carries it.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s) with Harmony, static_ctors 2) · tps 1 (tick flags ['map_component_tick']; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.13) · interaction 0 (patch_ops_all 0, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author) · maintenance 1 (GPLv3 fork: our redistribution, if ever public, must be GPL-compatible)
**Holds it in / exit:** requires Odyssey and Harmony -> None
**Open:** If the mod set is ever public: GPLv3 of this fork versus the project's own licence. Not a present problem (single-player build, brief §5.1).
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Ash'karr Landmark Art (`mandrake.rut.ashkarrlandmarkart`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/AshkarrLandmarkArt) (ours, in-repo)
**Adds:** content: 0 defs; 48 patch ops repointing LandmarkDefs (from Vanilla Landmarks Expanded, Odyssey, Alpha Biomes, mlie) to repainted icons / functionality: XML/texture only / art: 52 repainted world-map landmark icons, 1024x1024 each (measured with PIL on the source folder), 17.6 MB on disk
**Why:** It repaints icons of landmarks whose defs belong to donors (patches_mods: vanillaexpanded.vexploratione 72 refs, odyssey 100, alphabiomes 12, mlie 8). Our world will be painted once, at the end, with our own landmark defs (brief §2); the Ishko landmarks mod already shows the owned-def pattern. So the repaint rides donor defs and ends when owned landmark defs replace them. The memory proxy is the real issue: 52 icons at 1024x1024 decode to ~277 MB (INFERRED) for 128-px-class world-map sprites; downscaling is a cheap win independent of the verdict.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 3 (texture_decoded_mb_est 276.6 MB: 52 icons all 1024x1024 (measured)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 17.6) · interaction 1 (patch_ops_all 48, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** 48 LandmarkDefs of donors repointed to our art; landmarks present in the frozen world: UNMEASURED -> unfiled: ASHKARR_LANDMARKS_OWNED_DEFS
**Open:** Do world-map icons need 1024x1024? Vanilla landmark icons are far smaller; a downscale pass would cut the proxy about 16x. Not tested in game.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimUtinni: Ishko's Dark Landmarks (`mandrake.rut.ishkolandmarks`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/IshkoDarkLandmarks) (ours, in-repo)
**Adds:** content: 3 LandmarkDefs for the god Ishko: Lightless Sink, Shadowed Overhang, Cold Lava Tube / functionality: XML only; requires Odyssey / art: none
**Why:** Fills a measured gap: the sacred-sites pass found Ishko was the one of the Nine with no landmark (description). Owned defs, 0.01 MB, no donor dependency (only Odyssey, a hard prerequisite per brief §2). This is the model for replacing donor landmarks.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.01) · interaction 0 (patch_ops_all 0, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** depends on Odyssey (accepted prerequisite) -> None
**Open:** No art shipped (0 textures): the landmark icon must come from somewhere; which texture do the three defs point at? Not verified.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### JawaVoice (SpeakUp reskin) (`mandrake.rsw.jawavoice`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/JawaVoice) (ours, in-repo)
**Adds:** content: 0 defs; 203 patch ops adding Jawaese lines to SpeakUp interaction rulesStrings (370 refs into jpt.speakup) / functionality: no assembly; identity-gated so only Jawa pawns speak it / art: none
**Why:** Pure flavour with strong scenario fit (Jawaese bubbles with English gloss). Its only dependency is JPT.speakup, which is in FULL.LATEST. Zero cost beyond load-time patching. Coupling risk: 370 xpath refs into SpeakUp's defs, so a SpeakUp rename breaks it silently (a patch that matches nothing logs nothing, CLAUDE.md).
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.82) · interaction 1 (patch_ops_all 203, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author) · maintenance 1 (tied to a third-party mod (JPT.speakup) whose defs it patches 370 times)
**Holds it in / exit:** depends on JPT.speakup (third party, in FULL.LATEST) -> None
**Open:** Is SpeakUp itself wanted long term? It is a dependency of this mod; assessed in its own batch.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimStarWars: Cuisine (`mandrake.rsw.cuisine`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/Cuisine) (ours, in-repo)
**Adds:** content: 38 defs: RecipeDef 21, ThingDef 14, ThoughtDef 2, ThingCategoryDef 1 - campfire skewers (meat, veg, fungus, fruit, fish) / functionality: one DLL without Harmony flags; wave 1 of the cuisine design; patches mandrake.rm.biomes 4 refs / art: 11 textures, 3.2 MB decoded est
**Why:** Our own version of a food-on-a-stick donor; the description records the owner ruling to ingest that mod and jettison it, and no such mod is in FULL.LATEST (grep of ModsConfig.FULL.LATEST.xml for "stick": none). Neutral-to-resonant Star Wars cuisine for any SW scenario (RSW tier). Wave 1 only: more waves are designed.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 1 (11 textures, texture_decoded_mb_est 3.2 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s), no Harmony flag, static_ctors 0) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.38) · interaction 2 (patches_ours_refs 4, patched_by_ours_refs 0) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** replaces a retired food-on-a-stick donor (not in FULL.LATEST) -> None
**Open:** The DLL has no Harmony and no tick flags: what is it for (recipe discovery?). Not verified.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimStarWars: Structure Injections (`mandrake.rsw.injections`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/StructureInjectionsSW) (ours, in-repo)
**Adds:** content: 37 defs: GenStepDef 18, TileMutatorDef 15, ThingDef 3, SoundDef 1 - one finished structure promise (The Moisture Farm, roster row 1), 43 roster rows open / functionality: XML only; rides mandrake.rm.injections GenStep_RimplacePlan engine; 11 patch ops into mandrake.rm.biomes/droidworks/mlie/rut.patches / art: 7 textures, 2.06 MB on disk
**Why:** Content layer for the structure-injection program, tier-correct (Star Wars flavour over the franchise-free engine, brief §1 tiers). Hard dependency on our engine mod mandrake.rm.injections (dependencies). Nothing retires it; the description says 43 more roster rows are planned. It is not yet placed on any Ash'karr tile (description), so it costs nothing at play today.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 1 (7 textures, texture_decoded_mb_est 8.0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 2.25) · interaction 2 (patches_ours_refs 21, patched_by_ours_refs 0) · maintenance 0 (ours, in this repo (source_kind ours); no external author) · interaction 1 (4 patch refs target mlie.starwarsanimalcollection defs (patches_mods): a donor edge that must be repointed whe)
**Holds it in / exit:** depends on mandrake.rm.injections; wires TileMutators onto biomes via 15 patch refs to mandrake.rm.biomes -> None
**Open:** The 4 mlie.starwarsanimalcollection patch refs: do they name creatures already ported to RSW_ (swbestiary)? A checker should list them.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimUtinni: Structure Injections (`mandrake.rut.injections`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/StructureInjectionsRUT) (ours, in-repo)
**Adds:** content: 124 defs: GenStepDef 33, KCSG.SymbolDef 26, TileMutatorDef 18, ThingDef 10, HistoryEventDef 8, IncidentDef 8 - four campaign promises (Oasis Shrine, Rakatan Trace, Cistern, Toll Gap) / functionality: one small DLL (flags comp_tick, map_component_tick, settings_screen); KCSG symbol-based structures need Vanilla Expanded Core; 9 patch ops incl. 10 refs to Odyssey / art: 2 textures, 0.8 MB on disk
**Why:** Campaign-named structures (Oasis Shrine, Rakatan Trace) pass the RUT test (brief §1: names Ash'karr or this story). Depends on mandrake.rm.injections and on OskarPotocki.VanillaFactionsExpanded.Core, which is in FULL.LATEST and is a framework ours already lean on (brief §2 Q16 allows RM mods to require mods). No overlap with anything we own; the plan is to add more roster rows.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 1 (2 textures, texture_decoded_mb_est 0.4 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s), no Harmony flag, static_ctors 0) · tps 1 (tick flags ['comp_tick', 'map_component_tick']; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.8) · interaction 1 (patch_ops_all 9, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** depends on mandrake.rm.injections; needs VFE Core for KCSG.SymbolDef -> None
**Open:** The DLL carries tick FLAGS (comp_tick, map_component_tick) in a mod described as pure structure placement: what does it tick? Not verified.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimMandrake: Utinni — Inhabited (Ash'karr) (`mandrake.rut.inhabited`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/AshkarrInhabited) (ours, in-repo)
**Adds:** content: 8 defs: SecurityProfileDef 4, SettlementManifestDef 4 - the Junkers pilot settlement manifest (The Claim Jump, tile 16905) / functionality: data-only; the engine is mandrake.rm.inhabited (SETTLEMENT_VISIT_LOOP_1) / art: none
**Why:** Pure data (0.02 MB) for the inhabited-settlement engine, naming a real Ash'karr settlement. Keeping it costs nothing and it is the campaign half of an engine we own. Names a tile (16905, ZBiome_Badlands) and a donor biome def, which the paint pass may move; that is a content edit, not a reason to drop the mod (brief §2: paint once at the end).
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.02) · interaction 0 (patch_ops_all 0, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** depends on mandrake.rm.inhabited -> None
**Open:** Manifest names tile 16905 / ZBiome_Badlands: will the paint pass re-seat it? Not resolved here (brief §2 paint once).
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Jawa Rules (local) (`mandrake.rsw.jawarules`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/JawaRules) (ours, in-repo)
**Adds:** content: 0 defs; two code rules: Jawa may not sow (they harvest and cut but never plant), plus a second colony rule / functionality: one Harmony DLL (1 static ctor) + settings screen; 2 patch ops into armoury and starwarsraces / art: none
**Why:** Two rules a def cannot express (description), written as one small assembly so a load failure is attributable. Our own patches target it (patched_by none) and it targets only our mods (patches_mods armoury, starwarsraces). Fits the scenario directly. Retire only if the Jawa xenotype stops carrying the rules.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s) with Harmony, static_ctors 1) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.05) · interaction 2 (patches_ours_refs 4, patched_by_ours_refs 0) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** patches mandrake.rsw.armoury and mandrake.rsw.starwarsraces (4 refs) -> None
**Open:** Tier: packageId is rsw but the rule is Jawa-colony-specific ("Jawa Rules", DECIDE ruling); the brief §1 RUT test ("names this clan") would put it in RUT. Tier choice left to the owner.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Jawa Scavenger Events (`mandrake.rut.scavengerevents`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/ScavengerEvents) (ours, in-repo)
**Adds:** content: 8 defs: IncidentDef 7, ThoughtDef 1 - Migration, SurvivalPod, PodCrash, ShipBreak, Thanksgiving, Insects, Stroke / functionality: one DLL of IncidentWorkers (settings screen); ported behaviour of Mo'Events from a decompile, own defNames and letter text / art: none
**Why:** It exists to retire a donor: the description states mlie.moevents was RETIRED 2026-09-29 and removed from FULL.LATEST. Measured: mlie.moevents is not in ModsConfig.FULL.LATEST.xml. No remaining dependency on the donor, no Harmony, XML plus one DLL. MIT attribution to Mlie is recorded in the description.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s), no Harmony flag, static_ctors 0) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.04) · interaction 0 (patch_ops_all 0, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** replaces the retired donor mlie.moevents (absent from FULL.LATEST, MEASURED) -> None
**Open:** Storyteller threat odds: do 7 new baseChance incidents interact with the "no arms race, qualitative danger" pillar? Not assessed.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Empire Pursuit — Survey Shadow (`mandrake.rut.empirepursuit`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/EmpirePursuit) (ours, in-repo)
**Adds:** content: 7 defs: RUT_EmpireRungDef 6, ScenPartDef 1 - an orbital Empire pursuer scenario part (survey shadow) / functionality: one Harmony DLL (map_component_tick, 2 static ctors); fork of Ruthless Faction Pursuit (GPLv3, Matathias) with credit; only the mechanoid-pursuit half kept / art: none
**Why:** The Empire as orbital pursuer is one of the campaign's three pressures (brief §1, 01_campaign). Already forked and trimmed (Omni Pursuit dropped); the donor itself is not in FULL.LATEST (matathias.ruthlessfactionpursuit absent, MEASURED). Obligation: GPLv3 and the author asked for credit; the description carries it.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s) with Harmony, static_ctors 2) · tps 1 (tick flags ['map_component_tick']; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.13) · interaction 0 (patch_ops_all 0, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author) · maintenance 1 (GPLv3 fork: our redistribution, if ever public, must be GPL-compatible)
**Holds it in / exit:** requires Odyssey and Harmony -> None
**Open:** If the mod set is ever public: GPLv3 of this fork versus the project's own licence. Not a present problem (single-player build, brief §5.1).
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Ash'karr Landmark Art (`mandrake.rut.ashkarrlandmarkart`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/AshkarrLandmarkArt) (ours, in-repo)
**Adds:** content: 0 defs; 48 patch ops repointing LandmarkDefs (from Vanilla Landmarks Expanded, Odyssey, Alpha Biomes, mlie) to repainted icons / functionality: XML/texture only / art: 52 repainted world-map landmark icons, 1024x1024 each (measured with PIL on the source folder), 17.6 MB on disk
**Why:** It repaints icons of landmarks whose defs belong to donors (patches_mods: vanillaexpanded.vexploratione 72 refs, odyssey 100, alphabiomes 12, mlie 8). Our world will be painted once, at the end, with our own landmark defs (brief §2); the Ishko landmarks mod already shows the owned-def pattern. So the repaint rides donor defs and ends when owned landmark defs replace them. The memory proxy is the real issue: 52 icons at 1024x1024 decode to ~277 MB (INFERRED) for 128-px-class world-map sprites; downscaling is a cheap win independent of the verdict.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 3 (texture_decoded_mb_est 276.6 MB: 52 icons all 1024x1024 (measured)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 17.6) · interaction 1 (patch_ops_all 48, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** 48 LandmarkDefs of donors repointed to our art; landmarks present in the frozen world: UNMEASURED -> unfiled: ASHKARR_LANDMARKS_OWNED_DEFS
**Open:** Do world-map icons need 1024x1024? Vanilla landmark icons are far smaller; a downscale pass would cut the proxy about 16x. Not tested in game.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimUtinni: Ishko's Dark Landmarks (`mandrake.rut.ishkolandmarks`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/IshkoDarkLandmarks) (ours, in-repo)
**Adds:** content: 3 LandmarkDefs for the god Ishko: Lightless Sink, Shadowed Overhang, Cold Lava Tube / functionality: XML only; requires Odyssey / art: none
**Why:** Fills a measured gap: the sacred-sites pass found Ishko was the one of the Nine with no landmark (description). Owned defs, 0.01 MB, no donor dependency (only Odyssey, a hard prerequisite per brief §2). This is the model for replacing donor landmarks.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.01) · interaction 0 (patch_ops_all 0, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** depends on Odyssey (accepted prerequisite) -> None
**Open:** No art shipped (0 textures): the landmark icon must come from somewhere; which texture do the three defs point at? Not verified.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### JawaVoice (SpeakUp reskin) (`mandrake.rsw.jawavoice`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/JawaVoice) (ours, in-repo)
**Adds:** content: 0 defs; 203 patch ops adding Jawaese lines to SpeakUp interaction rulesStrings (370 refs into jpt.speakup) / functionality: no assembly; identity-gated so only Jawa pawns speak it / art: none
**Why:** Pure flavour with strong scenario fit (Jawaese bubbles with English gloss). Its only dependency is JPT.speakup, which is in FULL.LATEST. Zero cost beyond load-time patching. Coupling risk: 370 xpath refs into SpeakUp's defs, so a SpeakUp rename breaks it silently (a patch that matches nothing logs nothing, CLAUDE.md).
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.82) · interaction 1 (patch_ops_all 203, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author) · maintenance 1 (tied to a third-party mod (JPT.speakup) whose defs it patches 370 times)
**Holds it in / exit:** depends on JPT.speakup (third party, in FULL.LATEST) -> None
**Open:** Is SpeakUp itself wanted long term? It is a dependency of this mod; assessed in its own batch.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimStarWars: Cuisine (`mandrake.rsw.cuisine`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/Cuisine) (ours, in-repo)
**Adds:** content: 38 defs: RecipeDef 21, ThingDef 14, ThoughtDef 2, ThingCategoryDef 1 - campfire skewers (meat, veg, fungus, fruit, fish) / functionality: one DLL without Harmony flags; wave 1 of the cuisine design; patches mandrake.rm.biomes 4 refs / art: 11 textures, 3.2 MB decoded est
**Why:** Our own version of a food-on-a-stick donor; the description records the owner ruling to ingest that mod and jettison it, and no such mod is in FULL.LATEST (grep of ModsConfig.FULL.LATEST.xml for "stick": none). Neutral-to-resonant Star Wars cuisine for any SW scenario (RSW tier). Wave 1 only: more waves are designed.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 1 (11 textures, texture_decoded_mb_est 3.2 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s), no Harmony flag, static_ctors 0) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.38) · interaction 2 (patches_ours_refs 4, patched_by_ours_refs 0) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** replaces a retired food-on-a-stick donor (not in FULL.LATEST) -> None
**Open:** The DLL has no Harmony and no tick flags: what is it for (recipe discovery?). Not verified.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimUtinni: The Long Hunger (`mandrake.rut.longhunger`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/LongHunger) (ours, in-repo)
**Adds:** content: 5 defs: ThingDef 2 (RUT_LongHunger world entity, RUT_Groundcaller prop), IncidentDef 1, QuestScriptDef 1, WeatherDef 1 - a VAST dune leviathan with its own mythos, separate from the Krayt / functionality: one DLL (settings screen only); requires Anomaly / art: no textures shipped (0): the summoning prop is a v1 art placeholder per the description
**Why:** Campaign mythos content (dune leviathan, tremor damage, salvage on submerge), a qualitative threat rather than a stat-inflated one (brief §2 pillars). Small and self-contained. Art is owed: no textures in the mod, so the world entity and prop render placeholders or donor art; this is an art gap, not a verdict reason.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s), no Harmony flag, static_ctors 0) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.04) · interaction 2 (patches_ours_refs 0, patched_by_ours_refs 2) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** requires Anomaly (accepted prerequisite); patched by mandrake.rm.biomes (2 refs) -> None
**Open:** Art owed: RUT_LongHunger and RUT_Groundcaller have 0 textures in the mod; is art tracked in the art ledger?
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Desert Vehicle Reskin — Alpha Vehicles Neolithic (`mandrake.rsw.desertvehiclereskin`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/DesertVehicleReskin) (ours, in-repo)
**Adds:** content: 0 defs; 43 patch ops: 39 refs into sarg.alphavehiclesneolithic, 11 into VFE Props and Decor / functionality: one Harmony DLL (1 static ctor) + settings screen; texture overrides at the donor's own paths / art: 30 textures, 39.9 MB decoded est: redrawn draught animals so carts read as desert
**Why:** Entirely a skin on a donor (Alpha Vehicles - Neolithic, in FULL.LATEST): vehicles, stats and research stay the donor's. Brief §3 and §4 test 8: art kept only for a donor is not kept; the direction is to own the content. What holds it in is that the donor is in the list and the reskin makes it non-medieval. Exit is either to retire the vehicles donor with this mod or to build owned desert vehicles. Whether the campaign wants Neolithic carts at all is a design call, not mine.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 1 (30 textures, texture_decoded_mb_est 39.9 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s) with Harmony, static_ctors 1) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 1.1) · interaction 1 (patch_ops_all 43, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** sarg.alphavehiclesneolithic is in FULL.LATEST (hard dependency) -> unfiled: OWN_DESERT_HAULERS_OR_DROP_ALPHA_VEHICLES
**Open:** Does the campaign want Neolithic animal-drawn vehicles at all? If not, both this mod and the donor go.
**Needs owner:** Do you want animal-drawn carts (Alpha Vehicles Neolithic) in the campaign, or should vehicles be the gravship and nothing else?
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Jawa Doctrine Patches (`mandrake.rut.doctrine`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/Doctrine) (ours, in-repo)
**Adds:** content: 0 defs; 900 patch ops: mlie.starwarsanimalcollection 624, vanillaexpanded.vgeneticse 538, sarg.alphaanimals 347, vanilla 112, VFE Insectoid 2 108 (these are xpath refs, they overlap); MegafaunaYield meat-yield patches; Droid Factory removal / functionality: one Harmony postfix DLL (DROIDWORKS_ISFLESH_RELATIONS_CRASH_1 fix, 1 static ctor) / art: none
**Why:** The bulk of its 900 ops patch donors that are on the sunset track (mlie, Alpha Animals, VGE, Insectoid 2): when they go, those patches go inert (a patch that matches nothing logs nothing). The Droid Factory patch targets OuterRim_DroidFactory from Droid Depot, which is not in FULL.LATEST, so it is already inert (INFERRED: patch target mod absent). The Harmony ISFLESH crash fix belongs next to Droidworks. Exit: donor ports (DONOR_DEFS_PORT_TO_OURS_1), then fold survivors into rut.patches or droidworks.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s) with Harmony, static_ctors 1) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.55) · interaction 2 (patches_ours_refs 156, patched_by_ours_refs 0) · maintenance 0 (ours, in this repo (source_kind ours); no external author) · interaction 2 (pure patch layer over donors being retired; 900 ops of which most will go dead silently)
**Holds it in / exit:** patches 156 of our defNames (patches_ours_refs); donors still active: mlie, alphaanimals, vgeneticse, insectoid2 -> DONOR_DEFS_PORT_TO_OURS_1
**Open:** Is the Harmony ISFLESH fix still needed now that Droidworks owns the droid platform? A checker should read the postfix target.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimMandrake - Star Wars Races (`mandrake.rsw.starwarsraces`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/StarWarsRaces) (ours, in-repo)
**Adds:** content: 527 defs: GeneDef 164, HeadTypeDef 124, PawnKindDef 85, XenotypeDef 70, RulePackDef 48, HediffDef 6 - 69 Star Wars species owned outright / functionality: XML only (dll_count 0); depends on Biotech, VFE Core, HAR-family genes mods (Neronix17.Outland.Genetics, Turnovus, RedMattis BigSmall/BetterPrerequisites, LazyFriday eyes), all in FULL.LATEST / art: 891 textures, 11.3 MB on disk, 999 MB decoded est
**Why:** Its purpose is to own the species so the three colliding xenotype mods can be switched off, and measured: none of Star Wars Xenotypes, Outer Rim Galactic Diversity nor BTD Xenotype Remix is in FULL.LATEST. Most-patched mod of ours (patched_by_ours_refs 560: pawnflavor 424, rsw.patches 74, rut.patches 60). The founders and factions are species from here. Real cost: the memory proxy (999 MB) is the largest of any single mod in the batch.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 3 (891 textures, texture_decoded_mb_est 999.0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 12.09) · interaction 2 (patches_ours_refs 0, patched_by_ours_refs 560) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** patched by pawnflavor (424), rsw.patches (74), rut.patches (60), jawarules (2); supplies the xenotypes the Jawa founders use -> None
**Open:** Is the 999 MB texture proxy real? 891 textures at ~1.1 MB decoded each; head and body atlases might be oversized. Needs a measurement, not a guess.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Jawa Armoury Rebalance (`mandrake.rsw.armoury`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/Armoury) (ours, in-repo)
**Adds:** content: 1566 defs: ThingDef 761, SoundDef 304, HediffDef 125, ResearchProjectDef 74, RecipeDef 53, Lightsaber.HiltPartDef 43 - weapon ladder restretched, absorbed KotOR/other weapon mods / functionality: one Harmony DLL (comp_tick, 13 static ctors); depends on VFE Core, adaptive storage, EBSG framework, OuterRim Core / art: 2682 textures, 84.6 MB on disk, 3129 MB decoded est; 407 sounds, 51.5 MB
**Why:** Core of the "weapons match the setting's physics" design and the destination of the Star Wars weapon donor sunset (guy762 KotOR weapons defs are declared here, MEASURED by grep). Most-patched weapon surface: patched_by_ours_refs 842 (researchretag 444, rsw.patches 208, pawnflavor 170). Problems are cost, not fit: largest memory proxy in the batch and 3 distinct log config errors on its own absorbed guy762 weapons.
**Problems:** log_noise 2 (6 occurrences, 3 distinct: "Config error in guy762_bowcaster_ceremonial / hvyrepeater_massdriver / lgtrepeater) · memory 3 (2682 textures, texture_decoded_mb_est 3128.9 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s) with Harmony, static_ctors 13) · tps 1 (tick flags ['comp_tick']; per-mod TPS UNMEASURED) · size 2 (disk_mb 139.18) · interaction 2 (patches_ours_refs 65, patched_by_ours_refs 842) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** patched by researchretag (444), rsw.patches (208), pawnflavor (170), rut.patches (18); still depends on neronix17.outerrim.core -> None
**Open:** Fix the forcedMiss config on absorbed guy762 weapons (explosive projectiles only should force a miss).; 3.1 GB decoded proxy for 2682 textures: measure real memory before acting.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimMandrake: SW — Gizka Stowaway (`mandrake.rsw.gizkastowaway`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/GizkaStowaway) (ours, in-repo)
**Adds:** content: 5 defs: HediffDef 2, RecipeDef 1, ThingDef 1, ThoughtDef 1 - the Gizka ship-pest as a found-aboard event with escalation and exits / functionality: one Harmony DLL (map_component_tick, 2 static ctors); patches swbestiary (9 refs) and mlie.starwarsanimalcollection (8 refs) / art: none
**Why:** The creature is not ours here: the description says Gizka lives in mlie.starwarsanimalcollection, yet RSW_Gizka is now declared in SWBestiary (MEASURED grep) and the mod declares no dependency on either (dependencies: Ludeon.RimWorld, Harmony). It silently depends on a donor. Keep the event; exit is repointing its 8 mlie refs to the RSW_Gizka def and declaring swbestiary.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s) with Harmony, static_ctors 2) · tps 1 (tick flags ['map_component_tick']; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.06) · interaction 2 (patches_ours_refs 9, patched_by_ours_refs 0) · maintenance 0 (ours, in this repo (source_kind ours); no external author) · interaction 2 (9 refs to swbestiary and 8 to mlie; undeclared dependency means load order, not dependencies, decides success)
**Holds it in / exit:** 8 patch refs to mlie.starwarsanimalcollection; no declared dependency on its creature source -> unfiled: GIZKA_STOWAWAY_REPOINT_TO_RSW
**Open:** Does the event spawn the mlie Gizka or RSW_Gizka today? Only a live check tells; not run.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimMandrake: SW — Shokk (`mandrake.rsw.shokk`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/Shokk) (ours, in-repo)
**Adds:** content: 1 FactionDef; the mod was shrunk (SHOKK_SKIN_SHRINK_1) to a single skin patch after the Wyyyschokk mechanisms moved to rm.biomes / functionality: XML only, 14 patch refs into mandrake.rm.biomes; hard dependency on mlie.starwarsanimalcollection / art: 3 textures, 4.0 MB decoded est
**Why:** What holds it in: a hard dependency (dependencies) on the mlie donor for the Wyyyschokk creature; no RSW_ Wyyyschokk exists in SWBestiary (grep found only RSW_Shokk_FeraliskBrood and RSW_WyyyschokkFang). The exit is the port of the creature (MLIE_FAUNA_ABSORPTION_1 is closed without it). Tiny cost; the only reason it matters is that it keeps the donor hard-required.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 1 (3 textures, texture_decoded_mb_est 4.0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.84) · interaction 2 (patches_ours_refs 14, patched_by_ours_refs 0) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** hard dependency on mlie.starwarsanimalcollection; shokk mechanisms lived in rm.biomes after the shrink -> unfiled: WYYYSCHOKK_PORT_TO_RSW
**Open:** Is a Wyyyschokk creature port planned? SWBestiary has no RSW_Wyyyschokk def.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Jawa Ion Weapons (local) (`mandrake.rsw.ionweapons`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimStarWars/JawaIonWeapons) (ours, in-repo)
**Adds:** content: 6 defs: ThingDef 2, DamageDef 1, HediffDef 1, ResearchProjectDef 1, StatDef 1 - the Jawa Ion Blaster plus ion damage and ion-buildup stun hediff / functionality: two DLLs with Harmony (1 static ctor) + settings screen; depends on Neronix17.OuterRim.Core / art: 2 textures, 0.7 MB decoded est
**Why:** A capture-not-kill signature weapon that fits Jawa droid-capture (brief §1). Small and self-contained. Overlap check owed: Armoury also owns a large weapon set and ion/stun weapons are common; I did not compare. Depends on the OuterRim Core donor (in FULL.LATEST).
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 1 (2 textures, texture_decoded_mb_est 0.7 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (2 DLL(s) with Harmony, static_ctors 1) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.1) · interaction 2 (patches_ours_refs 0, patched_by_ours_refs 11) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** depends on Neronix17.OuterRim.Core; patched by researchretag 7, rsw.patches 3, droidworks 1 -> None
**Open:** Does mandrake.rsw.armoury already carry an ion weapon? Not compared.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### RimUtinni: Ship Memory — the Chains Below (`mandrake.rut.shipmemory`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/ShipMemory) (ours, in-repo)
**Adds:** content: 1 ThingDef; 15 patch ops into Anomaly (HoldingPlatform and others) adding a discovery-prerequisite reveal gate / functionality: one DLL (game_component_tick, settings screen); requires Anomaly / art: none
**Why:** Implements the owner's ruling that the Anomaly content is not cut, only the player's research route (quoted in description). Contained: 1 def and a reveal gate. The brief §5.7 contradiction (Anomaly "reskin library" versus "kept content is the Assailant war") is not resolved here; this mod sits on the second reading.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s), no Harmony flag, static_ctors 0) · tps 1 (tick flags ['game_component_tick']; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.03) · interaction 1 (patch_ops_all 15, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** patches 14 Anomaly defs -> None
**Open:** Brief §5.7: Anomaly storyline at zero versus Anomaly content as permanent canon. This mod assumes the latter; decide before extending.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Antiquities (`mandrake.rut.antiquities`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/Antiquities) (ours, in-repo)
**Adds:** content: 14 defs: ResearchProjectDef 5, ThingDef 5, JobDef 1, ResearchTabDef 1, WorkGiverDef 1, WorkTypeDef 1 - the 17th research tree (Language, Religion, Culture, Cartography, Voice) read out of urns / functionality: one DLL (settings screen); two of our mods depend on it (rites, scarlandsladder) / art: none
**Why:** Ruled design (antiquities_design.md RULED 2026-09-04) and a dependency of two of ours (dependants_ours). The tree is a discovery system, not a parallel ladder: stages are read from the world. Patched by researchretag (12 refs).
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 2 (1 DLL(s), no Harmony flag, static_ctors 0) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.05) · interaction 2 (patches_ours_refs 0, patched_by_ours_refs 12) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** dependants_ours: mandrake.rut.rites, mandrake.rut.scarlandsladder; 12 refs from researchretag -> None
**Open:** Tree rebrand names and merges remain open per its description; labels cheap, defNames never rename.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

### Salvation Rites (`mandrake.rut.rites`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** git@github.com:Lmandrake/RimMandrake.git (src/RimUtinni/Rites) (ours, in-repo)
**Adds:** content: 25 defs: ResearchProjectDef 5, PreceptDef 3, RitualBehaviorDef 3, RitualObligationTargetFilterDef 3, RitualOutcomeEffectDef 3, RitualPatternDef 3 - five liturgy rites revealed not bought / functionality: XML only; hard dependency on mandrake.rut.antiquities / art: none
**Why:** Authored on the owner's research-tree ruling; the reveal gate is live (RITES_REVEAL_MECHANISM_1). XML only, 0.04 MB, depends only on Antiquities. It is campaign liturgy (Scrap Shrine, Conduit Choir), not a player power ladder.
**Problems:** log_noise 0 (0 occurrences, 0 distinct errors, 0 chatter lines in the 550-mod session) · memory 0 (0 textures, texture_decoded_mb_est 0 MB (w*h*4*1.33 header proxy, not measured per mod)) · complexity 1 (XML-only (dll_count 0)) · tps 0 (no tick flag in assemblies; per-mod TPS UNMEASURED) · size 1 (disk_mb 0.04) · interaction 0 (patch_ops_all 0, none touch ours) · maintenance 0 (ours, in this repo (source_kind ours); no external author)
**Holds it in / exit:** depends on mandrake.rut.antiquities; Ideology precept defs -> None
**Open:** Rituals need Ideology (a hard prerequisite, brief §2); nothing else.
<sub>facts: batch 16 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by sonnet-5.5 (batch 16 assessor) 2026-10-10</sub>

