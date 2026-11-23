# Result: `RIMMANDRAKE_REWRITE_SEVEN_SMALL_UNDATED_FACT_FILES`

Part of batch `RIMMANDRAKE_REWRITE_UNDATED_FACT_FILES_DATED_ONES_STAY` (`batch_plan.md`, order 15). Run 2026-11-23. Files:
seven files in `infrastructure/state/facts/`. Special rule: these files are homes for evidence. Keep each measurement.
The STE target binds only their rule bullets.

Base: 2093cc9e104754d6f0b11cc6a90984e4c65a3490

## Scores

The scores are of the whole file, evidence included. "long" is sentences over 20 words. "flags" are the mechanical flags.

| file | bytes | STE before | STE after | long | flags |
|---|---|---|---|---|---|
| `distress_signals.md` | 5,813 → 6,849 | 4.74 | 2.35 | 14 → 6 | 12 → 7 |
| `dump-is-pre-cherrypicker.md` | 5,165 → 5,741 | 4.42 | 2.75 | 17 → 8 | 14 → 13 |
| `biome_paint_list.md` | 10,790 → 11,532 | 3.97 | 2.11 | 11 → 3 | 5 → 6 |
| `biome_rosters.md` | 5,780 → 6,693 | 2.71 | 0.66 | 8 → 1 | 5 → 4 |
| `naming_inventory.md` | 7,033 → 7,165 | 3.01 | 2.47 | 7 → 5 | 7 → 8 |
| `clone_memory_peak.md` | 4,291 → 4,773 | 2.95 | 0.64 | 13 → 3 | 2 → 1 |
| `almost_out_codex_log.md` | 12,791 → 13,781 | 3.35 | 2.91 | 1 → 0 | 6 → 6 |

- `dump-is-pre-cherrypicker.md` (2.75) and `almost_out_codex_log.md` stay above 2.5. Their violations are in evidence,
  quotes and log cells. No "rule text" score was measured.
- Two files gained one mechanical flag. `biome_paint_list.md`: a `pronoun` flag on "The two that do not are 18404 and
  21915" (one bullet split from one sentence). `naming_inventory.md`: a `shout` flag, because one line with two marks
  became two lines. The ⚠️ and 🔴 marks that stay are severity marks of the old text.

### The long sentences that stay, by kind

- **Two short sentences that the lint joined at a bold lead:** `distress_signals.md` 17, 69, 73, 79, 115;
  `dump-is-pre-cherrypicker.md` 6, 52, 62, 86; `biome_paint_list.md` 16; `naming_inventory.md` 98, 103, 127;
  `clone_memory_peak.md` 41.
- **A quote or a notice that a tool made:** `dump-is-pre-cherrypicker.md` 12, 35, 93; `clone_memory_peak.md` 1.
- **A sentence that holds a path, a command or a list of names:** `distress_signals.md` 81;
  `dump-is-pre-cherrypicker.md` 54; `biome_paint_list.md` 88, 116; `biome_rosters.md` 104; `naming_inventory.md` 56, 82;
  `clone_memory_peak.md` 61.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| `distress_signals.md`: "Feeds the BENCH scan in `infrastructure/agents/REP.md`" | REP is retired; where the scan is | says that REP is retired; names `rimflow next --bench` |
| same: "a rounded LIFT" | what a lift is | meaning from the file's own figures (42.9 / 8.2 = 5.22) |
| same: "Track detention instead" | what detention is, at first use | meaning from the file's own later heading |
| same: "to get past `COMMIT_GUARD_BLOCKS_SPECS_1`" | what that item was | meaning from its ledger title |
| same: "Useless breadth" | what that says of the signals | one plain sentence |
| `dump-is-pre-cherrypicker.md`: "Cherry Picker", "kill list" | what they are | one sentence, from the skill `rimworld-content-moderation` |
| same: "The numbers below" | the numbers are above | names the three figures |
| same: "The full record is `infrastructure/state/items/…`" | the file is gone | names the commit that deleted it and the `git show` command |
| `biome_paint_list.md`: "R3" | which save | defined at the save |
| same: "twins" | what a twin is | meaning from the rows that `ee7c219b70` removed |
| same: "Counted from the table" (34 NO PAINT) | the table has 9 NO PAINT rows now | says that the twin rows left on 2026-11-06 |
| `biome_rosters.md`: "donor", "this session" | what each is | defined; the date |
| `naming_inventory.md`: "Counted from … (⛔ not from the DLL …)" | who counted, what to do | two sentences |
| `clone_memory_peak.md`: "anon", "file" | what each is | from `clone_mem_probe.py` |
| `almost_out_codex_log.md`: "ALMOST_OUT", "r1", "rev_a", "marked clean" | what each is | defined above the table |

## Repairs of form and of stale facts

- `almost_out_codex_log.md`: four paths held control characters in place of `\r` and `\f`. All four repaired paths exist
  on disk. Three joined rows are three rows again. One row had an extra cell. Eight rows had two missing cells, which
  now read "not recorded". Each row has seven cells now.
- `biome_paint_list.md`: the text said that the repaint still owes the deletion of the 25 twins. Commit `ee7c219b70`
  (2026-11-06) deleted them.
- `biome_rosters.md`: the text said that `RUT_BlueDesert` is frozen in `UtinniPatches`. The same commit deleted it. The
  file now also says which rows were renamed after the measurement.

## The checks, with a planted loss first

For each file, the planted copy lost one named id and one figure. "Check 1" is `checkable.py compare`. "Check 2" is
`rule_doc_lint.py keep`.

| file | planted: check 1 | planted: check 2 | real: check 1 | real: check 2 |
|---|---|---|---|---|
| `distress_signals.md` | 2 lost, exit 1 | 3 lost, exit 1 | 56 items, 0 lost | 111 spans, 0 lost |
| `dump-is-pre-cherrypicker.md` | 1 lost, exit 1 | 3 lost, exit 1 | 17 items, 0 lost | 50 spans, 0 lost |
| `biome_paint_list.md` | 1 lost, exit 1 | 3 lost, exit 1 | 57 items, 0 lost | 180 spans, 0 lost |
| `biome_rosters.md` | 1 lost, exit 1 | 3 lost, exit 1 | 12 items, 0 lost | 128 spans, 0 lost |
| `naming_inventory.md` | 1 lost, exit 1 | 4 lost, exit 1 | 36 items, 0 lost | 169 spans, 0 lost |
| `clone_memory_peak.md` | 1 lost, exit 1 | 3 lost, exit 1 | 67 items, 0 lost | 89 spans, 0 lost |
| `almost_out_codex_log.md` | 2 lost, exit 1 | 2 lost, exit 1 | 43 items, 0 lost | 66 spans, 0 lost |

- Check 1 first read one lost path in `almost_out_codex_log.md`: `D:\ClaudeWork`. That "path" was the part of a broken
  path before its control character. The repair note in the file names `D:\ClaudeWork`, so check 1 finds the span.
- `rule_doc_lint.py selftest` PASS, `checkable.py selftest` 19 of 19, `batch_done.py selftest` GREEN.
- `selftest_biome_paint_list.py` OK, `selftest_fuelsnows_name_cull.py` PASS (both read the paint list),
  `selftest_cli.py` 62/62, `selftest_retired_era_gone.py` PASS. The 38 table lines of the paint list are
  byte-identical.
- People's names: counted per file before and after (owner, Conductor, Steve, Mandrake). No count fell.

## What the meaning read found

Seven fresh Opus readers (rm-judge), one per file, one at a time. No reader got the writer's reasoning. No reader read
the repairs.

| file | finding | repair |
|---|---|---|
| `distress_signals.md` | the pointer to `CONDUCTOR.md` for the triage duty leads nowhere useful | pointer removed |
| same | "fed" for "feeds" | "feeds" |
| same | "The scan is now the query" says too much | "the query computes the index of this file" |
| same | the lift definition covered lifts "against drops" too | limited to lifts of detention |
| same | "death (a drop)" cannot be confirmed | old word "death" back; listed below |
| same | "Contested scope kills work" is weaker than "What kills work is contested scope" | old words back |
| `dump-is-pre-cherrypicker.md` | "the list of defs that it removes" does not fit 1,289 against 1,209 | "is configured to remove" |
| same | "kill-list numbers in this file" could cover the 2026-09-05 figures | names the three figures |
| same | "judging" was lost | restored |
| `biome_paint_list.md` | "state of 2026-11-01" dated a debt that is still owed | removed |
| same | the twin deletion came before the re-stamp, and the draft did not say so | says so |
| same | "works its holes" changed the subject from the biomes to the holes | old words back |
| same | the "admission" sentence left its bullet | nested under its bullet again |
| `biome_rosters.md` | the draft said that the `RM_TheRot` row describes a def that still exists; the census measured `RUT_TheRot` | lists the 5 renamed rows; only `RUT_Umbra` survives |
| same | "the counts of this entry" covered the 2026-09-25 counts too | limited to the tables and the unguarded list |
| `naming_inventory.md` | the reason to re-measure became an aside | written as the reason, with its date |
| same | an open drift became a past one | present tense back |
| `clone_memory_peak.md` | the "anon" gloss was loose; the link between the two-clone lines was lost | both repaired |
| `almost_out_codex_log.md` | no change of meaning; four polish points | three repaired |

The added facts that the readers confirmed stay: each one is from the code, the ledger or git.

## Conflicts (listed, not decided)

1. `naming_inventory.md` says that `CLAUDE.md` calls the faith "the Second Hand". `CLAUDE.md` at `301d1299` and at
   `15a635c7` holds neither "Second Hand" nor "Salvation" (measured 2026-11-23).
2. `naming_inventory.md` serves a rename spec that is to come. Root `CLAUDE.md` says that the rename migration is done.
   The file is then a candidate for deletion or for a HISTORY head.
3. `distress_signals.md` sends the score "to the OWNER and to REP". REP is retired. The code admits BENCH and OWNER.
4. `biome_paint_list.md` lists `DONOR_BIOME_MODS_RETIRE_ZERO_TILES_LEFT` under "still owes". The ledger reads done. The
   file says that the twins are deleted. The item `BIOME_TWINS_RETIRE_TWENTY_FIVE_FROZEN` reads ready. The file leans on
   `BIOME_SPECIFIC_FAUNA_LAW_1`, which reads dropped.
5. `biome_paint_list.md` counts 61 owned BiomeDefs and 27 in `mandrake.rut.patches` (2026-11-01). `src/` holds 36 now.
6. `biome_rosters.md` says "Append only". This batch rewrote its entries, as the item orders.
7. `clone_memory_peak.md` names `min_mem_available_gb`. No `.py` or `.json` file in the repo holds that name now.

## Could not determine

| line | question | who would know |
|---|---|---|
| `distress_signals.md`, "against death" | whether death is all 47 drops or only the 9 failures | the author (REP, 2026-08-23) |
| `biome_paint_list.md`, "a withdrawn *admission*" | what an admission is, exactly | the Conductor |
| `almost_out_codex_log.md`, "P2" | the severity scale of the Codex reviews | the Codex review prompt of 2026-10-25 |
| `almost_out_codex_log.md`, log cells | the cells are terse notes; this run did not rewrite them | the runs that wrote them |
| `dump-is-pre-cherrypicker.md`, "Six other scripts" | which six, and how many today | a fresh grep for the settings file name |

## What this run did not test

- No agent read the new files in real work.
- No reader read the repairs after the meaning read.
- The measurements were not taken again. Each claim stays as the old text stated it, apart from the stale facts listed
  above.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. No quote differs (one match in the list was prose between two quotes).

| file | line read | verdict | what was done |
|---|---|---|---|
| distress | the `CONDUCTOR.md` pointer removed | SAME | none |
| distress | "feeds" | SAME | none |
| distress | "the query computes the index of this file" | SAME | none |
| distress | a lift of detention only | SAME | none |
| distress | "against death", restored | SAME | none |
| distress | "What kills work is contested scope", restored | SAME | none |
| dump | "is configured to remove" | SAME | none |
| dump | the three kill-list figures named | SAME | none |
| dump | "judging", restored | SAME | none |
| paint list | the dated debt removed | SAME | none |
| paint list | the twins left before the re-stamp | SAME | none |
| paint list | "as their own per-biome pass reaches them", restored | SAME | none |
| paint list | the "admission" sentence under its bullet | SAME | none |
| rosters | the 5 renamed rows; only `RUT_Umbra` survives | SAME | none |
| rosters | the dates limited to the tables and the unguarded list | SAME | none |
| naming | the reason to re-measure | SAME | none |
| naming | the open drift, present tense | SAME | none |
| clone memory | the anon gloss and the two-clone lines | SAME | none |
| almost-out log | three polish repairs, the row with its cells in place | SAME | none |
