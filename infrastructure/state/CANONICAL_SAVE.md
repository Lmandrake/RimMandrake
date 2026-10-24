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
superseded as canon by the start save on 2026-09-12. It is kept, with one `.bak`,
in `Saves/_cleanup_archive_2026-09-14/` (measured 2026-10-15), never loaded as canon.

## Which save is current — measured 2026-10-24

Appended by FOUNDRY (offline read, no game). The frozen block above is unchanged; only
the owner unfreezes it. This section records which file the evidence says is the newest
and most reliable world save, so nobody has to rebuild the answer from 40 file names.

**Current world save: `Saves\ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws`**
(13,564,631 bytes, mtime 2026-10-20 22:14 PDT, sha256 `24be08a2d76c732c…`; it matches the
copy in `D:\ClaudeWork\backups\Saves_20261023T0356\` byte for byte).

Evidence, in order:
- Owner card, 2026-10-20 9:38 PM PDT: "Dev start save -> PARITY_QUIET_R2", with labels70 and the
  region-import fix still to apply and re-save (OWNER.jsonl, note on `TIDAL_LOCK_RESTORE_SUN_STILL_COMMUTING`,
  2026-10-21T04:41:59Z).
- R2 was saved after the Celestial Rogues/Salvagers ban; check-save PASS (`CELESTIAL_ROGUES_SILENCE_GROUNDED_IN_ORBIT`
  closed 7ffc34b, 2026-10-21T03:52Z). Lineage: `_LOCKED` -> `_MOUNTAINS` -> `_RECORDLINKS` -> `_PARITY`
  -> `_PARITY_QUIET` (initialMapSize 325, `HOME_MAP_SIZE_RESTORE_ROOM_TO_STRETCH` 3742c2b6b; tidal lock verified,
  `TIDAL_LOCK_RESTORE_SUN_STILL_COMMUTING` 898817fa1) -> `_R2` -> `_R3`.
- R3 = R2 + labels70 applied live, dry run and readback both 0 mismatches over 71 features
  (`LABELS_SHRINK_APPLY_LIVE_SEVENTY_PERCENT` closed b262d9b9f, 2026-10-21T05:20Z, "saved in ..._PARITY_QUIET_R3").
  No separate "region-import fix" event exists in the ledger; the only labels/region work is the gate fix 4eecc31bc,
  which was applied in R3. Whether the owner meant anything more than that is UNMEASURED.
- `design/Jawa/worldbuilding/big_repaint_plan_2026-10-21.md` §1a measured R3 as "the de facto dev start":
  mod set MATCH with the 325 list, 21,872 tiles on our defs, 0 not ours, 0 unresolved.
- Re-read today: R3 has 325 `<modIds>`, `<worldPresetName>TidallyLocked`, `<initialMapSize>(325, 1, 325)`.
- **No repaint save exists.** `ASHKARR_DEV_START_2026-10-21_REPAINT.rws` is not in the Saves folder or the backups.
  `BIG_REPAINT_FINISH_ONCE_AND_FOR_ALL` and `REPAINT_SAVES_RETIRE_THREE_GHOST_STARTS` are still `proposed`
  (filed 2026-10-21, no later events). When the repaint lands, its save replaces R3 as current.
- Saves written after 10-21 (Autosave-*, `RM_fw_hose_proof_*`, `rm_proof_*`) are test sites, not world saves.

**`CANONICAL_ASHKARR_START_2026-09-12.rws` (the frozen file above)** stays as the record the owner froze. It is
not usable as a planet on today's list: 616-mod set, fingerprint MISMATCH, 1,903 tiles on 3 hashes no current def
has (repaint plan §1a).

**Superseded** (kept on disk, never deleted here; the full list of 40 names is in
`/home/mandrake/.seat-tmp/FOUNDRY/superseded_saves.txt`):
- every other `CANONICAL_ASHKARR_START_*` variant (`_donorfree`, `_donorfree_p6b`, `.DONORFREE_CANDIDATE_2026-10-18`,
  `2026-10-18_DONORFREE`, `_REPAIRED`, and each of their `_AREAFIX`/`_AREAFIX2` copies). This was the 536/542-mod
  donor-free line from 10-15 to 10-19. The world remake replaced it, and AREAFIX2 fails on the PAINT list with an
  error storm (Orbit2 PlanetLayerDef missing; OWNER.jsonl game GOING_DOWN, 2026-10-20T07:10Z);
- every `.rws.bak-*` beside them (pre-edit backups of the frozen file and of 10-18_DONORFREE);
- `ASHKARR_DEV_SHIP/LANDED/FOUNDERS_2026-10-20` and the FOUNDERS `.bak-pre-founder-import`. They are the PAINT 83-mod
  set, from before the mountains and the lock fix, with 31k donor mutators; `REPAINT_SAVES_RETIRE_THREE_GHOST_STARTS`
  moves them out once the repaint lands;
- `ASHKARR_FALLLINE_LABEL26_2026-09-21`, `ASHKARR_LABELSIZES_2026-09-26`, `ASHKARR_LABELSIZES_DRAWCENTERFIX_2026-09-26`
  (September label experiments on the old world).

**Tool pointers.** No tool in `src/` names a Saves file that is missing. `world_hill_preview.py` reads the repo copy
`world/ASHKARR_DEV_START_2026-10-20.rws`. That copy exists but is stale; the REPAINT_SAVES item replaces it.
`world_peak_decals.py` defaults to R3. `ashkarr_settle.py`, `world_layers_export.py`, `vanilla_beast_carriers.py`,
`saves_prune.py` and `Pyrelands/diag/save_world_check.py` default to the frozen 09-12 file, and
`save_adoption_check.py` defaults to `.DONORFREE_CANDIDATE_2026-10-18`. Those files exist, but they are not the
current world. Give these tools `--save`/the R3 name until one dev-start pointer is written. `canon.yml`
`start_savegame` still names the frozen file, and only the owner can change that.
