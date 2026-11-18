# The Greentide: the design, seen from the ship

**Status:** the one design document for the Greentide biome (`RM_Greentide`, source `src/RimMandrake/Greentide/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the
older definition sheet, rosters, reviews and the cleanse proposal as the place to read; what happened to every idea
in them is in `design/concepts/Greentide/rewrite_choices.md`. Nothing has been deleted yet. The Greentide is one of
the six biome mods HELD BY OWNER: this is a design document only and it launches nothing.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/Greentide/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Greentide has no locked sheet or tree; its only pipeline material is the
cleanse proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"A green ribbon of total war, steaming, growing while you watch."* (`the_greentide.md` §9)

A gallery jungle hugging every mile of the rivers that fall off the storm peaks, a ribbon a few tiles wide through
country that gets full desert sun. The rivers steam all the time and the steam cannot rise, so a hot fog rolls low
over black mud. Under it everything grows at a speed you can watch, everything eats everything in the open, and
*"the crashing of trees — cracked, gnawed, or simply shouldered over — is the background percussion of the place."*

> *"This is NOT an oasis, it's an open free-for-all."* (owner, 2026-09-06)

> *"The jungle should be filled with really intimidating dangers in terms of plants, beasts, diseases, and insects.
> That should in turn be countered with tremendous food abundance, unique medicines, a seemingly endless possibility
> for Star Wars cuisine ingredients..."* (owner, 2026-09-22)

His line for the experience, picked by card on 2026-10-20: *"Abundance with teeth: everything grows, and everything
sinks. Fight the jungle every day or lose your base to it."*

**Seen from the ship, the base is the ship.** The crew does not found a jungle home; it parks a stolen hull in the
most productive ground on the planet to fill the larder, and the jungle starts taking the landing site back the same
day. The older sheet already said where Jawa stand in this place: *"trade, not settlement... crawlers park at the
band's edge."* They have sold both survival kits at that edge all their lives. They have never been inside. An
earlier design pass put the whole biome in one sentence that needs no change: *"The Greentide is a destination,
not a home."*

The crew are small, hooded, skittish and built for dry heat (`reconciled_lore/05_the_clan.md`). Here the air is
as hot as home and wet enough to drink. *"You don't sweat, the air sweats you."*

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew halves every wait and a hidden one doubles it.

**UNSETTLED: how long a visit lasts.** Assumed here: a first week nearly free of the Empire, a first fight in the
second or third week, nothing past about a month. A season is fifteen days. The Greentide is kind to this clock: its
own pressure is measured in hours and days, so almost everything it does can be seen inside a stop.

---

## The first minutes

From the air the Greentide is *"visible from the dunes as a line of steam"*. The owner's test for the density is the
first thing the player should feel: *"You look at the map when you land and decide to go around."* There is
*"virtually no squares uncovered by lush foliage. Choked with foliage. Immediately intimidating to hack through."*

The ship comes down through the steam and flattens a hull-shaped hole in the green. The crowns stand clear above a
fog that hides the floor: nobody can see which mud is the hungry kind. The noise does not stop for the ship. This is
the loudest biome on the planet, *"scream, chew, drip, creak, crash"*, and the birds that scatter from the hull are
calling again before the ramp is down.

The hatch opens onto a wall of leaf taller than the crew. Every plant of the understory is tall and broad enough
that *"a colonist cannot see over or past"* it, and the crew is shorter than a colonist.

Before the first day is out the player should have seen three things without going looking: a tree come down
somewhere in the middle distance; the first crate left on the mud gone under it; and green at the cut edge of the
landing hole that was not there at noon.

## The first day

- **Everything sinks.** Anything loose left on churnmud, stockpiles included, is swallowed. A marker stays; the
  thing can be dug out as it was. For a crew whose whole life is piles of salvage set down wherever there is room,
  this is the first lesson and the funniest: the cargo has to go on root, on paving, or back aboard.
- **People sink too.** Mud mires the careless by stages, and a mired crew member is pulled free by another onto firm
  ground. (The owner's rule of 2026-11-10: a rescue is complete *"on nearby firm ground"*, with *"a usable escape for
  victim and helper"*.)
- **The roots are the roads.** The giants' roots stand clear of the mud, firm and fast, and every sensible errand
  follows them. So does everything else that prefers dry footing.
- **The larder.** Fruit under leaf mounds, gourds, sugar-drip, tubers, the river's strange catch, meat everywhere,
  greenwood lying where it fell. Nothing on the planet feeds a crew faster.
- **The fruit yearns to be eaten.** It is huge, sweet and everywhere, and loaded so the eater digests fast: hunger
  comes back early, filth follows, and for a while the eater waddles.
- **The percussion gets close.** Trees fall by three hands: cracked by their own growth, gnawed through by the big
  insects at their bases, or shouldered over by the herd. A fall gives a warning and then damages whatever is under
  it, the crew's own things included.
- **The water.** Something long and flat is in the deep reach and cannot be seen until it lunges. Just before it
  does, the jungle's noise ducks out. *"Players learn to fear a quiet jungle."*

## The first week

- **The green comes for the doors.** *"Plants will grow into and block your doors."* Cleared, unpaved ground the
  crew uses (the ramp's apron, the path to the river, the path to the fruit) is contested again within days.
  Three things hold it and one thing ends it: clearing by hand; a **dry-air blower** at a doorway, a downward
  curtain of dry air that the growth will not cross and that cools the room behind it, for as long as it has fuel
  and power; **grazers** that actually eat the growth line; and paving, which is permanent for the cells it covers.
  *"Darkness brings roots. Light brings leaves and branches. The only thing that repels them is dry heat."*
- **Neglect has stages.** The owner's answer of 2026-11-10: *"Recovery first, abandonment after prolonged neglect:
  warnings allow intervention, late response costs clearing and hauling, and continued neglect can force evacuation
  with supplies left behind."* On a ship that is the campaign's own loop arriving early: decide what to leave
  behind, and launch.
- **The fever.** The jungle's one sickness of its own is the Frenzy: the sick work faster and faster, then collapse
  for days. On a crew of five to seven with the Empire a week out, one coma is a real hole in the roster.
- **The clearing.** Rarely the lid breaks: the steam lifts at once and the jungle *"stands naked"* under the full
  sun for a few hours. *"Clarity as the disaster."* The grazers bolt for shade. For once the crew can see the whole
  map, and so can everything else.
- **The lace.** Ordinary research here yields the stellock lace, a cartridge that stops all of a patient's bleeding
  for a while, stumps included. It is learned here and works anywhere.
- **One giant.** A fellable greatbole stands in a clearing of its own making. Bringing it down is a project of days
  and *"the largest event on the map"*, and it is the only tree that pays true hardwood.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The cargo sinks.** *On screen:* a stack of salvage settles into black mud and is gone, a small marker in its
   place, and a hooded figure starts digging. *Why it is funny:* they put the next stack down beside it.
2. **The bank stands up.** *On screen:* a stretch of riverbank that looked like every other stretch rises under a
   walker and bites. *"The ground itself stands up."* The vurrak gives a moment's warning when weight lands, strikes
   the cell it marked, and after that is an ordinary animal that bleeds. A pet running ahead only reveals it.
   (`UNMEASURED`: whether a Jawa is heavy enough to set it off. Either answer is funny.)
3. **The quiet.** *On screen:* a flock of screaming magenta fliers goes silent mid-wheel; a second later the river
   opens. *Why it is alarming:* the player was warned and had one second.
4. **The herd comes through.** *On screen:* huge copper-teal browsers shouldering trees over to eat the crowns,
   *"crash after crash"*, a line of new sun-gaps walking toward the ship. *Why it lands:* nothing is attacking. It
   is weather with legs.
5. **The wrong fruit.** *On screen:* a crew member reaches into a sugar-drip plant, knocks a gall, and comes out
   under a cloud of wasps, running for the ramp.
6. **The waddle.** *On screen:* the crew gorges on free fruit, then moves at a waddle, hungry again, trailing filth.
7. **The doors.** *On screen:* the apron cleared on day one, grown shut on day four, and a blower's shimmer holding
   one doorway open in a wall of green.
8. **The frenzy.** *On screen:* one Jawa doing three Jawas' work, eyes bright, for a day; then flat on the deck for
   several.
9. **The shoal.** *On screen:* the water boils with small fast toothy things. The owner's words: *"crazy fast and
   nearly unkillable except with explosives."*

## When the Empire arrives

There is no truce here and the Empire does not get one.

- **Nobody can see.** The low steam costs accuracy and speed for everyone, and the understory blocks sight, shooting
  and witnessing. The Empire's probe and spotter each have to *see* the ship or the crew to succeed; at ground level
  the Greentide gives them very little to see. Fights happen close.
- **The mud does not care whose boots.** Troopers mire where the crew has learned the roots. What a downed trooper
  drops, the mud takes, and the crew can dig it out after: the one battlefield where the salvage buries itself for
  later.
- **The water takes them.** The lunger, the bank and the shoal are hostile to whatever comes close.
- **The trees take them.** A fall damages everything under it. A firefight among gnawed trunks is fought under them.
- **The clearing takes the cover away.** If the steam lifts during a fight, both sides can suddenly shoot.
- *0.2.0:* a provoked herd shoulders walls the way it shoulders trees, and a siege camp is a wall; steam devils
  wander through both lines; giant ants raid whoever is there; and plants that grab, spit and burst stand in the
  way of anything that pushes through them.

## Who else attacks; who hates the Empire

- **Everything.** The biome's law is that nothing here keeps a peace. Predators hunt whatever is near; disturbed
  insects sting whoever disturbed them.
- **Giant ants (0.2.0),** the jungle's own raiders, ours and franchise-free since the owner's card of 2026-10-22: a
  hidden hostile faction that assaults directly.
- **Nobody here is on the crew's side by design.** The Wildsteam hold two seats on this river in the campaign's world
  (*"safe harbor for the player"*, the sheet says), placed by the campaign layer and not by this biome. Whether
  they fight the Empire is `UNSETTLED`. The droid enclaves at the river's salt graves *"wanting only solitude"*.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The green closing the landing site faster than a small crew can clear it, with stock already in the mud.
- Crew down with the Frenzy.
- A tree, or a herd, through the camp.

**Stay, longer than the Empire would like:**
- Blowers on the doorways, a penned herd eating the growth line, a paved apron.
- Sight-blocking jungle between the ship and anything looking for it at ground level.
- Mud and water the crew knows and the Empire does not.
- `NEEDS HIM`: whether canopy and steam hide the ship from orbit. As built, they do not.

The danger does not grow as the crew learns. The owner's card of 2026-09-25: *"danger stays FLAT as players master
the jungle; the player improves, the jungle does not scale."* A second Greentide stop is easier only because the
player is better.

## What the crew takes away

- **Food,** more than any other stop: fruit, gourds, sugar, tubers, the catch, meat.
- **Greenwood,** weak, smoky and *"abundant beyond counting"*, on a world with almost no trees. *"The desert buys it
  by the crawler-load."*
- **True hardwood,** only from a felled greatbole. *"The price gap between the two woods tells the biome's story."*
- **Resin,** for sealing and lacquer. Whether it renders to fuel is `NEEDS HIM`.
- **The stellock lace,** as knowledge: learned here, crafted anywhere.
- **Tame grazers,** if the crew wants a living hedge-trimmer aboard.
- *0.2.0:* **a marked survivor.** A crew member who has been through the Frenzy and lived carries it for life and is
  immune, so the next jungle stop is led by someone who cannot catch it (owner's card, 2026-09-25: *"survivors
  become specialists"*).

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Used, unpaved ground beside the ship is taken back by growth within days, and clearing, a working blower, real grazing and paving each hold it. | A landed ship with a cleared apron and three used paths: one left alone, one behind a blower, one grazed; one paved. Run the days. | The blower with its fuel out: its tell stops and growth returns. A penned herd that is not eating protects nothing. |
| Loose things on churnmud sink and come back whole when dug out. | Stock on mud, on root and on paving; wait; dig. Save and reload while buried. | The dug-out thing has the quality, wear and rot it went down with. |
| A mired crew member is slowed by stages and is freed onto firm ground by another. | One pawn mired, one helper with a firm route. | A helper with no firm ground to stand on fails readably and does not loop. |
| Trees come down by crack, by gnawing and by the herd, with a warning, and hurt what is under them. | One of each feller; a pawn and a crate in the swath. | A tree nobody touched, in the same wind, stands. |
| The low steam hides the floor, costs accuracy and speed, and lifts for a few hours in a clearing. | Shoot and walk under the steam and during a clearing. Watch the grazers. | The same shots on a map with the steam switched off. |
| The understory blocks sight. | A watcher and a walker with mature leaf mounds between them. | The same line with the plants cut. |
| The river predator is unseen until it lunges, and the noise ducks first. | Prey at the bank of a deep reach, with a calling flock overhead. | Shallow water with the same prey: no lunge, no hush. |
| The bank ambusher bites what is heavy enough and is only revealed by what is light. | A person and a small animal walk the same bank cell. | A bank with no water near it holds none. |
| A disturbed gall releases wasps on the one who disturbed it. | Harvest a host plant that carries a gall, and one that does not. | A gall spawned by hand proves nothing: the gall has to be on its host by the map's own making. |
| The Frenzy speeds its victim, then drops them for days. | An ambient case run to its end, tended and untended. | Flu and malaria do not appear here. |
| The stellock lace stops all bleeding for a while and nothing else. | A bleeding patient with and without the lace, here and on another map. | The wounds are still there afterwards. |
| Eating the yearning fruit feeds, then costs: early hunger, filth, a slow walk. | Two pawns, one fed fruit, one fed an ordinary meal. | |

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary hot swamp (standing
rule, every mod).

## Shared machinery

**Featured here** (the Greentide is where each is vital and should be proven):
- **Growth as pressure, and what holds it back** (`ExplosiveGrowth`'s wet-native growth and its suppression grid;
  the dry-air blower and grazing in `EnvironmentalHazards`). Growth runs on every wet map; only here is it the
  thing the player fights.
- **Mud that mires and mud that buries** (`RM_MapComponent_TerrainMire`, `RM_MapComponent_MudSwallow`). The Fever
  Wood wants a cousin of the first in its 0.2.0.
- **Trees that fall on things** (`RM_TreeFallUtility` and its three fellers).
- **Plants that block sight** (`RM_CompSightBlocker` in `CreatureBehaviors`).
- **Standing weather that hides the floor, and its clearing** (the Roil and Breaklight, in `EnvironmentalHazards`).

**Merely active here:** the hush before a predator (the same `RM_MapComponent_SilenceCue` the Fever Wood features);
the lunge from water; bounded insect reactions; shade-seeking animals; real flight; the one sun from geometry, with
tree shade (the Greentide has no heat of its own any more; hot wet air is ordinary air temperature); bone from
butchery; wreck salvage; the Empire's search and the visibility dial; root causeways (shared with the Fever Wood's
painted routes).

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**0.1.0, the stop**
- The land: low standing steam and its rare clearing; churnmud that mires and buries; static root causeways; a
  choked, sight-blocking understory under a readable canopy. (built)
- The green contesting used unpaved ground around the ship; clearing, the blower (which also cools), grazing and
  paving as the answers. (parts built; natural pressure on used ground at shipped settings is unproven)
- Tree falls by three fellers; the gnawing krannock; the thurrock herd as browsers and fellers; the fellable
  greatbole and its hardwood. (built)
- The dhollock's lunge and the hush; the vurrak's bank; the illisk shoal as an ordinary shoal; yammeth flocks that
  really fly; sulleth grazers that seek shade in a clearing. (built; the vurrak moved in, see `rewrite_choices.md`)
- Galls on their host plants and the wasps in them. (the wasps are built; natural gall placement is not)
- The larder: brakkel, tumbel, sarquin, wollick, the catch, timber, resin; the yearning fruit with its tax. (built;
  the fruit's tax moved in)
- The Frenzy as the jungle's own ambient sickness. The stellock lace by ordinary research. (built)
- Natives are not mired at home; nothing disappears without a sign.

**0.2.0, the stop with company**
- Plants that act: the maddrick's closing ring, the gorbeleth's spitting throat, the phorrik's bursting bladders,
  the zhorrel's hanging strangler. (unbuilt)
- The thurrock shouldering walls when provoked; the illisk's immunity to everything but blast; steam devils; the
  zrrik, which heals itself by stabbing. (built)
- Giant ant raids. (built)
- The fever mark and immunity for survivors; taking the Frenzy on purpose as a dose, to work at fever speed before
  a deadline and pay for it afterwards. (built)
- Finding the lace by studying a self-sealing branch from a felled tree. (built)
- The yearning fruit's seed passing through and sprouting where it lands. (built)
- The stench grenade, the one tool that turns the jungle's animals. (built)
- The ship's acoustic sounder readings here. (built)

**Later (a crew that stays, or a colony)**
- The living greatbole tower: rooms mined into heartwood that heals shut, the sealant, the shaking and the
  catastrophe, fruitfall, fruit steaks and rind, grubs, seeds, the song, the cool sanctuary, pilgrims, servants.
- Roads that move between visits; the river growing saltier along its course and ending in a grave; the habitable
  band; drip under the canopy.
- The bottled growth extract. The cuisine system. The nine further reward ideas of 2026-09-22 that were never ruled.
- Ant carapace as a building stock; seeding and toxin weapons; branch travel for the canopy swinger.
- The Ceded Room rite (the owner's own later ruling put it in a second version).
- Wildsteam domes, droid enclaves at the river graves, wild greatboles as dungeons: campaign layer.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Wet-bulb heat as its own kind, and its gear tree (the one-sun ruling of 2026-10-19; hot air is ordinary air).
- Danger that scales with the player (declined 2026-09-25).
- Canon trees and the vanilla animals (*"we're making our own"*, 2026-09-22); the placeholder squirrel and alligator.
- The dianoga here (*"It belongs only in tank prisons and the Fever Wood"*, 2026-09-23).
- The moulting giant, the hull rasp, working between the crashes, the Uprooting rite (not chosen 2026-10-02).
- Churnmud seeded on other biomes (kept off and labelled unsupported, by the 2026-10-15 ruling).
- **Recommended for dropping, not yet his:** the unused sugar-famewort plant; the old natural-placement scoring.

## NEEDS HIM

1. **Do canopy and steam hide the ship from orbit?** The same question as the Fever Wood's. His 2026-08-05 ruling
   pauses the orbital clock on dark or covered tiles; only the Abyss is on the built list. *No* (as built, default).
   *Yes:* the Greentide becomes a place to hide, paid for in upkeep. *Partly:* one visibility band quieter.
2. **Is resin ship fuel?** The sheet lists *"rendered chemfuel — the dayside's fuel economy"* among the jungle's
   goods and nothing builds it. *Not in these versions* (default). *A rendering recipe in 0.2.0:* the Greentide
   becomes the fuel stop, and the blower burns what the jungle bleeds.
3. **Does the jungle touch the hull?** Today a falling tree can hit the ship like anything else, and growth stops at
   the hull's edge. *That is enough* (default). *The hull rasp he did not choose on 2026-10-02* (a colony organism
   rasping exposed metal, scraped off by hand, dying when the ship leaves): a second reason not to linger, and a
   new system.

Three questions the cleanse put to him on 2026-11-17 are answered here by scope instead of asked again, and each is
a line under "Scope moves" in `rewrite_choices.md`: plants that act are 0.2.0, not absent; cuisine in 0.1.0 is
ordinary cooking of extraordinary ingredients, with the combining system later; and paving ends regrowth on the
cells it covers, so care moves to the unpaved ground a visiting crew actually uses.
