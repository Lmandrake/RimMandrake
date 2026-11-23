# Measurement on real commits, 2026-11-23

Input: 17 commits that changed guiding prose: six rewrite commits of 2026-11-23 (`d11bfc6623`, `297e5c4214`,
`ea995310da`, `7042d696f6`, `37b717f531`, `ab2a3252f6`) and eleven ordinary commits of 2026-11-21 and 2026-11-22
(`ecb17dcdd8`, `cba242eda8`, `68355dc59b`, `50b30264c4`, `fe2670e8c8`, `c3633a8f30`, `ccd3ad1490`, `c4f917ce9c`,
`3395b45329`, `58ed9adf69`, `831d8d9d51`). Together they add 2,783 new sentences. The reader of the flagged and the
unflagged lines was the run that built the check, not a fresh reader. The final glossary is the one that landed with it.

| reading | count |
|---|---|
| sentences that the six rewrite commits add | 2,349 |
| sentences that the eleven ordinary commits add | 434 |
| program faults | 51 (37 bare pronouns, 5 long sentences, 9 of the other kinds) |
| model-reader faults (final glossary, one run) | 69 |
| new sentences with at least one fault | 106 (3.8%) |

## The flagged lines (all 51 and all 69 read)

- **Program, 51.** By the letter of the account rule, 1 is a false alarm (a list of boot times, counted as 27 words).
  Most of the 37 bare pronouns stand directly after the sentence that holds their noun. The account rule forbids them
  ("name the subject in each sentence, rather than use a pronoun"), but a reader who sees both sentences loses little.
  So the false-alarm rate is 2% by the rule's letter, and it can feel like most of the pronoun hits to a writer. That
  is the first thing to look at if the check is ignored.
- **Model reader, 69.** 3 were "Design Version", which the glossary holds since. Of the other 66, 8 are false alarms by
  this reading: "monitors" (its object is plain), "this pass", "Producer", "the probe log", "the note", "Since the fix"
  and "home biome" twice. So the false-alarm rate is about 12%.
- The reader found on its own most lines that the rewrite runs had listed under "Could not determine": `D/F`, "the
  belt", "Revert", "a root, an exam waiver, a floor disable", "coverage park", "N", "hashed section", "the pilot" and
  "preflight O13".
- A first run without the machinery words in the glossary gave 87 reader faults. "Seat", "card", "his five acts",
  "leave line", "companion" and "calibrated brief" made about 14 of them.
- The reader is not deterministic. The two runs flagged 81 and 62 lines and share 44. The glossary rows made part of
  the difference. Both runs named each of the owner's three lines.

## The unflagged lines (45 read, a random sample)

41 are good. 4 are lines that a cold reader cannot fully act on, and the check let them pass: "go to his set",
"the three defs that he described", "off-tier", "sit past the cut". So about 9% of unflagged lines hold a weak term.

## Calibration and mutation

- The reader: 18 planted cases, 10 bad and 8 good, all as planted (`infrastructure/state/judge_calibration.json`, family
  `guiding_prose_reader`). Sonnet missed "the D/F primitive" on the owner's own line, so the reader is Opus. One call
  took 4 to 13 s and about 27,000 input tokens, most of them cache writes.
- The selftest: 42 mutants of the check, of `publish.py` and of `detached_helper.py`. 40 were caught at first. Two
  survived (a fenced block with an empty line; other emphasis on old words). Each got a case, and both are caught.
