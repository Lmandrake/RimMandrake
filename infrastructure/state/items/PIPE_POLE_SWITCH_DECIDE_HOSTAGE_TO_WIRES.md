# PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES

Found by the FOUNDRY GSS code-review pass, 2026-10-21 (DIRTY_CODE_REVIEW_STANDING_LOOP_1).

## Finding

FlowWorks' `RM_PipePole` (`src/RimMandrake/FlowWorks/Defs/Machinery/RM_PipePoles.xml`) is a GSS aerial
anchor of kind Pipe (PIPE_POLES phase 4, 681d39c09). Every GSS aerial gate reads the POWER-lines master
switch `AerialSettings.enabled` ("Aerial power lines (master switch)") without looking at the anchor's kind.
So with that GSS switch OFF:

- pipe poles leave the architect menu: `PlaceWorker_AerialRange.IsBuildDesignatorVisible` (PlaceWorkers_Aerial.cs:12);
- built pipe spans are not drawn: `RM_MapComponent_Aerial.MapComponentUpdate` returns early (line ~509);
- their ground layer (span shadows, fallen-half ends) is hidden: `SectionLayer_RM_AerialGround.Visible`;
- a new pipe pole never auto-links: `ProcessAutoLinks` (~259) and `CompAerialAnchor.PostSpawnSetup` (195);
- re-string jobs on cut pipe spans never run: `RestringJob.cs` 86 / 119;
- the switch's own text names only masts, lamp masts and wall brackets, not pipe poles.

The FlowWorks liquid edge across the span (phase 5) presumably still joins, so the pipes would carry liquid
while being invisible: no graceful all-off degrade (standing rule: every mod ships superb Mod Settings).

## Also (same files, text only)

On a pipe pole, the gizmos "Unlink all" ("Take down every wire on this anchor") and "Re-string cut wires"
still say wire. RoofSweep's message says "overhead wires". A cut pipe's ground end is printed with the
electrical frayed-end decal (FrayDead). That is a cosmetic call, so ask the owner before changing it.

## verify

With GSS "Aerial power lines (master switch)" OFF, a pipe pole is still in the architect menu, its built spans
draw, a new pole auto-links, and the switch's label says exactly what it governs. GSS SelfTest and FlowWorks
SelfTest stay green.

## spec (decision owed)

Which switch owns pipe poles: (a) none in GSS, so gates check `AerialKinds.CarriesPower(kind)` before reading
`AerialSettings.enabled`; (b) a FlowWorks pipe-pole switch registered through `AerialLineProfiles`
(alongside its range and sag getters); or (c) keep the GSS master gating both and say so in its label.
(b) fits the existing profile seam. The files listed above stay DIRTY until this lands:
RM_MapComponent_Aerial.cs, CompAerialAnchor.cs, SectionLayer_RM_AerialGround.cs, AerialSettings.cs.
