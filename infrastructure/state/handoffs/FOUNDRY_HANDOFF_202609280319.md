# FOUNDRY_HANDOFF_202609280319 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202609271458`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

A "surprise reboot, check your work" wake surfaced a genuinely live incident that
had nothing to do with the reboot: `LANTERNDEEPS_TIER_COLLISION_1`'s own record
said the hazardous deploy was "reverted the same minute", but the live
`Mods\LanternDeeps` folder had actually carried the full RM successor (79 files)
since 2026-09-26, while `ModsConfig.xml` still referenced the old packageId —
undetected for two days because nothing routinely checks deployed-mod-identity
against ModsConfig's own references. It only surfaced because a canonical-save
`load_game_ready` compatibility check refused to load. **A "done/reverted" claim
in an item is only as good as the last time someone re-measured it against the
live game, not the repo** — this is the same family as the project's own
"queue items decay" doctrine, just applied to deployed mod state instead of
ledger items. See LESSONS_INBOX for the mechanism.

## What the owner should see

- **Two canonical-save fixes are staged but NOT resaved, deliberately.** VQE
  Cryptoforge is removed from ModsConfig (CRYPTOFORGE_HARVEST_RETIRE_1 step 4)
  and the LanternDeeps packageId mismatch is corrected (LANTERNDEEPS_TIER_
  COLLISION_1 step 4). Both items gate the final canonical resave on the
  owner's word — waiting for it before touching `CANONICAL_ASHKARR_START_
  2026-09-12.rws` (already backed up before any of this started).
- **The LanternDeeps discrepancy itself** — a live incident that sat
  undetected for 2 days (see "one thing to carry forward"). Worth knowing
  this class of drift exists and isn't caught by any routine check today.
- **Declined to spawn a subagent for BIOME_MOD_UNIFICATION_1** when asked —
  it's filed `for=BENCH`, already claimed by a BENCH session, and its own
  spec says step 1 (the backgrounded design/spec pass) is BENCH's to run
  before any FOUNDRY wave can start. Owner agreed ("unless it's not for
  you"). Left untouched.

## What is half-done, and where it stops

- `CORRECTED_LOAD_IN_PROGRESS` — a 629-mod cold load (Cryptoforge out, LanternDeeps
  swapped to `mandrake.rm.lanterndeeps`, RotSporeKit re-enabled, TerminalBiomes DLL
  redeployed) was launched and bridge was released before this handoff, load not yet
  confirmed ready; NEXT: check `Player.log` for `Bridge token:` (or a crash) and
  `rimflow bridge take` before touching the game further.
- `CRYPTOFORGE_HARVEST_RETIRE_1` — step 4 (ModsConfig removal) done, NOT yet
  load-verified or resaved; steps 1 (22-sprite art pass) and the resave still owed;
  NEXT: once the corrected load is confirmed clean, run
  `Transient/cryptoforge_retire_load_check.py` (loads `CANONICAL_ASHKARR_START_
  2026-09-12` via bridge, asserts `programState==Playing`) — do not resave without
  the owner's go-ahead.
- `LANTERNDEEPS_TIER_COLLISION_1` — step 4 (ModsConfig swap) done this session,
  NOT yet cold-load verified against the item's own PASS criteria (only the 5
  `RUT_Lantern*`/`RUT_PufferTendrils` price-history resolve failures, no
  duplicate-def error, `RM_LanternDeepEmergence`/`Mineshaft` resolve); NEXT: verify
  against the corrected load's `Player.log`, then hold the resave for the owner's
  word per the item's own step 7.
- `FEVERWOOD_PLANT_DANGLING_REFS_1` — filed, root cause UNMEASURED (ruled out
  mod-inactive, deploy-drift, XML-malformed, MayRequire — none fit, and the plants
  carry no `<comps>` so the TerminalBiomes-style stale-DLL explanation doesn't
  transfer); NEXT: re-check against the corrected load's `Player.log` — if it
  reproduces, this is a real standing defect and needs a deeper (RimSage-assisted)
  read of `BiomePlantRecord`'s custom loader timing.
- `TERMINALBIOMES` DLL fix — redeployed and verified in sync this session; NEXT:
  confirm `RM_Suulk`/`RM_Vaulisk` no longer show as dangling cross-references in the
  corrected load's `Player.log` (46 hits in the pre-fix load).
- `BLUEDESERT_MOD_DEPENDENCY_DECISION_1` — noted with a fuller dangling-ref
  inventory this session (BENCH's decision item, `needs owner`); NEXT: none for
  FOUNDRY, awaiting BENCH/owner's call (add the mod vs. redesign the death action).
- `BIOME_MOD_UNIFICATION_1` — correctly NOT started by FOUNDRY (BENCH's item,
  BENCH's spec pass first); NEXT: none for FOUNDRY until BENCH's spec lands and the
  owner rules the 5-point card agenda.

## Traps learned

- A deployed mod's `About.xml` packageId can drift from `ModsConfig.xml`'s
  reference with no error anywhere until a save-compatibility check refuses
  (filed: LESSONS_INBOX).
- A `.srchash` sidecar can be current while the DLL binary it stamps is stale —
  only `deploy_custom_mods.py`'s own drift-check catches it (filed: LESSONS_INBOX).
- `rimflow close --sha $(git rev-parse --short HEAD)` before committing the actual
  work records the pre-commit HEAD, not the real commit — the exact trap
  `using-rimflow`'s own skill already documents; corrected via a follow-up `note`
  this session (see: using-rimflow skill, `close --sha` rules).
- artpipe's facing daemon refuses a job whole (`bad_job_file`) if the prompt says
  "top-down" for any facing, even east/north — already recorded (see: last line of
  this same file, pre-existing).

## Commits

```
17007f2ad rimflow: bridge release before handoff
bd07940c9 ModsConfig backup before LanternDeeps/RotSporeKit fix
12f180372 Correct false "reverted" claim in LANTERNDEEPS_TIER_COLLISION_1
a5e38b38a Desert fill-out art: fix facing-contradicted prompts, requeue 39 jobs
29fe08b1b Grey Deep sitting agenda: merged proposal + card agenda (GREYSEA_FLOOR_PASS_1)
06ad23d6a File FEVERWOOD_PLANT_DANGLING_REFS_1: 15 plant dangling refs, cause UNMEASURED
a3ae11de2 Q17 ruled: biome mods merge NOW into one RimMandrake.Biomes mod (per-biome toggles)
8cab1d89a rimflow: close DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1 (corrected sha), note BLUEDESERT/wake-restart
201896a5e DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1: RM_ShadeMite, third shade-follow consumer
c28fa9719 File TWILIGHT_REVIEW_FIXES_1: 14 review findings from the Twilight build wave
eecf7d496 Code review: TerminalBiomes Twilight wave, 19 files clean
35010446a Ledger sync: weirs FlowWorks-overlap check recorded on SURFACE_RIVER_WEIRS_1
099fe6035 rimflow: sync ledger shards through DESERT_GLITTER_BIRDS_COMMENSALS_1 close
b5a8355f2 Stillsand fill-out: flora, review notes, name checks, art CSV (9 rows)
e78c6c146 rimflow: close DESERT_GLITTER_BIRDS_COMMENSALS_1, unblock DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1
bbbfc5b0f Stillsand fill-out: section 2, six new species
04242cb8f Build the shade-follow mechanism: RM_Comp_ShadowCaster + RM_JobGiver_FollowShadowCaster
5569cb5ff Stillsand fill-out: section 1, the measured gaps
a43626a01 Stillsand fill-out: skeleton
aa8b22e5a Stillsand execution: three FOUNDRY items from the ruled sitting
... 82 more: git log --oneline 71f4dbf63..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/codebase_health.html   ambient -- health-publisher/artpipe daemons, continuously running, predates and outlives this session
 M Transient/codebase_health.json   ambient -- health-publisher/artpipe daemons, continuously running, predates and outlives this session
 M Transient/codebase_health_artifact.html   ambient -- health-publisher/artpipe daemons, continuously running, predates and outlives this session
 M infrastructure/artpipe/daemon_run_20260927_derivefacings.log   ambient -- health-publisher/artpipe daemons, continuously running, predates and outlives this session
 M infrastructure/artpipe/registry.jsonl   ambient -- health-publisher/artpipe daemons, continuously running, predates and outlives this session
 M infrastructure/artpipe/throughput.jsonl   ambient -- health-publisher/artpipe daemons, continuously running, predates and outlives this session
 M infrastructure/dashboards/hub/data/health.json   ambient -- health-publisher/artpipe daemons, continuously running, predates and outlives this session
 M infrastructure/state/codebase_health_last.json   ambient -- health-publisher/artpipe daemons, continuously running, predates and outlives this session
 M infrastructure/state/queue/BENCH.md   generated -- rimflow auto-render on ledger change (mine and BENCH's concurrent activity both touched it), not authored content
 M infrastructure/state/queue/FOUNDRY.md   generated -- rimflow auto-render on ledger change (mine and BENCH's concurrent activity both touched it), not authored content
?? Transient/ModsConfig.FULL_plus_bacta_2026-09-24.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/Player.log.before_COLD_LOAD_RUN_SHEET_4_2026-09-23   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/Player.log.geneticrim_ctor_nre_2026-09-25   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/Player.log.pre-scald-round-20260926   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_facing_contradiction_manifests/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Ashworm_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Ashworm_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Ashworm_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Barbthorn_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Barbthorn_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Barbthorn_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_EmberCarpet.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Korrum_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Korrum_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Korrum_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Scrubgrass.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Spinerat_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Spinerat_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Spinerat_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Sporemass_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Sporemass_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Sporemass_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Sporepaw_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Sporepaw_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Sporepaw_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Starvine.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Stoneback_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Stoneback_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Stoneback_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/RSW_Whirlbloom.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_chimeglobe.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_chimeglobe_b.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_dorrak_dessicated.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_dorrak_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_dorrak_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_dorrak_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_glassfern.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_glassfern_b.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_glassfern_c.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_krissek_dessicated.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_krissek_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_krissek_halo_mote.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_krissek_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_krissek_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_palefloss.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_palefloss_b.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_palefloss_c.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_vekkit_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_vekkit_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/bluedesert_vekkit_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/canon_dewback_v1_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/canon_insectomorph_v1_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_brekkugar_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_brekkugar_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_brekkugar_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_dhukk_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_dhukk_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_dhukk_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_ghorrumak_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_ghorrumak_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_ghorrumak_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_gruzz_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_gruzz_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_gruzz_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_hulggarok_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_hulggarok_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_hulggarok_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_kessik_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_kessik_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_kessik_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_shekkur_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_shekkur_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_shekkur_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_thrizzik_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_thrizzik_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_thrizzik_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_ulkhorr_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_ulkhorr_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_ulkhorr_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_vrakk_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_vrakk_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_vrakk_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_zekkra_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_zekkra_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_zekkra_south.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_zhurrakor_east.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_zhurrakor_north.manifest.1790311643.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/crags_zhurrakor_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_falumpaset_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_feralgrazer_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_feralgrazer_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_feralgrazer_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_feralnerf_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_feralnerf_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_feralnerf_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_graniteslug_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_graniteslug_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_graniteslug_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_grank_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_grank_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_grank_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_greaterkraytdragon_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_greaterkraytdragon_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_greaterkraytdragon_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_horax_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_horax_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_horax_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_jakobeast_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_jakobeast_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_jakobeast_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_kowakianmonkeylizard_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_kowakianmonkeylizard_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_kowakianmonkeylizard_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_kraytdragon_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_kraytdragon_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_kraytdragon_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_krykna_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_krykna_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_krykna_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_mossbeetle_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_mossbeetle_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_mossbeetle_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_mossbeetlepupa_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_mossbeetlepupa_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_mossbeetlepupa_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_nerf_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_nerf_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_nerf_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_pikobis_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_pikobis_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_pikobis_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_plant_bloddle.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_plant_chakroot_wild.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_plant_hubbagourd_wild.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_plant_nysyllin_wild.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_porg_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_porg_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_porg_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_qormot_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_qormot_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_qormot_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_runyip_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_runyip_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_runyip_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_shaak_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_shaak_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_shaak_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_strill_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_strill_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_strill_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_teemuss_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_teemuss_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_teemuss_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_uvak_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_uvak_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_uvak_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_varactyl_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_varactyl_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_varactyl_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_voorpak_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_voorpak_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_voorpak_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_vulptex_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_vulptex_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_vulptex_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_warwyrm_east.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_warwyrm_north.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_warwyrm_south.manifest.1790254960.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_whisperbird_east.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_whisperbird_north.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_whisperbird_south.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_zeer_east.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_zeer_north.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/desertportb_zeer_south.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_brathek_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_brathek_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_brathek_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_chellow_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_chellow_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_chellow_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_drommath_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_drommath_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_drommath_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_gorrameth_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_gorrameth_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_gorrameth_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_grolth_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_grolth_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_grolth_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_kurreth_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_kurreth_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_kurreth_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_lommerel_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_lommerel_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_lommerel_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_murrelith_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_murrelith_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_murrelith_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_nemmel_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_nemmel_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_nemmel_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_ollareth_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_ollareth_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_ollareth_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_plant_ossagrel.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_plant_skethral.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_plant_thulvane.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_plant_tullick.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_plant_verrow.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_silloch_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_silloch_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_silloch_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_skellick_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_skellick_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_skellick_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_skreth_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_skreth_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_skreth_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_thavrik_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_thavrik_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_thavrik_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_thornbug_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_thornbug_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_thornbug_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_vaulm_east.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_vaulm_north.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/feverwood_vaulm_south.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_animalpersonhood.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_blindsight.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_bloodfeeding.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_cannibal.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_collectivist.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_darkness.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_femalesupremacy.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_fleshpurity.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_guilty.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_highlife.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_humanprimacy.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_individualist.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_inhuman.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_loyalist.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_malesupremacy.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_natureprimacy.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_nudism.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_painisvirtue.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_proselytizer.manifest.1790311644.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_raider.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_rancher.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_ritualist.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_shipborn.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_supremacist.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_transhumanist.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_treeconnection.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/glyph_tunneler.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_crossout.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_paste_flyer_p1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_paste_flyer_p2.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_paste_wanted_p1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_paste_wanted_p2.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_sigilframe_dripframe.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_sigilframe_halo.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_sigilframe_stencilbox.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_stencil_crown.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_stencil_fist.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_stencil_gear.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_tag_a_p1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_tag_a_p2.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_tag_b_p1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_tag_b_p2.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_tag_c_p1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_tag_c_p2.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_throwup_a_p1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_throwup_a_p2.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_throwup_b_p1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/graffiti_throwup_b_p2.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/nightside_mahllik_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/nightside_mahllik_north.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/nightside_mahllik_south.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/nightside_zhissa_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/nightside_zhissa_north.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/nightside_zhissa_south.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_brakkel_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_brunnock_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_cundral_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_gorbeleth_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_kaddrath_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_maddrick_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_mirrelbole_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_mourvel_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_phorrik_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_phorrik_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_quathis_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_quathis_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_sarnstilt_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_sarnstilt_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_sarquin_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_sarquin_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_thalquith_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_thalquith_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_tumbel_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_tumbel_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_vurmeloth_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_vurmeloth_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_wollick_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_wollick_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_zhorrel_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rm_zhorrel_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmleachmoss_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmleachmoss_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_east.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_north.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_north.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_south.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_south.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmvenomvine_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rmvenomvine_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_brogg_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_brogg_north.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_brogg_south.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_brullith_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_brullith_north.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_brullith_south.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_illoth_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_illoth_north.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_illoth_south.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_skerrith_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_skerrith_north.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_skerrith_south.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_thozzik_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_thozzik_north.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_thozzik_south.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_thozzikqueen_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_thozzikqueen_north.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rot_thozzikqueen_south.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_graffiti_stencil_imperialcog.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkro_dessicated_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkro_dessicated_v1.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_east.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_east.manifest.1790311645.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_north.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_north.manifest.1790311646.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_south.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_south.manifest.1790311646.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkroegg_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rsw_zakkroegg_v1.manifest.1790311646.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rswrawultracactus_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rswrawultracactus_v1.manifest.1790311646.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rswultracactus_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rswultracactus_v1.manifest.1790311646.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rut_grellbush.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rut_grellbush.manifest.1790311646.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rut_grellspine.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rut_grellspine.manifest.1790311646.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rut_wildhealroot.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rutfuzz_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rutstaggerseed_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_quota_failures/rutstaggerseeddish_v1.manifest.1790254961.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/artpipe_sizemismatch_control_manifests/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/biome_load_proof/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/biome_round_sentinels.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/bmt_verify/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/cellcheck.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/coldload_wait_2026-09-23.sh   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/configerror_dump.txt   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/cryptoforge_retire_load_check.py   mine, this session -- bridge load-check script for CRYPTOFORGE_HARVEST_RETIRE_1/LANTERNDEEPS_TIER_COLLISION_1 verification
?? Transient/deepfire_new4_contact.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/deepfire_pigment_review_assets/deepfire_crowncarpet_a.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/deepfire_pigment_review_assets/deepfire_crowncarpet_b.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/deepfire_pigment_review_assets/deepfire_pigmentjar_a.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/deepfire_pigment_review_assets/deepfire_pigmentjar_b.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/deepfire_sheet_serve.log   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/desk_after_click_check.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/desk_check_20260926.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/directional_probe.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/eg_check_state.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/eg_soak_test_plants.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/eg_spawn_test_plants.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/eg_step_and_report.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/events_resolved_2026-09-23.jsonl   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/game_state_check.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/game_state_check.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/game_state_check2.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/game_state_check2_crop.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/game_state_check2_dialog.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/game_state_check3.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/game_state_check3_crop.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/jawa_swim_ocean_20260926.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/jawa_swim_selected_20260926.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/jawa_swim_shallow_20260926a.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/jawa_swimjob_20260926.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/jawa_swimjob_close_20260926.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/jawa_swimpose_final_20260926.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/logs_2026-09-24/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu1.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu1.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu2.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu2.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu3.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu3.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu4.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu4.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu5.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu5.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu6.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu6.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu7.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/menu7.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/nightside_ice_research_rimworld_prior_art.md   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/nightside_ice_research_starwars_canon.md   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/pawn_survey.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/pigment_research/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/poll_bridge_ready.sh   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/poll_game_loaded.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/rw_state1.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/rw_state1_small.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/rw_state2.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/rw_state2_small.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/rw_state3.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/rw_state3_small.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/rw_win_capture.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald1.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald1.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald2.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald2.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald3.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald3.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald5.bmp   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald5.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_floor/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_renders_20260925.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase2_clear.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase2_close.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase2_steam.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase3_cast.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase3_clear.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase3_closeL.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase3_closeR.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase3_steam.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase_clear.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/scald_showcase_steam.png   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/swimcheck.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/swimcheck2.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/week_summary_art.md   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/week_summary_challenges.md   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/week_summary_design.md   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/week_summary_mechanics.md   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/world_label_sizes/CANONICAL_ASHKARR_START_2026-09-12.biome.equirect.svg   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? Transient/zoomprobe.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-firehawk.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_bluedesert.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_contagion.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_feverwood.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_floodedcanyon.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_forsakencrags.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_gelatinousslime.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_greentide.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_leaningscrub.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_longshade.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_miasma.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_nightsideice.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_poisonforest.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_pyrelands.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_rustcathedral.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_stillsand.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_terminalbiomes.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_theforge.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_therot.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_thesump.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_wasteland.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_webwork.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-proof_weepingstones.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? design/RimMandrake/biome_mod_unification_spec.md   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/active/RM_Gennok_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/active/RM_Gennok_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/active/RM_Hourbloom.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Dakkra_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Dakkra_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Dakkra_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Dakkra_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Dakkra_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Dakkra_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Dewfringe.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Dewfringe.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Duumma_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Duumma_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Duumma_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Duumma_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Duumma_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Duumma_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Gaanok_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Gaanok_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Gaanok_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Gaanok_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Gaanok_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Gaanok_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Gennok_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Gennok_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Glasscrust.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_Glasscrust.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_UltracactusPad.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/RM_UltracactusPad.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_eldspar.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_eldspar.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_fuselight.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_fuselight.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_ghostpane.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_ghostpane.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_keelgrass.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_keelgrass.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_pitchpearl.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_pitchpearl.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_skyharp.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_skyharp.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_slackwax.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_slackwax.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_stillbloom.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_stillbloom.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_stonewater.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_stonewater.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_tarspool.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/chill_plant_tarspool.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/rmshademite_v2_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/rmshademite_v2_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/rmshademite_v2_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/rmshademite_v2_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/rmshademite_v2_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/done/rmshademite_v2_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/failed/rmshademite_v1_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/failed/rmshademite_v1_east.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/failed/rmshademite_v1_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/failed/rmshademite_v1_north.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/failed/rmshademite_v1_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/failed/rmshademite_v1_south.manifest.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_KneelOllim.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Liikka_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Liikka_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Liikka_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Loomma_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Loomma_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Loomma_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Pirrik_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Pirrik_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Pirrik_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Qorrax_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Qorrax_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Qorrax_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Sollak_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Sollak_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Sollak_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Soorrak_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Soorrak_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Soorrak_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Tebbra_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Tebbra_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Tebbra_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Veessa_east.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Veessa_north.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/artpipe/pending/RM_Veessa_south.json   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/dashboards/hub/tabs/maturity.html   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/logs/harvested/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260926_142047.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/modlists/ModsConfig_before_miasma_predation_proof_2026-09-27.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? infrastructure/state/rescued/LanternDeeps_RUT/Assemblies/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
?? src/RimMandrake/Utils/firehawk_flight_probe.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it, unchanged by me this session
```

