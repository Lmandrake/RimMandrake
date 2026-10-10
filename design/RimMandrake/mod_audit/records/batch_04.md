# Mod audit record: batch 04 (code_tweaks_qol_ui_3, 41 mods)

Assessed against RUBRIC.md and SCENARIO_BRIEF.md. Stage 1 output; stage 2 checker has not run.

### Nomad Friendly Quests (`jaeger972.nomadfreindlyquests`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (none) (steam-only, None)
**Adds:** content: none (def_total 0) · functionality: Harmony DLL: lets temporary maps (camps, ancient complexes) count as player homes while you hold no settlement, and drops the minimum-colonist gate on quests (description) · art: 1 icon, no real art
**Why:** Directly serves the campaign's nomad loop: the crew lives aboard and camps, 'no tile is self-sufficient' (brief 1), and design/Jawa/mods/required_mods.md already records it as an owner-greenlit adoption ('strongly on-theme for a nomadic gravship'). Nothing of ours builds this behaviour, and it is a pure QoL gate removal that passes the 7 questions trivially (brief 4 test 4). Tiny (0.08 MB), zero logged errors.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.2 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony', 'settings_screen'], 1 static ctor(s), 0 defs, 0 patch ops) · size 1 (disk_mb 0.08) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** supplies a behaviour we have no plan to build: quest availability for settlement-less nomads; adopted on purpose in required_mods.md (owner 'sounds awesome, add if no red flags') -> None
**Open:** Does it treat a gravship-hosted map as 'temporary' correctly, i.e. does the ship count as the settlement? Untested; INFERRED only from the description.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Non uno Pinata (don't drop items) (`avilmask.nonunopinata`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (none) (steam-only, None)
**Adds:** content: 2 defs (DutyDef 1, JobDef 1) · functionality: Harmony DLL + settings: downed/killed pawns no longer burst loot onto the ground; adds corpse-inventory tools; 3 patch ops into Ideology and meaningfulparties · art: 4 small textures
**Why:** QoL that no mod of ours replaces; loot-burst is a vanilla annoyance, not a campaign pillar. Neutral fit; it does touch where loot ends up, and our scavenging design (jawa_scavenge_system_design_2026-10-03.md) wants salvage to be a deliberate process, so it is mildly in tune. No dependants, 0 logged errors.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.9 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony', 'settings_screen'], 4 static ctor(s), 2 defs, 3 patch ops) · size 1 (disk_mb 0.55) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 1 (3 patch ops into vanilla/third-party defs only; no edges with our mods)
**Holds it in / exit:** supplies QoL we have no plan to build -> None
**Open:** Check against the Doctrine/megafauna loot-yield generation (src/RimUtinni/Doctrine) that corpse loot is not expected to scatter; not examined.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Non-Destructive Gravlaunch (`planetace.nondestructivegravlaunch`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (none) (steam-only, None)
**Adds:** content: none (def_total 0) · functionality: Harmony DLL (needs Odyssey): launching a gravship no longer auto-abandons the tile it left (no 'nuclear detonation' crater of the old map) · art: 1 icon
**Why:** The ship moves repeatedly in this campaign (brief 1 loop: land, camp, improve, launch, repeat), so a launch that wipes the tile behind is the central mechanic it changes. design/Jawa/worldbuilding/gravship_landing_relaxation.md lists it by name as the existing gravship adjunct 'stops the old-tile crater'. Nothing of ours replaces it. Marked for the owner because the loop says 'decide what to leave behind', and a mod that keeps the abandoned map could soften that cost.
**Problems:** log_noise 1 (0 distinct error(s), 0 occurrence(s), 1 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 3.2 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony'], 1 static ctor(s), 0 defs, 0 patch ops) · size 1 (disk_mb 0.41) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** named in gravship_landing_relaxation.md as an installed adjunct; no ruling found on whether a launched-from tile should stay a map -> None
**Open:** When the ship launches, should the camp it leaves behind stay on the map for later return, or be abandoned (stuff lost)? This mod keeps it; vanilla destroys it.  [CARD-WORTHY]
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Out of Combat ReBoost (`coolzie.oocreboost`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (none) (steam-only, None)
**Adds:** content: none (def_total 0) · functionality: Harmony DLL + settings: out-of-combat pawn move-speed boost (rewrite of Murmur's mod); game-component tick · art: 2 small textures
**Why:** Pure QoL on movement speed outside combat; no scenario ruling touches it and no pillar is stressed (no ceiling raise, brief 4 test 4). Nothing of ours replaces it. Worth watching only because a speed buff is a stat modifier that might double-dip with our stat work.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 1 (tick FLAG(s) game_component_tick (string presence, not proof it runs); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.0 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['game_component_tick', 'harmony', 'settings_screen'], 2 static ctor(s), 0 defs, 0 patch ops) · size 1 (disk_mb 0.24) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** supplies QoL we have no plan to build -> None
**Open:** Does its speed bonus stack with any move-speed stat we ship (gravship crew gear, desert boots)? Not examined.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Persistent Precepts (`alleykat.persistentprecepts`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** https://github.com/Alleykatz/PersistentPrecepts (github, MIT)
**Adds:** content: none (def_total 0) · functionality: Harmony DLL (needs Ideology): a toggle on the ideoligion edit screen that stops precepts/rituals/buildings re-randomising when structure or memes change · art: 1 icon
**Why:** Its only use is editing an ideoligion; players receive fixed founders and a fixed world (brief 1, CLAUDE.md), so after the campaign ideoligion is authored it has no player job. It is an authoring convenience for building the Jawa ideoligion (item GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 exists). Held in only by the owner's own authoring; exit is the ideoligion freeze. Confidence INFERRED: I did not see the authoring plan state.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony', 'settings_screen'], 1 static ctor(s), 0 defs, 0 patch ops) · size 1 (disk_mb 0.07) · maintenance 2 (MEASURED repo, last push 2025-06-22; supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** owner's ideoligion authoring (no dependants in the universe) -> unfiled: PERSISTENT_PRECEPTS_RETIRE_AFTER_IDEO_FREEZE
**Open:** Is the campaign ideoligion already frozen? If so this can go now.; Are you still editing the campaign ideoligion's structure or memes? If not, this mod has no remaining job.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Perspective: Buildings (Continued) (`mlie.perspectivebuildings`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/PerspectiveBuildings (github, MIT)
**Adds:** content: none (def_total 0); 12 patch ops (Core 9, DBH Lite 5, Ideology 3, Royalty 2, Odyssey 1) · functionality: Harmony DLL: gizmo on most buildings to nudge position / mirror non-rotatable ones; purely graphical per description · art: 4 tiny textures
**Why:** Cosmetic, can be added or removed at any time per its own description, and it adds no defs. Mild interest for a hand-composed ship interior (the owner dresses scenes). The description warns attached objects (meals on tables) do not follow the offset and it is incompatible with Graphic Chair Overhaul; neither is a universe issue I could see. Lowest priority of any keep.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony'], 1 static ctor(s), 0 defs, 12 patch ops) · size 1 (disk_mb 0.17) · maintenance 2 (MEASURED repo, last push 2025-07-15; supports_1_6 True) · interaction 1 (12 patch ops into vanilla/third-party defs only; no edges with our mods)
**Holds it in / exit:** supplies a placement feature we have no plan to build -> None
**Open:** Does it correctly offset OUR buildings' art (matte natural-history register)? Not examined; it iterates a standard offset list for any building.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Prepare Landing (Continued) (`m00nl1ght.unofficialupdates.preparelanding`)
**Verdict:** ELIMINATE-COMPLETELY (INFERRED) · **Fit:** dissonant · **Source:** https://github.com/m00nl1ght-dev/PrepareLanding (github, MIT)
**Adds:** content: 3 defs (KeyBindingDef 2, KeyBindingCategoryDef 1); ~46 xml files (UI/filter layouts) · functionality: Harmony DLL + settings: a world-tile filter/search tool for choosing a landing site (Prepare Landing) · art: 4 textures
**Why:** Its job is picking a start tile on a generated world. There is no worldgen and no site selection for players: the world is one frozen savegame (brief 2 'No worldgen, ever'; brief 4 test 5, dissonant). Retirement cost checked: dependants [], no placed Things (KeyBindingDefs only), nothing inherits from its defs. The 2026-08-30 audit graded it keep (prior_verdict_2026_08_30) without individual examination. Residual risk: a world remake (brief 5 item 8) might want tile search, but the owner edits tiles through the bridge's world_* tools, not this UI. Cost on the 550 list is UNMEASURED; mods like this typically build world-grid caches on load, which is INFERRED not measured.
**Problems:** log_noise 1 (0 distinct error(s), 0 occurrence(s), 4 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.7 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony', 'settings_screen'], 4 static ctor(s), 3 defs, 1 patch ops) · size 1 (disk_mb 1.84) · maintenance 2 (MEASURED repo, last push 2025-07-21; supports_1_6 True) · interaction 1 (1 patch ops into vanilla/third-party defs only; no edges with our mods)
**Holds it in / exit:** nothing (dependants []) -> None
**Open:** World remake (brief 5 item 8): does the owner ever pick tiles with this UI?; Do you use Prepare Landing's tile search yourself when painting or checking the world? If not, it can be removed.  [CARD-WORTHY]
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Prisoners Should Fear Turrets (`mlie.prisonersshouldfearturrets`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** https://github.com/emipa606/PrisonersShouldFearTurrets (github, MIT)
**Adds:** content: 1 ThoughtDef · functionality: 2 DLLs + Harmony + settings: turrets fire on escaping prisoners and rebelling slaves, can terrorise slaves for suppression · art: 2 small textures
**Why:** Qualitative threat-handling, no stat inflation, and the campaign has slaves and prisoners as a society element (jawa_society.md slave design). Pairs with Slave Rebellions Improved, which the plot-mechanisms wave actually triggers (plot_mechanisms_wave.md). No replacement planned, 0 logged errors.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 2.5 MB (INFERRED header proxy)) · complexity 2 (2 DLL(s), flags ['harmony', 'settings_screen'], 2 static ctor(s), 1 defs, 0 patch ops) · size 1 (disk_mb 0.16) · maintenance 2 (MEASURED repo, last push 2025-06-22; supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** supplies prisoner/slave turret behaviour we have no plan to build -> None
**Open:** Turret 'terror' on slaves is a suppression lever; check against the 7 questions if slavery becomes a central economy.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Psilocap Cultivation (`laureeeeeeeeeeeeeeen.shrooms`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** (none) (steam-only, None)
**Adds:** content: 2 ThingDefs (cultivated psilocap and an ornamental potted variety); 1 patch op into Odyssey · functionality: Settings screen only (no Harmony): allows sowing psilocap where it grows wild; ornamental form for pots · art: 9 textures, ~3 MB
**Why:** Cultivable psilocap is plant content, and plants are being ported into our own defs (brief 3, owner 2026-09-20 'move everything to our own thing defs'; donor art not kept, brief 2). The plant register review lists Plant_Psilocap_Farmed (design/Jawa/worldbuilding/review/plant_register_rows.json) so a sitting is already deciding it. Held in until that sitting; exit is a port or a cut at the flora review.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 2.7 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['settings_screen'], 1 static ctor(s), 2 defs, 1 patch ops) · size 1 (disk_mb 3.47) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 1 (1 patch ops into vanilla/third-party defs only; no edges with our mods)
**Holds it in / exit:** listed as Plant_Psilocap_Farmed on the plant register review; placed plants in the save UNMEASURED -> unfiled: PSILOCAP_CULTIVATION_FLORA_SITTING
**Open:** Does the flora review want a cultivated hallucinogen at all (drug economy vs anti-exponential)?
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Quality Colors (Continued) (`dawnsglow.qualcolor`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (none) (steam-only, None)
**Adds:** content: none (def_total 0) · functionality: Harmony DLL + settings: colours item rows in the trade window by quality · art: 5 small textures
**Why:** Trade-UI cosmetic; trade is central to the Jawa fantasy and quality colour is an aid with no balance effect (brief 4 test 4). atmospheric_base_hook_ecosystem.md lists it in the lighting/looks ecosystem only as a name, no conflict identified. 0 logged errors.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 1 (tick FLAG(s) game_component_tick (string presence, not proof it runs); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 4.0 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['game_component_tick', 'harmony', 'settings_screen'], 0 static ctor(s), 0 defs, 0 patch ops) · size 1 (disk_mb 0.38) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** supplies a UI aid we have no plan to build -> None
**Open:** none
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Raid Protection Fee (`leo.raidprotectionfee`)
**Verdict:** ELIMINATE-COMPLETELY (MEASURED) · **Fit:** dissonant · **Source:** (none) (steam-only, None)
**Adds:** content: none (def_total 0) · functionality: Harmony DLL + settings: when a raid is imminent hostile human factions offer a wealth-based 'protection fee'; pay to cancel the raid · art: 2 small textures
**Why:** Three independent reasons. (1) It duplicates a mechanism the plot-mechanisms wave already chose differently: design/Jawa/proposals/plot_mechanisms_wave.md line 307 says 'pick one' of tributedemand and Raid Protection Fee and to 'cut Raid Protection Fee via Cherry Picker', keeping geojak.tributedemand (in the list, position 314). (2) It lets silver buy off danger, bypassing risk and scarcity, which the 7-question test and the 'no arms race, qualitative danger' pillar reject (brief 2 anti-exponential; brief 4 test 4). (3) It measurably harmed our own testing: in the 2026-10-10 live pass its Dialog_NodeTree swallowed a RaidEnemy, the journal read 0 pawns (Transient/foundry_fulllist_deploy_20261010.md 14:18 and honest-negatives line), and src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchIncidentTools.cs line 142 carries a special note for it. Retirement cost: dependants [], def_total 0 so no placed Things or ParentNames; it is cut by unticking or Cherry Picker, no content to port.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 4.8 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony', 'settings_screen'], 1 static ctor(s), 0 defs, 0 patch ops) · size 1 (disk_mb 0.95) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible)) · interaction 2 (live pass 2026-10-10: its modal swallowed a RaidEnemy and fire_incident still returned true with 0 pawns)
**Holds it in / exit:** nothing depends on it (dependants []); our test harness already special-cases it (JawaBenchIncidentTools.cs:142) -> None
**Open:** Confirm no save-time state (pending protection-fee letters) would break on removal; none seen since def_total 0.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Raider Swarm Compression (`ingendum.raiderswarmcompression`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (none) (steam-only, None)
**Adds:** content: 1 HediffDef · functionality: Harmony DLL + settings: merges large raids into 'swarm' pawns that stand in for several raiders · art: 1 texture
**Why:** Large raids are the main source of pawn-count load on a map that already ran 8-10 TPS on the 550 list (brief 4 test 10, cause not diagnosed). Compression keeps the danger qualitative instead of numeric, which suits 'no arms race' (brief 2). It is a Harmony patch on raid generation, so it needs a live check against our own raid arrival modes (Sh'kaar escalation, drop-in, sappers in plot_mechanisms_wave.md), which may build raids their own way. Nothing of ours replaces it.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony', 'settings_screen'], 0 static ctor(s), 1 defs, 0 patch ops) · size 1 (disk_mb 0.13) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** supplies a raid-size mitigation we have no plan to build -> None
**Open:** Does it compress raids built by our own plot mechanisms (arrival-mode overrides)? Untested; a swarm hediff on a pawn could read oddly in AftermathRites/Aftermath logic.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### RandomGrowthChoices (Continued) (`zal.randomgrowthchoices`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (none) (steam-only, None)
**Adds:** content: none (def_total 0) · functionality: Harmony: auto-picks passions/traits at child growth moments, confirmable · art: 2 tiny textures
**Why:** Owner-adopted: design/Jawa/mods/required_mods.md l.1088 records it as THE 'growth moments with choices' mod and puts it in the recommended core comedy stack; stat_normalization_audit_2026-09-09.md also checked its siblings. Nothing of ours builds it; QoL, no ceiling change. A sibling (arkymn.bettergrowthmoments) was flagged as possibly better; if both are active they would fight (not checked).
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.8 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony'], 0 static ctor(s), 0 defs, 0 patch ops) · size 1 (disk_mb 0.05) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** adopted in required_mods.md (core comedy stack) -> None
**Open:** Is arkymn.bettergrowthmoments also in the list? If yes the two growth-moment mods overlap; check.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Realistic Darkness (Light) (`wemd.realisticdarknesslight`)
**Verdict:** KEEP (INFERRED) · **Fit:** resonant · **Source:** (none) (steam-only, None)
**Adds:** content: none (def_total 0); 33 patch ops into Core (+SpeakUp, Ideology, meaningfulparties) · functionality: XML+DLL, no Harmony: darkens nights, dusks, eclipses and some weather · art: 1 texture
**Why:** Atmosphere that suits a hard desert-night frontier. design/RimMandrake/atmospheric_base_hook_ecosystem.md l.526 flags it as relevant to our L8 lighting compositor 'for the opposite reason' from the power-saver antagonist: it changes what darkness looks like, which our lighting is written against. So it is a known interaction, not a nuisance; keep and test the compositor against it. 33 patch ops into vanilla, none touching our defs (patches_ours_refs 0).
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.7 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags [], 0 static ctor(s), 0 defs, 33 patch ops) · size 1 (disk_mb 0.17) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 1 (33 patch ops into vanilla/third-party defs only; no edges with our mods)
**Holds it in / exit:** our lighting design (atmospheric_base_hook_ecosystem.md) assumes it as the darkness baseline -> None
**Open:** Which darkness level is the baseline for the L8 compositor tests; a changed darkness setting would change readability of our coloured lights.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Recycle This (Continued) (`mlie.recyclethis`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (MEASURED) · **Fit:** dissonant · **Source:** https://github.com/emipa606/RecycleThis (github, MIT)
**Adds:** content: 7 defs (DesignationDef 2, JobDef 2, WorkGiverDef 2, WorkTypeDef 1); 7 patch ops; 2 assetbundles · functionality: 2 DLLs + Harmony + settings: order icons to destroy or recycle weapons/apparel at nearest smelter or campfire without bills (yields ~25% of recipe) · art: 14 textures + 2 asset bundles
**Why:** jawa_scavenge_system_design_2026-10-03.md (owner-ruled design, nothing built) lists Mlie.RecycleThis as a HARD conflict: the nest's strip-for-parts process replaces it, and l.429 states it is active now and shipping the scavenge system removes it from the list. Until that is built it supplies the only quick-recycle path. Held in by: the absence of our replacement. Exit item: SALVAGE_WRECKAGE_EVERYWHERE_1 (the design's item).
**Problems:** log_noise 1 (0 distinct error(s), 0 occurrence(s), 1 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 2.7 MB (INFERRED header proxy); AssetBundles present, proxy understates) · complexity 2 (2 DLL(s), flags ['harmony', 'settings_screen'], 2 static ctor(s), 7 defs, 7 patch ops) · size 1 (disk_mb 0.93) · maintenance 2 (MEASURED repo, last push 2025-09-12; supports_1_6 True) · interaction 1 (7 patch ops into vanilla/third-party defs only; no edges with our mods)
**Holds it in / exit:** no replacement built yet (design only, SALVAGE_WRECKAGE_EVERYWHERE_1); frozensnowfox.complexjobs patches it (patched_by 1) -> SALVAGE_WRECKAGE_EVERYWHERE_1
**Open:** Does the planned salvage nest need an explicit incompatibility declaration with Mlie.RecycleThis (design l.19 says yes)?
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Relevant Stats In Description (`mlie.relevantstatsindescription`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** https://github.com/emipa606/RelevantStatsInDescription (github, MIT)
**Adds:** content: none (def_total 0) · functionality: 2 DLLs + Harmony + settings: shows selected stats in the architect-menu description · art: 2 tiny textures
**Why:** Pure UI info with per-stat toggles. Nothing of ours replaces it; no ruling touches it. 26 chatter lines in the log, 0 errors (log_chatter_lines 26).
**Problems:** log_noise 1 (0 distinct error(s), 0 occurrence(s), 26 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 2.5 MB (INFERRED header proxy)) · complexity 2 (2 DLL(s), flags ['harmony', 'settings_screen'], 2 static ctor(s), 0 defs, 0 patch ops) · size 1 (disk_mb 0.45) · maintenance 1 (source verified, last push 2026-08-23; supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** supplies a UI aid we have no plan to build -> None
**Open:** none
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Research Reinvented (`petetimessix.researchreinvented`)
**Verdict:** KEEP (MEASURED) · **Fit:** resonant · **Source:** https://github.com/PeteTimesSix/ResearchReinvented (github, MIT)
**Adds:** content: 192 defs: 78 AlternateResearchSubjectsDef, 33 ResearchOpportunityTypeDef, 21 SpecialResearchOpportunityDef, 14 ResearchOpportunityCategoryDef, 9 SettingsPresetDef, 9 ThingDef ... · functionality: Harmony: research is earned by field work (reverse-engineer turrets, analyse wrecks, test materials) instead of sitting at a bench · art: 48 textures
**Why:** Its design (analyse wrecked machines to learn) is the salvage-scavenger fantasy itself. Held in today by ours: WreckedMachines ParentNames SpecialResearchOpportunityBase and declares petetimessix.researchreinvented as loadAfter (About.xml); src/RimMandrake/WreckedMachines/Defs/Specials/SpecialResearchOpportunities_WreckedMachines.xml uses its def types; our mandrake.rut.researchretag patches it 4 times (patched_by_ours_refs 4) and owns 18 ported research defs from the retired Steppingstones add-on (RESEARCH_TRIO_RETIRE_1). Not a randomised-research mod (brief 2 named exclusion).
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 2 (tick FLAG(s) game_component_tick (string presence, not proof it runs); per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 7.6 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['game_component_tick', 'harmony', 'settings_screen'], 9 static ctor(s), 192 defs, 12 patch op) · size 1 (disk_mb 2.48) · maintenance 1 (source verified, last push 2026-04-18; supports_1_6 True) · interaction 2 (patched_by_ours_refs 4, patches_ours_refs 0)
**Holds it in / exit:** our WreckedMachines mod (src/RimMandrake/WreckedMachines) special opportunities; mandrake.rut.researchretag (4 patch edges); complexjobs and Euterpe patch it -> None
**Open:** research_tree_taxonomy.md and the restructured research model may change which projects RR can gate; check RR's per-project opportunities against the taxonomy.; Confirm WreckedMachines' dependency is truly soft (MayRequire-guarded per its About comment).
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Resource Dictionary (`scorpio.resourcedictionary`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# in mod folder) (ships-source (C# in mod folder), None)
**Adds:** content: none (def_total 0) · functionality: 2 DLLs + Harmony + settings; source files named Dialog_AddNewThing, ThingGroup, HarmonyPatches: a settings-driven UI to define custom resource/thing groups for the resource readout (INFERRED from file names; About description is empty) · art: 1 texture
**Why:** Small UI utility with C# source shipped in the folder (30 source files, 1.3 to 1.6), nothing of ours depends on it and nothing replaces it. QoL passes trivially. Low value, low cost: 0 logged errors, 0.48 MB. The description is empty so the claim of function rests on source file names only (INFERRED).
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 1.2 MB (INFERRED header proxy)) · complexity 2 (2 DLL(s), flags ['harmony', 'settings_screen'], 2 static ctor(s), 0 defs, 0 patch ops) · size 1 (disk_mb 0.48) · maintenance 1 (C# source ships inside the mod folder (MEASURED); no repo link seen; supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** supplies a resource-readout customisation we have no plan to build -> None
**Open:** Empty About description: confirm what it does in-game or at the next cold load.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Right Click to Toss Carried Pawn (`alma.tossem`)
**Verdict:** KEEP (INFERRED) · **Fit:** neutral · **Source:** (C# in mod folder) (ships-source (C# in mod folder), None)
**Adds:** content: 5 defs (JobDef 2, StatDef 2, HistoryEventDef 1) · functionality: XML+DLL, no Harmony: pawns carrying a pawn can throw them; mass and distance stats · art: 1 texture
**Why:** A novelty verb with C# source shipped (MEASURED). Neutral fit; a thrown Jawa fits the slapstick tone of required_mods' comedy stack, but this is a stretch (INFERRED). No dependants, no log noise (0 errors), no Harmony. Risk is low; downside would be griefing prisoners over walls.
**Problems:** log_noise 0 (0 distinct error(s), 0 occurrence(s), 0 chatter line(s) in the 550-mod session) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 1 (texture_decoded_mb_est 0.0 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags [], 0 static ctor(s), 5 defs, 0 patch ops) · size 1 (disk_mb 1.04) · maintenance 1 (C# source ships inside the mod folder (MEASURED); no repo link seen; supports_1_6 True) · interaction 0 (no patch ops, no edges with our mods (edges are a lower bound; Harmony runtime patches not visible))
**Holds it in / exit:** nothing depends on it -> None
**Open:** Does tossing a carried pawn interact with Odyssey flight/gravship zones (falling from height)? Not examined.
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

### Rim of Madness - Bones Unofficial Fix (`sihv.rombonesport`)
**Verdict:** KEEP-TEMPORARILY-THEN-PHASE-OUT (INFERRED) · **Fit:** neutral · **Source:** (none) (steam-only, None)
**Adds:** content: 30 defs (ThingDef 11, RecipeDef 8, TerrainDef 5, 3 DesignatorDropdownGroupDef, 2 ResearchProjectDef, 1 StatDef); 126 patch ops (75 into Alpha Animals) · functionality: Harmony: bones dropped by butchering, buildable as wood-stuffed things; custom BoneAmount stat · art: 73 textures, 154 MB decoded estimate (INFERRED)
**Why:** Held in by ours: mandrake.rut.researchretag patches it 15 times and lists it in loadAfter; src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_Maguana.xml writes BoneAmount with MayRequire sihv.rombonesPort, and src/RimUtinni/Doctrine/Source/gen_megafauna_yield.py names it. The 2026-09-09 stat audit confirmed its 479 statBases adds are the mod's own BoneAmount stat, not edits to existing numbers. Bone items/terrain are donor content and art (154 MB), which under 'no donor art kept' and the port-everything ruling must end up ours (brief 2, brief 3), but the bone economy has no replacement planned. 75 of its patch ops target Alpha Animals, which is itself being retired, so those die with it. Log: 1 error ('[Def Error]: BoneWall').
**Problems:** log_noise 1 (1 distinct error(s), 1 occurrence(s), 0 chatter line(s) in the 550-mod session; sample: [Def Error]: BoneWall) · tps 0 (no tick FLAG in dll_flags; per-mod TPS UNMEASURED) · memory 2 (texture_decoded_mb_est 154.3 MB (INFERRED header proxy)) · complexity 2 (1 DLL(s), flags ['harmony', 'settings_screen'], 1 static ctor(s), 30 defs, 126 patch ops) · size 1 (disk_mb 12.7) · maintenance 3 (steam-only: no repo link or source found (SEARCHED); supports_1_6 True) · interaction 2 (patched_by_ours_refs 15, patches_ours_refs 0) · log_noise 1 (1 distinct error '[Def Error]: BoneWall' (def-only attribution; may be a victim of someone else's patch))
**Holds it in / exit:** mandrake.rut.researchretag (15 edges); RSW_Maguana and Doctrine yield generator reference its stat; bones items in saves UNMEASURED; declares incompatible_with sihv.rombones and Soul.BonesNBits (neither in the universe) -> unfiled: ROMBONES_BONE_ECONOMY_PORT_OR_CUT
**Open:** Does the campaign want a bone-craft economy at all? If yes, port to RM_ defs; if no, cut and drop the MayRequire rows.; Do you want animals to drop bones that can be built into things (bone walls, tools)? If yes we port it into our defs; if no it can be cut.  [CARD-WORTHY]
<sub>facts: batch 04 · mod_facts.jsonl 2026-10-10T14:47:38-0700 · assessed by claude-sonnet-5.5 2026-10-10</sub>

