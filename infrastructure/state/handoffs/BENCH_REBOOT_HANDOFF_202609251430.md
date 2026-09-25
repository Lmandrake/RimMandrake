# BENCH_REBOOT_HANDOFF_202609251430 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609250541`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The TerminalBiomes "move" was a COPY, and the fix pattern is now built.** The kit move left
16 byte-identical twin files in UtinniPatches — 8 pairs DEPLOYED and duplicate-loading live
(7 TerrainDefs among them), the two scatterer register patches double-appending their GenStep
to Base_Player. Fixed for the Scald set (`abff00ed8`, repo AND the live Mods folder), but the
same copy-not-move shape is untested for the other three seas' moved files — diff both trees
before believing any biome build's "moved". And the settings-gate seam every next sea pass
should REUSE, not reinvent: `RM_MechanicGates` in EnvironmentalHazards (`d1ae5e4f9`) —
unregistered = enabled, gate opt-in per def via `RM_MechanicGateExtension`, biome mod
registers its toggles at load. The Scald's five toggles are the worked example.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **The Scald bedazzle sitting is queued behind art renders** — 16 Scald jobs in the artpipe
  (6 cast @ priority 40, 10 buildings/items/flora @ 45, all expedited past the ~370-deep
  queue). Plan he approved in-session: one restart deploys DLLs+defs+art together, then the
  staged sitting.
- **The steam-sky weather overlay texture is an escalated art call** — a tiling world-space
  pan texture, a category the artpipe has never produced; ships functional-but-invisible
  until someone specs it. His art direction, no rush.
- **The live UtinniPatches folder changed under the running game**: 11 duplicate Scald twins
  + 3 moved flora files deleted, 10 peer-committed files synced. Takes effect next load;
  nothing the running session reads was touched.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `SCALD_FLOOR_PASS_1` — offline wave LANDED and pushed (4 commits `d1ae5e4f9`/`0b7d42689`/`abff00ed8`/`7d77db88e`: real settings gates, native RM_ flora, twin cleanup, owned catch textures; UtinniPatches+DivingInteraction deployed and verified); NEXT: when the 16 artpipe jobs render, wire them into TerminalBiomes/Textures (noohm/shulla become 3-facing Graphic_Multi), deploy TerminalBiomes ATOMICALLY at a game-down window (its defs name classes in the rebuilt DLLs — never deploy XML without the DLLs), then the live half: standalone load-proof, vent placement, dive proof, bedazzle sitting WITH the owner.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- fill_queue.py reports "0 filed, 0 errors" on a single JSON object — needs a LIST with canvas_w/canvas_h (filed: LESSONS_INBOX).
- A repo deletion does not undeploy: deploy_custom_mods.py keeps `-` strays, and --prune sweeps peers' strays too — targeted rm in the Mods folder is the fix (filed: LESSONS_INBOX).
- Same-subject artpipe jobs hide under different naming conventions (rutwelcomeblanket vs scald_welcomeblanket) — grep pending/ in every spelling before filing (filed: LESSONS_INBOX).
- "Moved" content can be a copy — diff both trees (filed: LESSONS_INBOX; the carry-forward above).
- Pre-existing selftest failures surfaced (not caused) by this wave: vorrel dangle and RotSporeKit live-prep vacuous pass (see: LONGSHADE_RM_MOD_BUILD_1 and THEROT_RM_MOD_BUILD_1 ledger notes, 2026-09-25) — do not re-triage.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
b598171bc Ledger sync: close BACTA_SIDE_ITEMS_1, block four live-verify items, bridge release
5b9defb0f Live-verify batch on the full 627-mod list: results for five items
5488e4ddf prove_fish_bestiary_live: fix three instrument bugs that voided its verdicts
5fb3dd079 FlowWorks bottles header: delete the false "no tank building exists" claim
8d3af1636 Ledger sync: SHIELD_MODS_LEVERAGE_1 claim/start/note/verify (cryo envelope)
8193255c7 SHIELD_MODS_LEVERAGE_1: build shd:cryo-envelope, the last unbuilt ruled shield
b0377e47b RIVER_STEAM_ANIMATION_1: offline re-verify pass (bridge held by a peer window)
37e1c92fa HELIX_TELLUROX_BUILD_1: re-verify offline, still correctly blocked
456c7d5e4 Ledger sync: GOO_BOOM_COMMISSION_1 unblock/close (RUT_Vhessk built)
b00ea4272 GOO_BOOM_COMMISSION_1: build RUT_Vhessk, the one boom creature that replaces the cut family
feddf8808 THEY_MOD_REPLICATION_1: replicate They! (Giant Ants) in our own tier
f70984178 DONOR_DEFS_PORT_TO_OURS_1: census the ten smaller donors (spec step 1)
2db13d541 Fix four defs the full load discards: Bacta field items, three RUT races
99e465258 Ledger sync: re-render queue projections after VQE_ANCIENTS_CURATION_1 close
8a10813c2 Ledger sync: VQE_ANCIENTS_CURATION_1 unblock + close
a3cfeee65 VQE_ANCIENTS_CURATION_1: close out steps 1/2/4 verification gaps
b9e9e6db5 RUT_SCAVENGEREVENTS_BUILD_1: license check, stale-scope fix, dead row cleanup
2475856ba Ledger sync: ROSTER_DEAD_BMT_NAMES_SWEEP_1 closed, prose moved to closed/
0e7e47af7 ROSTER_DEAD_BMT_NAMES_SWEEP_1: close — both owner-judgment calls landed elsewhere
4708b0400 COMMISSION_LEDGER_CLEANUP_1 wave 14: re-checked, all 6 remaining groups still contended
... 11 more: git log --oneline e2d11dea5..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-25T08:24:17Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
D Transient/_focus_check.bmp   a peer window's live-verify debris — theirs
 D Transient/_focus_now.bmp   a peer window's live-verify debris — theirs
 M Transient/codebase_health.html   health publisher's auto-rebuild — FOUNDRY loop's
 M Transient/codebase_health.json   health publisher's auto-rebuild — FOUNDRY loop's
 M Transient/codebase_health_artifact.html   health publisher's auto-rebuild — FOUNDRY loop's
 D infrastructure/artpipe/_artsrc/lockjaw_improve_a_r7/lockjaw_improve_a_r7.png   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/_artsrc/lockjaw_improve_b_r7/lockjaw_improve_b_r7.png   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   artpipe daemon's churn — never commit mid-flight
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
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_cundral_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rut_wildhealroot.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutbloomcrop_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutdarkcrust_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutdeltaloam_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutemperorvulture_v1_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutemperorvulture_v1_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutemperorvulture_v1_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutfleetflier_v1_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutfleetflier_v1_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutfleetflier_v1_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutfuzz_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutglower_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutglowercrust_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutkarrathil_v1_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutkarrobel_v1_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_east.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_north.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_south.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutstaggerseed_v1.json   artpipe daemon's churn — never commit mid-flight
 D infrastructure/artpipe/pending/rutstaggerseeddish_v1.json   artpipe daemon's churn — never commit mid-flight
 M infrastructure/artpipe/pending/rutwelcomeblanket_v1.json   mine — priority bump 100->45 for the Scald pass; pending/ stays uncommitted by convention
 M infrastructure/dashboards/hub/data/health.json   health publisher's auto-rebuild — FOUNDRY loop's
 M infrastructure/state/codebase_health_last.json   health publisher's auto-rebuild — FOUNDRY loop's
MM infrastructure/state/queue/BENCH.md   rimflow projection, mixed mine+peer renders — commits with the next ledger sync
 M src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll   FOUNDRY's build outputs / tier backups — leave alone
 M src/RimMandrake/Utils/modset_builder.py   FOUNDRY's build outputs / tier backups — leave alone
 M src/RimUtinni/LanternDeeps/Assemblies/RimMandrake.Utinni.LanternDeeps.dll   FOUNDRY's build outputs / tier backups — leave alone
D  src/RimUtinni/UtinniPatches/Patches/RotSpecies_NamesAndSizes.xml   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/AgaricusDomeCap.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agarilux/Agarilux_A.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/AgariluxPrime.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agaripawn/Agaripawn_east.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agaripawn/Agaripawn_north.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agaripawn/Agaripawn_south.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/ArbuscularMycorrhiza/ArbuscularMycorrhiza_A.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Bryolux/Bryolux_A.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/DribblingCap/DribblingCap_A.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/GiantAgarilux/GiantAgarilux_A.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/GlowingAgarilux/GlowingAgarilux_A.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Glowstool/Glowstool_A.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/LilacBeacon/LilacBeacon_A.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/MycoidColossus/MycoidColossus_east.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/MycoidColossus/MycoidColossus_north.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/MycoidColossus/MycoidColossus_south.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/RecurvedStropharia.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/SlimyPholiota/SlimyPholiota_A.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Swarmling/Swarmling_east.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Swarmling/Swarmling_north.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Swarmling/Swarmling_south.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpawn/Wildpawn_east.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpawn/Wildpawn_north.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpawn/Wildpawn_south.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpod/Wildpod_east.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpod/Wildpod_north.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpod/Wildpod_south.png   TheRot move, peer's staged deletions — leave alone
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/WitchesOyster.png   TheRot move, peer's staged deletions — leave alone
?? deployed/config/ModsConfig.before-tier-firehawk.xml   FOUNDRY's build outputs / tier backups — leave alone
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   FOUNDRY's build outputs / tier backups — leave alone
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
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/artpipe/pending/crags_brekkugar_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_brekkugar_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_brekkugar_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_dhukk_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_dhukk_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_dhukk_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ghorrumak_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ghorrumak_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_ghorrumak_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_gruzz_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_gruzz_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_gruzz_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_hulggarok_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_hulggarok_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_hulggarok_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/crags_kessik_east.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/artpipe/pending/scald_bladderboilcatch_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_noohm_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_noohm_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_noohm_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_saalcatch_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_shulla_v1_east.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_shulla_v1_north.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_shulla_v1_south.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_shullacatch_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_steamcatchbuilding_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_ventbuilding_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_wreckframe_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_wreckhull_v1.json   artpipe daemon's churn — never commit mid-flight
?? infrastructure/artpipe/pending/scald_wrecktank_v1.json   artpipe daemon's churn — never commit mid-flight
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
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   owner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/handoffs/FOUNDRY_REBOOT_HANDOFF_202609251428.md   not mine — investigate before touching
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   owner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   owner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   owner's Desktop tooling backups — his to commit or cull
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   owner's Desktop tooling backups — his to commit or cull
?? src/RimMandrake/Utils/firehawk_flight_probe.py   not mine — investigate before touching
```

