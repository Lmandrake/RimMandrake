# FlowWorks walkthrough — save RM_fw_walkthrough_20261022d (2026-10-23)

*For Lukas, walking FlowWorks in game, and for the seat that files his notes. Written 2026-10-23 ~04:30 PDT from the
code, `map_r_placed.json`, the ledger and the night's live batch (`Transient/live_batch_20261023/RESULTS*.md`).
The per-plot detail (every piece, every poke, "broken looks like") stays in the key sheet:
`D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\northstar\review\scenarios\KEYSHEET.md`.*

## 0. Read this before loading

| # | fact | what it means for the walk |
|---|---|---|
| 0.1 | **Save d was written 2026-10-22 21:25.** Tonight's *layout* fixes were proven on in-memory rebuilds that were thrown away, so they are **not in save d**: creek crossings (C11 R1/R2), C1's battery cord moved inland, C1's dead tank stub, the C1 pipe tail at map R 142,45, the C5 pipe tail at map C 131,41, the R1 muffalo turned side-on. | Either the seat rebuilds map R and C5 into a fresh save before you walk (preferred), or you walk the old layout and skip those points. A rebuild moves C1 and the R stations (the last in-memory rebuild put C1 at 15,34), so the map R cells below then come from the new `map_r_placed.json`; `--goto` follows it. Since 5547ca7a09, `scenarios_map.py --save` refuses while the joint check is red, and map R's flat hose crossing (§3) is red until that fix is deployed. Drawing fixes (anything in the mod's code or art) **do** show on save d, because the game draws with the deployed mod. |
| 0.2 | Deployed now: FlowWorks **ab0204307d** (04:06 PDT) and Gimme Some Slack **2ae04e1509**. HEAD also has 5547ca7a09 (hose drawn ABOVE batteries, crossing shadow), **not deployed**. | Two hose looks in §3 (battery, flat crossing) are fixed in code but not in your game yet. |
| 0.3 | Every load of save d opens a VEF "New faction: Giant ant colony" dialog over the screen (`ANT_FACTION_SILENCE_KNOCKS_EVERY_LOAD`). | Click **Do nothing**. |
| 0.4 | Your saved FlowWorks Mod Settings hold nothing but defaults (absent = shipped default, not off). Your Gimme Some Slack cord style is **Extension cord** (ships Star Wars Jawa). | What you see is the shipped behaviour, except the cord look. |
| 0.5 | Canal overflow ("Overfilled channels spill water onto the ground") **ships OFF and is OFF on load**, although C13's sign says it is on. | Switch it ON before C13, OFF after; don't save the game with it on (it is a Mod Setting and outlives the save). |
| 0.6 | Joint fittings ("Connector fittings at liquid joins") are ON. Last night's "you switched them off" was wrong: the setting was simply absent, so it was at its default. | Nothing to do. |

**Camera:** the seat jumps the camera with `scenarios_map.py --goto <id>` (map C) or `--river --goto <id>` (map R; `C1`,
`C11`, `R1`..`R8`). Cells below are absolute map cells (x, z), the ones dev mode's mouse-over shows. Screenshots: F10
(Steam, lands in `C:\Program Files (x86)\Steam\userdata\40784075\760\remote\294100\screenshots\`).

## 1. Route

**Focus** = something changed there since save b, or a question in §4 is waiting. The others are unchanged since your
last walk; walk them only if you have time. Map C first (north-west to east), then map R (west to east along the river).

### Map C (map 0)

| stop | station | anchor cell(s) | the feature, in one sentence | do this |
|---|---|---|---|---|
| 1 **focus** | **C3** The Labyrinth Rescue (Scrapper), plot 12,12 40x40 | reel o1 18,42 · pump 17,42 · tank 17,44 · battery 18,39 · Hobb's pit 34,25 · relay reel o2 48,40 · reel park x 13, z 15-34 · turned reels 39-47,13 | Water from a pond reaches a colonist trapped in a 4 m pit by hose, through a maze. | Zoom on o1 where it meets the pump/pipe and the nozzle; follow the hose to Hobb's pit lip. Select o1 > Free end: **Outflow**, unpause: pond falls, pit fills. Look at the reel park (four looks; plump / filling / flat / wound) and the three turned reels. |
| 2 **focus** | **C12** The Oubliette and the Kennel (Modern), plot 62,12 40x36 | oubliette 66,34-37 · concealed pit 72,34 · 3 m ladder pit 65-67,16-18 (portable ladders on all four walls) · 5 m gear pit 73,17 · jump-pack 78,17 · kennel ring 80,30 · thrumbo shaft 97,35 | What a pit holds and every way in and out of one. | Look at the four portable ladders (W 65,17 · N 66,18 · E 67,17 · S 66,16). Order the drafted colonist across the concealed pit's planks (walks like floor). Unpause: wardens work from the lip; the husky climbs out, the chicken stays. |
| 3 **focus** | **C5** The Fuel Depot (Industrial), plot 112,12 40x36 | cargo tanks 114,42 · filling bay 114,26 · our hose on THEIR tank 132,20 → 142,20 · containment canal 134,33 · pump 133,34 | A fuel stop: cargo tanks, a filling bay, a tapped neighbour's tank, a canal that burns. | Zoom on each pipe entering a tank (riser onto the flange) and on the hose end at their tank (142,20). Set bay jobs Store / Fill / Empty and the pump-side tank to Dump; unpause. |
| 4 | **C6** The Tar Seep (Scrapper), plot 162,12 40x36 | sluices at the ditches' west ends 166,42 / 166,35 · slime pit 189,24 · vat 169,17 | Tar crawls, water runs, slime holds. | Open both race sluices, unpause, compare the two fronts. |
| 5 | **C9** The Trench Line, plot 162,62 44x32 | trench 172,64 · wet bay 175,84 | Trench cover and movement cost. | Hover a lane (walk cost by depth). Raids are on the branch save `RM_fw_composite_raid`. |
| 6 | **C8** The Canal Lock (Futuristic), plot 112,62 44x24 | S1 130,73 · S2 137,73 · swimmer 132,75 | A swimmer rides a lock chamber up and down on timers. | Order the swimmer into the chamber; unpause to 13:00. |
| 7 **focus** | **C2** The Drowned Keep (Industrial), plot 62,62 44x44 | gatehouse concealed pit 91,79 · guardrail 90,79 · drawbridge gate 95,80 · leaf + winch 99-101,80 · suspension bridge 68,86 · jetty 68,92 | A moated keep built from FlowWorks parts. | Max zoom on the concealed pit (seam); look at the new guardrail art on the gatehouse lip; then (god mode) deconstruct one plank to see the spikes. |
| 8 **focus** | **C4** The Wet Quarry (Industrial), plot 12,62 40x40 | benches 20,70 · sump 26,76 · pump 25,78 · hose 22-23,78 up the benches · bleed well 29,79 | A quarry below the water table kept dry by a pump. | Look at depth (D1/D2/D3, 3 m sump) and the hose climbing the benches to the drain canal. Optional: stop the pump and watch the sump rise. |
| 9 **focus** | **C7** The Bathhouse and Water Tower (Modern), plot 12,112 40x40 | ponds HIGH 13-16,134-137 / LOW 13-16,126-129 · reels on one pipe 24,127 and 24,134 · pipe west end 25,130 · bleed wells 26,129 · tower 20,145 · ground tanks 30,136 | Desert water: tower, bath, stills, thirsty colonists, two ponds levelling through a hose. | Select the LOW pond's reel (24,127) > Free end: **Outflow**; unpause ~2.5 in-game hours at speed 3; the ponds meet one level. Undraft the four thirsty colonists. |
| 10 **focus** | **DB** drawbridge picture row, 64,168 34x16 | timber lowered 64-68,174 · timber raised 72-76,174 · steel lowered 80-84,174 · steel raised 88-92,174 · closed gates timber 66,180 / steel 74,180 | Each drawbridge part draws its material picture (timber or steel). | Just look. The raised timber leaf drawing nothing is a known bug (§3). |
| 11 **focus** | **C13** The Spill Yard, plot 112,162 44x32 (new since save b) | brim-full canal 114,188 · spills R1 118,184 · R2 124,184 · R3 130,184 · R4 chemfuel 134,184 · rice row 138,180 · door room 149,174 | Canal overflow: six staged spills that spread, soak, return or burn. | Turn **"Overfilled channels spill water onto the ground" ON** first (0.5), unpause, watch the rows; then turn it OFF and see nothing new spill. |
| 12 **focus** | **MG** Modern gallery (staged into save d, open grass north of C13, x 100-160, z 198-226) | Modern tanks: short 116,202 · tall 116,208 · IBC 116,214 · extra-tall 116,220, each with a Modern reel at 104,z laid to its west port · FA fire reels: stored 134,210, laid west 132,204→120,204, laid north 140,204→140,214, laid south 126,222→126,211 | Your card picks for Modern tanks and the Modern (FA pedestal fire) reel, with hoses coupled. | Zoom on each tank's west port: the coupler should seem to go **under** the tank (your 10:27 ruling). Look at each FA reel's nozzle and shadow. |
| 13 **focus** | **C10** The Rain Basin, plot 196,112 44x40 | pond 197,140 · sluices A 209,143 / B 221,143 · pump + tank + hose 210,149 · closed ledger (two tanks, one hose) 236,117 | Ponds, springs and canals; every litre accounted. | Zoom on the ledger's two tank ports; open sluice A then B and unpause. |

### Map R (map 48, river tile 1246) — switch: `--river --labels`, then `--river --goto C1`

C1 in save d sits at origin **96,35** (48x40). C11's eight stations are on river crossings; in save d the R1 and R2
crossings still run **along** a shoreline inlet at z 105 (the old layout, 0.1).

| stop | station | anchor cell(s) | the feature, in one sentence | do this |
|---|---|---|---|---|
| 14 **focus** | **C1** The Thirsty Terraces (all four looks) | bank weir 106,74 · bank pump 116,74 · terrace 1 + S1 98-123,68 · S2 124,62 · pipe poles 128,73 and 133,73 (span over the dry ditch) · tall tank 140,72 · sprinkler rows from 135,65 · field hose 98,43 crossed by a second hose at 116,43-49 | A crop three steps above a river: lifted, carried over a ditch on poles, stored and sprayed. | Zoom on the pole span (now copper, 2 % sag) and where each ground pipe meets a pole. Open S1, unpause an in-game hour: the sprinklers spray. Look at the hose crossing at 116,43. |
| 15 | **R7** ferry rope | crossing 52,105 → 52,74 | A rope ferry across the deep run. | Order a colonist across; look whether the rope reads above the water. |
| 16 **focus** | **R2** ford stones | 78,105 → 73,105 (save d; the old inlet crossing) | Ford stones stop the current; a wader beside them is carried. | Look at the stones (untinted since tonight); unpause ~30 s: the control colonist in the water is carried, the one on the stones is not. |
| 17 | **R6** silt trap | 87,75 → 87,105 | Silt richens the neighbouring soil. | Look. |
| 18 | **R1** current | 114,105 → 104,105 (save d; old inlet crossing); a wild muffalo one cell into the water beside it | The river carries animals and logs. | Unpause and watch the muffalo and logs drift. In save d the muffalo faces north and reads as a white dome (its rear); not a missing texture. |
| 19 | **R3** weir · **R5** stakes | weir 152,104 → 152,73; stakes 152,73 → 152,104 | A weir pools the river; a stake levee holds the bank. | Look; dev "seasonal flood" breaches the worn weir. |
| 20 | **R4** breach | 178,102 → 178,71 | A worn weir breaks in a flood. | Look. |
| 21 | **R8** placer / sluice box | 204,100 → 204,69 | Panning and a sluice box draw from one shared stock. | Look. |

## 2. What changed since your last walk (save b, 2026-10-22 ~18:00)

Plain words; item ID in brackets. "Drawn" = shows on save d. "Builder only" = fixed in the scene builder, proven on a
rebuild, **not in save d** (0.1).

| where it shows | what changed | kind |
|---|---|---|
| a hose end coupled to a tank, pump or pumping station (MG tanks 116,202-220; C5 their tank 142,20; C10 ledger tanks 236,117) | **Under-couplers**, per your ruling 10:27: *"Make your couplers as needed, but have their art go UNDER the tank or pump or other fixture. That way you don't have to worry about how they "end" on the item … So have them seem to go beneath, and all is well."* A collar meets the hose's brass coupling at the port and a short pipe runs on beneath the fixture's body. The painted camlocks on the Modern tall/IBC/extra-tall tanks and the pumping stations' painted south fittings were taken back off (your picked pictures restored). (TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY, TANK_SOUTH_PORT_REDRAW_STUB_PEEKS_OUT, TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR; 387de3b5d1, 14ab773ed7) | drawn |
| tall / extra-tall tank corner lanes, cargo tank upper west/east ports (MG, C5, C7) | **Tank ports moved** onto the drawn body, so a hose couples at the tank's visible side, not the square's edge. (ab0204307d) | drawn |
| every reel (C3, C7, C10, MG, C1) | **Hose joints:** one port geometry; a hose leaves its reel's nozzle and a reel's pipe link ends on the nozzle or under the reel. **Staged reels face their hose's target** instead of all facing west (no more U-turns). (HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES, SCENARIO_REELS_FIX_STILL_FACING_WEST; c750fe9056) | drawn + saved |
| any hose beside a wall (C3 maze) | **No hose on a wall seam** (HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE, closed) and a **bend round a wall's end clears the corner** with the hose's full width (HOSE_BEND_FIX_SHAVES_WALL_CORNERS; 4cff1a0718). Reel o1 was re-laid through the wall gap at 22,42. | drawn |
| a port whose straight lead-out is blocked (water, wall) | **Side-entry elbow:** a hose arriving at a port from the side gets an elbow fitting, no stub poking on into the canal (HOSE_LEADIN_FIX_STUB_IN_THE_CANAL; 3ea460a66b). | drawn |
| C3, MG | GSS-era bare hose couplings back, four looks (34559c60d9). | drawn |
| MG; C7, C12 (Modern looks) | **Modern pictures you picked:** white leg tank, green poly tank, IBC, white poly extra-tall (fb34c9bc2d); the **FA pedestal fire reel** (694e9d2ddc), its square shadow shrunk (MODERN_REEL_SHADOW_FIX_BOX_TOO_BIG). | drawn |
| C12 ladder pit 65-67,16-18 | **Portable ladder redraw 8** installed (your pick: *"Use it, fix play-zoom legibility"*), shown on all four walls. | drawn + saved |
| C12 concealed pit, C2 gatehouse | A colonist on a concealed pit's lid now draws **at ground level**, not sunk with a dark square (PIT_LID_FIX_VICKY_PEEKS_THROUGH). | drawn |
| C2 gatehouse lip 90,79; C12 oubliette lip | **Guardrail** has its own linked rail art (was the vanilla fence) (GUARDRAIL_ART_RESKIN_BORROWED_FENCE; 34cbcbdef7). | drawn |
| C5, C7 pipes into tanks | Pipe **flange sits on the tank's drawn outline**; no extra corner elbow where a neighbour already joins (TANK_FLANGE_FIX_HOVERS_MID_PIPE; f4033cbd6d). | drawn |
| C1 poles 128,73 / 133,73 | **Pole span** follows the poles' style: copper on Scrapper poles, no longer bright Modern red; it sags at the shipped 2 % (POLE_CABLE_FIX_FORGOT_TO_SAG; GSS 2ae04e1509). | drawn |
| C11 R2 ford | **Ford stones** draw untinted: a pale stone line, no longer a dark smear (FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE; c22c6bb5bd). | drawn |
| new lays onto a tank | A hose aimed at a tank's own square now ends in front of its port (or is refused), never lying on the lid (HOSE_TANK_LAY_FIX_ENDS_ON_LID). | new lays only |
| anywhere (build it) | **Pipe faucet** (RM_PipeFaucet): a fitting on a pipe that colonists drink from and fill bottles at; four top-view looks (31f0455f60, 799e2490e0). None is staged; god-build one on a C7 pipe to try it. | new building |
| map C 112,162 | **C13 The Spill Yard** plot (overflow) is new since save b. | saved |
| C11 R1/R2 | Creek crossings now run bank to bank across the river (CREEK_STATIONS_REDESIGN_FORDED_A_PUDDLE). | builder only |
| C1 | Battery cord runs inland, not over the river (C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING); dead pipe stub under the tall tank and the pipe tail at 142,45 removed (C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE, WALK_PIPES_PRUNE_TWO_TAILS_TO_NOWHERE). | builder only |
| C5 | Pipe tail at 131,41 removed (WALK_PIPES_PRUNE_TWO_TAILS_TO_NOWHERE). | builder only |
| C11 R1 | Muffalo spawned side-on and locked (RIVER_MUFFALO_FIX_SHOWS_ITS_REAR). | builder only |

Your 10:41 card on the hose look is in force: **hoses stay over-ground**, joints fixed and gated by a joint check
(HOSE_LOOK_DECIDE_OVERGROUND_OR_UNDERPIPE, closed). If the gate cannot go green on both walkthrough maps in one sitting,
the under-pipe option comes back to you.

## 3. Known issues — don't spend time on these

Each is filed; a note that only repeats one of these needs no words beyond "seen". State is the ledger's at writing.

| item | state | station / cell | what you would see |
|---|---|---|---|
| (several, see 0.1) | fixed in the builder, not in save d | C1, C5, C11 R1/R2 | The old layouts: C1 battery cord arcing north over the river; a dead pipe stub under C1's tall tank (140,72) and a pipe tail at 142,45; a pipe tail at C5 131,41; R1/R2 crossing along an inlet instead of across; R1 muffalo as a white dome. (C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING, C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE, WALK_PIPES_PRUNE_TWO_TAILS_TO_NOWHERE, CREEK_STATIONS_REDESIGN_FORDED_A_PUDDLE, RIVER_MUFFALO_FIX_SHOWS_ITS_REAR) |
| `HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK` | built in HEAD, not deployed (0.2) | C3 north, battery 18,39 + power connector | A hose that crosses a walk-over building draws under it. The green GSS power cords running under the same battery (and at C4's pump) are the same rule owed in GSS, recorded on `HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS` (hose audit D12). |
| `HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE` | built in HEAD, not deployed | C1 field hoses, map R 116,43 | Two hoses cross flat, one painted over the other, no lift or shadow. |
| `HOSE_NOZZLE_DIAGNOSE_HUGS_WALL_ENDS` | open | C3 maze, any reel within ~2 cells of a wall end | The hose's straight run out of the nozzle can still graze a wall corner (6 of 172 test scenes). |
| `HOSE_SIDEPORT_FIX_AIMS_AT_OLD_MIDPOINT` | open | MG tanks, C5, C7 — a hose arriving at a moved port from the side | The coupling and under-coupler sit at the old edge midpoint, not the moved port. |
| `TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY` (+ `TANK_SOUTH_PORT_…`, `TANK_NS_PORTS_…`) | built; live look partly unmeasured; art regen running | every under-coupler | The collar/pipe art is a plain first pass; on tall tanks the north collar is wholly hidden behind the tank top (by the ruling). |
| `CARGO_UPPER_PORT_DECIDE_NOTHING_UNDER` · `UNDER_COUPLER_DECIDE_CORNER_CROWDING` | built, look owed | cargo tank upper west/east port (non-Modern); Modern extra-tall south+west | No body behind the upper cargo port, so nothing is drawn "under" there; on the extra-tall Modern tank two under-pipes may meet on open ground. |
| `MAST_PIPE_MEND_STOPS_SHY` | open | C1 poles 128,73 and 133,73 | Each ground pipe stops ~0.2 cell short of its mast, with no join to the mast's riser. (The blue pipe turning copper at the sprinkler-row corner beside it is the scene's four-looks design, not a fault.) |
| `MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY` | open | C7 well pump 17,146; Modern sprinkler row at C1; Modern hose ends | Modern pump, sprinkler, containers and hose ends are still the red repaint of the Jawa art. |
| `REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED` | open | C3 turned reels 39-47,13; any reel facing north or south | North/south reels show the west picture turned 90°. |
| `PORTABLE_LADDER_REDRAW_STAND_UP_STRAIGHT` | open (redraw 8 installed; legibility pass owed) | C12 ladder pit 65-67,16-18 | Ladder may read thin at play zoom. |
| `TIMBER_LEAF_DIAGNOSE_UP_AND_INVISIBLE` | open | DB timber raised leaf 72-76,174 | Draws nothing although it is raised. Judge the timber **lowered** deck and the gates instead. |
| `DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK` | open | C2 drawbridge 95-101,80, DB row | Where a FlowWorks look is set on a drawbridge part, the look's picture can win over your timber/steel material pick. |
| `OVERFLOW_DIAGNOSE_FIRST_WET_RUN` (under `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED`) | open | C13 | The proof's rain-spill, return-to-pit and ledger rows failed; the look is still yours (§4). |
| `PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE` | built | C7 pipe west end 25,130 | A real open pipe end beside the bleed wells (recorded as known; a faucet is the fitting that would close it). |
| `SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND` | built, live check owed | Mod Settings search box | Typing part of a checkbox's words may say "No setting matches"; scroll instead. |
| `ANT_FACTION_SILENCE_KNOCKS_EVERY_LOAD` | open | every load | The "Giant ant colony" dialog (0.3). |

## 4. Questions only you can answer

Answer with the word in **bold** (or your own words). Anything unanswered at the end of the sitting is taken by an agent
judge as a delegated call (`delegation_policy.md` §1) and logged as such, never as your approval.

| station | question | answer words | files to |
|---|---|---|---|
| C3 | Where a hose meets its reel, the pump link and the pipe, does each join read as **attached** or still **broken**? | attached / broken (+ which) | HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES |
| C3 | Hose girth, plump vs empty, beside a colonist: **keep**, **thinner**, **thicker**? | keep / thinner / thicker | PIPE_GIRTH_TUNE_HALF_AS_THICK, LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED |
| C12 | The new portable ladder on four walls at play zoom: **reads** as a ladder, or **too thin**? | reads / too thin | PORTABLE_LADDER_REDRAW_STAND_UP_STRAIGHT |
| C12 | A colonist walking the concealed pit's planks: **on the floor**, or **sunk / odd square**? | floor / sunk | PIT_LID_FIX_VICKY_PEEKS_THROUGH |
| C5 | Pipe rising onto each tank's flange: **right**, **riser too tall**, **enter lower**? | right / too tall / lower | PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID |
| C5 | Chemfuel, propane and water in hoses and canals: **all distinct**, or which two look alike? | distinct / X ~ Y | (a tune item if not distinct) |
| C2 | Concealed pit at max zoom: seam **right**, **too visible**, **too hidden**? | right / visible / hidden | north-star look bar `pit_covered_seam_at_max_zoom` |
| C2 | New guardrail on the gatehouse lip: **keep** or **redraw**? | keep / redraw | GUARDRAIL_ART_RESKIN_BORROWED_FENCE |
| C4 | Benches and the 3 m sump: does depth read **at a glance**, or do walls / water need more shade? | yes / walls / water | WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED |
| C4 | The hose climbing the benches: **reads right** or **ugly**? | right / ugly | (C4 hose lay; a rework item if ugly) |
| C7 | Two ponds levelling through one hose, no pump: speed **right**, **too fast**, **too slow**? | right / fast / slow | PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL |
| C7 | Bleed well (26,129): reads as a **well**, or as a **tap**? | well / tap | art call (strings already renamed: BLEED_WELL_STRINGS_RENAME_TAP_RETIRED, closed) |
| DB | Timber lowered deck, steel leaf + winch, two closed gates: **keep**, or which to **redraw**? | keep / redraw X | DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS, BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES |
| C13 | The overflow sheet on the ground: **right**, **too blue**, **too thin**, **spreads wrong**? | right / blue / thin / spread | CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED |
| C13 | Does every spill **end somewhere readable** (soaked, returned, evaporated, standing), or did one **vanish**? | readable / vanished (row) | CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED |
| MG | Do the couplers now **seem to go beneath** the tanks, as you asked? | beneath / not yet (which tank, which side) | TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY |
| MG | The four Modern tanks and the FA fire reel in game: **modern products**, or still **repainted Jawa**? | modern / repainted | MODERN_TANK_REDRAW_NOT_JUST_RED_PAINT |
| C10 | The ledger's hose into its two tanks (236,117): ends **attached** or **floating**? | attached / floating | TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR |
| C1 | The copper pipe span on poles: reads as **a pipe on poles**, **a power line**, or **sag wrong** (2 % now)? | pipe / power line / more sag / less sag | PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE |
| C1 | The four sprinkler-row looks spraying: **keep all**, or **redraw** which? | keep / redraw X | SPRINKLER_HEADS_BUILD_PUMP_REQUIRED |
| C11 R2 | Ford stones (untinted): read as **stones**, or as **dry ground**? | stones / ground | FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE |
| C11 R2 | The current's push on the wader beside the stones: **right**, **too strong**, **too weak**? | right / strong / weak | (feel; a tune item if not right) |

## 5. Settings to try

Main menu > Options > Mod Settings > **FlowWorks** (or **Gimme Some Slack**). Defaults are what ships; your saved files
hold defaults except the GSS cord style (0.4). Change one, look, change it back.

| setting (as labelled) | shipped default | where its effect shows |
|---|---|---|
| Connector fittings at liquid joins (art only) | ON | MG tanks, C5 142,20, C10 ledger: OFF removes fittings and under-couplers, leaving bare hose ends. |
| Pipes run right up to the tanks and machines they join (art only) | ON | C5, C7: OFF stops pipes at the square's edge. |
| Pipes and hoses run on beneath tanks and machines to their centre (art only) | ON | MG, C5: the part of a pipe or hose that disappears under a tank. |
| Hose thickness (slider) | 1.00x | C3 reel park (plump / filling / flat side by side). |
| Plump amount (slider) | 1.0x | C3 o1 while flowing vs the flat reel in the park. |
| Charged hoses darken with what they carry | ON | C5 chemfuel hose on their tank (142,20). |
| Brief wobble when a hose fills or drains | ON | C7 while the ponds level; C3 after Outflow. |
| Hose slack (slider) | 1.0x | C3 long hoses. |
| Water finds its level through hoses (no pump) | ON | C7 ponds: OFF and nothing levels. |
| Hose free ends: Capped / Intake / Outflow | ON | C3, C7, C10 free-end buttons. |
| Pipe poles carry pipe overhead across pits, trenches and canals (needs Gimme Some Slack loaded) | ON | C1 span over the ditch. |
| Pipe span sag: N% of its length (slider) | 2.0 % | C1 span; power wires hang ~6 %. |
| Rigid pipe and conduit need solid ground; cords lie on any bridge deck | ON | C1 ditch (why the pipe goes up on poles). |
| Sprinkler heads on pipes | ON | C1 rows. |
| Pipe faucets pour | ON | a faucet you god-build on a pipe. |
| **Overfilled channels spill water onto the ground** | **OFF** | C13 only: ON for the visit, OFF after (0.5). |
| Each liquid has its own surface | ON | C5, C6 canals. |
| Surface rivers have a current · Carry animals | ON · ON | C11 R1 drift. |
| Fords stop the current | ON | C11 R2: OFF and the wader on the stones is carried too. |
| GSS: Messy cords (master switch) | ON | C3 north and C4 pump power cords. |
| GSS: Default style | Star Wars Jawa (yours: **Extension cord**) | every unstyled cord. |
| GSS: Slack (slider) | 1.00x | cords; at 0 "off (path-tight)". |
| GSS: Aerial power lines (master switch) · Sag | ON · 6 % | C3 wire span on masts (30,38 and 30,46). |

## 6. Feedback capture

One line per thing, in chat or in `D:\ClaudeWork\rimmandrake\walk_notes_2026-10-23.txt`:

```
<station>[.<part or cell>] <VERDICT> <free text>
```

- **station** = the id in §1 (`C3`, `MG`, `C11.R2` …); a cell or part is optional: `C3.o1`, `MG.116,214.west`.
- **VERDICT** = `KEEP` (right, no change) · `FIX` (wrong, say what) · `CUT` (remove it) · `?` (puzzled; the seat explains,
  does not file) · or a §4 answer word.
- A screenshot (F10) helps: say "shot" in the line and the seat pairs it by time.

Examples: `C3.o1 FIX coupler sits left of the nozzle` · `MG beneath` · `C7 slow` · `DB.timber-gate CUT` · `C1 ?
why two pipe colours`.

The seat files each `FIX`/`CUT` as an item naming the station and cell, attaches your words verbatim (`--owner-said`), and
records each §4 answer on the item in the last column. `KEEP` closes or verifies the look bar it names.
