# BENCH_REBOOT_HANDOFF_202609260650 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609260401`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**A sea biome's `wildAnimals` can never ambient-spawn its cast on its own generated map, and a short-window zero from the spawner proves nothing.** MEASURED live (tile 7345 re-tiled `RM_TheScald`, map generated on the full list): the spawn chooser reads `BiomeAt(cell)` PER CELL (`MixedBiomeMapComponent`), so every standable cell belongs to the blend/secondary biome while the sea's own cells are the unstandable water — gen seeded 5 donor Gorg and 0 of 6 Scald entries though all 6 kinds resolve live. And the tick spawner is `Rand.Chance(0.027×density)` per 1213 ticks (~0.4%/roll at density 0.15), so never cite a few-thousand-tick zero. ⇒ dive/floor maps seed their own cast; sea `wildAnimals` rows still feed tile-level consumers (herd migration, animal ambush). Full account: SEA_DIVE_MAPS_BUILD_1 notes 2026-09-26 (item now closed — the notes survive in `items/closed/` and the ledger).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Swimming Jawa loses the hood, confirmed live with him watching** (he saw Gundozer's face). Evidence `D:\Luke\dev\Rimworld\Transient\jawa_swim_synced_20260926.png`; cause + fix shape on `JAWA_SWIM_HOOD_KEEP_1`. He knows; nothing more needed from him until the fix exists.
- **Deepfire crowncarpet regen renders** (`deepfire_crowncarpet_c` done, `d` in flight as of wrap) — his sedate/organic/gross directive applied; he should look before FOUNDRY wires mat art.
- **The seven non-Battle droid register rows** (`droid_oracle_voice_design.md` §2.2) are the only open rulings on that design — a card sitting when he has appetite.
- Shipped deliberately, flag raised: 6 of his 8 sheet overrides carried no reason; the one written note was read as the group rule (rainbow-loud = wrong everywhere) and drove both regen prompts. If that generalisation overreached, the regen prompts are where it landed.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `JAWA_SWIM_HOOD_KEEP_1` -- live FAIL, cause identified (hood node culled with the head under `parms.swimming`); NEXT: give `PawnRenderNodeWorker_JawaHoodFallback` its own swim-parms draw override, redeploy JawaRules at game-down, then look at a swimming AND sleeping Jawa with the owner.
- `DROID_ORACLE_VOICE_DESIGN_1` -- doc rewritten to rulings, item/INDEX corrected; NEXT: card the seven non-Battle register rows (§2.2) to the owner, then re-file the build for FOUNDRY.
- `SHRUBLAND_TREE_GUARDIAN_1` -- tier+name ruled and fully folded (RM_Barkwarden); NEXT: file the build item from the spec's "Build handoff" section and close this design item against it.
- `DEEPFIRE_PIGMENT_MOD_1` -- at FOUNDRY, spec+art ruled; regen `deepfire_crowncarpet_c` done / `d` in flight; NEXT: show the owner both new crowncarpet renders (BENCH's half) before FOUNDRY wires mat art.
- `SCALD_STEAM_WEATHER_DESIGN_1` -- untouched this session AND its protection ladder is now stale twice over (gear-matrix ruling + ship-only-dive ruling); NEXT: re-express the wrap→Royal Rind→boil-suit→vacsuit ladder on the two-axis gear matrix recorded on SEA_DIVE_MAPS_BUILD_1's notes before anyone builds from it.
- `SEA_SHORE_TILE_MUTATOR_1` -- untouched; the ship-only ruling makes "shore dive entry" prose false anywhere it appears; NEXT: sweep the item + mutator docs for dive-from-shore language and delete it.
- `STATUE_ART_EXPANSION_1` -- carried untouched again (second handoff running); NEXT: fold O1-O4 into the spec or drop the pointer deliberately.
- `harvested_questions` (no item id, carried from 202609260401) -- six candidate owner questions still UNVERIFIED against the ledger (kyber trade history, Forge plants rename, Rakatan endgame gods, Bazaar stolen-goods tuning, Contagion site purpose, extract CHURN->BURST); NEXT: grep the ledger shards per topic and card only the genuinely open ones.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Screenshots of pawns moved by `step_game_ticks` while paused show stale tween positions — unpause ~1s before shooting a moved pawn (filed: LESSONS_INBOX).
- `block_forged_owner_said.py` cannot see mid-turn chat messages, and the flag string inside `--text` also trips it (filed: LESSONS_INBOX).
- `jawa/world_neighbors`' `path` param is an output FILE path — it wrote 840KB to the game root while reading as a query (filed: LESSONS_INBOX).
- `serve_sheet.py`'s auto-open reported success and the owner never saw a browser — hand the tokened URL in chat too (filed: LESSONS_INBOX).
- `pkill -f` matched this window's own shell and killed it mid-chain, again (see: memory `pkill-f-matches-my-own-shell`; kill by PID).

## Closed since the last handoff (1)

- `SCALD_FLOOR_PASS_1` — 177aa325105d5e886dfa9c5eb853a5b987c10ce8

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
f28728633 Transient: swim-hood evidence shots (cited on JAWA_SWIM_HOOD_KEEP_1) + Scald walk frame
d701d36d8 Ledger: close SEA_BEASTS_TIER_RULING_1 at 099966fd1
099966fd1 SEA_BEASTS_TIER_RULING_1: retier 11 invented sea beasts from RSW_ to RM_
22a45a1b3 Ledger: DEEPFIRE_PIGMENT_MOD_1 art ruled, regen queued, item to FOUNDRY
c60f11c8b DEEPFIRE_PIGMENT_MOD_1: owner ruled the art sheet — keep crowncarpet_b + pigmentjar_b, cut all rainbow-loud renders; mat regen owed (sedate, organic, grosser)
d8ac5a8bb Ledger: block HOSTILE_MOBILE_PLANTS_1 on REACTION_MECHANISM_GENERALISE_1
4738fe049 Ledger: close FEVERWOOD_DIANOGA_PRISON_1 at 6318074f5
fd9480e3f DROID_ORACLE_VOICE_DESIGN_1: item + INDEX still said dormant/first-person after the owner's live/Narrator reversal
6318074f5 FEVERWOOD_DIANOGA_PRISON_1: Sekkulaath prison tank — teaches, produces, escapes
e4a2aee91 Ledger: note DROID_ORACLE_VOICE_DESIGN_1 doc rewritten to rulings
c211a1451 DROID_ORACLE_VOICE_DESIGN_1: rewrite to Narrator/third-person ruling; fold Q2/Q3/Q5/Q6/Q7; register rows 2-8 stay open
515083beb SHRUBLAND_TREE_GUARDIAN_1: rename kessrik -> bark-warden through the whole spec body (23 lines had the dead working label)
08033cec2 SHRUBLAND_TREE_GUARDIAN_1: build handoff was still naming SWBestiary and the kessrik after the ruling
99c228baf Ledger: SHRUBLAND_TREE_GUARDIAN_1 tier pick recorded
0e2cace11 SHRUBLAND_TREE_GUARDIAN_1: fold card ruling — species is RM_Barkwarden (Q11a: invented name, RM_ tier), label bark-warden
c3b9549cc DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 14: DivingInteraction/Source cluster CLEAN
87f3d683e FEATURE_DRAWCENTER_UNVERIFIED_1: audit all 71 world feature drawCenters, fix 52 wrong ones offline
db1040cbb Ledger: close SEA_DIVE_MAPS_BUILD_1 at 44a44438c
44a44438c SEA_DIVE_MAPS_BUILD_1: ship-only sea dive pocket maps, four terminal seas
22c357dcb Ledger: close FEVERWOOD_TENTACLE_BESTIARY_1 at 8ffcbfb88
... 55 more: git log --oneline e21e7bdc8..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-26T05:57:19Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   health publisher's own churn — leave alone
 M Transient/codebase_health.json   health publisher's own churn — leave alone
 M Transient/codebase_health_artifact.html   health publisher's own churn — leave alone
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
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Brindeth_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Brommet_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Brommet_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Brommet_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Dorvel_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Dredgel_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Dredgel_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Dredgel_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Gulveth_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Gulveth_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Gulveth_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Korveth_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Mirrelin_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Pallick_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skarrid_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skarrid_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skarrid_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skellarn_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skellarn_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skellarn_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skelver_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Soffeth_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_SumpMouse_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_SumpMouse_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_SumpMouse_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelWarden_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelWarden_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelWarden_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Thrummel_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Thrummel_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Thrummel_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Tolleth_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/RM_Velloch_a.json   artpipe daemon's churn — never commit mid-flight
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
 D infrastructure/artpipe/pending/desertportb_horax_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/miasma_ollamane.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/registry.jsonl   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/throughput.jsonl   artpipe daemon's churn — never commit mid-flight
 M infrastructure/dashboards/hub/data/health.json   health publisher's own churn — leave alone
 M infrastructure/state/codebase_health_last.json   health publisher's own churn — leave alone
 M skills/rimworld-debug-testing/SKILL.md   not mine — a peer window's uncommitted skill edit; leave alone
 M skills/rimworld-sprite-facings/SKILL.md   not mine — a peer window's uncommitted skill edit; leave alone
 M src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll.srchash   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/CreatureBehaviors/Source/RM_CompParentalEnrage.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/CreatureBehaviors/Source/RM_CompProperties_VerminBreeder.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/CreatureBehaviors/Source/RM_CompVerminBreeder.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/CreatureBehaviors/Source/RM_MentalState_ParentalEnrage.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/CreatureBehaviors/Source/RM_ParentalEnrageExtension.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll.srchash   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/EnvironmentalHazards/Source/RM_CompLivingBoleMarker.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_LivingRegrowth.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimMandrake/Greentide/About/About.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
D  src/RimMandrake/TheSump/Defs/PawnKindDefs/RUT_Placeholder_SumpMouse.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
D  src/RimMandrake/TheSump/Defs/ThingDefs_Races/RUT_Placeholder_SumpMouseRace.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimUtinni/UtinniPatches/Assemblies/RimMandrake.Utinni.UtinniPatches.dll   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimUtinni/UtinniPatches/Assemblies/RimMandrake.Utinni.UtinniPatches.dll.srchash   not mine — FOUNDRY window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/EffecterDefs/RM_KrissekHalo.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/HediffDefs/RM_BlueDesertCharges.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_GreatboleCore.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RM_ColdWax.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RM_BlueDesertFlora.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RM_BlueDesertFauna.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
 D src/RimUtinni/UtinniPatches/Source/BlueDesertLife.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimUtinni/UtinniPatches/Source/RimMandrake.Utinni.UtinniPatches.csproj   not mine — FOUNDRY window's uncommitted edit; leave alone
 M src/RimUtinni/UtinniPatches/Source/UtinniPatchesSettings.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
?? .rimflow_selftest_bridgefile/   rimflow selftest residue — leave alone
?? deployed/config/ModsConfig.before-tier-firehawk.xml   FOUNDRY modset backups — leave alone
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   FOUNDRY modset backups — leave alone
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   FOUNDRY modset backups — leave alone
?? infrastructure/artpipe/active/deepfire_crowncarpet_d.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Brindeth_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Brindeth_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Dorvel_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Dorvel_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Korveth_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Korveth_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Mirrelin_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Mirrelin_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Pallick_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Pallick_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Sivvern_v2_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Sivvern_v2_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Sivvern_v2_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Sivvern_v2_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Skelver_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Skelver_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Soffeth_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Soffeth_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Tolleth_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Tolleth_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Velloch_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Velloch_a.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_south.manifest.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/artpipe/done/deepfire_crowncarpet_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_c.manifest.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/artpipe/done/miasma_ollamane.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/done/miasma_ollamane.manifest.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/artpipe/failed/RM_Brommet_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_v2_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_v2_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_south.manifest.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   not mine — a peer window's; leave alone
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   not mine — a peer window's; leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   not mine — a peer window's; leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   not mine — a peer window's; leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   not mine — a peer window's; leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   not mine — a peer window's; leave alone
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   not mine — a peer window's; leave alone
?? src/RimMandrake/CreatureBehaviors/Languages/   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimMandrake/Greentide/Defs/RecipeDefs/   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimMandrake/Greentide/Defs/ThingDefs/RM_GreatboleHarvest_Items.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_GreatboleGrub.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimMandrake/Utils/firehawk_flight_probe.py   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_GreatboleFruitfall.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_GreatboleDeadHusk.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_GreatboleTrunkSegment.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Languages/English/Keyed/RUT_GreatboleHarvest.xml   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Source/RUT_CompGreatboleHarvestLadder.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
?? src/RimUtinni/UtinniPatches/Source/RUT_IncidentWorker_GreatboleFruitfall.cs   not mine — FOUNDRY window's uncommitted edit; leave alone
```

