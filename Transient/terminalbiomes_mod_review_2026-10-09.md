# TerminalBiomes Mod Settings full-file review 2026-10-09

File: `/home/mandrake/rm/bench/src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs` (684 lines). Verdict: NOT marked clean (significant findings; no source edit made).

## Passed
- Every setting Scribed (55 fields, ExposeData) with a default equal to the field initialiser (shipped behaviour). No stale keys.
- Window draws every setting with label + tooltip; worldgen-affecting ones labelled (Thurlsponge, Route B flora, cross-biome).
- Master/biome gating via *Active properties is correct where read; Scald gates reach shared assembly via RM_MechanicGates (registered in ctor).
- Load order: Mod ctor only reads settings and registers lambdas; DefDatabase touched only in [StaticConstructorOnStartup] applier (GetNamedSilentFail, null-safe). No NRE found.

## Findings (significant)
1. `twilightChainAvailability` (3-way radio) has NO reader anywhere in src/ - control does nothing, tooltip implies it restocks cages/lamps.
2. `twilightChartsAgeEnabled` ("Charts age") has NO reader - tooltip claims charts never go stale when off.
3. `twilightPaneStrikeFrequency` slider/tooltip claim to scale the pane strike; only scales flake litter (VeilFall).
4. `twilightSuulkPressureScalingEnabled` has no reader (tooltip honestly says so).
5. `BankWorksActive` property has zero readers (dead; its comment says the bank works answer to master).
6. Cage passability flips ThingDef.passability every settings frame with no map cache invalidation (tooltip says next rebuild).

All of 1-4 and 6 are already filed as TERMINAL_SETTINGS_CONSUMERS_WIRE_1 ("wire each control or relabel it honestly") - a wire-vs-relabel choice, FOUNDRY-owned, so left alone. File stays DIRTY; re-review after that item lands.
