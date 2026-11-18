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

An earlier design pass said it in six words: *"hospitality you cannot decline."* Every other biome threatens the
ship. This one moves in under it.

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
pavement. Shade is not cover: a hull in a shadow is still a hull. This is the price of the easiest living on the
day side. (*0.2.0:* the smoke haze that drifts in from the Pyrelands' fires dims the sun over the whole map; it is
the natural candidate for one step of cover while it lasts, and that is `NEEDS HIM` below, not assumed.)

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
  ground no native can stand on.
- **The shade is the dig site.** The wind never reverses, so *"everything that blows across this desert ends up
  in a shadow: nutrients, and also bones, debris and wreckage."* Heaps lie in the lee of the big shade-casters and
  can be searched once each, for scrap, bone and now and then a real find. Every heap is inside a shadow, and
  every shadow has tenants.
- **Soft ground and hard ground are opposite bargains.** Sand holds the rocks that cast shade, and things can
  come up through it. Hardpan is safe from below and bare of shelter. Deep sand can be walked, *"just very
  slowly."*

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
   in its shade with its flock wheeling in, and radiates the heat of its crossing at the hull.
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

*0.2.0 adds:* the road of dead machines across the widest gap, each one stride from the next, and the dead
sandcrawler at its end with the whole country sheltering in its shadow; the rival Jawa clan that comes back for that hull, to be paid, traded with or argued with;
the fruit that looks safe; a herd stampeding for the roof; the sky going orange with other people's smoke.

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
- **Midden finds:** scrap, bone, slag, and the occasional component cache or old corpse with its gear.
- **What the sun graves were carrying.**
- **Ultracactus pad,** the forage of the open ground: *"The ultracactus is not canon, I made it."* (owner,
  2026-09-27).
- **Tame stock:** *"the pack and draught animals the campaign runs on."*
- **Flat pavement stone.**
- *0.2.0:* steel and components off the wreck road, at the cost of the road; a negotiated hull or its price; the
  prepared vorrel, *"a euphoric delicacy that is a controlled near-miss with a lethal parasite"*; mirrak hide,
  which casts deeper shade.

## Fuel, and what this place does to the ship

**Fuel: the emergency-slow kind, and worse than most; this is where you buy it.** (Owner's ruling of 2026-11-18:
*"You can also buy it (the intended motivation to have to trade constantly, very Jawa)."*) Nothing in any Long
Shade source is a fuel. The vegetation is meagre by law (*"No lush"*), so even rendering biomass is thin work.
What this country has instead is people on roads: settlements on the big patches, herder camps, crawlers. Those
belong to the campaign layer, and they are where a crew fills its tanks for silver, salvage and hides. The Long
Shade is the trading stop.

**What wears on the ship (owner's ruling of 2026-11-18: in 0.1.0, from what the sources already say).** Less than
anywhere else, and all of it is company:
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
- (`UNMEASURED`: the khorrak, a resident that eats steel and slag. Whether it will eat stacked salvage or anything
  built is not established by anything read for this design; if it does, it belongs on this list.)

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
- The ship's shade filling by stages, and the console clearing it. (built; moved in, see `rewrite_choices.md`)
- The lee-side heaps and searching them. (built; moved in)
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
- The desperate moisture farm, the waiting camp, the gnomon line and the other shade ideas never ruled.
- The sun god's precepts and the two found rites, the Shade Tithe and the Shadow Walk (parked or tabled by him).
- The ship's shade awning, pavement flooring and vorrel galley.
- Walking with the giant across the world map (the Stillsand's by an earlier boundary).

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- A desert heat of its own kind (the one-sun rulings of 2026-09-29 and 2026-10-19).
- The smoke calendar's ash act: growth pulse and locked sand (cut 2026-10-23: *"nothing about shade or
  crossing"*).
- Pursuit predators; boom-and-bust populations; any day and night; rain; fire that starts here.
- Shade as a connected network to travel within (*"That was wrong"*, owner, 2026-09-05).
- The name thommak (it is the gloomcast); the sand-lion row; the kreetle and gizka rows here.
- Colonists that plan routes by shade (his answer of 2026-11-10: they react; the beasts are the evolved ones).
- **Recommended for dropping, not yet his:** the lure awning (ordinary roofs and the hull already do it); the
  chitin shade mast (against parasols-and-roofs); haze lengthening shadows by its own multiplier (against pure
  geometry); the tazzok's ash-only schedule (its ash act is gone).

## NEEDS HIM

1. **The discussion he said was owed.** On 2026-11-10 he wrote *"We need a deeper design discussion here"* about
   what people do when they overheat, and it has not been held. This design is written on the cleanse's default:
   a crew member in harmful direct sun, before the heatstroke turns serious, goes to the nearest reachable shade
   they can actually recover in, then resumes; drafted and broken people are left alone. It is a rule for every
   biome and it is unbuilt. *That default.* *Something lighter:* a warning and nothing automatic. *Something
   smarter:* which contradicts his own "they aren't evolved beings from that biome".
2. **Is this the crew's home ground?** The design plays the Long Shade as the one place the crew is competent on
   foot and the ship is the novelty. If instead the clan's roads are in the deep desert or elsewhere, the crew is
   as lost here as anywhere and the jokes change sides. *Home ground* (default). *Not home:* rewrite the tone, not
   the mechanics.
3. **Does the smoke haze hide the ship?** His card gives canopy, steam and fog one step of cover. Haze is none of
   the three and does the same job to the eye. *No cover in 0.1.0; one step under haze when haze arrives in 0.2.0*
   (default). *Never:* the Long Shade is the planet's bare table. *Now:* pull the haze into 0.1.0 with it.
