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

