# PYRE_SCORCHFRUIT_DIAGNOSE_FIRE_BEARS_NOTHING

## cause — MOD (INFERRED, strong)
`Patch_FireTick_AshAndScorchFruit.rolledFires` was a **static** `HashSet<int>` of fire thingIDNumbers. Each ratchet piece
reloads the site fixture, and a reload re-issues the same thingIDNumbers in the same order, so the cohort's fires in
p3/p5 carried ids that earlier pieces' fires (p2 fire_tick_effects, 18 fruit) had already "rolled": every roll was
refused and 0 fruit grew. Same bug class as the burrow-nudge table MEASURED in 0afba7de51. Offline evidence: the patch
is armed and threw nothing (Player.0afba7de51.log), the pad on r3 is clean deep ash, unroofed, no animals
(r3 save read), and fire_tick_effects grew 18 fruit on the same site and build, so the mechanism works for fresh ids.
Not measured live: that the cohort's fire ids overlapped p2's.

## fix (68049f4519)
Roll set per Map via `ConditionalWeakTable` (`RM_FireEcoKernel.RollSetFor`): a reload builds new Maps, so it starts empty.
Fuzz (eco): re-issued ids roll again for a new owner; the old owner still refuses; a shared set (the pre-fix model) blocks
all. Site selftest: no static set in FireEcologyHook.cs.

## sibling (not fixed here)
`RM_JobGiver_BurrowOnFire.lastTimeout` is also a static `Dictionary<int,int>` keyed by thingID — same class.
