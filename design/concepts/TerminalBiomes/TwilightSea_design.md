# The Twilight Sea: the design, seen from the ship

**Status:** the one design document for the Twilight Sea (`RM_TwilightSea`, in the mod
`src/RimMandrake/TerminalBiomes/`), written 2026-11-18 on the owner's instruction to see every biome "through the
lens of Utinni". Its sources were read in full this time. The same day's combined four-sea design read the
Twilight's largest files by heading only; it was retired on 2026-11-18 and kept only in git history, commit `b2530669e5`,
once each sea had its own design. What this design corrected against it is listed at the top of
`design/concepts/TerminalBiomes/TwilightSea_rewrite_choices.md`. That page says what became of every idea in every
source. None of the Twilight's older source files has been deleted. This is a design document only and it launches
nothing.

**Kind, checked against the sheet's own header:** a sea. Two rulings shape every section. *"You can't 'dive' as an
individual pawn nor return as one. It's ship or nothing."* (owner, 2026-09-26.) And *"You are either on their sea
floor, or you are on their beach. There is no 'on their surface' location."* (owner, 2026-11-01.) The ship flies to
the floor as its own planet layer, lands there, and is the only way back. The beach is the neighbouring land tile.

**Who reads this next:** a Designer run on this concept is handed the list of files in
`design/concepts/TerminalBiomes/` (`src/RimMandrake/rimflow/designer_cleanse.py`, `case_text`), so this file is in
its path by sitting here. Nothing in the pipeline reads it by name yet. The Twilight Sea has no locked Designer sheet
or tree. Its definition sheet (`the_twilight_deep.md`) is frozen by the older 2026-09-07 freeze, which later owner
rulings have amended three times; those rulings are followed here.

**One dependency under everything.** A ship flying down to a sea floor and back is built to the offline level and its
proof is blocked on its harness; the item that gives each sea its own floor on the ship's layer is blocked too, and
its note says *"nothing reaches a player until it lands"* (ledger, 2026-11-06 and the floor item's blocker note).
Every promise below reaches a player only when the Twilight's floor is a real place on that layer.

**Tags:** `NEEDS HIM` is a question only the owner can settle, with the real answers and the default used here.
`UNSETTLED` is a fact the sources do not fix. `UNMEASURED` is an engine fact nobody has checked. "Built" means a def
or class of that name is in source (the cleanse census of 2026-11-17, and my own search of 2026-11-18 where it says
"measured"); it does not mean it has passed anything. The walk for this mod has never been run live.

---

## What this place is

> *"A ceiling of cathedral living glass, where every creature is bedecked in reverent light. Shame most of them are
> so big, hungry, and quick."* (owner, 2026-10-20)

> *"Golden light-wells in dim green water, kelp towers, crowds."* (`the_twilight_deep.md`, header)

The last ordinary sea on the planet, under a lid. The lid is **the waveglass** (his name, typed 2026-09-26: *"love
what you made but just call it waveglass"*): one organism from shore to shore, seen from far below as *"a living
stained-glass ceiling"*, blue-green veined with gold, *"thick and opaque where it is old, thin and luminous where it
is new"*. It is *"a sky and not a surface"*. Nothing the crew owns ever touches it. What reaches the floor from it is
light, shed panes and falling things.

Where the lid has holes, his words are the picture: *"literal golden shafts of long beautiful light reaching down to
the sea floor."* Kelp towers stand in each one. Silver shoals turn in the gold. Everything alive carries its own
lamp: *"Creatures tend to have luminous balls, bladders, or patches of bioluminescent organisms within them, making
the place dim but well populated by local illumination plus the moving patches from the shafts of golden light."*
And: *"Colors should be lustrous green and blue-green. It's a pretty ocean."*

Along the bottom run **rivers that look dry**: *"mud-bedded channels where heavier water flows invisibly, carving
banks like any river anywhere."* The sheet's map of the place is one sentence: *"The banks are the wealth; the
columns are the light; the dark between is the predator's."* Above that dark, glowing colourful shafts of light hang
under the coloured panes and fade before they reach the floor. They light nothing there (his words of 2026-11-22;
Scope, the one signature).

A design pass named how this sea hurts people, and the line holds: *"The Grey kills you with chemistry and the Scald
with physics; the Twilight kills you with biology — with the abundance itself."* Nothing here is hostile the way a
raid is hostile. *"The thing you photograph is the thing that hurts you."*

**Seen from the ship,** this is the stop where a crew of desert scavengers finds a whole world that is alive, lit,
mild, full of food, and already picked clean of everything a Jawa came for. His words: *"This is a settled sea by the
Deepwater faction, so they would have cleaned up most of the scavenge and open mineral wealth lying about."* The
wealth that is left is alive, and a ship that leaves can only take the part of it that travels.

The crew are small, hooded, skittish and built for dry heat (`reconciled_lore/05_the_clan.md`). They have never
stood in water deeper than a trough. *(`UNMEASURED`: what gear the floor layer asks of a pawn here. His concept of
2026-08-13 says underwater "should have the same issues as vacuum for breathing"; no breathing rule was found in the
floor layer's defs on 2026-11-18.)*

## The clock on any stop

The Empire's search restarts at every landing (`src/RimUtinni/EmpirePursuit/`, cadence ruled by the owner
2026-08-28; ladder in `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`, its numbers marked
provisional): a probe droid five to eight days after landing, then scouts with a spotter, a strike team, an ion
cordon on the ship, a breaching assault, and an orbital bombardment that cannot be fought. Each step comes only if
the one before succeeded; a loud crew halves every wait and a hidden one doubles it. The arithmetic is taken from
"The clock on any stop" in `design/concepts/Greentide/design.md` and is not re-derived here.

**How long a stop on the floor can last: months, and that is the outer edge.** His ruling of 2026-11-18: *"The
numbers you're generating are likely the outer edge allowable for each biome, and that's just fine. Go with
that."* Under the sea is the top level of cover (`Answered on 2026-11-19` 2): every wait is four times the
open-ground wait, so a probe comes around day 20 to 32 and the bombardment around day 80 to 128 if the Empire wins
every step (four times the ladder's provisional numbers). **On the beach, in the open: about a month** (bombardment
on day 20 to 32).

Few crews will see that edge. A light-well lives about a week, so a long stay watches the light walk away many
times, and the deck fills the whole while. The deck and the lack of salvage, not the Empire, move most crews on
(this design's reading). A season is fifteen days.

---

## The first minutes

From the air the sea is his other picture of it: *"a stained glass window-like layer of life growing just below it's
surface everywhere"*, large soft panes of colour, about half of them lit (owner, 2026-10-24). The ship goes under.

It comes down through green dusk toward the gold. The landing is refused or moved rather than set astride a channel:
the hull, its ramp and a way to a bank are kept clear of the current's reach, calm and surge both. *(Built against
the retired hatch's position, not the ship's footprint: the cleanse measured this, and it is owed.)*

The ramp opens on *"the sound of company"*: *"click, chirr, shoal-hiss, the gardener's far slow calls through the
roof."* After every other stop on the planet, this one is full of small noise and nothing is screaming.

Before the first hour is out the player should have seen four things without going looking:

- a gold column standing in green water with a kelp tower in it and a shoal flashing as it turns;
- a line of lit stakes along something that looks like a dry gully, with litter skating down the gully by itself;
- a pane of the sky *"turning slowly down through a shaft"* a long way off;
- a stripped hull, crusted over, with a painted mark on it and nothing inside.

## The first day

- **The river that looks dry.** *"You see the floor is a river because the litter on it is travelling."* Lit stakes
  stand every few paces along both banks: *"people who have lived here for generations do not leave a river
  unmarked."* The fans on the bank all face the same way. The turf stops dead at the stakes. Past them, the first
  step is forgiving (*"the ground is moving under"* the walker, a few cells of drift, and they can still walk out);
  the middle is not. A worker in the middle is carried, upright and unhurt, to the low end of the map. *"No damage,
  no stun... the current itself only takes you somewhere."*
- **The sink.** Where every channel ends: *"alive, cold, half-buried in silt, in the dark — in the loohn's parish,
  at the end of the map from home."* The carried worker lies there marked and findable, getting worse, until
  somebody fetches them out of the water and into the hull. A roof over the sink saves nobody. By his rescue ruling
  of 2026-11-10 the rescue is complete on safe ground with a usable way back for both.
- **The cargo goes too.** Anything loose left on the bed drifts, more slowly than a person. Jawa pile salvage
  wherever there is room; here some of the room is a river.
- **The lost-property office.** The sink is *"floored in everything the river ever took: litter, panes, shells,
  stakes."* It is the one heap of free stuff on the whole floor, and it is in the predator's dark.
- **The first food is picked up by hand.** There is no fishing down here. His correction, typed 2026-09-26: *"you
  don't fish at the bottom of the ocean, I had meant the shoreline fishing."* On the floor the fish are hunted and
  the beds are gathered. The channel eel is *"so slow that bank-harvesters pick them up by hand."* The fat grazers
  move *"through the fall like cattle through a snowfall."*
- **Light you can carry.** The lamp-bladder weed hangs in *"a hanging curtain of soft lamps"*. A cut bladder glows
  for days and then rots: *"the torch you chase the light with."*
- **The dark between the wells.** Soot-black strings that only grow where nothing has been bright for a long
  time, and one long patient shape. The loohn *"waits far more than it hunts"*,
  and its only colour is a single bright mark. The safe roads are lit turf: *"walk on the alms."*
- **Nothing to dig.** *"A player who wants to mine the Twilight finds nothing."* The stripped hull is
  *"worth 0 silver and it is the most eloquent object on the floor."*

## The first week

- **The light leaves.** His words, 2026-09-26: *"the light can move around slowly over a week."* A well's rim
  thickens and dulls overhead, the column narrows and cools off gold, the shoals thin out, and then that ground is
  dark and another column is standing somewhere else. *"So the map always has light — just never where it was."*
  Anyone who looks up gets a day or so of warning for nothing. A well is never owned: *"A well belongs to whoever
  is standing under it."*
- **The floor forecasts it.** A stand of the soot-black strings browning means a well is about to open there. The
  gold haze in a column thinning means it is closing; when it closes the haze settles as *gilt*, and *"for a few
  days the dead well's floor glitters with it."* Then the dark sponges that drank that well's light all week switch
  on: *"The Deepwater call that ground the afterglow, and they walk it without lamps."* A crew that arrived late
  gets the afterglow, *"the poor diver's window."*
- **The sky lands on the ship.** His words, typed 2026-09-26: *"twilight drops sky panes on the ship that need to be
  cleared off."* More on this under "The ship while it sits here".
- **The undersurge.** *"The dry rivers breathe."* Hours ahead the bank combs blaze blue-white, the fans snap into
  line, the eels are gone upstream and the litter on the bed runs faster. Then the current climbs past the stakes
  for a day and takes whatever was left on the inner bank, one yank and then the ride. *"The Compact set them for
  the flood, not the fair day."* The surge never touches the light.
- **The gardener goes over.** The lid's keeper is the lanternwhale, the largest living thing in the seas: *"It does
  not notice you. That is the whole of its character, until you make it."* The floor dims, the *"far slow calls"*
  come through the roof, and sometimes when the light comes back a well has closed, or opened. *"A keeper you live
  beneath."* It cannot be harmed in this version; trying is refused with a reason.
- **Wells do not open in the river's reach.** A new column never stands on ground the current or the surge covers,
  nor on the hull. The light must not lead the crew into the water.

## The ship while it sits here

**Cover from orbit: the top level on the floor. None on the beach.** His card of 2026-11-18: *"Canopy, steam and
fog slow the search by one step; full dark still pauses it."* His later word the same day: *"Going under the ocean
is like the Dark... VERY concealed. But nowhere pauses it indefinitely."* The floor is under a sea and under one
living lid from shore to shore. It is not dark (*"the beautiful lighted Twilight floor with lots of lighted
everything"*, his words, 2026-09-26), but it is under the ocean, so it takes the top level of cover, like the
Abyss's Dark, and no pause (`Answered on 2026-11-19` 2). His own first thought about water, on 2026-08-13, was that it
hides a ship: *"'Hiding' your gravship from pursuit is a big deal in this campaign, and allowing them to under the
(admittedly very small) bodies of water or into the permanently dark terrain is pretty cool!"* The beach is an open salt pan in a wind that never stops:
no cover from above. At ground level its only cover is the kilometre-long shadow of a single blade plant.

**Wear on the hull: the laden deck.** His ruling of 2026-11-18: *"Yes in 0.1.0. It's easy, and most of the biome
already talk about this."* This sea's wear was his own, typed seven weeks earlier, and it is built.

- *What the player sees.* *"A deck under veil-fall is the most beautiful thing that can happen to a spacecraft,
  translucent blue-green sheets catching the beams, right up until the day you need to leave."* Flakes settle on the
  hull all the time. Now and then the lid lets go of a whole pane: a shadow the shape of a window grows on the
  deck for a few seconds, and then a room-sized sheet of living glass lands on it. By his card the pane *"can kill
  outright"* and the shadow is the fairness. Panes fall thickest near a well that is closing: *"the well that is
  dying rains first."*
- *What it costs.* A launch waits until the deck is cleared, one job per pane. *"The sky knows where it is parked."*
- *What answers it.* Hands. Clearing is ordinary work the crew can always do, and each cleared pane is harvest:
  *"the sea pays you for evicting it."* Moving the ship away from a dying well slows the fall. `UNSETTLED`: whether
  the ship's heavy field stops a pane. His shield ruling of 2026-09-02 gives the heavy field *"impactors"* and says
  *"Slow pressing things move through all shields"*; a pane is big, and it turns slowly down. This design assumes
  no field helps, so the answer is always the crew on the hull with whatever was in the hold.
- *It never traps.* The gate can only delay, and it fails open. *"Never a stranding."* It does not fire during a
  launch already under way.
- *The warning is on the floor from the first minute.* The stripped hull out in the dark has a second reading:
  *"a ship nobody cleared, generations on."*
- *Where it sits in the code.* The shared hull-wear frame is `src/RimUtinni/ShipShields/` (his shield rulings of
  2026-09-02): a tracker that wears a landed ship in a hazard its shield does not cover, and an advisory letter on
  landing that never refuses a landing. It knows heat, cold and blown particles. The pane system is its own code in
  the free mod (`RM_MapComponent_VeilFall`, `RM_Patch_GravEngineLaunchGate`), approved by his card of 2026-09-26. It
  should say so on the landing advisory. No new hull system is designed here. (`UNSETTLED`: a ship touch is campaign
  layer by his card of 2026-10-01 for the Abyss, and this one lives in the free mod.)
- *A second wear, for 0.2.0, flagged as mine.* The sea's oldest giant is described in source in these words: *"what
  those hands close on they do not let go of: a hull, a mooring, a diver."* The gripping terror is built as an
  animal; nothing makes it take hold of a ship. Making it do so is my proposal from that sentence, not a source's
  design; it comes at 0.2.0 as a rare event with a sign first and a grip that can be broken (`Answered on 2026-11-19` 4).
- *The approach.* No source says the lid or the water shakes a ship on the way down, and this design does not add it.
- *The beach.* No source names a wear on a ship parked on the Twilight's beach, and none is proposed. The frame's
  blown-particle case is there if salt in that wind is ever made weather.

**Fuel: the emergency route only, with a trickle.** His ruling: *"Every biome has a fuel source, but for most its
the hideously slow route of rendering biomass into chemfuel. Uselessly slow, only for emergencies."*

- *The slow route* has more to render here than in any other sea: kelp by the tower, and a sunk weed raft is,
  in the content drop's words, *"dried, a poor fuel"*.
- *The trickle.* One animal on this sea's roster is a small gas-filled drifter described in source as *"slowly
  weeping a thick gel that can be refined into fuel"* (the bulloo, which is the Forge's animal and also lives here).
  It is rare on this floor. That is a source line for a little fuel, not for a rich source, and the Twilight is
  written as the slow route.
- *Buying it.* Nobody on the floor is known to sell fuel. The Compact are *"keepers and neighbours, never landlords
  and never sellers"* of light by his ruling of 2026-09-27; a holding trades ordinary goods at one resident
  (`Answered on 2026-11-19` 3). On the beach side the campaign has a junker caravan that stocks chemfuel (measured in
  `src/RimUtinni/UtinniPatches/`, marked provisional there), and the crew has something no market has seen to pay
  with: light that is alive. Very Jawa: sell the glowing weed before it rots.
- *The contrast is the point.* The fuel sea is the Chill. This one feeds the crew and does not fill the tanks.

## "OMG did you see that?"

Each can happen inside the visit. Each says what is on screen.

1. **The dry gully.** *On screen:* a Jawa steps off the bank after something shiny lying in what looks like a dry
   gully, and slides away down it, upright, faster than anyone can run. A letter says where the gully ends. *Why it
   is funny:* the design pass said it first: *"the first time a colonist steps on 'dry mud' and is swept thirty
   cells... the biome has taught its one lesson."* The shiny thing went with them.
2. **The shadow of a window.** *On screen:* a soft dark square grows on the ground for a few seconds; hooded figures
   scatter; a slab of the sky lands where they were, and then they all run back toward it, because it is worth
   something.
3. **Shovelling the sky off the ship.** *On screen:* the crew on the hull among blue-green sheets, prying them up and
   passing them down the ramp into the hold. *Why it lands:* they are being paid to dig their own ship out.
4. **The piece of sky that leaves.** *On screen:* a Jawa bends to pick up a torn scrap of fallen lid and the scrap
   swims off. The lunoowa is *"indistinguishable from a torn piece of roof until it moves."*
5. **Somebody got here first.** *On screen:* the whole crew converging on a wrecked hull in the dark, and standing
   around it. A painted Compact mark, shells growing on the ribs, *"nothing inside."* *Why it is funny:* they are
   scavengers, and this is what being scavenged looks like from the other side.
6. **The gold dust.** *On screen:* a well closes and its floor glitters. A Jawa tries to scoop it up. It is not a
   thing. (By his ruling of 2026-09-27 the gilt is never an item.)
7. **The light moved.** *On screen:* the column the ship parked beside goes thin, then out, and a new one stands
   far off across a river, and the crew looks at the river.
8. **The dancers.** *On screen:* a pack of gold-amber bells turning together under the brightest pane, *"as if to
   music nobody else can hear."* A Jawa walks into them. *"The frills sting, mildly."*
9. **The drop.** *On screen:* something soft and wide-armed lets go of a kelp crown above a hooded head. The oobo
   *"hunts by letting go."*
10. **The heap in the dark.** *On screen:* a salvage party at the sink, picking through everything the river ever
    took by the light of a few cut bladders, and one point of colour appearing at the edge of the light. *"You hold
    a small circle of gold and things move at its edge."*
11. **The whole floor dims.** *On screen:* a slow darkening, a boom through the roof, every shoal turning at once.
    Nothing is attacking. Something the size of a district is overhead and has not noticed them.
12. *(0.2.0)* **Gems from the sky.** His five beats, in his words: *"eerie booming sounds and little light...
    animals freak out... and then it starts raining detritus, parasites, barnacle analogs with glowing bits in them
    like gems. and the whole ecosystem goes into overdrive and starts eating them at great speed."* *On screen:*
    glowing shells falling through the wells, Jawa snatching them up, and every animal on the floor racing them for
    it. For that hour the patient shape in the dark hunts things it never would.
13. *(0.2.0)* **The lamp that does not breathe.** *On screen:* a warm gold glow between two wells, steady where
    every real lamp pulses. *"A lamp with no piip around it is not a lamp."* The vaulisk; one to a map at most, and
    its tell can always be read. Killed, its lure is a trophy a Jawa would certainly keep.
14. *(0.2.0)* **The grazer and the junk lamp.** *On screen:* a slow fold of darkness drifting in to eat the brightest
    lamp the crew owns, and the crew lighting a worse lamp on a stick at the edge of the map to draw it off. *"Light
    the cheap one first."*
15. *(0.2.0, proposal)* **The hand on the hull.** *On screen:* a broad webbed hand with dark hooked claws closing on
    a corner of the ship.
16. *(Beach)* **The first fishing.** *On screen:* desert Jawa with a line in a sea, in a wind that never stops, on
    an empty white pan, pulling up something that is still lit. The liiru is *"a long thin excellent meal and a
    light that takes a minute to go out."*

## When the Empire arrives

How the Empire's ladder reaches a ship at the bottom of a sea: the probe and the bombardment follow, and the troops
wait at the beach (`Answered on 2026-11-19` 1). What the place does to anyone who comes down, whoever they are:

- **The river takes them.** Nobody warned them about the stakes. The river pass wrote the fight already: *"a bank
  fight one step from the current — free drama, by design."* A trooper knocked into the bed goes to the sink like
  anyone, and what they drop goes after them, to the heap the crew already knows the way to.
- **The sky lands on them.** A siege that sits under a shedding sky is strung out across the pane's strike zone, and
  its camp gets a laden roof.
- **The light walks off and leaves them in the dark.** A camp pitched in a well is in the predator's ground a week
  later.
- **A surge moves the line.** Whoever holds the inner bank when the combs blaze does not hold it for long.
- **The gardener ignores all of it.**
- *On the beach* there is nothing to hide behind and nowhere to fall back to but the ship. It is the worst ground on
  this sea for a small crew to be caught on.

## Who else attacks; who hates the Empire

- **Nobody raids.** *"no hostile faction or raid-analog of any kind"* (the danger pass's own limit). *"The Deepwater
  do not raid"*, and their holdings *"never become a war camp."*
- **The animals, ordinarily.** The loohn in the dark. The kelp squid and the drop-hunter among the towers. In 0.2.0
  the liar, a frenzied hour after the gardener passes, and the big ones: his line says *"most of them are so big,
  hungry, and quick"*, and his review notes of 2026-09 placed the famous ones here by name (the opee sea killer,
  *"make it 5 squares long"*; the crimson opee, *"9 squares long"*; the colo; the sando). Those are campaign-tier
  creatures the crew has heard of all their lives and never wanted to meet. Which of them are still cast is
  `UNSETTLED` (below).
- **Nobody here hates the Empire.** The Compact *"sell to everyone, the Empire included, and interrupting ANYONE's
  water costs their goodwill."* Their harbourmaster greets Imperial quartermasters by name. One of them has *"an
  exact figure for how much of the Empire's operational water … comes off his jetty … He will trade it. He has not
  yet decided for what."* That is the nearest thing to an ally in any Twilight source, and it is a man with a number
  to sell. Whether the Compact would tell the Empire a ship is under their sea, or shelter it, is `UNSETTLED`.
- **On the beach,** the settlers' fog-net holdings: *"a working net is wealth and a cut net is an act of war."*
  Their stance toward the Empire is not in any source read here.

## What forces the crew out; what lets them stay

**Out, before the Empire:**
- The deck filling faster than a small crew clears it.
- The well beside the ship closing, and the next one standing across a river.
- A crew member in the sink, and the rescue party's trip into the dark.
- A surge that took the stock off the bank.
- Nothing left to want: there is no salvage here, and a Jawa crew that has filled the hold with glowing weed has to
  sell it before it rots.

**Stay, longer than the Empire would like:**
- A lid and a sea over the ship: the top level of cover from orbit.
- Food, more of it and easier than anywhere but the Greentide, picked up by hand.
- Mild water. Nothing here burns, freezes, crusts or poisons.
- Free ground. Nobody charges for a well.
- Lit turf to walk on, stakes to read, and a floor that tells the truth about itself to anyone who looks.

## What the crew takes away

- **Light that is alive:** lamp-bladders by the sackful, good for days. *"The only light on the planet that
  grows."*
- **Pane,** off the deck and off the floor.
- **Timber, fibre and food from the kelp:** *"food, fiber, and the wet lattice-timber"*, on a world with almost no
  trees.
- **Meat and catch,** in quantity; lamp-black from the kelp squid.
- **Ledger coral cores,** slow to cut and worth carrying: the one thing here a crew chisels out.
- **Whatever was in the sink.**
- *0.2.0:* **living cuttings.** His words: *"underwater plants have the unusual property of staying alive after you
  'pick' them, so you can then decorate with a living plant easily."* A hold strung with glowing vine a thousand
  cells from any water is *"proof you went down and came back with something that is still breathing."* Also the
  gems from the gardener's rain, the liar's lure, green pigment, a tame ribbon of light, and whatever a holding
  gave in trade.
- **Not salvage.** That is the joke of the stop.

## The beach

*"A white salt pan under a permanent horizontal wind, with a dying sea on one side and a single black sail standing
on it, throwing a shadow that runs to the horizon."* The shore sheet's law is the opposite of the floor's: solitary,
sparse, *"loud and empty"*; *"constant wind, salt hiss, and one animal noise a long way off."* His words: *"The
terminator is solitary... In fact it's not lush there."* The floor is the surprise because the beach gives nothing
away.

From the ship a beach stop is a short one: fish the sea's catch (all of it has a living body below, by his ruling
that *"All the fishables should also be alive and moving around in the depths"*), read the terraces where the sea
used to reach, and trade if anyone is there. The air is mild, *"the only outdoor band where an unprotected human is
comfortable"*; there is no cover from orbit; water arrives as fog, *"a cupful at a time."*

## The promises of 0.1.0, and the scene that would show each one broken

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The ship lands on the Twilight's own floor, clear of the river's reach, with a way from the ramp to a bank, and can leave again. | A landing and a launch on a floor with a live channel. | A generic empty floor fails. A landing astride a channel fails. So does a floor reached any way but the ship. |
| Under a living lid, gold light-wells stand in dim green water with kelp in them, shoals working them, and dark between; every lit thing is lit by something alive or by a well. | A walk from the ramp to a well, across dark ground, to a second well. | A cold reader sorts unlabelled views of this floor from the other three seas'. A floor lit evenly everywhere fails. |
| The player sees glowing colourful shafts of light hanging under the panes that fade before the floor, while the floor between the wells stays dark and the wells are bright. | A walk from the ramp under the panes, across the dark between the wells, to a well. | A shaft that reaches the floor fails. A shaft that lights the floor, a crew member or a thing fails. Colour shown only as a tint on the ground fails. |
| The bed of a bottom river can be told from its bank without labels, and carries off whoever walks into its middle; the edge lets a walker back out. | A cold reader marks bed, stakes and bank on unlabelled views; then a worker walks the edge and the middle. | Views with the bed blended into the bank, or the stakes misplaced, are rejected even when the warning fires. A pawn that crosses the middle unharmed fails. |
| A carried worker ends at the sink, stays findable and worsening, and recovers once carried out of the water into the hull. | A worker past the stakes; a rescuer; a second rescuer after the first is lost; a save and reload while carried. | A roof built over the sink saves nobody. A full sink never loses the victim or drops them through a wall. |
| Loose things on the bed drift to the sink and can be fetched back. | A crate on the bed, a crate on the bank. | The crate at the sink is the crate that went in. |
| A surge is warned by the floor itself, widens the reach past the stakes, and passes; a way from the ship to a bank stays outside it. | Work at the stakes through one surge. | The same bank on a calm day: nothing is taken. |
| A light-well wanes, closes and another opens elsewhere within the visit; the closing can be read from the floor before it happens; a new well never opens in the river's reach or on the ship. | A stay long enough for one well to turn over. | A well whose shown remaining life never moves fails. A new well standing in surge reach fails. |
| A closed well's ground lights itself for a while afterwards and then goes dark. | The ground under a well before and after it closes. | The same sponges under a standing well stay dark. |
| Panes fall with a shadow first, can kill, lie where they land and can be harvested; they pile on a parked ship, and a launch waits until the deck is cleared. | A pawn and a crate under a shadow; a ship parked through several falls; a launch with a laden deck. | Launch is delayed, never locked: clearing always works, and a launch already under way is not stopped. The same ship on the beach gathers none. |
| Food can be gathered and hunted by hand on the floor; nothing can be fished there; the same kinds are fished from the beach. | A crew with no supplies for a day on the floor; a line on the beach. | A fishing zone on the floor does nothing. |
| Nothing rains under the sea; weather changes only the light. | A full visit's weather. | His words: *"Twilight Sea is a sea floor... no rain."* |
| Nothing vanishes. | Every loss above, with a save and reload in the middle. | |
| Under the lid the Empire's search comes at the top level of cover, much slower than for the same crew on the beach, and it still comes. | The same crew, as loud, landed on the floor and on the beach; read the search's next contact on both. | A search that never comes on the floor. |

**Promises that moved to 0.2.0 with their features** (his first-version answer of 2026-11-19):

| the player sees | the scene | what rules out a fake |
|---|---|---|
| The lid's keeper passes overhead: the floor dims, its call is heard, nothing is harmed; it cannot be hurt or removed. | One pass; an attack on the lanternwhale when it is on the floor. | The attack is refused with a reason; no corpse, no silent respawn, no roof left standing over a dead keeper. |

No row pins a rate: how often a pane falls, how long a well lives and how long a step is are tuning, and stay out of
any bar.

Settings: one switch per major feature, defaults as shipped; everything off leaves a lit floor with ordinary life on
it and a ship that can always leave (standing rule, every mod).

## Shared machinery

**Featured here** (the Twilight is where each is vital and should be proven):
- **Water that carries** (`RM_MapComponent_ChannelCurrent`, `RM_GenStep_TwilightChannels`, the surge condition, the
  sunk condition, on `FlowWorks`' bank and arrest seams). Built and proven here first; by his write-in of 2026-11-20
  it belongs to all four seas. The river pass measured that nothing else in the base
  game, the tide mod or our source moves a pawn along a flow; this is the one new movement system, and by his
  typed word its bank works are owed on ordinary surface rivers too.
- **Light as ground that moves** (`RM_MapComponent_WellLedger`: one clock for every well). The Abyss features light
  as a resource; here light is real estate nobody can own.
- **Light that follows its animal** (the mobile glow part), built here and *"shared by every glowing creature on
  every sea."*
- **Things landing on a parked ship** (the pane system and its launch gate): the hull-wear frame's case of an event
  that hits the hull, where the answer is hands.
- **A floor that forecasts** (plants that brown, glitter, light up and go out on the wells' clock).
- **The ship as the only door** (the seabed layer and its floor maps; `DivingInteraction`).

**Merely active here:** the rescue rule (the Fever Wood and the Greentide feature it); scenery that is an animal
(the lunoowa, the liar); a sign, then the event, then a window (the surge; the gardener's rain in 0.2.0); sound that
means something; wreck salvage (`Wreckage`'s sea-floor wrecks); bone from butchery; real flight for anything that
flies; the one sun from geometry, which on a floor is nothing and on the beach is a low, fixed sunset with dusk
reaching twelve degrees past the edge of day (his card of 2026-10-20); the Empire's search and the visibility dial;
the glow-seeking brain the grazer and the liar share, which the Grey and the Scald are owed for light that calls the
sea (his redirect of 2026-09-26).

**Three ship systems, and what the Twilight asks of each:**
- *Hull wear.* The frame is `src/RimUtinni/ShipShields/`. The Twilight asks it for nothing new: only that the
  landing advisory name the laden deck.
- *Cover from orbit.* One entry for this floor at the top level, beside the Abyss's Dark.
- *Fuel.* Nothing. The slow route is the base game's.

## Scope

Every feature is in one bucket. "Built" is source presence, not a pass.

**The one signature: the light-wells, with glowing colourful shafts of light under the panes** (his write-in on the
card of 2026-11-22, about 2:16 AM PST; `Answered on 2026-11-22`, entry 6). His words: *"The light well but in the
places away from the light well there are regions of colored ambiance from the colored panes above. It the bare
spots are so much brighter! That."* His later words of the same night, about 3:05 AM PST
(`Answered on 2026-11-22`, entry 10): *"the dark between the wells can be pitch, that's fine. But there should still be beautiful glowing colorful shafts of light portrayed somehow that don't quite reach the floor, just an artistic portrayal somehow"* The Conductor's reading, not his words: the bare spots
are the wells, the holes in the lid, and they are bright. The floor between the wells may be pitch dark. The colour
of the panes is shown as beautiful, glowing, colourful shafts of light that hang under the panes and do not quite
reach the floor. The shafts are an artistic portrayal: they light nothing on the floor and change no darkness. How
they are drawn is open. The falling
panes are not the signature: they stay this sea's hull wear (below). The wells move in 0.1.0: a well closes and
another opens elsewhere. His ruling of 2026-11-22: *"Yes light well first version."* (`Answered on 2026-11-22`, entry 9). The lid's keeper passing overhead is in 0.2.0: it
harms nothing and a stop can miss it. *Runner-up of the cleanse:* the cultivated light and tenancy economy, 0.2.0.

**The river is shared by all four seas, and is no sea's signature** (his write-in on the card of 2026-11-20,
`Answered`, entry 7). Bed, banks, lit stakes, the current, the surge and the sink are a system of every sea floor.
Here it is built, and it stays in this sea's 0.1.0 as land of the floor. The Grey Sea, the Chill and the Scald get
it at 0.2.0 (his card of 2026-11-22, `Answered on 2026-11-22`, entry 8).

**0.1.0, the stop**
- The floor as a real place on the ship's layer: the lid as a sky, gold wells, no rain, mild water.
  (flora and animals built; the floor on the ship's layer unproven)
- **The signature:** glowing colourful shafts of light hanging under the panes, fading before the floor; they light
  nothing, so the dark between the wells stays dark and the wells read bright. (unbuilt: owed. Owed: the drawing of
  the shafts, with no method chosen. No source draws them [measured, grep of `src/RimMandrake/TerminalBiomes/Source/`
  for shaft and god-ray, 2026-11-22: the only hits are a well's own column])
- The wells on the week's clock: opening, standing, waning, closed; the sky-read; free ground; never in the river's
  reach. (built; avoiding the surge's reach, not just the calm lane, is owed)
- The lit understorey: lamp-bladder weed, sea-lantern, giving turf, bank combs, soot-black strings, afterglow
  sponges, light-eating barrel sponges, answering coral, lamp moss, ledger coral, the haze in the column and its
  gilt, the light-pipe runner. (built; the afterglow, the wilt and the well-driven placement are behind a switch
  the cleanse wanted off)
- Five of the fourteen seaweeds: the two kelp towers, the sail-fan, the floor-felt turf, the detritus lace, with
  frond, timber and fibre as harvests. (measured unbuilt)
- The animals: both shoals split by light, the loohn, the pickers and the mimic, the grazers, the kelp crab and
  squid, the channel eel, the bells, the dancers, the drop-hunter, the ribbon, the lanternwhale, the gripping terror
  as an animal. (built)
- The river: bed, banks, lit stakes, fords, the current, drifting cargo, the surge and its tells, the sink as a
  place and a heap, the sunk condition, rescue into the hull, warnings, a landing kept clear. (built, except the
  bed's own ground and the ship-footprint reservation)
- Falling panes, flakes, the laden deck and the launch that waits. (built)
- The stripped wreck; ordinary sea-floor wrecks. (built)
- Weather that only changes the light. (today the floor has Clear and Fog; the four lighting weathers are unbuilt)
- The beach as it is: salt pan, wind, the catch. (shore plumbing built)
- Under the lid as the top level of cover from orbit. (unbuilt; campaign layer, one entry in the pursuit)

**0.2.0, the stop with company**
*Moved here from 0.1.0 by his first-version answer of 2026-11-19 (one signature a stop is sure to
see); each line goes back by one move:*
- The gardener overhead: the passing shadow, the call, sometimes a well moved; protected from harm. (the pass is
  unbuilt; the animal is built)
*Already here before that answer:*
- The gardener's five beats: the booming, the dark, the panic, the rain of flakes, parasites and glowing shells, and
  the hour of overdrive; the seam of gleanings along its track. (unbuilt)
- The grazer of lamps and the junk-lamp decoy; the liar and its trophy; lid-dark. (built; lid-dark unknown)
- The big ones: the gripping terror taking hold of a hull (proposal); the campaign's famous sea monsters.
  (campaign layer; cast `UNSETTLED`)
- The Compact's holdings: three bank holdings, the blessed cast of seven, their tended weir, their junk-lamp stake,
  cages and a cultured sun seen working. (campaign layer; the cast is drafted and blessed; the houses are unbuilt)
- Living cuttings as the take-home; a kept rolling lamp; a tame ribbon of light. (unbuilt)
- The other nine seaweeds and the six small things that cling to them; the stinging veil. (unbuilt)
- The float harness and the one-way ride to a weir. (harness built; it needs a weir downstream)
- The gardener come down to graze, and the lane it leaves. (unbuilt)
- Pane and cargo delivered by the river to a bank. (drift built)
- On the beach: a stranded giant, a half-drowned war ruin, the shore's own few animals, bait. (unbuilt)
- Fuel bought from caravans on the beach. (a caravan kind exists; nothing ties it to this shore)

**Later (a crew that stays, or a colony)**
- The bank works: weir, silt-trap, stake line and their breach. *"a colony that builds them has chosen to LIVE
  here."* Cargo floats.
- The chained fields: cages and clipped lamps walked from well to well, his *"movable chained floating fields"*;
  the cultured sun-sphere, *"other lights you can grow slowly yourself"*; kelp farming on bank silt.
- A lamp kept alive in a tank at home, and pigment from it.
- The harsher sink settings (scarred; lost, which must still leave a readable sign).
- Studying the gardener; the slow ruin if the last gardener dies.
- A full Compact town under the sea (his plan of record for a second version); their ledgers and soundings.
- Blade-sheet from the beach's century-old plants. Forty colonists on a floor.

**Dropped (already cut or declined; listed so nobody revives them by accident)**
- Selling or leasing light in any form: skylight rights, tenancy, claim buoys, charts as items, poaching standing,
  techprints from the Compact. His typed ruling, 2026-09-27: *"The Compact does NOT sell light, that's not a
  mechanic we accepted. Remove."* The code was removed that week. The cleanse of 2026-11-17 still lists these as
  future work (its census row X30 and ticket T30); they are not.
- Light calling the sea. His typed ruling, 2026-09-26: *"Actually attacking light makes more sense in the Grey and
  Scald (dark on the bottom) than it does on the beautiful lighted Twilight floor with lots of lighted
  everything."*
- Fishing on the floor, nets in the wells, "unlimited" fishing. His typed correction, 2026-09-26.
- A fixed ranking of marquee rewards (tenancy, permits, the Ark Seed). His typed answer, 2026-09-26: *"no we need to
  vary this..."*
- A pawn riding the river by swimming, steering or going upstream; a pawn simply lost past the last eddy.
- Diving or returning as a single pawn; the dive hatch; any place on the surface; rain; the word "mold".
- A catch item for the giants (dropped by its own item).
- Seven plants the flora pass cut on itself (a prism plant, a lying plant, a light-eating snare, a fourth lamp, a
  wild sun-sphere, a roof-tending plant, a walking plant) and anything mineral: *"The Twilight's plants are soft,
  wet, lit and alive."*
- **Recommended for dropping, not yet his:** the inert cross-biome switches (the cleanse's recommendation).

## UNSETTLED and UNMEASURED

- **How the Empire's ladder reaches a ship on a sea floor.** The probe and the bombardment follow; the troops wait at the beach (`Answered on 2026-11-19` 1).
- **Which big animals are cast.** The roster file carries his 2026-09 notes placing eight famous or donor animals
  here; the content drop measured them absent from the live def after the cast sitting of 2026-09-25; on 2026-11-18
  the free def carries eighteen animals and the campaign patch adds three (two scalefish and the sando). The colo
  claw is a corpse in the rare catch and alive nowhere, with an open item to decide which.
- **Whether the floor demands breathing gear** (above).
- **Whether a returning ship finds the same floor, and whether its wells aged while it was away.** The intent is
  recorded as *"one floor per sea, kept forever, discardable on purpose"*; the cleanse's review found nobody had
  measured it.
- **Whether the Compact would give a ship away to the Empire, or hide it.**
- **Whether the heavy field stops a pane** (above).

## NEEDS HIM

None open (2026-11-22).

The cleanse proposal of 2026-11-17 asked him one question, whether the wells may turn over in about a week when the
frozen sheet says years. He had answered it on 2026-09-26 in his own words (*"the light can move around slowly over a
week"*); it is not asked again.

## Answered on 2026-11-19

These entries were under `NEEDS HIM`, and each keeps its number. Item
`RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` (his word: "83 biomes yes") applied them after a
second reader checked each answer against its source. **His ruling** means his dated words answer it. **Delegated
call** means the Conductor took the obvious answer (`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`); he
can undo any one by name.

1. **What does the Empire do about a ship at the bottom of this sea?** The probe and the bombardment follow the ship
   down. The troops wait at the beach and meet it when it lifts. This needs the fewest new things and is the same in
   all four seas (the design's default). *Delegated call.*
2. **Is being under this sea one step of cover, or more?** *His ruling:* his word of 2026-11-18 (4:09 PM PST): *"Going
   under the ocean is like the Dark... VERY concealed. But nowhere pauses it indefinitely."* Under this sea is the top
   level of cover. **This changes the design's default.** Was: *One step*.
3. **Does a Compact holding trade with a visiting crew at all, and does anyone on this sea sell fuel?** Ordinary goods
   at one resident, no fuel on the floor, fuel from caravans on the beach (the design's default). *Delegated call.*
4. **May the gripping terror take hold of the ship (0.2.0)?** Yes, at 0.2.0, as a rare event: a sign comes first, the
   ship is never destroyed, the grip can be broken, and a launch stays possible. *Delegated call.*

**Answered by his five cards of 2026-11-19** (item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; each card and his pick, word for word:
`design/RimMandrake/biome_rulings.md` §Five biome answers). Each keeps its number.

5. **Ship or light ideas he declined or cut** (the selling of light, light calling the sea, the Ark Seed). *His card
   of 2026-11-19 (declined ship ideas):* they stay out. He can bring any one back by
   name.

**Answered by his card of 2026-11-20** (item `RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED`; the
enact item is `RIMMANDRAKE_ENACT_SIGNATURE_PICKS_INTO_DESIGNS_SLIME_KEEPS_FILM`). Each keeps its number.

7. **Is the river the Twilight's signature, or the signature of all four seas?** It was the Twilight's, under his
   approval of 2026-11-17 that read it as the one signature of the four-sea mod. On the card of 2026-11-20 he took
   neither offered option and typed, about 6:00 AM PST: *"Actually having underocean rivers should be commonplace in all the oceans, so this isn't even special for Twilight. EACH of them should get an actual special. Perhaps the Twilight should be the falling shards of the ocean's colorful cover"*
   So the river is shared by all four seas and is no sea's signature; this replaces his approval of 2026-11-17. The
   Twilight's own signature is entry 6, below.

## Answered on 2026-11-22

**Answered by his cards of 2026-11-22** (item `RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED`; the
enact item is `RIMMANDRAKE_ENACT_SIX_BIOME_ANSWERS_SLIME_GETS_BOTH_DRAWS`). Each keeps its number.

6. **What is the Twilight's one 0.1.0 signature?** The candidates were the falling sky, the light that moves and the
   dark between the wells. He took none of them and typed, about 2:16 AM PST: *"The light well but in the places
   away from the light well there are regions of colored ambiance from the colored panes above. It the bare spots
   are so much brighter! That."* So the signature is the light-wells, far brighter than the
   ground away from them; entry 10 says how the panes' colour is shown. The falling panes stay this sea's hull wear. That answer did not
   say whether a well moves; he ruled it later the same day (entry 9).
8. **Do the other three seas get the river in 0.1.0 or at 0.2.0?** *His card, about 2:19 AM PST:* "Twilight now,
   others 0.2.0". The Twilight keeps its built river in 0.1.0; the Grey Sea, the Chill and the Scald get it at
   0.2.0.
9. **Does a light-well move in the first version?** *His ruling of 2026-11-22:* *"Yes light well first version."*
   So in 0.1.0 a well closes and another opens elsewhere, on the built moving-wells system and its promise row.
10. **Is the ground between the wells dark, and how is the panes' colour shown?** He answered the Conductor's report
   that the second 0.1.0 promise row and the design's lines had been reworded to coloured ambient light between the
   wells. He typed, about 3:05 AM PST: *"the dark between the wells can be pitch, that's fine. But there should still be beautiful glowing colorful shafts of light portrayed somehow that don't quite reach the floor, just an artistic portrayal somehow"* So the
   dark between the wells stays, and may be pitch dark; the second promise row says "and dark between" again. The
   colour is glowing colourful shafts of light under the panes that fade before the floor: an artistic portrayal
   that lights nothing on the floor. The third 0.1.0 promise row is the shafts. How they are drawn is owed, with no
   method chosen (item `RIMMANDRAKE_CORRECT_TWILIGHT_DARK_STAYS_PITCH_COLOUR_SHAFTS_ARE_ART`).
