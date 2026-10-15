I found **10 actionable issues**: two high, seven medium, and one low. These are source findings; the proposed checks have **not** been run. I found no established save-corruption or gameplay power-delivery defect in this file set.

Paths below are relative to `GimmeSomeSlack/Source/`, except shared geometry files under `_Shared/SlackGeometry/`.

1. **A1 — high — Adjacent transmitter buildings are missing their connecting graph edge.**  
   **Location:** `CordWorldAdapter.cs:73–85,111`.

   Transmitter buildings connect only to adjacent **conduit cells**:

   > `if (world.IsConduit(C(adj)) ... ) m.Hookups.Add(C(adj));`

   There is no corresponding transmitter-to-transmitter adjacency pass. Line 111 handles a connector’s `connectParent`, which does not cover two adjacent transmitters. Consequently, a conduit run carried through adjacent batteries or other transmitter buildings becomes disconnected in the cosmetic graph even though vanilla has one connected power net. This is a remaining gap beside the previous B9 fix.

   **Repro:** Place two adjacent batteries, with conduit leaving opposite sides of the pair. Confirm both conduit arms belong to one vanilla `PowerNet`; inspect the reduced graph for the missing battery-to-battery connection.

   **Check:** One live fixture asserting: the two batteries share a `PowerNet`, both appear as graph nodes, and a graph path joins them through their actual transmitter adjacency.

   **Confidence:** High. The engine premise to verify is that the chosen adjacent transmitter pair conducts directly.

2. **A2 — high — Large tangles emit more connectors than their cables can possibly service.**  
   **Location:** `Core/CordBuilder.cs:860,911–944`.

   Connector count grows with field size:

   > `Math.Max(3, 1 + comp.Count / 2)`

   Cable count is independently capped:

   > `int n = Math.Min(24, ...);`

   Twenty-four cables provide at most 48 ends. Once more than 24 connectors are emitted, the stated requirement of at least two cable ends per connector is mathematically impossible. Large grids therefore produce numerous unused junction boxes or strips, contradicting the intended connected heap. Failed cable lays make the discrepancy larger.

   **Repro:** Build a large dense conduit rectangle on open ground, with ample walkable margin.

   **Check:** Offline, build a 20×20 field and assert `CordAudit.ArtFit(...).PileIdleConnectors == 0`. Also assert the fixture actually emitted more than 24 connectors, so the check cannot pass vacuously.

   **Confidence:** High.

3. **A3 — medium — A closed degree-two ring becomes a broken terminal.**  
   **Location:** `Core/CordGraph.cs:430–435,598–605`; `Core/CordBuilder.cs:748–764`.

   A ring with no kept vertices promotes one ordinary floor cell:

   > `keep.Add(v);`

   Its self-loop contributes degree two. `Classify` handles junctions and isolated nodes, then unconditionally falls through to:

   > `Type = NodeType.Terminal`

   The continuous ring therefore receives terminal displacement, frayed end art and endpoint registry entries. An unpowered ring looks broken despite having no break.

   **Repro:** Lay a hollow conduit perimeter large enough to avoid dense-field collapse, with no machine hookup or branch.

   **Check:** Offline, reduce that perimeter and assert zero `Terminal` nodes, zero `CordEnd`s, and no `FrayDead`/`FrayLive` decals.

   **Confidence:** High.

4. **A4 — medium — The previous tree-invalidation fix is incomplete: its hash changes, but nothing requests the rebuild.**  
   **Location:** `CordWorldAdapter.cs:47–48`; `RM_MapComponent_CordGraph.cs:883–894`; `_Shared/SlackGeometry/CordWorld.cs:172–173`.

   Tree cost now participates in the corridor hash, but the dirty-event mask remains:

   > `Buildings | PowerGrid | Terrain | FogOfWar | Roofs`

   It excludes the tree-only `Things` notification described in the supplied design. There is no periodic corridor rescan. Harvesting or planting a tree therefore leaves existing cords unchanged until another qualifying event causes a rebuild. Reloading can then produce different geometry because it finally samples the new tree state.

   **Repro:** Establish a cord, harvest a tree in its corridor, and perform no other building, terrain or power edits.

   **Check:** Live, record `Builds` and the geometry hash; harvest the tree and advance several frames. Compare against a fresh builder on the same resulting map. Choose a fixture where adding/removing that tree changes the fresh result.

   **Confidence:** High. This specifically reopens the **trigger** half of previous A13/B7.

5. **A5 — medium — String-pulling discards tree avoidance even when a rebuild happens.**  
   **Location:** `_Shared/SlackGeometry/CordPlanner.cs:76,157–180`; `_Shared/SlackGeometry/CordWorld.cs:123–146`.

   A* pays tree cost:

   > `... + w.ExtraCost(q)`

   But string-pulling accepts shortcuts using only obstacle clearance:

   > `if (w.Clearance(s) <= 0.2) return false;`

   Trees are stored as extra cost, not blocked geometry. On otherwise open floor, the pull accepts the direct endpoint-to-endpoint line and erases A*’s tree detour. The subsequent settle also has no tree/post obstacle representation.

   **Repro:** Put a tree on the direct line between two cord endpoints in an open room. Use minimum slack to make the route easy to inspect.

   **Check:** Offline, give the middle cell tree cost 1.5. Verify A* detours around it, then assert the pulled plan retains that avoidance. The current pull returns the straight shortcut through it.

   **Confidence:** High.

6. **A6 — medium — Cached diving cords retain the wrong barrier-entry art after a barrier-type replacement.**  
   **Location:** `Core/CordBuilder.cs:191,390,459–472`; `_Shared/SlackGeometry/CordWorld.cs:172–173`.

   Dive plates depend on `BlockKind`:

   > `k == BlockKind.Wall ? ...StubWall : k == BlockKind.Rock ? ...StubRock : null`

   Cache validation hashes only walkability, door state and extra cost. Replacing an interior barrier with another equally impassable kind preserves the hash, so the cached piece keeps its old wall plate, rock hole, or absence of a plate. A reload/fresh builder produces the new art.

   **Repro:** Make a machine lead dive through a barrier, then replace that barrier with an equally impassable device or another barrier kind without exposing a walkable intermediate state to a rebuild.

   **Check:** Offline, build a diving lead through `Wall`; change only the crossed cells’ kind to `Device`; compare an incremental build against a fresh builder, including decal kinds. They should match.

   **Confidence:** High.

7. **A7 — medium — Changing an attachment’s home wall can reuse a lead ending under its previous wall.**  
   **Location:** `Core/CordBuilder.cs:167–191,664–670`; `CordWorldAdapter.cs:153–158`.

   The adapter correctly derives `HasHome` and `HomeX/HomeZ`, and `IntoArt` uses them:

   > `V2 h = Home(m);`

   Those fields are absent from the edge cache key and corridor hash. If the same attachment retains its ID, footprint and hookup while its attached wall changes, its cached strand still ends beneath the old wall. Fresh construction after reload uses the new wall.

   **Repro:** Reorient or reinstall an attachment at the same footprint between two existing walls while preserving its thing ID and conduit hookup.

   **Check:** Offline, build a machine lead with home wall A, then change only `HomeX/HomeZ` to wall B. Assert incremental geometry equals fresh-builder geometry.

   **Confidence:** High for the cache defect; medium for the live repro. It assumes the chosen attachment supports that rotation/reinstall sequence.

8. **A8 — medium — A visible dirty event after this frame’s rebuild can be consumed without updating the graph.**  
   **Location:** `RM_MapComponent_CordGraph.cs:49,198,831–845,892`.

   Section access suppresses another rebuild in the same frame:

   > `if (Time.frameCount != builtFrame) Rebuild();`

   Meanwhile, the dirty-event patch discards visible events:

   > `...CurrentViewRect.ExpandedBy(3).Contains(loc)) return;`

   If a visible change lands after a rebuild but before its section regenerates, regeneration receives the old pieces and can clear its dirty flag. No `StaleOffscreen` flag preserves that event for the next frame. The deferred-event protection at lines 833–845 covers off-screen events only.

   **Repro:** In one frame, rebuild the component, change a visible wall affecting a cord, then regenerate the affected sections. This can arise through another mod’s later update callback.

   **Check:** One bridge action performing that ordered sequence, followed by two frames without another dirty event; assert published geometry equals a fresh builder’s result.

   **Confidence:** High for the mechanism; medium for ordinary-play frequency. This is a mesh-event latch issue, separate from the previously dismissed gizmo latch.

9. **A9 — medium — Long-run heaps bypass doorway pins.**  
   **Location:** `_Shared/SlackGeometry/CordLayer.cs:426–462,474,241–255`.

   Ordinary loop candidates consult the pin-derived ramp, but mandatory long-run heaps check only clearance:

   > `if (AllClear(w, c, LayParams.RC + 0.02)) { shape = c; break; }`

   Doors are walkable, so this accepts a heap in a doorway. Afterwards, the long-run branch replaces the ramp with an endpoint-distance ramp that also omits doorway pins:

   > `ramp = rs;`

   Finally, `PinMask` pins the already-created doorway heap, preserving it during the settle. This contradicts the explicit “no loops or heaps in the doorway” treatment.

   **Repro:** Run a cord longer than 40 cells through a doorway roughly 1.5–5 cells from an endpoint.

   **Check:** Offline, sweep seeds for that fixed scene and assert no added heap overlaps a door cell. Include a seed that actually admits an end heap near the doorway.

   **Confidence:** High.

10. **A10 — low — Unrelated rebuilds regenerate entire tangle geometry despite edge-cache hits.**  
    **Location:** `Core/CordBuilder.cs:206–218,853–875,900–943`.

    Tangles are explicitly rebuilt every time:

    > `// node pieces: junction decals, tangles (cheap, never cached)`

    `TanglePiece` shuffles cells, selects connectors, constructs and resamples cables, and smooths them. Connector selection additionally scans existing connectors:

    > `cons.Any(o => V2.Dist(o.Pos, at) < 0.45)`

    Thus accepted connector placement alone grows quadratically with connector count. A distant qualifying edit repeats this work even when every cord edge is reused. Replanned entry strands also reconstruct the same connector set through `AttachEnd`.

    **Repro:** Establish a large dense field, then place an unrelated building far away.

    **Check:** Offline, benchmark repeated unchanged builds of a roughly 5,000-cell field. Record total build time and tangle construction calls alongside `LastPlanned == 0`. The latter currently does not mean geometry work was avoided.

    **Confidence:** High for repeated work and complexity; actual hitch duration is unmeasured.

**Checked, looks fine**

- Production graph, edge-cache, live-state and downed-wire dictionaries are instance state. No static thing-ID/map/tick cache of the warned-about class appears here.
- Save omission uses per-call Harmony `__state`, restores the original component in a finalizer, and preserves the original exception.
- `DirtySection` contains the earlier load-time protection for sections not yet constructed.
- The previous B9 connector-to-transmitter fix and A17 transmitter `SetWallHome` call are present; A1 and A7 identify remaining gaps.
- Whip tails beyond the animation cap have a still-drawn path; the previous A10 omission is fixed.
- `MapRemoved` explicitly destroys the component’s dynamic meshes.
- Dark and lit power strips share the corrected aspect ratio.
- Buried endpoints at map boundaries are distinguished from interior hidden ends.
- Core geometry uses local deterministic RNG; existing cosmetic `Rand` usage was deliberately accepted previously and is not re-reported.
- Legacy namespace mapping and old loop-budget-key precedence look correct. Hose-name residue is documented migration support and is outside this consult.
- XML, translations, settings dispatch, material lifecycle, and other Harmony patches were not supplied here; no conclusions about those files are implied.