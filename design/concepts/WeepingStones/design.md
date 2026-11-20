# The Weeping Stones: the design, seen from the ship

**Status:** the one design document for the Weeping Stones biome (`RM_WeepingStones`, source
`src/RimMandrake/WeepingStones/`, with the companion `src/RimMandrake/OasisMaker/`), rewritten 2026-11-18 on the
owner's instruction to see every biome "through the lens of Utinni". It replaces the frozen definition sheet, the
two rosters, the "make it shine" options, the stocked-pool design, the bedazzle review and the cleanse proposal as
the place to read; what happened to every idea in them is in `design/concepts/WeepingStones/rewrite_choices.md`.
Nothing has been deleted yet. This is a design document only and it launches nothing. A second reader checked
it against every source on 2026-11-18 and corrected it where the sources said otherwise; the corrections are listed
at the top of the choices page.

**Who reads this next:** a Designer run on this concept is handed the list of files in
`design/concepts/WeepingStones/` (`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its
path by sitting here. Nothing in the pipeline reads it by name yet. The Weeping Stones has no locked sheet or tree;
its only pipeline material is the cleanse proposal of 2026-11-17, which this design supersedes and which was never
applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) or the special-mechanics review of 2026-10-22 found it in source; it
does not mean it has passed anything, except where a live result is named.

**Names.** This file uses the names the owner gave at the art sheet of 2026-10-10, which are the labels the game
shows: the *burra burra* (older documents: burrak), the *iaala* (karrek), the *fan eel* (vizhik), the *dewglider*
(kirruk), the *softstone* (the wild ikkal) and the *colossia*. Quotations from older documents keep the older
word.

---

## What this place is

> *"Stone that sweats on its cold faces, and everything alive or built crowding around to drink the wind."*
> (`weeping_stones.md`, header)

High pale stone standing in the path of a wet sea-wind on the hot side of the world. Most of it is *"bright, dry,
wind-scoured ridge and shoulder — but every cold shaded face of it weeps: thin black streaks of wet running down
white rock, moss and mat-growth crowding the seep lines, and here and there, where the catch is good enough, a true
pool with a green ring around it and a crowd at the water."* Water here *"is combed from moving air, never
rained"*, and one shape does the combing: *"a thin upright surface held into the airflow."* Plants grow as blades.
Animals carry crests and combs. So do the ancients' condenser machines, *"and at a distance you cannot tell the
relics from the living."*

> *"Bright dry stone and secret weeping shade, where every pool is a gathering. Keep the oasis healthy, or it
> breeds something wrong."* (owner, picked by card, 2026-10-20: the experience line)

And at the water there is a law. The owner's own passage, near-verbatim in the sheet: *"At the water, the truce
holds — completely. It is strangely sacred, especially for such a deeply dangerous world ... Even the Jawa — who
specialize in trade, profit, and salvaging things slightly before they were ready — feel it. If there is enough for
all, you take what you need and you leave."*

**Seen from the ship, this is the one stop of the whole run where the crew knows the manners.** The oasis string is
*"the bead-chain the desert roads follow"*, and the sheet says exactly how Jawa use it: *"pay-and-go, by doctrine
and temperament. The crawler parks at the margin, unfurls its comb-sails, and market-day happens at the water's
edge; nothing they raise claims the ground."* They have watered at pools like this all their lives, from the edge,
politely, with a crawler.

Now they are arriving from the sky in a huge stolen ship, with the Empire a week behind them, and
setting it down beside a pool where *"every big animal on the hot half of the world must come."* They know the
rule. They have never had to keep it with this much at stake, this close to this many teeth.

The crew are small, hooded, skittish and built for dry heat (`reconciled_lore/05_the_clan.md`). The heat, the
stone and the etiquette are home. The crowd is not.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28: *"around every 5-8 days, keep 'em running"*; ladder in
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked provisional): a probe
droid five to eight days after landing, then scouts with a spotter, a strike team, an ion cordon on the ship, a
breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if the one before
succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last: about a month, and that is the outer edge** (his ruling of 2026-11-18: the
numbers are *"the outer edge allowable for each biome"*). The ladder's arithmetic on open ground gives a probe on
day 5 to 8, a first real fight around day 12 to 20 and the bombardment around day 20 to 32 if the Empire wins
every step. Nothing here adds days. What the Weeping Stones does is make the days good: it is the kindest ground
in this design's five, and the place a battered crew comes to drink, eat, trade and mend. (`UNSETTLED`: whether a
ship parked at a pool that half the desert visits counts as loud to the search. If it does, every wait is halved
and the outer edge is about two weeks. The sources do not say.)

**Cover from orbit (his ruling of 2026-11-18: partial cover, by biome).** **None in clear air**, and clear
is about two thirds of the sky here. Fog is one step for as long as it stands, and fog is about a quarter of this
biome's weather (25 parts in 102 in the biome's own weather table), so a crew that waits can usually have a
fogged day. The
hot seep oases are a separate case: the sheet gives them *"ground-steam instead of fog"*, and steam is one step by
his ruling; whether a seep oasis map actually has standing steam is `UNMEASURED`. Overhangs hide people, not a
ship.

**Fuel (his ruling of 2026-11-18).** **Emergency-slow biomass only** from the land itself, and not much of that:
timber here is scattered, scraggly trees on rock rims. But this is the best place on the planet to do what his
ruling calls *"the intended motivation to have to trade constantly, very Jawa"*: **buy it.** Everyone on the
dayside comes to the water. The sheet's own list of who is found at an oasis runs to a dozen factions, and
*"market-day happens at the water's edge."* The crew arrives with a hold full of whatever the last stop was worth
and leaves with fuel. Who sells, and at what price, is campaign layer.

**What the place does to the ship (his ruling of 2026-11-18, in 0.1.0).** Little, and two things that are already
built. His ruling names *"Heat ... Rough weather ... Different kinds of shields or armor"*, and the frame for it
exists in `src/RimUtinni/ShipShields/`: an unshielded hull on a hazardous map loses structure slowly, faster after
some hours, with warning letters and never a hard stop.

- **Sandstorms.** Any weather that carries sand counts as a particulate hazard in that frame, and sandstorms are in
  this biome's sky (6 parts in 102). They are rare; while one blows, the hull wears. His answer of 2026-09-02 is
  the particulate screen: *"Light kinetic deflectors handle wind, ash, vapor, bio contamination, spores, smoke,
  sand, and rain damage completely as well as repels small animals."*
- **Killing heat, at the hottest oases only.** The frame's heat hazard begins at 58 °C outdoors. The old
  measurement of this biome puts the ninetieth tile at 57 °C and the hottest at 63.5 °C, so only the hot seep oases
  reach it. His answer is the thermal veil, which will *"reflect all external heat outward with a mild mirror
  sheen to the shield, but also reflect all internal heat inward, so the temperature slowly climbs anyway."* One
  generator holds one field at a time.
- On an ordinary tile in clear air or fog, nothing wears the hull. The review of 2026-10-02 says the Weeping
  Stones *"does nothing to your ship"*, and for most landings that stays true. (`UNMEASURED`: neither wear has
  been watched on a Weeping Stones map.)

**A proposal, not from any source: the ship weeps.** The first pass of this design invented one more wear, from
the sheet's physics (*"every cold shaded face of it weeps"*) and its palette (*"verdigris where metal meets
moss"*): a hull that stands here for weeks is a tall cold shaded face in a wet wind, so its shaded side films with
water, moss takes the seams, bare metal greens, and a basin set under the drip gives a trickle of water. It is
gentle and half a gift. No source contains it and nothing builds it. It is not in 0.1.0: an invented wear waits
for 0.2.0, and the two built wears answer his hull ruling (delegated call of 2026-11-19, `Answered on 2026-11-19`
4). It stays a proposal for 0.2.0.

---

## The first minutes

*"An oasis is heard before it is seen."* The sheet wrote the sound and nothing has built it: wind through the old
vane arrays making tones, *"each array its own chord, so each oasis has a name in sound before it has one in
words"*; drip-echo; the crowd at the pool. *"A dead oasis is silent — the first thing a traveler notices, and the
worst."*

From above, the tile is *"the most legible tile on the world"*: concentric rings, *"water, then green, then scrub,
then sand."* The ship has to come down on the dry shoulder outside the green. Everything at the water looks up.
Nothing leaves. A pool is the one place on Ash'karr where a ship landing is not a reason to stop drinking.

The campaign already has a line for this moment, in its Narrator's voice (`design/Jawa/worldbuilding/
sacred_sites_pass_1.md`; the hook that would speak it is not built): *"A single trembling drop holds itself
against the whole desert's want to drink it. The ship's hull throws its shadow across the water and does not
spill a drop of its own — a good beginning, and it is noticed as one."*

The ramp comes down into white glare and a wet wind. Blade-grass covers the hillside in tufts that all face one
way, *"like iron filings"*. On the shaded side of every rock there is a black wet streak and something green
holding on beside it. (The streak is owed: nothing known draws it today. The green is built.)

Then the crew walks down to the water, and into the densest crowd of large animals any of them has ever stood in.
The sheet calls it *"pilgrimage density"*. There are herds drinking in rotation. There is a placid
colossus with rain-fins fanned along its back. There are predators, drinking, a few steps from their prey. Nobody is
eating anybody.

Before the first hour is out the player should have seen three things without going looking: a wet black streak
down a shaded rock face with green beside it; predator and prey at the same water; and the crew standing in the
middle of it, very small, being ignored.

## The first day

- **The truce.** Inside a short distance of the water, nothing starts a hunt, and whoever lands the first guilty
  blow has every animal at the pool turn on them. The owner's words of 2026-09-24: *"I like that anyone fighting
  including raiders attacking you near the water get animal retribution. That's cool ... Don't fight back and the
  creatures will fight for you."* The engine can tell who started it, so defending oneself is not a breach.
- **The crew's own hands are the danger.** Jawa *"specialize in ... salvaging things slightly before they were
  ready."* Here the thing within reach is somebody's calf, somebody's kill or somebody's drinking place. A single
  nervous shot by a single crew member at the water is the worst thing that can happen on this map.
- **Water.** *"Reliable standing fresh water"*: the reason to come. The ship fills its tanks.
- **Shade.** The sun is the same one sun as everywhere, from the tile's own place on the planet; under an overhang
  at noon is where a person stays alive, and near the terminator the same overhang is worth nothing.
- **Forage.** Bladderquill, whose quills slosh when cut and bear a fruit that is *"food and drink in one object"*.
  Salvecomb, a single arched frond *"serrated along its windward edge like a comb's teeth"*, the medicine plant.
  A dewgourd, if someone else grew it: the owner's spec was *"a large melon like gourd that takes a long time to
  grow but is then worth a lot of food and keeps for a long time."*
- **The plants are a map of the water.** *"The flora is also the biome's plumbing diagram."* A weep-mat marks a
  wet face (*"a face without one is a face that has gone dry"*); a shadefern *"marks which side of a rock is the
  cold side"*; *"a dripfringe curtain over a dark mouth means water below."* A crew that has watered at these
  pools all its life reads them without being told.
- **Timber is scarce.** Two trees, both thin on the ground: the rockfinger, from his own brief (*"long terrible
  shadows from the rims of tall rocks… very scraggly and hardy"*; the roster adds *"you meet the shadow before
  the tree"*), and the talvessar, an ember-leaf tree he placed here on 2026-10-19.
- **The wild pool is gentle.** By his card of 2026-09-24 the nastiness is what pens breed: *"the pen makes the
  monster."* A line in a wild pool brings up the softstone, which *"a child can lift"*; the duul, *"the
  janitor"* (*"It is edible in the sense that most things are"*); the ullo, *"the wedding bell"*, whose
  *"light goes out in your hands"*; and now and then the vobbal, which stacks pebbles and offerings into towers
  in the shallows, and which *"some oases forbid catching."*
- **The fish.** His verdict of 2026-09-24 on the pool stock: *"Make the fish nasty and way too active. And some
  shouldn't be fish but alien beasts you really wonder if we should be eating."* The first crew member to put a
  hand into a pen finds out.

## The first week

- **Netting stock.** A wild pool holds a thin wild stock. A crew member with a net can take breeders: skarrin,
  *"a forearm-long pool fish that spends as much time above the water as in it"*; the iaala, *"a boiling crowd of
  little armored fish that hit thrown feed like one animal and leave nothing"*; the fan eel, *"never where
  you left it"*, which escapes. The net is thrown, and a fast fish can be out from under it before it lands. That
  is his ruling of 2026-10-07, not a defect: *"It's supposed to depend on how fast they are. Whether the net can
  hit the right place."*
- **A pen for the length of a stop.** A pen drawn over a stretch of pool beside the ship, stocked, fed and read.
  The owner's answer of 2026-11-10 on the routine: *"Care automatically; harvest only on orders. Use existing
  RimWorld animal tools for this work; do not invent new UI. Deliberate harvest orders protect breeding stock,
  while the player must notice overcrowding."* That is the rule to build to; today's workers harvest on their own and keep no reserve. Whatever the pen
  yields before the Empire arrives goes into the hold. (`UNSETTLED`: a stop's pen is small, and in a small pen the
  breeders that must be kept may already be a crowd. Nothing yet says which gives way.)
- **The ones that are not fish.** In the same water live the loomu, *"a cat-sized, boneless, dove-grey thing that
  ... repeats what it hears at the bank: the feed whistle, the wind through the vanes, a child's laugh, its
  keeper's name for it"*; the huldu, *"body-warm, with a pulse you can feel through the skin"*, which when lifted
  from the water *"grips the handler's forearm and presses close, and it shivers"*; and the ivvol, *"a
  doormat-sized floor-thing that knows the feed schedule better than the apprentice does."* The stocked-pool
  design's line for all three: *"They are the best eating in the biome. Everyone says so. Nobody says it
  comfortably."* Whoever cooks one and whoever eats one remembers doing it.
- **The pool reads back.** A healthy pen cuts rings on the water; a thin one is hungry; a silent one is in
  trouble. That is the design. Today the pen's state is a line of text when the pen is selected, and nothing is
  drawn on the water.
- **The vhorrin.** A pen left crowded or left to crash, because the crew was busy with something else, can turn
  out one fish that is *"the same stock, grown past the point where the pen can hold anything else"*. It eats the
  farm (as designed; the built vhorrin takes one fish's place and then eats nothing). It has to be culled,
  deliberately, and a culled vhorrin is a great deal of meat. Because care is automatic and harvest is on
  orders, a crew that only tends will crowd its own pen; in his words, *"the player must notice overcrowding."*
- **Who else is at the water.** Sillik on the wet faces, licking the film. A ssurr at the bank, crest-fan open,
  courting: *"harmless, spectacular, beloved."* Mirrik rising off the pool, *"the dew-smoke"*, really flying. A
  burra burra wallowing out a new basin. The tirbak, *"the walking cistern"*, the caravan mount of the oasis string.
  Out past the scrub, the vhakk, *"the warden"*, which *"never hunts at water"* and owns the approaches instead.
  *"Its patrol is the oasis's outermost wall."* (Its shipped description says the opposite, that it ambushes
  drinkers from the shallows; only the description changes, `Answered on 2026-11-19` 5.)
- **The road in and out is where things die.** *"Violence lives on the approaches and in scarcity, never at full
  water."* Errands away from the pool pass through the warden's ground.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The crowd.** *On screen:* five hooded figures threading between the legs of animals twenty times their
   size to fill a bucket, and one of the animals turning its head to watch. *Why it lands:* the crew has traded
   in sight of these animals for generations and has never once been underneath one.
2. **The first blow.** *On screen:* a crew member, startled, fires at the water's edge. Every head at the pool
   comes up at once and every animal there turns on the one who fired. *Why it is alarming:* the player has
   perhaps two seconds to get that Jawa up the ramp.
3. **The boil.** *On screen:* a handful of feed hits a stocked pen and the surface erupts; a handler pulls back
   an arm with rather less sleeve on it.
4. **The escape.** *On screen:* a fan eel leaves the pen, crosses wet stone on its gills, and is in the next pool
   before anyone has put down the bucket.
5. **The one that says your name.** *On screen:* a loomu in the seep-warm water at the bank gives a Jawa's own
   trading cry back to it, in its own voice, and then again. *Why it is funny, and then not:* it is on the menu.
6. **The one that holds on.** *On screen:* a huldu lifted for the pot grips the handler's arm and shivers, and
   the handler stands there.
7. **The vhorrin.** *On screen:* a pen that boiled with fish yesterday is silent, the gauge reads wrong, and
   there is one long shape in it, with pieces of the others floating.
8. **The fan-dancer.** *On screen:* a small reptile at the bank throws open a crest-fan as wide as it is long,
   rattles, and dances at another one, in the middle of the crew's bucket line.
9. **The warden's turn.** *On screen:* a hauler coming back along the approach with something low and
   blade-backed pacing it through the scrub, which stops, exactly, where the green begins.
10. **The ship weeps** (0.2.0, if the proposal is built). *On screen:* a week in, the hull's shaded flank has a black wet streak down it and a line
    of moss in a seam, and a sillik is licking it.

## When the Empire arrives

The sheet already says what the Empire is here: *"supplied, needs nothing local — and meters the water anyway where
it garrisons. Breaking the one law even enemies keep, as policy, is what makes the occupation legible at an oasis:
the metering station near the spaceport is despised past politics."*

- **The truce does not care whose blaster.** His ruling covers *"anyone fighting including raiders attacking
  you."* A strike team that opens fire inside the truce's reach has the whole pool on it: the herds, the
  predators and the walking cistern. The crew's best defence is a ship parked at the water's edge and a crew that
  does not shoot first.
- **And it cuts both ways.** A crew that fires the first shot from inside that reach gets the same answer. Fights
  the crew starts have to be started out on the dry shoulder.
- **The approaches belong to the warden.** A column walking in crosses its ground before it reaches the green.
- **There is nowhere to hide and nothing to hide behind but stone.** The fight is in the open, in glare, among
  overhangs.
- *0.2.0:* **if the old crab is here**, the pool it carries moves with it, and the truce with the pool.

## Who else attacks; who hates the Empire

- **Almost nobody attacks.** The sheet bans any predator whose hunting ground is the pool. What kills here kills
  on the road.
- **Everybody hates the Empire's meter.** The Deep Desert Tribes are *"the truce's zealots — the ones who execute
  toll-keepers."* The Deepwater Compact are the water's stewards. The Homestead farmers come to the pools *"for
  market, marriage, and the rituals."* Blackstar's hunters keep *"iron truce discipline — the kill happens on the
  road, never at the pool. A Blackstar team watering quietly means someone nearby is being hunted"*, and a crew
  with an Imperial price on it should think about who that is. All of these are faces the campaign puts at the
  water; none is placed by this biome, and whether any would fight the Empire beside a Jawa crew is `UNSETTLED`.
- **The claim law.** *"Making someone pay for water you do NOT live on is forbidden, alien, even cruel.
  Barbaric."* A crew that lands on an oasis for a month is not a settler and must not start acting like a
  toll-keeper. `UNSETTLED`: what the neighbours make of a ship that stays.

## What forces the crew out; what lets them stay

**Out, before the Empire:** very little, and that is the character of the stop.
- The crew breaking the truce, once.
- A pen gone wrong at the wrong moment.
- No cover at all from above.

**Stay, longer than the Empire would like:**
- Water, food that walks up to be netted, medicine on the rocks, shade under them.
- The truce as a wall the crew did not have to build.
- A market at the door for fuel and repairs.
- Nothing here that grows over the ship, sinks it, poisons it or eats it.

The Weeping Stones is where the run draws breath. The price is that everything here depends on the crew behaving
better than it is used to.

## What the crew takes away

- **Full water tanks.**
- **Fuel, bought.**
- **A hold of fish,** and the memory of what some of it was.
- **Iaala paste,** a ration *"that keeps"*, and **huldu fur,** which he called *"a trading commodity"*.
- **Breeding stock in a wet skin,** for the next water the crew can pen. The stocked-pool design's own picture:
  *"A colonist nets breeding stock at a strange oasis, carries it home in a wet skin."*
- **Medicine and keeping food:** salvecomb, bladder-fruit, a dewgourd.
- **A tirbak,** if one can be bought or tamed: a pack animal that carries its own water for days. (Tirbak and
  vellak walk in traders' caravans as pack beasts, which is where a crew buys one.)
- *0.2.0:* **the ancient condenser.** The Weeping Stones' named gift to the ship: the oldest stone-crab on the
  world carries a running ancient water machine, and a crew can cut it out. *"It weeps water with no power or fuel
  wherever it is installed."* One per world. As built it fills flasks that nothing yet drinks; its water gets a use aboard (`Answered on 2026-11-19` 2).
- *0.2.0:* **dewsilk,** from the cocoons of a tamed mirrik swarm: *"fiercely hydrophilic"*, the cloth of moisture
  cloaks and comb-sails.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Dry pale stone with wet shaded faces and green only at the seeps and pools; the hot seep oasis as the stated exception, a green ring on open flat ground. | A dew-country map and a seep map, looked at (a joint sitting). | A map that is green all over, or dry all over, fails. |
| Predators and prey drink at the same water; nothing starts a hunt near it. | A hungry predator and its prey at a full pool, wild and tamed. | The same pair far from water: the hunt happens. |
| Whoever lands the first guilty blow near the water is turned on by the animals there; defending oneself is not a breach. | A raider fires on a crew member at the pool; on another run the crew member fires first. | The defender who shoots back is not punished. The same shots on the dry shoulder draw no retribution. |
| Shade under an overhang protects from the sun where the sun is high. | A pawn in the open and one under an overhang, on a high-sun tile and on a low-sun tile. | No local heat field: the difference follows the sun's angle. |
| Wild pool stock can be netted alive and carried. | A handler nets a breeder from a wild pool and puts it in a pen. | A net that lands on the fish takes it; a fish that has moved off is missed, by his ruling of 2026-10-07. The animal that was netted is the animal in the pen. |
| A pen is cared for without orders and harvested only on orders, with existing animal tools; breeders are not sold off by accident. | A stocked, fed pen through the days of a stop with a harvest order given once. | A pen left with no reserve set must not be emptied by helpful workers. Real births, not repeated wild captures, are what count as a farm. |
| The pool's state can be read from the water before a loss: productive, thin, crowded, silent. | Four pens in the four states, looked at with the inspect pane closed (a joint sitting). | A fed, crowded pen must not look reassuring. |
| A mismanaged pen breeds a vhorrin, which eats the stock in its pen and leaves remains; culling it ends that and yields meat; the pen can recover. | Crowd one pen and starve another; cull; restock. | Save and reload with a vhorrin mid-meal. A well-kept pen never breeds one. |
| The fish are nasty: a pen bites the hand that feeds it, and one species escapes over wet stone by a route the player can see. | Feed a pen bare-handed; watch a fan eel pen. | The escaped eel is somewhere reachable, not gone. |
| Eating the ones that are not fish is remembered by the eater (built) and the cook (owed). | Two meals, one of murrin and one of huldu, served to the same pawns. | A callous eater does not mind. |
| The natives carry the comb and live their lives at the water; the real flyers really fly. | Sillik, ssurr, mirrik, burra burra, tirbak, vhakk, vellak and dewglider on one map; flight read from flight state. | The vhakk hunts on the approach and stops at the green. |
| An unshielded hull wears in a sandstorm and, at the hottest oases, in killing heat; a shielded one does not; on a mild tile in clear air or fog nothing wears it. | A ship parked through a sandstorm, shielded and unshielded; the same on a hot seep tile. | No wear on a mild tile in clear air. (If the weeping-hull proposal is taken it adds a row: the shaded side wets and greens, the sunlit side stays dry, and wiping it off works.) |

Settings: one switch per major feature, defaults as shipped, everything off leaves a dry bright upland with pools
and a lot of animals (standing rule, every mod).

## Shared machinery

**Featured here** (the Weeping Stones is where each is vital and should be proven):
- **A truce at water: no hunt starts inside its reach, and the first guilty blow is answered by every animal
  there** (in `EnvironmentalHazards`; any biome with a pool could carry it, and only here is it the law of the
  place).
- **Husbandry of things that live in water, in a pen drawn over the water** (the stocked pool: stock, feed, net,
  harvest, overdraw, cull, with `FlowWorks` under it).
- **A consequence that grows out of neglect and is cured by a deliberate act** (the vhorrin).
- **Food that leaves a memory in whoever cooked and ate it** (the doubt).
- **A creature that carries a place with it** (the walking condenser, 0.2.0: a pool and its truce wherever the
  oldest gorrask settles).

**Merely active here:** the one sun from geometry, with overhang shade (featured in the deep desert and the Long
Shade; here it is simply true); real flight; thirst and carried water; fishing; plants that follow wet ground
(`ExplosiveGrowth`'s wet-native growth); the oasis landmark and its companion loadouts (campaign world state: 186
pools placed and named by hand); the huge-things engine, for the gorrask as a landform; the oasis-maker machine
(its own mod); bones; wreck salvage; the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket.

**The one signature (his first-version answer of 2026-11-19): NOT CHOSEN YET; two candidates, listed for the
Conductor.** His experience line holds both: *"Bright dry stone and secret weeping shade, where every pool is a
gathering. Keep the oasis healthy, or it breeds something wrong."*
- *The truce at the water:* no hunt at full water, and retribution for the first guilty blow, for crew, raiders and
  Empire alike. A normal stop is sure to see it: the ship's water is the pool, and the crowd is already drinking
  there when the crew arrives.
- *The pen:* stocked pool care for the length of a stop, the readable water, the nasty fish, and the vhorrin when it
  goes wrong. It is his line's second half and the cleanse's signature (2026-11-17); this design keeps it for the
  length of a stop, but a vhorrin needs mismanagement over time, so a stop sees it only if the crew stocks a pen.
If the truce is chosen, the pen, the netting of live stock, the ones that are not fish and the vhorrin move to
0.2.0 with their rows. If the pen is chosen, the truce stays as life (how the animals at the water behave).

**0.1.0, the stop**
- The land: dry stone, weeping shaded faces, green pool margins, the open seep exception; clear and windy, fog,
  the odd sandstorm; no rain, no snow. (the ground, pools, plants and weather are built; nothing known draws the wet
  streak on the stone, which is owed)
- The one sun with overhang shade. (built; the cleanse found local heat fields and arrival advice that contradict
  the later roof-and-parasol ruling, to be corrected)
- The truce: no hunt at full water, and retribution for the first guilty blow, for crew, raiders and Empire
  alike. (built, never seen live)
- The cast as animals with ordinary lives: sillik, mirrik, ssurr, tirbak, burra burra, vhakk, vellak, dewglider,
  colossia, the murrin, the gorrask as an animal, with the campaign's eight canon beasts where the patch puts them.
  (built; the mirrik is missing from the biome's animal list and no other route onto the map is known; the vhakk's
  shipped description contradicts the ambush ban)
- The plants: dewblade, weep-mat, verdimoss, shadefern, bladderquill and its fruit, salvecomb, rockfinger, talvessar,
  dripfringe, steamfrond and its korrim spice, dewgourd. (built)
- Fishing for the six gentle wild fish, and netting live stock with a thrown net that a fast fish can escape, by
  his ruling. (built; the net job failed its last recorded live run, 2026-10-07, on another biome's map)
- The stocked pen for the length of a stop: care without orders, harvest on orders, the readable water, the
  nasty fish, the fan eel's escape. (built offline in part: the jobs exist, but harvest takes no orders and keeps
  no reserve, nothing is drawn on the water, and the escape is a silent move to dry ground)
- The ones that are not fish, and the doubt. (built for the eater; the cook's memory is not)
- The vhorrin, its cull and the pen's recovery. (built offline: it appears and can be culled; it does not yet eat
  the stock, and recovery is unproven)
- Water for the ship. (built by being water)
- Hull wear from sandstorms and, at the hottest oases, from heat, answered by his shields. (built in
  `src/RimUtinni/ShipShields/`; never watched here)
- No cover in clear air; fog as one step. (owed, small)

**0.2.0, the stop with company**
- The ship's shaded side weeping. (a proposal of this design, in no source; out of 0.1.0 by the delegated call of
  2026-11-19)
- The walking condenser: the oldest gorrask, the pool that forms round it for a season and dries when it leaves,
  and the three choices (guide it, sell where it goes next, or cut the machine out for the ship). (built; a closed
  item records the pool forming and the three choices firing end to end, from a debug spawn. As built the sale
  pays at once and delivers nothing, and the cut kills the crab without the truce answering)
- Its two quests, each closing the other: the Hutts' capture for the Arena, or keeping it free with the moisture
  farmers against hunters. (built, never run)
- Dewsilk from a tamed mirrik swarm's cocoons. (built)
- Rare catches from the pools. (built in part)
- The burra burra's dug basins becoming new small pools. (not built)
- The loomu doing anything with what it repeats; the special ways the pool beasts are caught. (not built)
- Sound: each oasis's own chord from its vanes, and silence at a dead one. (not built)
- The ship's acoustic scanner readings here. (built)

**Later (a crew that stays, a colony, or the campaign layer)**
- The oasis-maker: an ancient machine that grows a pool ring by ring beside shaded rock, *"a treasure type"*. His
  own words when he asked for it: *"Unfortunately it's not very important for the Jawa utinni scenario but it's a
  nice mod component."* Later the same day he added that they are *"sold but very expensive. Same tech as moisture
  farming itself."*
- The recapture ladder: condenser fins, shade-lids, cistern shafts, the servo-vented enclosure, *"the visible
  endgame of desert wealth."* The ancient vane arrays as salvage, and the named condensers as things a scavenger can
  repair (his ruling of 2026-10-03: *"it's a scavenger game, so this really should be honored"*).
- The pen as a farm across seasons: retained breeders, repeated surplus, the annual lockout.
- The faction faces at the water, the 186 named pools and their loadouts, the Hutt palaces, the Imperial metering
  station: campaign.
- The Refused Toll (his words: *"This is pretty cool ... Gotta do it."*), deferred with all rites on 2026-10-23 and
  blocked on a kind of site that does not exist yet.
- Pilgrim and courtship choreography at the pools. Truce-stones and Oomo tokens.
- The four close misses of 2026-10-02 (the fish walk, the pilgrim passage through the ship, the dewsilk casket,
  the fish that lies), recorded by his ruling as *"close misses"*, not dead and not to be pitched again as new. The
  pilgrim passage, a ship idea, stays down by his answer of 2026-11-19; he can bring it back by name.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Wind-hour (*"nah."*) and the born-and-dying water (*"nah too much."*), both dead by his word, 2026-09-24.
- Restorable vane arrays in four states (redirected into the oasis-maker the same day). The four-state draft only:
  a condenser a scavenger can repair is kept, under "later", by his ruling of 2026-10-03.
- Ambrosia at the pools (cut by his card, 2026-10-19, after his art note of 2026-10-10 had asked for it to be
  special).
- The truce as diplomacy or neutral ground (redirected into animal retribution the same day).
- An ambush predator at the pool margin; a toll on unsettled water; any native without the comb; rain-fed
  ecology; snow (sheet bans).
- The last caravan and the crab on the hatch (not chosen 2026-10-02). The Open Water rite (not chosen).
- Earth palms at our oases.
- **Recommended for dropping, not yet his:** the ivvol's proposed immunity to the vhorrin (the cleanse's
  recommendation: it removes the consequence of bad husbandry).

## NEEDS HIM

None open. Every entry is answered (next section).

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

2. **[other] Cutting the machine out of the crab, and what its water is for.** One of three choices in 0.2.0, and its
   water gets a use aboard (the design's default). *Delegated call.*
4. **[hull] The weeping hull.** Out of 0.1.0: it is in no source. The built sandstorm and heat wears answer his hull
   ruling (*"It's in there."*). It stays a proposal for 0.2.0. **This changes the design's default.** Was: a gentle
   third wear in 0.1.0. Undo: set this answer back to the third wear in 0.1.0. *Delegated call.*
5. **[other] The vhakk: his picture against his ban.** It looks as he asked and behaves as the ban says: it lies in
   the shallows and watches, and hunts only on the approaches. Only the description changes (the design's default).
   *Delegated call.*
6. **[scope] The ivvol's protection.** Farmers' belief only (the design's default). *Delegated call.*
7. **[cover] Is a ship at a crowded pool loud?** Not loud (the design's default). *Delegated call.*

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

1. **[scope] Is the pen still the signature, for a ship?** *His card of 2026-11-19 (first version):* 0.1.0 holds one
   signature that a normal stop is sure to see. Whether it is the truce or the pen is not obvious from this design
   and his words, so both are listed for the Conductor (Scope, top). Until the choice is made the split stays as
   written.
3. **[scope] The pilgrim passage.** *His card of 2026-11-19 (declined ship ideas):* it stays declined, as he typed
   on 2026-10-02 (*"None of these. Close misses."*). He can bring it back by name.
