# PYRELANDS_TERRAIN_BURNDEF_1

## spec
Diagnose "RM_FE terrain burnedDef flammable config errors on load" — filed
thin, `needs: offline`, `kind: defect`, no detail.

## finding
The live `Player.log` and `Player-prev.log` (2026-09-18) show exactly six
recurring lines, each pair repeating once per HugsLib/defs reload pass:

```
Config error in RM_FE_Ash_Trace: burnedDef is flammable
Config error in RM_FE_Ash_Light: burnedDef is flammable
Config error in RM_FE_Ground_Sand: burnedDef is flammable
Config error in RM_FE_Ground_Gravel: burnedDef is flammable
Config error in RM_FE_Ground_Soil: burnedDef is flammable
Config error in RM_FE_Ground_SoilRich: burnedDef is flammable
```

These are not a new/unhandled bug. They are the exact, already-diagnosed,
already-ruled-on condition documented in the source itself:

- `src/RimMandrake/Pyrelands/Defs/TerrainDefs/AshLadder.xml` (header comment,
  "confirmed live 2026-09-01") — `RM_FE_Ash_Trace` and `RM_FE_Ash_Light` are
  non-terminal rungs of the ash ladder (Trace -> Light -> Heavy -> Deep),
  each deliberately flammable with `burnedDef` pointing at the next rung.
  Vanilla's `Verse/TerrainDef.cs ConfigErrors()` assumes `burnedDef` is
  always a terminal end-state and flags any non-terminal, flammable
  `burnedDef` target — advisory only, never blocks load, and
  `TerrainGrid.Notify_TerrainBurned` fires regardless.
- `src/RimMandrake/Pyrelands/Defs/TerrainDefs/ScorchableGround.xml` (header
  comment, "owner ruled 'accept', 2026-09-03") — the four scorchable ground
  clones (`RM_FE_Ground_Sand/Gravel/Soil/SoilRich`) all set `burnedDef` to
  `RM_FE_Ash_Trace`, itself flammable, for the same reason. The file
  explicitly says: "DO NOT 'FIX' THIS BY ZEROING Flammability OR CLEARING
  burnedDef. That deletes the fire ecology this mod exists to provide.
  Twelve log lines are the accepted price" (six errors × the two-pass log
  write vanilla does per load, matching the twelve raw hits across both
  files above).

Cross-checked every `burnedDef` reference under `src/` (RM_FE and the
unrelated RUT_ terrain families in RotSporeKit/UtinniPatches): every target
(`RM_FE_Ash_Light`, `RM_FE_Ash_Heavy`, `RM_FE_Ash_Deep`, `RM_FE_Ash_Trace`,
`BurnedWoodPlankFloor`, `RUT_TarSpent`) resolves to a real def, no dangling
or typo'd reference exists, and the live log carries no config-error line
for any def outside the six already-documented ones. `RM_FE_FirebreakLine`
(`burnedDef/>`, empty, `Flammability=0`) and `RM_FE_Ash_Deep` (no
`burnedDef`, `Flammability=0`) are the correctly-built terminal ends and
throw nothing.

## verify
- `git log -p` on both files shows the accept rulings predate this item by
  weeks (2026-09-01, 2026-09-03).
- `Player.log` / `Player-prev.log` (2026-09-18, most recent two loads) show
  only the six known lines, no new ones.
- No code change made — the owner already ruled this stays exactly as
  written, and the comments in-file already carry that ruling so a future
  agent doesn't re-open it as a live defect.

## outcome
No defect. This item duplicates an already-ruled, already-documented,
intentional design tradeoff. Closed with no code change.
