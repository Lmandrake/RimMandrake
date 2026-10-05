# Gimme Some Slack - human review key sheet

## Old station -> new station (densified 2026-10-05)

Owner 2026-10-05: *"reduce the number of north Star verifications and verification stations for the human review sheet as well. If so, remove them."* Plan: `design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md` section 4. 47 stations -> 33: fifteen cut or merged, one new HOSE STATES station, the rest renumbered in order. Stations 1-12 kept their numbers; the default-look survivors moved into one column west of the style gallery; the north gallery kept its cells.

| old (47-station map) | new | station |
|---|---|---|
| 1 | **1** | GROUND CORDS: SCRAPPER |
| 2 | **2** | GROUND CORDS: INDUSTRIAL |
| 3 | **3** | GROUND CORDS: MODERN |
| 4 | **4** | GROUND CORDS: FUTURISTIC |
| 5 | **5** | MODERN: EVERY COLOUR ENTRY |
| 6 | **6** | OVERHEAD: FOUR LOOKS |
| 7 | **7** | MERGE: BIGGER RUN WINS |
| 8 | **8** | MERGE: A TIE |
| 9 | **9** | SPLIT KEEPS THE LOOK |
| 10 | **10** | RESTYLE THIS RUN (yours) |
| 11 | **11** | HOSE REELS: FOUR LOOKS |
| 12 | **12** | OLDER SAVE: NO STORED LOOK |
| 13 | **-** | removed -> covered by 1-4 (doc l.165 'powered line': the ground-cord stations) |
| 14 | **-** | removed -> covered by 1-4 (doc l.166 'unpowered line' (veto point): weakest distinct question; the matrix P=dead scenes cover it in state) |
| 15 | **-** | removed -> covered by 1-4 (doc l.167 'cut line': their missing cell, live + dead end) |
| 16 | **-** | removed -> covered by 1-4, 19 (doc l.168 'tangled pile': their 3x3 tangle; the electric room) |
| 17 | **-** | removed -> covered by 1-4, 18 (doc l.169 'devices + plugs': their switch + three plugged devices; the pole cluster) |
| 18 | **13** | WALL + ROCK ENTRIES |
| 19 | **-** | removed -> covered by 6, 10 (doc l.171 'mast chain': OVERHEAD: FOUR LOOKS has battery > mast > mast > lamp mast > wall bracket in all four looks; RESTYLE THIS RUN has a span) |
| 20 | **-** | removed -> covered by 6, 10 (doc l.171 'lamp masts': as the mast chain) |
| 21 | **-** | removed -> covered by 6, 10 (doc l.171 'wall bracket': as the mast chain) |
| 22 | **14** | CUT + FALLEN SPAN |
| 23 | **15** | POWER TAP |
| 24 | **-** | merged into 16 (doc l.173 'flat': HOSE STATES, three parallel hoses) |
| 25 | **-** | merged into 16 (doc l.173 'filling': HOSE STATES) |
| 26 | **-** | merged into 16 (doc l.173 'plump': HOSE STATES) |
| 27 | **-** | removed -> covered by 21, 22, 29, 32 (doc l.174 'long + bend': the maze bends, the relay's length, the pond) |
| 28 | **-** | removed -> covered by 17 (doc l.175 'crossing': the hose grid has four crossings with the same over/under question) |
| 29 | **-** | merged into 16 (doc l.173 'parallel': its question (lanes, one over the other) is the same picture) |
| 30 | **17** | HOSE GRID |
| 31 | **18** | POLE CLUSTER |
| 32 | **19** | ELECTRIC ROOM |
| 33 | **20** | OVER THE UNKNOWN |
| 34 | **21** | HOSE MAZE: TWO ROUTES |
| 35 | **22** | HOSE MAZE: SHORT WAY WALLED |
| 36 | **23** | MAP EDGE |
| 37 | **24** | RIVER CROSSING |
| 38 | **25** | ROOF BOUNDARY |
| 39 | **26** | LONG SPAN + DIAGONALS |
| 40 | **27** | CONVERGING HUB |
| 41 | **28** | NETS SIDE BY SIDE + HALF-BUILT |
| 42 | **29** | RELAY REELS: GOING FARTHER |
| 43 | **30** | DEPLOY BY HAND, THEN WIND IT IN |
| 44 | **31** | DROPPED HALFWAY |
| 45 | **32** | INTO THE POND |
| 46 | **33** | ON THEIR TANK |
| 47 | **-** | merged into 30 (doc l.180 'wind it in': the deploy card now says 'after he lays it, press Retract'; same reel and pawn, the reverse action) |
| new | **16** | HOSE STATES |
| F | **F** | free build area (unchanged) |
| M | **M** | art-slot board (unchanged; now carries a note) |

Built by `src/RimMandrake/GimmeSomeSlack/human_review.py`. Game paused, god mode on, weather clear, noon, Peaceful.

**This map reviews the per-build style design** (`design/RimMandrake/messyconduit_style_per_build_design.md`, your decisions of 2026-10-04): the look is picked on the build button and stored on each piece. Stations 1-11 are built through that machinery and stand side by side in four looks. `--style` (Mod Settings 'Default style') now only sets the DEFAULT look, which station 12 and every station 13-33 draw because they store no look. Default look now: **Scrapper**.

Jump the camera: `human_review.py --goto N` (N = station; S0 = style gallery 1-12; 0 = whole south region; N0 = north gallery 18-33; M = art board; F = free area).

## Everywhere

- Build menu: clicking a conduit, switch, pole, lamp mast, wall bracket or hose reel button opens a menu of four looks (Scrapper, Industrial, Modern, Futuristic); conduit adds the Modern colour entries (random mix, one colour per run, orange, green, brown, yellow, blue). The button remembers your last pick.
- 'Restyle this run' sits on any selected conduit, switch or pole: it repaints the whole run (art only, free).
- A run = connected conduit cells + switches + the poles and brackets wired into them. Batteries and machines end a run. Joining two runs of different looks: the run with more conduit cells wins; a tie goes to the older run.
- Mod Settings > RimMandrake: Gimme Some Slack: master switch OFF restores vanilla conduit art instantly.
- Unpause (space) to see motion: sway, live-end sparks, hose filling. Pause again to study a frame.

## Row S - one look per station (style gallery, south-east)

Built through the real style machinery: every piece stores its look; the global setting is not used. Neighbours differ in ONE thing: the look.

### 1. GROUND CORDS: SCRAPPER

one compact floor build in the Scrapper look: full battery, a 3x3 tangle, a run under a steel wall, an in-line switch, three plugged devices and one missing conduit cell (a live end and a dead end)

**Notice**

- every cord, plug, junction, wall stub, cut end and the switch is Scrapper art (the art board M says which pieces still fall back)
- the tangle: junction boxes with cables in them (KNOWN GAP, stage 2: the pile's pieces still follow the DEFAULT look, not the run's)
- the battery side of the gap sparks when unpaused (live end), the far side lies limp (dead end); the far lamp is dark
- the three floor lamps are Scrapper lamps (round 6: built in their run's look; 'Restyle this run' repaints them too)

**Try**

- select any conduit or the switch: the 'Restyle this run' gizmo repaints the whole run (art only)
- build one conduit into the gap from the menu in ANOTHER look: it joins the run and takes the run's look (the larger run wins: here the battery side)
- flick the switch: everything past it goes dark, the cords stay

**Note**

- U_motion_look (moved off the live proof 2026-10-05): UNPAUSE and judge the LOOK of motion here: the cord's whip, the live end's drip / spark rhythm, the sway in the wind. Motion is not a Northstar bar; state proxies cover the state, so only your eye judges this.

### 2. GROUND CORDS: INDUSTRIAL

one compact floor build in the Industrial look: full battery, a 3x3 tangle, a run under a steel wall, an in-line switch, three plugged devices and one missing conduit cell (a live end and a dead end)

**Notice**

- every cord, plug, junction, wall stub, cut end and the switch is Industrial art (the art board M says which pieces still fall back)
- the tangle: junction boxes with cables in them (KNOWN GAP, stage 2: the pile's pieces still follow the DEFAULT look, not the run's)
- the battery side of the gap sparks when unpaused (live end), the far side lies limp (dead end); the far lamp is dark
- the three floor lamps are Industrial lamps (round 6: built in their run's look; 'Restyle this run' repaints them too)

**Try**

- select any conduit or the switch: the 'Restyle this run' gizmo repaints the whole run (art only)
- build one conduit into the gap from the menu in ANOTHER look: it joins the run and takes the run's look (the larger run wins: here the battery side)
- flick the switch: everything past it goes dark, the cords stay

### 3. GROUND CORDS: MODERN

one compact floor build in the Modern look (menu entry 'Modern: one colour per run'): full battery, a 3x3 tangle, a run under a steel wall, an in-line switch, three plugged devices and one missing conduit cell (a live end and a dead end)

**Notice**

- every cord, plug, junction, wall stub, cut end and the switch is Modern art (the art board M says which pieces still fall back)
- the tangle: power strips with plugs in the sockets (KNOWN GAP, stage 2: the pile's pieces still follow the DEFAULT look, not the run's)
- the battery side of the gap sparks when unpaused (live end), the far side lies limp (dead end); the far lamp is dark
- the three floor lamps are Modern lamps (round 6: built in their run's look; 'Restyle this run' repaints them too)
- one colour along the whole run (built with 'one colour per run'); the 2 cells past the gap are a run of their own and may carry another colour

**Try**

- select any conduit or the switch: the 'Restyle this run' gizmo repaints the whole run (art only)
- build one conduit into the gap from the menu in ANOTHER look: it joins the run and takes the run's look (the larger run wins: here the battery side)
- flick the switch: everything past it goes dark, the cords stay

### 4. GROUND CORDS: FUTURISTIC

one compact floor build in the Futuristic look: full battery, a 3x3 tangle, a run under a steel wall, an in-line switch, three plugged devices and one missing conduit cell (a live end and a dead end)

**Notice**

- every cord, plug, junction, wall stub, cut end and the switch is Futuristic art (the art board M says which pieces still fall back)
- the tangle: junction boxes with cables in them (KNOWN GAP, stage 2: the pile's pieces still follow the DEFAULT look, not the run's)
- the battery side of the gap sparks when unpaused (live end), the far side lies limp (dead end); the far lamp is dark
- the three floor lamps are Futuristic lamps (round 6: built in their run's look; 'Restyle this run' repaints them too)

**Try**

- select any conduit or the switch: the 'Restyle this run' gizmo repaints the whole run (art only)
- build one conduit into the gap from the menu in ANOTHER look: it joins the run and takes the run's look (the larger run wins: here the battery side)
- flick the switch: everything past it goes dark, the cords stay

### 5. MODERN: EVERY COLOUR ENTRY

seven Modern runs, one per entry of the conduit build menu: random mix, one colour per run, orange, green, brown, yellow, blue (top to bottom)

**Notice**

- random mix (top, with two spurs up): each cord from one node to the next is ONE colour; the colours vary piece to piece through the run
- one colour per run: a single colour picked at random when it was built, the same along the whole run
- each single-colour run: that colour on every strand, plug, junction and wall stub (orange uses the shipped pieces)

**Try**

- build one conduit onto the end of any run: it joins and keeps that run's colour (nothing reshuffles)
- restyle the 'blue' run to random mix from its gizmo, then back: the blue comes back
- unpause, rebuild something elsewhere: no run changes colour

### 6. OVERHEAD: FOUR LOOKS

four overhead lines side by side, one per look (top to bottom: Scrapper, Industrial, Modern, Futuristic): battery, power mast, power mast, lamp mast, and a wall bracket on a steel wall stub

**Notice**

- each row's poles, lamp mast, bracket and hanging cable are that look's own (the cable falls back for all four: art board M)
- two different looks stand side by side on one map: the old global setting could not show this
- the spans sag and cast a ground shadow; the lamp masts are lit

**Try**

- select a pole > Restyle this run: the whole row (poles, bracket, spans) changes look
- build a new mast near a row from the menu in ANOTHER look: auto-link joins only a run of the SAME look
- select a pole > Link wire to a pole of another row: two looks meeting is a merge (the bigger run wins)

## Row T - runs: merge, tie, split, restyle (style gallery, south-east)

A run = connected conduit cells + switches + the poles wired into them. One run, one look. Each 'before' row is for YOU to poke; each 'after' row was done by the build so you see the result.

### 7. MERGE: BIGGER RUN WINS

two runs in two looks, one gap apart: Industrial (8 cells, powered) and Modern orange (4 cells, its lamp dark)

**Notice**

- after row: the joining cell was built as Futuristic, yet the whole run is now Industrial: the run with more conduit cells wins and the smaller one is repainted
- a message named both looks when it happened
- the Modern lamp lit: one run, one power net

**Try**

- before row: build ONE conduit in the gap from the menu (any look, god mode = instant): watch the 4 orange cells turn Industrial and read the message
- make the orange run longer first (5+ more cells), then join: now orange wins

### 8. MERGE: A TIE

two equal runs (5 cells each): Scrapper built FIRST (older), Futuristic built after

**Notice**

- after row: joined with an Industrial cell, the whole run is Scrapper: on a tie the OLDER run wins
- a message named both looks

**Try**

- before row: build one conduit in the gap: Scrapper should win
- deconstruct one Scrapper cell first (4 vs 5), then join: Futuristic wins

### 9. SPLIT KEEPS THE LOOK

an Industrial run of 11 cells; the after row had its middle cell deconstructed

**Notice**

- after row: two runs, BOTH still Industrial (nothing is re-defaulted)
- WATCH: Industrial picks a cable kind (black rubber / corrugated steel / coiled) per cord net; if a half changes cable kind after the split, that is the colour-reshuffle bug the test plan predicts (SR6/SR7)
- the far lamp is dark: the split cut its power

**Try**

- before row: deconstruct the marked cell yourself
- build it back in another look: it adopts the bigger half's look

### 10. RESTYLE THIS RUN (yours)

a Scrapper run (battery, conduit, an in-line switch, a lamp) with a power mast wired into its end and a span to a lamp mast: nothing restyled yet, the button is yours

**Notice**

- before you press anything: every piece is Scrapper, poles and span included

**Try**

- select ANY piece (a conduit cell, the switch, either pole) > 'Restyle this run' > pick a look: the cords, the switch, both poles, the span AND the floor lamp all change at once; cost and power do not
- select the lamp > 'Restyle this lamp' > another look: it keeps that look through the next run restyle ('Match its cable run' undoes it)
- pick Modern > random mix: the colours vary piece to piece along the run; restyle again and back: the same colours come back
- unpause: nothing reverts

## Row U - hose reels per look, and an older save (style gallery)

### 11. HOSE REELS: FOUR LOOKS

per look (top to bottom: Scrapper, Industrial, Modern, Futuristic) a reel with its hose laid out and full, and beside it a reel whose hose was laid and then reeled back in

**Notice**

- laid: the reel draws its EMPTY drum (hose out) and the hose leaves the drum's mouth in the reel's own look
- hose strand, wraps, couplings, nozzle or end cap: all in the reel's look (non-Scrapper wraps have no cloth tint)
- reeled in: the drum is full again and the style is kept
- NOT BUILT: the design's coil overlay; the reel swaps between two whole images instead (art board M)

**Try**

- select a reel: Lay hose / Reel in hose; lay the reeled-in one again: same look
- build a new reel from the menu: four looks on the button; copy a reel: the copy keeps its look

### 12. OLDER SAVE: NO STORED LOOK

conduit, a switch, a lamp, a power mast with a span to a lamp mast and a laid hose reel, all built OUTSIDE the menu (as in a save from before this change): nothing stores a look

**Notice**

- everything draws the DEFAULT look (Mod Settings 'Default style', `--style`): the same as before the change
- every station from 13 on is built the same way, so it follows the default too

**Try**

- `human_review.py --style Cybertek` (or Mod Settings): this set and stations 13-33 change; stations 1-11 do NOT
- build one conduit onto it from the menu: the run's look is written for real now (the save migration)

## Row A - floor cords (default look)

### 13. WALL + ROCK ENTRIES (was 18)

a run passing under a steel wall and through a granite block; a branch ending inside the wall

**Notice**

- where the cord meets the wall it goes into a plate mounted ON the wall (round 4): a thin edge-on strip inside a west or east face, the whole plate on a south face's lit band, a sliver on a hidden north face; nothing pokes out onto the floor
- the cord meets the plate straight (no hooked curl of cord printed on the plate)
- the rock tunnel has rock holes on both faces, inside the rock, the same way
- the branch ending in the wall is a wall terminal: its loose wire leaves the socket straight out of the wall and lies on the floor (on a south face it hangs straight down the face)

**Try**

- deconstruct a wall cell: the cord re-plans across the gap
- mine the granite: the tunnel opens

## Row B - overhead lines (default look)

### 14. CUT + FALLEN SPAN (was 22)

battery -> power mast -> mast -> mast -> lamp, two 12-cell overhead spans, the SECOND span cut (as if blown by an explosion)

**Notice**

- each cut half is ONE wire in the span's own cable: from the mast's insulator down to the break, where both halves meet on the ground
- the live downed end sparks; the far lamp is dark
- the first span still hangs and still carries power

**Try**

- select the middle mast > Re-string cut wires: the span goes back up and the lamp relights
- god mode: drop an explosion under a span (dev tools) to cut another

### 15. POWER TAP (was 23)

a power-tap clamp biting ANOTHER faction's grid (left, hostile battery), drained one-way into our lamp (right)

**Notice**

- the crocodile clamp sits on their conduit; one of our cords is taped to it
- the two grids never merge (their net and ours stay separate)
- our lamp is lit with no power source of our own

**Try**

- unpause and watch their battery drain
- Mod Settings > Gimme Some Slack > taps off: our lamp goes dark

## Row C - flexible hoses: states, lanes and crossings

Hoses never branch (ruled by card): one hose is one line with two ends. Shown as the system does it today; there is no crossing piece.

### 16. HOSE STATES (new)

three hoses laid side by side, two cells apart (top to bottom): FLAT (nothing flowing), FILLING (flow on, frozen half-way through filling), PLUMP (flow on, fully filled)

**Notice**

- flat: the hose lies flat and thin; a straight hose has NO joiner along it; the free end is a plain open end the hose's own width
- filling: half-plump, the swell is mid-transition; UNPAUSE and it finishes plumping in ~half a second
- plump: a full round hose, visibly wider than the flat one; still no joiner on the straight
- lanes: each hose keeps its own lane; where their S-curves meet, one draws over the other cleanly (the newer reel's on top)

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- NOT designed: there is no crossing piece and no T or + hose fitting (hoses never branch, by ruling)

### 17. HOSE GRID (was 30)

four hoses, two each way, crossing in a 2 x 2 grid

**Notice**

- four crossings: every one is over/under, with a fixed order (newest on top)
- FINDING to judge: where the S-curve slack of two hoses runs along each other they may overlap for a stretch

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- NOT designed: there is no crossing piece and no T or + hose fitting (hoses never branch, by ruling)

## Row E - power showpieces (north gallery)

Round 2 (owner notes 2026-10-04): a pole with many kinds of devices, a crowded electric room under an overhead line, a span over a hidden stone block.

### 18. POLE CLUSTER (was 31)

one power pole with a wide mix of devices: some right beside it (lamp, heater, sun lamp, mini-turret, two batteries), some reached by conduit runs (stove, hi-tech research bench, TV), a walk-in freezer with an in-wall cooler and wall lamps inside and out, and a lamp mast fed over the air

**Notice**

- each device right beside the pole gets its own hookup from the pole's insulators; with more hookups than insulators, see whether they share a terminal or pile onto one (owner question: which terminal does each go to?)
- big devices (5x2 bench, 3x1 stove, 2x1 TV): the cord should meet the building, not stop short of its edge or end in mid-air
- the in-wall cooler: the cord reaches it through the wall face, not across the room
- wall lamps (one inside the freezer, one outside on its south wall): their cords run up to and beneath the WALL the lamp hangs on, ending under it (round 4), never stopping short in the lamp's cell or crossing the room's middle
- the turret's cord does not cross the turret's own base art
- the lamp mast on the far NW gets its power through the air: one span, lit

**Try**

- toggle each device off (select > flick): its cord stays, the device goes dark
- deconstruct the pole: every adjacent hookup falls; the conduit-fed devices keep their cords
- build another lamp right beside the pole: does it pick a free terminal?

### 19. ELECTRIC ROOM (was 32)

a walled workshop crammed with powered devices joined by messy conduit (with a tangle), and three power poles carrying a line OVER it: west pole outside, middle pole inside the room, east pole outside

**Notice**

- the showpiece: does the room read as lived-in and messy without turning into noise?
- the overhead line passes over the walls and the devices; its ground shadow falls across the floor and furniture
- floor cords never cross on top of a device's art; the tangle sits in the open between the stoves and the TV
- the middle pole stands inside the (unroofed) room and joins both the overhead line and the floor run
- the east pole lights the lamp outside the room through the air

**Try**

- unlink the east span: only the outside lamp goes dark
- roof the room (Architect > Structure > Build roof, god mode): the middle pole is now under a roof - its spans should be cut (roof cut) and drop
- switch looks (--style): the whole room changes at once

### 20. OVER THE UNKNOWN (was 33)

two power poles carrying power OVER a solid granite block that lies hidden under fog of war and overhead mountain: the wire runs off into the unknown and emerges on the other side

**Notice**

- the span leaves the west pole, vanishes into the fog over the block and reappears to land on the east pole
- nothing of the wire shows ON the fog (no bright line drawn over the unknown), and its ground shadow vanishes with it
- both poles stand in open sky beside the block, so the link is allowed (a roof under a span is fine)
- the lamp and the heater beside the east pole are lit: power crossed the block

**Try**

- mine into the block from the west (god mode): the fog lifts cell by cell and the wire is revealed overhead
- toggle the roof overlay (bottom-right): the block is all mountain roof
- select a pole > Unlink wire: the east lamp goes dark; Link it again

## Row F - hose mazes (north gallery)

Two routes out of a small maze, then the short one walled off after laying. validation_hose.py owns the pass/fail; this map shows it.

### 21. HOSE MAZE: TWO ROUTES (was 34)

a hose laid from a reel deep inside a small walled maze to a free end outside; two ways out: the short one (south-east gap) and a longer one (north-east gap)

**Notice**

- the hose finds the SHORT route out through the inner chamber's west door, down and out the south-east gap
- it never clips a wall corner, and its bends stay smooth in the one-cell corridors
- it stays inside the corridors (it never jumps a wall)

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- reel it in and lay it again to the same free end: does it pick the same route?

### 22. HOSE MAZE: SHORT WAY WALLED (was 35)

station 21's maze; after the hose is laid, a wall is built across the short (south-east) gap - does the hose re-route the long way, or reel itself in?

**Notice**

- what the hose does when its route is blocked AFTER laying: it re-routes north-east if that still fits the hose length (it does: measured offline the long way needs about 25 of the hose's 40 cells), else it winds back onto the reel with a message and an alert saying how many cells the way round needs (HOSE_BLOCKED_REROUTE_RETRACT_1)
- add your own walls to lengthen the way round: past 40 cells (the default since round 6) the hose reels in (selftest r5: the 13x13 spiral needs 73)
- if it re-routes, the new path is as clean as station 21's

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- reel it in and lay it again to the same free end: does it pick the same route?
- deconstruct the blocking wall (cells 12,1 and 12,2): does the hose go back to the short way?

## Row G - challenge configurations (north gallery)

Built to make visible bugs show: map edge, water, roof edge, longest/odd spans, a full pole, neighbouring nets, half-built work and save-load.

### 23. MAP EDGE (was 36)

poles and cords at the map's north-east corner: a pole IN the corner cell, poles on the top and right edge cells, and floor runs lying along both edges

**Notice**

- the cords' loose curls must not draw off the map (nothing hanging past the edge, nothing cut off with a hard line)
- the corner pole's wires and shadow stay on the map
- no red errors (open the debug log: none mentioning GimmeSomeSlack)

**Try**

- pan the camera to the edge: is anything drawn in the black past the map?
- deconstruct the corner pole: both its spans drop

### 24. RIVER CROSSING (was 37)

a river (chest-deep moving water, shallow banks): an overhead span from bank to bank, and a floor run fording the shallow end in waterproof conduit

**Notice**

- the overhead wire's shadow falls on the water like on the ground (or not at all), never as a dark stripe on the river bed
- the floor cord on the water: does it float, sink or draw on top as if on soil? (waterproof conduit has its own look?)
- the cords' curls do not wander into the deep water
- both far devices are lit

**Try**

- unpause: the river flows; does the cord on the water move with it (it should not)?
- deconstruct one waterproof conduit cell in the river: the cut ends lie in water - do they still spark?

### 25. ROOF BOUNDARY (was 38)

a roofed steel room: an overhead span passes OVER its roof, a floor run goes in under the wall, and a pole standing INSIDE under the roof tries to link out

**Notice**

- wires over a roof are allowed: the span is drawn over the roof, its shadow on the roof
- the pole under the roof is refused (anchors need open sky): no wire through the roof
- the floor cord inside the room: drawn under the roof shading, no seam where it passes the roof edge
- the lamp and heater inside are lit

**Try**

- roof overlay on (bottom-right) to see the roof edge
- build a roof over the east pole (god mode): its span drops (roof cut)
- remove the room's roof: link the inside pole from its gizmo

### 26. LONG SPAN + DIAGONALS (was 39)

four chains: a span of EXACTLY the longest length (20), one cell too long (21, refused), a 45-degree diagonal chain, an odd-angle span, and a very short span (3 cells)

**Notice**

- the 20-cell span: the deepest sag; it must not touch or dip below the ground, and its shadow stays a smooth curve
- the 21-cell pair stays unlinked and its lamp dark (refused: too far)
- diagonals: the wire leaves from the insulator tips on the correct side of the crossarm, not from the pole's middle
- the odd-angle span: no kink or zig-zag where it changes direction
- the 3-cell span: nearly no sag, but the wire still meets both insulators (not a straight line through the poles)

**Try**

- select a mast > Link wire to the 21-cell partner: the message says too far
- Mod Settings: raise the longest span to 25: then link it

### 27. CONVERGING HUB (was 40)

a hub pole with four spans (its maximum) arriving from N, E, S and W, a FIFTH pole trying to link (refused: full), and three lamps plus a heater right beside the hub

**Notice**

- four wires meet on one crossarm: each lands on an insulator tip, none crossing through the pole art
- with more wires than insulators, do two share a tip cleanly or overlap in a blob?
- the fifth (NE) pole stays unlinked, its lamp dark
- the hub's local hookups: which terminal does each lamp take?

**Try**

- unlink one spoke, then link the NE pole: it takes the freed slot
- deconstruct the hub: four spans drop at once

### 28. NETS SIDE BY SIDE + HALF-BUILT (was 41)

three separate powered nets two cells apart; two nets end to end with a one-cell gap that is a conduit BLUEPRINT; a half-built run (conduit, then blueprints, a pole blueprint, a lamp blueprint)

**Notice**

- side by side: each net's cords stay with its own net (no cord jumping across to the neighbour's run)
- Modern look, 'a different colour per power net': three nets = three colours; after the gap is built, the two merged nets should become ONE colour
- blueprints draw no cords (a cord never runs to a ghost)
- SAVE then LOAD the game here: every cord comes back the same (same curls, same colours), blueprints still cord-free

**Try**

- god mode: build the gap blueprint (or unpause and let colonists build): nets merge, the dark lamp lights
- save, load, compare (this is the save-load station)
- --style ExtensionCord for the colour checks

### 29. RELAY REELS: GOING FARTHER (was 42)

three hose reels in a row, 32 cells apart: the first reel's hose is laid onto the second reel, whose own hose is laid onto the third (66 cells end to end; one hose holds 40)

**Notice**

- each hose ends in a brass coupling on the NEXT reel's side: the chain reads connected, not two loose hoses
- flow into the first reel (dev gizmo, on): its hose plumps, and the second reel's hose plumps too -- it is fed through the relay (there is no real liquid yet: FlowWorks pipes are paper)
- select the middle reel: 'Relay: fed by the hose from the reel at ...'; each hose shows its own 'N of 40 cells'

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- reel in the first hose: the second one drains (nothing feeds it)
- lay the third reel's hose back onto the first: refused, a chain may not loop back
- build a fourth reel 30 cells further east and lay the third reel onto it: the chain goes on

### 30. DEPLOY BY HAND, THEN WIND IT IN (was 43)

a hose reel with a Deploy order 24 cells out and one idle colonist beside it (UNPAUSE: nothing else is ordered); after he lays it, press Retract

**Notice**

- the colonist walks to the reel, picks up the hose end and walks it out: the hose unrolls behind him along his walk
- he sets the end down at the order's cell and the hose lies there, coupled
- the hose is never longer than his walk: it does not jump out to the target
- after he lays it, press Retract on the reel: he winds the hose back along its route to the reel
- the free end runs back along the hose's route; the hose gets shorter, it does not vanish at once
- it ends Stored: no hose on the ground, the reel's drum full

**Try**

- select the reel: the gizmos are the player orders (Lay hose / Move hose end / Retract hose); the instant 'DEV:' ones appear only with dev mode on
- draft him mid-walk: the end drops where he stands (see station 31)

### 31. DROPPED HALFWAY (was 44)

a reel whose hose end was dropped 14 cells out (an interrupted carry)

**Notice**

- the open end lies on the ground at the end of the hose; the hose is drawn only as far as it was walked
- select the reel: 'Move hose end' and 'Retract hose' are offered; no colonist is carrying anything

**Try**

- select the reel: the gizmos are the player orders (Lay hose / Move hose end / Retract hose); the instant 'DEV:' ones appear only with dev mode on
- Move hose end to a cell beside it, then unpause: an idle colonist picks the end up and walks it there

### 32. INTO THE POND (was 45)

a reel 10 cells from a pond, its hose laid into the water

**Notice**

- the hose end lies in the water, not on the bank
- select the reel: inspect reads 'intake in ...' (it is drawing from the pond)

**Try**

- select the reel: the gizmos are the player orders (Lay hose / Move hose end / Retract hose); the instant 'DEV:' ones appear only with dev mode on

### 33. ON THEIR TANK (was 46)

a hose coupled to another faction's liquid tank

**Notice**

- a brass coupling sits on THEIR tank where the hose ends
- select the reel or the tank: inspect names their faction

**Try**

- select the reel: the gizmos are the player orders (Lay hose / Move hose end / Retract hose); the instant 'DEV:' ones appear only with dev mode on

## Expected refusals (shown on purpose)

- 25 ROOF BOUNDARY (was 38): link 0-2 is refused (Roofed).
- 26 LONG SPAN + DIAGONALS (was 39): link 2-3 is refused (OutOfRange).
- 27 CONVERGING HUB (was 40): link 0-5 is refused (FullA).

## M. Art-slot board: which per-look pieces still fall back

Computed from the files on disk at the paths the shipped code reads, so it shrinks as art lands. In world (north band, `--goto M`) the board lists only the rows that are not all 'own'.

**Note**

- U_style_missing_art (moved off the live proof 2026-10-05): per-family EndFrayed_Live / PowerStrip / StrandShadow art does not exist; those slots fall back to the Jawa (Scrapper) pieces. Judge whether the fallback reads acceptably in each look; it is taste, not a Northstar bar.

| piece | Scrapper | Industrial | Modern | Futuristic |
|---|---|---|---|---|
| ground strand | own | own | own | own |
| plug | own | own | own | own |
| junction (T) | own | own | own | own |
| junction (+) | own | own | own | own |
| wall stub | own | own | own | own |
| rock stub | own | own | own | own |
| dead frayed end | own | own | own | own |
| live frayed end | own | own | own | own |
| power strip, dark | n/a | n/a | own | n/a |
| power switch, on | own | own | own | own |
| power switch, off | own | own | own | own |
| overhead span cable | fallback: the Scrapper ground strand | fallback: black rubber ground cable | fallback: black rubber ground cable | fallback: the Futuristic ground strand |
| power mast | own | own | own | own |
| lamp mast | own | own | own | own |
| wall bracket (S face) | own | own | own | own |
| power-tap clamp | own | not wired: draws the Scrapper clamp; this look's file IS on disk | not wired: draws the Scrapper clamp; this look's file IS on disk | not wired: draws the Scrapper clamp; this look's file IS on disk |
| hose reel, stored | own | own | own | own |
| hose reel, laid | own | own | own | own |
| hose strand, flat | own | own | own | own |
| hose strand, plump | own | own | own | own |
| hose binding | own | own | own | own |
| hose coupling | own | own | own | own |
| hose nozzle | own | own | own | own |
| hose end cap | own | own | own | own |
| hose open mouth | own | own | own | own |
| hose reel coil overlay | not built: the reel swaps two whole images | not built: the reel swaps two whole images | not built: the reel swaps two whole images | not built: the reel swaps two whole images |

## F. Free build area

North band, west end (`--goto F`): open soil. A charged power pad (2 solar generators, 3 full batteries) with a conduit stub labelled *plug in here*; steel, plasteel, components and wood along the south edge. Use the build menus here to try the picker yourself: pick a look, build, extend, join two looks, restyle. God mode builds instantly; turn it off (dev toolbar) to watch colonists build from blueprints (the look rides blueprint -> frame -> building). Research is finished. No gallery mast is within 20 cells, so nothing you build links into the gallery.

## This build

```
{
 "builds": {
  "Battery/hostile": "1/1",
  "Battery/player": "15/15",
  "Cooler/player": "1/1",
  "ElectricStove/player": "3/3",
  "FlatscreenTelevision/player": "2/2",
  "Granite/None": "287/287",
  "Heater/player": "11/11",
  "HiTechResearchBench/player": "2/2",
  "PowerConduit/hostile": "2/2",
  "PowerConduit/player": "273/273",
  "PowerSwitch/player": "1/1",
  "RM_AerialLampMast/player": "3/3",
  "RM_AerialMast/player": "35/35",
  "RM_HoseReel/player": "17/17",
  "RM_LiquidTank/hostile": "0/1",
  "RM_PowerTapClamp/player": "1/1",
  "SolarGenerator/player": "2/2",
  "StandingLamp/player": "30/30",
  "SunLamp/player": "2/2",
  "Turret_MiniTurret/player": "2/2",
  "Wall/player": "301/301",
  "WallLamp/player": "1/1",
  "WaterproofConduit/player": "8/8"
 },
 "default_style": "StarWarsJawa",
 "expected_refusals": {
  "25:0-2": "Roofed (expected Roofed)",
  "26:2-3": "OutOfRange (expected OutOfRange)",
  "27:0-5": "FullA (expected FullA)"
 },
 "hose_hooks": {
  "21": {
   "judged": "TODO validation_hose.review_maze",
   "route": {
    "couplings": 3,
    "layOk": true,
    "pathLen": 18.6385,
    "state": "Plump"
   }
  },
  "22": {
   "after_wall": {
    "couplings": 2,
    "layOk": true,
    "pathLen": 22.3851,
    "state": "Plump"
   },
   "before": {
    "couplings": 3,
    "layOk": true,
    "pathLen": 18.6385,
    "state": "Plump"
   },
   "judged": "TODO validation_hose.review_block_wall"
  },
  "30": {
   "colonist": {
    "cmd": "pawn:814=tp:16,128",
    "pawn": {
     "downed": false,
     "drafted": false,
     "driver": null,
     "forced": false,
     "id": 814,
     "job": null,
     "name": "Cave",
     "pos": [
      16,
      128
     ],
     "toil": -1
    },
    "success": true
   },
   "order": {
    "carry": "Stored",
    "cmd": "order:14,124=deploy:38,125",
    "pending": "Deploy",
    "pendingAt": [
     38,
     125
    ],
    "reason": null,
    "success": true
   }
  },
  "31": {
   "settrail": {
    "carry": "Dropped",
    "cmd": "settrail:58,124=dropped;58,124;59,124;60,124;61,124;62,124;63,124;64,124;65,124;66,124;67,124;68,124;69,124;70,124;71,124;72,124",
    "layOk": true,
    "success": true,
    "trail": 15,
    "trailLength": 14.4862
   }
  }
 },
 "hose_states": {
  "11@206,14": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 14.4862,
   "state": "Plump"
  },
  "11@206,19": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 14.4862,
   "state": "Plump"
  },
  "11@206,24": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 14.4862,
   "state": "Plump"
  },
  "11@206,9": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 14.4862,
   "state": "Plump"
  },
  "11@224,14": {
   "blend": 0,
   "couplings": null,
   "pathLen": null,
   "state": "Flat"
  },
  "11@224,19": {
   "blend": 0,
   "couplings": null,
   "pathLen": null,
   "state": "Flat"
  },
  "11@224,24": {
   "blend": 0,
   "couplings": null,
   "pathLen": null,
   "state": "Flat"
  },
  "11@224,9": {
   "blend": 0,
   "couplings": null,
   "pathLen": null,
   "state": "Flat"
  },
  "12@208,98": {
   "blend": 0,
   "couplings": 2,
   "pathLen": 16.4901,
   "state": "Flat"
  },
  "16@100,39": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 21.4842,
   "state": "Plump"
  },
  "16@100,41": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 21.4842,
   "state": "Plump"
  },
  "16@100,43": {
   "blend": 0,
   "couplings": 2,
   "pathLen": 21.4842,
   "state": "Flat"
  },
  "17@100,14": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 21.4842,
   "state": "Plump"
  },
  "17@100,23": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 21.4842,
   "state": "Plump"
  },
  "17@106,8": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 20.5822,
   "state": "Plump"
  },
  "17@115,8": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 20.5822,
   "state": "Plump"
  },
  "21@172,149": {
   "blend": 1,
   "couplings": 3,
   "pathLen": 18.6385,
   "state": "Plump"
  },
  "22@200,149": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 22.3851,
   "state": "Plump"
  },
  "29@160,174": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 31.711,
   "state": "Plump"
  },
  "29@192,174": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 31.711,
   "state": "Plump"
  },
  "32@98,124": {
   "blend": 1,
   "couplings": 2,
   "pathLen": 13.4923,
   "state": "Plump"
  },
  "33@142,124": {
   "blend": 0,
   "couplings": 2,
   "pathLen": 13.4923,
   "state": "Flat"
  }
 },
 "merge_actions": {
  "7": {
   "action": "C",
   "error": null,
   "message": "Joined a Modern run to a larger Industrial run (8 conduit cells): the Modern run is now Industrial.",
   "ok": true
  },
  "8": {
   "action": "C",
   "error": null,
   "message": "Joined a Futuristic run to a larger Scrapper run (5 conduit cells): the Futuristic run is now Scrapper.",
   "ok": true
  },
  "9": {
   "action": "D",
   "error": null,
   "message": "Joined a Futuristic run to a larger Scrapper run (5 conduit cells): the Futuristic run is now Scrapper.",
   "ok": true
  }
 },
 "notes": [
  "build RM_LiquidTank: 0 of 1 survived [{'op': 'RM_LiquidTank:156,124', 'why': \"no ThingDef 'RM_LiquidTank'\"}]",
  "swept 1 hostile/non-colonist pawn(s) off the review map"
 ],
 "pawns_in_region": [
  "Human814",
  "Human817",
  "Human820"
 ],
 "peaceful": true,
 "station_roofs": true,
 "style_reads": {
  "1": {
   "runs": [
    {
     "PowerConduit_Scrapper": 16,
     "PowerSwitch_Scrapper": 1
    },
    {
     "PowerConduit_Scrapper": 2
    }
   ]
  },
  "2": {
   "runs": [
    {
     "PowerConduit_Industrial": 16,
     "PowerSwitch_Industrial": 1
    },
    {
     "PowerConduit_Industrial": 2
    }
   ]
  },
  "3": {
   "runs": [
    {
     "PowerConduit_Modern_Orange": 16,
     "PowerSwitch_Modern": 1
    },
    {
     "PowerConduit_Modern_Green": 2
    }
   ]
  },
  "4": {
   "runs": [
    {
     "PowerConduit_Futuristic": 16,
     "PowerSwitch_Futuristic": 1
    },
    {
     "PowerConduit_Futuristic": 2
    }
   ]
  },
  "5": {
   "mixPieces": 5,
   "mixStrands": [
    "Strand_Brown",
    "Strand_Green",
    "Strand_Yellow"
   ],
   "runs": [
    {
     "PowerConduit_Modern_Mix": 18
    },
    {
     "PowerConduit_Modern_Yellow": 12
    },
    {
     "PowerConduit_Modern_Orange": 12
    },
    {
     "PowerConduit_Modern_Green": 12
    },
    {
     "PowerConduit_Modern_Brown": 12
    },
    {
     "PowerConduit_Modern_Yellow": 12
    },
    {
     "PowerConduit_Modern_Blue": 12
    }
   ]
  },
  "6": {
   "anchors": [
    [
     "RM_AerialMast",
     "RM_AerialMast_Futuristic",
     [
      "Futuristic",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialMast",
     "RM_AerialMast_Futuristic",
     [
      "Futuristic",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialLampMast",
     "RM_AerialLampMast_Futuristic",
     [
      "Futuristic",
      "AerialLampMast"
     ]
    ],
    [
     "RM_AerialWallBracket",
     "RM_AerialWallBracket_Futuristic",
     [
      "Futuristic",
      "WallBracket"
     ]
    ],
    [
     "RM_AerialMast",
     "RM_AerialMast_Modern",
     [
      "Modern",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialMast",
     "RM_AerialMast_Modern",
     [
      "Modern",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialLampMast",
     "RM_AerialLampMast_Modern",
     [
      "Modern",
      "AerialLampMast"
     ]
    ],
    [
     "RM_AerialWallBracket",
     "RM_AerialWallBracket_Modern",
     [
      "Modern",
      "WallBracket"
     ]
    ],
    [
     "RM_AerialMast",
     "RM_AerialMast_Industrial",
     [
      "Industrial",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialMast",
     "RM_AerialMast_Industrial",
     [
      "Industrial",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialLampMast",
     "RM_AerialLampMast_Industrial",
     [
      "Industrial",
      "AerialLampMast"
     ]
    ],
    [
     "RM_AerialWallBracket",
     "RM_AerialWallBracket_Industrial",
     [
      "Industrial",
      "WallBracket"
     ]
    ],
    [
     "RM_AerialMast",
     "RM_AerialMast_Scrapper",
     [
      "Scrapper",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialMast",
     "RM_AerialMast_Scrapper",
     [
      "Scrapper",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialLampMast",
     "RM_AerialLampMast_Scrapper",
     [
      "Scrapper",
      "AerialLampMast"
     ]
    ],
    [
     "RM_AerialWallBracket",
     "RM_AerialWallBracket_Scrapper",
     [
      "Scrapper",
      "WallBracket"
     ]
    ]
   ],
   "runs": [
    {
     "RM_AerialLampMast_Futuristic": 1,
     "RM_AerialMast_Futuristic": 2,
     "RM_AerialWallBracket_Futuristic": 1
    },
    {
     "RM_AerialLampMast_Modern": 1,
     "RM_AerialMast_Modern": 2,
     "RM_AerialWallBracket_Modern": 1
    },
    {
     "RM_AerialLampMast_Industrial": 1,
     "RM_AerialMast_Industrial": 2,
     "RM_AerialWallBracket_Industrial": 1
    },
    {
     "RM_AerialLampMast_Scrapper": 1,
     "RM_AerialMast_Scrapper": 2,
     "RM_AerialWallBracket_Scrapper": 1
    }
   ]
  },
  "7": {
   "afterLooks": [
    "Industrial"
   ],
   "runs": [
    {
     "PowerConduit_Industrial": 8
    },
    {
     "PowerConduit_Modern_Orange": 4
    },
    {
     "PowerConduit_Industrial": 13
    }
   ]
  },
  "8": {
   "afterLooks": [
    "Scrapper"
   ],
   "runs": [
    {
     "PowerConduit_Scrapper": 5
    },
    {
     "PowerConduit_Futuristic": 5
    },
    {
     "PowerConduit_Scrapper": 11
    }
   ]
  },
  "9": {
   "afterRuns": 2,
   "runs": [
    {
     "PowerConduit_Industrial": 11
    },
    {
     "PowerConduit_Industrial": 5
    },
    {
     "PowerConduit_Industrial": 5
    }
   ]
  },
  "10": {
   "anchors": [
    [
     "RM_AerialMast",
     "RM_AerialMast_Scrapper",
     [
      "Scrapper",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialLampMast",
     "RM_AerialLampMast_Scrapper",
     [
      "Scrapper",
      "AerialLampMast"
     ]
    ]
   ],
   "runs": [
    {
     "PowerConduit_Scrapper": 12,
     "PowerSwitch_Scrapper": 1,
     "RM_AerialLampMast_Scrapper": 1,
     "RM_AerialMast_Scrapper": 1
    }
   ]
  },
  "11": {
   "reels": [
    [
     "Futuristic",
     "RM_HoseReel_Futuristic",
     "deployed"
    ],
    [
     "Futuristic",
     "RM_HoseReel_Futuristic",
     "stored"
    ],
    [
     "Modern",
     "RM_HoseReel_Modern",
     "deployed"
    ],
    [
     "Modern",
     "RM_HoseReel_Modern",
     "stored"
    ],
    [
     "Industrial",
     "RM_HoseReel_Industrial",
     "deployed"
    ],
    [
     "Industrial",
     "RM_HoseReel_Industrial",
     "stored"
    ],
    [
     "Scrapper",
     "RM_HoseReel_Scrapper",
     "deployed"
    ],
    [
     "Scrapper",
     "RM_HoseReel_Scrapper",
     "stored"
    ]
   ],
   "runs": []
  },
  "12": {
   "anchors": [
    [
     "RM_AerialMast",
     null,
     [
      "Scrapper",
      "AerialMast"
     ]
    ],
    [
     "RM_AerialLampMast",
     null,
     [
      "Scrapper",
      "AerialLampMast"
     ]
    ]
   ],
   "reels": [
    [
     "Scrapper",
     null,
     "deployed"
    ]
   ],
   "runs": [
    {
     "null": 13
    }
   ]
  }
 },
 "styled_refused": [],
 "wall_s": 59.8
}
```
