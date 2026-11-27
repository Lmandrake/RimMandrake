# Boundary: `ruling_search` finds the lines that may say the opposite of a new ruling (`src/RimMandrake/rimflow/ruling_search.py`)

Item RIMMANDRAKE_BUILD_RULING_SEARCH_540_GREPS_FOR_OPPOSITES (script candidate 3 of
`design/specs/2026-11-26-script-candidates/one_page.md`). Why: 68 owner turns carried into rule files held 540 grep or
`owner_rulings.py` calls, 48 min of generation (a bound: some calls were not hunts for an opposite line). The program does
the search. The model still judges whether a line really says the opposite, and writes the new wording. The part that
records his words and places the rule is `ruling_fast.py` (page `design/specs/2026-11-26-ruling-fast-path/boundary.md`).

Code: `src/RimMandrake/rimflow/ruling_search.py` (all of it).

## ACCEPTS

- **his-words.** `ruling_search.py "<his words>" [--root DIR] [--top N | --all] [--min-terms K]`. The key terms are the
  words of 4 letters or more that are not stop words, cut to a simple stem ("holds", "hold" and "holding" meet; "held" does not).
- **five-trees.** Under `--root` (default: this repo): `CLAUDE.md`; `design/RimMandrake/standing_rulings.md`;
  `src/RimMandrake/rimflow/roles/` (`*.md`, `*.txt`); `skills/` (`*.md`, `*.txt`); `design/specs/*/boundary.md`.

## DOES NOT SURVIVE

- **a-different-word.** A line that says the opposite in other words (no shared content word) is not found. Search with
  the other words too.
- **a-judgement.** The program does not say that a line is against the ruling. It prints candidates, ranked by how many
  terms they hold.
- **a-short-key-word.** A content word under 4 letters is not searched.

## PROMISES

- **finds-a-planted-opposite-line-in-each-tree.** A line that holds the key terms and sits in any one of the five trees is
  listed under that tree.
- **prints-file-line-and-the-negation-words.** Each hit prints `path:line`, `[n/N terms]`, the negation words on the line
  (`never`, `not`, `no`, `without`, `only`, `refuse`, `stop`, `retired`, `dead`, `banned`, ...) and the negation words
  on the line before and after (`near`). The ruling's own negation words are printed in the header.
- **no-hit-reads-none-looked.** A tree that was read and has no hit reads `none (looked)` with the number of files and
  lines read. No tree reads blank. Exit 1 when every tree is that.
- **an-unreadable-tree-reads-could-not-look.** A missing root, a root with no file, or a file that cannot be read or
  decoded reads `COULD NOT LOOK (<cause>)` with its path. The rest of the tree and the other trees are still printed.
  Exit 3, whatever else was found.

Exit 0: a hit in some tree. 2: the call has no key term.

The output is cut to the top `--top` lines per tree (default 8). The count of the rest and the flag `--all` are printed;
the cut hides lines and ends no work.

Each limit names its danger in the code: `TOP_DEFAULT`, `MIN_WORD`, `SNIP`.

## LIFE CYCLES

- **A ruling carried into the rules (by a model worker or the Conductor):** `ruling_fast.py` records his words and
  places the hold and the rule; then `ruling_search.py "<his words>"` lists the lines that may say the opposite; the
  model reads the candidates and edits or removes each line that truly says the opposite.

Later lists beside this page: `polish.md` (none yet).
