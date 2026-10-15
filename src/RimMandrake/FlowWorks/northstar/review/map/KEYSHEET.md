# FlowWorks review map - key sheet

Load the save in RimWorld (Load game > (no keeper saved yet: build, then --save)). The game is paused, god mode is on, clear weather, noon, Peaceful. Mod Settings are the shipped defaults.

Each station is labelled in the world with its number, a short name, its status and what to look at. Status colours: green = works in game, blue = built, not yet seen, gold = partly built, rust = not built.

75 stations: 13 works in game, 51 built, not yet seen, 10 partly built, 1 not built yet.

## V - pits: what they look like (south-west block)

Columns: depth 1 to 4, left to right. Rows from the bottom: dry in soil, dry in granite, water in soil, water in granite, tar in soil, tar in granite, scorched in soil, scorched in granite; the top two rows are seven more liquids in soil at depth 3. A colonist stands in the near row of every pit so you can see how far the near bank hides him.

- **dry:** The far bank shows a lit face with a dark rim, the way the game draws its own walls; at depth 3 it is about a wall's height, at depth 4 taller. The side banks show as narrow faces. The person in the near row is hidden below the near bank, more the deeper the pit.
- **water:** The water moves like the game's own shallow water. The pit's floor and its drowned far wall show through it, fainter the deeper the water.
- **tar:** Tar is dark grey and opaque on soil and granite alike, never blue: a thick liquid that slowly creeps and shines.
- **scorched:** Still an empty pit with the same walls, but burned: granite pits turn to grey ash, dirt pits to baked reddish-brown soil with ash over it; char darkest against the walls and in patches; charcoal lumps and ash flakes scattered on the floor; soot drips running down the far wall; smoke-blackened ground round the rim in uneven lobes. Deeper pits still read deeper.
- **oil:** Oil: slow dark gloss with a faint rainbow film.
- **slime:** Green slime: thick, opaque, slowly creeping, a few bubbles rising.
- **slimewhite:** White slime: thick, opaque, slowly creeping, a few bubbles rising.
- **slimered:** Red slime: thick, opaque, slowly creeping, a few bubbles rising.
- **blood:** Blood: thick, opaque dark red, slowly creeping.
- **chemfuel:** Chemfuel: a thin amber-brown fuel with a faint rainbow film; the pit floor shows faintly through it.
- **astrofuel:** Astrofuel: a thin pale blue fuel with a faint rainbow film; the pit floor shows faintly through it.

## 2 · Liquid in canals and ponds

### 1. A canal off the map edge drains - works in game

A canal that runs off the edge of the map drains away. A canal ending inside the map holds its water.

**Look at:** the lower canal runs off the map edge and stays empty; the upper one ends inside the map and holds its water

**Poke it:**

- unpause: the lower canal keeps pouring away off the edge

**Look for:** weak spot: the upper canal draining too; water standing in the lower one

### 2. Liquid spreads along the canal - works in game

Liquid spreads along a canal from its pond, in every direction, and stays inside the dug channel. It moves in steady pulses, the same way every time; two canals off one pond both fill. Switching the engine off in settings freezes every canal where it is.

**Look at:** one pond, a canal branching three ways, all filled

**Poke it:**

- dig a new cell onto any end: next pulse it fills
- unpause: it moves in pulses, not every tick

**Look for:** weak spot: liquid outside the dug cells; one branch left dry

### 3. Tar crawls, water runs - works in game

Each liquid keeps its own nature: tar crawls while water runs, and a canal shows the liquid it came from. Water fed from water looks like water; tar fed from tar looks like tar.

**Look at:** same canal, same pulses: the water canal (top) is full, the tar canal (bottom) has crawled a few cells

**Poke it:**

- unpause and watch the tar front creep

**Look for:** weak spot: the tar canal drawn as water; both fronts the same length

### 4. Liquids never mix - built, not yet seen

Two different liquids never mix: where their fronts meet, both stop. Drain one side and the other moves in. Old saves keep their liquids.

**Look at:** water from the west, tar from the east: the fronts meet and stop

**Poke it:**

- fill in a water cell: the tar moves in

**Look for:** weak spot: a cell between the fronts drawn as a blend; one liquid overwriting the other

### 5. A small pond runs dry - works in game

Any pond is a source: a lake touching the map edge never runs dry; an enclosed pond runs out. An enclosed pond feeds about five canal tiles for each tile of water, then the flow stops.

**Look at:** a 2x2 pond feeding a long canal: it fills about 20 cells, then stops (5 canal cells per pond cell)

**Poke it:**

- the far end stays dry: the pond has paid out
- a lake touching the map edge never runs out

**Look for:** weak spot: water at the far end (the pond never runs out)

### 6. A pond shrinks as it pays out - built, not yet seen

A pond visibly shrinks as it pays out, and slowly refills from rain, season and seepage. You can see a source being drawn down.

**Look at:** a 4x4 pond feeding a long canal: its edge cells turn to shallow then mud as it is drawn down

**Poke it:**

- unpause through rain: it slowly refills

**Look for:** weak spot: a pond that shrinks from the middle, or not at all

### 7. A drained pond leaves a hollow - built, not yet seen

A drained pond leaves a hollow

**Look at:** a 2x2 pond fed out into a long canal: its bed is left as lakebed, a hollow, not flat ground

**Poke it:**

- hover the bed: lakebed terrain, and a hollow you climb down into
- order a colonist into the bed and back out: a hollow never traps

**Look for:** weak spot: water still in the pond (the build's pulses ran short, say so); a bed drawn as flat soil; a colonist stuck in it

### 8. Refill waits for whoever stands in it - built, not yet seen

Refill waits for whoever stands in it

**Look at:** the same drained pond with a muffalo standing in its bed

**Poke it:**

- dev: Change weather > Rain, unpause: the bed refills around the muffalo, never over it

**Look for:** weak spot: water poured onto the muffalo; a refill that never starts after it walks off

### 9. Filling in sends water home - built, not yet seen

Filling in sends water home

**Look at:** a pond feeding a water canal, with a fill-in order on the canal's far end

**Poke it:**

- unpause: a colonist fills the far end and that water runs back into the pond

**Look for:** weak spot: water deleted at the filled cells; the pond's edge never rising

### 10. Rain fills open trenches - works in game

Rain fills open trenches; roofed ones stay dry

**Look at:** two dry trenches; the right one is roofed

**Poke it:**

- dev: Change weather > Rain, unpause: the open trench fills, the roofed one stays dry

**Look for:** weak spot: the roofed trench filling; rain filling undug ground

### 11. Canyon floods run through canals - built, not yet seen

Canyon floods run through your canals instead of wiping them out

**Look at:** a dry canal waiting for a canyon flood

**Poke it:**

- dev: start a canyon flood upstream: it runs down the canal

**Look for:** weak spot: the flood wiping the canal flat instead of running in it

### 12. Slime is nearly uncrossable - not built yet

Slime is nearly impossible to cross and slow to climb out of. Your words: so slippery it is nearly uncrossable.

Not built yet: the station is an empty concrete pad with its label.

## 1 · Digging canals and pits

### 13. Dig a canal, dig deeper - works in game

You mark ground and a colonist digs a canal there; dig again to go one level deeper. There are four depths. The fourth is a pit: nothing more than the deepest dug ground.

**Look at:** four depths side by side, D1 to D4; the right one is a pit

**Poke it:**

- unpause: a colonist digs the marked strip (top left)
- Architect > Orders > Dig canal on a dug strip: it goes one level deeper; a D4 strip refuses

**Look for:** weak spot: a D4 strip that still takes a dig order; dug ground that reads as a gravel path

### 14. Fill a canal back in - works in game

You can fill a canal back in, and the liquid in it is pushed along, not deleted. Only liquid with nowhere at all to go is lost, and the game counts it.

**Look at:** a water canal with a fill-in order on its east end

**Poke it:**

- unpause: a colonist fills the marked cells and their water moves back along the canal, not deleted

**Look for:** weak spot: water that vanishes instead of moving back; a filled cell still drawn as canal

### 15. Trenches slow people down - built, not yet seen

Trenches slow people down: deeper is slower, flooded is slower still, and a pit can't be crossed. A dug line is a real barrier you can build defences with.

**Look at:** dry lanes D1, D2, D3, a pit row D4, and a flooded D2 lane

**Poke it:**

- hover a lane: the walk cost climbs with depth; the wet lane is slower than the dry D2
- order a colonist across: he goes round the pit row

**Look for:** weak spot: the pit row crossed anyway; the wet lane no slower than the dry D2

### 16. Digging turns up minerals - partly built

Digging a canal sometimes turns up local minerals, with a letter the first time each one appears. Deep cuts can reach the minerals deep drills find; where there are none, you get chunks of local rock.

**Look at:** a dig order 14 cells long, waiting for a colonist

**Poke it:**

- unpause: about 1 in 70 dug tiles leaves a lump on the bank, with a letter the first time

**Look for:** weak spot: a lump dropped into the canal; a second letter for the same mineral

**Not built yet in this feature:** finds following the shared list of which minerals belong where

## 3 · Fire and corrosion

### 17. Fire lights tar - built, not yet seen

Fire or an explosion lights tar, oil or propane, and the flame travels along the canal. Tar and propane creep like a fuse you can outrun; fuels go up fast.

**Look at:** a tar pond and its canal; the mark is where to drop a fire

**Poke it:**

- dev: Spawn fire (or an explosion) at the mark: the flame runs back along the canal
- nothing lights? 'Liquid ignition' ships OFF in Mod Settings > FlowWorks

**Look for:** weak spot: a flame that lights and dies at once; fire jumping onto dry ground

### 18. A burning canal burns for days - built, not yet seen

A burning canal burns for days, spreads back into its pond, and sets anyone standing in it alight. About one canal level a day; a pond burns far longer. Corrosive liquids also eat whatever stands in them (that one is switched off by default).

**Look at:** a long tar canal back to its pond

**Poke it:**

- light the far end, unpause: about one canal level a day, and it spreads back into the pond

**Look for:** weak spot: the whole canal burnt out within an hour; the pond never catching

### 19. Foam or rain puts it out - built, not yet seen

Foam or rain puts burning liquid out. Foam keeps it out while the foam lies there; rain has a chance on open ground.

**Look at:** a tar canal with a firefoam popper beside it

**Poke it:**

- light it, then trigger the popper: foamed cells stop burning while the foam lies there

**Look for:** weak spot: foamed cells relighting while the foam still lies there

### 20. Acid eats what lies in it - built, not yet seen

Acid eats what lies in it

**Look at:** an acid canal with steel and wood lying in it

**Poke it:**

- Mod Settings > FlowWorks > Liquid corrosion ON (it ships OFF), unpause: what lies in the acid loses health

**Look for:** weak spot: damage while the switch is OFF; a stack gone in seconds

## 4 · Pits: catching

### 21. Nothing climbs out of a pit - works in game

Anything that falls into a pit cannot climb out. It stays where it is; its info line says it is trapped.

**Look at:** a muffalo in a 3x3 pit

**Poke it:**

- unpause: it walks the floor and never climbs out; its info line says trapped

**Look for:** weak spot: the muffalo on the lip an hour later; no 'trapped' on its info line

### 22. A pit only holds what fits - works in game

A pit only holds a creature that fits: anything wider walks out, and narrowing a pit frees it. Your rule: the pit must be as wide as the creature.

**Look at:** a muffalo in a 1-wide slot (too narrow) and a hare in a 1x1 pit

**Poke it:**

- unpause: the muffalo walks out, the hare stays

**Look for:** weak spot: the muffalo held in the slot; the hare walking out

### 23. Climbing depends on size - built, not yet seen

Climbing depends on size

**Look at:** three 2-deep pens: a chicken, a husky, a muffalo

**Poke it:**

- unpause: the chicken stays, the husky climbs out slowly, the muffalo steps out
- Mod Settings > Pits trap by relative height OFF: only D4 holds, and all three walk out

**Look for:** weak spot: all three held or all three out; 'trapped' on any but the chicken

### 24. Falling in hurts - works in game

Falling in hurts, and only being forced, blown or jumping in does it: colonists never walk into an open pit

**Look at:** a pit and one of your colonists beside it

**Poke it:**

- order him into the pit: he will not walk in (colonists never path into an open pit); 'Jump into pit', or a blast or skip that puts him in, hurts him and holds him until a lowered ladder lets him climb out

**Look for:** weak spot: a colonist who walks in on an ordinary move order; a fall with no injury

### 25. Shots only from the pit's edge - built, not yet seen

Someone in a pit can only shoot, and be shot at, from the pit's edge. Raiders don't waste shots on them from further away.

**Look at:** a boar in a pit; your colonist stands 6 cells off

**Poke it:**

- order an attack on the boar: he walks to the lip before he can shoot

**Look for:** weak spot: a shot fired from 6 cells away

### 26. Jump in on purpose - partly built

A 'jump in' button drops a colonist in on purpose; explosions and knockback can throw people in. Whoever jumps in is stuck there too.

**Look at:** a pit and a colonist beside it

**Poke it:**

- select him: 'Jump into pit' drops him in, and he is stuck there too

**Look for:** weak spot: no 'Jump into pit' button; the jumper unhurt and free

**Not built yet in this feature:** an explosion or knockback throwing someone into a pit

### 27. A ramp is a way out - built, not yet seen

A ramp is a way out

**Look at:** two 3-deep pits with a chicken in each; the left one has a ramp up its north wall

**Poke it:**

- unpause: the left chicken walks up the ramp and out; the right one is held
- Architect > Structure > pit ramp: the ghost marks the square it climbs to

**Look for:** weak spot: placeholder art, judge the shape not the paint; a ramp facing the wrong way; the right chicken escaping

### 28. A staircase never traps - built, not yet seen

A staircase never traps

**Look at:** a staircase dug D1 to D4 with a chicken at the bottom

**Poke it:**

- unpause: it climbs out one step at a time

**Look for:** weak spot: the chicken read as trapped at the bottom (a slope must never trap)

### 29. A cover hides the hole - works in game

A pit cover hides the hole and looks like the ground around it. A faint seam shows only at the closest zoom.

**Look at:** left: a covered pit; right: the same pit uncovered

**Poke it:**

- zoom in close on the left one: only a faint seam shows

**Look for:** weak spot: a hole outline showing through the cover at play zoom

### 30. Step on a cover, fall through - built, not yet seen

Step on a cover and you fall through; three cover builds bear different weights. Plank lattice, woven scrap, reinforced frame.

**Look at:** three covered pits: plank lattice, woven scrap, reinforced frame

**Poke it:**

- order a colonist across each: the weaker covers give way

**Look for:** weak spot: the reinforced frame giving way under one colonist; all three alike

### 31. Spikes at the bottom - built, not yet seen

Spikes at the bottom stab whoever falls in: badly, scaled to their size, never instantly fatal. Walking up to the spikes is harmless; only a fall triggers them.

**Look at:** a pit floored with spikes

**Poke it:**

- walking up to the spikes is harmless; only a fall in triggers them

**Look for:** weak spot: spikes hurting someone who only walks beside them; a fatal stab

### 32. Flood an occupied pit - built, not yet seen

Flood an occupied pit to drown, poison or burn whoever is in it. Water drowns non-swimmers, poison builds up, oil can be lit; open a gate to let the liquid in.

**Look at:** a boar in a pit, a water canal behind a shut sluice

**Poke it:**

- open the sluice (select it): water pours into the pit

**Look for:** weak spot: water stopping at the open sluice; a boar that never starts drowning

## 5 · Pits: holding prisoners

### 33. A ladder in and out - works in game

A ladder: lowered, people climb out; raised, they're stranded. It works like a prison door. Ladders only go on dug ground.

**Look at:** a 5x5 pit with a LOWERED ladder on its west wall, a colonist in it and steel on its floor

**Poke it:**

- undraft him: he climbs out; undrafted haulers then fetch the steel off the pit floor
- select the ladder: Ladder up and nobody climbs it either way

**Look for:** weak spot: haulers ignoring the steel while the ladder is down

### 34. A raised ladder strands him - built, not yet seen

A raised ladder strands him

**Look at:** the same pit with its ladder RAISED

**Poke it:**

- undraft him: he stays put, and nobody goes down for the steel
- select the ladder: Ladder down and he climbs out

**Look for:** weak spot: raised and lowered drawn the same (compare the station to the left); anyone using a raised ladder

### 35. A pit prison, run from the lip - built, not yet seen

A walled-in pit is a room; add a prisoner bed and it's a prison you run from the edge. Wardens feed, tend, capture, recruit and convert from the lip without climbing down; nothing too wide is offered.

**Look at:** a 3x4 pit with a prisoner bed and a prisoner

**Poke it:**

- wardens feed and talk to him from the lip; nobody climbs down

**Look for:** weak spot: a warden climbing down; the room not labelled a prison

### 36. Sun and cold wear him down - built, not yet seen

An open pit bakes by day and freezes by night, wearing down a prisoner's resistance. Colonists whose beliefs mind cruelty are upset by it; psychopaths are not.

**Look at:** an open pit with a prisoner, noon sun on it

**Poke it:**

- inspect a pit cell: hotter than the ground by day, colder by night

**Look for:** weak spot: the pit cell's temperature the same as the ground's

### 37. Sluice and grate doors - built, not yet seen

Sluice gates and grate doors let liquid through but hold creatures and prisoners. They can't be opened from inside the pit; open one to let a held creature walk out.

**Look at:** a pit with a sluice (wood) and a security grate (steel) in its wall; a hare and a prisoner inside

**Poke it:**

- open either door: liquid flows through, nobody inside can open it

**Look for:** weak spot: water stopped by an open door; the prisoner opening it from inside

## 6 · How it looks

### 38. People sink as the ground deepens - works in game

People sink as the ground deepens and rise as they climb out; in a pit the walls stand over their head. Someone in slime is drawn sunk into it, not standing on top.

**Look at:** one colonist standing at each depth D1..D4

**Poke it:**

- undraft one and order it out: it rises step by step

**Look for:** weak spot: the D4 head showing over the wall; a snap instead of a step on the way out

### 39. A canal looks dug and shows how full - partly built

A canal looks dug, not like a gravel path, and shows how full it is. Trace, half and brimming fills look different; trenches read as obstacles without a tooltip.

**Look at:** D3 cells: empty, trace, half, brim; and a brimming pit

**Poke it:**

- hover each: the fill reads empty, trace, half, brim

**Look for:** weak spot: trace and half drawn the same

**Not built yet in this feature:** a dug canal looking dug, not like a gravel path

### 40. Four more canal liquids - built, not yet seen

Four more canal liquids

**Look at:** D3 canals brimming with poison, yellow slime, boiling water and icy water

**Poke it:**

- hover each: the canal names its liquid

**Look for:** weak spot: boiling and icy water drawn like plain water; the V block holds the other seven canal liquids

### 41. A pit reads as one dark hole - partly built

Pit walls are drawn with depth, Quarry-style, so a pit reads as one big dark hole. Every depth looks different; an occupied pit reads differently from an empty one; never like a building.

**Look at:** two 4x4 pits: empty (left) and occupied (right)

**Poke it:**

- zoom out to play zoom, then in close

**Look for:** weak spot: a pit drawn as a grid of tiles; the muffalo drawn over the wall

**Not built yet in this feature:** a pit reading as a big dark hole

### 42. Walls show what they are cut in - built, not yet seen

Walls show what they are cut in

**Look at:** four 3-deep pits cut in soil, sand, gravel and granite

**Poke it:**

- zoom in: each wall face takes its ground's colour
- Mod Settings > wall material OFF: all four turn the same

**Look for:** weak spot: all four walls one colour; a seam where the wall meets the floor

### 43. Spikes, ladder, gates: own drawings - built, not yet seen

Spikes, ladders and gates have their own drawings, not borrowed vanilla ones. Ladder, spikes, sluice and grate each ship their own texture.

**Look at:** a ladder, spikes, a sluice and a grate on dug ground, side by side

**Poke it:**

- open the sluice and the grate: open and shut read differently without selecting

**Look for:** weak spot: any of the four drawn with a vanilla stand-in

### 44. Tar and slime look thick - partly built

Tar looks thick and sticky; slime looks thick and opaque, not tinted water

**Look at:** a tar pond and canal (left); green, white and yellow slime pools (right)

**Poke it:**

- order a colonist through the tar: he leaves a wake and is drawn sunk into it

**Look for:** weak spot: slime that looks like tinted water; no bubbles or surface motion

**Not built yet in this feature:** slime looking thick and opaque, not tinted water

### 45. Burning liquid looks alight - partly built

Burning liquid looks alight, and a burnt-out canal looks scorched. The burning-liquid flame still uses the vanilla fire graphic; the scorched canal has its own art.

**Look at:** a tar canal to light, and a scorched-dry pit beside it

**Poke it:**

- dev: Spawn fire at the mark

**Look for:** weak spot: the scorched pit looking like plain dirt; the flame drawn as a vanilla fire

**Not built yet in this feature:** burning liquid looking alight (its own art)

## 7 · Bottles, tanks and pumps

### 46. Bottles, buckets, barrels - partly built

Bottles, buckets and barrels: fill at a shore or tank, use, wash and reuse. Boiling water cools and blood spoils in a bottle; bottles are tagged for a future cooking mod.

**Look at:** empty, full and dirty bottles, a bucket and a barrel by a pond and a tank

**Poke it:**

- unpause: colonists fill bottles at the shore or the tank and wash dirty ones

**Look for:** weak spot: dirty bottles never washed; tar bottled as water

**Not built yet in this feature:** boiling water cooling and blood spoiling in a bottle; bottles tagged for future cooking

### 47. Every liquid, every container - built, not yet seen

Every liquid, every container

**Look at:** bottles (top), buckets, barrels (bottom) of nine liquids; left to right fresh, salt, boiling, icy, toxic, acid, tar, brine, propane

**Poke it:**

- hover each stack: its liquid; unpause a while: the boiling water cools

**Look for:** weak spot: two liquids whose containers read the same; the dirty ones not looking dirty

### 48. Containers in every material - built, not yet seen

Containers in every material

**Look at:** empty bottles, buckets and barrels in each material, by a crafting spot

**Poke it:**

- select the crafting spot: Bills lists the bottle, bucket and barrel recipes

**Look for:** weak spot: every material drawn the same; a material named but not in the label

### 49. Tanks, pumps, hoses - built, not yet seen

Tanks store liquid; pumps move it from ponds and canals; hoses and adapters connect it all. One full tank holds about five canal tiles of liquid.

**Look at:** a pump on the pond shore piped to a tank, powered by a battery

**Poke it:**

- unpause: the pump draws the pond down into the tank

**Look for:** weak spot: the pond not going down; the tank's fill bar never moving

### 50. A pump set to Pour - built, not yet seen

A pump set to Pour

**Look at:** the same pump and tank, the pump set to Pour and the tank full

**Poke it:**

- unpause: the tank empties back into the pond
- the pump's button flips Draw and Pour

**Look for:** weak spot: pouring with no power; water poured onto dry ground

### 51. Four tank sizes - built, not yet seen

Four tank sizes

**Look at:** a short, a tall, a cargo and an extra-tall tank, each half full

**Poke it:**

- select each: 80, 160, 160 and 320 units, every fill bar at half

**Look for:** weak spot: both tall tanks are placeholder art (a drum stacked twice); a tall top cut off or hidden behind the label

### 52. Tank looks: short and tall - built, not yet seen

Tank looks: short and tall

**Look at:** the short tank (bottom) and the tall tank (top) in each of the four looks

**Poke it:**

- select a tank: Choose style

**Look for:** weak spot: a look whose tall tank does not match its short one; a look missing art

### 53. Tank looks: cargo tanks - built, not yet seen

Tank looks: cargo tanks

**Look at:** the cargo tank (bottom) and the extra-tall cargo tank (top) in each of the four looks

**Poke it:**

- select a tank: Choose style

**Look for:** weak spot: the extra-tall tank's top running into the label above the station

### 54. Tank modes - built, not yet seen

Tank modes

**Look at:** four tanks set Store, Fill, Empty and Dump, with empty bottles by them

**Poke it:**

- unpause: colonists fill bottles from Empty and pour into Fill only
- the Tank mode button cycles the four

**Look for:** weak spot: the Dump tank losing water with nothing connected; a Store tank being emptied

### 55. A hose laid to a tank - built, not yet seen

A hose laid to a tank

**Look at:** a hose reel with its hose laid out to a tank, nozzle on

**Poke it:**

- select the reel: Retract, Move hose end, Fitting, Free end role
- dev mode adds: lay instantly, reel in instantly, flow through hose

**Look for:** weak spot: the hose drawn through the tank; bends sharper than it can take; a nozzle with no art

### 56. Four hose reel looks - built, not yet seen

Four hose reel looks

**Look at:** four hose reels: scrapper, industrial, modern, futuristic

**Poke it:**

- select one: Choose style

**Look for:** weak spot: the scrapper look has no art folder of its own; two looks that read the same

### 57. Four pipe looks - built, not yet seen

Four pipe looks

**Look at:** four rigid pipe runs, one per look

**Poke it:**

- select a pipe: Choose style, for one pipe or its whole run

**Look for:** weak spot: the tees (middle of the top and third runs) breaking the joins; a run that changes look half way

### 58. Pipe-net adapters - built, not yet seen

Pipe-net adapters

**Look at:** the chemfuel and propane adapters next to a tank

**Poke it:**

- select an adapter: its mode button cycles Send, Take and Shut

**Look for:** weak spot: the adapters exist only with Vanilla Chemfuel Expanded loaded; without it (the release test list) this pad is empty and the build notes say so

### 59. Spilled liquid - built, not yet seen

Spilled liquid

**Look at:** spilled liquid (left) and tracked tar (right) on the ground

**Poke it:**

- unpause: colonists clean both

**Look for:** weak spot: the spill drawn as a vanilla water puddle; tar filth with no art

### 60. Drills, taps and stills - built, not yet seen

Drills and taps bring underground liquids up, and cleaned water feeds thirst

**Look at:** a liquid drill, a tap, a fuelled still, a sun-pan still and a drip filter

**Poke it:**

- select the drill: it says what liquid lies under it, if any

**Look for:** weak spot: a drill with nothing under it and no message saying so

### 61. Liquid kits - partly built

Liquid workings other biomes borrow: bills that use up a liquid, a vat where two liquids react, scalding floods and tar stains. Built and switchable in settings, first-guess numbers. Only the reaction vat can be built today; the other three wait for the biome that uses them to wire them in.

**Look at:** a reaction vat between two tanks; the bath bills, scalding floods and tar stains have nothing to show until a biome wires them in

**Poke it:**

- unpause: with tar and acid water in the tanks the vat vents a gas cloud

**Look for:** weak spot: no gas although both tanks hold their liquids

**Not built yet in this feature:** workbench bills that need a liquid to hand and use it up; floods released boiling hot that scald until they cool; drained floods leaving a stain behind, such as tar

### 62. Ruined liquid works - built, not yet seen

Ruined industrial liquid plants (desalination, tar refinery, pumping station) are found and repaired. Never built from the menu in the campaign.

**Look at:** four wrecked plants: desalination, detox works, tar refinery, pumping station

**Poke it:**

- select a wreck: repair it in stages; none are on the build menu in the campaign

**Look for:** weak spot: a wreck that offers no repair

### 63. Wrecked, kludged, repaired - built, not yet seen

Wrecked, kludged, repaired

**Look at:** one desalination plant at each stage

**Poke it:**

- select each: what it makes and what it needs

**Look for:** weak spot: the three stages hard to tell apart

### 64. The other plants, mended - built, not yet seen

The other plants, mended

**Look at:** detox works, tar refinery and pumping station, kludged (bottom) and repaired (top)

**Poke it:**

- select each: what it needs and what it makes

**Look for:** weak spot: a kludged and a repaired plant drawn alike

## 8 · Rivers, shores and the land

### 65. Many liquids as ground - built, not yet seen

Many liquids exist as ground: brine, boiling water, propane, acid and more, each with its own flood, rain, river, lake and sea. Nobody goes swimming in sand for fun.

**Look at:** brine, boiling water, propane, acid, tar, red slime

**Poke it:**

- hover each: the ground names its liquid

**Look for:** weak spot: two liquids that look the same

### 66. Six more liquids - built, not yet seen

Six more liquids

**Look at:** frigid, brackish, mineral, poisoned water, ammonia, coolant

**Poke it:**

- hover each: the ground names its liquid

**Look for:** weak spot: the four waters reading as plain water

### 67. Six odd grounds - built, not yet seen

Six odd grounds

**Look at:** fuel sap, ichor, ooze, reaction liquor, churnmud, tar glass

**Poke it:**

- hover each; walk a colonist across the churnmud and the tar glass

**Look for:** weak spot: tar glass that walks like liquid; churnmud that looks like plain mud

### 68. Coloured waters and slimes - built, not yet seen

Coloured waters and slimes

**Look at:** five coloured waters (top), five coloured slimes (middle), a bottle of each water (bottom)

**Poke it:**

- hover each; the bottles along the bottom are each water bottled
- coloured steam rises only off a RIVER of these waters (not here)

**Look for:** weak spot: two colours that read the same; a slime that looks like its water

### 69. Deep sand - built, not yet seen

Deep sand

**Look at:** a patch of deep sand with a colonist on it

**Poke it:**

- undraft him: idle colonists never go swimming in sand for fun
- hover: the walk cost

**Look for:** weak spot: deep sand that reads as ordinary sand

### 70. Liquid shores on new maps - built, not yet seen

New maps get shores of the local liquid, and hot rivers steam in colour. The shores change only newly generated maps.

**Look at:** shores come only on newly generated maps; here a boiling pool for the steam

**Poke it:**

- unpause: steam rises; hover the air over it: hotter

**Look for:** weak spot: no steam; the air over boiling water no warmer

### 71. A swale turns sand to soil - partly built

A water-fed canal improves the land: a swale turns sand into soil, and crops beside it count as watered. In the campaign the swale stays locked until found; its art comes from a real canal.

**Look at:** a swale on sand beside a water canal

**Poke it:**

- unpause for days: the sand beside the swale slowly turns to soil

**Look for:** weak spot: soil turning far from the swale; nothing changing after days

**Not built yet in this feature:** the swale being locked in the campaign until found; crops beside a filled canal counting as watered

### 72. Panning and the sluice box - built, not yet seen

Pan a river for gold, or set a sluice box to sift ore from a stream

**Look at:** a sluice box across the bank edge and a panning spot beside the shallow margin (painted river: see map R for the real one)

**Poke it:**

- unpause a day: the sluice washes a little ore onto its bank end
- a miner pans at the spot: mostly nothing, sometimes a few units

**Look for:** weak spot: ore on the water end; compare with map R, where the river is real

### 73. Every mechanic has a switch - built, not yet seen

Every mechanic can be switched off in Mod Settings, and with everything off the mod still digs dry canals

**Look at:** nothing to see here: open Options > Mod Settings > FlowWorks

**Poke it:**

- switch everything off: the mod still digs dry canals
- a master switch off greys its dependents and keeps their values

**Look for:** weak spot: a switch that changes nothing; all off and the dig order gone

## 9 · Rivers: the bank works as they look (they work on map R)

### 74. Ford stones (look) - built, not yet seen

Ford stones (look)

**Look at:** a shallow river with a line of ford stones across; painted, so no current

**Poke it:**

- judge the stones; the crossing itself is on map R

**Look for:** weak spot: stones that read as dry ground; a seam at the stones' edge

### 75. Bank works (look) - partly built

Bank works (look)

**Look at:** a weir, a stake line, a silt trap and ferry posts on a painted river: no current here

**Poke it:**

- judge the drawings; every one of them WORKS only on map R

**Look for:** weak spot: a rope drawn across land or not at all; a weir whose wet end sits on the bank

**Not built yet in this feature:** silt traps, stake lines and hoppers on river banks

## R - map R: the river works on a real river

River works only work on a real river: painted river ground has no current. So the second save (RM_fw_review_rivers_<date>) holds a river map with these stations, each placed where the river suits it; ask and the agent frames any one.

### R1. The current carries things

**Look at:** a log stack and a muffalo in the fast water, frozen before the current moves them

**Poke it:**

- unpause: the logs drift downstream and the muffalo is pushed along; at the map edge the water takes it

**Look for:** weak spot: does the push follow the river's bend, or run straight into the bank? A carried muffalo should bruise sometimes and drop what it carries

### R2. Ford stones across

**Look at:** a line of ford stones right across, and a drafted colonist on the near bank

**Poke it:**

- order him to the far bank: on the stones he is not carried
- order him across beside the stones: he is

**Look for:** weak spot: stones that read as dry ground in the middle of a river; a colonist pushed off the line

### R3. A weir pools and catches

**Look at:** a new weir on the bank; its slack pool forms upstream once the game runs

**Poke it:**

- unpause a few hours: the pool spreads upstream and fish and drift gather by the weir
- select it: the inspect line says what it holds

**Look for:** weak spot: a pool on the downstream side; a catch that never stops growing (the cap is 30)

### R4. A worn weir breaches

**Look at:** the same weir, worn below half health: the next flood breaches it

**Poke it:**

- dev: Incidents > seasonal flood, then unpause: the weir breaks and its catch is washed downstream

**Look for:** weak spot: a breach that deletes the catch instead of washing it a few cells; a breach with no letter

### R5. A stake-line levee

**Look at:** a line of bank stakes along the shore with one gap in the middle

**Poke it:**

- dev: Incidents > seasonal flood: the water stays behind the stakes and leaks only through the gap

**Look for:** weak spot: water crossing a stake; a stake that blocks walking (it should not)

### R6. A silt trap

**Look at:** a silt trap on the bank

**Poke it:**

- unpause a day: the soil beside it turns rich; remove the trap and it slowly goes back

**Look for:** weak spot: richening that spreads beyond the trap's neighbours

### R7. A ferry rope

**Look at:** two ferry posts on opposite banks with the rope strung between them

**Poke it:**

- undraft a colonist and send him across: he takes the rope and is not swept
- deconstruct one post: the rope goes too

**Look for:** weak spot: a rope drawn under the water or not at all; a rope across land

### R8. Sluice box and panning

**Look at:** a sluice box set into the bank and a panning spot beside it, on real moving water

**Poke it:**

- unpause a day: the sluice washes a little ore onto its bank end
- a colonist pans at the spot: mostly nothing, sometimes a few units

**Look for:** weak spot: ore that appears on the water end; panning that never yields

## F - free area

Round your colonists, in the middle of the map: steel, components, wood, granite blocks, chemfuel, bottles, buckets and barrels along the south edge, a pond on the east side. Dig, fill, build ladders, spikes, covers and doors here yourself.

## S0 and M

S0 (west of the free area) is the status board: each section's counts. M (below it) lists the look features still drawn with borrowed or missing art.
