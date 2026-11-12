# Notes (newest first)

## 2026-11-11 19:52 -0800 — picked by CLAUDE_STEVEDESKTOP_FWLIVE (SETUP)
- Runs so far: 0 (`wc.py nonpass` = 0). Built 9a463b5bf3 (selftest clean mark); 5b3a342a76 added the `--prove` gate and
  the look read-back fix (": this tank" tail stripped); 20571d33f1 pinned ford/weir-style verdicts in a selftest.
  Relentless started it 2026-11-03 but never ran it live.
- Proof script: `src/RimMandrake/FlowWorks/northstar/objects_sheet.py` (456 lines; ~6-8 min live). `--mock` proves the
  script offline in seconds. `--prove` exits 0 only when every row MATCHES and each group has its rows and picture
  (`prove_verdict`, line ~344); verdict in `<out>/prove.txt`, out = `Transient/fw_scenes/live/objects/` in Steve's clone.
- Site: the river groups need moving river water. Run `river_site.py` first (founds a colony on a mild river tile,
  makes that map current) — otherwise river_weirs/river_fords read "this map has no moving river water" and the prove
  fails on a SITE fault, not a MOD fault.
- Selftests that touch it: `selftest_fw_walks.py`, `selftest_water_walks.py` (both in FlowWorks/northstar).
- Game: SteveDesktop game A via `infrastructure/whittle_claude/steve.sh` (sync / deploy / up / run / fetch). Never
  Archmagi's game. Classify each non-MATCHES row MOD, SITE or HARNESS before changing anything.
- The criterion text in the ledger is truncated at 160 chars; STATEMENT.md fills the rest from `EXPECT` in the script,
  which is what `--prove` actually checks.
