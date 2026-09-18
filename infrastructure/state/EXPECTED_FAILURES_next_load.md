# Expected failures + decision strings — load 2 of 2026-09-18 (BENCH, FlowWorks water fix)

Load 1 (10:31) delivered its goals (injections active, EnvHazards DLL clean,
dump fresh, 635 held) but ran with EVERY water TerrainDef discarded: the
deployed `RM_LiquidProperties_CompatIndex.xml` still carried lowercase
`viscosityClass water` although repo fix `cd8ab494e` landed 03:59 — the deploy
gap, now closed (FlowWorks redeployed 14 files, verified). Load 2 decision
strings, written before launch:

| item | expected PRESENT | failure string | baseline (load 1) |
|---|---|---|---|
| water terrains live | `Exception loading def from file Terrain_Water.xml` count **0** | any hit | 49 def-load exceptions |
| crossref cascade gone | crossref count back to ≤ baseline 0–25 band | hundreds again | 434 |
| load itself | `Bridge token:` | `Recovered from incompatible` | clean |
| list held | 635 active after launch | 634/6 | 635 |

Still expected RED on load 2 (filed for FOUNDRY, not this load's problem):
RSW patchfail lines (9 RimStarWars Patches + 1 Pawn Flavor), RSW_*Juv config
errors (42), TYR meat/corpse Scribe refs (10).

---

# (superseded same day) load 1 notes — kept for the harvest comparison

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
