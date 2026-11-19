# The Webwork: the design, seen from the ship

**Status:** the one design document for the Webwork biome (`RM_Webwork`, source `src/RimMandrake/Webwork/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the
frozen definition sheet, the owner-and-nest sitting record, the egg black-market draft, the two rosters, the
bedazzle review, the kit spec and the cleanse proposal as the place to read; what happened to every idea in them is
in `design/concepts/Webwork/rewrite_choices.md`. Nothing has been deleted yet. This is a design document only and it
launches nothing.

**Second reader, 2026-11-18:** a different agent read the sources the first pass had read in part and repaired this
page; what changed, and why, is at the top of `rewrite_choices.md`. The largest repairs: the place is hot, and that
heat is a built wear on the hull; convergence, the droid preference and the web's mark are not built; and the look
of the ollathrix, the three ways into a nest and the debris-pile ambush are now in the design.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/Webwork/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Webwork has no locked sheet or tree; its only pipeline material is the
cleanse proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) or the special-mechanics review of 2026-10-22 found it in source; it
does not mean it has passed anything. That review found every recorded Webwork run was a mock. Later live runs
exist: on 2026-11-06 the traction lance passed, the remains and the silk harvest were partial and the siege
failed (`designer_codex_2026-11-09/Webwork/NOTES.md`).

**Names.** The owner species is the **ollathrix**, an invented spider of ours (his pick, 2026-09-23). When the
campaign layer is active it wears the canon Wyyyschokk's skin and its silk is called Shokkweave (the older
bestiary animal `RSW_Wyyyschokk` gets a new label, so only one creature carries the name; `Answered on 2026-11-19`
6); in the free biome
the silk is **thrixweave**. This document uses the free names. One ollathrix, three ollathrix. Everything here was
invented first, on his instruction of 2026-09-23: *"we should just invent our own complete roster of fauna, flora,
etc. that make it a rich place THEN look for Star Wars specific injection opportunistically."*

---

## What this place is

> *"A green and white hellscape, silent, owned, and growing."* (`the_webwork.md`, header)

A jungle with no river on the map, because the plants *"drank their entire river"*: *"the water is inside."* Above
it a sealed canopy; under it a dim green gloom threaded with white silk, laid *"through the entire ecosystem"* by
the things that own it. *"This is not an infested jungle. It is a plantation, and every living thing in it is stock
in the owner's ledger."*

> *"So quiet that you know you're in terrible danger. It makes treasure, it eats all, and it's coming for you."*
> (owner, typed, 2026-10-20: the experience line)

It is the Greentide turned inside out. The Greentide is loud and lawless; here *"the quiet is not peace, it is
ownership."* *"The Greentide's silence-before-the-predator is the Webwork's permanent state."* There is no truce
to be had: *"you are not a fellow drinker, you are prey in someone's ledger."* (His "it eats all" has two
readings in the sources, the canopy swallowing clearings and the owners having eaten the wildlife; both are true
here, and the 2026-11-17 cleanse took the second.) *"Most of the animals have been eaten, and few will enter. Those who do frequently discover a shadow,
seconds before it lands upon them, and know nothing more."*

One law runs the whole place: *"the entire biome is a single organism of shadow."* The owners are as big as an
elephant on *"too many sharp legs"* and they are **helpless in direct sunlight**. *"Direct sunlight is lethal to
the owners; clearings are the only safe ground."* The sheet's summary of how to live here is five words: *"a
clearing is the fortress."* A later item says the same thing in eleven words: *"the Webwork is the one place on
the planet where the hungry sun protects you."*

The sun protects and it also cooks. This is an extreme-heat biome (the old sheet measured 38.6, 49.2 and 58.2 °C
at its tenth, middle and ninetieth tile, under an overhead sun), and the bedazzle review drew the consequence:
*"the sunlit clearing that keeps the owners out is also where colonists overheat, while the canopy that is cool is
never safe."*

**Seen from the ship, the owner has already said what happens.** His card answer of 2026-10-22: *"Landing a ship
into a webwork will surely get a response it's only quiet if you walk into it."* The crew does not get the hush.
It gets the answer.

And this is the one place on the planet where the things the crew values most are a liability. The sheet: *"They
HATE droids and preferentially destroy them. The why stays unexplained — it is scarier as a fact of the place ...
the one terrain where a droid force is a liability."* Jawa are droid people.

The crew are small, hooded, skittish and built for dry heat (`reconciled_lore/05_the_clan.md`). The one thing in
the Webwork that is on their side is the sun they grew up under.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28: *"around every 5-8 days, keep 'em running"*; ladder in
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked provisional): a probe
droid five to eight days after landing, then scouts with a spotter, a strike team, an ion cordon on the ship, a
breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if the one before
succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last: about six weeks under the canopy's edge, about a month in the open, and those are
the outer edge** (his ruling of 2026-11-18: the numbers are *"the outer edge allowable for each biome"*). On open
ground the ladder's arithmetic gives a probe on day 5 to 8, a first real fight around day 12 to 20 and the
bombardment around day 20 to 32 if the Empire wins every step; canopy slows the search by one step. Almost no stop
here will run that long. The Webwork's own clock is faster than the Empire's: the answer to a landing comes inside
the first hour, and from then on the stop lasts as long as the crew can keep its ground in sunlight.

**Cover from orbit (his ruling of 2026-11-18: partial cover, by biome): the canopy, one step, and it is the worst
bargain on the planet.** The sealed canopy that hides a ship from above is the shade the owners hunt in. A ship in
a sunlit clearing is safe from them and plain to the sky, and it stands in the heat. A ship tucked under the
canopy's edge has its step of cover, is cool, and has parked inside the web. Where to land is the whole decision,
and neither answer is free. The canopy is one plant's work: the dulloth, whose leaves are *"the size of doors"*,
in his art note *"like lilly pads grown straight up out of the ground above you to the scale of a tree."* *"From
below it is a ceiling; from above, a sealed floor of dark green."* That floor is what the ship comes down through.

**Fuel (his ruling of 2026-11-18).** A **richer source**, named in the sheet: the still-tree. *"The
still-burners — the Wildsteam's belching flame weapons, fueled by liquors and oils tapped from the trees and
fermented in their stills: one fuel item that is also a drink and a trade good."* The tree is built (the tavrosk,
*"a squat tree that is mostly trunk ... it looks kept, like a barrel someone owns"*); tapping it and fermenting
the sap is built as far as the drink (the tree is harvested for tavrosk liquor today); burning that liquor as
fuel is not, and is the small build for 0.2.0. The emergency route has good feedstock too: this is a jungle, and
its margin scrub, the brennoth, *"looks like kindling because it is."* Fuel can be **bought** from the Wildsteam,
who are at war on this biome's far side and *"pay for mandibles"*; a crew with fresh mandibles has the one
currency they want. Campaign layer.

**What the place does to the ship (his ruling of 2026-11-18, in 0.1.0).** Two things, one for each place a ship
can stand.

*In the clearing, the sun.* This wear is built. The frame his ruling points at (`src/RimUtinni/ShipShields/`, his
shield rulings of 2026-09-02) wears an unshielded ship's structures whenever the air outside is 58 °C or hotter
(`ShieldHazardUtility.HasHeatHazard`): a few parts at a time, faster after about six hours, with letters that
advise and never refuse. The old sheet's hottest tenth of Webwork tiles reach that; which tiles do after the
planet is painted is `UNMEASURED`. The answer is the thermal veil, in his words a field that *"would reflect all
external heat outward with a mild mirror sheen to the shield, but also reflect all internal heat inward, so the
temperature slowly climbs anyway."* A mirrored ship in a sunlit gap is safe from the owners and is the brightest
thing the search could ask for.

*At the canopy's edge, the silk.* It is spun in. The built siege work already has living spiders spinning silk
toward a target from shaded cells, and **wrapping doors**: a wrapped door will not open until the wrap is cut or
burned off. On a Webwork map that work is aimed at the ship. Every hour the hull sits within reach of shade, there
is more silk on it, across its ramp and over its doors, and silk laid across open ground is shade for the next
spider. The answers are hands-on and the sheet names them: **blades and fire** (*"only fire provides the kind of
protection and offense needed to drive them back"*), and **sunlight**: a hull standing in a kept clearing cannot
be reached at all. *This half is the first pass's proposal.* The spinning and door-wrapping run today only in the
siege incident on a neighbouring tile; pointing them at a landed ship on the home map is a build, and no source
asks for it. (A third, stranger wear is in the sources and was not chosen in October: roots that thread the ship's
doorframes. See `NEEDS HIM` 1.)

---

## The first minutes

A foot party would hear *"drip, silk-creak, and the listener's own steps"*: *"the quietest green place on the
planet."* The ship gets none of that. It comes down through the canopy or into a gap in it, and the web feels it:
*"touching it anywhere is being felt everywhere nearby."* A fresh contact thrums along the cables.

Then nothing, for long enough to lower the ramp.

Cables as thick as a leg span between braided trunks. Finer strands hang across the easy ways through. This is
his picture (2026-10-12): *"it should still look like a jungle with web shit through it. Thick powerful cables
running through are the main portions with thinner local webs and the finer carpet where the spiders have 'sites'
they use."* The trunks are kollavane, each *"a standing braid of dozens ... visibly several ages at once."* Pale
flowers stand *"in runs and arcs that trace the web"*, faintly glowing, *"like a graveyard's flowers"*. There is
no birdsong, no insect noise, nothing running away. A crew used to the desert's emptiness may take a minute to
understand that this emptiness was made.

At the edge of the gap the ship tore, where the sun reaches the ground, something stops. It is as big as an
elephant, it is all legs, and it does not come into the light. It is *"bone-white to dead-silk cream"*: *"a white
spider in a green gloom is the 'green and white hellscape' made animal."* It has *"one pale ring of small
colourless eyes around a raised head-boss"* and *"reads blind"*, because it hunts by feel. It stays where it is.
Others arrive beside it.

Before the first hour is out the player should have seen three things without going looking: the web answer the
landing; an ollathrix come to the edge of sunlight and hold there; and the shade line itself, as the most
important line on the map. He asked for that line to be readable (2026-10-12): *"Big shade patches. A bright
sunlit regions should shine and be clearly visible."*

## The first day

- **Sunlight is the wall.** The ollathrix is crippled in direct sun and will not choose a path across it, not
  even in a rage. Shade is theirs: canopy, roofs, the ship's own shadow, an overcast sky. Lamps do not count; the
  owner's words of 2026-09-11: *"There is no night here, and no light a player can make has the effect of this
  planet's terrible sun."* By his card the same day the sun cripples and never downs: a caught spider crawls for
  shade and is not a free kill. What the wall does not stop: spit from a shaded edge within range, a spider
  already inside, fire, and the heat. The margin is the dangerous place: keeping it open means working among the
  cables in it, every touch marks the worker, and the owners come to the nearest shade, *"which is exactly where
  the workers stand."* The cleanse's reviewer put the whole refuge on one comparison: spit range against the width
  of the cleared margin. A ship's clearing has to be wider than a spit.
- **The clearing has to be made and kept.** *"Cut the canopy, burn a ring, keep it burned."* The margin scrub
  burns hot and clean. *"Fire is architecture, not just weaponry."* The threats to a clearing are *"regrowth ...
  overcast skies, and an untrimmed margin"*: *"the moat maintains itself only as long as you do."*
- **The web is a floor plan and an alarm.** Thick cables slow a walker. Fine strands cross the easy ways
  through and are the ones a careless walker touches. Silk carpet marks where the owners live. Cutting any of it is felt.
- **Being caught.** The ollathrix spits from the mouth at range, and what it spits does not wound: it binds. A
  bound crew member is nearly helpless *"for days unless attended medically. Not damage — helplessness. The spider
  comes back."* What comes back has mandibles that *"crush a human head in a single bite."*
- **They come together.** One contact brings the others over whatever shaded ground connects them. The owner's
  answer of 2026-11-10: *"The existing ollathrix are enough. Ordinary elephant-wide spiders hunting together ...
  coordination must be convincing."*
- **Water.** There is none on the ground. The brimlock is *"a leaning trunk swollen into a drum-tight bladder"*
  that *"audibly sloshes when struck. Cut one and water runs out."* The roster adds a price: the spill *"draws
  churn regrowth to the cut"*, so drinking closes the clearing (whether that pulse is built is `UNMEASURED`).
- **The ground is pipework.** The root mat underfoot is the threllick, the stolen river's plumbing: *"you are
  walking on pipework"*, and it is why walking is slow.
- **The piles.** A dormant ollathrix hides under what his ruling of 2026-09-11 calls *"a small debris pile"*,
  *"built out of the local environment"*. *"Too clever..."* The counterplay is the kit's: *"shoot the suspicious
  pile or eat the ambush."*
- **An overcast day is ordinary weather.** This jungle's weather table has rain, fog and thunderstorms. Each one
  is the wall coming down.
- **Food.** Fellome pods hang in strings along the web-lines where the pollen-dusted owners pass: good calories,
  everywhere, free, and every string of them is beside a line.
- **The droids stay aboard.** Anything mechanical that walks out under the canopy is the first thing attacked.

## The first week

- **The silk is the treasure.** Thrixweave is the finest cloth there is and by ruling it comes from nowhere else:
  *"the ONLY way to obtain it in the game."* It is cut from the web itself, *"which rings the line you cut"*;
  taken in small amounts from a kill; and taken from a nest. Burning a web, fighting on it or letting the beetles
  chew it yields nothing: only deliberate, risky cutting pays, and by his ruling of 2026-09-11 a cut has *"a small
  chance of SPAWNING"* a spider *"to get you"* (built; the cleanse moves it off, this design keeps it because the
  words are his). Cut web is never rebuilt: *"regrowing trees restore shade, not silk."*
- **The beetles.** Quarrok are great insects that *"hate them instinctively"* and chew through web anchors,
  *"neutral, unbothered"*. Where they have been, the web is cut and blind.
- **The mites.** Vennick are fist-sized, run the silk, and eat eggs. They are harmless, *"which makes a mite trail
  a living treasure map to a nest."* *"Never alone: vennick read as a current, not as animals."* The roster's
  summary of the two: *"the player's two instruments against the owner are both animals used well."*
- **The evidence.** A cravvet *"parked on a stain means a fresh kill site."* A skennet is *"built for one sprint
  it will eventually lose."* The sivvern is *"the only thing in the sky."*
- **The nest.** One on every map, by his card of 2026-09-24: woven *"from great masses of young trees and the
  rotting hides of victims"*, ringed with rust-red blooms that grow only on hide-rot, silk in its walls, clutches
  inside, guardians waking when it is touched. A living nest lays again in twenty to thirty days. Its parts: the
  clutches, each *"a pale mass of leathery eggs packed in silk"*; the silk walls; the hide mass, *"the only warm
  colour in the biome"* (*"a nest is where the missing went"*); and the mother beside the clutch, *"the one place
  a guaranteed Ollathrix sits — every other one on the map is a roll."* Wounding a guardian is its own alarm:
  the nest's defenders turn out to attack whoever did it and stand down only after a quiet spell.
- **Three ways in.** Follow the mites, free and slow, and *"arrive felt"*. Burn a corridor, which is unfelt and is
  also *"a light-moat pointing at the nest, so every Ollathrix on the map converges on the fire."* Or lure the
  beetles along a route for *"the only silent approach"* (0.2.0). What comes out, in order of worth: eggs, wall
  silk, the mother's mandibles and fangs, and the dead's gear, *"the consolation take"* (later).
- **The eggs.** *"The smuggler's jackpot, priced in risk."* An egg in a crew member's hands marks them to every
  web they pass. Set on a shelf aboard, it is quiet. *"Drop the eggs and the web loses you within a day; keep them
  and it never does."* Off the Webwork nothing hears them at all: *"the mark is not a curse; it is a signal only
  web can hear."* The eggs spoil in about fifteen days (*"a countdown to a buyer — it is smuggling, not
  hoarding"*), and they never hatch: *"a hatching egg is a tamed Ollathrix by the back door."* With no campaign
  loaded the buyer is any orbital trader: *"sell them to the sky."*
- **The run home.** His answer of 2026-11-10: *"A prepared escape route is essential. Clearing and guarding the
  return path matters; improvised retreat is unreliable once noticed."* The stop's whole plan is a sunlit path
  from the nest to the ramp, cut and burned before anyone touches a clutch.
- **Webfall.** Now and then silk drifts down out of a clear sky without dimming the sun. His words: *"Webfall
  weather is cool."*
- **The green comes back.** The thicket *"churns against itself"*; a clearing nobody tends closes. Every day of
  regrowth is shade creeping toward the ramp.
- **What it was worth.** His answer of 2026-11-10: *"A major windfall: surviving the jungle should finance
  substantial progress and earn a memorable reward for serious danger."*

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The answer.** *On screen:* the ship is down for a minute and the cables around the landing are shivering.
   *Why it is alarming:* nothing has moved yet.
2. **The line.** *On screen:* three animals each the size of an elephant standing in a row exactly where the
   shade stops, facing the ship, perfectly still, at noon. *Why it lands:* a cloud is coming.
3. **The cloud.** *On screen:* the sky goes overcast, the shade line is suddenly everywhere, and the row walks
   forward.
4. **The spit.** *On screen:* a strand from a mouth in the undergrowth, and a Jawa stuck fast in the open, alive,
   unhurt and unable to move, while another runs out into the sun to cut it free before the shade moves.
5. **The droid.** *On screen:* the crew's hauling droid rolls ten cells under the canopy and every ollathrix in
   reach turns from what it was doing. *Why it is funny, once:* the crew sends a broken one in next, on purpose,
   as bait.
6. **The treasure map.** *On screen:* a stream of fist-sized mites running a silk line in single file, and a
   line of Jawa following it at what they believe is a safe distance.
7. **The egg carrier.** *On screen:* one Jawa running down a burned corridor of sunlight with an egg the size of
   its own torso, and the web on both sides of the corridor thrumming along with it, cable by cable.
8. **The beetles' work.** *On screen:* a file of quarrok chewing through anchors, a whole span of web sagging
   and falling, and a way through that was not there an hour ago.
9. **The door.** *On screen:* morning; the ship's ramp door is under a white wrap of silk and the crew is
   inside. Somebody finds the cutting torch.
10. **The brimlock.** *On screen:* a thirsty crew member puts a blade into a swollen trunk and gets a face full
    of someone's river.
11. **The suspicious pile.** *On screen:* a heap of leaf litter and sticks beside the path that is slightly too
    tidy. One Jawa points at it. Another shoots it. It stands up.
12. **The wrong corridor.** *On screen:* the crew burns a clean sunlit lane straight to the nest and every white
    shape on the map starts walking toward the smoke.

## When the Empire arrives

The sheet gives the benchmark itself: the ollathrix's legs are *"known to cut through a Stormtrooper's leg armor in
a single slash."*

- **The web feels them too.** A team that walks in under the canopy has announced itself to everything on the
  map. The owners are *"enemy of all, ally to none."*
- **The probe is a droid.** The first thing the Empire sends is exactly what the owners hate most. An Imperial
  probe counts as a droid the web eats (delegated call of 2026-11-19, `Answered on 2026-11-19` 2): a probe that
  goes under the canopy does not report. The later search steps still come. It is the single strongest thing this
  biome does for a crew. (`UNMEASURED`: whether the built droid preference recognises an Imperial probe today; one
  check, and a fix if it does not.)
- **Their camp is in the shade or in the open.** Under the trees it is in the web. In the crew's clearing it is
  in the crew's field of fire.
- **A bound trooper is somebody's dinner.** Whoever is spat on and left is collected.
- **The crew's corridor works for the crew.** The cut and burned paths are known to the people who made them.
- *0.2.0:* **the traction lance,** a crewed tether emplacement learned from a junction cut out of the web's own
  plumbing, which reels a target in along the ground: a downed crew member out of danger, or, in the words of the idea he
  chose, *"an ollathrix out into the sun"*.
- *0.2.0:* **cocoons.** Downed people in the shade are wrapped and have a clock on them: a day, by his card of
  2026-10-22. That goes for both sides.

## Who else attacks; who hates the Empire

- **The ollathrix,** and nothing else worth the name. *"They are their own main predator as well as everything
  else's"*: *"turning on each other as swiftly as they cooperate."* The infighting is the only reason they have
  not won.
- **The plants are on the owner's side (0.2.0).** A snap-jawed trap at knee height; a wand that flings glassy
  needles; a dark bell whose scent draws animals to where the web is thickest.
- **The beetles and the mites** are at war with the owners and indifferent to everyone else. They are the nearest
  thing to allies here and they do not know the crew exists.
- **The Wildsteam** *"are at war here"*, on the far side, with flame weapons and a standing bounty on mandibles.
  Campaign layer. Whether they fight the Empire is `UNSETTLED`; they certainly fight the thing the Empire will
  meet first.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- An overcast day.
- Sickness: the sheet keeps *"a heavy disease load in the canopy air"* (malaria, sleeping sickness, plague).
- Regrowth and silk closing the clearing faster than a small crew can cut and burn.
- The ship's doors wrapped, and nobody left outside to cut them free.
- Crew bound and waiting on medicine while the shade line moves.
- Carrying eggs: the longer a clutch is in hands, the more of the web knows.

**Stay, longer than the Empire would like:**
- A kept clearing in full sun. The owners *"physically cannot cross open sunlit ground."*
- The canopy's step of cover, for a crew willing to live at the edge of it.
- Everything the Empire sends on foot or on repulsors having to cross the web to arrive.
- Fire.

The honest summary is the owner's line: *"it's coming for you."* The Webwork is a heist. The crew lands, takes the
silk and a clutch down a path it prepared, and lifts with the web still ringing.

## What the crew takes away

- **Thrixweave.** Nothing else on the planet makes it, and by his card of 2026-10-22 the rare traders who resell it
  do so *"at a steep price"*.
- **Eggs,** if they are sold before they spoil. In the free biome they are simply very valuable; the campaign adds
  who buys them.
- **Mandibles,** which the Wildsteam pay for, and **fangs.** His words of 2026-09-13: *"Wyyyschokk fangs on a
  tribal pendant showing the bravery of the person. These should have social consequences for being worn by
  implying the person is quite brave (with those factions), and be a trade good elsewhere on planet regardless."*
  (Campaign layer; the item is open.)
- **Tavrosk liquor,** a drink and a trade good today.
- **Fuel** from the still-trees (0.2.0), and water from the brimlocks.
- **The knowledge that sunlight is a wall,** which is worth something at the next green place.
- *0.2.0:* **the traction lance,** the Webwork's named gift to the ship: *"a crewed tether emplacement that reels
  a target or a downed colonist in."* His words when it was ruled: *"That traction lance was just suggested in
  another biome too. So now there are two places to get it from I guess. Lasso relative."*
- *0.2.0, and the campaign's:* a buyer. *"Totally add the black market trader (likely hutt / bounty hunter faction
  related) and some quests that have [optional immoral] solutions to [assassinate] someone by planting an egg in
  their room to hatch in the night."* (His typed words of 2026-09-24, with his typing slips mended inside the
  brackets.)

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A ship landing on a living Webwork draws the owners within the hour; a party that walks in quietly does not, until it touches the web. | Land a ship; on another run, walk a party in and stand still. | A map whose owners and nest have been destroyed stays quiet when a ship lands: nothing is resurrected. A letter alone is not a response; a spider must change what it is doing. |
| The jungle is audibly quiet: steps, drip, silk, and a thrum on contact. | A listening check at a staged save, at a joint sitting. | The same save with an ordinary rainforest chorus added must fail the check. |
| An ollathrix will not choose to cross direct sunlight, and one caught in it is crippled and goes for shade. | A spider at a shade line with prey in the sun, at noon: hunting, following a mark, idling, in a rage, and as a nest guardian turned out to attack. | Roof the gap, or let it cloud over: it crosses. A lamp changes nothing. A spider already in the sun crosses it only toward shade. |
| One contact brings others, over shaded ground that connects them. | Touch a strand at one end of the map with spiders at the other, with and without a continuous shaded way between. | Their positions and paths show convergence; a queue of spiders stuck at a sunlit gap is the control and must not be counted as converging. |
| The spit binds without wounding, lasts days untended, and medicine ends it. | One bound pawn tended, one left. | The bound pawn has a named condition and can be rescued; nobody is deleted. |
| A kept clearing holds; an untended one closes, by regrowth and by silk. | Two clearings beside the ship, one burned and trimmed, one left, over the days of a stop. | Real trees and real weather, not a roof standing in for canopy. |
| Deliberate cutting of web yields thrixweave and rings the line; burning, fighting and beetles yield none; no trader sells it but the rare reseller. | Cut, burn and let beetles chew three like spans; inspect generated trader stock. | The check is on stock a live trader actually generated, not on the XML. |
| The nest is a place: marked by its blooms, guarded, with clutches that can be cut out; it lays again while any owner lives. | Follow the signs to the nest, raid it, wait. | Its guardians are finite: the wall does not replace the fallen (owed: today it does). Save and reload mid-raid. |
| A carried egg marks the carrier to the web; a shelved one does not; dropping it does not end the hunt at once. | Carry a clutch down a corridor; shelve it aboard; on another run, drop it. | The egg spoils on schedule and never hatches. |
| Droids are attacked first, among prey equally in reach. | A droid and a person enter the shade together, the same distance from a hunter. | With the preference switched off they are treated alike. A droid standing in sunlight is not preferred over a person in shade. |
| Quarrok chew anchors and the web they cut stops feeling; vennick run the silk toward eggs. | Watch a beetle file and a mite stream on a map with a nest. | A cut span no longer alarms when touched. The mites' line ends at a clutch. |
| Spiders spin toward a ship within reach of shade and wrap its doors; a wrap is cut or burned off; a ship in a kept clearing is not reached. | One ship at the canopy's edge, one in open sun, over the days of a stop. | The silk appears only where a living spider worked, with the work visible first. |

Settings: one switch per major feature, defaults as shipped, everything off leaves a quiet, dim, heavily webbed
jungle with large animals in it (standing rule, every mod).

## Shared machinery

**Featured here** (the Webwork is where each is vital and should be proven):
- **Sunlight as a wall for a creature** (the sun-scald, keyed to the shared tree-shade grid; the same one sun from
  geometry as everywhere, with real tree shade counted, by his ruling of 2026-10-19 and the shade model of the
  same date). The Webwork is the tree-shade model's hardest customer: here shade is where the enemy can stand.
- **A structure that feels touches and calls its owners** (the sense web and the convergence job, in
  `CreatureBehaviors`).
- **A condition that immobilises without wounding** (the binding spit).
- **Things carried that mark the carrier** (the egg mark).
- **Animals that undo a hazard as they go** (the quarrok's anchor-chewing; the Greentide's grazers are the same
  idea against growth).
- **Growth that takes back cleared ground** (`ExplosiveGrowth`, which the Greentide also features; here it closes
  a defence instead of a doorway).

**The one hard dependency.** By his Direct Sun ruling the sun is switched off on tree-heavy maps unless the
tree-shade model is excellent, and the Webwork is the most tree-heavy map there is. The cleanse says it plainly:
*"If tree-shade calibration fails, this signature is not demonstrated: do not pass by replacing trees with
roofs."* Sunlight as a wall, the landing bargain and promise 3 all wait on that model.

**Merely active here:** the tether pull (shared with the Sump's capstan, one implementation by his ruling); wet
native growth holding the water inside; fire and wind; darkness and canopy as cover from the Empire's search; the
door-wrap and cocoon work (built for the siege); real flight (the sivvern); plants that block sight and plants that
act (`HostileFlora`, `CreatureBehaviors`); the huge-things engine (for the giant's remains and the battle he asked
for); the ship's acoustic scanner; the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket.

**0.1.0, the stop**
- The land: sealed canopy and gloom, water held inside the plants, cables, strands, carpet at spider sites,
  ordinary weather, webfall. (built)
- The hush. (not built as sound; owed)
- The ship's landing answered. (the response is specified; the adapter from a landing to the web is an owed
  ticket)
- The ollathrix as it is: one race, one kind; dormant ambushers with a visible tell; spit, mandibles, venom;
  convergence; sunlight as its wall, counted through real tree shade. (The body, the spit, the dormant ambush
  and the sun-scald are built. Convergence is not: the census of 2026-11-17 found the hunter's convergence,
  coordinated pursuit and the debris-pile burst absent from the ordinary animal's wiring. The web's mark and
  thrum are silently off, because the code looks up two definitions that no longer exist.)
- Droids attacked first, among prey the owners can equally reach; sunlight and unreachability still win. (the
  preference is specified and its implementation is an owed ticket; the free biome names no Star Wars machine, so
  what counts as a droid is supplied by the campaign layer)
- The clearing and what threatens it: felling, burning, regrowth, overcast. (built from shared parts; whether a
  small crew can afford to keep one is the cleanse's open measurement)
- Thrixweave as the sole source, by cutting, butchery and the nest; rare steep resale. (built; the live trader
  check has never run)
- The nest, its blooms, its finite guardians, its clutches, re-laying. (The nest, guardians, clutches and
  re-laying are built; the placing can give up and leave a map with no nest. The guardians are not finite yet:
  the wall replaces its dead for as long as it stands, so a raid cannot be won by attrition today. Mining a
  clutch rings nothing, because the clutch is not on the web's sense. The rust-red ring and the flowers
  that follow the web are not placed by anything yet.)
- The egg: inert, perishable, valuable, and the carried mark. (The egg is built. The carried mark is not
  working: see the mark defect above.)
- Quarrok and vennick doing their jobs; the vennick's run toward clutches. (quarrok built; the vennick's
  clutch-seeking moved in)
- The trace cast: skennet, cravvet, the flying sivvern; the sixteen invented plants as ordinary plants, with the
  brimlock's water and the fellome's food. (built; a seventeenth plant, the glasmaw, was added after the roster)
- Silk spun at the ship and its doors wrapped. (built for the siege; pointing it at a landed ship is owed)
- Canopy as one step of cover. (owed, small)
- The heat of the clearing on crew and hull; the thermal veil as the answer. (The shield frame is built. Heat
  here is ordinary hot air plus the one Direct Sun from geometry, by his ruling of 2026-10-19; the biome's old
  heat-kind fields are obsolete and must stop having any effect. Never run on a Webwork map.)

**0.2.0, the stop with company**
- The siege on the next tile over: the owners arrive at a home beside the Webwork, spin, wrap doors, cocoon the
  downed, and leave after days. His order of 2026-10-22: *"Make a webwork event into neighboring biomes where
  spiders come in and start spinning webs as a map attack. Their version of a raid. Siege"*, and his card the
  same day: they work in shade only, the silk yields thrixweave, a cocooned person dies after a day, the silk
  stays until cut. (built; failed its live run of 2026-11-06, and as written it can arrive across open sun)
- Cocoons with a rescue clock, on the home map too. (built)
- The traction lance, its rigging in cloth, devilstrand or thrixweave, and learning it from a cut junction (or from
  the Sump's draw-joints). (built; passed live 2026-11-06. Nothing places gutter junctions any more, so today it
  can only be learned in the Sump.)
- The giant the spiders ate: a wrapped skeleton bigger than a building, read bone by bone, whose loaded bones
  creak and come down. (built)
- Plants that act: the snap-trap, the needle-wand, the bait bell. (built in part)
- The still-tree's liquor as fuel. (the liquor is built; nothing burns it)
- Beetles herded along a route to cut a corridor. (not built)
- Webfall spoiling aim; passive stickiness of web underfoot. (built)
- The spiders' pale flowers showing which lines are live and which abandoned. (not built as a state; see the
  choices page)
- The ship's acoustic scanner readings here. (built)

**Later (a crew that stays, a colony, or the campaign layer)**
- The Hutt egg market and the Wildsteam weavers; the Wildsteam's bounties for destroyed eggs and for mandibles; the
  broker's deadline quest for eggs; the Reckoning and its family of quests that end with an egg in someone's
  room: campaign.
- The titanic battle he asked for on 2026-10-22: *"Use a neighboring giant but also spawn some giant spiders to
  attack it."*
- The Felled Noon rite (tabled with all rites, 2026-10-03; and by his card it waits for the tree-shade model).
- Silk gutters as moving water; the still-burner as a weapon.
- An egg that can be planted as a weapon outside a quest (filed as future work by his card of 2026-09-24).
- Two sketched campaign jobs that suit a ship: *"Fragile Cargo"*, the Cartel paying to move a clutch across
  Webwork ground against the mark, and *"Something in the Walls"*: *"someone paid to put an egg in your colony —
  find it before nightfall."*
- Dry air as a second weakness of the owners (the sheet: weak *"away from high humidity"*; unbuilt).

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- A tamed, traded or negotiated owner; truce language; silk from an abdomen; a safe cell under dense canopy;
  thrixweave from any other source (sheet bans).
- Castes or guilds of the owner (one race, one kind, by card 2026-09-23).
- A web front that creeps without spiders. His words, 2026-10-22: *"Webs don't creep they are made by spiders."*
  With it went harvesting from the creeping border.
- The living colossus (the morravell, *"the one thing the web cannot hold"*, whose feeding opens *"a line of
  fresh sun-holes"*), falling sheets of web, the Cut Cocoon and the testimony rite (not chosen 2026-10-02).
- Castes by another door: the parked guild names and the donor hatchling (one race, one kind).
- A player-built sticky trap (deliberately never built); the commanded slick-or-locked web.
- An egg that hatches as an item, or a second egg def (ruled out 2026-09-24).
- An attack-free grace period on foot (rejected by his card of 2026-10-22).
- The egg broker as a Bazaar tab (cut 2026-10-23).
- The three donor animals and the six generic donor plants (cut at this biome's own sitting).
- Biome placement scoring as a feature (no worldgen, ever; the existing worker stays as it is by his card).
- **Recommended for dropping, not yet his:** the old duplicate anchor, sheet-web and gutter objects that nothing
  places any more; the mutator that seeds owners on other biomes' maps.

## NEEDS HIM

1. *(hull)* **Roots in the ship.** On 2026-10-02 he was offered *"Your Hull Is a Trellis"*: where a living silk gutter
   touches a landed ship, pale roots thread an inside doorframe, thicken, force the door and split the frame;
   *"cut it out, or take off: the supply is severed but the damage flies with you."* He did not choose it that
   day: the card recommended taking all three new ideas and he took the lance only. The review called it *"the
   biome acting on the ship in its own voice (the plantation occupies structures), not a ship gadget."* He was
   offered the Greentide's hull rasp the same week, did not choose that either, and on 2026-11-18
   said yes to it by name. *Silk and wrapped doors only* (default: built parts, and the owners' own hand).
   *Add the roots:* a second wear that works in the dark while nobody is watching, and a new system.
   *Waits on the declined-ship-ideas question of 2026-11-19.*
7. *(scope)* **Should the cut cocoon exist as a thing to find?** The rite was not chosen on 2026-10-02. Its found
   site is one of the best pictures in the sources: *"a silk cocoon on a sunlit rock, cut open from the inside,
   empty, knife marks on the inner wall and boot prints going away into the light. Someone got out."* *Leave it
   out* (default). *Place it as scenery with no rite attached:* small, and it tells a crew that people do leave.
   *Waits on the declined-ship-ideas question of 2026-11-19.*

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

2. *(other)* **Does an Imperial probe count as a droid?** Yes, and the design says so: the web eats the probe step,
   and the later search steps still come (the design's recommended answer). *Delegated call.*
3. *(scope)* **The plants that act.** 0.2.0, not retired (the design's default). *Delegated call.*
4. *(hull)* **Which wear is the Webwork's own?** Heat, built and sourced, is the 0.1.0 wear. Silk at the canopy's edge
   is a proposal for 0.2.0 (the design's default). *Delegated call.*
5. *(cover)* **Is the bargain right?** Keep the bargain as written (the design's default). *Delegated call.*
6. *(other)* **Two animals called wyyyschokk.** Rename the older one. Two creatures with one name is a defect. The
   older one is `RSW_Wyyyschokk` (the generic bestiary animal); its label changes and its defName stays, because
   TrophyCraft and the Utinni tolerances patch name it. **This changes the design's default.** Was: *Leave both*.
   Undo: set this answer back to *Leave both*; nothing is built. *Delegated call.*
