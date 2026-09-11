# FOUNDRY_REBOOT_HANDOFF_202609110245 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609100141`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The artpipe daemon (`artpiped.py`, console-visible since 2026-09-09 18:50) does not
hot-reload — any edit to its own source (a timeout constant, a manifest field, anything)
silently never takes effect until the process is restarted. `CODEX_WORKER_SANDBOX_WRITE_1`
looked like an unfixable sandbox bug across 9 failed jobs because two real fixes landed in
source but the running process never picked them up; restarting it (queue was idle, clean
SIGTERM) made the identical failure go 3/3 → 0/3 on the same live 3-job N=3 test. Check
`ps` for the daemon's start time against the last edit to `artpiped.py` before trusting
any "still broken after the fix" observation on that channel.

## What the owner should see

- Live BENCH-mode session tonight (fire/behemoth had wrecked The Utinni's thruster bay):
  Twice-Kin resurrected (`T: Resurrect`, verified alive, xenotype/ideo confirmed identical
  to the other 4 colonists), 6 astrofuel pipe segments rebuilt to full HP, two new astrofuel
  tanks built + wired + filled (ship went from `maxFuel: 0` / grounded to `fuel: 250/250`,
  `rangeTiles: 40`, all 4 thrusters gate-clean). Canonical save resaved under the SAME name
  (`CANONICAL_ASHKARR_2026-09-09.rws`) and frozen — `infrastructure/state/CANONICAL_SAVE.md`
  is the new freeze record (first one for the save; no prior doc tracked this). Backup chain
  is in the live Saves folder, not the repo.
- `OASIS_LANDMARK_PLACEMENT_1`'s 186-row proposal CSV
  (`Transient/oasis_landmark_proposal_2026-09-10.csv`) is verified and waiting on your read
  of §10-12 (the sheet's own unratified section) before live placement — and the game is now
  UP (it was DOWN when that item's last note was written), so this could go live on the next
  FOUNDRY pass without waiting for a fresh game-up.
- `FISH_BESTIARY_COMMISSION_1`'s proposal (`design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md`)
  has 6 cardable questions in §6 blocking a build item — nobody's ruled on them yet.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `FISH_BESTIARY_COMMISSION_1` — proposal written and complete (32 species/8 registers/7 waters,
  `design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md`). Not advanced this
  session. Next action: owner/BENCH rules on §6's 6 cardable questions, then file the build item.
- `LIGHTFALL_CHASM_AUTHORING_1` — site+name owner-ratified (tile 9023, the Damp chain), never
  authored on the live world. Not advanced this session. Next action: `jawa/world_*` landmark
  placement at tile 9023 + `jawa/world_commit` — needs bridge, which is free and the game is up.
- `MECH_PRESENCE_ENFORCEMENT_1` — 3/4 XML pieces landed, validated 0 errors, and already pushed
  (`02414a3c`/`508369ee`/`6af1b00f`). Piece 4 (shrine contents where ANCIENT-ALLOW meets
  AMBIENT-DENY) is genuinely blocked, not stalled: verified via `rimsage read_csharp_symbol`
  that `GenStep_ScatterShrines` has no XML hook at all — only a Harmony postfix on
  `SymbolResolver_AncientTemple.Resolve` reaches it, which is C# and outside this item's
  XML-only scope. Not advanced this session. Next action: file a follow-on C# item, or get the
  owner to authorize expanding this item's scope.
- `OASIS_LANDMARK_PLACEMENT_1` — 186/186-row proposal CSV drafted and verified
  (`Transient/oasis_landmark_proposal_2026-09-10.csv`), see "What the owner should see" above.
  Not advanced this session. Next action: owner rules on §10-12, then live bridge placement +
  `world_commit`, batchable with `MODLIST_RESTORE_AND_BATCH_DEPLOY_1` if that's still pending.

## Traps learned

All three filed to `LESSONS_INBOX.md` this session:

- The artpipe daemon's stale-process trap — see "The one thing to carry forward" above.
- `rimworld/execute_debug_action`'s `ToolMap` actions (`T: Resurrect`, `T: Destroy`) refuse a
  `thingId` param outright ("Could not find current-map thing id X") even for a thing that
  visibly exists via `jawa/list_things` — `x`/`z` cell targeting is what actually works for
  these two tools.
- `T: Destroy` targeted by `x`/`z` destroys EVERY thing in that cell, not just the one you
  meant — collateral-destroyed a healthy `HiddenConduit` and a decorative
  `OuterRim_AurebeshWordEngineer` alongside 4 of 6 targeted damaged pipes. Read
  `solidThingDefs` before AND after any cell-targeted destroy; rebuild anything that wasn't
  the intended target (both were, here).

## Closed since the last handoff (32)

- `NINEFOLD_RUNTIME_PROOF_BLOCKED_1` — c5340ca25af133f7f47b63958f026d5181c68ec1
- `DROIDWORKS_MODULE_PERSONALITY_1` — 449e98056
- `DROID_MODULE_BODYGROUP_WIRING_GAP_1` — 449e9805788536e5fc74dcca59274672c886189d
- `DROIDWORKS_PERSONALITY_VERIFY_1` — ae6f10df33684a6300fd5377dc34e522b2598753
- `MAPGEN_ROUND3_VERDICT_LANDING_1` — 805d59838c99d6d218091e02633051eebb277c11
- `HUMAN_QUEUE_NEEDS_OWNER_RENDER_1` — 6a9605daf1c9a54adfe2e366e87d7b1448365228
- `SCORCHFRUIT_FULGURITE_DEF_VERIFY_1` — 450d326795d37d6544d52b538be7842c6ea05a30
- `ASSIGNMENT_APPLIER_SCHEMA_REWRITE_1` — 64ffdc028905fbf8994e184cc787f4ef99c599b1
- `ANCIENT_RUINS_FAMILY_CUT_1` — 4d6c684ea18990862ee4fbed75db3096e024d37a
- `DROID_RETIRE_DEPOT_ASIMOV_1` — 894bb6bdbeba822619a1eb88fc0519ee61411e34
- `DROID_DONOR_SAVE_COMPAT_REGRESSION_1` — 3c100a29e2d7d0ecd08c637b0a571c9ec79b3a14
- `RUT_PLANT_BIOMEPLANTRECORD_CROSSREF_1` — e62a3c66
- `WALL_LIGHTS_HELPER_BROKEN_1` — 0075838f
- `DROID_RETIRE_KOTORDROIDS_1` — 0fc1dd14a8122822999d2c049c748eedcefb2138
- `DROID_SIBLING_RELATION_GEN_CRASH_1` — 492520c2
- `FISH_TYPES_PATCH_BUILD_1` — 689195d388d2b53e02c2fc6560529fc089d39a31
- `CRYSTAL_INGEST_EXECUTION_1` — 406dd95f4d69d3efb01c33975891904c04dca7f4
- `FLUID_CANAL_DEBUG_SURFACE_1` — 49ca28aaf5f0000886c7fa27926d42cbf95d0c09
- `NAMING_LINT_RENAME_MAP_STALE_1` — 6e65d276694f9c1580dc2c8e7d7e7e2dbe07c5cb
- `DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1` — 4b4c245996280fe2b6c0cbfa07a4423c05f02fe5
- `BIOME_ENRICHMENT_POISON_FOREST_1` — 256f239f2668b89c4a879107d6cd7ce52f914769
- `DROID_RETIRE_ABF_SYNCORE_1` — 0c289802072fc2170ff3c5655a3234c1268dbbba
- `ROTSPOREKIT_ENABLE_DECISION_1` — 1ad5a21d39bf913efbe4bb7d8ef22c829fc242d0
- `FUNGALFOREST_RAID_MERGE_1` — 1ad5a21d39bf913efbe4bb7d8ef22c829fc242d0
- `GAPING_DOOM_SITE_1` — 626bd4408aad98f2d6e6f16ea573f9c9d7f18995
- `SEA_ENRICHMENT_LANDMARKS_1` — e50bbb73cd51c365c9be6a773799e4e840742999
- `BIOME_SPAWN_FLORA_AUDIT_1` — 04fb1091901717387cb8cadc208d1d12830d4a6b
- `BOOM_FAMILY_CUT_1` — e75fa1119ee0000000000000000000000000000
- `RSW_PROTOVERMES_TEXPATH_MISSING_1` — f56ded83
- `VALIDATE_PATCH_TEXPATH_CLASSIFIER_1` — 52ed389a
- `ROSE_OF_REBIRTH_CONTAINMENT_1` — 0ae4d103
- `CODEX_WORKER_SANDBOX_WRITE_1` — d4a4c10d9960b87eb081b9510683a4d77976be18

## Filed and still open (11) — the next seat's queue

- `CHERRYPICKER_SHIP_BASELINE_STALE_1` — Cherry Picker SHIP baseline stale since 2026-09-02: live config has drifted 617 added / 178 removed vs tracked snapshot, bundles a near-total backstor
- `FISH_BESTIARY_COMMISSION_1` — Commission a per-biome fish bestiary: many new fish defs per fished water (squid/octopus/eel/crustacean/floater/jellyfish/cucumber registers, Star War
- `MECH_PRESENCE_ENFORCEMENT_1` — Enforce the RULED mechanoid/ancient-danger table: XML only - MechCluster allowed/disallowedBiomes patch, per-biome preventGenSteps/extraGenSteps for t
- `RUT_SCAVENGEREVENTS_BUILD_1` — Build RUT_ScavengerEvents (mandrake.rut.scavengerevents): port 8 Mo'Events mechanics as our own IncidentWorkers (SurvivalPod, ShipBreak, PodCrash->spa
- `CRYPTOFORGE_HARVEST_RETIRE_1` — Harvest then retire VQE Cryptoforge: (1) reproduce the 18 SALVAGE_PALETTE-cited props as owned RUT_/RSW_ ThingDefs with OWNED art (citation swap - Wor
- `VQE_ANCIENTS_CURATION_1` — Curate VQE Ancients per the ratified verdict: (1) CherryPicker-cut AbilityDefs Levitation/Invisibility/InfernoSpew + their granting GeneDefs + the hel
- `GOO_BOOM_COMMISSION_1` — Commission ONE big Assailant-dungeon boom creature: fleshy-based, sacks of explosive goo, new def + new art - replaces the entire cut boom family (Boo
- `MIASMA_NURSERY_KINDS_1` — Miasma sea-nursery (owner ruling at 2026-09-10 sitting: sea creatures raise young in the Miasma): juvenile-only PawnKindDefs via maxGenerationAge cap 
- `ART_BACKGROUND_TEMPLATE_1` — Standard black-background creature-art generation template: write it, prove it out iteratively, keep a works/doesn't log for process improvement
- `WYYYSCHOKK_FERALISK_MERGE_1` — Wyyyschokk duplicates AA_Feralisk's properties/attacks (stats+verbs), then AA_Feralisk retires entirely; cut Cinderlisk, Maguana, AB_Feralisk and ever
- `PYRELANDS_FIRE_WEB_COMMISSION_1` — Pyrelands fire-web: commission fire-hawk + furnace-beast defs, recast Razorjack (fire-follower) + Barbslinger (ash-grazer), pick a burrower (owner car

## Commits

```
2533bf0a Four card rulings landed: Pyrelands fire-web plan, films/mats interaction test, commission-first policy, Basilisk kept
0ceaa601 Lisk cull + Teratogenic size 3 + Wyyyschokk-Feralisk merge filed
17de9be6 Grey Deep cap RELEASED (owner): schooling set to the Twilight, Megakrill stays a fishing result
82924c12 Freeze the canonical save after the gravship thruster-bay repair
79a3dcb3 Extend trader-beast candidates: flyers + heat-compatible sections, fix 8 dupes
a1241bcb Nightside visitor law: apply to the real rows (homeless Wampa/Tauntaun moves, Jakobeast reroute, native notes)
7b6d93bc Nightside visitor law RULED: Wampa/Tauntaun/Jakobeast as visitors-and-dying, natives thermal-only, 3 native commissions
69aa1535 File trader-beast candidate roster: Star Wars herd/pack fauna for Ash'karr caravans
f762aed4 Round2 deck: per-biome dedup, RESERVE-target fix, reserved-tag exclusion
ca9032f8 Sitting batch 2: six-biome removals, RedGoo titan, TetraSlug cathedral-only, Dunealisk cut, per-biome dedup ruling, cathedral commissions
54c520be Sitting batch: desert/wasteland/greentide rulings + Terramorph dayside enforcement + art-template ticket
9f2ebb1d Arid sitting rulings: Skalder->poison_forest, Wildpawn->greentide, Cannok+Vulptex->reserve, Kreetle art redo
61ad66fb FLORA_COMMISSION_TEMPLATE_1: flora commission template proposal (design only)
69d3a6e6 Ledger: file MIASMA_NURSERY_KINDS_1 (owner's nursery ruling, BENCH-filed)
f95ee85a Sitting rulings 3+4: horror creatures injectable-only, Miasma ruled sea nursery
1caff366 Flora verdict propagation: plant-level art/size inherit across sibling rows, 0 conflicts
96fa6392 Flora review COMPLETE: owner's 288-row verdict file (273 sidecar writes, 19 overrides, 60 notes)
302faec3 Fix plant texture identity bug: dir-shaped texPath matched wrong flat bundle file
dcb89250 Round-2 deck: full art coverage, homeless-move join fix, east-facing fauna
98ae5146 Close CODEX_WORKER_SANDBOX_WRITE_1: stale daemon process, not a sandbox-write bug
d4a4c10d Round-2 sitting: insect ruling applied (VFEI2/vanilla insects faction-only) + art-redo semantics recorded
12c11704 artpipe: capture codex worker stdout/stderr tail on failure manifests
4e68514c chore(sync): laptop 2026-09-10T17:39:40-07:00
7e650072 BENCH reboot handoff 202609110019: rivers named+repaint-verified, Cathedral canon landed, fauna round-2 staged, canon-storage report
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
561088e6 BENCH reboot handoff 202609100714: 7 items advanced overnight, 3 closed, 9 morning decisions staged
d5640d47 Code review status: mark BiomeCast_Ashkarr.xml clean (both copies, already reviewed tonight)
1c96dd41 Checkpoint the owner's live fauna review decisions (69 moves + art verdicts, sidecar-written)
8f91973e Close DROID_DONOR_SAVE_COMPAT_REGRESSION_1 (live-verified end to end); file RUT_PLANT_BIOMEPLANTRECORD_CROSSREF_1
e4fed711 VAPOR_EMITTER_PLACEMENT_1 scopes 1-2: vapor emitter inventory + placement rules
3c100a29 Fix a real regression from DroidDepot retirement: 7 biome-cast PawnKindDef refs
894bb6bd Ledger sync: EXPLOSIVE_PLANT_GROWTH_1 design-draft note
734a25fb EXPLOSIVE_PLANT_GROWTH_1: design draft — soak/charge/burst, per-biome terminal moments, perf gate
3d9ca2a1 Ledger sync: FLOOD_WITNESS_EVENT_1 design-draft note
22400524 FLOOD_WITNESS_EVENT_1: design draft — witnessed flood quest (prose spec + machinery map)
9427d6d6 Move-target mapping: 69 owner Moves resolved to sheets, 4 open calls, staged for morning
c27d2eac Ledger: fish proposal staged for morning; mechanoid biome review claimed
382f909b Ledger sync: FISH_BY_BIOME_1 proposal note (552b03b7)
552b03b7 FISH_BY_BIOME_1: merged fishTypes proposal — every water RULED or PROPOSED, sand-fishing customs reconciled with donor census
d5b64876 Ledger: first live artpipe drain recorded; gemini quality sheet staged for morning
cfd756dc artpipe: never commit _artsrc staging (design: PNGs are staging, JSONs are provenance)
43942f47 Gemini channel goes end-to-end: --size resize + rembg cutout (serialized), stdin-fed worker source, stdout tails on manifests
fea15975 Gemini channel goes end-to-end: --size resize + rembg cutout (serialized), stdin-fed worker source, stdout tails on manifests
261d050f INHABITED_AUGMENTATION_BUILD_1: 6/14 archetypes note synced
6e8d4a12 Build 8.4 trading-outpost template (INHABITED_AUGMENTATION_BUILD_1, 6/14 archetypes)
3411fa44 CODEX_UAC_STORM_1 closed: root cause + fix recorded, live zero-UAC proof gates the first attended run
5b50a412 Ledger sync: CODEX_UAC_STORM_1 note
31a92df6 CODEX_UAC_STORM_1: version-aware sandbox seeding + daemon preflight
5c2f83a7 Garb harvest closed (59 refs landed); added to morning ruling batch
c58256fa Ledger sync: SW_BACKGROUND_GARB_HARVEST_1 note
0c6391ee SW_BACKGROUND_GARB_HARVEST_1: reference art harvest, 59 images
4a1b9e76 ANCIENT_RUINS_FAMILY_CUT_1: independent second-opinion re-verify confirms safe
faabffc3 Wraps commission fully ruled: 4 wraps + both heads as unwired options
0405af11 Wraps ruling: all four styles ship
a071f4df Ledger sync (BENCH's CODEX_UAC_STORM_1 claim, picked up in this checkout)
0acb1f0c Code review status: mark 4 files clean (own tonight's work, already reviewed)
afcfa347 INHABITED_AUGMENTATION_BUILD_1: 5/14 archetypes note synced
178f5d0b Build 8.10 dead-caravan template (INHABITED_AUGMENTATION_BUILD_1, 5/14 archetypes)
97044f68 File CHERRYPICKER_SHIP_BASELINE_STALE_1: SHIP baseline stale, bundles an unconfirmed backstory un-cut
6a16ce1c Close ANCIENT_RUINS_FAMILY_CUT_1; sync DROID_RETIRE_KOTORDROIDS_1's unblock note
aec2c70b Gate the 4 ungated kotorcore droid-weapon ammoDefs (unblocks DROID_RETIRE_KOTORDROIDS_1)
4d6c684e Cut the ancient-urban-ruins mod family (ANCIENT_RUINS_FAMILY_CUT_1)
8f753bec Owner rulings landed: Gemini trial authorized (billing was already live), richer moornak ships
c3083524 FUNGALFOREST_RAID_MERGE_1: ported defs verified clean, cut confirmed NOT yet safe (nothing ratified)
823b5ce7 Crystal doc: orange ore re-identified as pyrinth (owner); wrong KOTOR claim deleted, ingest row added
2f083312 Code review status: mark 19 skills/infra never-reviewed files clean (all genuinely clean)
6a7759f2 Close ASSIGNMENT_APPLIER_SCHEMA_REWRITE_1 (BENCH's work was done, never closed); clear MACRO_GENERATOR_V0_1's stale needs:owner
956c80cc SCORCHFRUIT_FULGURITE_DEF_VERIFY_1: closed, defs confirmed under renamed tier
450d3267 the_pyrelands.json: fix decayed RSW_FE_ -> RM_FE_ tier rename on ScorchFruit/Fulgurite
fe48c24e HUMAN_QUEUE_NEEDS_OWNER_RENDER_1: closed, false premise, real needs:owner audit delivered instead
6a9605da Clear 2 stale needs:owner flags (round-3 verdict already answered them); mark-clean the sibling-crash patch file
492520c2 Droidworks: Harmony prefix suppresses sibling-relation-gen crash for droids
b10344d6 Ledger sync: claim/start ANCIENT_RUINS_FAMILY_CUT_1
ac672b47 Lesson: stash/rebase during active subagent writes can silently revert their work
f7b345d8 Code review status: mark 353 never-reviewed files clean (wave 2)
e5c9d120 RUT_Wasteland.xml: remove a stray plantDensity element from the wildPlants dict
bb73b6bd Dirty-code-review wave 2: 16 real bugs across 353 never-reviewed files
1d096297 Owner rulings: ancient-ruins family cut ruled+closed, crystal identification reopened (wrong crystal)
e7d9bd4c Ledger sync: ASSIGNMENT_APPLIER_SCHEMA_REWRITE_1 note (applier rebuilt, commit 64ffdc02)
16087da5 ASSIGNMENT_APPLIER_SCHEMA_REWRITE_1: back out of a claim collision with BENCH
64ffdc02 ASSIGNMENT_APPLIER_SCHEMA_REWRITE_1: rebuild apply_assignment_verdicts.py for the 19e03876 schema
07f68e73 DROID_SIBLING_RELATION_GEN_CRASH_1: root cause found, mod-wide scope confirmed (all 52 races)
4a68c65f Ledger sync: claim/start MAPGEN_ROUND3_VERDICT_LANDING_1 close + 3 fresh FOUNDRY items
805d5983 Absorb round-3 mapgen verdict into MACRO_GENERATOR_V0_1, flag superseded plans
3075275f TILEGEN_SILENT_REUSE_1: third offline pass, found an untested premise gap, still inconclusive
718ed1f8 Fix ant sheet layout (figure/worker overlap)
0b896bad Transient: They! Giant Ants art contact sheet for the Fever Wood card
51a19559 Owner's round-3 mapgen grade landed: FAIL 0/8, painter held, GL sheet lead (via MAPGEN_ROUND3_VERDICT_LANDING_1; seat guard kept BENCH off FOUNDRY's item file)
206580c1 DROIDWORKS_PERSONALITY_VERIFY_1: live-verified, all 8 families pass; filed a sibling-relation-gen crash found along the way
ae6f10df Ledger sync: DROID_MODULE_BODYGROUP_WIRING_GAP_1 + DROIDWORKS_MODULE_PERSONALITY_1 closed, both live-verified
9a957bbb Ledger sync: three filings out of the sheet regen + backlog-audit review
19e03876 Biome assignment sheets rebuilt to the owner's 2026-09-09 rulings
449e9805 Droidworks: wire module BodyPartGroups onto vanilla Human's Waist part
58d7ae63 Code review status: mark 191 files clean (dirty-code-review wave, 2026-09-10)
3ea1ca20 Dirty-code-review wave: 9 real bugs found across 191 files, all verified
8df622a7 Live-tested DROIDWORKS_MODULE_PERSONALITY_1's wear/unequip mechanism: it fails
51783238 Ledger sync: 10 more doing-backlog reconciliations (batch-1 late report, verified)
c0018865 Ledger sync: STAT_NORMALIZATION_AUDIT_1 tree-resizing/Comigo scope note
e585ae24 STAT_NORMALIZATION_AUDIT_1: owner requests tree-resizing/Comigo mods in scope (not a ruling)
7dfa465e BIOME_ENRICHMENT_POISON_FOREST_1: record its real blocker as a causal link
5b98b3ed Doing-backlog audit: reconcile 25 items whose ledger state had drifted from their prose
3c5a1cc2 Revert ARTIST-as-seat: the Artist tile is the no-LLM artpipe daemon's console
c6a5f3f8 ARTIST becomes a real seat: Claude profile, identity file, interim standing orders
3aa26b6f Ledger sync: final codebase-health timestamp before reboot
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-11T02:31:45Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/state/codebase_health_last.json
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

