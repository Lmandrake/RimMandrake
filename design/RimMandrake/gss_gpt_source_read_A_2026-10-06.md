The paste contains no `Hose/` files. I cannot verify the outlet-blend cause, identify its offending lines, check `CheckInstall`’s length accounting, or audit hose carry/cancel cleanup. `LayParams.Hose()` alone does not establish those behaviors.

The findings below concern the supplied source. Paths are relative to `src/RimMandrake/GimmeSomeSlack/Source/`. Checks are proposed reproductions, not tests I executed.

1. **Multiple taps can claim the same energy.**  
   **Location:** `Aerial/CompPowerTap.cs`, `CompPowerTap.CompTick`, `TapRegistry.bypass`, `TapRegistry.Debit`.  
   Every tap reads the victim’s gain with **all tap debits bypassed**, then independently claims its available gain and storage. Two taps can therefore export more energy than the victim can supply; nothing limits their combined debit.  
   **Confidence:** high.  
   **Check:** Give a battery-free victim 500 W of surplus and attach two 500 W taps feeding separate home grids. Compare total exported power against available victim power.

2. **Switched-off or broken taps still drain the victim.**  
   **Location:** `Aerial/CompPowerTap.cs`, `CompPowerTap.CompTick`.  
   Theft and `TapRegistry.Debit` happen before—and independently of—the flick/breakdown checks. Those checks only control enabling `t.PowerOn`; `t.PowerOutput = t.PowerOn ? lastStolenW : 0f` can discard already-stolen energy. A disabled tap can drain batteries and accumulate theft totals while delivering nothing.  
   **Confidence:** high.  
   **Check:** Connect a functioning tap, flick it off, and watch the victim’s batteries and `stolenTotalWd`. Repeat with a breakdown.

3. **Preview and rendering calls advance unseeded `Rand`.**  
   **Location:** `Aerial/ConduitStylePicker.cs`, `Resolve`; `RM_MapComponent_CordGraph.cs`, `DownedWires`.  
   The style getter resolves `Modern_Multi` using `Rand.Range` on every read. The getter also supplies previews, so preview frequency changes the colour eventually placed. Separately, real-time, per-frame spark creation calls `Rand` without a pushed state. Neither path isolates cosmetic/UI randomness from the shared random stream.  
   **Confidence:** high.  
   **Check:** Start from an identical seeded state, vary preview/update call counts without advancing game ticks, then compare the next placement colour and subsequent `Rand` outputs.

4. **“Auto-link selected” can modify enemy anchors.**  
   **Location:** `Aerial/CompAerialAnchor.cs`, `AutoLinkSelected`.  
   The gizmo is offered by a player-owned anchor, but its selection list includes every spawned anchor without filtering faction. `MinimumSpanningLinks` permits pairs sharing a foreign faction, and `TryLink` likewise checks faction equality rather than player ownership. The player can consequently string wires between selected enemy anchors.  
   **Confidence:** high.  
   **Check:** Select one player mast and two nearby, mutually unlinked enemy masts belonging to the same faction. Invoke the gizmo.

5. **Link targeting can add a link to a destroyed source.**  
   **Location:** `Aerial/CompAerialAnchor.cs`, “Link wire” callback, `Verdict`, `TryLink`.  
   Neither `Verdict` nor `TryLink` requires both anchors to remain spawned on the same map. The targeting callback retains `this`. If the source disappears during targeting, a valid target can acquire a link to that despawned source. The dead link consumes capacity although `LivePartners` excludes it.  
   **Confidence:** high.  
   **Check:** Begin linking, destroy the source while targeting remains active, then choose another mast. Inspect its link count and partner reference.

6. **Saving while paused loses queued automatic links.**  
   **Location:** `Aerial/CompAerialAnchor.cs`, `PostSpawnSetup`; `Aerial/RM_MapComponent_Aerial.cs`, `pendingAuto`, `MapComponentTick`.  
   Auto-link requests exist only in an unsaved queue processed by ticks. Build an anchor while paused and save before ticking: after loading, `respawningAfterLoad` prevents requeueing, so that anchor never performs its pending automatic link.  
   **Confidence:** high.  
   **Check:** God-mode build a mast near another mast while paused. Compare unpausing directly against saving/loading before unpausing.

7. **Unroutable cords are still drawn across barriers.**  
   **Location:** `Core/CordPlanner.cs`, `Plan`; `Core/CordBuilder.cs`, `LayEdge`; `SectionLayer_RM_MessyCords.cs`, `Regenerate`.  
   When A* fails, `Plan` appends the destination anyway. `LayEdge` records `Unroutable` but continues building strands; its fallback is the same planned centreline. The renderer never checks `Unroutable`. Projection can also leave a segment jumping across a wall even when its individual vertices have been pushed outside.  
   **Confidence:** high.  
   **Check:** Electrically connect a device across a sealed room wall, with no walkable route to its conduit. Inspect the rendered lead and test every segment against blocked cells.

8. **Fallen aerial wires retain obsolete paths after walls change.**  
   **Location:** `Aerial/RM_MapComponent_Aerial.cs`, `Lays`, `DirtyCell`; `Aerial/SectionLayer_RM_AerialGround.cs`, `Regenerate`.  
   `Lays` depends on live path-grid walkability, but its cache is cleared only through `DirtyCell`. Ordinary building changes can regenerate the ground layer without calling `DirtyCell`; regeneration then retrieves the old lay. A wire can continue through a newly built wall, while a reload computes a shorter, blocked lay.  
   **Confidence:** high.  
   **Check:** Drop a span, build a wall across its fallen path, then compare before and after reloading. Also remove a wall that previously stopped the wire.

9. **Roof changes can make cords disappear or become double-drawn.**  
   **Location:** `RM_MapComponent_CordGraph.cs`, `SwaysNow`, `RipplesNow`, `Sig`; `SectionLayer_RM_MessyCords.cs`, `Regenerate`.  
   Roof state controls whether a strand belongs to the static or dynamic renderer. However, `Sig` does not include that decision. When the roof changes outside the piece’s owning section, rebuilding unchanged geometry does not dirty its owner. The dynamic renderer switches immediately while the static mesh retains its previous omission or inclusion. Plant-sway preference changes have a similar handoff problem.  
   **Confidence:** high.  
   **Check:** Use a long piece owned in another section. Add/remove a roof at its lifted pin or ripple midpoint; look for disappearance or overlapping copies.

10. **The whip limit removes complete hose-like cord ends from view.**  
    **Location:** `SectionLayer_RM_MessyCords.cs`, `Regenerate`; `RM_MapComponent_CordGraph.cs`, `DrawMotion`.  
    Static rendering removes every enabled whip tail and its `OnWhip` fray. Dynamic rendering stops at `MaxSparkingEnds * 3`. Tails beyond that limit receive neither a moving replacement nor a static fallback, leaving visibly truncated cords.  
    **Confidence:** high.  
    **Check:** Put more than the configured limit’s worth of live terminal tails in view. Lower the limit and compare near zoom with far zoom.

11. **A long rippling cord disappears when its midpoint is offscreen.**  
    **Location:** `RM_MapComponent_CordGraph.cs`, ripple branch of `DrawMotion`; `SectionLayer_RM_MessyCords.cs`, `Regenerate`.  
    Static rendering omits the entire rippling strand. Dynamic rendering checks only whether its midpoint is inside the expanded camera rectangle. A visible end or intermediate stretch receives no rendering when the midpoint is elsewhere.  
    **Confidence:** high.  
    **Check:** Enable floor ripple on a long outdoor cord. Pan to one end while keeping its midpoint outside the view.

12. **`sprawlCap` does not cap final extra cord length.**  
    **Location:** `Core/CordLayer.cs`, `Sprawl`, `AddLoops`; `Core/CordBuilder.cs`, `LayEdge`.  
    The target uses `L + maxExtra`, but `restLen = Min(Lq + 0.8 * lost, Max(Lq, target))` preserves excursions already exceeding that target. Ordinary loops permit up to `target * 1.25`; long-run end heaps have no target check. Knot loops and endpoint reshaping happen afterward. Thus the setting’s “at most … extra cord” promise is false.  
    **Confidence:** high.  
    **Check:** Set the cap to two cells and measure each final strand against its planned path length across short, long and spur-bearing scenes.

13. **Tree-cost changes are absent from cache invalidation.**  
    **Location:** `CordWorldAdapter.cs`, tree `SetExtraCost`; `Core/CordBuilder.cs`, `CorridorHash`; `RM_MapComponent_CordGraph.cs`, mesh-dirty mask.  
    A* reads `ExtraCost`, but the reuse hash contains only walkability and door flags. Tree removal leaves those unchanged. Plant mesh changes also are not among the rebuild flags. Even a later rebuild can retain a route planned with obsolete tree costs, whereas a fresh load replans it.  
    **Confidence:** high.  
    **Check:** Create two possible passages whose route choice changes when a tree’s cost is removed. Compare an incremental build with a fresh builder after cutting the tree.

14. **The once-per-frame latch can consume a change without rebuilding it.**  
    **Location:** `RM_MapComponent_CordGraph.cs`, `PiecesForSection`, `MapComponentUpdate`; `Patch_MapDrawer_MapMeshDirty_MarkStale`.  
    A second relevant change after that frame’s rebuild receives cached pieces. For onscreen changes, the dirty-event patch deliberately supplies no pending invalidation. For offscreen changes, `MapComponentUpdate` clears `StaleOffscreen` before discovering that this frame already built. Either path can lose the second change until another event occurs.  
    **Confidence:** medium; the failure requires that ordering within one frame.  
    **Check:** Rebuild, mutate the map, then regenerate its affected section or process the stale flag within the same frame. Advance another frame without further changes and inspect the graph.

15. **Cut spans still join “Restyle this run” operations.**  
    **Location:** `Aerial/RM_MapComponent_ConduitRuns.cs`, `Neighbours`; `Aerial/ConduitStylePicker.cs`, `Patch_TryLink_Bridge`.  
    `Neighbours` traverses all saved span links, including `SpanState.Cut`. Restyling one electrically separated side therefore repaints the other side across a wire that has been taken down. The comments also describe restringing as a bridge operation, but only `TryLink` queues that check.  
    **Confidence:** medium on intended run scope; high on the observed traversal.  
    **Check:** Cut the only span between two distant grids, restyle one side, and inspect the other.

16. **Grouped menu/target gizmos execute separately for each selected object.**  
    **Location:** `Aerial/CompAerialAnchor.cs`, “Link wire” and “Unlink wire”; `Aerial/ConduitStylePicker.cs`, `RestyleGizmo`, `RestyleLampGizmo`.  
    Each action opens its own targeter or float menu bound to one object. Unlike `AutoLinkSelected`, none has a group guard or collected selection. With matching grouped commands, selection iteration determines which object’s menu/target survives; choosing a style does not constitute one operation over the selected runs or lamps.  
    **Confidence:** high, using the grouped-command behavior explicitly documented in `AutoLinkSelected`.  
    **Check:** Select two disconnected runs of the same look, invoke Restyle, and inspect menu creation and which run changes. Repeat with two lamps.

17. **Wall-mounted transmitters never get the wall endpoint adaptation.**  
    **Location:** `CordWorldAdapter.cs`, `Snapshot`’s `transmitterBuildings` loop and connector loop.  
    Only connectors call `SetWallHome`. A wall bracket is a transmitter, so its `MachineInfo.HasHome` stays false. `CordBuilder.IntoArt` consequently finishes its ground lead at the bracket cell’s centroid instead of beneath the supporting wall, despite the explicitly documented wall-attachment rule.  
    **Confidence:** high.  
    **Check:** Put conduit beside a wall bracket. Inspect its snapshot machine record and final lead endpoint against the wall centre.

18. **Span meshes leak when caches are cleared or replaced.**  
    **Location:** `Aerial/RM_MapComponent_Aerial.cs`, `Notify_SpansChanged`, `Notify_SettingsChanged`, `MeshFor`.  
    These paths discard `SpanMesh` entries without destroying their Unity `mesh` objects. Replacement also overwrites an old mesh without destroying it. This differs from the explicit destruction used for fallen and local-drop meshes. Repeated topology/settings changes accumulate native meshes.  
    **Confidence:** high.  
    **Check:** Repeatedly invalidate and redraw spans; count live meshes named `RM_AerialSpan` after collection and compare memory use.

19. **Unpowered power strips double their printed height.**  
    **Location:** `SectionLayer_RM_MessyCords.cs`, decal aspect calculation in `Regenerate`.  
    `PowerStrip` receives aspect `0.5f`, but `PowerStripDark` receives `1f`. The same strip placement therefore becomes a square-height quad when power goes out. This also breaks the tinted-original fallback’s proportions.  
    **Confidence:** high.  
    **Check:** Toggle power to a Modern tangle or device strip and compare its quad dimensions.

20. **“Match its cable run” silently does nothing for an unconnected lamp.**  
    **Location:** `Aerial/ConduitStylePicker.cs`, `RestyleLampGizmo`; `Aerial/RM_MapComponent_ConduitRuns.cs`, `RestyleLamp`.  
    The menu always offers this option. When no run exists, the handler merely sets `lastMessage` and returns before displaying any message—even with `message: true`. The player receives neither a disabled option nor rejection feedback.  
    **Confidence:** high.  
    **Check:** Place an isolated lamp with no connected or adjacent run and choose this option.

**None found:** explicit background-thread work; mismatches between field initializers, `ExposeData` defaults and `ResetToDefaults` in the two supplied settings classes.

The omitted hose implementations and job drivers are still required to complete the hose geometry, maximum-length, reservation, interruption and saved-job-class checks.