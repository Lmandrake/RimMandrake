# BENCH_REBOOT_HANDOFF_202610220122 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610211147`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Archmagi blue-screened at ~14:52 PDT 2026-10-21 in the middle of BENCH's offline-pile proofs (live game, full list); it stayed dead until 18:07 because AutoReboot was off. The proof run was cut off, not finished, so anything it was mid-way through is UNMEASURED. The crash investigation now belongs to **Hestia**: ticket `HEST-1` (`D:\Luke\dev\Hestia\tickets\HEST-1.md`). Its read is hardware (0x1E inside nt!KiAbProcessPostContextSwitch, 8 unexpected shutdowns since May; stale BIOS 1501 plus XMP RAM).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The owner is flashing the BIOS and turning XMP off; expect a reboot, and possible further freezes until that is done. AutoReboot is now ON, so a crash costs minutes.
- `~/dev/Lodestar` on this machine is diverged (ahead 39, behind 198), so `bin/ticket.py` is missing locally; HEST-1 was filed with an origin/main export at `D:\ClaudeWork\scratch\lodestar_origin`. Someone should reconcile that clone (not done here: merging a shared checkout is forbidden without care).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `HEST-1` — Archmagi crash: AutoReboot on, WinDbg installed, owner holds BIOS-flash steps; NEXT: Hestia confirms the new BIOS version after the flash and runs !analyze on any new minidump.
- `OFFLINE_PILE_DEPLOY_ONE_TRIP_FOR_ALL` follow-on proofs — cut off by the 14:52 BSOD (last bridge call 21:51:53Z, jawa/static_call reply_fail); NEXT: re-run the pile proofs from the top on the next game-up and treat the 14:3x–14:51 results as UNMEASURED.
- Uncommitted BENCH tree (Transient decisions, art snapshots, ModsConfig backup, fixtures) is the pre-crash session's; NEXT: the next BENCH seat reviews `git status` and commits by explicit path or reverts.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Event 6008 'previous shutdown at' is a stale heartbeat, not the crash time (filed: lessons)

## Closed since the last handoff (1)

- `OFFLINE_PILE_DEPLOY_ONE_TRIP_FOR_ALL` — f382a5d0df

## Filed and still open (4) — the next seat's queue

- `WINCH_REACH_DIAGNOSE_CANREACH_FIBS` — drawbridge_proof LOWER_ONLY_FROM_WINCH FAIL: with the leaf raised the far-bank colonist still gets the lower job (ProofWorkJob spot=winch: CanReach tr
- `DRAWBRIDGE_RAID_DIAGNOSE_LOITERING_AT_MOAT` — drawbridge_proof RAID_UP FAIL (2 runs): 4 assault raiders reach 3-9 cells outside the 2 m island ring and stand still ~1000 of 3000 ticks; WinchJobs 0
- `FALLEN_CORD_DIAGNOSE_LIVE_BUT_HARMLESS` — lines_proof COLLAPSE_CORD_SHOCKS_ONCE FAIL: collapse drops 4 cords, 1 live fall (held at +360), GSS RM_FallenWireShock.externalContacts=2, yet shocks 
- `LADDER_HOSE_DIAGNOSE_SIPS_NOTHING` — lines_proof LADDER_HOSE_DRAINS_RAISED_STAYS FAIL: hose hangs down the ladder (ladders=1, line 'Hangs down a ladder'), pump powered after 30 ticks, but

## Commits

```
0d55d7fb64 conversations: catch-up 5 record(s)
30359599aa Big repaint plan 2026-10-21: dev world measured all-ours (0 donor tiles); biome-only re-stamp tool; 7 items filed
1dd464166e Titanoslime: def header no longer claims the art is owed and renders magenta
be5a561a14 artpipe: BENCH art feed 2026-10-21, 22 gated stand-in jobs (Webwork contracts, PoolNet, meats, terrains)
1a104682f1 TitanPassage: pool from the biome's own hints, sea giants only at sea (owner card 2026-10-21)
0b38d6f451 ledger: offline pile deployed and proven live; 4 MOD findings filed; result JSONs pinned
d392461cd9 northstar_driver.preflight: check_paused reads UNMEASURED on a probe/pause error, not a TypeError crash
3f8ed35a59 code review: RM_LiquidNetKernel.cs CLEAN (full read after the tank-corner change)
f382a5d0df Pile proofs: first live runs' HARNESS/SITE fixes (drawbridge, lines, Webwork static_call args)
f1df418065 tickets: scaffold tickets/ (Lodestar D30)
731a416983 FOUNDRY handoff 2026-10-21: world look live, flier architecture change, night-shift order
e21efac0c9 conversations: catch-up 2 record(s)
1fe520982c lesson: defName rename tile check covers every keeper save
11ffe035c8 ledger: BIOME_DEFNAME_MIGRATION_WAVE_1 note - dev saves carry 3359 tiles on the old names; owner call owed
466dbf8702 ledger: NORTHSTAR_FAST_DRIVER_1 done at 5e068bd4a; lesson: WSLENV for python.exe, DurationMs in replies
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: for     BENCH: deploy offline pile + run proofs (owner: 'You now have bridge')

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/dragonsnake_swim_variants_sheet_2026-10-18.decisions.json   pre-crash BENCH session (untouched this session)
 M Transient/biome_ffar/facings_regen_picks_sheet_2026-10-18.decisions.json   pre-crash BENCH session (untouched this session)
 M Transient/biome_ffar/flowworks_owner_walk_art_sheet_2026-10-11.decisions.json   pre-crash BENCH session (untouched this session)
 M Transient/biome_ffar/leaningscrub_open_rows_sheet_2026-10-18.decisions.json   pre-crash BENCH session (untouched this session)
 M Transient/biome_ffar/liquid_connections_sheet_2026-10-16.decisions.json   pre-crash BENCH session (untouched this session)
 M Transient/biome_ffar/liquid_containers_four_styles_sheet_2026-10-16.decisions.json   pre-crash BENCH session (untouched this session)
 M Transient/modcheck/fixtures.json   pre-crash BENCH session (untouched this session)
 M deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/events/BENCH.jsonl   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/aiwha_wingfirst_sheet_2026-10-15.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/blue_desert_sheet_2026-10-04.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/braskeen_on_e_variation_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/cauldron_sheet_2026-10-04.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/cauldron_soils_sheet_2026-10-20.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/contagion_sheet_2026-10-04.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/dewback_reconcile_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/dhoggur_swollen_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/donor_pack_port_sheet_2026-10-14.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/donor_pack_redraws_sheet_2026-10-14.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/dragonsnake_canon_variants_sheet_2026-10-18.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/dragonsnake_jfo_pick_sheet_2026-10-18.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/dragonsnake_swim_variants_sheet_2026-10-18.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/facing_regen_needs_eyes_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/facings_regen_picks_sheet_2026-10-18.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/facings_stand_tall_pilot_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/firespit_with_zisska_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/fleetflier_alien_sheet_2026-10-15.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/floodedcanyon_sheet_2026-10-05.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/flowworks_owner_walk_art_sheet_2026-10-11.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/flyer_north_redraw_sheet_2026-10-15.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/gale_dust_sheet_2026-10-20.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/gelatinousslime_sheet_2026-10-05.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/greysea_crown_retracted_and_elder_sheet_2026-10-18.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/greysea_sheet_2026-10-05.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/gss_all_art_sheet_2026-10-11.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/gss_owner_walk_art_sheet_2026-10-11.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/hosereel_coupling_sheet_2026-10-15.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/leaningscrub_open_rows_sheet_2026-10-18.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/liquid_connections_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/liquid_containers_four_styles_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/nightsideice_sheet_2026-10-05.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/nonrm_plants_census_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/own_render_keep_sheet_2026-10-11.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/pit_ladder_hung_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/pit_spikes_half_a_man_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/plant_baroque_bases_sheet_2026-10-16.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/art/sheets/rustcathedral_sheet_2026-10-05.snapshot.json   pre-crash BENCH session (untouched this session)
 M infrastructure/state/ledger/events/BENCH.jsonl   pre-crash BENCH session (untouched this session)
 M infrastructure/state/ledger/events/OWNER.jsonl   pre-crash BENCH session (untouched this session)
 M src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md   pre-crash BENCH session (untouched this session)
 M src/RimMandrake/FlowWorks/northstar/review/map/keysheet.html   pre-crash BENCH session (untouched this session)
?? deployed/config/ModsConfig.swap-active.json   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/raw/A_rails_front.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/raw/B_rails_front.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/runA.out   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Ladder/v2/runB.out   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/out/   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/guides/   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/out/   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_east.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_north.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/A_south.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_east.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_north.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/B_south.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_east.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_north.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/raw/C_south.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runA.out   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runB.out   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/PitRamp/v2/runC.out   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/SuspensionLooks/out/   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/gen.out   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Futuristic/   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Industrial/   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Modern/   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_east.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_north.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_south.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/RM_BankWeirWater_west.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/Scrapper/   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Futuristic.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Industrial.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Modern.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/out/composite_Scrapper.png   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_cap.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_spill.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_h_upstream.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Futuristic_v_east.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_cap.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_spill.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_h_upstream.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Industrial_v_east.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_cap.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_spill.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_h_upstream.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Modern_v_east.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_cap.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_spill.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_h_upstream.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/Scrapper_v_east.log   pre-crash BENCH session (untouched this session)
?? src/RimMandrake/FlowWorks/art_source/Weir/raw/foam_toe.log   pre-crash BENCH session (untouched this session)
```

