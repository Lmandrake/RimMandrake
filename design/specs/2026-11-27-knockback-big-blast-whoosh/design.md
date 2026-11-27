# Explosive Knockback, next version: the whoosh of a blast bigger than one cell (design, 2026-11-27)

Item: `RIMMANDRAKE_DESIGN_KNOCKBACK_WHOOSH_FOR_BLASTS_OVER_ONE_CELL`. Record row: `design/concepts/ExplosiveKnockback/record.json`
`d_big_blast_whoosh_next`. Entry: `design/concepts/ExplosiveKnockback/version/next_version/README.md`. This page moves no
0.2.0 bar. Its bars are proposals for the version after 0.2.0.

His words, 2026-11-26 (OWNER:1795663740423093535): *"The "blowback" range of setting a whole moat of chemfuel on fire
should be bigger than the squares of the moat itself (expanding air) similar to igniting gas vapors in the air. So that's
a new ticket for Explosive Knockback: what happens when something bigger than 1 square blows up? Let's make sure it has a
REALLY big range of "whoosh" knocking things back (needs some design work to well define this)."*

Rulings that this design must keep: `d_gas_per_clump` (each clump bursts on its own, "never one centroid blast"),
`d_c_gas_shove` (a clump shoves a person one cell, unhurt), `d_chemfuel_is_explosion` (a lit pool is an explosion), and
vision lines 1 to 9 and 10 to 13 (`version/vision.md`).

## 1. What the build does today, measured in the code

- Each `GenExplosion.DoExplosion` is one blast with one centre. EK throws each thing once per blast id
  (`KbExplosionLedger.TryAdd`), from that centre (`KbPlanner.Direction`, `Dist` in `RM_KnockbackPlan.cs`).
- FlowWorks lights big fuel bodies as many small blasts. The sheet fire fires Flame blasts of radius 1.9, at most 3 per
  check (`FlowWorks/Source/Sheet/RM_SheetFire.cs`, `BlastRadius`, `MaxBlastsPerCheck`). The astrofuel chain fires Bomb
  blasts, at most 4 per tick (`RM_FuelFireMath.MaxBlastsPerTick`, `RM_LiquidFire.RunDetonation`). Today's separate build
  adds one blast when a chemfuel pool is first lit (`RIMMANDRAKE_PROVE_LIT_CHEMFUEL_BLAST_THROWS_WITH_KNOCKBACK`).
- Our burning gas bursts clump by clump, radius 1.9 by default, a person shoved one cell (`RM_MapComponent_Knockback.GasBurst`).
- Vanilla chemfuel stacks explode one by one, radius 1.1 plus 0.037 per unit, after a wick of 70 to 150 ticks
  (Core `Items_Resource_Manufactured.xml`, `CompProperties_Explosive`).
- Result: a burning moat of 100 cells throws each person by the first small blast that reaches them. The thing is then in
  flight, so every later blast skips it (`PawnSkipReason` "flying"). The reach of the whole moat is the reach of one cell,
  about 2 cells past its edge. That is the fault that he saw.

## 2. What the player sees and feels

1. A moat of chemfuel goes up. A wave of bent air and kicked-up dust rolls out from the whole burning shape. The wave
   follows the outline of the moat. It does not grow as a circle around the middle of the moat.
2. The wave throws each person, animal, corpse and loose good when it reaches them. Near things fly first. Things farther
   out fly a moment later. People well outside the burning cells are thrown. A bigger burning area reaches farther.
3. Each thing flies away from the part of the fire that is nearest to it. Beside a long trench, it flies straight out
   from the trench. Inside a ring moat, it flies inward, away from the near bank. A person in the trench is thrown out
   onto the nearer bank.
4. Where the pushes from two fires meet (the middle of a ring moat, the middle between two trenches), a person is jolted
   on the spot. They are not flung toward either fire.
5. The wave is moving air. A wall, a closed door or a rock face shelters what is behind it. The wave pours through an open
   door or a gap. It comes out weaker and bends round the corner, as air does. A sealed room is never reached. The wave
   never goes through the diagonal gap where two wall corners touch.
6. The usual rules of a throw hold: heavier flies less, a rat flies farther than a colonist and a colonist farther than a
   muffalo, no creature over the mass limit flies, goods fly wild and rebound, closed containers keep their goods, a pawn
   that hits a wall or another pawn takes the impact of a throw.
7. The push of the air itself does no damage, as a gas shove does no damage. The fire and the blasts at the burning cells
   do their own damage, as they do today. Because the push is not damage, a shield belt does not stop it (the same reading
   as `dl_gas_ignores_belts`).
8. One sound and one screen shake for each whoosh: a deep whump, then rushing air. Their size follows the burning area.
   There is no rattle of one sound for each cell.
9. A blast on one cell throws exactly as it does in 0.2.0. A whoosh exists only when more than one cell goes up together.

## 3. How an extended blast is represented: one event over a set of cells

**The call: one whoosh event over a set of burning cells. The per-cell blasts stay, and the event folds their throws
into one.**

- An event holds: the source cells, the tick that each cell caught, a charge for each cell, the source kind (chemfuel,
  astrofuel, gas), and an id from its own number range. A cell joins an open event when it touches (8 neighbours) a cell
  of that event and catches inside the join window. The event closes when no cell joins for one join window.
- Number source: the join window is the longest gap between two neighbouring cells that catch in one flash. Measure it
  in the Cauldron chain and in the FlowWorks pool and astrofuel spread at build. It is a fact, not a taste.
- The per-cell blasts keep their damage, their fire and their goods scatter (bar 5 and `d_gas_per_clump` stay as built).
  At the queue flush, a thing that both the event and one of its own per-cell blasts would throw is thrown once, by the
  stronger plan. Each thing is thrown at most once by one event.

Why not many explosions (today): each thing goes with the first small blast, so the reach never grows past one cell.
The cost grows with the cells, and so do the sounds, rings and shakes. Why not one big explosion at the centre: his ruling
`d_gas_per_clump` forbids the centroid. On a ring moat, a centre blast throws the people inside the ring outward, into
the fire. That is the wrong direction. Why not merge any blasts that are near in space and time: that changes every mortar
barrage, which is a locked scene (`sc_barrage_perf`). Also, vanilla chemfuel stacks go off 70 to 150 ticks apart, so a
merge would not catch them. Only a source that declares its cells makes an event.

## 4. How the push is computed: a pure decision in the shipped plan code

All of this goes in a new Verse-free file, `RM_KnockbackWhoosh.cs`, beside `RM_KnockbackPlan.cs`. It reads an air grid
(`IKbGrid`) and plain values, so `Source/SelfTest` compiles it as shipped.

1. **Air grid.** Air passes every cell except `KbCell.Wall`, `KbCell.Door` (a closed door) and `KbCell.OutOfBounds`. Pawns,
   sandbags, pits and water do not stop air. A diagonal step is allowed only when both side cells pass air (no corner
   cutting).
2. **Distance field.** One multi-source flood (Dijkstra, steps of 1 and 1.41) runs from all source cells over the air
   grid. It stops at the reach. It gives each air cell its path distance `d` to the nearest burning cell and the id of that
   cell. Inside the source, a second flood from the source edge gives the depth, as a negative `d`. One flood for each
   event, not one for each cell or thing.
3. **Local charge.** For each source cell, `Q` is the summed charge of the source cells within the reach limit `L` of it
   (a box sum over the event's bounds). A thin trench has a small `Q`. A wide pool has a large `Q`. A thing reads the `Q`
   of its nearest source cell.
4. **Reach.** `R = k * sqrt(Q)`, never under the radius of one per-cell blast, never over the reach limit. Number source
   for `k`: burning fuel vapour in air expands about 7 to 8 times in volume (a textbook figure, not measured here). A
   burned disc of `Q` cells then pushes air out to about 2.7 times its own radius, so `k` is near 1 cell per root cell. His
   look sets the final `k`. The reach limit is a Mod Setting; its default comes from the frame-time measurement in §8.
5. **Direction.** The push goes down the slope of the field: minus the gradient of `d`, read from the neighbour air cells.
   Out from a trench, in from a ring bank, round the corner of an open door. Where the slope is near zero (two waves meet),
   the plan is a jolt in place (`ContainerJolt`'s look for a pawn; no flight).
6. **Strength.** The existing kernel decides the cells: `ThrowCells(dist = max(d, 0), radius = R, force = whoosh force,
   mass, settings)`. So mass, the mass limit, the global cap, the wild factor of goods and every gate of `KbPlanner.Decide`
   (shield, pit, cooldown, held goods, containers) stay one code path. `KbBlast` gains three fields (a given direction, a
   given distance, a whoosh flag). `Direction` and `Dist` use them when the flag is set. This collapses the whoosh into the
   blast class; it adds no second thrower.
7. **Timing.** A thing launches when the wave front reaches it: on its cell's catch tick plus `d / v`. Number source for
   `v`: his look (the wave must read as a wave and still feel like one blow).
8. **Fold.** The pure rule `KbWhoosh.Fold(planA, planB)` picks the stronger plan for one thing among an event and its own
   per-cell blasts.
9. **Pits.** A whoosh throw is a full throw. A person thrown onto an intact cover breaks it and falls, as from any blast.
   The air breaks no cover under a person who stands on it (`LandingBreaksCover` gains a whoosh input).

## 5. Interplay with FlowWorks and gas, with no hard dependency

- EK owns the coupling, as it does for the Cauldron's vent gas today (`RM_KnockbackCompat.VentGasIgnitePostfix`). EK
  probes FlowWorks by reflection and patches one named FlowWorks method. FlowWorks holds no reference to EK.
- The FlowWorks seam: one public static method that FlowWorks calls when a connected body of fuel flashes, with the map,
  the cells that catch now, and the fuel per cell. FlowWorks keeps its own blasts and fire with EK absent or present. The
  method name is a contract. An EK selftest reads the FlowWorks source and fails when the method is renamed, and the
  compat probe logs one warning live when it is missing (a patch that matches nothing logs nothing).
- Our gas: `GasBurst` adds each clump cell to an open gas event. The clump bursts stay (bar 5). The event gives the
  whoosh. A lone clump with no burning neighbour stays a one-cell shove. Any future flammable gas (FlowWorks' next version
  of air flows, a tar smoke) joins through the same call.
- Without FlowWorks: gas still whooshes. With EK absent: FlowWorks burns and blasts as it does today.
- Charge by fuel: chemfuel and astrofuel give charge by the fuel in the cell; a gas cell by its density. Astrofuel
  detonation, which is a Bomb chain, gives more charge per cell than a chemfuel flash.

## 6. The look and the sound of the shockwave

This joins the blast show of `RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS`
(`design/specs/2026-11-24-knockback-blast-show/design.md`). A pure function `RM_KnockbackShowPlan.PlanWhoosh` gives the
front, from the same field as the push.

- **The front.** Each tick, the cells at distance `v*t` to `v*(t+1)` form a band. Air-ripple flecks (the 0.2.0 ripple,
  shader `MoteLargeDistortionWave`) go along the band at a spacing, each one turned along the push. The band stops at the
  reach. Because the show and the push read one field, the wave ends where the push ends (guiding principle 4: an effect
  that implies harm is true).
- **Dust.** Ground dust, sand, snow or leaves lift along the front, by terrain, and fall behind it.
- **Fire.** The flames lean outward with the push for a moment.
- **The per-cell blasts of an event** keep their flash and fire. They draw no ripple, no shake and no sound of their own.
- **Shake and sound.** One shake by the event's power (`ShakeToAdd`, the trauma rule). One sound at the loudest part of the
  source (sound only; the physics never reads a centre). Until a sound source is decided (blast show, item 10, "Later"),
  it plays the vanilla flame blast sound of the event's size class.
- **Budget.** A cap on live ripple flecks for each event and for each view, as for the 0.2.0 barrage.

## 7. What changes in code

| File | Change |
|---|---|
| `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackWhoosh.cs` | New, Verse-free: air grid rule, flood, local charge, reach, direction, jolt, timing, `Fold`. |
| `.../Source/RM_KnockbackPlan.cs` | `KbBlast` gains the given-direction fields and the whoosh flag; `Direction`, `Dist` read them. |
| `.../Source/RM_KnockbackMath.cs` | `LandingBreaksCover` gains the whoosh input. |
| `.../Source/RM_MapComponent_Knockback.cs` | The open-event table, joins and close, launches by arrival tick, fold at flush, `GasBurst` joins a gas event. |
| `.../Source/RM_KnockbackCompat.cs` | The FlowWorks seam probe and postfix. |
| `.../Source/RM_KnockbackShowPlan.cs`, `RM_KnockbackShow.cs` | `PlanWhoosh`, the front flecks, one shake, one sound, per-cell show folded. |
| `.../Source/RM_KnockbackMod.cs` | Settings: "Big fires whoosh" on/off, whoosh strength, reach limit. |
| `.../Source/SelfTest/KnockbackWhoosh.cs`, `Program.cs`; `selftest_explosiveknockback_whoosh.py` | The offline cases of §9. |
| `.../Source/RM_KnockbackProof_Whoosh.cs` | The live scene `sc_moat_whoosh`. |
| `src/RimMandrake/FlowWorks/Source/Sheet/RM_SheetFire.cs`, `RM_LiquidFire.cs` | A FlowWorks item: the named flash method with the body's cells. |

## 8. Proposed bars (plain experience sentences)

| id | The player sees |
|---|---|
| `whoosh_reaches_past_burning` | When more than one cell of chemfuel, astrofuel or gas goes up together, people and goods well outside the burning cells are thrown away from it, farther out than any one burning cell reaches. |
| `bigger_fire_bigger_whoosh` | A bigger or wider burning area reaches farther, and throws farther at the same distance, than a smaller one of the same fuel. |
| `whoosh_from_nearest_fire` | Each thing flies away from the part of the fire nearest to it, never from the middle of the shape: straight out from a trench, inward from the near bank of a ring moat. |
| `whoosh_meeting_jolts` | Where the pushes from two sides meet, a person is jolted where they stand, not flung toward either fire. |
| `whoosh_walls_shelter` | A wall or a closed door shelters what is behind it; the whoosh pours through an open door weaker and bent round the corner; a sealed room is never reached. |
| `whoosh_wave_shows_reach` | A wave of bent air and dust rolls out along the shape of the fire and stops where the push stops; each thing flies as the wave reaches it, near things first. |
| `whoosh_throws_once` | Each thing is thrown once by one whoosh, never once for each burning cell. |
| `one_cell_blast_unchanged` | A blast on one cell throws exactly as it did before. |
| `whoosh_keeps_throw_rules` | Heavier flies less, small animals fly farther, the mass limit holds, goods fly wild, closed containers keep their goods, a cover under a thrown person breaks, as for any blast. |
| `whoosh_one_sound_one_shake` | One whump and one shake for each whoosh, sized by the burning area. |
| `whoosh_no_hitch` | Lighting the biggest moat a player can dig round a colony, with the colony in it, does not stall the game. |
| `whoosh_switches_off` | The whoosh switches off by itself in Mod Settings; off, each burning cell throws only as its own blast, and gas shoves as in 0.2.0. |
| `whoosh_without_flowworks` | Without FlowWorks, burning gas still whooshes, and nothing errors. |

## 9. Each bar's cheapest test

- Offline, `selftest_explosiveknockback_whoosh.py` (the shipped `RM_KnockbackWhoosh.cs` and `RM_KnockbackPlan.cs` on a
  fake grid). It prints the worst value, its limit and the count of cases for each check.
  - `whoosh_reaches_past_burning`: for every source shape, a thing at the reach of one cell plus one is thrown; red on base.
  - `bigger_fire_bigger_whoosh`: reach and cells never fall as charge or width rises (monotone sweep).
  - `whoosh_from_nearest_fire`: the angle between the push and the line to the nearest source cell, worst case, on
    trench, ring, L, pool, two pools; a centroid planted fault must go red on the ring.
  - `whoosh_meeting_jolts`: on the ridge cells of a ring and of two parallel trenches, the plan is a jolt.
  - `whoosh_walls_shelter`: zero push behind a sealed wall, a closed door and a diagonal corner gap; less push through an
    open door than at the same straight distance in the open.
  - `whoosh_throws_once`, `one_cell_blast_unchanged`: `Fold` cases; a one-cell event equals the 0.2.0 plan in every field.
  - `whoosh_keeps_throw_rules`: the existing gate cases rerun with the whoosh flag set.
  - `whoosh_wave_shows_reach`: `PlanWhoosh` puts no front fleck past the reach and leaves no reached cell without a band.
  - `whoosh_one_sound_one_shake`: `PlanWhoosh` gives one sound and one shake for an event of any size.
  - `whoosh_switches_off`: with the switch off, the plans equal 0.2.0's.
- Live, one scene `sc_moat_whoosh` on the small list: a ring moat of chemfuel with colonists inside, outside, in the
  trench and behind a wall, a row of goods and a rat; one fire lights it. Its frame probe reads `whoosh_no_hitch`
  (`KbFrameStats`). Its mod-off arm reads the control. A FlowWorks-off arm with Cauldron gas reads
  `whoosh_without_flowworks`.
- His look: the same scene, at his walk, for the wave and the sound.

## 10. Offline simulation: yes, and why

Yes. The push is geometry and physics with many cases (shapes, walls, doors, masses, settings), and each live scene is
slow. The simulation is the shipped `RM_KnockbackWhoosh.cs` and `RM_KnockbackPlan.cs` against a fake grid and a fake
clock, in `Source/SelfTest`. It varies: source shapes (one cell, trench, ring, L, filled pool, two pools, a gas blob),
source sizes from 2 cells to the reach limit, charge per cell, walls, closed and open doors, corner gaps, thing places
(inside, on the edge, outside, between, behind walls), masses from a rat to over the mass limit, and every whoosh
setting. It leaves out: flight and flecks on screen, frame time, the real map's read of air cells, and FlowWorks' own
choice of which cells flash. The live scene checks those: `map_agreement.py` reads the air grid on the real map against
the fake one, as it does for gas today.

## 11. Risks

- **A big moat is many things at once.** 100 cells of trench round a colony can throw 30 people and 300 goods. The
  launches spread over the ticks of the wave, which helps. The flood is one for each event and is bounded by the reach.
  `whoosh_no_hitch` measures it; the reach limit default comes from that measurement.
- **Chain reactions.** A thrown burning thing can land in a second pool and light it. That is a new event or a join of
  the open one. Each event throws a thing once, and the landing stun window (`KbImmunity`) stops ping-pong between two
  events. Air lights nothing. The brake is in the world: the fuel burns away (guiding principle 3).
- **A slow chain.** An astrofuel chain runs for many ticks. The event grows while it runs, and each thing flies when the
  front reaches it, with the field of that tick. An early thing gets the push of the fire so far. That is true to a
  travelling flame.
- **Save mid-wave.** Launches that wait for the front are not saved, as `gasShovedAt` is not. A load inside the few ticks
  of a wave loses those throws. No thing is lost or doubled.
- **Load on every map** (guiding principle 5): nothing runs until two cells catch together. The open-event table is empty
  otherwise. No new reading for the player beyond the wave.
- **Double show.** The per-cell blasts of an event must not draw their own ripple, or the screen goes muddy. The fold of
  §6 covers it, and the `PlanWhoosh` test checks it.

## 12. Questions for him (each with my recommendation)

1. **Big gas clouds.** His card `d_c_gas_shove` made a gas clump shove a person one cell, unhurt. Now he asks for a
   really big whoosh from lit vapour. When a whole cloud goes up, may the whoosh throw people several cells, as a moat
   does? *Recommend yes:* a lone clump keeps its one-cell shove; a cloud of more than one cell whooshes like a moat; the
   push itself still does no damage. This changes what vision line 5 means for a big cloud, so it is his card.
2. **Fire at half.** Vision line 1 throws fire at half strength. Is a chemfuel flash "fire" for its whoosh?
   *Recommend no:* the whoosh is moving air with its own strength setting; the half rule stays on flame damage blasts.
3. **Round corners.** Should the whoosh pour through an open door and bend round a corner (moving air), or reach only what
   a burning cell can see in a straight line (as a vanilla blast)? *Recommend moving air:* an open door then vents the
   whoosh into the next room, a sealed room stays safe, and the corner fix of
   `RIMMANDRAKE_STOP_GAS_SHOVE_PAST_WALL_CORNER_UNSEEN` still holds, because air never passes a corner gap.
