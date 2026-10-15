# FlowWorks GPT fixes — builder A (liquid network, tanks, hoses, bottles) — 2026-10-15

Source: `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md`. Tests: `src/RimMandrake/FlowWorks/Source/SelfTest/GptFixesAChecks.cs`
(run `python3 src/RimMandrake/Utils/selftest_flowworks_stock.py`). DLLs built from clean HEAD exports (the shared tree held uncompiled WIP).

| item | sev | status | sha | notes |
|---|---|---|---|---|
| LIQUID_ROTATION_FIX_STARVED_STRANGER | HIGH | FIXED, closed | 69a9a10adb | rotation keyed per store; unservable neighbour forfeits after one yield; multi-input NextRunnable |
| BOTTLE_STOCK_MEND_FREE_REFILLS | HIGH | FIXED, closed | a6ce6a54db | fill/wash debit the pond body; spent bodies skipped; wear carried through chain steps |
| TANK_SETTLE_FIX_DOUBLE_DIPPED | MED | FIXED, closed | 72185cbc4c | per-tank sent/recv shared across components |
| TANK_CONTENTS_SALVAGE_ON_DECONSTRUCT | MED | FIXED, closed | 682b968dc5 | tank spills, drill returns to deposit, converter drops pending items |
| PIPE_ADAPTER_FIX_DEBT_NEVER_PAID | MED | FIXED, closed | 3ddf921362 | negative carry paid on next Send |
| HOSE_OFF_MEND_SLEEPWALKING_RETRACT | MED | FIXED, closed | e46ed827b5 | obstacle block gated on hoses enabled |
| HOSE_ORDERS_MEND_WAITING_FOREVER | MED | FIXED, closed | 944b9d1060 | F2/F3/F4/F5/F8 fixed; F6 not a bug (fuzz invariant) |
| HOSE_SPILL_MEND_POND_GETS_NOTHING | MED | FIXED, closed | 4ded2d06ec | pond return for drains and spills; wall-blocked end |
| DBH_WATER_MEND_ACID_ON_TAP | MED | FIXED, closed | 80ac4bda4b | F4 + F6 fixed; F5 not expressible in XML |
| LIQUID_FIRE_MEND_COVER_AND_SAVE | MED | FIXED, closed | 9bca729c18 | F1 save, F7 cover/flyers, F9 blast id |
| CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL | MED | OWNER | - | new capability (fuel moats); needs=owner |
| HOSE_LAY_POLISH_CENTRE_VS_MOUTH | LOW | PARTIAL, open | 79902641c6 | F4 fixed; F5 not a bug; F2 confirmed visual-only, live check owed |
| HOSE_IMPORT_MEND_ONE_SHOT_MISS | LOW | FIXED, closed | 8fb5afd51f | |
| LIQUID_THEFT_VERIFY_FALSE_ACCUSATION | LOW | FIXED, closed | b7d2d03dd2 | confirmed by reading; live check owed |
| WATER_NUTRITION_JUDGE_DRINKING_DINNER | LOW | OWNER | - | design question |

Coordinator extras: LiquidCorrosion.cs (worn-out apparel destroyed, not orphaned) and LiquidIgnition.cs (comments) — e23ff19890, both CLEAN.

## Notes
- A concurrent builder's RM_MapComponent_FlowStatics block was wedged between RM_Patch_NetTopologySpawn's attributes; my 72185cbc4c
  swept their then-uncommitted RM_LiquidNet.cs edit in; they fixed the placement in df46b3e3a9.
