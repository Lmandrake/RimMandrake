# WB-game-canonical-save-20261126-181519

Home: game:canonical-save. Canonical start save: `ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws` (canon.yml
`planet.start_savegame`); the 09-12 frozen file is record only (owner card 2026-11-06) and is not touched.

- Step A done: stale 1, done already 1, keep 1.
  - `SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS`: stale. R3 holds 41 `Precept_Relic`, none on a VWE def and none of the five
    named precepts; VWE is not in R3's 325 modIds. The repair targeted the 09-12 save, which is record only now.
  - `UNWANTED_FACTIONS_SILENCE_NOT_DELETED`: done already. `banned_factions.py check-save` PASS on R3 (CombHolds,
    TradersGuild, Salvagers BANISHED; CASacrilegHunters ABSENT), `check-repo` PASS; SHIP/LANDED/FOUNDERS retired
    2026-11-02 (`REPAINT_SAVES_RETIRE_THREE_GHOST_STARTS`).
  - `SLAUGHTER_ROWS_PRUNE_GHOSTS_IN_PEN`: keep. R3 names 131 deleted prune defs 272 times, wider than the ticket:
    230 food-restriction filter rows, 31 auto-slaughter rows, 4 drug-policy rows, 2 worn-apparel stuffs, 2 inventory
    things, and the whole `RSW_PustuleHornets` faction (loadID 17, 24 relation rows). Engine: one
    `Could not load reference` Log.Error each (ScribeExtractor.DefFromNode), plus `Some factions were null after loading.`
- Step B: check `cmd:python3 src/RimMandrake/Utils/save_ghost_defs.py check world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws`
  (FOUND 272 on the parent).
- Step C: tool `src/RimMandrake/Utils/save_ghost_defs.py` + `selftest_save_ghost_defs.py`; stripped copy at
  `D:\ClaudeWork\scratch\rimmandrake\prune42_ghosts_2026-11-26\R3.rws` (618 lines removed, 2 stuff lines repointed to
  `Leather_Plain`). Backups: `D:\ClaudeWork\backups\saves_pre_strip_prune42_ghosts_2026-11-26\` and
  `…R3.rws.bak-pre-strip-prune42-ghosts-2026-11-26` beside the Saves file.

Next: see the last PROGRESS note on `SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS`.
