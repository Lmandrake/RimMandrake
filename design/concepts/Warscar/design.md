# Warscar: the design, seen from the ship

**Status:** the one design document for the Warscar biome (`RM_Warscar`, source `src/RimMandrake/Scarlands/`; the
older documents call it the Scarlands, and the owner's card of 2026-09-30 set the label to "Warscar" with no
article), rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It
replaces the frozen definition sheet, the bedazzle review, the turn-three development document, the cast bible, the
kit spec and the cleanse proposal as the place to read; what happened to every idea in them is in
`design/concepts/Warscar/rewrite_choices.md`. Nothing has been deleted yet. This is a design document only and it
launches nothing.

**Second reader, 2026-11-18 (same day, a different agent).** The sources the first pass read in part were then
read to the end. What that changed here: the hull paragraph (the built shield frame already wears a ship on this
map, two ways, and the first pass said nothing was built); the heat (this is the hottest ground a crew lands on
outside the Rust Cathedral, not a comfort); the fuel paragraph (two poor fuels are in the sources); the mark (it has
a line at about eight days, which is the stop's real clock); what the dead rings give up; the hospice (seen live,
and its accepted words carried in); an animal he added by hand that neither document mentioned; and the status of
"every danger already sprung", which is not wired on this biome today. Each change is listed at the top of
`rewrite_choices.md`.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/Warscar/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. Warscar has no locked sheet or tree; its only pipeline material is the cleanse
proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) or the special-mechanics review of 2026-10-22 found it in source; it
does not mean it has passed anything, except where a live pass is named.

**One rule about what may be said.** The frozen sheet partitions this biome's lore. A player-facing text may say
only what the Jawa know. Who the defenders were, who they fought, what the Rust Cathedral is, who made the madness
and why the pilgrims come are campaign truths behind reveal gates, and none of them appears in any description,
letter or first-tier text. This document keeps to that rule itself: it describes what a crew sees.

---

## What this place is

> *"A battlefield where the whole story is still legible in the ground, except who the enemy was."*
> (`the_scarlands.md`, header)

Crater fields and slag terraces on shattered megastructure floors, under a white sun almost straight overhead.
Along every rise sits a line of old fortification facing **outward**, toward nothing anyone can see: bunkers,
embankments, ruined turret rings, burnt shield emplacements. Black varnish crusts every crater lip. Nothing is
green and nothing ever will be: *"The land can never be made fertile; the toxicity replenishes itself."* The pools
are the only colour on the map, and the owner's line for them is the biome's palette in one sentence: *"The color
isn't life, it's reaction and acid."*

> *"Poisoned forever, mad beasts, silent guns. Everyone calls it cursed, and everyone who scavenges here learns
> why."* (owner, picked by card, 2026-10-20: the experience line)

What the Jawa are told about it, and all they are told:

> *"The Jawa do not know who they were fighting, but they were keeping them away from the Rust Cathedral — that
> much is clear."* ... *"The place is cursed — though how glorious it would be to be able to... somehow."*

**Seen from the ship, this is the biome the crew already has an opinion about.** The sheet says so twice:
*"it is, by every Jawa's flat testimony, cursed"*, and *"Salvagers return changed — sick in body, marked in mind.
The Jawa call the place cursed and keep coming anyway."* It is the largest heap of old technology on the planet,
and everything obvious was *"plundered to skeletons generations ago"*. What is left is sealed, buried, powered down
or still running. The owner's answer of 2026-11-10 names the pull: *"it's the story of radiation seeping in but
fabulous technology too."*

The crew are small, hooded, skittish and built for dry heat (`reconciled_lore/05_the_clan.md`). The heat here is
more than home: the sheet measures the sun at seventy-two degrees up and the air near sixty, and the sun-heat
review of 2026-10-19 calls it *"the hottest sun of all after the Rust Cathedral"*. The sheet's line for it: *"The
energy regime just keeps the corpse hot."* A desert crew can live in it, in shade, and nothing else about the place
is theirs.

The first review of the biome gave it a family, and it is the best single description of what a crew does here:
*"The Warscar is what already happened here, and the ground still telling it."*

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28: *"around every 5-8 days, keep 'em running"*; ladder in
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked provisional): a probe
droid five to eight days after landing, then scouts with a spotter, a strike team, an ion cordon on the ship, a
breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if the one before
succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last: about a month, and that is the outer edge** (his ruling of 2026-11-18: the
numbers are *"the outer edge allowable for each biome"*). It is the bare pursuit clock and nothing more: the
ladder's arithmetic on open ground gives a probe on day 5 to 8, a first real fight around day 12 to 20 and the
bombardment around day 20 to 32 if the Empire wins every step. The Warscar adds no days to that. It is open ground under a high sun and it hides nothing. That is the outer
edge, and very few crews will reach it, because the place charges for every day in four currencies of its own
(below) and one of them never comes off.

**Cover from orbit (his ruling of 2026-11-18: partial cover, by biome).** **None.** No canopy, no steam, no
standing fog, no dark. The pale fall of a Settling is thin and comes with dead-calm air; this design does not count
it as cover. The aerosol dome screens poison, not eyes. The Warscar is one of the places a crew goes knowing it
will be found on schedule.

**Fuel (his ruling of 2026-11-18).** **The slow route only**, and less of it than almost anywhere: there is no
soil, and the animals are armour and madness. The sources do name two things here that burn, and both are poor.
Wreck-lichen scrapings are *"a dye base and a poor fuel"* (built as a harvest). Glower crust, by its own shipped
description, *"burned, ... makes a crude, hot fuel"*; the sheet listed *"glower fuel — radiogenic harvest from the
black crusts"* and the first review proposed a brazier that doses whoever tends it. His card of 2026-09-30 put the
glower-black uses out, fuel among them, so the crust burns in its description and in nothing else. That cut
stands by his answer of 2026-11-19 on declined ship ideas, though his fuel ruling came seven weeks after it. Nobody lives on this ground and
nobody trades on it, so fuel cannot be bought here either. A crew lands on the Warscar with the fuel to leave it,
or it does not land.

**What the place does to the ship (his ruling of 2026-11-18, in 0.1.0).** Three things, all in the sources, and
the first two are already wired into the built frame (`src/RimUtinni/ShipShields/`, his shield rulings of
2026-09-02; nothing new is designed here).

- **The air.** The toxic weather here was ruled *"a war aerosol, not rain"*, *"settling out as a corrosive fall
  when the air stills"* (freeze ruling R23, 2026-09-07). The frame's test for a particulate hazard
  (`ShieldHazardUtility.HasParticulateHazard`) asks `RM_PollutionSense` whether the map is polluted, and the
  Warscar's BiomeDef carries the polluted-biome marker. So `ShieldHazardExposureTracker` counts a ship landed
  here as standing in a hazard for the whole stop, calm or wind, and wears its structures unless the generator
  is holding the light screen. His words for that field: *"Light kinetic deflectors handle wind, ash, vapor, bio
  contamination, spores, smoke, sand, and rain damage completely as well as repels small animals."* The
  Warscar's own aerosol screen is the same comp (`ShipShields` derives from `RM_CompAerosolScreen`), and a
  humming ring over the ship is that screen for free.
- **The heat.** The frame's heat hazard fires at an outdoor temperature of 58 degrees
  (`ShieldHazardUtility.ExtremeHeatThreshold`). The sheet's measured air here is 58 to 66. So the ship also takes
  *"thermal stress"* unless the generator holds the thermal veil. And by his ruling one generator holds **one
  field at a time**. On the Warscar a ship with one generator chooses which of the two it will be worn by. That
  choice is the biome's hull wear, and it needs no new system: only for somebody to have noticed.
  (`UNMEASURED`: whether a generated Warscar map really sits at or above 58 in play. The number is the sheet's
  record of the planet.)
- **The mynocks.** The sheet's own ruling: *"if the gravship comes to the Scarlands, mynocks get aboard —
  reproducing strangely fast, consuming conduit, flooring and lighting until hunted out of the hull. The biome
  follows you home."* The owner tuned it by card: *"Nuisance unless there are many."* They eat *"the flooring, not
  the hull"* (the kit's words: floors are stripped to the deck plate, conduit and lamps are destroyed). They come
  out of the wrecks, which carry their nests (his ruling of 2026-09-12), and the animal is built to survive
  vacuum, so launching does not shake them off. The answer is hands-on: the crew hunts them out of the hull.
  Whether the light screen's *"repels small animals"* keeps them off a screened ship is `UNSETTLED`.

What is not built: a film drawn on the hull itself. The wear above falls on the ship's structures whether or not
anything is drawn. Nothing in this section has been seen live.

---

## The first minutes

The turn-three document wrote the landing, and it needs no change: *"You land in a place where everyone already
lost. Grey ground runs to a grey sky in long stepped terraces of slag, and along every rise sits a line of old
fortification facing outward, toward nothing you can see."*

The ground **ticks**. Small beetles in the black crust *"click faster where it runs hot, so you can hear where not
to stand."* Rust-orange lichen grows on the wrecks and nowhere else, and low plated grazers scrape it off the
hulls and look up at nothing.

On the nearest rise the stub of an old turret turns, slowly, and follows the ship down. It does not fire. It never
fires. When the ramp opens it is pointing at the ramp.

Along the line near the landing a ring of slumped pylons that was dead a minute ago begins to hum. *"The ship and
the old defense recognise each other."*

One ring on every map is working when the crew arrives (the build forces the first ring placed to be a live
one), so there is always a dome to find.

Before the first hour is out the player should have seen three things without going looking: a dead gun tracking a
walking crew member; a plated grazer scraping a wreck within arm's reach of one, uninterested; and something
leathery and wet-winged peeling off a dead machine and drifting toward the ship.

## The first day

- **Everything in the open is already stripped.** *"The open wrecks teach the rule: everything obvious is long
  plundered; the prizes are sealed."* Hermetic crates, ancient pods and the levels under the husks are where the
  stop pays. Jawa have to be shown this once.
- **Every old danger is already dead.** The sheet's rule, the owner's: *"Ancient dangers, plentiful — and ALL
  already opened and destroyed."* Sprung machine clusters, cracked vaults, spent horrors, lying beside the sealed
  salvage. *"This is what all that was for."* Nothing sealed here wakes when it is opened. The kit's line for
  what that does to a scavenger: the dread inverts, *"not 'what's inside' but 'what did this, and where did it
  go.'"* (Not true of the built biome yet: see Scope.)
- **The ground is poison and stays poison.** Open native ground renews its pollution. A floor or a roof over it
  pauses that; taking the cover away starts it again. The ponds are toxic. Nothing can be farmed.
- **The heat is the sun.** The sun stands high and the Direct Sun rule is the same one as everywhere: shade from a
  ruin wall or a roof is shade. Here that sun is worth about fifty degrees on top of air already near sixty. The
  crew was born for heat and still works this ground from shadow to shadow. (A wall's shade is shade from the
  sun. It is not a roof against the fall.)
- **The mynocks find the hull.** They are *"oddly cute — to the Jawa"*, and the sheet's last word on them is the
  crew in one line: *"Mynock pets — oddly cute, catastrophically hungry; the Jawa keep trying."*
- **The scavengers' own animals.** The pallbearer, armour-plated and unhurried, *"never seems to notice there was a
  war at all"*, comes for anything dead. The scar roach cleans what is left and runs from everything. The
  rakeshank, an ultra-gaunt carrion gleaner, is here because the owner put it here: of its picture, on
  2026-10-16, *"Wonderfully grotesque. Add it to the Warscar."* The bileworm rots a corpse to black bile within
  minutes and drinks it, leaving the dead pawn's gear in the puddle.
- **The beetles are a map.** *"Thick ticking means thick glower: rich harvest, and the place to stand least
  long."*
- **The mark begins.** Time on this ground brands a person, under a roof or not. On the first day it is nothing.

## The first week

- **The Settling.** Calm air is the hazard. When the wind has been low for hours *"the barrels on the line stop
  keening, the ticking carries farther in the hush, and a fine pale fall begins to come straight down. It is the
  war, still hanging in the air after all this time."* Anyone in the open takes poison; anyone under a roof or a
  humming ring does not. *"By morning every unroofed surface wears a film, and the film keeps footprints."*
- **Reading the film.** Every person, animal and raider that crosses it leaves prints pointing the way they went,
  and the prints stay until the wind returns. *"You can read where the raiders came in, where your hauler went,
  where the grazer circled before it charged."* It is this biome's answer to the rule that nothing vanishes
  without a readable sign.
- **The film finds the shells.** Buried unexploded ordnance is still faintly warm and the film will not settle on
  it, so *"after a Settling each one shows as a clean round spot."* Mark it; defuse it for shells and components,
  or set it off from a distance. *"The Settling becomes a minesweeper."* (One thing lies about it: a scar roach
  eats film, so a roach's clean patch looks like a shell's.)
- **The lift.** When the wind comes back the film goes, across the whole map, as *"a visible grey front crossing
  the map downwind"* with a brief dose for anyone it passes. *"The wind is back. The ground forgets."*
- **The grazer turns.** The plated chatrak is *"an animal built beyond fear, guaranteed to lose its mind"*. The
  owner's words for it: *"they care little about weapons or much of anything... until the madness inevitably
  comes."* It shows first, in stages a player can learn (plates lift, it stops eating, it circles), and the
  circling is on the film as a tight loop of heavy prints. Then it attacks and does not stop. (Live pass on all
  seven parts of the turn, 2026-10-06.)
- **Something nobody can see.** A line of prints walks across the film with nothing above it. See the moments.
- **The mark deepens, and it has a line.** By the owner's ruling it is both a small permanent cost to mood and
  nightmares while on this ground; *"leaving the map ends the nightmares, never the mark."* As built, a mark that
  has not yet crossed its halfway point fades after the crew leaves, a tenth a day, to nothing. Past that point
  it has a floor and never goes below it. The build notes put the crossing at *"about eight days on the map"*
  (a tuning number, and no promise pins it). So the Warscar's own clock is about a week: leave inside it and the
  crew forgets the place; stay past it and they carry it for the rest of the campaign. The Empire's probe arrives
  in the same week. That is the stop.
- **The hull count.** By the end of the week the question is how many mynocks are aboard, because *"meanness
  scales with population"* and they breed.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The gun that watches.** *On screen:* every broken turret on the line swivels to follow whoever moves, in
   silence. In a Settling they are the only things moving on the map. *Why it is alarming:* the player keeps
   waiting for one of them to fire, for the whole stop.
2. **The grazer and the firefight.** *On screen:* a plated grazer *"walks straight through a firefight to scrape
   lichen off a hull"*, shots sparking off it, not looking up.
3. **The snap.** *On screen:* the same placid animal, plates lifted, walking a tight circle for a day; then a
   sprint. *Why it lands:* the player watched it get ready and decided it could wait.
4. **The page.** *On screen:* morning after a calm: the whole map dusted pale and written on, every route anyone
   took overnight drawn in prints.
5. **Prints with nobody in them.** *On screen:* a single line of fresh prints crossing the film toward a crew
   member working alone, and the ticking of the beetles going quiet in a small ring that moves with it. The
   owner's words for the thing making them: *"Gotta make some invisible hunters now... tricky in this genre."* His
   answer of 2026-11-10 on how it meets people: *"Lone travel accepts an ambush. Companions and local clues
   provide protection."* It never attacks two together.
6. **The minesweeper.** *On screen:* a hooded figure crouched over a clean round spot in the film with a
   toolkit, and the rest of the crew watching from very far away.
7. **The ring wakes.** *On screen:* a dead projector ring humming because the ship is near, and when the fall
   comes, *"the film stops at the edge of the dome in a crisp circle."*
8. **Aboard.** *On screen:* a ceiling lamp inside the ship goes dark, then a stretch of conduit; a crew member
   opens a panel and three mynocks look back. *Why it is funny:* somebody names one.
9. **The lift.** *On screen:* a grey wall of dust crossing the map and the night's whole record going with it.
10. **The pallbearer.** *On screen:* after the fight, the one calm animal on the map walking in at its one speed
    to collect the dead, the crew's and anyone else's.
11. **The choice at the generator** (built, never seen). *On screen:* the ship's advisory letter on landing, and a
    crew member standing at the shield generator with two modules and one socket: the veil that turns the heat,
    or the screen that turns the air.
12. **The wall stands up** (0.2.0). *On screen:* a slag hump on the old line that has been rising and falling
    since the crew landed gets to its feet, and the letter reads *"Part of the Last Line just stood up."*
13. **It looked at the Cathedral first** (0.2.0). *On screen:* a dead machine on a cradle in the hold, a week of
    lights, then twitching, then pieces of a voice (*"I took the port out so I could not hear the next one."*),
    and when it finally stands it turns to face the same way every kneeling thing on the map faces, before it
    looks at the Jawa who woke it.

## When the Empire arrives

It arrives on time. Nothing here delays it.

- **It leaves prints too.** After a calm the film shows where a probe drifted, where the scouts stood and which
  way the strike team came in, *"before the letter says so"*.
- **The fall does not care whose armour.** A Settling doses everyone in the open. The crew has its roofs and its
  ring; a team walking in across the terraces has neither.
- **The ground is still mined.** Every shell the crew marked and did not defuse can be set off from range, and the
  crew knows where they are because the film showed them.
- **The grazers turn on whoever is near.** A chatrak that snaps during a fight is on nobody's side.
- **The ground marks them too.** As built, the mark accrues in every person on the map, visitors and prisoners
  included. A siege camp that sits here for eight days goes home changed.
- **They pull the wrong lever.** Blasting and demolition near the old line are what wake the wall (0.2.0), and a
  breaching assault is made of both.
- **The dead guns watch them as well.** They track the troopers exactly as they tracked the crew.
- *0.2.0:* **the guns can be made to fire.** An old-line turret refitted with components and steel is slow,
  long-ranged and the crew's.
- *0.2.0:* **the wall that eats walls.** One stretch of the old line *"has a slag hump that rises and falls every
  few seconds"*. Mining, demolition or blasting near it wakes the totchak, a colossal animal that walks to the
  nearest wall and eats it, ruins first and then anybody's. A breaching assault brings its own blasting.
- *0.2.0:* **the screen and the cloak.** A built aerosol screen keeps the crew working through a fall the besiegers
  have to stand in. Lacquer from the invisible hunter's hide makes a cloak that hides a wearer who stays still.
  The cloak's effect is permanent by his card of 2026-09-30 21:10. (It does not hide a ship.)
- *0.2.0:* **the listener.** One of the seven deserter histories has *"a receiver array grown oversized"* and, on
  the free tier, *"warns of raids an hour early"*. (Written; the build has the history and not yet the warning.)

## Who else attacks; who hates the Empire

- **The mad.** Scaria runs at half the wildlife. The owner ruled the cruelty stays: carriers cannot be made pets;
  *"scaria carriers are a lesson, not a pet."*
- **The invisible hunter,** on anyone alone, at night.
- **The feral munitions.** Small things that burst, arc and charge, *"breeding true since the last day"*. (They
  are donor and campaign animals today; what they are descended from is a campaign truth.)
- **The Forgotten Sentinels,** where the campaign places them (sparse, by his word at the legends sitting of
  2026-09-11: most strongpoints are bones, the manned one is the exception). *"The Forgotten Sentinels defend, never raid, never
  pursue past their lines, and never explain."* By the owner's ruling of 2026-09-11 they may strike whoever wrecks
  one of their structures, in range, *"but NEVER march on the colony"*. They are on nobody's side and they are the
  nearest thing this ground has to a third army: an Imperial team that blasts its way across Sentinel ground has
  picked that fight itself. Their attachment to this biome is not built: the grave-wards were wired to the
  campaign's old twin of this biome, the twin was deleted, and `WARSCAR_REWIRE_SCARLANDS_KIT_TWIN_GONE` is the
  open item. As last built they were stand-in machines of the mechanoid faction, which is hostile to everyone.
  (`UNSETTLED` whether they fight the Empire by design; as ruled, they fight anyone who breaks what they guard.)
  The shipped landing warning already tells the player *"The Forgotten Sentinels defend the ground"*, which on a
  free-tier map today is a promise with nothing behind it.
- **Runaway droids** come here to stop. *"Runaway droids flee here to die."* Whether any that are woken hold a
  grudge against the Empire is theirs to say, one history at a time.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The mark, which becomes permanent at about eight days.
- Whichever of heat and air the ship's one field is not turning.
- Poison in the body from the falls and the ground.
- Mynocks past the point where they are a nuisance.
- A chatrak herd reaching the end of its patience near the ship.
- No water that is not poison, no food that grows, and no fuel to be had.

**Stay, longer than the Empire would like:** almost nothing. A humming ring over the ship (and landing beside dead
ones wakes them). Roofs. Company on every errand. The Warscar is a raid, not a hide: the design is that the crew comes for the sealed things, pays in the
four currencies, and leaves early by its own choice.

## What the crew takes away

- **Sealed salvage:** hermetic crates, ancient pods, the contents of the levels under the husks.
- **Shells and components** from defused ordnance.
- **Chatrak plate,** *"the only light-armour leather that turns bullets"*. It is harder to come by than it
  sounds: the base game makes a carcass that carried the madness rot unbutcherable more often than not.
- **A projector core,** from stripping a dead ring: *"a prize you carry out, not a bench recipe."*
- **The mark,** on everyone who stayed. And **the mynocks,** unless they were all found.
- *0.2.0:* **a working shield generator.** His words: *"We're going to have to evaluate those shield generators
  if they're present and working. That's salvage man!"* A live ring can be assessed, pulled and carried home, and
  it runs there *"with no research"*: the build item calls it *"the prize of the biome, rarer than cores"*. Pulling
  it *"ends its dome on that map; that is the trade."*
- *0.2.0:* **the aerosol screen,** learned from a humming ring and buildable aboard: *"it works in every polluted
  biome, which is the reason to land here."* His rule for it: *"I like powerful tech. Don't be afraid of making
  good ideas broadly useful and powerful."*
- *0.2.0:* **a deserter.** Among the kneeling machines a few are intact. *"Walk in, carry one out, wake it."* His
  words: *"Those droids should be INTERESTING cases... they all left their owner, ran away, then died a slow
  death. That's gotta leave some strange features inside."* Waking one takes about a week, in stages: lights,
  twitching limbs, pieces of voice. An intact one packs down to be carried, so the cradle can be aboard. Seven
  histories are written and accepted as final by his card of 2026-09-30 (the one who cut its own leash, the
  counter, the carrier with a sealed box it never opened, the quiet one, the gardener, the defector, the
  listener). The carrier's three lines: *"Keep it safe."* ... *"Keep it safe from them."* ... *"From us. They said
  from us."* A failed repair leaves the same machine, by name, dead: never a blank chunk.
- *0.2.0:* **bloom liquor,** the reagent of the pools' most beautiful phase, *"a high-value trade good"* that burns
  whoever draws it.
- *0.2.0:* cloak lacquer; reagents from the pools; what the wall panels say, to those who can read them.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Nothing grows; open native ground renews its poison; a floor or roof pauses it and removing the cover restarts it. | Three patches of native ground: bare, floored, roofed. Clean them all, wait, uncover one. | The ground's own inspect text and the pollution overlay agree with what happened. |
| Open wrecks are stripped, sealed containers pay, and every ancient danger on the map is already sprung. | Open every sealed thing on a generated map. | A sealed threat that wakes on opening fails. |
| Broken turrets follow movement and never fire, on Warscar maps only. | A pawn walks the line; then the same turrets on another biome's map. | The other map's turrets do not turn. |
| In a long calm a pale fall begins, doses people in the open and not under a roof or a humming ring, and leaves a film. | Let a calm arrive by the weather's own course, with one pawn out, one roofed, one under a ring. | A calm forced by a debug command proves only the plumbing; the season must produce one by itself. |
| What crosses the film leaves prints that point the way it went and last until the wind returns; the returning wind clears film and prints together as a visible front. | A raid, a hauler and a grazer cross the film; save and reload; wait for wind. | Prints laid before the reload are still there after it. Film gone with prints left, or the reverse, fails. |
| Buried shells show as clean spots after a fall and can be defused for parts or set off from range. | A map with shells; a Settling; one defused, one triggered. | A spot with no shell under it would pass a lazy check: dig one that is not marked and find nothing. |
| A chatrak carrying the madness shows it in stages, then attacks for good; a treated one does not turn. | One carrier left alone, one cured, one clean arrival kept on the map. | The cured one stays calm through the time the other took. |
| Time here marks a person; the mark costs mood for good, gives nightmares only while on this ground, and roofs do not stop it. | Two crew, one who stayed a week and one who stayed a day, then both on another map. | Nightmares stop on leaving; the mark does not. |
| The crust beetles tick faster over hotter ground, the barrels keen in wind and fall silent in a Settling. | Walk a pawn from clean slag onto thick crust, in wind and in calm (a listening check at a joint sitting). | |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| An invisible hunter attacks only someone alone, shows when it strikes, and can be read beforehand by its prints and by the beetles going quiet around it. | One pawn alone at night on film; then two together on the same path. | The pair is not attacked. The hunter's kill is dragged and the drag is on the film. |
| Dead projector rings near a landed ship hum while it stays, and a humming ring keeps the fall and the film off the ground under it. | Land near a dead ring; wait for a Settling; lift off. | The ring goes dead again when the ship leaves. A ring far from the ship stays dead. |
| Mynocks board a landed ship, breed, and eat conduit, lamps and flooring until hunted out; a few are a nuisance and many are a problem. | A landed ship with wild mynocks near; leave them; then hunt them. | The damage stops when the last one is dead, and they are ordinary animals that can be shot. |

Settings: one switch per major feature, defaults as shipped, everything off leaves a hot, sterile ruin field
(standing rule, every mod).

## Shared machinery

**Featured here** (the Warscar is where each is vital and should be proven):
- **Ground that keeps footprints** (the capped track grid and its draw layer, ruled one kit shared with the
  Stillsand; each biome supplies only its surface and its eraser: film and wind here, sand and dunes there).
- **Weather that falls when the wind stops, and lifts as a front** (`RM_Settling` on the shared environmental
  weather condition).
- **A screen against airborne poison** (the particulate screen, lifted from the ship-shields mod; it works on
  toxic fallout, toxic rain, the Wasteland's ash and anything else that goes through the same vanilla call).
- **A latent condition that arms and then fires in visible stages** (`GameCondition_ArmLatentHazard`: the chatrak's
  turn).
- **A lasting scar with a floor that never clears** (`RM_HediffComp_SeverityFloor`: the mark).
- **A sound that tells you where the hazard is** (the proximity soundscape the Greentide also uses: the Geiger
  choir).
- **Invisible things made readable by the ground.** *"The Warscar answers every invisible hunter on the planet,
  by ground."*

**Merely active here:** ship vermin (`ShipVermin` and `CreatureBehaviors`: built once for every hull-infesting
creature by his ruling of 2026-09-11, and the mynock is its first tenant; the Warscar is where a crew is most
likely to pick them up); gnawing things that eat walls (the totchak uses the mynock's gnaw kit); the one sun from
geometry (high here, and nothing else); liquids (`FlowWorks`, for the reaction pools); wrecked machines and their
repair ladder (`WreckedMachines`, which the hospice reuses); staged lore (`LoreStages`, campaign); wreck salvage;
bones; the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket.

**The one signature (his first-version answer of 2026-11-19): NOT CHOSEN YET; two candidates, listed for the
Conductor.** His experience line names a curse that scavenging teaches: *"Poisoned forever, mad beasts, silent
guns. Everyone calls it cursed, and everyone who scavenges here learns why."*
- *The Settling:* in a long calm a pale fall doses people in the open and lays a film that records every walker,
  shows buried shells, and lifts when the wind returns. The cleanse chose it (2026-11-17). A stop sees it only if a
  long calm comes inside the stay; the design does not say how often one does.
- *The mark:* time on this ground marks a person, costs mood for good, and gives nightmares only here. A normal stop
  is sure to see it, because it accrues from time spent; it is the curse that *"everyone who scavenges here learns"*.
Moved now, because they are extras under either choice: the invisible hunter, the humming rings and the landed ship
waking them, and the mynocks aboard. The chatrak's turn stays as life (a native animal's disease and its cure).

**0.1.0, the stop**
- The land: sterile megastructure floors, slag and craters, the outward-facing line, stripped wrecks, sealed
  salvage, every ancient danger already sprung, poison ponds, ground that renews its pollution. (Built in part.
  Second reader: three of these are owed, not built. Nothing renews the ground's pollution today and the crust
  plants would die of it if something did, as the cleanse found. The sprung-danger dressing was wired to the
  deleted twin and never to this biome, and nobody has checked whether the base game's ruins here hold a sealed
  threat that still wakes. And no code arranges the line to face outward; it rests on the base game's ruin
  layouts, which nobody has looked at for that.)
- The Settling: calm, fall, film, prints on the shared grid, the lift front. (built, never seen live)
- Buried shells found by the film; defuse or trigger. (built; moved in)
- The cast: chatrak, tetchik, pallbearer, scar roach, rakeshank, bileworm, rimclaw, the three feral munitions
  (the tick that bursts, the one that shoots arcs, the juggernaut), korrum, wreck-lichen and glower crust, with
  the campaign's animals where its patch puts them. (built. His art sheet of 2026-10-05 cut the interim grazer
  and the mole: *"Cut this, no longer needed"*.)
- The chatrak's turn, its warning stages, and cure. (built; live pass)
- The mark: accrual, the lasting cost, nightmares only here. (built; live pass. The nightmare gate is an owed
  repair.)
- Turrets that track and never fire. (built)
- The Geiger choir: tick, keen, silence. (built)
- Chatrak plate as a material. (built)
- The ship worn by the air and by the heat, with one field to answer them. (built in the campaign's shield
  frame; never seen)
- No cover from orbit; fuel by the slow route only. (nothing to build)

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The invisible hunter and its signs: prints, the quiet ring, the shimmer, the drag. (built offline; moved in)
- Humming rings that screen the fall, and the landed ship waking dead ones. (built; moved in)
- Mynocks aboard. (built in the shared vermin mod; the animals arrive by the campaign's roster today, which is a
  wiring question for the free tier and not a design one)
*Already here before that answer:*
- Ring evaluation and salvage; the buildable aerosol screen aboard; glower shield panels and plate. (built in
  part)
- The hospice: kneeling rings, intact deserters with histories, the cradle, the five stages of waking, failure
  that leaves a recognisable wreck; a deserter that walks in on its own, sometimes with a pursuer behind it, and
  if turned away *"kneels at the map edge and stops"*. (built; second reader: four live checks passed on
  2026-11-06, bounded: rings and saved histories, a cradle run with its stages completed by a test hook, and a
  walk-in by ordinary movement. The histories' distinctive behaviours after waking are only partly built.)
- The totchak. (built offline)
- The lacquer cloak. (built)
- Turret refit. (built)
- The reaction pools: four phases, reagents, *"the prettiest phase is the deadliest"*. (built offline)
- The old tongue: panels a clever crew member can read, unlocking steps in the chains above. (built offline)
- War dust swept from the film. (built)
- The mark's trade (small skill bonuses) and the loosened panels that open only to the deeply marked. (built; live
  pass)
- The bileworm's rot and stench. (built) The ship's acoustic scanner readings here. (built)

**Later (a crew that stays, a colony, or the campaign layer)**
- The pilgrim camps and their journals; the five rungs of truth; the old tongue's translators; the bastion that
  could not fall; the droid hospice as a place with rumours beyond it: campaign.
- The Sentinels' attachment to this biome, their patrol lines and grave-wards: campaign.
- The three rites found here (the Open Boast, the Deserter's Welcome, the Vindication Walk): all rites are tabled.
- The stripped fleet as its own set of wrecks. Mynocks as pets.
- The screen's calibrated upgrade that scrubs gas and cleans ground.
- Transcriptions sold at a premium to scholars.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Any fertile cell, any green plant, snow weathers, intact treasure in the open (sheet bans).
- Sentinels that raid or pursue (sheet ban; local reprisal only).
- Glower-black uses (fuel, pigment, the war-black hull) and the Watch ritual (out by card, 2026-09-30). The hull
  plating is a cut ship idea; it stays down by his answer of 2026-11-19, and he can bring it back by name.
- The calm alarm and the entombed line (out by card, turn four). The bearing, the phantom barrage and the slag
  ricochet (left blank twice; treated as not picked).
- Narrowing the aerosol screen (he rejected it in words).
- The tetchik in a jar and its caravan warning (removed from source on 2026-10-23 as fluff; the picture he kept
  is still there).
- Cross-biome spread settings (off, unsupported, by the 2026-10-15 ruling).
- Biome rarity and placement scoring (no worldgen, ever).
- **Recommended for dropping, not yet his:** the rule that chatrak plate cannot be dyed (the cleanse recommends
  it; nothing depends on it).

## NEEDS HIM

None open. Every entry is answered (next section).

One question the cleanse put on its owner pages is answered here without asking: the label is "Warscar", the later
of the two cards.

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. (other) **"Etchant."** Fold the three reagents into one pool reagent for 0.2.0 (the design's default). *Delegated
   call.*
2. (hull) **Do mynocks belong to the free biome?** *His ruling:* his naming-tier ruling of 2026-09-22 (Q11a,
   `design/RimMandrake/biome_rulings.md`): a genuine canon name is IP and goes through the campaign layer. Campaign
   only.
3. (cover) **Is there anything here that hides a crew?** No. The Warscar's draw is its salvage (the design's default).
   *Delegated call.*
5. (hull) **Which field should a ship here have to give up?** As built: one generator, one field. That is the choice
   (the design's default). *Delegated call.*
6. (scope) **Do the dead of the old line stay dead for free-tier players?** Rewire the dressing onto this biome, item
   `WARSCAR_REWIRE_SCARLANDS_KIT_TWIN_GONE` (the design's default). *Delegated call.*
7. (scope) **The hospice in 0.1.0?** *His ruling:* the move card of 2026-11-18 (*"Move it, list every move"*): 0.2.0.

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

4. **The war-black hull, and glower as fuel.** *His card of 2026-11-19 (declined ship ideas):* they stay out, as his
   card of 2026-09-30 put them. The Warscar's fuel is the slow route only; the ship's wear here is the air and the
   heat, answered by one field. He can bring any of the three back by name.
