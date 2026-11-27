## spec
A work bundle that ends files the fresh reader of its fixes (`work_bundle.reader_step`). When the worker already filed
the reader of the bundle's last fix sha, the bundle's filing reused that ticket id: `rimflow file` refused it (exit 2,
the name exists), and the bundle printed "was NOT filed (2); file it by hand". The hand act it named (`fresh_reader.py
file --fix <sha> ...`) is refused the same way. Seen 2026-11-27 for b553269938 and 5f4a5eaecc. The bundle also named a
file (JawaBenchWorldTools.cs) under a sha that did not change it (it changed at fa9a5f4176).

Fix, test first:
1. `fresh_reader.py file` for a fix whose reader ticket exists and names each file is not a refusal: exit 0, and it
   names the ticket. Files that no reader ticket of that fix names are filed under a twin id, never the taken id.
2. The bundle files one reader per fix sha, with the files that sha changed (each file under the newest bundle commit
   that changed it). A reader ticket that exists counts as filed: no "file it by hand" line for it.

## refs
file: src/RimMandrake/rimflow/fresh_reader.py
file: src/RimMandrake/rimflow/work_bundle.py
file: src/RimMandrake/rimflow/selftest_fresh_reader.py
file: src/RimMandrake/rimflow/selftest_work_bundle.py

## verify
`python3 src/RimMandrake/rimflow/selftest_fresh_reader.py` (case t_a_second_filing_for_one_fix_is_not_a_refusal, red on
the base) and `python3 src/RimMandrake/rimflow/selftest_work_bundle.py` (case t_a_code_bundle_gets_one_fresh_read).

## criteria
Every case of both selftests PASS; the new case is seen red on the base.
