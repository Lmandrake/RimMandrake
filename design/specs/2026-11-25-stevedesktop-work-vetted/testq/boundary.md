# Boundary: the test lane obeys the host work switch; a harness repair re-runs only what held

Item: RIMMANDRAKE_VET_WORK_BOUND_FOR_STEVEDESKTOP_HE_SAW_FIREHAWK_AGAIN. The code:

- `src/RimMandrake/Utils/testq/pipeline_admit.switch_refusal` and `steve_switched`;
- `testq.hold_refusal`, `testq.switch_applies` and `testq.fill_plan` (verdict `switched`);
- the `steward` state SWITCHED;
- `ingest.rerun_line` (only the chains that held).

## ACCEPTS

- **job.** A testq job with `mod`, `selector`, `requested_by` and `lane`.

## DOES NOT SURVIVE

- **selftest-queue.** A queue that is not the live one (a selftest's) is not held by the live switch. A test names its
  own switch file with `RM_HOST_SWITCH_FILE`.

## PROMISES

- **admission.** A mod job for the SteveDesktop lane, or for lane `any`, is refused while SteveDesktop is switched, and
  the refusal names its repair. These jobs pass: a `--proofs` job, an Ops job, a job on the Archmagi lane. An
  unreadable switch file refuses.
- **filler.** While SteveDesktop is switched, the idle filler queues nothing, with or without `fill.stop`. The steward
  reads SWITCHED as settled, never a fault.
- **rerun-line.** A harness repair re-runs only the chains that held the fault. When no chain is known to have held,
  the repair re-runs the whole selection.
