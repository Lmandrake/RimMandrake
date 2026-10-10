# Mod audit batch 11: weapons_apparel

### [NL] Facial Animation - WIP (`nals.facialanimation`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 73 declared defs, mostly FacialAnimation.FaceAnimationDef 36 plus eye/lid/brow/head/mouth shape and type defs (defs_by_type) · functionality: animated faces (blink, wear/remove apparel, lovin, ingest, mine, downed...) driven by one DLL with Harmony, comp_tick and a settings screen (dll_flags); 5 static ctors · art: 1,238 textures, 6.35 MB on disk; 1,596.8 MB decoded estimate (INFERRED proxy)
**Why:** Framework for animated faces. Five mods in the universe depend on it (dependants: Head Set For FA / facial-animation compat, experimentals, reel.facialanims, sd.fa.geneticheadsframework, vanillaexpanded.vtexe.facialanims), and our own patch src/RimMandrake/MandrakePatches/Patches/HeadSetForFA_Revive.xml repairs a Head Set For FA static-constructor crash against it, so animated Jawa faces are something we already invested in. CLAUDE.md states cosmetic changes risk breaking the animated faces, so the owner treats them as live. Nothing replaces them in our plan. The cost is the memory proxy, not fit.
**Problems:** memory 3 (texture_decoded_mb_est 1596.8 (>250); proxy from PNG headers, not measured) · tps 2 (comp_tick FLAG on a per-pawn face comp; per-mod TPS UNMEASURED) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · complexity 3 (Harmony DLL, 5 static ctors, 5 dependants) · maintenance 3 (source_kind steam-only, redistribution prohibited in the description, title says WIP)
**Holds it in / exit:** 5 dependants incl. vanillaexpanded.vtexe.facialanims (dependants); our MandrakePatches HeadSetForFA_Revive.xml (8 refs, opened); mandrake patches-by-ours-refs 0; placed Things none (no ThingDefs) -> None
**Open:** Is 1.6 GB of decoded face texture real? The header proxy may count atlases that are never all resident; a live memory snapshot would settle it. · **Needs owner:** Is the 30 GB process budget worth animated faces for every pawn, or only for named Jawa founders?
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Astronomy Style Pack (`asp.halituisamaricanous`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 52 declared defs: ThingStyleDef 40, TerrainDef 5, plus a StyleCategoryDef and a ritual effect (defs_by_type) · functionality: XML only (dll_count 0); an Ideology style pack giving space-life themed weapons, armor and buildings · art: 138 textures, 13.3 MB on disk, ~52.6 MB decoded estimate; the description claims 103 unique sprites
**Why:** Pure cosmetic skin pack ('Inspired by midworld and argi-industrial art'). Nothing depends on it (dependants []) and nothing of ours references it (searched src with a sanity probe). It is art-only and the donor-art rulings (brief §2, §4 test 8) point away from keeping it. I do not choose ELIMINATE because fit is only neutral and I could not check whether the frozen Jawa ideoligion or any placed building uses one of its 40 styles (save placement UNMEASURED); an unreferenced ThingStyleDef is cheap to drop once that is checked.
**Problems:** memory 2 (texture_decoded_mb_est 52.6 (50-250)) · interaction 1 (patches 12 vanilla ThingDefs only (patches_mods ludeon.rimworld 12), patched_by none) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · maintenance 3 (steam-only, no source link found)
**Holds it in / exit:** Ideoligion/placed-Thing references in the campaign save: UNMEASURED -> unfiled: ASTRONOMY_STYLE_PACK_SAVE_CHECK_THEN_DROP_1
**Open:** Does any ideoligion in the save select the Astronomy style category?
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### BestApparel (`io.github.relvl.rimworld.bestapparel`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/Relvl/Rimworld_BestApparel (github, None)
**Adds:** content: 10 UI defs (ToolbarButtonDef 5, ThingTabDef 4, MainButtonDef 1) · functionality: a main-button window to search apparel by layer, slot and stat and sort it · art: 2 images, 0.2 MB
**Why:** Small UI tool the owner can use for gear comparison; it cannot affect the world (no patches, no thing defs). It passes the ceiling test trivially (brief §4 test 4) and costs 0.62 MB and zero log lines. Nothing of ours depends on it; it is kept because it supplies a UI we have no plan to build.
**Problems:** log_noise 0 (log_error_occurrences 0 in the 550-mod session) · size 1 (disk_mb 0.62) · maintenance 1 (github, last push 2025-07-11, not archived, supports 1.6)
**Holds it in / exit:** supplies a UI nothing of ours replaces -> None
**Open:** none
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Destiny Exotic Weapons (`milkwater.destinymod`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: 59 declared defs: 25 ThingDefs (9 exotic weapons), 15 SoundDefs, 9 FleckDefs, 8 HediffDefs, a StatDef and a WorkGiver · functionality: nine weapons from the Destiny game, each with a unique power, plus 'a new method to acquire them'; one DLL with a MapComponent tick FLAG · art: 33 textures, 6.1 MB, ~25.5 MB decoded estimate
**Why:** Third-party game IP (Destiny) with named unique-power weapons: off-genre for a Star-Wars-style scavenger setting (brief §4 test 3) and an arms-race shape, since each exotic is a hand-made power spike and the pillars forbid stat inflation (brief §1 pillars). Retirement cost checked: dependants [] and dependants_ours [], patched_by [], no xpath from src targets it, and our Armoury lists it only in an optional loadAfter (src/RimStarWars/Armoury/About/About.xml line 134), which is harmless when absent. Not checked: placed exotics in the save, and a MapComponent tick it adds that could not be attributed to a number.
**Problems:** interaction 1 (patches no defs; Armoury lists it as loadAfter only) · tps 1 (map_component_tick FLAG, small content (25 ThingDefs)) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · maintenance 3 (steam-only, no source)
**Holds it in / exit:** nothing depends on it; Armoury loadAfter is optional -> None
**Open:** Placed Destiny exotics in the save: UNMEASURED. · **Needs owner:** Do you want any Destiny-style exotics as unique one-of-a-kind weapons, or should the mod go entirely?
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Dub's Paint Shop (`dubwise.dubspaintshop`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** https://github.com/Dubwise56/Dubs-Paint-Shop (github, None)
**Adds:** content: 18 defs: DesignationDef 4, JobDef 4, WorkGiverDef 3, ThingDef 2, key bindings · functionality: painting tools that recolour stuffed/colourable buildings, apparel and terrain; two DLLs, Harmony, settings screen; 4 static ctors · art: 25 textures, 10.7 MB on disk, 1.6 MB decoded
**Why:** Cosmetic colouring tool with a github source (pushed 2026-09-18, not archived) and no clash with our mods: patches_ours_refs 0, patched_by_ours_refs 0, and the only other mod touching it is complexjobs (3 edges). Colouring is cosmetic so it passes the ceiling test trivially (brief §4 test 4). We have no plan to build a paint system, so it stays.
**Problems:** complexity 2 (two DLLs with Harmony, 4 static ctors) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · size 1 (disk_mb 10.73) · maintenance 1 (github pushed 2026-09-18)
**Holds it in / exit:** supplies a recolour tool we do not plan to build -> None
**Open:** Colour-by-material rulings (memory: colour with material, not paint) concern dev paint; unclear if player paint conflicts.
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Ion Weaponry (Continued) (`zal.ionweaponry`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: 34 declared defs: 15 ThingDefs (IW_Gun_* ion pistol/PDW/slugthrower/rifle/DMR/LMG, heavy ion lance), 15 SoundDefs, a DamageDef, a HediffDef, an AbilityDef, a ResearchProject · functionality: spacer ion weapons trading raw damage for short cooldowns and armor penetration, with an EMP-explosion passive; one DLL (Athena code integrated), no Harmony flag · art: 13 textures, 1.15 MB, ~7.3 MB decoded
**Why:** Our own work leans on it: mandrake.rsw.patches references its defs 21 times (patched_by) and src/RimMandrake/Utils/weapon_tag_audit.py EXTRA_TAGS tags IW_Gun_IonPistol/PDW/Slugthrower/Rifle/DMR/LMG/HeavyIonLance as Jawa_IonWeapon because the ion blaster is the one thing Jawas canonically manufacture and the Trade Moot grunt is built around it. We also ship our own ion armament, mandrake.rsw.ionweapons (JawaIonWeapons), so the exit is to absorb these guns into it (the description grants CC BY 4.0 reuse with credit). Fit is resonant.
**Problems:** interaction 2 (patched_by_ours_refs 21) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · complexity 2 (one DLL, no Harmony) · maintenance 3 (steam-only continuation of Elseud's mod; no repo link found)
**Holds it in / exit:** mandrake.rsw.patches: 21 xpath refs (WeaponTags_Renormalise.xml); weapon_tag_audit.py EXTRA_TAGS names 7 IW_ defs; placed ion weapons in the save: UNMEASURED -> WEAPONS_DONOR_RETIREMENT_1 (existing); remaining step: unfiled: ION_WEAPONRY_ABSORB_INTO_JAWAIONWEAPONS_1
**Open:** Does mandrake.rsw.ionweapons already cover the same seven guns, or only a lower tier?
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Jewelry (`kikohi.jewelry`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/vbardales/Rimworld-Precious-Stones-And-Jewelry-Enhanced (github-search, other)
**Adds:** content: 35 defs: 15 ThingDefs (necklace, ring, bracelet, earrings, laser sculpting table), 8 recipes, 3 terrains, 2 research projects, ApparelLayer, BodyPartGroup · functionality: stuffable jewelry apparel (gold, stone, jade plus added diamond, sapphire, ruby) and a faster sculpting bench; Harmony DLL with a settings screen, 28 patch ops into Royalty titles, PawnKinds, traders, factions · art: 41 textures, 0.61 MB, ~5.5 MB decoded
**Why:** Our ResearchRetag already retags its research (mandrake.rut.researchretag: 15 edges; kikohi.jewelry is in its About.xml list), so it is part of the tuned research tree. Adds trade and loot flavour (jewelry from salvage and wealth objects) which fits a scavenger economy and does not raise the combat ceiling. Source link is only a name-search hit and needs confirming.
**Problems:** interaction 2 (patched_by_ours_refs 15; it patches Royalty titles/PawnKinds/traders (28 ops)) · complexity 2 (one Harmony DLL) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · maintenance 2 (source_kind github-search is a name match (vbardales/...Jewelry-Enhanced); unverified that it is this mod)
**Holds it in / exit:** mandrake.rut.researchretag: 15 patched_by refs and an About.xml entry; jewelry on pawns/in stockpiles: UNMEASURED -> None
**Open:** Confirm the github repo is the Kikohi/Sarg Jewelry mod.
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Slave Outfits [1.6] (`usgiyi.slaveoutfits`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** none (steam-only, None)
**Adds:** content: 12 apparel ThingDefs · functionality: XML only; uniforms for slaves and prisoners (spacer suit with vacuum resistance since 1.7.3) · art: 145 textures, 3.8 MB, ~44.6 MB decoded estimate
**Why:** Directly on-theme for the clan: the earlier audit noted the enslave-not-recruit doctrine (prior_note_2026_08_30), and the mod costs 3.84 MB, no code, no patches in or out, zero log errors. We have no own prisoner or slave garb planned in the facts I could find. If the owner extends the no-donor-art ruling to third-party apparel packs, this becomes a phase-out; that is his call.
**Problems:** memory 1 (texture_decoded_mb_est 44.6 (<50)) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · maintenance 3 (steam-only)
**Holds it in / exit:** no ours references; nothing else touches it -> None
**Open:** Does the 'no donor art kept' ruling reach third-party apparel used only for function? · **Needs owner:** Does 'no donor art is kept' apply to apparel packs like Slave Outfits that we use for function, or only to creature and biome art?
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Stronger Quality Scaling (1.6) (`kas.strongerscaling`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 23 StatDefs (def_total 23) that redeclare vanilla stats such as ArmorRating_Sharp/Blunt/Heat, Insulation_Cold/Heat and StuffEffectMultiplier* (opened its Defs folder) · functionality: XML only; makes apparel, armor, weapon and building stats vary much more with quality · art: 1 texture
**Why:** It rewrites vanilla stat definitions globally, so every armor rating and weapon stat in the game shifts with quality; that pulls against the no-arms-race pillar (brief §1: qualitative danger, never stat inflation) and widens the gap between crafted gear tiers. The 15 mods listed in patched_by (incl. mandrake.rm.biomes 5, lee.theforce.lightsaber 10) are edges on the SAME vanilla stat defNames, so they show our numbers sit on top of this override, not that they patch the mod (INFERRED). Our armour retune (Armoury gen_armour_patch.py) was calibrated against the live stack; I could not tell whether that included this mod, so I keep it until that is checked, with the exit being an owner ruling on quality scaling.
**Problems:** interaction 2 (patched_by_ours_refs 6 on shared vanilla stat defNames) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · complexity 1 (XML only) · maintenance 3 (steam-only)
**Holds it in / exit:** our armor and weapon numbers sit on the same stat defNames; calibration baseline UNMEASURED; qualities already on saved gear: UNMEASURED -> unfiled: QUALITY_SCALING_OWNER_RULING_1
**Open:** Was the armor/weapon calibration done with this mod active (gen_armour_patch/weapon register asserts AP values; check its freshness stamp against FULL.LATEST)? · **Needs owner:** Should masterwork gear be a much bigger step up than normal gear (this mod), or stay at vanilla spacing?
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### WASDed Pawn (`addvans.wasdedpawn`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 10 defs: 8 KeyBindingDefs, 1 hediff (arm exhaustion), 1 category · functionality: WASD direct control of one drafted pawn with mouse aim; sprint/walk; Vanilla and Arcade modes; Harmony DLL with a game-component tick FLAG · art: 7 textures, 0.19 MB
**Why:** Pure player-input mod: no patches in or out, 0.19 MB, zero log errors, no content to retire. It is a play-style toy the owner may enjoy; it adds no progression and does not touch the ship loop. Source is a Discord link only, so maintenance is the risk, not fit.
**Problems:** tps 1 (game_component_tick FLAG, tiny mod) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · maintenance 3 (no source repo; about_url is a Discord invite)
**Holds it in / exit:** supplies direct control we do not plan to build -> None
**Open:** Prior audit said 'examine'; this is now examined.
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Weapon Racks (`aelanna.weaponracks`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/MarvinLira/RimWorld-WeaponRacks-de (github-search, gpl-3.0)
**Adds:** content: 13 defs: 4 ThingDefs (decorative weapon racks) and 9 WeaponAdjustmentDefs that position each weapon's draw · functionality: racks that display stored weapons; Harmony DLL with settings screen; 3 static ctors · art: 17 textures, 0.99 MB
**Why:** Small decorative storage that draws the weapons in it. Four other mods patch its defs (sihv.rombonesport 6, VFE Core 5, VEE 3, VFE Tribals 2) and nothing of ours conflicts (patches_ours_refs 0, patched_by_ours_refs 0). Capacity is bounded by the rack, so it is not the infinite-storage class the brief excludes.
**Problems:** complexity 2 (one Harmony DLL, 3 static ctors) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · maintenance 2 (github-search hit is a German fork (MarvinLira ...-de) last pushed 2022-09-13; not proof it is the upstream)
**Holds it in / exit:** displays salvage weapons; no ours dependency -> None
**Open:** Source link is a name-search match to a 2022 fork; confirm upstream.
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### WeaponStats (`bodlosh.weaponstats`)
**Verdict:** KEEP (MEASURED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (ships-source, None)
**Adds:** content: 1 MainButtonDef · functionality: a Weapons tab listing ranged, melee and explosive weapons and apparel with stats; one DLL, no flags · art: 40 textures, 0.99 MB
**Why:** Read-only information tab that ships its C# source (ships_source MEASURED). Useful to the owner when judging the weapon register; no patches, no ticks, no log lines. Passes the ceiling test trivially.
**Problems:** log_noise 0 (log_error_occurrences 0 in the 550-mod session) · complexity 2 (one DLL, no Harmony) · maintenance 2 (source ships in the folder but no repo URL or push date)
**Holds it in / exit:** supplies a UI nothing of ours replaces -> None
**Open:** none
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### Yayo's Combat 3 (Continued) (`mlie.yayoscombat3`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/emipa606/YayosCombat3 (github, MIT)
**Adds:** content: 40 defs: 18 RecipeDefs (ammo), 13 ThingDefs, 5 ApparelLayerDefs, a JobDef · functionality: rewrites combat: all ranged weapons consume ammunition, loadout, new armor algorithm where penetration matters, plus a 3-patch tweak of vanilla ThingDefs; Harmony, comp_tick, settings screen, 2 DLLs · art: 15 textures, ~1.8 MB decoded
**Why:** Load-bearing for our weapon numbers: src/RimMandrake/Utils/gen_weapon_register.py states Bullet_AssaultRifle.armorPenetrationBase 0.19 comes from this mod's patch_weapon.xml and its calibration FAILS on vanilla's 0.165, so every ranged AP figure in our register assumes it. The Armoury About.xml also lists it in loadAfter. Ammo consumption is resonant with the scarcity pillar. This is a combat-system overhaul in the same family as the excluded Combat Extended (brief §2), so it is a card item: the exclusion and this dependency disagree.
**Problems:** tps 2 (comp_tick FLAG with Harmony on every ranged weapon; per-mod TPS UNMEASURED) · interaction 2 (our calibration and Armoury patches assume its values; patched_by sihv.rombonesport 8) · log_noise 1 (log_chatter_lines 2, no errors) · complexity 3 (Harmony, 2 DLLs, settings screen) · maintenance 1 (github emipa606/YayosCombat3, MIT, pushed 2026-06-02)
**Holds it in / exit:** gen_weapon_register.py asserts its AP 0.19 (opened); Armoury About.xml loadAfter (line 138); incompatible_with Solaris.SYS (not in this batch's universe check) -> None
**Open:** Is the brief's Combat Extended exclusion meant to cover this mod, given our weapon register already depends on its numbers? · **Needs owner:** Is Yayo's Combat 3 (ammo for every ranged weapon, penetration-based armor) wanted as part of the game, given Combat Extended was excluded?
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### More Utility Packs (Continued) (`zal.moreutilitypacks`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, None)
**Adds:** content: 21 defs: 11 ThingDefs (utility belt packs), 7 HediffDefs, 2 ThoughtDefs, a research project · functionality: XML only; eight craftable and several quest-reward utility belts giving focused bonuses (manipulation/aim, medical support, etc.); requires VFE Core and VAE Accessories · art: 171 textures, 1.5 MB, ~46.5 MB decoded
**Why:** Our ResearchRetag patches its research (mandrake.rut.researchretag 8 edges; zal.moreutilitypacks is in its About.xml), so it is already part of the tuned tech tree. The packs are exclusive-choice bonuses ('tough choice'), not a ladder, which sits better with the pillars than most gear mods. Hard-depends on VFE Core and VAE Accessories, which are kept anyway.
**Problems:** interaction 2 (patched_by_ours_refs 8) · memory 1 (texture_decoded_mb_est 46.5) · log_noise 0 (log_error_occurrences 0 in the 550-mod session) · maintenance 3 (steam-only continuation)
**Holds it in / exit:** mandrake.rut.researchretag: 8 refs and About.xml entry; placed/worn packs: UNMEASURED -> None
**Open:** none
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

### RimTek DigiPal (`deon.rimtek.digipal`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** none (steam-only, None)
**Adds:** content: 4 defs: a belt ThingDef, a JobDef, a JoyGiverDef, a ThoughtDef · functionality: a belt with a personal computer that raises melee and ranged accuracy and lets the wearer play games for recreation; XML only; requires Deon.rimtek.core · art: 2 textures, 0.09 MB
**Why:** A modern consumer gadget (a game-playing PC belt) is off-tone for a Star-Wars-style frontier (brief §4 test 3: modern-corporate brands dissonant) and gives a flat accuracy bonus. It is tiny (4 defs) so retirement is cheap: dependants [], dependants_ours [], patches in and out 0, only a JoyGiver/Thought it declares itself. Only one hold-out: whether any belt is worn in the save (UNMEASURED); the belt is lootable only if a loot table names it, which the facts do not show.
**Problems:** log_noise 0 (log_error_occurrences 0 in the 550-mod session) · maintenance 3 (steam-only; framework Deon.rimtek.core is a hard dependency)
**Holds it in / exit:** nothing depends on it; placed belts UNMEASURED -> None
**Open:** Deon.rimtek.core stays unless its other dependants are also retired; that belongs to the framework batch.
<sub>facts: batch 11 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 2026-10-10</sub>

