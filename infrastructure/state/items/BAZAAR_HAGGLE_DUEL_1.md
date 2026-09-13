# BAZAAR_HAGGLE_DUEL_1 — the whole-deal patience-meter duel (slice 3)

Filed by BENCH, 2026-09-13. Spec: `design/RimMandrake/bazaar_trade_window_design.md`
§5 — note the owner's ruling: WHOLE-DEAL haggling only, per-item rejected as
monotonous ("haggling for the whole deal seems really like the only important
thing"). model: opus for the tuning pass.

## spec

One patience meter per trader session (4–9, personality/goodwill adjusted;
numbers only with RM_HagglerModule, vague face at Social 7+). Push acts on the
CURRENT DEAL TOTAL: success ~3% diminishing, costs 1 patience; crit free +
spoil (junk freebie from lowest-value stock rows, or a TRUE rumor token read
from the engine); fail costs 2 + claws back last concession; critical fail =
session lockout + −2% stinger; zero patience = lockout, no stinger; closing a
big deal restores +1. Re-basketing allowed (concessions are a %); push count
never resets. Deterministic seeding from (world seed, trader stock seed, push
index) — reload replays identically. Social XP per push (~150; ×2 crit, ×0.5
fail). Four personalities (stingy/desperate/gullible/volatile) deterministic
per trader, persisted in the Ledger with lockout/purchase memory.

## verify

Scripted push sequences via dev actions replay identically across save/reload
(the anti-save-scum property, tested not asserted). Lockout greys all haggle
controls and survives re-basketing. XP ticks. A crit freebie actually lands in
the deal and executes.

## Watch out

- Depends on BAZAAR_WINDOW_GRID_1 + BAZAAR_PRICE_ENGINE_1 (rumor tokens read
  the engine).
- The haggle delta applies inside the session-guarded GetPriceFor path —
  verify an executed deal's silver matches the displayed haggled total exactly.
- Tuning is owner-facing feel work: budget a review save with staged traders
  (options-as-savegame rule) rather than tuning by argument.
