# The Lantern Deeps: the design, seen from the ship

**Status:** the one design document for the Lantern Deeps (`RM_LanternDeeps`, source `src/RimMandrake/LanternDeeps/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the
older definition sheet, the fauna and flora proposals, the review and the cleanse proposal as the place to read; what
happened to every idea in them is in `design/concepts/LanternDeeps/rewrite_choices.md`. Nothing has been deleted.
This is a design document only and it launches nothing.

**What kind of place this is (checked against the sheet's own header):** not a world-map biome and not a sea. It is
an **underground layer**: a cave map reached through a mouth on any nightside map at −40 °C or colder. *"Not a
worldmap biome (owner: 'that was a mistake')"* (`the_lantern_deeps.md`). **The ship cannot go down.** It parks on
the frozen surface above, and the crew goes down on foot and on a cable.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/LanternDeeps/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Deeps have no locked sheet or tree; their only pipeline material is the
cleanse proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"A blue lantern burning under the mountain, and a dead miner's suit walking toward it."* (`the_lantern_deeps.md` §9)

Under the coldest mountains on the planet the crust is thick and slow, and slow cold crystal grows big. The voids it
grew in are the Deeps: enclosed, still, humming, *"warm-by-comparison"*, lit from inside by **lanternstone**, the
blue crystal that carries light, and pastured by glowing fungus. *"Nothing here has a body in the ordinary sense.
The oldest minds in the caverns cannot move at all, and so they wear what the dead brought down with them."*

> *"A deep wondrous cavern of strange crystal life and haunted technology. Mineral riches for kings, until you
> realize they are both alive and intelligent."* (owner, typed, `biome_experiences_2026-10-20.md`)

> *"Nobody reaches this place without excellent technology; that is why the caverns are full of it, walking."*

**Seen from the ship, this is the best scrapyard the crew has ever heard of, and it is occupied.** Every corpse down
here was superbly equipped: exo-suits, droids, power cells, cutting gear. A crew that has spent its life stripping
wrecks along desert roads is standing over a shaft full of the finest salvage on the planet, in the dark, with the
light they carry telling everything alive exactly where they are. The sheet says who has tried this before: the
Junkers *"occasionally try and usually fail to get far enough"*, and today nobody mines here *"except maybe a very
rare Junker with a death wish"* (owner). The crew is that Junker, with a stolen ship idling overhead.

Two things turn every desert habit upside down. At home light is the enemy you hide from at noon and the comfort you
gather round at night; here *"we are blazing beacons begging to be messed with."* And at home a dead droid is stock.
Here it stands up and looks at the lamp.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last (the outer edge of a stay, not the usual one; owner's ruling of 2026-11-18).** The
ship is landed on a nightside host, so the clock is the host's, and the host is in full dark. His ruling of
2026-08-05 pauses the orbital search on dark tiles, and his card of 2026-11-18 keeps that: *"full dark still pauses
it."* By the rulings, then, a Deeps stop is among the longest on the planet, ended by cold, provisions and nerve
before the Empire. **As built it is not:** only the Abyss is on the pursuit mod's slowed list, so until the cold
hosts are added a Deeps stop runs the ordinary ladder: a first week nearly free, a first fight in the second or
third week, nothing past about a month. This design is written to work under either; the host designs own the fix.

**What cover this place gives, and which kind (same card).** Two different things, and the design keeps them apart:

- **The ship** gets the host's cover, which is darkness, and nothing from the Deep. A probe has to come close to
  see anything in the dark (built: in `EmpireLadderMath.Sees` a target on unlit ground is seen only from a few
  cells away, against a long sight line in light).
- **The crew** gets a mountain. Everyone below is under stable rock in a separate map: no probe, spotter or
  bombardment reaches them, and nothing the Empire sends counts a sighting on a crew it cannot see. The Deep hides
  people and cargo completely and the ship not at all.

So the Deeps make a specific and funny kind of hide-out: the safest place on the planet for everyone except the
one thing the Empire is actually looking for.

---

## The first minutes

The ship comes down in the dark onto ice or blue sand at forty below. From the air a natural mouth is the only
light for miles: *"a geode open to the aurora, glowing from below."* The other kind of mouth is a shaft head inside
the wreck of somebody's mining works, and the wreck is the first thing a Jawa notices, because it is full of good
metal nobody came back for.

The ship lands **beside the mouth, not on it**, and that choice is the stop. A ship that carries the **keel hoist**
(built: `src/RimMandrake/KeelHoist/`, a gravship part) can hang its cable down the shaft, send cargo and downed
animals up and down without anyone carrying them, and haul the whole haul straight into the hold. While the cable
is down the pilot's console refuses to launch: *"Reel in the keel hoist first."* A crew without the hoist walks
everything through the mouth by hand.

The first party goes down out of the killing cold into still air at room temperature, in the only light there is:
lanternstone blue, fungus glow, and their own lamp, *"a spotlight everything turns toward."* The cave hums.

Before the first descent is over the player should have seen three things without hunting for them: a dead miner
in a suit worth more than the crew's ship parts; something pale and winged turning toward the lamp from the far end
of a gallery; and a chassis that was lying down when the party walked past, standing, facing them.

## The first day

- **Light is a bill.** Work needs light, and sustained ordinary light on a crew member builds the cave's attention
  until a native hunter (the drinker, a pale moth that drains what it lands on) comes along a real route for the
  brightest one. The risk reads on inspect as quiet, building, drawn or cooling, and dim work is left alone.
- **One light is free.** A standing **Lantern**, a living colony crystal, is *"the only safe light that does not
  draw the others."* Work lit only by a Lantern draws nothing. Harvest it and it is ordinary lanternstone, a trade
  good, and ordinary light. *"Light now"* against *"light later, sold"* is a decision made for a Jawa: the one safe
  lamp in the cave is also worth money.
- **The dead are well provisioned.** Equipped corpses and dead droid chassis lie along the galleries and at the
  shaft bottom. This is the loot the stop is for, and it is lying in the open.
- **Some of them walk.** Near an aware crystal a dead chassis stands, worries at the rock without mining it, and
  turns to face a light it can actually see. Its inspect names the rooted crystal that moves it; the crystal's
  names its bodies.
- **The larder and the loom.** Puffer tendrils (they go on twitching in the bowl for hours: *"the squirming bowl
  that is not alive"*), nurrik and brellik to eat, prenna lace for cloth, thrakk for tough timber.
- **The roof talks first.** An unsupported span gives dust, sand and a rumble where it will fall, with time for a
  miner to leave or a prop to go in.
- **The cow gives fuel.** Candlers graze the fungus in small groups, each with a swollen yellow sac along its back.
  They can be milked for cold wax, which *"burns like chemfuel and needs no refinery."*

## The first week

- **The riches answer back.** The best lanternstone in the cave is a marked gallery the crystals keep. Selecting
  it, or designating mining in it, shows the mark and says what taking it will do. Taking it anyway, or hurting a
  mind or its body, wakes a finite number of dead shells after a visible wind-up, against the one who did it. They
  hold their gallery. They do not chase through the mouth and they never close the way out. (His answer of
  2026-11-10: *"Recognition changes the relationship, especially as the crystals start to defend themselves with
  droid bodies remote controlled."*)
- **One of them is company.** **Orun-Ghal** is a huge dead mining exoframe, the miner's skeleton still inside,
  walked by the crystals. *"It might not just mine as when animated it is controlled by the sentient crystals.
  Instead it becomes an inhabitant on the map to study and befriend. I don't think the crystals are too keen
  mining."* It walks its rounds near the Lantern. A crew member can spend real time studying it, once a day at
  most; after a completed visit it knows the crew, and on the next descent it comes over, stops, faces them and
  gives a blue pulse of greeting, then keeps near them for a while by its own choice. (His answer of 2026-11-10:
  *"Peacefulness indicated through a greeting and harmless presence and curiosity."*) A stop of a week or two holds
  enough descents for the greeting to be earned and seen.
- **The sun under the mountain.** Some Deeps hold one **galuush**: *"a sun hung under the mountain"*, a roof-pinned
  bladder four cells across that lights its whole chamber blue-gold, with every light-loving animal in the cave
  gathered under it. Killed cold, with blades, it is *"a fortune in fuel — the single richest harvest in the
  biome."* Touched by anything hot while it dies, it goes off.
- **The floating herd.** Drifters graze the voids, harmless to a blade, and each one bursts into flame if it is
  killed by fire or spark. A crew that hunts by lamp and blaster is hunting with explosives.
- **It is the same cave every time.** The Deep is a saved place. The excavated face, the shell the crew shot, the
  stores left at the shaft bottom and the suit that knows them are all there on the next descent, and on the next
  landing.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The suit turns its head.** *On screen:* a hooded figure with a lamp walks past a dead exo-suit slumped at a
   rock face; the suit stands and turns to follow the light. *Why it lands:* the crew were about to strip it.
2. **The lamp gets an answer.** *On screen:* a work party under a bright lamp; the inspect line climbs from quiet to
   drawn; a pale moth comes down the one open gallery straight at the brightest Jawa. *Why it is funny:* the one
   holding the lamp was holding it for everyone else.
3. **The shot at the balloon.** *On screen:* a drifter floats into the lamplight, somebody fires, and the drifter
   is a fireball. *Why it lands:* it would have died quietly to a knife.
4. **The sun goes out.** *On screen:* the lit chamber, the crowd of animals under the galuush, the crew cutting it
   down cold; the light dies and the chamber is dark with everything that came to feed still in it. Or one spark,
   and there is no chamber.
5. **The gallery says no.** *On screen:* a miner takes the first block of marked lanternstone; three dead shells
   along the wall straighten, slowly, and start walking. The miner runs. They stop at the gallery's edge.
6. **The greeting.** *On screen:* the party climbs down on day six braced for trouble and a huge mining suit with a
   skeleton in it walks up, stops, and pulses blue at them. Then it follows the one who studied it around
   like a very large dog that owns the house.
7. **Selling the lamp.** *On screen:* a crew member harvests the standing Lantern for its price; the safe pool of
   light becomes a crate; the inspect line starts to climb.
8. **The squirming bowl.** *On screen:* dinner aboard, a bowl of cut tendrils still twitching.
9. **The cable.** *On screen:* the Empire's letter arrives; the hold is half loaded; the console reads *"Reel in
   the keel hoist first"*; and two of the crew are still at the bottom.
10. **The milk run.** *On screen:* a Jawa milking a blind loaf-shaped animal for fuel in a glowing fungus meadow,
    and the wax going straight into the coldest corner of the ship because a warm store of it *"is a fire waiting
    for a reason."*

*0.2.0 adds:* the droid that carried the tools down stops at the gallery mouth and will not go in; lamps dimming
under a crust of sippers; the hunter nobody could see on the unlit floor; a drinker that bites a crew member and
dies of the wrong blood; a blind grazer drumming the wall seconds before the roof goes.

## When the Empire arrives

**The fight is at the ship, on the host's surface, and the Deep takes no part in it.** Incidents are suppressed
inside a Deep (built), and nothing in any source sends the Empire down a mouth. What the Deep does to the fight is
divide the crew:

- **Whoever is below is out of it.** They cannot be seen, struck or bombarded. They also cannot hold the ramp.
- **The cable is a decision.** Hoist down, the ship cannot launch. A crew that wants the last crate has to weigh it
  against the cordon, and reeling in takes time it will be counted in.
- **The dark is on the crew's side up top.** The probe and the spotter each have to see the ship or a crew member,
  and on unlit nightside ground they have to come close to do it. A crew with its surface lamps out is hard to
  find. A crew working the shaft head under floodlights is not.
- **Leaving people behind is possible, and readable.** The Deep is persistent. A party still below when the ship
  must fly is not deleted; they are in a warm cave with food, and the tile remembers. Coming back for them is a
  landing on a tile the Empire has already searched.

`NEEDS HIM` (below): whether the Empire ever comes down the shaft.

## Who else attacks; who hates the Empire

- **Down here, the cave itself:** the drinker drawn by light, ordinary cave hunters, and the crystals' shells if
  their gallery is robbed. None of it is a raid and none of it leaves the Deep.
- **Nobody trades here and nobody visits.** Living droids *"avoid the Deeps at all costs."* The only other people
  who ever come are the dead ones.
- **The crystals are not on anyone's side.** They are not the Empire's friends: in the campaign's deeper story they
  are the mechanoids' *"wild cousins"*, afraid of the Rust Cathedral, and selling the kyber that lies among them is
  *"extremely illegal to the Empire"*. None of that is in these versions (see Scope: later). In 0.1.0 they want
  their gallery left alone and they like the one who sat with the suit.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The surface: the ship is parked at forty below, and whatever the host does to a hull and a crew is happening the
  whole time the party is underground (the host's design states it).
- A robbed gallery with its defenders up, between the party and the rest of the cave.
- A galuush chamber or a drifter herd met with fire.
- A route closed by a roof nobody propped.
- A full hold. This is the one stop where the crew may leave because it cannot carry any more.

**Stay, longer than the Empire would like:**
- A whole warm cave with food, cloth, fuel and no sky, under a surface nobody can live on.
- The crew invisible below; the ship in the dark above.
- A standing Lantern, kept instead of sold.
- A suit that knows them.

## What the crew takes away

- **The dead's gear:** the best salvage on the planet. *"Excellent loot, sometimes still moving."*
- **Lanternstone:** *"light, volatile blasting material, the trade crystal."* The protected gallery's is the prize
  worth the trip; ordinary lanternstone is everywhere else.
- **Fuel:** cold wax by the crate, and the galuush's harvest if the crew dared.
- **Prenna lace** (the Deep's one cloth), **thrakk wood**, **puffer tendrils** and the other three table fungi.
- **A tame candler,** for a crew with a cold hold: fuel on the hoof.
- **A place that remembers them.** The acquaintance with Orun-Ghal belongs to the crew, not to the one who studied,
  and survives the stop.

## Fuel, and what this place does to the ship

**Fuel: a richer source, named.** (Owner's ruling of 2026-11-18: most biomes only render biomass, *"a few biomes
have richer sources."*) The Deeps are one of the few, on their own sources: the candler's cold wax *"burns like
chemfuel and needs no refinery"*; the drifter is the *"best fuel-per-kill"*; the galuush is the richest single
harvest. It is not replete: the wax comes at a milking pace and the big harvests are each a risk. Nobody sells fuel
here, because nobody is here. Two honest gaps: the wax item is referenced by the animals' definitions and its own
definition was not found in source by the cleanse (`UNMEASURED`); and whether cold wax goes into the ship's tanks
directly or through an ordinary recipe is `UNSETTLED`. The trade the old proposal wrote is the Jawa part: this fuel
*"must be stored cold"*, it softens and spoils above freezing, and a warm store near fire ignites. The crew that
strikes fuel has to keep it colder than they keep themselves.

**What wears on the ship.** (Owner's ruling of 2026-11-18: in 0.1.0, from what the sources already say.) The Deep
never touches the hull: the review's own scorecard reads *"Gravship touch: MISS... a ship cannot go down; nothing
down here reaches up to it."* This design does not invent one. The wear at a Deeps stop is the **host's cold on a
landed ship**, stated in the host's design (the Sleeping Ice, the Blue Desert, the Propane Lakes' margins), and the
answer is whatever that host names. The Deep adds two things of its own to the ship, both from sources: the
**tether** (cable down, no launch), and a **cargo that must stay cold** in a hold the crew would like to heat.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A mouth on a cold nightside map leads down to a cave that is the same saved place on every descent. | Go down, dig a face, kill one animal, leave stores; go up; save, reload; go down. | A second mouth on the same map leads to its own cave. A host warmer than the rule gets no mouth. |
| Sustained ordinary light on a crew member draws a native hunter along a real route; dim work does not. | A bright party and a dim party in the same gallery, with a hunter alive somewhere reachable. | A sealed room draws nothing through its walls. With no hunter left alive the cave stays quiet and says so. No new animal is created to do the hunting. |
| Light from a standing Lantern alone draws nothing, and harvesting the Lantern ends that. | Work lit only by a Lantern; then add a lamp; then harvest the Lantern and keep working by its stone. | A lamp behind rock from the worker counts for nothing; a Lantern near a lamp-lit worker does not excuse the lamp. |
| Well-equipped dead lie along the galleries and at the shaft bottom. | Walk a fresh Deep from each kind of mouth. | A corpse with poor gear, or none placed at all. |
| Near an aware crystal a dead chassis stands and turns to a light it can see, and each names the other on inspect. | Carry a lamp past a chassis with a mind in reach, and past one without. | Light blocked by rock does not turn it. It does not mine the rock out. |
| Taking the marked gallery's lanternstone, or hurting a mind or its body, brings finite dead shells against the one who did it, after a warning; they stay with their gallery and leave the way out open. | Designate (nothing happens but the mark); extract; retreat to the mouth. | Mining ordinary rock, harvesting fungus or a wild animal's damage provokes nothing. No new bodies appear. A friend of the suit is warned the same as a stranger. |
| Orun-Ghal is harmless company: it can be studied by real visits, it remembers the crew, and on a later descent it comes to greet them and keeps near them. | Study to completion; leave; save, reload; return with a different crew member. | An interrupted visit earns nothing. It never mines, fights, or is recruited. A destroyed suit stays destroyed. |
| An unsupported roof warns where it will fall, in time to leave or prop it. | Remove a support under a span with a miner beneath; once leave, once prop. | A propped span does not fall; the warning does not hold a roof up for ever. |
| A drifter or a galuush killed by fire or spark detonates; killed cold it does not. | One of each, each way. | The inspect text says so before the first shot. |
| Candlers can be milked for a fuel that works as fuel. | Tame, milk, burn. | A candler butchered for meat gives none: these animals are fuel, not food. |
| The cave feeds and clothes a visiting party from its own fungus, and what is eaten grows back. | A week of foraging on one pasture. | |
| With a keel hoist, cargo and a downed animal ride the cable between the ship and the Deep, and the ship will not launch with the cable down. | The walk already written in `design/validation_walks/RimMandrake/KeelHoist.md`, step 3 and 4. | Reeled in, the launch is allowed. |

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary lit cave with its
plants and plain animals (standing rule, every mod). Existing Deeps and their mouths survive any switch.

## Shared machinery

**Featured here** (the Deeps are where each is vital and should be proven):
- **Light as exposure** (`MapComponent_LanternDeepDarkness`, with the shared light ledger): carried light is counted
  and answered. The Abyss features darkness; the Deeps feature what light costs inside it.
- **A second, persistent map under a landed ship** (vanilla pocket maps and portals; the two mouths). The seas go
  down by ship; this is the one place the crew goes down without it.
- **The keel hoist** (`src/RimMandrake/KeelHoist/`): active wherever there is a portal or a pit, and first pictured
  here. The tether lock is the Deep's whole relationship with the ship.
- **Dead bodies moved by something else** (`RM_WorkingDead`, `RM_ShardMind`): the remote-body pattern, which the
  Rust Cathedral's design may want for its own machines.
- **Roofs that warn** (`RM_DeepCollapseKernel`): any mined or roofed map could use it; here it is the only weather.

**Merely active here:** wreck and salvage placement (`Wreckage`); bones from the dead (`Bones`); creature
behaviours (fluid feeding, real flight for the drinker); fast-growth rosters (`ExplosiveGrowth`, with the sowable
stone deliberately left out); the acoustic scanner's readings; the Empire's search and the visibility dial, which
act on the surface map only; the one sun from geometry, which an intact roof shuts out entirely (the cave's warmth
is ordinary air temperature, not a heat of its own).

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**0.1.0, the stop**
- Two kinds of mouth on cold nightside hosts; the persistent Deep; its still air, hum, lanternstone rock and
  glowing formations; sealing a mouth as the player's own destructive choice, with a warning. (built)
- Light draws the drinker; the standing Lantern's safe light and its sale; a Lantern placed naturally where a first
  party can find it. (built, except natural placement of the Lantern)
- The well-provisioned dead; the Working Dead that stand and turn to light; the aware crystals that move them.
  (built; the only chains proven inside a placed Deep, 2026-10-05)
- The protected gallery and its defence by remote shells; the route out left open. (unbuilt: the present shells
  cannot fight)
- Orun-Ghal's rounds, real study and the remembered greeting. (rounds and study built; the greeting is not)
- Roof warnings. (built, unproven)
- The fungus pasture, food, cloth and timber, and its regrowth. (built)
- The plain hydrocarbon animals as bodies with their own light; the candler's fuel; the galuush as a lit chamber
  and a harvest; drifter and galuush ignition when killed hot. (built; ignition moved in, see `rewrite_choices.md`)
- The keel hoist's line down a mouth and its tether lock. (built in its own mod; the live walk is uncovered)
- Nothing disappears without a sign: bodies, falls and sealed mouths leave something to read.

**0.2.0, the stop with company**
- Crew droids stop and listen at a mindstone gallery. (built, switched off)
- The hush, unseen on unlit floor; the sipper, shrinking lamps; the tapper, draining batteries; the pooler,
  smothering fires and heaters; the slick's fuse trail. (built, unproven; hush and slick failed their last live
  check)
- The drinker's wrong-blood death; the soulchime's stun and soothe. (built)
- The knocker's drumming before a roof fails, and the tame one's longer warning. (built)
- The Creep, growing over sleepers; the Cleavers splitting when struck. (built, unproven)
- The galuush's blast bringing its roof down; formations that explode when damaged. (built)
- The aurora overhead waking the cave: brighter stone, louder Chorus, faster Cleavers. (built, failed its last live
  check; needs the host's storm)
- The shoal's shared wounds. (built)
- The scanner's echoes of hidden voids. (built)
- Bonus rewards and lore steps from studying the suit. (built)

**Later (a crew that stays, a colony, or the campaign)**
- The mindstone gallery, the Kindled, droids that leave wiped and rogue, the cousins who talk, the facility's
  trickle, the testimony about the Cathedral. Campaign layer; canon is ruled, nothing here builds it.
- Kyber as a find and the illegal kyber trade (it raises the Empire's attention with every sale: a campaign device
  this design would want the day it is built).
- The Answering rite (the owner tabled rites on 2026-10-03 until the biome mod is complete).
- A deeper giant that forces a longer or more dangerous route (his answer of 2026-11-10; no candidate chosen).
- The Chorus as a psychological effect; formations that mature and cleave offspring; sowing lanternstone.
- The warm-wax reaction as its own behaviour; the cantina's Deep lane of dishes; Pyrinth and other added minerals;
  the imported orange crystal.
- Living in the Deep; a home of forty.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- The Lantern Deeps as a world-map biome (*"that was a mistake"*).
- Crystal-studded animals (*"a bit hokey... I'd rather have crystals AS creatures"*) and the rat.
- The blinker's flash (removed 2026-10-23); the earlier local glowbulb, grabber, shatterjaw and chiller.
- Dulcis here (*"It makes no sense that the rot has something growing in the lantern deeps as well"*).
- Any Force route through kyber or mindstone; any Deep under a host warmer than the rule; regenerating Deeps.
- A ship that goes underground.
- **Recommended for dropping, not yet his:** the old donor renaming and eviction compatibility patches.

## NEEDS HIM

1. **Does the Empire ever come down the shaft?** Nothing in any source sends them, and incidents are suppressed
   below. *No* (default, as built): the Deep is a bolt-hole for people and the fight is always at the ship.
   *Yes, at the strike step and after:* troopers with bright lamps in a cave that answers light would be the
   funniest fight on the planet, and it needs a new arrival route and a rule for what the crystals do about them.
   *Only a probe:* one droid drifting down the mouth with its searchlight on, which the cave deals with unaided.
2. **Is the host's dark enough to pause the search here, as built?** His rulings say full dark pauses it; the
   pursuit mod slows only the Abyss. This is the hosts' question more than the Deep's, and it decides whether a
   Deeps stop is a month or a long winter. *Add the cold nightside hosts to the slowed list* (what the rulings
   read as). *Leave them out:* the Deeps become a smash-and-grab like anywhere else.
3. **Do the crew's own droids stop at the gallery in 0.1.0?** It is built, it is what a Jawa crew would see first
   (their stock in trade refusing to walk), and the cleanse switched it off because it also interrupts a player's
   Biotech mechanoids and a fresh review refused it as a default. *0.2.0* (default here). *0.1.0, droids only,
   mechanoids exempt:* a small change and a strong first-descent moment.
