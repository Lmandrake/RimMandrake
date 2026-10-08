# Regression fixes 2026-10-08

- FLOOD_LEDGER_LOAD_LOSS_1: ExposeData lists now fields (same Scribe labels); `Ledger.Restore` in kernel; fuzz round trip + source guard. 2830452b5
- CANYON_FLOOD_ROAR_SILENT_1: MaintainRoar called each tick that began in Flooding; source guard in selftest_floodedcanyon_fuzz.py. 2830452b5
- GRIPPER_THEFT_FLOOR_PRECISION_1: float quotient restored, clamp kept; fuzz oracle (which encoded the double bug) fixed; explicit 0.6/0.3/0.1 case. b54c172cb
- CONDENSER_SLOT_SELF_RELATION_1: IsPlayer guard on HostileTo/PlayerGoodwill; source guard in selftest_weepingstones_fuzz.py. c8d0e3baf
- CHANNEL_CADENCE_ROUNDING_DRIFT_1: restored half-to-even in ChannelKernel and LampWatchKernel (old behaviour; no evidence new is better); explicit .5 cases. 8ba431e90
- DLLs rebuilt with clean stamps (source 8ba431e9078d).
