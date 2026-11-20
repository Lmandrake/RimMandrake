# RIMMANDRAKE_BLOCK_SLACK_ROOF_OVER_POLE_KEEP_THE_CUT

Gimme Some Slack **0.1.1** (his card of 2026-11-20). From his walk of 2026-11-20: `design/RimMandrake/validation_holding/gss_walk_20261120.md` row #14.

## spec

He said a pole must not end up inside a roofed building, and the roof cut stays in code ("nice test if you ever did, you can
leave the behavior in the code, just disable building it that way"). The masts already carry `PlaceWorker_NotUnderRoof`
(`src/RimMandrake/GimmeSomeSlack/Defs/Aerial/RM_AerialAnchors.xml:47`), which refuses only a roof that stands at
placement. A roof built later is not refused: a hand-placed build-roof area, and vanilla's auto-roof over a closed room,
since the masts do not set `building.allowAutoroof` false (vanilla `AutoBuildRoofAreaSetter.cs:55`) [measured]. Fix:
`allowAutoroof` false on every standing mast, and refuse a roof over a mast's cell (the build-roof designator and the
roof job), with a message that names the pole. Keep the cut (`Source/Aerial/RM_MapComponent_Aerial.cs:407`, verdict
`Roofed`) for roofs that still come (a mod, a collapse, god mode). Change station 16's "roof the room" poke in
`human_review.py` and `review/KEYSHEET.md` to "a roof is refused". The wall bracket is outside this: it hangs on a wall.

## verify

Live: a mast in a closed, unroofed room; wait for auto-roof; then designate build-roof over the mast's cell.

## criteria

Acceptance test: no roof forms over the mast's cell by auto-roof or by the build-roof designator, and the refusal names the
pole; a roof forced by god mode still cuts the spans. Red today: auto-roof roofs the cell [measured from the def and vanilla's
`AutoBuildRoofAreaSetter`]; the designator does too [guess ~85%]; the live read is UNRUN.

## refs

file: src/RimMandrake/GimmeSomeSlack/Defs/Aerial/RM_AerialAnchors.xml
file: src/RimMandrake/GimmeSomeSlack/human_review.py
def: ThingDef/RM_AerialMast
tier: gimmesomeslack
