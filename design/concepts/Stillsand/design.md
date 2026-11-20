# The Stillsand: the design, seen from the ship

**Status:** the one design document for the Stillsand biome (`RM_Stillsand`, source `src/RimMandrake/Stillsand/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the two
older definition sheets (the dune sea and the deep desert, which are regions of this one biome), the reviews, the
cast documents and the cleanse proposal as the place to read; what happened to every idea in them is in
`design/concepts/Stillsand/rewrite_choices.md`. Nothing has been deleted yet. The Stillsand is one of the mods HELD BY
OWNER: this is a design document only and it launches nothing.

**Kind, checked against the sheets' own headers:** land. Open sand on the deep dayside. *"The Dune Sea is a region,
not a biome. Be careful!"* (owner, 2026-09-28.)

**Who reads this next:** the Stillsand already has a Designer tree in this folder: an adopted root (`root.md`), a
sheet (`sheet.md`), leaves (`tree.json`) and scenes. This design does not edit them. A Designer run on this concept
is handed the list of files in this folder (`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this
file is in its path by sitting here; the root and leaves were written for a colony that stays, and a later run has
to reconcile them with this document. Where they disagree until then, the root is what the pipeline holds and this
is what the owner asked for on 2026-11-18.

**Second reader, 2026-11-18:** a second pass read every file this design replaces to its end and repaired this
page. The hull section now stands on the campaign's built shield frame (the first pass wrote that no hull system
existed) and on wear the sources name. The biome's gift to the ship, the lens kit, is in 0.2.0, and the sun lance
is out of "recommended for dropping": he took it by card on 2026-09-30. The sentence that leaned on *"No roads
through the deep dune"* is corrected, because his word of 2026-10-20 put the roads back. The zuurrik, the piinnok,
the dead crawler and the gale's effect on the swimmers are now where a reader of the Empire section will meet
them. The locked tree is still not edited. The count of what was added is at the top of `rewrite_choices.md`.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"A corrugated ochre plain that goes on past every horizon, under a star that has not moved in the history of the
> world."* (`dune_sea.md` §1)

Every dune runs the same way. Every shadow is the same length and points the same way, so *"the whole landscape is a
compass pointing at the star."* There is no night, no evening, no cool hour to wait for. It looks dead: *"the
standing crop of this biome would fit in a bucket."* It is not dead. *"The dune sea is not lifeless, it is latent,
and it is armed. It looks the same whether it is empty or loaded, and the player is the detonator."*

The owner's line for the experience, picked by card on 2026-10-20:

> *"An ocean of nothing under a sun that never sets, crossed by giants. Rock islands are your harbours, and their
> caves are your fortune."*

And his brief for it, typed on 2026-09-30:

> *"This is THE poster biome of the old tattoine. Huge skeletons on the sand. Barren tracks of apparent
> nothingness."*

**Seen from the ship, this is the one stop where the crew thinks it knows better.** Everywhere else the Jawa are
desert people in the wrong place. Here they are desert people in the desert, and an older design pass put it in a
sentence: *"This is old Tatooine: the place Jawas were made for, and the place that made the krayt."* They walk down
the ramp without flinching. By the owner's ruling of 2026-09-30 the glare that blinds everyone else does nothing to
them (*"the Jawa won't need it, but the slaves might"*).

They are still in over their heads, because they are road people and a ship does not land on a road. The frozen
sheet banned roads here outright (*"No roads through the deep dune"*); his later word of 2026-10-20 put the old
road lines back across it (*"For now just replicate where we had roads before."*), so on the world map a few
roads cross the Stillsand and everything between them is this. The sheet's own word for the place is still the
right one: *"It is not a place you visit. It is the distance between places."* What lives here lives under the sand, feels every footfall, and has been asleep for years waiting
for something to do something. A ship landing is something.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew shortens every wait and a hidden one lengthens it.

**The outer edge of a stay here: about a month.** By the owner's word of 2026-11-18 the figure a design derives is
*"the outer edge allowable"*, not the typical stay. If the Empire wins every step, the bombardment is the fourth
full interval of the ladder, 20 to 32 days at the ordinary pace. Nothing in the Stillsand lengthens that. It is the
plainest clock on the planet, and the campaign's own rule for open sky applies in full: the search *"forces exit
from any open-sky tile in under one growing season."*

**Cover from orbit: none, except inside a dune gale.** His ruling of 2026-11-18: *"Canopy, steam and fog slow the
search by one step; full dark still pauses it."* The Stillsand has no canopy, no steam, no fog, no night and no
cloud. *"Sightlines. You can see anything coming from an hour away. So can it."* The one exception is the biome's
own weather: for the day or two a dune gale lasts, *"the sky goes brown-gold and dim, sight shortens"*, and this
design gives the search its one slower step for exactly that long (0.2.0, with the gale). A cave hides people, not
a ship. The gale is also the one time the sand itself looks away: *"The gale blinds the swimmers. Their appraisal
is by vibration, and the storm is all vibration, so swimmers stay down and strike rates collapse."* The older
design's conclusion holds for a crew as well as a caravan: *"A player who learns this crosses the Stillsand in the
gale."*

---

## The first minutes

The ship comes down onto a plain *"the colour of old bone under a white sky."* The landing is the loudest thing
that has happened here in years, and everything under the sand felt it.

A letter names the one landmark and its bearing: *"A rock island stands to the north-east."* Usually there is one
outcrop on the whole map, long and wind-carved, and *"everyone who has ever lived here knows there is a cave in it
and something precious in the cave."*

Before anyone has moved, the player can read the page:

- A ribcage *"the size of a sandcrawler"* stands out of a dune, each rib throwing a hard black stripe, the wind
  moaning through it.
- *"A track across the flat, a trough in the sand that runs straight for a hundred cells and then simply stops, at
  a patch of sand that is darker than the rest."*
- Small clear glass nubs flush with the surface, one every few paces, catching the sun. They are the only visible
  part of almost everything that grows here.
- Under the hiss of the one wind, *"a sound you feel in your teeth before you hear it: a long, low rumble, moving.
  A line of sand lifts and falls, far out, travelling."*
- And some of the glass is looking back. *"Half the 'light-pipe nubs' in a field are not plants."* They are the
  lenses of the piinnok, the Stillsand's watcher: *"Walk past a nub field and a few glints turn to follow."*

The Jawa do not cook when they step off the ramp. Anyone else aboard does.

## The first day

- **The sun does not move.** The one sun from geometry, at this tile's own height in the sky, forever. *"The light
  is a fixed condition, like the pressure at the bottom of a sea."* A roof or a parasol is shade at any angle.
  Standing shade is three things only: an ollim, a wreck or skeleton, and the rock. The ship is now a fourth, and
  the largest: the sources already count on it (*"move in the shadow of your own landed ship"*), and the sheet
  says what a fallen hull's shade becomes: *"Where debris falls it makes shade, and shade makes a small living
  biome right beside it."*
- **The sand is a medium, not a surface.** Vekka and qorrax swim under it. The player sees a wake and hears a
  rumble that grows with the size of the swimmer; the animal itself shows only when it breaches to strike. What it
  takes leaves a drag mark and a darker funnel. Nothing vanishes without a sign.
- **The ground lies.** The drazzik drums *"fat and wounded"* through the sand to bring hunters to it. The duumma, a
  barrel of stored water, drums dry and hollow so they pass it by.
- **Eggs are canteens, and some are traps.** *"A large egg is portable water in a rigid shell, which is exactly why
  a Jawa prizes one."* Some clutches hatch on approach, and the newborn *"tries to drink the intruder."*
- **The wrecks are bright.** *"Nothing rusts without an electrolyte; dayside wreckage is sand-scoured bright and
  half-buried, never brown."* Hulls, cylinders and dead crawler treads come apart for ordinary salvage. A tread
  line in the sand can end at a dead sandcrawler, the crew's own ancestral machine, with a note scratched on the
  dash: *"We ran her until the sand had her. If you find her, start her once before you take her apart. She will
  know you."* (The rite built on that note is in "later"; the crawler and the note need no rite.)
- **The walk to the rock is the first expedition.** Deep sand is slow. The crossing is measured in water, in heat
  and in how much noise the party makes.
- **A droid makes no ripple.** Swimmers strike what holds water. *"A droid is invisible to the food web... A Jawa
  clan that fields droids can cross ground nothing alive can cross."* The crew that sends its droids to fetch is
  playing this biome correctly.

## The first week

- **The cave.** The mouth opens on the rock's shade face. Inside *"the air is cool, the light is gone, and there is
  water"*: one of a brine seep with its own vicious little food web; a guzzka on a clutch of eggs that are *"the
  best drink of water a person could carry"*; a grotto walled in grown glass; a sealed cache; or a cave somebody
  took before. His answer of 2026-11-10: *"Only a prepared harbour is dependable"*; arrival alone promises nothing,
  and not every cave holds a fortune.
- **The giant.** An oommok, mirror-plated, *"moving at the speed of a shadow on a sundial, carrying its own weather
  underneath it."* Its shade moves with it and small things live in that shade. *"Following a giant is how you
  cross the dune sea."*
- **The follower.** A gaanok, *"taller than a wall and thin as famine"*, appears on the horizon behind any party
  that walks out, and keeps its distance, and waits. *"Shooting it is spending water on a thing that has not
  touched you... The horror is that it is patient, visible, and correct."*
- **The glints that moved.** The liikka, a thumb-sized mirror-backed mite that eats light, is the one animal a
  traveller actually sees: *"a scatter of stationary glints that turn out, on the next look, to have moved."*
- **The sky's one owner.** A soorrak, a sail-winged giant that nests here because nothing can walk to its nest. It
  really flies. Its eggs are the biggest canteens on the map.
- **The ground goes off.** Camping, digging and drilling on dry sand are a wager. The sand busters come up under
  the work: one giant eruptor and a wave of grain-sized ones after it. *"The planet's only infestation biome."*
- **The drifts.** The dunes move, slowly, toward the star. Sand banks against whatever stands in the wind and can
  be shovelled off.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The swagger.** *On screen:* the ramp drops, the Jawa stroll out into heat that drops a human, and one of them
   sets off across the flat alone. A wake turns toward the footsteps. *Why it is funny:* this is home, and home has
   teeth they only ever heard about from the road.
2. **The track that stops.** *On screen:* a trough in the sand, dead straight, ending at a dark patch. The player
   works out what it means a moment before the same thing happens to a pack animal.
3. **The wrong egg.** *On screen:* a Jawa hugging an egg the size of its own torso, running; behind it the rest of
   the clutch splits open and small sharp things pour out after the water.
4. **The liar.** *On screen:* a drumming under the sand that sounds like easy meat. A swimmer's wake goes to it.
   So, a little later, does a hunter from the crew. *Why it lands:* the ground fooled both of them the same way.
5. **The droid walks through.** *On screen:* a crew member frozen at the edge of the deep sand with a wake circling;
   a droid trundles past, across the same sand, to the wreck and back, and nothing so much as turns. *Why it is very
   Jawa:* they knew droids were worth having. Now they know why.
6. **The ground goes off.** *On screen:* the sand under the salvage camp domes, bursts, and a thing the size of a
   speeder comes out of it in a column of dust; then the sand around it boils with small ones.
7. **Living in a skull.** *On screen:* the crew's forward camp set up inside the skull of something vast, in the
   only full shade for a mile, with the ribs humming.
8. **The cave has a tenant.** *On screen:* torches in the dark, a wall of pale eggs, and behind them the guzzka,
   which has been breathing the whole time.
9. *(0.2.0)* **The mountain that looks back.** *On screen:* a warning rumble for a full minute, a wake as wide as
   the ship, and the muurrok surfaces and turns a crest of mirror plates until the sun in them finds a target.
10. *(0.2.0)* **The gale.** *On screen:* the windward horizon turns ochre, the dunes march across the yard in
    hours, a crew member caught outside is carried off with a drag trail and a letter, and when it clears a whole
    mummified caravan is standing where there was a dune. *"Its packs are intact, and its water skins are the most
    valuable thing in it."*
11. *(0.2.0)* **The water that is not there.** *On screen:* a heat-struck passenger walks off toward a shimmer at
    the map's edge, and has to be fetched.
12. **The field blinks.** *On screen:* a patch of glass nubs the crew has walked past all day; then every lens in
    it sinks at once, and a moment later the rumble arrives. *"When a field's piinnok lenses all sink at once,
    something large is moving under that sand."* *Why it lands:* the warning was free and they had been ignoring
    it. (Built in the watcher kit; its place on this biome's roster is owed.)
13. *(0.2.0)* **The stain boils.** *On screen:* after a fight on open sand the blood on the ground starts to
    move. *"Kill something in the Stillsand and within the hour the stain boils with zuurrik stripping it, then
    the bodies around it."* What is left is a picked skeleton and clean sand. *Why it is very Jawa:* *"Kill, loot
    fast, leave."*
14. **She will know you.** *On screen:* a tread line ending at a dead sandcrawler, and the crew, who came to strip
    it, standing in the cab trying to make the drive turn over once first.

## When the Empire arrives

- **Everyone sees everyone.** There is nowhere to stage out of sight and nowhere to hide the ship. The probe's
  sighting is nearly certain unless it is shot first.
- **The probe is a droid.** Nothing under the sand will touch it. The Empire's attack droids cross deep sand as
  safely as the crew's own.
- **The troopers are full of water.** A strike team walking in across deep sand is the biggest, loudest, wettest
  thing the swimmers have felt in years. The sand takes whoever is heaviest on it and leaves a funnel.
- **The noise is on their side of the bill.** Drop pods, a siege camp and an ion emplacement are drums. The sand
  busters do not ask whose camp they are under.
- **They saw the ship first.** The older design's note on any raid here: *"raids here see you too. They arrive
  knowing your layout and pick the side without a wall."*
- *0.2.0:* **every firefight starts a clock.** Blood on sand wakes the zuurrik, which strips the stain and the
  bodies beside it and never touches the unwounded. *"A battle left standing becomes a zuurrik bloom."* A strike
  team that wins on open sand has an hour to enjoy it. So has the crew.
- **Shade is ground worth holding.** Under this sun a fight is also a fight for the skull, the wreck and the rock's
  lee. Whoever stands in the open is on a second clock.
- **The cave is a redoubt for people.** A thick natural roof, one mouth, cool air. It does nothing for the ship.
- *0.2.0:* **the thumper.** A staked drum that draws swimmers while its sand is wet (owner, 2026-09-30: *"thumper
  needs moisture not just thump"*). *"Bait a krayt away from your walls, or call one."* A crew that plants one
  beside a cordon and pours its last water on it has done the most Jawa thing in the campaign. **The gale** takes
  the sun off everyone, blinds everyone, and buries a siege line as readily as a stockpile. It also keeps the
  swimmers down, so the gale is the one hour a strike team can cross deep sand safely, and the one hour the crew
  can.

## Who else attacks; who hates the Empire

- **The swimmers,** whoever walks. **The sand busters,** whoever digs.
- **The follower,** who attacks nobody and finishes whoever falls.
- **Krayt dragons** are wild animals here in the campaign's cast (owner's card of 2026-09-30: they *"stay wild"*),
  patch-added by the Star Wars layer; krayt attack events are that layer's addition. The free tier's own leviathan
  is the muurrok (0.2.0).
- **Ordinary raids** arrive across open sand like anyone else, announced by their own dust.
- **Who hates the Empire:** the sheet seats the **Deep Desert Tribes** here, in *"canyon lips, rock islands, and
  dug-in shelters far from everything including each other, with no roads leading anywhere"*, and says the **Jawa
  Trade Moot's** crawler circuit runs through. Both are placed by the campaign layer, not by this biome. Whether
  either fights the Empire is `UNSETTLED`. *"Fire is the tribes' weapon"*: here it routs what nothing else will
  move, and there is no fuel to make it with.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- Water and food. *"The deep dune kills by absence."* The eggs, the sacs and the sand's small catch stretch a
  larder; they do not fill one.
- The busters, once the camp has been loud for long enough.
- Open sky. Nothing here slows the search.

**Stay, as long as the clock allows:**
- A secured cave: shade, cool, a seep, one door.
- Droids to do the walking.
- The sun itself: it never sets, so anything aboard that runs on light never stops. The older design read the
  base game's solar generator and found it follows the sky's brightness, not the clock, so under the pinned sun
  *"solar panels run at 100% forever with zero patches"*, and *"the dune gale... is then the only thing that ever
  cuts the colony's power."* (That reading was of the code; nobody has watched it in a running game.)
- The ship's own shadow: shade to work in on the lee side, and by the sheet's rule a place small life will come
  to rent.
- Nothing rots quickly in a cave the crew holds, and nothing rusts anywhere.

## Fuel, and the hull

**Fuel: the emergency route only.** *"There is no fuel here, so every scrap is imported."* *"No fire. There is no
fuel; a wildfire in the dune sea is a rendering error."* The slow rendering of biomass into chemfuel that every
biome allows has almost no plant matter to work on; what it has is carcass, and here a carcass can be enormous:
*"hide, plate, tallow and bone at a scale nothing else on Ash'karr provides."* Killing a giant for its tallow is a
fuel plan only for the desperate. The local find is salvage: a sand-sealed cylinder in the wreck field can hold
chemfuel (the tank salvage table in `src/RimMandrake/Wreckage/Defs/ThingSetMakerDefs/RM_SalvageLoot.xml` lists it).
The campaign's fuel ruling of 2026-08-15 names *"helixien gas (volcanic/deep-desert tiles)"* as one of the paths to
fuel; no Stillsand source places a gas deposit on this biome, so this design does not claim one: `UNSETTLED`.
**Where fuel is bought:** from the Jawa Trade Moot's crawlers if the campaign layer puts one on the map, and from
ordinary trader caravans (the free tier has its own pack giant, the vaalok, built so that caravans come here at
all). Buying fuel from cousins who know exactly how badly the crew needs it is the intended kind of trade.
**What the crew pays with:** the sand. By his card of 2026-09-30 shovelled drift is glass sand at full yield and
sifts to fine sand, *"a trade commodity"*; by his card of 2026-10-16 glass sand is also the ingredient another
biome's rite needs. A crew that pays for fuel in sand it shovelled off its own ramp is the joke working.

**The hull: the sun, the sand, and what the landing woke.** His ruling of 2026-11-18 puts the biome's wear on the
ship in 0.1.0 and names the kinds: *"Heat... Rough weather... Different kinds of shields or armor. It's in there."*
The frame is built: `src/RimUtinni/ShipShields/` (his eight shield rulings of 2026-09-02, recorded in
`design/Jawa/proposals/ship_shields_deep_design.md`). This design adds no hull system. Every wear below has a
source, named beside it.

- *Heat on the hull (0.1.0; built, in the campaign tier).* The shield frame's exposure tracker wears the ship's
  own structures while the map is in extreme heat and no shield covers it, with one advisory letter on landing
  and never a refused landing. The answer he ruled is the **thermal veil**: *"It would reflect all external heat
  outward with a mild mirror sheen to the shield, but also reflect all internal heat inward, so the temperature
  slowly climbs anyway... Just use power for fuel"*. Under a sun that never sets the veil never gets a night off,
  and here the power for it is free. `UNMEASURED`: the tracker calls a map hot at 58 °C outdoors or in a heat
  wave. The dune sheet gives this ground 52 to 70 °C and the deep sheet's far-ring regions a median of 26 to
  43 °C, so on some Stillsand tiles the built heat wear would fire and on others it would not. Nobody has read it
  in a running game, and no bar pins the number.
- *Blown sand (0.1.0; built for the stock sandstorm only).* The tracker also wears an unshielded ship while the
  weather carries sand, and the biome's weather table includes the base game's sandstorm. The answer he ruled is
  the light screen, which handles *"wind, ash, vapor, bio contamination, spores, smoke, sand, and rain damage
  completely as well as repels small animals"*. The biome's own dune gale is written to carry no falling sand
  (`RM_DuneGale.xml`), so the frame cannot see it today; teaching the frame the gale is the build, with the gale,
  in 0.2.0.
- *Drift (0.1.0, ordinary systems).* The frozen sheet says it of everything that stands here: *"a structure is
  buried on its windward face and undercut on its lee"*, and bans any *"permanent structure not either buried or
  actively dug out."* Its consolation is written for exactly this crew: *"crawler-scale machines are the only
  settlements that make sense in a landscape that buries fixed ones."* The dunes engine banks sand against the
  windward side of whatever stands in the wind; around a landed ship that means ramps, vents and outside fittings
  going under a cell at a time, and hands with shovels. Shovelled drift is glass sand, which sells. `UNMEASURED`:
  whether drift builds against a gravship's hull today (the engine clears the sand under a ship as it lands).
- *Things that come up at it (0.2.0, with the creatures).* The landing is a drum. In the campaign layer the krayt
  attack is *"weighted up by... vibration (drilling, a landing ship, the thumper)"*, and the krayt goes *"toward
  whatever is making the most noise"*; in the free tier the muurrok and the busters answer the same noise. His
  heavy field is the shield for it: it *"resists impactors, blaster fire, and large animal assault."*
- *A proposal, flagged as the second reader's own:* ollim wood as cladding. The sources give the wood (*"armour
  and structure that laughs at fire and folds to a hammer"*) and his ruling names armour among the answers; no
  source puts ollim on a hull. It would be the scrap answer to the heat for a crew without a veil.
- *Declined, and not revived here:* **the dunes take the ship** (sand climbing the hull until dug out, and the
  landing raising the odds of an eruption by the ship's mass; out by his card of 2026-09-30) and **gale
  abrasion** (structure wear in a dune gale; built, then cut on 2026-10-23 under his *"I cut, you veto"* card,
  restorable by reverting one commit). Both stay down by his answer of 2026-11-19 on declined ship ideas.

## What the crew takes away

- **Salvage, bright and unrusted,** and whatever a sealed cache held.
- **Eggs and water sacs:** drink that travels.
- **Biosilica** from the glass nubs and the grotto walls: *"the only natural glass on the planet that is not
  volcanic."* **Glass sand** by the shovel.
- **Ollim wood:** near-immune to heat and flame, *"helpless against sharp and blunt."*
- **Glass pearls and dune crawlers** from fishing the deep sand.
- **Giant hide, plate and bone,** if something vast died within reach.
- **Karrask plate,** from a livestock animal that sheds it.
- **A cave the crew knows.** A second landing on the same tile starts with a harbour.
- *0.2.0:* **the lens kit, the Stillsand's gift to the ship.** His instruction of 2026-09-24 for every biome:
  *"how can this biome uniquely add something to the ship?"* The answer on record (`BIOME_SHIP_CONTRIBUTIONS_1`;
  the lens chain is his typed ruling, choosing these two as the gift was an agent's pick) is *"the lens-glass
  solar still and sun lance, fuel-free on an open deck"*. Both are built. The still makes water out of brine, wet
  kills and eggs under the fixed sun; the lance is *"Archimedes' mirror in a biome where the sun never sets"*,
  and it heats and never ignites.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A whole map of open sand with one rock, a few bones and wrecks, and room between them. | A fresh landing, the whole map in view. | A showcase pad proves nothing: the look is judged on a generated map with every kept feature on. |
| The sun never moves; a roof or parasol shades at this tile's sun angle; a skull is full shade and ribs are partial. | A pawn in the open, under a roof, under a parasol, inside a skull, under ribs, for the same hours. | The same pawns on a tile with a lower sun: longer shadows, milder sun. |
| A giant carries shade that moves with it, and the place it stood a minute ago is not shaded. | A pawn walking beside an oommok and one standing where it was. | |
| Things travel under the sand with a wake and a rumble that scales with their size, and breach to strike. | A vekka and a qorrax, each with prey on deep sand. | On rock or gravel there is no wake and no strike from below. |
| What a swimmer takes leaves a drag mark and a funnel. | A kill on sand, watched and unwatched. | The same kill by an ordinary predator leaves a body and no funnel. |
| Swimmers do not strike a droid. | A droid and a person cross the same deep sand with a swimmer near. | A person carrying nothing is still struck: it is the body, not the cargo. |
| The drazzik's drum draws hunters; the duumma's hides it. | Each with a swimmer in range. | A silent drazzik draws nothing. |
| Some clutches are canteens and some hatch on approach. | Take eggs from a soorrak nest and a drazzik clutch; drink one. | |
| The rock holds a cave; the cave is cool, dark and occupied by one of its kinds; clearing and holding it makes it a place to rest and store. | Find the mouth on the shade face, go in, deal with what is there, stock it, sleep in it. | An unexplored cave gives no safety: its tenant is still in it. A cave with nothing useful in it exists. |
| The wrecks and sealed caches give real salvage and are not replaced. | Strip a hull, a cylinder and a tread; open a cache. | |
| The soorrak flies, by the flight state, and nests where nothing walks. | A state read of its flight tracker (never a live look without the owner). | |
| Sand banks against the windward side of what stands in the wind and can be shovelled off for glass sand. | A wall and the ship left a season's worth of fast-forward; shovel. | The lee side stays clear. |
| Nothing vanishes. | Every loss above, and the mod's master setting switched off mid-event. | |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Digging and building on dry sand can bring the busters up under the work, with a rumble first. | A work camp on sand run until it happens; the same camp on rock. | On rock it never happens. |

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary extreme desert
(standing rule, every mod).

## Shared machinery

**Featured here** (the Stillsand is where each is vital and should be proven):
- **Travel under the surface with a live tell above it** (`RM_CompSandSwim` in `CreatureBehaviors`): submerge,
  wake, rumble, breach, drag and funnel signs, and the rule that a body with no water in it is not prey. The
  Sleeping Ice borrows it for its tunnelers.
- **Dunes that move** (`MovingDunes`): drift, burial, uncovering, and the eraser for tracks.
- **A sun pinned by the tile's place on the planet** (`RM_PinnedSunExtension`, with the one sun from geometry in
  `EnvironmentalHazards`). Every dayside biome uses the geometry; only here is there never anything else.
- **Shade that walks** (the moving-shade support on giants) and **shade as a place** (skeleton and skull cover).
- **Tracks the sand keeps** (`RM_MapComponent_TrackGrid`).
- **Eggs that hatch on approach** (`ProximityHatch`).

**Merely active here:** wreck salvage (`Wreckage`); bone from butchery; real flight; walking giants and their
footprints (`HugeThings`); the growth engine, which has almost nothing to grow; water volumes in eggs and sacs
(`FlowWorks`); fishing; the ship's scanner; the Empire's search and the visibility dial; cold storage.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**The one signature (his first-version answer of 2026-11-19): the rock island and its cave.** A crossing of open sand,
where things hunt under the surface, ends at the one rock; its cave on the shade face is cool, dark and occupied by
one of its five kinds; clearing and holding it make a refuge whose finds provision the next crossing. *Why a normal
stop is sure to see it:* the rock island is the harbour a ship lands by, and its cave mouth is on the face the crew
shelters behind. His experience line: *"Rock islands are your harbours, and their caves are your fortune."*
*Runner-up:* the dune gale's carry and return (the cleanse's runner-up), at 0.2.0. The sand busters, the busters'
eruption under work, move to 0.2.0: they are a second hazard a stop can avoid by not digging on dry sand.

**0.1.0, the stop**
- The land: open sand and slow deep sand, the pinned sun and the one-sun rule, moving dunes and drift, the rock
  island and its arrival letter, sparse skeletons with skull and rib shade and their wind-harp, the bright wreck
  field. (built; the one-sun rule replaces an older per-biome heat regime still in source)
- The cave: the mouth on the shade face, and its five kinds (seep and food web, guzzka clutch, glass grotto, sealed
  cache, taken before); things kept in a held cave keep. (built)
- Under the sand: vekka and qorrax, wake, rumble, breach, drag and funnel; droids not struck. (built)
- The liars and the eggs: drazzik and its trap clutch, duumma and its water sac, soorrak and its canteen eggs,
  guzzka eggs. (built)
- The giants and their shade: oommok with its eemmok, the aurrok grazer, the gaanok. (built; the gaanok is an
  ordinary slow predator today and its following is owed)
- The small and the planted: grain-scale life, light-pipe nubs and glasscrust, tall and kneeling ollim and its
  loomma tenant, the murrowbulb crop. (built)
- Sand fishing; the wind and sand sound bed and the rumble. (built)
- Heat and blown sand on the hull through the campaign's shield frame, answered by the thermal veil and the light
  screen. (built in `src/RimUtinni/ShipShields/`; whether the heat wear fires at this biome's temperatures is
  `UNMEASURED`) Drift against the hull. (ordinary systems)
- The campaign's cast where the Star Wars and Utinni layers add it.

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The piinnok, the watcher whose lenses follow a walker and sink when something large passes under. (built in the
  watcher kit, admitted by his card of 2026-09-30; its roster row on this biome is owed)
- The sand busters' eruption under work on dry sand. (built; moved in, see `rewrite_choices.md`)
*Already here before that answer:*
- The dune gale: herald, marching dunes, sun off, the carry and the return, one thing uncovered when it clears
  (the mummified caravan among them), and the search slowed one step while it blows. (built, except the last)
- The muurrok and its mirror beam. (built)
- The thumper, wet. The krayt horn, in the Star Wars layer. (built)
- The busters' spreading brood mound. The zuurrik, the swarm that blood on sand wakes. (built)
- The geophone; the swimmer that comes when someone starts fishing; the singing dunes that warn a dune is
  marching on the camp. (built)
- Glare that blinds everyone but the Jawa, and the goggles for it. (built)
- The mirage, and the passenger who chases it. (built; the cleanse recommended retiring it)
- The ship scanner's readings here. (built)
- The lens kit as the ship's gift from this biome: the solar still and the sun lance, on an open deck. (built;
  moved here by the second reader, see `rewrite_choices.md`. The workshop that makes lenses stays in "later"; how
  a visiting crew comes by the kit's lenses without it, by salvage or by trade, is `UNSETTLED`.)
- Large things drawn to the landing, as wear on the hull; the frame taught to see the dune gale. (unbuilt)

**Later (a crew that stays, or a colony)**
- Learning to live here: glass sand to fine sand to sun glass and lenses, the sun furnace and lens bench, the solar
  oven and still, brine dipping and salt, the pearl and crest upgrades. (built)
- The water ledger: the Sun-Debt, the Return at a debt stone, the pour, the wet line, the hourbloom that answers
  it, the wringing still. (built; campaign faith. The Return belongs to the Deep Desert Tribes: by a ruling of
  2026-10-01 a Salvation colony cannot learn it.)
- The two rites the Jawa's own faith can find here (ruled-kept 2026-10-02, *"Accept all rites for now."*; since
  put under review by his word of 2026-10-23 that many rites are *"somewhat fluff"*): the Last Track, at a dead
  crawler; and the Unspilled March, walking full water toward a mirage and drinking none: *"He is the pool that
  walks away. Walk after him with full skins. Do not drink. He is watching the water."* (unbuilt)
- Giants' corpses becoming skeleton landmarks over a season; special outdoor desiccation.
- The den quest, the sarlacc that comes to root at the seep, the krayt-den, sarlacc and debt-shrine cave kinds:
  campaign layer.
- The ship's lens array and egg cistern; crossing the world map in a giant's shade; the cavern as a full authored
  ecosystem; yardang wind-grain across the whole map; loomma dung seeding flora.
- A harbour at colony scale, and wetting of crops by the all-game thin film.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Choosing prey by how much water it holds, "travel thirsty" (out by card 2026-09-30).
- The dunes take the ship; sinkhole caves; the glass sea landmark (out by card 2026-09-30). The first stays down
  by his answer of 2026-11-19 on declined ship ideas.
- Dust devils, gale abrasion and static, skeleton burial, the cave drip, the tribal mark, fulgurites (cut
  2026-10-23). Gale abrasion stays down by the same answer; he can bring either back by name.
- Krayts as events only (declined 2026-09-30: they stay wild). Kudda and truffle mole here (one home each, the Long
  Shade).
- A biome heat kind, a glare floor, cover rules that change with a named region (the one-sun ruling of 2026-10-19).
- **Recommended for dropping, not yet his:** arrivals delayed behind a dust plume; the extra fossil scatter; the
  cooling draught. (The cleanse's recommendations, kept. The sun lance and the mirage were on the cleanse's list
  too; both were his own card picks of 2026-09-30, so neither is on this one.)

## NEEDS HIM

None open. Every entry is answered (next section).


Two things the cleanse proposal of 2026-11-17 decided are changed here by scope rather than asked, and each is a
line under "Scope moves" in `rewrite_choices.md`: the sand busters were in 0.1.0 (his first-version answer of
2026-11-19 moved them back to 0.2.0), and the mirage is 0.2.0 instead of recommended for retirement. The second
reader added a third: the lens kit (solar still and sun lance) is in 0.2.0 as the ship's gift, where the cleanse
deferred the still and recommended retiring the lance.

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number.

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

1. **[scope] Should the muurrok or the gale come forward into 0.1.0?** *His card of 2026-11-19 (first version):* no.
   Neither is the signature (the rock island and its cave), so both stay in 0.2.0 as written, and the sand busters
   go back there too.
2. **[hull] The two wears on the ship that were cut: "the dunes take the ship" and gale abrasion.** *His card of
   2026-11-19 (declined ship ideas):* they stay cut. Heat, blown sand and drift carry the hull. He can bring either
   back by name.
