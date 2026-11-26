## spec
One standard for the savegame the owner opens at his first human look at a mod, after the system judges the mod ready.
It merges two things that are one idea (owner pick 12, 2026-11-12, OWNER.jsonl tsn 1794524114165680240):

- the "for the human" review map, `design/RimMandrake/northstar_human_review.md` (MessyConduit worked example,
  `src/RimMandrake/GimmeSomeSlack/human_review.py`, gallery plus free area, numbered labelled stations, key sheet);
- the matrix-scene principle (owner, 2026-11-12T18:43:50Z, Conductor log `D:\ClaudeWork\rimmandrake\conductor\log.md`):
  prepare one cell holding every fitting and facing with goods in it, then replicate it over the variables that matter
  (for example pit depth x water fill), with a grid key. Lesson
  `infrastructure/state/lessons/20261112T184403Z-CONDUCTOR-owner-looks-are-matrix-not-one.md`.

Owner's words: "this is the generalized version of the matrix scenes... combine. It's important for "first human look"
after the system thinks a mod is ready for the human to have a well prepared savegame like this that's dense and
informative and intuitive and well labeled".

### What to deliver
1. One rewrite of `northstar_human_review.md` into the standard. It covers stations plus matrix grids, label and key
   rules, density, how the save is kept and filed in the mod's `review/` folder, and the pre-look by a fresh judge
   (`design/RimMandrake/scene_look_judge_brief.md`) before he sees it. Delete what the merge replaces; fix inbound references.
2. One mod's first-look save built to the standard (FlowWorks pit or GSS, wherever a matrix already exists) as the
   worked example.

### Done when
The standard is a single doc with no rival copy, and one keeper save built to it has been pre-looked by a judge.
Its key sheet names every station and grid cell. Inventory row: `design/RimMandrake/validation_inventory_2026-11-12.md` (human review map).
