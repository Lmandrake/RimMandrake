# The Cauldron: the design, seen from the ship

**Status:** the one design document for the Cauldron biome (`RM_Cauldron`, source `src/RimMandrake/Cauldron/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the
older definition sheet, cast bible, reviews, pitches and the cleanse proposal as the place to read; what happened to
every idea in them is in `design/concepts/Cauldron/rewrite_choices.md`. Nothing has been deleted yet. The Cauldron is
one of the six biome mods HELD BY OWNER: this is a design document only and it launches nothing.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/Cauldron/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. Unlike most biomes the Cauldron has a Designer tree: an adopted root (`root.md`),
a locked sheet of seventeen leaves (`sheet.md`), thirty-five planned scenes and a passed exam, all written for a
forty-colonist settlement. This design keeps the root's experience and re-aims it at a ship that stays weeks; the
tree should be re-cut from this file, and until it is, the two disagree on scope and this file says where.
**The locked sheet, root and tree describe a colony that stays and are NOT edited by this rewrite or by its second
reader;** a later Designer run reconciles them.

**Second reader, 2026-11-18:** a second agent that did not write this page read the six older biome files and the
roster whole and repaired it. The hull section now rests on the owner's own words of 2026-10-09 and cites the built
shield frame; the scab question now carries the related idea he declined; the suush's burst rests on his words; and
the art law now says green is allowed in dewfall, as he ruled. What changed and why is at the top of
`rewrite_choices.md`.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) or the mechanics review of 2026-10-22 found it in source; it does not
mean it has passed anything.

**What kind of place:** land. A low forest on the terminator, in permanent dusk (checked against the sheet's own
header: *"terminator not deep nightside · scattered twilight"*, median +11.4 °C, *"Water tiles 0, river tiles 0"*).
It is not a sea, it is not dark, and the ship lands on it like any ground.

---

## What this place is

> *"The sky roils with eternal anger and lightning yet no rain ever falls. Water is acid, animals are minerals, and
> life twists under the load… including you."* (owner, typed 2026-10-20)

> *"A forest slowly turning into a smelter, lit like a dawn that never arrives."* (`cauldron.md` §9)

*"A low, wet-black forest standing in permanent dusk over ground that breathes."* The terminator is where the
dayside's scorched crust meets the nightside's hoarded volatiles, and where they touch they react. There is no
volcano and no heat: *"It's all about the chemistry at the local site, not anything heat-based."* The ground
exhales metal-rich gas through vents. The trees live on it, cannot get rid of the metal, and push it out into
their own bark: *"The poison is not a weapon. It is metabolic waste, and the tree is slowly plating itself in its
own tailings."* An old trunk is *"part tree, part slag heap."* Everything alive is *"either sealed or poisoned. There is no third strategy."* The pools look like water
and are not.

**Seen from the ship, this is the richest scrapyard the crew has ever landed in, and it is alive.** The sheet says
so in as many words: bio-accumulated metal is *"the biome's whole reason to exist for a scavenger clan — paid for in
exposure."* The trees are steel you fell. The ruins are other people's failed industry, *"corroded, not
sand-blasted"*, with *"a water tank hauled in from somewhere else"* standing in them. The vents are free gas with a
hole to cap. A Jawa looks at all of it and sees stock. What the Jawa is wearing is a cloth robe and a hood, and the
rule here is sealed or poisoned.

The owner's answers of 2026-11-10 fix what the place costs: *"heavy metal poisoning requires advanced medicine to
purge, never on its own. Acid disfigures and harms sensory organs permanently."* And what a gas fire is: *"absolutely
it should be dramatic and should blow back items like an explosion."* The load a crew member takes here leaves with
the ship. That is the biome's own sentence: *"including you."*

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid, then scouts with a spotter, a strike team, an ion cordon on the ship, a breaching
assault, and an orbital bombardment that cannot be fought. Each step comes only if the one before succeeded; a loud
crew halves every wait and a hidden one doubles it.

**Cover from orbit here: partial, from the sky.** The Cauldron has no canopy (*"each trunk carries a crown of fine
chemical fronds"*) and its dusk is light, not dark. What it has is his own first sentence, a sky that *"roils with
eternal anger"*, and the vapour bank, chemical fog off the vents. By the card of 2026-11-18 that is worth one step:
the search here runs one visibility band quieter than on open sand. It is owed work; the pursuit's built list of
slowed biomes holds the Abyss alone.

**How long a stop lasts (the outer edge).** On the ladder's arithmetic one step quieter stretches the open-ground
five to eight days to about seven to eleven: a first probe in the second week, a first real fight in the fourth,
the cordon soon after, and the bombardment somewhere between about **four and a half and seven weeks** if the crew
wins every fight on the way. That is the outer edge. The place sets a nearer one: every bloom caught outdoors adds
to a load that does not come off, and the ship's water lasts only until the crew can filter its own. Most stops
should be a week or two of fast, greedy work. `UNSETTLED`: how much water the ship carries.

A season is fifteen days. The forest's renewal (rhossak rooting new groves) and anything that needs the trees to
grow back are not in 0.1.0 or 0.2.0.

---

## The first minutes

The approach is through the anger: a rainless sky full of lightning. `UNSETTLED`: whether the descent itself is
rough (see "What the place does to the ship").

On the ground the light *"never changes and never comes from anywhere"*: no shadows, no noon, a dawn that will not
resolve. *"Your eyes never adapt because there is nothing to adapt to."* It is faintly brighter toward the star,
*"the only way the player can tell which way the sun is."* The soil is black and slate, ringed with mineral stain. The trunks are bone-pale and streaked with grey
metal tears. Somewhere close a vent is puffing visibly, steadily, like something breathing. There are pools. Nothing
is green: *"Anything green is a visitor, a mistake, or dying."* (One exception, his ruling of 2026-10-03: the law
lifts during dewfall, when the dew itself may flash green-amber.)

Before the first hour is out the player should have learned three things by looking and by inspecting, without a
worker being hurt: which trunks carry metal (flecks on the bark, and an assay on inspection); that the pools are
chemistry and not drink; and where the nearest vent is and that it is active.

A translucent gasbag drifts past the hatch at head height. It is docile. It is a suush. Do not shoot it. His words
when he asked for it (2026-09-26): it *"floats around the Cauldron feasting on the strange chemistry of its roiling
atmosphere and... detonates when you shoot it... Make it both disturbing and beautiful... Docile, tamable, bizarre."*

## The first day

- **The trees are ore.** Felling a thornwood is slow, exposed work and pays wood and metal together, more from the
  older, scabbier trunks. Ruled 2026-09-28: *"metal-infused trees are slow to fell, yield growth-scaled metal."*
  This is what the stop is for.
- **Under the hull or in a suit.** The air itself burns: an unsealed, unroofed body takes acid every hour it stands
  outside, bloom or no bloom, whatever its faction; only the natives are spared. A roof stops what comes out of the
  air. So does a complete environmental seal (the mod has a suit and helmet in vexxith to craft; his words:
  *"Environmental/vacsuits will protect the players of course"*). A robe does not. Direct contact with a pool, and
  smoke from a gas fire, are separate dangers that a roof does nothing about.
- **Where the ship sits.** The bloom's dose is *"strongest near vents, not a whole-map toxin tax"*, and the vents
  are leaking, stable or lately blown out. Setting down away from the leaking ones, and capping the near ones
  first, is the first plan of the stop.
- **The water problem.** Nothing here can be drunk. *"The one thing this wet-looking place cannot give you is a
  drink."* The crew is on ship's water until it has a filter running.
- **The falter.** Before a bloom the vents' breathing visibly drops off, a message says so, and the small native
  animals near them go still. From that moment there is about an in-game hour (his choice, recorded in the
  locked sheet's falter leaf) before the air loads everything outdoors with metal. *"When the eskith stop answering
  each other, the old hands are already walking for the roof."*
- **The gas.** An uncapped vent leaks a visible, flammable cloud that pools and drifts. One spark and it carries
  fire along every connected patch of gas, over water as easily as ground, with toxic smoke and blasts that throw
  loose goods. A gap with no gas in it, or a sealed wall, stops it; a pond does not. The cloud rides the wind, on a
  heading that changes by the day, so the crew can see which way it will go. The dry storms overhead are real
  lightning, and lightning is a spark.
- **The ruin.** One corroded works stands on the map: wellhead, condenser stack, dead tanks, broken pipe, a spent
  filter cartridge. It is salvage, and studying its rig in place is how the crew learns to build its own.
- **Food that bites back.** Every animal's meat is toxic and prized; the sulphur-yellow tsevrix (*"a spill of wet
  lanterns that give no light"*) roasts into something safe, *"the only plant food in a biome whose meat is all
  poison"*, and *"only to a camp with a fire"*; selvix is the local medicine herb. None of it is a larder, and the
  one meal needs the one thing the giant punishes.

## The first week

- **Cap and filter.** A gas-tap scaffold on a vent stops that vent's leak and banks condensate: *"a scavenger's
  answer to a hole in the world that breathes fire: a clamped scaffold of salvage steel."* A powered,
  cartridge-fed Filter-Works turns condensate into saleable reagent and toxic or acid water into water the crew can
  drink. This is the point at which a stop can last. The cartridges are local craft and local salvage: *"crushed
  crust-mineral, frond-felt from the xithess crowns, a wax seal at each end. Spent ones turn the colour of what
  they caught. The ruins are full of spent ones."* And the scaffold has a rival: *"Every scaffold in the forest has
  pry-marks on it, because something out there prefers to drink from the tap."*
- **Fuel.** Xithess, the pale filter-frond plant, harvests straight to chemfuel, *"a fistful of the forest's own
  refinery"*; the amber sessarix resin boil does the same.
- **The giant has opinions.** The vexxiss is *"a hill of slag that moves"*, eyeless and slow. It drinks vents dry
  for a while, pries ordinary taps off the ones it wants, and *"hates fire the way a lung hates smoke"*: it comes
  for whoever lit one and beats the fire out. A vent it has drunk stays quiet for days and then visibly recovers.
  Tame, it can be sheared for vexxith, plate that acid and heat do nothing to; only a living one gives it (*"a
  kill wastes the lode... a corpse's plates crumble"*), which is the whole reason not to shoot the fire marshal.
- **Bound herds.** Rhossak keep to the grove they are bound to and read as bound; the galled ones carry edible
  galls.
- **The ledger.** By the end of a week the Health tab is the story of the stop: who was outside in the second
  bloom, who put a hand in a pool. Ordinary tending does not shift the metal. An advanced-medicine purge does, and
  the medicine is not made here.
- **The hull.** Exposed parts of the ship have been burning slowly in the acid air since landing, with one warning.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The balloon.** *On screen:* a docile floating gasbag drifts over the salvage pile; someone shoots it; it goes
   off as a cloud of toxic gas over the whole work party. *Why it is funny:* it was not doing anything. The source's
   own summary: *"one joke with a fuse on it."* It can be tamed, and a crew that tames one has a pet that must
   never be shot at, aboard a ship the Empire shoots at.
2. **The yard goes up.** *On screen:* a spark at one end of a low haze; fire runs the length of it and across a
   pool, and the blast throws a week of stacked salvage in every direction. *"Blow back items like an explosion."*
   For people whose wealth is piles, this is the worst thing that can be shown. The blast throws eligible pawns
   too, and a Jawa is small.
3. **The fire marshal.** *On screen:* a Jawa lights a cooking fire to roast the tsevrix. A hill gets up, walks
   over without hurry, stamps the fire out and then turns to the cook. (The enrichment spec gave it a bellow and a
   readable "bellows" sign so the player knows before it turns; the sound is out, the sign is worth keeping.)
4. **Everything stops.** *On screen:* the vents' puffs thin out, the drummers freeze mid-step, the floating things
   hang still, and a line of hooded figures drops what it is carrying and runs for the ramp.
5. **The tree pays.** *On screen:* a pale trunk comes down at last and what spills out with the wood is steel.
6. **It pulled the tap off.** *On screen:* the crew's first scaffold, two days' work, levered off its vent by a
   vexxiss that wanted a drink.
7. **Shearing day.** *On screen:* small figures on the flank of a tame giant, cutting plate. *"The trick is not
   the climbing. The trick is doing it without warming the shears."*
8. **The delicacy.** *On screen:* the butcher in gloves to the elbow; the meal that follows; the crew member who
   ate the unroasted one.
9. **The face.** *On screen:* a crew member who reached into a pool, healed, and is not the same. Alarming, and
   permanent: this one should sting.
10. **The ship is rusting.** *On screen:* the one-time warning, and damage ticking on the hull's exposed parts
    until someone rigs a liner.

## When the Empire arrives

- **The air does not take sides.** His words (2026-10-09): *"raids from the empire suffer constant slow damage from
  that ambient acidity when they raid the players there."* Ambient acid and the bloom fall on every unsealed body
  of every faction. `UNMEASURED`: whether Imperial armour counts by its stats as a full seal. If it does, the
  build contradicts his sentence, and his sentence wins (`Answered on 2026-11-19` 2, below).
- **Blasters are sparks.** A firefight in vent haze is a firefight in fuel. The crew chose which vents to cap, so
  the crew knows where the gas lies, and a line of troopers advancing through an uncapped hollow is standing in
  it. Lightning lights it too.
- **The fire marshal again.** The vexxiss goes for whoever ignited. It spares nobody's side but its own.
- **A siege sits in the weather.** The cordon's emplacement has to stand two days in the open. Two days is long
  enough for a bloom.
- **The fog.** In a vapour bank sightlines close; the probe and the spotter each have to *see* the ship.
- **The crew's own stores.** The same gas chain that scatters a siege camp scatters the salvage yard. Where the
  crew stacked things decides who loses more.

## Who else attacks; who hates the Empire

- **The fast imports.** Seven outside animals were wired in on his word (*"Wire and keep"*, 2026-09-28), the ripper
  hound among them, against the sheet's own *"nothing fast"*. They are the things that chase.
- **Ambushers.** The forest's own predators wait; the bedbug bites, the floating garsulix hunts.
- **The vexxiss,** if provoked with fire, or over a vent.
- **Nobody lives here, but somebody works here.** *"Whoever came before came for the metal and the gas, and had to
  bring their own water."* The item descriptions name the Farmers five times: they cap vents (*"The Farmers cap
  them. The forest keeps making more"*) and build small shrines to the river god. No source gives them a
  settlement or a trader on the ground, so none is promised; a Farmer work party met at a wellhead would be new
  content. Nothing here hates the Empire in particular; the vexxiss hates fire, and the Empire brings a great deal
  of it.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- Water, until the filter runs.
- The load: each exposure is permanent until purged, and the purge needs medicine the crew must have brought or
  bought.
- A gas fire through the stores.
- The hull, if nobody lines it.

**Stay, longer than the Empire would like:**
- A sky that slows the search by a step.
- Filter-Works: water, and reagent to sell.
- Capped vents near the ship and uncapped ones where visitors will walk.
- Vexxith, for whatever must stand in the acid.

## What the crew takes away

- **Metal,** by the tree-load. The best reason to come.
- **Reagent** from condensate, the thing this stop makes that other people pay for. With it the crew buys what it
  cannot make: medicine first.
- **Fuel:** the slow route, and buying elsewhere (his fuel answer of 2026-11-19: the Cauldron is not one of the
  richer sources). Xithess crowns and sessarix resin are biomass for the slow route. Nobody on the ground sells
  fuel. The richer reading is kept in the 0.2.0 list as text.
- **Toxic prized meat,** *"the things a cook brags about surviving."*
- **Vexxith,** *"everything made from it outlives the argument, the forge, and the smith."*
- **The knowledge of filtering,** which works anywhere there is bad water.
- **The load,** in whoever was careless. It comes too.

## What the place does to the ship

His ruling (card, 2026-11-18) names this biome's wear first after heat: *"Heat. Acid."* The wear below is his
own, said a month earlier, and it is built. This design adds no hull system and proposes no wear of its own.

- **Acid air on the hull (his words, built).** 2026-10-09: *"the Forge and Cauldron have ambient acidic
  environments that would constantly damage the ship and even players, but materials like this allow the ship to
  exist there without such damage."* Built in `src/RimMandrake/Cauldron/Source/RM_AcidAir.cs`: a player building
  on the ship's substructure under open sky is sampled hourly and burns down toward a floor and no further, with
  one message (*"The air here is eating the ship's hull. Vexxith plate or a hull liner rig will stop it."*). The
  Forge shares the service. The armour answers are his: vexxith parts take none, and the biome's deck part, the
  hull liner rig, *"glazes the whole ship's skin against acid, from ground vexxith plate"*
  (`BIOME_SHIP_CONTRIBUTIONS_1`). So the hull's answer runs through the living giant.
- **How it sits with the shield frame.** The shared frame is `src/RimUtinni/ShipShields/` (his shield rulings of
  2026-09-02). It already sees the Cauldron: the frame's particulate hazard reads a fouled-air mark, and a patch
  that ships with the Warscar mod puts that mark on the Wastes, the Cauldron and the Contagion
  (`src/RimMandrake/Scarlands/Patches/RM_AerosolScreen_PollutedBiomes.xml`). So an unscreened ship here takes two
  wears at once: the frame's slow fouling of the things at the ship, which a shield in particulate mode stops, and
  the Cauldron's own acid sampler on the substructure, which lives in the free tier and which only vexxith plate
  or the liner answers. His words give the light screen *"wind, ash, vapor, bio contamination, spores, smoke, sand,
  and rain damage completely"*. Whether a raised screen should also quiet the acid sampler is `UNSETTLED`; folding
  the sampler under the frame is owed shared work.
- **Hands-on work.** An older pitch that he neither took nor struck on 2026-09-28: the ship *"becomes the biome's
  newest tree"*, growing crystal scab that is scrubbed off for trace metal. It is not built and not promised.
  Two days later he declined GPT's extension of it by name. It stays down (his answer of 2026-11-19).
- **The approach.** His ruling names *"rough weather turbulence in the approach"* among the ways biomes wear on a
  ship, and this is the biome with the angry sky. No Cauldron source describes a rough descent, so none is promised
  here; it belongs to whatever shared rule covers storm approaches.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A rainless mineral forest in even dusk: dark soils, pale metal-streaked trunks, chemical fog, lightning, no green. | A fresh map through a cycle of its weathers. | Rain or snow ever falling fails it. |
| The vents quiet, a message says so, and nearby small natives go still, about an hour before a bloom. | An active vent with eskith and a suush near it, run into a bloom; a worker walks to shelter on the cue. | A map with no animals still warns. A capped vent warns by message. |
| A roof or a full seal stops what the air does; a robe does not; pool contact and smoke are separate. | Four pawns through one bloom: roofed, sealed, robed, and roofed but wading. | An acid-proof coat on an unsealed wearer protects the coat. |
| Metal load stays through care, travel and reload, and only an advanced-medicine purge removes it. | A loaded pawn tended, flown to another map, saved and loaded, then purged. | Ordinary tending and waiting change nothing, however long. |
| Acid can leave permanent facial and sensory damage after ordinary healing. | A burn that heals; the Health tab after. | A scar label with no capacity change is not it. |
| Slow thornwood felling pays wood and metal, more from older trunks. | An old and a young trunk felled; an interrupted felling. | The interrupted job pays nothing. |
| The native animals and plants feed, breed and pay what they are said to pay; the meat is toxic unless prepared. | A week of ordinary husbandry and foraging. | |
| The exposed hull burns slowly in the acid air until lined. | The ship through several days, with and without the liner. | Vexxith parts take none. |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The pools are what they are through contact, filling, pumping and filtering. | A pawn wades, a tank is filled, the tank is filtered, the output is drunk. | A coloured pool, or a tank filled by hand for the test, proves nothing about delivered water. |
| One spark carries through connected gas, over water, and stops at a gas-free gap and at a sealed wall; a save mid-burn resumes burning. | A gas field across a pond with one gap and one walled corner; ignite; save halfway. | The pond does not stop it. |
| A gas blast visibly throws nearby loose goods. | Stacks beside an ignited pocket. | Goods that move with no visible blast, or a blast that moves nothing, both fail. |
| A tap stops its vent and banks condensate; a powered Filter-Works makes reagent from it and drinking water from bad water, and says why when it stops. | Tap, tank, works; run it short of power, cartridges and room in turn. | Stored stock never silently disappears. |
| The ruin is on the map, can be stripped, and its rig can be studied to learn the works. | A fresh map; study to completion. | |
| Shooting a suush sets it off as a gas blast. | One shot, one punched. | Melee does not start it. |
| A wild vexxiss drinks a vent quiet, pries an ordinary tap, and goes for whoever lit a fire and puts it out; tame, it shears for vexxith. | A vent, a tap and a lit fire near a wild one; a tame one sheared. | It never attacks its own faction's fire-lighter. |
| Rhossak keep to their grove and say so; galled ones give edible galls. | A bound herd with its tree, then with the tree felled. | With no tree left they read as unbound animals; none disappears. |

Settings: one switch per major feature, defaults as shipped, everything off leaves a dim wet forest with ordinary
animals (standing rule, every mod). The suush's flight is checked by reading its flight state, never by watching it
unattended (standing rule).

## Shared machinery

**Featured here** (the Cauldron is where each is vital and should be proven):
- **Gas that pools, drifts and burns as a chain** (`RM_VentGas`, `RM_VentGasKernel`, about 1,280 lines, the
  largest system in the mod).
- **Blasts that throw goods** (`ExplosiveKnockback`, designed on his instruction after this biome's answer).
- **Air that harms the unsealed, with a warning first** (`RM_AcidAir`, `RM_VentBloomExposure`, the falter).
- **One fluid filtered into another** (Filter-Works on `FlowWorks` liquids).
- **A landed ship worn by the air** (the acid-hull sampler and its liner).
- **Trees that pay a second material** (`RM_CompMetalYield`).

**Merely active here:** a home tether for animals (the rhossak's grove binding rides it); creature tracks
(`CreatureBehaviors`); stalled low-light growth (`ExplosiveGrowth`'s services); the one sun from geometry, which at
the terminator contributes little, with the vents chemical and not hot; exposure from weather
(`EnvironmentalHazards`); real flight; wreck salvage; the acoustic sounder; the Empire's search and the visibility
dial; the Scarlands' aerosol screen, which answers this biome's air next door.

## Scope

Every feature is in one bucket.

**The one signature (his first-version answer of 2026-11-19): the vent bloom.** The vents falter, a message says
so and the small natives go still; about an hour later the bloom poisons every unsealed body outdoors; a roof or a
full seal stops it, a robe does not; and the metal load it leaves stays until an advanced-medicine purge. *Why a
normal stop is sure to see it:* the bloom is one of the Cauldron's four ruled weathers and comes round on the vent
cycle, so a stop of days meets the falter and at least one bloom. His experience line: *"life twists under the load…
including you."* *Runner-up:* the gas that pools and burns as a chain (the largest system in the mod); it lost
because a stop can live through the bloom without ever lighting the gas.

**0.1.0, the stop**
- The land: the four ruled weathers (scatter-dusk, vent bloom, vapour bank, dewfall), dark soils, hazardous pools
  with real chemistry, vents. (built; pool identity through use is unproven)
- The falter, with the animals' stillness, about an hour ahead. (built; tied to the wrong clock today)
- Roof and full seal against the air. (built for acid; the bloom does not yet honour a full seal)
- Metal load that never clears itself and an advanced-medicine purge. (the load is built and wrongly decays; the
  purge is owed)
- Permanent acid injury. (owed)
- Thornwood felling for wood and metal, more from older trunks: an ordinary product of a native tree. (built)
- The native cast as ordinary animals and plants with their products; xithess and sessarix burn on the slow route.
  (built)
- The acid-worn hull and its liner. (built)

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The assay and the metal flecks. (built; seven fleck textures missing)
- Connected gas fire over water; thrown goods. (built; saving mid-burn is owed; throwing needs
  `ExplosiveKnockback`)
- Gas tap, tank, Filter-Works, cartridges. (built; four live checks passed 2026-10-21)
- The corroded ruin and study of its rig. (built; live checks passed 2026-10-21)
- The suush's burst. The vexxiss drinking vents, prying taps, warding fire; tame shearing for vexxith. (built)
- Rhossak binding and galls. (built)
*Already here before that answer:*
- *Not chosen as a richer source (his fuel answer of 2026-11-19); kept as text, his to bring back by name:*
  *"Xithess crowns and sessarix resin are chemfuel in the hand, with no refinery in between. It is not replete:
  the plants are picked, not pumped."*
- The vexxiss poisoning water it wades through, and its identifiable tracks. (built)
- Zisska fire-spit, bedbug paralysis, the garsulix's death blast, fexxil venom, kissaveth gas when cut. (built)
- Vexxith-lined tap and filter vessel; the plate-only door. (built)
- Dew beads and plants that flare in wrong colours in dewfall; flower rings that show a vent's state; nettles on
  poisoned shores. (built; five dew textures missing)
- The ship's acoustic sounder readings here. (built)

**Later (a crew that stays, or a colony)**
- The forty-colonist prepared day; a whole season of gas, sickness and labour holding together.
- Rhossak seeding plants and rooting new groves: the forest renewing itself.
- The age-based scab and crystal-fan coat on trunks.
- Refining shed ossrith crystal to uranium.
- The three rites (the Filtered Cup, the Engine Hour, the Capping) and Oomo's grudging shrine.
- A Farmer work party as an encounter (new here; the sources only name the Farmers in descriptions).

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- The bespoke soundscape, the engine underfoot as audio, directional hisses, the vexxiss bellow (sound out,
  2026-10-03). The seismograph (*"I don't like that idea."*, 2026-10-15).
- The exploding vexxiss (*"too many exploding giant beasts"*, 2026-09-28).
- Volcanism, steam, geysers, any heat source; green foliage; rain.
- The tile scorer and its rarity setting (worldgen is out in every version).
- The frozen sheet's bans on grazers and fast animals, for the seven imports he kept.
- The scab on the ship (*"neither adopted nor struck"*, 2026-09-28): it stays down by his answer of 2026-11-19 on
  declined ship ideas; he can bring it back by name.
- GPT's extensions he declined on the enrichment card of 2026-09-30, *"None of these thanks"*: Scabweight (the
  ship-scab extension), Pressure Lattice, ruin-learned filtercraft, Oomo's courtesy; and the Engine Below, not
  picked. *"The ruled versions of those features still stand... only GPT's extensions are out."*
- **Recommended for dropping, not yet his:** crystalmit bricks.

## NEEDS HIM


None open. Every entry is answered (next section).

Themes, for gathering these across biomes: 1 hull · 2 other · 3 locked-tree · 4 scope.

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

2. **Imperial armour and the acid air.** *His ruling:* his typed words of 2026-10-09: raids from the Empire *"suffer
   constant slow damage from that ambient acidity"*. His sentence wins: raiders burn whatever they wear, unless a unit
   is plainly a sealed machine.
3. **The locked tree is a settlement; this design is a stop.** *His ruling:* his word of 2026-11-18, *"Let's rewrite
   them all and let git be provenance."* Re-cut the tree from this file when the hold lifts.
4. **Oomo's shrine: in, or later?** *His ruling:* his ruling of 2026-11-17: *"The rituals. Little custom details that
   weren't strictly necessary. They absolutely should be, at minimum, moved to the next version if not retired
   outright."* It is later than the list of 2026-10-15. Later.

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

1. **Does the ship grow scabs?** *His card of 2026-11-19 (declined ship ideas):* they stay turned down. The built acid
   wear and its liner are the whole of what the place does to the hull. The scab is on the Dropped list; he can bring
   it back by name.
