# FlowWorks Artisan, aspect 1 (pits and depth): progress

## Pass 2 (2026-11-07): what I saw, what I changed

Game A on Steve, `flowworks` list, quick-test temperate map (story1 layout). Weather: 0 dead games, 0 dropped ssh, bad_cpus
[], ~5 deploy+restart cycles (bridge up in 28-34 s), one slow fetch retried. Retired on the context hook (~260k).

**The raid stall, measured live and fixed (commit dc3a5cd108, deployed, seen).** Pass 1's theory (reach disagrees with the
pather) was WRONG: `RM_WallReach.ProofReachPair` agreed with A* for every raider/colonist pair (save `fw_story1_stall`).
Tick-by-tick job watch (`ralph/live/jobwatch.py`): every 250 ticks each raider took AttackMelee on the colonist INSIDE the
compound, the pather failed, vanilla's ErroredPather Wait(250) followed. Cause: a melee searcher takes AttackTargetFinder's
region-BFS branch (`GenClosest.ClosestThingReachable`, AttackTargetFinder.cs:233), which never asks CanReach, and regions
don't know the pit. Fix: `Source/Superdeep/RM_MeleeTargetReach.cs`, melee target picks require CanReach on maps with a hole.
`ProofThink` there runs one pawn's think tree and names the giving node (use it on any future "they just stand there").
After the fix (`shots/pass2/story_replay_after_stall_fix_r7.png`): raiders ran TrashBuildingsDistant on the pit spikes,
set them alight with their trapped comrade on them (he burned to death), one climbed into the pit to club them, two went
round to a colonist outside and later left. Fix: `RM_Spikes` gets `ai_neverTrashThis` (vanilla's rule for traps).
BUILT, NOT DEPLOYED, NOT SEEN.

**TRAP: `Source/RimMandrake_FlowWorks.csproj` lists every .cs by name.** A new file not listed there is silently not
compiled. Two of my "fixed" replays ran the old DLL. Check `grep -c -a <TypeName>` on the DLL after every build.

**Built by a subagent, self-tested, NOT deployed, NOT seen** (logs `D:\ClaudeWork\rimmandrake\flowworks_fetch_prison\`):
- raiders_fetch_their_fallen: `Source/Superdeep/RM_RaiderRescue.cs`, JobGiver_RM_FetchFallen before FightEnemies in
  AssaultColony/Breaching/Sapper. One rescuer per raid (2,500-tick lease), supply chain then set-ladder from the rim, one
  message per raid; given up when the raid stops assaulting; the trapped one walks out by the ladder.
- drained_hole_is_a_prison: `Source/Superdeep/RM_BedlessPitPrison.cs`, setting bedlessPitPrisonEnabled (on): Capture-down
  with no bed on anyone the hole traps; five warden jobs work from the lip (needs wardenFromLipEnabled), food dropped on an
  edge square in his room. NOT covered: a DOWNED bedless prisoner is not fed (vanilla hand-feeding needs a bed); tending
  only when he lies against the wall; hemogen. Decision for him: `ralph/QUESTIONS.md` 1 (a rescue ladder frees prisoners).
- Code review of these two: not done (code_review_status DIRTY). Do one before relying on them.

**The other 14 lines, staged by a subagent at root 11 and 20** (`shots/pass2/bar_<line>_r11|r20_<n>.png`, its notes
`D:\ClaudeWork\rimmandrake\ralph_flowworks\pass2_progress.md`, scripts `ralph/live/bars2_*.py`). Mod bugs it found, each
with repro there: worn climbing gear draws nothing (RM_ClimbingGear: Belt layer, no wornGraphicPath); a lowered south-wall
(rot 2) RM_Ladder draws nothing; a pawn walking under a suspension deck is drawn on top of it; sluice water tint did not
change with fill (probable). Pits at r20 are a dark outlined square; pawns in 4 m pits are drawn on the south lip.

**Four untested fixes: probes built, not run.** `RM_CliffMask.ProofCliffTiming("reset"|"")` times every full derive (load a
save with a big excavation, read it); `RM_PitCoverUtility.ProofCoverScan("")` times one trigger census over every cover vs
the old flood-from-every-cover. Two maps: compare `thisMapDerives` per map after a dig on the other. TakenByLand reload:
not attempted (a river-swept prisoner, aspect 2's river). Baseline (telemetry, Archmagi's game): median tick 1.6-2.0 ms at
x1-x12 after the last FlowWorks deploy (#2139428).

**GPT broaden (asked this pass; answer `D:\ClaudeWork\rimmandrake\ralph_flowworks\gpt_help_pass002.md`).** I sent the
replay sheet and the depth sheet. Seven leads; the three I mean to play, not yet played: (2) at the usual camera distance,
can a player tell who is trapped and does a click beside an occupant land where it looks (the pawn is drawn a cell south
of where it stands); (5) interrupt the rescue: shoot the rescuer, retreat the raid, watch the half-set ladder; (6) live
with the pit prison for three days with a wounded captive, save and reload, and check a left-behind ladder.

**Conductor note 17:08 (owner's authority), handled:** reshot at root 11 and 20; count as bullets; NaN-accepting
AssertClose fixed (`SelfTest/Program.cs`): the full self-test then read 1243/1246, the three reds the known ones
(RiverSwitchFlip_weirWhiteWater, PitCapture_follows, LW1), so no check was hiding behind NaN; everything committed. NOT handled yet: retake the contrast sheet with every
hole occupied (draft them); say which build first_look_3b's seam is (unknown, so the seam line is unseen); shoot a covered
pit dug IN GRASS at root 20 (the cover shows as a bare grassless square on open ground).

## Next (in order)
1. Deploy (spikes def + fetch-fallen + prison + probes). Replay his story fresh at root 20: ordinary map, defenders with
   bows inside the doorway, tribal raid. Watch for: the rescue (message, chop, ladder), arrows on the rescuer, the flee,
   Capture-down from the lip, a warden feeding from the lip, a save/reload. Then GPT leads 5 and 6.
2. The depth look, the biggest visible gap (6 lines false): three real treatments on one view, every hole occupied,
   root 11 and 20, side by side in LOOK.md: (A) consistent oblique (far face 0.6 cell a metre, same scale as the sink, no
   0.62 clamp, opaque near lip, no black box outline); (B) strata cutaway (the far wall shows one band a metre, compressed
   into the opening; pawns kept inside the opening, darkened with depth); (C) shadow well (darkness and inner shadow by
   depth, pawns smaller and darker with depth). Items on a pit floor (logs, bodies) need the same treatment: the replay pit
   read as a log stockpile. Mind GPT lead 2: the drawn pawn and its clickable cell must agree.
3. Fix the three render bugs above (worn gear, south ladder, pawn under deck), then the ladder rails/state, the portable
   ladder's lean, the hung bridge look.
4. Run the four-fix probes; the covered pit in grass; the seam on the deployed build at root 11.

## Running count (only what was seen in game counts; root 11/20 unless said)
- pit_depth_ladder_legible: false — 4 m and 8 m alike (old contrast sheet); at r20 pits are dark squares
- pawn_height_ladder_legible: false — occupants drawn on the south lip, not in the hole (contrast sheet, bar_geared_pawn_climbs_out_r20_1)
- pawn_lowers_on_deeper_cell: unseen — no walk filmed
- pawn_rises_on_shallower_cell: unseen — no walk filmed
- pit_reads_as_hole: false — at r20 a dark outlined square, reads as a hatch as much as a hole (bar_ladder_state_legible_r20_1)
- pit_walls_have_visible_depth: false — one thin pale band on the north edge (same shot)
- pit_not_vanilla_trap: true — nothing like the spike trap at r20 (bar_ladder_state_legible_r20_1)
- pit_reads_at_size: unseen — pass 1 saw it only at root 7.2
- pit_occupant_below_floor: false — occupants drawn on the south lip (bar_geared_pawn_climbs_out_r20_1)
- pit_occupied_distinguishable: unseen — pass 1 only at root 7.2
- pit_trapped_reads_as_trapped: false — no wall shows above any occupant's head
- pit_covered_invisible: false — on open grass the cover is a bare grassless square (conductor, pass-1 shots 3/3b)
- pit_covered_seam_at_max_zoom: unseen — the build in first_look_3b is unknown; the widened seam not yet looked at
- ladder_state_legible: false — raised vs lowered differ by a few pixels at r11, nothing at r20; south ladder invisible
- sluice_gate_state_legible: false — the post moves visibly at r11, a few pixels at r20; water tint unchanged
- spikes_read_distinct: unseen — pass 1 only at root 7.2
- trench_wall_cover_shown: true — tooltip "Trench wall: blocks 44%" at 1 m, "blocks 74%" at 1.5 m (bars2_trench, read from the shot tooltip text)
- raiders_never_shelter_in_a_cage: unseen — not staged
- wall_ladder_rides_on_rails: false — no rails at any zoom (bar_wall_ladder_rides_on_rails_r11/r20)
- portable_ladder_leans_on_its_wall: false — upright on the lip at 2 m, a smudge at 4 m (bar_portable_ladder_leans_on_its_wall_r20_1)
- climbing_gear_reads_as_kit: false — a brown coil on the ground, nothing drawn worn
- geared_pawn_climbs_out: false — he does get out (634 ticks), but the BEFORE frame draws him on the lip, not on the floor
- jump_into_pit_lands_unhurt: unseen — Longjump into 2 m and 4 m: no injury; jump pack and creatures not tried
- geared_pawn_scales_built_wall: unseen — geared pawn crosses (531 ticks); the ungeared refusal not shot
- suspension_bridge_reads_hung: false — flat straight strips, no sag or cables
- pawn_walks_under_deck: false — the walker is drawn on top of the deck
- pit_cover_unlike_bridge: false — unlike a bridge, but its first half (cover passes for ground) is false
- digging_takes_hours: unseen — 3.8 game hours for 0.5 m by shovel (true half); raiders carrying fill not watched
- never_snared_standing (cannot): true — falls end on the floor, no snare tile (pass 1 fall, pass 2 replay)
- never_reads_as_building (cannot): false — the black-outlined dark square reads as a placed hatch

Count: 3 true, 17 false, 10 unseen.

## Between this and done
| kind | what | evidence | next observation |
|---|---|---|---|
| blocker | the depth look (6 false lines, never_reads_as_building) | r20 shots, old contrast sheet | 3 treatments side by side, every hole occupied, r11 + r20 |
| unknown | fetch-fallen and the bed-less prison in play | built, self-tested, never run | his story replayed fresh at r20 to the prisoner fed from the lip |
| unknown | spikes never trashed | def built, not deployed | the same replay |
| regression | none known | | |
| blocker | three render bugs (worn gear, south ladder, pawn under deck) | bars2 repros in pass2_progress.md | fix, reshoot r11/r20 |
| unknown | the four fixes | probes built, not run | ProofCliffTiming on a big dig, ProofCoverScan on a 20x20 deck, two maps |
| decision | rescue ladder frees colony prisoners | QUESTIONS.md 1 | his answer |
