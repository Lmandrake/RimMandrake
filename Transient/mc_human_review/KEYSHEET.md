# Messy Conduit - human review key sheet

Built by `src/RimMandrake/MessyConduit/human_review.py`. Game paused, god mode on, weather clear, noon, Peaceful.
Cable look now: **Scrapper** (one global setting: flip it with Mod Settings > RimMandrake: Messy Conduit > Style, or `human_review.py --style <X>`; every station changes at once).

Jump the camera: `human_review.py --goto N` (N = station, 0 = whole gallery, F = free area).

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
- the masts change with the look too (a tinted stand-in until each look's own pole art lands)
- masts are 4 cells tall; the wire leaves from the insulator at the top

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

an overhead wire from a mast to a bracket bolted ON a shed wall; floor cord from the bracket to a lamp

**Notice**

- the bracket is drawn on the wall face, like a vanilla wall torch (it stands in the cell beside the wall, facing it)
- the wire lands on the bracket's insulator
- a floor cord continues from the bracket to the lamp

**Try**

- build another: Architect > Power > scrap wall bracket, point it AT a wall (vanilla wall-attachment placement)
- deconstruct the wall behind the bracket
- unlink and re-link the span from the mast's gizmo

### 10. CUT + FALLEN SPAN

the station-7 chain with the SECOND span cut (as if blown by an explosion)

**Notice**

- the cut wire still hangs from each mast TOP down to the ground, then lies on the ground, in the span's own cable
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

## Row D - hose crossings and parallel runs (hoses never branch: no T or + pieces, by ruling)

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

## F. Free build area

Open soil east of the hoses. West end: a charged power pad (2 solar generators, 3 full batteries) with a conduit stub labelled *plug in here*. South edge: steel, components and wood. God mode builds instantly; research is finished. Masts built here auto-link (shipped default); gallery masts are more than 20 cells away, so nothing you build links into the gallery.
