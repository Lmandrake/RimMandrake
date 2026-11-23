## spec
Filed 2026-11-23 about 2:45 AM PST by the run on `RIMMANDRAKE_BUILD_LIST_LANE_ON_RED_DISPATCH_GOALS_FIRST` (live proof 1 of
the List Pipeline's Work stage). A real debt: his ruling of Sun 2026-11-22 about 5:57 PM PST, by card, is not in
`infrastructure/state/CONDUCTOR_GOALS.md`, and that file is the Producer's only input
(`src/RimMandrake/rimflow/roles/producer.md`).

His words (ledger, `--owner-said` on `RIMMANDRAKE_DEBATE_CLEAN_HOUSE_ADVICE_WITH_GPT_ONE_AGENT_PER_VIEWPOINT`, read them
whole with `rimflow show`): "One week focusing on mods. At the end of the week, we study what we know. If there are some
trials we KNOW will inform that decision, do t..." The note beside it: ONE week on mods (to 2026-11-29), then study
what we know; a trial runs now only if we KNOW it will inform that decision; otherwise trials wait. This replaces the
plan's two-week window to 12-06.

Do: add a new block on top of `infrastructure/state/CONDUCTOR_GOALS.md` in the file's own form (a dated heading, his
words cited from the ledger, the goals in his order). State the week's end as the date 2026-11-29. Do not delete or
reorder older blocks beyond what the new block replaces in his words; a block he replaced is deleted, as the file's
header says (git holds the history).

What would pass the check and leave the need unmet: the date 2026-11-29 written anywhere in the file without the
ruling. The run writes the ruling.

## criteria
- `infrastructure/state/CONDUCTOR_GOALS.md` holds a block for his ruling of 2026-11-22 with the week's end 2026-11-29.

## verify
python3 src/RimMandrake/rimflow/list_effect.py check 'path-has:infrastructure/state/CONDUCTOR_GOALS.md::2026-11-29'   # holds
