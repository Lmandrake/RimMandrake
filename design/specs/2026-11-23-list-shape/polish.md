# Polish: the List Pipeline's Shape stage (a record; nobody works it)

- `write_fields` records the item check's `seen` as "fails" also when every check part came in by its `holds_why`.
  Nothing decides on that reading.
- `effect --clear` on a shaped item leaves it "shaped already", so `shape --enter` says it needs no Shape run. Shape it
  again with `--parts`, or give it a check.
- A part whose check is the item's own `holds` command runs itself without end. On a first shape the gate refuses it; on
  a re-shape it does not.
- A live Shape run whose split is all routed fills no lane slot until it ends.
- A malformed `shape_from` raises in `due`, so the tick fails with a traceback.
- `list_dispatch.brief_text` puts the check in single quotes; a check that holds single quotes prints a command line that
  does not run as written.
- A part that holds both a check and a full route keeps the check; its route is dropped at the write and no note says so.
- A due item whose script was refused is tried for adoption again after each new event on the item, also while its Shape run
  is live; that tick reads `adopt_refused` instead of `live`.
- A Work run that shapes the item again with the default `--size small` makes an earlier `large` Shape run count as a Work
  run. No brief asks a Work run to shape.
- A routed item with no check that another party claims reads `claimed`, not `routed`, until the lease ends.
