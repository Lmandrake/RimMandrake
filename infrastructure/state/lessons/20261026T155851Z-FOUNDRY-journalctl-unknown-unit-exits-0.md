journalctl --user -u <unit> exits 0 with NO lines when systemd does not know the unit (probed 2026-10-26: bogus unit rc=0), so an empty journal reads as 'no errors/no 429s'. Check 'systemctl --user show -p LoadState --value <unit>' == loaded before trusting an empty journal (fixed in art/donor_regen_jobs.recent_429s, wave 87).
home: infrastructure/state/facts/instrument_traps.md
