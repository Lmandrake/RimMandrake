# decisions_propagated repoint 2026-10-09

## Readers
- build_review_deck.py, build_review_pptx.py (round2): DEAD (last touched 2026-09-10, no caller/doc/hook; only a closed item and handoffs mention them). git rm'd.
- apply_assignment_verdicts.py: kept (item ASSIGNMENT_SHEETS_VERDICT_SITTING_1 is BLOCKED but live; mapping mode used). load_propagated_notes() now reads art-ledger rulings (source_file contains decisions_propagated). Equivalence: all 399 old notes present in ledger with 0 text diffs (ledger adds 60+ flora/homeless keys, which the old fauna-only file lacked: correct, more complete); --from-mapping report byte-identical old vs new. Selftest test 5 added.
- decisions_propagated.json + flora_ copy: NOT deleted tonight; no live reader remains in code.

## design/ docs citing it (owner's; not edited) -> point at the art ledger (infrastructure/state/art/events/*.jsonl, rulings with source_file decisions_propagated.json; read via art.py / artledger.read_events by row_key) or infrastructure/state/art_rulings/
- `design/Jawa/worldbuilding/beast_normalization_spec.md`
- `design/Jawa/worldbuilding/biomes/caverns_replacement_scoping.md`
- `design/Jawa/worldbuilding/biomes/rosters/the_propane_lakes.json`
- `design/Jawa/worldbuilding/biomes/rosters/the_rot.json`
- `design/Jawa/worldbuilding/creatures/RUT_ruled_commissions_wave2.md`
- `design/Jawa/worldbuilding/desert_shade_plants_design.md`
- `design/Jawa/worldbuilding/flora_commission_template.md`
- `design/Jawa/worldbuilding/review/homeless_disposition_register.decisions.json`
- `design/Jawa/worldbuilding/review/round2/biome_findings.md`
- `design/Jawa/worldbuilding/review/round2/move_mapping_v2.md`
- `design/Jawa/worldbuilding/rosters/trader_beast_candidates.md`
- `design/RimMandrake/art_ledger_design_2026-10-04.md`
- `design/RimMandrake/art_resolution_rootcause_2026-10-04.md`
