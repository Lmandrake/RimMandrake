# Expected-failure signatures — written BEFORE launch, per rimworld-load-round §3

Load: enabling `mandrake.rm.property` + `mandrake.rm.theft_hauler` (2 new C#
assemblies) on the owner's real 591-mod full list. Two assemblies, well
under the three-assembly waiver; batched together since neither depends on
the other and each has its own distinguishing failure signature below.

## RimMandrakeProperty.dll (`mandrake.rm.property`)
Pure `GameComponent` mod, no Harmony, no Defs/Patches — picked up only via
`Game.FillComponents`'s reflection scan. If broken, expect a line naming
the `RimMandrake.Property` namespace specifically, e.g.:
`Could not load type 'RimMandrake.Property.GameComponent_PropertyLedger'
from assembly 'RimMandrakeProperty'` or a `TypeLoadException`/
`ReflectionTypeLoadException` citing `RimMandrakeProperty` in its message
or stack. No XML `Config error in mandrake.rm.property` is expected (no
Defs shipped) — if one appears, that itself is the anomaly.

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
