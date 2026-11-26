# BOUNDARY: the notes of his next look list every pinned pass that a fix moved, Design Version 0.1.0

Code: `src/RimMandrake/Utils/look_notes.py` (`notes`, `render`, `pin`, `read_pins`, `save_why`), called by
`src/RimMandrake/rimflow/maturation.py` (`walk_brief_pins_why`, inside `read_walk_brief`, the `walk_brief` clause of
the move to `his_walk`) and by the walk brief writer (`src/RimMandrake/rimflow/roles/walk_brief.md`). Item:
`RIMMANDRAKE_LIST_MOVED_PINS_IN_LOOK_NOTES`. Rule: 2e of `design/RimMandrake/validation_map_and_rules.md` (his card,
2026-11-12: "A fix that changes something he passed → Allow it, list what moved"). Each promise has a test of its name
in `src/RimMandrake/Utils/selftest_look_notes.py`.

## ACCEPTS (the only inputs this is built for)

- **one-pins-file-per-mod.** `design/concepts/<Mod>/version/pins.json`, `{"pins": [{"id", "said", "cell", "value",
  "read": {"path", "regex"}}]}`. `read.path` is repo-relative; `read.regex` has one group, the value.
- **values-compare-as-numbers-or-text.** Two values that both parse as numbers compare as numbers (`0.49` = `0.490`);
  else they compare as stripped text.

## DOES NOT SURVIVE (not promised)

- **a-value-the-regex-cannot-reach.** A pass whose value no one regex can read from one file (a curve, a picture) is
  pinned with no reader, and so reads UNMEASURED on every look until a reader is written.
- **a-moved-line-the-regex-still-matches-elsewhere.** If the pinned line is deleted and another line matches the same
  regex, the other line's value is read.
- **the-save-file-itself.** "In the save" is read from the save's cells file (`look_cells/<save>.json`, written by
  `look_changed_labels.record`), not from the `.rws` savegame. A builder that records a cell it did not stage is not seen.
- **unpinned-passes.** A pass that nobody pinned is not seen. `pin` is run when his pass is recorded.

## PROMISES (each one is owed a test of the same name)

- **an-unchanged-pin-is-not-listed.** A pin whose reader finds its stored value is not in the notes.
- **a-moved-pin-is-listed-old-beside-new.** A pin whose value moved is listed with its id, its cell, and `old -> new`.
- **a-pin-whose-line-is-deleted-is-listed-gone.** A pin whose file or line is gone is listed `old -> gone`.
- **an-empty-pin-set-says-so.** An empty pin list, or no pins file, lists nothing and says "nothing to list".
- **a-pin-with-no-value-is-unmeasured.** A pin with no stored value, or no working reader, is listed UNMEASURED with its
  cause, never dropped.
- **an-unreadable-pins-file-is-could-not-look.** A pins file that cannot be read or parsed prints COULD NOT LOOK and
  exits 2; it is never read as an empty set.
- **the-walk-brief-names-each-listed-pin.** `walk_brief_pins_why` refuses a walk brief that does not name each listed
  pin by its whole id, names only the missing ones, and names an unreadable pins file.
- **each-listed-cell-is-in-the-save.** `save_why` (and so the walk_brief gate) refuses a listed pin whose cell is not a
  key of the save's cells file (the one named, else the newest), names a missing cells file, and asks nothing when
  nothing is listed.
- **pin-records-the-value-now-and-refuses-a-reader-that-finds-nothing.** `pin` stores the value its reader finds now (or
  the value given), replaces an entry of the same id, and refuses a reader that finds nothing.
