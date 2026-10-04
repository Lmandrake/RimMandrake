# MessyConduit round-2 AERIAL workstream report (2026-10-04)

## 1. Terminal assignment logic today (before this pass)

There were three separate cases, and none of them picked a terminal per connection.

* **Span between two anchors (mast-mast, mast-bracket).** `AerialMath.SpanStrands`
  (`src/RimMandrake/MessyConduit/Source/Aerial/AerialMath.cs:253-269`) draws ONE wire per insulator:
  count = min(insulators at A, insulators at B, the "wires per span" setting `maxStrands`).
  `AerialMath.InsulatorIndex` (`AerialMath.cs:274-280`) maps strand to insulator: 1 wire takes the
  MIDDLE insulator, 2 wires take the OUTER PAIR, and 3 wires take one each. Insulators per anchor come from
  `AerialMaterials.InsulatorsFor` (`AerialMaterials.cs:138-153`): a mast with its look's own art has the 3
  tips measured from the PNG (`PoleGeometryTable.Insulators`), a wall bracket has 1, and a stand-in has 3 if
  `insulatorSpread > 0`, otherwise 1. So a mast-to-mast span is 3 parallel wires, and a mast-to-bracket span
  is 1 wire from the mast's middle insulator. `maxLinks` (mast 4, lamp mast 3, bracket 2) caps how many SPANS
  an anchor holds and has nothing to do with terminals. Every span on a pole lands on the same insulators.
* **A local device wired to a mast (lamp, heater; vanilla `connectParent` = the mast).** There was no terminal
  logic. `Patch_PrintWirePieceConnecting` (`src/RimMandrake/MessyConduit/Source/ConduitVisuals.cs:135-168`,
  pre-change) printed one straight cable from the device's GRAPHIC centre to the mast's graphic centre
  (`TrueCenter + DrawOffset`, which is 1.5 cells up the shaft) at `SmallWire` altitude. That put it under the
  mast art, so it never visibly reached any insulator. Two or three devices on one mast all converged on the
  same hidden point.
* **A transmitter standing next to the pole (the battery at stations 7-10).** It joins the net by cardinal
  adjacency (`AerialPowerPatch`/vanilla). Nothing drew it, which is the "no visible connector between
  batt[ery] and power pole" at station 9 (owner's F10 shot `20261004151208_1.jpg`: the battery sits beside
  the mast with no cable). Station 9's mast-to-bracket span IS drawn in that shot, so I read "battern" as the
  battery. Section 5 covers both readings.


## 2. Device connectors to centroid, beneath building

* **Floor cords (station 4's lamps, every machine end).** `CordBuilder.IntoArt` (`src/RimMandrake/MessyConduit/Source/Core/CordBuilder.cs`)
  now runs every cord into a machine on to the footprint CENTROID (`CordBuilder.Centroid`). The last 0.2 cell runs
  straight along the way in, and the plug sits there pointing in. Cords print at `Conduits` altitude, below every
  building, so the art hides the run and the old per-machine art insets no longer matter.
* **Hookup cables to non-anchors (switch, other transmitters).** `ConduitVisuals.PrintCable` now ends at both
  buildings' `TrueCenter()` (the footprint centroid, no graphic offset) at `SmallWire` altitude, i.e. beneath both.
* **Hookups to masts, lamp masts and brackets** are now drop wires to a terminal (section 6). Each one runs from the
  device's centroid, and its part over the device's art (footprint united with graphic rect) is drawn at `SmallWire`
  under the device. The rest hangs at span altitude.
* SelfTest: the oracle-scene floor check and the endpoint-attachment check now trim a strand's end run inside its
  machine's footprint (`Program.TrimUnderArt`). That run is there by design now. A vertex inside a footprint anywhere
  else still fails. A new check confirms every machine cord end sits on the centroid, and the sanity counts are
  non-zero: nodal 11/11, gap 4/4, downed 4/4, under 8/8, needless 9/9, tangle 5/5.


## 3. Power tap clamp art

* I searched artpipe first. `D:\Luke\dev\_artpipe\_artsrc\RM_MessyConduit_Jawa_TapClamp\RM_MessyConduit_Jawa_TapClamp.png`
  already held a finished render of rusted crocodile jaws biting a vertical length of line, with a cable trailing
  off. The shipped `TapClamp.png` was a crude 64 px placeholder instead. That render is now `Aerial/TapClamp.png`
  (128 px, Lanczos upscale of the 64 px source).
* The clamp is now drawn per frame (`RM_MapComponent_Aerial.DrawTaps`). The bitten line in the art (measured at
  -0.375 of the width) lies ON the victim transmitter's cell centre, the handle turns toward the tap's own cell, and
  it is drawn 1.5 cells wide at `BuildingOnTop`. The building's own graphic is now transparent, and its UI icon is
  the clamp.
* Sparks: `TapSparks`. While the clamp is stealing (`lastStolenW > 0`), micro-sparks come from the jaws every
  ~150-270 ticks (scaled by spark intensity), with a small lightning glow on every third burst. It is look-only
  and capped by the tap count.
* Unproven live: the scale, the bite offset, and whether the 64->128 upscale reads crisply enough. If it is soft, a
  128 px artpipe re-render of the same brief is the fix. The clamp is not drawn while the master aerial switch is off.


## 4. Wall bracket geometry

What I found: the **Scrapper** and **Futuristic** `_south` textures were wired with the plate at the TOP. A south-facing
bracket stands north of its wall and points at it, so on those two looks the insulator pointed INTO the wall. The
other two looks were right. Separately, every look and facing used one def-wide 0.9-cell draw offset, which put the
plate at the wall's inner side or centre instead of its outer edge, and buried the E/W brackets inside the wall.

What I changed:
* `src/RimMandrake/Utils/mockups/messy_conduit/wire_bracket_art.py` now enforces "plate on the wall side" for every
  facing. It flips any render drawn for the opposite wall (it flipped Scrapper south and Futuristic south) and
  records each texture's measured PLATE EDGE.
* `BracketGeometryTable.cs` is regenerated and now Verse-free (`P2`, plus a `PlateEdge()` table), so the SelfTest
  compiles it.
* In `AerialMath`, the new `WallNormal`, `BracketDrawOffset` and `BracketLeansOut` work as follows. The per-look,
  per-facing draw offset runs along the wall normal only, and puts the plate's wall-side extreme 0.12 cell past the
  wall's outer face (`BracketPlateInset`). The arm and insulator then stand over the bracket's own cell.
  `AerialMaterials.ApplyPoles` writes those offsets into the look's `GraphicData` (`drawOffsetNorth/East/South/West`).
  `CompAerialAnchor.BasePoint` reads them, so the span still lands on the drawn insulator.
* SelfTest: for all 4 looks x 4 facings, it checks that the insulator leans out, that the plate edge sits at
  0.5+0.12 along the normal, that the insulator is outside the wall and inside its own cell, and that the offset has
  no tangential part. There is a can-fail check: the OLD Scrapper/South insulator (0.004,-0.229) must read as leaning in.
* Unproven live: the flipped Scrapper/Futuristic south art is a mirror of a plate-up render. If its lighting looks
  wrong in game, it needs a re-render from artpipe.


## 5. Bracket-to-pole connector

In the owner's station 9 shot (`20261004151208_1.jpg`) the mast-to-bracket SPAN is drawn, and what has no connector
is the BATTERY beside the mast. It joins by adjacency, and nothing drew that join. Adjacent transmitters (cardinally
beside a mast or bracket, excluding conduit and other anchors) now count as local connections
(`RM_MapComponent_Aerial.LocalConnections`). Each gets a drop wire from its centroid up to a pole terminal, like any
device. If he meant the mast-to-bracket span, that is already one wire from the mast's middle insulator to the
bracket's insulator (section 1). The bracket offsets moved in section 4, and the span follows the drawn insulator
through `BasePoint`. Unproven live.


## 6. Spreading devices across terminals

Done, without a rewrite. `AerialMath.AssignTerminals` (Verse-free, selftested) orders a pole's local connections by
where they stand across the crossarm, then by id. One device takes the middle terminal, two take the outer pair,
three take one each, and more share in even, contiguous groups that never cross. A one-insulator bracket puts
everything on its one terminal. `DrawLocalDrops` recomputes this every frame from the pole's `connectChildren` and
adjacent transmitters, so adding a third lamp re-spreads the first two. Meshes are cached by signature.
Vanilla's straight hookup print to an anchor is suppressed (`Patch_PrintWirePieceConnecting`). The state read is
`lastTerminals[anchorId][deviceId]`, and `lastLocalDrops` is ready for a probe/bridge check. The selftests cover
1/2/3/7 devices, a 1-insulator bracket, and order independence. Unproven live: the drop wire's look and its split
point under the device art.


## Build / tests / deploy

* `winbuild.py MessyConduit`: 0 errors.
* MessyConduit SelfTest: 457/457 (aerial 70/70 including the new bracket and terminal checks).
* `run_selftests.py`: 172/174. Both failures are outside this change: `northstar_matrix/selftest.py` C2 reads the
  live shots under `Transient/mc_matrix_live_20261002` (dirty in the tree from another window), and
  `selftest_utinnipatches_dump.py` is unrelated.
* Deploy: textures and defs are in the game folder. The DLL was NOT written because the running game holds the lock,
  so none of the C# changes are live until the next deploy after the game closes
  (`deploy_custom_mods.py --mod MessyConduit --apply`). Until then the deployed def draws the tap clamp
  transparent with the old DLL, so the clamp is invisible until the DLL lands.

