# Gimme Some Slack - human review key sheet

31 stations; every card leads with how to POKE it and what to LOOK FOR (the suspected weak spot). Coverage of every feature: `src/RimMandrake/GimmeSomeSlack/review/COVERAGE.md`.

Built by `src/RimMandrake/GimmeSomeSlack/human_review.py`. Game paused, god mode on, weather clear, noon, Peaceful.

**This map reviews the per-build style design** (`design/RimMandrake/messyconduit_style_per_build_design.md`, your decisions of 2026-10-04): the look is picked on the build button and stored on each piece. Stations 1-10 are built through that machinery and stand side by side in four looks. `--style` (Mod Settings 'Default style') now only sets the DEFAULT look, which station 11 and every station 12-30 but 24 draw because they store no look. Default look now: **Scrapper**.

Jump the camera: `human_review.py --goto N` (N = station; S0 = style gallery 1-11; 0 = whole south region; N0 = north gallery 15-23 and 28-31; M = art board; F = free area).

The hose is not on this map: it moved to FlowWorks, and so did its review stations (owner 2026-10-15: *"Get rid of those hoses..."*). They are on the FlowWorks review map (`src/RimMandrake/FlowWorks/review_map.py`).

## Everywhere

- Build menu: clicking a conduit, switch, pole, lamp mast, wall bracket or floor lamp button opens a menu of four looks (Scrapper, Industrial, Modern, Futuristic); conduit adds the Modern colour entries (random mix, one colour per run, orange, green, brown, yellow, blue). The button remembers your last pick.
- 'Restyle this run' sits on any selected conduit, switch or pole: it repaints the whole run (art only, free).
- A run = connected conduit cells + switches + the poles and brackets wired into them. Batteries and machines end a run. Joining two runs of different looks: the run with more conduit cells wins; a tie goes to the older run.
- Mod Settings > RimMandrake: Gimme Some Slack: master switch OFF restores vanilla conduit art instantly.
- Unpause (space) to see motion: sway, live-end sparks. Pause again to study a frame.

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

## Row U - an older save (style gallery)

### 11. OLDER SAVE: NO STORED LOOK

conduit, a switch, a lamp and a power mast with a span to a lamp mast, all built OUTSIDE the menu (as in a save from before this change): nothing stores a look

**Poke it:** `--style Cybertek`: this set and 12-30 (not 24) change, 1-10 do not; build one conduit onto it

**Look for / suspected weak spot:** the build must write the run's look for real; nothing here may change when only the stored looks (1-10) are touched

**Notice**

- everything draws the DEFAULT look (Mod Settings 'Default style', `--style`): the same as before the change
- every station from 12 on is built the same way (except 24 and 31, which store a look), so it follows the default too

**Try**

- `human_review.py --style Cybertek` (or Mod Settings): this set and stations 12-30 change (not 24); stations 1-10 do NOT
- build one conduit onto it from the menu: the run's look is written for real now (the save migration)

## Row A - floor cords (default look)

### 12. WALL + ROCK ENTRIES

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

### 13. CUT + FALLEN SPAN

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

### 14. POWER TAP

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

## Row E - power showpieces (north gallery)

Round 2 (owner notes 2026-10-04): a pole with many kinds of devices, a crowded electric room under an overhead line, a span over a hidden stone block.

### 15. POLE CLUSTER

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

### 16. ELECTRIC ROOM

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

### 17. OVER THE UNKNOWN

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

## Row G - challenge configurations (north gallery)

Built to make visible bugs show: map edge, water, roof edge, longest/odd spans, a full pole, neighbouring nets, half-built work and save-load.

### 18. MAP EDGE

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

### 19. RIVER CROSSING

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

### 20. ROOF BOUNDARY

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

### 21. LONG SPAN + DIAGONALS

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

### 22. CONVERGING HUB

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

### 23. NETS SIDE BY SIDE + HALF-BUILT

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

## Row H - pieces the gallery never showed (south band, added 2026-10-15)

From the feature inventory (review/COVERAGE.md): waterproof conduit in four looks, the three conduit kinds, a bracket on every wall face, the tap clamp's poses.

### 24. WATERPROOF CONDUIT: FOUR LOOKS

four runs of waterproof conduit, one per look (top to bottom: Scrapper, Industrial, Modern, Futuristic), each from a full battery across a shallow-water strip to a lamp in its look (plain conduit on the soil legs: vanilla allows waterproof conduit only on water or marsh)

**Poke it:** Mod Settings > Which conduits become cords > untick Waterproof

**Look for / suspected weak spot:** the cord in the water: does it dive, or lie on top as if on soil?

**Notice**

- each run draws its look's cord on soil AND in the water: the waterproof cells are the same cord as the plain ones
- in the water the cord dives (Mod Settings 'cords dive under walls and water'): it should not lie on top of the water as if on soil
- all four lamps lit

**Try**

- select a cell > Restyle this run: the waterproof run takes any look, like plain conduit
- Mod Settings > 'Which conduits become cords' > untick Waterproof conduit: these four runs go back to vanilla art

### 25. CONDUIT KINDS

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

### 26. WALL BRACKETS: EVERY FACE

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

### 27. TAP CLAMP POSES

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

### 28. AUTO-LINK SELECTED

five power masts standing unlinked (one touches a full battery) and two dark lamps beside the far masts

**Poke it:** select all five masts > Auto-link selected

**Look for / suspected weak spot:** exactly 4 wires, no loop, no doubled wire; a full mast must be skipped

**Notice**

- nothing is strung: no wire, no shadow, both lamps dark

**Try**

- select all five masts > 'Auto-link selected': the shortest set of wires that joins them all (4 wires), both lamps light
- undo with Unlink all on each, then link them by hand with 'Link wire' and compare

### 29. FALLEN WIRE HAZARDS

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

### 30. CLAIM THEIR POLE

two power masts of ANOTHER faction strung together, their battery at the south mast and their lamp at the north one

**Poke it:** select the north mast > Claim

**Look for / suspected weak spot:** the wire must coil AT ONCE and their lamp go dark; their grid must never fuse with ours

**Notice**

- their wire hangs between their poles like ours (same art, same sag)
- their lamp is lit by their battery

**Try**

- select the north mast > Claim (god mode: instant): the wire to their other pole is taken down and coiled at once, their lamp goes dark (Mod Settings 'Claiming a pole cuts wires to the other owner')
- claim the south mast too, then Link wire between them: one grid, yours

### 31. STYLED BLUEPRINTS

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

- 20 ROOF BOUNDARY: link 0-2 is refused (Roofed).
- 21 LONG SPAN + DIAGONALS: link 2-3 is refused (OutOfRange).
- 22 CONVERGING HUB: link 0-5 is refused (FullA).

## Mod Settings: one switch each

Global settings change every station at once, so they are never faked side by side. Flip one live with `human_review.py --set gss.FIELD=VALUE` or `--set aerial.FIELD=VALUE` (the same field the Mod Settings window writes; `--set` again with the shipped value to undo), or in Mod Settings > Gimme Some Slack.

| setting | shipped | what it does | where to look |
|---|---|---|---|
| `gss.enabled` | True | Messy cords master switch (off = vanilla conduit art) | 25, any cord station |
| `gss.style` | StarWarsJawa | default look of unstyled pieces (also `--style`) | 11, 12-30 (not 24), 25, 27 |
| `gss.extCordColorMode` | Mixed | default Modern colour: one per net (Mixed) or one everywhere (Single) | 23 with --style ExtensionCord |
| `gss.extCordColor` | 0 | the single Modern colour (0 orange .. 4 blue) | 23 with Single |
| `gss.hideHookupWires` | True | hide vanilla's thin machine hookup wires | 15 |
| `gss.slack` | 1.0 | slack, 0 = path-tight | 1-4, 12 |
| `gss.loopBudget` | 16 | cells of each cord in loops and heaps | 1-4 |
| `gss.cordsPerConnection` | 3 | cords per connection, 1 to 3 | 1-4, 16 |
| `gss.tangles` | True | dense conduit fields become one tangle | 1-4 (the 3x3), 16 |
| `gss.tangleMin` | 9 | cells before a dense field becomes a tangle | 1-4, 16 |
| `gss.needlessLoops` | True | needless stubs (2 cells or less) become pointless loops | 25 (the stub) |
| `gss.diveThrough` | True | cords dive under walls and water (a plate marks the wall) | 12, 19, 24 |
| `gss.breakReadout` | True | live ends spark, dead ends lie limp | 1-4, 13 |
| `gss.sparkIntensity` | 1.0 | spark intensity (also clamp sparks) | 1, 13, 27, 29 |
| `gss.whip` | True | live broken floor ends whip (also paused) | 1-4 |
| `gss.downedWire` | True | live wires hanging out of walls drip sparks | 12 |
| `gss.sparksOnlyOverlay` | False | sparks only while the power overlay is open | 13, 29 |
| `gss.maxSparkingEnds` | 24 | most sparking ends per map | no station (needs 24+ live ends on one map) |
| `gss.highlight` | True | selecting a powered building highlights its net's cords | 23 |
| `gss.sway` | True | hanging cords sway in the wind | 12 (unpause) |
| `gss.swayAmplitude` | 1.0 | cord sway strength | 12 |
| `gss.swayMode` | CPU | cord sway on the CPU or the plant wind shader | 12 |
| `gss.floorRipple` | True | outdoor floor cords ripple | 1-4 (unpause) |
| `gss.excludedConduits` | [] | which conduits become cords (a list: Mod Settings window only) | 24, 25 |
| `gss.lod` | True | far zoom: one thin strand, no pieces | any: zoom out |
| `gss.debugDraw` | False | draw the node graph | any |
| `aerial.enabled` | True | overhead lines master switch | 6, 13, 15-23, 26-30 |
| `aerial.maxSpan` | 20 | longest span, cells | 21 |
| `aerial.sag` | 0.06 | sag, share of the span | 21 |
| `aerial.autoLink` | True | new anchors link to the nearest in range | F, 28 |
| `aerial.maxStrands` | 3 | wires per span, 1 to this | 6, 22 |
| `aerial.dripLoops` | True | drip loops at the insulators | 6 |
| `aerial.keepWiresOnGravship` | True | wires on a launched gravship stay strung | no station (needs a gravship launch) |
| `aerial.sway` | Auto | wire sway: Auto / CPU (always) / Off | 6, 21 (unpause) |
| `aerial.swayStrength` | 1.0 | wire sway strength | 6, 21 |
| `aerial.explosionsCut` | True | explosions cut wires | 13 |
| `aerial.kineticSway` | True | Kinetic Arms push waves swing wires, never cut | no station (needs a Kinetic Arms push wave) |
| `aerial.fallenWireShock` | True | live fallen wires shock whoever touches them | 29 |
| `aerial.fallenWireKnockback` | 2 | cells a shock throws the victim | 29 |
| `aerial.fallenWireIgnites` | True | live fallen wires light spilled fuel | 29 |
| `aerial.wireDownAlert` | True | the 'Wire down' alert | 13, 29 |
| `aerial.cutWiresOnOwnerChange` | True | claiming a pole coils wires to the other owner | 30 |
| `aerial.tapsEnabled` | True | power-tap clamps allowed | 14, 27 |
| `aerial.tapRate` | 500 | most a clamp takes, W | 14 |
| `aerial.tapEvents` | True | taps have consequences | 14 |
| `aerial.theftGoodwill` | True | caught theft drains goodwill | 14 (spawn one of their pawns) |
| `aerial.theftGoodwillPerDay` | 2 | goodwill lost per day | 14 |
| `aerial.theftSightRange` | 12 | victims spot a clamp within N cells | 14 |

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

## F. Free build area

North band, west end (`--goto F`): open soil. A charged power pad (2 solar generators, 3 full batteries) with a conduit stub labelled *plug in here*; steel, plasteel, components and wood along the south edge; a short run of ANOTHER faction's grid (*their grid: clamp here*) for a power-tap clamp, and a steel wall stub (*wall for brackets*). Every Gimme Some Slack buildable can be built here: conduit (plain, waterproof, hidden), switch, floor lamp, power mast, lamp mast, wall bracket, power-tap clamp. Use the build menus here to try the picker yourself: pick a look, build, extend, join two looks, restyle. God mode builds instantly; turn it off (dev toolbar) to watch colonists build from blueprints (the look rides blueprint -> frame -> building). Research is finished. No gallery mast is within 20 cells, so nothing you build links into the gallery.

## Old station -> new station (densified 2026-10-05)

Owner 2026-10-05: *"reduce the number of north Star verifications and verification stations for the human review sheet as well. If so, remove them."* Plan: `design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md` section 4. 47 stations -> 33: fifteen cut or merged, one new HOSE STATES station, the rest renumbered in order. Eight stations were added 2026-10-15 (round 8, now 24-31), and the same day every hose station moved to the FlowWorks review map (owner: *"Get rid of those hoses..."*), leaving 31, renumbered in order. The old numbers in the left column are the 47-station map's, not today's.

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
| 11 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_reels_laid (owner 2026-10-15: hoses left Gimme Some Slack) |
| 12 | **11** | OLDER SAVE: NO STORED LOOK |
| 13 | **-** | removed -> covered by 1-4 (doc l.165 'powered line': the ground-cord stations) |
| 14 | **-** | removed -> covered by 1-4 (doc l.166 'unpowered line' (veto point): weakest distinct question; the matrix P=dead scenes cover it in state) |
| 15 | **-** | removed -> covered by 1-4 (doc l.167 'cut line': their missing cell, live + dead end) |
| 16 | **-** | removed -> covered by 1-4, 16 (doc l.168 'tangled pile': their 3x3 tangle; the electric room) |
| 17 | **-** | removed -> covered by 1-4, 15 (doc l.169 'devices + plugs': their switch + three plugged devices; the pole cluster) |
| 18 | **12** | WALL + ROCK ENTRIES |
| 19 | **-** | removed -> covered by 6, 10 (doc l.171 'mast chain': OVERHEAD: FOUR LOOKS has battery > mast > mast > lamp mast > wall bracket in all four looks; RESTYLE THIS RUN has a span) |
| 20 | **-** | removed -> covered by 6, 10 (doc l.171 'lamp masts': as the mast chain) |
| 21 | **-** | removed -> covered by 6, 10 (doc l.171 'wall bracket': as the mast chain) |
| 22 | **13** | CUT + FALLEN SPAN |
| 23 | **14** | POWER TAP |
| 24 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_states (owner 2026-10-15: hoses left Gimme Some Slack) |
| 25 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_states (owner 2026-10-15: hoses left Gimme Some Slack) |
| 26 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_states (owner 2026-10-15: hoses left Gimme Some Slack) |
| 27 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_maze, hose_maze_walled, hose_relay, hose_into_pond (owner 2026-10-15: hoses left Gimme Some Slack) |
| 28 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_grid (owner 2026-10-15: hoses left Gimme Some Slack) |
| 29 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_states (owner 2026-10-15: hoses left Gimme Some Slack) |
| 30 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_grid (owner 2026-10-15: hoses left Gimme Some Slack) |
| 31 | **15** | POLE CLUSTER |
| 32 | **16** | ELECTRIC ROOM |
| 33 | **17** | OVER THE UNKNOWN |
| 34 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_maze (owner 2026-10-15: hoses left Gimme Some Slack) |
| 35 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_maze_walled (owner 2026-10-15: hoses left Gimme Some Slack) |
| 36 | **18** | MAP EDGE |
| 37 | **19** | RIVER CROSSING |
| 38 | **20** | ROOF BOUNDARY |
| 39 | **21** | LONG SPAN + DIAGONALS |
| 40 | **22** | CONVERGING HUB |
| 41 | **23** | NETS SIDE BY SIDE + HALF-BUILT |
| 42 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_relay (owner 2026-10-15: hoses left Gimme Some Slack) |
| 43 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_deploy_by_hand (owner 2026-10-15: hoses left Gimme Some Slack) |
| 44 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_dropped (owner 2026-10-15: hoses left Gimme Some Slack) |
| 45 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_into_pond (owner 2026-10-15: hoses left Gimme Some Slack) |
| 46 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_their_tank (owner 2026-10-15: hoses left Gimme Some Slack) |
| 47 | **-** | moved to the FlowWorks review map (FlowWorks/review_map.py): hose_deploy_by_hand (owner 2026-10-15: hoses left Gimme Some Slack) |
| new | **24** | WATERPROOF CONDUIT: FOUR LOOKS |
| new | **25** | CONDUIT KINDS |
| new | **26** | WALL BRACKETS: EVERY FACE |
| new | **27** | TAP CLAMP POSES |
| new | **28** | AUTO-LINK SELECTED |
| new | **29** | FALLEN WIRE HAZARDS |
| new | **30** | CLAIM THEIR POLE |
| new | **31** | STYLED BLUEPRINTS |
| F | **F** | free build area |
| M | **M** | art-slot board |

## This build

```
{
 "builds": {
  "Battery/hostile": "3/3",
  "Battery/player": "25/25",
  "Cooler/player": "1/1",
  "ElectricStove/player": "3/3",
  "FlatscreenTelevision/player": "2/2",
  "Granite/None": "287/287",
  "Heater/player": "11/11",
  "HiTechResearchBench/player": "2/2",
  "HiddenConduit/player": "12/12",
  "PowerConduit/hostile": "28/28",
  "PowerConduit/player": "294/294",
  "PowerSwitch/player": "1/1",
  "RM_AerialLampMast/player": "3/3",
  "RM_AerialMast/player": "45/45",
  "RM_AerialWallBracket/player": "1/1",
  "RM_HoseReel/player": "17/17",
  "RM_LiquidTank/hostile": "1/1",
  "RM_PowerTapClamp/player": "5/5",
  "SolarGenerator/player": "2/2",
  "StandingLamp/hostile": "1/1",
  "StandingLamp/player": "45/45",
  "SunLamp/player": "2/2",
  "Turret_MiniTurret/player": "2/2",
  "Wall/player": "317/317",
  "WallLamp/player": "1/1",
  "WaterproofConduit/player": "20/20"
 },
 "default_style": "StarWarsJawa",
 "expected_refusals": {
  "25:0-2": "Roofed (expected Roofed)",
  "26:2-3": "OutOfRange (expected OutOfRange)",
  "27:0-5": "FullA (expected FullA)"
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
  "swept 2 hostile/non-colonist pawn(s) off the review map",
  "2026-10-15 hoses removed IN PLACE from the 41-station walk (owner: \"Get rid of those hoses...\"): 25 reels, 10 sign books, 118 maze walls and their tank destroyed; labels and sign books re-pinned in the 31-station numbering; saved as RM_gss_walk_20261015b. The style reads above are the 41-station build's, keyed by its old numbers."
 ],
 "pawns_in_region": [
  "Human672",
  "Human675",
  "Human678"
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
     "PowerConduit_Modern_Blue": 16,
     "PowerSwitch_Modern": 1
    },
    {
     "PowerConduit_Modern_Green": 2
    }
   ]
  },
  "34": {
   "runs": [
    {
     "PowerConduit_Futuristic": 7,
     "WaterproofConduit_Futuristic": 6
    },
    {
     "PowerConduit_Modern_Yellow": 7,
     "WaterproofConduit_Modern_Yellow": 6
    },
    {
     "PowerConduit_Industrial": 7,
     "WaterproofConduit_Industrial": 6
    },
    {
     "PowerConduit_Scrapper": 7,
     "WaterproofConduit_Scrapper": 6
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
  "41": {
   "runs": []
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
     "PowerConduit_Modern_Brown": 12
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
  }
 },
 "styled_refused": [],
 "wall_s": 178.5
}
```
