# RIMMASTER_MOVE_IMAGE_SKILLS_OUT_PAST_CODE_PATHS

`generating-images` and `editing-images` are general (true with RimWorld removed) and belong in `~/dev/MandrakeWorkflows/skills/`,
but the 2026-11-07 spring clean left them in this repo: 32 tracked code files and 39 docs name `skills/generating-images/...` paths
(scripts under it are called by art tools such as `src/RimMandrake/FlowWorks/art_source/*/`), and the art pipeline is running
(owner: *"It's ok to keep the art pipeline going"*). MandrakeWorkflows' rule is that a skill moves with all its files.

**Done when** the scripts the project calls resolve through one indirection (a path read from config or `~/.claude/skills/generating-images`),
every code reference uses it, the two skills live in MandrakeWorkflows with project detail moved to `generating-rimworld-sprites`, the art
pipeline's selftests pass, and `~/dev/Lodestar/claude/skills.md` has their rows. Find the references with
`git grep -n "skills/generating-images\|skills/editing-images" -- '*.py' '*.sh' '*.json'`.

## Measured before moving (spring clean run 2, 2026-11-07)

Not moved: the scripts are project code, not a general skill yet, and a move today would break the running art pipeline.

- `skills/generating-images/scripts/codex_image.py` imports `rmpaths` from `parents[3]/src/RimMandrake/Utils` (the data root), carries
  artpipe sandbox, latch and guard-calibration logic, and names Windows home paths; `make_sprite.py` calls
  `skills/generating-rimworld-sprites/scripts/conform_sprite.py`. Outside this repo they do not run.
- `rm-artpiped.service` runs from `/home/mandrake/rm/bench` and computes `common.DEFAULT_WORKER_SCRIPT` (and the Gemini worker) once at
  import, so removing the folder breaks every job until that unit restarts. The unit is not a spring-clean helper's to restart.
- 56 tracked code files (artpipe, art tools, FlowWorks `art_source/*`, the sprite skill's scripts, three evidence scripts) and about 39
  docs name the folder. Editing them all makes each one DIRTY for code review.

So this is building work, in order: (1) one resolver in `src/RimMandrake/Utils/` that every caller uses; (2) split each script into a
general core with no project import (data root, Codex home and guard thresholds passed in or read from config) and a project wrapper that
adds them; (3) move the general cores and both SKILL.md files to MandrakeWorkflows, written to be public-safe, with project detail moved to
`generating-rimworld-sprites`; (4) leave forwards at the old paths until `rm-artpiped` has restarted on the new code; (5) the art pipeline's
selftests and one real job pass, then remove the forwards and add the `~/dev/Lodestar/claude/skills.md` rows.
