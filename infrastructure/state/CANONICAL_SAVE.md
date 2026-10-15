# The canonical savegame is FROZEN

```
frozen:        true
frozenOn:      2026-09-12
frozenBy:      owner
```

**File**: `CANONICAL_ASHKARR_START_2026-09-12.rws`, in the live Saves folder —
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws`.
Not tracked in git (a savegame is a binary/XML blob, not source — this doc is
the provenance record CLAUDE.md's Transient rule asks for). The same file is
`planet.start_savegame` in `infrastructure/state/canon.yml`, which carries its
full provenance.

**frozenMeaning**: the frozen world with the player start on it (The Utinni at
tile 17007 with the Five Founders). Owner, 2026-09-12 10:20: *"record this save
game as the new canonical frozen start savegame"*. **Do not
`rimworld/save_game {"saveName": "CANONICAL_ASHKARR_START_2026-09-12"}` over
this file** without the owner's say-so — that silently discards this checkpoint,
the same way any other frozen artifact's generator would.

**The name stays `CANONICAL_ASHKARR_START_2026-09-12` even on a later resave or
in-place edit** — it is the established identity, not a "date last written"
stamp (the live file's mtime is later than its name). Every edit so far backed
up the live file first (`.rws.bak-pre-<change>-<date>`, in the Saves folder),
confirmed the backup's size, then wrote, then stat'd BOTH files — the live
file's mtime and a size delta, never the tool's self-reported `sizeBytes`
(`rimbridge` skill: `saveName` has been measured to silently overwrite the
wrong slot before).

**To unfreeze**: the owner says to update the canonical checkpoint again.
Then: back up the current file the same way, re-save under this same name,
verify by stat, and update `frozenOn` above (or drop this file's frozen
status entirely if the owner says the doctrine itself is retired).

## Backup chain

The backups sit beside it as `CANONICAL_ASHKARR_START_2026-09-12.rws.bak-*`;
list the Saves folder for the current set rather than trusting a copy here.

## The earlier save

`CANONICAL_ASHKARR_2026-09-09.rws` (the world before the player start existed
on it, last resaved after the 2026-09-10 gravship thruster-bay repair) was
superseded as canon by the start save on 2026-09-12. Neither it nor any of its
`.bak-*` files is in the Saves folder (measured 2026-10-15).
