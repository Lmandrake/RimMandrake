NEW mechanism never observed: the Nine Faults rite (RUT_Ritual_NineFaults) has never started in game.

Sitting 3 found RitualBehaviorDefs without `<roles />` NRE in Dialog_BeginRitual.CreateRitualRoleAssignments; fixed af95c91e6 (RUT_NineFaultsBehavior). JoiningWater was proven live after the same fix (GELATINOUSSLIME_JOININGWATER_RECHECK_1); this one was not run.

## criteria
`jawa/ritual_start RUT_Ritual_NineFaults` on a player ideo holding the precept, with a fresh-found machine as target (RUT_FreshFind), returns started with participants and no NullReferenceException.

## verify
Tier needs mandrake.rm.ninefold + rut.rites + Ideology. Add the precept via ideo_precept_edit, get_defs PreceptDef/RUT_Ritual_NineFaults as a STRING (foundCount 1), place a freshly claimed machine, call ritual_start (it now returns the stack on failure). A throw or no eligible target is UNMEASURED/FAIL, not pass.
