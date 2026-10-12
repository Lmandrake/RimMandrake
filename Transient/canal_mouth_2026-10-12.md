# CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY — trace 2026-10-12 (BENCH subagent, offline)

Live input: Transient/bench_live_20261012/ext_dry.json chain plot_C_limitless_canal / canal_fill_front.
nextPulseTick -1 -> 208516 over 750 ticks; body 1 stock 300 -> 297.081238, recededCount 0 -> 1; mouth (159,88) depth 1 fill 0.

## Where the 2.918762 went
3 whole levels debited (one per pulse through the single D=1 mouth) less ~0.08 refill accrued on pulses 2-3 (Refill skips a
full body, so pulse 1 accrues nothing). The 3 levels are in the channel's LAST three cells (offline, production kernel).

## Root cause
HARNESS. Water races: in RM_FlowKernel.ResolveComponent the mouth takes a level from the source, and the next recipient
(nearest-source-first order) pulls it on in the same pulse (brimming equal-depth donor allowed; MayFlowBetween hop 1 -> 2),
so a dead-end D=1 channel fills from the far end back. Designed ("water near-instant", FL-2 left water untouched).
No conservation leak: ledger balanced, debit == levels in channel.

## Fix + selftest
- SelfTest `CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY_dead_end_fills_from_far_end`: after 3 pulses `0000000111`, debited 3.000,
  in channel 3; after 10 `1111111111`, stock 290.0; worst imbalance 0.000.
- extensions.py plot_C: canal_fill_front judges the channel + conservation (|debit - levels| < 1), not the mouth cell;
  canal_holds_only_channel skips the painted source cells beside the mouth.
- No kernel/DLL change.

## Shas / DLL
(pending)
