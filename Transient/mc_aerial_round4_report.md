# MessyConduit aerial/cords round 4 — report (2026-10-04)

Owner's typed review (round 3 build) — each point below gets: cause, fix, proof, unproven-live.

## 1. Station 6: wall-socket connector curve / hanging wire on west wall
Cause (read from source + `20261004161954_1.jpg`): the StubWall/StubRock art is a FRONT view of a plate with its own short
cord curling in from the left into the grommet. Round 3 squashed the whole canvas to 0.5 along the cord, so on a west face the
built-in curl became a hook that does not continue the straight incoming cord. The wall-terminal tail
(`CordLayer.HangingTail`) always dropped screen-down (-Z) from the socket, which on an edge-on (west) face reads as a wire
hanging in mid-air.
Fix: plates/holes print only the plate (UV crop, `Core/WallMount.cs` WallU0..), so the straight incoming cord meets a plate with
no curl of its own. The loose wire (`WallMount.LooseWire`) leaves the socket dead straight out of the wall and only then sags
onto the floor; on the visible south face it hangs straight down the face. Selftest `review4: loose` (+ can-fail: the round-3
hook).

## 2. Wall plates / rock holes perspective (must be ON the wall, not out of it)
Measured from his station-9 shot (`20261004162252_1.jpg`, room 5 cells = 665 px -> 133 px/cell): a 1.6 wall cell draws its TOP
over its north 0.62 cell and its visible SOUTH FACE as the light band over its south 0.38; east/west faces are edge-on (a
narrow bevel); the north face is hidden behind the top. Round-3 plates were centred ON the face line (half of each plate on the
open floor): yes, they extended OUT of the wall.
Fix: `WallMount.EntryDecal` draws every plate/hole INSIDE the wall cell from the face line: south face = whole plate
foreshortened into the 0.38 band; east/west (edge-on) = a 0.10-deep strip within the bevel; hidden north face = a 0.06 sliver.
The cord runs on 0.03 past the face under the wall (`CordBuilder.PastFace`) so cord and plate meet with no floor gap.
`CordAudit` now counts any plate not `WallMount.OnFace` (FlatWallPlates / FlatRockHoles). Pixel proof against the real
textures at his 133 px/cell: `src/RimMandrake/Utils/mockups/messy_conduit/wall_mount_check.py` -> 0 faults; `--plant` (round-3
rules) -> 33 faults (E/W bracket plates 0.02 out of the wall, Industrial south-face plate 0.01 out, every cord plate out).
Proofs: `D:\Luke\dev\RimMandrake\Transient\mc_aerial_r4\wall_mount_<Look>.png`.

## 3. Lamp mast: controls present, no illumination


## 4. North-facing bracket vs owner's torch photo
The def already had CompGlower (radius 9, warm), flick, colour picker, darklight. Nothing in our code turns it off, so
"no illumination" is most likely daylight: the review map is pinned to noon, where glow-grid light is invisible outdoors (true
of vanilla lamps too), and the mast head has no lit look of its own (a StandingLamp's art always shows a bulb). Not provable
offline whether it was powered.
Fix: glower = vanilla StandingLamp's radius 12 and colour (217,217,208); while `CompGlower.Glows` (powered AND switched on)
`RM_MapComponent_Aerial.DrawLitHead` draws a lit bulb (additive glow, the glower's colour) at each look's measured lamp head.
The probe now reports `lampMasts[{powerOn, glows, glowRadius}]` and `litHeads`, so a live pass can tell unpowered from
invisible.

## 5. Station 19: wall-device cords end under the device's wall
His north-facing bracket is our rot South (it points at a wall to its south, sitting on the wall's NORTH face).
His torch photo: the vanilla `TorchWallLamp` (drawOffsetSouth -0.9) shows only its flame, ~0.15-0.3 cell over the wall's
top edge; the torch body is behind the wall. Round 3 drew our whole plate face-on across the edge.
Fix (`wire_bracket_art.py`, installed through the art ledger): the _south art is cut just under its insulator (KEEP_S per
look) and drawn with the cut line 0.03 under the wall's top edge (`AerialMath.BracketInset`): only the insulator shows, 0.04-0.2
over the edge. Other facings: per-face inset from the measured plate depth so every plate is inside its face (E/W in the bevel,
rot North in the south band). Side-by-side with his photo: `D:\Luke\dev\RimMandrake\Transient\mc_aerial_r4\torch_compare.png`.

## 6. Station 21: two poles carrying power OVER a hidden stone block
Cords to devices end at the footprint centroid; a wall lamp (building.isAttachment) stands in the cell in FRONT of its
wall, so the cord stopped there. Fix: `MachineInfo.HasHome` = the wall cell (`CordWorldAdapter.SetWallHome`, the same wall
vanilla's `PowerConnectionMaker.TryConnectToAnyPowerNet` measures from); the cord runs on through the lamp's cell to the
wall's centre, beneath the wall. Pole drops do the same (`RM_MapComponent_Aerial.DeviceHome`; the wall cell counts as the
device's art so the drop goes under it). Selftest `review4: home` (+ can-fail).

## 7. Station 26: battery shows no wire to local pole; connection range
Station 26 put the battery at (1,9)-(1,10) and the mast (1x1 footprint, no `<size>`) at (3,9): a one-cell gap. A battery is a
TRANSMITTER (CompPowerBattery transmitsPower) and transmitters join a net only by touching; so it was not on the net at all,
not merely undrawn (a layout bug in `human_review.py`, not a renderer bug).
Ranges, from the code: a CONSUMER (lamp, heater, turret...) joins the nearest transmitter within 6 cells -- vanilla
`PowerConnectionMaker.ConnectMaxDist = 6` (BestTransmitterForConnector, a 13x13 box), and our poles are transmitters, so yes,
devices connect to a pole over a distance as usual; we draw that `connectParent` link (`RM_MapComponent_Aerial.cs`
LocalConnections ~l.379 / DrawLocalDrops; `CordWorldAdapter.cs` connectors loop ~l.84). A TRANSMITTER (battery, switch,
conduit, pole) joins only by touching (vanilla net flood); we draw a battery's hookup only to cardinally adjacent conduit
(`CordWorldAdapter.cs` ~l.71-80) or an adjacent pole (`RM_MapComponent_Aerial.cs` LocalConnections). Our visual link never
joins nets: the vanilla grid decides, we draw it.
Fix: the new `layout_check` rule `battery_touch` found FOUR such batteries (stations 19 x2, 20 x2, 26, 28); all moved to touch
their pole/conduit. Selftest `src/RimMandrake/MessyConduit/selftest_human_review.py` (+ can-fail: the old st-26 battery).

## Builds / tests / commits
- `winbuild.py MessyConduit`: 0 errors. The committed DLL was built from a clean `git archive` of the committed source (the hose
  agent's Hose/*.cs edits are uncommitted in the clone, so a clone build would stamp a mismatching .srchash).
- `selftest_messyconduit.py` 511/511 (new `ReviewRound4Checks.cs`: plates on all three face kinds, loose wire, 16 brackets,
  wall home; each with a can-fail). `selftest_human_review.py` 4/4. `wall_mount_check.py` 0 faults, `--plant` 33.
- `run_selftests.py` 173/177: northstar_matrix C2 (dirty live shots), MandrakePatches, UtinniPatches dump: pre-existing;
  modcheck failed only under the parallel run (22/22 solo).
- Not deployed (the game holds the DLL).
- Commits: `adab32eef` source+art+tests, `33e9d2d65` DLL, `22604d76e` review map (only my hunks; the hose agent's
  station-23 text stays uncommitted in the clone).
- Key sheet (`Transient/mc_human_review/KEYSHEET.md`) regenerated by `--plan` but NOT committed (it was already dirty from
  another writer).

## Unproven live
Everything visual: plate/hole look per face (strip on E/W/N, band plate on S), the straight loose wire, the insulator-only
north-face bracket vs the torch, wall-lamp cords ending under the wall, the lit lamp-mast head and whether the lamp masts were
powered at all (read `lampMasts` from the aerial probe), station 21 wire vanishing into the fog, the four moved batteries now
joining their nets. Needs redeploy after the game closes and `human_review.py --build`.
