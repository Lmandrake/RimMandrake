# The Rust Cathedral: the design, seen from the ship

**Status:** the one design document for the Rust Cathedral biome (`RM_RustCathedral`, source
`src/RimMandrake/RustCathedral/`), rewritten 2026-11-18 on the owner's instruction to see every biome "through the
lens of Utinni". It replaces the older definition sheet, its amendment draft, the kit spec, the review, the giant's
hook pitch and the cleanse proposal as the place to read; what happened to every idea in them is in
`design/concepts/RustCathedral/rewrite_choices.md`. Nothing has been deleted. This is a design document only and it
launches nothing.

**What kind of place this is (checked against the sheet's own header):** a surface biome: a flat plateau of metal
almost directly under the sun. The ship lands on it like anywhere else. One patch of it exists in the world.

**A rule this document keeps:** the sheet partitions its lore. Most of what is known about this place is plot the
players discover late, and its bans forbid any player-facing text from explaining the mind, the droids' mercy or
what happens when someone digs too deep. This design names those truths only where a builder must know them, and
every such line is marked *(not player-facing)*.

**Who reads this next:** a Designer run on this concept is handed the list of files in
`design/concepts/RustCathedral/` (`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its
path by sitting here. Nothing in the pipeline reads it by name yet. The Rust Cathedral has no locked sheet or tree;
its only pipeline material is the cleanse proposal of 2026-11-17, which this design supersedes and which was never
applied.

**Second reader, 2026-11-18.** A second reader who did not write this design read the sources to their ends and
repaired it; what changed and why is at the top of `rewrite_choices.md`. In short: the wear on the ship is built
already (every tile here is over the shield frame's heat line, and the ground is saturated with pollution, which
the frame also reads), so the hull section now cites the frame and his shield rulings and invents nothing; the
pattern hull is named as this biome's row on his ship-gift register, with what it costs; his founding rulings of
August (the file the first read did not open) are carried in, including what the free droids think of Jawa; the
campaign's ruled answer to "what if the Empire comes here" is cited; and several lines say "as built" where the
signature is not built yet.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"A maze built by minds you'll never meet, still guarded by their machines. Salvage paradise with a temper."*
> (owner, by card, 2026-10-20)

> *"A circuit board the size of a country, humming to itself in its sleep."* (`the_rust_cathedral.md` §9)

> *"Astounding quantities of metal were brought down from the asteroids onto the surface to feed vast factory
> complexes, which have now ground to a rusty halt."* (owner, 2026-08-15)

*"A metal country."* A dead-flat plateau of deck plate at the foot of the eternal noon, cut by *"a complex, almost
circuit-board maze of walls, structures and designs that scream of meaningful complexity and intention"* (owner),
rust dust banked in drifts against them, heat shimmer for weather, *"and almost nothing alive."* *"You do not stand
on ground that holds a factory; you stand on the factory."* Dried, cooked animals lie where they strayed in. *"And
under everything, always, a hum."* The hum changes. Everyone eventually notices that it is *"reacting to them."*

It is *"not a place that contains metal. It is built of it — the whole map is the reward"* (owner, 2026-08-15),
so *"the only thing regulating the reward is how hard it is to survive standing on it."* The ground is saturated
with old industrial poison as well as heat: *"the droids are immune to the heat and the poison, which is exactly
why the place can be a home to them and to no one else."* And *"for machinery this old it has barely rusted at
all, and that wrongness is the first thing an educated visitor notices."*

The sheet's whole instruction for surviving here is one sentence: *"the Cathedral is not survived by walls but by
manners."* Mine the plain plate freely; touch nothing sacred; when the hum drops, stop.

**Seen from the ship, this is the richest scrapyard on the planet, and it is watching.** *"The map is MADE of
treasure."* *"Every wall is money, every sacred building is blasphemy, and the hum grades you continuously in
between."* An earlier pass put the crew's side of it plainly: *"We are Jawas: a giant ownerless droid is the
biggest salvage prize on Ash'karr."* So this is the stop where a crew whose whole nature is to take things apart
and carry them off is set down in a country made of metal, told it may have most of it, and asked to be polite
about the rest. The founding ruling put the bargain in one line, and it is a line about Jawa: *"I can have all of
this if I am careful and slow"*, *"the only bargain that makes a scavenger clan's patience into a virtue."*

The free droids hold this ground as their holy city, *"the machines' equivalent of a birthplace"*, and they have
a history with this crew's kind. His words of 2026-08-19, on why their goodwill starts at neutral: *"They were
hostile due to Jawa tendency to enslave and sell droids, but then they stole the ship and angered the Hutts… so
now it's up to neutral."* They have one piece of advice, and the sheet keeps it word for word:

> *"Why have you angered this place? We know what it feels. So will you if you just listen."*

*(Not player-facing.)* The ship has been here before. His ruling of 2026-08-15: the Utinni is a Forsaken ship,
*"one of the initiators"*, built by the people who built this, and *"the vaults, the Arsenal, the Rust Cathedral —
these are not somebody's ruins. They are her people's."* Her systems would call the place by its makers' name,
Archon. Nothing says any of this to a player (there is no talking ship in the first version, by his ruling of the
same day); it is why bolts stay alive on this hull and on no other.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last (the outer edge of a stay, not the usual one; owner's ruling of 2026-11-18).** The
ordinary ladder with nothing to slow it: a first week nearly free, a first fight in the second or third week,
nothing past about a month. In practice less, for reasons that are the place's own: there is nothing to eat that
the crew did not bring, the noon is hard on people and hull alike, and the hum keeps its own account of how the
crew behaves.

**What cover this place gives, and which kind (same card: canopy, steam and fog slow the search by one step).**
**None from orbit.** *"The whitest, emptiest sky on the planet over the fullest ground."* No canopy, no steam, no
fog, no dark. On the ground the maze's walls break sight lines, so a probe or spotter has to come round a corner
to see anything; that is all.

*(Not player-facing.)* The sheet's plot canon makes this the one biome with an opinion about the pursuit: the mind
under the plate survives by *"looking exceptionally dull"*, *"the Empire's modern presence is the top threat"*, and
*"the player's Rakatan gravship flying around agitating the Empire is exactly the danger it fears — so it dislikes
the player at first."* The campaign's arc is already ruled to act on it (`design/Jawa/cathedral_concealment_arc_spec.md`):
*"Empire heat brought near: high Heat while parked on/adjacent to the Cathedral region; any Act II+ pursuit event
resolving on Cathedral ground is a large hit — the 'local skirmish' it dreads, made real by the player."* And his
ending for a crew that lets it go all the way (2026-09-12): *"The rust cathedral fights the Empire and slowly
falls, the planet becomes a warzone again... Something ancient and wondrous is gone forever, and the ship
mourns."* So in the campaign this is the one stop where staying until the Empire arrives is the worst thing a
crew can do. Nothing in 0.1.0 or 0.2.0 acts on it; see `Answered on 2026-11-19` 2.

---

## The first minutes

From altitude the walls are *"alignments that resolve into meaning"*: this is the one biome best seen from a ship
coming in, a circuit board the size of a country. The ship comes down out of a white sky onto plate that rings
under the landing gear. The shadows of the walls are
hard, short and exactly where they will always be. The air is hotter than the crew's own desert and the sun is
straight overhead. Then the engines stop and the hum is there, *"felt in the teeth."*

On the deck near the ramp something that looks like a dropped component gets up and walks. Then several. They move
*"in complex, strange, dance-like patterns for no reason."* These are **living bolts**: *"component-looking
creatures the player tries to pick up and simply move out of the way."* They are not organic, not tameable and not
meat: *"a bolt with legs, or a gear with opinions"*, and very small (a tenth of a cell, by his sheet note of
2026-10-05: *"more like a little button"*). They like the edges of the ship: *"a landed ship on deck plate draws
the living bolts; they gather and dance on its hull and under its struts while the hum watches."*

Before the first hour is out the player should have seen three things without hunting for them: the bolts dancing;
a wall that is plainly steel and plainly minable; and, a long way off down a corridor, something very large
crossing a gap between walls, slowly, not looking this way.

## The first day

- **Most of it is free.** Deck plate and ordinary corridor walls mine out as steel. Veins of **dead smartsteel**
  are worth a good deal more. A crew can fill a hold from the first hundred paces.
- **Some of it is not.** Certain dividers are marked: they are the maze's intended routes, and cutting a shortcut
  through one sours the hum and may open a chamber with a guardian in it. (His answer of 2026-11-10: *"cutting
  through shortcuts angers the Hum and can reveal trapped chambers with guardians."*) A few buildings are
  **sacred**: owned, rare, and not offered for mining at all.
- **The hum is the meter.** It has a mood, voiced as layered tones, calm to very much not. *"Mine deck plate all
  day and it stays a warm drone."* Do the wrong thing and *"a new tone slides in under the first, then another."*
  At its worst it goes silent. (As built, at default settings the display is clamped to calm, so none of this
  can be heard yet: owed work on the signature itself.)
- **The bolts show where.** *"Living bolts tend to gravitate around what they don't like"* (his answer of
  2026-11-10): when the hum rises, the bolts gather at the work that caused it. Stop the work and withdraw, and a
  small irritation fades by itself.
- **Killing a bolt is noticed.** It is allowed: *"the sheet prices sacrilege, it does not un-button the gun."*
- **The ground is poison as well as oven.** The whole plateau is saturated with old pollution. A crew works here
  the way it would in any fouled place: covered, in shifts, and not for long. The only sicknesses on the place's
  own table are mechanites, and they are rare.
- **The heat is ordinary heat, and there is a great deal of it.** Hot air, plus the planet's one sun from almost
  straight overhead, which is the strongest it gets anywhere. Shade works. The walls' short hard shadows are the
  shade.
- **The pools.** Still, toxic, with a sulfur-yellow edge that reads as acid from a distance. They do not move and
  they do not hide. Walk round.
- **The cleaners.** Small tough machine-roaches eat filth. A Jawa camp produces filth. The camp is tidied by
  something nobody asked. They tell the crew nothing about the hum, by his ruling: they are fauna, *"not
  instrumentation"*, and go on cleaning while everything else has frozen.
- **The guards hold ground.** The great machines keep marked grounds and slow patrol lines. They do not hunt.
  The sheet's advice when one crosses the line of sight: *"be small and biological and boring."*

## The first week

- **Sacrilege has a price, in a real currency.** Destroying or claiming a sacred building costs standing with the
  Free Droid Enclaves, the faction whose holy city this is, and that standing is the same one the crew trades on
  everywhere else. There are about ten such buildings; from neutral a crew can strip five before the Enclaves
  turn (*"half the Cathedral is takeable on arrival and finishing it costs the war"*), and then *"there is no
  cheap apology"*: *"the punishment is isolation, not an army."* (As built none of this is wired: the sacred
  walls belong to the machines' own faction, whose goodwill cannot move, and the real Enclave debit is owed
  work.) The hum stays above calm while the debt stands, and its inspector says what is owed and where.
  Paying is plain: deliver silver against a visible bill, from the public side. No rite. (His answer of
  2026-11-10: *"sacred damage requires costly, concrete repayment before comfortable access returns, without a new
  ritual."*)
- **The canals.** Where a map has them, coolant still runs in channels, *"to cool nothing anyone can find"*, and
  blind pale eels circle in it. They can be fished and sold. *"Fishing the canals is possible and deeply
  inadvisable — the hum changes the moment a line goes in."*
- **The giant.** A **borehulk** may be on the map: *"a massive mining droid, more like a digging tank with drill
  and scoop... Not very intelligent but ridiculously armored and strong. Fortunately it is also peaceful."* (owner,
  2026-10-02). Its bit is worn out. It scrapes at the plate and gets nowhere, and backs away from anyone who hurts
  it. It came here *"having escaped the abandoned mines"*. It is the largest ownerless machine a Jawa has
  ever seen, and in this version there is one thing to be done about it besides look: it can be killed, which is
  *"possible and very hard"*, and its wreck is steel, plasteel, components and the drill head. It will not fight
  back. It sounds *"a long grinding horn and backs slowly away."*
- **Digging deep.** Under the plate is metal of another kind, live and patterned. Drilling for it brings machines,
  in force, against the drill and anything defending it. They lose interest when the drilling stops. This metal
  is what the pattern hull is seeded with (below), so the ship's best armour is under the plate and guarded. *"Dig deep enough and very bad things
  happen. No one's quite sure what."* No text will ever say more.
- **The dead.** Old wrecks lie among the walls with their own salvage, and at the map's edges the dried bodies of
  animals that wandered in mad and were cooked.
- **Leaving with passengers.** At launch, bolts that were on the ship's edges stay on the hull. They go on
  dancing out there, in any weather, on any world. *"Almost like external hull pets"* (owner, 2026-10-02).

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The part that walked off.** *On screen:* a Jawa bends to pick a loose bolt off the deck for the scrap bin;
   it stands up on small legs and joins a line of others turning a slow figure on the plate.
2. **Everything is steel.** *On screen:* the first wall comes down as a stack of steel, and the crew looks along
   a corridor of identical walls to the horizon.
3. **The tone drops.** *On screen:* a miner starts on a marked divider; the hum falls a step; every bolt in sight
   turns and begins to drift toward that one Jawa.
4. **The room behind the wall.** *On screen:* the shortcut opens, and there is something standing in it.
5. **Be boring.** *On screen:* one of the great machines crosses the end of the corridor, and the whole work
   party goes still in a wall's shadow until it has gone.
6. **The line goes in.** *On screen:* a crew member drops a fishing line in the coolant; the hum changes on the
   instant; they keep fishing.
7. **The bill.** *On screen:* a sacred conduit lies in pieces, the hum will not settle, and the inspector shows a
   price. A hooded figure carries a sack of silver to the public side and counts it out.
8. **The tidy camp.** *On screen:* the crew's rubbish heap, and a small machine-roach working steadily through it.
9. **The big one.** *On screen:* a massive armoured digging machine grinding a ruined drill
   against the plate. A Jawa walks all the way round it, twice.
10. **They came for the drill.** *On screen:* the deep drill bites, the hum goes quiet, and machines arrive and go
    straight past the crew to the drill.
11. **Stowaways.** *On screen:* the ship lifts, the camera follows, and on the hull three small shapes are still
    turning their figure in the wind. The letter says only what was seen: *"A few of the dancing bolts are still
    clinging to the hull."*
12. **The approach.** *On screen:* the last seconds of the descent, and the maze below resolving into a pattern
    that was plainly drawn by somebody.

*0.2.0 adds:* the floor rolling as a mile of machinery under it turns over once, a dust front crossing the map,
and every animal and machine standing still until it passes while the crew, who are not held, stand there
feeling it (see `Answered on 2026-11-19` 6: this is built, he picked it by card on 2026-10-02, and it asks nothing of the
player); the hull bolts all stopping at once and turning to face a crew member who is selling something of the
Cathedral's, on another world; a crew member who has listened long enough to read the tones, and writes it down to sell;
the worn bit unbolted and hauled to a Junker yard to be haggled over; the hull bolts' cold little marks, and what
the crew sold while they were watching; what the eels do to the one who eats them.

## When the Empire arrives

- **They see the ship at once,** and they come on the ordinary schedule.
- **The ground is garrisoned, and not by the crew.** The guardian machines hold their marked grounds against what
  enters them. The sheet's description of the great ones is *"terrifying in their destructive capacity against any
  biological they spot."* A strike team that drops or stages on held ground has that to deal with first. They do
  not leave their grounds to help anyone: *"perimeter defense only."* (`UNMEASURED`: whether guarded grounds and
  patrol lines are built; the census could not tell.)
- **The crew may be passed over where a trooper is not.** In the campaign the crew can carry a pass that stops the
  machines treating its holder as an enemy on Cathedral ground (built at the campaign tier). The free droids are
  passed over too, and *"even the droids don't know why."*
- **The maze is the crew's by then.** A crew that has kept to the routes knows them. An assault that cuts its own
  shortcuts is cutting marked dividers, and the hum does not ask who is holding the cutter.
- **Shade decides the firefight.** Everybody fights in the same noon. Whoever holds the walls' shadows is not
  cooking.
- *(Not player-facing; campaign.)* A fight with the Empire on this ground is the thing the mind fears most, and
  the arc prices it as the largest loss of its regard a crew can cause. A crew that knows the place lifts before
  the strike team lands.
- **Nobody may explain any of this.** If the place seems to take a side, no letter, inspector or droid says why.

## Who else attacks; who hates the Empire

- **The guardian machines,** on their own ground only. The permanently hostile hidden faction they belong to
  stays in the raid roster by an old ruling, with *"vault and perimeter emphasis, not manhunts."*
- **Whatever is behind a marked divider.**
- **The machines that answer a deep drill.**
- **The Junkers,** in the campaign's world: *"hostile on sight, bribable, no trader caravans."* Their yard is
  where a worn bit goes in 0.2.0.
- **The Free Droid Enclaves** hold eight of their twelve seats on this ground. They were enemies of Jawa once,
  for the obvious reason, and are neutral now because the crew stole from the Hutts. They become enemies again
  one sacred building at a time.
- **The Hutts,** in the campaign: they *"want the ship back and they want paying."* Whether they would fight the Empire is `UNSETTLED`.
- **Who hates the Empire:** nothing here says so. *(Not player-facing: the mind fears the Empire's attention more
  than anything and hates something else entirely.)*

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The larder. *"Green flora count: zero."* Nothing grows, almost nothing lives, and the eels are watched.
- The noon, on a crew that works outside.
- The hum at its worst, with debts unpaid and the Enclaves' doors closing everywhere else the ship will land.
- A deep drill left running.
- Almost no fuel to be had here (below).

**Stay, longer than the Empire would like:**
- Steel without limit, and better than steel.
- Shade that never moves, and walls already built.
- A garrison between the ship and some of the approaches, for a crew with manners.
- Nothing that hides the hull. Every day here is taken in plain view.

## What the crew takes away

- **Steel,** by the hold-full. **Dead smartsteel.** For the bold, **live-pattern metal** from under the plate.
- **Wreck salvage** from the derelicts.
- **Eel catch,** *"salable"* and *"watched"*.
- **Hull bolts:** not chosen, not owned, and not leaving. They take no harm from heat, cold, poison or vacuum;
  a blow can still kill one.
- **Roach shell,** which sells and which nobody is watching.
- **A standing with the Free Droid Enclaves** that goes with the ship to every other stop, for better or worse.
- *0.2.0:* shed bolt curiosities; a written primer on reading the hum; a refurbished bit and the choice it buys;
  and **the pattern hull,** this biome's gift on his ship register (an agent's pick of 2026-11-11): hull plate
  cut from dead smartsteel, each section seeded with one ingot of live metal, on which *"dents creep shut,
  cracks close, and a holed section is whole again in a few days."*

## Fuel, and what this place does to the ship

**Fuel: the thin slow route, and buying from the Enclaves.** (Owner's ruling of 2026-11-18: *"Every biome has a
fuel source, but for most its the hideously slow route of rendering biomass into chemfuel. Uselessly slow, only
for emergencies. A few biomes have richer sources. You can also buy it"*.) Here there is almost no biomass to
render: no plants at all, a handful of animals, the eels. So the slow route is thinner here than anywhere, and
buying is the real route. This design does not invent a source (`Answered on 2026-11-19` 1). One lead exists in
the sources: a measured note
of 2026-08-19 found that the game's own ancient chemfuel refinery landmark is allowed on the donor biome this one
was made from. Whether it can occur on our definition is `UNMEASURED`. A dead refinery on a factory plateau would
be the least invented fuel there could be. A crew arrives with most of the fuel it means to leave on.
Buying: the Enclaves deal on standing, so standing with the droids is worth fuel; the Junkers have no trader caravans at all (*"a loot source, not a
market"*), so their truce yard is for one work order and not a shop. Fuel is bought from the Enclaves; how
much they sell is `UNSETTLED`. One thing here burns fuel instead of giving it: a kept borehulk's servicing takes
chemfuel (0.2.0).

**What wears on the ship (owner's ruling of 2026-11-18: in 0.1.0, from what the sources already say; his list
began with "Heat").** The frame exists and is not redesigned here: `src/RimUtinni/ShipShields/`, on his shield
rulings of 2026-09-02. *"The environment is hostile and immediately goes to work on the ship... Its hull is thick
and can take a lot of damage in most situations, so no environment is immediately lethal."* An unshielded hull in
a hazard deteriorates, faster the longer it sits; the ship advises and never refuses. On this biome the frame
already has two hazards to see, so nothing here is new work.

1. **The noon (built).** The frame counts a map as a heat hazard at 58 C outdoors. The sheet's measured
   temperatures for these tiles run from 58.9 to 65.9: every one is over the line, all the time. It is ordinary
   heat, by the one-sun ruling. *The answer by shield:* the thermal veil, which by his own note reflects the
   ship's heat inward too, *"so the temperature slowly climbs anyway"*: here the veil is a clock of its own.
   (Read from the code and the sheet; no map temperature was measured.)
2. **The poison (built, on the fixed world).** The plateau is saturated with pollution, and the frame's
   particulate test reads a polluted tile. *The answer by shield:* the particulate screen. His ruling on that
   screen says it *"repels small animals"*, and the living bolts are very small machines that he later ruled
   climb aboard. Whether a screened ship keeps its stowaways off is `Answered on 2026-11-19` 4.
3. *The answer by armour, to both:* **the pattern hull**, which mends itself (provisionally 120 hit points a day).
   It is built and switched off; this design places it in 0.2.0. Each section needs an ingot of the live metal,
   and the live metal comes only from a deep drill, which brings machines. A crew that wants the hull has to
   decide how many ingots it dares to raise.
4. *The answer by hand:* ordinary repair, and getting out of the open. The walls' shadows are too short to cover
   a ship.

*Not wear:* the pools (stationary and legible: do not land in one) and the hull bolts (passengers, not damage).
Dry thunderstorms are on the weather table and are not a hazard the frame sees.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The land is a flat metal maze of deliberate, connected corridors; most reachable metal, ordinary corridor walls included, mines freely as steel, and dead smartsteel is worth more. | A generated map; walk the routes; mine plate, a plain wall and a vein. | A scatter of walls with no routes. Bulk mining that angers the hum. |
| Cutting a marked divider sours the hum even though the metal is ordinary, and a guarded chamber behind one is a guarded chamber. | Mine an unmarked wall and a marked one. | A random trap with no chamber. A mark that cannot be seen before the cut. |
| The hum has a mood that can be heard and read, rises with disliked work, falls with restraint, and goes silent at its worst. | Do a disliked thing; stop; wait. | A hum that never leaves calm. A tone change with no cause the player did. |
| Living bolts dance, and gather at the work the place dislikes; a plain cue marks the site when no bolt can reach it. | A disliked job in the open and one sealed away from every bolt. | Bolts that gather at innocent work. A bolt that can be tamed, butchered for meat or picked up as an item. |
| Destroying or claiming a sacred building costs real Enclave standing, keeps the hum above calm until repaid, and is cleared by paying silver against a visible bill. | Break one; read the bill; pay part; pay the rest; reload between. | A private local ledger. A debit for damage that left the building standing. A rite. |
| Deep drilling brings machines against the drill, and they leave when the drilling ends. | Drill; stop; and a second time, do not stop. | A manhunt after the drill is off. Any text that says what they are. |
| The guardian machines hold their ground and their patrol lines and hunt nobody. | Stand outside a marked ground; step in; step out. | Pursuit across the map. |
| Coolant eels live in the canals, can be caught and sold, and a line in the water moves the hum. | Fish; stop; fish on. | A reading that was calm before and after. An eel walking on the deck. |
| The pools are stationary, visibly marked, and hurt what stands in them. | Walk a pawn round one and through one. | A pool that moves or cannot be told from plate. True acid. |
| The air and the overhead sun are ordinary heat at their strongest; the walls' shadows are real shade. | The same pawn in the open and in a wall's shadow. | A heat of the Cathedral's own. |
| A roach cleans filth; a worn borehulk scrapes, backs away when hurt, and never fights. | A camp with filth; a shot at the borehulk. | |
| An unshielded ship parked here wears, on the built shield frame, from the heat and from the polluted ground; the veil and the screen answer each, and neither is a design of this biome's. | A ship parked a week in the open, bare; then veiled; then screened. | Wear that stops when the crew behaves. A hazard the frame does not report. |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Bolts on the ship's edges at launch stay on the hull and keep dancing wherever the ship lands. | Land, wait, launch, land elsewhere. | Bolts that fall off in weather. Bolts carried as cargo. |

Settings: one switch per major feature, defaults as shipped, everything off leaves a hot metal flat with its plain
salvage and residents (standing rule, every mod). Switching off never resets a real faction standing.

## Shared machinery

**Featured here** (the Rust Cathedral is where each is vital and should be proven):
- **A place with an attitude** (`RM_AttitudeKernel`, `RM_MapComponent_BiomeAttitude`): a slow saved mood per map,
  raised by named acts, voiced in sound and shown by creatures. Any guarded site could use it.
- **Debts that follow the ship** (sacred receipts against a real faction standing, saved across maps). Kin to the
  Leaning Scrub's witness-and-trail and the Miasma's nursery ledger: three places that remember who did what.
- **Creatures that are a display** (the living bolts' figures).
- **Things that ride the hull between worlds** (`RM_HullBolts`): the only biome content that leaves with the ship
  by itself.
- **Machines that answer one act and stand down when it stops** (the deep-drill response).

**Merely active here:** the one sun from geometry (at its maximum, with nothing but walls for shade); the shared
cleaner job and water confinement in `CreatureBehaviors`; arrival safety notices from `EnvironmentalHazards`;
wreck salvage; the acoustic scanner's readings; remote bodies moved by a mind (the Lantern Deeps feature that
pattern; here it stays behind the plot's gate); the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**The one signature (his first-version answer of 2026-11-19): the temper.** Extraction disturbs the Cathedral; the
hum's mood and the living bolts show where the place minds the work; a marked divider or a sacred building costs
real standing until repaid; deep drilling brings machines that leave when it stops; guardians hold ground and hunt
nobody. *Why a normal stop is sure to see it:* salvage is why a crew stops here, and the first cut, haul or line in
the canals moves the hum and gathers bolts at the work. His experience line: *"Salvage paradise with a temper."*
*Runner-up:* restoring the borehulk (the cleanse's runner-up), later. The bolts that board at launch are a ship
moment, not the temper, and move to 0.2.0 (the card's cost: *"several of your own picks wait a version"*).

**0.1.0, the stop**
- The land: deck plate, the maze of routes and marked dividers, dry bright weather, toxic pools with their
  sulfur edge, cooked strays, derelict wrecks; heat as ordinary air and overhead sun. (part built; the pools are
  absent; whether the maze is laid as deliberate corridors is unknown)
- Bulk salvage and dead smartsteel; live-pattern metal only from deep. (built)
- The hum: its saved mood, its sound, silence at the worst. (built; at default settings the display is clamped
  to calm, which hides it, and nothing yet restores lost standing)
- Living bolts: figures, gathering at disliked work, protection. (figures and protection built; gathering is not)
- Marked shortcuts as an offence; guarded chambers behind them. (unbuilt)
- Sacred buildings, real Enclave standing, the visible bill and repayment in silver. (placement built; the real
  currency and the repayment are not)
- The deep-drill response. (built)
- Guardians that hold ground and never hunt. (unknown)
- Roaches; eels, their catch and what fishing does to the hum; the worn, peaceful borehulk. (built)
- The wear on the landed ship: heat and pollution, on the built shield frame, answered by the veil and the
  screen. (built; shared machinery, nothing of this biome's to add)
- The ground's pollution as a cost on a crew working outside. (the fixed world's tiles; ordinary game rules)
- An arrival notice of the pools and the heat. (built)

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- Bolts that board at launch and live on the hull. (built; moved in, see `rewrite_choices.md`)
*Already here before that answer:*
- The line-cycle: machinery turning over under the plate, and every animal and machine standing still while the
  crew, who are not held, feel it. (built; in the batch he picked by card on 2026-10-02; `Answered on 2026-11-19` 6)
- Hum reading and the written primer; the droids' muttered commentary. (built)
- Hull bolts as witnesses: the ledger of what the crew sold or broke in their sight, the cold marks, the uneasy
  hum on return, the revealed dilemma of prying them off, the small comfort of having them. (built)
- The Worn Bit: taking the bit off, the truce yard and its haggling, the long restoration, and keeping the giant
  or freeing it, with what each costs and earns. (built in large part; *"This should be a MAJOR pain to repair"*)
- The pattern hull, this biome's gift on his ship register; each section needs live metal from a deep drill.
  (built; an agent's pick)
- The bolt as a button on the wall: a living bolt keeps to cells beside a wall and is drawn onto the wall's face,
  as he asked on 2026-10-05 (*"more like a little button that flits around on walls and other surfaces"*). One
  job-giver and a draw offset; option A of `RUSTCATHEDRAL_LIVINGBOLT_WALL_FLIT_1`. (unbuilt; delegated call of
  2026-11-19, `Answered on 2026-11-19` 7)
- Shed curiosities and the charge for picking one up; the coolant in the eater's blood; the shock from the canal;
  standing that bleeds while the hum is at its worst; the giant frozen with the mood. (built)

**Later (a crew that stays, a colony, or the campaign)**
- The hiding mind and its long arc with the crew: stages, regard, offers, the survey, the descent and what is
  revealed. Campaign layer, and gated.
- The two rites he shaped on 2026-10-02, the Mending Weld (*"restoring an old creation. Very sacred."*) and the
  Stranger's Overhaul (rites are tabled).
- The interlock doors: paired factory doors the line-cycle swings, where bracing one seals the other for good.
  Held for a second turn in October and never shown to him.
- The campaign's price for bringing the Empire here, its going dark, and his ending in which it *"fights the
  Empire and slowly falls"* and *"the ship mourns."*
- The pass, which the mind *"can also grant... to the player jawas if it chooses."*
- Gravtech boons; hum-literacy as a trade.
- The rarer wall tiers between dead smartsteel and the deep metal.
- The enclave seats, shrines and roads as places.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- True acid terrain; hunting or raiding guardians; ordinary wildlife or anything green; organic settlement here.
- Any text that explains the mind, the droids' mercy or the deep response.
- A heat kind of the Cathedral's own (retired for every biome by the one-sun unification).
- The eldest eel, the armed great patroller, remnant rebuilding, sun bars, the Second Signature, the Loosing, and
  four of the giant's five hooks: the Furrow, the Bounty Notice, Scoop-Loads and the Rider (not chosen
  2026-10-02).
- Stowaway bolts that go still a day after leaving (the pitch; he replaced it with bolts that remain).
- The Loosing and the Rider (not chosen 2026-10-02): they stay down by his answer of 2026-11-19 on declined ship
  ideas; he can bring either back by name.
- A debt owed to the machines' own faction (the kit's reading; his August ruling names the Enclaves).
- The nineteen hill tiles (the later flatness ruling); the mech-rat and the mech-chicken (his cuts).
- The alternate-planet scoring worker and its biome-rarity slider (his ruling of 2026-08-15 and 2026-08-18: no worldgen, ever; no setting that could roll a second world).

## NEEDS HIM

None open. Every entry is answered (next section).

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. **[fuel] What is the fuel here?** *His ruling:* his ruling of 2026-11-18: *"Every biome has a fuel source, but for
   most its the hideously slow route of rendering biomass into chemfuel. Uselessly slow, only for emergencies. A few
   biomes have richer sources. You can also buy it"*. The thin slow route, plus buying from the Enclaves. Not "none".
   **This changes the design's default.** Was: *None, and say so*.
2. **[other] Does the place show that it wants the crew gone before the Empire comes?** Nothing in the free versions.
   The campaign owns it (the design's default). *Delegated call.*
3. **[other] Jawa with droids aboard, in the free droids' holy city.** Nothing (the design's default). *Delegated
   call.*
4. **[hull] Does the particulate screen keep the bolts off?** *His ruling:* his shield ruling of 2026-09-02: *"Slow
   pressing things move through all shields"*. They get through.
5. **[hull] The pattern hull as the ship's armour, and when.** 0.2.0 (the design's default). *Delegated call.*
7. **[other] The bolt as a button on the wall.** Back in, at 0.2.0, built the small way: the bolt keeps to cells
   beside a wall and is drawn onto the wall's face. It was his own wish (sheet note of 2026-10-05), and the digest
   that cut it did not say so. **This changes the design's default.** Was: *Stays dropped*. Undo: move it back to
   "Dropped" and set this answer back to *Stays dropped*. *Delegated call.*

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

6. **[scope] One signature, or the pieces.** *His card of 2026-11-19 (first version):* one signature a stop is sure
   to see: the temper (Scope, top). Neither the boarding bolts nor the line-cycle is in 0.1.0: the bolts move to
   0.2.0 with their text and promise row, and the line-cycle stays there. **This changes the design's default.**
   Was: the bolts board in 0.1.0.
8. **[other] Ship ideas he did not choose** (the Loosing, the Rider, the first form of the stowaways). *His card of
   2026-11-19 (declined ship ideas):* they stay turned down. His own replacement, bolts that *"REMAIN on the ship"*,
   stands, at 0.2.0 by answer 6.
