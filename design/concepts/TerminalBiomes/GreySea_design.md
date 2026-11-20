# The Grey Sea: the design, seen from the ship

**Status:** the design document for one of the four sea biomes carried by the mod
`src/RimMandrake/TerminalBiomes/`: the Grey Sea (`RM_GreySea`; older files call its floor the Grey Deep). Written
2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni", by a pass that read the Grey
Sea's sources in full. Earlier the same day one pass wrote all four seas as a single design from a partial read;
that combined design was retired on 2026-11-18 and kept only in git history, commit `b2530669e5`, once each sea had
its own design. This file differs from its Grey section in the places listed at the top of
`design/concepts/TerminalBiomes/GreySea_rewrite_choices.md`. What happened to every idea in the older sources is in
that same page. None of the Grey Sea's older source files has been deleted. This is a design document only and it
launches nothing.

**Kind, checked against the sheet's own header:** a sea. The sheet defines *"the bottom of the Grey Sea"*. So two
rulings shape every section below. *"You can't 'dive' as an individual pawn nor return as one. It's ship or
nothing."* (owner, 2026-09-26.) And *"You are either on their sea floor, or you are on their beach. There is no 'on
their surface' location."* (owner, 2026-11-01.) The ship flies to the floor as its own planet layer
(*"Now the ship just flies to a new planetary layer called sea floor"*, owner, 2026-10-01), lands there, and is the
only way back. The visit sections are written for a ship on the floor; the beach has a short section of its own.

**Who reads this next:** a Designer run on this concept is handed the list of files in
`design/concepts/TerminalBiomes/` (`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in
its path by sitting here. Nothing in the pipeline reads it by name yet. The mod has no locked Designer sheet or tree,
so there is no locked tree describing a colony that stays, and nothing for a later Designer run to reconcile on that
score. Its only pipeline material is the cleanse proposal of 2026-11-17, which was never applied. The definition
sheet (`design/Jawa/worldbuilding/biomes/the_grey_deep.md`) is frozen and is not edited here; it is written for
divers and shore-camps, and this design keeps its rulings and changes who is standing on the floor.

**Two dependencies under everything.** Whether a gravship can be sent from a sea tile down to its floor and back is
not proven: the ledger item for the ship's flight down and back (`SEABED_DESCENT_ASCENT_1`) is built to its
offline level and blocked on a live read. And a measured read
of 2026-10-29 found that sea tiles still painted with the older campaign-tier sea biome fall back to *"the generic,
empty"* floor until the planet is repainted. The Grey's own floor generator exists on the layer
(`RM_SeabedGenerator_GreySea`: pillars, domes, chimneys, statuary, four crystal colours, the dressing step, a wreck
field, a walkability check). Every promise below reaches a player only when a ship lands on that floor. The ledger's
own item for this floor (`GREYSEA_FLOOR_PASS_1`) is still open, and closes only when the owner has walked the floor
live.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means found
in `src/` by the census of 2026-11-17 (`cleanse/census.json`) or by this pass's own search on 2026-11-18; it does not
mean it has passed anything. The validation walk records every Grey line as never run live.

---

## What this place is

> *"Pillars in grey murk, a lake with shores at the bottom of a sea, and the dead standing in crystal where they
> sank."* (`the_grey_deep.md`, header)

His line for the experience, typed 2026-10-20: *"It looks and smells like it's dying. Yet in the crusted remains
bold new life remains and emerges older than what dies."*

The Grey Sea is a salt sea with no way out, shrinking, and everything it holds is settling to the bottom. The floor
is *"a wonderland of odd pillars and formations"* (owner, 2026-09-26): bone-pale columns, *"salt-domes a little like
mushrooms growing, strange shapes everywhere"*, chimneys *"shooting up from the sea floor, shooting out murky white
super-brine"*. In the hollows lie pools of brine *"heavier than the murk itself... with their own surfaces, their
own slow ripples, their own shores, underwater."* Salt falls through the water like snow. And the sea keeps what it
is given: *"Everything that enters dies; everything that dies there keeps."* Anything that holds still long enough is
jacketed in crystal and stands there for good. The sheet calls the result **the statuary**: *"the war's losses and
the sea's whole history, standing."*

It is not empty. Green tissue lives inside salt it has grown into cubic armour, pink and violet and amber. Small
soft things pick through what rains down. Two animals own the place: something *"enormous and crusted"* that
*"moves between the pillars, rarely, in a temper"*, and *"a man-sized skeletal thing"* that *"picks its careful way,
watching you longer than you've been watching it."*

An earlier pass put the Grey's kind of danger in one row, and it needs no change: *"mineral encasement — the sea
precipitates itself onto you; stillness is death."* On the dayside the crew fights the sun. Here they fight the salt.

**Seen from the ship, this is a stop where the ship is the air, the larder and the lamp, and the sea starts filing
it the hour it lands.** The crew are Jawa: small, hooded, desert scavengers who trade scrap along dry roads. Three
of their habits are exactly the three things the Grey punishes. They reach for anything shiny, and the shiniest
things here are in the pools. They leave the lights on. And they go everywhere in a huddle, in a sea where *"one
pawn at a pool shore is a harvester; two are a crowd."* Against that, nothing on the planet suits a scavenger
better: a museum of a war's vehicles standing in crystal, salt *"harvestable and rather valuable"* in four colours,
and a sea that pays them for chipping it off their own hull.

*(`UNMEASURED`: what a crew member needs to wear outside the hull here. The dive specification of 2026-09-25 designed
a "deep exposure" clock; a search of `src/` found a suit and oxygen system for the Chill only, and none for the
Grey.)*

## The clock on a stop here

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`): a probe droid five to eight days
after landing, then scouts with a spotter, a strike team, an ion cordon on the ship, a breaching assault, and an
orbital bombardment that cannot be fought. Each step comes only if the one before succeeded; a loud crew halves
every wait and a hidden one doubles it. The arithmetic is the Greentide design's ("The clock on any stop") and is
not re-derived here; the pursuit's own source marks its numbers provisional.

**How long a stop on the floor can last: long, and the hull sets the edge.** His ruling of 2026-11-18: *"The
numbers you're generating are likely the outer edge allowable for each biome, and that's just fine. Go with
that."* The sea floor is the top level of cover (see "The ship while it sits here"): each wait is four times the
open-ground wait, as in the Abyss, so a probe comes around day 20 to 32 (four times the ladder's provisional five
to eight days). The search still comes, because *"nowhere pauses it indefinitely"*. On this floor the salt on the
hull and the crew's deck end most stops before the Empire does (this design's reading). **On the beach, in the open: about a month** (a probe on day 5 to 8, a first fight around day 12 to
20, the bombardment around day 20 to 32 if the Empire wins every step).

Few crews will see either edge, because the Grey's own clock is measured in days and it is on the hull. As built,
rime shows from about the first day parked, the first outer door salts shut at two to three, and crust that holds
the ship down begins inside the first week. A crew that stays a fortnight is chipping every day to keep the ship
able to leave. The owner chose that ladder by card on 2026-09-27; its numbers are tuning and no promise below pins
them.

How the Empire's ladder reaches a ship at the bottom of a sea: the probe and the bombardment follow, and the troops
wait at the beach (`Answered on 2026-11-19` 1).

---

## The first minutes

The ship comes down through water that gets greyer and thicker until the viewports show nothing, and settles on
pale sediment. *"Grey-green murk a few meters deep to the eye."* Shapes stand in it at the edge of sight: columns,
squat capped mounds, and here and there something the shape of a vehicle or a person, white, not moving. One
ruling keeps this playable: the pillar forest is *"STORY ONLY"* (card, 2026-09-27). Nobody gets lost and nobody
walks slower for the murk. The murk is what the place looks like, never a penalty.

The ship says what it can see. His ruling of 2026-09-02 on every landing: *"The ship will know what's visibly
dangerous and will advise course of action, but no more than that."* Here the advice is one line: this water puts
salt on anything that holds still, and the hull is holding still.

Salt is falling. The sound is *"pressure-muffled near-silence; the crackle of growing crystal."* By the time the
ramp is down, the player should have seen three things without going looking: a chimney venting white, with
something standing in crystal at its foot; a pool lying in a hollow with a flat, still surface and a white flower on
it; and a human shape in a block of salt a little way off, as an example.

## The first day

- **Salvage is chiselled out.** *"Old ruined vehicles and skeletons stand encased in mineral where they sank."*
  The jacket is a block of salt that *"can be mined through with relative ease"*, and the wreck field on this floor
  is jacketed the same way: mine the crystal first, then strip the wreck. For a crew whose whole trade is other
  people's wrecks, the Grey is a warehouse with the stock shrink-wrapped.
- **The chimneys teach, the pools do not.** A chimney's plume *"jackets whatever walks into it"*, in the open, with
  a visible cause. A pool does the same to whoever touches it, with no warning but its stillness. *"The chimneys
  teach this in the open; the pools never warn."* The channels of heavier brine run downhill from the chimney fields
  into the pools, so *"the floor's gradient always points at the danger."*
- **An encased crew member is a thing on the map.** By his ruling of 2026-09-26 a crystallised pawn is *"ENCASED AS
  AN OBJECT that must be mined out — not a hediff."* Air runs out slowly inside the jacket and an alert counts it
  down; friends cut them free alive. *"A colonist standing white among the war's vehicles is this sheet's image
  exactly."* If nobody comes, the body stays inside the block. Nothing vanishes.
- **The rime.** By the end of the first day the hull has a bloom of white on it. *"The warning IS the beauty."*
- **The garden.** The owner's seven crystal plants: cubic sculptures; sphere plants on radial spines, *"like a huge
  version of a microscopic creature"*; Glass Veil Kelp hung over the brine channels, *"a hanging chain of salt
  prisms"* that *"clatter softly"*; the Brine Crown, *"an anemone made of crystal thorns"*; Mosaic Fan Palms, *"a
  tiled mosaic or ceremonial shield"*; white vines spiralled up the black rock of the chimneys; Crucible Pods as
  sealed cubes, open cubes and empty cages. His one rule for all of it: *"marred slightly, don't make them too
  perfect or they look manufactured."* Between them, ten small grey soft things, each a different answer to salt: a
  mat at the pillar feet, beards on the formations that sweat salt, nets that sort food from mineral by touch, a
  sponge that makes the water gentler round itself, a coral turning itself to stone on a schedule, a plant that is
  usually a puddle (*"a diver who steps in one is startled, unharmed, and faintly insulted"*), combs along the
  channel beds, a sprig salt cannot take, and a cushion that has colour only while a lamp is on it.
- **The pool lily.** *"A white flower seen through the murk means a pool is there."* It cannot be picked: *"every
  stillbloom grows exactly out of reach."*
- **The line brings up little.** Four kinds of catch and a rare table (a creature kept in crystal, *"the statuary
  made portable"*; and *"somebody's ring, still in its jacket"*). Every one of the four is alive on the floor:
  a pale eyeless ribbon cruising above the pools, and a clam, a mussel and a hand-sized shrimp working the litter.
  Nothing schools. The Grey is not where the crew fills the larder.

## The first week

- **The doors.** Somewhere in the second or third day an outer door will not open. It has salted shut from the
  outside. By his card of 2026-09-26 it is *"never a tomb"*: a pawn inside always forces it, and chipping it from
  either side needs no tools. A letter explains it once; after that the white on the door is the notice.
- **The crust.** Then blocks of salt begin to stand on and against the hull, and the ship will not lift while they
  are there. The refusal says why and how many. Three things about this were his choices and are kept exactly:
  *"the sea pays you"* (chipped crust is salt in the hold); nothing bought ever slows it (*"nothing purchasable
  ever"*, card, 2026-09-27; interior heat *"does nothing to it"*); and where the ship sits and what is falling
  change the pace (weather and berth, same card). Under salt snow it runs faster. Beside a chimney field or a
  brine channel it runs faster. *"Where you park and what the sky is doing are reading-the-floor skills, not
  purchases."*
- **Tearing free.** By his card of 2026-10-08 a forced launch is always there: it rips the ship loose, strips the
  crust, opens the doors and damages the whole hull. It is the answer for the day the Empire arrives and the deck is
  still white.
- **The lamp.** His typed word of 2026-09-26: *"Actually attacking light makes more sense in the Grey and Scald
  (dark on the bottom) than it does on the beautiful lighted Twilight floor with lots of lighted everything."*
  Nothing in this sea glows. So *"a player lamp is the brightest thing this sea has contained in its whole
  history"*, and the sea notices in three steps. Small sighted things drift into the light. Then **the fessk**
  comes to the rim of it and stands there, *"half-behind a pillar, watching"*: man-sized, bone-white, all forelimbs.
  It *"never enters, never attacks"*, and leaves when approached. Then fresh scrape-marks appear on the pillars. If
  a strong work-light is still burning steadily after hours of this, **the giant** comes. To the one animal here
  with a glowing mark of its own, a steady strange light is *"a rival's mark standing on its ground."* By his card
  it breaks the lamp, *"not the ship, not the pawns"*, and goes. By his card of 2026-09-27 this is *"deterministic
  and forgiving"*: never a torch, only after hours, always after the watcher and the scrape, and switching the lamp
  off always resets it. *"Light discipline is a learnable craft."*
- **The cushions.** Under the work-lights the grey cushions on the floor turn oil-sheen blue and green. They show
  exactly which ground the lamp is lighting. *"The prettiest thing in the biome is a countdown."*
- **The dome that breathes.** At a pool's edge, one of the salt domes has a small puckered spout on top. It is an
  animal, the orruhmu (the owner's own name for it, 2026-09-27). In 0.1.0 it is only that: a dome that shuffles a
  few cells a day. What it does to a crowd is 0.2.0.

## The ship while it sits here

Three things every biome design states, by his rulings of 2026-11-18.

**Cover from orbit: partial on the floor, none on the beach.** His card: *"Canopy, steam and fog slow the search by
one step; full dark still pauses it."* Then his word of 2026-11-18: *"Going under the ocean is like the Dark... VERY concealed. But nowhere pauses it
indefinitely."* The floor is under a sea and under *"directionless
grey-green dimness fading to blind"*, so it is the top level of cover, like the Abyss's Dark (`Answered on
2026-11-19` 4). A loud crew gives some of it back, and on this floor loud and lit are the same
mistake: the lamps that would give the ship away are the lamps that call the giant. So running dark is one craft
with two rewards. (That coupling is this design's reading; no source states it.) The beach is the opposite: *"a
white salt pan under a permanent horizontal wind"*, where *"anything that stands up out of the ground casts a shadow
a kilometre long."* No cover at all.

**Wear on the hull: the sea crystallises it.** His words, typed 2026-09-26: *"Yes. The grey sea should crystallize
the hull, freeze doors shut."* His ruling of 2026-11-18 put hull wear in 0.1.0 for every biome: *"It's easy, and
most of the biome already talk about this."* For the Grey it is more than talked about. It was designed on
2026-09-27, ruled by six card answers, and built (`RM_GreyHullCrust.cs`, its doors, crust, launch gate and the
tear-free launch; settings for each). No new hull system is designed here.

- *What the player sees.* Rime, then salted doors, then crust on the footprint and a launch that waits for
  chipping. *"The ship is not being attacked. It is being filed — the statuary reaching for its newest exhibit."*
- *What answers it.* Hands. Chipping a door or a block is short work that anyone can do and that pays in salt.
  Choosing the berth: away from chimneys and channels. Watching the weather. Leaving. And, when there is no time,
  tearing free and paying for it in hull.
- *What does not answer it, by his rulings.* Heat or fuel (card, 2026-09-26: *"no heat-for-time trade"*). Anything
  bought (card, 2026-09-27). A cut sprig of the one plant salt cannot take (card, 2026-09-27: *"pure dressing, no
  harvest, no item"*). And no shield: his shield ruling of 2026-09-02 says *"Slow pressing things move through all
  shields... This is why nothing 'holds out water,' it just doesn't work that way."* His 2026-11-18 words also name
  *"different kinds of shields or armor"* as answers to hull wear in general; whether that reopens the Grey's
  *"nothing purchasable"*: it does not (`Answered on 2026-11-19` 2).
- *It never traps.* Doors force from inside. The launch gate only delays. The tear-free launch is always offered.
  His ruling of 2026-09-02: *"no environment is immediately lethal."*
- *The shared frame.* The campaign's hull-wear frame is `src/RimUtinni/ShipShields/` (his eight shield rulings of
  2026-09-02): an exposure tracker that wears a landed ship in a hazard its shield does not cover, and a landing
  advisory. It knows heat, cold and blown sand; none of the three applies on this floor, and the Grey's wear is
  built on its own in the free tier. What the Grey asks of the frame is small: that the landing advisory can speak
  for a biome's own wear (so the ship says "salt" on arrival), and that a biome can declare that no field counts as
  cover against it. See "Shared machinery".
- *The approach.* No source says the descent itself knocks or scours the hull, and this design does not add it.

**Fuel: the emergency route only, and less of it than anywhere.** His ruling: *"Every biome has a fuel source, but
for most its the hideously slow route of rendering biomass into chemfuel. Uselessly slow, only for emergencies."*
Nothing in any Grey source burns, pools as fuel or is rendered to it. The biomass is thin by law: a sparse garden,
four small kinds of catch. This is a stop that spends fuel and makes none (the descent item's specification says
*"fuel cost per depth both ways"*; `UNMEASURED` whether that is built).

- *Buying it.* On the floor nobody sells anything. On the shore the campaign's world has people: Homestead holdings,
  Trade Moot seats (*the Ore Moot* among them), Junkers, Free Droid seats, and the Deepwater Compact's Tidewatch
  (*"The Grey Sea — salt-encrusted, shrinking, and worth less every year. The Compact holds it anyway."*). All of
  that is the campaign layer's, and whether any of them stocks fuel is `UNSETTLED`.
- *Paying for it.* This is the Grey's "very Jawa" answer. The crew arrives with nothing the shore wants and leaves
  with salt chipped off its own hull, four colours of crystal salt, and war salvage in its original packaging. The
  sea that glued the ship down is what pays for the fuel to leave the region.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The reach.** *On screen:* a hooded figure leaning out over a still pool toward something that glints under
   the surface; then the figure is a white block with an arm out. *Why it
   lands:* the player watched it coming. An alert starts counting air, and two more Jawa arrive with picks.
2. **The lesson, in the open.** *On screen:* a crew member cuts a corner through a chimney's white plume and stops
   mid-stride in crystal, in full view of the ramp. *Why it is funny:* the next one walks round.
3. **The door.** *On screen:* the ramp door rimed white, not opening; a Jawa inside leaning on it until it cracks
   outward; two outside chipping the frame and putting the pieces in a sack.
4. **Paid to scrape.** *On screen:* the crew working along the hull with picks, a growing stack of salt beside the
   ramp, and fresh white already on the plate they cleared yesterday.
5. **The watcher.** *On screen:* at the edge of the work-lights, a tall pale shape that was not there a moment ago,
   half behind a pillar, not moving. Someone walks toward it and it is simply gone. *"The shrimp saw you first."*
6. **The colour.** *On screen:* one point of impossible colour in the grey, getting larger. *"You see the
   mate-mark's glow before you see anything else."* What looked like a drifting pillar is under it.
7. **The lamp.** *On screen:* the giant arrives at the camp, ignores the ship and every Jawa on the floor, breaks
   the big work-light, and leaves. The crew stands in the dark. *Why it is funny:* they were warned twice, by a
   shrimp and by scratches, and the lamp was still on because somebody was sorting salvage under it.
8. **The blush.** *On screen:* a lamp is switched on and the dull floor round it turns iridescent. It is beautiful
   and it is a map of exactly how much attention the crew is asking for.
9. **Tearing free.** *On screen:* the search has found the ship, the deck is still crusted, and the pilot pulls
   anyway: salt shatters off the hull in sheets, every door bangs open, and the ship goes up trailing white, with
   damage on every plate.
10. **The crowd** (0.2.0). *On screen:* three Jawa cluster round a salt dome at a pool's edge to argue about what
    is in the pool. The dome swells and hisses. Two scatter. The third is a statue. *Why it is funny:* *"The Grey
    is a sea of solitary things, and the orruhmu punishes company"*, and Jawa do nothing alone.
11. **The customer** (0.2.0). *On screen:* the crew hauls junk to the edge of the deepest pool, where a branching
    crystal thing the size of a building stands. It takes one of each thing it has never tasted and is not
    interested in the second (his own paragraph, 2026-09-26: a new thing *"may be extraordinarily valuable once,
    then nearly worthless thereafter because the Elder has already incorporated its chemistry into memory"*). Charge crawls along its limbs; something that has been in the pool since before the
    war comes up onto the shore. *Why it lands:* it is the only trader they have ever met that wants scrap for
    being strange, and it cannot be haggled with.
12. **The exhibit** (0.2.0). *On screen:* a trooper who died on this floor a few days ago is standing in crystal
    beside the war's dead, and something flat and grey is grazing the block.

## When the Empire arrives

How the ladder reaches the floor: the probe and the bombardment follow, the troops wait at the beach (`Answered on 2026-11-19` 1). So:

- **The search clock runs under the sea four times slower (the top level of cover),** and the bombardment at its end does not care about
  water.
- **The launch is the fight.** On this floor the crew's real opponent on the day the Empire comes is its own deck.
  A kept hull lifts at once. A neglected one chips against the clock or tears free and flies wounded into whatever
  comes next. That is the Grey's whole contribution to the pursuit and it needs nothing new built.
- **What the floor does to anyone who comes down** (if anyone does): the pools and plumes take whoever stands in
  them. The built trigger counts humanlike and mechanoid pawns and never animals, so a trooper or a droid that
  walks through a plume is jacketed like a Jawa. (`UNMEASURED`: whether the pursuit's probe droid is a pawn of a
  kind that counts.) Nothing here cares about blasters.
- *0.2.0:* a squad at a pool's edge is a crowd, and the orruhmu does not sort crowds. The dead of both sides join
  the statuary. A Brine Elder's discharge, by his own paragraph, can *"stun living creatures, disable droids,
  collapse shields, and cripple nearby ships"*; it fires when its pool is disturbed, and a firefight beside the
  pool is a disturbance. The crew's ship is a nearby ship too. (*"Cripple nearby ships"* is ruled as its own engine
  check and is not built.)

## Who else attacks; who hates the Empire

- **Nobody raids here.** The Grey's danger was put in one line by its sentinel pass: *"the place kills, the animals
  mostly don't."* The fessk *"never attacks and is never tamed."* The small things are harmless. The giant is
  *"ill-tempered"* and answers a lamp or a wound, nothing else.
- **No ancient machine wakes.** A draft of where mechanoids may appear denies the Grey outright: the statuary is
  *"meant to be seen, not to wake."* Kept.
- **The Brine Elders take no side** (0.2.0). *"Older than every faction"*, they *"remember the arrival of the
  Reshapers"* (ruled 2026-09-26: the Elders' own word for the Rakata) and they *"interpret history through
  chemistry... rather than names, politics, or technology."* The Empire is one more change in the water.
- **On the shore,** the holdings named above. Whether any of them would fight the Empire, or shelter a ship, is
  the campaign layer's to say and is `UNSETTLED` here.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The deck. Crust grows faster than a small crew can chip once it is behind, and every day it is behind makes the
  day of leaving worse.
- The larder and the tanks. Air, food and water are what the ship carried down. *"The sea is not potable"*, the
  catch is thin, and nothing here refuels.
- A crew member in crystal, and the hours it takes to cut them out.
- The dark. Work needs light and light has a price.

**Stay, longer than the Empire would like:**
- A hull chipped daily, on a berth chosen well away from chimneys and channels.
- Lamps run in short windows and dowsed when the watcher shows.
- A sea over the ship: the top level of cover above.
- Chipping pays, so the stay is never wasted time.

## What the crew takes away

- **Salt, by the sack:** raw salt off the hull, the doors, the pillars and the jackets.
- **Crystal salt in four colours** (white, pink, violet, amber; ratified by card 2026-09-27) from the great
  crystals, which stand alone and well apart: *"harvestable and rather valuable."* *"Different colours of salt make
  great... ingredients."* Our cuisine mod cooks with them and cures rations in them.
- **Jacketed salvage:** wrecks mined out of crystal. The sheet's phrase for the dead in their cases, *"half the
  value IS the case: a crystal-encased soldier of the old war is furniture, relic, and museum in one object"*, is a
  promise the built floor does not keep yet (the statuary is built as blocks of jacket that yield salt); it is in
  0.2.0.
- **The rare catch:** a salt cameo, a ring in its jacket.
- **Nothing alive.** The fessk is never tamed, and the Grey tames nothing.
- *0.2.0:* what an Elder gave for something it had never tasted, including the one thing in this sea a ship would
  cross the planet for: *"a resonant storage crystal that passively increases the effective capacity or charge
  retention of all nearby batteries."* And a reason to fly to the next Grey tile: *"ONLY grey sea, but there's one
  per grey sea tile"* (owner, 2026-09-26), and each Elder has seen only its own set of things.

## The beach

The Grey's beach is the land tile beside the sea. Every Grey shore carries *"the crusty whiteness that should be on
every Grey Sea shoreline"* (owner, 2026-09-26): white crust terrain with salt domes scattered on it. By his ruling
there is *"no harvestable shore salt"*: the floor's salt stays the prize. A crew on the beach can fish the Grey's
catch, sees no cover from orbit, and is where the shore's people are. `UNSETTLED`: where the shore's own life lives.
The sea's biome reaches only its floor, and two things written for the shore (the tall salt-rimed blades and the
drifter that *"rides the shore current through the shadow lanes"*) are on the floor's lists today.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The ship lands on the Grey's own floor (pillars, domes, venting chimneys, brine channels, still pools, statuary, falling salt, the crystal garden and the small grey things between) and can leave again. | A landing and a launch. A walk from the ramp to a pool and back. | A generic empty floor fails. So does a floor reached any way but the ship. The mineral shapes stay readable as shapes through the murk, not a white screen. |
| Whoever touches a pool, or stands in a chimney's plume, is encased where they stand, and is cut out alive by others while an alert counts their air. | One crew member at a pool, one in a plume, one rescuer each. Save and reload while encased. | A native animal in the same plume is untouched. The encased pawn is a thing on the map before and after the reload. Left too long, the body is still inside the block. |
| A parked hull rimes; then its outer doors salt shut from outside and force open from inside; then crust holds the launch until it is chipped off; and chipping pays in salt. | A ship parked for the stay; chip one door from each side; chip the deck; launch. | Interior heating changes nothing. A running shield changes nothing. The same ship on another sea's floor grows nothing. Nobody is ever sealed in. |
| Where the ship sits and what is falling change how fast the salt comes. | The same ship beside a chimney field and well away from one; in clear water and under salt snow. | Nothing the crew builds, burns or buys changes the pace. |
| A crusted ship can always tear free, at a cost in hull. | A launch with the deck still crusted, by the forced launch. | The ship leaves; the crust and salted doors are gone; the damage is real and never destroys a hull part. |
| Every catch has a living body on the floor, and nothing here schools. | Fish the beach; find the same four kinds alive below. | A catch that exists only as an item fails. |
| Under the sea the Empire's search comes at the top level of cover, much slower than for the same crew on the beach, and it still comes. | The same crew, as loud, on the floor and on the beach; read the search's next contact on both. | A search that never comes on the floor. |
| Nothing vanishes. | Every loss above, with a save and reload in the middle; a launch with someone still encased outside. | The launch warns that someone is held. |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A strong steady work-light brings the watcher to the edge of the light, then fresh scrape-marks, then the giant, which breaks that lamp and leaves. Switching the lamp off at any point resets it. | One work-light left burning; a second ship-day with the lamp dowsed when the watcher shows. | A torch never brings the giant. The watcher never enters the light and never attacks. The giant harms neither ship nor crew. |

No row pins a rate, a day count or a yield: how fast salt comes, how long a lamp may burn and how much a block pays
are tuning.

Settings: the Grey has its own switch, and one per major feature (hull crust and its pace, tear-free launch, each of
the three lamp steps, pool defence; and for 0.2.0 the sentinel, the Elder's trade and discharge). All built.
Everything off leaves a quiet mineral floor with ordinary life on it. A review found that switching the crust off
left already-salted doors locked; whatever the fix's state, "off" has to mean off (standing rule, every mod).

## Shared machinery

**Featured here** (the Grey is where each is vital and should be proven):
- **A place wearing on a parked hull, with no purchasable answer.** Of the four seas the Grey's is the most
  complete: sign first, a bill that grows, a launch that only delays, work that pays, and an exit that always
  exists. It is the worked example for whatever shared hull-wear machinery the other biomes ask for, and the one
  case where the rule is that no shield helps.
- **Encasement** (`RM_BrineEncasement`, `MapComponent_BrineCrystallisation`, the smother timer and its alert, in
  `DivingInteraction`): one mineral for the statuary, a wreck, a pawn and a hull. Other biomes that hold a pawn
  (mire, tar, the Twilight's sink, the Slime) share its rescue shape: a findable victim, a clock, a companion.
- **The place noticing light** (`RM_JobGiver_SeekGlow`, `RM_GreyLampResponse.cs`): built once for the Twilight's
  light-grazer, pointed at the Grey by his word, and owed to the Scald's floor by the same word.
- **A warning that is an animal.** The fessk at the rim and the scrape-marks are the Grey's version of the sign
  before the event.

**Merely active here:** the ship as the only door (the seabed layer and its floor maps; `DivingInteraction`,
`SeaShores`); catch with a living counterpart (every sea); the growth engine; wreck salvage (`Wreckage`, with the
Grey's jacketed wreck field); bone from butchery; the landing letter and the launch warning for a held colonist;
the Empire's search and the visibility dial; the one sun from geometry, which on a sea floor is nothing.

**Three ship systems built once for every biome, and what the Grey asks of each:**
- *Hull wear.* The frame is `src/RimUtinni/ShipShields/`. The Grey's wear is already built outside it, in the free
  tier, which differs from the Abyss card of 2026-10-01 that kept a ship touch in the campaign layer; the Grey's was
  built on his typed word before that and is left where it is. The frame needs to let a biome name its own wear to
  the landing advisory and declare that no field covers it.
- *Cover from orbit.* One entry for this floor at the top level, beside the Abyss's Dark.
- *Fuel.* Nothing. The Grey is on the buying side only.

## Scope

Every feature is in one bucket. Moves against the cleanse proposal and against the retired combined four-seas
design are listed, with reasons, in `GreySea_rewrite_choices.md`.

**The one signature (his card of 2026-11-20): the sea keeps what it is given.** Whoever touches a pool or stands in
a chimney's plume is encased where they stand and is got out by mining. *Why a normal stop is sure to see it:* the
pools and plumes are everywhere on the floor and the statuary shows it from the first minute. The lamp
(light-seekers, the fessk at the rim, the giant that breaks the lamp) is an extra and is in 0.2.0.

**The river is shared by all four seas, and is no sea's signature** (his write-in on the card of 2026-11-20,
`Answered`, card of 2026-11-20, entry 5). Bed, banks, lit stakes, the current, the surge and the sink are a system of every sea
floor. *Its version in the Grey is not ruled:* whether it comes in 0.1.0 or waits for 0.2.0 is one question for him, on
the item `RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED`. *What it adds here:* the current, the surge
and the sunk condition read no biome (measured 2026-11-20: `RM_MapComponent_ChannelCurrent`, `RM_GameCondition_Undersurge`,
`RM_HediffComp_Sunk`); the channel generator `RM_GenStep_TwilightChannels` is gated to the Twilight's floor by name
and registered on that floor's generator alone. So this sea needs the gate opened and one registration patch (small
code), a bed, bank and stake look of its own (art and defs), and the river's promise rows proven on its floor (the
biggest part, and live). *Fit:* the Grey's brine channels already run to the pools, so a river here must keep its sink and its
carrying centre clear of every pool and plume: a carried worker must never be delivered into encasement.

**0.1.0, the stop**
- The floor as a place on the ship's layer: murk without penalty, pillars, domes, chimneys with crystallising
  plumes, brine channels running to the pools, the deepest pool, the statuary as blocks of jacket, the four great
  crystals, salt snow, the jacketed wreck field, and a floor that stays walkable. (built; the layer's descent is
  unproven live)
- The crystal seven, the ten small grey plants (the lamp-only blush among them), the two salt blades. (built)
- The nine animals as ordinary life: the giant, the fessk, the ribbon-swimmer, the statuary-grazer, the clam,
  mussel and small shrimp, the shore drifter, and the orruhmu as a dome that breathes. (built)
- Pools and plumes that encase; rescue by mining out; the air timer and its alert. (built)
- The hull: rime, salted doors, crust, the launch that waits, chipping that pays, berth and weather changing the
  pace, the tear-free launch. (built; moved in)
- The catch of four and its rare table; the beach's white crust and domes. (built)
- Salt as goods: raw salt, the four coloured salts. (built)
- The sea floor as the top level of cover from orbit. (unbuilt; campaign layer, one entry in the pursuit)
- The ship's landing advice naming the salt. (unbuilt; campaign layer, on the shared frame)

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The lamp: light-seekers, the fessk at the rim, scrape-marks, the giant that breaks the lamp. (built; moved in)
*Already here before that answer:*
- The orruhmu's squirt: two or more people within reach, one swell of warning, then the nearest is encased. (built)
- The plants that hurt to touch: the sphere plant and the Brine Crown. (built)
- The Brine Crown pulling its membranes in under salt snow, as a picture only (card, 2026-10-19). (built; the
  retracted art may be owed)
- The Brine Elder: one per Grey tile, the trade in novelty, the discharge with its tell of *"motion, crackle and
  sound only"*, the pool's contents given up, five treasures of the six. (built; no live trade recorded; the three
  canon treasures belong to the campaign layer and cannot yet be added there)
- Lit ground yielding more to fishing and gathering (card, 2026-09-26: *"lit cells yield more"*). (not found in
  source)
- The statuary as figures worth carrying off: encased soldiers and vehicles as objects, and the dead of this visit
  joining them. (unbuilt)
- The watcher that hides in place, asked for by his typed card of 2026-10-08: *"That is not a watcher, that's its
  own creepy thing. Add an independent watcher that hides in place."* Designed as a grey eye-cup that follows a
  walker and folds flat into a pebble. (unbuilt)

**Later (a crew that stays, or a colony)**
- The full jacket of a hull neglected for a season, and the wreck nobody chipped, *"generations on"*.
- A cut sprig that speeds cutting someone out of crystal (the card of 2026-09-27 called this *"the only acceptable
  later opening"*); small creatures gathering in the sponge's gentler water (*"the good later door"*, same card).
- The sixth treasure, *"some beautifully useless artifact whose significance only becomes apparent much later"*,
  which waits for a plot to name it. The specimen cabinet.
- The giant's shed crust and pillar stone as their own goods; dip-harvest of minerals at the pool shores; whatever
  the pools hold that only an Elder can give up.
- The giant's life between this sea and the Miasma's nursery; Deepwater's sounding lines; divers' waymarks.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Diving or returning as a single pawn; the dive hatch; any place on the sea's surface.
- Getting lost in the murk; waymark jobs; any penalty for the murk (card, 2026-09-27).
- Heat, fuel or anything bought against the crust (cards, 2026-09-26 and 2026-09-27). A product from the sprig salt
  cannot take (card, 2026-09-27). A door that seals anyone in.
- The seven catch creatures of the sallik family, here: *"Sallik in the Grey Sea → Remove from the Grey Sea only"*
  (card, 2026-10-12). Their defs are kept and cast nowhere. With them go the thirteen-kind catch table and four
  small behaviours built for them.
- The pillar-snail and its catch (deleted by card, 2026-10-08). The donor drifter (cut 2026-09-26, replaced by ours).
- Any school or swarm; any plant or creature that glows; a fessk that fights or is tamed; survivable entry to a
  pool; rot on anything encased. (The sheet's six bans, all standing.)
- A yield bonus round the sponge (card, 2026-09-27: *"prose only"*). Harvestable salt on the shore.

## NEEDS HIM

None. All entries were answered on 2026-11-19 (next section).

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. **What does the Empire do about a ship at the bottom of a sea?** The probe and the bombardment follow the ship
   down. The troops wait at the beach and meet it when it lifts. This needs the fewest new things and is the same in
   all four seas (the design's default). *Delegated call.*
2. **Does "different kinds of shields or armor" (2026-11-18) reopen "nothing purchasable ever" for the Grey's crust
   (card, 2026-09-27)?** No. His sentence of 2026-11-18 ends *"It's in there."*, so the sources decide, and the Grey's
   sources say nothing purchasable (the design's default). *Delegated call.*
3. **Should the Brine Elder come forward into 0.1.0?** *His ruling:* the move card of 2026-11-18 (*"Move it, list
   every move"*): 0.2.0.
4. **Is the Grey's floor "full dark"?** *His ruling:* his word of 2026-11-18 (4:09 PM PST): *"Going under the ocean is
   like the Dark... VERY concealed. But nowhere pauses it indefinitely."* The Grey's floor is the top level of cover,
   like the Abyss's Dark. **This changes the design's default.** Was: *One step, like fog*.

**Answered by his card of 2026-11-20** (item `RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED`; the
enact item is `RIMMANDRAKE_ENACT_SIGNATURE_PICKS_INTO_DESIGNS_SLIME_KEEPS_FILM`). Each keeps its number.

5. **Which is this sea's one 0.1.0 signature?** It was left unchosen between his approval of 2026-11-17
   (the Twilight's river as the one signature of all four seas) and this sea's own. He took neither option as
   offered and typed, about 6:00 AM PST: *"Actually having underocean rivers should be commonplace in all the oceans, so this isn't even special for Twilight. EACH of them should get an actual special. Perhaps the Twilight should be the falling shards of the ocean's colorful cover"*
   So the river is shared by all four seas and is no sea's signature; this replaces his approval of 2026-11-17.
   The Grey's signature is its own: the sea keeps what it is given.

## Found while reading, for whoever builds

None of these is fixed here; this run changes no code.

- The giant's shipped description (*"the one place in the deep where a crew can rest in the light of something
  else's garden"*) was written for the creature's older home and reads against the Grey's ban on any glow but its
  mark.
- The lamp's first step was built to draw three small animals, and two of them were cut from the Grey on
  2026-10-12. `UNMEASURED` whether anything but the clam still drifts into the light.
- The dive specification's rule that a corpse left on the Grey's floor is jacketed into the statuary was not found
  in source.
- A review of the hull crust found the clock belongs to the berth, not the ship, and that salt on a door could be
  lost while the door was in flight. One ship in the campaign makes the first harmless; the second has its own
  item.
