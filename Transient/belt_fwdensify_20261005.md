# belt fwdensify 2026-10-05

## status
- started Mon Oct  5 17:40:26 PDT 2026

## phase1 lessons

## phase2 apply

## phase3 prove
- lessons doc published 33da014e5 (design/RimMandrake/northstar_densification_lessons.md)
- review-sheet helper (opus) dispatched: FlowWorks/human_review_sheet.py + selftest + review/
- finding: floor 38/38 is claimed by validation.py plot chains that have NEVER run live; modcheck record judged v2 rows (no shows). Densify = wire shows onto v2 rows (GSS ROW_SHOWS) where v2 proves the mechanism; visual plot chains + toggle chains v2 duplicates -> delete; optional-feature toggle chains -> extensions module.
- NOTE: another session at 59681505d (owner) released FlowWorks: walk DRAFT, hash blank, status record forgotten. floor now "DRAFT no bar" for FlowWorks by design; coverage checked in memory (uncovered [] / orphans [] / cannot-unclaimed [] / toggles []).
- v2 densified: 74 -> 58 live rows (harness 11->5 folded rows; 5 per-direction E2 + shared-source oracle + A/B/C/R global -> G_every_cell_vs_oracle). mock GREEN 58, offline PASS incl O-LIVE-NEG 32 faults.
- validation.py 1541 -> wiring (~200): ROW_SHOWS/ROW_TOGGLES on v2 rows; extensions.py holds plots + optional toggles; 7 toggle chains deleted (v2 proves both sides).
- PUBLISHED fb68e4020 (densification) ; helper sheet 869099fdc (139 caps: 39 PROVEN / 63 BUILT-UNPROVEN / 14 PARTIAL / 23 NOT BUILT)
- peer agent mid-edit in this clone: FlowWorks Source (superdeep rooms: captureDown/rooms/wardenFromLip), DLL, JobDefs, Keys -- NOT mine; selftest_flowworks_northstar FAILs "same field set as the C#" because of it
