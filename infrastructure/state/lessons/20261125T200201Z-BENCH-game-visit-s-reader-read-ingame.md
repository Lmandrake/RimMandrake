An in-game visit's reader (read_ingame_exit) lacked the blind cycle's rule that a driver's exit_met false, written only for an owed fresh fix reader, reads as that reader once it lands sound; so FlowWorks visit 13 stayed not met after its reader landed, and a steward --steward-confirms could not move it. Fixed at 32df3b51c5; when a stage reader has a twin, check the twin carries the same rule.
item: RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_THIRTEEN_FAILURES_BACK
home: src/RimMandrake/rimflow/maturation.py
