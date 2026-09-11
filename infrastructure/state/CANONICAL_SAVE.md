# The canonical savegame is FROZEN

```
frozen:        true
frozenOn:      2026-09-10
frozenBy:      owner
```

**File**: `CANONICAL_ASHKARR_2026-09-09.rws`, in the live Saves folder —
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_2026-09-09.rws`.
Not tracked in git (a savegame is a binary/XML blob, not source — this doc is
the provenance record CLAUDE.md's Transient rule asks for).

**frozenMeaning**: this is the canonical state of the campaign as of the
gravship thruster-bay repair (fire + behemoth damage, astrofuel pipes
rebuilt, two new astrofuel tanks wired in and filled, Twice-Kin resurrected —
CLAUDE_SESSION session_01Bik3t3cB32AYwy1fCpTqsR, 2026-09-10). **Do not
`rimworld/save_game {"saveName": "CANONICAL_ASHKARR_2026-09-09"}` over this
file** without the owner's say-so — that silently discards this checkpoint,
the same way any other frozen artifact's generator would.

**The name stays `CANONICAL_ASHKARR_2026-09-09` even on a later resave** —
that is the established identity (see `Transient/save_canonical.py`), not a
literal "date last written" stamp. Every prior resave already followed this:
back up the live file first (`.rws.bak-pre-<change>-<date>`, several already
in the Saves folder), confirm the backup's size, then re-save, then stat
BOTH files yourself — the live file's mtime and a size delta, never the
tool's self-reported `sizeBytes` (`rimbridge` skill: `saveName` has been
measured to silently overwrite the wrong slot before).

**To unfreeze**: the owner says to update the canonical checkpoint again.
Then: back up the current file the same way, re-save under this same name,
verify by stat, and update `frozenOn` above (or drop this file's frozen
status entirely if the owner says the doctrine itself is retired).

## Backup chain (Saves folder, `CANONICAL_ASHKARR_2026-09-09.rws.bak-*`)

Newest first — a resave's own backup, taken immediately before that resave:

- `.bak-pre-gravship-repair-2026-09-10` — this freeze's pre-save backup (26,330,447 bytes)
- `.bak-pre-sea-enrichment-2026-09-10`
- `.bak-pre-donor-retire-resave-2026-09-10`
- `.bak-doorsexpanded-resave-2026-09-10`
- `.bak-preresave-20260910`
- `.bak-asimov-20260910`

Plus `Transient/desert_band_repair_backup_2026-09-09/CANONICAL_ASHKARR_2026-09-09_PRE_DESERT_BAND_REPAIR.rws`,
committed in-repo as an exception (the Transient rule's shelf life applies —
it is not a substitute for the live backup chain above).
