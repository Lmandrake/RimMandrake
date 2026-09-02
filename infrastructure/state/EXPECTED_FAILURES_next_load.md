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
