# Polish beside design/specs/2026-11-25-stevedesktop-work-vetted/boundary.md

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- `src/RimMandrake/Utils/maturation_now.py` `switch_line`: the import of `host_work_switch` and any `H.load()` error other than Unreadable are outside the try; not handled (for DOES NOT SURVIVE): a `host_work_switch.py` that fails to import stops the whole MATURATION_NOW build.
