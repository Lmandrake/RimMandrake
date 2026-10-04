# MessyConduit aerial round 3 report (2026-10-04)

## Status
started

## Items
1. wires beneath Power Switch
2. wall connector angle (face out, not nadir)
3. lamp mast lighting controls
4. station 9 triple cords -> single
5. north wall bracket perspective
6. three wires fall on explosion
7. power tap as node / bite on top

## Findings

## Build / tests

## Commits

## Unproven live

### Owner shots read (Steam F10)
- `C:\Program Files (x86)\Steam\userdata\40784075\760\remote\294100\screenshots\20261004154938_1.jpg` wall connectors (cords through a wall) read as plates seen from above.
- `...\20261004155115_1.jpg` station 9: lamp mast in a walled square, 4 brackets; north one sticks far up off the wall.
- `...\20261004155402_1.jpg` station 11: clamp art carries its own grey conduit segment (the "solid piece of conduit").

### Root causes (read from source)
1. Power switch: vanilla `PowerSwitch` uses `shaderType Transparent` (queue 3000, no depth write). Cords print at queue 3000 and plugs at 3001, so they paint OVER the switch whatever their altitude. Every other device is Cutout (writes depth), which is why "beneath the device" works everywhere else.
2. Wall connectors: `StubWall` decal is drawn square (top-down); only `StubRock` is foreshortened (`RockSquash 0.6`).
3. Lamp mast: has `CompProperties_Flickable` (the "toggle power" gizmo) but lacks vanilla StandingLamp's `colorPickerEnabled`, `darklightToggle`, `ColoredLights` power upgrade and `PlaceWorker_GlowRadius`.
4. Station 9 triple cord: `CordBuilder.LayEdge` draws `rr.Int(CordsMin 1, CordsMax 3)` parallel strands on EVERY edge, including a device's own lead (wall stub -> lamp).
5. North-wall bracket: that is rot South (`_south` texture, plate at bottom); its arm is drawn full length straight up off the wall top.
6. Broken span: `FallenCord` lays ONE wire from the middle insulator, whatever the span's strand count.
7. Tap: the clamp render includes its own grey conduit segment (that is the "solid piece of conduit"); the victim conduit cell is a dead end in THEIR cord graph, so it draws a live sparking free end beside the clamp.

## Done so far
- Switch: our switch GraphicData now Cutout (`ConduitVisuals.ApplySwitch`); rule in `Core.DrawStack.CordsPaintOver`.
- Lamp mast: + colorPickerEnabled, darklightToggle, ColoredLights powerUpgrade, PlaceWorker_GlowRadius (flick was already there: the "toggle power" gizmo). Colour picker appears only once ColoredLights is researched (vanilla rule).
- Device lead = ONE cord (`CordBuilder.DeviceLead`), seeded draws unchanged.
- Wall plate foreshortened `WallSquash 0.5` (+ `CordAudit.FlatWallPlates`).
- Tap: clamp art is jaws only (`wire_tap_clamp_art.py`, installed via art ledger from the artpipe render); clamp drawn on the tap node, queue above every cord; `CordWorldAdapter.AddTapNodes` hooks the bitten conduit (or links the bitten transmitter) to the tap's machine node.
## progress 16:09: code edits done (switch, lamp, lead, wall, bracket art, fallen strands, tap node+art); building next

## Build / tests
- `winbuild.py MessyConduit`: 0 errors, 0 warnings.
- MessyConduit SelfTest 491/491 (aerial 75/75 incl. round-3 bracket lean per facing + north-wall foreshorten + 3-wire fall; review3: switch draw order, wall plates foreshortened, device lead = 1 cord, tap node has both grids and no free end; each with a planted can-fail).
- `run_selftests.py` 172/176: failures are pre-existing/unrelated (northstar_matrix C2 reads the dirty live shots in `Transient/mc_matrix_live_20261002`; MandrakePatches, StarWarsPatches semantics, UtinniPatches dump).
- Not deployed (game holds the DLL).

## Decisions made here (PROVISIONAL, judge live)
- "One cord" applies to EVERY edge that ends on a device (its lead), not only short ones; bundles stay between junctions / stubs / conduit ends.
- North-wall bracket art squashed to 0.55 height (`FORESHORTEN_N`); wall plates squashed to 0.5 along the cord (`WallSquash`).
- Tap placement rule unchanged (beside their conduit); the tap is now a drawn NODE of both cord graphs.
- Fallen wires lie 0.22 cell apart at the break (`FallenSpread`).

## Commits
- `898e82764` round 3 source, defs, art, selftests
- `19186b1e1` DLL + srchash rebuilt from committed source

## Unproven live
Everything visual: switch over cords (Cutout edge look), wall plate squash, north-wall bracket look, lamp-mast colour/darklight gizmos (colour needs ColoredLights research), one-cord leads, 3 fallen wires, tap node + jaws-only clamp placement/scale. Needs redeploy after the game closes.
