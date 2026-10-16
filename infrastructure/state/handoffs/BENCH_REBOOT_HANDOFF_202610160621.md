# BENCH_REBOOT_HANDOFF_202610160621 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610160353`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Night order (owner, Thu 10-15 ~22:35 PDT): "I must go to bed/AFK. Feel free to get a head start on the next sprint cycle while I sleep. I will finish these reviews tomorrow morning. If you don't need the bridge tonight after the saves are prepared, let Foundry go for its donor retirement items too." It ENDS when he next writes. The FlowWorks walk save RM_fw_walk_20261016 is built and loaded in game (paused); the bridge is FREE for FOUNDRY's Phase 0. He still owes the FW tour + S0. Sprint scope is now three biomes + ExplosiveGrowth folded into Baroque Biomes (his ruling 10-16, reverses unification Q4); the Rot leads the sprint after.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- FW tour: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\RM_fw_walk_20261016.rws` (loaded now; 39/39 visuals, 85/87 gallery, 125 sign books; goto via review_map.py --goto). Then restore his ModsConfig from Transient/bench_live_20261015_l2/ModsConfig.OWNER_BACKUP_before_review_walk.xml.
- S0: approve §1 criteria incl. §1.4 ExplosiveGrowth X1-X5 in design/RimMandrake/biome_sprint_kickoff_2026-10-15.md; X1 needs mandrake.rut.plantgrowth in biomes_sprint (left out: changes growth under every suite).
- Facing-size standard (one decision): fix only the 76 pictures too big vs vanilla's own envelope, or hold all ~345 to the ground-camera rule (ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL).
- GSS 1.0.0 package is stale: GSS DLL changed after packaging (52a6a44d20, 0c3e8fe248); repackage before any release.
- Deployed tonight from ce02e94845 incl. FOUNDRY's Phase 0 art; missing pictures for its donor ports logged on DONOR_DEFS_PORT_TO_OURS_1.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK` — built a2b4a7cd22, not deployed (companion DLL deploys with game closed); NEXT: at the next game-closed window run `build.py --gm --apply`, then prove release/re-pin on a quicktest and on RM_pyre_review_20261015_r2.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- rimflow refuses a too-short --owner-said ("Yup.") that doesn't name the action; quote the sentence it answered or use --why (see: ledger notes on HOSE_REEL_COUPLING_REDRAW_QUIT_STARING_BACK)
- Hand-editing a sheet decisions.json to schema 1 makes art.py enact plan nothing; convert with decisions_v2.py --apply (see: 7d4cc8be98)
- Sheet row re-collapsed as "already ruled" on every click (filed: lessons 20261016T045739Z)
- Shared _Shared/PatchApplier.cs re-reads every settings class on load (see: PATCH_APPLIER_FIX_WRONG_SETTINGS_REREAD)

## Closed since the last handoff (2)

- `FLYER_NORTH_REDRAW_WINGS_LEFT_AT_HOME` — 19775594de
- `GSS_WALK_HOSES_EXCISE_REELED_IN` — b805ca93d9

## Filed and still open (9) — the next seat's queue

- `ROT_BIOME_PROVE_FIRST_IN_LINE` — The Rot is the first biome of the sprint after BIOME_SPRINT_PROVE_SCRUB_SETS_PACE (after Phase 0 removes its Alpha Animals/Alpha Biomes content); plan
- `SPILL_FILTH_FIX_SOIL_SAYS_NO` — RM_Filth_LiquidSpill (placementMask Natural) is refused on Soil (filthAcceptanceMask Unnatural, measured live 2026-10-15): outflow spills never show o
- `FLYER_VARIANTS_INSTALL_MORE_FACES_PLEASE` — Install the owner's variant picks as alternate graphics: Fleet Flier B/C/D (alien sheet; his note 'Use B, C, D as variants'), Murrelith B-H (his note 
- `LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY` — LeaningScrub saved site + the Lean rows (heading lock, upwind flee, downwind fire)
- `GSS_TOGGLES_FIX_OFF_MEANS_OFF` — GSS: settings that do not switch their patches off (run queueing, anchor looks, power scope, tap debit) — make each patch honour its toggle; defaults 
- `PATCH_APPLIER_FIX_WRONG_SETTINGS_REREAD` — _Shared/PatchApplier.cs: AfterExpose should re-read only the fields of the settings class being loaded; rebuild the ~30 mods that share it (DLL+srchas
- `CONTAGION_SITE_BUILD_SKY_STAYS_CALM` — Saved RM_Contagion test site (on-Contagion arm), no Burn at save/load
- `CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK` — Contagion northstar: split the test arms so the suite runs on a saved Contagion site (northstar_site.py refuses an already-Contagion map)
- `PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK` — Review-save pen animals: companion tools to end/re-apply their 60000-tick Wait pin (jawa/pen_release, jawa/pen_pin) + human_review.py --release-pens/-

## Commits

```
cb959641bc BENCH night: conversation record and ledger shard
6b584dd0ff Ledger: deploy notes (flyer, hose reel), load-gap note for FOUNDRY, bridge released
2147d6fa20 FW walk save RM_fw_walk_20261016: 39/39 visuals + 85/85 gallery, 125 sign books; hose outlets cleared west
8159a1c576 Ledger: PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK built; owes A1 L1, A2 L2 (live)
a2b4a7cd22 Companion pen_release/pen_pin + human_review.py --release-pens/--pin-pens (built, not deployed)
8cdcd1cdd6 Cauldron saved-site recipe now runs on shared biome_site.py; vent count is its probe census record shape is {natives, probe:{vents}} now, like Contagion/LeaningScrub.
af209389cb File CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK for FOUNDRY
360bc76fa1 Ledger: file CONTAGION_SITE_BUILD_SKY_STAYS_CALM, notes on both site items
b4d14d44c8 Contagion + LeaningScrub saved-site recipes (offline), shared biome_site.py; O-SITE needs loadVerified
caa5f8450b File PATCH_APPLIER_FIX_WRONG_SETTINGS_REREAD (shared patch helper, ~30 mods)
0576b27e63 Code review: 8 GSS files from 52a6a44d20 marked clean
0c3e8fe248 GSS: apply Harmony after both settings files load; reforce failed features after the settings window
0951d0a6c9 File GSS_TOGGLES_FIX_OFF_MEANS_OFF: some GSS toggles do not switch their patches off
231957f6be Ledger: GSS_PATCHES_FIX_TWENTY_THREE_UNLABELLED implemented -> built
52a6a44d20 GSS: [PatchFeature] on all 23 Harmony classes; settings keep a failed feature's player value
e730d42b7b File LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY (was LEANING_SCRUB_LEAN_SITE_1); packet names it; D0 progress
e1e5a6ff3a Cauldron saved-site recipe (offline): site_spec + prep_site, test_site_saves 'cauldron' site
b96ef7528c Ledger: BENCH shard events from tonight's helpers
61489166de Biome sprint offline preflight: shared rows + Cauldron/Contagion/LeaningScrub wrappers
95337e5f45 Facing-scale lint calibrated per body plan: vanilla flags 4.7% (LOO), roster 65% -> 48% Known positives (FireWasp, Anooba m, Furnace beast) still flag on old art; 76 pictures beyond vanilla's envelope.
... 56 more: git log --oneline 34fec8300f..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-16T06:20:57Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   ours: regenerated by tonight's sheet builds (derived, left uncommitted)
 M Transient/mc_human_review/KEYSHEET.md   not ours: predates this session (left untouched)
 M Transient/mc_human_review/keysheet.html   not ours: predates this session (left untouched)
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   not ours: predates this session (left untouched)
 M conversations/2026-10-12-1403-b0ee9afc.md   not ours: predates this session (left untouched)
 M conversations/2026-10-13-0007-b342a8ee.md   not ours: predates this session (left untouched)
 M deployed/config/ModsConfig.before-tier-bridge.xml   not ours: predates this session (left untouched)
 M src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnKitTools.cs   not ours: predates this session (left untouched)
?? conversations/2026-10-02-1217-54206aec.md   not ours: predates this session (left untouched)
?? conversations/2026-10-02-1952-4b4a687b.md   not ours: predates this session (left untouched)
?? conversations/2026-10-02-2332-d58606e4.md   not ours: predates this session (left untouched)
?? conversations/2026-10-03-1458-7ed5ddfd.md   not ours: predates this session (left untouched)
?? conversations/2026-10-04-2105-400ef7dc.md   not ours: predates this session (left untouched)
?? conversations/2026-10-04-2219-962263b0.md   not ours: predates this session (left untouched)
?? conversations/2026-10-05-1426-fab8a134.md   not ours: predates this session (left untouched)
?? conversations/2026-10-06-0601-5ab77072.md   not ours: predates this session (left untouched)
?? conversations/2026-10-06-1305-ecebcb6f.md   not ours: predates this session (left untouched)
?? conversations/2026-10-07-0058-b305fb53.md   not ours: predates this session (left untouched)
?? conversations/2026-10-07-0059-c857706d.md   not ours: predates this session (left untouched)
?? conversations/2026-10-07-0120-033b16fc.md   not ours: predates this session (left untouched)
?? conversations/2026-10-07-0547-d6861da6.md   not ours: predates this session (left untouched)
?? conversations/2026-10-07-1520-6a6f7a30.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-0001-cc216258.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-0158-8aeef5fc.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-0215-c4ae9260.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-0217-3acaea39.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-1348-bac7589f.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-1411-2294fe53.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-1411-3ffd55d0.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-1413-52caf5c0.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-1413-658e0588.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-1414-b4b8553c.md   not ours: predates this session (left untouched)
?? conversations/2026-10-08-1428-de9591de.md   not ours: predates this session (left untouched)
?? conversations/2026-10-09-0450-85e0a0f9.md   not ours: predates this session (left untouched)
?? conversations/2026-10-09-1308-818639f9.md   not ours: predates this session (left untouched)
?? conversations/2026-10-10-0040-5e2fd376.md   not ours: predates this session (left untouched)
?? conversations/2026-10-10-0049-58eabd09.md   not ours: predates this session (left untouched)
?? conversations/2026-10-10-0440-c71b568d.md   not ours: predates this session (left untouched)
?? conversations/2026-10-10-1341-91d07ad1.md   not ours: predates this session (left untouched)
?? conversations/2026-10-10-2102-71d8c9eb.md   not ours: predates this session (left untouched)
?? conversations/2026-10-11-0052-2f152d1c.md   not ours: predates this session (left untouched)
?? conversations/2026-10-11-1934-f086ce1a.md   not ours: predates this session (left untouched)
?? conversations/2026-10-11-1953-24347684.md   not ours: predates this session (left untouched)
?? conversations/2026-10-11-2000-edefebc8.md   not ours: predates this session (left untouched)
?? conversations/2026-10-12-0625-88710e84.md   not ours: predates this session (left untouched)
?? conversations/2026-10-13-1146-7444c21a.md   not ours: predates this session (left untouched)
?? conversations/2026-10-15-1939-5e86e9cb.md   not ours: predates this session (left untouched)
?? deployed/config/ModsConfig.before-gss-restore-20261010.xml   not ours: predates this session (left untouched)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   not ours: predates this session (left untouched)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   not ours: predates this session (left untouched)
?? deployed/config/ModsConfig.before-tier-flowworks_vepipe.xml   not ours: predates this session (left untouched)
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   not ours: predates this session (left untouched)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   not ours: predates this session (left untouched)
?? deployed/config/ModsConfig.before-tier-ratchet_pilot.xml   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/RM_WallFace_North.png   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/RM_WallFace_Side.png   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/out/   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/guides/   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/out/   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_east.log   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_north.log   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_south.log   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.log   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.png   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.log   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.png   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.log   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.png   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.log   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.png   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.log   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.png   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.log   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.png   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runA.out   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runB.out   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runC.out   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T034753.json   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T040637.json   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T041535.json   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T042312.json   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T050823.json   not ours: predates this session (left untouched)
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T052325.json   not ours: predates this session (left untouched)
?? src/RimMandrake/GSS   not ours: predates this session (left untouched)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T220702.json   not ours: predates this session (left untouched)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T230453.json   not ours: predates this session (left untouched)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json   not ours: predates this session (left untouched)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230218.json   not ours: predates this session (left untouched)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230455.json   not ours: predates this session (left untouched)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230639.json   not ours: predates this session (left untouched)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231027.json   not ours: predates this session (left untouched)
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231203.json   not ours: predates this session (left untouched)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   not ours: predates this session (left untouched)
```

