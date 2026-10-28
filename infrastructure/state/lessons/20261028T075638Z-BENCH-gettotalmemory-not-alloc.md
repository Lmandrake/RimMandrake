Under Mono Boehm, GC.GetTotalMemory(false) deltas around a tick are not that tick's allocation: map1 hose 'allocated 993 MB' in a DRY window yet 0/27 GCs landed in its ticks. Measure a component's share of the garbage as the number of collections landing inside its ticks (GC.CollectionCount(0) before/after).
home: design/validation_walks/RimMandrake/FlowWorks.md
