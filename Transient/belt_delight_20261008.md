# DELIGHT batch — 2026-10-08 (FOUNDRY helper)

Source: design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md (owner card: queue ALL batches).
Offline only. One commit per item.

## FV-1 tentacle linger + cap
DONE `b20a31ffc` — FEVERWOOD_LIMB_LINGER_CAP_1 built; verified not already present (CompTentacleLimb had no lifetime, watch had no cap). Linger 12 h / cap 6 PROVISIONAL, settings toggle + 2 sliders. Owes A1-A3 L1, H1 L4.

## DI-2 Chill air pump
DONE `8ceac720a` — CHILL_AIR_PUMP_1 built. Found Odyssey already ships OxygenPump, so the pump IS that building plus RM_CompChillAirSupply (patch), not a new def/art. Per-provider ledger kernel fuzzed. 300 W / 60 cells-per-pump PROVISIONAL. Owes A1 L1, A2-A4 L2, H1 L4.

## LP-2 glow tank drinks from pipes
DONE `041c0142b` — GLOW_TANK_LIQUID_FEED_1 built. Verified unbuilt (def header + Building_GlowTank said so). Reflection bridge to FlowWorks RM_LiquidNet.TanksFor; dry = growth paused. 4 units/day PROVISIONAL. North-star component + mutant added. Owes A1 L1, A2-A3 L2, H1 L4.

## X-6 / FV-5 arrival letters
pending
