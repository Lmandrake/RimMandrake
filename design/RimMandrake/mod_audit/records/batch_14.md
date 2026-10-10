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

