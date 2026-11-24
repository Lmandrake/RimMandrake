## spec
One fresh-context curation session on `skills/generating-rimworld-sprites/SKILL.md`. The evidence is §Conflicts (14 items) of
`design/specs/2026-11-19-plain-english-rule-docs/results/RIMMANDRAKE_REWRITE_SKILL_GENERATING_RIMWORLD_SPRITES.md`.
Five of them give an agent wrong guidance today:

- "Generate creature sprites at 256 px, not 512": `common.canvas_for_cells` and `ART_PAINTERLY_RESTORATION_1` (2026-09-14)
  size at drawSize × 128, floor 256, ceiling 1024. 256x256 is also under the legal minimum that the skill states.
- Outlines: `design/RimMandrake/art_judge_brief.md` B1a (no outlines, card 2026-10-04) against "thin or absent outlines turn to mud".
- "The legibility gate gates the job": the gate in `artpiped.py` is advisory and off by default.
- "passes 0/0 VACUOUSLY" and "can fail a render forever": `canon_check.py` is an advisor, and 0/0 reads UNGRADED.
- The 16.0 row of the size table (2048) against the 2026-09-02 ceiling ruling.

Decide each from the code and the newer ruling. Correct or delete the line. Do the same in `references/traps.md`.
Keep the `description`.

## verify
The effect check on this item. On `fed51daad6` it read `fails` (the old lines stand). It passes when the four old phrases are gone.
Also run `selftest_validate_skills.py` and `selftest_skills_by_work.py`.

## criteria
- Each of the 14 conflicts is corrected, or is kept with a reason in the session's report.
- The skill names no size, gate or canon verdict that the code does not have.
