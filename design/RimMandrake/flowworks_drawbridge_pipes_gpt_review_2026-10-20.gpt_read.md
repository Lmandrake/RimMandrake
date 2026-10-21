# GPT skeptical review: drawbridge + pipes-across-pits (2026-10-20)

## Owner's answers to the review questions (question cards, 2026-10-20 evening)

1. **Tipping overflow:** anyone who doesn't fit on the hinge bank falls into the pit.
2. **Two-leaf bridge:** each leaf tips toward its own hinge.
3. **Trapped hostiles:** only free hostiles lock drawbridges. A hostile trapped in a pit or cell does not.
4. **Steel bridge, power lost:** it freezes where it is.
5. **GSS-restyled vanilla power conduit:** this is rigid conduit, so it crosses only by poles. A separate flexible power cord is what lies on decks.
6. **Lines on a raising leaf:** hoses and cords disconnect when the leaf raises and rejoin when it lowers.
7. **Ladder raised with a hose hanging:** the hose stays, hanging down the wall.
8. **Pipe pole on a deck:** not allowed. Poles stand on solid ground only.
9. **Old saves with lines across pits:** *"Can't happen. We don't have any."* No migration rule is needed.
10. **Siphon:** *"Yes, always"*. Passive levelling flow may cross a crest.
11. **Different liquids joined:** *"Whatever we ruled about mixing in a canal happens."*

Owner, 2026-10-20: *"Send the new pipe and hose drawbridge and pit crossing logic to GPT for review and skeptical improvement."*

Sent: `flowworks_drawbridge_design_2026-10-20.md`, `flowworks_pipes_across_pits_design_2026-10-20.md` (their Owner's answers ruled and fixed), plus `flowworks_bridges_design_2026-10-17.md`, `PIT_SUPERDEEP_COLLAPSE_1.md`, `gss_flowworks_rulings_2026-10-11.md`. Model gpt-6.1-sol, high effort. GPT read text only, not source: its engine points are required checks, not observations. Evidence, not authority.

## Triage (BENCH, 2026-10-20) — numbers are GPT's finding numbers below

Verdict key: VALID (checked against the docs/code I read), PARTLY, WEAK. Action: AMEND (design doc, within rulings), ASK (owner card), IGNORE.

**Both docs are stale against their own Owner's answers (#1).** VALID, and the biggest process finding. Both docs still price and plan the pre-ruling options (drawbridge §2-§6 sells A/B/C separately with a minified Gangplank; pipes §3B/§4 recommends deck-carried pipes). AMEND: one "ruled design" section per doc replaces the option bodies; options become history. Do this before any item is filed.

**Drawbridge**
- #2 raise must not call `Collapse` (destructive: rubble, descent damage, underpass crushing). VALID: D §2 literally says "each square drops its pawns through Collapse/the descent event", and the owner's tip rule is a different movement. AMEND: raise/lower is a reversible state change that shares only the sequencer.
- #3 tipping has no legal destination or overflow rule. VALID, real gap. AMEND (deterministic order, obstruction checks, no spike damage on the bank). ASK: *"If the hinge bank cannot take every pawn tipped onto it, does raising wait, or do the overflow fall into the pit?"*
- #4 two-leaf bridge has a hinge on each bank, so "pulls enemies inside" fails for half the occupants. VALID. Length-by-material (answer 7) may allow two leaves. ASK: *"On a two-leaf drawbridge, does each leaf tip toward its own hinge even when that is the enemy's bank, or is the bridge always one leaf hinged on the colony bank?"*
- #5/#6 a generation bump plus 60-tick pocket rebuild leaves a stale-crossing window; async 1.6 pathing may finish after a toggle. PARTLY. RM_PitPathing builds the cost grid per request via `IPathGridCustomizer` (`RM_PitPathing.cs:45,248`), so no shared vanilla mask goes stale, but the pocket-grid rebuild delay and pawns already holding a path are real. AMEND: raise must force an immediate rebuild (or bypass the 60-tick limit for this cause), re-path pawns on the leaf, and the offline spike already owed in D §6 gets a test: toggle while requests are outstanding.
- #7 pawns on the leaf vs pawns beneath it share an x/z cell. VALID. AMEND: riders chosen by band (floor depth vs deck), not by position. Underpass is already band-aware (`RM_SpanMath.cs:76-78`).
- #8 gate "is vanilla door semantics" is no longer true (inside-only lowering, hostile lock, 1-3 lanes). VALID. AMEND: restate B as a custom door subclass; audit `BlocksPawn/PawnCanOpen/FreePassage` and `Notify_PawnApproaching` reads.
- #9 hostile arrival must be an atomic lock; a hostile trapped in a pit still counts as "hostiles on the map". VALID, good catch. AMEND: lock on any hostile spawned; pending auto-lower cancels. ASK, one line: *"Do hostiles locked in a sealed pit or captive-mech cell keep a drawbridge locked?"*
- #10 power loss / winch destroyed / anchor lost conflict. VALID. AMEND: separate structural support from the winch; structural loss (swing-down) wins. ASK: *"When a steel drawbridge loses power while raised or lowered, does it freeze where it is, or fall to lowered?"* Owner answer 4 says only "steel is powered"; no hand fallback was ruled.
- #11 `raisedSquares` int is not a save format. VALID. AMEND: record per leaf with hinge, target, progress, lock mode; no pathing caches saved.
- #12 "trench giver takes over" is unproved; winch may sit on the inaccessible bank. VALID. D itself says `RM_RaiderTrench` runs "when nothing else is reachable" and does not test the handoff. AMEND: add live row RAID_UP with decoy and inside winch.
- #13 raider planks need single-transaction deployment, span limits, exactly-once accounting. VALID, small. AMEND.
- #28 spawned-but-hidden deck Things keep fire/targeting/repair at the old far cells. VALID, and the sharpest engine risk of Option A: `Decked` is read in seven places but ThingGrid queries are not. AMEND: grep audit beyond `DeckAt` (already half owed in D §6).
- #27 "decks sit above the fill" contradicts awash sunken decks. PARTLY. B §2/§7 does allow water over a deck; I did not re-read it fully. AMEND: drop the unconditional claim; ASK only if the cord-short rule is wanted (see #14 card).
- #29/#30 map/layer identity in all caches; gravship relocation is not destruction. VALID, standing rule (every DLC assumed). AMEND as test rows; ASK deferred, low priority: *"May a bridge or pipe-pole line crossing the gravship boundary block launch?"*
- #31 under-layer terrain recipe may not cover 1.6 foundation/temporary layers. PARTLY: it concerns the bridges/water doc, not these two. Fold into the existing water-engine item; no action here.

**Pipes**
- #14 "cord yes, conduit no" has no mechanical discriminator because GSS restyles vanilla `PowerConduit` (pipes doc §1.1 says so). VALID, blocker. AMEND: explicit def-level tag (`DeckCord` vs `RigidConduit`) independent of style. ASK: *"Does the existing power conduit (restyled by GSS) count as a cord that may lie on bridges, or only as rigid conduit needing poles?"* The owner said "conduit does not cross"; GSS cords are a separate cord def, so the likely reading is cord = cord def, conduit = vanilla conduit.
- #15 old placement plan permits rigid pipe on timber/steel and excludes rope; the ruling reverses both. VALID, tied to #1. AMEND with one crossing-policy table.
- #16 hose/cord geometry through a moving leaf is undefined. VALID. ASK: *"When a drawbridge raises, do hoses and cords on it stay connected (slack) or disconnect until lowered?"*
- #17 hoses down ramps and ladders need band-aware transitions; a raised ladder with a hanging hose is undefined. VALID. AMEND; ASK: *"When a ladder is raised, does the hose on it hang loose, retract, or disconnect?"*
- #18 pipe poles must not be walking ground or support deck. VALID. AMEND; poles reuse GSS anchors (Light only), so placement over open pit squares must be refused. Needs a rule for poles standing on decks: ASK: *"May a pipe pole stand on a suspension deck?"*
- #19 long-range liquid edge vs `MaxConductors` and port caps. VALID (pipes doc names the kernel edge its riskiest change). AMEND: cap applied after the edge joins components; a test for ring-of-two-routes.
- #20 teardown needs exactly-once and support ownership. VALID. AMEND: each segment records its supports.
- #21 "move the line first" refusal now contradicts "digging breaks it". VALID, stale text. AMEND: break at dig commit, not at designation; frame completion revalidates. ASK: *"On loading an old save, do unsupported floor pipes and conduits break at once or only when something changes?"*
- #32 legibility: part-raised, locked, unpowered, obstructed states need readout. VALID. AMEND: readout lists state, progress, lock reason, power, tip destination preview; line art must distinguish deck cord, pole crossing, ladder descent.

**Gravity levelling (owner answer 7)**
- #22 passive levelling vs GSS ruling 3 ("filling storage needs a pump"). PARTLY. GSS 3/9 concern tanks (storage), and the owner's new rule is world-body to world-body, which GSS never covered; so a narrow exception is the right reading, but the doc must say tank-fill stays pump-only. AMEND, no card.
- #23 levelling must compare surface elevation, conserve volume. VALID; the level-surface model is already built (`flowworks_level_surface_*`), so use it. AMEND with a conservation test (1-cell vs 100-cell basin, parallel links, same-body loop).
- #24 intake exposure, switched-off hose, siphon over a crest. VALID. AMEND (stop extraction at an exposed intake; a switched-off hose drains only its own contents per GSS 2/13). ASK: *"Does a passive hose between two waters work over a hill (siphon) or only when its highest point is below the source surface?"*
- #25 connecting water to poison/oil needs a fluid-identity rule. VALID, collides with the unresolved body-merging in PIT_SUPERDEEP `[F]` (line 299). ASK: *"Does a hose between two bodies of different liquid refuse to level, or mix?"*
- #26 no bounded update algorithm; per-link scanning of body cells; variable tick intervals. VALID, the performance blocker. AMEND: map-owned budgeted solver, cached body volume/level, delta-tick integration, test on a 325x325 map with 200 links.

**Ignore / noted:** none ignored outright. #31 is deferred to the water-engine item. GPT's claims about a Ludeon modder primer (async batched pathing, `PlanetTile`, `PreSwapMap`) are unverified by me; check against the decompile before relying on them.

## GPT's engine claims, checked against the 1.6 decompile (RimSage) and HEAD `99a127889a`

| GPT claim | verdict | evidence |
|---|---|---|
| 1.6 pathfinding is batched and multithreaded (#5, #6) | **MEASURED, true** | `Verse/PathFinder.cs:293-311` (`PathFinderTick`: complete last tick's jobs, `GatherData`, schedule), `:371-412` (Unity `job.Schedule`); customizer grid read at schedule time, `PathFinderMapData.cs:290` |
| a path requested before a toggle can finish after it (#6) | **MEASURED, true** | same: jobs scheduled in one tick complete at the next `PathFinderTick` |
| FlowWorks offset grids are per request (triage #5/#6) | **MEASURED, corrected** | immutable snapshots per map, keyed on the customizer object, rebuilt when the open-pit set changes (`RM_PitPathing.cs:35-37`); cliff masks key on `ClimbGeneration` inside `GatherData` (`RM_CliffMask.cs:125-129`) |
| pocket rebuild is rate-limited (#5) | **MEASURED, true** | `RM_PocketGrid.cs:31` (`RebuildMinTicks = 60`), `:216` (skipped unless paused); no force-rebuild entry in that file |
| 1.6 has foundation and temporary terrain layers (#31) | **MEASURED, true** | `Verse/TerrainGrid.cs:11,15` (`tempGrid`, `foundationGrid`), `:61-67` (temp wins, then foundation when no under layer) |
| `PlanetTile` for layers (#29) | **MEASURED, exists** | `RimWorld/Planet/PlanetTile.cs:6`, `PlanetLayer.cs:16`; "Ludeon recommends" it is UNMEASURED (primer not read) |
| `PreSwapMap`/`PostSwapMap` for gravship moves (#29, #30) | **MEASURED, true** | `Verse/Thing.cs:2212-2217`, `ThingComp.cs:326-330`, called from `GravshipUtility.cs:383` and `GravshipPlacementUtility.cs:172` |
| variable tick intervals (#26) | **MEASURED, true** | `Verse/ThingWithComps.cs:334` `TickInterval(int delta)` |
| door open/close only clears hostile reachability (D §1) | **MEASURED, true** | `RimWorld/Building_Door.cs:592-598` |
| the one-cell door-region argument does not cover a 1-3 wide gate (#8) | **PARTLY** | 1.6 has `Building_MultiTileDoor : Building_SupportedDoor` (`RimWorld/Building_MultiTileDoor.cs:6`, Core def at `Buildings_Structure.xml:164`); its region shape is UNMEASURED |
| GSS restyles `PowerConduit` rather than replacing it (#14) | **MEASURED, true** | `GimmeSomeSlack/Patches/RM_ConduitStyleable.xml:10-12`; no cord/cable/wire ThingDef in GSS or FlowWorks Defs |
| `Decked` is not virtual (D §2) | **MEASURED, true** | `Pits/Building_SpanDeck.cs:27` |
| hidden spawned decks keep ThingGrid interactions (#28) | UNMEASURED | an audit is step 1 of the drawbridge build |
| 1.6 shares batched map data across requests, needing vanilla path invalidation (#5) | UNMEASURED beyond the above | `mapData.GatherData` is per tick; no FlowWorks-specific stale case was read |

Both design docs now open with a `## Ruled design` section built on these marks (2026-10-20).

## Owner-ruling questions this produces (each can become a card)

All eleven are answered (§Owner's answers above); kept as the record of what was asked.
1. Hinge bank full: raising waits, or overflow falls?
2. Two-leaf bridge: each leaf tips to its own hinge, or only one colony-hinged leaf?
3. Hostile sealed in a pit or captive: keep a drawbridge locked?
4. Steel drawbridge loses power: freeze or fall to lowered?
5. Existing GSS-styled power conduit: deck cord or rigid conduit?
6. Hose/cord on a raised leaf: stay connected or disconnect?
7. Raised ladder with a hose on it: hang, retract, or disconnect?
8. Pipe pole standing on a suspension deck: allowed?
9. Old save, unsupported floor line: break at load or later?
10. Passive hose over a crest (siphon): allowed?
11. Different liquids joined: refuse or mix?

---

# GPT's raw answer (verbatim)

Run: `gpt_consult.py`, 128155 chars in, 5 files, model gpt-6.1-sol.

---

The owner’s answers leave several implementation sections obsolete. The largest risks are destructive code being reused for raising, undefined tipping destinations, stale pathing after a toggle, and gravity transfer bypassing the existing pump/storage rules.

References below:

- **D** — `flowworks_drawbridge_design_2026-10-20.md`
- **P** — `flowworks_pipes_across_pits_design_2026-10-20.md`
- **B** — `flowworks_bridges_design_2026-10-17.md`
- **Pit** — `PIT_SUPERDEEP_COLLAPSE_1.md`
- **GSS** — `gss_flowworks_rulings_2026-10-11.md`

This reviews the supplied text; it does not verify its source-code excerpts. Engine risks below are required checks, not claimed observations of running code. “Blocker” means the design needs resolution before implementation can safely follow it.

1. **A — blocker: The selected designs no longer match their proposed architectures.**  
   **Cites:** D §§2–5, Owner’s answers #1–5; P §§3–4, Owner’s answers #1, #7.  
   D still prices and tests a falling bascule, a permanent-deck door, and a minified gangplank. The ruling selects all three, removes the carried colony plank item, requires tipping, and adds conditional automatic operation. P’s recommendation and build order still implement deck-carried pipes and height-blind transfer, although poles and levelling were selected. These are obsolete implementation plans.  
   **Test:** Follow the written C implementation: uninstalling creates a `MinifiedThing`, directly violating the art-only stored-plank decision.  
   **Fix — WITHIN THE OWNER’S RULINGS:** Replace the engine, persistence, cost and test sections with specifications for the ruled designs. Keep rejected proposals labelled as historical alternatives.

2. **D — blocker: Raising cannot run the destructive collapse operation.**  
   **Cites:** D §2 “Anyone on it,” “Engine”; B §6.3; D Owner’s answer #2.  
   The cited `Collapse` path marks collapse, removes decks and invokes descent. Raising must preserve the structure and tip occupants toward the hinge. Structural collapse additionally drops riders and strikes pawns below. Sharing the destructive operation would produce falls, spike damage, rubble or underpass crushing during an ordinary raise.  
   **Test:** Raise an intact bridge with a raider above, a colonist underneath and spikes below. The raider must undergo the ruled tipping movement; the colonist must not receive collapse damage; the bridge must remain lowerable.  
   **Fix — WITHIN THE OWNER’S RULINGS:** Separate reversible movement from structural failure. Share sequencing helpers only where they carry no destruction, descent, salvage or crushing side effects.

3. **B — blocker: Tipping has no legal destination or obstruction rule.**  
   **Cites:** D Owner’s answer #2; Pit “two states,” prisoner interactions and spike rulings.  
   Pulling enemies inside is ruled behavior. Teleporting them through a closed gate or wall, deleting overflow occupants, or automatically capturing them would break movement and prisoner semantics. A bank destination also must not trigger spike damage merely because the implementation reused descent code.  
   **Test:** Put six armed raiders on a three-wide leaf. Leave one free hinge-bank square, with a closed door and wall behind it. Raise. Check every pawn’s destination, faction, equipment and ability to fight.  
   **Fix — WITHIN THE OWNER’S RULINGS:** Specify deterministic occupant ordering, obstruction checks and ordinary post-movement hostility.  
   **Fix — WOULD NEED HIS RULING:** “If the hinge bank cannot receive every occupant, should raising wait, or should blocked occupants fall?”

4. **A — major: Opposing hinges can contradict “pulls enemies inside.”**  
   **Cites:** D §2 one/two-leaf proposal; Owner’s answers #2, #3, #7.  
   A two-leaf bridge has a hinge on each bank. Tipping toward each leaf’s hinge sends half its occupants toward the outside bank. The proposed topology therefore cannot promise both “toward the hinged side” and “pulls enemies inside” for every occupant. “Winch side” is also ambiguous with two winches.  
   **Test:** Put one raider on each leaf of an opposing-hinge bridge. Raise both and record destinations and permitted lowering interaction cells.  
   **Fix — WITHIN THE OWNER’S RULINGS:** Give every leaf explicit hinge, control-bank and movement identities; do not infer them from faction or current pawn position.  
   **Fix — WOULD NEED HIS RULING:** “For opposing leaves, does each leaf tip toward its own hinge, even when that sends enemies outside—yes or no?”

5. **C — blocker: A generation bump with a 60-tick rebuild delay is not a complete pathing contract.**  
   **Cites:** D §§1–2 “pocket grid,” “pit pathing,” “Path flip cost.”  
   `Decked` can change immediately while the pocket grid, custom costs, cliff masks, reachability cache and existing pawn paths still describe the previous state. “Vanilla’s path grid never sees a pit” does not prove that no vanilla path-data invalidation is needed: 1.6 reuses batched map data across requests. [Ludeon’s modder primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub)  
   **Test:** Raise immediately after a pocket rebuild while pawns already hold crossing paths. Attempt every subsequent step before the next rebuild; then lower after a cached “unreachable” result.  
   **Fix — WITHIN THE OWNER’S RULINGS:** Document every affected cache and its invalidation. Enforce changed-cell legality immediately, invalidate affected paths/results, and publish consistent cost and topology versions. Expensive rebuild batching must not permit stale crossing.

6. **C — blocker: The asynchronous pathfinding handoff is unspecified.**  
   **Cites:** D §1 per-request customizer; B §5.1, P2 prerequisite.  
   A worker must not observe half-updated bridge state, mutable shared masks, or a disposed map. A path requested while lowered can finish after raising. Ludeon explicitly describes 1.6 pathfinding as batched and multithreaded; the existing P2 prerequisite therefore remains applicable. [Ludeon’s modder primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub)  
   **Test:** Issue simultaneous friendly, hostile, animal and floor-band requests while repeatedly toggling two bridges; unload one map with requests outstanding.  
   **Fix — WITHIN THE OWNER’S RULINGS:** Supply immutable/versioned request data, avoid shared mutable per-pawn mask swaps, and reject or revalidate results whose topology version is obsolete. Perform map mutation on the owning game thread.

7. **C — major: Floor-band occupants must survive a toggle without becoming deck riders.**  
   **Cites:** D §2 “Underpass”; B §§2, 5.2, 7; Pit room ruling.  
   Inspecting only `pawn.Position` cannot distinguish a pawn standing on a leaf from one beneath it. Raising can also join floor pockets previously divided by a shallow deck; lowering can divide them again. Those changes affect pit-room membership and confinement, not just route cost.  
   **Test:** Toggle over one pawn above and another below. Repeat at 1.5 m and 2 m clearance, with a prisoner bed in one adjoining pocket. Check tipping, room membership and prison status.  
   **Fix — WITHIN THE OWNER’S RULINGS:** Select riders by their actual band and bridge association. Recompute affected pocket/room connectivity, while preserving the rule that decks create neither roofs nor additional temperature rooms.

8. **C — major: B is not vanilla door semantics unchanged.**  
   **Cites:** D §3 “Who raises it,” “Engine,” “Save/load”; Owner’s answers #2–5.  
   An inside-only lowering permission, hostile-triggered manual lock and ruled tipping behavior are custom semantics. `openInt` and `holdOpenInt` alone do not describe them. The cited one-cell door-region argument also does not establish correctness for a gate “1 to 3 wide.”  
   **Test:** Build a three-wide gate. Approach from both banks and laterally with a colonist, visitor, animal and raider. Spawn a hostile while a friendly is approaching. Check every lane and cached reachability result.  
   **Fix — WITHIN THE OWNER’S RULINGS:** Define the multi-lane gate representation, sided permissions, custom state and invalidation explicitly. Audit all door passage/permission reads instead of assuming the subclass inherits the required behavior.

9. **D — major: Hostile arrival needs an atomic control-mode transition.**  
   **Cites:** D Owner’s answer #5; Pit trapped-enemy and stored-mech rulings.  
   A queued friendly auto-lower must not execute after a hostile appears. Conversely, “locks and moves only when ordered” does not authorize automatically raising a lowered bridge. Trapped armed enemies remain hostiles; absence of a reachable hostile is not absence of hostiles on the map.  
   **Test:** Queue auto-lowering, then drop a hostile onto the map before execution. Separately retain one hostile mech in a sealed pit. Verify automatic operation remains disabled and that threat arrival does not itself order raising.  
   **Fix — WITHIN THE OWNER’S RULINGS:** Recheck the map’s hostile condition when accepting and committing automatic movement, cancel pending automatic requests on locking, and expose why the bridge is locked.

10. **D — major: Power loss and winch destruction have incompatible failure paths.**  
    **Cites:** D §2 power, interrupted work, winch destruction and fire; B §6.3; D Owner’s answer #4.  
    “Interrupted stays part-way,” “destroying the winch lowers the leaf,” and “losing an anchor causes swing-down collapse” require distinct conditions. If the winch is also the anchor, destroying it cannot both restore an intact crossing and remove its structural support. Steel’s manual fallback also remains an unruled proposal.  
    **Test:** Cut power, destroy machinery and destroy structural support separately at each movement stage. Repeat during lowering with a pawn beneath the leaf.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Define structural support separately from operating machinery and give structural failure precedence over normal movement.  
    **Fix — WOULD NEED HIS RULING:** “On power loss, should an intact steel leaf freeze or lower?” “May steel be hand-winched without power—yes or no?”

11. **C — major: `raisedSquares` alone is not a specified save format.**  
    **Cites:** D §2 “Engine,” “Save/load,” interrupted work; §3 vanilla-only scribing claim.  
    A count is sufficient only if it implies one deterministic arrangement. It does not presently specify independent leaves, lane synchronization, target direction, committed tipping, movement progress or control overrides. Loading must not repeat a completed tip or destruction event.  
    **Test:** Save after every movement step, including immediately after occupants move. Reload, interrupt the worker, destroy one control building and save again. Check for duplicate movement and orphaned records.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Define versioned authoritative state, stable leaf/support references and event commit boundaries. Resolve references before rebuilding derived caches; validate counts and missing supports after load. Do not persist disposable pathing snapshots.

12. **B — major: “The trench giver takes over” is an unproved AI handoff.**  
    **Cites:** D §§1–3 raider behavior; Owner’s answer #6.  
    A raised leaf does not itself guarantee that target selection, reachability and breach jobs recognize the denial. The winch can be on the inaccessible bank. A hostile may also retain a bridge path or keep retrying a target that coarse reachability considers reachable.  
    **Test:** Raise during an approaching raid. Exercise ordinary assault, sapper, breacher, jumper and plank-equipped raids. Include a reachable decoy outside and an inaccessible winch inside. Verify legal progress rather than repeated failed jobs.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Define the failed-crossing-to-countermeasure handoff and invalidate affected jobs. Winch attacks must have executable routes. Preserve the ruled free crossing for flyers/jumpers/floaters and the existing titan stride behavior.

13. **B — major: Raider planks need deployment accounting and structural limits.**  
    **Cites:** D §4 raider-plank proposal; Owner’s answers #1, #6–8.  
    Reusing a ladder slot does not define plank length, support, consumption, reservation or cleanup. An interrupted deployment could duplicate free crossings; an unconstrained one could bridge any moat or overwrite a wall. The colony’s art-only stored planks must also remain distinct from whatever a raid brings.  
    **Test:** Interrupt two raiders deploying into the same slot; kill the carrier during placement; destroy the resulting plank; save/reload midway. Try a gap beyond its material limit.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Use a single reserved deployment transaction, enforce material-specific span and bank requirements, and account for each raid deployment exactly once. Apply ordinary load, fire and destruction behavior after deployment.

14. **A — blocker: “Cord allowed, conduit forbidden” has no reliable mechanical discriminator.**  
    **Cites:** P §1.1 GSS facts; Owner’s answers #1, #4.  
    P says GSS restyles vanilla `PowerConduit` rather than replacing it. The ruling permits cords on decks while requiring conduit to use poles. Classification by `isPowerConduit` cannot satisfy both; classification by artwork creates a style-changing placement exploit.  
    **Test:** Place the same conduit def with vanilla and GSS styles on a rope bridge. Change style after construction. Its mechanical crossing permission must not silently change.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Introduce an explicit mechanical distinction between deck cords and rigid conduit, independent of cosmetic style.  
    **Fix — WOULD NEED HIS RULING:** “Does the existing GSS-restyled vanilla `PowerConduit` count as an allowed deck cord—yes or no?”

15. **A — major: The placement plan both permits forbidden lines and blocks permitted ones.**  
    **Cites:** P §3B placement; D §2 building prohibition; P Owner’s answers #3–4, #6.  
    The old plan permits rigid pipe on timber/steel decks, excludes rope, and checks excavated cells. The ruling reverses the first two and covers bridge crossings generally. D’s blanket refusal of buildings on moving leaves can also reject permitted cords implemented as buildings. Lending rope `Light` generally would admit unrelated structures.  
    **Test:** Attempt pipe, conduit, hose, cord and a workbench on rope, steel, drawbridge and vanilla bridge crossings; also test a covered pit and shallow dug ditch.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Use one semantic crossing policy across placement, construction and rebuilding. Grant narrow hose/cord exceptions; do not grant general affordances or infer legality solely from displayed terrain.

16. **D — major: Permission to lie on a moving leaf does not define connectivity while raised.**  
    **Cites:** P Owner’s answers #4, #6; P §1 hose length/settling; D Owner’s answers #1–2.  
    A hose or cord may be allowed on the lowered leaf yet lack the slack or attachment geometry to remain connected through movement. Ordinary 2-D replanning could instead redraw a free crossing over the newly opened moat.  
    **Test:** Lay a minimum-length hose across a leaf, raise halfway, then fully raise and reload. Repeat with an energized cord. Check route, length, connection and stock conservation.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Associate carried segments with the moving structure and prevent unsupported automatic rerouting.  
    **Fix — WOULD NEED HIS RULING:** “Do hoses and cords remain connected through raising, or disconnect until lowered?”

17. **D — major: Ramp and ladder hoses require explicit vertical transitions.**  
    **Cites:** P §1 hose world; Owner’s answer #5; B underpass restrictions.  
    An eight-way cell route cannot establish whether a hose crossed the lip, descended a ladder, passed through a wall or connected to a deck-level port from the floor band. Allowing hose descent does not authorize floor-band pumps, tanks or arbitrary buildings beneath decks.  
    **Test:** Drain an 8 m pit through a ladder route. Raise/remove the ladder, block its landing and place a pump directly above the hose endpoint in the same x/z cell. Verify length and port matching.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Add band-aware hose transition edges and endpoint reach checks, retaining existing wall restrictions.  
    **Fix — WOULD NEED HIS RULING:** “When its ladder is raised, should the hanging hose remain suspended or retract/disconnect?”

18. **B — major: Pipe poles must not become unintentional bridge supports or pawn routes.**  
    **Cites:** P §3C; §1.1 anchors requiring only `Light`; Owner’s answer #1; B §§6.1–6.2.  
    Reusing GSS anchors unchanged permits placement wherever their affordance allows—including terrain that P says incorrectly admits infrastructure today. A utility truss also must not supply walking ground, a climb exit or a zero-mass support on a rope deck.  
    **Test:** Try posts on open pit cells, hidden covers and rope decks. Connect across a prison moat and request pawn paths in both directions. Dig out one post’s support.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Validate actual endpoint support and support dependencies. Keep utility edges out of pawn topology and deck detection; count support-building mass where supported by a deck.  
    **Fix — WOULD NEED HIS RULING:** “May pipe-pole supports stand on suspension decks—yes or no?”

19. **C — major: Long-range liquid edges must obey existing component and port limits.**  
    **Cites:** P §1 liquid kernel; §3C; opening pump-port ruling.  
    An aerial edge joining two valid pipe components can create one oversized component. It can also introduce cycles, alternate routes and multiple connections to a pump side. Updating only the local post will leave stale topology after a cut.  
    **Test:** Join two components each using 60% of `MaxConductors`; create a ring with two aerial routes; cut each route in turn. Attempt simultaneous pipe and hose occupation of one pump-side port.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Apply component limits after incorporating aerial edges, preserve one-port-per-side semantics, and rebuild affected connectivity on edge changes. Use one logical edge per connection, without duplicate cardinal and aerial conduction.

20. **D — major: Destruction needs support ownership and exactly-once cleanup.**  
    **Cites:** P §§3B–3C collapse/downed-span handling; B §6.3; D fire and winch failure.  
    “Destroy lines on the collapsed squares” is now insufficient. A pole-supported line can cross the picture of a bridge without depending on it; a deck-carried cord does depend on it. Simultaneous anchor loss, deck destruction and span callbacks can duplicate salvage, hose spills or fallen-wire effects. Naming `KillFinalize` does not establish complete lifecycle cleanup.  
    **Test:** Explode both posts and the bridge in one event. Check network removal, liquid stock, salvage and fallen wires exactly once; repeat with only the bridge destroyed.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Track each segment’s actual supports and centralize idempotent teardown. Verify ordinary despawn/network notifications and ensure a disconnected fallen wire is not treated as powered by a stale edge.

21. **D — major: Digging, construction races and legacy saves need separate rules.**  
    **Cites:** P §3B dig/migration; Owner’s answers #1–2; §1.1 blueprint/frame facts.  
    The old “move the line first” refusal contradicts the new dig-break ruling. Breaking at designation time would destroy a line even if digging never happens. Checking only blueprint placement permits a frame to finish after support disappears. Existing unsupported finished lines are a separate migration question.  
    **Test:** Designate then cancel digging; complete digging beneath a live line; remove support between frame delivery and completion; load an old unsupported pipe.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Apply dig consequences when the terrain edit commits, revalidate support at construction completion, and prevent unsupported automatic rebuilding.  
    **Fix — WOULD NEED HIS RULING:** “On loading an old save, should unsupported floor pipe/conduit be broken immediately—yes or no?”

22. **A — blocker: Passive body levelling needs a narrow exception to the pump-intake rule.**  
    **Cites:** P Owner’s answer #7; GSS #3, #9, #12; P §3 shared height-blind semantics.  
    GSS requires pumps to pull from the world and fill storage. The newer ruling permits passive exchange between water bodies. Leaving both statements unqualified either prevents levelling or permits free world-to-tank filling. “Everything is height-blind” also cannot govern the direction of passive levelling.  
    **Test:** Connect two unequal water bodies without a pump: they should slowly approach equilibrium. Replace the receiving world endpoint with a tank: it must not acquire the same pump-free intake permission.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Specify passive world-body-to-world-body transfer as the new exception. Preserve pump-required storage filling and existing tank drainage. Separate boundary-level calculations from internal pipe transport.

23. **B — blocker: Levelling must use surface elevation and conserved volume.**  
    **Cites:** P Owner’s answer #7; B §2 level-surface model.  
    Equal fill depth is not equal water level. Equal litres per body is not equal level either. Independent links can overdraw the same source, reverse repeatedly or create liquid through clamping. A same-body hose must not manufacture circulation or additional volume.  
    **Test:** Connect a one-cell basin to a hundred-cell basin with different floor elevations. Add ten parallel links and then a same-body loop. Require convergence to equal surface elevation, nonnegative volumes and conserved finite-body volume.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Calculate transfer from a consistent surface-elevation convention and each body’s volume/level relationship. Bound combined withdrawals and equilibrium overshoot. Account explicitly for limitless-source exchanges and preserve small transfers at large stored volumes.

24. **D — major: Gravity connections lack priming, mouth-height and off-state semantics.**  
    **Cites:** P Owner’s answers #5, #7; GSS #2, #12–14.  
    Without endpoint immersion checks, a hose can continue extracting water after its intake is exposed. Without an off-state boundary, a switched-off hose can keep draining an entire reservoir, contradicting the ruled small-volume hose drain. A route whose crest exceeds the source surface additionally raises an unanswered siphon/priming question.  
    **Test:** Lower the source below the intake mouth; switch off a filled connecting hose; route another over a crest above both water surfaces.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Stop extraction at an exposed intake and separate drainage of hose contents from continued reservoir transfer.  
    **Fix — WOULD NEED HIS RULING:** “Should a passive connection automatically prime when its highest point is above the source surface—yes or no?”

25. **A — blocker: Cross-body gravity exposes the unresolved fluid-identity rule.**  
    **Cites:** P universal pipe and Owner’s answer #7; Pit “[F] Fluid identity,” unresolved body merging.  
    Connecting water, poison or oil cannot silently overwrite one body’s `FluidDef`, duplicate incompatible contents or neutralize poison for free. A hose connection also must not merge spatial body membership as though the separating land had become a channel.  
    **Test:** Connect fresh water to poison and separately to burning fuel. Disconnect after partial transfer. Inspect fluid identity, quantities, terrain membership and fire state.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Keep spatial bodies distinct across utility links and require an explicit compatibility result before transfer.  
    **Fix — WOULD NEED HIS RULING:** “Should passive levelling refuse connections between different FluidDefs—yes or no?”

26. **C — blocker: “Slowly level out” has no bounded update algorithm.**  
    **Cites:** P Owner’s answer #7; §3C topology cache; B level-surface model.  
    Scanning every cell of every connected body for each hose each tick scales with links × body area. Repainting terrain after every tiny transfer compounds the cost. Independent per-link updates also make results depend on iteration order. If Thing-based timers use 1.6’s variable tick intervals, ignoring elapsed delta changes behavior with update frequency. [Ludeon’s modder primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub)  
    **Test:** Benchmark a 325×325 map with two 40,000-cell basins and 200 links. Compare camera positions, simulation speeds and reordered links; record tick time, allocations and conservation.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Use a budgeted map-owned solver, cached volume/level data, batched withdrawals and thresholded visual updates. Specify cadence, elapsed-tick integration, convergence tolerance and topology-change invalidation.

27. **D — major: “Decks sit above the fill; flooding: nothing” contradicts awash decks.**  
    **Cites:** P §3B flooding; B §2 rule 4, §7; D flood/fire interactions.  
    B explicitly allows water above deck height, especially on sunken decks. Hoses, cords, controls and riders therefore can be submerged. Placement affordances such as `WaterproofConduitable` do not establish a runtime shorting implementation; P itself says existing conduits are not rechecked.  
    **Test:** Use a floor 7 m down, deck 4 m down and water 4 m deep: the deck is under 1 m of water. Raise it with a rider and cord present.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Evaluate rider water depth at the occupied band and remove unconditional flood immunity claims.  
    **Fix — WOULD NEED HIS RULING:** “Should a submerged deck cord short—yes or no?”

28. **C — major: Hidden spawned deck Things retain interactions at their old positions.**  
    **Cites:** D §2 spawned raised squares, upright overlay and fire.  
    Making `Decked` false changes selected readers, not every `ThingGrid`, targeting, collision, repair, fire or explosion query. The old far-end tiles can remain invisible attack/work targets while the visible upright leaf is at the winch. Raised damage must also remain associated with the correct structure.  
    **Test:** Raise fully. Target, ignite and repair both the empty far-end cells and visible upright leaf. Repeat with an explosion at each location and a pawn walking beneath.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Audit spatial interactions beyond `DeckAt`. Define the raised leaf’s authoritative target/work geometry and route damage to its persistent structure without leaving invisible blockers or repair targets.

29. **C — major: Map and layer identity must be part of every connection and cache.**  
    **Cites:** D map-component record; P §3C aerial graph; both docs’ DLC assumptions.  
    Cell indices, body IDs and world tile integers alone cannot identify endpoints across multiple maps and Odyssey layers. A static cache can connect unrelated coordinates or retain a removed map. Ludeon recommends `PlanetTile` for layers and provides `PreSwapMap`/`PostSwapMap` callbacks for gravship transfers. [Ludeon’s modder primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub)  
    **Test:** Create two maps with identical cell coordinates and body IDs, including surface/orbit locations. Toggle and transfer on one, then remove it.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Scope records, epochs, jobs and edges to map identity; prohibit accidental cross-map utility edges; clear subscriptions and pending work when maps disappear.

30. **D — major: Gravship transfer cannot be treated as ordinary destruction.**  
    **Cites:** D spawn/despawn and anchor-loss reuse; P aerial endpoints; B collapse rules.  
    Relocation can remove an anchor or post from its old map without destroying it. Feeding that through ordinary despawn/support-loss handling can collapse transported structures, spill their contents or leave duplicate connections behind. A connection crossing the ship boundary needs a gameplay policy.  
    **Test:** Launch with both endpoints aboard, then with only one aboard, including a half-raised leaf and stocked hose. Reland rotated; check endpoints, stock and old-map records.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Distinguish transfer from destruction and rebuild connections after coordinate transformation.  
    **Fix — WOULD NEED HIS RULING:** “Should a bridge or utility connection crossing the gravship boundary block launch—yes or no?”

31. **C — major: The terrain-layer recipe needs verification against the actual 1.6 build.**  
    **Cites:** P §1.1 terrain-change reasoning; B §§1, 2.1, 7 under-layer writing instruction.  
    The context relies heavily on a top/under-layer account of bridge preservation. Ludeon’s 1.6 primer explicitly adds foundation and temporary terrain layers, with foundations including vanilla bridges. That does not prove the cited fix wrong, but “write the under layer” alone is not a verified preservation contract for the current layer stack. [Ludeon’s modder primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub)  
    **Test:** Change water bands beneath a vanilla bridge foundation carrying flooring and conduit, including temporary terrain. Drain, refill and reload.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Pin the supported 1.6 assembly version, inspect its terrain APIs and verify that water writers preserve every unrelated layer and trigger the required support notifications.

32. **E — major: The player cannot predict the new state transitions from the proposed readout.**  
    **Cites:** D settings/readout/live tests; P width prerequisite and Owner’s answers; B load/readout requirements; GSS #5.  
    “Raised/lowered” is insufficient for a part-raised, unpowered, hostile-locked or obstructed bridge. The line art also needs to distinguish deck-carried cords, pole-supported rigid crossings, ladder descents and disconnected segments. An apparently usable lowered route with a locked control is otherwise indistinguishable from a broken command.  
    **Test:** Without debug tools, ask a player to predict whom raising moves, where they land, why lowering is unavailable, and which connections survive bridge loss.  
    **Fix — WITHIN THE OWNER’S RULINGS:** Show actual/target movement state, progress, operating bank, lock reason, power state and obstruction. Preview tipping destinations and identify support/connection status. Honor the width-before-pole-art decision; use existing port labels and status text without reviving the deferred flow-direction display.

The five most important findings are:

- **#2:** Reversible raising must be separate from destructive collapse.
- **#3:** Tipping needs legal destinations and an obstruction ruling.
- **#5:** Bridge state and pathing must change consistently without a stale-crossing window.
- **#22:** Passive body levelling must preserve pump-required storage filling.
- **#23:** Levelling must conserve volume and compare surface elevations.