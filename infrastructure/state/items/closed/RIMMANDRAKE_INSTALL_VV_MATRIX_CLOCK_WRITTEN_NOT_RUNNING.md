# RIMMANDRAKE_INSTALL_VV_MATRIX_CLOCK_WRITTEN_NOT_RUNNING

## spec
Child of `RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS`, an OPERATIONAL item. The clock is written and was not installed (the lane enabled no unit):
`src/RimMandrake/Utils/systemd/rm-vv-matrix.{service,timer}` run `vv_matrix_clock.py` nightly at 02:40 local from the ops
deploy (/home/mandrake/rm/dispatch), with `--prove` on Sundays, and write one reading after the run:
`D:\ClaudeWork\rimmandrake\vv_matrix\last.json`. Install:
  cp src/RimMandrake/Utils/systemd/rm-vv-matrix.{service,timer} ~/.config/systemd/user/
  systemctl --user daemon-reload && systemctl --user enable --now rm-vv-matrix.timer
and add `"rm-vv-matrix": "rm-vv-matrix.timer"` to `src/RimMandrake/Utils/systemd/ops_clocks.json` "clocks". The full
matrix needs Windows dotnet.exe and D: free space; a first manual run (`python3 src/RimMandrake/Utils/vv_matrix_clock.py
--prove`) measures its wall before the timer is trusted.

## criteria
- Closed only running: `rimflow close <ID> --sha <sha> --live "unit=rm-vv-matrix.timer reading=<last.json> max_age=30h"`.
- Acceptance test: none offline, a live operational clock (its reading is the test).

## verify
- last.json fresh, matrix_verdict PASS (a red is a law broken at the shipped settings: read matrix_why).

## refs
file: src/RimMandrake/Utils/vv_matrix_clock.py
file: src/RimMandrake/Utils/systemd/rm-vv-matrix.service
