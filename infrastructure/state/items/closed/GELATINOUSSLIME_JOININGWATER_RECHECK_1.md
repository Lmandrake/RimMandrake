NEW mechanism never observed: the Joining Water ring and rite have never run in game.

Re-check of GELATINOUSSLIME_JOININGWATER_LIVECHECK_1 (FAIL in sitting 2: the rite defs were dead). Same folded-id MayRequire cause, fixed cd03da899; sitting 2 live-proved the defs load after redeploy. The ring and rite were not run.

## criteria
Same as GELATINOUSSLIME_JOININGWATER_LIVECHECK_1: one RM_SlimeHandRing on a generated Slime map, the rite targets it, a shared hediff yields RM_SharedBurden on other participants.

## verify
Follow GELATINOUSSLIME_JOININGWATER_LIVECHECK_1 `## verify` steps 1 to 3 (get_defs each as a STRING; list_things; run_genstep; ritual_start). No Slime map or precept adoptable is UNMEASURED.
