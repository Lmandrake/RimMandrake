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
it dry."* A crew with a hull does not walk. For desert people the way out of the Slime is to go home.

His answers of 2026-11-10 keep it plain: no new rescue interface (*"We make it work in their existing ui... If you
want to be nice just send a message at a certain critical moment of how much time left"*); the returned dead meet
*"grief and moving on"*; and the weapon made from the giant makes its victims *"struggle now"*, nearby allies
included.

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
  does not. The ordinary health display shows the course; there is no special screen.
- **The larder and the tanks.** Cooked slime is *"disgusting but fully edible."* When the body is thirsty it *"sweats
  into the sky and pulls down a warm green rain that fills every barrel"*, drinkable, standing briefly on bare
  ground and draining back.
- **Stone is pressed, not quarried.** A compressor turns ooze into block. *"Construction here means eating the
  database."*
- **The cure that starts a clock.** Raw slime *"instantly cures any poison in you, and most radiation"*, and then it
  starts on the one who swallowed it. For a crew fresh from the Cauldron this is the best offer on the planet and
  the worst.
- **The antidote.** A deliberately toxic injection ends the Slime's hold. It hurts. A friend can give it.
- **The neighbours.** Gelatid herds that *"pool together at night"*; the scoop-mouthed gappo, small, middling and
  huge; the dwommo floating over all of it; the iron-crusted glurro in the channels; the fubbum, the one hunter,
  which *"never hunts a pawn first."* None of them minds the crew. Some of the animals that wander in from next door
  are part-read already and do not seem to have noticed.

## The first week

- **The gene.** Pick one from the archive of *"everything that ever touched it"*. A handheld seeker finds where on
  the map the current carrying it will pass. Walk out there, onto the open body, and draw it. The dose spoils, so
  there is no doing this from the ship. Inject. *Coma.* Then the race: the reading runs fast in a comatose body,
  and unless a friend reaches them with the antidote in time there is nothing left to bury. Whoever wakes has the
  gene they wanted, one they did not choose, and a mark other people can see. The accepted gene lists (2026-09-06)
  price all of it where this crew lives: *"costs land where Jawas live — haggling, sneaking, scavenging,
  tinkering, warren life. A gene should make a Jawa argue with themselves."* And *"the marked are hard to love"*,
  which matters in a clan whose whole future is who will lie down with whom.
- **The giant.** A Titanoslime *"hunts by rolling over things."* It swallows prey whole, crew included, and what it
  holds can be got out again while there is time, and the time is shown. What it eats makes it permanently bigger.
- **The ruins.** *"Fence lines and dead irrigation sinking into slime-grass, every ruin a legible story of someone
  who thought they'd beaten the conversion rate."* Other people's abandoned gear, half absorbed.
- **The ledger.** By the end of a week, anyone who has been careless with bare ground is past the stage where
  stepping off it helps. They need the antidote, or they need the desert.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The gene run.** *On screen:* one Jawa far out on the shining flat with a seeker, a needle, a pause, and then
   flat on its back; and four more Jawa leaving the ramp at a dead run with the antidote, across ground that is far
   slower to cross than it looks. *Why it lands:* the clock is on screen and the ground is slow.
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
9. **The piece (0.2.0).** *On screen:* a chunk torn off the giant and thrown; everyone it lands on, and everyone
   standing next to them, is at once coated and struggling. His words: *"a terrible bomb like weapon... Bioweapon
   after all."* A Jawa threw it. A Jawa is standing next to them.

## When the Empire arrives

It arrives on time. Nothing here hides the ship.

- **Everyone wades.** The soft ground slows troopers as it slows the crew. A crew on planks is the only thing on
  the map that moves at speed.
- **The body reads them too.** Contact films any unprotected flesh. A week is longer than a raid lasts, so this
  matters to a siege and not to a strike. `UNMEASURED`: whether Imperial armour counts as protection.
- **The hill does not take sides.** A Titanoslime rolls over whatever is in its way, by reflex and never by
  intent. A cordon's emplacement is in its way if the crew can arrange that.
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
- **Resistance,** the same way: the Slime-resistant gene is in the archive like any other.
- **Pressed block,** stone from a place with no stone.
- **The antitoxin trick,** for as long as there is antidote to follow it with.
- **Rendered cargo (0.2.0):** the slime pit makes safe food of the toxic and the indigestible, which is what the
  hold is full of after the Cauldron and the Rot.
- **Fuel:** emergency-slow only. The body is biomass to the horizon and renders to fuel no faster than anything
  else does. The Helix and the margin-dwellers are the only people who might sell any, and both are campaign-layer
  traders not built into the biome.
- **Not the piece.** Off the body it shrinks; it *"never stockpiles."*
- **The film,** if they were careless, until the desert dries it out.

## What the place does to the ship

The review of 2026-10-02 says it in so many words: the Slime *"does nothing to your ship."* It reads flesh, and a
hull is not flesh. One pitch from that review was about the ship and he did not choose it, before he had stated the
ship lens: *"The Landing You Cannot Take Back: landing on the body exposes the hull's organic residue to reading;
clean the contact points..."*

His ruling of 2026-11-18 puts what each biome does to the hull in 0.1.0 and says the sources mostly have it. Here
they do not. This design's default, flagged as new and asked below: the hull is untouched, and the wear is at the
**contact points**, the gear and the ramp, where the body climbs whatever organic the crew has tracked there. It is
scrubbed off by hand before launch, or it rides along and keeps filming whoever uses the ramp until the ship
reaches dry country. Hands-on work, no armour, and very little to build.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A living plain: buildable crust, slow soft ground, moving liquid channels, no rock anywhere, soft-bodied life. | A fresh map at ordinary zoom. | A quarry, or a vanilla animal standing in for a native, fails. |
| Bare contact films unprotected flesh; the ordinary health display shows the course; early film recedes off the slime and late film does not. | Three pawns: one on planks, one on bare slime briefly, one for days; then all moved to a floor. | A roof with a slime floor does not protect. |
| Left alone the course ends in dissolution, and the victim's belongings remain. | One pawn left to the end. | Gear that vanishes with the body fails. |
| Leaving for dry country, or a completed antidote treatment, ends the hold. | One late-stage pawn flown to desert, one treated. | The antidote is toxic and shows it. |
| Slime gives food, block and poison relief by ordinary work, and raw slime's cure starts the film. | A cooked meal eaten, a block pressed, a poisoned pawn fed raw slime. | A free cure with no film fails. |
| Organism rain leaves drinkable standing water on bare ground, none on floors or under roofs, and drains away. | One rain over mixed ground with barrels out. | Water that stays, or that cannot be drunk, fails. |
| A chosen gene is found with the seeker, drawn in the open on the body, and spoils if not used. | The journey start to finish; one dose left to spoil. | A dose made at a bench or handed over by a helper is not the journey. |
| The injection brings a coma and a race; a friend's antidote in time saves the patient; there is a message when little time is left. | One rescued, one not. | No new interface: the game's own, plus the one message. |
| The survivor keeps the chosen gene, an unchosen one, and a mark others react to; it passes to offspring. | The rescued pawn, afterwards and a generation on. | A journey with no cost fails. |
| The natives live as an ecology (herds that pool at night, three sizes of scoop-feeder, a real flier, a hunter of the herds); outsiders arrive part-read; nothing turns hostile from being read. | A week of the map left alone. | Flight is read from state, never watched unattended. |
| The giant swallows prey whole, shows how long a rescue has, gives up the same person if freed in time, and keeps what it gains from feeding. | A crew member engulfed and cut free; an animal engulfed and digested; a save and reload after. | A giant that shrinks again unseen fails. |
| The contact points of a landed ship gather slime, and it can be scrubbed off. | A ship through several days, gear cleaned and uncleaned. | New in this design; see `NEEDS HIM`. |

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
- The native ecology: gelatid, the gappo family, dwommo, glurro, fubbum; part-read visitors; nothing made hostile.
  (built; several still wear stand-in art)
- The Titanoslime: engulfing, visible rescue time, permanent growth. (built; his look at its art is owed)
- The farm ruins as places. (built)
- Slime on the ship's contact points, scrubbed by hand. (new in this design; unbuilt; `NEEDS HIM`)

**0.2.0, the stop with company**
- The piece torn from the giant: a thrown weapon that coats friend and foe, on short-lived ground, and does not
  keep. (built)
- A wounded giant leaking gelatids. (built)
- The slime pit rendering toxic and indigestible cargo into food. (built)
- The greater gappo's scoop leaving a clean channel behind it. The glurro's salve, which slows the reading. (built
  in part)
- A visible film on the body of whoever carries it. (built)
- The ship's acoustic sounder readings here.

**Later (a crew that stays, a colony, or the campaign)**
- Return from the last touch: a dead person grown back as they were when they last touched the slime, by expensive
  Helix technology, to a family that has moved on.
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

## NEEDS HIM

1. **What does the Slime do to the ship?** The sources say nothing, and the one ship pitch was not chosen on
   2026-10-02. *Slime gathers at the contact points and is scrubbed off, or rides along* (default, new, small).
   *Nothing:* the Slime is the one biome that leaves the hull alone, and says so. *The Landing You Cannot Take Back
   in full:* a Helix broker pays to leave a passenger's sample open to the body, and a rival later turns up wearing
   that gene; a quest, not hull wear.
2. **Is the gene journey the heart of a stop, or an extra?** The cleanse asked this and defaulted to "extra". This
   design defaults to *the heart*: it is his original ask, it is the chosen showcase, and it fits in a day. *An
   extra:* 0.1.0 is larder, tanks and the film, and the journey waits.
3. **Does flying to dry country cure as walking does?** The law says drying biomes halt slimification. *Yes, the
   ship is the cure* (default). *Only time spent on dry ground counts, not the flight.* *The antidote only, for a
   ship's crew:* the stop is then limited by doses carried.
4. **The locked tree is a colony; this design is a stop.** *Re-cut the tree from this file when the hold lifts*
   (default). *Keep the tree and treat this as a second reading.*
