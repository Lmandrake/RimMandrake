# FOUNDRY_REBOOT_HANDOFF_202609110804 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609110402`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

15-agent parallel fanout (owner: "full belt, fan out, go big") works as a FOUNDRY
pattern when each agent gets its own `isolation:"worktree"` and the orchestrator
serializes ALL ledger/queue writes and merges (cherry-pick, close, commit, push)
centrally — never let subagents touch the ledger or push themselves. The failure
mode to guard against: a bare `git commit` in the shared main tree, even after
`git add <own files>`, still commits whatever ELSE is staged — it swept a
concurrent BENCH session's in-progress file rename into one of my commits
tonight (harmless this time, content was complete). Use the trailing-pathspec
form on every commit from here on: `git commit -m "..." -- <exact files>`.

`.git/index.lock` contention was near-constant with BENCH active in the same
physical tree — a retry loop (`fuser` to confirm no live holder, then `rm -f`
+ retry, ~15-20x @ 2s) cleared every stall safely.

## What the owner should see

- **RESEARCH_TRIO_RETIRE_1 blocked, needs his ruling**: steppingstones/gravtech
  own 17 `ResearchProjectDef`s nothing else defines (RUT_ResearchRetag only
  patches tab/tier onto them), several under his own dated rulings
  (GravWeapon/GravForge/GravBionics, 2026-09-01/09-04) a bare retire would
  silently reverse. Three routes laid out in `items/RESEARCH_TRIO_RETIRE_1.md`:
  port the 17 rows first, accept the content loss, or counter-patch and keep
  the mods.
- **BMT_FAUNA_ABSORPTION_1 partially done, retirement blocked on his call**:
  all 68 ruled `biomesteam.*` creatures ported to RSW_ tier clean, but the 3
  donor mods are NOT retired yet — 7 live defNames (ChemSnail/CaveSpider/
  GiantSlug/GiantSnail/Pillbug/GlowBat) are marked keep in hand-authored biome
  files but aren't in the ruled 68; needs a call on whether they're genuinely
  cut or the round-2 census undersold them.
- **Live ModsConfig.xml was edited directly tonight** (STAT_NORM_WAVE2/3):
  11 packageIds removed (Cephaloids/VE Succulents/VAE Waste donor, VSRexamined,
  SurvivalTools + their donor deps), all backed up first. His next cold load
  will look different from what he last saw.
- **5 new C# mods built tonight, zero live/deploy proof**: RUT_PyrelandsMechanics,
  mandrake.rm.environmentalhazards (Alpha kit), mandrake.rsw.brainworms,
  mandrake.rm.gelatinousslime, mandrake.rm.lorestages + mandrake.rut.scarlandsladder.
  All compile clean and validate_patch clean; none deployed, none seen running.
- SLIME_MOD_BUILD_1's build found the spec overestimated effort on one leg
  (world-pawn hediff ticking needs zero Harmony — vanilla already ticks every
  world pawn) — not urgent, just a correction for future estimates.
- Two independent fixes landed for the same MIASMA null-thingClass bug tonight
  (mine: redeploy; BENCH's, concurrently: moved the def file to live beside its
  SWBestiary parents) — not a conflict, BENCH's is the more permanent fix.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `BAREHANDED_MELEE_FALLBACK_1` — 15 of 18 ranged-only pawn kinds fixed with
  faction-voice melee tags, validator clean. `needs=bridge`: the 5 originally-
  undiagnosed kinds need a live per-pawn trait join via bridge spawn batches.
  Separately, 3 Geonosian kinds have no affordable in-voice melee tag (only
  candidate prices 20950 vs 400-1200 budgets) — noted on the item, needs an
  owner ruling on voice, not a bridge session.
- `GREENTIDE_FISH_ITEMS_FIX_1` — mechanism fixed (new RSW_*Catch item defs,
  patch retargeted off the race defs), validate_patch clean. `needs=bridge`:
  the item's own criteria require a live quicktest fishing pass to confirm a
  real item drops, not a bare Pawn — not yet run.
- `SHRINE_GUARDIAN_BIOME_GATE_1` — inherited from an earlier wave, NOT touched
  this window. Harmony postfix + XML already built and independently code-
  reviewed (commits `0bca15e89`/`0e94b4d27`). Still in `doing` because its own
  criteria's 2nd box ("quicktest-proven on at least one candidate biome") has
  never been run — next action per its own `## Verify`: quicktest on `Desert`
  and confirm the postfix substitutes AMBIENT-appropriate guardians/loot
  instead of the stock ancientTemple monument content.

## Traps learned

(All three filed to `LESSONS_INBOX.md` this session.)

- A bare `git commit` in this shared tree commits whatever else is staged,
  not just what you just `git add`ed — it swept a concurrent BENCH rename
  into a FOUNDRY commit tonight. Always `git commit -m "..." -- <files>`.
- `.git/index.lock` contention was near-constant with BENCH driving the same
  physical tree concurrently — `fuser`-checked stale-lock removal + retry
  (not blind `rm -f`) cleared every stall safely; never skip the fuser check.
- Cherry-picking into a JSON roster file another already-merged commit
  reformatted (`sort_keys=True` re-serialization) produces conflicts whose
  diff context looks unrelated to the real change — hand-apply the small
  semantic diff from `git show <sha> -- <file>` to the current-format file,
  `git checkout --ours` the path, `cherry-pick --continue`, rather than
  fighting the textual merge.

## Closed since the last handoff (16)

- `MECH_PRESENCE_ENFORCEMENT_1` — 023beee3
- `CHERRYPICKER_SHIP_BASELINE_STALE_1` — fb54a3f2
- `ROSTER_MOVE_APPLY_1` — 688bddbb27834541fca107add5f6f39b3baef03d
- `LAW3_RETARGET_RSW_1` — 63965c192f1d23023947b67c307040bafc9f79a4
- `ALPHA_MECHANICS_KIT_1` — ddd8d379f6d9f3127cfaa33f6429ee0c01f4f06f
- `PYRELANDS_MECHANICS_1` — 6946c18735f6064247a0e09463fd9d30b4596357
- `RESTORE_FALLOUT_TRIAGE_1` — 097ec3110668f27c0033e7e1e3ac3df0cec183d4
- `STAT_NORM_WAVE2_RETIRE_1` — 5ad48a0786581de88fc406927da789bb16f2b8b5
- `MIASMA_JUVENILES_NULL_THINGCLASS_1` — f1f305e177153efb4617d3e6f4a68c082caeb85b
- `BRAINWORM_MOD_BUILD_1` — 0d4f5701fbcd67fd21cbdcc408df5c84489677ab
- `STAT_NORM_WAVE3_RETIRE_1` — 329fbb55f1811d96815976c052687131ad611bc6
- `SLIME_MOD_BUILD_1` — c16236fdc899025db0fa163134ca5354afbb0099
- `STAGED_LORE_BUILD_1` — dd882616e5db8e972ffa9d646c07b778cc4f6cc4
- `SAND_STALKER_BADGER_SOUNDS_1` — b143edf32298e1f2c3b6d100ac6203a9deb09940
- `QUICKTEST_MAPGEN_NRE_1` — 2dd896ed07b21992f3038f75682aae17308474fa
- `FAUNA_STATS_BRIDGE_TOOL_1` — f45e7e78d10a0370c2ae1e866986a185d12e7756

## Filed and still open (5) — the next seat's queue

- `SHRINE_GUARDIAN_BIOME_GATE_1` — Harmony postfix on SymbolResolver_AncientTemple.Resolve to gate shrine guardian/loot per-biome (ANCIENT-ALLOW/RARE x AMBIENT-DENY) — piece 4/4 of MECH
- `BAREHANDED_MELEE_FALLBACK_1` — 18 of 23 bare-handed pawn kinds have 100% ranged weapon pools with zero melee fallback (shooting-disabled pawns spawn bare) - re-run pool join vs toda
- `GREENTIDE_FISH_ITEMS_FIX_1` — BiomeFishTypes_Greentide.xml lists scalefish RACE defs (RSW_Mee/Faa/Laa) in fishTypes instead of item defs -- fishing there makes a bare Pawn, no cate
- `BMT_FAUNA_ABSORPTION_1` — Port the 71 cast Beasts of the Rim creatures (41 in + 30 move per decisions_propagated) into our tier per the SWBestiary donor-retirement pattern, the
- `RESEARCH_TRIO_RETIRE_1` — Retire steppingstones + als.gravtech x2 and re-validate the research recost after the cut (owner ruled Wave 3 'fold into the research pass' 2026-09-11

## Commits

```
b836646f2 Close FAUNA_STATS_BRIDGE_TOOL_1: jawa/animal_stats built, compiled, 318 tools registered
f45e7e78d FAUNA_STATS_BRIDGE_TOOL_1: jawa/animal_stats companion tool
b732bb0d5 Close QUICKTEST_MAPGEN_NRE_1: same root cause as MIASMA_JUVENILES fix, already deployed
2dd896ed0 QUICKTEST_MAPGEN_NRE_1: root-caused, fix already deployed, live verify owed
3afdbb65c Close SAND_STALKER_BADGER_SOUNDS_1: retargeted to real Pawn_Rodent_* sounds
b143edf32 Fix RSW_SandStalker: retarget nonexistent Pawn_Badger_* sounds to Pawn_Rodent_*
8ca278efe FOUNDRY claims+starts next 3: FAUNA_STATS_BRIDGE_TOOL_1, SAND_STALKER_BADGER_SOUNDS_1, QUICKTEST_MAPGEN_NRE_1
2990adf53 QUICKTEST_MAPGEN_NRE_1 filed; worldmap review Phase-0 exporter staged
d21289cbf BMT_FAUNA_ABSORPTION_1: 68/68 ported, retirement blocked on 3 open items
a72757b9d BMT_FAUNA_ABSORPTION_1: port 68 biomesteam.* creatures to RSW_/SWBestiary tier
fc82d9030 Close STAGED_LORE_BUILD_1: staged-lore-description mechanism built and proven
dd882616e STAGED_LORE_BUILD_1: the staged-lore-description mechanism (engine + Scarlands ladder wiring)
662b578d3 Close SLIME_MOD_BUILD_1: Gelatinous Slime mod built, compiled, validated
c16236fdc SLIME_MOD_BUILD_1: the Gelatinous Slime universal mod, built to the ruled spec
c58e39ffd Close STAT_NORM_WAVE3_RETIRE_1: VSRexamined+SurvivalTools retired, 2 counter-patches landed
329fbb55f STAT_NORM_WAVE3_RETIRE_1: retire VSRexamined+SurvivalTools, counter-patch CaravanAdventures + More Vanilla Textures to neutral
2e7aa9cff Close BRAINWORM_MOD_BUILD_1: RSW Geonosian brain worms built, compiled, validated
0d4f5701f BRAINWORM_MOD_BUILD_1: Geonosian brain worms, RSW tier
f01f06869 Close MIASMA_JUVENILES_NULL_THINGCLASS_1: root cause was stale SWBestiary deploy
f1f305e17 MIASMA_JUVENILES_NULL_THINGCLASS_1: root-caused as SWBestiary deploy drift, fixed by redeploy
19830ab40 Close STAT_NORM_WAVE2_RETIRE_1: Wave 2 remainder ported+retired
5ad48a078 STAT_NORM_WAVE2_RETIRE_1: port Cephaloids/VE Succulents/VAE Waste's Megatardi, verify+retire 6 more
720ccb5bb Close RESTORE_FALLOUT_TRIAGE_1: cross-ref/duplicate fallout fixed, redeployed; file badger-sounds separately
097ec3110 RESTORE_FALLOUT_TRIAGE_1: fix biome animal-record duplicates from the CherryPicker restore
9077211da Record PYRELANDS_MECHANICS_1 close event in ledger (commit landed separately)
6946c1873 PYRELANDS_MECHANICS_1: the igniter kit, built (new RUT-tier mod PyrelandsMechanics)
b35c3dc14 the_pyrelands.json: manually reconcile PYRELANDS_MECHANICS_1's fauna-row updates
636192203 Close ALPHA_MECHANICS_KIT_1: all 6 generalized comps built, compiled, validated
313a39c66 Belt-mode consolidation: 20-card owner sitting + graphs sitting filed with prose; biomesteam retirement half HELD on the two-rulings conflict; Wave-2 registry facts recorded
ddd8d379f ALPHA_MECHANICS_KIT_1: RM-tier generalized mechanics kit, all six comps
c3e71385b Land GREENTIDE_FISH_ITEMS_FIX_1 mechanism fix, needs bridge for live proof
240111d8d GREENTIDE_FISH_ITEMS_FIX_1: fish the Greentide for items, not Pawns
a712b1765 Land BAREHANDED_MELEE_FALLBACK_1 progress (15/18 fixed), block RESEARCH_TRIO_RETIRE_1
0167e7af8 Three C# kit specs installed (Greentide 12 / Webwork 7 / Scarlands 5 mechanics, engine-verified) + Owed pointers; KIT_SPECS_CARD_SITTING_1 (18 cards) and FAUNA_GRAPHS_SITTING_1 filed for the owner's return
1dd78b9cf BAREHANDED_MELEE_FALLBACK_1: melee fallback tags for 15 of 18 ranged-only kinds
67265094e RESEARCH_TRIO_RETIRE_1: escalate, do not execute — steppingstones/gravtech own the tree nodes they'd delete
d647b7db4 TERRAMANUFACTURE_CANON_1: propagate the factory/dynamo/war-lab ruling into 5 canon docs
63965c192 LAW3_RETARGET_RSW_1: add RSW_ fork operations to BeastNorm Law 3, do not retarget/prune
300c3d349 Ledger sync: fauna graphs built, stats tool re-scoped, four design lanes claimed
06c0a1be1 Canonical fauna graphs v1: 326 rostered animals from the fresh 579-mod inventory — damage/DPS vs bodySize with Law-3 bands, temp tolerance by domain (23 narrow), meat explicit on only 14
50dca0bd8 BMT_FAUNA_ABSORPTION_1: owner corrects donor to biomesteam.*, unblocked
0d7759d67 Close ROSTER_MOVE_APPLY_1: 114/114 ruled fauna moves landed, validate --cross clean
688bddbb2 ROSTER_MOVE_APPLY_1: land all 114 ruled fauna moves into biomes/rosters
0aba1bf96 Block BMT_FAUNA_ABSORPTION_1: item's donor and creature count contradict each other
a9692352a BMT_FAUNA_ABSORPTION_1: escalate — donor mod and creature count don't match
0d1ad7a8d Bridge sitting: Oracle + ScavengerEvents CONFIRMED RUNNING; game at main menu; get_defs cannot harvest fauna stats (MEASURED) — FAUNA_STATS_BRIDGE_TOOL_1 filed
d54ba753f FOUNDRY claims+starts full belt: 15 proposed items to doing
e7bcf0217 Ledger sync: STAGED_LORE_DESCRIPTIONS_1 closed, STAGED_LORE_BUILD_1 filed
927fc9f00 STAGED_LORE_DESCRIPTIONS_1: owner GO — build filed as STAGED_LORE_BUILD_1
c58f0ac77 STAT_NORMALIZATION_AUDIT_1 closed: all four waves ruled, execution in the wave items
85cabcfde Wave 4 ruled: all keeps confirmed as permanent residents, Big and Small experiment reconfirmed, MV Textures drawSize counter-patch — every wave of the stat audit now ruled
daeef5831 Capture new FULL.LATEST modlist baseline (579 active), release bridge
66aaa3dce File MIASMA_JUVENILES_NULL_THINGCLASS_1: 7 juvenile ThingDefs load with null thingClass
4d9546e36 Wave 3 ruled: work-speed pair retires together, complexjobs declared resident, caravanadventures strip-stats-keep-quests, research trio carried by RESEARCH_TRIO_RETIRE_1 (the pass it was to fold into is closed)
0e6b1137e Wave 2 ruled: BMT port-then-retire (71 cast), Cephaloids/Succulents/VAEWaste-used port-then-retire, unused five verify-then-retire; BMT_FAUNA_ABSORPTION_1 + STAT_NORM_WAVE2_RETIRE_1 filed
5ca10e50f Expected-failure signatures for second batch-restart pass
23fe959da LAW3_RETARGET_RSW_1 filed: BeastNorm Law 3 no-ops live — 105 xpaths target bare donor names, RSW_ forks carry raw stats (Bantha 23 vs ruled 60.0, MEASURED)
0df6a3c59 Notes: Aftermath rule 4 and Inhabited road_warehouse build results
7fcf553f0 Merge branch 'worktree-agent-a0e24dde9450bb1dd'
35d2509b2 Merge branch 'worktree-agent-a09a9efeb0318007a'
a1ff87b68 INHABITED_AUGMENTATION_BUILD_1: wire road_warehouse.lua (8.5), correct the item's wiring census
39da0b74f PLOT_MECHANISM_MODS_WAVE_1: wire Aftermath rule 4 (They come for their own)
e0283248f Merge branch 'worktree-agent-ad4da7aed7d67e97d'
b2b5bea77 Full-file review: 3 dirty files clean, no bugs found
6a3b78b54 File GREENTIDE_FISH_ITEMS_FIX_1: fishTypes lists race defs, not items
9a7dc1dc8 Merge branch 'worktree-agent-a7b2f64a1425044d3'
696a03d86 Note: macro generator round-4 design options delivered
42e964de5 FISH_BESTIARY_COMMISSION_1: evening reconciliation — Greentide fishTypes wires race defs, 3 scalefish catch items owed; bladderboil folded in
4c857fee3 Merge branch 'worktree-agent-ae9453b13f0ddd01d'
1664012fd MACRO_GENERATOR_V0_1: round-4 chooser as OPTIONS - three 8-premise sets on one silhouette sheet (Fable design pass, not ruled)
839c5ad25 Notes: DroidRepairJobs verified clean, both it and Mynock re-added to ModsConfig
5fa7e55af WORLDMAP_FINAL_REVIEW_1: save-vs-bundle elevation+hilliness agree 21872/21872 (MEASURED); biome half needs a fresh dump
50f52d6e0 Restart triage: RESTORE_FALLOUT_TRIAGE_1 (config errors 95 vs 23, orphaned juveniles, dup records) + BAREHANDED_MELEE_FALLBACK_1 (18 ranged-only pools) filed; shrine-guardian measured NOT built (source only), noted on its item
86aba7dc4 GOAL_SHEET first honest scoring: 20 boxes ticked on verified evidence, 115 stay open
b40cadf81 Quickgrass built and deployed: RM_FE_Plant_Quickgrass (Rakatan forage lawn), all generic grasses evicted from Pyrelands per owner ruling; flora move mapping for the 6 unparseable rows
0777dfc43 Lesson: merge commits need git merge --continue, not git commit, under block_blanket_git_stage.py
3b9a69f87 Merge branch 'worktree-agent-ab04b4d40052f3631'
0bca15e89 Shrine-guardian biome gate: AmbientShrineGuardians.cs/xml (SHRINE_GUARDIAN_BIOME_GATE_1)
0845c3356 CODE_REVIEW_STATUS: mark 6 files clean after independent review
d328d7f4c Ledger sync: GEONOSIAN_BRAINWORM_MORPH_1 closed, BRAINWORM_MOD_BUILD_1 filed
94ba19d25 Brain worms reviewed: corpse-walker ruled out permanently ('too gross'), three vectors ruled (ruins, cargo, weaponized-egg retribution); BRAINWORM_MOD_BUILD_1 filed
d72e96a36 Notes: Ninefold gravship postfix fix details, tree-mod deep dive findings
0e94b4d27 SHRINE_GUARDIAN_BIOME_GATE_1: independent bug-hunt review of AmbientShrineGuardians
56a66500b TwinkleFloraSpike.cs: guard against pulseSteps<2 causing a NaN pulse color
c093c2288 CHERRYPICKER_SHIP_BASELINE_STALE_1 closed: 141 genuine reversals restored, new SHIP baseline captured
fb54a3f2b Merge branch 'worktree-agent-a0cd572bddd72c1ae'
35298ea68 RUT_PyrelandsFauna.xml: fix dead/mis-bound melee tools found in code review
611304868 NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1: hook the gravship at its own takeoff
222d945ba Mirror retirement remainder: tombstone committed, review entries pruned, QUEUE_GITHUB_MIRROR_1 retirement noted; maturity dashboard regenerated
3644bbe9c Merge: resolve CODE_REVIEW_STATUS.json conflict, both ScavengerEvents review batches
1c46266d3 mark-clean: 7 ScavengerEvents files (RUT_SCAVENGEREVENTS_BUILD_1 pre-load review)
6600bba5e FAUNA_TOLERANCE_NORMALIZATION_1 filed (biome-aware tolerance law + Law 3 full-roster extension); GitHub mirror synced, tickets board regenerated (249) and republished
60dd1ce2f RUT_SCAVENGEREVENTS_BUILD_1: fix Thanksgiving's player-faction lookup
2449bb166 Merge branch 'worktree-agent-a150eb5658219d23a'
447b6a1eb Mark ScavengerEvents incident workers CLEAN after first full-file review
339af58e3 Owner rulings + fan-out findings: all six Alpha comps ruled in (ALPHA_MECHANICS_KIT_1 filed, source review closed); ROSTER_MOVE_APPLY_1 filed — 0 of 114 ruled fauna moves ever reached rosters (MEASURED)
c4a2ec830 DIRTY_CODE_REVIEW_STANDING_LOOP_1: wave note, 5 bugs found across 27 files
aa88e3f0f Expected-failure signatures for tonight's batch restart
73ca1d89f Merge branch 'worktree-agent-a67e163ba311124cb'
c93cacf12 Merge branch 'worktree-agent-a1f30ff7c1434715f'
a48c29174 Merge branch 'worktree-agent-a5ce326bfbead68e1'
daa21d2ee Mark clean: validate_patch.py, JawaBenchLandmarkNameTool.cs, Pyrelands.xml, artpiped.py
263492eca Clean marks: Ashkarr biome/landmark defs and cast/tolerance patches
8abbec7ba jawa/world_landmark_rename: match tile by PlanetTile, not raw tileId
ac920c1fd Mark clean: Armoury_RangedDamage.xml + 3 SeaBeasts defs + Protovermes absorption
21ca544a9 mark-clean: 6 files from the Doctrine/StructureInjectionsRUT dirty-review wave
4b81823b7 DroidsAreMachines.xml: correct header left stale by the ABF Operation removal
a264b2d34 Doctrine About.xml: remove 3 loadAfter entries dead against current patch set
d3ffec032 RUT_Scarlands: restore extraGenSteps, missing since the def has no ParentName
1c708ea4d validate_patch.py: fix unguarded-op check missing bare Sequence nesting
ecccefa4c Ledger pass on wake: CREATURE_ART_REVIEW_SHEET_1 superseded-closed, FLORA_COMMISSION_TEMPLATE_1 + PALETTE_ANCHOR_DRAFT_1 + GELATINOUS_SLIME_MOD_1 closed, PYRELANDS_MECHANICS_1 prose written + to FOUNDRY, SLIME_MOD_BUILD_1 filed
0ca7aa20e CREATURE_ART_REVIEW_SHEET_1 closed: superseded by the 09-10 sitting's per-row art verdicts
24e86a87c Record clean marks: naming_lint, animal_tolerances, animal/thing contact sheets, extract_bundle_textures
05e084a55 naming_lint.py: strip XML comments before defName scan, fix Windows path check
a6a9316c6 BENCH reboot handoff 202609110230: cast wave complete, commission wave staged, all sittings drained
0daf1a65e Wave-2 brief: fold in all eight owner rulings; RUT_FurnaceHide item brief (§12)
6e94a086f Wave-2 final hand: chittik carve-out, one-species bolts, sacrilege hookup, bespoke furnace hide
4a6f6200b Wave-2 rulings: both igniters tameable (ban 5 reversed in sheet), spread-only ratified, ilverr corona accepted, Mechachicken cut; mechanoid audit clean
bafcf19b6 MECH_PRESENCE_ENFORCEMENT_1 closed: XML-only scope done, shrine-guardian piece spun off
023beee3b GELATINOUS_SLIME_MOD_1: fold round-2 rulings into the design doc
684f0a8df Homeless dispositions APPLIED: 6 placed, 25 cut, 9 trader, 18 ninth-roster, 67 reserved; bug-faction law recorded; sitting closed
fbe09dcf1 Homeless disposition sitting COMPLETE: owner's 125-row verdict file, frozen (24 writes, 17 overrides)
d5ca9a795 GELATINOUS_SLIME_MOD_1: round-2 card rulings - handheld scanner-extractor-injector redesign, salt ocean dries, rarity slider, flavor as options
09ccf5f74 GELATINOUS_SLIME_MOD_1: re-scope slimification to a RimMandrake-tier universal mod
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     WORLDMAP_FINAL_REVIEW_1 Phase 0-2: load canonical save, fresh exports, audits, STARE screenshots

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/state/codebase_health_last.json
 M src/RimStarWars/Armoury/Patches/Armour_Leather.xml
 M src/RimStarWars/Armoury/Patches/Armoury_RangedDamage.xml
 M src/RimStarWars/Armoury/Patches/Armoury_TorpedoSpeed.xml
 M src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_NurseryJuveniles.xml
 M src/RimUtinni/ScavengerEvents/Assemblies/RimMandrake.Utinni.ScavengerEvents.dll
?? defs.sqlite
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? src/RimStarWars/Armoury/Textures/Things/Item/Resource/Crystal/
```

