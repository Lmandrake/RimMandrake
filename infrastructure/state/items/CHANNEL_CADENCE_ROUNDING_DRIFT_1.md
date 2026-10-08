# CHANNEL_CADENCE_ROUNDING_DRIFT_1 — TerminalBiomes channel drift cadence rounds .5 differently

Found by the kernel extraction audit, `Transient/kernel_audit_20261008.md` (2026-10-08). Low severity.

## spec
Commit `d670d2c72`: old `RM_MapComponent_ChannelCurrent.CadenceFor` used
`Mathf.Max(1, Mathf.RoundToInt(baseCadence / strength))` (Mathf.RoundToInt = Math.Round, half-to-even).
New `src/RimMandrake/TerminalBiomes/Source/Kernel/RM_ChannelKernel.cs` `CadenceFor` uses
`Math.Round(cadence / s, MidpointRounding.AwayFromZero)` (called from `RM_MapComponent_ChannelCurrent.cs:424`).
At an exact .5 quotient the step is one tick slower — e.g. strength 2.0, centre lane: 22 → 23 ticks.
Same rounding change in `RM_LampWatchKernel.cs` `ThresholdTicks` (its .5 case is not realistically reachable).
Default strength 1.0 unaffected.

Fix: use `MidpointRounding.ToEven` (the default `Math.Round`) in both kernels, or accept and record as deliberate.

## verify
Kernel fuzz asserts CadenceFor(…, 2.0) equals the pre-extraction value.

## criteria
Rounding matches the pre-extraction behaviour, or the change is recorded as deliberate.
