## spec
`art.py enact` (src/RimMandrake/Utils/art/enact.py, commit 93d799120b) installs a schema-1 `decision` letter at the lane it had
on the sheet he clicked on, even when today's rebuild moved that letter INTO A DIFFERENT LANE THAT STILL EXISTS. The case:
the ruled build had Y in the adult lane `swanimals/Kite/Kite`, today's build files Y under `swanimals/Kite/Kite_young`.
Enact plans Y's bytes at `swanimals/Kite/Kite_east.png` and reports it only in `lane_resolved` (no conflict). Cause:
`resolve_ruled_lane` answers "same" because the adult lane still exists, so `moved_in()` is never asked.

The same click recorded as schema 2 (`slots[adult].pick = Y`) is REFUSED by the slot-membership guard (7188fd52f9). Two record
shapes of one click get opposite outcomes, and the one that installs is the young-into-adult wrong-texture class the guard was
written against. A rebuild that moves a letter between two existing lanes is usually a CORRECTION of where it belonged.

Not edited by the reviewer: selftest_enact_stale_lane.py case 4 asserts this behaviour on purpose, and the real dry run showed
0 installs through this path today. Severity high (wrong texture if it ever fires).

Evidence: /home/mandrake/.seat-tmp/FOUNDRY/probe/p1.out (schema 1 installs Y at Kite_east.png; schema 2 refuses the same pick).

## failing test (sketch)
In selftest_enact_stale_lane.py, case 4 as it stands, but assert the opposite:
    history[:] = [older({"A": AD, "B": AD, "C": AD, "Y": AD})]      # he saw Y in the adult lane
    r, inst = plan({"schema": None, "decision": "Y"})                # today Y is in Kite_young
    assert not any(i["letter"] == "Y" for i in inst)
    assert any(c.startswith("RSW_Kite: pick Y") and "Kite_young" in c for c in r["conflicts"])
Today: Y is planned at swanimals/Kite/Kite_east.png, conflicts empty.

## verify
Fix: in the schema-1 re-route, when the ruled lane != today's lane and BOTH lanes exist today, refuse by name (as the
schema-2 guard does) instead of installing at the ruled lane. Keep the proved-rename case (ruled lane gone today) resolving.
Update case 4 and its docstring line; run --only selftest_enact_stale_lane selftest_enact_slot_membership selftest_enact.
