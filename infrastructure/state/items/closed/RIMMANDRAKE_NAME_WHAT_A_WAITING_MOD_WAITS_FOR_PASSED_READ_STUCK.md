## spec

The status page of the Maturation Pipeline (`src/RimMandrake/Utils/maturation_now.py`) shows the orange word "waiting"
for every mod that is not held and has no live run. A mod that passed and rests (Gimme Some Slack 0.2.0,
Explosive Knockback 0.2.0) looks the same as a mod that is stuck. Fix: each badge of a mod with no live run names the
next step and who takes it. The reason comes from what the pipeline already records (`./pipe why`, the dispatch tick's
reason, the files of `design/concepts/<Mod>/version/next_version/`, `scope_answer` in VERSION.json). A passed mod that
rests uses a calm colour inside the warm brown palette; orange stays for a mod that waits for an act that somebody owes.
A reason that the page cannot read shows as "could not look" with the name of what could not be read.

## verify

Acceptance test: `python3 src/RimMandrake/Utils/selftest_maturation_now.py` (four new cases; case 1 fails on the base
commit) and the cases of commit `c8e4277a` still pass.

## criteria

- A passed mod with no scope proposal page: its badge says that the version passed and the mod rests, and that no scope page for the next version exists yet. It does not read the bare word "waiting".
- A passed mod with a scope proposal page and no `scope_answer` in VERSION.json: its badge says that the mod waits for the owner's answer, and names the page.
- A mod in a build stage with no live run: its badge names the next step, from the reason of the dispatch tick.
- A mod that the owner holds: its badge is unchanged.

## refs

file: src/RimMandrake/Utils/maturation_now.py
file: src/RimMandrake/Utils/selftest_maturation_now.py
