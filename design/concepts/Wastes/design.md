# The Wastes: the design, seen from the ship

**Status:** the one design document for the Wastes biome (`RM_Wastes`, source `src/RimMandrake/Wastes/`; the older
documents call it the Wasteland), rewritten 2026-11-18 on the owner's instruction to see every biome "through the
lens of Utinni". It replaces the frozen definition sheet, the survivor cast bible and the cleanse proposal as the
place to read; what happened to every idea in them is in `design/concepts/Wastes/rewrite_choices.md`. Nothing has
been deleted yet. This is a design document only and it launches nothing.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/Wastes/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Wastes has no locked sheet or tree; its only pipeline material is the cleanse
proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) or the special-mechanics review of 2026-10-22 found it in source; it
does not mean it has passed anything, except where a live check is named.

---

## What this place is

> *"A just-lost sunset, flickering with wrathful lightning."* (`wastes.md`, header)

The planet's drain. *"A wasteland is anywhere the planet drains to and nothing drains from"*: the basins where
dying rivers evaporate to salt and brine, the dark shoulder where the sky's soot falls and no rain will ever wash
it, and the old war's poisons, *"used and left"*. *"Nothing recycles here — water doesn't leave, fallout doesn't
wash, history doesn't decay — and for all the ages since the war it has also been the place you throw what nobody
wants, because it was already ruined."*

> *"Where rivers come to die and nothing ever leaves: salt, ash and fallout pile up forever. The land is the
> monster, and the creatures are its victims."* (owner, picked by card, 2026-10-20: the experience line)

It is the gentlest-looking deadly place on Ash'karr. The sheet: *"the land itself is the only danger, and there is
almost nothing alive to fear. You can sleep here without a watch. The ground will still be killing you while you
do."*

And what does live here is doing fine. The owner's ruling of 2026-09-28 turned the whole cast from sufferers into
survivors: *"ugly warty life that was already tough enough to survive the waste products… creatures that already
ate the waste of other beings, survived extreme environments."* They have plain ugly names (Scumrat, Boilhide,
Sloghog) and they are content.

**Seen from the ship, the Wastes is three stops with one name.** By ruling it is one biome that varies only by
where the tile sits: the **warm basins** (blinding salt-white under a low sun), the **margin**, and the **dark
scour** (cold, high, lit only by the stormwall's glow on one horizon). Which one the crew lands in decides what the
place hides, what it costs and how long the stop can run.

It is also, from a scavenger's side of the counter, the best-stocked shelf on the planet: *"ground nobody can
live on is ground nobody has stripped"*, and *"the prize compounds: every failed expedition adds itself to the
hoard."* The people who usually die trying are Junkers. *"Junker corpses are more common than anyone else's."*

The crew are small, hooded, skittish and built for dry heat (`reconciled_lore/05_the_clan.md`). The basins look
like home. That is the trap.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28: *"around every 5-8 days, keep 'em running"*; ladder in
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked provisional): a probe
droid five to eight days after landing, then scouts with a spotter, a strike team, an ion cordon on the ship, a
breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if the one before
succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last, as the outer edge** (his ruling of 2026-11-18: the numbers are *"the outer edge
allowable for each biome"*). On open ground the ladder's arithmetic gives a probe on day 5 to 8, a first real
fight around day 12 to 20 and the bombardment around day 20 to 32 if the Empire wins every step.
- **In a warm basin: about a month.** Open salt under a sun that never sets. Nothing hides.
- **In the dark scour: about six to nine weeks.** A crew the search reads as discreet or hidden has every wait
  multiplied by 1.4 or by 2 (`EmpireLadderMath.BandIntervalMultiplier`), and the scour is dark.

Neither is the usual stay. The Wastes ends a stop by dose: nothing here attacks, nothing here hurries, and every
day costs a little more of everyone's body.

**Cover from orbit (his ruling of 2026-11-18: partial cover, by biome).** It depends on the family, and that is
the choice of where to land.
- *Warm basins:* **none** in clear air.
- *Any family, while an ash storm blows:* **one step.** The sheet calls the storms *"blinding"*; this design
  counts blowing ash with canopy, steam and fog. It lasts as long as the storm does, and the storm charges for it.
- *The dark scour:* **full dark, which still pauses the search.** The sheet: *"Past arc ~100 the only light is the
  stormwall's glow on one horizon."* His ruling of 2026-08-05 pauses the orbital clock on dark tiles; only the
  Abyss is on the built list, and adding the scour's tiles is the small build this biome owes. At ground level
  the same rule as the Sump's holds: a watcher sees a target in darkness only from six cells
  (`EmpireLadderMath.Sees`), so every lamp is a choice.

**Fuel (his ruling of 2026-11-18).** The Wastes is one of the **richer sources**, by three routes that are all in
the sources.
- **Soot bricks.** The sootgrazer *"eats deposition itself and presses what it can't burn into brick"*:
  *"fuel-grade soot bricks ... sells low but the supply is endless where the sky keeps falling."* A penned
  sootgrazer on ash is a fuel plant with legs. (Built; two of its live checks failed on 2026-10-08 and were not
  re-run.)
- **Wartshrub.** A scarce wild shrub whose harvest is chemfuel outright. (Built; its harvest passed a live re-run
  on 2026-10-08.)
- **Buying it.** The Junkers *"claim ownership of the dump"* and extract *"usable nuclear (or worse) fuel"* from
  it. Where the campaign places a Junker toll gate, the crew can buy.
The fourth route is the one the sheet calls *"the cursed prize"*: the vault-roots' *"densely concentrated fuel
deposits"*. Digging them out is *"exactly what the Junkers do and exactly what reopens the wound."* In these
versions it stays cursed and unbuilt as a fuel: destroying a loaded root releases what it bound, and that is all.
The Wastes is not replete. Rendering soot bricks into ship fuel is the small build this ruling asks for.

**What the place does to the ship (his ruling of 2026-11-18, in 0.1.0).** It sandblasts it and buries it. The
sheet's ash storm is *"blinding, abrasive, conductive — and radiologically live"*, and the built storm already
drifts ash over gear so that it has to be dug out afterwards. A ship that sits through storms is scoured, its
yard is under drift and its apron has become some of the hottest ground on the map. In the terminator pockets
only, the Cinderwire storm adds what the sheet calls *"EMP, burn, dose and burial in one weather event"*, a wind
*"strong enough to throw wreckage"* that stuns powered things (0.2.0). The answers are a **shield** and a
**shovel**: the aerosol screen learned in the Warscar is ruled to work on *"the Wasteland's ash fall"*; without
one, the crew digs the yard out by hand and scrubs the apron after every blow. What is not built: any effect of
ash on the hull itself. The promise below is written for the yard, the apron and the people, and marks the hull
skin as owed.

---

## The first minutes

In a basin the ship comes down onto a white floor so bright the crew's hoods go down over their eyes. The sheet's
silhouette law is the whole view: *"horizons of nothing, then one enormous thing — a rib-vault, a dead hull, a
throat mound."* In the scour it comes down into the dark with one horizon burning: *"a permanent just-lost sunset
with lightning in it. Navigation trivial; morale not."*

Nothing runs from the ship and nothing comes at it. A line of fist-sized beetles files past the landing struts,
each one carrying a scrap of something.

The first thing a careful crew does is look at where the plants are, because here the rule runs backwards:
*"the vegetation is the dosimeter ... the 'lushest' ground in a Wasteland is the deadliest ... locals camp where
nothing grows."* A crew that parked beside the only green on the map has parked on the worst of it.

Before the first hour is out the player should have seen three things without going looking: moss thick over one
patch of ground and absent from another; a wreck that nobody has stripped; and a beetle walking off with
something that was the crew's.

## The first day

- **The ground is the danger.** Old contamination sits in the ash flats, around the wrecks and along the brine.
  Standing on it, working on it and sleeping beside it is paid for in the body, slowly. The owner's answer of
  2026-11-10 on how well it can be judged: *"Reliable rough comparison: landscape observation distinguishes safer
  from worse exposure, with closer inspection refining route and duration choices."*
- **The refuge is the ship.** His answer the same day on what makes an ordinary day matter: *"Keeping a habitable
  refuge leads. Resisting accumulated pollution at home makes the land matter between expeditions and requires
  ongoing maintenance."* Clean decks, a clean apron, a roof: the crew goes out to work and comes back to the one
  place that is not killing it, and keeping it that way is a chore that never ends.
- **Nothing rots.** *"Rot runs slow to nothing."* Food left out keeps. So does everything anyone ever left here:
  *"What you leave, you find again"*, with the sheet's warning attached: *"you may not want what you left here
  too long."*
- **The salvage.** Rusted hulls, tanks, the wrecks of everyone who tried before, and sealed **warcasket
  sarcophagi**: *"a dead Junker in an adjusted warcasket is a sealed salvage-within-salvage: suit, tools, and the
  half-extracted core still in its grips."*
- **The neighbours.** Scumrats, fat on what nothing else will touch. Boilhides, a herd whose hides are *"a
  landscape of sealed boils"*, which run. A gravelgut, a low armoured slab that eats gravel and *"passes it as
  smooth sorted pebbles the locals kick apart to read what is buried underneath."* None of them wants anything
  from the crew, with one exception (below).
- **The rib-vaults.** *"The bones of creatures that did not understand what they wandered into are the
  monuments"*: the only architecture for miles and *"the traditional ash-storm shelter (with the traditional
  price: the bones lie where the dust settles thickest)."*

## The first week

- **The ash storm.** *"Centuries of deposition picked up and re-dealt."* Anyone in the open is dosed; the ground
  it crosses is dirtier afterwards; loose gear is buried and has to be dug up. *"The storm redraws the danger
  map: hot dust scoured off one field and laid on another; re-survey after every storm, trust no old reading."*
- **The exhumation lottery.** *"Storms exhume — every blow reveals a trench line, a hull, a cache, a crime
  somewhere, and buries something else."* After each storm the map has new things on it. On a planet whose map is
  fixed forever, this is *"the single place the map is allowed to regenerate."* For a crew of scavengers it is
  the reason to sit through a storm.
- **The cinderfelt.** A felt-grey mat that grows only on fresh ash fall and marks where the last storm laid its
  load, *"the way the dosimeter lawn marks the ground."*
- **The beetle that trades up.** A wild gripper arrives already carrying a piece of junk. It finds something of
  the crew's that is worth more, swaps, and leaves. Hit it and it drops what it has. Tame it and it never steals
  again. (All seven checks of this passed live on 2026-10-08.)
- **The herd that pays.** A sloghog penned on poisoned ground *"periodically coughs up the poison as a stone you
  can sell"*; a sootgrazer on ash presses bricks. *"A kept herd is a slow refinery."* Both fit in a hold.
- **The hill that walks.** Hours of warning: a tremor, dust, loose metal on the ground creeping to point at one
  edge of the map. Then the Middenshell arrives. See the moments.
- **The dose adds up.** By the end of a week the question is who has been outside too much.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The swap.** *On screen:* a beetle sets a bent spoon down beside the crew's best component, picks up the
   component, and files away. *Why it is funny:* it is the crew's own business model, done to them, by a beetle,
   with a straight face.
2. **Parked on the green.** *On screen:* the moss is thickest in a ring around the ship's apron, and the crew
   who have been sleeping there are the sickest. *Why it lands:* at home, green means water.
3. **The storm deals.** *On screen:* a wall of ash crosses the map; when it has gone, the crate yard is a row of
   humps and there is a hull standing clear of the flat that was not there yesterday.
4. **The Middenshell.** *On screen:* a living rampart **twenty cells wide**, *"landscape that turns out to be an
   animal"*, crossing the map at a crawl, wearing *"centuries of what it processed"* fused into its shell,
   flattening whatever is in front of it and leaving a hot trail and a scatter of small bezoars behind. It is
   never hostile. It *"does not fight, it does not hunt, it barely notices."* *Why it lands:* the crew can see
   the salvage embedded in it going by, and it is the dose of a lifetime to stand close enough to pry at it.
5. **The yard and the giant.** *On screen:* the route overlay runs through the crew's outdoor stockpile; the
   crew hauls scrap out of its path while the loose metal on the ground points the way it is coming. (It goes
   around the ship itself: the built crawl avoids gravship parts.)
6. **The sloghog coughs.** *On screen:* a warty, barrel-bodied hog with *"content half-shut eyes"* stops grazing
   poison, heaves, and produces a dense lump worth money.
7. **The sarcophagus.** *On screen:* a sealed warcasket is cracked open and inside is a dead Junker, a full set of
   tools, and a half-extracted core still in its grips, which the crew will now have to decide about.
8. **The warm boulder** (dark scour). *On screen:* in the cold dark, one rock with no frost on it and steam where
   it sits. Something very hot bedded there, and it is still nearby.
9. **The grimewing.** *On screen:* a half-bald scavenger bird riding a storm's edge, really flying, down onto
   whatever the storm just dug up.

## When the Empire arrives

- **The ground does not care whose boots.** A strike team that camps on the handiest flat ground has camped where
  the crew learned not to. Their dose runs from the hour they land.
- **The storm blinds everyone and buries the besiegers' gear with the crew's.** A crew that knows a storm is a
  day out can choose to be inside for it.
- **Nothing here will help either side.** No animal in the Wastes hunts people; the sheet bans it.
- **In the scour, the dark.** Watchers see six cells. A cold, unlit ship is hard to find from the ground.
- *0.2.0:* **the Middenshell can be steered.** Its route bends toward waste stockpiles. A crew that stacks waste
  on the far side of a siege camp has aimed a twenty-cell animal at it, and nobody can call that an attack.
- *0.2.0:* **the Cinderwire** (terminator pockets only) stuns powered buildings in pulses and strikes lightning.
  The Empire's cordon is powered.
- *0.2.0:* **the Deadlight Halo**, a quieter storm that raises the dose on everything outside for as long as it
  glows.
- *Later, and the campaign's:* **the waste run.** A ship whose cask bays hold the planet's worst waste has five
  places to put it, and the sheet's first is *"Drop it on the Empire — an act of war dressed as sanitation."*

## Who else attacks; who hates the Empire

- **Nobody attacks.** *"The wildlife is never the biome's headline threat."* The scabspinner hunts scumrats and
  flees people; a gristleswarm pack fights back as one if one is hurt; a gravelgut *"hits like a wall if
  attacked."* That is the whole list.
- **The Junkers,** where the campaign places them: *"crude sovereigns of the dump"*, charging everyone for *"the
  rite of dropping waste here, making meager credit off a claim that is legally absurd and universally honored,
  because nobody else wants to enforce anything in a Wasteland."* They are who the crew trades with and who the
  crew is trespassing on. Whether they fight the Empire is `UNSETTLED`.
- **Wildsteam and Deepwater** *"both sincerely care about the planet's future habitability and have no
  leverage"*. They want hands. So do the Junkers. The sheet: *"the players are the only hands all three can
  use."* Campaign layer.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The dose, which only goes one way while the crew is on this ground.
- The ship's own apron and decks losing the fight with what is tracked and blown in.
- A storm season that keeps re-burying the yard.
- In the scour, the cold.

**Stay, longer than the Empire would like:**
- Nothing here hunts, raids or grows over anything. *"You can sleep here without a watch."*
- Nothing rots, so the larder lasts.
- The dark scour's dark, and any storm's ash.
- Fuel on the hoof and in the shrubs.
- The plants are slowly burying the poison: *"the flora heals by sequestration"*. Leave them alone and the ground
  under them is a little better every year, which no stop will see. Dig them up and it is worse at once, which
  any stop can.

## What the crew takes away

- **War salvage nobody has stripped,** and whatever each storm turned up.
- **Warcasket sarcophagi and what is in them.**
- **A sloghog or a sootgrazer in the hold,** and their bezoars and bricks.
- **Fuel:** soot bricks, wartshrub chemfuel, or barrels bought at a toll gate.
- **Salt, glass and brine minerals** (the brine beds are 0.2.0).
- **A tamed gripper,** which never steals from its own crew, by design.
- **The dose** each of them is carrying.
- *0.2.0:* **the waste cask bay,** the Wastes' named gift to the ship: *"the only way a gravship may carry the
  planet's waste at all"*, with launch refused if a cask is loose or the bay is unsafe; and **paid cargo**: the
  tipping trade pays a crew to take casks. A penned sloghog beside the bay turns casks into bezoars in flight.
- *0.2.0:* **a smolderback,** *"a living furnace that heats a shelter all winter and irradiates it the entire
  time."*

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Ground differs in how fast it harms, and the plants and the look of the ground are enough to tell better from worse before inspecting. | Two routes to the same wreck, one over thick moss and ash, one over bare crust, with the pollution overlay hidden (a look at a joint sitting, then the doses read from state). | The route that looked worse did dose more. A difference the eye cannot see must not exist. |
| A clean, roofed refuge stays habitable only with upkeep; tracked and blown contamination comes in. | A landed ship with a cleaned apron through two storms, tended and untended. | The untended ship's decks and apron measurably foul; cleaning that is done stays done until something new arrives. |
| An ash storm doses people in the open, dirties ground, buries loose gear that can be dug up whole, and leaves cinderfelt on the fresh fall. | A natural storm with one pawn out, one roofed, and a crate in the open. | The dug-out crate is the same crate. Cinderfelt grows only where ash actually fell. |
| After a storm there are finds on the map that were not there before, and some old ones are gone under. | Record the map's visible salvage before and after a natural storm. | The total hoard is finite and tracked: a find revealed is one that was buried, never spawned from nothing. |
| Nothing rots, in the warm basins too. | Raw food left out in a basin for the visit. | The same food on another biome's map at the same temperature rots. |
| Destroying a loaded vault-root releases what it bound, once. | Cut, burn and dig one; read the ground. | A root that had bound nothing releases nothing. |
| Every resident is visibly marked, none hunts people, and the real flyer really flies. | A crew member walks through each species; the grimewing's flight read from its flight state. | A provoked gravelgut or gristleswarm fights; an unprovoked one never does. |
| A wild gripper swaps its junk for something better of the crew's and drops its haul when hurt; a tamed one does not steal. | Unguarded valuables near a wild gripper; then the same with a tamed one. | The stolen thing is the thing recovered. Forbidden items are left alone. |
| A sloghog on poisoned ground yields bezoars and a sootgrazer on ash yields soot bricks, faster there than on clean ground. | One of each penned on dirty ground and one of each on clean floor. | The clean-floor pair lag visibly. |
| The Middenshell is announced hours ahead, crosses on a route the player can read, flattens what is in its path except the ship, doses whoever stands near, never attacks, and leaves a trail. | Let one arrive with a yard in its path and the ship beside it. | Shooting it does not turn it on the crew. Nothing it crushes vanishes without wreckage or a message. The ship's parts are untouched. |
| In the dark scour an unlit crew is not seen by a watcher beyond a few cells; a lit one is. | A probe passes an unlit and a lamplit camp at the same distance on a scour tile. | The same pass on a basin tile sees both. |
| Wartshrub and soot bricks give fuel. | Harvest one; pen the other; put the product in a tank. | |

Settings: one switch per major feature, defaults as shipped, everything off leaves a dry, bleak flat with odd
animals (standing rule, every mod).

## Shared machinery

**Featured here** (the Wastes is where each is vital and should be proven):
- **Ground that carries a dose, and an account of where every bit of it came from and went** (Biotech's pollution
  grid, by his ruling of 2026-09-28: *"radiation AND pollution, ridden mostly on the Biotech pollution
  mechanism"*). Every poisoned biome uses the grid; only here is it the whole design.
- **Storms that move the ground and what is under it** (the ash storm on the `MovingDunes` engine, ruled the same
  day: drift, burial and exhumation are the dunes' own mechanism with ash for sand).
- **Plants that show a hidden quantity** (radmoss following the dose; cinderfelt following the fall).
- **Animals that turn a ground condition into goods** (`RM_CompProcessorGatherable`: sloghog and sootgrazer).
- **A giant that is a moving place, not a fighter** (the Middenshell, built as a twenty-by-twenty building that
  crawls; not the huge-pawn engine).
- **An animal that takes and leaves real items** (the gripper; the Sump's kethrel is its cousin).

**Merely active here:** the airborne-poison screen from the Warscar; darkness as cover from watchers (the Sump and
the Abyss feature it); wreck scatter and weathering (`Wreckage`); warcaskets as a suit class (`Warcasket`, ruled
on 2026-09-28 as *"a primitive tank around a person"*, for every hostile terrain on the planet); real flight; the
one sun from geometry (low over the basins, absent in the scour; ambient cold is ordinary cold); thirst; bones;
the ship's acoustic scanner; the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket.

**0.1.0, the stop**
- The land in its three families: salt, ash, broken ground, brine, preserved remains; old contamination laid once
  on ash flats, wreck surrounds and brine margins with cleaner ground left to build on; no rain, no snow; the
  stormwall's glow on one horizon in the scour. (built; the horizon light's direction is owed)
- Dose from ground and air, comparable by eye; the ship as the refuge that needs upkeep. (built on the pollution
  grid; the by-eye comparison is the cleanse's own unproven hypothesis)
- The ash storm: dose, dirtied ground, drift and burial, exhumation of buried salvage, cinderfelt. (built; the
  "doses an unroofed pawn" check failed live on 2026-10-08 and the dunes binding was broken at the time; both are
  defects to fix)
- A finite, tracked buried hoard laid down before the crew arrives. (not built; the cleanse specified it for a
  later version; moved in)
- Preservation: nothing rots. (built)
- Radmoss, vault-root and what destroying a loaded root does; scumgrass, pusberry, boilbulb, wartshrub. (built)
- The cast as animals with ordinary lives: scumrat, slagmole, scabspinner, boilhide, gristleswarm and its soot
  cousin, gravelgut, kroffa, frethik, scumslider, grimewing with real flight. (built)
- The gripper's swap. (built; live pass; moved in)
- Sloghog bezoars and sootgrazer soot bricks. (built; moved in; two failed live checks to fix)
- The Middenshell: omen, arrival, readable route, crawl, crushing, proximity dose, trail. (built; eight of nine
  body checks and six of seven arrival checks passed live; the proximity dose failed and was not re-run. Moved in.)
- Wrecks and sealed warcasket sarcophagi as salvage. (wrecks built; a real sealed corpse inside is not)
- Cover by family, and dark-scour tiles on the orbital pause list. (owed, small)
- Soot bricks rendered to ship fuel. (owed, small)

**0.2.0, the stop with company**
- The Middenshell's lure toward waste stockpiles and its tentacle that eats things near it. (built, never seen
  live)
- The Deadlight Halo and the Cinderwire storm, with their staged warnings. (built; the dose-after-warning check
  failed live)
- The smolderback: heat and dose in one animal. (built, never measured)
- Waste casks, the cask bay, the launch refusal, herd-assisted processing aboard, reburial; the Rite of Tipping
  with its paid deliveries, evidence requests, containment grant and discovery. (built; the core passed live)
- Brine beds, sparkcrab and brineleech, brine plate, the shock from eating a brineleech raw. (built)
- The processors slowly cleaning the cell they stand on. (built)
- The grimewing circling a fresh exhumation. (not built)
- The ship's acoustic scanner readings here. (built)

**Later (a crew that stays, a colony, or the campaign layer)**
- The waste run and its five destinations; the throat cask; the Stenchlands as *"the environmental doomsday
  clock"* and the three factions around it: campaign.
- Junker toll gates, roads of shame, waste caravans, buried crimes, dead sarlacc throats as dungeons: campaign
  and the inhabited pass.
- The dead Middenshell as a permanent bezoar quarry (it has to be killed first, which no stop does).
- Vault-root ore as a fuel economy. The top-down healing of the land, which runs on a scale of ages.
- Radiation-scrubbing drugs and the dive structure priced in a dose budget.
- A second, native giant that passes through as a huge pawn.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Anomaly entities, bioweapon lifeforms, wildlife as the headline threat, unmarked wildlife, rain, anything that
  depends on spoilage, plasma storms outside the terminator pockets (sheet bans).
- The pathos reading of the fauna (revised 2026-09-28: survivors, not sufferers), and with it the donor cast.
- Invented-exotic or Star Wars names for this cast (same ruling).
- The dead brine-deposits toggle (deleted 2026-10-23).
- **Recommended for dropping, not yet his:** the raw kroffa-milk mood bonus; special poisoning from raw pusberry
  (both the cleanse's recommendations).

## NEEDS HIM

1. **"The creatures are its victims."** His experience line, picked on 2026-10-20, ends with those words. His
   ruling of 2026-09-28 says the opposite in as many words: survivors, *"never pitiable"*. This design follows the
   earlier, typed ruling for the creatures and reads "victims" as the unadapted dead (the rib-vaults, the
   Junkers). *Leave it* (default). *Re-pick the line* so its last clause matches the cast.
2. **Is cargo you are paid to carry a 0.2.0 thing?** The tipping trade as built delivers casks to a licensed pad
   on the player's land every few days. For a ship it is better as a single paid pickup: take casks aboard at a
   toll gate, be paid, and own the problem. *Keep the built pad contract for 0.2.0* (default; it exists).
   *Reshape it to a paid pickup:* very Jawa, and a rewrite of a quest that passed live.
3. **Does the Middenshell touch the ship?** As built it goes around gravship parts and its tentacle will not take
   them. *Keep that* (default: the player loses a yard, never the campaign). *Let it crush what is in its path,
   ship included, with the hours of warning as the fairness:* a real reason to launch early, and one bad save
   away from ending a run.
