# BOUNDARY: a docstring or a comment is not brief text, so its edit does not reset a judge's calibration

Code: `src/RimMandrake/rimflow/brief_text.py` (the bytes of a brief file that the calibration hash reads). Caller:
`refusal_contract.brief_hash`. Item `RIMMANDRAKE_RECALIBRATE_COVERAGE_JUDGE_A_DOCSTRING_RESET_IT`, written 2026-11-24.
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_brief_text.py`.

Why: commit 6cfd21b97c (2026-11-24) changed two docstring lines of `coverage_judge.py`. No model reads them. The coverage
judge's row read UNTESTED from then on, so its refusals bound nobody, and nothing said so.

## ACCEPTS (the only inputs this is built for)

- **a-brief-file.** A repo-relative path and its bytes. A `.py` file is read as Python source. Any other file is a
  prompt, a corpus or data, and every byte of it counts.

## DOES NOT SURVIVE (not promised)

- **a-docstring-read-from-another-file.** A prompt that takes `module.__doc__` of a brief file from another module, or
  that tells the judge to read the `.py` file itself. No brief on the registry does either (read 2026-11-24).
- **an-edit-of-live-code.** Any change to a code line resets the calibration, also when the model would not see it
  (a renamed variable, a moved blank inside a line).

## PROMISES (each one is owed a check of the same name)

- **a-docstring-edit-keeps-the-hash.** An added, edited or removed module, class or function docstring does not move it.
- **a-comment-or-blank-line-edit-keeps-the-hash.** The same for a comment and for a blank line between code lines.
- **a-prompt-string-edit-moves-the-hash.** An edit inside any other string moves the hash, also one that looks like a
  comment (`# ...`), a blank line in a triple-quoted string, or a blank line in a triple-quoted f-string.
- **a-code-edit-moves-the-hash.** An edit of a code line moves the hash.
- **a-docstring-the-program-reads-counts.** In a file that reads a `__doc__` anywhere but a `print(...)` or an
  argparse `description=`/`epilog=`, or that calls `getdoc`, `getsource` or `getsourcelines`, every byte counts.
- **a-file-that-does-not-parse-counts-whole.** Source that Python cannot parse counts byte for byte.
- **a-non-python-brief-counts-whole.** Every byte of a `.md` or `.json` file counts.
- **the-docstring-commit-of-2026-11-24-keeps-the-hash.** `coverage_judge.py` as it was before and after that commit's
  edit (its two docstring lines) hashes the same, and a one-word edit of its prompt does not.
- **an-edited-docstring-leaves-the-row-calibrated.** `refusal_contract.status` reads CALIBRATED after a docstring edit
  of a brief's `.py` file, and UNTESTED after a prompt edit.
