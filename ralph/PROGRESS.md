# FlowWorks Artisan, aspect 1 (pits and depth): progress

## Pass 5 (2026-11-08, 00:32-~01:30): his story, played three times
Weather: 0 dead games, 0 dropped ssh, 1 deploy (`up` refused to swap the tier list — "REFUSING TO WRITE: swap marker ...
missing or changed" — but game A came up on the right 11-mod flowworks list anyway; checked ModsConfig). `bad_cpus=[0]`.
Retired on the context gate (252k).

**The grey box is explained:** it was rainwater, not the pit's look. s4's crops w020-w050 (`/tmp` only; the shots are on Steve
under the game's Screenshots, `s1_w0*_2044*`/`_2045*`/`_2046*`) show rain streaks, then the spikes going under a flat grey
surface: ~0.5 m of water, aspect 2's silt colour. Dry, the same pit reads as a dark hole with stakes at r20 in morning light.
Rain filling a pit that fast is PIT_RAIN (aspect 2), but it changes his story (prisoners standing in water): worth a number.

**His story, made to come up the passage** (`ralph/live/story1.py raid --spawn gx,0` uses `jawa/fire_raid` with
spawnCenter/EdgeWalkIn/ImmediateAttack; `story3.sh` env FW_SPAWN/FW_ARCHERS/FW_CLOSE; `story5.sh` raids an already staged
map; the watch now logs job targets, lord toils, every pit square and the defenders). Logs on Steve: `Transient/ralph_fw/*_s5b.out`, `*_s6.out`.
- s5b (500 pts Neanderthal tribe, 3 archers): two warriors fell onto the spikes (seen, r20); the others walked round the passage
  and bashed its west wall; one chopped saplings (`RM_RaiderChopForLadder` x2) and ran `RM_RaiderRescueLadder` x3; both fallen
  climbed out by ~2,400 ticks. **No ladder was visible in any frame**: the rescuer stands on the raid's side, so the ladder goes on
  the pit's NEAR (south) wall, where only a stub shows. Then the raid beat the archers and kidnapped everyone (staging: the
  archers stand in a walled passage with no line of sight to anyone outside it).
- s6 (400 pts, 5 archers): **raiders made for the hidden cover from the map edge, 55 squares out**: `AttackMelee@RM_PitCover_WovenScrap`
  and `Ignite@RM_PitCover_WovenScrap` at t+600. One fell (Red, berserker, badly speared: spine, lung, three torso stabs). The
  rescuer spent **2,400+ ticks felling a grown oak** out of sight, the rest bashed walls, and at t+4200 the raid left on its
  colony-damage trigger, so the rescue never came: Red was left in the pit. The archers never shot (Ruling 23: into a pit only
  from the edge; they stood 2-3 rows back, and nobody outside was in their line of sight). Red, in the pit: inspect says
  "Held in a pit: it cannot climb out without a ladder"; right-click from a drafted colonist offers **"Capture Red from the
  edge of the pit"** (it waits at the lip for him to come near). He went down from blood loss, was taken ("In restraints"),
  and "Feed" is offered (no food on a quick-test map). Not seen: the capture message, a doctor tending him from the lip.
  Shots `am_pit_r20_005722`, `am_pit_r11_005722`, `cap_pit_r11_005452` (Steve Screenshots), unjudged.

**Fixed in source this pass (in the commit with this file; built, self-test run; NOT yet watched in game):**
1. `Defs/Pits/ThingDefs/RM_PitCovers.xml`: the three covers are `<isTrap>true</isTrap>`: vanilla's TrashUtility never trashes or
   torches a trap; without it a concealed pit was just a building to raiders.
2. `RM_LadderParity.ChopForLadderJob`: the tree for a ladder is the one felled soonest (walk ~12 ticks a square + felling), and
   felling scales with the tree's growth (`RM_LadderParityMath.ChopWork`, floor a quarter): saplings, as his story says.
3. `RM_RaiderRescue.RescueActive`: a raider of the raid felling wood or taking a ladder while one of its raid is trapped counts as a
   rescue under way, so the colony-damage exit is held through the supply phase too (still capped 5,000 ticks).
4. `RM_LadderDraw`: a portable ladder leans visibly: far wall top/foot ±0.2 cells (it read "straight"); near wall stands 0.72
   above the lip and slants (the rescue ladder's usual wall).
5. Suspension bridge: NOT built. A builder subagent ran out of time after the numbers only: `RM_SuspensionHangMath.cs`
   (deck sag per cell of span by tier, clamped 0.18-0.8 cells; post heights 0.8/0.95/1.25/1.4; cables post top to post top
   dipping to 0.4 above the deck; 0.12 outboard splay so north-south spans show the hang; shadow offset) and
   `SelfTest/SuspensionHangChecks.cs`. Nothing draws from it yet. Its design for the drawing (bend the deck print by the sag,
   posts/cables/suspenders as plain meshes layered between floor pawns and deck walkers, floor shadow, deck walkers lowered by
   the sag, the faded-deck-over-underpass fix, redraw on build/remove): `D:\ClaudeWork\rimmandrake\ralph_flowworks\hung_bridge\PROGRESS.md`.

## The owner's note (1:14 AM PST, via the Conductor): done means provably OK
"I don't need the Judge to say it's ok. I just need it to be provably OK... if you have that evidence, call it, stop the spend,
close the mod." When every bar has evidence anyone can re-check (measurements, telemetry, proof rows on a real map, shots for
the look bars), write DONE.md citing that evidence bar by bar. A judge's approval is not the bar; proof is.

## Next (in order)
0. CONDUCTOR RULING 1:23 AM (read `/mnt/d/ClaudeWork/rimmandrake/conductor/apparatus_audit_flowworks_2026-11-08.md`, 96 lines):
   behaviour bars count measurements; the three it named are marked true above; close the one missing clause on jump, digging
   and wall scaling; reopened: occupant/trapped looks at depths other than 2 m, the ground kit. The long pole is his story played
   END TO END (defenders shoot, the rescue finishes): STAGE it so it completes, don't replay until luck delivers it.
1. (0009583872 is deployed on game A, 01:5x; game up, no map loaded.) Replay `FW_SPAWN=gx,0 FW_ARCHERS=5 FW_CLOSE=3 bash ralph/live/story3.sh 400 TribeRoughNeanderthal s7`
   and look for: nobody targets the cover before it springs; the rescuer fells a sapling in hundreds of ticks; the raid waits;
   the ladder is SEEN going in on the near wall; arrows. Then stage it fairer to his words: archers on the north lip row
   (PZ+2), or open ground beside the passage so defenders see the rescuers (he wrote "the defenders standing on the other side").
2. Odd, unfixed: a trapped raider melee-bashes the passage wall beside the pit from the floor (`AttackMelee@Wall`, s5b and s6
   for 1,700+ ticks). A 2 m-deep pawn hitting a wall on the rim reads wrong; check RM_MeleeTargetReach for buildings.
3. Bridge: build the drawing from the hang math (5 above), then `ladders5.py bridge` at r20/r11; `pawn_walks_under_deck` frames.
4. Re-shoot the depth sheet on this build in daylight (`bars3.py`, look 1 only), same pawn kind in every hole (GPT lead 3:
   different bodies/clothes confound it), and walk one pawn down a graded trench 0..8 levels for pawn_lowers/rises.
   0.5 m vs undug is 0.3 cells (7 px at r20) by `RM_PitDrawMath.SinkFor`; ObliqueFace uses the same pitSinkPerLevel, so any
   shallow-depth boost must change both. Untried.
5. Sluice (`sluice_gate_state_legible` false): for an E-W canal the gate is the side view (owner's FLOWDOOR_EW_PERSPECTIVE
   ruling 2026-10-18), a ~5 px plank whose lifted part hides behind the north post (frame drawn over panel,
   `Building_RM_FlowDoor.DrawAt`, liftCells 0.56). Ideas: lift it clear above the frame, a thicker panel, water's own cue.
6. Owed from earlier: the four fixes' last one (`four.py` grace probe take/save/reload/read), Crashlanded bottle, dig keeps
   progress, trench cover hover shot, geared climb-out, jump, wall scaling. A rm-bridge subagent with a run sheet can take
   these in one sitting while you work C# offline.
7. GPT broaden (pass 4) leads acted on this pass: #1 (let the raid come for real, read what happens) and #6 (stay with the
   prisoner) — both found bugs above. Untried: #3 (one pawn through changing depth), #5 (escape by what the ladder promises).

## Running count (seen in game)
- pit_depth_ladder_legible: false — 4 m vs 8 m too close (pass 3); eased cap unseen
- pawn_height_ladder_legible: false — 0.5 m vs undug barely differs at r20 (pass 3)
- pawn_lowers_on_deeper_cell: unseen
- pawn_rises_on_shallower_cell: unseen
- pit_reads_as_hole: true — the story's dry spiked pit is a dark hole at r20 (s5b); the grey box was rainwater (aspect 2)
- pit_walls_have_visible_depth: true
- pit_not_vanilla_trap: true
- pit_reads_at_size: true
- pit_occupant_below_floor: false — REOPENED (Conductor 1:23): true at 2 m (s5b), but at 4 m in a 3x3 pit the occupant is drawn on the south lip and looks beside the pit (pass 2); the sink clamp to the near lip is the suspect
- pit_occupied_distinguishable: true
- pit_trapped_reads_as_trapped: unseen — REOPENED: nothing measures the wall-over-head fifth; at 8 m the ungeared pawn did not look trapped (pass 2)
- pit_covered_invisible: true — but raiders "saw" it (they targeted it): fixed in source, unwatched
- pit_covered_seam_at_max_zoom: true
- ladder_state_legible: false — south fix built pass 4, deployed this pass, not looked at
- sluice_gate_state_legible: true — Conductor ruling 1:23 on the bar's wording (no zoom named): shut vs lifted reads at r11 (p2), ProofLiquid fill 2/0 shut, 1/1 lifted. Still thin at r20 (5 below is a nice-to-have)
- spikes_read_distinct: true
- trench_wall_cover_shown: true — text read; hover shot owed
- raiders_never_shelter_in_a_cage: unseen
- wall_ladder_rides_on_rails: false — side walls dotted at r20
- portable_ladder_leans_on_its_wall: false — stronger lean built, unseen
- climbing_gear_reads_as_kit: false — REOPENED: worn reads (r8, four facings), on the ground a small brown coil readable only at r3
- geared_pawn_climbs_out: true — Conductor ruling 1:23 on the audit's evidence: p2 geared pawn out at depth 0 at +634 ticks, ungeared control stayed at depth 8; B4_access_gear_climbs_sheer_4m PASS
- jump_into_pit_lands_unhurt: unseen — mostly proven (p2: jumps into 2 m and 4 m landed, no injury hediff); one staging clause owed (see the audit)
- geared_pawn_scales_built_wall: unseen — mostly proven (p2 landed outside the granite ring at +531); owed: the same pawn WITHOUT gear cannot, live on a built wall
- suspension_bridge_reads_hung: false — flat strip; only the hang numbers exist (not drawn)
- pawn_walks_under_deck: false — the walk works (UND_floor_path_walks_under PASS, pass 2 walked it); the DRAWING is wrong: the pawn under it is drawn on top of the deck and the south anchor (pass 2)
- pit_cover_unlike_bridge: true — Conductor ruling 1:23: the cover half is the two cover bars; the bridge reads as a built crossing (posts and rails, p2); hung is judged by its own bar
- digging_takes_hours: unseen — mostly proven (p2: 0 to 0.5 m by shovel 9,520 ticks, ~3.8 h); owed: fill time read live, and raiders filling a trench carry the fill in first
- never_snared_standing (cannot): true
- never_reads_as_building (cannot): true

Count: 14 true, 9 false, 7 unseen (of 30).

## Between this and done
| kind | what | evidence | next observation |
|---|---|---|---|
| blocker | his story has not played to "driven off, prisoners in a tidy prison" | s5b defenders lost; s6 no arrows, no rescue | s7 replay on this build, archers at the lip |
| regression-like | raiders target the concealed cover | s6 t+600 jobs | s7: no job on the cover before it springs |
| unknown | rescue ladder seen going in | s5b frames show none | s7 close shots at r11/r20 |
| unknown | trapped raider bashing a rim wall | s5b, s6 AttackMelee@Wall | read the target finder; decide |
| blocker | bridge reads flat | look4 | this build's bridge shots |
| unknown | returned-prisoner grace across a reload | probe deployed, not run | four.py take/save/reload/read |
| decision | raised ladder drawn on the ground (side/near walls) | QUESTIONS 2 | his look |
