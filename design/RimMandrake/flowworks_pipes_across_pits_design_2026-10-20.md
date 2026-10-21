# FlowWorks: pipes, hoses, cords and conduit across pits (RULED DESIGN, 2026-10-20)

Owner, verbatim (2026-10-20): *"Do a background design pass. We need to think about how pipes and conduit work across
pits."*

**Design only.** Nothing in code, defs, the bridge or the game was touched. Paths are under `src/RimMandrake/FlowWorks/`
unless stated, at HEAD `99a127889a`. Each engine claim is marked MEASURED (read, with file:line) or UNMEASURED. He
answered the eight option cards (§Owner's answers) and the eleven GPT-review cards
(`flowworks_drawbridge_pipes_gpt_review_2026-10-20.gpt_read.md` §Owner's answers); the section below folds all of them
in, plus every GPT finding the triage marked valid inside his rulings. Build items: `PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE`,
`PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL`, `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS`,
`LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED`.

Standing rulings obeyed: a pit is a SUPERDEEP cell, not a building (`infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`);
R8, no real z-levels, amended only so pawns walk under a suspension bridge; nothing rests and no building stands under a
deck (`suspension_bridge_construction_design_2026-10-18.md` §1.4); each side of a pump takes one port, pipe or hose
(`flowworks_bars_answers_2026-10-20.md` #21); the GSS/FlowWorks rulings (`gss_flowworks_rulings_2026-10-11.md`).

### Levelling feasibility

Item `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL`, 2026-10-20 (owner: *"Let's see if we can do this"*). **Verdict:
feasible, and built behind a Mod Setting. The offline selftests pass; the live run is owed.**

- **What already existed (MEASURED).** Every body already stores exact decilitres, and all bodies share one surface
  convention (dL per square, 0 = brim, negative below ground). A dug square is `WaterDl − depth·U`. A pond is
  `RM_LevelSolve.PondSurfaceHeight(hist, stockDl)`, cached per pulse in `RM_LiquidStock.SurfaceHeightOf`. A limitless body
  stands at 0. The pump's world-to-world move already has reversible legs for both kinds of end
  (`Building_LiquidPump.cs` ~l.324: `TryTakeDl`/`TryPourDl` for a dug square, `Stock.TryDebitDl`/`CreditDl` for a pond).
  Tanks drain by gravity in `RM_LiquidNet.SettleTick`, every 250 ticks (`RM_PumpMath.CycleTicks`), from
  `RM_MapComponent_Excavation.MapComponentTick`. Levelling hooks into that same tick, just before the settle.
- **Solver shape.** The kernel is `Source/RM_LevellingMath.cs`, which is Verse-free. Each body is a floor histogram plus
  its dL, a liquid, a key, and a limitless flag. Each link records the floor under each end, what each end can give, and
  what each end can take. Links are visited in a fixed order, Gauss-Seidel style: each link plans against the volumes
  that earlier links in the same cycle left behind. That makes parallel links add up, and a body on many links is never
  overdrawn.
  - A link moves water from the higher surface to the lower one. The amount is the smaller of two limits: the rate
    (`levellingLitresPerCycle`, 1,000 L per link per cycle), and half of what would bring the two bodies level. The
    level point is found by bisection on the exact surfaces.
  - Because a move never goes past half-way, it can never reverse a gap. Heights therefore converge monotonically and
    cannot oscillate. The halving also absorbs model error, for example a run that counts too much area at a sill.
  - Same key: nothing moves. Different liquids: nothing moves. A dry receiver takes the source's liquid. A source stops
    when its surface reaches the floor under its end (exposed intake). There is no crest test, so a siphon always works.
- **Game adapter.** `Machinery/RM_Levelling.cs`. A link is two open hose ends (Intake or Outflow) on one network
  component. Each end is resolved the way a pump finds its source: the end square, then its 8 neighbours. Rigid pipe
  reaches a body only through such ends.
  - A dug end's body is the 4-way run of wet squares of its liquid, walked from that end. A natural end's body is its
    pond.
  - Skipped: a component with a working pump, and exact-level water switched off.
  - The mover is `RM_LiquidTransfer.Move` with the pump's own legs, and it credits the hose's flow art.
  - The hose's inspect line shows the link state: flowing, level, same water, different liquids, intake out of the
    water, or no room.
  - Settings: `gravityLevellingEnabled` (on) and `levellingLitresPerCycle`, in the Flexible hoses section.
- **Cost per tick (offline, MEASURED by the selftest).** The kernel plans a hard budget of 64 links per cycle; the rest
  rotate in later and catch up by up to 8 cycles' worth. The test scene had 200 bodies, 40 of them 40,000-square basins,
  and 400 links. Planning took **89 µs per cycle, about 0.36 µs per tick**.
  - The adapter's walk of dug runs is capped at 20,000 squares per run and 60,000 squares per cycle. Its live cost is
    UNMEASURED, so the L1 benchmark on a 325×325 map with 200 links is owed live.
- **Selftests** (`Source/SelfTest/LevellingChecks.cs`, all green). The four gates were checked every cycle:
  - volume exact, counting what limitless bodies gave or took;
  - energy never rising, and in two-body scenes the gap never growing;
  - no link reversing and no gap changing sign;
  - no exchange between liquids.
  The fuzz covered 300 scenes, all of which reached a fixed point. The item's L1 cases also pass: a 1-square pit
  against a 100-square basin, ten parallel links, a same-body loop, a siphon, an exposed intake, water against oil, a
  dry receiver, and the sea filling a pit to the brim.
- **Risks.**
  1. The adapter treats a dug run and a pond joined below the surface as two bodies. Their surfaces already match, so it
     moves nothing, but the readout says "level" rather than "same water".
  2. A run bigger than the walk cap is under-counted. That only slows levelling; it never overshoots.
  3. The pour lands near the receiving end and the pulse spreads it. Between pulses, that end reads high, which errs
     toward moving less.
  4. A hose's held contents do not fill from a passive move.
  5. Levelling stops whenever a working pump is on the network. That is an owner question below.
  6. Nothing has run live: the ruled L2 rows (two ponds level; a pond and an oil pit do not) are owed.
- **Owner question.** *"When a hose network has a running pump on it, should passive levelling still run alongside the
  pump, or should the pump alone decide (as built)?"*

## Ruled design

### P1. Four kinds of line, told apart by a def-level tag

| kind | defs | flexible? |
|---|---|---|
| **rigid pipe** | `RM_UniversalPipe` (`Defs/Machinery/RM_LiquidLogistics.xml:23-87`) | no |
| **rigid conduit** | vanilla `PowerConduit`, `WaterproofConduit`, **with or without the GSS restyle** | no (review answer 5) |
| **flexible power cord** | **a new def** (does not exist today; item `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS`) | yes |
| **hose** | the FlowWorks hose (`Source/Hose/`) | yes |

GSS **restyles** vanilla `PowerConduit` rather than replacing it (MEASURED, `GimmeSomeSlack/Patches/RM_ConduitStyleable.xml:10-12`,
`GimmeSomeSlack/Defs/Aerial/RM_ConduitStyles.xml:8`), and no cord, cable or wire ThingDef exists in GSS or FlowWorks Defs
(MEASURED, defName grep). So the crossing permission must come from an explicit **def-level tag** (a `DefModExtension`,
e.g. `LineKind = RigidPipe | RigidConduit | FlexCord | Hose`), never from `isPowerConduit` and never from the style: changing
a conduit's look must not change where it may go (GPT #14).

### P2. The crossing policy (one table for placement, construction and rebuild)

| surface | rigid pipe | rigid conduit | power cord | hose |
|---|---|---|---|---|
| solid ground | yes | yes | yes | yes |
| an excavated square, any depth (pit, trench, canal, moat) | **no** | **no** | **no** | yes, entering only by a ramp or a ladder (P5) |
| a pit cover | **no** | **no** | **no** | **no** |
| any suspension deck, rope included | **no** | **no** | **yes** | **yes** |
| a drawbridge leaf | **no** | **no** | yes, disconnects while raised | yes, disconnects while raised |
| across a gap in the air | **pipe poles** (P3) | **GSS power poles** (shipped) | no | no |

- Owner, answer 1: *"Otherwise conduit does not cross bridges or moats or pits without this. Can't build there."*
- Answer 3: a cover carries nothing. Answer 4 and its follow-up: hoses and cords may lie on **any** deck; only rigid pipe
  and conduit need poles. This is a **narrow exception** for the two flexible kinds: rope does not gain a general `Light`
  affordance (that would admit unrelated buildings; rope lends none today per `RM_SuspensionPatches.cs:53-111`).
- The policy is applied at blueprint placement, re-checked when a frame **completes**, and checked before any automatic
  rebuild. Vanilla cancels blueprints and frames that fail `CanBuildOnTerrain` when terrain changes, but never re-checks a
  finished building (vanilla `TerrainGrid.DoTerrainChangedEffects`, read in the pre-ruling pass; not re-read this pass).
- A 1 m canal counts as excavated in this table. If he wants shallow ditches exempt, see Q2.

### P3. Pipe poles

Answer 1: *"Pipes get a version of the power pole: supports that provide a somewhat saggy hose between them. Same
mechanics, just much thicker and less flexible. Same art variation."*

- **Supports on solid ground only** (review answer 8): never on a deck, a cover or an excavated square. GSS anchors
  require only `Light` (`GimmeSomeSlack/Defs/Aerial/RM_AerialAnchors.xml:30`, read in the pre-ruling pass), so pipe poles
  need their own placement check; the inherited affordance alone would admit pit floors.
- **The span** reuses GSS's aerial mechanics (`GimmeSomeSlack/Source/Aerial/`: parabola sag `sag = sagFactor·|AB|`,
  `AerialMath.cs:87-103`; wire-down alert and restring job), with a **smaller sag factor and a thicker draw**. Max span
  and sag are Mod-Settings tuning; proposal: sag 3 % (power is 6 %), max span 12.
- **Same art variation**: one pole and one span look per `RM_UniversalPipe` style (four looks).
- **No art before the width spec** (answer 8): a pipe and hose width is settled and judged in game first
  (`LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED`).
- **Not ground, not support.** A pole span is not walking ground, not a climb exit, not a deck, and not in pawn topology
  or `DeckAt`.
- **The liquid net gains one long-range edge kind** (pole to pole). Component caps (`MaxConductors`,
  `RM_LiquidNetKernel.cs`) are applied **after** the edge joins its components; one logical edge per connection, never a
  duplicate cardinal + aerial path; one-port-per-pump-side still holds; topology is rebuilt on any edge change.
- **Where the shared code lives** is a build decision: GSS and FlowWorks are separate mods that talk today by soft
  reflection (`RM_FallenWireShock.cs:233-281`); the shared aerial piece goes in `RimMandrake.Shared` or one mod depends on
  the other. Not an owner question.

### P4. Digging, collapse and teardown

- **Digging breaks the line** (answer 2 and answer 1, *"Digging a pit destroys them"*). The break happens when the
  terrain edit **commits** (`Deepen`), never at designation, so a cancelled dig breaks nothing. Rigid pipe, rigid
  conduit and cords on the square are destroyed with leavings; the net splits through the normal despawn path. A hose
  re-plans (it may lie in a pit by P5) or, if it cannot, is cut. The pre-ruling "refuse the dig until the line is moved"
  is withdrawn.
- **A deck that collapses** destroys the cords and hoses on its squares. A live cord dropped into the hole should reuse
  GSS's fallen-wire behaviour (`RM_FallenWireShock.cs:23,233-281`: shocks, ignites FlowWorks' burnable liquid).
- **A pole that loses its ground** (dug, destroyed) drops its spans.
- **Teardown is idempotent and support-owned** (GPT #20): each segment records what holds it up (deck squares, or its two
  poles). Simultaneous anchor loss, deck destruction and pole loss produce salvage, spill and fallen-wire effects exactly
  once, and a disconnected fallen cord is never treated as powered through a stale edge.
- **No migration** for lines already across pits: review answer 9, *"Can't happen. We don't have any."*

### P5. Hoses into pits, down ramps and ladders

Answer 5: a hose may run **down ramps and hang down ladders** into a pit, to drain or fill it.

- The hose world (`Source/Hose/RM_MapComponent_Hoses.cs`) gets **band-aware transition edges**: lip to ramp to floor, and
  lip to ladder to floor. An open excavated square is otherwise blocked to a hose route; a hose never drops down a sheer
  wall except on a ladder. Endpoint reach is checked by band, so a pump on the lip does not connect to a hose end on the
  floor in the same x/z cell.
- **A raised ladder leaves the hose hanging** down the wall (review answer 7): the hose stays connected. This does not
  make the ladder climbable.
- Allowing a hose down does not allow floor-band pumps, tanks or buildings under a deck.

### P6. Gravity levelling between bodies of water

Answer 7: *"Tanks already empty by gravity themselves, slowly. That would still be true here. Just extend that:
connecting two bodies of water will cause them to slowly flow from one to the other until they level out. Let's see if
we can do this"*. Review answer 10, siphon: *"Yes, always"*. Review answer 11: *"Whatever we ruled about mixing in a
canal happens."* Item `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL` (feasibility first).

- **Scope: world body to world body only.** A pipe or open hose whose two ends sit in two liquid bodies (pond, canal, pit,
  natural body) moves liquid with no pump, from the higher surface to the lower, slowly, until the surfaces match.
  **Filling storage still needs a pump** (GSS ruling 3); tanks keep their existing slow gravity drain (Dump tanks,
  MEASURED, `Source/RM_PumpMath.cs:17-24`), unchanged.
- **Compare surface heights, conserve volume** (GPT #23). Use the built level-surface solver (each connected body holds
  exact decilitres and one surface height; item `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`, built). Equal depth and equal
  litres are not equal level. Transfer is bounded so it never overshoots equilibrium, never drives a body negative, never
  creates liquid by clamping, and sums correctly over parallel links; a link whose two ends are in the **same** body moves
  nothing. A limitless source (an on-map ocean, the edge law, `flowworks_liquid_matrix.md` rule 2) exchanges
  explicitly.
- **Siphon: always.** Passive flow may cross a crest higher than both surfaces; no priming rule.
- **Exposed intake stops.** When the source surface falls below the intake end, flow stops (GPT #24). A switched-off hose
  drains only its own contents (GSS ruling 2/13), never the reservoir behind it.
- **Different liquids do not mix.** The canal ruling is **no-mix**: owner, typed on a card 2026-10-02
  (`infrastructure/state/ledger/events/OWNER.jsonl`, tsn `1790950262957442637`, note on `PIT_SUPERDEEP_COLLAPSE_1`):
  *"Analyze which of these is most feasible in the game/code. If (1) is easiest, it's also the best for now. I had
  thought (2) would be easiest and it isn't bad either. (3) seems like a huge mess with little payoff."* (the card's
  options, as recorded: (1) no-mix, (2) bigger pool wins, (3) sludge). The code ships no-mix: a driver *"cannot pour into
  a cell already holding a different fluid (fluids never mix): Refused"* (MEASURED, `Source/RM_MapComponent_Excavation.cs:3326-3327`),
  and the canal kernel's donor pick filters by no-mix (`Source/RM_FlowKernel.cs:1992`). So a link between two bodies of
  **different** fluids moves nothing, and the readout says why; a link into a **dry** body stamps the source's fluid on
  it, as a canal fill does. Bodies stay spatially distinct across a utility link: a hose is not a channel.
- **Bounded solver** (GPT #26): one map-owned, budgeted solver, not per-link per-tick scans. Cached body volume and
  level, batched withdrawals per body, a fixed cadence with elapsed-tick integration (1.6 ticks Things with a variable
  `TickInterval(int delta)`, MEASURED, `Verse/ThingWithComps.cs:334`), a convergence tolerance, terrain repaint only past
  a visible threshold, and invalidation on topology change. Benchmark: a 325×325 map, two 40,000-cell basins, 200 links.
- Conduction **inside** a pipe net stays height-blind; levelling is a boundary rule between bodies, not pressure.

### P7. Flooded decks

A sunken deck can be awash (`flowworks_bridges_design_2026-10-17.md` allows water over a deck), so the pre-ruling "decks
sit above the fill, flooding does nothing" is withdrawn. Whether a submerged cord shorts is not ruled (Q1). Rigid lines
never lie on a dug square, so a filling pit cannot submerge one.

### P8. Map and gravship identity

Every line, edge and body link is scoped to its map; no utility edge joins two maps. Gravship relocation calls
`PreSwapMap`/`PostSwapMap` (MEASURED, `Verse/Thing.cs:2212-2217`, `RimWorld/GravshipPlacementUtility.cs:172`), and a pole
or link on a gravship re-keys there instead of running support loss. A pole span crossing the ship boundary has no ruled
policy (drawbridge doc Q4 asks the same).

### P9. Readout

Line art and inspect text distinguish: cord on a deck, pole-supported span, hose down a ramp or ladder, disconnected
segment (raised leaf), and a levelling link with its state (flowing, level, stopped: intake exposed, stopped: different
liquids). Use the existing port labels; do not revive the deferred flow-direction display.

### P10. Build order and cost

ESTIMATE, pending feasibility: crossing policy + tag + dig-break + teardown 2 to 3 d; pipe poles and the liquid aerial
edge 4 to 6 d plus art after the width look; hose transitions 1 to 1.5 d; power cord 1.5 to 2 d plus art; levelling
solver 3 to 5 d. Live: pipe and cord on a rope deck; overload the span and read both nets split; dig under a pipe;
drain a pit through a ladder hose; level two ponds of unequal height, then two of different liquids.


## Owner's follow-up answers (question cards, 2026-10-20, late evening). These override the Ruled design where they differ.

- **Cord on a flooded deck:** cords are insulated. Flooding does not short them or cut them.
- **Canals:** any dug channel blocks rigid pipe and conduit, the way a pit does, whatever its depth. A pit, a trench or a canal of any depth needs pipe poles to cross.

## Owner questions as asked (ANSWERED, see the next section)

1. **A deck goes under water with a power cord on it.** The cord shorts and stops carrying power until dry · the cord
   keeps working · write-in.
2. **Does a shallow 1 m dug canal block pipes and conduit like a pit?** Yes, any dug square (as written) · only pits 2 m
   or deeper; a 1 m ditch can be crossed on the ground · write-in.

## Owner's answers (question cards, 2026-10-20 evening)

1. **Approach**, in his words: *"Pipes get a version of the power pole: supports that provide a somewhat saggy hose between them. Same mechanics, just much thicker and less flexible. Same art variation. Otherwise conduit does not cross bridges or moats or pits without this. Can't build there. Digging a pit destroys them."*
2. **Digging a pit under an existing line:** the line breaks.
3. **Pit cover:** a cover cannot carry a line.
4. **Rope bridges:** carry hoses and cords, but not pipes. This was clarified on a follow-up card: hoses and power cords may lie on **any** bridge deck. Only rigid pipe and conduit need pipe poles to cross.
5. **Hose into a pit:** yes. A hose may run down ramps and hang down ladders into a pit, to drain it or fill it.
6. **What can cross a drawbridge leaf:** not asked. By answers 1 and 4, hoses and cords may lie on it, while pipe and conduit need poles.
7. **Gravity**, in his words: *"Tanks already empty by gravity themselves, slowly. That would still be true here. Just extend that: connecting two bodies of water will cause them to slowly flow from one to the other until they level out. Let's see if we can do this"*.
8. **Width first:** settle a pipe and hose width spec, and judge it in game, before any pipe-pole art is made.

## Appendix: options considered (pre-ruling, one line each)

- **A, Floor run** (lines down the wall, along the floor, up): rejected; rigid lines may not be built on a dug square.
  Only hoses go down, and only by ramp or ladder.
- **B, Ride the deck** (lines cross only on a bridge that carries them): kept for hoses and cords only; rigid pipe and
  conduit may not ride any deck.
- **C, Hung span** (lines hang between lip posts): chosen for rigid pipe as pipe poles; conduit already has GSS power
  poles. Hoses do not hang between posts.
- **Height** (pumps do all lifting vs gravity): gravity levelling between world bodies chosen, siphon always.
- What the pre-ruling read of today's code found, still true: digging leaves lines spawned and conducting across the
  hole; a span collapse leaves lines spawned; no line reads depth. The ruled design replaces all three behaviours.
