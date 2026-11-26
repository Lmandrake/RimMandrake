# Boundary: the test lane obeys the host work switch; a harness repair re-runs only what held

Items: RIMMANDRAKE_VET_WORK_BOUND_FOR_STEVEDESKTOP_HE_SAW_FIREHAWK_AGAIN and
RIMMANDRAKE_ADMIT_LIVE_MOD_TESTS_STEVEDESKTOP_GAMES_SAT_IDLE (owner's card, 2026-11-25 11:02 PM PST, "Tests of live mods":
"(1) as well as pipeline updates/upgrades."). The code:

- `src/RimMandrake/Utils/testq/pipeline_admit.switch_refusal`, `live_mod`, `switch_text_for` and `steve_switched`
  (the test code is `src/RimMandrake/Utils/testq/selftest_testq_host_switch.py`);
- `testq.hold_refusal`, `testq.switch_applies` and `testq.fill_plan` (verdict `switched`);
- the `steward` state SWITCHED;
- `ingest.rerun_line` (only the chains that held).

## ACCEPTS

- **job.** A testq job with `mod`, `selector`, `requested_by` and `lane`.

## DOES NOT SURVIVE

- **selftest-queue.** A queue that is not the live one (a selftest's) is not held by the live switch. A test names its
  own switch file with `RM_HOST_SWITCH_FILE`.

## PROMISES

- **admission.** A test job of a mod that is not live, for the SteveDesktop lane or lane `any`, is refused while SteveDesktop
  is switched, and the refusal names its repair. These jobs pass: a `--proofs` job, an Ops job, a job on the Archmagi lane.
  An unreadable switch file refuses.
- **live-mod-admitted.** A live mod is in the Maturation Pipeline's advancing list, not on the owner's hold and not
  switched off (`./pipe show` reads it ON). While SteveDesktop is switched, a test job of a live mod is admitted, whatever
  its purpose and selection: a commission, a fix, a guard (a pipeline run's or the idle filler's) and a stage-6 checks job.
- **not-live-stays-refused.** While SteveDesktop is switched, a test job of a mod the owner holds, of a mod `./pipe show`
  reads OFF and of a mod that is not in the Maturation Pipeline is refused, the idle filler's guard job included. A
  Claude run that builds or fixes a mod is not this file's (`list_dispatch.switch_refuses` decides it).
- **unreadable-state-refused.** A mod whose state cannot be read (the hold list, the control store, the pipeline's
  advancing list) is refused, and the refusal says `could not look` with the cause. An advancing list that reads empty is
  could-not-look, never "not in the pipeline".
- **filler-live-mods.** While SteveDesktop is switched, the idle filler may pick guard jobs for a live mod and queues
  nothing for a mod that is not live. The steward reads SWITCHED only when every mod of the filler's list is refused.
- **filler.** While SteveDesktop is switched, the idle filler queues nothing for a mod that is not live, with or without
  `fill.stop`. The steward reads SWITCHED as settled, never a fault.
- **rerun-line.** A harness repair re-runs only the chains that held the fault. When no chain is known to have held,
  the repair re-runs the whole selection.
