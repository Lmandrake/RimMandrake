# Expected-failure signatures — written BEFORE launch, per rimworld-load-round §3

Load 1 (591 mods): enabled `mandrake.rm.property` + `mandrake.rm.theft_hauler`.
**Result, confirmed via harvest_log.py + literal log scan**: 0 DEAD MODS (static
ctor/type load), zero lines mentioning `RimMandrake.Property`/
`RimMandrake.TheftHauler`/`RimMandrakeProperty`/`RimMandrakeTheftHauler` anywhere
in the fresh log — both assemblies loaded clean. (Unrelated pre-existing findings
on this load: 1 stale-Scribe `Corpse_Titan` hit, baseline-mismatch not a
regression; 123 NEW `Jawa Pawn Flavor` patch-operation failures — real
regression, PAWN_FLAVOR_PHASE2_APPLY_1's patches, out of scope here, filed
separately.)

Load 2 (592 mods): additionally enabling `mandrake.rm.salvageclaim` — discovered
mid-task to be the actual carrier of `SETTLEMENT_VERBS_WAVE_1`'s claim-fee
gizmo (`FloatMenuOptionProvider_PaySalvageClaim`), which the original 2-mod
scope did not anticipate. Pure C#, no Defs/Patches, `loadAfter` both
`Ludeon.RimWorld` and `mandrake.rm.property` (satisfied — inserted directly
between them). If broken, expect a line naming `RimMandrake.SalvageClaim`
specifically, e.g. `Could not load type
'RimMandrake.SalvageClaim.FloatMenuOptionProvider_PaySalvageClaim'`.

## RimMandrakeProperty.dll (`mandrake.rm.property`)
Pure `GameComponent` mod, no Harmony, no Defs/Patches — picked up only via
`Game.FillComponents`'s reflection scan. If broken, expect a line naming
the `RimMandrake.Property` namespace specifically, e.g.:
`Could not load type 'RimMandrake.Property.GameComponent_PropertyLedger'
from assembly 'RimMandrakeProperty'` or a `TypeLoadException`/
`ReflectionTypeLoadException` citing `RimMandrakeProperty` in its message
or stack. No XML `Config error in mandrake.rm.property` is expected (no
Defs shipped) — if one appears, that itself is the anomaly.

## Load 3 (593 mods) — 2026-09-02

Two changes riding together: (a) `mandrake.rut.pawnflavor`'s
`PawnFlavorPhase2_ThoughtDef.xml` regenerated with the `stage_op()` fix
(XML-only, mod already active, config-class change — free per §3's table) and
(b) newly enabling `mandrake.rsw.livestock` (one new assembly,
`RimMandrakeLivestockRSW.dll`, `CompLightAversion` on Skarnix). XML-only +
one new assembly batches fine (well under the three-assembly waiver), signature
written first per §3.

## RimMandrakeLivestockRSW.dll (`mandrake.rsw.livestock`)
`CompLightAversion` lives in namespace `RimMandrake.StarWars.Livestock`
(`src/RimStarWars/Livestock/Source/CompLightAversion.cs`), plus Cindermare's
cold-drain via pure XML (`RSW_ColdDrainDamage`/`RSW_ColdDrain`, no C#). If
broken, expect a line naming `RimMandrake.StarWars.Livestock` or
`RimMandrakeLivestockRSW` specifically — a `TypeLoadException`/
`ReflectionTypeLoadException` citing that assembly, or (since `CompLightAversion`
is referenced from `RSW_Skarnix`'s `<comps>` list) a `Config error in
mandrake.rsw.livestock` naming `RSW_Skarnix` if the comp class doesn't resolve.
Cindermare is pure XML — any error naming `RSW_Cindermare` would be a
different, def-level problem, not an assembly load failure.

## RimMandrakeTheftHauler.dll (`mandrake.rm.theft_hauler`)
Ships a JobDef/JobDriver/marker class plus one `MayRequire="mandrake.rsw.droidworks"`-
gated patch. **`mandrake.rsw.droidworks` is NOT active on this list** — the
patch is a documented no-op in that case (silent, by design), so expect
ZERO lines mentioning `RSW_DW_Race_OuterRim_MuckrakerDroid` or
`TheftHaulerExtension` this load. A genuine break shows as a line naming
`RimMandrake.TheftHauler` specifically, e.g. `Could not load type
'RimMandrake.TheftHauler.JobDriver_TheftHaul'` or a JobDef registration
failure for `JobDefs_TheftHauler.xml`'s own defName(s). Because Droidworks
is absent, this pass can only prove the engine loads clean — it CANNOT
prove the theft job actually fires on a real droid (needs Droidworks
active, out of scope for this load per the owner's strict two-mod scope).

## Load 4 (594 mods) — 2026-09-02, WeatherSuite pair

Enabling `mandrake.rsw.weathersuite` (engine, new assembly `WeatherSuiteHook.dll`)
+ `mandrake.rut.weathersuite` (Ash'karr content, XML-only, `loadAfter`
`mandrake.rsw.weathersuite`, satisfied — inserted directly after it) together.
`mandrake.rsw.livestock` (`RSW_Cindermare`/`RSW_Skarnix`) was DISABLED by the
prior pass (593→592, live `Pawn_AgeTracker.get_CurKindLifeStage` crash on both
defs, unresolved) — confirming it's still absent before launch is part of
this load's own baseline check, not assumed.

## WeatherSuiteHook.dll (`mandrake.rsw.weathersuite`)
Confirmed from source (`src/RimStarWars/WeatherSuite/Source/WeatherSuiteHook.cs`):
namespace `RimMandrake.StarWars.WeatherSuite`, types `PlanetGeometryDef`,
`MapComponent_TerminatorBand`, `IncidentWorker_NightsideAurora`,
`CompForecaster`/`CompProperties_Forecaster` (the `RSW_WS_WeatherInstrument`
inspect-string reader). If broken, expect a line naming
`RimMandrake.StarWars.WeatherSuite` or `WeatherSuiteHook` specifically — a
`TypeLoadException`/`ReflectionTypeLoadException` citing that assembly, or
a `Config error in mandrake.rsw.weathersuite` naming `RSW_WS_WeatherInstrument`
if the comp class doesn't resolve. `mandrake.rut.weathersuite` is pure XML
(one `PlanetGeometryDef`, 5 `PatchOperationConditional`-wrapped folk-sign
`WeatherDef` description replaces) — any error naming `RSW_WS_TerminatorFront`/
`RSW_WS_DarkAurora`/the folk-sign patch would be a def-level problem in that
mod, not an assembly load failure in the engine mod.

---

## Load 3 (593 mods) — 2026-09-02, BENCH. THREE assemblies, owner's batch waiver.

Deployed in this shutdown window, all three previously `Build succeeded` and none
proven live. Written BEFORE launch, per §3: the waiver is affordable only because
these three fail in *different* places, and that is worthless unless the
distinctions exist on paper before the log does.

Fingerprint of the load set at deploy time: `0d594d931ddff722`, 593 active mods,
RimWorld 1.6.4871 rev591. New since the live dump: `mandrake.rm.loadtracer`.

| # | assembly | deployed to | its own signature |
|---|---|---|---|
| 1 | `JawaBench.BridgeTools.dll` (companion, `--gm`) | `<RimWorld>\BridgeTools\JawaBench\` | the `[JawaBench] ready:` line |
| 2 | `RimMandrakeStructureInjections.dll` | `Mods\StructureInjections\Assemblies\` | type names under `RimMandrake…StructureInjections` |
| 3 | `RimDefDump.dll` | `Mods\RimDefDump\1.6\Assemblies\` | the `[RimDefDump]` prefix |

**1 — JawaBench companion.** The build stamp is the real check, not a tool count.
- ✅ PASS: a `[JawaBench] ready:` line exists AND its build stamp reads
  **`acec5065`** (build.py named it: game copy was `e911f9e6be95`, this build
  `acec5065627f`).
- ❌ FAIL, old DLL still loaded: the stamp reads `e911f9e6` — the deploy did not
  take, and every `jawa/*` result this session describes the previous build.
- ❌ FAIL, did not load at all: no `[JawaBench] ready:` line, and `jawa/*` tools
  absent from the bridge's tool list. ⚠️ The bridge itself will still answer
  (`brrainz.rimbridgeserver` is a separate mod) — a live bridge is NOT proof the
  companion loaded.

**2 — StructureInjections.** Distinguishable because nothing else in this batch
carries the `StructureInjections` namespace.
- ❌ FAIL: any `TypeLoadException` / `Could not load type` / `Could not resolve
  type` naming `GenStep_RimplacePlan`, `RimplacePlan`, or
  `StructureInjectionsDebugActions`.
- ✅ PASS (positive, not silence): the rimplace debug action places its build AT
  the clicked cell — run a plan at (60,60) and expect it at (60,60), not
  (160,160). That doubled coordinate IS the bug this deploy fixes, so the
  observation is the proof.

**3 — RimDefDump.** The one that changes what a session can do at all.
- ❌ FAIL: no `[RimDefDump]` line at startup with the dump armed, or any type-load
  error naming `RimDefDump` / `DefDumper`.
- ✅ PASS (positive): `[RimDefDump]` writes a dump at the main menu (~27 s, ~1.2 GB)
  AND the new on-demand debug action `Actions\RMDefDump\Dump defs now (all)`
  exists — the second half is the actual deliverable, since a startup dump proves
  only the old code path.

⚠️ **Silence acquits none of them.** Each has an expected-PRESENT string above
precisely because a no-op logs nothing, and "zero hits" is not "it worked".
