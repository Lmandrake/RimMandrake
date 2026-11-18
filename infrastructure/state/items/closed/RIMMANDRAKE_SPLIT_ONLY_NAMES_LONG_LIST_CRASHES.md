## spec

`run_selftests.py:268` `_only_names()` decides whether an `--only` entry is a real file *before* splitting it on
commas:

```python
return [n for e in entries for n in ([e] if Path(e).is_file() else e.split(",")) if n]
```

With a long comma list, `Path(e).is_file()` on the WHOLE string raises instead of answering, and the raise escapes:
`OSError: [Errno 63] File name too long`. Reproduced here 2026-11-17 with 40 names (949 chars); the builder who hit
it worked around it by splitting the run in two, which is the hand workaround the pipeline rule forbids leaving
behind.

**This is the owner's 2026-11-17 four-answers rule, variant "two causes share one code".** `is_file()` has three
outcomes a caller needs apart: it IS a file, it is NOT a file, and *the question could not be asked* (ENAMETOOLONG,
ELOOP, EACCES on a parent). The code treats only the first two as possible, so the third kills the run — and would
be just as wrong if it were swallowed into "not a file", because then a real file whose name is merely unreadable
would be silently split on commas into nonsense test names and refused by the wrong message.

**The fix.** Decide the file-or-list question in a way that cannot raise: a comma is not legal in any test path we
have, so split first, or guard the `is_file()` with `try/except OSError` and treat a raise as "could not look" —
naming the entry and the errno, never as "not a file". An entry that really is an unreadable path must refuse by
name, not by crash.

## refs

file: src/RimMandrake/Utils/run_selftests.py
file: src/RimMandrake/Utils/selftest_run_selftests.py

## verify

python3 src/RimMandrake/Utils/run_selftests.py --only selftest_run_selftests

## criteria

- A1: `--only` with a comma list of any length resolves to the same test set as the same names split across
  several `--only` flags, and never raises.
- A2: an entry that IS a real file still stays whole (today's behaviour, not regressed).
- A3: an entry that is a path the filesystem cannot answer for is refused by name with its cause, distinct from
  both "not a file" and "no such test".

## acceptance

Acceptance test: new cases in `selftest_run_selftests.py` passing (a) a 40-name comma list, asserting the resolved
names equal the same names given as separate flags, and (b) an entry that raises OSError from `is_file()` (a path
over NAME_MAX, built in a tmpdir), asserting a named refusal rather than a traceback or a silent comma-split.
Watched FAILING on the base commit — today (a) raises `OSError: [Errno 63]`, which the case must show before the
fix. Reproduction one-liner for the base reading:
`python3 -c "from pathlib import Path; Path(','.join('selftest_x_%d'%i for i in range(40))).is_file()"`
