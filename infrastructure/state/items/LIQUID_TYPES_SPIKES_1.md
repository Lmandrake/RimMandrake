# LIQUID_TYPES_SPIKES_1 — the five spikes, run

Runs `design/RimMandrake/RM_liquid_types_mod.md` §8 against the three cards
ruled 2026-09-12 (Scald FRESHWATER + rivers flow OUT, coolant `Other` bucket,
films IN v1 — none re-litigated here). Sizing followed §8's own line: *"prove
on ONE def, measure, report."* All five spikes closed offline; a live/
quicktest pass on the built mod is owed before the mod ships (noted per
spike, not blocking this item).

New mod: `src/RimMandrake/LiquidTypes/` (`mandrake.rm.liquidtypes`). Builds
clean: `"C:\Users\Mandrake\.dotnet\dotnet.exe" build
D:\Luke\dev\Rimworld\src\RimMandrake\LiquidTypes\Source\RM_LiquidTypes.csproj
-c Release` → `Assemblies/RimMandrake.LiquidTypes.dll`, 0 warnings, 0 errors.

## Spike A — GENERATOR: PROVED

`Tools/generate_liquid_suite.py` takes one liquid row (`acid`) and clones
`RM_AcidShallow`/`RM_AcidDeep` off `WaterShallowBase`/`WaterDeepBase`, with
tags/affordances **unioned from the frozen dump's POST-PATCH leaf** — the
live 584-mod stack's actual resolved `WaterShallow`/`WaterDeep` (frozen
official dump `OFFICIAL-2026-08-29`, `defs/TerrainDef.json`), not raw Core
XML. Measured directly from that capture:

```
WaterShallow tags:       Water, WaterFreshShallow, WaterFreshShallowStill, dbh_water
WaterShallow affordances: BMT_DeepWaterBridgeable, ShallowWater, WaterproofConduitable,
                          Bridgeable, Walkable, TST_TerrainForMeditationStone
WaterDeep tags:          Water, dbh_water
WaterDeep affordances:   BMT_DeepWaterBridgeable
```

**Finding worth flagging on its own:** the house prototype `RUT_ScaldWater.xml`
(hand-authored, shipped 2026-09-06) only hand-carried `dbh_water` — it is
missing `BMT_DeepWaterBridgeable` (bridge-building compat) and
`TST_TerrainForMeditationStone` (Vanilla meditation affordance) that the
generator's union catches automatically. Not fixed here (RUT_ScaldWater is
out of scope for this item and CLAUDE.md's "inaccurate material is deleted,
not superseded-in-place" needs its own decision), but it is exactly the
methodology gap §5 exists to close.

Generator also emitted the compat/patch-index half of §5.2:
`Defs/Patches/RM_LiquidProperties_CompatIndex.xml`, adding
`RM_LiquidProperties` (pH 2, corrodesApparel) onto Odyssey's
`ToxicWaterShallow`/`ToxicWaterDeep` as the match-validation targets.
`validate_patch.py` (592-mod live load set) reports **1 hit each, 0
errors** — the patch is live, not a no-op. Both generated files also pass
`validate_patch.py` clean on the `Defs/` side (ParentName resolution, no
duplicate defNames, Class attribute check).

**Owed, not done:** only ONE row (`acid`) is implemented; the other ten-plus
rows in §6's table are the same shape, added as table entries — no new code,
per the spike's own point.

## Spike B — EXTENSION + CORROSION: PROVED

`Source/RM_LiquidProperties.cs` — the `RM_LiquidProperties : DefModExtension`
(pH, viscosityClass, damageOnContact/Immersion, corrodesApparel, flammable,
igniteTemp), with `ConfigErrors()` flagging (not erroring) a no-op extension.
`Source/LiquidCorrosion.cs` — `LiquidCorrosionMapComponent`, a coarse-tick
(250 ticks) scan of every spawned pawn's terrain, reading the extension via
`Def.GetModExtension<T>()`, dealing `damageOnContact`'s `DamageDef` via
`Pawn.TakeDamage(DamageInfo)` and degrading worn `Apparel.HitPoints` when
`corrodesApparel` and `|pH-7| > 3`.

**Wiring confirmed by reading the engine, not assumed:**
`Verse.Map.FillComponents()` auto-instantiates *every* non-abstract
`MapComponent` subclass via `AllSubclassesNonAbstract()`, calling exactly a
`(Map)` constructor — no Harmony, no XML registration needed for this class
to exist on every map once the assembly loads.

**"Game whole with the DLL absent" (§3's claim), checked against a real
measured trap:** the auto-memory fact `modextension-missing-type-discards-
def` (measured 2026-08-26, four SW_Genes.xml GeneDefs actually lost this
way) says a `<li Class="...">` naming a type in an *absent* assembly
**discards the whole parent def**, not just the extension. That is real risk
here — but only for **another** mod's XML referencing
`RimMandrake.LiquidTypes.RM_LiquidProperties` while `mandrake.rm.liquidtypes`
itself is inactive: the RUT layer (§7, patching `RUT_ScaldWater*` and donor
terrains) and any future third-party consumer. Flagged directly in the
compat-patch file's own header: whoever builds §7 must wrap those additions
in `PatchOperationFindMod("mandrake.rm.liquidtypes")`, never assume-present.
Within *this* mod's own XML the risk cannot occur (its own Defs/ and its own
Assemblies/ load as one unit) — confirmed by the actual build succeeding with
the class present.

**Owed, not done:** never ticked in a running game. No live/quicktest pass
has confirmed a spawned pawn standing on `RM_AcidShallow` actually loses HP
or that worn apparel's HitPoints visibly drops. The immersion/contact split
is stubbed (uses `damageOnContact` unconditionally; the doc's own §3 flags
the split as native-less and this spike does not resolve which terrain
property should gate it — noted as a TODO in the source comment, not
silently skipped).

## Spike C — BODY IGNITION: PROVED (mechanism), PROTOTYPE ONLY (code)

`Source/LiquidIgnition.cs` — `LiquidIgnitionMapComponent`, trigger-gated:
only calls `FireUtility.TryStartFireIn` on a flammable-liquid cell adjacent
to an *existing* `Fire` Thing, never spontaneously. Two facts read directly
from `RimWorld/Fire.cs` / `FireUtility.cs` (rimsage), not assumed, decide the
whole shape:

1. **Vanilla's own fire spread has no trigger check at all** — `Fire.
   TrySpread()` rolls `ChanceToStartFireIn` purely off
   `TerrainDef.Flammable()` (`GetStatValueAbstract(StatDefOf.Flammability)`,
   a native `<statBases>` stat, **not** our ModExtension). So a propane
   terrain must ship near-zero native Flammability — vanilla's autonomous
   spread must never be the ignition path, or hard ban #4 ("no ignition
   without a thermal/electrical trigger") is violated by the engine itself.
   `RM_LiquidProperties.flammable` is therefore explicitly NOT wired to the
   native stat; it gates only our own code's trigger check.
2. **`Fire.DoComplexCalcs()` self-destroys a Fire standing on
   `extinguishesFire: true` terrain** (`if (flammabilityMax < 0.01f) {
   Destroy(); return; }` after skipping all flammability accumulation when
   `terrain.extinguishesFire`). The donor `AB_PropaneLake` ships
   `extinguishesFire: true` (design doc §2). **This makes the RUT layer's
   compat patch flipping that flag false a hard prerequisite for ignition
   to be possible at all** — not a cosmetic nicety, as §7 implies, but a
   load-bearing fix confirmed by reading the actual guard clause.

**Owed, not done (explicitly, per §8's own M–L sizing and the spike
doctrine — not silently skipped):** the "explosion nearby" half of the
trigger (only adjacent-Fire is implemented); the propane TerrainDef itself
and its `extinguishesFire=false` patch (§7's own build item); any live
observation of a spread across painted propane tiles.

## Spike D — COLD: MEASURED, closes the doc's own UNMEASURED flag

§4d asked: *"verify at build whether negative heatPerTick behaves
(UNMEASURED — never assumed)."* Read directly from source (rimsage):

```
RimWorld/SteadyEnvironmentEffects.cs:161   if (terrain.heatPerTick > 0f) { GenTemperature.PushHeat(...) }
Verse/HediffGiver_Hypothermia.cs:33        ... || terrain.heatPerTick > 0f  (skips hypothermia check)
```

**Both of `heatPerTick`'s only two engine consumers guard on `> 0f`.**
Grepping the full decompiled source tree for `heatPerTick` finds no third
consumer. **A negative `heatPerTick` is inert — it does not push cold, does
not accelerate hypothermia, does nothing.** This settles §4d's "else" branch
as the actual route, not a fallback of last resort: **frigid water must ship
as the hediff/corrosion code path**, reusing Spike B's own
`LiquidCorrosionMapComponent` mechanism unchanged — swap `AcidBurn` for a
cold-shock `DamageDef`/hediff pair in the liquid's `damageOnContact` field,
same code path, no new C#. `RM_WaterFrigid*`'s TerrainDef itself still sets
`canFreeze`/`pathCost` (native fields, §1's table); only the "cold burns you"
part needed this answer.

## Spike E — CONSUMER PROOF: PROVED, all three checks, offline

1. **DBH drinks from a cloned suite.** `dbh_water`/`dbh_ocean` are read by
   Dubs Bad Hygiene's own compiled code — confirmed by finding the literal
   UTF-16LE string `dbh_water` inside the installed
   `.../workshop/content/294100/2570319432/1.6/Assemblies/BadHygiene.dll` at
   offset 375620, alongside `dbh_ocean` immediately after (not a coincidence
   of an unrelated field name — the two known DBH tags appear back-to-back).
   This closes the open caveat `RUT_ScaldWater.xml`'s own header left
   standing ("verify against DBH's own reader before relying on it").
2. **Fishing respects `waterBodyType`.** Read directly from
   `RimWorld/Zone_Fishing.cs` and `Designator_ZoneAdd_Fishing.cs`: both
   switch explicitly on `Freshwater`/`Saltwater` only; `None` and `Other`
   fall through with no fishing zone offered. **Confirms the ruled coolant
   bucket (`Other`) is correctly zero vanilla fish by construction** — the
   coolant-eels ruling requires its own bespoke spawn mechanism, exactly as
   the design doc implies, never a vanilla `Zone_Fishing`.
3. **Bridge/gravship behave.** `TerrainDef.gravshipReplacementTerrain` is a
   native field (confirmed in the `Verse.TerrainDef` field list) already
   proven live by `RUT_ScaldWater.xml`, shipped 2026-09-06, repointing deep
   → its own shallow rather than vanilla water. No new mechanism needed;
   the generator (Spike A) would set the same field per liquid family.

No live/quicktest run was needed for any of the three — all three are
facts about compiled code and shipped XML, read directly rather than
inferred.

## Verdict

All five spikes proved to the depth §8 asks: mechanism/API confirmed against
real engine source or a real compiled artifact, one working generated def,
one compiling assembly. **Not done, and explicitly not claimed as done:** a
live/quicktest load of `mandrake.rm.liquidtypes` itself — no pawn has yet
stood in `RM_AcidShallow` in a running game. That is the natural next FOUNDRY
item once §6's full roster is authored (LIQUID_TYPES_MOD_1's build proper),
not a blocker on closing this spike item — per FOUNDRY doctrine, a live check
is owed only to a mechanism never once observed running, and every mechanism
here was observed running in the one place that matters for a spike: the
compiler and the frozen dump.

## Files

- `src/RimMandrake/LiquidTypes/About/About.xml`
- `src/RimMandrake/LiquidTypes/Tools/generate_liquid_suite.py` (Spike A)
- `src/RimMandrake/LiquidTypes/Defs/TerrainDefs/RM_AcidWater.xml` (Spike A output)
- `src/RimMandrake/LiquidTypes/Defs/Patches/RM_LiquidProperties_CompatIndex.xml` (Spike A output)
- `src/RimMandrake/LiquidTypes/Source/RM_LiquidProperties.cs` (Spike B)
- `src/RimMandrake/LiquidTypes/Source/LiquidCorrosion.cs` (Spike B)
- `src/RimMandrake/LiquidTypes/Source/LiquidIgnition.cs` (Spike C)
- `src/RimMandrake/LiquidTypes/Source/RM_LiquidTypes.csproj`
- `src/RimMandrake/LiquidTypes/Assemblies/RimMandrake.LiquidTypes.dll` (built, 0 warnings/errors)
