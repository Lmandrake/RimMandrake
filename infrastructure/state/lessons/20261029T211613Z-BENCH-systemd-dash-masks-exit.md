A leading '-' on a systemd ExecStart (ExecStart=-/usr/bin/python3 ...) makes the unit report success whatever the step exits, so an UNMEASURED exit 2 goes unseen. Only use '-' for a step whose failure is truly harmless, and say why beside it (findings_fold in testq-tick.service, fixed 5ee3ccc7d8).
home: src/RimMandrake/Utils/testq/testq.py UNITS
