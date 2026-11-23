# Gimme Some Slack: Polish list

Polish improves play but is not part of passing 0.1.0. Each entry is moved here only with his confirmation, marked in the decision (owner, by card 2026-11-13).

*Empty at entry on 2026-11-13: no open judge gap sorted as Polish.* Candidate if he disagrees with the sort: g2's FlowWorks fallen-deck cord case (`gaps_sorted.md`).

- **The cord runs further into a rock hole before it disappears** (cord art only, never printed stub art). Owner, his walk of 2026-11-20 (`conversations/2026-11-20-1329-aab6064a.md` line 1814): *"The yellow cable should "go into" the black of the hole before disappearing a bit more than it does currently... that's just extending the cable art a little longer into the black before it's cut off and disappears in, don't use hard-printed stub art! They suck. (This is definitely polish for next version)"*

0.1.1 blind cycle 1 (`blind_challenge/cycle_1/lane2/faults.json`), moved to Polish by the steward RIMMANDRAKE_CONFIRM_GIMMESOMESLACK_CYCLE_ONE_EXIT_MET as the Conductor's delegated call (`--per-ruling RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME`), 2026-11-20:
- **RIMMANDRAKE_CLIP_SLACK_FALLEN_WIRE_TENTH_CELL_INTO_WALL** (MOD): a fallen wire's bend can clip up to 0.117 cell into a wall face in 15 of 5934 random walled lays (`LayFallen` samples walkability every 0.2 cell). The wire never crosses a wall; `fallen_span_on_ground` names no wall, and `cords_meet_walls_at_face` reds only a cord across a wall top. Stage 6 sees it live.
- **RIMMANDRAKE_NOTE_SLACK_DLL_HOSE_NAMES_ONLY_ALTITUDES** (HARNESS): five hose-named altitude constants from `_Shared/SlackGeometry/DrawOrder.cs` are compiled into the GSS DLL; no hose def, texture, class or drawing ships.
- **RIMMANDRAKE_SHARE_SLACK_TAP_SURPLUS_UNTESTED_IN_CALLER** (HARNESS): no check puts two taps on one victim; the shipped code shares the surplus and no bar names several taps.
- **RIMMANDRAKE_MISS_SLACK_PIPE_KIND_IN_BLIND_LANE_ONE** (HARNESS): the blind lane-1 scanner missed a `lineKind` pipe plant; repaired in the sitting and shown both ways.

The switch lamp (RIMMANDRAKE_LIGHT_SLACK_SWITCH_GREEN_RED_DARK_WHEN_UNPOWERED, 2026-11-20), the art judge's polish notes (`version/evidence/switch_light/judge_v1.json`, `judge_v2.json`); nobody fixes these:
- **Futuristic baked cyan** (ART): the Futuristic look's closed art carries its own cyan glow, which still shows on an unpowered switch beside the dark lamp.
- **Modern two reds** (ART): on the Modern look the red lever sits beside the red lamp when the switch is open; still readable.
- **Dark lamp at far zoom** (ART): at 36 px per cell the unlit lamp is nearly invisible on the dark bodies (Industrial, Futuristic); the lit states still read.
- **Scrapper halo cast** (ART): the green halo takes a yellow cast over the Scrapper look's copper bar at 112 px per cell.

Ticket sweep of 2026-11-22 (RIMMANDRAKE_SWEEP_SLACK_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE): each ticket below failed test 1 of §Touching code has a cost (no broken promise in ordinary play, no failure that happened, no red test that shows misbehaviour) and was dropped `not worth the touch`. One line each; nobody fixes these. Page: `ticket_sweep_2026-11-22.md`.
- **CORD_PLANNER_MEASURE_ASTAR_EXPANSIONS** (TOOL): an A* expansion counter for the hose replay harness; a measurement, no failure.
- **GSS_FRAME_GARBAGE_SHRINK_HALF_MEG_LEFT** (MOD): CordBuilder.Build allocates ~0.45 MB per AsyncLay frame at 8 lattices; the no-delay bar passes in game.
- **RIMMASTER_POLISH_GSS_CORD_LEFTOVERS_AFTER_APPROVAL** (ART): Scrapper lead S-bend, 5-12 degree plug-join slopes, the r3_13 crossing, the faded wall plug; each changes the look he approved (put on this list 2026-11-19).
- **RIMMANDRAKE_COVER_GSS_CALLERS_FOUR_PLANTS_WALKED_PAST** (HARNESS): blind-cycle caller and patch plants no offline suite reds; the in-game rows decide those bars.
- **RIMMANDRAKE_TRIM_GSS_LAY_COST_SLICES_ROSE_A_THIRD** (MOD): the cold lay costs ~690 ms over ~71 Builds after 0416599c69; the no-delay bar passes.
- **RIMMANDRAKE_ALIGN_GSS_SHARP_ROW_READS_CUT_END_CELL** (HARNESS): lane 1's sharp-turn row reads windows the bar's instrument does not count.
- **RIMMANDRAKE_GUARD_GSS_RESTRING_TICKS_NAN_NEVER_IN_GAME** (MOD): AerialMath.RestringTicks(NaN) is int.MinValue and (+inf) is 0; the caller feeds ConstructionSpeed, never NaN or inf.
- **RIMMANDRAKE_TRIM_GSS_FALLEN_WIRE_COILS_OUTGROW_CABLE** (MOD): 13 of 1500 seeded fallen wires draw over 2x their cable; no bar promises length.
- **RIMMANDRAKE_PROVE_GSS_GEOMETRY_RAN_COUNT_IS_ONLY_TELL** (HARNESS): T_CORD_GEOMETRY_OFFLINE stays rc 0 when --geometry is dropped; only its check count tells.
- **RIMMANDRAKE_EXERCISE_GSS_CORD_GUARDS_THREE_PLANTS_SURVIVE** (HARNESS): three cord-lay guards can be weakened with T_CORE and T_CORD_GEOMETRY_OFFLINE green.
- **RIMMANDRAKE_REPIN_GSS_ASYNC_FAULT_CAP_FIFTY_SEVEN_USED** (HARNESS): SliceGateChecks asserts builds5 < 60 with ~57 used; never red on record.
- **RIMMANDRAKE_TIGHTEN_GSS_FALLEN_WIRE_WALL_CHECK_HALF_STEP** (MOD): LayFallen checks every 0.2 cell, draws every 0.1; up to 0.114 cell inside a wall, hidden under wall art (same family as the 0.1.1 cycle 1 line above).
- **RIMMANDRAKE_SPLIT_GSS_DLL_HOSE_DRAW_ORDER_SHARED_TABLE** (HARNESS): hose-named altitude members compiled into the GSS DLL from the shared DrawOrder.cs (same as the cycle 1 line above).
- **RIMMANDRAKE_GUARD_GSS_NOHOSE_FLEXIBLE_PIPES_CLAUSE_UNMUTATED** (HARNESS): T_NO_HOSE's 'flexible pipes' clause has no self-mutant.
- **RIMMANDRAKE_SCAN_GSS_ABOUT_TEXT_HOSE_CLAIMS_UNREAD** (HARNESS): T_NO_HOSE does not read About.xml; the shipped About text names FlowWorks as the home of the hoses, which is true.
- **RIMMANDRAKE_SEE_GSS_DLL_HOSE_NAMES_HIDDEN_IN_TAILS** (HARNESS): T_NO_HOSE's byte scan misses LayParams.Hose and CordKind.Hose; no hose ships.
- **RIMMANDRAKE_MEASURE_SLACK_LIVE_END_PARITY_COPY_AGAINST_GAME** (HARNESS): parity of the Python live-end copy against the game is UNMEASURED; the in-game live-end rows decide the bars (P_B3_whip_live_ends PASS, visit 3).
- **RIMMANDRAKE_EXPLAIN_SLACK_DECK_SHOCK_COUNTED_VICTIM_UNMARKED** (SITE): once in six trials on 2026-11-17 the shock counter rose with no hediff on the deck colonist; not seen again (P_SC_shock_reach_deck_cord_per_value PASS, visit 3).
- **RIMMANDRAKE_TRACE_TURRET_TICK_EXCEPTION_ON_FULL_LIST_WALK_SAVE_LOAD** (NOT OURS): one exception on the first tick of his full list; the throwing frame is LargePawns.LargePawnsMapComponent.GetLargePawns (a corrupted Dictionary of the third-party mod neku.largepawns); FlowWorks is only a prefix on the stack (`D:\ClaudeWork\rimmandrake\gss_walk_stage\load_walk_log_tail.txt` line 4228).
- **Mast head over a plant over 4 cells tall to its south** (MOD, journal Questions 4 (b)): unreachable with vanilla plants (the tallest is 3.0 cells; `selftest_gss_pole_south_draws_front.py`).
- **Restyle reach menu says "1 lamps"** (MOD, polish): the All connected count reads "8 pieces, 1 lamps" with one lamp (ConduitStylePicker.ReachMenu); grammar only.
- **The style reach menu has no on-screen capture** (HARNESS): screenshot_cell_rect renders the map without UI, so the live check reads the menu's labels (style_reach_live.py R1) instead of a picture of the menu.
