## spec
The first measurement report (D:\ClaudeWork\rimmandrake\conductor\cr\gss_live_end_measurement_report_20261118.txt, src/RimMandrake/rimflow/measurement_report.py gss-live-end) reads parity UNMEASURED on every one of the five live-end checks: the sweep (src/RimMandrake/GimmeSomeSlack/selftest_gss_live_end_sweep.py) runs the Python copy src/RimMandrake/Utils/mockups/messy_conduit/live_end_lay.py of Core/CordLiveEnd.cs, and no instrument compares the copy's numbers with the game's own [measured by grep 2026-11-18]. Two of its worst cases sit 0.001 from their limits (box 0.749 vs 0.75, machine 0.219 vs 0.22), so a small copy-vs-game drift could flip them unseen. Wanted: a parity reading (the same inputs through both, an agreement number, every disagreement named), which the report then prints.
Acceptance test: none, the instrument's shape (which inputs, which game call) is a design call for whoever owns Slack's Stage 6.

## refs
file: src/RimMandrake/rimflow/measurement_report.py

## criteria
- measurement_report.py gss-live-end prints a parity agreement for the live-end checks.

## verify
python3 src/RimMandrake/rimflow/measurement_report.py gss-live-end
