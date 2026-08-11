# STRUCTURE.md — the manifest

_Rewritten 2026-08-11 from a full audit of all 88 docs. Half the corpus was missing from the previous version, including `CLAUDE.md`, `NEXT_RELOAD.md`, `REFRESH.md`, `live_mod_inventory.md` and the modding skill — every one of them load-bearing. This file is the map: what each doc is, **who owns what** so a fact lives in exactly one authoritative place, and — new — **what kind of doc it is**, so you know whether to trust it, regenerate it, or ignore it._

**Four threads work in this repo simultaneously, sharing one working tree.** Before editing a doc, `git status` it — if it is already modified, someone is in it. When committing, **name every path explicitly**; never `git add -A` / `git add .` / `git commit -a`, or you will sweep another thread's unfinished work into your commit. Full rule in `CLAUDE.md`.

---

## 0. The six kinds of document

The single most useful thing to know about a file here is which of these it is. Most navigation mistakes are category mistakes — treating a log as a spec, or hand-editing generated data.

| Kind | Trust it for | Rule |
|---|---|---|
| 🧭 **SPINE** | Orientation. Read before anything else. | Keep short. Detail belongs in the doc it points to. |
| 📜 **OWNER** | Current truth about its one domain. | The single source of truth. If two docs disagree, the owner wins. |
| ⚙️ **GENERATED** | Measured facts about the live install. | **Never hand-edit.** Regenerate — see `REFRESH.md`. |
| 📚 **REFERENCE** | Imported craft/research from outside this project. | Consult when relevant. Not maintained, not project state. |
| 🔄 **EPHEMERAL** | Live working state right now. | Short shelf life. Harvest, then clear. |
| 🗄️ **ARCHIVE** | Why a past decision was made. | **Never** for what is true now. |

---

## 1. Read these first (🧭 SPINE)

| File | Role |
|---|---|
| **`CLAUDE.md`** | **Standing operating rules, auto-loaded every session.** The actual entry point. Kept short by design. |
| **`STRUCTURE.md`** | This file. What exists, who owns what, what kind it is. |
| **`concept.md`** | The one-page orientation: premise, pillars, sanctioned mechanics. The elevator pitch. |
| **`NEXT_RELOAD.md`** | 🔄 **The shared queue for the next game load.** A cold load costs ~23–30 min and is the project's scarcest resource. Any thread may append. Work the pre-flight list before launching; harvest and clear after. |
| **`REFRESH.md`** | 🔄 What to re-run after changing the mod list. Every generated artefact is a snapshot of one mod set; stale data still answers questions, which is worse than missing data. |
| **`skills/rimworld-modding/`** | The modding skill — XML PatchOperations, custom Defs, C#/Harmony, load order, `Player.log` triage. `SKILL.md` + `references/{traps,patch-operations,csharp-and-loading}.md`. **Load it before writing into any mod folder**; RimWorld XML has silent-failure modes. |

---

## 2. Owner docs (📜) — the single source of truth, by domain

### Mods and the load set

| File | Owns |
|---|---|
| `mods/required_mods.md` | **The adopted-mod list** + every per-mod restriction/config. Also owns the **THE FORCE system** (NPC-only VPE), the four-axis terrain verdicts, and the Faction Territories spec. |
| `mods/forbidden_mods.md` | **The anathema list** — banned mods/categories, each tagged with the pillar it violates. Owns the **7-question test**, the **player-psycasting ban** + its NPC-only exception, and the VFE-Insectoids 2 / VGE strip-and-keep lists. |
| `mods/cherry_picker_killlist.md` | **§2 owns the race inventory** — which Star Wars races we actually have. Also the master Cherry Picker cull list. Scale and appearance are owned separately: see the atlas below. |
| `mods/benign_log_errors.md` | **Log errors that are safe to ignore**, each traced to root cause. §0 owns the triage method. Read it before investigating any red text. |
| `mods/armoury_keeplist.md` | The proposed weapon roster, drafted from the live 674-weapon dump. Follows `setting_physics.md`. |
| `mods/world_interest_and_mech_danger.md` | ~15 mech-danger / world-interest mod verdicts. |
| `mods/outer_rim_cherrypick_list.md` | Def shopping-list for the custom 1.6 Outer Rim sub-mod. |
| `mods/def_override_clusters.md` | Contested defNames across the stack. Backlog note, not an investigation. |

### The world and the fiction

| File | Owns |
|---|---|
| `worldbuilding/desert_world_design.md` | The desert world. The **four-axis terrain schema**, the **dark-biome / fog ruling + the LOCKED "dark tiles pause the orbital timer" mechanic**, and §3F pre-placed hazards. |
| `worldbuilding/setting_physics.md` | **The physical laws of this universe** — the constitution every balance decision derives from. |
| `worldbuilding/balance_paradigm.md` | **Why we would change any number.** The decision framework for normalising/cutting/re-skinning the stack. Paradigm, not a work order. |
| `worldbuilding/faction_roster_v2.md` | The **10-NPC faction roster**: dossiers, relations matrix, racial spawn tables. Owns faction *casting*. |
| `worldbuilding/faction_authoring_mechanism.md` | The *method* for building differentiated factions. The filled roster is `faction_roster_v2.md`. |
| `worldbuilding/jawa_xenotype_and_religion.md` | The Jawa xenotype + ideoligion. **Part 4 owns the society lore** — slavery/reproduction/aging churn, §4.2 love-gate, §4.2b mood economy. |
| `worldbuilding/jawa_crew_personas.md` | The five founding colonists (Nekko/Tobb/Griz/Yeku/Wim). |
| `worldbuilding/jawa_dialogue_source_audit.md` | The source-audited Jawaese corpus. §3 owns the Grade-A canonical palette. |
| `worldbuilding/biome_terrain_palette.md` | ⚙️-adjacent: the **verified** defName-level biome/terrain inventory. §A6 owns the dark-biome candidates. |
| `worldbuilding/Alien_Bestiary.md` | The Star Wars naming layer over the VGE creature roster. |
| `worldbuilding/Livestock_Trade_Utility_Pets_v1.md` | The livestock/pet/companion layer across the whole adopted creature stack. §16 owns the beast trade; §16.5 owns the **slave-block imperative** that `jawa_xenotype_and_religion.md` §4 depends on. _(Moved out of `Utils/` 2026-08-11 — it is design, not tooling.)_ |
| `worldbuilding/setup_checklist.md` | The ordered scenario-setup checklist. §13 owns the in-game verification battery. |
| **`worldbuilding/star_wars_species_scale_reference_atlas.pdf`** | 📚 **How big each race is and what it looks like** — 46 species, sourced art, heights normalised to a 1.80 m human. Companion to the §2 race inventory: that owns *which*, this owns *how big*. |

### The ship

| File | Owns |
|---|---|
| `worldbuilding/ship_designs.md` | Hull silhouette + topology. |
| `worldbuilding/ship_deck_plan.md` | Deck plan + repair progression: the campus→wings map, the **heat doctrine**, the **repair-as-progression gate**, bounded by the 2,000-tile substructure cap. |
| `worldbuilding/ship_distinctive_features.md` | The Kolyska's identity layer — 8 accepted features + a parked idea pool + the distinctive-ship mod research. |
| `worldbuilding/Factory_lore.md` | 📚 **How to actually run VFE-Factory** — machine footprints, conveyor rules, the thermal spine, failure modes. §11 owns the #15-hull interior across three passes. Distinct from `required_mods.md`, which owns the *adoption decision*. |

### Runtime, agents and authored mods

| File | Owns |
|---|---|
| `runtime/build_plan.md` | **The execution strategy** — the four-tier allocation rule, the stamp→save→polish resolution, the M0–M5 milestone ladder. |
| `runtime/first_live_access.md` | The day-one runbook: Phase A prove the bridge, Phase B load the stack and inventory it, Phase C adapt the design. Owns the shadow-mode default. |
| `runtime/RimMaster.md` | The external enrichment agent. §4b owns the phased agent catalogue. |
| `runtime/rimbridge.md` | RimBridgeServer — the live in-game modification pipe. |
| `runtime/divine_satiation_engine.md` | Agent G's mechanics: per-god satiation, event-driven, whole-pantheon ritual scoring. Consumes the §2.0b pantheon canon. |
| `runtime/llm_voice_preauthoring.md` | Paste-ready install-time prompts for the two adopted LLM voice mods. |
| `runtime/llm_stack_assessment.md` | How far the installed LLM stack gets us without writing code. |
| `runtime/rimtalk_analysis.md` | RimTalk adoption analysis (written when RimDialogue was delisted). |
| `runtime/music_protocol.md` | Adding our own music. RimTunes already replaces the vanilla music system — read before authoring SongDefs. |
| `runtime/carbonite_trophy_mod.md` | The carbonite mod design + its canonical numbers. |
| `runtime/parked_mod_concepts.md` | Mechanics we liked but are not building yet. A parking lot, deliberately. |
| `runtime/ollama.md` | Standing up local Ollama on Windows. |
| `custom_patches/README.md` | **Deployment.** The repo copy is NOT what the game loads — read before testing anything. Owns the `Utils/deploy_custom_mods.py` process. |
| `image_request/graphic.md` | The Gamorrean head-art commission brief. |
| `image_request/graphics_overhaul_protocol.md` | The generalised method for overhauling race art ourselves. |

### Technique manuals

| File | Owns |
|---|---|
| `save_authoring_pipeline.md` | How we hand-craft the world by editing `.rws`/def files. ⚠️ Must stay at root — `Utils/Savegame_*.py` hard-code `../<file>.md`. |
| `rimworld_file_lore.md` | Self-teaching manual for RimWorld save/scenario/def XML. ⚠️ Same hard-coded-path constraint. |
| `worldbuilding/Custom_World.md` | Playbook for authoring storytelling-centric worlds, reverse-engineered from Samuel Streamer's configs. |
| `mods/cqf_quest_types_explainer.md` | What kinds of quests Custom Quest Framework can build. |

---

## 3. Generated (⚙️) — regenerate, never hand-edit

| File / dir | Produced by |
|---|---|
| `mods/live_mod_inventory.md` | **Single source of truth for mod identity** — overrides every such claim elsewhere in the corpus. From `ModsConfig.xml` + every `About.xml`. |
| `mods/inventory/` | `Utils/animal_inventory.py` — animals CSVs, attacks, life stages, biome map, conflicts, patch watch, contact sheets, `races_crossmod.md`. |
| `savegame/03_Gravtasm__*.md` | `Utils/Savegame_*.py`. Gitignored. |
| `player_maps/*_improvement.md`, `*_loop_report.md` | `Utils/loop_run.py` / `map_loop_agent.py`. Run artefacts, not reference docs — regenerate rather than read as history. **Exception:** `player_maps/authored/coastal_mesa_rationale.md` is 📜 hand-written, not generated — it is the worked example of LLM-authored (not algorithmic) map design, and its renderer is only a pen. |
| `custom_patches/JawaVoice/` | `Utils/build_jawavoice.py`. |
| `custom_patches/Jawa_Armoury/Patches/` | Its own `Source/*.py` generators. |

`REFRESH.md` says what to re-run and when.

---

## 4. Reference (📚) — imported wisdom, sorted not maintained

Consult when the topic comes up. **Nothing in the project depends on these being current**, and they are not project state. Do not spend effort keeping them fresh.

| File | What it is |
|---|---|
| `reference/rimworld_handcrafted_map_atlas.md` | A 2026-08-07 census of the publicly discoverable handcrafted-map scene. _(Moved out of `Utils/` 2026-08-11 — research, not tooling.)_ |
| `reference/rimworld_map_image_sources.md` | A 2026-08-05 catalogue of sources for RimWorld map imagery. _(Same move.)_ |
| `samuel_streamer_study/` | Downloaded mod-lists and per-mod configs from Mr Samuel Streamer, plus `02_TECHNIQUE_ANALYSIS.md`. The technique that mattered was already extracted into `Custom_World.md`. |
| `mods/inspiration/` | Two research dossiers on weapon effects and gadget/utility mods — candidates, not decisions. |
| `mods/sw_ingredients_inventory.md` | Inspiration-only inventory of six non-1.6 SW faction mods. ⚠️ **DO NOT LOAD** them. |
| `hand_authored_maps/` | Study library of downloaded `.rws` maps. README manifest tracked; payloads gitignored. |

---

## 5. Ephemeral (🔄) and archive (🗄️)

| File | State |
|---|---|
| `NEXT_RELOAD.md` | 🔄 Live queue. Clear it after harvesting a load. |
| `REFRESH.md` | 🔄 Live protocol. |
| `custom_patches/JawaIonWeapons/CSHARP_BUILD_SPEC.md` | Now the **design record** for the ion capture mechanic, not a work order — it was built in `a5856a9` while the header still said "TO DO". Retire when the rationale migrates into the mod README. |
| `context.md` | 🗄️ **ARCHIVE — demoted from the spine 2026-08-11.** A chronological log of design conversations (67 headings from 2026-08-02 alone), unmaintained after 2026-08-06. Every load-bearing decision in it has been promoted to an owner doc. Read it for **why**, never for **what is true now**. Do not append. |
| `mods/concept_defnames.md` | Verified defName vocabulary — but `live_mod_inventory.md` overrides it for mod identity. Keeps the reasoning only. |
| `mods/github_issue_swcp_bundle.md` | An upstream bug report (issue #7, open) + a correction to it. Close out and delete when resolved. |
| `custom_patches/JawaIonWeapons/CSHARP_BUILD_SPEC.md` | Build spec for a shipped mod. Retire if the DLL is stable. |

---

## 6. Ownership rules (to prevent drift)

- **Mod identity** (exists? packageId? Workshop ID?) → `mods/live_mod_inventory.md`. It overrides every other doc, including this one.
- **Race inventory** (which races) → `cherry_picker_killlist.md` §2. **Race scale/appearance** (how big, what they look like) → `star_wars_species_scale_reference_atlas.pdf`.
- **Cherry-pick strip lists** → `forbidden_mods.md`. `required_mods.md` carries a pointer only.
- **Dark-biome / fog / timer-pause** → `desert_world_design.md`. Palette → `biome_terrain_palette.md`. Workshop IDs → `live_mod_inventory.md`. In-game checks → `setup_checklist.md`.
- **THE FORCE / VPE NPC-only** → `required_mods.md`, with `forbidden_mods.md` stating the player-side ban.
- **§19 enemy-danger thesis** → `Gravship_Campaign_Planning_Discussion_2026-08-02.md` (🗄️ otherwise; that thesis is the live part).
- **Deploying an authored mod** → `custom_patches/README.md`. The repo copy is not what the game loads.
- **Log noise** → `mods/benign_log_errors.md` before investigating anything.

## 7. Directory map

| Folder | Contents |
|---|---|
| `/` | **Spine only** (`CLAUDE.md`, `STRUCTURE.md`, `concept.md`, `NEXT_RELOAD.md`, `REFRESH.md`), plus `context.md` (🗄️) and the two docs pinned here by hard-coded script paths: `save_authoring_pipeline.md` and `rimworld_file_lore.md` (`Utils/Savegame_*.py` cite them as `../<file>.md`). Eight files. Nothing else belongs at root. |
| `worldbuilding/` | The fiction + design. |
| `mods/` | Mod decisions, generated inventories, `inspiration/`, and the gitignored `mod_sources/` audit tree. |
| `runtime/` | Agents, LLM stack, and authored-mod designs. |
| `custom_patches/` | **Source** for our four authored mods. Deploy with `Utils/deploy_custom_mods.py`. |
| `Utils/` | Tooling only. Python probes + the deploy script. |
| `reference/` | 📚 Imported research. Added 2026-08-11. |
| `skills/` | The `rimworld-modding` skill. |
| `image_request/` | Art commissions; `seed/` is gitignored third-party reference art. |
| `player_maps/`, `hand_authored_maps/`, `savegame/`, `samuel_streamer_study/`, `promo/` | Map artefacts, study library, save teardowns, external study, pitch material. |

## 8. Audit outcomes (2026-08-11, completed pass)

The first pass deferred four items because other threads held the files. All four are now closed:

1. ✅ **Root bucketed.** `ship_designs`, `ship_deck_plan`, `ship_distinctive_features`, `Factory_lore` and the three ship PNGs moved to `worldbuilding/`. Root is the eight files listed in §7 and nothing else.
2. ✅ **`HANDOFF_2026-08-10.md` deleted.** Two facts lived nowhere else and were migrated first: the **RimMaster relay must be restarted after every game restart** (stale socket → `ConnectionAbortedError`, looks like a bridge bug) → `runtime/RimMaster.md` §2b; and the **`validate_patch.py --defnames`** idea → `NEXT_RELOAD.md` Parked. Everything else in it had already landed in `CLAUDE.md`, `benign_log_errors.md` or `live_mod_inventory.md`.
3. ✅ **`required_mods.md` — verdict reversed after reading it.** The first pass flagged 287 dated lines as trimmable narration. That was a line-count heuristic and it was wrong: **246 lines carry an explicit restriction, strip-list or "do not"**, and the dates are the verification record backing the project's own "never guess a packageId" rule. Hand-trimming it would risk dropping a restriction to buy tidiness. Its real defect is that it is ordered **by decision date, not topic**, so a later section silently overrides an earlier one. Fixed with a navigation header + topic index rather than a rewrite. Reorganise only with the live inventory open and a way to diff mod-by-mod.
4. ✅ **`context.md` kept as 🗄️ archive, not deleted.** It is pure superseded narrative, but git holds it either way and 16 docs cite it; deleting would orphan those references for no operational gain. The banner does the real work — it stops anyone reading it as current.
5. ✅ **Stale status corrected:** `custom_patches/JawaIonWeapons/CSHARP_BUILD_SPEC.md` still said "TO DO. Nothing has been built yet" after the DLL shipped in `a5856a9`. It is now marked BUILT and reframed as the design record.

**Still open, deliberately:**

- **9 `player_maps/` reports are orphaned run artefacts** — nothing references them, and they regenerate from `Utils/loop_run.py`. Harmless; delete if the folder ever gets noisy.
- **`git config core.fileMode false` was set locally** (2026-08-11) because Drive's DrvFs mount flips permission bits, so **136 files showed as modified when only 7 had changed** — which is very likely why a thread reached for `git commit -a`. That config lives in `.git/config` and is **not committed**, so every clone and every other thread must set it themselves. Do it before trusting `git status`.

## 9. Removed (recover from git)

`Gravship_Campaign_Design_Notes.md`, `resource_catalogue.md`, `candidate_factions.md`, `faction_dossiers.md`, `in_game_verification_checklist.md`, `races.md` — folded into the owners above 2026-08-05/06.

`HANDOFF_2026-08-10.md` — deleted 2026-08-11 after its two unmigrated facts were moved out (see §8.2). It was a one-session cloud→local handoff; `CLAUDE.md` + this file replaced it.
