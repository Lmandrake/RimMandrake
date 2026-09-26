# BENCH_REBOOT_HANDOFF_202609260401 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609260109`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Item prose keeps its "open question" text after the ruling lands, so a prose harvest of owner questions is mostly stale.** Tonight a harvester's list produced 4 re-asked questions the owner had already ruled (egg black market, roach parts, Frenzy mood, thief birds) and 2 false premises (the "never-activated" mods and the "missing" quest mod were active all along, MEASURED by parse). Before carding any harvested question, grep the ledger shards for its topic and look for a sibling item. (see: LESSONS_INBOX, memory verify-open-questions-against-ledger)

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **33 rulings landed tonight by card/typed answer**, all on their items/ledger: Deepfire Q5 (salt or boiling only, haul water if inland — spec §2.5/§11 folded), graffiti (wildstyle+stencil, every meme a glyph, crown stencil + RSW Imperial cog, Shipborn hull-and-star), droid letters (**Narrator, third person — he reversed first-person**; late OK; all four consumers live; programmable never; share gods' budget; battle tone varies; ship fixed lines now), grate passes burning oil, sluice = pit size cutoff, rat stays wreck-only, both donor ports in parallel, sarlacc stages Seeker/Digger/Dreamer/Devourer, WreckedMachines gets settings, dune burial = setting default off, Pyrelands gets a real grazer, Scald water is SALT, brine fish by dredging, guardian = Bark-warden, dianoga memory dropped ("just that hard to tame"), stench repels all animals, toxin water hurts anyone, mobile plants hurt all / jungle only, jungle danger flat, payoff = survivors become specialists, NEW canopy swarm layer, Shokkweave harvest job build now.
- He skipped the fluid-join question (oil meets poison in a dug channel) — still open on PIT_SUPERDEEP_COLLAPSE_1.
- Still needs his eyes: Scald save walk (game UP, loaded for it), Deepfire art sheet `D:\Luke\dev\Rimworld\Transient\deepfire_pigment_review.html` (refresh first; 4 renders are in done/), graffiti candidate glyphs `D:\Luke\dev\Rimworld\Transient\graffiti_generic_marks_contact_sheet_2026-09-09.png`, droid register rows other than Battle.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `DROID_ORACLE_VOICE_DESIGN_1` -- all 7 questions ruled except register rows 2-8; doc §1 still says first person; NEXT: rewrite design/RimMandrake/droid_oracle_voice_design.md to the Narrator/third-person ruling and fold Q2/Q3/Q5/Q6/Q7.
- `UTINNIPATCHES_LOAD_ORDER_CYCLE_1` -- filed for FOUNDRY tonight (loadAfter cycle patches<->rustcathedralroaches, 6 deps misordered); NEXT: FOUNDRY decides the real edge and topo-sorts both modlists.
- `SEA_DIVE_MAPS_BUILD_1` -- owner card: hand to FOUNDRY only after the Scald walk; NEXT: walk SCALD_REVIEW with him, then re-file for FOUNDRY.
- `DEEPFIRE_PIGMENT_MOD_1` -- spec fully ruled (Q5 folded tonight); NEXT: refresh the art sheet, get his ruling, re-file for FOUNDRY.
- `SHRUBLAND_TREE_GUARDIAN_1` -- named Bark-warden; tier open (invented name -> RM_ or RUT_ per Q11a, not RSW); NEXT: pick the tier by the Q11a test and fold into sweetline_guardian_spec.md §11.
- `harvested_questions` -- not yet asked and UNVERIFIED against the ledger: kyber trade history (KYBER_TRADE_PLOT_1 K1), Forge plants RUT_->RM_ rename, Rakatan endgame gods, Bazaar stolen-goods tuning, Contagion site purpose, extract CHURN->BURST; NEXT: grep ledger shards per topic, card only the genuinely open ones.
- Carried from prior handoff, untouched tonight: STATUE_ART_EXPANSION_1 (fold O1-O4 into spec), SEA_SHORE_TILE_MUTATOR_1 (confirm coast water), SCALD_STEAM_WEATHER_DESIGN_1 (quicktest step 1), JAWA_SWIM_HOOD_KEEP_1 (look with owner), SCALD_FLOOR_PASS_1 (contact-sheet scald2 renders); NEXT: each as written in BENCH_REBOOT_HANDOFF_202609260109.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A prose harvest of "open owner questions" returns already-ruled ones; verify each against the ledger first (filed: LESSONS_INBOX).
- UtinniPatches' loadAfter and the live list disagree, including a true cycle with RustCathedralRoaches (see: UTINNIPATCHES_LOAD_ORDER_CYCLE_1).
- `rimflow file` takes no `--text`; file first, then `note --text` (see: using-rimflow skill).

## Closed since the last handoff (1)

- `OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1` — 35dc68cca

## Filed and still open (1) — the next seat's queue

- `UTINNIPATCHES_LOAD_ORDER_CYCLE_1` — UtinniPatches loads before 6 of its loadAfter targets; cycle with RustCathedralRoaches

## Commits

```
7d01cd0e7 GELATINOUSSLIME_RM_MOD_BUILD_1 step 3: freeze RUT_Slime.xml
f1c12c83d LESSONS_INBOX: verify harvested owner questions against the ledger
641604174 DIRTY_CODE_REVIEW_STANDING_LOOP_1: wave 11 — PropaneLakeMechanics gas-vent/saturation/incident cluster clean
73c23c474 Ledger: Greentide payoff + canopy swarm, toxin water, Shokkweave job ruled
c06d4b891 Closes: MIASMA_RM_MOD_BUILD_1
2438d5458 MIASMA_RM_MOD_BUILD_1: route Star Wars fauna through a Utinni patch; retarget docs
aba102c8d MIASMA_RM_MOD_BUILD_1: build RM_Miasma as its own RimMandrake mod
476c99a55 Ledger: dianoga memory dropped (owner); stench, mobile plants, jungle danger ruled
ef94514b6 STONEBACK_BOKKA_ART_STANDARD_1: regen still pending, daemon's own validator has failed it twice
6aec5e93a Closes: CONTAGION_RM_MOD_BUILD_1
209985e76 Ledger: card rulings — Pyrelands grazer, Scald salt, brine-fish dredge, Bark-warden
33db46fed CONTAGION_RM_MOD_BUILD_1: retarget RUT_Contagion -> RM_Contagion references + paint list
7283c26b9 CONTAGION_RM_MOD_BUILD_1: build RM_Contagion as its own RimMandrake mod
d4bd7f831 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 10: mark 6 PropaneLakeMechanics pipe-network files CLEAN
01c8932b7 Ledger sync: close THEFORGE_RM_MOD_BUILD_1
86ddebac7 THEFORGE_RM_MOD_BUILD_1: build RM_TheForge as its own RimMandrake mod
9c4fffedf Ledger: close stale never-activated item (both mods active since 09-20/21); file UtinniPatches load-order cycle; sarlacc/wreck/dune rulings
35dc68cca WORLD_LABEL_SIZE_HIERARCHY_1: derive world-feature label sizes from a tile-count curve
41011b5c5 Closes: PYRELANDS_RM_MOD_BUILD_1
28b1922e6 Ledger: card rulings — desert rat, donor port order, activate three dark mods
... 28 more: git log --oneline 6aab55492..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-26T01:08:29Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   auto-regenerated health artifacts (take either side)
 M Transient/codebase_health.json   auto-regenerated health artifacts (take either side)
 M Transient/codebase_health_artifact.html   auto-regenerated health artifacts (take either side)
 M design/Jawa/mods/biome_flora.py   not mine — a peer window's uncommitted edit; leave alone
 M design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md   not mine — a peer window's uncommitted edit; leave alone
 M design/Jawa/worldbuilding/biomes/lantern_deeps_flora_names.md   not mine — a peer window's uncommitted edit; leave alone
 M design/Jawa/worldbuilding/biomes/rosters/the_slime.json   not mine — a peer window's uncommitted edit; leave alone
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_crowncarpet_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_crowncarpet_b.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_pigmentjar_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_pigmentjar_b.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/registry.jsonl   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/throughput.jsonl   artpipe daemon's churn — never commit mid-flight
 M infrastructure/dashboards/hub/data/health.json   auto-regenerated health artifacts (take either side)
 M infrastructure/state/codebase_health_last.json   auto-regenerated health artifacts (take either side)
 M infrastructure/state/facts/biome_paint_list.md   not mine — a peer window's uncommitted edit; leave alone
 M infrastructure/state/items/GELATINOUSSLIME_RM_MOD_BUILD_1.md   not mine — a peer window's uncommitted edit; leave alone
 M infrastructure/state/queue/BENCH.md   rimflow render projection — regenerate, don't hand-commit
 M infrastructure/state/queue/FOUNDRY.md   rimflow render projection — regenerate, don't hand-commit
 M skills/rimworld-debug-testing/SKILL.md   not mine — a peer window's uncommitted edit; leave alone
 M skills/rimworld-sprite-facings/SKILL.md   not mine — a peer window's uncommitted edit; leave alone
 M src/RimMandrake/GelatinousSlime/Assemblies/RimMandrakeGelatinousSlime.dll   not mine — a peer window's uncommitted edit; leave alone
 M src/RimMandrake/GelatinousSlime/Source/SlimeVisitors.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/ART_JOBS.md   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/About/About.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Assemblies/RimMandrake.Utinni.LanternDeeps.dll   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/Biomes/RUT_LanternDeeps.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/MapGeneration/RUT_LanternDeepEmergence_Scatter.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/MapGeneration/RUT_LanternDeepFloraGate.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/MapGeneration/RUT_LanternDeepGenerator.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/MapGeneration/RUT_LanternDeepKyberScatter.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/MapGeneration/RUT_LanternDeepMineshaft_Scatter.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/MapGeneration/RUT_LanternDeepPyrinthScatter.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/MapGeneration/RUT_LanternstoneFormations.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/MapGeneration/RUT_LanternstoneRock.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/SoundDefs/RUT_DeepAmbience.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/TerrainDefs/RUT_LanternstoneTerrain.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/ThingDefs_Buildings/RUT_LanternDeepEmergence.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/ThingDefs_Buildings/RUT_LanternDeepMineshaft.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/ThingDefs_Items/RUT_LanternstoneItems.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/ThingDefs_Natural/RUT_LanternstoneFormations.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/ThingDefs_Natural/RUT_LanternstoneWall.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/ThingDefs_Plants/RUT_DeepFlora.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/ThingDefs_Plants/RUT_LanternstoneSowable.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Defs/Weather/RUT_DeepCalm.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/LICENSE   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepEmergence_MapGenPatch.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepEvictCrystalFauna.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepGateKotorStygium.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepGateKyber.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepGatePyrinth.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepIncidentSuppression.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepMineshaft_MapGenPatch.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Patches/RUT_LanternstoneFictionRename.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Patches/RUT_LanternstoneKotorCrystals.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/DeepFloraPlanter.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/GenStep_DeepFloraGate.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/GenStep_LanternstoneRock.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/GenStep_ScatterCavePortal.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/GenStep_ScatterLanternstone.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/GenStep_ScatterMineshaftPortal.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/LanternDeepsMod.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/MapComponent_DeepFloraRegrowth.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/MapComponent_LanternDeepDarkness.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/Patch_PocketMapGrowthRate.cs   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Source/RimMandrake.Utinni.LanternDeeps.csproj   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Terrains/Lanternstone.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Chunks/LanternstoneChunk/a.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Chunks/LanternstoneChunk/b.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Chunks/LanternstoneChunk/c.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Chunks/LanternstoneChunk/d.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneHuge/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneHuge/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneLarge/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneLarge/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneMedium/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneMedium/C.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneSmall/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneSmall/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneSmall/C.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneSowableImmature.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneSowableImmature/a.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Item/Crops/PufferTendrils.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Item/Lanternstone/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Item/Lanternstone/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Item/Lanternstone/C.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Natural/Linked/lanternstone_wall_atlas.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Natural/Linked/lanternstone_wall_icon.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Natural/Linked/smoothedlanternstone_wall_atlas.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/BrellikBulb/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/BrellikBulb/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/KuvraSpout/a.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/KuvraSpout/b.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/Mycelium/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/Mycelium/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/Mycelium/C.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/NurrikGill/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/NurrikGill/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/OsskBramble/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/OsskBramble/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/PrennaLace/PrennaLaceGrown/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/PrennaLace/PrennaLaceGrown/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/PrennaLace/PrennaLaceGrown/C.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/PrennaLace/PrennaLaceImmature/a.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/QuorrFern/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/QuorrFern/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/QuorrFern/C.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/QuorrFern/D.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/ThrakkCap/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/ThrakkCap/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/TwitchingPuffer/PufferGrown/a.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/TwitchingPuffer/PufferHarvested/a.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/TwitchingPuffer/PufferImmature/a.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/VellokReed/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/VellokReed/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/ZivvitTaper/A.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Plant/ZivvitTaper/B.png   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/build_art_sheet.py   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/build_species_sheet.py   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/tint_organics.py   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/validation.py   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/LanternDeeps/wire_art.py   not mine — a peer window's uncommitted edit; leave alone
 M src/RimUtinni/UtinniPatches/About/About.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/EffecterDefs/RM_KrissekHalo.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/HediffDefs/RM_BlueDesertCharges.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RM_ColdWax.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RM_BlueDesertFlora.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RM_BlueDesertFauna.xml   not mine — a peer window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Source/BlueDesertLife.cs   not mine — a peer window's uncommitted edit; leave alone
?? deployed/config/ModsConfig.before-tier-firehawk.xml   FOUNDRY/modset backups — leave alone
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   FOUNDRY/modset backups — leave alone
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   FOUNDRY/modset backups — leave alone
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_kessik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_kessik_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_kessik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_kessik_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_thrizzik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_thrizzik_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_thrizzik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_thrizzik_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/deepfire_pigmentjar_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/deepfire_pigmentjar_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/deepfire_pigmentjar_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/deepfire_pigmentjar_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_wildhealroot.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rut_wildhealroot.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutbloomcrop_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutbloomcrop_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdarkcrust_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdarkcrust_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdeltaloam_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdeltaloam_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutfuzz_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutfuzz_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglower_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglower_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglowercrust_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutglowercrust_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseed_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseed_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutvaultroot_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutvaultroot_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_shullacatch_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_shullacatch_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_shullacatch_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_shullacatch_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_steamcatchbuilding_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_steamcatchbuilding_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ventbuilding_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ventbuilding_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ventbuilding_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_ventbuilding_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_b.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_c.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_saalcatch_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_saalcatch_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shullacatch_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_shullacatch_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_ventbuilding_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_ventbuilding_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckframe_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckframe_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckhull_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckhull_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wrecktank_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/scald_wrecktank_v1.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/crags_kessik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/crags_kessik_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/crags_thrizzik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/crags_thrizzik_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rut_firehawk_flying_v2_2_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rut_firehawk_flying_v2_2_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/scald2_shullacatch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/scald2_shullacatch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_essarn_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_essarn_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_essarn_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_fessk_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_fessk_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_fessk_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_otheska_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_otheska_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_otheska_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_sorruth_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_sorruth_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/greysea_sorruth_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_mahllik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/nightside_zhissa_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_heemin_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_heemin_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_heemin_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_body_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_body_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_body_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_atlas.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_menuicon.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_bezzul_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_greateroomb_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_hennul_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_mubbaro_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_oomb_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_thummorak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_vohhm_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuppik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_wuum_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/slime_yollum_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   FOUNDRY/modset backups — leave alone
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   FOUNDRY/modset backups — leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   FOUNDRY/modset backups — leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   FOUNDRY/modset backups — leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   FOUNDRY/modset backups — leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   FOUNDRY/modset backups — leave alone
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   FOUNDRY/modset backups — leave alone
?? src/RimMandrake/GelatinousSlime/Assemblies/RimMandrakeGelatinousSlime.dll.srchash   not mine — a peer window's uncommitted edit; leave alone
?? src/RimMandrake/GelatinousSlime/Defs/GenStepDefs/   not mine — a peer window's uncommitted edit; leave alone
?? src/RimMandrake/GelatinousSlime/Patches/RM_SlimeVisitorSeed_MapGenPatch.xml   not mine — a peer window's uncommitted edit; leave alone
?? src/RimMandrake/LanternDeeps/   not mine — a peer window's uncommitted edit; leave alone
?? src/RimMandrake/Utils/firehawk_flight_probe.py   not mine — a peer window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_LanternDeepKyberScatter.xml   not mine — a peer window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Patches/RUT_LanternDeepGateKotorStygium.xml   not mine — a peer window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Patches/RUT_LanternDeepGateKyber.xml   not mine — a peer window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Patches/RUT_LanternstoneKotorCrystals.xml   not mine — a peer window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Patches/WildAnimals_LanternDeeps.xml   not mine — a peer window's uncommitted edit; leave alone
```

