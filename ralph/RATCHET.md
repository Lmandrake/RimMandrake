# FlowWorks aspect 1 (pits and depth): the ratchet (Conductor, 2026-11-08 ~02:00 AM PST)

Follows the audit (`/mnt/d/ClaudeWork/rimmandrake/conductor/apparatus_audit_flowworks_2026-11-08.md`) plus the Conductor ruling 1:23 AM (OWNER_NOTE.delivered) where PROGRESS differs. PROGRESS's "Count: 14/9/7" is wrong; the true split is 14 proven, 16 remaining (30 bars).
Bar ids are the 30 in `ralph/ASPECTS.md` / the north-star walk (`design/validation_walks/RimMandrake/FlowWorks.md`). "p2" = `D:\ClaudeWork\rimmandrake\ralph_flowworks\pass_002.jsonl` line 3294, shots in `shots\old\pass2\bar_<id>_*`.

## Remaining (work only on these, in this order)
Bars (16). Batch the stagings: one bridge sitting should close several.
1. jump_into_pit_lands_unhurt: floating creatures in and out, and jump/fly OUT, are not shown on the current build. One state-read run (no flight imaging, read depth + injury hediffs) closes it.
2. digging_takes_hours: fill time not read live; "raiders filling a trench carry the fill in first" never staged. One raid filling a trench with jobs logged settles both.
3. geared_pawn_scales_built_wall: the no-gear control on a built wall was never run live. Run the same pawn without gear on the granite ring; confirm ProofLadderParity goes through the production access check.
4. pit_occupant_below_floor (REOPENED): true only at 2 m. At 4 m in a 3x3 pit the occupant is drawn on the south lip (sink clamped to the near lip). Fix, then one r20 shot each at 4 m and 8 m.
5. pit_trapped_reads_as_trapped (REOPENED): nothing measures wall-over-head (about a fifth of the pawn's height). At 8 m the ungeared pawn did not look trapped. Measure the ratio, one shot at 4 m and 8 m.
6. climbing_gear_reads_as_kit (REOPENED, half shown): worn reads (r8, four facings); on the ground it is a brown coil, readable only at r3. One ground shot at r11/r20 where it reads as a kit.
7. STORY (the done condition, not a bar): his covered-pit-trap story played end to end: defenders shoot, the rescue finishes, ladder seen going in on the near wall. Stage it so it completes: s7 replay (`FW_SPAWN=gx,0 FW_ARCHERS=5 FW_CLOSE=3 bash ralph/live/story3.sh 400 TribeRoughNeanderthal s7`), then archers on the north lip row or open ground beside the passage. Must also show no raider job on the concealed cover before it springs (pit_covered_invisible regression check, isTrap fix unwatched).
8. ladder_state_legible: south (near) wall lowered draws nothing; fix deployed pass 5, unseen. One r20 lowered/raised pair on the south wall. Open owner look: QUESTIONS 2 (raised ladder drawn on the ground).
9. portable_ladder_leans_on_its_wall: stronger lean (`RM_LadderDraw`) deployed, unseen. One r11/r20 shot, plus a negative control (too tall lies flat and gives no way out).
10. pit_depth_ladder_legible: 4 m vs 8 m too close. Eased cap built, unseen. Re-shoot the depth sheet in daylight on this build, same pawn kind in every hole (`bars3.py`).
11. pawn_height_ladder_legible: 0.5 m vs undug is 0.3 cell (~7 px at r20, `RM_PitDrawMath.SinkFor`). Boost shallow sink; ObliqueFace shares `pitSinkPerLevel`, so change both. Shot of 0.5 m vs undug.
12. pawn_lowers_on_deeper_cell and 13. pawn_rises_on_shallower_cell: never tried. One pawn walks a graded trench 0..8 levels and back; shot at each cell and the drawn y read. Likely inherits item 11.
14. raiders_never_shelter_in_a_cage: never staged. One ranged raid beside a climbable trench and a sheer pocket; read each raider's cover cell and the cage flag (TRENCH_raiders_skip_sheer_cage was UNMEASURED).
15. wall_ladder_rides_on_rails: behaviour measured; look half open: no rails drawn on any wall (dotted rungs). Draw rails, r20 shot of N/E/W/S.
16. pawn_walks_under_deck (draw): walk measured (UND_floor_path_walks_under PASS); pawn under a deck is drawn on top of it. Fix draw order; frames of a pawn walking beneath. (Do not call it "never walked": pass 2 walked it.)
17. suspension_bridge_reads_hung: nothing drawn from `RM_SuspensionHangMath.cs`. Build the drawing (design: `D:\ClaudeWork\rimmandrake\ralph_flowworks\hung_bridge\PROGRESS.md`), `ladders5.py bridge` at r20/r11.
Owed, not bars: four.py grace probe (take/save/reload/read); trapped raider melee-bashing a rim wall (`AttackMelee@Wall`, check RM_MeleeTargetReach); a number for rain filling a pit (aspect 2).

## Proven (locked)
- geared_pawn_climbs_out: p2: geared pawn out at depth 0 at +634 ticks, ungeared control stayed at depth 8; `Transient/live_session/pass2c_20261019T023413/session.json` B4_access_gear_climbs_sheer_4m PASS, B4_access_no_gear_stays_in PASS (ruling 1:23).
- pit_cover_unlike_bridge: p2: the bridge reads as a built crossing, timber deck with posts and rails; hung look is judged only by suspension_bridge_reads_hung (ruling 1:23).
- sluice_gate_state_legible: p2: shut vs lifted reads at r11 (`shots\old\pass2\bar_sluice_gate_state_legible_crop_r11_shut_over_open*`), ProofLiquid fill 2/0 shut vs 1/1 lifted. The bar names no zoom (ruling 1:23). r20 plank is a nice-to-have only.
- pit_reads_as_hole: dry story pit, dark hole with stakes at r20 (s5b, pass 5, commit 0009583872; rain-filled grey box was aspect 2).
- pit_walls_have_visible_depth: PROGRESS pass 5 count; `shots\old\first_look_*` and pass 4 look sheets.
- pit_not_vanilla_trap: PROGRESS pass 5 count.
- pit_reads_at_size: PROGRESS pass 5 count.
- pit_occupied_distinguishable: PROGRESS pass 5 count; `shots\pass6\s7_undug_covered_open_occupied_61px.png`.
- pit_covered_invisible: same look before and after the cover (`shots\old\first_look_1a_passage_before.png`, `first_look_1b_passage_covered.png`), commit 0009583872. (The story check is item 7.)
- pit_covered_seam_at_max_zoom: `shots\old\first_look_3_seam_closeup.png`, `first_look_3b_seam_at_game_max_zoom.png`.
- spikes_read_distinct: `shots\old\first_look_4_open_spiked_pit.png`.
- trench_wall_cover_shown: p2 read ShotCalculationTipString "Trench wall: blocks 44%" at D2, "74%" at D3 (ProofTrenchCover 0.441/0.740). The "hover shot owed" caveat is dropped.
- never_snared_standing (cannot): every occupant frame shows a sunk pawn.
- never_reads_as_building (cannot): PROGRESS pass 5 count.
(For bars with only "PROGRESS count", the loop should add the exact file next time it opens that shot.)

## Rules
1. A proven bar stays proven and is not re-tested unless a change touched what it depends on; a pass does not re-prove Proven bars.
2. A bar moves back to Remaining only on a shown regression, with the evidence written beside it.
3. When a Remaining bar is proven, move it to Proven with its evidence and build/commit in the same commit. When Remaining is empty, write DONE.md citing Proven ("I don't need the Judge to say it's ok. I just need it to be provably OK").
