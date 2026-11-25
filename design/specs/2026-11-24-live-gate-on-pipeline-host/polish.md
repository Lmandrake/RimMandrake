# polish: the close gate's live check on the pipeline host

- Off the pipeline host, a selftest that drives `rimflow close` with a line that fails locally now also asks Archmagi over ssh (about 2 s): the verdict is still right, but such a test is not hermetic; set RIMFLOW_LIVE_SSH empty in those tests if one ever flakes. (2026-11-24)
- CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM closed with --live hook=conductor_goodbye.py; the hook its commit touched is block_agent_over_slots.py. Both are wired; the promise names the neighbour. (2026-11-24)
