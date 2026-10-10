# Mod audit batch 06 (star_wars_donors)

10 mods, assessor sonnet-5.5-batch06, 2026-10-10. Facts: mod_facts.jsonl 2026-10-10.

### JecsTools Unofficial 1.6 BETA (`jecrell.jecstools`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (ships Source/ in the mod folder (549 .cs, 18 csproj); the facts source_url (roxxploxx/RimWorldModGuide) is a modding wiki, not this code, Apache-2.0 (of the wiki repo only))
**Adds:** content: 25 declared defs only (JobDef 6, StatDef 6, RulePackDef 5, StatCategoryDef 2, ThingDef 2, ...); functionality: modder component library: ability casting, activatable effects, deflector, oversized weapons, vehicles, float-menu registry. 18 DLLs, Harmony, comp_tick and world_component_tick flags. Port is labelled 'Not yet tested or proven to be fully functional'; art: 3 textures, 0.8 MB est
**Why:** Nothing in the universe lists it as a hard dependency (dependants [] and dependants_ours []), but lee.theforce.lightsaber and jecrell.StarWarsTheForce name it in loadAfter and the 2026-08-30 survey recorded runtime use by lightsaber/oversized-weapon graphics as UNCERTAIN without a live test. Our Armoury has already re-implemented one JecsTools mechanism itself (Source/CompExtraSounds/HarmonyCompExtraSounds.cs, Harmony id jecstools.jecrell.comps.sounds), so the direction is to own what we use. Removal is blocked by not knowing what the closed-source lightsaber DLL calls, not by a known dependency. Brief s4 tests 1-2 (nothing of ours declares it) and s3 (retire what we port). It is a BETA port (supports 1.6 per About), which adds a maintenance risk.
**Fit:** Pure library with no theme; brief s4 test 1 and s2 (nothing in the ban list, no ladder). Not an A-list lightsaber dependency we can prove.
**Problems:** complexity 3 18 DLLs, Harmony, 17 static ctors (>20 not reached, but 18 DLLs is 'many DLLs') · tps U flags comp_tick and world_component_tick present across AbilityUser/CompDeflector etc.; cost unmeasured, content that spawns tickers is small (25 defs) · maintenance 2 unofficial BETA port by a third party, 'not yet tested'; repo URL in facts is a wiki guide not the code (last push 2017) · size 2 29.7 MB disk, of which 22.9 MB 'other' and 605 shipped .cs files · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** soft loadAfter from lee.theforce.lightsaber (no source; runtime need UNMEASURED); oversized-weapon/slot comps possibly used by lightsaber donors: UNMEASURED; placed Things: 2 ThingDefs only, save placement UNMEASURED -> unfiled: JECSTOOLS_RUNTIME_USE_PROBE_THEN_DROP
**Open:** Does Lightsaber.dll or the KotOR comps call into JecsTools at runtime? Needs a live load without it on the minimal list (not done offline).
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>

### Star Wars Animal Collection (Continued) (`mlie.starwarsanimalcollection`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** resonant · **Source:** https://github.com/emipa606/StarWarsAnimalCollection (github, MIT)
**Adds:** content: 1,578 declared defs: SoundDef 589, ThingDef 454, PawnKindDef 160, BodyDef 102, IdeoIconDef 90, ThoughtDef 33 ... a Star Wars creature roster; functionality: XML only (dll_count 0); 54 patch ops, 41 on BiomeDef, into Core/Odyssey/More Vanilla Biomes; art: in AssetBundles (37.7 MB disk); the 5.0 MB texture proxy cannot see inside bundles
**Why:** Genuine Star Wars IP, so its future is RSW_ ports routed through Utinni patches (brief s2, s3; test 7). Held in by 3,439 xpath references from our mods (rut.patches 1,838, rut.doctrine 624, rsw.swbestiary 498, rut.pawnflavor 350, rsw.armoury 87 ...) and by two hard dependants (mandrake.rsw.shokk, mandrake.rsw.swbestiary). MLIE_FAUNA_ABSORPTION_1 is closed yet the edges persist, so the exit is unfinished. Zero log errors in the 550-mod session.
**Fit:** Star Wars creatures fit the setting (brief s1, s4 test 3) but as IP belong in the RSW_ tier via ports (s2); donor art is not kept (s4 test 8); brief s5.3 (big-creature mods welcome vs retired) applies to its content.
**Problems:** interaction 2 patched_by_ours_refs 3,439 · memory U art is in AssetBundles; decoded size not measurable from headers · complexity 1 XML only, 0 static ctors · tps U 454 ThingDefs/160 PawnKindDefs worth of creatures could spawn in number; cost unmeasured · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** dependants_ours: mandrake.rsw.shokk, mandrake.rsw.swbestiary; patched_by_ours_refs 3,439; placed creatures in the save: UNMEASURED -> MLIE_FAUNA_ABSORPTION_1 (closed); remaining edges: unfiled: MLIE_DONOR_EDGES_STILL_BITE
**Open:** Split the 3,439 references into ported-twin wiring vs live dependence.
**Needs owner:** Which of the donor's creatures must still come from this mod once every one has an RSW_ twin: is it acceptable to cut the mod at the next world repaint even if some placed animals vanish from the old save?
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>

### Outer Rim - Core (`neronix17.outerrim.core`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** resonant · **Source:** none (ships Source/ in mod folder; facts source_url (pardeike/Harmony) is WRONG for this mod, unknown (author Patreon page only))
**Adds:** content: 404 declared defs: ThingDef 179, SoundDef 58, TerrainDef 42, PawnKindDef 17, ResearchProjectDef 16, DamageDef 8 (incl. OuterRim_Blaster), TraderKindDef 6, PipeNetDef 1, plus VEF ability/projectile defs; functionality: Star Wars material/weapon/tech base (durasteel, vibro weapons, blasters, battle droid kinds); one DLL with Harmony and a settings screen; 2 static ctors; art: 1,108 textures counted, 708.7 MB decoded proxy (INFERRED, may include non-loaded version folders; the 2026-08-30 survey found 73 loose files plus a 36.5 MB bundle)
**Why:** Hard framework dependency of five other mods in the universe (dependants: mineablesor, mines2patchouterrim, galacticempire, rebelalliance, plus ours: mandrake.rsw.armoury and mandrake.rsw.ionweapons) and 256 of our xpath references (rut.researchretag 139, rsw.armoury 94). Our Armoury also calls OuterRim_Blaster as a damageDef it does not ship (Armoury About.xml line ~85) and Droidworks references OuterRim_Durasteel/BattleDroid. It is Star Wars IP so the exit is RSW_ ports, which the closed STARWARS_DONOR_SUNSET_1 puts in Wave 3 entangled with DROID_SYSTEM_BUILD_1. Brief s3: retirement needs dependant, save and ParentName checks and none are done.
**Fit:** Star Wars material and weapon base fits Utinni's setting (brief s1) but is IP and so belongs behind RSW_ (s2, s3 test 7).
**Problems:** memory 3 texture_decoded_mb_est 708.7 (>250); proxy may over-count unloaded folders · interaction 2 patched_by_ours_refs 256; our Armoury depends on its DamageDef · complexity 2 one Harmony DLL, 2 static ctors; also needs VEF, PipeSystem, TabulaRasa defs · size 2 117.4 MB disk · maintenance 2 no source link verified (facts url points at pardeike/Harmony, a false match); Source/ ships inside the mod (28 .cs) · tps U comp_tick flag; cost unmeasured · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** hard dependants incl. ours: mandrake.rsw.armoury, mandrake.rsw.ionweapons; 2 unguarded cross-refs from the LK mine patches; world-save OuterRim_ prefix count 3,156 in the 2026-08-30 survey (scan-grade, shared across 5 submods; UNMEASURED now) -> STARWARS_DONOR_SUNSET_1 (closed, Wave 3) + DROID_SYSTEM_BUILD_1; unfiled: OUTERRIM_CORE_DAMAGEDEF_AND_MATERIALS_PORT_1
**Open:** Facts source_url is a false match; find the real repo or confirm none.
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>

### LK Mineable Resources Outer Rim (`leutiankane.mineablesor`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 4 ThingDefs (Outer Rim metals as mineable ore); functionality: 13 patch ops: 6 GenStepDef, 4 SitePartDef, 3 ThingDef, so Outer Rim metals appear in mountain generation and deep drilling; Ideology/Odyssey FindMod gates; art: 2 textures, 2.0 MB est
**Why:** Owner ruling 2026-08-12 kept it ('something on the map to find and leave behind', per sw_ownership_survey). It hard-depends on neronix17.outerrim.core and per the survey has unguarded cross-refs to OuterRim_ ThingDefs, so it falls when Core does; STARWARS_DONOR_SUNSET_1 tracks it alongside Core's Wave 3. Nothing of ours depends on it (dependants_ours []). Tiny (0.42 MB). Its resource-spawning patches on GenStepDefs touch map generation, so scarcity tuning (brief s1, loop) could be affected, which is why we only keep it temporarily.
**Fit:** Mineable materials are scarcity-neutral dressing; brief s4 test 4 (no ladder by itself) but rewards extraction, offset by 'decide what to leave behind' (s1).
**Problems:** interaction 2 patches GenStepDef (6) and SitePartDef (4) that shape map resources; patches_mods lists neronix17.outerrim.core 3 · maintenance 2 no source link, steam-only, tiny community patch · size 1 0.42 MB · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** owner ruling 2026-08-12 (survey); must be retired with Core: it hard-references OuterRim_ defs; mined ore Things in the save: UNMEASURED -> STARWARS_DONOR_SUNSET_1 (closed, Wave 3); unfiled: ASHKARR_ORE_SET_OWN_DEFS_1
**Open:** Do its GenStep patches change ore frequency on the Ashkarr tiles? Not measured.
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>

### LK Mines 2.0 Compatability[Outer Rim Core] (`leutiankane.mines2patchouterrim`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: none (def_total 0); functionality: 9 patch ops on Outer Rim Core ThingDefs so Outer Rim resources work with Mines 2.0 (Cain.Mineshaft) bills; art: 3 textures, 3.8 MB est
**Why:** A glue patch between Outer Rim Core and Mines 2.0. Survey records an owner override 'Mines 2.0 IS LIVE' (2026-08-12); it hard-depends on Core and on Mines 2.0's C# class, so it must leave with whichever of those goes first. Nothing of ours uses it (dependants_ours []). It adds no content of its own, so once Core is ported or Mines 2.0 is dropped there is nothing to preserve.
**Fit:** Compatibility glue; fit is whatever Mines 2.0 and Core's fit is (brief s4 test 2).
**Problems:** interaction 2 9 patch ops on Core ThingDefs; breaks if Core or Cain.Mineshaft removed · maintenance 2 steam-only, no source · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** Mines 2.0 is live (owner override 2026-08-12, survey); Core hard-ref; unguarded cross-refs per survey -> STARWARS_DONOR_SUNSET_1 (closed, Wave 3, with Core); drop when Mines 2.0 is judged in its own batch
**Open:** Is Cain.Mineshaft (Mines 2.0) staying? Its batch decides this mod.
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>

### Outer Rim - Furniture & Decor (`neronix17.outerrim.furnitureanddecor`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 276 defs: ThingDef 258, TabulaRasa.HologramDef 10, JobDef 2, JoyGiverDef 2, JoyKindDef 1 - furniture, decals, joy buildings, statues; functionality: XML only, no patches; without Core it falls back to vanilla materials; no DLL; art: 507 textures counted, 643.8 MB decoded proxy (INFERRED; 2026-08-30 survey saw 3 loose files plus a 19.4 MB bundle, so the proxy may count unloaded folders)
**Why:** Cosmetic furniture, nothing of ours depends on it (dependants_ours [], patched_by {}), and by brief s2/s4 test 8 donor art is not kept, so the long-term answer is our own decor. It is not REPLACE-NOW because I found no scoped replacement (a src/ search found no own-furniture mod; the search was by packageId/defName only, so UNVERIFIED) and no measured problem forcing a deadline: 0 log errors. Its Star Wars look does support the ship's interior feel (brief s1). Memory proxy is the largest of the batch's decor but is unverified.
**Fit:** Cosmetic and pillar-neutral (brief s4 test 4), but donor art (s4 test 8) and SW IP (s2).
**Problems:** memory 3 texture_decoded_mb_est 643.8 (>250); possible over-count · size 2 50.2 MB disk · tps 1 258 ThingDefs but no tick flags (XML only); hologram defs may tick · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** placed furniture in the colony and ship save: UNMEASURED; no replacement set scoped -> unfiled: SHIP_INTERIOR_DECOR_OWN_SET_1
**Open:** Run the texture count against LoadFolders: 507 textures vs 3 loose files in the older survey.
**Needs owner:** Do you want our own ship-interior furniture, or are you content to keep Outer Rim furniture until the paint-once pass?
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>

### Outer Rim - Galactic Empire (`neronix17.outerrim.galacticempire`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** none (ships Source/ in mod folder; facts url wrong, unknown)
**Adds:** content: 104 defs: ThingDef 61 (stormtrooper wardrobe, Imperial weapons), PawnKindDef 23, FactionDef 2, RulePackDef 5, TraderKindDef 3, ScenarioDef 1, CultureDef 1; functionality: Imperial faction module; one small Harmony DLL (10.5 KB) patching Outer Rim Core's settings class; 2 patch ops; art: 700 textures, 364.3 MB proxy (INFERRED); survey saw 3.5 MB in a bundle
**Why:** The campaign's Empire is vanilla Royalty Empire, reskinned; the mod's own FactionDef is struck from the records (UtinniPatches and Jawa_Patches GalacticEmpire.xml). The content still used is the OuterRim_Imp pawnkinds, uniforms and armour: our patches reference it 14 times (rsw.patches 9, rut.patches 5) and Droidworks has 9 files naming OuterRim_Imp. It rides Core. Exit is the Wave 3 port plan under STARWARS_DONOR_SUNSET_1 / DROID_SYSTEM_BUILD_1.
**Fit:** Imperial pursuit and armour fit the Empire pressure (brief s1), but the faction itself was excluded in favour of vanilla Empire (s2, s5.2).
**Problems:** memory 3 364.3 MB proxy (>250) · interaction 2 patched_by_ours_refs 14; patched by regrowth.botr.core too · complexity 2 one Harmony DLL coupled to Core internals · maintenance 2 facts source_url (pardeike/Harmony) is a false match; Source ships in mod (7 .cs) · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** OuterRim_Imp* pawnkinds under MayRequire in our patches (survey, 129 scan-grade save hits); depends on Core, with a Harmony patch into Core's settings -> STARWARS_DONOR_SUNSET_1 (closed, Wave 3); unfiled: IMPERIAL_RAID_KIT_RSW_PORT_1
**Open:** Brief s5.2: is the OuterRim faction cut or kept for the raid armour? Kept for armour per memory, not in older mod docs.
**Needs owner:** Is it right that the Empire's soldiers keep wearing Outer Rim's stormtrooper gear until we make our own, or should the Empire raid kit be rebuilt on vanilla now?
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>

### Outer Rim - Rebel Alliance (`neronix17.outerrim.rebelalliance`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 46 defs: ThingDef 20, PawnKindDef 11, FactionDef 2, RulePackDef 5, TraderKindDef 3, ScenarioDef 1, CultureDef 1; functionality: Rebel faction module, XML only; its FactionDef is suppressed by our RebelAlliance_Suppress.xml (weights zeroed); art: 216 textures, 165.3 MB proxy (INFERRED); survey saw a 1.4 MB bundle
**Why:** The faction is suppressed on purpose but weapons stay in use: OuterRim_A280Blaster appears in src/RimMandrake/Inhabited/Defs/CastRosters/CastRoster_WILDSTEAM.xml, and our patches reference the mod 16 times (rut.patches 12, rsw.patches 3, rsw.armoury 1). The mod's own Scenario_Rebel.xml names the FactionDef, so it cannot be deleted without losing that scenario. Exit: port the A280 and used kit to RSW_ and drop it with the Core wave.
**Fit:** Rebel faction not in the Utinni cast (brief s2: Empire only, OuterRim faction cut); its weapons fit the style.
**Problems:** memory 2 165.3 MB proxy (50-250) · interaction 2 patched_by_ours_refs 16 incl. a suppression patch · maintenance 2 no source, steam-only · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** A280 blaster used by the WILDSTEAM cast roster; 16 patch references of ours; depends on Core -> STARWARS_DONOR_SUNSET_1 (closed, Wave 3); unfiled: REBEL_GEAR_RSW_PORT_1
**Open:** Is anything beyond A280 used? The WILDSTEAM roster lists one item; a defName census of our rosters would settle it.
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>

### Star Wars : The Force - Lightsaber (`lee.theforce.lightsaber`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: 328 defs: Lightsaber.HiltDef 112, HiltPartDef 60, ThingDef 33, SoundDef 30, TraitDef 7, HediffDef 7, DamageDef 7, ManeuverDef 4, plus kyber crystals and upgrades; functionality: lightsaber builder with a melee parry system; one Harmony DLL; patches 43 TraitDefs and 13 StatDefs (and Royalty/Meaningful Parties/Stronger Scaling); art: 444 textures, 260.3 MB proxy (INFERRED); survey saw 3 MB loose + 0.4 MB bundle
**Why:** Lightsaber weapons stay in v1 (required_mods banner: weapons not Force powers; Force is v2) and our Armoury patches this mod in 29 files (patched_by_ours_refs 32). The KotOR hilt parts that targeted it are absorbed, but the DLL (273 KB, no source) and 112 hilt defs are not, and we cannot port a closed DLL offline. STARWARS_DONOR_SUNSET_1 recorded that it conflicts with the 2026-08-30 owner ruling 'stays upstream' and left it to an explicit owner call. The 43 TraitDef patches need a read to confirm they do not reshape Force-user traits the lore defers.
**Fit:** Lightsaber weapons stay (brief s2 names 'lightsaber weapons stay'); Force powers are v2.
**Problems:** memory 3 260.3 MB proxy (>250) · interaction 2 patches 43 TraitDefs and 13 StatDefs; our Armoury patches it in 29 files · complexity 2 Harmony DLL with no source, 9 static ctors · maintenance 3 no source anywhere (steam-only) · tps U comp_tick flag; parry system ticks during melee only · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** 29 Armoury patch files + 3 rut.patches; LIGHTSABER_RECIPE_GATE_1 and LIGHTSABER_MELEE_PATCH_FAIL_1 behaviour tied to it; 68 <def> occurrences in the save (2026-08-30 survey, scan-grade) -> None
**Open:** Wave 4 of STARWARS_DONOR_SUNSET_1: does 'get rid of them all' override 'stays upstream'?
**Needs owner:** You ruled on 2026-08-30 that the lightsaber mod stays and on 2026-09-02 that we retire the Star Wars donors. Does the lightsaber mod stay as a permanent dependency, or do we eventually build our own sabers?
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>

### [BTD] Ship Pack: KotOR Ships VGE (`btd.gbp.shippack.kotor.vge`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: none by defs (def_total 0); two gravship blueprint files (Dynamic Class Freighter, KT-400 Freighter) with preview PNGs, plus a gated KotOR Droids distress-call incident/quest/site subfolder; functionality: Odyssey gravship layouts loadable through btd.remix.gravshipblueprints; art: 4 textures, 34 MB est
**Why:** Fit is dissonant: the campaign is one fixed ship, the Utinni, 'getting it off the ground is the campaign'; ready-made freighters of another franchise undercut that (brief s1, s2 'Mini Gravships' excluded). Nothing depends on it (dependants []), it has zero defs (no ParentName risk), and the one real asset, its _BTDKotORGravships gated folder, is already absorbed per WEAPONS_DONOR_RETIREMENT_1. Missing: save placement (the 2026-08-30 survey found its packageId string once in the world save, uncertain). Its base btd.remix.gravshipblueprints is the only other mod involved and belongs to another batch.
**Fit:** Brief s1 (the Utinni is the one ship), s2 (Mini Gravships, GravTech excluded); also donor-art law (s4 test 8).
**Problems:** size 1 5.6 MB disk · interaction 1 incompatible_with btd.gbp.shippack.kotor, the non-VGE edition; patches nothing · log_noise 0 0 error occurrences, 0 chatter lines in the 550-mod session
**Holds it in / exit:** no dependants; a possible packageId string in the save (UNMEASURED); bases on btd.remix.gravshipblueprints and optionally guy762.KotORDroids (not hard) -> None
**Open:** Does the world save carry a ship from this pack? Check with the savegame skill before unticking.
**Needs owner:** Should players ever be able to build other ships from blueprints (for example a Kotor freighter), or is the Utinni the only ship, ever?
<sub>facts: batch 06 · mod_facts.jsonl 2026-10-10 · assessed by sonnet-5.5-batch06 2026-10-10</sub>
