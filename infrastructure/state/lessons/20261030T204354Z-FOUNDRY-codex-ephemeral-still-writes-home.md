codex-cli 0.164 exec --ephemeral is NOT stateless: it still writes state_5/logs_2/goals_1/queue_1/memories_1 sqlite stores, tmp/, cap_sid and skills/.system into CODEX_HOME (measured live on the arena judge home 2026-10-30). Anything that needs a clean home per call must wipe those itself (judge_codex_home.wipe_call_state) and check leftovers with the same predicate.
home: chatgpt-consult
