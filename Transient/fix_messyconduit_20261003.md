# MessyConduit fixes 2026-10-03 (plan)
1. Hoses.EnsureLay: cache failed lay (guard on layKey only); 250-tick check clears layKey for failed lays too; DropMeshes destroys cached meshes on re-lay/Deregister.
2. Patch_Section_TryUpdate_MarkStale: per-section seen-bits; stale only on newly set bits.
3. SectionLayer relevantChangeTypes + Roofs (also in patch mask).
4. CordBuilder cache key: append endpoint NodeType.
