# RESTRUCTURE_PLAN.md — executable migration to option B (revised)

Target chosen by the owner from `output/RESTRUCTURE_OPTIONS.md` §5 B.
**This document moves nothing.** Execution is `queue/PROJECT.md` P5.

Reference counts below are `output/RESTRUCTURE_OPTIONS.md` §4's baseline.
`python3 Utils/check_refs.py` is the measure. **Baseline re-measured for this
plan: 21 BROKEN, 153 UNVERIFIED across 194 docs (2395 path claims)** — lower than
the 25/160/2595 in `RESTRUCTURE_OPTIONS.md` §4, which has drifted. Re-measure
immediately before stage 0 and use that number, not this one.

---

## 1. Target tree

| dir | holds | Jawa/generic split |
|---|---|---|
| `design/` | free-form + templated design docs, inspiration imagery; concepts and definitions | **yes** |
| `src/` | source we author. Python is the working version; compilable source kept in lockstep | **yes** |
| `deployed/` | compiled mods, XML patches, key game config files copied from the game | **yes** under `mods/`; `config/` unsplit |
| `observed/` | game-state artifacts **tied to `deployed/`**. Datetime-stamped subdirs, stamped when the bridge first contacts a new live game | **no** — the stamp is the axis |
| `vendor/` | Steam content that is not ours: source + markdown wisdom on using those mods | **no** (owner's ruling) |
| `research/` | material not authored by us but summarised | **yes** (owner's ruling) |
| `infrastructure/` | project coordination, agent definitions, daily operations | **no** — proposed, see §3 |
| `infrastructure/state/` | current system state: locks, todo lists, resume/state files, queues | — |

**How the split is expressed:** two subdirectories, `Jawa/` and `RimMandrake/`,
directly beneath the top-level dir. Contents keep their existing names —
**no artifact is renamed by this migration** (owner's ruling; see §7).

**The promotion test, verbatim:** *"Am I likely to want this in a totally
unrelated playthrough, or will I have to fundamentally remake it — not just
reconfigure it?"* Reconfigure → `RimMandrake/`. Remake → `Jawa/`. Worked example:
`faction_authoring_mechanism.md` (the method) → generic; `faction_roster_v2.md`
(ten Star Wars factions) → Jawa.

---

## 2. Mapping — every current top-level dir and root file

### Directories

| current | → destination | refs | notes |
|---|---|---|---|
| `worldbuilding/` (most) | `design/Jawa/worldbuilding/` | 101 | fiction, ship, factions, xenotype, `ship_build/`, PNGs, `*.html` |
| `worldbuilding/Custom_World.md`, `faction_authoring_mechanism.md`, `balance_paradigm.md` | `design/RimMandrake/` | — | methods, reconfigurable |
| `worldbuilding/Factory_lore.md` | `vendor/wisdom/` | — | how to run VFE-Factory; about a mod, not about Jawa |
| `worldbuilding/star_wars_species_scale_reference_atlas.pdf` | `research/Jawa/` | — | 16 MB |
| `runtime/*.md` (generic) | `design/RimMandrake/` | 104 | `rimbridge`, `map_authoring_decision`, `music_protocol`, `ollama`, `llm_stack_assessment`, `llm_voice_preauthoring`, `rimtalk_analysis`, `beautiful_tilemap` |
| `runtime/*.md` (scenario) | `design/Jawa/` | — | `build_plan`, `first_live_access`, `carbonite_trophy_mod`, `divine_satiation_engine`, `droid_ruling`, `parked_mod_concepts` |
| `runtime/logs/`, `runtime/latency_*.json` | `observed/<stamp>/` | — | gitignored payloads |
| `runtime/backups/*ModsConfig*`, `Mod_*.xml` | `deployed/config/` | — | game config copied for tracking — exactly this tier |
| `runtime/backups/*-strayAssemblies/` | `vendor/salvage/` | — | 25 MB of salvaged game DLLs, not ours |
| `runtime/art/` | `src/Jawa/art_bench/` | — | gitignored raw/cut stages; see §3 |
| **`runtime/` is deleted by stage 5** | — | — | ratified as a drawer, `STRUCTURE.md` §7 |
| `mods/*.md` (decisions) | `design/Jawa/mods/` | 139 | `required_mods`, `forbidden_mods`, `cherry_picker_killlist`, `armoury_keeplist`, `world_interest_and_mech_danger`, `agent_supersession_audit`, `outer_rim_cherrypick_list`, `concept_defnames` |
| `mods/*.md` (mod wisdom) | `vendor/wisdom/` | — | `benign_log_errors`, `cqf_quest_types_explainer`, `def_override_clusters`, `github_issue_swcp_bundle` |
| `mods/inspiration/` | `research/RimMandrake/` | — | candidate dossiers |
| `mods/sw_ingredients_inventory.md` | `research/Jawa/` | — | |
| `mods/live_mod_inventory.md`, `mods/inventory/` | `observed/<stamp>/` | — | ⚙️ generated; `GENERATED_FROM.json` already stamps a loadset fingerprint |
| `mods/dumps/` | `observed/` | — | already the manifest pattern this plan generalises; `capture_manifest.py` → `src/RimMandrake/` |
| `mods/dev/RimDefDump` | `src/RimMandrake/RimDefDump/` | — | dev-only mod |
| `mods/mod_sources/` | `vendor/mod_sources/` | 0 tracked | 430 MB, gitignored |
| `custom_patches/Jawa_*`, `JawaVoice`, `JawaIonWeapons`, `DesertVehicleReskin` | `src/Jawa/` | 92 | folder names unchanged |
| `custom_patches/MissingArtFixes`, `WreckedMachines` | `src/RimMandrake/` | — | reconfigure, not remake |
| `bridgetools/` | `src/RimMandrake/bridgetools/` | 39 | assembly name `JawaBench.BridgeTools` **not** renamed |
| `Utils/` | `src/RimMandrake/Utils/` | **322** | **moves as ONE unit** — see §4 dep 6 |
| `Utils/Jawa_Visual_Research_Dossier_v2.pdf` | `research/Jawa/` | — | 47 MB; do **not** delete for size — §6 |
| `Utils/_speakup_src_1p6/` | `vendor/mod_sources/` | — | third-party `Defs/` + `Patches/` |
| `player_maps/*.py`, `authored/` | `src/RimMandrake/mapsynth/` | 54 | `authored/coastal_mesa_rationale.md` is hand-written design → `design/RimMandrake/` |
| `player_maps/*.png .json *_report.md` | `src/RimMandrake/mapsynth/runs/` | — | gitignore; not game state, so **not** `observed/` — see §3 |
| `savegame/*.rws` | `observed/<stamp>/` | 25 | untrack in the same stage |
| `savegame/*_items.md` etc. | `observed/<stamp>/` | — | already gitignored |
| `hand_authored_maps/` | `research/RimMandrake/hand_authored_maps/` | 6 | payloads already gitignored |
| `samuel_streamer_study/` | `research/RimMandrake/` | 11 | reusable technique |
| `reference/` | `research/RimMandrake/` | 9 | |
| `image_request/*.md` | `design/Jawa/art/` | 12 | commission briefs |
| `image_request/_review/` | `src/Jawa/art_bench/_review/` | — | gitignored |
| `agents/` | `infrastructure/agents/` | 36 | |
| `queue/` | `infrastructure/state/queue/` | **100** | |
| `output/` | `infrastructure/output/` | — | see §3 |
| `disposing/` | `infrastructure/disposing/` | 12 | |
| `skills/` | **PINNED AT ROOT** | 149 | owner gate, stage 9 — §4 dep 1 |
| `.claude/` | **PINNED AT ROOT** | — | fixed by the harness |

### Root files

| file | → | file | → |
|---|---|---|---|
| `CLAUDE.md` | **root, pinned** | `TODO.md`, `TODO_v2.md` | `infrastructure/state/` |
| `.gitignore` | **root, pinned** | `NEXT_RELOAD.md` | `infrastructure/state/` |
| `STRUCTURE.md` | `infrastructure/` | `OWNER_DECISIONS.md` | `infrastructure/state/` |
| `agents_def.md` | `infrastructure/` | `CLOSED.md` | `infrastructure/state/` |
| `DOC_BUDGET.md` | `infrastructure/` | `V1_SCOPE.md` | `infrastructure/state/` |
| `REFRESH.md` | `infrastructure/` | `AGENT_*_state.md` ×4 | `infrastructure/state/` |
| `concept.md` | `design/Jawa/` | `rimworld_file_lore.md` | `design/RimMandrake/` |
| `context.md` | **unplaced** — §3 | `save_authoring_pipeline.md` | `design/RimMandrake/` |

`Utils/Savegame_*.py` cite the last two as `../<file>.md` in **docstrings only**,
so they are movable — `STRUCTURE.md` §2 and §7 claim they are pinned by code, and
**that claim is wrong.** Stage 5 corrects it.

---

## 3. Unplaced — the question that settles each

| item | question |
|---|---|
| `skills/` | Is a 5-symlink re-point with a **silent** failure mode worth the tidiness? Default: leave pinned at root forever. |
| `deployed/` compiled mod DLLs | Track the binaries (the exact defect §6 names — they churn every build) or gitignore them and track only XML patches + config + the generated modlist? Recommend the latter. |
| `player_maps/` run outputs, `runtime/art/`, `image_request/_review/` | These are tool run-artifacts, not game state. Widen `observed/` to "generated artifacts" or keep them gitignored beside their generator in `src/`? Recommend the latter — `observed/` stays tied to a live-game contact. |
| `output/`, `disposing/` | `infrastructure/` or `infrastructure/state/`? Is a spent report "current system state"? Recommend `infrastructure/`. |
| `context.md` (🗄️ archive, 16 inbound refs) | `infrastructure/archive/` or straight to `disposing/`? |
| `infrastructure/` split | No Jawa/generic split proposed — coordination is singular. Confirm. |
| `mods/inventory/` | Generated from a mod set, not from a bridge contact. `observed/<stamp>/` (recommended — it already carries a loadset fingerprint) or a `src/` output dir? |

---

## 4. Hard dependencies that must survive

| # | dependency | handling | stage |
|---|---|---|---|
| 1 | `.claude/skills/*` — **5 relative symlinks** to `../../skills/<name>` | **Pin `skills/` at root.** Git stores a symlink as a blob of its target string, so `git mv skills/` does **not** update them; they break with **no error** — the harness just stops offering the skill. If stage 9 runs: `git mv`, then `ln -sfn ../../infrastructure/skills/<n> .claude/skills/<n>` for all five, in the same commit. | 9, gated |
| 2 | `Utils/deploy_custom_mods.py` `SRC_ROOT = ROOT/"custom_patches"` | **Not 1 line, contrary to `RESTRUCTURE_OPTIONS.md` §3** — the split puts mods under `src/Jawa/` *and* `src/RimMandrake/`, so `SRC_ROOT` becomes `ROOT/"src"` and the mod glob gains one level (`*/*/About/About.xml`). ~3 lines. Re-run `Utils/selftest_deploy_hold.py`. | 7 |
| 3 | Steam deploy targets in `deploy_custom_mods.py`, `game_paths.py`, `ilprobe/meta*.py`, `bridgetools/build.py` | Point **out** of the repo. Never change. | — |
| 4 | `.claude/settings.json` hooks → `${CLAUDE_PROJECT_DIR}/.claude/hooks/*.py` | `.claude/` is not moved. Unaffected. | — |
| 5 | Docs/skills invoke `Utils/*.py` **by path**: `refresh.py` ×26, `deploy_custom_mods.py` ×24, `whats_new.py` ×18, `doc_budget.py` ×10 | Mechanical `sed` over tracked `.md .py .sh .json` in the move commit, then `check_refs.py`. | 8 |
| 6 | **`Utils/` sibling imports.** 20 scripts carry a `sys.path` insert; `game_paths`, `mapkit`, `rimbridge_client`, `rimworld_loadset`, `jawaese` are imported by bare module name | **`Utils/` moves as ONE unit. Do not split its Jawa scripts out in this migration** — `jawaese.py`, `build_jawavoice.py`, `expand_jawavoice_conditions.py`, `jawavoice/` are flagged for a later split once the imports are packaged. | 8 |
| 7 | **`.gitignore` names eight directories this plan moves** — `mods/mod_sources/`, `runtime/{art,logs}`, `hand_authored_maps/**`, `disposing/*/`, `image_request/_review/`, `bridgetools/artifacts/` | Update `.gitignore` **in the same commit as each move**. Miss one and a 430 MB vendor tree becomes newly-trackable; one `git add` then sweeps it in permanently (§6). | every |
| 8 | `Utils/doc_budget.py` per-class patterns are rooted at the repo top (`queue/`, `agents/`, `AGENT_*_state.md`, `CLAUDE.md`) | Moving those files makes them silently **stop counting**. Update the patterns in the same commit; the check is that the file *count* does not drop. | 4 |
| 9 | `CLAUDE.md` at repo root | Claude Code auto-loads the root copy only. Never moved. | — |
| 10 | `Utils/Savegame_*.py` → `../save_authoring_pipeline.md` | Docstrings only. Cosmetic update. **Not** a hard dependency. | 5 |

---

## 5. Staged order

Each stage is **one commit** that leaves the repo working, ordered
lowest-risk-first with every code dependency last. **Run `python3
Utils/check_refs.py` and `python3 Utils/doc_budget.py` after every stage** — a
stage is not done until both are back at baseline.

| S | scope | refs | re-point | proves it landed whole |
|---|---|---|---|---|
| 0 | Scaffold the 7 top dirs + a `README.md` each stating its tier rule; `.gitignore` block for `observed/`; add the generated-modlist emitter (§6) | 0 | — | `harvest_log.py --emit-modlist` writes a manifest; no file moved |
| 1 | `research/` — `hand_authored_maps`, `samuel_streamer_study`, `reference`, `mods/inspiration`, the two PDFs | ~30 | `.gitignore` | old dirs gone, not drained: `ls hand_authored_maps` errors |
| 2 | `vendor/` — `mods/mod_sources`, `Utils/_speakup_src_1p6`, `runtime/backups/*-strayAssemblies`, the four wisdom docs | ~5 | `.gitignore` | `git status --ignored --porcelain \| grep -c vendor/` > 0 |
| 3 | `observed/` + `deployed/config/` — `savegame`, `mods/{dumps,inventory,live_mod_inventory}`, `runtime/{logs,latency,backups}`; **untrack the two `.rws`** | ~65 | `refresh.py`, `capture_manifest.py` output paths | `python3 Utils/refresh.py` runs; `git ls-files '*.rws'` empty |
| 4 | `infrastructure/` + `state/` — `agents`, `queue`, `output`, `disposing`, 12 root files | ~160 | `doc_budget.py` patterns, `.gitignore` | `doc_budget.py` lists the **same file count**, exit 0 |
| 5 | `design/` — `worldbuilding`, `runtime/*.md`, `mods/*.md`, `image_request/*.md`, `concept.md`. **`runtime/` ceases to exist** | ~250 | none (docs only) | `ls runtime` errors; `check_refs.py` back to baseline |
| 6 | `src/` low-risk — `bridgetools`, `player_maps`, `mods/dev`, art benches | ~105 | `bridgetools/build.py`, `loop_run.py` | `python3 src/RimMandrake/bridgetools/build.py` plan-only exits 0 |
| 7 | `src/` mods — `custom_patches` split into `src/Jawa/` + `src/RimMandrake/` | ~92 | `deploy_custom_mods.py` (dep 2) | plan-only run lists the **same mod and file count** as pre-move; `selftest_deploy_hold.py` passes |
| 8 | `src/RimMandrake/Utils/` — the whole of `Utils/` in one move | **322** | dep 5 sed sweep | `refresh.py`, `status.py`, `harvest_log.py --help` all exit 0 |
| 9 | `skills/` → `infrastructure/skills/` — **OWNER GATE, may never run** | 149 | 5 symlinks (dep 1) | `ls -L .claude/skills/*/SKILL.md` resolves all five |

Total ≈ 1180 references. Stages 0–5 are ~510 and touch **no code**.

---

## 6. The two modlists

Each top-level directory carries a modlist of the mods believed required for its
contents. `design/` will list many more than `deployed/`. **The two kinds are not
interchangeable.**

| | hand-authored | generated |
|---|---|---|
| where | `design/MODLIST.md`, `src/MODLIST.md`, `research/MODLIST.md` | `deployed/MODLIST.md` |
| what it is | a **statement of intent** — what this tier's contents assume exists | the **last runnable instantiation actually tested** |
| changes | slowly, by hand, in the commit that adds the dependency | only by a post-load harvest |
| format | table: `packageId \| name \| why this tier needs it \| confidence` | see below |

**`deployed/MODLIST.md` is GENERATED and must never be hand-written.** A
hand-written record of a measured event is the defect class this project spent a
day removing.

**Emitted from `Utils/harvest_log.py`**, as a new `--emit-modlist` flag. That
script is already the right place: `provenance()` opens `Config/ModsConfig.xml`,
`DefDump/manifest.json` and `Player.log` at exactly the post-load moment, and
today reads a **count** from each and throws the identities away. Import
`Utils/rimworld_loadset.py::build_load_set()` for the ordered identities rather
than re-parse. Wire the call into `skills/rimworld-load-round/SKILL.md` §8,
beside the existing `harvest_log.py` step — §8 has **no "record what was loaded"
step today**, which is the gap this closes.

Contents — header `<!-- GENERATED by Utils/harvest_log.py --emit-modlist. Never
hand-edit. -->`, then:

- `gameVersion` from the `RimWorld 1.` log line (`1.6.4871 rev591` today)
- `capturedUtc`, and the `observed/<stamp>/` dir this pairs with
- `modCount` **and** the loadset fingerprint (`refresh.py::loadset_fingerprint()`,
  sha256[:16] — it already computes this and stores only the hash)
- the ordered list: `loadOrder | packageId | name | workshopId`
- whether the def dump was armed; if not, say so rather than emit a short list

**Precedent, already working:** `mods/dumps/manifest.<modCount>.<date>.json` +
its `README.md` — the same idea at 144 KB per load, whose *"could a machine
regenerate this without a human decision?"* test is the rule `observed/`
generalises. Moves to `observed/` in stage 3.

### `observed/` payloads are gitignored — track only the manifest

Per `observed/<stamp>/`: track `MANIFEST.json` (mod set, game version,
fingerprint) and nothing else. Payloads — `.rws`, def dumps, logs, screenshots —
are ignored.

**Why the rule is about *adding*, not cleaning up.** `.git` is **275 MB** for a
repo whose text is a few MB. ~135 MB of that is **eleven binaries**, and 12 MB is
`promo/` — already **deleted from the tree and still permanent in history**.
**Untracking never shrinks history; only not-adding does.** Therefore: the 47 MB
dossier and the two saves are **sunk cost** — move them, never delete them for
size, which buys nothing and loses the file. The only thing that helps is
refusing the *next* payload. A `git filter-repo` rewrite is the sole real
recovery and is **out of scope** — it invalidates every seat's clone at once.

---

## 7. Deferred renames — not in this plan

The owner ruled: **convention on new work now, renames later.** New work only:
generic is **`RimMandrake.<name>`**, scenario-specific is **`Jawa.<name>`**.
The backlog item is `queue/PROJECT.md` P6. Measured scope, for when it is picked up:

| target | blast radius |
|---|---|
| `JawaBench.BridgeTools` → `RimMandrake.Bridge` | **14 tracked files.** Four identities must move together: csproj filename, `<AssemblyName>`, `<RootNamespace>`/`namespace`, and the deploy folder `JawaBench` (`bridgetools/build.py:59,73` → `<RimWorld>/BridgeTools/JawaBench/`). Not a mod — absent from `ModsConfig.xml`, so no load-order risk. |
| the `jawa/` tool namespace | **35 tracked files** repo-wide (17 in `bridgetools/` + `Utils/rimbench/` + `skills/rimbridge/`). Canonical definition is **17 `[Tool("jawa/…")]` attributes** in `bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`. Pattern is `jawa/<lower_snake>` with a **slash, never a dot** — a regex must not catch the `mandrake.jawa.*` packageIds. Three of the 35 are **generated data** (`runtime/latency_*mod.json`, `worldbuilding/ship_build/ship_bridge.json` carry tool names as JSON values), so the rename rewrites artifacts too. |
| the five `Jawa*` mod folders | ⚠️ **Correction to the stated basis: packageIds ARE at risk.** All five are active in the live `ModsConfig.xml` (lines 560–571 of a 575-entry ordered list): `mandrake.jawa.doctrine`, `mandrake.jawavoice`, `mandrake.jawa.armoury`, `mandrake.jawaionweapons`, `mandrake.jawa.patches`. A packageId rename is a **load-order edit at a specific slot**, not a text change, and must also be made in RimSort user rules. Still a cost question — but the cost includes a game-list edit, not just `sed`. The id scheme is **already inconsistent** (two flat, three dotted; folder names mixed camel/underscore), which is the real argument for doing it once, properly. |

**Stale count found while measuring, worth folding in:** `skills/rimbridge/SKILL.md:403`
says "all 14 `[Tool]` methods" and `references/capability-matrix.md:63` says
"the first 14"; the source now carries **17** (15 in a default non-GM build).

---

## 8. Rollback

A `git mv` is fully reversible. **The failure mode is a half-done rename** — a
directory drained of nine files out of ten, where every check still passes
because the survivors are the ones nobody references. Per stage, in order:

1. `git status --porcelain` shows only `R` lines plus the doc edits named in the
   stage. **Any bare `D` without a matching `A` is a half-done stage** — stop.
2. `ls <old_dir>` must **error**. A directory that still exists is drained, not
   moved. (Stage 5 is the sharpest: `runtime/` must be gone entirely.)
3. `python3 Utils/check_refs.py` — BROKEN back to the **pre-stage-0** number or
   lower. A rise is the count of references the stage forgot.
4. `python3 Utils/doc_budget.py` — exit 0, and the **file count must not drop**.
   A drop means a pattern in dep 8 stopped matching and a file silently left its
   budget class.
5. The stage's own runnable check from §5, column 6.

**To undo:** `git revert <stage-sha>`. **Never `git reset --hard`** — five seats
share this tree and another seat's commit may already sit on top.
