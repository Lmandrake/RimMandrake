# FlowWorks ticket sweep, 2026-11-22

Item `RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE` (detached BENCH run). His words (2026-11-22 about 3:05 PM PST, phone typos corrected): *"Find. Adjudicate. Eradicate the stale. Merge the modern. Apply/build them RIGHT NOW if they're valuable, after adjudicating if they are part of the current or next version."*

Evidence folder (per-item verdicts, batches, run logs): `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_20261122\FlowWorks\` (`all_v.jsonl` holds one line per item: class, one line of evidence, cause, files, his words).

## Was there an earlier sweep of FlowWorks?

None on record for FlowWorks alone. The whole-queue trash sweep of 2026-11-05 (`D:\ClaudeWork\rimmandrake\conductor\triage_20261105\`) classed waiting items of every mod and touched some FlowWorks items; the pipeline ticket triage of 2026-11-18 (`pipeline_ticket_triage_20261118.md`) covered pipeline tickets, not the mod. No ledger item named a FlowWorks sweep before this one.

## How the open set was found (measured)

- The ledger replayed (`model.replay()`) holds 9,700 items; 1,949 are open (proposed, ready, doing, built, validated).
- An open item was a candidate when its id, title, prose or notes name FlowWorks or an old name (RiverWorks, River Colors, ManyWaters, `mandrake.rm.flowworks`, `src/RimMandrake/FlowWorks`), or name FlowWorks-only def or class names (1,853 names read from `src/RimMandrake/FlowWorks/Source`, `Defs`, `Patches`, less the names other mods also define), or carry a FlowWorks sub-system word (pit, canal, hose, sluice, drawbridge, ladder and the like) together with one of those. **471 candidates**; 249 name FlowWorks in the id or title; 268 have prose. The Conductor's rough count was 281 open item files naming FlowWorks.
- Five fresh Opus judges read every candidate with `rimflow show` (prose and history to the end) and checked origin with `git log`; one line each. They judged **417 about FlowWorks** (368 FlowWorks, 49 shared pipeline items that name it) and 54 not about it (another mod's item that names FlowWorks in passing; left alone).
- A second pass read `git log` against every KEEP item: three judge verdicts were wrong and are corrected here (a fix already on origin under another name).

## Count per class (the 417)

| class | count | act |
|---|---|---|
| DONE | 153 | dropped with `DONE: <commit or passing check>`; `close` refuses them because their old per-item live rows are owed (see below) |
| DUPLICATE | 24 | superseded into the ticket of their cause |
| STALE | 39 | dropped with the later ruling, version or item named |
| DEAD | 4 | dropped |
| NOT_WORTH | 53 | dropped with `not worth the touch: <why>`; one line each on `version/polish.md` |
| NEEDS_HIM | 8 | kept; listed below |
| KEEP_CURRENT | 93 | kept for 0.1.0, merged where a cause or file group is shared |
| KEEP_NEXT | 42 | kept for 0.2.0, merged likewise |
| OTHER | 1 | a shared item the judges left to its own mod |

Not acted on, on purpose: `PIT_SUPERDEEP_COLLAPSE_1` (DONE, but the root `CLAUDE.md` and `standing_rulings.md` cite its live path; closing it moves the file, so it waits for the Conductor to move both pointers); three items in `doing` under live runs (`RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_THREE_RUN_TWO`, `RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD`, `RIMMANDRAKE_RUN_TARGETED_CHECKS_PAST_UNBUILT_MUST_SHOW_LINES`); the routing item of his walk and this item.

Why DONE items are dropped, not closed: `rimflow close` refuses an item whose old acceptance rows (A2 L2 and the like, the per-item ladder of the retired pipelines) were never recorded, and only his word or the Conductor window may close past that. The work is on origin; FlowWorks 0.1.0 is judged by its own test table and his walk. Each drop reason starts `DONE:` and names the commit or check.

## The modern tickets that remain

### Merged by this sweep (one cause or one file group each)

| ticket | version | what |
|---|---|---|
| `RIMMANDRAKE_PRUNE_FLOWWORKS_DRAWBRIDGE_TO_HIS_NOV_THIRD_RULINGS` | 0.1.0 | FlowWorks drawbridges: carry out his 2026-11-03 rulings (one leaf only, no plank stack, see-through gate) and the four old drawbridge faults (5 old tickets) |
| `RIMMANDRAKE_MEND_FLOWWORKS_HOSES_SIX_OLD_FAULTS_ONE_SYSTEM` | 0.1.0 | FlowWorks hoses: six old faults in one system (small pump lays unconnected, no replan when walled, stale overdraw, style drift and lost links after reload, levelling budget starves the back row) (6 old tickets) |
| `RIMMANDRAKE_TEACH_FLOWWORKS_BRIDGE_TOOL_HIS_THREE_WALK_ASKS` | 0.1.0 | FlowWorks suspension bridge tool: his three asks from the 2026-11-20 walk (Choose style on built bridges, span over ruined bridge scrap, say the drag starts on the landing) (3 old tickets) |
| `RIMMANDRAKE_FIX_FLOWWORKS_RAIDER_LADDERS_FOUR_FAULTS_ONE_PATH` | 0.1.0 | FlowWorks raiders and ladders: four faults on one path (leaning ladders skipped, the chop never lands, climber def names that left, no short ladder tried at a 4 m pit) (4 old tickets) |
| `RIMMANDRAKE_RESCUE_FLOWWORKS_STRANDED_COLONIST_REACHABLE_LADDER` | 0.1.0 | FlowWorks pit rescue: a colonist stranded in a pit reads untrapped, and the rescue picks a spare ladder nobody can reach (2 old tickets) |
| `RIMMANDRAKE_REPAIR_FLOWWORKS_WRONG_CHECKS_SIX_OLD_TICKETS` | 0.1.0 | FlowWorks checks that are wrong: six old tickets (fuzz float tolerance, lake floor skips height, idle-pulse settle, pond arms split, pit shot passes on another target, plot grid off the map) (6 old tickets) |
| `RIMMANDRAKE_MEND_FLOWWORKS_LIQUID_RULES_FIVE_OLD_DEFECTS` | 0.1.0 | FlowWorks liquid rules: five old defects (shut sluice seals its whole square, deep sand reads as fresh water, bottle refuses a small pond, fuel sap never ignites, colonists ignore liquid spill filth) (5 old tickets) |
| `RIMMANDRAKE_FINISH_FLOWWORKS_RIVERS_PLACERS_EIGHT_OLD_TICKETS` | 0.1.0 | FlowWorks rivers and placers: eight old tickets (swept pawn stuck mid-river, river colours, weir catch and look, panning, placer refill, sluice box wash and its sideways art) (8 old tickets) |
| `RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS` | 0.1.0 | FlowWorks pit prison capture: three faults (prisoner flag backslides, warden downed beside the held raider, held raider read free one square out of a 4 m trench) (3 old tickets) |
| `RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_MAP_THREE_TICKETS_ONE_TOOL` | 0.1.0 | FlowWorks review map: three old tickets on one tool (signs over unbuilt scenes, 39 things still unshown, stations with no hose lead-out) (3 old tickets) |
| `RIMMANDRAKE_PROVE_FLOWWORKS_NINE_LIVE_ROWS_OWED_ONE_VISIT` | 0.1.0 | FlowWorks: nine built behaviours still owe one live row each; run them in one in-game visit (9 old tickets) |
| `RIMMANDRAKE_REPAIR_FLOWWORKS_HARNESS_SEVEN_RED_OR_BLIND_ROWS` | 0.1.0 | FlowWorks validation harness: seven rows red or blind for harness reasons (hose gate on SteveDesktop, rain E6, site hold, slime rows tier, fuel moat mod, sticky limitless, W8 edge on canary) (7 old tickets) |
| `RIMMANDRAKE_BUILD_FLOWWORKS_THIN_FILM_WETTING_FOR_ZERO_TWO` | 0.2.0 | FlowWorks 0.2.0: build wetting as the thin film (two squares damp beside a canal, the wetness probe, the downhill garden spill), after the one-state design (3 old tickets) |
| `RIMMANDRAKE_BUILD_FLOWWORKS_FOUNTAIN_LOOP_ART_FOR_ZERO_TWO` | 0.2.0 | FlowWorks 0.2.0: the fountain that pumps its own rain, and its art pick (2 old tickets) |
| `RIMMANDRAKE_PIN_FLOWWORKS_FOUR_UNWATCHED_LAWS_FOR_ZERO_TWO` | 0.2.0 | FlowWorks 0.2.0: pin four laws no test watches (toss range and relight, fetch fire window and key, drill power when off, coating on colonists) (4 old tickets) |
| `RIMMANDRAKE_REDRAW_FLOWWORKS_FOUR_PLACEHOLDER_ARTS_FOR_ZERO_TWO` | 0.2.0 | FlowWorks 0.2.0: four placeholder or borrowed arts (gravel pile, geyser plume bubble, Modern reel tail colour, style icons in every look menu) (4 old tickets) |

Also merged into existing modern tickets: `MODERN_RED_LEFTOVERS_REDRAW_TODAYS_LOOK` into `RIMMANDRAKE_REDRAW_MODERN_PIPE_AND_SPRINKLER_THEY_READ_PLASTIC_FUTURISTIC` (a walk finding); `FLOWWORKS_GUARDS_FIX_THREE_RED_SELFTESTS` into `RIMMANDRAKE_GUARD_STATIC_GAME_STATE_THREE_NEW_CACHES_UNREVIEWED`; `SWALE_CANAL_ART_REFERENCE_1` into `RIMMANDRAKE_REBUILD_SWALE_AS_SOAKING_FLOOR_NOT_FURNITURE`; `RIMMANDRAKE_LINE_PITS_WITH_FLOORS_AND_WALLS_ROCK_FREE` into `RIMMANDRAKE_DESIGN_PIT_FLOOR_SOILS_FOR_GROWING_RIVER_MUD_IS_RICHEST`. His words on every merged ticket are carried into its successor (prose or a note).

### The eleven findings of his walk of 2026-11-22 (modern already; the routing run sends them to fixers)

- `RIMMANDRAKE_ASK_GPT_HOW_TO_DRAW_STEPPED_PIT_FLOOR_HE_COULD_NOT_READ_IT`
- `RIMMANDRAKE_DESIGN_PAWN_IN_LIQUID_LOOK_WATER_SHEET_IS_A_MISTAKE`
- `RIMMANDRAKE_DESIGN_PIT_FLOOR_SOILS_FOR_GROWING_RIVER_MUD_IS_RICHEST`
- `RIMMANDRAKE_FADE_EVERY_PIT_COVER_TRANSPARENT_OVER_A_PAWN_LIGHTEN_PLEASED_HIM`
- `RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR`
- `RIMMANDRAKE_HIDE_WATER_OVER_EAST_WEST_SLUICE_GATE_STATION_SEVEN`
- `RIMMANDRAKE_LET_PAWN_WALK_UNDER_PLANK_COVER_BRIDGES_ALREADY_ALLOW_IT`
- `RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD`
- `RIMMANDRAKE_REDRAW_FLOWWORKS_TANKS_THREE_STYLES_ONLY_SCRAPPER_READS_RIGHT`
- `RIMMANDRAKE_REDRAW_MODERN_PIPE_AND_SPRINKLER_THEY_READ_PLASTIC_FUTURISTIC`
- `RIMMANDRAKE_REMOVE_WHITE_FRAMES_AT_EVERY_WATER_EDGE_HE_SAW_THEM_EVERYWHERE`

### Kept as they stand (already one cause each; each got a sweep note with its version)

| ticket | version | title |
|---|---|---|
| `DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD` | 0.1.0 | Clicking the raise/lower button appeared to do nothing for the owner in game 2026-11-03. Code reads as an order waiting for a colonist at the winch (R |
| `DRAWBRIDGE_GATE_BUILD_SEE_THROUGH_DOOR` | 0.1.0 | Drawbridge build spec 2026-11-04, part 3: option B gate frame (posts + lintel, all widths); interior transparent like a doorway, not black; winch and  |
| `DRAWBRIDGE_LEAF_PRUNE_NO_TWINS_NO_PILE` | 0.1.0 | Drawbridge build spec 2026-11-04, part 2: remove two-leaf drawbridges (SplitLeaves to one leaf; a span over the max leaf is not a drawbridge, ordinary |
| `DRAWBRIDGE_LOWER_FIX_LIFTS_OCCUPANTS_BENEATH` | 0.1.0 | [MINOR] Lowering a drawbridge promotes occupants beneath it onto the deck |
| `DUG_SUBSTRUCTURE_PROBE_SURVIVES_UNDER_WATER` | 0.1.0 | Digging through ancient substructure leaves terrain BrokenSubstructure at d6/f6 (full of water) and a wall is accepted there; seen only on test-drive  |
| `PAWNTWEENER_DIAGNOSE_ROOT_NRE_ON_HOSE_SAVE` | 0.1.0 | Session ee0fbaa8: 'Root level exception in Update()' NRE 100x from log line 36595, on the RM_fw_hose_proof_20261106122151 load: Verse.PawnTweener.Twee |
| `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP` | 0.1.0 | Raiders path around or breach a trench; jump-pack raiders cross; ladders pre-built for shallow pits; sieges unchanged |
| `RIMMANDRAKE_CHECK_SHOOTING_RULE_OFF_PICKS_FARTHER_PIT_FOE` | 0.1.0 | Superdeep shooting rule OFF: the shooter picks a farther target than the nearer pit enemy; MOD or expectation unknown |
| `RIMMANDRAKE_CLAIM_FLOWWORKS_MUST_SHOWS_FOUR_LEFT_BARE` | 0.1.0 | FlowWorks: 4 validated must-show lines no component claims (drained_hole_is_a_prison, geyser_pit_is_a_hot_tub, liquid_coating_washes_off, toss_flame_f |
| `RIMMANDRAKE_DECIDE_MOAT_RAID_BAR_TEXT_SAYS_D4_SCENE_NEEDS_SIX` | 0.1.0 | FlowWorks: the scenario text of bar moat_raid_sequence says a D4 moat, but a drained 2 m moat reads NotHeld (the prison rule starts at 3 m) and the pa |
| `RIMMANDRAKE_FIX_MOD_SETTINGS_FIELD_STATIC_CLASS_TRAP` | 0.1.0 | jawa/mod_settings_field throws on a static settings class. Live 2026-11-12: typeName=RimMandrake.FlowWorks.Sheet.RM_SheetSettings field=sheetOverflowE |
| `RIMMANDRAKE_LAUNCH_CODEX_REVIEWS_OF_MOD_CODE_AND_ART` | 0.1.0 | Tonight, on his word of 2026-11-20: launch Codex reviews of mod code (Gimme Some Slack 0.1.1 fixes, FlowWorks pits) and of the art sheet; never pipeli |
| `RIMMANDRAKE_LIST_FLOWWORKS_SHALLOW_OPACITY_SO_SECTION_RESET_REACHES_IT` | 0.1.0 | FlowWorks settings: the shallow under-liquid opacity slider is drawn but not listed in its section, so section reset and search miss it |
| `RIMMANDRAKE_READ_FLOWWORKS_WALK_BRIEF_ARRIVAL_TWO_BEFORE_STAGING_HIS_WALK` | 0.1.0 | Read design/concepts/FlowWorks/version/walk_brief/arrival_2.md before staging his FlowWorks 0.1.0 walk; then open it for him |
| `RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT` | 0.1.0 | Rain fills a 4 m open pit to the brim in one night (~0.5 m/h); the prisoner swims out |
| `RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY` | 0.1.0 | A look picked on one element of a water line does not spread to everything on that line: the pipe's Choose style restyles only pipes of the same def ( |
| `RIMMANDRAKE_SWEEP_OWNER_ONLY_TEXT_LEFT_AFTER_FIVE_ACTS` | 0.1.0 | After the five-acts ruling, read each remaining owner-only phrase and open it to the Conductor or say why it stays: the art_guard pre-push check over  |
| `RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR` | 0.1.0 | Tier gimmesomeslack_flowworks: the scenes block logs 'ThingsOfDef of MinifiedThing' (no stack); Z_log_budget FAIL there, clean on tier gimmesomeslack |
| `RIMMANDRAKE_VETO_DUPLICATE_PICKUP_ACROSS_SEALED_PIT_DROPS_HAUL` | 0.1.0 | FlowWorks: vanilla's duplicate pickup retargets a haul at a stack in a sealed pit (raised ladder) within 8 cells; the path errors, the carried stack i |
| `TIMBER_WINCH_FIX_POWERS_STEEL_BRIDGE` | 0.1.0 | [MINOR] A timber winch powers a steel drawbridge without electricity |
| `ABSOLUTE_DESCENT_FIX_MISSES_DECK_SHOVE` | 0.2.0 | [MINOR] Absolute-mode descent detection misses falls from a deck over the same excavation |
| `AQUATIC_WATER_BREATHING_GENE_1` | 0.2.0 | Design and build a real water-breathing mechanism (gene or hediff) for the 4 aquatic xenotypes currently missing one entirely |
| `BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND` | 0.2.0 | Each biome names its stones; basalt for volcanic biomes |
| `DIG_RIG_BUILD_BUCKET_OVER_THE_PIT` | 0.2.0 | v2: a buildable dig rig (winch-and-bucket frame over a pit, operated by a colonist) that digs past the 2 m colonist cap; design start: design/RimMandr |
| `DROWNING_ESCAPE_FIX_READS_DECK_ABOVE` | 0.2.0 | [MINOR] Drowning escape checks use the deck above a floor-band pawn |
| `EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES` | 0.2.0 | RM_MapComponent_Excavation (mandrake.rm.flowworks) costs 0.87 ms/tick mean with 158-172 ms single-tick spikes on the 325x325 RM_PerfSite map, the larg |
| `GRAVSHIP_LOCKED_FIX_ENGINE_TURNS_THEM_ANYWAY` | 0.2.0 | 14 non-square buildings say rotatable=false, but a turned gravship turns them anyway (Gravship.GetPlacementValues forces shipRotation on a non-square  |
| `INDUSTRIAL_RUINS_FIX_HIDDEN_EH_DEPENDENCY` | 0.2.0 | [MINOR] Default industrial progression requires an undeclared extra mod |
| `LIQUID_INDUSTRY_SETPIECES_1` | 0.2.0 | Found industrial liquid works via the shared scatterer: desal, detox, tar refinery, pumping station — wreck-tier, never player-buildable in campaign |
| `REFUSED_HANDOVER_DRAIN_FIX_PUDDLE_OVERSTAYS` | 0.2.0 | Refused handover leaves a puddle on a dug square forever |
| `RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY` | 0.2.0 | Black rain fills no moat or tank; owner: a rare chance to fill both |
| `RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION` | 0.2.0 | FlowWorks dig interface: design one consolidated UI for dig, fill, repair and the rest |
| `RIMMANDRAKE_DESIGN_FLOWWORKS_WATER_WAVES_FOR_THE_NEXT_VERSION` | 0.2.0 | FlowWorks 0.2.0, Divergent: moving water (waves, ripples) as a function of depth, designed after the 0.1.0 colour and clarity target is picked. Never  |
| `RIMMANDRAKE_DESIGN_MELEE_SHOVE_INTO_PIT_CONTEST_FLOWWORKS` | 0.2.0 | FlowWorks: a melee 'shove into pit' — one pawn shoves another into an open pit as a contest of both masses and both melee skills / agility (dodge) |
| `RIMMANDRAKE_DESIGN_NATURAL_WATER_AS_PITS_NOT_FLAT_PONDS` | 0.2.0 | Redesign with the owner how FlowWorks handles large natural bodies: at map load they become real pits with a bottom altitude map, filled to match, kee |
| `RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE` | 0.2.0 | Designer pass: all game wetness becomes one thin film (DECIDED by owner 12:01 PM); wet mud under drained natural water, wet/dry terrain looks, spilled |
| `RIMMANDRAKE_PORT_SUITES_TO_SCENE_RUNNER_PIT_EXPOSURE_FIRST` | 0.2.0 | Port more suites to jawa/run_scenes: FlowWorks pit exposure first, then EK's remaining scenes |
| `RIMMANDRAKE_REBUILD_SWALE_AS_SOAKING_FLOOR_NOT_FURNITURE` | 0.2.0 | Rebuild RM_Swale as a floor tile that soaks water fast and turns nearby ground to fertile soil, not a Building (owner look 2026-11-14 #4; PROPOSED Con |
| `RIMMANDRAKE_REFUSE_PITS_IN_LOOSE_GROUND_EVEN_BY_BRIDGE` | 0.2.0 | Refuse digging in sand, mud and loose snow cover on every dig path incl. the bridge drive; pit mouse-over names its original ground (owner look 2026-1 |
| `RIMMANDRAKE_SHORT_DROWNED_ELECTRONICS_LIKE_RAIN_DOES` | 0.2.0 | Short and explode powered electronics under conductive liquid via vanilla ShortCircuitUtility.TryShortCircuitInRain (owner look 2026-11-14 #8; Diverge |
| `RIVER_STEAM_ANIMATION_1` | 0.2.0 | Animated steam rising from the rivers (Pyrelands weather visual) |
| `WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS` | 0.2.0 | Climbing gear scales built walls (unroofed both sides): ask whether 'walls' meant building walls |
| `WRECKED_DISTILLATION_MODULE_1` | 0.2.0 | WreckedMachines ship Distillation module: clean water from distillable rows (not oil), rate per repair tier |

## Built in this run

All in commit `5d9004b9ce` (FlowWorks DLL rebuilt, 0 errors), test first:

- **Drawbridges are one leaf, with no plank stack** (his rulings of 2026-11-03), the first half of `RIMMANDRAKE_PRUNE_FLOWWORKS_DRAWBRIDGE_TO_HIS_NOV_THIRD_RULINGS`. `SplitLeaves` returns one leaf or none; a longer span stays an ordinary bridge; the drag text and the settings say so; the plank stack is no longer drawn. A two-leaf drawbridge in an older save keeps its two leaves. SelfTest `Drawbridge*`: red on the base source (48/50, the two intended cases), green on the fix (50/50). Two checks the change made wrong were repaired: `Drawbridge_raised_leaf_draws_without_its_winch` (it relied on the plank gate) and the live row `TWO_LEAF_TIPS_OWN_HINGE`, now `LONG_SPAN_NOT_A_DRAWBRIDGE` in `drawbridge_proof.py` (mock passes; its planted fault `two_leaf_allowed` goes red). Live: UNRUN, `python.exe src\RimMandrake\FlowWorks\northstar\drawbridge_proof.py --only LONG_SPAN_NOT_A_DRAWBRIDGE`. `required_checks.json` rebuilt for the renamed rows (other mods there changed only in stale script hashes).
- **A colonist stranded in a pit gets a rescue, and an unreachable spare ladder is skipped** (`RIMMANDRAKE_RESCUE_FLOWWORKS_STRANDED_COLONIST_REACHABLE_LADDER`). SelfTest `PitAccess_rescue_reads_no_way_out_and_a_reachable_spare`: red on base (8/9), green on the fix (59/59 with the drawbridge cases). Live: UNRUN, load save `RM_PitExposure_Review_20261112T032231` and watch the stranded colonist get a ladder job.
- **Per-game caches cleared on load** (`RIMMANDRAKE_GUARD_STATIC_GAME_STATE_THREE_NEW_CACHES_UNREVIEWED`, closed): the drawbridge raid's `winchAttacks` is cleared on every new game or load; both FlowWorks caches are listed as reviewed. `selftest_static_game_state.py`: 2 FAIL before, 145/145 after.
- Found already done by other runs (dropped as DONE): the frozen-pond ice cut (`f3f597ccc6`), the toss-flame decider (green today).

Not built, and why: the eleven walk findings go to the fixers the tick launches. The raider short ladder, the small-pump hose and the other current-version tickets were left merged and ready for lack of time in this run; each carries its check.

## Needs him

In plain words, for the Conductor. Only the first is one of his five acts; the rest are looks a judge could take, or that his next walk covers:

1. **The pump art** (`LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB`): all four pump looks are art he kept, and a review says they read as flat medallions beside the tilted tanks. Replacing kept art is his act.
2. **The drawbridges in game** (`DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS`): built and checked; only his in-game look is left.
3. **The deep-lake colour and the wall band** (`WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED`): his in-game look against the two mockups.
4. **The faucet art** (`PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE`), **the guardrail art** (`GUARDRAIL_ART_RESKIN_BORROWED_FENCE`), **the portable ladder and climbing-gear icon** (`PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS`): each built, each owes his look.
5. **Thin water by depth** (`POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD`): his look in situ; his 2026-11-20 walk asked for a water design pass by depth.
6. **Three open look questions from his 2026-11-20 walk** (`RIMMANDRAKE_JUDGE_FLOWWORKS_REVIEW_SAVE_FOUR_LOOK_QUESTIONS`, questions 4 to 6).
7. **`PIT_SUPERDEEP_COLLAPSE_1`** is DONE, but the root `CLAUDE.md` and `standing_rulings.md` point at its live file; the Conductor moves both pointers to `items/closed/` and then drops it.
8. **Current or next?** About 50 kept tickets were put in a version by the obvious reading, not by his words (listed as `split_obvious: false` in `all_v.jsonl`). The biggest: the dig interface (0.2.0 by his card already), the drawbridge gate and button (0.1.0), the rain filling a pit prison in one night (0.1.0; the fix is a default rain rate, a design call).

## Could not look at

- An open item about FlowWorks that never names it, an old name, a FlowWorks-only def or class, or a sub-system word beside one: the search cannot see it.
- The live game: no live check ran in this run (the rows built here are UNRUN with their commands).
- The judges read each item for about a minute. The second pass found 3 wrong verdicts in the keep set; more may remain in the drops [guess ~5% of drops misclassed]. A wrong drop is undone by reopening the item (its prose is in `items/closed/`).
