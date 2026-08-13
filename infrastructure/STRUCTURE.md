# STRUCTURE.md — the manifest

_Rewritten 2026-08-11 from a full audit of all 88 docs. **Re-audited against the tree 2026-08-12** — see the note below. This file is the map: what each doc is, **who owns what** so a fact lives in exactly one authoritative place, and **what kind of doc it is**, so you know whether to trust it, regenerate it, or ignore it._

> ⚠️ **This file must not restate a count that lives somewhere else.** On
> 2026-08-12 it carried per-file trap counts that had drifted within hours of
> being written (tooling 17→20, xml-and-defs 13→14) while the index they were
> copied from stayed correct — because appending an entry updates the index and
> nothing updates a copy. Caught by BRIDGE. **Name the thing and point at its
> authority; let the authority hold the number.** This is `DOC_BUDGET.md`
> §"A written instruction rots" rule 1 (was `agents_def.md` Rule 0.6), and the
> manifest is the single most tempting place to break it.

> ⚠️ **A manifest decays silently.** The 2026-08-12 re-audit found this file had missed **four of the five skills**, the entire `src/RimMandrake/bridgetools/` directory, `runtime/{map_authoring_decision,droid_ruling}.md`, the four `AGENT_*_state.md` files and `agents_def.md`, and it still said "four authored mods" against six. Nothing here was *wrong* — it was true on 2026-08-11 and simply never re-run. **If you add a top-level directory, a skill, an authored mod or a root file, update this file in the same commit.** Everything else in the repo announces itself; a missing manifest entry does not.

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
| ⛔ **DEFERRAL REGISTER** | What was deliberately **cut**, and why. | The only kind that tells you **not** to act. Do not "helpfully" implement an entry. |

> ⛔ **The deferral register is new (2026-08-12) and currently has exactly one instance:** `src/RimMandrake/WreckedMachines/V2.md`, by CREATE. It is listed as a kind because it is the only class here whose entries are **prohibitions**, and mis-filing one is actively harmful: **a deferral filed in `TODO.md` reads as work someone should pick up**, and picking it up silently un-cuts a decision the owner made deliberately. That risk is not hypothetical — two of its entries are *coupled*, and restoring "sacred scrap" alone would restore the fiction while **silently deleting the repair loop**, because `deconstructible=false` is exactly what blocks build-over.
>
> **Deliberately NOT generalised into a repo-wide convention yet.** One instance is not a pattern, and naming a document class from a single example is how you get five near-identical files nobody indexes. **The trigger is the second instance:** when a second mod needs a deferral register, that is when this earns a naming convention and an index entry here — not before. _(CREATE's call, and it is the right one. **Correction, on CREATE's own account:** they did not derive it from Rule 0.6 — the scoping judgement came first, because one instance felt thin, and the resemblance to 0.6 was recognised afterwards. Recorded because the earlier wording implied the rule was applied deliberately, which would leave a later reader expecting that reasoning to have been available in advance. It was available in hindsight. The call is no worse for it — but a manifest that overstates how a decision was reached is the same defect this file keeps finding elsewhere.)_

---

## 1. Read these first (🧭 SPINE)

| File | Role |
|---|---|
| **`CLAUDE.md`** | **Standing operating rules, auto-loaded every session.** The actual entry point. Kept short by design. |
| **`STRUCTURE.md`** | This file. What exists, who owns what, what kind it is. |
| **`concept.md`** | The one-page orientation: premise, pillars, sanctioned mechanics. The elevator pitch. |
| **`TODO.md`** | 🔄 **The authoring backlog** — work accepted but not started. Leaves the file by being built. Not to be confused with `design/Jawa/parked_mod_concepts.md` (a shelf of uncommitted ideas) or `NEXT_RELOAD.md` (questions needing the game running). |
| **`NEXT_RELOAD.md`** | 🔄 **The shared queue for the next game load.** A cold load costs ~23–30 min and is the project's scarcest resource. Any thread may append. Work the pre-flight list before launching; harvest and clear after. |
| **`REFRESH.md`** | 🔄 What to re-run after changing the mod list. Every generated artefact is a snapshot of one mod set; stale data still answers questions, which is worse than missing data. |
| **`agents_def.md`** | **The five seats and the rules they share** — Rule 0 (name your window), 0.5 (never drop a finding you do not own), 1–10, 6a (hold a shared file for minutes, not hours), 6b (addressing), 9 (mixed-subject directories), plus the VISION→CREATE→OPS→BRIDGE handoff contract and "who draws, who fixes". **Dissolved 2026-08-13** to a short residue: seat identities went to `infrastructure/agents/<SEAT>.md`, Rule 0.6 (how an instruction rots) to `DOC_BUDGET.md`, and all messaging/addressing/filing detail to `skills/agent-messaging/SKILL.md`. Read with `CLAUDE.md`. |
| **`skills/rimworld-modding/`** | The modding skill — XML PatchOperations, custom Defs, C#/Harmony, load order, `Player.log` triage. **Load it before writing into any mod folder**; RimWorld XML has silent-failure modes. Its earned-lessons log was **split five ways on 2026-08-12** (it had reached 51 entries against its own 40-entry threshold): read the **index** at `references/traps.md` and open only the topic file you need — `traps-tooling.md`, `traps-xml-and-defs.md`, `traps-mods-and-managers.md`, `traps-art.md`, `traps-diagnosis.md`. Reading all five at once is not the intent. **Per-file entry counts live in the index and only in the index** — it is updated whenever an entry lands, so a second copy here would drift, and did. |
| **`skills/rimbridge/`** | The live-game skill — drive a running RimWorld through the RimBridgeServer GABP bridge: spawn things, build, set quality, control time, screenshot. `SKILL.md` + `references/{capability-matrix,traps}.md`. Every claim in it was verified against a running game. **Load it before your first live mutation.** |

### The other three skills — the art pipeline

Not spine; load them only when making art. They stack, and the RimWorld one wraps the other two:

| Skill | What it does |
|---|---|
| `skills/generating-rimworld-sprites/` | **The one to load for any PNG bound for a mod's `Textures/`.** Enforces the game's asset contract — exact canvas, real alpha, silhouette inside the def's footprint — and ships an **offline validator** (`scripts/validate_sprite.py`) that rejects bad art *before* it costs a ~23–30 min load. |
| `skills/generating-images/` | Makes an image from nothing, by driving the Codex CLI's `$imagegen`. Owns the chroma-key route, which is the only way to get alpha on a ChatGPT-auth Codex install. |
| `skills/editing-images/` | Modifies an image that already exists, and proves what changed. Owns the drift problem: **everything you did not mention is free to move** — size, framing, palette, outline. |

The `*.skill` files beside these directories are packaged zips built by `src/RimMandrake/Utils/package_skill.py`. The **directory is the source**; edit there and re-package. Never hand-edit a `.skill`. All five package clean — `python src/RimMandrake/Utils/package_skill.py --all` (verified 2026-08-13 under WSL `python`, exit 0). **Either `python` or `python3` works; the owner installed Python in WSL on 2026-08-13.**

### Discovery, and the installed plugins

`.claude/skills/` holds a **symlink per skill** into `skills/`, so Claude Code auto-discovers them for every agent while there is still only one copy on disk. Edit `skills/<name>/`; the symlink follows. _(Whether Claude Code follows a symlinked skill dir is confirmed by whether they appear in a **new** session's skill list — see `TODO.md` §3.)_

Three Anthropic plugins are enabled in `~/.claude/settings.json` (user scope, so they apply outside this repo too), together ~579 tokens always-on:

| Plugin | Why it is here |
|---|---|
| `skill-creator` | Audits and improves skills, and measures triggering. It produced the 2026-08-12 traps split. |
| `claude-md-management` | Audits `CLAUDE.md` quality and captures session learnings — PROJECT's job, with tooling. |
| `hookify` | Builds guardrail hooks from observed mistakes. This repo's failure mode is shared-tree accidents, and `.claude/hooks/block_blanket_git_stage.py` is the pattern it generalises. |

`claude plugin details <name>` prints a component inventory **and projected token cost** — run it before enabling anything else, since every plugin taxes all four agents' context.

---

## 2. Owner docs (📜) — the single source of truth, by domain

### Mods and the load set

| File | Owns |
|---|---|
| `design/Jawa/mods/required_mods.md` | **The adopted-mod list** + every per-mod restriction/config. Also owns the **THE FORCE system** (NPC-only VPE), the four-axis terrain verdicts, and the Faction Territories spec. |
| `design/Jawa/mods/forbidden_mods.md` | **The anathema list** — banned mods/categories, each tagged with the pillar it violates. Owns the **7-question test**, the **player-psycasting ban** + its NPC-only exception, and the VFE-Insectoids 2 / VGE strip-and-keep lists. |
| `design/Jawa/mods/cherry_picker_killlist.md` | **§2 owns the race inventory** — which Star Wars races we actually have. Also the master Cherry Picker cull list. Scale and appearance are owned separately: see the atlas below. |
| `vendor/wisdom/benign_log_errors.md` | **Log errors that are safe to ignore**, each traced to root cause. §0 owns the triage method. Read it before investigating any red text. |
| `design/Jawa/mods/armoury_keeplist.md` | The proposed weapon roster, drafted from the live 674-weapon dump. Follows `setting_physics.md`. |
| `design/Jawa/mods/world_interest_and_mech_danger.md` | ~15 mech-danger / world-interest mod verdicts. |
| `design/Jawa/mods/agent_supersession_audit.md` | **"Does a mod already do this?"** for each enrichment agent — owns the **ADJUSTER vs DEFINED-EFFECT** test and the ship-voice bake-off verdict. Adoption itself stays in `required_mods.md`. |
| `design/Jawa/mods/outer_rim_cherrypick_list.md` | Def shopping-list for the custom 1.6 Outer Rim sub-mod. |
| `vendor/wisdom/def_override_clusters.md` | Contested defNames across the stack. Backlog note, not an investigation. |

### The world and the fiction

| File | Owns |
|---|---|
| `design/Jawa/worldbuilding/desert_world_design.md` | The desert world. The **four-axis terrain schema**, the **dark-biome / fog ruling + the LOCKED "dark tiles pause the orbital timer" mechanic**, and §3F pre-placed hazards. |
| `design/Jawa/worldbuilding/setting_physics.md` | **The physical laws of this universe** — the constitution every balance decision derives from. |
| `design/Jawa/worldbuilding/enrichment_agents.md` | **The world-enrichment agent catalogue** — Phases A–D, the religious/hediff cluster (§5), and the open questions §7.1–7.3 that the runtime docs cite. |
| `design/RimMandrake/balance_paradigm.md` | **Why we would change any number.** The decision framework for normalising/cutting/re-skinning the stack. Paradigm, not a work order. |
| `design/Jawa/worldbuilding/faction_roster_v2.md` | The **10-NPC faction roster**: dossiers, relations matrix, racial spawn tables. Owns faction *casting*. |
| `design/RimMandrake/faction_authoring_mechanism.md` | The *method* for building differentiated factions. The filled roster is `faction_roster_v2.md`. |
| `design/Jawa/worldbuilding/jawa_xenotype_and_religion.md` | The Jawa xenotype + ideoligion. **Part 4 owns the society lore** — slavery/reproduction/aging churn, §4.2 love-gate, §4.2b mood economy. |
| `design/Jawa/worldbuilding/jawa_crew_personas.md` | The five founding colonists (Nekko/Tobb/Griz/Yeku/Wim). |
| `design/Jawa/worldbuilding/jawa_dialogue_source_audit.md` | The source-audited Jawaese corpus. §3 owns the Grade-A canonical palette. |
| `design/Jawa/worldbuilding/biome_terrain_palette.md` | ⚙️-adjacent: the **verified** defName-level biome/terrain inventory. §A6 owns the dark-biome candidates. |
| `design/Jawa/worldbuilding/Alien_Bestiary.md` | The Star Wars naming layer over the VGE creature roster. |
| `design/Jawa/worldbuilding/Livestock_Trade_Utility_Pets_v1.md` | The livestock/pet/companion layer across the whole adopted creature stack. §16 owns the beast trade; §16.5 owns the **slave-block imperative** that `jawa_xenotype_and_religion.md` §4 depends on. _(Moved out of `src/RimMandrake/Utils/` 2026-08-11 — it is design, not tooling.)_ |
| `design/Jawa/worldbuilding/setup_checklist.md` | The ordered scenario-setup checklist. §13 owns the in-game verification battery. |
| **`research/Jawa/star_wars_species_scale_reference_atlas.pdf`** | 📚 **How big each race is and what it looks like** — 46 species, sourced art, heights normalised to a 1.80 m human. Companion to the §2 race inventory: that owns *which*, this owns *how big*. |

### The ship

| File | Owns |
|---|---|
| `design/Jawa/worldbuilding/ship_designs.md` | Hull silhouette + topology. |
| `design/Jawa/worldbuilding/ship_deck_plan.md` | Deck plan + repair progression: the campus→wings map, the **heat doctrine**, the **repair-as-progression gate**, bounded by the 2,000-tile substructure cap. |
| `design/Jawa/worldbuilding/ship_distinctive_features.md` | The Kolyska's identity layer — 8 accepted features + a parked idea pool + the distinctive-ship mod research. |
| `vendor/wisdom/Factory_lore.md` | 📚 **How to actually run VFE-Factory** — machine footprints, conveyor rules, the thermal spine, failure modes. §11 owns the #15-hull interior across three passes. Distinct from `required_mods.md`, which owns the *adoption decision*. |

### Runtime, agents and authored mods

| File | Owns |
|---|---|
| `design/Jawa/build_plan.md` | **The execution strategy** — the four-tier allocation rule, the stamp→save→polish resolution, the M0–M5 milestone ladder. |
| `design/Jawa/first_live_access.md` | The day-one runbook: Phase A prove the bridge, Phase B load the stack and inventory it, Phase C adapt the design. Owns the shadow-mode default. |
| `infrastructure/disposing/RimMaster.md` | 🗑️ **RETIRED residue** — only the dead relay/architecture sections. Mechanism superseded by `skills/rimbridge/` + `skills/rimworld-savegame/`; the live content went to `design/Jawa/worldbuilding/enrichment_agents.md` and `design/Jawa/mods/agent_supersession_audit.md`. |
| `design/RimMandrake/rimbridge.md` | RimBridgeServer — the live in-game modification pipe. The *how-to* is `skills/rimbridge/`; this owns the adoption and setup. |
| `design/RimMandrake/map_authoring_decision.md` | **RimBridge vs save-editing for authoring a map** — written 2026-08-12 at the point where both paths were proven and the choice became real. Owns which pipe we author maps through. |
| `design/Jawa/droid_ruling.md` | **Ion, capture and what detonates** — the owner's droid design ask, verified against the live install and the game assembly. Research complete, nothing built; referenced from `TODO.md` §1. |
| `design/Jawa/divine_satiation_engine.md` | Agent G's mechanics: per-god satiation, event-driven, whole-pantheon ritual scoring. Consumes the §2.0b pantheon canon. |
| `design/RimMandrake/llm_voice_preauthoring.md` | Paste-ready install-time prompts for the two adopted LLM voice mods. |
| `design/RimMandrake/llm_stack_assessment.md` | How far the installed LLM stack gets us without writing code. |
| `design/RimMandrake/rimtalk_analysis.md` | RimTalk adoption analysis (written when RimDialogue was delisted). |
| `design/RimMandrake/music_protocol.md` | Adding our own music. RimTunes already replaces the vanilla music system — read before authoring SongDefs. |
| `design/Jawa/carbonite_trophy_mod.md` | The carbonite mod design + its canonical numbers. |
| `design/Jawa/parked_mod_concepts.md` | Mechanics we liked but are not building yet. A parking lot, deliberately. |
| `design/RimMandrake/ollama.md` | Standing up local Ollama on Windows. |
| `src/Jawa/README.md` | **Deployment.** The repo copy is NOT what the game loads — read before testing anything. Owns the `src/RimMandrake/Utils/deploy_custom_mods.py` process. ⚠️ Its contents table still lists **four** authored mods; there are six (filed for CREATE in `TODO.md`). |
| `src/RimMandrake/WreckedMachines/` | ⛔ **PARKED — the whole mod is deferred to v2** (owner, 2026-08-12: v1 uses mangled metal salvage and role-plays the wrecked machines; no new research). The mod is **complete, validated, committed, undeployed and absent from `ModsConfig.xml` — that is the intended state, not an unfinished one.** Four docs, not interchangeable: `README.md` = how to run the art pipeline · `DESIGN.md` = ⛔ PARKED, now the **brief for v2** rather than a design in progress · `MACHINES.md` = per-machine art state · **`V2.md` = the deferral register**, nine entries, opening with the whole-mod stand-down. ⚠️ **Its `replaceTags` repair loop was never run in game** — the def shape is proven against Core, that a blueprint actually places over an existing tier is not. v2 starts with a game cycle, not more design. |
| `src/RimMandrake/bridgetools/` | **The RimBridge companion assembly** (`JawaBench.BridgeTools`). Not a mod — the mod loader never sees it; RimBridgeServer loads it late from the *game root's* `BridgeTools/` folder and registers its `[Tool]` methods onto the live bridge. So it does **not** go through `deploy_custom_mods.py` and does **not** appear in `ModsConfig.xml`. Build + deploy with `src/RimMandrake/bridgetools/build.py` (plan-only; `--apply` deploys). |
| `design/Jawa/art/graphic.md` | The Gamorrean head-art commission brief. |
| `design/Jawa/art/graphics_overhaul_protocol.md` | The generalised method for overhauling race art ourselves. |

### Technique manuals

| File | Owns |
|---|---|
| `save_authoring_pipeline.md` | How we hand-craft the world by editing `.rws`/def files. ⚠️ Must stay at root — `src/RimMandrake/Utils/Savegame_*.py` hard-code `../<file>.md`. |
| `rimworld_file_lore.md` | Self-teaching manual for RimWorld save/scenario/def XML. ⚠️ Same hard-coded-path constraint. |
| `design/RimMandrake/Custom_World.md` | Playbook for authoring storytelling-centric worlds, reverse-engineered from Samuel Streamer's configs. |
| `vendor/wisdom/cqf_quest_types_explainer.md` | What kinds of quests Custom Quest Framework can build. |

---

## 3. Generated (⚙️) — regenerate, never hand-edit

| File / dir | Produced by |
|---|---|
| `observed/2026-08-13_pre-restructure/live_mod_inventory.md` | **Single source of truth for mod identity** — overrides every such claim elsewhere in the corpus. From `ModsConfig.xml` + every `About.xml`. |
| `observed/2026-08-13_pre-restructure/inventory/` | `src/RimMandrake/Utils/animal_inventory.py` — animals CSVs, attacks, life stages, biome map, conflicts, patch watch, contact sheets, `races_crossmod.md`. |
| `observed/2026-08-13_pre-restructure/savegame/03_Gravtasm__*.md` | `src/RimMandrake/Utils/Savegame_*.py`. Gitignored. |
| `player_maps/*_improvement.md`, `*_loop_report.md` | `src/RimMandrake/Utils/loop_run.py` / `map_loop_agent.py`. Run artefacts, not reference docs — regenerate rather than read as history. **Exception:** `design/RimMandrake/coastal_mesa_rationale.md` is 📜 hand-written, not generated — it is the worked example of LLM-authored (not algorithmic) map design, and its renderer is only a pen. |
| `src/Jawa/JawaVoice/` | `src/RimMandrake/Utils/build_jawavoice.py`. |
| `src/Jawa/Jawa_Armoury/Patches/` | Its own `Source/*.py` generators. |
| `src/RimMandrake/bridgetools/artifacts/BridgeTools/` | `src/RimMandrake/bridgetools/build.py` — the compiled companion DLL. **Gitignored, not committed** (`.gitignore:68`, untracked in `b59b673`). ⚠️ It was previously committed here and this table justified that with "so a session without the .NET SDK can still deploy it" — **that capability has never existed**: `main()` calls `build()` unconditionally, `build()` `sys.exit`s on a missing SDK before `plan_deploy` is reached, and there is no `--no-build`. Corrected 2026-08-12 on BRIDGE's finding. |
| `deployed/config/` | Timestamped `ModsConfig.xml` and per-mod settings snapshots, taken before each risky change. ⚠️ **Never pin a filename to one of these** — take the newest with `ls -t … \| head -1`. A pinned backup name is the classic "true statement that has stopped being the current baseline". |
| `observed/2026-08-13_pre-restructure/latency_*.json`, `src/Jawa/art_bench/` | `src/RimMandrake/Utils/bridge_latency.py` run data; art work-in-progress staged for `src/`. |
| `design/Jawa/worldbuilding/*.html` | Rendered review sheets (`biome_roster_for_review`, `resource_terrain_matrix`) — read-only views over decisions the owner docs hold. |

`REFRESH.md` says what to re-run and when.

---

## 4. Reference (📚) — imported wisdom, sorted not maintained

Consult when the topic comes up. **Nothing in the project depends on these being current**, and they are not project state. Do not spend effort keeping them fresh.

| File | What it is |
|---|---|
| `research/RimMandrake/reference/rimworld_handcrafted_map_atlas.md` | A 2026-08-07 census of the publicly discoverable handcrafted-map scene. _(Moved out of `src/RimMandrake/Utils/` 2026-08-11 — research, not tooling.)_ |
| `research/RimMandrake/reference/rimworld_map_image_sources.md` | A 2026-08-05 catalogue of sources for RimWorld map imagery. _(Same move.)_ |
| `research/RimMandrake/samuel_streamer_study/` | Downloaded mod-lists and per-mod configs from Mr Samuel Streamer, plus `02_TECHNIQUE_ANALYSIS.md`. The technique that mattered was already extracted into `Custom_World.md`. |
| `research/RimMandrake/inspiration/` | Two research dossiers on weapon effects and gadget/utility mods — candidates, not decisions. |
| `research/Jawa/sw_ingredients_inventory.md` | Inspiration-only inventory of six non-1.6 SW faction mods. ⚠️ **DO NOT LOAD** them. |
| `research/RimMandrake/hand_authored_maps/` | Study library of downloaded `.rws` maps. README manifest tracked; payloads gitignored. |

---

## 5. Ephemeral (🔄) and archive (🗄️)

| File | State |
|---|---|
| `AGENT_BRIDGE_state.md`, `AGENT_OPS_state.md`, `AGENT_CREATE_state.md`, `AGENT_VISION_state.md`, `AGENT_PROJECT_state.md` | 🔄 **One per agent: where that thread is, and its cross-session address.** **Only the named agent edits or deletes its own file** — read the others, never write them. Each publishes a `uds:` socket under a `**Cross-session address:**` line (rule 6b); `grep -A1 'Cross-session address' AGENT_*_state.md` is the routing table. ⚠️ The addresses are **PID-based and go stale on any session restart** — a stale one routes silently to whoever inherited the PID, which is worse than an absent one, so republish on resume before anything else. |
| `NEXT_RELOAD.md` | 🔄 Live queue. Clear it after harvesting a load. |
| `REFRESH.md` | 🔄 Live protocol. |
| `src/Jawa/JawaIonWeapons/CSHARP_BUILD_SPEC.md` | Now the **design record** for the ion capture mechanic, not a work order — it was built in `a5856a9` while the header still said "TO DO". Retire when the rationale migrates into the mod README. |
| `context.md` | 🗄️ **ARCHIVE — demoted from the spine 2026-08-11.** A chronological log of design conversations (67 headings from 2026-08-02 alone), unmaintained after 2026-08-06. Every load-bearing decision in it has been promoted to an owner doc. Read it for **why**, never for **what is true now**. Do not append. |
| `design/Jawa/mods/concept_defnames.md` | Verified defName vocabulary — but `live_mod_inventory.md` overrides it for mod identity. Keeps the reasoning only. |
| `vendor/wisdom/github_issue_swcp_bundle.md` | An upstream bug report (issue #7, open) + a correction to it. Close out and delete when resolved. |
| `src/Jawa/JawaIonWeapons/CSHARP_BUILD_SPEC.md` | Build spec for a shipped mod. Retire if the DLL is stable. |

---

## 6. Ownership rules (to prevent drift)

- **Mod identity** (exists? packageId? Workshop ID?) → `observed/2026-08-13_pre-restructure/live_mod_inventory.md`. It overrides every other doc, including this one.
- **Race inventory** (which races) → `cherry_picker_killlist.md` §2. **Race scale/appearance** (how big, what they look like) → `star_wars_species_scale_reference_atlas.pdf`.
- **Cherry-pick strip lists** → `forbidden_mods.md`. `required_mods.md` carries a pointer only.
- **Dark-biome / fog / timer-pause** → `desert_world_design.md`. Palette → `biome_terrain_palette.md`. Workshop IDs → `live_mod_inventory.md`. In-game checks → `setup_checklist.md`.
- **THE FORCE / VPE NPC-only** → `required_mods.md`, with `forbidden_mods.md` stating the player-side ban.
- **§19 enemy-danger thesis** → `Gravship_Campaign_Planning_Discussion_2026-08-02.md` (🗄️ otherwise; that thesis is the live part).
- **Deploying an authored mod** → `src/Jawa/README.md`. The repo copy is not what the game loads.
- **Log noise** → `vendor/wisdom/benign_log_errors.md` before investigating anything.

## 7. Directory map

| Folder | Contents |
|---|---|
| `/` | **Spine + live agent state, and nothing else.** Fourteen files: the spine (`CLAUDE.md`, `STRUCTURE.md`, `concept.md`, `TODO.md`, `NEXT_RELOAD.md`, `REFRESH.md`, `agents_def.md`), the four `AGENT_*_state.md`, `context.md` (🗄️), and the two docs pinned here by hard-coded script paths: `save_authoring_pipeline.md` and `rimworld_file_lore.md` (`src/RimMandrake/Utils/Savegame_*.py` cite them as `../<file>.md`). A new doc at root needs a reason from that list. |
| `design/Jawa/worldbuilding/` | The fiction + design, plus the ship PNGs and the rendered `*.html` review sheets. |
| `mods/` | Mod decisions, generated inventories, `inspiration/`, `dev/RimDefDump` (the dev-only mod that produces the live def dump), and the gitignored `mod_sources/` audit tree. |
| `runtime/` | Agents, LLM stack, authored-mod designs, `backups/` (⚙️ ModsConfig + settings snapshots) and `art/`. ✅ **Owned under `agents_def.md` rule 9, ratified by the owner 2026-08-12** (re-confirmed 2026-08-13): *the doc is owned by whoever owns the subject; the directory is owned by PROJECT for shape and staleness.* `runtime/` was the case that forced the rule — it is a decision-doc drawer, not one subject, so PROJECT reshapes/indexes/chases staleness and files findings on the subject owner rather than editing their content. |
| `src/` | **Source** for our **six** authored mods — `Jawa_Patches`, `JawaVoice`, `JawaIonWeapons`, `Jawa_Armoury`, `Jawa_Doctrine` (removes the Droid Factory from the build menu), `WreckedMachines` (art pipeline only, not enabled). Deploy with `src/RimMandrake/Utils/deploy_custom_mods.py`. |
| `src/RimMandrake/bridgetools/` | The `JawaBench.BridgeTools` RimBridge **companion assembly** — C# source, `build.py`, the Python probes that exercise it, and a **gitignored** build output under `artifacts/`. **Not a mod**, and it deploys to the *game root*, not to `Mods/`. Building requires the .NET SDK; there is no deploy-without-build path. |
| `src/RimMandrake/Utils/` | Tooling only. Python probes, the deploy script, `set_agent_window.sh`, `package_skill.py`. |
| `reference/` | 📚 Imported research. Added 2026-08-11. |
| `infrastructure/output/` | 🔄 **Evidence, not doctrine** — audit reports, options papers, one-off analyses. Produced to answer a question, never to state a rule, so **no seat may cite one as authority**. A finding that matters moves to a durable home; the report then moves to `infrastructure/disposing/`. PROJECT sweeps it with the stale-file audit. Tracked, but outside `doc_budget.py` per-class budgets and unscanned by `check_refs.py`. See `infrastructure/output/README.md`. |
| `infrastructure/disposing/` | 🗑️ **Quarantine for files believed dead** — 7-day unreferenced dwell, then PROJECT deletes. Nothing here is authoritative; treat it as absent, and exclude it from greps. The step *after* `infrastructure/output/`. See `infrastructure/disposing/README.md`. |
| `skills/` | **Five skills**, each a directory plus a packaged `.skill` zip: `rimworld-modding`, `rimbridge`, `generating-rimworld-sprites`, `generating-images`, `editing-images`. Edit the **directory**, then re-package with `src/RimMandrake/Utils/package_skill.py`. |
| `design/Jawa/art/` | Art commissions; `seed/` is gitignored third-party reference art. |
| `player_maps/`, `research/RimMandrake/hand_authored_maps/`, `observed/2026-08-13_pre-restructure/savegame/`, `research/RimMandrake/samuel_streamer_study/`, `promo/` | Map artefacts, study library, save teardowns, external study, pitch material. |

## 8. Audit outcomes (2026-08-11, completed pass)

The first pass deferred four items because other threads held the files. All four are now closed:

1. ✅ **Root bucketed.** `ship_designs`, `ship_deck_plan`, `ship_distinctive_features`, `Factory_lore` and the three ship PNGs moved to `design/Jawa/worldbuilding/`. _(Root was eight files **on 2026-08-11**; `agents_def.md` and the four `AGENT_*_state.md` have joined it legitimately since. §7 carries the current list — read it there, not here.)_
2. ✅ **`HANDOFF_2026-08-10.md` deleted.** One fact lived nowhere else and was migrated first: the **`validate_patch.py --defnames`** idea → `NEXT_RELOAD.md` Parked. Everything else in it had already landed in `CLAUDE.md`, `benign_log_errors.md` or `live_mod_inventory.md`.
3. ✅ **`required_mods.md` — verdict reversed after reading it.** The first pass flagged 287 dated lines as trimmable narration. That was a line-count heuristic and it was wrong: **246 lines carry an explicit restriction, strip-list or "do not"**, and the dates are the verification record backing the project's own "never guess a packageId" rule. Hand-trimming it would risk dropping a restriction to buy tidiness. Its real defect is that it is ordered **by decision date, not topic**, so a later section silently overrides an earlier one. Fixed with a navigation header + topic index rather than a rewrite. Reorganise only with the live inventory open and a way to diff mod-by-mod.
4. ✅ **`context.md` kept as 🗄️ archive, not deleted.** It is pure superseded narrative, but git holds it either way and 16 docs cite it; deleting would orphan those references for no operational gain. The banner does the real work — it stops anyone reading it as current.
5. ✅ **Stale status corrected:** `src/Jawa/JawaIonWeapons/CSHARP_BUILD_SPEC.md` still said "TO DO. Nothing has been built yet" after the DLL shipped in `a5856a9`. It is now marked BUILT and reframed as the design record.

**Still open, deliberately:**

- **9 `player_maps/` reports are orphaned run artefacts** — nothing references them, and they regenerate from `src/RimMandrake/Utils/loop_run.py`. Harmless; delete if the folder ever gets noisy.
- **`src/Jawa/README.md` still says "four authored mods"** and its contents table omits `Jawa_Doctrine` and `WreckedMachines`. Not corrected here because that doc belongs to whoever owns the authored mods, and `WreckedMachines` is under active edit. Filed for CREATE in `TODO.md`.
- **`git config core.fileMode false` was set locally** (2026-08-11) because Drive's DrvFs mount flips permission bits, so **136 files showed as modified when only 7 had changed** — which is very likely why a thread reached for `git commit -a`. That config lives in `.git/config` and is **not committed**, so every clone and every other thread must set it themselves. Do it before trusting `git status`.

## 8b. Re-audit (2026-08-12)

The 2026-08-11 pass audited the **docs**. It did not re-walk the **tree**, so everything added in the day since was invisible here: four of the five skills, `src/RimMandrake/bridgetools/` entirely, two `runtime/` docs, `agents_def.md` + the four state files, and two of the six authored mods.

**The lesson, which is the reason this section exists:** a manifest is the one document that cannot be maintained by reading documents. It has to be diffed against `ls`. Doing that takes about two minutes:

```bash
find . -maxdepth 1 -not -name '.*' | sort     # root files + top-level dirs
ls skills/ src/ runtime/           # the three that grow fastest
```

If any of those prints something §7 does not name, this file is stale.

## 9. Removed (recover from git)

`Gravship_Campaign_Design_Notes.md`, `resource_catalogue.md`, `candidate_factions.md`, `faction_dossiers.md`, `in_game_verification_checklist.md`, `races.md` — folded into the owners above 2026-08-05/06.

`HANDOFF_2026-08-10.md` — deleted 2026-08-11 after its two unmigrated facts were moved out (see §8.2). It was a one-session cloud→local handoff; `CLAUDE.md` + this file replaced it.
