# Code and stray-file audit — 2026-08-20

**AUDIT ONLY.** Nothing in this report has been deleted or moved. Dead files go to
`D:\Luke\dev\Rimworld\infrastructure\disposing\` by `git mv` for a 7-day dwell, per
`infrastructure\disposing\README.md`.

**Scope:** `src\RimMandrake\Utils\` (105 top-level scripts + 3 subpackages),
`src\RimMandrake\bridgetools\`, `src\RimMandrake\mapsynth\`, `skills\*\scripts\`, and
every untracked / `.bak` / `.orig` / `__pycache__` file in the working tree.

**Sibling reports, do not duplicate:** `audit_2026-08-20_observed.md` covers
`observed\` and the `world\` payloads; `audit_2026-08-20_docs.md` covers prose;
`audit_2026-08-20_research_vendor.md` covers `research\` and `vendor\`.

## Method and its one calibration trap

Inbound references were computed from a single repo-wide token index
(`grep -rIoE '[A-Za-z0-9_.-]+\.(py|sh|ps1|html|slice)'`), self-references removed,
`vendor\` excluded. A reference from a **skill, a CLAUDE.md, a hook, or a queue file**
is live. A reference from **`infrastructure\disposing\*`, from a sibling audit report,
or from a directory README that merely indexes its own folder** is NOT — those are
inventory, not use.

🔑 **`src\RimMandrake\Utils\README.md` names only 17 of 105 scripts.** Absence from it is
therefore *no evidence at all* in this repo, and any audit that treats "not in the README"
as a death signal will condemn most of the live tooling. Every verdict below rests on
callers and docs, never on README membership.

## Table 2 — stray files

Sizes are bytes. "Ignored" = `git check-ignore` agrees. Note the `.gitignore` gained a
PRESWAP rule in `ee6f5b9` **during this audit**, so those three stopped being untracked
mid-sweep; they are still on disk.

| path | size | last touched | inbound refs | verdict | why |
|---|---:|---|---|---|---|
| `D:\Luke\dev\Rimworld\world\WORLDMAP_gen.rws.bak` | 14,175,759 | 2026-08-18 08:07 | none | **QUARANTINE** | Ad-hoc backup taken 8 min before the `.rws` it shadows. Untracked *and* not ignored (`*.rws` does not match `.bak`), so a blanket `git add` would put 14 MB in history forever. Biggest single stray. Already flagged in `audit_2026-08-20_observed.md`; same verdict, reached independently. |
| `D:\Luke\dev\Rimworld\world\relief.npz` | 172,405 | 2026-08-18 08:13 | `world_relief.py` (writer), `world_hydro/biomes/settle.py` (readers) | **DELETE** | Intermediate of the superseded `world_*.py` chain — see the ambiguity note below before acting. |
| `D:\Luke\dev\Rimworld\world\hydro.npz` | 271,211 | 2026-08-18 08:14 | same chain only | **DELETE** | As above. |
| `D:\Luke\dev\Rimworld\world\biomes.npz` | 106,982 | 2026-08-18 08:15 | same chain only | **DELETE** | As above. |
| `D:\Luke\dev\Rimworld\world\settle.npz` | 84,917 | 2026-08-18 19:03 | `world_settle.py` only | **DELETE** | Terminal output of the chain; nothing downstream reads it. |
| `D:\Luke\dev\Rimworld\world\discmap_520.npz` | 235,765 | 2026-08-17 21:56 | `world_relief.py` writes it as `discmap_%d.npz`; **no reader anywhere** | **DELETE** | A projection cache with no consumer at all — the clearest dead byte in `world\`. |
| `D:\Luke\dev\Rimworld\world\live_tiles_check.csv` | 1,342,873 | 2026-08-18 08:04 | `queue\DECIDE_ARCHIVE.md:496` | **KEEP** | ⚠️ Deliberate override of the "untracked = stray" rule. This is a **bridge read-back**: regenerating it costs a game load, and it is cited as evidence for "21,872 tiles, zero blank biome cells". Untracked means it is also the only copy. Concurs with `audit_2026-08-20_observed.md`: track it, do not sweep it. |
| `D:\Luke\dev\Rimworld\infrastructure\state\modlists\ModsConfig.PRESWAP.20260819_202911.xml` | 22,011 | 2026-08-19 19:03 | `modlist_swap.py` writes, nothing reads | **DELETE** | **Byte-identical to `ModsConfig.FULL.LATEST.xml`** (md5 `5a9a4d3a…`). Zero information. |
| `D:\Luke\dev\Rimworld\infrastructure\state\modlists\ModsConfig.PRESWAP.20260819_212042.xml` | 738 | 2026-08-19 20:19 | as above | **DELETE** | **Byte-identical to `ModsConfig.MINIMAL.xml`** (md5 `8652938e…`). |
| `D:\Luke\dev\Rimworld\infrastructure\state\modlists\ModsConfig.PRESWAP.20260819_212256.xml` | 22,011 | 2026-08-19 20:15 | as above | **DELETE** | Also byte-identical to `FULL.LATEST`. Three swaps produced three copies of two files. |
| `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\modlist_swap.py` *(the cause)* | 4,081 | 4h ago `8a4e5d2` | 6, incl. the modlists README | **KEEP — but fix** | 🔑 Protected tooling, so not for removal, but it is the **generator** of the row above: line 63 writes `ModsConfig.PRESWAP.<stamp>.xml` and **nothing ever prunes**. `ee6f5b9` gitignored the output; the accumulation on disk is unaddressed. A `keep newest N` in the writer stops this recurring. |
| `__pycache__` × 18 dirs (repo-wide, incl. `.claude\hooks\`, `skills\*\scripts\`, `design\Jawa\art\`, all of `src\RimMandrake\`) | 3.4 MB | continuous | n/a | **DELETE** | Gitignored (`__pycache__/`, `*.pyc`), pure bytecode cache. Includes `.pyc` for **deleted** sources (e.g. `Utils\__pycache__\apply_world`, `ashkarr_write`, `board`, `status`, `status_board` — five modules with no `.py` left), which is independent confirmation those five are already gone. |
| `D:\Luke\dev\Rimworld\vendor\mod_sources\ResearchReinvented-main\ResearchReinvented\Source\ResearchReinvented.csproj.bak` | small | third-party | none | **KEEP** | Inside `vendor\mod_sources\`, which `.gitignore` excludes wholesale. Upstream's own file — not ours to tidy. |
| `D:\Luke\dev\Rimworld\skills\*.skill` × 24 | 536 KB total | rebuilt on demand | `package_skill.py --all` | **KEEP** | Gitignored by design; regenerable zips of tracked folders. Working as intended. |
| empty dirs: `skills\generating-rimworld-sprites\references`, `skills\verify-before-you-escalate\references`, `src\Jawa\Jawa_Patches\Defs\GeneDefs`, `src\RimMandrake\WreckedMachines\Textures\Things\Building\Factories`, `infrastructure\disposing\RimMaster\spool\inbox` | 0 | — | — | **DELETE** | Git does not track empty directories, so these are pure working-tree residue from moves. Harmless but misleading — two of them advertise a `references/` a skill does not have. |

**Stray total: ≈ 16.4 MB**, of which `WORLDMAP_gen.rws.bak` alone is 14.2 MB (86%) and
`__pycache__` is 3.4 MB. Everything else together is under 900 KB. The `world\*.npz`
files matter for *tidiness*, not for space.

---

# Table 1 — scripts

## 1a. `src\RimMandrake\bridgetools\` — 51 scripts, 39 of them spent

This directory is **a session scratchpad that was committed, not a tool library**. The 39
spent one-shots come to ~110 KB total, so this is a tidiness question, not a size one.
Nothing here is broken: every import resolves and every input path exists.

**KEEP — daily (5):** `build.py` · `load_session.py` · `prove_new_tools.py` ·
`launch_and_wait.sh` · `shoot_planet.py`. All named in `skills\rimbridge\SKILL.md`,
`traps.md`, `NEXT_RELOAD.md` or `LIVE.md`.

**KEEP — occasional but real (7):** `prove_capture_restore.py` (drives production
`rimbench.TerrainPainter`, cited in the rimbench README) · `prove_set_terrain.py` (the
canonical read-before/read-after proof pattern) · `execute_ship_plan.py` (its
`ship_bridge.json` input exists) · `import_gravship.py` · `time_formation.py` ·
`c37_race_lineup.py` (re-runnable after any xenotype change) · `prove_world_lint.py`
(recalibrate when the linter changes).

| path | size | last touched | inbound refs | verdict | why |
|---|---:|---|---:|---|---|
| **35 spent one-shots**, e.g. `D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\prove_map_tools.py`, `prove_buildings.py`, `prove_prefabs.py`, `prove_prefab_diff.py`, `prove_pawn_identity.py`, `prove_pawn_gear.py`, `prove_pawn_allegiance.py`, `prove_p4.py`, `prove_connect.py`, `prove_social.py`, `prove_world_tools.py`, `prove_world_import.py`, `prove_world_links.py`, `prove_world_mutators.py`, `prove_world_objects.py`, `prove_world_add.py`, `prove_world_features.py`, `answer_owner_qs.py` | ~95 KB | 2 min – 5 days | 0–1 | **QUARANTINE** | 🔑 **The evidence they are safe to drop:** each one's finding is written into `infrastructure\state\observed\LIVE.md` — §193 (world tools), §257 (map/M1–M4), §272 (pawns/P1–P3), §321 (P4, connect_cells, rituals, non-square maps) — plus `design\Jawa\worldbuilding\WORLDMAP_BRIDGE_SURFACE.md`. The script is the derivation; the doc is the answer. |
| `…\prove_zones.py` · `prove_events.py` · `e1_verify.py` · `e1_raid_live.py` | 9,720 | 82–86 min ago | 0 | 🔴 **KEEP until harvested** | **The one real gap.** M4 (zones/gas/areas, commit `669be9e`) and E1 (weather/conditions/threats, a real 14-raider raid, commit `a5b0f2d`) exist **only in commit messages** — grep LIVE.md for "zone", "gas", "weather", "raid" and nothing relevant comes back. Harvest into LIVE.md first; *then* they join the row above. |
| `…\m1_shot.py` · `w6_shot.py` · `w6_shot2.py` | 4,109 | 2–3 h | 0 | **DELETE** | Superseded outright by `shoot_planet.py`, which alone carries the 4-try debug-log-close loop these three lack. Not merely spent — replaced. |
| `…\find_dry_row.py` · `diag_bounds2.py` · `diag_size.py` · `diag_connect.py` | 4,545 | 29 min | 0 | **DELETE** | `find_dry_row` superseded by `prove_connect2.py` painting its own testbed; the other three duplicate `diag_bounds.py`'s finding ("maps are NOT square", LIVE.md §321). |
| `…\p1_backstory.py` · `p2_social.py` · `p3_followup.py` · `p3_age_verify.py` · `prove_pregnancy.py` · `prove_social2.py` · `prove_connect2.py` · `m3_confirm.py` | ~12 KB | 2 h | 0 | **DELETE** | Narrowing *reruns* of a parent `prove_*.py` that reached the same recorded finding. The parent is the derivation worth keeping; these are the second and third attempts at it. |

## 1b. `src\RimMandrake\Utils\` — the world / map-authoring family

🔑 **Nothing here is dead by the no-worldgen ruling.** Both planet builders are
frozen-seed and single-planet — no `--seed`, no argparse, `world_relief.py` hard-codes
`SEED = 20260817` — so neither can roll an alternative world. That was the first thing
checked and it came back clean.

**KEEP — the live one-map loop (5):** `ashkarr_paint.py` → `ashkarr_settle.py` →
`worldgeom.py` → `worldmap.py` (decoders only; both `write()` methods now raise) →
`worldview.py`. Named in `CLAUDE.md` itself.

**KEEP — occasional but real (4):** `worldmap_review.py` · `worldmap_effects.py` (its only
consumer is `worldmap_review.py`, which is enough) · `ideology_palette.py` ·
`design_doc_render.py`.

| path | size | last touched | inbound refs | verdict | why |
|---|---:|---|---:|---|---|
| `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\world_relief.py` | 18,933 | 2 days `3fbfa91` | 9, **all inside the chain** | ⚠️ **QUARANTINE — see ambiguity §A** | Head of a closed, superseded second implementation of the painter. |
| `…\world_hydro.py` | 16,896 | 2 days | 3, chain only | ⚠️ **QUARANTINE — §A** | Steps 3–4. Output `hydro.npz` has no reader outside the chain. |
| `…\world_biomes.py` | 16,386 | 2 days `3fbfa91` | 4, chain only | ⚠️ **QUARANTINE — §A** | Steps 5–6. |
| `…\world_settle.py` | 14,393 | 2 days | 5, chain only | ⚠️ **QUARANTINE — §A** | Step 8 — and its own docstring records that step 7 was never done. |
| `…\world_graph.py` | 4,230 | 2 days `91ff9fa` | 9, chain only | ⚠️ **QUARANTINE — §A** | Adjacency graph read only by the four above and `world_shape.py`. |
| `…\world_shape.py` | 4,884 | 2 days `fc159d6` | 5, chain only | ⚠️ **QUARANTINE — §A** | Blob/despeckle helpers for that chain and nothing else. |
| `…\worldmap_prefill.py` | 32,843 | 4 days `d3ad2aa` | 4 | **QUARANTINE** | **Self-frozen 2026-08-16** — refuses to run without `--i-know-this-overwrites-the-owners-decisions`. Its output landed in `worldmap_elements.prefill.json` (296 keep / 52 no). A generator that has already been locked against re-running is spent by its own admission. |
| `…\biome_review.py` | 16,802 | 5 days `5c33807` | 5 | **QUARANTINE** | Review server; the decisions landed in `observed\inventory\decisions_biomes.json` (Aug 15) — which `.gitignore` explicitly negates back in as the owner's hand-made calls. The answers are safe, so the asking tool is spent. |
| `…\dump_vwel_tiers.py` | 7,030 | 4 days `9ab3906` | **0** | **DELETE** | Finding landed twice over: `observed\2026-08-13\dumps\vwel_tier_{salvaged,ultratech}.json`, feeding `design\Jawa\worldbuilding\ship_legacy_armoury.md`. No caller anywhere. |
| `…\set_planet_subcount.py` | 4,685 | 3 days `fb9c658` | 2 | **QUARANTINE** | A worldgen-*parameter* forcer. The preset path still exists, but the world is built and frozen — there is nothing left for it to act on. |
| `…\Map_synth.py` | 10,070 | 6 days `7e98004` | 1 (Utils README) | **QUARANTINE** | Fabricated practice base maps into `player_maps/` — **that directory does not exist**. Head of the abandoned map-improver line. |
| `…\mapkit.py` | 13,931 | 6 days `16bad27` | 7, all in-island | **QUARANTINE** | Library for the same abandoned line; every consumer is inside it. |
| `…\map_agent.py` | 31,218 | 6 days `16bad27` | 5, in-island | **QUARANTINE** | Perception/primitives/metrics for that line; findings landed in `mapsynth\runs\coastal_mesa_*` and `design\RimMandrake\map_authoring_decision.md`. |
| `…\author_coastal_mesa_terrain.py` | 21,555 | 6 days `7e98004` | **0** | **QUARANTINE** | Same island; output landed at `mapsynth\runs\coastal_mesa_terrain.*`. Largest zero-reference script in `Utils\`. |
| `…\map_loop_agent.py` | 11,844 | 6 days `7e98004` | 1 (Utils README) | **DELETE** | **Broken by construction** — ships a stub `call_llm` that raises, and was never wired to an endpoint. It has never been able to run. |
| `…\frame_lock_probe.py` | 5,324 | 6 days `7e98004` | 1 | **QUARANTINE** | One-shot probe; its finding is written into `design\RimMandrake\map_authoring_decision.md`, which is also its only referrer. |
| `…\bridge_latency.py` | 17,419 | 6 days `754e84f` | 2 | **KEEP** | Same one-shot origin, but `skills\rimbridge\references\map-authoring.md` cites it as a re-runnable measurement, not just a past result. |

## 1c. `src\RimMandrake\mapsynth\` — the gravship design line, largely settled

🔴 **Landmine before touching anything here:** `build_sheet_15.py`'s output is
**sha256-pinned at `330e6ff`** inside `src\RimMandrake\Utils\rimbench\shipbuild.py`'s
selftest. Regenerating it moves five machines and breaks a protected file. Also
`ship_designs.py` and `build_sheet_15.py` were committed **16 minutes before this audit** —
someone is actively in them.

**KEEP:** `ship_designs.py` (every other script imports its constants) ·
`build_sheet_15.py` (pinned, above) · `render_single.py` · `render_skeleton.py` ·
`render_build_sheet.py` (inputs all present in `runs\`).

| path | size | last touched | inbound refs | verdict | why |
|---|---:|---|---:|---|---|
| `D:\Luke\dev\Rimworld\src\RimMandrake\mapsynth\geom_check.py` | 1,366 | 6 days | 2 (README + a design doc) | **DELETE** | 🔴 **Provably cannot run** — loads `ship_grid.npy` and `placements.json`, and **neither file exists anywhere in the repo**. |
| `…\verify_coverage.py` | 1,849 | 6 days | 2 | **DELETE** | Same missing `ship_grid.npy`. |
| `…\render_ship.py` | 3,312 | 6 days | 1 (README only) | **DELETE** | Same missing `ship_grid.npy`. |
| `…\render_ship2.py` | 5,321 | 6 days | 1 (README only) | **DELETE** | Same, plus the missing `placements.json`. |
| `…\build_designs.py` | 39,847 | 6 days | 5 | **QUARANTINE** | Design #15 won; grids are in `runs\` and the export at `ship_build\exported\Gravship_v1.xml`. Largest spent script in the repo. |
| `…\ship_layout.py` | 2,176 | 6 days | 6 | **QUARANTINE** | The first hand-blocked 64×92 hull; `mapsynth\README.md` itself says it is superseded by `build_designs.py`. |
| `…\interior_fit.py` | 6,719 | 6 days | 3 | **QUARANTINE** | Pass 1; `runs\interior_fit_summary.json` holds the result and feeds pass 2. |
| `…\skeleton_15.py` | 9,468 | 6 days | 3 | **QUARANTINE** | Result in `runs\skeleton_15.json`. |
| `…\render_designs.py` | 5,489 | 6 days | 2 | **QUARANTINE** | The comparison sheet it makes is already rendered into `runs\`. |

## 1d. `src\RimMandrake\Utils\` — the rest

**KEEP — daily tooling (no action, listed so nobody re-audits them):** `game_paths.py`
(**22 inbound — the most-imported module in the repo**, including protected
`validate_patch.py`) · `def_inventory.py` · `def_diff.py` · `check_refs.py` (named in
`agents\POLICY.md`) · `check_sprite.py` · `check_git_locks.py` (**executed by
`.claude\hooks\set_session_title.py:251` on every session**) · `doc_budget.py` ·
`harvest_log.py` · `animal_inventory.py` · `animal_contact_sheet.py` ·
`extract_bundle_textures.py` · `cherrypick_build.py` · `gen_races_mod.py` (in flight, open
queue item) · `genome_scan.py` · `gravship_layout.py` · `validate_ideoligion.py` ·
`validate_save_artifact.py` · `weapon_tag_audit.py` · `rimbridge_client.py` ·
`rimworld_loadset.py` · `say.py` · `statusline.py` (wired into the harness) ·
`status_board.html` · `build_packageid_index.py`.

**KEEP — occasional but real:** `backup_rimsort_rules.py` · `build_jawavoice.py` ·
`jawaese.py` · `mod_inventory.py` · `modset_builder.py` · `patch_provenance.py` ·
`preload_check.py` · `extract_bundle.py` · `check_load.py` · `check_declarations.py` ·
`selftest_checkers.py` · `selftest_deploy_hold.py` · `shutdown_deploy.sh` ·
`cherrypick_review.py` · `genome_matrix_build.py` · `genome_art_cache.py` ·
`thing_contact_sheet.py` · `rimbridge_lineup.py` · `install_wt_seat_profiles.py` ·
`ilprobe\{il,meta,meta_core,xref,enumdump}.py` · all `jawavoice\*.py` (provenance headers
inside the shipped `src\Jawa\JawaVoice\Patches\*.xml`) · **all 13 `skills\*\scripts\*.py`**
— every one is named by its own `SKILL.md`.

| path | size | last touched | inbound refs | verdict | why |
|---|---:|---|---:|---|---|
| `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\fleet_toast.ps1` | 1,842 | bulk `8893c37` | **0, repo-wide, all file types** | **QUARANTINE** | The only true orphan. A Windows toast for a stalled seat; nothing ever wired it up — no `FleetToast` caller exists. |
| `…\fs_bench.sh` | 4,850 | 5 days `6a291e9` | **0** | **DELETE** | Ran once to settle "is WSL slow". **Its output is also gone** — no `fs_bench_*.txt` in `observed\resource_watch\` — and no doc cites the answer. Removing it loses nothing that exists today. |
| `…\ilscan.py` | 8,571 | 6 days `027572c` | **0** | **QUARANTINE** | Superseded by the `ilprobe\` package, which has a README and four design-doc citations. `ilscan.py` is the predecessor with neither. |
| `…\ilprobe\sigdump.py` | 4,167 | 6 days | **0 — not even its own package README** | **QUARANTINE** | The one file in `ilprobe\` nothing documents. Still runs (its DLL resolves), so this is orphanhood, not breakage. |
| `…\animal_live_diff.py` | 21,245 | 6 days `754e84f` | 2, prose only | **QUARANTINE** | **Explicitly superseded**: `def_diff.py`'s own header says it *generalises* this animals-only v1.0. Nothing imports it. |
| `…\Savegame_detailed_items.py` | 14,006 | 6 days | 2 | **QUARANTINE** | Findings written up in `design\RimMandrake\rimworld_file_lore.md`; save work now goes through `rimbench\savemap.py` and the rimworld-savegame skill. |
| `…\Savegame_ideoligions.py` | 15,210 | 6 days | 2 | **QUARANTINE** | Same doc; ideoligion reading now goes through `validate_save_artifact.py`. |
| `…\Savegame_mapview.py` | 14,098 | 6 days | 3 | **QUARANTINE** | Self-described "first-pass utility to confirm we *can* read the map". That question is closed. |
| `…\peers.py` | 6,707 | bulk `8893c37` | 1 (`set_agent_window.sh`) | **QUARANTINE** | 🔑 **Killed by doctrine, not by disuse.** Its entire purpose is enumerating peers to message, and agent-to-agent messaging is ruled OFF and hook-enforced (`.claude\hooks\block_peer_messages.py`). Its documented input `AGENT_*_state.md` no longer exists. Unpick the `set_agent_window.sh` reference first. |
| `…\loop_run.py` | 6,090 | 6 days | 3, self-referential | **QUARANTINE** | The LLM-in-the-loop executor behind `map_loop_agent.py`. Dead under the ONE-MAP ruling — there is no generated map left to iteratively improve. |
| `…\gen_droid_faction_sheet.py` | 7,788 | 3 days `db87d90` | **0 real** | **QUARANTINE** | Its output is frozen at `design\Jawa\worldbuilding\review\droid_faction_assignment.html`. (Its only "reference" is today's sibling audit report — which does not count.) |
| `…\gen_xenotype_contact_sheet.py` | 14,125 | 5 days | **0 real** | **QUARANTINE** | Output frozen at `review\xenotype_art_selector.html`. Keep only if those sheets will be re-cut. |
| `…\gen_race_faction_sheet.py` | 23,952 | 3 days `fb9c658` | 1 | **QUARANTINE** | Sheet produced, decisions frozen and already consumed by `apply_race_factions.py`. |
| `…\apply_race_factions.py` | 5,648 | 3 days | 1 (a provenance comment in `Jawa_Patches\Patches\VanillaFaction_Xenotypes.xml`) | **KEEP** | Spent, but cheaply re-runnable and re-run is the *correct* action if the A/S/R matrix changes. Its output is deployed. |
| `…\expand_jawavoice_conditions.py` | 2,823 | 5 days | 1, and that one is inside `infrastructure\disposing\` | **QUARANTINE** | A fan-out authoring helper; the expansion is already baked into the JawaVoice corpus. Its only referrer is itself already quarantined. |
| `…\thruster_placement_scan.py` | 6,104 | 5 days `e4be212` | **0** | 🔑 **KEEP** | ⚠️ **Deliberate exception to the zero-reference rule.** Its docstring: *"Keep it: the conclusion rests on a roof map that the export does not contain, and this script is the only record of how that map was produced."* Zero refs, spent, and still the sole surviving derivation of a live finding. |
| `…\wsl_monitor.ps1` · `wsl_watchdog.ps1` | 20,035 | 5 days | **0 each** | **KEEP — document instead** | The watch and alarm halves of a documented WSL-death incident pair. Real tools that nobody wrote down; they need a line in `Utils\README.md`, not a quarantine. |
| `…\xenotype_check.py` | 23,393 | 6 days `0cd0ec2` | **0** | **KEEP — document instead** | A real validator (defName resolution, `exclusionTags` collisions) against the live gene set; `observed\genome\genes.json` exists so it still runs. `skills\rimworld-xenotypes\SKILL.md` names `genome_scan.py`, `refresh.py` and `validate_patch.py` but **not this** — a documentation gap, not death. |
| `…\game_focus.py` | 5,360 | 6 days | 1 (`skills\rimbridge\SKILL.md`) | **KEEP for now** | Documents its own obsolescence in its header — *"the real fix is a preference, not this module"* (`runInBackground`). A candidate the moment the skill stops naming it. |
| `…\make_vehicle_mask.py` | 8,581 | bulk `8893c37` | 2 live callers | 🔴 **KEEP — but it is BROKEN** | Not a removal candidate; a **bug found during the sweep**. Line 67 inserts `src/RimMandrake/skills/generating-images/scripts` onto `sys.path` — **that directory does not exist** (the real one is repo-root `skills\`), so `import pnglib` at line 69 fails. This breaks its two callers, `src\Jawa\DesertVehicleReskin\Source\build_eopie_sled_{north,south}.py`. |

## 1e. `src\RimMandrake\` more broadly — clean

All twelve non-`Utils` subdirectories (`BlastDoorFrameAsyncFix`, `CereanManeFix`,
`GravshipAstronautFix`, `KotORBandolierNorthFix`, `MSEDroidFix`, `PhytokinBarkHeadFix`,
`ResearchKitEastFix`, `SauridFrillFix`, `StrandedQuest`, `ToolBeltFix`, `RimDefDump`,
`WreckedMachines`) are **referenced AND currently deployed** to
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\`. Nothing to reclaim.

---

# Ambiguities — do not act on these without the owner

### §A · The `world_*.py` chain: the code and the doc disagree

`skills\rimworld-world-editing\references\generating-a-world.md` line ~263 says
**"what survives is the front half"** and lists `world_relief.py`, `world_hydro.py`,
`world_biomes.py`, `world_settle.py`, `world_graph.py` and `world_shape.py` alongside
`ashkarr_paint.py` as the live painter.

**The code says otherwise.** `ashkarr_paint.py` imports exactly two modules —
`worldgeom` and `worldmap` — and recomputes relief itself. The six `world_*.py` files
import only each other. They are a **closed, superseded second implementation**, and their
`.npz` outputs (Table 2) have no reader outside the chain.

🔑 **One of the two is wrong and it is not safe to guess which.** Either the doc is stale
and eight files plus 872 KB of `.npz` are dead, or the chain is a deliberate second route
somebody still intends to use. **Fix the doc first; the deletion decision follows from it.**

### §B · The fleet / WSL-seat cluster is a closed island — and half the seats just retired

`fleet_toast.ps1` · `launch_fleet.ps1` · `install_fleet_shortcut.py` · `claude_bounded.sh`
· `claude-seats.slice` · `wsl_monitor.ps1` · `wsl_watchdog.ps1` · `fs_bench.sh` ·
`resource_watch.sh` reference **only each other**. Nothing in `skills\`, `design\`,
`infrastructure\` or `.claude\` reaches into the group — except `install_wt_seat_profiles.py`,
which `.claude\hooks\set_session_title.py` and `set_agent_window.sh` do use, so that one
is anchored and stays.

⚠️ **Two reasons not to sweep the island anyway.** First, `install_fleet_shortcut.py`
creates a **Windows desktop shortcut** — the owner may launch the fleet by double-clicking,
which no grep can see. Second, commit `8893c37` ("purge the retired seats") **retired four
of the eight seats 20 minutes before this audit**, so a launcher built for eight is stale
in a way that argues for *revision* rather than removal. **Owner's call.**

### §C · Two files exist twice, with different content

- `check_sprite.py` — `Utils\` vs `src\RimMandrake\WreckedMachines\Source\`, **different
  md5**. A live drift hazard, not a deletion candidate.
- `pnglib.py` — `skills\generating-images\scripts\` vs
  `src\RimMandrake\WreckedMachines\Source\`. Duplication, not deadness.

### §D · Four bridge findings live only in commit messages

`prove_zones.py`, `prove_events.py`, `e1_verify.py`, `e1_raid_live.py` — M4 (zones, gas,
areas) and E1 (weather, conditions, a real 14-raider raid). Grep `LIVE.md` for "zone",
"gas", "weather" or "raid" and nothing relevant comes back. **A commit message is not a
durable home.** Harvest into `LIVE.md`, then quarantine the four.

---

# Counts

| group | count | bytes |
|---|---:|---:|
| daily tooling (KEEP, no action) | 39 | — |
| occasional but real (KEEP) | 43 | — |
| spent one-shot (QUARANTINE) | **77** | ~430 KB |
| broken-and-unreferenced (DELETE) | **6** | ~24 KB |
| superseded duplicates (DELETE) | 15 | ~25 KB |
| KEEP despite zero references (deliberate) | 4 | ~55 KB |
| stray files | 40+ | **≈16.4 MB** |

**The six provably-broken files** — the only ones where "does it still run?" answers *no*:
`mapsynth\geom_check.py`, `mapsynth\verify_coverage.py`, `mapsynth\render_ship.py`,
`mapsynth\render_ship2.py` (all four load a `ship_grid.npy` that exists nowhere in the
repo), `Utils\map_loop_agent.py` (ships a `call_llm` stub that raises), and
`Utils\make_vehicle_mask.py` (broken `sys.path`, but it has live callers — **fix it, do not
move it**).
