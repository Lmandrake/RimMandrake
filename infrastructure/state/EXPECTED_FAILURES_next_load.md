# Expected-failure signatures — THE BIG DUMP LOAD, written 2026-09-03 BEFORE launch (BENCH)

Deploy batch: every drifted mod at `e9373f4f` + companion `build.py --gm` (e9373f4f8df6).
Each assembly fails distinguishably: a `ReflectionTypeLoadException`, `TypeLoadException`
or `Could not resolve type` line NAMES the assembly or its namespace. One signature each;
a log line matching none of these is a NEW failure, not part of this batch.

| assembly | signature string in Player.log |
|---|---|
| JawaArmoury.dll | `JawaArmoury` |
| RuthlessPursuingMechanoids.dll (EmpirePursuit fork) | `RuthlessPursuingMechanoids` |
| FireEcologyHook.dll | `FireEcologyHook` |
| RimMandrakeGraffiti.dll | `RimMandrakeGraffiti` |
| Inhabited.dll | `Inhabited` (namespace RimMandrake.Utinni / mapgen: `INHABITED_TILEMUTATOR_NO_ENTRY_1` means its GenSteps never fire — silence from this mod's mapgen is KNOWN, not a pass) |
| RimMandrakeStructureInjections.dll | `RimMandrakeStructureInjections` |
| RimMandrakeTheftHauler.dll | `RimMandrakeTheftHauler` |
| RimMandrakeVisibility.dll | `RimMandrakeVisibility` |
| RimDefDump.dll | `RimDefDump` — plus the POSITIVE checks in COLD_LOAD_RUN_SHEET_2 "THE BIG DUMP LOAD" section |
| JawaBench.BridgeTools.dll (companion, sibling of Mods\) | `JawaBench` — gate is the ready-line census, not a literal count |
| (inactive this load: Droidworks.dll, WeatherSuiteHook.dll — deployed but not in ModsConfig; ANY log line naming them is unexpected) | `Droidworks` / `WeatherSuiteHook` |

XML/def drift (Jawa_Patches roster, IonWeapons hediff, Inhabited defs, StructureInjections
batches, AshkarrInhabited manifest): attribution-free config tier per the load-round skill;
failures name the def or patch file directly.
