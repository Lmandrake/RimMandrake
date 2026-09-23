# SKILL_SIZE_SPLIT_PASS_1 — split two oversized SKILL.md files into references/

The 2026-09-23 lessons drain (308 + 18 entries folded across ~20 skills) left two skills
well past `skill-creator`'s 500-line guideline for a SKILL.md:

- `skills/rimworld-modding/SKILL.md` — 659 lines (was 512 before the drain)
- `skills/generating-rimworld-sprites/SKILL.md` — 887 lines (was 759)

## what to do

Move the detailed trap catalogues into `references/<topic>.md` next to each skill (the
`rimworld-modding` skill already has five such files — extend those rather than creating
parallel ones) and leave one-line pointers in SKILL.md. The `description:` frontmatter is
NOT to be touched — the owner ruled 2026-09-23 that descriptions stay as they are this
pass, because the description is the trigger and a hand-trim can silently un-fire a skill.

Cut nothing: every folded rule survives, only its file changes. Verify with `wc -l` after
and by re-reading each moved block once in its new home.
