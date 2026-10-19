# Proposed skill-text patch: rimworld-review-sheets, 2026-10-19 (for the next curation pass)

Skills are edited only in fresh-context curation sessions (CLAUDE.md), so this is a proposal, not an edit. Files are the
repo copy `skills/rimworld-review-sheets/` (`.claude/skills/rimworld-review-sheets` resolves to it). Source of the
change: owner card 2026-10-19 "How far do we go to make art review fast and reliable? → Python command, no agent before
you see it"; design `design/RimMandrake/art_sheet_speedup_2026-10-19.md` (option B); commits 7e22dc2de, 8668090c8 and
the review_queue commit.

## SKILL.md

1. "Which builder" table — add a first row:

   | everything waiting on his pick, across all open sheets | `python3 src/RimMandrake/Utils/art/art.py review awaiting-pick` (builds, gates, serves, opens; `--dry-run` lists the rows) |

   and one line under it: *When he asks to "see the art", run this first. No agent composes the subject list.*

2. "The lifecycle" step 2 (Serve) — append: *A stale row (installed art changed since the build) is badged `STALE:
   <reason>` with its picks off; the sheet still serves (owner card 2026-10-19). Do not rebuild other sheets before
   serving the one he asked for.*

3. "Before he sees a sheet" — replace nothing; add: `- [ ] stale rows, if any, are badged on the page (no whole-sheet refusal any more)`.

## references/lifecycle.md

1. § Serve — DELETE the false line "`refresh_sheets.py` restarts a dead server itself (same log), so an already-served
   sheet needs nothing." Replace with: "`refresh_sheets.py` does NOT restart a dead server unless `--restart-servers`
   (default off since the 2026-10-14 OOM: one server per sheet reached 5.1 GB)."
2. § Build — add `art.py review awaiting-pick` above the three `art_sheet.py` lines, with the definition of
   "awaiting his pick" from the `review_queue.py` docstring (open sheet; untouched row; something to pick).
3. § Serve — add: "`art.py review awaiting-pick` keeps ONE server for its page (`<sheet>.server.json` holds pid + URL)
   and reuses it while it answers; it never starts per-sheet servers."

## references/art_requirements.md

1. § Enforcement, "Renders for real" (req 13) — append: "The throwaway sidecar logs to a FILE, never a pipe: a pipe
   read only until the URL filled at ~64 KB of 404 lines and deadlocked every big sheet until the 600 s timeout
   (2026-10-19, `selftest_gate_browser.py`). The Edge stage is capped at 90 s (`GATE_EDGE_TIMEOUT_S`) and a timeout is
   not retried."
2. Wherever it says a stale sheet is refused when served — change to: "a stale ROW is badged and its picks are off;
   only a page with no ITEMS block is refused. Gate req 15 still refuses a sheet stale at build."

## references/traps.md — add rows

| Big sheet never gates | req 13 hung on the sidecar's stdout pipe (fixed 7e22dc2de) | `selftest_gate_browser.py`; a gate over 2 min is a bug, not load |
| Rebuild cascade before a sitting | the hourly install made ~20 sheets stale and serve refused them whole: 53 min of serial rebuilds (2026-10-19) | rows are labelled now; never rebuild unrelated sheets to serve one; `art.py review awaiting-pick` |

## Controls removed from the page (2026-10-19) — for any doc describing the row controls

Gone: the Requests panel, `✕ not for this slot`, every random-pool verb (`+ random pool`, `leave the random pool`,
`add all new renders to the pool`), the `this is:` select (now `use` / `not needed`, same `assign` field).
`accept unchanged` was already gone (2026-10-12). Data those controls saved still reads and enacts; the note box is the
place for rename, description, more-like-C, pool, size, move and cut.
