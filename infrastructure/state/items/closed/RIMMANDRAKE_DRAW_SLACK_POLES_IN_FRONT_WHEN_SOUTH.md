# RIMMANDRAKE_DRAW_SLACK_POLES_IN_FRONT_WHEN_SOUTH

Gimme Some Slack **0.1.1** (his card of 2026-11-20). From his walk of 2026-11-20: `design/RimMandrake/validation_holding/gss_walk_20261120.md` row #13 (no picture).

## spec

He asked that power poles follow the "huge things" rule: a pole south of something draws in front of it. The rule's one
home is MandrakePatches' SouthDrawsFront (RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES;
`src/RimMandrake/MandrakePatches/Source/SouthDrawsFront/`). It orders by south only inside a layer: plants print flat on
BuildingOnTop (17), buildings keep their own layer, pawns sit two layers above every building [measured,
`SouthDrawsFrontPatches.cs:15-25`]. The masts print on `Building` (15) with a 2 x 4 picture drawn 1.5 cells north of the
foot (`src/RimMandrake/GimmeSomeSlack/Defs/Aerial/RM_AerialAnchors.xml`), so a plant, tree or BuildingOnTop thing north of a
mast draws over the mast's body; only the head overlay is lifted (`Source/Aerial/RM_MapComponent_Aerial.cs:626`)
[measured from the layers]. What he saw over a pole is not recorded [guess ~60% a plant or tree]. Fix in the rule's home
or by the mast's layer: a tall building whose picture reaches north joins the common layer and its south order. A pawn
standing north of a mast is vanilla's choice (pawn over buildings) and is out of scope unless he says so.

## verify

Offline: a selftest over the SouthDrawsFront kernel and the mast's def: the printed y of a mast at row z against a plant
and a BuildingOnTop thing at rows z+1 and z+2. Live: a mast with a tree one cell north; capture at play zoom.

## criteria

Acceptance test: the mast's printed altitude is above that of every plant or building standing north of it within its
picture's height, and below one standing south of it. Red today [measured from the layer numbers above: 15 under 17];
the selftest is not yet written, the live look is UNRUN.

## refs

file: src/RimMandrake/GimmeSomeSlack/Defs/Aerial/RM_AerialAnchors.xml
file: src/RimMandrake/MandrakePatches/Source/SouthDrawsFront/SouthDrawsFrontPatches.cs
def: ThingDef/RM_AerialMast
tier: gimmesomeslack
