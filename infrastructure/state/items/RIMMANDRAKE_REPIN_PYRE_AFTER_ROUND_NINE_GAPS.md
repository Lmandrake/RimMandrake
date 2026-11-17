# RIMMANDRAKE_REPIN_PYRE_AFTER_ROUND_NINE_GAPS

## spec
Pyrelands 0.1.0 is locked (`design/concepts/Pyrelands/version/VERSION.json`). Judging stopped 2026-11-17T18:05:37Z
(round-8 look not_covered). Option A was taken as a delegated Evidence-for-Ask call (CONDUCTOR:<tsn>, named in the
grant on stage.json): both Problems and the three text leftovers are fixed in 0.1.0. The three are
RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE_FLOOD_ALSO_MOVES, RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED and
RIMMANDRAKE_CORRECT_PYRE_STALE_TEXT_THREE_ADVISORY_LEFTOVERS. The grant (`coverage_judge.py release ... --after`)
waits on them AND on a re-pin. This item is the re-pin, last in the after-list, so its fixer run comes after theirs.

Do, once the three have landed their commits (if one is still open, note which and stop: no partial re-pin):
1. The stop commit is `git log -1 --format=%h -S'18:05:37Z' -- design/concepts/Pyrelands/stage.json`. Then
   `git log --format='%h %s' <stop commit>..origin/main -- design/concepts/Pyrelands/` lists every commit since the
   stop that moved a stage input (record.json, sheet.md, tree.json, scenes.json, floor.json, exam.json).
2. Each commit must be tied to the card of his that it carries out. It cites the OWNER tsn in its message, or a
   ledger event on the card's item names the sha (`designer_stage.change_tied`). The cards:
   - OWNER:1794926130118775229 (2026-11-17, "Fire bars -> Just 'The fire walks with the wind.'"): the wind bearing
     and the record.json decision the text leftovers name.
   - OWNER:1794894282613045211 / OWNER:1794894288587863659 (2026-11-16 burn-line words): the burned-share flood read.
   The sources of the 2026-11-17T17:09:38Z locked_change in stage.json are the model.
3. `python3 src/RimMandrake/rimflow/designer_stage.py repin design/concepts/Pyrelands --source OWNER:<tsn>@<sha> ...
   --why "round-9 gaps fixed in 0.1.0 (CONDUCTOR:<tsn>, option A); re-pin for the one final look"`. Commit stage.json.
4. If repin refuses because a commit carries out no card of his, that is a finding. File it and name it here. Do not
   cite a Conductor event as his word.

## verify
`python3 src/RimMandrake/rimflow/coverage_judge.py status design/concepts/Pyrelands` no longer lists the re-pin among
the grant's waits, and stage.json history holds a `locked_change` after 2026-11-17T18:05:37Z.

## criteria
- a locked_change after the round-8 stop, citing only OWNER events of his
