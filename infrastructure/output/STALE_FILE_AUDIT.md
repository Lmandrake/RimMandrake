# STALE_FILE_AUDIT.md — keep-or-delete candidates, post-restructure

> # 🔴 NOTHING HERE HAS BEEN DELETED, AND NOTHING WILL BE BY ANY SEAT
>
> **Deletion is the owner's call by standing rule.** This file is a list and an
> argument, nothing more. No file was moved, edited or removed to produce it.
> This exists so the owner can rule on `OWNER_DECISIONS.md` **#7** interactively.

_PROJECT, 2026-08-13. Replaces the pre-restructure audit disposed of today
(`infrastructure/disposing/STALE_FILE_AUDIT.md`, commit `faef9a7`) — every path in
that one was dead. **No path below was carried over from it.** Each was located by
`find`/`git ls-files` against the tree as it stands and its inbound references
re-counted from scratch._

---

## ⚠️ Read this before you read a single row: git dates are useless here

The repo was **re-initialised today** — `7e98004`, 16:02, *"Repo re-initialised:
option-B tier structure, history archived"*. All 152 commits carry today's date,
so the method the audit was supposed to use —

```bash
git log -1 --format=%ad --date=short -- <path>     # returns 2026-08-13 for EVERY file
```

— distinguishes nothing. **Every "last touched" column below is the filesystem
mtime**, which the move preserved and which ranges 2023 → today.

⚠️ **And in `design/` even mtime fails**: the restructure rewrote 74 of 79 tracked
mtimes to today. There, the only reliable age signal is the **date written inside
the document**, marked `(doc)` in the column. Rows sourced from a real post-re-init
commit are marked with the hash.

**So there is no mechanical staleness signal left in this repo.** Every verdict
below rests on reference-counting and on reading the file, not on a date.

The pre-restructure hashes those old docs cite resolve in
`infrastructure/archive/OLD_HISTORY.md`, not in `git`.

---

## The shape of the answer, before the detail

| | |
|---|---|
| Repo on disk | **1.2 GB**; **95.2 MB tracked** |
| Candidates flagged | **50 rows** across the four buckets |
| Tracked bytes implicated | **≈ 14.1 MB** — of which **8.3 MB is four `_superseded_pilot` PNGs and one bench directory** |
| Untracked bytes implicated | **≈ 17.9 MB** (one third-party `bin/Debug` tree, one 2.7 MB census) |
| Prose implicated | **≈ 5,900 lines** |

🔴 **The size story is not where the prose story is.** 8.3 MB of the 14.1 MB is
five image files nobody disputes. The *interesting* decisions — the inspiration
dossiers, `Map_improver.py`, the map-image catalogue — are worth **≈ 130 KB
combined**. Rule on those for tidiness, not for space.

⚠️ **Seven rows in the tables are marked UNSURE and give the evidence both ways,
plus three more inside CHECKED AND FINE.** Those ten are the ones to read slowly;
the rest are safe either way.

---

# DUPLICATED — two files holding the same content or the same answer

| path | size / lines | last touched | inbound refs | why a candidate | recommendation |
|---|---|---|---|---|---|
| `deployed/config/ModsConfig.before-tier-bridge.xml`<br>`deployed/config/ModsConfig.full-568.post-exit.xml` | 21,683 B each | 2026-08-13 15:31 | **0 each** | **md5-verified** `2db10983…` — three byte-identical files with `ModsConfig.full-568.2026-08-11.xml`. The dated one is the one `ls -t ModsConfig.full-*` finds. | **DELETE both aliases.** Keep `full-568.2026-08-11.xml`. 42 KB. |
| `deployed/config/ModsConfig.pre-missingartfixes.2026-08-12.xml` | 22,472 B | 2026-08-13 15:31 | **0** | md5 `8f18a7ae…` identical to `ModsConfig.full-573.2026-08-12.xml`. | **DELETE one.** Keep the `full-573` name — the deploy skill globs `full-*`. |
| `deployed/config/ModsConfig.STEP1-before-tailfix2-2026-08-11.xml` | 2,005 B | 2026-08-13 15:31 | **0** | md5 `33ff68b2…` identical to `ModsConfig.STEP1-44-all-suspects-2026-08-11.xml`. | **DELETE one.** |
| `deployed/config/ModsConfig.43-step1-final-2026-08-11.xml` | 1,962 B | 2026-08-13 15:31 | **0** | md5 `ba6ccd98…` identical to `ModsConfig.43-bubbles-working-2026-08-11.xml`. | **DELETE one.** |
| `deployed/config/userRules.580-artfix-rules-2026-08-13.json` | 14,508 B | 2026-08-13 17:19 | **0** | md5-identical to `deployed/config/rimsort/userRules.json`, which is the canonical path `backup_rimsort_rules.py:105` writes. The flat copy is a stray. | **DELETE the flat copy.** |
| `src/Jawa/art_bench/smelter/variant_rendered.png` | 486,541 B | 2026-08-12 | **0** (own README only) | md5 `65b29ecc…` — byte-identical to the **shipped** `WreckedMachines/Textures/…/Wrecked/AutomatedSmelter_south.png` *and* to `art_source/…/wrecked/AutomatedSmelter_south.png`. Three copies of one image; the bench README itself says the shipped copies are "where they actually live now". | **DELETE the bench copy.** |
| `src/Jawa/JawaIonWeapons/art_candidates/tatooine_JawaIonBlaster.png`<br>`…/core_BlasterBolt_Blue.png` | 7,718 B + 15,425 B | 2026-08-08 | **0 each** | Both md5-identical to the shipped `Textures/JawaIon/` versions — the *chosen* candidates, kept twice. | **DELETE both.** |
| `observed/2026-08-13_gravship_substructure_capacity.md` | 4 KB / 69 lines | 2026-08-13 18:41 | **0** | Same measurement as `observed/2026-08-13_gravship_capacity_ceiling.md` written **31 minutes later by a different seat** — identical `4057 / 633` and `SubstructureSupport 632.7954`, same screenshot. The ceiling doc is 130 lines and additionally rules out distance, second engine and power. Both findings already landed in `design/Jawa/worldbuilding/gravship_flight_invariants.md:157-163`. | **DELETE this one, keep the ceiling doc.** Two seats measured the same thing in the same hour — worth noticing on its own. |
| `skills/editing-images.skill` · `generating-images.skill` · `generating-rimworld-sprites.skill` · `rimbridge.skill` · `rimworld-modding.skill` | 4 KB / 23 KB / 19 KB / 37 KB / 110 KB — **194 KB total** | 2026-08-13 00:49 (×4), 07:13 | **0 each** | Zip build outputs of the sibling directories, and **all five have drifted**: `rimworld-modding.skill` differs from source in **8 of 11 files** (incl. `validate_patch.py`), `rimbridge.skill` in all 3. Source dirs were edited up to 18:44 today. Git keeps every version of a binary forever. | **NOT deletable as such** — `package_skill.py` states *"Writing the folder is NOT shipping the skill"*, so the archive is the install artifact. **Choose one: regenerate (`package_skill.py --all`) or untrack + gitignore.** Committing stale zips is the worst of the three. |
| `src/RimMandrake/MissingArtFixes/` (7 PNGs + 3 scripts + About) | ~60 KB | 2026-08-12 | 21 — but `src/Jawa/README.md:86` marks it *"Split into the four `*Fix/` mods below on 2026-08-13; still LIVE and deployed, retirement is sequenced by the owner"* | **All 7 textures md5-identical** to the split mods; two `Source/*.py` identical too. Old mod **and** all 8 split mods are enabled together in `deployed/config/ModsConfig.580-artfix-enabled-2026-08-13.xml`. | 🔴 **DO NOT DELETE — this is a ModsConfig decision, not a file decision.** Listed so the owner sees the duplication is real and the retirement is still pending. |
| `design/Jawa/worldbuilding/faction_engine_gap_audit.md`<br>`design/Jawa/worldbuilding/faction_stage2_gap_audit.md` | 12 KB / 210 lines<br>12 KB / 185 lines | 2026-08-12 (doc)<br>2026-08-13 (doc) | 1 — `TODO.md:39,129`<br>2 — `agents/VISION.md:77`, `queue/VISION.md:40` | 🔴 **Two "Stage 2" gap audits, both by PROJECT, one day apart, both auditing `faction_roster_v2.md` against the live `FactionDef` surface, and neither mentions the other.** Their findings differ, so it is not a byte dupe. **The real defect is that `TODO.md` and `VISION.md` each cite a *different* one as *the* Stage 2 answer.** | 🔴 **MERGE, do not delete blind.** `TODO.md:129` points specifically at the older doc's §3 goodwill evidence and §5 *"125 fields is a schema not a checklist"* finding, which the newer one does not carry. Fold §3+§5 into `faction_stage2_gap_audit.md`, dispose the older, fix `TODO.md:39`. **Which survives is secondary; two seats believing different files are authoritative is the thing to fix.** |
| `research/RimMandrake/hand_authored_maps/World_*/…/Download Instructions.txt` (9 files, 3 md5 groups) | 9.7 KB total | 2023–2026 (upstream) | **0** | Verbatim third-party boilerplate, duplicated inside each creator's distributed folder. | **KEEP ALL.** Their value is being unaltered; 9.7 KB. Listed only so nobody re-finds them. |

---

# SUPERSEDED — a newer file answers the same question better

| path | size / lines | last touched | inbound refs | why a candidate | recommendation |
|---|---|---|---|---|---|
| `src/RimMandrake/WreckedMachines/art_source/AutomatedSmelter/{kludged,wrecked}/_superseded_pilot/` | **6.19 MB** (4 PNGs; the two `_raw/AutomatedSmelter_east.png` alone are 2.86 MB + 2.20 MB) | 2026-08-12 01:08 | **0** | The directory name is the verdict. `MACHINES.md` records all three tiers 4/4 validated against the accepted art sitting beside these. The whole mod is parked to v2 per `src/DEPLOY_HOLD.txt`. | 🔴 **DELETE — the single highest-value item in the audit by MB.** Half the tracked bytes at stake are these four files. |
| `observed/2026-08-13_pre-restructure/live_mod_inventory.md` | **116 KB** / 1,488 lines | 2026-08-13 15:31 | **11** — six `design/Jawa/mods/*.md` open with *"LIVE-DATA OVERRIDE: …is authoritative for mod identity"* | ⚠️ **The worst file in the repo right now, and deleting it is the wrong fix.** `infrastructure/state/TODO_v2.md:906` already flags it: *"stale and it is a ⚙️ GENERATED file"* — it reports **562** active mods against an actual **580**, and undercuts Star Wars content by ~11 mods. Six design docs inherit the drift while calling it authoritative. | 🔴 **REGENERATE, do not delete.** Deleting breaks 11 refs and six "authoritative" claims; leaving it keeps six design docs pointing at wrong numbers. **Highest-value action in this audit that is not a deletion.** |
| `observed/2026-08-13_modset_census.md` + `observed/2026-08-13_modset_map.json` | 58 KB + 157 KB = **215 KB** / 780 + 4,347 lines | 2026-08-13 16:28 / 16:21 | 1 and 2 — only each other and the `.py` | Census of a **570**-mod set. The stack is now **580** (`inventory/GENERATED_FROM.json`, `refresh_all.log`, `dumps/manifest.580`). Its headline finding — `lee.theforce.lightsaber` listed-but-absent — is **explicitly reversed** at `infrastructure/state/queue/OPS.md:514`: *"Lightsabers restored: 15 lightsaber ThingDefs live after the owner's re-subscribe."* | **DELETE — but promote two paragraphs first.** Its method traps (`<packageId>` is **not** unique in `About.xml`; DLCs live under `Data\`, not `Mods\`) are durable and are in **no** skill. Move them into `skills/rimworld-start-prep/SKILL.md`, then delete. |
| `observed/2026-08-13_lightsaber_availability.md` | 16 KB / 299 lines | 2026-08-13 16:49 | **0** | Its verdict — *"the next load has zero lightsabers"* — was **falsified the same day**; 15 are live. Its durable half (a mod active-but-absent stays silent because siblings use `loadBefore`, not `modDependencies`) **already landed** in `design/Jawa/force_users_build_spec.md:28-54`. | **DELETE.** Finding is durable elsewhere, verdict is now wrong, zero things cite it. |
| `research/Jawa/sw_ingredients_inventory.md` | 11.4 KB / 96 lines | 2026-08-13 15:31 (path-fix only) | **2 real** — `design/Jawa/mods/outer_rim_cherrypick_list.md:5`, `design/Jawa/mods/required_mods.md:597` | 🔴 **Its loudest sentence is known-false.** The banner reads *"⚠️⚠️ NOT 1.6 — DO NOT LOAD THESE SIX MODS"*; `required_mods.md:590-603` records the owner's **2026-08-12 retraction** with on-disk evidence (Galactic Empire / Rebel Alliance / Separatists / Chiss all ship 1.6, and Galactic Empire was **adopted, 1.6 verified**). `required_mods.md:597` says outright this file *"has NOT been corrected."* | 🔴 **DO NOT DELETE — FIX.** Its body (the per-mod FactionDef/pawnkind/ThingDef census) exists nowhere else and is cited. Strike the banner, keep the census. **A wrong load-order warning is worse than a missing file.** |
| `src/RimMandrake/Utils/Map_improver.py` | 36,972 B / 826 lines | 2026-08-05 | **5, and all five are epitaphs** — `Utils/README.md:16` *"⚠️ superseded heuristic improver"*, `:49` *"kept for reference"*, `map_agent.py:8` *"The earlier Map_improver.py was wrong"*, `mapkit.py:6` back-pointer | Superseded by the `mapkit` + `map_agent` + `loop_run` + `map_loop_agent` quartet. **The coupling that made the last audit hesitate is now resolved**: `player_maps/` no longer exists anywhere in the tree (`find` returns nothing), so the artefacts it generated are already gone. | ⚠️ **UNSURE — owner's call, and this is one of the named #7 items.** *For:* successor shipped, outputs already deleted, zero functional callers. *Against:* two READMEs say "kept for reference" **deliberately**, and it is a coherent 826-line record of a rejected design. This was open question #5 of the last audit and is still unanswered. |
| `src/Jawa/DesertVehicleReskin/Source/art/raw/{sled_east_raw.png,sled_south_raw.png}` | 1.17 MB + 1.29 MB = **2.46 MB** | 2026-08-13 10:01 | 1 weak (`art/raw/README.md`) | A `_v2` exists for each, and the build pipeline consumes **neither** — `build_eopie_sled_south.py:9` reads the committed *cut* pair and says so: *"is committed, so this script is reproducible"*. | ⚠️ **UNSURE, leaning DELETE the two superseded originals.** Keep `sled_north_raw.png` and both `_v2` files until the owner confirms no re-crop is planned. |
| `src/RimMandrake/mapsynth/README.md` | 8 lines | 2026-08-05 | **0** | **Wrong-directory README.** Titled `# player_maps/ — practice base maps`, describes 4 map fixtures, and was dragged in from the deleted `player_maps/` during the restructure. `mapsynth/` actually holds 16 ship-design/render scripts, none of which it mentions. | **REWRITE, do not delete** — the directory needs a README; this one answers a question about a directory that no longer exists. |
| `design/Jawa/art/codex_imagegen_origin_plan.md` | 8 KB / 241 lines | 2026-08-12 (doc) | **0 anywhere** | **Self-declares supersession on line 3**: *"⚠️ SUPERSEDED, 2026-08-12. Kept as the origin record — do not follow it."* It lists four of its own mechanical claims as wrong and names the replacement — `skills/generating-images/`, which exists alongside `editing-images/` and `generating-rimworld-sprites/`. | **DISPOSE.** Lowest-risk deletion in the audit: the file itself says so, zero refs, and the corrected facts are in three live skills. If the origin record is wanted it belongs in `infrastructure/disposing/`, not `design/`. |
| `design/Jawa/worldbuilding/ship_build/exported/Gravship_v1_capture.png` | **283 KB** | `a12fe3a` "Re-export from a CLEARED map" | **0** | **One export revision behind its own subject.** `Gravship_v1.xml` and `Gravship_v1.png` were both re-exported at `9684fb6` (*"Cut two doors into the gravship and re-export — the hull was sealed"*); this capture was not. **It depicts the sealed-hull ship that no longer exists.** | **DISPOSE or re-capture.** A screenshot silently showing a superseded hull is exactly the failure mode this repo keeps flagging. |
| `design/RimMandrake/rimtalk_analysis.md` | 12 KB / 122 lines | 2026-08-09 (doc) | **1 real** — `design/RimMandrake/llm_stack_assessment.md` | `llm_stack_assessment.md` §0 is literally titled **"Correction to `rimtalk_analysis.md`"** and *reverses* its central recommendation (*"Recommendation reversed: adopt"*), written a day later against 28 mods read from disk rather than a Workshop-page survey. | ⚠️ **UNSURE — keep for now.** *For:* headline verdict overturned. *Against:* it is the only record of **why RimDialogue is delisted** and what vacated that slot, and the correction cites it by name — deleting it orphans that citation. **Annotate with a header pointer to the correction instead.** |

---

# SPENT — a report whose question is answered, or a plan already executed

| path | size / lines | last touched | inbound refs | why a candidate | recommendation |
|---|---|---|---|---|---|
| `observed/2026-08-13_graphic_multi_attribution.md` | 24 KB / 400 lines | 2026-08-13 16:38 | **0** | Textbook spent by the tier's own doctrine. Both its verdicts said *"waiver into `benign_log_errors.md` (draft below)"* — and **both landed**, at `vendor/wisdom/benign_log_errors.md` §1.12 and §1.13, with the same 16:38 mtime. `observed/README.md`: *"Commit the finding, ignore the log."* | **DELETE.** The finding is durable in `vendor/wisdom/`; this is the working paper. Cleanest spent report in the repo. |
| `observed/2026-08-13_mechanoid_removal_study.md` | 36 KB / 666 lines | 2026-08-13 17:20 | **0** | Its own header: *"Nothing was changed… This document is the entire output."* The plan was then **executed** — `queue/OPS.md:516` records *"the four removed mech mods took 110 `SkinDef`s with them"* in the 573→580 delta. A plan already carried out. | **DELETE or move to `infrastructure/archive/`.** ⚠️ First check its Cherry Picker schema section (read from the assembly) is captured in a skill — it currently is **not**. |
| `observed/2026-08-13_load_1730_triage.txt` | 8 KB / 38 lines | 2026-08-13 18:11 | **0** | Not a report — raw grouped `Player.log` lines (16 identical `Pawn_Melee_Punch_HitBuilding` entries and so on). This is the bottom-left cell of `CLAUDE.md`'s own table: unreproducible, but its value expires. `.gitignore:106` catches `*.log`; it slipped through by being named `.txt`. | **UNTRACK.** Findings, if any, belong in `benign_log_errors.md`. |
| `src/Jawa/DesertVehicleReskin/Source/REVIEW_all_three.png` + `REVIEW_sled_brown.png` | 272 KB + 176 KB = **448 KB** | 2026-08-13 | 3 — all **past-tense narrations** of the review (`AGENT_CREATE_state.md:29`, `queue/CREATE.md:87,125`) | The review completed: `src/DEPLOY_HOLD.txt` records the owner's verdict verbatim — *"Eopie is reviewed! Ship it!"* — hold lifted today. Both files regenerate in one command (`review_sheet.py:36`, `preview_tint.py:27` write exactly these paths). | **DELETE.** Regenerable, and the question they existed to answer is closed. |
| `src/Jawa/art_bench/smelter/{variant_flat,variant_painterly,_alltiers}.png` | 392 KB + 452 KB + 798 KB = **1.57 MB** | 2026-08-12 | **0** (own README only) | Unchosen variants from a style bake-off that **concluded** — the *rendered* variant won and shipped, and is already preserved byte-identically in `WreckedMachines/Textures/`. The README documents an 89→4 prune that stopped one step short. | **DELETE**, or keep exactly one as the style record. |
| `src/Jawa/JawaIonWeapons/art_candidates/core_{IonRifle,IonBlaster,HeavyIonRifle,BlasterBolt_Red}.png` | ~40 KB | 2026-08-08 | **0** — the dir is in `deploy_custom_mods.py:99` `EXCLUDE_DIRS`, so it never ships | Rejected candidates from a selection that concluded; `ThingDefs_JawaIonBlaster.xml:19` narrates the outcome. | **DELETE.** Small, but pure spent-selection residue. |
| `src/Jawa/JawaIonWeapons/CSHARP_BUILD_SPEC.md` | 12 KB / 209 lines | 2026-08-11 | 1 | **Names its own retirement condition in its header**: *"It is no longer a work order. Retire it if the DLL stays stable and the rationale migrates into the mod's own README."* DLL unchanged since 2026-08-12; a 115-line `README.md` already sits beside it. | **MERGE into `JawaIonWeapons/README.md`, then delete.** The stability half of its condition is met; the migration half has not been done. |
| `research/RimMandrake/samuel_streamer_study/_targets.tsv` | 7,372 B / 58 lines | 2026-08-02 | **0** | Literally a download worklist (`coll_num / title / label / kind / download_url`) for a fetch that **completed** — `lists/` and `configs/` on disk are its output. Its Drive URLs are a strict subset of `00_MASTER_INDEX.md`, which carries all 48 collections' links, so it is redundant even for a re-pull. | **DELETE.** |
| `research/RimMandrake/inspiration/gadget_and_utility_inspirations.md` | 38,735 B / 1,218 lines | 2026-08-11 11:48 | **1, weak** — its own `inspiration/README.md:9` | 🔴 **This is the "idea backlog" from decision #7.** Its question was answered in the same directory: `inspiration/README.md` carries a *"Decisions taken 2026-08-11"* table ruling on ten items (Muzzle Flash ENABLE, VWE Laser ENABLE, Gunplay REMOVED, Dedicated Turrets ADDED, Laser Cannon ADDED, Rimatomics offline-only, droid frameworks keep-both), and those conclusions landed in `required_mods.md`. **No `STRUCTURE.md` reference to this directory survives the restructure** — so it is now unindexed as well as uncited. | ⚠️ **OWNER CALL — leaning keep-but-demote.** *Against deleting:* the README explicitly keeps Rimatomics *"as a source of ideas and implementation patterns"*, and an open TODO (pare 82 droid pawns via RimBridge) still points at dossier content. **Safest cut: keep `README.md` — which holds every decision plus the measured install audit — and drop the two raw dossiers.** |
| `research/RimMandrake/inspiration/weapon_effects_research.md` | 28,558 B / 639 lines | 2026-08-11 11:49 | **1, weak** — own `README.md:8` | Same. All four of its "top teardown targets" were adjudicated in that table, and 40 of its 53 cited mods are *"not on this machine"*. | **Rule on it together with the gadget dossier — 66 KB for the pair.** Keep both or cut both. |
| `research/RimMandrake/reference/rimworld_map_image_sources.md` | **30,762 B** / 727 lines | self-dated 2026-08-05 | **0 anywhere** | 🔴 **This is the "map-image catalogue" from decision #7.** A dated catalogue of *where on the web to find RimWorld map screenshots* — Reddit JSON, Imgur API, Steam CDN pagination — written when web egress was the constraint. **No image-scraping ever happened**; the map corpus arrived as 44 `.rws` saves via Fetcher, and authoring has since moved to live RimBridge. Every link in it is a mutable third-party URL that decays anyway. | ⚠️ **DELETE unless the owner wants image-scraping reopened.** Honest counter-evidence: it is **not** superseded by its sibling `rimworld_handcrafted_map_atlas.md` — that answers *who authors maps*, this answers *where the pictures are*. If deleted, that specific answer is unrecoverable without re-doing the scan. |
| `design/Jawa/worldbuilding/gravship_export_roundtrip.md` | 8 KB / 105 lines | 2026-08-13 (doc) | **0** | A **pre-test spec with a 7-row success-criteria table**, and every gate in it has since been settled: `V1_SCOPE.md:251` — *"✅ Gravship round-trip — ANSWERED, and answered offline."* Its one flagged live question (item 6, "do floors survive?") is closed at `V1_SCOPE.md:182` — *"4,057 `terrainDef` cells survived the round trip."* The format it wanted to establish is now owned, source-cited and measured by `skills/gravship-layout/SKILL.md`. | ⚠️ **DISPOSE AFTER SALVAGE — do not just delete.** Its final section lists **five exporter constraints** (pawns/items are not exported; include Shelves or starting items may not spawn; pawnless rooms spawn fogged; every mod used becomes a hard dependency; preview screenshots must be placed by hand). **`skills/gravship-layout/SKILL.md` carries none of them** — verified by grep. Move those five lines into the skill first. |
| `design/Jawa/worldbuilding/biome_roster_for_review.html` | 24 KB / 210 lines | **2026-08-04** (genuine mtime) | **1** — `design/Jawa/worldbuilding/desert_world_design.md:156` | Its name says "for review" and the review **happened**: `desert_world_design.md` records *"Two biomes were CUT (user 2026-08-04)"*. A generated review artifact whose decision has landed. | ⚠️ **UNSURE, lean KEEP.** Still cited as the provenance of a locked directive (*"see biome_roster_for_review.html for the per-biome disposition table these directives came from"*) — deleting makes that dangle. It is machine-generated HTML in `design/`, so **the right move is probably a tier move, not a delete.** |
| `infrastructure/disposing/` — 8 docs + 2 scripts (`RESTRUCTURE_PLAN.md`, `RESTRUCTURE_OPTIONS.md`, `RESTRUCTURE_LOG.md`, `REF_AUDIT.md`, `STALE_FILE_AUDIT.md`, `agents_redesign_options.md`, `RimMaster.md`, `do_restructure.sh`, `fix_refs.py`) | 152 KB tracked | all landed today, **16:02–16:11** | 2–6 each, all from inside `disposing/` | Already ruled, already quarantined. | 🔴 **DO NOT RE-RULE. The 7-day dwell expires 2026-08-20.** Listed here only so the owner is not asked twice about the same files. `disposing/RimMaster/` (672 KB) is gitignored and goes with them. |

---

# ORPHANED — nothing references it and nothing plausibly will

| path | size / lines | last touched | inbound refs | why a candidate | recommendation |
|---|---|---|---|---|---|
| `src/RimMandrake/Utils/weapon_landscape.py` | 153 lines | 2026-08-13 | 🔴 **0 anywhere in the tree** — verified by an unfiltered grep, `.git` excluded | The only script in `Utils/` with literally no mention outside itself: no caller, no doc, no README row. The pre-restructure audit reached the same verdict and it survived the move unexecuted. | 🔴 **DELETE. Cleanest true orphan in the repo.** |
| `research/RimMandrake/hand_authored_maps/SickBoyWi_RimWorldMaps/bin/`, `obj/`, `*.pdb` | **15.2 MB — untracked/gitignored** | 2023-12-30 | 1, dismissive — `hand_authored_maps/README.md`: *"the historical blueprint-exporter C# project (no `.rws`, as expected)"* | The one repo of the 40-repo pull that yielded **zero maps**. What is on disk is somebody else's `bin/Debug` output, including a vendored copy of RimWorld's own **`Assembly-CSharp.dll` at 11.0 MB**, 20 Unity module DLLs, `.pdb`s and `.cache` files. | **DELETE the build output** (~15.2 MB, zero information). Keeping the ~220 KB of `Data/*KeyValues.cs` source is defensible; keeping the game's assembly under `research/` is not. **Largest single disk win in the audit.** |
| `observed/quicktest_terrain_top_250x250.json` | 116 KB | 2026-08-13 17:56 | **0** | **Untracked and NOT gitignored** — `git status` shows it as `??`, so the next blanket add sweeps it in. A terrain-band dump from a quicktest map destroyed the same evening; `observed/README.md` says tool run-artifacts *"live gitignored beside their generator in `src/`"*, and it also violates the `observed/<stamp>/` layout. | **Do not commit.** Gitignore it or move it beside `src/RimMandrake/Utils/rimbench/terrain.py`. |
| `src/RimMandrake/BlastDoorFrameAsyncFix/Source/REVIEW_before_after.png` | untracked | 2026-08-13 | **0** | Untracked review scratch left inside a shipped mod's `Source/`. Same `??` exposure as the row above. | **Delete on disk** if the review is done; costs nothing either way. |
| `src/RimMandrake/Utils/dump_map_terrain.py` | small | 2026-08-05 | **0** | Zero references. Part of the abandoned offline map-synthesis line; live map work moved to RimBridge. | ⚠️ **UNSURE, leaning delete — rule on it in the same breath as `Map_improver.py`.** Same family, same fate. |
| `src/RimMandrake/Utils/author_coastal_mesa_terrain.py` | — | 2026-08-05 | **0 inbound** (it *imports* `map_agent`; nothing imports it) | A one-shot authoring script for a single named fixture whose outputs live in gitignored `mapsynth/runs/`. Its sibling `mapsynth/authored/author_coastal_mesa.py` authors the same fixture from a different entry point. | ⚠️ **UNSURE.** Two scripts author one map; one is redundant. **Confirm which before deleting** — do not guess. |
| `observed/2026-08-13_modset_census.py` | 8 KB / 74 lines | 2026-08-13 16:28 | 1 (its own `.md`) | **Misplaced rather than stale** — a reusable tool living in the measurement tier, which `observed/README.md` forbids. Its target data is the superseded 570-mod set. | **Move to `src/RimMandrake/Utils/`** if the census will be re-run; delete with the census if not. |
| `vendor/wisdom/cqf_quest_types_explainer.md` | 16 KB / 150 lines | 2026-08-13 15:31 | **0** | Nothing links it — **but CQF is live**: both `design/Jawa/mods/required_mods.md` and `design/Jawa/worldbuilding/tile_augmentation_catalogue.md` discuss it, and the doc is keyed to `desert_world_design.md` §3E. It passes `vendor/README.md`'s own test for the tier. | 🔴 **LINK, DO NOT DELETE.** An unlinked live doc, not a dead one. |
| `design/Jawa/worldbuilding/ship_build/exported/JawaTestBarge.xml` | **92 KB** / 2,828 lines | `e265be3` "gravship-layout skill: author a ship as a FILE" | **0** | A throwaway test fixture from the commit that built the gravship-layout skill. **Its sibling `JawaTestSled.xml` IS referenced** — by `skills/gravship-layout/SKILL.md:103,114` and `src/RimMandrake/Utils/gravship_layout.py:323`, both naming `JawaTestSled` specifically. Nothing anywhere names the Barge. | **DISPOSE**, or wire it into the skill as the "large layout" fixture if that was the intent. 92 KB of unreferenced generated XML. |
| `design/Jawa/art/census_building_graphics.tsv` | **2.7 MB** | untracked | n/a | 🔴 **Untracked AND not gitignored** — `git check-ignore` returns nothing; `design/Jawa/art/.gitignore` covers only `seed/` and `*.png`. A 2.7 MB machine-generated census sitting one `git add -A` away from entering history permanently. It is output of `scan_graphics.py` (also untracked) — a measurement, which `design/README.md` explicitly excludes from the tier. | 🔴 **FLAG — gitignore it or move it to `observed/`.** Not a deletion decision; a "do not let this into history" decision. |
| `design/Jawa/worldbuilding/ship_build/exported/Gravship_v1.png` | **1.3 MB** | `9684fb6` | **0** | 1.3 MB image with zero inbound references. Its companion `Gravship_v1.xml` **is** referenced (`V1_SCOPE.md:176`, `skills/gravship-layout/SKILL.md:31`), so the XML is live; only the PNG is unreferenced. | ⚠️ **UNSURE.** It is the visual record of the current exported ship, which has real value even unlinked. **Either link it from `V1_SCOPE.md` row 8 beside the XML, or drop it** — leaving a 1.3 MB unreferenced render is the worst of the three. |
| `infrastructure/state/CREATE_TEST_PLAN.md` | 9 KB / 160 lines | 2026-08-13 | 🔴 **0 anywhere** | Zero inbound refs — **and that is the bug, not the verdict.** Its own header says *"Written because I owed it at deploy time and did not send it… BRIDGE drives — I do not connect."* It is a live test plan for material already deployed, and **the seat that must execute it has no pointer to it.** | 🔴 **NOT STALE — REFERENCE IT.** Add it to `queue/BRIDGE.md` and `NEXT_RELOAD.md`. Filed as a finding, not a deletion. |

---

## 🔴 Four things this audit found that are NOT stale files, and matter more than most rows above

0. **Ten files in `design/` violate `design/README.md`'s own exclusion rule, and
   "misfiled" looks identical to "stale" from a ref-count table.** That README —
   38 lines, written today — says *"**Anything a machine generates.** If a script
   writes it, it is not design"* and *"**Measurements.** …is `observed/`."* The
   violators, all generated, none stale:

   `design/Jawa/worldbuilding/ship_build/{ship_tiles.json (628 KB), ship_bridge.json (36 KB), def_sizes.json, ship_build.md}`
   — all emitted by `src/RimMandrake/Utils/rimbench/shipbuild.py`, and
   `ship_build.md` says so in its own header (*"Generated by… Regenerate, never
   hand-edit"*); the five files in `ship_build/exported/` (live-game exporter
   output); `design/Jawa/data/mech_inventory.json` (126 KB, committed today in
   `67a3072`, zero inbound refs, a measurement of the live game); and
   `biome_roster_for_review.html` + `resource_terrain_matrix.html`.

   🔴 **Raise this before any deletion pass.** "Move to `observed/`" and "delete"
   are indistinguishable in a reference table and are very different actions.



1. **`observed/2026-08-13_pre-restructure/` is not a snapshot of the old tree.**
   The name is an artefact of the restructure script — `disposing/fix_refs.py:27`
   sets `STAMP = "observed/2026-08-13_pre-restructure"` and swept every old path
   into it. **35 files across `design/`, `infrastructure/` and `research/` point
   inside it, including `infrastructure/REFRESH.md:18` for the live
   `GENERATED_FROM.json` stamp.** It is the *current* generated-data home under a
   misleading name. **Anyone auditing on the name alone will delete live data.**

2. **`infrastructure/state/EXPECTED_FAILURES_next_load.md` has a blank results
   table — and its load already happened.** The file was written before the
   next cold load; that load ran at **17:30** and was harvested at 18:11
   (`observed/2026-08-13_load_1730_triage.txt`). The three-row Results table at
   the foot is still empty. The owner granted the three-assemblies waiver *on
   the condition that these signatures be checked*. **Not stale — unfinished.**

3. **`infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md:139` and
   `NEXT_RELOAD.md:614` both cite `dumps/defnames.573.2026-08-13.json`, which
   does not exist** — `queue/OPS.md:530` records it was deleted (`262666b`) and
   that the reasoning was wrong. Only `defnames.580` remains.

   Supporting: `check_refs.py` currently reports **789 BROKEN, 232 UNVERIFIED
   across 221 docs**. Most of the commit-hash failures are expected (the re-init
   moved them to `OLD_HISTORY.md`), but the **path** failures are restructure
   fallout worth a sweep — e.g. `src/RimMandrake/Utils/README.md` cites
   `../custom_patches/`, `../player_maps/` and `../mods/dev/RimDefDump`, none of
   which exist.

---

## The owner's four named #7 items — where they actually are now

| named in decision #7 | verdict |
|---|---|
| **the pitch deck** (`Kolyska_pitch.html` + concept PNGs) | 🔴 **NOT IN THE REPO — nothing to rule on.** No `promo/` directory exists anywhere; `find` for `*pitch*` outside `vendor/` returns nothing; `git log --all -- '*Kolyska_pitch*'` is **empty** (it was never tracked); `.gitignore` has no `promo`/`pitch` entry. Only two `.html` files exist in the whole repo, both in `design/Jawa/worldbuilding/`. It was working-tree-only and it is gone. |
| **the idea backlog** | `research/RimMandrake/inspiration/` — 3 files, 2,016 lines, 73 KB. Filed under SPENT above. |
| **the map-image catalogue** | `research/RimMandrake/reference/rimworld_map_image_sources.md` — 727 lines, 30 KB. Filed under SPENT above. |
| **`Map_improver.py`** | `src/RimMandrake/Utils/Map_improver.py` — 826 lines, 36 KB. Filed under SUPERSEDED above. Still the same unanswered question as last time. |

⚠️ **The "~85 MB" in decision #7 does not survive re-measurement.** It was
dominated by the pitch deck's PNGs, which are not in the repo. The four named
items now total **≈ 140 KB**. The MB is elsewhere, in rows the owner has not seen
before.

---

## CHECKED AND FINE — examined, NOT stale, do not re-check

**Tier and structure docs**
- `infrastructure/README.md`, `STRUCTURE.md`, `DOC_BUDGET.md`, `REFRESH.md`, `agents_def.md` — 9–38 inbound refs each, all current. *(Two cosmetic drifts noted, not staleness: `infrastructure/README.md` says "the four `AGENT_*_state.md`" when there are five, and `CLAUDE.md:109` lists the seats as `BRIDGE | WORLD | CREATE | PROJECT` — there is no WORLD seat; `agents_def.md:20-24` and `infrastructure/agents/` agree the roster is `BRIDGE | OPS | CREATE | VISION | PROJECT`.)*
- `infrastructure/agents/*.md` (5) vs `state/AGENT_*_state.md` (5) vs `state/queue/*.md` (5) — **not duplication.** Cleanly separated: identity / live state + socket address / work queue. Verified by reading all three PROJECT files.
- `infrastructure/state/TODO.md` (965 lines) vs `TODO_v2.md` (1,168 lines) — **not duplication.** A deliberate v1/v2 split made today when the scope line was drawn; `TODO_v2.md`'s header says so and `TODO.md` explains the three-way distinction against `NEXT_RELOAD.md` and `parked_mod_concepts.md`.
- `infrastructure/archive/context.md` (187 KB) and `OLD_HISTORY.md` (79 KB) — both self-label as archive with an explicit "do not consult for current state" banner, and `OLD_HISTORY.md` is the **only** resolver for the 77 pre-re-init commit hashes cited across the repo. Keep both.
- `infrastructure/output/README.md`, `infrastructure/disposing/README.md` — the doctrine this audit is judged against.
- `design/README.md`, `research/README.md`, `src/README.md`, `deployed/README.md`, `observed/README.md`, `vendor/README.md` — tier charters, all cited from `STRUCTURE.md`.

**Live state**
- `infrastructure/state/V1_SCOPE.md` (42 refs), `NEXT_RELOAD.md` (38), `TODO.md` (40), `OWNER_DECISIONS.md` (16), `CLOSED.md` (15) — the spine. Over budget, not stale (see below).
- `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` — ratified by VISION today and marked EXECUTE. Live work.

**`observed/`**
- `observed/2026-08-13_gravship_capacity_ceiling.md` — newest file in the tier and **newer than** the invariants doc it fed; its section on writing the BG setting has not landed yet.
- `observed/2026-08-13_ion_weapon_live_test.md` — `queue/OPS.md:510` calls it *"the only v1 item whose proof is a screenshot rather than a log line, and it always will be."*
- `observed/2026-08-13_HAR_pregnancy_patch_failure.md` — spent as a task, **live as a citation**: `harvest_log.py:170` cites it by path as the evidence for `baseline 1`.
- `observed/evidence/*.png` (3.1 MB) — sole evidence for live claims; `observed/README.md` forbids deleting a payload for size.
- `observed/2026-08-13_pre-restructure/dumps/manifest.{573,574,580}.json` (428 KB) — zero refs by filename, but `dumps/README.md` argues each is the only record of what a given load built, and the next load overwrites it.
- `observed/2026-08-13_pre-restructure/dumps/defnames.580.2026-08-13.json` (**2.55 MB**, largest tracked file in the tier) — `queue/OPS.md:549` records the deliberate reversal *"defnames.580 is now COMMITTED."* Keep; revisit only if repo size becomes the constraint.
- `observed/2026-08-13_pre-restructure/inventory/*.csv` + `contact_sheets/` (~19 MB tracked) — regenerated 19:03 **today** by `refresh.py`; cited 3× by `design/RimMandrake/balance_paradigm.md`.
- `observed/2026-08-13_refresh_all.log` (316 KB) — gitignored. Correct handling.
- `observed/2026-08-13_log_harvest_1004.md` — **UNSURE, leaning keep.** Operationally superseded by the 17:30 load, but three sibling `observed/` docs cite it by path (§c1/§c2/§c3).
- `observed/2026-08-13_vwel_armoury_dump.md` — **UNSURE, evidence both ways.** 0 inbound refs; it claims to answer `design/Jawa/worldbuilding/ship_legacy_armoury.md`, but that doc (16:45) predates the dump (17:09) and does not cite it. Either the answer has not been folded in (keep, action owed) or it went into `force_users_build_spec.md:1049` (spent). **Resolve before acting.**

**`src/` and `deployed/`**
- `deployed/` is **not** a copy of `src/` — it holds only `config/`. No src↔deployed mod duplication exists.
- All 8 art-fix mods, `Jawa_Patches`, `Jawa_Armoury`, `Jawa_Doctrine`, `JawaVoice`, `JawaIonWeapons`, `RimDefDump` — enabled in the current `ModsConfig`; the game loads them. Committed `Assemblies/*.dll` are shipped content, not build output.
- `src/Jawa/DesertVehicleReskin/Source/art/eopie_pair_gen*.png` (3.0 MB) and `src/Jawa/Jawa_Patches/Source/claim_rumour_raw.png` (2.00 MB) — **deliberately committed for reproducibility**; the build scripts read them by path. Load-bearing despite size.
- `src/RimMandrake/Utils/backup_rimsort_rules.py` — 0 refs, **not stale**: it is the sole producer of `deployed/config/rimsort/userRules.json`, which was written at 17:19 today. The textbook "unreferenced by docs ≠ dead" case. Add a README row instead.
- `src/RimMandrake/Utils/loop_run.py` — actively cited as the fallback by `map_loop_agent.py:67,268`. Its `player_maps/` reports are already gone; the executor is not.
- `src/RimMandrake/Utils/{show.sh,refresh.py,peers.py,whats_new.py,doc_budget.py,mapkit.py,set_agent_window.sh,harvest_log.py,deploy_custom_mods.py}` — 9–136 inbound refs each. Core tooling.
- `src/DEPLOY_HOLD.txt` — live input to `deploy_custom_mods.py`, validated by `selftest_deploy_hold.py`.
- `deployed/config/` — the ~20 `BEFORE-*`/`STEP1*`/`MIN2*`/`43-*` bisection snapshots (~150 KB) beyond the exact duplicates listed above: **keep for now.** `skills/rimworld-deploy/SKILL.md:77` and `agents_def.md:202` both run `ls -t deployed/config/ModsConfig.full-*.xml | head -1`; deleting the wrong file breaks a documented command.
- `obj/`, `bin/`, `__pycache__/`, `mapsynth/runs/` (5.2 MB), `art_bench/_review/` — all correctly gitignored. No repo cost.
- ⚠️ **Do not reuse the last audit's "missing from the Utils index" heuristic.** `Utils/README.md` now indexes only **15 of 52** scripts; 37 are absent, including `harvest_log.py`, `deploy_custom_mods.py` and `refresh.py` (37 refs). Absence from that index is now meaningless.

**`research/`**
- `research/RimMandrake/samuel_streamer_study/{00_MASTER_INDEX,01_STUDY_INDEX,02_TECHNIQUE_ANALYSIS,mod_inventory_from_saves}.md` — **`00` and `01` are not redundant**: `00` catalogues all **48** collections including the 24 never downloaded and holds their Drive links; `01` manifests the **24** on disk. `02` is the source `design/RimMandrake/Custom_World.md:3` defers *to*. `mod_inventory_from_saves.md` is cited at `required_mods.md:1249` as the raw un-decided complement to that doc, not a copy of it.
- `research/RimMandrake/samuel_streamer_study/configs/*.zip` (26 files, **19.5 MB**, three over 1.9 MB) + `lists/*` (1.28 MB) — unreproducible primary source; Samuel strips old collections' downloads, so the older ones cannot be re-pulled. `03_Gravtasm__modlist_ingame.rml` is cited by name at `required_mods.md:987`.
- `research/RimMandrake/reference/rimworld_handcrafted_map_atlas.md` (702 lines) — 2 live refs; provenance for all 49 world directories. *(The live half of the pair whose other half is flagged above.)*
- 49 × `research/RimMandrake/hand_authored_maps/World_*/README.md` — mtimes 2023-05 → 2026-03 prove these are the **upstream creators' own** READMEs. Each is the only surviving description of its gitignored `.rws`. ~16 KB total.
- `research/RimMandrake/inspiration/README.md` — the live product of the two dossiers: install audit vs `ModsConfig.xml`, the decisions table, three unresolved conflicts, one open RimBridge TODO. **Keep even if both dossiers go.**
- `research/Jawa/star_wars_species_scale_reference_atlas.pdf` (16.0 MB, gitignored) — load-bearing: `design/Jawa/art/graphic.md:239` and `cherry_picker_killlist.md:211` (the Gamorrean height contradiction).
- `research/Jawa/Jawa_Visual_Research_Dossier_v2_Image_Dense.pdf` (**46.7 MB**, gitignored, largest file in the repo) — **UNSURE, flagged not recommended.** Zero inbound refs under its current name, but `disposing/RESTRUCTURE_PLAN.md:68` moved it with an explicit *"do not delete for size"*. A filing gap worth the owner's eye, not a deletion.

**`design/Jawa/` — campaign doctrine, the highest bar for calling anything stale**
- `concept.md` (13 refs incl. src XML), `build_plan.md` (6), `first_live_access.md` (5), `droid_ruling.md` (4, incl. two live src files), `divine_satiation_engine.md` (5), `force_users_build_spec.md` (**6 commits today — the most actively edited doc in the slice**).
- `build_plan.md` vs `first_live_access.md` — **not duplication.** One says *in what order we build*, the other *what to prove first*; both headers state the split explicitly.
- `carbonite_trophy_mod.md` and `parked_mod_concepts.md` — explicitly **parked**, which is not spent. They state what should be built.
- `mods/required_mods.md` (**39 refs — the most-referenced file in the repo**), `forbidden_mods.md` (17), `cherry_picker_killlist.md` (12), `concept_defnames.md` (6), `outer_rim_cherrypick_list.md` (3), `world_interest_and_mech_danger.md` (4), `armoury_keeplist.md` (3), `agent_supersession_audit.md` (1). The killlist and the cherrypick list are **not** duplicates — one is a *delete* list, one a *lift* list. `cherry_picker_killlist.md` is dated 2026-08-02 but carries a fresh LIVE-DATA OVERRIDE banner: self-dating, not stale.
- `art/graphic.md` (3 refs) — `graphics_overhaul_protocol.md:384` names it *"the template. Its structure works"*; actively the reference brief. ⚠️ *`GamorreanXenotype.xml:65` cites it at the old path `image_request/graphic.md` — a broken reference to fix.*
- `worldbuilding/` fiction and spec layer, all live: `faction_roster_v2.md` (29), `desert_world_design.md` (30), `ship_deck_plan.md` (23), `jawa_xenotype_and_religion.md` (20, pantheon LOCKED), `setting_physics.md` (16, incl. 10 live src patches), `biome_terrain_palette.md` (14), `ship_designs.md` (11, hull LOCKED), `ship_distinctive_features.md` (10), `setup_checklist.md` (10), `Alien_Bestiary.md` (8), `enrichment_agents.md` (8), `jawa_dialogue_source_audit.md` (9), `tile_augmentation_catalogue.md` (7), `jawa_crew_personas.md` (5), `v1_quest_the_claim.md` (4, incl. two shipped defs), `Livestock_Trade_Utility_Pets_v1.md` (2), `biome_and_fauna_roster.md` (2).
- `hiding_the_gravship.md` — **0 refs and 3 commits today.** Brand-new owner doctrine ("the third verb"); zero refs because it is newer than anything that would cite it. **Explicitly not stale** — the same pattern as `skills/gravship-layout/`.
- `faction_world_spec.md`, `faction_stage3_buildable_spec.md`, `orbital_towers_and_the_sky_ladder.md`, `water_doctrine.md`, `ship_legacy_armoury.md`, `gravship_pursuer_mechanism.md`, `gravship_flight_invariants.md` — all owner rulings or specs landed **today**. Live.
- `row8_build_order.md` — an execution sheet **largely executed** (`V1_SCOPE.md`: *"ROW 8 STATUS — 3 of 4"*). **Not yet spent**: the fourth criterion, *boardable*, is UNTESTED, and `src/RimMandrake/bridgetools/execute_ship_plan.py` reads it. 🔔 **This is the next thing that will go stale — re-check when row 8 closes.**
- `Gravship_Campaign_Planning_Discussion_2026-08-02.md` (1,529 lines, oldest doc in the slice) — **keep.** 4 files cite it, and `world_interest_and_mech_danger.md` names it as the owner of the §19 enemy-danger framework, which nothing else holds.
- `resource_terrain_matrix.html` — generated, but `desert_world_design.md:92` calls it **"the canonical column set"**. Authoritative.
- `ship_image.png` (2.8 MB) + `ship_damaged_image.png` (3.1 MB) — each cited once by `ship_designs.md` as load-bearing evidence that the chosen hull #15 is the one drawn. **Not stale**, but ~6 MB of PNG for one citation each is worth an owner decision on downscaling.
- `ship_build/exported/{Gravship_v1.xml, JawaTestSled.xml}` — the v1 delivery artifact and the skill's named worked example. Live.

**`design/RimMandrake/` — the generic-method tier**
- `map_authoring_decision.md` (8 refs incl. `skills/rimbridge/SKILL.md`), `rimworld_file_lore.md` (9, incl. 5 Utils scripts), `save_authoring_pipeline.md` (11), `rimbridge.md` (11), `Custom_World.md` (11), `balance_paradigm.md` (13), `faction_authoring_mechanism.md` (5 — named in `design/README.md` as **the canonical example** of what belongs in this tier), `llm_voice_preauthoring.md` (7), `llm_stack_assessment.md` (2), `music_protocol.md`, `ollama.md`. All live method doctrine with real consumers.
- `beautiful_tilemap.md` — explicit `[v2]`, "Nothing built", cited by `queue/CREATE.md`. Parked with a queue entry, not orphaned.
- `coastal_mesa_rationale.md` (51 lines, 1 ref) — weakest-referenced doc in the tier, but it is the design-reasoning record for `author_coastal_mesa_terrain.py`. ⚠️ **Note the coupling: that script is itself an UNSURE orphan above. Rule on the pair together.**

**`vendor/` and `skills/`**
- `vendor/mod_sources/` (431 MB) and `vendor/salvage/` (25 MB) — gitignored except 2 `MANIFEST.json`. Exactly the "track that we have them, never the bytes" rule. Old mtimes here are **not** a staleness signal.
- `vendor/wisdom/{Factory_lore,benign_log_errors,def_override_clusters}.md` — 13, 14 and 4 refs; `benign_log_errors.md` edited today.
- `vendor/wisdom/github_issue_swcp_bundle.md` — 0 refs but its header reads *"FILED as issue #7, open"* with a correction still to post. Open action, not stale.
- `skills/gravship-layout/SKILL.md` (250 lines) — **0 refs and NOT stale**: newest skill in the tree, assembled today. Zero refs = brand new, not abandoned.
- All 13 `skills/*/SKILL.md` — 2–23 refs each; every sampled path uses the **new** structure. None point at pre-restructure paths.
- `skills/rimworld-modding/references/traps{,-*}.md` (7 files) — **not duplicates.** `traps.md` is an explicit index over six topic files, product of a deliberate 2026-08-12 split.

---

## Over budget ≠ stale — these get SPLIT, not deleted

`python3 src/RimMandrake/Utils/doc_budget.py` reports **12 files over budget**;
none of them are stale, and every one is actively cited:

| file | lines | budget | over |
|---|---|---|---|
| `infrastructure/state/NEXT_RELOAD.md` | 642 | 400 | +242 |
| `infrastructure/state/queue/CREATE.md` | 588 | 150 | **+438** |
| `infrastructure/state/queue/OPS.md` | 556 | 150 | **+406** |
| `infrastructure/state/V1_SCOPE.md` | 539 | 300 | +239 |
| `infrastructure/state/queue/VISION.md` | 404 | 150 | +254 |
| `infrastructure/state/queue/BRIDGE.md` | 350 | 150 | +200 |
| `CLAUDE.md` | 328 | 300 | +28 |
| `infrastructure/agents_def.md` | 237 | 200 | +37 |
| `infrastructure/state/queue/PROJECT.md` | 186 | 150 | +36 |
| `infrastructure/agents/{OPS,PROJECT,BRIDGE}.md` | 147 / 130 / 125 | 120 | +27 / +10 / +5 |

**The four seat queues are the real problem** — 1,898 lines across four files with
a 600-line combined budget. `doc_budget.py`'s own advice applies: closed items
belong in `CLOSED.md` as **one line each**, and provenance belongs in the commit
message. That is a compaction job for each seat on its own queue, not PROJECT's
to do and not a deletion.

Repo total: **327 markdown files, 68,352 lines (~751k tokens if read whole).**

---

## Method, so the next audit can reproduce or contradict this

- Fanned out across five slices — `design/`, `research/`, `src/`+`deployed/`,
  `observed/`+`vendor/`+`skills/`, `infrastructure/` — and re-derived every path
  from `git ls-files` and `find`. **No path was carried in from the disposed
  audit**; its four named items were re-located from scratch, and one of them
  (the pitch deck) does not exist.
- Inbound references counted with
  `grep -rn "<basename>" --include='*.md' --include='*.py' --include='*.sh' --include='*.json' --include='*.xml'`,
  excluding `infrastructure/disposing/` (nothing there is authoritative) and the
  file itself. **Zero refs is the strong signal; "referenced only by its own
  directory README" is recorded separately as a weak reference.**
- Every duplication claim above is **md5-verified**, not inferred from names.
- **Where the evidence pointed both ways it is marked ⚠️ UNSURE and both sides are
  given.** Nine rows carry that mark. A false "stale" costs a bad deletion, and
  that is the more expensive error here.
