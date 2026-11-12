# Broadening the testing (2026-11-11)

## The question (to GPT, `gpt_consult.py --codex wsl`, model gpt-6.1-sol, job consult-20261111-201726-21864-f12c62)

I gave it the statement's six claims and what had been tested so far: the generator run against today's `src/` (all 8
outputs byte-identical to the 10-30 build); an independent checker that parses the audit's markdown table, resolves
each row's def file, checks the extras' marks and scans every output for "(Jawa)" after a planted probe; a selftest
proving the checker refuses 6 mutants; a 56-check headless-Chromium harness; a fresh Opus judge on all 29 rows; a
passing `prereview.py check`. Then I asked: *what would a real user try that we have not (someone new, someone
experienced, someone trying to break it, a messy real case)? The 5 most revealing concrete tests, ranked.*

## The answer (verbatim, abridged to the five items)

1. **Truly fresh clone:** run the documented command from outside the checkout, with the original scratch directory
   unavailable and only documented dependencies installed. Require all eight manifest hashes to match.
2. **Source disappears mid-workflow:** in a disposable clone, delete a referenced BiomeDef and rerun with existing
   outputs present. Require an actionable failure and no partial replacement or stale outputs presented as a success.
3. **Stale approval attack:** change one nonzero cell while keeping the passing pre-review JSON. `prereview.py check`
   must reject it.
4. **Real persistence under contention:** two tabs against the real database, edit the same row, interrupt a save.
5. **Hostile but valid labels:** BiomeDefs with commas, quotes, HTML markup and a leading `=1+1`. Require exact CSV
   round-tripping, literal HTML display, and spreadsheet cells that cannot run as formulas.

## What I tried and what I found

All in a throwaway shallow clone of the published commit on ext4 (`/home/mandrake/rm/scratch/CLAUDE_STEVEDESKTOP_OFFLINE2/mm_fresh`),
log in `evidence/broaden_attacks.log`.

- **1, fresh clone from outside:** cloned the published commit, ran `python3 <clone>/src/RimMandrake/Utils/mineral_matrix/gen_matrix.py`
  from `$HOME`. Nothing on Archmagi or in any scratch folder is read; the code names no `/mnt` path (grep).
  `ALL CHECKS PASS`, exit 0 (`evidence/fresh_clone_run.log`). 7 of 8 outputs hash to the 10-30 build. The eighth,
  `column_changes.csv`, differs by one deliberate wording fix, and the generator proves that is its only difference
  (`evidence/diff_vs_2026-10-30.txt`).
- **2, a def vanishes:** removed `RM_Webwork_Biome.xml` with a passing run's outputs in place. The run stopped (exit 1)
  and **the output folder was left empty**: the generator clears its own old outputs before reading anything, a change
  this test prompted. The message used to be a Python traceback. It is now one line:
  `gen_matrix: STOPPED (outputs incomplete; no older run left beside them): ('no BiomeDef in src for', {'RM_Webwork'})`.
- **3, stale approval:** changed RM_Cauldron's cave_crystal 0.3 → 7 in the round-two input and kept the judged record.
  `prereview.py check` REFUSED: "RM_Cauldron: changed since it was looked at". The generator exits 4, and its 10-30
  comparison names 3 UNEXPLAINED files.
- **5, hostile label:** set the Wastes def label to `=1+1, "the" <b>Wastes</b>` (XML-escaped). The CSV round-trips
  exactly through `csv` and the checker passes, because it is the def's own label. The record is refused, since the
  row changed. The browser harness (58 checks at that point) passed, including "row labels = src labels" by `textContent`, so the markup
  shows as literal text. **Not tested:** whether SheetJS writes `=1+1` as a formula in the xlsx. `aoa_to_sheet` makes
  string cells, but I did not open the exported file to look.
- **4, live database contention:** not tried. The offline lane cannot open the sheet inside a live Claude artifact
  host, and the harness uses a mocked `claude.db`. The pre-review record tells the owner so.

The fresh judges added two problems a reader would see, both fixed and now checked by the harness. Column headers
were cut short ("live pattern m…"), and the Changes tab showed raw ids and a bare `''`. The harness now holds three
more checks: no header cut short, no bare `''`, and every old row named by what it was. Each one failed on the
page as it was before its fix (run on it).
