# BENCH_REBOOT_HANDOFF_202610180544 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610180037`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Order (owner, 2026-10-17 ~22:30 PDT): "I can't help tonight. I'll see you in the morning. Do what you can until then." — ends when he next writes. Credited FlowWorks live reruns cannot land while FOUNDRY pushes FlowWorks (it did so at 22:33 and 22:39 mid-run again tonight); salt rows T5/T11/T12/T17 PASS at edb4b72b49 are the real evidence meanwhile.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Everything from the previous handoff's owner list still stands (walk saves, rulings by card, 36 provisional art installs mis-recorded as KEEPs).
- New: RUT_Cauldron world texture `Biomes/PoisonForest` is a dead pre-rename path; proposed one-line fix `World/Biomes/Jawa_HorrorWastes` (cosmetic, needs his OK) — note on RONTO_PACK_TEXTURE_REPAIR_SADDLEBAGS_MISSING.
- Overnight closes: RIVERCOLORS_MERGE, TRIBES_LOOKUP_DIAGNOSE_FIRST_ONE_FALLS, GSS_PATCHES_FIX_TWENTY_THREE_UNLABELLED (live PASS, all-off/all-on), RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID (live raid_arrived PASS).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `THIRST_RULES_BUILD_SALT_OFF_THE_MENU` — salt rows PASS live at edb4b72b49, not credited (FOUNDRY pushed DLL 26a47408f7 mid-run); NEXT: in a FlowWorks-quiet window deploy HEAD, run thirst_live.py + sprinkler_live.py, then `modcheck run FlowWorks`.
- `THIRST_ROWS_DIAGNOSE_SLIME_SITS_STILL` — filed for FOUNDRY: T27/T15/T16 FAIL twice, pawn wanders; NEXT: FOUNDRY diagnoses from Transient/bench_live_20261018/.
- `THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT` — all ruled; NEXT: close once the build item is credited.
- `TREE_BURST_BUILD_LITRES_BUY_YEARS` — NEXT: card the owner on the 6 unlisted 3.0–3.9 plants.
- `DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER` — NEXT: owner picks the 12 canon JFO renders.
- `TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE` — NEXT: ask owner permission for real tank art.
- `INSITU_ART_JUDGE_SAVES_KEPT_WARM` — NEXT: walk the RM_walk_20261017_* saves with the owner and enact his verdicts.
- `TITANOSLIME_SLIME_BIOME_1` — gates 1–6,8 PASS; NEXT: owner judges gate 7 sheet Transient/afk_2026-10-17/titano_g7/g7_sheet.jpg, then close.
- `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING` — NEXT: put Q1–Q9 to the owner as cards.
- `CANAL_COVER_DESIGN_WET_FOXHOLE` — NEXT: put Q1–Q8 to the owner as cards (Q1 first).
- `ARTPIPE_FACING_COHERENCE_1` — NEXT: owner looks at one regenerated set in game, then close.
- `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED` — NEXT: owner judges nozzles on RM_walk_20261017_sprinklers.
- `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` — NEXT: owner judges thin water on RM_walk_20261017_thinwater.
- `RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS` — NEXT: owner judges weirs on RM_walk_20261017_weirs.
- `VENOMVINE_BUILD_SCRUB_GROWS_TEETH` — NEXT: owner judges on RM_walk_20261017_venomvine.
- `RONTO_PACK_TEXTURE_REPAIR_SADDLEBAGS_MISSING` — Ronto PNGs exist; NEXT: owner OKs the Cauldron texture fix, then apply and close.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- run_selftests.py --only rejects a bare file name (selftest_detectors); run the file directly or look up the registered name (see: Transient/bench_live_20261018/)
- modcheck governor stops on hostile_arrival before the detector sweep, so a fired raid records no raid_arrived unless swept immediately (see: RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID ledger note)

## Closed since the last handoff (4)

- `RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW` — 0e472b3fc2
- `TRIBES_LOOKUP_DIAGNOSE_FIRST_ONE_FALLS` — 902f562a87
- `GSS_PATCHES_FIX_TWENTY_THREE_UNLABELLED` — 52a6a44d20ff
- `RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID` — f18737e762e7

## Filed and still open (1) — the next seat's queue

- `THIRST_ROWS_DIAGNOSE_SLIME_SITS_STILL` — thirst_live T27 water_items, T15 slime_effects, T16 living_slime FAIL in two consecutive runs at FlowWorks edb4b72b49 (pawn only wanders); salt rows p

## Commits

```
bde6e29f89 ledger: BENCH close GSS_PATCHES_FIX_TWENTY_THREE_UNLABELLED and RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID on live PASS
dc3068ebc1 GSS settings round + raid detector live evidence (bench_live_20261018)
ea44bf7957 FlowWorks core review: dig scan materialised, pump-circle hose guard, FluidDef very-shallow check, swept-away letter pronoun, proof reset bound
0c6222a809 ledger: BENCH file THIRST_ROWS_DIAGNOSE_SLIME_SITS_STILL for FOUNDRY
d9bf435d78 THIRST_RULES_BUILD_SALT_OFF_THE_MENU: uncredited rerun, FlowWorks moved mid-run
26a47408f7 FlowWorks review misc: 9 files CLEAN, PipeStyles doc fix
b86c249755 ledger: BENCH notes on RAID_DETECTOR flood selftest and Cauldron texture
ca292442fa Hose review night: 3 files marked CLEAN, no code changes
c9c691cb11 ledger: BENCH close TRIBES_LOOKUP_DIAGNOSE_FIRST_ONE_FALLS
edb4b72b49 code_review: titanoslime_gates.py CLEAN
ae666dda72 titanoslime_gates: sheds-off row can no longer pass blind; g7 checks screenshots; g3 cleans up on no-swallow
5deb813aee ledger: BENCH close RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW
54f5c85bfb FOUNDRY handoff 2026-10-18: FlowWorks rebuild live-proven, rulings and looks owed
01f4201569 water art candidates: commit the sheet images
d219a67c2d ledger: FOUNDRY bridge take/release, live day 5
299f54ecfb ledger: FOUNDRY live day 5 verifies
5360cda86e Live day 5 on DLL 487e9161d: v2 calm2 61/0/0, prisoner sweep returns and stays, S5 12/1 (S5.i only vs whole-notch doc)
a3ab75fd5a prisoner return log: published
487e9161db FlowWorks DLL: prisoner return fix
0bf02772af Returned prisoner comes back to a cell that holds it, not an edge cell
... 16 more: git log --oneline 7f4d872d02..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-18T05:44:00Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/census.json   not ours / pre-existing or another agent's derived output: left untouched
 M Transient/biome_ffar/census.md   not ours / pre-existing or another agent's derived output: left untouched
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

