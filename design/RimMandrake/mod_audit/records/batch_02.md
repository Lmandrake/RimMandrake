# Mod audit record: batch 02 (code_tweaks_qol_ui_1)

Assessor: Sonnet 5.5, stage 1. Template per RUBRIC.md section 7.

### Better Stacktraces (`aleksey.betterstacktraces`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no license seen)
**Adds:** content: none (def_total 0); functionality: Harmony patch (1 DLL) that improves stack traces written to Player.log; description: "improve the game's stacktraces in the log"; art: one 0.03 MB icon
**Why:** Pure diagnostics: it makes the log readable, which the owner's debug process (CLAUDE.md "How we debug": every mod debugged through its script and Player.log) depends on. No gameplay effect, so it passes the 7-question test trivially (brief §4 test 4). It loads at position 4 (full_latest_position) by design. Nothing of ours depends on it (dependants_ours empty), so this is KEEP on supply, not dependency: no plan exists to build our own log tooling.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 3 no source link found (source_kind steam-only); cannot patch if 1.7 breaks it · complexity 2 dll_count 1, flags ['harmony'], static_ctors 0 · memory 1 texture_decoded_mb_est 1.2 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.04
**Holds it in / exit:** nothing depends on it; kept for log quality -> none
**Open:** Whether a shipped player list should carry dev-only mods depends on the unresolved audience question (SCENARIO_BRIEF §5.1); not resolved here.
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Cherry Picker (`owlchemist.cherrypicker`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/Owlchemist/cherry-picker (github, MIT)
**Adds:** content: none (def_total 0); functionality: Lets a mod list pseudo-remove defs from other mods (references cut, defs kept) via Harmony; a settings screen is the editor; art: one 0.04 MB icon
**Why:** It is the curation instrument the scenario is built on: brief §1 pillars say curation is "by Cherry Picker trimming, not uninstalling", and §3 lists "keep the mod, cut the content" as a legitimate verdict shape. Our tooling hard-codes it: src/RimMandrake/Utils/preload_check.py has HARD_RULES (Cherry Picker must precede oskarpotocki.vanillafactionsexpanded.core) and CHERRYPICKER_MAX_INDEX = 40, and design/Jawa/fauna/gen_cast_patch.py references it. The brief names Vanilla Genetics Expanded and VFE-Insectoids 2 as "cherry-pick the engine, keep the creatures" cases, which need it.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 3 last push 2023-05-30 (> 3 years); MIT; still lists 1.6 support · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 2 · memory 1 texture_decoded_mb_est 0.8 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.31 · interaction 1 patches no defs (patches_ours_refs 0); its power is its config, which is outside the facts
**Holds it in / exit:** preload_check.py HARD_RULES and CHERRYPICKER_MAX_INDEX=40; the brief's curation strategy (pillars); every Cherry Picker cut file in the live config -> none
**Open:** Upstream is stale (no push since 2023-05) yet works on 1.6 in the measured session; a checker could confirm via Player.log that cut keys resolve (preload_check check 5 reads the keys).
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### [JM]Disable Pseudo Translate 禁用泰南语 (`jm.disstynan`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no license seen)
**Adds:** content: none (def_total 0); functionality: Harmony patch that disables the pseudo-translation garble ("Thean" gibberish) shown in developer mode for untranslated strings; art: one 0.02 MB icon
**Why:** Developer-mode readability fix only. Zero defs, 1 static ctor, no log errors; it touches nothing a player sees. KEEP on supply for the owner's own debugging sessions (CLAUDE.md "How we debug"). No plan to replace it; the cost of keeping is negligible.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 3 no source link found (source_kind steam-only); cannot patch if 1.7 breaks it · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · memory 1 texture_decoded_mb_est 1.2 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.07
**Holds it in / exit:** nothing depends on it; kept for dev-mode readability -> none
**Open:** Dev-only: a shipped player list would not need it (audience question SCENARIO_BRIEF §5.1).
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### [KV] Call Trade Ships (Continued) (`zal.calltradeships`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (ships-source, no license seen)
**Adds:** content: 1 JobDef; no creatures or items; functionality: Adds a comms-console/menu action to summon orbital trade ships on demand (the KiameV original), with settings to toggle which traders can be called and whether ships land or stay in orbit; C# source ships in the folder (6 .cs); art: 5 small textures (0.66 MB)
**Why:** Calling a trader on demand fits a ship-centred, keep-moving loop (brief §1 "decide what to leave behind", the Hutt ledger as a pressure) and costs nothing in progression terms beyond vanilla orbital trade. It has no dependants and none of our mods reference it, so this is KEEP on supply with an open interaction question: calling traders at will could blunt the scarcity pressure the brief builds around trade (Bazaar haggle window, memory bazaar-trade-window-ruled).
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 2 C# ships in the folder (6 cs, csproj) but no upstream link; description credits a chain of re-uploads (KiameV -> Cavenaugh -> Wecardo) · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 0 · memory 1 texture_decoded_mb_est 3.1 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.73 · interaction 1 patch_ops_all 0; adds a JobDef only
**Holds it in / exit:** supplies on-demand trade; nothing of ours depends on it -> none
**Open:** Does on-demand trader summoning undercut the Bazaar trade-window design and the Hutt-ledger trade cadence? If so, gate or drop it.; NEEDS OWNER: Should the player be able to call trade ships whenever they want, or should trade only arrive on the story's schedule (Hutt ledger, Bazaar)?
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### [LC] Selectable Sculpture Graphic (`lc.tammybee.selectablesculpturegraphic`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (ships-source, no license seen)
**Adds:** content: none of its own (def_total 0); 50 patch ops adding one comp to sculpture/statue ThingDefs (Odyssey 16, Core 11, Biotech 4, Ideology 2, Anomaly 1); functionality: Harmony mod adding a gizmo to choose which graphic a sculpture displays; C# source ships (6 .cs, sln); art: 1 icon texture; the 85 assembly files (25.9 MB) are per-version DLL copies, not art
**Why:** Our own statue design depends on it: design/RimMandrake/statue_expansion_assessment.md (lines 12-15, 60-63) rules "patch into LC, don't fork it": our statue defs get its CompSculpture added by a PatchOperationFindMod-gated patch, with our art shipped as a Graphic_Random pool. That is a planned dependency (not yet built; src/ has no reference), so what holds it in is a design doc, not code. It supplies manual variant selection we have no plan to build ourselves (the assessment explicitly chose not to).
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · size 2 disk_mb 26.79, of which assemblies 25.92 MB across 85 files (version copies) · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · memory 1 texture_decoded_mb_est 1.2 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · maintenance 2 C# ships inside the mod folder but no upstream repo link seen; patchable locally, no verified upstream · interaction 2 50 xpath ops over vanilla/DLC sculpture defs; no edge into our mods yet (patches_ours_refs 0)
**Holds it in / exit:** design/RimMandrake/statue_expansion_assessment.md and statue_mods_spec.md (planned compat patch, not built) -> unfiled: STATUE_SCULPTURE_COMPAT_PATCH_1 (if the assessment is acted on)
**Open:** Confirm the compat patch exists before anyone retires it; license is mixed (CC BY-NC-SA / MIT per description).
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### [RH2] CPERS: Arrest Here! (`rh2.cpers.arrest.here`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/chickenforcer/-RH2-CPERS---Arrest-Here (github, no license seen)
**Adds:** content: 1 JobDef, 1 SoundDef; functionality: Harmony mod: arrest a downed pawn on the spot without a prison room; C# source ships (25 .cs, 5 csproj, .git folder); art: 2 small textures, 1 sound
**Why:** Pure QoL for a scavenger crew that captures downed raiders in the field (brief §1 Jawa as salvagers and captors, Hutt ledger people-trade). It raises no ceiling (§4 test 4) and nothing of ours depends on or conflicts with it (patched_by empty). KEEP on supply; the repo link in the facts is INFERRED from a git folder and should be confirmed.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 2 repo https://github.com/chickenforcer/-RH2-CPERS---Arrest-Here, last push None (name-search match, unverified) · complexity 2 dll_count 1, flags ['harmony'], static_ctors 1 · memory 1 texture_decoded_mb_est 1.1 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 4.76
**Holds it in / exit:** supplies arrest-without-room; nothing depends on it -> none
**Open:** source_url is INFERRED (chickenforcer repo); verify before relying on it.
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### [SYR] More Slaves (Continued) (`mlie.syrmoreslaves`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/SYRMoreSlaves (github, MIT)
**Adds:** content: no defs of its own; 3 patch ops (jm.bettertraders 2, Core 2); functionality: Increases the number of slaves offered by slave-carrying traders and bases; settings screen; XML plus two small DLLs (no Harmony); art: 2 small icon textures
**Why:** Slave trade fits the Hutt-ledger setting (brief §1) and the mod is tiny and XML-driven, with a verified MIT repo (emipa606/SYRMoreSlaves, pushed 2025-08-22). The tension is arithmetic: the pillars fix the crew at about 3-8 and tie scale to the ship, and more purchasable slaves is a labour-supply lever (brief §2 anti-exponential). No ruling covers it, so KEEP is the conservative verdict until the owner answers the question below.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 1 repo https://github.com/emipa606/SYRMoreSlaves, last push 2025-08-22T18:57:35Z · complexity 1 dll_count 2, flags ['settings_screen'], static_ctors 0 · memory 1 texture_decoded_mb_est 1.4 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.15 · interaction 1 patches Core and jm.bettertraders only
**Holds it in / exit:** supplies larger slave stock at traders; nothing of ours depends on it -> none
**Open:** SCENARIO_BRIEF §2 pillars: does buying more slaves bypass the fixed-crew scarcity? No ruling found.; NEEDS OWNER: The crew is meant to stay small (3-8). Should traders be allowed to sell you extra slaves in larger numbers, or should slave stock stay at the vanilla level?
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Allow Dead Animals (`andrewraphaellukasik.allowdeadanimals`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/andrew-raphael-lukasik/rimworld-mod_allow-dead-animals (github, no license seen)
**Adds:** content: none (def_total 0); 131 xml files under its folder tree are translation/keyed data; functionality: Auto-allows (un-forbids) animal corpses so they are hauled/butchered; a map-component tick checks corpses; settings screen; source on GitHub; art: 1 icon
**Why:** Direct resonance: the brief's scavenger crew steals meals from wild predators' kills, and the mod's own description targets exactly that. Design/Jawa/mods/stat_normalization_audit classed it as designation QoL with no gameplay number. The only cost is a map-component tick (dll_flags map_component_tick), small for a corpse-allow check. No dependants, no overlap with our mods found in src/.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps 1 tick FLAGs ['map_component_tick'] (a corpse scan per interval); per-mod TPS UNMEASURED · maintenance 1 repo https://github.com/andrew-raphael-lukasik/rimworld-mod_allow-dead-animals, last push 2025-07-19T10:34:08Z · complexity 1 dll_count 1, flags ['map_component_tick', 'settings_screen'], static_ctors 0 · memory 1 texture_decoded_mb_est 1.2 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.19
**Holds it in / exit:** supplies auto-allow of corpses; nothing depends on it -> none
**Open:** none
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Almost There! Fork (`duz.almosttherefork`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/duztamva/Almost-There-Fork-1.5- (github-search, no license seen)
**Adds:** content: none (def_total 0); 3 patch ops (Core 3, VehicleFramework 1); functionality: Harmony mod adding a caravan switch: do not rest when within x hours of the goal, or never rest; art: 4 UI icons (0.46 MB)
**Why:** The campaign is an expedition crossing an unexplored world (brief §1), so caravans are plausible even though the colony lives aboard; the mod only changes resting behaviour and raises no ceiling. It carries a patch into smashphil.vehicleframework (1 op), a framework not in this audit's scope, so the interaction is benign unless that framework is removed. Repo link is a name-search match (INFERRED).
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 2 repo https://github.com/duztamva/Almost-There-Fork-1.5-, last push 2025-11-27T05:50:01Z (name-search match, unverified) · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · memory 1 texture_decoded_mb_est 2.9 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.52 · interaction 1 patches Core and VehicleFramework only
**Holds it in / exit:** supplies caravan rest toggles; nothing depends on it -> none
**Open:** Confirm whether caravans are used at all given the ship-centred loop; if never, this is dead weight but harmless.
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Ambient Rim (`swablu.ambience`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/foran7/Rimworld-Ambient-Rim-1.4 (github-search, no license seen)
**Adds:** content: 8 SoundDefs; functionality: Harmony mod that aggregates sustainers into environmental ambient loops; map-component tick; settings screen; art: 5.3 MB of sound files (37 files) plus one icon
**Why:** Our own ambient layer is designed to replace it: design/RimMandrake/atmospheric_base_hook_ecosystem.md (line 497) names Ambient Rim "the closest thing to a direct competitor for the bed layer", lists four ambient mods coexisting audibly as an open test (question F), and ATMOSPHERIC_BASE_BUILD_PROGRAM_1 is the build item. design/RimMandrake/music_protocol.md (line 43) records it as ambience, not music. While AtmosphericBase is unbuilt it supplies ambience we do not yet have; once built, two beds beat against each other unless one ducks.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps 1 tick FLAGs ['map_component_tick']; per-mod TPS UNMEASURED · maintenance 3 last push 2024-03-31 for a repo named for 1.4 (name-search match), i.e. > 2 years and unverified · complexity 2 dll_count 1, flags ['harmony', 'map_component_tick', 'settings_screen'], static_ctors 1 · memory 1 texture_decoded_mb_est 1.9 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 5.53 · interaction 2 competes with our planned AtmosphericBase bed layer and other ambience mods (neronix17.outerrim.core, dorbo.watersfx); no xpath edge
**Holds it in / exit:** no ambient bed layer of ours exists yet (ATMOSPHERIC_BASE_BUILD_PROGRAM_1 is the build); no mod depends on it -> ATMOSPHERIC_BASE_BUILD_PROGRAM_1
**Open:** Does donor audio fall under the no-donor-art ruling (brief §2 names art only)? Not ruled.; NEEDS OWNER: Our own ambient sound system is planned. Should this donor ambience mod be dropped once ours exists, or is donor sound allowed to stay (the no-donor-art rule mentions art only)?
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Auto links (`automatic.autolinks`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (ships-source, no license seen)
**Adds:** content: none (def_total 0); functionality: Harmony mod (2 DLLs, source in folder) that auto-inserts hyperlinks into def descriptions so one can click through to related defs; 0.83 MB of XML data; art: one small icon
**Why:** UI convenience over 550 mods' worth of descriptions; no gameplay effect, so it passes the 7-question test trivially (brief §4 test 4). Description parsing happens at load or on display, but no tick FLAG exists; its load cost is UNMEASURED. Nothing of ours references it.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; may cost load time over every def description (unmeasured); per-mod TPS UNMEASURED · maintenance 2 C# ships inside the mod folder but no upstream repo link seen; patchable locally, no verified upstream · complexity 2 dll_count 2, flags ['harmony'], static_ctors 1 · memory 1 texture_decoded_mb_est 0.8 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 4.46
**Holds it in / exit:** nothing depends on it -> none
**Open:** Our own mods' descriptions will be auto-linked; the player may see links to donor defs we mean to retire. Cosmetic only.
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Auto Strip on Haul (`fuu.autostriponhaul`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/tenguin/Rimworld_AutoStripOnHaul (github, MIT)
**Adds:** content: none (def_total 0); 3 patch ops on Core; functionality: Haulers automatically strip corpses of weapons, apparel and inventory; tainted apparel can be forbidden, left or destroyed; settings screen; art: 2 small icons
**Why:** Its own description says "ideal for scavenger or cannibal colonies", and the brief's Jawa are salvagers (§1). It was once a named suspect in BRIDGE_INVENTORY_TRANSFER_REFUSES_ALL_1 (closed item, line 82: culprit never identified, static search abandoned), so there is no measured case against it. Verified MIT repo (tenguin/Rimworld_AutoStripOnHaul), pushed 2025-03-09.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 1 repo https://github.com/tenguin/Rimworld_AutoStripOnHaul, last push 2025-03-09T22:11:29Z · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 0 · memory 1 texture_decoded_mb_est 2.2 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.86 · interaction 1 patches Core only
**Holds it in / exit:** nothing depends on it -> none
**Open:** The closed inventory-transfer item never cleared or convicted this mod; a checker could run the transfer test with it off if the problem recurs.
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Better Ambushes Continued (`ionfrigate12345.coolandgoodambush`)
**Verdict:** KEEP (UNVERIFIED) · **Fit:** neutral · **Source:** https://github.com/Ionfrigate12345/RimworldBetterAmbushesContinued (github-search, no license seen)
**Adds:** content: none (def_total 0); functionality: Harmony mod: a slider that enlarges ambush encounters by a multiple, plus an option to flee an ambush after a set time; world-component tick; 5 static ctors; art: one 0.14 MB icon
**Why:** Thematically fine (ambush is an expedition hazard) but it is a quantitative lever: the pillars say danger must be qualitative, "never stat inflation" (brief §1 pillars, §2 no arms race). Whether it hurts depends on the configured multiplier, which is not in the facts. Default behaviour is UNVERIFIED, so the conservative verdict is KEEP with a question rather than ELIMINATE.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps 1 tick FLAGs ['world_component_tick']; per-mod TPS UNMEASURED · maintenance 2 repo https://github.com/Ionfrigate12345/RimworldBetterAmbushesContinued, last push 2026-08-05T18:18:44Z (name-search match, unverified) · complexity 2 dll_count 2, flags ['harmony', 'settings_screen', 'world_component_tick'], static_ctors 5 · memory 1 texture_decoded_mb_est 0 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.24
**Holds it in / exit:** nothing depends on it -> none
**Open:** What multiplier is configured in the live ModSettings? 1.0 makes it inert; higher is numeric danger inflation.; NEEDS OWNER: This mod scales ambushes bigger by a slider. The scenario wants danger to be qualitative, not just bigger numbers. Do you want ambush size left at normal, or is bigger ambush acceptable here?
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Better Beggars (Continued) (`mlie.betterbeggars`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/BetterBeggars (github, GPL-3.0)
**Adds:** content: 4 QuestScriptDefs and 3 IncidentDefs (beggar quests and incidents, cloned from the vanilla beggar root per skills/rimworld-quests/references/mod_patterns.md); functionality: XML plus two DLLs, settings screen; Ideology is a declared dependency; art: 2 small textures
**Why:** Self-contained quest pack: a beggar asks for help and the response is rewarded or punished. It requires Ideology (hard prerequisite of shipping per CLAUDE.md, so no problem). Nothing of ours patches it and it has no dependants. Fit is neutral: beggars are generic frontier flavour, not specific to a Jawa crew, and quest rewards can be a ceiling lever, but vanilla beggars share that shape.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 1 repo https://github.com/emipa606/BetterBeggars, last push 2026-06-02T20:27:49Z · complexity 1 dll_count 2, flags ['settings_screen'], static_ctors 1 · memory 1 texture_decoded_mb_est 1.4 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.44
**Holds it in / exit:** supplies beggar quests; nothing of ours depends on it -> none
**Open:** GPL-3.0 licensed; matters only if we ever absorb code.
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Better Growth Moments (`arkymn.bettergrowthmoments`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# source inside the mod folder) (ships-source, no license seen)
**Adds:** content: none (def_total 0); functionality: Harmony mod adding settings to tune passion and trait choices at child growth moments (Biotech); source in folder (6 .cs); lists incompatible_with Laayoune.author, which is not a package in the universe; art: one 0.2 MB icon
**Why:** Fixed six founders (brief §1) make child growth a marginal system, but if children arrive the mod only tunes vanilla Biotech outcomes. The stat-normalization audit (design/Jawa/mods/stat_normalization_audit_2026-09-09.md line 168) scoped it out as unrelated to plant growth. Passion/trait gain tuning is a parallel-ladder risk only if the owner sets generous values. KEEP on supply with an open question.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 2 C# ships in the folder but no upstream link seen · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · memory 1 texture_decoded_mb_est 1.2 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.42 · interaction 1 incompatible_with names Laayoune.author, absent from the universe, so no live conflict
**Holds it in / exit:** nothing depends on it -> none
**Open:** Are there ever children in the campaign (fixed founders)? If not, this mod is idle.
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Better ModMismatch Window (`madeline.modmismatchformatter`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/zzzz465/ModMisMatchFormatter (github, no license seen)
**Adds:** content: none (def_total 0); functionality: Replaces the mod-mismatch window shown when loading a save made with different mods with a nicer GUI and version check (uses Manifest.xml); art: one 0.71 MB texture (decoded estimate 14.9 MB)
**Why:** Directly useful here: the owner moves between machines and the list is 550 mods, so mismatch dialogs are routine. No gameplay effect. Source repo verified (zzzz465/ModMisMatchFormatter, pushed 2025-06-15). The decoded texture estimate (14.9 MB) is high for one icon but still low severity.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 1 repo https://github.com/zzzz465/ModMisMatchFormatter, last push 2025-06-15T03:53:33Z · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · memory 1 texture_decoded_mb_est 14.9 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 1.15
**Holds it in / exit:** nothing depends on it; useful for save loads across machines -> none
**Open:** A player list would only need it if players load saves with changed mod sets (audience question §5.1).
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Better Projectile Origin (`mlie.betterprojectileorigin`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/emipa606/BetterProjectileOrigin (github, MIT)
**Adds:** content: none (def_total 0); functionality: Harmony patch: projectiles leave from the weapon muzzle instead of the pawn centre (2 DLLs, settings screen, 2 static ctors); art: 2 small textures
**Why:** Visual accuracy for ranged weapons and a good match for blasters, which the scenario ships (lightsaber and blaster weapons stay, brief §2 named exclusions). It patches the projectile launch path, so a custom Verb in our weapon mods could bypass it; no xpath edge exists to confirm. Verified MIT repo (emipa606/BetterProjectileOrigin, pushed 2026-06-02).
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 1 repo https://github.com/emipa606/BetterProjectileOrigin, last push 2026-06-02T18:21:07Z · complexity 2 dll_count 2, flags ['harmony', 'settings_screen'], static_ctors 2 · memory 1 texture_decoded_mb_est 2.5 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.17 · interaction 1 Harmony patch on vanilla projectile launch; no xpath edges into our mods; compatibility with our custom verbs UNVERIFIED
**Holds it in / exit:** nothing depends on it -> none
**Open:** Test with our custom weapon verbs: does a non-vanilla Verb_LaunchProjectile subclass still launch from the muzzle?
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Better Workbench Management (`falconne.bwm`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** none (steam-only, no license seen)
**Adds:** content: none (def_total 0); 1 patch op; functionality: Better Workbench Management: richer "do until you have X" targets, copy/paste and link bills, restrict bills to a pawn, many bill-tab conveniences; 2 DLLs, 3 static ctors; art: 8 small UI textures
**Why:** Named adoption: design/Jawa/mods/required_mods.md line 1338 lists it as in both saves ("Pillar: none", i.e. pure QoL). It reduces micromanagement across a 550-mod production stack. No source link was found, so maintenance rests on the Steam author (INFERRED); it works on 1.6 in the measured session with 0 log errors.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 3 no source link found (source_kind steam-only); cannot patch if 1.7 breaks it · complexity 2 dll_count 2, flags ['harmony', 'settings_screen'], static_ctors 3 · memory 1 texture_decoded_mb_est 5.9 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.52
**Holds it in / exit:** design/Jawa/mods/required_mods.md adoption (line 1338) -> none
**Open:** none
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Bigger Gravships (and other Odyssey spaceship related settings) (`redmattis.biggergravship`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** none (steam-only, no license seen)
**Adds:** content: none (def_total 0); no XML patches; functionality: Stamps gravship size/range/support values from C# at implied-def time (settings for engine radius, extender count and range, support, thruster range, chemfuel tank size) for Odyssey gravships; art: 4 small textures
**Why:** Load-bearing for the campaign ship. src/RimMandrake/mapsynth/ship_designs.py (lines 38-75) records that the Utinni design only lifts with the owner's stored settings (BG_gravEngineMaxDistance 34, extender distance 30, extender max 12, distance from engine 85; mod defaults leave the hull unliftable, measured needing reach 74.46 vs 51.80) and that the mod wins over Vanilla Gravship Expanded because it runs after XML patching. design/Jawa/worldbuilding/gravship_landing_relaxation.md line 157 also lists it. Losing the settings file silently breaks the ship. Brief §2 lists Mini Gravships as excluded, but this mod enlarges, not shrinks, ship capability.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 3 no source link found (steam-only); cannot patch if Odyssey 1.6.x changes the comps it stamps · complexity 2 dll_count 1, flags ['harmony', 'settings_screen'], static_ctors 1 · memory 1 texture_decoded_mb_est 9.4 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.69 · interaction 2 overrides numeric comp values after XML patching, so it overrides Vanilla Gravship Expanded and any patch of ours on those comps regardless of load order (ship_designs.py)
**Holds it in / exit:** ship_designs.py stored-float settings (owner 2026-08-13); gravship_landing_relaxation.md; Mod_3522759531_GravshipSizeSettings.xml in the live Config -> unfiled: GRAVSHIP_SIZE_STATS_OWN_PATCH (own the four numbers in an RM patch so a settings reset cannot unlift the ship)
**Open:** Settings file Mod_3522759531_GravshipSizeSettings.xml matches this mod's workshop_id 3522759531 (MEASURED).; Anything that cuts or reorders it unlifts the hull silently.; NEEDS OWNER: The ship only flies because of this mod's size settings, and nothing logs it if they reset. Do you want us to build our own copy of those four numbers into a mod of ours so the ship no longer depends on a donor setting?
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Biome Compatibility Project (`kopp.biomecompatibilityproject`)
**Verdict:** ELIMINATE-COMPLETELY (MEASURED) · **Fit:** dissonant · **Source:** (C# source inside the mod folder) (ships-source, no license seen)
**Adds:** content: none (def_total 0); source ships (19 .cs); functionality: At load, appends every modded animal and plant to the wildAnimals / wildPlants lists of modded biomes (Creatures.cs lines 73-82; PlantLife.cs lines 74-81 in the shipped 1.6_Source); settings screen; art: one icon
**Why:** It directly contradicts the roster law: biome casts are hand-built per biome sitting and an animal belongs to ONE biome (CLAUDE.md "An animal belongs to ONE biome"; brief §2 evictions stopped, roster changes at each sitting). Its code mutates the same fields: the closed item WILD_ANIMALS_PADDED_LISTS_1 measured every wildAnimals list padded to 1024 records and named this mod "suspect", and src/RimMandrake/Utils/biome_wildbiomes_evictions.py exists to undo the effect. Our own tooling already refuses it: modset_builder.py TIERS["pyrelands"] puts it in `forbid`, and Pyrelands/Source/WildPlantAllowlist.cs is a runtime guard built because it (with other biome mods) injects foreign flora. Retirement is cheap: def_total 0, no dependants, no placed Things.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps U no tick FLAG in dll_flags; per-mod TPS UNMEASURED · maintenance 2 C# ships inside the mod folder but no upstream repo link seen; patchable locally, no verified upstream · complexity 1 dll_count 1, flags ['settings_screen'], static_ctors 1 · memory 1 texture_decoded_mb_est 2.6 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.55 · interaction 3 writes into wildAnimals/wildPlants of BiomeDefs, the exact fields our biome mod owns, with conflicting intent (source read: Creatures.cs lines 73-82, PlantLife.cs lines 74-81)
**Holds it in / exit:** nothing depends on it (dependants empty, patched_by empty); ship tiers already exclude it -> WILD_ANIMALS_PADDED_LISTS_1 (closed; the mechanism) / unfiled: BIOMECOMPAT_REMOVE_FROM_FULL_LIST
**Open:** Confirm in the live Player.log session that removing it clears the 1024-record padding; the closed item never named the culprit with certainty.; NEEDS OWNER: This mod stuffs extra animals and plants into every modded biome, fighting the one-home-per-animal rule. May we remove it from the full list?
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

### Build From Inventory - Continued (`memegoddess.buildfrominventory`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (C# source inside the mod folder) (ships-source, no license seen)
**Adds:** content: none (def_total 0); functionality: Harmony mod: construction jobs use materials in a colonist's or pack animal's inventory (6 DLLs, source in folder, map-component tick); art: 3 small textures
**Why:** Named adoption: design/Jawa/mods/required_mods.md line 1337 says "Prefer the Continued fork for 1.6", pillar "logistics QoL, no free materials". It suits a crew that carries salvage and builds on the move. It was a named candidate (not convicted) in the closed BRIDGE_INVENTORY_TRANSFER_REFUSES_ALL_1 item (line 82). Six DLLs is a complexity flag, and the map-component tick is unmeasured.
**Problems:** log_noise 0 0 error occurrences, 0 distinct in the 550-mod session · tps 1 tick FLAGs ['map_component_tick']; per-mod TPS UNMEASURED · maintenance 2 C# ships in the folder (7 .cs) but no upstream link; the Continued fork of a long-abandoned original · complexity 2 dll_count 6, flags harmony+map_component_tick · memory 1 texture_decoded_mb_est 1.2 MB (INFERRED proxy from PNG headers; per-mod memory UNMEASURED) · size 1 disk_mb 0.4
**Holds it in / exit:** design/Jawa/mods/required_mods.md adoption (line 1337) -> none
**Open:** Was the inventory-transfer refusal ever tested with this mod off? The closed item did not decide.
<sub>facts: batch 02 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5-5 (stage-1 batch 02) 2026-10-10</sub>

