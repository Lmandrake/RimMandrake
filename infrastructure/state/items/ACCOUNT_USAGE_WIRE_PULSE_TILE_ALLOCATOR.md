# ACCOUNT_USAGE_WIRE_PULSE_TILE_ALLOCATOR

Owner, 2026-10-26: "The system should be able to confirm how much is left on each of the three accounts it
uses. This should be provided to rimpulse or any other rimflow need."

The instrument exists (`src/RimMandrake/Utils/account_usage.py`, sha d738710ad9): headless `claude -p /usage`
per account, every 15 min on `rm-account-usage.timer`, MEASURED / ESTIMATE / UNMEASURED labelled per record.

## Owed (BENCH; the stream-metrics builder's files, not account_usage.py's)
1. **RimPulse tile**: one row per account: week % left + hours to week reset, session % left + hours to
   session reset, source label (an ESTIMATE must read as one, never as a measurement), age; greyed when `stale`.
2. **Allocator input** (`streams.py allocate`, work_allocation_framework_2026-10-26.md R8 token pace):
   per account `week_pct_left` against `hours_to_week_reset`, instead of (or alongside) `pulse/usage.py`'s panel.
   Percent only: absolute tokens left are not reported by /usage.

## Contract (schema 1)
- `python3 src/RimMandrake/Utils/account_usage.py now --json` or `import account_usage; account_usage.read_now()`
  -> `{"schema", "updated", "accounts": {name: {...record, week_pct_left, hours_to_week_reset,
  session_pct_left, hours_to_session_reset, age_min, poll_age_min, stale}}}`.
- Files: `D:\ClaudeWork\rimmandrake\account_usage\latest.json` (newest per account) and `series.jsonl`
  (append-only, one record per account per poll; keys = `account_usage.RECORD_KEYS`); dir overridable by
  `RM_ACCOUNT_USAGE_DIR`.
- `*_pct_used` are percent USED, as /usage shows; `*_pct_left` is null once that window's reset has passed.
