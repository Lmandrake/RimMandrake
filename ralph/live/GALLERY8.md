# GALLERY8: the pass-8 pits-and-depth sitting (manifest)

One saved map, `RM_FW_Gallery8`, holds every fixture; batch A (`g8_depth.py`) and batch B (`g8_kit.py`) load it, stage the
pawns, read the game's state and shoot. Nothing is staged by hand. Scripts: `ralph/live/g8_common.py` (layout, bridge with
the unknown-parameter guard on, run folder, shots), `g8_site.py` (build/verify the save), `g8_depth.py`, `g8_kit.py`,
`g8_fetch.sh` (fetch one run), `g8_harness.py` (the FlowWorks-free harness checks on any map).

## Commands (from the repo root on Archmagi)
```
ralph/steve.sh sync                                                   # Steve gets the scripts
# build the map once (a new name each rebuild, or --replace to move the old file into the run folder):
ralph/steve.sh run 'nohup python.exe ralph/live/g8_site.py build --save RM_FW_Gallery8 > Transient/ralph_fw/g8_site.out 2>&1 &'
ralph/steve.sh run 'python.exe ralph/live/g8_site.py verify'          # load it and read every fixture back
# batch A (~8 min): empty, occupied, the two graded walks; two depth-draw settings side by side:
ralph/steve.sh run 'nohup python.exe ralph/live/g8_depth.py --k 0.3,0.375 --hold 0,0.4 --tag a > Transient/ralph_fw/g8_depth.out 2>&1 &'
# batch B (~5 min): ladders, portables, bridge treatments + walk under, gear:
ralph/steve.sh run 'nohup python.exe ralph/live/g8_kit.py --tag b > Transient/ralph_fw/g8_kit.out 2>&1 &'
# progress / end: the last lines of the .out, then the SUMMARY line
ralph/steve.sh run 'tail -n 5 Transient/ralph_fw/g8_depth.out'
# fetch a run (one tar): latest, latest-depth, latest-kit, latest-site, or the run folder name
ralph/live/g8_fetch.sh latest-depth /mnt/d/ClaudeWork/rimmandrake/ralph_flowworks/shots/pass8
```
Each run writes `Transient/ralph_fw/g8/<batch>_<tag>_<HHMMSS>/` on Steve: `log.txt`, `results.jsonl` (one row per read
or assert: `name, value, expected, pass, source`; `pass` is true/false for an assert, null for a reading, `UNMEASURED`
when the build lacks the read), `shots.json` and `shots/`. Shot files are
`g8<A|K|S>_<HHMMSS>_<nn>_<name>_r<root>__cell_rect.png`; root 7.2 is the owner's play zoom (63.6 px a cell measured on
Steve's window, which holds about 42 x 14 cells there), root 20 is 22.9 px a cell. A frame the window clipped is a
harness error in the log. Run either batch with `--no-load` to stay on the map already loaded.

## The map
Built from `RM_TestSite_calm_v3` (AridShrubland, 250 x 250, tile 112579, three colonists, fog and dangers cleaned) by
`g8_site.py build`: Phoebe on Peaceful, threat scale 0, the incident queue cleared, Clear weather locked, the clock set to
11:00 (a declared time exception: the site has colonists), the gallery rect cleared (`clear_area`), unroofed and painted
Soil, every fixture dug dry with `jawa/flowworks_excavation_drive` (1 level = 0.5 m), then saved through
`test_site_saves.save_site` (stat before/after, compressed grid expanded). Every load re-applies the quiet profile and
drafts the colonists.

**ORIGIN (60, 150) is PROVISIONAL**: it has not been checked against the calm map yet (`g8_site.py probe` ranks
candidate origins by water/rock/sand and colonists nearby; set `ORIGIN` in `g8_common.py` and regenerate this table).
The gallery clears and paints its own ground, so any origin inside the map works; the probe only picks the quietest.

Origin (60, 150). Site rect (cleared, unroofed, Soil, unfogged): x 52..123, z 146..182.

| fixture | cells (x, z) | depth | subject / walk cells | shot rect(s) |
|---|---|---|---|---|
| A1 hole 0 (0 m) | x 60..62, z 150..152 | 0 levels | north row centre (61, 152) | west x 55..73, z 149..154 / east - at 7.2, all at 20 |
| A1 hole 1 (0.5 m) | x 65..67, z 150..152 | 1 levels | north row centre (66, 152) | west x 55..73, z 149..154 / east - at 7.2, all at 20 |
| A1 hole 2 (1 m) | x 70..72, z 150..152 | 2 levels | north row centre (71, 152) | west x 55..73, z 149..154 / east - at 7.2, all at 20 |
| A1 hole 3 (1.5 m) | x 75..77, z 150..152 | 3 levels | north row centre (76, 152) | west - / east x 74..93, z 149..154 at 7.2, all at 20 |
| A1 hole 4 (2 m) | x 80..82, z 150..152 | 4 levels | north row centre (81, 152) | west - / east x 74..93, z 149..154 at 7.2, all at 20 |
| A1 hole 5 (4 m) | x 85..87, z 150..152 | 8 levels | north row centre (86, 152) | west - / east x 74..93, z 149..154 at 7.2, all at 20 |
| A1 hole 6 (8 m) | x 90..92, z 150..152 | 16 levels | north row centre (91, 152) | west - / east x 74..93, z 149..154 at 7.2, all at 20 |
| A1 control | (57, 152) | undug | (57, 152) | west |
| A2 4 m | x 60..62, z 157..159 | 8 levels | south (60, 157), middle (61, 158), north (62, 159) | x 58..69, z 155..161 |
| A2 8 m | x 65..67, z 157..159 | 16 levels | south (65, 157), middle (66, 158), north (67, 159) | x 58..69, z 155..161 |
| A3 N-S graded trench | x 73..75, z 157..168 | row z0+r at min(r,8): z 157=0 .. z 165=8, z 166..168=8 | walk x=74, z 157..168 (start (74, 156)) | x 71..77, z 156..169 |
| A4 E-W graded strip | x 80..91, z 157..159 | col x0+c at min(c,8): x 80=0 .. x 88=8, x 89..91=8 | walk z=158, x 80..91 (start (79, 158)) | x 78..93, z 155..161 |
| B1 5x5 pit, wall ladders | x 60..64, z 173..177 | 4 levels (2 m) | ladders N (62, 177) E (64, 175) S (62, 173) W (60, 175) (RM_Ladder, WoodLog, facing its wall); floor pawn (61, 174); reach target (62, 171) | x 58..66, z 171..179 |
| B2 N | x 69..71, z 174..176 | 4 levels (2 m) | portables N (70, 176); pawn (70, 175); reach target (70, 172) | a x 67..82, z 172..178 |
| B2 E | x 74..76, z 174..176 | 4 levels (2 m) | portables E (76, 175); pawn (75, 175); reach target (75, 172) | a x 67..82, z 172..178 |
| B2 S | x 79..81, z 174..176 | 4 levels (2 m) | portables S (80, 174); pawn (80, 175); reach target (80, 172) | a x 67..82, z 172..178 |
| B2 W | x 84..86, z 174..176 | 4 levels (2 m) | portables W (84, 175); pawn (85, 175); reach target (85, 172) | b x 82..97, z 172..178 |
| B2 deep | x 89..91, z 174..176 | reach+1 levels (7 at reach 6) | portables N (90, 176), E (91, 175), S (90, 174), W (89, 175); pawn (90, 175); reach target (90, 172) | b x 82..97, z 172..178 |
| B2 bare | x 94..96, z 174..176 | 4 levels (2 m) | portables none; pawn (95, 175); reach target (95, 172) | b x 82..97, z 172..178 |
| B3 hole + suspension bridge | x 102..106, z 169..177 | 4 levels (2 m) | timber bridge anchors (101, 173) and (107, 173) (deck row z=173); walk (104, 176) -> (104, 173) -> (104, 170) | x 99..109, z 168..178 |
| B4 climbing gear | gear (112, 174), Apparel_PackJump (113, 174) | undug | wearer (115, 174) (RM_ClimbingGear worn) | x 110..117, z 172..176 |


## Checks, bars and asserts
| check | bar(s) | fixture | shots (name part) | reads / asserts |
|---|---|---|---|---|
| empty depth row | `pit_depth_ladder_legible` | A1 (+A2, A3, A4) | `empty_A1_r7.2`, `empty_A1_r20`, `empty_A2..A4` | A1 depths read back (`fixture_A`) |
| occupied depth row | `pawn_height_ladder_legible`, `pit_occupant_below_floor` | A1 + control | `occ_<k>_<hold>_A1_r7.2/_r20` | per occupant `A1_occupant_<m>` (sink, state); assert `A1_sink_nondecreasing`, `A1_sink_4m_eq_8m` |
| occupants by row | `pit_occupant_below_floor`, `pit_trapped_reads_as_trapped` | A2 | `occ_<k>_<hold>_A2_r7.2/_r20` | `A2_occupant_*`; assert `A2_<south/middle/north>_4m_eq_8m` |
| graded walk N-S | `pawn_lowers_on_deeper_cell`, `pawn_rises_on_shallower_cell` | A3 | `A3_walk_start`, `A3_<nn>_<out/back>_d<D>` (camera fixed) | `A3_stop_<nn>` (cell, depth, drawnZ, state); assert `A3_step_<i>_<j>`: sink strictly up onto deeper, strictly down onto shallower |
| graded walk E-W | same two bars | A4 | `A4_walk_start`, `A4_<nn>_...` | `A4_stop_*`, assert `A4_step_*` |
| two settings | all of the above | A1, A2 | every `occ_` shot tagged `k<k>_h<hold>` | `setting_<tag>`; hold is UNMEASURED without `SetSinkHoldAbove` |
| wall ladders | `ladder_state_legible`, `wall_ladder_rides_on_rails` | B1 | `B1_lowered_r7.2/_r20`, `B1_raised_r7.2/_r20` | `B1_ladders_lower/raise` (ProofLadder raised=), `B1_reach_out_lower` (expect reach=True), `B1_reach_out_raise` (expect False) |
| portable ladders | `portable_ladder_leans_on_its_wall` | B2 | `B2_N_E_S_W_deep_bare_r7.2/_r20` | `B2_<N/E/S/W>_portable_spans` (Reaches=True), `B2_deep_portable_spans` (False), `B2_<pit>_reach_out` (2 m pits True; deep and bare False) |
| bridge looks | `suspension_bridge_reads_hung` | B3 | `B3_t0/_t1/_t2_r7.2/_r20` (or `B3_asbuilt` on a build without treatments) | `B3_span`, `B3_treatment_<t>` (UNMEASURED without SetTreatment) |
| walk under the deck | `pawn_walks_under_deck` | B3 | `B3_walk_BEFORE`, `B3_walk_MID`, `B3_walk_AFTER` (camera fixed) | `B3_underpath`, `B3_reach_end`, `B3_walk_MID/AFTER` (arrived, depth, sink) |
| climbing gear | `climbing_gear_reads_as_kit` | B4 | `B4_ground_and_worn_S_r7.2/_r20`, `B4_worn_E/N/W_r7.2` | `B4_ground` (gear + jump pack present) |

Reads that do not exist on the old build are called by name from `g8_common.py` and come back `UNMEASURED`:
`RimMandrake.FlowWorks.RM_PitDepthDraw.DepthDrawState(int thingIDNumber)` ("cell=x,z depth=D sink=S drawnZ=Z lipZ=L face=F
hold=H k=K"), `SetSinkHoldAbove(float)`, `SetSinkPerLevel(float)` (k falls back to the `pitSinkPerLevel` settings field),
`RimMandrake.FlowWorks.Pits.RM_SuspensionHang.SetTreatment(int)`. Beside the new read, the old build's
`RM_PromotionProofs.ProofPawnSink(ThingID)` is always read; when DepthDrawState is missing it carries the asserts, and the
row's `source` says `ProofPawnSink(legacy)`.

`jawa/static_call` convention: `args` is one string, `|`-separated, one item per parameter (the count must match; `""` is
no arguments); each is coerced by the parameter type: int, float, double (invariant culture), bool, string, IntVec3 as
`x,z` or `x,y,z`, Map as `current` or an index, any Def by defName, any Thing/Pawn by ThingID (`Human123`) or bare
thingIDNumber. Overloads and instance methods are refused with the candidate signatures.
