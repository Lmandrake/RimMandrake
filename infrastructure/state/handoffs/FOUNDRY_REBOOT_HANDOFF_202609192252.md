# FOUNDRY_REBOOT_HANDOFF_202609192252 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609192150`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A `--owner-said` quote is now provable, not just shape-checked: `.claude/hooks/block_forged_owner_said.py`
refuses any `--owner-said "..."` whose text does not appear in a `promptSource=="typed"`
line of THIS session's own transcript (the harness's `transcript_path`, JSONL). A subagent's
own Bash calls share the exact same transcript file and `CLAUDE_CODE_SESSION_ID` as its
parent window — MEASURED this wave by having a subagent's `git add -A` get refused by
`block_blanket_git_stage.py` with that hook's own message, and by diffing env vars. So any
future provenance-style guard should read the shared transcript rather than trying to build
an identity check between a seat and its own subagent — there is no such signal (env vars,
session id, role file are all identical).

Also: several "recent" queue items this wave were not actually new work — they were OLD
items (some from 2026-09-03) that a peer BENCH window `reassign`ed to FOUNDRY minutes before
I started, because they had a real owner ruling attached but nobody had ever pulled them.
`reassign` timestamps, not `file` timestamps, told the true story here.

## What the owner should see

- `CANONICAL_SAVE_CUT_RESIDUE_1` and `CANONICAL_SAVE_SCENARIO_MISMATCH_1` are both still
  `needs owner`/deliberately not worked this wave — both touch the SAME single shipped save
  (`CANONICAL_ASHKARR_START_2026-09-12.rws`), and they interact: the scenario-mismatch item
  asks him to choose between redoing the flight from a fresh `Scenario_Utinni` start or
  hand-building founders into the existing save, and a full residue scrub (~4,828 dead
  references across 16 missing mods, ~50x the scale of the one dead-def scrub already done
  for Caverns) would be wasted work if he picks "redo the flight." Recommend he rule on the
  scenario question FIRST; the residue item names the safest next probe (a plain bridge
  re-save under the override flag) once he does.
- `TWILIGHT_DEEP_WATER_LAYER_1` also sits `needs owner` — genuine biome/mechanism design
  fork (three candidate shapes, none built), not guessed at.
- Two C# companion fixes (`DESIGNATE_BATCH_OVER_DESIGNATES_1`,
  `BRIDGETOOLS_TILE_LAYER_DROPPED_1`) are built and staged in the same DLL but NOT deployed —
  `build.py --apply` refuses while RimWorld holds the file memory-mapped. Needs the game down,
  then a restart, to actually take effect. Nothing urgent forces that restart; batch it.
- `BARBSLINGER_SCORPION_REDESIGN_1`: found an existing `barbslinger_scorpion_v1_{east,north,
  south}` render set in `infrastructure/artpipe/_artsrc/` dated HOURS before his correction
  landed, with no matching job in the pipeline (never went through the normal queue) and no
  visible tails on the south facing — read as the "earlier scorpion-concept renders were
  HATED" batch his own note refers to. Left untouched rather than guessed at; filed 3 fresh
  jobs from his exact words instead. Worth his eye if he wants to confirm that read.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `BARBSLINGER_SCORPION_REDESIGN_1` — needs=harvest, 3 fresh art jobs filed (`barbslinger_redesign_v1_{south,east,north}`), mechanics researched but not built; NEXT: once `infrastructure/artpipe/done/barbslinger_redesign_v1_*` exists, show the owner, then build the `CompProperties_TurretGun` ranged attack per the item file's turret-gun-shape decision point.
- `BRIDGETOOLS_TILE_LAYER_DROPPED_1` — needs=deploy, fix built and passing 62/62 selftests; NEXT: `python.exe src/RimMandrake/bridgetools/build.py --gm --apply` with the game DOWN, then restart, then `close --sha f761f0966`.
- `DEEPS_FAUNA_VERDICTS_1` — needs=harvest, def/deploy work already landed at `a00f52f10` (a prior wave); NEXT: once the remaining 7/8 creatures land in `infrastructure/artpipe/done/`, spot-check in game and `close`.
- `DESIGNATE_BATCH_OVER_DESIGNATES_1` — needs=deploy, fix built and passing 62/62 selftests; NEXT: same deploy as `BRIDGETOOLS_TILE_LAYER_DROPPED_1` (same DLL, same restart) — `python.exe src/RimMandrake/bridgetools/build.py --gm --apply`, then `close --sha ce6479dc7`.
- `GRAFFITI_VANDAL_ART_REGEN_1` — needs=harvest, 6 fresh single-motif art jobs filed; NEXT: once `infrastructure/artpipe/done/graffiti_vandal_regen_v1_*` exists and is reviewed, copy the kept PNGs over `vandal_0.png`..`vandal_5.png` and deploy.
- `PYRELANDS_WEATHER_SCAR_ART_1` — needs=harvest, filth-legibility + Cinderfall-overlay def fixes already landed+deployed at `a98c30f81`; NEXT: once the 4 `pyrelands_ash_*` terrain jobs land, review and wire into `AshLadder.xml`'s `texturePath`, then `close`.

## Traps learned

- `.claude/settings.json` PreToolUse hook edits do not take effect mid-session for either the seat or a subagent — only a hook already live at session start fires (filed: LESSONS_INBOX).
- `build.py`'s default (no `--gm`) plan can show ~40 false "would remove tools" lines against a live `--gm`-built DLL — the flag gates far more than the two tools its own doc names (filed: LESSONS_INBOX).

## Closed since the last handoff (2)

- `REOPEN_DESTROYS_CLEANCOUNT_STREAK_1` — 340b06961
- `OWNER_SAID_PROVENANCE_GUARD_1` — fce1c0f2a

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
87188b29c rimflow: sync ledger (BRIDGETOOLS_TILE_LAYER_DROPPED_1 fix landed, deploy owed)
f761f0966 bridgetools: thread the planet layer id through tile resolution (BRIDGETOOLS_TILE_LAYER_DROPPED_1)
87f8296d5 rimflow: sync ledger (DESIGNATE_BATCH_OVER_DESIGNATES_1 fix landed, deploy owed)
ce6479dc7 designate_batch: filter Things by the DesignationDef's own target rules (DESIGNATE_BATCH_OVER_DESIGNATES_1)
0ba047881 Retract the handoff's road-premise doubt — the Umbra ruling was right
4cec820ac LESSONS_INBOX: three traps from the Rot size wave
3688a4017 rimflow: sync ledger (Rot size rulings applied and deployed)
dab0bba2b ROT_SIZE_REJUDGE_APPLY_1: apply his 11 re-judged Rot sizes
51023fecc rimflow: sync ledger (GRAFFITI_VANDAL_ART_REGEN_1 art filed, needs=harvest)
0005d9857 Graffiti: regenerate all 6 Vandal marks as single motifs, zero lettering (GRAFFITI_VANDAL_ART_REGEN_1)
ce6101e4e Remove the AB size recheck sheet — he already re-judged those rows
eaee7202c rimflow: sync ledger (BARBSLINGER_SCORPION_REDESIGN_1 art filed, needs=harvest)
593395b09 rimflow: sync ledger (landmark sheet built; drift finding on the biome switch)
377e74ab6 Barbslinger redesign: fresh art jobs filed, ranged-attack mechanism researched (BARBSLINGER_SCORPION_REDESIGN_1)
6930733d6 BIOME_LANDMARK_REFINEMENT_1: the landmark density sheet, 26 rows
bb74b9d62 rimflow: sync ledger (PYRELANDS_WEATHER_SCAR_ART_1 def work landed, needs=harvest)
a98c30f81 Pyrelands: legible ash filth, a real storm overlay for Cinderfall (PYRELANDS_WEATHER_SCAR_ART_1)
525737260 rimflow: sync ledger (AB size recheck sheet built; landmark recon)
c674c1e55 AB size recheck sheet: the 11 mushroom rows, re-served at true scale
bccc9fab5 rimflow: sync ledger (CANONICAL_SAVE_CUT_RESIDUE_1 sequencing note)
... 8 more: git log --oneline 2486cafe6..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-19T20:16:26Z

Uncommitted (replace each not mine -- not touched this session with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   auto-regenerated health/dashboard artifact, re-touched by every window's rimflow activity -- not specifically mine
MM Transient/codebase_health.json   auto-regenerated health/dashboard artifact, re-touched by every window's rimflow activity -- not specifically mine
 M Transient/codebase_health_artifact.html   auto-regenerated health/dashboard artifact, re-touched by every window's rimflow activity -- not specifically mine
 M deployed/config/ModsConfig.before-tier-pits.xml   modlist_swap.py tier-test backup -- not run this session, not mine
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
 M infrastructure/dashboards/hub/data/health.json   auto-regenerated health/dashboard artifact, re-touched by every window's rimflow activity -- not specifically mine
 M infrastructure/state/codebase_health_last.json   auto-regenerated health/dashboard artifact, re-touched by every window's rimflow activity -- not specifically mine
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\claude-1000\\-mnt-d-Luke-dev-Rimworld\\84f9b274-abd5-4c73-81fd-7f936a8b3cc9\\scratchpad\\check_tile.py"   untracked scratch file from another window/process, not mine
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   untracked scratch file from another window/process, not mine
?? deployed/config/ModsConfig.before-tier-bridge.xml   modlist_swap.py tier-test backup -- not run this session, not mine
?? deployed/config/ModsConfig.before-tier-oracle.xml   modlist_swap.py tier-test backup -- not run this session, not mine
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   modlist_swap.py tier-test backup -- not run this session, not mine
?? deployed/config/ModsConfig.before-tier-visibility.xml   modlist_swap.py tier-test backup -- not run this session, not mine
?? deployed/config/ModsConfig.before-tier-warlab.xml   modlist_swap.py tier-test backup -- not run this session, not mine
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
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow concurrency scratch dir from a different session id -- not mine
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing since 2026-09-11, not mine
```

