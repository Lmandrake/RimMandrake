## spec
Settle the on-screen width of rigid pipe, hose (and the new power cord) and judge it **in game** with a colonist beside
each, **before any pipe-pole art** (owner, pipes card answer 8, 2026-10-20; bars answer #22: *"Colonists don't have
arms. Need an in-game look"*). Inputs: hose width `FlatVisible`/`PlumpExtra` × `WidthScale` (shipped 1) and the unshipped
0.65 thickness proposal (`src/RimMandrake/FlowWorks/Source/Machinery/LiquidJoinRule.cs:107-111`); `HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY`
(hose a bit thinner than the pump). Output: one width spec (cells) per line kind, recorded in
`design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md` P3, staged as a review savegame.
Gates: `PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE` art, `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS` art.

## verify
- L4: owner looks at the staged savegame (pipe, hose, cord beside a colonist, two candidate widths each) and picks.
