# READ_LINE_REGISTRY_SHARED_1 report

## Item read
`infrastructure/state/items/READ_LINE_REGISTRY_SHARED_1.md` does NOT exist on
disk (queue entry in `infrastructure/state/queue/BENCH.md:346-354` says so
explicitly: "no items/READ_LINE_REGISTRY_SHARED_1.md yet"). The ruling text
itself is fully recorded in that queue entry, verbatim-matching the task
prompt, so I worked from that. Did not create the item file — not one of the
four deliverables and creating queue prose is BENCH's own judgement call.

## Deliverable 1: registry file
`design/validation_walks/_read_line_registry.md` — new. Home chosen because
`walklint.find_walks`/`northstar.find_walk` only descend into
`design/validation_walks/<tier>/` subdirectories, so a file directly under
`design/validation_walks/` is invisible to both and can never be mistaken for
a walk. Contains the citation convention (`(class, shared)` tag) and one
entry: `never_engineering_marker_in_player_text`.

## Deliverable 2: lint
`src/RimMandrake/Utils/modcheck/readline_registry.py` (new) — offline,
stdlib-only, report-never-repair, same shape as `walklint.py`. Finds every
`shared`-tagged read-line id in any walk and FAILs loudly
(`DANGLING_CITATION`) if it is not a member of the registry; refuses a silent
zero if the registry file itself is missing.
Wired into `python3 -m modcheck.cli lint` (`src/RimMandrake/Utils/modcheck/cli.py`).
Selftest: `src/RimMandrake/Utils/modcheck/selftest_readline_registry.py` (new,
9 checks, fixture + live-repo), auto-discovered by `run_selftests.py`'s
`selftest*.py` glob over `src/` — confirmed: `run_selftests.py` now reports
67/67 (was 66 before this file existed).

## Deliverable 3: Aftermath draft de-prefixed
`Transient/north_star_read_aftermath_DRAFT_2026-09-16.md` — all 15
`aftermath_`/`rites_` prefixed ids stripped to global-shaped ids (e.g.
`aftermath_prose_is_tier_neutral` -> `prose_is_tier_neutral`). No collisions
between the two mods' de-prefixed ids (verified by inspection). Its own
flagged "id namespace collision" question (section 7) is marked RESOLVED,
citing this ruling.

## Deliverable 4: Oracle reconciled
`design/validation_walks/RimMandrake/Oracle.md`'s
`never_engineering_marker_in_player_text` line (DRAFT section, untouched by
validation) retagged `(absolute, shared)` and annotated as the registry's
founding entry. The Aftermath draft's local copy of the same demand now cites
this entry (`(absolute, shared)`) instead of defining its own.

## floor --all BEFORE (src/RimMandrake/Utils, `python3 -m modcheck.cli floor --all`)
VALIDATED: FlowWorks (13 bars), Graffiti (8 bars), Pits (11 bars). Everything
else DRAFT/no-bar, including Oracle and Aftermath. WreckedMachines confirmed
DRAFT (matches CLAUDE.md note).

## floor --all AFTER
Identical: FlowWorks 13, Graffiti 8, Pits 11, all still VALIDATED with the
same bar counts. Oracle and Aftermath still DRAFT/no-bar. No mod changed
state. `modcheck lint` (walklint + readline_registry) reports 0 FAIL both
checks against the live repo.

## Escalations
None required — the only edits to a real walk file were to Oracle.md's
DRAFT section (no hash to break) and a brand-new file the two lookup
functions already ignore by construction. `modcheck run` was never invoked.
