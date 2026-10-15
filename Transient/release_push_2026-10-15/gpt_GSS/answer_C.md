Source review only: the checks below are proposed, not executed. References use the supplied line numbers. C14–C15 depend on lifecycle code outside this packet.

1. **C1 — critical — A victim-net rebuild can erase an already-booked tap debit.**  
   **Where:** `CompPowerTap.cs:110–115,139–155`; `TapLedger.cs:30–33`.  
   **Mechanism:** The recipient’s trader retains its output, but the victim’s obligation is keyed to its current `PowerNet` object: `ledger.Debit(net, wd, ...)`. Settlement only looks up that same object: `debits.TryGetValue(net, out Entry e)`. If the victim net is replaced before settlement, the new net owes nothing while the existing recipient trader still produces the booked power. This follows the tick ordering documented at `CompPowerTap.cs:148–151`. Saving also omits the outstanding ledger; the precise first-load effect depends on vanilla trader restoration.  
   **Repro:** Let a clamp book a transfer, pause, then add/remove an otherwise irrelevant conduit on the victim grid before the next net tick.  
   **Check:** Extend the conservation test with victim-net replacement between booking and settlement; assert recipient credit equals actual victim loss.  
   **Confidence:** high for net replacement; medium for the reload consequence.

2. **C2 — high — Repaired or removed wires can keep shocking pawns; switching the aerial master off does not stop this immediately.**  
   **Where:** `RM_MapComponent_Aerial.cs:87–96,104–115`; `RM_FallenWireShock.cs:81–85`.  
   **Mechanism:** Topology/settings changes clear layouts and meshes, but leave `shockCells` intact until the next 250-tick sweep. Meanwhile, `CheckPawns` checks only `fallenWireShock`: `if (contacts.Count == 0 || !AerialSettings.fallenWireShock) return;`. It neither checks the master switch nor verifies that the wire still exists. An invisible, already re-strung wire can therefore still kill a weak-heart pawn.  
   **Repro:** Establish contacts for a live fallen wire; immediately re-string it or disable the aerial master; place a pawn on its former contact cell before the next sweep.  
   **Check:** Step through the next 20-tick contact check and assert no shock hediff/death occurs.  
   **Confidence:** high.

3. **C3 — high — The hanging portion’s fake height becomes a ground-level shock zone.**  
   **Where:** `RM_FallenWireShock.cs:62–70`; `AerialMath.cs:429,453–455`; `PoleGeometryTable.cs:28–35`.  
   **Mechanism:** Contacts include **every** rendered point: `foreach (P2 p in l.Pts)`. Those points include insulator height encoded as extra screen/world `z`: `g.Z + h * k * k`. A mast head roughly three cells above its base therefore creates dangerous cells roughly three cells north of the actual ground projection. Only the mast’s own cell is excluded.  
   **Repro:** Cut a horizontal live span. Put a pawn beneath the projected mast-head point, north of the pole and away from the grounded tail.  
   **Check:** Use `census` → `wireStarts`; place the pawn at a start point’s floored cell, then step 20 ticks after contacts exist. That elevated point should not shock a ground pawn.  
   **Confidence:** high.

4. **C4 — high — Fallen ground tails retain the overhead rendering altitude.**  
   **Where:** `RM_MapComponent_Aerial.cs:508–514,721–742`; `AerialMaterials.cs:133,265`.  
   **Mechanism:** Fallen wires use the overhead span material and call `WireMesh(a, f, spanY)`. Every vertex—including the grounded tail—receives that same `y`. Consequently, the tail is layered above pawns and ordinary buildings instead of occupying the ground layer. This misses the supplied “downed span lies on ground” requirement when something overlaps it.  
   **Repro:** Cut a span and walk a pawn across its grounded tail.  
   **Check:** Assert the final grounded vertices returned by `WireMesh` lie below `AltitudeLayer.Pawn`; currently they equal `SpanAltitude`.  
   **Confidence:** high.

5. **C5 — high — Players have no individual “switch off this clamp” control.**  
   **Where:** `RM_AerialAnchors.xml:241–251`; `CompPowerTap.cs:98`; `PowerTheftConsequences.cs:58`.  
   **Mechanism:** The clamp has only `CompPowerTrader` and `CompPowerTap`; there is no `CompFlickable`. Nevertheless, both implementation and player-facing theft letter rely on switching it off: `FlickUtility.WantsToBeOn(parent)` and “Remove or switch off the clamp”. Under ordinary vanilla `BuildingBase`/trader behaviour, that predicate stays true and no flick gizmo exists.  
   **Repro:** Build a working clamp and select it after receiving the discovery letter.  
   **Check:** Inspect the resolved def and gizmos: assert a `CompFlickable` and its toggle command exist.  
   **Confidence:** high, assuming no unseen XML patch adds that comp.

6. **C6 — high — Interior wire contacts usually prevent the promised knockback.**  
   **Where:** `RM_FallenWireShock.cs:174–182`.  
   **Mechanism:** Knockback points away from the tip, often **along the wire**: `IntVec3 dir = at - tip`. Its first step then hits another wire-contact cell, triggering `contacts.ContainsKey(...)` and stopping immediately. On a horizontal grounded tail, a pawn touching an interior cell receives zero displacement despite open ground on both sides.  
   **Repro:** Shock a pawn midway along a straight horizontal grounded tail, with knockback set to two.  
   **Check:** Read its position before and after the shock; assert displacement occurs when adjacent ground away from the strand is free.  
   **Confidence:** high.

7. **C7 — medium — Goodwill charges measure occupied event windows, not draining time.**  
   **Where:** `CompPowerTap.cs:113–119`; `PowerTheftConsequences.cs:62–63`.  
   **Mechanism:** Any positive energy accumulated during a window causes a fixed `EventInterval` of draining time to accrue: `TheftGoodwillAccrue(..., EventInterval, wd > 0f, ...)`. One draining tick followed by 249 idle ticks is charged as 250 draining ticks. This contradicts the documented “ticks it spends draining” behaviour.  
   **Repro:** After discovery, supply stealable power for one tick in each event window.  
   **Check:** An offline scheduler test with 240 such windows should accrue 240 draining ticks, not 60,000 and a full day’s goodwill charge.  
   **Confidence:** high.

8. **C8 — medium — Changing victims forgets previous discovery and unpaid goodwill time.**  
   **Where:** `CompPowerTap.cs:42–44`; `PowerTheftConsequences.cs:48–60`.  
   **Mechanism:** Discovery is remembered in one `caughtBy` slot. Seeing a different victim executes `comp.caughtBy = victim; comp.caughtDrainTicks = 0;`. Returning to the first faction requires another witness and loses its accrued time. The documented “once per clamp per victim faction” memory is not implemented.  
   **Repro:** Get caught stealing from A, change the bitten grid to B and get caught, then return to A with its witnesses absent.  
   **Check:** Seed A’s accrual just below one day, perform that transition, and assert A remains discovered with its remainder preserved.  
   **Confidence:** high.

9. **C9 — medium — A8’s layout-invalidation fix can still leave a permanent obsolete frayed end.**  
   **Where:** `RM_MapComponent_Aerial.cs:87–96,345–346,372–379`; `SectionLayer_RM_AerialGround.cs:46,62–69`.  
   **Mechanism:** `DirtyCell` globally executes `lays.Clear()` but dirties only the supplied section. The ground checker then discards signatures for missing layouts: `if (!lays.ContainsKey(kv.Key) ...) { laySig.Remove(...); continue; }`. Rebuilding a distant layout installs a fresh signature without reprinting its owner section, so the old fray can remain beyond an obstacle while the dynamic cable stops earlier.  
   **Repro:** Put a long fallen tail across a section boundary. Build a wall across it in the remote section; before its sweep, change unrelated anchors elsewhere, clearing all layouts. Let drawing rebuild the tail.  
   **Check:** Compare the owner section’s fray-quad centre with `census`’s new fallen `tip` after another sweep; they must coincide.  
   **Confidence:** high.

10. **C10 — medium — The wire-down alert omits player anchors on non-home maps.**  
    **Where:** `Alert_WireDown.cs:35–40`; `AerialProbe.cs:62`.  
    **Mechanism:** `Culprits()` filters maps with `if (m.IsPlayerHome)`, although the requirement says every player anchor. A player’s temporary expedition or landing map can contain dangerous fallen wires without an alert. The probe masks this distinction because its `alert` command directly calls `Down(map)`, which has no home-map filter.  
    **Repro:** Cut a player span on a map whose `IsPlayerHome` is false.  
    **Check:** Assert both `Down(map)` and the actual alert report include that anchor; currently only the former does.  
    **Confidence:** high.

11. **C11 — medium — Placement previews promise links that automatic linking refuses.**  
    **Where:** `PlaceWorkers_Aerial.cs:28–33`; `RM_MapComponent_Aerial.cs:231–236`.  
    **Mechanism:** Actual auto-linking filters candidates by style: `StylePicker.LookOfThing(o.parent) == look`. The ghost chooses from all anchors without that filter. With distinguishable runs nearby, the preview can point to the nearest incompatible look while construction connects to a farther pole—or nothing.  
    **Repro:** Place a Modern anchor near an Industrial pole and farther from another Modern pole.  
    **Check:** Compare the preview target ID with the completed anchor’s automatically selected partner.  
    **Confidence:** high.

12. **C12 — medium — Re-stringing bypasses the designed pawn work entirely.**  
    **Where:** `CompAerialAnchor.cs:356–366,429–434`.  
    **Mechanism:** The gizmo directly calls `Restring`, which immediately assigns `SpanState.Up`. There is no job, reservation or 300-tick work requirement from design §2.6. It repairs every cut connection instantly while paused, without any available pawn.  
    **Repro:** Cut a span, pause, and invoke “Re-string cut wires”.  
    **Check:** Invoke the actual gizmo action through the bridge with no available workers; assert the span stays cut pending work. It currently becomes Up at the same tick.  
    **Confidence:** high against the supplied design.

13. **C13 — medium — Explosion damage never falls off with distance.**  
    **Where:** `RM_MapComponent_Aerial.cs:973–982`; `AerialMath.cs:529–537`.  
    **Mechanism:** Radius controls only whether a span is hit. Every hit executes `r.Hp = hp - damage`, regardless of distance. The hook also receives no explosion falloff flag. Thus a span just inside a blast radius takes the same damage as one through its centre, contrary to design §2.6’s `damage × falloff`.  
    **Repro:** Detonate a falloff explosion with a span near its outer edge.  
    **Check:** Compare `BlastSpan` damage at the centre and near the radius boundary; assert the edge loses less HP under the designed falloff rule. Currently both lose the full amount.  
    **Confidence:** high.

14. **C14 — medium — Static tap-ledger pruning retains future-tick entries after rollback.**  
    **Where:** `CompPowerTap.cs:139,158`; `TapLedger.cs:21,36–38`.  
    **Mechanism:** The ledger is static, pruning starts only above 64 entries, and removal requires `entry.tick < now - 2`. After loading an earlier save, entries from the abandoned future fail that test and remain until time catches up. Repeated reloads can accumulate old net references. These are reference keys, so this is retention—not an ID-collision debit bug.  
    **Repro:** Steal at a late tick, load a much earlier save, and repeat with newly constructed nets.  
    **Check:** Search all lifecycle callers of `TapRegistry.Clear()`. If none clear on load/new game, assert the ledger drops old net references across a rollback.  
    **Confidence:** medium; an unseen lifecycle reset could close this finding.

15. **C15 — medium — The negative-control reseed switch can contaminate later fixtures and games.**  
    **Where:** `CompAerialAnchor.cs:110,228`; `AerialProbe.cs:77`.  
    **Mechanism:** `debugSkipReseed` is static and suppresses real despawn repair. The supplied files only change it through the probe; save/load does not restore its default. A failed or interrupted negative-control test can therefore leave subsequent maps running without the despawn fix.  
    **Repro:** Send `skipreseed:true`, reload a fixture, then destroy a middle anchor without first sending false.  
    **Check:** Assert the flag is false after load/new game, then run the existing despawn-gap check.  
    **Confidence:** medium; assumes no unseen lifecycle reset.

16. **C16 — low — Cached local drops still allocate and sort every rendered frame.**  
    **Where:** `RM_MapComponent_Aerial.cs:584–592`; `AerialMath.cs:349–355`.  
    **Mechanism:** Every visible connected anchor allocates an insulator list and calls `AssignTerminals`, which creates a dictionary, sorts, and materializes another list. `lastTerminals[...] = term` replaces that dictionary every frame, even when all cached meshes and connections are unchanged and the game is paused. At 200 visible anchors and 60 FPS, that is 12,000 dictionary constructions per second before the accompanying lists.  
    **Repro:** View a dense, connected mast installation while paused.  
    **Check:** Profile steady-state `GC.Alloc` after mesh warm-up; inspect allocation stacks through `DrawLocalDrops → AssignTerminals`.  
    **Confidence:** high.

17. **C17 — low — Ground probe measurements belong to the last regenerated section anywhere.**  
    **Where:** `SectionLayer_RM_AerialGround.cs:20,76–78`; `AerialProbe.cs:216–217`.  
    **Mechanism:** `LastPrintedVerts`, `LastFallenPrinted` and `LastShadowsPrinted` are static, overwritten by each section regeneration, then reported by any map’s census. They are neither map totals nor reliably measurements of the queried map. This can produce stale positive evidence after switching maps or misleading zeroes from an empty section.  
    **Repro:** Regenerate a populated section on A, then query an already-rendered empty map B without regenerating its ground layer.  
    **Check:** Assert B’s ground census is zero independently of which section regenerated last on A.  
    **Confidence:** high.

**Checked, looks fine**

- **Save payloads:** partner references, span state/HP, fallen coordinates, exact cut points, seeds, wire counts and cut-partner IDs are scribed. Null partner references are removed during `PostLoadInit`.
- **A6:** pending auto-link status is now saved and requeued on load.
- **A5/cross-map guards:** `Verdict` rejects despawned endpoints and different maps; `LivePartners` also enforces map equality.
- **A18:** span-cache invalidation now explicitly destroys Unity meshes. That fixes the previously reported change/settings leak; map-removal cleanup is not established here.
- **Power scope:** thread-local depth and `__state`-guarded finalizers are present; appended adjacency is materialized inside the scope. No transpiler or specific named-mod conflict is demonstrated by this packet.
- **A1/A2:** same-tick sharing and switched-off/broken checks are present; their arithmetic looks correct while net identity remains stable.
- **Multiple maps:** watchdog, roof, owner and fallen-contact work runs through each map’s tick, independently of viewing it.
- **Gravship removal plan:** aboard links are preserved, ground links are coiled, and landing reseeds retained links, given the engine lifecycle documented inline.
- **Lamp registration:** the mast has vanilla power, glower, colour controls and flickability.
- **Material caches:** shown material caches use def/style/path keys rather than repeating map or thing IDs; pooled materials should not be treated like owned meshes.
- **Probe reads:** aerial census does not call `ProcessPending`; it does populate layout caches.
- **Defs/localization:** supplied DefOf names match the supplied defs; no `.Translate()` calls occur here. `RM_AerialStyles.xml` and the style-picker implementation were not supplied, so their wiring cannot be validated.
- **FlowWorks:** the references shown are integration/documentation, not leftover hose implementation.