# DROID_CANON_LIBRARY_1

Broad canon index of Star Wars droids, deliberately wider than the game's current content
because the owner intends to add droids from it. Owner's ask, verbatim: *"do the same thing
for every droid type on the web we can find. We may very well add more droids to the game, so
make this search more broad and comprehensive. Include manufacturing company, typical racial
ownership, time period, etc."*

## What exists

`design/RimStarWars/canon_references/DROIDS_INDEX.md` — **1,757 droids**, eight columns, every
row carrying a source URL. QA'd once: junk rows, duplicates and malformed rows removed, and
two invented-looking fields blanked.

Measured coverage (derived by counting the table's own rows, not a naive scan):

| column | filled | |
|---|---|---|
| name | 1757 | 100% |
| continuity | 1757 | 100% |
| source URL | 1757 | 100% |
| class / role | 1577 | 89.8% |
| typical owners | 890 | 50.7% |
| manufacturer | 693 | 39.4% |
| **era** | **48** | **2.7%** |
| already in repo | 54 | 3.1% |

## 🔴 RULED — era stops at 2.7% (owner, 2026-09-15)

**Era cannot be filled from canon, and the owner accepted that rather than deriving it.**

A script fetched all 1,757 articles: 48 carry a usable era, **1,709 are confirmed blank** — no
`firstmade`, `retired`, `birth` or `death` field exists on the article — and zero errored. The
gap is in Wookieepedia, not in our extraction.

He was offered a derived-era column built from each droid's first appearance, which would have
given near-complete coverage, and **chose to stop at 2.7% instead.** So:

- ⛔ **Do not "finish" the era column.** It is not unfinished; it is complete and the field is
  genuinely absent. A future pass that fills it by inference is reversing a ruling.
- Era is honest where present and blank where canon is silent. Filtering the index by period is
  therefore not possible, and that cost was accepted knowingly.

Two traps caught during that run, worth keeping: treating the Legends continuity flag as an era
marker would have mislabelled roughly half the index, and one live wiki page really does carry
`retired=Galactic Republic` — a faction, not a date, the same defect our own earlier QA had
already fixed once.

## Still open

- **Do individual droids get `description.md` entries** the way the 69 species did, and if so
  which? 1,757 is infeasible; the 54 already in the repo plus named candidates is not.
- Manufacturer at 39% and owners at 51% could both be raised from article prose rather than
  infoboxes, if either is worth the runs.
