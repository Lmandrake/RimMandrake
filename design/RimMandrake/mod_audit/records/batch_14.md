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

