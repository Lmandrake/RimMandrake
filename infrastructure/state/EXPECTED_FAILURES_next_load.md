# Expected failures + decision strings — load of 2026-09-18 (BENCH, owner-ordered restart)

Written BEFORE launch, per load-round §2/§3. Batch: enable `mandrake.rut.injections`
(XML-only, Assemblies empty) + redeploy the rebuilt EnvironmentalHazards DLL
(the ONE assembly in this load). List is 635 active (was 634; injections added
at 166, right after `mandrake.rsw.injections`; the `mandrake.rut.utinnipatches`
id from MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1 is a phantom — real id
`mandrake.rut.patches`, already active).

## Assembly signature (one assembly, so one signature)

- **EnvironmentalHazards DLL (rebuilt)** — failure looks like:
  `TypeLoadException` / `ReflectionTypeLoadException` naming
  `RimMandrake.EnvironmentalHazards`, or a static-ctor stack frame containing
  `EnvironmentalHazards` during `GenTypes`/`RebindAllDefOfs`. Anything else is
  not this DLL.

## Decision strings

| item | expected PRESENT | failure string | baseline |
|---|---|---|---|
| injections active | `mandrake.rut.injections` in Player.log's active-mod dump; count 635 held after launch | `Could not find a type` / mod dropped, count 634 | was inactive |
| EnvHazards DLL | game reaches `Bridge token:` with no EnvironmentalHazards-named exception | signature above | old DLL loaded clean |
| load itself | `Bridge token:` | `Recovered from incompatible or corrupted mods` (recovery reset persists to disk — REWRITE the list before retrying) | full list loads ~15 min |
| def dump | `[RimDefDump]` writes (marker armed; DELETE marker after harvest) | marker present, no `[RimDefDump]` | dump stale (list changed) |
