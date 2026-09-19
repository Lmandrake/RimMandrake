# FUNGAL_SOIL_TRADE_1 — dig fungal soil, haul it to the farms; the fungus objects

Owner's player note, 2026-09-06 (Badlands sitting), verbatim in intent: *"the Jawas might
be able to make money by going and digging up fungal soil and transporting it to
settlements, especially moisture farmers. Normally quite a long haul, but the ship can get
it done quickly. An early game way to make money... and a fast way to make the fungal
creatures attack you when they sense the distress signals emerging from the fungal whole."*

## spec
- **The good**: fungal soil (the Rot's mycelial ground — `the_rot.md`; the raided
  `BMT_MycelialSoil` terrain/material is the ready def pattern) is dug as a haulable item
  and sold/delivered to settlements — the Moisture Farmers above all (their cisterns and
  Badlands shade-soil farms want it: `badlands` sheet). Long haul overland; the gravship
  makes it a fast early-game income.
- **The price**: digging tears the connected fungal whole (the Rot's health-sharing
  network, `the_rot.md` §4) — **distress signals** bring the Rot's fauna down on the
  diggers. Design the trigger (dig count / area) and the response (which creatures, how
  fast) so the money is real and the raid is real.
- Anti-exponential: price the soil below any infinite-loop threshold; the ship's speed is
  the edge, not a ladder.
- Ties: `the_rot.md` (the Sheen, the hybrids), `MOISTURE_FARM_TEMPLATES_1` (the buyers),
  the trade/heat systems.

## verify
A quicktest: dig N soil on a Rot map → creatures respond; a delivery quest/trade pays out
at a farm; the owner has played it once.
