Claude exits 143 (not a signal death) on SIGTERM, measured via pty; claude_bounded passes it through, so tile tails can key on $? -eq 143 to close fleet-stopped tabs (exit 0 needed: WT closeOnExit graceful). Installed WT profiles need install_wt_seat_profiles.py re-run to pick up SHELL_TAIL. Also: queue_lint ARG_WRITER_RE now anchors writer words to command position.
home: NONE
