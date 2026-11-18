# The Blue Desert: the design, seen from the ship

**Status:** the one design document for the Blue Desert biome (`RM_BlueDesert`, source `src/RimMandrake/BlueDesert/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the
older definition sheet, the life brief, the cast bible, the flora pitches, the reviews and the cleanse proposal as the
place to read; what happened to every idea in them is in `design/concepts/BlueDesert/rewrite_choices.md`. Nothing has
been deleted yet. The Blue Desert is not on the owner's hold list, but only the Pyrelands is advancing as a biome
mod: this is a design document only and it launches nothing.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/BlueDesert/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Blue Desert has no locked sheet or tree; its only pipeline material is the
cleanse proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

**What kind of place:** land. A dark, frozen plateau on the deep nightside (checked against the sheet's own header:
*"Deep nightside regime (eternal dark, near-zero energy budget)"*, median −42.6 °C, *"zero water, zero rivers"*).
It is not a sea and the ship lands on it like any ground.

---

## What this place is

> *"An alien expanse of beautiful blue locking ancient secrets from the depths of time. Mine slowly and carefully or
> risk your own passion's heat turning everything into a bomb."* (owner, typed 2026-10-20)

> *"From orbit it is the bluest thing on the planet; underfoot it is colorless."* (`the_blue_desert.md` §1)

A plateau of the oldest ice on Ash'karr, scoured bare by cold wind. Its sand is ice grain; its snow is that sand
blowing. *"It is usually clear, and silent, and beautiful, and almost empty. Then the ablation line gives something
up — a meteorite, a hull, a freeze-dried body that fell from orbit, or a cocoon that has waited since the war — and
the beauty has a price tag on it."*

Nothing alive here runs on water. Plants and animals are *"hydrocarbon plumbing"*: butane and pentane for stored
energy, *"transparent, needing no light and so growing fractal branches for gas exchange in place of leaves — ferns,
dandelions, fuzzballs."* Every one is a charge of fuel that only the cold keeps quiet. *"Cold enough that starting
them burning is very hard; when they do go, it is not a fire, it is an explosive chain reaction."*

**Seen from the ship, the crew is the heat.** Jawa are comfortable to 46 °C and have never been cold in their lives
(`reconciled_lore/05_the_clan.md`). They arrive in the warmest object for a hundred kilometres, need a heater to
stay alive, and carry ion weapons as their whole identity (*"personal, carryable ion is the Jawa innovation and
identity"*, `07_physics_and_arms.md`). Everything outside the ramp is free fuel, free salvage and the purest water
on the planet, and every one of those three habits (warmth, ion, hauling it all aboard) is the wrong one here. They
do see in the dark, which is the one thing the place gives them for nothing.

The owner's later answers (question card, 2026-11-10) fix what "carefully" means: *"Prepare containment: separate
dangerous growth and secure escape routes before digging"*; and the ice itself *"should be minable like an ordinary
mineral."* The ground never explodes. The life on it does.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing on open ground, then scouts with a spotter, a strike
team, an ion cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. A loud crew
halves every wait and a hidden one doubles it.

**Cover from orbit here: full dark.** The Blue Desert never sees the sun, and by his rulings *"Dark/covered tiles
PAUSE the orbital clock and substitute their own dangers and scarcities"* (2026-08-05) and, on today's card, *"full
dark still pauses it"*. It gets no second kind of cover on top: the sky is *"usually clear — much less shelter than
the crags"*, and the ice fog hides the crew at ground level only. As built, the pursuit's list of slowed biomes
holds the Abyss alone (waits multiplied by four), so the Blue Desert's pause is owed work, not a fact of the game
today.

**How long a stop lasts (the outer edge).** If the dark pause is built the way the Abyss's is, a quiet crew gets
the ladder's own figure for a dark refuge, *"roughly 40–64 days between rungs"*, so the Empire is not what ends a
stop here. The larder is: nothing native is food for the crew, and the heater eats fuel every hour.
`UNSETTLED`: nobody has measured how long the ship's stores feed six Jawa. This design treats **about a month
to six weeks** as the outer edge of a stay, set by food and nerve, and expects most stops to be far shorter: a
salvage run of a few days. A season is fifteen days, so one regrowth of a cleared patch can be seen and little else
that is slow.

`NEEDS HIM` (see the end): whether a blast chain, visible from orbit on a black plain, ends the pause. This design
assumes it does, which makes the biome's own signature the thing that gives the crew away.

---

## The first minutes

The ship comes down on a blue plain that turns colourless as it gets close. *"Starlit clear as the baseline — the
widest sky on the planet."* Around the landing site the ice is dotted with small glassy things, knee-high at most:
floss, ferns, lattice globes, a scarlet cushion of beads, a violet rosette giving off the only natural light. Far
off, something the size of a hill is not where a hill was on approach.

The ramp opens and the cold comes in. The first decision of the stop is made by people who want to be warm: where
the heat goes. Warm air spilling down the ramp onto living floss, a heater by the door, a brazier outside for the
watch: each is a slow fuse under a field. A warmed plant shows a readable warning state and gives a crack before
it goes, and taking the heat away before that point stops it. After that point it is a chain: *"not a fire."*

Whether the ship's own landing sets off the growth under the hull is `UNMEASURED` (it depends on what a gravship
landing does to the cells beneath it) and `NEEDS HIM` as a design matter.

Before the first hour is out the player should have seen: transparent plants with the ice visible through them; an
old extraction face with somebody else's abandoned gear standing at it; and a herd of small pale grazers that
ignore the ship entirely.

## The first day

- **Clear before you work.** The answer he gave: cut the growth along the working route, carry its wax away from
  the exit, keep a way back to the ramp that no fuel touches. Cutting and harvesting a plant is safe; killing it
  with damage is not. A gap has to account for animals, corpses and carried wax as well as plants: a dead grazer
  on the path reconnects it.
- **The ice is just ice.** An ordinary Mine job on the old face yields blue ice: *"mineable water-ice blocks of
  distilled-level purity"*, which he called *"golden"*. No special technique, no hidden roll, no penalty for
  swinging fast.
- **Everything else is fuel.** Every plant harvests to cold wax and every animal butchers to it. Wax is safe below
  freezing and ruins, then wicks, in the warm. So does a native corpse. *"You never bring one indoors"*, and
  bringing everything indoors is what Jawa do.
- **The old workings.** *"Not the first time anyone thought of it."* An abandoned cut, with equipment, salvage and
  mineable ice, readable as an earlier crew's attempt without any letter or study. To a Jawa it is an unattended
  yard.
- **The fallen.** Wreckage locked in the ice, placed with the map: *"meteoritic metal, crashed wreckage,
  freeze-dried corpses that fell from orbit (the Empire's orbital holdings are the unwitting supplier)."*
- **The hold.** Loose blue ice stacked in a closed room keeps it cold by itself, with no rack and no power,
  for *"a very, very long time"* (his write-in, 2026-11-10). That room is where the wax lives aboard.

## The first week

- **Drift.** The weather that passes for snow is ice sand on the wind, and it piles deepest on the cells beside
  walls, doors and the hull, slowing every trip until it is shovelled or erodes. His condition when he ruled it:
  *"we need to do testing to make sure it goes deep."*
- **Ice fog.** Diamond dust at forty below: long shots miss, weapon range is capped short, everyone walks slower,
  and it lifts by itself.
- **The Haze.** A soft blue-white veil of hydrocarbon settling out of the air. In these versions it is weather to
  look at, not an illness.
- **Fuel for the tank.** Wax carried into a cold room with a biofuel refinery becomes ordinary chemfuel. The
  workroom has to stay below freezing the whole time: warm it and the bill's own ingredients go first.
- **The food web at work.** Small croppers on the floss; the sealed, armoured dorrak tearing plants up whole; the
  krissek running them down with a halo of blue fire; pickers on what is left. A predator's kill is a small
  explosion. Careless shooting in connected growth is a large one.
- **The mountain.** Rarely, a vhaulk crosses the map: *"From the ridge it reads as a hill that was not there last
  season."* It ignores the ship. It leaves by walking off the edge, with a notice.
- **The hull goes white.** By the end of a week the windward side of the ship has a drift against it, and leaving
  means digging first.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The warm welcome.** *On screen:* a Jawa sets a heater by the ramp and stands in front of it, pleased. The
   floss nearest the door changes state, cracks, and a line of small blasts runs out across the ice and back
   toward the cargo stacked beside it. *Why it is funny:* the heater is fine.
2. **Do not still the mountain.** *On screen:* a hooded figure levels the clan's proudest ion gun at the biggest
   animal anyone has ever seen. *"Any EMP hit against a living vhaulk detonates it immediately."* The largest blast
   on the planet's surface. *Why it is alarming:* ion is what a Jawa reaches for first, because *"you want the
   thing afterwards."*
3. **The right way.** *On screen:* the same giant brought down slowly with slugs and blades, no fire anywhere, and
   then a house-sized cistern of fuel lying intact on the ice with six Jawa standing round it working out how to
   get it up the ramp cold.
4. **The hump.** *On screen:* a dorrak shot in the hump goes up and takes the shooter's neighbour with it; the one
   shot anywhere else just falls over.
5. **Blue fire.** *On screen:* a krissek at full sprint with a halo of blue flame, *"the only warm light for a
   hundred kilometres"*, straight through the picket line; whoever kills it is standing next to it.
6. **The pantry.** *On screen:* the cold hold's stack shows its warning; somebody left the door open hauling.
   The crew can save it by shutting the door and taking the heat away, or can run. *"One cooling failure aboard
   and the pantry is a bomb."*
7. **The souvenir.** *On screen:* a dead picker carried proudly into the warm ship. A warning, a wick, a hauler
   reversing down the ramp at speed.
8. **The pet ate a plant.** *On screen:* one of the clan's gross little pets crops a glassy fern and is visibly,
   noisily ill with a gut full of butane.
9. **Shovelling out the ship.** *On screen:* a stolen starship up to its landing gear in blue-white drift and a
   line of very small figures with shovels.
10. **The kite.** *On screen:* a vrisk, thin as a kite, really flying, skimming the Haze over the crew's heads.

## When the Empire arrives

It arrives late if the crew has kept dark, and soon if it has not.

- **They bring heat.** Drop pods, blaster fire and a siege camp's stoves all land in the same fuel the crew spent
  a day clearing around its own door. The field does not care who warmed it. `UNMEASURED`: which Imperial weapon
  damage counts as heat-family for the charges.
- **Prepared ground is the defence.** The crew's cleared apron is a firebreak; the uncleared growth beyond it is a
  minefield the attackers walk through and shoot across.
- **Fog.** In ice fog nobody hits anything at range, and weapon range is capped: a fight in fog is close, which
  suits nobody small.
- **The cordon and the mountain.** The Empire's fourth step is an ion emplacement aimed at the ship. Ion is the
  one thing that sets off a living vhaulk, and the cast bible already says what a vhaulk near a siege is: *"lure
  it toward a siege camp and it is a weapon."*
- **Their own old cut.** One of the abandoned workings is theirs: *"the Empire (the recent shallow arrogant
  cut)."* They have lost people here before.
- *0.2.0:* a drift against any wall may hold a murrek, the Empire's walls included.

## Who else attacks; who hates the Empire

- **The krissek and the murrek** hunt whatever is small enough, and the crew is small.
- **Nobody lives here.** There is no settlement, no trader and no ally on the ice. Nothing here hates the Empire
  because nothing here has opinions; the vhaulk and the field are impartial.
- **The Horrors (0.2.0, and the campaign's to deliver).** *"The ice hands up the weapon"*: the war's siege forms
  wait in the ice, *"hardened for siege, building and vehicle attack"*, and warming a quarry face can release one.
  They attack everyone, and a landed ship is a vehicle. The neighbouring Night Horrors mod owns them; nothing
  links mining to them today.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The larder: nothing here feeds a Jawa.
- The cold: the heater needs fuel, and the fuel must be made in a room the heater must not reach.
- A blast that takes the stores, or a pantry that goes.
- The drift, if digging out is left too long.
- A flare that ends the dark (see `NEEDS HIM`).

**Stay, longer than the Empire would like:**
- The dark itself. This is the quietest sky on the planet for a crew that shows no light and sets nothing off.
- Fog at ground level against a probe that has to *see* the ship.
- Fuel and water on the doorstep.
- A cleared apron that turns the plateau into the crew's own minefield.

## What the crew takes away

- **Blue ice:** the top grade of water on the planet, and the hold's own refrigeration while it lasts.
- **Fuel:** this is one of the richer fuel stops. Cold wax from every plant and carcass, refined cold to chemfuel:
  *"a chemfuel windfall that explodes if you warm it."* An amber vashpuk bladder regrows after tapping, *"a
  renewable cold-wax well"*; one vhaulk taken the hard way is a tankful. It is not the richest: the propane lakes,
  one step colder, are the replete source. Nobody here sells fuel, because nobody is here.
- **Salvage:** meteoritic metal, wreckage, the gear at the old workings.
- **Wax as cargo,** to sell on the dayside, for as long as the hold stays cold. *"The phase-line physics travels
  with you."*
- **A cold-blooded pet,** if the crew tames a dovvik or a choir of ossivel, and can keep a room below freezing for
  it for the rest of its life.

## What the place does to the ship

- **Drift burial.** Ice sand piles against the grounded hull (ruled into the slate on 2026-09-28: *"drift burial
  of a landed gravship"*). The answer is hands and shovels: clear the sand before launch. What an undug hull costs
  at launch is for the shared hull-wear rules to state; this design promises only that the drift is deep, is
  against the hull, and can be cleared.
- **Cold.** The hull has to be heated from inside, against −42 °C, by a crew that must not warm what is outside
  or what is in the hold. The answer is two rooms and a closed door: a warm one for Jawa, a cold one for cargo.
- **Blast.** A chain reaching the hull damages it like anything else. The answer is the cleared apron.
- **Fog** does not ground the ship in these versions.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The ground is pale ice with transparent, small, branching life on it, and an abandoned working with ice and salvage to take. | A fresh map seen at ordinary zoom, then the old face mined and its salvage hauled. | A map with generic loot and no physical site fails. The plants must show the ice through them. |
| Blue ice is mined like any mineral and never explodes. | The same face mined fast and slow, beside a heater. | Neither pace changes yield or danger. |
| A warmed plant warns, cracks, then goes; taking the heat away before the crack stops it. | A heater beside a patch; one run leaves it, one removes it in time. Save and reload mid-warning. | The reload does not reset the warning. A brief warm moment that harms nothing is not the test. |
| A blast spreads through connected growth and stops at a prepared gap. | Two equal sites, one cleared with a fuel-free route to the ramp, one not; the same shot fired into each. | A corpse or a dropped wax stack laid across the gap carries the blast over it. Bare ice never carries it. |
| Cutting, harvesting and native grazing are safe; killing a plant with damage is not. | One plant cut, one grazed by a dorrak, one shot. | |
| Native animals are fuel: a kill is a blast, the dorrak's hump is the fatal place, the krissek burns blue when it runs and goes up once. | One of each killed; a dorrak shot in the hump and one shot elsewhere. | One death, one blast: the krissek does not go off twice. |
| The vhaulk goes off only when killed by heat, or at once when ion touches it alive; killed cold, its cistern is intact. | Three vhaulks: a heat kill, an ion hit, a kinetic kill. | The kinetic carcass, warmed afterwards, is still dangerous. It leaves the map with a notice, never silently. |
| Wax, native feed and native corpses stay dangerous in the warm, in stacks, in hands and across a reload. | Each carried from a cold room into a warm one; one saved halfway. | Splitting a stack or loading the save does not make it safe. |
| Loose blue ice keeps a closed hold cold through a power failure far longer than a repair takes. | Two matched holds with a heated room next door, one with ice and one without; the power cut. | The hold without ice crosses the wax's limit; the one with ice is still cold, with ice left, well after the repair is done. |
| Wax refined in a cold room is ordinary chemfuel; in a warm room the wax goes first. | The same bill run cold and run warm. | The finished fuel stacks, fuels and burns like any other. |
| A foreign animal that eats a native plant is visibly ill. | A crew pet and a dorrak fed the same fern. | |
| Drift piles deepest beside walls, doors and the hull and slows travel there until cleared or eroded. | A wall, a door and the ship through a drift storm; trips timed after the storm ends. | Trips timed in the storm prove nothing: the weather itself slows walking. |
| Ice fog cuts range and accuracy and slows movement while it lasts. | The same shot in clear air and in fog. | |
| The vrisk really flies. | Its flight state read while aloft (never a live capture: standing rule). | |

Settings: one switch per major feature, defaults as shipped, everything off leaves a cold empty ice plain with
ordinary animals (standing rule, every mod). A switch that says off must never make anything more dangerous: today
turning the vhaulk's heat gate off makes every death a detonation, and that is a defect.

## Shared machinery

**Featured here** (the Blue Desert is where each is vital and should be proven):
- **Things that go off when warmed, and carry that with them** (`RM_CompPlantCharge`, the per-species charge
  hediffs, `RM_ColdWax` with its ruin-then-wick, all in `BlueDesertLife.cs`). The propane lakes' ascendant Burner
  shares the krissek's death class.
- **Cold kept by stored ice** (loose-ice passive cooling; unbuilt, the built cold rack is its predecessor). Any
  cold cargo on the ship would use it.
- **Sand that buries** (Odyssey's sand grid under `RM_IceSandDrift`; the Moving Dunes and every sand biome share
  the grid). Here it is against the ship.
- **Fuel from the land** (wax to chemfuel at the vanilla refinery; the Abyss and the Chill already have refinery
  bills of their own).

**Merely active here:** wreck placement, salvage and weathering (`Wreckage`); fog that caps range (the same shape
as any blinding fog); real flight; the one sun from geometry, which on the nightside contributes nothing; exposure
film from weather (`EnvironmentalHazards`, switched off here); bone from butchery (`Bones`, which must not hand out
a warm-safe organic here); the ice and meltwater that `FlowWorks` drinks; the Empire's search and the visibility
dial; the ship's acoustic sounder; the passage of giants (`HugeThings`); the Night Horrors' crysalises.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**0.1.0, the stop**
- The land: old water ice, ice-sand drift that goes deep beside structures and the hull, ice fog, the Haze as a
  veil, static abandoned workings and ice-locked wrecks. (built, except readable workings with ordinary ice and
  salvage, which are owed)
- Ordinary mining of blue ice. (the mineable is built; today a block counter rolls for loot, which goes)
- The charge family: twelve native plants and ten native animals as cold-stable fuel; the warning and crack; chains
  through connected growth; safe cutting and grazing. (built; a warning that survives a reload is owed)
- The dorrak's hump, the krissek's halo and single blast, the vhaulk's three ways to die and its walk-off, the
  vrisk's flight, the rest as ordinary animals (murrek visible, dovvik a grazer, ossivel a herd). (built)
- Wax, feed and corpses that stay dangerous warm. (wax is built; corpses and feed are owed)
- The cold hold on loose ice. (owed)
- Wax to chemfuel in a cold room. (owed)
- The butane gut for foreign eaters. (built)
- Drift against the hull, cleared by hand. (the sand grid is built; proof that it goes deep is owed since
  2026-09-24)

**0.2.0, the stop with company**
- The murrek buried in fresh drift, flushed by digging, re-armed by every storm. (built)
- The ablation line giving something up while the crew watches: a crack, a shape under the ice, the payload.
  (built)
- The quarry that hands up a siege form. (unbuilt; needs the Night Horrors)
- A passing giant whose track exposes buried ground worth the risk of following (his answer of 2026-11-10).
  (unbuilt)
- The tame dovvik as a living minesweeper (approved by him 2026-09-28). (unbuilt)
- Tapping a living vhaulk at the valve. (unbuilt)
- Oskelloth, the oil-sheen crust that grows only beside the fallen: *"where the sheen is, the salvage is."*
  (unbuilt)
- Hazebells opening after the Haze. Char-lace from a burned kethevar, the one thing from here that is safe
  indoors. (built)
- The ship's acoustic sounder readings here. (built)

**Later (a crew that stays, or a colony)**
- Reading the warnings: the study ladder, the five epochs and their trailing translations, the full reading.
- The rites: the Returned and the Charged Reed (they live in the rites mod).
- The Haze as an exposure illness; ice fog grounding shuttles; the thunderbeast's storm toolkit; preserved roe as
  human food.
- A whole season of the food web holding together under blasts.
- Whether the ship's own Rakatan mind can read Rakatan warnings (new here; nothing in the sources).

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- The cold-cutting technique and any heat model on mining pace (his answer, 2026-11-10: *"it's just ice"*).
- The cold rack, its tint and groan (superseded by his loose-ice answer); the meltwater drip (cut 2026-10-23).
- The soundscape: the ossivel choir's silence alarm and the virr's rising pitch (cut 2026-10-23, *"pure audio at
  361 lines"*). The animals and the reed stay.
- The vhaulk's pressed rime road (cut 2026-10-23).
- The three donor water plants, grimpepper and the whole Earth desert zoo (ruled out 2026-09-28 and before).
- Sowing any native plant; any warm-safe native organic; rain; a Horrors settlement.
- The lobe mosaic, sector tables and tile counts (the planet is painted once, at the end).
- **Recommended for dropping, not yet his:** the block-counter thaw loot; the krissek's second, duplicate blast;
  milelace reseeding into drifts.

## NEEDS HIM

1. **Does a blast end the dark?** Nothing in the sources says. *Yes* (default here): a chain on a black plain is
   seen from orbit and the search starts as on open ground, so the crew's own carelessness is what finds them.
   *No:* the dark is free cover whatever happens, and the Blue Desert is the safest hiding place on the planet for
   anyone who can eat. *Only a large one:* a vhaulk, or a field, but not a single plant.
2. **Does the landing itself set off the growth under the ship?** *Not promised* (default): the first blast is
   something a Jawa did. *Yes:* every arrival opens with a ring of blasts around the hull, spectacular and
   unavoidable, and a first stop teaches the rule before the crew has a say. Needs the engine fact first.
3. **The campaign's two outsiders, the vapaad and the thunderbeast, have ordinary meat and leather in a biome whose
   law is that nothing is warm-safe.** Carried from the cleanse. *Keep both and owe them native bodies* (default).
   *Give them a stated exception.* *Take them off this biome's patch.*
