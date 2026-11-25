# BOUNDARY: guiding prose is checked when it is written, Design Version 0.1.0

Code: `src/RimMandrake/Utils/guiding_prose.py`, its config `src/RimMandrake/Utils/guiding_prose.json`, its reader brief
`src/RimMandrake/Utils/guiding_prose_reader.md`, the line that `src/RimMandrake/Utils/publish.py` `main` adds after a
landing, and the line that `src/RimMandrake/rimflow/detached_helper.py` `main` adds after a launch. Item:
`RIMMANDRAKE_CHECK_GUIDING_PROSE_AT_WRITE_NO_SEARCHING_FOR_MEANING`, written 2026-11-23. The owner, 2026-11-23: *"Yes we
should have a check that when we write any guiding prose (the equivalent of code) it should be checked to follow the
account level Claude guidance on binding and simplified language. No more searching across whole documents to figure out
what something means. Rules have to be exceptionally clear to be powerful or they can't bind to the moment they pertain
to."* Each promise has a test of its name in `src/RimMandrake/Utils/selftest_guiding_prose.py`.

Guiding prose is a text that tells an agent how to act. `guiding_prose.json` holds the one list of those files. A fault
is one term or one sentence form that a reader at that line cannot resolve in one step. The lint that this check uses is
`design/specs/2026-11-19-plain-english-rule-docs/rule_doc_lint.py`. The glossary that this check reads is `LEXICON.md`.

## What a program decides, and what a model reads

Measured 2026-11-23 on 2,357 sentences that six rewrite commits changed (`d11bfc6623`, `297e5c4214`, `ea995310da`,
`7042d696f6`, `37b717f531`, `ab2a3252f6`). The figures after the build are in `measurement.md` beside this page.

| rule | decided by | why |
|---|---|---|
| a long sentence | the lint's count | A command has at most 20 words and a description at most 25 (ASD-STE100). A quote and a code span count as one word each. Words in parentheses do not count: most are evidence. A colon, a semicolon, a dash or a comma before a joining word ends the count. |
| two commands in one sentence | the lint | Only two positive commands. "Do X; never do Y" is one instruction with its contrast: all 4 hits of the plain lint were that kind. |
| active voice | a program, narrowed | Only a duty with no actor ("must be run"). Plain passive (135 hits) was good text in almost every sample, and `FINDING.md` of clear-findings measured passive as no defect. |
| modals | a program, narrowed | Only `should`. `may` gives permission, `would` and `could` sat in tests and past facts (58 hits, almost all good). |
| -ing forms, a condition after its command, capital letters | not checked | 122, 3 and 291 hits, almost all good text. |
| a bare pronoun as the subject | a program | A closed list of sentence openings. |
| state written as prose | a program | A closed list of phrases. A sentence that holds a date is a dated reading, not state. |
| a path or an item id that does not exist | a program | The tree and the ledger answer. |
| a coded name (`D/F`, `D31`) | a program | The section, the sentence and `LEXICON.md` answer. |
| a retired name | a program | `LEXICON.md` §Retired names answers. |
| "see above", a verb with no object ("Revert if") | a program | Closed lists. |
| a coined term made of ordinary words, a synonym | a model | No list can hold them. "The belt" is two ordinary words. A program that flags each unexplained "the X" flags most good lines. |

The model reader is one Opus call with no tools, on the changed sentences and their sections only. Sonnet missed `D/F`
on the owner's own line, so the reader is Opus.

## ACCEPTS (the only inputs this is built for)

- **a-landing-of-local-commits.** `./publish` in a git clone: the changed lines are the diff from the merge base with
  `origin/main` to the commit that the landing replayed.
- **a-brief-file-or-text.** `detached_helper.py launch --brief-file F` or `--brief TEXT`, before the footer is added.
- **markdown-with-atx-headings.** Bullets, paragraphs, tables, fenced code and block quotes, as `rule_doc_lint.py`
  reads them.

## DOES NOT SURVIVE (not promised)

- **our-own-prose-in-quote-marks.** Text between quote marks is exempt, whoever wrote it. The check reads the marks; it
  does not prove that the words are his.
- **a-landing-that-is-not-publish.** A `git push`, a merge on the server and a ledger landing run no check. The daily
  recheck counts landings of guiding prose that have no run record, and names them.
- **instruction-text-inside-code.** A brief that a program builds from strings in code, and a hook's refusal text, are
  read only as a launched brief.
- **a-definition-that-is-wrong.** The check asks if a term is defined at the line. The check does not ask if the
  definition is true.
- **every-vague-word.** The reader is told to flag only a term that two readers could take for two things and then act
  differently. A weaker vagueness passes.

## LIMITS (each names the danger that it guards and the evidence)

- `20 words` in a command (`MAX_SENTENCE_WORDS` of the lint) and `25 words` in a description (`MAX_DESCRIPTIVE_WORDS`):
  the two limits of ASD-STE100. Danger: a sentence that holds several ideas, which a reader at that line must take apart.
  Evidence: the census of 2026-11-19 (4,247 long sentences).
- `DOOR_TIMEOUT_S = 180`, `GIT_TIMEOUT_S = 60`: hang guards of the recheck and of local git reads.
- `READER_TIMEOUT_S = 300`: a hang guard. Danger: a model call that never returns keeps the writer's `./publish` open
  after the landing. A real call took 4 to 13 s on 61 to 434 sentences.

## PROMISES (each one is owed a test of the same name)

- **the-list-covers-the-census.** Each file of `census.json` that still exists is matched by `guiding_prose.json`, or is
  in its `left_out` with a reason. `GUIDING_PRINCIPLES.md` is matched.
- **the-three-lines-he-quoted-are-caught.** In the wording before `de63778138e0`, "the D/F primitive", "the belt" and the
  "in progress" build are each caught and named, with a repair that says where a definition goes.
- **the-repaired-lines-stay-green.** The same section as repaired at `de63778138e0` gives no program fault.
- **each-form-fault-is-caught-and-named.** A bare pronoun subject, a 30-word sentence, `should`, a duty with no actor,
  two commands in one sentence, state as prose, a verb with no object, a dead path, an item id that the ledger lacks, a
  coded name with no meaning and "see above" are each caught, and the fault names the words.
- **exempt-text-stays-green.** An owner quote that breaks each rule (one line, many lines, a block quote), a table row, a
  fenced block, a code span, a heading, front matter, an existing path and a filed item id give no fault.
- **only-changed-sentences-are-read.** A sentence that the old text already holds gives nothing: an unchanged file with
  many faults, a re-wrapped bullet, a moved bullet, and the old lines of a file with one new line.
- **the-reader-gets-only-what-changed.** The reader's prompt holds each changed sentence, its whole section, the file's
  opening lines and the glossary, and no other section. With no changed sentence, no model runs.
- **the-reader-answer-is-bound-to-the-line.** A reader fault whose term is not in the numbered sentence is dropped and
  counted. A dead call, a refusal, an unreadable answer and a timeout each read UNMEASURED with the cause, never zero.
- **an-uncalibrated-reader-sends-nothing-back.** While the reader's row in `judge_calibration.json` is not CALIBRATED,
  its faults print as "shown only". When the row reads CALIBRATED, they count as faults.
- **a-publish-with-faults-still-lands.** `./publish` of a rule file with faults prints `PUBLISHED`, exits 0, and then
  prints each fault with its repair. The check runs after the landing and outside the clone's lock.
- **a-launch-with-faults-still-starts.** A launch by a program or by a launched run (`RM_ROLE_UNIT` set) with a faulty
  brief starts the unit, exits 0, and its text ends with each fault and its repair. A refused launch's text stays the
  gate's own. A test's stand-in for `launch` and a throwaway clone that does not hold `guiding_prose.json` are not read
  and leave no record.
- **a-principal-launch-gets-its-faults-before-the-start.** A launch from the Conductor window or the owner is read
  before the start. A brief with a fault that counts starts nothing, sends no sentence, exits 5, and its text names
  each fault with its repair. A changed brief is read again. The same brief text launched again unchanged starts, and
  its faults print as a NOTE after the start, so a fault that the writer judged wrong never blocks. A brief with no
  fault starts at once. A check that raises before the start stops nothing. A "shown only" fault of an uncalibrated
  reader never returns a brief. Item: `RIMMANDRAKE_TRIAL_STE_BRIEFS_CHECK_BEFORE_LAUNCH_NOT_AFTER`; 4 of 11 Conductor
  briefs of 2026-11-24 needed a correction note after their run had started.
- **a-sentence-already-sent-in-a-brief-is-silent.** A sentence that an earlier launch sent is not checked again, so a
  program's template is read once.
- **a-broken-check-stops-nothing.** When the check itself raises, the landing and the launch complete and the writer
  reads one line that says UNMEASURED and the cause.
- **a-principal-gets-a-note.** For the owner or the Conductor window, the faults print as a NOTE, and the run record
  names the principal. The record of every run holds the faults.
- **the-check-verb-exits-for-a-caller.** `guiding_prose.py check` exits 0 with no fault, 1 with a fault, 3 when it could
  not look. `./publish` and `launch` keep their own exit codes, except the return before the start (exit 5).
- **one-list-for-a-meaning-nobody-finds.** `guiding_prose.py unfindable` files one ledger item for a term in a file, with
  the file, the line, the term and the exact question. A later question on that term and file is a note on that item. An
  entry with no question is refused.
- **the-recheck-sees-a-dead-check.** `guiding_prose.py recheck` writes its reading only as `ok` when a planted fault
  went through a real throwaway `publish.py` and came back, and when the launch path returned one too. A check cut out
  of either door reads `ok: false` with the cause. The launch door is played twice: as the Conductor window (the
  brief must come back before the start) and as a launched run (it must start and return the fault after), and the reading names each landing of guiding prose with no record.
