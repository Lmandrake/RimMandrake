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

