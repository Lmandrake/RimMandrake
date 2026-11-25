# The Abyss: the design, seen from the ship

**Status:** the one design document for the Abyss biome (`RM_Abyss`, source `src/RimMandrake/Abyss/`), rewritten
2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the older
definition sheet, cast bible, review and cleanse proposal as the place to read; what happened to every idea in them
is in `design/concepts/Abyss/rewrite_choices.md`. Nothing has been deleted yet. This is a design document only and
it launches nothing.

**A correction to this pass's own brief.** The brief called the Abyss "a sea biome: the ship is the only way down
and back". It is not. Every source describes a dark highland: *"obsidian teeth in a fog that light cannot cross"*.
The seabed rulings do not apply here. (The Abyss does have a fishery, by the owner's mark of 2026-11-17; it is in
mineral pools on land.) Where the word "sea" came from: on 2026-08-13 the owner's first idea for the donor's
pitch-black biome was to *"pretend [it] is at the bottom of the ocean"* and *"'go to that biome' when we try to land
on water"*. His sheet of 2026-09-06 made it a highland instead, and the seas later got a seabed of their own.

**What the owner had already approved.** On 2026-11-17 he walked the cleanse proposal for the Abyss and approved its
scope with four marks (`cleanse/owner_marks.md`): *"I saw how much you put into 0.2.0 Impressive, and the right
call. It's still a daunting mod even with that you chose to keep in 0.1.0. I approve."* This design keeps that
scope and his four marks, and makes **one** move against it, which was the first thing under `NEEDS HIM` and stands by the move card (`Answered on 2026-11-19` 1): the hidden
ship comes forward into 0.1.0.

**Revised the same day** after his card of 2026-11-18, 3:10 PM PST, which ruled on how long a stop lasts, on cover
from orbit (*"full dark still pauses it"*), on fuel, and that a biome wears on the hull in 0.1.0. That last answers
the first pass's question about the grain and the ship. The answers are written in below (see "The ship while it
sits here"); the changes are listed at the top of `rewrite_choices.md`. The hidden-ship move is left exactly as the
first pass made it, and is still his to revert.

**Second reader, 2026-11-18** (a different agent from the writer, before any old file is deleted): every Abyss
source was re-read, the ledger items and the owner's card answers of 2026-11-10 among them, and this design was
repaired. The largest repairs: his three card answers on what the hide is for are now in the design (the first read
never opened them); the grain on the hull is sourced (a ship idea put to him on 2026-10-01); the rites moved to
"later" on his ruling of 2026-10-23; six animals he cut are listed as cut; and what is and is not built of the
hidden ship is stated plainly. The list and the reasons are in the section "Second reader" at the top of
`rewrite_choices.md`. Continued the same evening: the sixteen files first read in part were read to their
end, with the four ledger items filed under the biome's older names, and 101 more rows were added (the rites'
own design, the Empire's ladder, his planet rulings of 2026-09-07, the first names, the census and the dry-run
record). The Abyss has no locked Designer sheet or tree, so nothing here waits on a Designer run to
reconcile.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/Abyss/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything. Nothing
of the Abyss has been watched working in the game except one recorded run of 2026-10-07 (loading, sign placement,
flight eligibility and four cryptid checks) and the cold grip, seen once on an older build of the animal.

---

## What this place is

> *"A country of obsidian-black stone twisted into shapes no wind carved, drowned in a darkness that behaves like a
> substance: it fills the air, it pools, it parts without warning into pockets of impossibly clear air, and it
> closes again. Light does not fail here for lack of a sun — light is eaten in transit."* (`abyss.md` §1)

The owner's own line for the experience, typed 2026-10-20:

> *"The dark is a palpable tide that protects you yet conceals terrors close by. Wonders emerge just as often for
> moments of transcendent beauty, only to twist into nightmares just as swiftly. You fear staying here too long will
> find the source of the nightmares themselves."*

**Seen from the ship, the Abyss is the one biome that was about the ship from the start.** His concept of
2026-08-13: *"'Hiding' your gravship from pursuit is a big deal in this campaign."* The sheet's ruling: *"this is
one of the few biomes that measurably slows Imperial pursuit... no orbital eyes, no long lances; pursuit drops to
walking pace and short knives."* And its star: *"The sensor shadow — the place to run to when the Empire is close.
Refuge priced in darkness, breakage and cold."*

The note that first worked his idea out said why hiding is the Jawa verb: *"They are small and overlooked, and
being overlooked is the thing they are actually good at."*

So the Abyss turns the other biomes inside out. Everywhere else the question is what a crew can see in a week
before the Empire arrives. Here the crew came *because* the Empire is close, the Empire is slow to come, and the
question is how long they dare stay. The design note that first worked his hiding idea out set the two rules this
document keeps: *"The hiding place must be poor"*, and *"it must not be permanent."*

**His three answers on what the hide is for** (by question card, 2026-11-10; `designer_codex_2026-11-09/Abyss/ANSWERS_OWNER.md`):

> *When shelter turns frightening:* "Wonder draws you out: beauty offers something worth approaching, then leaves you
> exposed when darkness returns. Shelter remains worth choosing, while wonder tempts the crew beyond it."

> *Keeping a hidden colony working:* "Searches interrupt work: ordinary work is safe between searches, but exposed
> activity becomes dangerous while a search probe passes."

> *Why staying becomes frightening:* "Danger becomes more frequent: close threats and frightening reversals gradually
> leave fewer peaceful stretches, giving a practical reason to depart at the cost of breathing room."

And it gives the place its central bargain, which is already built: **light keeps the things in the Dark off you,
and light is what gives the ship away.** (Second reader, read from the source: the cover counts the crew's own lit
lamps and does not count light that grows. So the bargain has an answer the place itself supplies: hide by the
light of living things.)

The campaign's own gods say the same thing twice. The god of flight and the god of concealment *"reconcile in
exactly one posture, hidden and watching for the instant to flee"* (`design/Jawa/biome_rites_pass_2026-10-01.md`),
and the hungry war-sun is *fed by light cast into darkness* and starved by *"staying dark, hidden, and unfought"*
(`design/Jawa/salvation_rites_2026-10-01.md`). A ship lying dark in the Abyss is in that posture.

The crew are small, hooded, weak in a brawl and evolved for the dune sea. This is the cold side of the world. The
Jawa see well in ordinary darkness. This is not ordinary darkness: it is in the air, and the sheet's ban is flat,
*"no clean sensing"*. (`UNMEASURED`: whether the built sight penalty already ignores the xenotype's dark vision.
The intent is that it gives them no pass.)

## The clock here is different

The Empire's search restarts at every landing: a probe droid five to eight days after landing, then scouts, a
strike, a cordon, a breach, a bombardment (`src/RimUtinni/EmpirePursuit/`; ladder in
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers provisional). The Abyss is on the
pursuit's built list of poorly surveyed biomes, which multiplies every wait by four; the note of his 2026-08-28 ruling
(`design/Jawa/mods/ruthless_faction_pursuit.md`) records his figure for such refuges as 20 to 30 days. The ladder's own arithmetic: *"A Hidden clan on an Abyss tile
therefore gets roughly 40–64 days between rungs."*

**How long a stay here can last: about two months before the Empire's first contact, and that is the outer edge.**
His ruling of 2026-11-18 on the numbers the first pass assumed: *"The numbers you're generating are likely the outer
edge allowable for each biome, and that's just fine. Go with that."* The arithmetic: three weeks to a month for a
crew the search reads as ordinary (five to eight days, times four), and up to two months for one that stays hidden,
with the ladder's later steps as far apart again. A ship that holds its cover does better still, because the
search has lost it; then the edge is set by the place and not by the Empire. Most stays end well short of it, on
food, on fuel, on the hull (below), or on a probe that got its report out.

His words for the ordinary pace (2026-08-28): *"around every 5-8 days, keep 'em running"*. (`UNMEASURED`: the
Empire also raids as an ordinary storyteller enemy, by his ruling of the same day; the built delay is on the
pursuit's own timers, and whether it slows those other raids nobody has read.)

His rule for how the search opens (2026-09-27, in the ladder): *"Escallation isn't just 'more troopers' it's more
kinds of raids that rapidly escalate until you move. Always start with probes that can be evaded."* The oldest
source for the pause is in the same file: his rulings of 2026-08-05 and 06 that *dark/covered tiles PAUSE the
orbital clock*. What is built slows the clock fourfold and does not stop it, and his later word of 2026-11-18 keeps
it so: *"nowhere pauses it indefinitely"* (`Answered on 2026-11-19` 9). The ladder
also has the tile remember how far the search got, fading a step a season: *"the desert remembers, decaying"*. The
same dark valley is not a free hide twice running. By the same design the storyteller's own Empire raids never
advance the search. (Rung definitions exist in `src/RimUtinni/EmpirePursuit/` today; nobody has run them.)

A season is fifteen days, so **the Abyss is the one stop where seasons pass and slow things can be seen**: a crop
under a lamp tree, stone wearing away, a crew getting used to the dark. (The pursuit's numbers are marked
provisional in its own source.)

---

## The first minutes

The ship comes down past the terminator into air that eats its running lights. Every lamp aboard reaches a
fraction of what it reached an hour ago. Sound is muffled. There is no wind at all.

What the player sees is dim country with its outlines kept: black etched rock, dark sand, and the land's own
lamps, *"lit like a harbor at night"*: blue glow against yellow, a carpet of glowing grass.

Then the first gust arrives *"like an impact"*, and every gharrek on the map opens at once: flat, plate-shelled
crawlers that were invisible on the obsidian lift their shells and show *"a map-wide carpet of fluttering
gill-fans"* with a faint chemical glow, feed on the stirred air, and shut. Then stillness again. (Known gap: the
gharrek has its facings and no picture yet of the fans opening. This moment is owed its art.)

The crew's first decision is in front of them before the ramp is down: how many lights to leave on.

## The first days

- **Warmth clears the air.** A heated room is clear inside while the Dark stands at its open door. The ship's warm
  rooms are islands. Cold rooms fill.
- **Lamps shrink; living light does not.** Artificial light reaches less the thicker the Dark. The glow plants
  resist it. A lamp tree (wickwood) can be dug up and replanted beside the ship; glowberries, once picked, are a
  light a crew member carries.
- **The moths come to the light.** Krizzaks are soft dark moth-things *"with a mouth like a lamp-glass"*. They eat
  light. They settle on lamps and glow plants and the lit radius shrinks: *"a perimeter going dark one lamp at a
  time is the warning."* They scatter from heat. They really fly.
- **Something waits for the lamp to fail.** The ishvarith, one of the Abyss's family of pitch-black, yellow-eyed
  things, breaks for the dark when it is lit. Light is a wall against it until the moths eat the wall. (Built for
  light only; the older line about heated space is not built, and a cornered one still fights.)
- **The rattle.** The ombrathia hunts by the tremor of movement; its quills pick it up, and it *"raises them in a
  clattering hackle"* before it lunges. The rattle is the warning and it comes before the attack, not after.
- **The grip.** The saevitha has no mouth. It kills by holding on and draining warmth. It has no mouth because
  the picture came first: it and the ishvarith began as two drawings passed over for a livestock animal, and his
  words of 2026-09-01 sent them here: *"Others get promoted to other crag creatures. The forsaken crags are the
  dark biomes on the night side."* He approved both on 2026-09-02.
- **The kin.** These are one family, and his rule for it (2026-10-05) is exact: pitch black, four glowing yellow
  eyes, soft sibilant names, *"the 'possibly of Sith origin' type."* Every one of them is described as *"less
  evolved than made, as if some old and patient cruelty once had the shaping of it."* The pack beast *"still bows
  its head to a hard voice."* The hauler works all night *"as if it remembered whose it was."* A crew that has been
  owned by nobody is surrounded by animals that remember an owner.
- **The grain.** The Dark, where it dies, falls as fine corrosive grain. It wears unroofed stone and steel, never skin, and it
  leaves a rust-brown oily dust, tholin, that sweeps up and refines to fuel. *"Roof everything"*, and feed the
  heaters with what fell on the roof.
- **The poor larder.** Berries, a slow black-and-violet fungus that grows only where grain has eaten the rock,
  milk and meat from the herds, and what can be fished from the mineral pools: veiljaws, black ribbon swimmers with
  pale hinged jaws and blind pits, and suturefins, flat things that ripple along the bottom with a pale seam like
  a stitch. Each catch is also alive in the pool, moving. (His mark of 2026-11-17, overruling an older roster note
  that this water held no fish; the two creatures are the cleanse's designs.) All of it grows slowly, by his
  growth law of 2026-09-07: fast growth needs *water AND light* both, and the Abyss has no light of its own.

## The first weeks

- **The hidden ship.** While the ship sits with its engine cold and few lamps lit, cover builds: the search loses
  it. Starting the engine tears the cover away. Every lamp lit for the farm, the perimeter or the workshop is
  weighed against it. *"You are unfound, which is different."* (In the campaign layer, by his card of 2026-10-01
  that the free tier gets no ship touch. What is built, `RM_MapComponentShipCover`: a meter that few lit lamps
  anywhere on the map build and noise wears down. What is not: the engine's start does not yet break it, and
  nothing outside the Abyss reads it, so today the pursuit is slowed by the biome alone.) (`UNSETTLED`: the built
  meter calls the map quiet at four lit lamps or fewer anywhere on it, so a lamp in a far workshop counts the same
  as one on the ramp. Whether the count belongs to the ship's surroundings or the whole map is open. The meter's
  code sits in the free biome mod, against the campaign-only card; that is for whoever builds to reconcile and is
  not a reason to remove it.)
- **Probes still come.** His words, typed 2026-09-30: *"Yes but probe droids will still come that must be
  avoided."* A probe drifts in under the Dark looking for movement and light. His rule for it (card, 2026-11-10):
  *"ordinary work is safe between searches, but exposed activity becomes dangerous while a search probe passes."*
  The crew beats it by being still and dark while it passes, by letting it leave having seen nothing, or by
  destroying it before it reports. The campaign's ladder adds that a shot probe destroys itself, *"a kill is never
  free loot"*, and gives the probe its letter, *"Probe landed"*, with a bar that fills as it sees. (The ladder's
  probe sees by line of sight; the Abyss's own built probe does not, which is the gap named next.) (Built: the
  probe counts lamps and moving crew by distance alone, through walls, and reads no heat. Seeing through walls is
  a gap to close.) A probe that reports collapses the cover, and the search
  resumes at its ordinary pace: the Abyss becomes a five-to-eight-day stop like any other.
- **Farming by lamp.** Crops grow under a lamp tree if they are also kept warm. A lamp tree is living light, and
  living light does not count against the ship's cover (built), so the farm is not what gives the hide away. Its
  cost is the warmth: fuel, and the heaters' own lamps. This is the hide's real ration.
- **The lane.** Ordinary research at the bench teaches heat-folding, and the fold lamp: a fuelled heater-lamp with
  a throat that holds a lane of clear air open, stopped by walls and fading with distance. The review's phrase for it: *"explicitly a heater
  that clears air, not a magical sensor."* It is the only clean line of sight on the map, and the crew chooses where
  it points.
- **The Unveiling.** Rarely the Dark folds away wholesale and *"the actual map shows itself, naked and lit — then
  it simply folds back. The one moment you see what country you have been living in."* When it closes, the lamps
  shrink again, the moths return, and whatever was waiting is nearer than it was. His answer of 2026-11-10 is what
  the clearing is for: *"Wonder draws you out... then leaves you exposed when darkness returns."* The crew that
  walks out to look is the crew caught outside. The review's line: *"Every other biome's rare weather is a hazard.
  This one is a gift."* It has a price that is built: the grain falls harder while the air is clear. It has a second
  price: while the Dark is gone, the ship has no cover from orbit, and the search runs as on open ground until the
  Dark returns (delegated call of 2026-11-19, `Answered on 2026-11-19` 3). (In 0.2.0 it also shows the
  sorter's rings standing in the open. Its name collides with the campaign's "nine unveilings"; neither has been
  renamed and nobody has asked him.)
- **The wear.** Weeks of grain on anything left unroofed. The hide is paid for in roofing, fuel, cold and the
  things the crew is not salvaging while it sits here.

## The ship while it sits here

Three things every biome design now states, by his rulings of 2026-11-18.

**Cover from orbit: the top level.** His card: *"Canopy, steam and fog slow the search by one step; full dark
still pauses it."* His later word the same day: *"Going under the ocean is like the Dark... VERY concealed. But
nowhere pauses it indefinitely."* So the Dark is the top level of cover, which it shares only with the sea floors.
As built, that is the fourfold delay on every wait, and on top of it the cover a quiet, dark, cold-engined ship
gathers (the first weeks, above). No other biome is on the pursuit's list yet. An Unveiling takes the cover away
while it lasts.

**Wear on the hull: the grain.** His ruling: *"Yes in 0.1.0. It's easy, and most of the biome already talk about
this."* The Abyss has talked about it since its first sheet, whose star reads *"Refuge priced in darkness, breakage
and cold"*, and the note that worked out his hiding idea said *"Something has to erode while you are down there."*
What erodes is now settled: the ship. The grain on the hull is in a source after all: the review of 2026-09-30
offered him *"The Abyss etches the hull"*, slow wear on the ship's hull fittings with *"sweeping the tholin off
pays for some of the repair"*, as a ship touch for the free tier, and on 2026-10-01 he chose no free-tier ship
touch. This design puts the wear in the campaign layer.

The same note holds the rule this wear must not break: *"Hiding must cost the thing the campaign is about — salvage
and progress — not hit points."* So the wear is slow, a crew can answer it by hand, and it is never the main price
of the hide. The main price is *"the weeks they are not earning."*

- *What the player sees.* In an etchfall the grain ticks on the hull as it ticks on stone, and the outside of the
  ship wears like any steel left under the sky. Dry weather wears nothing. The dust it leaves on and around the
  hull is tholin, the same fuel-dust that falls everywhere else.
- *What answers it.* The etchfall's old lesson, *"roof everything"* (`fluff_cuts_2026-10-23.md`), turned on the ship: a hull face with roofed
  building against it is out of the weather, so a crew can throw up a lean-to of walls and roof along the weather
  side from wreck-field scrap, and leave a ship-shaped shed behind when it flies. (Building outside takes light,
  and light is what gives the ship away.) Patching worn plate by hand. And, for a crew that owns one, the ship's
  light screen: his shield ruling of 2026-09-02 is that it handles *"wind, ash, vapor, bio contamination, spores,
  smoke, sand, and rain damage completely"*. (`UNSETTLED`: whether a running shield counts against the ship's
  cover the way a lamp does. Assumed not; nothing built says it does.)
- *The cold wears the crew, not the hull.* The hiding note calls this country *"cold enough to hurt a species
  evolved for the dune sea"*. The shared hull-wear machinery counts cold only far below anything the Abyss's sheet
  records, so the cold is felt in the rooms and paid for in fuel.
- *It never traps.* His ruling of 2026-09-02: the hull *"is thick and can take a lot of damage in most situations,
  so no environment is immediately lethal"*, and the ship *"will advise course of action, but no more than that"*.
  Launching always ends the wear, and ends the hide with it.
- `UNMEASURED`: how the built etchfall sampler treats a hull today. A ship's own cells are probably roofed in the
  engine's eyes and so spared; wearing the outside faces is the part to build. The census adds one fact: the
  sampler wears natural rock and things built of steel and nothing else, so what a hull is made of decides whether
  today's grain would touch it at all.
- *0.2.0: the repair is here too.* The rescue ship in Lightfall's wall yields four kinds of fitting the crew's own
  ship accepts (hull plating, conduit loom, thruster liner, seal gaskets), and each repairs worn structure aboard
  (built, never loaded).
- *0.2.0: the rough way in.* His own ruling on the planet's wind (2026-09-07) says the terminator's colliding air
  makes *"the atmospheric volatile precipitates, the lightning, the ship damage"*. The sheet's wind: *"Laminar flow hits the relief and the Dark's temperature mosaic
  and shatters into micro-turbulence: wild vortices dancing among the crags, suddenly icy-still, then blasting"*,
  and of the wind machines that once stood here, *"the gust-shear snaps it"*. A ship coming down through that takes a knock on arrival unless its
  screen is up. It waits a version because its only answer is a shield and its only warning is the ship's own
  advisory; the first version's wear is the one a crew with nothing can answer by hand.

**Fuel: a richer source, named, that the hide itself burns; and nowhere to buy.** His ruling: *"Every biome has a
fuel source, but for most its the hideously slow route of rendering biomass into chemfuel... A few biomes have
richer sources. You can also buy it."*

- *The richer source is tholin.* The sheet: *"the Dark's fallen grains are concentrated organic feedstock;
  chemfuel-adjacent industry from air."* It is built: swept up, refined, chemfuel. The crew scavenges its fuel out
  of the weather, off the roof and off the hull.
- *His two words on tholin.* On 2026-09-07 he ruled tholins *"unharvestable — a similar keyword, not a fuel"*. On
  2026-10-01, by card, he ruled that etchfall leaves sweepable tholin dust that refines into fuel, and that is
  what was built. The later decision is the one this design follows.
- *The hide spends it.* Heaters keep the rooms clear and the fold lamp is fuelled. What is left over after warmth
  is what goes in the ship's tanks. A crew that hides well leaves with less.
- *The emergency route is at its worst here.* There is very little biomass in the Abyss to render: berries, a slow
  fungus, the herds.
- *Buying it: nobody.* The hiding note is flat about the kind of place this is: *"No salvage. No sun. No trade."*
  The ship item adds that under cover *"trade ships cannot reach it"* (0.2.0). For a crew whose whole life is
  trade, that silence is the hide's real price. The only people the sources put here are the fugitive holds,
  *"some still occupied"*, and they are later.
- Not replete. *"The hiding place must be poor."* His fuel ruling of 2026-09-07 gives the general reason:
  *"the fact that people have found SO MANY ways to get fuel is still evidence of its scarcity."*

## "OMG did you see that?"

Each can happen inside a stay. Each says what is on screen.

1. **The ground opens its gills.** *On screen:* dead-still black rock, a gust, and the whole map flutters and
   glows for a few seconds. *Why it lands:* nobody knew anything was there.
2. **The lamps go out one at a time.** *On screen:* moths settling on the perimeter lights, each circle of light
   drawing in; a hooded figure with a torch chasing them off one lamp while the next dims. *Why it is alarming:*
   yellow eyes at the edge of the last circle.
3. **The rattle.** *On screen:* a crown of banded quills rising out of the dark with a clatter, a beat, and the
   lunge. *Why it works:* the player had the beat.
4. **Fishing.** *On screen:* a Jawa hauls a black ribbon with pale hinged jaws out of a mineral pool, and the pool
   is visibly full of more of them. His mark: *"YES TO FISH (WEIRD CREATURES)!"*
5. **The vine turns.** *On screen:* the paddle vines along the hull slowly face the one lamp left on.
6. **The helper.** *On screen:* a tamed sorter, stoop-backed, long-fingered, carrying one small item to the
   stockpile *"at a crawl"*, with great seriousness, and eating the filth on the way. A scavenger crew has found the only creature on the planet
   that likes tidying.
7. **The Unveiling.** *On screen:* the Dark lifts and the country stands lit, etched and enormous, for a few
   hours. *Why it is beautiful, and why it twists:* it closes.
8. **The probe.** *On screen:* a probe droid drifting between the crags, the ship dark, every crew member
   standing still. *Why it is funny:* someone left a lamp on in the galley. And when someone does shoot it, it
   blows itself up: the one piece of Imperial hardware a Jawa cannot strip.
   And its twin, from his card: an Unveiling opens, half the crew walks out to stare at the lit country, and the
   air closes with them a long way from the ramp.
9. **Sweeping the ship.** *On screen:* after an etchfall, hooded figures with brooms on and around the hull,
   sweeping rust-brown dust into sacks and carrying the sacks to the refinery. *Why it is funny:* the thing eating
   the ship is the thing that fuels it, and they are not going to waste either.
10. **The shed.** *On screen:* a lean-to of turbine housings and scrap vanes built up against the hull's weather
   side; then the ship lifts and the shed stands there, ship-shaped and empty, in the dark.

## When the Empire arrives

It arrives late, and it arrives into the same Dark.

- **Nobody shoots far.** The Dark cuts sight and aim for everyone on foot, and intervening Dark spoils a shot even
  from clear air. The owner's phrase: *"walking pace and short knives."* For a crew that is *"weak in melee"* this
  cuts both ways, and the design keeps that.
- **The Empire's lights are eaten too.** A lit camp draws the moths; a camp going dark draws what waits for lamps
  to fail. A siege that has to sit in place for two days sits in the Abyss for two days.
- **The crew owns the only clear lane.** A fold lamp pointed down the approach is a firing lane the strike team
  does not have.
- **The grain falls on their steel as well.**
- **The Unveiling is nobody's friend.** For a few hours everyone can see everyone, and orbit can see the ship.
- **Launching ends the hide.** The engine tears the cover away. Leaving is the loud option, and it is always open.

## Who else attacks; who hates the Empire

- **What lives in the Dark,** impartially: the light-eaters, the thing that fears light, the quill-hunter, the
  warmth-drainer, and herd animals that turn on whoever hurts them.
- **People who hate the Empire have been here before.** The sheet lists *"fugitive holds — smuggler caches and
  bolt-holes of everyone the Empire ever chased into the sensor shadow; some still occupied, some now just supplies
  in the dark."* Nothing builds them yet. They are the natural answer to "who here might fight the Empire" and they
  are in "later", campaign layer.
- **The Nhaleth never appear.** The visitors who come for the Dark are a rumour: *"sworn to by nobody credible,
  believed by everybody a little."* No faction, no pawn, no certain structure, in any version.
- *0.2.0:* in a Witchfire storm, a summ may come down and cross the map. *"A storm does not bring the summ; the
  summ brings the storm."*

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The hide is poor. Food, fuel and warmth run down, and nothing here is the salvage the campaign is about.
- The grain eats what is left outside, and now the outside of the ship.
- Nobody to trade with, for as long as the hide holds.
- Lamps and a hidden ship cannot both be had in full; only light that grows is free of that cost.
- The cover wears thin by itself in time (built, with the message *"the search will find it again. It can be built
  up again after a few days"*). The hide was never permanent.
- A probe that got its report out.
- **The longer the stay, the fewer the quiet stretches.** His card of 2026-11-10: *"Danger becomes more frequent:
  close threats and frightening reversals gradually leave fewer peaceful stretches, giving a practical reason to
  depart at the cost of breathing room."* Nothing built does this yet and no source says how; it is the hide's own
  clock in his words, and it is 0.2.0 by the move card (`Answered on 2026-11-19` 4).
- *0.2.0:* the dread. *"You fear staying here too long will find the source of the nightmares themselves."* The
  free tier's whisper about the Nhaleth is that they *"are not visitors at all. They are whoever stays"*, and its
  sign after a long stay is a dream: *"Dreamt I didn't need the light."* For a crew in hiding, the rumour is about
  them.

**Stay, longer than anywhere else:**
- The pursuit's fourfold delay, and the cover on top of it.
- Warm rooms, living lamps, roofed work, fuel swept off the ground.
- A hull kept out of the weather: a lean-to along it, a patch crew, or the ship's light screen.
- Stillness when a probe is on the map.

## What the crew takes away

- **Time.** The weeks the Empire spent not finding them. It is the real product of the stop.
- **Fuel,** whatever the heaters left. Tholin swept up and refined (built: it becomes chemfuel).
- **The fold lamp,** as knowledge: *"useful as a cold-night lamp anywhere."*
- **A lamp tree** dug up and carried; **glowberries**, a light in the hand.
- **Etchcap,** a delicacy and a trade good, slow and scarce.
- **Animals:** a pack beast, a milker, a sorter that tidies.
- *Later:* **a rite.** His words of 2026-10-01: *"Just make a discoverable rite here in the deep dark that they can
  perform later. That's the discoverable tech, or one of them anyway."*
- *0.2.0:* **a great bone,** the Abyss's recorded gift to the ship (`BIOME_SHIP_CONTRIBUTIONS_1`, an agent's pick):
  set aboard, it is what lets a summ egg bond with the crew.
- *0.2.0, from Lightfall only:* parts cut from the rescue ship in the chasm wall to restore the crew's own (his
  words: *"You can't have two ships but you can cannibalize that one to improve yours. A rich haul. But only then do
  they discover that their ship only wants certain parts. It likes what it is and doesn't want deep redesign. Just
  repair."*); an egg; and a great bone to stand on the deck so the egg will bond.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The Dark dims the country and wild creatures but keeps their outlines; the crew stays fully drawn. | A predator, a rock face and a crew member at the same distance, in thick Dark and in a warm room. | A predator hidden entirely fails. A sky tint with nothing else dimmed fails. |
| Sight and aim suffer in the Dark, and a shot through intervening Dark suffers even from clear air. | A shooter in a warm clear room firing out through the Dark at a marked target; then the same shot down a fold-lamp lane. | The same room and target with the Dark switched off. |
| Warm rooms are clear; cold rooms are not. | Two rooms, one heated; open the heated one to the cold. | Temperature is the only thing changed. |
| Lamps reach less in the Dark; living lamps hold. | An electric lamp and a lamp tree side by side, in thin and thick Dark. | |
| Krizzaks shrink a light they settle on, and it recovers when they are driven off; they do not feed through a wall. | A lit lamp with a moth swarm and one behind a sealed wall. | Heat near the lamp: they leave. |
| The ishvarith breaks for darkness when lit and comes closer as the light fails. | The same animal approaching a lit edge, then the lamp dimmed by moths. | A trapped one may still attack: it is deterrence, not a wall. |
| The quill rattle comes before the close attack. | A crew member approached by an ombrathia. | A rattle spent on a distant hunt and silent at the lunge fails. |
| Grain wears unroofed stone and steel, spares what is roofed, and leaves dust that becomes fuel. | Matched pieces roofed and unroofed through an etchfall; sweep and refine. | Dry weather: no wear. |
| An Unveiling clears the Dark everywhere for a while and the Dark returns. | A full Unveiling with lamps, moths and a predator in place before, during and after. | It reveals nothing through unexplored fog. |
| Gusts are real and intermittent; gharrek open on each one. | A day of natural wind with gharrek on the map. | Steady wind with a gust sound over it fails. |
| The pools hold living swimmers and the line brings up the same creatures. | Watch a pool; fish it. | A catch with nothing living in the pool fails (standing ruling). |
| Etchfall wears the outside of a landed hull, with the grain's own sound and dust as the sign; a hull face behind roofed building, or under the ship's light screen, is spared; a worn ship can always launch. | A landed ship through an etchfall with one side bare, one side behind a lean-to; then launch. | Dry weather: no wear. With the wear switched off the bare side is untouched. |
| A quiet, dark ship gains cover; lamps slow it; the engine ends it. | A landed ship run dark, run lit, then started. | With the feature switched off none of the three changes anything. |
| A probe can be beaten by stillness and darkness or by killing it, and its report ends the cover and brings the search back to ordinary pace. | Three probes: avoided, destroyed, and allowed to report. Read the pursuit's next timer after each. | A probe that reports changes the timer; the other two do not. |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The fold lamp holds a lane of clear air that walls stop. | A lamp pointed down an open approach and at a wall. | Unfuelled: the lane closes. |
| Vines turn to the strongest light; a picked glowberry lights its carrier. | Move the only lamp; hand a berry to a crew member in the Dark. | |

The hull row pins no rate: how fast plate wears is tuning and stays out of any bar.

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary dark highland
(standing rule, every mod).

## Shared machinery

**Featured here** (the Abyss is where each is vital and should be proven):
- **The pursuit's survey shadow and the ship's cover** (`surveyShadowBiomes` in `EmpirePursuit`; the visibility
  dial). Every biome sits somewhere on the Empire's clock; this is the one whose identity is that clock.
- **The light ledger:** one shared account of who is dimming which light, so the Dark and the moths never fight over
  a lamp's radius. Any biome with light-eaters or darkness wants it.
- **The gust signal** (`RM_GustController`): one reading of real wind excursions that the gharrek, the sound and
  anything later all obey.
- **Exposure that wears things** (the etchfall sampler, on the shared hazards machinery). With his ruling of
  2026-11-18 this is also the plainest case of a biome wearing a hull: weather that falls on it.
- **Sound dimmed by a medium** (the muffling hook).

**Merely active here:** real flight (the moths); wreck salvage (storm-torn turbine housings and vanes); bone from
butchery; the ship's acoustic sounder; shared creature behaviours (tidying, light aversion's plumbing). The one sun
from geometry applies and has nothing to do: this is past the terminator, and an Unveiling's brightness is not
sunlight.

**Three ship systems built once for every biome, and what the Abyss asks of each** (found while revising; the
shared-machinery file has the whole of it):
- *Hull wear.* The campaign already has the frame: `src/RimUtinni/ShipShields/`, whose exposure tracker wears a
  landed ship's structures in a hazard its shield does not cover, sends an advisory and never refuses a landing. It
  knows heat, cold and blown particles today. The Abyss needs it to know etchfall, and to count a roofed lean-to
  as cover.
- *Cover from orbit.* The Abyss is the built case: the pursuit's `surveyShadowBiomes` list and
  `RM_MapComponentShipCover`. The partial kind the jungles need is a second, weaker entry beside it.
- *Fuel.* Built here: tholin to chemfuel. Nothing to add but the absence of a seller.

## Scope

"Built" is the 2026-11-17 census, not a pass. Items marked **(his mark)** were moved into 0.1.0 by the owner on
2026-11-17.

**The one signature (his first-version answer of 2026-11-19): the hidden ship.** A quiet, dark, cold-engined ship
gathers cover in the Dark; lamps slow it, the engine ends it, probes still come, and a probe's report ends it.
*Why a normal stop is sure to see it:* every stop lands a ship that sits quiet in the Dark from its first night, and
the Empire's ladder sends its first probe within the stop. His move card of 2026-11-18 already names the hide the
Abyss's signature. *Runner-up:* living light against the native feeders (the cleanse's signature of 2026-11-17); it
lost because the ship lens makes the ship the subject. The Dark itself stays as land: without it there is no hide.

**0.1.0, the hide**
- The land: black etched highland and dark sand; stillness broken by gusts; etchfall; the rare Unveiling; the
  biome's dark swirling face on the world map. (built)
- The Dark: dimming with outlines kept (unbuilt presentation), the sight and aim penalty (built), intervening Dark
  spoiling shots (unbuilt), lamps shrinking (built), rooms cleared by warmth (built), muffled sound and the gust
  soundscape (built).
- Living light: the lamp tree and crops under it, glow globes, glowing grass. (built)
- The moths that eat light; the ishvarith; the saevitha; the ombrathia; the gharrek; the tameable sorter that
  tidies; the herds, pack animals and milkers; the summ as an ordinary great beast. (built)
- Etchfall, tholin and its fuel; etchcap in its hollows. (built)
- The fishery of creepy dark pool creatures, living in the pools **(his mark; unbuilt)**.
- The ordinary wreck field. (built)
- **The hidden ship:** cover that builds on a quiet, dark, landed ship and breaks on engine start; probes that
  still come; the report that ends the cover and restores the ordinary search. (the cover meter and probes are built;
  the engine's start breaking the cover and the pursuit reading the cover are not) **Moved in by this rewrite.**
- **The grain wears the hull:** etchfall on the outside of the landed ship; a roofed lean-to, patching by hand and
  the ship's light screen as the answers. (unbuilt; campaign layer, as every ship touch is by his card of
  2026-10-01; on the shared hull-wear machinery; his ruling of 2026-11-18)

**0.2.0, Lightfall and the long stay** (as he approved on 2026-11-17, except the line above)
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The fold lamp, reached by ordinary research **(his mark; built)**.
- Living light: vines that turn to light and a picked berry that lights its carrier **(his mark; unbuilt)**.
*Already here before that answer:*
- The brood at the bottom of Lightfall: the landscape-sized sleeping mother, the clutch, the bone field, one wake
  meter fed by greed, the egg, the storms that follow a stolen egg home, the summing that *"never stops growing"*.
- The Ship in the Wall and the fittings it yields; the great bone aboard. The ship takes four kinds of part and
  refuses three, in plain words: *"The ship will not take this. It does not want to be something else."* Where the
  greed line lies may be learned by saving and loading (his words: *"that's pretty normal in these games"*).
- The cryptid: rings, stocked dens and caches the sorter may or may not have made; the unwatched exchange; a clear
  pocket around nothing; whispers, tales and the long-stay dream.
- Drifting clear pockets outdoors; the nevarithia's worn knot of Dark and its release at death.
- A summ answering a Witchfire storm; summ regeneration and its hurt in daylight.
- Trade ships unable to find a covered ship.
- The rough way in: gust shear knocking a ship that arrives without its screen up. (unbuilt)
- Learning heat-folding by watching warm air, with its letter (he left this open: *"We'll make that determination
  later."*).
- The roster's bespoke behaviours not yet built (corpse-stripping, spine spray, hungry digging, and the like);
  glow-globe poison; fungus spores.

**Later**
- The four darkness rites the deep dark teaches (the Dark Vigil, the Blind Offering, the Snuffing, the Lightless
  Burial): campaign layer, and deferred with every biome rite by his ruling of 2026-10-23, *"hereby documented and
  deferred to v2."* The first version of this page had them at 0.2.0. Each is found at a place a hiding crew
  would pass: an inscription where no light has reached, a Nhaleth circle, a ring of dead lamps, the rescue ship
  in Lightfall. A fifth thing waits with them, the Unlit Wedding. The Snuffing's reason is the hide's own: the
  hungry god is starved by *"staying dark, hidden, and unfought"*.
- Fugitive holds, seep-works and their explosions, the wind-farm ruins as inhabited sites: campaign layer.
- Lightfall as a landmark on the world: authored at the one painting pass.
- The crags' place names (Gray Crags, Rimewall, Twilight Crags, Sunreach, Nightspill, Coldstone, The Verge): for
  the same painting pass. They exist in no other Abyss file.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Gust turbines and gust power (cut by card, 2026-10-01).
- A ship touch in the free tier (declined by card, 2026-10-01).
- The lasting etch scar, moths on the ship's own lamps lifting the cover, and the heatless stealth lamp (passed over
  on his card of 2026-10-01; they stay down by his answer of 2026-11-19, and he can bring any one back by name).
- Any on-screen Nhaleth; the name "Forsakens" for them (his words, 2026-10-01).
- Anything that reads as a fantasy dragon: no fire breath, no hoard, never the word (his words, 2026-10-01).
- Geothermal anything; steady wind; water rain; permanent clear weather; clean sensing; sun-fed residents (the
  sheet's bans, all kept).
- The four Lightfall options he did not pick (the Sink, the Lowered, the Mercy Engine, the Lantern Tide).
- Six animals he cut on his sheet of 2026-10-05: the dusk rat (*"No longer needed, cut."*), the frostling, the
  night ave, the sand prowler (*"doesn't belong here"*), the shadow charger and the thunderox.
- Ship and light ideas put to him on 2026-10-01 and not chosen: moths drawn to the ship's own lamps as the free
  tier's hide; cold-burn cells, a heatless "stealth light"; grafting glow onto any tree; a vigil rite at a ring.
- This biome as the sea floor (his first idea of 2026-08-13, overtaken by his sheet of 2026-09-06).
- Any eclipse: *"There are no eclipses on this planet"* (2026-10-01). The nevarithia's death looses its own knot
  of Dark and nothing in the sky.
- The natural-placement worker and its biome-rarity slider (his ruling of 2026-08-15 and 2026-08-18: no worldgen, ever; no setting that could roll a second world).
- **Recommended for dropping, not yet his:** gill-ash as a second fuel line; the unused donor weather copies.

## NEEDS HIM

None open. Every entry is answered (next section).

Not a question: the Abyss has no locked Designer tree. Not asked again: where the greed line lies (his waiver),
the gust turbines (cut), the rites (deferred by him).

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. **[scope] The hidden ship in 0.1.0.** *His ruling:* the move card of 2026-11-18 (*"Move it, list every move"*). The
   hide stays in 0.1.0 and is on the move list. It is the Abyss's signature, so it holds under any answer to the
   first-version size question.
2. **[other] Sharp-edged clear pockets outdoors.** Off until 0.2.0. The built engine ties outdoor Dark to one outdoor
   temperature, so it cannot make them yet. *Delegated call.*
3. **[cover] Does an Unveiling expose the ship?** Yes, while it lasts. The Dark is gone, so its cover is gone: for the
   hours of an Unveiling the search runs as on open ground. **This changes the design's default.** Was: *No*. Undo:
   set it back to *No* here and strike the cover lines added to "The Unveiling" and "The ship while it sits here".
   *Delegated call.*
4. **[scope] "Danger becomes more frequent" the longer the crew stays: which version?** *His ruling:* the move card of
   2026-11-18 (*"Move it, list every move"*): 0.2.0, as the hide's clock, with the cryptid's signs.
6. **[hull] Wear against the hiding rule.** *His ruling:* his card of 2026-11-18, hull wear *"Yes in 0.1.0"*. The
   "salvage and progress — not hit points" note is not his words. Both stand: the wear is slow and answered by hand,
   and it is not the hide's main price.
7. **[other] Is Lightfall's bottom clear or dark?** His sheet wins: clear above (*"the one place the Dark always
   dies"*), with the brood in whatever dark the chasm floor keeps. The biology draft's sentence stays for him to edit.
   0.2.0. *Delegated call.*
9. **[cover] Pause, or four times slower?** *His ruling:* his word of 2026-11-18 (4:09 PM PST): *"Going under the
   ocean is like the Dark... VERY concealed. But nowhere pauses it indefinitely."* The Dark is the top level of cover,
   and the top level is the built fourfold delay. Nothing pauses the search for good, a ship holding its cover
   included. This later word overtakes *"full dark still pauses it"*.

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

5. **[hull] The lasting etch scar.** *His card of 2026-11-19 (declined ship ideas):* they stay turned down. No lasting
   mark; the hull wears and is repaired like any damage. He can bring it back by name.
8. **[other] Moths on the ship's lamps lifting the cover, and the heatless stealth lamp.** *His card of 2026-11-19
   (declined ship ideas):* they stay turned down. Both are on the Dropped list.
