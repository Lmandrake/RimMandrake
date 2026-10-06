# Placeholder gate wiring progress 2026-10-05

DONE: art_sheet.py PLACEHOLDER badge (live cols of PLACEHOLDER rows); scaled_review_gate.py req 3 counts placeholder-only as no art of ours (+ selftest fixture); SKILL.md req 3 + Enforcement lines.
Selftests: 190/191; the one failure is src/RimMandrake/bridgetools/selftest_tool_metadata.py (DLL lacks 9 source tools; unrelated, stale DLL).
Rebuild (refresh_sheets --force): rebuilt+PASS with badges: Webwork, Twilight Sea, The Chill (every placeholder row has a pending job).
Rebuild REFUSED by req 3 (previous stamped sheet still served): Grey Sea (RM_HaarnCatch, RM_HessalCatch placeholder, no job), Fever Wood (RSW_Plant_Chakroot_Wild donor-only), Weeping Stones (Plant_Ambrosia donor-only), Greentide (Plant_Grass donor-only).
`gate all --urls` PASS on greysea/feverwood-class sheets is the OLD sheet verifying; the new build is what fails.
