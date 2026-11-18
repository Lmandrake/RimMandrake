# The Leaning Scrub: the design, seen from the ship

**Status:** the one design document for the Leaning Scrub biome (`RM_LeaningScrub`, source
`src/RimMandrake/LeaningScrub/`; the campaign world's "arid shrubland"), rewritten 2026-11-18 on the owner's
instruction to see every biome "through the lens of Utinni". It replaces the older definition sheet, cast bible,
reviews and pitches as the place to read; what happened to every idea in them is in
`design/concepts/LeaningScrub/rewrite_choices.md`. Nothing has been deleted. The Leaning Scrub is one of the biome
mods HELD BY OWNER: this is a design document only and it launches nothing.

**What kind of place this is (checked against the sheet's own header):** a surface biome on the day side, near the
terminator; flat, mild, landable. The ship sets down on it like anywhere else.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/LeaningScrub/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Leaning Scrub is unusual among the biomes: it has a **locked** Designer
sheet, tree and scenes beside this file (locked 2026-11-16, design version 0.1.0), built on a promise the owner
validated two days before he stated the ship lens: *"a dependable wind-powered home in a restless plain"*. Those
files still describe a settled home and would be re-argued from this one when the hold lifts. Almost all of their
content survives here; what changes is whose home it is, and three features that only pay over seasons.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
locked sheet of 2026-11-16 cites it in source; it does not mean it has passed anything live.

---

## What this place is

> *"Endless leaning grass, endless motion, endless venomvine. Power is free here, but footing is not."*
> (owner, picked by card, `biome_experiences_2026-10-20.md`)

> *"Knee-high silver-green fuzz at eerily even spacing, running unbroken to every horizon, all of it leaning the
> same way, all of it moving — because the wind never, ever stops."* (`arid_shrubland.md` §1)

No rain falls. The only water is fog carried on the ground-wind from the stormwall, thinning with every metre
toward the sun. *"It is mild here — the first ground on the dayside that is not trying to kill you — and that is
the trap: the moment the environment stops being the danger, the danger becomes each other, and everything you
cannot see."*

The fuzz is a canopy at the knee, and it splits the place into two floors that cannot see each other. Above it
walk giants that eat it in mouthfuls and have *"not noticed your species"*. Below it, small things live their whole
lives in worn tunnel-runs *"without once standing in open light."* *"The floors never meet — except violently."*

> *"An intelligent biped is precisely the wrong size for this place — too large to hide in it, too small to be safe
> over it."*

**Seen from the ship, this is the one biome whose older pages were already written about Jawa**, and nearly every
line of that survives. The one thing here that stands as tall as a person is **venomvine**: near-black islands of
thorn, *"nearly impossible to cut down"*, where *"a scratch carries venom with serious results."* The sheet:
*"Small creatures pass through easily; larger ones simply cannot"*; *"sparser stands let a Jawa slowly thread them
— no larger race can"*; a hedge-fort's wall is something *"a Jawa can sometimes walk through"*; and inside the
thickets the birds line their nests *"with glittering scrap — wire, lens-glass, chips of hull — beautiful creations,
and a treasure worth seeking for a Jawa."* The crew are the right size for the wrong place: small enough for the
vine, too tall for the fuzz, and they have just parked the tallest object for a horizon in every direction.

His own direction for the vine, 2026-10-16: *"Venomvine was supposed to be integral to the Leaning Scrub... the one
plant that grows abundantly tall and dangerous."* And for its look: *"especially rich, varied, interesting... its
the strange showpiece here."*

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew halves every wait and a hidden one doubles it.

**How long a stop here can last (the outer edge of a stay, not the usual one; owner's ruling of 2026-11-18).**
About as short as the ladder allows: a first week nearly free of the Empire, a first fight in the second or third
week, nothing past about a month, and less for a crew that is seen early. This is the most exposed landing on the
planet. A ship on a flat plain of knee-high fuzz can be seen from the map's edge the moment anything arrives to
look. The sheet's own word for a person here is the word for the ship: *"People stand out."*

**What cover this place gives, and which kind (same card: canopy, steam and fog slow the search by one step).**
- **From orbit: fog, and only while it is in.** The Scrub has no canopy and no steam. Its water is ground fog on
  the wind, and fog is the commonest weather in the biome's built list. This design gives the Scrub the one-step
  slowing on fog days and nothing on clear ones, which makes it the weakest cover of any covered biome. (This is
  my reading of the card, flagged in `rewrite_choices.md`; the plain alternative is no cover at all.)
- **On the ground: none for the ship, real cover for the crew.** A crew member inside venomvine is behind the only
  sight-blocking thing on the map. A probe or a spotter that has to *see* the crew cannot see into it, and anything
  bigger than the crew cannot follow them in.
- **In a Gale, nobody can read anything.** In the Stall, everything that moves is seen.

---

## The first minutes

The ship comes in low over a plain that ripples from horizon to horizon like water, every plant bowed toward the
low sun. The wind that bows them is the same wind the ship lands in. On an ordinary day that is nothing. In a
**Gale** it is the roughest approach on the day side, and it is the first thing the biome does to the hull (see
"Fuel, and what this place does to the ship").

The ramp comes down into moving fuzz to the crew's knees, a steady hiss, and no other sound at all. *"The wild has
no voice, only posture."* The air is cool and damp, the light is *"the last ten minutes of a sunset that never
ends."* Nothing attacks. Nothing even looks.

Before the first hour is out the player should have seen three things without hunting for them: the lean, shared
by every plant on the map and pointing the way the wind blows; a black island of venomvine taller than the crew,
somewhere between the ship and anything worth walking to; and a shimmer running through the fuzz where something
small is moving that cannot be selected, shot or seen.

## The first day

- **Power is free.** The wind never stops, so wind gear never stops. The ship's batteries fill on the first day
  and stay full. This is the reason anyone lands here.
- **Footing is not.** Venomvine stands in islands across the map and leaves the ship a usable patch to start on.
  Small animals walk through it. A person forces a slow way in and is scratched for it, and the venom builds with
  every scratch. Big things cannot enter at all. Ordinary errands go around it or visibly wait; nobody walks into
  poison because the shorter path lay through it. Going in is an order the player gives on purpose.
  (`UNMEASURED`: which side of the built size gate a Jawa falls. The gate passes the small freely, lets a
  person-sized body thread slowly and stops the big; the sheet says a Jawa threads sparser stands where *"no
  larger race can"*. Either way the crew gets through where a trooper struggles, or better.)
- **Which way the wind blows is a fact about the map.** Stand upwind of an animal and it smells the crew and
  moves off. Fire runs downwind and creeps upwind. Anything built casts a calm lee, and in that lee the fuzz stops
  shivering, so whatever moves there under the canopy shows.
- **The runs are busy.** Walking across the fuzz sets off whatever lives under it: a flush of small bodies
  scattering, some of them straight up into the air.
- **The vine has kinds, and the kinds do things.** One beads venom that can be harvested and beads again. One
  lashes once at whatever comes next to it and then droops, spent. One is dead and hollow, a street for small
  animals that *"a Jawa-sized pawn can crawl through."* One stands up, pale side out, when something pushes into
  it. One keeps what is dropped in it.
- **The giants graze past.** Thundersteps walk their line. They do not care about the crew. Their young walk
  behind them, and the sheet's rule for the young has no exceptions: *"approach is attack: the parent enrages if
  you even get near the young. No warning is given."*
- **A tree with a name.** A map may hold one or two sweetline trees: huge, ancient, each with a name the
  road-folk gave it, the only other tall thing on the plain. Animals with coats walk to it and rub them off
  against the bark, because it heals them: *"they receive a health/healing bonus (Hediff) when they scratch their
  hide against it. Removes parasites and disease over time."* (owner, 2026-11-16). The wool lies at the trunk for
  whoever dares the traffic.

## The first week

- **The Gale.** The canopy is whipped to white noise. Dust and torn fuzz drive across the map. Wind gear surges
  and can break; anyone organic caught in the open is battered and deafened; the small floor erupts into
  everything it was too dangerous to do on a quiet day. *"Raids ride the gales."*
- **The Stall.** Rarely the wind dies. The hiss stops. Every small animal freezes where it is, because *"every
  step under the fuzz is a signal flare"*, and the hunters that read the canopy choose from what they can now see.
  *"Hours of held breath."* The wind gear stops with it.
- **The vine moves.** Stands send runners downwind on their own slow clock. One kind walks: in each Gale it lays
  new growth ahead of itself and dies back behind. Ground the crew has built on and the routes it keeps clear stay
  dependable; everything else is negotiable.
- **The vine takes hold of things.** A strangler stand wraps what is built near it and damages it until someone
  trims it. A shedding stand throws its thorns downwind in a Gale, and the litter scratches whoever walks it until
  it is swept. A weeping stand pools something foul at its foot. A sleeping stand looks dead until a foot lands on
  it, once.
- **Fire means someone.** *"There is hardly ever lightning... a fire almost always means someone lit it."* The
  giants despise it: *"They charge it and stamp it dead at all costs — and then stamp out its source."* A big open
  blaze brings the herd, and the herd works out who made it by having watched, or by a fresh trail.
- **The scrap in the thorns.** A hoard stand grows in whatever is left in it: dropped gear, the gear of things
  that died there, the scrap the nest-birds carried home. Cut it open and it gives back the actual objects. The
  sheet's promise to a Jawa, *"salvage, eggs and venom-thorns behind a wall only a Jawa can thread"*, is this.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The shortcut.** *On screen:* a crew member ordered through a black thicket, moving at a crawl, a venom bar
   climbing with each scratch; then, beside them, a rat-sized thing trotting through the same thorns untouched.
2. **The lash.** *On screen:* a Jawa walks past a stand a pace too close; one cane whips out, hits, and hangs
   limp. The next Jawa walks past the limp one safely, and says so by doing it.
3. **The ground takes off.** *On screen:* a hauling party crosses open fuzz and the fuzz in front of them bursts
   into running, leaping, flying small things in every direction.
4. **The hedge moved.** *On screen:* after a Gale, the black wedge that was well clear of the apron has a soft
   rust-coloured edge laid toward the ramp.
5. **The walking hill does not stop.** *On screen:* a thunderstep on its grazing line, the crew's stacked salvage
   on that line, and the thunderstep still on its line afterwards. *Why it lands:* it never looked down.
6. **Too close to the calf.** *On screen:* a curious Jawa, a young thunderstep, and with no warning at all the
   largest animal on the plain coming at a run.
7. **The cooking fire.** *On screen:* somebody lights a big open fire to render scrap. The grazing heads come up,
   all of them, and the herd walks over and stamps the fire flat, and then looks for who lit it.
8. **Everything stops.** *On screen:* the hiss cuts out mid-errand. The fuzz stands still for the first time.
   The shimmer in the runs freezes. Something lifts off a venomvine crown. A hauler takes one more step.
9. **The nest.** *On screen:* a Jawa crawls out of a hollow stand with an armful of wire and lens-glass, scratched,
   delighted, and the stand they robbed has stood up behind them, pale side out, where anything can see it.
10. **The scratching post.** *On screen:* a line of shaggy animals queuing at an enormous leaning tree to rub
    themselves bald, and a hooded figure darting in between two of them for the wool.
11. **Charged in a day.** *On screen:* the ship's power full before the first sleep, and in the first Gale a
    wind turbine spinning itself to pieces.

## When the Empire arrives

- **They see the ship at once.** Nothing on this plain hides a hull. The probe and the spotter will complete
  their sightings on the ship unless they are stopped; hiding the crew does not hide the stop.
- **They arrive in the weather.** A Gale changes which raids come, and when: this is the biome where the strike is
  most likely to land in the storm, with the crew deaf and the wind gear failing. (Built as a weighting; the sheet's
  *"raids ride the gales."*)
- **Their fires have an owner.** Whatever of theirs starts an open blaze (a crashed pod, an incendiary, a camp
  fire) is theirs in the giants' eyes. The giants stamp open blazes and then go for whoever they saw or tracked
  making them. A firefight on this plain can end
  with a herd in the middle of whichever side lit the most.
- **They cannot follow the crew into the vine.** A trooper is a person: slow in the thicket, scratched, poisoned
  by degrees. A crew that knows its hollow stands has streets the Empire has to cut.
- **A reared stand tells on both sides.** Anything that pushes into rearing venomvine flags itself, troopers
  flanking through a hedge as much as a Jawa robbing a nest; in a Gale the flag cannot be read.
- **The lee gives them away, and the crew.** Whatever shelters behind a wall or a hull stops shimmering.
- *0.2.0:* the calling-pyre. Light the plain on purpose and bring the herds down on *"ALL who remain — attacker,
  defender, farm and field"*, *"spoken of the way sailors speak of running aground on purpose."* On a siege camp
  parked beside the ship it is the most Jawa answer in the game: burn the lot and hope to be standing in the right
  place.

## Who else attacks; who hates the Empire

- **Nothing hunts the crew on purpose.** *"Big things ignore the fuzz and ignore you."* The danger is being in
  the way, being near the young, or lighting a fire.
- **The interface killers** hunt each other and will take a crew member who is where the prey was: the shokka at
  the edge where a run surfaces, the fuzzviper holding a run wall, the surrik that swims the crust and comes up to
  strike, the thornhold defending its den against whoever hit it.
- **The Deep Desert Tribes** raid here in the campaign's world with a moving wall of fire, *"and leave with the
  burned."* Here *"pyroculture is pure weapon"*, and it is also *"a beacon"*: the giants come for the arsonist.
  They are placed by the campaign layer, not by this biome.
- **The road-folk** (moisture farmers and hedge-fort households, the comb holds) hold no love for anyone who
  brings fire or the Empire near their vaporators. Whether they fight the Empire is `UNSETTLED`. Their ruins and
  camps are built and wait for 0.2.0 by the owner's ruling of 2026-11-16.
- **The thundersteps hate fire, not the Empire.** That is close enough to be useful.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- Being seen: there is no stop here the Empire does not find on its first look.
- A Gale that breaks more than the crew can mend, or a strangler on something that matters.
- Venom: a crew of five to seven with two of them down from the thorns is not loading cargo.
- An enraged parent, or a herd answering a fire, through the camp.
- The vine closing a route the crew needs.

**Stay, longer than the Empire would like:**
- Free power, every hour of every day but the Stall.
- Mild air, clean fog water, no weather that kills.
- The vine: a wall the crew can cross and a larger enemy cannot, and the only place on the map to be unseen.
- Fog days, which slow the search from orbit by a step.
- The giants, for a crew that has learned never to be the one seen with the match.

## What the crew takes away

- **A full charge,** and whatever the crew builds with a week of power nobody had to pay for.
- **Scrap from the hoard stands and the nests:** wire, lens-glass, hull chips, and whatever gear died in there.
- **Raw venom,** harvested from the dripping stands.
- **Sweetline wool and felt,** *"a uniquely comfortable blend"*: bedding and coats for a cold hold.
- **Cane:** dead venomvine, *"the finest fuel in the region — wood that spent its life refusing to burn and, dry
  at last, burns long and hot."* A visiting crew gets it only where a stand has already died (see below).
- **Pelts and meat** from the interface, *"reliable protein... for those who learn the crossings."*
- *0.2.0:* plans recovered from a dead farmstead, and a vaporator the crew can build elsewhere.

## Fuel, and what this place does to the ship

**Fuel: the emergency-slow kind, with one premium exception a visitor can only find or buy.** (Owner's ruling of
2026-11-18: most biomes only render biomass, *"uselessly slow, only for emergencies"*; *"you can also buy it."*)
The Scrub is worse than most at biomass: its living plants *"resist fire greatly and burn only grudgingly."* Its
one real fuel is cane, and making cane is the local industry of years: throw a blanket over a thicket, starve it
of light, come back when a grandchild is grown. *"My grandmother darkened this stand."* No stop is that long. A
visiting crew gets cane three ways: from the tail of a walking stand that has died back behind itself (built);
from the road-folk, who are the people to **buy** it from when their camps arrive in 0.2.0; and, also 0.2.0, from
a blanketed claim somebody else banked and is not there to defend. The last is the very Jawa one. The Scrub is
**not** a fuel stop; it is the power stop.

**What wears on the ship (owner's ruling of 2026-11-18: in 0.1.0, from what the sources already say; his list
included "rough weather turbulence in the approach").** Three things, all already in the sources:
- **The Gale.** Rough air on any approach or launch made during one, and on the ground the same wear the built
  Gale already puts on wind gear: surges, breakage, repairs. *Answer:* land and leave outside a Gale (the wind
  state is readable); stow or brace exposed gear; mend after. A hull part that shrugs off wind is the armour
  answer and is `UNSETTLED` (no source names one).
- **The vine.** A strangler stand wraps what is built beside it and damages it (built, for walls); a shedding
  stand litters the apron with thorns each Gale. *Answer:* hands-on work, exactly as the code already calls it:
  trimming and sweeping. Do not park against a black island.
- **The giants.** A thunderstep *"will walk through your wall on its grazing line, ignore your rage, and not know
  what it did."* *Answer:* do not land on a grazing line, and never give them a fire to stamp beside the hull.
  (`UNMEASURED`: whether wall-indifference is built; the stamping is.)

An older idea goes further and is `NEEDS HIM` below: that the engine's burn at launch reads as fire to the plain,
and the herds converge on a ship trying to leave.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Every plant leans one way, the wind always blows that way, and the Stall and the Gale are each unmistakable at normal zoom and sound. | A landed ship on a generated map through an ordinary day, a Gale and a Stall. | A motionless fog sheet in a Gale; ambience that is stuck on or silent in both. |
| Wind gives the ship real, usable power, and a Gale puts that gear at risk. | Wind gear wired to the ship's own consumers across the same three states. | A number on an inspect pane with nothing powered by it. |
| Ordinary work keeps to ground and routes the crew maintains, or visibly waits; only an ordered trip enters the vine, and it comes back. | A needed item beyond a thicket with a long safe way round and no safe way; then an ordered expedition. | One detour that passes while a later errand quietly walks through poison. |
| Venomvine passes the small, slows and scratches people, and stops the big; the venom builds by scratches and fades. | A small animal, a crew member, a trooper-sized stranger and a large animal at the same stand. | Any health loss called venom; a boundary size that passes or fails depending on the day. |
| The vine islands are tall, many and varied on a generated map and still leave the ship a usable start; they creep on a capped clock and never take ground the crew has built on or keeps clear. | A generated landing; the days run with an apron and two kept routes. | A hand-planted line of vines; a walking stand that crosses the apron. |
| Each kind of vine does its one thing, readably, and shows whether it is ready or spent: beads venom and regrows, lashes and droops, lets small things through, gathers a cloud in the Stall, rears when entered, walks in a Gale, keeps and returns what was left in it, quenches fire once, sheds thorns downwind, wraps and damages what is built, weeps a bounded pool, wakes once under a foot, bears fruit that draws the hungry. | One of each, met in play on the same map. | Art that changes at random; a hoard stand that returns new steel for lost gear; litter placed by hand. |
| Small animals under the fuzz cannot be seen or targeted but shimmer; in a built lee they show; in the Stall the ones that hold still are safe and a hunter picks from the ones it can see and reach. | Watch the runs on an ordinary day, behind the hull, and in a Stall with a hunter present. | A hidden marker on an animal that can still be shot; a hunt assigned by hand. |
| Walking the fuzz sets off the runs, and what flies really flies. | A hauling party across untouched fuzz. | (Flight in the air is looked at only with the owner present; unattended it is a state read.) |
| A rare named sweetline tree stands on some maps; coated animals choose to rub on it and are healed of parasites and disease over time; the wool at its trunk can be gathered and the felted mass harvested once; felt is worth having. | A map with a tree, wild coated animals carrying a parasite, a week. | A sheep led to the trunk by hand; a healing label with the parasite still there. |
| The native animals appear on their own and do what they are for: the den-defender, the crust-swimmer, the edge-ambusher, the run-wall ambusher, the canopy-top thread, the glider that returns home, the carrion-roller, the star-armed thing that sheds an arm and regrows it. | A generated map left to run, then walked. | An animal spawned beside a decorative bush and called an ecology. |
| A big open blaze brings thundersteps to stamp it out, and they go for the maker only if they watched it lit or can follow a fresh trail. | A fire lit in view; a fire lit unseen with the maker gone and the trail cold. | A herd teleported in; the nearest person blamed. |
| Getting near a thunderstep's young enrages the parent, with no warning. | Walk a crew member toward a calf. | |
| A Gale changes which raids come and when. | A long run of raid picks under Gale and under ordinary wind. | One forced raid. |
| The place wears on the ship in the three ways stated above, and each has the stated answer. | A ship landed in a Gale, parked by a strangler, with gear exposed; then the same with the answers applied. | Wear with no visible cause; an answer that changes nothing. |

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary windy scrubland
(standing rule, every mod).

## Shared machinery

**Featured here** (the Leaning Scrub is where each is vital and should be proven):
- **Wind as a map fact** (`RM_TheLean`, `RM_WindCalendar`): one heading per map; scent, fire spread and plant lean
  all read it; the Stall and the Gale are its two events. The owner's own example of shared machinery was *"wind
  effect on fire"*; this is where that is built and where it should be proven. The Pyrelands feature fire; the
  Scrub features the wind that steers it.
- **Passage by body size, and venom by contact** (`RM_MapComponent_BodySizeBarrier`, `CompProperties_ContactVenom`,
  both in `EnvironmentalHazards`): any biome's hedge can use them; here they are the footing.
- **Concealment as a field** (`RM_Ripple`): cover that depends on weather and on what is built upwind.
- **Giants that answer fire and know who lit it** (`RM_FireStamp` and the witness-and-trail tracking). The owner
  wants the tracking kept robust because *"we will need this later for the ownership mod anyway."*
- **A tree that animals use** (`RM_SweetlineScratching`): an auto-shearing, healing station.

**Merely active here:** parental enrage (`CreatureBehaviors`, on the thunderstep); real flight; fast-growth
rosters; the acoustic scanner's readings; eggs that hatch near people; the one sun from geometry (low sun, long
shade, nothing tall enough to cast it but the vine, the trees and the hull); the Empire's search and the
visibility dial; wreck salvage.

## Scope

Every feature is in one bucket. "Built" is what the locked sheet of 2026-11-16 cites in source, not a pass.

**0.1.0, the stop**
- The wind: the lean, ordinary windy days, the Stall, the Gale and what each does to sound, power, exposed people,
  small animals and raid timing; scent and fire following the wind. (built)
- Concealment under the fuzz, the lee that reveals, hunting in the Stall, the runs that flush under traffic.
  (built)
- Venomvine as land: islands on generation, the size gate and contact venom, creep on its own capped clock,
  dependable built ground and kept routes, ordered expeditions only. (built)
- The thirteen kinds: dripping, twitcher, hollow, crown, rearing, walking, hoard, quench, shedding, strangler,
  weeper, sleeper, lure. (built; four of them have passed a first live check)
- Cane as a fuel worth having, taken from stands that have died back. (the item is built; a visitor's route to it
  is this design's)
- The sweetline tree: named landmark, coats rubbed off, the healing his words added, wool on the ground, the one
  harvest of felt, felt's comfort. (built, except the healing)
- The native cast and what each does; pillowmoss wetting ground from fog; tanglefuzz anchoring dens; crustweevils
  grazing cruststar. (some built, several marked by the sheet as owed)
- Thundersteps stamping open blazes and finding the maker by witness or trail; parental enrage. (built)
- What the place does to the landed ship: Gale wear, strangler and thorn litter, a giant on its line. (the Gale's
  wear on the ship itself is new work; the rest is built for ordinary structures)
- Fog as one step of cover from orbit on fog days. (new, small, by his card)
- The scanner's readings here; the eggs that hatch near people. (built)

**0.2.0, the stop with company** (the owner's own "next Design Version" of 2026-11-16, plus two lens additions)
- The dead farmstead, recovered plans, the wind vaporator and its dried wake, the road-folk's camps and their
  peace and war. (built, unproven; his ruling)
- The calling-pyre: its three beliefs, the rite, the field fire and the herds. (built, unproven; his ruling)
- Blanketed claims found on the map, banked by somebody else and ripe; cane bought from the camps. (the injection
  step that places smother-claimed fields is built; buying is ordinary trade once the camps exist)
- The ship as the tallest thing on the plain: its wind-shadow greening a wake behind the hull, and the herds
  answering the launch burn. (unbuilt; `NEEDS HIM`)

**Later (a crew that stays, or a colony)**
- Laying a smother blanket and waiting years for the cane. Built and locked into the current tree; no stop sees
  it pay.
- Sworn venomvine: the one strain a player can sow, and the sap-mark that lets its own walk through. A hedge-fort
  is a home's wall.
- Transplanted venomvine as fortification; farming under cover and growlight; the moisture farmer's whole trade.
- The sweetline tree-roads, the name register's deeper layers, pilgrims and traveller camps at the trees.
- The Stall-Hold rite. The Blurrg as a tamed-only mount (campaign).
- The fuzz changing colour along the gradient from the stormwall; the sweetline as a contour on the map.
- A crust terrain of our own to replace open sand.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- The bark-wardens, the trees' guardians (cut 2026-10-23); farmer camps; the drying scar; any work to preserve old
  saves (his answer of 2026-11-16: *"the savegame stuff is simply gone"*).
- Creatures built or described as warning instruments (*"Too much focus on constant advanced warning... Players
  arent that into it."*).
- A resident animal of the large size band; rain; lightning or any fire nobody lit; dense flora other than the
  vine; a still ordinary day.
- "Cover everywhere" for people (*"interpreted only for smaller things than you. People stand out."*).
- The vissler arm's own code (the behaviour is vanilla; the animal and its arm stay).
- No worldgen and no guaranteed tiles; the planet is painted once, at the end.

## NEEDS HIM

1. **Do the herds come for the launch burn?** A 2026-09-29 design idea, never ruled that I could find: *"at
   spool-up the engine reads as FIRE to the plain — thunderstep herds converge on a launching ship to stamp the
   burn, so leaving is an event you schedule around the herds, or a Gale you gamble on."* Its own caution:
   *"herds delay/damage, never forbid."* *0.2.0* (default here: unbuilt, and it needs a rule that it can never trap
   the ship). *0.1.0:* the biome's strongest ship moment, and the natural fourth line under hull wear. *Never:*
   fire-stamping stays about fires the crew lights.
2. **The years-long smother claim.** His validated bar of 2026-11-16 names *"banked years-long smothering and
   premium useful cane fuel"* as something that must show. Under the lens stated two days later nothing a crew
   lays can pay within a stop. *Later* (default here; cane stays in 0.1.0 through died-back stands). *Keep it in
   0.1.0 as laying the claim only:* testable, and its payoff is taken on trust. *Keep it whole:* the bar stands as
   validated and the lens bends for this one.
3. **Is fog cover?** This design gives the Scrub one step of cover from orbit on fog days, as the thinnest reading
   of *"canopy, steam and fog"*. *Yes, on fog days* (default). *No:* the Scrub is the planet's open ground, power
   paid for in exposure, and its only cover is the vine at ground level.
