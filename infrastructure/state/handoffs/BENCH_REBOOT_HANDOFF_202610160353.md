# BENCH_REBOOT_HANDOFF_202610160353 — READ FIRST on wake

Follows `BENCH_HANDOFF_202610151936`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The ratchet pilot is CLOSED and the owner approved the whole Pyrelands review save in game (RM_pyre_review_20261015_r2). The pattern that worked: a review save built to `design/RimMandrake/biome_review_save_standard.md` (v1.1). That means sign books per station, pens of four facing S/E/N/W, controls that really compare, and an offline graphics audit of what the GAME resolves before he walks it, with defects on one pick sheet. Every biome review in the next sprint uses that standard. Donor art mod retirement (SWAC, Alpha Animals, Alpha Biomes) comes first: owner, 2026-10-15: "we should finish THAT before we try to review any biomes beyond the Pyrelands." 

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Release = "ready, not published": PACKAGING for GSS, FlowWorks and Pyrelands is not started (About text, preview image, version). He asked for it in the background while he looks at GSS and FlowWorks again.
- Facing-size fixes (fire-wasp + Skerrel, Anooba male, furnace beast; 3791e139ea) are installed but NOT deployed. Deploy Pyrelands + SWBestiary at the next restart, only when he says.
- The facing-scale lint flags 456/698 roster pictures against vanilla's ~5%, so treat it as uncalibrated (ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL).
- Next sprint: three biomes deep (BIOME_SPRINT_PROVE_SCRUB_SETS_PACE), with 17 kickoff cards plus N1-N5 ruled on the ledger. Packet: design/RimMandrake/biome_sprint_kickoff_2026-10-15.md, phase 0 at §0.5. Calendar INFERRED: phase 0 10-16..10-19, sign-off ~10-27..29. FOUNDRY builds, BENCH tests.
- The game is UP on the 23-mod ratchet_pilot+EmpirePursuit tier, with his ModsConfig backed up at Transient/bench_live_20261015_l2/ModsConfig.OWNER_BACKUP_before_review_walk.xml (restore it when he's done with review saves).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RELEASE_PACKAGING` — not started; NEXT: per mod (GimmeSomeSlack, FlowWorks, Pyrelands) write About.xml description, preview.png and version, as a background agent while he walks GSS/FlowWorks.
- `WALKTHROUGH_MAPS_GSS_FW` — builders now place sign books (5a66172ad5); maps not built; NEXT: build and save the GSS (41 stations) and FlowWorks (75+8) walkthrough saves to the review-save standard, with a graphics audit first.
- `FACING_SCALE_DEPLOY` — 3 Pyrelands creatures rescaled, not deployed; NEXT: on his word, close the game, deploy Pyrelands (--compose biomes) + SWBestiary from a clean export, relaunch.
- `ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL` — lint over-flags; NEXT: calibrate facing_scale_lint.py (fish/snake/lizard handling) before any roster-wide rescale.
- `BIOME_SPRINT_PROVE_SCRUB_SETS_PACE` — planned and ruled; NEXT: start phase 0 (donor retirement: SWAC, Alpha Animals, Alpha Biomes) per kickoff §0.5, FOUNDRY building.
- `GSS_PATCHES_FIX_TWENTY_THREE_UNLABELLED` — 23 GSS Harmony patches have no [PatchFeature]; NEXT: tag each with its Mod Settings feature (every-mod-ships-settings rule).
- `ALT_GRAPHICS_FIX_SIX_SECOND_FACES` (FOUNDRY) — 6 creatures' alternate pictures were never ruled on, and the art tracker can't see alternates; NEXT: make artpipe read alternateGraphics, then put the 72 files on a pick sheet.
- `FLYER_NORTH_REDRAW_WINGS_LEFT_AT_HOME` — RM/RUT_FleetFlier north wingless, RM_Murrelith placeholder; NEXT: redraw in the flyer effort (FLYER_STABLE_BODY_GATE_1).
- `REVIEW_SAVE_RELEASE_PENS` — pen animals hold a 60000-tick Wait and can't be released by bridge; NEXT: add a companion tool that ends the Wait job on pen animals so he can watch them move.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Ledger notes with owner provenance land in OWNER.jsonl, not BENCH.jsonl (filed: LESSONS)
- Approved art never reached the game: an alternateGraphics slot the art tracker can't see (Gizka, 7 approvals); guard selftest_drawn_art_ruled.py (filed: LESSONS by the Gizka agent)
- dnfile misparses a DLL with exactly 2048 MemberRef rows (coded-index sizing); patched in lint_harmony_targets.py f9fe51aff8 (see: that commit)
- Serial art agents are slow; split per subject (filed: LESSONS)
- A projectile column in a body row made a pick ambiguous (filed: LESSONS)
- Review-save Wait jobs can't be released for wild animals (filed: LESSONS)

## Closed since the last handoff (3)

- `POND_ELEVATION_BUILD_LAKES_RUN_DEEP` — 536e6c3d0165dac531808fb71f95a5c04fcc106e
- `FUEL_MOAT_VERIFY_LIGHT_THE_GASOLINE` — 2024fb4890c1ee15603219fbf1caaccf17128ebc
- `RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP` — 682da5d82c

## Filed and still open (4) — the next seat's queue

- `BIOME_SPRINT_PROVE_SCRUB_SETS_PACE` — Next sprint: Cauldron, Contagion and LeaningScrub fully to done (art + mechanics + 0-fail/0-unmeasured suites on saved test maps), per-biome criteria 
- `GSS_PATCHES_FIX_TWENTY_THREE_UNLABELLED` — GSS: 23 Harmony patch classes have no [PatchFeature], so no Mod Settings toggle governs them (lint_harmony_targets NO_FEATURE, visible since the dnfil
- `ALT_GRAPHICS_FIX_SIX_SECOND_FACES` — Alternate pictures (alternateGraphics) never ruled on for Eopie, Falumpaset, KowakianMonkeyLizard, Hssiss, Worrt, Gembug (72 files, known-issues list 
- `FLYER_NORTH_REDRAW_WINGS_LEFT_AT_HOME` — Flyer idle north facings that hide the wings (FleetFlier x2) and Murrelith placeholder

## Commits

```
332a660f59 Owner approves the whole Pyrelands review save; grass saturation closed
3791e139ea Facing-scale lint + PW10 gate; Pyrelands rescales (FireWasp, Anooba male, Furnace beast S/N) by owner's words; roster item filed
85ae916777 Twin-only ports: rupture spawns RM_BloodyMess, lesser oomb art filed, owner home questions
39e2b5c339 Phase 0 P3 Q3: three Forge candidates for the anole slot (jobbosh, dhoggur, jurrox), first renders filed
f690b6984e Scorchpod carries the red spore's acid death burst, repointed to our EnvironmentalHazards class
3021d70315 Phase 0 twin-only ports: wuum, oomb and lesser oomb as our own RM_ defs in the Gelatinous Slime
58595b22e2 Zhool haze rebuilt in our code: red fleck haze; plants in it turn into the Contagion's ocular-forest flora
aabcd7a5a2 Phase 0 P3 Q4: keep the ondrukka as our own RM_Ondrukka (no cocoon), Miasma row repointed, picked art installed
4da6137888 Port Blood Shrimp (RM_Zrrik) and Sharpshrimp (RM_Sharpshrimp), repoint Greentide/Miasma rows, drop the Skorra Greentide row; file Sharpshrimp art
ed98c49856 Cut the Skorra (needlepost): delete RM_Skorra def (owner, by card 2026-10-15); its Greentide row goes with the shrimp repoint
4aed7e6f25 Pyrelands review save rebuilt from HEAD deploy: RM_pyre_review_20261015_r2 (37/37 stations, 44 signs)
ee7a3d4a53 Biome review save standard v1.1: owner rulings on Q1-Q5 (free layout, pen counts 4-8, DO-line action, paused-only)
49d28e10c7 Ledger: review save standard, defects to one pick sheet before walk
de1a238695 SWAC Phase 0 Q1: file artpipe renders for the sarlacc pit, dead-sarlacc husk and sarlacci spore
15414fe38c SWAC Phase 0 Q1: port both Sarlacc landmarks to RSW_ defs; repoint Gaping Doom, ring, sign and icons
9e53c3e455 Ledger: owner rulings on the biome review save standard v1
59c2718b0a Lastvine rearing: per-node scan cache (no shared dictionaries off the main thread); mutant skin colour on the reared graphic
98f7b45060 Phase 0 P3: owner questions for the Alpha Animals code-rider creatures
036740fa77 Biome review save standard v1 (owner: define a standard savegame for the biomes); kickoff packet points at it
419d5e70bf Phase 0 P3: port greater bulloo and lastvine off Alpha Animals code; lastvine rears up in our own render node
... 112 more: git log --oneline 536e6c3d01..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-16T03:51:01Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/bench_live_20261015_l2/SITTING.md   ours: this session's live round notes (committing)
 M Transient/biome_ffar/scale_ground_measured.json   ours: generated by tonight's pick-sheet build (committing)
 M Transient/mc_human_review/KEYSHEET.md   not ours: predates this session (left untouched)
 M Transient/mc_human_review/keysheet.html   not ours: predates this session (left untouched)
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   not ours: predates this session (left untouched)
 M conversations/2026-10-12-1403-b0ee9afc.md   not ours: predates this session (left untouched)
 M conversations/2026-10-13-0007-b342a8ee.md   not ours: predates this session (left untouched)
 M conversations/2026-10-14-0337-c7981846.md   ours: this session's conversation record (committing)
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

