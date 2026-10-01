# RUST_CATHEDRAL_HUM_UNMAINTAINED_1 — the Rust Cathedral hum ends two ticks after it starts

`src/RimMandrake/RustCathedral/Source/Hum/RM_MapComponent_BiomeAttitude.cs` spawns its hum layers
with `SoundInfo.OnCamera(MaintenanceType.PerTick)` and never calls `Maintain()`. Zero hits for
`Maintain()` in the file, as of 2026-10-01. Decompiled 1.6 `Sustainer.SustainerUpdate` ends a
PerTick sustainer once `TicksGame > lastMaintainTick + 1`, so every layer goes silent two ticks
after it starts.

`RM_MapComponent_ProximitySoundscape` (Creature Behaviors) copied this shape and had the same
defect. That one was fixed in `LONGSHADE_GPT_ENRICHMENT_1` by maintaining every live layer on every
tick.

## spec

- Maintain every live layer on every tick, the same fix as the proximity soundscape. Rebuild the
  DLL with its `.srchash`.

## criteria

- The hum is audible and stays on in a Rust Cathedral quicktest.
