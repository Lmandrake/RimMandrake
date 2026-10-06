# FlowWorks review map - key sheet

Load the save in RimWorld (Load game > RM_fw_review_20261005). The game is paused, god mode is on, clear weather, noon, Peaceful. Mod Settings are the shipped defaults.

Each station is labelled in the world with its number, a short name, its status and what to look at. Status colours: green = works in game, blue = built, not yet seen, gold = partly built, rust = not built.

51 stations: 13 works in game, 26 built, not yet seen, 10 partly built, 2 not built yet.

## V - pits: what they look like (north-west block)

Columns: depth 1 to 4, left to right. Rows from the bottom: dry in soil, dry in granite, water in soil, water in granite, tar in soil, tar in granite, scorched in soil, scorched in granite; the top row is oil and green slime at depth 3. A colonist stands in the near row of every pit so you can see how far the near bank hides him.

- **dry:** The far bank shows a lit face with a dark rim, the way the game draws its own walls; at depth 3 it is about a wall's height, at depth 4 taller. The side banks show as narrow faces. The person in the near row is hidden below the near bank, more the deeper the pit.
- **water:** The water shimmers and drifts instead of being one flat colour; a person walking through leaves a V-shaped wake. Deeper water keeps its darker colour. The far face shows only above the water line.
- **tar:** Tar is black but wet: slow glossy highlights slide across it, nothing like a burnt patch. It barely leaves a wake.
- **scorched:** Still an empty pit with the same walls, but charred: ash and char on the floor, soot climbing the faces, a scorch ring on the ground round the rim.
- **oil:** Oil: slow dark gloss with a faint rainbow film.
- **slime:** Slime: thick, soft bright blobs that barely move.

## 1 · Digging canals and pits

### 1. Dig a canal, dig deeper - works in game

You mark ground and a colonist digs a canal there; dig again to go one level deeper There are four depths. The fourth is a pit: nothing more than the deepest dug ground.

**Look at:** four depths side by side, D1 to D4; the right one is a pit

**Try:**

- unpause: a colonist digs the marked strip (top left)
- Architect > Orders > Dig canal on a dug strip: it goes one level deeper; a D4 strip refuses

### 2. Fill a canal back in - works in game

You can fill a canal back in, and the liquid in it is pushed along, not deleted Only liquid with nowhere at all to go is lost, and the game counts it.

**Look at:** a water canal with a fill-in order on its east end

**Try:**

- unpause: a colonist fills the marked cells and their water moves back along the canal, not deleted

### 3. Trenches slow people down - built, not yet seen

Trenches slow people down: deeper is slower, flooded is slower still, and a pit can't be crossed A dug line is a real barrier you can build defences with.

**Look at:** dry lanes D1, D2, D3, a pit row D4, and a flooded D2 lane

**Try:**

- hover a lane: the walk cost climbs with depth; the wet lane is slower than the dry D2
- order a colonist across: he goes round the pit row

### 4. Digging turns up minerals - partly built

Digging a canal sometimes turns up local minerals, with a letter the first time each one appears Deep cuts can reach the minerals deep drills find; where there are none, you get chunks of local rock.

**Look at:** a dig order 14 cells long, waiting for a colonist

**Try:**

- unpause: about 1 in 70 dug tiles leaves a lump on the bank, with a letter the first time

**Not built yet in this feature:** finds following the shared list of which minerals belong where

## 3 · Fire and corrosion

### 5. Fire lights tar - built, not yet seen

Fire or an explosion lights tar, oil or propane, and the flame travels along the canal Tar and propane creep like a fuse you can outrun; fuels go up fast.

**Look at:** a tar pond and its canal; the mark is where to drop a fire

**Try:**

- dev: Spawn fire (or an explosion) at the mark: the flame runs back along the canal
- nothing lights? 'Liquid ignition' ships OFF in Mod Settings > FlowWorks

### 6. A burning canal burns for days - built, not yet seen

A burning canal burns for days, spreads back into its pond, and sets anyone standing in it alight About one canal level a day; a pond burns far longer. Corrosive liquids also eat whatever stands in them (that one is switched off by default).

**Look at:** a long tar canal back to its pond

**Try:**

- light the far end, unpause: about one canal level a day, and it spreads back into the pond

### 7. Foam or rain puts it out - built, not yet seen

Foam or rain puts burning liquid out Foam keeps it out while the foam lies there; rain has a chance on open ground.

**Look at:** a tar canal with a firefoam popper beside it

**Try:**

- light it, then trigger the popper: foamed cells stop burning while the foam lies there

## 2 · Liquid in canals and ponds

### 8. A canal off the map edge drains - works in game

A canal that runs off the edge of the map drains away A canal ending inside the map holds its water.

**Look at:** the lower canal runs off the map edge and stays empty; the upper one ends inside the map and holds its water

**Try:**

- unpause: the lower canal keeps pouring away off the edge

### 9. Liquid spreads along the canal - works in game

Liquid spreads along a canal from its pond, in every direction, and stays inside the dug channel It moves in steady pulses, the same way every time; two canals off one pond both fill. Switching the engine off in settings freezes every canal where it is.

**Look at:** one pond, a canal branching three ways, all filled

**Try:**

- dig a new cell onto any end: next pulse it fills
- unpause: it moves in pulses, not every tick

### 10. Tar crawls, water runs - works in game

Each liquid keeps its own nature: tar crawls while water runs, and a canal shows the liquid it came from Water fed from water looks like water; tar fed from tar looks like tar.

**Look at:** same canal, same pulses: the water canal (top) is full, the tar canal (bottom) has crawled a few cells

**Try:**

- unpause and watch the tar front creep

### 11. Liquids never mix - built, not yet seen

Two different liquids never mix: where their fronts meet, both stop Drain one side and the other moves in. Old saves keep their liquids.

**Look at:** water from the west, tar from the east: the fronts meet and stop

**Try:**

- fill in a water cell: the tar moves in

### 12. A small pond runs dry - works in game

Any pond is a source: a lake touching the map edge never runs dry; an enclosed pond runs out An enclosed pond feeds about five canal tiles for each tile of water, then the flow stops.

**Look at:** a 2x2 pond feeding a long canal: it fills about 20 cells, then stops (5 canal cells per pond cell)

**Try:**

- the far end stays dry: the pond has paid out
- a lake touching the map edge never runs out

### 13. A pond shrinks as it pays out - built, not yet seen

A pond visibly shrinks as it pays out, and slowly refills from rain, season and seepage You can see a source being drawn down.

**Look at:** a 4x4 pond feeding a long canal: its edge cells turn to shallow then mud as it is drawn down

**Try:**

- unpause through rain: it slowly refills

### 14. Rain fills open trenches - works in game

Rain fills open trenches; roofed ones stay dry

**Look at:** two dry trenches; the right one is roofed

**Try:**

- dev: Change weather > Rain, unpause: the open trench fills, the roofed one stays dry

### 15. Canyon floods run through canals - built, not yet seen

Canyon floods run through your canals instead of wiping them out

**Look at:** a dry canal waiting for a canyon flood

**Try:**

- dev: start a canyon flood upstream: it runs down the canal

### 16. Slime is nearly uncrossable - not built yet

Slime is nearly impossible to cross and slow to climb out of Your words: so slippery it is nearly uncrossable.

Not built yet: the station is an empty concrete pad with its label.

## 4 · Pits: catching

### 17. Nothing climbs out of a pit - works in game

Anything that falls into a pit cannot climb out It stays where it is; its info line says it is trapped.

**Look at:** a muffalo in a 3x3 pit

**Try:**

- unpause: it walks the floor and never climbs out; its info line says trapped

### 18. A pit only holds what fits - works in game

A pit only holds a creature that fits: anything wider walks out, and narrowing a pit frees it Your rule: the pit must be as wide as the creature.

**Look at:** a muffalo in a 1-wide slot (too narrow) and a hare in a 1x1 pit

**Try:**

- unpause: the muffalo walks out, the hare stays

### 19. Falling in hurts - works in game

Falling in hurts, and your own colonists are not trapped unless you choose that in settings

**Look at:** a pit and one of your colonists beside it

**Try:**

- order him into the pit: he is hurt by the fall, and (shipped default) climbs back out

### 20. Shots only from the pit's edge - built, not yet seen

Someone in a pit can only shoot, and be shot at, from the pit's edge Raiders don't waste shots on them from further away.

**Look at:** a boar in a pit; your colonist stands 6 cells off

**Try:**

- order an attack on the boar: he walks to the lip before he can shoot

### 21. Jump in on purpose - partly built

A 'jump in' button drops a colonist in on purpose; explosions and knockback can throw people in Whoever jumps in is stuck there too.

**Look at:** a pit and a colonist beside it

**Try:**

- select him: 'Jump into pit' drops him in, and he is stuck there too

**Not built yet in this feature:** an explosion or knockback throwing someone into a pit

### 22. A cover hides the hole - works in game

A pit cover hides the hole and looks like the ground around it A faint seam shows only at the closest zoom.

**Look at:** left: a covered pit; right: the same pit uncovered

**Try:**

- zoom in close on the left one: only a faint seam shows

### 23. Step on a cover, fall through - built, not yet seen

Step on a cover and you fall through; three cover builds bear different weights Plank lattice, woven scrap, reinforced frame.

**Look at:** three covered pits: plank lattice, woven scrap, reinforced frame

**Try:**

- order a colonist across each: the weaker covers give way

### 24. Spikes at the bottom - built, not yet seen

Spikes at the bottom stab whoever falls in: badly, scaled to their size, never instantly fatal Walking up to the spikes is harmless; only a fall triggers them.

**Look at:** a pit floored with spikes

**Try:**

- walking up to the spikes is harmless; only a fall in triggers them

### 25. Flood an occupied pit - built, not yet seen

Flood an occupied pit to drown, poison or burn whoever is in it Water drowns non-swimmers, poison builds up, oil can be lit; open a gate to let the liquid in.

**Look at:** a boar in a pit, a water canal behind a shut sluice

**Try:**

- open the sluice (select it): water pours into the pit

## 5 · Pits: holding prisoners

### 26. A ladder in and out - works in game

A ladder: lowered, people climb out; raised, they're stranded It works like a prison door. Ladders only go on dug ground.

**Look at:** a pit with a ladder on its west wall and a colonist in it

**Try:**

- select the ladder: raise it and he is stranded; lower it and he climbs out

### 27. A pit prison, run from the lip - built, not yet seen

A walled-in pit is a room; add a prisoner bed and it's a prison you run from the edge Wardens feed, tend, capture, recruit and convert from the lip without climbing down; nothing too wide is offered.

**Look at:** a 3x4 pit with a prisoner bed and a prisoner

**Try:**

- wardens feed and talk to him from the lip; nobody climbs down

### 28. Sun and cold wear him down - built, not yet seen

An open pit bakes by day and freezes by night, wearing down a prisoner's resistance Colonists whose beliefs mind cruelty are upset by it; psychopaths are not.

**Look at:** an open pit with a prisoner, noon sun on it

**Try:**

- inspect a pit cell: hotter than the ground by day, colder by night

### 29. Sluice and grate doors - built, not yet seen

Sluice gates and grate doors let liquid through but hold creatures and prisoners They can't be opened from inside the pit; open one to let a held creature walk out.

**Look at:** a pit with a sluice (wood) and a security grate (steel) in its wall; a hare and a prisoner inside

**Try:**

- open either door: liquid flows through, nobody inside can open it

## 7 · Bottles, tanks and pumps

### 30. Bottles, buckets, barrels - built, not yet seen

Bottles, buckets and barrels: fill at a shore or tank, use, wash and reuse Boiling water cools and blood spoils in a bottle; bottles are tagged for a future cooking mod.

**Look at:** empty, full and dirty bottles, a bucket and a barrel by a pond and a tank

**Try:**

- unpause: colonists fill bottles at the shore or the tank and wash dirty ones

### 31. Tanks, pumps, hoses - built, not yet seen

Tanks store liquid; pumps move it from ponds and canals; hoses and adapters connect it all One full tank holds about five canal tiles of liquid.

**Look at:** a pump on the pond shore piped to a tank, powered by a battery

**Try:**

- unpause: the pump draws the pond down into the tank

### 32. Drills, taps and stills - built, not yet seen

Drills and taps bring underground liquids up, and cleaned water feeds thirst

**Look at:** a liquid drill, a tap, a fuelled still, a sun-pan still and a drip filter

### 33. Ruined liquid works - built, not yet seen

Ruined industrial liquid plants (desalination, tar refinery, pumping station) are found and repaired Never built from the menu in the campaign.

**Look at:** a wrecked desalination plant, a kludged tar refinery, a repaired pumping station

**Try:**

- select the wreck: repair it in stages; none are on the build menu in the campaign

## 6 · How it looks

### 34. People sink as the ground deepens - works in game

People sink as the ground deepens and rise as they climb out; in a pit the walls stand over their head Someone in slime is drawn sunk into it, not standing on top.

**Look at:** one colonist standing at each depth D1..D4

**Try:**

- undraft one and order it out: it rises step by step

### 35. A canal looks dug and shows how full - partly built

A canal looks dug, not like a gravel path, and shows how full it is Trace, half and brimming fills look different; trenches read as obstacles without a tooltip.

**Look at:** D2 cells: empty, trace, half, brim; and a brimming pit

**Not built yet in this feature:** a dug canal looking dug, not like a gravel path; trenches looking like obstacles without a tooltip

### 36. A pit reads as one dark hole - partly built

Pit walls are drawn with depth, Quarry-style, so a pit reads as one big dark hole Every depth looks different; an occupied pit reads differently from an empty one; never like a building.

**Look at:** two 4x4 pits: empty (left) and occupied (right)

**Not built yet in this feature:** an occupied pit reading differently from an empty one; painted pit-wall art for all four depths; a pit reading as a big dark hole; a large pit reading as one place, not a grid of tiles; a bare pit never looking like a building; depth and fill both readable at once

### 37. Spikes, ladder, gates: own drawings - partly built

Spikes, ladders and gates have their own drawings, not borrowed vanilla ones Today the ladder still borrows the vanilla spike trap; gates borrow the vanilla door.

**Look at:** a ladder, spikes, a sluice and a grate on dug ground, side by side

**Not built yet in this feature:** spike art where some spike shows; ladder art, raised and lowered; a gate looking open or shut at a glance (its own art); no pit part borrowing the vanilla spike-trap drawing

### 38. Tar and slime look thick - partly built

Tar looks thick and sticky; slime looks thick and opaque, not tinted water

**Look at:** a tar pond and canal (left), a slime pond (right)

**Not built yet in this feature:** slime looking thick and opaque, not tinted water

### 39. Burning liquid looks alight - partly built

Burning liquid looks alight, and a burnt-out canal looks scorched Today it uses the vanilla fire and ash.

**Look at:** a tar canal to light, and a scorched-dry pit beside it

**Not built yet in this feature:** burning liquid looking alight (its own art); a burnt-out canal looking scorched (its own art)

## 8 · Rivers, shores and the land

### 40. Many liquids as ground - built, not yet seen

Many liquids exist as ground: brine, boiling water, propane, acid and more, each with its own flood, rain, river, lake and sea Nobody goes swimming in sand for fun.

**Look at:** brine, boiling water, propane, acid, tar, red slime

### 41. Liquid shores on new maps - built, not yet seen

New maps get shores of the local liquid, and hot rivers steam in colour The shores change only newly generated maps.

**Look at:** shores come only on newly generated maps; here a boiling pool for the steam

### 42. A swale turns sand to soil - partly built

A water-fed canal improves the land: a swale turns sand into soil, and crops beside it count as watered In the campaign the swale stays locked until found; its art comes from a real canal.

**Look at:** a swale on sand beside a water canal

**Try:**

- unpause for days: the sand beside the swale slowly turns to soil

**Not built yet in this feature:** the swale being locked in the campaign until found; swale art drawn from a real canal; crops beside a filled canal counting as watered

### 43. Panning and the sluice box - not built yet

Pan a river for gold, or set a sluice box to sift ore from a stream

Not built yet: the station is an empty concrete pad with its label.

### 44. Every mechanic has a switch - built, not yet seen

Every mechanic can be switched off in Mod Settings, and with everything off the mod still digs dry canals

**Look at:** nothing to see here: open Options > Mod Settings > FlowWorks

**Try:**

- switch everything off: the mod still digs dry canals

## 8 · Rivers: the bank works

### 45. Ford stones - built, not yet seen

Ford stones

**Look at:** a shallow river with a line of ford stones across

**Try:**

- on a real river the current carries people; on ford stones it does not

### 46. A weir - built, not yet seen

A weir

**Look at:** a weir on the bank edge, its slack pool upstream

**Try:**

- select the weir: its pool and catch

### 47. Stake-line levee - partly built

Stake-line levee

**Look at:** a line of bank stakes with one gap

**Try:**

- a seasonal flood does not spread past the stakes, only through the gap

**Not built yet in this feature:** silt traps, stake lines and hoppers on river banks

### 48. Silt trap - partly built

Silt trap

**Look at:** a silt trap on the bank

**Try:**

- over time the ground beside it richens

**Not built yet in this feature:** silt traps, stake lines and hoppers on river banks

### 49. Fish catch - built, not yet seen

Fish catch

**Look at:** a weir that catches fish and drift

**Try:**

- unpause: fish and drift gather at the weir

### 50. Ferry rope - built, not yet seen

Ferry rope

**Look at:** ferry posts on both banks, the rope strung between

**Try:**

- undrafted colonists cross on the rope instead of being swept

### 51. Drift and breach - built, not yet seen

Drift and breach

**Look at:** an untended weir: in a flood it breaches and washes its catch away

**Try:**

- dev: start a flood: the weir breaches

## F - free area

Round your colonists, in the middle of the map: steel, components, wood, granite blocks, chemfuel, bottles, buckets and barrels along the south edge, a pond on the east side. Dig, fill, build ladders, spikes, covers and doors here yourself.

## S0 and M

S0 (west of the free area) is the status board: each section's counts. M (below it) lists the look features still drawn with borrowed or missing art.
