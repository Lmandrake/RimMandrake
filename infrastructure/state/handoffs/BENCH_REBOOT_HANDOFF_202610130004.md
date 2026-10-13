# BENCH_REBOOT_HANDOFF_202610130004 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610121341`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The ratchet pilot is one Pyrelands green pass from done: pass 6 (`Transient/bench_live_20261012g/SITTING.md`, HEAD 7589d73ef6) had GSS 106/106 and FlowWorks 61/61 at one HEAD; Pyrelands is 25/3/8 on the brand-new ash build. The ash paint and scorch harness are fixed offline since (160a9acbef) and need ONE more live pass (redeploy first — `deploy --apply` now prunes repo-deleted files). Unattended live passes must never wait on a prompt: pass 6 sat 2.3 h on an "allow bash" prompt; a PermissionRequest hook (0766c8c531) and defaultMode bypassPermissions now remove that.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Review queue, 6 rows, ranked: `D:\Luke\dev\RimMandrake\Transient\ratchet_owner_review_2026-10-12.md` (ash ground look, FireEcology walk re-validation, embergrass thresholds 26.2%/59.8% vs 25/60, provisional creature art, canal look, pilot verdict).
- Account reset deferred to next week by his card; budget tight until Wed 2026-10-14 16:00 PDT.
- ART_SHEET_REDESIGN_FRESH_OR_REFUSE is HIGH PRIORITY for Wed night (his words on the item, plus his two new requirements: retire in-use art in the same pass as "use this"; no "accept unchanged").
- Changed his machine config on his word ("Change that then."): `~/.claude/settings.json` defaultMode plan -> bypassPermissions (backup `~/.claude/settings.json.bak-20261012`).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED` — implemented (3cf1662bbb), live A1 FAIL (deep ash 0.840/0.778), A2/A3 PASS, A4/A5 partial; paint retuned b761462eba offline; NEXT: run Pyrelands main + long split live at HEAD after redeploy and close if ground_deep_ash >= 0.85 on two fresh maps
- `PYRE_DEEP_ASH_TUNE_ONE_POINT_SHORT` — implemented offline (b761462eba), coverage unmeasured; NEXT: read ground_deep_ash on two fresh maps in the next live pass
- `PYRE_HARNESS_SCORCH_CAP_REPAIR_SHARED_BUDGET` — implemented (e0aab994e3); NEXT: confirm scorchfruit_fire_born PASS after fire_tick_effects in one full Pyrelands run
- `PYRE_RUINS_ASH_DIAGNOSE_TEN_THEN_TWO` — filed, untraced (10/10 vs 2/10 ruins ashed on two worlds); NEXT: read the ruin-scorch code path against both worlds' evidence in bench_live_20261012g and fix offline
- `PYRE_SCORCH_YIELD_DIAGNOSE_FLAKY_HARVEST` — filed, flaky; NEXT: rerun scorchfruit_produces after the scorch-cap fix and diagnose only if it still fails
- `RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP` — doing; verdict in ratchet design §H, GSS+FlowWorks green at one HEAD; NEXT: after Pyrelands goes green, run all three suites at one HEAD and put review-queue row 6 to the owner
- `POND_BED_DESIGN_LAKES_ARE_TALL_CANALS` — doing; every card ruled 2026-10-12, build items filed (pond return leg, hollow bed, volume unify, elevation, deep dig, pit climb x3); NEXT: close it citing those items once FOUNDRY has taken the first build

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Unattended "allow bash" prompt stalled live pass 6 for 2.3 h (see: .claude/hooks/auto_allow_bash_permission.py)
- northstar_driver run --mod Pyrelands without --plan does an empty 0-row run (filed: lessons)
- Harmony workshop 'Current' folder gone; fixed in src/Directory.Build.props (filed: lessons)
- deploy_custom_mods kept repo-deleted files in the game copy (stale AshLadder.xml) — fixed d7139d7e6b (see: DEPLOY_PRUNE_DELETED_FILES_STALE_ASH_LADDER)
- Art sheet "now" column came from a stale def dump (pre-rename texPaths) and still passed the gate (see: ART_SHEET_REDESIGN_FRESH_OR_REFUSE)

## Closed since the last handoff (10)

- `PYRE_ASH_REDESIGN_BURN_FEEDS_THE_FIELD` — 7f4bd3e283
- `CAMPAIGN_STORY_SITTING_1` — 05d6077603
- `ASSIGNMENT_SHEETS_VERDICT_SITTING_1` — 05d6077603
- `CANAL_FRONT_FIX_WRONG_END_WETS_FIRST` — 6202592e59
- `IDEO_DEITY_HUNT_GOD_WITH_NO_NAME` — c474102eae
- `FLOWWORKS_ORACLE_SYNC_V2_MISSES_THE_CREEP` — c474102eae
- `PYRE_BURN_LINE_PROVE_TWO_QUIET_DAYS` — c474102eae
- `HARMONY_PATH_REPAIR_CURRENT_WENT_MISSING` — 7a223e165e8f
- `DEPLOY_PRUNE_DELETED_FILES_STALE_ASH_LADDER` — d7139d7e6b
- `PYRE_SETTINGS_SELFTEST_FIX_UNLUCKY_THIRTEEN` — b4d04d123d

## Filed and still open (8) — the next seat's queue

- `ART_SHEET_REDESIGN_FRESH_OR_REFUSE` — Art review sheets must guarantee freshness by construction (hashes/hooks/design): never serve an image that is not the art installed now. HIGH PRIORIT
- `PAINTER_REGIONS_RETHINK_GHOSTS_MAY_HAUNT` — AFTER the one-time repaint: revisit the 5 painter-only regions (Ashteeth, Ember Sink, Fall Line Barrens, Scald Spine, Umbra Trap) with the owner — the
- `CANOPY_SHADE_DESIGN_BIG_DARK_PATCHES` — Jungle-adjacent heavily vegetated biomes (Webwork, Greentide, LongShade...): tree canopy casts BIG shade patches; sunlit regions shine clearly. Design
- `PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE` — burrowers_dive FAIL once (grazer Flee/Wait), PASS on rerun; passed 20261012b
- `PYRE_DEEP_ASH_TUNE_ONE_POINT_SHORT` — ash build: fresh Pyrelands map is 0.840 deep ash of 57454 open-land cells, bar pyre_ground_deep_ash is >=0.85 (gravel 5843 = 10.2%, soil 842, soil-ric
- `PYRE_HARNESS_SCORCH_CAP_REPAIR_SHARED_BUDGET` — HARNESS: fire_tick_effects leaves 35 ScorchFruit on the map (cap 40) so scorchfruit_fire_born later finds 0 in its cohort (FAIL in full run, 25 PASS a
- `PYRE_RUINS_ASH_DIAGNOSE_TEN_THEN_TWO` — ruins_scorched: 10 of 10 sampled ruins carry loose ash on one fresh world, 2 of 10 (want >=30%) on the next, same HEAD and defs. MOD (ash scatter on r
- `PYRE_SCORCH_YIELD_DIAGNOSE_FLAKY_HARVEST` — scorchfruit_produces: in two full runs no ScorchFruitYield after a forced harvest of 3 plants; alone on a reloaded fixture it harvested both times, th

## Commits

```
3845d2a4ce Owner review queue refreshed after pass 6
160a9acbef Ledger: BENCH implemented marks
b64a3f7372 Ledger: BENCH four Pyrelands/deploy items
b761462eba Pyrelands paint: deep ash ~90%+ (gravel rung <0.02, rock-margin gravelTerrain -> deep ash, rarer pockets) + lint guard; live re-measure owed
e0aab994e3 Pyrelands harness: fire-pad chains clear their ScorchFruit so the per-map cap (40) is not shared between chains
0766c8c531 PermissionRequest hook: auto-allow Bash prompts (an unattended prompt stalled live pass 6 for 2.3 h)
b4d04d123d selftest_settings_screens: Pyrelands expects the 13th group, Ash field (scope Now)
d7139d7e6b deploy: --apply prunes game files the repo deleted (git history), keeps hand-edits, refuses paths outside the mod folder; selftest
29293ffc79 BENCH pass 6 (pilot exit run) at 7589d73ef6: GSS 106/106, v2 61/61, ash build A1 FAIL; files 5 items
1e32b92105 Ledger: HARMONY_PATH_REPAIR closed at 7a223e165e8f
7a223e165e Harmony reference resolves in one place (src/Directory.Build.props): 1.6 then Current, clear error if none; winbuild stages the props
7589d73ef6 lesson: Harmony Current path gone; file HARMONY_PATH_REPAIR_CURRENT_WENT_MISSING
e0f577d545 Ledger: PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED implemented at 3cf1662bbb3b, live proof owed (A1-A5)
3cf1662bbb Pyrelands ash field: deep ash everywhere, watered fertility, fresh-burn bonus, ambient ash drift
a275b5980c results join: find FlowWorks checkout results (manifest.py stem != result stems); selftest drops magic row counts
af80f8fd8a lesson: northstar_driver needs --plan; ledger: BENCH takes ash build
17512e3a83 Ledger: BENCH pass 5 closes IDEO_DEITY, FLOWWORKS_ORACLE_SYNC, PYRE_BURN_LINE; files PYRE_BURROWERS flake
c474102eae BENCH live pass 5 evidence at 90e2783301: GSS 106/106, v2 61/61, river 17/3, Pyrelands burn_line PASS
90e2783301 Ledger: burn_line arm and ideo structure fallback implemented (live proof owed)
480611e4df Pyrelands burn_line: 120k-tick quiet-arm (long split); Utinni fixed-ideo structure fallback (hypothesis)
... 27 more: git log --oneline b7a4256a7f..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-12T21:31:22Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   served sheet / other seat output, not this session's work
 M Transient/mc_human_review/KEYSHEET.md   served sheet / other seat output, not this session's work
 M Transient/mc_human_review/keysheet.html   served sheet / other seat output, not this session's work
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   served sheet / other seat output, not this session's work
?? conversations/2026-10-02-1217-54206aec.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-02-1952-4b4a687b.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-02-2332-d58606e4.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-03-1458-7ed5ddfd.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-04-2105-400ef7dc.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-04-2219-962263b0.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-05-1426-fab8a134.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-06-0601-5ab77072.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-06-1305-ecebcb6f.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0058-b305fb53.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0059-c857706d.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0120-033b16fc.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0547-d6861da6.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-1520-6a6f7a30.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0001-cc216258.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0158-8aeef5fc.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0215-c4ae9260.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0217-3acaea39.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1348-bac7589f.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1411-2294fe53.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1411-3ffd55d0.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1413-52caf5c0.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1413-658e0588.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1414-b4b8553c.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1428-de9591de.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-09-0450-85e0a0f9.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-09-1308-818639f9.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-0040-5e2fd376.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-0049-58eabd09.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-0440-c71b568d.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-1341-91d07ad1.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-2102-71d8c9eb.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-0052-2f152d1c.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-1934-f086ce1a.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-1953-24347684.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-2000-edefebc8.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-12-0625-88710e84.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-12-1403-b0ee9afc.md   generated (conversations.py; hourly sweep commits)
?? deployed/config/ModsConfig.before-gss-restore-20261010.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-flowworks_vepipe.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-ratchet_pilot.xml   generated (modset_builder ModsConfig backups)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   untracked art, not BENCH's (artpipe/FOUNDRY); left alone
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   untracked art, not BENCH's (artpipe/FOUNDRY); left alone
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T034753.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T040637.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T041535.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T042312.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T050823.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T052325.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/GSS   stray path, not BENCH's this session; left alone
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T220702.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T230453.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json   generated harness output from live runs (not committed by design)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   untracked art, not BENCH's (artpipe/FOUNDRY); left alone
```

