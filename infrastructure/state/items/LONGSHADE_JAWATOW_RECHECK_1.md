NEW mechanism never observed: the Jawa return tow incident has never run in game.

Re-check of LONGSHADE_JAWATOW_LIVECHECK_1 (FAIL in sitting 2: RUT_JawaReturnTow was dead). Cause was a MayRequire naming mandrake.rm.longshade, a packageId that exists only folded into mandrake.rm.biomes; fixed cd03da899, and sitting 2 live-proved the def loads after the redeploy. Behaviour was never run.

## criteria
Same as LONGSHADE_JAWATOW_LIVECHECK_1: canFireNow true with a colonist in the hull and hostiles dead; firing spawns a Peaceful group; after towTicks the hull buildings are removed and "[RM LongShade] Jawa return: hull towed" logs; jawaReturnEnabled=false gives canFireNow=false.

## verify
Follow LONGSHADE_JAWATOW_LIVECHECK_1 `## verify` steps 1 to 3 on a generated RM_LongShade map. Do not redeploy-test with rsw.patches absent; the tier needs a RUT_Jawa_ faction, otherwise UNMEASURED.
