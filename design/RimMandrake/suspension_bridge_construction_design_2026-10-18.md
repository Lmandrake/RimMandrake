# Suspension bridge: how it is built (DESIGN, 2026-10-18)

**Design only: nothing in code, defs, the bridge or the game was touched.** Every question ruled 2026-10-18 (end of
file); build items listed in the parent's §10. Parent design:
`design/RimMandrake/flowworks_bridges_design_2026-10-17.md` (the span design; its §6 tiers, §6.3 collapse and the
answered Q1/Q2 in §11 are inputs here). Epic: `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (R8 amended 2026-10-18). Vanilla
facts below were read with RimSage (1.6 decompile and defs) on 2026-10-18; anything not read is marked UNMEASURED.
Numbers are ESTIMATES or playtest starting points, never measurements.

Owner, verbatim (2026-10-18):
- Name: *"Suspension bridge"*.
- Q1: *"These are not "Bridges" in the sense Rimworld normally uses... Something that shows they're not pier/pyle-type
  bridges over water. You can walk "under" them. Likely a building type."*
- Q2: walk-under yes, *"but only for these new bridges uniquely, NOT actual tunnels."*
- This pass: *"we need to make some rulings now on how they get built (are they like free tiles you "add on to" like a
  wall is built? Or do they only come in certain widths and lengths and must simply fit? They should have guardrail vs.
  open designs too. And are cantilevers permitted?"*

Fixed by LAW 1 (*"We dig down. We never build up."*): a suspension bridge sits at the **surface** (deck height 0), or,
as a **sunken bridge**, at a ledge's height inside a deeper hole (parent §5.1; reached from a ledge, ramp or ladder,
parent Q7). Nothing is ever raised above ground. It crosses **dug** ground, and (parent Q5) is designed toward natural
rivers, large lakes and the ocean too. "Walk under" means: pawns down in the hole pass beneath it.

## Summary (as ruled 2026-10-18)

- **Construction model: the hybrid, "drag like a wall".** You drag a line (or a narrow rectangle) across a dug hole, like a
  wall; the drag must start and end on solid surface ground; the game puts an **anchor** at each end; each cell of the
  deck is its own 1×1 piece, built from the ends inward. Free length up to the tier's limit, width 1 to 3.
- **Guardrail vs open: one deck, railings as a per-bridge switch** (a gizmo that orders railings built or removed).
  Railings stop falls and give **no cover**; open edges let pawns drop down on purpose and fall off by accident.
- **Cantilevers: a short jetty only**, 1 to 2 cells out from solid ground, one person's weight (§3).
- **Walk-under clearance: the floor under a deck must be at least 2 m below it**; shallower holes are spanned but are a
  wall to anyone down there.
- **Collapse hits whoever is underneath like a roof collapse**; the wreck blocks the floor until cleared.
- **ESTIMATE: about 7.5 to 11 agent-days for this construction layer** including the jetty (on top of the parent's
  S0), of which walk-under drawing and pathing are the risky half.

## 1. Construction model

### 1.1 How vanilla 1.6 builds things that cover ground (read, not guessed)

| thing | how it is placed | relevant fact |
|---|---|---|
| walls | `Designator_Build`, one Blueprint then Frame **per cell**; `drawStyleCategory` `Walls` | lines and rectangles by drag; each cell is independent; the drag is never validated as a whole |
| vanilla `Bridge` / `HeavyBridge` | a **TerrainDef** (floor), per cell; gated by the `Bridgeable` affordance | no length rule at all; no end condition |
| Odyssey `Substructure` (gravship deck) | TerrainDef, `drawStyleCategory` `Floors`, `isFoundation`, `layerable`; PlaceWorkers `PlaceWorker_InSubstructureFootprint` + `PlaceWorker_BuildingsValidOverSubstructure` | the only vanilla "range from an anchor" rule: a cell must lie inside the grav engine's footprint (`GravshipUtility.InsideFootprint`), and the engine's `SubstructureSupport` stat caps the connected count (`Building_GravEngine.cs:445`). Validation is **per cell**, against an anchor that already exists |
| multi-cell buildings | one Thing with `<size>`, rotated by `Rot4`; one Blueprint, one Frame | must fit whole; one hit-point pool; one texture per rotation |
| drag shapes | `DrawStyle_Line`, `_AngledLine`, `_FilledRectangle`, `_EmptyRectangle`, `_FilledOval`, `_EmptyOval`; categories include `Walls`, `Floors`, `Foundations`, `FilledRectangle` | `Designator.DesignateMultiCell(IEnumerable<IntVec3>)` is virtual (`Designator.cs:261`): **a custom designator can see and refuse the whole drag**, which a PlaceWorker cannot |

So a PlaceWorker answers "may this one cell take a piece?"; only a custom designator (subclass of `Designator_Build`)
can answer "does this drag reach ground at both ends?". Every option below that has an end rule needs that designator.

### 1.2 The three models

| | **A. Free tiles, wall-style** | **B. Fixed sizes that must fit** | **C. Hybrid: drag anchor to anchor (ruled)** |
|---|---|---|---|
| what the player does | drags deck cells anywhere over a hole; each must be within N cells of support (counting planned cells) | picks "Suspension bridge 1×5" (or 2×7…) and places it so both ends land on ground | drags a line or a 1-3 wide rectangle; it must begin and end on solid ground; anchors appear at both ends |
| engine shape | 1×1 building per cell; PlaceWorker per cell; a span record built from connectivity afterwards | one multi-cell Thing with `<size>`; one PlaceWorker checks ends on ground and middle over a 2 m+ hole | 1×1 building per cell plus 2 anchor buildings; custom `Designator_Build` checks the whole drag in `DesignateMultiCell`; a map component records "this span = these cells between these anchors" |
| odd shapes (L-bends, T-junctions, wide plazas) | yes, freely | no | straight runs only; a bend is two bridges meeting on solid ground or a tower (see Q on towers) |
| fits any dug trench | yes | **only if he digs to the bridge's size** | yes, any length up to the tier limit |
| what holds it, legibly | unclear: a blob of tiles has no visible ends | obvious | obvious: two anchors, one line |
| load and collapse | per connected blob between supports (parent §6.2) | trivial: one Thing | per span record: whole span between its two anchors |
| art | deck tile linked + railing linked, per style | **one large texture per size × rotation × style × rail/open** (6 sizes gives about 96 images) | deck tile linked + railing linked + anchor (Graphic_Multi), per style |
| build feel | cells go up in any order, so a "floating" middle cell can exist mid-build | appears all at once from one frame | built from the anchors inward; a half-built span is visibly half a bridge |
| ESTIMATE | 2 to 3 days | 2 to 3 days + heavy art | 3 to 4 days |

**Ruled: C** (owner, by card: drag like a wall). It is the only one that is both honest (a suspension bridge visibly hangs between two ends) and
flexible (any trench length). A is the cheapest code but reads as "floor you paint over holes", which is exactly the
vanilla bridge he said these are not. B looks the best per bridge but forces the player to dig to a catalogue and
multiplies art by every size.

### 1.3 Anchor and support rules (model C)

- **An end must be solid ground at the deck's height**: not dug (or, for a sunken bridge, a ledge at its height), not
  water, no edifice. The anchor is a small 1×1 building
  (posts or a pylon) on that cell, built first; the deck cells next to it are built next.
- **Width 1 to 3** (ruled). Each row of a wide bridge shares the two anchor cells' line; a 3-wide bridge has 3
  anchors per end (or one wide anchor; art choice).
- **Every deck cell must cover a dug hole** at least 0.5 m deep (parent rule 3), **or natural water** (rivers, large
  lakes, the ocean: parent Q5, designed toward, may be backtracked). A drag that passes over undug ground
  in the middle is refused ("a bridge must cross a hole without touching down"): touching down means it is two bridges.
- **Maximum length (anchor to anchor), by tier**, from the parent's §6.1, re-read for a suspension bridge: rope 8,
  timber 6, steel 10, heavy 14 cells (proposals; rope is longer than timber because rope bridges are). A longer gap
  needs a **tower**: a pillar built on the hole's floor that counts as an anchor in the middle (the parent's "pier",
  renamed; it splits the bridge into two spans). Towers need someone to reach the floor to build them (in natural water:
  a builder wading or swimming to it; how is owed to `SUSPENSION_WATERS_BUILD_MAY_BACKTRACK`).
- **Building order**: the builder stands on an anchor or on a finished deck cell next to the one being built. A cell
  whose neighbours toward both anchors are unbuilt cannot be started. No scaffolding, no flying builders.
- **Deconstruct an anchor** = the span it holds falls (§4). The game asks first.

### 1.4 Walk-under: how it is represented (ruled in: pawns only, 2 m clearance)

Pawns draw at one altitude (`AltitudeLayer.Pawn` = 23 of 40; `PawnRenderer` already moves flying pawns' draw height,
line 179, so moving a pawn's draw height by state is an engine-sanctioned pattern). Proposal:

- **Two bands per decked cell, nothing else gets two.** A decked cell has the **deck band** (surface, everyone who
  crossed from an anchor) and the **floor band** (the trench floor, everyone who walked in along the trench). A pawn's
  band is the pocket it is in; the pocket grid (`RM_PocketGrid.cs`) already gives each depth band its own passability,
  and P2 (`PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH`) is proving the per-request mask swap that this rides on.
- **Clearance**: the floor band is walkable under the deck only if the floor is **at least 2 m below** the deck. A
  shallower hole is spanned but is a wall from below (the parent's §5.2 consequence).
- **Drawing**: the deck draws above floor-band pawns (deck at an altitude between `Pawn` and `PawnState`), and deck-band
  pawns are raised above the deck by a draw-height offset (Harmony, the flying-pawn pattern). Optional: the deck fades
  toward see-through while a colonist is under it, so you can find your people. UNMEASURED: shadows, apparel layers,
  and whether 1.6's draw batching respects a per-pawn altitude change; the risk row in §6 says so.
- **Things under a deck stay simple**: no item can rest, and no building can stand, under a deck. Anything dropped there
  slides to the nearest open floor cell. Corpses too. Only pawns pass beneath.
- **Shooting between bands**: a **solid** deck blocks shots between someone on it and someone under it; a **grated**
  deck does not (LAW 2: no height advantage, so a grate is just a fence-like gap). Shots within a band ignore the deck.
- **Clicking**: deck band first; a second click cycles to the floor band (vanilla click-cycling).
- **"NOT actual tunnels"**: the band exists only under a suspension bridge's deck cells. No roof, no dug passage, no
  other building ever grants a floor band. The code check is "is there a suspension deck here", never "is the cell
  covered".

## 2. Guardrails vs open

| effect | railed edge | open edge |
|---|---|---|
| falling off by accident (downed, staggered by a blast, fleeing in panic, slipping on slime) | **never** | a chance per event (proposal: blast or stagger on an edge cell 25%; slime slip on an edge 10%) to fall into the hole: the existing descent event, fall damage by metres (V3) |
| dropping down on purpose | no | yes: an open edge is a one-way way down into the trench (a jump of `F` metres, same fall rule; pathing uses it only when told, like a ladder) |
| pathing | the edge is a wall | the edge is a drop, not a walkway; nobody routes off it unasked |
| enemies | cannot be thrown off | a raider downed on an open bridge over a pit ends up in the pit: the trap value of open bridges |
| cover for pawns on the deck | **none (ruled)**: a railing is waist-high cable and mesh, not sandbags; and vanilla cover is read from neighbouring cells, so a railing on the pawn's own cell would need a new rule | none |
| cost | more material (proposal: +50% of the deck's cost) and more work | base |

**Knockback**: only stagger, blasts and `RM_SlimeSlip`; a melee "shove off the bridge" is a new mechanic, not proposed.

### 2.1 How a railing is represented

| | per-bridge switch (ruled) | separate def ("railed" / "open") | railing as its own thin building per cell |
|---|---|---|---|
| player choice | one gizmo on the bridge: "Railings: on / off"; orders the railing work | choose at build time; change = rebuild | any cell, any edge |
| what it draws | railings on every open (non-deck) edge, automatically | same | same, per cell |
| defs per style | 1 deck def | 2 | 2 (deck + railing) |
| code (ESTIMATE) | 0.5 day: a span flag + an "add railings" job | 0.25 day | 1 day: edge-linked building on a deck cell |

A railing is drawn on a deck cell's edges that do **not** touch another deck cell or an anchor: that is a linked
graphic (`Graphic_Linked` family; `LinkFlags.Custom1`..`Custom10` are free for our own linking, `LinkFlags.cs`).
UNMEASURED: which linked subclass suits an edge-only railing on a 1×1 non-edifice building.

## 3. Cantilevers

A cantilever is deck that sticks out past its last support with nothing at the far end.

- **Ruled: a short jetty only** (owner, by card; against the "none in v1" recommendation). Free overhangs are out.
- **Support:** a jetty starts from an anchor on solid ground at the deck's height (its own, or a bridge's) and reaches
  1 to 2 cells out over a hole or water; no far end. Steel or heavy tier only; railed on its three open sides by
  default, the same railing switch as a bridge.
- **Load:** capped at one person's weight (proposal 120 kg, × the load multiplier), shown in the inspect pane like a
  bridge's.
- **Collapse:** it fails **at the root**: the whole overhang drops at once (descent for those on it, roof-collapse hit
  for those below). Losing its anchor drops it.
- Its use: a platform over a pit or trench to push prisoners from, fish from, or pour from. ESTIMATE 1.5 days,
  +4 textures. Item: `SUSPENSION_JETTY_BUILD_WALK_THE_PLANK`.

## 4. Collapse and load (with the parent's Q3)

- **Load is per span** (anchor to anchor, or anchor to tower): pawns, items and buildings on the deck. Pawns under it
  weigh nothing on it.
- **Weight (parent Q3 ruled yes, load shown)**: a span over its rating sags (a warning in the inspect pane and a creak
  sound at 90%) and then **the whole span** goes at once. A suspension bridge does not unzip cell by cell; it swings
  down cell by cell only when one anchor is lost (falling from the lost end toward the kept one). Hit points to zero in
  any one cell also drops the whole span.
- **Walk-under consequence (ruled Q6)**: a falling deck lands on the floor band. Pawns under it are hit like a roof
  collapse (the vanilla scale), and the debris (filth or a skip) blocks the floor cells until cleared. Pawns on it descend through the existing event (fall damage by metres; water or fire below as the parent's §3).

## 5. Art

| asset | class | per style | × 4 styles |
|---|---|---|---|
| deck tile, solid | linked (`Graphic_Linked` family) so a run reads as one deck | 1 | 4 |
| deck tile, grated | linked, real alpha holes (the liquid or the floor-band pawns show through) | 1 | 4 |
| railing edge set | linked, drawn on open edges only | 1 | 4 |
| anchor (posts / pylon), facing the span | `Graphic_Multi` (north, south, east; west mirrors east) | 1 | 4 |
| tower | `Graphic_Single` seen from above | 1 | 4 |
| collapse debris on the floor | filth or skip | 1 | 4 |
| jetty | `Graphic_Multi` | 1 | 4 |

**About 28 textures, jetty included**, replacing the parent's §8 deck/railing/pier rows. Model B would instead need one
large texture per size × rotation × style × rail/open. The rope tier stays Scrapper-only. Every texture is shown to him
at true scale beside a vanilla human before it ships, including one shot of a pawn passing under a deck, because that is
the picture that proves the idea. Search `artpipe_state.py find` and existing sheets for deck, catwalk or rope-bridge
art first.

## 6. Cost (ESTIMATED agent-days) and risks

| piece | ESTIMATE | depends on |
|---|---|---|
| custom designator: drag anchor-to-anchor, width 1-3, refusals with reasons | 1 to 1.5 | parent S0 |
| anchors, span record, build order from ends inward, length per tier, towers | 1.5 to 2 | the above |
| railings switch, open-edge falls and deliberate drops | 1 | the above |
| walk-under: two bands in the pocket grid, draw heights, nothing-rests-under rule, shots between bands, click cycling | 2.5 to 4 | P2 proved |
| collapse as a whole span, swing-down on anchor loss, crush below | 0.5 to 1 | parent S1 |
| jetty | 1.5 | the above |
| **total** | **about 7.5 to 11**, plus about 1 day live on the minimal list | |

| risk | why | fallback |
|---|---|---|
| walk-under drawing breaks in 1.6's render batching (UNMEASURED) | pawns are drawn in batches by altitude; a per-pawn offset may not take | draw the deck semi-transparent over floor-band pawns instead of re-layering anyone |
| per-request mask swap under multithreaded pathing (P2's question) | two bands in one cell rely on it | until P2 passes, ship decks with no walk-under (a wall from below), add the band later |
| raid AI and the floor band | raiders in a moat now walk under bridges instead of being stopped by them | that is the ruling; worth one line on the raider card |
| "NOT tunnels" erodes | every later request ("a roof I can walk under") will cite this | the band is keyed to one building class; refuse in review |

## Owner answers 2026-10-18 (by card)

1. Build: **drag across like a wall**, 1-3 wide, solid ground at both ends.
2. Length: **a limit per type plus towers** on the hole floor.
3. Guardrails: **an on/off switch per bridge**; railings off = knock/slip/jump off.
4. Rail cover: **no, safety only**.
5. Cantilevers: **short jetty, 1-2 squares** (one person's weight) — not the recommendation; its support and collapse rules are §3.
6. Collapse: **hit like a roof collapse**; the wreck blocks the trench until cleared.
7. Clearance: **at least 2 m** to walk under.
