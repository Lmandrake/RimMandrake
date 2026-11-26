A spawn that one PreToolUse hook denies can still hold a slot: a helper's Agent call refused by block_unbounded_agent.py (subagent_type general-purpose) or another subagent-type hook still left a 90 s spawn reservation from block_agent_over_slots.py (both PreToolUse Agent hooks run, the slot gate reserved before the other refused), so the next, corrected spawn reads slots_full with 'reserved-HHMMSS' until the reservation ages out. Workaround: wait for spawn_reservations.json age > reserve_s (RESERVE_S, 90 s), then spawn; better, spawn a bounded agent type the first time. Fix idea: the slot hook should reserve only after the type check passes (or check subagent_type itself).

Sightings (three):
- 2026-11-12 ~08:38-08:42Z on the ExplosiveKnockback exam: with CONDUCTOR_WINDOW N=2 the corrected rm-judge spawn was refused 'Running: <me>, reserved-0' for ~90 s, three times.
- Filed 2026-11-23: the same; a later hook (the unbounded-context blocker on general-purpose) refused the call after block_agent_over_slots.py had reserved the slot; the next spawn read slots_full with 'reserved-HHMMSS'.
- 2026-11-25 about 7:45 PM PST (2026-11-26 ~03:45Z), the Conductor's run of RIMMANDRAKE_RUN_WEEKLY_CRYSTALLIZE_2026W48: 4 spawns refused by the subagent-type hook left 4 'reserved-' slots; the next spawns read slots_full; it cleared within ~3 min. At 7f1dfe0c7d (settings last changed 90cda010d8) .claude/settings.json lists block_unbounded_agent.py before block_agent_over_slots.py, and the slot was still reserved, so the listed hook order does not prevent it.
item: NONE
home: .claude/hooks/block_agent_over_slots.py

Fixed 2026-11-25 at aec65b3540: `block_agent_over_slots.py` writes no reservation for a spawn that `block_unbounded_agent.py` refuses (selftest case (c)).
