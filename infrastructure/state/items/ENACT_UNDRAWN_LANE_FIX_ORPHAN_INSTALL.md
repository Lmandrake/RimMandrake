# ENACT_UNDRAWN_LANE_FIX_ORPHAN_INSTALL

Found in the ENACT_KEYED_FIX_UNREVIEWED review (FOUNDRY, 2026-10-24).

## Defect
`build_plan` accepts a clicked lane as current whenever a file of ours still ships at it (`ships()` / `slots_for`),
even when no def draws that texPath any more. bridge_art_redraw_sheet_2026-10-21: he clicked the anchors'
Heavy/Steel/Timber B of each look under the shared lane `.../SuspensionBridge/<Look>/RM_SuspensionAnchor`
(2026-10-22T06:10Z). Wave 2 (4e049d8bdb) then repointed the style defs to per-material lanes
(`RM_SuspensionAnchor_Heavy|Steel|Timber`), by hand. The old shared files still exist; only `uiIconPath ..._north`
names them. A re-enact therefore plans his picks onto the old shared `_south.png`, which nothing draws, and leaves the
drawn per-material files untouched. Before the shared-file collision guard (same review), it also kept only the last of
the three picks.

The collision guard now refuses these 12 installs (realdiff2 evidence). The lane is still wrong for any
SINGLE row whose lane went undrawn this way.

## Failing-test sketch (selftest_enact_stale_lane.py)
In the fixture, keep the live files at `swanimals/Kite/Kite_*.png`, but make the row's def texPath (the `res` and
`graphic_of` in today's snapshot) name `swanimals/Kite/Kite_Heavy`. Record a schema-2 slot `{swanimals/Kite/Kite: B}`.
Expect: nothing installs at `swanimals/Kite/Kite_east.png`. The plan either resolves to `Kite_Heavy_*` (a proved rename)
or lists a named conflict. Today it installs at the undrawn file.

## Evidence
- /home/mandrake/.seat-tmp/FOUNDRY/enact_vet4/collide.txt (8 collisions, all on bridge anchors)
- /home/mandrake/.seat-tmp/FOUNDRY/enact_vet4/realdiff2.txt
- src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionStyles.xml:333-415
