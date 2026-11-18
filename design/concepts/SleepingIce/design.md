# The Sleeping Ice: the design, seen from the ship

**Status:** the one design document for the Sleeping Ice biome (`RM_SleepingIce`, source
`src/RimMandrake/SleepingIce/`; older files call it the Nightside Ice), rewritten 2026-11-18 on the owner's
instruction to see every biome "through the lens of Utinni". It replaces the older definition sheet, roster draft,
review and cleanse proposal as the place to read; what happened to every idea in them is in
`design/concepts/SleepingIce/rewrite_choices.md`. Nothing has been deleted yet. This is a design document only and it
launches nothing.

**Kind, checked against the sheet's own header:** land. A high plateau of ice on the night side, *"the deep night's
mountains, under ice"*. It is not a sea and the seabed rulings do not apply.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/SleepingIce/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Sleeping Ice has no locked sheet or tree; its only pipeline material is the
cleanse proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"Dirty white ice on the highest ground of the night, under the aurora, with something moving inside it."*
> (`sleeping_ice.md`, header)

Ice as hard as quartzite, white because it is full of everything the sky ever dropped, under stars and aurora, with
no wind at all. *"The ground rings when you strike it and fractures in slabs."* Nothing grows. There is no water in
any form. *"Life here does not grow. It catalyses, and it waits."* What looks like a ridge is one animal. What looks
like nothing is a blind thing inside the ice, turning toward the nearest warmth.

The owner's line for the experience, picked by card on 2026-10-20:

> *"A frozen highway that nobody stays on. You cross it, dig into it, or go under it."*

And the law of the place, from the sheet, which no other biome has:

> *"Sensing is thermal, and the player is the loudest thing on the hemisphere... Insulate, run cold, and nothing
> comes. Heat the base to a comfortable temperature and you have lit a flare on a dark plain."*

**Seen from the ship, the base is the hottest object for a thousand miles.** A review of 2026-10-01 said it and
nobody picked it up: *"A landed ship is the hottest thing on the hemisphere, and that is unclaimed."* This design
claims it. The crew does not build a refuge here; it sets down a warm hull on cold ice, and the plateau notices.

The crew are small, hooded and built for the dune sea. The sheet's rule for this hemisphere is flat: *"Anything warm
on the nightside is a visitor, a machine, or dying."* The Jawa are the first, live in the second, and are one broken
heater from the third. They came because the sheet's other promise is the best thing a scavenger has ever heard:
*"Everything that ever landed here is still exactly where it landed"*, and *"nothing on the nightside rusts and
nobody comes out here to strip it, so whatever was bolted inside is still bolted inside."*

So the stop is a bargain a Jawa understands at once. The salvage is perfect and nobody else wants it. Every degree of
comfort is paid for.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew shortens every wait and a hidden one lengthens it.

**The outer edge of a stay here: about a month, and about six weeks for a crew that runs the ship cold.** By the
owner's word of 2026-11-18 the figure a design derives is *"the outer edge allowable"*, not the typical stay. It
comes from the ladder's own arithmetic: if the Empire wins every step, the bombardment is the fourth full interval,
which is 20 to 32 days at the ordinary pace and 28 to 45 days one step quieter. Most stops end long before that,
because of what is in the next two paragraphs.

**Cover from orbit: none overhead; the cover here is cold.** His ruling of 2026-11-18 gives each biome partial cover
by its own nature: *"Canopy, steam and fog slow the search by one step; full dark still pauses it."* The plateau has
no canopy, no steam, no fog and no weather; it is open white ice under a bright aurora. What it has is in the sheet:
*"Buried and bermed structures, exteriors at ambient — thermal camouflage, unique to this hemisphere"*, and
*"Whoever is out here is out here to be un-findable."* So this design gives the Sleeping Ice its one step for a ship
whose thermal signature is held low, and nothing for a warm one. The same dial that brings the tunnelers is the one
the Empire reads. Whether the sunless night also counts as the "full dark" that pauses the search is the first
question under `NEEDS HIM`; the default here is that it does not.

The plateau is also the worst ground on the planet for hiding from anything at eye level. It is flat, white and
still: *"The party can see farther than it can afford to walk unprotected."* A probe droid that needs to see the ship
will see it.

---

## The first minutes

The ship comes down out of the aurora onto a plain with nothing on it. No snow blows, because nothing blows here.
Hoarfrost stands in crystal gardens and feathered blades that only perfectly still air can build, and the landing
wash is the first wind they have ever met.

The ramp drops onto ice that rings underfoot. The crew steps out into a cold that the desert has no word for, and
steps back in.

Three things are in view before anyone has decided anything: a frost-locked hull section a short walk off, white with
rime and plainly never touched; a low ridge with a seam along its spine that is slightly too regular; and, on the
screen, a new reading that was not there on any dayside landing, the ship's own **thermal signature**, already
climbing.

Nothing attacks. Nothing here is fast. *"Nothing moves on a human timescale — on the surface."*

## The first day

- **The salvage is untouched.** Frost-locked hull sections, cylinders and the frames of crystal-cutting rigs from
  expeditions that never came back stand where they fell. They come apart with ordinary work and give ordinary
  salvage. They are finite and nothing replaces them. A frost-locked cylinder is *"a fuel or pressure cylinder frozen
  where it landed, its seams still whole. The cold kept what was inside it."*
- **Nothing here can be eaten and nothing grows.** No plants, no soil, no water. The crew eats what it brought, and
  so do its animals. The one mercy: nothing the crew brought will rot outdoors.
- **The ridge is alive and does not care.** The hessarund is *"a ridge, by every measure you can take of it. It is
  also one living thing."* It mines like stone and gives a chalky, rose-tinted catalyst crust. It never moves and
  never answers, by the owner's ruling of 2026-10-01 (*"only a landform"*).
- **The pale goat.** A zhissa or two cross the plain, six-eyed and seeing nothing, reading the world by heat. They
  give milk. They discharge static when handled roughly, and a Jawa is rough with everything.
- **The ship is loud.** Every heater, every powered machine and every warm compartment adds to the thermal
  signature. The alert says what is contributing. A crew that wants to work bare-handed in a warm hold is choosing
  something, and the game says so before anything comes of it.

## The first week

- **The first crack.** Somewhere in the open ice beside the ship, a crack appears, and a letter explains it once:
  the ship's warmth has softened the ice around it, something below is coming up through that crack, and there is a
  countdown. The crack is a thing on the map that can be attacked. Break it and nothing comes. *"The colony's
  first-ever breach is precisely timed — it teaches the mechanic; every later breach is vaguely warned, direction
  unknown."*
- **The shivven.** Blind, dog-sized, hairless tunnelers that travel *inside* the ice. The player never sees one
  travel. What shows is a seam running across the ice with a low grumble under it, heading for the warmest thing it
  can reach. It surfaces to bite that thing and goes for whoever hits it.
- **The floor line.** *"A burst can NEVER come through constructed floor or the gravship hull."* (owner,
  2026-09-24.) The shivven cannot cross flooring either. A crew that lays an apron of floor around the ramp and keeps
  its warm fittings behind it has a line the ice cannot pass. A crew that sets a heater out on bare ice beside a
  salvage job has made a lure.
- **Reachable warmth wins.** His answer of 2026-11-10: *"an inaccessible heat source loses its appeal, and the
  shivven redirects toward warmth it can reach."* The ship's reactor behind its hull does not hold their attention.
  The camp stove out by the wreck does.
- **The choice.** Run the ship warm and guard its edge, or run it cold and work in frostbite. *"Ward with cold, never
  with lamps."* Light does nothing here; nothing native sees.
- **A way down.** Some maps hold a mouth into the Lantern Deeps (`src/RimMandrake/LanternDeeps/`, its own design).
  The Sleeping Ice only has to host that entrance and let a party go down and come back. It is the *"go under it"*
  of his line.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The step back.** *On screen:* the ramp comes down, a hooded figure walks out onto the ice, stops, and walks
   back in. *Why it is funny:* they are desert people, and the game's own temperature reading is the punchline.
2. **The floor is knocking.** *On screen:* a crack in the ice near the ramp with a countdown over it, and several
   Jawa hitting it with whatever they were holding. *Why it lands:* the first one is fair. They were told exactly
   when.
3. **The seam.** *On screen:* a hairline running across open ice toward the camp stove, the ice twitching along it,
   a grumble getting louder. Nothing else is visible. Then a pink-grey wrinkled thing with ivory incisors comes up
   through the ice and bites the stove. *Why it is alarming:* the player watched it come the whole way and still had
   to decide.
4. **The doormat.** *On screen:* a Jawa standing on the last floor tile of the apron while a shivven circles in the
   bare ice a cell away, unable to cross. *Why it is funny:* both of them know.
5. **The goat bites back.** *On screen:* a crew member goes at a zhissa with a prod, there is a blue-white snap, and
   the crew member is on the ice. *Why it is funny:* they will try again.
6. **Still bolted inside.** *On screen:* a rime-white hull section comes apart and gives up fittings that look newer
   than the ship's own. *Why it lands:* for scavengers this is the cathedral. The crew strips it with the ramp
   heaters off, shivering.
7. **The dark ship.** *On screen:* every heater off, the thermal signature falling, the crew bundled in the hold
   with their breath showing, and a seam on the ice outside slowing, stopping and waiting. *Why it lands:* hiding
   here looks like nothing else in the game.
8. *(0.2.0)* **The mound moves once.** *On screen:* a low even mound of ice that has been in view since landing
   lunges, all at once, onto the campfire, and never moves again. The sheet: *"There is no fleeing from it and no
   fighting it twice."* What is left is *"a corpse that is still technically alive."*
9. *(0.2.0)* **Someone is in the ice.** *On screen:* a pane of clearer ice with a dark, human-shaped blur in it, one
   arm out. *"Cut them out and you can have whatever they carried."* *Why it is very Jawa:* they do, and they
   haggle over the pack.
10. *(0.2.0)* **The frost that points.** *On screen:* fans of feathered frost growing on the open ice, every plume
    leaning the same way, straight at the one compartment the crew forgot to shut. *"It points straight at whatever
    is warmest."*

## When the Empire arrives

The ice does not take sides, and the Empire is warm.

- **Open ground.** There is no cover between the plateau's edge and the ship. A strike team is seen a long way off
  and sees the ship from the same distance. Fights are long-range across bare ice or close at the hull.
- **The floor line holds for whoever stands on it.** The crew fights from its apron and its hull. Troopers who walk
  in across open ice are standing where the shivven travel.
- **Their warmth counts.** The design intent, from the sheet's law, is that the tunnelers read heat and nothing
  else: a siege camp's fire, a cordon emplacement with its crew huddled round it, and a trooper downed and still
  alive on bare ice are all warmth on open ice. *"A body dying on the plateau is a warm signal in the ice; the
  tunnelers come to it from below."* Built today, the shivven seek only the player's own working heaters; fires,
  warm rooms and downed living bodies as targets, whoever owns them, are in this version's scope below and are not
  built.
- **A cold crew is hard to starve out and easy to see.** A cordon that sits for two days sits on a plateau with no
  food, no fuel and no shelter but what it brought. So does the crew.
- **What a fight leaves behind does not spoil.** Dropped gear and the dead stay exactly as they fell.
- *0.2.0:* a thaw softens the ice under whatever has sat warm longest, and a slab can go from under a camp; the
  sohl commits to the largest steady warmth within its reach, and a siege camp is that.

## Who else attacks; who hates the Empire

- **The shivven,** impartially.
- **Almost nobody else.** *"The only animals here are migrating to somewhere else — or badly lost."* Ordinary raids
  still come by the storyteller's own rules, and they arrive cold and exposed like everyone else.
- **Heat-drawn assailants (0.2.0).** The sheet rules that mutated assailant assaults *"reach the plateau only as
  heat-drawn incidents — a raid form and a wild manhunter-style pack form."* *"What they leave behind is warren
  food."*
- **Wampa and tauntaun** are in the campaign's cast here as dying visitors, patch-added in the Utinni layer. A
  wampa that is *"badly lost"* is still a wampa.
- **Who hates the Empire:** the sheet seats four Free Droid Enclave holdings on this ground (*The Trade Socket*,
  *Vent Nine*, *Coldfire*, *The Cracking Station*), *"built cold on purpose"* so that nothing organic follows them.
  They are placed by the campaign layer, not by this biome. Whether they fight the Empire or only hide from it is
  `UNSETTLED`.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The larder. Nothing here feeds anyone, and the animals eat from the same stores.
- The fuel it costs to stay warm, against the trouble warmth brings. A warm ship fills the ice around it with
  waiting shivven; they do not leave when the heat drops, and they do not starve.
- The salvage running out. The wreck field is finite and the reason for the stop goes with it.

**Stay, longer than the Empire would like:**
- A floored apron and warm fittings kept behind it.
- A ship run cold: the tunnelers lose interest and, by this design, the search above slows one step.
- Stores that cannot rot.
- The way down, where the map has one.

## Fuel, and the hull

**Fuel: the emergency route only, and barely that.** The sheet is blunt about what the plateau gives: *"Not food,
not water you can drink unfiltered, not fuel, not safety."* The slow rendering of biomass into chemfuel that every
biome allows has almost nothing to work on here, because there are no plants; it runs on carcasses and on what the
crew carried in. The one local find is salvage: a frost-locked cylinder can hold chemfuel (the tank salvage table in
`src/RimMandrake/Wreckage/Defs/ThingSetMakerDefs/RM_SalvageLoot.xml` lists it), a few to a map and never renewed.
That is a very Jawa way to refuel and it is not a supply. The rich fuel of the deep night is the next biome down the
slope, the propane sea, and it belongs to that design. **Where fuel is bought:** the sheet puts *"cracking and tap
plant on the pan margins"* and names a droid holding *The Cracking Station*; whether an enclave sells is the
campaign layer's to say, `UNSETTLED`.

**The hull: cold, and its own warmth.** His ruling of 2026-11-18 puts the biome's wear on the ship in 0.1.0 and
names *"heat or cold"* among the kinds. Here the sources name three things and this design uses two.
- *Cold (0.1.0).* The air is far below freezing all year. Holding the ship habitable is a standing cost in power
  and fuel, and it is the same cost that raises the thermal signature. The answer is insulation and discipline:
  closed doors, thick outer walls, cold outer compartments.
- *The edge (0.1.0).* Floor and hull stop the tunnelers from coming up or crossing; they do not stop a shivven on
  bare ice from striking a warm fitting that stands at the hull's edge. Exposed heaters, vents and powered fittings
  on the ship's rim take damage from the ice side. The answer is the floored apron, and hands to repair what was
  bitten.
- *The footing (0.2.0).* The sheet: *"stay light, because a warm building softens its own foundation."* With the
  thaw built, a ship that sits warm softens the ice around itself; that soft ring is where cracks open and slabs go.
- *Not used:* the kesshet, a crust that grows on the warm hull and must be scraped before launch. It is the only
  idea in any source written about this ship on this ice, and the owner passed it on 2026-10-01, before he stated
  the ship lens. It is the second question under `NEEDS HIM`.

No shared system for hull wear was found in `src/` (the ship mods there are landing, hoist, vermin and scanner). The
two 0.1.0 kinds above need none: they are ordinary heating load and ordinary building damage.

## What the crew takes away

- **Salvage in mint condition,** the best on the planet for its weight.
- **Whatever was in the cylinders.**
- **Catalyst crust** from the ridge: a building stock, nothing more promised.
- **Zhissa,** tame, for milk; and their shock, for anyone who earns it.
- **A larder that kept.** Anything stored on the ice left exactly as it arrived.
- **Whatever the Deeps gave up,** if the crew went down.
- *0.2.0:* the kit of the ice-kept dead; the spent body of a sohl, cut for crust and hide-plate; whatever a calving
  slab delivered.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Warmth exposed to the ice raises a readable thermal signature, and a ship run cold sees no trouble. | Two identical landings: one heated with doors open and a heater on bare ice, one run cold. Run the days. | A third landing, just as comfortable inside but closed and insulated, draws less than the open one and more than the cold one. |
| The first crack is taught: a letter, a countdown, an attackable crack. Breaking it stops the breach. Later cracks are warned without a time or a direction. | Let the first crack come naturally; break it. Let the second come; find it by searching. | A crack ignored to its deadline releases shivven. A save and reload mid-countdown keeps the deadline. |
| Shivven travel unseen inside the ice with a moving seam and a grumble, toward warmth they can reach. | A strong heater behind flooring and a weak one on bare ice, both in range. | They go to the weak reachable one and do not linger at the strong one. |
| Nothing comes up through floor or hull, and nothing crosses it. | A ship with a floored apron, a pending crack floored over, a shivven on the ice side of a concave floor. | The floored crack is visibly sealed and never reopens elsewhere. The shivven routes round or waits in view; it does not teleport. |
| A warm fitting at the ship's edge on bare ice gets bitten; the same fitting behind the apron does not. | Two heaters on the hull's rim, one with floor between it and the ice. | |
| The ice does not take sides. | An unowned fire and a downed, living stranger on open ice, with shivven already up. | A cold corpse in the same place draws nothing. |
| The frozen wrecks give real salvage and are not replaced. | Strip a hull section, a cylinder and a rig; wait a season. | |
| Nothing grows here and animals need feed. | A zhissa with and without stored feed. | No plant of any kind appears, with the growth engine on. |
| A zhissa gives milk and shocks who fights it hand to hand. | Milk one; strike one in melee. | The same blow on a pack animal with no charge. |
| The ridge mines to catalyst crust and never moves, wakes or answers. | Mine part of a hessarund and build a wall of the crust. | A heater left beside the rest of it for days changes nothing. |
| A ship held cold is searched for more slowly than a warm one. | Two landings on this biome, thermal signature low and high; read the search's next-contact time. | The same two ships on open desert show no difference from heat. |
| Nothing vanishes. | Kill a surfaced shivven, a submerged one, and one mid-travel; switch the mod's master setting off with a crack pending. | Every animal is a body or a visible waiting animal; the crack is visibly cancelled. |

Settings: one switch per major feature, defaults as shipped, everything off leaves an ordinary ice sheet with wrecks
on it (standing rule, every mod).

## Shared machinery

**Featured here** (the Sleeping Ice is where each is vital and should be proven):
- **Loudness measured as heat** (`RM_HeatDial`): heaters, fires, power draw and warm rooms summed into one reading.
  Nothing else in the game prices comfort. This design also asks the Empire's search to read it on this biome.
- **A threat that travels under the surface with a live tell above it** (the submerged-travel kit in
  `CreatureBehaviors`, built first for the Stillsand's sand-swimmers and retuned here to follow heat through ice).
- **A breach that is a thing on the map** (`RM_BreachLoop`, `RM_Building_BreachCrack`): taught the first time,
  vague afterwards, attackable always.
- **Ground a creature cannot leave** (the ice-only routing and the hull rule).

**Merely active here:** wreck salvage and its Frozen weathering (`Wreckage`); the ship's acoustic scanner, which
reads cracks, wrecks and voids here; bone from butchery; Lantern Deeps entrances; the nightside aurora
(`WeatherSuite`); the one sun from geometry, which on this side of the world is no sun at all; the growth engine,
which must leave barren ground barren; the rule that no walking giant passes over this biome (`HugeThings`); cold
storage, which the outdoors does for free; the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**0.1.0, the stop**
- The land: hard dirty-white ice, no plants, no water, no weather, the aurora overhead. (built) Hoarfrost forms as
  scenery and the hessarund ridge with its catalyst crust. (art done; unbuilt)
- The thermal signature and its alert; the taught first crack and vaguer later ones; the shivven, their seam and
  grumble; the hull rule and ice-only travel; reachable warmth over stronger unreachable warmth. (built; the last is
  his answer and is not yet how the code chooses)
- Fires, warm rooms and downed living bodies as warmth the shivven can go to, whoever owns them. (unbuilt)
- The frozen wreck field: hull sections, cylinders, expedition rigs. (built)
- The zhissa with its milk and its shock; the tellurox as a pack beast the crew can own; the campaign's dying
  visitors where the Utinni layer adds them. (built; the shock moved in, see `rewrite_choices.md`)
- The cold as a standing cost on the ship, and bitten fittings at its edge. (ordinary systems)
- A cold ship searched for more slowly. (unbuilt: one call from the thermal signature into the visibility dial)
- The scanner's readings here; hosting a Lantern Deeps entrance with a real trip down and back. (built; the trip is
  unproven)
- Nothing disappears without a sign.

**0.2.0, the stop with company**
- The sohl: a mound that moves once. (art done; unbuilt)
- The ice-kept dead: bodies in the ice, cut out with their gear. (unbuilt)
- The thaw and the calving slab: the ice softening under steady warmth, and giving up what it held. (unbuilt)
- Frissim woken by a thaw, and wyrmlets coming up to eat them: *"seeing wyrmlets means you are in the big one's
  country."* (art done; unbuilt)
- Neshkoll, the frost that points at the leak; saallen, the crust that blisters where the ice has gone soft.
  (unbuilt)
- Heat-drawn assailants, as a raid and as a pack. (unbuilt)
- The lost soul: a dying traveller on the plateau, with the tunnelers already coming. (unbuilt)
- The insect-fall: a freeze-dried dayside swarm dropped at the column's foot, food for whoever gets there first.
  (unbuilt)

**Later (a crew that stays, or a colony)**
- The dhorrumak and its nest: *"It came because you were warm for too long."*
- The larder, and the rescue into a pocket under the ice (his answer of 2026-11-10: *"pocket map style"*, with a
  way home).
- Oolm, the clonal lobes that harden as they are cut, and their insulating block.
- The reconnection storm; rime-fall and ablation at the plateau's margins; the Abyss's Dark drifting over;
  crevasses that open, close and collapse.
- The Cold Ledger rite (ruled-kept 2026-10-01; campaign layer).
- Cold as a resource (superconduction, heat rejection), the electrojet tap, dirty ice melted and filtered.
- A lasting refuge at colony scale, which his answer of 2026-11-10 allows as *"exceptional"*.
- Droid enclaves, bermed structures, the failed Junker expeditions as sites: campaign layer.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- The Breath-Choir, the Witness Method, the kesshet and the Keel-Press (*"I don't like any of these. We should
  likely just pass this."*, 2026-10-01). The kesshet alone is asked again below.
- The ridge that bargains and the ridge that creeps toward heat (not chosen 2026-10-01).
- The Exchange at the Crack and the Cold Hearth rites (not taken 2026-10-01).
- The six donor residents and vanilla's arctic zoo (evicted 2026-09-24; the roster is closed and not reopened).
- Warding with light. Walking giants. Snow, wind or rain on the interior. Farming of the ground, ever.
- **Recommended for dropping, not yet his:** the tellurox hexplate floor (the cleanse's recommendation, kept).

## NEEDS HIM

1. **Is the sunless night "full dark"?** His ruling pauses the orbital search in full dark. The Sleeping Ice has no
   sun, ever, and a bright aurora. *No pause; a cold ship earns one step* (default: the sheet's own cover is
   thermal, and a pause here would make half the planet a hideout). *Yes, it pauses:* every nightside biome becomes
   a refuge and the ice's price for it is the cold. *No cover at all:* the thermal signature matters only to the
   tunnelers.
2. **The kesshet, again?** He passed it on 2026-10-01. On 2026-11-18 he ruled that every biome wears on the hull in
   0.1.0 and that the answer should be found in the sources. The kesshet is the source's answer here. *Stay passed*
   (default: cold and the bitten edge carry it). *Bring it back in 0.2.0:* a rime-ring on the warm hull that raises
   the signature and must be scraped before launch, for a superconducting film; a new small system.

The cleanse proposal of 2026-11-17 asked him nothing, and one of its own readings is changed here by scope rather
than asked: it built the first version around a supplied refuge of forty colonists. The same warmth, cracks and
floor line are kept, and the refuge is the ship.
