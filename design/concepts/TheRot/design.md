# The Rot: the design, seen from the ship

**Status:** the one design document for the Rot biome (`RM_TheRot`, source `src/RimMandrake/TheRot/`, with shared
mechanisms in `src/RimMandrake/EnvironmentalHazards/` and `CreatureBehaviors/`), rewritten 2026-11-18 on the owner's
instruction to see every biome "through the lens of Utinni". It replaces the older definition sheet, reviews, cast
and naming documents, kit specification and cleanse proposal as the place to read; what happened to every idea in
them is in `design/concepts/TheRot/rewrite_choices.md`. Nothing has been deleted yet. This is a design document only
and it launches nothing. A second reader checked it against the sources on 2026-11-18 and repaired the fuel, hull,
scope and `NEEDS HIM` sections; what changed and why is at the top of the choices page. A third run the same day
read the roster file and the bars draft to their ends and corrected what the giant spares (a roof or a stockpile
zone).

**Kind, checked against the sheet's own header:** land. A fungal continent on the night shoulder of the storm wall.
Its milky ponds are *"not water"* and are no sea; the seabed rulings do not apply.

**What the owner had already marked.** On 2026-11-17 he read the cleanse proposal for the Rot and changed one cell
(`cleanse/owner_marks.md`): the pleasure brew, which the Designer had proposed dropping, he set to 0.1.0. Every
other row he let stand. This design keeps his mark and moves a good many of the rows he let stand, each listed under
"Scope moves" in the choices page, because he let them stand the day before he stated the ship lens.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/TheRot/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Rot has no locked sheet or tree; its only pipeline material is the cleanse
proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"A pale fungal continent on the night shoulder of the stormwall — bone-white and lilac towers under a black sky,
> a glow-moss floor that is warm to lie on while the air above it would kill you, milky ponds that are not water,
> and a fine wet gloss on every surface that is the jungle deciding whether you belong to it yet."*
> (`the_rot.md` §1)

*"Nothing here is a plant. Nothing here is quite an animal. Everything here is connected, everything is warm from
the inside, and everything — including what you take away with you — is still alive."* The sheet's name for it is
*"the planet's gut"*: the dayside is the leaf, the storm wall the throat, and this is where what falls is digested.

The owner's line for the experience, picked by card on 2026-10-20:

> *"A cathedral of mushrooms in the dark, generous and hungry. The Rot shares everything, including you."*

**Seen from the ship, the Rot is the stop that eats what you put down.** It is the kindest landing on the night
side: the floor is warm, food stands in towers, the light is soft. And *"the gut digests whatever is set down in
it."* Meat left out is *"gone within a day, for certain."* What the crew harvests *"keeps metabolizing after
harvest, pushing heat — it will wreck any freezer that is not overbuilt."* And something the size of a house crawls
the forest floor eating *"whatever lies down."*

For a crew of scavengers there is one clause in all this that changes everything. The giant *"digests all but
metal and passes polished salvage."* The Rot will take their food, their dead and, if they are careless, their
wounded. It gives back their scrap in better condition than it went in.

The Rot was also given a ship story before the lens was stated, in the owner's own words. On 2026-10-02 he chose
the giant and typed: *"Like a huge maggot slow maggot covered in small wriggling tentacles and eye spots, I love the
old ship that's pinging from within begging the players to figure out how to kill it."* Something aboard a ship
that came here before this one is still calling. The crew's console can hear it.

That earlier ship's log is written, eight entries of it, and built. It is the story of a crew exactly like this
one. *"Day nine. Something big came through camp in the night. Slow. Pale. It ate the cargo netting, the tarps, the
galley. It did not touch us. It left the cutlery in a glossy lump by the ramp, clean as new."* *"Day fifteen.
Engineer took the drive coil out to clean the spores off it. Left it on the mat for one hour. One hour. It is gone,
and the pale thing is lying where it was, and we can hear the coil humming inside it."* And the last entry, which
stops in the middle: *"Cut the beast open gently. It never meant us harm. It just keeps"*

The crew are desert people on the cold side of the world. They will be lying on the floor a great deal.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought.

**The outer edge of a stay here: about six weeks.** By the owner's word of 2026-11-18 the figure a design derives is
*"the outer edge allowable"*, not the typical stay. If the Empire wins every step, the bombardment is the fourth
full interval of the ladder: 28 to 45 days at one step quieter than open ground.

**Cover from orbit: canopy, one step.** His ruling of 2026-11-18: *"Canopy, steam and fog slow the search by one
step; full dark still pauses it."* The Rot is a forest of caps wide enough to stand a camp under, *"dense beyond
anything dayside"*, in a fog of its own making. That is canopy and fog, and this design gives it the one step. It is
also on the night side under a black sky. Whether that makes it "full dark" is the same question the Sleeping Ice's
design asks first, and the default is the same: it does not, because the forest floor glows. *"All useful light is
biological"*, and there is a lot of it.

---

## The first minutes

The ship comes down through cap and fog into blue-gold light from below. The air is cold enough to hurt. The crew
steps off the ramp onto a floor that is warm. *"You land warm. That is the first wrong thing."* The sheet's way of
saying it: *"air temperature is a lie about the ground."*

Before anyone has decided anything: towers of pale fungus on every side, with room to walk between their stems; a
milk-white pond catching the light; a wet shine already on the hull; and, on the pilot's console, a ping that is not
the ship's.

Somebody puts down a crate of meat.

## The first day

- **The floor is the heater.** Living mat warms a room built over it. Walls and a roof on the mat are a warm
  bedroom with nothing burning. Lay a hard floor over the mat and the warmth is gone. It helps a great deal and it
  does not make the cold trivial (owner, 2026-09-17: *"It just helps a lot."*).
- **The rot clock.** Anything organic left in the open where the mat is alive spoils fast and then is gone. A
  lean-to does not help; walls and a roof do. Frozen food keeps as it would anywhere. Metal is not touched.
- **The harvest is alive.** Caps for food, giant stems *"as strong as wood"*, fibre, fungal medicine: all there for
  ordinary cutting. Stored, the food stays warm. A freezer full of it has to work harder, and the game shows why.
- **The milk.** Shallows of fungal not-water. Native things drink it. Nobody else should. Mushroom bridges cross it.
- **The fall.** What comes down from the sky is the Sheen, *"a reproductive sleet flung outward to colonize"*. *"No
  water rain, ever."* In this version it is weather to look at and a shine on everything, the ship included:
  *"everything sheened is being considered for colonization."* It comes aboard with the crew. His reason for
  ruling that gear only slows it (2026-09-17): *"incidental exposure every time you go in and out — you just can't
  totally sterilize everything."*
- **The armed ones.** Some mushrooms defend themselves. An Agarilux Prime *"releas[es] large clouds of extremely
  dangerous spores"*, and when what it gassed is dead it *"extends prehensile hyphae to feed on their rotting
  corpses."* Its little sibling the Skulltop *"produces toxic spores when anything gets close."* Both stand where
  they stand and can be walked round.
- **The residents** are all part fungus: grazers and milkers, a wasp colony, a silk moth that really flies, a
  mantis the size of a person that stands so still it passes for a cap, and a six-legged colossus with *"its back a
  grove of full-grown caps."*

## The first week

- **The gut that walks.** The hwelgrue: huge, slow, tentacled, eye-spotted. It does not hunt. It grazes the open
  ground and eats what is lying on it: stores, corpses, and anyone who is down. *"It simply clears up after a
  fight."* It leaves whatever is under a roof or inside a stockpile zone, goods and the downed alike (read in the
  built source; the drafted bar of 2026-10-22 names the same control).
- **Something is still alive in there.** Whoever it swallowed can be heard: *"a muffled knocking and a voice through
  the hide that grows fainter as digestion goes on. The knocking is a clock and a name."* Select the giant and it
  says who and how long. Hurt it enough, in time, and they come out alive. His answer of 2026-11-10: *"A prompt,
  committed response can still succeed... delay worsens the outcome."* *"Sometimes the knocking is a stranger."*
- **What it gives back.** Everything it ate that was metal comes out later in a casting that cracks open: whole,
  cleaned, mended.
- **The ping.** One hwelgrue on the whole planet carries a ship's drive core in its gut, and the core answers this
  ship's engine. The pitch of the ping tells how sound the core still is.
- **The cup.** A lussa crown, guarded by its own cloud of spores, cut and brewed on the day and drunk where it was
  cut: joy, and a good memory that lasts a while. *"You want some of this, you come to the biome and prepare it in
  your vessel, right now."* It cannot be carried away. This one was kept in 0.1.0 by the owner's own mark.
- **Fuel in a pod, perhaps.** A wild blastpod can be cut for a sac that burns, bursts, or renders to chemfuel. It
  is built, and as built it cannot grow at any temperature the Rot has; see "Fuel, and the hull".

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The warm floor.** *On screen:* a whole crew of small hooded figures lying flat on a glowing floor, in the
   open, not asleep. *Why it is funny:* the thermometer over their heads says the air would kill them.
2. **The crate is gone.** *On screen:* a stack of meat set down beside the ramp at breakfast; by the next breakfast,
   a smear. Beside it, untouched, the scrap pile.
3. **It ate the scrap pile.** *On screen:* the hwelgrue crawling across the salvage yard, the yard empty behind it.
   The crew follows it for a day. A casting drops and cracks, and everything is in it, shining. *Why it is very
   Jawa:* on the second day they are carrying rusty things *to* it. The sheet's review saw it first: scavengers
   follow it *"as crows follow a plough."*
4. **The knocking.** *On screen:* after a fight, the giant moving off across the field, and from inside it a
   knocking, and a name over it, and a time.
5. **The cap moves.** *On screen:* one of a row of pale caps beside the path unfolds into a mantis.
6. **The mushroom that eats.** *On screen:* an animal wanders too near a Prime; a cloud; the animal down; thin
   pale threads reaching out to it across the ground.
7. **The freezer.** *On screen:* the hold's cold room climbing degree by degree with nothing wrong with it. It is
   full of mushrooms, and the mushrooms are warm.
8. **Brewing in the grove.** *On screen:* a Jawa crouched over a pot at the foot of a guarded crown, inside the
   drifting edge of its spores, drinking the result on the spot because it will not keep.
9. *(0.2.0)* **Hurt one and the others come.** *On screen:* a hunter wounds a rennok; the wound on it shrinks, and
   every rennok in the grove is suddenly bleeding a little and walking this way.
10. *(0.2.0)* **The shine.** *On screen:* a crew member who has been outside all week has a gloss the others do
    not. *"The longer you stay, the more you shine."* The inspect line says what the gloss is becoming.
11. *(0.2.0)* **Cutting out the core.** *On screen:* the crew fighting the one giant that pings, by hand, with the
    ship's guns silent, because a hit from the ship's weapons costs the core its soundness.
12. *(0.2.0)* **The console reads a dead crew's diary.** *On screen:* every few pings, a letter in another ship's
    voice. *"The fog does not clear; it sticks."* *"Note for whoever reads this: cover what you keep."* Every
    second entry puts a cache on the world map. The eighth is the camp *"past the third ridge"*, where *"the warm
    mat took them in the way it takes everything, gently and completely."* What is there to carry home is a root
    of the mat, for the ship. The log only goes on while the giant lives; the core only comes out when it dies.
13. *(0.2.0, campaign layer)* **Digging up the floor to sell it.** *On screen:* Jawa with shovels cutting warm
    fungal soil for the moisture farms, and every hybrid within earshot turning toward them. The fungal-soil
    trade is built in the campaign tier: dig it, sell it by ship, and the digging *"sends distress through the
    fungus and brings its creatures."*

## When the Empire arrives

- **The forest is close.** Stems and caps block long shots. A probe or a spotter that needs to see the ship has to
  come in under the caps to do it.
- **The armed mushrooms do not ask.** A squad that sets up beside a Prime is gassed, and then it is fed on.
- **The gut clears up.** Troopers who go down in the open are on the hwelgrue's path like anyone else. What comes
  out the other end, in a day or two, is their armour and their blasters, cleaned. This is the one battlefield on
  the planet where the salvage is delivered.
- **The rot clock takes the rest.** Dead left outdoors are gone fast. So are a siege camp's unwalled stores.
- **A camp on the mat is warm.** The Empire's shelter gets the floor's warmth exactly as the crew's does. The Rot
  is generous to everybody.
- **They may already be following the giant.** Pitched with the hwelgrue on 2026-10-02 as a hook and never ruled
  on or built: *"Imperial salvage crews have started following it too; a trail shared with rivals."* `UNSETTLED`.
- *0.2.0:* **the Sheen marks whoever stands in it.** *"Breathing it without a compatible immune system virtually
  guarantees disease: the biome's border is enforced by its own breath."* A cordon that sits for two days under
  the fall is two days further along than a crew that slept under a roof. And a wounded native brings its kin.

## Who else attacks; who hates the Empire

- **The residents,** as animals do: a mantis that ambushes, wasps that defend a nest, predators that hunt small
  things. Nothing here raids.
- **The giant** attacks nobody and is the most dangerous thing on the map to anyone lying down.
- **The Wildsteam** hold sacred groves here: *"the wild's partisans finally somewhere they are not preaching to
  deaf ears"*, with *"pilgrim paths worn through Hanging Wood."* They are the campaign layer's. Whether they would
  fight the Empire or shelter a ship is `UNSETTLED`.
- **The old war** fell here once and was composted. *"Nature won here."* There are *"digestion sites — where
  Assailant material fell and was tamed"*; they are ruins, *"quietly warm"*, and nothing in them is a weapon any
  more.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- Losing the stores to the open ground, or the cold room to its own contents.
- The giant on the wrong day.
- *0.2.0:* the Sheen. A crew that works outside builds it up, and past a point it roots.

**Stay, longer than the Empire would like:**
- Free warmth, on the cold side of the world.
- Food everywhere, for a crew that cooks and eats what it cuts.
- Canopy, one step slower above.
- By his answer of 2026-11-10, quiet: *"Understanding the Rot and arranging the base well earns peaceful ordinary
  days and dependable comfort between outings; its hungry character can concentrate in exceptional events."*

## Fuel, and the hull

**Fuel: the emergency route, with more to render than anywhere on the night side; and one named source that does
not hold up.** The first read named wild blastpods as the Rot's richer source, on his ruling of 2026-09-06: the
blastpod's chemfuel chain taken in *"wild-only — it cannot be cultivated (by Jawa at least)"*, *"a fungus that's
energy rich enough to be chemfuel, that's not so bad as long as we're harvesting it"*, and it *"may be cut later if
it plays hokey."* The second read found three things against leaning on it. The built plant
(`RM_BlastpodShroom`) cannot grow below 50 °C (measured in its def), and the sheet gives this biome a maximum of
+24 °C. The roster said so on 2026-09-09: *"it can only live in hot caves; the wild-only ruling stands but its wild
presence is cavern-gated, not surface."* The donor blastpod was purged from the Rot for that reason, its stand-in
was purged too, and the roster records with his ruling of 2026-09-20 that no replacement be made: *"I don't want
new versions of these silly plants."*
And on 2026-11-17 he let the cleanse leave blastpod fuel switched off. So this design claims no richer source here.
The slow rendering of biomass has a forest to work on. Blastpod fuel goes back where the cleanse put it, and the
question was the third under `NEEDS HIM`: emergency fuel only (`Answered on 2026-11-19` 3). (`UNMEASURED`: whether map generation places grown pods that then simply
never regrow. Filed as `RIMMANDRAKE_DECIDE_ROT_BLASTPOD_GROWS_ONLY_ABOVE_FIFTY_DEGREES`.) The fungal power generator
was cut (*"that's stupid"*) and stays cut. **Where fuel is bought:** no source puts a seller in the Rot. What the
Rot gives a crew that has to buy fuel is something to sell: in the campaign tier the warm soil itself, dug and sold
to moisture farms by ship; in the free tier, mended salvage out of the giant.

**The hull: the Rot spares metal, sticks to it, and eats what is left lying beside it.** His ruling of 2026-11-18:
*"Hull wear: Yes in 0.1.0. It's easy, and most of the biome already talk about this."* The frame is built:
`src/RimUtinni/ShipShields/` (his eight shield rulings of 2026-09-02, recorded in
`design/Jawa/proposals/ship_shields_deep_design.md`). This design adds no hull system. Every wear below has a
source, named beside it.

- *The Sheen on the ship (0.1.0 by his rulings; the frame cannot see it yet).* The sources say what the Sheen does
  to a ship in a dead crew's words: *"The fog does not clear; it sticks,"* and an engineer who *"took the drive
  coil out to clean the spores off it."* His ruling of 2026-09-02 names the answer. He cut a special spore shield
  (*"spores aren't magical, just particulates"*) and gave the job to the light screen, which *"handle[s] wind,
  ash, vapor, bio contamination, spores, smoke, sand, and rain damage completely."* The built tracker wears an
  unscreened ship's outside while a particulate hazard is up, but it knows that hazard only as pollution or as
  weather carrying sand, and the three Sheen weathers carry none (measured in
  `RM_RotSporeKit_SheenWeathers.xml`). Teaching the frame that Sheen-fall is particulate is the build, and it is
  small. This is fouling that a screen stops. It is not the sheened hull, below.
- *Whatever is left on the mat (0.1.0; built).* The giant *"only eats what lies in the open."* The dead crew
  lost *"the cargo netting, the tarps, the galley"*, and then the drive coil, set down for one hour. The built
  rule is the same: any loose thing on open ground is food, and only the metal comes back. A ship part taken off
  to be cleaned is a loose thing. *"Cover what you keep."*
- *The stores (0.1.0).* Anything organic outside walls and a roof is on the rot clock. Loading and unloading
  across open mat is a race.
- *The cold room (0.1.0).* Living harvest heats whatever it is stored in. The ship's refrigeration is the part of
  the ship this biome attacks. The answers are more cooling, smaller stores, or cooking and eating it.
- *Cold (built; mostly out of reach here).* The frame wears a ship in extreme cold, with the cryo envelope as his
  answer. Its tracker calls a map cold at forty below or in a cold snap; the sheet measured the Rot's median at
  −18.8 °C and its floor at −42 °C after the coldest tail was repainted as ice. On most Rot ground the cold wear
  would not fire. `UNMEASURED` in a running game.
- *The ship's guns (0.2.0).* They cannot be used on the one giant worth killing without ruining what is inside it.
- *The crew (0.2.0).* The Sheen builds on whoever is outside.
- *What the ship gains (0.2.0).* Two parts, and they pull against each other. The **drive core**, cut out of the
  one giant that carries it, is on record as the Rot's gift to the ship. The **living mat root** is his own
  ruling of 2026-10-22: *"Can be installed on the gravship to help with heating in cold places as a reward. Needs
  food."* It is won at the log's last camp, and the log stops when the giant dies. (A judging pass of 2026-11-11
  took the root off the list of ship gifts because two other biomes also gave a heater. That was an agent's
  tidying. His ruling stands above it.)
- *Declined, and not revived here:* **the sheened hull**, in which a landed ship *"slowly takes the Sheen"*, pale
  fruiting pockets mature along its seams and cargo bays (in the consult's harder version, late pockets cost deck
  sections and the payload goes off inside the ship), and a ship that launches without scraping them seeds *"a
  small warm patch of Rot mat"* wherever it lands next: *"the biome marks the ship by using it to travel."* He
  turned it down on 2026-10-02 (*"none of these hit the mark"*). And **the launch siege**, pitched the same day
  and not chosen: *"the warm mat grows up over the landing struts and holds the ship down for a few hours"* when a
  joined crew member is aboard. Both were before he stated the ship lens. Both stay down by his answer of
  2026-11-19 on declined ship ideas; he can bring either back by name.

## What the crew takes away

- **Their own scrap, mended,** and other people's.
- **Fungal timber, fibre, mushroom leather, fungal medicine;** food for as long as the cold room holds.
- **Milk and silk,** and the animals that give them.
- **Nothing brewed.** *"No stockpilable teas or symbionts."* What the cup gave stays in the drinker.
- *0.2.0:* **the drive core,** cut out of the one giant that carries it and fitted to the ship, for a quarter more
  range at full soundness (his card of 2026-10-02); **a dead ship's log** that goes on naming salvage sites across
  the planet for as long as its carrier lives; **a root of the living mat**, from the log's last camp, that warms
  a cabin on the cold side for as long as it is fed; a **gut-mother** sac, grown aboard into a vat that returns
  the implants and gear from any corpse, with starter jars of it to sell (the one living thing he ruled may leave
  the Rot). *Campaign layer:* **fungal soil**, dug and sold. *Asked:* chemfuel from wild blastpods.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A pale forest lit from below, with ground a crew can read and walk under very large caps. | A fresh landing; a walk from the ramp to a pond and back. | A showcase pad proves nothing: a generated map with every kept feature on. |
| A walled, roofed room on living mat is warmer than the same room on bare ground, with nothing burning; flooring over the mat ends it. | Two matching rooms; then floor one. | The room is still cold-side: clothing and insulation matter. |
| Organic things in the open on live mat spoil fast and vanish; inside walls and roof they do not; a lean-to does not count; frozen stock keeps; metal is untouched. | Meat, a corpse and steel: open, lean-to, enclosed; a frozen stack outside in deep cold. | The same meat on dead cold ground at the forest's starving edge spoils at the ordinary rate. |
| Stored native food warms its store, visibly in proportion to how much is stored. | A cold room filled in steps. | The same weight of imported food does nothing. |
| A Prime gasses what comes near in the ordinary course of play, and feeds on what dies there; a Skulltop does the lesser version. | An animal wandering near each, with nobody forcing anything. | A burst fired by a debug helper proves nothing: it has to happen on the plant's own tick. |
| Under Sheen-fall an unscreened ship's outside fouls, slowly and with a letter; a ship under the light screen does not. | Two ships through a fall, one screened. | Under a clear sky neither fouls. (The frame does not see Sheen today; this is the row that says it must.) |
| The fliers fly, by the flight state. | A state read of the illoth's and dustveil's flight trackers (never a live look without the owner). | |
| Nothing vanishes. | Every loss above; the mod's master setting switched off with someone swallowed. | The swallowed person is released, not deleted. |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The hwelgrue eats loose stores, corpses and the downed in the open, and nothing that is up and walking. | A loose stack on open ground, a corpse, a downed stranger and a healthy colonist in its path. | Things under a roof or inside a stockpile zone are left, the downed included. |
| A swallowed person knocks, is named with a time on the giant, and is got out alive by hurting the giant in time; too late, a body comes out. | One prompt rescue, one late. | Never a missing-person letter with nothing on the map. |
| What it ate that was metal comes back whole in a casting. | Feed it a marked, damaged steel item; wait. | The item has its mark and quality; nothing organic comes back. |
| With the ship's engine on the map, the core's carrier pings and the ship hears it. | A map with the carrier and one without. | Only one giant in the world ever pings. |
| A lussa crown defended by its spores can be cut, brewed that day and drunk on the spot for joy and a lasting good memory; it cannot be stored or carried off. | Brew and drink at the grove; try to stock one. | A crown cut yesterday will not brew. |
| A ship part or crate set down on open mat in the giant's path is eaten like anything else, and only its metal comes back. | A minified ship part and a crate, in the open and under a roof. | The roofed ones are left. |

Settings: one switch per major feature, defaults as shipped, everything off leaves a cold forest of large mushrooms
(standing rule, every mod).

## Shared machinery

**Featured here** (the Rot is where each is vital and should be proven):
- **Ground that warms a room** (`RM_MapComponent_WarmGround` in `EnvironmentalHazards`): ordinary room heat from a
  living floor, capped.
- **Exposure that speeds decay,** and **produce that heats its store** (the same engine's organic-decay and
  living-produce parts).
- **Plants that defend themselves with gas** (the shared local gas emitter; the Prime is the pattern for every
  armed plant on the planet).
- **A creature that holds things inside it** (the hwelgrue's saved gut: items, a person, a clock, a release).
- **Preparations that cannot be stored** (the live-item viability clock).
- **Wounds shared between kin** (`RM_CompWoundLink`, `RM_HediffComp_KinMending` in `CreatureBehaviors`; 0.2.0).

**Merely active here:** very large standing things with honest footprints (`HugeThings`); the growth engine's
wet-native cycling; wreck salvage, weathered as digested; bone from butchery; real flight; the ship's scanner; the
one sun from geometry, which on the night shoulder is low or absent; the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**The one signature (his first-version answer of 2026-11-19): the metabolism.** The living mat warms a walled,
roofed room with nothing burning; organic things left in the open on live mat spoil fast and vanish; stored native
food warms its store. *Why a normal stop is sure to see it:* a landed crew sets things down and sleeps somewhere on
the first day, and what it leaves outside is gone by the next. His experience line: *"generous and hungry. The Rot
shares everything, including you."* *Runner-up:* the hwelgrue, the giant that swallows the downed; this design had
brought it into 0.1.0, and it goes back to 0.2.0 whole, as he let the cleanse mark it on 2026-11-17.

**0.1.0, the stop**
- The land: cap architecture with readable ground, living mat, milk shallows and bridges, biological light, the
  Sheen as weather, digested wreckage. (built; milk placement unproven)
- The metabolism: mat warmth in enclosed rooms; fast decay of exposed organics; living harvest heating storage.
  (built; no produce carries the heat yet)
- The armed residents: Prime and Skulltop patches. (built; their gas on the ordinary plant tick is unproven)
- The life: fungal forage, timber, fibre, medicine; the hybrid roster with its ordinary milk, silk, eggs, hunting
  and poison. (built)
- The Sheen as fouling on an unscreened ship, on the built shield frame. (frame built; it cannot see Sheen yet)

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The hwelgrue: grazing the open ground, swallowing the downed, the knocking and the rescue, castings that return
  metal, the first-sighting letter, the ping. (built; moved in, see `rewrite_choices.md`)
- The pleasure cup, brewed live at a guarded lussa crown. (built; his mark)
*Already here before that answer:*
- The drive core: one carrier in the world, soundness lost to ship weapons, cut out and fitted for range. The dead
  ship's log and its salvage sites. (built)
- The log's last camp and the living mat root: a ship part by his ruling of 2026-10-22, fed off the Rot, budding.
  (built; moved in from "later" by the second reader, see `rewrite_choices.md`)
- Wild blastpod sacs and their chemfuel. (built, but the plant cannot grow at the Rot's temperatures; asked)
- A watcher: the mollugh, *"a fungus/animal that pulls itself under its own cap"*, pitched under his 2026-10-08
  ruling that every biome gets one and never admitted at a sitting. (unbuilt; a proposal)
- Campaign layer: the fungal-soil trade, dug from the mat and sold by ship, with the distress it raises. (built)
- The Sheen on people: the coating that builds outdoors, slows under gear and shelter, and can root; the chitin
  helmet against it. (built)
- Shared wounds and kin mending. The chittik's implanting bite. (built)
- The guarded groves: the ageless cap's gas, the veil that calls defenders, the false fruit that traps; the brewing
  vessel and the two great cups, age given back and old wounds healed. (built)
- The three symbionts, each a bargain: fast healing for hunger, no sleep for a little madness, Sheen immunity for
  the sun's enmity. The unjoining draught that drives them out. (built)
- The gut-mother: the sac, the vat, implants back from the dead, starters to sell. (built)
- The thrown spore weapon. The ambrosyx. (built)

**Later (a crew that stays, or a colony)**
- The pale tree and its two levels of psylink. The grown furnace; the furnace-blood gene and a body that pushes
  heat.
- The gourmet line. Exports for the Slime. The conscience about selling marked treasures. Industrial medicine.
- The regional spore cloud, which by its own rule never falls on the Rot itself. Outdoor filth thinning.
- The Unjoining as a rite; sacred-grove wiring; found shrines, pilgrim paths, digestion-site ruins: campaign layer,
  and rites are a second version by his ruling of 2026-10-23.
- A wayward Prime on an authored tile elsewhere. A colony of forty.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- The sheened hull, the ground's heartbeat, Unseaming (*"none of these hit the mark"*, 2026-10-02). The sheened
  hull stays down by his answer of 2026-11-19.
- The launch siege for the joined; the joined ear (pitched 2026-10-02, not chosen). The launch siege stays down by
  the same answer.
- Two giants offered beside the hwelgrue and not chosen (2026-10-02): the yssomar, the wound-bearer whose scars
  are not its own; and the brullith that cannot lie down. *"No yssomar is built."*
- The wound-tie surgery (held off the card). The grove's audible breath (offered with the heartbeat).
- The Gut's Due and Standing in the Sheen rites; the Bought Quarrel (not chosen).
- The fungal power generator (*"that's stupid"*). Cultivated blastpods.
- Storable or exportable teas and symbionts. A general gene bank (the Slime's alone). A psycast economy. Any living
  weapon. Conventional plants. Animals that are not part fungus. Water rain.
- The vanilla zoo; the nameable donor animals evicted in 2026-09.
- **Recommended for dropping, not yet his:** the extra spore allergy; the giant's own rot aura; the mould mood
  penalty; the fungal hydroponics basin; the spider-head trophy; the airborne-food collector; world scoring. (The
  cleanse's recommendations, kept.)

## NEEDS HIM

None open. Every entry is answered (next section).


The cleanse proposal's own question to him still stands and is not re-asked here: whether exposed frozen meat
should also be digested. This design keeps the cleanse's default, that frozen stock keeps.

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

3. **Is the blastpod the Rot's fuel?** Emergency fuel only. The plant cannot grow at the Rot's temperatures, and he
   kept its donor bodies purged (the design's default). *Delegated call.*

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

1. **The sheened hull, again?** *His card of 2026-11-19 (declined ship ideas):* it stays turned down, and the launch
   siege with it. The Rot spares metal and wears on stores, the cold room and the crew. He can bring either back by
   name.
2. **How much of the giant is 0.1.0?** *His card of 2026-11-19 (first version):* none. The signature is the
   metabolism (Scope, top), and the hwelgrue moves to 0.2.0 whole, as he marked it on 2026-11-17: the eating, the
   swallowing and rescue, the castings, the first-sighting letter and the ping, with the core, the log and the vat
   already there. The pleasure cup (his mark) moves with it. **This changes the design's default.** Was: the eating,
   swallowing, rescue, castings and ping in 0.1.0.
