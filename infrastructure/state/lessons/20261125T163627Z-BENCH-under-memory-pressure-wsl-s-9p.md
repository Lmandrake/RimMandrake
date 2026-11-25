Under memory pressure WSL's 9p reads of /mnt/c and /mnt/d fail with OSError ENOMEM (6 in 08:10-08:46 PST on 2026-11-24). A reader that turns every OSError into an empty list then reports healthy data as 'no record': ops_watch alarmed 5 fresh families blind. Catch FileNotFoundError as the empty set and keep any other OSError as could-not-look.
item: OPS_SENSE_FAMILY_READING_RESTORE_XAOE
home: infrastructure/state/facts/instrument_traps.md
