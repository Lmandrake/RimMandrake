# ENACT_ALIAS_KEEP_FIX_BLOCKS_NEWER_PICK

Found in the enact_vet5 review of 8fa14fcec6 (FOUNDRY, 2026-10-24).

## Defect
`keep_blocks_pick` (enact.py) treats a keep from ANOTHER row as always blocking. A row that was renamed keeps its
old keeps under the OLD row name, so the old keeps block his newer pick and his ✕ on the renamed row, with no end
date. Picking again does not clear them, because the keep's row never equals the new row.

Live case, owner_escalations_leaningscrub_2_sheet_2026-10-24 (dry run, /home/mandrake/.seat-tmp/FOUNDRY/enact_vet5/ls2_dry.json):
- RM_TunnelSnake B (2026-10-24): east and south were refused. The live files hold 5f5c9c531370 / d19250d2b134, which
  are owner-kept by row **RSW_TunnelSnake** col A via leaningscrub_sheet_2026-10-05. Those keeps are a9f4747ad67919c81b4d
  and 9ca52399d9a90ca7b651. His ✕ on the same shas is also refused ("not purged — owner-kept").
- RM_Vurra B: east was refused. The keep is by **RSW_Vurra** col B (c66dc2358dc84c12bc9c, b1330cfa36299d8ef0a5), same via.
Since the partial-pick fix that ships with this item, both picks are refused whole, so there is no wrong art. They
still cannot be installed.

## Fix direction
Treat a keep whose row is an alias of this row the same as a same-row keep: it blocks only when it is newer. Alias
means a carriedFrom/census rename, or the same defName with RSW_ swapped for RM_. Never guess the alias: read it from
the census or the snapshot `carriedFrom`. A real other row (a different creature sharing the picture) still blocks.

## Failing-test sketch (selftest_enact_stale_lane.py, beside case 14)
Patch `L.Index.protected` to return the keep `{"target": {"row": "RSW_KiteOld"}, "at": "2026-10-05T00:00:00Z", "via": "old.decisions.json"}`
for the live east sha. Record RSW_Kite as an alias of RSW_KiteOld, in the same form the census uses. Plan
`{"decision": "B"}` at 2026-10-10.
- Expect: B installs at every facing.
- Control: with the keep at 2026-10-11 (newer than the pick), it is refused whole.
- Control: a non-alias other row still blocks.
