# FlowWorks drawbridges: three ways to build them (DESIGN, 2026-10-20)

**Design only.** Nothing in code, defs, the bridge or the game was touched. Code claims are file:line at HEAD
`1e9f157163`; vanilla claims are from the 1.6 decompile through RimSage. Anything not read is marked UNMEASURED; every
day count is an ESTIMATE.

Owner, verbatim (2026-10-20): *"Please do a design pass in the background to make Drawbridges parallel to suspension
bridges. Come up with three potential implementations to consider with tradeoffs."*

## 0. Interpretation

"Parallel to suspension bridges" is read as **a sibling in the same family**. A drawbridge spans a dug pit, trench or
canal (or the waters the suspension family reaches) exactly as a suspension bridge does, and it can also be **raised to
deny the crossing**. It is the defensive moat bridge. The suspension design already named the gap: *"A span the player
deconstructs or burns is the drawbridge the moat design was missing"* (`flowworks_bridges_design_2026-10-17.md` §7,
Raiders row). Nothing in the sources reads the request any other way.

Rulings every option obeys. Today's are by card unless quoted:
- A pit cover that is destroyed or deconstructed **drops whoever stands on it** (2026-10-20).
- The wall ladder can be **raised from below or above, lowered only from above** (2026-10-20).
- **Flyers, jumpers and floaters cross pits freely** (2026-10-20). No drawbridge stops them, raised or not.
- **A pawn walks under a bridge deck** where the floor is at least 2 m below it (Q2, 2026-10-18; R8 amended for these
  bridges only, *"NOT actual tunnels"*).
- R8: no raised ground and no cells above cells. A raised leaf is a **picture plus a state**, never a wall in the air.
- One kind of heat, every DLC assumed, and superb Mod Settings with defaults equal to shipped behaviour.

## 1. What already exists (searched first)

`grep -riE 'drawbridge|liftbridge|bascule'` over `src/`, `design/` and `infrastructure/state/items/` (closed items
included) finds **one hit**: the sentence quoted in §0. **No drawbridge has been built or filed.** Everything a drawbridge
needs is built, though:

| piece | where | what a drawbridge takes from it |
|---|---|---|
| span base | `Source/Pits/Building_SpanDeck.cs` | `Decked => !collapsed && Spawned` (not virtual today); `Collapse(fallers)` drops riders through the descent event; spawn/despawn bump `ClimbGeneration` |
| suspension deck + record | `Pits/Suspension/Building_SuspensionDeck.cs`, `RM_MapComponent_SuspensionBridges.cs` (`SuspensionBridgeRecord : IExposable`: lanes, length, anchors, towers, grated, deckNotches, jetty, style) | the dragged anchor-to-anchor bridge, load per span, whole-span collapse, the square-by-square **swing-down from a lost anchor** (`:979`), railings, underpass floor band, readout |
| pocket grid | `Superdeep/RM_PocketGrid.cs:19-31, :291` | a deck reads as ground at its height. A deck appearing or vanishing moves `ClimbGeneration`; the grid rebuilds from the map tick at most once per `RebuildMinTicks = 60`; flipped cells go to `RM_PitRooms.NotifyPitnessChanged` (`RM_PitRooms.cs:154`), which dirties regions through `map.regionDirtyer` |
| pit pathing | `Superdeep/RM_PitPathing.cs:8-44` | **vanilla's path grid never sees a pit**: an open D=4 cell is a costly *passable* cell, made impassable per request by an `IPathGridCustomizer` offset grid (>= 10000) and the cliff masks. So no drawbridge option touches vanilla's path grid |
| raisable ladder | `Superdeep/RM_LadderUtility.cs:157-260` (`RM_CompLadder.raised`, gizmo, `EffectivelyRaised`, ladder generation bump, setting `ladderRaiseLowerEnabled`) | the family's existing "raise to deny" mechanism: a per-pawn read, player gizmo only, *"no job or AI ever does"* |
| canal doors | `Superdeep/RM_FlowDoors.cs` (`Building_RM_FlowDoor : Building_Door`, sluice and security grate) | a FlowWorks door subclass already works, stuffable, with a pit rule |
| raiders vs trenches | `Superdeep/RM_RaiderTrench.cs`, item `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP` | when nothing is reachable: jump pack → scaling ladders → breach by fill; sieges shell. A raised drawbridge hands the raid to this giver |
| big creatures | `HugeThings/Source/Titanic/Clearing/TitanClearingUtility.cs`; `FlowWorks/Source/Superdeep/RM_TrenchStride.cs` | a titan **steps over** a trench of width up to its stride (B/4, card 3) through its own stride view, deck or no deck; titans clear obstacles (whether that includes a door or a raised leaf is UNMEASURED) |

**Vanilla, read through RimSage:**
- `Building_Door` opens and closes with `CheckClearReachabilityCacheBecauseOpenedOrClosed()`, which is
  `Map.reachability.ClearCacheForHostile(this)` (`Building_Door.cs:592-598`). A door is its own one-cell region, so
  **opening and closing rebuilds no region**. `BlocksPawn` / `PawnCanOpen` / `FreePassage` decide passage per pawn.
- **Odyssey has no movable bridge.** `Bridge`, `HeavyBridge` and the `Ancient*` bridges are foundation terrain
  (`TerrainDefOf`, `SectionLayer_BridgeProps`). Gravship parts move by relanding, not by a passable/impassable toggle.
  There is no vanilla or Odyssey pattern for a deck that comes and goes, so a drawbridge leaf is ours whichever option
  is chosen.

---

## 2. Option A: the Bascule (a hinged leaf with machinery)

**In one line:** a suspension bridge built from an anchor with a winch. Raising it lifts the leaf so the deck squares
stop being ground, and the hole is open again.

### In play
- **Built as** a suspension bridge whose near anchor is a **winch house**. It comes in one leaf, hinged at the winch,
  or two leaves that meet in the middle (proposal: one leaf up to 4 squares, two leaves up to 8). Timber and steel
  only; rope is too light to lift.
- **Who raises it:** the player, with a gizmo on the winch or any deck square. **Manual winch** (timber): a colonist
  goes to the winch and works it, about 4 s per square (proposal), and the leaf rises square by square from the far end.
  **Powered** (steel): about 2 s for the whole leaf with power on, and manual work with power off. Following the
  ladder ruling: **raised from either side, lowered only from the winch side**. On the far side the gizmo can raise
  it, but lowering needs a pawn at the winch.
- **Anyone on it when it raises:** the cover ruling's spirit is that a deck that goes drops its riders. So each square
  drops its pawns through `Collapse`/the descent event as it lifts, with fall damage by metres. (Open question Q2 offers
  the alternatives.) Items on the deck slide to the hinge square. Buildings are refused on a drawbridge deck.
- **Raiders:** lowered, it is a suspension bridge and they walk it. Raised, the squares are open hole, and when nothing
  else is reachable `RM_RaiderTrench` runs: jump packs, scaling ladders, then breach by fill. Sappers and breachers
  target the winch house, an edifice on solid ground. Destroying it **drops the leaf** (lowers it with a crash), which
  is the classic way to storm a drawbridge.
- **Under it:** while lowered, pawns in a moat at least 2 m deep pass under it (Q2). Raised, there is nothing overhead.

### Engine
- **Reuse:** the whole suspension machinery: drag, anchors, record, load per span, railings, readout, the swing-down
  sequencer (`:979`, which already removes squares one by one from one end; raising runs it without destroying).
- **New:** `Building_DrawbridgeDeck : Building_SuspensionDeck`; `Building_DrawbridgeWinch` (the anchor def, with a
  `CompPowerTrader` on steel); a `raisedSquares` int on `SuspensionBridgeRecord` (Scribed, default 0, so old saves
  load); a `JobDriver_WorkWinch`. **One base change:** `Decked` becomes `!collapsed && Spawned && !Raised`, with a
  virtual `Raised` that defaults to false, so every reader (`DeckAt`, the pocket grid at `:291`, the seven call sites)
  sees a raised square as open hole with no further edits.
- **Path flip cost:** each square that rises or falls bumps `ClimbGeneration` once. That means one pocket-grid rebuild
  (rate-limited to once per 60 ticks, so a whole leaf that rises in 2 s costs about two rebuilds) plus
  `NotifyPitnessChanged` for each flipped square (a region dirty in pit rooms only). The cost of one rebuild on a big
  dug map is **UNMEASURED**: it is the same cost the game already pays when a suspension deck is built or broken.
- **Save/load:** the record's `raisedSquares`. The deck Things stay spawned and keep hit points and style.
- **Done:** a raise or lower that is half-worked when the colonist is interrupted stays where it is. The record holds
  the part-way state.

### Art and facings
Lowered, it is the suspension deck tiles in the four styles. Raised, each square becomes empty hole (no deck draw), and
the **winch house draws the leaf standing upright** as an overlay, its height scaled to the raised length, for 4
facings (N/S/E/W: the leaf's hinge side). The winch house is also needed in 4 facings × 4 styles. Count: winch × 4
styles × 4 facings, plus leaf-upright × 4 styles × (1 to 4 lengths) × 4 facings. That is the largest art bill of the
three options. Check `artpipe_state.py find` first.

### Interactions
- **Water:** not an edifice, so floods and flow pass under it, raised or not. Over moving water the current spares
  riders (the fords' exemption).
- **Pit covers:** none. The drawbridge is visible, not a trap. (A "trapdoor drawbridge" is the same code with the
  cover's look. It is not proposed.)
- **Underpass:** lowered, as Q2. If a leaf rises over pawns in the floor band, they stay where they are, with open
  sky above them.
- **Big creatures:** a titan whose stride is wider than the trench steps over it either way. A creature over the
  span's load rating breaks a lowered leaf (whole-span collapse, as today).
- **Fire:** a timber leaf burns raised or lowered; a burnt square collapses the span (today's rule). A burnt winch
  drops the leaf.
- **Settings:** "Drawbridges can be built"; "Raising drops riders" (on: they fall; off: refuse to raise while occupied);
  "Raise speed ×"; "Lowered only from the winch side". All off, a drawbridge is a suspension bridge stuck lowered.

### Cost, risk, live test
- **ESTIMATE 5 to 7 agent-days** (base hook 0.5, deck/winch/record 2, job and power 1, raise sequencer and rider
  rule 1, selftests and readout 1, functional script 0.5 to 1), plus art (a separate item, like
  `SUSPENSION_ART_RESKIN_HE_SEES_FIRST`).
- **Risk: medium.** The new path is the generation bump on a *spawned* deck. That is untested; today every bump comes
  from a spawn or despawn. A reader that caches `Decked` somewhere other than through `DeckAt` would go stale
  (UNMEASURED: a grep of every `is Building_SpanDeck` read is owed).
- **Live test:** about 1 day on the minimal list: rows RAISE_PATH (a colonist re-routes), RAISE_DROPS_RIDER,
  LOWER_ONLY_FROM_WINCH, RAID_UP (a raid meets a raised bridge and falls back to `RM_RaiderTrench`), WINCH_DESTROYED_DROPS.
  These are new scenes in `suspension_bridge_proof.py`.

### Trade-offs
- **For:** this is the drawbridge players picture. It is the real denial: raised, the moat is whole again, and every
  existing pit rule (capture, climb, raiders, pit rooms) applies with no special case. It reuses most of the suspension
  code.
- **Against:** it has the largest art bill and the most new code. Every raise pays a pit-grid rebuild. The rider-drop
  rule makes raising under attack a weapon, which may be what he wants, or may be cheesy against a raid crossing the
  bridge (see Q2).

---

## 3. Option B: the Gate Leaf (a door at the bank)

**In one line:** an ordinary suspension bridge whose bank end is a **gate**, a `Building_Door` subclass. Raising the
leaf closes the gate; the deck never moves.

### In play
- **Built as** a suspension bridge plus a **Drawbridge gate** placed on the colony-side anchor square, set into the
  wall line, 1 to 3 wide to match the lanes.
- **Who raises it:** it behaves like a vanilla door. Own faction opens it as they pass (powered: auto, like an
  autodoor; unpowered: slower, by hand). "Hold raised" is the gizmo, the reverse of "hold open". Following the ladder
  ruling: the gate is **operated only from inside**. From the bridge side it is a locked door.
- **Anyone on it when it raises:** nobody stands on the gate square when it shuts (a vanilla door never closes on a
  pawn), and the deck stays put, so **nobody falls**. People out on the deck are shut out on the bridge.
- **Raiders:** the bridge is a path right up to a door. Vanilla door AI applies unchanged: they bash it, breachers
  breach it, sappers dig around it, and a siege shells it. `RM_RaiderTrench` is **not** triggered, because the far
  bank is reachable through a destroyable thing. Raiders gather on the deck, which is a kill zone the player can
  collapse.
- **Under it:** unchanged. The deck stays, so the moat below keeps its underpass.

### Engine
- **Reuse:** the suspension bridge as it is, unchanged, and `Building_RM_FlowDoor`'s pattern (a stuffable
  `Building_Door` subclass with a FlowWorks extension).
- **New:** `Building_DrawbridgeGate : Building_Door`, one def per tier and style, and a placement rule: only on a
  suspension anchor square, flush with its lanes. A raised-leaf graphic is drawn when closed.
- **Path flip cost:** **the cheapest of the three.** Vanilla door machinery means `ClearCacheForHostile` only, with no
  region rebuild, no pocket-grid rebuild and no `ClimbGeneration` bump (`Building_Door.cs:592-598`). The deck's
  reachability never changes.
- **Save/load:** vanilla `Building_Door` scribing (`openInt`, `holdOpenInt`). Nothing new.

### Art and facings
The gate needs a closed state (the leaf upright: the drawbridge look) and an open state (the leaf down, drawn as the
first deck square), in 4 styles. Doors draw rotated by `Rot4`, so 2 facings (the vanilla door convention: N/S and E/W)
are enough. This is the smallest art bill.

### Interactions
- **Water:** the gate stands on solid ground at the anchor, so floods are unaffected. If a gate is ever allowed on a
  dug square, it is an edifice and blocks floods (`RM_FerryAndLevee.cs:132-135`), so B's placement rule forbids that.
- **Pit covers:** none.
- **Underpass:** unchanged, and that is the weakness. Raiders who get down into a moat at least 2 m deep walk under
  the bridge and climb out wherever the masks allow. The gate guards the deck only.
- **Big creatures:** a door has hit points, and a titan's obstacle clearing may smash it (UNMEASURED). A big creature
  on the deck counts against the span's load as usual.
- **Fire:** it burns by stuff, like any door.
- **Settings:** "Drawbridge gates can be built"; "Gate opens for your people automatically" (on, as a door). All off,
  the gate is a door held open.

### Cost, risk, live test
- **ESTIMATE 2 to 3 agent-days** (door subclass and defs 1, placement rule 0.5, art hookup and readout 0.5, selftests
  and script 0.5 to 1).
- **Risk: low.** It is vanilla door semantics on solid ground.
- **Live test:** about 0.5 day: GATE_SHUT_BLOCKS (a colonist on the far bank routes the long way or waits),
  GATE_OPENS_FOR_OWN, RAID_BASHES_GATE.

### Trade-offs
- **For:** it is cheap, safe and engine-native. Raiders behave like they do at any door, and his rule *"no animal or
  pawn ever vanishes without a readable sign"* is easy to keep, because nobody falls.
- **Against:** it is not really a drawbridge in the moat sense. The crossing is never removed, only gated, so the moat
  adds nothing the wall does not already add. Raiders reach the gate and bash it, which is just a door with a different
  picture. If he wants the moat to deny, B does not do it.

---

## 4. Option C: the Gangplank (a deck carried in and laid out)

**In one line:** a short **portable deck**. Colonists lay it across a narrow gap and haul it back inside to deny the
crossing. It is the bridge-sized sibling of the portable ladder.

### In play
- **Built as** a minifiable plank deck, 1 to 3 squares long (proposal: timber 2, steel 3), 1 wide, crossing a trench
  between two solid banks. No anchors or towers are needed, because each end rests on a bank.
- **Who raises it:** a colonist **uninstalls** it (vanilla Uninstall work, a few seconds) and it becomes a carried
  item, stored anywhere. Laying it again is vanilla **Install** from the chosen bank. Ladder parallel: it can be
  pulled in from **either bank**, but laid only by a pawn who reaches a bank with the plank. In practice that is the
  colony side, because the plank is stored inside.
- **Anyone on it when it is pulled:** vanilla does not let a minifiable thing be uninstalled while a pawn stands on its
  square. Either we keep that (nobody falls), or under Q2's "drop" rule the cover ruling applies: a plank taken out
  from under someone drops them.
- **Raiders:** raised, the trench is open, and `RM_RaiderTrench` jumps, ladders or breaches as for any trench. They
  can also **carry their own planks**: a fourth rung on the jump → ladder → breach ladder, using the same slot code that
  places scaling ladders today. That is the natural mirror. Lowered, they walk it. They can also uninstall it from the
  far bank to cut a retreat (proposed: no; Q5).
- **Under it:** as Q2. Over at least 2 m the floor band passes under. Most planks span narrow, shallow trenches,
  where it is a wall from below.

### Engine
- **Reuse:** `Building_SpanDeck`, with a span of the plank's own squares (the cover's join rule), a load rating,
  and collapse. Vanilla `MinifiedThing`, `JobDriver_Uninstall` and `JobDriver_Install`. The scaling-ladder slot code in
  `RM_RaiderTrench`.
- **New:** `Building_Gangplank : Building_SpanDeck` (multi-square, `minifiedDef` set, placement: both end squares on
  ground at the same height and every middle square spannable); and a `CanPlaceBlueprintAt` rule. No record and no map
  component: the Thing is the state.
- **Path flip cost:** the same as building or breaking a deck today. Spawn and despawn bump `ClimbGeneration` (one
  pocket-grid rebuild), plus `NotifyPitnessChanged` for each square. There is no new invalidation path at all.
- **Save/load:** vanilla, whether spawned or minified.

### Art and facings
One deck graphic per length in 4 styles, drawn rotated (2 facings: N/S and E/W), plus the minified look (vanilla draws
a crate or the shrunken graphic). Small.

### Interactions
- **Water:** not an edifice, so floods pass. A plank over moving water: the current spares riders, as for fords.
- **Pit covers:** a gangplank must not be placed over a hidden cover. The placement rule reads `DeckAt`.
- **Underpass:** as Q2.
- **Big creatures:** a 1-wide plank carries one person's load (proposal 150 kg timber, 300 kg steel). A thrumbo on it
  breaks it, and a titan strides the trench anyway.
- **Fire:** a timber plank burns. Steel does not.
- **Settings:** "Gangplanks can be built"; "Raiders carry gangplanks" (on); "Pulling a plank drops whoever is on it"
  (follows Q2).

### Cost, risk, live test
- **ESTIMATE 2.5 to 3.5 agent-days** (building and minify 1, placement 0.5, raider plank rung 1, selftests and script
  0.5 to 1).
- **Risk: low to medium.** Install and uninstall are vanilla, and the deck plumbing already exists. The raider rung is
  new AI, but it has the scaling-ladder template.
- **Live test:** about 0.5 to 1 day: PLANK_PULL_PATH, PLANK_LAY_PATH, RAID_CARRIES_PLANK.

### Trade-offs
- **For:** it truly denies the crossing (the moat is whole once it is pulled), it is cheap, it mirrors the portable
  ladder exactly, and it gives raiders a readable counter.
- **Against:** it is only for narrow gaps (1 to 3 squares), and pulling it takes a colonist's work, so it cannot
  shut in a second when a raid appears. There is no grand gate, so a broad moat still needs a suspension bridge, which
  stays permanently down.

---

## 5. Side by side

| | A. Bascule | B. Gate leaf | C. Gangplank |
|---|---|---|---|
| denies the moat when raised | **yes** (open hole) | no (gates the bank only) | **yes** (open hole) |
| raise in seconds under attack | yes (powered) / slow (manual) | **yes** (a door) | no (Uninstall work) |
| riders fall when raised | yes, by default (Q2) | never | only if Q2 says so |
| max span | 4 (8 with two leaves) | any suspension length | 1 to 3 |
| path flip cost | grid rebuild per raise, a new path (spawned deck) | **reachability cache only** | grid rebuild, existing path |
| raider behaviour when up | `RM_RaiderTrench` + sap the winch | vanilla door bash | `RM_RaiderTrench` + raiders bring planks |
| new code | most | least | small |
| art bill | largest (winch + upright leaf × lengths × 4 facings) | smallest | small |
| ESTIMATE agent-days | 5 to 7 + art | 2 to 3 + art | 2.5 to 3.5 + art |
| risk | medium | low | low to medium |
| live test | about 1 day | about 0.5 day | 0.5 to 1 day |

They combine: **A + C** (a grand bascule for the main gate and planks for side trenches) shares the base hook and the
raider work. **B** is the fallback if A's spawned-deck flip proves costly.

## 6. Recommendation

**Option A, the Bascule.** It is the only option that is both a real moat denial and a member of the suspension
family (dragged, anchored, styled, rated). C is a good cheap second for narrow trenches, and B gates the bank without
denying the moat.

Before A's build, a 0.5-day offline spike: grep every reader of `Building_SpanDeck`/`Decked` that bypasses `DeckAt`, and
time one pocket-grid rebuild on the largest dug test map. If a rebuild is slow, rate-limit the raise to whole-leaf steps.

## 7. Open questions for the owner (each a question card)

1. **Which drawbridge?** A Bascule (a hinged leaf with a winch, the moat is open when up) · B Gate leaf (a door at the
   bank end, the deck stays) · C Gangplank (a short plank carried in and out) · A and C both.
2. **Someone is on it when it raises.** They fall into the hole (like a destroyed pit cover) · Raising waits until it
   is clear · They are tipped back onto the winch bank.
3. **Which side works it?** Raise from either side, lower only from the winch side (like the wall ladder) · Only from
   the winch side, both ways · Either side, both ways.
4. **What drives it?** A colonist at a winch, slow · Power, fast, with a colonist as fallback · Both, by type (timber
   by hand, steel powered).
5. **Does it lower itself for your people?** No, only on your order (like the ladder) · Yes, for your own faction
   while not held raised (like a door).
6. **Raiders facing a raised drawbridge:** use the trench rules as they stand (jump, ladder, breach) · Also aim
   sappers and breachers at the winch first · Also let raiders bring their own gangplanks (C's mirror).
7. **How long can it be?** One leaf up to 4 squares · Two leaves meeting, up to 8 · As long as the bridge type allows.
8. **Which types get a drawbridge?** Timber and steel · Steel and heavy only · Every type except rope.

## Owner's answers (question cards, 2026-10-20 18:19 PDT)

1. **Design:** *"All of those, with the planks laid beside the bridge (part of its art, not an actual item you can misplace)"*. That means A (bascule with winch), B (gate leaf) and C (gangplank) together, with the planks drawn as part of the bridge's art rather than carried as an item.
2. **Occupant when it raises:** *"tips towards hinged side, pulls enemies inside"*.
3. **Sides:** like the wall ladder. It raises from either side and lowers only from the winch side.
4. **Power:** timber is hand-winched; steel is powered.
5. **Auto-lower:** *"(2) when there are no hostiles on map, (3+1) when hostiles appear"*. With no hostiles on the map, it lowers like a door for friendlies. Once hostiles appear, it locks and moves only when ordered.
6. **Raiders:** *"1+3"*. Raiders use the trench rules and sappers go for the winch. Some raids also bring their own planks.
7. **Length:** set by material.
8. **Types:** timber and steel.
