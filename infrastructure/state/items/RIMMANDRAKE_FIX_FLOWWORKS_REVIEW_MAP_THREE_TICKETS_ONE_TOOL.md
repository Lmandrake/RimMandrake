## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks review map: three old tickets on one tool (signs over unbuilt scenes, 39 things still unshown, stations with no hose lead-out).

## merged tickets

- `RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES` (proposed): owner_review_stage.py signs scenes it did not build: 11 sluice 'held open' reads closed; 17 '0.2 m' is 0.5 m holes with 0.5 m water; 24-27 four looks never picked (objects_sheet.choose_look run=True wants a 'whole connected run' row the pipe menu no longer has, objects_sheet.py:175 vs PipeLook.cs:181); 40-41 trench shooter has no ranged weapon; 59-60 jetties dragged 4 squares out past JettyMaxCells 2 and refused, and proof() logs only replies starting REFUSED so 'JETTY ok=False' went unseen. Add his request: two water heights across the closed sluices at 9 and 10. Acceptance test: selftest_owner_review_stage.py gains cases for jetty drag <= JettyMaxCells, an 'ok=False' proof reply landing in NOTES, and choose_look picking a bare '<Look>' row; then a restaged map reads 11 open=True, 17 water 0.2 m, 24-27 four looks read back, 40-41 cover proof run, 59-60 parts > 0, 9-10 two levels
  - sweep reading: Partly fixed 2026-11-21 (af8babff42 pipe looks pick the bare whole-run row; 02df5f8f4a jetties drag 2 squares; stations 40-41 passed his look 2026-11-22); still open by the 2026-11-22 walk: station 47 a sign with nothing staged; 11 sluice open, 17 0.2 m and 9-10 two levels not re-read
  - its check: selftest_owner_review_stage.py has cases for jetty drag, an ok=False proof reply landing in NOTES and a bare <Look> row; the restaged map reads 11 open=True, 17 water 0.2 m, 9-10 two levels across the gate, 47 staged; no station is signed without its scene
  - files: `src/RimMandrake/FlowWorks/northstar/owner_review_stage.py`, `src/RimMandrake/FlowWorks/northstar/objects_sheet.py`
- `RIMMANDRAKE_COVER_FLOWWORKS_REVIEW_MAP_THIRTY_NINE_STILL_UNSHOWN` (proposed): FlowWorks selftest_review_map.py is red on main: 43 inventory items match no FEATURES rule in review_map_coverage.py (39 after this run covered 5)
  - sweep reading: ran src/RimMandrake/FlowWorks/selftest_review_map.py on HEAD: rc=1 FAIL, 5 uncovered now (JobDef/JoyGiverDef RM_SoakInGeyserPool, ThoughtDef RM_BathedInTar, a HediffDef; all Defs/Pits/GeyserPool, the inv_geyser_tub bar); output /tmp/fwsweep/s00/review_map_run.txt
  - its check: selftest_review_map.py passes with 0 uncovered
  - files: `src/RimMandrake/FlowWorks/selftest_review_map.py`, `src/RimMandrake/FlowWorks/review_map_coverage.py`
- `REVIEW_MAP_FIX_STATIONS_NO_LEAD_OUT` (proposed): review_map: stations 63/66/67 hose lays refused (no straight lead-out); stations 35/36 Ladder never reads Ladder up
  - sweep reading: review_map.py (still the live look map, touched 3dbd3822bd 2026-11-13) refused stations 63/66/67 hose lays (layOk false, no straight lead-out) and stations 35/36 never read 'Ladder up' (bridge run 1, 2026-10-24); no later fix recorded
  - its check: review_map build on a fresh quicktest: every station hose lays with layOk true and stations 35/36 read 'Ladder up'
  - files: `src/RimMandrake/FlowWorks/review_map.py`

## his words (as recorded on the merged tickets)

- on `RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES`: Station 47 has nothing prepared for me.

## verify

Acceptance test: none as one command, selftest_review_map.py and selftest_owner_review_stage.py carry the cases (each merged ticket above names its check).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES
item: RIMMANDRAKE_COVER_FLOWWORKS_REVIEW_MAP_THIRTY_NINE_STILL_UNSHOWN
item: REVIEW_MAP_FIX_STATIONS_NO_LEAD_OUT
