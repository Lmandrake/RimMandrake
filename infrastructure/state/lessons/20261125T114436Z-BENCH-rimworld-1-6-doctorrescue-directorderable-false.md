In RimWorld 1.6, DoctorRescue is directOrderable=false, and the player's rescue (FloatMenuOptionProvider_RescuePawn) builds a plain Rescue job with no workGiverDef. A live test that must check an order through a work giver cannot use the rescue: use a directOrderable giver such as DoctorTendToHumanlikes. A humanlike is tended only in bed (WorkGiver_Tend.GoodLayingStatusForTend), so stage the rescue first. Measured on ArchBig 2026-11-25.
item: RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER
home: skills/rimworld-modding/references/project-engine-facts.md
