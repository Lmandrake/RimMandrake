# FlowWorks P-series items, 2026-10-11 (FOUNDRY picker wAF1)

Source: `design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md` section 5 (GPT review of the hose port).
Filed by BENCH 2026-10-11 08:58-08:59Z, all owner FOUNDRY. P1-P3, P12, P13 were fixed inside the port (no items).
This picker (wAF1) takes the lowest unclaimed; agent AG takes from the top.

| P | item | state at pick | taken by | result |
|---|---|---|---|---|
| P4 | `PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD` | proposed | wAF1 | test failed first (old rule: far end 0), fixed: a backed-up pump/drill re-marks a brimming cell (`RM_DriverInputs`) |
| P5 | `FLOOD_DEBIT_MEND_DEEP_CELL_ONE_LEVEL` | proposed | | |
| P6a | `FLOOD_SWITCH_RACE_MEND_ENGINE_OFF` | proposed | | |
| P6b | `TAR_COOLING_GLASS_MEND_ENGINE_CELLS` | proposed | | |
| P7 | `FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO` | proposed | | |
| P8 | `FIRE_BURN_PULSE_PROVE_REFILL_RACE` | proposed | | |
| P9a | `HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE` | proposed | | |
| P9b | `NATURAL_HEAT_CACHE_PROVE_STALE_DAYS` | proposed | | |
| P10 | `WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST` | validated (L1) | pickAD | fixed `137743f75`, owes live A2 |
| P11 | `STATION_REACH_CENTRE_RETHINK_FOOTPRINT` | proposed | | |
| P14 | `MISSION_TANK_GOAL_REWIRE_TO_DEST` | proposed | | |

## P4 evidence (wAF1)

- Defect confirmed, not hypothetical: a driver marks an input only on a write that RAISES fill, and neither the pump
  (`RM_PumpMath.PickPour` finds no room) nor the drill (`room <= 0`) writes into a brimming cell. After a load the
  unsaved set is empty, so a brimming outlet is never re-marked; the same stall follows digging on after the 5000-tick window.
- Fix: driver-input bookkeeping moved Verse-free into `RM_DriverInputs` (`RM_PumpMath.cs`), used by
  `RM_MapComponent_Excavation`; new `NoteDriverBackedUp(IntVec3)`, called from the pump's no-room branch (brimming reach
  cells holding a providing tank's liquid) and the drill's backed-up branch. No save-format change.
- Selftest `PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD_brimming_outlet_reload_resumes_spread`
  (`FlowKernelFuzz.PumpFedChannelResumesAfterReload`, production kernel + production rule): fixed far end 2, old-rule
  probe 0. Full `selftest_flowworks_stock.py` rc 0; `winbuild.py FlowWorks` 0 warnings 0 errors.
- Owed live: a pump against a saved brimming outlet, reloaded, dug on, spreads into the extension.
