# Polish: the family cleaner

- `src/RimMandrake/Utils/family_clean.py`: a folder whose removal fails part way keeps its last files and gets a new
  modified time, so the next runs read the folder as YOUNG and leave it for 14 days. Measured 2026-11-25: 13 removals
  failed on drive errors in the first run; the run of 4:52 PM PST read the leftovers YOUNG (about 20 MB in four
  folders that were checked). A failed removal could be retried on the next run without the age line.
