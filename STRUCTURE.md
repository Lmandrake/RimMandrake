# STRUCTURE.md — canonical index of the Gravship Campaign docs

_Last updated: 2026-08-06. This is the map: what each file is, and — importantly — **who owns what**, so a fact lives in exactly one authoritative place and everyone else points to it. Read this first to navigate the folder. Lives at `~/GDrive/Personal/Rimworld/`._

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
| `jawa_xenotype_and_religion.md` | The Jawa xenotype + buildable ideoligion spec (player faction deep-dive). **Part 4 owns the society lore**: slavery/reproduction/aging churn, the §4.2 love-gate + acquisition/no-rot rules, §4.2b mood economy. |
| `jawa_crew_personas.md` | The five founding Jawa colonists (Nekko/Tobb/Griz/Yeku/Wim): role coverage + each embodies one lore strand + one story-arc seed. Owns the Character-Editor scope note + the 7-Q verdicts on the persona-authoring mods. |
| `jawa_dialogue_source_audit.md` | Source-audited Jawa dialogue/translation corpus for SpeakUp voice authoring (§3 Grade-A canonical palette). |
| `faction_authoring_mechanism.md` | The *method* (how) for building differentiated factions to "Samuel Streamer level." The *filled roster* is `faction_roster_v2.md`. |
| `Custom_World.md` | Living playbook for authoring storytelling-centric worlds, reverse-engineered from Samuel Streamer's configs. |
| `outer_rim_cherrypick_list.md` | Concrete def shopping-list for the custom 1.6 Outer Rim sub-mod (Task A). |
| `sw_ingredients_inventory.md` | Inspiration-only ingredient inventory of the six non-1.6 SW faction mods (⚠️ DO NOT LOAD) + the triage that feeds `outer_rim_cherrypick_list.md`. |
| `carbonite_trophy_mod.md` | Design for a custom (cooler-than-donor) carbonite mod. **CANONICAL SPEC v3 (2026-08-06)** now owns the concrete design: "Class 3 Carbon Freezing Chamber" station, freeze inputs (lots of Chemfuel + 2 Components + 2 Steel + 1 Plasteel + 1 Uranium + a pawn *or* material stack), black-monolith Slab (value ≈ contents + 1 cryptosleep casket, shows contents, near-indestructible, drops only burning debris, no power once frozen), half-day blind/disorient thaw debuff, wall-rotatable Furniture placement + 5-high minified storage rack. v3 supersedes the earlier Task B numbers where they conflict. |
| `Factory_lore.md` | **Player-wisdom operating guide for VFE-Factory** (compiled 2026-08-06, fully sourced [S1]–[S10]). The definitive "how to actually run this mod" reference: the modular 8-cell campus architecture, per-machine footprints + input/output counts + optimization notes, conveyor/filter/hopper rules and their known limitations (no priority splitter, steel clogs, chemfuel-network unevenness), the booster/heatsink thermal spine (9.9-tile radius, 3 boosters→500%, 4 heatsinks→−25% each), build order, failure-mode table, and capability checklist. Distinct from `required_mods.md` (which owns the *adoption decision* + anti-exponential restrictions) — this owns *layout/operation craft*. Directly feeds the parked deck-plan deep-think. |
| `save_authoring_pipeline.md` | How we hand-craft the world by editing `.rws`/def files directly, grounded in the Gravtasm save teardown. |
| `first_live_access.md` | **Day-one runbook** for the first time we have running RimWorld + real mods + a harmonized save: ordered tooling/agent-integration steps (shortHash resolver → Def index → validate JawaVoice/factions/scenario → RimBridge swap) + the offline pre-reqs to build first. Distinct from `setup_checklist.md` (in-game scenario decisions). |
| `rimworld_file_lore.md` | Self-teaching technical manual for editing RimWorld save/scenario/def XML — file structures, safe-vs-fragile regions, gotchas. |
| `rimbridge.md` | Living context on RimBridgeServer (live in-game modification pipe — not a content editor). |
| `RimMaster.md` | Spec for the external RimMaster enrichment agent (save-editing +/or RimBridge). |
| `resource_terrain_matrix.html` / `biome_roster_for_review.html` | Rendered review views (resource×terrain matrix; biome roster). |

## Subfolders

| Path | Contents |
|---|---|
| `samuel_streamer_study/` | Downloaded Samuel Streamer mod-lists/configs + the technique/theme analysis they feed. |
| `Utils/` | Tooling: Jawa-voice builder, save-inspection scripts, the LLM-in-the-loop map-improver. |
| `player_maps/` | Authored player-map plans + loop reports (coastal_mesa v1–v3). |
| `savegame/` | The Gravtasm reference `.rws` and related saves. |
| `mod_sources/` | Extracted mod source trees, audited during design (not all committed). |

---

## Ownership rules (to prevent drift)
- **Race inventory** → `cherry_picker_killlist.md` §2. Everyone else points to it.
- **Cherry-pick strip lists** (VFE-Insectoids 2, VGE) → `forbidden_mods.md`. `required_mods.md` carries only a pointer + summary.
- **Dark-biome / fog / timer-pause mechanic** → `desert_world_design.md`. Palette table stays in `biome_terrain_palette.md`; Workshop IDs in `required_mods.md`; in-game checks in `setup_checklist.md`.
- **THE FORCE / VPE NPC-only decision** → `required_mods.md` (~428–436), with `forbidden_mods.md` stating the player-side ban + exception and `faction_roster_v2.md` §"Global system 5" giving the one-liner.
- **§19 enemy-danger thesis** → `Gravship_Campaign_Planning_Discussion_2026-08-02.md`.

## Recently removed (recover from git if needed)
`Gravship_Campaign_Design_Notes.md`, `resource_catalogue.md`, `candidate_factions.md`, `faction_dossiers.md`, `in_game_verification_checklist.md`, `races.md` — all folded into the owners above on 2026-08-05/06.
