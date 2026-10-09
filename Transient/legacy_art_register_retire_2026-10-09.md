# Legacy art register retire 2026-10-09

## apply_verdicts.py (+ its only generator make_verdict_sheet.py) — REMOVED
Readers: none live (no importer, no doc/hook/systemd instruction to run; judge_cli.apply_verdicts is an unrelated function).
Design table art_ledger_design_2026-10-04.md lines 315-316 marks both retired (0 events ever). Dead pointers fixed in
git_migration_phase5 doc, art_resolution_rootcause doc (R11 row), DESERT_FAMILY_PORT_EXECUTION_1 item.
Left: `artreg.py verdict/committed/deployed` subcommands (only caller was apply_verdicts) — can be removed next.

## art_status.json — KEPT (live readers)
Writer: artreg.py render (daemon, every job). Readers: infrastructure/dashboards/hub/{regen_hub,hub_check,build_standalone,make_tab_data}.py,
artpipe/artpipe_state.py (SEARCH_FILES, find), artreg.py. Migration = reproject from ledger + repoint hub; not done.

## decisions_propagated.json (+ flora_) — KEPT (live readers)
Readers: design/Jawa/worldbuilding/review/apply_assignment_verdicts.py (load_propagated_notes, best-effort; ledger has the same
notes under row_key, source_file=decisions_propagated.json, 1121 events), round2/build_review_deck.py, round2/build_review_pptx.py,
~25 design docs cite it as provenance. Migrate the 3 scripts (or declare deck builders dead), then rewrite doc pointers, then git rm.
