# LIQUID_LEDGER_BUILD_NO_UNIT_LOST

Spec: `design/RimMandrake/liquid_network_semantics_design_2026-10-11.md` rev 2 (2dafd0502), §6 L1-L11; owner cards Q1-Q5
ruled 2026-10-11 (Q1 "Hose ends + tank jobs", Q2 real held volume + cleanable spill, Q3 pump pour = fast drain for Dump
tanks, Q4 theft priced like power theft).

## built (offline, all pushed; SelfTest 267/267, hose 342/342, 16/16 python selftests)
L1 7432ac095a transfer service · L2 12f1b314c7 components per revision · L3 9d727a3b22 fill/draw order · L4 25d272ff93
tank jobs + settle (tanksFeedHoses -> tankModesEnabled) · L5 9163cd3d76 free-end roles · L6 fe13508b7a pump as world mover ·
L7 5b9a704357 outflow ends + Dump drain · L8 8ec0dbef2a held volume + spill · L9 e329b72036 liquid theft · L10 5ce7f4aae3
adapter modes · L11 a341da28fa perf fixture (0.00016 ms mean, 0.11 ms worst offline).

## criteria
- A1 L0: C# SelfTest 267/267 + hose 342/342 + 16/16 FlowWorks python selftests at a341da28fa.
- A2 L2: lake -> pump -> hose Outflow -> disconnected canal fills with no tank (NS_canal_from_lake_no_tank).
- A3 L2: a Dump tank drains out an Outflow end with no pump (NS_dump_tank_drains_without_pump); a pump on Pour drains it fast.
- A4 L2: an Intake end in a pond moves nothing without a pump (NS_intake_needs_pump); pond round trip conserves units.
- A5 L2: ship tank on Fill loads from base tanks over a hose; on Empty unloads.
- A6 L2: a hose switched off spills its held liquid at the open end; on a cleanable cell colonists clean it.
- A7 L2: a hose into another faction's tank: spotted within 12 cells, 2 goodwill/day while taking.
- A8 L2: worst tick on a real map with the §4 fixture <= 1 ms.
- A9 L4: owner judges the spill art and the "Fitting:" relabel of the cosmetic end-fitting button.
