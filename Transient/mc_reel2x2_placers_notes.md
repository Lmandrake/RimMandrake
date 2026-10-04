# RM_HoseReel 2x2 placer notes

(skeleton; appended per file)

## validation_hose.py  (py_compile ok)
Main scene (run_live, lines ~134-140): positions UNCHANGED (Position = SW cell).
- R1 (42,66) -> footprint (42,66)(43,66)(42,67)(43,67); F1 (66,66); WALL x=53 z62..68. Overlaps none (computed). Centre (43,67) to F1 23.5; A* route with wall detour 25.5 + hop, x1.08 = 28.3 <= 30.
- R2 (42,74) -> (42,74)(43,74)(42,75)(43,75); F2 (60,74); route 19.1 <= 30. R1/R2 footprints disjoint; all inside SITE (38,58,36,20).
- H1b: far target (R1x+60) still "too far"; WALL[2]=(53,64) still "target blocked" (checked before routing).
Maze (MAZE text unchanged; marker R=(44,86) is now the SW cell): footprint (44,86)(45,86)(44,87)(45,87), all '.' chamber cells (rows MZ0+2/MZ0+3). Spiral route re-computed: 29.9 with 1.08 slack vs the default cap 30 -> added MAZE_LEN=40 (set:maxLength=40 after defaults) so M2 is not marginal.
- PREEL (42,96): (42,96)(43,96)(42,97)(43,97). PTANK moved (43,96) -> (44,96): footprint (44,96)(45,96)(44,97)(45,97), shares the reel's whole east edge (portSide [1,0]); old (43,96) would have overlapped the reel. PLONE (52,96): (52..53,96..97), no neighbour, disjoint from reel/tank/maze walls; all inside MSITE. Shot rect widened 8->10.
- New FILLER wall (49,87) inside the spiral corridor box, off both routes, not in the reel footprint.
- M3b: was RECORD "still drawn"; now PASS iff laid false + retractReason "route too long" (a cap change alone does not move the corridor hash, so the FILLER wall triggers the 250-tick check). Then maxLength back to 40 and re-lay.
- M4: was "laid, not drawn"; now expects laid false + retractReason "no route" (+ check "no route"). Renamed M4_unreachable_retracts.
- M5: walls (g, b, FILLER) removed, then lay again (hose was reeled in), then expects layOk via the gap.
- Docstring predictions M3/M4/M5 rewritten. run_maze ends with defaults.

## northstar_matrix/  (py_compile ok; selftest.py 53/54, only the pre-existing C2 live-shots check fails)
- design_spec.py hose_spec (~line 319): reel a=(2,4) design -> game Position gc(a); footprint design (2,4)(3,4)(2,3)(3,3). Positions unchanged. Added an assert at spec time: footprint disjoint from walls/water, free end b not inside. Overlap check: walls y=5 (x>=1), water x>=4, b x>=8 -> none. Distances: L=24 straight centre->far 23.5, route*1.08 ~26 <= 30; corner L=24 ~ 18 <= 30. Spec hash unchanged (DS2/DS6 PASS).
- scenes.py _add_strips (~line 532): composed hose strip cells x3..14 at row y; reel Position = cells[0] = design (3,y); footprint (3,y)(4,y)(3,y-1)(4,y-1) (design y grows south). OLD footprint was 1 cell. (4,y) is the strip's 2nd planned cell, now under the reel (cells list kept: oracle counts it). New sc["hose"]["footprint"]; lint (line ~663) now also flags a footprint cell on cord/device cells; lint over all topologies x aerial x hose = 0 problems (row y-1 is the blank gap row / aerial gap).
- placer.py line 196: comment only (reel = cells[0] = the 2x2 SW cell); hose_plan uses design_spec's g(a) = SW cell. Steps unchanged (check/lay/flow/census all key on Position, found by any cell).
- fakegame.py: reels keyed by Position, footprint x..x+1 z..z+1, _reel_at any-cell lookup, "same cell" over 4 cells, "too far" from centre (x+1,z+1) to target cell centre, start cell = nearest footprint cell (ties lowest x,z), route = hop + A* with other footprint cells blocked, *1.08 vs 30 -> "route too long" (old "no route" for over-cap), build refuses (and logs reel_refused) a reel whose footprint overlaps edifice/conduit/thing/another reel, destroy_batch drops a reel when any footprint cell is inside the rect, census gains footprint/start/port*/retractReason/retractTick + top-level retracts, 250-tick corridor check retracts (laid false + reason) or re-lays. Hand-tested: same cell, route too long, too far, retract after wall across the corridor, overlap refusal.
- run_live.py: no change needed (matches census reel = Position; no distance literals).

## human_review.py  (py_compile ok; `--plan` layout_check clean, negative control (st.15 reel moved onto the wall) flagged)
Footprint = Position .. Position+(1,1), station-local north-up cells. New reel_footprint() + layout_check now flags a footprint cell on a wall/rock/conduit/device/mast/hostile cell, another reel's footprint, or any free end. Route = A* from nearest footprint cell with the rest of the footprint blocked, +hop, x1.08 vs the 30-cell default.
- st.12/13/14 (line ~194-200) reel (0,2): cells (0,2)(1,2)(0,3)(1,3); far (16,2); station 18x6, no walls. Dist 15.5, route 17.0. Unchanged.
- st.15 (~204) reel (0,2) same cells; wall (13,1..4) clear. Far was (26,2): route 29.6/30 (too marginal) -> far moved to (24,2), ~27.6; title text "26-cell" -> "24-cell".
- st.16 (~211) reels (0,10): (0,10)(1,10)(0,11)(1,11), far (19,10); (10,0): (10,0)(11,0)(10,1)(11,1), far (10,19). Disjoint, no far in either; 20.2 each.
- st.17 (~215) (0,3): (0..1,3..4); (0,5): (0..1,5..6) - adjacent, disjoint; far (21,3)/(21,5); lanes (centre z 4 and 6) still 2 apart. 22.4.
- st.18 (~219) (0,6),(0,15),(6,0),(15,0): footprints (0..1,6..7),(0..1,15..16),(6..7,0..1),(15..16,0..1); disjoint; far ends not inside any. 22.4 each.
- st.22 (~318) reel (6,5): (6,5)(7,5)(6,6)(7,6), inside the inner chamber interior x5..7 z4..6 (no wall; west door (4,5) reached via row z=4). Short route 24.5/30.
- st.23 (~324) same reel; with (12,1),(12,2) walled the NE route is 29.1/30 -> still re-routes (thin margin: 0.9). Station text now says it re-routes if it fits, else retracts with message + alert.
- Placement code (put("RM_HoseReel", g(s, reel)), lay/flow/census at ~714/796/816) takes Position; unchanged. Key sheet regenerated by --plan.

## Not touched / no reel placement found
validation.py (only a CompHoseReel.cs string check), pole_shots.py, northstar/ (data JSON only), run_live.py (keys on census reel = Position).
