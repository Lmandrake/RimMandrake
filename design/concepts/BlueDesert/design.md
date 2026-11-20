# The Blue Desert: the design, seen from the ship

**Status:** the one design document for the Blue Desert biome (`RM_BlueDesert`, source `src/RimMandrake/BlueDesert/`),
rewritten 2026-11-18 on the owner's instruction to see every biome "through the lens of Utinni". It replaces the
older definition sheet, the life brief, the cast bible, the flora pitches, the reviews and the cleanse proposal as the
place to read; what happened to every idea in them is in `design/concepts/BlueDesert/rewrite_choices.md`. Nothing has
been deleted yet. The Blue Desert is not on the owner's hold list, but only the Pyrelands is advancing as a biome
mod: this is a design document only and it launches nothing.

**Second reader, 2026-11-18:** a second agent that did not write this page read the seven older biome files whole
and repaired it: the hull section now cites the built shield frame, the Horrors are stated as the night side's own
raiders, and several scenes took lines the first read had missed. What changed and why is at the top of
`rewrite_choices.md`. One thing the owner said on 2026-11-10 stands over this whole page: *"We likely need to revisit
this biome and do a full redesign pass."* This rewrite is an agent's attempt at that pass, not his approval of it.

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
them burning is very hard; when they do go, it is not a fire, it is an explosive chain reaction."* *"Everything alive
here lives two degrees on the warm side of a phase line. Two degrees the other way, and the propane pools"*: that is
the propane lakes, the next stop down, and the planet's replete fuel.

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

**Cover from orbit here: full dark, one step.** The Blue Desert never sees the sun. By his card of 2026-11-19
*"Full dark is one step, like fog"*, and nothing pauses the search for good. It gets no second kind of cover on top:
the sky is *"usually clear — much less shelter than the crags"*, and the ice fog hides the crew at ground level
only. As built, the pursuit's list of slowed biomes holds the Abyss alone, so the Blue Desert's step is owed work
(the shared partial-cover entry), not a fact of the game today.

**How long a stop lasts (the outer edge).** One step makes each wait about 1.4 times the open-ground figure. His card
puts a night-side stop at *"about six weeks"*, and the larder ends one about then too: nothing native is food for
the crew, and the heater eats fuel every hour. `UNSETTLED`: nobody has measured how long the ship's stores feed six
Jawa. This design treats **about six weeks** as the outer edge of a stay, set by the Empire, food and nerve, and
expects most stops to be far shorter: a salvage run of a few days. A season is fifteen days, so one regrowth of a cleared patch can be seen and little else
that is slow.

`Answered on 2026-11-19` 1 (see the end) answers that a blast chain, visible from orbit on a black plain, takes away the dark's step while it
lasts. That makes the biome's own signature the thing that gives the crew away. Without the step the stop runs on
the open-ground clock, taken from the Greentide design's arithmetic and not re-derived here: a probe
on day 5 to 8, a first real fight around day 12 to 20, the bombardment around day 20 to 32 if the Empire wins every
step.

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
landing does to the cells beneath it) and not promised as a design matter (`Answered on 2026-11-19` 2).

Before the first hour is out the player should have seen: transparent plants with the ice visible through them; an
old extraction face with somebody else's abandoned gear standing at it; and a herd of small pale grazers that
ignore the ship entirely.

## The first day

- **Clear before you work.** The answer he gave: cut the growth along the working route, carry its wax away from
  the exit, keep a way back to the ramp that no fuel touches. Cutting and harvesting a plant is safe; killing it
  with damage is not. *"A crew that clears a firebreak with knives is doing the right thing; a crew that clears it
  with a flamethrower is the sound in"* the sheet's last line (*"then the boom"*). A gap has to account for animals,
  corpses and carried wax as well as plants: a dead grazer on the path reconnects it. The plants grow slowly, so a
  cleared apron stays cleared for most of a stop; it is still worth a look before each trip out.
- **The field is a fuse.** *"The field is a fuse laid by the spawner"*: the floss underfoot carries a blast from
  plant to plant, a glassfern steps it up, and a chimeglobe *"restarts the whole thing."* The warning is for *"a
  warm room, not a warm breath"*: one gust from a blast nearby does not set off the next field by itself.
- **The ice is just ice.** An ordinary Mine job on the old face yields blue ice: *"mineable water-ice blocks of
  distilled-level purity"*, which he called *"golden"*. No special technique, no hidden roll, no penalty for
  swinging fast.
- **Everything else is fuel.** Every plant harvests to cold wax and every animal butchers to it. Wax is safe below
  freezing and ruins, then wicks, in the warm. So does a native corpse. *"You never bring one indoors"*, and
  bringing everything indoors is what Jawa do. A warming stack says so: it shows an "Overheating" figure climbing
  for a little over an hour before it lights (the life brief's arithmetic; tuning). Nothing here can be foraged:
  there is *"nothing a human can forage that will not detonate in a pack."*
- **Water, the Jawa way.** Blue ice melts to drinking water over a campfire or a stove (built: a melting bill).
  Where the crew lights that fire is the day's second decision.
- **The old workings.** *"Not the first time anyone thought of it."* An abandoned cut, with equipment, salvage and
  mineable ice, readable as an earlier crew's attempt without any letter or study. To a Jawa it is an unattended
  yard.
- **The fallen.** Wreckage locked in the ice, placed with the map: *"meteoritic metal, crashed wreckage,
  freeze-dried corpses that fell from orbit (the Empire's orbital holdings are the unwitting supplier)"*, *"free
  for the finding, guarded by whatever thawed beside it."* A wreck in the ice has to be mined free first (the
  salvage design's rule for this biome; the ice jacket is owed).
- **Follow the linewalkers.** The pickers gather where the ice gives things up: *"a dozen of them standing around a
  fallen hull or a freeze-dried spacer, working, patient, not interested in you unless you are lying down. The
  crews call them linewalkers and follow them to the good salvage."*
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
  explosion. Careless shooting in connected growth is a large one. The crews' own names for them are the warnings:
  the dorrak is a "cask" (*"The crews call them casks and give them the road. Nobody who has shot one in the belly
  has described it afterwards"*), the krissek a "torch" (*"never, ever go for the body shot"*). A krissek at rest
  is grey on grey ice; the fire shows only when it runs or fights, so colour means it has seen something.
- **The choir, without the alarm.** Ossivel stand at the line in dozens: *"the only proof for a hundred kilometres
  that anything is glad to be here."* (Their song and its silence were cut on 2026-10-23; the animals stay.)
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
3. **The right way.** *On screen:* the same giant brought down with slugs and blades, no fire anywhere. It is not
   patient work: the cast bible sets a wounded vhaulk to turn on its attacker every time, *"neutral until wounded;
   then the mountain notices you, slowly."* Then a house-sized cistern of fuel lying intact on the ice with six
   Jawa standing round it working out how to get it up the ramp cold. Done beside the ship, the wrong way is the
   source's own sentence: *"Kill it near your base and you have detonated a district."*
4. **The hump.** *On screen:* a dorrak shot in the hump goes up and takes the shooter's neighbour with it; the one
   shot anywhere else just falls over.
5. **Blue fire.** *On screen:* a krissek at full sprint with a halo of blue flame, *"the only warm light for a
   hundred kilometres"*, straight through the picket line; whoever kills it is standing next to it. They come in
   twos and threes: *"a pack of torches is the biome's set-piece."*
6. **The pantry.** *On screen:* the cold hold's stack shows its warning; somebody left the door open hauling.
   The crew can save it by shutting the door and taking the heat away, or can run. *"One cooling failure aboard
   and the pantry is a bomb."*
7. **The souvenir.** *On screen:* a dead picker carried proudly into the warm ship. A warning, a wick, a hauler
   reversing down the ramp at speed.
8. **The pet ate a plant.** *On screen:* one of the clan's gross little pets crops a glassy fern and is visibly,
   noisily ill with a gut full of butane. If it keeps eating, the source finishes the scene: it *"dies of it and
   takes the barn with it."* The sick pet is itself a charge until it recovers.
9. **Shovelling out the ship.** *On screen:* a stolen starship up to its landing gear in blue-white drift and a
   line of very small figures with shovels.
10. **The kite.** *On screen:* a vrisk, thin as a kite, really flying, skimming the Haze over the crew's heads.
11. **Tea.** *On screen:* a Jawa builds a campfire on the ice to melt a pot of the purest water on the planet,
    three paces from a lawn of floss. (A reading of built behaviour, not a source's scene: the melting bill is
    real and so is the lawn.)
12. **The live one.** *On screen:* a tamed native led proudly up the ramp into the warm. *"Bring one indoors and
    the room does the rest"*: it sickens with the heat, dies of it, and goes off in the corridor. And one blast in
    a closed room warms the room, which is how one pop in the hold becomes the whole hold.

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
- **The Horrors (the campaign's to deliver; the quarry link is 0.2.0).** The first read had these only as
  something mining might release. The Horrors' own sheet makes them the night side's raiders whatever the crew
  does: *"Players who land on the night side encounter them: the weapon on patrol comes out of the cold."* Here
  the weapon *"has degraded LESS than anywhere else"*: slow, patient, *"surfacing to hunt and to collect (the
  BroodLord still takes victims alive — samples for a master who no longer exists)."* His words for it: *"A
  semi-live version of the weapon slowly operating on the frozen darkside, showing its complex, alien, weaponized
  behavior far from the dayside."* They are never residents and never a settlement: *"delivered — by thaw, or by
  trigger"*; and the rule for how they may look here is *"the horror emerges from beauty and emptiness, never from
  a landscape that already looks like horror."* The forms in the ice are *"hardened for siege, building and
  vehicle attack"*, and a landed ship is a vehicle. *"A crysalis is a butane charge with a program"*, so a release
  beside growth is also a blast. The Night Horrors code owns all of it (crysalises that wake to nearness or
  warmth are built there); nothing links mining to them today, and whether their reach is the night side only is
  still marked for his confirmation on their sheet.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The larder: nothing here feeds a Jawa.
- The cold: the heater needs fuel, and the fuel must be made in a room the heater must not reach.
- A blast that takes the stores, or a pantry that goes.
- The drift, if digging out is left too long.
- A flare that ends the dark (`Answered on 2026-11-19` 1).

**Stay, longer than the Empire would like:**
- The dark itself. This is the quietest sky on the planet for a crew that shows no light and sets nothing off.
- Fog at ground level against a probe that has to *see* the ship.
- Fuel and water on the doorstep.
- A cleared apron that turns the plateau into the crew's own minefield.

## What the crew takes away

- **Blue ice:** the top grade of water on the planet, and the hold's own refrigeration while it lasts.
- **Fuel:** the slow route, and buying elsewhere (his fuel answer of 2026-11-19: the Blue Desert is not one of
  the richer sources). Cold wax from plants and carcasses renders to chemfuel in a cold room at the slow route's
  rate; in a warm room the wax goes first. The propane lakes, one step colder, are the replete source. Nobody here
  sells fuel, because nobody is here. The richer reading (the vashpuk well, a vhaulk as a tankful) is kept in the
  0.2.0 list as text.
- **Salvage:** meteoritic metal, wreckage, the gear at the old workings.
- **Wax as cargo,** to sell on the dayside, for as long as the hold stays cold. *"The phase-line physics travels
  with you."*
- **A cold-blooded pet,** if the crew tames a dovvik or a choir of ossivel, and can keep a room below freezing for
  it for the rest of its life, with qeshra roe in the cold hold to feed it. The source's warning: *"A tamed dorrak
  is a walking bomb in a barn, and a krissek pet is a torch in the kitchen."*

## What the place does to the ship

His ruling (card, 2026-11-18) puts hull wear in 0.1.0: *"most of the biome already talk about this... Heat or cold.
Different kinds of shields or armor. It's in there."* For the Blue Desert it is in there twice over. The frame is
`src/RimUtinni/ShipShields/` (his shield rulings of 2026-09-02, `design/Jawa/proposals/ship_shields_deep_design.md`);
this design adds no hull system and every wear below comes from a source. Nothing here is this page's invention.

- **Cold-seize (built in the frame).** The shield frame already treats outdoor cold of forty below as a hazard to
  an unshielded ship (`ShieldHazardUtility.ExtremeColdThreshold`, with the landing letter *"exposed systems will
  cold-seize over time"*). The sheet's median here is −42.6 °C, so most Blue Desert tiles trip it and the warmest
  (−19 °C) do not. The shield answer is his cryo envelope: *"Pulls in heat in both directions and allows the
  shields to start glowing with red-orange black body radiation, holding severe cold at bay. But slowly decreases
  the temperature within the ship... still better than the extreme cold of the night-side atmosphere."* The shield
  design makes a cold trip *"expedition-shaped: fuel committed up front, no casual hop in and out."* The answer by
  hand is the one Jawa would reach for: heaters, closed doors, and patching what seizes. `UNSETTLED`: whether an
  envelope that pulls in heat warms the growth round the hull (assumed not). `Answered on 2026-11-19` 5: whether a hull glowing
  red-orange on a black plain can be seen from orbit.
- **Blown ice sand (built in the frame, by its signal).** The frame's third hazard is any weather that carries
  sand (`sandRate` above zero), and the ice-sand drift rides exactly that field, so a drift storm should foul an
  unscreened ship as a dust storm does. `UNMEASURED`: nobody has watched it do so here. The shield answer is the
  light screen, which by his words handles *"wind, ash, vapor, bio contamination, spores, smoke, sand, and rain
  damage completely."*
- **Drift against the hull (the ground under the ship; owed).** Ice sand piles against the grounded hull (ruled
  into the slate on 2026-09-28: *"drift burial of a landed gravship"*, *"costing a dig-out on departure"*, to be
  tuned so it *"reads as weather, not tax"*). No field answers it: *"Slow pressing things move through all
  shields."* The answer is hands and shovels. The engine gives a deep drift a heavier walking cost, never a wall,
  and no sand under the hull itself, so the drift slows every trip to the ramp and never traps the ship. What an
  undug hull costs at launch is for the shared hull-wear rules to state; this design promises only that the drift
  is deep, is against the hull, and can be cleared.
- **Blast.** A chain reaching the hull damages it like anything else. The heavy field is the frame's answer to
  *"impactors, blaster fire, and large animal assault"*; the crew's answer is the cleared apron.
- **The warm ship, the cold hold.** The crew quarters must be warm and the hold must not be. Two rooms and a
  closed door. In flight the cargo's warming does not reset: loading it, carrying it or leaving the map is not
  refrigeration.
- **Fog** does not ground the ship in these versions. (The fog weather as built does forbid a shuttle launch; that
  switch is in "later".)

The frame sends one letter on landing and never refuses a landing (his ruling: *"no environment is immediately
lethal"*). Under the shared rules proposed for every biome, each wear here shows a sign before it costs, is a bill
that grows and never a wall, and ends at launch.

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
| Wax refined in a cold room is ordinary chemfuel; in a warm room the wax goes first. | The same bill run cold and run warm. | The finished fuel stacks, fuels and burns like any other. |
| Drift piles deepest beside walls, doors and the hull and slows travel there until cleared or eroded. | A wall, a door and the ship through a drift storm; trips timed after the storm ends. | Trips timed in the storm prove nothing: the weather itself slows walking. |
| Ice fog cuts range and accuracy and slows movement while it lasts. | The same shot in clear air and in fog. | |
| The vrisk really flies. | Its flight state read while aloft (never a live capture: standing rule). | |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| A foreign animal that eats a native plant is visibly ill. | A crew pet and a dorrak fed the same fern. | |
| Loose blue ice keeps a closed hold cold through a power failure far longer than a repair takes. | Two matched holds with a heated room next door, one with ice and one without; the power cut. | The hold without ice crosses the wax's limit; the one with ice is still cold, with ice left, well after the repair is done. |

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

**The one signature (his first-version answer of 2026-11-19): the charge.** Every native plant and animal is fuel
that only the cold keeps quiet. Warmth or damage makes it warn, crack and blow; the blast runs through connected
growth and into cargo; a prepared gap, safe cutting and cold handling are the answers. *Why a normal stop is sure to
see it:* the ship lands warm on a field of charges, and its first heater, fire, kill or careless cut warms one on the
first day of work. His experience line names it: *"Mine slowly and carefully or risk your own passion's heat turning
everything into a bomb."* *Runner-up:* the ablation line giving something up (study, siege forms), already 0.2.0.

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
- Wax to chemfuel in a cold room. (owed)
- Drift against the hull, cleared by hand. (the sand grid is built; proof that it goes deep is owed since
  2026-09-24)

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The butane gut for foreign eaters. (built)
- The cold hold on loose ice. (owed)
*Already here before that answer:*
- *Not chosen as a richer source (his fuel answer of 2026-11-19); kept as text, his to bring back by name:* the Blue
  Desert as a fuel stop. *"A chemfuel windfall that explodes if you warm it."* An amber vashpuk bladder regrows
  after tapping, *"a renewable cold-wax well"*, refilling in about ten days, so a long stop taps it two or three
  times: *"a fuel well that is also a bomb you must never let warm."* One vhaulk taken the hard way is a tankful.
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
- The kuvvel, the Watchers kit's animal for this biome: a drift-sitter with one eyestalk above the ice sand that
  sinks when a murrek is buried near it, so *"a drift whose kuvvel all sink holds one."* It belongs with the buried
  murrek and comes or waits with it. (designed in `design/RimMandrake/watcher_creatures_pitch.md`; unbuilt)
- The dovvik as first written, the "defuser": it taps a plant and leaves *"drained glass, inert"*, so *"a
  dovvik-cleared field is safe to walk warm."* This is the safe-trail idea's root and goes with the minesweeper
  above.
- Hazebells opening after the Haze. Char-lace from a burned kethevar, the one thing from here that is safe
  indoors. (built)
- The ship's acoustic sounder readings here. (built)

**Later (a crew that stays, or a colony)**
- Reading the warnings: the study ladder, the five epochs and their trailing translations, the full reading.
- The rites: the Returned and the Charged Reed (they live in the rites mod). His ruling of 2026-10-23 made every
  found rite of the Nine, these two by name, a matter for the second release (`design/RimMandrake/v2_nine_rituals.md`).
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
- The three donor water plants, grimpepper and the whole Earth desert zoo (ruled out 2026-09-28 and before); the
  boomalope with them (his card, 2026-09-14: *"Absolutely no boomalopes"*).
- Sowing any native plant; any warm-safe native organic; rain; a Horrors settlement.
- The lobe mosaic, sector tables and tile counts (the planet is painted once, at the end).
- **Recommended for dropping, not yet his:** the block-counter thaw loot; the krissek's second, duplicate blast;
  milelace reseeding into drifts.

## NEEDS HIM


None open. Every entry is answered (next section).

Themes, for gathering these across biomes: 1 cover · 2 hull · 3 other · 4 cover · 5 hull · 6 other.

No ship idea of his was found declined for this biome. The two cut ship-side details are already on the dropped
list: the rack's meltwater drip (cut 2026-10-23) and the rack itself (his own later answer).

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. **Does a blast end the dark?** Yes, for a while: after a blast the search runs as on open ground (the design's
   default). *Delegated call.*
2. **Does the landing itself set off the growth under the ship?** Not promised. Measure what the engine does first
   (the design's default). *Delegated call.*
3. **The campaign's two outsiders, the vapaad and the thunderbeast, have ordinary meat and leather in a biome whose
   law is that nothing is warm-safe.** Keep both, and owe them native bodies (the design's default). *Delegated call.*
5. **Does a hull glowing with the cryo envelope give the ship away in the dark?** No in 0.1.0: the envelope's glow is
   not built. Ask again when it is built. *Delegated call.*
6. **What is the Blue Desert's deck part now?** *His ruling:* his answer of 2026-11-10, *"no rack needed"*. The later
   word wins: the Blue Desert gives the ship a room and a habit, not a part.

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

4. **Is the plain night side "full dark"?** *His card of 2026-11-19 (cover):* full dark is one step, like fog, and
   nothing pauses the search for good. **This changes the design's default.** Was: a full pause. Now: one step of
   cover, a stop of about six weeks at the outer edge; the clock section above says so.
