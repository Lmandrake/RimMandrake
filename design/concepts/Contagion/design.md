# The Contagion: the design, seen from the ship

**Status:** the one design document for the Contagion biome (`RM_Contagion`, source `src/RimMandrake/Contagion/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the
older definition sheet, cast bible, limb sheet, the Rawshade design and the cleanse proposal as the place to read;
what happened to every idea in them is in `design/concepts/Contagion/rewrite_choices.md`. Nothing has been deleted
yet. The Contagion is one of the six biome mods HELD BY OWNER: this is a design document only and it launches
nothing.

**Second reader, 2026-11-18:** a second agent that did not write this page read the older Contagion files again and
repaired it. What the place does to the ship now rests on his shield rulings of 2026-09-02 and on what is built: the
Contagion is already marked as a fouled-air biome and the shared shield frame already wears an unscreened ship here.
The first read's goo on the hull was its own proposal and is withdrawn. Two creatures the first read had no line for
are in (the ogleknot and the Unblinking), the blistered bulloo is named, and two scenes now say plainly what the
build does not do yet. What changed and why is at the top of `rewrite_choices.md`. The locked sheet and tree
(`sheet.md`, `tree.json`) describe a colony that settles the valley; they are not edited here, and a later Designer
run reconciles them with this page.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/Contagion/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Contagion has a locked sheet (`sheet.md`, Design Version 0.1.0, with his
certified words of 2026-11-15 and 2026-11-16), a validated north star in the validation walk, and a cleanse proposal
of 2026-11-17 that cut further and was never applied. Where the two disagree this design follows the locked sheet,
because it carries his words, and says so in the choices page.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
mechanics review of 2026-10-22 or the cleanse census of 2026-11-17 found it in source; it does not mean it has
passed anything.

**What kind of place:** land. High valleys on dayside peaks under a permanent storm (checked against the sheet's own
header and §2: *"Mid-dayside regime... × the altitude-rain anomaly"*, median 32 °C, *"zero standing water"* as
tiles, red pools on the map). It is not a sea and the ship lands on it like any ground.

---

## What this place is

> *"A mutation engine under a red lid, where nothing is finished, including you. When the sky clears, run."*
> (owner, by card, 2026-10-20)

> *"A red valley on a scalded mountain, roofed by a thunderstorm that has never been known to stop. Under the cloud
> everything is wet, warm, and unfinished: trees half-way to being something else, animals with one design completed
> and two abandoned, ground that is itself an organism budding new attempts every hour. And then the cloud tears —
> and the sun comes through like a sterilizing lamp, and everything alive dives for cover, because here the clear
> sky is the killer."* (`the_contagion.md` §1)

This is the old war's bioweapon with the governor off. Everywhere else it is starved of water; here it has all it
wants, so it mutates faster than it can finish anything. *"Ferociously effective at infecting, hopeless at
holding."* The storm is its cage: the dayside sun sterilises whatever leaves the cloud, which is why the rivers
that rise here *"arrive in the lowlands clean."* *"The dry, bright edge is its quarantine; the desert does
not fight it, the desert just stops shielding it."*

His register for everything that lives here, typed 2026-09-27: *"bizarre one or two-word descriptions of the
strangeness of the thing. Eyegore. Fleshsop. Bloody Mess."* And one order: *"really gross fleshy flapping skin
things that fly."*

**Seen from the ship, this is the best hiding place on the dayside and the worst place to stand outside.** The sheet
said it before anyone thought of a ship: *"Knife country — pursuit with blasters means nothing under the Bloom;
refuge priced in biology."* The lid hides the hull; the fog ruins everybody's aim; and the price is paid in the
crew's own bodies, a little every day they work under it. The crew is from the desert. It has always trusted a
clear sky. Here the clear sky is what kills, and it is also the moment the hull can be seen.

His answers of 2026-11-10: the Burn and lasting mutation are the spine; clear skies allow *"one dash, at a cost"*;
and a trip for tissue that misses still brings *"other useful tissue"*. And two he typed on 2026-10-15. What
touches a body: *"Bloom time, stronger in burn, and contact."* What the Sunbeam does about it: *"Stops current
mutations. No protection if you get exposed again later."*

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid, then scouts with a spotter, a strike team, an ion cordon on the ship, a breaching
assault, and an orbital bombardment that cannot be fought. A loud crew halves every wait and a hidden one doubles
it.

**Cover from orbit here: partial, from the lid.** The storm is a roof over the whole valley. By the card of
2026-11-18 that is worth one step: the search runs one visibility band quieter than on open sand, while the lid is
closed. In a Burn the lid is open. A Burn the crew forces with a Cloud Repulsor is the crew opening its own roof.
Whether the search notices a Burn's few minutes is `UNSETTLED`; this design assumes the step is lost for exactly as
long as the sky is clear. All of it is owed work: the pursuit's built list of slowed biomes holds the Abyss alone.

**How long a stop lasts (the outer edge).** One step quieter stretches the open-ground five to eight days to about
seven to eleven: a first probe in the second week, the first real fight around the fourth, and the bombardment
somewhere between about **four and a half and seven weeks** for a crew that wins every fight before it. That is the
outer edge. The body sets a nearer one. Everyone who works under the Bloom is being changed, slowly, and *"it never
just upgrades you."* Nothing here is food. Most stops should be days: land, send a party for tissue, dash home in
the first Burn, leave.

A season is fifteen days. The Coalescence (a mass that grows *"during long Blooms"*) is 0.2.0 by his word, and it
is the only thing here that wants a long stay to be seen.

---

## The first minutes

The ship drops through a thunderstorm into red light. Under the lid the valley is wet, warm, fogged and never
still: *"budding, dissolving, diving."* Nothing outside the hatch is the colour or the shape of a plant. Eyebark
with eyes in it. Meatvine *"flexing slowly like something testing a limb it hasn't finished growing."* A carpet of
small grinding teeth. A pool of *"somebody that never happened"* creeping along the low ground, and things with
three good legs and a stump climbing out of it.

Overhead, at canopy height, drift translucent bags *"stuffed with mismatched eyes, all of them open, all of them
looking up."* They are the forecast.

Before the first hour is out the player should have seen: a sky that is plainly a sick red storm and not overcast,
and plants that read as grown flesh at ordinary zoom. (An Unfinished dying back into slime is 0.2.0, by his
first-version answer of 2026-11-19.)

## The first day

- **The hull is the refuge.** A refuge is whatever casts shade: a roof, a tree's cast shade, water. The ship is the
  biggest roof on the map. How far from it a work party goes is the whole risk of the stop.
- **The screen's yard.** By his card of 2026-11-20 a raised particulate screen keeps the Bloom off the crew inside
  its bubble: a safe yard by the ramp. Whether it also stops the Burn is not ruled; this design assumes not, since
  the Burn is light and the screen's rulings name particulates.
- **The tells.** Before a Burn the gawpsacks sink as one, the rattlegrope shakes, and red puffs rise. Always
  before, never after. The natives dive during the tells; the two armoured ones walk *out*.
- **The Burn.** The cloud tears and *"a white shaft of sterilizing sun"* hits the valley floor. Everyone within a
  dash of shade gets in during the tells. A party that went too far is caught out.
- **One dash.** A prepared crew member can cross between refuges in a Burn and live, hurt. Staying out is grave.
- **The fog cuts both ways.** Under the Bloom ranged fire is close to useless. In a Burn the fog lifts and guns
  work, for whoever is willing to stand in the light.
- **The water's edge.** The red pools are where the Bloodlurk waits: *"all forelimb and siphon, that holds still
  better than anything alive should."*
- **Nothing here feeds you.** No forage, no meat worth the name, no fish (*"the red water is the organism's
  excreted spore/toxin load"*). The larder is the ship's. Nor is the red a drink: by his thirst ruling of
  2026-10-17, red slime swallowed as a last resort *"is Contagion: full mutation exposure right away."*
- **The ground gives you away.** Gorestalk stands *"like stood-up entrails, faintly peristaltic"* and blocks the
  sight line; Toothmoss, *"a carpet of small grinding teeth"*, is slow and loud to cross. (Lashgrass that
  *"flinch[es] away from footsteps in a spreading wave; the ground telling everything where you are"* is the
  description; the flinch itself is unbuilt and sits in "later".)

## The first week

- **Touched.** A crew member who works out in the Bloom, or is caught by a Burn, or stands next to an Unfinished,
  shows an early touched state, with one message when the change begins. Walking back inside stops the dose, not a
  change already under way. Then the changes come from a mixed deck, harmful and mixed, capped, never the same one twice on a
  body.
- **The arrest.** Held on the patient, a Sunbeam's lens stops the change where it is. What has already changed
  stays, and the treatment leaves a burn. It works at the warning stage too, before anything has grown: that is
  the moment the warning is for. A crew member who goes out again starts again. (How a crew comes by a Sunbeam in 0.1.0: it buys one before it lands, `Answered on 2026-11-19` 1.)
- **The tissue run.** What the crew came for. Take a sample from a donor; carry it to a Bloody Mess; read the odds
  before committing; come back about four days later for what grew (the host dies making it: one batch each). A batch that misses the wanted part still brings matched,
  usable tissue: a kidney, a liver, a lung, a heart.
- **The Unfinished.** The goo buds them constantly, each *"half-made its own way"*; most are nuisances, *"some roll
  a monster"*; they live days and die into slime and mulch.
- **The dead leave marks.** A corpse here becomes skin, then a lasting print on the ground, and a Bloody Mess eats
  the rest. Nothing just disappears.
- **The Repulsor.** A powered Helix device that punches a hole in the cloud. It warns first that its Burn covers
  the whole map and everyone in the open, then clears the sky, and stops when the power does.
- **The zhool.** *"A gas-filled, veined bell trailing loose tendrils through the canopy"* whose red haze turns
  ordinary plants into flesh plants, in our biomes only. With it drifts the blistered bulloo, *"an unfortunate
  visitor"*: a clean gas-bag that blew in on the wind and caught what lives here.
- **Plants that burst.** The flesh plants do not grow old; they rupture (his card of 2026-10-17: *"Contagion
  rupture is their burst"*), and what comes out of a rupture can be a Bloody Mess or a zhool. Built in the shared
  growth machinery; nobody has yet counted how many hosts a wet week makes that way.
- **Wrecks and the ship's ears.** Eroded hull fragments lie on the peaks as on any ground. The ship's acoustic
  scanner has a reading for this biome too (his card of 2026-10-06: every biome of ours carries one): pods, wrecks
  and caves.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **They all looked down.** *On screen:* every eye-bag in the sky sinks at once; a stand of tentacles starts to
   rattle; and six hooded figures who were arguing over a carcass drop it and sprint for the ramp. *Why it lands:*
   the player has seconds and knows it.
2. **The sunbathers.** *On screen:* the valley empties in a Burn, and one armoured slab walks *out* into the
   killing light and starts eating what was too slow, *"already cooked."*
3. **Not safe under the tree either.** *On screen:* a crew member makes the canopy just in time, stands there
   breathing, and a jaw on a cord drops from the branches. *"Under the trees is safe from the sky and not safe."*
4. **The dash.** *On screen:* one Jawa, sent back for the sample case, crossing open ground in white light,
   smoking, making it.
5. **The tent that hunts.** *On screen:* a shadow the size of a tent crosses a straggler; *"its shadow crossing
   yours is the only warning before it drops and smothers."*
6. **Confetti.** *On screen:* a flock of loose wet skins slapping through the air and draping themselves over the
   ship to dry. Harmless. Nobody wants to be the one to peel them off.
7. **Something under the robe.** *On screen:* the message that a change has begun, and a crew whose whole custom is
   never to be seen uncovered working out what is now under one of the hoods.
8. **The line.** *On screen:* soaked sponge-things walking out in a loose row to meet whoever is coming up the
   valley and take the fire meant for the pool behind them. *"These are weapon systems, not sad zombies."*
9. **The harvest.** *On screen:* the pod opened, and what the crew gets is not the arm it wanted but a perfectly
   good liver. Somebody will buy a liver.
10. **The tick.** *On screen:* a dog-sized thing *"swollen tight with red water"* that *"sloshes audibly when it
    walks"*, and a native punctures it to drink.
11. **The rendering vat.** *On screen:* a house-sized slug crossing in front of the ramp, *"whose translucent belly
    shows the last three things it swallowed, at three stages of not existing any more."* One of them has legs the
    crew recognises from yesterday.
12. **It stings with it anyway.** *On screen:* a big segmented thing in the Eyebark *"whose raised tail ends not in
    a sting but in an eye"*, and the eye comes down like a sting.
13. **The stare.** *On screen:* a knot of eyeballs on stilt legs that *"stops dead to stare, every eye turning a
    different way at once"*; and, in the wet sand by the ramp, a lidded globe on a stub of red tissue that watches
    the crew work and sinks into the goo when the light comes. (The first is the ogleknot, built. The second is the
    Unblinking, his by his word of 2026-10-08, *"Of course it can get another creature. Just make one"*, designed
    and not built: 0.2.0.)
14. **The tree gave birth.** *On screen:* a swollen flesh plant splits, and what slides out is a pool that starts
    to creep.

**Two of these are in the text and not yet in the build.** The Danglemaw (3) ships as a slow, hard-hitting lurker
near Eyebark: the cast bible itself waived the true drop from the canopy for the first version. The Fleshsop (8)
fights as a pack that answers every hit; walking out in a line is its description, not yet its behaviour. Both
scenes are kept because they are the creature, and both are owed.

## When the Empire arrives

- **Blasters mean little under the Bloom.** Accuracy collapses for both sides; the fight is at arm's length, which
  is not where a stormtrooper wants it. Nor where a Jawa does.
- **The probe has to see.** It needs line of sight to the ship or a crew member, in red fog, in a valley full of
  things that eat what drifts.
- **Everything here eats them too.** The Bloodlurk at the pools, the Danglemaw under the trees, the Gorekite on
  *"anything man-sized caught in the open"*, the Fleshsop line that walks to meet *"whatever comes up the valley."*
  None of it is on the crew's side. It is on nobody's.
- **They are touched as well.** `UNMEASURED`: whether troopers on the map long enough begin to change.
- **The Burn is everyone's.** Troopers caught in the open take it like anyone. A siege camp is a camp in the open.
- **The crew can call it.** With a Repulsor the crew chooses when the Burn falls on the whole map: the fog lifts,
  the natives hide, the besiegers cook, and for those minutes the ship stands under an open sky.

## Who else attacks; who hates the Empire

- **The valley,** as above, impartially.
- **The Unfinished** that roll a monster.
- **The Ascendant Helix watch.** *"They love the genetic diversity of the out-of-control weapon's creativity;
  observation posts at the valley mouths."* They buy samples (his note of 2026-09-30: *"I like the helix offering to purchase strange scans of the
  beasts here. You assume the risks"*), and they are the only people here. Their own name for the place is "the
  Overdrive". Their caravan and
  contracts are 0.2.0 by his word. Whether they fight the Empire, sell to it, or report a stolen ship parked in
  their test ground is `UNSETTLED`.
- **The Rust Cathedral's enmity** toward this place is ideological and belongs to the campaign layer.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The changes. Each one stays.
- The larder: nothing here is food.
- A Burn that catches the party too far out, on a crew of six.
- A monster out of the goo.

**Stay, longer than the Empire would like:**
- The lid, worth a step of the search.
- Fog that blinds the probe and the spotter at ground level.
- A valley that attacks whatever walks up it.
- A Sunbeam, to stop a change before it costs a crew member; a Repulsor, to clear the map on the crew's own clock.

## What the crew takes away

- **Grown organs,** matched or sellable. The crew grew a spare heart in a pod on a mountain; that is a trade good
  anywhere.
- **Samples and prints** of things nobody has seen, for the Helix, who pay (0.2.0).
- **Mulch,** plain fertiliser by his card of 2026-10-16: *"the best fertilizer on Ash'karr"* in the sheet's words.
- **Gallium** off the Scorchpod's shell: *"electronics feedstock, Jawa tinkering gold."*
- **Water** (0.2.0): *"the only unlimited water on the dayside"*, red and lethal until the sun has had it.
- **Fuel:** emergency-slow only. This is the most biomass on the planet and none of it is fuel except by rendering
  it down the slow way. The only people who might sell any are the Helix curators, in 0.2.0; whether they stock
  fuel is `UNSETTLED`.
- **The deck part: a Cloud Repulsor on a hardpoint.** This biome's entry on the list of what each place gives the
  ship (`BIOME_SHIP_CONTRIBUTIONS_1`; `RM_CloudRepulsorShip`, built, untested). Here it forces the Burn. Anywhere
  else the ship lands it *"holds the sky clear"*: no rain, no fog, for as long as it has power. The ground device
  can arrive as a quest reward; the hardpoint is stocked by the curators (0.2.0).
- **Whatever changed.** It leaves with the crew. *"Including you."*

## What the place does to the ship

The first read said no source covers this. Two do, and one of them is built.

- **His ruling, 2026-09-02** (the shield sheet, `design/Jawa/proposals/ship_shields_deep_design.md`): *"The
  environment is hostile and immediately goes to work on the ship. The ship will know what's visibly dangerous and
  will advise course of action, but no more than that. Its hull is thick and can take a lot of damage in most
  situations, so no environment is immediately lethal."* The proposal he was ruling on names this place by its old
  name, among the maps *"guarded by physics"*: *"the ocular forest's spore/toxin load."* And his answer to what
  stops it: *"Light kinetic deflectors handle wind, ash, vapor, bio contamination, spores, smoke, sand, and rain
  damage completely as well as repels small animals."*
- **What is built.** The Contagion is marked a fouled-air biome (a patch in the Warscar mod marks the Wastes, the
  Cauldron and the Contagion; it ships with that mod because the marker's code lives there). The shared frame in
  `src/RimUtinni/ShipShields/` reads that mark as its particulate hazard. With no shield in particulate mode, the
  things standing at the ship wear a little at a time, a letter warns after about six hours that the fouling is
  getting worse, and the wear then doubles its pace. A powered shield switched to its particulate mode stops all of
  it. The ship says so on landing and does not refuse to land.
- **The screen also keeps the Bloom off the crew inside its bubble** (his card of 2026-11-20, `Answered` 2). That
  is an owed build line, above under Scope.
- **So the wear here is the air itself:** spore, red rain and whatever the rain carries, working into the gear
  parked at the ramp. Nothing in it is this page's proposal.
- **The hull is otherwise the answer, not the victim:** it is the roof, and the biggest one on the map.
- **Not carried forward.** The first read proposed goo creeping onto the hull and a hardpoint Repulsor as *"the
  hull's own cleaning lamp"*. Neither is in any source. They are withdrawn in favour of the sourced wear and stay
  in the choices page as rows.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Under the standing Bloom the sky is a red storm lid, not grey overcast. | A fresh map at rest. | An ordinary overcast tint fails. |
| Gawpsacks sink, rattlegrope shakes and red puffs rise before the Burn, never after. | A natural Burn, watched from before the tells. | A Burn with no tells first fails, whatever follows. |
| Crew within one dash of shade get in during the tells; a far party is caught out. | Two parties at two distances from the ship. | The far party pays. |
| A prepared crew member crosses between refuges in a Burn and lives, hurt; one who stays out is in grave trouble. | One dash, and one pawn left standing in it. | Unhurt fails; dead on a normal dash fails. |
| A roof, a tree's cast shade and water each count as refuge. | One pawn in each through a Burn, one in the open. | The Burn uses the shared shade, with no test of its own. |
| Under the Bloom, a crew member inside a raised particulate screen's bubble is not touched; one outside it is. | Two pawns in the open under the Bloom, one inside the bubble and one beyond it; then the screen lowered. | The pawn inside is touched once the screen is down. |
| UV-shy natives are hurt by the Burn and dive during the tells; Scaldhide and Crispling are not hurt and come out. | A mixed group through a Burn. | A native that dives only after being burned fails. |
| No native runs from the sun under the Bloom; they do when the Burn clears the sky. | The same animals under Bloom and in a Burn. | |
| A worker out in the Bloom shows an early touched state and one message when change begins. | A worker left outdoors, one kept in. | |
| Changes come from a mixed deck, each with a real cost, capped, never twice on one body. | A run to the cap. | A change that is only a label, or only a gain, fails: *"it never just upgrades you."* |
| A Sunbeam held on the patient stops the change, keeps what has changed and leaves a burn. | A patient at warning stage and one already changed. | Later exposure can start it again. |
| The plants read as grown flesh; zhool haze turns plants, in our biomes only. | A fresh map; a zhool beside ordinary plants. | A recoloured forest fails. |
| The natives are there in numbers, each plainly its own creature, each with the death or trick its description promises. | A walk of the roster. | No number is a promise. The flyers' flight is read from state, never live-tested without him. |
| A save reloaded mid-way, and the main actions done in another order, give the same Burn, body and batch. | The walk. | |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The Repulsor warns that its Burn covers the whole map, clears the sky, and stops without power. | Power it; read the warning; cut the power. | A cleared patch is wrong: the Burn is map-wide. |
| Each budded Unfinished is half-made its own way and dies into slime and mulch. | A Bloody Mess over several buddings. | Two identical in a row is suspect; one that vanishes with no sign fails. |
| A gestation shows its odds before the sample is spent and, when the wanted part misses, still brings matched tissue. | A run that hits and a run that misses. | A cancelled run does not spend the sample. |
| A corpse becomes skin, then a lasting print, and a Bloody Mess eats the rest. | A death left alone. | |

Settings: one switch per major feature, defaults as shipped, each switch stops only its own feature (standing rule,
every mod). The three 0.2.0 features he named ship switched off; today they ship on, and that is owed work.

## Shared machinery

**Featured here** (the Contagion is where each is vital and should be proven):
- **Weather that warns through the animals, then harms** (the sky clock, the tells, the Dive:
  `RM_MapComponent_ContagionSky`, `RM_ContagionTellRender`).
- **Shade as refuge from something other than heat** (the Burn reads the shared shade geometry; his ruling of
  2026-10-19: *"a pure function of geometry, NOT biome"*). Water as cover is a term the shared geometry still
  lacks.
- **Bodies that change and stay changed** (`RM_ContagionTouched`), and a tool that arrests without undoing.
- **Short-lived random creatures budded by terrain** (`CompSpawnerUnfinished`, `CompRandomizeUnfinished`).
- **Growing tissue in a host** (the genome loop, Wombpod hosts).
- **Remains that tell the story** (Bodyprints).

**Merely active here:** fog that ruins aim (the same shape as the Blue Desert's ice fog and any blinding fog); real
flight for its flyers; creature tracks and ordinary departures (`CreatureBehaviors`); the one sun from geometry,
which under the lid is quiet and in a Burn is not the Burn; wreck salvage on the peaks; the Empire's search and the
visibility dial; plain fertiliser.

## Scope

Every feature is in one bucket.

**The one signature (his first-version answer of 2026-11-19): the Burn under the Bloom.** Under the standing red lid
the Bloom touches and changes whoever stays out; then the tells come, the cloud tears, and everyone runs for shade,
a roof, a tree's shade or water; a Sunbeam arrests unwanted change. *Why a normal stop is sure to see it:* the lid
stands over every map, and the tells and a Burn come on the first day; the ship is the biggest refuge on the map.
His experience line: *"A mutation engine under a red lid, where nothing is finished, including you. When the sky
clears, run."* *Runner-up:* the biological laboratory (the Unfinished, the genome batch, bodyprints); it lost because
it is a second progression a stop can skip.

**0.1.0, the stop** (the locked sheet's version, read for a ship)
- The Bloom as a red lid; the Burn; the tells; the Dive; the armoured natives coming out. (built; the Dive and the
  natives' Burn damage are owed or were failing)
- Refuge as shared shade; one dash at a cost. (built in part; water as cover is owed)
- A raised particulate screen keeps the Bloom off crew inside its bubble (his card of 2026-11-20). (owed build: the
  touched dose reads only what is overhead and never asks about a shield, so the built behaviour does not match.
  No build ticket is filed while the mod is held.)
- The touched state, the mixed deck, the Sunbeam arrest. (built)
- Flesh flora; zhool haze; the grotesque cast with each creature's promised trick; the new smaller Zhool'Iza.
  (built; the Zhool'Iza is owed)
- Mulch as plain fertiliser.
- The fouled air wearing an unscreened ship, stopped by a particulate-mode shield. (built in the shared frame;
  never proven on this biome)
- The ogleknot; the blistered bulloo. (built)

**0.2.0, the stop with company** (the first three by his word of 2026-11-16)
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The ground Repulsor with its warning. (built)
- The Unfinished. The genome loop's ordinary batch with odds shown first. (built; the odds display is owed)
- Bodyprints by phases. (owed, by his card of 2026-10-16)
*Already here before that answer:*
- The Coalescence, all of it.
- The Grown Limbs, all of it: Pillar Arm, Lash, Eyeburst, Caudal Spring, Bellows.
- Helix trade: draftprints, contracts, the curators' caravan.
- The Repulsor's ship hardpoint (the curators stock it). (built, untested)
- The Rawshade: a creature that stands still in a Burn so that small things shelter under it, *"Then the skirt
  comes down."* (designed 2026-11-02)
- Red water made drinkable by a day in the sun. Red sap as repellent and sealant. (items exist; uses do not)
- The Unblinking: a watcher the goo budded and never finished. (designed 2026-10-08 on his word; unbuilt)
- The Sunbeam's extra harm to natives, if it is not already wanted in 0.1.0. (built)

**Later (a crew that stays, a colony, or the campaign)**
- The Ashfall Research Base and its one line of plot; Helix observation posts as places.
- Spore blooms downwind as this biome's export event; the infection front advancing in Blooms and burned back in
  Burns.
- A whole season of the valley's ecology holding together.
- Steering a gestation toward a wanted part.
- Lashgrass that flinches from footsteps; Eyebark whose eyes follow; the Halfmade Tree's front moving.
- The peaks drawn on the world map as the planet's rain makers (his words of 2026-10-24: *"Contagion-stained
  mountains (the only place we use Contagion) is particularly important, and to draw those as wet/water
  generators"*; by card, a look only: *"they weep"*).
- The three rites (the Sunning, the Unfinished Laid Down, the Kept Mistake); they live in the rites mod.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Silence as the alarm; the god mid-birth (cut at the sitting of 2026-09-27).
- Mulch that infects a field unless sunned (his card: plain fertiliser only).
- Any heat or sun particular to this biome (2026-10-19). The Burn's own exact-cell tree test.
- A touched outcome that is a net gain (the sheet's ban, his ruling).
- Bars that pin yields, creature numbers or art variant counts (2026-11-16).
- The donor cast, the exotic draft names, "Eyegore", the Fleshsop that *"needs to be loved to live another day"*.
- Edible forage. Any native that persists under open sky. Fish.
- A spore membrane for the ship (cut by him 2026-09-02: *"spores aren't magical, just particulates."*). It stays
  down by his answer of 2026-11-19 on declined ship ideas.
- Goo creeping onto the hull, and the Repulsor as a hull-cleaning lamp (the first read's own proposals; withdrawn).
- The seven other ideas of the GPT consult of 2026-09-30: he picked three by card (Draftprints, the Dive,
  Bodyprints) and *"GPT's seven other ideas were not picked, so they are out."* The record does not name them.
- The Shambles here: he moved it to the Rot on 2026-10-05 (*"this belongs in the Rot, not here."*).
- Eye grass: purged, *"I don't want new versions of these silly plants."* The donor's own ocular giant, never
  admitted.
- The planet-scoring worker and its biome-rarity slider (his ruling of 2026-08-15 and 2026-08-18: no worldgen, ever; no setting that could roll a second world).
- **Recommended for dropping, not yet his:** the duplicate seed-fist fertiliser, the unused donor plants.

## NEEDS HIM

None open. Every entry is answered (next section).

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. **[other] Is the built way to a Sunbeam enough for a ship on the run?** As built: a crew that wants one buys it
   before it lands (the design's default). *Delegated call.*
4. **[cover] Does a Burn show the ship to orbit?** Yes, for as long as the sky is clear (the design's default).
   *Delegated call.*
5. **[other] Do the Helix sell out a stolen ship?** Not decided in the biome. The campaign layer decides. Here they
   trade and say nothing (the design's default). *Delegated call.*
6. **[scope] The Rawshade.** Safe for a Jawa as for anyone, until a Jawa's body size is measured against the 0.7 line
   (`UNMEASURED` today). *Delegated call.*
7. **[scope] Bodyprints in 0.1.0.** *His ruling:* his card of 2026-10-16: *"Dive and Bodyprints stay in THIS sprint"*.
   In 0.1.0; the first-version size question can still move it.
8. **[locked-tree] The locked sheet and tree describe a colony that settles the valley** *His ruling:* his word of
   2026-11-18, *"Let's rewrite them all and let git be provenance."* The tree is not edited now; a Designer run
   reconciles it when the hold lifts.

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

3. **[hull] The spore membrane.** *His card of 2026-11-19 (declined ship ideas):* it stays turned down, as he cut it
   on 2026-09-02. He can bring it back by name.

**Answered by his card of 2026-11-20** (item `RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED`; the
enact item is `RIMMANDRAKE_ENACT_SIGNATURE_PICKS_INTO_DESIGNS_SLIME_KEEPS_FILM`). Each keeps its number.

2. **[hull] Does a raised particulate screen keep the Bloom off the crew standing inside its bubble?** It was left
   open on 2026-11-19: *"the ship and a bubble around it"* is the shield design's text, not his words, and a Yes
   changes a built default. *His card of 2026-11-20, about 6:00 AM PST:* **Yes: inside the bubble too**:
   *"Why: it makes the screen worth raising and gives the crew a safe yard by the ramp. Buys: the trip away from the
   ship becomes the whole risk, a clear rule. Costs: a code change to a built default, and anyone who stays by the ramp
   is never in danger."*
   **This changes the design's default.** Was: *No, the screen protects the ship and its gear* (as built). Owed build:
   the touched dose must ask whether the pawn stands inside a raised particulate screen's bubble; today it reads only
   what is overhead. No build ticket is filed while the Contagion is held.
