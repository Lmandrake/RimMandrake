# COPY_DAMAGED_FAUNA_REDRAW_OWNER_PROMPTS

## Decision (owner, question card 2026-10-24 06:29 PDT)
Question: what happens to a creature that stays bad after round 3 and that he leaves unpicked.
Picked: "Fresh honest rounds", and he typed: "1 + user improved prompts".

Our reading (FOUNDRY, not his words): the five creatures whose earlier rounds were damaged by foreign-image copies
(RM_Crustweevil, RM_Dustflutter, RM_Fuzzrunner, RM_Surrik, RM_Peeper) get 3 fresh rounds now that the copy guard
(codex_image.py CODEX_FOREIGN_COPY_GUARD_FIX_RESIZED) exists. Where he has written an improved prompt for a creature,
the redraw uses his text.

## Owner notes found (2026-10-24 06:35)
NONE. All four sheets (Transient/biome_ffar/owner_escalations_{cauldron,contagion,leaningscrub_1,leaningscrub_2}_sheet_2026-10-24.decisions.json)
are still `reviewStatus.state = prefill` with `by: null`; every row's `note` is empty and the serve logs show no
save. `python3 src/RimMandrake/Utils/art_eval/fauna_drive.py prompts RM_Crustweevil RM_Dustflutter RM_Fuzzrunner RM_Surrik RM_Peeper`
prints "no owner prompt" for all five. **Waiting on his prompt text**; round 1 of the fresh series was filed with
the pipeline's own prompt (below) so it is not idle meanwhile.

## Mechanism (src/RimMandrake/Utils/art_eval/round_series.py, fauna_drive.py, runner.py)
- Reset: `fauna_drive.py reset <DEF>... --source-run <run> --by-card "…"` appends one line per def to
  `infrastructure/state/art_eval/round_resets.jsonl` (no hand edit of regen_rounds.json or decision logs). Every
  counter then reads the new series: rounds = 1 + REGEN decisions after the reset, cap 3 (runner `rounds`,
  fauna_drive rows/candidates/install). Job ids carry the series so nothing collides with the old jobs:
  `arteval_<DEF>_s1r1_{south,east,north}`.
- Owner prompt: `rows` looks up `round_series.owner_prompts()` on every call: newest of
  `infrastructure/state/art_eval/owner_prompts.jsonl` (append with
  `fauna_drive.py owner-prompt <DEF> --text "<his words>" --owner-said "<his words>"`) and any non-empty `prompt` field
  on an `owner_escalations_*` sheet row (a free `note` is never read as a prompt: review 2026-10-24 found the real notes
  are complaints/instructions; record a note that is prompt text with `owner-prompt`). His text goes in VERBATIM as the description, between the template's
  own sentences:
  `A single RimWorld creature sprite of the <label>, painterly vanilla RimWorld style, realistic, clean dark outline,
  transparent background. <HIS TEXT> Same low, angled game camera and the same body size in every drawing. The edges
  fade cleanly into transparency with crisp dark outline pixels and no coloured fringe.`
  The facing is stamped per job by the artpipe daemon. His text is never sent through the facing-neutral rewrite;
  if it names a view the per-facing gate refuses, the row is HELD and printed (ask him), not reworded.
- Tests: `src/RimMandrake/Utils/art_eval/selftest_round_series.py` (12 checks) + selftest_art_eval.py, both PASS.
- Skill: rimworld-art-evaluation SKILL.md "Fresh rounds and owner prompts".

## Status / pending jobs (2026-10-24 07:20) — ALL FIVE SERIES STOPPED, nothing installed
- s1r1 (15 jobs): no foreign copy; runs fauna_s1_r1_00/_01 judged all five REGEN.
- s1r2 (15 jobs): no foreign copy against the WHOLE global codex cache (where the bollard / pipe-flange / belt-pack
  sheets came from; probe: Crustweevil_r2_north still flags at 0.69). Evidence:
  `D:\ClaudeWork\rimmandrake\fresh_rounds\nn_s1r2_full.txt`. Run fauna_s1_r2_00: Crustweevil REGEN, Dustflutter ACCEPT.
  Fuzzrunner/Surrik/Peeper s1r2 renders were never judged.
- STOPPED via `fauna_drive.py stop` (append-only stop lines in round_resets.jsonl; rows/candidates/install now refuse
  the def): Crustweevil and Dustflutter (he kept the in-game art), Fuzzrunner (he chose its art on the leaningscrub
  sheet), Surrik (he picked B earlier), Peeper (he kept A on the contagion sheet), all relayed by the coordinator.
  The Dustflutter s1r2 ACCEPT is NOT installed; its delegated verdict file is a record only.
- Pending jobs: none (artpipe pending/active hold no job for these five).
- Owed: code review of round_series.py / fauna_drive.py / runner.py hunk (not marked CLEAN in code_review_status).
- See FRESH_SERIES_STOP_FIX_AFTER_OWNER_KEEP: the stop is manual; an automatic refusal when a keep ruling postdates
  the reset is still to build.
