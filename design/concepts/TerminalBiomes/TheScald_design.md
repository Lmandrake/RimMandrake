# The Scald: the design, seen from the ship

**Status:** the one design document for the Scald (`RM_TheScald`), written 2026-11-18 on the owner's instruction to
see every biome "through the lens of Utinni", and read in full this time. The Scald's biome, beach and weather live
in `src/RimMandrake/TerminalBiomes/`; its sea floor lives in `src/RimMandrake/DivingInteraction/`
(`RM_SeabedFloor_TheScald`). The same day's combined four-sea design read the Scald's largest sources by heading
only; it was retired on 2026-11-18 and kept only in git history, commit `b2530669e5`, once each sea had its own design. What this
design corrected against it is at the top of `design/concepts/TerminalBiomes/TheScald_rewrite_choices.md`. None of
the Scald's older source files has been deleted. This is a design document only and it launches nothing.

**Design Version this aims at:** 0.1.0, the stop.

**Kind, checked against the sheet's own header and bans:** a sea, and by his words a sea with exactly two places.
*"There's no 'on the surface of the Scald.' ... 'on the seafloor' experiences where bubbles would be appropriate
(you're under boiling water), or on the beach next to the Scald."* (owner, 2026-11-01.) *"You can't 'dive' as an
individual pawn nor return as one. It's ship or nothing."* (owner, 2026-09-26.) *"Now the ship just flies to a new
planetary layer called sea floor."* (owner, 2026-10-01.) So the visit below is written twice where the two places
differ: **the floor**, under 350 metres of boiling water, and **the beach**, under the steam.

**Who reads this next:** a Designer run on the concept is handed the list of files in
`design/concepts/TerminalBiomes/` (`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in
its path by sitting here. Nothing in the pipeline reads it by name. The mod has no locked sheet or tree. Its
pipeline material is the cleanse proposal of 2026-11-17, never applied, and one thing older and better: three card
answers he gave about the Scald's floor on 2026-11-10 (`design/RimMandrake/designer_codex_2026-11-09/TheScaldFloor/
ANSWERS_OWNER.md`), which this design is built around and which the cleanse did not use.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "In source" means
I found the def or class by name on 2026-11-18; it does not mean it has run. Nothing about the Scald has passed a
live check: the mod's own script reads *"NEVER RUN LIVE"*.

---

## What this place is

> *"The kettle at the centre of the world: every river starts here, boiling. Life here is cooked and proud of
> it."* (owner, picked by card, 2026-10-20)

> *"A crater sea that boils. Volcanic heat rises under it and the high dayside sun stands over it, and between the
> two the water never rests... **A place of roiling wonder**."* (`the_scald.md` §1; the bold words are his)

His three answers of 2026-11-10 are the whole brief for a stop, so they go first, word for word from the card:

- *What makes the depths worth visiting:* **"A thriving world inside the heat: life flourishing in the depths
  leads, with wonder and understanding the herds worthwhile beyond extraction."**
- *What a vent warning lets the crew save:* **"Prepared crews finish a short job. Learning the reliable gathering
  of sail creatures and the vent cycle allows calculated work through the warning before retreat."**
- *How long good preparation lets the ship remain:* **"A useful working visit: a well-equipped expedition can make
  several purposeful outings, explore and recover cargo before withdrawing when cooling or supplies become
  inadequate. Uses ordinary room heat, power and equipment, not a special colonist heat system."**

That last answer was already a description of a ship that leaves. Nothing in the Scald had to be bent to fit the
lens; it had to be read.

**The floor** is a pasture. At the bottom *"the boil gentles to mere heat"*, and there is ground to walk on. The
sheet's economy in one line: *"The mats coat, the walkers mow, the dung feeds, the silver darts, the sails ride:
one economy, wholly submerged."* It is dark down there. By his card of 2026-09-25 visibility on this floor is
*"light-based only"*, and a day later he called the Scald *"dark on the bottom"*. What can be seen is what glows:
cyan in the boiling pools, ember at the tips of the glass coral, one warm bead on each kettlewick, and the ship.

**The beach** is the kettle's lid. *"Cyan glow under white steam — the sea that is also a forge."* White steam
stands over the water all day; every few days it lifts for a still day and the wrecks in the shallows show through
the cyan. He asked on 2026-09-25 for that steam to be *"really beautiful and interesting (and deadly without
protective gear)."*

**The water is never drink.** *"Fouled, not toxic."* The sheet's hardest ban: *"no def, tech, or story renders
its body drinkable; only its distilled breath."* A crew of desert scavengers parks at the bottom of the largest
body of water they have ever seen, and drinks what it brought.

**Seen from the ship, the base is the ship and the ship is getting warmer.** The crew are small, hooded, and
*"adapted only to their parent desert biomes"*. Dry heat they know. This is the other kind.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew halves every wait and a hidden one doubles it. (The arithmetic is taken from
"The clock on any stop" in `design/concepts/Greentide/design.md`, not derived again.)

**How long a stop here can last: about six weeks, floor or beach, and that is the outer edge.** His ruling of
2026-11-18: *"The numbers you're generating are likely the outer edge allowable for each biome, and that's just
fine. Go with that."* With one step of cover (below), the ladder's arithmetic gives a probe on day 7 to 11, a first
fight in the third or fourth week, and nothing past about six weeks. On a still day the beach has none of that
cover for a few hours.

**Few crews will see that edge.** His own answer is the practical one: the ship withdraws *"when cooling or
supplies become inadequate."* The Scald's pressure is measured in hours (a vent's cycle), days (the rooms warming)
and what was in the larder, so everything it does can be seen inside a stop.

**`UNSETTLED`: how the Empire's ladder reaches a ship on a sea floor.** No source says. It is the first question
under `NEEDS HIM`, as it is for the other three seas. The sections below assume only what is safe in every answer:
the clock runs, the probe comes, and the bombardment does not care about water.

---

## The first minutes

**On the floor.** The ship goes down through the steam and then through the boil, and sets down in the dark on
sediment the def calls *"compacted enough"* to walk. No weather follows it down: by his card of 2026-10-23 the
steam sky belongs to the beach map only, and under the sea the weather is bubbles (his words of 2026-11-01: *"File
the bubble design too for underwater experience"*; the design is filed and not yet written). Bubble lines climb
from the vents, and translucent bells are riding them, heeled over, sails up. Somewhere past the lamps something
the size of a house is moving, slowly, with company.

Before the first outing is over the player should have seen three things without going looking: a boiling pool
glowing cyan with a ring of cooler water round it; a flotilla of sails on a bubble line; and the herd.

**On the beach.** The ship comes down through white steam onto dry shore beside water that moves. The margin is
calm, the shallows ripple, the deep never stops (the owner's own three-way description, built). Geysers thump along
the shore: this is *"the vapor law's second densest ground after the Forge."* Sight is short and soft. The hatch
opens and the air comes in.

## The first day

**On the floor.**

- **The ground is hot and the pools are worse.** The floor is 55 °C everywhere, which is ordinary heat on the
  thermometer and ordinary heatstroke if a crew member stays out. Boiling pools, clustered at the vents, burn
  whoever stands in them. Around each boiling core lies a ring of the water that only comforts. *"The water burns
  to touch and comforts as it burns."* Step back onto the sediment and the burning stops.
- **The pasture.** Rainbow mats, *"oddly fuzzy"*, banded by temperature: *"the Scald's is the oldest truth"* among
  the planet's rainbows. With them a small garden of things that each survive the boil by a different trick and
  say so in their shape: a flat silver lace that mirrors the heat away, a finger-high string that *"boils itself
  on purpose"* and sweats one clean drop from its tip, a man-high fan that leans into the dung-fall *"like a
  congregation"*, a barrel sponge heavy with hoarded metal, a shrub in a sleeve of its own bubbles, a candle that
  never stops melting, a copper reed that lives only on the line where simmer becomes boil. At the vents, glass
  coral: *"centuries of glass, one season of flesh."*
- **The herd.** The sheet's signature and the owner's centrepiece: bottom-walkers, *"armored, slow, pastoral"*,
  *"huge, sea-urchin-like, very alien"* in his typed words of 2026-09-25, when he also named them: **the Mighty
  Vu'uul**. (In source the creature is labelled *iridesce*; see `NEEDS HIM`.) *"A domed, heat-glossed giant that
  walks the Scald's floor on a hundred short thick legs... It barely notices anything the size of a person; it is
  simply very large and has somewhere to be."* They never attack. Where one grazes, the mat's pigment-rich
  underside is left briefly bare, and that is the crew's work: follow the herd, gather behind it, stop when it
  turns.
- **The small life.** Every kind the line can bring up is alive down here and written from its own catch: a
  mirror-skinned sliver that *"lives in the boiling column itself"* and moves as one cloud; a shrimp-thing *"pink
  from birth as though it had already been cooked"*; an eel in the mats' own colours living under them; a crab
  that *"looks like a piece of the vent walked off"*; a knot of filaments of which *"nobody knows which way up"*
  it goes; a golden gas-sac that gulps itself taut in the roar and sighs out in quiet pools; and the walker's
  hand-long cousin working the bands.
- **The sails.** The saal, *"the biome's signature silhouette and kindest resident."* *"Harmless, gel-bodied, and
  never in a hurry."* They stay on their bubble lines. Watch where they go.
- **The rooms.** By evening the bunk rooms against the outer hull are warmer than the ones inside.

**On the beach.**

- **The steam is a clock.** Out in it, unroofed and unprotected, a crew member goes from damp to scalded to
  steam-burned by stages a player can read, and by his card of 2026-09-25 is dead in under two days. A roof stops
  it; the ship is a roof. So work on this beach is done in shifts from the ramp.
- **The water burns.** Wading costs burns, more in the deep than the shallow (his word: *"Yes, deep water should
  burn harder"*). The sealed cool margin is the one water that does not, and the only place a line can be put in.
- **What lives here is not hurt by any of it.** *"Likely should make its own creatures immune to that"* (owner,
  2026-09-25); natives carry one tag that the steam, the boil and the steam devils all read.

## The first week

- **The crew learns the vents.** One vent at a time goes quiet, then warns, then discharges. During the warning
  every sail on the map gathers over that vent. *"The same gathering ALWAYS precedes a discharge"* (the built
  component's own header), so the sails are a tell a crew can trust, and his card says what the trust buys:
  *"calculated work through the warning before retreat."* The discharge burns and interrupts whoever is still
  there.
- **The crew learns the herd.** A grazing walker stands still and can be worked beside. A moving one tramples what
  is too close; by his card of 2026-10-09 it *"tramples the colonist and deals damage (not push-aside). A warning
  to the player is owed with it."* Two grazing lanes converging is the moment to back off.
- **The ship gets smaller.** The heat comes in through the hull's outside faces, so a sprawling ship pays more
  than a tight one. The crew chooses which rooms get the coolers and the power, and lives in those. Nothing seals
  and nothing stops a launch.
- **The pan gives up what it swallowed.** Wrecks lie on the floor and in the beach shallows, *"cooked clean"*:
  no rot, no bodies, nothing guarding them. On the floor old sponges coat them for the iron, and *"salvagers read
  a thick thurl-coat the way prospectors read an outcrop."*
- **On the beach, the still day.** About every fourth day the breath pauses for half a day or more. The clock
  stops, the shallows clear, and the wrecks show *"through cyan glow."* It is *"a pause in the breath, never in
  the boil"*: the water burns exactly as before.
- **The supplies run down.** Water most of all.

## The ship while it sits here

Three things every biome design now states, by his rulings of 2026-11-18.

**Cover from orbit: partial, one step, in both places.** His card: *"Canopy, steam and fog slow the search by one
step; full dark still pauses it."* The beach is under standing steam. The floor is under the same steam and a
boiling sea. Two covers are still one step. The Scald has one more claim that is his own, from the Rust
Cathedral's history (2026-09-10): the machine dumps its heat here because *"it's an easy way to covertly dump heat
to avoid detection"*; in the amendment's words, *"a boiling crater lake is the one place on the planet where more
heat is invisible."* A warm ship in a boiling lake is hidden the same way. This design claims no more than the one
step for it. (`UNSETTLED`: whether a still day costs the beach its step while it lasts. Assumed not, to match the
Greentide's clearing; the other answer is attractive here, because the still day is when the crew most wants to be
outside. Whether the dark floor counts as "full dark" is part of the one question the shared-machinery file
already asks for every sunless place; default here is no.)

**Wear on the hull: the sea warms the rooms.** His ruling: *"Yes in 0.1.0. It's easy, and most of the biome
already talk about this."* The Scald's is named, ruled and in source. By his card of 2026-10-02, the Immersion
Berth: *"a parked ship's rooms slowly heat; doors never seal, launch never blocked."* (The sitting's agenda called
it "the Scald's ship-touch voice", deferred there from the Grey Sea's sitting.)

- *What the player sees.* Room temperatures on a ship parked on the floor climb over days, fastest in rooms with
  the most outside wall. No new meter: his answer of 2026-11-10 is that it *"uses ordinary room heat, power and
  equipment, not a special colonist heat system."* The ship gets worse *"as a bedroom, hospital and workshop"*.
- *What answers it.* Coolers and the power to run them; a compact ship; choosing which rooms to keep; leaving.
  For a crew that owns one, the ship's thermal veil, which by his shield ruling of 2026-09-02 would *"reflect all
  external heat outward... but also reflect all internal heat inward, so the temperature slowly climbs anyway"*:
  a slower bill, not a cancelled one.
- *What does not answer it.* Holding the water off. His ruling, same day: *"Slow pressing things move through all
  shields... This is why nothing 'holds out water,' it just doesn't work that way."* The sea is against the hull
  whatever field is up.
- *It never traps.* *"Doors never seal, launch never blocked"*; and his general ruling that the hull *"can take a
  lot of damage in most situations, so no environment is immediately lethal"*, with the ship advising *"but no
  more than that."*
- *The frame.* The shared hull-wear frame is `src/RimUtinni/ShipShields/`. Its exposure tracker calls a map hot
  at an outdoor temperature of 58 °C or more (`ShieldHazardUtility.ExtremeHeatThreshold`); the Scald's floor is a
  constant 55 °C, so today the tracker does not see this floor at all, and the Berth
  (`RM_MapComponent_ScaldImmersionBerth` in `DivingInteraction`) does the whole job from the free tier. What the
  frame needs is to know the Berth is this sea's wear: say so in the landing advisory, and count a running
  thermal veil against it. This design does not add a second heat wear on top. The hottest beach tiles (air +44
  to +61 °C by the sheet) would trip the tracker's built heat case as it stands.
- *On the beach* the ship is a roof in a steam bath: no source gives the steam a bite on metal, and none is added.
- *The approach.* The sources name turbulence once, over the Scald's mountains, where it hides the Spire
  (*"visible only occasionally due to the atmospheric turbulence over the Scald's mountains"*). His hull ruling
  lists *"rough weather turbulence in the approach"* as a kind of wear. This design does not turn the one into the
  other; it notes the line exists.

**Fuel: the emergency route only. Buy it from the neighbours.** His ruling: *"Every biome has a fuel source, but
for most its the hideously slow route of rendering biomass into chemfuel. Uselessly slow, only for emergencies...
You can also buy it (the intended motivation to have to trade constantly, very Jawa)."*

- *The emergency route* has mats and carcasses to render. It is the slow route.
- *No source makes the Scald rich.* One plant burns: the seepcandle's wax, of which the flora pass says *"the wax
  burns"*, with its yield left an open question to him since 2026-09-27. It is a scrap, written here as a scrap.
  Gas seeps were offered for this floor and declined by card on 2026-09-25.
- *The richer source is next door, not here.* His older ruling (2026-08-15, "Fuel is life") lists *"helixien gas
  (volcanic/deep-desert tiles)"* among the paths to fuel, and the Scald's rim is the planet's one volcanic
  province. That belongs to the rim's own tiles and their designs.
- *Buying it.* The world definition seats the Deepwater Compact *"two on the Scald despite the Empire"* and the
  Wildsteam on *"the Scald's jungles"*. What either stocks is `UNSETTLED`; both are campaign layer. What the crew
  has to sell is in "What the crew takes away".
- *Spending.* The Scald charges power, not fuel: the coolers. On the beach the geysers are free geothermal power
  for whoever builds on one (the base game's own). The floor's vents take only a condenser.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The herd turns.** *On screen:* three domed giants on a hundred legs each, grazing a rainbow floor in the
   lamplight, and behind them a line of hooded figures picking up what the grazing bared. The lead giant turns.
   A warning. The figures scatter; one is a step slow and is walked over. *Why it lands:* nothing attacked
   anyone. It *"barely notices anything the size of a person."*
2. **The sails all go one way.** *On screen:* every bell on the map tacks over to the same vent and hangs there.
   The crew that has been here a week finishes its last haul and walks. The crew member who has not keeps working.
   The vent goes. *Why it is funny:* the warning was thirty jellyfish wide.
3. **The wrong pool.** *On screen:* a Jawa wades into the glowing core of a pool after something shiny, comes out
   burned, sits down in the ring beside it, and gets the bathing thought. The water *"hurts nicely"*.
4. **The piece of the vent walks off.** *On screen:* a scavenger reaching for a promising lump of mineral crust
   on a chimney, and the lump leaving. The karrash *"looks like a piece of the vent walked off."*
5. **The warm ship.** *On screen:* bedrolls dragged into the one cooled room, the hospital moved inboard, the
   workshop dark, and a cooler humming against a wall with the whole sea on the other side of it.
6. **Shift change on the beach.** *On screen:* a hooded figure coming up the ramp out of the white with
   "scalded skin", passing the next one going down. *Why it is funny:* they were issued hoods at birth and this is
   the first weather the hood is wrong for. (The built scald wrap is *"a hooded cloak"*: *"appalling to wear in
   the Anvil's heat, because the same seal that keeps the boil's breath out keeps your own in."*)
7. **The still day.** *On screen:* the steam thins, the lake turns to clear cyan, and three hulls are lying in
   the shallows where there was only white. The whole crew is on the shore inside the hour. The water burns just
   the same.
8. **The gas-bag.** *On screen:* a golden sac the size of a head swelling taut as a vent roars, then sighing flat
   in a quiet pool. No use at all. The crew watches anyway.
9. **The guardians** (0.2.0). *On screen:* whip-armed things coming off the herd's flank at a gatherer who strayed
   inside their ring, and breaking off the moment the gatherer is out of it. His words: *"big leggy things like
   brittlestars gone wild. They think they're defending the Walker."*
10. **Gold on the floor** (0.2.0). *On screen:* lumps of crusted gold and silver lying in the open at the edge of
    a chimney field, and a crew that mines nothing and salvages everything deciding how much burning a robe-full
    is worth. His ruling: *"Ore is NODULES you simply gather"*.
11. **The swarm** (0.2.0). *On screen:* a cloud of orange-white sparks pouring out of a chimney field at whoever
    went in for the pearl on its flank.
12. **The gauge** (0.2.0). *On screen:* a Jawa hooking a gauge to a capped pipe end older than the Republic,
    reading it, shaking its head, and walking to the next one. One of the five runs *"still pulls warm water
    home."*
13. **Something at the edge of the water** (0.2.0, the beach). *On screen:* through the steam, at the deep-water
    edge of the map, a back the size of a building, there for a while, then gone *"unless harassed"* (his card,
    2026-11-01).

## When the Empire arrives

How it arrives on a floor is `UNSETTLED` (above). What the Scald does to whoever comes, in 0.1.0:

- **On the beach, nobody shoots well.** The steam costs accuracy for everyone (built). A still day gives sight
  back to both sides at once.
- **On the beach, the steam is on the Empire's clock too.** It reads heat armour on whatever a pawn wears;
  whether a trooper's kit has any is `UNMEASURED`. An unroofed siege camp is standing in it.
- **The water charges everyone.** *"No boiling-immune traversal for free"*, by the sheet's ban, and nothing waives
  it for a uniform.
- **On the floor, the vents and the herd keep their own time.** A discharge burns *"anyone near it"*. A moving
  walker does not check allegiance. (`UNMEASURED`: the trample is written for colonists; whether it lands on
  others.) A crew that has learned the sails knows where not to stand; a landing party has not been here a week.
- **And the Empire is close.** Of its three ground holdings on the whole planet, one is *"the Scald Gate"*,
  which the world definition calls *"the one breach in the Spine"* and draws running down toward this sea's rim.
  What that does to a search that starts here is `UNSETTLED`; no source connects them.

## Who else attacks; who hates the Empire

- **Nothing here hunts the crew in 0.1.0.** *"No native land predator hunts the water"* (ban 3), the walkers
  *"never attack"* (his typed word), and the sails are the kindest thing on the planet. The Scald's dangers are
  the place and the crew's own carelessness. That is deliberate and it is a rest the campaign needs: the stop
  where the animals are a wonder. 0.2.0 adds the two threats he typed for this floor, both of which defend
  something and neither of which hunts: the guardians at the herd and the swarms at the chimneys.
- **The Deepwater Compact** hold two seats on the Scald *"despite the Empire"* (world definition); the steam-catch
  is their *"headwater interest (whoever holds catch-rights holds the monopoly's source)."* Campaign layer.
- **The Wildsteam** have two jungle seats on the flanking groves, *"a day's walk from the sacred baths they
  quietly prefer to their own Miasma pilgrimage's odds."* Campaign layer.
- **Two faiths hold the shore** and read the same water as opposite proofs. Campaign layer.
- **The Rust Cathedral is hiding in this lake.** It cools its mind through the Scald so that nobody sees the
  heat, and by his plot canon of 2026-09-10 *"the player's Rakatan gravship flying around agitating the Empire is
  exactly the danger it fears."* A crew that brings the Empire's search to the Cathedral's hiding place has done
  the one thing it dreads. What it does about that is the campaign's, and `UNSETTLED`.
- **In the mountains above** stands the dark tower, which is the Spire: *"They are the same building. It's in the
  mountains, visible from the huge sea/lake of the Scald"* (owner, 2026-10-10). Its defenders and the Assailants
  inside it are another design's. A Helix outpost holds the ocular forest on the mountainous shore.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The rooms: more heat than the ship has coolers and power for.
- The larder and the water tanks. Nothing in this sea can be drunk.
- On the floor, heatstroke on every errand: the length of an outing is set by ordinary heat.
- On the beach, the steam: every job is a shift, and injuries pile up in the one cooled room.

**Stay, longer than the Empire would like:**
- A tight ship with a cooled core, and enough power.
- Knowing the sails and the herd, which turns the floor's two dangers into a timetable.
- Nothing hunting the crew.
- Steam and sea over the ship, one step slower from orbit (his card of 2026-11-18; unbuilt).
- On the beach: the ship as a roof, heat-armoured gear, the still day, and a geyser to power the coolers.

## What the crew takes away

- **Pigment mat**, gathered behind the herd: the raw stuff of deepfire, the luminous pigment (its own mod, by his
  word *"Required by the Scald mod"*). A fresh mat *"dies within a day, and dies at once if chilled"*, so it is
  pressed at the Scald or it is lost. A cargo this stop alone gives.
- **Steel from the sponges.** By his card the thurlsponge *"yields real Steel"*: *"the floor's kidney pays in
  metal."* The one plant a salvage crew strips on purpose.
- **Wrecks, cooked clean,** from the floor and the shallows.
- **The catch,** nine kinds, taken at the beach (and from the cool rings on the floor, where the build put the
  fishable water). It comes up cooked.
- **Keepsakes:** kettlewick collars, glass spires, karrash shell, ekkel knots. Small, pretty and saleable.
- **Walker plate**, the stuff the scald wrap is stiffened with. (`UNSETTLED`: how a crew now comes by it. Its only
  built source was the pawn-dive hunt that the ship-or-nothing ruling retired.)
- *0.2.0:* **clean water off the steam** at the beach, *"the tap of the world"*: on a desert planet, the best
  trade good there is, drawn from under the nose of the people who claim the monopoly on it. **Nodules** of gold,
  silver and uranium, iron that smelts to steel, and the pearl that grows on the chimneys. **What the coolant
  manifold's locker held.**
- *Campaign layer, one hex of this sea only:* the mineral-crusted wreck he asked for by name. *"I love the idea of
  a crashed ancient Rakatan vessel, encrusted in minerals, with a few goodies still left."* The goodies he chose
  are things a ship wants: a great turret that can be refitted onto the hull, batteries, a degraded shield
  emitter, and a sealed archive.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The ship lands on the Scald's own floor, with its ground, pools, vents, mats, plants and animals, and leaves again. | A landing and a launch. | A generic empty floor fails. So does a floor reached any way but the ship. |
| On the floor, boiling pools burn a visitor and the ground between them does not; the ring round a pool comforts and does not burn; none of it can be drunk. | One pawn on sediment, one in a pool's core, one in its ring, one sent to drink. | A native animal in the same core is unhurt. A floor that burns everywhere outside the hull fails. |
| No weather from above reaches the floor, and the floor is lit only by what glows. | A stay on the floor through a steam day and a still day above. | The beach map over the same hours shows both. |
| Every kind the line brings up is alive on the floor. | Fish at the beach; find the same kinds below. | A catch that exists only as an item fails. |
| The herd grazes the mats; where it has grazed, pigment mat lies bare for a while and the crew can gather it; the work moves with the herd. | A herd, a gatherer, and the hours. | Mat far from any walker is not offered. A map with no walkers offers none. |
| A moving walker tramples a visitor who is too close, after a warning; a grazing one can be worked beside. | One pawn beside a grazing walker, one in a moving walker's path. | A downed pawn is stepped over, not trampled again. The walker never takes an attack job. |
| The sails gather over a vent before it discharges, every time; the discharge burns and interrupts whoever is near. | Several cycles of one vent field, with a worker who leaves at the gathering and one who stays. | No discharge without the gathering first. Sails drifting between vents at other times are not a warning. |
| A ship parked on the floor warms room by room, most where it has most outside wall; cooling holds it; no door seals and launch is never blocked. | A ship parked for days, one room cooled and one not; then launch. | The same ship on another sea's floor does not warm. Dividing a room with inside walls does not raise its load. |
| On the beach, the steam stands, lifts for a still day, and returns. Unroofed and unprotected in it a visitor sickens by readable stages and can die; a roof, a still day and heat-armoured clothing each answer it; no clothing makes it free. | Three pawns on the beach through steam and a still day: one in the open, one roofed, one in a boil-suit. | A native in the open is unharmed. The clock does not run on the floor map. |
| On the beach, boiling water burns a wader, more in the deep; the cool margin does not; wrecks in the shallows can be salvaged at that price. | A wader in shallow, in deep and in the margin; a salvage job on a still day and a steam day. | The water burns the same on a still day. |
| The Empire's search comes one step slower here than for the same crew on open ground. | The same crew, as loud, landed here and on an uncovered tile; read the search's next contact on both. | A crew made loud here loses the step. |
| Nothing vanishes. | A trampled pawn, a vent-burned pawn, a steam-killed pawn, each with a save and reload in the middle. | |

No row pins a rate. How fast a room warms, how long a still day lasts, how many days the steam takes and how
wide a herd's ring is are tuning, and stay out of any bar. (His card did put a number on the steam: *"dead in
under two days."* A number binds only where he said it; it is recorded here and not written into the row.)

Settings: a switch per major feature in both places, defaults as shipped; everything off leaves a hot floor and a
steamy beach with ordinary life on them (standing rule, every mod). Most of these switches are in source already
(`RM_DivingSettings`, `RM_TerminalBiomesMod`).

## Shared machinery

**Featured here** (the Scald is where each is vital and should be proven):
- **The sea warming a parked ship.** The heat case of hull wear, done with room temperature and nothing else. The
  one wear in the game that is answered by the shape of the ship.
- **Wildlife as the forecast.** "A sign, then the event, then a window" is shared by half the planet; here the
  sign is an animal's behaviour (`RM_MapComponent_ScaldVentForecast`).
- **A herd as a moving worksite** (`RM_MapComponent_ScaldWalkerGrazing`, `RM_WorkGiver_GatherGrazedMat`,
  `RM_WalkerTrampleKernel`). No other biome has work that walks.
- **Standing steam with still spells, and an exposure clock answered by ordinary heat armour.** The weather pulse
  is the Forge's class pointed the other way (`RM_GameCondition_WeatherPulse`); the clock is the shared
  `RM_HediffComp_EnvironmentalExposure` that the Miasma and the Rot also use. His card of 2026-10-08 folded the
  Scald's own protection stat into the base game's heat armour, so no second kind of heat exists here.

**Shared with the other three seas:** the ship as the only door (`RM_SeabedLayer` and its floor maps); catch with
a living counterpart; calm underwater weather.

**Merely active here:** the one sun from geometry, which on the floor is nothing and on the beach is high (the
Scald's built sun extension (heat kind ambient, plus 15 °C) is due to become plain air temperature under the one-sun design of
2026-10-19; not yet done); natives never hurt or left thirsty by their own home (`RM_HazardNativeExtension`; his
ruling of 2026-11-01 that natives *"drink their own environmental water"*); liquid contact heat (`FlowWorks`);
agitated water (`RM_MapComponent_WaterAgitation`, built for this sea and usable by any); wreck salvage
(`Wreckage`); bone from butchery; the growth engine; the Empire's search and the visibility dial.

**Three ship systems built once for every biome, and what the Scald asks of each:**
- *Hull wear.* Recognise the Berth as this sea's wear; count the thermal veil against it; never count any field
  as keeping water out.
- *Cover from orbit.* One entry on the partial-cover list for `RM_TheScald` and one for its floor biome.
- *Fuel.* Nothing local. Sellers at the Compact's and the Wildsteam's seats.

## Scope

Every feature is in one bucket. "In source" is my search of 2026-11-18, not a pass.

**0.1.0, the stop**
- The floor as a real place on the ship's layer: walkable hot sediment at a constant 55 °C, boiling pools with
  their cool rings, vent fields, wrecks, calm, dark. (in source: `RM_SeabedGenerator_TheScald`; the dark is
  `UNMEASURED`; whether the ship can actually fly down and back is the layer's own owed live proof,
  `SEABED_DESCENT_ASCENT_1`)
- The floor's life: ten animals, eight plants on the roster and two at the vents, every catch alive below.
  (in source)
- The herd: grazing, the bared mat, the following job, the trample with its warning. (in source)
- The vent cycle and the sails' gathering. (in source; displacement of loose items by a discharge is not built)
- The Immersion Berth. (in source)
- The beach: steam sky and still days, agitated water, boiling water that burns, the cool margin, vents and
  geysers, wrecks in the shallows, fishing. (in source; the margin cove is unplaced on the beach map)
- The steam clock on the beach and the clothing that answers it: the scald wrap, the boil-suit, any heat armour.
  (in source; moved in against the cleanse, see `TheScald_rewrite_choices.md`)
- Natives unhurt by steam, boil and devils, and not thirsty beside their own water. (in source)
- Steam and sea as partial cover from orbit. (unbuilt; campaign layer, one entry in the pursuit)
- Fuel by the slow route.

**0.2.0, the stop with company**
- His floor of 2026-09-25, the part not yet built: chimney fields as three heat zones; the guardians (askirath)
  and the swarms (feen) with their nests; the swirl of small glowing life that follows a herd (ullium); walkers
  that lay the mats as well as mow them; nodules, the two crystals, Chimney Iron, Mother-of-Scaldpearl; unbranded
  ancient machines on every floor; marine snow and the shimmer band. (unbuilt)
- The Return Gallery: the broken coolant manifold and its locker. (in source)
- The dive clock and the gear he ruled for it: the two-axis matrix, the air bladder and rebreather, *"Locals make
  their own."* (unbuilt)
- Light draws things on this dark floor (his redirect of 2026-09-26). (unbuilt; no design yet)
- The beach's extras: steam devils, vent flashes, the steam-catch and distilled water, the walker seen at the
  deep-water edge, the sail scatter. (in source, except the walker's pawn)
- Sponge on wrecks as a placement of its own. (in source)
- The underwater bubble weather. (unbuilt; filed 2026-11-01)
- Buying fuel and selling water at the Compact's and the Wildsteam's seats. (campaign layer)
- The Rakatan vessel in its one hex. (unbuilt; campaign layer)

**Later (a crew that stays, a colony, or a second version by his own ruling)**
- The Royal Rind coat (waits on the Greentide's fruit) and vacuum suits as dive gear.
- The margin bath as a rite (his ruling of 2026-10-23 puts every taught rite in a second version); the two-faith
  shore, the witness trail, catch-rights politics.
- The boiling-lift; the steam-catch on a pipe network.
- Deepfire's whole craft chain beyond carrying the mat to a press.
- Forty colonists on a floor.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Diving or returning as a single pawn; the dive hatch; any place "on" the boil.
- The sandos here. His words on the Scald's review sheet, 2026-10-05: *"Move this to the Twilight Sea, it does
  not belong in the Scald"*, and of the elder: *"Rename this to the Gripping Terror and move it to the Twilight
  Sea."* The passing-shadow wonder of 2026-09-25 went with them.
- Mee and faa here (*"Put them in the twilight sea instead."*, 2026-10-02).
- A cold plant (*"No, this is silly. No cold."*, 2026-09-26). Brine pools (*the Grey Sea's*, typed 2026-09-25).
- A potable, drained, cooled or tamed Scald. Burn immunity anyone can wear. A second kind of heat.
- "No macro-life in the boil" (withdrawn by him, 2026-11-01).
- Kettle scale on the hull; steam and sound only (the two ship touches not picked on 2026-10-02).
- For the wreck: a navigation core (declined by card, 2026-09-25). For the floor: gem clusters and gas seeps
  (declined by card, 2026-09-25).
- The Unanswered Wound rite (offered 2026-10-02; he chose the bathing rite).
- **Recommended for dropping, not yet his:** the inert cross-biome switch (the cleanse's recommendation, kept).

## NEEDS HIM

1. **What does the Empire do about a ship at the bottom of a sea?** The same question each of the four sea
   designs asks. *The probe and the bombardment follow; the troops wait at the beach and meet the ship when it
   lifts* (default; it needs the fewest new things). *Everything follows:* troopers on the floor, and the Scald
   does to them what it does to the crew. *Nothing follows but the clock:* the floor is safe from all but the
   last step.
2. **Is the steam's clock still wanted, now that there is one kind of heat?** *Yes, in 0.1.0 on the beach*
   (default). His words asked for steam *"deadly without protective gear"* (2026-09-25); his card of 2026-10-08
   folded its protection into ordinary heat armour; his card of 2026-11-06 tuned the rind coat against it, which
   is after the one-sun ruling of 2026-10-19. *No, hot air only:* the cleanse's reading of that ruling
   (*"Volcanic/steam/fog heat is plain air temperature"*); then the beach is a hot, blind shore and the gear is
   only for wading.
3. **The herd's name.** He typed *"bottom walkers: The Mighty Vu'uul"* on 2026-09-25. The creature in source is
   labelled *iridesce*, with the *iridai* as its small cousin; no word of his was found for either, and he
   finished the Scald's art sheet on 2026-10-05 with the creature shown under the built label. *Vu'uul* (default
   in this design's prose). *Iridesce*, as built.
4. **Does every river start here, or end here?** Nothing in a stop shows it, so this design says only his line
   of 2026-10-20: *"every river starts here, boiling."* But the documents disagree and each side has his words.
   Typed 2026-09-12: *"the rivers flow OUT of the Scald... and you know this!"* The world definition's ruling of
   2026-08-21 and the sheet as amended in October say eight rivers end in it and none leaves, and the cleanse
   followed those. *Leave both: the rivers start here as steam and come home as water* (default; it is what the
   sheet's water chain already says). *Or rule one,* and the def text and the world document follow.
5. **Two ship ideas for the Scald that he did not pick, not revived here.** *Kettle scale* (mineral fur on the
   hull, scraped off): offered on the card of 2026-10-02 and passed over for the Immersion Berth; the agenda
   called it *"too close to the Grey's crust-and-chip."* *A navigation core in the Rakatan wreck:* declined by
   card, 2026-09-25. Neither card has typed words of his. Listed in case the hull ruling of 2026-11-18 changes
   his mind about the first.
