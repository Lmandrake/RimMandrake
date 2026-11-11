# Independent design calls and implementation choices

Initial tools-disabled Opus design: preserve the existing door (engine has one edifice per cell; spawning a blocker would wipe it), delete approach/connectivity/root-access exceptions, and permit a real inside cutter to work from an owned trunk when its root is enclosed.

A second consultation used an incorrectly decoded TargetIndex brief. It is retained as invalid input, not adopted as independent evidence. Installed enum metadata proved None=0, A=1, B=2, C=3. A corrected fresh consultation (design3_prompt.txt, design3_raw.json, design3_call.json) supports retaining vanilla plant work and redirecting only approach/work-touch to unused C. Its remaining DestroyThing(B) input error is resolved by the retained engine IL: ldc.i4.1 = A.

Implementation retains vanilla JobDriver_PlantCut_Designated and the job's A plant target; only two exact validated iterator call sites route through wrappers. The same toil count/order is retained even for an invalid loaded C. Invalid ownership/settings/map/contact fail locally during approach/work; they do not abort the completion toils after PlantCollected. Giver returns no jobs when IL validation fails. Ordinary root-reachable cuts and all harvests remain vanilla.

The engine field-consumer metadata audit scans 90,840 methods. CutPlantDesignated is referenced only by WorkGiver_PlantsCut.JobOnThing and PostProcessedGerund. The first is called on the actual registered vanilla worker; the second is delegated with a temporary vanilla-description job. No work/yield/destruction body is copied. Contacts enumerate all claimants, not only the primary display owner.

The final fixture adapter PrepareCutter changes only the owned pawn's work tab and timetable, and creates no job. OrderCut was removed after BROADEN. The normal think tree must pick up the registered giver's job with playerForced=False. CutState is read-only. Actual execution is governed game ticks, including in-progress save/reload and exact work/target comparison. Effects/progress still face the root; no visual/feel claim.
