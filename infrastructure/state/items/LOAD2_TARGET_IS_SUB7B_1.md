## spec
`rt_probe.rws` aborts its load on the 578 set — see `RT_PROBE_LOAD_ABORTS_ON_578_1`.
`WORLDMAP_gen_sub7b.rws` is the correct target and the reasons are structural:
  planetCoverage **1** · subdivisions **7** ⇒ the 21,872-tile MLP-7 geometry the
  CSVs are named for · **0 pawns** · **0 settlements** · no map component · 11.9 MB
  against rt_probe's 23 MB.
🔑 Zero pawns is the point. rt_probe's abort came with dozens of
`Could not find think node with key …`, and it carried ~250 scratch pawns from the
race lineup and the weapon sweep. A world with no pawns cannot fail that way.
📌 It also satisfies W9's own `Find.CurrentMap == null` precondition, which every
run so far has knowingly violated.

## verify
after loading: `list_debug_action_children("Actions")` enumerates, and
`world_info_get.tilesCount == 21872`. `w9_run.py` asserts both before it writes.

## criteria
`python.exe src/RimMandrake/Utils/w9_run.py --apply --load WORLDMAP_gen_sub7b`
completes with stage 2 (links) reporting rivers and roads > 0 — that is the
untested fix finally exercised — and a screenshot to compare against the reference.

## notes
**from:** CHECK, 2026-08-20, chosen by reading the save headers offline rather than by
loading one and finding out.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
