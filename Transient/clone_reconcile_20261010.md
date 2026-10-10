# Clone reconcile 2026-10-10
HEAD was 61 behind origin/main, 0 ahead. 265 dirty entries at start.
- (a) identical to origin/main (leftover, discarded): 70 modified incl. all ledger/art shards (no unique lines), plus 79 untracked files identical to origin.
- (b) real local change: 1 -- Transient/modcheck/fixtures.json (tick 300 vs 2501, test state; discarded, in backup).
- deleted (D) 25: all absent on origin (landed there), deletion is a leftover; follows origin.
- (c) genuinely untracked, left in place: ~124 files (Transient/.probe, .b4_*, conversations/, deployed/config/ModsConfig.before-*, northstar result jsons).
- Backups: branch backup/foundry-local-20261010; files /home/mandrake/rm/_foundry_dirty_backup_20261010/
- Result: git reset --keep origin/main; HEAD == origin/main.
