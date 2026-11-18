# DISPATCHER_FIX_INCIDENT_BELLS_OVERWRITE

## Findings

Codex full-file review of dispatcher.py at 494774e9d3 (round 4 of CLEANER_SANITY_REVIEW_FINISH_FULL_FILES), quoted as it answered. Each is a claim: verify it before fixing, and drop any that is not real.

1. **`denied_runs`: a logging failure permanently consumes the refusal.** `_refused_last()` advances `denied_seen` before the handoff, but rollback only handles `IN.read_rows() is None`. If the ledger reads successfully and `do_conductor()` raises—for example, the Conductor log directory is unavailable—the Operations refusal never reaches `conductor_hand()`. `execute()` catches the failure and the tick saves the advanced marker. After logging recovers, that refusal is ignored instead of being handed to the Conductor.

2. **`incident_execute`: multiple incident doorbells overwrite one another.** If two incidents produce doorbells for BENCH in the same pass, with no ordinary dispatcher ring pending, both pass the pending-ring check. Each `do_ring()` replaces the same `inbox/BENCH.json`; the second destroys the first notification. Incident writes never establish pending state for this check, and neither notification is retained in `held`, although the result reports both doorbells.

3. **`incident_execute`: incident doorbells can reach a known wrong session.** A `claude -p` child or second window can re-arm BENCH’s doorbell with its own session ID—the situation explicitly checked in `one_seat()`. Ordinary dispatch then refuses to ring that stranger, but incident dispatch checks neither the armed session nor the current seat session and calls `ring()` without `session_id`. An incident therefore still reaches the other session despite the ordinary path detecting the mismatch.

4. **`decide.one_seat` / `ring`: verification timestamps precede the actual ring.** Pending rings receive `rung_at=now` and `rung_iso=iso(now)`, where `now` is the tick’s start, while inbox delivery happens after observation and potentially a 90-second ingest-lock wait. If BENCH independently takes a lease during that interval, then consumes the later ring without taking further work, `handoff_seen()` accepts the earlier lease and reports `verified`. This falsely records a successful handoff and clears the no-handoff escalation state.
