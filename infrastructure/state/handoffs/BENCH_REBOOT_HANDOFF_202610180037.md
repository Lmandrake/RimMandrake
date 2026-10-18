# BENCH_REBOOT_HANDOFF_202610180037 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610170737`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Results credited by FlowWorks `validation.py` are bound to the exact mod hash + deployed DLL, and FOUNDRY pushes FlowWorks several times an hour — a ~25 min live rerun was invalidated twice today by commits landing mid-run. Don't chase credit while FOUNDRY is active in FlowWorks; run the credited rerun (`thirst_live.py` + `sprinkler_live.py`, then `modcheck run FlowWorks`) in a quiet window, and treat PASS-at-an-older-hash (8b8aa4a2, today) as real evidence meanwhile.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Order still standing from the owner's AFK (2026-10-17 10:54 PDT): live work allowed when the bridge is free; art installs provisional for in-game judging; NO phone messages. Ends when he next writes.
- In-game walk is staged: keeper saves `RM_walk_20261017_{sprinklers,thinwater,weirs,venomvine,creatures}`; guide `Transient/review_walk_2026-10-17/WALK_GUIDE.md` (item `INSITU_ART_JUDGE_SAVES_KEPT_WARM`). Thin-water art reads very faint in game; adult taozin crowds the line-up.
- 36 provisional art installs were recorded in the art ledger as owner KEEPS (helper misused --owner-said) — his in-game rejections must still purge them (see `INSITU_ART_JUDGE_SAVES_KEPT_WARM` note; Transient/afk_2026-10-17/art_installs.md).
- Picks owed: 12 canon Fallen Order dragonsnake renders refused (slots owner-kept); Lothcat_f east refused (his pick C); TeeMuss N/S + Yobshrimp redraws installed provisionally.
- Rulings owed by card: tree-burst — 6 plants 3.0–3.9 not in his table now burst with 10 logs (GlowGlobe, KeeningCordax, Maddrick, Phorrik, Thulvane; DulcisPlant treated as fungus); canal-cover Q1–Q8 (Q1: LAW 2 says cover-from-below is cut — needs an exception) in design/RimMandrake/canal_cover_design_2026-10-17.md; bridges Q1–Q9 in design/RimMandrake/flowworks_bridges_design_2026-10-17.md; taozin tank art (stand-in barrel; cosmetic needs permission); titanoslime art (gate 7, Transient/afk_2026-10-17/titano_g7/g7_sheet.jpg); BIOME_SPECIFIC_FAUNA_LAW_1 droppable if he agrees.
- Calls made without him (veto-able): thirst — tank set to Fill counts as order for brine; green slime "full exposure" = 5 doses; ice melts via stove bill; all numbers first guesses. Taozin tank 2 days/jar, 15 days to white. Dragonsnake albino = rare variant on Greentide (0.02). Sweetline numbers he accepted.
- StarWarsPatches was dropped from the walk list (332 errors without his full list); the last modcheck run wrote his 548-mod list into ModsConfig before BENCH restored the 22-mod walk list.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `THIRST_RULES_BUILD_SALT_OFF_THE_MENU` — built, live PASS credited at FlowWorks 8b8aa4a2 only; NEXT: when FOUNDRY is quiet in FlowWorks, deploy HEAD and rerun thirst_live.py + sprinkler_live.py, then `modcheck run FlowWorks`.
- `THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT` — all owner questions ruled; NEXT: close it once the build item's live rows are credited.
- `TREE_BURST_BUILD_LITRES_BUY_YEARS` — built, live probes PASS (75 rows); NEXT: put the 6 unlisted 3.0–3.9 plants to the owner as a card.
- `DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER` — built, live PASS, albino art installed; NEXT: owner picks the 12 canon JFO renders (slots owner-kept).
- `TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE` — built, live PASS; NEXT: ask owner permission for real tank art (stand-in barrel).
- `INSITU_ART_JUDGE_SAVES_KEPT_WARM` — saves staged; NEXT: walk them with the owner and enact his verdicts (purge rejects despite keep marks).
- `TITANOSLIME_SLIME_BIOME_1` — gates 1–6 + g8 PASS; NEXT: owner judges gate 7 art from Transient/afk_2026-10-17/titano_g7/g7_sheet.jpg, then close.
- `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING` — design drafted; NEXT: put Q1–Q9 to the owner as cards, then file the stage items.
- `CANAL_COVER_DESIGN_WET_FOXHOLE` — design drafted; NEXT: put Q1–Q8 to the owner as cards (Q1 first: LAW 2 exception).
- `ARTPIPE_FACING_COHERENCE_1` — remainder is owner eyes only; NEXT: owner looks at one regenerated set in game (N back, S front), then close.
- `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED` — 9/9 live rows PASS; NEXT: owner judges nozzle looks on RM_walk_20261017_sprinklers.
- `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` — L8 PASS; NEXT: owner judges thin water on RM_walk_20261017_thinwater (reads faint).
- `RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS` — weir rows PASS, 28 hose/river jobs queued/partly installed; NEXT: owner judges weirs on RM_walk_20261017_weirs.
- `VENOMVINE_BUILD_SCRUB_GROWS_TEETH` — islands 5/5 PASS, 47 tall renders installed; NEXT: owner judges on RM_walk_20261017_venomvine (old _d renders still mix in).
- `RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW` — deployed, planet colours PASS by eye; NEXT: close it with that evidence.
- `TITANOSLIME_GATES_SCRIPT` (no item) — titanoslime_gates.py never full-file reviewed; NEXT: review and mark-clean it.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- art.py install has no --by-card; --owner-said with card text records a KEEP (filed: lessons)
- enact variant letters clobber earlier V_ picks (filed: lessons)
- DEPLOY_HOLD.txt paths must be mod-relative (SWBestiary/...), not src-relative — a wrong path holds nothing (filed: lessons)
- PatchOperationFindMod matches the mod's display NAME, not packageId — 20 animals silently missing from Greentide (filed: lessons)
- static no-search marks keyed by pawn id survive save reload (thirst + snow) (filed: lessons)
- FlowWorks csproj does not glob new .cs files — new code can build into nothing (filed: lessons)
- Large Pawns registers multi-cell occupancy at spawn size; a later size change leaves ghost cells (see: items/closed/TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID.md)
- Verse log caps at 10,000 messages; a clean log budget can be a dead log (filed: lessons)
- modcheck run on exit rewrites ModsConfig to the owner full list, even after a crash (filed: lessons)
- Steam may ignore the first launch request (filed: lessons)

## Closed since the last handoff (1)

- `TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID` — 5f3da64927

## Filed and still open (11) — the next seat's queue

- `THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT` — 3x3 deep design pass: thirst, every fluid type, gathering/storage/access, health, jobs, crop watering, machine loading, bottle/bucket/barrel/pipe/hose
- `TREE_BURST_DESIGN_SWEETLINE_TAKES_ITS_TIME` — Explosive growth for tree-sized plants: water advances a tree a bit along a long life; a full burst yields logs, sprouts, fruit; grass never makes woo
- `TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO` — Taozin split: adult RSW_Taozin + RSW_TaozinGrub, nest, brine, art
- `TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE` — Taozin grub brine tank (C#): grub kept in brine makes RSW_TaozinBrine from RM_Brine; long-brined grub switches to its white look; nest Mod Settings sw
- `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` — Owner: approve scene S5 redrawn a third time with exactly-level numbers (plan P10; one surface per body, litres to the decilitre), after the epic's in
- `DEPTH_DEFAULTS_ASK_ELEVEN_VETOES` — One question card: keep or veto the rebuild's defaulted choices, V1-V8 of the plan (dig cost curve, drowning over the head, fall by metres, spikes on 
- `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST` — The rebuild's unasked cards, raiders first: raiders facing a trench they cannot cross (play Q7: scaling ladders, a perfect moat, or they leave); a big
- `FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING` — Owner re-validates the FlowWorks north-star section in one sitting: the new bar still_water_one_surface_height (R9) plus fill_tier_legible and depth_a
- `INSITU_ART_JUDGE_SAVES_KEPT_WARM` — Joint in-game walk on staged keeper saves: sprinkler heads (4 looks), thin-water pond, joined weirs (4 looks), tall venomvine, facings picks incl. Tee
- `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING` — Bridges in the FlowWorks redesign: generalized over water or non-water spans, grated bridges that let fire rise through, and bridges at non-surface al
- `CANAL_COVER_DESIGN_WET_FOXHOLE` — Consider a pawn standing in a shallow canal as standing in a trench, with cover implications

## Commits

```
0416402102 ledger: BENCH close TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID (item prose moved to closed/)
8ea0bc9dcf Titanoslime gate g8 PASS live: vanish leaves no ghost; gates back to vanish cleanup
37a292b621 FOUNDRY handoff 2026-10-18: FlowWorks one-big-rebuild built offline, live proof owed (bridge held by BENCH)
e687cd557c ledger: FOUNDRY shard events
89412268ac code review: RM_LiquidStock.cs and 21 FlowWorks SelfTest files CLEAN at 71aaadd97; review day 3 log
71aaadd97e FlowWorks DLL rebuilt on 646a91a38 (review day 3)
646a91a382 FlowWorks SelfTest: stale 5:1 comments and a misplaced case comment
3994081539 FlowWorks SelfTest review: two can't-fail screen checks, an unbound migration case, dL movers in caller coverage, a fuzz past 2 m
e5f647564f FlowWorks review day 3: whole-level pour all-or-nothing; head fraction live with drowning off; stale settings text
8c6cb8111a lesson: re-register a pawn around a BodySize change under Large Pawns
c237719449 code review: Titanoslime.cs, TitanoslimeProof.cs CLEAN at 46de5ee79b
46de5ee79b Titanoslime vanish ghost: re-register around stage locks (Large Pawns sizes the square at registration)
6528f2ca3a TITANOSLIME_SLIME_BIOME_1: spec 8 gates 1-6 PASS live; gate 7 art awaits owner
7986cc51e9 code review: 15 FlowWorks files CLEAN at 93eb2695a; review day 2 log
93eb2695a1 FlowWorks DLL rebuilt on 5774e06a6 (review day 2: ledger dL, refill dL, shallow-drowning switch)
5774e06a64 review day 2 log
6dc5f36ab6 FlowWorks review day 2: L0 ledger counts decilitres + limitless input; refill stays in dL; stale absolute-rule settings text
2dc962d6d2 review day 2 log
7b7401a3ca FlowWorks swim: shallowWaterDrowningEnabled switches wadeable natural-water drowning off alone (shipped on)
336c92dde8 vv_shipped_matrix: stage the other-mod files Thirst_slime_last_resort_ruled reads
... 199 more: git log --oneline 9d73c59929..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-18T00:36:58Z

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
 M Transient/modcheck/fixtures.json   modcheck run output (BENCH live round 2), derived; left untouched
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   not ours / pre-existing or another agent's derived output: left untouched
 M conversations/2026-10-12-1403-b0ee9afc.md   conversation records: the hourly sweep commits them
 M conversations/2026-10-13-0007-b342a8ee.md   conversation records: the hourly sweep commits them
 M deployed/config/ModsConfig.before-tier-bridge.xml   not ours / pre-existing or another agent's derived output: left untouched
 M infrastructure/state/ledger/events/OWNER.jsonl   BENCH game events — committed in cf0ee537f7
 M src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md   not ours / pre-existing or another agent's derived output: left untouched
 M src/RimMandrake/FlowWorks/northstar/review/map/keysheet.html   not ours / pre-existing or another agent's derived output: left untouched
 M src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPawnKitTools.cs   another agent's uncommitted doc-string change (one line, no behaviour); left untouched
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

