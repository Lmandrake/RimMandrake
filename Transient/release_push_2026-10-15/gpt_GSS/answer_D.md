I found **three high-severity issues**, plus several timing, compatibility and probe defects. No critical finding is established by the supplied source. These are source-read findings; I did not run checks or open files.

Paths below are relative to `GimmeSomeSlack`, except `_Shared/StylePicker/StylePickerCore.cs`.

1. **D1 — High: changing the default can give one connected run several looks.**

   **File:line:** `Source/Aerial/RM_MapComponent_ConduitRuns.cs:270–276,300–305`; `Source/Aerial/ConduitStyles.cs:337–341`.

   **What/mechanism:** Adopting or merging into a legacy run preserves its unstored members while explicitly styling incoming members. The decisive rule is:
   > `if (!ConduitStyles.NeedsWrite(...)) { legacyKept++; return; }`

   Meanwhile, `NeedsWrite` preserves an unstyled member whenever `look == defaultLook`. Changing the default later changes those unstored members, while their explicitly styled neighbours retain the previous look. `MaterialiseWinner` does not fix this: `Apply` paints only `plan.Repaint`, which excludes the winner.

   **Repro:** With default Scrapper, create an unstyled conduit run containing an unstyled mast. Build an explicitly styled mast onto that run; it adopts Scrapper. Change the default to Industrial. The legacy mast becomes Industrial; the adopted mast remains Scrapper, within the same run.

   **Check:** Read `cstyles` and `styles` before and after changing the default. Assert that all anchors belonging to the same reported run have the same effective `look`.

   **Confidence:** High.

2. **D2 — High: a lamp can follow a nearby run instead of its actual cable run.**

   **File:line:** `Source/Aerial/RM_MapComponent_ConduitRuns.cs:161–167,178–185,352–360`.

   **What/mechanism:** `RunOfLamp` prioritizes the actual `connectParent`. `LampsOf`, however, falls back to adjacency even when the lamp already has a valid connection to another run:
   > `if (!hooked)`  
   > `... if (cells.Contains(c + dd)) { hooked = true; break; }`

   Consequently, two electrically separate runs can both claim the lamp. Restyling the neighbouring run repaints it, and can subsequently make its real run treat that accidental look as an intentional override.

   **Repro:** Put two separate Scrapper conduit runs two cells apart, with a Scrapper lamp between them. Confirm its connection belongs to run A. Restyle run B to Industrial. The lamp becomes Industrial although “Match its cable run” still identifies A.

   **Check:** Through `cstyles`, establish the lamp’s `run` first. Restyle the other run and assert that the lamp’s `rawStyle` remains unchanged.

   **Confidence:** High.

3. **D3 — High: masters off still assign and display GSS floor-lamp styles.**

   **File:line:** `Source/Aerial/ConduitStylePicker.cs:358,371–374`; `_Shared/StylePicker/StylePickerCore.cs:171–175`; `Defs/Aerial/RM_ConduitStyles.xml:136–186`.

   **What/mechanism:** The master switch hides the stage-2 menu, but does not gate its style getter:
   > `__result = ConduitStylePicker.Resolve(__instance) ?? __result;`

   Existing lamps retain their stored GSS `ThingStyleDef`, whose `graphicData` supplies the custom art. Neither master-off path shown here suppresses that graphic. New lamps also continue receiving GSS styles while their style menu is unavailable.

   This violates the context’s all-off/vanilla-art rule.

   **Repro:** Build a Futuristic floor lamp, turn both masters off, then build another StandingLamp.

   **Check:** Read both lamps’ `rawStyle` and `drawnPath`. After all-off, assert vanilla lamp art; also inspect the newly created blueprint’s stored style.

   **Confidence:** High, assuming no unseen patch suppresses StandingLamp style graphics when disabled.

4. **D4 — Medium: saving before style resolution permanently loses pending placements and bridges.**

   **File:line:** `Source/Aerial/RM_MapComponent_ConduitRuns.cs:29–31,47–48,382–390`; `Source/Aerial/ConduitStylePicker.cs:419–422`.

   **What/mechanism:** Both pending queues exist only in memory. Saving removes the component without draining them:
   > `list.RemoveAt(i);`

   Loading deliberately declines to requeue members:
   > `if (respawningAfterLoad || map == null || ...) return;`

   A save taken in that interval preserves unresolved member styles or a mixed-style newly linked run indefinitely. This is a separate queue from the previously fixed aerial auto-link queue.

   **Repro:** In one synchronous bridge action, place a differently styled member beside an existing run and save before the next update/tick. Reload and advance a tick.

   **Check:** Assert `PendingCount > 0` immediately before saving. Compare the reloaded styles with a control branch that calls `cprocess` before saving.

   **Confidence:** High; the save window is timing-dependent.

5. **D5 — Medium: batched links use future topology when deciding which run wins.**

   **File:line:** `Source/Aerial/RM_MapComponent_ConduitRuns.cs:44,63–68,251–259`.

   **What/mechanism:** The queue stores endpoint pairs, but resolves each pair against the graph containing *all* links already created:
   > `List<Thing> ra = RunOf(a, exclude, a, b);`

   Only the link currently being processed is excluded. Later queued links therefore contribute their areas prematurely. With redundant links forming a cycle, every queued link can instead hit:
   > `if (ra.Contains(b)) return;`

   In that case, no bridge rule runs and different styles can remain connected.

   **Repro:** Prepare runs A/B/C with 10/6/6 conduit cells and different looks; make B the oldest styled member of B+C. Create A–B and B–C spans in one synchronous action, then process. A–B is evaluated as 10 versus 12, whereas processing each link immediately would let A’s style win both merges.

   **Check:** Build identical fixtures; process after each link in one and only after both links in the other. Assert identical final member styles.

   **Confidence:** High for the algorithm; live reachability assumes `TryLink` does not drain this queue synchronously inside its unseen implementation.

6. **D6 — Medium: queued links are consumed after their relationship or map has changed.**

   **File:line:** `Source/Aerial/RM_MapComponent_ConduitRuns.cs:65–67,74–90,251–264`.

   **What/mechanism:** Consumption checks only:
   > `if (a.Spawned && b.Spawned) Link(a, b);`

   It does not verify that an Up link still exists, or that either endpoint still belongs to this component’s map. A link cut or unlinked before consumption still repaints the disconnected runs. If both anchors transfer to another map, the old component can traverse the old map’s grid using the transferred anchors’ positions and repaint unrelated members there.

   The Up-only neighbour fix for A15 is present, but does not validate this deferred bridge operation.

   **Repro:** Queue a link between differently styled runs, cut/unlink it before processing, then process.

   **Check:** Assert the disconnected runs retain their original styles. Add the equivalent transfer case: move both endpoints to map B before processing map A, and assert map A’s styles remain unchanged.

   **Confidence:** Medium. Live reachability assumes unseen cut/unlink/gravship handlers do not drain or cancel this queue first.

7. **D7 — Medium: bulk spawning styled conduit performs quadratic flood-fill work.**

   **File:line:** `Source/Aerial/RM_MapComponent_ConduitRuns.cs:54–59,224–240`; `Source/Aerial/ConduitStylePicker.cs:419–422`.

   **What/mechanism:** Every styled placement floods and sorts its already resolved neighbouring run:
   > `List<Thing> r = RunOf(n, exclude);`

   The fast path applies only to unstyled pieces. For N connected, styled cells queued together, the component revisits approximately `1 + 2 + … + (N−1)` members. At 5,000 cells, that is roughly **12.5 million member visits**, each involving neighbour enumeration and allocations, before counting sorting and information scans.

   **Repro:** Land or synchronously spawn a large connected set of already styled conduit. Save loading avoids this because it skips the spawn queue; a styled gravship landing does not receive the legacy fast path.

   **Check:** Instrument `RunOf` member visits. Process connected batches of N and 2N styled cells; verify approximately fourfold visits rather than twofold.

   **Confidence:** High for complexity; elapsed stall duration is unmeasured.

8. **D8 — Medium: eligible modded conduits are omitted from style-run connectivity.**

   **File:line:** `Source/Aerial/ConduitStyles.cs:25–27,45`; `Source/Aerial/ConduitStylePicker.cs:66–95`; `Source/Aerial/RM_MapComponent_ConduitRuns.cs:85`.

   **What/mechanism:** Registration accepts only the named vanilla conduit defs:
   > `public static readonly string[] ConduitDefs = { "PowerConduit", "WaterproofConduit" };`

   Neighbour traversal accepts only registered members. A third-party conduit can therefore carry power and be rendered as GSS cords while acting as a gap in the style graph. Joining or restyling through it does not enforce one-run-one-style.

   **Repro:** Connect differently styled vanilla conduit sections through a custom `isPowerConduit` def.

   **Check:** Confirm the custom def is a `ConduitVisuals` target and the sections share a power connection; then assert `cstyles` reports one style run and a restyle reaches both sides.

   **Confidence:** High under the context’s stated eligibility rule. Assumption: the unseen adapter includes that custom conduit, as the context says it should.

9. **D9 — Medium: restyling a run overwrites lamps carrying another system’s explicit style.**

   **File:line:** `Source/Aerial/ConduitStylePicker.cs:114–123`; `Source/Aerial/ConduitStyles.cs:328–329`; `Source/Aerial/RM_MapComponent_ConduitRuns.cs:359–360`.

   **What/mechanism:** Unrecognized stored styles become a null *look*. The following rule then treats them as unstyled:
   > `lampLook == null ? restyle : lampLook == (runLookBefore ?? defaultLook)`

   A vanilla Ideology or another mod’s explicitly styled StandingLamp is consequently repainted by “Restyle this run,” despite having a look of its own.

   **Repro:** Connect an explicitly Ideology-styled StandingLamp to a run and restyle that run.

   **Check:** Record its non-null, non-GSS `rawStyle`; invoke `crestyle`; assert that exact style survives.

   **Confidence:** High for the overwrite mechanism; medium for whether every Ideology-assigned style should count as an intentional lamp override.

10. **D10 — Medium, conditional: tangle construction still selects its art kind from the global default.**

    **File:line:** `Source/GimmeSomeSlackMod.cs:164–168`; `Source/CordMaterials.cs:316–325,344–345`.

    **What/mechanism:** Build options select:
    > `Pile = style == CordStyle.ExtensionCord ? PileArt.Strips : PileArt.Junctions`

    Here `style` is the global default. Per-piece material lookup preserves the selected `DecalKind`; it cannot itself turn junctions into power strips. Thus a fully styled Modern run can receive junction piles under a Scrapper default, and changing only the default can change its pile construction.

    **Assumption:** The unseen cord graph/core does not subsequently rewrite pile decal kinds according to each piece’s stored look.

    **Repro:** Build a fully Modern-styled dense grid with default Scrapper, then change only the default to Modern.

    **Check:** Compare `cstyles` piece `decalTex` results before and after. A fully styled run’s pile kinds/textures should remain identical.

    **Confidence:** Medium; the missing graph/core can settle or refute this.

11. **D11 — Medium: last-picked looks can leak into the next new game.**

    **File:line:** `Source/Aerial/ConduitStylePicker.cs:41,136–149`; `_Shared/StylePicker/StylePickerCore.cs:24,101–108,123`.

    **What/mechanism:** Both picker registries retain selections for the process lifetime, and always prefer them over the default:
    > `return LastPicked(d) ?? DefaultKey(d);`

    No production game-start/reset hook is shown. A new game in the same process therefore starts with the previous colony’s choices, contrary to the settings text that the default determines what new games start with.

    **Repro:** Pick Futuristic, return to the main menu, and start another game with default Scrapper.

    **Check:** Before making any new selection, read each designator’s resolved style and assert the configured default.

    **Confidence:** Medium. Assumption: no unseen lifecycle handler calls both `ClearPicks` methods. Remembering picks within one game is intentional and is not the finding.

12. **D12 — Medium: placement probes can act on the current map while reporting success for another map.**

    **File:line:** `Source/Aerial/ConduitStyleProbe.cs:90–107`; `Source/Aerial/StyleProbeAerial.cs:109–122`.

    **What/mechanism:** These methods accept `map`, but invoke the Architect designator without selecting that map:
    > `des.DesignateSingleCell(c);`

    They then search the supplied map for the result. Both return success even when `made == null`. A multi-map check can thus place a building on map A, inspect map B, and receive a successful response.

    **Repro:** Keep A current; directly invoke either placement method with map B and a coordinate valid on both.

    **Check:** Census both maps before and after. Assert exactly one building/blueprint was created on B and none on A; require non-null `made`.

    **Confidence:** High under vanilla designator current-map semantics. The unseen dispatcher may constrain ordinary calls to the current map, but these public methods do not enforce that constraint.

13. **D13 — Low: placement hints reuse another map’s cached result.**

    **File:line:** `Source/Aerial/ConduitStylePicker.cs:261–270`.

    **What/mechanism:** The static cache is keyed only by cell and frame:
    > `if (c == hintCell && Time.frameCount - hintFrame < 30) return hintText;`

    Switching maps at the same mouse cell can display another map’s join/winner prediction for up to 30 frames.

    **Repro:** Move between two maps with differently styled runs under the same coordinate.

    **Check:** In one frame, call `JoinsHint(A, c)` followed by `JoinsHint(B, c)` and compare the second result against B’s independently calculated runs.

    **Confidence:** High.

14. **D14 — Low: `cline` overshoots endpoints for unequal diagonal deltas.**

    **File:line:** `Source/Aerial/ConduitStyleProbe.cs:84–85`.

    **What/mechanism:** Both axes advance by their sign for the maximum axis distance:
    > `new IntVec3(a.x + dx * i, 0, a.z + dz * i)`

    For `(10,10) → (14,12)`, the probe instead ends at `(14,14)`. Geometry checks can therefore exercise a different scene from the requested one.

    **Repro:** Invoke that `cline` command on clear terrain.

    **Check:** An offline assertion over the generated coordinates should require the final cell to equal the requested endpoint.

    **Confidence:** High.

**Checked, looks fine**

- A15’s direct flood-fill fix is present: neighbours traverse only `SpanState.Up`.
- A20’s unconnected-lamp feedback fix is present and emits the rejection message before returning.
- Placement queue processing rejects members that are despawned or have moved to another map; the corresponding protection is missing specifically for queued links.
- The legacy `Thing.StyleDef` fallback only answers the getter; it does not write the saved style field.
- Anchor art uses individual style graphics and style-specific geometry, rather than editing shared ThingDef graphics.
- The supplied XML contains the expected **28 stage-2** and **12 anchor** style defs, matching the generated names.
- Material/LOD caches are keyed by the finite texture/material catalogue, not repeating thing IDs or ticks. I found no reload-ID collision in them.
- The supplied style files contain no `.Translate()` calls requiring missing Keyed entries.
- The previously accepted random preview behaviour is unchanged and is not re-reported. Hose implementation remains outside this consult.