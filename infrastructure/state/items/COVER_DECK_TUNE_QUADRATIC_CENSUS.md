# COVER_DECK_TUNE_QUADRATIC_CENSUS

FlowWorks: cover deck census O(N^2), mixed-tier lead threshold, 400 cap

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C4-F3** CONFIRMED MEDIUM — Every pit cover floods its whole deck every scan (O(N^2) on big covered moats). Pits/Trigger/CompPitCoverTrigger.cs:73-76 builds Deck(self) before the lowest-id lead check, on every cover.
- **C4-F5** CONFIRMED LOW — A mixed-tier cover deck springs at the LEAD cover's tier (lowest thingID), not per cover. CompPitCoverTrigger.cs:76 lead = lowest id, :104 threshold from Pit.CoverTier of the lead.
- **C4-F6** CONFIRMED LOW — Decks over 400 covers are census-truncated: several leads, partial collapse. Pits/Building_PitCover.cs:65 'deck.Count < 400'.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
