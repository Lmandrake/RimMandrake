# RIMMASTER_MOVE_IMAGE_SKILLS_OUT_PAST_CODE_PATHS

`generating-images` and `editing-images` are general (true with RimWorld removed) and belong in `~/dev/MandrakeWorkflows/skills/`,
but the 2026-11-07 spring clean left them in this repo: 32 tracked code files and 39 docs name `skills/generating-images/...` paths
(scripts under it are called by art tools such as `src/RimMandrake/FlowWorks/art_source/*/`), and the art pipeline is running
(owner: *"It's ok to keep the art pipeline going"*). MandrakeWorkflows' rule is that a skill moves with all its files.

**Done when** the scripts the project calls resolve through one indirection (a path read from config or `~/.claude/skills/generating-images`),
every code reference uses it, the two skills live in MandrakeWorkflows with project detail moved to `generating-rimworld-sprites`, the art
pipeline's selftests pass, and `~/dev/Lodestar/claude/skills.md` has their rows. Find the references with
`git grep -n "skills/generating-images\|skills/editing-images" -- '*.py' '*.sh' '*.json'`.
