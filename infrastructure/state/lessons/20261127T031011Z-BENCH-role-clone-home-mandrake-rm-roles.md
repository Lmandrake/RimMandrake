A role clone (/home/mandrake/rm/roles/<Role>) moves only when a unit of that role starts (its first step is ./sync), so a concept admitted after the role's last run is absent there: run-now refused WreckedMachines 'no stage.json' with the clone 5 days behind origin. run-now --apply now syncs the role clone first (ab5b15ee3c). Before you trust a 'missing' read from a role clone, compare it with origin/main.
item: RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO
home: skills/using-rimflow/references/traps.md
