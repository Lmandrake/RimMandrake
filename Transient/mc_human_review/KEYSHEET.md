# Messy Conduit - human review key sheet

Built by `src/RimMandrake/MessyConduit/human_review.py`. Game paused, god mode on, weather clear, noon, Peaceful.
Cable look now: **Scrapper** (one global setting: flip it with Mod Settings > RimMandrake: Messy Conduit > Style, or `human_review.py --style <X>`; every station changes at once).

Jump the camera: `human_review.py --goto N` (N = station, 0 = south gallery 1-18, N0 = north gallery 19-29, F = free area).

Station numbers never move: round-2 stations are appended as 19-29 in a north gallery (above the colonists).

## Everywhere

- Mod Settings > RimMandrake: Messy Conduit: master switch OFF restores vanilla conduit art instantly, ON brings the cords back.
- Looks (Mod Settings name = `--style` value): Scrapper = StarWarsJawa, Industrial = StarWars, Modern = ExtensionCord, Futuristic = Cybertek. Each look owns its floor cords, its junction pieces, its power poles and its overhead lines. Modern also has a colour mode: in 'one colour everywhere' every plug, junction box and wall stub takes that colour.
- Unpause (space) to see motion: sway, live-end sparks, hose filling. Pause again to study a frame.
- Power overlay (bottom-right toggle) still shows vanilla connector lines.

## Row A - floor cords

### 1. POWERED LINE

battery (full) -> conduit -> heater, plus a lamp plugged in from 3 cells away

**Notice**

- no conduit graphic at all: only a loose, too-long cord lying between the nodes
- the plug cord from the lamp curls over to the run; the plug head sits at the lamp
- the cord ends in a plug at the heater and at the battery

**Try**

- select the battery: the whole net's cords highlight
- open the power overlay (bottom-right): vanilla connector lines still draw
- unpause: the cord sways a little in the wind

### 2. UNPOWERED LINE

the same build, battery EMPTY

**Notice**

- the cord looks identical to station 1: power state changes nothing on an intact cord
- the lamp and heater are off (compare with 1)

**Try**

- god mode: right-click the battery > dev: set charge, or drag a cord from station 1's grid over

### 3. CUT LINE

powered line with ONE conduit cell missing in the middle (cell 6)

**Notice**

- two cut ends: the battery side end is LIVE (sparks when unpaused), the far end is DEAD and lies limp
- no cord bridges the gap
- the far lamp and heater are off; the near lamp is on

**Try**

- unpause at 1x: watch the live end spark
- build one conduit into the gap (god mode = instant): the cord rejoins
- deconstruct another conduit cell: a new pair of ends appears

### 4. TANGLED PILE

a 3x3 block of conduit (9+ cells = a tangle) feeding three lamps and a heater

**Notice**

- the block becomes one TANGLE: a mass of cables plugged into each other
- Scrapper / Industrial / Futuristic: the cables run into MANY + and T junction boxes, every box has cables in it, no power strips
- Modern: power strips, every strip with cables PLUGGED IN (a plug in each used socket), LEDs lit while the net is live
- every lamp's cord runs out of the pile

**Try**

- --style ExtensionCord (Modern) vs StarWars (Industrial): strips vs junction boxes
- Modern: empty the battery (or cut the feed at cell 3): the strip LEDs go dark
- add conduit cells to the block: the pile grows

### 5. DEVICES + PLUGS

battery, an in-line power switch, a wood generator (unfuelled), lamps, heater

**Notice**

- each device gets its own plug; the switch sits in-line with NO dark outline round its tile
- the generator hooks to the run on two cells
- a lamp 3 cells off the run still gets a cord

**Try**

- flick the switch off (select it > toggle): everything past it goes dead
- refuel the generator: nothing changes visually

### 6. WALL + ROCK ENTRIES

a run passing under a steel wall and through a granite block; a branch ending inside the wall

**Notice**

- where the cord meets the wall it goes into a STUB (a hole/grommet), and comes out the other side
- the rock tunnel has rock holes on both faces, drawn foreshortened (angled like the rock face), not straight down
- the branch ending in the wall is a wall terminal

**Try**

- deconstruct a wall cell: the cord re-plans across the gap
- mine the granite: the tunnel opens

## Row B - overhead lines

### 7. MAST SPAN CHAIN

battery -> scrap power mast -> mast -> mast -> lamp, two 12-cell overhead spans

**Notice**

- the wires sag between masts and cast a ground shadow
- the far lamp is lit through the air
- the overhead cable is the look's own: thick dark scrap cable (Scrapper), thick BLACK cable (Industrial), thin black power line (Modern), sleek steel (Futuristic)
- the poles change with the look too: weathered wood (Scrapper), riveted steel with black insulators (Industrial), grey concrete with a transformer can (Modern), faceted steel with blade insulators (Futuristic)
- masts are 4 cells tall and 2 wide; the wire leaves from the insulator tips on the crossarm

**Try**

- select a mast: Link wire / Unlink wire / Re-string gizmos
- build a new mast within 20 cells: it auto-links to the nearest
- unpause: spans sway

### 8. LAMP MASTS

a power mast feeding two scrap lamp masts over the air

**Notice**

- each lamp mast is a light AND an anchor: it lights the ground under it
- the wire runs mast to lamp mast to lamp mast

**Try**

- unlink the second span: that lamp mast goes dark
- build one more lamp mast within range

### 9. WALL BRACKET

an overhead wire from a mast to a bracket bolted ON a shed wall, feeding a lamp INSIDE the shed

**Notice**

- the bracket is drawn on the wall face, like a vanilla wall torch (it stands in the cell beside the wall, facing it); the look's own art per facing
- three spare brackets show the other facings: on the shed's west, east and south walls (outside, unlinked)
- the wire ENDS on the bracket's insulator; nothing lies on the ground outside
- the power goes through the wall into the shed (a conduit under the wall) and lights the lamp inside

**Try**

- build another: Architect > Power > scrap wall bracket, point it AT a wall (vanilla wall-attachment placement)
- deconstruct the wall behind the bracket
- unlink and re-link the span from the mast's gizmo

### 10. CUT + FALLEN SPAN

the station-7 chain with the SECOND span cut (as if blown by an explosion)

**Notice**

- each cut half is ONE wire in the span's own cable: from the mast's insulator down to the break, where both halves meet on the ground
- the live downed end sparks; the far lamp is dark
- the first span still hangs and still carries power

**Try**

- select the middle mast > Re-string cut wires: the span goes back up and the lamp relights
- god mode: drop an explosion under a span (dev tools) to cut another

### 11. POWER TAP

a power-tap clamp biting ANOTHER faction's grid (left, hostile battery), drained one-way into our lamp (right)

**Notice**

- the crocodile clamp sits on their conduit; one of our cords is taped to it
- the two grids never merge (their net and ours stay separate)
- our lamp is lit with no power source of our own

**Try**

- unpause and watch their battery drain
- Mod Settings > Messy Conduit > taps off: our lamp goes dark

## Row C - flexible hoses

### 12. HOSE: FLAT

a laid hose with nothing flowing through it

**Notice**

- the hose lies flat and thin
- a straight hose has NO joiner along it; the free end is a plain open end the hose's own width

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)

### 13. HOSE: FILLING

the same hose, flow ON, frozen half-way through filling

**Notice**

- half-plump: the swell is mid-transition
- UNPAUSE and it finishes plumping in ~half a second

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)

### 14. HOSE: PLUMP

flow ON, fully filled

**Notice**

- full round hose, visibly wider than the flat one
- still no joiner on the straight

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)

### 15. HOSE: LONG + BEND

a 26-cell plump hose routed round a wall stub

**Notice**

- the hose bends smoothly round the obstacle (never kinks tighter than the minimum bend)
- joiners only at the bends: two brass couplings screwed face to face, joining two lengths
- it never crosses the wall

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)

## Row D - hose crossings and parallel runs

Hoses never branch (ruled by card): one hose is one line with two ends. Shown as the system does it today; there is no crossing piece.

### 16. HOSE CROSSING

two plump hoses laid straight across each other at right angles

**Notice**

- one hose passes cleanly OVER the other, the same way every frame (the newer reel's hose is on top)
- no joiner and no end fitting at the crossing
- the hoses do not route round each other: a hose is not an obstacle to another

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- NOT designed: there is no crossing piece and no T or + hose fitting (hoses never branch, by ruling)

### 17. PARALLEL RUNS

two hoses laid side by side, two cells apart, one flat and one plump

**Notice**

- each keeps its own lane; where their S-curves meet, one draws over the other cleanly
- flat vs plump side by side: width and shine

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- NOT designed: there is no crossing piece and no T or + hose fitting (hoses never branch, by ruling)

### 18. HOSE GRID

four hoses, two each way, crossing in a 2 x 2 grid

**Notice**

- four crossings: every one is over/under, with a fixed order (newest on top)
- FINDING to judge: where the S-curve slack of two hoses runs along each other they may overlap for a stretch

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- NOT designed: there is no crossing piece and no T or + hose fitting (hoses never branch, by ruling)

## Row E - power showpieces (north gallery)

Round 2 (owner notes 2026-10-04): a pole with many kinds of devices, a crowded electric room under an overhead line, cords through a fogged mountain.

### 19. POLE CLUSTER

one power pole with a wide mix of devices: some right beside it (lamp, heater, sun lamp, mini-turret, two batteries), some reached by conduit runs (stove, hi-tech research bench, TV), a walk-in freezer with an in-wall cooler and wall lamps inside and out, and a lamp mast fed over the air

**Notice**

- each device right beside the pole gets its own hookup from the pole's insulators; with more hookups than insulators, see whether they share a terminal or pile onto one (owner question: which terminal does each go to?)
- big devices (5x2 bench, 3x1 stove, 2x1 TV): the cord should meet the building, not stop short of its edge or end in mid-air
- the in-wall cooler: the cord reaches it through the wall face, not across the room
- wall lamps (one inside the freezer, one outside on its south wall): their cords run to the wall, never through the room's middle
- the turret's cord does not cross the turret's own base art
- the lamp mast on the far NW gets its power through the air: one span, lit

**Try**

- toggle each device off (select > flick): its cord stays, the device goes dark
- deconstruct the pole: every adjacent hookup falls; the conduit-fed devices keep their cords
- build another lamp right beside the pole: does it pick a free terminal?

### 20. ELECTRIC ROOM

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

### 21. MOUNTAIN TUNNEL

a cord run through a winding one-cell tunnel and a small cavern inside a big block of granite under OVERHEAD MOUNTAIN, fog of war ON over the rock; a pole in the cavern tries to link to one outside

**Notice**

- the cords stay INSIDE the tunnel: their curls must not draw over the fogged rock or poke out of the fog
- the cords are drawn under the mountain-roof shading like everything else (no bright cord in a dark tunnel)
- where the tunnel turns, the cord turns with it (no shortcut through rock)
- the cavern pole is under the mountain roof: its link to the pole outside is REFUSED (anchors need open sky), so no wire runs through the rock
- the lamp in the cavern and the one past the east exit are lit

**Try**

- mine a cell of the tunnel wall: the fog lifts there; do the cords move?
- toggle the roof overlay (bottom-right)
- select the cavern pole > Link wire to the outside pole: the refusal message should say 'roofed'

## Row F - hose mazes (north gallery)

Two routes out of a small maze, then the short one walled off after laying. validation_hose.py owns the pass/fail; this map shows it.

### 22. HOSE MAZE: TWO ROUTES

a hose laid from a reel deep inside a small walled maze to a free end outside; two ways out: the short one (south-east gap) and a longer one (north-east gap)

**Notice**

- the hose finds the SHORT route out through the inner chamber's west door, down and out the south-east gap
- it never clips a wall corner, and its bends stay smooth in the one-cell corridors
- it stays inside the corridors (it never jumps a wall)

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- reel it in and lay it again to the same free end: does it pick the same route?

### 23. HOSE MAZE: SHORT WAY WALLED

station 22's maze; after the hose is laid, a wall is built across the short (south-east) gap - does the hose re-route the long way, refuse, or pass through the new wall?

**Notice**

- what the hose does when its route is blocked AFTER laying: re-routes north-east, stays and clips the wall, or drops
- if it re-routes, the new path is as clean as station 22's

**Try**

- select the reel: Lay hose / Reel in hose / Free end nozzle-endcap gizmos
- dev mode: the reel's 'DEV: flow through hose' gizmo toggles water flow (there is no pump yet)
- reel it in and lay it again to the same free end: does it pick the same route?
- deconstruct the blocking wall (cells 12,1 and 12,2): does the hose go back to the short way?

## Row G - challenge configurations (north gallery)

Built to make visible bugs show: map edge, water, roof edge, longest/odd spans, a full pole, neighbouring nets, half-built work and save-load.

### 24. MAP EDGE

poles and cords at the map's north-east corner: a pole IN the corner cell, poles on the top and right edge cells, and floor runs lying along both edges

**Notice**

- the cords' loose curls must not draw off the map (nothing hanging past the edge, nothing cut off with a hard line)
- the corner pole's wires and shadow stay on the map
- no red errors (open the debug log: none mentioning MessyConduit)

**Try**

- pan the camera to the edge: is anything drawn in the black past the map?
- deconstruct the corner pole: both its spans drop

### 25. RIVER CROSSING

a river (chest-deep moving water, shallow banks): an overhead span from bank to bank, and a floor run fording the shallow end in waterproof conduit

**Notice**

- the overhead wire's shadow falls on the water like on the ground (or not at all), never as a dark stripe on the river bed
- the floor cord on the water: does it float, sink or draw on top as if on soil? (waterproof conduit has its own look?)
- the cords' curls do not wander into the deep water
- both far devices are lit

**Try**

- unpause: the river flows; does the cord on the water move with it (it should not)?
- deconstruct one waterproof conduit cell in the river: the cut ends lie in water - do they still spark?

### 26. ROOF BOUNDARY

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

### 27. LONG SPAN + DIAGONALS

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

### 28. CONVERGING HUB

a hub pole with four spans (its maximum) arriving from N, E, S and W, a FIFTH pole trying to link (refused: full), and three lamps plus a heater right beside the hub

**Notice**

- four wires meet on one crossarm: each lands on an insulator tip, none crossing through the pole art
- with more wires than insulators, do two share a tip cleanly or overlap in a blob?
- the fifth (NE) pole stays unlinked, its lamp dark
- the hub's local hookups: which terminal does each lamp take?

**Try**

- unlink one spoke, then link the NE pole: it takes the freed slot
- deconstruct the hub: four spans drop at once

### 29. NETS SIDE BY SIDE + HALF-BUILT

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

## Expected refusals (shown on purpose)

- 21: the cavern pole's link to the outside pole is refused (Roofed).
- 26: the pole inside the roofed room is refused (Roofed).
- 27: the 21-cell pair is refused (OutOfRange).
- 28: the fifth pole is refused (FullA: the hub's 4 slots are used).

## F. Free build area

Open soil east of the hoses. West end: a charged power pad (2 solar generators, 3 full batteries) with a conduit stub labelled *plug in here*. South edge: steel, components and wood. God mode builds instantly; research is finished. Masts built here auto-link (shipped default); gallery masts are more than 20 cells away, so nothing you build links into the gallery.
