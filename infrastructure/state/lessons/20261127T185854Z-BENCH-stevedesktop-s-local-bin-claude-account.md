SteveDesktop's ~/.local/bin/claude-account is a copy made by accounts/install.sh, not a link: a fix in MandrakeWorkflows skills/claude-remote-control reaches the warm timer only after install -m 755 of scripts/claude_account.py. On 2026-11-27 the copy was a month stale and still warmed with --model haiku (banned). Compare with cmp before you trust what the timer runs.
item: WARMTIMER_HARDEN_SPARE_LIVE
home: skills/claude-remote-control (MandrakeWorkflows) references
