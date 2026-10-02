# MessyConduit full-file review 2026-10-02

Fixed (files now DIRTY, for FOUNDRY): Core/CordGraph.cs, Core/CordBuilder.cs, RM_MapComponent_CordGraph.cs, SectionLayer_RM_MessyCords.cs (+ rebuilt Assemblies DLL/.srchash).
1. HIGH RM_MapComponent_CordGraph.Sig compared piece Key only; a re-laid piece (corridor walkability changed) keeps its Key, so a cord owned by a section far from the edit was never re-meshed and drew through the new wall. Sig now includes GeometryHash.
2. HIGH SectionLayer: no vertex cap; Unity 16-bit index mesh breaks past 65535 verts (dense base, tangles). Ribbon/Quad now drop past 65000.
3. MED CordGraph: machine reached only via MachineLinks had no MachineOf entry -> KeyNotFound in Classify (adapter never sets MachineLinks, so test scenes only).
4. MED Rebuild had no try/catch: a build exception repeated every section regen. Now logs once, draws no cords.
5. LOW CordBuilder parallel-edge count was O(E^2) string compares; precomputed. GeometryHash negative double->ulong cast made defined.
Unfixed notes: CordGraph.Deg is O(E) and PruneSpurs restarts per prune (O(S*E^2), only noticeable on thousands of edges); each Rebuild snapshots the whole map per frame that any section regenerates; ExtraCost (trees) not in corridor hash; Fingerprint omits SlackLo/Hi (constants). Harmony prefix signature verified vs 1.6 PrintWirePieceConnecting(layer,A,B,forPowerOverlay). Master switch: texture swap restored via originals map + Notify_ColorChanged, layer Visible gated, hookup prefix gated: OK.
Build 0 errors; selftest 102/102.
