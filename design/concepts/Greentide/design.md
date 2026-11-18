# The Greentide: the design, seen from the ship

**Status:** the one design document for the Greentide biome (`RM_Greentide`, source `src/RimMandrake/Greentide/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the
older definition sheet, rosters, reviews and the cleanse proposal as the place to read; what happened to every idea
in them is in `design/concepts/Greentide/rewrite_choices.md`. Nothing has been deleted yet. The Greentide is one of
the six biome mods HELD BY OWNER: this is a design document only and it launches nothing.

**Revised the same day** after his card of 2026-11-18, 3:10 PM PST, which answered the three questions the first
pass had left for him here (cover from orbit, fuel, the hull) and ruled on how long a stop lasts. The answers are
written in below (see "The ship while it sits here"); the changes are listed at the top of `rewrite_choices.md`.

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

**How long a stop here can last: about six weeks, and that is the outer edge.** His ruling of 2026-11-18 on the
numbers the first pass assumed: *"The numbers you're generating are likely the outer edge allowable for each biome,
and that's just fine. Go with that."* On open ground, for a crew the search reads as ordinary, the ladder's
arithmetic gives a probe on day 5 to 8, a first real fight around day 12 to 20 and the bombardment around day 20 to
32 if the Empire wins every step. The Greentide's canopy and steam are **partial cover from orbit** (his card, same
day: *"Canopy, steam and fog slow the search by one step; full dark still pauses it"*), read here as one band on the
pursuit's built visibility scale, which stretches every wait by about four tenths: a probe on day 7 to 11, a first
fight in the third or fourth week, nothing past about six weeks. Canopy and steam together are still one step, not
two. A loud crew gives the step back. (The pursuit's numbers are marked provisional in its own source; the shape is
what this design leans on.)

Few crews will see that edge. The Greentide is kind to a short clock: its own pressure is measured in hours and
days, so almost everything it does can be seen inside a stop, and the green, the fever or the hull usually ends the
stay first. A season is fifteen days.

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

## The ship while it sits here

Three things every biome design now states, by his rulings of 2026-11-18.

**Cover from orbit: partial.** Canopy and standing steam slow the search by one step (above). At ground level the
understory does more than that, because the probe and the spotter have to see the ship. Neither makes the
Greentide a hideout: the probe still comes. This is a campaign-layer line, one entry for this biome in a list the
pursuit already reads. (`UNSETTLED`: whether a clearing, which lifts the steam and leaves the canopy, costs the
step while it lasts. Assumed not.)

**Wear on the hull: the jungle eats metal too.** His ruling: *"Yes in 0.1.0. It's easy, and most of the biome
already talk about this."* The Greentide's own wear is in the review of 2026-10-02
(`greentide_bedazzle_review_2026-10-02.md`), the hull rasp: *"a colonial organism rasps exposed wet metal, the
landed ship as one more feeding surface; scrape it off by hand in the heat; take off and the damage flies home, the
rasp blanches and dies away from the jungle."* He did not choose it that day (he chose the lace). His card of
2026-11-18 asked about it by name and he answered yes.

- *What the player sees.* A visible colony spreading on outside metal within days of landing (its look is art still to be made): on hull plate, and
  *"on every metal building alike, so no ship special case"*. Where it sits, the metal loses condition. Its marks
  stay after it is gone.
- *What answers it.* Scraping it off by hand, which is hot work in this air. A dry-air blower set at the hull: the
  review calls the blower *"its natural counter"*, and the blower burns fuel. And, for a crew that owns one, the
  ship's light screen: his shield ruling of 2026-09-02 is that it handles *"wind, ash, vapor, bio contamination,
  spores, smoke, sand, and rain damage completely as well as repels small animals"*. The shield holds one setting
  at a time, so the screen that keeps the rasp off is not the heavy field that would take a falling tree.
- *It ends when the ship leaves.* The rasp dies away from the jungle. The scars fly home and are repaired like any
  damage.
- *The other wears are already here.* A tree that falls on the hull damages it like anything under a fall. The
  green that closes the doors blocks them and does not eat them.
- *The approach.* The ship comes down through the steam; no source says the steam shakes or scalds a hull on the
  way in, and this design does not add it. Steam devils, which scald whatever they cross, are 0.2.0.
- *It never traps.* His ruling of 2026-09-02: the hull *"is thick and can take a lot of damage in most situations,
  so no environment is immediately lethal"*, and the ship *"will advise course of action, but no more than that"*.
- The organism's name is `UNSETTLED`: the review's working name carries the note "Rename needed".

**Fuel: a richer source, named, bought at the band's edge, and spent here faster than anywhere.** His ruling:
*"Every biome has a fuel source, but for most its the hideously slow route of rendering biomass into chemfuel... A
few biomes have richer sources. You can also buy it (the intended motivation to have to trade constantly, very
Jawa)."*

- *The emergency route* has the best feedstock on the planet: greenwood *"abundant beyond counting"*. It is still
  the slow route.
- *The richer source is resin.* The sheet lists, among what only the Greentide has, *"sap and resin — tapped from
  trees growing too fast not to bleed: glue, lacquer, waterproofing, and rendered chemfuel — the dayside's fuel
  economy."* Resin is a built harvest; the recipe that renders it to chemfuel is not, and is 0.2.0.
- *Buying it.* The crew's own kind are already here: *"crawlers park at the band's edge"*, and *"the desert buys
  [greenwood] by the crawler-load"*. A crew that fills the hold with wood has something every crawler wants. The
  Wildsteam's two seats on the river are the other sellers. Both are campaign layer.
- *Spending it.* The blower drains chemfuel all the time it runs (built). Holding the doors and the hull dry is
  paid for in the same drums the ship flies on. That is the Greentide's fuel joke: it sells fuel and eats it.
- Not written as replete. The sheet's phrase *"the dayside's fuel economy"* is strong, and if he reads it that way
  it is a one-word change here.

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
10. **Scraping the ship.** *On screen:* hooded figures on the hull in the steam, scraping the colony off the
   plate with whatever was in the hold, and the patch they cleared yesterday already furred over behind them.
   *Why it is funny:* the jungle has decided the ship is food, and it is not wrong about anything else here.
11. **Wood for fuel** (0.2.0, campaign layer). *On screen:* a crawler at the band's edge, a heap of greenwood, and
   two groups of Jawa haggling over drums. *Why it lands:* the crew is finally on the selling side of the jungle.

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
- The hull furring over with rasp faster than a small crew can scrape it, and the fuel the blowers burn.
- The green closing the landing site faster than a small crew can clear it, with stock already in the mud.
- Crew down with the Frenzy.
- A tree, or a herd, through the camp.

**Stay, longer than the Empire would like:**
- Blowers on the doorways, a penned herd eating the growth line, a paved apron.
- Sight-blocking jungle between the ship and anything looking for it at ground level.
- Mud and water the crew knows and the Empire does not.
- Canopy and steam over the ship, which slow the search from orbit by one step (his card of 2026-11-18; unbuilt).
- A hull kept scraped, blown dry or screened.

The danger does not grow as the crew learns. The owner's card of 2026-09-25: *"danger stays FLAT as players master
the jungle; the player improves, the jungle does not scale."* A second Greentide stop is easier only because the
player is better.

## What the crew takes away

- **Food,** more than any other stop: fruit, gourds, sugar, tubers, the catch, meat.
- **Greenwood,** weak, smoky and *"abundant beyond counting"*, on a world with almost no trees. *"The desert buys it
  by the crawler-load."*
- **True hardwood,** only from a felled greatbole. *"The price gap between the two woods tells the biome's story."*
- **Resin,** for sealing and lacquer, and from 0.2.0 rendered to fuel.
- **A hold full of greenwood,** which is what the crawlers at the band's edge sell fuel for.
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
| Outside metal left in the jungle, the hull included, grows a visible rasp that wears it; scraping, a working blower and the ship's light screen each keep it off; it dies when the ship leaves, and a worn ship can always launch. | A landed ship and a steel wall, each with one face left alone, one scraped, one behind a blower. Run the days, then launch. | The same steel on another biome's map grows nothing. The blower with its fuel out: the rasp returns. |
| Under canopy and steam the Empire's search comes one step slower than it does for the same crew on open ground. | The same crew, as loud, landed here and on an uncovered tile; read the search's next contact on both. | A crew made loud here loses the step. |

Neither new row pins a rate: how fast the rasp wears and how long a step is are tuning, and stay out of any bar.

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

- **A living thing that wears metal** (the hull rasp). The hull-wear machinery is shared; this is its biological
  case, and the one where the answer is a blower, a scraper or the light screen.

**Merely active here:** the hush before a predator (the same `RM_MapComponent_SilenceCue` the Fever Wood features);
the lunge from water; bounded insect reactions; shade-seeking animals; real flight; the one sun from geometry, with
tree shade (the Greentide has no heat of its own any more; hot wet air is ordinary air temperature); bone from
butchery; wreck salvage; the Empire's search and the visibility dial; root causeways (shared with the Fever Wood's
painted routes).

**Three ship systems built once for every biome, and what the Greentide asks of each** (found while revising; the
shared-machinery file has the whole of it):
- *Hull wear.* The campaign already has the frame: `src/RimUtinni/ShipShields/`, whose exposure tracker wears a
  landed ship's structures in a hazard its shield does not cover, sends an advisory and never refuses a landing. It
  knows heat, cold and blown particles today. The Greentide needs it to know a biome's own wear (the rasp) and to
  count the light screen and a blower's dry air as cover against it.
- *Cover from orbit.* The pursuit has one list for full shadow (the Abyss only) and no notion of partial cover. The
  Greentide needs a second, weaker entry.
- *Fuel.* One recipe from resin to chemfuel, and traders who stock fuel. The slow biomass route is the base game's
  own.

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
- The hull rasp on outside metal, the ship included; scraping, the blower and the light screen as the answers.
  (unbuilt; campaign layer for the ship, on the shared hull-wear machinery; his ruling of 2026-11-18)
- Canopy and steam as partial cover from orbit. (unbuilt; campaign layer, one entry in the pursuit; his card of
  2026-11-18)
- Fuel by the slow route from greenwood; resin and greenwood as goods. (the base game's refining; the harvests are
  built)

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
- Resin rendered to chemfuel; fuel bought from crawlers at the band's edge and at the Wildsteam's seats. (unbuilt)

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
- The moulting giant, working between the crashes, the Uprooting rite (not chosen 2026-10-02). The hull rasp was
  on this line and is back in 0.1.0 by his ruling of 2026-11-18.
- Churnmud seeded on other biomes (kept off and labelled unsupported, by the 2026-10-15 ruling).
- **Recommended for dropping, not yet his:** the unused sugar-famewort plant; the old natural-placement scoring.

## NEEDS HIM

Nothing is left for him here. The three questions the first pass asked were answered by his card of 2026-11-18 and
are written into the design above: canopy and steam are partial cover from orbit; resin is the Greentide's richer
fuel source; the jungle wears the hull, by the rasp, in 0.1.0.

Three questions the cleanse put to him on 2026-11-17 are answered here by scope instead of asked again, and each is
a line under "Scope moves" in `rewrite_choices.md`: plants that act are 0.2.0, not absent; cuisine in 0.1.0 is
ordinary cooking of extraordinary ingredients, with the combining system later; and paving ends regrowth on the
cells it covers, so care moves to the unpaved ground a visiting crew actually uses.
