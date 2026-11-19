# The Long Shade: the design, seen from the ship

**Status:** the one design document for the Long Shade biome (`RM_LongShade`, source `src/RimMandrake/LongShade/`;
the campaign world's "desert"), rewritten 2026-11-18 on the owner's instruction to see every biome "through the
lens of Utinni". It replaces the older definition sheet, the sitting documents, reviews, cast bible and the cleanse
proposal as the place to read; what happened to every idea in them is in
`design/concepts/LongShade/rewrite_choices.md`. Nothing has been deleted. This is a design document only and it
launches nothing.

**What kind of place this is (checked against the sheet's own header):** a surface biome, the outer day-side
desert: *"the livable one"*, the largest biome on the planet, dry, rocky, landable anywhere.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/LongShade/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Long Shade has no locked sheet or tree; its only pipeline material is the
cleanse proposal of 2026-11-17, which this design supersedes and which was never applied.

**Second reader, 2026-11-18:** a reader who did not write this design read the sheet, the sitting, the shade
ideation, the cast bible, his rulings on the ledger and the mod's own definitions, and repaired this file. What
changed and why is at the top of `rewrite_choices.md`. The largest repairs: the ship's shade filling with animals
is not a cleanse leftover but his own card pick of 2026-09-30; the hull wear now names the one hazard the built
ship-shield frame already sees here, the sandstorm; this place does have a fuel plant; the gnomon line and the farm
on the horizon were cut by him, not left unruled; and the ultracactus has lived in the Stillsand since 2026-10-05.

**There is no locked Designer tree here** to hold apart from this design: the only pipeline material is the
cleanse proposal, which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"Shade is the currency, and every crossing is a gamble. Rest, dash, rest, and never trust a shadow you didn't
> cast yourself."* (owner, by card, 2026-10-20)

> *"The one place on the dayside with enough shade to survive between — but never enough to survive in."*
> (`desert.md` §1)

The sun sits a hand's width above the horizon and never moves, so every rock and scarp throws a shadow four times
its own height, and the shadows never move either. They are *"patches, not cover"*: islands of cool dark with hot
light between. Life here is *"a sprint between shelters"*: rest in a shadow, run to the next, rest again. *"Nothing
in this biome pursues."* The predator owns a shadow and waits *"for something to arrive overheated and out of
options."* And every patch is a commons, predator and prey together, the strongest in the deep centre and
everything else on the rim: *"the biome's waterhole."*

> *"Permanent golden hour, and everything is waiting at the edge of a shadow."* (`desert.md` §9)

It is *"the most straightforwardly beautiful ground on the planet: a sunset that has been going on for a million
years."*

**Seen from the ship, this is the one stop where the crew are not the fools on the ground.** This is desert with
roads in it, herd beasts, dead vehicles and a dead sandcrawler at the end of one of the roads; by every sign in
the sources it is the crew's own kind of country (no source says in one sentence which biome the clan calls home;
`NEEDS HIM` below). They know to rest, dash and rest. They know *"for a Jawa, the shade is the dig site."* What
they have never done is arrive in something that casts shade. The sheet's own warning to any builder is exact for
a landed hull:

> *"Building a roof is the most powerful act available here... the moment you do, your base is the largest shade
> patch for miles. ⇒ Every living thing in the region wants to be in it. Your walls are not keeping out raiders —
> they are keeping out an ecosystem that has correctly identified you as the best harbour on the route. Including,
> eventually, something whale-sized that has walked this line for a very long time and does not know you have
> moved in."*

An earlier design pass said it in six words: *"hospitality you cannot decline."* The review of 2026-09-29: *"every
other biome threatens the ship; this one is hospitable to it, and hospitality is the threat."* He picked exactly
this by card on 2026-09-30 (the Shipfall Commons): *"small animals take the ramp shadow, herds press the hull,
pirrik circle, eventually the gloomcast walks over. Launch is never blocked; occupants get a readable dispersal
job."* It is built. Every other biome threatens the ship. This one moves in under it.

His verdict on the whole place, typed at the sitting of 2026-09-29, is the brief for everything below: *"It's
ok... but a tad boring unless we get really strict about the dashing animal behavior. If we can do that it's quite
interesting. But the shade should be more interesting. That's where everything's hanging out."* And: *"Maybe some
of those shady spots aren't so natural after all?"* The ideation that answered him put it in one line: *"the light
is the law, and the shade is where everything is kept."*

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last (the outer edge of a stay, not the usual one; owner's ruling of 2026-11-18).** The
ordinary ladder with nothing to slow it: a first week nearly free, a first fight in the second or third week,
nothing past about a month. What is different here is that **the Empire is the only clock.** The air is mild, the
game is steady, the ground is buildable, and nothing the biome does forces a competent crew to leave. A crew will
stay here exactly as long as it dares.

**What cover this place gives, and which kind (same card: canopy, steam and fog slow the search by one step).**
**None.** No canopy, no steam, no fog, a sky that is clear and gold for ever, and long sight lines across open
pavement. Shade is not cover: a hull in a shadow is still a hull. A sandstorm blows through now and then and is
not on his list of what slows the search either. This is the price of the easiest living on the day side.
(*0.2.0:* the smoke haze that drifts in from the Pyrelands' fires dims the sun over the whole map; it is the
natural candidate for one step of cover while it lasts, and that is `NEEDS HIM` 3, not assumed. His card of
2026-11-17 on the Pyrelands' own smoke weather was *"Next version"*.)

---

## The first minutes

The ship comes down out of a sky the colour of a banked fire onto amber ground striped with long blue shadows, all
of them lying the same way. Wherever it lands it lays down a new one, bigger than any rock's, and it will not move
until the ship does.

The ramp opens on stillness: *"stillness, then a sudden committed sprint across the light, then stillness."* At the
edge of the nearest natural shadow something is standing, looking at the new one, *"an animal at the edge of a
shadow, deciding."*

Before the first hour is out the player should have seen three things without hunting for them: an animal rest in
shade, cross a lit gap at a run, and rest again; the first small creature make the dash to the ship's own shadow
and settle under the hull; and a crew member working in the open walk back into shade on their own when the sun
begins to tell on them.

## The first day

- **The sun is ordinary heat.** There is no special desert heat. Direct sun adds to what the body feels, by the
  same geometry as everywhere on the planet, and here the sun is low, so it is mild and it is always there.
  *"Relief never arrives on a schedule. The heat does not break. It is only ever somewhere else."* A crew member
  who starts to overheat goes to the nearest shade they can reach, cools, and goes back to work. They do not plan
  routes; they react. (His words of 2026-11-10: *"They just seek shade when they start to overheat in every
  biome... It's the beasts that should act specially since they're evolved to do so."*)
- **The animals are strict about it.** Natives visibly rest, dash and rest, each within what its body can cross:
  *"Body size maps directly to maximum dash distance... The landscape is sorted by size."* (His words of
  2026-09-29: *"a tad boring unless we get really strict about the dashing animal behavior. If we can do that
  it's quite interesting."*)
- **The ship fills up.** In order of how far each can run, the country arrives in the hull's shade: small things
  first, then a herd staging against the lee side before its next crossing, then something that hunts by waiting.
  This is game delivered to the ramp, and it is also a predator under the landing gear.
- **Shade can be carried and built.** Parasols and any quick roof are real shade. A party under parasols can work
  ground no native can stand on. His words: *"Actual shadow-casting gear doubles down on the idea of heat building
  up. I like it. Parisols, shade tents, simple shields you can stand behind."* The standing shield, a tall panel
  of stretched hide on a braced frame, is *"the one piece that works under a low sun."*
- **A full shadow is a safe shadow; an empty one is not.** Every patch here is crowded, so *"a perfect, deep,
  dew-ringed shadow with nothing in it is the loudest warning on the map... The animals know; the player learns to
  watch the animals."* He kept this as a rule by card (2026-10-04, admitted 2026-10-08): every hidden danger in
  the shade empties its patch.
- **The shade is the dig site.** The wind never reverses, so *"everything that blows across this desert ends up
  in a shadow: nutrients, and also bones, debris and wreckage."* Heaps lie in the lee of the big shade-casters and
  can be searched once each, for scrap, bone and now and then a real find. Every heap is inside a shadow, and
  every shadow has tenants.
- **Soft ground and hard ground are opposite bargains.** Sand holds the rocks that cast shade, and things can
  come up through it. Hardpan is safe from below and bare of shelter: *"Safety and shelter are on opposite ground,
  and every crossing is a choice between them."* Deep sand can be walked, *"just very slowly."* Where to set the
  ship down is the same choice.
- **Three plants worth knowing.** The **shadespire**, *"the only vertical that grows"*: a rare banded column three
  or four metres tall that is its own small patch, with tenants and a pale fringe at its shadow's edge; felling
  one gives dense pale wood *"and removes the shelter."* **Pavecrust**, a grey lichen on bare hardpan whose
  *"harvested scraps burn slowly and hot"*. **Maidenbloom**, a fat rosette that grows only where a giant has
  stopped, *"the visible proof of it"* (his name: *"Middenbloom sounds disgusting. Maidenbloom is better."*). All
  three are built and on the map.

## The first week

- **The moving harbour.** A **gloomcast** crosses the map: the shade whale, by the game's own measure sixteen times a person's size, a
  walking shadow with a flock of small glittering fliers that *"live their entire lives in one animal's shadow."*
  It strains the sand for food as it goes and leaves dung where it rests. Standing beside it is standing in shade.
  Sooner or later it rests at the largest harbour on its line, which is now the ship.
- **The shadow that points the wrong way.** A **mirrak** lies on open pavement and looks like shade: a dark
  oblong where no rock stands, at an angle to every other shadow on the map. It gives no cooling. An overheated
  animal that runs to it is taken, and the taking leaves a drag mark and remains to read. Watching the spot raises
  suspicion; a safe inspection or a careful approach confirms it before anyone commits. (His answers: *"we can't
  have animals 'disappear spontaneously'"*, 2026-09-29; and, 2026-11-10, look, then inspect.)
- **The landlord under the woodshed.** A **dakkra** takes a shadow and holds it: it bursts out at whatever arrives
  spent, grabs, and goes back to cool. It does not chase. *"Its hunting radius is bounded by the trip back."*
- **The sun graves.** Out on the gold, far from any shadow, a pack animal lies where it fell long ago, *"still
  loaded, dry as paper, its rider beside it. Nothing has ever come for them — nothing can afford to."* Getting the
  load is a dash by the crew's own bodies: out, grab, back, under a parasol or not at all.
- **Leaving has a step.** A ship with a herd, a hunter and a whale in its shade does not simply lift. The pilot's
  console clears the shade first, and the tenants scatter for the next patch. Nothing is harmed by the launch that
  was given the warning, and nothing can hold the ship down.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The first tenant.** *On screen:* a small animal at the edge of a rock's shadow looks at the ship, runs
   flat out across the light, and flops down under the hull, panting. Then four more.
2. **The court.** *On screen:* by the third day the ship's shadow holds a herd packed on the lee side, small
   things along the rim, and one still shape in the best spot that nothing stands near. *Why it lands:* the crew
   has to walk through all of it to get to the ramp.
3. **The whale parks.** *On screen:* the largest animal on the planet's day side walks up to the ship, lies down
   in its shade with its flock wheeling in, and radiates the heat of its crossing at the hull. Its tread is heard
   through the ground before it is seen.
4. **The shadow that closes.** *On screen:* an overheated animal sprints for a dark patch on the pavement, drops
   into it, and the patch folds over it *"like a book"*. A drag mark. *Why it is alarming:* the player's eye had
   already marked that patch as the next stop.
5. **Checking the angle.** *On screen:* a Jawa stops short of a shadow, looks at it, looks at the others, and
   walks round. *Why it is funny:* they are right, and the newcomer behind them is not.
6. **The dash for the pack.** *On screen:* one hooded figure breaks from the shade toward a glint far out on the
   pavement, the heat bar climbing, grabs the bundle off a dried corpse and runs back with it.
7. **The parasol train.** *On screen:* a work party crossing the open under parasols, and two small wild things
   running in to trot along in the moving shade.
8. **The landlord strikes.** *On screen:* a herd animal arrives spent at the ship's rim; the still shape under the
   struts covers the distance in a blink, takes it, and is back in the cool before the dust settles.
9. **The dig.** *On screen:* a Jawa elbow-deep in a wind-heap behind a boulder, pulling out bone, bone, slag,
   bone, and a sealed component case.
10. **Clearing the shade.** *On screen:* the console is worked, and the whole court under the hull gets up and
    runs for the rocks in order of size, the whale last.
11. **The herd at the rim, deciding.** *On screen:* a chorn stands with its forelegs in the light and its body in
    the dark, facing the next rock. It stands a long time. Then the whole herd goes at once, flat out across the
    gold. *"The last calf is two strides behind. It makes it."*
12. **The empty shadow.** *On screen:* the best patch for a hundred cells, deep, dew-ringed, and nothing in it,
    with six animals crowded into a worse one beside it. A newcomer walks toward the good one.

*0.2.0 adds:* the road of dead machines across the widest gap, each one stride from the next, and the dead
sandcrawler at its end with the whole country sheltering in its shadow; the rival Jawa clan that comes back for that hull, to be paid, traded with or argued with;
the fruit that looks safe; a herd stampeding for the roof; the sky going orange with other people's smoke; and
**the swimmer's road**. One young sarlacc comes up out of the deep desert *"following water"*, a wake under the
soft sand moving rim to rim, and it is heading for the largest ring of dew on the map, which is the one round the
biggest shadow, which is the ship. *"You have days. You can see the route."* The sources' three answers are all a
crew's: be parked on hardpan, which *"a swimmer cannot cross"*; meet it out in the gap, where *"every metre costs
it water"*; or send the droids, because *"the swimmer ignores droids... The Jawa fantasy."* His condition for it:
*"we can't have animals 'disappear spontaneously.' There needs to be SOME kind of indication of what happened to
them."*

## When the Empire arrives

- **They find the ship at once.** There is nothing to hide behind. The probe's and the spotter's work is easy
  here, and the ladder runs at its ordinary pace or faster.
- **They fight in the sun, and the crew does not have to.** Direct sun is ordinary heat on everybody. Troopers
  who stage in the open for hours, or cross lit ground to assault, take it; a crew that fights from its own shade
  does not. Shade is the currency in a firefight too.
- **The best cover on the map is occupied.** Any shadow big enough to stage a strike team in has tenants, and one
  of them hunts by waiting for something to arrive tired.
- **A false shadow does not check uniforms.** A mirrak takes whatever commits to it.
- **The ship's own tenants are in the way of both sides.** A fight at the ramp is a fight through a herd. A whale
  in the shade is the largest piece of cover on the field and nobody's.
- *0.2.0:* a stampede for the roof goes through whatever is between the herd and the shade, a siege camp included;
  and the haze, when it comes, lets everything cross everywhere at once.

## Who else attacks; who hates the Empire

- **Nothing pursues.** Danger here is positional: a held shadow, a false one, something under soft sand. The
  crew is attacked when it arrives somewhere, never when it is followed.
- **The sand-swimmer.** The qorrax is *"a deadly sand-swimming predator"* bound to deep sand. Stay off deep sand
  and it cannot reach.
- **Deep Desert Tribe holdings** lie in this country in the campaign's world: *"canyons, caves, isolated ridges,
  never near water, and no roads."* They are placed by the campaign layer, not by this biome.
- **The road people.** Settlements stand on the big patches, herder camps work the chains of shade *"by smoke,
  not by calendar"*, and somebody owns every dead crawler. None of them is built by this biome mod, and whether
  any of them would fight the Empire is `UNSETTLED`. They are the people a Jawa crew trades with, and in 0.2.0 one
  of them comes back for its hull: another Jawa clan, with a tow, and an opinion about whose crawler it is.

## What forces the crew out; what lets them stay

**Out, before the Empire:** almost nothing, and that is the point of this stop. A crew is pushed out only by its
own mistakes: a hunter it let settle under the ramp, a whale parked where the cargo was, people sent across a gap
too wide for them.

**Stay, longer than the Empire would like:**
- Reliable game: *"a food web steady enough to hunt as a livelihood rather than a windfall"*, and it walks to
  the ship.
- Mild air, buildable ground, stone, and shade the crew can make.
- People to trade with (campaign layer).
- Nothing at all that hides the ship. Every day here is bought at the ordinary price.

## What the crew takes away

- **Meat and hides,** steadily, from the ship's own shadow.
- **Midden finds:** scrap, bone, slag, and the occasional component cache or old corpse with its gear. Vanilla
  items only, by his card of 2026-10-03; a heap is searched once and is spent (his later card, 2026-10-08).
- **What the sun graves were carrying.**
- **Forage:** dewfringe sprigs from the shadows' rims and maidenbloom hearts from the dung grounds. (The
  ultracactus, which he made and named, moved to the Stillsand with his moves of 2026-10-05, as the ultriss pad.
  It is no longer this biome's.)
- **Tame stock:** *"the pack and draught animals the campaign runs on."* Of the biome's own animals the chorn and
  the gennok carry packs.
- **Flat pavement stone,** and pale shadespire wood.
- **For the ship itself: the long-shade mast.** His question of 2026-09-24 to every biome: *"how can this biome
  uniquely add something to the ship?... What can they take and improve their ships environment with?"* This
  biome's answer on the register is *"a tall black-chitin vane whose lee runs the length of an open deck under a
  low sun... shade a roof cannot give without closing the deck."* It is built. An agent chose it, not he; the
  cleanse recommends retiring it (`NEEDS HIM` 4).
- *0.2.0:* steel and components off the wreck road, at the cost of the road; a negotiated hull or its price; the
  prepared vorrel, *"a euphoric delicacy that is a controlled near-miss with a lethal parasite"*; mirrak hide,
  which casts deeper shade.

## Fuel, and what this place does to the ship

**Fuel: the emergency-slow kind, and worse than most; this is where you buy it.** (Owner's ruling of 2026-11-18:
*"You can also buy it (the intended motivation to have to trade constantly, very Jawa)."*) One plant here is a
fuel and it is built: **pavecrust**, the hardpan lichen, harvests straight to chemfuel, one unit a patch, on
ground nothing else wants. It is thin gleaning, a crew on its knees with scrapers, which is the emergency-slow
route with a Jawa's posture. The rest of the vegetation is meagre by law (*"No lush"*), so rendering biomass is
thinner still. What this country has instead is people on roads: settlements on the big patches, herder camps,
crawlers. Those belong to the campaign layer, and they are where a crew fills its tanks for silver, salvage and
hides. The Long Shade is the trading stop.

**What wears on the ship (owner's ruling of 2026-11-18: in 0.1.0, from what the sources already say).** Less than
anywhere else. The frame is the built one, `src/RimUtinni/ShipShields/`, on his shield rulings saved 2026-09-02
(*"The environment is hostile and immediately goes to work on the ship... Its hull is thick"*): a ship in a hazard
its shield is not set for takes slow wear near the hull, faster after about six hours, with advice and never a
refusal. It knows three hazards. Heat needs 58 degrees of air and this place is in the twenties. Cold does not
apply. The third does:
- **The sandstorm.** The biome's own weather table carries the base game's sandstorm at a low weight (4 in 99,
  read from the biome definition), and the frame recognises a particulate hazard by exactly that weather's sand
  rate. So this is already true in the built game: a ship that sits through a Long Shade sandstorm without its
  particulate screen wears. His ruling on that screen: *"Light kinetic deflectors handle wind, ash, vapor... sand,
  and rain damage completely as well as repels small animals."* *Answer:* the particulate screen, the cheap one.
  Note what else that sentence does here: a screened ship *repels small animals*, so the first rung of the court
  under the hull does not arrive. The crew chooses between a clean hull and game at the ramp.

The rest is company:
- **Heat at the hull from a resting giant.** The megafauna *"absorb enormous heat on the crossing and radiate it
  fiercely once shade is reached"*; an earlier pass had it radiating *"the crossing's furnace-heat into your
  courtyard."* A gloomcast lying against the ship warms what is next to it. This is ordinary air temperature, not
  a new heat. *Answer:* clear the shade from the console before it settles, or put up with a hot flank until it
  moves on.
- **Bulk.** *"A fence is not an argument it understands."* Tenants crowd the ramp, the gear and the cargo. The
  sources' own limit is the rule here: a visitor of that size *"must delay and damage, never hard-block a
  launch."* *Answer:* the dispersal step before lift; keep cargo aboard or walled.
- **The direct sun on the lit side,** mild at this angle and constant. *Answer:* none needed that the sources
  name; no shield is invented here.
- **Where it is parked.** On soft sand, things can come up under it and, in 0.2.0, the swimmer can reach its dew
  ring. On hardpan nothing can, and there is no natural shade for a day's walk. *Answer:* the sheet's own bargain,
  made once at landing.
- (`UNMEASURED`: the khorrak, a resident that eats steel and slag. What the sources describe is a tamed khorrak
  penned among iron slowly turning it to an alloy, *"the knowledge you keep is a working animal, not a research
  node"*. Whether a wild one will eat stacked salvage or anything built is not established by anything read for
  this design; if it does, it belongs on this list.)

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The sun is pinned low; every shadow lies one way and stays; the light is a standing golden hour. | A generated map watched across several days, in more than one weather. | A shadow drawn one way while the cooling falls another. |
| Direct sun is ordinary heat set by geometry alone: shade, a roof or a parasol removes it; hot air still hurts in shade. | The same pawn in the open, behind a rock, under a roof, under a parasol; then the same in a heat wave. | Any private desert heat, angle or offset. A cool-looking shadow that does not cool. |
| Native animals rest in shade, cross lit gaps briskly within what their size allows, and rest again, at ordinary shipped conditions. | A generated map left alone, natives of three sizes. | Animals that only wander as vanilla animals do and happen not to overheat. A small native on ground only a big one could reach. |
| A crew member who begins to overheat in the sun goes to the nearest shade they can reach, recovers and returns to the same work, again and again, and the work gets done. | An ordered job in the open with shade in reach; with shade out of reach; with the only shade too hot to recover in. | A crew member who loops between shade and sun and never works. A drafted crew member who walks off. |
| The landed ship's shade fills with the country's animals in order of how far each can cross, and the pilot's console clears it before launch. | Land; wait; count who is under the hull each day; work the console; launch. | Animals created at the hull. A ship held on the ground by its tenants. |
| A gloomcast is real moving shade, its followers keep to it, it feeds from the sand and leaves plain dung. | A crossing gloomcast, a crew member walking beside it and one walking apart. | Followers that never leave to eat or drink. |
| A mirrak looks like shade and is not: it cools nothing, it can be told from real shade by looking and confirmed by a safe inspection, and what it takes leaves a mark. | A mirrak lying square with the real shadows and one lying across them; an overheated animal; a crew member who inspects first. | A loss with nothing left to read. A mirrak that cannot be told when it happens to lie the right way. |
| A shadow's holder strikes what arrives and returns to cool; nothing here runs prey down. | A dakkra in a shadow, prey arriving spent, prey passing at a distance. | A chase across the open. |
| The lee-side heaps in the shadows can each be searched once for scrap, bone and rare finds. | A generated map; search three heaps of different size. | A heap that pays twice. A heap in the open. |
| The remains in the open still carry their loads, and reaching them is a real crossing for the crew. | A grave within one dash, and one beyond it reached under a parasol. | Loot that comes back after it is taken. |
| The place wears on the ship only through its company: a resting giant warms the hull's flank and crowds the apron, and clearing the shade answers both. | A gloomcast settled at the hull, then dispersed. | Heat with no visible source. |

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary dry desert under a
low sun (standing rule, every mod).

## Shared machinery

**Featured here** (the Long Shade is where each is vital and should be proven):
- **The one sun, and shade as a grid** (the shared shade and heat layers in `CreatureBehaviors`:
  directional, roof, gear and moving shade feeding vanilla heat). His ruling began here: *"It can't be a new
  'kind' of heat."* It runs on every day-side map; this is the biome built on it. The tree-shade model the
  forests need is the same question with leaves.
- **Animals that seek shade and dash between it** (the shared patch graph and wild-animal sun escape).
- **People who seek shade when they overheat** (shared, cross-biome, **not built**: *"This mechanic should be
  true everywhere in the biomes."*).
- **Shade gear:** parasols and quick roofs, a cross-biome family (*"this MUST be applied on other biomes where
  heat is extreme too"*).
- **A pinned sun and sky** (the shared pinned-sun types, configured here as golden hour).
- **Moving shade from a body, and followers that keep to it.**

**Merely active here:** ambush from a fixed spot (the same shape as the water ambushers elsewhere); real flight
(the pirrik and skiralim); walkable deep sand from `FlowWorks`; wreck salvage (`Wreckage`); bones from butchery;
the acoustic scanner's readings; wind (nothing here features it); the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**0.1.0, the stop**
- The land: sand, soil, hardpan and walkable deep sand; dry weather; the pinned golden-hour sun. (built)
- Shade and the one sun feeding ordinary heat; parasols and quick roofs. (built, shared; current source still
  carries an older biome heat that must be brought into line)
- Natives that rest, dash and rest, sorted by size. (built, unproven)
- Crew who seek shade when they begin to overheat, and go back to work. (unbuilt, shared)
- The gloomcast as moving shade, its followers, its sand-feeding and plain dung. (built)
- The mirrak, with look-then-inspect and a readable loss. (built)
- The dakkra holding a shadow. (built)
- The ship's shade filling by stages, and the console clearing it. (built; his card pick of 2026-09-30; moved in
  against the cleanse, see `rewrite_choices.md`)
- The lee-side heaps and searching them. (built; his card pick of 2026-09-30; moved in)
- The empty patch as the tell of a held shadow. (his rule by card; the static markers are built)
- The shadespire, pavecrust and maidenbloom as plants on the map; pavecrust scraps as a thin fuel. (built; their
  special growing rules are not)
- The sandstorm as the one hazard the ship-shield frame sees here. (built)
- The sun graves and their loads. (built; moved in)
- The native roster, ordinary forage, taming and stock; fliers that really fly. (built)
- What the place does to the landed ship, as stated above. (a resting giant's warmth is new, small work)

**0.2.0, the stop with company**
- The wreck road across the widest gap, its salvage, and the dead crawler at its end. (built)
- The returning Jawa clan: pay, trade or argue to keep the hull, or watch it towed. (the claim and tow are built; the
  negotiation his answer of 2026-11-10 asked for is not)
- The vorrel: the fruit that kills and aims the body at shade, and the prepared dish. (built)
- The stampede for the roof; the harrok's strike from a strip of shade; tollok ticks caught by resting in
  wild shade and never in shade the crew made. (built)
- The smoke haze from fires beyond the horizon. (built; its ash act was cut)
- Dung that feeds plants and seeds young life; plants bound to dung and to hardpan; the dew-fringe bound to the
  shadow's rim. (part built)
- Leachmoss and venomvine defending a patch. (built)
- Mirrak hide casting deeper shade; the khorrak's vacstone. (built)
- The sippra walking the exact rim; the skiralim dropping from a scarp. (unbuilt)
- Heat and footfall sound beds; the arrival letter. (built or unknown)
- The young sarlacc's road. (built at the campaign tier)

**Later (a crew that stays, a colony, or the campaign)**
- Lessons from study, and the overlay showing how far a person can go and return.
- The harbour ladder for a built base; thin buildings farming the dew line; living off the rim.
- Named wide gaps (*"named at the repaint window, with the owner — not before"*); known routes as something to
  map; settlements, herder camps and tribe holdings as places.
- The shade ideas he set aside with *"Will consider the rest later"* (2026-09-29) and never returned to: the
  desperate moisture farm besieged by the ecosystem, the waiting camp at the last patch, the shade-rent men at a
  dead crawler, the broken caravan in the gap, route cairns, the shade-cool cellars, the dew wells that still
  bead water, the dry vaporator stands, shade debt, the skellok carpet, the noon stone, reading and mimicking the
  herds' calls.
- A hardpan terrain of our own, and the dew condenser as something learned.
- The sun god's precepts and the two found rites, the Shade Tithe and the Shadow Walk (parked or tabled by him).
- The ship's shade awning, pavement flooring and vorrel galley.
- Walking with the giant across the world map (the Stillsand's by an earlier boundary).

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- A desert heat of its own kind (the one-sun rulings of 2026-09-29 and 2026-10-19).
- The smoke calendar's ash act: growth pulse and locked sand (cut 2026-10-23: *"nothing about shade or
  crossing"*).
- Pursuit predators; boom-and-bust populations; any day and night; rain; fire that starts here.
- Shade as a connected network to travel within (*"That was wrong"*, owner, 2026-09-05).
- **The gnomon line and the farm on the horizon with its heliograph** (cut 2026-09-29, his words: *"No on 6 7."*).
  The ideation's own rulings section still shows them as "not yet ruled"; the ledger note written minutes later is
  the record. Heliograph signalling survives only inside the separate Solar Mirrors mod, where he liked it.
- The name thommak (it is the gloomcast); the sand-lion row; the kreetle and gizka rows here.
- Cut from this biome's cast on his word of 2026-10-05 (*"Go ahead and do the moves and cuts now please."*):
  kudda, ossik, thurra and the mature fleshbeast. Moved out the same day: the ultracactus, the ulgga and the
  vosska to the Stillsand, the ommok to the Miasma, the truffle mole to the Leaning Scrub.
- The sun god's country as built content (*"Ignore ideoligion concept for now."*, 2026-09-29), with its event the
  Searing; a sarlacc egg clutch in the middens (cut by its own pass).
- Colonists that plan routes by shade (his answer of 2026-11-10: they react; the beasts are the evolved ones).
- **Recommended for dropping by the cleanse, not his:** haze lengthening shadows by its own multiplier (against
  pure geometry); the tazzok's ash-only schedule (its ash act is gone). The cleanse also recommended retiring the
  lure awning and the shade mast. This design does not follow it on either: he admitted the lure awning by card
  on 2026-10-08 (*"the one biome where you can bait with geometry"*) and it is built, so it sits in 0.2.0 with the
  other admitted extras; and the mast is this biome's gift to the ship (`NEEDS HIM` 4).

## NEEDS HIM

Each is tagged with one theme word.

1. **[other] The discussion he said was owed.** On 2026-11-10 he wrote *"We need a deeper design discussion here"* about
   what people do when they overheat, and it has not been held. This design is written on the cleanse's default:
   a crew member in harmful direct sun, before the heatstroke turns serious, goes to the nearest reachable shade
   they can actually recover in, then resumes; drafted and broken people are left alone. It is a rule for every
   biome and it is unbuilt. *That default.* *Something lighter:* a warning and nothing automatic. *Something
   smarter:* which contradicts his own "they aren't evolved beings from that biome".
2. **[other] Is this the crew's home ground?** The design plays the Long Shade as the one place the crew is competent on
   foot and the ship is the novelty. If instead the clan's roads are in the deep desert or elsewhere, the crew is
   as lost here as anywhere and the jokes change sides. *Home ground* (default). *Not home:* rewrite the tone, not
   the mechanics.
3. **[cover] Does the smoke haze hide the ship?** His card gives canopy, steam and fog one step of cover. Haze is
   none of the three and does the same job to the eye. *No cover in 0.1.0; one step under haze when haze arrives
   in 0.2.0* (default). *Never:* the Long Shade is the planet's bare table. *Now:* pull the haze into 0.1.0 with
   it.
4. **[hull] Does the ship keep its mast?** The long-shade mast is this biome's entry on the list he asked for on
   2026-09-24 (what each biome adds to the ship). An agent picked it on 2026-11-11 after a judge found the lure
   awning *"only shaded its footprint"*; it was carded to him for review and no answer is recorded. The cleanse of
   2026-11-17 recommends retiring it as against the rule that shade gear is parasols and roofs. *Keep it as the
   ship's gift* (default here: the lens makes the ship the point, and an open deck is what a roof cannot shade).
   *Retire it:* the Long Shade then gives the ship nothing, and something else must be chosen.
5. **[scope] One signature, or the pieces he picked?** His card of 2026-11-17: a biome's first version holds
   *"Land, life, one signature."* The cleanse chose real and false shelter as the signature and switched off the
   ship's shade filling up, the heaps, the sun graves, the wreck road, the vorrel and the rest. This design brings
   the first three back into 0.1.0. Two of them (the ship as refuge, the heaps) are his own card picks of
   2026-09-30, and the lens of 2026-11-18 makes the ship the subject. *As this design has it* (default). *Strictly
   one signature:* 0.1.0 is the sun, the dash, the gloomcast and the mirrak, and the ship's shade is just shade.
6. **[other] Should lightning strike here?** The sheet bans fire that starts here (*"Ash and smoke ARRIVE; they do
   not originate"*). The biome's weather table carries dry thunderstorms at weight 4 in 99. *Remove them*
   (default). *Keep them:* rare fires on ground the sheet says never burns of itself.
