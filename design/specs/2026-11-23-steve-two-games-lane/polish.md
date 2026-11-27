# Polish: the two-game lane of SteveDesktop
- Codex review 2026-11-24, not significant in ordinary operation (worker_busy_under_steve2_stop, `fault_monitor.py:393`): When Steve1 is idle and the operator creates `steve2.stop` during a Steve2 attempt, the in-memory replay returns `False` from `worker_busy()`. Both reboot paths still hold because the dispatched job remains in `steve_running()`.
