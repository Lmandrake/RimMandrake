# FlowWorks — GPT pre-release consult (BENCH, 2026-10-15)

Owner, 2026-10-15: "since we're getting near deployment, go ahead and do a full ConsultGPT on each mod
individually with all of its information, the design goals, the known behaviors, and information on how
we debug rimworld so that it can help grind out any strange hidden behaviors."

Status: DONE 2026-10-15 — 11 consults answered, every finding triaged in `TRIAGE.md`, 33 items filed (--for BENCH).

Dossier = `dossier/00_brief.md` (design laws, known bugs, how we debug) + `dossier/known_behaviours.md` (heads of FlowWorks ledger items) + the design docs and source named per slice in `consults.py` (referenced by path, not copied). C7/C8 timed out at 585 s and were split into C7a/C7b/C8a/C8b; C8a ran at medium effort without known_behaviours.md.

- `dossier/` — context files built for the consults (design/known-behaviour/debug digests; source is referenced by path, not copied)
- `q_*.md` — the question per themed consult
- `answer_*.md` — GPT answers
- `TRIAGE.md` — every finding, verdict, item ID
