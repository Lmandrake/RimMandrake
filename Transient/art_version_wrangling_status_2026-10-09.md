# ART_VERSION_WRANGLING_1 status 2026-10-09
Item has no prose file; criteria taken from title + design/RimMandrake/art_ledger_design_2026-10-04.md.

| Criterion | State |
|---|---|
| Find every variant per creature (artpipe, sheets, deployed, git, donor) | MET: `art.py variants` (index 13,506 pictures, 5,222 resources, 861 purged); renders bound 4,414/4,743 (b3c7dd58a, ab8b15b57) |
| What is live and why / what replaced what | MET: `art.py status`, rulings 11,285 events, archive-before-write install |
| One source of truth, better art never overwritten | MET: ledger + `art install` + guard (`art.py guard worktree` = 0 unledgered), PreToolUse hook, writers via artwrite.TextureWriter (9125dbb44); selftests GREEN 258/351, 0 fail |
| Phase 4: desert re-review + the 45 doubles | PARTIAL: doubles ruled and acted; sitting 1 built; sittings 2-3 (deep, blue desert) not built; owner-paced |
| Phase 5: retire registries (apply_verdicts, art_status.json, decisions_propagated, make_verdict_sheet) | NOT MET |
| ~329 renders still unbound | NOT MET (ART_SUBJECT_RESOLVER_1 domain) |

Verdict: NOT ready to mark implemented. CANON_ENTRY_BRIEFS_OWED_1 left alone (doing).
