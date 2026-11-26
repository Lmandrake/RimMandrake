# Pre-Design Concepts

This folder is the store of Pre-Design Concepts: good ideas that the owner likes and that nobody has designed yet. A
concept can be of any kind: a new mod, a capability for a mod that does not exist yet, a new agent, a new pipeline, a
tool, or another kind. Each concept has its own file, so that a concept can hold much detail.

The Maturation Pipeline's status page (`D:\ClaudeWork\rimmandrake\conductor\MATURATION_NOW.md`) shows, at its intake,
how many concepts wait here and the plain name of each.

## The rules of the store

- **Any seat may add a concept.** Write a new file here. You need no ticket and no ask.
- **A concept is not owed work.** Nothing in the store is scheduled. No run starts from the store.
- **No sweep, filter or judge ages, shortens or drops a concept.** Only the owner drops a concept.
- **More detail is better.** Copy everything that is known. Never shorten a concept to save space.
- **A capability for a mod that exists does not go in the store.** Such a capability goes on the next-version list of
  the mod: `D:\Luke\dev\RimMandrake\design\concepts\<Mod>\version\next_version\README.md`.
- **A concept leaves the store when the owner picks it.** Then the concept becomes a mod at the intake of the Maturation
  Pipeline, an entry of a next-version list, or a ticket. Write in the concept's file where the concept went, in its
  `- **Went to:**` line. The file stays as the record. The page does not count it, and it is never due again.

## The weekly card

About once a week, the line `PRE-DESIGN CONCEPTS: card due` goes to the Conductor log
(`D:\ClaudeWork\rimmandrake\conductor\log.md`), with the concepts that are due. The daily tick of
`rm-crystallize.timer` writes it once per ISO week (`pre_design_concepts.py sweep --apply`). The Conductor reads each
due concept and offers the owner one question card: each option is one concept to flesh out with the Conductor, and one
option lets all of them sleep. After his answer, the Conductor runs `pre_design_concepts.py offered <name> --answer
"<his answer>"` for each concept on the card (`D:\Luke\dev\RimMandrake\src\RimMandrake\rimflow\roles\conductor.md`,
Quick mode step 3).

## The form of one concept file

The file name is `<plain_name>.md`. The head of the file is these bullet lines, before the first `## ` section:

    # <plain name>

    - **Name:** <plain name>
    - **Kind:** <new mod | capability for a mod that does not exist yet | new agent | new pipeline | tool | other>
    - **Gets:** <one sentence on what the player or the user would get>
    - **Added:** <YYYY-MM-DD>
    - **From ticket:** <the ticket that the concept came from, or "none">
    - **Code:** <whether code exists, as measured, with the date and how>
    - **Last offered:** <never | YYYY-MM-DD>
    - **His answer:** <none yet | his answer at the last offer>

The body holds everything that is known: his words with their dates (quoted from the ledger, never rewritten), the full
prose and notes of the source ticket, the card texts, and the paths of design files. `## Offers` keeps each offer and
his answer, oldest last; `offered` writes it.

## The program

`D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\pre_design_concepts.py` (no model):

    python3 src/RimMandrake/Utils/pre_design_concepts.py list      one line per concept
    python3 src/RimMandrake/Utils/pre_design_concepts.py check     fails by name on a file that lacks a field
    python3 src/RimMandrake/Utils/pre_design_concepts.py due       the concepts for the next card, at most four
    python3 src/RimMandrake/Utils/pre_design_concepts.py offered <name> --answer "<his answer>"

Its test: `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\selftest_pre_design_concepts.py`. Its promises:
`D:\Luke\dev\RimMandrake\design\specs\2026-11-26-pre-design-concepts\boundary.md`.
