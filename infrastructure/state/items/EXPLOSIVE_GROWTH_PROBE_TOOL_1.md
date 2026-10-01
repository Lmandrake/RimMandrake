# EXPLOSIVE_GROWTH_PROBE_TOOL_1

## spec
The first ExplosiveGrowth north-star script (`src/RimMandrake/ExplosiveGrowth/validation.py`, item EXPLOSIVE_GROWTH_FIRST_SCRIPT_1) marks harvest jackpot, cut gamble, rupture mutation and the visual tell stages UNCOVERED because no bridge tool reads their state. Build the companion probe tool named in `Transient/worker_notes_EXPLOSIVE_GROWTH_FIRST_SCRIPT_1.md` (JawaBench, pattern in `~/.claude/skills/rimbridge-companion`; declare every parameter; independent read after every write; ResultDescription on the tool), then add the covering components to the script and remove the UNCOVERED marks.

## verify
Offline: lint_calls.py and selftest_tool_metadata pass. Live: the new components run in the ExplosiveGrowth driver run and fail when the mechanic is disabled in Mod Settings.

## criteria
Each of the four UNCOVERED behaviours has a component that can fail, proven by switching the mechanic off.
