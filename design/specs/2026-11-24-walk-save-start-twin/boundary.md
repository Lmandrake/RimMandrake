# BOUNDARY: an aftermath station of a walk save has a START twin (walk_twins.py), Design Version 0.1.0

Code: `src/RimMandrake/Utils/walk_twins.py`, read by `save_keeper` (`src/RimMandrake/Utils/modcheck/reviewmap.py`) and by the
Stage 6 exit (`read_ingame_exit` in `src/RimMandrake/rimflow/maturation.py`). Tests: `src/RimMandrake/rimflow/selftest_walk_twins.py`.

The rule: `design/RimMandrake/standing_rulings.md` §Options he must LOOK at ship as a savegame (owner, 2026-11-23). The failure: he
could not judge stations 10 and 14 of `EK_VISIT4_WALK_20261123`, because its 16 stations showed the end of a blast and no start.

## ACCEPTS

- **a-station-sign.** A sign book of `reviewmap.sign_book`: the title `SIGN <key> <name>[ - DO: ...]`. The last word of the name may be
  the tag AFTER or START.
- **an-rws-file.** The books are read from the save itself, so a save with no sidecar file is read too.

## DOES NOT SURVIVE (not handled)

- **an-aftermath-nobody-tagged.** A station that shows an aftermath, has no AFTER tag and quotes no proof verdict is not seen. The walk
  brief's fresh reader looks for it (`roles/walk_brief.md`).
- **a-start-sign-over-a-bare-site.** The check reads signs. It does not read the scene round a sign.
- **a-save-with-labels-only.** A save that holds no sign book gives no station. The exit does not refuse it, and `check` exits 2.

## PROMISES (each one is owed a test of the same name)

- **an-aftermath-with-no-twin-is-refused.** Each such station is named, with the repair.
- **an-aftermath-with-its-twin-passes.**
- **a-finished-scene-is-an-aftermath-without-the-tag.** A sign that quotes a proof verdict and has no tag, as on the save of 2026-11-23.
- **a-station-he-acts-on-needs-no-twin.**
- **a-twin-of-another-station-does-not-count.** Nor does a START sign on the same cell.
- **the-save-itself-is-read.** The books in the save give what the sign ops gave.
- **save-keeper-refuses-before-the-save.** No file is written; the repair is in `refused`.
- **the-exit-refuses-it.** The Stage 6 exit is not met, and says why.
- **a-save-that-cannot-be-read-is-said.** It never reads as clean.
- **could-not-look-exits-two.** An absent save and a save with no station sign exit 2, never 0 or 1.
- **the-driver-brief-says-the-rule.**

## LIMITS

None.
