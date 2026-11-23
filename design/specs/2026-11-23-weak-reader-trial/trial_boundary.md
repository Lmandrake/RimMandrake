# Boundary: what the weak-reader trial measures

## It measures
- The share of correct acts that a fresh reader (Sonnet, and Opus as a check) states, from ONE section of a rule file,
  in ONE situation. Four outcomes stay apart: CORRECT, WRONG, NOT_TOLD ("the text does not tell me"), FAILED (the call
  failed or gave no readable answer). FAILED is never counted as a wrong act and is never dropped silently.
- NOT_TOLD is the reader's own mark (`TOLD: no`). A program reads it; the grader does not decide it.
- The difference new − old for four kinds of change. The kind belongs to the sentence that the situation turns on,
  not to the whole section. Measured on a random 36 changed sections: an Opus reading calls 3 of them style only. So a
  whole section is almost never of one kind, and the other changes in a section travel with the arm.
  - STYLE: the sentence was split, made active or reordered; same meaning, same terms.
  - BINDING: an undefined term got its meaning at its place (a RESOLVED row of `undefined_terms_and_conflicts.md`).
  - CORRECTION: a false line was corrected (a row of `conflicts_settled.md`). The known positive.
  - CONTROL: a section with the same bytes in both arms. The known zero.

## It does not measure
- What an agent with tools does in a real session. A reader states an act; it does not act, and it cannot open the file
  that a pointer names.
- Whether a reader of the whole file finds the section. The section is put in front of the reader.
- What the owner understands when he reads.
- Root `CLAUDE.md` and the skills that no batch rewrote.
- Any case where the rule of today is already newer than both texts. ("No long runs" was picked by the seed and
  removed: his card of 2026-11-23 replaced that rule.)

## How this differs from the earlier study (`clear-findings`)
- Earlier: whole `CLAUDE.md`-style rules reworded to one wording (D), five comparisons from four items, agents' acts on
  tasks, strong models among them; 0 of 5 changed. The rules bound already (the gate says "if every term binds, stop").
- Here: one section against its real rewrite; three kinds apart; the weakest model that the estate permits; a
  known-positive kind and a known-zero kind, so a zero can be told from a blind instrument; and NOT_TOLD is its own outcome.

## Separation
- Old text: `git show <base>:<path>`. New text: the same path at `4b95f0e62a` (`pool.py`).
- The cases were picked by seed 20261123 from lists. By hand, I removed from each list the rows that no act turns on
  (a fact table, a name only). That filter is a judgment, made before any reader ran.
- Situations, keys and planted answers: fresh Opus calls (`author.py`), no tools, each with the OLD section, the
  target sentence of the old text, and the source of truth. No call gets the new text. One call for each case, not
  one long session, so that no case colours another.
- A limit: I wrote the source-of-truth strings (`make_spec.py`) from the code, commits and owner words, and I had seen
  many new lines by then. So a source string can carry a word of the new text. That favours the new text in BINDING
  and CORRECTION. The STYLE source is the old text itself. That favours the old text.
- The style target was picked by an Opus call that saw both texts; it gave back only the old sentence to the author.
- A second fresh Opus call (`keycheck.py`) reads only source, situation and key, and says whether the key follows. A
  case that fails is dropped before any reader runs, and the next reserve case takes its place.
- Grading: an Opus call for each case gets the key and the ACT lines only, in shuffled order, with random ids: no arm,
  no model, no quoted words (a quoted word shows the arm). Plants are mixed in.

## Machine
`pool.py` → `classify.py` → `make_spec.py` → `author.py` → `keycheck.py` → `run.py` → `grade.py` → `score.py`. `selftest_trial.py`
tests the parser and the scorer. Raw answers: `raw/answers.jsonl`. No limit on calls but a 20-minute hang guard for each call.
