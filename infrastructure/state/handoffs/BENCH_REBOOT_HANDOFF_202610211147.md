# BENCH_REBOOT_HANDOFF_202610211147 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610210533`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Order (owner, 2026-10-20 night): "You are to be a light orchestrator. I am going to bed/AFK. You may use one subagent in offline building and design work only. Keep working." — ends when he next writes. Under it, everything below was built OFFLINE and nothing is deployed: FlowWorks (drawbridge proof class + fixes, pipe poles phases 1-7, power cord), GSS (pipe spans, live-wire hook), StarWarsRaces (FA opt-out, first C#), CreatureBehaviors (world sun pin, tether pull refactor), Webwork (web/carpet/webfall), WeepingStones (net), GelatinousSlime (titan prey slider). `OFFLINE_PILE_DEPLOY_ONE_TRIP_FOR_ALL` is now much bigger: whoever next closes the game deploys the pile, then runs the proof scripts — `northstar/drawbridge_proof.py`, `northstar/lines_proof.py`, `titanoslime_gates.py --only g5`, Webwork `web_terrain_weather` rows.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Sag 2% not 3%** for pipe spans (followed his later line-widths card "about a third of GSS wire sag, about 2% of span"); slider.
- **Unruled: deconstructing a drawbridge winch while the leaf is up crashes the leaf** (general winch-loss rule) — alternative is lower-then-release. Ledger note on DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS.
- **Webwork balance:** each cut web-cable cell yields 1 thrixweave and a map has hundreds; web everywhere means spiders sense colonists constantly. Needs his numbers.
- **Face-art design doc, 6 decisions (D1-D6):** `design/RimStarWars/face_art_reassessment_2026-10-21.md`; mockups pinned in `Transient/face_art_2026-10-21/`. Headline (MEASURED): 91 of 93 heads in use are grey donor-style cartoons, only Mimbanese/Ortolan painted; 54/93 fit the vanilla envelope; chin tolerance 0.06 fails 7/35 vanilla heads (propose 0.08).
- **FA opt-out:** `RSW_MandrakeJawa` and the Gamorrean xenotype left off the list (they wear vanilla heads; adding them changes their look); his FA config still lists the pre-rename Gamorrean.
- **Rind coat insulation 35/35** is a made-up number; may not read as "extreme".
- **Net:** by design a fleeing skarrin escapes every 6-cell throw, so "5 of 5" only holds for a calm animal.
- **06 Q4 (proof JSONs out of git)** never answered — question card owed. Telemetry P5 also skipped the tps→health fold because he turned health_observer off.
- **Story rulings 2026-10-12 propagated** (cfa2f408545c) with open questions in `dungeons_arc_spec.md` §2.9 and fever_wood F4: cost of defying the Cathedral, choice timing, hyperdrive the only way off?, does leaving end the game, specimen choices, sekkulaath sites.
- **KEYSHEET downgrade:** regenerating `review_map_coverage.py` rewrites FlowWorks KEYSHEET stations "works in game" → "built, not yet seen"; left uncommitted every time — someone must judge whether the generator or the old status is right.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `FACE_OPTOUT_REPAIR_ONLY_AT_HOME` — implemented dd394d076b (StarWarsRaces C# skip patch, 69 xenotypes, setting default on), undeployed; NEXT: deploy StarWarsRaces and load with a fresh FA config, confirm no FA eyes/mouth on painted heads, then verify
- `PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE` — implemented (phases 1-7: 37c87f15bb..a852bb422b), offline selftests green, undeployed; NEXT: deploy FlowWorks + GSS, run `northstar/lines_proof.py` on the minimal list and sort every non-PASS row into MOD/SITE/HARNESS
- `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS` — implemented (56f1fbb202, live-wire hook eb10651917), its 2 L2 rows live in lines_proof.py; NEXT: run lines_proof.py rows for the cord after the same deploy, then verify
- `TITANOSLIME_SLIME_BIOME_1` — doing; prey-size slider added dddc50016a, gates script hardened 268367220c; NEXT: deploy GelatinousSlime, run `titanoslime_gates.py --only g5`, then stage stages 1 and 5 on a review save for his gate-7 look
- `WEBWORK_TERRAIN_WEATHER_PASS_1` — doing; web cables, local webs, silk carpet, webfall built 031c866cd0 (stand-in art), undeployed; NEXT: deploy Webwork (in mandrake.rm.biomes), run the web_terrain_weather rows on a quicktest map, then ask him the thrixweave/detection balance numbers
- `WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY` — implemented de4658ad89 (sun pin + stars yearly), selftest_sun_heat 54/54; NEXT: deploy CreatureBehaviors, bridge-read the world sun vector and take two planet screenshots one in-game day apart, then verify

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Queue items marked `ready` can already be built (Titanoslime, world stars, rind coat); search git + src before briefing a build (filed: lessons)
- A sweep's "still owed" claim can be wrong (Cauldron art was installed); check `git log -S` on the named files before trusting it (see: CAULDRON_SOILS note)
- `./publish -F` refuses when the ledger shard is a path; inline -m works (filed: lessons)
- FlowWorks C# selftest outside the build stage needs the recipe; staging lacks textures, so PNG-exists checks belong in WSL tests (filed: lessons)
- `rm-memwatch.service` runs memwatch.py straight from the BENCH clone — an edit there is live within a minute (filed: lessons)
- StarWarsRaces About.xml is generated by gen_races_mod.py; hand edits drift the selftest (filed: lessons)
- FA's skip list lives only in each player's settings file, so it must ship as C# (filed: lessons)
- Webwork is folded into mandrake.rm.biomes; loadAfter on its own packageId is a no-op (filed: lessons)
- Helpers sometimes commit with the Co-Authored-By trailer as the subject (67e9baf3c2, 2533c34501); briefs must demand a real subject line (see: this handoff)

## Closed since the last handoff (6)

- `TANK_TALL_BUILD_TWICE_THE_DRINK` — 19e8ab2abb
- `SCALD_SHEET_REDOS_1` — ae9493dd99
- `QUARANTINE_PURGE_WEEK_1` — 9cafde3ee7
- `AWAY_DASHBOARD_BUILD_1` — 593156f3a5
- `THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT` — bca3f5497a
- `BIOME_WORLDTEX_BUILD_EVERY_BIOME_A_FACE` — ede2336a57

## Filed and still open (1) — the next seat's queue

- `FACE_OPTOUT_REPAIR_ONLY_AT_HOME` — Facial Animation exclusion (68 RSW_ head entries) lives only in the owner's own FA config; on a player's install the anime face draws over every paint

## Commits

```
3a32a2529f conversations: catch-up 2 record(s)
0f8524893e Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com> Claude-Session: https://claude.ai/code/session_018tfAs1dZz6hkrRKynaSovR
b9b53e9243 ledger: DIRTY_CODE_REVIEW_STANDING_LOOP_1 note (HugeThings pass)
5c79409496 HugeThings: WarningTicks clamps hours before the long cast; review marks 6 titan files clean
2a3364b277 code review: titanoslime_gates.py CLEAN after independent full read
268367220c titanoslime gates sweep spawns; Webwork harvest fog timeout UNMEASURED; Joining Water WORLDGEN label
870058d2f2 ledger + lessons: SCRUB_WILDLIFE full-list Scrub map has wildlife; site picker ocean bug fixed 283644b90
94a27aa4f2 Site picker: read waterCovered as the export's 1/0; ocean tiles were taken as land
fcd0d3b144 lesson: a refusal in a built hook needs its mirror in the lost hook
08d8f8563e titanoslime_gates: g3 gearless arm and g4 cut slimes are cleaned up, not leaked
230a4b268b titanoslime_gates: blind shed counts and gearless victims are UNMEASURED, not MOD FAIL
add600a736 Webwork ProofHarvest: refuse a node gone mid-wait; never report a stale yield
2de274da49 Suspension: losing a tower that never held the bridge swings nothing down
1db86ec524 lesson: OWNER ledger note text= is a gloss; only ownerSaid/byCard are verbatim
21011a5c6b ledger: close CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE; notes on breakout and sekkulaath items
cfa2f40854 Propagate 2026-10-12 war lab and sekkulaath rulings into the arc spec and canon.yml
62273510de ledger: game-state stamps (live driver)
b66dec6e1f ledger: bridge released; full 325 list + R3 up
7ca4556654 ledger + lesson: telemetry P5 steps 1,2,4 landed; 3 and 5 skipped with reasons
b4f71797dd tps_record.md: 'was it slow at T' starts at 'telemetry at'
... 129 more: git log --oneline 001360cefa..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-21T11:46:00Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/dragonsnake_swim_variants_sheet_2026-10-18.decisions.json   owner's picks saved by served sheets; OWNER's, enact or commit on his next sheet pass
 M Transient/biome_ffar/facings_regen_picks_sheet_2026-10-18.decisions.json   owner's picks saved by served sheets; OWNER's, enact or commit on his next sheet pass
 M Transient/biome_ffar/flowworks_owner_walk_art_sheet_2026-10-11.decisions.json   owner's picks saved by served sheets; OWNER's, enact or commit on his next sheet pass
 M Transient/biome_ffar/leaningscrub_open_rows_sheet_2026-10-18.decisions.json   owner's picks saved by served sheets; OWNER's, enact or commit on his next sheet pass
 M Transient/biome_ffar/liquid_connections_sheet_2026-10-16.decisions.json   owner's picks saved by served sheets; OWNER's, enact or commit on his next sheet pass
 M Transient/biome_ffar/liquid_containers_four_styles_sheet_2026-10-16.decisions.json   owner's picks saved by served sheets; OWNER's, enact or commit on his next sheet pass
 M Transient/modcheck/fixtures.json   generated by modcheck; leave
 M infrastructure/state/art/sheets/aiwha_wingfirst_sheet_2026-10-15.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/blue_desert_sheet_2026-10-04.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/braskeen_on_e_variation_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/cauldron_sheet_2026-10-04.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/cauldron_soils_sheet_2026-10-20.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/contagion_sheet_2026-10-04.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/dewback_reconcile_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/dhoggur_swollen_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/donor_pack_port_sheet_2026-10-14.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/donor_pack_redraws_sheet_2026-10-14.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/dragonsnake_canon_variants_sheet_2026-10-18.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/dragonsnake_jfo_pick_sheet_2026-10-18.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/dragonsnake_swim_variants_sheet_2026-10-18.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/facing_regen_needs_eyes_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/facings_regen_picks_sheet_2026-10-18.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/facings_stand_tall_pilot_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/firespit_with_zisska_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/fleetflier_alien_sheet_2026-10-15.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/floodedcanyon_sheet_2026-10-05.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/flowworks_owner_walk_art_sheet_2026-10-11.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/flyer_north_redraw_sheet_2026-10-15.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/gale_dust_sheet_2026-10-20.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/gelatinousslime_sheet_2026-10-05.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/greysea_crown_retracted_and_elder_sheet_2026-10-18.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/greysea_sheet_2026-10-05.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/gss_all_art_sheet_2026-10-11.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/gss_owner_walk_art_sheet_2026-10-11.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/hosereel_coupling_sheet_2026-10-15.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/leaningscrub_open_rows_sheet_2026-10-18.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/liquid_connections_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/liquid_containers_four_styles_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/nightsideice_sheet_2026-10-05.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/nonrm_plants_census_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/own_render_keep_sheet_2026-10-11.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/pit_ladder_hung_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/pit_spikes_half_a_man_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/plant_baroque_bases_sheet_2026-10-16.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M infrastructure/state/art/sheets/rustcathedral_sheet_2026-10-05.snapshot.json   generated art-ledger snapshot churn (BENCH art helper, 2026-10-20); regenerable, not committed
 M src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md   regenerated by review_map_coverage.py tonight (BENCH helpers); it downgrades stations "works in game" -> "built, not yet seen" — deliberately NOT committed until judged
 M src/RimMandrake/FlowWorks/northstar/review/map/keysheet.html   regenerated by review_map_coverage.py tonight (BENCH helpers); it downgrades stations "works in game" -> "built, not yet seen" — deliberately NOT committed until judged
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/raw/A_rails_front.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/raw/B_rails_front.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/runA.out   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/runB.out   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/out/   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/guides/   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/out/   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_north.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_south.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runA.out   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runB.out   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runC.out   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/SuspensionLooks/out/   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/gen.out   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Futuristic/   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Industrial/   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Modern/   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_east.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_north.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_south.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_west.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Scrapper/   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Futuristic.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Industrial.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Modern.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Scrapper.png   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_cap.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_spill.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_upstream.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_v_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_cap.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_spill.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_upstream.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_v_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_cap.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_spill.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_upstream.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_v_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_cap.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_spill.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_upstream.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_v_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/foam_toe.log   generated artpipe logs/outputs from earlier art runs (not BENCH tonight); leave
```

