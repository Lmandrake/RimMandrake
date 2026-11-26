# RIMMANDRAKE_SWITCH_STEVEDESKTOP_PAST_A_RUN_THAT_ONLY_WAITS

## spec
The account plan runs on Archmagi. SteveDesktop is a following machine. The timed pass (`account-plan.timer`) sends
SteveDesktop a notice, and `machine_switch` switches SteveDesktop when its account is at its end. `machine_switch`
waits while any run is live on the machine, with no end to that wait.

The failure that happened, 2026-11-26:
- The account steven reached its 52% leave line. The notice of the account end is dated 3:13 AM PST. Archmagi went to
  the account lukas. SteveDesktop stayed on steven.
- One run was live on SteveDesktop (`rm-detached-bench-rimmandrake-kill-live-holder-resume-afte-1795681443`). From
  3:45 AM PST that run only waited, in one foreground command, for an event on Archmagi that never came.
- The account gate on SteveDesktop refused every new launch (`refused: ACCOUNT GATE (./acct can-use): the account
  steven is draining`). The Conductor log holds these lines from 2026-11-26T12:08:35Z. Five tickets of the Workshop
  Pipeline had 3 to 6 launches each that never started.
- At 7:10 AM PST the Conductor switched SteveDesktop to lukas by hand. That switch closed the waiting run.

The fix: a following machine whose account is at its end leaves that account without a hand. The pass ends a run that
does not end by itself a long time after the save order, in the way of `./pipe stop --write-now`, and then switches.
The stopped run spends no trial, and `left_open_continue.py` carries its work on.

A second lead, not measured at filing: `./acct can-use` on SteveDesktop over a plain ssh command printed "the live
runs are UNMEASURED (systemd could not be read), so they count as live". If the pass reads the runs the same way, it
never switches for a second reason.

The brief: `D:\ClaudeWork\rimmandrake\conductor\stevedesktop_switch_past_waiting_run_brief_20261126.md`.

## refs
file: src/RimMandrake/Utils/account_plan.py
file: src/RimMandrake/Utils/account_plan_machines.py
file: design/specs/2026-11-24-account-end/boundary.md

## verify
The selftest that tests `machine_switch` gets a case built from the records of 2026-11-26: a machine at its account
end with one run that never ends. The case is red on the code at filing (the switch waits for ever) and green on the
fix (the run is stopped after the wait, then the switch goes). Not yet seen red: the run that does the fix writes the
case first and keeps the red output.

## criteria
- A following machine at its account end, with a run that never ends, is switched by the pass without a hand.
- A run that ends in time is not stopped: the switch waits for it.
- When the runs of the machine could not be read, the pass does not switch, and its line says could not look.
- The wait before the stop names its danger and its measured need beside the number.
- The reading of the second lead is a note on this item.
