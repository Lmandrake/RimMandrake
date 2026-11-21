# RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Pipeline defect.

## spec

`design/concepts/Pyrelands/version/test_table.json` gives 42 live checks the command
`python.exe src\RimMandrake\Pyrelands\validation.py --live <chain>`. That command dies at import:
`ModuleNotFoundError: No module named 'modcheck'` (validation.py line 59, measured 2026-11-20 7:25 PM PST). validation.py
has no `__main__` and no `--live` switch: it is a modcheck suite. The command that runs a chain is
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains <chain>`
(visits 1 and 2 both ran it).

Run as judge_certificate.red_seen runs it (`shell=True` in WSL, repo root), every one of the 46 live commands dies
before its test (measured 2026-11-20 by the script below): `/bin/sh` eats the backslashes of the Windows-style path
(`python.exe: can't open file ...srcRimMandrakePyrelands...`), and the `(minimal list + ...)` annotation inside the
command is a shell syntax error (`Syntax error: "(" unexpected`, rc 2). That includes the two real scripts
(P_firefoam_aim, P_gate).

Two harms:
1. A Stage 6 driver, Lightspeed or testq that runs the table's command gets rc 1 and no rows.
2. `maturation.py red-seen Pyrelands <live test> --patch <fault>` (judge_certificate.red_seen) runs the table's command
   and records a red run when rc != 0. A crash at import is rc 1, so ANY planted fault "goes red". The red-seen proof is
   void for every live decider of this table.

Fix: the table maker writes the driver command for each validation.py chain. And red_seen refuses to record a red run
whose last line is an import or start-up error (it proves nothing about the fault).

## verify

Run each table command once with no fault. It must start and reach the bridge, or exit 2 with "bridge" in the reason.

## criteria

- Every live command in the table starts (no ModuleNotFoundError).
- red_seen does not record a run that died before it ran the test.

## Acceptance test

`python3 design/concepts/Pyrelands/version/in_game/visit_2/scripts/table_commands_start.py` runs every live command as
red_seen does and exits 1 when any never starts. Red now: "46 live command(s) never start", exit 1 (seen 2026-11-20 on
396d73530c). Green: exit 0 ("0 live command(s) never start"). It needs no game: a command that reaches the bridge and is
refused there has started.

## refs

file: design/concepts/Pyrelands/version/test_table.json
file: src/RimMandrake/rimflow/judge_certificate.py
file: src/RimMandrake/Pyrelands/validation.py
