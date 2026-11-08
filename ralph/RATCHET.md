# FlowWorks aspect 1 (pits and depth): the ratchet (Conductor, 2026-11-08 ~02:00 AM PST)

Follows the audit (`/mnt/d/ClaudeWork/rimmandrake/conductor/apparatus_audit_flowworks_2026-11-08.md`) plus the Conductor ruling 1:23 AM (OWNER_NOTE.delivered) where PROGRESS differs. PROGRESS's "Count: 14/9/7" is wrong; the true split is 14 proven, 16 remaining (30 bars).
Bar ids are the 30 in `ralph/ASPECTS.md` / the north-star walk (`design/validation_walks/RimMandrake/FlowWorks.md`). "p2" = `D:\ClaudeWork\rimmandrake\ralph_flowworks\pass_002.jsonl` line 3294, shots in `shots\old\pass2\bar_<id>_*`.

## Remaining (work only on these; batches per the Conductor strategy 3:02 AM, OWNER_NOTE.delivered)
Bar numbers are the old Remaining order (kept so earlier notes still point right). Each bar keeps its acceptance test.
Another pass is justified only by a named failed assertion or a missing shot.

### Batch 0, offline (pass 8): the shared depth drawing and the look fixes, with draw-math tests; one validation map,
staging scripts, state-log asserts and shot coordinates (`ralph/live/g8_*`, manifest `ralph/live/GALLERY8.md`).

### Batch A, daylight depth gallery (bars 4, 5, 10-13)
4. pit_occupant_below_floor (REOPENED): true only at 2 m. At 4 m in a 3x3 pit the occupant was drawn on the south lip (sink clamped to the near lip). Accept: occupants on the south/middle/north rows of 3x3 pits at 4 m and 8 m, root 7.2 and 20.
5. pit_trapped_reads_as_trapped (REOPENED): wall over head about a fifth of the pawn's height at a superdeep (2 m+) occupant. Accept: the ratio measured on a shot at 2 m, 4 m and 8 m (crown to rim vs feet to crown), plus the state read.
10. pit_depth_ladder_legible: 4 m vs 8 m were too close. Accept: daylight depth sheet, undug/0.5/1/1.5/2/4/8 m side by side, each told apart by eye.
11. pawn_height_ladder_legible: 0.5 m vs undug was 0.3 cell. Accept: same pawn kind in each hole, sink read per hole, strictly lower to 4 m, equal at 4 and 8 m, each step visible on the shot.
12. pawn_lowers_on_deeper_cell and 13. pawn_rises_on_shallower_cell: never tried. Accept: one pawn walks the graded trench 0..8 levels both ways (N-S and E-W), cell/depth/drawn-y logged per stop, before/after frames.

### Batch B, equipment and crossings gallery (bars 6, 8, 9, 15-17)
6. climbing_gear_reads_as_kit (half shown): worn reads; on the ground a brown coil. Accept: ground shot at root 7.2 and 20 reading as a kit.
8. ladder_state_legible: south (near) wall lowered drew nothing (fix pass 5, unseen). Accept: lowered/raised pair, all four walls, root 7.2. Open owner look: QUESTIONS 2.
9. portable_ladder_leans_on_its_wall: lean on every wall, plus the too-tall control lying flat with no way out (shot + reachability read).
15. wall_ladder_rides_on_rails: no rails drawn. Accept: rails on N/E/W/S at root 7.2, raised and lowered.
16. pawn_walks_under_deck (draw): walk measured in pass 2; pawn under a deck drawn on top of it. Accept: before/mid/after frames of a floor pawn passing beneath, deck over him.
17. suspension_bridge_reads_hung: nothing drawn from `RM_SuspensionHangMath.cs`. Accept: treatments side by side at root 7.2 and 20, one default.

### Batch C, mechanics arena (bars 1-3, 14)
1. jump_into_pit_lands_unhurt: jump pack/Skip in and out with depth + injury hediffs read (no flight images). Floater races are all from mods not on game A's list (FlowWorks_PitTravel.xml): needs a profile with one of them or the owner's ruling.
2. digging_takes_hours: fill time read live; raiders filling a trench carry the fill in first (jobs logged).
3. geared_pawn_scales_built_wall: same pawn without gear on the granite ring (control), through the production access check.
14. raiders_never_shelter_in_a_cage: a ranged raid beside a climbable trench and a sheer pocket; each raider's cover cell and the cage flag read.
Owed, not bars, piggyback here: four.py grace probe (take/save/reload/read); trapped raider melee-bashing a rim wall (`AttackMelee@Wall`, RM_MeleeTargetReach); a number for rain filling a pit (aspect 2).

### Batch D, LAST: his story made deterministic (the done condition, item 7)
Scripted raid, fixed seed, dry weather, known defenders (the colony's own armed) and rescuer; layout of s14 (`FW_PERIM=20`, spawn 6 south of the mouth). SAVE just before the raiders reach the cover (and read their jobs: none on the concealed cover, pit_covered_invisible regression check), save after capture and before the rescue; retry only the failed segment; keep one continuous successful run as the final evidence: two fall through the cover, rescue ladder on the near wall, defenders shooting the rescuers, raid driven off, injured prisoners in the drained pit prison.

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
