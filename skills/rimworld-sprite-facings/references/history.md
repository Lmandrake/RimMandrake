# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only replaced lines and their evidence. Git holds the rest.

## Vanilla facings

- Until 2026-11-23 the skill said: "Vanilla base-game art has NOT been checked: there is no RimWorld install on the Laptop
  and no `resources.assets`". It said that the check was owed from the Windows box. The check ran on 2026-11-23. The script
  read the extracted `ludeon.*` textures that `facing_scale_lint.py` uses, at alpha > 16, with the mirror-overlap formula
  of `art_checks.py`.
- The six lowest north scores: Squirrel 0.67, Cobra 0.72, HermitCrabC 0.74, HermitCrabA_Stationary 0.80 (under the floor before the rounding),
  StoneCrab 0.82, HermitCrabA 0.84. The six lowest south scores: Squirrel 0.66, Cobra 0.70, HermitCrabC 0.75, HermitCrabA
  0.78, HermitCrabA_Stationary 0.79, StoneCrab 0.82. 38 of 127 easts also reach 0.80.

## Generate to satisfy this

- The line "It also takes 3 renders per creature to 1" was false. A derived facing is an edit of the master, and each edit is
  one render.

## Duplicates

- The second trap list repeated the pairs of "No facing may BE another facing" and the complaint *"north and south aren't the
  right color"*. No such pair exists among the installed files of 2026-11-23.

## The export halo

- On 2026-11-23, of 17 south and
  east textures added since 2026-11-15, 3 had a halo that makes the height at `alpha > 0` more than 2% larger. The checks
  measure at `alpha > 16`, so no item was filed. `MYCOID_COLOSSUS_ART_MISROUTE_1` set the faint pixels to zero at install.

## Codex `edit` timing

- The skill once said: cap `--timeout` at **120 s** (a good call returns in ~80) and wrap every facing in a retry loop. The pointer to the history file named the 120 s cap too. The
  home, `generating-images` "Cost and timing", says 105 s and a retry at the caller's level, not inside a script.

- The skill once said both "pass the reference as image 1 and the approved facing as image 2" and "Two-image anchoring is not
  reliable here". The hangs were intermittent, with one image or two (`codex-edit-hang-history.md`).

## Pointers that were wrong

- The line "⚠️ **This file needs a curation pass**: "Multi-facing assets" appears three times" was stale. The heading appears once.
- "Full account and the CLAUDE.md correction: search this repo's CLAUDE.md" pointed at text that moved to
  `design/RimMandrake/standing_rulings.md` and `skills/rimworld-modding/references/flight.md`.
- "per the worked-example lie above": no worked example of this skill or its parent had such a lie.
- "the check's own docstring concedes it cannot catch this": the comment on `SYMMETRY_MIN_NS` says so. The docstring speaks
  only of a face in the north.
