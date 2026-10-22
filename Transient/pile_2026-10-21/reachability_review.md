# Reachability: review of GPT's solutions, and the question for the owner (2026-10-21, BENCH helper)

Inputs: `Transient/pile_2026-10-21/reachability_dossier.md` (the problem, failures, history, 22 complications),
`Transient/pile_2026-10-21/reachability_gpt_solutions.md` (GPT's full answer, gpt_consult default model, high effort),
`Transient/pile_2026-10-21/relativeveto_options.md` (the earlier memo, options a-e). Checked against source at
`649aef87e1` and vanilla 1.6 via RimSage. No code edited, no game.

Process note: the first GPT run (150 KB prompt: dossier + four whole .cs files) hit the 580 s timeout and returned
nothing; the second (49 KB: dossier, memo, `RM_PocketGridMath.cs`, a 12 KB excerpt of the veto and mask code, a word
budget) answered.

## 1. What GPT proposed (summary)

GPT gave five designs. All five are **exact joint-graph** designs: one graph that sees walls, cliffs, water and per-pawn
door and ladder permissions together. They differ in how that graph is kept up to date:

1. **Dense profiles**: a full cell labelling per (view, band, permission profile). This is the reference implementation.
2. **Chambers + gates (GPT's pick)**: wall- and cliff-aware "chambers", with doors and ladders as explicit gate edges.
   Per-profile labels are kept over the small chamber graph.
3. **Tiles + portals**: 16×16 tiles with local chambers and a global portal graph, for local rebuilds.
4. **Refined vanilla regions**: vanilla regions split privately wherever cliffs cut them.
5. **Dynamic spanning forest**: incremental connectivity with replacement edges.

It also says the memo's option (d) leaves a two-route false yes, recommends replacing vanilla's CanReach answer with a
prefix, and recommends an API and profiling spike first.

GPT **dismissed** the cheap options: (a) per-caller A* gates, (d) a second wall-aware labelling with doors treated as
open, and (e) a bounded A* confirm. They stay in the comparison below, because they are what can ship this week.

## 2. Claim-by-claim validation

| # | GPT claim | verdict | evidence |
|---|---|---|---|
| V1 | `ConnectivitySource` alone admits destroyable walls | **VERIFIED** | vanilla `ConnectivitySource.ComputeCellConnectivity`: an impassable **destroyable** edifice keeps the bit; walls are closed in A* by the cost grid (`PathGridJob.CellIsPassable`: `pathGridDirect >= 10000 && !DestroyableBuilding`). A wall-aware labelling must build its own `passable[]`; it cannot reuse the connectivity byte. |
| V2 | Per-request offsets ≥ 10000 mean impassable | **VERIFIED** | `PathGridJob.CellIsPassable`: `custom[index] >= 10000` → false. |
| V3 | Memo (d) "still permits the same two-route false yes" | **VERIFIED, but narrower than stated** | It needs a door that is closed **to this pawn** on one route and a cliff on the other. (d) treats doors as open, and vanilla's regions are cliff-blind, so each half finds its own route. **It hits our own drawbridge gate**: `Building_DrawbridgeGate.PawnCanOpen` (`RM_DrawbridgeControl.cs:340`) opens for nobody while the map is LOCKED and the gate is not held. So with the gate locked plus a second wall gap behind the moat, a colonist outside gets a false yes. It also hits animals (vanilla `PawnCanOpen`: `!p.CanOpenDoors` → false) wherever a door route and a cliff route both exist. |
| V4 | The walking graph may be directed, so it needs SCCs; "pathological 23.4 GB" | **WRONG for this mod** | `RM_PitTrapMath.StepAllowed` uses `abs(fromD − toD) <= K`, so steps are symmetric. Ladders are "down or up" (`RM_LadderRules.LadderLetsOut`, `RM_LadderUtility.cs:567`). Vanilla doors are symmetric. The flow-door "not from inside a pit" rule depends on the pawn's held state, not on its direction of travel. Plain component labels are enough. Drop the SCC machinery and the GB figure. |
| V5 | "Some usable ladder in this pocket is insufficient; edges must be per ladder" | **WRONG about today's code; right as a requirement** | Today's veto already joins components per ladder edge (`RM_PocketGrid.LadderEdges` / `JoinedByLadders`, ladder square ↔ the square across its wall). `UsableLadderIn` only answers "is a pocket destination enterable". Any wall-aware labelling must re-key those edges onto its own labels (memo (d) says so too). |
| V6 | Replace vanilla's CanReach with a prefix that returns the indexed answer, and fix vanilla's flying false negatives | **REJECTED (risky, out of scope)** | Vanilla CanReach also applies `maxDanger` per region, avoid-grid doors, the `ClosestTouch` and `Touch` corner rules, the region-pair cache and the PassAllDestroyable cell flood (`Reachability.CanReach`, `Region.Allows`). A full replacement must re-implement all of these, and every other mod's CanReach patch would see a different method. Vanilla CanReach does ignore the Flying path context (VERIFIED, `Pathing.For(TraverseParms)`). That is vanilla behaviour with no failure seen, and our flyers are exempt from the veto (`FreePitTraveller`). **Keep the postfix-veto shape: it can only turn a yes into a no.** |
| V7 | Memory: 48 atlases × 62,500 cells = 3M labels = 12 MB of ints | **VERIFIED arithmetic, pessimistic in use** | Views are built lazily (`RM_PocketGrid.For`: a stride or floor view exists only once a titan or an underpass deck asks for it). A normal colony has one view × 6 bands = 1.5 MB, and a wall-aware twin adds 1.5 MB more. |
| V8 | A full 48-atlas rebuild takes 48–480 ms | **UNMEASURED; the typical case is ~8× smaller** | One view × 6 bands is about 1.5M neighbour tests. Arithmetic gives roughly 5–30 ms per rebuild in managed C#. That is a guess until the first build adds a `Stopwatch` to `RM_PocketGrid.Build` (the memo asked for this already). Today's depth-only grid already pays this on every dig or fill, throttled to once per 60 ticks. |
| V9 | `RegionAndRoomUpdater.TryRebuildDirtyRegionsAndRooms` exists (marked UNSURE) | **VERIFIED exists** | `Verse/RegionAndRoomUpdater.cs:77`. Its safe completion point is not studied; only solution 4 needs it. |
| V10 | Touch is not just "any cell of the expanded rect" | **VERIFIED; harmless direction** | Vanilla uses `TouchPathEndModeUtility.IsAdjacentCornerAndNotAllowed`. Our `DestInComponent` counts corners too, so it vetoes less often: it can add a false yes but never a false no. The fix is cheap: reuse the corner rule. |
| V11 | Jump-pack possession is not the free-traveller exemption | **VERIFIED** | `FreePitTraveller` (`RM_PocketGrid.cs:396`) reads `CanFly` and the race's `RM_PitTravelExtension`, never the apparel. Jumps are `PawnFlyer`s targeted by range and line of sight, with `reachable: false` (`JumpUtility.OrderJump`). They are outside reachability in every design. |
| V12 | Sappers: never blanket-skip the cliff and water checks | **VERIFIED; consistent with the memo** | The memo skips only the WALL-aware half for `PassAllDestroyable*`, because walls are passable to them. The depth veto still runs. |
| V13 | Publish at the path-data epoch (`GatherData`), not inside queries | **VERIFIED as a requirement** | The masks already move only in `GatherData` postfixes (`RM_CliffMask.cs` header). The pocket grid never rebuilds inside a query (`RM_PocketGrid` header), and pit rooms read it mid-flood. |
| V14 | Agent-day estimates: 4–7 / 7–12 / 12–20 / 15–25 / 20–35 | **Plausible for exact designs**; the cheap ones were not costed by GPT | My estimates are in the table (§3). |
| V15 | A bounded A* per query must stay a gated diagnostic | **VERIFIED** | A failing A* floods the reachable area, and CanReach sits in every work scanner. That is memo option (e). |

Extra finding (not GPT's, from the dossier read): **deep water for non-swimmers is the same lie.** Swim water is
walkable in regions, and A* bars non-swimmers only through an offset grid. `RM_Patch_Reachability_NonSwimmer`
(`Swimming/RM_Swim.cs:1011`) checks only the destination. This is INFERRED and has not been seen live. Any option with
a "pawn class" input can carry it.

## 3. Comparison

Options: **A** = (a), the per-caller A* gates (today). **B** = (d), the memo's second wall-aware labelling with doors
open. **C** = B plus a few coarse pawn classes (my synthesis, explained in §4). **G1–G5** = GPT's five.

| | per-query CPU | rebuild CPU | latency after a change | realism (lies left) | code | design | tuning | risk | size |
|---|---|---|---|---|---|---|---|---|---|
| **A** gates | 0 (one A* per gated job offer) | none | exact at the gate | vanilla callers keep the loop; every new giver must remember it | trivial | trivial | none | low | done (winch); ~0.2 d per caller |
| **B** wall-aware labels, doors open | +1 int read (≤ 9 for Touch) | as today's grid, also on wall changes; ~5–30 ms per rebuild, ≤ 1/s (UNMEASURED) | ≤ 60 ticks (memo: force a rebuild on a breach) | false yes left where a door closed to the pawn plus a cliff cut the route (locked drawbridge gate, animals vs doors, faction doors) | small (~200 lines) | +1 concept ("reach labels ≠ pocket labels") | none new | low-med | 1–2 d with proof |
| **C** B + pawn classes | as B | ×(classes actually used), built lazily: ≤ 4 classes ≈ ≤ 4× B worst case | as B; a gate lock or hold bumps it at once | false yes left only for faction- or pawn-specific doors (e.g. a raider at one particular colony door it cannot bash) | ~300–400 lines | +1 concept ("class") | the class list | med | 2–3 d with proof |
| **G1** dense per-profile | as B | O(profiles × N); profiles unbounded (GPT: 20 profiles → 240 MB at 48 views) | next epoch | exact | moderate | simple idea, hard extraction | profile retention | med (memory) | 4–7 d |
| **G2** chambers + gates | as B | geometry as B; a permission change is cheap (small graph) | next epoch | exact incl. per-pawn doors and ladders | larger | 3 concepts | low | med (gate completeness) | 7–12 d (mine: 5–8) |
| **G3** tiles + portals | 2 lookups | local (≈ 256 cells) + global relabel | next epoch, bounded | exact if tile seams are right | large | 4+ concepts | tile size | med-high | 12–20 d |
| **G4** refined regions | as B | per native region | waits on vanilla's region rebuild | exact if complete | hard | lifecycle-heavy | few | high (region code, other mods, pit rooms) | 15–25 d |
| **G5** dynamic forest | O(1) | variable; worst O(N) per cut | fast common case | exact if never corrupted | hardest | hardest | thresholds | highest | 20–35 d |

Per complication (✓ = handled as the shipped behaviour intends, ~ = handled with a stated residual, – = not
affected / out of reachability, ✗ = still lies):

| | A | B | C | G1 | G2 | G3–G5 |
|---|---|---|---|---|---|---|
| C1 drawbridge toggle (already forces a rebuild) | ✓ at gate only | ✓ (add to the forced rebuild) | ✓ | ✓ | ✓ | ✓ |
| C2 drawbridge gate locked/held | ✓ at gate only | ✗ residual false yes | ✓ (pawn-independent state fed in) | ✓ | ✓ | ✓ |
| C3 dig/fill mid-transit | ✓ step floor | ~ ≤ 60 ticks stale, step floor backstop | ~ same | ~ next epoch | ~ | ~ |
| C4 faction/pawn-locked doors | ✓ at gate only | ✗ residual | ~ residual only for faction-specific doors | ✓ | ✓ | ✓ |
| C5 animal fences | ✓ at gate only | ✗ residual | ✓ (fence class) | ✓ | ✓ | ✓ |
| C6 flyers | – exempt | – exempt | – exempt | – (GPT would model flying; not needed) | – | – |
| C7 jump packs / C8 teleport | – | – | – | – | – | – |
| C9 ladders raised/lowered | ✓ | ✓ (edges re-keyed, existing StateVersion) | ✓ | ✓ | ✓ | ✓ |
| C10 portable / raider ladders | ✓ | ✓ (as C9; own-faction rule kept) | ✓ | ✓ | ✓ | ✓ |
| C11 climbing gear (band 0) | – skips veto | – skips (walls still vanilla's) | – | ✓ | ✓ | ✓ |
| C12 sappers/breachers | ✓ | ✓ wall half skipped, depth kept | ✓ | ✓ | ✓ | ✓ |
| C13 titan strides | ✓ | ✓ (twin per view, lazy) | ✓ | ✓ | ✓ | ✓ |
| C14 decks/covers/planks | ✓ | ✓ (same depth input) | ✓ | ✓ | ✓ | ✓ |
| C15 deep water, non-swimmers | ✗ | ✗ | ✓ (swimmer class) | ✓ | ✓ | ✓ |
| C16 ramps | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| C17 wall built/breached | ✓ | ~ ≤ 60 ticks; force on removal | ~ same | ~ next epoch | ~ | ~ |
| C18 gravships | ✓ | ~ terrain + depth bumps (under-ship depth UNMEASURED) | ~ | ~ | ~ | ~ |
| C19 map edge | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| C20 pawnless (StartPath walker) | ✓ | ✓ (walker rule kept) | ✓ (walker's class) | ✓ | ✓ | ✓ |
| C21 too-wide pawns | ✓ | ✓ unchanged | ✓ | ✓ | ✓ | ✓ |
| C22 1.6 path batching | ✓ | ~ labels can lead A* by a tick | ~ | ✓ epoch-tagged | ✓ | ✓ |
| vanilla job loops (the class of bug) | ✗ | ✓ mostly | ✓ | ✓ | ✓ | ✓ |

## 4. Recommendation

**C**: a second, wall-aware reach map per climb band, used only by the reach check, keyed by a few coarse pawn classes
(opens doors or not; fence-blocked or not; swims or not), with the drawbridge gate's locked/held state as an input. The
winch A* gate stays. **Why:** it closes the bug for every vanilla job and the map-edge check, including our own locked
drawbridge gate (the case GPT showed B misses), at B's per-query cost and in about 2–3 agent-days. GPT's exact designs
cost 3–10× more and buy only faction-specific doors, which the 2026-10-12 design already accepted as a logged residual.

How C works:
- Pockets, holding, trapping, pit rooms and capture stay on the depth-only labels (ruling 1).
- `passable[]` comes from the path grid: walkable, a door counted open unless it is closed to everyone (a locked,
  un-held drawbridge gate). With a class flag, a door is closed to non-openers, a fence to fence-blocked pawns, and deep
  swim water to non-swimmers.
- Each class's labels are built only when a pawn of that class first asks.
- Invalidation: a walkability generation bumped from the existing `ConnectivitySource.UpdateIncrementally` postfix, and
  from gate lock/hold changes. Rebuilds are throttled to once per 60 ticks; a breach or a drawbridge toggle forces one.
- `PassAllDestroyable*` modes skip the wall half.
- Mod Setting: "Reachability sees walls and cliffs together" (on).

The upgrade path to G2 stays open: the chambers are C's labels, and only the gate edges are new.

**De-risk first (build step 1):**
1. Time `RM_PocketGrid.Build` per band on a 250² map with holes, through `ProofPocket`.
2. Count rebuilds per 1000 ticks during a minute of heavy construction.
3. Make the bar a proof row: CanReach == A*-found on every staged pair (after ≥ 10 ticks). Stage the winch site, a
   locked gate with a second gap behind the moat, an animal at a door + trench, and a non-swimmer at a water moat.

If one rebuild costs more than ~10 ms, rebuild only the bands and classes of pawns now on the map.

## 5. Draft question card (for the seat to ask)

**Question.** Pawns are sometimes told they can reach a place that they cannot actually walk to, so they take a job,
fail to find a path, drop the job and take it again, over and over. It happens where a wall and a dug trench together
block the way. Each one alone leaves a way round, but together they don't.

Why: the game's own "can I get there?" check sees walls but not our dug depth. Our extra check sees depth but not
walls. We only ask "did both say yes?", and each can say yes about a *different* route. The actual walking route-finder
sees both and is always right, but it is too slow to ask every time.

We fixed this at the drawbridge winch (the winch job now checks for a real walking route). Everywhere else (hauling,
building, raiders, animals, the "can I leave the map?" check) still has the bug. Which fix?

Terms:
- **Reach map**: a precomputed map of which squares connect to which. It is cheap to look up, but has to be redone
  when walls or digging change, at most once a second.
- **Pawn class**: a group of pawns that move the same way: can open doors or not (animals can't), avoid fences or not,
  can swim or not.

**Options.**
1. **Keep spot-fixing (what we have).** Each job we write checks for a real route before it is offered.
   - For: no new system, nothing to slow the game, no risk to anything that works.
   - Against: vanilla jobs (hauling, building, raids, animals) keep looping wherever a wall and a trench meet, which
     is exactly the moat-and-wall gate this mod is built for. Every new job must remember the check.
2. **One wall-aware reach map, doors counted as open.** Add a second reach map that sees walls and depth together.
   Trapping and pit rooms do not change.
   - For: fixes almost every case for every job, the cheapest lookup, about 1–2 days.
   - Against: still wrong where a door is shut to that pawn and a trench blocks the other way round. That includes our
     own drawbridge gate when it is locked during a raid, and animals at doors.
3. **The wall-aware reach map, kept per pawn class (recommended).** As option 2, but kept separately for door-openers
   vs animals, fence-avoiders and non-swimmers, and it knows when the drawbridge gate is locked.
   - For: fixes every case we know of, including the locked drawbridge gate, animals at doors and non-swimmers at a
     water moat. Same cheap lookup. About 2–3 days.
   - Against: a bit more memory and rebuild time when several kinds of pawn are on a dug map (rebuild time to be
     measured first). Still wrong for a door that only one particular faction cannot open, which is rare.
4. **The exact route graph (GPT's pick).** Rooms joined by doors and ladders, with every pawn's own permissions
   checked.
   - For: exactly right, every door and ladder, every pawn.
   - Against: about 1–2 weeks. More code to keep correct, and more ways for a missed update to cause a new, quieter
     bug. It mainly adds faction-specific doors over option 3.
5. **Rebuild the game's own region system to see depth (or the other heavy GPT designs).**
   - For: the most "native" answer.
   - Against: 2–5 weeks. It touches the game's core room and region code that other mods also patch, and our pit-room
     code relies on that code. Highest risk of breaking saves or other mods.

**Recommended: 3.** It fixes the whole class of bug, including our own drawbridge gate and animals, for little cost
per lookup and a few days of work. The exact graph (4) stays possible later on the same foundation.
