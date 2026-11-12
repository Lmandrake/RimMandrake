# CHILL_AIR_PUMP_1: done statement

Item title: DI-2: air pump building oxygenates a sealed Chill room (per-provider counts); power cost; research-gated; settings toggle
Written by wc.py setup (no model) from the ledger criteria and `infrastructure/state/items/CHILL_AIR_PUMP_1.md`; the item file's spec and verify sections are the owner's words where it has them.
The item file is thin (it has no ## spec section). Read the ledger history (`rimflow show CHILL_AIR_PUMP_1`) for what is meant, and write what you find into NOTES.md; do not invent scope.

- **O1 (L0):** DivingInteraction builds; oxygen ledger fuzz and RoomServed units pass; patch matches 1 OxygenPump in Odyssey
- **A1 (L1):** OxygenPump def carries RM_CompProperties_ChillAirSupply on the live load
- **A2 (L2):** on a Chill floor map, a fuelled stove in a sealed roofed room with a powered pump lights; with the pump switched off it goes dark
- **A3 (L2):** two pumps in one room; switching one off keeps the room lit, switching both off ends it
- **A4 (L2):** a pump in an unroofed or edge-touching room oxygenates nothing and says so in its inspect line
- **H1 (L4):** the owner judges power cost and room capacity (PROVISIONAL until then)
