# BENCH_REBOOT_HANDOFF_202609260109 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609251827`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**A REFUSED `git merge` hard-resets the shared tree, and the shared tree now has one sanctioned sync path.** The 07:54 loss of 215 files' edits was git's internal restore_state() (stash, reset --hard, re-apply) failing its re-apply on a peer's index.lock. `block_shared_tree_merge.py` now refuses merges, bare pulls, --autostash and whole-tree discards in the main tree; publish and catch up ONLY with `python3 src/RimMandrake/Utils/shared_sync.py` (git replay onto origin, push, reset --keep). Worktree subagents land their own work (rebase + `push origin HEAD:main` from inside the worktree). Both hooks, and `block_dll_source_mismatch.py` (DLLs carry a .srchash sidecar), only fire in windows started after 2026-09-25 ~13:00 — the FOUNDRY window that was live then predates them. (see: CLAUDE.md Git, CHARTER, git-efficiency skill)

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Walk SCALD_REVIEW.rws** — he asked to walk it at wrap; the game was relaunched at 17:54 for exactly that (cold load ~17 min). Load it with `rimworld/load_game {saveName:"SCALD_REVIEW"}` under **python.exe** (WSL cannot reach the bridge). Open points: cast reads tiny, wreck shadows are big dark boxes, margin looks identical to shallows.
- **Deepfire art sheet** `D:\Luke\dev\Rimworld\Transient\deepfire_pigment_review.html` — 4 new jobs (deepfire_pigmentjar_a/b, deepfire_crowncarpet_a/b) had left pending/ at wrap; refresh the sheet when they're in done/, then hand it to him. The 3 rainbow jars are flagged contested.
- **SeaShores + Bacta were silently dropped** from his live list by a 17:18 FOUNDRY minimal-list restore (stale ModsConfig.FULL.LATEST.xml); both restored in the live list and in FULL.LATEST (42c8b8fdc) — 628 active.
- **Design assumes every DLC** is now a standing rule (his words, CLAUDE.md).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `SEA_DIVE_MAPS_BUILD_1` -- spec fully ruled (Scald floor sitting: Vu'uul/Ullium/Askirath/Feen, chimney fields, nodules, Rakatan wreck, droids, gear matrix; design/RimMandrake/sea_dive_maps_spec.md + exposure_gear_matrix_spec.md); NEXT: hand steps S1-S9 to FOUNDRY (re-file for FOUNDRY; it's build work now).
- `DEEPFIRE_PIGMENT_MOD_1` -- spec fully ruled except Q5 (GlowTank liquids, default salt/boiling) (design/RimMandrake/deepfire_luminous_pigment_spec.md); NEXT: re-file for FOUNDRY starting with the proxy-glower quicktest, after the owner rules the art sheet.
- `STATUE_ART_EXPANSION_1` -- O1-O4 ruled by card (picker button, Ohm+Rekko grands in wave one, any colony, Sh'kaar must burn first) but NOT folded into statue_mods_spec.md; NEXT: fold those four into §1.3/§6 of the spec, then queue wave-one art.
- `SEA_SHORE_TILE_MUTATOR_1` -- SeaShores built, healer Coast-skip fixed (3955400fd), enabled + cold-loaded clean; NEXT: load any save with a sea-coast tile and confirm the coast shows that sea's water, then close.
- `SCALD_STEAM_WEATHER_DESIGN_1` -- step 1 (native immunity) built 212eafe4f + deployed; NEXT: quicktest Noohm/Shulla in boiling water beside a colonist control, then build the exposure clock (step 2) on the gear matrix.
- `JAWA_SWIM_HOOD_KEEP_1` -- all parts deployed (JawaRules found already in sync at restart); NEXT: with the owner, look at a swimming and a sleeping Jawa, then close.
- `SCALD_FLOOR_PASS_1` / `SCALD_ART_UPGRADE_WAVE_1` -- 42 scald2_* jobs rendering; NEXT: contact-sheet them for the owner, then wire per the handoff-202609251827 pointer.
- `MINERALS_WHERE_THEY_BELONG_1` -- filed, design for later (census at design/RimMandrake/minerals_census_2026-09-25.md; absorbs the plasteel->Durasteel rename); NEXT: none until he schedules it.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A refused `git merge` is not harmless: restore_state() hard-resets and, if the re-apply hits index.lock, every tracked edit is gone with no reflog entry (filed: git-efficiency skill).
- The shared tree is never clean, so `pull --rebase` refuses and ff fails once diverged; use shared_sync.py (see: CLAUDE.md Git).
- modlist_swap restores from ModsConfig.FULL.LATEST.xml, which goes stale when anyone hand-edits the live list (filed: LESSONS_INBOX).
- `--owner-said` routes events to the OWNER.jsonl shard, not your seat's — commit that shard too (filed: LESSONS_INBOX).
- Mid-turn owner messages are refused by the owner-said guard; record under the seat with the words quoted in --text (filed: using-rimflow skill).
- Worktree pushes can fail in Windows Git Credential Manager; use the gh helper (filed: git-efficiency skill).
- Bridge is Windows-loopback only: drive it with python.exe from the repo, never WSL python (see: rimbridge skill §1).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (2) — the next seat's queue

- `DEEPFIRE_PIGMENT_MOD_1` — Deepfire: new RM mod LuminousPigment — expensive glowing pigment (colour from the dye it's mixed with, pigment supplies a dim glow); +1 quality on art
- `MINERALS_WHERE_THEY_BELONG_1` — Design (later): minerals where they belong — per-biome allocation of every mineral, gem and mineable material; specific forms (nodules, crystal cluste

## Commits

```
6f69bbc12 Ledger: bridge release (BENCH handoff; SCALD_REVIEW walk moves to next session)
141e9e40c FOUNDRY reboot handoff 2026-09-26 00:52; full-belt wave closed 5 items
fe210116e Ledger: game -> LOADING recorded (owner broadcast, cross-session relay)
42c8b8fdc FULL.LATEST modlist: restore SeaShores and Bacta the 17:18 restore dropped
21b81ce8e Gear matrix: §6 open questions replaced by the owner's rulings
974e797a4 Ledger: gear matrix Q5 — KotOR suits dive
8db0b4807 FORSAKENCRAGS_RM_MOD_BUILD_1: add real load-clean proof (retry)
ac97f20f2 Closes: LEANINGSCRUB_RM_MOD_BUILD_1
dbf2a1c06 CLAUDE.md: design assumes every DLC is present (owner ruling)
ca856414c modset_builder.py: add leaningscrub test tier
8398dde1f Closes: FORSAKENCRAGS_RM_MOD_BUILD_1
6b389ddb9 LEANINGSCRUB_RM_MOD_BUILD_1: build RM_LeaningScrub as its own RimMandrake mod
948b482c8 ledger sync: FORSAKENCRAGS_RM_MOD_BUILD_1 claim/start/note
2a71b271c FORSAKENCRAGS_RM_MOD_BUILD_1: build RM_ForsakenCrags as its own RimMandrake mod
72976da01 Dive spec: fold the 16:31+ rulings; new exposure gear matrix spec
2f3d4749c Paint list: RUT_AridShrubland frozen, RM_LeaningScrub added
9d85b4800 UtinniPatches: loadAfter mandrake.rm.leaningscrub
baee73bc6 Ledger: Scald floor §8.8 rulings — names, heat, droids, wreck, visuals, pearl, gear matrix
7581f2ca7 Close STILLSAND_RM_MOD_BUILD_1 and THEROT_RM_MOD_BUILD_1: false "proposed" state
3db720e51 biome_paint_list.md: RUT_ExtremeDesert row was stale, said bare PAINT
... 59 more: git log --oneline b066a1576..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : LOADING
- Bridge: FREE    since 2026-09-26T01:08:29Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   auto-regenerated health artifacts (take either side)
 M Transient/codebase_health.json   auto-regenerated health artifacts (take either side)
 M Transient/codebase_health_artifact.html   auto-regenerated health artifacts (take either side)
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_crowncarpet_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_crowncarpet_b.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_pigmentjar_a.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_pigmentjar_b.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/registry.jsonl   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/throughput.jsonl   artpipe daemon's churn — never commit mid-flight
 M infrastructure/dashboards/hub/data/health.json   auto-regenerated health artifacts (take either side)
 M infrastructure/state/codebase_health_last.json   auto-regenerated health artifacts (take either side)
 M infrastructure/state/queue/BENCH.md   rimflow render projection — regenerate, don't hand-commit
 M infrastructure/state/queue/FOUNDRY.md   rimflow render projection — regenerate, don't hand-commit
 M skills/rimworld-debug-testing/SKILL.md   not mine — a peer's uncommitted skill edit; leave alone
 M skills/rimworld-sprite-facings/SKILL.md   not mine — a peer's uncommitted skill edit; leave alone
?? deployed/config/ModsConfig.before-tier-firehawk.xml   FOUNDRY modset_builder tier backups — leave alone
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   FOUNDRY modset_builder tier backups — leave alone
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   FOUNDRY modset_builder tier backups — leave alone
?? infrastructure/artpipe/active/scald2_wreckframe_c.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/artpipe/pending/crags_kessik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_shekkur_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_thrizzik_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ulkhorr_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_vrakk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zekkra_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_zhurrakor_south.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/artpipe/pending/scald2_wreckhull_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald2_wreckhull_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald2_wreckhull_c.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald2_wrecktank_a.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald2_wrecktank_b.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald2_wrecktank_c.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   mine (BENCH) — safety backup before restoring SeaShores+Bacta; keep
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   FOUNDRY/owner tier backups — leave alone
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   FOUNDRY/owner tier backups — leave alone
?? src/RimMandrake/Utils/firehawk_flight_probe.py   FOUNDRY's (FIREHAWK_FLIGHT_BEHAVIOR_1) — not mine
```

