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

**Second reader, 2026-11-18:** a reader who did not write this design read the older sheets, the sitting notes on
the ledger, the venomvine design of 2026-10-16, the cleanse and the ship-shield rulings to their ends and repaired
this file. What changed and why is at the top of `rewrite_choices.md`. The largest repairs: the ship ideas this
design had revived were both cut by the owner on 2026-09-28 and are now listed as declined; the hull wear cites the
built ship-shield frame; "no sound at all" is replaced by his later ruling for a rich soundscape; the vine is no
longer claimed as cover, because nothing in its definitions blocks sight yet.

**The locked Designer tree is not edited.** `sheet.md`, `tree.json` and `scenes.json` beside this file describe a
colony that stays. They are left exactly as locked, for a later Designer run to reconcile with this design.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means a
source file carries the behaviour; it does not mean it has passed anything live. The pipeline's own journal of
2026-11-16 names what is still a stub or missing, and this design now says so where it matters: the thundersteps'
knowledge of who lit a fire, the sweetline tree's healing, cane burning better than wood, the shokka's and the
fuzzviper's ambushes, the ribbonwhip's canopy routes, pillowmoss wetting ground and crustweevils grazing cruststar.

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
the strange showpiece here."* He ruled how much of it by card on 2026-10-16: *"Heavy: islands at about 15%"* of
open ground, *"Tree-tall, 1.8 to 2.4 cells"*, with *"its own slow creep downwind, capped"*. The venomvine design of
that day calls the result what it is: *"The Scrub becomes a maze"*, and the vine *"the dungeon, the curtain wall,
the treasure vault and the fuel bank of the biome, all in one plant."*

**The plain is not silent.** The September sheet wrote a hush: *"The wild has no voice, only posture."* He reversed
it at the sitting of 2026-09-28: *"A rich soundscape of bugs and birds and stranger animals in the wind."* So the
hiss of the wind carries a dry click-chorus from under the canopy (*"That is the tikkit nation talking to itself.
About what, nobody has ever needed to know."*), wing-bursts and stranger calls, and all of it thins when the wind
does. The Stall is quiet because the wind stopped, and that is why it frightens.

**The crew are not strangers to this kind of ground.** The shared machinery page puts the Scrub among *"the open
crossings... closest to the crew's home desert"*, where *"the joke cannot be that they are out of their depth."*
Here the joke is size: Jawa are built for the one thing on this plain that everything else their height avoids.

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
- **From orbit: fog, and only while it is in.** His card names fog: *"Canopy, steam and fog slow the search by one
  step."* The Scrub has no canopy and no steam. Its water is ground fog on the wind, and wind-fog is the commonest
  weather in the biome's built list (weight 40 of 85, read from the biome definition). This design gives the Scrub
  one visibility band of slowing on fog days and nothing on clear ones, which makes it the weakest cover of any
  covered biome. Whether fog that comes and goes counts is `NEEDS HIM` 3.
- **On the ground: none for the ship, and for the crew only what the vine's size gate gives.** Anything bigger than
  the crew cannot follow them into a thicket; that is built. Being *unseen* in there is not: no venomvine
  definition blocks sight or gives cover today (measured: none sets a cover value or carries the sight-blocker).
  The venomvine design of 2026-10-16 proposed exactly this and nobody built it: half cover inside or behind a
  stand, a pawn deep inside an island hidden from view, and scent masked (*"the cane's own smell covers theirs...
  Hunting from inside the thicket becomes the Jawa ambush"*). It is the crew's only possible cover on this map and
  it is `NEEDS HIM` 4.
- **Fog blunts every gun.** Wind-fog halves ranged accuracy for both sides (built into the weather). A Gale takes a
  fifth off accuracy and a tenth off walking speed, and deafens whoever is outdoors.

---

## The first minutes

The ship comes in low over a plain that ripples from horizon to horizon like water, every plant bowed toward the
low sun. The wind that bows them is the same wind the ship lands in. On an ordinary day that is nothing. In a
**Gale** it is the roughest approach on the day side, and it is the first thing the biome does to the hull (see
"Fuel, and what this place does to the ship").

The ramp comes down into moving fuzz to the crew's knees and a steady hiss with a dry clicking under it, horizon
to horizon. The cleanse's first-hour story has it right: *"Wind is audible before anything asks for attention."*
The air is cool and damp, the light is *"the last ten minutes of a sunset that never ends."* Nothing attacks.
Nothing even looks.

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
  (The built gate: body size under 0.8 passes freely, 0.8 to 1.5 threads slowly, 1.5 and up cannot enter. Which
  side of 0.8 a Jawa falls is `UNMEASURED`; the venomvine design says *"A Jawa slips in, a person forces a way, a
  giant is stopped."*) A scratch lands on entering a stand and again each hour inside; venom fades by half a stage
  a day. **A long crossing is not survivable as built:** on 2026-11-01 one drafted walk of about 113 cells through
  the islands left a colonist's venom at 0.56 to 0.87 and downed them, cause untraced. Expeditions are short, in
  and out, or they are rescues.
- **The young edge of the vine is harmless.** A fresh runner is rust-ochre, soft and thornless and carries no venom
  until it is half grown. Trimming the front of an island is a cheap chore; walking into its body is not.
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
- **A tree with a name.** About one map in four holds one or two sweetline trees: huge, ancient, each with a name
  the road-folk gave it (*"Gomaun"*, *"Morrara the Leaner"*, *"Where the Wind Stood Still"*), the only other tall
  thing on the plain. Animals with coats walk to it and rub them off
  against the bark, because it heals them: *"they receive a health/healing bonus (Hediff) when they scratch their
  hide against it. Removes parasites and disease over time."* (owner, 2026-11-16; the healing is not built yet).
  The wool lies at the trunk for whoever dares the traffic. Who rubs is whoever grows a coat: the campaign's
  banthas and nerfs, and any woolly animal the crew brought. The plain's own animals grow none, and the
  thunderstep has no coat as built, so on a map with no coated animals the tree gives only its own slow shed of
  felt, five every five days.

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
- **Fire means someone.** *"There is hardly ever lightning... a fire almost always means someone lit it."* *"Smoke
  on the horizon is a person."* The giants despise it: *"They charge it and stamp it dead at all costs — and then
  stamp out its source."* A big open blaze brings the herd: several fires burning together in the open, not one
  campfire, and never a roofed stove. As built they stamp the fire and whatever was burning. Working out who lit
  it, by having watched or by a fresh trail, is his ruling of 2026-11-10 and is not built yet.
- **Not everything that looks dead is.** A sleeper stand is labelled and drawn as bleached dead cane, the same
  grey as the fuel, until a body bigger than a hare steps beside it. Then it is a live stand and it lashes.
- **The plain cleans up.** A rollbug rolls any corpse in reach to its larder, the crew's own dead included (his
  card of 2026-10-26: *"Any corpse in reach"*), eats it a part at a time and leaves the gear on the ground there.
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
7. **The rendering fire.** *On screen:* somebody lights a row of big open fires to render scrap. The grazing heads
   come up, all of them, and the herd walks over and stamps the fires flat, and then looks for who lit them. (The
   looking is owed; the stamping is built.)
8. **Everything stops.** *On screen:* the hiss cuts out mid-errand. The fuzz stands still for the first time.
   The shimmer in the runs freezes. Something lifts off a venomvine crown. A hauler takes one more step.
9. **The nest.** *On screen:* a Jawa crawls out of a hollow stand with an armful of wire and lens-glass, scratched,
   delighted, and the stand they robbed has stood up behind them, pale side out, where anything can see it.
10. **The scratching post.** *On screen:* a line of shaggy animals queuing at an enormous leaning tree to rub
    themselves bald, and a hooded figure darting in between two of them for the wool.
11. **Charged in a day.** *On screen:* the ship's power full before the first sleep, and in the first Gale a
    wind turbine spinning itself to pieces.
12. **The firewood stood up.** *On screen:* a Jawa sent to gather grey dead cane reaches for one more bundle, and
    the bundle goes black, rises and whips. *Why it lands:* the fuel and the trap share a label. (Built; the label
    clash is an open item, `LEANINGSCRUB_DEAD_VENOMVINE_RECONCILE_FUEL`, and should be kept as a feature.)
13. **Where did he go.** *On screen:* a crew member dies out in the fuzz. By the time anyone comes for the body, a
    beetle the size of a boot is rolling it away in a ball, and the robes and the ion blaster are lying in a neat
    pile outside a hole. (Built, live rows owed.)
14. **The umbrella opens.** *On screen:* the wind dies; the hunched thing that sat all week on the turbine head
    *"like a folded umbrella nobody wants"* unfolds and goes up, and drops through the still canopy onto something
    that *"believed, until that hour, that the roof was theirs."* (A flyer: looked at only with the owner present.)
15. **The fire they cannot reach.** *On screen:* a fire burning deep inside a venomvine island, and thundersteps
    ringed at its edge, too big to enter, stamping the fuzz in fury. (The venomvine design's intent, 2026-10-16;
    the stamping code has not been checked against the size gate: `UNMEASURED`.)

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
- **They cannot follow the crew into the vine at speed.** A trooper is a person: slow in the thicket, scratched,
  poisoned by degrees. A crew that knows its hollow stands has streets the Empire has to cut. They can still shoot
  in: the vine gives no cover as built (`NEEDS HIM` 4).
- **A reared stand tells on both sides.** Anything that pushes into rearing venomvine flags itself, troopers
  flanking through a hedge as much as a Jawa robbing a nest; in a Gale the flag cannot be read. The pitch's line
  for it: its *"weapon is information, not injury."*
- **Fog days are bad shooting days.** Half accuracy for everyone, on the commonest weather there is.
- *0.2.0:* the calling-pyre. Light the plain on purpose and bring the herds down on *"ALL who remain — attacker,
  defender, farm and field"*, *"spoken of the way sailors speak of running aground on purpose."* On a siege camp
  parked beside the ship it is the most Jawa answer in the game: burn the lot and hope to be standing in the right
  place. He merged it by card on 2026-10-01 into the controlled waking, as that rite's Scrub form (god: Zizzik);
  its found inscription reads *"When there is no way out, burn your own field. The giants will come for the fire.
  Let them find everyone."* A quench stand stalls it, and so does any island of living vine.
- *Later:* the Stall-Hold, the plain's other rite and the only cover idea in the sources that is pure Jawa: every
  member of the crew holds still in the open for the length of a Stall. *"When the wind stops, so do you.
  Everything is looking. Be the thing it does not see."* Its poor outcome is *"a scout spots the colony"*; its best
  is a raid that arrives not knowing the layout. Rites are tabled by his word of 2026-10-03.

## Who else attacks; who hates the Empire

- **Nothing hunts the crew on purpose.** *"Big things ignore the fuzz and ignore you."* The danger is being in
  the way, being near the young, or lighting a fire.
- **The interface killers** hunt each other and will take a crew member who is where the prey was: the shokka at
  the edge where a run surfaces, the fuzzviper holding a run wall, the surrik that swims the crust and comes up to
  strike, the thornhold defending its den against whoever hit it.
- **The Deep Desert Tribes** raid here in the campaign's world with a moving wall of fire, *"and leave with the
  burned."* Here *"pyroculture is pure weapon"*, and it is also *"a beacon"*: the giants come for the arsonist.
  They are placed by the campaign layer, not by this biome.
- **The road-folk are gone; their ruins are not.** He typed on 2026-10-15 that the living camps hold *"Scavengers
  and vapor farming new"*, then banned the farming people on 2026-10-20 (*"We don't want those"*) and removed
  their camps by card (*"Remove the camps"*). What is left, built and waiting for 0.2.0 by his ruling of
  2026-11-16: dead farmsteads with a comb-row of vaporator wrecks, smother-claimed fields, hedge homesteads, and
  living camps of whatever scavenger clans the campaign supplies. A scavenger camp defends at peace and attacks
  when hostile. Whether any of them fights the Empire is `UNSETTLED`.
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
- The vine: a wall the crew can cross and a larger enemy cannot. (Being unseen inside it is `NEEDS HIM` 4.)
- Fog days, which slow the search from orbit by a step.
- The giants, for a crew that has learned never to be the one seen with the match.

## What the crew takes away

- **A full charge,** and whatever the crew builds with a week of power nobody had to pay for.
- **Scrap from the hoard stands and the nests:** wire, lens-glass, hull chips, and whatever gear died in there.
- **Raw venom,** harvested from the dripping stands, three to a harvest, and the stand beads again. A trade good,
  and the makings of the sap-mark; the content item also names it a *"weapon coating / medicine precursor"*
  (neither is built).
- **Sweetline felt,** *"a uniquely comfortable blend"*: bedding and coats for a cold hold (built: a comfort bonus
  in furniture, a small mood lift worn). The older name "giant-wool" names a source that is no longer the source;
  the word for it has never been ruled.
- **Cane:** dead venomvine, *"the finest fuel in the region — wood that spent its life refusing to burn and, dry
  at last, burns long and hot."* As built it burns exactly like wood; burning better is owed. A grown stand gives
  about forty.
- **Pelts and meat** from the interface, *"reliable protein... for those who learn the crossings."* A shokka pelt
  *"takes dye badly and light beautifully, and a coat of it is the closest a person gets to being hard to see out
  here."*
- **Vissler arms,** shed still twitching when the runs flush. *"Hunters buy them."*
- *0.2.0:* plans recovered from a dead farmstead, and a vaporator the crew can build elsewhere.

## Fuel, and what this place does to the ship

**Fuel: the emergency-slow kind, with one premium exception a visitor can only find or buy.** (Owner's ruling of
2026-11-18: most biomes only render biomass, *"uselessly slow, only for emergencies"*; *"you can also buy it."*)
The Scrub is worse than most at biomass: its living plants *"resist fire greatly and burn only grudgingly."* Its
one real fuel is cane, and in the fiction making cane is the local industry of years: throw a blanket over a
thicket, starve it of light, come back when a grandchild is grown. *"My grandmother darkened this stand."*

**The built clock is not years.** The blanket craft ships with a claim of thirty days by default, on a slider from
one day to a hundred and twenty (read from the mod's settings). The Designer of 2026-11-16 saw that, declined to
ask him, kept the sheet's "years" and proposed a hundred and twenty days. So there are three clocks on record and
he has chosen none of them. At the built thirty days, a crew that lays a blanket in its first week collects cane
at the outer edge of a stop; at a hundred and twenty it never does. A blanket costs forty fuzz fibre and fifteen
felt, woven at a tailoring bench, and the felt comes only from a sweetline tree, which three maps in four do not
have. This is `NEEDS HIM` 2.

Whatever he rules, a visiting crew gets cane three more ways: from the tail of a walking stand that has died back
behind itself (built); by **buying** it, from traders and from the scavenger camps when those arrive in 0.2.0;
and, also 0.2.0, from a smother-claimed field somebody else banked and is not there to defend (the ruin is built).
The last is the very Jawa one. And a blanket does one thing inside any stop: a smothered tail stops a walking
stand, and the venomvine design says smothering the body stops a whole island creeping. The Scrub is **not** a
fuel stop; it is the power stop.

**What wears on the ship (owner's ruling of 2026-11-18: in 0.1.0, from what the sources already say; his list
included "rough weather turbulence in the approach").** The frame for it already exists and this design adds
nothing to it: `src/RimUtinni/ShipShields/`, built to his shield rulings saved 2026-09-02. *"The environment is
hostile and immediately goes to work on the ship. The ship will know what's visibly dangerous and will advise
course of action, but no more than that. Its hull is thick and can take a lot of damage in most situations."* As
built, a ship sitting in a hazard its shield is not set for takes slow wear on a few things near the hull every
few hours, twice as fast once it has sat there about six hours, with an advisory letter and then a sharper one,
and never a refusal to land. Three hazards are known to it: heat, cold and particulate. Three things wear here:
- **The Gale, as the particulate hazard.** His ruling on the particulate screen names this place's weather first:
  *"Light kinetic deflectors handle wind, ash, vapor, bio contamination, spores, smoke, sand, and rain damage
  completely as well as repels small animals."* And the Gale he ruled on 2026-10-20 is *"driven dust and fuzz."*
  So a ship caught in a Gale without its particulate screen up wears, and the shield design's own words say how:
  abrasive grit in *"thruster intakes, joints and vents"*, and neglect that ends in a ship that will not launch.
  *Answer:* the particulate screen, which is the cheap shield; or land and leave outside a Gale, since the wind
  state is readable. On the ground a Gale also does to the crew's wind gear what it does to anyone's: surge,
  breakage, repair. **One piece is missing and is my proposal, not a source's:** the built frame recognises a
  particulate hazard by a weather's sand rate, and the Gale's definition does not set one (measured), so today the
  frame cannot see a Gale. Setting it is one field. `NEEDS HIM` 5.
- **The vine.** A strangler stand wraps a wall or tree beside it and damages it until trimmed; a shedding stand
  litters the ground downwind with thorns each Gale. *Answer:* hands-on work, exactly as the code already calls
  it: trimming and sweeping. Do not park against a black island, or downwind of a ragged one. (`UNMEASURED`:
  whether a strangler will take hold of a hull part; it is built for walls and trees.)
- **The giants.** A thunderstep *"will walk through your wall on its grazing line, ignore your rage, and not know
  what it did."* *Answer:* do not land on a grazing line, and never give them a fire to stamp beside the hull. His
  ruling on the heavy shield says it *"resists impactors, blaster fire, and large animal assault"* and is *"very
  energy intensive when struck"*. (`UNMEASURED`: whether wall-indifference is built; the stamping is.)

The particulate screen also *"repels small animals"*, which settles what happens to the runway nations around a
shielded hull: nothing moves in.

**Two older ship ideas were declined and are not revived here.** Both come from the review of 2026-09-29: that the
landed ship casts a calm lee where things green and nest, and that the launch burn reads as fire and brings the
herds. He cut both at the sitting. They are listed with his words under `NEEDS HIM` 1.

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
- **Giants that answer fire and know who lit it** (`RM_FireStamp` is built; the witness-and-trail tracking is
  not). The owner wants the tracking built robust because *"we will need this later for the ownership mod
  anyway."*
- **A tree that animals use** (`RM_SweetlineScratching`): an auto-shearing station; the healing is owed.
- **What a place does to a landed hull** (`src/RimUtinni/ShipShields/`): the Scrub is where the particulate
  screen meets wind rather than sand, and where "repels small animals" has the most small animals to repel.

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
- Cane as a fuel worth having, taken from stands that have died back. (the item is built and burns as wood;
  burning better than wood is owed; a visitor's route to it is this design's)
- The sweetline tree: named landmark, coats rubbed off, the healing his words added, wool on the ground, the one
  harvest of felt, felt's comfort. (built, except the healing)
- The native cast and what each does; pillowmoss wetting ground from fog; tanglefuzz anchoring dens; crustweevils
  grazing cruststar. (some built, several marked by the sheet as owed)
- Thundersteps stamping open blazes; parental enrage. (built; the stamper marking reaches the thunderstep through
  the campaign's patch layer, and no franchise-free stamper ships yet)
- Thundersteps finding the maker by witness or trail. (his ruling of 2026-11-10; not built)
- What the place does to the landed ship: the Gale as a particulate hazard on the built ship-shield frame,
  strangler and thorn litter, a giant on its line. (the frame is built; the Gale's definition needs its one
  field, `NEEDS HIM` 5; the rest is built for ordinary structures)
- Fog as one step of cover from orbit on fog days. (new, small, by his card)
- The plain's sound: wind, the tikkit click-chorus, wing-bursts and stranger calls, quiet in the Stall. (built on
  vanilla sounds; his ruling of 2026-09-28)
- The rollbug rolling any corpse to its larder; the thornhold standing its ground at its den against whoever
  struck it and nobody else; the shirrel gliding downwind in a Gale and walking home to its tree. (built; his
  cards of 2026-10-26)
- The scanner's readings here; the eggs that hatch near people. (built)

**0.2.0, the stop with company** (the owner's own "next Design Version" of 2026-11-16, plus two lens additions)
- The dead farmstead, recovered plans, the plain wind vaporator, and the scavenger clans' camps with their peace
  and war. (built, unproven; his ruling. The vaporator has no dried wake: his card of 2026-10-16, *"Plain
  vaporator, no scar"*. The farming people's camps are gone: see "Dropped".)
- The calling-pyre: its three beliefs, the rite, the field fire and the herds. (built, unproven; his ruling)
- Blanketed claims found on the map, banked by somebody else and ripe; cane bought from traders and camps. (the
  injection step that places smother-claimed fields is built; buying is ordinary trade)
- Wild sworn stands, *"those a dead settlement left behind"*, at the hedge homestead ruins: a hedge that spares
  whoever carries the sap-mark, and the mark can be looted. (built; his card of 2026-10-03)

**Later (a crew that stays, or a colony)**
- Laying a smother blanket and waiting for the cane, if he rules the long clock. Built (at thirty days) and
  locked into the current tree; see `NEEDS HIM` 2.
- Sworn venomvine: the one strain a player can sow, and the sap-mark that lets its own walk through. A hedge-fort
  is a home's wall.
- Transplanted venomvine as fortification; farming under cover and growlight; the moisture farmer's whole trade.
- The sweetline tree-roads, the name register's deeper layers, pilgrims and traveller camps at the trees.
- The Stall-Hold rite. The Blurrg as a tamed-only mount (campaign; his words *"yes Blurrg here"*, then by card
  tamed-only, arriving by trade, scenario or quest: *"carried here, the way saddles are — and the plain has not
  been consulted"*).
- Cover, concealment and scent masking for a body inside a stand, unless he takes it sooner (`NEEDS HIM` 4).
- Living cane as a spiked building material for fences and traps (venomvine design, proposed, never built).
- People who actually walk in and camp under a sweetline tree. As built a "visit" is cold ash or a token left at
  the trunk and a line in the tree's history, with nobody seen.
- The fuzz changing colour along the gradient from the stormwall; the sweetline as a contour on the map.
- A crust terrain of our own to replace open sand.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- **The ship's wind-shadow and lee** (cut 2026-09-28, his words: *"No, we dont need a downwind lee around the
  ship."*) and **the herds converging on a launching ship** (cut the same sitting: *"Yes in 1. 2) not needed."*).
  See `NEEDS HIM` 1.
- The bark-wardens, the trees' guardians (cut 2026-10-23); the vaporator-farming people and their camps (banned
  2026-10-20, *"We don't want those"*; camps removed by card); the vaporator's drying scar (card 2026-10-16,
  *"Plain vaporator, no scar"*); any work to preserve old saves (his answer of 2026-11-16: *"the savegame stuff
  is simply gone"*).
- Silence as the plain's sound (reversed 2026-09-28: *"A rich soundscape of bugs and birds and stranger animals in
  the wind"*).
- Creatures built or described as warning instruments (*"Too much focus on constant advanced warning... Players
  arent that into it."*).
- A resident animal of the large size band; rain; lightning or any fire nobody lit; dense flora other than the
  vine; a still ordinary day.
- "Cover everywhere" for people (*"interpreted only for smaller things than you. People stand out."*).
- The vissler arm's own code (the behaviour is vanilla; the animal and its arm stay).
- No worldgen and no guaranteed tiles; the planet is painted once, at the end.

## NEEDS HIM

Each is tagged with one theme word.

1. **[hull] Two ship ideas he already declined. Not revived; listed so he can say if the lens reopens them.** The
   review of 2026-09-29 pitched the landed ship as *"the tallest thing on the plain"*: a calm lee behind the hull
   where fog-fat plants green and *"thornholds [nest] in your hull's lee"*, and *"at spool-up the engine reads as
   FIRE to the plain — thunderstep herds converge on a launching ship to stamp the burn."* At the sitting of
   2026-09-28 he typed, on the first, *"No, we dont need a downwind lee around the ship."* and on the second,
   *"Yes in 1. 2) not needed."* The mechanics item records *"both halves cut by his word"*, and the later GPT
   consult was told *"none of these restores a gravship mechanic."* That was seven weeks before he asked for every
   biome through the ship's eyes. *Stay cut* (default here; neither is in any scope bucket). *Reopen the herds:*
   the biome's strongest ship moment, and the review's own caution applies (*"herds delay/damage, never
   forbid"*). *Reopen the lee:* note that the Long Shade has a built relative, the Shipfall Commons, where a
   landed ship's shade draws wildlife.
2. **[fuel] Which clock does a smother claim run on?** The sheet says years. The mod ships thirty days, on a
   slider from one to a hundred and twenty. The Designer of 2026-11-16 chose not to ask and proposed a hundred and
   twenty. His validated bar of that day names *"banked years-long smothering and premium useful cane fuel."*
   *Leave the built thirty days:* a crew can lay a claim and collect inside one long stop, and the craft is in
   0.1.0 whole. *A hundred and twenty days or years* (default here, because the bar says years): laying a claim
   moves to "later", cane stays in 0.1.0 through died-back stands and purchase. *Keep the lore and shorten only
   for a visitor:* two clocks, which is a rule nobody has needed before.
3. **[cover] Does fog that comes and goes count as cover?** His card names fog: *"Canopy, steam and fog slow the
   search by one step."* Here fog is weather, about half the days, not a standing condition. *Yes, on fog days*
   (default). *No:* the Scrub is the planet's open ground, power paid for in exposure.
4. **[cover] Should a body inside venomvine be hard to see?** Proposed on 2026-10-16 and never built: half cover in
   or behind a stand, a pawn deep in an island hidden from view, and scent masked. Without it the vine slows
   pursuers and hides nothing. *Not promised* (default here: this design claims only the size gate). *Build it in
   0.1.0:* the crew gets real ground cover, and troopers get it too. *Scent masking only:* cheap, and it makes the
   thicket the place to hunt from.
5. **[hull] May the Gale count as a particulate hazard?** His shield ruling names wind, and the frame is built,
   but the frame reads a weather's sand rate and the Gale's is unset. Setting it is my proposal. *Yes* (default):
   the Gale wears an unscreened ship. *No:* the Scrub's hull wear is the vine and the giants only.
6. **[scope] One signature, or every "did you see that"?** His card of 2026-11-17: a biome's first version holds
   *"Land, life, one signature."* The cleanse that followed chose the creeping vine as the signature and proposed
   switching off, for 0.1.0, the ripple, the Stall's hunt, the runs flushing, the lash, ten of the thirteen kinds
   of vine, the rollbug, the gliding shirrel, fire-stamping and the tree's history, and asked him whether they
   stay. No answer is recorded. The day before, he had said of those same things *"Why am I choosing between
   these? These are all important."* The day after, he made the *"OMG did you see that?"* *"the overriding
   priority"*. *Keep them all in 0.1.0* (default here: nearly every moment in this design's list is one of them).
   *One signature:* 0.1.0 is the wind, the vine islands, dripping and hollow stands, the tree and the plain
   animals, and most of the list above moves to 0.2.0.
7. **[other] Should lightning exist here?** The sheet bans it (*"fire implies folly"*), and the giants' whole
   response assumes a maker. The biome's weather list carries a windy dry thunderstorm at weight 1 of 85, added
   when he asked for calm days to be given the Scrub's wind (card 2026-10-20). The cleanse read that as *"preserve
   its wind while excluding ignition."* *Remove the strikes* (default). *Keep them:* a rare fire nobody lit, and a
   herd looking for a culprit among the crew.
8. **[locked-tree] The locked tree promises a home.** `sheet.md`, `tree.json` and `scenes.json` (locked
   2026-11-16) are built on *"a dependable wind-powered home"* and on his card of 2026-11-10, *"Home and routes
   are safe."* This design reads home as the landed ship and its apron and has not touched those files. A later
   Designer run has to reconcile them; until then two documents in this folder disagree about who lives here.
9. **[other] Does the thunderstep grow a coat?** The tree's ruled spec left it open: as built the giants do not
   rub, though the sheet's picture of the tree is giants rubbing. *No* (default, as built). *Yes:* one line in the
   campaign layer, and the scratching post gets its biggest customer.
