# review_B (FlowWorks Python, 19 files) - all CLEAN 2026-10-15
Reachability: all live (imported by validation.py/selftests/other northstar modules or documented CLI live proofs: climb_proof, pond_pump, liquid_checks). No dead files.
Never-clean (full review): climb_proof (docstring owed list wrong, fixed), selftest_climb_proof, pond_pump, selftest_pond_pump (none), selftest_conservation_roundtrip (trip 9 vacuous round trip -> real float32 G9 check; stale comment + unused import).
Previously clean (diff-scoped since mark): extensions (tank_loop OFF passed on unanswered tank -> UNMEASURED fixed), extensions_rivers, fakegame, liquid_checks, prep_site, selftest_extensions (redundant ternary), selftest_flowworks_northstar, site_spec, validation_v2 (stale "either rule" docstring), review_map, call_sites, cover_breaks, hose_port, validation: nothing.
Selftests: 13 FlowWorks selftests + validation_v2 --offline green.
