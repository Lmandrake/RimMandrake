# The Sump: the design, seen from the ship

**Status:** the one design document for the Sump biome (`RM_TheSump`, source `src/RimMandrake/TheSump/`), rewritten
2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the frozen
definition sheet, the two rosters, the kit spec, the bedazzle review and the cleanse proposal as the place to read;
what happened to every idea in them is in `design/concepts/TheSump/rewrite_choices.md`. Nothing has been deleted
yet. This is a design document only and it launches nothing.

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

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28: *"around every 5-8 days, keep 'em running"*; ladder in
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked provisional): a probe
droid five to eight days after landing, then scouts with a spotter, a strike team, an ion cordon on the ship, a
breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if the one before
succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last (the outer edge, by his ruling of 2026-11-18).** By the pursuit rules: a first week
nearly free of the Empire, a first fight in the second or third week, nothing past about a month. The Sump stretches
that as far as any open ground on the planet can, for two reasons that are already built. The watchers must *see*
the crew or the ship, and a target standing in darkness is seen only from six cells instead of twenty-six
(`EmpireLadderMath.Sees`); the Sump is permanent dusk, so an unlit crew is nearly invisible at ground level and
every lamp it lights is a choice. And nothing here grows, floods or closes in on a schedule: the tar is patient.
That is the outer edge, not the usual stay. What actually ends most stops is on the crew's side of the ledger: the
water it brought, the solvent it can make, and whether somebody dug one stratum too deep.

**Cover from orbit (his ruling of 2026-11-18: partial cover, by biome).** The Sump has no canopy and no steam. It
has the dusk, with the sun held about ten degrees under the horizon. That is deep twilight, not full dark, so this
design gives the Sump **one step of cover** (the search from orbit runs one step slower) and not the pause that
true night earns. Two things throw it away at once: a lit moat, whose smoke column the sheet calls *"visible for a
day's travel"*, and a lit-up camp. (The other reading, that the Sump's dusk counts as full dark and pauses the
search outright, is listed in `rewrite_choices.md`.)

**Fuel (his ruling of 2026-11-18).** The Sump is one of the **richer sources**, and the source is the tar. The
built research project "tar rendering" says so in its own description: *"waterproofing, adhesive, road-metal,
fuel"*; the sheet lists bitumen as torch-fuel; and the Junker stations pump and barrel the stuff as the biome's only
industry. Rendering barrelled tar into ship fuel is **not built** (the research is marked *"unwired flavor tech"*),
and it is the small build this ruling asks of this biome. It should be slow, filthy bench work that needs solvent
to keep the bench hands working, so the richer source is paid for in the Sump's own coin. Fuel can also be
**bought** at a Junker station where the campaign places one, which is the intended way: haggling for barrels with
people who smell worse than the crew does. The Sump is not replete: nothing here is fuel until somebody has
rendered it.

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

Before the first hour is out the player should have seen three things without going looking: a line of sump-mice
crossing open tar; a crew member walk through a shallow margin and come out black to the knee and slower; and
black footprints going up the ramp.

## The first day

- **It gets on everything.** Crossing raw tar slows and dirties whoever crosses it, and the tar comes home with
  them: onto ordinary floors, onto the decks, onto the next thing they carry. The crew does not get clean here.
  The owner's answer of 2026-11-10 sets the routine: *"workers clean and retrieve food from tar on their own; he
  plans routes, chooses dig sites and spends scarce solvent. The colony stays dirty."*
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
  slowly"*), *"and the mice always tell the truth about it."*
- **Nothing to drink.** There is no water terrain and no rain. The crew drinks what the ship carried. Animals
  brought from elsewhere cannot drink here at all and show it; the natives drink tar.
- **The margin ring.** Skelver rosettes to forage, korveth shrubs swelling into black pitch nodules (*"a plant
  growing its own coal"*), and, rarely, lanneth, dark stalks hung with amber pods, the Sump's one sweet thing.
- **The first dig.** A bowed white bell on a bare black stem, alone: the tolleth, *"the grave-bloom"*, which grows
  only where the tar is holding something. The crew sinks a shaft there. Jawa do not need to be told twice.

## The first week

- **The dig lottery.** *"Every dig is treasure or a click."* The shaft pays by depth: junk and bitumen, then bones
  and hides *"of ages the bestiary never named"*, then sunken machines and sealed casings. And traps, which by the
  owner's ruling come up **more often** than anything of the people who set them, *"preserved in perfect working
  order"*: *"The tar preserves everything, including intentions."* A trap clicks before it fires. The owner's
  answer of 2026-11-10 fixes what the click buys: time *"to clear workers and to fetch a qualified miner from a
  nearby site; a distant one may not arrive in time."* Deeper strata pay better and click more.
- **The mound.** A low warm mound at the tar's edge with a plated head planted in its mouth. Thrummels are round,
  furred, soot-dark and harmless one at a time; the warden is *"dangerous AT the mound, indifferent a step away"*;
  the pale broodmother underneath is the wax. Raiding a mound is how a crew gets solvent, and it is *"a deliberate,
  priced choice"*. (Built as plain animals; the mound that defends a radius is not built, and until it is the wax
  comes from hunting the broodmother.)
- **The belch.** Without warning a pit *"just belches a huge amount of tar out all over the local terrain"* (the
  owner's own event, typed 2026-09-24). What was a clean route at breakfast is shallow tar at noon, and whatever
  stood there is coated.
- **The thing wearing the salvage.** Something boneless lives on the tar's surface and picks up loose rigid things
  (dropped weapons, slag, components, scrap) and wears them. See the moments, below.
- **The bulge.** Somewhere out in the black is one wrong smooth swell. The mice bend around it. The sheet's sound
  for it: *"underfoot, rarely, a bubble the size of a room, rising slowly."* It is asleep. Explosions wake it.
  Building too close wakes it. Digging too deep wakes it.
- **The beast, if they wake it.** It does not hunt and it cannot be fought. It moves at about a tenth of a walking
  pace toward the densest cluster of built things on the map, and on this map that is the ship and the crew's
  yard. Every cell it crosses becomes tar. Everything built that it reaches is swallowed, with a mound left behind
  and a letter naming what was taken. The owner's answer of 2026-11-10 on what an evacuation saves: *"People and
  chosen goods: everyone escapes and he picks which valuable stores to carry; buildings are lost."* For a ship
  crew that is the campaign's own loop with a slow black clock on it: choose what comes aboard, and lift.

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
4. **The click.** *On screen:* a dig shaft, a sound, a pause letter, and every Jawa on the map running in a
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

## When the Empire arrives

The sheet's third driving force is the owner's own: *"The tar defends ... wonderfully, twice — nothing crosses it
willingly, and it can be lit into a terrible smoky horror nothing can cross."*

- **Nobody can see.** Watchers see a target in the dark only from six cells. An Imperial probe or spotter crossing
  the Sump has to come almost within arm's reach of an unlit crew to report it. Every lamp, fire and lit doorway
  the crew allows itself is a beacon in a country with no other lights.
- **The tar does not care whose boots.** Troopers who cross shallow tar are slowed and filthy; deep tar turns
  them; the false floor takes whoever steps on it. What a mired or dead trooper drops near the tar is the
  kethrel's by morning, and the crew's after the next molt.
- **Ordinary fire is already a weapon.** Tar burns long once lit. A firefight at a pool's edge can light the pool.
- *0.2.0:* **the poured moat and the fuse post.** A perimeter of tar laid like flooring, lit on command into *"a
  long-burning wall of flame and smoke that blocks sight and passage"*. It is spent when it has burned (*"burnt tar
  is spent tar"*), it ends every hope of staying hidden, and it is exactly what a small crew that cannot win a
  fight wants between itself and a strike team while it loads the ship.
- *0.2.0:* **the capstan.** A fixed turret that ropes one visible target and reels it in along the ground, through
  whatever lies between, which here is tar. It also reels in a downed crew member. (His words: *"if that mechanic
  is attached to a turret, it makes complete sense and is awesome."*)
- *0.2.0:* **the solvent wake.** His words: *"Throwing solvent into the pit should INSTANTLY wake the beast in
  Manhunter."* Ruled a deliberate weapon, *"a scorched-earth last resort"*. Under the lens it is the crew's parting
  shot: the siege camp is now the densest cluster of built things on the map, and the ship is leaving.

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
- A deep stratum that clicked and was not answered in time.
- Solvent gone, the crew slowed to a crawl and the decks black.

**Stay, longer than the Empire would like:**
- The dusk: an unlit crew is seen only from six cells, and the search from orbit runs one step slow.
- Tar between the ship and anything walking toward it.
- Nothing here grows over the ship, floods it or freezes it. A careful crew that stays out of the deep strata can
  sit in the dark for as long as its water lasts.
- *Later:* the Sinking. His ruling of 2026-10-02: one thing of value thrown into the tar *"pushes the next Imperial
  probe or raid away x5"*, and other parties' ownership claims on what the crew keeps go down with it. It is the
  most direct answer any biome has to "what helps them stay", and it is a rite, and he tabled the rites on
  2026-10-03. See `NEEDS HIM`.

## What the crew takes away

- **Dig finds:** old bones and hides, sunken machines, sealed casings, partial remains of the old wars.
- **Bitumen and pitch,** for sealing, glue and paving, and **glasswalk for the ship's own decks** (his named gift).
- **Fuel,** rendered from barrelled tar or bought from Junkers (see the clock section; rendering is owed).
- **Solvent and seepwax.** The acid that cleans tar also cleans it anywhere else the crew meets it.
- **Tar-cured hide and glassy black leather,** thrummel chitin, skellarn leg-spines *"prized for awls"*.
- **A cage of sump-mice.** The owner ruled them tameable, cheap and easy: *"a living tar-detector a caravan
  carries."*
- **Whatever the kethrel was wearing.**
- *0.2.0:* the capstan, learned by studying two preserved draw-joints from the strata and buildable anywhere after;
  the tar vault as a larder aboard; gaslight lamps and flame statues for the decks.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Crossing raw tar slows and dirties a walker, and the tar travels with them onto floors and decks. | One pawn crosses shallow tar and walks up the ramp; one walks round on solid ground. | The clean walker's deck stays clean. Deep tar turns a ground walker back; nobody is deleted by it. |
| Solvent scrubbing really removes tar, from the person and from what they carry, without the player ordering each scrub. | A tarred crew with reachable weak solvent and Cleaning enabled; then the same with the solvent forbidden. | A scrub that clears the health label while the carried tar puts it straight back is a failure. |
| Glasswalk never fouls and is never walked at full speed. | A dirty walker on glasswalk, on ordinary floor and on bare pan. | Glasswalk does not clean the walker's boots. |
| Sump-mice cross tar freely and bend around what is under it. | A map with a dormant bulge and open pools; watch the lines. | Remove the bulge: the lines straighten. |
| The pallick fails under a walker, mires and hurts and does not kill; mice never cross it. | A pawn walks onto pallick and onto mirrelin crust beside it; a helper stands by. | Mirrelin holds. A mouse routed at the pallick goes around. |
| A dig pays by depth and sometimes clicks; the click gives time to clear the site and for a nearby miner to answer it. | A shaft worked through several strata with a miner near and with one far. | A stratum table with no trap row would pass a lazy check: the scene must see a click and both outcomes. No whole Assailant or Rakatan ever comes up. |
| A dormant bulge wakes by cause, with signs first, and the woken beast is slow, unfightable, goes for built things and leaves a mound and a letter for each one taken. | Wake one by a deep dig with the ship's yard built at a distance; load and launch ahead of it. | Shooting it changes nothing that matters. Nothing it takes disappears without a mound. It sinks back and is a bulge again. |
| The kethrel picks up loose scrap near the tar, wears it in visible stages, and gives every piece back on molt or death. | Scrap left by a pool; a kethrel loads; a handler coaxes a molt. | The dropped things are the same things, counted. |
| A belch coats ground, goods and decks near a pit, and solvent or glasswalk answers it. | Trigger a belch beside a stockpile and the ship's ramp. | Glasswalk under the splash takes no deposit. |
| The skellarn really flies, lands, and walks the open tar. | A skellarn over a pool with mice on it (flight read from its flight state, never from a screenshot). | It is not mired where a pawn would be. |
| An unlit crew in the dusk is not seen by a watcher beyond a few cells; a lit one is. | A probe passes an unlit camp and a lamplit camp at the same distance. | The same pass on a daylit map sees both. |
| Native plants grow with no sun and no sunlamp, and nothing native glows. | Skelver, korveth and lanneth growing through the visit. | A plant from elsewhere planted beside them does not grow. |

Settings: one switch per major feature, defaults as shipped, everything off leaves a cold dark flat with black
ground (standing rule, every mod).

## Shared machinery

**Featured here** (the Sump is where each is vital and should be proven):
- **Stuff that gets on you and comes home with you** (the tar coating, the carried-filth link and the tarred
  condition, in `EnvironmentalHazards`; solvents in `TheSump`). Any biome with a sticky hazard can use it; only
  here is it the whole day.
- **Animals whose avoidance is a map** (`RM_MapComponent_DreadField`, `RM_JobGiver_DreadAvoidWander`,
  `RM_CompFilthTrail`): mice bend around dread sources and leave a trail that shows it.
- **Work that rolls on a table and can roll a trap** (`RM_CompWorkedLottery`, `RM_LotteryTableDef`): the dig. Any
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

**0.1.0, the stop**
- The land: permanent dry dusk, deep and shallow tar, cooled glass reaches, the pan, the margin ring of
  chemotrophs. (built)
- Tar on everyone and everything, the tarred condition, weak solvent from seepwax, automatic scrubbing, ordinary
  floors that foul and glasswalk that does not. (built; a live run found the scrub leaving the condition in place,
  which is a defect to fix, not a scope question)
- Sump-mice as the instrument; the pallick's false floor; the tolleth and soffeth as honest signs. (mouse-lines
  built; the pallick is built as a plant but its collapse and the mice's avoidance of it are not; placing the sign
  plants on the right cells is not built either. All three are owed, and without them the mice are scenery.)
- The dig shaft, the stratum lottery and the click. (built; moved in. Most of what the table pays today is
  placeholder salvage: the old bones, hides, casings and machines the sheet promises are still to be authored.)
- The dormant bulge, its warning signs, and the station-eating beast that is evacuated ahead of. (the bulge, the
  wake causes and the beast are built offline; the day-ahead warning, the bubble and the ring, was not found in
  source and is owed. Moved in.)
- The kethrel: pickup, the scrap shell in stages, the molt. (built; moved in)
- The belch. (built as a splash; moved in. The real flood through FlowWorks is 0.2.0.)
- The cast: sump-mouse, gulveth, the three thrummels as plain animals, dredgel, skarrid, skellarn with real flight.
  (built)
- The margin's goods: skelver, korveth pitch, bitumen, seepwax, hides, lanneth. (built)
- Dusk as cover from the Empire's watchers, and one step of cover from orbit. (the first is built in the pursuit
  code; the second is the small build his ruling asks for)
- Tar rendered to ship fuel at a bench. (owed: the small build his fuel ruling asks for)
- Tar fouling of the ship's decks and standing ground, answered by solvent and glasswalk. (the decks are built by
  being floor; the hull skin is owed)

**0.2.0, the stop with company**
- The poured moat, the fuse post and the smoke wall; fire that runs along connected tar and stops at a gate. By
  his ruling of 2026-09-12 a lit moat does catch the natural pools beside it. (moat and post built; nothing today
  makes the promised impassable smoke wall or its column; network fire is a prototype that has never run)
- The capstan turret, its rescue pull, and learning it from two preserved draw-joints; the salvage winch. (built)
- The solvent wake as a weapon. (built)
- The thrummel mound that defends a radius. (not built)
- The tar vault, with solvent-gated extraction, on the ground and as a larder aboard. (built)
- Gaslight: tar and acid make green gas, the warbling lamp, natural seep flames that teach it, flame statues.
  (lamp and gas built; a live run found the scrub making no gas; the natural flames are not built)
- The belch as a real flood that cools to glass at its edge. (engine built, not wired)
- The dredgel parking on dug ground as a prospecting hint. (not built)
- The ship's acoustic scanner readings here. (built)

**Later (a crew that stays, a colony, or the campaign layer)**
- The two tar rites, the Sinking and Mob'Unloo's Price, with their offerings (the beast sleeps a season, the
  ancient traps fizzle). Tabled with all rites by the owner on 2026-10-03.
- Dorvel as a farmed food crop in tar-beds: slow by his ruling (*"due to the inclination of the sun it wouldn't
  grow very fast"*), so a stop never sees a harvest.
- Tar-aged food. Duckboards as their own floor (ordinary wood flooring already does their job).
- Junker stations, the ruins of tar expeditions, failed refineries, miserable moisture farmers, the weighted
  factions: the inhabited pass and the campaign layer.
- The living map of tar that moves between visits. Re-paving the Ashfall Road (his words: *"this one is about the
  ship"*).
- The soundscape the sheet wrote. It is the cheapest large gain in the biome and nothing has built it.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- A fightable tar beast, or one on any raid list (sheet ban; the solvent wake's manhunter state is his one ruled
  exception and is a weapon the player chooses).
- Whole Assailants or Rakatans in the tar; live creatures preserved in it (*"Only truly ancient machines or
  assailants"*).
- Any water terrain, rain, tar rain (ruled out 2026-10-18), sun-driven plant or glowing plant.
- The wick-plant and the brommet (cut at his later review sheets, per the biome's own source comments).
- The lasso as a worn item (*"Remove lasso's from the game, but keep this"*).
- Biome placement scoring and world mutators (no worldgen, ever).
- The pump rhythm, the buried dragline, the Reckoning of Owners, the first round of tar offerings (not taken).
- **Recommended for dropping, not yet his:** the arrival letter "The Ship Remembers the Sump" as written (it
  teaches clues by telling; the mice should do that).

## NEEDS HIM

1. **The Sinking, for a ship on the run.** He ruled its effect (*"pushes the next Imperial probe or raid away
   x5"*) and then tabled every rite. *Leave it tabled* (default; the Sump still hides a crew by its dusk). *Pull
   this one rite forward to 0.2.0:* the Sump becomes the place a hunted crew goes to buy time by throwing away
   something it loves, which is the campaign in one act; it needs the rites machinery, which does not exist yet.
2. **Does the beast swallow the ship?** The ruled beast swallows buildings and leaves a mound. A grounded gravship
   is made of buildings. *It goes for the yard and the ship alike, and the ship can always lift first* (default: the
   beast is slow by design and the lift is the evacuation). *The ship's hull is exempt:* safer, and the beast then
   threatens only what the crew left outside, which is a smaller reason to leave.
3. **Is the scrap the kethrel takes ever the crew's own?** There is a setting for it, default not stated in the
   sources I read. *The crew's unguarded outdoor salvage is fair game* (default here: it is the joke, and nothing
   is lost, only worn). *Never the crew's property:* gentler, and the kethrel is then scenery until a trooper dies.

Two questions the cleanse put on its owner pages are answered here by scope instead of asked again, and each is a
line under "Scope moves" in `rewrite_choices.md`: the playable "hides all" (the dig) is in 0.1.0, not deferred; and
the water problem is not solved, it is the stop's own clock.
