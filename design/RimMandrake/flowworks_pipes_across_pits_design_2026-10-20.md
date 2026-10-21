# FlowWorks — pipes, hoses and power conduit across pits (DESIGN, 2026-10-20)

Owner, verbatim (2026-10-20): *"Do a background design pass. We need to think about how pipes and conduit work across
pits."*

**Design only.** Nothing in code, defs, the bridge or the game was touched. Code claims are file:line at HEAD
`100c3d7252` (paths under `src/RimMandrake/FlowWorks/` unless stated). Anything not read is marked UNMEASURED. No live
check was run, so every "today" below is **read from code, not seen in game**.

Rulings this pass obeys (all owner): a pit is a SUPERDEEP cell, not a building
(`infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`); R8, no real z-levels, amended only so pawns walk **under**
a suspension bridge (*"only for these new bridges uniquely, NOT actual tunnels."*); **nothing rests and no building
stands under a deck** (`design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md` §1.4); by card
2026-10-20: a pit cover drops whoever stands on it when destroyed or deconstructed; a pawn walks under a bridge deck;
**each side of a pump takes one port, either a pipe or a hose** (`flowworks_bars_answers_2026-10-20.md` #21); pipe and
hose art need a better width definition (#22, *"Colonists don't have arms. Need an in-game look"*). Drawbridges are
designed in parallel (`flowworks_drawbridge_design_2026-10-20.md`); this doc only says how a line crosses one.

---

## Summary

- **Nobody has designed this before.** Searched `src/`, `design/`, `infrastructure/state/items` and `closed/` for
  pipe/conduit/hose/cable against pit/trench/span/deck/bridge: no prior design, no item. The hose code's only bridge
  mention is a cost comment (`Source/Hose/RM_MapComponent_Hoses.cs:182-183`).
- **Today, every line ignores the pit.** Digging never touches a pipe or conduit; a pipe or conduit can be built on a
  pit floor; the line keeps conducting across the hole and is drawn at ground level as if the hole were not there.
  Details in §2.
- **Three approaches (§3):** **A. Floor run** (lines follow the hole down the wall, along the floor and up);
  **B. Ride the deck** (lines cross only on a suspension bridge, or a pit cover, that carries them; open pit squares
  refuse them); **C. Hung span** (lines cross in the air between two lip posts, as GimmeSomeSlack's overhead power
  already does, extended to hoses and pipes).
- **Recommendation: B, with GSS overhead wires kept as power's second route.** Reason: the suspension deck already
  lends `Light` to whatever is built on it, so most of B exists; it needs one refusal, one dig rule and one collapse
  rule, not a new net edge or a new draw layer.

---

## 1. What already exists (searched first)

| thing | where | what it gives this design |
|---|---|---|
| rigid pipe `RM_UniversalPipe` | `Defs/Machinery/RM_LiquidLogistics.xml:23-87` | FlowWorks' own def (not VE PipeSystem): `BuildingBase`, `isEdifice false`, layer `FloorEmplacement`, Standable, draws like a conduit, 100 HP, flammability 0.4, 2 steel. No `terrainAffordanceNeeded` of its own (inherits `BuildingBase`'s; see §1.1). Four looks by `ThingStyleDef` (`RM_UniversalPipeStyles.xml`) |
| liquid net | `Source/Machinery/RM_LiquidNet.cs`, `RM_LiquidNetKernel.cs:6-14,60-64` | cardinal pipe conduction; a component over `MaxConductors` is refused whole. **No elevation, head, pressure or gravity anywhere** in the net or hose flow (grep of `RM_LiquidNet*`, `RM_LiquidTransfer`, `HoseFlow`, `HoseMath`) |
| pump | `Source/LiquidTypes/Building_LiquidPump.cs:23-25,191,277`; `RM_PumpMath.cs:15-60` | draws from / pours into a dug channel beside it; ports found by `RM_LiquidNet.PortsOf(…, Intake/Outflow)`. Reach is x/z footprint distance, height-blind. The only gravity word is a *rate* rule for Dump tanks |
| spill | `Source/Machinery/RM_LiquidSpill.cs:16-90` | an Outflow end pours into an excavated cell (or one within 1.5 cells), a pond, or filth on dry ground. **No leak, rupture or break-spill on a pipe.** (Propane rupture/valve exist only in `src/RimUtinni/PropaneLakeMechanics/`, a separate mod) |
| hose | `Source/Hose/HoseMath.cs:106-108,176-182,507-525,1165`; `RM_MapComponent_Hoses.cs:97-125` | free-path 8-way A* on a `CordWorld`; fog, rock, walls and impassable buildings block; water costs 3 ("a hose floats"); **no depth or pit test**. Laid shape is a 2-D rope settle (bend radius 1.2 cells, slack budget); **no vertical sag**. Width `FlatVisible`/`PlumpExtra` × `WidthScale` (shipped 1); a 0.65 thickness proposal sits unshipped (`Machinery/LiquidJoinRule.cs:107-111`) |
| pit terrain | `Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml:32-141` | `RM_Channel_Empty/Mid/Deep` carry `Walkable, Light, Diggable`; `RM_Channel_Superdeep` (every square 2 m or deeper; the true depth is the grid) carries **`Light` only** |
| dig | `Source/Designator_DigCanal.cs:67-110`; `RM_MapComponent_Excavation.cs:1461-1511`; `JobDriver_DigCanal.cs:95-115` | refuses a square with an **edifice** or a floor; refuses under any suspension part (`RM_Patch_DigRefusedUnderSuspension`). `Deepen` only writes depth and terrain: **no Thing on the square is checked or destroyed** |
| span base, pit cover | `Source/Pits/Building_SpanDeck.cs:22,76-117,142,219-228`; `Building_PitCover.cs:133-188,256,288-309` | collapse = mark span, `Vanish` each deck, rubble filth, each pawn falls through `RM_SuperdeepTrap.OnForcedDescent`. Comment `:228`: *"Items and buildings on a deck are the POSTS item's to add"* — **not handled**. Cover `DeSpawn` drops its pawns on kill or deconstruct; a blast springs the whole cover |
| suspension bridge | `Source/Pits/Suspension/` | `RM_Patch_SuspensionAffordance` (`RM_SuspensionPatches.cs:53-111`): a built deck **lends affordances**: timber Light, steel Light+Medium, heavy all three, **rope none**; railings need a deck. Vanilla bridges refused over dug ground (`:113-`). Whole-span collapse on kill/deconstruct (`Building_SuspensionDeck.cs:209-224`), swing-down on a lost anchor (`:289-364`) |
| underpass | `Source/RM_SpanMath.cs:76-78`; `RM_PitExposure.cs:34-36`; `SelfTest/UnderpassReachChecks.cs` | floor ≥ 2 m below a suspension deck: pawns walk under it; exposed, not roofed. Items sliding out from under a deck: `SlideOut` in `RM_SuspensionPatches.cs` |
| pawn sink draw | `Source/Superdeep/RM_PitDepthDraw.cs:29,141-173` | **pawns** in a dug square are drawn sunk; **buildings are not** |
| GSS overhead power | `src/RimMandrake/GimmeSomeSlack/Source/Aerial/` | masts, lamp masts and wall brackets carry power on **sagging overhead wires**: `maxSpan` 20 cells (slider 8-40), `sag` 6 % of span (`AerialSettings.cs:25-27,124,148-158`); per-look poles and span wire (`AerialMaterials.cs:10-19`); wire-down alert, restring job, **fallen live wire shocks and ignites FlowWorks' burnable liquid** (`RM_FallenWireShock.cs:23,233-281`) |

### 1.1 Vanilla and GSS facts (from the parallel research read)

- **Vanilla `PowerConduit`** (RimSage, merged def): `terrainAffordanceNeeded Light`, altitude `Conduits`,
  `isEdifice false`, `clearBuildingArea false`, Standable, `isPowerConduit`, `PlaceWorker_Conduit`; goes under walls and
  buildings. So it is placeable on every channel terrain, superdeep included, and the dig designator does not refuse it.
- **Vanilla never re-checks a finished building when the terrain under it changes.** `TerrainGrid.DoTerrainChangedEffects`
  cancels **blueprints and frames** that fail `GenConstruct.CanBuildOnTerrain` (`DestroyMode.Cancel`), kills plants and
  filth, and notifies; a completed conduit on terrain that no longer gives its affordance stays. The one built-in "falls
  with its support" rule is a terrain's `destroyBuildingsOnDestroyed` (vanilla `Bridge`), and it kills only the
  **first** building on the cell (`Notify_TerrainDestroyed`). FlowWorks' `Deepen` goes through `SetTerrain`, so a
  **blueprint or frame** of a non-`Light` thing on a square being dug is cancelled; every channel terrain keeps `Light`,
  so a line's blueprint survives.
- **Vanilla water and conduits:** only shallow and chest-deep water carry `WaterproofConduitable`; deep water carries
  no affordances (`flowworks_natural_water_engine_2026-10-17.md:93,195`). Nothing re-checks a conduit when a pit fills.
- **VEF PipeSystem pipes:** VEF ships the code, not a pipe base def; each mod defines its own. One sample measured,
  Alpha Biomes' `AB_PropanePipe` (workshop `1841354677/1.6/Defs/NetDefs/PropaneNet.xml`): the same setup as
  `PowerConduit` (`Conduits` layer, not an edifice, `Light`, `PipeSystem.PlaceWorker_Pipe`) **plus
  `CompProperties_SpillWhenDamaged`** (filth spill below a third of HP). So VE pipes sit on pit floors exactly as ours
  do. Other mods' pipes UNMEASURED. FlowWorks' pipe is its own def; VE nets join only through the chemfuel adapter
  (`Patches/Machinery/RM_PipeNetAdapters.xml`, a 1×1 PassThroughOnly building).
- **GSS:** vanilla conduits are **restyled, not replaced**: `Patches/RM_ConduitStyleable.xml` adds the style comp, and
  `ConduitVisuals.cs:10-40` hides the vanilla graphic so GSS draws cords. Overhead span sag is a parabola,
  `P(t) = lerp(A,B,t) + (0, −sag·4t(1−t))`, `sag = sagFactor·|AB|`, sampled every ~0.5 cell
  (`Aerial/AerialMath.cs:87-103`), with drip loops at each end (`:203-221`, depth 0.12, reach 0.45) and a ground shadow
  (`:245`). Anchors need `Light` (`Defs/Aerial/RM_AerialAnchors.xml:30`). **No GSS code reads terrain, depth or pits**:
  an overhead span over a pit already works and draws correctly, because it is drawn from its anchors only. There is no
  ruling "pipes rigid, hoses sag"; rigid vs flexible is a purpose split (permanent vs fast deployment, GSS ruling 1).

---

## 2. What happens today (read from code)

| event | pipe `RM_UniversalPipe` | vanilla power conduit | hose |
|---|---|---|---|
| a pit is dug under an existing line | **allowed**: not an edifice, so `Designator_DigCanal.cs:67-72` passes it; `Deepen` leaves it spawned. The line stays whole and keeps conducting across the hole | same: `PowerConduit` is not an edifice and needs only `Light` | the hose's `CordWorld` is rebuilt per tick asked; a pit square is walkable under the default relative pit rule, so the laid hose is kept or re-planned **straight across** at no extra cost (`RM_MapComponent_Hoses.cs:116`) |
| a line is built across an existing pit | **allowed** wherever placement needs `Light`: every channel terrain, superdeep included, carries `Light` | same | same: routes over the hole as if flat |
| how it looks | drawn at ground level over the hole: a pipe **floats across** the pit with the wall faces drawn around it. Draw order against `RM_ExcavationWalls` is UNMEASURED | same | same |
| water fills the pit | nothing: the net has no wetness; spill only at an Outflow end | nothing: vanilla never re-checks a built conduit, so it keeps carrying power under 2 m of water | nothing |
| a pawn trapped in the pit | can reach and deconstruct a floor line beside it (standard job); no rule says otherwise | same | same |
| a suspension deck carrying the line collapses | decks `Vanish`, pawns fall; **the pipe stays spawned** on the now-open square and keeps conducting (`Building_SpanDeck.cs:76-117,228`) | same | hose world re-plans; unaffected |
| a pit cover under a line is destroyed | the cover drops pawns; a pipe on its square stays (the cover's affordance is not consulted: the square under it already carries `Light`) | same | same |

**In one line: the pit is invisible to every line.** Height-blind conduction is fine and is kept by every option below;
the defects are the picture (a line floating over a hole), the missing consequences (collapse, flood) and the hose's
free crossing.

---

## 3. Three approaches

Shared by all three: **conduction stays height-blind** (no head or pressure: pumps do the lifting, as today). The
level-surface ruling already makes *open* water find its level; putting head into closed pipes would mean a second
physics for the same litres, and nothing in play asks for it. The drop matters only to the **picture**, to **damage**,
and to **who can reach the line**. Every option also fixes the measured collapse gap (§2): a line on a square whose
support goes is dealt with, never left floating.

### A. Floor run: the line follows the ground down, across and up

**How it plays.** Lines are ground things. Drag a pipe, conduit or hose across a pit and it is laid down the near wall,
along the floor and up the far wall: the "honest plumber" answer. Pits stay cheap to cross (no bridge needed) but the
line is **in** the pit: flooded with it, burned by oil fires in it, cut by whoever is trapped in it, and in the way of
the underpass. A moat with a pipe on its floor is a moat with a weak point a prisoner can wreck.

**Engine.** Keep today's placement (every channel terrain already carries `Light`), and add:
1. sink-draw for buildings on a dug square (the `RM_PitDepthDraw` offset applied to `FloorEmplacement` things and
   GSS cords), plus a **riser** piece drawn on the wall face where a run crosses the lip (a per-look sprite chosen
   from the run's neighbours, as `PipeLook` already picks pieces);
2. flood rule: a power conduit under liquid shorts (as vanilla: only `WaterproofConduitable` water takes conduit) unless
   it is a waterproof conduit; a pipe under liquid is fine; a hose floats as it already does;
3. reach: a pawn trapped below can deconstruct a floor line (today's behaviour, now named and shown);
4. **the underpass collision:** the ruling says no building stands under a deck. A floor run under a suspension
   bridge needs an exception ("non-edifice lines on the floor band only") or must refuse the square.

**Reuse.** High for logic (nothing new in the nets), low for art: risers × 4 looks × 3 line kinds × 4 facings, and a
sunk draw for buildings that has never been tried (pawns only today).

**Interactions.** Collapse: debris lands on the floor run and breaks it (vanilla damage). Fire: oil in the pit burns
the line (flammability 0.4 for pipe; conduit per its def). Cover destroyed: nothing for the line (it is underneath).
Raiders: lines in a moat become reachable from inside it (a raider who falls in can cut your power). Drawbridge: the
line runs under it on the floor, independent of whether the leaf is up or down.

**Cost (ESTIMATE).** 3 to 4.5 agent-days (sunk draw 1-1.5, risers and flood rule 1-1.5, underpass exception 0.5-1,
selftests 0.5) + 16-48 sprites. **Risk:** medium-high: the sunk building draw is 1.6 batching territory (the same
UNMEASURED risk the underpass design names). **Live test:** 1 sitting (pit with floor runs, flooded and dry, plus an
owner look at the riser).

**For:** no bridge needed; the most physically honest; flooding and fire have real stakes. **Against:** most art; adds
an exception to a ruling made two days ago; a moat floor full of lines is visual clutter where the owner wants the
wall faces to carry the depth read.

### B. Ride the deck: a line crosses a hole only on something that carries it

**How it plays.** An open pit square refuses lines, with the reason *"Lines cross a pit on a bridge"*. To cross, build a
suspension bridge (or, for a short gap, a jetty) and lay the pipe, conduit or hose on its deck. The bridge becomes
infrastructure, not just a path: break the bridge and you cut the water and power with it. Power has a second route
already shipped: GSS overhead wires on masts at each lip (§1). Pit covers do **not** carry lines (a line on a cover
gives the trap away; ruled question Q3 below).

**Engine.** Almost all built:
1. **Placement**: a `CanBuildOnTerrain` postfix sibling to `RM_Patch_SuspensionAffordance`: on an excavated square, a
   pipe, a GSS cord or a vanilla conduit is placeable only where a built deck lends `Light` (timber, steel, heavy;
   rope lends none, so rope bridges carry no lines unless Q4 says otherwise). Pipes, conduits and cords are named by a
   list (pipe extension, `PowerConduit`-class `building.isPowerConduit`/GSS cord defs), not by "any `Light` thing".
2. **Dig**: digging a square that holds a line is refused (*"Move the line first"*), mirroring the existing refusal
   under suspension parts; the alternative (dig and drop the line as wreckage) is Q2.
3. **Collapse**: `Building_SpanDeck.Collapse` (`:76-117`) destroys the lines on its squares with `KillFinalize`
   (leavings fall into the hole as wreckage), which splits the net through the normal despawn path. This is also the
   "POSTS" gap at `:228` for lines.
4. **Hose**: `RM_MapComponent_Hoses.World()` blocks an excavated square unless it is decked (a hose may also run down a
   ramp and along a dry floor if Q5 allows; then it is a floor hose, not a crossing).
5. **Weight**: lines weigh nothing on the deck (a 2-steel pipe square is under 2 kg; not worth a rule).

**Reuse.** Very high: the affordance-lending patch, the collapse path, the dig refusal pattern and the hose grid all
exist; the line draws at ground level, which on a deck **is** the deck's height, so today's art is already right.

**Art.** None required. Optional: a pipe-under-deck-edge clamp sprite per look (the pipe hugging the deck side rather
than lying on the walking surface); waits on the width spec the owner asked for (#22).

**Interactions.** Collapse: the line breaks with the span; liquid in the broken pipe is lost (no spill picture
needed: nets hold no per-pipe stock); a GSS cord on the deck becomes a **fallen live wire** in the hole
(`RM_FallenWireShock` already shocks and ignites oil there). Cover destroyed: no line ever stood on it. Fire on a
grated deck: fire below reaches the line through the grate (the grate rule already passes fire). Flooding: decks sit
above the fill; nothing. Raiders: to cut your lines they must reach or break the bridge, which is the same target as
cutting your path; trapped pawns below cannot reach a line on a deck. Underpass: pawns walk under the deck and the
line on it, no conflict with "no building under a deck". Drawbridge: a raised leaf **breaks** a rigid pipe or conduit
on it unless it carries a flexible joint; the simple rule is "only a hose may cross a drawbridge leaf" (hand to the
drawbridge pass, Q6).

**Cost (ESTIMATE).** 1.5 to 2.5 agent-days (placement + dig refusal 0.5-1, collapse + hose block 0.5-1, selftests
0.5). **Risk:** low: every hook is one the bridge work already patches. **Live test:** half a sitting, folded into the
next suspension-bridge session (lay a pipe and a cord on a steel span, overload it, read the nets split).

**For:** cheapest; no new physics, no new draw layer; makes bridges matter; keeps the underpass ruling clean.
**Against:** a player must build a bridge before plumbing across a 3-square ditch, which may feel heavy-handed early
game; refuses something that works today (a save with lines on pit floors needs a one-time migration: leave them,
flag them in the inspect pane, or drop them; Q2).

### C. Hung span: lines cross in the air between two lip posts

**How it plays.** Lines leap holes. Build a **pipe gantry** (a post at each lip, like a GSS mast) and the pipe or hose
is hung between them; power already does this with GSS masts. Hoses sling between two hose hooks and sag; rigid pipe
spans on a light truss (no sag, it is rigid) up to a short limit; power sags on its existing 6 % rule. Nothing is on
the floor and nothing is on the deck, so the line is independent of bridges, covers and drawbridges entirely. Raiders
can **shoot it down**: a hung line is a building with HP on two posts, and a downed span drops into the hole (a hose
spills its stock there; a live wire shocks).

**Engine.** Generalise GSS's aerial graph (`RM_MapComponent_Aerial`, `CompAerialAnchor`, `AerialMath`) to a second
carrier: a **liquid aerial edge** that joins two pipe-net components the way a span wire joins two power nets. Needs:
a liquid post def per look; an edge kind in `RM_LiquidNetKernel` (a non-cardinal conductor between two posts; the
net's topology cache gains a long-range edge, the riskiest change in the doc); the hose re-planned as two free halves
meeting at hooks (or a hose-specific "sling" where the A* may jump an excavated run of ≤ N squares between hooks with
a catenary draw); downed-span handling copied from `Alert_WireDown` / `RestringJob`.

**Reuse.** Medium: GSS has the whole aerial apparatus for power (poles, styles, sag, wire-down, restring, fallen-wire
shock); none of it is liquid-aware, and GSS and FlowWorks are separate mods (today they talk by soft reflection,
`RM_FallenWireShock.cs:233-281`), so the shared piece must live in `RimMandrake.Shared` or one mod must depend on the
other.

**Art.** Most new art of the three: liquid post × 4 looks, pipe span (rigid truss) × 4 looks, hose sling sag drawn as
a catenary consistent with GSS's span wire (same `sag` fraction, same draw path), downed-span wreckage. The width spec
(#22) is a prerequisite: a hung pipe is drawn larger than one on the ground.

**Interactions.** Collapse of a bridge: no effect on lines. Cover destroyed: none. Flood/fire below: a hose sling
over burning oil burns (heat rises per cell already); a rigid span does not. Raiders: a new target class (a shootable
line); pathing unaffected (spans are not obstacles). Underpass: clears it by construction. Drawbridge: independent.

**Cost (ESTIMATE).** 5 to 8 agent-days (liquid aerial edge 2-3, posts/defs/styles 1-1.5, hose sling 1.5-2, wire-down
reuse 0.5-1, selftests 1) + 20-30 sprites. **Risk:** high: a long-range edge in the liquid kernel touches the net
caps, the topology cache and save compatibility; cross-mod coupling. **Live test:** 1.5 sittings (span, shoot down,
restring; one owner look at the sag).

**For:** the most legible picture (a line visibly leaping the hole, matching power lines he already approved); free of
bridge rulings; adds a satisfying raid target. **Against:** the most work and the most risk; two mods share a new core
piece; a rigid pipe in the air is the least "Jawa scavenger" look.

### Side by side

| | A floor run | B ride the deck | C hung span |
|---|---|---|---|
| crossing needs | nothing | a bridge (or GSS mast for power) | two posts |
| new physics | flood shorts conduit | none | long-range liquid edge |
| new art | risers, 16-48 | none required | posts, spans, slings, 20-30 |
| underpass ruling | needs an exception | clean | clean |
| raiders | trapped pawns cut lines | must break the bridge | can shoot lines down |
| agent-days | 3 to 4.5 | 1.5 to 2.5 | 5 to 8 |
| risk | medium-high (sunk draw) | low | high (kernel, cross-mod) |
| live | 1 sitting | ½ sitting, folded in | 1.5 sittings |

## 4. Recommendation

**B, ride the deck; power also keeps GSS overhead wires as its no-bridge route.** One line: *the suspension deck
already lends `Light` to what is built on it, so B is one refusal, one dig rule and one collapse rule on hooks we
already patch, and it is the only option that leaves the walk-under ruling untouched.*

What B answers, question by question:

| his question | B's answer |
|---|---|
| dug under an existing line | refused until the line is moved (or Q2's alternative) |
| built across a pit | refused on open squares; allowed on a timber, steel or heavy deck; power may also hang on GSS masts |
| floor, span, deck or forbidden | **deck** for pipes, conduit and hoses; **air** for power only (shipped); **floor** only by walking it down a ramp (Q5) |
| hoses | as pipes: cross on a deck; the hose world blocks open excavated squares |
| does a floor pipe flood, does pressure care about the drop | no line lies on a pit floor, so no flood case; conduction stays height-blind |
| collapse, flood, fire, bridge or cover destroyed | collapse kills the lines on the span (net splits, a cord becomes a fallen live wire that shocks and ignites oil, already built); flood: none; fire: through a grate, else per flammability; cover: never carries lines |
| look and sag | pipe on a deck draws flat on the deck (today's art); power overhead uses GSS's 6 % parabola unchanged; a hose has no sag rule because it never hangs |
| raiders, pathing, underpass | cutting lines means breaking the bridge; nobody trapped below can reach them; pawns under the deck pass under the line |
| drawbridge | a rigid line cannot cross a moving leaf; only a hose may (handed to the drawbridge pass) |

**Build order if he picks B (ESTIMATE 1.5 to 2.5 agent-days, ½ live sitting):**
1. Placement postfix + dig refusal + migration rule for existing saves (Q2). Selftests offline.
2. Collapse kills lines on its squares (closes the `Building_SpanDeck.cs:228` gap for lines; items stay POSTS' work).
3. Hose world: excavated and not decked = blocked (or ramp rule, Q5).
4. Fold the live check into the next suspension-bridge sitting: a pipe and a cord on a steel span, overload, read both
   nets split and the fallen-wire shock.

**Also true whatever he picks** (defects in today's code, independent of the choice): a built conduit under liquid keeps
working (vanilla never re-checks); a span collapse leaves its buildings spawned over the hole. File them only after his
pick, since A, B and C each fix them differently.

## 5. Open questions for the owner (each a question card)

1. **Which way do lines cross a pit?** A floor run: down the wall, along the floor, up (most honest, most art, needs an
   underpass exception) · **B ride the deck: only on a bridge; power can also hang on masts (cheapest, bridges become
   infrastructure)** · C hung span: posts at each lip, pipes and hoses hang like power lines (best picture, most work and
   risk) · write-in.
2. **A save already has a pipe or conduit on a pit floor (and the player digs under a line). What happens?** Digging is
   refused until the line is moved, and existing ones stay but read "unsupported" in the inspect pane · digging drops
   the line into the hole as wreckage (net cut) · existing and future floor lines are left alone; only new building is
   refused · write-in.
3. **Can a pit cover carry a line?** No: a line on a cover gives the trap away · yes, and the line breaks when the cover
   springs (a trap that also cuts the enemy's power) · yes, and the line survives the cover · write-in.
4. **Rope bridges and lines.** Rope carries nothing (today it lends no affordance) · rope carries hoses only (light and
   flexible) · rope carries hoses and power cords, not rigid pipe · write-in.
5. **Can a hose go down into a pit along a ramp and lie on the floor?** No: hoses never enter a pit; to fill a pit, pour
   from the lip (an Outflow end already pours into an excavated square within 1.5 cells) · yes, on a ramp or stairs only,
   never down a sheer wall · yes, anywhere a pawn could walk · write-in.
6. **(For the drawbridge pass) What crosses a drawbridge leaf?** Only a hose (it flexes when the leaf lifts) · any line,
   and raising the leaf disconnects it until lowered (like a switch) · nothing: lines cross beside it on a fixed span ·
   write-in.
7. **Should a pipe ever care about height?** No: pumps do all lifting and pipes are height-blind (today) · a downhill
   pipe flows without a pump (a siphon or gravity main; new physics, ~2 agent-days more) · write-in.
8. **Pipe and hose width (#22) before any line-on-deck art?** Decide width first, at an in-game look with a colonist
   beside a pipe and a hose · ship B with today's art and set width later · write-in.
