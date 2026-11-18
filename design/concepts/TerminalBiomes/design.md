# The four seas: the design, seen from the ship

**Status:** the one design document for the mod `src/RimMandrake/TerminalBiomes/`, which carries four sea biomes:
the Scald (`RM_TheScald`), the Grey Sea (`RM_GreySea`), the Twilight Sea (`RM_TwilightSea`) and the Chill
(`RM_TheChill`; older files call it the Propane Lake). Rewritten 2026-11-18 on the owner's instruction to see every
biome "through the lens of Utinni". It replaces the older definition sheets, content drops, floor passes, agendas and
the cleanse proposal as the place to read; what happened to every idea in them is in
`design/concepts/TerminalBiomes/rewrite_choices.md`. Nothing has been deleted yet. This is a design document only
and it launches nothing.

**Kind, checked against the sheets' own headers:** all four are seas. So two rulings shape every section below.
*"You can't 'dive' as an individual pawn nor return as one. It's ship or nothing."* (owner, 2026-09-26.) And *"You
are either on their sea floor, or you are on their beach. There is no 'on their surface' location."* (owner,
2026-11-01.) The ship flies to the floor as its own planet layer, lands there, and is the only way back.

**Who reads this next:** a Designer run on this concept is handed the list of files in
`design/concepts/TerminalBiomes/` (`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in
its path by sitting here. Nothing in the pipeline reads it by name yet. The mod has no locked sheet or tree; its only
pipeline material is the cleanse proposal of 2026-11-17, which this design supersedes and which was never applied.

**One dependency under everything.** On 2026-10-02 a measured read found that a ship flying to a sea floor landed on
*"an empty generic floor"*: the cast, plants and mechanics lived on a retired hatch map, and the per-sea floors of
the new layer were unbuilt. Whether that is still so is `UNMEASURED` here (the cleanse marks the floor adapters
"unknown"). Every promise below reaches a player only when each sea's floor is a real place on the layer the ship
flies to.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What these places are

> *"Visit alien sea floors by gravship: the Scald boils, the Grey grows salt, the Chill holds dark fuel, and the
> Twilight shelters gardens beneath living glass."* (cleanse proposal, 2026-11-17)

Four seas on one planet with nothing in common but the way in. The owner's line for each, from 2026-10-20:

- **The Scald:** *"The kettle at the centre of the world: every river starts here, boiling. Life here is cooked and
  proud of it."*
- **The Grey Sea:** *"It looks and smells like it's dying. Yet in the crusted remains bold new life remains and
  emerges older than what dies."*
- **The Twilight Sea:** *"A ceiling of cathedral living glass, where every creature is bedecked in reverent light.
  Shame most of them are so big, hungry, and quick."*
- **The Chill:** *"A frigid alien sea with unspeakable beauty and strangeness. All is fuel yet nothing burns."*

**Seen from the ship, these are the only stops where the base really is the ship and nothing else.** On land a crew
can walk away from the hull. Here the hull is the air. Everyone who goes out goes out in gear and comes back to the
same ramp. The cleanse proposal already wrote the stop as a visit: *"A sea visit has an arrival, a safe working
edge, temptation beyond it, a bad choice and a possible recovery."*

And the crew are Jawa: small, hooded desert scavengers who have never seen standing water deeper than a trough.
Nothing in their lives has prepared them for being at the bottom of any of this. *(`UNMEASURED`: what gear the floor
layer requires of a pawn in each sea; the cleanse says hull atmosphere and ordinary protective gear come from the
floor layer's own mod.)*

**The sea owes the ship something, and the owner said what.** On 2026-09-26 he typed: *"Yes. The grey sea should
crystallize the hull, freeze doors shut. twilight drops sky panes on the ship that need to be cleared off."* A
design pass put the principle in one line: *"Each sea claims a parked hull in its own register."* On 2026-11-18 he
ruled that every biome wears on the hull in 0.1.0. For the seas that work was already designed and mostly built;
this design moves it into 0.1.0.

## The clock under a sea

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought.

**The outer edge of a stay on any of the four floors: about six weeks. On a beach in the open: about a month.** By
the owner's word of 2026-11-18 the figure a design derives is *"the outer edge allowable"*, not the typical stay.
If the Empire wins every step, the bombardment is the fourth full interval of the ladder: 20 to 32 days at the
ordinary pace and 28 to 45 days one step quieter. In practice each sea pushes the crew out sooner by its own means,
which are below.

**Cover from orbit: a sea floor is covered ground, one step.** His ruling of 2026-11-18: *"Canopy, steam and fog
slow the search by one step; full dark still pauses it."*
- *The Scald's floor* is under a boiling sea and a permanent steam sky. *Its beach* is under the same steam. One
  step, both.
- *The Grey's floor* is under *"grey-green murk a few meters deep to the eye"*. One step. *Its beach* is an open
  salt pan in a wind that never stops. None.
- *The Twilight's floor* is under the waveglass, one living lid shore to shore. One step. *Its beach:* none.
- *The Chill's floor* is under a black sea of fuel on the night side of the world. One step by default; whether it
  is the "full dark" that pauses the search is under `NEEDS HIM`. *Its beach* is the opposite: the sheet rules the
  sky *"aurora-clear"* with *"no visibility blockage"*. None.

**`UNSETTLED`: how the Empire's ladder reaches a ship on a sea floor.** No source says. A probe droid can go
anywhere a droid can go. What a scout team, a siege camp or a breaching assault does at the bottom of a boiling sea
is not written anywhere, and this design does not make it up; it is the first question under `NEEDS HIM`. The
sections below assume only what is safe in every answer: the search clock runs, the probe comes, and the
bombardment at the end does not care about water.

---

## The Scald

> *"A crater sea that boils... a roiling, steaming, mineral-fouled expanse ringed by geysered shores... A place of
> roiling wonder."* (`the_scald.md` §1)

**The first minutes.** The ship drops through white steam into cyan light. *"The water burns to touch and comforts
as it burns."* On the floor the boil *"gentles to mere heat"*: hot mineral ground to walk on, and around each vent a
pool of the real thing, which scalds. The landing leaves a pool-free way from the ramp to working ground. Bubble
lines climb from the vents, and things are riding them.

**The first day and week.**
- *The pasture.* Rainbow mats of ancient growth coat everything, *"oddly fuzzy"*, banded by heat. Armoured
  bottom-walkers mow them in herds, slow and pastoral. *"Their feces are the food"*: silver shoals work the fall.
- *The sailors.* The saal, a translucent bell heeled over on a line of bubbles, *"like little solar sails"*,
  tacking up the vent columns and drifting down to ride again. *"The biome's signature silhouette and kindest
  resident."*
- *The rest.* A crab that *"looks like a piece of the vent walked off"*; a golden gas-sac that gulps itself taut in
  the roar; an eel living under the mats in the mats' colours; and, one to a sea if that, the elder sando.
- *The water is never drink.* *"Fouled, not toxic."* No tool in any version makes the body of it potable.

**"OMG did you see that?"**
1. *On screen:* a Jawa wades into a vent pool after something shiny, comes out scalded, and has the bathing
   thought on its face anyway. The water *"hurts nicely"*.
2. *On screen:* a flotilla of saal comes tacking through the camp on the bubble lines and the crew stops work to
   watch them go by.
3. *On screen:* the ground beside the salvage party gets up. It was a bottom-walker's back.
4. *On screen:* the ship's inner doors standing open and the crew sleeping in the corridor, because the bunk rooms
   are too hot to enter.

**The hull.** By his card of 2026-10-02, the Immersion Berth: *"a parked ship's rooms slowly heat; doors never
seal, launch never blocked."* The answer is cooling, and leaving. (`UNMEASURED`: whether this is built; it is not a
row in the cleanse census.)

**Fuel.** The emergency route only: mats and carcasses rendered slowly. Nothing here burns or pools.

**What the crew takes away.** The catch; rainbow pigment from the mats; walker plate; wrecks *"cooked clean"*. From
the beach in 0.2.0, the one thing the dayside pays anything for: clean water off the steam.

## The Grey Sea

> *"Pillars in grey murk, a lake with shores at the bottom of a sea, and the dead standing in crystal where they
> sank."* (`the_grey_deep.md`, header)

**The first minutes.** The ship settles into murk. Sight is short. Around it stands *"a wonderland of odd pillars
and formations"*: salt domes like mushrooms, chimneys *"shooting out murky white super-brine"*, great crystals. Salt
falls through the water like snow. In the hollows lie pools of heavier brine with their own surfaces and their own
shores, underwater. *"Everything that enters dies; everything that dies there keeps."*

**The first day and week.**
- *The statuary.* *"Old ruined vehicles and skeletons stand encased in mineral where they sank."* Salvage here is
  chiselled out.
- *The pools.* Touch one and the same thing happens to the toucher. An encased crew member is cut free by others
  like any other exhibit.
- *The crystal garden.* Green tissue living inside salt it has grown into cubic armour: pink, violet, amber,
  *"marred and never perfect."* Small pickers, clams and mussels work what rains down.
- *The watcher.* The fessk, *"a man-sized, skeletal-seeming shrimp... strangely intelligent and nimble, but shy and
  evasive"*, which *"has watched every diver who ever came down here from two pillars away."*
- *The giant.* One crusted, ill-tempered thing, *"indistinguishable from a drifting pillar until it moves."* *"Fresh
  scrape-sign means the giant is near."*
- *The line brings up little.* Thirteen kinds of catch, all rare by his ruling: *"the murk hides plenty, but most
  days the line brings up little."*

**"OMG did you see that?"**
1. *On screen:* a crew member reaching into a brine pool for a perfectly kept droid, and standing there in crystal a
   moment later, arm still out.
2. *On screen:* the ramp door, rimed white overnight, not opening; a Jawa on the inside leaning on it; two on the
   outside with chisels, pocketing the salt.
3. *On screen:* one point of colour in the grey, getting larger. The sheet: *"you see the mate-mark's glow before
   you see anything else."*
4. *(0.2.0)* *On screen:* at the edge of the work lamps, a tall pale shape that was not there before, not moving,
   watching. It never comes in.

**The hull.** His words: *"The grey sea should crystallize the hull, freeze doors shut."* Built. Rime first,
*"the warning is the beauty"*; then doors, which salt shut from the outside and by his card *"always force open from
the inside"*: *"Never a tomb."* Parking near a chimney or a brine channel is faster. The answers are chipping and
leaving; by his card interior heat does nothing to it. *"The sea pays you"*: chipped crust is salt crystal.

**Fuel.** The emergency route only. Nothing in any Grey source burns.

**What the crew takes away.** Salt crystal, including what came off the hull; mineral-kept salvage; the rare
catch; ordinary harvest from the crystal flora. In 0.2.0, whatever a Brine Elder gave for something it had never
tasted.

## The Twilight Sea

> *"Golden light-wells in dim green water, kelp towers, crowds."* (`the_twilight_deep.md`, header)

**The first minutes.** The ship comes down under the waveglass: *"a living stained-glass ceiling — translucent
blue-green, veined gold."* Where it has holes, amber light *"stands in visible golden columns in green water"*, and
kelp towers reach up into each one. Silver shoals turn in the light. Something vast and unhurried is grazing the
ceiling. After every other stop on the planet, *"the sound of company."*

**The first day and week.**
- *The rivers that look dry.* Mud-bedded channels along the bottom *"where heavier water flows invisibly."* *"Their
  banks are the richest ground in the sea."* *"No swimmable river"*: *"entering a bottom channel means sinking with
  it."* Stakes mark the reach. A worker who goes past them is carried down the channel to a sink, stays findable,
  and has to be fetched out into the hull.
- *The undersurge.* The current floods with a warning, the reach widens, and the crew pulls back past the stakes.
- *The wells move.* A light-well wanes and closes inside the visit and another opens somewhere else. *"No skylight
  permanence."* The garden under a closed well is on borrowed time.
- *The gardener.* The endemic giant, *"placid where the Grey's is cross"*, grazes the lid's underside and patches
  its tears. *"Killing the last gardener kills the roof, and the roof is the biome."* In this version it cannot be
  harmed.
- *The only ordinary fishing on the planet.* Nets in the light columns. It works like fishing.
- *One true predator,* *"fast and almost nostalgically ordinary, hunting the shoals in the dark between columns."*

**"OMG did you see that?"**
1. *On screen:* a Jawa steps off the bank into what looks like a dry gully to pick something up, and slides away
   down it, upright, faster than anyone can run. A letter says where the gully ends.
2. *On screen:* a shadow the shape of a windowpane grows on the deck for a few seconds; the crew scatters; a slab
   of the sky lands where they were. By his card the pane *"can kill outright"* and the shadow is the fairness.
3. *On screen:* the whole floor dims as the gardener passes overhead, and brightens again behind it.
4. *On screen:* the gold column the crew set up under goes thin, then out, and a new one stands a long way off
   across a river.
5. *(0.2.0)* *On screen:* a warm gold glow in the dark between two wells, where no well is. It is not a well. The
   vaulisk; one to a map at most, and its tell can always be read.

**The hull.** His words: *"twilight drops sky panes on the ship that need to be cleared off."* Built: falling
panes, flakes settling on the deck, and a launch that waits until the deck is cleared. Never a trap; a chore with a
deadline.

**Fuel.** The emergency route, with more to render than anywhere else: this is the one sea with real plant matter
by the tower. No source makes it a rich one.

**What the crew takes away.** Fish, in quantity; kelp for food, fibre and *"wet lattice-timber"*; bank forage;
shed pane.

## The Chill

> *"The far end of the world: a black sea of liquid fuel under the brightest sky on the planet."*
> (`the_propane_lakes.md` §1)

**The first minutes.** The ship is lowered into fuel. It is far colder than anything on the surface. A shroud of
boiling fuel flickers round the warm hull. Overhead the aurora shows drowned and dim; on the floor, points of living
light. Ice bedrock, rime terraces, pools of liquid propane ringed with crust. And nothing can burn: *"Total fire ban
on the floor (no oxygen)."*

**The first day and week.**
- *The suit is the clock.* A heated suit with one charge. Empty means freezing fast. Every errand is measured in
  it.
- *The ship freezes room by room* if it cannot keep up.
- *The garden.* Ten crystal plants: slackwax, skyharp, ghostpane, pitchpearl, keelgrass, tarspool, stonewater,
  stillbloom, fuselight, eldspar. They grow from what falls.
- *The cast.* Small, sparse, strange; every catch has a living body on the floor.
- *The first hot thing in ten thousand years.* The sheet: nothing hot has touched this lake *"since the war"*, and
  *"a spacecraft's thruster is the first."* The Sleeping Ice's sheet, looking down at it: *"you are the only
  source of ignition on the hemisphere."* On the floor there is no air to burn with. On the beach there is.

**"OMG did you see that?"**
1. *On screen:* a crew member's suit charge reads low at the far end of an errand, and the walk back becomes a run.
2. *On screen:* a Jawa tries to light a fire. Nothing. Tries again.
3. *On screen:* a wall of the ship's hold frosting over from the outside in, and the crew dragging bedrolls into
   the one warm room.
4. *(0.2.0)* *On screen:* the crew's own warm footprints, refrozen glossy across the ice, and arcs of light
   running along them toward the ship. The garden has an immune system and it reads heat.
5. *(0.2.0)* *On screen:* somebody harvests the wrong crystal. The fuselight carries its own oxidiser. It is the
   one thing down here that does explode.
6. *(On the beach, campaign layer)* *On screen:* hoses run from the grounded ship to the lake, pumps thudding, and
   a V-shaped wake coming across the black mirror toward the hose.

**The hull.** Cold. An underpowered ship loses rooms to it, and everything that keeps it warm marks it. The answers
are power and insulation, and not staying.

**Fuel: replete.** His word of 2026-11-18 names it: *"One or two are REPLETE with fuel (the frozen Chill beach for
example)."* The sheet: *"Fuel by the pipe-length — a single vast deposit, refueled in place (ruled), priced entirely
in cold survival."* Refuelling is *"by long flexible pipes from the grounded ship"*; tanker runs were cut. The
pipes, pumps and what pumping wakes are built in the campaign layer (`src/RimUtinni/PropaneLakeMechanics/`). On the
floor, the rare catch table already brings up chemfuel. Refining catch and crystal into fuel is built and, by his
ruling on the flora, *"very late game."*

**What the crew takes away.** Full tanks. Crystal wood; the rime nodule's mild euphoric; stonewater for cooking.
The ending of the campaign is under this floor (the war lab and the crater) and belongs to the campaign layer.

---

## When the Empire arrives

Under `UNSETTLED` above. What each sea does to anything that comes down, whoever it is:

- **The Scald** scalds it at the vents and heats whatever it parks.
- **The Grey** crystallises it. A siege that holds still is the Grey's favourite kind of visitor.
- **The Twilight** carries it down a river that looks dry. Nobody warned them about the stakes.
- **The Chill** freezes it, and on the beach anything hot near the lake is the most dangerous object on the planet.
  The sheet's own ending for the Empire here is on file: if the Empire learns of the place, *"they bomb their way
  into it."*

## Who else attacks; who hates the Empire

- **The seas' own predators,** ordinarily. In the Twilight, the one hunter in the dark; in the Grey, the giant.
- **Nobody raids from the water.** *"No native land predator hunts the water"* (the Scald), and the reverse holds.
- **The Deepwater Compact** live on the Twilight's floor: *"lamplit dwellings on the bottom, where the Deepwater
  Compact has been living all along."* *"The Deepwater do not raid."* They are the campaign layer's (0.2.0 here),
  and what they sell is *"dock-rights, air, lamplight, and charts."* Whether they would shelter a ship from the
  Empire is `UNSETTLED`.
- **The Brine Elders** of the Grey (0.2.0) are *"older than every faction"* and remember *"the arrival of the
  Reshapers"*. They *"can release... blinding area-wide discharges powerful enough to stun living creatures,
  disable droids, collapse shields, and cripple nearby ships."* They take no side. They trade.
- **Two faiths hold the Scald's shore** and neither is the Empire's. Campaign layer.

## What forces the crew out; what lets them stay

**Out, before the Empire:** in the Scald, the rooms heating; in the Grey, the doors; in the Twilight, the deck
filling and the light walking away; in the Chill, the power it costs to stay warm. Everywhere: air, food and water
are what the ship carried down.

**Stay:** cooling, chisels, a cleared deck, a warm core room. Covered ground, one step slower above. In the
Twilight, the only place on the planet where a crew can simply fish.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The ship lands on each sea's own floor, with that sea's ground, light, plants and animals, and can leave again. | A landing and a launch on each of the four. | A generic empty floor fails. So does a floor reached any way but the ship. |
| Every catch has a living body on the floor. | Fish each beach; find the same kinds alive below. | |
| **Scald:** vent pools scald and the ground between does not; the water also gives the bathing thought; it is never drink. | A pawn on substrate, in a pool, and trying to drink. | A native animal in the same pool is unhurt. |
| **Scald:** a parked ship's rooms slowly heat; doors never seal and launch is never blocked. | A ship parked for days, cooled and uncooled. | The same ship on the Twilight floor does not heat. |
| **Grey:** touching a brine pool encases the toucher, who is cut free alive by others. | One pawn at a pool, one rescuer. | An encased pawn is never lost: it is a thing on the map. |
| **Grey:** a parked hull rimes, then its doors salt shut from outside and force open from inside; chipping clears it and yields salt. | A ship parked near and far from a chimney field; chip one door. | Interior heating changes nothing. Nobody is ever sealed in. |
| **Grey:** formations, salt fall, a crystal garden and solitary animals in short sight. | A walk from the ramp to a pool and back. | Nothing schools. |
| **Twilight:** the bed of a bottom river carries off whoever steps past the stakes, to a sink where they stay findable and from which they are rescued into the hull. | A worker past the stakes; a rescuer; a second rescuer after the first is lost. | A roof built over the sink saves nobody. A cold reader can tell bed from bank without labels. |
| **Twilight:** a surge is warned, widens the reach, and passes. | Work at the stakes through one surge. | |
| **Twilight:** light-wells wane, close and open elsewhere within the visit; a giant animal visibly tends the lid and cannot be harmed. | A stay long enough for one well to turn over; an attack on the gardener. | The attack is refused with a reason; no corpse, no silent respawn. |
| **Twilight:** panes fall with a shadow first, can kill, pile on the deck, and must be cleared before launch. | A pawn and a crate under a shadow; a launch with a laden deck. | Launch is delayed, never locked: clearing always works. |
| **Chill:** brutal cold; no fire; a suit with one charge; a ship that loses rooms it cannot heat. | An errand to the end of a suit's charge; a fire attempt; a ship on half power. | A fuselight still burns: it carries its own oxidiser. |
| **Chill:** the catch can bring up fuel. | Fish the floor's rare table. | |
| Nothing vanishes in any sea. | Every loss above, with a save and reload in the middle. | |

Settings: a switch per sea and per major feature, defaults as shipped; everything off leaves four floors with
ordinary life on them (standing rule, every mod).

## Shared machinery

**Featured here** (a sea is where each is vital and should be proven):
- **The ship as the only door** (the seabed layer and its floor maps; `DivingInteraction`, `SeaShores`).
- **A place wearing on a parked hull:** rooms heating (Scald), crust and salted doors (Grey), a laden deck
  (Twilight), cold (Chill). Four forms of one idea, and the natural home for whatever shared hull-wear machinery the
  other biomes' designs end up asking for. No shared system exists in `src/` today; each is its own code.
- **Water that carries** (the Twilight's current, surge and sink, on `FlowWorks`' bank and arrest seams).
- **Encasement** (the Grey's pools; one mineral for statuary, a pawn and a hull).
- **Light as ground** (the well lifecycle and the shared light ledger; creature light that moves with its body).
- **Catch with a living counterpart** (the rule for every sea).

**Merely active here:** contact heat and liquid classes (`FlowWorks`, `EnvironmentalHazards`); ordinary creature
behaviour and real flight (`CreatureBehaviors`); the growth engine; wreck salvage; bone from butchery; the one sun
from geometry, which on a floor is nothing and on the Scald's beach is high; the Empire's search and the visibility
dial.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**0.1.0, the stop**
- Four floors as real places on the ship's layer, each with its ground, sight, ordinary weather, plants, animals
  and catch. (rosters, flora and catch built; the Scald's walkable hot substrate is not; the layer's per-sea floors
  unproven)
- The Scald: vent pools that scald; the bathing thought; the Immersion Berth. (terrains built; the berth unproven)
- The Grey: formations, channels, pools and salt fall; encasement and rescue from it; hull rime and salted doors.
  (built; the hull work moved in, see `rewrite_choices.md`)
- The Twilight: the lid, the columns, wells that turn over on the built week-scale clock; the gardener, protected;
  the current, banks, stakes, surge, sink, rescue, harness and warnings; falling panes and the laden deck. (built,
  except the gardener; panes moved in)
- The Chill: the cold, the fire ban, the heated suit, the drowned aurora; fuel in the rare catch. (reported built
  2026-10-01; the census marks the floor "unknown")
- The beaches as they are: fishing, the Scald's steam sky.

**0.2.0, the stop with company**
- The Grey's lamp life: the fessk at the edge of the light, light-seekers, the giant that comes to break a lamp;
  the pool sentinel's squirt; plants that sting on contact; the Brine Elder's trade. (built)
- The Twilight's liars and grazers: the vaulisk; the suulk that eats light; lid-dark when the gardener passes.
  (built; lid-dark unknown)
- The Scald's set-pieces: bubble-sail and walker appearances, steam devils, vent flashes; the steam-catch for clean
  water at the beach. (built)
- The Chill's garden defence: warmth trails, arcs and waking colonies; the fuselight's explosion; the wax
  procession; aurora surges; catch refined to fuel. (built or reported built)
- The Deepwater Compact's lamplit holdings on the Twilight floor. (campaign layer; unknown)

**Later (a crew that stays, or a colony)**
- The Twilight's light economy: tenancy, claim buoys, ageing charts, light cages, clipped lamps, the cultured
  sun-sphere, cargo floats, the harsher sink outcomes, plant charge and wilt; the Ark Seed; the Compact's permits and
  the full underwater town.
- The Chill's industry: cryoponics, tarspool fractions and the drug, hydrocarbon flesh, stonewater extraction; the
  crater and the war lab's ending (campaign).
- The Scald's exposure clock and boil-suit; the two-faith shore, the bathing rite, the Walking Pasture as a
  followed herd, the Return Gallery; sponge colonising wrecks.
- The Grey's reactive art; the elder's relics.
- Forty colonists on a floor.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Diving or returning as a single pawn; the dive hatch; any place "on the surface" of a sea.
- Light calling the sea in the Twilight (cut by his typed word, 2026-09-26). Fuel traded for time against the
  Grey's crust. A tomb.
- Waymark navigation and getting lost in the Grey's murk (story only, 2026-09-27).
- A potable, drained or cooled Scald. A tanker economy on the Chill. Kyber in the Chill's crystals.
- **Recommended for dropping, not yet his:** the inert cross-biome switches (the cleanse's recommendation, kept).

## NEEDS HIM

1. **What does the Empire do about a ship at the bottom of a sea?** *The probe and the bombardment follow; the
   troops wait at the beach and meet the ship when it lifts* (default for writing the rest; it needs the fewest new
   things). *Everything follows:* troopers on the floor in their own gear, and each sea does to them what it does
   to the crew. *Nothing follows but the clock:* the floor is safe from all but the last step, and the seas become
   the campaign's hideouts.
2. **Is the Chill's floor "full dark"?** Under a black sea on the night side it is the darkest place a ship can
   park. *One step, like the other floors* (default). *It pauses the search:* the Chill becomes the second true
   refuge after the Abyss, priced in cold and power, and it is also the fuel stop.
3. **Should the Brine Elder's trade come forward into 0.1.0?** It is built, it is his own paragraph, and a mind
   that pays richly for anything it has never tasted *"once, then nearly worthless thereafter"* is a customer made
   for a hold full of junk. *0.2.0* (default). *0.1.0:* the Grey's first version has its marquee, and one more
   system to prove.

The cleanse proposal of 2026-11-17 asked him one question, whether the Twilight's wells may turn over on the built
week-scale clock when the frozen sheet says years. It is answered here by scope: a visit lasts weeks, so the
week-scale clock is the only one a crew can see, and "years" is read as the sheet's ban on a permanent well.
