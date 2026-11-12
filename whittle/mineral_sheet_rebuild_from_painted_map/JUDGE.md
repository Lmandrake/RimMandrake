# JUDGE: MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP (fresh-eyes judge, 2026-11-11)

Read: STATEMENT.md, NOTES.md, evidence/*.txt, *.log, extras_rows.csv, check.json, desk_light.png, desk_chg.png.
Not read: DONE.md, BROADEN.md, judge1/judge2 verdicts, broaden_attacks.log.
My own run: `gen_matrix.py --out D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_STEVEDESKTOP_OFFLINE2\mineral\judge_run2`
from the clone at HEAD 00b0c15a9f (on origin/main, mineral_matrix paths clean in git status), exit 0. I then compared
the files myself with `cmp`/`diff` against the 2026-10-30 copy, separately from the script's own comparison.

| Line | Verdict | What shows it |
|---|---|---|
| Regenerates from the repo | true | gen_matrix.py, check_matrix.py, page/*, and the round-two inputs are tracked (17 files under `src/RimMandrake/Utils/mineral_matrix` + `design/RimMandrake/mineral_matrix`). No hard-coded ClaudeWork, seat or /mnt path appears in the code; the only mentions are docstring history. The default output is `<repo>/Transient/`. My run: biomes, draft_matrix, reasons, mineral_homes, inventory, reach_summary and stats.json are byte-identical to the 10-30 copy. column_changes.csv differs in one line (RUT_Desert krayt-pearl note: the old `RM_LongShade pull stays: ''` is now plain words). That matches diff_vs_2026-10-30.txt and its explanation. fresh_clone_run.log shows the builder's fresh-clone run. |
| Every painted biome has a row | true | I parsed the audit's "authoritative biome list" myself: 26 RM_ rows + RUT_Umbra (row 23, which the audit marks as the biome itself, not a twin) = 27. biomes.csv has 29 unique rows: those 27 + RM_ChillCrater + RM_LanternDeeps. None is missing and nothing else is there. |
| The two extras are marked | true | extras_rows.csv and my biomes.csv: both rows have painted=no and kind aftermath / cave, with a mark saying why. painted=yes on all 27 others. |
| Every row's src names a real source | true | My own script: every src_def file exists and holds `<defName>` = the row biome, and its `<label>` = the row label in 28 of 29 rows. RM_Warscar shows "the Warscar" where the def says "Warscar". This is disclosed in the row (src_label=Warscar, label_note cites the 2026-09-26 the-Xxx ruling, which biome_mod_architecture.md §7 Q5 confirms as owner-reversed to "the Warscar"), and it is one of the 5 rows flagged for the owner. Note: the builder edited audit row 9 from "the Gelatinous Slime" to "the Slime" (d16950e9a9). The def really says `<label>the Slime</label>`, so the edit corrects the audit. It does not touch the row set. |
| No (Jawa) tag remains | true | check.json: 12 output files scanned, 0 hits, and a planted probe in biomes.csv was found (1 hit). My own grep: "(Jawa)" appears only in check.json (the check's own text). The plain "Jawa" hits in inventory.csv are the source-mod name "Jawa Armoury Rebalance", not a tag. |
| Prereview recorded | true | My own `prereview.py check` on my run's page/index.html: OK, 29 rows (24 OK, 5 FLAG), exit 0. The row fingerprints match freshly generated rows. |
| Nothing shipped | true | All 6 item commits since 52c51a89cf touch 18 paths, all in design/ or Utils/. None is under Defs/Patches/About/Assemblies/Textures. The closing commit 00b0c15a9f changes only index.prereview.json (1 line). |

Staged or flattering evidence:
- desk_chg.png shows "9 changes saved so far". The harness made those edits against a stand-in database. The prereview text says so: live saving is proven only where the owner opens it.
- The screenshots are stills of a static sheet, which is the right medium for a table.
- The "two fresh Opus judges" claim in the prereview record is the builder's own pipeline. I did not rely on it. My verdicts above come from my own run and checks.
- The owner's xlsx (10-30 copy) is untouched by this run, because gen_matrix writes only CSV + page.

would show: yes
