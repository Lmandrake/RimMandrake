# Warscar: the design, seen from the ship

**Status:** the one design document for the Warscar biome (`RM_Warscar`, source `src/RimMandrake/Scarlands/`; the
older documents call it the Scarlands, and the owner's card of 2026-09-30 set the label to "Warscar" with no
article), rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It
replaces the frozen definition sheet, the bedazzle review, the turn-three development document, the cast bible, the
kit spec and the cleanse proposal as the place to read; what happened to every idea in them is in
`design/concepts/Warscar/rewrite_choices.md`. Nothing has been deleted yet. This is a design document only and it
launches nothing.

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
home. Everything the heat is keeping warm is not.

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

**Fuel (his ruling of 2026-11-18).** **Emergency-slow biomass only**, and less of it than almost anywhere: there is
no soil, the only plants are a black crust and a lichen on wrecks, and the animals are armour and madness. The
sheet once listed *"glower fuel — radiogenic harvest from the black crusts"*; the owner's card of 2026-09-30 put
the glower's uses out, so it is not a fuel here. Nobody lives on this ground and nobody trades on it, so fuel
cannot be bought here either. A crew lands on the Warscar with the fuel to leave it, or it does not land.

**What the place does to the ship (his ruling of 2026-11-18, in 0.1.0).** Two things, both already in the sources.
- **The fall.** The toxic weather here was ruled *"a war aerosol, not rain"*, *"settling out as a corrosive fall
  when the air stills"*. In a Settling every unroofed surface takes a film, and the ship's skin is an unroofed
  surface. The answer is a **shield**: the old projector rings still screen the fall where they hum, a landed ship
  wakes dead rings near it, and the screen the crew can learn from them is the Warscar's named gift to the ship
  (*"a clean-air dome over the ship in any polluted biome"*).
- **The mynocks.** The sheet's own ruling: *"if the gravship comes to the Scarlands, mynocks get aboard —
  reproducing strangely fast, consuming conduit, flooring and lighting until hunted out of the hull. The biome
  follows you home."* The owner tuned it by card: *"Nuisance unless there are many."* The answer is hands-on: the
  crew hunts them out of the hull.

What is not built: any effect of the film on the hull itself (today it lays on ground and poisons people in the
open). The promise below is written for the ground and people around the ship and for the vermin aboard, and marks
the hull skin as owed.

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

Before the first hour is out the player should have seen three things without going looking: a dead gun tracking a
walking crew member; a plated grazer scraping a wreck within arm's reach of one, uninterested; and something
leathery and wet-winged peeling off a dead machine and drifting toward the ship.

## The first day

- **Everything in the open is already stripped.** *"The open wrecks teach the rule: everything obvious is long
  plundered; the prizes are sealed."* Hermetic crates, ancient pods and the levels under the husks are where the
  stop pays. Jawa have to be shown this once.
- **Every old danger is already dead.** The sheet's rule, the owner's: *"Ancient dangers, plentiful — and ALL
  already opened and destroyed."* Sprung machine clusters, cracked vaults, spent horrors, lying beside the sealed
  salvage. *"This is what all that was for."* Nothing sealed here wakes when it is opened.
- **The ground is poison and stays poison.** Open native ground renews its pollution. A floor or a roof over it
  pauses that; taking the cover away starts it again. The ponds are toxic. Nothing can be farmed.
- **The heat is the sun.** The sun stands high and the Direct Sun rule is the same one as everywhere: shade from a
  ruin wall or a roof is shade. This is the one hazard here the crew was born for.
- **The mynocks find the hull.** They are *"oddly cute — to the Jawa"*, and the sheet's last word on them is the
  crew in one line: *"Mynock pets — oddly cute, catastrophically hungry; the Jawa keep trying."*
- **The scavengers' own animals.** The pallbearer, armour-plated and unhurried, *"never seems to notice there was a
  war at all"*, comes for anything dead. The scar roach cleans what is left and runs from everything.
- **The mark begins.** Time on this ground brands a person. On the first day it is nothing.

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
  or set it off from a distance. *"The Settling becomes a minesweeper."*
- **The lift.** When the wind comes back the film goes, across the whole map, as *"a visible grey front crossing
  the map downwind"* with a brief dose for anyone it passes. *"The wind is back. The ground forgets."*
- **The grazer turns.** The plated chatrak is *"an animal built beyond fear, guaranteed to lose its mind"*. The
  owner's words for it: *"they care little about weapons or much of anything... until the madness inevitably
  comes."* It shows first, in stages a player can learn (plates lift, it stops eating, it circles), and the
  circling is on the film as a tight loop of heavy prints. Then it attacks and does not stop. (Live pass on all
  seven parts of the turn, 2026-10-06.)
- **Something nobody can see.** A line of prints walks across the film with nothing above it. See the moments.
- **The mark deepens.** By the owner's ruling it is both a small permanent cost to mood and nightmares while on
  this ground; *"leaving the map ends the nightmares, never the mark."* A crew member who stayed a week carries
  the Warscar for the rest of the campaign.
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

## When the Empire arrives

It arrives on time. Nothing here delays it.

- **It leaves prints too.** After a calm the film shows where a probe drifted, where the scouts stood and which
  way the strike team came in, *"before the letter says so"*.
- **The fall does not care whose armour.** A Settling doses everyone in the open. The crew has its roofs and its
  ring; a team walking in across the terraces has neither.
- **The ground is still mined.** Every shell the crew marked and did not defuse can be set off from range, and the
  crew knows where they are because the film showed them.
- **The grazers turn on whoever is near.** A chatrak that snaps during a fight is on nobody's side.
- **The dead guns watch them as well.** They track the troopers exactly as they tracked the crew.
- *0.2.0:* **the guns can be made to fire.** An old-line turret refitted with components and steel is slow,
  long-ranged and the crew's.
- *0.2.0:* **the wall that eats walls.** One stretch of the old line *"has a slag hump that rises and falls every
  few seconds"*. Mining, demolition or blasting near it wakes the totchak, a colossal animal that walks to the
  nearest wall and eats it, ruins first and then anybody's. A breaching assault brings its own blasting.
- *0.2.0:* **the screen and the cloak.** A built aerosol screen keeps the crew working through a fall the besiegers
  have to stand in. Lacquer from the invisible hunter's hide makes a cloak that hides a wearer who stays still.
  (It does not hide a ship.)

## Who else attacks; who hates the Empire

- **The mad.** Scaria runs at half the wildlife. The owner ruled the cruelty stays: carriers cannot be made pets;
  *"scaria carriers are a lesson, not a pet."*
- **The invisible hunter,** on anyone alone, at night.
- **The feral munitions.** Small things that burst, arc and charge, *"breeding true since the last day"*. (They
  are donor and campaign animals today; what they are descended from is a campaign truth.)
- **The Forgotten Sentinels,** where the campaign places them. *"The Forgotten Sentinels defend, never raid, never
  pursue past their lines, and never explain."* By the owner's ruling of 2026-09-11 they may strike whoever wrecks
  one of their structures, in range, *"but NEVER march on the colony"*. They are on nobody's side and they are the
  nearest thing this ground has to a third army: an Imperial team that blasts its way across Sentinel ground has
  picked that fight itself. Their attachment to this biome is not built (`UNSETTLED` whether they fight the
  Empire by design; as ruled, they fight anyone who breaks what they guard).
- **Runaway droids** come here to stop. *"Runaway droids flee here to die."* Whether any that are woken hold a
  grudge against the Empire is theirs to say, one history at a time.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The mark, which only deepens, on a crew that has to live with itself afterwards.
- Poison in the body from the falls and the ground.
- Mynocks past the point where they are a nuisance.
- A chatrak herd reaching the end of its patience near the ship.
- No water that is not poison, no food that grows, and no fuel to be had.

**Stay, longer than the Empire would like:** almost nothing. A humming ring over the ship. Roofs. Company on every
errand. The Warscar is a raid, not a hide: the design is that the crew comes for the sealed things, pays in the
four currencies, and leaves early by its own choice.

## What the crew takes away

- **Sealed salvage:** hermetic crates, ancient pods, the contents of the levels under the husks.
- **Shells and components** from defused ordnance.
- **Chatrak plate,** *"the only light-armour leather that turns bullets"*.
- **The mark,** on everyone who stayed. And **the mynocks,** unless they were all found.
- *0.2.0:* **a working shield generator.** His words: *"We're going to have to evaluate those shield generators
  if they're present and working. That's salvage man!"* A live ring can be assessed, pulled and carried home.
- *0.2.0:* **the aerosol screen,** learned from a humming ring and buildable aboard: *"it works in every polluted
  biome, which is the reason to land here."* His rule for it: *"I like powerful tech. Don't be afraid of making
  good ideas broadly useful and powerful."*
- *0.2.0:* **a deserter.** Among the kneeling machines a few are intact. *"Walk in, carry one out, wake it."* His
  words: *"Those droids should be INTERESTING cases... they all left their owner, ran away, then died a slow
  death. That's gotta leave some strange features inside."* Waking one takes about a week, in stages: lights,
  twitching limbs, pieces of voice.
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
| An invisible hunter attacks only someone alone, shows when it strikes, and can be read beforehand by its prints and by the beetles going quiet around it. | One pawn alone at night on film; then two together on the same path. | The pair is not attacked. The hunter's kill is dragged and the drag is on the film. |
| Time here marks a person; the mark costs mood for good, gives nightmares only while on this ground, and roofs do not stop it. | Two crew, one who stayed a week and one who stayed a day, then both on another map. | Nightmares stop on leaving; the mark does not. |
| Dead projector rings near a landed ship hum while it stays, and a humming ring keeps the fall and the film off the ground under it. | Land near a dead ring; wait for a Settling; lift off. | The ring goes dead again when the ship leaves. A ring far from the ship stays dead. |
| Mynocks board a landed ship, breed, and eat conduit, lamps and flooring until hunted out; a few are a nuisance and many are a problem. | A landed ship with wild mynocks near; leave them; then hunt them. | The damage stops when the last one is dead, and they are ordinary animals that can be shot. |
| The crust beetles tick faster over hotter ground, the barrels keen in wind and fall silent in a Settling. | Walk a pawn from clean slag onto thick crust, in wind and in calm (a listening check at a joint sitting). | |

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

**0.1.0, the stop**
- The land: sterile megastructure floors, slag and craters, the outward-facing line, stripped wrecks, sealed
  salvage, every ancient danger already sprung, poison ponds, ground that renews its pollution. (built; the
  renewal and the crust plants' tolerance of it are owed repairs the cleanse named)
- The Settling: calm, fall, film, prints on the shared grid, the lift front. (built, never seen live)
- Buried shells found by the film; defuse or trigger. (built; moved in)
- The cast: chatrak, tetchik, pallbearer, scar roach, wreck-lichen and glower crust, with the donor and campaign
  animals where they are. (built)
- The chatrak's turn, its warning stages, and cure. (built; live pass)
- The invisible hunter and its signs: prints, the quiet ring, the shimmer, the drag. (built offline; moved in)
- The mark: accrual, the lasting cost, nightmares only here. (built; live pass. The nightmare gate is an owed
  repair.)
- Turrets that track and never fire. (built)
- Humming rings that screen the fall, and the landed ship waking dead ones. (built; moved in)
- Mynocks aboard. (built in the shared vermin mod; the animals arrive by the campaign's roster today, which is a
  wiring question for the free tier and not a design one)
- The Geiger choir: tick, keen, silence. (built)
- Chatrak plate as a material. (built)
- No cover from orbit; fuel by the slow route only. (nothing to build)

**0.2.0, the stop with company**
- Ring evaluation and salvage; the buildable aerosol screen aboard; glower shield panels and plate. (built in
  part)
- The hospice: kneeling rings, intact deserters with histories, the cradle, the five stages of waking, failure
  that leaves a recognisable wreck; a deserter that walks in on its own. (built offline)
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
- The stripped fleet as its own set of wrecks. Mynocks as pets.
- The Open Boast rite (tabled with all rites, 2026-10-03).
- The screen's calibrated upgrade that scrubs gas and cleans ground.
- Transcriptions sold at a premium to scholars.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Any fertile cell, any green plant, snow weathers, intact treasure in the open (sheet bans).
- Sentinels that raid or pursue (sheet ban; local reprisal only).
- Glower-black uses and glower fuel; the Watch ritual (out by card, 2026-09-30).
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

1. **"Etchant."** On 2026-11-10 he wrote: *"I don't know what Etchant even is, so we will need to revisit these
   strange little design quirks that seem to have gotten into the notes to make sure we still want it."* It is one
   of three reagents drawn from the pools (with a gel for the screen and a coagulant), adopted by his card of
   2026-09-30 from an outside consult, and it is what machine repair and turret refit consume. This design keeps
   every chain that used it out of 0.1.0 and writes 0.2.0's refit and waking as needing *"components and steel"*
   only. *Keep the three reagents as adopted. Fold them into one "pool reagent"* (default for 0.2.0: one thing to
   learn, one colour table). *Drop pool reagents as inputs:* the pools are then scenery and hazard, and the chains
   cost ordinary parts.
2. **Do mynocks belong to the free biome?** The sheet makes the infestation the Warscar's own (*"the biome
   follows you home"*), but the mynock is a canon animal and arrives only through the campaign's roster. *Campaign
   only* (default, as built). *An invented hull-leech of ours in the free tier:* the free Warscar then wears on
   ships too, and it needs a creature and art.
3. **Is there anything here that hides a crew?** As written, no, and this design says so plainly. The one
   candidate in the sources is the lacquer cloak, which by its built rule *"does not cloak ships"*. *Leave the
   Warscar with no hide* (default: every biome need not have one, and "found on schedule" is this stop's
   character). *Let lacquer be painted on a hull at a punishing price:* a second reason to come, and a new system.

One question the cleanse put on its owner pages is answered here without asking: the label is "Warscar", the later
of the two cards.
