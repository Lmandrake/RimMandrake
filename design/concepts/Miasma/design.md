# The Miasma: the design, seen from the ship

**Status:** the one design document for the Miasma biome (`RM_Miasma`, source `src/RimMandrake/Miasma/`), rewritten
2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the older
definition sheet, the two rosters, the kit spec, the review and the cleanse proposal as the place to read; what
happened to every idea in them is in `design/concepts/Miasma/rewrite_choices.md`. Nothing has been deleted. This
is a design document only and it launches nothing.

**What kind of place this is (checked against the sheet's own header):** a surface biome: the deltas where the day
side's last rivers reach a dying salt sea. It is wet but it is not a sea. The ship lands on the mud and roots like
anywhere else; nobody dives. (The open Grey Sea beyond the mouths is a different biome with its own design.)

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/Miasma/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Miasma has no locked sheet or tree; its only pipeline material is the
cleanse proposal of 2026-11-17, which this design supersedes and which was never applied.

**Second reader, 2026-11-18.** A second reader who did not write this design read the sources to their ends and
repaired it; what changed and why is at the top of `rewrite_choices.md`. In short: the hull section now rests on
his shield rulings of 2026-09-02 and the built frame, and says plainly which wear is built, which is his ruling
waiting on one flag, and which is this rewrite's proposal; the decay cell is named as the Miasma's row on his
ship-gift register and described as it is built; the cast uses his names of 2026-10-08; and several lines say
"as built" where the first read said "built".

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"A stinking, beautiful nursery where the sea dumps everything. Rot is power, and every surge brings orphans."*
> (owner, by card, 2026-10-20)

> *"Out of darkness, possibility. Out of muck and stink, rebirth... maybe. It's being worked out."*
> (owner, `the_miasma.md` header)

A salt-crusted forest of mangal trees on stilt-roots, standing in brackish channels between a dying sea and the
rivers that feed it, *"under a green-gold haze of its own breath."* It has never once rained here. *"Everything
ends up here: the water, the sins it carries, and the life running from the salt."* The sea is being pickled in
its own basin and its whole roster has crowded into this fringe to breed, so the water boils with young. *"The
record density is not abundance. It is refugee crowding."* The ground *"crawls with little armoured scuttlers that
everything eats."* The mud is *"the planet's compost heap at fever heat"*, and the air makes people sick.

And through all of it, flowers. *"These plants should all be strangely beautiful but also a little sick looking."*
(owner, 2026-09-23). The rainbow blooms are the one thing here that is exactly what it seems: *"VERY beautiful and
hopeful"*, *"never a trap, never a mimic, never toxic."*

**Seen from the ship, this is the only wet biome on the planet where the crew's own trade is already practised.**
The sheet lists them among the inhabitants: *"The Jawa — flotsam-combing crews working the root-lines after every
surge; the delta is a harvest that restocks itself."* It is *"the planet's driftwood-and-salvage beach."* The crew
know what a salvage beach is. What they do not know is mud, brine, fever, a food chain that clicks, or the size of
the thing in the shallows whose children keep washing up at their feet with a price on them.

His question to every biome, typed on 2026-09-24, was the lens seven weeks early: *"how can this biome uniquely add
something to the ship?... What can they take and improve their ships environment with?"* The Miasma's row on that
register (`infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`) is the **decay cell**: *"power from rot, in a
bed of delta loam, silt and salt."* (The pick is an agent's, carded to him; no answer was found.)

What holds the place together is his own answer of 2026-11-10: *"Abundance forces difficult choices: there are
competing worthwhile opportunities."* Every surge delivers more than a small crew can pick up.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last (the outer edge of a stay, not the usual one; owner's ruling of 2026-11-18).**
Longer than an open landing by the two steps of cover below: on the ladder's provisional numbers each wait about
doubles, so first contact comes around day 10 to 16, a first fight around day 24 to 40, and nothing much past about
two months. That is the Empire's edge. The Miasma's own edge usually comes first: the place sickens a crew on a clock
of its own, and each surge may put the ship's footing in brine.

**What cover this place gives, and which kind (same card: canopy, steam and fog slow the search by one step).**
- **From orbit: partial cover, two ways over.** A closed mangal canopy, and under it a haze that *"never lifts"*.
  Canopy and haze are one step each, and by his card of 2026-11-19 they add up: the search runs two steps slower
  here. It is never paused: this is a dim place, not a dark one.
- **On the ground:** the haze softens everything and the root-maze breaks every sight line. A probe has to see
  the ship or the crew to count, and here it has to find them first. The ground is also the slowest to cross on
  the day side (the sheet keeps the donor's figure for how hard it is to move here and explains it as *"the
  root-maze and the muck"*), for the Empire as for the crew.

---

## The first minutes

The ship comes down through green-gold murk onto the only ground there is: roots, mud and salt crust. Which of
the three it lands on matters for the rest of the stop, and the map says which is which: every map has a fresh
end and a brine end, and trees, animals, sickness and the colour of the muck all sort along the line between
them. Two trees bracket the line. The ilbareen lives only at the fresh end, and where brine has ever reached it
stands dead and white for years: *"a flagpole, and a graveyard of them."* The brelloch, squat and armoured in its
own salt, is *"the last living thing before the salt wins."* (As built the surge kills ilbareen where it reaches;
the living canopy does not yet sort itself by band.)

**Where to park is a three-way trade.** The fresh end has the fertile mud and the crops. The middle of the line
has the worst air: the kit sorts the haze's load along the gradient, heaviest *"where everything settles,
mid-gradient"* (the built exposure reads salinity). The brine end has the cleanest air, the firmest ground, the
mother's water if there is one, and the salt.

The ramp opens on a sound nobody aboard has heard before: *"the wet click-and-chitter of the arthropod floor,
swarm-hum, channel-slap."* The mud is moving. It is scuttlers, *"in uncountable numbers... faintly comic; the
entire food pyramid stands on their backs."* The commonest, the karravel, is a coin-flat disc whose legs never
show, and in numbers *"the ground appears to be sliding."* Something flowerlike closes on one.

Before the first hour is out the player should have seen three things without hunting for them: the water in the
channels thick with small swimming young; a plant eat a scuttler; and, among the roots at the last water line, a
drift of things the sea left, some of them metal.

## The first day

- **The root-lines are the yard.** What the rivers carry and the sea throws back lodges in the roots: timber,
  brined wreck frames and tanks, loose goods. The crew combs it. This is the work they came for. The yard has a
  plant: thrannock, a root-mass strung between two trees like *"a net someone left"*, hung with *"rags, shell,
  splintered wood, salt-bleached plastic."* *"A freshly loaded thrannock means the water came up recently."* The
  near roots hold a little wood and cloth; the metal, the wrecks and the crying are farther out.
- **The mud is slow, the roots are the ground.** *"The trees drink what nothing else can; the roots are the only
  ground."* Fresh mud is fertile and miserable to cross; salt crust is firm and dead.
- **The small are cheap.** The sea's young are everywhere in the shallows, *"small and almost charming and cheap
  to hunt."* *"Every scavenger knows the arithmetic: don't kill what's small here; its mother is why nobody goes
  out onto the open water."*
- **Scuttlers are dinner.** Harvestable, renewable, and eaten by everything else too, including five kinds of
  plant that never touch a person or a tame animal.
- **The flowers are honest.** A crew that has learned on every other stop not to touch the pretty thing can touch
  these. The commonest plant in the delta, the aphreen, has every growing tip flushed red and furred as if
  inflamed: *"it looks diseased and it is perfectly healthy, and a player who learns that about aphreen has
  learned how to read this biome."*
- **The air is a wager, and the ship is the roof.** The haze carries the mud's failed experiments: *"the 15-day
  clock and the hope are the same process."* Sooner or later somebody is ill. Separately, time spent outdoors in
  the haze builds a mild exposure that clears under a roof (built). A crew that sleeps and works aboard pays less
  of it than a colony in the open would.
- **Sometimes the offer is there on the first day.** A warden mother, where there is one, sometimes arrives with a
  stranded young of her own already calling from a cut-off pool. The roster's reason is the lens's reason: without
  this *"the entire relationship waits on an irregular, storm-driven surge... the offer arrives with her."* A stop
  too short to see a surge can still be asked the question.
- **A dead meter in a compost bed is still reading current.** New maps hold one. Working out why teaches the crew
  to build a **decay cell**: a bed that makes power from ordinary rot. *"Opportunistic extra power, using waste
  already on hand"* (his answer of 2026-11-10). The design is that spoiled food, scraps and the day's butchering
  all go in: *"spoiled freight becomes power."* **As built it does not do that yet:** the cell needs the
  electricity research and its hopper takes raw food, not rot (`Answered on 2026-11-19` 7).

## The first week

- **The surge.** *"No moon, no clockwork tide."* When storms far off pile the sea against the shore it comes up
  the channels, days apart and never on schedule, announced by *"a long exhale from seaward."* Brine wets ground
  that was fresh. The salt line *"moves miles per surge."* Then it draws back, never quite to the old line. The
  warning is long enough to get the crew back aboard; it is not long enough to move anything that was put in the
  wrong place.
- **What the surge leaves, all at once.** New flotsam in the roots. Crops on unfloored ground the brine reached,
  dead. A tree that only lives in fresh water, the ilbareen, standing dead and white where the brine got to: the
  gauge that shows how far it came. And sometimes, in pools the water left behind, young of the sea that cannot
  get back. And often, in the days after, a karrimeth mass: thousands of thumb-sized shells flowing through the
  camp as one clicking body, *"the surge's aftermath made visible"*, a nuisance that *"strips forage and fills the
  traps."*
- **The orphans are an event, not a duty.** His words of 2026-11-10: *"the colony doesn't HAVE to rescue them,
  this was supposed to just be an event, not the center of the whole biome."* A stranded young cries, and the cry
  can be located. Some have been in the pool too long and are changed by it: *"gills going leathery, fins splaying
  into feet that don't quite work."* A crew member can carry one to connected water. Or pen it wet and sell it to
  the next ordinary trader, for a great deal. Or leave it. The pools shrink, and a
  bozzuga, the ambush frog of the fresh roots, eats stranded young as readily as scuttlers.
- **Sometimes there is a mother.** Not on every map: *"only sometimes. And babies can be swept in without the
  mother present as well."* Where there is one she is a **warden mother**: *"a not-so-gentle giant"* in the
  shallows, an enormous barnacled sea elder, lethal within reach, who *"cannot get on dry land"*: *"the sea's
  memory dying in its lifeboat."* She is visibly old from the first sight of her, and her inspect line says so
  outright (*"a player who is surprised by her death means this was built wrong"*). She can hear a
  stranded young and see it *"and will never cross the few metres of dry ground between. A colony can."* Carry
  her young back and she stops counting the crew as prey. Sell one and her nursery remembers for good. Harvest
  inside her reach and tolerance ends on the spot. (As built she is not yet held to water on every step: her
  destinations are checked and a recovery walk brings her back. The whole friendship rests on that line, so it is
  owed work, not polish.)
- **Her protection is a place.** *"A colony with its back to open water is nearly unraidable from that side. A
  colony four tiles inland gets nothing."* A ship set down with its back to her channel has one side nobody
  crosses. A ship parked inland has a neighbour.
- **Triage.** A surge's leavings do not wait: the pools dry, and the next surge rearranges the yard. A crew of
  five to seven chooses.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The floor moves.** *On screen:* the ramp comes down and the mud scatters in a thousand small armoured
   directions; a hooded figure lifts one foot, then the other.
2. **The flower eats.** *On screen:* a lovely, slightly feverish-looking plant snaps shut on a scuttler. The Jawa
   beside it backs away from every flower on the map, including the harmless ones. The roster's best version is a
   wave: *"a channel of braskeen snapping shut one after another as scuttlers cross is the biome's best ambient
   moment."*
3. **The sea comes to the ship.** *On screen:* a long breath from seaward, and water creeping up the channels,
   over the mud, around the landing gear; the white edge of salt left on everything when it goes.
4. **The crying pool.** *On screen:* a puddle among the roots with something small and finned turning in it,
   calling; and out in the channel, a shape the size of a building, as near as the water lets it come, not moving.
5. **The carry.** *On screen:* a Jawa wading with an armful of infant sea-monster toward the largest animal they
   have ever seen, which watches them come.
6. **The sale.** *On screen:* the same infant in a wet pen, a trader counting out silver, and the cry going on
   the whole time. Afterwards the shape in the channel is no longer still.
7. **Too close.** *On screen:* a crew member combing flotsam a few cells inside her reach.
8. **Plugging in the compost.** *On screen:* the crew shovelling spoiled rations into a bed of mud and salt with
   wires in it, and the ship's lights coming up. (The scene as designed. As built the bed takes raw food.)
9. **The gauge.** *On screen:* after a surge, a row of trees gone white overnight, ending two cells short of the
   ship.
10. **The swarm.** *On screen:* a humming gold cloud comes through the camp, *"the green-gold breath the biome is
    named for, seen close up"*; the day after, a Jawa is in bed. (As built the cloud is an animal and the fever is
    the biome's own clock: the two are not yet linked, and the old rule that the trees need the swarm was removed.)
11. **The mass.** *On screen:* after a surge, the ground at the brine end starts to flow: a grey clicking carpet
    goes round the landing gear, through the cook-fire and out the other side.
12. **Too clean.** *On screen (the haze counts on the ship's screen, `Answered on 2026-11-19` 1):* the particulate
    screen comes up and the scuttlers peel back from the hull in a ring; the ship stands in the only bare mud on
    the map.

*0.2.0 adds:* the survivor who gets up from the fever changed; the young that decide they belong to the crew and
cannot leave the water (one *"stops at the waterline and watches you walk inland. It is there when you come
back."*); the beauty oil pressed from the ugliest mud on the planet; the lastvine (*"It is not a plant."*) that
spits acid, the duskfire that spits fire (*"never fight one near anything you want to keep"*) and the fermatalis,
*"usually drunk on it"*, which ferments whatever it breathes on and takes to a crew *"especially if you bring a
drink"*; the cell that takes a corpse and gives back bones and a named skull. With the campaign's cast: the hell's
lantern, a muffalo-sized worm whose pods *"glow a sickly orange"* in the dusk under the roots.

## When the Empire arrives

- **They are slow to find the ship and slow to reach it.** Two steps slower from orbit; on the ground, haze, roots
  and the worst walking on the day side.
- **The water is not theirs.** A strike team wading the brine shallows may be wading inside a warden mother's
  reach. She tolerates a crew that returned her young. She tolerates nobody else.
- **A ship with its back to her channel is attacked from one side fewer.**
- **Nobody shoots well here.** The haze takes a little off every shot and a surge's weather takes more, for
  both sides (built; the amounts are tuning).
- **The surge does not take sides.** A siege camp built on ground the next surge reaches is in brine with the
  crew's crops.
- **The air does not take sides either.** A force that stages here for days breathes what the crew breathes.
- **The crew can be standing on the only good ground.** A crew that has read the gradient holds the roots; what
  is left for an assault is mud.
- *0.2.0:* a held, unsold young is still crying when the troopers come ashore beside it.

## Who else attacks; who hates the Empire

- **The warden mother,** where there is one: whatever comes within her reach and is not tolerated.
- **Ordinary predators** of the channels and the mud, and the swarms, which bring fever rather than wounds.
- **Other flotsam crews,** Jawa among them, work these root-lines in the campaign's world. They are rivals for
  the same yard and the nearest thing to neighbours; the biome mod places none of them.
- **Buyers.** In the campaign the ones who come for a held young have names: the Deepwater vigil, who want it
  *"for the sea"*, and margin traders, who want it *"for the pens."* They are not the same sale.
- **The Wildsteam** hold a seat on this coast, Bitterleaf, and make pilgrimage here: *"come here when all hope is
  lost, and you either die or return with hope found."* *"A Wildsteam pilgrim in the muck is on the worst day of
  their life, on purpose."* **The Deepwater vigil** watches the sea die from posts at
  the mouths. Both are campaign layer; whether either would fight the Empire is `UNSETTLED`.
- **Nothing here hates the Empire.** The place is busy.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- Sickness: a crew this small cannot carry many in bed, and the air keeps dealing.
- Brine at the ship: a surge that reaches the landing site, and the next one coming.
- A mother betrayed, between the crew and the water they need.
- The yard combed out, if the surges hold off.

**Stay, longer than the Empire would like:**
- Canopy and haze over the hull.
- Food that restocks itself, salvage that restocks itself, power from the waste of both.
- A tolerant mother in the channel, which is a guard nobody posted.
- Fresh-end ground the crew chose well.

## What the crew takes away

- **Flotsam:** timber, brined frames and tanks, loose goods. The reason to come.
- **Silver for a stranded young,** and what it cost.
- **The decay cell,** the Miasma's gift to the ship on his register: learned here, built on the deck, usable
  anywhere there is rot. On a ship that always has spoiled food and butchery waste, this is the stop's most
  lasting gain. *"The gravship becomes a scrapbook of everywhere it has been."*
- **Scuttler meat, delta loam** (clean, fertile soil from the sickest ground), **delta salt, delta silt.**
- **Thessamor wood** from the mangals; **liliana silk** (his moth of 2026-10-08, which *"never stops"* spinning)
  and eggs; **sarrash cloth**; **sharpshrimp chitin**.
- *0.2.0:* **a fever survived,** best of all the one that leaves a crew member **fever-tempered**, comfortable
  across a wider span of heat and cold, which *"pays game-wide on a planet whose geography is temperature"*;
  **attar,** *"an expensive oil that restores beauty... the planet's loveliest luxury, pressed from its
  ugliest mud"*; **a fever survived,** with what it left behind; **bizarre ingredients** from a spent cell's
  rotting bed (*"Decay cells, but they become a rotting bed that is part of Star Wars Cuisine ingredients"*,
  owner, 2026-10-02).

## Fuel, and what this place does to the ship

**Fuel: the emergency-slow kind, in the one place it is never short of feedstock; and a coast where it can be
bought.** (Owner's ruling of 2026-11-18.) Nothing in any Miasma source is a fuel. Rendering biomass is as slow
here as anywhere, but there is no end of biomass. What the Miasma offers instead is the thing that saves fuel: a
ship running its lights and benches off decay cells is not burning its tanks to do it. *"Rot is power."* Fuel
proper is bought: Bitterleaf, the Wildsteam seat on this coast, runs stills (*"stills running attar, liquor, and
hope"*), and the flotsam crews trade. Both are campaign layer, and whether Bitterleaf's stills sell fuel is
`UNSETTLED`. Bitterleaf is a sea-facing island with no road, so "on this coast" means a flight, not a walk. And
the fuel-saving half of this paragraph holds only when the cell eats waste: as built it eats raw food, which on a
hungry ship is fuel of another kind (`Answered on 2026-11-19` 7).

**What wears on the ship (owner's ruling of 2026-11-18: in 0.1.0, from what the sources already say).** The frame
exists and is not redesigned here: `src/RimUtinni/ShipShields/`, on his shield rulings of 2026-09-02. *"The
environment is hostile and immediately goes to work on the ship... Its hull is thick and can take a lot of damage
in most situations, so no environment is immediately lethal."* An unshielded hull in a hazard deteriorates, faster
the longer it sits; the ship advises and never refuses. The October review said of this biome that it *"does
nothing to your ship."* Read against the frame, there are three candidates, in order of how well sourced each is.

1. **Heat, on the hottest ground (built, nothing to add).** The frame already counts a map as a heat hazard at 58 C
   outdoors or in a heat wave, and the sheet's temperatures for the deltas run to 59. On those days an unveiled
   ship wears here as it would anywhere. *Answer:* the thermal veil. (Read from the code and the sheet; no map
   temperature was measured.)
2. **The haze (his ruling, one flag short of built).** His note on the particulate screen: *"Light kinetic
   deflectors handle wind, ash, vapor, bio contamination, spores, smoke, sand, and rain damage completely as well
   as repels small animals."* The Miasma's air is vapor and bio contamination by its own description (*"thick with
   the Working's breath"*). As built the frame looks for pollution or a weather with a sand rate, and the haze has
   neither, so today the frame does not see it. Counting the haze is one flag on one weather, not a new system.
   *Answer:* the particulate screen. And because that screen *"repels small animals"*, a screened ship in this
   biome stands in a ring of mud with no scuttlers on it and no swarm over it. The haze counts: an unscreened ship
   wears slowly for the whole stop (`Answered on 2026-11-19` 1, by his ruling).
3. **Brine (this rewrite's proposal; no source says a hull wears from it).** One pitch he did not choose calls a
   warden mother's shell *"the only brine-proof plating on the planet"*, which implies what brine does to other
   plate; nothing else in the sources puts salt on a hull. What his rulings do settle is that no shield answers
   it: *"Slow pressing things move through all shields... This is why nothing 'holds out water,' it just doesn't
   work that way."* So if brine wears a ship whose footing a surge has reached, the answers are by position (land
   above the dead ilbareen; the brine comes up the gradient, not from the sky), by hand (clean the crust off: new,
   small work, no source describes it), or by armour (the plate he did not choose). The surge does not repaint the
   deck itself: the built repaint leaves gravship foundations alone. Not in 0.1.0: brine wear is a proposal for
   0.2.0, because no source has it (delegated call, `Answered on 2026-11-19` 2).

The fever wears on the crew, not the ship, and is covered above.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Every map runs from a fresh end to a brine end, and ground, trees and water sort along it. | A generated map walked end to end. | Bands painted with nothing living sorted by them. |
| A surge comes without a schedule, actually wets ground and draws back, and moves the salt line; the gauge trees show how far. | A landed ship through two surges, one of which reaches it. | A repaint of colours with no water moved. A surge on a timer. |
| Brine that reaches unfloored crops kills them, and floors survive. | A planted patch and a floored patch in the surge's path. | |
| After each recession new flotsam lies in the root-lines, and it is real goods. | Comb the roots; wait for a surge; comb again. | A yard that was stocked once at the start and never again. Goods that appear on dry ground far from any root. |
| Some recessions leave sea young in cut-off pools; they cry and can be found; a crew member can carry one to connected water; left alone, the pool's end leaves something to read. | A recession that strands young, with and without anyone responding. | A pond that was always there. A young that vanishes with no sign. A recession that must strand young every time. |
| A stranded young can be held wet and sold to an ordinary trader for a notable price. | Hold one; a trader visits. | A sale that completes without a trader. A training order mistaken for a sale. |
| The ground life is real: scuttlers in numbers, hunted by animals and by five plants that never take a person or a tame animal. | A generated map left to run with a pet walked past each predator plant. | |
| The rainbow blooms are harmless in every way. | Touch, harvest and eat near each. | |
| The haze never lifts and never rains, softens the light, and the air here makes people ill more often than elsewhere. | A stop of some weeks. | Rain. Clear sky. |
| *(0.2.0 proposal only, not a 0.1.0 promise; `Answered on 2026-11-19` 2.)* A hull a surge has reached is worn by salt until it is cleaned, and a ship landed above the surge's reach is not. | Two landings, one surge. | Wear with no brine. |
| The haze wears an unscreened ship and a screened one is clean, with the small animals keeping off it. | Two ships, one screened, some days. | A screen that changes nothing visible. |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Where a warden mother is present, she keeps to water, defends her reach, tolerates a crew that returned her young, and never forgives a sale; harvesting inside her reach ends tolerance at once. | A map with a mother: return one young; then harvest inside and outside her reach. A second map: sell one. | A mother on every map. A mother on dry land. Tolerance that survives a sale. |
| A dead meter found on the map teaches the decay cell; a cell fed ordinary rot gives real power. | Find, study, build, feed with spoiled food, run a bench from it. | A cell that runs on nothing. A cell that only takes good food (what is built today). |

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary hot mangrove swamp
(standing rule, every mod).

## Shared machinery

**Featured here** (the Miasma is where each is vital and should be proven):
- **A gradient across the map, and a surge that moves it** (the shared gradient, surge and pool pieces in
  `EnvironmentalHazards`). Any shore could have a tide line; here it is the whole stop.
- **Pools cut off by receding water, and what is caught in them.**
- **A large animal anchored to a place and bound to water, with a list of whom it tolerates.** The witness and
  tolerance bookkeeping is kin to the Leaning Scrub's giants knowing who lit the fire.
- **Small breeding prey as a floor** (`CreatureBehaviors` vermin breeding), and plants that eat it.
- **Power from rot** (the decay cell), learned here and usable everywhere.

**Merely active here:** canals (`FlowWorks`: water where the crew digs it, and brine if they dig from the wrong
end); wreck salvage (`Wreckage`, as brined frames and tanks); fast-growth rosters; bones; the acoustic scanner's
readings; real flight (the swarm); the one sun from geometry, with tree shade (hot wet air is ordinary air
temperature); standing weather that softens sight (the same family as the Greentide's steam); the Empire's search
and the visibility dial.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**The one signature (his first-version answer of 2026-11-19): the surge and what it leaves.** A surge comes without a
schedule, wets the ground, moves the salt line and draws back; brine kills unfloored crops; each recession leaves
flotsam in the root-lines and, sometimes, sea young crying in cut-off pools, to carry back or hold and sell. *Why a
normal stop is sure to see it:* surges come without a schedule through any stop, and the ship's own landing ground
sits on the fresh-to-brine line they move. His experience line: *"A stinking, beautiful nursery where the sea dumps
everything. Rot is power, and every surge brings orphans."* *Runner-up:* rot becoming power in the decay cell (the
cleanse's runner-up), now 0.2.0 with the mother's price, as this design's own one-signature reading named.

**0.1.0, the stop**
- The land: fertile mud, salt crust, mangal canopy, the fresh-to-brine gradient, the permanent haze and its
  sickness. (built, except that the living canopy does not yet sort itself along the line)
- The surge moving the salt line, the gauge trees, crops lost to brine. (built, except that the surge does not
  yet move real water)
- Flotsam in the root-lines after every recession, and brined wrecks. (built; moved in, see `rewrite_choices.md`)
- Stranding pools, the changed young and their cry; carrying one back; holding and selling one to an ordinary
  trader. (built; the cry while carried is not)
- The warden mother where she occurs, as an ordinary animal: water-bound, defending her reach; old to look at and
  said to be old on inspection. (built, except that she is not yet held to water on every step)
- Scuttlers, plant predation, the swarm, the free nursery young, the ordinary predators, rainbow blooms and muck
  plants. (built)
- The ship's wear, on the built shield frame: heat on the hottest days (built); the haze on the particulate
  screen (his ruling of 2026-09-02; one flag on the haze weather, unbuilt).
- Canopy and haze as two steps of cover from orbit, added. (new, small, by his cards of 2026-11-18 and
  2026-11-19)

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The mother's price: tolerant after a return, unforgiving after a sale; sometimes arriving with a stranded young of
  her own. (built, except that a return can credit the wrong mother where two nurseries are close)
- The found meter and the decay cell, the Miasma's gift on his ship register. (built; moved in; as built it
  takes raw food, not rot)
*Already here before that answer:*
- The mother dying of age and one of her young taking the nursery; the heir's guard. A crew that stays its full six
  weeks can watch her fail and leave a child on watch behind it. (The cleanse's own target puts her death 30 to 60
  days after a crew meets her. As built the heir is a name and a message; no guard passes to it. Moved here from
  "later" by his first-version answer of 2026-11-19.)
- Brine on the hull, with its answers by position and by hand (this rewrite's proposal; no source has it; new,
  small).
- Fever-forging: a disease survived sometimes leaves a lasting change; the five strange ones he chose
  (swarm-marked, salt-blooded, loam-lunged, mother-dreamed, fever-tempered). (part built: the five are stand-ins)
- Young that tame themselves to a crew that has not harmed them, their guard and attack work, and the weaker
  watch a rescued nursery's young keeps. (built in part)
- Attar: the still, the oil, the glaze on artwork. (built)
- The spent cell's rotting bed and its ingredients; a cell that takes corpses and leaves bone. (built)
- The creatures' own tricks: the lastvine rearing and spitting acid, the duskfire's burning spit, the
  sharpshrimp healing, the siezer's lockjaw, the drake fermenting and drinking. (built)
- Buyers who come for a held young. (built)
- Fever passed by the swarm's touch. (unbuilt)

**Later (a crew that stays, a colony, or the campaign)**
- Canals that bring her water, and her, inland; a colony *"buying her protection with labour instead of
  location"*.
- Water-only hauling by tame young (the roster's *"single best fit between a creature and an existing economy in
  this biome"*: an orphan working the root-lines for a salvage crew; unbuilt); trees bound to hosts and castings;
  plants that show when they have fed.
- The Recall of the Written-Off rite (the owner's pick of 2026-10-02; a second-version design by the census;
  rites were tabled on 2026-10-03). It is the one Miasma idea that attacks the ship itself: its reclaimers
  *"dismantle powered structures (the gravship included) until the colony drives them off."*
- Bitterleaf, the pilgrimage, the vigil's posts, the named nurseries: campaign layer.
- The arthropod harvest as an industry (a trap and one dish were left out of the batch he picked on 2026-10-02);
  delta loam as an export trade.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Any medicine from this place (*"we have given medicine many times today"*); any gene machine; rain; a tide on a
  clock; saying whose plagues these are.
- A rainbow bloom that harms (*"the rainbow flora never lies"*).
- The mother at the centre of the biome, and a mother on every map (his answer of 2026-11-10).
- The stranded as species of their own (they are a condition of the nursery's young).
- **Raising a young into a leviathan.** His cut of 2026-09-23: *"the game isn't that long to watch it grow."* No
  growth arc, no "it leaves for the sea", no later meeting with the grown adult.
- **Salt gates and contested brine.** Declined 2026-09-23, when of five proposals he chose the warden mother
  *"only, all the way."*
- A conventional taming grind (*"animals in this project are not conquered, they agree"*); a second giant; a
  second pollinator; an auction or appraisal game on the yard.
- The brine-proof plate from a dead warden mother (passed over 2026-10-02), and the last dry deck: they stay down by
  his answer of 2026-11-19 on declined ship ideas; he can bring either back by name.
- The grounded mother, the last dry deck, the scuttler appraisal, the first egg above water, the second-hand
  young, the mother's blind side (not chosen 2026-10-02); the Tide-reader boon (cut 2026-09-12); the pollination
  gate (removed 2026-11-02 by a delegated decision under his veto card, as *"invisible to the player"*).
- The world-scoring worker and its biome-rarity slider (his ruling of 2026-08-15 and 2026-08-18: no worldgen, ever; no setting that could roll a second world).
- **Recommended for dropping, not yet his:** the
  map-wide rise in wild aggression when a mother dies at her site (built from the kit; his card of 2026-09-12
  ruled its scope, *"marked sites only"*, so dropping it is his to confirm); the attar balm that changes injuries;
  the old medicinal mangrove harvest.

## NEEDS HIM

None open. Every entry is answered (next section).

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. **[hull] Does the haze count on the ship's shield frame?** *His ruling:* his shield ruling of 2026-09-02: the light
   screen handles *"wind, ash, vapor, bio contamination, spores, smoke, sand, and rain damage completely"*. Counted:
   one flag on the haze weather. An unscreened ship wears slowly the whole stop, and a screened one stands in a ring
   of clean mud. **This changes the design's default.** Was: *Not counted*.
2. **[hull] Brine on the hull, and the brine-proof plate.** No brine wear in 0.1.0: no source has it. Brine wear is a
   proposal for 0.2.0. The brine-proof plate stays not revived: his card of 2026-11-19 keeps declined ship ideas
   down. *Delegated call* (the plate: his card).
4. **[other] Does a rescued young ever come aboard?** They stay in the water (the design's default). *Delegated call.*
7. **[fuel] What the decay cell eats.** Rot, as promised. The build is wrong and is owed a fix (the design's default).
   *Delegated call.*
8. **[other] The sando aqua monster adult.** Held: it breaks the sheet's "no second giant" (the design's default).
   *Delegated call.*

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

3. **[other] The last dry deck.** *His card of 2026-11-19 (declined ship ideas):* it stays turned down. He can bring
   it back by name.
5. **[scope] One signature, or the pieces.** *His card of 2026-11-19 (first version):* one signature a stop is sure
   to see: the surge and what it leaves (Scope, top). The decay cell with its found meter, and the mother's price,
   move to 0.2.0 with their text; the mother stays in 0.1.0 as an ordinary animal. **This changes the design's
   default.** Was: the pieces in 0.1.0.
6. **[scope] Her death.** *His card of 2026-11-19 (first version):* not in 0.1.0; the rest goes to 0.2.0, so her
   death and the heir move from "later" to the 0.2.0 list.
