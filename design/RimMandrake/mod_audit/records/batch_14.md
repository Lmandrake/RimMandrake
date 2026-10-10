# Mod audit record: batch 14 (misc_content_2)

48 mods. Assessor: Sonnet 5.5, stage 1. Facts generated 2026-10-10T14:47:38-0700.

### RimTraits - General Traits (`sierra.rt.generaltraits`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Sierra0001/RimTraits---General-Traits (github, NOASSERTION)
**Adds:** content: 46 TraitDefs plus 4 ThoughtDefs (defs_by_type) / functionality: XML only; mutually exclusive tiers with rising rarity (About description) / art: 5 images, 22.2 MB est (INFERRED)
**Why:** Supplies a layer of minor personality traits that we have no plan to build (46 TraitDefs). Cosmetic/uniqueness systems pass the 7-question test trivially (brief section 4 test 4); no parallel ladder, no scaling. Nothing of ours depends on it (dependants_ours empty) and it patches nothing (patch_ops_all 0), so it carries no interaction risk. 0 log errors in the 550-mod session.
**Problems:** memory 1 (texture_decoded_mb_est 22.2 MB (INFERRED header proxy, 5 textures)) · size 1 (disk_mb 1.09) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) (U = unmeasured)
**Holds it in / exit:** no dependants; placed traits on the six fixed founders and saved pawns: UNMEASURED -> None
**Open:** Do any of the 46 traits imply medieval/off-genre flavour? Not read trait by trait.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Roofed Scanning 1.6 (`kupie.isjustdoingitlive.plzdonthateme.roofedscanning`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (ships-source, None)
**Adds:** content: none (def_total 0) / functionality: Harmony patch of the vanilla roof check so Odyssey scanners work under a roof (7 patch ops into Core/Odyssey) / art: 1 image
**Why:** Life on the ship is indoors under roof, so scanners that refuse a roof would be unusable aboard; the mod supplies the one-line roof-check relaxation that we do not plan to build. Ships its own C# source (2 .cs, 1 csproj in the folder) so it can be maintained by us if the author goes. Nothing of ours depends on it and 0 log errors were measured.
**Problems:** memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.22) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) (U = unmeasured)
**Holds it in / exit:** no dependants in the universe (dependants empty) -> None
**Open:** Does allowing indoor scanning trivialize the Odyssey scan-and-explore loop (brief section 4 test 4 bypass-risk)? Not measured.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### RW - Planet Atmosphere (`rwnodetree.rwplanetatmosphere`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (ships-source, None)
**Adds:** content: 14 defs: RendererDef 8, CloudDef 4, AtmosphereDef 1, RingDef 1 (defs_by_type) / functionality: Harmony DLL with a settings screen that draws atmosphere, clouds and rings on the planet view; 3 patch ops / art: 19 textures, 174 MB on disk, 1131.6 MB est decoded (INFERRED)
**Why:** Purely cosmetic and fits a planetary expedition feel, but it is the heaviest art footprint in this batch: 186 MB on disk and a 1.1 GB decoded-texture proxy (INFERRED; not a measurement) on a list already at 30.6 GB private and 8-10 TPS (brief section 4 test 10). It has no dependants, so it can be dropped without breakage; keep only until the owner decides whether the planet view needs atmosphere, and if wanted, make our own lighter version. Per-mod cost is UNMEASURED.
**Problems:** memory 3 (texture_decoded_mb_est 1131.6 MB (INFERRED header proxy, 19 textures)) · size 2 (disk_mb 186.07) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 2) · tps U (per-mod TPS UNMEASURED; no tick flag in the DLL) (U = unmeasured)
**Holds it in / exit:** no dependants; kept only for look -> unfiled: PLANET_ATMOSPHERE_COST_OR_OWN_1
**Open:** Measure texture memory actually resident with and without the mod before any removal.
**Needs owner:** Do you want a visible atmosphere, clouds and rings on the planet view enough to keep a 186 MB mod whose textures decode to roughly 1 GB (an estimate)? If yes we should shrink or redraw it ourselves; if no it goes.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Salvage Rubble (`moja.salvagerubble`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: none (def_total 0) / functionality: 2 patch ops make Odyssey rubble piles deconstructible for steel (common), wood, components, gold and plasteel (rare) / art: 1 image
**Why:** Salvage is the clan's identity and this mod gives rubble a salvage yield. But our own scavenge/wreckage design (SALVAGE_WRECKAGE_EVERYWHERE_1, design only, nothing built) lists this mod as a SOFT conflict that touches the same yields (jawa_scavenge_system_design_2026-10-03.md line 417), so the yield curve should become ours. Plasteel and gold drops may undercut scarcity (brief section 2 anti-exponential), unmeasured.
**Problems:** memory 1 (texture_decoded_mb_est 2.1 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.46) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** our scavenge design names it as a soft conflict; nothing depends on it -> SALVAGE_WRECKAGE_EVERYWHERE_1 (design only)
**Open:** Does the plasteel/gold rubble yield break scarcity pressure? Not measured.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Signs and Comments (`dark.signs`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (ships-source, None)
**Adds:** content: 36 defs: ThingDef 29 signs, DesignatorDropdownGroupDef 4, DesignationDef 2, DesignationCategoryDef 1 / functionality: Harmony DLL (comp_tick, comp_tick_rare flags) adds sign buildings with custom label text and adds sign function to some vanilla objects; 15 patch ops / art: 123 textures, 7.7 MB disk, 59 MB est
**Why:** Labelling stockpiles and rooms aboard a ship is a quality-of-life need nothing else of ours owns, and our own MandrakePatches mod already patches it 9 times (patched_by mandrake.rm.patches 9; ThirdPartySignConfigErrors_Fix.xml adds disableImpassableShotOverConfigError to the 9 impassable signs). It ships C# source in its folder. Its 29 sign/neon art defs sit in the furniture register under owner art review, so the art may be replaced later without losing the function.
**Problems:** memory 2 (texture_decoded_mb_est 59.0 MB (INFERRED header proxy, 123 textures)) · size 1 (disk_mb 7.65) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['comp_tick', 'comp_tick_rare', 'harmony', 'settings_screen'], static_ctors 0) · tps 1 (tick flags ['comp_tick', 'comp_tick_rare']; per-mod TPS UNMEASURED) · interaction 2 (ours patch it: patched_by mandrake.rm.patches 9) (U = unmeasured)
**Holds it in / exit:** our patch ThirdPartySignConfigErrors_Fix.xml (9 refs); incompatible with Dark.CommentsAndNoSigns (not in universe) -> None
**Open:** Art is donor art: whether neon cocktail/open signs stay is a furniture-register ruling, not decided here.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Smelt More Stuff (`hol.smeltpatch`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: none / functionality: 3 patch ops remove the filter on smelting weapons and apparel / art: 1 image
**Why:** Smelting everything is a scavenger convenience, but the scavenge design lists Hol.SmeltPatch as a SOFT conflict touching the same yields (line 417 of jawa_scavenge_system_design_2026-10-03.md); our own yield curve is meant to govern what scrap returns. Nothing depends on it and 0 log errors.
**Problems:** memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.3) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** no dependants; named as soft conflict in our design -> SALVAGE_WRECKAGE_EVERYWHERE_1 (design only)
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### SpeakUp (`jpt.speakup`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (ships-source, None)
**Adds:** content: 185 InteractionDefs (defs_by_type) / functionality: Social Interaction Framework that gives pawns spoken lines in bubbles; Harmony DLL with settings screen; 29 patch ops into Core and Meaningful Parties / art: 1 image, 5 MB est
**Why:** A hard dependency of our mandrake.rsw.jawavoice (dependants_ours) whose README describes adding Jawaese lines into every SpeakUp InteractionDef; our mods reference it 380 times (patched_by: jawavoice 370, pawnflavor 10). The owner adopted it for the Jawa comedy layer (design/Jawa/mods/required_mods.md). It also needs Interaction Bubbles (dependencies).
**Problems:** memory 1 (texture_decoded_mb_est 5.4 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 3.63) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 0) · tps U (per-mod TPS UNMEASURED; no tick flag in the DLL) · interaction 2 (patched_by_ours_refs 380 (jawavoice 370)) (U = unmeasured)
**Holds it in / exit:** mandrake.rsw.jawavoice hard dep; 380 xpath refs from our mods -> None
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Stylized Slave Collars and Headgears (`gerrymon.stylizedslavecollar`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 15 defs: ThingStyleDef 13, HediffDef 1, ThingDef 1 / functionality: XML only; adds a bridle item (talking 10%, eating 50%) and 13 collar/headgear styles; Ideology dependency / art: 57 textures, 72.9 MB est
**Why:** Slavery is part of the clan doctrine (01_campaign.md; prior pass called collars on-theme), so collar styling fits, but this is mostly cosmetic ThingStyleDef art and donor art is not kept (brief section 2), and it overlaps tribeagle.simpleslaverycollars, which already adds collars. Keep until the collar family is chosen, then fold the survivors into our own styles.
**Problems:** memory 2 (texture_decoded_mb_est 72.9 MB (INFERRED header proxy, 57 textures)) · size 1 (disk_mb 0.69) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** nothing depends on it -> unfiled: SLAVE_COLLAR_FAMILY_CONSOLIDATE_1
**Open:** The bridle halves eating: does the owner want a punitive restraint item at all?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Tabletop Decorations (`ucp.tabletopdecorations`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 32 defs: ThingDef 29 tabletop decor, DesignatorDropdownGroupDef 3 / functionality: XML only; small decor items for tables, a few lamps (2 LightsTab items) / art: 76 textures, 1.2 MB disk, 120.5 MB est
**Why:** Trivial flavour (prior pass). The 29 defs are in the furniture register under per-def owner review (furniture_register_rows.json, none cut yet), and that register already flags "blank_png: every side variant is transparent" on at least one row, so some art is broken. Donor art is not kept (brief section 2), so the exit is the register review that regenerates or cuts per def.
**Problems:** memory 2 (texture_decoded_mb_est 120.5 MB (INFERRED header proxy, 76 textures)) · size 1 (disk_mb 1.22) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** nothing depends on it; 29 rows pending in the furniture register -> unfiled: FURNITURE_DONOR_DECOR_REVIEW_1
**Open:** Identify which decor survive the furniture-register sitting.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### None (`vlvop.tormentmaster.expansion`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (UNVERIFIED) · **Fit:** neutral · **Source:** none (none, None)
**Adds:** content: UNKNOWN: installed in neither root, no facts beyond its id (README known gap) / functionality: UNKNOWN; our furniture register still holds 6 rows from an earlier install: torture devices, a laser flayer, an organ vending machine / art: UNKNOWN
**Why:** The mod is in FULL.LATEST (position 306) and named by ResearchRetag's About.xml and restructured_model_v4.json, but is not on disk, so it cannot load and nothing can be measured. Most conservative verdict: do not eliminate unseen content; the real action is to decide whether the id should stay in the list.
**Problems:** log_noise U (not loaded in the measured session) (U = unmeasured)
**Holds it in / exit:** ResearchRetag About.xml lists it; a research retag exists for TormentMaster_CranialPinResearch; not installed: nothing to retire -> unfiled: TORMENTMASTER_STALE_LIST_ENTRY_1
**Open:** Why is an uninstalled id in the 550-list and in ResearchRetag?
**Needs owner:** vlvop.tormentmaster.expansion (torture devices, an organ-vending machine) is on the active list but is not installed on this machine. Do you want it re-subscribed and judged, or dropped from the list and our research patches?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Torture Pod (`tsa.torturepod`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (ships-source, None)
**Adds:** content: 12 defs: ThoughtDef 5, HediffDef 2, JobDef 2, WorkGiverDef 2, ThingDef 1 / functionality: one DLL (settings screen); a torture pod that lowers prisoner resistance, scars the victim and sours colonist mood / art: 7 images, 13 MB est
**Why:** Prisoner-breaking fits a slaving scavenger clan but the pod art/behaviour is a generic donor mechanic; mandrake.rut.pawnflavor patches it 50 times (patched_by) to attach faction flavour, so it is held in by our patches. It ships C# source (13 .cs). Exit is an own prisoner-pressure mechanic, unfiled.
**Problems:** memory 1 (texture_decoded_mb_est 13.3 MB (INFERRED header proxy, 7 textures)) · size 1 (disk_mb 2.74) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['settings_screen'], static_ctors 0) · tps U (per-mod TPS UNMEASURED; no tick flag in the DLL) · interaction 2 (patched_by mandrake.rut.pawnflavor 50) (U = unmeasured)
**Holds it in / exit:** mandrake.rut.pawnflavor patches (50 refs) -> unfiled: PRISONER_RESISTANCE_DEVICE_OWN_1
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Trystan Traveller's Shuttle Schematics (`trouperton.trystantravellersshuttleschematics`)
**Verdict:** REPLACE-NOW-WITH-OUR-OWN (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: 10 defs: ThingDef 6, TransportShipDef 2, WorldObjectDef 2 / functionality: XML only (Odyssey dependency); personal and cargo shuttle variants / art: 33 textures, 4.4 MB disk, 202.5 MB est
**Why:** Shuttles compete with the gravship, the only scalable tree and the campaign centre (brief section 2; forbidden_mods.md movement-solves-problems guard); a personal long-range shuttle with better hop range erodes the ship-or-nothing logic. Donor art is not kept. Our Stillsand kernel and vehicle register mention it (vehicle_register_rows.json, RM_LeviathanKernel.cs), so check those references first. Scope: 2 TransportShipDefs and 6 ThingDefs; or simply ELIMINATE if no use is found.
**Problems:** memory 2 (texture_decoded_mb_est 202.5 MB (INFERRED header proxy, 33 textures)) · size 1 (disk_mb 4.4) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** vehicle_register_rows.json has rows; Stillsand source mentions "trystan" (2 hits) - not read in detail -> unfiled: SHUTTLE_VARIANTS_OWN_OR_CUT_1
**Open:** Read what Stillsand does with the string "trystan" before any removal.
**Needs owner:** Should extra personal and cargo shuttles exist at all, or is the gravship the only vehicle? This mod adds shuttles with longer hop range.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Tunneler Expanded (`error277.tunneler.expanded`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: 28 defs: ThingDef 21, RecipeDef 3, TerrainDef 3, ResearchProjectDef 1 / functionality: XML only; cave-dweller buildings, terrain, recipes and a research project / art: 45 textures, 5.4 MB disk, 15.1 MB est
**Why:** Prior pass called its tunneling content on-theme for the Nomad+Tunneler ideology memes. Our ResearchRetag retags it (8 refs, patched_by mandrake.rut.researchretag) and the plant register holds its mushrooms (Plant_NeutroShroom etc.) in the crystalline caverns biomes, so the content is already wired into our biome and research work. XML only, small, 0 log errors.
**Problems:** memory 1 (texture_decoded_mb_est 15.1 MB (INFERRED header proxy, 45 textures)) · size 1 (disk_mb 5.39) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) · interaction 2 (patched_by mandrake.rut.researchretag 8) (U = unmeasured)
**Holds it in / exit:** mandrake.rut.researchretag patches it (8 refs); plant register references its mushrooms -> None
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Vanilla Skills Rexamined (`gravenwitch.vsrexamined`)
**Verdict:** ELIMINATE-COMPLETELY (MEASURED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: 5 StatDefs only (defs_by_type) / functionality: XML patch of Vanilla Skills Expanded: 105 patch ops rebalance and condense expertise (stat offsets); no code / art: 1 image
**Why:** The owner already ruled it retired together with Survival Tools Reborn on 2026-09-11 (STAT_NORM_WAVE3_RETIRE_1: "retire gravenwitch.VSRexamined ... TOGETHER"), and the audit measured it save-clean (0 placed; it declares only 5 StatDefs, no ThingDefs). Yet it is still in FULL.LATEST at position 355, so either the retirement was never executed on this list or it was re-added. It rebalances a VSE expertise ladder, a parallel progression system (brief section 2 anti-exponential), and declares itself incompatible with zlj.staticqualityplus and imranfish.madderskills. Nothing depends on it (dependants empty); its StatDefs are not inherited (no ParentName risk).
**Problems:** memory 1 (texture_decoded_mb_est 1.9 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.14) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** nothing (dependants empty); save placement: 0 as of CANONICAL_ASHKARR_2026-09-09 per STAT_NORM_WAVE3_RETIRE_1 (stale save, re-check) -> None
**Open:** Why is a ruled-retired mod still on the 550 list? Check whether ModsConfig was reverted by a later list rebuild.
**Needs owner:** You retired Vanilla Skills Rexamined on 2026-09-11 but it is back on the full list. Should it be unticked again, or did you want it back?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### VehicleRaid Framework (`gabrieel1482.raidvehicleframework`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 20 defs: DutyDef 13, JobDef 3, GenStepDef 1, SoundDef 1, ThingDef 1, Vehicles.AirdropDef 1 / functionality: Harmony DLL (comp_tick, map_component_tick flags): lets other mods add raids that arrive in vehicles; needs Vehicle Framework / art: 2 images
**Why:** The owner pre-committed (V2_DREAMS.md section 0b, 2026-08-12): "The point is to be able to have enemies use these against us in raids. If they can't or won't, then these three mods should be dropped." The test is unresolved there, and VRF_SettlementVehicleDef was empty in the dump. Nothing in the universe depends on it (dependants empty) and no mod of ours references it. It stays only until that binary test is run.
**Problems:** memory 1 (texture_decoded_mb_est 6.4 MB (INFERRED header proxy, 2 textures)) · size 1 (disk_mb 1.14) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['comp_tick', 'harmony', 'map_component_tick', 'settings_screen'], static_ctors 4) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) · tps 1 (tick flags comp_tick, map_component_tick on a framework that adds raids) (U = unmeasured)
**Holds it in / exit:** V2_DREAMS.md section 0b open test; dependency of nothing -> unfiled: RAID_VEHICLES_DO_ENEMIES_USE_THEM_1
**Open:** Run V2_DREAMS 0b checks: does any live PawnKind or faction pawnGroupMaker use a vehicle?
**Needs owner:** Your 2026-08-12 test says drop the vehicle-raid mods if enemies never use vehicles against us. Has anyone shown that they do? If not, drop VehicleRaid Framework (and Vehicle Framework with it?).
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Wing's Meaningful Parties (`winggar.meaningfulparties`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/benjaminiserman/MeaningfulParties (github, MIT)
**Adds:** content: 119 PartyCauseDefs / functionality: Harmony DLL (world_component_tick): colonists throw parties for birthdays, raid survival, settling a tile, brewing etc without changing party frequency; 3 patch ops / art: 1 image, 0.7 MB est
**Why:** Our mods write to its def type heavily: patched_by mandrake.rut.pawnflavor 110, mandrake.rm.biomes 27, mandrake.rsw.patches 23, plus gravtide and lightsaber mods (patched_by_ours_refs 166). It supplies reasons-to-party flavour we do not intend to rebuild, and several reasons (settling a new tile, surviving a raid) read as expedition life. MIT source verified on GitHub, last push 2025-08-12; 0 log errors.
**Problems:** memory 1 (texture_decoded_mb_est 0.7 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.27) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['harmony', 'world_component_tick'], static_ctors 0) · tps 1 (tick flags ['world_component_tick']; per-mod TPS UNMEASURED) · interaction 2 (patched_by_ours_refs 166) (U = unmeasured)
**Holds it in / exit:** 166 xpath refs from our mods (pawnflavor 110, biomes 27, rsw.patches 23) -> None
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Wirehead Style (`tleno.wireheadstyle`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: 28 defs: ThingStyleDef 25, ThingDef 2, StyleCategoryDef 1 / functionality: XML only; Ideology style category with exposed-cable techno-cultist looks / art: 68 textures, 1.9 MB disk, 18.7 MB est
**Why:** The look (exposed cables, piles of electronics, post-apocalyptic techie) is a very good match for Jawa junk-tech. But it is all style art, donor art is not kept (brief section 2, vanilla counts as donor), so the exit is our own style set. No reference to it exists in src/, so whether any Utinni ideoligion actually picks this style is UNMEASURED.
**Problems:** memory 1 (texture_decoded_mb_est 18.7 MB (INFERRED header proxy, 68 textures)) · size 1 (disk_mb 1.89) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** nothing found referencing it in src/ -> unfiled: UTINNI_IDEO_STYLE_OWN_ART_1
**Open:** Does the frozen Jawa ideoligion use Wirehead style? Check the save/ideo definition.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### [BTD] Gravship Blueprints (`btd.remix.gravshipblueprints`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 27 defs: ThingDef 10, HistoryEventDef 3, QuestScriptDef 3, SitePartDef 3, IncidentDef 2, ScenPartDef 2 / functionality: Harmony DLL (game/map component ticks, settings): a Save Ship button on the pilot console, a scenario that starts with a saved gravship, downed-gravship quest sites and an endgame gravship salvage site / art: 40 textures, 44 MB disk, 177 MB est
**Why:** The campaign's gravship is one fixed Rakatan ship delivered in the savegame; ship blueprints, extra downed gravships to salvage and a start-with-your-saved-ship scenario compete with that (brief section 1, flight hardware ships unbuilt). It is held in by our patches: BTDGravshipQuest_GrammarFix (mandrake.rm.patches 1; a validation walk exists) and a Droidworks distress-call repoint that is a no-op because guy762.KotORDroids is not in the facts (rsw.droidworks 2), and by a third-party dependant btd.gbp.shippack.kotor.vge. The Save Ship function may be useful for authoring.
**Problems:** memory 2 (texture_decoded_mb_est 177.1 MB (INFERRED header proxy, 40 textures)) · size 2 (disk_mb 44.29) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['game_component_tick', 'harmony', 'map_component_tick', 'settings_screen'], static_ctors 4) · tps 1 (tick flags ['game_component_tick', 'map_component_tick']; per-mod TPS UNMEASURED) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) · interaction 2 (patched_by mandrake.rsw.droidworks 2, mandrake.rm.patches 1) (U = unmeasured)
**Holds it in / exit:** mandrake.rm.patches BTDGravshipQuest_GrammarFix; mandrake.rsw.droidworks BTD_DistressCall_Repoint (inert without KotORDroids); dependant btd.gbp.shippack.kotor.vge (third party) -> unfiled: GRAVSHIP_BLUEPRINT_QUEST_SITES_DECIDE_1
**Open:** Are the 3 QuestScriptDefs wanted as scavenging content or do they dilute the one-ship premise?
**Needs owner:** This mod lets players save their gravship as a blueprint and finds other downed gravships to salvage. Should the campaign have any gravship other than the Utinni, or should these quests be cut?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### [NL] Facial Animation - Experimentals (`nals.facialanimationexperimentals`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 93 defs: FaceAnimationDef 49, LidTypeDef 7, EyeballTypeDef 6, MouthShapeDef 5, SkinTypeDef 5, BrowTypeDef 3, ... / functionality: XML only; the human-race half of [NL] Facial Animation, with textures and definitions for new features; 4 patch ops / art: 359 textures, 1.95 MB disk, 476 MB est
**Why:** Animated faces are core to the look (owner rule: cosmetic changes can break animated faces, so ask first), and this is the human-race content of Facial Animation, patched by vanillaexpanded.vtexe.facialanims (7), memegoddess.giddyup (5) and others. But the Jawa and Star Wars pawns use their own head sets (MandrakePatches HeadSetForFA_Revive, SW_HeadTypes), so the human texture set matters mainly for non-Jawa pawns. Cost is the 476 MB decoded-texture proxy (INFERRED).
**Problems:** memory 3 (texture_decoded_mb_est 476.1 MB (INFERRED header proxy, 359 textures)) · size 1 (disk_mb 1.95) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** patched by vtexe.facialanims 7, giddyup 5, complexjobs 2 and others; depends on nals.facialanimation -> unfiled: FACIAL_ANIMATION_HEADSET_AUDIT_1
**Open:** Which of the 8 Facial Animation add-ons in this batch are actually reached by a pawn in the campaign?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Character Editor Retextured (`neronix17.retexture.charactereditor`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: none (def_total 0) / functionality: retextures the UI of Character Editor; no code / art: 49 images, 1.1 MB disk, 85 MB est
**Why:** UI skin for void.charactereditor (list position 87), an authoring/cheat tool whose own verdict belongs to its batch. Pure UI art passes the pillars trivially (brief section 4 test 4) but exists only as long as Character Editor does. Nothing depends on it.
**Problems:** memory 2 (texture_decoded_mb_est 85.4 MB (INFERRED header proxy, 49 textures)) · size 1 (disk_mb 1.11) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** depends on Character Editor staying -> unfiled: CHARACTER_EDITOR_VERDICT_FOLLOW_1
**Open:** Follow the Character Editor verdict.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Fortifications - Industrial (`aoba.fortress.industrial`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: 111 defs: ThingDef 53, TerrainDef 13, RecipeDef 12, ResearchProjectDef 6, SoundDef 6, FleckDef 4 / functionality: XML only; fortification walls, defences and terrain; 64 patch ops into Core, VFE Architect and VQE Ancients / art: 460 textures, 15.5 MB disk, 361.7 MB est
**Why:** Static fortifications are a camp-defence tool (land, camp loop; brief section 1) and fit qualitative defence rather than an arms race. Our ResearchRetag retags its research (patched_by researchretag 28, armoury 2), so it is wired into the campaign research tree; the prior pass recorded a documented adoption reason. The memory proxy is the cost: 361.7 MB est (INFERRED, severity 3).
**Problems:** memory 3 (texture_decoded_mb_est 361.7 MB (INFERRED header proxy, 460 textures)) · size 1 (disk_mb 15.46) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) · interaction 2 (patched_by researchretag 28, armoury 2) (U = unmeasured)
**Holds it in / exit:** mandrake.rut.researchretag 28 refs; mandrake.rsw.armoury 2 refs -> None
**Open:** Is 361 MB of decoded art justified by actual use? Not measured.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Makeshift: Re-Examined (`smxrez.makeshiftreexamined`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** https://github.com/Smxrez/Makeshift-ReExamined (github-search, )
**Adds:** content: 2 ThingDefs / functionality: XML rebalance of Vanilla Weapons Expanded - Makeshift (22 patch ops on 21 ThingDefs) / art: 2 images
**Why:** Makeshift weapons are junk-built scavenger gear (resonant), but this mod only rebalances VWE-Makeshift (vanillaexpanded.vwems, list position 358), whose own verdict is in the weapons batch; weapons are being absorbed into the RSW Armoury (brief section 3). It lives or dies with its parent. Source repo is a name match (github-search INFERRED).
**Problems:** memory 1 (texture_decoded_mb_est 4.8 MB (INFERRED header proxy, 2 textures)) · size 1 (disk_mb 0.46) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) (U = unmeasured)
**Holds it in / exit:** hard dependency on vanillaexpanded.vwems -> unfiled: WEAPON_DONOR_REBALANCE_FOLLOW_PARENT_1
**Open:** Follow the vanillaexpanded.vwems verdict in batch 11.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### More Ritual Rewards (`sinnamon.moreritualrewards`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/ahls/RimworldRitualExpansion (github, None)
**Adds:** content: 22 defs: RitualAttachableOutcomeEffectDef 16, GameConditionDef 4, IncidentDef 1, WeatherDef 1 / functionality: two DLLs with Harmony: extra Ideology ritual outcome rewards including game conditions and a weather; 4 patch ops (Improved Insectoids and Precepts and Memes gated) / art: 1 image
**Why:** Rituals carry doctrine, so extra reward outcomes touch our own ritual design; four GameConditionDefs and a WeatherDef are not content I could read in detail here, so their effect on weather pressure and rewards is UNVERIFIED. Upstream source is stale (last push 2021-09-08) and ships 6 .cs in the folder. Hold it only until our doctrine mod defines its own ritual outcomes.
**Problems:** memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 2.19) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 3 (dll_count 2, flags ['harmony'], static_ctors 1) · tps U (per-mod TPS UNMEASURED; no tick flag in the DLL) · maintenance 3 (upstream repo last push 2021-09-08) (U = unmeasured)
**Holds it in / exit:** no dependants -> unfiled: RITUAL_REWARDS_OWN_SET_1
**Open:** Read the 4 GameConditionDefs and the WeatherDef: do they add free benefits?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Vanilla Mining Outpost Patch (`kuhlyus.modpatch.vanillaoutpost`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: none / functionality: XML patch adding ores from other mods to Vanilla Outposts Expanded mining outposts (21 patch ops on 19 WorldObjectDefs) / art: 2 images
**Why:** Only useful if Vanilla Outposts Expanded stays (list position 346; its verdict is in batch 7), and most of the ore mods it targets (Gemstones, MorrowRim Adamantium, Obsidia, Kraltech, Starbound ...) are patch_findmod_names that are not among the mods I could confirm in the facts. Outposts as passive income conflict with the no-automation pillar (brief section 2), unverified. Nothing depends on it.
**Problems:** memory 1 (texture_decoded_mb_est 2.1 MB (INFERRED header proxy, 2 textures)) · size 1 (disk_mb 0.53) · log_noise 1 (0 error occurrences / 0 distinct, chatter 1 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** depends on vanillaexpanded.outposts -> unfiled: OUTPOST_PATCHES_FOLLOW_PARENT_1
**Open:** Which of its 13 target mods are actually in the list? Not measured.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Alpha Animals Patch for Outposts Mines (`daria40k.alphaanimalspatchoutposts`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Daria40K/Alpha-Animals-Patch-for-Outposts-Mines (github-search, )
**Adds:** content: none / functionality: XML patch adding Alpha Animals sky steel ore to Vanilla Outposts mines (2 patch ops on 1 WorldObjectDef) / art: 1 image
**Why:** Held only by two donors that are on the sunset track: Alpha Animals is the main absorption job (72 of 128 donor rows; donor_retirement_plan_2026-10-02 section 1) and Outposts may go. When Alpha Animals leaves, sky steel disappears and this patch is dead weight. Source link is a name match, UNVERIFIED.
**Problems:** memory 1 (texture_decoded_mb_est 1.1 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.2) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) (U = unmeasured)
**Holds it in / exit:** depends on sarg.alphaanimals and vanillaexpanded.outposts -> unfiled: ALPHA_ANIMALS_RETIRE_TAIL_PATCHES_1
**Open:** Delete in the same change that retires Alpha Animals.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Ancient Ruins All Deconstructible (`meteores.ancienturbanruinsalldeconstructible.aurad`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: none (def_total 0) / functionality: XML only: 48 patch ops that make almost everything in Ancient Urban Ruins deconstructible from outside / art: 1 image
**Why:** Two owner-side documents say cut: forbidden_mods.md lists it as the exact inverse of the exploration rule (it lets you strip ruins from outside without entering) and ancient_ruins_mod_audit.md (ANCIENT_RUINS_MOD_AUDIT_1, 2026-10-03) recommends cutting the whole family because the content (mall maps, firearms, LEGO loot) is "not very Star Wars at all". Retirement cost: it patches only defs of xmb.ancienturbanruins.mo (patches_mods), has one third-party dependant (the Hit Point mod, same verdict), no ParentName exposure (no defs of its own), and placed ruins in the current save are UNMEASURED.
**Problems:** memory 1 (texture_decoded_mb_est 4.7 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.54) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** dependant meteores.ancienturbanruinsvanillaloot.aurvl -> None
**Open:** forbidden_mods.md also says to use the Hit Point mod instead of AURAD, while Hit Point declares AURAD as a dependency: which document stands?
**Needs owner:** Two earlier notes disagree about the Ancient Urban Ruins family: one says keep the Hit Point mod and forbid All Deconstructible; the 2026-10-03 audit says cut all three. Which stands?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Utility Columns (`nephlite.orbitaltradecolumn`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/RealTelefonmast/UtilityColumns (github-search, gpl-3.0)
**Adds:** content: 36 defs: ThingDef 29 columns, ResearchProjectDef 3, TerrainDef 3, RWCSettingsDef 1 / functionality: two DLLs with Harmony (comp_tick, comp_tick_rare, 5 static ctors): roof-holding utility columns incl. lamp and crystal columns; 9 patch ops into Royalty and Ideology / art: 177 textures, 15.7 MB disk, 81 MB est
**Why:** Columns that hold up roofs and light rooms are useful aboard, but our mods are wired to it: ResearchRetag retags its research (OrbitalTradeColumnRes goes to RUT_Tree_Workshop; patched_by researchretag 16) and Armoury patches it 5 times. The 6 furniture-register rows are lighting/grave art under owner art review (none cut), and donor art is not kept (brief section 2). Source link is a name match to RealTelefonmast/UtilityColumns (GPL-3.0, last push 2024-05-13, over 2 years), UNVERIFIED as this mod's repo.
**Problems:** memory 2 (texture_decoded_mb_est 81.0 MB (INFERRED header proxy, 177 textures)) · size 1 (disk_mb 15.72) · log_noise 1 (0 error occurrences / 0 distinct, chatter 1 in the 550-mod session) · complexity 3 (dll_count 2, flags ['comp_tick', 'comp_tick_rare', 'harmony'], static_ctors 5) · tps 1 (tick flags ['comp_tick', 'comp_tick_rare']; per-mod TPS UNMEASURED) · interaction 2 (patched_by mandrake.rut.researchretag 16, mandrake.rsw.armoury 5) · maintenance 3 (nearest matched repo last pushed 2024-05-13 (>2 years); match unverified) (U = unmeasured)
**Holds it in / exit:** researchretag 16 refs, armoury 5 refs -> unfiled: UTILITY_COLUMNS_ART_OWN_OR_CUT_1
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Genetic Biotech for Facial Animation (`sd.fa.geneticheadsbiotech`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 7 defs: HeadTypeDef 5, LidTypeDef 2 / functionality: XML only; extra Facial Animation head types for Biotech genes (fur-covered, gaunt, heavy jaw variants, gray/red eyes) / art: 117 textures, 0.8 MB disk, 132.9 MB est
**Why:** Companion to the Genetic Heads Framework (sd.fa.geneticheadsframework, list position 394). Which pawns use these head types is UNMEASURED, and head sets are what our HeadSetForFA_Revive patch has to keep alive for Facial Animation; removing a head set under a placed pawn risks a missing-face error. Hold it until the head-set audit says which races the campaign actually draws.
**Problems:** memory 2 (texture_decoded_mb_est 132.9 MB (INFERRED header proxy, 117 textures)) · size 1 (disk_mb 0.83) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** depends on the Genetic Heads Framework staying; pawn placement UNMEASURED -> unfiled: FACIAL_ANIMATION_HEADSET_AUDIT_1
**Open:** Which Biotech xenotype in the campaign draws fur-covered heads?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Genetic Mods for Facial Animation (`sd.fa.geneticheadsmods`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 0 own defs; 8 patch ops; LoadFolders gates per mod / functionality: XML plus textures: head, eye, lid and mouth sets for other mods, loaded per LoadFolders only when the named mod is active (VRE Genie/Phytokin/Saurid, Faun, Bone Reapers, Profaned, ERN races, Star Wars Xenotypes) / art: 809 textures, 6.4 MB disk, 1057 MB est before LoadFolders gating (INFERRED upper bound)
**Why:** The 1,057 MB figure is an upper bound: LoadFolders.xml (opened) loads each pack only if its host mod is active, and in the facts VRE Genie, Phytokin, Saurid, Alpha Genes and Big and Small are active while guy762.StarWarsXenotypes, Faun, Profaned, Bone Reapers and the Erin races are not found, so the Star Wars heads in this pack (Gungan, Ithorian, Mon Cal, Rodian, Wookiee, Tusken, Hutt mouth ...) appear to be inert today (INFERRED). It stays while those VRE races remain; if the VRE races go, so does this.
**Problems:** memory 3 (texture_decoded_mb_est 1057.3 MB (INFERRED header proxy, 809 textures)) · size 1 (disk_mb 6.37) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** hosts: vanillaracesexpanded.genie, .phytokin, .saurid, sarg.alphagenes, redmattis.bigsmall.core -> unfiled: FACIAL_ANIMATION_HEADSET_AUDIT_1
**Open:** Confirm guy762.StarWarsXenotypes absence in the live ModsConfig (facts universe lacks it).
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Reel's Facial Animation Textures (`reel.facialanims`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: 23 defs: MouthTypeDef 9, EyeballTypeDef 7, LidTypeDef 7 / functionality: XML only; six custom vanilla-style eye/mouth textures "based on Roblox faces", for [NL] Facial Animation with VTE and EyeGenes2 / art: 422 textures, 2.1 MB disk, 559.7 MB est
**Why:** Stylistically a cartoon face source (its own description names Roblox faces), which sits poorly with the matte natural-history register (brief section 2). But pawns in the save may carry its eye/mouth defs, and cosmetic changes to animated faces need the owner's permission first, so it cannot simply go. Dependant: sd.fa.reelsadjustments. Hold until the head-set audit.
**Problems:** memory 3 (texture_decoded_mb_est 559.7 MB (INFERRED header proxy, 422 textures)) · size 1 (disk_mb 2.08) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** dependant sd.fa.reelsadjustments (third party); pawn placement UNMEASURED -> unfiled: FACIAL_ANIMATION_HEADSET_AUDIT_1
**Open:** none
**Needs owner:** Several Facial Animation add-ons give pawns cartoon, anime or Roblox-style faces (Reel, Danzinagri, parts of the Genetic Heads packs). Which face styles are acceptable for pawns in this campaign: only vanilla and our own, or are these fine?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Adjustments for Reel's Facial Animation Textures (`sd.fa.reelsadjustments`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: none / functionality: texture-only patch shifting Reel's female eyes and some mouths; no code / art: 179 textures, 22.6 MB disk, 247 MB est
**Why:** Moves the placement of someone else's art (author says "I made none of the art"; will take it down if Reel asks). It lives and dies with reel.facialanims, so its verdict follows that one. Re-hosted third-party art is a licence/availability risk (maintenance).
**Problems:** memory 2 (texture_decoded_mb_est 247.3 MB (INFERRED header proxy, 179 textures)) · size 2 (disk_mb 22.56) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** depends on reel.facialanims -> unfiled: FACIAL_ANIMATION_HEADSET_AUDIT_1
**Open:** Same card as reel.facialanims.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### All Specialists Can Work (`opa.allspecialistscanwork`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: none (2 patch ops on PreceptDefs) / functionality: XML only; removes the work restriction on the Ideology Specialist role / art: 1 image
**Why:** A crew of three to eight cannot spare a role-holder who refuses work (brief section 1: crew ~3-8), so removing the Specialist work ban is a small quality-of-life fix that we are not going to build ourselves. It does not touch speed or scaling, so it passes the 7 questions. Incompatible only with Ducks.SpecialistsCanWork, which is not in the facts.
**Problems:** memory 1 (texture_decoded_mb_est 2.9 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.14) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** no dependants -> None
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Alpha Skills (`sarg.alphaskills`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/vbardales/Rimworld-Skill-Icons (github-search, other)
**Adds:** content: 98 defs: PassionDef 51, HediffDef 19, ExpertiseDef 19, StatDef 5, ThoughtDef 4 / functionality: one DLL with Harmony; Vanilla Skills Expanded add-on with 13 new passions and 19 expertises / art: 120 textures, 2 MB disk, 44.2 MB est
**Why:** It is an add-on to Vanilla Skills Expanded (hard dependency), and an expertise ladder is a parallel progression system of the kind brief section 2 excludes, though the owner ruling on VSE itself is not in the brief (see section 5 item 4, the ISEKAI tension). The alpha-family research note records that AlphaSkills was "in our stack and was not opened". So the verdict follows VSE: keep while VSE stays, and mark for review. Repo link in the facts is a name guess (vbardales/Rimworld-Skill-Icons), UNVERIFIED.
**Problems:** memory 1 (texture_decoded_mb_est 44.2 MB (INFERRED header proxy, 120 textures)) · size 1 (disk_mb 2.0) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['harmony'], static_ctors 1) · tps U (per-mod TPS UNMEASURED; no tick flag in the DLL) (U = unmeasured)
**Holds it in / exit:** hard dependency chain vanillaexpanded.skills, VEF Core -> unfiled: VSE_EXPERTISE_LADDER_RULING_1
**Open:** Brief section 5 item 4 (ISEKAI leveling vs parallel ladders) is unresolved: expertise ladders fall under the same question.
**Needs owner:** Alpha Skills and Vanilla Skills Expanded add more skill passions and expertises. Is a skill-specialisation ladder allowed in the campaign, or does it count as a parallel progression system you want out?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Ancient Urban Ruins Hit Point (`meteores.ancienturbanruinsvanillaloot.aurvl`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: none (22 patch ops on Ancient Urban Ruins defs) / functionality: XML only; gives hit points to ruin walls and objects and changes loot; warns of -1 HP walls and save incompatibility / art: 1 image
**Why:** Part of the ruins family the 2026-10-03 audit (ancient_ruins_mod_audit.md) recommends cutting entirely because the content is mall maps and modern loot, not Star Wars. forbidden_mods.md wanted this very mod as the counterweight to All Deconstructible, so the two documents disagree; the later audit post-dates it. Its 22 patch ops only apply to defs of xmb.ancienturbanruins.mo, so it falls away if the base is cut. Its own About warns players who started the Scavenger Group scenario not to install it.
**Problems:** memory 1 (texture_decoded_mb_est 5.3 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.58) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** depends on XMB.AncientUrbanrUins.MO and AURAD -> None
**Open:** Same ruling as meteores AURAD: decide the family together.
**Needs owner:** Same question as All Deconstructible: do we cut the whole Ancient Urban Ruins family (the base mod and both patches)?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Keyz' Allow Utilities (`keyz182.keyzallowutilities`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/spdskatr/RWModdingResources (github, MIT)
**Adds:** content: 32 defs: KeyBindingDef 17, DesignationDef 5, JobDef 2, WorkGiverDef 2, WorkTypeDef 2, EffecterDef 1 / functionality: two DLLs with Harmony (15 static ctors): bulk allow/forbid, selection helpers, haul urgently / art: 22 images, 11 MB est
**Why:** Hauling and allowing is the daily friction of a scavenger crew sorting salvage, and nothing of ours builds a bulk-allow tool. QoL passes the 7 questions trivially. Caution: it adds two WorkTypeDefs that Complex Jobs rewrites, and our scavenge design places a new Salvaging work type in the same Work tab. The linked repo in the facts (spdskatr/RWModdingResources, MIT, pushed 2020-08-14) is a modding-resource library, not this mod's source, so source availability is UNVERIFIED.
**Problems:** memory 1 (texture_decoded_mb_est 11.0 MB (INFERRED header proxy, 22 textures)) · size 1 (disk_mb 1.43) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 3 (dll_count 2, flags ['harmony', 'settings_screen'], static_ctors 15) · tps U (per-mod TPS UNMEASURED; no tick flag in the DLL) · interaction 1 (adds 2 WorkTypeDefs; Complex Jobs (patch_ops_all 772) rewrites worktypes) (U = unmeasured)
**Holds it in / exit:** no dependants -> None
**Open:** Test the 2 added work types against Complex Jobs load-last behaviour.; Find the real source repo (keyz182).
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Simple Slavery Collars (`tribeagle.simpleslaverycollars`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (ships-source, None)
**Adds:** content: 24 defs: JobDef 6, ThingDef 5, ThoughtDef 4, WorkGiverDef 4, HediffDef 3, MentalStateDef 1 / functionality: Harmony DLL (115 .cs files shipped, comp_tick flags, 8 static ctors): shock-style slave collars from Simple Slavery plus Ideology slavery tweaks; 24 patch ops incl. Vanilla Gravship Expanded / art: 41 images, 5.6 MB est
**Why:** Slavery is part of the clan doctrine, and our PawnFlavor mod patches this mod 130 times (patched_by mandrake.rut.pawnflavor 130; patched_by_ours_refs 130), so it is wired into the faction flavour. It ships its full C# source folder, easing maintenance if the author stops. Overlaps in purpose with gerrymon.stylizedslavecollar (cosmetic styles).
**Problems:** memory 1 (texture_decoded_mb_est 5.6 MB (INFERRED header proxy, 41 textures)) · size 1 (disk_mb 8.67) · log_noise 1 (0 error occurrences / 0 distinct, chatter 3 in the 550-mod session) · complexity 2 (dll_count 1, flags ['comp_tick', 'comp_tick_rare', 'harmony', 'settings_screen'], static_ctors 8) · tps 1 (tick flags ['comp_tick', 'comp_tick_rare']; per-mod TPS UNMEASURED) · interaction 2 (patched_by_ours_refs 130) (U = unmeasured)
**Holds it in / exit:** mandrake.rut.pawnflavor 130 refs -> None
**Open:** Three small chatter log lines (log_chatter_lines 3): read them in the next full-list session.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Tabula Rasa (`neronix17.toolbox`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (ships-source, None)
**Adds:** content: 13 defs: JobDef 5, ApparelLayerDef 4, FleshTypeDef 1, HediffDef 1, ScenPartDef 1, ThoughtDef 1 / functionality: library DLL (Harmony, 9 static ctors): reusable code for Outpost 21 mods; our StarWarsRaces uses its TabulaRasa.DefModExt_HeadTypeStuff / art: 66 textures, 9.7 MB disk, 43.8 MB est
**Why:** A library with named dependants in the universe: neronix17.outerrim.core, .furnitureanddecor, neronix17.outland.genetics and neronix17.shieldgenerators. Our src/RimStarWars/StarWarsRaces SW_HeadTypes.xml carries about 36 MayRequire="neronix17.toolbox" references and JawaFactionRoster.xml 3, and PawnFlavor patches it 10 times. The MayRequire guards make it soft for us, but required_mods.md marks it a hard dep of every Outer Rim module. Source is shipped inside the mod folder.
**Problems:** memory 1 (texture_decoded_mb_est 43.8 MB (INFERRED header proxy, 66 textures)) · size 1 (disk_mb 9.72) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['comp_tick', 'comp_tick_rare', 'harmony', 'settings_screen'], static_ctors 9) · tps 1 (tick flags ['comp_tick', 'comp_tick_rare']; per-mod TPS UNMEASURED) (U = unmeasured)
**Holds it in / exit:** dependants: neronix17.outerrim.core, neronix17.outerrim.furnitureanddecor, neronix17.outland.genetics, neronix17.shieldgenerators; 36+3 MayRequire refs in our RimStarWars/RimUtinni defs; pawnflavor 10 refs -> None
**Open:** Review the Outer Rim modules' own verdicts: if all go, the toolbox goes with them.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### VFE Pirates - Hardworking Warcaskets (`dmp.vfepirates.warcasketwork`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: none (11 patch ops on VFE Pirates Warcasket and Trait defs) / functionality: XML only: warcasket suits may work at reduced work speed; configurable through VEF Toggable Patches / art: 2 images
**Why:** A leaf patch that exists only for oskarpotocki.vfe.pirates (list position 449), whose own verdict is in the factions batch; warcasket-as-worker bends the "no arms race" pillar mildly by adding working labour to combat armour, unmeasured. Nothing depends on it.
**Problems:** memory 1 (texture_decoded_mb_est 4.7 MB (INFERRED header proxy, 2 textures)) · size 1 (disk_mb 0.63) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** hard dependency on oskarpotocki.vfe.pirates -> unfiled: VFE_PIRATES_PATCHES_FOLLOW_PARENT_1
**Open:** Follow the VFE Pirates verdict.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### [GTG]Traders Accept All Junk Gear (`teiwaz.taajg`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: none (3 patch ops on 2 TraderKindDefs) / functionality: XML patch making certain traders buy junk gear; needs GTG Trader Core / art: 1 image
**Why:** Selling battlefield junk is a scavenger convenience, but our scavenge design lists Teiwaz.TAAJG as a SOFT conflict touching the same yields (jawa_scavenge_system_design_2026-10-03.md line 417), and our own Bazaar trade window (a whole-deal haggle) now owns the trading experience. Held in by nothing; exit is the scavenge yield curve.
**Problems:** memory 1 (texture_decoded_mb_est 5.9 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.95) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** depends on teiwaz.gtgtradercore -> SALVAGE_WRECKAGE_EVERYWHERE_1 (design only)
**Open:** Check interaction with mandrake.rm.bazaar trader defs: not measured.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### [GTG]Traders Accept Chunks & Corpses (`teiwaz.tacac`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: none (3 patch ops on 2 TraderKindDefs) / functionality: XML patch making certain caravans buy chunks and corpses; needs GTG Trader Core / art: 1 image
**Why:** Same family and author as TAAJG; chunks and corpses selling bypasses a disposal chore. Not named in the scavenge design's conflict list, but it touches the same trader buying ranges. Exit with the scavenge yield curve and Bazaar.
**Problems:** memory 1 (texture_decoded_mb_est 3.0 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.49) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** depends on teiwaz.gtgtradercore -> SALVAGE_WRECKAGE_EVERYWHERE_1 (design only)
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Adjustments for Vanilla Textures Expanded - [NL] Facial Animation (`sd.fa.vteadjustments`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: none / functionality: texture-only: moves side-facing male eyebrows and a Hawk mouth for VTE Facial Animation / art: 47 textures, 0.2 MB disk, 71.7 MB est
**Why:** Placement tweak of someone else's art ("I made none of the art"); follows vanillaexpanded.vtexe.facialanims (list position 468) and the head-set audit.
**Problems:** memory 2 (texture_decoded_mb_est 71.7 MB (INFERRED header proxy, 47 textures)) · size 1 (disk_mb 0.16) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** depends on vanillaexpanded.vtexe.facialanims -> unfiled: FACIAL_ANIMATION_HEADSET_AUDIT_1
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Beard Adjustment (`kem.beardadjustment`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: none (3 patch ops on HeadTypeDefs) / functionality: XML only: scales the narrow-head beard to fit the normal head / art: 0.01 MB
**Why:** A tiny visual fix (0.01 MB, three patch ops) to a vanilla mismatch that we have no plan to build; passes trivially. Whether any campaign pawn wears the narrow-head beard is UNMEASURED.
**Problems:** memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy, 1 textures)) · size 1 (disk_mb 0.01) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** no dependants -> None
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### LEVIATHANS:SANDWORM (`chezhou.creature.sandworm`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: 10 defs: ThingDef 3, SoundDef 2, ClAssetLord 1, QuestScriptDef 1, SongDef 1, WeatherDef 1 / functionality: Harmony DLL (comp_tick, game/map component ticks, settings) on the closed ChezhouLib; a quest where a sandhammer summons a leviathan sandworm out of an anomalous sandstorm; Chinese-language description / art: 8 images, 38 MB in AssetBundles (decoded size not visible), 1.85 MB sounds
**Why:** Desert, a hunt, atmosphere: strong thematic fit. But we built our own: RUT_LongHunger (SANDWORM_MYTHOS_BUILD_1, closed; src/RimUtinni/LongHunger/Source) takes this mod as its architecture reference ("quest-gated encounter, summoning device, weather") and the item states its C# is original and did not read ChezhouLib. Two sandworms would also split the mythos. setting_physics.md still names it as the working reference, so it stays until that reference role ends. No source: ChezhouLib is described as Workshop-only closed code.
**Problems:** memory 1 (texture_decoded_mb_est 2.3 MB (INFERRED header proxy, 8 textures)) · size 2 (disk_mb 40.7) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 2 (dll_count 1, flags ['comp_tick', 'game_component_tick', 'harmony', 'map_component_tick', 'settings_screen'], static_ctors 0) · tps 1 (tick flags ['comp_tick', 'game_component_tick', 'map_component_tick']; per-mod TPS UNMEASURED) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** named as working reference in design/Jawa/worldbuilding/setting_physics.md Part 5; placed objects in the save UNMEASURED -> unfiled: CHEZHOU_SANDWORM_RETIRE_AFTER_LONGHUNGER_1
**Open:** Is the reference role finished now that RUT_LongHunger shipped and passed quicktest?
**Needs owner:** We built our own sandworm (the Long Hunger). Can the Chezhou Leviathans: Sandworm mod go now, or do you want it kept as a second, separate sandworm quest?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Big and Small - Enable All Optional Content (`redmattis.optional`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: none (def_total 0) / functionality: activates optional content in Big and Small - Genes & More (giant weapons, large meals, shrink rays) without needing the mods that normally trigger it / art: 2 images
**Why:** Our UtinniPatches/GiantWeaponWielders_Ashkarr.xml (owner ruling 2026-08-23) grants BS_GiantWeaponWielder to 16 Star Wars species and says the gene opens "all 23 giant weapons AND all 15 warcasket weapons", so those weapons have to exist; this mod is what enables that optional content (INFERRED: the 2026 gene-deps item found RSW defs never name its content directly, and it was deemed not required for RSW load). Dependant in the universe: none; dependants_ours: none. Keep while the giant-weapon rule stands.
**Problems:** memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy, 2 textures)) · size 1 (disk_mb 0.21) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** GiantWeaponWielders_Ashkarr.xml needs the giant weapons to exist (weapon register has 19 bigsmall rows) -> None
**Open:** Confirm in a quicktest that the 23 giant weapons are absent without this mod.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### [FSF] Complex Jobs (`frozensnowfox.complexjobs`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: 22 defs: WorkTypeDef 21, XmlExtensions.SettingsMenuDef 1 / functionality: XML only but 772 patch ops over 363 WorkGiverDefs, 226 ThingDefs, 136 alien-race defs, 31 GeneDefs, 14 ThinkTreeDefs; splits worktypes into finer ones / art: 2 images
**Why:** Owner-ruled KEEP and "declared resident" (STAT_NORM_WAVE3_RETIRE_1, mod_config_rulings.md): it changes work assignment, not work speed, and the stat-normalization audit measured 0 placed and save-clean. A crew of three to eight benefits from finer jobs. Costs to watch: 772 patch ops are a load-time cost (INFERRED), it must load last, and it is incompatible with CodeOptimist.JobSplitter, DarthSergeant.NurseJob and its own Legacy build (not in facts).
**Problems:** memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy, 2 textures)) · size 1 (disk_mb 1.38) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) · interaction 2 (patches 363 WorkGiverDefs and 226 ThingDefs across mods; load-last requirement) (U = unmeasured)
**Holds it in / exit:** owner ruling KEEP declared resident; our scavenge design adds a Salvaging work type in the same tab -> None
**Open:** Check our planned Salvaging WorkTypeDef against Complex Jobs' worktype rewrites before it ships.
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Facial Animation Compatability Project (`danzinagri.facialanimationcompatabilityproject`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: 0 own defs; 16 patch ops / functionality: Harmony DLL: Facial Animation heads in an anime style for many modded races, loaded per LoadFolders only when each race mod is active (Alpha Genes, Big and Small, VRE Phytokin/Saurid/Sanguophage/Lycanthrope, Keshig, and others) / art: 536 textures, 28.7 MB disk, 633.7 MB est before LoadFolders gating (INFERRED upper bound)
**Why:** The author states the goal is an "anime aesthetic" for races like Ratkin, which fights the matte natural-history art register (brief section 2, art lawset). It has no defs of its own (so no ParentName exposure), nothing depends on it, and its packs load only for race mods. Remaining risk is placed pawns of Alpha Genes/VRE races that already use its heads, a save question UNMEASURED.
**Problems:** memory 3 (texture_decoded_mb_est 633.7 MB (INFERRED header proxy, 536 textures)) · size 2 (disk_mb 28.67) · log_noise 1 (0 error occurrences / 0 distinct, chatter 1 in the 550-mod session) · complexity 2 (dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1) · tps U (per-mod TPS UNMEASURED; no tick flag in the DLL) · maintenance 2 (no source repo found (steam-only); supports 1.6 per About) (U = unmeasured)
**Holds it in / exit:** no dependants; only affects pawns of gated race mods -> None
**Open:** Which gated race mods are actually active in the list? Compute before removal.
**Needs owner:** This mod redraws heads in an anime style for many fantasy races. Remove it, or keep for those races?
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### RimThemes (`arandomkiwi.rimthemes`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/aRandomKiwi/RimThemes (github, GPL-3.0)
**Adds:** content: none (def_total 0) / functionality: two DLLs with Harmony, 65 static ctors and a settings screen: a UI theme engine with its own native background slot / art: 288 textures, 44.7 MB, plus 44 MB sounds and 177.7 MB other (themes)
**Why:** A hard dependency of our mandrake.rut.menushell (dependants_ours; MenuShell About.xml lists it as a dependency and loadAfter), whose Utinni Shell theme is the campaign's UI skin (UI_SHELL_SLICE_BUILD_1; ui_shell_spec.md). The theme-versus-VBE background conflict was resolved by using RimThemes' own background slot (RIMTHEMES_VBE_BACKGROUND_CONFLICT_1). GPL-3.0 source verified on GitHub, last push 2025-07-22. It is heavy on disk (286.7 MB) and in initialisation (65 static constructors), which is the cost of keeping it.
**Problems:** memory 2 (texture_decoded_mb_est 84.8 MB (INFERRED header proxy, 288 textures)) · size 3 (disk_mb 286.68) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 3 (dll_count 2, flags ['harmony', 'settings_screen'], static_ctors 65) · tps U (per-mod TPS UNMEASURED; no tick flag in the DLL) (U = unmeasured)
**Holds it in / exit:** mandrake.rut.menushell hard dependency; UI_SHELL_SLICE_BUILD_1 and the shell spec -> None
**Open:** A one-theme use may let us strip the other bundled themes later (size 286 MB).
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### SimpleStairs (Fork) (`rw.mod.simplestairs`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/rw-mod/SimpleStairs (github, None)
**Adds:** content: 10 ThingDefs: stairs, handrails, high walls, floor fences (standable stairs, impassable fences) / functionality: XML only 1.6 fork of gomi's SimpleStairs / art: 53 textures, 0.7 MB disk, 20.6 MB est
**Why:** Decorative multi-height-looking stairs and railings are cheap (XML only, 0.7 MB, 0 log errors) and can furnish a ship interior; no plan to build them ourselves. Incompatible with the original SimpleStairs, so do not add both. Verified GitHub repo (rw-mod/SimpleStairs, pushed 2025-07-16; licence unspecified).
**Problems:** memory 1 (texture_decoded_mb_est 20.6 MB (INFERRED header proxy, 53 textures)) · size 1 (disk_mb 0.72) · log_noise 0 (0 error occurrences / 0 distinct, chatter 0 in the 550-mod session) · complexity 1 (XML-only (dll_count 0)) (U = unmeasured)
**Holds it in / exit:** no dependants -> None
**Open:** none
<sub>facts: batch 14 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

