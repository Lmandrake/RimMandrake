<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: [ ] **Regenerates from the repo.** `gen_matrix.py` and every input it reads are committed in the repo (no path into | evidence: `whittle/mineral_sheet_rebuild_from_painted_map/evidence/fresh_clone_run.log` `whittle/mineral_sheet_rebuild_from_painted_map/evidence/diff_vs_2026-10-30.txt`
- true: [ ] **Every painted biome has a row.** All 27 painted biomes in | evidence: `whittle/mineral_sheet_rebuild_from_painted_map/evidence/check.json` `whittle/mineral_sheet_rebuild_from_painted_map/evidence/fresh_clone_run.log`
- true: [ ] **The two extras are marked.** RM_ChillCrater (aftermath) and RM_LanternDeeps (cave layer) carry rows marked as | evidence: `whittle/mineral_sheet_rebuild_from_painted_map/evidence/extras_rows.csv` `whittle/mineral_sheet_rebuild_from_painted_map/evidence/check.json`
- true: [ ] **Every row's `src` names a real source.** Each label and src comes from a BiomeDef that exists in `src/` at run | evidence: `whittle/mineral_sheet_rebuild_from_painted_map/evidence/check.json`
- true: [ ] **No (Jawa) tag remains** in any output file. Evidence: a measured zero over the outputs, with a sanity probe | evidence: `whittle/mineral_sheet_rebuild_from_painted_map/evidence/check.json` `whittle/mineral_sheet_rebuild_from_painted_map/evidence/broaden_attacks.log`
- true: [ ] **Prereview recorded.** The sheet built from these outputs has a passing prereview record | evidence: `whittle/mineral_sheet_rebuild_from_painted_map/evidence/prereview_check.txt` `whittle/mineral_sheet_rebuild_from_painted_map/evidence/harness_summary.txt` `whittle/mineral_sheet_rebuild_from_painted_map/evidence/desk_light.png` `whittle/mineral_sheet_rebuild_from_painted_map/evidence/desk_chg.png` `whittle/mineral_sheet_rebuild_from_painted_map/evidence/phone_light.png`
- true: [ ] **Nothing shipped.** No mod file or deployed def changes (D10 hold). Evidence: the diff stat of the closing commit. | evidence: `whittle/mineral_sheet_rebuild_from_painted_map/evidence/nothing_shipped.txt`

## How each line is shown

- **Regenerates from the repo.** The tool is `src/RimMandrake/Utils/mineral_matrix/gen_matrix.py`. Its round-two
  inputs, byte-identical to Archmagi's originals, are in `design/RimMandrake/mineral_matrix/round_two_2026-10-28/`
  (README.md beside them). The final run was in a shallow clone of the published commit 7d935d3e, started from
  `$HOME`, as one command, exit 0. Seven of the eight outputs hash to the 10-30 build. `column_changes.csv` differs in
  one line, `RM_LongShade pull stays: ''`, which now reads in words. `diff_vs_2026-10-30.txt` shows the diff, and the
  generator checks that undoing that wording gives the 10-30 hash exactly.
- **Rows.** `check.json` comes from `check_matrix.py`, which parses the audit's markdown table itself rather than the
  generator's list: 27 numbered rows plus the 2 "-" rows with an RM_ defName. It finds `biomes.csv` and the matrix
  rows equal to that set, each once. The selftest proves the check refuses a dropped row and an extra twin row.
- **Extras.** `extras_rows.csv`: kind aftermath and cave, painted=no, each with a "not painted: …" mark. The check also
  requires that nothing else is marked.
- **src.** For every row, `check.json` → `src` holds the def file, the label parsed fresh from it, and
  generatesNaturally. The one sheet label that differs from its def is the Warscar ("the Warscar" vs "Warscar"), noted
  per WARSCAR_LABEL_RESTORE_THE_ARTICLE, which is still open.
- **(Jawa).** `check.json` → `jawa_probe` is `[["biomes.csv", 1]]`: the scan found the tag planted in a copy. Then
  `jawa_hits` is `[]` over the 12 output files. `broaden_attacks.log` T6 plants one in `reach_summary.csv` of a real
  run and the check fails on it, then passes on a clean regeneration.
- **Prereview.** `prereview_check.txt` shows `check` OK on the fresh-clone sheet with the committed record: 29 rows,
  24 OK, 5 FLAG, 0 dropped. Two fresh Opus judges passed all 29 rows; the record carries their notes. The browser harness passed
  59 of 59 checks. The five flags are decisions for the owner, not defects.
- **Nothing shipped.** No commit of this item touched a Defs/, Patches/, About/, Assemblies/ or Textures/ path. No
  deploy, bridge or game command was run.

## What I'm least sure about

- The five FLAG rows are content questions only the owner can answer. **The Stillsand holds no steel**, though D2
  says rocky biomes sit near 10. **The Long Shade loses its twin's krayt-pearl pull.** The other three are the
  Warscar's article, the Grey Sea's 5-vs-3 merge, and the Scald leaving D4. They were carried from round two and the
  sibling repair items; I did not change any value.
- The sheet's live saving into the owner's database is proven only against a mocked `claude.db`. The real artifact
  host was not reachable from the offline lane.
- Whether an `=`-leading label becomes a formula in the exported xlsx was not tested (BROADEN.md).
- The six new `.py` files are DIRTY under `code_review_status.py`: no separate full-file review has run.
- Housekeeping: this Whittle's `DONE.md` and `JUDGE_PROMPT.md` were laid down as 0-byte files (the loop skips files
  that exist). The judge was briefed with the loop's template `JUDGE_PROMPT.md`, with its paths pointed here: the
  same text the loop lays for every item. I did not edit the file.
