## spec
`StructureInjections`, `StructureInjectionsRUT` and `StructureInjectionsSW`
all ship plan templates (`Templates/*.txt`) that place a `PrimitiveWell`
THING, a real ThingDef defined only by `Dubs Bad Hygiene Lite`
(`dubwise.dubsbadhygiene.lite`). None of the three mods' `About.xml`
declares it in `<modDependencies>` (confirmed 2026-09-26 while working
`PRIMITIVEWELL_DEAD_DEFNAME_1`, dropped as a misdiagnosis -- see its closed
prose). It is currently active in the owner's live mod list so nothing is
broken today, but the dependency is silent: nothing warns if it is ever
deactivated, and it is why `StructureInjections`' own minimal modcheck tier
(which never loads DBH Lite) measures one fewer `thingsSpawned` than the
plan's raw THING count on `moisture_farm_test.txt` (already folded into that
suite's floor via `MOISTURE_HYGIENE_ITEMS`).

## verify
Judgment call, not mechanical: decide whether this should be a soft
`<modDependencies>` entry (informational, does not block load), a
`MayRequire`-style guard added to the plan compiler so a missing-mod THING
degrades with a clearer signal than a bare `Log.Error`, or left as-is now
that it is understood and documented. Whichever is chosen, apply it to all
three mods (`StructureInjections`, `StructureInjectionsRUT`,
`StructureInjectionsSW` About.xml / template tooling) consistently.

## criteria
The dependency on Dubs Bad Hygiene Lite for `PrimitiveWell` is either
declared somewhere a human or tool can see it before it silently fails, or
there is a recorded decision that today's undeclared state is fine and why.
