# BENCH_REBOOT_HANDOFF_202610210533 — READ FIRST on wake

Follows `BENCH_HANDOFF_202610191052`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Every BENCH build today is offline-only and UNDEPLOYED. The game was FOUNDRY's all day. The owner ruled by card: *"Next time the game is down"*. So whichever seat next closes the game runs `OFFLINE_PILE_DEPLOY_ONE_TRIP_FOR_ALL`: plan the deploy, `--apply` it, then run the batched live rows owed on each item below. Until that happens, none of today's FlowWorks, Scrub, Cauldron or stars work is in the game, and no live row on it means anything.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Drawbridge art sheet, partly filled:** 27 of 84 renders landed; the rest are queued or failed on 429s. http://localhost:38623/?t=wcfqMASoXac2spP8ySt6tw (`\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\biome_ffar\drawbridge_art_sheet_2026-10-20.html`). Two three-quarter east views are flagged.
- **Hose width:** the code sets the hose at 24-30 px. The owner's spec is about 7 px, half the 30 cm (14 px) pipe, and he approved a redraw. Art alone can't fix it. See `design/RimMandrake/flowworks_line_widths_2026-10-20.md`.
- **160 sheet rows await his picks:** the list is at `D:\ClaudeWork\rimmandrake\scratch\awaiting_pick.txt`. 152 finished renders also need his words before install.
- **Ruled today, all by card:**
  - the 25-biome experience lines (`design/RimMandrake/biome_experiences_2026-10-20.md`), with the Wastes reworded as "no outlet";
  - the FlowWorks bars sitting, 22 answers. The section is still DRAFT and needs his word to validate;
  - the drawbridge, 8 answers plus 5 follow-ups;
  - pipes across pits, 8 answers plus the GPT-review answers;
  - the line widths;
  - GSS: done after one live pass.
- **Warscar and the Wastes are distinct biomes** (deep dive, 2026-10-20).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `CAULDRON_SOILS_BUILD_DIRT_THAT_BREATHES` — owner picked plain B and rich A, installed at Cauldron Terrain/Surfaces/RM_CauldronSoil(Rich) with texturePaths repointed (7cf9993886), undeployed; NEXT: after the deploy, look at an RM_Cauldron map, then close
- `DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS` — phases 1-6a built and pushed (7bc5c14712..58f0307b96), 690 selftests green, nothing live yet; NEXT: write phase 6b, the 11 R13 live rows as northstar drawbridge_proof.py plus the validation rows, run them in mock mode, then implemented
- `FLOWWORKS_ENDLESS_LABEL_WIRE_READOUT_PLAINLY` — implemented (6d89d31519), readout "Endless (about 2 m deep)" by card; NEXT: run live_session B2 endless_live after the deploy, then verify
- `FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT` — implemented (b6bc6dd54e), 13 races tagged from lore (7227381877), owner vets the list later under PIT_TRAVEL_TAGS_VET_LORE_FIRST_GUESS; NEXT: run pit_travel_live state reads after the deploy (never a live flight test)
- `FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE` — implemented; owner corrected it: a hose joins at a side port only, a rigid pipe joins anywhere adjacent and draws under to the centre, corners and tanks included (a6f45e39e5, a75cd10f5b, 7f876380b2); NEXT: run pump_ports_live after the deploy
- `FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE` — implemented (6ec8c609a9), a colonist walks to the ladder (by card); NEXT: run ladder_rails_live after the deploy
- `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL` — implemented (84017204d0..697a56127f), offline fuzz green, off while a pump runs (by card); NEXT: after the deploy, run its two pond live rows plus a timing read on a real map
- `PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO` — implemented (660d437a6b); NEXT: run the live deconstruct-with-occupant row after the deploy
- `PROOF_VERDICTS_REPAIR_SAME_BUG_EVERY_ROUND` — implemented (7295681743..3bd9ee1524); preconditions.py, proof_hose.py, suspension_bridge_proof.py and the Contagion validation/selftest were reviewed clean in later rounds; NEXT: re-run proof_hose and suspension_bridge_proof live after the deploy, then verify
- `SCRUB_WIND_BUILD_LEAN_ON_PURPOSE` — built: lean, Gale dust (pick A installed), calm twins, and a wind heading pointed at the sun (1ec532ea11); NEXT: run the windlean chain on a Leaning Scrub map after the deploy, then the owner looks

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A per-call review loop on proof scripts did not converge, so fix the class structurally (filed: lessons)
- `art.py enact` installs nothing when the live slot is a Core texPath; install to a new path and repoint the def (filed: lessons)
- `--by-card` and `--owner-said` events land in OWNER.jsonl, not the seat shard (filed: lessons)
- The question-card hook needs the question text to end in '?' and the header to be 12 characters or fewer (filed: lessons)
- With Worldbuilder loaded, Alien Worlds resets the planet type to Default on load (see: TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING)

## Closed since the last handoff (5)

- `FLOWWORKS_V2_DIAGNOSE_THREE_NEW_REDS` — 7a0d4309f3
- `VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG` — 7a0d4309f3
- `PIT_COVER_DIAGNOSE_GIVES_WAY_TOO_SOON` — 7a0d4309f3
- `HOSE_REALFLOW_DIAGNOSE_SHORT_POUR_DRY_TANK` — 7a0d4309f3
- `RELOAD_POCKETS_DIAGNOSE_KEPT_NO_RECEIPTS` — 7a0d4309f3

## Filed and still open (10) — the next seat's queue

- `FACE_ART_DESIGN_ALIGNING_EARS_AND_HELMETS` — Re-assess all alien and human face art: design only, no work order
- `WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY` — World view: pin the sun direction for the tidally locked planet so stars, sun disc and planet light stop spinning daily; stars drift once per 60-day y
- `PROOF_VERDICTS_REPAIR_SAME_BUG_EVERY_ROUND` — Proof scripts score site/harness failures as mod FAIL: three fresh reviews (d85e8a410c, 966a0b922f) each found new call sites in proof_hose.py, suspen
- `PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO` — FlowWorks: deconstructing a pit cover drops whoever stands on it, same as destruction (ed99fbee6b covers fire/damage). Ruling: design/RimMandrake/biom
- `DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS` — FlowWorks drawbridges (timber hand-winch, steel powered): bascule + gate leaf + plank art; tips occupants to hinge side; raise either side/lower winch
- `PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE` — Pipe poles: GSS-style supports carrying a thick, stiffer sagging pipe span (same mechanics + art variation as power poles); rigid pipe/conduit cannot 
- `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL` — Connected bodies of water level out slowly through pipes by gravity (extending tanks' slow gravity emptying), owner: 'Let's see if we can do this'. Fe
- `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS` — Flexible power cord def: the only power line allowed on bridge decks (rope incl.) and drawbridge leaves; GSS-restyled PowerConduit stays rigid, poles 
- `LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED` — Pipe, hose and cord width spec judged in game beside a colonist, before any pipe-pole or cord art
- `PIT_TRAVEL_TAGS_VET_LORE_FIRST_GUESS` — Owner reviews the lore-tagged jumpers/floaters list in the animal normalization pass (design/RimMandrake/pit_travel_jumpers_floaters_2026-10-20.md)

## Commits

```
ce9348c126 ledger: note on HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME (widths measured; hose width is code)
1a91814ebe Drawbridge art review sheet (partial: renders still queued after 429 throttling)
02c27d9058 FOUNDRY handoff 2026-10-21: planet look/physics wave, owner order for next session
25c46c85d5 conversations: catch-up 2 record(s)
6684950b5f ledger: labels70, Dune Sea centre, Comb camps closed; sun flare verify item; deploy notes
662386035d conversations: catch-up 2 record(s)
86e16be471 conversations: catch-up 2 record(s)
3378ff783e ledger: owner card 10:16 PM, Rings ship
a6a3a2995f lessons: BENCH 2026-10-20 (review loop, enact vs Core slots, OWNER shard, card hook)
e07d4bb937 ledger: drawbridge phases 4-6a notes
58f0307b96 FlowWorks DLL rebuilt from merged source (drawbridge phase 6a + origin's FlowWorks changes)
9630b2f039 Line widths: measured pipe (on spec, 14.5 px) and hose (24-30 px, set in code)
69290c91cc Drawbridge phase 6a (content): timber/steel drawbridge build buttons, gate leaf, art-contract paths with stand-ins
439401d21a ledger: file OFFLINE_PILE_DEPLOY_ONE_TRIP_FOR_ALL (owner card)
7613d36ca5 Owner cards 10:12 PM: sun-lit peaks, biome-wide swirl layer, harsher Rust Cathedral
b262d9b9fd Scrub farmer camps removed (owner card: Remove the camps); Dune Sea label centred on its interior
a7ce577bbf Owner cards 10:09 PM: Uvak canon recolour, Dune Sea label centre items
040ec719de World paths: ancient highway is old broken asphalt, not gold
cfa4ba8f77 Worldmap mods study: WMBP fixed-rotation peaks, sun-facing hill rotation verdict, swirl techniques
45a2a528d0 Owner feedback items: flier eye/shoulder test, farmer camps, mountains and faces redraw
... 433 more: git log --oneline a6f1439959..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : LOADING  → corrected to UP, measured now
- Bridge: FREE    since 2026-10-21T05:31:15Z

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
 M infrastructure/state/art/sheets/aiwha_wingfirst_sheet_2026-10-15.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/blue_desert_sheet_2026-10-04.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/braskeen_on_e_variation_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/cauldron_sheet_2026-10-04.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/cauldron_soils_sheet_2026-10-20.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/contagion_sheet_2026-10-04.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/dewback_reconcile_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/dhoggur_swollen_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/donor_pack_port_sheet_2026-10-14.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/donor_pack_redraws_sheet_2026-10-14.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/dragonsnake_canon_variants_sheet_2026-10-18.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/dragonsnake_jfo_pick_sheet_2026-10-18.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/dragonsnake_swim_variants_sheet_2026-10-18.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/facing_regen_needs_eyes_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/facings_regen_picks_sheet_2026-10-18.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/facings_stand_tall_pilot_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/firespit_with_zisska_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/fleetflier_alien_sheet_2026-10-15.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/floodedcanyon_sheet_2026-10-05.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/flowworks_owner_walk_art_sheet_2026-10-11.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/flyer_north_redraw_sheet_2026-10-15.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/gale_dust_sheet_2026-10-20.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/gelatinousslime_sheet_2026-10-05.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/greysea_crown_retracted_and_elder_sheet_2026-10-18.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/greysea_sheet_2026-10-05.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/gss_all_art_sheet_2026-10-11.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/gss_owner_walk_art_sheet_2026-10-11.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/hosereel_coupling_sheet_2026-10-15.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/leaningscrub_open_rows_sheet_2026-10-18.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/liquid_connections_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/liquid_containers_four_styles_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/nightsideice_sheet_2026-10-05.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/nonrm_plants_census_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/own_render_keep_sheet_2026-10-11.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/pit_ladder_hung_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/pit_spikes_half_a_man_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/plant_baroque_bases_sheet_2026-10-16.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
 M infrastructure/state/art/sheets/rustcathedral_sheet_2026-10-05.snapshot.json   generated: art-ledger snapshot churn from today's backfill/sheet refreshes (BENCH art helper); regenerable, not committed
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/raw/A_rails_front.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/raw/B_rails_front.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/runA.out   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/runB.out   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/out/   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/guides/   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/out/   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_north.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_south.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runA.out   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runB.out   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runC.out   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/SuspensionLooks/out/   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/gen.out   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Futuristic/   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Industrial/   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Modern/   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_east.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_north.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_south.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_west.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Scrapper/   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Futuristic.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Industrial.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Modern.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Scrapper.png   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_cap.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_spill.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_upstream.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_v_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_cap.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_spill.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_upstream.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_v_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_cap.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_spill.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_upstream.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_v_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_cap.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_spill.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_upstream.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_v_east.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/foam_toe.log   generated artpipe logs/outputs from earlier art runs (not BENCH today); leave
```

