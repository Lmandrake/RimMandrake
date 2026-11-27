## spec

The status page of the Maturation Pipeline (`src/RimMandrake/Utils/maturation_now.py`) showed the badge "helper on it" for
a mod in the column "Passed" (ExplosiveKnockback 0.2.0), because a live run of the ticket lane carried
`RM_CONTROL_MOD=ExplosiveKnockback`. That run repaired a pipeline tool; its title only named the mod as the example of the
fault. Cause: `list_dispatch.mod_of` ties a ticket to a mod by a word of its id or title, and the lane put that word tie
into the run's launch env. Fix: the lane passes a mod to a run only when `mod_work` reads the ticket as that mod's work;
the page does not count a lane-launched run as work on a mod; the badge names what the live run does (its stage, or its
item) instead of "helper on it".

## verify

Acceptance test: `python3 src/RimMandrake/Utils/selftest_maturation_now.py` (four new cases; the first fails on the base
commit) and `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_list_dispatch.py`.

## criteria

- A mod in the column "Passed" with one live run on a pipeline-tool item: its badge does not read "helper on it", and the page lists the run with the pipeline repairs.
- A mod in a build stage with one live run of its own stage: its badge names the stage or the item of the run.
- A mod with no live run: its badge is unchanged.
- A mod that the owner holds, with a live run tied to it: its badge still reads held.

## refs

file: src/RimMandrake/Utils/maturation_now.py
file: src/RimMandrake/Utils/maturation_nonmod.py
file: src/RimMandrake/rimflow/list_dispatch.py
