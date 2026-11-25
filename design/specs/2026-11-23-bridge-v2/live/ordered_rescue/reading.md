# Live reading: prove_ordered_rescue.py (RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER)

RESULT PASS: 5 of 5 rows on ArchBig, 2026-11-25 03:33 PST, on the companion built from the giver fix
(`prove_fixed_2026-11-25.txt`). The command:

    python3 src/RimMandrake/rimflow/game_lock.py run ArchBig --for "ordered rescue proof" -- \
        python.exe <clone>\src\RimMandrake\bridgetools\prove_ordered_rescue.py --host ArchBig

The game was a TEST-profile quicktest map on ArchBig's small list. The run downs one colonist, builds one bed, has a second
colonist rescue the first to the bed (the scene, R0), and spawns and removes one hostile.

## The rows

| row | claim | fixed build | base 577381c7e5 | always-raw plant |
|---|---|---|---|---|
| R1 | a doctor ordered through `DoctorTendToHumanlikes` tends the victim in bed: the job ends Succeeded | PASS | PASS | PASS on the old R1 check (see below) |
| R2 | a doctor not assigned to Doctor: given false, the float menu's reason ("Not assigned to doctoring"), no tick | PASS | PASS | PASS |
| R3 | `jawa/motive` on a hostile with no lord: refused `NO_LORD` | PASS | PASS | PASS |
| R4 | the job tap's giver agrees with the receipt: `WorkGiverDef:DoctorTendToHumanlikes` for the tend, `JobGiver_WanderColony` for the node, no giver for a raw Goto; the force record reads 3, 3, 4 | PASS | **FAIL**: the tap named `ThinkNode_QueuedJob` | **FAIL**: the tap named `ThinkNode_QueuedJob` for a Goto that the receipt called the work giver's |
| R5 | a giver made to refuse (a target that is not in bed): given false, nothing started, no tick | PASS | PASS | PASS |

## What the live game taught

- **The base build's job tap named the queue, not the work giver.** A float-menu order reaches `StartJob` from the job queue:
  `TryTakeOrderedJob` enqueues the job and `ThinkNode_QueuedJob` starts it (RimSage, `Pawn_JobTracker.TryTakeOrderedJob`).
  `Giver()` in `JawaBenchCast.cs` named the node first, so the `WorkGiverDef:<defName>` branch never ran for a player order.
  The fix names the work giver when the node is the queue's. Seen red: `prove_base_577381c7_2026-11-25.txt` (R4).
- **The wrong code that GPT named goes red live.** `plant_always_raw.patch` makes `StartGiven` start a raw Goto and leaves the
  receipt as the giver's. R4 reads the tap's `ThinkNode_QueuedJob` against the receipt's `WorkGiverDef:DoctorTendToHumanlikes`
  and fails: `prove_plant_always_raw_2026-11-25.txt`. That run also passed R1, because R1 then checked only that the reply's
  job ended Succeeded, and the plant's Goto did. R1 now also requires the job to be a `TendPatient`. That change touches no
  check that R4 reads, so the R4 reading of the plant stands.
- **A rescue is no work order** (an assumption of the item's note was false). `DoctorRescue` is `directOrderable` false in 1.6:
  `jawa/order giver=DoctorRescue` replied "the giver is not directOrderable". The player's rescue
  (`FloatMenuOptionProvider_RescuePawn`) builds a plain `Rescue` job with no work giver on it, so the tap cannot tell that job
  from a raw one. The scene stages the rescue (`jawa/ordered_job Rescue`) and the row orders a tend, because a humanlike is
  tended only in bed (`WorkGiver_Tend.GoodLayingStatusForTend`).
- **Scene faults on the way, all repaired in the sitting:** a doctor who "will never do doctoring" (the doctor is now the
  first colonist that `set_work_priority` lets do Doctor work); a tend by an unskilled doctor outlasts 1500 ticks (the run is
  now 5000); a guessed Goto cell ended the raw job at once (the cell is now a standing colonist's, 3 or more cells off).
- **Two launches on ArchSmall were lost** to a WSL interop timeout (`UtilAcceptVsock: accept4 failed 110`), a known trap
  (`skills/rimworld-deploy/references/traps.md`). They are no reading of the work.
