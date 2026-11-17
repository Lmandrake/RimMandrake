# RIMMANDRAKE_TEACH_CONTRACT_CHECK_PICTURES_ARE_NOT_TEXT

## spec

`refusal_contract.check` reads every evidence ref as text (`_text_of`). An art judge's evidence is a picture: a PNG
opened as UTF-8 gives binary noise, so every well-made REDO that cites `north.png` is refused "observed quotes no token
of its evidence" (measured 2026-11-17 on the brief's own example against a real staged north.png). Under the brief's
re-ask rule a second such answer marks art_judge_brief FAILED: no art refusal could ever be well formed.

Fix: `_text_of` returns None for a binary evidence file (an image cannot be word-matched; its ref is still checked
against the given inputs). Text evidence keeps its word check. Found by RIMMANDRAKE_BUILD_ART_BRIEF_CALIBRATION_NOTHING_TO_RUN.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_art_calibration.py` (its two `contract:` checks: a refusal
citing a real PNG is well formed; one citing a text file with an unrelated `observed` is still refused). Watched failing on
the base (2026-11-17): the PNG check fails.

## criteria

- A refusal whose evidence is a picture the judge was given can be well formed.
- Text evidence keeps its observed-words check.

## refs

file: src/RimMandrake/rimflow/refusal_contract.py
file: src/RimMandrake/rimflow/selftest_art_calibration.py
