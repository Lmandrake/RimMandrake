The codex scratch homes used by facing_regen (codex_home_facing_regen, _w3, ramp2 under ClaudeWork) hold stale auth: 401 'refresh token already used' (last_refresh 10-09). The shared home (no --codex-home) worked, serially. Check a home's last_refresh before a batch; do not copy auth.json into a scratch home that another process refreshes.
home: generating-images
