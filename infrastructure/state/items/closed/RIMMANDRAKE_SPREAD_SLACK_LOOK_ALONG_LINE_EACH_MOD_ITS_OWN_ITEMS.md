# RIMMANDRAKE_SPREAD_SLACK_LOOK_ALONG_LINE_EACH_MOD_ITS_OWN_ITEMS

His words, 2026-11-22 2:44 PM PST (filing): *"Both Flow Works need the "change everything on this line" (for flow works items) and GSS needs "change everything on this line" (for GSS items). They don't need to change each other's items though. Each mod can handle only its own, that's ok."*

## spec

Choosing a look on one Gimme Some Slack item changes every GSS item on the same connected line: cords, poles, lights, switches.
Another mod's items stay as they are. Twin of `RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY`.

What the code does today (read by the ticket sweep of 2026-11-22, not measured live): "Restyle this run"
(`RM_MapComponent_ConduitRuns.RestyleRun`, owner 2026-10-04) repaints every run member (`ConduitStylePicker.IsMember`: the styled
conduit defs, and the three mast defs `RM_AerialMast`, `RM_AerialLampMast`, `RM_AerialWallBracket` that touch the run) and the floor
lamps hooked to it, unless a lamp was styled on purpose. Unread: whether a run follows an overhead wire to the next pole, and
whether a styled switch is a member. So the gap may be small.

## version

Next version, by the obvious reading (the sweep's call, listed for the Conductor): no 0.1.1 bar names a restyle along the line,
and following the line across poles and switches extends the 0.1.0 feature. If the Conductor reads it as a Problem of 0.1.1
("needs"), it moves to the current version.

## criteria

Acceptance test: none offline yet. Live, on his walk save or any map: a cord run, a pole, an overhead wire to a second pole, a
switch and a lamp on one line; "Restyle this run" on one cord to Futuristic; each item's own look menu then reads Futuristic.
UNRUN: ArchBig is his walk.

## verify

The live acceptance test under ## criteria, its capture cited on the close.
