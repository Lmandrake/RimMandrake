# MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP: done statement

Item criterion A1 (L0), verbatim: "matrix regenerated, complete and correctly labelled; prereview recorded; nothing shipped".
Item verify text: "`gen_matrix.py` regenerates the matrix from the repo; every painted biome has a row, the two extras are
marked, every row's `src` names a real source, no (Jawa) tag remains; the sheet passes its prereview record before it
reaches him. Nothing goes into the game before his review (D10 hold)." Item title: "restore gen_matrix.py".

- [ ] **Regenerates from the repo.** `gen_matrix.py` and every input it reads are committed in the repo (no path into
  `D:\ClaudeWork` or a seat clone); one command in a fresh clone writes the matrix CSVs, and the output matches the
  2026-10-30 build (`D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-30\` on Archmagi) or every difference is explained.
  Evidence: the run's log plus a diff of the output against the 2026-10-30 CSVs.
- [ ] **Every painted biome has a row.** All 27 painted biomes in
  `design/RimMandrake/biome_name_provenance_audit_2026-10-28.md` ("The authoritative biome list") have a row; nothing else
  does except the two extras. Evidence: a check that compares the row set with the audit list.
- [ ] **The two extras are marked.** RM_ChillCrater (aftermath) and RM_LanternDeeps (cave layer) carry rows marked as
  what they are. Evidence: those rows in biomes.csv.
- [ ] **Every row's `src` names a real source.** Each label and src comes from a BiomeDef that exists in `src/` at run
  time. Evidence: the check resolves every row to a def file.
- [ ] **No (Jawa) tag remains** in any output file. Evidence: a measured zero over the outputs, with a sanity probe
  showing the search sees a planted tag.
- [ ] **Prereview recorded.** The sheet built from these outputs has a passing prereview record
  (`src/RimMandrake/Utils/art/prereview.py`). Evidence: the record's `check` output.
- [ ] **Nothing shipped.** No mod file or deployed def changes (D10 hold). Evidence: the diff stat of the closing commit.
