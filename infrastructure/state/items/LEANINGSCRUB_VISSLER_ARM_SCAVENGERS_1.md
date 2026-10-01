# LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 — shed vissler arms draw real scavengers

From `LEANINGSCRUB_GPT_ENRICHMENT_1` part 2: "visslers shed twitching harvestable arms
(`RM_VisslerArm`) that draw real scavengers." The shedding is built: a runway bloom makes half the
wild visslers in reach drop one `RM_VisslerArm` and flee
(`src/RimMandrake/LeaningScrub/Source/RM_RunwayBloom.cs`, `RM_RunwayBloomExtension` on `RM_Vissler`).
The arm is still a plain `ResourceBase` trade good. It is not food, so nothing comes for it.

## open questions

1. **Which species scavenge it?** Rollbug (its def comment names "carrion-ball rolling"), the
   predators (shokka, surrik, fuzzviper, ribbonwhip), or a set to be named?
2. **Mechanism:** make the arm ingestible (a food item, so vanilla hunger AI finds it), or a lure job
   that pulls scavengers to an arm in range whatever their hunger? The second also covers the
   "hunter's lure" use the item comment mentions.
3. Does an arm decay (rot) if no one takes it?

## criteria

- An arm on the ground visibly draws the ruled scavengers. Proven by a state read of their jobs,
  never by a screenshot hunt.
