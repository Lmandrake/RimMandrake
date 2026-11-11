## spec
found-by: GPT full-file review during PUMP_SOURCE_FIX_REJECTS_PARTIAL_DRAW (2026-11-02; receipt D:\ClaudeWork\rimmandrake\scratch\codex\consult-20261102-053911-1953658, copy D:\ClaudeWork\rimmandrake\scratch\pspd\gpt_review.md). Verified by reading TryDraw.
Severity: MINOR. Pre-existing; not touched by that item.

`Building_LiquidPump.TryDraw`, outflow branch: when `amt <= 0 || (!LevelExact && amt < units)` the code does `usedOutflows.Add(oi); continue;`, consuming the OUTFLOW's turn for the cycle although only the SOURCE is short. Scenario: exact-level off, a 900 dL channel cell first in source order, a full cell second, one usable outflow, no tank room: PumpNext picks source 0 + the outflow, the guard burns the outflow, source 1 then finds no outflow and no tank room → nothing moves, every cycle.
Fix direction: reject the (source, outflow) pair, not the outflow — e.g. mark the source dead for the cycle when the shortfall is the source's (avail < units), and burn the outflow only when the outlet room is the limit. Add a selftest of PumpNext ordering with that scenario.
