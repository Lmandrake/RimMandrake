# RIMMANDRAKE_FIX_LEFT_OPEN_PARSE_READS_ITS_OWN_DENIAL

## spec

`detached_helper.result_left_open` (`src/RimMandrake/rimflow/detached_helper.py:1252`) finds `LEFT OPEN:` with
`t.upper().find(LEFT_OPEN)`. That matches the phrase anywhere in the result text, including a run that says it
wrote NO such note.

Failure observed 2026-11-19 8:01 PM PST: run `rm-detached-bench-rimmandrake-fix-red-selftests-one-sweep-1795144073`
ended with "The slice item ... stays `doing` (no `LEFT OPEN:` note; its 5-line summary is below)". The continuer
(`left_open_continue.py`) launched `...-1795147264` and quoted `LEFT OPEN:` note; its 5-line summary is below)` as
the run's verbatim LEFT OPEN note, with the "carry on from where it stopped" brief. The correct brief for that case is
the owed-close brief ("settle that: close the item or write a note that starts LEFT OPEN:"). The same parse feeds
`owed_close`, so a denial also hides an owed close from the status page.

Fix: a LEFT OPEN paragraph starts at the start of a line (optional leading markdown emphasis `*`/`_`). A mention
inside a sentence is not a note. Keep the paragraph cut (to the next blank line) as it is.

## criteria

- A result that only mentions `LEFT OPEN:` inside a sentence yields `""`.
- A note at the start of the text or of any line is returned, to the next blank line, including a `**LEFT OPEN:**`
  line.
- When a mention comes first and a real note follows, the real note is returned.

## verify

Acceptance test (run from the repo root). Watched FAIL on base `db268445c0`: `PASS 3/6`, exit 1. A correct fix prints
`PASS 6/6`, exit 0. Put it into the formal selftests with the fix.

```python
import sys; sys.path.insert(0, 'src/RimMandrake/rimflow')
import detached_helper as DH, role_launch as RL
cases = [
    ("stays `doing` (no `LEFT OPEN:` note; its summary is below).", ""),          # negated mention: no note
    ("LEFT OPEN: rerun mutants\nstill owed\n\nbye", "LEFT OPEN: rerun mutants\nstill owed"),  # note at text start
    ("Done.\n\nLEFT OPEN: two tickets\n\nend", "LEFT OPEN: two tickets"),        # note at a line start
    ("Done.\n**LEFT OPEN:** two tickets", "**LEFT OPEN:** two tickets"),        # bold markdown at a line start
    ("mentions no `LEFT OPEN:` note.\n\nLEFT OPEN: real one", "LEFT OPEN: real one"),  # mention first, real note after
    ("", ""),                                                                    # empty result
]
ok = 0
for text, want in cases:
    RL.read_result = lambda r, t=text: {"result": t}
    got = DH.result_left_open({})
    if got == want: ok += 1
    else: print("FAIL", repr(text[:40]), "->", repr(got[:40]), "want", repr(want[:40]))
print("PASS %d/%d" % (ok, len(cases))); sys.exit(0 if ok == len(cases) else 1)
```

## refs

file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/left_open_continue.py
