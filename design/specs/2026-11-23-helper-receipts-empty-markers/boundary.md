# BOUNDARY: the helper receipts of dead windows, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/helper_receipts.py` (`collect`, `open_receipts`, `ack`, `empty_path`, `harvest`, `_read_main`). Items: `RIMMANDRAKE_SPLIT_EMPTY_RECEIPTS_BEAT_READ_783_NOTHINGS`, `HELPER_RECEIPTS_FOREGROUND_FIX_UNREAD_SKIP`.

## ACCEPTS
- A seat's project folder of window transcripts (`*.jsonl`), each with an optional `subagents/` folder.
- A receipts folder per seat that holds `<session>.json` (a receipt with findings) and `<session>.empty` (a window read with no findings). Measured 2026-11-23 on BENCH: 801 files, 783 of them empty markers in the old `.json` form.

## DOES NOT SURVIVE
- A Dispatcher that runs code from before this page while a newer tool renames the markers: the old `collect` does not see a `.empty` file and reads that window again. Migrate only after every clone has this code.

## PROMISES (tests of the same name in `src/RimMandrake/rimflow/selftest_helper_receipts.py`)
- **empty-markers-are-not-reread**: `collect` writes a window with no findings as `<session>.empty`, never `.json`. `open_receipts` opens no `.empty` file, and renames an empty `.json` from before this page to `.empty` the first time it reads it. `collect` counts a `.empty` file as seen and does not read that window again. A receipt with findings still reads open.
- **foreground-result-needs-assistant**: `harvest` counts a foreground helper's result as read only after a later assistant record. A finished helper's unread report appears in the receipt even if a user record or a torn line follows the result.
