`timeout` does not exist on macOS — use `curl --max-time` (or `gtimeout`). A bare `timeout` fails with `command not found` AND resets the shell's cwd.
