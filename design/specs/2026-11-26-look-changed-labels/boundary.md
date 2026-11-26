# BOUNDARY: a review save labels each cell changed since his last look (look_changed_labels.py), Design Version 0.1.0

Code: `src/RimMandrake/Utils/look_changed_labels.py`, called by the walk-save script that the Stage 6 brief asks for
(`ingame_brief_text` in `src/RimMandrake/rimflow/maturation.py`) and by the walk brief writer
(`src/RimMandrake/rimflow/roles/walk_brief.md`). Tests: `src/RimMandrake/Utils/selftest_look_changed_labels.py` (also run by `look_changed_labels.py --selftest`).

The rule: `design/RimMandrake/validation_map_and_rules.md` rule 2f. His card of 2026-11-12: "Who closes his objections → His
look, as a labelled cell in the next save". A fixed cell is labelled in the next save he opens anyway, so his re-look is
of the changed cells only.

## ACCEPTS

- **a-cell.** `{key, name, inputs: [repo paths, files or folders], params: any JSON}`. The key is unique in the save.
- **a-stage-record.** `version/stage_record.json` and `version/previous/*/stage_record.json`. His look is a move out of
  `his_walk` by OWNER, or with `owner_said` or `by_card` in `confirmed`.
- **a-cells-file.** `design/concepts/<Mod>/look_cells/<save>.json`, written by `record()` with its `staged_at`.

## DOES NOT SURVIVE (not handled)

- **an-input-left-out.** A file that the cell is made from but that the builder did not name does not move the hash.
- **a-save-he-did-not-open.** His last look is the newest cells file staged before his newest look. A save staged
  then and not opened is taken as the one he saw.
- **a-builder-that-skips-record.** With no cells file, the next save reads every cell new.

## PROMISES (each one is owed a test of the same name)

- **a-cell-whose-inputs-changed-gets-the-label.** "changed since your last look", at the front of the sign name, with
  an AFTER or START tag still last (`walk_twins.station` reads it); `show` lists it.
- **an-unchanged-cell-gets-no-label.**
- **a-cell-absent-from-the-last-look-is-new.** "new since your last look".
- **no-prior-look-labels-every-cell-new.** No cells file, or no move out of `his_walk` that is his. A record that cannot
  be read, or a cell input that is not there, is could not look (`why`, exit 2), never every cell new.
- **a-cell-removed-since-the-last-look-is-named-in-the-notes.** `notes`, and the lines of `show`.

## LIMITS

None.
