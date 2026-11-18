# The Cracked Lands: the design, seen from the ship

**Status:** the one design document for the Cracked Lands biome (`RM_FloodedCanyon`, source
`src/RimMandrake/CrackedLands/`), rewritten 2026-11-18 on the owner's instruction to see every biome "through the
lens of Utinni". It replaces the older definition sheet, cast bible, review, flora pitch and the cleanse proposal as
the place to read; what happened to every idea in them is in `design/concepts/CrackedLands/rewrite_choices.md`.
Nothing has been deleted yet. The Cracked Lands are not on the owner's hold list, but only the Pyrelands is advancing
as a biome mod: this is a design document only and it launches nothing.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/CrackedLands/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Cracked Lands have no locked sheet or tree; their only pipeline material is
the cleanse proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
mechanics review of 2026-10-22 or the cleanse census of 2026-11-17 found it in source; it does not mean it has
passed anything.

**What kind of place:** land. Dry canyon country on the outer dayside (checked against the sheet's own header and
§2: *"Outer dayside (arc 17–116, sun ~21°) × the flash-flood anomaly"*, median 27 °C, rain median 0). It is not a
sea. Water comes to it, rarely, and leaves.

---

## What this place is

> *"Most days it is a quiet canyon, and one day it is a river that kills. Listen for the chimes and farm the mud it
> leaves."* (owner, by card, 2026-10-20)

> *"A thin line of green in the shade, beside the razor's edge of the open sun."* (`the_cracked_lands.md` §9)

Canyon country below the only dayside mountains that rain: mesas, hoodoos, slot canyons, clay pans split into
polygons. *"Most of the time it is dry, cracked, shadowed and still."* Then the water comes down: *"violent downward
floods of hot, crud-laden water that are fertilizer, life, death, disaster and damage all rolled into one"* (owner).
It leaves soil in the shade, the only real soil on the dryland ladder, and then *"the water hides"* in the cracks.
The animals here are divided *"by when it is alive"*: the Sealed, who sleep through the dry years under the clay;
the Spenders, who live a whole life in the flood-weeks; the Patient, who wait in the shade line. *"You see nothing
all day, and are watched the whole time."*

**Seen from the ship, this is the one biome the crew already knows, from the road.** The sheet wrote the Jawa into
it before there was a ship: *"The Jawa — road traffic with a rhythm: a flood is a salvage strike. The wall tears
open ruins, washes buried tech from the banks, re-deals the board; crawler crews follow flood-news the way
prospectors follow gold. The best scavenging on the dayside, for exactly as long as the mud is fresh."* They have
always arrived after, by crawler, with everyone else. Now they have a ship and can be standing in the canyon when
it happens. Nobody has told them that is not an improvement.

His answers of 2026-11-10 fix the three things that matter: the river *"can kill"*, by drowning and by impact,
*"death not guaranteed but damage that may be lethal is"*; the warning saves people, and *"you should never rely
on a valley floor being safe for slow transport, it's a gamble"*; and the mud is *"wetted and highly fertile but
once it's dry, it's over. And in Utinni, there's no farming anyway, so don't spend too much time implementing this
deeply."* So for this crew the mud is not a field. It is a yard sale with a closing time.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing on open ground, then scouts with a spotter, a strike
team, an ion cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. A loud crew
halves every wait and a hidden one doubles it.

**Cover from orbit here: none from the sky, and one step for a ship down in the cut.** The sky is *"clear, hot,
still"*: no canopy, no steam, no fog. What the place has is depth. The canyons are *"cut deep enough to shade
themselves"*, and a hull on the canyon floor sits in that shade under the walls. This design reads that as the
card's one step, on the floor only, and nothing on the benches or the flats. It is this design's reading of the
card of 2026-11-18, which names canopy, steam and fog and not rock; see `NEEDS HIM`. It makes the landing the
choice the card asked for: the floor hides the ship and is where the flood comes; the bench is safe from the water
and in plain view. All of it is owed work.

**How long a stop lasts (the outer edge).** On a bench, in the open: a first probe in five to eight days and the
whole ladder run in about **three to five weeks**. On the floor: the Empire's clock stretches by a step, and the
river's clock becomes the edge instead. The built flood clock defaults to one flood every twenty days, and a
storm on the peaks can pull the next one forward. So the outer edge of a floor stop is **the next flood**, which
the crew does not get to schedule. Most stops should be a few days on the fresh mud.

A flood must be something a stop can meet. On a twenty-day default most short visits would see only the stillness.
He already ruled the cure for a first visit: the campaign arranges a witnessed flood at least once. Beyond that the
interval is tuning, and this design asks only that a crew which stays into its second week has heard the chimes.

A season is fifteen days. Nothing in 0.1.0 needs one.

---

## The first minutes

From the air: white flats, and cut into them a maze of blue shadow. *"The hardest contrast on the planet —
slot-canyon shadow against white-hot flats; the green only ever in the blue shade."* The player picks where to put
the ship down, and it is the most important decision of the stop: high bench or canyon floor.

On the ground it is silent and nothing moves. The pans are cracked into polygons. Along the foot of the walls, in
the shade and nowhere else, runs a thin line of living colour. The walls carry old stain lines well above head
height, and above the stains there are ledges cut by somebody, with steps.

One pan near the landing site is *"slightly out of pattern — the polygons a touch too regular, the mounding a
touch too high."*

Before the first hour is out the player should have seen: that plants grow only in shade; the high-water marks; the
refuge ledges and a way up to them; and, if a flood was recent, things half-buried in the bed.

## The first day

- **Shade decides.** The open sun is the ordinary killer, by the planet's one sun and nothing special to this
  biome. Work goes where the walls throw shade.
- **The bed is where everything is.** Wrecks the last flood half-buried, scatter along the flood line, the
  shade-line plants worth gathering, the fossils in the freshly cut wall. All of it is on the floor.
- **The ledges.** Refuges cut into the cliff above the stain line, reachable from the bed. A roof on the floor is
  shade and nothing more: *"a roof shades but does not elevate."*
- **The pans are asleep.** *"Walk them and you walk on sleeping animals."* The Sealed lie under the clay in wax-lined
  burrows. They do nothing. Yet.
- **The voice.** Long low calls down the crack network: tarruq, each answering the next. *"Wind, then tarruq, then
  wind."*
- **The patient ones.** Ambushers at the seep and the shade line, and a plant with fangs.

## The first week

- **The warning.** It comes in a known order. The wind in the slots changes. The flats begin to *tick* as the
  sleepers wake under the clay. The tarruq go silent. Then the chimes: *"their tones ring not from wind but the
  tugs of water coursing down... far overhead"*, far, then nearer, then near. Then the roar.
- **The river.** It fills the open canyon bed from wall to wall. Anyone still on the floor is hit and may drown.
  Prompt climbing gets people clear. Slow freight is a gamble, and so is one more trip to the wreck.
- **The ship.** A hull on the floor is in the river. It can take it, or it can launch on the chimes with whatever
  is aboard.
- **The mud.** When the water drops the wetted bed is soft, dark and briefly fertile. Plants in it grow while the
  player watches. Irqit hatch as *"a sudden carpet of small frantic life between the roar and the dry."* A fresh
  line of salvage lies where the water left it, and half-buried hulls and speeders that were not there before.
- **The pan gets up.** The muttavaq, a giant that has slept for years under a pan the crew took for ground, wakes
  when the water reaches it, wades the wet floor feeding, and at the dry digs in wherever it stands and seals. It
  is the same animal the whole time and can be inspected as one.
- **The fliers come to feed** and leave again. They really fly. Nothing nests here.
- **The dry.** Within days the mud stiffens, the carpet dies, the fertility ends, and it is a quiet canyon again.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The ground is ticking.** *On screen:* a crew spread over a flat, mid-salvage, and the pan under them starts
   to tick and twitch. They look at their feet. *Why it lands:* it is the first warning, and it is the ground.
2. **It went quiet.** *On screen:* the calls that have run under every hour of the stop cut off together. A
   moment later, far up the canyon, the first chime.
3. **One more trip.** *On screen:* the near chime is ringing and one Jawa is still dragging a power cell toward
   the ledge. The water arrives on screen before the Jawa arrives at the ledge. Nothing in the game is more Jawa
   than this, and it can kill.
4. **The river.** *On screen:* a dry canyon becomes a brown river from wall to wall in the time it takes to read
   the alert. Whatever was stacked on the bed is in it.
5. **The hill woke up.** *On screen:* the pan the crew stockpiled on heaves, cracks along lines *"radiating from a
   center the way dried clay never does"*, and stands up as an animal the size of a building, shedding their
   cargo.
6. **The carpet.** *On screen:* every wetted cell alive with palm-sized things at once, and the sky filling with
   fliers come to eat them.
7. **It grew.** *On screen:* a plant in the wet mud getting visibly larger. The owner's words for the feeling:
   *"OMG, what's going to happen?"*
8. **Launch on the chimes.** *On screen:* the ship lifting off the canyon floor with the roar already audible and
   half the salvage still on the bed.
9. **The yard sale.** *On screen:* the crew down on fresh mud among hulls the flood just dealt out, working fast,
   with the stain line on the wall behind them higher than the ship.

## When the Empire arrives

The sheet already says how the Empire feels about this country: *"convoys must thread the slots and every officer
hates it... patrols through the best ambush terrain on the planet, where the locals hold the high benches."*

- **Walls.** *"Fortification — canyon walls; the best natural defense on the dayside."* A crew on a ledge above a
  slot has the only good position on the map.
- **The floor is the approach.** Whoever comes on foot comes up the bed. A siege camp is built where there is
  room, and the room is on the floor.
- **The river is impartial.** If the chimes ring during a siege, the besiegers are standing where the water goes.
  Troopers are hit and drowned by the same rule as anyone. The crew has heard chimes before and they have not.
- **The pans.** A camp pitched on a sleeping muttavaq is pitched on a sleeping muttavaq.
- **In the open they see everything.** A ship on a bench has no cover at all; the probe needs only to look.

## Who else attacks; who hates the Empire

- **The road.** The Cracked Lands are *"on the way"*, and everybody on the way is somebody: *"Junker caravans come
  through to sell things — or to threaten people; envoys from the Hutts; Jawa; and, rarely, only when desperate,
  the deep desert tribes."* The Hutts want this particular ship back. The Blackstar Company's hunts *"end
  here."* The tribes make *"the short sharp raid on the road itself."* All of them belong to the campaign layer;
  this biome supplies the ground they meet on.
- **Rival salvage crews (0.2.0).** A flood is everybody's salvage strike. Other crews stake claims on the same
  mud.
- **The Moisture Farmers** are the only residents: high-bench homesteads, never the floor. Whether they shelter a
  hunted crew, sell to it, or sell it out is `UNSETTLED`.
- **The ambushers** of the shade line; the uttaqar, a rock troll under the walls, if provoked.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The flood, for a ship on the floor.
- The dry: once the mud has set there is nothing left to take.
- The open sun and a plain view of the sky, for a ship on a bench.
- The road finding out who is parked here.

**Stay, longer than the Empire would like:**
- The cut's shade over a hull on the floor.
- Ledges and walls to fight from.
- Road traffic to buy from.
- A river that sometimes clears the canyon of everyone who does not know the chimes.

## What the crew takes away

- **Salvage,** fresh from the flood line: components, slag, the half-buried hulls and speeders.
- **Crack-wax,** the sleepers' burrow lining, the Farmers' waterproofing.
- **The bloom harvest,** whatever of it can be gathered before the dry; ink-bladder for the pot, rope reed for
  cloth.
- **Fossils (0.2.0):** *"the ship's take is fossil cargo"*, cut from seams the flood exposes.
- **The Swale and the survey (0.2.0):** a seep-canal technique *"shaped for transient gravship players: the
  technique travels with the ship"*, and a survey of newly found hidden water, *"an exceptionally valuable thing
  to sell."*
- **Fuel:** emergency-slow only from the land itself. But this is the place to *buy* it: the roads run through
  here and the caravans sell. That is campaign-layer traffic, not this biome's own content, and none of it is
  built into the biome.
- **A sale.** The sheet's own line: the Rot's soil *"hauled by ship to the farms is how a Jawa makes early
  money."* The Cracked Lands are where cargo from other stops turns into credit.

## What the place does to the ship

- **The flood.** A hull on the canyon floor is hit by the wall of water like everything else there. The sources
  name the damage in general (*"disaster and damage"*; *"the farm that was built one meter too low"*) and nothing
  ship-specific is built. The answers are the two the Farmers use, and one they do not have: park above the stain
  line; build a wall *"facing the sun and the flood"* upstream of the hull; or launch on the chimes.
- **Sandstorms** *"across the flats and the pans"* reach a ship on a bench. No source says they wear a hull, and
  none is promised here.
- **A ship-mounted chime was rejected by him** (2026-09-28: chimes work *"by being strung on lines up the canyons,
  not magic"*). The ship hears the canyon's chimes like everyone else.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Cracked pans, stained cut walls, a dry sky, and living colour only in the shade. | A fresh map at ordinary zoom. | A plant on open sun-flat fails. |
| Refuge ledges above the stain line that people on the bed can reach. | A party on the floor sent up at the first chime. | A ledge with no route to it is scenery. |
| The warning comes in order: wind, ticking flats, the tarruq falling silent, chimes far to near, the roar. | A natural flood from before the first sign. | Water before chimes fails. With no tarruq on the map the chimes still warn. |
| The river fills the open bed from wall to wall. | A canyon with a wide and a narrow reach. | A patch of water in the middle of a dry bed fails. |
| Being caught means real harm, from impact and from drowning, that can kill and does not always. | Pawns left on the floor, several runs. | Never hurt fails; always dead fails. |
| Prompt climbing gets people clear; slow freight is a gamble. | Two parties at the first chime: one drops everything, one finishes a haul. | A roofed room on the floor does not save anyone. |
| A ship on the floor is in the river and can launch on the chimes. | The same landing ridden out and launched from. | A ship on a bench is untouched. |
| After the water, the wetted bed is briefly fertile in the shade and then is not. | The bed followed from recede to dry. | A second flood does not stack it richer; unwetted cells gain nothing. |
| Plants in wet mud visibly grow. | A soaked plant watched. | The same plant on dry ground. |
| Irqit hatch as a carpet on wetted cells, live once, and die at the dry; fliers come to feed and really fly. | One recede through to the dry. | A flood elsewhere does not extend this carpet. A carried irqit still dies on time, visibly. |
| A sleeping pan is one inspectable animal that wakes unharmed in the flood, feeds, and seals alive at the dry. | A muttavaq pan through a full cycle; save and reload asleep and awake. | It is never two animals and never vanishes. |
| The flood leaves salvage on its line and half-buried wrecks in the bed. | Two floods, the bed compared. | The second flood deals a different hand. |

Settings: one switch per major feature, defaults as shipped, everything off leaves a dry shaded canyon with
ordinary animals (standing rule, every mod). Flight is read from state, never watched unattended (standing rule).

## Shared machinery

**Featured here** (the Cracked Lands are where each is vital and should be proven):
- **A flood on a clock, with a warning sequence** (`RM_MapComponent_CanyonFlood`, the chime sounds, the roar).
- **Refuge by height** (`RM_MercyLedges`, `RM_LedgeRefuge`): the Contagion's refuge is shade; this one is up.
- **Animals that sleep in the terrain** (`RM_CompPanSleeper`).
- **Plants that visibly grow when soaked** (the `ExplosiveGrowth` soak call). His words: *"a WORLD mechanic, born
  here."* The Greentide features its pressure; this is where it was first asked for.
- **Salvage dealt out by an event** (`RM_MapComponent_RecedeAftermath`, the canyon wrecks, on `Wreckage`).

**Merely active here:** shade as geometry, which is this biome's whole map (the one sun; shade-bound plants); water
and canals (`FlowWorks`: the Swale is an ordinary buildable there); creature calls and tracks; real flight; bone
from butchery; the acoustic sounder; the passage of giants; the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket.

**0.1.0, the stop**
- The land: pans, stained walls, shade-bound flora, banks with refuge ledges. (built)
- The flood: wall to wall, with chimes and roar. (built as a capped patch today; wall to wall is owed)
- The herald sequence before the chimes: wind, ticking, the tarruq's hush. (built)
- Harm that can kill, by impact and drowning. (built as one light hit today; owed)
- A hull on the floor in the river; launching on the chimes. (owed)
- The wet aftermath: brief fertility in shade, visible growth, the irqit carpet, a feeding flier in the free
  roster. (built in part; the soil is permanent today, and the free flier is new)
- The muttavaq's sleep, waking and sealing. The tarruq's calls. The rest of the cast as ordinary animals. (built)
- Salvage on the flood line and half-buried wrecks. (built)
- Ordinary gathering: crack-wax, ink-bladder, rope reed and the other shade plants. (built)

**0.2.0, the stop with company**
- Rival salvage crews staking claims on the same mud. (designed; partly built)
- Fossil seams the flood re-cuts, and what comes out of them. (built)
- The crack-wax suit, for working flooded ground. (built; its protection is missing)
- Hidden water: the veqma's blush, the survey to sell or dig, the cistern; the Swale learned here and carried
  with the ship. (the Swale is built; the rest is not)
- The uttaqar's wounds turning to stone, and its disguise as rock. The muttavaq dredging a trail through the
  floor. (built in part)
- The witnessed-flood invitation. (designed; campaign layer)
- The ship's acoustic sounder readings here. (built)

**Later (a crew that stays, a colony, or the campaign)**
- Farming the mud in any depth (his word: not in Utinni).
- The bloom market; the Hutt toll gate; Moisture Farmer homesteads, roads and who is on them.
- Deep-stratum unique fossils; prying talus; the zennaq's filament and the luqqim's light.
- Special passages of giants.
- The two rites (the Chime Vigil, the Mud Claim); they live in the rites mod.
- A whole canyon season holding together.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- A ship-mounted chime; a wax tank (both rejected 2026-09-28).
- The earlier ceiling on flood injury (superseded by his answer: the river can kill).
- Any structure on the canyon bottom in a settlement or template: *"NEVER the bottom. NEVER."*
- Fossil display mounts, lightning drawn to zennaq, dust that drifts backward, fliers arriving on a timer (retired
  before this pass).
- The vanilla zoo and flora; rain in the canyons; flier nests.
- The planet-placement worker (worldgen is out in every version).
- **Recommended for dropping, not yet his:** mood carvings on the ledges, the newer decorative fossil case, metal
  and stone harvested from lithops.

## NEEDS HIM

1. **Does a deep cut count as cover from orbit?** The card names canopy, steam and fog. *Yes, one step, on the
   canyon floor only* (default here): the landing becomes a real choice between hidden-and-floodable and
   safe-and-seen. *No:* the Cracked Lands have no cover anywhere, every stop is on the open clock, and the floor is
   simply the wrong place to park.
2. **What does the flood do to a hull?** Nothing ship-specific is built. *Damage like any structure on the bed, and
   the ship may launch on the chimes* (default). *The ship is grounded while the water is up:* closer to a trap
   than the ladder allows. *The hull is proof against it and only what is outside is lost.*
3. **Do the Farmers and the road shelter a hunted ship or sell it?** Campaign layer; it decides whether this is the
   friendly stop or the dangerous one. *Not decided here.*
