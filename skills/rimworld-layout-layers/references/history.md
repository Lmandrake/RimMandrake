# History: the measurements, and the lines that were wrong

The active files hold the lessons. This file holds dates, full measurements and corrected lines (corrected 2026-11-23).
Engine facts were read in the decompiled 1.6 source through RimSage.

## The measured case (2026-08-26)

- The generated Jawa dwelling: 81 planned things, **81 placed**, 0 failed, 0 refused. Terrain **112/112**, roof **180/180**. The
  read-back, cell by cell: **0 missing, 0 wrong material**.
- Each room: `properRoom: true`, `openRoofCount: 0`, `usesOutdoorTemperature: false`. Three doors were placed, and all three
  rooms reported `doors: []`.
- On that day `palette.json` had no `CONDUIT` entry. The entry came later, in the role lists.
- The skill listed the causes of the hot nursery. The template file `design/Jawa/templates/nursery.lua` lists a third cause
  instead of the size: the cooler's cold side faced out.

## The template that passes (2026-08-26)

```
outdoor 56.3 C   ->   room 21.7 C        worst 22.8 C vs a 32 C threshold
```

- Four wrong designs were found and fixed against a running game in one sitting. After the compiler fix of 2026-08-26, the
  template passed end to end: one 1700 W net straight from the paint, **25.1 C worst against 38.8 C outdoor**. The old text
  counts five wrong designs at that point.
- The old text said that the battery was inside and reached out as a connector. The template puts the battery outside, on
  the bus. The def dump reads `transmitsPower` True for `Battery`. So the battery is a transmitter.

## Corrected lines

- **A connector and a late transmitter.** The old text said: a connector binds to a transmitter at spawn, and a transmitter
  that appears later does not claim it. `PowerNetManager.TryCreateNetAt` calls `ConnectAllConnectorsToTransmitter` for each
  transmitter of a new net. That method claims each connector in range whose `connectParent` is null. So only a connector that
  already has a parent stays. The old build order was `Battery, Cooler, Door, EggBox, PowerConduit, SolarGenerator, Wall`, in
  groups by `(defName, stuff)`, alphabetically. The coolers read `Grid excess: 0 W`, so they had a net. The likely cause: they had
  bound to the battery's own net, which had no source. Nobody measured that cause.
- **`Current power use: Low`.** The old text marked it "actually running". `CompTempControl.CompInspectStringExtra` prints Off,
  High or Low, and Low means that `operatingAtHighPower` is false.
- **The roof lint.** The old text said that the lint over-warns and never under-warns, because Manhattan ≤ 6 implies
  Euclidean ≤ 6. `RoofCollapseUtility.WithinRangeOfRoofHolder` fills through roofed cells only. A plan with one wall and one
  roof cell 5 cells away gave no `roof-unsupported` finding (run 2026-11-23).
- **Refuse on a missing path.** The old text said to refuse the write. The owner's ruling of 2026-08-26 in the same file says
  that none of this may become a block. So the assessment reports.
- **Conduit over a wall.** The old text said that it cannot be authored. `place_overlay` came on 2026-09-05 or before
  (`DISTRICT_TEMPLATE_LIBRARY_1`). A test plan with `place_overlay("CONDUIT", x, z)` on a wall row gave 0 findings.
- **`jawa/power_net`.** The old text said that it was NOT deployed. The deployed DLL of ArchBig, dated 2026-11-23, holds
  `jawa/power_net`, `jawa/get_power_nets_batch` and `jawa/pipe_net_info` (strings in the DLL; ArchSmall's DLL has the same
  size and date). `jawa/room_get` returns `usesOutdoorTemperature`. Before that, the reader derived it as
  `openRoofCount / cellCount`.
- **Paused games.** `layer-mechanics.md` said that a power net resolves on tick. `Map.MapUpdate` calls
  `UpdatePowerNetsAndConnections_First`, so a paused game resolves it on the next frame.
- **A generator.** `layer-mechanics.md` said that a generator is a connector. `SolarGenerator` transmits.
- **`set_roof_batch`.** The old message was `Roofed 0 cell(s) — already correct`. The tool now prints the count of cells and ops.
- **`jawa/set_substructure_batch`.** On 2026-08-28/29 (BENCH) it reported `success` + `cellsFailedVerify: 0` while it skipped each
  cell whose floor already wrote under-terrain, and it was silently refused outright on floor terrain. The tool now counts
  each refused cell in `refusedCount`.
