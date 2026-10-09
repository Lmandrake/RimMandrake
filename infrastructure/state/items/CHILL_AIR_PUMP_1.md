# CHILL_AIR_PUMP_1 — air pumped down to the Chill floor

Source: `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row DI-2 (owner card 2026-10-08: queue all batches).
Owner ruling it serves (CHILL_FIRE_BAN_1): fire exists below **only where someone pumps air down**.

## what
Built at `8ceac720a`. Checked first: nothing in `src/` wrote `RM_MapComponent_ChillOxygenation`; no pump existed.
Odyssey already ships `OxygenPump` (wall-mounted, powered, OrbitalTech-gated), and all DLC is assumed, so the pump
is that building, not a new one:
- `Patches/RM_ChillAirPump_OxygenPump.xml` adds `RM_CompChillAirSupply` to `OxygenPump` and a sentence to its description.
- On the Chill seabed only, a live pump (powered, switched on, not broken) marks every cell of its **sealed** room
  oxygenated (not open to the map edge, not mostly unroofed). Pumps in one room pool capacity; a room bigger than
  `cells-per-pump × pumps` is not served. Its inspect line says which.
- `RM_OxygenLedgerKernel`: per-provider cell sets plus per-cell counts, so two pumps sharing a room keep it lit
  until both stop. Fuzzed against a reference model (`DivingFuzz` family `oxygen`).
- Air costs power: on the seabed it draws the full setting, overriding vanilla's low-power-unless-vacuum mode.
  Vanilla's own "power mode: low" line may read wrong down there (cosmetic).
- Mod Settings (Diving): toggle, watts (50–1000), cells per pump (10–400).

**PROVISIONAL numbers** (invented, owe a sitting): 300 W while pumping, 60 cells per pump.

Feeds ANCIENT_WAR_LAB_1 / CHILL_WARLAB_ROUTES_1's oxygen-bomb route (same hook).

## criteria
- O1 L0: DivingInteraction builds; oxygen ledger fuzz and RoomServed units pass; patch matches 1 OxygenPump in Odyssey
- A1 L1: OxygenPump def carries RM_CompProperties_ChillAirSupply on the live load
- A2 L2: on a Chill floor map, a fuelled stove in a sealed roofed room with a powered pump lights; with the pump switched off it goes dark
- A3 L2: two pumps in one room; switching one off keeps the room lit, switching both off ends it
- A4 L2: a pump in an unroofed or edge-touching room oxygenates nothing and says so in its inspect line
- H1 L4: the owner judges power cost and room capacity (PROVISIONAL until then)
