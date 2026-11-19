# The Fever Wood: the design, seen from the ship

**Status:** the one design document for the Fever Wood biome (`RM_FeverWood`, source `src/RimMandrake/FeverWood/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the older
definition sheets, rosters, reviews and the cleanse proposal as the place to read; those files are listed, with what
happened to every idea in them, in `design/concepts/FeverWood/rewrite_choices.md`. Nothing has been deleted yet.
The Fever Wood is one of the six biome mods HELD BY OWNER: this is a design document only and it launches nothing.

**Revised the same day** after his card of 2026-11-18, 3:10 PM PST, which answered four questions the first pass had
left for him: how long a stop lasts, what hides a ship from orbit, where fuel comes from, and whether a biome wears
on the hull. The answers are written in below (see "The ship while it sits here"); the changes are listed at the top
of `rewrite_choices.md`.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/FeverWood/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet; the locked `sheet.md`, `tree.json` and `scenes.json` beside it still describe the
older settled-colony design and would be re-argued from this one when the hold lifts.

**The locked Designer tree is not edited by this rewrite.** Its root is a colony that stays: *"Make a home on the
branches, whose routes shape daily work and travel, above black water that remembers what you do and sometimes
reaches up to change your plans."* (a delegated call, not his words). Two north-star bars were validated from it on
2026-11-16 (`feverwood_branch_home`, `feverwood_water_memory`, in `design/validation_walks/RimMandrake/FeverWood.md`),
under his card line of 2026-10-20: *"A world in the treetops above a black mirror nobody touches. You live on the
branches, and the water remembers."* This document moves neither bar and changes neither file. A later Designer run
has to reconcile them with the ship lens; until it does, the tree and the bars are the binding record and this is a
proposal.

**Second reader, 2026-11-18.** A second pass read the nine older biome files whole, and the rulings and ledger items
behind them, and changed this document in eight places; they are listed at the top of `rewrite_choices.md`.

**How to read the tags:** `NEEDS HIM` marks a question only the owner can settle, with the real answers and the
default this document was written on. `UNSETTLED` marks a fact the sources do not fix. `UNMEASURED` marks an engine
fact nobody has checked. "Built" means the census of 2026-11-17 (`cleanse/census.json`) found it in source; it does
not mean it has passed anything.

---

## What this place is

> *"wood-roads twisting through a living crown, high above black mirror pools that nothing sane touches."*
> (`the_fever_wood.md`, header)

The place where trees finally won. Trunks wider than houses rooted the backswamp still, and their limbs grew together
into roads of living wood above shallow, perfectly black pools that never ripple. The crown is the loudest place on
the planet: alien birds, nectar herds, things clamped to bark. The floor is dim, wet and nearly empty. Under all of
it, under one water table that every pool is only a window onto, lives the **sekkulaath**: one animal, too big ever
to be seen whole, that reaches up with tentacles, takes what comes near, and sets its victims' gear out at the
water's edge as bait.

> *"Below: the black mirrors, unrippled. Nothing goes in the water here. Everything remembers why."*
> (`the_fever_wood.md` §1)

> *"It's the classic Star Wars beast that is so big it can't even enter the screen, but it can reach up with
> tentacles to lash out, grab, pull under."* (owner, 2026-09-23)

> *"Perhaps it literally strips loot of its victims and scatters it near the pools to attract you: treasure to
> lure."* (owner, 2026-09-23)

**Seen from the ship, the Fever Wood is one joke told very well: a crew of scavengers has landed beside a monster
that fishes with scrap.** Jawa cannot walk past salvage. The sekkulaath does not need them (the mud feeds it); it
baits them *"because it can, not because it is hungry"*. Everything in the first two versions serves that meeting,
plus the one sound nobody forgets: the whole crown going silent at once.

It is known and it is named, and that costs nothing: *"The horror is SCALE, not mystery."* His line for how much
the player understands (2026-10-10): *"It is not an unknown mystery, but a mystery still for most of the game."*
The one rule under everything is *"never explained to newcomers because the pools explain it themselves"*.

The crew are small, hooded, skittish, weak in a brawl and at home in dry heat (`reconciled_lore/05_the_clan.md`).
The heat here is the one familiar thing. The wet, the height, the noise and the water are not.

## The clock on any stop

The crew does not settle here. The Empire's search restarts at every landing, and its timing is fixed in
`src/RimUtinni/EmpirePursuit/` (owner's cadence ruling of 2026-08-28: *"around every 5-8 days, keep 'em running"*)
and in the escalation ladder (`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, whose own
numbers are marked provisional):

- First contact, a probe droid, five to eight days after landing. Then a scout team with a spotter, then the first
  real fight (a strike team), then an ion cordon on the ship, a breaching assault, and last an orbital bombardment
  whose letter reads *"This cannot be fought. Leave."*
- Each step comes only if the one before it succeeded for the Empire, and a loud, visible crew halves every wait
  while a hidden one doubles it.

**How long a stop here can last: about six weeks, and that is the outer edge.** His ruling of 2026-11-18 on the
numbers the first pass assumed: *"The numbers you're generating are likely the outer edge allowable for each biome,
and that's just fine. Go with that."* So the figures below are the longest stay the Fever Wood allows, not the
usual one.

- On open ground, with a crew the search reads as ordinary, the ladder's arithmetic gives a probe on day 5 to 8, the
  first real fight around day 12 to 20, and the bombardment around day 20 to 32 if the Empire wins every step.
- The Fever Wood's closed crown is **partial cover from orbit** (his card, same day: *"Canopy, steam and fog slow
  the search by one step; full dark still pauses it"*). Read here as one step on the pursuit's built visibility
  scale: the search runs at the pace of a crew one band quieter than this one really is, which stretches every wait
  by about four tenths. That gives a probe on day 7 to 11, a first fight in the third or fourth week, and nothing
  past about six weeks.
- Noise gives the step back. The water answers noise and so does the Empire's dial; a crew that fights at the
  margins every day is read as loud whatever is over its head.

Most stops end well inside that edge, because the eye, the hull (below) or a full hold ends them first. A season is
fifteen days, so **anything that needs a season to show itself is not in 0.1.0 or 0.2.0 here.** (The pursuit's
numbers are marked provisional in its own source, `EmpireLadderMath.cs`; the shape is what this design leans on.)

---

## The first minutes

The ship comes down through the green ceiling. The trunks cannot fall (the crown is interlocked; *"so you can just
mine right through one"*), so nothing topples: the ship settles between towers onto wet floor, and the marsh that
refuses every heavy building takes the hull because the hull is its own foundation. (UNMEASURED: whether Odyssey's
landing check honours the marsh's building refusal. If it does, the fallback is that only bough-soil and causeway
clearings are legal landing ground, which the landing picker must show.)

On the way down the player hears the crown at full voice: every bird makes its own call and the noise is only their
sum (*"Each animal literally makes its own noise and just adds together"*, owner). The birds really fly, and they
scatter from the descending hull.

Then the landing is heard below. The ship is *"the heaviest, loudest thing that ever came to the Fever Wood"*
(the review of 2026-10-02). The sekkulaath has excellent hearing; noise near a pool calls it. At the pools
nearest the ship a motionless limb rises and stands, and **the whole crown goes silent**. The ruling is that the
crown goes quiet only for the water, so this silence means exactly one thing, and the crew learns what it means in
their first minute: the hatch opens onto the quietest moment the Fever Wood ever has.

> *"crown-life constant and easy; ground-level none — then a ripple, and everything above goes silent to watch."*
> (`the_fever_wood.md` §9)

And from the hatch the crew can already see why they will not simply stay aboard: gear, glinting at the margin of
the nearest pool.

*New in this rewrite:* the landing counting as a noise the water hears. The hearing, the standing limb and the hush
are all built; only the landing as a source is new, and it is small. What the marsh and the water then do to the
hull is in "The ship while it sits here", below.

## The first day

- **The bait.** Stripped gear lies at the pool margins and keeps arriving. A crew that watches a pool sees, sooner or
  later, the slender tentacle that brings it: *"a rare moment of a tentacle coming up and placing a new item"*. It is
  drawn *"more slender and delicate than the others"* so the player can tell it apart before anyone shoots.
- **The first grab.** A Jawa collecting at the margin is taken by a thick fast limb and dragged toward the water. He
  is not dead: he is down in the shallows on a clock, and a companion who was near enough carries him out. The
  owner's words for the distance: *"A nearby companion should have a fair chance. Shore work rewards bringing help;
  someone across the settlement may arrive too late."* The crew learns to go to the water in pairs.
- **Reading the water.** A small pool reaches a little way; a great one reaches far inland. Clicking any pool shows
  its reach on the ground before anything has happened there (the "show water reach" overlay), so the first grab is
  a risk the player took, never a trick.
- **The roads.** The crew walks onto the living-wood routes wherever they touch the ground. Height is paint: nothing
  climbs, nothing is gated. The routes are where the fruit, the nectar herds and the dry footing are, so ordinary
  errands follow them.
- **Shooting the wrong one.** Someone shoots the delicate limb. It vanishes; that pool never gives again and is
  angrier from then on. The next pool over does not hold the grudge.
- **Fighting back.** A hurt limb withdraws and the pool is quiet for some hours. A limb cut through before it can
  withdraw leaves a severed tentacle to butcher and buys a day.

## The first week

- **The nectar deal.** Thornbugs, great thorn-shaped insects clamped to the bark, give sweet nectar to an ordinary
  gathering job, and only while calm. *"The dairy is the alarm system, and every raid costs nectar before it costs
  blood."* A fight near a herd dries it; a fight on the far side of the map does not.
- **The margin's honest goods.** Seep-oil from a squat barrel plant sitting in its own rainbow slick; potter's clay
  from a root-plate; resin medicine scraped from bark. The oil and the clay stand inside some pool's reach: the sheet's
  *"still-water goods, hauled up from the mirrors' edges by people with excellent nerves"*. Reward and hazard are
  the same walk. (The leaning half-dead tree that *"looks like a wreck and is not one"* is still
  here to look at, but it gives no timber: since the tree ruling of 2026-10-17 only true trees give wood.)
- **Working a pool hard.** Every encounter at a pool, every item taken and every loud fight at the margin pushes
  that pool toward its big one. At a great pool the big one is the set-piece: many limbs and **the eye itself**.
  Hurting the eye drives every tentacle on the map off for a day. Killing it before it withdraws ends the water's
  danger on this map for good. There is no protection and no minimum crew: the legibility (pool size, the overlay,
  the silence) is the fairness, and the ship is the way out.
- **A crew that has been greedy for a week has probably met the eye.** That is intended. The set-piece is the
  Fever Wood's climax and it has to be reachable inside a stop; pressure from the crew's own salvaging is what
  brings it within days instead of seasons.

## The ship while it sits here

Three things every biome design now states, by his rulings of 2026-11-18.

**Cover from orbit: partial.** The closed crown slows the search by one step (above). It is not a hideout: the
probe still comes, and at ground level the trunks only break sightlines, they do not close them. This is a
campaign-layer line (the pursuit lives in `src/RimUtinni/EmpirePursuit/`), one entry for this biome in a list the
pursuit already reads.

**Wear on the hull: the ground that refuses and the thing that hears.** His ruling: *"Yes in 0.1.0. It's easy, and
most of the biome already talk about this."* The Fever Wood's sources name two wears, both in the review of
2026-10-02 (`feverwood_bedazzle_review_2026-10-02.md`, the row called the Mooring): *"The biome acts on the ship in
its own two voices: the ground that refuses and the thing that hears."*

- *The marsh.* *"A ship on mud lists and mires a few hull cells a day."* Hull resting on refusing marsh takes wear
  day by day, and the listing edge is the sign. Hull resting on bough-soil or causeway ground takes none.
- *The water.* A hull edge parked inside a pool's reach is lashed when noise wakes that pool, like anything else in
  reach. The reach overlay shows it before the ramp is down.
- *The approach is calm.* No rain and no wind are bans of this biome, so nothing shakes the ship on the way in. The
  wear starts when it sits.
- *What answers it.* Where the ship is put down: firm ground, outside every reach, is free of both. Failing that,
  hands-on work: jacking a sinking edge onto stilt footings (stilts on marsh are built; under a hull they are a new
  use), patching worn plate by hand, and buying quiet from a pool the ordinary way (hurt a limb for hours, sever one
  for a day). No shield setting stops the marsh: his ruling of 2026-09-02 on the ship's shields is that *"slow
  pressing things move through all shields... nothing 'holds out water'"*. The heavy field does resist *"large
  animal assault"*, so a crew that owns one can take the lash on it, at the power that costs.
- *It never traps.* His ruling of the same sitting: the hull *"is thick and can take a lot of damage in most
  situations, so no environment is immediately lethal"*, and the ship *"will advise course of action, but no more
  than that"*. Wear is a bill that grows, with a sign, and launching always ends it.
- *What the built frame already sees here: almost nothing.* The shield tracker's heat case starts at 58 °C
  outdoors or a heat wave (`ShieldHazardUtility.cs`), and the sheet measures this biome at 45.5 °C typical, 51.5 at
  most. So the Fever Wood's heat wears the hull only in a heat wave, and both wears above are new kinds the frame
  has to learn. No source gives the Fever Wood a weather or an air that wears metal.
- `UNMEASURED`: whether Odyssey lets a ship land on refusing marsh at all. If it does not, the marsh's wear never
  happens and the water's is the whole of it.
- *Not in any version until he says: the Mooring in full.* If the ship stays beside a pool, *"a snare wraps a hull
  edge and holds. Launch while moored and the wrapped section tears off into the pool (the porter sets its pieces
  down at the margin weeks later)."* A crew that comes back finds its own hull plate set out as bait. On his card
  of 2026-10-02 the mooring was offered by name and not chosen (he picked the oil boil only). The first pass of
  this rewrite moved it into 0.2.0 on the strength of the hull-wear ruling; the second reader took it back out,
  because a ship idea he passed over is his to bring back. It is question 2 under `NEEDS HIM`.

**Fuel: a richer source, named, and sold nearby.** His ruling: *"Every biome has a fuel source, but for most its
the hideously slow route of rendering biomass into chemfuel... A few biomes have richer sources. You can also buy
it."*

- *The emergency route* is here as everywhere: fruit, tuber and carcass rendered down, hideously slow.
- *The richer source is seep-oil.* The sheet, twice: *"strange oily deposits boiling gently to the surface —
  gathered for perfumes, lubrication, and fuel"*, and *"perfume, lubricant, and fuel from the deep decay"*. The
  barrel plant that carries it stands inside some pool's reach, so every drum is skimmed from under the water's
  nose, in pairs. The harvest is built; the recipe that turns the oil into chemfuel is not, and is 0.2.0.
- *Buying it.* The only sellers the sources name are Sporefall's Wildsteam traders (the kit spec stocks goods at
  *"Sporefall/Wildsteam traders"*), who are campaign layer. The sheet gives the town *"stills running
  nectar-liquor and seep-oil"* and calls the oil *"the still-burners' second source"*, so the refining is already
  there in the lore. The crew pays in what the water set out as bait.
- Not replete. The oil comes a plant at a time, and each plant is a walk to a pool.

## "OMG did you see that?"

Each of these can happen inside the visit. Each says what is on screen.

1. **The crown goes silent.** *On screen:* birds wheeling and calling, then a tall still limb standing out of a
   pool, and every call stops together. *Why it lands:* the loudest map in the game has an off switch, and it is
   not the player's.
2. **The gift-giver.** *On screen:* a thin, almost dainty tentacle lifts a blaster rifle out of black water and sets
   it carefully on the mud, then withdraws. *Why it is funny:* a Jawa is already walking toward it.
3. **The grab and the tug-of-war.** *On screen:* a hooded figure hauled feet-first toward the water, a second
   hooded figure sprinting the boughway, picking him up and carrying him clear. *Why it is alarming:* the clock is
   real, and the one who went alone does not get the second figure.
4. **Shooting the gift-giver.** *On screen:* the delicate limb is hit, snaps under, and the pool's inspect line
   changes for good. *Why it is funny:* it is the single wholly self-defeating act at a mirror, and a trigger-happy
   crew will do it once.
5. **The bark bites.** *On screen:* a pet trots along a trunk and a flat piece of bark unfolds two hooked arms and
   holds it. The silloch *"must read as bark"*; it strikes once from where it sits and does not chase, so the pet
   that breaks free gets away.
6. **The sac that will not come off.** *On screen:* a Jawa tries to handle a grey sac on the bark and it inflates
   under his hands until it cannot be detached. Next to it an amber bead floods its own shell and sets hard.
   *Why it is funny:* the crew's instinct is to pry things loose and take them, and here the things refuse.
7. **The eye.** *On screen:* a great pool erupts in many limbs and one eye on a stalk, the crown silent, the crew
   deciding in that moment whether to run for the ramp or aim for the eye. The owner's phrase for the animal:
   *"shocking even to those who know them."*
8. **The trooper in the pool** (see the Empire, below). *On screen:* a white-armoured figure taken off the shore by
   the same limb that took the Jawa on day one, and nobody runs to carry him out.
9. **The ship is sinking.** *On screen:* one corner of the hull visibly lower than it was yesterday, and three
   hooded figures under it with a jack made of salvage, arguing. *Why it is funny:* the footings going in under the
   hull are the cargo.
10. **Mopping up** (0.2.0). *On screen:* ants from one edge, spiders from the other, the crew behind a shut
   ramp; then hooded figures walking the churned ground between two heaps of dead raiders, picking it clean.
   The sheet's words: *"the two-front war's leavings: stand back, let them, mop up."* The owner's design for the
   wait in between: one comes, *"there's tension, then maybe the other arrives too"*, so the crew ends up
   *"hoping the second column shows up, which is a genuinely novel thing to want during a raid"*.
11. **The gift from the bottom** (0.2.0). *On screen:* a young one tipped from its cask into black water, and
   within the hour something old and heavy set down at the margin. The built table can give a ship chunk, a
   sealed ancient crate, an archite capsule, a persona core or a **gravcore**. *Why it lands:* the monster pays
   its ransom in the one thing a gravship crew wants most.
12. **Paying for fuel with bait** (0.2.0, campaign layer). *On screen:* a crew member counting gear the water laid out (a helmet, a rifle,
   somebody's boots) into a trader's hands for drums of fuel. *Why it lands:* the monster fishes with scrap, and the
   Jawa have found a way to spend it.

## When the Empire arrives

The Fever Wood does not take sides. It does to the Empire what it did to the crew, and the crew has had a week to
learn the rules the Empire has not.

- **The water takes anyone who is not native.** Troopers who cross a pool's reach are seized like anyone else. A
  strike team dropped at the map edge has to cross ground the crew has already mapped pool by pool.
- **Noise calls it.** Blaster fire at a margin brings feelers and raises the standing limb, so a firefight near
  water is fought in the silence, with a third party. A crew can choose where the fight happens.
- **The probe and the spotter need to see the ship.** Solid trunks block sight. A ship parked among towers offers
  few long sightlines, and the ladder's own rule is that a spotter with no line to the ship fails his call. This is
  a consequence of two built things, to be shown in a scene, not a new mechanic.
- **The herd goes dry.** A strike near the crew's thornbugs costs nectar for days. Small, true, and the player
  notices.
- **The eye is no ally.** A crew that has killed the eye has also removed the pools' help against the Empire. That
  trade is real and the design keeps it.
- *0.2.0 adds the floor.* Sink-mud catches by weight (*"heavy things sink"*), so armoured troopers bog down where
  light, small Jawa cross. *"The floor is the wall."* And it adds the lure (next section).

## Who else attacks; who hates the Empire

- **Two raiders, from opposite directions, who hate each other more than anyone:** the kurreth (a wild ant swarm,
  never a faction) and the skreth (the free-tier face of the Webwork's spider brood; the campaign patches the canon
  spider over it). Both are permanent enemies of everyone, each other and the Empire included. They arrive from
  off the map; neither lives here.
- **The lure (0.2.0).** *"Both enemies like helpless prey chained down and wounded."* Staking live bait spares the
  crew and raises the chance a raid comes at all, and *"if only one comes, that's not so good... they might look
  around."* They never arrive together: *"One comes, there's tension, then maybe the other arrives too."* Seen from
  The bait has to be worth eating: since 2026-11-03 the built stake draws nothing for a rat or a chicken and
  draws fully for a horse or a prisoner, and once a raid is drawn the bait cannot be untied. Seen from
  the ship this is the crew's best trick against a strike team: the oldest rule here is *"when both come at once,
  open the gates between them and stand back"*, and it does not say who the two have to be.
- **Nobody here fights *for* the crew.** The Wildsteam's treetop town of Sporefall is campaign lore, placed by the
  campaign layer and not by this biome; they are friendly at home and the sources do not say they fight the Empire.
  `UNSETTLED`, and not this document's to invent.
- **No native chases.** The crown's own animals wait or graze. Pursuit comes only from off the map. That ban stands.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The hull. A ship on marsh sinks a little every day, and a ship in reach is lashed whenever the pool wakes.
- The eye at a great pool, arriving on the crew's own greed, with no protection. A crew that cannot face it leaves.
- An angered pool beside the ship (someone shot the gift-giver) that makes the nearest salvage not worth it.
- *0.2.0:* the oil boil. On the hottest still days the seep-oil lifts into a low rainbow haze; oil gathering pays
  double; *"one spark (a gunshot, a torch, dry lightning) flashes fire along the haze, and a burning pool edge wakes
  the deep."* A crew that fights in it burns its own camp. The review's line for it:
  *"A harvest window you work in silence and without guns."* The haze lies on the ground only, so a shot from a
  boughway does not light it.

**Stay, longer than the Empire would like:**
- Broken sightlines among the trunks (above).
- Pools the crew has learned and the Empire has not.
- A crafted radioactive charge fouled into a pool suppresses the water for several days without a fight
  (owner: *"Fouling the water with specific poisons or radioactive material will cause it to be supressed for
  several days as the material diffuses away."*). In the campaign only genuinely dangerous radioactive salvage
  works; outside it the charge *"can be crafted from Uranium"*. His words name it twice (the ladder of 2026-09-23,
  and on 2026-11-10 *"poison the water of that pool if you have the right poison on hand"*), so it is in 0.1.0
  here; see question 1.
- The closed crown, which slows the search from orbit by one step (his card of 2026-11-18). It is unbuilt.
- A ship set down on firm ground outside every reach, which the place does not wear.

## What the crew takes away

- **The bait itself:** the gear of everyone the water ever took (the built table gives silver, gold, seep-oil, clay
  and sap). Salvage with a story on it.
- **Severed tentacle:** meat from the one animal that cannot be hunted. In the campaign it is dianoga, with a canon
  kitchen behind it.
- **Nectar**, the crown's trade good, *"priced in the herd's peace"*.
- **Seep-oil:** *"scent, slick, and flame"*: a trade good from the first day, and from 0.2.0 the Fever Wood's fuel.
- **Resin medicine, ribbon plumage** sheared from the murrelith, **potter's clay**.
- **A chellow**, if someone tames one: a beakless bird with a throat like *"a lamp with a bellows"*, and a private
  alarm that still goes quiet for water anywhere the ship lands near it.
- *0.2.0:* **one great gift from the bottom** for a returned young (it can be a gravcore), wreck salvage, and
  **chitin and salvage** from wherever the two raiders met.

## The promises of 0.1.0, and the scene that would show each one broken

A promise here is something a player sees. None of them is a number.

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The ship's landing silences the crown and raises a standing limb at the nearest pool. | Land beside a pool with a living flock; read the calls and the limb. | The same landing on a map with the water switched off: the birds scatter and keep calling. |
| Gear arrives at pool margins and can be collected. | Leave a pool alone; a deposit appears on a free cell and a pawn hauls it home. | A hit on the bringer: it vanishes, nothing is left, and that pool gives nothing afterwards while a second pool still does. |
| A seized crew member can be carried out by a companion who was near, and is lost if nobody comes. | Two pawns at the margin, one seized; the other carries him clear. Save and reload mid-clock. | A helper staged far away arrives late; a helper who only touches the victim rescues nobody. |
| A bigger pool reaches farther, and the reach can be read before any attack. | Stand pawns at the same distance from a small pool and a great one; open the overlay on both. | A solid trunk between pawn and pool: no strike. |
| Hurting a limb earns hours; severing it earns flesh and a day. | Light damage, then heavy damage, on fresh limbs. | Quiet stops gifts as well as attacks: no risk-free farming window. |
| Working a great pool brings the eye; killing the eye ends the water's danger on this map. | Raise the pool's pressure by ordinary collecting and fighting until the set-piece comes; fight it both ways. | A small pool under the same pressure never shows the eye; a second map is untouched. |
| Thornbugs give nectar calm and none frightened; a far fight does not dry them. | Gather; stage a threat near one herd and far from another. | The frightened herd recovers only after the threat is gone. |
| Imperial troopers are seized like anyone else. | Walk a trooper squad across a mapped reach. | A native animal on the same cells is left alone. |
| The bark ambusher strikes once and does not chase. | Small prey passes a silloch; prey that breaks free flees. | The silloch stays at its trunk. |
| The vaulm seals and the drommath swells when hurt or mishandled, every time, never at random. | Hurt each; hit again inside and after its recovery. | An untouched one beside it does nothing. |
| A ship resting on marsh, or with an edge inside a pool's reach, is visibly worn day by day, with a sign before the damage; a ship on firm ground outside every reach is not, and a worn ship can always launch. | Three landings: on marsh, on firm ground inside a reach with noise made, on firm ground clear of every pool. Run the days, then launch each. | With the water and the wear switched off, the marsh landing is untouched. An edge on stilt footings stops sinking. |
| Under the closed crown the Empire's search comes one step slower than it does for the same crew on open ground. | The same crew, as loud, landed here and on an uncovered tile; read the search's next contact on both. | A crew made loud here loses the step. |

Neither new row pins a rate: how fast a hull wears and how long a step is are tuning, and stay out of any bar.

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary safe swamp
(standing rule, every mod).

## Shared machinery

**Featured here** (the Fever Wood is where each is vital and should be proven):
- **Water that seizes, with a rescue clock** (in `EnvironmentalHazards`, the component the code calls the Tenant).
  Any biome with a thing in its water can use it; this is its home.
- **The hush** (`RM_MapComponent_SilenceCue` in `CreatureBehaviors`): a living chorus that one event can silence.
  The Webwork owns silence as a place; the Fever Wood owns it as an alarm.
- **Calm-gated gathering** (`RM_CompGatherableCalmGated`): an animal that yields only while it feels safe.
- **Ground that refuses heavy building, and painted causeways** (`RM_GroundRefusalBiomeExtension`,
  `RM_GenStep_RootCauseways`).
- **Mineable living trunks**, the sibling of the Greentide's greatbole body. Here they never fall and never regrow
  in 0.1.0.
- **Ground that wears a hull.** The hull-wear machinery is shared (below); the Fever Wood is where the *ground*
  is the thing doing it.

**Merely active here:** the one sun from geometry, with the crown as tree shade (no Fever Wood heat of its own);
fast jungle growth (`ExplosiveGrowth`); natives drinking their own water (`FlowWorks` thirst, where present); real
flight for anything that flies; bone from butchery (`Bones`); wreck salvage (`Wreckage`); the ship's acoustic
sounder; the Empire's search and the visibility dial.

**Three ship systems built once for every biome, and what the Fever Wood asks of each** (found while revising; the
shared-machinery file has the whole of it):
- *Hull wear.* The campaign already has the frame: `src/RimUtinni/ShipShields/`, whose exposure tracker wears a
  landed ship's structures in a hazard its shield does not cover, sends an advisory and never refuses a landing. It
  knows heat, cold and blown particles today. The Fever Wood needs two wears it does not know: terrain under the
  hull, and a pool's reach. Neither is answered by any field setting.
- *Cover from orbit.* The pursuit has one list for full shadow (`surveyShadowBiomes`, the Abyss only) and no notion
  of partial cover. The Fever Wood needs a second, weaker entry.
- *Fuel.* One recipe from seep-oil to chemfuel, and a trader who stocks fuel. The slow biomass route is the base
  game's own.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**0.1.0, the stop**
- The land: solid mineable trunks that cannot fall; static living-wood routes and bough-soil; marsh that refuses
  heavy building, with stilts; still black pools. (built)
- The landing heard below: a standing limb and the hush on arrival. (new, small)
- The bait and its bringer; the pool that remembers being shot at. (built)
- The ordinary limbs: the blind feeler after noise, the grab with its rescue clock, the barbed lash, the standing
  sentinel. (built; the reload of a live rescue clock is a known defect to fix)
- Reach by pool size, with the read-before-you-go overlay. (overlay unbuilt)
- Driving it off: withdraw, sever, flesh. The eye at a great pool, brought on by the crew's own pressure; the
  map-wide kill. (built)
- The chorus as the sum of living, flying birds, and its silence. (hush built; per-bird calls unbuilt)
- Thornbug nectar on the calm deal; ordinary harvests (fruit, tuber, resin medicine, seep-oil, clay, cordage,
  cane sap). (built)
- The bark ambusher that does not chase; the carrion mound; the wood-eating grub as an ordinary animal. (built)
- The vaulm's seal and the drommath's swelling. (built; moved in, see `rewrite_choices.md`)
- The water takes troopers too; trunks break the Empire's sightlines. (consequences of built things; scenes owed)
- The place wears the hull: marsh under it and limbs in reach of it, each with a sign, answered by where the ship
  is put down, by stilt footings and by hand. (unbuilt; campaign layer, on the shared hull-wear machinery; his
  ruling of 2026-11-18)
- The closed crown as partial cover from orbit. (unbuilt; campaign layer, one entry in the pursuit; his card of
  2026-11-18)
- Fuel by the slow route, and seep-oil as a trade good. (the base game's refining; the harvest is built)
- The radioactive charge that quiets a pool without a fight. (built; his ladder of 2026-09-23 names it and the
  validated water bar says "treatment"; moved in by the second reader, `Answered on 2026-11-19` 1) With hull wear in, it is
  also how a crew buys days of quiet for a ship parked in reach.
- Limbs that nobody hurts sink back by themselves after a while, so a quiet pool does not fill up and a standing
  sentinel does not mute the crown for good. (built; *"the pool breathes"*)
- Natives are never seized and drink their own water. Every loss shows a sign.

**0.2.0, the stop with company**
- Sink-mud that catches by weight and never harms by itself, and the too-even green skin that hides it (*"firm
  ground — which is the lie"*). (unbuilt)
- The lure: live bait worth eating, staggered raiders, the two fronts, and what they leave. (built)
- The oil boil. (built; owner's card of 2026-10-02)
- Seep-oil rendered to chemfuel, and fuel on sale at Sporefall. (unbuilt)
- The mirror list: a dated note of which pools *"moved lately"*, bought from Sporefall's traders, stale by the
  time it is read. (built, but nothing sells it; the locked Designer sheet keeps it, so the cleanse's advice to
  retire it does not stand. Campaign layer.)
- The ransom of its young: a juvenile bought or carried from elsewhere, released into a pool, earns *"one great
  gift from the bottom"*. (built; owner's card of 2026-10-02) The cask is cargo; the gift is a reason to come back.
- The ollareth, which *"screams, and the crown comes"*: its alarm, once what answers it is defined.
- The thieving bird (the skellick: *"This creature is a thief."*), where the Property mod is loaded.
- Summoning the eye on purpose with noise or an offering, so a prepared crew can pick its moment.
- Broken ant hives at the mirrors (*"the ants tried the water, and it took them"*) as day-one evidence and loot;
  the indicator spike (corvath, *"a grave marker"*) standing at pools that have fed, placed when the map is made.
- The Fever Wood's wreck field and the acoustic sounder's readings here.
- The crown's only safe water, the cistrel cup, once the thirst service it needs is in the build.
- The fever: a fungal sickness from the wood's own spore load, which a crew catches within days and which the
  Wildsteam of Sporefall sell an answer to (his freeze ruling R15 of 2026-09-07: *"the fever is fungal — the wood's
  own spore load"*). It must read clearly apart from the Miasma's and the Rot's disease registers. The light screen
  keeps spores off the ship (*"spores aren't magical, just particulates"*). (unbuilt; delegated call of 2026-11-19,
  `Answered on 2026-11-19` 3)

**Later (a crew that stays, or a colony)**
- The prison tank as an industry: products, teaching, neglect, escape, the escapee establishing in a pool and
  maturing over days. One part of it belongs to a ship more than to a colony, by his ruling of 2026-09-23: a
  young one can only ever be tamed by letting it out *"on a map without such pools"*, where it *"will escape and
  simply wander wild"*; near pools it *"plops down into them and installs itself as a new tentacled horror"*.
  Only a crew that carries the tank to another stop can do that. *"It remembers the tank..."*
- The reactive ant-hive dungeon, its farm, guards and sealing corridors. (*"You decide how deep to go, and then
  you decide too late."*)
- Borers that extend their galleries through a trunk someone lives in; trunks that regrow and crush; sealant.
- Routes that slowly move; plennith that makes the crown's soil; corvath that appears only after a feeding.
- Ranching the four sap-drinkers; nests worth raiding; the doomed-herd incident.
- The mirror-break incident; a bespoke arrival letter; the grolth's acid trail.

**Dropped (already cut or declined by the owner; listed so nobody revives them by accident)**
- Ants carrying thornbugs off alive, and the raid-back quest (cut 2026-10-23).
- The hive parasite (cut 2026-10-23). Any rite (*"none, move on"*, 2026-10-02).
- A sap-drinker that drops into the pool; a crafted bloodless lure; any protection against the eye; split crown and
  floor animal densities; climbing or gated ascent (all declined 2026-09-23).
- A Fever Wood heat kind (the one-sun ruling of 2026-10-19 replaced the "ambient" reading of 2026-10-02).
- The lommerel, thavrik, nemmel, gorrameth and the arch-throwing tree (cut from this roster 2026-10-08, *"no longer
  needed"*).
- A lure that takes any animal at all (closed 2026-11-03: poor bait draws nothing).

**Outside the biome's versions**
- The whole animal rising. It is the campaign's, spent once, in the crater event
  (`sekkulaath_rising_crater_event_2026-11-01.md`).
- Sporefall, the herd-groves, the dianoga's name and kitchen: campaign layer, mapped over a free tier that is whole
  without them.

## NEEDS HIM

One question is left. Three others were answered by his card of 2026-11-18 and are written into the design above:
the crown is partial cover from orbit; the place wears the hull, in 0.1.0; seep-oil is the Fever Wood's richer fuel
source. Two more were answered on 2026-11-19 (next section).

2. **The Mooring in full: bring it back?** (hull) Offered by name on his card of 2026-10-02 (*"if you stay, a
   tentacle wraps a hull edge and holds. Launch anyway and that section tears off into the pool"*) and not
   chosen; he took the oil boil only. No words of his were recorded against it, and he passed over it before he
   had said the ship lens or ruled hull wear in. Default here: out. Yes puts the snare, the torn-off section and
   the crew's own plate as bait into 0.2.0. The same card passed over a rented trunk-top landing pad at
   Sporefall and a steel saddle across two trunks; they come back with it or not at all.
   *Waits on the declined-ship-ideas question of 2026-11-19.*

Two readings this document rests on, flagged where they are used: "one step" of cover is one visibility band
(cover), and an unbuilt fuel recipe goes in 0.2.0 (fuel). Both are asked once for every biome in
`design/RimMandrake/biome_shared_machinery_2026-11-18.md`.

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. (scope) **The no-fight charge: 0.1.0 or 0.2.0?** *His ruling:* his ladder of 2026-09-23, his answer of 2026-11-10
   and the move card of 2026-11-18 (*"Move it, list every move"*). 0.1.0; the first-version size question can still
   move it.
3. (other) **Is there a fever in the Fever Wood?** Yes, at 0.2.0. His freeze ruling R15 (2026-09-07) says *"the fever
   is fungal — the wood's own spore load"*, and nothing later reversed it. The sheet's ban 5 forbids a *"fungal
   miracle"*, not a disease. R15 also owes a clear line between this fever and the Miasma's and the Rot's registers.
   **This changes the design's default.** Was: no fever. Undo: strike the fever line from the 0.2.0 list and set this
   answer back to *no fever*. *Delegated call.*
