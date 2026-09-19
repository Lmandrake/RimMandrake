# FIRE_ECOLOGY_BURNEDDEF_FLAMMABLE_1

Filed after harvest_log.py's new `configerror` check (reading `^Config error in`
from the live log) surfaced 12 hits naming our own `RSW_FE_*` fire-ecology
terrain — "burnedDef is flammable" — and its own baseline comment called that
"a real defect, tracked separately. NOT benign," directly contradicting
`AshLadder.xml`'s own header, which already called the identical pattern
deliberate. Two on-disk docs disagreed about a decision; this resolves it.

## spec

Determine whether `RSW_FE_{Ash_Trace,Ash_Light,Ground_Sand,Ground_Gravel,
Ground_Soil,Ground_SoilRich}` triggering `TerrainDef.ConfigErrors()`'s
"burnedDef is flammable" warning is an actual defect or expected noise from
the deliberate trace→light→heavy→deep escalating-burn ladder
(`design/Jawa/proposals/fire_ecology_deep_design.md` §3).

## Resolved (FOUNDRY, 2026-09-02) — CONFIRMED NOT A DEFECT, by source, not by re-reading the same comment

Read the actual engine methods via RimSage rather than trust either doc's
prose:
- `TerrainDef.ConfigErrors()` (`Verse/TerrainDef.cs:520-554`) only ever
  `yield return`s a string. It cannot block a def from loading or change
  runtime behavior for ANY def type — confirmed by reading the method body,
  not assumed from its name.
- `TerrainGrid.Notify_TerrainBurned` (`Verse/TerrainGrid.cs:599-613`), the
  method that actually consumes `burnedDef` when a `Fire` thing burns
  through a cell, sets `terrain.burnedDef` unconditionally with **no check
  at all** on whether that target terrain is itself flammable. There is no
  loop-protection needed because it only ever fires once per real burn
  event — a later, separate fire igniting the resulting (still-flammable)
  terrain and burning it again is the escalating ladder working exactly as
  `AshLadder.xml`'s header describes, not a malfunction.

`harvest_log.py`'s baseline comment (line ~207) called this "a real defect...
NOT benign," which was wrong — corrected in the same pass to point at this
item and stop suggesting a future FOUNDRY should chase the count down to 24.

## verify

Source-read above (`ConfigErrors()` never gates load; `Notify_TerrainBurned`
never checks `burnedDef.Flammable()`) is the proof — no live check adds
anything a source read of two short methods doesn't already settle.

## criteria

Both docs agree: the 12 `RSW_FE_*` "burnedDef is flammable" config-error
lines are permanent, by-design noise, not a defect. `harvest_log.py`'s
baseline comment corrected to match `AshLadder.xml`'s existing framing.
