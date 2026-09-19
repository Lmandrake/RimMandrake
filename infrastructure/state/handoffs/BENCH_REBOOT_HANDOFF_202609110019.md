# BENCH_REBOOT_HANDOFF_202609110019 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609100714`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**A per-biome fauna cast is joined from TWO sources, and reading the decisions file
naively double-counts.** In `fauna_assignment_register.decisions.json`, a row keyed
`fauna:<biome>:<creature>` with decision `move` means the creature **LEAVES** that
biome — its arrival biome is in `round2/move_mapping_v2.md`, not the key. So a biome's
real cast = its `in`-rows PLUS the move-rows whose resolved target is that biome. The
round-2 builders (`build_review_deck.py` / `build_review_pptx.py`) already do this join
correctly (see `build_biomes()` + `canon()` for the sea-biome key merge); reuse them,
don't re-derive casts from the raw decisions file. I got this wrong on first read and
the verification pass caught it.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **The round-2 fauna review is staged and waiting on HIM** — the per-biome sittings
  (highest churn first: the Miasma). Materials: the interactive deck (artifact URL in
  session), the editable pptx (`round2/fauna_review_deck.pptx`, sent to him), and
  `round2/biome_findings.md` (the Grey-Deep "three residents" collision, the Pyrelands
  losing its fire food-web to the boom cut, and the nightside-ice Wampa/Tauntaun
  physics call are the headline decisions).
- **Two reports await his review sitting:** `CANON_STORAGE_ARCHITECTURE_1`
  (`design/CANON_STORAGE_ARCHITECTURE_options.md` — recommends the hybrid store) and
  `CANON_DRAIN_1` (scheduled AFTER the fauna+flora wave, NOT the FOUNDRY builds).
- **A large Cathedral/Scald canon landed this wave** (frozen sheets amended, additive-
  only, verified 0 deletions) — he can veto by reading `the_rust_cathedral.md` §GM/§7b.
  Key new canon he may want to sit on: the sleeping-Rakata = reskinned vanilla
  ancient-danger mechanic, and the Cathedral hiding from the player at first.
- **Art gap flagged, not fixed:** 11 custom `RSW_` sea creatures + 58 vanilla/ReGrowth
  plants have no cached sprite in the decks (shown as labeled placeholders) — owed art.
  And the Codex art channel is broken (`CODEX_WORKER_SANDBOX_WRITE_1`); he ruled art
  regeneration HELD until it's fixed (no Gemini stopgap).

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
- **Nothing of BENCH's is mid-edit** — every ruling, deck, report and canon amendment
  this wave is committed and pushed. Clean stop.
- **The round-2 fauna sittings** are staged but not started (need the owner). Next
  action when he sits: open `round2/biome_findings.md`, start with the Miasma, rule its
  post-move cast; the deck/pptx are his to examine. The 4 propagation conflicts
  (`round2/propagation_conflicts.md`) and the faction-fauna roster want his eye there.
- **`RUST_CATHEDRAL_MECHANICS_1`** exists for the two-hum-rhythms mechanic that the
  amendment referenced but did not build — a real owed build, not started.
- **FOUNDRY has ~6+ build items** from this wave's rulings, interleaved in the commit
  log above (Cryptoforge harvest-retire partial, VQE Ancients curation partial,
  Mo'Events→RUT_ScavengerEvents 7/8 built, mech-presence enforcement, the codex fix).
  Those are FOUNDRY's lane, not BENCH's to resume.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
- **VEF quest chains self-schedule into the save silently.** The canonical save's
  `VEF.Storyteller.GameComponent_QuestChains.futureQuests` held Cryptoforge (~day 30),
  VQE PrototypeARC (~day 20) and Ancients (~day 118) — quests that WOULD fire on the
  shipped campaign with no player action. Grep a save's futureQuests before assuming a
  quest mod is inert; retiring such a mod must scrub these entries at resave.
- **River direction lives in `tileRiverDistancesDeflate` (1 byte/tile, mouth=0 rising
  upstream), NOT elevation.** The Scald reads −350m only because RimWorld can't render
  an elevated ocean — reading direction from elevation would invert every Scald river.
  Read the byte array; the seas/graves are the 0s.
- **Codex art channel: a strict-schema 400 and a too-tight timeout BOTH masqueraded as
  a dead channel** (worker exit 1, "not_run" validator). Real cause was two fixable bugs
  over a genuine third (the worker can't write its resized PNG into the sandbox —
  `CODEX_WORKER_SANDBOX_WRITE_1`). OpenAI strict output-schema needs every property in
  `required` and rejects min/max/maxLength.
- **Sprite audit: verify IDENTITY not coverage.** 96% "have art" meant nothing until I
  checked distinct creatures resolve to distinct files; a shared-sprite collision reads
  as success in every count.
- All four filed to `LESSONS_INBOX.md`.

## Closed since the last handoff (2)

- `ASHKARR_RIVER_LEDGER_1` — 4c24f9cb
- `RUST_CATHEDRAL_SCALD_HISTORY_1` — 2eaa493a

## Filed and still open (6) — the next seat's queue

- `ECONOMY_TRADE_SWEEP_1` — Full economic sweep of what is sold where and when, scheduled at the END of the world sweeps; includes Deeps-gated crystals (pyrinth/kyber/KOTOR/lante
- `MECH_PRESENCE_ENFORCEMENT_1` — Enforce the RULED mechanoid/ancient-danger table: XML only - MechCluster allowed/disallowedBiomes patch, per-biome preventGenSteps/extraGenSteps for t
- `CODEX_WORKER_SANDBOX_WRITE_1` — Codex art worker generates the image but cannot resize/copy it into its job workspace: worker exits 1, daemon sees no image (validator never runs), di
- `CATHEDRAL_PLAYER_CONCEALMENT_ARC_1` — Design the Rust Cathedral <-> player relationship arc: it hides from and dislikes the player at first because the player's Rakatan gravship agitating 
- `CANON_DRAIN_1` — Total canon drain: reconcile every lore doc to ONE level of truth, grinding out all superseded/obsoleted statements - a fresh-context pass gated on th
- `CANON_STORAGE_ARCHITECTURE_1` — Decide how to store the growing canon: options+tradeoffs report written (design/CANON_STORAGE_ARCHITECTURE_options.md) - recommends hybrid (prose cano

## Commits

```
307313b8 Canon-storage architecture options report (discussion product, nothing applied)
f99108ce File CANON_DRAIN_1: total canon reconciliation, gated on the biome-cast wave
29f1f68e Ledger sync: GOO_BOOM_COMMISSION_1 blocked (design done, build phase owed after owner rules on 8 open calls)
97069155 GOO_BOOM_COMMISSION_1: file the design brief (Fable pass, commit 477ab973) into the ledger
477ab973 GOO_BOOM_COMMISSION_1: design brief for RUT_Vhessk, the one Assailant-dungeon boom creature
6bf79d7c Ledger sync: ROSE_OF_REBIRTH_CONTAINMENT_1 closed
0ae4d103 ROSE_OF_REBIRTH_CONTAINMENT_1: the mechanism cannot self-spread; the 476 live instances are a static placement artifact, not an active bug
49a1dbf9 Ledger sync: VALIDATE_PATCH_TEXPATH_CLASSIFIER_1 closed
52ed389a VALIDATE_PATCH_TEXPATH_CLASSIFIER_1: fix the texPath ERROR/WARN classifier's false positives on universal top-level folder names
4fa06406 Ledger sync: RSW_PROTOVERMES_TEXPATH_MISSING_1 closed, VALIDATE_PATCH_TEXPATH_CLASSIFIER_1 filed
f56ded83 RSW_PROTOVERMES_TEXPATH_MISSING_1: false positive, not a game defect - Dessicated_Boomrat is real Core art, packed in resources.assets
dc5636bb Ledger sync: VQE_ANCIENTS_CURATION_1 blocked (partial - steps 1/3/6 done)
9b9240c1 VQE_ANCIENTS_CURATION_1: CherryPicker cut proven live, Empire patch audited clean, dungeon-guardians roster fed (steps 1/3/6 of 6; step 5 confirmed not-yet-fireable)
e3fffd48 Ledger sync: CRYPTOFORGE_HARVEST_RETIRE_1 blocked (partial - steps 2/3 done)
25019d7c CRYPTOFORGE_HARVEST_RETIRE_1: harvest reference copied, both FindMod-gated patches deleted (steps 2-3 of 5)
0d7f17ee Contagion naming: 'the Overdrive' is the Helix's name for it (owner 2026-09-10)
12034a59 File CATHEDRAL_PLAYER_CONCEALMENT_ARC_1: the Cathedral<->player relationship arc
a7a0295f Apply Cathedral/Scald amendment to the frozen sheets; close RUST_CATHEDRAL_SCALD_HISTORY_1
2eaa493a Fold the 5 owner resolutions into the Cathedral/Scald amendment draft
e4934d14 Record ancient-danger reskin canon: sleeping Rakata = reskinned vanilla ancient dangers
77963140 Cathedral/Scald amendment DRAFT + fix river-ledger Scald-origin contradiction
20d6e732 Capture Cathedral/Scald canon: 4 rulings + the whole Cathedral-situation dump
1d3ddbe7 Ledger sync: BOOM_FAMILY_CUT_1 closed, RSW_PROTOVERMES_TEXPATH_MISSING_1 and ROSE_OF_REBIRTH_CONTAINMENT_1 filed, RUT_SCAVENGEREVENTS_BUILD_1 and SCALD_RIVER_REPAINT_1 blocked
e75fa111 BOOM_FAMILY_CUT_1: cut the 15-creature boom family, owner ruling - CherryPicker cut proven live, every biome-cast/stat-patch/vault reference removed by hand
596f39e8 RUT_SCAVENGEREVENTS_BUILD_1: 7 of 8 mechanisms built; correct an earlier wrong finding on RescueTraitor
bf52228f RUT_SCAVENGEREVENTS_BUILD_1: RUT_ShipBreak, the 7th mechanism built (7 of 8 named mechanisms now ported)
28af11e9 RUT_SCAVENGEREVENTS_BUILD_1: RUT_Stroke, mechanism 6 of 8
89a8dcfb Close SCALD_RIVER_REPAINT_1 (owner override): verified already-done, no-op
0b28a91d Scald river repaint VERIFIED already-done in the save; closed as no-op
a03900ad RUT_SCAVENGEREVENTS_BUILD_1: RUT_Insects, mechanism 5 of 8
8a725b27 RUT_SCAVENGEREVENTS_BUILD_1: RUT_PodCrash, mechanism 4 of 8
dac87450 River naming sitting: 16 rivers named, ledger ratified and closed
4c24f9cb RUT_SCAVENGEREVENTS_BUILD_1: RUT_SurvivalPod and RUT_Thanksgiving, mechanisms 2 and 3 of 8
ed911967 chore(sync): laptop 2026-09-10T09:24:23-07:00
5be01cf8 River ledger ruled: full R1 outflow, R02 the Saltward is the Notch, R03 is a river; Cathedral-Scald history filed
9ad72a2d River ledger DRAFT: all 16 rivers named; data-vs-R1 conflicts surfaced for owner sitting
d40e3a79 Editable PowerPoint of the review deck: drag critters between biomes
73aebd3d Round-2 examination deck: per-biome fauna+flora with intent tooltips, biome text, BENCH comments, grouping sheets
0dd780a7 RUT_SCAVENGEREVENTS_BUILD_1: RUT_Migration built, compiles clean, deployed, queued for next load
4e0e599d RUT_SCAVENGEREVENTS_BUILD_1: decompile and record the real mechanism for all 8 Mo'Events incidents before writing any RUT_ C#
4a60a50d Owner: hold all fauna art regeneration until the Codex channel is fixed (no Gemini stopgap)
0dc328dc File CODEX_WORKER_SANDBOX_WRITE_1: worker's resize/copy fails under sandbox, masquerades as timeout
98e6cdff Zero-UAC proof passed, owner-attested: codex channel's attended-run gate satisfied
935e37df artpipe: raise codex worker timeout defaults (150/220 -> 300/420)
c20b5410 Lesson: strict output-schema rejection masquerades as a dead codex channel
69f46929 artpipe: fix manifest schema for OpenAI strict structured output; per-biome findings pass
3ee26fb2 Transient: canonical Ash'karr save backup, taken before killing 6 behemoths and clearing corpses on the live map
04fb1091 BIOME_SPAWN_FLORA_AUDIT_1: the def-level rainbow-plant fix already landed and matches live; the campaign map just predates it, and Rose of Rebirth is a separate mechanism filed on its own
3430e5e2 Fauna wrap: ninth roster (faction fauna) + dungeon-owner column + both-jungles rulings landed
0198c6f9 Fauna round-2 mechanical passes: propagation (29 rows, 4 conflicts), move mapping v2 (164/164), groups + homeless buckets
b56238dd Fauna wrap sitting: round-2 plan ruled and recorded; boom family cut + goo-boom commission filed
8dbc2e01 Fauna review COMPLETE: the owner's 828-row verdict file (1134 sidecar writes, 291 overrides, 230 notes)
2b0a8c10 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark 5 tonight-authored files clean (Lightfall, MECH_PRESENCE pieces)
50af6a2b FISH_BESTIARY_COMMISSION_1: fish bestiary proposal — 32 species, 8 registers, 7 waters, the 4 owed defs specified
e48e7847 Ledger sync: SEA_ENRICHMENT_LANDMARKS_1 closed
0d543990 SEA_ENRICHMENT_LANDMARKS_1: placement script + verification outputs
e50bbb73 Ledger sync: GAPING_DOOM_SITE_1 closed, LANDMARK_NAMING_PASS_1 tool fix noted
626bd440 Fix jawa/world_landmark_rename never registering: partial-class the tool
8d5e3df2 VQE Ancients ruled: keep-curated (archite = Assailant flesh-craft); curation filed for FOUNDRY
264ff8e2 VQE Ancients: census+sweep+save evidence recorded; Cryptoforge futureQuests finding on the harvest item
92a3a0d3 Cryptoforge ruled: retire-after-harvest; VQE Ancients deep analysis filed+claimed
f69b7fb2 Mo'Events ruled: retire-and-replicate as RUT_ScavengerEvents (build filed); Cryptoforge canon pass extended
88cc1e27 Ledger: GAPING_DOOM_SITE_1 rename still blocked, real root cause found on LANDMARK_NAMING_PASS_1
40d25145 Ledger: file+claim the Cryptoforge retirement and Mo'Events independence audits
936fe88a GAPING_DOOM_SITE_1: live placement done, rename blocked on a real tool bug
e74ad31e Ledger sync: ROTSPOREKIT_ENABLE_DECISION_1 + FUNGALFOREST_RAID_MERGE_1 closed
1ad5a21d Enable mandrake.rut.rotsporekit live, cold-load-verified clean
5ed4610e Ledger sync: GAPING_DOOM_SITE_1 fix note, DIRTY_CODE_REVIEW_STANDING_LOOP_1 cross-reference
b4144afc GAPING_DOOM_SITE_1: fix RUT_GapingDoom's missing guaranteed mutator
15330396 LIGHTFALL_CHASM_AUTHORING_1: author RUT_Lightfall LandmarkDef
c9c60968 Ledger note: FUNGALFOREST_RAID_MERGE_1 re-verification pass
188546bc Ledger sync: DROID_RETIRE_ABF_SYNCORE_1 closed, live-verified
0c289802 DROID_RETIRE_ABF_SYNCORE_1: remove DroidsAreMachines ABF-gated FleshTypeDef Operation
9ffb281c Ledger sync: DROID_RETIRE_ABF_SYNCORE_1 unblocked (order-constraint cleared by kotordroids retirement)
fed5cebf Ledger sync: BIOME_ENRICHMENT_POISON_FOREST_1 closed
256f239f BIOME_ENRICHMENT_POISON_FOREST_1: placed 245 mutators across 216 PoisonForest tiles
d7030b03 Ledger sync: DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1 closed, BIOME_ENRICHMENT_POISON_FOREST_1 unblocked
4b4c2459 DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1: donor lumi.doorsexpanded retired for real, live-verified
6af1b00f MECH_PRESENCE_ENFORCEMENT_1 piece 3/4: zero mechanoid raidCommonalityFromPointsCurve
508369ee MECH_PRESENCE_ENFORCEMENT_1 piece 2/4: ANCIENT column preventGenSteps/extraGenSteps
02414a3c MECH_PRESENCE_ENFORCEMENT_1 piece 1/4: MechCluster AMBIENT biome whitelist
b68916e7 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 repo-wide clean milestone
0584783f DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark final 20 mod LICENSE files clean (repo-wide code review now complete)
6e65d276 naming_lint: derive tier from mod's own tier-folder when unmapped, not UNASSIGNED
327c8986 Dirty code review: mark 10 Armoury files clean (wave 13)
6784196e Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 LanternDeeps wave note
6a20ff8f Ledger sync: mark 8 LanternDeeps files clean (DIRTY_CODE_REVIEW_STANDING_LOOP_1)
1dc7382d DIRTY_CODE_REVIEW_STANDING_LOOP_1: fix LanternDeeps CRYSTAL_INGEST genstep-order and dead-patch bugs
6cc9df02 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave notes (MenuShell, Pyrinth, UtinniPatches remainder)
d8c9c29e Code review: mark UtinniPatches fish-types wave clean (DIRTY_CODE_REVIEW_STANDING_LOOP_1)
429d1760 Dirty code review: src/RimMandrake/Pyrinth/ marked CLEAN (26 files)
40d1b98c Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 note for MenuShell wave
1753a927 Code review wave: mark src/RimUtinni/MenuShell/_artsrc clean (11 files)
fa90b445 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 - LICENSE batch + session summary note
f5f2d0a2 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark 25 mod LICENSE files clean
92e56d4f Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 Aftermath wave note
d842d4ae Mark Aftermath LICENSE + both .csproj files clean (DIRTY_CODE_REVIEW_STANDING_LOOP_1)
5ed4b469 Dirty-review wave: mark MovingDunes csproj CLEAN (no findings)
5c4a5137 Ledger sync: FLUID_CANAL_DEBUG_SURFACE_1 closed (live-retested, no longer reproduces on full stack)
49ca28aa Code review: FluidCanals full-scope sweep, csproj clean
a13a5975 Code review: RustChrome sweep, LICENSE + RustChrome.csproj clean
7d23de24 Ledger sync: CRYSTAL_INGEST_EXECUTION_1 closed
406dd95f Ledger sync: FISH_TYPES_PATCH_BUILD_1 closed
689195d3 FISH_TYPES_PATCH_BUILD_1: strip live fishTypes from 16 ruled no-fish biomes
6fe8f7ce CRYSTAL_INGEST_EXECUTION_1 items 3-5: KOTOR labeling, Stygium leak fix, lanternstone fiction
2ab0ee09 FISH_TYPES_PATCH_BUILD_1: trim weeping-stones fishTypes to the 4 swfish_ donors
7740beb4 FISH_TYPES_PATCH_BUILD_1: fill Cracked Lands uncommon fishTypes with BMT_Rocktooth/BMT_Boneblade
fbcef399 CRYSTAL_INGEST_EXECUTION_1 item 2: absorb The Force - Lightsaber kyber, gate to Lantern Deeps
3e7a8571 ManyWaters: fix RM_ColoredWaterBottles ParentName that never resolved (null thingClass)
22283c02 CRYSTAL_INGEST_EXECUTION_1 item 1: absorb Epochs - Pyrinth, gate scatter to Lantern Deeps
3781dba4 Add crashed_ship.lua template (spec 8.9): one-deck starship wreck with a real walled hull
acbb58c6 Ledger sync: StructureInjections wave note (DIRTY_CODE_REVIEW_STANDING_LOOP_1)
39c2909a DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark src/RimMandrake/Pits/LICENSE clean
b88a6f90 Ledger sync: ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1 status reconciliation note
7b757e10 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 Oracle-wave note
678ff6dc Mark Oracle LICENSE and Oracle.csproj clean (DIRTY_CODE_REVIEW_STANDING_LOOP_1)
80f5da8f Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 Ninefold-sweep note
ef6ce8e4 INHABITED_AUGMENTATION_BUILD_1: add beast_pens.lua (spec 8.13, pet/beast breeding facility)
46f6de21 Mark Ninefold LICENSE and Ninefold.csproj clean (DIRTY_CODE_REVIEW_STANDING_LOOP_1)
87f6db62 INHABITED_AUGMENTATION_BUILD_1: build garrison_tiny.lua archetype (8.6)
4ee3a58e Add beast_lair.lua: giant-beast nest/lair template (spec 8.11)
e1d56ba1 Add pre-retirement ModsConfig backup (DROID_RETIRE_KOTORDROIDS_1 provenance)
b9c49d6b Ledger sync: DROID_RETIRE_KOTORDROIDS_1 + DROID_SIBLING_RELATION_GEN_CRASH_1 closed
0fc1dd14 FULL.LATEST: 578->577 active mods, guy762.kotordroids retired
18372f2a INHABITED_AUGMENTATION_BUILD_1: battle_site.lua, the 8.12 ruin transform
e91d7241 Armoury: gate armband_wristgun's default microrocket part MayRequire=KotORDroids
2f70104d Close WALL_LIGHTS_HELPER_BROKEN_1
0075838f Fix wall_lights() call sites in road_warehouse.lua and trading_post.lua
21b4a0c5 INHABITED_AUGMENTATION_BUILD_1: 8/14 archetypes note synced; file WALL_LIGHTS_HELPER_BROKEN_1
1bd9e669 Ledger sync: 3 ruled parents superseded by their build successors
abd97be8 Morning batch 2026-09-10: 12 owner rulings landed, 5 items filed
6093b7fc Build 8.5 road-warehouse template (INHABITED_AUGMENTATION_BUILD_1, 8/14 archetypes)
9a7e680c DROID_RETIRE_KOTORDROIDS_1: broader indirect-reference sweep clean, proceeding to live retry
70dfe98f Code review status: mark 7 artpipe/codex_image files clean
7dabaa86 artpiped.py: warn on unrecognised gemini model instead of silently mispricing it
a50793cb Code review status: mark RUT_TheRot.xml clean (already reviewed tonight)
f183a403 Close RUT_PLANT_BIOMEPLANTRECORD_CROSSREF_1; file ROTSPOREKIT_ENABLE_DECISION_1 as follow-on
e62a3c66 RUT_TheRot.xml: gate 19 RotSporeKit plant refs with MayRequire (fixes RUT_PLANT_BIOMEPLANTRECORD_CROSSREF_1)
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-10T22:24:39Z

Uncommitted ownership: `codebase_health*` + `codebase_health_last.json` = FOUNDRY's
health tool. `artpipe/throughput.jsonl` = the resident Artist daemon's billing log
(BENCH's codexcal calibration wrote to it; daemon state, not to commit). `events.jsonl`
+ `BENCH.md` + `FOUNDRY.md` = ledger/queue render churn (committed in the handoff sync
below; the FOUNDRY.md delta is only a render-clock timestamp). `defs.sqlite` = shared
derived DB, never commit. `serve_fauna.log`/`serve_flora.log` = the review-sheet
sidecars, DELIBERATELY still running (owner's live tabs) — do not kill. The `codexcal_*`
failed jobs = BENCH's Codex calibration artifacts (diagnosis captured on
`CODEX_WORKER_SANDBOX_WRITE_1`; operational churn, left uncommitted). The Armoury
`Crystal/` textures = FOUNDRY's crystal-ingest work, not BENCH's.

Raw list:

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
?? defs.sqlite
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? infrastructure/artpipe/failed/codexcal_lockjaw_a.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_a.manifest.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_a_r2.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_a_r2.manifest.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_a_r3.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_a_r3.manifest.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_b.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_b.manifest.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_b_r2.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_b_r2.manifest.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_b_r3.json
?? infrastructure/artpipe/failed/codexcal_lockjaw_b_r3.manifest.json
?? infrastructure/artpipe/failed/codexcal_mantrap.json
?? infrastructure/artpipe/failed/codexcal_mantrap.manifest.json
?? infrastructure/artpipe/failed/codexcal_mantrap_r2.json
?? infrastructure/artpipe/failed/codexcal_mantrap_r2.manifest.json
?? infrastructure/artpipe/failed/codexcal_mantrap_r3.json
?? infrastructure/artpipe/failed/codexcal_mantrap_r3.manifest.json
?? src/RimStarWars/Armoury/Textures/Things/Item/Resource/Crystal/
```

