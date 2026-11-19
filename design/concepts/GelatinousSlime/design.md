# The Slime: the design, seen from the ship

**Status:** the one design document for the Gelatinous Slime biome (`RM_GelatinousSlime`, source
`src/RimMandrake/GelatinousSlime/`), rewritten 2026-11-18 on the owner's instruction to see every biome "through the
lens of Utinni". It replaces the older definition sheet, the mod brief, the Titanoslime spec, the review and the
cleanse proposal as the place to read; what happened to every idea in them is in
`design/concepts/GelatinousSlime/rewrite_choices.md`. Nothing has been deleted yet. The Gelatinous Slime is one of the
six biome mods HELD BY OWNER: this is a design document only and it launches nothing.

**Who reads this next:** a Designer run on this concept is handed the list of files in
`design/concepts/GelatinousSlime/` (`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in
its path by sitting here. Nothing in the pipeline reads it by name yet. The Slime has a Designer tree: an adopted
root (`root.md`), a locked sheet of twelve leaves (`sheet.md`) and a chosen showcase, all written for a colony; and a
cleanse proposal of 2026-11-17 that moved the gene journey out and asked him whether that was right. This design
answers that question by scope (the journey is in) and says where it parts from each.

**Second reader, 2026-11-18:** a second agent that did not write this page read the mod brief, the Titanoslime
spec, the review, the gene lists and the roster whole (the first read had them in part) and repaired it. The gene
run now follows his card of 2026-09-10: the seeker is drawn in the open and the needle goes in wherever the crew
likes, so the coma is in a bunk aboard. The return from the last touch moves from "later" to 0.2.0, because the
archive vat is this biome's part on the ship list and is built. The glurro is gone (cut before this pass; nothing
of it is in source). The contact-point scrub on the hull is withdrawn: it was the cleaning half of a ship pitch he
passed over on 2026-10-02. What does reach the ship is in the sources and is the giant. What changed and why is at
the top of `rewrite_choices.md`. The locked sheet, root and tree (`sheet.md`, `root.md`, `tree.json`) describe a
colony; they are not edited here, and a later Designer run reconciles them with this page.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
cleanse census of 2026-11-17 or the bedazzle review of 2026-10-02 found it in source; it does not mean it has passed
anything.

**What kind of place:** land, of a sort. A flat living body on the terminator (checked against the sheet's own
header and §0: *"it straddles the terminator itself"*, median 13.4 °C, *"the mildest, most stable climate on
Ash'karr"*, *"zero water and river tiles"*). It is not a sea and the ship lands on it. What it lands on is alive.

---

## What this place is

> *"Kind, generous and slowly eating you. It feeds you, heals you and reads you, and the price is who you are."*
> (owner, by card, 2026-10-20)

> *"A body the size of a country, reading everything that touches it."* (`the_slime.md` §9)

*"It was a weapon once. It ate everything it was sent against, and what it ate unmade it — now it is a living
registry and database, forever seeking to ingest, analyze, recombine, store, and multiply, still faithfully serving
a master ages decayed."* Its grass, its trees and its herds are its own flesh. There is no rock and no soil. *"Stand
on it for a week unprotected and it reads you so thoroughly that you become an entry and there is nothing left to
bury."* It does not hate anyone. It does not think. *"So far, it only reads."*

His words for the wonder at the middle of it, 2026-09-10: *"the machine that allows a player to select a target
gene, identify it, extract some slime and inject it into their body, collapse into coma and then... turn into slime
unless they have a friend nearby to administer the slime antidote in time."*

**Seen from the ship, this is the friendliest landing on the planet, and the crew should not believe it.** Mild
air. No storms. Nothing attacks. Food underfoot, drinkable rain, a cure for any poison free for the scooping, and a
catalogue of every gene that ever touched the place, available to anyone prepared to go and stand in it. A Jawa
has never been offered so much for nothing. Each of those gifts is the body beginning to read whoever took it.

And the cure is the ship. The brief's law since 2026-09-10: *"drying biomes: desert/arid halt slimification... walk
it dry."* A crew with a hull does not walk. For desert people the way out of the Slime is to go home. The brief is
exact about it: in dry country a late film does not just hold, it fades, in about four or five days, *"slower than
it grew; the walk must be earned."* The salt sea counts too (*"brine leaches the film"*). In ordinary country it
only holds.

His answers of 2026-11-10 keep it plain: no new rescue interface (*"We make it work in their existing ui... If you
want to be nice just send a message at a certain critical moment of how much time left"*); the returned dead meet
*"grief and moving on"*; and the weapon made from the giant makes its victims *"struggle now"*, nearby allies
included.

His words on the giant, 2026-09-20: *"I am now enchanted by the idea of a titanic green slime... It should have the
devoured ability to swallow pawns whole of nearly any size."* And his ruling the next day, which matters to anyone
parked beside one: growth is permanent. *"A fed slime is a permanently escalating threat."*

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. A loud crew halves every
wait and a hidden one doubles it.

**Cover from orbit here: none.** The terminator's light is a *"permanent low amber"*, not dark. *"Clear stays
common."* The slime rain is brief. There is no canopy: the trees are *"rounded pseudo-trees"* on *"the flat immense
horizontal of the body itself."* It is, in the sheet's words, *"the one biome that shines by day."* A hull parked
on it can be seen, and every step the crew takes shows: *"footprints always show."*

**How long a stop lasts (the outer edge).** By the Empire's clock: a first probe in five to eight days and the
whole ladder run in about **three to five weeks**. By the body's clock, shorter: unprotected flesh in contact
converts in *"~1 week"*. A crew that works from the deck, wears what it should and carries antidote can stay for the
Empire's three to five weeks. A crew that does none of that has a week. Most stops should be a few days: fill the
tanks and the larder, send one fool for a gene, leave.

A season is fifteen days. The body's one seasonal lesson (*"farms fail by conversion... within a few harvests"*) is
not for a crew that does not farm, and is "later".

---

## The first minutes

A wet, shining plain under low amber light. *"Translucent greens and ambers, membrane pinks in the rich ground."*
Domed things the height of a knee wander in loose herds. Something like a bladder with fronds drifts overhead.
Somewhere toward the horizon there is a hill of green glass, and it has shapes inside it: *"a shell, a jawbone, a
tool haft — entries not yet filed."* It is quiet. *"Donor silence kept: wet stillness... and underfoot always the
faint sound of moving-through."*

The ramp comes down onto ground that gives. The first Jawa off it leaves a footprint, and the footprint slowly
fills.

Before the first hour is out the player should have seen: that there are three kinds of ground (crust that can be
built on, soft ground that is slow, and liquid channels that move); that nothing here is rock; and that a crew
member standing on bare slime has started to show a film.

## The first day

- **Stand on something.** A roof does not stop contact. A built floor that is not slime does. The ship's deck is
  the largest such floor on the map; planks from the ramp to the work site are the first job.
- **The film.** Bare contact starts it. Early on it recedes by itself once the person is off the slime. Later it
  does not. The ordinary health display shows the course; there is no special screen. The brief's four steps:
  touched (a sheen), slicked (a green tint, slower, clumsier, and it no longer goes by itself), half-absorbed
  (heavy, painless, *placid*: they stop running from things), and returned to the flow. The art law for all of it:
  *"film, tint, drip — never eyes, never buds, never new limbs."* That is the Contagion's business, not this
  place's.
- **Slippery.** His word of 2026-10-16: *"Natural slime should also be slippery."*
- **The larder and the tanks.** Cooked slime is *"disgusting but fully edible."* When the body is thirsty it *"sweats
  into the sky and pulls down a warm green rain that fills every barrel"*, drinkable, standing briefly on bare
  ground and draining back. The rain is the drink. The living slime is not: by his thirst ruling of 2026-10-17 it
  is drunk only when there is nothing else, at *"a massive negative mood impact, a lingering laxative health issue
  for a day"*, and the green kind is then *"full exposure to the absorption rules from that biome."*
- **Stone is pressed, not quarried.** A compressor turns ooze into block. *"Construction here means eating the
  database."*
- **The cure that starts a clock.** Raw slime *"instantly cures any poison in you, and most radiation"*, and then it
  starts on the one who swallowed it. For a crew fresh from the Cauldron this is the best offer on the planet and
  the worst.
- **The antidote.** A deliberately toxic injection ends the Slime's hold. It hurts. A friend can give it. It is
  made from the thing itself, raw slime and neutroamine at a drug bench: *"cheap enough to keep two in the fridge,
  dear enough that a caravan carrying none made a decision."*
- **The neighbours.** Gelatid herds that *"pool together at night, and split again by morning with no apparent
  sense of which half was which"*; the scoop-mouthed gappo, small, middling and huge; the dwommo, an amber bladder
  floating over all of it (*"The Slime cannot touch it. The little herds below treat it as weather."*); the oomb,
  small, middling and great, a spiked lobe that eats litter and *"leaves the ground clean behind it"*; the wuum,
  budding copies of itself; the fubbum, the one hunter, with *"no interest in anything that stands taller than the
  herds it hunts."* None of them minds the crew. The oomb and the wuum burst when they die, *"and what bursts out
  burns like acid."*
- **The plants.** Slime-grass, bellows, thumbstalk, and the readerbloom, a pale disc on a stalk that stands where
  the flow beneath is dense: *"prospectors of a certain kind learned to read them as a sign, which is a polite way
  of saying they learned where to stand and got read back."* Some of the animals that wander in from next door
  are part-read already and do not seem to have noticed.

## The first week

- **The gene.** By his card of 2026-09-10 the machine is a thing held in the hand: *"It is a machine you hold that
  tells you WHERE you must go to extract (a scanner). Then you place it upon the slime, and it expends itself
  sucking up just the right parts of the slime, becoming an injectible. Then it is used up once used to inject."*
  So: pick one gene from the archive of *"everything that ever touched it"*. The seeker points to where on the
  map the current carrying it will pass, and when. One crew member walks out there, onto the open body, sets it
  down, and stands exposed while it drinks. Then the walk home with the dose, which keeps for days and no longer.
  The needle can go in anywhere, *"including home in bed, which is the point: bring it back to your people."*
  *Coma.* Then the race: the reading runs fast in a comatose body, and unless a friend gives the antidote in time
  the bunk holds *"a smear."* *"A lone pawn cannot do this and live."* Whoever wakes has the gene they wanted, one
  they did not choose, and a mark other people can see. The accepted gene lists (2026-09-06) price all of it where
  this crew lives: *"costs land where Jawas live — haggling, sneaking, scavenging, tinkering, warren life. A gene
  should make a Jawa argue with themselves."* And *"the marked are hard to love"*: *"One gene is a quirk; four is
  a creature."* That matters in a clan whose whole future is who will lie down with whom. The seeker is crafted
  blank at an ordinary bench; nobody has to sell one.
- **What is on the list.** In the campaign's archive: a scavenger's nose that finds a third more in every wreck and
  never closes; a trader's head that grieves over anything given away (*"that had VALUE"*); buoyant step, to *"wade
  the Slime like a local"*; and resistance itself, whose price is the cure (*"you chose the wall over the well"*).
  The riders nobody chooses include involuntary loud Jawaese when startled, a pocketing instinct, a snore, and one
  he commissioned himself: the Reek, *"offensive even to other Jawas."*
- **The giant.** A Titanoslime *"hunts by rolling over things."* It swallows prey whole, crew included, and what it
  holds can be got out again while there is time, and the time is shown: about two hours for someone
  crew-sized, during which they neither bleed nor starve. Down it or kill it and they fall out stunned and
  acid-burned, with the film a step further on. Leave it and they are absorbed: the gear comes back, and *"there is
  nothing to bury."* What it eats makes it permanently bigger, and a bigger one holds more at once and swallows
  bigger things. It arrives small. *"Stages 4 and 5 are only ever earned on the player's map, so the player has
  watched it happen."* It swallows flesh only: a machine it merely hits. Hurt, it always comes for whoever hurt
  it. The cold nights slow it.
- **The ruins.** *"Fence lines and dead irrigation sinking into slime-grass, every ruin a legible story of someone
  who thought they'd beaten the conversion rate."* Other people's abandoned gear, half absorbed.
- **The ledger.** By the end of a week, anyone who has been careless with bare ground is past the stage where
  stepping off it helps. They need the antidote, or they need the desert.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The gene run.** *On screen:* one Jawa far out on the shining flat, standing still beside a device that is
   drinking the ground, the film creeping up its legs, and a hill of green glass beginning to turn that way. Then
   the long slow walk home with the dose. Then a bunk aboard, a needle, a body gone slack, a clock in the health
   tab, and a friend with the other needle. *Why it lands:* every step is chosen and the clock is on screen. If the
   friend is late there is *"a smear in the bed."*
2. **What it came back with.** *On screen:* the survivor on its feet, with the tail it wanted and something it did
   not ask for.
3. **The hill ate one of them.** *On screen:* a slope of green jelly rolls over a crew member, who is then visible
   *inside* it, drifting, with a timer. The rescue is the others attacking a hill.
4. **Lunch.** *On screen:* a poisoned crew member eats a handful of raw slime and is cured on the spot, to general
   relief; then the film appears and the relief stops.
5. **The rain.** *On screen:* a silver-green curtain, every barrel on the apron filling, standing water on the
   bare ground and none on the planks, and the whole flood drinking back into the land within the hour.
6. **Footprints.** *On screen:* a crew member's trail across the crust filling in behind them, one print at a
   time.
7. **The visitor.** *On screen:* an animal the crew knows from another biome wanders past, half translucent,
   grazing, perfectly calm.
8. **The night pool.** *On screen:* the knee-high herds drifting together at dusk into one mass, and the fubbum
   arriving.
9. **It grew.** *On screen:* the small hill that has been grazing by the ramp all week swallows a gappo, pauses,
   and is visibly larger; the message says so. Nobody remembers deciding to keep it fed.
10. **Through the wall.** *On screen:* the same hill, weeks and many meals later, the size of the ship's bow,
    crossing the apron in a straight line through whatever is standing on it. (The wrecking is the giant-creature
    machinery's, when that mod is loaded; nobody has watched this one do it.)
11. **The one who came back (0.2.0).** *On screen:* a glass-fronted vat on the deck, three days of power, and a
    dead crew member stepping out as they were the last time they touched the slime, *"and no memory of anything
    since."* His question, which is the design: *"But are they the same?"* *"The old grave stays where it is."*
12. **The piece (0.2.0).** *On screen:* a chunk torn off the giant and thrown; everyone it lands on, and everyone
   standing next to them, is at once coated and struggling. His words: *"a terrible bomb like weapon... Bioweapon
   after all."* A Jawa threw it. A Jawa is standing next to them.

## When the Empire arrives

It arrives on time. Nothing here hides the ship.

- **Everyone wades.** The soft ground slows troopers as it slows the crew. A crew on planks is the only thing on
  the map that moves at speed.
- **The body reads them too.** Contact films any unprotected flesh. A week is longer than a raid lasts, so this
  matters to a siege and not to a strike. `UNMEASURED`: whether Imperial armour counts as protection.
- **The hill does not take sides.** A Titanoslime rolls over whatever is in its way, by reflex and never by
  intent. A cordon's emplacement is in its way if the crew can arrange that. It swallows troopers as it swallows
  anyone made of flesh, and every one it finishes makes it bigger, for good. It does not swallow droids.
- **The rain** floods bare ground under a siege camp and not the crew's floors.
- **The piece (0.2.0).** The one weapon this place gives is thrown by hand and coats friend and foe alike.
- **No high ground, no walls, no rock.** The body is flat and there is nothing to build a fort from but pressed
  slime. This is a bad place to be found.

## Who else attacks; who hates the Empire

- **Nothing here is hostile on purpose.** *"Slimified creatures are never hostile"* is law. The giant feeds; the
  fubbum hunts the herds; a cut giant leaks gelatids. That is all.
- **The Ascendant Helix** *"come to sell, not to stay"*: they sold the machine and lost interest. Margin-dwellers
  live on the edges: *"slime-cooks, pit-renderers, machine-pilgrim outfitters."* Both are campaign-layer people.
  Whether any of them cares about the Empire is `UNSETTLED`.
- **The Wildsteam** will not come near the place, and their routes visibly bend round it.
- **The body itself** is the nearest thing to an enemy and is not one. *"The fear of more is rumor."*

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The film, on anyone who has been walking bare ground. The stop can end because the cure is elsewhere.
- A coma with no antidote left aboard.
- A crew member inside the giant and no way to get them out in time.
- A sky with nothing in it between the ship and a probe.

**Stay, longer than the Empire would like:**
- Planks, the deck and the antidote: with all three the body is only a larder.
- Food and water that cannot run out.
- Ground that slows every attacker to a crawl.
- Nothing else. The Slime does not help anyone hide.

## What the crew takes away

- **Full tanks and a full larder,** of the least appetising food on the planet. *"A place to fill your belly and
  your tanks."*
- **A gene,** chosen, with its rider and its mark, in one crew member for life and in their eggs after.
- **Resistance,** the same way: the Slime-resistant gene is in the archive like any other, and it shuts off the
  cure with the hazard.
- **The deck part: the archive vat (0.2.0).** This biome's entry on the list of what each place gives the ship
  (`BIOME_SHIP_CONTRIBUTIONS_1`; `RM_ArchiveVat`, built): it *"grows a dead colonist back from the slime's last
  reading of them, anywhere the ship goes."* His ask, 2026-10-02: *"An ability to resurrect someone from the last
  time they touched the slime. Requires expensive helix tech."* The body files everyone who touches it, so a crew
  that has stood on the Slime once carries its own back-ups away with it.
- **Pressed block,** stone from a place with no stone.
- **The antitoxin trick,** for as long as there is antidote to follow it with.
- **Rendered cargo (0.2.0):** the slime pit makes safe food of the toxic and the indigestible, which is what the
  hold is full of after the Cauldron and the Rot. By his card of 2026-10-11 it also makes the Rot's ambrosyx into a
  lavish dish with the addiction taken out. *"The gourmet chain now spans three biomes"*, and only a ship visits
  three biomes.
- **Fuel:** emergency-slow only. The body is biomass to the horizon and renders to fuel no faster than anything
  else does. The Helix and the margin-dwellers are the only people who might sell any, and both are campaign-layer
  traders not built into the biome.
- **Not the piece.** Off the body it shrinks; it *"never stockpiles."*
- **The film,** if they were careless, until the desert dries it out.

## What the place does to the ship

- **By itself, nothing.** The review of 2026-10-02, in the plain words read to him on the card: the Slime *"does
  nothing to your ship."* It reads flesh, and a hull is not flesh. The shared shield frame in
  `src/RimUtinni/ShipShields/` agrees: the air is mild, the rain carries no sand, and this biome is not one of the
  three marked as fouled air, so none of the frame's hazards is raised here. The ship's deck is built floor, and
  built floor is what stops contact.
- **Its giant, if the crew feeds it.** The Titanoslime spec is plain about the big ones: *"a stage-4 titanoslime
  walking through a wall is the Titanic Creatures mod doing exactly what it was built for."* A giant only reaches
  that size by eating on the map in front of the player, and by his ruling of 2026-09-21 it never shrinks again.
  So the one thing here that damages a ship is a thing the crew allowed to grow next to it. That is the hull wear
  the sources give this place, and it needs no new system: the giant-creature mod's wake does the wrecking where
  that mod is loaded.
- **Three ship ideas were put to him on 2026-10-02 and he chose none of them,** answering each card item in his own
  words instead. They are listed in `NEEDS HIM` and not revived: the Landing You Cannot Take Back (the body reads
  the hull's contact points; clean them or sell a passenger's gene), the Unfiled Hull (a swallowed ship inside the
  oldest giant, stripped for *"a ship-grade part for the gravship"*), and the tamper-proof seal for freight.
- **Withdrawn.** The first read's default, slime gathering at the contact points and scrubbed off by hand, was the
  cleaning half of the first of those. It is not this page's to bring back.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A living plain: buildable crust, slow soft ground, moving liquid channels, no rock anywhere, soft-bodied life. | A fresh map at ordinary zoom. | A quarry, or a vanilla animal standing in for a native, fails. |
| Bare contact films unprotected flesh; the ordinary health display shows the course; early film recedes off the slime and late film does not. | Three pawns: one on planks, one on bare slime briefly, one for days; then all moved to a floor. | A roof with a slime floor does not protect. |
| Left alone the course ends in dissolution, and the victim's belongings remain. | One pawn left to the end. | Gear that vanishes with the body fails. |
| Leaving for dry country, or a completed antidote treatment, ends the hold. | One late-stage pawn flown to desert, one treated. | The antidote is toxic and shows it. |
| Slime gives food, block and poison relief by ordinary work, and raw slime's cure starts the film. | A cooked meal eaten, a block pressed, a poisoned pawn fed raw slime. | A free cure with no film fails. |
| Organism rain leaves drinkable standing water on bare ground, none on floors or under roofs, and drains away. | One rain over mixed ground with barrels out. | Water that stays, or that cannot be drunk, fails. |
| A chosen gene is found with the seeker and drawn in the open on the body, the carrier exposed while it drinks; the dose keeps for days and then spoils. | The journey start to finish; one dose left to spoil. | A dose made at a bench or handed over by a helper is not the journey. |
| The injection, given anywhere, brings a coma and a race; a friend's antidote in time saves the patient; there is a message when little time is left. | One rescued aboard, one not. | No new interface: the game's own, plus the one message. Nobody rescues themselves. |
| The survivor keeps the chosen gene, an unchosen one, and a mark others react to; it passes to offspring. | The rescued pawn, afterwards and a generation on. | A journey with no cost fails. |
| The natives live as an ecology (herds that pool at night, three sizes of scoop-feeder, a real flier, a hunter of the herds); outsiders arrive part-read; nothing turns hostile from being read. | A week of the map left alone. | Flight is read from state, never watched unattended. |
| The giant swallows prey whole, shows how long a rescue has, gives up the same person if freed in time, and keeps what it gains from feeding. | A crew member engulfed and cut free; an animal engulfed and digested; a save and reload after. | A giant that shrinks again unseen fails. |
| The Slime itself leaves a landed ship alone, and the deck counts as built floor. | A ship through several days, crew kept on deck. | A film on someone who never left the deck fails. |

Settings: one switch per major feature, defaults as shipped, everything off leaves a mild wet plain with ordinary
soft animals; switching a feature off stops what it does, clears film safely, releases anything swallowed and keeps
size the giant has earned (standing rule, every mod, and the cleanse's own detail).

## Shared machinery

**Featured here** (the Slime is where each is vital and should be proven):
- **Ground that changes whoever stands on it, with built floor as the answer** (`MapComponent_SlimeExposure`, the
  slimification ladder).
- **A cure that lives in another biome** (the drying-country rule): the only hazard in these designs whose answer
  is to leave.
- **A creature that holds what it swallows, and grows** (`RM_CompEngulfer`; the life-stage growth with no Harmony
  patch).
- **Choosing a gene and paying an unknown price** (the seeker, the archive, the rider).
- **Organism rain that is drinkable and drains** (and that `FlowWorks` treats as toxic water for distilling).

**Merely active here:** soft ground that slows (the Greentide's churnmud mires; this only slows); real flight for
the dwommo; animals wandering in from neighbouring biomes; plants that grow fast when wet (`ExplosiveGrowth`, left
on); the one sun from geometry, low and mild at the terminator; roads, allowed here by his card of 2026-10-20; the
Empire's search and the visibility dial; the acoustic sounder.

## Scope

Every feature is in one bucket.

**0.1.0, the stop**
- The land: crust, soft ground, channels, no rock; organism rain, drinkable and draining. (built; the rain's
  drinkable water and drainage are unproven)
- Contact film, its course, dissolution with belongings left; drying country and the antidote as the ways out.
  (built)
- Food, pressed block and poison relief from the body. (built)
- The gene journey: archive, seeker, extraction in the open, the perishable dose, coma, the friend's rescue with
  its one message, the rider, the mark, inheritance. (built)
- Resistance as a gene taken the same way. (built)
- The native ecology: gelatid, the gappo family, dwommo, fubbum; part-read visitors; nothing made hostile.
  (built; several still wear stand-in art)
- The Titanoslime: engulfing, visible rescue time, permanent growth. (built; his look at its art is owed)
- The farm ruins as places. (built)
- The oomb family and the wuum; the four plants. (built)
- The deck as built floor; nothing in the shield frame raised here. (built)
- A fed giant walking through what is in its way. (the giant-creature mod's wake; unproven on this animal)

**0.2.0, the stop with company**
- The piece torn from the giant: a thrown weapon that coats friend and foe, on short-lived ground, and does not
  keep. (built)
- A wounded giant leaking gelatids. (built)
- The slime pit rendering toxic and indigestible cargo into food. (built)
- The greater gappo's scoop leaving a clean channel behind it. (built in part)
- Return from the last touch, by the archive vat on the deck: a dead crew member grown back as they were when they
  last touched the slime, by expensive Helix technology. (built; his look at what carries over is owed)
- A visible film on the body of whoever carries it. (built)
- The ship's acoustic sounder readings here.

**Later (a crew that stays, a colony, or the campaign)**
- The returned meeting a family that has moved on (*"grief and moving on"*; the old marriage does not resume): the
  rule is his and binds whenever a return happens; a family is a thing a crew that stays grows.
- The seeker naming a tile on the Slime from anywhere in the world (the brief's design; whether it is built is
  `UNMEASURED`).
- Farms that convert back to slime; the farm ruins' ledger.
- The sealed vault in the Slough that only a piece of the giant opens.
- The Throat experiment: *"scoop tons of the living genetic database onto the gravship and pour it down the Glowing
  Throat."*
- The Helix as vendor; the margin-dwellers; the Wildsteam's bend in the road.
- Joining Water, the rite (a second version by his ruling).
- Footprints that linger on warm ground. A whole season of the body, the rain and the herds holding together.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Any mind, intent or communication in the Slime; any content that re-arms it (the piece is his one exception).
- A new triage interface for rescues (his answer, 2026-11-10).
- A remote or bench-made gene dose (the sheet's ban).
- The giant's three pitched stories: the Unfiled Hull, the Return to Sender, the Last Feeding, and the cook's giant
  (not chosen, 2026-10-02).
- Two rites not chosen (the Moving Grave, the Walked-Off Reading); the two hammers and the tamper-proof seal.
- The vanilla zoo; meteorological rain; natural rock.
- The planet-scoring worker and its rarity slider (worldgen is out in every version).
- The glurro and its salve (built 2026-10-03, then cut; nothing of it is in source, and the cleanse records it as
  *"already cut"*). The "Entry recorded" mote and the read-mark smears (cut 2026-10-23).
- The Landing You Cannot Take Back, and with it the contact-point scrub this page's first read proposed (not
  chosen, 2026-10-02).
- GPT's lacquer and its rite of debts (not chosen, 2026-10-02). Slime in the eyes, the Rot-derived antidote and the
  Helix selling blank seekers (*"not in this batch"*, 2026-10-02).
- Patched donor animals: *"We absolutely don't want patched donor stuff in there, we would remake"* (2026-09-24).

## NEEDS HIM

Each is tagged with one theme word.

1. **[hull] Three ship ideas he was offered on 2026-10-02 and did not choose; listed so nobody revives them.** He
   answered that card in his own words: *"Grab a chunk of the giant..."* for the giant and *"An ability to
   resurrect someone..."* for the new marks. Not chosen: **the Landing You Cannot Take Back** (the body reads the
   hull's organic residue; clean the contact points, or take a broker's fee to leave a passenger's gene in the
   archive); **the Unfiled Hull** (a small ship inside the oldest giant, got out by leading it onto dry ground,
   then sold sealed, opened, or stripped for a bio-sealed hold); **the tamper-proof seal** (a lacquer for freight
   crates). The first read asked him the first of these again. This page does not.
   *Waits on the declined-ship-ideas question of 2026-11-19.*
2. **[scope] Is the gene journey the heart of a stop, or an extra?** The cleanse asked this and defaulted to
   "extra". This design defaults to *the heart*: it is his original ask, it is the chosen showcase, and it fits in
   a few days. *An extra:* 0.1.0 is larder, tanks and the film, and the journey waits.
   *Waits on the first-version size question of 2026-11-19.*
5. **[other] His look at the giant.** Card of 2026-10-18: *"Can't judge from this sheet."* The in-game look at the
   smallest and largest sizes is still owed.
   *Waits on his look at the giant in game (not a question) of 2026-11-19.*

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

3. **[scope] The return from the last touch.** *His ruling:* the move card of 2026-11-18 (*"Move it, list every
   move"*): 0.2.0, as the deck part. Still owed: his look at the list of what carries over (asked for on 2026-10-02).
4. **[other] Is a dry room aboard a cure?** No, as built: the cure is days in dry country, or the antidote (the
   design's default). *Delegated call.*
6. **[locked-tree] The locked tree is a colony; this design is a stop.** *His ruling:* his word of 2026-11-18, *"Let's
   rewrite them all and let git be provenance."* Re-cut the tree from this file when the hold lifts.
