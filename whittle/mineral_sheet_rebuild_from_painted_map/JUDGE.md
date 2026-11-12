# JUDGE: MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP

Judged 2026-11-11 by a fresh judge that did not build the work. I read STATEMENT.md, NOTES.md and the evidence
folder. I did not read DONE.md, BROADEN.md or the earlier JUDGE.md. I re-ran the generator myself at HEAD 7d935d3e82:
`python3 src/RimMandrake/Utils/mineral_matrix/gen_matrix.py --out D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_STEVEDESKTOP_OFFLINE2\mineral\judge_run3`
(run from $HOME, exit 0, log `...\mineral\judge_run3.log`). I then checked its outputs with my own script, separate
from the builder's check_matrix.py.

## Statement lines

1. **Regenerates from the repo: true.**
   - `git ls-files` shows gen_matrix.py, check_matrix.py, the page builder and template, and every input committed:
     the five round-two CSVs under `design/RimMandrake/mineral_matrix/round_two_2026-10-28/` and the audit file.
   - The run tree is clean: none of these paths is modified.
   - In the generator and page scripts, the only mention of ClaudeWork or Archmagi is a provenance comment
     (gen_matrix.py:24). No path is read from a seat clone or from ClaudeWork.
   - My run wrote all the CSVs. I compared them myself with `diff` against the copied 2026-10-30 build. These match
     byte for byte: biomes, draft_matrix, reasons, mineral_homes, inventory, reach_summary and stats.json.
   - Only column_changes.csv differs, by one line. That is the RUT_Desert krayt-pearl note: the old text
     `pull stays: ''` (a repr of an empty string) is now a plain-words sentence. The change is explained in
     evidence/diff_vs_2026-10-30.txt and is a wording fix only. No number changed.

2. **Every painted biome has a row: true.**
   - I parsed the audit's "authoritative biome list" table myself: 27 numbered rows plus the 2 extras, 29 in all.
   - My biomes.csv has 29 unique rows. The symmetric difference with the audit set is empty.
   - draft_matrix.csv has the same 29 biome rows plus 4 `SRC_` rows. Those are the other-source rows (asteroid,
     meteorite, salvage, trade), not biomes.

3. **The two extras are marked: true.**
   - Only RM_ChillCrater and RM_LanternDeeps have `painted=no` and a non-empty `mark`.
   - RM_ChillCrater: "aftermath biome (generatesNaturally=false)".
   - RM_LanternDeeps: "cave layer injected under cold maps, not a worldmap biome".
   - Source: evidence/extras_rows.csv, which my run reproduces.

4. **Every row's `src` names a real source: true.**
   - For all 29 rows I opened `src_def` and found the matching `<defName>`. Each `src_label` equals that def's
     `<label>`.
   - One shown label differs from its def: RM_Warscar is shown as "the Warscar" while the def says "Warscar".
   - This is disclosed in `label_note`, made under the ledgered WARSCAR_LABEL_RESTORE_THE_ARTICLE item, flagged to
     the owner on the sheet, and the def's own label is kept in `src_label`. So no label is invented.

5. **No (Jawa) tag remains: true.**
   - My own scan of every file in the output folder found zero `(Jawa)` in the data and page files.
   - It found 2 hits, both in check.json. Both are the check's own description text ("no '(Jawa)' tag ..."), not
     data.
   - My scan can see the tag: it found 17 "Jawa" in the audit file. The builder's planted-tag probe passed in my run,
     and broaden_attacks.log T6 shows the check failing on a tag planted in reach_summary.csv.

6. **Prereview recorded: true.**
   - `prereview.py check` on my freshly built `page/index.html` says OK (exit 0): 29 rows, 24 OK, 5 flagged for the
     owner, 0 dropped.
   - The committed record `design/RimMandrake/mineral_matrix/index.prereview.json` is byte-identical to the one my
     run placed beside the page.
   - T3 in broaden_attacks.log shows the record refuses a changed cell, so it is not a rubber stamp.

7. **Nothing shipped: true.**
   - I listed every path in the item's 8 commits since 52c51a89cf: 37 paths. None is under Defs/, Patches/, About/,
     Assemblies/, Textures/, Languages/ or Sounds/.
   - Everything is design data, Utils scripts, lessons and whittle evidence.
   - The wider range does contain mod-file changes, but they are from other items' commits.
   - The statement asks for "the closing commit's diff stat". There is no closing commit yet. The per-commit path list
     in evidence/nothing_shipped.txt is the stronger evidence, and I confirmed it.

## Where the evidence looks staged or flattering

- The desktop screenshots show a sheet that is already in use. The Changes tab reads "9 changes saved so far": those
  are the browser harness's own edits against a stand-in database.
- The grid screenshot stops at the header, before any biome row, so it shows layout but not the rows themselves.
  I judged the rows from the CSVs instead.
- Live saving is proven only against a stand-in database. The sheet says so itself; it is not a statement line.
- The prereview judges were commissioned by the builder. Their record's hash still matches the outputs, and the
  record refuses a changed row.

None of this changes a verdict above.

would show: yes
