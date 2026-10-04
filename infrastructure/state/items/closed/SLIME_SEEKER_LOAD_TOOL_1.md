# SLIME_SEEKER_LOAD_TOOL_1

## spec
The GelatinousSlime first script (item GELATINOUS_SLIME_FIRST_SCRIPT_1) marks seeker prime, extract, inject and the antidote race UNCOVERED because no bridge tool can load a seeker. Build `jawa/slime_seeker_load` in the JawaBench companion (pattern: `~/.claude/skills/rimbridge-companion`; declare every parameter; independent read after every write; ResultDescription), per `Transient/worker_notes_GELATINOUS_SLIME_FIRST_SCRIPT_1.md`, then add the covering components to the script.

## verify
Offline: lint_calls.py and selftest_tool_metadata pass. Live: the new components run in the GelatinousSlime driver run and fail with the mechanic switched off.

## criteria
Each of the four behaviours has a component that can fail, proven by switching the mechanic off.
