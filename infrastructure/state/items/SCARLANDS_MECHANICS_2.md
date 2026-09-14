# SCARLANDS_MECHANICS_2 — the Scarlands C# kit build

Successor to `SCARLANDS_MECHANICS_1` (filed 2026-09-07, closed 2026-09-11 at
`0167e7af` — spec-drafting only, no build). That ID is permanently closed
(append-only ledger — `rimflow why SCARLANDS_MECHANICS_1` confirms it will
never be offered again), so this item carries the kit's build/spike work
under a new ID rather than reopening it. `caused_by: SCARLANDS_MECHANICS_1`
on the filing event, and a note left on that item pointing here — same
precedent `GREENTIDE_MECHANICS_2` set for the identical situation.

## spec

Per `design/Jawa/worldbuilding/biomes/the_scarlands.md` (FROZEN, §4 mynock,
§7b curse currencies, §5/§6 Sentinel rules, §8 pre-sprung dangers): the
mynock ship-infestation, the Scarlands mark (a permanent mood/nightmare
hediff), plated-grazer scaria onset (wild scaria animals that always
eventually rage), the Forgotten Sentinels' defend-only AI (hard ban: never
raid, never pursue past their lines), and pre-sprung danger dressing (every
ancient hazard found already opened/destroyed).

**The engine mapping is drafted**:
`design/Jawa/worldbuilding/biomes/kits/scarlands_kit_spec.md` (2026-09-11) —
5 mechanics, reuses 2 ruled comps from `ALPHA_MECHANICS_KIT_1`
(`mandrake.rm.environmentalhazards`), owner rulings from the 2026-09-11 card
sitting (mod placement, mynock pressure curve, mynock race, mark
permanence, grazer taming, Sentinel bounds/radii, dressing density).

**🔴 Load-bearing finding this pass, same shape as Greentide's own spike**:
§1 (the whole mynock ship-infestation mechanic — board/breed/eat/hunt-out)
is not "unbuilt" at all. It shipped in full under `SHIP_VERMIN_MOD_1`
(closed 2026-09-11, sha unrecorded in that item's own text — see its file)
and `WRECKAGE_VERMIN_SPAWN_1` (closed 2026-09-12), owner-ruled off this
kit's own naming (`mandrake.rm.hullvermin`/RM_ classes named in this spec)
and into a dedicated shared home instead:

- **Board** — `RM_SeekTargetExtension` + `RM_JobGiver_SeekMarkedTerrain`
  (`src/RimMandrake/CreatureBehaviors/Source/`, `mandrake.rm.creaturebehaviors`),
  attached to `RSW_Mynock` with `seekSubstructure=true` in
  `src/RimMandrake/ShipVermin/Patches/RSW_Mynock_ShipVermin.xml`. Vanilla
  `ThingDef.bringAlongOnGravship` (default true) does the actual gravship
  carry — zero C# for that half, exactly as this spec's own §1 predicted.
- **Breed** — `RM_CompVerminBreeder`/`RM_CompProperties_VerminBreeder`
  (same assembly), lord-free, population-capped via
  `RM_MapComponent_VerminPopulation`'s pressure curve (the "nuisance unless
  there are many" owner ruling, implemented as an actual 0..1 scaling curve
  read by both the breeder and the gnaw job).
- **Eat** — `RM_GnawTargetExtension` + `RM_JobGiver_GnawTargets` +
  `RM_JobDriver_Gnaw` (JobDef `RM_Gnaw`), data-driven target set (building
  defNames, comp types — e.g. `CompGlower` for every lamp without a
  denylist — and floor terrain defNames), bite damage scaling with
  population pressure, `TerrainGrid.RemoveTopLayer` for the floor-strip
  ("eats the flooring, not the hull").
- **Hunt-out** — `RM_Alert_ShipVermin` (`mandrake.rm.shipvermin`) +
  `RM_Alert_VerminPopulationBase`; mynocks are ordinary wild pawns once
  spawned, so vanilla hunting/drafted shooting already ends the infestation.
- **Wreck-anchored spawning** (owner ruling 2026-09-12, not in the original
  spec): `RM_CompProperties_VerminNest`/`RM_CompVerminNest`
  (`mandrake.rm.shipvermin`), wired onto `ShipChunk_Mech` for the Fall
  Line's ground hulks — live-verified with an actual observed spawn
  (`WRECKAGE_VERMIN_SPAWN_1`'s own closing pass).
- **RSW_Mynock** itself (`src/RimStarWars/SWBestiary/Defs/ShipVermin/`) is
  our own clone per the owner's ruling (never a donor patch) and already
  ships vacuum-capable (`canBeVacuumBurnt=false`, `canFlyInVacuum=true`,
  `VacuumResistance 1`) — resolving this spec's own §1 vacuum ❓ as a
  non-issue: RaceProps already handles it, no special-casing needed.

**Also already shipped, resolving §2 without new fields**:
`EnvironmentalWeatherExtension` (RC4, `ALPHA_MECHANICS_KIT_1`'s own class)
already carries `hediffToApply`/`hediffSeverityPerInterval` AND
`carrierHediff`/`carrierHediffSeverity` — added by `MIASMA_MECHANICS_1`'s M4
build, after this kit spec's §2 was drafted. The spec's proposed "extend RC4
with two fields" is already done; §2 needs no RC4 changes at all.

`scarlands_kit_spec.md` is corrected this pass at §1 and §2 (see "files"
below) so the next reader doesn't redo shipped work, matching Greentide's
own precedent for a stale spec caught against real shipped code.

**What is genuinely still unbuilt, confirmed by grep (zero hits in `src/`)
before this pass**: §2's `RM_HediffComp_SeverityFloor` (the "never fully
fades" clamp; everything else in §2 is XML/reuse), §3's scaria-onset content
(`RUT_ScariaIncubation` HediffDef) and RC5 extension fields
(`pawnKindFilter`/`requiredHediff`) to gate the arming sweep, §4's Sentinel
lord (`RM_LordJob_DefendPerimeter` + duty wiring) and content
(`RUT_Sentinel*` kinds, `RUT_SentinelDefend` DutyDef), §5's pre-sprung
dressing prefab content.

## verify

- [x] Every ❓ engine claim the kit spec still carried (after the §1/§2
      reconciliation removed the ones already settled by shipped code) is
      re-checked against the real 1.6/Odyssey decompile —
      **2026-09-14, 4 resolved this pass, see "spike pass" below.**
- [ ] Build lands per the spec's build order, after `ALPHA_MECHANICS_KIT_1`
      (closed). **Not done this pass** — three small compiling proof
      classes shipped (RC5 extension fields, the severity floor, the
      Sentinel lord/toil); the content defs (Scarlands mark HediffDef,
      scaria incubation HediffDef, Sentinel kind/duty XML, pre-sprung
      prefabs) are later, separate FOUNDRY build-pass work, same posture as
      every sibling kit's own spike pass.
- [ ] A quicktest map in the biome shows the remaining mechanics live.
      **Not done this pass** — no bridge/game access in this task, same as
      every sibling spike.

## spike pass — 2026-09-14, run per GREENTIDE_MECHANICS_2's/SCALD_MECHANICS_1's own methodology

Sizing followed those items' own line: prove each risky/uncertain piece
minimally, offline, against real engine source, not the full 5-mechanic
build. Decompile used throughout:
`/mnt/d/Luke/dev/reference/rimworld-decompiled` (same path GREENTIDE_MECHANICS_2
and MIASMA_MECHANICS_1 confirmed as 1.6/Odyssey).

### Engine ground-truth: 4 named claims resolved against the real decompile

1. **§4's "does `LordToil_DefendPoint` accept a custom DutyDef" ❓ —
   RESOLVED NO, hardcoded.** `Verse.AI.Group/LordToil_DefendPoint.cs` read
   in full: `UpdateAllDuties()` constructs
   `new PawnDuty(DutyDefOf.Defend, lordToilData_DefendPoint.defendPoint)`
   directly — no virtual seam, no field, no override point. The spec's own
   fallback ("the subclassed toil is another ~10 lines") is confirmed the
   only route; built as `RM_LordToil_DefendPerimeter` below.
2. **§4's "does `LordJob_DefendPoint` have a `SpawnedPawnParams` ctor" —
   RESOLVED NO, confirmed as the spec suspected.**
   `Verse.AI.Group/LordJob_DefendPoint.cs`'s only real ctor is
   `(IntVec3 point, float? wanderRadius, float? defendRadius, bool
   isCaravanSendable, bool addFleeToil)`. `RimWorld/CompSpawnerPawn.cs`'s
   `CreateNewLord` calls `Activator.CreateInstance(lordJobType, new
   SpawnedPawnParams { aggressive, spawnerThing, defendRadius, defSpot })` —
   a single-arg ctor taking that exact type
   (`RimWorld/SpawnedPawnParams.cs`: `aggressive`, `spawnerThing`,
   `defendRadius`, `defSpot` — no `wanderRadius` field, confirming the spec's
   note that wander radius can't ride this ctor and must default
   separately). `RM_LordJob_DefendPerimeter` below adds that ctor.
3. **§5's "can `PrefabDef` entries set hit points / opened states
   declaratively" ❓ — RESOLVED YES.** `RimWorld/PrefabThingData.cs` (the
   per-entry payload `PrefabDef.things` is a list of) carries a plain
   `public int hp` field read straight off the XML (`XmlHelper.ParseElements`
   over every public field). Pre-damaged/opened dressing is expressible with
   zero new C# — per the spec's own conditional ("if yes, this class
   evaporates and the mechanic is zero C#"), **`RUT_GenStep_SprungDanger` is
   not needed.** §5 ships as pure `RUT_` PrefabDef content in a later pass;
   no proof class built here (there is nothing to prove).
4. **§2's "can a `TileMutatorDef`/GenStep attach a permanent
   `GameCondition` without C#" ❓ — RESOLVED YES, and a live shipped example
   already exists to copy.** `RUT_MiasmaWeatherLock.xml`
   (`src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/`, from
   `MIASMA_MECHANICS_1`'s M4 build) does exactly this: a `GameConditionDef`
   with `<canBePermanent>true</canBePermanent>` listed in the biome's own
   `<biomeMapConditions>` — that file's own header cites the mechanism
   (`BiomeConditionMapComponent.MapGenerated ->
   GameConditionMaker.MakeConditionPermanent`, decompile-confirmed by that
   pass) as needing no extra Def field. The Scarlands mark's permanent lock
   (`RUT_ScarlandsMarkLock`, later content pass) copies this file's shape
   verbatim onto `RUT_Scarlands.xml`'s own `biomeMapConditions` — no
   `MapComponent` of this kit's own is needed, deleting the spec's
   ❓-flagged fallback outright.

### Built this pass (compiling proof)

- **RC5 extension fields for §3** — `ArmLatentHazardExtension.cs` gains
  `pawnKindFilter` (`List<PawnKindDef>`) and `requiredHediff` (`HediffDef`),
  both optional and additive to the existing `targets`/`affects` gates;
  wired into `GameCondition_ArmLatentHazard.Eligible()`. Exactly the "one
  small extension: a pawnKindFilter/requiredHediff gate (two fields)" the
  spec's own §3 called for, so the scaria-onset arming sweep can target only
  grazers already carrying vanilla `Scaria` once the content HediffDef
  ships. (`src/RimMandrake/EnvironmentalHazards/Source/`)
- **`RM_HediffComp_SeverityFloor`** (§2) — new
  `HediffCompProperties_SeverityFloor` + `RM_HediffComp_SeverityFloor`
  (`HediffComp`, `CompPostTick` override). Clamps severity at a configured
  floor once it has ever crossed a trigger threshold — the "never fully
  fades" half of the mark that vanilla severity math (no floor concept,
  RimSage/decompile-confirmed) can't express declaratively. Everything else
  in §2 (application via RC4's already-shipped `hediffToApply`, mood via
  vanilla `ThoughtWorker_Hediff`, nightmares via vanilla
  `HediffStage.mentalStateGivers`) is zero new C#, matching the spec's own
  prediction. (`src/RimMandrake/EnvironmentalHazards/Source/`)
- **`RM_LordJob_DefendPerimeter` + `RM_LordToil_DefendPerimeter`** (§4) —
  the `SpawnedPawnParams` ctor `CompSpawnerPawn.CreateNewLord` requires,
  `AddFleeToil` permanently `false` (ban §6, structural — no toil transition
  exists to route into an assault the way vanilla
  `LordJob_MechanoidsDefend` does), and a subclassed `LordToil_DefendPoint`
  that assigns a caller-supplied `DutyDef` instead of the hardcoded
  `DutyDefOf.Defend` (defaulting to `DutyDefOf.Defend` when none is given,
  so the class is a strict superset of vanilla's own behavior). Deliberately
  content-blind: `RUT_SentinelDefend` (the tightened-radius `DutyDef` clone
  the owner's ruling calls for) is passed in by whoever spawns the lord,
  never hardcoded, so the class is reusable RM_-tier. Largest and riskiest
  of the three proof classes — this is the one the spec flagged needing a
  real build-time check. (`src/RimMandrake/EnvironmentalHazards/Source/`)

### Not built this pass, explicitly

§2's `RUT_ScarlandsMark` HediffDef + `ThoughtDef` + `RUT_ScarlandsMarkLock`
GameConditionDef (pure XML, now unblocked by finding 4 above). §3's
`RUT_ScariaIncubation` HediffDef + the `ArmLatentHazardExtension` instance
that arms it (pure XML, now unblocked by the RC5 fields above). §4's
`RUT_Sentinel*` PawnKindDefs, `RUT_SentinelDefend` DutyDef, repair-alcove/
grave-ward spawner buildings (content, rides `RM_LordJob_DefendPerimeter`
above). §5's `RUT_` PrefabDef wreck-dressing content + scatter GenStep
(content, now confirmed zero-C# by finding 3). All are later, separate
FOUNDRY build-pass work — the mynock/§1 content is DONE (see reconciliation
above), nothing further owed there.

## verdict

4 named engine claims resolved with file:line/class citations against the
real 1.6/Odyssey decompile — none left a guess standing. Three compiling C#
proof classes landed (RC5's two-field extension, the severity floor, the
Sentinel lord/toil pair), 0 warnings/0 errors
(`"C:\Users\Mandrake\.dotnet\dotnet.exe" build ... RM_EnvironmentalHazards.csproj
-c Release`). The dominant finding this pass, same shape as Greentide's own
spike: the kit's own spec had gone stale against work that shipped under
different names after it was drafted — §1's entire mynock mechanic
(`SHIP_VERMIN_MOD_1`, `WRECKAGE_VERMIN_SPAWN_1`) and §2's RC4 hediff fields
(`MIASMA_MECHANICS_1`'s M4 build) — and was still describing both as
unbuilt. `scarlands_kit_spec.md` is corrected at §1 and §2 so the next
reader doesn't redo shipped work. Remaining unbuilt surface (§2's HediffDef/
ThoughtDef/lock, §3's HediffDef/arming instance, §4's Sentinel content +
lord wiring, §5's prefab dressing) is honestly owed to later build passes —
item stays in `doing`.

## files

- `src/RimMandrake/EnvironmentalHazards/Source/ArmLatentHazardExtension.cs`
  (2 new fields: `pawnKindFilter`, `requiredHediff`)
- `src/RimMandrake/EnvironmentalHazards/Source/GameCondition_ArmLatentHazard.cs`
  (`Eligible()` gates on the 2 new fields)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_SeverityFloor.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_LordJob_DefendPerimeter.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj`
  (2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll`
  (rebuilt, 0 warnings/errors)
- `design/Jawa/worldbuilding/biomes/kits/scarlands_kit_spec.md` (§1/§2
  reconciled against shipped code; §1/§2/§4/§5 ❓s resolved)

## criteria

- Every mechanic traces to a sheet section; no lore invented outside
  **INVENTED** tuning values already in the spec.
- Naming per `design/NAMING_SCHEME_PLAN.md`: mechanism classes `RM_` tier;
  §1 content already RSW_-tier (`RSW_Mynock`) per the owner's own ruling;
  remaining content (§2-5) is RUT_-tier, owed to later passes. "Jawa" stays
  lore text only.
- No duplicate defs/classes against what `SHIP_VERMIN_MOD_1`,
  `WRECKAGE_VERMIN_SPAWN_1` and `MIASMA_MECHANICS_1` already shipped —
  enforced by this pass's own spec reconciliation, to be checked again at
  the next build pass.
