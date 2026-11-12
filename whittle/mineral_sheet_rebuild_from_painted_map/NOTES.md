# Notes (newest first)

## 2026-11-11 19:58 -08:00, picked by CLAUDE_STEVEDESKTOP_OFFLINE2 (offline lane)
- No runs on the item; mode whittle.
- Built on 2026-10-30 by BENCH, never closed: ledger notes say the sheet, `index.prereview.json` (check OK, naive judge
  gpt via gpt_consult) and the xlsx live in Archmagi `D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-30\`, with
  `PROGRESS.md`, `gen_matrix.py` (306 lines), `gen.log`, `page/` (build_data.py, build_page.py, template.html,
  index.html, index.prereview.json), `prereview/` (run.py harness 56/56, judge.json) and `build_xlsx.py`. Reach it from
  SteveDesktop with `ssh mandrake@archmagi-wsl`; it is not on this machine's D:.
- The gap: "gen_matrix.py NOT committed to repo (scratch generator)". Its inputs are round-two CSVs in Archmagi
  `D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-28\` (draft_matrix_v2.csv, reasons_v2.csv, mineral_homes_v2.csv,
  inventory.csv, reach/reach_summary.csv): `R2` at gen_matrix.py line 32. Those carry the owner's D1-D9 rulings, so
  they are inputs, not derived files: commit them (or the smallest set gen needs).
- The owner may already have labelled the xlsx (note 2026-10-30T02:16Z: "Read his edits back from that file"). Do not
  overwrite it; it is his.
- Downstream: MINERAL_MATRIX_DESIGN_ROUND_TWO_SPARSER (proposed, BLOCKED) is fed by this sheet.
- An older round lives in the repo under `Transient/mineral_matrix_round_two/` (untracked rule: never cite it as the
  only copy). Repo registry: `design/RimMandrake/mineral_abundance_registry_2026-10-03.csv`.
- Lessons from the build: infrastructure/state/lessons/*mineral-sheet-old-twin-rows.md, *prereview-items-attr-order.md.
- No live game is needed; classify nothing as MOD/SITE/HARNESS: this is offline data work.
