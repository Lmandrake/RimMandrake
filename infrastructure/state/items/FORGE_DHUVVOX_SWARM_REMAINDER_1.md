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
