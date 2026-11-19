# The Chill: the design, seen from the ship

**Status:** the design document for one sea, the Chill (`RM_TheChill`, the fourth sea of the mod
`src/RimMandrake/TerminalBiomes/`; its floor mechanics live in `src/RimMandrake/DivingInteraction/`, its beach
pipework in `src/RimUtinni/PropaneLakeMechanics/`; older files call it the Propane Lake, and the frozen campaign
twin is still `RUT_PropaneLake`). Written 2026-11-18 on the owner's instruction to see every biome "through the lens
of Utinni". The same day's first pass wrote all four seas as one design and read thirteen of its sources by
heading only; that combined design was retired on 2026-11-18 and kept only in git history, commit `b2530669e5`,
once each sea had its own design. This file is the Chill written on its own with its sources read through. What
happened to every idea, and what this file corrected against the combined design, is in
`design/concepts/TerminalBiomes/TheChill_rewrite_choices.md`, which also says exactly which files were read whole
and which were not. None of the Chill's older source files has been deleted. This is a design document only and it
launches nothing.

**Kind, checked against the sheet's own header and his rulings:** a sea. *"Umbra is a region not a biome. The
Propane Lake is an ocean-biome made of propane, definitely its own biome."* (owner, 2026-09-21.) So two rulings
shape every section. *"You can't 'dive' as an individual pawn nor return as one. It's ship or nothing."* (owner,
2026-09-26.) And *"You are either on their sea floor, or you are on their beach. There is no 'on their surface'
location."* (owner, 2026-11-01.) The ship flies to the floor as its own planet layer (`RM_SeabedLayer`; owner,
2026-10-01: *"Now the ship just flies to a new planetary layer called sea floor"*), lands there, and is the only
way back. The beach is the land beside the lake, which is the Auroral Umbra (`RUT_Umbra`); this design covers the
beach only as the place a ship stands to fuel and fish, and leaves the Umbra's own land to its own design.

**No locked Designer sheet or tree exists for this sea.** The mod's only pipeline material is the cleanse proposal
of 2026-11-17 (never applied), plus two short pages of the owner's own answers to a Designer rehearsal, dated
2026-11-10: `design/RimMandrake/designer_codex_2026-11-09/TheChillFloor/ANSWERS_OWNER.md` and
`.../PropaneLakesShore/ANSWERS_OWNER.md`. Those six answers are his latest words on this place and this design is
built on them. They are dated before the cleanse, and the cleanse switched off the very thing three of them
describe; that is corrected here (see `TheChill_rewrite_choices.md`, "Scope moves").

**Who reads this next:** a Designer run on the concept `TerminalBiomes` is handed the list of files in this folder
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing
in the pipeline reads it by name yet.

**One dependency under everything.** The ship's flight down and up (`SEABED_DESCENT_ASCENT_1`) is still an open
item whose live proof nobody has run, and the saved world's sea tiles are the frozen twin's, which fall back to a
generic empty floor until the one repaint (`design/RimMandrake/sea_floor_census_2026-10-29.md`, "Blockers"). Every
promise below reaches a player only when a ship that lands on the Chill's floor tile gets the Chill's floor.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means a
file of that name was found in `src/` on 2026-11-18, or the special-mechanics review of 2026-10-22 lists it as
built; every built Chill mechanic in that review reads "built-untested" except the air pump, which was checked on a
test map. Built is not passed.

---

## What this place is

> *"A frigid alien sea with unspeakable beauty and strangeness. All is fuel yet nothing burns."*
> (owner, typed, 2026-10-20)

> *"The far end of the world: a black sea of liquid fuel under the brightest sky on the planet."*
> (`the_propane_lakes.md` §1)

At the antistellar point, where the cold is far below the temperature at which propane turns liquid, the planet's
hydrocarbon haze has pooled into one lake. The sheet calls it *"the planet's fuel tank"* and its handle for the
whole region is *"the exhaust port of a machine"*. From the beach it is a black mirror under the strongest aurora
on the world. From inside it is something else: *"Liquid propane is water-clear; the black mirror is only black
from above."* On the floor the aurora arrives drowned, as dim curtains moving over a garden of crystal and wax,
and the owner's own brief for that garden is the register every part of this design answers to:

> *"eerily beautiful, alien and strange and mildly wonderful"* · *"delicate, entrancing, precious, shocking when it
> can actually defend itself but quite overcomable"* · *"totally unlike the dayside."* (owner, typed, 2026-09-27)

The chemistry is upside down, and the flora pass put it in one line: *"Water here is a mineral, not a solvent."*
Ice is the bedrock. Wax is flesh. Fuel is the water. And because there is no oxygen below, the sea of fuel is,
from inside, *"the most fireproof place on the planet"*. *"So there's no oxygen down in the sea floor so it's not
explosive."* (owner, typed, 2026-09-27.)

**Why the garden is beautiful at all.** He said why, the same day: the whole aesthetic exists *"so that the player
really feels the choice later to blow it up or not to get to the ancient war lab."* The lab under this lake is the
campaign's ending and belongs to the campaign layer. What this design owes it is a floor a player would grieve.

**Seen from the ship, this is the stop where the hull is the only warm thing in the world.** His answer of
2026-11-10 to "what draws an expedition beyond the ship" is the order of the whole visit: *"Wonder before
extraction. Encountering the astonishing living world leads, with exploration worthwhile beyond fuel collection and
discoveries that can reward curiosity rather than immediate production."* And for the beach: *"A dangerous place
worth exploring: refuelling is one reason among several to visit, alongside wildlife, strange resources and
discoveries."*

The crew are Jawa: small, hooded, built for dry heat and for trading scrap along desert roads. They have come to
the coldest liquid on the planet, in a stolen ship, to steal fuel from a sea. Everything they know about fuel says
do not bring fire near it. Down here the joke runs the other way: they cannot get a fire to light.

## The clock under the Chill

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid, then scouts with a spotter, a strike team, an ion cordon on the ship, a breaching
assault, and an orbital bombardment that cannot be fought. The arithmetic is taken from "The clock on any stop" in
`design/concepts/Greentide/design.md` and is not re-derived here: on open ground a probe on day 5 to 8, a first
real fight around day 12 to 20, the bombardment around day 20 to 32; one visibility band quieter stretches every
wait by about four tenths, and the top level of cover (the Abyss's Dark and the sea floors) makes every wait four
times longer: a probe around day 20 to 32.

**The outer edge of a stay: months on the floor, about a month on the beach.** On the floor the search is four
times slower and still comes (`Answered on 2026-11-19` 2). By his word of 2026-11-18
the figure a design derives is *"the outer edge allowable"*, not the typical stay. Few crews will see either edge.
The Chill pushes a ship out by its own means long before: the power it costs to stay warm, the charge in the
suits, the food and water that came down in the hold.

**Cover from orbit.** His card of 2026-11-18: *"Canopy, steam and fog slow the search by one step; full dark still
pauses it."* "One step" is read as one visibility band, as in every other design of this rewrite. His later word
the same day: *"Going under the ocean is like the Dark... VERY concealed. But nowhere pauses it indefinitely."*

- *The floor: the top level.* The ship sits under a sea that is black from above, on the night side of the world.
  Under the ocean is the top level of cover, like the Abyss's Dark: every wait four times longer, and no pause
  (`Answered on 2026-11-19` 2). This sea still costs a ship its quiet: it must heat, and its heat is written on
  the sea. The owner's ruling: *"There
  should be bubbling animations surrounding the hot ship boiling the propane simply by being normal temperature."*
  The build item's line: *"The player's presence is visible as violence against the medium before they touch
  anything."* (`UNSETTLED`: whether a boil shroud on the floor can be seen from orbit. If it can, it takes cover away
  while it shows, like any light.)
- *The beach: none.* The sheet's hard ban 3 is *"No visibility penalty as the standing state"*, on the owner's
  ruling of an aurora-clear sky with *"no visibility blockage"*. His later word on the land (2026-10-19) is that it
  is *"totally dark except for the utterly beautiful and wildly active aurora"*, and he made the aurora perpetual.
  A place lit at every hour by the brightest sky on the planet is not dark, and a pumping operation is loud. A
  ship on the beach is in the open.

**The Chill is a late stop by cost, not by lock.** The crossing to the night side is itself an engineering price
(the sheet's R-H10: the ship must be excellently heated to survive it), and his ruling of 2026-09-07 names this
lake *"the one real source — and inaccessible until very late game: terminator shock passage, extreme-cold
safety"*, adding that by the time a crew can reach it, fuel scarcity *"SHOULD NOT be the driving limiter — the
player is getting ready to win."* Nothing here gates the landing. A cold-seized ship is the gate.

**`UNSETTLED`: how the Empire's ladder reaches a ship on a sea floor.** No source says, for any sea. Each of the
four sea designs asks it, and it is asked below with what the Chill adds. The sections here
assume only what is safe in every answer: the clock runs, the probe comes, and the bombardment at the end does not
care about fuel.

---

## The first minutes

**On the floor.** His ruling of 2026-09-02, which is the origin of this whole sea: *"a wild underwater adventure
WITHIN a propane lake... and the ship must carefully lower itself into FUEL rather than water this time."* The
descent is priced in fuel by depth, both ways (built: `Patch_SeabedDescentFuel`).

The ship settles onto sparkling ice bedrock, the owner's *"solid ice sparkling with strange interaction with
hydrocarbon life"*. Before the ramp is down the sea around the hull is boiling: a shroud of bubbles on every cell
of liquid that touches warm plate, because the ship is the hottest thing to arrive here in ten thousand years.
The sheet: *"nothing hot has touched that lake since; a spacecraft's thruster is the first."*

Overhead the brightest sky on the planet comes down as *"dim shifting curtains... The floor breathes light."*
Below it, fixed points: the small blue-white flash of a fuselight, the edge of a ghostpane catching green. The
floor is never wholly black and never bright. Pale stepped drifts run off into the dusk, *"snowdrifts made of
molted armor"*: ten thousand years of plates shed by the rime-crabs. Somewhere out on the bedrock stands a black
horseshoe the size of a building, cut with busbars, humming.

The advisory comes with the landing (the campaign's shield mod sends one letter and never refuses a landing): this
is far past the cold at which the ship's own advisory speaks. Nobody goes out without a heated suit. Inside, somebody tries to light the stove.

**On the beach.** Black ice under a sky that never rests. *"It is cold enough here that propane falls as rain and
gathers in clear, still pools that will burn the instant anything hot reaches them."* (`RUT_Umbra`, description.)
The ship does not land at the water's edge; it cannot. His ruling of 2026-09-02: *"you have to run long flexible
pipes from your ship to the lake, because of your thrusters."* So the first minutes on the beach are a small crew
in mittens dragging hose across black ice toward a lake that is perfectly still, and something far out on the
mirror beginning to turn toward the noise.

## The first day

- **The suit is the clock.** One gauge, by his card (the two-clock version and the no-clock version were
  declined): a battery. Full charge, a crew member works outside. Empty, hypothermia comes fast, and *"the walk
  back to the airlock is the horror beat, not instant death."* The suit charges aboard, out of the same power the
  ship is heating with. Unsuited outside is immediate, severe cold.
- **Nothing burns.** Campfires fizzle, chemfuel will not light, incendiaries *"splash inert"*, torches die. *"Heat
  is electric only."* This is true inside the hull as well as outside it: the rule covers the whole floor map, every
  cell that is not supplied with air (`RM_ChillFireGate`). Fire
  exists below *"only where someone pumps air down"*: an ordinary oxygen pump, powered, in a sealed and roofed
  room, makes that one room a place where a stove will light (built and validated: `CHILL_AIR_PUMP_1`). A crew of
  scavengers who want a hot meal at the bottom of a sea of fuel have to build a room for the fire.
- **The ship is losing heat as fast as it can make it.** *"There should be a MASSIVE cooling load on the ship down
  there requiring extensive ship heating."* (owner, typed, 2026-09-27.) Brutal and the same everywhere on the
  floor, by his card; no gentle shallows. *"An underpowered ship freezes room by room — a real, plannable fail
  state."*
- **The garden.** Nine crystal and wax plants of the flora pass and one hummer rehomed from the Greentide, sparse
  on purpose. Slackwax, a kelp of living paraffin that the scrapers' shacks are furnished with. Skyharp, strung
  for the aurora, lighting *"string by string as the sky runs through its registers."* Ghostpane, leaves of frozen
  gas that cannot wilt, only vanish. Tarspool, banded black to amber to violet, *"a chromatography column that is
  also an organism."* Pitchpearl, hung with glossy black beads. Stonewater, bone-white: *"a plant whose stone is
  water, in a sea whose water is fuel."* Stillbloom, which is mostly not there. Eldspar, a finger's width a
  decade, *"the oldest living structure anyone on Ash'karr can visit."* Fuselight, of which every scraper is told
  the same thing before a first dive: *"the pretty one is a grenade."*
- **The cast is small, sparse and none of it is a fish.** A visit meets a few animals drawn by weight, not one of
  each (the number is his to set on a live walk; three is the provisional). The fessu, a paper-thin crystal flake
  drifting edge-on. The krellik, a crab in frost plates regrown nightly. The oddu, a shell that never moves and
  holds a mild joy. The oovu, a bell riding high in the fuel. The heemin, *"visible only as distortion."* The
  oovanam, soot-dark, leaving a clean wake through pale dust. The zhiil, hand-long, black, thrashing. The iliss,
  a wire eel on the ground currents. The tarnn, a lattice that might be a plant. Every one of them can be caught
  on a line from the beach, and by his ruling of 2026-09-26 every catch is alive down here.
- **The ship paints a ring.** *"Warm bloom, both edges"* (his card, 2026-09-27). Around a heat plume the
  stillbloom and its kin flower in the outer ring while the innermost cells boil bare. *"A parked ship therefore
  wears a halo of bloom around a ring of harm: the prettiest thing a crew will see down here is the ring their own
  engines painted."*
- **Their own tracks.** Everything warm marks the ice. A walking crew member's melt-prints refreeze glossy; a
  parked warm machine leaves a polished shadow. By the end of the first day the crew's errands are written on the
  floor.

## The first week

- **The garden answers.** It has an immune system in two steps, and his answer of 2026-11-10 says what the first
  step is for: *"Stop disturbing it and withdraw. Electrical defence reveals that the delicate garden can protect
  itself and offers a useful opportunity to back off, abandoning work before further escalation."* Harvest past a
  point, kill floor life, or turn heat on it, and the wire eels come: *"literal electric arc-discharges through
  the conductive frost around the offender. Stinging, eerie, survivable."* Keep going and the second step wakes:
  *"things catalogued as scenery stand up and fight, several at once. Sized like a hard skirmish, NOT a raid — one
  genuinely frightening fight, then the stillness returns."* A prepared crew beats either step; that was ruled a
  requirement, not a hope.
- **The floor remembers the route.** His third answer: *"Return ready for resistance. Repeated exploitation and
  thermal traces make familiar disturbed routes more confrontational, a persistent consequence that can cost
  peaceful reuse after extraction."* The defence weights where it gathers along old warm trails, *"so a second
  visit finds the first visit waiting."* The floor stays generated between visits (his card, 2026-09-25), so this
  is true across stops and not only within one.
- **The procession.** A slow file of wax colonies each *"the size of a wagon"* crosses the floor eating what has
  settled. *"Now and then the file stops, and each colony sheds an exhausted filter sheet, dead and clean, that a
  crew can carry home before the file walks on. It does not fight and cannot be tamed. Kill one and its sheets
  spoil."* The built first pause comes about a day and a half into a file's walk, so a week's stop sees it. This
  is the floor's giant by his card of 2026-10-02, and it is the most Jawa thing in the sea: a herd of enormous
  strangers that leaves salvage behind it, and the only way to get the salvage is to trot after them.
- **The landmark.** The Return Comb: *"a vast horseshoe of ice-rock cut by black busbars — the exposed return
  junction of the unfinished planetary dynamo."* Scenery and lore only, by his card; the tracing puzzle was not
  taken. It is the one place on the floor a crew navigates by, and it is the sheet's *"the machine is under
  everything"* made into something that can be walked up to.
- **Fishing for fuel, at the beach.** *"The one sea on the planet where the catch is worth more burned than
  eaten."* Every catch is flammable and barely food. By his card of 2026-09-24 the catch as fuel is a mechanic:
  ten catches render to chemfuel at an ordinary refinery, *"a second fuel source beside the pipe."* The rare line
  brings up *"a sac of pooled fuel, frozen round the line."*
- **Pumping, at the beach.** The pipes are the fuel story (below, under fuel). The lake creature is the price.
- *0.2.0:* **the sky reaches the floor.** On a reconnection night *"every Iliss lights up, the Skyharps sing loud,
  and arcs walk across the conductive frost."* A collector mast turns the surge into power, *"free watts against
  the brutal cooling load"*; suited crew caught outside take shocks. *"The storm is harvest or hide, never
  neutral."*

## The ship while it sits here

Three things every biome design now states, by his rulings of 2026-11-18.

**Cover from orbit:** the top level on the floor, none on the beach (above).

**Wear on the hull: cold, and the sources already say how.** His ruling: *"Yes in 0.1.0. It's easy, and most of
the biome already talk about this... Heat or cold. Different kinds of shields or armor. It's in there."* For the
Chill it is in there twice, once in the sea's own build and once in the campaign's shield mod, and no new hull
system is designed here.

- *What the sea does.* The floor is one cold everywhere, far below anything on the surface, and the liquid takes
  heat out of the hull hard enough that heating is *"THE logistics of every visit."* A ship that cannot keep up
  loses rooms: this is ordinary room temperature doing ordinary things, and the crew ends up in whichever room
  still has a working heater.
- *What the frame does.* `src/RimUtinni/ShipShields/` (built from his shield rulings of 2026-09-02) already knows
  this hazard: its cold test is an outdoor temperature at or below forty below, and its own comment reads *"gates
  the nightside and the propane sea"*. While a ship sits in that cold without the matching field, the exposure
  tracker wears the ship's own structures, at a flat strength that comes round twice as often after a long
  unshielded spell, with a second, harsher advisory. It never blocks a landing or a launch. His ruling: the hull
  *"is thick and can take a lot of damage in most situations, so no environment is immediately lethal"*, and the
  ship *"will advise course of action, but no more than that."* (`UNMEASURED`: that the tracker reads the floor's
  temperature on a seabed-layer map as it does on a surface map. The beach, on land at about fifty to eighty
  below, is its plain built case.)
- *What answers it.* The cold field, in his words of 2026-09-02: *"The opposite of the thermal rejection shield:
  thermal absorptivity. Pulls in heat in both directions and allows the shields to start glowing with red-orange
  black body radiation, holding severe cold at bay. But slowly decreases the temperature within the ship... still
  better than the extreme cold of the night-side atmosphere."* It is built as one mode of the one shield
  generator (the glow is not drawn yet). It is an answer with a bill: the ship still cools, only slower. The rest
  of the answer is power, closed doors, cold outer compartments and one warm room; and, from 0.2.0, the aurora
  collector.
- *What no shield does.* *"Slow pressing things move through all shields... This is why nothing 'holds out
  water,' it just doesn't work that way."* The fuel is against the plate whatever field is up. The field holds
  the cold off; it does not hold the sea off.
- *The approach.* The sources name two costs on the way in and no third: the crossing to the night side, which
  wants a well-heated ship, and the descent, priced in fuel by depth. No source says the lowering shakes or
  strikes the hull, and this design does not add it.
- *It never traps.* Launching always ends it.
- `UNSETTLED`, and worth his eye because it is funny: on the beach, the answer to the cold is a shield that glows
  like a coal, beside a lake whose rule is that it burns only when something hot reaches it. No source says
  whether a glowing cold field counts as hot. This design assumes it does not, and writes nothing that depends
  on it.

**Fuel: replete.** His word of 2026-11-18 names this place: *"One or two are REPLETE with fuel (the frozen Chill
beach for example)."* The sources agree from every side.

- *The pipe.* The sheet: *"Fuel by the pipe-length — a single vast deposit, refueled in place (ruled), priced
  entirely in cold survival."* Refuelling is by long flexible pipes from the grounded ship; tanker runs were cut
  on 2026-09-02. Pipes, pumps, valves, rupture and the lake creature's answer to pumping are built in the campaign
  layer. A lake joined to a cut is an endless source on its own map (`flowworks_liquid_matrix.md`).
- *The price.* His three answers of 2026-11-10 for the shore are the three things a fuel stop here has to be.
  The stop itself: *"A dangerous place worth exploring."* The lake creature: *"Stop pumping and withdraw. Noticing
  its approach offers a useful withdrawal window for the crew, while exposed equipment and pipe remain at risk."*
  A gas emergency: *"People first, equipment uncertain. Evacuation remains practical; shutting the valve is
  dangerous work, and parts of the operation may have to be abandoned."*
- *The rain.* On the land beside the lake it rains propane, *"equivalent with chemfuel"* (owner, 2026-10-19), and
  the rain pools.
- *The line.* Catch rendered to fuel, and fuel in the rare catch, as above.
- *The garden, last.* Fuel from the floor's plants was first forbidden and then allowed in his own words: *"it's
  ok to harvest them for fuel. This is very late gme."* *"Just have it result at the harvest bench (hydrocarbon
  flesh) that can then be converted at the refinery."* It stays where he put it, with a crew that stays.
- *Buying and selling.* Nobody sells fuel here because nobody needs to. The people of this shore are in the
  descriptions only: *"scrapers"* who furnish shacks with set wax, fish the lake for the oddu and *"carry them home
  in mittens to eat by the tap-wire, which is as close to a good evening as the nightside offers."* Who they are,
  and whether they trade, is `UNSETTLED`. The very Jawa thought, that a crew with full tanks should fill the hold
  with drums and sell fuel everywhere else, runs into a cut he made by name, and is under `NEEDS HIM`.
- *The joke.* The ship flies on fuel and is parked in a sea of it, and what will drive the crew out is power.
  Nothing down here can be burned to keep warm.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen. Numbers one to eleven are the floor; the rest are
the beach.

1. **The stove.** *On screen:* a hooded figure at the ship's cookfire, striking and striking. Nothing. A second
   figure arrives with a torch to help; it goes out in its hand. *Why it is funny:* they are surrounded by more
   fuel than exists anywhere else on the planet.
2. **The room for the fire.** *On screen:* a small sealed room, a pump thudding on its wall, and through the door
   the only flame for a thousand kilometres, with the whole crew packed in around it.
3. **The ship boils the sea.** *On screen:* the hull sitting in a collar of bubbles; and by the next day a ring of
   pale flowers round the ship, with a ring of bare scoured ice inside it. *Why it lands:* nobody did anything.
   The ship did it by being warm.
4. **The pretty one.** *On screen:* a crew member reaches for the only plant with a light on it, and it goes off
   in their hands. *"No one who harvests one does it twice."* It carries its own oxidiser; it is the one thing
   down here that does burn, and by the sheet's own line *"the only fire at the bottom of the world is a flower."*
5. **The gauge.** *On screen:* a suit's charge reading low at the far end of an errand, and a walk back that
   becomes a run. *Why it is alarming:* the ramp is in sight the whole way.
6. **One warm room.** *On screen:* frost creeping across the hold wall from the outside in, and the crew dragging
   bedrolls past dark compartments toward the one door with light under it.
7. **The arcs.** *On screen:* a crew member cutting one plant too many, and blue-white arcs walking toward them
   through the frost. They stop cutting. The arcs stop. *Why it lands:* the garden just said no, and meant it
   politely.
8. **The scenery stands up.** *On screen:* the crew did not stop. Three of the crystal lattices they have been
   walking past all week unfold and come for them.
9. **The trail.** *On screen:* yesterday's glossy footprints leading out from the ramp, and arcs already running
   along them before anyone has stepped outside.
10. **The procession.** *On screen:* a file of wagon-sized wax things crossing the camp without looking at it,
    and five small hooded figures trotting behind with their arms out. *Why it is funny:* it is the crew's whole
    trade, on foot, at the bottom of a sea.
11. **It was there a moment ago.** *On screen:* a pale flower, half crystallised out of clear liquid, and a crew
    member edging toward it. It un-happens. The scrapers' line: finding one blooming is *"the lake deciding whether
    you were quiet enough to deserve it."*
12. **The wake** (beach). *On screen:* hoses run across black ice, pumps thudding, and a V of parted fuel coming
    over the mirror toward the hose. His ruling: *"it should be seen moving around the lake as a submerged V-shaped
    wake trailing around, just to add suspense... the loud pumping agitates them."* The crew kills the pump and
    runs; the pipe is what gets bitten.
13. **Nobody shoot** (beach). *On screen:* a haze over the pumping site, a letter, and every weapon on the map
    lowered at once. His framing: gas *"making weapons fire too dangerous to entertain."* *Why it is alarming:*
    the valve is over there, inside the haze.
14. **Pull the line and leave** (beach). *On screen:* a line comes up with something hand-long, black and
    thrashing on it. The description: *"Scrapers who have fished up a zhiil pull the line and leave, because the
    parent is a thing that attacks pipe on sight and has a fairly clear idea of where its young went."*
15. *(0.2.0)* **Harvest or hide.** *On screen:* the whole floor lighting up, every wire eel aglow, the harps
    singing, arcs crossing the frost, and the crew split between the ones running for the ramp and the ones
    running for the collector.

## When the Empire arrives

How the ladder reaches a floor is `UNSETTLED` (above). What this sea does to anyone who comes, whoever they are:

- **It freezes them.** The campaign's own note on an Imperial garrison posted beside this lake says its men *"would
  freeze in hours"* without cold kit given to them as equipment
  (`design/Jawa/worldbuilding/warlab_garrison_early_blast_2026-11-01.md` §4). Troopers on the beach or the floor
  are on the same clock as the crew, without the crew's ship to go back into.
- **On the floor, nothing they bring will burn.** No incendiary, no flame weapon, no fire to warm a siege camp.
- **On the beach, their own rifles are the hazard.** Where pumping or a rupture has put gas over the map, ranged
  fire risks a fireball at the shooter. The ruled answer for raiders who mean to fight in gas is the owner's:
  *"Give them better weapons... Strictly non-flammable, non-temperature-based, non explosives. Vibro-weaponry."*
  The Empire arrives with blasters.
- **The garden does not ask whose heat it is.** Warm troopers leave trails; a firefight in the garden is directed
  harm. The arcs and the waking lattices answer whoever earned them.
- **The lake creature does not ask either.** It goes for what moves near the fuel.

The sheet has its own, larger ending for the Empire at this lake, and it is not part of an ordinary stop: if the
Empire ever learns what is under the lake, *"they bomb their way into it and then get overrun"* (owner, typed,
2026-09-27). That is lit by plot events, never by a landing, and by his card of 2026-11-02 blowing the lake does
not light it either. It belongs to the campaign layer.

## Who else attacks; who hates the Empire

- **The garden,** when harmed (0.1.0).
- **The lake creature,** at the beach, when the pumps run. *"Not guaranteed, but often... NOT the reason the
  propane lake is there, they just dwell within it."* Its home in today's build is `UNSETTLED`: it was taken off
  the floor's cast on 2026-10-02 to wait for a shore home, and the shore's own sitting has not been held.
- **A raid in the gas** (0.2.0, campaign layer; built as an incident): raiders who come when the air is thick,
  armed with sonic weapons, javelins and vibro-blades, because they know nobody can shoot back.
- **The guardian of one place** (0.2.0): the Burner in its polar form, *"always in flame when moving... the most
  beautiful killer on the ice"*, ruled by card on 2026-09-27 as *"a set-piece encounter you go to, not one that
  comes to you."* The place has not been picked.
- **Nothing native follows the ship.** *"Nothing native survives the crossing dayside."*
- **Who hates the Empire here:** nobody lives here to hate anyone. What is under the lake hates everything, and
  the Rust Cathedral and the Helix each want it for their own reasons; all of that is the campaign's.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- Power. Heating, suit charging and any fire room all draw on it, and nothing below can be burned instead.
- Rooms lost to the cold faster than the crew can win them back.
- Food and water. The natives are not food; the catch is *"edible only barely and only cooked"*; the only water on
  the floor is ice in a plant's bones.
- A garden that has learned the crew's routes.
- On the beach: the lake creature, a gas emergency, the cold, and the open sky.

**Stay, longer than the Empire would like:**
- The cold field, and one warm room run with discipline.
- A fire room.
- A light hand in the garden. By his answers, stopping is always allowed and always works.
- The sea itself over the ship: the top level of cover from orbit.
- *0.2.0:* a collector mast on a surge night.

## What the crew takes away

- **Full tanks.** That is what the stop is for, and the only place on the planet where the tank fills from a hose.
- **Fuel by the basket:** catch rendered at a refinery, and the frozen sacs off the rare line.
- **Dead filter sheets** from behind the procession: *"inert and clean... a refinery input that crews haul back
  from the file's pauses."*
- **Cut wax,** the sea's only timber, which is supple below and sets hard in air *"holding whatever curve it
  drowned in."*
- **The mild joy:** the oddu, and the violet crown scraped off a tarspool, ruled the same stuff as the rime
  nodule's.
- **One flawless spar,** and in its smoke-grey heart *"the planet's prettiest treasure"*, at a price the
  description states plainly: the garden it came from was centuries old. (The treasure is still a campaign-tier
  item hung on a free-tier plant; the cleanse ticketed that and the ticket stands.)
- **Pitch pearls,** as poor oily animal feed.
- **Salvage.** By the standing wreckage ruling every sea floor carries wrecks densely. The sheet adds what is
  particular to this one: the dead of the Blue Desert arrive here, and nothing that sinks in an airless, frozen,
  lightless sea ever spoils.
- **Nothing alive.** *"Slackwax sets, ghostpane sublimes, stillbloom dissolves, fuselight detonates — the roster
  enforces untransportability by chemistry."*
- **Knowledge of what is under the hill of the oldest garden.** Campaign layer.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The ship lands on the Chill's own floor (ice bedrock, fuel pools, crust, rime drifts, the black horseshoe, a drowned aurora over points of light) and can leave again. | A landing and a launch. | A generic empty floor fails. So does a floor reached any way but the ship. |
| The floor's light rises and falls with the aurora above and is never wholly dark. | The same floor under a bright sky and a quiet one. | With the glowing plants removed and the sky quiet, the floor is darker than with them. |
| Outside the hull an unsuited crew member is in severe cold at once; a charged heated suit keeps one working; an empty one starts fast hypothermia with time to walk back. | Three crew at the ramp: unsuited, charged, nearly flat. | A native animal beside them is unharmed. The gauge is the only clock. |
| Nothing flammable lights anywhere on the floor map, inside the ship included; in a sealed, roofed room with a powered oxygen pump, it does. | A stove in the hold; the same stove in a pumped room; the pump switched off. | The same stove on any other map lights. An unroofed or leaking room stays dead and says so. |
| The one plant with a light on it explodes when harvested, on a map where nothing else burns. | A harvest order on a fuselight; a torch held beside it first. | The torch stays dead and the plant still goes off. |
| A parked ship boils the liquid against its hull, and plants flower in a ring round its heat with bare ground inside the ring. | A ship parked for days; the same ground before it came. | A cold, unpowered hulk grows no ring. |
| A ship that cannot heat itself loses rooms to the cold, and can always launch. | A ship on full power and on half. | The same ship on the Twilight floor loses none. |
| While the ship sits in this cold without the cold field, its own structures wear and an advisory says why; with the field up the wear stops and the inside still cools, slowly. | The same ship with the field off, then on. | The wear follows the field, not a timer. A launch is never refused. |
| Harming the garden brings arcs at the one doing the harm, first; stopping and backing off ends it. | A crew member harvesting past the garden's patience, then standing down. | A crew member standing idle in the same spot draws nothing. |
| Carrying on brings a hard fight with things that were scenery, sized for a prepared crew to win, and then quiet again. | The same crew member not standing down. | It is one fight. It does not grow into a raid and it does not repeat by itself. |
| Warm things leave visible trails on the ice, and the garden's answer comes sooner along a trail already used. | The same errand walked twice on the same line, and once on fresh ice. | Save and reload between the two walks: the trail and its effect are still there. |
| A file of giant wax colonies crosses the floor, pauses, and sheds sheets a crew can carry off; killing one spoils its sheets. | A file followed through one pause; one colony shot. | The file never fights and cannot be tamed. |
| Every kind of catch on the beach's line is alive on the floor. | Fish the beach; find the same kinds below. | |
| The catch renders to fuel, and the rare line can bring fuel up directly. | A refinery bill on a basket of catch. | The catch is poor food, and raw it can sicken. |
| At the beach the ship fuels from the lake through pipes laid from a standoff, and never by parking at the edge. | A pipe run, a pump, a tank filling. | With the valve shut nothing flows. |
| Pumping draws the lake creature, with warning enough to stop and get people clear; the pipe may be lost. | A pump left running and a pump stopped at the first sign of the wake. | A silent pump on the same lake draws nothing. |
| A gas emergency can always be walked away from; shutting the valve is the dangerous choice. | A rupture with a crew near it: one group leaves, one goes for the valve. | Nobody is ever sealed in gas. A shot fired in thick gas is what makes the fireball; the lake does not light by itself. |
| On the floor the Empire's search comes at the top level of cover, much slower than for the same crew on the open beach, and it still comes. | The same crew, as loud, on the floor and on the beach; read the search's next contact on both. | A search that never comes on the floor. |
| Nothing vanishes. | Every loss above, with a save and reload in the middle. | |

No row pins a rate, a temperature, a charge time, a wattage or a count: those are tuning and stay out of any bar.

Settings: a switch per major feature, defaults as shipped; everything off leaves a cold floor with ordinary life
on it (standing rule, every mod).

## Shared machinery

**Featured here** (the Chill is where each is vital and should be proven):
- **Cold on a parked hull, and the cold field.** The shared hull-wear frame's cold case
  (`ShieldHazardUtility.HasColdHazard`, `CompShieldCryoEnvelope`). Other night-side designs lean on the same code;
  this is the stop where a ship sits in it longest and deepest.
- **A place with no fire** (`RM_ChillFireGate`, `Patch_ChillFireBan`), **and air as the thing that brings fire
  back** (`RM_MapComponent_ChillOxygenation`, on the base game's own oxygen pump). The shared-machinery file's
  "wind on fire" is active everywhere fire is; this is the one map where fire is not.
- **You were noticed** (`RM_MapComponent_ChillGardenDefense`, `RM_GardenDefenseKernel`,
  `RM_MapComponent_ChillFootprints`). The shared file lists this idea in the Lantern Deeps, the Rust Cathedral and
  the Webwork and finds no shared engine. The Chill's is the version with a warning the player can obey.
- **A suit on a charge** (`RM_CompHeatedSuitBattery`, the charger, the danger-clock alerts).
- **Fuel as terrain and fuel by pipe** (`FlowWorks`' propane suite; `PropaneLakeMechanics`' pipe net, pump, valve
  and rupture; the gas-saturation tracker).
- **A herd that leaves a harvest behind it** (`RM_Comp_WaxProcession`).
- **Catch with a living counterpart**, featured in every sea.

**Merely active here:** the ship as the only door (the seabed layer, featured across the four seas together);
fuel priced by depth; wreck salvage; light as a resource (the drowned aurora and the plants' points of light; no
one farms by it here); ordinary creature behaviour; the Empire's search and the visibility dial; the one sun from
geometry, which on the night side and on a sea floor is nothing.

**Three ship systems built once for every biome, and what the Chill asks of each:**
- *Hull wear.* Nothing new. The frame's cold case and cold field are built; what is owed is proof that they read
  a seabed-layer floor, and the field's glow.
- *Cover from orbit.* One entry for the floor at the top level, beside the Abyss's Dark.
- *Fuel.* The pipes are built. The Chill needs no recipe to be replete; it has two anyway (catch, and the late
  plant chain).

## Scope

Every feature is in one bucket.

**0.1.0, the stop**
- The floor as a place on the ship's layer: ice bedrock, fuel pools ringed with standable crust, rime terraces,
  the Return Comb, the drowned aurora over the plants' own light. (built; the layer's flight and the frozen twin's
  floors unproven)
- The cold: one brutal temperature, the heated suit on one charge, the ship's cooling load and boil shroud,
  natives comfortable far below it. (built)
- No fire, the pumped fire room, and the fuselight's real explosion. (built; the explosion moved in)
- The garden: the plants and the animals at sparse draws; warm bloom round the ship; warmth trails; the arcs that
  warn; the lattices that wake. (built; the defence moved in on his answers of 2026-11-10)
- The wax procession and its sheets. (built; moved in)
- The hull: cold wear on the ship's structures and the cold field that answers it. (built in the campaign's shield
  mod; unproven on a floor)
- The top level of cover from orbit on the floor. (unbuilt; one entry in the pursuit)
- The beach as a fuel stop: fishing with every catch alive below; catch rendered to fuel; pipes, pump and valve
  from a standoff; the lake creature drawn by pumping, with a window to withdraw; a gas emergency that can be
  walked away from. (built, campaign layer for the pipework; the creature's home unsettled)

**0.2.0, the stop with company**
- Aurora surge storms and the collector mast. (built)
- The raid in the gas; gas vents on the beach. (built, campaign layer)
- The polar Burner at its one place. (creature built; place unpicked)
- The lake creature at the scale its sheet promises, and a sea giant big enough for the titan passage. (open
  items; his call at the shore's sitting)
- The lakebed set he seeded on 2026-09-10, if he still wants it: the bottlearm, the lakestar and its crown, the
  bead fields and the pale spire. (unbuilt; the stinger and the lakestar pair come into 0.2.0, `Answered on 2026-11-19` 4)
- The crust-sitter that flinches from warmth, from the watchers pitch. (a pitch; admitted or cut at the sitting)

**Later (a crew that stays, or a colony)**
- Growing the floor's plants: the enclosed cryoponics vat and the floor-only bed. (built)
- The floor's industry: hydrocarbon flesh to fuel (*"very late game"*), tarspool fractions, the powered stonewater
  extractor. (built)
- The electrojet tap, the cold-native leather, the wire-loop ruins of earlier taps. (land; unbuilt)
- The ending: the war lab, the six routes to its door, the crater that changes the map, the garrison, the
  specimens. (campaign layer; parts built)
- A Deepwater claim on the floor's ice; shafts and caissons on the beach. (campaign layer)

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Diving or returning as a single pawn; the dive hatch; any place "on the surface" of the lake.
- Tanker runs (cut 2026-09-02); the tar and propane dual-hazard map (cut 2026-09-02: *"too much, no need"*).
- The lake lighting by accident, and any fire on the floor's own account (the fire ruling of 2026-09-27 replaced
  the floor-ignition weather of the 2026-09-25 dive spec).
- A two-clock suit, a suit with no clock, and a floor with gentler shallows (declined by card 2026-09-27).
- The ulkhoss (*"Drop the ulkhoss, don't need it."*, 2026-10-06). Keelgrass (*"cut no longer needed"*, 2026-10-06).
- A second biome for the lake's shelf (*"No... No change. Just confusing words."*, 2026-09-25).
- Kyber in the crystals. An eldspar that never regrows. A fishing-thins-the-wakes loop (flavour only by card).
- The Return Comb's puzzle; the three ideas not chosen on 2026-10-02 (taking cartridges apart in solvent; a cold
  hold aboard for knowledge that deforms when warm; a rite of washing a grudge away).
- The menu siblings not adopted on 2026-09-27: krellik-frost insulation, ice coring, thaw temptation; clear-ice
  windows, breath pillars, living stained glass; melt-settle, fogging the windows, supercool pools.
- Every icy version of a dayside animal; the donor fliers on the floor.
- **Recommended for dropping, not yet his:** the inert cross-biome switches (the cleanse's recommendation, kept).

## NEEDS HIM

5. **Ship ideas he has already cut or passed over here.** Listed, not revived. *Tanker runs*, cut 2026-09-02:
   *"You're not extra flammable on the way home, just right next to that explosive lake... and you have to run
   long flexible pipes from your ship to the lake, because of your thrusters."* The cut was of hauling as the
   fuel mechanic; whether a crew may still load drums of ordinary fuel to sell elsewhere is the very Jawa
   question it leaves. *A cold hold aboard* for cargo that must stay frozen, not chosen 2026-10-02 (no words
   recorded). *Krellik-frost insulation* for the hull, not adopted 2026-09-27 (no words recorded). Default for
   all three: they stay out.
   *Waits on the declined-ship-ideas question of 2026-11-19.*

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. **What does the Empire do about a ship at the bottom of this sea, and what does a bombardment do beside it?** The
   probe and the bombardment follow the ship down. The troops wait at the beach and meet it when it lifts. This needs
   the fewest new things and is the same in all four seas (the design's default). An ordinary bombardment never lights
   the lake (his card of 2026-11-02). *Delegated call.*
2. **Is the Chill's floor "full dark"?** *His ruling:* his word of 2026-11-18 (4:09 PM PST): *"Going under the ocean
   is like the Dark... VERY concealed. But nowhere pauses it indefinitely."* The Chill's floor is the top level of
   cover, like the Abyss's Dark. **This changes the design's default.** Was: *One step, like the other floors*.
3. **What is the beach, exactly?** The beach is the land beside the lake, with its own pools and crust. The lake
   creature lives in the lake, seen from the beach. It rains propane (his word of 2026-10-19). These are the design's
   defaults. *Delegated call.*
4. **Does the lakebed he seeded on 2026-09-10 still stand?** Yes: the stinger and the lakestar pair come into 0.2.0
   beside the present cast (the design's default). *Delegated call.*
6. **Where does the polar Burner stand?** The Conductor picks the place in the shore's design. *Delegated call.*
