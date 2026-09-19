# FOUNDRY_REBOOT_HANDOFF_202609192150 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_20260906`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`jawa/gravship_launch` + `jawa/gravship_land` already exist as closed, proven bridge
tools (`GRAVSHIP_LAUNCH_TRAVEL_1`, 2026-08-27) and reach the REAL vanilla launch/travel/
arrival path — `WorldComponent_GravshipController.InitiateTakeoff` → `GravshipUtility.
GenerateGravship`, and (confirmed via RimSage source) `Gravship.TickInterval` fires
`ArriveExistingMap`/`ArriveNewMap` automatically once world-travel ticks complete, no
landing confirmation needed for an arrival hook to fire. Six `COLONY_VISIBILITY_BUILD_1`
passes over three weeks stood on "no debug shortcut exists for a player gravship
launch" — that premise was simply wrong, because every pass checked only the
DEBUG-ACTION TREE, never the bridge's own `jawa/` tool surface. Any future item needing
a real gravship flight (launch, travel, arrival, or a Harmony hook on any of those
methods) has a proven, ~10-minute route: `prove_gravship.py`'s minimal-ship recipe
(site scan → substructure → GravEngine/PilotConsole/ChemfuelTank/SmallThruster →
`DEV: Set fuel to max` on vanilla, non-VGE lists) + `jawa/gravship_launch` →
`step_game_ticks` → `jawa/gravship_land`. Don't re-search the debug-action tree for
this again.

## What the owner should see

The live mod list is currently the 9-mod `visibility` test tier (bridge + DLC +
`mandrake.rm.visibility`), not the 617-mod full campaign — left that way deliberately,
on his own instruction this session (asked; he chose "leave the test mod list in
place" over restoring/relaunching the full list). If he sits down expecting the
Ash'karr campaign, that's why it isn't there: `python3 src/RimMandrake/Utils/
modset_builder.py --restore` (game must be down) puts the full list back, no restart
performed yet. Nothing else this wave needs his ruling — both closes below were
self-contained live proofs with no ambiguous judgment call.

## What is half-done, and where it stops

Nothing of this seat's own is left in `doing`. Both items pulled this window
(`MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1`, `LIQUID_SINK_DRAINAGE_1`, and
`COLONY_VISIBILITY_BUILD_1`) were closed with commits, not left mid-flight.

## Traps learned

- A background fork shares the same OS process space and the same deployed game
  install as its parent — dispatching one that touches `src/RimMandrake/bridgetools/`
  or restarts RimWorld while the foreground session is doing the same thing is a real
  race, not a theoretical one; it broke the whole `jawa-bench` tool provider mid-pass
  this wave (filed: LESSONS_INBOX).
- Vanilla marks an abandoned gravship-launch tile permanently unlandable (a
  `GravshipLaunch` world object sits there forever) — a real round trip back to a tile
  the SAME ship departed cannot be flown; seed the memory data instead and let a real
  arrival at a DIFFERENT tile restore it (see: `COLONY_VISIBILITY_BUILD_1`).

Note, not a trap: `infrastructure/state/LESSONS_INBOX.md` currently holds BOTH this
seat's one new line (above, filed) and 5 uncommitted BENCH lines in the same
working-tree copy (BENCH's own, pre-existing when this seat started) — deliberately
NOT committed here to avoid attributing BENCH's lessons to a FOUNDRY commit message.
Whoever commits it next should credit both.

## Closed since the last handoff (1)

- `COLONY_VISIBILITY_BUILD_1` — 45b9b9602

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
b6c38801e dashboards: regenerate health tab data (Utinni control panel refresh)
ad0c054f0 Correctness outranks seat ownership — owner's ruling, 2026-09-19
68534f6ef rimflow: sync ledger (COLONY_VISIBILITY_BUILD_1 closed)
45b9b9602 COLONY_VISIBILITY_BUILD_1: live-prove the tile-memory round trip, close
2eca56cd8 JawaBenchColonyVisibilityTools: add a tile-memory seed tool for the arrival test
a305ded7d rimflow: sync ledger (COLONY_VISIBILITY_BUILD_1 collision note)
c1c340327 modset_builder: add a visibility tier (bridge+DLC+mandrake.rm.visibility)
281b711d7 PIT_TRAP_VISUAL_REDESIGN_1 superseded by PIT_SUPERDEEP_COLLAPSE_1
cd50c47d3 JawaBenchColonyVisibilityTools: read GameComponent_ColonyVisibility live
637fbb850 RUT_UMBRA_ROADS_RULING_1: the ban stands, and now it is ruled
9d55fb5ef Ruling sitting 2026-09-19: 9 items ruled, oldest first
ce76906fb Fix 2 citations inside FOUNDRY's live item files
ab65b97b7 Repoint doctrine and 97 citations at items/closed/ and handoffs/
91d333b83 Terminal item prose moves to items/closed/ (578 files)
75bf9d7f7 Handoff move, second half: drop the old items/ paths
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-19T20:16:26Z

Uncommitted (replace each WHOSE-marker with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   auto-regenerated by the health-rebuild trigger on any rimflow close, not mine
MM Transient/codebase_health.json   auto-regenerated by the health-rebuild trigger, not mine
 M Transient/codebase_health_artifact.html   auto-regenerated by the health-rebuild trigger, not mine
 M deployed/config/ModsConfig.before-tier-pits.xml   mine -- pits-tier swap snapshot for LIQUID_SINK_DRAINAGE_1\'s live proof
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/nuitae_a_v1.json -> infrastructure/artpipe/done/nuitae_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/nuitae_b_v1.json -> infrastructure/artpipe/done/nuitae_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/yumbulbs_a_v1.json -> infrastructure/artpipe/done/yumbulbs_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/yumbulbs_b_v1.json -> infrastructure/artpipe/done/yumbulbs_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_4_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/rut_firehawk_flying_5_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_drinker_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_drinker_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_drinker_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/mycelium_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/mycelium_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/mycelium_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaricusdomecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agariluxprime_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agelesscap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_arbuscularmycorrhiza_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_arpeau_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_blastpodshroom_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_bleedingtooth_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_brightbell_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_bryolux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_crimsoncap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_dewshrooms_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_dribblingcap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_dulcisplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_euphoriccrown_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_falsefruit_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_flakespirefungus_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fruitingbodies_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_furnacecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_giantagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_glowingagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_glowstool_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_greylady_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_lilacbeacon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mortalmorelplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_nogtyl_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_nuitae_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_palemoss_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_paletree_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_pusmelon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_recurvedstropharia_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_regenerantveil_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_rustpuff_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_falsefruit_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_furnacecap_plant_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_gene_furnaceblood_icon_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_grownfurnace_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveingredient_agelesscap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveingredient_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveprep_toxicinjection_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_livingfurnacecap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_palemoss_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_paletree_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_mycoid_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_nightwake_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_quickflesh_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_sheenblood_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_tea_agereversal_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_tea_bioregeneration_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_tea_pleasure_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
MM infrastructure/artpipe/registry.jsonl   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
MM infrastructure/artpipe/throughput.jsonl   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 M infrastructure/state/LESSONS_INBOX.md   BENCH\'s (5 new lessons, all signed BENCH), not mine
 M infrastructure/state/codebase_health_last.json   auto-regenerated by the health-rebuild trigger, not mine
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   mine, disposable scratch script from this session
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   not mine, unrelated stray tmp file
?? deployed/config/ModsConfig.before-tier-bridge.xml   not mine, pre-existing from other tier tests this session
?? deployed/config/ModsConfig.before-tier-oracle.xml   not mine, pre-existing from other tier tests this session
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   not mine, pre-existing from other tier tests this session
?? deployed/config/ModsConfig.before-tier-visibility.xml   mine -- visibility-tier swap snapshot for COLONY_VISIBILITY_BUILD_1\'s live proof
?? deployed/config/ModsConfig.before-tier-warlab.xml   not mine, pre-existing from other tier tests this session
?? infrastructure/artpipe/done/deeps_drinker_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/deeps_drinker_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaricusdomecap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agarilux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agariluxprime_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agariluxprime_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agaripawn_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agelesscap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_agelesscap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_arbuscularmycorrhiza_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_arpeau_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_arpeau_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_blastpodshroom_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_bleedingtooth_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_brightbell_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_brightbell_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_bryolux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_bryolux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_crimsoncap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_crimsoncap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dewshrooms_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dewshrooms_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dribblingcap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dribblingcap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dulcisplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_dulcisplant_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_euphoriccrown_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_falsefruit_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_falsefruit_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_flakespirefungus_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fruitingbodies_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_fungalweevil_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_furnacecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_furnacecap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_giantagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_giantagarilux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_glowingagarilux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_glowstool_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_glowstool_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_greylady_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_greylady_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_lilacbeacon_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mortalmorelplant_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_mycoidcolossus_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_nogtyl_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_nogtyl_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_nuitae_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_nuitae_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_palemoss_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_palemoss_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_paletree_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_paletree_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_pusmelon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_pusmelon_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_regenerantveil_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_regenerantveil_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_rustpuff_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/done/rot_rustpuff_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_scratches_p1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_scratches_p2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_scratches_p3.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_tally_p1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_tally_p2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_tally_p3.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_warn_p1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_warn_p2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_fulgurite_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_3_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_4_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_4_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_4_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_5_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_5_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/rut_firehawk_flying_5_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow concurrency scratch dir, not mine (pre-existing this session)
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing since 2026-09-11, not mine
?? infrastructure/state/handoffs/BENCH_REBOOT_HANDOFF_202609192149.md   BENCH\'s own handoff, not mine
```

