# Pyrelands review map - key sheet

Load (no keeper saved yet: build, then --save) in RimWorld. Paused, god mode on, research finished, Clear weather locked, noon, Peaceful. Mod Settings are the shipped defaults. Every station carries an in-world sign: its number, a short name, one clause, then LOOK / DO / DECIDE (zoom in to read the last three); this sheet repeats each sign and has the rest. Each station also has a SIGN BOOK in the save itself, on the cell just north of its west corner: mouse over it for the DO line, press i for the whole sign; it needs no agent and no mod. The floating labels return with the save when the JawaBench companion is awake; if they are missing, `--labels` re-pins them. Colonists are drafted inside the cool shelter at F: outside is ~50 C, so anything that sends a colonist out costs Heatstroke.

Navigate: `--goto N` (station), `--goto F`, `--goto N0`, `--goto R`, `--goto 0`. Rows run north to south: A ground, B fire, C plants, D build and craft, E creatures, F campaign cast.

## A - Ground

### 1. Deep ash

*The biome's ordinary ground.*

**Sign:** LOOK: grey-black ash ground, not dirt or concrete. DO: hover a cell: it should say deep ash, 40%. DECIDE: does it read as ash? any ugly edge?

**Look for:** Reads as grey-black ash, not dirt or concrete. Weak spot: the tile edges against vanilla terrain; the three retired ash rungs (trace/light/heavy) still ship PNGs no def points at.

**Poke it:**

- Hover a cell: terrain 'deep ash', fertility 40% dry.

**If you unpause:** Nothing changes on bare ash.

### 2. Unburned pockets

*Soil, rich soil, gravel, sand: burn to ash.*

**Sign:** LOOK: four pockets: soil, rich soil, gravel, sand. DO: light one with Dev > Debug actions > Fire. DECIDE: does it turn to deep ash in one step?

**Look for:** Four pockets that have not burned. Weak spot: all four borrow the VANILLA textures, so nothing says Pyrelands until they burn.

**Poke it:**

- Hover each: 'soil' 70%, 'rich soil' 140%, 'gravel' 28%, 'sand' 5%.
- Start a fire on one (god mode: Dev > Debug actions > Fire): it burns to deep ash in one step.

**If you unpause:** Nothing, unless fire reaches them.

### 3. Water ring

*Standing water ringed with rich ground.*

**Sign:** LOOK: water ringed with mud, then rich soil. DO: hover the rich soil (140%); compare N0's pond. DECIDE: does it look like the biome's own pond?

**Look for:** The biome's terrain patch makers ring water with mud and rich soil. Compare N0 (the site's own pond).

**Poke it:**

- Hover the rich soil: 140%. Plant something on it.

**If you unpause:** Nothing.

### 4. Firebreak line

*The buildable firebreak floor.*

**Sign:** LOOK: a stone firebreak strip beside grass. DO: light the grass (Dev > Debug actions > Fire). DECIDE: does the fire stop at the line? does it look deliberate?

**Look for:** Architect > Floors > firebreak line. Weak spot: it borrows RoughHewnRock's texture; does it read as a deliberate firebreak beside grass?

**Poke it:**

- Lay more of it yourself (god mode builds at once).
- Light the grass (Dev > Debug actions > Fire): the fire stops at the line.

**If you unpause:** Nothing until you light the grass.

### 5. Loose ash drifts

*Fire and ash fall leave loose ash.*

**Sign:** LOOK: loose ash, 1 to 4 layers, west to east. DO: select a drift; clean it if you like. DECIDE: do thick drifts read as ash, or as dirt?

**Look for:** RM_FE_Filth_LooseAsh at 1, 2, 3 and 4 passes, west to east. Weak spot: thick drifts may read as dirt.

**Poke it:**

- Select the filth: cleaning removes it.
- --weather RM_FE_Weather_AshFall lays more over the whole map.

**If you unpause:** Nothing; colonists may clean it if it is in the home area (it is not).

### 6. Fulgurite on sand

*Lightning glass where a strike hit sand.*

**Sign:** LOOK: three lumps of lightning glass on sand. DO: zoom to play distance; haul one. DECIDE: do the lumps read as glass at play zoom?

**Look for:** Three RM_FE_Fulgurite lumps on Pyrelands sand: how the glass reads at play zoom.

**Poke it:**

- --weather DryThunderstorm and unpause: strikes on sand leave fulgurite (35% a strike).
- Haul one: it is an item (fulgurite).

**If you unpause:** Locked Clear weather: no lightning until you switch weather.

### 7. Heat: sun vs shade

*Overhead sun; a roof answers it.*

**Sign:** LOOK: west pad open sky, east pad under a roof. DO: walk a colonist onto each pad; watch his heatstroke. DECIDE: does the roofed pad clearly slow heatstroke?

**Look for:** West pad open sky, east pad under a roof on four granite posts. The cell temperature is the same; the difference is in a pawn's felt heat (the sun-heat kind 'overhead', +4..10 C, from the shared CreatureBehaviors engine). Weak spot: nothing on screen says which pad is shaded except the roof overlay.

**Poke it:**

- Undraft a colonist, walk him to each pad, compare his Heatstroke climb (Health tab).
- Toggle the roof overlay (bottom-right) to see the shade.

**If you unpause:** A pawn left in the open pad gains Heatstroke; in shade, slower.

## B - Fire

### 8. Before the burn

*Unburned grass on soil: light it.*

**Sign:** LOOK: unburned grass on soil. DO: light it (Dev > Debug actions > Fire), unpause at 1x. DECIDE: does it end up like the AFTER pad next door?

**Look for:** The twin of the next station before fire: ember grass and quickgrass on an unburned soil pocket.

**Poke it:**

- Light it: Dev > Debug actions > Fire on a grass cell, then unpause at 1x.
- Or equip the firefoam sprayer (D, items) and put it out half way.

**If you unpause:** Paused: nothing. Lit: burns out in ~1-2 in-game hours inside the ring and leaves what the AFTER pad shows.

### 9. After the burn

*Burned during the build, then put out.*

**Sign:** LOOK: the same pad, burned during the build. DO: hover a cell: fertility shows +50% burn bonus. DECIDE: ash, loose ash, maybe a pod: does it look burned?

**Look for:** The same pad burned for ~1.5 h: soil -> deep ash in one step, loose ash dusted on it, and maybe a scorch-fruit pod (1 in 20 burned cells). Weak spot: leafless (burnt) grass art; a pod that never appears.

**Poke it:**

- Hover a burned cell: fertility shows the fresh-burn bonus (+50%, fading over 6 days).
- Unpause at 3x: ember grass re-greens within a few days, largely green in about a week.

**If you unpause:** Regrowth over days; any scorch-fruit pod ripens and withers within ~a day.

### 10. Burning now

*A live fire, paused mid-burn.*

**Sign:** LOOK: a live fire, paused mid-burn. DO: unpause at 1x and watch it walk. DECIDE: do fire and smoke look right on ash ground?

**Look for:** Ember grass on deep ash, lit along its west edge at the end of the build and paused ~300 ticks in. Look at the flames on the grass and the smoke. Weak spot: does fire on ash ground look right (the ground itself never burns)?

**Poke it:**

- Unpause at 1x and watch it walk; it cannot cross the ring.
- Firefoam it, or Dev > Debug actions > extinguish.

**If you unpause:** Burns out inside the ring in about an hour.

### 11. Burn bonus vs control

*Burned ash feeds; unburned ash does not.*

**Sign:** LOOK: west half burned, east half not. DO: hover both halves: about 90% vs 40%. DECIDE: is the burned half visibly better?

**Look for:** West 4x8: deep ash that burned during the build. East 4x8: the same deep ash, unburned. Weak spot: the bonus is invisible unless you hover; does a crop on the burned half grow visibly faster?

**Poke it:**

- Hover both halves: fertility ~90% burned vs 40% control.
- --weather RM_FE_BlackRain and unpause ~15 h: the bonus washes away and the black rain waters the ash (both halves go up to 140%).

**If you unpause:** The bonus fades linearly over 6 days.

### 12. Burrower

*An ashwallow in grass: light it.*

**Sign:** LOOK: an ashwallow in grass. DO: light the west edge, unpause at 1x, select it. DECIDE: can you SEE that it has burrowed, and that it survives?

**Look for:** A wild ashwallow penned on a grass pad. When fire reaches it, it burrows (status 'burrowed') and comes up unharmed after the fire passes. Weak spot: is the burrowed state readable on screen?

**Poke it:**

- Light the west edge (Dev > Debug actions > Fire), unpause at 1x, select the ashwallow.

**If you unpause:** Paused: nothing. Lit: the burn crosses the pen; the ashwallow dives and surfaces.

### 13. Firebreak and foam

*Lay your own firebreak, then light it.*

**Sign:** LOOK: an open grass pad: your tools vs fire. DO: lay a firebreak, light one side, spray firefoam. DECIDE: do the firebreak and the foam both stop it?

**Look for:** An unringed grass pad: try the player's tools against fire.

**Poke it:**

- Architect > Floors > firebreak line across the pad, then light one side.
- Equip a colonist with the firefoam sprayer (D, items) and spray the fire.

**If you unpause:** Paused: nothing. The pad is surrounded by bare ash, so the fire cannot leave the station.

## C - Plants

### 14. Ember grass: growth

*Sprout to full, west to east.*

**Sign:** LOOK: ember grass at 5, 25, 50, 75, 100%. DO: hover each strip for its growth. DECIDE: does young grass read as young, or just small?

**Look for:** Five strips at growth 5, 25, 50, 75 and 100%. Three random variants (A/B/C). Weak spot: young ember grass is only the full sprite shrunk (vanilla), so growth reads as size only.

**Poke it:**

- Hover a strip: growth %.
- Unpause: it grows in under a day (growDays 0.8).

**If you unpause:** All strips reach full within a day.

### 15. Quickgrass: 3 stages

*Sprout, half, tall: three drawings.*

**Sign:** LOOK: three drawings: sprout, half, tall. DO: hover each strip for its growth. DECIDE: are the three stages clearly different?

**Look for:** Its own three-stage art (Plant_GrowthStaged): growth 20% sprout, 50% half, 90% tall. Weak spot: RM_FE_QuickgrassStages also holds stray copies of the sprout/half PNGs at its root, unused.

**Poke it:**

- Hover each strip: growth %.
- Unpause: it reaches tall in about a day (growDays 1).

**If you unpause:** All strips grow to tall within a day.

### 16. Ground cover mix

*Ember and quick grass, carpeting ash.*

**Sign:** LOOK: the two grasses mixed, 3 ember to 1 quick. DO: compare with N0, the site's own ground. DECIDE: grass everywhere, ash where burned, no bare dirt?

**Look for:** The two grasses at about the biome's mix (3 ember : 1 quick), 10x10. PYRELANDS_GRASS_SATURATION_1 waits on your look: grass everywhere, ash where burned, no bare dirt. Compare N0 (the site's own ground).

**Poke it:**

- Walk N0 too (--goto N0): that is what the biome itself grew.

**If you unpause:** Nothing visible within hours.

### 17. Scorch-fruit pods

*Unripe, growing, ripe: four pod drawings.*

**Sign:** LOOK: pods unripe, growing, ripe. DO: hover each: growth and 'harvestable'. DECIDE: can you tell a ripe pod from an unripe one?

**Look for:** Pods are fire-born (never wild): here planted by hand at growth 0.5%, 50% and 100%. Four random variants. Weak spot: a ripe pod and an unripe one may look the same.

**Poke it:**

- Hover: growth and 'harvestable'.
- Unpause ~1 day: ripe pods wither (rotDestroys).

**If you unpause:** Ripe pods wither within about a day; that is the point of the fruit.

### 18. Scorch-fruit harvest

*Pick it, eat it, watch it rot.*

**Sign:** LOOK: ripe pods and a stack of fruit. DO: designate harvest; hover the stack for spoil time. DECIDE: does it harvest, show as food, and rot in ~4 days?

**Look for:** Ripe pods plus a stack of 10 harvested scorch-fruit on the ground. Weak spot: rot timing (fruit ~4 days unrefrigerated) and whether eating it shows as food.

**Poke it:**

- Designate the pods for harvest; a colonist walks out (heat!) and picks 5 a pod.
- Hover the stack: 'spoils in 4 days'. Force-feed a colonist (right-click > consume).

**If you unpause:** Pods wither in ~a day; the stack rots in ~4 days.

### 19. Ash + water

*Deep ash beside water feeds; dry ash starves.*

**Sign:** LOOK: ash strip, water at the west end, potatoes. DO: hover beside the water, then the dry end. DECIDE: 140% by water, 40% dry: do the crops show it?

**Look for:** A deep-ash strip with one water cell at its west end and a potato row along it. Watered ash reads 140%, dry ash 40% (radius 2 from water). Weak spot: nothing but the hover shows the watering; if the dry end refused the potatoes, the ash was too poor to sow, which is the point.

**Poke it:**

- Hover the cell beside the water vs one 8 cells east.
- Unpause a few days: the potatoes near the water pull ahead.

**If you unpause:** Crops beside the water grow clearly faster.

## D - Build and craft

### 20. Breaker: armed

*Battery, breaker, battery; hopper full.*

**Sign:** LOOK: breaker between two charged batteries. DO: Dev > Incidents > Zzzt, then read both batteries. DECIDE: did it trip and save one side? does tripped look tripped?

**Look for:** A lightning breaker between two charged batteries, its hopper full of glass sand. A short circuit on one side trips it and spares the other side's batteries. Weak spot: the tripped (_Off) drawing.

**Poke it:**

- Dev > Incidents > Zzzt (short circuit): it can only pick a conduit here (21's batteries are empty and the shelter has no conduit).
- Then read both batteries and click 'Re-arm breaker'.

**If you unpause:** Nothing until a short circuit.

### 21. Breaker: no glass

*The same chain, hopper empty: not armed.*

**Sign:** LOOK: the same chain, hopper empty. DO: select the breaker: 'Not armed'. DECIDE: does an unarmed breaker look different at all?

**Look for:** Inspect reads 'Not armed: needs 10 glass sand'. Weak spot: does an unarmed breaker look different at all?

**Poke it:**

- Select the breaker: hopper 0 / 30.
- Drop glass sand from F and let a colonist refuel it.

**If you unpause:** Nothing.

### 22. Breaker core: smithy

*Metal and glass sand at the smithy.*

**Sign:** LOOK: smithy, steel, glass sand, one finished core. DO: Smithy > Bills > Make lightning breaker core. DECIDE: is the bill there? does the core look right?

**Look for:** A fueled smithy with steel, glass sand and wood beside it, and one finished breaker core. The research is finished on this map (god mode); its Pyrelands-only gate is the matrix's to show.

**Poke it:**

- Smithy > Bills > Make lightning breaker core.
- Hover the core on the floor: its drawing.

**If you unpause:** A colonist would craft it (they are drafted in the shelter).

### 23. Shovel sand

*An order: sand to glass sand, leaves gravel.*

**Sign:** LOOK: a patch of Pyrelands sand. DO: Orders > Shovel sand; undraft a miner; unpause. DECIDE: does he dig glass sand and leave gravel?

**Look for:** A Pyrelands sand patch. Orders > Shovel sand: a miner digs 5 glass sand a cell and the cell becomes gravel (a finite deposit). Weak spot: whether a miner takes the order at all (proven only by ProofShovel).

**Poke it:**

- Orders > Shovel sand over the patch; undraft a colonist with Mining (heat!).
- Unpause.

**If you unpause:** The colonist digs; glass sand piles up; gravel is left.

### 24. Pyrelands items

*Hide, glass, fruit, core, sprayer.*

**Sign:** LOOK: hide, glass, fruit, core, sprayer, glass sand. DO: hover each item for its label and text. DECIDE: does each have its own look? (hide borrows leather)

**Look for:** Furnace hide, fulgurite, scorch-fruit, breaker core, firefoam sprayer and glass sand, one stack each, west to east. Weak spot: the furnace hide has no texture of its own (it draws its parent leather).

**Poke it:**

- Hover each: label and description.
- Equip the sprayer and aim it at BURNING NOW.

**If you unpause:** Fruit rots in ~4 days.

## E - Creatures

### 25. Fire-hawk

*Flyer, shown standing only.*

**Sign:** LOOK: a flyer, shown standing only. DO: look at all three facings. DECIDE: standing art right? (flight is judged with you live)

**Look for:** Three facings standing. Its five flying frames and its ember carrying are a FLIGHT: judged only with you present (FIREHAWK_FLIGHT_BEHAVIOR_1), never here.

**Poke it:**

- Rotate the camera round it; check the three facings.

**If you unpause:** It stays in its roofed pen.

### 26. Fire-wasp

*Flyer, shown standing only.*

**Sign:** LOOK: a flyer, shown standing only. DO: look at all three facings. DECIDE: standing art right? (flight is judged with you live)

**Look for:** Standing art only; its eight fly frames are a flight (owner-present only).

**Poke it:**

- Look at all three facings.

**If you unpause:** It stays in its roofed pen.

### 27. Furnace-beast (giant)

*The walking hearth: it warms a cold room.*

**Sign:** LOOK: this pen and the control pen east both start cold. DO: hover both floors; unpause 1 hour at 1x; hover again. DECIDE: is this pen clearly warmer than the control pen?

**Look for:** The giant (setting on by default; body size 6). Its pen and the CONTROL PEN east of it are the same room; the build chilled both to 10 C, because outside is ~55 C and the beast's heat pusher stops at 24 C (a pen at the outdoor 56 C can never read warmer: the 2026-10-15 build measured 56.75 vs 56.68). Weak spot: its warmth/thermal comps attach by a patch that only applies when RimUtinni Patches is loaded (RM_PyrelandsIgniters_Comps.xml); standalone Pyrelands ships a plain beast.

**Poke it:**

- Hover the floor of both pens: room temperature.
- Unpause at 1x for an in-game hour: this pen should climb clearly faster than the control pen (both drift back toward the outdoor heat through the walls).
- Select the beast: 'Heat charge' in its inspect pane (it charges in heat above 35 C).

**If you unpause:** Its pen warms faster than the control pen; when it lies down it may smoulder its bed (the ash floor has nothing to burn).

### 28. Control pen: no beast

*The same room with no beast in it.*

**Sign:** LOOK: EMPTY ON PURPOSE: the yardstick for the beast. DO: hover its floor, then the furnace-beast pen west. DECIDE: after an hour unpaused, is this pen the cooler one?

**Look for:** Same walls, roof, floor and starting chill as the furnace-beast pen west of it, and nothing inside: it is the yardstick for the beast's heat, not a missing animal.

**Poke it:**

- Hover the floor: room temperature, against the beast's pen.

**If you unpause:** Warms only from the outdoor heat through its walls, slower than the beast's pen.

### 29. Ullai herd

*The ash grazer, three of a herd.*

**Sign:** LOOK: three ullai, the ash grazer. DO: look at facings and size beside the others. DECIDE: does it read as a herd grazer?

**Look for:** Three facings, herd look. Its burn-following walk (to a two-day-old burn) needs days of roaming: the matrix's row, not this pen.

**Poke it:**

- Look at the three facings and its size beside the others.

**If you unpause:** They graze the pen.

### 30. Ashwallow

*The burrowing grazer.*

**Sign:** LOOK: the burrowing grazer, standing. DO: look at all three facings. DECIDE: is the art right? (its burrow is at BURROWER)

**Look for:** Standing art (three facings). Its burrow is shown at B (BURROWER).

**Poke it:**

- Facings.

**If you unpause:** It grazes.

### 31. Emberscythe

*Predator; its dessicated art still borrows.*

**Sign:** LOOK: a predator. DO: look at all three facings. DECIDE: is the art right? (only its rotted corpse borrows)

**Look for:** Three facings (emberscythe_v1). Weak spot: only its dessicated (rotted corpse) graphic is the Megascarab's.

**Poke it:**

- Facings.

**If you unpause:** It stays.

### 32. Sytheclaw

*Predator.*

**Sign:** LOOK: a predator. DO: look at all three facings. DECIDE: is the art right?

**Look for:** Three facings.

**Poke it:**

- Facings.

**If you unpause:** It stays.

### 33. Barbslinger

*Predator with a tail gun.*

**Sign:** LOOK: a predator with a tail gun. DO: look at all three facings. DECIDE: is the art right? (the spike shows only in a fight)

**Look for:** Three facings (the scorpion redesign). Its spike projectile shows only in a fight.

**Poke it:**

- Facings.

**If you unpause:** It stays.

### 34. Flamefang

*Predator; a venomous bite.*

**Sign:** LOOK: a venomous predator. DO: look at all three facings. DECIDE: is the art right? (the venom shows only after a bite)

**Look for:** Three facings. Its venom (RM_FlamefangVenom) shows only after a bite.

**Poke it:**

- Facings.

**If you unpause:** It stays.

## F - Campaign cast

### 35. Anooba

*Campaign roster (utinnipatches).*

**Sign:** LOOK: a canon animal the campaign adds here. DO: look at all three facings. DECIDE: does it belong in the Pyrelands?

**Look for:** A canon kind the campaign adds to the Pyrelands roster (WildAnimals_Pyrelands.xml); its art is SWBestiary's, not this mod's. Here so the whole roster stands in one place.

**Poke it:**

- Facings.

**If you unpause:** It stays.

### 36. Iriaz

*Campaign roster (utinnipatches).*

**Sign:** LOOK: a canon animal the campaign adds here. DO: look at all three facings. DECIDE: does it belong in the Pyrelands?

**Look for:** A canon kind the campaign adds to the Pyrelands roster (WildAnimals_Pyrelands.xml); its art is SWBestiary's, not this mod's. Here so the whole roster stands in one place.

**Poke it:**

- Facings.

**If you unpause:** It stays.

### 37. Nuna

*Campaign roster (utinnipatches).*

**Sign:** LOOK: a canon animal the campaign adds here. DO: look at all three facings. DECIDE: does it belong in the Pyrelands?

**Look for:** A canon kind the campaign adds to the Pyrelands roster (WildAnimals_Pyrelands.xml); its art is SWBestiary's, not this mod's. Here so the whole roster stands in one place.

**Poke it:**

- Facings.

**If you unpause:** It stays.

### 38. Orray

*Campaign roster (utinnipatches).*

**Sign:** LOOK: a canon animal the campaign adds here. DO: look at all three facings. DECIDE: does it belong in the Pyrelands?

**Look for:** A canon kind the campaign adds to the Pyrelands roster (WildAnimals_Pyrelands.xml); its art is SWBestiary's, not this mod's. Here so the whole roster stands in one place.

**Poke it:**

- Facings.

**If you unpause:** It stays.

### 39. Zeer

*Campaign roster (utinnipatches).*

**Sign:** LOOK: a canon animal the campaign adds here. DO: look at all three facings. DECIDE: does it belong in the Pyrelands?

**Look for:** A canon kind the campaign adds to the Pyrelands roster (WildAnimals_Pyrelands.xml); its art is SWBestiary's, not this mod's. Here so the whole roster stands in one place.

**Poke it:**

- Facings.

**If you unpause:** It stays.

### 40. Dalgo

*Campaign roster (utinnipatches).*

**Sign:** LOOK: a canon animal the campaign adds here. DO: look at all three facings. DECIDE: does it belong in the Pyrelands?

**Look for:** A canon kind the campaign adds to the Pyrelands roster (WildAnimals_Pyrelands.xml); its art is SWBestiary's, not this mod's. Here so the whole roster stands in one place.

**Poke it:**

- Facings.

**If you unpause:** It stays.

### 41. Gizka

*Campaign roster (utinnipatches).*

**Sign:** LOOK: a canon animal the campaign adds here. DO: look at all three facings. DECIDE: does it belong in the Pyrelands?

**Look for:** A canon kind the campaign adds to the Pyrelands roster (WildAnimals_Pyrelands.xml); its art is SWBestiary's, not this mod's. Here so the whole roster stands in one place.

**Poke it:**

- Facings.

**If you unpause:** It stays.

## Boards (labels, no build)

### N0. Natural ground

*the site's own cover round its pond: untouched.*

**Sign:** LOOK: what the biome grew by itself. DO: walk it; compare station 16. DECIDE: grass everywhere, ash where burned, no bare dirt?

What the biome grew by itself: the two grasses, deep ash, a pond ringed with rich ground and mud. PYRELANDS_GRASS_SATURATION_1 asks for your look here: grass everywhere, ash where burned, no bare dirt.

### R. Scorched ruin

*the nearest ruin the build found.*

**Sign:** LOOK: the nearest ruin on the map. DO: look at the ground under and round it. DECIDE: is the ruin blackened, or pristine?

Ruins on a Pyrelands map stand blackened: deep ash under and round them, loose ash filth, burned stuff. Weak spot: a pristine ruin (PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE).

### G. Weather switch

*one global switch: --weather NAME.*

**Sign:** LOOK: weather is one switch for the map. DO: ask the agent: --weather NAME, then unpause. DECIDE: does each weather read as itself?

Weather is global, so it is one switch, not stations. RM_FE_Weather_AshDrift: free-flying ash like snow (the commonest). RM_FE_Weather_AshFall: the map dims, loose-ash drifts pile up. RM_FE_Weather_Cinderfall: glowing cinders, must not read as ash fall renamed. RM_FE_BlackRain: dark rain, washes the burn bonus at 11, waters ash. DryThunderstorm: lightning without rain; strikes on sand leave fulgurite (6), and a strike on station grass starts a fire there. There is no ordinary rain here. Unpause to see it fall; --weather Clear puts the calm back.

### S. Mod settings

*Options > Mod Settings > Pyrelands.*

**Sign:** LOOK: every setting at its default. DO: Options > Mod Settings > Pyrelands. DECIDE: are the toggles clear? anything missing?

Every toggle at its shipped default. Station by setting: fulgurite 6; fire dusts ash 5, 9; scorch-fruit seeding 9, 17; ash-fall drifts 5, G; watered ash 19; fresh-burn bonus 9, 11; rain fades bonus 11; ambient drift G; growth stages 15; wild allowlist N0; scorched ruins R; standing burn line L; fire-hawk carrying 25 (flight, owner-present); furnace thermal 27-28; fire clock E; world migration W; giant furnace-beast 27 (restart); ullai herds 29 (restart); burrowing 12; breakers 20-22; shovel sand 23; cross-biome (off). PyrelandsMechanics: arson-justice raids, flame-harvest visits, the tribes' fire rite: E.

### W. World map

*press the World tab.*

**Sign:** LOOK: the biome on the world map. DO: press the World tab. DECIDE: does the Pyrelands patch look right?

The site sits in a 2-ring Pyrelands patch: the biome's world drawing. A furnace-beast herd marker (RM_FurnaceHerd) may be on the world; it migrates over days. Pyrelands has 0 tiles on Ash'karr by design (painted once at the end).

### E. Fire-clock events

*Dev > Incidents: RUT_FlameHarvest, RUT_FireRaid.*

**Sign:** LOOK: fire-clock events (Peaceful keeps them off). DO: save first; Dev > Incidents > RUT_FireRaid etc. DECIDE: does each event make sense?

Storyteller events from RimUtinni PyrelandsMechanics: a flame-harvest visit, an arson-justice fire raid, and the tribes' fire rite (they light the burn themselves). Peaceful keeps them away; fire one from the Dev menu to see it. A fire raid is hostile: save first.

### L. Burn line and fire front

*put out by the calm world; it comes back.*

**Sign:** LOOK: the burn line was put out for the calm. DO: unpause at 3x for ~2 days. DECIDE: does a fire come back on its own?

A Pyrelands map is never fireless: after 2 quiet days the standing burn relights one smoulder, and every 2-4 days a fire front sends a grass line up. Unpause at 3x for ~2 days to see it return. Once wild grass regrows between stations (days), a front can reach station grass.

### F. Free area and shelter

A roofed granite shelter with two coolers on a solar + battery net (no conduits, so a short circuit can only hit station 20). Colonists stand drafted inside; undraft one to use him. Stock on the south edge: steel, wood, granite blocks, components, glass sand, survival meals, medicine, two firefoam sprayers.
