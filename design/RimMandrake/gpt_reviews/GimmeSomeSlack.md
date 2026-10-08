**1. DEBUGGING**

This bundle is incomplete: the cord kernels, two central map components, hose implementation, most XML, and validation script are marked omitted. Their correctness is **UNVERIFIABLE**. The findings below concern supplied code; comments describing previous live verification are not evidence that this refactor works.

Line references are relative to each inlined file.

1. **Same-frame changes can be permanently dropped.**  
   `Source/RM_MapComponent_CordGraph.cs:48`, `:682`. Rebuilding once per frame is being used as a substitute for tracking changes. If another edit occurs after that frame’s rebuild, `PiecesForSection` returns old pieces. Worse, `MapComponentUpdate` clears `StaleOffscreen` before deciding whether it can rebuild. A second offscreen edit can therefore lose its pending refresh entirely.  
   **Minimal fix:** track a topology revision and last-built revision. Defer an outstanding change rather than clearing it when rebuilding is suppressed.  
   **Severity: high. Confidence: high.**

2. **Roof changes do not reliably invalidate the section owning the affected strand.**  
   `Source/RM_MapComponent_CordGraph.cs:269`, `:440`; `Source/SectionLayer_RM_MessyCords.cs:130`. Whether a floor strand is printed statically depends on its midpoint’s roof. Section signatures contain geometry, seeds and material indices, but no roof-dependent rendering state. Roofing a distant midpoint can leave the owner section unchanged: the dynamic path stops drawing, while its static mesh still omits the strand. Removing that roof can produce duplicate drawing.  
   **Minimal fix:** include rendering eligibility in owner-section signatures, or explicitly dirty owners whose roof-dependent cells changed.  
   **Severity: medium. Confidence: high.**

3. **Changing vanilla’s plant-sway preference can make cords disappear or double.**  
   `Source/RM_MapComponent_CordGraph.cs:401`, `:440`; `Source/SectionLayer_RM_MessyCords.cs:109`, `:130`. Static exclusion is decided during regeneration; dynamic eligibility reads `Prefs.PlantWindSway` continuously. No supplied code invalidates static meshes when that preference changes.  
   **Minimal fix:** detect preference transitions and regenerate affected owner sections. Apply the same transition handling when the effective shader route changes.  
   **Severity: medium. Confidence: high.**

4. **Dynamic culling tests a point instead of the strand’s extent.**  
   `Source/RM_MapComponent_CordGraph.cs:496`, `:534`, `:562`. A long rippling strand disappears when its midpoint leaves the expanded viewport, even if much of the cord remains visible. Sway similarly tests only the pin. The whip “tip” expression actually selects the joint: after reversing a start tail, that indexed point becomes `tail[0]`.  
   **Minimal fix:** cull against cached strand/tail bounds expanded by maximum displacement.  
   **Severity: medium. Confidence: high.**

5. **Lifted strands have no far-zoom representation.**  
   `Source/SectionLayer_RM_MessyCords.cs:109`, `:112`, `:144`; `Source/RM_MapComponent_CordGraph.cs:471`. CPU-swaying strands skip the remainder of static printing, including LOD generation. Shader-swaying strands also `continue` before LOD generation. At far zoom, dynamic drawing stops and non-LOD submeshes are disabled. These strands consequently disappear.  
   **Minimal fix:** generate the simplified representation before selecting the near-view rendering path.  
   **Severity: medium. Confidence: high.**

6. **Far zoom disables wall sparks and selection highlighting, independently of their settings.**  
   `Source/RM_MapComponent_CordGraph.cs:471`, `:577`. `DrawMotion` returns before `DownedWires` and `DrawHighlight`. Meanwhile, `Sparks` deliberately skips wall ends owned by the downed-wire schedule. Zooming out therefore stops their spark production and removes highlighting.  
   **Minimal fix:** separate effects and highlighting from the geometry-motion early return.  
   **Severity: medium. Confidence: high.**

7. **The “most sparking ends per map” limit is not a shared limit.**  
   `Source/RM_MapComponent_CordGraph.cs:350`, `:583`. Ordinary sparks and downed-wire sparks independently admit up to `MaxSparkingEnds`. A map can have the configured number of floor ends plus the configured number of wall ends emitting. Ordinary sparks also count wall ends before skipping them, potentially starving later floor ends.  
   **Minimal fix:** select one eligible endpoint set and share it across sparks, glow and downed-wire processing.  
   **Severity: medium. Confidence: high.**

8. **Spark intensity does not scale the downed-wire spark rate.**  
   `Source/RM_MapComponent_CordGraph.cs:583`, `:606`. Positive intensity enables the schedule and changes flash size, but no intensity value reaches the schedule constructor or `SparksDue(now)`. Changing intensity from 0.5 to 2 produces the same scheduled micro-spark count, unlike ordinary sparks.  
   **Minimal fix:** scale scheduled emission explicitly, preserving fractional emission credit.  
   **Severity: low. Confidence: high.**

9. **Offscreen endpoints consume the effect budget before visible endpoints.**  
   `Source/RM_MapComponent_CordGraph.cs:333`, `:354`, `:587`. Glow and spark limits follow piece iteration order without viewport filtering before admission. The first live ends elsewhere on the map can suppress every visible broken end.  
   **Minimal fix:** prioritize visible endpoints; use a stable rotation for any remaining map-wide budget.  
   **Severity: low. Confidence: high.**

10. **The rebuild exception boundary excludes important failure paths.**  
    `Source/RM_MapComponent_CordGraph.cs:205`, `:210`, `:213`; `Source/SectionLayer_RM_MessyCords.cs:80`. Snapshot construction and style collection happen outside the `try`. A failure there escapes after the requesting section has cleared its mesh. A caught builder failure instead publishes an empty piece set, removing all cords while conduit art remains invisible.  
    **Minimal fix:** construct the complete replacement inside one guarded operation and publish only on success. Retain the previous complete state on failure, with an explicit retry condition.  
    **Severity: high. Confidence: high.**

11. **Ordinary mesh regeneration triggers unnecessary whole-map work.**  
    `Source/RM_MapComponent_CordGraph.cs:48`, `:205`. Any requesting section in a later frame causes another full snapshot, style scan, seed computation and signature comparison—even if it was dirtied only to reprint already-computed pieces. Builder edge reuse does not eliminate these adapter costs.  
    **Minimal fix:** distinguish topology invalidation from owner-mesh invalidation; rebuild only for a newer topology revision.  
    **Severity: medium. Confidence: high.**

12. **Per-frame motion repeatedly scans the whole piece collection.**  
    `Source/RM_MapComponent_CordGraph.cs:479`, `:485`, `:529`, `:553`. The current ten global material indices cause repeated full scans for whip, sway and optionally ripple. Visibility tests occur inside those scans; visible strands then allocate new point lists. Disabling sway still leaves its scanning loop active.  
    **Minimal fix:** bucket pieces by material and spatial extent during rebuilding, skip disabled passes, and reuse deformation buffers.  
    **Severity: medium. Confidence: high.**

13. **Native motion meshes have no supplied destruction path.**  
    `Source/RM_MapComponent_CordGraph.cs:378`, `:448`. `Fresh` creates Unity `Mesh` objects, including empty ones because `Flush` allocates before checking `mv.Count`. There is no map-removal cleanup in this supplied component. Repeated map creation/removal can retain native allocations.  
    **Minimal fix:** allocate only when needed and destroy owned meshes when the map is discarded.  
    **Severity: medium. Confidence: high.**

14. **Multi-map diagnostics can report another map’s reset counters.**  
    `Source/RM_MapComponent_CordGraph.cs:326`, `:468`. Static draw counters are reset before checking `Find.CurrentMap != map`. An inactive map updating afterward can erase the active map’s results. Probe servicing also occurs before that component draws its current frame.  
    **Minimal fix:** make counters instance state and include the map ID and measured frame in probe responses.  
    **Severity: medium for validation. Confidence: high.**

15. **The renderer silently discards geometry at its vertex limit.**  
    `Source/SectionLayer_RM_MessyCords.cs:215`, `:246`. Once a material submesh exceeds 65,000 vertices, subsequent ribbons or decals simply return zero. Dense sections lose cables without an error or an explicit overflow count.  
    **Minimal fix:** split into additional submeshes, or use supported 32-bit meshes; expose overflow diagnostics.  
    **Severity: medium. Confidence: high.**

16. **Cross-map anchors pass link validation.**  
    `Source/Aerial/CompAerialAnchor.cs:247`. `Verdict` checks spawning, faction, coordinates and range, but never requires `a.Map == b.Map`. Public callers can create reciprocal links between different maps. `LivePartners` excludes those links electrically, leaving occupied link slots and saved references without the promised connection.  
    **Minimal fix:** reject different maps before constructing `AnchorInfo`; also guard topology mutators.  
    **Severity: medium. Confidence: high.**

17. **Cut-point precision is discarded immediately and cannot survive saving.**  
    `Source/Aerial/CompAerialAnchor.cs:43`, `:291`. `Cut` computes an exact position, floors it into an `IntVec3`, and stores cable lengths measured to the original position. `FallenCord` has no field capable of retaining the original cut position. The supplied aerial probe subsequently treats the target as the cell centre. Thus target position and recorded length disagree; a diagonal boundary cut can shift by roughly 0.71 cells.  
    **Minimal fix:** save exact horizontal coordinates, with a legacy fallback to the old cell centre.  
    **Severity: medium. Confidence: high for precision loss; actual laying interpretation is UNVERIFIABLE because the component is omitted.**

18. **`LayFallen` validates a different curve from the one it emits.**  
    `Source/Aerial/AerialMath.cs:369` (`LayFallen`). The collision pass evaluates `ground(s, want)`. After shortening the reach, generation evaluates `ground(sPos, reach)`, changing the bow along the entire path. The emitted curve can enter a blocked cell that the checked curve avoided.  
    A direct arithmetic counterexample uses seed 0, `top == basePt == (0.5, 0.8)`, target `(8.5, 0.8)`, length 8, and blocked cells `(4,0)` and `(2,1)`: checking stops at reach 3.25; the regenerated bow reaches approximately `(2,1.00193)`, inside `(2,1)`.  
    **Minimal fix:** preserve the checked curve when truncating, or revalidate the final curve including its endpoint and crossed cells.  
    **Severity: medium. Confidence: high.**

19. **The tap debit ledger does not establish exactly-once payment.**  
    `Source/Aerial/CompPowerTap.cs:134`, `:153`. `Owed` exposes the same debit during its recorded tick and the following tick, without recording whether the victim already paid it. If the victim net processes after the tap, then the tap stops next tick, the old debit remains available for a second payment. Conversely, a net processed before taps needs the delayed debit. One entry cannot distinguish those histories.  
    **Minimal fix:** settle transfers in one defined power-accounting phase, with explicit pending and settled tick records.  
    **Severity: high. Confidence: high in the ledger ambiguity; the actual engine ordering and resulting live loss are UNVERIFIABLE from this bundle.**

20. **Tap connection guards use incompatible ownership predicates.**  
    `Source/Aerial/CompPowerTap.cs:197`, `:210`, `:225`. Candidate nets are permitted if they contain *any* same-faction transmitter; the final connection is rejected if the chosen transmitter itself is foreign. A mixed-faction net can pass the first guard, repeatedly select a nearby foreign transmitter, fail the second, and requeue.  
    **Minimal fix:** apply ownership filtering to transmitter candidates, or consistently define ownership at net level.  
    **Severity: medium. Confidence: high in the predicate disagreement; exact retry behavior is UNVERIFIABLE without the target method.**

21. **Non-finite settings can propagate into power accounting.**  
    `Source/Aerial/CompPowerTap.cs:100`, `:108`. The tap consumes `tapRate` without finite-value validation. The supplied probe accepts converted floating-point values without normalization. A NaN rate survives the kernel’s comparisons, produces NaN stolen energy, contaminates totals, and can reach an already-on trader’s `PowerOutput`. Slider limits do not protect settings files or probes.  
    **Minimal fix:** normalize loaded and probe-supplied settings; reject NaN/infinity and validate energy values before publication.  
    **Severity: high. Confidence: high.**

22. **Tap consequence accounting loses information across saves and victim changes.**  
    `Source/Aerial/CompPowerTap.cs:39`, `:56`, `:106`, `:111`. `sinceEventWd` is not Scribed. Saving before the reporting interval loses unreported energy on reload. The accumulator also combines multiple victims, then attributes the entire total to the victim found on the reporting tick—even null if the connection disappeared.  
    **Minimal fix:** persist pending amounts keyed by victim identity, or settle the old victim before switching.  
    **Severity: low currently; medium once consequence subscribers exist. Confidence: high.**

23. **The settings round-trip probe is not exception-safe.**  
    `Source/StyleProbe.cs:122`, `:134`, `:136`, `:143`. It overwrites the real settings file and resets every static setting, but restoration is not in `finally`. A write/read exception can leave the test style on disk or default values in memory. Successful reads restore the other fields; the defect is the failure path.  
    **Minimal fix:** snapshot all settings and original file contents, restore both in `finally`, and run ordinary round-trip tests against an isolated file.  
    **Severity: medium. Confidence: high.**

24. **The “fresh” validation oracle uses different build inputs and misses stale extras.**  
    `Source/RM_MapComponent_CordGraph.cs:212`, contrasted with `GimmeSomeSlackProbe.Fresh`. Production adds the per-cell `PileAt` callback; `Fresh` does not. Styled runs can therefore produce differences unrelated to cache correctness. Its comparison also only iterates freshly generated edges, so obsolete cached edges are not counted.  
    **Minimal fix:** share input construction while keeping builders independent; compare both key sets and geometry.  
    **Severity: medium for validation. Confidence: high in the input/comparison mismatch.**

25. **Harmony scope cleanup can corrupt the depth after another prefix throws.**  
    `Source/Aerial/AerialPowerPatch.cs:31`, `:38`. Finalizers unconditionally decrement thread-local depth. If an earlier mod’s prefix throws before this mod increments it, the finalizer can decrement an unentered scope. Subsequent builds can run at depth zero and omit aerial neighbours. Harmony finalizers cover exceptions from prefixes as well as the original method. [Harmony finalizer documentation](https://harmony.pardeike.net/v2/articles/patching-finalizer.html).  
    **Minimal fix:** record whether this invocation entered the scope in `__state`; decrement only for an entered invocation.  
    **Severity: high when triggered. Confidence: high.**

Additional requested checks that remain **UNVERIFIABLE**:

- Kernel routing, off-by-one behavior, geometric cache keys and deterministic reload reconstruction: kernels omitted.
- Actual Scribe rename mapping, old settings-file discovery and migration precedence: `LegacyName.cs` omitted.
- Hose job persistence, carrying, ports, flow, heat integration and settings effectiveness: hose sources omitted.
- Def inheritance, comp ordering, style graphics, assets, missing references and load compatibility: relevant XML/assets omitted. The supplied mesh-flag XML cannot establish these.
- Harmony target signatures, overload uniqueness, private field names and compatibility with the campaign’s other patches: game assemblies and patch inventory absent.
- Duplicate patching beyond the supplied constructors: no duplicate is demonstrated here; omitted constructors remain unaudited.
- Coverage or correctness of the offline validation script: script omitted.

**2. LIKELY FUTURE COMPLICATIONS**

- **Saved links need reconciliation, not just reference cleanup.** `CompAerialAnchor.cs:236` removes null partners but does not enforce reciprocal links, matching state/HP, uniqueness, same-map membership or valid enum values. Whether the omitted component repairs these is **UNVERIFIABLE**. Version migrations should reconcile each undirected link once before building power nets.

- **Ownership changes need a topology policy.** `CompAerialAnchor.cs:114` admits live partners without checking faction. Capturing or reassigning one linked anchor can preserve a connection that new-link validation would prohibit. Test ownership changes explicitly.

- **Ship transfers and reinstalling anchors can erase topology.** The supplied `PostDeSpawn` clears links and fallen cords for every despawn mode. Whether gravship movement invokes that path—and how the campaign’s ship-only seafloor transition transfers buildings—is **UNVERIFIABLE**. Removal, relocation and temporary transfer need distinct semantics.

- **Adding styles eventually breaks dynamic rendering.** `RM_MapComponent_CordGraph.cs:378` fixes motion storage at 16 materials; `:479` silently clamps the global count. Once content exceeds that count, static rendering can support indices that motion never visits. Size storage from `GlobalCount`.

- **Partial texture installations destabilize variant correspondence.** `CordMaterials.Build` packs only present strand textures into variant arrays, whereas `LegacyVariant` uses the complete colour/kind tables. Missing intermediate variants change index meaning and selection weights. Preserve canonical slots and substitute fallback art in place.

- **Shared graphics restoration can overwrite another mod’s edits.** `ConduitVisuals.Apply` restores objects captured at startup. Another mod changing the same def afterward can lose its modifications on the next settings application. Shared texture wrap-mode mutations have similar cross-mod consequences.

- **Thread-local scope is not general thread safety.** `TapRegistry` and material/style registries use unsynchronized dictionaries; `ThreadStatic bypass` protects only that counter. Parallel ticking or drawing would require main-thread confinement or redesign. Actual concurrent execution in this campaign is **UNVERIFIABLE**.

- **Tap events are an unstable extension contract.** `CompPowerTap.cs:178` invokes the multicast delegate inside one catch. One throwing subscriber prevents later subscribers from receiving that event. Victim attribution, save persistence and subscription lifecycle need definition before raids or goodwill depend on it.

- **Degree-constrained Kruskal is not a guaranteed minimum spanning solution.** `AerialMath.MinimumSpanningLinks` greedily accepts shortest edges with degree limits. It can strand a vertex despite an available spanning solution. Additional pole types with small `maxLinks` make that limitation more visible; the gizmo description should not promise universal joining.

**3. UNLEVERAGED OPPORTUNITIES**

- **Make invalidation an explicit, testable kernel.** The defects around `PiecesForSection`, roof eligibility and frame suppression can be tested with simple event sequences: build → edit again in the same frame → request section → advance frame. No rendering screenshot is needed to prove that a revision remains pending.

- **Add conservation tests around a fake power scheduler.** Exercise tap-before-net, net-before-tap, shutdown, despawn, multiple taps, depleted batteries and victim switching. Assert cumulative victim payment equals credited delivery plus explicitly pending energy. Testing only `TapStolenPerTick` cannot verify the ledger.

- **Test the rendering partition directly.** For every strand and zoom, assert that exactly one appropriate representation owns it. Include roof transitions, plant-preference transitions, shader fallback, viewport overlap with an offscreen midpoint, and vertex overflow.

- **Use saved XML fixtures for compatibility.** Fixtures should cover old namespaces, missing new fields, unresolved partners, asymmetric links, pending auto-links, legacy loop-budget keys and settings read/write failures. Verify both restored values and the next emitted save. The present fixture coverage is **UNVERIFIABLE**.

- **Turn probes into reliable evidence.** Add request IDs, map IDs, topology revisions and measurement frames. Report overflow and build failure explicitly. Make state reads observational: `ConduitStyleProbe.Styles` currently processes pending work and rebuilds before reporting, potentially repairing the defect being measured.

- **Improve settings dependencies and explanation.** Disable irrelevant controls while preserving their saved values; explain that the three master switches have different scopes. Show effective sway mode and fallback reason using the existing diagnostic machinery. Label defaults versus persisted per-building styles clearly.

- **Apply settings by impact.** Geometry changes need replanning; material changes need reprinting; effect-rate changes need neither. Avoid whole-map regeneration and conduit graphic replacement when values did not change.

**4. EXTENSIONS BEYOND THE MOD**

- **Reuse the routing model through separate adapters.** `CordWorldAdapter.Snapshot` already defines an input boundary suitable for hoses, pipes or other service networks. Reuse geometry and routing without making those systems inherit power connectivity or electrical live/dead semantics.

- **Centralize campaign rendering contracts.** Cord, hose and overhead layers need shared altitude, queue, culling and overflow rules. `DrawOrder.cs` is omitted, so its adequacy is **UNVERIFIABLE**; make these relationships executable contracts before adding more layered infrastructure.

- **Expose topology to campaign diagnostics.** A stable network/endpoint API could support broken-service alerts, construction overlays and offline scenario auditing. Avoid using runtime `PowerNet.GetHashCode()` as persistent identity.

- **Keep heat and travel semantics outside the visual graph.** Future electrical losses or heated hoses should feed the campaign’s existing “one kind of heat.” Cross-map infrastructure transfer must follow the ship/seafloor lifecycle rather than treating aerial links as travel or unrestricted remote connectivity. Neither integration is demonstrated in the supplied code.