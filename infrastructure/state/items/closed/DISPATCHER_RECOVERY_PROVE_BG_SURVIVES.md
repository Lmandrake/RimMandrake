# DISPATCHER_RECOVERY_PROVE_BG_SURVIVES

The Dispatcher's recovery (dispatcher.py DEFAULT_RECOVER, fixed in b183e72775) now runs the seat launcher's own line,
`claude_bounded.sh --bg --resume <id> --dangerously-skip-permissions --name 'AGENT <SEAT>' --model <m> --remote-control 'AGENT <SEAT>'`.
Not yet proven live:
- `--bg` combined with `--remote-control` through claude_bounded.sh works at all;
- launched from the oneshot rm-dispatcher.service, the session's systemd-run scope survives the unit's exit
  (otherwise systemd kills it with the unit cgroup and every recovery burns cap for nothing);
- a recovered `--bg` session reports `state`, not `status`, in `claude agents --json`, so it may never read "idle"
  to the wake path.

Until this passes, keep `recover_dead` false for every seat under --apply.
Review evidence: D:\ClaudeWork\rimmandrake\review_dispatcher\gpt_a.md (finding 5).
