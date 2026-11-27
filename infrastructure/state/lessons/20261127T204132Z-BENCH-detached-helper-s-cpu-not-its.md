A detached helper's CPU is not in its rm-detached-*.service unit: its claude process and tool commands run in claude.slice/claude-seats.slice/claude-seat-<SEAT>-rm-detached-*.scope (parts seat and claude-code-bash). A census by systemd unit that reads only the rm-detached service shows the helpers at about 1% when they used 61% of the CPU.
item: RIMMANDRAKE_FIND_LOAD_USERS_RM_TIMERS_ONLY_TEN_PERCENT
home: infrastructure/state/facts/instrument_traps.md
