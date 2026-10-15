# Gimme Some Slack - human review key sheet

41 stations; every card leads with how to POKE it and what to LOOK FOR (the suspected weak spot). Coverage of every feature: `src/RimMandrake/GimmeSomeSlack/review/COVERAGE.md`.

Built by `src/RimMandrake/GimmeSomeSlack/human_review.py`. Game paused, god mode on, weather clear, noon, Peaceful.

**This map reviews the per-build style design** (`design/RimMandrake/messyconduit_style_per_build_design.md`, your decisions of 2026-10-04): the look is picked on the build button and stored on each piece. Stations 1-11 are built through that machinery and stand side by side in four looks. `--style` (Mod Settings 'Default style') now only sets the DEFAULT look, which station 12 and every station 13-40 but 34 draw because they store no look. Default look now: **Scrapper**.

Jump the camera: `human_review.py --goto N` (N = station; S0 = style gallery 1-12; 0 = whole south region; N0 = north gallery 18-33 and 38-41; M = art board; F = free area).

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

**Poke it:** flick the switch; Restyle this run; build one conduit into the gap in another look

**Look for / suspected weak spot:** the tangle's pieces may follow the DEFAULT look, not the run's (known gap); only the battery side of the gap may spark

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

**Poke it:** as 1: switch, Restyle this run, fill the gap

**Look for / suspected weak spot:** Industrial picks a cable kind per net: does the tangle or a cut half pick a different kind?

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

**Poke it:** as 1; also restyle to random mix and back

**Look for / suspected weak spot:** the 2 cells past the gap are a run of their own and may take another colour: confusing or fine?

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

**Poke it:** as 1

**Look for / suspected weak spot:** fallback pieces (power strip, live end) borrowed from Scrapper: do they jar in Futuristic?

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

**Poke it:** build one conduit onto a run's end; restyle the blue run to random mix and back

**Look for / suspected weak spot:** random mix: a colour may change only at a node, never mid-cord; restyling back must bring the same colours back

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

**Poke it:** select a pole > Restyle this run; Link wire across to another row

**Look for / suspected weak spot:** the span cable has no per-look art (falls back): does each row's wire still read as its look?

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

**Poke it:** build ONE conduit into the upper row's gap (hover first)

**Look for / suspected weak spot:** the hover hint must say 'bridges Industrial + Modern runs: Industrial wins' BEFORE the click; the message must name both looks

**Notice**

- after row: the joining cell was built as Futuristic, yet the whole run is now Industrial: the run with more conduit cells wins and the smaller one is repainted
- a message named both looks when it happened
- the Modern lamp lit: one run, one power net

**Try**

- before row: build ONE conduit in the gap from the menu (any look, god mode = instant): watch the 4 orange cells turn Industrial and read the message
- make the orange run longer first (5+ more cells), then join: now orange wins

### 8. MERGE: A TIE

two equal runs (5 cells each): Scrapper built FIRST (older), Futuristic built after

**Poke it:** deconstruct one Scrapper cell, then join the gap

**Look for / suspected weak spot:** tie goes to the OLDER run: a rebuilt (younger) cell must not make its run count as newer

**Notice**

- after row: joined with an Industrial cell, the whole run is Scrapper: on a tie the OLDER run wins
- a message named both looks

**Try**

- before row: build one conduit in the gap: Scrapper should win
- deconstruct one Scrapper cell first (4 vs 5), then join: Futuristic wins

### 9. SPLIT KEEPS THE LOOK

an Industrial run of 11 cells; the after row had its middle cell deconstructed

**Poke it:** deconstruct the marked cell in the upper row

**Look for / suspected weak spot:** after the split a half may re-pick its Industrial cable kind (the colour-reshuffle bug)

**Notice**

- after row: two runs, BOTH still Industrial (nothing is re-defaulted)
- WATCH: Industrial picks a cable kind (black rubber / corrugated steel / coiled) per cord net; if a half changes cable kind after the split, that is the colour-reshuffle bug the test plan predicts (SR6/SR7)
- the far lamp is dark: the split cut its power

**Try**

- before row: deconstruct the marked cell yourself
- build it back in another look: it adopts the bigger half's look

### 10. RESTYLE THIS RUN (yours)

a Scrapper run (battery, conduit, an in-line switch, a lamp) with a power mast wired into its end and a span to a lamp mast: nothing restyled yet, the button is yours

**Poke it:** select any piece > Restyle this run; then the lamp > Restyle this lamp

**Look for / suspected weak spot:** the lamp's own look must survive the next run restyle; 'Match its cable run' must undo it; the span must restyle with the poles

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

**Poke it:** Deploy / Retract each reel; build a reel from the menu

**Look for / suspected weak spot:** a reeled-in drum must be full again in the SAME look (FlowWorks feature)

**Notice**

- laid: the reel draws its EMPTY drum (hose out) and the hose leaves the drum's mouth in the reel's own look
- hose strand, wraps, couplings, nozzle or end cap: all in the reel's look (non-Scrapper wraps have no cloth tint)
- reeled in: the drum is full again and the style is kept
- NOT BUILT: the design's coil overlay; the reel swaps between two whole images instead (art board M)

**Try**

- select a reel: Deploy hose / Retract hose (dev mode: the instant DEV ones); lay the reeled-in one again: same look
- build a new reel from the menu: four looks on the button; copy a reel: the copy keeps its look

### 12. OLDER SAVE: NO STORED LOOK

conduit, a switch, a lamp, a power mast with a span to a lamp mast and a laid hose reel, all built OUTSIDE the menu (as in a save from before this change): nothing stores a look

**Poke it:** `--style Cybertek`: this set and 13-40 (not 34) change, 1-11 do not; build one conduit onto it

**Look for / suspected weak spot:** the hose reel here follows FlowWorks' default, not --style: it will look like it ignored the switch

**Notice**

- everything draws the DEFAULT look (Mod Settings 'Default style', `--style`): the same as before the change; the hose reel is the exception: it draws FlowWorks' own default ('Look of reels built without a picked look', Scrapper here)
- every station from 13 on is built the same way (except 34 and 41, which store a look), so it follows the default too

**Try**

- `human_review.py --style Cybertek` (or Mod Settings): this set and stations 13-40 change (not 34, not the hose reels: their default is FlowWorks' setting); stations 1-11 do NOT
- build one conduit onto it from the menu: the run's look is written for real now (the save migration)

## Row A - floor cords (default look)

### 13. WALL + ROCK ENTRIES

a run passing under a steel wall and through a granite block; a branch ending inside the wall

**Poke it:** deconstruct a wall cell; mine the granite

**Look for / suspected weak spot:** the NORTH-face plate is a sliver: is it there at all? no curl of cord printed on any plate

**Notice**

- where the cord meets the wall it goes into a plate mounted ON the wall (round 4): a thin edge-on strip inside a west or east face, the whole plate on a south face's lit band, a sliver on a hidden north face; nothing pokes out onto the floor
- the cord meets the plate straight (no hooked curl of cord printed on the plate)
- the rock tunnel has rock holes on both faces, inside the rock, the same way
- the branch ending in the wall is a wall terminal: its loose wire leaves the socket straight out of the wall and lies on the floor (on a south face it hangs straight down the face)

**Try**

- deconstruct a wall cell: the cord re-plans across the gap
- mine the granite: the tunnel opens

## Row B - overhead lines (default look)

### 14. CUT + FALLEN SPAN

battery -> power mast -> mast -> mast -> lamp, two 12-cell overhead spans, the SECOND span cut (as if blown by an explosion)

**Poke it:** middle mast > Re-string cut wires; dev: an explosion under the first span

**Look for / suspected weak spot:** both cut halves must meet on the ground at ONE point; the 'Wire down' alert must list this mast

**Notice**

- each cut half is ONE wire in the span's own cable: from the mast's insulator down to the break, where both halves meet on the ground
- the live downed end sparks; the far lamp is dark
- the first span still hangs and still carries power
- the alert list (right edge) shows 'Wire down'; clicking it jumps to the mast (round 8)

**Try**

- select the middle mast > Re-string cut wires: the span goes back up and the lamp relights
- god mode: drop an explosion under a span (dev tools) to cut another

### 15. POWER TAP

a power-tap clamp biting ANOTHER faction's grid (left, hostile battery), drained one-way into our lamp (right)

**Poke it:** unpause: their battery drains; Mod Settings taps off; dev: spawn one of THEIR pawns near the clamp and unpause

**Look for / suspected weak spot:** the clamp sits ON their cord (v3 pose), not on the node; their net and ours stay two nets; a seen clamp must send 'Power theft discovered' and cost goodwill each day

**Notice**

- the crocodile clamp sits on their conduit; one of our cords is taped to it
- the two grids never merge (their net and ours stay separate)
- our lamp is lit with no power source of our own

**Try**

- unpause and watch their battery drain
- Mod Settings > Gimme Some Slack > taps off: our lamp goes dark
- round 8: dev-spawn one of THEIR pawns within 12 cells, in sight of the clamp, and unpause: a 'Power theft discovered' letter, then their goodwill falls 2 a day while the clamp drains (`--goto` sweeps that pawn away again)

## Row C - flexible hoses: states, lanes and crossings

Hoses never branch (ruled by card): one hose is one line with two ends. Shown as the system does it today; there is no crossing piece.

### 16. HOSE STATES

three hoses laid side by side, two cells apart (top to bottom): FLAT (nothing flowing), FILLING (flow on, frozen half-way through filling), PLUMP (flow on, fully filled)

**Poke it:** unpause: the filling hose finishes in about half a second

**Look for / suspected weak spot:** a straight hose must have NO joiner; filling must not jump straight to plump (FlowWorks)

**Notice**

- flat: the hose lies flat and thin; a straight hose has NO joiner along it; the free end is a plain open end the hose's own width
- filling: half-plump, the swell is mid-transition; UNPAUSE and it finishes plumping in ~half a second
- plump: a full round hose, visibly wider than the flat one; still no joiner on the straight
- lanes: each hose keeps its own lane; where their S-curves meet, one draws over the other cleanly (the newer reel's on top)

**Try**

- select the reel: Deploy hose / Move hose end / Retract hose (a colonist carries it) and the 'Free end' gizmo (nozzle / end cap / open); dev mode adds 'DEV: lay hose instantly' / 'DEV: reel in instantly'
- dev mode: the reel's 'DEV: flow through hose' gizmo fakes flow (no tank, pump or pipe feeds these reels, so nothing moves real liquid through them)
- NOT designed: there is no crossing piece and no T or + hose fitting (hoses never branch, by ruling)

### 17. HOSE GRID

four hoses, two each way, crossing in a 2 x 2 grid

**Poke it:** lay a fifth hose across the grid

**Look for / suspected weak spot:** where S-curves run side by side two hoses may overlap for a stretch (FlowWorks)

**Notice**

- four crossings: every one is over/under, with a fixed order (newest on top)
- FINDING to judge: where the S-curve slack of two hoses runs along each other they may overlap for a stretch

**Try**

- select the reel: Deploy hose / Move hose end / Retract hose (a colonist carries it) and the 'Free end' gizmo (nozzle / end cap / open); dev mode adds 'DEV: lay hose instantly' / 'DEV: reel in instantly'
- dev mode: the reel's 'DEV: flow through hose' gizmo fakes flow (no tank, pump or pipe feeds these reels, so nothing moves real liquid through them)
- NOT designed: there is no crossing piece and no T or + hose fitting (hoses never branch, by ruling)

## Row E - power showpieces (north gallery)

Round 2 (owner notes 2026-10-04): a pole with many kinds of devices, a crowded electric room under an overhead line, a span over a hidden stone block.

### 18. POLE CLUSTER

one power pole with a wide mix of devices: some right beside it (lamp, heater, sun lamp, mini-turret, two batteries), some reached by conduit runs (stove, hi-tech research bench, TV), a walk-in freezer with an in-wall cooler and wall lamps inside and out, and a lamp mast fed over the air

**Poke it:** build another lamp right beside the pole

**Look for / suspected weak spot:** more hookups than insulators: do two pile onto one tip? a cord must meet a big device's edge, not stop short

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

### 19. ELECTRIC ROOM

a walled workshop crammed with powered devices joined by messy conduit (with a tangle), and three power poles carrying a line OVER it: west pole outside, middle pole inside the room, east pole outside

**Poke it:** roof the room (god mode): the middle pole's spans must drop

**Look for / suspected weak spot:** noise: does it still read as a room? any cord drawn ON TOP of a device's art

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

### 20. OVER THE UNKNOWN

two power poles carrying power OVER a solid granite block that lies hidden under fog of war and overhead mountain: the wire runs off into the unknown and emerges on the other side

**Poke it:** mine into the block from the west

**Look for / suspected weak spot:** any wire or shadow drawn ON the fog is a leak of the unknown

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

### 21. HOSE MAZE: TWO ROUTES

a hose laid from a reel deep inside a small walled maze to a free end outside; two ways out: the short one (south-east gap) and a longer one (north-east gap)

**Poke it:** reel in, lay again to the same end

**Look for / suspected weak spot:** a bend clipping a wall corner in a one-cell corridor (FlowWorks)

**Notice**

- the hose finds the SHORT route out through the inner chamber's west door, down and out the south-east gap
- it never clips a wall corner, and its bends stay smooth in the one-cell corridors
- it stays inside the corridors (it never jumps a wall)

**Try**

- select the reel: Deploy hose / Move hose end / Retract hose (a colonist carries it) and the 'Free end' gizmo (nozzle / end cap / open); dev mode adds 'DEV: lay hose instantly' / 'DEV: reel in instantly'
- dev mode: the reel's 'DEV: flow through hose' gizmo fakes flow (no tank, pump or pipe feeds these reels, so nothing moves real liquid through them)
- reel it in and lay it again to the same free end: does it pick the same route?

### 22. HOSE MAZE: SHORT WAY WALLED

station 21's maze; after the hose is laid, a wall is built across the short (south-east) gap - does the hose re-route the long way, or reel itself in?

**Poke it:** deconstruct the blocking wall

**Look for / suspected weak spot:** the hose must re-route or reel in with a message, never pass through the wall (FlowWorks)

**Notice**

- what the hose does when its route is blocked AFTER laying: it re-routes north-east if that still fits the hose length (it does: measured offline the long way needs about 25 of the hose's 40 cells), else it winds back onto the reel with a message and an alert saying how many cells the way round needs (HOSE_BLOCKED_REROUTE_RETRACT_1)
- add your own walls to lengthen the way round: past 40 cells (the default since round 6) the hose reels in (selftest r5: the 13x13 spiral needs 73)
- if it re-routes, the new path is as clean as station 21's

**Try**

- select the reel: Deploy hose / Move hose end / Retract hose (a colonist carries it) and the 'Free end' gizmo (nozzle / end cap / open); dev mode adds 'DEV: lay hose instantly' / 'DEV: reel in instantly'
- dev mode: the reel's 'DEV: flow through hose' gizmo fakes flow (no tank, pump or pipe feeds these reels, so nothing moves real liquid through them)
- reel it in and lay it again to the same free end: does it pick the same route?
- deconstruct the blocking wall (cells 12,1 and 12,2): does the hose go back to the short way?

## Row G - challenge configurations (north gallery)

Built to make visible bugs show: map edge, water, roof edge, longest/odd spans, a full pole, neighbouring nets, half-built work and save-load.

### 23. MAP EDGE

poles and cords at the map's north-east corner: a pole IN the corner cell, poles on the top and right edge cells, and floor runs lying along both edges

**Poke it:** pan the camera past the map edge

**Look for / suspected weak spot:** anything drawn in the black past the edge; a red error naming GimmeSomeSlack

**Notice**

- the cords' loose curls must not draw off the map (nothing hanging past the edge, nothing cut off with a hard line)
- the corner pole's wires and shadow stay on the map
- no red errors (open the debug log: none mentioning GimmeSomeSlack)

**Try**

- pan the camera to the edge: is anything drawn in the black past the map?
- deconstruct the corner pole: both its spans drop

### 24. RIVER CROSSING

a river (chest-deep moving water, shallow banks): an overhead span from bank to bank, and a floor run fording the shallow end in waterproof conduit

**Poke it:** unpause; deconstruct one waterproof cell in the river

**Look for / suspected weak spot:** the overhead shadow as a dark stripe on the river bed; cut ends in water still sparking?

**Notice**

- the overhead wire's shadow falls on the water like on the ground (or not at all), never as a dark stripe on the river bed
- the floor cord on the water: does it float, sink or draw on top as if on soil? (waterproof conduit has its own look?)
- the cords' curls do not wander into the deep water
- both far devices are lit

**Try**

- unpause: the river flows; does the cord on the water move with it (it should not)?
- deconstruct one waterproof conduit cell in the river: the cut ends lie in water - do they still spark?

### 25. ROOF BOUNDARY

a roofed steel room: an overhead span passes OVER its roof, a floor run goes in under the wall, and a pole standing INSIDE under the roof tries to link out

**Poke it:** build a roof over the east pole (god mode)

**Look for / suspected weak spot:** the inside pole must stay refused (Roofed); a seam where the floor cord passes the roof edge

**Notice**

- wires over a roof are allowed: the span is drawn over the roof, its shadow on the roof
- the pole under the roof is refused (anchors need open sky): no wire through the roof
- the floor cord inside the room: drawn under the roof shading, no seam where it passes the roof edge
- the lamp and heater inside are lit

**Try**

- roof overlay on (bottom-right) to see the roof edge
- build a roof over the east pole (god mode): its span drops (roof cut)
- remove the room's roof: link the inside pole from its gizmo

### 26. LONG SPAN + DIAGONALS

four chains: a span of EXACTLY the longest length (20), one cell too long (21, refused), a 45-degree diagonal chain, an odd-angle span, and a very short span (3 cells)

**Poke it:** Link wire on the 21-cell pair; Mod Settings Longest span 25, link again

**Look for / suspected weak spot:** the 20-cell sag dipping under the ground; diagonal wires leaving from the pole's middle

**Notice**

- the 20-cell span: the deepest sag; it must not touch or dip below the ground, and its shadow stays a smooth curve
- the 21-cell pair stays unlinked and its lamp dark (refused: too far)
- diagonals: the wire leaves from the insulator tips on the correct side of the crossarm, not from the pole's middle
- the odd-angle span: no kink or zig-zag where it changes direction
- the 3-cell span: nearly no sag, but the wire still meets both insulators (not a straight line through the poles)

**Try**

- select a mast > Link wire to the 21-cell partner: the message says too far
- Mod Settings: raise the longest span to 25: then link it

### 27. CONVERGING HUB

a hub pole with four spans (its maximum) arriving from N, E, S and W, a FIFTH pole trying to link (refused: full), and three lamps plus a heater right beside the hub

**Poke it:** unlink one spoke, then link the NE pole

**Look for / suspected weak spot:** four wires on one crossarm: an overlapping blob at the tips

**Notice**

- four wires meet on one crossarm: each lands on an insulator tip, none crossing through the pole art
- with more wires than insulators, do two share a tip cleanly or overlap in a blob?
- the fifth (NE) pole stays unlinked, its lamp dark
- the hub's local hookups: which terminal does each lamp take?

**Try**

- unlink one spoke, then link the NE pole: it takes the freed slot
- deconstruct the hub: four spans drop at once

### 28. NETS SIDE BY SIDE + HALF-BUILT

three separate powered nets two cells apart; two nets end to end with a one-cell gap that is a conduit BLUEPRINT; a half-built run (conduit, then blueprints, a pole blueprint, a lamp blueprint)

**Poke it:** build the gap blueprint; SAVE then LOAD here

**Look for / suspected weak spot:** after the load every cord must return with the same curls and colours

**Notice**

- side by side: each net's cords stay with its own net (no cord jumping across to the neighbour's run)
- Modern look, 'a different colour per power net': three nets = three colours; after the gap is built, the two merged nets should become ONE colour
- blueprints draw no cords (a cord never runs to a ghost)
- SAVE then LOAD the game here: every cord comes back the same (same curls, same colours), blueprints still cord-free
- select one lamp: only its own net's cords highlight, never the neighbour's (Mod Settings 'highlights every cord of its net')

**Try**

- god mode: build the gap blueprint (or unpause and let colonists build): nets merge, the dark lamp lights
- save, load, compare (this is the save-load station)
- --style ExtensionCord for the colour checks

### 29. RELAY REELS: GOING FARTHER

three hose reels in a row, 32 cells apart: the first reel's hose is laid onto the second reel, whose own hose is laid onto the third (66 cells end to end; one hose holds 40)

**Poke it:** reel in the first hose: the second drains

**Look for / suspected weak spot:** a relay that loops back must be refused (FlowWorks)

**Notice**

- each hose ends in a brass coupling on the NEXT reel's side: the chain reads connected, not two loose hoses
- flow into the first reel (dev gizmo, on): its hose plumps, and the second reel's hose plumps too -- it is fed through the relay (the dev flag stands in for real liquid: no tank or pipe feeds the first reel here)
- select the middle reel: 'Relay: fed by the hose from the reel at ...'; each hose shows its own 'N of 40 cells'

**Try**

- select the reel: Deploy hose / Move hose end / Retract hose (a colonist carries it) and the 'Free end' gizmo (nozzle / end cap / open); dev mode adds 'DEV: lay hose instantly' / 'DEV: reel in instantly'
- dev mode: the reel's 'DEV: flow through hose' gizmo fakes flow (no tank, pump or pipe feeds these reels, so nothing moves real liquid through them)
- reel in the first hose: the second one drains (nothing feeds it)
- lay the third reel's hose back onto the first: refused, a chain may not loop back
- build a fourth reel within 40 cells of the third (north or south: east is the map edge) and lay the third reel onto it: the chain goes on

### 30. DEPLOY BY HAND, THEN WIND IT IN

a hose reel with a Deploy order 24 cells out and one idle colonist beside it (UNPAUSE: nothing else is ordered); after he lays it, press Retract

**Poke it:** UNPAUSE, then press Retract after he lays it

**Look for / suspected weak spot:** the hose must never be longer than his walk; Retract must wind back along the route (FlowWorks)

**Notice**

- the colonist walks to the reel, picks up the hose end and walks it out: the hose unrolls behind him along his walk
- he sets the end down at the order's cell and the hose lies there, coupled
- the hose is never longer than his walk: it does not jump out to the target
- after he lays it, press Retract on the reel: he winds the hose back along its route to the reel
- the free end runs back along the hose's route; the hose gets shorter, it does not vanish at once
- it ends Stored: no hose on the ground, the reel's drum full

**Try**

- select the reel: the gizmos are the player orders (Deploy hose / Move hose end / Retract hose); the instant 'DEV:' ones appear only with dev mode on
- draft him mid-walk: the end drops where he stands (see station 31)

### 31. DROPPED HALFWAY

a reel whose hose end was dropped 14 cells out (an interrupted carry)

**Poke it:** Move hose end to a nearby cell, unpause

**Look for / suspected weak spot:** nobody should be shown carrying anything until a colonist picks it up (FlowWorks)

**Notice**

- the open end lies on the ground at the end of the hose; the hose is drawn only as far as it was walked
- select the reel: 'Move hose end' and 'Retract hose' are offered; no colonist is carrying anything

**Try**

- select the reel: the gizmos are the player orders (Deploy hose / Move hose end / Retract hose); the instant 'DEV:' ones appear only with dev mode on
- Move hose end to a cell beside it, then unpause: an idle colonist picks the end up and walks it there

### 32. INTO THE POND

a reel 10 cells from a pond, its hose laid into the water

**Poke it:** select the reel: inspect

**Look for / suspected weak spot:** the end must lie IN the water, not on the bank; it draws nothing by itself (FlowWorks)

**Notice**

- the hose end lies in the water, not on the bank
- a hose end in water draws nothing by itself (owner ruling 2026-10-11 #3): the reel's inspect reads 'Not connected' and 'Hose laid to ...'; the end's own reading 'lying in ... (no intake: filling a tank takes a pump)' is a state read (HoseProbe census freeEnd.describe), not shown in the inspect pane

**Try**

- select the reel: the gizmos are the player orders (Deploy hose / Move hose end / Retract hose); the instant 'DEV:' ones appear only with dev mode on

### 33. ON THEIR TANK

a hose coupled to another faction's liquid tank

**Poke it:** select the reel and the tank

**Look for / suspected weak spot:** the coupling must sit on their tank; nobody's inspect names their faction (FlowWorks)

**Notice**

- a brass coupling sits on THEIR tank where the hose ends
- their faction is a state read (HoseProbe census freeEnd.portFaction / describe 'coupled to ... (<faction>)'); neither the reel's nor the tank's inspect names it

**Try**

- select the reel: the gizmos are the player orders (Deploy hose / Move hose end / Retract hose); the instant 'DEV:' ones appear only with dev mode on

## Row H - pieces the gallery never showed (south band, added 2026-10-15)

From the feature inventory (review/COVERAGE.md): waterproof conduit in four looks, the three conduit kinds, a bracket on every wall face, the tap clamp's poses.

### 34. WATERPROOF CONDUIT: FOUR LOOKS

four runs of waterproof conduit, one per look (top to bottom: Scrapper, Industrial, Modern, Futuristic), each from a full battery across a shallow-water strip to a lamp in its look

**Poke it:** Mod Settings > Which conduits become cords > untick Waterproof

**Look for / suspected weak spot:** the cord in the water: does it dive, or lie on top as if on soil?

**Notice**

- each run draws its look's cord on soil AND in the water: waterproof conduit is the same cord as plain conduit
- in the water the cord dives (Mod Settings 'cords dive under walls and water'): it should not lie on top of the water as if on soil
- all four lamps lit

**Try**

- select a cell > Restyle this run: the waterproof run takes any look, like plain conduit
- Mod Settings > 'Which conduits become cords' > untick Waterproof conduit: these four runs go back to vanilla art

### 35. CONDUIT KINDS

three runs in the DEFAULT look, top to bottom: plain power conduit, waterproof conduit (on soil), hidden conduit; each from a full battery to a lamp. The plain row has a 2-cell dead-end stub hanging down

**Poke it:** untick one conduit kind; `--set gss.needlessLoops=False`; `--set gss.enabled=False`

**Look for / suspected weak spot:** hidden conduit must draw NOTHING; the stub's loop must not reach the waterproof row; an unticked kind must go vanilla without a reload

**Notice**

- plain and waterproof draw the same messy cord
- the 2-cell stub is drawn as a pointless loop of cord, not a stub (Mod Settings 'Needless conduit stubs become pointless loops')
- hidden conduit stays hidden: no cord at all, the lamp still lit
- all three lamps lit

**Try**

- Mod Settings > 'Which conduits become cords': untick one kind and only that row returns to vanilla art
- `human_review.py --set gss.enabled=False` (master switch): every row is vanilla conduit art at once

### 36. WALL BRACKETS: EVERY FACE

a 3x3 steel wall block with a wall bracket on each face (north, east, south, west), all four strung from one power mast; a lamp beside each bracket

**Poke it:** select a bracket > Unlink wire, then Link wire

**Look for / suspected weak spot:** the west bracket is the east art mirrored: is its insulator on the right side? the north one mostly hidden

**Notice**

- each bracket sits flat on its own face: the east and west ones mirror each other, the north one shows only a sliver (the wall hides most of it), the south one shows whole
- each wire lands on the bracket's insulator, not on the wall or the bracket's middle
- all four lamps lit

**Try**

- select a bracket > Unlink wire: only its lamp goes dark; Link wire to put it back
- deconstruct a wall cell under a bracket: the bracket has nothing to hang on (what happens to it?)

### 37. TAP CLAMP POSES

their grid (hostile batteries) as one east-west cord and one north-south cord; four of our clamps bite them, our cord arriving from the north, the south, the west and the east; a lamp on each

**Poke it:** `--style Cybertek` (or any look): four clamp arts

**Look for / suspected weak spot:** north-south cord: handles must turn AWAY from our cord's side; jaws along their cord, never across

**Notice**

- each clamp's jaws grip THEIR cord just in from where ours meets it, laid along their cord
- on the east-west cord the handles stand upright; on the north-south cord they turn away from the side our cord comes from
- the clamp draws in the look of the run it bites: their conduit stores no look, so all four follow the DEFAULT look
- all four lamps lit, on no power of our own; their grid and ours never merge

**Try**

- `human_review.py --style Cybertek` (or any look): all four clamps change art (the four clamp looks)
- unpause: clamp sparks (Mod Settings 'Spark intensity' and 'Sparks only while the power overlay is open' govern them)
- try to build a clamp on YOUR OWN conduit (free area): what does the game say?

## Row I - wiring, hazards, ownership, blueprints (north gallery, added 2026-10-15)

Auto-link selected, a cut wire's hazards (shock, spilled fuel, the alert), a claimed enemy pole, and the look riding a blueprint.

### 38. AUTO-LINK SELECTED

five power masts standing unlinked (one touches a full battery) and two dark lamps beside the far masts

**Poke it:** select all five masts > Auto-link selected

**Look for / suspected weak spot:** exactly 4 wires, no loop, no doubled wire; a full mast must be skipped

**Notice**

- nothing is strung: no wire, no shadow, both lamps dark

**Try**

- select all five masts > 'Auto-link selected': the shortest set of wires that joins them all (4 wires), both lamps light
- undo with Unlink all on each, then link them by hand with 'Link wire' and compare

### 39. FALLEN WIRE HAZARDS

battery -> mast -> mast -> lamp, the span CUT; spilled fuel lies around the live end on the ground

**Poke it:** draft a colonist onto the live end; unpause

**Look for / suspected weak spot:** the thrown-back pawn landing inside a wall or off the map; fuel lit by the DEAD half

**Notice**

- the top-right alert reads 'Wire down'; clicking it jumps to the mast
- the live end sparks on the fuel; the far lamp is dark
- UNPAUSE: the live end lights the spilled fuel (Mod Settings 'Live fallen wires light spilled fuel')

**Try**

- draft a colonist and walk him onto the live end: he is shocked and thrown back about 2 cells (a weak heart can die; Mod Settings 'shock' / 'thrown back')
- select the battery-side mast > Re-string cut wires: the alert clears, the lamp relights

### 40. CLAIM THEIR POLE

two power masts of ANOTHER faction strung together, their battery at the south mast and their lamp at the north one

**Poke it:** select the north mast > Claim

**Look for / suspected weak spot:** the wire must coil AT ONCE and their lamp go dark; their grid must never fuse with ours

**Notice**

- their wire hangs between their poles like ours (same art, same sag)
- their lamp is lit by their battery

**Try**

- select the north mast > Claim (god mode: instant): the wire to their other pole is taken down and coiled at once, their lamp goes dark (Mod Settings 'Claiming a pole cuts wires to the other owner')
- claim the south mast too, then Link wire between them: one grid, yours

### 41. STYLED BLUEPRINTS

an Industrial run picked from the build menu but NOT built: conduit, an in-line switch and a floor lamp as blueprints, beside a full battery

**Poke it:** unpause and let colonists build it

**Look for / suspected weak spot:** the look lost at the frame stage, or a vanilla-looking ghost that builds Industrial

**Notice**

- each blueprint ghost already shows the Industrial look (or the vanilla ghost: which?)
- UNPAUSE: colonists haul steel from the free area and build; frame and finished piece keep the Industrial look

**Try**

- unpause and watch one cell go blueprint -> frame -> building
- cancel a blueprint and rebuild it from the menu in another look

## Expected refusals (shown on purpose)

- 25 ROOF BOUNDARY: link 0-2 is refused (Roofed).
- 26 LONG SPAN + DIAGONALS: link 2-3 is refused (OutOfRange).
- 27 CONVERGING HUB: link 0-5 is refused (FullA).

## Mod Settings: one switch each

Global settings change every station at once, so they are never faked side by side. Flip one live with `human_review.py --set gss.FIELD=VALUE` or `--set aerial.FIELD=VALUE` (the same field the Mod Settings window writes; `--set` again with the shipped value to undo), or in Mod Settings > Gimme Some Slack.

| setting | shipped | what it does | where to look |
|---|---|---|---|
| `gss.enabled` | True | Messy cords master switch (off = vanilla conduit art) | 35, any cord station |
| `gss.style` | StarWarsJawa | default look of unstyled pieces (also `--style`) | 12, 13-40 (not 34), 35, 37 |
| `gss.extCordColorMode` | Mixed | default Modern colour: one per net (Mixed) or one everywhere (Single) | 28 with --style ExtensionCord |
| `gss.extCordColor` | 0 | the single Modern colour (0 orange .. 4 blue) | 28 with Single |
| `gss.hideHookupWires` | True | hide vanilla's thin machine hookup wires | 18 |
| `gss.slack` | 1.0 | slack, 0 = path-tight | 1-4, 13 |
| `gss.loopBudget` | 16 | cells of each cord in loops and heaps | 1-4 |
| `gss.cordsPerConnection` | 3 | cords per connection, 1 to 3 | 1-4, 19 |
| `gss.tangles` | True | dense conduit fields become one tangle | 1-4 (the 3x3), 19 |
| `gss.tangleMin` | 9 | cells before a dense field becomes a tangle | 1-4, 19 |
| `gss.needlessLoops` | True | needless stubs (2 cells or less) become pointless loops | 35 (the stub) |
| `gss.diveThrough` | True | cords dive under walls and water (a plate marks the wall) | 13, 24, 34 |
| `gss.breakReadout` | True | live ends spark, dead ends lie limp | 1-4, 14 |
| `gss.sparkIntensity` | 1.0 | spark intensity (also clamp sparks) | 1, 14, 37, 39 |
| `gss.whip` | True | live broken floor ends whip (also paused) | 1-4 |
| `gss.downedWire` | True | live wires hanging out of walls drip sparks | 13 |
| `gss.sparksOnlyOverlay` | False | sparks only while the power overlay is open | 14, 39 |
| `gss.maxSparkingEnds` | 24 | most sparking ends per map | no station (needs 24+ live ends on one map) |
| `gss.highlight` | True | selecting a powered building highlights its net's cords | 28 |
| `gss.sway` | True | hanging cords sway in the wind | 13 (unpause) |
| `gss.swayAmplitude` | 1.0 | cord sway strength | 13 |
| `gss.swayMode` | CPU | cord sway on the CPU or the plant wind shader | 13 |
| `gss.floorRipple` | False | outdoor floor cords ripple | 1-4 (unpause) |
| `gss.excludedConduits` | [] | which conduits become cords (a list: Mod Settings window only) | 34, 35 |
| `gss.lod` | True | far zoom: one thin strand, no pieces | any: zoom out |
| `gss.debugDraw` | False | draw the node graph | any |
| `aerial.enabled` | True | overhead lines master switch | 6, 14, 18-28, 36-40 |
| `aerial.maxSpan` | 20 | longest span, cells | 26 |
| `aerial.sag` | 0.06 | sag, share of the span | 26 |
| `aerial.autoLink` | True | new anchors link to the nearest in range | F, 38 |
| `aerial.maxStrands` | 3 | wires per span, 1 to this | 6, 27 |
| `aerial.dripLoops` | False | drip loops at the insulators | 6 |
| `aerial.keepWiresOnGravship` | True | wires on a launched gravship stay strung | no station (needs a gravship launch) |
| `aerial.sway` | Auto | wire sway: Auto / CPU (always) / Off | 6, 26 (unpause) |
| `aerial.swayStrength` | 1.0 | wire sway strength | 6, 26 |
| `aerial.explosionsCut` | True | explosions cut wires | 14 |
| `aerial.kineticSway` | True | Kinetic Arms push waves swing wires, never cut | no station (needs a Kinetic Arms push wave) |
| `aerial.fallenWireShock` | True | live fallen wires shock whoever touches them | 39 |
| `aerial.fallenWireKnockback` | 2 | cells a shock throws the victim | 39 |
| `aerial.fallenWireIgnites` | True | live fallen wires light spilled fuel | 39 |
| `aerial.wireDownAlert` | True | the 'Wire down' alert | 14, 39 |
| `aerial.cutWiresOnOwnerChange` | True | claiming a pole coils wires to the other owner | 40 |
| `aerial.tapsEnabled` | True | power-tap clamps allowed | 15, 37 |
| `aerial.tapRate` | 500 | most a clamp takes, W | 15 |
| `aerial.tapEvents` | True | taps have consequences | 15 |
| `aerial.theftGoodwill` | True | caught theft drains goodwill | 15 (spawn one of their pawns) |
| `aerial.theftGoodwillPerDay` | 2 | goodwill lost per day | 15 |
| `aerial.theftSightRange` | 12 | victims spot a clamp within N cells | 15 |

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
| power mast top | own | own | own | own |
| lamp mast | own | own | own | own |
| lamp mast top | own | own | own | own |
| wall bracket (S face) | own | own | own | own |
| wall bracket (N face) | own | own | own | own |
| wall bracket (E/W face) | own | own | own | own |
| power-tap clamp | own | own | own | own |
| floor lamp | own | own | own | own |
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

North band, west end (`--goto F`): open soil. A charged power pad (2 solar generators, 3 full batteries) with a conduit stub labelled *plug in here*; steel, plasteel, components and wood along the south edge; a short run of ANOTHER faction's grid (*their grid: clamp here*) for a power-tap clamp, and a steel wall stub (*wall for brackets*). Every Gimme Some Slack buildable can be built here: conduit (plain, waterproof, hidden), switch, floor lamp, power mast, lamp mast, wall bracket, power-tap clamp. Use the build menus here to try the picker yourself: pick a look, build, extend, join two looks, restyle. God mode builds instantly; turn it off (dev toolbar) to watch colonists build from blueprints (the look rides blueprint -> frame -> building). Research is finished. No gallery mast is within 20 cells, so nothing you build links into the gallery.

## Old station -> new station (densified 2026-10-05)

Owner 2026-10-05: *"reduce the number of north Star verifications and verification stations for the human review sheet as well. If so, remove them."* Plan: `design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md` section 4. 47 stations -> 33: fifteen cut or merged, one new HOSE STATES station, the rest renumbered in order. Stations 34-41 were added 2026-10-15 (round 8); the old numbers in the left column are the 47-station map's, not today's.

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
| new | **34** | WATERPROOF CONDUIT: FOUR LOOKS |
| new | **35** | CONDUIT KINDS |
| new | **36** | WALL BRACKETS: EVERY FACE |
| new | **37** | TAP CLAMP POSES |
| new | **38** | AUTO-LINK SELECTED |
| new | **39** | FALLEN WIRE HAZARDS |
| new | **40** | CLAIM THEIR POLE |
| new | **41** | STYLED BLUEPRINTS |
| F | **F** | free build area |
| M | **M** | art-slot board |
