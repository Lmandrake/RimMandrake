The Utinni scenario's file is Scenario_Utinni.xml but its defName is RUT_Jawa_UtinniStart (label 'the opened hull'); runbook 06 and plan 15 named the file as if it were the def, so jawa/scenario_select {scenario:'Scenario_Utinni'} could never match. Read the defName out of the def before writing it into a runbook tool call.
home: design/RimMandrake/world_remake_2026-10-19/15_conductor_plan.md
