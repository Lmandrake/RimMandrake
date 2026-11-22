# FlowWorks 0.1.0: bar gaps that his walk of 2026-11-22 found

Written 2026-11-22 by the route run `RIMMANDRAKE_ROUTE_FLOWWORKS_WALK_TWO_FINDINGS_BACK_ELEVEN_FILED`, for the Designer.
The walk result is `walk_2_result.md` in this folder. The locked bars are not edited here.

The Stage 6 exit reads the bars. When no bar holds a thing that he rejected, the exit passes over it, and the mod comes
back to his walk with the thing unfixed. That happened twice: his findings of 2026-11-20 were still open on
2026-11-22 (arrival 2, "What I noticed first", point 5). From now on the walk gate (`walk_items_closed`) holds the walk
until each item is closed. A bar line is still owed, so that a check finds a return of the fault before he does.

Each row: what he rejected, the bar that comes nearest today, and the bar line that this run proposes. The bar lines
are experiences, with no tuning number (`bar_rule.py`). Adding a bar to 0.1.0 is a Conductor act
(`lock-bars --add`), as `inv_geyser_tub` and `inv_liquid_coating` were added on 2026-11-14.

| His finding (item) | Nearest bar today | Gap | Proposed bar line |
|---|---|---|---|
| White frames at every water edge (`RIMMANDRAKE_REMOVE_WHITE_FRAMES_AT_EVERY_WATER_EDGE_HE_SAW_THEM_EVERYWHERE`, `RIMMANDRAKE_TRACE_PALE_BLOCKS_IN_PIT_HE_DOUBTS_THE_FORGE_HAZE`) | `inv_looks` (water looks per depth), `pit_reads_as_hole` | No bar says that water meets its walls with no artefact. | Water in a pit, canal or moat meets its walls with no pale frame, band or block that is not part of the art. |
| Water drawn over an east/west sluice gate (`RIMMANDRAKE_HIDE_WATER_OVER_EAST_WEST_SLUICE_GATE_STATION_SEVEN`) | `sluice_drains_on_command` (reads open or shut) | Open or shut is read; the water drawn over the gate, by its facing, is not. | A sluice gate of either facing shows water only where the water stands, never over its own panel. |
| A shut sluice keeps its own square's water (`RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE`) | `inv_doors`, `sluice_drains_on_command` | The bar exists. Its check passed, and the fault stayed. The check is too weak. | None new: repair the check of `sluice_drains_on_command` so that it reads the gate's own square. |
| Choose style changes one part only (`RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY`) | `inv_looks` (pipe, reel and tank styles), `hose_reads_as_hose` (four styles) | No bar says that a pick spreads. | Choose style on any FlowWorks part restyles every FlowWorks part on its connected line. |
| A built bridge has no Choose style (`RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES`) | `inv_bridges`, `inv_looks` | No bar names a bridge's look as the player's pick. | A built bridge offers Choose style, like every other FlowWorks part. |
| A pawn cannot walk beneath a plank or concealed cover (`RIMMANDRAKE_LET_PAWN_WALK_UNDER_PLANK_COVER_BRIDGES_ALREADY_ALLOW_IT`) | `hung_bridge_spans` (pawns walk under a bridge) | The bar covers bridges only. No bar covers pit covers. | A pawn in a pit or canal walks beneath any cover over it, as beneath a bridge. |
| A cover only lightens over a pawn (`RIMMANDRAKE_FADE_EVERY_PIT_COVER_TRANSPARENT_OVER_A_PAWN_LIGHTEN_PLEASED_HIM`, his ruling: this version) | none | No bar. | A bridge or cover over a pawn turns see-through, so that the cover and the pawn beneath both read. |
| Pit floors deeper than 2 m draw one colour (`RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR`); a stepped floor does not read (`RIMMANDRAKE_ASK_GPT_HOW_TO_DRAW_STEPPED_PIT_FLOOR_HE_COULD_NOT_READ_IT`, his pick) | `inv_looks` (depth legible by wall faces), `pit_reads_as_hole` | The wall-face check passed. Nothing reads the floor. | In a pit whose floor has parts of different depths, the player can tell by looking which part is deeper. |
| The water sheet over a pawn (`RIMMANDRAKE_DESIGN_PAWN_IN_LIQUID_LOOK_WATER_SHEET_IS_A_MISTAKE`, his pick; `RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES`) | `pawn_height_follows_depth`, `inv_liquid_coating` ("a clean, not crude, look"), `no_snared_standing` | The bar exists. An agent judged it passed, and he rejected the look. | None new: after his pick, the check of `inv_liquid_coating` reads the picked look against its mockup. |
| The tanks, the Modern pipe and the sprinkler read the wrong style (`RIMMANDRAKE_REDRAW_FLOWWORKS_TANKS_THREE_STYLES_ONLY_SCRAPPER_READS_RIGHT`, `RIMMANDRAKE_REDRAW_MODERN_PIPE_AND_SPRINKLER_THEY_READ_PLASTIC_FUTURISTIC`, his picks) | `inv_looks` (styles exist) | That a style exists is a bar. That it reads as its style is not. | Each look reads as its named style (Scrapper, Industrial, Modern, Futuristic) on every tank, pump, pipe and head. |
| Jetties read as two squares of wood; bridge looks are dull (`RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD`, his pick) | `inv_bridges`, `hung_bridge_spans` | No bar for how a jetty or a bridge material reads. | A jetty reads as one structure from its ledge to its end, held by its cables, and each material reads as that material. |
| The bridge drag must start on the landing, and nothing tells him (`RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING`) | `inv_bridges` | No bar on how a bridge is placed. | A player who drags a bridge from the wrong square is told where to start. |
| A bridge will not span a ruined bridge's scrap (`RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP`) | `inv_bridges` | No bar. | A new bridge can be built over the wreck of an old one. |
| No check reads that railings stop a blast throw (`RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS`) | `inv_bridges` (guardrails) | The bar names railings. No check decides it. | None new: give `inv_bridges` a check for railings. |
| Raiders do not try a short ladder at a 4 m pit (`RIMMANDRAKE_BUILD_RAIDERS_TRY_SHORT_LADDER_AT_FOUR_METRE_PIT`) | `raiders_fetch_their_fallen` | The bar covers a ladder that reaches. "Try, and fall short" (his card of 2026-11-21) is not in it. | Raiders at a pit too deep for their ladder try it, and the player sees that it falls short. |
| A stranded colonist in a sealed 4 m pit reads not trapped; no rescue (`RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE`) | `ways_in_and_out` | No bar says that a colonist who cannot climb out is rescued. | A colonist who cannot climb out of a pit reads as trapped, and the colony goes to get them out. |
| An interrupted dig starts again from zero (`RIMMANDRAKE_KEEP_DIG_PROGRESS_ACROSS_MEALS_AND_NAPS`) | `inv_dig_depth` ("digging takes hours") | No bar says that work is kept across a break. | A dig that is interrupted goes on from where it stopped. |
| A red log line with Gimme Some Slack (`RIMMANDRAKE_TRACE_SLACK_FLOWWORKS_TIER_MINIFIED_LOOKUP_ERROR`) | the floor's clean-log line (`floor.json`) | Covered by the floor. | None new. |
| Station 47 empty; signs over unbuilt scenes (`RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES`) | none: a test-map fault, not the mod | Not a bar. | None: the staging selftest owns it. |

Passes he stated, which need no new bar: pit depth at stations 34-39, trench cover at 40-41, a bridge lightens over a
pawn beneath it (station 51), and no white ring on the geysers.
