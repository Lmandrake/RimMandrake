# Expected failures + decision strings — rot-wave tier load, 2026-09-18 (BENCH)

Two loads planned this cycle. Written BEFORE launch, per load-round §2/§3.

## Load A — tier list (minimal 13 + 4 rot mods), quicktest battery

Assemblies riding (2 new this load; signatures distinguishable by namespace):

| assembly | expected-failure signature (Player.log) |
|---|---|
| RimMandrake.EnvironmentalHazards.dll | `Could not find class RimMandrake.EnvironmentalHazards.` or `TypeLoadException` naming `RimMandrake.EnvironmentalHazards` |
| RimMandrake.CreatureBehaviors.dll | `Could not find class RimMandrake.CreatureBehaviors.` or Harmony patch error naming `CreatureBehaviors` (TradeDeal.TryExecute seam) |

Expected-PRESENT strings / probes (absence = failure, not success):

- Player.log: `Adding mandrake.rm.environmentalhazards` and `Adding mandrake.rut.rotsporekit`
- `jawa/get_defs RUT_SheenExposureLock` returns a def (MayRequire now satisfied — ENVHAZARDS_NEVER_ACTIVATED_1 probe)
- `jawa/get_defs RUT_SporeCloud` shows conditionClass `RimMandrake.EnvironmentalHazards.GameCondition_EnvironmentalWeather`
- `jawa/get_defs RUT_PaleTree` shows a TWO-entry requiredSubplantCountPerPsylinkLevel (card 4)
- Guardian defs resolve: RUT_AgelessCap / RUT_RegenerantVeil / RUT_EuphoricCrown / RUT_FalseFruit — and the previously-known `RM_BaseGasDamaging` parent error is GONE (EH active)
- Live-prep defs resolve: RUT_BrewingVessel, teas, symbiont pairs
- `^Config error in` sweep: baseline is the standing minimal-list count; any line naming a RUT_/RM_ rot def is a finding

LIES: a def absent from get_defs on the TIER list can be a missing dependency
that the FULL list carries — cross-check the def's MayRequire before filing.
A no-op patch logs nothing; zero hits proves nothing without the present-strings above.

## Load B — FULL list restore (after battery)

Third assembly, solo-attributable here because it only acts on Pyrelands defs:

| assembly | expected-failure signature |
|---|---|
| FireEcologyHook.dll (density enforcer) | enforcer line ABSENT from Player.log, or exception naming `FireEcologyHook` |

Expected-present:
- FireEcologyHook enforcer log line (it logs when it catches the rewriter)
- `jawa/get_defs` Pyrelands plantDensity reads 3.0 live (not 1.0)
- gizkastowaway + environmentalhazards both in the `Adding` roster
- Fresh-map Pyrelands vegetation screenshot for the owner

LIES: density 3.0 read from XML on disk is not the live value — only the
get_defs read-back counts (the rewriter is a startup def-mutator).
