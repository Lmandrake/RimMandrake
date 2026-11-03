# FORGE_DHUVVOX_SWARM_REMAINDER_1 — dhuvvox clock remainder

Split from `FORGE_GPT_ENRICHMENT_1` §7.

## built in the parent

`RM_CompForgeCycleDormancy` gained `runClock`, set on the dhuvvox only:

- a click (`RM_DhuvvoxNoduleClick`) and sparks as each nodule opens;
- an inspect countdown to the end of the run (the flash window's end, or the cycle's rain-phase end);
- `RM_DhuvvoxRunSlowing` (Moving -0.4, TUNED) in the final quarter-hour;
- at the end, a dust puff, sparks and one "curling back" message per map.

The pawn is never removed. Sealed, it is drawn as its nodule, so none vanishes. Toggle: "The dhuvvox clock".

## open questions (owner)

1. The spec says "phase spawning from nodule **Things**" and "resealing conversion". Today a sealed dhuvvox IS
   its nodule (a dormant pawn with a nodule graphic). Converting to separate Things would mean despawning the pawn.
   Keep the pawn-as-nodule build, or convert?
2. "Swarm aggregation for performance": is there a measured performance problem? Nobody has counted dhuvvox on a
   Forge map.
3. "Their movement **and sound** slow": the dhuvvox has no running sound to slow. Add one?

## answered (2026-11-03, Relentless)
1. Kept the pawn-as-nodule build (question card 2026-10-08). Nothing converted.
2. Measured offline, not built. Vanilla `WildAnimalSpawner` arithmetic over the parsed roster gives 0.9 to 2.1 wild
   dhuvvox per map. The Rain's `EruptSwarm` adds 60. Peak on a 325x325 map, taking the residents as the expected count
   plus one more full group of 14: 76 awake, under a 100 budget. The SoundDef caps the scuttle at 6 voices.
   `src/RimMandrake/TheForge/selftest_dhuvvox_swarm_budget.py` turns red if a roster or weight change pushes the peak over the budget.
3. Built in 2b45ba7168: `RM_DhuvvoxScuttle` (vanilla `UI/TickHigh`) ticks while awake, and its gap stretches up to 4x in
   the final window (`RM_DormancyKernel.ScuttleDelay`, fuzzed by `selftest_theforge_fuzz.py`). Toggle "Scuttling sound".
