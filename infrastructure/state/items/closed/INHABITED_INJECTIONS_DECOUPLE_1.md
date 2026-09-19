# INHABITED_INJECTIONS_DECOUPLE_1

## Spec
Decouple `Inhabited` (`mandrake.rm.inhabited`) from `StructureInjections`
(`mandrake.rm.injections`) per the soft-hook law in
`design/CHRONICLE_EVENT_SPINE.md` ("Law 1" — no `<modDependencies>` naming
another `mandrake.*` mod, no hard `<Reference>` between csproj files, every
cross-mod C# call behind `AccessTools.TypeByName`/reflection with a null
guard). Found during CHRONICLE_NINEFOLD_DECOUPLE_1's Law-1 sweep
(point 4 of that item's "Still owed before close").

Confirmed, all three clauses of the law violated — same shape as the
Aftermath→Ninefold coupling CHRONICLE_NINEFOLD_DECOUPLE_1 just fixed,
slightly worse (three coupling points, not one):

1. **`<modDependencies>` (About.xml):**
   `src/RimMandrake/Inhabited/About/About.xml` lines 38-41 list
   `mandrake.rm.injections` as a hard mod dependency (also in
   `<loadAfter>`, line 46).
2. **Hard csproj `<Reference>`:**
   `src/RimMandrake/Inhabited/Source/Inhabited.csproj` lines 81-84:
   ```
   <Reference Include="RimMandrakeStructureInjections">
     <HintPath>..\..\StructureInjections\Assemblies\RimMandrakeStructureInjections.dll</HintPath>
     <Private>false</Private>
   </Reference>
   ```
3. **Direct compile-time C# type reference:**
   `src/RimMandrake/Inhabited/Source/GenStep_ComposeSettlementDistrict.cs`
   line 4: `using RimMandrake.StructureInjections;`, and lines 207-232 call
   `RimplacePlan.Parse(path)` and
   `GenStep_RimplacePlan.ApplyPlan(map, plan, dx, dz, fileName)` directly.
   (`GenStep_InhabitedStock.cs` line 26 only references the class in a
   comment — no live coupling there.)

## Shape difference from the Aftermath/Ninefold fix — read before assuming the exact same pattern applies

Aftermath→Ninefold was a **fire-and-forget notification**: Aftermath raises
an event, Ninefold subscribes and reacts; no return value crosses the
boundary, so a static `event Action<T>` + `AccessTools.TypeByName(...).GetEvent(...)`
subscribe pattern was a clean fit.

Inhabited's coupling is a **functional call with a return value**: it reads
a `.txt` template describing a structure plan, needs `RimplacePlan.Parse`
to turn that text into a `RimplacePlan` object, then needs
`GenStep_RimplacePlan.ApplyPlan` to stamp it onto the map. This is a
library call, not a notification — there is no natural "event" here.
Whoever fixes this needs one of:

- Reflection-based calls (`AccessTools.TypeByName` + `MethodInfo.Invoke`)
  wrapped in a null-guard, accepting the `object`/boxing cost and losing
  static typing on `RimplacePlan`; or
- Duplicating/inlining the tiny amount of plan-parse-and-apply logic
  Inhabited actually needs into Inhabited itself, breaking the runtime
  dependency entirely (bigger change, but a real decouple rather than a
  reflection shim around a still-mandatory library); or
- Accepting this one as a deliberate, declared library dependency (like a
  shared framework a game DLC depends on) and NOT reflection-hiding it —
  i.e. ruling that Law 1 does not apply to genuine utility libraries, only
  to sibling "engines" that should each stand alone. That is an owner call,
  not this item's to make — record the options, do not pick one silently.

Either way: this item is filed as the measurement/scoping output. The fix
itself (pick + implement one of the above) is separate work, offline,
C# authoring.

## Verify
`grep -c "RimMandrakeStructureInjections\|mandrake.rm.injections" ` returns
zero across `Inhabited.csproj` and `About.xml`, and no `using
RimMandrake.StructureInjections;` remains in Inhabited's Source/ (or the
owner has explicitly ruled this coupling acceptable and this item is
dropped/superseded on that ruling instead).

## Criteria
Either Inhabited cold-loads standalone (Inhabited + Harmony only) with the
District-template feature gated off cleanly when Injections is absent, or
an owner ruling records that this dependency is intentional and Law 1 does
not apply to it.
