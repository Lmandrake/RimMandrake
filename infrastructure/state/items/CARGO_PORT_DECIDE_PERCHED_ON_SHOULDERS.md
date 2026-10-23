# CARGO_PORT_DECIDE_PERCHED_ON_SHOULDERS

**For:** FOUNDRY · **Filed:** 2026-10-23 by a BENCH offline helper (judge FIX on tank_port_fittings).

## What is true
- The hose port the code defines for `RM_UniversalCargoTank` west/east upper lane (end-cell edge midpoint, z = 1.5 cell,
  texture row 128 of 512) lies **above the drawn body's side silhouette** in Scrapper, Industrial and Futuristic: at
  row 128 the only opaque art is the strap tops; the body's top is at row ~133 and its side is within reach of the
  edge only from row ~180 down (measured on `port_fittings.body_image`). On the east, the kept outlet nozzle occupies
  rows ~148-195 to 35 px from the edge.
- A straight stub therefore hovers on the strap tops and covers the nozzle (judge FIX,
  `infrastructure/state/delegated/2026-10-23/tank_port_fittings.json`).
- Art workaround in place (candidates only, the tank pictures are owner-KEPT): `port_fittings.py` `ROUTES` — the coupler
  stays at the port, a thin bypass pipe drops 23 px in from the edge to a collar on the end cap's side (~row 220).
- Related, not a port-off-body: Futuristic `RM_LiquidTank` north lane 1.5 (column 384) lands on the kept elbow-pipe
  fixture; the art jogs east above the valve wheel instead.

## Decide
Keep the bypass art, or move the upper W/E port (C# tank port geometry) to a row where the body is (z <= ~1.3) /
redraw the body. If the port moves, drop the UCT entries from `ROUTES` and regenerate.

## Watch out
`selftest_hose_fittings.py` measures the INSTALLED textures; it cannot see a candidate's bypass. A moved port also
moves the gate's KNOWN entries and the joint check.
