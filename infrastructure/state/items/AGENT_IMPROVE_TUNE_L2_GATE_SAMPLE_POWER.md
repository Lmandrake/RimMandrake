## criteria
- Decide, from measured no_signal rates at L1/L2 or before the ramp first reaches L2, whether the 6-pair held-out sample is enough for the L2 gate, which applies only a proven keep.
- If not, change the sample or the gate's reading of no_signal, and record why on the ledger.

## why
With noise_floor_v1 a general verdict needs 5-0 or 6-0 at 6 held-out pairs. The sign bar alone calls a change that truly wins 80% of decided pairs about 20% of the time (12 pairs: 46%), computed for 20% ties, so L2 would refuse most real improvements. The ramp is at L0 today, so nothing is refused yet. See design/RimMandrake/daily_agent_improvement_2026-11-02.md section 4.3.
