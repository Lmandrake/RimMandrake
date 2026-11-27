On WSL, /proc/<pid>/io read_bytes counts reads from /mnt/c and /mnt/d (9p) in full (shell32.dll: 8,189,472 of 8,189,472 bytes), so a per-process read census sums to more than /proc/vmstat pgpgin (1,434 GB against 563 GB in one hour on Archmagi). pgpgin is the ext4 disk only.
item: RIMMANDRAKE_FIND_LOAD_USERS_RM_TIMERS_ONLY_TEN_PERCENT
home: infrastructure/state/facts/instrument_traps.md
