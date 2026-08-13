# STALE_FILE_AUDIT.md — what is dead, and the evidence

_Audit run 2026-08-13. **Nothing was deleted.** Deletion is the owner's call; this
file is the evidence for it. Method: reference graph over all 190 tracked
`.md`/`.html`, `git log -1` per candidate, and a read of each candidate's content —
not its title. Reverse direction checked: where content was duplicated **into** a
newer file, the table says which copy is the redundant one._

**Scope excluded, as instructed:** `.git`, `mods/mod_sources/` (gitignored,
430 MB / 17,046 third-party files — correctly handled, not itemised), and
shipping mod payloads under `custom_patches/`.

> ⚠️ **Read this before acting on the table.** Zero inbound references is
> *necessary but not sufficient*. Six files below have zero refs and are **alive**
> — entry points, colocated READMEs, and one brief whose work is still owed. Every
> DELETE row rests on a content read, not on a ref count.

---

## The four kinds

| kind | meaning |
|---|---|
| **1 DUPLICATED** | Content now lives elsewhere authoritatively; this is a stale second source. |
| **2 SUPERSEDED** | A later file, decision or restructure replaced it. |
| **3 SPENT ANALYSIS** | One-off investigation whose conclusion has already been acted on or written up elsewhere. |
| **4 ORPHANED** | Nothing references it, nobody owns it, subject finished or abandoned. |

---

## A. DELETE — high confidence

Sorted by confidence, highest first.

| file | kind | size | last touched | inbound refs | recommendation | evidence |
|---|---|---|---|---|---|---|
| `runtime/backups/TribalFurniture-strayAssemblies-2026-08-11/` (24 DLLs) | 3 | **19.4 MB** | 2026-08-11 `7693264` | **0** | **DELETE** (keep `MANIFEST.json`) | Its own manifest records every file as `"shipped_by_game": true, "byte_identical_to_game": true` — incl. a 15.7 MB `Assembly-CSharp.dll`. The trap it proved is already recorded; commit subject is *"Strip packaged base-game assemblies from three mods; **record the trap**"*. Restore path if ever needed: Steam re-verify the mod. |
| `runtime/backups/StrayBaseGameAssemblies-2026-08-11/` (3 DLLs) | 3 | **5.3 MB** | 2026-08-11 `7693264` | **0** | **DELETE** (keep `MANIFEST.json`) | Same commit, same manifest claim, same investigation. |
| `Utils/Jawa_Visual_Research_Dossier_v2_Image_Dense.pdf` | 4 | **47.8 MB** | added 2026-08-07 `b00fe37` | **0** | **DELETE** | Largest tracked file in the repo, referenced by nothing anywhere. Misfiled besides: `STRUCTURE.md` §7 says `Utils/` is "Tooling only", and its two companion research files *were* moved out to `reference/` on 2026-08-11 ("research, not tooling") — this one was left behind. `mods/dumps/README.md` already documents why large tracked binaries hurt: a push carries every seat's commits. |
| `runtime/logs/Player.2026-08-13_session2.log` | 3 | **1.1 MB** | `c4897d2` | 0 | **`git rm --cached`** | 🔴 **A closed decision that was never executed.** `CLOSED.md` records *"Tracking harvested game logs — rejected; `runtime/logs/` gitignored — `0d398c0`"*. But `git show --stat 0d398c0` touched **only `.gitignore` and `CLAUDE.md`**. The blob is still in HEAD: `git ls-tree -r HEAD -- runtime/logs/` returns it. `.gitignore:84` is inert against an already-tracked path. |
| `custom_patches/WreckedMachines/art_source/**/_superseded_pilot/` (4 PNGs) | 2 | **6.1 MB** | 2026-08-12 | 0 | **DELETE** | Directory name is the verdict. `MACHINES.md` marks all three tiers ✅ 4/4 validated against the accepted art beside these. |
| `agents_redesign_options.md` | 3 | 188 | 2026-08-13 `796f28f` | **0** | **DELETE** | *"Decision document — nothing here is adopted."* The decision has been taken **and implemented**: five seats live in `agents/`, queues split per seat in `queue/`, `agents_def.md` restructured. Its six open questions are all answered by what shipped. `DOC_BUDGET.md` rule 2 puts provenance in the commit, and `796f28f` holds it. |
| `image_request/codex_imagegen_origin_plan.md` | 2 | 241 | 2026-08-12 `8ead0ca` | **0** | **DELETE** | **Self-declared.** Line 3: *"⚠️ SUPERSEDED, 2026-08-12. Kept as the origin record — do not follow it."* It then lists five of its own claims as wrong and names `skills/generating-images/` as the replacement. Direction confirmed: the skill is authoritative (387 lines across `SKILL.md` + 2 references), this is the redundant copy. |
| `player_maps/{coastal_mesa,desert_flats,river_valley,volcanic_shelf}_improvement.md` + `coastal_mesa{,_v2,_v3}_loop_report.md` (8 files) | 4 | 576 | 2026-08-11 `b4e3c39` | **0 each** | **DELETE** | Already convicted by the repo itself: `STRUCTURE.md:246` — *"9 `player_maps/` reports are orphaned run artefacts — nothing references them, and they regenerate from `Utils/loop_run.py`."* Verified: `Utils/loop_run.py:119` writes `%s_loop_report.md`; `Utils/Map_improver.py:778/782` writes `%s_improvement.md`. Untouched since the bulk move. The matching `*_improvement.json` go with them. |
| `worldbuilding/biome_roster_for_review.html` | 2 | 210 | content 2026-08-04 | 1 (`desert_world_design.md:156`, past tense) | **DELETE** | Its stated purpose — *"decide how many columns the resource × terrain matrix needs"* — is a review that **completed**. Its ~37-biome disposition table is a strict subset of `worldbuilding/biome_and_fauna_roster.md` §2 (57 biomes, numeric commonality weights, 2026-08-13), which also carries the two cuts the HTML records. Re-point the one citation first. ⚠️ **Do NOT treat its sibling `resource_terrain_matrix.html` the same way** — see §D. |
| `custom_patches/WreckedMachines/art_source/AutomatedSmelter/BRIEF_{1_WRECKED,2_KLUDGED,3_REPAIRED}.md` | 3 | 214 | 2026-08-12 | 3/2/2 | **DELETE** | Art delivered (4/4 PNGs on disk per `MACHINES.md`), **and** they are regenerable output: each header says do-not-hand-edit, and `Source/briefs.py:173/219/259` writes all three. Deleting is free; recreating is one command. |
| `runtime/latency_3mod.json` | 2 | 98 | 2026-08-12 `6b65fb3` | **0** | **DELETE** | `skills/rimbridge/SKILL.md` §8 explicitly disowns it: *"The old '0.002 s per call' figure was measured on 3 mods, paused, and did not survive the full stack."* Its one surviving useful column is already inline in `runtime/map_authoring_decision.md`'s comparison table. **Keep `latency_568mod.json` and `latency_573mod.json`** — see §D. |
| `samuel_streamer_study/_targets.tsv` | 4 | 58 | 2026-08-11 | **0** | **DELETE** | Download worklist for a fetch that completed; `lists/` and `configs/` are its output. |
| `Utils/weapon_landscape.py` | 4 | 153 | 2026-08-13 | **0** | **DELETE** | Zero references anywhere, **and** the only script under `Utils/` missing from `Utils/README.md`'s 40-script index. |
| `runtime/rimtalk_analysis.md` | 2 | 122 | 2026-08-11 `b4e3c39` | 2 (`STRUCTURE.md`, `llm_stack_assessment.md`) | **DELETE** | `runtime/llm_stack_assessment.md` §0 literally opens *"Correction to `rimtalk_analysis.md`"* and overturns its central recommendation. The adoption question it existed to answer is settled in `mods/required_mods.md`. |

**Subtotal A:** 23 text files / **1,987 lines**, plus 33 binaries / **~78 MB**.

---

## B. MERGE-then-delete — real content to rehome first

| file | kind | lines | last touched | inbound refs | recommendation | evidence |
|---|---|---|---|---|---|---|
| `custom_patches/JawaIonWeapons/CSHARP_BUILD_SPEC.md` | 2 | 209 | 2026-08-11 | 1 (`STRUCTURE.md`) | **MERGE → `JawaIonWeapons/README.md`** | **Names its own successor and its own retirement condition.** Header: BUILT 2026-08-11, `a5856a9`; *"It is no longer a work order. **Retire it** if the DLL stays stable and the rationale migrates into the mod's own README."* DLL has been stable two days. Cleanest kind-2 in the audit. |
| `TODO.md` | 2 | **848** | 2026-08-13 `053b819` | 30 | **MERGE → `queue/*` + `CLOSED.md`** | Already owned as `queue/PROJECT.md` **P3**: *"848 lines holding roughly 14 live items; the rest is closed records and doctrine."* `agents_def.md:556` says it is being retired and *"file new work in `queue/`, not there"*. Section numbers are non-sequential and `13` appears **twice** (`:599`, `:634`). ⚠️ **Do not delete the closed ledger** — it is what stops items being re-filed; it belongs in `CLOSED.md`. ⚠️ It is also the **sole** inbound reference for `worldbuilding/faction_engine_gap_audit.md`; rehome that pointer or you orphan a live doc. |
| `mods/world_interest_and_mech_danger.md` | 3 | 210 | content 2026-08-03 | 5 | **MERGE → `required_mods.md` / `forbidden_mods.md`** | Self-labelled *"DRAFT candidate list… Nothing here is subscribed yet — this is the vetting pass."* The vetting concluded and the adoptions landed. ⚠️ Diff its ~15 verdicts against `required_mods.md` before deleting — not every candidate was traced. |
| `mods/def_override_clusters.md` | 3 | 81 | 2026-08-11 | 4 | **MERGE or regenerate** | Self-labelled *"Backlog note, not an investigation… Nobody has audited these yet"*, says to regenerate with `DefSet.duplicates()`, and was measured against the **562**-mod stack (live is 570). A stale measurement of a regenerable thing. |
| `worldbuilding/gravship_export_roundtrip.md` | 3 | 105 | 2026-08-13 | **0** | **MERGE → `V1_SCOPE.md`** | Its offline answer table was already promoted to `V1_SCOPE.md:135` (*"✅ ANSWERED, and answered offline… Resolved by CREATE in `b7e49db`"*), and its residual live test is duplicated into `NEXT_RELOAD.md:294,310`. Both halves now live in higher-traffic files and nothing links back here. Unique residue worth saving: the 7-row PASS/FAIL success-criteria table. |

**Subtotal B:** 5 files / **1,453 lines** (net ~1,400 after the ledger and the PASS/FAIL table are rehomed).

---

## C. KEEP-but-fix — alive, but actively misleading

These are not deletion candidates. They are listed because each one is a
**rule 0.6 instance** — true when written, still being read.

| file | defect | recommendation |
|---|---|---|
| `STRUCTURE.md` | 🔴 **The manifest describes a world that no longer exists.** Zero mentions of `queue/`, `agents/`, `CLOSED.md`, `DOC_BUDGET.md`, `V1_SCOPE.md`, `TODO_v2.md`, `skills/agent-messaging`, `worldbuilding/ship_build/`. Says "Five skills" (six exist), "four agents" / "Four threads" (five seats). `:196` points at **`AGENT_VISION_state.md`, which does not exist.** Seven `worldbuilding/` files are absent from it — six of them the newest work in the directory. Its own §8b warns *"a manifest is the one document that cannot be maintained by reading documents"*. | **Rewrite against `ls`, not against docs.** Highest-value fix in this audit. |
| `CLAUDE.md:56` | Still lists `# BRIDGE \| WORLD \| CREATE \| PROJECT` in the `set_agent_window.sh` example. WORLD is gone; VISION is missing. The script itself rejects `WORLD`. | Owner-only edit (rule 0.6). **Filed, not fixed.** |
| `agents_def.md:118` | Rule 0.5's routing table still says to file offline findings in **`TODO.md`**, contradicting `:556` in the same file (*"`TODO.md` is being retired… file new work in `queue/`"*). | Point rule 0.5 at `queue/<SEAT>.md`. |
| `NEXT_RELOAD.md` | 2,355 lines / 27 sections, many marked ✅ CLOSED / SETTLED with full bodies retained — exactly what `DOC_BUDGET.md` rule 3 forbids. Carries **37** `[WORLD]` tags for a seat that no longer exists. | Drain closed bodies to `CLOSED.md`; retag `[WORLD]` → `[OPS]`/`[VISION]` per the split already recorded in `queue/OPS.md`. |
| `mods/live_mod_inventory.md` | 🔴 **A stale snapshot that 11 docs cite as live authority.** Claims *"Single source of truth for mod identity… overrides all such claims elsewhere"*; generated 2026-08-10 against **562** mods. `ModsConfig.xml` says **570** today. Its own header says "Regenerate, don't hand-edit" — not done in 3 days. | Regenerate. Then **delete** the hardcoded counts in `required_mods.md:4` (461), `inventory/README.md:1`, `def_override_clusters.md:1,54`, `benign_log_errors.md:153,529,889,990`, `inspiration/README.md:80` rather than updating them — per the project's own rule 0.6 #1. |
| `worldbuilding/faction_engine_gap_audit.md` | **Two files are both titled "Stage 2"**, written 8 h apart. `TODO.md:39` points "Stage 2 ✅ done" at *this* one; `agents/VISION.md:77` and `queue/VISION.md:17` point at `faction_stage2_gap_audit.md`. Its §1 headline was resolved 2 h later by `faction_stage3_buildable_spec.md` §1; its §5 method findings were restated in the newer audit. **Still uniquely live:** §3 (goodwill has no mechanism — cited by `TODO.md:124`, tracked as VISION V10 / OPS O4, both OPEN) and §5's "the def dump is a POST-PATCH artifact" trap. | **Rename to disambiguate** and rehome §3 + the post-patch trap. Do not delete while O4 is open. |
| `mods/inventory/races_crossmod.md` + `.csv` | Header says *"GENERATED… regenerate with `gene_index.py` + `race_crossmod.py`"*. **Neither script exists anywhere in the repo.** Unreproducible output masquerading as regenerable — the one artifact here that a delete would genuinely destroy. | Fix the header, or restore the generators. **Do not delete.** |
| `skills/*.skill` | The packaged zips are **stale against their source directories**: `rimbridge.skill` is 11 h behind `skills/rimbridge/`, `rimworld-modding.skill` is 5 h behind. `skills/agent-messaging/` has **no `.skill` zip and no `.claude/skills/` symlink** — the newest skill is undiscoverable and unshippable. | `python Utils/package_skill.py --all`, and add the `agent-messaging` symlink. |
| `worldbuilding/resource_terrain_matrix.html` | **A load-bearing owner doc trapped in an undiffable format.** `desert_world_design.md:92` defers to it three times: *"The canonical column set is the 15-terrain / 6-band matrix in `resource_terrain_matrix.html`."* Families 1–10 have no markdown equivalent. | **KEEP.** Consider converting to markdown so it can be reviewed and diffed. |
| `Utils/_speakup_src_1p6/` (22 tracked XML) | Third-party mod source living in `Utils/` instead of `mods/mod_sources/`, which is why it escaped the gitignore that covers every other vendored tree. | Move under `mods/mod_sources/` (gitignored) or delete. |

---

## D. CHECKED AND ALIVE — do not re-audit these

Recorded so nobody spends the hunt again. Each was read, not just counted.

**Governance / root.** `CLAUDE.md` · `agents_def.md` · `concept.md` ·
`V1_SCOPE.md` · `REFRESH.md` · `CLOSED.md` · `DOC_BUDGET.md` ·
`rimworld_file_lore.md` · `save_authoring_pipeline.md` (last two pinned to root by
hard-coded `../<file>.md` paths in `Utils/Savegame_*.py`) · all 5 `queue/*.md` ·
all 5 `agents/*.md` · all 4 `AGENT_*_state.md`.
**`TODO_v2.md`** (1,095) is **alive** — deferred v2 bodies, explicitly *"Nothing
here is cancelled"*, cited from 6 files. **`context.md`** (919) is alive as
🗄️ ARCHIVE: 17 inbound refs, carries a correct do-not-consult banner, and
`STRUCTURE.md` §8.4 already ruled on keeping it.

**`skills/` — the healthiest directory in the repo; nothing dead.** The
de-duplication in `1bc12e7` was done correctly: all three former holders of the
messaging protocol (`CLAUDE.md:137-155`, `agents_def.md:350,384`, and all five
`agents/*.md` Communication sections) are now **pointers, not copies** — verified
by grep for `ten-line`, `from=`, `messaging`. No traps file was left empty by the
compression; `traps-diagnosis.md` is smallest at 41 lines and holds 4 real
entries. `minimal-load.md` is a correct split, still referenced, not an orphan.
`csharp-and-loading.md` is the only reference that did not get the compression
pass — a future compression candidate, **not** dead.

**Zero inbound refs but ALIVE — the six that prove ref-counting is insufficient:**

| file | why it is alive |
|---|---|
| `custom_patches/MissingArtFixes/Source/blast_door_frameasync_east_BRIEF.md` | **The work is still owed.** *"Three files owed"* — the three `SWDoorBlast*_FrameAsync_east.png` targets are absent from `Textures/`. The opposite of spent. |
| `worldbuilding/biome_and_fauna_roster.md` (451) | Newest design doc in the directory, 57-biome decision pass. Un-indexed, not dead — this is the clearest filing gap in the repo. |
| `runtime/art/smelter/README.md` | Records an 89→4-file / 143 MB→2.1 MB prune plus SHA-256 verification that nothing was lost. Provenance for the PNGs beside it. |
| `mods/dumps/README.md` | The clearest doc in the audit; states the regenerable/not test that the rest of the repo should be applying. |
| 7 colocated tool `README.md`s (`Utils/ilprobe`, `Utils/jawavoice`, `Utils/rimbench`, `JawaVoice`, `Jawa_Armoury`, `Jawa_Patches`, `WreckedMachines`) | Colocation is the reference. Deleting them is how a directory becomes unnavigable. |
| 48 `hand_authored_maps/World_*/README.md` | The **only** record of what each gitignored `.rws` payload is. Correctly designed. |

**Other confirmed alive.** `runtime/`: `build_plan.md`,
`map_authoring_decision.md` (9 refs, highest in the drawer), `droid_ruling.md`,
`ollama.md`, `llm_voice_preauthoring.md`, `divine_satiation_engine.md`,
`carbonite_trophy_mod.md`, `parked_mod_concepts.md`, `music_protocol.md` (its whole
job is a negative-result gate), `llm_stack_assessment.md` (1 ref, but §0 carries a
live reversal that exists nowhere else — a linking problem, not a deadness one),
`latency_568mod.json` and `latency_573mod.json` (the 4× discrepancy at higher mod
count **is** the refutation; the 573 file may be its only surviving evidence).
`runtime/rimbridge.md` is alive — it owns identity/provenance/deps, which
`skills/rimbridge/SKILL.md` deliberately excludes; but its §5.1 and §5.2 **are**
duplicated into the skill's `traps.md`, and **the runtime copy is the redundant
one** (the traps version is richer). Trim those two subsections, keep the file.

`worldbuilding/`: the three ship docs **do not overlap** — `ship_designs.md` owns
topology, `ship_deck_plan.md` the wing map/heat/repair gate,
`ship_distinctive_features.md` the identity layer; each declares its boundary and
the boundaries agree. **There has never been a `faction_roster_v1.md`** — the `_v2`
suffix is a pre-repo pass number, same for `Livestock_..._v1.md`. Also alive:
`desert_world_design.md` (25 refs, most-cited in the dir), `setting_physics.md`,
`balance_paradigm.md`, `biome_terrain_palette.md`, `Factory_lore.md`,
`jawa_xenotype_and_religion.md`, `jawa_crew_personas.md`,
`jawa_dialogue_source_audit.md` (consumed by shipping code), `Alien_Bestiary.md`,
`setup_checklist.md` (2 of 74 items done — barely started, not spent),
`faction_stage2_gap_audit.md`, `faction_stage3_buildable_spec.md`,
`faction_authoring_mechanism.md`, `ship_build/*` (generated, regenerated today),
the species-scale PDF (named as an owner doc by `STRUCTURE.md` §6).

`samuel_streamer_study/` is **not** spent, and its two indexes are **not**
redundant: `00_MASTER_INDEX.md` catalogues all **48** collections including those
never downloaded; `01_STUDY_INDEX.md` manifests the **24** actually on disk.
`02_TECHNIQUE_ANALYSIS.md` is the **source** that `Custom_World.md:3` defers to —
reverse direction: `Custom_World.md` is the summary, so 02 must survive.
`configs/*.zip` and `lists/*` are unreproducible primary source (Samuel strips old
collections' links).

`mods/`: `required_mods.md` (35 refs, most-cited doc in the repo),
`forbidden_mods.md`, `benign_log_errors.md`, `cherry_picker_killlist.md`,
`concept_defnames.md`, `armoury_keeplist.md` (proposal pending, nothing cut yet),
`outer_rim_cherrypick_list.md` (dormant — the sub-mod it specifies was never
built), `inventory/README.md`, `dev/RimDefDump/README.md`.
`custom_patches/`: `README.md`, and all four `WreckedMachines` docs — `V2.md` is
the **opposite** of landed (nothing in it shipped; the mod is absent from
`ModsConfig.xml` by design). `DesertVehicleReskin/Source/GEOMETRY.md` is
work-in-progress (spec 15 textures, 13 on disk).
`player_maps/README.md` and `player_maps/authored/coastal_mesa_rationale.md` are
alive — `STRUCTURE.md:165` carves the latter out explicitly.

---

## E. NEEDS THE OWNER

Each with the specific question. **I could not establish these are dead, so I am
not recommending deletion.**

1. **`promo/` — `Kolyska_pitch.html` (233 lines) + 2 concept PNGs (6.6 MB).**
   Zero inbound refs; added 2026-08-08 `f1eacb2`; a self-contained slide deck
   ending "Wake her up." The *ship* is very much alive (10 files mention it);
   nothing mentions the deck. → **Do you still want a pitch artifact for showing
   the concept to someone?** If yes it is alive and should be indexed; if no it is
   kind 4.

2. **`mods/inspiration/` — 3 files, 2,016 lines.** ⚠️ My subagent called this
   landfill on a zero-ref reading; **that was wrong and I am correcting it** —
   `STRUCTURE.md:186` *does* index it, as 📚 REFERENCE. So it is filed, just never
   consulted: nothing has been adopted from either dossier since 2026-08-11.
   → **Is the idea backlog still wanted?** It is the largest single block of
   low-traffic prose in the repo.

3. **`reference/rimworld_map_image_sources.md` (727 lines).** A 2026-08-05
   catalogue of *where to find* map imagery, written when web access was the
   constraint. `player_maps/README.md` records the session ended up synthesising
   maps instead, and authoring has since moved to RimBridge live-authoring. Only
   the manifest points at it. → **Is map-image sourcing a closed subject?**
   (Its sibling `rimworld_handcrafted_map_atlas.md` is clearly alive — it is the
   provenance for all 49 worlds in `hand_authored_maps/`.)

4. **`runtime/first_live_access.md` (127 lines).** Phases A and B are visibly
   done (bridge proven, `skills/rimbridge/` is the kit A4 asked for,
   `live_mod_inventory.md` is B's deliverable). I inferred Phase C completion from
   `V1_SCOPE.md`'s existence and date, **not** from an explicit statement.
   → **Is Phase C ("adapt the design") fully absorbed into `V1_SCOPE.md`?**

5. **`Utils/Map_improver.py` (826 lines).** `Utils/README.md:16` marks it
   *"⚠️ superseded heuristic improver"* and `:49` says *"kept for reference"* —
   a deliberate keep, not an oversight. But it is also the generator for four of
   the `player_maps/` artefacts in §A. → **Delete both, or keep both?**

6. **`mods/cqf_quest_types_explainer.md` (150)** and
   **`mods/sw_ingredients_inventory.md` (96).** Both self-declare a completed
   triage; both are evergreen *reference* rather than analysis with a spent
   conclusion, and `sw_ingredients_inventory.md` carries a load-bearing warning
   ("NOT 1.6 — DO NOT LOAD THESE SIX MODS") found nowhere else.
   → **Reference worth keeping, or spent?**

7. **`mods/github_issue_swcp_bundle.md` (132).** Upstream issue #7 is filed —
   that part is spent — but the tail holds an **unposted** correction comment.
   → **Was the correction posted?** One look at the issue settles it; dead the
   moment it is.

8. **`worldbuilding/ship_deck_plan_scale_map.png`.** Possible stale-diagram risk:
   `shipbuild.py` found an 18-machine corner-vs-centre offset on 2026-08-13 and
   the PNG predates it. → **Needs a visual check**, which I could not do.

9. **The two stray-assembly `MANIFEST.json` files.** I recommend keeping them —
   they are the work product that records the decision, at 4 KB against 24 MB of
   DLLs. → **Confirm you want the manifests retained without their payloads.**

---

## F. The total

| bucket | files | lines | bytes |
|---|---:|---:|---:|
| **A. DELETE, high confidence** — text | 23 | **1,987** | — |
| **A. DELETE, high confidence** — binary | 33 | — | **~78 MB** |
| **B. MERGE-then-delete** | 5 | **1,453** | — |
| **E. NEEDS THE OWNER** (if all ruled dead) | 11 | ~3,480 | ~6.6 MB |
| **Total if everything lands** | **72** | **~6,920** | **~85 MB** |

Against a corpus of 190 tracked docs / 46,288 markdown lines, buckets A+B alone
are **28 files and 3,440 lines — 7.4% of the prose and roughly 78 MB of git
history weight.**

**The single highest-value item is not in any of those buckets.** It is
`STRUCTURE.md` in §C: the manifest is the file everyone reads to find everything
else, and it currently does not know that `queue/`, `agents/`, `CLOSED.md`,
`DOC_BUDGET.md` or the fifth seat exist. A stale map costs more than a stale
document, because it is how people decide which documents to trust.

---

## G. Method notes, for whoever re-runs this

- **A concurrent commit landed mid-audit.** `Utils/whats_new.py` was untracked
  while five doctrine files referenced it — a genuine finding at 12:20 — and
  another seat committed it in `7e5b712` at 12:30 while this audit was running.
  **Re-verified before writing; the finding is resolved and is not in the table.**
  Five seats share this tree; re-check any finding older than an hour.
- **Bulk-move commits poison `git log -1`.** 21 of 31 `worldbuilding/` files carry
  the same `b4e3c39` / `76d7f64` timestamp — those are re-file commits, not
  content edits. Where git and a doc's internal "Updated" date disagree, trust the
  doc and say so.
- **Ref counts measure textual mention, not use.** A doc with 35 mentions may go
  unread; one with 0 may be opened daily. Every DELETE above rests on a content
  read.
- **Path-qualify greps for common basenames.** A bare `-F "README.md"` matches ~20
  unrelated files and manufactures false liveness.
