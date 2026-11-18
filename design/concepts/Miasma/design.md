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

What holds the place together is his own answer of 2026-11-10: *"Abundance forces difficult choices: there are
competing worthwhile opportunities."* Every surge delivers more than a small crew can pick up.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last (the outer edge of a stay, not the usual one; owner's ruling of 2026-11-18).**
Longer than an open landing by the one step of cover below: on the ladder's provisional numbers, first contact in
the second week instead of the first, a first fight around the end of the first month, and nothing much past six
weeks. That is the Empire's edge. The Miasma's own edge usually comes first: the place sickens a crew on a clock
of its own, and each surge may put the ship's footing in brine.

**What cover this place gives, and which kind (same card: canopy, steam and fog slow the search by one step).**
- **From orbit: partial cover, two ways over.** A closed mangal canopy, and under it a haze that *"never lifts"*.
  The search runs one step slower here. It is never paused: this is a dim place, not a dark one.
- **On the ground:** the haze softens everything and the root-maze breaks every sight line. A probe has to see
  the ship or the crew to count, and here it has to find them first. The ground is also the slowest to cross on
  the day side (the sheet keeps the donor's figure for how hard it is to move here and explains it as *"the
  root-maze and the muck"*), for the Empire as for the crew.

---

## The first minutes

The ship comes down through green-gold murk onto the only ground there is: roots, mud and salt crust. Which of
the three it lands on matters for the rest of the stop, and the map says which is which: every map has a fresh
end and a brine end, and trees, animals, sickness and the colour of the muck all sort along the line between
them.

The ramp opens on a sound nobody aboard has heard before: *"the wet click-and-chitter of the arthropod floor,
swarm-hum, channel-slap."* The mud is moving. It is scuttlers, *"in uncountable numbers... faintly comic; the
entire food pyramid stands on their backs."* Something flowerlike closes on one.

Before the first hour is out the player should have seen three things without hunting for them: the water in the
channels thick with small swimming young; a plant eat a scuttler; and, among the roots at the last water line, a
drift of things the sea left, some of them metal.

## The first day

- **The root-lines are the yard.** What the rivers carry and the sea throws back lodges in the roots: timber,
  brined wreck frames and tanks, loose goods. The crew combs it. This is the work they came for.
- **The mud is slow, the roots are the ground.** *"The trees drink what nothing else can; the roots are the only
  ground."* Fresh mud is fertile and miserable to cross; salt crust is firm and dead.
- **The small are cheap.** The sea's young are everywhere in the shallows, *"small and almost charming and cheap
  to hunt."* *"Every scavenger knows the arithmetic: don't kill what's small here; its mother is why nobody goes
  out onto the open water."*
- **Scuttlers are dinner.** Harvestable, renewable, and eaten by everything else too, including five kinds of
  plant that never touch a person or a tame animal.
- **The flowers are honest.** A crew that has learned on every other stop not to touch the pretty thing can touch
  these.
- **The air is a wager.** The haze carries the mud's failed experiments. Sooner or later somebody is ill.
- **A dead meter in a compost bed is still reading current.** New maps hold one. Working out why teaches the crew
  to build a **decay cell**: a bed that makes power from ordinary rot. *"Opportunistic extra power, using waste
  already on hand"* (his answer of 2026-11-10). Spoiled food, scraps, the day's butchering: it all goes in.

## The first week

- **The surge.** *"No moon, no clockwork tide."* When storms far off pile the sea against the shore it comes up
  the channels, days apart and never on schedule, announced by *"a long exhale from seaward."* Brine wets ground
  that was fresh. The salt line *"moves miles per surge."* Then it draws back.
- **What the surge leaves, all at once.** New flotsam in the roots. Crops on unfloored ground the brine reached,
  dead. A tree that only lives in fresh water, the ilbareen, standing dead and white where the brine got to: the
  gauge that shows how far it came. And sometimes, in pools the water left behind, young of the sea that cannot
  get back.
- **The orphans are an event, not a duty.** His words of 2026-11-10: *"the colony doesn't HAVE to rescue them,
  this was supposed to just be an event, not the center of the whole biome."* A stranded young cries, and the cry
  can be located. Some have been in the pool too long and are changed by it: *"gills going leathery, fins splaying
  into feet that don't quite work."* A crew member can carry one to connected water. Or pen it wet and sell it to
  the next ordinary trader, for a great deal. Or leave it. The pools shrink.
- **Sometimes there is a mother.** Not on every map: *"only sometimes. And babies can be swept in without the
  mother present as well."* Where there is one she is a **warden mother**: *"a not-so-gentle giant"* in the
  shallows, an enormous barnacled sea elder, lethal within reach, who *"cannot get on dry land."* She can hear a
  stranded young and see it *"and will never cross the few metres of dry ground between. A colony can."* Carry
  her young back and she stops counting the crew as prey. Sell one and her nursery remembers for good. Harvest
  inside her reach and tolerance ends on the spot.
- **Triage.** A surge's leavings do not wait: the pools dry, and the next surge rearranges the yard. A crew of
  five to seven chooses.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The floor moves.** *On screen:* the ramp comes down and the mud scatters in a thousand small armoured
   directions; a hooded figure lifts one foot, then the other.
2. **The flower eats.** *On screen:* a lovely, slightly feverish-looking plant snaps shut on a scuttler. The Jawa
   beside it backs away from every flower on the map, including the harmless ones.
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
   wires in it, and the ship's lights coming up.
9. **The gauge.** *On screen:* after a surge, a row of trees gone white overnight, ending two cells short of the
   ship.
10. **The swarm.** *On screen:* a humming cloud comes through the camp; the day after, a Jawa is in bed. The
    trees it visited are in flower.

*0.2.0 adds:* the survivor who gets up from the fever changed; the young that decide they belong to the crew and
cannot leave the water; the beauty oil pressed from the ugliest mud on the planet; the creature that spits acid,
the one that spits fire and the one that gets drunk on what it ferments; the cell that takes a corpse.

## When the Empire arrives

- **They are slow to find the ship and slow to reach it.** One step slower from orbit; on the ground, haze, roots
  and the worst walking on the day side.
- **The water is not theirs.** A strike team wading the brine shallows may be wading inside a warden mother's
  reach. She tolerates a crew that returned her young. She tolerates nobody else.
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
- **The Wildsteam** hold a seat on this coast, Bitterleaf, and make pilgrimage here: *"come here when all hope is
  lost, and you either die or return with hope found."* **The Deepwater vigil** watches the sea die from posts at
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
- **The decay cell,** as knowledge: learned here, built anywhere there is rot. On a ship that always has spoiled
  food and butchery waste, this is the stop's most lasting gain.
- **Scuttler meat, delta loam** (clean, fertile soil from the sickest ground), **delta salt, delta silt.**
- **Thessamor wood** from the mangals.
- *0.2.0:* **attar,** *"an expensive oil that restores beauty... the planet's loveliest luxury, pressed from its
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
`UNSETTLED`.

**What wears on the ship (owner's ruling of 2026-11-18: in 0.1.0, from what the sources already say).** **Brine.**
The surge is the sources' own statement of it: *"what you built on fresh ground may be standing in brine
tomorrow"*, and the review's phrase for a warden mother's shell is *"the only brine-proof plating on the planet"*,
which says what brine does to every other plate. A hull whose footing a surge has reached is salted, and salt
left on it goes on working.
- *The answer by position:* land toward the fresh end and read the gauge trees; the brine comes up the gradient,
  not from the sky.
- *The answer by hand:* clean the crust off after a surge. (New, small work; no source describes it.)
- *The answer by armour:* the brine-proof plate. It exists in one design idea that the owner did **not** choose on
  2026-10-02, before the ship lens and before he ruled that biomes wear on hulls. `NEEDS HIM` below.

The haze and the fever wear on the crew, not the ship, and are covered above.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Every map runs from a fresh end to a brine end, and ground, trees and water sort along it. | A generated map walked end to end. | Bands painted with nothing living sorted by them. |
| A surge comes without a schedule, actually wets ground and draws back, and moves the salt line; the gauge trees show how far. | A landed ship through two surges, one of which reaches it. | A repaint of colours with no water moved. A surge on a timer. |
| Brine that reaches unfloored crops kills them, and floors survive. | A planted patch and a floored patch in the surge's path. | |
| After each recession new flotsam lies in the root-lines, and it is real goods. | Comb the roots; wait for a surge; comb again. | A yard that was stocked once at the start and never again. Goods that appear on dry ground far from any root. |
| Some recessions leave sea young in cut-off pools; they cry and can be found; a crew member can carry one to connected water; left alone, the pool's end leaves something to read. | A recession that strands young, with and without anyone responding. | A pond that was always there. A young that vanishes with no sign. A recession that must strand young every time. |
| A stranded young can be held wet and sold to an ordinary trader for a notable price. | Hold one; a trader visits. | A sale that completes without a trader. A training order mistaken for a sale. |
| Where a warden mother is present, she keeps to water, defends her reach, tolerates a crew that returned her young, and never forgives a sale; harvesting inside her reach ends tolerance at once. | A map with a mother: return one young; then harvest inside and outside her reach. A second map: sell one. | A mother on every map. A mother on dry land. Tolerance that survives a sale. |
| The ground life is real: scuttlers in numbers, hunted by animals and by five plants that never take a person or a tame animal. | A generated map left to run with a pet walked past each predator plant. | |
| The rainbow blooms are harmless in every way. | Touch, harvest and eat near each. | |
| The haze never lifts and never rains, softens the light, and the air here makes people ill more often than elsewhere. | A stop of some weeks. | Rain. Clear sky. |
| A dead meter found on the map teaches the decay cell; a cell fed ordinary rot gives real power. | Find, study, build, feed with spoiled food, run a bench from it. | A cell that runs on nothing. |
| A hull a surge has reached is worn by salt until it is cleaned, and a ship landed above the surge's reach is not. | Two landings, one surge. | Wear with no brine. |

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

**0.1.0, the stop**
- The land: fertile mud, salt crust, mangal canopy, the fresh-to-brine gradient, the permanent haze and its
  sickness. (built)
- The surge moving the salt line, the gauge trees, crops lost to brine. (built, except that the surge does not
  yet move real water)
- Flotsam in the root-lines after every recession, and brined wrecks. (built; moved in, see `rewrite_choices.md`)
- Stranding pools, the changed young and their cry; carrying one back; holding and selling one to an ordinary
  trader. (built; the cry while carried is not)
- The warden mother where she occurs: water-bound, defending, tolerant after a return, unforgiving after a sale.
  (built)
- Scuttlers, plant predation, the swarm, the free nursery young, the ordinary predators, rainbow blooms and muck
  plants. (built)
- The found meter and the decay cell. (built; moved in)
- Brine on the hull, and its answers by position and by hand. (new, small)
- Canopy and haze as one step of cover from orbit. (new, small, by his card)

**0.2.0, the stop with company**
- Fever-forging: a disease survived sometimes leaves a lasting change; the five strange ones he chose. (part
  built)
- Young that tame themselves to a crew that has not harmed them, their guard and attack work, and the weaker
  watch a rescued nursery's young keeps. (built in part)
- Attar: the still, the oil, the glaze on artwork. (built)
- The spent cell's rotting bed and its ingredients; a cell that takes corpses and leaves bone. (built)
- The creatures' own tricks: the lastvine rearing and spitting acid, the duskfire's burning spit, the
  sharpshrimp healing, the siezer's lockjaw, the drake fermenting and drinking. (built)
- Buyers who come for a held young. (built)
- Fever passed by the swarm's touch. (unbuilt)

**Later (a crew that stays, a colony, or the campaign)**
- The mother dying of age and one of her young taking the nursery; the heir's guard.
- Canals that bring her water, and her, inland; a colony *"buying her protection with labour instead of
  location"*.
- Water-only hauling by tame young; trees bound to hosts and castings; plants that show when they have fed.
- The Recall of the Written-Off rite (the owner's pick of 2026-10-02; a second-version design by the census).
- Bitterleaf, the pilgrimage, the vigil's posts, the named nurseries: campaign layer.
- The arthropod harvest as an industry; delta loam as an export trade.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Any medicine from this place (*"we have given medicine many times today"*); any gene machine; rain; a tide on a
  clock; saying whose plagues these are.
- A rainbow bloom that harms (*"the rainbow flora never lies"*).
- The mother at the centre of the biome, and a mother on every map (his answer of 2026-11-10).
- The stranded as species of their own (they are a condition of the nursery's young).
- The grounded mother, the last dry deck, the scuttler appraisal, the first egg above water, the second-hand
  young, the mother's blind side (not chosen 2026-10-02); the Tide-reader boon (cut 2026-09-12); the pollination
  gate (cut).
- **Recommended for dropping, not yet his:** world scoring and rarity (there is no worldgen in any version); the
  map-wide manhunter lottery when a mother dies; the attar balm that changes injuries; the old medicinal mangrove
  harvest.

## NEEDS HIM

1. **The brine-proof plate.** On 2026-10-02 he chose the mother's price over the grounded mother: a dead warden
   mother's body as a reef of *"ship-grade hull plate"*, *"the only brine-proof plating on the planet"*, guarded
   by her young. That was before the ship lens and before his ruling that every biome wears on the hull and has
   an answer in shield, armour or hands. It is the only armour answer to brine in any source. *Not revived*
   (default: position and cleaning answer brine). *Revived for 0.2.0 or later:* scavenger against loyalty on the
   biome's own giant, and a plate worth carrying to every wet stop afterwards. Large build.
2. **The last dry deck.** Not chosen the same day: during a surge a flotsam crew retreats along the last roots to
   the landed ship, *"dragging two workshop frames, and asks for passage to Bitterleaf with its livelihood."* It
   was then one ship idea among five; under the lens it is the direct answer to "who else is here" and it is very
   Jawa on both sides of the ramp. *Not revived* (default). *0.2.0:* a medium build and a real cost in deck.
3. **Does a rescued young ever come aboard?** His words of 2026-09-23: *"now what when they love you but can only
   survive in the water?"* For a colony the answer was that they inherit their mother's nursery. A ship leaves.
   *They stay* (default: the stop ends with something in the channel watching the ship go, which may be the best
   moment the biome has). *They can be carried wet* in some hold fitting: a new system, and it turns an orphan
   into livestock.
