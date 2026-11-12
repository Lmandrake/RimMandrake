# BROADEN: EXCAVATION_WALL_ART_1 (2026-11-12 05:33 -0800, CLAUDE_ARCHMAGI_FWLIVE)

## The question (to GPT via `src/RimMandrake/Utils/gpt_consult.py`, model gpt-6.1-sol)

> You are reviewing the testing of a RimWorld mod feature, as a different model. Be concrete and brief (max ~15 bullets).
> 
> STATEMENT (what must be true in ordinary use):
> - A1: Every dug depth D1..D4 (0.5 m steps; D4 = 2 m "superdeep") draws its own wall-face height (north face band grows, floor darkens), and liquid in the pit covers the foot of the wall.
> - A2: Pit spikes (RM_Spikes), the wooden ladder lowered (RM_Ladder) and raised (RM_LadderRaised) ship their own PNGs, no magenta, and no def uses vanilla's TrapSpikeArmed art.
> - A3: In a game frame, D1..D4 read as visibly different depths and a D4 cell reads as a hole, not a building.
> - A4: In a frame, some spike shows at the bottom of a spiked D4 cell.
> - A5: the owner reviews them in game (not ours to test).
> 
> The drawing: a SectionLayer draws per-cell faces from a depth grid in a 3/4 "quarry" perspective: north face band (height grows with exposed drop = own depth minus north neighbour depth minus fill), thin side strips, floor darkness. Spikes are a Building drawing stakes inside the visible floor rect, fading out under water (gone at 1 m). Spikes may be placed only at the foot of a wall >= 2 m.
> 
> WHAT I TESTED (live, fresh quicktest map, small mod list with all DLC):
> - A row of separate 3x3 pits D1, D2, D3, D4 dry; D4 with 1 m water; D4 spiked via the player's Architect designator (centre square refused: no wall over it); D4 with a lowered ladder on the north wall and a raised one on the south wall; D3 where spikes were tried (refused); a 3x3 given the player's "Dig to 4 m" order that colonists dug partly (shovel needed). Screenshots at ordinary zoom and closest zoom, midday light. Ordinary map clutter (rock chunks, logs) present.
> - Live read of the loaded DLL's face math (D1..D4 heights 0.12/0.23/0.35/0.50 of a cell; a 5-deep with 1 m water shows a 3-deep face). C# SelfTest cases. Deployed PNG census, magenta-pixel scan (found and fixed one near-transparent pure-magenta fringe pixel in the raised ladder's east/west sprites), Player.log texture-error scan.
> 
> QUESTION: What would a real player try that I have NOT tested — someone new, someone experienced, someone trying to break it, a messy real case — that could make one of A1-A4 false in practice? Rank by how likely it is to reveal a real defect. For each: what to set up and what to look at.

## The answer (verbatim)

Ranked by my estimate of defect likelihood:

1. **Change an already visible pit through normal play.** Finish digging D1 → D4, then change its fill and north neighbour’s depth without moving the camera. Look for stale face heights, darkness or spike positions; pan away and back to see whether that “fixes” them. **A1, A3, A4**

2. **Use adjoining pits with unequal depths.** Build a connected D1–D4 staircase running north–south, then east–west, including an inside corner. Check faces against the *exposed drop*, side-strip joins and floor shading. A neighbour legitimately hides some wall, but should not produce gaps or floating faces. **A1, A3**

3. **Put spikes against every permitted wall orientation.** Try north, south, east and west edges, plus corners, in dry D4 pits. Inspect each accepted placement at ordinary zoom: does at least one stake remain visible inside the floor, or does the wall cover it completely? **A4**

4. **Fill gradually through the spike fade range.** Observe a spiked D4 at several fills below 1 m, immediately below 1 m and at 1 m; drain it again. Look for liquid behind the wall foot, premature spike disappearance, abrupt jumps or spikes failing to return. **A1, A4** The intentional disappearance at 1 m is not itself a defect.

5. **Leave ordinary clutter exactly where the pit is dug.** Dig beneath chunks, logs and dropped stacks; let pawns cross and items accumulate at the north edge and floor. Check whether drawing order makes objects appear suspended, conceals every spike or makes D4 resemble a solid platform. **A3, A4**

6. **Exercise every ladder rotation and state transition.** Build lowered and raised ladders on every supported wall orientation; raise/lower an existing ladder where supported. Inspect construction previews and finished objects for magenta, missing art, wrong sprites and overlap that obscures the hole. **A2, A3**

7. **Make irregular, cramped holes.** Try a single cell, a one-cell-wide trench in both directions, an L shape and a narrow connection between larger pits. These stress overlapping face bands and side strips; check whether the D4 floor or its spikes disappear entirely. **A1, A3, A4**

8. **Save and reload a mixed, partially flooded installation.** Include all depths, spikes and both ladder states; reload, then modify one cell. Check restored depths, fill, art and whether the first modification updates all affected neighbours. **A1–A4**

9. **Cross a rendering-section boundary.** Locate a section boundary and place a connected pit across it; dig or fill cells on either side. Look for seams, a neighbour face that updates only on one side, or spikes clipped at the boundary. **A1, A3, A4**

10. **Remove the wall supporting installed spikes.** After valid placement, deepen the adjacent cell until the qualifying wall disappears; also change that neighbour’s fill. Whatever retention rule is intended, inspect for floating stakes, buried stakes and stale wall geometry. **A1, A3, A4**

11. **Judge it under less favourable viewing conditions.** Repeat the depth comparison at night, under roof/shadow, with snow where applicable, and at a farther routinely used zoom. Check whether D1–D4 remain distinguishable and D4 retains a readable opening. **A3, A4**

12. **Check the final resolved definitions.** Inspect the loaded spike and ladder defs, including rotation/state graphics and inherited fields, for any reference to `TrapSpikeArmed`. Clean screenshots and a PNG census cannot by themselves establish that no def still uses it. **A2**

## What I tried and what I found (live, Archmagi, FlowWorks tier, fresh quicktest; script `whittle/excavation_wall_art_1/evidence/broaden_script.py`)

- **#1 change a visible pit, camera never moves** (`evidence/broaden_e1_pit_changed_under_fixed_camera.png`): a 3x3 dug
  to D1, then deepened to D4, filled to 1 m, drained, with no camera move between shots. Every step redrew at once: the
  D1 hairline face became the D4 face, the 1 m water cut the face to about 13-16 px (the expected 2-notch face is 0.23 of a
  73 px cell, about 17 px), and draining brought the D4 face back. No stale section.
- **#2 adjoining pits with unequal depths** (`evidence/broaden_e2_staircases.png`): three 4-step staircases. Depth
  growing south: each step shows its own 1-notch north face, and the floors darken step by step. Depth growing east: each
  column's north face grows (it borders ground) and the side strips show the 1-notch step. Depth growing north: only the
  deepest row (against ground) shows a face, and the shallower rows show none, because their north neighbour is deeper
  (as specified). It reads as a ramp falling away north. No gaps or floating faces.
- **#3 and #7 spikes at every permitted wall in cramped holes** (`evidence/broaden_e3_spikes_single_cell_and_trenches.png`):
  a single-cell D4 hole, a 1x3 N-S trench and a 3x1 E-W trench, spikes laid through the player's Architect button (all
  7 squares accepted). Stakes show in every one: a sliver below the face in the single cell and the E-W trench, a full
  strip in the N-S trench.
- **#4 fill through the spike fade** (`evidence/broaden_e4_spike_fade_half_metre.png`): the spiked D4 at 0.5 m shows its
  stakes faded under the water film, with the wall face above the water. Drained, the full stakes return. (My first run
  used the wrong columns, 116-118 instead of 117-119; it is in `broaden_log.json`, and the fixed run is
  `broaden_e4fix_log.json`.)
- **#12 the resolved defs**: RM_Spikes and RM_Ladder inherit only `BuildingBase` (no graphic), the deployed
  MandrakePatches holds no patch naming them or TrapSpikeArmed, and the live `jawa/get_def` reads of both defs carry no
  TrapSpikeArmed. Deployed and repo FlowWorks XML: 0 (`evidence/a2_texture_census.txt`).
- **#5 clutter** came from ordinary play: the run-3 map left rock chunks in the D3 pit and logs in the water pit
  (`evidence/live_contact_sheet_D1_D4_water_spikes_ladder.png`). They draw over the floor and the pits still read as
  holes.
- **#8 save and reload** (`evidence/broaden_e5_row_after_save_reload.png`): `EWA_WALL_ART_REVIEW_20261112.rws` loaded
  with `rimworld/load_game_ready`. The row draws exactly as it did before the save: D1..D4 faces and floors, the water
  pit, the spike ring, the lowered and raised ladders, and the colonist-dug cell.
- Not tried: night or snow light (#11), a section-boundary seam (#9), removing a spike's wall
  afterwards (#10), and raising or lowering an existing ladder in every rotation (#6; the scene raises one and the owner
  review stage covers all four walls).

Cause of the half-covered spiked pit (the judge's flag; first E4 frame, `D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_ARCHMAGI_FWLIVE\ewa\broaden\sheet_e1_e4.png`, panel 5): HARNESS. `broaden.py` filled x=116..118 at 0.5 m, but the spiked pit is x=117..119, so the
east column stayed dry and the stray 116 column is the water strip at the panel's left edge. `broaden_e4fix.py` filled 117..119
and the whole pit draws under water (`evidence/broaden_e4_spike_fade_half_metre.png`). Not a water-render defect.

Found and fixed this round: a near-transparent pure-magenta pixel in RM_LadderRaised east/west (`c39192a556`, see
DONE.md). Found, harness: owner_review_stage staged spikes in a 1.5 m pit and on the pit centre, where a player cannot
build them (fixed in the same commit).
