# STRUCTURE.md — canonical index of the Gravship Campaign docs

_Last updated: 2026-08-08. This is the map: what each file is, and — importantly — **who owns what**, so a fact lives in exactly one authoritative place and everyone else points to it. Read this first to navigate the folder. Lives at `~/GDrive/Personal/Rimworld/`._

---

## Directory layout (2026-08-08 reorg)

The project is now sorted into four topic buckets, with a thin navigation spine kept at the root. **File names below are unchanged — only their folders moved** — so any doc that references another by bare filename still resolves; just prepend the bucket.

| Folder | What lives here |
|---|---|
| **`/` (root spine)** | Navigation + orientation only: `STRUCTURE.md`, `concept.md`, `context.md`. |
| **`worldbuilding/`** | The fiction + design: `Alien_Bestiary`, `desert_world_design`, `biome_terrain_palette`, `faction_roster_v2`, `faction_authoring_mechanism`, `jawa_xenotype_and_religion`, `jawa_crew_personas`, `jawa_dialogue_source_audit`, `Gravship_Campaign_Planning_Discussion_2026-08-02`, `setup_checklist`, `Custom_World`, `biome_roster_for_review.html`, `resource_terrain_matrix.html`, `star_wars_species_scale_reference_atlas.pdf`. |
| **`mods/`** | Which mods we use + why: `required_mods`, `forbidden_mods`, `cherry_picker_killlist`, `sw_ingredients_inventory`, `outer_rim_cherrypick_list`, `world_interest_and_mech_danger`, `cqf_quest_types_explainer`, `concept_defnames`, and the `mod_sources/` audit tree (gitignored). |
| **`runtime/`** | Run-time apps/agents we're building or planning + the custom mods we author: `RimMaster`, `rimbridge`, `ollama`, `llm_voice_preauthoring`, `first_live_access`, `carbonite_trophy_mod`. |
| **`promo/`** | Promotional/pitch material (summaries that *sell* the campaign): `Kolyska_pitch.html` (self-contained, inline base64 art) + `concept_art_01.png`, `concept_art_02.png` (ship concept renders). |
| **`Utils/`, `player_maps/`, `custom_patches/`, `hand_authored_maps/`, `samuel_streamer_study/`, `savegame/`** | Tooling + build artifacts, unchanged (see Subfolders table). |

### Left at root deliberately (NOT yet bucketed)
- **`ship_designs.md`, `ship_deck_plan.md`, `ship_distinctive_features.md`, `Factory_lore.md`** + the ship reference images (`ship_image.png`, `ship_damaged_image.png`, `ship_deck_plan_scale_map.png`) — these are **actively owned by the concurrent Cowork instance**; moving them risks colliding with in-flight edits. They belong in `worldbuilding/` in the next pass, once that instance is idle.
- **`save_authoring_pipeline.md`, `rimworld_file_lore.md`** — the `Utils/Savegame_*.py` scripts cite these via hard-coded `../<file>.md` doc-string paths; since `Utils/` is contested I can't fix those refs, so the manuals stay adjacent for now.
- **`custom_patches/`** (JawaVoice + Jawa_Patches) — `Utils/build_jawavoice.py` hard-codes its output to `../custom_patches/JawaVoice`; moving it would silently break the build. Stays put until the builder can be updated together with it.

---

## The canonical spine (start here)

These are the load-bearing, authoritative files. If two docs disagree, the owner named here wins.

| File | Role — the single source of truth for… |
|---|---|
| **`concept.md`** | The one-page orientation: premise, pillars, sanctioned mechanics. The elevator pitch. |
| **`context.md`** | Narrative running log of decisions and discussion. References the mod files rather than restating them. |
| **`required_mods.md`** | **Authoritative** selected-mod list — every adopted mod + its per-mod restrictions/config. Also owns: the **THE FORCE system** (NPC-only VPE, lines ~428–436), the four-axis terrain adopt/reject verdicts, and the Faction Territories conditional-accept spec. |
| **`forbidden_mods.md`** | **Authoritative** anathema list — banned mods/categories, each tagged with the pillar it violates. Owns: the **7-question test**, the **player-psycasting ban + its NPC-only VPE/Force exception**, and the full **VFE-Insectoids 2** and **VGE** cherry-pick strip/keep lists. |
| **`Gravship_Campaign_Planning_Discussion_2026-08-02.md`** | The major scope-expansion doc. Owns the **§19 enemy-danger thesis (§19.1–§19.9)** and the custom-progression-mod build spec. |
| **`desert_world_design.md`** | The desert world's design. Owns the **four-axis terrain schema** (① Abundant / ② Scarce / ③ Exotic / ④ Threat), the **dark-biome / fog-of-war ruling + the LOCKED "dark tiles pause the orbital timer" mechanic** (§3(e) + §4-Orbital), and the pre-placed-hazard §3F (Hutt corpse-marker tripwire). |
| **`biome_terrain_palette.md`** | **Verified** biome/terrain inventory — the defName-level palette (vanilla + Odyssey + Alpha/Advanced Biomes). Owns the dark-biome candidate table (§A6). |
| **`setup_checklist.md`** | The live, ordered scenario-setup checklist (§0–§13). Owns the **§13 in-game verification battery** (throwaway dev-world tests before the real save). |
| **`faction_roster_v2.md`** | **Canonical** 10-NPC desert-world faction roster: per-faction dossiers, relations matrix, racial-mixture spawn tables, GM/narrative appendix. Owns faction *casting* (which race → which faction). |
| **`cherry_picker_killlist.md`** | **§2 is the single source of truth for the race inventory** (verified in-hand; supersedes the deleted `races.md`). Also the master Cherry-Picker cull list. |

---

## Supporting / specialist docs

| File | Role |
|---|---|
| `concept_defnames.md` | Companion to `concept.md`: verified defNames/packageIds/Workshop IDs — "known-good starting guesses," re-confirm before any patch/save-edit. |
| `world_interest_and_mech_danger.md` | Sole home of ~15 mech-danger / world-interest mod adoption verdicts (Reinforced Mechanoids 2, Total Warfare, etc.). Cites the §19 thesis (which lives in the Planning Discussion doc). |
| `star_wars_species_scale_reference_atlas.pdf` | **Visual + scale reference for the race roster** (added 2026-08-11). 49 pages, one per species: 46 campaign species each with sourced reference art, a canonical height range, and a scale strip normalising it against a **1.80 m human**. Grades its own evidence — TURNAROUND (Twi'lek, Rodian: Lucasfilm production sheets) > FULL BODY > PORTRAIT/PARTIAL — and keeps one entry (Sith Pureblood) with no captured image specifically to expose the gap. Source URLs on every page (mostly swrpggm.com; StarWars.com for the turnarounds; dimensions.com for Jabba). **Use it to check any race-authoring or art work against canon scale** — e.g. Gamorrean is **1.3–1.6 m, shorter than a human**, Jawa 0.8–1.2 m, Wookiee 2.0–2.3 m, Hutt ~1.75 m tall × 3.9 m long. Companion to the §2 race inventory in `cherry_picker_killlist.md`, which owns *which* races we have; this owns *how big they are and what they look like*. |
| `jawa_xenotype_and_religion.md` | The Jawa xenotype + buildable ideoligion spec (player faction deep-dive). **Part 4 owns the society lore**: slavery/reproduction/aging churn, the §4.2 love-gate + acquisition/no-rot rules, §4.2b mood economy. |
| `jawa_crew_personas.md` | The five founding Jawa colonists (Nekko/Tobb/Griz/Yeku/Wim): role coverage + each embodies one lore strand + one story-arc seed. Owns the Character-Editor scope note + the 7-Q verdicts on the persona-authoring mods. |
| `jawa_dialogue_source_audit.md` | Source-audited Jawa dialogue/translation corpus for SpeakUp voice authoring (§3 Grade-A canonical palette). |
| `faction_authoring_mechanism.md` | The *method* (how) for building differentiated factions to "Samuel Streamer level." The *filled roster* is `faction_roster_v2.md`. |
| `Custom_World.md` | Living playbook for authoring storytelling-centric worlds, reverse-engineered from Samuel Streamer's configs. |
| `outer_rim_cherrypick_list.md` | Concrete def shopping-list for the custom 1.6 Outer Rim sub-mod (Task A). |
| `sw_ingredients_inventory.md` | Inspiration-only ingredient inventory of the six non-1.6 SW faction mods (⚠️ DO NOT LOAD) + the triage that feeds `outer_rim_cherrypick_list.md`. |
| `carbonite_trophy_mod.md` | Design for a custom (cooler-than-donor) carbonite mod. Its **CANONICAL SPEC** section owns the concrete numbers ("Class 3 Carbon Freezing Chamber" station, freeze inputs, black-monolith Slab, thaw debuff, furniture placement + storage rack); the **implementation-architecture** section owns the class/def/JobDriver structure. |
| `Factory_lore.md` | **Player-wisdom operating guide for VFE-Factory** (compiled 2026-08-06, fully sourced [S1]–[S10]). The definitive "how to actually run this mod" reference: the modular 8-cell campus architecture, per-machine footprints + input/output counts + optimization notes, conveyor/filter/hopper rules and their known limitations (no priority splitter, steel clogs, chemfuel-network unevenness), the booster/heatsink thermal spine (9.9-tile radius, 3 boosters→500%, 4 heatsinks→−25% each), build order, failure-mode table, and capability checklist. Distinct from `required_mods.md` (which owns the *adoption decision* + anti-exponential restrictions) — this owns *layout/operation craft*. Directly feeds the deck-plan (`ship_deck_plan.md`). **§11 (2026-08-07) owns the #15-hull interior craft across three passes: §11.1 fit-check evidence (every rim pod holds its real machine set at true footprints, 101+ tiles headroom); §11.2 systems/flow skeleton (ring corridor, causeway, pod airlocks, 9.9-tile-verified thermal spine, 7 filtered belt trunks); §11.3 the buildable build sheet (machines re-packed with 1-tile aisles, factory-floor apron, 100% of hoppers seated, belt-to-machine stubs, thermal re-verified at worst 7.51 tiles). Tooling: `player_maps/{interior_fit,skeleton_15,render_skeleton,build_sheet_15,render_build_sheet}.py`.** |
| `ship_deck_plan.md` | **The hulk-ship deck plan + repair-progression design** (deep-think 2026-08-06). Owns the **campus-cells→ship-wings map**, the **heat doctrine** (open holes vent early → sealing forces active cooling), and the **repair-as-progression gate** (7-phase restoration table enforcing the anti-exponential pillar), all bounded by the verified **2,000-tile substructure cap** (~1,850 used, ~150 headroom). The hull silhouette **[DECIDE B] is RESOLVED → #15 "Falcon Halo (hollow)"** (topology owned by `ship_designs.md`); consumes `Factory_lore.md` (layout craft) + the substructure math; still carries open decisions **[DECIDE A, C, D, E]**. The one true blocker (authoring a large pre-broken start save) routes to `save_authoring_pipeline.md` + `first_live_access.md`. |
| `ship_distinctive_features.md` | **The Kolyska's identity layer** (2026-08-07) — the aesthetic/narrative/light-mechanical touches that make the ship feel specific. Owns 8 [ACCEPTED] features (carbonite reliquary dead, engine-is-god, asymmetry-as-identity, the dead prong, running-lights-as-repair-progress-bar, per-pod trade shrines, hammocks-among-the-machines→religion, external glowing heat vents) + a parked [IDEA] pool + the **distinctive-ship mod research** (Fetcher 2026-08-07): Q1 no non-LLM talkable-AI mod exists→keep SpeakUp+CQF+persona-core; Q2 graffiti/signs = Signs&Comments Continued + Graffiti Mod Continued; Q3 holograms = EGI Holograms&Projectors + Afterlife: Ghosts of the Rim. Distinct from `ship_deck_plan.md` (topology/heat/repair-gates) and `Factory_lore.md` §11 (buildable interior). |
| `llm_voice_preauthoring.md` | **Paste-ready LLM voice prompts** (created 2026-08-08). Owns the actual install-time text for the two adopted LLM voice mods: PART A = RimAI Persona for the Kolyska machine-spirit ("Cradle-Mind" identity/worldview/backstory, anti-exp refusal in-voice, voice-only); PART B = RimDialogue "Additional Instructions" Jawa-scoped dynamic-Jawaese prompt + the A/B-vs-JawaVoice comparison table + scope/model-quality install checks. Consumes `ship_distinctive_features.md` (§Q1-bis adopt-both decision), `jawa_dialogue_source_audit.md` (Grade-A Jawaese), `jawa_xenotype_and_religion.md` (ideoligion voice). The two in-situ forks stay open by design. |
| `save_authoring_pipeline.md` | How we hand-craft the world by editing `.rws`/def files directly, grounded in the Gravtasm save teardown. |
| `first_live_access.md` | **Day-one runbook**, reframed 2026-08-09 to the user's **three-phase build plan**: **Phase A** = prove the live-LLM bridge (Ollama and/or Claude) on a *stock vanilla world* with RimBridge — a research spike whose deliverable is reusable agents/skills/patterns, not a save; **Phase B** = load the full mod stack (ours + favorites) just to confirm it runs, make a real save, and export **one giant live inventory** of every def/item/creature/faction to study together (live-via-bridge preferred, offline shortHash→defName Def-index scan as backstop); **Phase C** = only then decide how to adapt the design into a playable game. Carries the **shadow-mode default** (satiation engine reports what it WOULD do before live injection is flipped on). Distinct from `setup_checklist.md` (in-game scenario decisions). |
| `rimworld_file_lore.md` | Self-teaching technical manual for editing RimWorld save/scenario/def XML — file structures, safe-vs-fragile regions, gotchas. |
| `rimbridge.md` | Living context on RimBridgeServer (live in-game modification pipe — not a content editor). |
| `RimMaster.md` | Spec for the external RimMaster enrichment agent (save-editing +/or RimBridge). §4b = the phased agent-possibilities catalogue (incl. the 8 religious-observance + HeDiff agents A–H, added 2026-08-08). |
| `divine_satiation_engine.md` | **Mechanical design for agent G** (created 2026-08-08): per-god satiation + fickle-Mood vector, no drift-to-baseline (event-driven), 3 input channels per god (ambient / costly-lever / extreme-band), whole-pantheon ritual scoring, contextual PC-death, ghost-as-divine-actor hypothesis. Consumes `jawa_xenotype_and_religion.md` §2.0b (pantheon canon); feeds agents A/H/C/F/D. |
| `resource_terrain_matrix.html` / `biome_roster_for_review.html` | Rendered review views (resource×terrain matrix; biome roster). |

## Subfolders

| Path | Contents |
|---|---|
| `worldbuilding/` | Fiction + design docs (see Directory layout above). |
| `mods/` | Mod decisions + `mods/mod_sources/` audit tree (see Directory layout above). |
| `runtime/` | Run-time apps/agents + authored custom mods (see Directory layout above). |
| `promo/` | Promotional/pitch material — reserved, currently empty. |
| `samuel_streamer_study/` | Downloaded Samuel Streamer mod-lists/configs + the technique/theme analysis they feed. |
| `Utils/` | Tooling: Jawa-voice builder, save-inspection scripts, the LLM-in-the-loop map-improver. Writes JawaVoice output to `../custom_patches/JawaVoice`. |
| `player_maps/` | Authored player-map plans + loop reports (coastal_mesa v1–v3). |
| `custom_patches/` | Our authored 1.6 mods: JawaVoice (built) + Jawa_Patches. Built by `Utils/build_jawavoice.py`. |
| `hand_authored_maps/` | Study library of downloaded `.rws` maps (payloads gitignored; README manifest tracked). |
| `savegame/` | The Gravtasm reference `.rws` and related saves. |
| `mod_sources/` | → moved to `mods/mod_sources/` (gitignored extracted mod trees, audited during design). |

---

## Ownership rules (to prevent drift)
- **Race inventory** → `cherry_picker_killlist.md` §2. Everyone else points to it.
- **Cherry-pick strip lists** (VFE-Insectoids 2, VGE) → `forbidden_mods.md`. `required_mods.md` carries only a pointer + summary.
- **Dark-biome / fog / timer-pause mechanic** → `desert_world_design.md`. Palette table stays in `biome_terrain_palette.md`; Workshop IDs in `required_mods.md`; in-game checks in `setup_checklist.md`.
- **THE FORCE / VPE NPC-only decision** → `required_mods.md` (~428–436), with `forbidden_mods.md` stating the player-side ban + exception and `faction_roster_v2.md` §"Global system 5" giving the one-liner.
- **§19 enemy-danger thesis** → `Gravship_Campaign_Planning_Discussion_2026-08-02.md`.

## Recently removed (recover from git if needed)
`Gravship_Campaign_Design_Notes.md`, `resource_catalogue.md`, `candidate_factions.md`, `faction_dossiers.md`, `in_game_verification_checklist.md`, `races.md` — all folded into the owners above on 2026-08-05/06.
