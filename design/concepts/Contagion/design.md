# The Contagion: the design, seen from the ship

**Status:** the one design document for the Contagion biome (`RM_Contagion`, source `src/RimMandrake/Contagion/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the
older definition sheet, cast bible, limb sheet, the Rawshade design and the cleanse proposal as the place to read;
what happened to every idea in them is in `design/concepts/Contagion/rewrite_choices.md`. Nothing has been deleted
yet. The Contagion is one of the six biome mods HELD BY OWNER: this is a design document only and it launches
nothing.

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
that rise here *"arrive in the lowlands clean."*

His register for everything that lives here, typed 2026-09-27: *"bizarre one or two-word descriptions of the
strangeness of the thing. Eyegore. Fleshsop. Bloody Mess."* And one order: *"really gross fleshy flapping skin
things that fly."*

**Seen from the ship, this is the best hiding place on the dayside and the worst place to stand outside.** The sheet
said it before anyone thought of a ship: *"Knife country — pursuit with blasters means nothing under the Bloom;
refuge priced in biology."* The lid hides the hull; the fog ruins everybody's aim; and the price is paid in the
crew's own bodies, a little every day they work under it. The crew is from the desert. It has always trusted a
clear sky. Here the clear sky is what kills, and it is also the moment the hull can be seen.

His answers of 2026-11-10: the Burn and lasting mutation are the spine; clear skies allow *"one dash, at a cost"*;
and a trip for tissue that misses still brings *"other useful tissue"*.

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

Before the first hour is out the player should have seen: a sky that is plainly a sick red storm and not overcast;
plants that read as grown flesh at ordinary zoom; and at least one Unfinished, half-made its own way, die back into
slime.

## The first day

- **The hull is the refuge.** A refuge is whatever casts shade: a roof, a tree's cast shade, water. The ship is the
  biggest roof on the map. How far from it a work party goes is the whole risk of the stop.
- **The tells.** Before a Burn the gawpsacks sink as one, the rattlegrope shakes, and red puffs rise. Always
  before, never after. The natives dive during the tells; the two armoured ones walk *out*.
- **The Burn.** The cloud tears and *"a white shaft of sterilizing sun"* hits the valley floor. Everyone within a
  dash of shade gets in during the tells. A party that went too far is caught out.
- **One dash.** A prepared crew member can cross between refuges in a Burn and live, hurt. Staying out is grave.
- **The fog cuts both ways.** Under the Bloom ranged fire is close to useless. In a Burn the fog lifts and guns
  work, for whoever is willing to stand in the light.
- **The water's edge.** The red pools are where the Bloodlurk waits: *"all forelimb and siphon, that holds still
  better than anything alive should."*
- **Nothing here feeds you.** No forage, no meat worth the name. The larder is the ship's.

## The first week

- **Touched.** A crew member who works out in the Bloom shows an early touched state, with one message when the
  change begins. Then the changes come from a mixed deck, harmful and mixed, capped, never the same one twice on a
  body.
- **The arrest.** Held on the patient, a Sunbeam's lens stops the change where it is. What has already changed
  stays, and the treatment leaves a burn. (How a crew comes by a Sunbeam in 0.1.0 is `NEEDS HIM`.)
- **The tissue run.** What the crew came for. Take a sample from a donor; carry it to a Bloody Mess; read the odds
  before committing; come back later for what grew. A batch that misses the wanted part still brings matched,
  usable tissue: a kidney, a liver, a lung, a heart.
- **The Unfinished.** The goo buds them constantly, each *"half-made its own way"*; most are nuisances, *"some roll
  a monster"*; they live days and die into slime and mulch.
- **The dead leave marks.** A corpse here becomes skin, then a lasting print on the ground, and a Bloody Mess eats
  the rest. Nothing just disappears.
- **The Repulsor.** A powered Helix device that punches a hole in the cloud. It warns first that its Burn covers
  the whole map and everyone in the open, then clears the sky, and stops when the power does.
- **The zhool.** A creature whose red haze turns ordinary plants into flesh plants, here and nowhere else.

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
  observation posts at the valley mouths."* They buy samples, and they are the only people here. Their caravan and
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
- **Whatever changed.** It leaves with the crew. *"Including you."*

## What the place does to the ship

No Contagion source says what this place does to a landed hull. The sources name three things that touch
everything else here, and this design picks the first as its default and asks (see `NEEDS HIM`):

- **The goo comes aboard from the ground up.** The Bloody Mess is *"an extension of the terrain itself"* that
  *"creeps"* and *"eats everything dead."* Default: it creeps onto whatever of the hull touches the ground and has
  to be scraped off by hand, or burned off by a Burn, which sterilises it. That gives the Repulsor's ship
  hardpoint (ruled 2026-09-27 as *"the ship touch"*, 0.2.0 here) a second job: the hull's own cleaning lamp.
  New in this design, unbuilt, and marked as such in the scope.
- **The Burn and the scald rain** are in the sheet as weather. Nothing built makes either damage a structure.
- **The hull is otherwise the answer, not the victim:** it is the roof.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| Under the standing Bloom the sky is a red storm lid, not grey overcast. | A fresh map at rest. | An ordinary overcast tint fails. |
| Gawpsacks sink, rattlegrope shakes and red puffs rise before the Burn, never after. | A natural Burn, watched from before the tells. | A Burn with no tells first fails, whatever follows. |
| Crew within one dash of shade get in during the tells; a far party is caught out. | Two parties at two distances from the ship. | The far party pays. |
| A prepared crew member crosses between refuges in a Burn and lives, hurt; one who stays out is in grave trouble. | One dash, and one pawn left standing in it. | Unhurt fails; dead on a normal dash fails. |
| A roof, a tree's cast shade and water each count as refuge. | One pawn in each through a Burn, one in the open. | The Burn uses the shared shade, with no test of its own. |
| UV-shy natives are hurt by the Burn and dive during the tells; Scaldhide and Crispling are not hurt and come out. | A mixed group through a Burn. | A native that dives only after being burned fails. |
| No native runs from the sun under the Bloom; they do when the Burn clears the sky. | The same animals under Bloom and in a Burn. | |
| The Repulsor warns that its Burn covers the whole map, clears the sky, and stops without power. | Power it; read the warning; cut the power. | A cleared patch is wrong: the Burn is map-wide. |
| A worker out in the Bloom shows an early touched state and one message when change begins. | A worker left outdoors, one kept in. | |
| Changes come from a mixed deck, each with a real cost, capped, never twice on one body. | A run to the cap. | A change that is only a label, or only a gain, fails: *"it never just upgrades you."* |
| A Sunbeam held on the patient stops the change, keeps what has changed and leaves a burn. | A patient at warning stage and one already changed. | Later exposure can start it again. |
| Each budded Unfinished is half-made its own way and dies into slime and mulch. | A Bloody Mess over several buddings. | Two identical in a row is suspect; one that vanishes with no sign fails. |
| A gestation shows its odds before the sample is spent and, when the wanted part misses, still brings matched tissue. | A run that hits and a run that misses. | A cancelled run does not spend the sample. |
| A corpse becomes skin, then a lasting print, and a Bloody Mess eats the rest. | A death left alone. | |
| The plants read as grown flesh; zhool haze turns plants, in our biomes only. | A fresh map; a zhool beside ordinary plants. | A recoloured forest fails. |
| The natives are there in numbers, each plainly its own creature, each with the death or trick its description promises. | A walk of the roster. | No number is a promise. The flyers' flight is read from state, never live-tested without him. |
| A save reloaded mid-way, and the main actions done in another order, give the same Burn, body and batch. | The walk. | |

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

**0.1.0, the stop** (the locked sheet's version, read for a ship)
- The Bloom as a red lid; the Burn; the tells; the Dive; the armoured natives coming out. (built; the Dive and the
  natives' Burn damage are owed or were failing)
- Refuge as shared shade; one dash at a cost. (built in part; water as cover is owed)
- The touched state, the mixed deck, the Sunbeam arrest. (built)
- The ground Repulsor with its warning. (built)
- The Unfinished. The genome loop's ordinary batch with odds shown first. (built; the odds display is owed)
- Bodyprints by phases. (owed, by his card of 2026-10-16)
- Flesh flora; zhool haze; the grotesque cast with each creature's promised trick; the new smaller Zhool'Iza.
  (built; the Zhool'Iza is owed)
- Mulch as plain fertiliser.
- The goo on the hull, scraped or burned off. (new in this design; unbuilt; `NEEDS HIM`)

**0.2.0, the stop with company** (the first three by his word of 2026-11-16)
- The Coalescence, all of it.
- The Grown Limbs, all of it: Pillar Arm, Lash, Eyeburst, Caudal Spring, Bellows.
- Helix trade: draftprints, contracts, the curators' caravan.
- The Repulsor's ship hardpoint (the curators stock it). (built, untested)
- The Rawshade: a creature that stands still in a Burn so that small things shelter under it, *"Then the skirt
  comes down."* (designed 2026-11-02)
- Red water made drinkable by a day in the sun. Red sap as repellent and sealant. (items exist; uses do not)
- The Sunbeam's extra harm to natives, if it is not already wanted in 0.1.0. (built)

**Later (a crew that stays, a colony, or the campaign)**
- The Ashfall Research Base and its one line of plot; Helix observation posts as places.
- Spore blooms downwind as this biome's export event; the infection front advancing in Blooms and burned back in
  Burns.
- A whole season of the valley's ecology holding together.
- Steering a gestation toward a wanted part.
- The three rites (the Sunning, the Unfinished Laid Down, the Kept Mistake); they live in the rites mod.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Silence as the alarm; the god mid-birth (cut at the sitting of 2026-09-27).
- Mulch that infects a field unless sunned (his card: plain fertiliser only).
- Any heat or sun particular to this biome (2026-10-19). The Burn's own exact-cell tree test.
- A touched outcome that is a net gain (the sheet's ban, his ruling).
- Bars that pin yields, creature numbers or art variant counts (2026-11-16).
- The donor cast, the exotic draft names, "Eyegore", the Fleshsop that *"needs to be loved to live another day"*.
- Edible forage. Any native that persists under open sky.
- **Recommended for dropping, not yet his:** the duplicate seed-fist fertiliser, the unused donor plants, the
  planet-scoring worker.

## NEEDS HIM

1. **Where does a 0.1.0 crew get a Sunbeam and a Repulsor?** Both are sold only by the Helix curators, and Helix
   trade is 0.2.0 by his word of 2026-11-16; the arrest and the Repulsor are 0.1.0 leaves of the locked sheet.
   *Found as salvage in a dead visitor's Burn shelter on the map* (default; the sheet has *"the ruins of visitors
   who learned the clock too late"*; one new placement to build). *The curators' caravan sells devices in 0.1.0
   and only contracts and prints wait.* *Both devices move to 0.2.0 with their sellers,* and a touched crew member
   in 0.1.0 cannot be arrested.
2. **What does this place do to the hull?** No source says. *Goo creeps onto it and is scraped or burned off*
   (default, new). *Nothing: here the hull is purely the refuge.* *The scald rain wears it,* borrowed from the
   Scald.
3. **Does a Burn show the ship to orbit?** *For as long as the sky is clear* (default). *No:* the lid's step is
   constant and a forced Burn is free. *A forced one only.*
4. **Do the Helix sell out a stolen ship?** Unsettled anywhere. It decides whether trading with the only people
   here is safe. *Not decided here* (default: they buy and say nothing).
