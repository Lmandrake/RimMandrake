# The Forge: the design, seen from the ship

**Status:** the one design document for the Forge biome (`RM_TheForge`, source `src/RimMandrake/TheForge/`, with its
shared kit in `src/RimMandrake/EnvironmentalHazards/`), rewritten 2026-11-18 on the owner's instruction to see every
biome "through the lens of Utinni". It replaces the older definition sheet, review, cast bible, kit specification
and cleanse proposal as the place to read; what happened to every idea in them is in
`design/concepts/TheForge/rewrite_choices.md`. Nothing has been deleted yet. This is a design document only and it
launches nothing. A second reader checked it against the sources on 2026-11-18 and repaired the hull, fuel, scope and
`NEEDS HIM` sections; what changed and why is at the top of the choices page. A third run the same day read the
roster file to its end; it changed two facts here (the tibidee is wired; the date of the lava snail's cut).

**Kind, checked against the sheet's own header:** land. One volcanic massif, *"the only vertical skyline in the Dune
Sea."* It has lava, not a sea; the seabed rulings do not apply.

**Who reads this next:** a Designer run on this concept is handed the list of files in `design/concepts/TheForge/`
(`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in its path by sitting here. Nothing in
the pipeline reads it by name yet. The Forge has no locked sheet or tree; its only pipeline material is the cleanse
proposal of 2026-11-17, which this design supersedes and which was never applied.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means the
census of 2026-11-17 (`cleanse/census.json`) found it in source; it does not mean it has passed anything.

---

## What this place is

> *"Dark foundry towers rising defiantly against the sun, over herds grazing the smoke."* (`the_forge.md`, header)

One mountain. Red seams and open lava below, ash skirts around, tall dark towers above, and over all of it, floating
in the columns of vapor, herds. *"The mountain rains on itself in scalding bursts."* On a world where every joule
belongs to the star, *"vulcanism is the one heat that owes nothing to the sun."* The sheet's name for it is *"the
only unstolen fire."*

The owner's line for the experience, typed 2026-10-20:

> *"Where the gods came to forge a world is now the ruins that seek to unmake you. Even the beasts challenge your
> presence."*

**Seen from the ship, the Forge is a clock the crew has to learn before it kills them, and it runs fast enough to
learn.** The whole place turns on one cycle, built and measured in source: two or three days of still heat; a hiss;
gas that burns off every exposed plant; hours of boiling rain; and then the lava itself crusts over, gardens of
light stone ripen on the crust, the crust cracks, and it all goes back to lava. One turn takes five to seven days.
A stop sees it several times. The cleanse proposal put the lesson well: the crew *"learns the difference between
ground that belongs to it and ground it is borrowing."*

The cycle is his. He typed it on 2026-09-29: *"This is a biome of fire and water. The open lava is horrible, hot,
deadly. The occasional washes of superheated gas burst ignite much of the map. Then the torrential rains pour down,
causing flooding. There should be huge plumes of steam and transformation of the lava vents to temporary basalt
shingle and pumice chunk."* And the end of it: *"Eventually glowing cracks form on the rock covering, and the whole
thing melts back into lava again, destroying them."*

For this crew there are two more things. The sheet says whose mountain it is to them: *"the Jawa sacred geography
sees Sh'kaar's forge — the war-sun's anvil."* They are parking a stolen ship on their own god's workbench. And the
sheet says who else is here: *"The Empire holds the tibanna harvest over the heads of all — a garrisoned gas-mining
station working the herds."* The people chasing them already have an address on this mountain.

The crew are heat people. The air here will not shock them. The rain will.

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought.

**The outer edge of a stay here: about six weeks.** By the owner's word of 2026-11-18 the figure a design derives is
*"the outer edge allowable"*, not the typical stay. If the Empire wins every step, the bombardment is the fourth
full interval of the ladder: 28 to 45 days at one step quieter than open ground, which is what this mountain gets.

**Cover from orbit: steam and ash, one step.** His ruling of 2026-11-18: *"Canopy, steam and fog slow the search by
one step."* The Forge is the planet's steam engine: vent columns *"streaming vent-steam like banners"*, red fog, ash
fall, and the fog off every quench. It hides nothing at ground level for long; the towers are *"visible for a
hundred kilometers."*

**`UNSETTLED`: what it means to land beside the Empire's own station.** The gas operation is the campaign layer's
(`design/Jawa/tibanna_embargo_plot_spec.md`; its build is owed). Whether a ship that lands on this mountain is
found sooner because the garrison is in sight is not written anywhere. The ordinary search applies (`Answered on 2026-11-19` 1).

---

## The first minutes

The towers are in view from the air long before the ground is. The ship comes down through steam onto a dark bank
between red seams. An arrival note says the three things a newcomer has to know: the rain here scalds and a roof
stops it; shade is only shade; the hot air is ordinary hot air and has to be managed like any other.

The crew looks around and sees, in order: a tower footing they have to walk round, plainly *made* and not a rock;
lava, open, a few steps from the ramp; a herd of round pale things drifting in a column of vapor overhead; and, down
in the melt, something that glows the same colour as the lava and is moving slowly and on purpose. *"Nothing lives
in the lava — but there is movement there."* It is a machine. What it is doing is never told.

## The first day

- **Still heat.** Most of the time nothing happens. Flash plants sit sealed. The banks are firm and can be built on.
  Lava is lava, with the game's ordinary rules for it.
- **The works.** His answer of 2026-11-10: *"Old works shape ordinary journeys."* Towers are whole, permanent and
  cannot be entered, mined or salvaged. Broken remains around them can be.
- **The herds.** Bulloos, small and great, float in the vapor columns and feed on the vapor itself. Fleet fliers
  dart in to eat and out again. A jossur rides the updrafts above them and hunts: *"The columns are pasture, and
  every pasture gets its wolf."*
- **On the ground,** few and tough: the dhoggur, a placid ash-forager, in his words of 2026-10-16 *"a bizarre
  creature that constantly snuffles and digs at the ashy minerals freshly deposited by volcanic sputter. Very tough
  heat resistant hide"*; a slug that eats metal; and along the lava's lip, the ummisk, a colony of tubes riding a
  cushion of its own steam.
- **A short burst.** Even in the still phase the mountain throws brief showers of boiling rain. A crew member
  caught outside is hurt, not killed, and learns to look for a roof.

## The first week: one turn of the mountain

1. **The hiss.** About an hour and a half of warning. His answer: *"Recall before gas."*
2. **The gas.** A wash of it ignites every exposed thing that can burn. Bare bank does not burn.
3. **The rain.** Hours of it, boiling. A roof stops it. Everything unroofed is scalded. *"Mosses drink in the
   seconds between fall and flash"*: the flash plants open and grow at a rate they never otherwise reach.
4. **The mountain wakes.** *"Half the outcrops on the skirts are stone. The other half are waiting for rain."* An
   outcrop that has been in view since landing unfolds and stands up. It is a dhokkur, a plated giant that drinks
   the rain and sleeps as stone the rest of the time. *"It is not angry. It has never needed to be."* Julmox,
   *"a row of dull kettles on the skirts"* until now, fan out to crop the wet growth: *"Pasture is wherever it last
   rained."* Knuckle-sized dhuvvox uncurl from nodules in the ash that anyone would take for slag. *"The old hands
   tell time by them. When the dhuvvox run, you reap; when they still, you are already late for shelter."*
5. **The crust.** The rain quenches the lava. A skin of basalt and pumice forms over it, firm enough to walk.
6. **The gardens.** On the crust, floatstone gardens seed and ripen: lace-walled globes of a stone that is light,
   strong, will not burn and is good to look at. The stone is his, typed 2026-09-29: *"Ultra-light pumice made of
   what looks like spun glass whirled into tangles. Super strong and light building material, not flammable, quite
   valuable, and the walls it makes look like swirled stone spun sugar made into blocks. Very beautiful."* They are
   cut like any plant and carried to the bank. *"A block of floatstone weighs what a lie weighs."* This is the
   expedition: two days and more of borrowed ground.
7. **The cracks.** The crust starts to glow along its seams. The deadline can be read at any time. Gardens nobody
   cut lift off in a puff of dust and are gone, *"the one form the lava never gets back"*, with a count of what was
   lost. His answer: *"orderly retreat before
   melting... loads may be abandoned and delayed rescues remain risky."*
8. **The melt.** It is lava again. Whatever was still on it is gone, and the game says what.

Then still heat, and round again.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **One more globe.** *On screen:* cracks glowing all round a crew member who is still sawing at a floatstone
   garden, a second one waving from the bank. *Why it is very Jawa:* it is free, it is right there, and there is
   always one more.
2. **The rock stands up.** *On screen:* in the first minutes of the rain, a boulder beside the salvage pile groans,
   sheds dust, and is a thing the size of a hill, pouring water off its plates, walking.
3. **The hiss.** *On screen:* every Jawa on the map drops what it is carrying and runs for the ramp. A moment later
   every shrub outside is burning.
4. **The floor uncurls.** *On screen:* the ash a crew member is standing on turns out to be hundreds of small sealed
   things, and they all wake at once.
5. **The machine nobody can have.** *On screen:* a crew of scavengers lined up at the lip of a lava seam, watching
   a working machine walk through the melt. They cannot reach it, strip it or sell it. They watch anyway.
6. **Herds grazing the smoke.** *On screen:* a great bulloo, feelers trailing, drifting through a column of vapor
   over the ship like a slow balloon; a jossur falling on a fleet flier behind it.
7. **The garden leaves.** *On screen:* the last uncut globes lifting off the cracking crust in dust, and a message
   counting them.
8. *(0.2.0)* **Don't poke it.** *On screen:* a Jawa prods the placid dhoggur. It swells to three times its size and
   spits fire. (Owner, 2026-10-16.)
9. *(0.2.0)* **It ate the scrap.** *On screen:* the metal-eating slug in the middle of the crew's salvage pile, and
   less salvage.
10. *(0.2.0)* **The giant has a road.** *On screen:* the dhokkur walks the path it has walked for a thousand rains.
    The crew's tent was on it.
11. *(campaign layer)* **A blade for the anvil.** *On screen:* a Jawa at the lip of a lava lake throws its own
    weapon into the melt, in front of the rest of the crew. The rite is the Anvil Gift, kept by the owner
    2026-10-02, and its inscription is found hammered into an obsidian slab: *"This is where the sun hammers. Give
    him a blade and he will not come for yours. For a while."* *Why it is very Jawa:* the god is theirs, the
    mountain is his, and the price is a thing they could have sold.

## When the Empire arrives

- **They do not know the clock.** A strike team that walks in during the still phase is walking on ground that will
  hiss, burn and boil on a schedule the crew has read all week. A cordon needs two days standing. If it is set up
  on crust, it has two days and a bit.
- **The rain does not care about armour that is not heat armour.** Scald uses the game's ordinary heat-armour
  rating. Whoever is unroofed is scalded.
- **The gas burns what can burn,** including a siege camp's stores.
- **Lava is a wall.** Seams and pools cut the map into banks. A crust crossing is a bridge that exists for part of
  the week, for both sides.
- **The towers are cover that cannot be destroyed** and shade that moves with the fixed sun's geometry. Their shadow
  is not a roof.
- **Steam is everywhere,** and fights are close.
- *0.2.0:* moving steam fronts roll across the ground after a quench; his answer of 2026-11-10: *"Walls stop the
  immediate front; roofs alone offer little protection from sideways steam."* The dhokkur walks its road through
  whatever is on it.

## Who else attacks; who hates the Empire

- **The beasts,** as his line says. The jossur hunts what it can carry off. A native that is hurt may turn on
  whoever hurt it. Nothing here is hostile by nature and nothing here is harmless.
- **The Empire is already here.** *"Watching their ammunition slowly run out with a smart grin."* The station, its
  garrison and the embargo's clock are the campaign layer's.
- **Who hates the Empire: everyone with a blaster.** *"The situation must resolve soon, or those who resist will
  have no guns to speak back."* Tibanna, the gas every blaster burns, comes only from the beldon herds over this
  mountain (*"no tibanna source but the beldons"*), and the Empire meters it. A crew that milks a beldon under the
  garrison's nose is doing something the whole planet wants done. Campaign layer; a review of 2026-09-28 reports the tap shipped
  there. Two rulings of 2026-09-12 shape it. Taming a beldon is *"brutal-but-possible"*: *"breaking the monopoly is a
  campaign act, not a pen."* And the embargo's clock has two ends: the crew can break the meter (an assault or heist
  on the station; the garrison *"must be beatable"*), and if nobody does, the Empire wins the clock and the
  resistance goes quiet.
- **The Deep Desert Tribes** climb the ash to see the fire once. *"Pyrelands fire is collected; Forge fire is only
  witnessed."* They take nothing and they are not the Empire's friends. Campaign layer.
- **The tenders in the melt** take no side that anyone can see.
- **The Contagion** *"will often push into this place and die, always testing."* Its dead red ring at the skirts is
  the one border on the planet it cannot cross. *"You can watch it lose."*

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The larder. *"Heat-adapted and few"*: there is hunting and some grazing, and not much of either.
- A bad turn of the cycle: a fire that reached the stores, a crew member lost on the crust.
- The neighbours.

**Stay, longer than the Empire would like:**
- A roofed camp on permanent bank. The cycle cannot touch it.
- Floatstone, which does not burn, for everything outside.
- Steam overhead, one step slower above.
- Knowing the clock, when the people hunting them do not.

## Fuel, and the hull

**Fuel: the emergency route in play; a richer source on paper.** The campaign's fuel ruling of 2026-08-15 names
*"helixien gas (volcanic/deep-desert tiles)"* among the paths to fuel, and this is the planet's one volcanic place.
The sheet's own list of what the Forge uniquely gives says *"free heat"* and *"the vents — the vapor law's richest
taps"*, and does not say fuel. Nothing in this mod taps gas for the ship. So in play today the Forge gives only the
slow rendering of plant and carcass that every biome allows, and less of it than most, because the gas wash burns
the plants every turn. The one idea in the sources that made this *"the best refuel stop on Ash'karr and the most
uncomfortable one"* (a heat exchanger feeding the ship's engine from a vent) was struck by the owner before he
stated the ship lens; it is the first question under `NEEDS HIM`. **Where fuel is bought:** nowhere a fugitive would
want to ask. The only station on the mountain is the Empire's.

**Tibanna is not fuel.** The embargo's own law: *"Tibanna is not propane."* It is blaster gas; *"no conversion route
exists in either direction."* A hold full of poached tibanna buys fuel somewhere else. It does not burn in the engine.

**Power is the thing this mountain gives free.** When he struck the vent machines on 2026-09-29 he kept the plain
version: *"lets just keep vent-based power as an option (already present in game)."* The game's own geothermal
generator, on the densest geyser field on the planet. It matters for the hull, below.

**The hull: lava, heat, ash and rain.** His ruling of 2026-11-18: *"Hull wear: Yes in 0.1.0. It's easy, and most of
the biome already talk about this."* The frame is built: `src/RimUtinni/ShipShields/` (his eight shield rulings of
2026-09-02, recorded in `design/Jawa/proposals/ship_shields_deep_design.md`). This design adds no hull system. Every
wear below has a source, named beside it.

- *Setting down on lava (0.1.0; built, in the campaign tier).* The one landing he named: *"Landing on lava should be
  the worst case causing immediate severe damage (don't do that)."* The frame fires one burst at the moment of
  landing, and no shield setting prevents it. `UNSETTLED`, read from source and not run in a game: the check
  (`HasLavaAtLanding` in `ShieldHazardUtility.cs`) looks for lava anywhere on the map, not under the ship, and
  every Forge map is generated with open lava. As written, every landing on this mountain would take the burst
  wherever the ship sits. His words describe a mistake the pilot can avoid; this design reads them that way (the
  burst is for a ship set down on or against lava), and the difference is filed as
  `RIMMANDRAKE_NARROW_LAVA_LANDING_BURST_WHOLE_MAP_SCAN`.
- *Heat (0.1.0; built).* The frame wears the ship's own structures while the map is in extreme heat and no shield
  covers it, with an advisory letter and never a refused landing. Its design names *"any volcanic-tile approach"*.
  The answer he ruled is the **thermal veil**: *"It would reflect all external heat outward with a mild mirror
  sheen to the shield, but also reflect all internal heat inward, so the temperature slowly climbs anyway... but
  not nearly as badly as it would in an active fire/volcano. Just use power for fuel."* Here the power is free.
  `UNMEASURED`: the tracker calls a map hot at 58 °C outdoors, in a heat wave, or under the game's own lava-flow
  condition. The sheet measured this ground at 42 to 56 °C, so on some Forge maps the built heat wear would not
  fire at all. Nobody has read it in a running game, and no bar pins the number.
- *Ash, steam and boiling rain (ruled; the frame cannot see them yet).* His light screen *"handle[s] wind, ash,
  vapor, bio contamination, spores, smoke, sand, and rain damage completely as well as repels small animals."* The
  built tracker knows a particulate hazard only as pollution or as weather that carries sand. No weather this mod
  ships sets that field (measured by search of `src/RimMandrake/TheForge/`; the donor ash weathers were not read:
  `UNMEASURED`). So today the rain phase and the ash fall do nothing to a ship, shielded or not. Teaching the
  frame the Forge's rain phase is the build; it is in 0.2.0 with the question under `NEEDS HIM` 3, because the
  one source that put rain on the hull was struck.
- *Fire (0.1.0, ordinary systems).* The gas wash lights what will burn. Outside fittings and stores on the apron
  burn like anything else. By the kit's specification scald is dealt to unroofed pawns, not to buildings: a crew
  member on deck is scalded and the deck is not.
- *Borrowed ground (0.1.0).* The crust returns to lava and destroys or burns whatever stands on it, with a count.
  A ship must sit on permanent bank. (`UNMEASURED`: whether the landing picker can put a ship on crust at all. If
  it can, the melt warning has to name the ship.)
- *The armour: floatstone (0.1.0; built).* On 2026-09-24 he asked of every biome *"how can this biome uniquely add
  something to the ship?"* The Forge's answer on record, by his card of 2026-10-03, is the **spunstone hull and
  the floatstone door**: *"Gravship hull laid from floatstone in the grain... Pearl-white, airtight, and far
  tougher than its weight has any right to be"*, and a door *"so light that a push swings it wide and it falls
  shut on its own weight a breath later."* Both are built, behind a study of ripe gardens (about three study sessions, by the
  build's own note). Floatstone does not burn, so a hull of it is the mountain's own answer to the
  gas wash. The first read put this in 0.2.0; the second reader moved it to 0.1.0, because the hull is in 0.1.0
  by his ruling and this is the only armour the sources give the Forge. `UNSETTLED`: how many trips onto the
  crust a meaningful piece of hull should cost. A garden gives one block and a hull cell takes seven; the
  Designer rehearsal drafted that question for him and it was never asked.
- *Declined, and not revived here:* **the scour** (*"every burst scours the parked ship (minor exterior
  damage/ash filth on unroofed ship tiles during boiling rain)"*, struck 2026-09-29 with the heat exchanger it
  came with) and **the floatstone keel brace** (a brace threaded through the ship that saved launch fuel and rang
  like glass at launch; he picked it by card from a consult of 2026-09-30, it was built, and it was cut on 2026-10-23 under his
  *"I cut, you veto"* card as *"small effect; the only ship hook"*; restorable by reverting one commit). They are
  the third question under `NEEDS HIM`.

## What the crew takes away

- **Floatstone:** building stone that weighs little in the hold; and, studied, a hull and a door for the ship.
- **Dhokkur hide,** from the one giant, if the crew dares: heat-shielding.
- **Julmox,** tame, as a herd that knows how to sit out a rain.
- **Firevine wood,** and what the flash plants give.
- **Salvage** from the broken works.
- *0.2.0:* blue gel from the bulloos. *Campaign layer:* tibanna; and **zersium**, the ore that turns steel into
  durasteel on the ship's alloy forge. By his cards of 2026-10-09 it is a rare local ore with one home biome, and
  that biome is this one: *"I like the forge makes that mineral."* It is built in the campaign tier. A live read
  the same day found most new Forge maps carried none, so its placement is owed a retune.

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The mountain reads as made: whole towers that change a walk, broken works to salvage, and something that is not alive moving in the lava. | An ordinary wood trip from the ramp on a generated map. | A tower that can be mined, entered or destroyed fails. So does still lava. |
| The cycle turns by itself, in order, and can be read at any time: what phase, how long. | A week with nobody touching anything; a save and reload mid-phase. | The same week with the cycle's setting off shows none of it and leaves no hazard behind. |
| A hiss gives time to get under cover before the gas; the gas burns exposed plants and nothing on bare bank. | Workers at the far end of the map when the hiss starts. | A map with nothing flammable outside: nothing burns. |
| Boiling rain scalds the unroofed and not the roofed; a healthy adult caught in a short burst is hurt, not killed. | Four pawns: open, tower shadow, parasol, roof. | The tower shadow does not stop the rain. Heat armour reduces it. |
| The rain crusts the lava; the crust can be walked and built on; gardens seed only on crust and ripen without help. | Follow one patch of lava from rain to cracks. | A garden placed by hand proves nothing; it has to seed by the cycle. |
| Floatstone cut on the crust and carried to the bank builds ordinary walls that do not burn, and a stack of it weighs less than stone. | One trip, cut to wall; a fire test against a wood wall; a carried-weight comparison. | |
| Cracks warn; uncut gardens leave with dust and a count; the crust returns to lava and what was left on it is lost with a readable account. | A crew that leaves on the warning, one that leaves late, a crate left behind. | No pawn vanishes: a body or a located loss, every time. |
| The rain wakes the dhokkur, the julmox and the dhuvvox, and they seal again after. | Watch one of each through a turn. | The same animal after reload is the same animal. |
| A dhokkur asleep reads as an outcrop until it wakes, and wakes with a groan, dust and water. The sources allow it one quiet tell: *"the gutter-lines converge too regularly for stone. The tooltip lies; the sprite may only whisper."* | A fresh crew walking past one before the first rain. | |
| Bulloos float in the vapor columns and are fed by them; away from a column they need ordinary feed. | A wild herd over a vent; a tame one led away. | A bulloo with no column and no feed starves. |
| The fliers fly, by the flight state. | A state read of the fleet flier's and the jossur's flight trackers (never a live look without the owner). | |
| The jossur hunts; a hurt native can turn. | A jossur with a small colony animal in reach; a provoked julmox. | A roster where nothing can hurt anyone fails his line. |
| Fire reaches the parked ship's outside like anything else's, and a bare apron keeps it off; a crew member on an open deck in the rain is scalded. | A ship with stores on an open apron and one with a bare apron, through a turn. | |
| A crew that studies ripe gardens learns to lay a floatstone hull and hang a floatstone door on the ship, and neither burns in the gas wash. | Researchers at ripe gardens through one growth phase; then one hull cell and one door built aboard; then a gas wash. | Before the study the two are not offered. A wooden fitting beside them burns. |
| A ship set down on or against lava takes immediate severe damage, once, with a letter that says why; a ship set down on bank well clear of lava does not. | Two landings on one Forge map. | The second landing is the control: as written today it would also take the burst (see the hull section). |

Settings: one switch per major feature, defaults as shipped, everything off leaves a hot volcanic map with towers on
it (standing rule, every mod).

## Shared machinery

**Featured here** (the Forge is where each is vital and should be proven):
- **A place on a phase clock** (`RM_GameCondition_ForgeCycle`, with the shared weather-pulse and flash-window
  machinery in `EnvironmentalHazards`): warned phases, saved deadlines, terrain that changes owner and changes back.
- **Temporary ground** (owned crust over lava, and what happens to things on it when it goes).
- **Animals that are terrain until the weather says otherwise** (`RM_CompForgeCycleDormancy`).
- **Vapor as pasture** (the shared column field; herds that float in it and feed on it).
- **Rain that is a hazard and a harvest window at once** (scald on the game's heat armour; flash growth).

**Merely active here:** the one sun from geometry and tower shade (the per-biome heat still in source has to go);
real flight; the growth engine, which must run together with the flash window; wreck salvage for the broken works;
bone from butchery; the ship's scanner; fire by the game's own spread; the Empire's search and the visibility dial.

## Scope

Every feature is in one bucket. "Built" is the 2026-11-17 census, not a pass.

**0.1.0, the stop**
- The land: volcanic ground, permanent banks, lava seams and pools; still heat, boiling rain, red fog and ash;
  vapor columns that can be seen. (built) Whole towers and salvageable works on ordinary maps. (unbuilt) Machines
  moving in the melt. (unknown)
- The cycle: still, hiss and gas, rain, crust, gardens, cracks, melt, with its warnings and its arrival note.
  (built)
- Floatstone as ordinary building stone. (built)
- The life: flash plants and firevine; dhokkur, julmox and dhuvvox waking with the rain; bulloos small and great,
  fed by vapor; fleet flier and jossur; dhoggur, metal-eating slug as an ordinary forager, ummisk. (built; vapor
  feeding is not)
- The dhokkur's wake as a show: groan, dust, pouring water. (built; moved in, see `rewrite_choices.md`)
- Fire on the parked ship's outside; melt under anything on crust. (ordinary systems)
- The shield frame's wear here: the lava landing and extreme heat, with the thermal veil as the answer. (built, in
  the campaign tier; the lava check is filed as too wide)
- Studying the gardens; the spunstone hull and the floatstone door, the Forge's gift to the ship by his card of
  2026-10-03. (built; moved in by the second reader, see `rewrite_choices.md`)

**0.2.0, the stop with company**
- The dhoggur's swell. The slug's metal diet. The jossur's stoop. (built)
- The dhokkur's roads and what it does to things on them. (built)
- Moving steam fronts after a quench; flooding in the rain. (built)
- The swarm of extra dhuvvox in the rain, and their countdown. (built)
- The four phase voices: the sound of the mountain. (built)
- Bulloo gel and bulloos that split. (built)
- Ash and boiling rain as wear the shield frame can see, and the light screen as the answer. (unbuilt; asked)
- A watcher: the zhaskel, *"an ember-dark plated sitter in cooled-crust fissures"*, pitched under his 2026-10-08
  ruling that every biome gets one and never admitted at a sitting. (unbuilt; a proposal)
- The two giants he said to wire in on 2026-09-29 (*"Wire in all waiting"*): the tibidee and the great aerofleet,
  now the greater bulloo. (the greater bulloo is built; the tibidee is wired in the campaign patch, `WildAnimals_TheForge.xml`)
- The scanner's readings here. (built)
- Campaign layer: beldons and the tibanna tap; the Contagion's testing ring; one floor of a foundry tower as a
  dungeon over open melt, *"richer or cooked"*. (ring built; the tap reported shipped 2026-09-28 and marked unknown
  by the census; towers unknown)
- Campaign layer: zersium ore for the ship's alloy forge (built; placement owed a retune); the Anvil Gift, a rite
  to the crew's own god at a lava lake (kept by him 2026-10-02; build state not checked).

**Later (a crew that stays, or a colony)**
- The embargo's clock, the station and the resolution he ruled must come: campaign.
- Two faiths, one mountain, as content. The second Forge rite, the Flawed Masterwork (kept, pending an engine
  check), which needs a masterwork and a vent forge.
- Breaking the meter, or the Empire winning the clock (both ends ruled 2026-09-12).
- Geothermal work beyond what the game already gives; learning the towers' craft and carrying it away.
- Fungus as a study source. A colony of forty on the banks.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Life in the lava. Any telling of what the machines are for. Ordinary rain. Carrying Forge fire away, in the
  Tribes' canon. Any tibanna source but the beldons.
- The ship's heat exchanger and the scour that came with it; vent machines beyond the game's own; the fireweed
  and scald-gear economy; two-faiths map mechanics (all struck 2026-09-29). The fuel-saving keel brace (cut
  2026-10-23). The ship ideas among these are asked below and not revived.
- Creatures offered and not chosen: the kettugal and the brazzok (2026-10-20, he picked the ummisk); the jobbosh
  (2026-10-16, *"insufficiently alien"*); the lava snail and seven other vanilla rows (cut by card on the evening of 2026-10-19, Pacific; the ledger stamps
  it 2026-10-20 in universal time).
- Three enrichments offered on 2026-09-30 and not picked: The Last Lift, Quench Crossings, The Anvil Answer. Only
  their names survive in the sources.
- Worldgen scoring of hot tiles, in any version.
- **Recommended for dropping, not yet his:** the fungus's promise to cool a room; bulloos that explode; the inert
  settings knobs. (The cleanse's recommendations, kept.)

## NEEDS HIM

1. **Should the ship drink the mountain?** He struck the heat exchanger before he stated the lens. On 2026-11-18 he
   ruled that every biome states its fuel, that *"a few biomes have richer sources"*, and the campaign's own ruling
   lists volcanic gas as one. *Stay struck* (default: the Forge is emergency fuel only, and its prize is floatstone).
   *Bring it back in 0.2.0:* a rig on a vent that charges the ship faster than anywhere, on ground that scalds and
   burns it every few days; a small build on the cycle's own state. *A gas tap instead:* the campaign's helixien
   path given a home here; a new deposit and its own design.
   *Waits on the rich-fuel question (which biomes are the few with a richer source) of 2026-11-19.*
3. **Two things he cut that touched the hull: the scour and the keel brace.** The scour (boiling rain doing minor
   damage and leaving ash on the ship's unroofed tiles) was struck on 2026-09-29 as half of the heat exchanger,
   before the ship lens and before his 2026-11-18 ruling that hull wear is in 0.1.0; his own light-screen ruling of
   2026-09-02 names *"ash"* and *"rain damage"* as things a screen stops. The keel brace was cut on 2026-10-23
   under *"I cut, you veto"* as *"small effect; the only ship hook"*. *Both stay out* (default: the Forge's wear is
   the lava landing, heat and fire, and its armour is floatstone). *The scour comes back in 0.2.0 on the shield
   frame:* rain and ash wear an unscreened ship; a small build on the cycle's rain phase. *The brace comes back:*
   one commit to revert; a second ship gift beside the hull and door.
   *Waits on the declined-ship-ideas question of 2026-11-19.*

The cleanse proposal of 2026-11-17 asked him nothing. One of its readings is changed here by scope rather than
asked: it wrote the first version for a colony that *"settles among dark foundry towers"*. The same cycle is kept,
and the settlers are a crew on a stop.

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

2. **Does landing beside the Empire's station change the search?** No: the ordinary search. The station belongs to the
   campaign layer (the design's default). *Delegated call.*
