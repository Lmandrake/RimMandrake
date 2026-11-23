Deleting an ops_watch collector family also needs its name in REMOVED_FAMILIES in BOTH Utils/ops_watch.py and rimflow/incident.py: without it an OPEN alarm of the family stays in alarms.json for good and its incident never closes (PLAN_DISTRESS, 2026-11-23). The live incident closes 60 min after it first reads sane.
item: RIMMANDRAKE_REMOVE_RETIRED_V3_ROLES_FROM_ACTIVE_RULES_STILL_LISTED
home: rimflow-operations
