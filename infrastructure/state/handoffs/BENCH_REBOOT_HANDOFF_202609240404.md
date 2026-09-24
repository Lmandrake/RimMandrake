# BENCH_REBOOT_HANDOFF_202609240404 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609240332`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 **The Webwork's owner species is now OURS: the Ollathrix (owner card, 2026-09-23), one race one kind, mapped to the Wyyyschokk only under Utinni.** That inverts the 2026-09-11 kit ruling that put the Shokk mechanisms in an RSW mod — bound hediff, spit, sun-scald and the emergent-spawn comp are mechanism-not-IP and belong in `mandrake.rm.webwork`; `mandrake.rsw.shokk` shrinks to a skin patch. The full record is `design/Jawa/worldbuilding/biomes/webwork_owner_and_nest_2026-09-23.md`; ⛔ do not build from `WEBWORK_RM_MOD_BUILD_1`'s step plan as written (its "wildAnimals ships empty" is superseded — the doc's §5 says what changed).


## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Eight rulings owed, one card each**, listed verbatim in `design/Jawa/worldbuilding/biomes/webwork_owner_and_nest_2026-09-23.md` §6 (Shokk mod inversion; Wildsteam and eggs; nest frequency; egg respawn; egg tradeability; skin-patch home RSW vs RUT; the three proposed fauna cuts; tooke-trap disposition).
- The silk's free-tier word-form was chosen by the design pass, not by him: **thrixweave** (doc §2). He picked only "named after the spider" by card.
- Nothing deployed, nothing live-touched this window. Bridge untouched.


## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `WEBWORK_DESIGN_SITTING_1` -- owner-and-nest doc COMPLETE; flora and fauna roster docs are 26-line SKELETONS (the Fable pass was stopped for this handoff); NEXT: re-spawn the Fable roster pass per the item's NEXT list, then card §6.
- `WEBWORK_RM_MOD_BUILD_1` -- `proposed`, untouched except a ruling note; NEXT: nothing until the sitting closes — its step plan is partly superseded (see above).
- `BIOME_MOD_SPLIT_EXECUTION_1` -- inherited in `doing`, untouched this window; NEXT: take the child tickets one biome per sitting with him (the Webwork's is now `WEBWORK_DESIGN_SITTING_1`), never a sweep.
- `SEA_FLOOR_AND_CATCH_PASS_1` -- inherited, untouched this window, nothing live-proven; NEXT: on his word enable `mandrake.rm.seashores`, deploy UtinniPatches knowingly, cold load, read the healer log line beside the Scald.


## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `handoff.py --check` says "ALREADY HANDED OFF" when nothing has been COMMITTED since the last handoff, even with real uncommitted work in the tree — commit first, then it gates on unpushed instead (see: this handoff's own commits).
- 🔴 The per-seat ledger sharding (`events/<SEAT>.jsonl`) is UNCOMMITTED peer code in `src/RimMandrake/rimflow/{model,cli}.py` at wrap — this window's shard is committed, the reader that merges it is not; until the peer commits, origin's rimflow cannot see this sitting's rulings or `WEBWORK_DESIGN_SITTING_1` (see: `git status src/RimMandrake/rimflow`).
- The ledger now shards per seat: a note lands in `infrastructure/state/ledger/events/<SEAT>.jsonl`, not `events.jsonl`, and the shard file is a NEW untracked path the first time — commit it by explicit path or the whole sitting's rulings stay local (see: `src/RimMandrake/rimflow/model.py` header).


## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (1) — the next seat's queue

- `WEBWORK_DESIGN_SITTING_1` — finish the roster docs, then card §6

Nothing filed in this window.

## Commits

```
1e95238fe Webwork sitting 2026-09-23: Ollathrix owner-and-nest record; flora/fauna rosters are SKELETONS
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T01:17:37Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M .claude/hooks/queue_lint.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M .claude/hooks/selftest_queue_lint.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M Transient/codebase_health.html   health publisher, auto-rewritten
 M Transient/codebase_health.json   health publisher, auto-rewritten
 M Transient/codebase_health_artifact.html   health publisher, auto-rewritten
 D infrastructure/artpipe/pending/RSW_Cindermite_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Cindermite_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Cindermite_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Dunegrass.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Dunestalker_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Dunestalker_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Dunestalker_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Ferroclaw_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Ferroclaw_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Ferroclaw_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Sandhorn_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Sandhorn_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Sandhorn_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Sandmaw_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Sandmaw_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Sandmaw_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Sandstrider_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Sandstrider_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Sandstrider_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Spineroller_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Spineroller_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Spineroller_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Stareling_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Stareling_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Stareling_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_SweetbarkTree.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Tuskcoil_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Tuskcoil_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Tuskcoil_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_VellaraBloom.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Voltmaw_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Voltmaw_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/RSW_Voltmaw_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/bluedesert_dorrak_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/bluedesert_dorrak_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/bluedesert_dorrak_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/bluedesert_krissek_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/bluedesert_krissek_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/bluedesert_krissek_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/bluedesert_vekkit_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/bluedesert_vekkit_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/bluedesert_vekkit_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/desertportb_convor_south.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/desertportb_falumpaset_east.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/desertportb_falumpaset_north.json   artpipe daemon (pending→done churn)
 D infrastructure/artpipe/pending/rm_greatbole_v1.json   artpipe daemon (pending→done churn)
 M infrastructure/artpipe/registry.jsonl   artpipe daemon (pending→done churn)
 M infrastructure/artpipe/throughput.jsonl   artpipe daemon (pending→done churn)
 M infrastructure/dashboards/hub/data/health.json   health publisher, auto-rewritten
 M infrastructure/state/codebase_health_last.json   health publisher, auto-rewritten
 M src/RimMandrake/Utils/broadcast.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/Utils/codebase_health.py   health publisher, auto-rewritten
 M src/RimMandrake/Utils/handoff.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/Utils/modcheck/doctor.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/Utils/project_maturity_dashboard.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/Utils/repair_torn_ledger.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/rimflow/cli.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/rimflow/live_proof_lint.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/rimflow/model.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/rimflow/render.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/rimflow/selftest_cli.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/rimflow/selftest_concurrency.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/rimflow/selftest_items_glob_live.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
 M src/RimMandrake/rimflow/selftest_model.py   a PEER window, mid-edit (rimflow per-seat sharding + tooling) — NOT this window
?? infrastructure/artpipe/daemon_run_20260923_owner_100pct.log   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Cindermite_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Cindermite_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Cindermite_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Cindermite_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Cindermite_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Cindermite_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Dunegrass.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Dunegrass.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Dunestalker_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Dunestalker_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Dunestalker_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Dunestalker_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Dunestalker_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Dunestalker_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Ferroclaw_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Ferroclaw_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Ferroclaw_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Ferroclaw_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Ferroclaw_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Ferroclaw_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandhorn_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandhorn_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandhorn_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandhorn_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandhorn_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandhorn_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandmaw_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandmaw_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandmaw_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandmaw_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandmaw_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandmaw_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandstrider_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandstrider_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandstrider_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandstrider_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandstrider_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Sandstrider_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Spineroller_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Spineroller_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Spineroller_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Spineroller_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Spineroller_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Spineroller_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Stareling_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Stareling_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Stareling_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Stareling_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Stareling_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Stareling_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_SweetbarkTree.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_SweetbarkTree.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Tuskcoil_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Tuskcoil_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Tuskcoil_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Tuskcoil_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Tuskcoil_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Tuskcoil_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_VellaraBloom.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_VellaraBloom.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Voltmaw_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Voltmaw_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Voltmaw_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Voltmaw_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Voltmaw_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/RSW_Voltmaw_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_boma_v1_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_boma_v1_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_boma_v1_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_boma_v1_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_boma_v1_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_boma_v1_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_dewback_v1_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_dewback_v1_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_dewback_v1_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_dewback_v1_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_insectomorph_v1_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_insectomorph_v1_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_insectomorph_v1_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_insectomorph_v1_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_shiro_v1_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_shiro_v1_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_shiro_v1_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_shiro_v1_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_shiro_v1_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_shiro_v1_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_vornskyr_v1_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_vornskyr_v1_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_vornskyr_v1_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_vornskyr_v1_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_vornskyr_v1_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_vornskyr_v1_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_whisperbird_v1_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_whisperbird_v1_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_whisperbird_v1_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_whisperbird_v1_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_whisperbird_v1_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_whisperbird_v1_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_zakkeg_v1_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_zakkeg_v1_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_zakkeg_v1_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_zakkeg_v1_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_zakkeg_v1_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/canon_zakkeg_v1_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_convor_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_convor_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_falumpaset_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_falumpaset_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_falumpaset_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_falumpaset_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_falumpaset_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_falumpaset_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralgrazer_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralgrazer_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralgrazer_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralgrazer_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralgrazer_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralnerf_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralnerf_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralnerf_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_graniteslug_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_graniteslug_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_graniteslug_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_grank_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_grank_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_grank_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_grank_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_grank_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_grank_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_horax_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_horax_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_horax_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_horax_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_horax_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_horax_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_jakobeast_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_jakobeast_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_jakobeast_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kraytdragon_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kraytdragon_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kraytdragon_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kraytdragon_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_krykna_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_krykna_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_krykna_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetle_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetle_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetle_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_nerf_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_nerf_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_nerf_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_pikobis_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_pikobis_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_pikobis_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_plant_bloddle.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/rm_greatbole_v1.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/done/rm_greatbole_v1.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/RSW_Voltmaw_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/RSW_Voltmaw_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_dorrak_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_dorrak_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_dorrak_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_dorrak_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_dorrak_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_dorrak_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_krissek_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_krissek_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_krissek_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_krissek_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_krissek_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_krissek_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_vekkit_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_vekkit_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_vekkit_north.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_vekkit_north.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_vekkit_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/bluedesert_vekkit_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/canon_dewback_v1_south.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/canon_dewback_v1_south.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/canon_insectomorph_v1_east.json   artpipe daemon (pending→done churn)
?? infrastructure/artpipe/failed/canon_insectomorph_v1_east.manifest.json   artpipe daemon (pending→done churn)
?? infrastructure/state/.rimflow_conc_97j8px_9/   a peer window or a tool backup — NOT this window
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   a peer window or a tool backup — NOT this window
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   a peer window or a tool backup — NOT this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   a peer window or a tool backup — NOT this window
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   a peer window or a tool backup — NOT this window
```

