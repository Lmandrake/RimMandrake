# BENCH_REBOOT_HANDOFF_202610181718 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610180544`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Look at any review sheet yourself (render what it displays, Read the PNG) before offering it: today two sheets went to the owner wrong — the dragonsnake sheet resolved art from a stale def dump (stand-in x4 + white albino swim art, real renders unshown) and the tree-art sheet showed a rejected grub-tank render as Thulvane's in-game art. Both rebuilt and verified (filed: lessons).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Open sheets waiting for his picks: dragonsnake variants http://localhost:44669/?t=vD2eSexEV9qQ_Ab2qn9Nsw (Transient/biome_ffar/dragonsnake_canon_variants_sheet_2026-10-18.html); tree art picks http://localhost:39367/?t=J2BObfLmSc4_xYRral5_GQ (Transient/biome_ffar/tree_art_picks_sheet_2026-10-18.html). Servers die with the session; rebuild/serve via serve_gated.py if gone.
- Veto-able: the tree-defs helper applied "NO HYDROCARBON LIFE FEATURES THE BURSTING MECHANISMS" to Thalquith AND the Chill's 9 propane-floor plants (one roster block to revert). GiantFibreStalk stays a tree though its description now calls it half fungus.
- Five rejected tree pictures cannot be purged (kept/in-game): CrackedThornwood's TwistingThornwood_a, Tumbel x3, Zhorrel_a_a; Veluthar's retired AB_JungleTreeA. Cracked and Twisting thornwood still share one picture via his D pick.
- Regression for FOUNDRY: SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING (salt bottle no effect, sprinkler T22 FAIL at ea44bf7957).
- Deploys owed: RimMandrake.Biomes (tree defs, world-map textures; plan carries ~60 files of others' work and the mod is not in the live list) and SWBestiary (dragonsnake fix; plan carries another seat's uncommitted RSW_DonorPack_P1_Plants.xml).
- Owner rulings today: tree tiers Small 3-5/Big 5-8/Giant 8-12/Titanic 12-30+; zoom-only art scales to its zoom (canopy 32 px/cell, in generating-rimworld-sprites SKILL.md); dragonsnake = 4 JFO variants, albino = white art; placeholder world textures for all biomes; brine tank art yes; fauna-law item dropped.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER` — 4 JFO variant renders on a pick sheet, stand-ins installed, 12 swim jobs pending in _artpipe; NEXT: enact his picks with `art.py enact` on dragonsnake_canon_variants_sheet_2026-10-18, then sheet the swim renders.
- `TREE_TIERS_JUDGE_FORTY_FOUR_TRUNKS` — def half enacted 9a8fc0edfb, 20 new renders on the picks sheet; NEXT: enact his picks on tree_art_picks_sheet_2026-10-18 (Veluthar's variant goes into RM_Veluthar_a/), then deploy RimMandrake.Biomes.
- `CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD` — filed for FOUNDRY, ruled option A + 32 px/cell; NEXT: FOUNDRY builds after tier picks settle which trees are Titanic (Sweetline only so far).
- `BIOME_WORLDTEX_BUILD_EVERY_BIOME_A_FACE` — 62 defs repointed, 36 textures installed, sheet Transient/biome_worldtex_2026-10-18/sheet.png; NEXT: deploy RimMandrake.Biomes once its plan is clean of other seats' files.
- `TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE` — tank art installed+deployed (provisional); NEXT: owner judges it in game on the walk.
- `THIRST_RULES_BUILD_SALT_OFF_THE_MENU` — uncredited; salt regressed at ea44bf7957; NEXT: after FOUNDRY fixes SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING, rerun thirst_live.py with --only splits (helpers die at 600 s) + sprinkler_live.py, then `modcheck run FlowWorks`.
- `THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT` — NEXT: close once the build item is credited.
- `INSITU_ART_JUDGE_SAVES_KEPT_WARM` — walk saves staged + titanoslime added; NEXT: walk with the owner and enact verdicts (purge rejects among the 36 mis-recorded KEEPs).
- `TITANOSLIME_SLIME_BIOME_1` — gate 7 moves to the walk; NEXT: stage a titanoslime stage 1 + 5 on a walk save, owner judges, close.
- `RONTO_PACK_TEXTURE_REPAIR_SADDLEBAGS_MISSING` — Cauldron texture covered by the world-texture item; NEXT: close once RimMandrake.Biomes deploys with the new Cauldron texture.
- `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING` — NEXT: put Q1-Q9 to the owner as cards.
- `CANAL_COVER_DESIGN_WET_FOXHOLE` — NEXT: put Q1-Q8 to the owner as cards (Q1 first).
- `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED` / `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` / `RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS` / `VENOMVINE_BUILD_SCRUB_GROWS_TEETH` / `ARTPIPE_FACING_COHERENCE_1` — NEXT: judged on the in-game walk (INSITU_ART_JUDGE_SAVES_KEPT_WARM).
- `ART_SHEET_REVIEW` (no item) — art_sheet.py gained --question and --hide-sets today; NEXT: full-file review and `code_review_status.py mark-clean`.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- WSL root disk filled from never-cleaned ~/.seat-tmp scratch clones; FOUNDRY's ~175 GB still there (filed: lessons)
- review sheets built from a stale def dump show the wrong art; look before offering (filed: lessons)
- foreground helpers die at 600 s: full thirst_live / modcheck runs cannot finish inside one helper (see: THIRST_RULES_BUILD_SALT_OFF_THE_MENU ledger note)
- art.py install refuses a free-text reason; only artpipe-collect / script:<path> without an owner decision (see: TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE note)

## Closed since the last handoff (2)

- `TREE_SIZE_ASK_GIANTS_WANTED` — 21febb1008
- `CANOPY_ZOOM_DIAGNOSE_SEE_THE_FOREST` — a9ef6975ad

## Filed and still open (3) — the next seat's queue

- `BIOME_WORLDTEX_BUILD_EVERY_BIOME_A_FACE` — Placeholder world-map textures for ALL our biomes: read each description, make each distinct in colour and texture, install; owner reviews in parallel
- `TREE_TIERS_JUDGE_FORTY_FOUR_TRUNKS` — One review sitting: owner places each of our 44 trees in Small 3-5 / Big 5-8 / Giant 8-12 / Titanic 12-30+ (Titanic shown only as solid trunk), prefil
- `SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING` — Regression at FlowWorks ea44bf7957: thirst_live T5 salt bottle consumed with no hydration and no poisoning (PASS at edb4b72b49 last night); sprinkler_

## Commits

```
76e72b9156 Tree art picks sheet: only plants matching their rows; art_sheet --hide-sets (no purge)
b551136cdd ledger: tree-tier def half enacted note
9a8fc0edfb Tree tiers sheet enacted: sizes, not-trees, random pools, Thalquith to the Chill floor, TreeMartyr cut
afffe8db6f Tree art new-renders review sheet (picks blank) + Thulvane refile job
37b730b5de ledger: dragonsnake sheet fix note
95451f92e7 Dragonsnake: no white swim art on canon; canon variants sheet rebuilt from artpipe renders
dd68458cd6 FOUNDRY handoff 2026-10-18: owner rulings recorded, build items filed
e600c0f05f ledger: owner card V8 readout kept
2759d3c42d ledger: owner cards 2026-10-18 (D4, dug fish, no beach ring)
67a345f3e3 lesson: look at a review sheet before offering it
38b2356903 Tree art jobs for TREE_TIERS_JUDGE_FORTY_FOUR_TRUNKS (20 jobs, owner tree-tier notes)
231b7a7de7 ledger: tree-tier sheet enactment ordered; Dulloth canopy note carried
3a4812fddc Dragonsnake canon variants review sheet (4 JFO renders, no picks); ledger note
d9ecc13128 BIG_CREATURES_DESIGN_WALLS_AND_SLOTS: walls/slots/roofs design pass + GPT review
28f403aedb Dragonsnake: canon art off the white serpent; four JFO variants via alternateGraphics RSW_Dragonsnake now draws DragonsnakeCanon/Dragonsnake_A..D (stand-in render dragonsnake_jfo_v1 in all four until jobs dragonsnake_jfo_var{a..d}_v1 install); the white art stays only on RSW_DragonsnakeAlbino. Donor fold repointed too.
95a624b187 ledger: dragonsnake split clarified by owner
ae88df220c ledger: owner cards 2026-10-18 (big creatures, rescue access, alert, spikes)
279d1b4055 Dragonsnake JFO pick sheet (6 owner-kept slots), no picks
b72a4cb5b1 ledger: file SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING (thirst/sprinkler regression at ea44bf7957) for FOUNDRY; ModsConfig restored to the 11-mod list
fa441daef9 ledger: owner cards 2026-10-18 (dig cost, falls, shooting, raiders)
... 15 more: git log --oneline f738509c79..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-18T15:44:02Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/census.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/census.md   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/dragonsnake_jfo_pick_sheet_2026-10-18.decisions.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/liquid_containers_four_styles_sheet_2026-10-16.decisions.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/scale_ground_measured.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/facing_regen_batch_2026-10-16/events.jsonl   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/fw_review_map_verify.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/mc_human_review/KEYSHEET.md   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/mc_human_review/keysheet.html   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/modcheck/fixtures.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   not ours / pre-existing or another agent's derived output: left untouched
 M conversations/2026-10-12-1403-b0ee9afc.md   conversation records: the hourly sweep commits them
 M conversations/2026-10-13-0007-b342a8ee.md   conversation records: the hourly sweep commits them
 M deployed/config/ModsConfig.before-tier-bridge.xml   not ours / pre-existing or another agent's derived output: left untouched
 M infrastructure/state/art/events/BENCH.jsonl   not ours / pre-existing or another agent's derived output: left untouched
 M src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md   not ours / pre-existing or another agent's derived output: left untouched
 M src/RimMandrake/FlowWorks/northstar/review/map/keysheet.html   not ours / pre-existing or another agent's derived output: left untouched
 M src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnKitTools.cs   not ours / pre-existing or another agent's derived output: left untouched
?? conversations/2026-10-02-1217-54206aec.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-02-1952-4b4a687b.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-02-2332-d58606e4.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-03-1458-7ed5ddfd.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-04-2105-400ef7dc.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-04-2219-962263b0.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-05-1426-fab8a134.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-06-0601-5ab77072.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-06-1305-ecebcb6f.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0058-b305fb53.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0059-c857706d.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0120-033b16fc.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-0547-d6861da6.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-07-1520-6a6f7a30.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0001-cc216258.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0158-8aeef5fc.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0215-c4ae9260.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-0217-3acaea39.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1348-bac7589f.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1411-2294fe53.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1411-3ffd55d0.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1413-52caf5c0.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1413-658e0588.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1414-b4b8553c.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-08-1428-de9591de.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-09-0450-85e0a0f9.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-09-1308-818639f9.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-0040-5e2fd376.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-0049-58eabd09.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-0440-c71b568d.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-1341-91d07ad1.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-10-2102-71d8c9eb.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-0052-2f152d1c.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-1934-f086ce1a.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-1953-24347684.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-11-2000-edefebc8.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-12-0625-88710e84.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-13-1146-7444c21a.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-15-1939-5e86e9cb.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-16-0628-abd280e4.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-16-1824-05355635.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-17-0128-782256d7.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-17-1422-0fdd99bf.md   conversation records: the hourly sweep commits them
?? conversations/2026-10-18-0524-52bb863f.md   conversation records: the hourly sweep commits them
?? deployed/config/ModsConfig.before-gss-restore-20261010.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-flowworks.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-flowworks_vepipe.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.before-tier-ratchet_pilot.xml   not ours / pre-existing or another agent's derived output: left untouched
?? deployed/config/ModsConfig.swap-active.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/out/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/guides/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/out/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_north.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_south.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runA.out   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runB.out   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runC.out   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/gen.out   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Futuristic/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Industrial/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Modern/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_east.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_north.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_south.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_west.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Scrapper/   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Futuristic.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Industrial.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Modern.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Scrapper.png   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_cap.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_spill.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_upstream.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_v_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_cap.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_spill.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_upstream.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_v_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_cap.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_spill.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_upstream.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_v_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_cap.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_spill.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_upstream.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_v_east.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/foam_toe.log   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T125537.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T130318.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T144034.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T161200.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261016T162747.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T034753.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T040637.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T041535.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T042312.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T050823.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/sprinkler_live_result_20261017T155357.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T135834.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T135854.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T135923.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T140243.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T140307.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T140728.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141144.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141624.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141722.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141802.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141913.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T141941.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T142026.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T142323.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T142428.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T142939.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T144343.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T052325.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261016T125532.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GSS   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T220702.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T230453.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230218.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230455.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T230639.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231027.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_flips_20261012T231203.json   not ours / pre-existing or another agent's derived output: left untouched
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   not ours / pre-existing or another agent's derived output: left untouched
```

