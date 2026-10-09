NEW mechanism never observed: the Return rite (RUT_Ritual_TheReturn) has never started in game.

Same cause and fix as NINEFAULTS_RITE_START_RECHECK_1: `<roles />` added to RUT_TheReturnBehavior (af95c91e6). Not run live.

## criteria
`jawa/ritual_start RUT_Ritual_TheReturn` at a RUT_DebtStone in full sun with water set nearby (RUT_DebtStoneWithWater filter) starts with no NullReferenceException; the pour outcome runs.

## verify
Tier needs mandrake.rm.biomes (Stillsand) + rut.patches + Ideology. get_defs the precept as a STRING, add it to the player ideo, build a RUT_DebtStone on open sand, set water within a few cells, call ritual_start. canStartAnytime is false (event-gated), so the tool may need to bypass the obligation; say so in the result. No Stillsand map is UNMEASURED.
