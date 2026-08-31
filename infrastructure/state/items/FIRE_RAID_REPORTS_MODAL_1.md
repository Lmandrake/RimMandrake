
## spec
`jawa/fire_raid` sets `executed = incident.Worker.TryExecute(parms)`. A Harmony prefix can
set `__result = true`, skip the raid entirely and push a modal instead — `Leo.RaidProtectionFee`
does exactly this on `IncidentWorker_RaidEnemy.TryExecuteWorker` (proven in
`SIX_FACTIONS_NEVER_RAID_1`). The tool then reports `executed: true, arrived: []` and the
caller cannot tell "the raid was cancelled by a dialog" from "pawn generation produced zero".
That ambiguity cost this project three retracted evidence tables.

Snapshot `Find.WindowStack` before the `TryExecute` call and again after; report any window
that appeared. Same treatment is worth having on `jawa/fire_incident` and
`jawa/storyteller_fire`, which share the failure mode.

## criteria
- [ ] `jawa/fire_raid` returns a `windowsOpened` array (type name + `forcePause`) listing any
      window added during the firing, and a `blockedByDialog: true` flag when one appeared
      while `arrived` is empty.
- [ ] The `note` field says plainly that a dialog swallowed the raid and names
      `jawa/window_list_close` as the clear.
- [ ] Proven live: firing at a humanlike hostile faction that is not on the Protection Fee
      cooldown reports `blockedByDialog: true` rather than a bare `executed: true`.
- [ ] Needs a game-down window (companion DLL cannot deploy while RimWorld runs).
