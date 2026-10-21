# FlowWorks drawbridges (RULED DESIGN, 2026-10-20)

**Design only.** Nothing in code, defs, the bridge or the game was touched. FlowWorks paths are under
`src/RimMandrake/FlowWorks/` at HEAD `99a127889a`; vanilla claims are from the 1.6 decompile through RimSage. Each engine
claim is marked MEASURED (read, with file:line) or UNMEASURED. Every day count is an ESTIMATE.

Owner, verbatim (2026-10-20): *"Please do a design pass in the background to make Drawbridges parallel to suspension
bridges. Come up with three potential implementations to consider with tradeoffs."* He answered the eight option cards
(§Owner's answers) and the eleven GPT-review cards (`flowworks_drawbridge_pipes_gpt_review_2026-10-20.gpt_read.md`
§Owner's answers). The section below folds all of them in, plus every GPT finding the triage marked valid that sits
inside his rulings. Build item: `DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS`.

## Ruled design

### R1. What a drawbridge is

One structure in the suspension-bridge family, **timber or steel only** (answer 8), with three parts that are all
built (answer 1, *"All of those"*):

1. **The leaf (bascule).** A suspension-style deck dragged across a dug pit, trench, canal or moat, hinged at a
   **winch house** on the hinge bank. Raised, its squares stop being ground and the hole is whole again: every pit rule
   (capture, climb, raiders, pit rooms) applies with no special case.
2. **The gate leaf.** A door set in the wall line on the hinge-bank anchor squares, 1 to 3 lanes wide to match the
   deck. It is the per-pawn, seconds-fast passage control at the bank: own people pass it like a door when the bridge's
   control mode allows (R4); it is never a plain vanilla door (R7).
3. **The planks.** *"laid beside the bridge (part of its art, not an actual item you can misplace)"*. There is **no
   minified gangplank, no `MinifiedThing`, nothing hauled or stored.** The planks are part of the bridge's own state and
   drawing. What the planks *do* in play is not yet ruled (see Q1 at the end); until he answers, the build treats them as
   art only.

**Length is set by material** (answer 7): each material has a maximum leaf length (numbers are a tuning proposal for
the build, Mod-Settings sliders, defaults: timber 4, steel 8). A leaf longer than one hinge allows is built as **two
leaves**, one hinged on each bank; **each leaf tips toward its own hinge** (review answer 2), even when that is the far
bank. Every leaf records its own hinge bank, control bank and movement state; none of these is inferred from faction
or from where pawns stand.

### R2. Who works it, and how

- **Sides** (answer 3, the wall-ladder rule): a leaf **raises from either side, lowers only from its winch side**.
- **Drive** (answer 4): **timber is hand-winched** (a colonist at the winch works it, proposal about 4 s per square);
  **steel is powered** (proposal about 2 s per whole leaf).
- **Steel without power freezes where it is** (review answer 4). There is no hand fallback on steel and no automatic
  drop to lowered. A frozen steel leaf part-way up stays part-way; it moves again when power returns.
- A hand-winched raise or lower that is interrupted stays where it is; the leaf's saved state holds the part-way point.

### R3. Someone on the leaf when it raises: tipping, never collapse

Answer 2: *"tips towards hinged side, pulls enemies inside"*. Review answer 1: anyone who does not fit on the hinge bank
**falls into the pit**.

- **Raising is a reversible state change, never `Building_SpanDeck.Collapse`.** `Collapse` (MEASURED,
  `Source/Pits/Building_SpanDeck.cs:76`) marks the span collapsed, vanishes the decks, leaves rubble and runs each
  faller through the descent event; none of that may happen on an ordinary raise. Raise and lower share only the
  square-by-square sequencer with the suspension swing-down, and only the parts with no destruction, descent, salvage
  or crushing side effects.
- **Who rides.** Riders are chosen by **band**, not by `pawn.Position`: a pawn on the deck band rides; a pawn in the
  floor band underneath (the underpass, floor at least 2 m below) is not touched by the raise. Underpass is already
  band-aware (`Source/RM_SpanMath.cs:76-78`, per the triage).
- **Where they go.** Riders are ordered deterministically (nearest the hinge first, ties by cell index). Each is moved
  to the nearest free, standable, reachable-from-the-hinge square on the hinge bank, checked for walls, closed doors,
  buildings and other pawns; nobody is moved through a wall or a closed gate. They keep faction, equipment and the
  ability to fight: being tipped is not capture. The bank landing does no fall or spike damage.
- **Overflow falls.** A rider who has no legal bank square falls into the pit through the ordinary descent event, with
  fall damage by metres and the pit's own rules (spikes only in the deepest pits) applying.
- **Items** on the leaf slide to the hinge square, or fall with overflow if it is full.
- **Buildings** are refused on a drawbridge leaf. Hoses and flexible power cords are not buildings for this rule: they
  may lie on the leaf and **disconnect while it is raised, rejoining when it is lowered** (review answer 6); they never
  re-route across the opened moat. Rigid pipe and rigid conduit cross only on pipe poles
  (`flowworks_pipes_across_pits_design_2026-10-20.md` §Ruled design).

### R4. Control mode: friendly auto-lower, hostile lock

Answer 5: *"(2) when there are no hostiles on map, (3+1) when hostiles appear"*. Review answer 3: only **free**
hostiles lock it; a hostile trapped in a pit or held in a cell does not.

- **Peace mode** (no free hostile on the map): the bridge lowers for own-faction pawns and the gate opens for them,
  like a door, unless the player has set "hold raised".
- **Locked mode** (any free hostile on the map): the bridge moves **only when ordered**, and the gate opens for nobody
  automatically. A hostile's arrival **locks** the bridge; it does **not** raise it. Raising is still the player's order.
- **The switch is atomic.** The hostile check is made both when an automatic lower is accepted and again when it
  commits; locking cancels any pending automatic lower. "Free hostile" excludes a pawn the pit engine holds as trapped
  and a prisoner or captive in a cell; the exact predicate is the pit engine's own trapped test (to be named at build).
- The readout always says **why** the bridge is locked.

### R5. Raiders

Answer 6: *"1+3"* (plus the triage's reading of sappers): raiders use **the trench rules as they stand**, sappers and
breachers aim at **the winch**, and **some raids bring their own planks**.

- Raised, the moat is open hole and `Source/Superdeep/RM_RaiderTrench.cs` (jump pack, scaling ladders, breach by fill)
  takes over when nothing else is reachable. That hand-off is **unproved** (GPT #12): the build must invalidate
  hostile jobs holding a path over the leaf and prove progress in a live row (RAID_UP, below) with a reachable decoy
  outside and the winch inside.
- **Winch attacks need an executable route**; a winch on the inaccessible bank is attacked only by ranged fire,
  sappers and breachers as their AI allows.
- **Raid planks** are a raid deployment, not the colony's art planks: one reserved deployment transaction per plank
  (no duplicate crossings from an interrupted carrier), material span limits, both ends on banks at the same height,
  counted exactly once, then ordinary load, fire and destruction rules.
- Flyers, jumpers and floaters cross pits freely (by card, 2026-10-20); titans step over a trench narrower than their
  stride (`HugeThings/.../TitanClearingUtility.cs`, `FlowWorks/Source/Superdeep/RM_TrenchStride.cs`). No drawbridge
  changes either.

### R6. Failure, structure and machinery are separate

- **Structural support** (the anchors) and **operating machinery** (the winch, its power) are separate things. Losing
  structure runs the existing suspension swing-down/collapse (`Building_SuspensionDeck.cs`, whole-span collapse; that
  path drops riders, it is a collapse). Structural failure wins over any movement in progress.
- **Losing the winch** (destroyed or burnt) does not collapse anything: the leaf **freezes where it is**, the same rule
  as steel losing power. (The pre-ruling text "a destroyed winch drops the leaf" is withdrawn; it contradicted the
  freeze ruling. If he wants a crash-down on winch loss, see Q2.)
- Fire: a timber leaf burns raised or lowered; a burnt deck square collapses the span (today's rule).
- **Hidden geometry (GPT #28).** A raised far-end square must stop being a target, a fire cell, a repair job or a
  blocker. Making `Decked` false changes only the readers that go through `DeckAt`, not `ThingGrid` queries. The
  build audits every spatial reader beyond `DeckAt` and gives the raised leaf one authoritative target/work geometry
  (drawn upright at the winch), with damage routed to the persistent structure.

### R7. The gate is a custom door, not vanilla semantics

The gate subclasses the 1.6 multi-cell door (`Building_MultiTileDoor : Building_SupportedDoor`, MEASURED, Core uses it
at `Defs/Core/ThingDefs_Buildings/Buildings_Structure.xml:164`) or `Building_Door`, chosen at build. It adds sided
permission (operated only from the hinge side), the R4 control mode and a closed look of the upright leaf. The build
audits every passage read (`BlocksPawn`, `PawnCanOpen`, `FreePassage`, `Notify_PawnApproaching`) for each lane and
from both banks; whether a multi-cell door is one portal region is UNMEASURED. Opening and closing a vanilla door only
clears hostile reachability (`Building_Door.cs:592-598`, MEASURED).

### R8. Pathing contract: no stale crossing

A raise or lower must be visible to every path immediately (GPT #5/#6):

- **Pocket grid.** `RM_PocketGrid` rebuilds at most once per `RebuildMinTicks = 60` unless paused (MEASURED,
  `Source/Superdeep/RM_PocketGrid.cs:31, :216`); a deck flip only bumps `ClimbGeneration`. **A drawbridge toggle forces an
  immediate rebuild** (bypassing the 60-tick limit for this cause; no such entry exists today, MEASURED by grep of that
  file), and flipped cells notify `RM_PitRooms.NotifyPitnessChanged` as today.
- **Cliff masks** key on `ClimbGeneration` and derive inside `GatherData` (MEASURED, `Source/Superdeep/RM_CliffMask.cs:125-129`),
  so they follow the bump on the next scheduled path without a delay.
- **Offset grids are immutable snapshots** keyed on the customizer object (MEASURED, `RM_PitPathing.cs:35-37`); a toggle
  publishes a new snapshot, never mutates one in place.
- **1.6 pathfinding is batched Unity jobs** (MEASURED: `PathFinder.PathFinderTick` completes last tick's jobs, then
  `GatherData` and `ScheduleBatchedPathJobs`, `Verse/PathFinder.cs:293-311, :371-412`; the customizer's grid is read on
  the scheduling thread, `PathFinderMapData.cs:290`). So a path requested before a toggle can be delivered after it.
  Pawns holding a path over a changed square are re-pathed, and a result computed on the old generation is revalidated.
- Pocket and room connectivity is recomputed when a raise joins or splits floor pockets; decks still make neither roofs
  nor temperature rooms.

### R9. Save state

Per leaf, versioned and Scribed: hinge bank, control bank, target (raised/lowered), progress, power/frozen state, lock
mode, hold-raised flag, and stable references to its supports and winch. A completed tip is committed once and never
replayed on load. No pathing cache is saved. Old saves load with every leaf lowered. The pre-ruling single
`raisedSquares` int is withdrawn (GPT #11).

### R10. Map and gravship identity

Every record, cache and pending job is scoped to its map (and the map's planet layer: `PlanetTile`/`PlanetLayer` exist
in 1.6, MEASURED, `RimWorld/Planet/PlanetTile.cs:6`, `PlanetLayer.cs:16`). Gravship relocation is **not** destruction:
1.6 calls `Thing.PreSwapMap`/`PostSwapMap` around a gravship move (MEASURED, `Verse/Thing.cs:2212-2217`,
`RimWorld/GravshipUtility.cs:383`, `GravshipPlacementUtility.cs:172`), and a drawbridge on a gravship must re-key on
`PostSwapMap` instead of running anchor-loss. A bridge crossing the gravship boundary has no ruled policy (Q4).

### R11. Readout and settings

Readout: actual and target state, progress, operating bank, lock reason, power, obstruction, and a preview of where
riders would be tipped (or fall). Mod Settings (defaults = shipped behaviour): "Drawbridges can be built"; "Raise speed
×"; per-material max leaf length; "Raids bring planks". All off, a drawbridge is a suspension bridge stuck lowered.

### R12. Art

Leaf lowered: the suspension deck tiles in the four styles. Raised: the squares draw empty, and the winch house draws
the leaf upright, height scaled to its length, 4 facings. Gate: closed (leaf upright) and open, 4 styles. Planks: drawn
stacked beside the bridge. Search `artpipe_state.py find` and the sheets' `.decisions.json` before queuing any art; art
is a separate item, as `SUSPENSION_ART_RESKIN_HE_SEES_FIRST` was.

**Art contract (BENCH, 2026-10-20; the builder reads texture paths from here).** Owner: *"commission the art for the
bridges so it will be ready for you by the time you need it."* Searched first: no drawbridge, winch, bascule, gangplank
or raid-plank art existed (`artpipe_state.py find`, the done jobs, every `Transient/biome_ffar/*.decisions.json`).
All paths are texPaths under `src/RimMandrake/FlowWorks/Textures/`, 256 px per cell like the suspension art. Queued
from `infrastructure/artpipe/art_lists/flowworks_drawbridge_2026-10-20.json` (28 jobs); until each passes review and
`art install`, the path does not exist on disk, so the builder ships a stand-in or guards for a missing texture.
`<M>` is `Timber` or `Steel`.

| picture | texPath | graphic | canvas / size |
|---|---|---|---|
| leaf lowered | `Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_<M>_Atlas` (+ railing edge) | existing, reused | no new art |
| winch house (timber hand-crank; steel motor house) | `Things/Building/FlowWorks/Drawbridge/RM_DrawbridgeWinch_<M>` | Graphic_Multi `_south/_east/_north`; front (chains) faces the leaf | 384×384, 1×1 footprint, drawSize 1.5 |
| leaf raised, deck face toward camera | `Things/Building/FlowWorks/Drawbridge/RM_DrawbridgeLeafUp_<M>_Face` | single, drawn by code at the hinge | 256×1024 = 1 lane × 4 cells, hinge at the bottom edge |
| leaf raised, underside toward camera | `…/Drawbridge/RM_DrawbridgeLeafUp_<M>_Underside` | as above | as above |
| leaf raised, edge-on (span runs east/west; flip for west) | `…/Drawbridge/RM_DrawbridgeLeafUp_<M>_Edge` | as above | as above |
| gate leaf closed / open | `…/Drawbridge/RM_DrawbridgeGate_<M>_Closed`, `…_Open` | Graphic_Multi `_south` (face-on) and `_east` (edge-on); north reuses south | 256×384 per lane, drawSize 1×1.5 |
| planks beside the bridge (art only) | `…/Drawbridge/RM_DrawbridgePlanks_<M>` | single | 256×256, 1 cell |
| raid plank, carried/dropped item | `Things/Item/FlowWorks/RM_RaidPlank` | single | 256×256 |
| raid plank laid across the pit | `…/Drawbridge/RM_RaidPlank_Laid` (one per cell) + `…/Drawbridge/RM_RaidPlank_LaidEnd` (each bank end, hooks at the top) | single, rotated with the span | 256×256 each |
| command icons | `UI/Commands/FlowWorks/RM_DrawbridgeRaise`, `…/RM_DrawbridgeLower`, `…/RM_DrawbridgeHoldRaised` | UI | 256×256 |

Which raised view to draw: the leaf rotates up about its hinge, so a span running **north** from its hinge shows its
`_Face` to the camera, a span running **south** shows its `_Underside`, east/west show `_Edge`. The raised art is drawn
1 lane wide and 4 cells tall; the code draws one copy per lane and scales its height to the leaf length (a steel leaf
over 4 cells is stretched).

**The four looks**, as the suspension bridge ships them (`ThingStyleDef` per part per look, `Machinery/PipeLook.cs`):
`RimMandrake/FlowWorks/Drawbridge/<Look>/` with `<Look>` = `Scrapper`, `Industrial`, `Modern`, `Futuristic`, holding
`RM_DrawbridgeWinch_<M>` (Graphic_Multi, per material because the drive differs), `RM_DrawbridgeLeafUp_Face/_Underside/_Edge`,
`RM_DrawbridgeGate_Closed/_Open` (`_south`, `_east`) and `RM_DrawbridgePlanks`; same sizes as the table. 56 jobs from
`infrastructure/artpipe/art_lists/flowworks_drawbridge_looks_2026-10-20.json`.

**Not commissioned:** a mid-raise picture (the spec does not animate the raise), raid planks in steel, a crash-down
wreck (`RM_SuspensionWreck` exists).

### R13. Build order, cost, live rows

ESTIMATE 8 to 11 agent-days plus art.

1. Offline spike (0.5 d): grep every reader of `Building_SpanDeck`/`Decked`, and every `ThingGrid` spatial read, that
   bypasses `DeckAt`; time one pocket-grid rebuild on the largest dug test map.
2. Base hook: `Decked` becomes `!collapsed && Spawned && !Raised` with a virtual `Raised` (today `Decked` is a plain
   property, MEASURED, `Building_SpanDeck.cs:27`). Forced pocket rebuild on toggle.
3. Leaf, winch, per-leaf record (R9), hand job and powered drive, freeze rules.
4. Tipping (R3) and overflow fall; band-aware rider selection.
5. Gate (R7) and control mode (R4).
6. Raider hand-off, winch targeting, raid planks (R5).
7. Selftests, readout, functional script (`suspension_bridge_proof.py` new scenes).

Live rows (minimal list, about 1 day): RAISE_PATH (a colonist re-routes at once), RAISE_TIPS_RIDERS (six raiders on a
3-wide leaf, one free bank square: one lands, five fall), RAISE_SPARES_UNDERPASS (a pawn beneath is untouched),
LOWER_ONLY_FROM_WINCH, TWO_LEAF_TIPS_OWN_HINGE, HOSTILE_LOCKS (queued auto-lower cancelled when a raid spawns; a trapped
hostile does not lock), STEEL_UNPOWERED_FREEZES, WINCH_LOST_FREEZES, RAID_UP (decoy outside, winch inside; legal
progress, no job loop), RAID_PLANK (interrupted carrier makes no duplicate crossing), SAVE_MIDRAISE.


## Owner's follow-up answers (question cards, 2026-10-20, late evening). These override the Ruled design where they differ.

- **Planks:** art only. This was settled earlier: *"part of its art, not an actual item you can misplace"*.
- **Winch destroyed:** the leaf **crashes down**, and anything under it is hit. This replaces "a lost winch freezes the leaf". A steel bridge that loses power still freezes.
- **Two-leaf bridges:** each leaf has its own winch house on its own bank.
- **Bridge across the gravship edge:** the bridge **collapses** on launch, and anyone on it falls.

## Owner questions as asked (ANSWERED, see the next section)

1. **What do the drawbridge planks do?** Art only (drawn beside the bridge, no use) · a 1-wide footway a colonist lays
   or pulls at the bank, drawn stacked when pulled, never an item · write-in.
2. **The winch is destroyed.** The leaf freezes where it is (same as steel without power) · the leaf crashes down to
   lowered · write-in.
3. **Which banks may a two-leaf bridge be worked from?** Each leaf only from its own winch · both leaves from the
   colony winch · write-in.
4. **A drawbridge crosses the gravship's edge at launch.** Launch is blocked until it is raised or removed · the part
   off the ship is left behind and the bridge collapses · write-in.

## Owner's answers (question cards, 2026-10-20 18:19 PDT)

1. **Design:** *"All of those, with the planks laid beside the bridge (part of its art, not an actual item you can misplace)"*. That means A (bascule with winch), B (gate leaf) and C (gangplank) together, with the planks drawn as part of the bridge's art rather than carried as an item.
2. **Occupant when it raises:** *"tips towards hinged side, pulls enemies inside"*.
3. **Sides:** like the wall ladder. It raises from either side and lowers only from the winch side.
4. **Power:** timber is hand-winched; steel is powered.
5. **Auto-lower:** *"(2) when there are no hostiles on map, (3+1) when hostiles appear"*. With no hostiles on the map, it lowers like a door for friendlies. Once hostiles appear, it locks and moves only when ordered.
6. **Raiders:** *"1+3"*. Raiders use the trench rules and sappers go for the winch. Some raids also bring their own planks.
7. **Length:** set by material.
8. **Types:** timber and steel.

## Appendix: options considered (pre-ruling, one line each)

- **A, Bascule** (hinged leaf with a winch): chosen as the leaf; the only option that truly denies the moat.
- **B, Gate leaf** (a door at the bank, deck fixed): chosen as the bank gate; kept as a custom door, not vanilla.
- **C, Gangplank** (a minified plank carried in and out): rejected as an item, he ruled the planks are bridge art
  that cannot be misplaced; its raider mirror survives as raid planks.
- Rider rules offered (fall like a cover / wait until clear / tip to the winch bank): tip, with overflow falling.
- Drive offered (winch / power / both by type): both by type, steel without power freezes.
- Engine facts used to price the options, still true: no drawbridge existed before this pass (grep of `src/`,
  `design/`, items); Odyssey has no movable bridge (vanilla bridges are foundation terrain).
