# BAZAAR_BANTER_LINES_1 — banter: authored pools first, dormant Oracle consumer (slice 5)

Filed by BENCH, 2026-09-13. Spec: `design/RimMandrake/bazaar_trade_window_design.md`
§6. model: opus (prompt/validation quality is the product). Owner-ruled
posture: the LLM consumer ships DORMANT until ORACLE_EXPERIMENT_SPIKE_1's live
proof lands; authored pools are the day-one experience.

## spec

Part A (ships alone, complete): authored line pools per (personality × event
type) — push won/lost/crit/lockout/greeting/closing — rendered in the banter
strip. Part B (dormant behind a settings flag + Oracle-proof gate): the fourth
Oracle consumer riding OracleClient's claude -p subprocess: system prompt =
persona + hard rules (~160 chars, no invented game terms); stdin = the
deterministic event + up to 3 TRUE engine facts + Ledger memory; async with
~8s timeout, fallback shows immediately, fresh line used on the NEXT exchange;
one outstanding call per session, budget 5/session under the Oracle global
kill-switch; CLI missing → detect once, silent disable for the save session.
Both Oracle laws bind: text authority only; game whole with LLM absent.

## verify

CLI absent: every event type produces a pool line, zero log spam. CLI present
+ consumer enabled: the stub-marker discrimination trick (per the Oracle
verification plan) proves a real delivery vs a fallback; a "real intel" line's
fact matches the engine's actual multiplier state.

## Watch out

- Depends on BAZAAR_HAGGLE_DUEL_1 (events) and the OracleClient rewrite being
  live-proven — do not enable Part B before that item closes.
- The LLM may never decide or phrase a NUMBER the UI treats as data — lines
  are display-only; validate length and strip anything resembling a price.
