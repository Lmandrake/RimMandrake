# 06 — Live-found bugs, mined: where real bugs land, and which scenarios to write first

*2026-11-08, detached helper on `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL`. Asked for because the owner adopted, by
card 2026-11-08 9:06 AM, GPT's scenario-test policy (`05-gpt-review-trial1.md`, at present only in the bench clone,
`/home/mandrake/rm/bench/design/RimMandrake/2026-11-07-pocock-design/05-gpt-review-trial1.md`, uncommitted) and asked: "can't we
mine out the bugs in the last ~3 days of testing? … Aren't they minable for this purpose?" Yes. This is that census, a seed set,
and a pilot of the policy's "prefer real game and mod types" line.*

## The answer in five lines

- **66 bugs found in live play or a live proof and fixed, 2026-11-05 to 2026-11-08** across Pyrelands, FlowWorks, GSS and
  Graffiti. 47 of them have the live sighting written in the record; 19 were fixed during a live pass without the sighting written down.
- **47 of 66 (71%) were fixed in a CALLER** (game-facing C#), 13 in a kernel, 6 in XML. Leave out GSS, whose cord-shape code is a
  Verse-free kernel, and it is **44 of 50 (88%)**. This is the number trial 1 left UNMEASURED ("how often real bugs land in
  callers"): **in this record, most of the time.**
- **42 were WIRING** (the rule was known; the code got it wrong) and 24 DESIGN (nobody had said what should happen until play
  showed it). A scenario only gets written ahead of time for the first kind: **25 bugs are CALLER, WIRING and plainly
  scenario-catchable** (15 of them with the sighting written). Those 25 are what the policy could have caught before play.
- **Real types work for a gate; they stop at a map.** The real `ThinkNode_ConditionalPyrelandsColonist` built against the real
  `Assembly-CSharp.dll` and ran outside the game in 2.9 s: 5 scenarios pass, 6 of 6 planted mutants go red. A real `Map` cannot get its
  components (they need a loaded DefDatabase), and pathing cannot run at all (Unity's native allocator).
- **Seed set:** ten scenarios below, ranked; the first one written is the pilot's.

## Method

**Sources.** The four Artisan loop branches (`ralph/pyrelands`, `ralph/flowworks`, `ralph/gss`, `ralph/graffiti`, clones under
`/home/mandrake/rm/scratch/BENCH/ralph_<name>`), every commit since 2026-11-05 that touches the mod's `src/` folder (Pyrelands with
ExplosiveGrowth: 50, FlowWorks: 131 including merges and Relentless harness items, GSS: 69, Graffiti: 57). The branches have
merged main, and main's own commits in these mods since the merge base are the loop landings (`b967d9e9cb` Graffiti) plus
`682e7b4e72`, so main's log adds nothing new. Bodies, `ralph/PROGRESS.md` and `DONE.md`, and the loop logs
`D:\ClaudeWork\rimmandrake\ralph_<name>\` (token tallies, pass counts) filled in the rest.

**A row** is one behaviour that live play or a live proof showed wrong, and a commit fixed. **Not rows:** art, colour and look
changes judged by eye or by a blind judge (most of GSS's cord shapes, Graffiti's art and pigments, Pyrelands' eight ash redraws);
harness and proof-script fixes (most of FlowWorks' 11-05/06 Relentless items: `GAMEENV_FIX_*`, `SELFTEST_FIX_*`, `PROOF*_FIX_*`);
design changes the owner ruled by card; performance work never seen in play; fixes found by code review rather than play
(`682e7b4e72`, `db0cfe2a12`); false text (Pyrelands' burn letter promising that walls keep fire out). I did not count the
excluded commits by class.

**Columns.** `loc`: where the fix landed. CALLER = game-facing C# (ThinkNode, JobGiver, JobDriver, Harmony patch, Comp,
MapComponent, WorkGiver, load migration, adapter); KERNEL = Verse-free logic (checked: `CordBuilder.cs`, `CordShape.cs`,
`CordWorld.cs`, `CordPlanner.cs` have no `using Verse`); XML = defs or a setting's default. `class`: WIRING or DESIGN as above.
`ev`: L = the commit or progress file names the live sighting; I = the fix came in a live pass and the sighting is not written.
`catch`: could a scenario at the fix's location have caught it before play, had someone written it (yes / partly = needs a real
map, a Lord, a timing bar or a draw read / no).

**Limits.** One reader classified every row from commit text: no second judge saw the classes, and WIRING against DESIGN is a
judgment. Where one commit fixed several bugs I split them, and where one bug took several commits (`gr_edgeon_migrate`: four) it is
one row. Cost per bug is mostly not in the record: the column carries what it says, and the loop totals are below.

## The table

The data is `06-mined-live-bugs.tsv` beside this file; `python3 mined_counts.py` recomputes every count here from it.

| id | mod | fix | symptom | loc | class | ev | catch | scenario | cost |
|---|---|---|---|---|---|---|---|---|---|
| `pyre_fire_no_flee` | Pyrelands | `c5c65aad3e` | colonists wandered beside fire; Gaz, downed by heat and thirst, burned lying in the grass (map x run 6) | CALLER | DESIGN | L | yes | a colonist standing on a cell next to burning grass is off every burning cell within 60 ticks; a downed one who can crawl crawls to a burned-out cell | one colonist dead on run 6; pass 21 |
| `pyre_fire_duty_starves` | Pyrelands | `800e7d6bd8` | an unmanaged colony fought a day-long burn from day 2.2 to 3.1 down to food 0.00; the first colonist went down starving | CALLER | DESIGN | L | yes | an undrafted colonist at urgent hunger, with fire in the home area and a meal in the stockpile, eats before taking a firefight job | one colony run lost (map x) |
| `pyre_burrower_flees` | Pyrelands | `a2efdf4e92` | a domed ashwallow was pulled up 2.2 cells from a creeping front by vanilla's animal flee; an earlier one ran instead of diving | CALLER | WIRING | L | yes | a domed ashwallow 3 cells from a fire front stays domed for 2 hours; a standing one in dive range dives | seen on map w and an earlier map |
| `pyre_wetroots_season` | Pyrelands | `b3dd0877b1` | canal rice at 58.8 C read 'out of temperature growth range' under 'grows as if 27F cooler': watered crops stopped at the heat ceiling | CALLER | WIRING | L | yes | a watered rice plant on ash at 58.8 C is in growth season and gains growth over a day | found on map w day 21, fixed next pass |
| `pyre_no_water_letter` | Pyrelands | `aea14e1a9f` | map v's colony was down with thirst in 0.68 days and nothing said why | CALLER | DESIGN | L | yes | a Pyrelands map with no drinkable water sends the 'No water here' letter on day 0 | one colony run (map v) |
| `pyre_no_water_landing` | Pyrelands | `8661a6e36b` | no-water landings killed the colony of thirst | CALLER | DESIGN | L | partly | every generated Pyrelands map holds drinkable water (needs real map generation) | colonies lost before the fix |
| `pyre_study_into_front` | Pyrelands | `8661a6e36b` `3e67dc9776` | colonists walked into the fire front to study scorch-fruit; one walked 120 cells at 60 C to study a pod | CALLER | DESIGN | L | yes | with no order, a colonist does not take a study job on a pod beside a live front or 120 cells from home | two fixes, passes 8 and 11 |
| `pyre_hawk_embers_die` | Pyrelands | `f6fe748c79` | fire-hawks flew 7 sorties and dropped 0 embers in 2 days (map t): the ember died with its source fire | CALLER | WIRING | L | yes | a hawk carrying an ember whose source fire burns out still drops a lit ember on standing grass | 2 game days of play |
| `pyre_hawk_bearing` | Pyrelands | `4eebd22110` | hawk embers took a random bearing at smoulder 0.1 and did not catch | CALLER | WIRING | L | yes | an ember drop lands on standing grass away from the burn centre at front strength and catches within an hour | one pass |
| `pyre_furnace_heat_cap` | Pyrelands | `4eebd22110` | a furnace-beast never heated a room on its home ground (47.31 C against 47.21 C); the suite row passed only because it chilled both rooms to 10 C | CALLER | WIRING | L | yes | at the biome's own 50 C, a closed room holding a furnace-beast reads hotter than a matched empty room after 2 hours | an existing scenario passed on wrong staging |
| `pyre_herd_thirst_sync` | Pyrelands | `e25dbaf6b5` | all 43 natives read thirst 0.72 and whole herds reached the water at once | CALLER | DESIGN | L | yes | two herds spawned on the same map start at different thirst | one pass (map s) |
| `pyre_hay_burial` | Pyrelands | `d1f1c9d12b` | grass bursts left 11,039 hay stacks in three days and hit and downed colonists; Tinder popped pods within hours | CALLER | WIRING | L | partly | a burst on a full grass carpet leaves no hay and damages no pawn (needs many cells) | first real landing, 3 days |
| `pyre_pod_stub` | Pyrelands | `fd1725e98c` | harvesting a pod left a 1% stub that regrew and was picked again | XML | WIRING | I | yes | harvesting a ripe scorch-fruit pod removes the plant | - |
| `pyre_pod_rot_throws` | Pyrelands | `ea63499a7e` | pod rot threw an exception on its long tick | CALLER | WIRING | I | yes | a pod past its rot age is removed on TickLong without an exception | - |
| `pyre_stall_250` | Pyrelands | `9492f0a461` | the game stalled every 250 ticks (plants stepped in one tick, pops uncapped) | CALLER | WIRING | I | partly | a tick on a full carpet costs under a set time (a timing scenario) | - |
| `pyre_canal_in_ash` | Pyrelands | `19a92fd4e5` | canals could not be dug in the ash or reach the ponds | XML | WIRING | I | yes | a canal designation on ash ground is accepted (a def check) | - |
| `pyre_burn_warn_side` | Pyrelands | `19a92fd4e5` | the burn warning named the wrong side of the colony | CALLER | WIRING | I | yes | a front west of home warns 'west' | - |
| `pyre_eg_dry_rule` | Pyrelands | `22f9a309ab` | Pyrelands crops obeyed Explosive Growth's x0.1 dry rule (two mods' rules stacked) | CALLER | DESIGN | I | yes | on a Pyrelands map a dry-ash crop's growth follows the ash field, not Explosive Growth's x0.1 | - |
| `pyre_natives_die_dry` | Pyrelands | `2becd87bea` | native animals died in the dry | XML | DESIGN | I | yes | a native animal 100 cells from water is alive after 5 days | - |
| `pyre_regrow_tuning` | Pyrelands | `c3a3d093d6` | a burn scar regrew too fast: a 2-day scar was 56% grass | XML | DESIGN | L | no | (a tuning number judged in play) | - |
| `pyre_predator_ratio` | Pyrelands | `a507c093e1` | map e had 7 big predators to 4 small grazers | XML | DESIGN | L | yes | every roster roll has more small grazers than big predators (the suite asserts it since) | - |
| `fw_melee_across_lip` | FlowWorks | `e56b37d320` | a fallen raider fought the archers above him across the pit lip and was shot dead (story s7) | CALLER | WIRING | L | yes | a raider in a 2 m pit cannot melee a pawn on the lip, and drafted archers do not auto-target him | story run s7 |
| `fw_trapped_target_pick` | FlowWorks | `421634dec0` | a trapped raider who had only picked a target, not attacked, drew the archers' arrows while his rescuer set a ladder 3 cells away (s11) | CALLER | WIRING | L | yes | a raider in a pit who has not swung is not a target for drafted archers above; after one real attack he is | re-fix of fw_melee_across_lip, 4 story runs later |
| `fw_rain_fill_rate` | FlowWorks | `eb0df56993` | a pit flooded in one shower (0.5 m an hour) and the trapped swam out (s9) | XML | WIRING | L | yes | a day of rain raises an open pit's water about 0.24 m | story run s9 |
| `fw_cover_trashed` | FlowWorks | `0009583872` `e56b37d320` | a tribal raid went for the hidden pit cover from 55 cells out (covers were not traps to TrashUtility; isTrap was then rejected on a non-edifice) | CALLER | WIRING | L | yes | a raider 55 cells from a concealed cover never picks it to trash | two fixes (s6, s7) |
| `fw_rescue_fells_oak` | FlowWorks | `0009583872` | the rescuer spent 2,400+ ticks felling a grown oak for ladder wood | CALLER | DESIGN | L | yes | a rescuer who needs ladder wood fells the nearest sapling, not a grown tree | story run s6 |
| `fw_raid_leaves_rescue` | FlowWorks | `0009583872` | the raid left on its colony-damage trigger before the rescue finished, stranding a raider | CALLER | DESIGN | L | partly | a raid with a rescue under way does not leave for 5000 ticks (needs a Lord) | story run s6 |
| `fw_raid_stall_reach` | FlowWorks | `dc3a5cd108` | a raid stalled: melee attackers picked targets they could not walk to (the region search ignored the pit) | CALLER | WIRING | L | yes | a melee raider whose only colonist is across a pit picks a reachable target or none | - |
| `fw_cover_faces_show` | FlowWorks | `0e5b38c58f` | a covered passage pit read as a framed box with spikes on top | CALLER | WIRING | L | partly | an intact cover's draw decision hides the faces, outline and stakes below it | live 2026-11-07 |
| `fw_lip_unhides_legs` | FlowWorks | `0e5b38c58f` | a raider standing on the lip un-hid the legs of one in the pit | CALLER | WIRING | L | partly | a pawn in a pit draws below the near-lip band whatever stands on the lip | - |
| `fw_sheetrain_spike` | FlowWorks | `86bceb1e18` | a deluge spiked the frame time (sheet pulse on the pulse tick, rain offers in the kernel walk) | CALLER | WIRING | I | partly | a deluge tick on a full map stays under a set time | - |
| `gss_cords_per_run` | GSS | `a1278c49fe` | seven cords ran into one solar panel in a lived-in colony | CALLER | WIRING | L | yes | a panel fed by one conduit run draws one cord | - |
| `gss_stumps_pruned` | GSS | `c90676cd07` | a real blast cut drew no ends: both stumps were pruned as needless spurs | KERNEL | WIRING | L | yes | a 3-cell blast gap in a run leaves two drawn stumps | - |
| `gss_fold_spikes` | GSS | `32997cba6d` | cords folded into spikes, seen in a real colony | KERNEL | WIRING | L | yes | no laid cord in a played colony world has a fold tighter than the bar | - |
| `gss_inwall_conduit` | GSS | `ed38750b6a` | a machine wired to conduit inside a wall or rock drew no cord | KERNEL | WIRING | L | yes | a lamp fed by in-wall conduit draws a cord from the wall face | - |
| `gss_parallel_lines` | GSS | `2451d28c67` | one cord laid three parallel lines to one machine | KERNEL | WIRING | L | yes | no cord runs back alongside itself | - |
| `gss_door_slack` | GSS | `c976b24ca4` | one cord under a door it does not route through read as several cables | KERNEL | DESIGN | L | yes | a cord whose route skips a door leaves no slack in it | - |
| `gss_machine_slack` | GSS | `377174d2a3` | one cord in under a bench and back out read as more cables into it | KERNEL | DESIGN | L | yes | a cord's slack stays off a powered machine it does not cross | - |
| `gss_coil_on_door` | GSS | `cc3b3a275c` | slack coiled on a door or its own end: one cord read as up to 6 lines at a door | KERNEL | DESIGN | L | yes | no coil lies on a door cell or on its own cord's end | - |
| `gss_wall_dive` | GSS | `61a39d8bee` | a lamp cord wired through a wall went out the door, down the alley and back (17.8 cells) | KERNEL | WIRING | L | yes | a lamp beside a wall from its conduit dives through the wall when the way round is long | - |
| `gss_strip_faces_wall` | GSS | `615528951c` | a power strip beside a wall outlet faced the wall, so its cords read as three cables into one outlet | KERNEL | DESIGN | L | yes | a strip beside a wall outlet plugs into it and faces the room | owner saw it 2026-11-07 |
| `gss_cords_under_beds` | GSS | `93f4b98170` | cords threaded under beds, read as plugged in twice | CALLER | DESIGN | L | yes | a cord from a lamp to a socket across a bed routes round the bed | - |
| `gss_fallen_stops_at_wall` | GSS | `3569c65a32` | a mortar-cut span over a shed fell as three straight wires ending in sparks at the shed wall (game B) | KERNEL | DESIGN | L | yes | a cut wire whose line crosses a building falls beside it at full length | - |
| `gss_fallen_reads_strung` | GSS | `99a51cc8f9` | a cut N-S span lay straight along its line and read as still strung | KERNEL | DESIGN | L | yes | a cut span's wire on the ground is not straight along the span's line | - |
| `gss_stale_world_copy` | GSS | `b60a5949d6` | a graph from an earlier world copy laid a lamp's cord round its own cell; a sliced lay no longer equalled a plain Build | KERNEL | WIRING | I | yes | a sliced lay equals one plain Build on the same world | - |
| `gss_short_hop_v` | GSS | `a410bd2df4` | round excursions on short hops laid a lamp lead as a V; live row M2c failed with 3 folds, kinks 44 to 56 | KERNEL | WIRING | L | yes | no fold on a cord under 2.5 cells (a regression from the pass's own change, caught by a live row) | one live proof run |
| `gss_frame_alloc` | GSS | `903ba19f5d` | over-bar frame slices: Boehm GC paid by per-frame allocation | CALLER | WIRING | I | partly | a frame Build allocates under the pinned byte budget | - |
| `gr_weak_hands_paint` | Graffiti | `340252ca53` | on game B the two weakest hands made 7 of 8 marks and the level-15 artist none | CALLER | WIRING | L | yes | over three days a level-15 artist paints more marks than a level-2 hand | - |
| `gr_disabled_paints` | Graffiti | `340252ca53` | an Artistic-disabled pawn painted | CALLER | WIRING | L | yes | an Artistic-disabled colonist never starts a paint job | - |
| `gr_list_modified` | Graffiti | `340252ca53` | a colonist list changed while being iterated (fixed by copying before iterating) | CALLER | WIRING | L | partly | a read that adds a thought while colonists are iterated throws nothing | - |
| `gr_tally_excellent` | Graffiti | `c7512fe80a` | a tally or scratch could come out as excellent art | CALLER | WIRING | L | yes | a tally painted by a level-20 artist is never above its form's ceiling | live with 8 cast colonists |
| `gr_drafted_fight` | Graffiti | `3a1747f863` | a drafted pawn could be pulled into a paint fight or a confront | CALLER | WIRING | I | yes | a drafted colonist who reads an insult is given no fight or confront job | - |
| `gr_accidental_goover` | Graffiti | `b368a38c4e` | painters went over marks by accident, and a repeating feeling was logged on every read | CALLER | WIRING | I | yes | a painter finishing next to another mark leaves it whole; a repeated read logs once a day | - |
| `gr_double_please` | Graffiti | `418504cd11` | our sign and our piece pleased twice, through situational thoughts as well as the wall memory | CALLER | WIRING | I | yes | a colonist who sees their faith's sign gets one mood line for it, not two | - |
| `gr_memorial_save` | Graffiti | `4302c3208d` | after a save a memorial lost its dead subject and the mourner painted another | CALLER | WIRING | I | yes | after save and load a memorial still names its subject and the mourner paints no second one | - |
| `gr_thought_names_reader` | Graffiti | `4302c3208d` | wall thought descriptions named the reader instead of the painter | CALLER | WIRING | I | yes | a wall thought's text names the mark's painter | - |
| `gr_ceiling_on_load` | Graffiti | `88c654abea` | a saved mark lost its form's craft ceiling on load | CALLER | WIRING | I | yes | a loaded tally keeps its craft ceiling | - |
| `gr_edgeon_marks` | Graffiti | `d5e8d31324` | a third of Ashgate's marks sat on walls seen edge-on; a fist, two mockeries and a memorial came out as blots read as blood or mould | CALLER | DESIGN | L | yes | a painter never picks a wall face seen edge-on for a picture | - |
| `gr_spree_spam` | Graffiti | `d5e8d31324` | one spree sent sixteen messages in five hours | CALLER | DESIGN | L | yes | a spree sends one summary message when it ends | - |
| `gr_death_spam` | Graffiti | `d5e8d31324` | a death sent seven mourning messages in an hour | CALLER | DESIGN | L | yes | a death sends at most one mourning message a day | - |
| `gr_edgeon_migrate` | Graffiti | `b723a6aaf1` `350f024ca7` `d3f3c31958` `f9a7afbb88` | an older save's edge-on pictures stayed on load: 1 of 7 moved, then 6 of 9 stayed, then 4 stayed as sideways scraps | CALLER | WIRING | L | yes | a save with seven edge-on pictures loads with none left on an edge-on face | four fix commits in one evening, each found on the next live load |
| `gr_confront_names` | Graffiti | `959cb0dc25` | 'Karen confronted Lark about what's on the wall' when he had painted over her work | CALLER | WIRING | L | yes | a confront over painted-out work names the work and the mark that covered it | - |
| `gr_one_cell_stub` | Graffiti | `47c6566629` | a fitted portrait was squeezed onto the one-cell stub beside a door | CALLER | DESIGN | L | yes | a picture is never placed on a face under two cells wide | - |
| `gr_order_wrong_hand` | Graffiti | `c30fdbba96` | an order could go to a hand that may not paint that mark; a mark could land where there was no wall | CALLER | WIRING | I | yes | an order for a mark goes only to a colonist allowed that mark, on a cell with a wall | - |
| `gr_doorway_painting` | Graffiti | `b8456e74a9` | painters painted from doorways | CALLER | DESIGN | I | yes | a paint job never stands its painter in a doorway | - |
| `gr_numb_enemy_claim` | Graffiti | `0d0552b918` | numb pawns got the enemy-claim line | CALLER | WIRING | I | yes | a pawn with no mood from marks gets no enemy-claim line | - |

## Counts (MEASURED from the rows above)

| | all 66 | 47 with the sighting written |
|---|---|---|
| by mod | Pyrelands 21, Graffiti 19, GSS 16, FlowWorks 10 | Pyrelands 14, GSS 14, Graffiti 10, FlowWorks 9 |
| **by location** | **CALLER 47 (71%)**, KERNEL 13, XML 6 | **CALLER 32 (68%)**, KERNEL 12, XML 3 |
| by class | WIRING 42, DESIGN 24 | WIRING 26, DESIGN 21 |
| caller scenario could catch | yes 56, partly 9, no 1 | yes 40, partly 6, no 1 |
| **CALLER and WIRING and yes** | **25** | **15** |

- **The kernels are not where these bugs were.** All 13 KERNEL rows are GSS's cord geometry. In the other three mods, 44 of 50
  fixes landed in a caller (a few also touched a kernel) and 6 in XML; none in a kernel alone.
- **GSS is the exception, and it supports the point.** Its offline self-tests read 1178 of 1178 green in its 11-08 passes, and a kernel test could have
  caught every one of its 13 kernel rows. Nobody had written the rule yet (7 WIRING, 6 DESIGN), so the tests had nothing to check against.
  Writing the rule down came first; where it lives came second.
- **Two existing tests were blind in the way trial 1 predicted.** `pyre_furnace_heat_cap`: the suite row passed by chilling
  both rooms to 10 C, so a furnace-beast that never heated a room on its own 50 C ground passed for days. `gss_short_hop_v`: a pass's
  own change raised the kinks from 44 to 56, and only a live proof row (M2c) caught it.
- **Re-fixes are the regression signal.** `fw_trapped_target_pick` re-fixed `fw_melee_across_lip` four story runs later;
  `gr_edgeon_migrate` took four commits in one evening, each one found broken on the next live load; `pyre_study_into_front` took two.
  A scenario written at the first fix would have caught each second failure without a live load.

**Cost of finding them live (loop totals; per bug only where a row says).** The four loops ran 66 passes for 235.9 M weighted
tokens (Pyrelands 70.7 M over 21 passes, FlowWorks 54.3 M over 8, GSS 57.2 M over 18, Graffiti 53.7 M over 19; `ralph/tally.py`
over each `pass_*.jsonl`), between 11-06 18:52 and 11-08 08:32 PST. That is 3.6 M weighted tokens per live-found bug as an
**upper bound**: the same passes also made art, ran judges and wrote proofs. Rows whose cost is written: a dead colonist
(`pyre_fire_no_flee`), lost colony runs (`pyre_fire_duty_starves`, `pyre_no_water_*`), two game days of play
(`pyre_hawk_embers_die`), three days of a first landing (`pyre_hay_burial`), four commits and four live loads (`gr_edgeon_migrate`).

## Seed set: the ten to write first

Ranked by consequence (a death or a lost colony first, then a broken story, then a wrong look) times chance of regressing
(re-fixed already, or resting on vanilla behaviour that the caller overrides). **Reach:** R = buildable now on real types (a
gate or a predicate over pawn and def state, like the pilot); M = needs a real map (rooms, temperature, pathing, region
search), so either the decision is pulled out into a predicate the caller calls (and that predicate gets R), or the scenario runs
as a bridge quicktest (~90 s a map).

| rank | seed | the scenario, in play terms | reach | why here |
|---|---|---|---|---|
| 1 | `fw_melee_across_lip` + `fw_trapped_target_pick` | a raider in a 2 m pit cannot melee anyone on the lip, and drafted archers above do not target him until he has really attacked | M (target choice); R for a "may target" predicate | a death, and already re-fixed once |
| 2 | `pyre_fire_duty_starves` | an undrafted colonist at urgent hunger on a Pyrelands map eats before taking fire duty; drafted, raider, other biome, mod off: not gated | **R, written** (`pilot_realtypes/`) | a lost colony; it rests on vanilla's think-tree order |
| 3 | `pyre_fire_no_flee` | a colonist next to burning grass is off every burning cell within 60 ticks; a downed one crawls to a burned-out cell | M | a death |
| 4 | `pyre_wetroots_season` | a watered rice plant on ash at 58.8 C is in growth season and grows | M (cell temperature) | starvation; a Harmony postfix on a vanilla gate |
| 5 | `gr_edgeon_migrate` | a save with seven edge-on pictures loads with none left on an edge-on face | M (wall geometry) | four fixes in one evening |
| 6 | `pyre_furnace_heat_cap` | at the biome's own 50 C, a closed room with a furnace-beast reads hotter than a matched empty room | M (rooms) | its existing row passed on false staging |
| 7 | `fw_raid_stall_reach` | a melee raider whose only colonist is across a pit picks a reachable target or none | M (region search) | a stalled raid stops the game's story |
| 8 | `gr_disabled_paints` + `gr_weak_hands_paint` | an Artistic-disabled colonist never paints; a level-15 artist paints more than a level-2 hand | R if `GraffitiTemperament.Urge` takes plain pawn state | wrong on a clean colony |
| 9 | `pyre_burrower_flees` | a domed ashwallow 3 cells from a front stays domed; a standing one in range dives | R for the flee-gate predicate | a Harmony patch on vanilla's animal flee |
| 10 | `gr_double_please` | a colonist who sees their faith's sign gets one mood line for it, not two | R (trial 1's ThoughtWorker harness, `trial1_scenario/`) | same family as trial 1 |

## Real-types pilot: it builds, it runs, and it stops at a map

`pilot_realtypes/` (bound: 45 minutes; used about 15).

**What it is.** `PyreGateScenario.csproj` compiles the real `ThinkNode_ConditionalPyrelandsColonist.cs` (seed 2's caller) against the
real `Assembly-CSharp.dll` and `UnityEngine.CoreModule.dll` from the RimWorld install, and the mod's own built
`FireEcologyHook.dll` for `PyrelandsMechanicsGate` and the settings. Like the mods it targets net472, and it runs as a plain .NET
Framework exe, built by `winbuild.stage_build`. No fake Verse. The caller is not on main yet: `run_pilot.py` copies it from
`origin/ralph/pyrelands` (from `src/` once it lands) into `caller/` on every run, so the build always compiles today's file.

**Does it build?** Yes, first time, once the source path existed (main lacks the file; see above).
**Does it run?** Yes: `ALL SCENARIOS HOLD`, 2.9 s wall for build plus run. `run_pilot.py --mutants` plants six faults in the
copy (each conjunct dropped, the biome name misspelt, `&&` turned into `||`, the draft test inverted) and **all six go red**.
Five staging checks also run first, reading each staged pawn back through the real getters (`Map.Biome`, `IsColonist`, `Drafted`, the gate).

**What blocked, and the smallest workaround for each:**

| blocker | what it hits | workaround used |
|---|---|---|
| `new Game()` | `DefMap<HistoryEventDef,…>` throws: defs not initialized | `FormatterServices.GetUninitializedObject(typeof(Game))`, then set the `maps` list by reflection; `Current.Game` has a public setter |
| `new ThingDef()` | `ShaderDatabase` static ctor, then `Resources.Load`, an engine ECall (`SecurityException`) | uninitialized `ThingDef`, set `race` by hand |
| `Map.Biome` | goes through `Find.WorldGrid[Tile]` | mark the map a pocket map (`info.isPocketMap = true`) and give it `pocketTileInfo` with the biome set |
| `Verse.Log` | ends in Unity's `DebugLogHandler`, an ECall | `UnityEngine.Debug.unityLogger.logHandler = <a console handler>` (managed state) |
| `GenTypes` (in the gate's static ctor) | `ReflectionTypeLoadException` over Assembly-CSharp, logged, harmless here | none needed; but a caller that finds a type by name sees null outside the game |
| `Pawn`, `Faction`, `FactionDef`, `BiomeDef`, `Tile`, `Map`, `Pawn_DraftController`, `RaceProperties` | nothing | constructed normally; private fields (`factionInt`, `mapIndexOrState`, `draftedInt`) set by reflection |

**Where it stops** (`run_pilot.py --probe-map`, run on both frameworks; `--net8` uses `PyreGateScenario.net8.csproj`, where the
same scenarios also pass):

- `new TerrainGrid(map)`, `new ThingGrid(map)`, `new RegionGrid(map)`: **ok.**
- `Map.ConstructComponents()`: on .NET Framework, `TypeLoadException: Non-abstract, non-.cctor method in an interface` (Unity's
  assemblies use default interface methods, which .NET Framework cannot load). On .NET 8 that passes, and it stops at
  `DesignationManager`'s `DefMap` (needs a loaded DefDatabase).
- `DefOfHelper.RebindAllDefOfs`: `Verse.ModsConfig`'s static ctor throws (it reads the game's config paths).
- `PathFinder(map)`: on .NET 8 an ECall in `Unity.Collections.NativeArray.Allocate`; on .NET Framework the same TypeLoadException.
  **There is no pathing outside the Unity player.**

**Verdict.** Use real types for scenarios at **gates and predicates over pawn, faction and def state**. They build against the
shipped assemblies, so they cannot drift from a fake, and they run in seconds. Anything whose decision needs a map's
components, room temperature, reachability or a path (seeds 1, 3-7) has two routes: pull the decision out into a predicate the
caller calls with plain arguments (then real types reach it), or run the scenario live as a bridge quicktest (`rimworld-debug-testing`).
Loading a real DefDatabase outside the game (`LoadedModManager` over Core's XML) was not tried. It is the next wall to probe, and
ModsConfig's static ctor suggests it needs Unity's paths. One trap seen: in a back-to-back mutant run, one build reported the
previous mutant's result (a stale incremental build; cause not established). `--mutants` therefore builds with `--no-incremental`.

## The two-week measure, as a recipe to rerun on 2026-11-22

The policy's measure: **agent minutes, authoring plus drift repair, per genuine regression caught before live testing**, against
the recorded cost of finding those bugs live. Planted mutants and harness build failures are excluded. Zero catches are reported as zero.

**Start now (or the 11-22 number is UNMEASURED).** Every commit that writes or repairs a scenario test carries a trailer
`Scenario-Minutes: <n> (authoring|drift)`. Every fix commit whose bug a scenario caught before live testing carries
`Scenario-Caught: <seed or row id>`. Minutes are wall minutes of the agent doing the work: the time from starting the scenario to the commit.

**On 2026-11-22:**

1. **Scenarios that exist.** `git log origin/main --since=2026-11-08 --diff-filter=A --name-only -- '*Scenario*' '*scenario*' 'design/RimMandrake/2026-11-07-pocock-design/pilot_realtypes'`.
   Run each one's runner (`trial1_scenario/run_scenarios.py`, `pilot_realtypes/run_pilot.py`, and any new ones); a red that is not a
   planted mutant or a build break is a candidate catch.
2. **Minutes.** `git log origin/main --since=2026-11-08 --format=%B | grep -E '^Scenario-Minutes:'`, summed by kind (authoring, drift).
3. **Catches.** `git log origin/main --since=2026-11-08 --format='%h %s%n%b' | grep -B1 -E '^Scenario-Caught:'`. Check each one: a
   real regression in shipped behaviour, caught by a scenario before any live run saw it. A scenario that went red only because of
   the harness's own drift is drift, not a catch.
4. **Re-mine the live record, 2026-11-08 to 2026-11-22,** with this file's row rules (the Method section): new TSV rows, then
   `python3 mined_counts.py <new.tsv>`. Every new CALLER/WIRING row whose behaviour a scenario in step 1 covers is an **escape**
   (the scenario existed and missed it); every new row a seed scenario would have caught but that nobody wrote is a **gap**.
5. **Report:** minutes ÷ catches (or "N minutes, 0 catches"); escapes and gaps; and against them the live cost of the rows found in
   step 4 (the loops' `tally.py` tokens per pass over the same dates, and any per-bug cost the record gives). For comparison,
   today's upper bound is 3.6 M weighted tokens per live-found bug.
6. **Decide by the policy's fourth line:** expand only if catches × live cost beats minutes; otherwise stop writing scenarios ahead of
   a bug, and keep only the failure-led ones.
