# The Sump: the design, seen from the ship

**Status:** the one design document for the Sump biome (`RM_TheSump`, source `src/RimMandrake/TheSump/`), rewritten
2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the frozen
definition sheet, the two rosters, the kit spec, the bedazzle review and the cleanse proposal as the place to read;
what happened to every idea in them is in `design/concepts/TheSump/rewrite_choices.md`. Nothing has been deleted
yet. This is a design document only and it launches nothing.

**Second reader, 2026-11-18 (same day, a different agent).** Every source was then read to its end, starting with
the ones the first pass had read in part or not at all. What that changed here: the fuel paragraph (the source and
the machinery were already ruled and built), the hull paragraph (it now cites the built frame and is flagged as a
proposal), the cover paragraph (fog, and his own light ruling), the belch and the tar fire (both further built than
this page said), the solvent wake (it hunts the crew too), the arrival letter (it was his idea), and several
moments and takeaways that were sitting in files nobody had opened. Each change is listed at the top of
`rewrite_choices.md`.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/TheSump/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Sump has no locked sheet or tree; its only pipeline material is the cleanse
proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) or a named ledger item found it in source; it does not mean it has
passed anything. The special-mechanics review of 2026-10-22 records every Sump map mechanic as built and untested.

---

## What this place is

> *"Black glass under a sun that never rises, holding a million years of the unlucky, perfectly."* (`the_sump.md`,
> header)

The planet's oil sump: the lowest basin on Ash'karr, just past the terminator on the night side, filled by every
slow black flow off the twilight slopes for geological time. Flat black pools and cooled glassy sheets under
permanent dusk, ringed with low waxy plants that feed on the tar instead of a sun that never comes up. It is cold,
it is dry (no rain, no water of any kind: *"the only liquid is tar"*), and it reeks for miles.

> *"Sticky, stinking, slow to move or burn or surrender. The sump hides all and makes you fight it for every
> action."* (owner, typed, 2026-10-20: the experience line)

The sheet's handle for it is **the trap that remembers**: *"The tar takes slowly, keeps perfectly, and sells it all
back to whoever digs."* Its rule of thumb is five words long: *"Mice run the black; where they won't, you don't."*

**Seen from the ship, this is the most Jawa place on the planet and the least comfortable.** It is a basin full of
everything anyone ever lost, preserved, for whoever is willing to get filthy digging it out. The owner's own ruling
of 2026-09-24 says who feels at home here: the biome *"should reward players who enjoy their colony being dirty,
messy, idiosyncratic. It should frustrate players who want neat, tidy, controlled. The world factions that align
with that are junkers, Jawa, deep tribes, black star."* The crew knows the Junkers' tar caravans from the Cracked
Lands roads. They have never stood at the place the barrels come from, in the cold, in the dark, with no sun, no
sand and nothing to drink, up to the hem in something that will not come off.

The crew are small, hooded, skittish and built for dry heat (`reconciled_lore/05_the_clan.md`). Here the dry is
the one familiar thing.

And one more thing is theirs. At the Sump sitting of 2026-09-24 the owner was offered a trait that would make the
aligned factions *enjoy* mess, declined it, and typed instead: *"Jawa should be immune from messes. The others just
live with it and suffer."* A Jawa takes no mood penalty from filth or squalor (built as a gene on the xenotype,
campaign layer: `src/RimUtinni/UtinniPatches/Defs/GeneDefs/Jawa_MessImmunity.xml`). So the tar slows the crew,
sticks to them, ruins what they carry and makes them easier to set alight, and none of them minds. Everybody else
who comes here is miserable. That is the whole joke of the biome, in his words, and it was missing from this page.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28: *"around every 5-8 days, keep 'em running"*; ladder in
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked provisional): a probe
droid five to eight days after landing, then scouts with a spotter, a strike team, an ion cordon on the ship, a
breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if the one before
succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last: about six to nine weeks for a crew that stays unlit, and that is the outer edge**
(his ruling of 2026-11-18: the numbers are *"the outer edge allowable for each biome"*). On open ground the ladder's
arithmetic gives a probe on day 5 to 8, a first real fight around day 12 to 20 and the bombardment around day 20 to
32 if the Empire wins every step. A crew the search reads as discreet or hidden has every wait multiplied by 1.4 or
by 2 (`EmpireLadderMath.BandIntervalMultiplier`), which is where six to nine weeks comes from; a crew that lights
the place up gets the open-ground month. The Sump earns the long end for two reasons that are already built. The watchers must *see*
the crew or the ship, and a target standing in darkness is seen only from six cells instead of twenty-six
(`EmpireLadderMath.Sees`); the Sump is permanent dusk, so an unlit crew is nearly invisible at ground level and
every lamp it lights is a choice. And nothing here grows, floods or closes in on a schedule: the tar is patient.
That is the outer edge, not the usual stay. What actually ends most stops is on the crew's side of the ledger: the
water it brought, the solvent it can make, and whether somebody dug one stratum too deep.

**Cover from orbit (his cards of 2026-11-18 and 2026-11-19: one step per kind of cover on the tile, added; full
dark is one step; nothing pauses the search).** The Sump has no canopy and no steam. It has the dusk, with the sun
held about ten degrees under the horizon, and fog. Two things throw it away at once: a lit moat, whose smoke
column the sheet calls *"visible for a day's travel"* and paints *"an orange smear on the underside of the sky"*, and a lit-up camp.

The cover has a leg the first pass did not see: the Sump's forced weather is fog. `RM_SumpWeather`, the
only weather the dusk lock allows, wears the base game's fog overlay and fog wind, and his card names fog as one of
the three things that slow the search by a step. So the fog gives one step every day. The dark is a measurement of
the sun's angle at each tile: the measurement put before him on 2026-10-20 reads the Sump at a median glow of 0.02,
with four tiles in ten fully dark (`design/RimMandrake/glow_consumers_2026-10-20.md`), and a fully dark tile adds a
second step. A ship on such a tile has two steps; elsewhere it has one.

**Fuel (his ruling of 2026-11-18, and three older ones the first pass did not find).** The source is the tar, and
it is neither new nor unbuilt.

- *He ruled it on 2026-09-02.* On the tar-pits proposal's row for a chemfuel economy he wrote: *"Yes, but it's slow
  and gross. Tar oozes out of the pipe joints. Only slowly produces chemfuel."*
  (`design/Jawa/proposals/tar_pits_deep_design.md`).
- *He bounded it on 2026-09-07.* The freeze ruling on fuel (*"the fact that people have found SO MANY ways to get
  fuel is still evidence of its scarcity"*) gives tar its own line: *"not fuel — must be **processed**, on machinery
  found only in some tar-containing squares (injected by inhabited), and it is **slow**; the player cannot stay
  long."*
- *He gave it a job on 2026-10-10.* The story card on what the Sump is for: *"fuel route in v1; the Junkers' supply
  chain feeds the Hutt ledger pressure."*
- *It is built, in FlowWorks.* A **wrecked tar refinery** is scattered once per map beside tar
  (`RM_TarRefinery_RuinScatter`), found broken, and patched back to work where it stands: wrecked, then kludged
  (*"mismatched plate and hope; it runs at half its old rate"*), then repaired. It is never on the build menu in the
  campaign. It cracks tar to chemfuel at four to one by volume and needs power and a tank on each side. Tar itself
  comes in bottles, buckets and barrels, and the Deep Black mere (below) never runs dry. None of this has been
  proven live, and one small defect is on file (`TAR_REFINERY_FIX_CAN_FALLBACK_DEAD`).

So the Sump's fuel is exactly the Jawa kind: a dead machine somebody else abandoned in the worst place on the
planet, coaxed back to half speed with scrap, dribbling chemfuel out of its joints while the Empire's clock runs.
The other two routes are his as well. **Buying** it from the Junker stations, where the campaign places one. And
**carrying the tar away**: the liquids design's tanker raid (hose from the shore to a tank aboard, a stolen pump,
*"undeploy, fly away rich. Raid pressure = time on the ground while pumping"*), with the Sump named in its notes as
the place to *"fly to that tar lake"*. The hardware is FlowWorks'; nothing in the Sump's sources says it has run.

His fuel answer of 2026-11-19 makes the Sump one of the three richer sources, with the Abyss and the Fever Wood:
the found refinery on an inexhaustible pool is its fuel in 0.1.0. It stays slow by his word of 2026-09-07, and the
answer sets only that a crew can plan a stop around it.

**What the place does to the ship (his ruling of 2026-11-18, in 0.1.0).** It tars it. Every source agrees that the
tar *"gets on everything"* (the nastiness ruling of 2026-09-24): boots carry it up the ramp and across the decks, a
belch throws it *"out all over the local terrain"* and the hull is local terrain, and a woken beast lays shallow
tar on every cell it crosses. Tar is flammable. So the Sump's wear on the ship is **fouling**: a tarred hull and
tarred decks are slow, filthy, and one stray fire from being alight. The answers are already in the sources and
both are hands-on: **solvent**, scrubbed on by the crew (the same weak acid that cleans people), and **glasswalk**,
the poured bitumen deck that *"never fouls, never needs cleaning"* and is one of the owner's two named ship gifts
from this biome. The cold is ordinary cold and wears on nothing. What is not built: any effect of tar on the hull
itself (today tar coats terrain and people, and the ship's floor is terrain). The promise below is written for the
decks and the ground the ship stands on, and marks the hull skin as owed.

**This wear is a proposal, flagged as one.** No Sump source names a hull wear. The sources name tar on everything
and tar that burns; applying them to the hull is this design's reading, and his to confirm. The frame it would sit
in exists: `src/RimUtinni/ShipShields/` (his eight shield rulings of 2026-09-02,
`design/Jawa/proposals/ship_shields_deep_design.md`), where `ShieldHazardExposureTracker` wears the ship's own
structures while the map holds a hazard the fitted field does not cover and `ShieldLandingAdvisory` warns once on
landing and never refuses. Nothing new is designed here. What the Sump needs from that frame is one declared wear
of the kind `biome_shared_machinery_2026-11-18.md` calls "the ground under the hull", with solvent and glasswalk
named as its answers. No field is an answer, by his own ruling in that document: *"Slow pressing things move
through all shields ... This is why nothing 'holds out water,' it just doesn't work that way."* Tar is the slowest
pressing thing on the planet. The two built hazards the tracker can already see do not fire here: the Sump is cold
but nowhere near forty below, and its weather carries no sand.

One sourced line runs the other way and belongs beside this. The tar-pits proposal lists pitch as a reagent for
*"roofing seal, Utinni hull patching"*. The stuff that fouls the hull is also what a Jawa patches it with.

---

## The first minutes

From the air there is nothing to see but one long flat darkness with a glow along its edge, and, if a station is
near, a few warm points of lamplight. The sheet's sound for the place carries in the cold: *"derrick-creak and
pump-thud carrying miles"*.

The ship has to come down on the solid ground between the pools: the cracked ash-dark pan and the cooled sheets the
sheet calls the glass reaches, *"walkable, faintly shining, mouse-tracked"*. It cannot tell from above which pale
crust is cooled glass and which is a skin over soft deep tar. The mice can.

The ramp comes down into dusk that will never get lighter. Out on the black, lines of tiny pale things on
*"absurdly broad star-feet"* are running across the pools as if they were pavement, *"always mid-dash, always in a
LINE"*. In one place the lines bend around a patch of tar that looks like every other patch.

The owner asked for a letter here, and the first pass recommended dropping it without knowing the idea was his
(2026-09-24, typed: *"I'm wondering if the narrator should announce each biome when the ship lands to give some
hints."*). It fires once, at the first landing, and its ruled content is three reads: *"watch the mice — where the
lines bend, the tar lies; an unbroken pale crust no line touches is a lie; a soffeth ring means gas below."* It
stays. It must not promise a sign that is not built yet (see Scope).

The mice themselves are stranger than the word. His note on their art, 2026-10-05: *"Great idea and I love the huge
paws, but make it less mouse-like and more alien please. Can still call it a sump mouse."*

Before the first hour is out the player should have seen three things without going looking: a line of sump-mice
crossing open tar; a crew member walk through a shallow margin and come out black to the knee and slower; and
black footprints going up the ramp.

## The first day

- **It gets on everything.** Crossing raw tar slows and dirties whoever crosses it, and the tar comes home with
  them: onto ordinary floors, onto the decks, onto the next thing they carry. The crew does not get clean here.
  The owner's answer of 2026-11-10 sets the routine: *"workers clean and retrieve food from tar on their own; he
  plans routes, chooses dig sites and spends scarce solvent. The colony stays dirty."* A tarred crew member is
  slower at walking and at work, and from the second stage of the condition is easier to set alight. A fouled
  floor is slower to cross than a clean one, which is what the decks become. None of it costs a Jawa any mood.
- **Solvent is the currency.** The cleaner is a weak acid, and cleaning works by turning tar into green gas. The
  local acid renders from seepwax, and seepwax comes out of the warm hives under the tar (see the mound, below).
  The owner ruled the supply generous: *"one raid should give you a lot. Not meant as a starvation mechanism."*
- **Routes.** Deep tar is a wall to anything on feet. Shallow tar is a toll. Cooled glass is free. Poured
  **glasswalk** is the crew's own cooled glass: it never fouls and never needs scrubbing, and nobody ever walks it
  at full speed. The owner's seed, typed: *"resistant to the tar but ... slippery so you can't walk full speed ever
  but don't have to clean them anymore."*
- **Reading the mice.** Mice cross tar freely except where they will not. A stretch they detour around is something
  under the surface. A pale crust with no gnawed edges and no mouse on it is the pallick, the one lying plant: a
  skin grown over soft tar that fails under a walker. It mires and hurts and never kills outright (*"the tar takes
  slowly"*), *"and the mice always tell the truth about it."* The kit spec's rule for all of this: *"The telegraph
  is emergent and diegetic: no overlay, no alert, no UI — the player who looks sees the gap in the tracery, and the
  player who doesn't learns like the Junkers did."*
- **Reading the plants.** The flora roster's line: *"The flora is also the biome's index: what grows where tells
  you where the tar is shallow, where it breathes, where it is holding something, and where it is lying."* Skelver
  arcs along a pool edge and never grows away from black. Mirrelin, the pale lace the mice graze, grows only on
  cooled glass, *"a quiet promise the ground holds"*. Soffeth, a loose ring of soft grey bladder-stalks, grows only
  where the tar breathes: gas below, so *"don't dig here, don't pour a moat here, don't ground a lamp here."* The
  stalks *"nod when a bubble passes below — the only plant here that moves."*
- **Nothing to drink.** There is no water terrain and no rain. The crew drinks what the ship carried. Animals
  brought from elsewhere cannot drink here at all and show it; the natives drink tar.
- **The margin ring.** Skelver rosettes to forage, korveth shrubs swelling into black pitch nodules (*"a plant
  growing its own coal"*), and, rarely, lanneth, dark stalks hung with amber pods, the Sump's one sweet thing.
- *(0.2.0, by his card of 2026-11-20)* **The first dig.** A bowed white bell on a bare black stem, alone: the tolleth, *"the grave-bloom"*, which grows
  only where the tar is holding something. The crew sinks a shaft there. Jawa do not need to be told twice.

## The first week

- *(0.2.0)* **The dig lottery.** *"Every dig is treasure or a click."* The shaft pays by depth: junk and bitumen, then bones
  and hides *"of ages the bestiary never named"*, then sunken machines and sealed casings. And traps, which by the
  owner's ruling come up **more often** than anything of the people who set them, *"preserved in perfect working
  order"*: *"The tar preserves everything, including intentions."* A trap clicks before it fires. The owner's
  answer of 2026-11-10 fixes what the click buys: time *"to clear workers and to fetch a qualified miner from a
  nearby site; a distant one may not arrive in time."* Deeper strata pay better and click more. What the table
  should pay is also his, from 2026-09-02, and the first pass never saw it: *"Superb! The loot table is the fun
  part. Draw from fossils but also sealed alien eggs, technology, dead bodies with equipment intact, and story-rich
  objects. And of course Assailant and Forgotten Arsenal aspects."* The proposal he was answering adds the two
  finds that make a Jawa's hands shake. A machine the tar kept working: *"functional or near-functional rather than
  the corroded husk everything else on this world arrives in"*. And a moment, not a thing: *"The tar preserves the
  moment, not just the remains"*, a great carcass *"frozen mid-motion — limbs splayed as if still struggling,
  sometimes a second skeleton locked in its jaws, sometimes wrapped around ancient machinery it died reaching
  for."* A disarmed trap is a prize in its own right (his card of 2026-09-12: *"high skill gate, failure
  detonates"*; the kit calls the result *"a skill-priced"* find). And what comes out of wild tar belongs to nobody:
  the proposal calls unclaimed pits *"one of the few genuinely no-provenance-risk salvage sources on the planet"*.
- **The Deep Black.** One landmark on every Sump map: an unbroken mere of deep tar a few hundred cells across with
  a shallow rim, ruled by card on 2026-09-24 as *"beast country, undiggable from shore, the biome's 'ocean' at map
  scale"*. It is where the bulge is likeliest to be, and it is the one tar source that never runs out. (Built.)
- **The dead refinery.** Somewhere beside the tar is what is left of a tar-cracking works: *"split casings, seized
  valves, nothing running."* See Fuel, above. For this crew it is the first thing on the map worth more than
  whatever they came for.
- **The mound.** A low warm mound at the tar's edge with a plated head planted in its mouth. Thrummels are round,
  furred, soot-dark and harmless one at a time; the warden is *"dangerous AT the mound, indifferent a step away"*;
  the pale broodmother underneath is the wax. Raiding a mound is how a crew gets solvent, and it is *"a deliberate,
  priced choice"*. (Built as plain animals; the mound that defends a radius is not built, and until it is the wax
  comes from hunting the broodmother.)
- **The belch.** Without warning a pit *"just belches a huge amount of tar out all over the local terrain"* (the
  owner's own event, typed 2026-09-24). What was a clean route at breakfast is shallow tar at noon, and whatever
  stood there is coated. It is built as a real flood through FlowWorks, not a splash: by his cards of 2026-09-24
  it is the only way the map gains tar (*"No slow-drown background pressure"*), and its front cools to walkable
  glass, so *"every belch rewrites the map, and natural glass is the process the glasswalk imitates."* Within hours
  the mice avoid the fresh crust; within a day a soffeth ring starts at the new edge (*"The literacy game stays true
  after every belch"*). His first word on the event, 2026-09-02, when it was still called a geyser, asked for
  company: *"Superb vile shock. Add creatures that consume tar too and run towards these events/moments. Able to
  [move] through the tar easily unlike trapped creatures. They may like to eat tar-encrusted pawns too."* The
  gulveth is the tar-eater that was later built. Running to a belch, and taking an interest in a tarred Jawa, is
  not built and is owed to that sentence.
- **The thing wearing the salvage.** Something boneless lives on the tar's surface and picks up loose rigid things
  (dropped weapons, slag, components, scrap) and wears them. See the moments, below.
- **The bulge.** Somewhere out in the black is one wrong smooth swell. The mice bend around it. The sheet's sound
  for it: *"underfoot, rarely, a bubble the size of a room, rising slowly."* It is asleep. Explosions wake it.
  Building too close wakes it. Digging too deep wakes it.
- **The beast, if they wake it.** It does not hunt and it cannot be fought. It moves at about a tenth of a walking
  pace toward the densest cluster of built things on the map, and on this map that is the ship and the crew's
  yard. Anyone who stands in its way is shoved aside (*"a stagger, not a bite"*). Every cell it crosses becomes
  tar. Everything built that it reaches is swallowed, with a mound left behind
  and a letter naming what was taken. The owner's answer of 2026-11-10 on what an evacuation saves: *"People and
  chosen goods: everyone escapes and he picks which valuable stores to carry; buildings are lost."* For a ship
  crew that is the campaign's own loop with a slow black clock on it: choose what comes aboard, and lift. When
  it has eaten enough it sinks back at a new address, and the kit spec's card of 2026-09-12 says why: *"the map
  heals, the mouse-lines redraw, no player is ever taught to farm it."*

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The footprints.** *On screen:* one Jawa takes the short way across a shallow margin, comes out black and slow,
   and a line of black prints follows it up the ramp, along the deck and onto the bunk. *Why it is funny:* by the
   third day the inside of the ship is the same colour as the outside.
2. **The mice turn.** *On screen:* a line of pale mice running flat out across open tar swerves as one around
   nothing at all. *Why it is alarming:* the player has just queued a dig on the far side of it.
3. **The false floor.** *On screen:* a crew member steps onto a pale, perfect, ungnawed crust and goes through it
   to the waist, mired and hurt; a second one has to haul the first out onto real glass. No mouse was on that
   crust, and the player can see that now.
4. **The click (0.2.0).** *On screen:* a dig shaft, a sound, a pause letter, and every Jawa on the map running in a
   different direction while one miner runs the other way, toward it.
5. **The kethrel.** *On screen:* a glossy shapeless animal comes off the tar wearing a carapace of somebody's
   blasters, slag and components, clanking, and settles near the crew's salvage pile to add to it. A handler coaxes
   a molt and the whole hoard drops in a heap; a clumsy one gets a panicked charge from an animal dressed in scrap
   metal. *Why it lands:* it is the only creature on Ash'karr that collects junk the way the crew does, and the
   crew wants what it is wearing.
6. **The stilts.** *On screen:* a crane-sized dark flier folds out of the dusk onto four *"absurd spike-tipped
   stilts"* and *"simply keeps walking"*, out across the open tar where nothing else its size can follow; the
   mouse-lines under its shadow break and scatter.
7. **The small bulge.** *On screen:* a smooth swell at the margin, a little too small to be the beast, opens along
   a seam and takes a mouse (or a hand). The owner ruled that the skarrid may mimic the bulge, *"smaller and subtly
   wrong"*: the false alarm is the biome teaching.
8. **The belch.** *On screen:* a pool heaves and throws a sheet of tar across the yard, the crates and one side of
   the ship.
9. **The bubble.** *On screen:* a slow ring of filth spreading on a still pool for a day, a sound from under the
   ground, and then the mice running outward from the bulge.
10. **The beast.** *On screen:* a low glossy mound the size of a building, no clear head, tar sheeting off it,
    crossing the map toward the ship more slowly than anyone can walk, and a small crew carrying everything
    they own up the ramp in front of it.
11. **The tar-eaters come running** (owed to his words of 2026-09-02; not built). *On screen:* a pit belches, and
    every gulveth in sight turns and wades toward the mess at a barge's full speed, straight through tar that
    would hold anything else, and one of them stops to investigate the Jawa who was standing too close and is now
    the same colour as lunch.
12. **The thing that died reaching** (0.2.0; owed; the table pays placeholder salvage today). *On screen:* the shaft
    opens on a carcass the size of the ship's bridge, limbs still spread, wrapped around a machine. The machine's
    lights come on.
13. **The dead refinery wakes.** *On screen:* a split column patched with hull plate shudders, and black tar goes
    in one end and something thin and gold drips out of every joint except the one with the bucket under it.
14. **The plant that nods.** *On screen:* a ring of grey bladder-stalks at a seep all bow at once, then the next
    ring over, then the next, in a line pointing at the ship.

## When the Empire arrives

The sheet's third driving force is the owner's own: *"The tar defends ... wonderfully, twice — nothing crosses it
willingly, and it can be lit into a terrible smoky horror nothing can cross."*

- **Nobody can see.** Watchers see a target in the dark only from six cells. An Imperial probe or spotter crossing
  the Sump has to come almost within arm's reach of an unlit crew to report it. Every lamp, fire and lit doorway
  the crew allows itself is a beacon in a country with no other lights.
- **The tar does not care whose boots.** Troopers who cross shallow tar are slowed and filthy; deep tar turns
  them; the false floor takes whoever steps on it. What a mired or dead trooper drops near the tar is the
  kethrel's by morning, and the crew's after the next molt.
- **Ordinary fire is already a weapon, and it does not go out.** Tar burns as a slow creeping front along
  connected liquid and stops at a shut sluice (built 2026-11-03; its live proof failed on 2026-11-04 and no pass
  is recorded since). The shared fire code's own note is that *"a limitless source burns forever"*, and here
  nothing rains. A firefight at the edge of the mere can light the mere, and a lit mere is a beacon for the rest
  of the stop. His word on what the burn is like, 2026-09-02: *"Not kill outright, just burns like normal fire.
  But yes, toxic thick smoke that obscures and produces coughing and stinging eyes and stink."*
- **The tar can be sent.** Channels and gates for tar are built in FlowWorks, and his card of 2026-09-24 lists
  the use: *"drain a dig claim, feed the moat and refinery, flood a raider approach on command."* On raiders and
  tar his 2026-09-02 note is the rule: *"Pawns with goals inside a region make the call to go across it, while if
  there's any way around it they do so."*
- *0.2.0:* **the poured moat and the fuse post.** A perimeter of tar laid like flooring, lit on command into *"a
  long-burning wall of flame and smoke that blocks sight and passage"*. It is spent when it has burned (*"burnt tar
  is spent tar"*), it ends every hope of staying hidden, and it is exactly what a small crew that cannot win a
  fight wants between itself and a strike team while it loads the ship.
- *0.2.0:* **the capstan.** A fixed turret that ropes one visible target and reels it in along the ground, through
  whatever lies between, which here is tar. It also reels in a downed crew member. (His words: *"if that mechanic
  is attached to a turret, it makes complete sense and is awesome."*)
- *0.2.0:* **the solvent wake.** His words: *"Throwing solvent into the pit should INSTANTLY wake the beast in
  Manhunter."* Ruled a deliberate weapon, *"a scorched-earth last resort"*. The first pass described this wrongly.
  A beast woken this way does not crawl to buildings: the build item's words are that it *"hunts every pawn on the
  map, colonists included"*, with no day of warning (*"the pour is the warning"*) and a confirmation that says so.
  Under the lens it is still the parting shot, but only for a crew that pours and is aboard and lifting before it
  surfaces. Everyone left on the ground, troopers and stragglers alike, is prey.

## Who else attacks; who hates the Empire

- **Almost nothing attacks.** The roster has no pursuit predator by design (*"the tar defends; nothing crosses it
  willingly"*). The skarrid ambushes at the margin and never chases; the warden bites at its mound; the skellarn is
  dangerous only cornered. The danger in the Sump is the ground and what the crew does to it.
- **What comes out of the deep strata.** By the owner's ruling, a dig wakes *"only truly ancient machines or
  assailants. No normal life can survive otherwise."* Never a whole Assailant or Rakatan: partial remains, and
  their traps.
- **Who is here.** The Junker stations, where the campaign places them: *"the biome's only industry, law, and
  light"*. The owner's notes for the later inhabited pass add Jawa, deep tribes and Black Star as the factions
  that belong in a place this dirty, with *"old ruins of tar gathering expeditions. Attempts at refineries. Some
  rather miserable moisture farmers trying a go at it."* None of them is placed by this biome. Whether any of them
  fights the Empire is `UNSETTLED`. They are where the crew trades: solvent, barrels, fuel, dig finds.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The water the ship carried running low, with nothing on the map to refill it.
- A woken beast walking toward the ship.
- *(0.2.0)* A deep stratum that clicked and was not answered in time.
- Solvent gone, the crew slowed to a crawl and the decks black.
- A pool that caught fire and will not go out.

**Stay, longer than the Empire would like:**
- The dusk and the fog: an unlit crew is seen only from six cells, and the search from orbit runs one step slow,
  two on a fully dark tile.
- Tar between the ship and anything walking toward it.
- Nothing here grows over the ship, floods it or freezes it. A careful crew that stays out of the deep strata can
  sit in the dark for as long as its water lasts.
- *Later:* the Sinking. His ruling of 2026-10-02: one thing of value thrown into the tar *"pushes the next Imperial
  probe or raid away x5"*, and other parties' ownership claims on what the crew keeps go down with it. It is the
  most direct answer any biome has to "what helps them stay", and it is a rite, and he tabled the rites on
  2026-10-03. It stays tabled (`Answered on 2026-11-19` 1).

## What the crew takes away

- *(0.2.0)* **Dig finds:** old bones and hides, sunken machines, sealed casings, partial remains of the old wars.
- **Bitumen and pitch,** for sealing, glue and paving, and **glasswalk for the ship's own decks** (his named gift).
- **Fuel,** cracked from tar at the found refinery or bought from Junkers (see the clock section).
- **Solvent and seepwax.** The acid that cleans tar also cleans it anywhere else the crew meets it.
- **Tar-cured hide and glassy black leather,** thrummel chitin, skellarn leg-spines *"prized for awls"*.
- **A cage of sump-mice.** The owner ruled them tameable, cheap and easy: *"a living tar-detector a caravan
  carries."*
- **Whatever the kethrel was wearing.**
- **A disarmed trap** of the old wars, intact.
- **A barrel of tar.** His note on the cuisine proposal's preservation row: *"now we know why we want to go to the
  salt flats, or the tar pits, or sand dunes. Let's make everything salvageable commodities! The ship should be
  absolutely full of weird stuff. I love the idea of piles of sand in a box, or a barrel of tar."* Tar by the
  barrel is a built item. With a tank and a hose it is tar by the hold (the tanker raid; see Fuel).
- **Chemfuel,** as much as the dead refinery gave up before the crew had to go.
- *0.2.0:* the capstan, learned by studying two preserved draw-joints from the strata and buildable anywhere after;
  the tar vault as a larder aboard; gaslight lamps and flame statues for the decks; the salvage winch, which was
  filed as *"a tow line on the ship"* (it drags wrecks, carcasses or a downed beast *"home to a capstan or the
  ship"*); and, with Cold Storage, food sealed under pitch that ages into the best ingredient in that line.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Crossing raw tar slows and dirties a walker, and the tar travels with them onto floors and decks. | One pawn crosses shallow tar and walks up the ramp; one walks round on solid ground. | The clean walker's deck stays clean. Deep tar turns a ground walker back; nobody is deleted by it. |
| Solvent scrubbing really removes tar, from the person and from what they carry, without the player ordering each scrub. | A tarred crew with reachable weak solvent and Cleaning enabled; then the same with the solvent forbidden. | A scrub that clears the health label while the carried tar puts it straight back is a failure. |
| Glasswalk never fouls and is never walked at full speed. | A dirty walker on glasswalk, on ordinary floor and on bare pan. | Glasswalk does not clean the walker's boots. |
| Sump-mice cross tar freely and bend around what is under it. | A map with a dormant bulge and open pools; watch the lines. | Remove the bulge: the lines straighten. |
| The pallick fails under a walker, mires and hurts and does not kill; mice never cross it. | A pawn walks onto pallick and onto mirrelin crust beside it; a helper stands by. | Mirrelin holds. A mouse routed at the pallick goes around. |
| The skellarn really flies, lands, and walks the open tar. | A skellarn over a pool with mice on it (flight read from its flight state, never from a screenshot). | It is not mired where a pawn would be. |
| An unlit crew in the dusk is not seen by a watcher beyond a few cells; a lit one is. | A probe passes an unlit camp and a lamplit camp at the same distance. | The same pass on a daylit map sees both. |
| Native plants grow with no sun and no sunlamp, and nothing native glows. | Skelver, korveth and lanneth growing through the visit. | A plant from elsewhere planted beside them does not grow. |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19; the dig's row by his
card of 2026-11-20):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A dormant bulge wakes by cause, with signs first, and the woken beast is slow, unfightable, goes for built things and leaves a mound and a letter for each one taken. | Wake one by a deep dig with the ship's yard built at a distance; load and launch ahead of it. | Shooting it changes nothing that matters. Nothing it takes disappears without a mound. It sinks back and is a bulge again. |
| The kethrel picks up loose scrap near the tar, wears it in visible stages, and gives every piece back on molt or death. | Scrap left by a pool; a kethrel loads; a handler coaxes a molt. | The dropped things are the same things, counted. |
| A belch coats ground, goods and decks near a pit, and solvent or glasswalk answers it. | Trigger a belch beside a stockpile and the ship's ramp. | Glasswalk under the splash takes no deposit. |
| A dig pays by depth and sometimes clicks; the click gives time to clear the site and for a nearby miner to answer it. | A shaft worked through several strata with a miner near and with one far. | A stratum table with no trap row would pass a lazy check: the scene must see a click and both outcomes. No whole Assailant or Rakatan ever comes up. |

Settings: one switch per major feature, defaults as shipped, everything off leaves a cold dark flat with black
ground (standing rule, every mod).

## Shared machinery

**Featured here** (the Sump is where each is vital and should be proven):
- **Stuff that gets on you and comes home with you** (the tar coating, the carried-filth link and the tarred
  condition, in `EnvironmentalHazards`; solvents in `TheSump`). Any biome with a sticky hazard can use it; only
  here is it the whole day.
- **Animals whose avoidance is a map** (`RM_MapComponent_DreadField`, `RM_JobGiver_DreadAvoidWander`,
  `RM_CompFilthTrail`): mice bend around dread sources and leave a trail that shows it.
- **Work that rolls on a table and can roll a trap** (`RM_CompWorkedLottery`, `RM_LotteryTableDef`): the dig, 0.2.0. Any
  excavation, salvage or wreck-stripping elsewhere can use the same table.
- **A dormant set-piece that wakes by cause and eats buildings** (`RUT_BeastBulge`, `RM_CompBeastWakeRelay`,
  `RM_CompStationEater`, `RM_TarBeast`). The third of the Patient family, with the sarlacc and the Fever Wood's
  deep thing: *"huge, buried, patient feeders ... unmoving until they do."*
- **An animal that carries real items as armour** (`RM_Kethrel`).
- **Darkness as cover from watchers** (already in the pursuit code; the Abyss features a thicker version of it).

**Merely active here:** liquids, channels, burning and cooling (`FlowWorks`: the tar is one of its liquids, and its
cooled front is the glasswalk); the weather lock and the dusk (`EnvironmentalHazards`, with the sun's angle coming
from the tile's place on the planet: the one sun from geometry, which here is simply below the horizon); thirst and
carried water (`FlowWorks`); the tether pull the capstan shares with the Webwork's traction lance
(`CreatureBehaviors`); real flight; bones from butchery; wreck salvage; ownership claims (`RimProperty`, which the
Sinking would use); flame statues (`FlameStatues`); the acoustic scanner's readings; the Empire's search and the
visibility dial.

## Scope

Every feature is in one bucket.

**The one signature (his card of 2026-11-20): the tar's burden.** Crossing raw tar slows and dirties a walker and
travels onto floors and decks; solvent, scrubbing and glasswalk answer it; the sump-mice and the honest plants show
where the tar is safe. *Why a normal stop is sure to see it:* the ship lands on the black and the crew's first walk
is across tar. He picked **Tar burden** with this description: *"Why: every stop sees it, since the crew's first walk is across tar. Buys: it is already built, bar one scrubbing
defect. Costs: the dig moves to 0.2.0, so the "hides all" half of your line is not playable yet. Recommended: it
passes your 'a stop must see it' test and is nearly done."*
His experience line is *"The sump hides all and makes you fight it for every action."* The fight is in 0.1.0; the
"hides all" half, the dig, is in 0.2.0. The dormant bulge and its beast, the kethrel and the belch were extras and
are in 0.2.0 since 2026-11-19.

**0.1.0, the stop**
- The land: permanent dry dusk, deep and shallow tar, cooled glass reaches, the pan, the margin ring of
  chemotrophs. (built)
- Tar on everyone and everything, the tarred condition, weak solvent from seepwax, automatic scrubbing, ordinary
  floors that foul and glasswalk that does not. (built; a live run found the scrub leaving the condition in place,
  which is a defect to fix, not a scope question)
- Sump-mice as the instrument; the pallick's false floor; the tolleth and soffeth as honest signs. (mouse-lines
  built; the pallick is built as a plant but its collapse and the mice's avoidance of it are not; placing the sign
  plants on the right cells is not built either. All three are owed, and without them the mice are scenery.)
- The Deep Black mere. (built; it had no line on this page)
- The first-landing letter, with text that names only signs that work. (built; his idea)
- The wrecked tar refinery, found and kludged back. (built in FlowWorks, never run for the Sump)
- The cast: sump-mouse, gulveth, the three thrummels as plain animals, dredgel, skarrid, skellarn with real flight.
  (built)
- The margin's goods: skelver, korveth pitch, bitumen, seepwax, hides, lanneth. (built)
- Dusk as cover from the Empire's watchers, and cover from orbit: fog one step, a fully dark tile one more. (the
  first is built in the pursuit code; the second is the small build his ruling asks for)
- Chemfuel from tar at the found refinery. (built, unproven; this replaces the first pass's "rendering bench",
  which nothing in the sources asks for)
- Owed and small, found by reading the build notes to the end: mouse tracks build up over days and fade in about a week, so a map the ship has just
  landed on shows the mice and no tracery, and the tracks need laying down when the map is made; mice and the
  grounded skellarn have no built way to cross tar yet.
- Tar fouling of the ship's decks and standing ground, answered by solvent and glasswalk. (the decks are built by
  being floor; the hull skin is owed)

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his card of 2026-11-20 (the tar's burden is the signature); goes back by one move:*
- The dig shaft, the stratum lottery and the click. (built. Most of what the table pays today is placeholder
  salvage: the old bones, hides, casings and machines the sheet promises are still to be authored. Owed with it: the
  click has no sound and no letter today, only a countdown on inspection; an unqualified miner can be sent to disarm
  automatically, which his answer of 2026-11-10 makes a defect.)
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The dormant bulge, its warning signs, and the station-eating beast that is evacuated ahead of. (the bulge, the
  wake causes and the beast are built offline; the day-ahead warning, the bubble and the ring, was not found in
  source and is owed. Moved in.)
- The kethrel: pickup, the scrap shell in stages, the molt. (built; moved in)
- The belch, as a real tar flood whose front cools to glass, and the slow responders after it (fresh crust the
  mice avoid, a soffeth ring at the new edge). (Second reader: the incident is built as a flood in
  `RM_IncidentWorker_TarPitBelch.cs`, not as the splash this page said, and the responders are built and passed one
  live check on 2026-11-06. Two defects are on file: the glass edge may not be written on cells the depth engine
  owns, and the responder looks for a glass terrain the Sump's cooling no longer produces. Both moved in from
  0.2.0 and "later", because a belch that rewrites the ground without the signs catching up would make the mice
  lie.)
*Already here before that answer:*
- The poured moat, the fuse post and the smoke wall; fire that runs along connected tar and stops at a gate. By
  his ruling of 2026-09-12 a lit moat does catch the natural pools beside it, with the build note that the cascade
  stay *"survivable-by-foresight ... no silent map-wipe"*. (moat and post built; nothing today makes the promised
  impassable smoke wall or its column; network fire and the sluice firebreak were built on 2026-11-03, failed
  their live proof the next day, and have no recorded pass; the fuse post's own ignition does not honour gates)
- Tar channels and gates used on purpose: draining a dig, feeding the refinery, flooding an approach. (built,
  shared; active here from the first day whether or not anyone promises it)
- The tanker raid: hose, pump and ship tank. (FlowWorks hardware; `Answered on 2026-11-19` 6)
- Tar-eaters that run to a belch and nose at tarred people. (not built; his words of 2026-09-02)
- The capstan turret, its rescue pull, and learning it from two preserved draw-joints; the salvage winch. (built)
- The solvent wake as a weapon. (built)
- The thrummel mound that defends a radius. (not built)
- The tar vault, with solvent-gated extraction, on the ground and as a larder aboard. (built)
- Gaslight: tar and acid make green gas, the warbling lamp, natural seep flames that teach it, flame statues.
  (lamp and gas built; a live run found the scrub making no gas; the natural flames are not built)
- The dredgel parking on dug ground as a prospecting hint. (not built)
- The ship's acoustic scanner readings here. (built)

**Later (a crew that stays, a colony, or the campaign layer)**
- The two tar rites, the Sinking and Mob'Unloo's Price, with their offerings (the beast sleeps a season, the
  ancient traps fizzle). Tabled with all rites by the owner on 2026-10-03.
- Dorvel as a farmed food crop in tar-beds: slow by his ruling (*"due to the inclination of the sun it wouldn't
  grow very fast"*), so a stop never sees a harvest.
- Duckboards as their own floor (ordinary wood flooring already does their job).
- Junker stations, the ruins of tar expeditions, failed refineries, miserable moisture farmers, the weighted
  factions: the inhabited pass and the campaign layer.
- Re-paving the Ashfall Road (his words: *"this one is about the ship"*).
- Going under. The tar-pits proposal's showcase, which he moved to the first version on 2026-09-02: a held pawn
  that visibly sinks, a rescue that can drag the rescuer in (*"the two-pawn-down trap"*), machines that sink faster
  and corrode. Today deep tar is simply a wall and shallow tar a toll, and the false floor is the only thing that
  holds anyone. Nothing in the later Sump sittings picks this up or drops it; it is listed so it is not lost.
- Tar-sealed and pitch-aged food (with Cold Storage). Built.
- The soundscape the sheet wrote. It is the cheapest large gain in the biome and nothing has built it.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- A fightable tar beast, or one on any raid list (sheet ban; the solvent wake's manhunter state is his one ruled
  exception and is a weapon the player chooses).
- Whole Assailants or Rakatans in the tar; live creatures preserved in it (*"Only truly ancient machines or
  assailants"*).
- Any water terrain, rain, tar rain (ruled out 2026-10-18), sun-driven plant or glowing plant.
- The wick-plant and the brommet. His words on the Sump art sheet of 2026-10-05: the wick, *"cut this no longer
  needed"*; the brommet, *"terrestrial, cut"*.
- A trait that makes anyone enjoy mess (declined 2026-09-24; only the Jawa's immunity stands).
- The lasso as a worn item (*"Remove lasso's from the game, but keep this"*).
- Biome placement scoring, its biome-rarity slider and world mutators (no worldgen, ever).
- The pump rhythm, the buried dragline, the Reckoning of Owners, the first round of tar offerings (not taken).
- **No longer recommended for dropping:** the arrival letter. The first pass and the cleanse both wanted it gone
  for teaching by telling. It was his own idea and his card (2026-09-24). What is wrong with it is only that its
  text names signs that are not built; the text is fixed (`Answered on 2026-11-19` 8).

## NEEDS HIM

None open. Every entry is answered (next section).

No ship idea that he declined or cut was found in the Sump's sources. The nearest things are not ship ideas:
re-paving the Ashfall Road, tar rain, and the mess-lover trait, each listed under Dropped with his words.

Two questions the cleanse put on its owner pages are answered here by scope instead of asked again, and each is a
line under "Scope moves" in `rewrite_choices.md`: the playable "hides all" (the dig), which his card of 2026-11-20
moved to 0.2.0 (`Answered` 11); and
the water problem is not solved, it is the stop's own clock.

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. (scope) **The Sinking, for a ship on the run.** *His ruling:* he tabled every rite, and his ruling of 2026-11-17
   moves rituals *"to the next version if not retired outright"*. Leave it tabled.
2. (hull) **Does the beast swallow the ship?** It goes for the yard and the ship alike, and the ship can always lift
   first (the design's default). This keeps his shield ruling of 2026-09-02: *"no environment is immediately lethal"*.
   Whether a ship set down within twenty cells wakes the bulge is still `UNSETTLED`. *Delegated call.*
3. (other) **Is the scrap the kethrel takes ever the crew's own?** The crew's unguarded outdoor salvage is fair game
   (the design's default). *Delegated call.*
6. (fuel) **The tanker raid, for this crew.** *His ruling:* the move card of 2026-11-18 (*"Move it, list every
   move"*): 0.2.0, with the moat and channels.
7. (hull) **Tar fouling as the hull wear.** Fouling stays in 0.1.0, answered by solvent and glasswalk. The only
   sourced wear (cold) does not bite here, so this is the one exception to "an invented wear waits for 0.2.0".
   *Delegated call.*
8. (other) **The arrival letter.** Keep it, and fix its text (the design's default). *Delegated call.*
9. (other) **Sealed eggs in the dig.** *His ruling:* his typed word of 2026-09-24: *"Only truly ancient machines or
   assailants. No normal life can survive otherwise."* Eggs are loot that never hatch.
10. (other) **The vault as a ship gift.** Keep all three gifts. The vault is marked as an agent's pick, not his (the
   design's default). *Delegated call.*

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

4. **Is the Sump's dusk dark enough to pause the search?** *His card of 2026-11-19 (cover):* nothing pauses it.
   The fog is one step every day; a tile whose measured light is full dark adds one more, and the steps add. A lit
   moat or a lit camp takes them away while it burns. **This changes the design's default in part.** Was: one step
   from dusk and fog together.
5. **Which fuel class is the Sump?** *His card of 2026-11-19 (rich fuel):* a richer source, one of three with the
   Abyss and the Fever Wood. The found refinery on a pool that never runs dry is the Sump's fuel in 0.1.0, slow by
   his word of 2026-09-07.

**Answered by his card of 2026-11-20** (item `RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED`; the
enact item is `RIMMANDRAKE_ENACT_SIGNATURE_PICKS_INTO_DESIGNS_SLIME_KEEPS_FILM`). Each keeps its number.

11. **Which is the Sump's one 0.1.0 signature, the tar's burden or the dig?** It was left unchosen in Scope. *His
    card of 2026-11-20, about 5:45 AM PST:* **Tar burden**: *"Why: every stop sees it, since the crew's first walk is across tar. Buys: it is already built, bar one scrubbing
    defect. Costs: the dig moves to 0.2.0, so the "hides all" half of your line is not playable yet. Recommended: it
    passes your 'a stop must see it' test and is nearly done."*
    The dig moves to 0.2.0 with its row.
