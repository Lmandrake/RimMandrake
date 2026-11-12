# Mineral matrix: inputs and how to rebuild the sheet

Item `MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP`. One command, from any clone, rebuilds the matrix on the painted map's
biome list (27 painted biomes plus RM_ChillCrater and RM_LanternDeeps, marked) and the review sheet built from it:

    python3 src/RimMandrake/Utils/mineral_matrix/gen_matrix.py            # writes Transient/mineral_matrix/
    python3 src/RimMandrake/Utils/mineral_matrix/gen_matrix.py --out DIR  # anywhere else

It writes `biomes.csv`, `draft_matrix.csv`, `reasons.csv`, `mineral_homes.csv`, `inventory.csv`, `reach_summary.csv`,
`column_changes.csv`, `stats.json`, then the self-contained sheet `page/index.html` with its pre-review record, then runs
`check_matrix.py` (row set against the audit, every row resolved to its BiomeDef, the `(Jawa)` scan with a planted
probe), `prereview.py check` on the sheet, and a comparison with the 2026-10-30 build. Exit 0 only if every check
passes. The browser harness (`prereview_harness.py <out>`) needs playwright and is run by hand.

## What is here

| file | what it is | where it came from |
|---|---|---|
| `round_two_2026-10-28/draft_matrix_v2.csv` | round-two values per biome row (D1 ladder, D2 steel ~10, D3 home + one minor second, D4 empty biomes, D7-D9) | Archmagi `D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-28\`, written by its `gen_v2.py` |
| `round_two_2026-10-28/reasons_v2.csv` | one reason row per nonzero cell | same |
| `round_two_2026-10-28/mineral_homes_v2.csv` | each mineral's home and second biome (D3) | same |
| `round_two_2026-10-28/inventory.csv` | the material and biome inventory (round one) | same folder |
| `round_two_2026-10-28/reach_summary.csv` | recipe reachability per material | same folder, `reach\reach_summary.csv` |
| `round_two_2026-10-28/design.md` | the round's design and its D1-D10 questions, which the values above follow | same folder |
| `build_2026-10-30.sha256` | hashes of the 2026-10-30 build's outputs (Archmagi `D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-30\`) | measured 2026-11-11 |
| `index.prereview.json` | the judged pre-review record of the sheet; `gen_matrix.py` puts it beside `page/index.html` | a fresh naive judge, 2026-11-11 |

These CSVs are inputs, not derived files: they carry the owner's rulings and the round-two drafting, and nothing in the
repo regenerates them. The copies are byte-identical to the Archmagi originals. Labels and src paths are NOT in them:
the generator reads those from the BiomeDefs under `src/` at run time.

The pre-review record is valid only while every sheet row's fingerprint (label and the row's nonzero cells) matches;
change a value or a label and `prereview.py check` refuses the sheet until someone looks again
(`python3 src/RimMandrake/Utils/art/prereview.py init Transient/mineral_matrix/page/index.html --by judge:<model>`,
fill the rows, copy the record back here).

Nothing here reaches the game: the matrix is design data held for the owner's review (D10).
