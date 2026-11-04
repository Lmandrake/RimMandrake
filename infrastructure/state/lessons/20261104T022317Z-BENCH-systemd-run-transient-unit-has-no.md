A systemd-run transient unit has no ~/.local/bin on PATH, so claude-account and claude fail with FileNotFoundError; pass --setenv=PATH and read the first real run's log before calling it armed.
