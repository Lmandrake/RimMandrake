# FlowWorks Artisan, aspect 1 (pits and depth): progress

## Pass 8 (2026-11-08, ~03:00-07:00 PST): batch 0, offline, per the Conductor's 3:02 strategy
RATCHET.md is now in his batches (0 offline, A depth gallery, B equipment and crossings, C mechanics arena, D the story
last). This pass did batch 0. Nothing new was seen in the game: at 05:02 the Conductor gave game A to GSS for its landing
("this pass sends nothing more to game A"), and game A was on Graffiti's list anyway (see weather).

**Built, merged, DLL + .srchash committed (source d4671811b8c6), NOT deployed:**
1. Depth drawing, one scale (builder branch worktree-agent-a908dbc64d5ccd15e). Sink `RM_PitDrawMath.SinkFor`: 4k(D/4)^0.85
   to D4, then +k/4 a level to D8, flat past: k 0.3 gives 0.37/0.67/0.94/1.20/1.50 at 0.5/1/1.5/2/4 m. The far face
   (`RM_PitLookMath.ObliqueFace`) uses the same curve plus a small extra past 4 m, soft-capped into the column's opening, and
   the occupant's sink uses the same soft cap, so floor line and face foot agree. Face heights: 3- and 5-row pit 1.20/1.50/
   1.72 at 2/4/8 m; 2-row 1.20/1.49/1.63; 1-row ~0.85 at all. Lip is riser-aware ((z_s+1) - SinkFor(that square)), so a graded
   trench no longer clamps the sink. New setting `pitSinkHoldAbove` (default 0 = drawn centre on the near lip). Bridge calls
   (`args` is one '|'-separated string): `jawa/static_call` type `RimMandrake.FlowWorks.RM_PitDepthDraw`, methods
   `DepthDrawState "<thingIDNumber>"` (one line: cell, depth, sink, drawnZ, lipZ, face, hold, k), `SetSinkHoldAbove "0.4"`,
   `SetSinkPerLevel "0.375"` (live only, not saved). New SelfTest/PitDepthDrawingChecks.cs (11 cases).
   Known edge: a N-S trench whose deepest part is ONE row squeezes its 4 m step below the 3.5 m one (soft cap on a 1-row run);
   the gallery's graded trench has 3 rows at 4 m. `northstar/validation_v2.py` X rows still model the old linear sink: its
   predicted sinks are wrong now (don't trust its X rows until updated).
2. Ladders on rails (worktree-agent-a685de667d76a4c0c): `RM_LadderRigMath.Strokes` drives `RM_LadderDraw.TryPrint`; rails on
   all four walls in both states (north rim to face foot, east/west 0.36 apart, south hooks 0.34 over the lip), rails ~5.5 px
   at 64 px (was 2.6); lowered rides between rails, raised lies out beyond the rim (QUESTIONS 2 rule kept). Portables lean
   11-39 degrees on all four walls; too tall a wall: flat on the floor, and no way out (`RM_LadderUtility.Reaches`
   :87-115 is the one rule the drawing, `LadderLetsOut` and the climb join in RM_CliffMask:430 all ask). Staging a too-short
   portable: placement refuses it, so place on a shallow pit, dig past `portableLadderMaxLevels`, redraw.
3. Hung suspension bridge (worktree-agent-aadc260db98b8231d, pass 7's builder finished): `RM_SuspensionHang.cs`;
   treatment 0 (default) posts on both end squares, main cable dipping post to post, hangers to a sagging deck; 1 rope walk
   (reads as a railing), 2 cable-stayed (reads rigid). Switch: static_call `RimMandrake.FlowWorks.Pits.RM_SuspensionHang`
   `SetTreatment "1"`. Deck redrawn over floor-band pawns beneath, not over a pawn that has walked out south of it. Staging:
   `RM_SuspensionProofs.ProofBuild "x1,z1;x2,z2;timber;god"` (see ladders5.py). A walk-under shot needs a pit at least 5 rows
   N-S (B3 in the gallery is 9 rows at 2 m). Unverified: posts/cables may draw over the head of a pawn in front of them; in a
   pit shallower than 2 m the redrawn deck can hide the head of a pawn beneath that pokes above it.
4. Climbing gear on the ground: candidate E2 (rope coil in a belt, two grapnels, claws, drawSize 0.9) made and judged, NOT
   installed: the art ledger refuses any agent install over an owner-KEPT picture (pre-push ART_VERSION_WRANGLING_1, then
   `art.py install` REFUSED). Put to him as QUESTIONS 6 with the sheet `shots\climbgear_ground_contrast_pass8.png`; files in
   `art_source/ClimbingGear/E2_128_pass8.png`. E2 reads as rope + hooks + claws at 64 px; at 23 px a light coil with spikes.
   Until he rules, climbing_gear_reads_as_kit stays false on the ground (decision row below).
5. Staging for the next sitting: `ralph/live/g8_*.py` + manifest `ralph/live/GALLERY8.md` (fixtures A1-A4, B1-B4, shot
   names, asserts to results.jsonl, commands). Checked offline against the live tool schemas and a mock bridge; the
   FlowWorks-free half ran on game A; the FlowWorks half (dig, ladders, bridge, the save `RM_FW_Gallery8`) has NEVER run.
   `ORIGIN (60,150)` in g8_common.py is provisional until `g8_site.py probe` on the calm map.

Self-tests on the merged build: targeted 181/181 (PitDraw, PitLook, PitDepth, Ladder, Suspension, Hang, Drawbridge,
PitCover, DeepDig, DeepBed, Swim, WallClimb, PitAccess...). Full suite on the merged build (logs
`D:\ClaudeWork\rimmandrake\ralph_flowworks\pass8\selftest_full_*.txt`): 1282/1285; reds PitCapture_follows (known),
LW1 (a hose SwimCellsPublished source pin) and RiverSwitchFlip_weirWhiteWater (a stale text pin), all three red on the
builders' bases before their changes too.

**Weather and harness:** 0 game crashes, 0 restarts, 0 dropped ssh (bad_cpus=[2] all pass). Harness: the print session
stops background agents 10 min after a turn ends ("Background tasks still running 10m after the last turn ... stopping
them"): all five builders died at 03:27 and 1.5 h went before I relaunched them in the FOREGROUND (all five in one message,
run concurrently, ~50-60 min). Never end a turn with background agents running; a builder with no writes for 30 min is
dead. Game A was switched to Graffiti's list at 03:27 (steve_games.py tier_a=graffiti); since 04:01 GSS ranks first on A.
`codex_home_1`'s Codex login is dead ("refresh token already used"): the next image job there needs a fresh login.

## Next (in order; ralph/NEED_GAME is set)
1. When game A is ours: `ralph/steve.sh tier` (flowworks list), `deploy`, `up`. Check the deployed DLL's srchash.
2. `g8_site.py probe` -> set ORIGIN -> `build --save RM_FW_Gallery8` -> `verify` (GALLERY8.md has the commands).
3. Batch A (`g8_depth.py --k 0.3,0.375 --hold 0,0.4`): measure a colonist's drawn feet-to-crown on the undug control at
   root 7.2 (vanilla head offset +0.34 suggests ~1.25 cells, not the provisional 1.0). If ~1.25, the 20 % needs k ~0.375
   (sink 1.5 at 2 m): pick k and hold by eye from the side-by-side, set the defaults, rebuild. Judge bars 4, 5, 10-13; also
   re-see pit_walls_have_visible_depth, pit_occupied_distinguishable, never_snared_standing (their face/sink changed).
4. Batch B (`g8_kit.py`): bars 8, 9, 15-17 (6 waits on QUESTIONS 6), plus pit_cover_unlike_bridge (bridge look changed).
5. First-look shots refreshed (3-4 `first_look_*`), then the GPT broaden call with them (none in passes 6-8; required
   before DONE.md).
6. Batch C, then D (RATCHET).

## Running count (seen in game; look bars judged at ~64 px where re-shot)
- pit_depth_ladder_legible: unseen (rebuilt pass 8; was false)
- pawn_height_ladder_legible: unseen (rebuilt pass 8; was false)
- pawn_lowers_on_deeper_cell: unseen
- pawn_rises_on_shallower_cell: unseen
- pit_reads_as_hole: true (s12 open spiked pit at 64 px)
- pit_walls_have_visible_depth: unseen (true before; pass 8 changed the far face's height)
- pit_not_vanilla_trap: true
- pit_reads_at_size: true
- pit_occupant_below_floor: unseen (rebuilt pass 8; was false at 4 m)
- pit_occupied_distinguishable: unseen (true before; occupant sink changed)
- pit_trapped_reads_as_trapped: unseen
- pit_covered_invisible: true (s11 pair at 64 px)
- pit_covered_seam_at_max_zoom: true
- ladder_state_legible: unseen (rebuilt pass 8)
- sluice_gate_state_legible: true
- spikes_read_distinct: true
- trench_wall_cover_shown: true
- raiders_never_shelter_in_a_cage: unseen
- wall_ladder_rides_on_rails: unseen (rails built pass 8)
- portable_ladder_leans_on_its_wall: unseen (rebuilt pass 8)
- climbing_gear_reads_as_kit: false (ground: kept sprite, a brown blob at 64 px; E2 awaits his ruling, QUESTIONS 6)
- geared_pawn_climbs_out: true
- jump_into_pit_lands_unhurt: unseen (out, and floaters: not on this mod list)
- geared_pawn_scales_built_wall: unseen (no-gear control owed)
- suspension_bridge_reads_hung: unseen (built pass 8)
- pawn_walks_under_deck: unseen (deck over floor pawns built pass 8)
- pit_cover_unlike_bridge: unseen (true before; the bridge's look changed)
- digging_takes_hours: unseen
- never_snared_standing (cannot): unseen (true before; occupant sink changed)
- never_reads_as_building (cannot): true

Count: 10 true, 1 false, 19 unseen (of 30).

## Between this and done
| kind | what | evidence | next observation |
|---|---|---|---|
| blocker | game A is GSS's until it lands | Conductor 05:02; tier_a=graffiti since 03:27 | NEED_GAME; then tier, deploy, up |
| unknown | the whole pass-8 look (depth, rails, portables, bridge, gear) | built, 181/181 offline, never drawn in game | batches A and B |
| unknown | a colonist's drawn feet-to-crown (sets the 20 %) | head offset +0.34 on a 1.5 mesh suggests ~1.25 | undug control at root 7.2 in batch A |
| unknown | g8 FlowWorks staging works at all | mock dry run only | g8_site.py build/verify |
| regression risk | Proven pit look bars ride on the changed face | pass 5 shots predate it | batch A frames |
| decision | climbing gear ground sprite: his kept one fails the bar | shots/climbgear_ground_contrast_pass8.png | his ruling on QUESTIONS 6 |
| decision | rain rate (QUESTIONS 4), floaters off game A's list, raised-ladder rule (QUESTIONS 2) | unchanged | his word |
| unknown | his story end to end | s14 best so far (pass 7) | batch D, last |
