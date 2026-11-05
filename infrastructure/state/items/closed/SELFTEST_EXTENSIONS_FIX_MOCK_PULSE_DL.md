## spec
found-by: relentless builder on FILLIN_PROOF_FIX_ORDER_NEVER_FILLS, 2026-11-05.

python3 src/RimMandrake/FlowWorks/northstar/selftest_extensions.py exits 1 on origin/main 7104dc958f before any change: 'clean mock run not green'.
Mock V2.run_live rows FAIL: A0_instrument (pulse_contract: 'flowworks_pulse sent no per-cell dl', validation_v2.py:2113), E3_budget_exhaustion, E3n_budget_off_supplies, E6_rain_fills_unroofed (same), E5n_sinks_off, E5_sinks_back_on, E2_rerun_determinism.
Likely the mock pulse (fakegame.py) never gained per-cell dl/sumDl after the pulse contract required it. Fix the mock, not the contract.
