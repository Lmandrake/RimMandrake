# FlowWorks Artisan, aspect 1 (pits and depth): progress

## Pass 4 (2026-11-07, 19:38-20:55): what I saw, what I changed
Weather: 1 dead game (native Unity crash right after a quick-test map generated, no managed exception, `bad_cpus=[2]`;
restarted, the rerun was clean), 0 dropped ssh, 1 deploy (bridge up in 35 s). Retired on the context gate.

**Landed (db0cfe2a12, pushed, deployed, partly seen):** pass 3's lost builder work redone by a subagent: all 8 review
findings (claim written only by the job that starts; downed bedless captives hand-fed from a touching lip, capture refused
with a reason when no lip touches; room-only food count; lip memo keyed by the prisoner's cell; climb-out ends at the wall
top; fallen list rebuilt per pocket; fetcher skips ladders down to a standing raid-mate; dead lords pruned, rescue has its own
JobDef `RM_RaiderRescueLadder`); one message when a raid's rescue ladder goes into a hole holding colony prisoners; the
assault's colony-damage exit held while a rescue is under way (postfix, AssaultColony only, capped 5,000 ticks, setting
`raiderRescueHoldsRaid`). Self-test: only the 3 known reds (LW1, RiverSwitchFlip_weirWhiteWater, PitCapture_follows).
None of this has been seen live yet: the story replay below never reached a rescue.

**Ladders printed down their wall (`Superdeep/RM_LadderDraw.cs`, art `Textures/.../Canals/LadderRig/`, cut by
`art_source/LadderRig/slice.py` from codex art): SEEN** (`shots\pass4\sheet_ladders_r11.png`, `first_look_*`). Lowered =
in the hole on fixed iron rails at the hole's drawn depth (`SectionLayer_RMExcavationWalls.ObliqueFaceAt`); raised = out on
the ground beyond its rim, bare rails left. Reads clearly at r11; at r20 side ladders are dotted lines and the south one was a
sliver -> made taller (`SouthAbove` 0.5): BUILT AND IN THE WORKING TREE'S DLL, NOT DEPLOYED, NOT SEEN.

**Climbing gear worn: SEEN** (`first_look_climbing_gear_worn_r8.png`): pack on the back, belt+coil from the front, all four
facings right. Pass 3 had replaced his KEPT ground sprite (ledger ruling cd19c72f, his words "belt/backpack type item of ropes,
little grappling hooks, climbing claw"): put back. Pushing textures needs the art ledger (`art.py install ... --file`, a
`script:` writer for mechanical art; a kept picture only moves by his ruling) or the pre-push guard refuses.

**Four fixes:** cover scan 0.30 ms on a 400-cover deck vs 71-120 ms flooding from every cover (early=399); cliff-mask full
rebuild 1.96 ms for a 900-cell hole after a reload (250x250 map); two maps: A's derive count held at 1 while B derived (global
10->11). The returned-prisoner grace across a reload: probe `Rivers.RM_RiverWorksProof.ProofReturnGuard("take:<id>")` /
`("read:<id>")` is in the deployed DLL, NOT RUN: capture a raider (or spawn a prisoner), take:id, save, reload, read:id
(want guarded=True watched=True). `ralph/live/four.py` (static_call passes NO argument for "": give every probe one).

**His story replayed once (`story3.sh 600 TribeRoughNeanderthal s4`, logs `Transient/ralph_fw/*_s4.out`): did NOT play.**
The raid entered from the NORTH edge, burned and bashed the compound's north wall, 5 of 6 died there; the last walked round
and fell through the covered pit in the south passage alone; no rescue (nobody left). The layout only works if the raid comes
from the south. AND the opened pit read as a flat grey box at r20 in evening light (`first_look_story_raider_in_pit_r20`)
where daylight staged pits read as dark holes. Unexplained: sprung-cover debris? spikes art? the light? Look first next pass.

**Phone:** `broaden` sent 20:47 with 5 images (ask `ralph/live/broaden4.md`); the answer lands at
`D:\ClaudeWork\rimmandrake\ralph_flowworks\gpt_help_pass004.md`. Read it first; play the 1-2 likeliest leads.

**Open items triage (subagent):** of 16, 10 fixed in code; open: PIT_RAIN headroom (aspect 2), PIT_SHOT_PROOF (harness),
SUSPENSION_GRATE fire (needs his ruling); needs eyes: PIT_SINK soil strip over a wall, SUSPENSION_UNDERPASS picture.

## Next (in order)
1. Deploy the working-tree DLL (south stub). Read gpt_help_pass004.md.
2. The story, made to happen: pick the raid's arrival (`jawa/fire_incident` raid with a spawn spot/edge if it has one — read
   its schema) or build the passage on the side the raid comes from; replay; watch for: the fall, the rescue ladder under
   arrows, the exit hold, the prisoner-hole message, Capture from the lip, a warden feeding from the lip. Then the open-ground
   variant (no walls, a covered pit line across the approach).
3. Explain the grey-box pit in the story frame (fetch `s1_w0*` shots of s4; compare daylight).
4. Bridge: no sag, catenary or floor shadow exists (deck = flat 1x1 linked tiles at FloorEmplacement; `SuspensionBridgeRecord.
   TryIndexOf` gives a tile's span index). Build the hung look; the l5 bridge/under-deck shots of this build are fetched,
   unjudged (`b2_l5_bridge_*`, `b2_l5_under_*`; the walk now goes south row -> north row).
5. Conductor's owed list (8:07 PM): ladder warning live (2); Crashlanded start has a bottle, "give patients water" day 1 (3);
   dig patch: digger eats, progress kept — `ladders5.py dig` (4); re-shoot the daylight depth contrast sheet r11/r20 after the
   eased 4/8 m cap (5); trench_wall_cover_shown hover shot (6).

## Running count (seen in game)
- pit_depth_ladder_legible: false — 4 m vs 8 m too close (pass 3); eased cap unseen
- pawn_height_ladder_legible: false — 0.5 m vs undug barely differs at r20 (pass 3)
- pawn_lowers_on_deeper_cell: unseen
- pawn_rises_on_shallower_cell: unseen
- pit_reads_as_hole: false — staged daylight yes, but the story's opened pit read as a grey box (s4 w060)
- pit_walls_have_visible_depth: true — far face rim to floor (pass 3 contrast, pass 4 ladders)
- pit_not_vanilla_trap: true
- pit_reads_at_size: true — 5x5 pits read as one place (sheet_ladders_r11)
- pit_occupant_below_floor: true — colonist in the 5x5 pit, legs behind the near lip
- pit_occupied_distinguishable: true
- pit_trapped_reads_as_trapped: true (2 m+, pass 3)
- pit_covered_invisible: true — sod before/after at r20 the same (look4, previous build)
- pit_covered_seam_at_max_zoom: true — faint darker rectangle at r11 (look4)
- ladder_state_legible: false — in vs out reads at r11; the south lowered ladder was a sliver (fix unseen)
- sluice_gate_state_legible: false — pass 2
- spikes_read_distinct: true — stakes visible in the open spiked pit at r20 and r11 (look4)
- trench_wall_cover_shown: true — tooltip numbers (pass 2); hover shot owed
- raiders_never_shelter_in_a_cage: unseen
- wall_ladder_rides_on_rails: false — rails seen on the north face; side walls dotted at r20, south fix unseen
- portable_ladder_leans_on_its_wall: false — side wall leans, north wall stands straight; too-short lies flat (true part)
- climbing_gear_reads_as_kit: true — worn, four facings, and the kept ground sprite (r8)
- geared_pawn_climbs_out: unseen under the new look
- jump_into_pit_lands_unhurt: unseen
- geared_pawn_scales_built_wall: unseen
- suspension_bridge_reads_hung: false — flat strip (look4); this build's shots unjudged
- pawn_walks_under_deck: false — never walked across (pass 3 script walked onto the deck row); fixed script's shots unjudged
- pit_cover_unlike_bridge: false — cover half true, bridge half not
- digging_takes_hours: unseen
- never_snared_standing (cannot): true
- never_reads_as_building (cannot): true

Count: 13 true, 11 false, 6 unseen.

## Between this and done
| kind | what | evidence | next observation |
|---|---|---|---|
| blocker | his story has never played end to end | s4: raid came from the north | a raid made to arrive at the pit |
| unknown | rescue fixes, exit hold, prisoner message, lip capture/feeding | deployed, never reached | the same replay |
| regression? | opened pit a grey box in the story | s4 w060 | daylight vs evening, cover debris on/off |
| blocker | bridge reads flat, no sag | look4 | build the hung look, shoot |
| unknown | returned-prisoner grace across a reload | probe deployed, not run | take/save/reload/read |
| decision | raised ladder drawn on the ground (side/near walls) | LOOK.md "my call" | his look |
