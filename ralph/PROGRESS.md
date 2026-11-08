# FlowWorks Artisan, aspect 1 (pits and depth): progress

## Pass 7 (2026-11-08, ~09:55-10:35Z): rain fixed, the archers' target bug fixed, the story staged three ways
Weather: 3 crashes of game A (one native crash in map generation, one Mono JIT crash in vanilla `StunHandler.StunFor`
mid-raid, one at load) and 1 failed start, all with `bad_cpus=[2]`; 0 dropped ssh. Retired on the context gate (258k).
Shots: `D:\ClaudeWork\rimmandrake\ralph_flowworks\shots\pass7\` (pass 6's moved to `shots\old\pass6`).

**Landed (built, DLL + .srchash committed, deployed, live):**
1. Rain (QUESTIONS 4, my call B): `rainFillPerPulse` 0.1 -> 0.002. The old rate was 0.5 m per game hour of rain (every vanilla
   rain weather has rainRate 1), so any pit trap flooded in one shower (s9). Now ~0.24 m per rain day. Live setting read 0.002;
   the story pits in s12-s13 read fill 0 throughout.
2. `RM_CliffMelee` threat rule: a held pawn stays an auto-target only after a REAL attack (`lastAttackTargetTick`), not after
   merely picking a target (`lastEngageTargetTick`, which `JobGiver_AIFightEnemy.UpdateEnemyTarget` stamps on every pick).
   s11 showed why: the trapped raider was refused 72 swings yet stayed a "threat", so 5 archers on the lip shot him while his
   rescuer chopped wood, fetched it and set a ladder 3 cells away (ladder in at +3960, rescuer dead only at +4680). Deployed
   for s12+; not yet seen in a run where a rescue was under way.

**The story, three runs on this build** (`story3.sh`, logs on Steve `Transient/ralph_fw/watch_sN.out`; summarise with a
regex over the `t+` lines, the raw lines are 1.5k chars each):
- s11 (raid from the map edge, 400 pts): every raider took vanilla's trash-a-distant-building job on the staged colony's only
  buildings (its walls) from 70 cells out. One (Hippo) came up the passage and fell; Gaxo chopped, took a portable ladder and
  set it on the south wall (seen, `s11_rescue_ladder_set_south_wall_64px.png`); Hippo climbed out ~1,200 ticks later and was
  shot; 3 raiders dead, 2 fled. All 8 defenders lived. No prisoner left. Closest to his story so far.
- s12 (spawn 18 cells south of the passage mouth, 400 pts = 4 Neanderthals): the first raider fell through at once and died
  in the pit (arrows on the way in, then spikes); with the hole open the passage is truly blocked, so the other three bashed
  walls for 3,000 ticks and left. Correct behaviour, not his story.
- s13 (800 pts): a mixed 15-pawn raid (ancient soldiers and a militor joined) broke in through the compound walls; nobody fell.
- s14 (600 pts, spawn 6 cells south of the mouth, NEW `FW_PERIM=20` perimeter wall along the passage mouth's row): **the
  first two fell through the cover together** (Trogo held from t240, Cale from t720), the raid stayed, Orange chopped and
  set a rescue ladder (in at t2400, ~1,700 ticks after the second fall, most of it chopping out of bow range), both climbed
  out: Cale was shot dead at the lip, Trogo escaped with the raid; Orange (the rescuer) was never hit. Raid driven off (1 dead),
  no prisoner left. Pit dry. Cliff melee refused 610 swings. His story up to "driven off", but the rescue beat the archers.
With the perimeter wall the trap springs as he wrote it. What stands between s14 and his ending is the rescue race: 5
tribal short bows never touched a rescuer who was out of range while chopping and spent only ~240 ticks at the lip setting the
ladder. Open question for pass 8, look before tuning: is ~240 ticks at the lip too quick for a makeshift ladder (his story has
defenders "peppering them with arrows while they try"), or are 5 short bows simply too few? Try first with the colony's own
3 colonists armed (a player defends with everyone), then judge the ladder-setting time.

**Seen, not changed:**
- `pit_covered_invisible`: pass 6's dark south row did NOT come back (s11 undug vs covered at 64 px: the covered squares are
  2.6% darker, `s11_undug_vs_covered_passage_64px.png`). Two hairline seams do show at root 7.2, because the bridge widens the
  camera's minimum to 0.5 so `RM_PitCoverLookMath.SeamStrength` applies its closest-zoom floor (0.9) up to root 13. A player
  at 64 px on a 4K screen (root ~17) gets none; on a 1440p screen 64 px IS the closest zoom, where the seam is meant to show.
  Kept Proven (no regression shown).
- Open item triage (subagent, `D:\ClaudeWork\rimmandrake\ralph_flowworks\pass7\items_triage.md`): of 17 items, 8 fixed in
  code, 2 really open (a harness false pass; grate fire, aspect 2), 7 need a live look (deep stone letter; soil strip over
  wall; capture-down from the lip; bridge art = suspension_bridge_reads_hung; underpass shot = pawn_walks_under_deck; river and
  flood rows, aspect 2).
- `jump_into_pit_lands_unhurt`: every floater and jumper race tagged in `Patches/Canals/FlowWorks_PitTravel.xml` comes from
  other mods (RM_Bulloo, RSW_*), none on game A's small list, and CLAUDE.md forbids live flight. Only the jump pack/Skip in
  AND out can be shown on this list; the floater clause needs a list with one of those mods (owner's call or another tier).

**In flight at retire:** an rm-builder subagent in a worktree is writing the hung suspension bridge (`RM_SuspensionHang.cs`,
treatments 0/1/2 by `jawa/static_call RimMandrake.FlowWorks.Pits.RM_SuspensionHang SetTreatment`, deck redrawn over pawns
beneath) from `hung_bridge_pass6\PROGRESS.md`, building with `WINBUILD_ROOT=D:\ClaudeWork\rimmandrake\build_fw7_bridge`. Its
commit lands on a `worktree-agent-*` branch (`git branch -a | grep worktree`); merge its SOURCE, rebuild the DLL here, deploy.
If no branch exists, look for uncommitted source in `.claude/worktrees/agent-*` before rerunning the brief.

## Next (in order)
1. Story again with `FW_PERIM=20 FW_SPAWN=gx,p-6` (s14's layout) and the defenders armed as a player would; frames of the
   rescue ladder going in. If fallen remain after the raid leaves: `python.exe ralph/live/capture.py <colonist> <x> <z>`
   (right-click capture from the edge), and look for the `RMFlow_RaidLeftTrapped` message.
2. Merge and deploy the hung bridge; `ladders5.py bridge` at root 7.2 and 11 for the three treatments side by side in LOOK.md.
3. `bash ralph/live/look7.sh p7` (written, never run): depth sheet in the default look with occupied 3x3 pits at 4 m and
   8 m, `walk7.py` graded walk 0-4 m and back with the real drawn sink per stop, ladders/portables/gear at root 7.2 and 11.
   Judges pit_depth/pawn_height/lowers/rises/occupant_below_floor/trapped/ladder_state/portable/rails/gear in one sitting.
4. Jump pack in and out of a 2 m pit with hediffs read (`bars2_pit.py jump` has the in half).
5. GPT broaden call (none in passes 6-7; required before DONE.md) with the 64 px shots.
Owed from earlier: trench cage staging, no-gear wall control, dig hours + raiders carrying fill, four.py (grace across a reload).

## Running count (seen in game; look bars judged at ~64 px where re-shot)
- pit_depth_ladder_legible: false (pass 3 at r20); unjudged at 64 px
- pawn_height_ladder_legible: false (pass 3 at r20); unjudged at 64 px
- pawn_lowers_on_deeper_cell: unseen
- pawn_rises_on_shallower_cell: unseen
- pit_reads_as_hole: true (s12 open spiked pit at 64 px)
- pit_walls_have_visible_depth: true
- pit_not_vanilla_trap: true
- pit_reads_at_size: true
- pit_occupant_below_floor: false (true at 2 m, s11 at 64 px; the 4 m 3x3 case drew on the south lip, pass 2)
- pit_occupied_distinguishable: true
- pit_trapped_reads_as_trapped: unseen
- pit_covered_invisible: true (s11 pair at 64 px; hairline seam only at a bridge-only zoom)
- pit_covered_seam_at_max_zoom: true
- ladder_state_legible: false (south fix unseen)
- sluice_gate_state_legible: true
- spikes_read_distinct: true
- trench_wall_cover_shown: true
- raiders_never_shelter_in_a_cage: unseen
- wall_ladder_rides_on_rails: false
- portable_ladder_leans_on_its_wall: false (s11 rescue ladder leans on the south wall at 64 px; too-tall control unseen)
- climbing_gear_reads_as_kit: false (ground kit)
- geared_pawn_climbs_out: true
- jump_into_pit_lands_unhurt: unseen (out, and floaters: not on this mod list)
- geared_pawn_scales_built_wall: unseen (no-gear control owed)
- suspension_bridge_reads_hung: false (being built at retire)
- pawn_walks_under_deck: false (draw order; being built at retire)
- pit_cover_unlike_bridge: true
- digging_takes_hours: unseen (fill + raiders carrying fill owed)
- never_snared_standing (cannot): true
- never_reads_as_building (cannot): true

Count: 14 true, 9 false, 7 unseen (of 30).

## Between this and done
| kind | what | evidence | next observation |
|---|---|---|---|
| blocker | his story has never reached "prisoners in a tidy prison" | s14: two fell, rescue ladder in, both climbed out, raid driven off | s14 layout with armed defenders, then capture.py |
| unknown | archers now shoot the rescuer, not the trapped | s11 (before the fix) | a run where a rescue is under way |
| unknown | the withdrawing-raid message | never fired (no raid left anyone trapped) | a run that leaves a raider in the pit |
| blocker | bridge reads flat; pawn drawn over the deck | builder in flight | merge, root 7.2 shots |
| unknown | ten look bars at 64 px | look7.sh written | run it |
| decision | rain rate (QUESTIONS 4) | 0.5 m/h was the old rate | his word on 0.24 m/rain day |
| decision | floaters/jumpers not on game A's list | FlowWorks_PitTravel.xml names only other mods' races | owner: accept as a limit, or a tier with one of them |
