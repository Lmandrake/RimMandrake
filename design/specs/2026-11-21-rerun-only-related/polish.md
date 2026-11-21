# Polish: the change relation (no ticket; a record)

- C# relates by source file only: a one-line call added to RM_MapComponent_CordGraph.cs reruns every check that declares that file (sc_switch_off_ends on 2026-11-21). A member-level C# relation would be finer; not worth the touch now.
- `acceptance/guard_judge_certificate_accept.py` run without `--red-seen` reads 14/18 on origin/main before this change too (the pipeline runs it with `--red-seen`: 28/28).
- Pyrelands `P_mapgen_log` may be a whole-mod log check; its table text does not say, so it has no `"*"` declaration.
