# Corpse eviction ghost cleanup — CORPSE_EVICTIONS_PRUNE_PATCHING_GHOSTS

- The eviction generator never emits a wildBiomes removal targeting a Corpse_ ThingDef, including when that name appears in a capture or cache, while retaining its existing roster, duplicate and live-race filters for real races.
- The shipped BiomeCastEvictions_WildBiomes.xml contains no Corpse_ operations, remains well-formed XML, and preserves every existing non-corpse operation in its original order without changing any roster or real-race eviction policy.
- Focused offline regression evidence demonstrates corpse rejection with positive real-race controls and continued shrink-guard refusal; the cleanup claims only offline artifact correctness, with no gameplay or deployment acceptance.
