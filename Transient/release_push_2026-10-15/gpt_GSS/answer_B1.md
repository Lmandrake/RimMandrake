Source review only; the checks below have not been run. Assumptions about files outside this packet are stated explicitly.

1. **B11 — high — Styled conduit can escape the invisibility swap.**  
   **File:** `ConduitVisuals.cs:109–114`, `ConduitVisuals.cs:122`

   **What/mechanism:** The swap changes only the `ThingDef` graphic:

   > `d.graphicData = use;`  
   > `d.graphic = use.Graphic;`

   A conduit carrying an Ideology `ThingStyleDef` with its own graphic can resolve that graphic instead. Calling `Notify_ColorChanged()` refreshes the instance but does not make the style’s graphic transparent. The player then sees vanilla-style conduit underneath the cosmetic cords. The existing def-level `CurrentTexPaths()` read can still report success.

   This applies to another mod’s visible conduit style even if GSS’s own style defs already use transparent graphics. **Assumption:** no patch outside this packet overrides styled conduit graphic resolution or also makes those style graphics transparent.

   **Repro:** Give `PowerConduit` a fixture `ThingStyleDef` with an unmistakably visible graphic; spawn a styled conduit and enable cables.

   **Check:** Read the spawned thing’s `StyleDef`, actual `Thing.Graphic.path`, and material texture, alongside `def.graphicData.texPath`. Assert the actual rendered graphic is transparent.

   **Confidence:** medium; the style-resolution path is established, but the other Harmony patches were not supplied.

2. **B12 — medium — Shader-sway strands have no far-zoom representation.**  
   **File:** `SectionLayer_RM_MessyCords.cs:125–140`, `SectionLayer_RM_MessyCords.cs:162`, `SectionLayer_RM_MessyCords.cs:79–80`

   **What/mechanism:** A strand successfully printed with the plant shader exits its iteration:

   > `k++;`  
   > `continue;`

   That bypasses LOD generation below it. At far zoom, the layer then disables every material that is not an LOD material:

   > `sm.disabled = GimmeSomeSlackSettings.lod ? (isLod ? !far : far) : isLod;`

   Plant materials are not in `CordMaterials.lods`. Consequently, shader-rendered hanging strands disappear at far zoom rather than receiving the simplified representation.

   **Assumption:** the unseen component does not explicitly redraw shader-mode strands as a far-zoom fallback. Its documented static/GPU ownership suggests it does not.

   **Repro:** Enable shader sway and LOD; create a wall-terminal hanging strand; zoom from near to far.

   **Check:** For a strand taking `ShaderSwayPrints`, inspect enabled submesh membership and dynamic draw membership at both zooms. Assert exactly one enabled representation. `plantVerts` and `PrintedStatic` alone cannot decide this: they include geometry subsequently disabled by LOD.

   **Confidence:** medium for disappearance; high for the missing static LOD path.

3. **B13 — medium — The hookup replacement does not preserve HiddenConduit suppression when the call reaches it.**  
   **File:** `ConduitVisuals.cs:91–94`, `ConduitVisuals.cs:191–206`

   **What/mechanism:** `HookupTo` deliberately classifies hidden and excluded conduit as `PatchCable`:

   > `if (IsOtherConduit(parent.def) || …) return HookupDraw.PatchCable;`

   The prefix subsequently prints a visible cable for that category:

   > `PrintCable(layer, A, B);`  
   > `return false;`

   There is no HiddenConduit exception before this replacement. Thus any such invocation bypasses the original method’s handling and acquires GSS’s visible cable. Excluded conduit hookups also receive replacement art despite being outside the target set.

   **Assumption:** for the ordinary vanilla repro, HiddenConduit hookups reach this method rather than being rejected earlier in `CompPower.PostPrintOnto`. That caller was not supplied. Direct callers from other mods encounter the replacement regardless.

   **Repro:** Connect a consumer several cells from hidden conduit, with cables and hookup suppression enabled; regenerate its section.

   **Check:** Instrument prefix calls whose `B.def == ThingDefOf.HiddenConduit`, and count replacement primitives. Assert zero visible replacement primitives. An offline invocation with that `B`, a valid layer, and initialized span material also decides the prefix’s behavior directly.

   **Confidence:** high for the prefix behavior; medium for vanilla reachability.

4. **B14 — low — Optional floor ripple allocates full geometry buffers on every evaluation.**  
   **File:** `Core/CordMotion.cs:99–105`

   **What/mechanism:** Every call allocates both:

   > `var o = new List<V2>(n);`  
   > `var arc = new double[n];`

   The section layer explicitly hands rippling strands to the per-frame renderer (`SectionLayer_RM_MessyCords.cs:143–155`). At 1,000 visible strands of 250 points, the arc arrays alone allocate about **2 MB per frame**, before result-list storage and mesh work. This is a concrete GC-pressure source on the requested large-base case, including repeated evaluations of an unchanged paused pose.

   **Assumption:** the unseen dynamic caller evaluates each visible rippling strand every frame, as the section-layer comment describes, without caching identical inputs.

   **Repro:** Enable floor ripple over a large outdoor conduit layout; compare allocation samples while paused with ripple enabled and disabled.

   **Check:** Offline, measure allocated bytes for 1,000 `Ripple` calls over a fixed 250-point strand. Separately sample the live caller’s calls per frame to establish the actual allocation rate.

   **Confidence:** high for allocations; medium for their live frequency and impact.

5. **B15 — low — Whip evaluation becomes progressively more expensive during a session.**  
   **File:** `Core/CordMotion.cs:44–58`

   **What/mechanism:** Every evaluation reconstructs the snap schedule from its beginning:

   > `double snap = 0, acc = H01(seed, 7) * 2.0 - 2.0;`  
   > `while (acc <= tt && idx < 100000)`

   With `tt = t % 10000.0`, work grows with elapsed time until the modulo wraps. At `t = 9000`, each call must examine roughly **at least 4,500 intervals**, because an interval is at most two seconds. With 24 tails evaluated at 60 FPS, that is over six million interval hashes per second before ribbon construction. Removing the RNG allocation did not remove the repeated historical scan.

   **Repro:** Evaluate the same tail and seed at `t = 1` and `t = 9000`.

   **Check:** Instrument interval-loop iterations in the offline motion test. Record counts for those two inputs; the later call demonstrates the time-dependent work directly, without a long live run.

   **Confidence:** high.

6. **B16 — low — The static print census retains removed maps’ strand records.**  
   **File:** `SectionLayer_RM_MessyCords.cs:67–68`, `SectionLayer_RM_MessyCords.cs:95–96`

   **What/mechanism:** Each regenerated section publishes a newly allocated set into a process-wide dictionary:

   > `PrintedStatic[SectionKey(Map, section.botLeft)] = printed;`

   No removal appears in this class. Creating and removing maps with advancing IDs therefore retains their section keys and every recorded strand-key string. This retains diagnostic data rather than the `Map` objects themselves, but repeated temporary-map generation can accumulate substantial managed memory.

   **Assumption:** no external load/map-removal hook clears or prunes `PrintedStatic`; those lifecycle files are in B2.

   **Repro:** Generate and render several temporary maps, then remove them without restarting the process.

   **Check:** Grep all references to `PrintedStatic` for lifecycle cleanup. If absent, read its key/strand counts before and after repeated map creation/removal; assert removed-map entries disappear.

   **Confidence:** medium pending that cross-file grep.

### Checked, looks fine

- **Material-cache lifetime:** `lodCache`, `lods` and `plants` are keyed by installed texture/material assets, not map IDs or ticks. Repeated builds reuse LOD materials; no reload-driven growth is evident.
- **Master-off restoration:** `ConduitVisuals.Apply(false)` restores original def graphics and notifies spawned targets across **all** loaded maps. The hookup prefix also returns vanilla control when disabled.
- **Power overlay:** the overlay branch returns before hookup suppression or replacement.
- **Static-layer gravship guard:** the supplied layer distinguishes ordinary cutscene drawing from the gravship capture pass.
- **Motion randomness:** these motion functions use local seeded hashing/RNG; no global `Rand` use appears here.
- **Previous A19 aspect fix:** the hard-coded dark-strip aspect is gone; rendering delegates to `DecalAspect.Of`. Its actual values require the shared definition, which was not supplied.
- **XML:** the supplied map-mesh flag def and its C# reference agree; no translation calls occur in these files.