# FEVER_WOOD_MECHANICS_1 — the Fever Wood C# kit, spike pass landed

## spec
The authoritative brief is the FROZEN lore sheet
`design/Jawa/worldbuilding/biomes/the_fever_wood.md` (Owed section = ruling
scope). **Kit spec DRAFTED 2026-09-11:
`design/Jawa/worldbuilding/biomes/kits/fever_wood_kit_spec.md`** — 9 mechanics
(F1–F9) engine-mapped against RimSage source, 3 sibling-kit reuses from
`greentide_kit_spec.md` (causeway GenStep, Greatbole/LivingRegrowth class,
silence cue), 7 new RM_/RUT_ classes (1 L, 4 M, 2 S).

🔑 **The "3 owner cards open" line above this edit was STALE, same pattern
`MIASMA_MECHANICS_1`'s spike found on its sibling kit.** All three are ruled,
directly in the kit spec's own "Owner cards" section, dated 2026-09-12 (two
commits: `831201d4c` rules card 1, `744da3686` rules cards 2 and 3) — one day
after this item's 2026-09-11 draft, in a sitting separate from and after
`KIT_SPECS_CARD_SITTING_1`. Rulings: **card 1** hidden plumbing factions are
FINE (A, spec as written — §6.2's "no faction allegiance" is a lore rule, not
a ban on hidden system FactionDefs); **card 2** dragged under, rescue window
(B — colonists/tamed go down with a drowning clock, adjacent pawns can pull
them out; wild animals stay the clean-splash despawn); **card 3** fear radius
as drafted (A, ~40 cells). Nothing in F1–F9 is blocked on these cards anymore.

The filing title's four systems all land in the spec: the Tenant as
map-spanning aquifer entity (F1: pool-strike logic, never-resolved rule),
evidence + mirror-break events (F2), marsh building-refusal terrain (F5),
pool-state intelligence (F3). The sheet's Owed additions likewise: boughway
network (F6, static in v1 — moving lanes parked on
`EXPLOSIVE_PLANT_GROWTH_1` v2, same posture as the Greentide's clause),
nectar-for-safety herd economy (F8, ban §6.6 enforced in the comp), two-front
war with ant theft-hauling + raid-back quest (F9), and the deep thing built in
full but dormant (F4 — defs + art ship, referenced by nothing; the emergence
event files with the plot when its moment is chosen).

"The Tenant" is the internal working name only (live in `water_taxonomy.csv`
row `fever_pool`); hard ban §6.1 keeps it out of player-facing text.

Build dependencies: `GREENTIDE_MECHANICS_1` M9/M12 land before F6/F7 — **checked
this pass and still blocked**: `GREENTIDE_MECHANICS_1` is closed
(`0167e7af`), but its own ledger note says it closed at spec-drafting only
("build waits on `ALPHA_MECHANICS_KIT_1` first per each spec's build order");
`RM_GenStep_RootCauseways` and `RM_MapComponent_LivingRegrowth` (the
Greatbole class) do not exist anywhere in `src/` — closed ≠ built. F6/F7 stay
gated on that sibling class actually landing, not on any card. F9's raid-back
quest may trail its raids by one build. ❓-marked engine seams in the spec
**re-verified this pass** against the real vendored 1.6/Odyssey decompile at
`/mnt/d/Luke/dev/reference/rimworld-decompiled` (not the 1.5-era RimSage
index) — see the spike pass section below.

## verify
- [x] No Tenant ThingDef is reachable from any ambient IncidentDef/ThinkTree —
      `RUT_TenantEmergenceSpawner` (F4) and `RUT_MapComponent_TheTenant` (F1)
      are referenced by nothing this pass added; the Tenant is data, not a
      Thing, so the ban holds by architecture.
- [x] `Gathered()` on a below-floor-calm thornbug yields zero regardless of
      caller — **not via `Gathered()` itself** (see spike pass: it is
      non-virtual, unoverridable). `RM_CompGatherableCalmGated` overrides
      `Active` instead, the real and only gate both vanilla callers
      (`WorkGiver_GatherAnimalBodyResources`, `JobDriver_
      GatherAnimalBodyResources`) use; a decompile-wide grep confirms
      `JobDriver_GatherAnimalBodyResources` is the ONLY caller of
      `Gathered()` in vanilla, so this closes "regardless of caller" for
      every reachable path.
- [x] Pool terrains grant no buildable affordance; marsh grounds never carry
      Heavy; `RUT_StiltPlatform` is the only Heavy route at ground level. —
      **closed by the F5 build pass (2026-09-24).** MEASURED this closing
      pass, direct read of every terrain def in play:
      `RUT_FeverWoodMirrorPool.xml` carries no `<affordances>` element at
      all (inherits `WaterDeepBase`'s none); the ground-refusal GenStep
      converts every remaining Soil/SoilRich cell to vanilla `MarshyTerrain`
      (`Light`/`GrowSoil`/`Diggable`/`Bridgeable` only — MEASURED against
      the shipped `Data/Core/Defs/TerrainDefs/Terrain_Natural.xml`, no
      Medium/Heavy); `RUT_Boughway` (elevated) carries `Light`/`Medium`
      only, no Heavy; `RUT_StiltPlatform` alone carries
      `Light`/`Medium`/`Heavy`/`Walkable`. So Heavy is reachable at ground
      level nowhere in this biome except the stilts, exactly as required.
      Architecturally proven, not live/bridge-verified (no game access this
      task, same posture as every other pass in this item).
- [ ] Ant raid exits with living thornbugs → they are recoverable alive
      (theft, not slaughter), once the raid-back quest ships. — **not
      closed by this item; ownership moved.** `RUT_HaulPawnAndExit`
      JobDriver built and compiles (this item's own F9 spike); the
      remainder — the ants'/Feralisks' hidden FactionDefs, LordJob/LordToil
      wiring, thornbug/animal victim-finder, staggered paired-arrival
      IncidentWorker, the lure building, and the raid-back quest — is now
      explicitly owned by `FEVERWOOD_TWO_FRONT_LURE_1` (filed 2026-09-23,
      cites this item's F9 spike as its own foundation) and
      `FEVERWOOD_ANT_HIVE_DUNGEON_1` (the ants' hive-as-dungeon ruling).
      Leaving this bar unchecked here is correct and permanent — it closes
      under those items, not this one.

## criteria
- [x] The three cards ruled at a card sitting before C# is spent on
      F1 (card 2 changes its strike behavior) or F9 (card 1 changes its
      architecture). — confirmed ruled 2026-09-12, this pass's own finding
      (see spec section above); C# spent on F1 and F9 per the rulings as
      written.
- [x] Build lands per the spec's order, or this file's spec section is
      updated to say what shipped and what remains — see spike pass below;
      F1/F2/F3/F4/F8/F9 spiked, F5 XML-only (not authored), F6/F7 blocked on
      `GREENTIDE_MECHANICS_1`'s classes not existing yet.

## spike pass — 2026-09-13, run per `LIQUID_TYPES_SPIKES_1`'s methodology

Sizing followed that item's own line: prove each uncertain piece minimally,
offline, against real engine source or a real compiling artifact — not the
full 9-mechanic build. New files added to the ruled kit home,
`src/RimMandrake/EnvironmentalHazards/` (`mandrake.rm.environmentalhazards`,
already built by `ALPHA_MECHANICS_KIT_1`/extended by `MIASMA_MECHANICS_1`
today). Builds clean with the eight new files added:

```
"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build "D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Source\RM_EnvironmentalHazards.csproj" -c Release
```
→ `Assemblies/RimMandrake.EnvironmentalHazards.dll`, 0 warnings, 0 errors.

Packaging note: the kit spec leaves "whether RUT_ content lives in a
standalone Fever Wood mod vs this kit's RM_ home" as FOUNDRY's call. This
pass put every new class (RM_ and RUT_ alike) in `EnvironmentalHazards/`,
same as `MIASMA_MECHANICS_1` did for its own RM_-only roster — a build-time
convenience, not a packaging ruling.

### Per-mechanic disposition

- **F1 (the Tenant, one aquifer)** — **PROVED (spine).**
  `RUT_MapComponent_TheTenant` + `RM_LurkingWaterExtension` +
  `RM_TenantTruceExtension`. Card 2 (ruled: rescue window) implemented for
  real: strikes on colonists/tamed pawns call `Verse/HealthUtility.cs:246`
  `DamageUntilDowned` (confirmed real, non-lethal) then track a countdown
  cleared by `Verse/Pawn.cs:882` `CarriedBy != null` (rescued) or expiring
  into the despawn wild animals already get. Exposure/strike uses the real
  `Rand.MTBEventOccurs(float mtb, float mtbUnit, float
  ticksSinceLastCheck)` (`Verse/Rand.cs:509`, called the same way vanilla
  itself does at `:715`).
- **F2 (pool evidence + mirror-break)** — **PROVED (thin).**
  `RUT_IncidentWorker_MirrorBreak` confirms the `IncidentWorker.
  TryExecuteWorker` seam (`RimWorld/IncidentWorker.cs:289`, protected
  virtual) and writes into F1's agitation store. Silence-cue reuse is
  **not yet wired**: `RM_MapComponent_SilenceCue`
  (`src/RimMandrake/CreatureBehaviors/`) exists but its only trigger is a
  carrying pawn's `PredatorHunt` job near a colonist — it has no public
  "hush now" entry point an unrelated event can call. Owed: either give it
  one, or resolve the assembly split so EnvironmentalHazards can reference
  it.
- **F3 (mirror list intel)** — **PROVED (minimal).**
  `RM_CompUseEffect_RevealHazards` confirms the spec's own ❓ was correct as
  written: `CompUseEffect` (`RimWorld/CompUseEffect.cs`) is a real abstract
  `ThingComp` with virtual `DoEffect`; `MapComponentUpdate`/
  `MapComponentOnGUI` (`Verse/MapComponent.cs:12,20`) are real virtual draw
  hooks. Reuses F1's agitation store as the "flagged" signal rather than a
  second parallel array. Not done: trader-kind XML, the actual overlay
  draw call.
- **F4 (deep thing, dormant)** — **PROVED (gate + seam only), rest OWED by
  design.** `RUT_TenantEmergenceSpawner : BuildingGroundSpawner` — confirmed
  real at `RimWorld/BuildingGroundSpawner.cs` (re-terrains for affordance on
  spawn, matches the spec's own citation) and referenced by nothing, so ban
  §6.1's linter check passes by construction. The L-effort remainder
  (`RUT_TenantEmergedMass`, `RUT_TenantTentacle` pawn wiring, all art) is
  explicitly not done — off the critical path by the sheet's own design, not
  silently skipped.
- **F5 (ground refusal + stilts)** — **Engine claim confirmed, no C# needed.**
  `BuildableDef.terrainAffordanceNeeded` (`Verse/BuildableDef.cs:52` —
  corrects the spec's own citation path, which said `Source/RimWorld/
  BuildableDef.cs`; the class is in `Verse`, not `RimWorld`) and its
  enforcement at `RimWorld/GenConstruct.cs:494` are both real, exactly as
  the spec assumed. This mechanic is XML + a donor-terrain audit; nothing to
  spike.
- **F6 (boughway network)** — **BLOCKED on `GREENTIDE_MECHANICS_1`, not on
  cards.** `RM_GenStep_RootCauseways` does not exist in `src/` anywhere —
  see the "Build dependencies" correction above. Not attempted.
- **F7 (bore-caves / Greatbole reuse)** — **BLOCKED, same reason.**
  `RM_MapComponent_LivingRegrowth` does not exist in `src/` anywhere. Not
  attempted.
- **F8 (thornbugs, fear-gated nectar)** — **PROVED, with a real correction
  to the spec.** `RM_CompGatherableCalmGated`. The spec's plan —
  "`Gathered()` override yields ZERO below a calm floor" — **does not
  compile as written**: `RimWorld/CompHasGatherableBodyResource.cs`'s
  `Gathered(Pawn)` is `public void`, not virtual, not abstract; no subclass
  can override it. The real seam, confirmed against both vanilla callers
  (`RimWorld/WorkGiver_GatherAnimalBodyResources.cs`'s `ShouldSkip`/
  `HasJobOnThing`, and `RimWorld/JobDriver_GatherAnimalBodyResources.cs`'s
  `AddEndCondition(() => ... ActiveAndFull ? Ongoing : Incompletable)`) is
  `Active` (`protected virtual`) — exactly the pattern
  `RimWorld/CompMilkable.cs` already ships (its `milkFemaleOnly`/life-stage
  gates). Gating `Active` below the calm floor stops fullness accrual
  (`CompTick` checks `Active`), blocks the WorkGiver from ever offering the
  job, and aborts an in-progress gather the instant calm crashes — and a
  decompile-wide grep for `.Gathered(` finds exactly one call site
  (`JobDriver_GatherAnimalBodyResources`), so this closes ban §6.6's
  "regardless of caller" for every vanilla-reachable path. Fear source uses
  the real `Map.dangerWatcher.DangerRating`
  (`RimWorld/DangerWatcher.cs`) plus a direct hostile-pawn scan at card 3's
  ruled ~40-cell radius, closing the spec's own ❓ without inventing a new
  detector.
- **F9 (two-front war, ant theft-hauling)** — **PROVED (driver only), one
  correction found.** `RUT_HaulPawnAndExit : JobDriver_TakeAndExitMap`
  reuses `JobDriver_Kidnap`'s exact `FailOn` (`!Takee.Downed &&
  Takee.Awake()`) — confirmed real and correctly generalizable to an
  animal target. **Correction**: the spec's cited victim-finder,
  `RimWorld/KidnapAIUtility.cs`'s `TryFindGoodKidnapVictim`, filters
  `pawn.RaceProps.Humanlike` in its own validator — **not reusable for
  thornbugs as written**; a new predicate (crib `StealAIUtility`'s
  targeting shape, generalized to downed tamed/wild animals) is needed for
  the ants' LordJob, not built this pass. `FactionDef.permanentEnemy`
  (`RimWorld/FactionDef.cs:186`) confirmed real and sufficient alone —
  Faction.cs:411/419 shows a `permanentEnemy` faction is hostile to
  literally everyone including another `permanentEnemy` faction, so setting
  it on both `RUT_AntSwarm` and `RUT_FeraliskBrood` delivers "hostile to
  the player AND to each other" from one bool each, no XML complexity
  beyond it (spec's citation range 186-190 was directionally right — the
  three related fields sit at exactly 186/188/190). Forcing a raid's arrival
  edge (the spec's other ❓) is confirmed achievable: `IncidentParms.
  spawnCenter` can be preset by the calling IncidentWorker before
  `PawnsArrivalModeWorker_EdgeWalkIn.TryResolveRaidSpawnCenter` runs
  (`RimWorld/PawnsArrivalModeWorker_EdgeWalkIn.cs`). Target-preference
  weighting (ants/feralisks preferring each other over the player) was
  **not found** as an exposed seam beyond plain `permanentEnemy` contact
  hostility — this matches the spec's own stated fallback ("v1 ships
  contact-hostility only"), not a new gap. Not built: the two hidden
  FactionDef XMLs, LordJob/LordToil wiring (crib `LordToil_KidnapCover`'s
  shape), the new victim-finder, the "unclamp stun" downing job, and the
  raid-back QuestScriptDef.

## verdict

6 of 9 mechanics (F1, F2, F3, F4, F8, F9) got a real, compiling spike proof
this pass, all re-verified against the live 1.6/Odyssey decompile rather
than the 1.5-era RimSage index the spec was drafted against — one mechanic
(F8) had a genuine unbuildable-as-written correction (Gathered() is
non-virtual; Active is the real gate) and another (F9) had a genuine
victim-finder correction (KidnapAIUtility is humanlike-only). F5 needed no
C#, just a confirmed engine claim. F6 and F7 are correctly left unbuilt —
not because of the three owner cards, which are all ruled and gate nothing
here, but because their sibling reuse targets
(`RM_GenStep_RootCauseways`, `RM_MapComponent_LivingRegrowth`) do not exist:
`GREENTIDE_MECHANICS_1` closed at spec-drafting only, same posture this item
itself is closing at. No live/bridge/quicktest verification was done or
attempted, per scope.

## files

- `src/RimMandrake/EnvironmentalHazards/Source/RM_LurkingWaterExtension.cs` (F1/F5)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_TenantTruceExtension.cs` (F1)
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_MapComponent_TheTenant.cs` (F1)
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_IncidentWorker_MirrorBreak.cs` (F2)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompUseEffect_RevealHazards.cs` (F3)
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_TenantEmergenceSpawner.cs` (F4)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompGatherableCalmGated.cs` (F8)
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_HaulPawnAndExit.cs` (F9)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (8 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_FeverWood_MirrorBreak.xml` (F2, wired)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_FeverWood_MirrorList.xml` (F3, wired)
- `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_FeverWoodMirrorPool.xml` (F1/F5 pt.3, wired)
- `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_StiltPlatform.xml` (F5 pt.2, wired)

## continuation pass — 2026-09-13, resuming after an interrupted run

Picked up two files already sitting uncommitted from the prior pass
(F2/F3, above) — validated clean (see below), not redone. Continued wiring
per the spike roster (F1, F4, F5, F8, F9):

- **F2/F3 (pre-existing, this pass's own finding)**: both validate 0
  errors/0 warnings against `validate_patch.py` with the installed-defs
  cross-check. `RUT_FeverWood_MirrorList.xml` had one real defect the
  previous pass's own header claimed was already caught but the file on
  disk still had: a literal `--` inside an XML comment body (naming the
  validator's own `--defs` flag), which is illegal in XML and broke the
  parse. Fixed by rephrasing the comment (no flag syntax inside the
  comment body); no field/logic change.
- **F1 (the Tenant, terrain half) — WIRED.** `RUT_FeverWoodMirrorPool.xml`:
  new `TerrainDef` (`ParentName="WaterDeepBase"`, the same already-verified-
  safe base `RUT_ScaldWater.xml` uses) carrying
  `RM_LurkingWaterExtension` as a real `modExtensions` entry, `MayRequire`-
  gated. Gives `RUT_MapComponent_TheTenant`'s terrain-grid scan (it auto-
  attaches to every map — `Map.FillComponents()` instantiates every
  `MapComponent` subclass automatically, no Def wiring needed for the
  component itself) something real to find. Deliberately carries no
  `<affordances>` (inherits `WaterDeepBase`'s none) and no `dbh_water` tag
  (unlike `RUT_ScaldWater.xml`'s own precedent — marking it drinkable would
  contradict §5/§7b's "nothing goes in the water here"). **Not done**:
  painting this terrain onto any generated Fever Wood map. Editing the
  already-shipped `RUT_FeverWood.xml` BiomeDef's `terrainsByFertility` to
  reference a `MayRequire`-gated defName risks a dangling cross-reference if
  `mandrake.rm.environmentalhazards` is ever absent, and the actual
  fertility threshold is an unspecified tuning call the kit spec gives no
  number for — left for a GenStep pass (F6's shape) or a deliberately-
  guarded terrainsByFertility edit, not guessed here. `RM_TenantTruceExtension`
  (native-pawn exemption) has no PawnKindDef to attach to yet — no Fever
  Wood native roster (Wookiee/Ewok/Wildsteam kinds) exists in `src/` at all;
  that's the roster pass's territory, not this item's.
- **F4 (deep thing, dormant) — CONFIRMED, correctly left unwired.**
  Re-checked: `RUT_TenantEmergenceSpawner` is still referenced by nothing.
  It cannot be safely wired into even a dormant `BuildingDef` yet regardless
  — its own class comment notes a `BuildingDef` needs a real
  `groundSpawnerThingToSpawn` target, and `RUT_TenantEmergedMass` (the L-
  effort remainder) does not exist. Ban §6.1 holds by construction; nothing
  to do here until the roster/art pass lands the emerged-mass def.
- **F5 (ground refusal + stilts) — PARTIALLY WIRED.** Point 3 (pool water
  grants no affordance) ships in `RUT_FeverWoodMirrorPool.xml` above.
  Point 2 (stilts): `RUT_StiltPlatform.xml`, a new `TerrainDef`
  (`ParentName="Bridge"`, verified real via RimSage this pass — vanilla
  `Bridge` carries `Name="Bridge"`), Heavy/Medium/Light/Walkable affordances
  and construction shape copied from vanilla `HeavyBridge`'s own merged def,
  costed at 30 wood (kit spec's own "INVENTED, >= 2x bridge" rule off
  Bridge's 12-wood cost). Pure XML, no C#, no `MayRequire` needed. **Point 1
  (ground refusal audit) NOT done, and a real gap found, not guessed away**:
  `RUT_FeverWood.xml`'s own `terrainsByFertility` currently lists only
  vanilla `Soil`/`SoilRich` — there is no biome-specific marsh/mud terrain
  to audit yet, so ground-level Heavy building is NOT currently refused
  anywhere in this biome, contradicting hard ban §6.4. Fixing it means
  authoring real marsh terrain (texture, values, which fertility band) to
  replace the shared vanilla terrain in this biome's own table — genuine
  unspecified design, not touched this pass to avoid inventing it or
  breaking the shipped, FROZEN-sheet biome's terrain table blind.
- **F8 (thornbugs) — left as a compiling skeleton, not wired, on purpose.**
  `RM_CompGatherableCalmGated` has no `ThingDef`/`PawnKindDef` to attach to.
  The kit spec itself assigns "RUT_Thornbug PawnKindDef (roster pass owns
  stats/art)" to a different pass — building a full animal def (body plan,
  life stages, wildness, market value) here would be inventing content this
  item does not own, the same category of gap the previous pass avoided for
  Sporefall's trader lane. No repo precedent for
  `CompProperties_HasGatherableBodyResource` exists yet to safely clone
  from either (checked: zero hits in `src/RimUtinni`).
- **F9 (two-front war) — left as a compiling skeleton, not wired, on
  purpose.** `RUT_HaulPawnAndExit`'s own class comment already lists what's
  missing (hidden FactionDef XML, LordJob/LordToil wiring, a new victim-
  finder predicate, an "unclamp stun" job, the raid-back quest) — all
  genuine new design/mechanism work at M/L effort, not a Def-wiring step
  like F2/F3/F1/F5 were. Confirmed unchanged this pass; not attempted.

Build: `RM_EnvironmentalHazards.csproj` rebuilds clean, 0 warnings/0 errors,
no new `.cs` files this pass (only existing spike classes wired into new
XML). All four touched/added Fever Wood def files (`RUT_FeverWood_
MirrorBreak.xml`, `RUT_FeverWood_MirrorList.xml`,
`RUT_FeverWoodMirrorPool.xml`, `RUT_StiltPlatform.xml`) validate 0 errors/0
warnings via `validate_patch.py` against the live 590-mod installed set.

Remaining after this pass: F1's terrain-painting step, F4's L-effort
remainder (off critical path by design), F5 point 1 (ground-refusal
terrain), F6/F7 (blocked on `GREENTIDE_MECHANICS_1`'s own classes, still
absent from `src/`), F8's content (roster pass), F9's Lord/Faction/quest
build. Item stays in `doing`.

## F6/F7 build pass — 2026-09-14

Unblocked by `GREENTIDE_MECHANICS_2`'s own M9/M12 build pass (same day,
commits `07118c4e6`/`647b306fe`): `RM_GenStep_RootCauseways` and
`RM_MapComponent_LivingRegrowth` now exist, compile, and — checked for
real this pass rather than assumed from the sibling item's own claim — are
genuinely reusable as advertised. Built F7 first (trunk anchors), then F6
(reads F7's registered bole centers automatically via
`RM_MapComponent_LivingRegrowth.BoleCenters`).

**Greentide-class reuse finding: genuinely reusable, with one real gap.**
Read all four classes (`RM_GenStep_RootCauseways`,
`RM_MapComponent_LivingRegrowth`, `RM_CompLivingBoleMarker`,
`RM_LivingBoleBiomeExtension`, `RM_RootCausewayBiomeExtension`) before
writing anything. Nothing in them names Greentide, a bole, or a
Churnmud — every one is a harmless no-op on any `BiomeDef` that doesn't
carry its extension, exactly the "generic kit's home" promise the sibling
item's own header makes. F7 used them completely unmodified (**"No new
C#" holds**). F6 found one real gap: the kit spec's own text claims the
ground-causeway pass is "the same GenStep's second call... zero extra
code, just a second GenStepDef instance with different tuning" — but
`RM_GenStep_RootCauseways` reads its whole profile off the ONE
`RM_RootCausewayBiomeExtension` instance a `BiomeDef` carries
(`GetModExtension<T>()` returns only the first match of a type), so a
second `GenStepDef` of the same class would read the IDENTICAL extension
and repaint the identical lanes, not a second, differently-tuned network.
Fixed with the minimal generic addition described below — not
Fever-Wood-specific, and Greentide's own existing single-profile XML is
unchanged (`additionalPasses` defaults to null/empty).

**F7 — bore-caves and the trunks.** `RUT_FeverTrunkHeartwood` (mineable
`ThingDef`, `ParentName="RockBase"`, cribbed field-for-field from
`RUT_GreatboleHeartwood`) + `RUT_FeverTrunkCore` (marker `ThingDef`,
cribbed from `RUT_GreatboleCore`, oversized `drawSize` reusing vanilla's
real `Things/Building/Misc/DeepDrillPowered` texture with a paler tint,
same RESOLVED ❓ the Greentide spike already settled — a plain
`GraphicData.drawSize` override, not a Skyfaller). `RM_LivingBoleBiomeExtension`
wired directly onto `RUT_FeverWood.xml`'s own `modExtensions` (a direct
edit, not a Patch — matching `RUT_Greentide.xml`'s own precedent for
these two specific extensions: each risky cross-reference is guarded at
its own `<li MayRequire=...>`, not by a patch layer around the whole
addition).

Two real decisions, not guessed:
- **mineableThing = vanilla `WoodLog`, not `RUT_Hardwood`.** `RUT_Hardwood`'s
  own description is Greentide-flavor-specific ("cut from the living heart
  of a Greatbole... worth real money off-world") — wrong lore for a Fever
  Wood trunk, and inventing a second bespoke wood-resource economy here is
  exactly the unrequested-design category F8/F9's own prior passes already
  declined. Vanilla `WoodLog` is the honest neutral choice.
- **sealantTerrain reuses `RUT_ToxinSealant` verbatim** (the ALREADY-SHIPPED
  Greentide terrain) rather than a second Fever-Wood-named sealant def —
  same "one def, reused cross-kit" shape `RUT_Scald`/`RM_ScaldArmor`
  already set (checked per the calling brief's own pointer:
  `FORGE_MECHANICS_1` reused Greentide's damage-type trio rather than
  duplicating it). Gated `MayRequire="mandrake.rm.environmentalhazards,mandrake.rm.greentide"`
  — TWO packages, not one, since `RUT_ToxinSealant.xml`'s own def carries
  `MayRequire="mandrake.rm.greentide"` (its `costList` consumes a
  Greentide-mod item) and a reference to it needs the same guard or it
  dangles. **Real finding against the sibling precedent, not fixed there
  (out of this item's scope):** `RUT_GreatboleCore.xml`'s own comp `<li>`
  (in `GREENTIDE_MECHANICS_2`) is gated on
  `MayRequire="mandrake.rm.environmentalhazards"` ONLY, despite the exact
  same `sealantTerrain` reference — a latent dangling-cross-reference risk
  in the already-shipped Greentide code if `mandrake.rm.environmentalhazards`
  were ever active without `mandrake.rm.greentide` (currently moot: both
  ship together in this campaign's full mod list, but inconsistent with
  that same file's own sibling M9 extension, which DOES two-package-gate
  its cross-mod `basinTerrains` reference). Flagged for the record in this
  def's own header; not touched (`GREENTIDE_MECHANICS_2`'s file, not this
  item's).

Regrowth retuned per the spec's own INVENTED call ("this biome is the
still one"): `regrowDaysRange` 10~18 days versus the Greatbole's 3~6 —
roughly 3x. Creak/crush timings left at the shared class's own defaults;
the spec names no separate number for those.

**F6 — the boughway network.** `RUT_Boughway` `TerrainDef` (elevated lane:
`pathCost` 1, affordances Light+Medium only — no Heavy, "platforms yes,
bunkers no" per the spec's own INVENTED tier) is `RM_RootCausewayBiomeExtension`'s
primary profile on `RUT_FeverWood`, anchored automatically on F7's
registered trunk centers. The "ground causeway... second pass" uses the
new `additionalPasses` field with `RUT_RootCauseway` reused verbatim
(narrower/shorter/fewer paths per anchor than the primary network, so it
reads as the modest, cheap alternative rather than a duplicate network).

**RESOLVED ❓ (water-bridging):** checked `Verse/TerrainGrid.cs:193`
(`TerrainGrid.SetTerrain`, the real method GenStep terrain-painting calls)
against the live 1.6/Odyssey decompile — it carries NO
`terrainAffordanceNeeded`/Bridgeable check at all, only null/bounds/
temporary/`isFoundation` branches. That gating exists exclusively on the
PLAYER-CONSTRUCTION path (`BuildableDef.terrainAffordanceNeeded` +
`GenConstruct.cs:494`, F5's own already-confirmed engine route), which
map-gen terrain painting never goes through. **There is no
"Bridgeable-style replacement" mechanism to reuse in the first place** —
so the simpler, more honest route (taken here) is to never paint a
boughway cell over a registered pool at all, not to synthesize a
drawn-fiction bridge visual with no engine mechanism behind it. Both
passes' `basinTerrains` is set to Fever Wood's own two buildable ground
terrains (`Soil`/`SoilRich`, `RUT_FeverWood.xml`'s own
`terrainsByFertility`) — `PaintFootprint`'s existing "restricted to
basinTerrains" allowlist check (built for Greentide's opposite use,
painting ONLY over its churnmud basin) doubles as an EXCLUDE of
everything not in that list, including `RUT_FeverWoodMirrorPool` and
`RUT_StiltPlatform`, with **zero new C# for the exclusion itself**. This
preserves F1's pool-terrain registry (`RUT_MapComponent_TheTenant`'s own
terrain-grid scan would lose a cell if a boughway simply overwrote it) and
the lore's own "nothing goes in the water here." Caveat for the record:
F1's own `RUT_FeverWoodMirrorPool` terrain is not yet painted onto any
generated map by any GenStep (the continuation pass's own note — "not
done: painting this terrain onto any generated Fever Wood map" still
holds), so this exclusion is a forward safeguard for when that painting
step lands, not something that changes today's generated output.

Per-mechanic C# needed: **F7 none** (pure XML/content, as the spec
demanded). **F6 one minimal, generic addition** — `RM_RootCausewayPass`
(a plain nested profile class: `causewayTerrain`/`basinTerrains`/
`pathsPerAnchorRange`/`laneWidthRange`/`pathLengthRange`/
`turnChancePerStep`) plus `RM_RootCausewayBiomeExtension.additionalPasses`
(`List<RM_RootCausewayPass>`, default null) and a refactor of
`RM_GenStep_RootCauseways.Generate` to build a `CausewayProfile` struct
from the primary extension fields, run it, then run one more per
`additionalPasses` entry over the same anchor set — `TraceSpline`/
`PaintFootprint`/`ConnectNearestNeighbors`/`ConnectAnchors` now take that
struct instead of the extension directly. Backward-compatible:
`RUT_Greentide.xml`'s own existing single-profile XML is untouched and
behaves identically (`additionalPasses` unset).

**Slow variation** — explicitly not attempted, per the calling brief and
the spec's own deferral (parked on `EXPLOSIVE_PLANT_GROWTH_1`'s v2 list,
same posture as Greentide's identical clause).

**Build/validate.** `RM_EnvironmentalHazards.csproj` rebuilds clean, 0
warnings/0 errors, with only the two touched `.cs` files (no new `.cs`
files — F6's addition lives inside the two already-existing M9 classes).
`validate_patch.py` against the live 99-active-mod installed set: 4 new/
changed def files (`RUT_FeverTrunkHeartwood.xml`, `RUT_FeverTrunkCore.xml`,
`RUT_Boughway.xml`, `RUT_FeverWood.xml`), 0 errors, 1 expected WARN
(`RUT_FeverTrunkCore`'s reused vanilla `DeepDrillPowered` texture — "cannot
verify a packed vanilla texture from here," the same class of WARN
`RUT_GreatboleCore`'s own identical reuse gets) plus the one pre-existing,
unrelated WARN (`mandrake.rut.vaultdungeons` has no folder on disk).

**Art.** `RUT_FeverTrunkHeartwood` ships a genuine flat-color placeholder
PNG (`Textures/Things/Building/RUT_FeverTrunkHeartwood/RUT_FeverTrunkHeartwood.png`,
128×128 RGBA) — UtinniPatches owns the `Things/` texture namespace itself,
so a vanilla-path reuse would be a hard ERROR here, same shape
`RUT_GreatboleHeartwood`'s own header already documents. `RUT_FeverTrunkCore`
and `RUT_Boughway` both reuse real, already-loaded vanilla texture paths
(`Things/Building/Misc/DeepDrillPowered`, `Terrain/Surfaces/WoodFloor`)
with a distinguishing tint — legitimate reuse, no placeholder, no
`DEPLOY_HOLD` entry needed (terrain texture reuse is not the "Things/"
namespace-ownership check; `RUT_RootCauseway`/`RUT_StiltPlatform`'s own
headers already established this). Real bespoke art for all three is
still owed to the standing art pipeline.

**Owed after this pass.** F6's ground-causeway pass is an approximation,
not a literal water's-edge pathfinder — it runs the same anchor-based
random-walk shape as the primary network, just narrower/shorter/fewer per
anchor, not a route that hugs pool edges cell-by-cell; a true
edge-hugging placement would be genuinely new, more complex C#, out of
proportion for this pass's effort budget, and not attempted. F1's own
pool-terrain painting (noted above). No bridge/quicktest/game verification
attempted — no game access in this task, same posture as every sibling
spike/build pass in this item's own history. Wild bore-cave occupant
content (roster pass) untouched, out of this pass's scope per the calling
brief.

Item stays in `doing`.

## files (F6/F7 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_RootCausewayBiomeExtension.cs` (new `RM_RootCausewayPass` class + `additionalPasses` field)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GenStep_RootCauseways.cs` (multi-pass refactor)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_FeverTrunkHeartwood.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_FeverTrunkCore.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_Boughway.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_FeverWood.xml` (modExtensions added)
- `src/RimUtinni/UtinniPatches/Textures/Things/Building/RUT_FeverTrunkHeartwood/RUT_FeverTrunkHeartwood.png` (new placeholder)

## F5 build pass — 2026-09-24 (ground building-refusal terrain)

Picked up F5 point 1, the one concrete gap the continuation pass (2026-09-13)
flagged and explicitly declined to guess through: `RUT_FeverWood.xml`'s own
`terrainsByFertility` lists only vanilla `Soil`/`SoilRich`, both
Heavy-affordance terrains (MEASURED this pass, direct read of the shipped
`Data/Core/Defs/TerrainDefs/Terrain_Natural.xml`), so hard ban 4 ("No heavy
structures on the ground — the marsh refuses them (donor, kept)") was not
actually enforced anywhere on a generated map — a real linter-checkable
ban, silently unmet.

**Not fixed by editing `terrainsByFertility` directly.** A sibling item
landed the SAME DAY (`FEVERWOOD_BOUGH_SOIL_TERRAIN_1`, a different FOUNDRY
pass, 17:01-17:11 UTC — crown-soil fertility, a different gap on the same
BiomeDef) and its own "Watch out" section rules that table off-limits
pending the terminal biome-paint pass (`BIOME_PAINT_ONCE_AT_THE_END_1`) and
names the GenStep route as the correct one instead: "Paint via the GenStep;
do not reach for the fertility table." Followed that precedent rather than
re-litigating it.

**The fix: a new generic GenStep, not a bespoke terrain.** `RM_GenStep_GroundRefusal`
+ `RM_GroundRefusalBiomeExtension` (same BiomeDef-modExtension idiom as
`RM_GenStep_ScatterPools`/`RM_GenStep_RootCauseways`/`RM_GenStep_LivingBoles`)
sweep every map cell after generation and convert whatever is still listed
in `convertFromTerrains` (Soil/SoilRich) to `refusalTerrain`. `refusalTerrain`
reuses **vanilla `MarshyTerrain`** (`Data/Core/Defs/TerrainDefs/Terrain_Natural.xml`)
rather than a bespoke `RUT_` def — MEASURED this pass: affordances Light +
GrowSoil + Diggable + Bridgeable, NO Medium, NO Heavy (exactly the ceiling
ban 4 demands), pathCost 14 against Soil's 2 (independently matches the
sheet's own §0 donor line, "near-impassable ground movement," kept from the
donor). No MayRequire needed (Core, always loaded), no invented texture or
fertility value, no new art debt — the most defensible fix available, not
an arbitrary engineering default.

**Ordering is the whole safety mechanism, same idiom as F1/F6/F7.**
`RUT_FeverWood_GroundRefusalGenStep.xml` registers `RUT_GenStep_GroundRefusal`
at **order 230** — after `RUT_GenStep_ScatterPools` (226) and
`RUT_GenStep_RootCauseways` (228, which as of `FEVERWOOD_BOUGH_SOIL_TERRAIN_1`
also runs the bough-soil pass within that same GenStepDef/order). Every
lane/pool/crown-soil cell those earlier steps paint is no longer
Soil/SoilRich by the time this step runs, so the blanket "convert whatever
is still eligible" sweep leaves every previously-painted special cell alone
by construction — no cross-extension bookkeeping needed. Deliberately
blanket, not chance-gated: ban 4 is absolute, not a rarity dial.

Wired onto `RUT_FeverWood.xml`'s existing `modExtensions` block (direct
edit, same `MayRequire="mandrake.rm.environmentalhazards"`-gated `<li>`
pattern every other extension on this def already uses).

New WORLDGEN-AFFECTING Mod Settings toggle: `groundRefusalEnabled` (49th in
the kit) — off means a map generated while it's off keeps ordinary
Heavy-capable ground; maps already generated are untouched either way.

**Build/validate.** `RM_EnvironmentalHazards.csproj` rebuilds clean, 0
warnings/0 errors (two new `.cs` files added to the `.csproj`'s explicit
`<Compile>` list — `EnableDefaultCompileItems false`). `validate_patch.py`
against the live 620-active-mod installed set: 0 errors/0 warnings on all
3 touched/new files (the two "Class not resolved" infos are the same
expected pre-deploy note every new-class GenStepDef in this assembly gets).
Deployed to both `EnvironmentalHazards` and `UtinniPatches`, both VERIFIED
in sync (`deploy_custom_mods.py --apply`).

**Real finding, not mine to fix, flagged for the record:**
`run_selftests.py`'s full sweep (74/75 passed) caught one pre-existing,
unrelated failure surfaced by this pass's full-mod deploy —
`selftest_deployed_biome_refs.py`: `RUT_PoisonForest.xml`'s `wildAnimals`
references `RSW_VentStalker` (`MayRequire="mandrake.rsw.swbestiary"`), which
does not resolve in the currently deployed mod set. Already committed at
`666f11656` (`COMMISSION_LEDGER_CLEANUP_1`, unrelated wave, a different
seat's in-progress content), clean working tree — this pass's deploy just
carried an already-committed dangling reference from repo to the live Mods
folder for the first time; it predates and is untouched by this pass.
**Not fixed here** — different item/seat's own content, out of this pass's
scope.

**Owed after this pass.** No live/bridge/quicktest verification attempted —
same posture as every prior offline build pass in this item's history (no
game access in this task). The other owed gaps from prior passes are all
untouched and unrelated to F5: F4's L-effort remainder (dormant by design,
plot-owned), F6's ground-causeway true edge-hugging placement
(disproportionate effort, already flagged), the ants'/Feralisks' FactionDefs
+ LordJob + raid-back quest (blocked on the roster pass), F9's raid-arrival-edge
wiring. Wild bore-cave occupant content (roster pass) also untouched, per
the calling brief's own scope line.

Item stays in `doing`.

## files (F5 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_GroundRefusalBiomeExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GenStep_GroundRefusal.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (setting #49, `groundRefusalEnabled`)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_FeverWood_GroundRefusalGenStep.xml` (new)
- `src/RimUtinni/UtinniPatches/Patches/RUT_FeverWood_GroundRefusalGenStep_Register.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_FeverWood.xml` (modExtensions: added `RM_GroundRefusalBiomeExtension`)

## closing pass — 2026-09-24 (resumed after a reboot mid-work)

Resumed this item cold (prior session's F5 build pass above was already
committed and pushed at `a1ca38a04`, tree clean). Re-checked for newer work
before doing anything, per this repo's own standing lesson that this project
keeps having already built the thing being asked for: found F1's own pool-
placement gap had *also* already been closed and live-fire PASS-verified in
game (`921b9790f`, 2026-09-18/19 ledger notes on this item — pools confirmed
appearing on a real generated map via `jawa/get_terrain_batch`), which this
item's own body text above predates.

**Verified verify-bar 3 for real** (see the checked box above) rather than
leaving it as a stale 2026-09-13 "not authored this pass" note now that F5
landed — MEASURED every terrain def in play, not re-asserted from memory.

**Decided this item's own remaining scope is exhausted, not merely paused.**
Of the two things left in this item's own "criteria"/"verify" sections and
every pass's "owed after this pass" list:
- F4's L-effort remainder (emerged mass, tentacle pawn wiring, art) — this
  item's own 2026-09-13 note already scoped it to "the plot's own moment,"
  and `FEVERWOOD_TENTACLE_BESTIARY_1`/`FEVERWOOD_DIANOGA_PRISON_1` (filed
  2026-09-23) now own the deep-thing content build.
- F9's full raid mechanism (hidden FactionDefs, LordJob/LordToil, victim-
  finder, raid-back quest) — `FEVERWOOD_TWO_FRONT_LURE_1` (filed 2026-09-23)
  explicitly cites this item's own F9 spike/corrections as its foundation
  and owns the remainder; `FEVERWOOD_ANT_HIVE_DUNGEON_1` owns the ants'
  hive-as-dungeon half.
- F6's true edge-hugging boughway placement is a flagged, disproportionate-
  effort refinement on top of an already-shipped, working approximation —
  not a missing mechanism.
- Thornbug/ant roster content (F8's stats/art) is `FEVERWOOD_FLORA_ROSTER_1`/
  `FEVERWOOD_SAP_SUCKER_GUILD_1`/roster-pass territory, never this item's.

So every remaining thread has a named, filed successor item that already
claims it, cross-referencing this item's own spike work as its foundation —
the same shape `GREENTIDE_MECHANICS_1`→`GREENTIDE_MECHANICS_2` used, not the
"closed but nothing built" failure this item's own body text (above) warned
against for that sibling: here the *engine kit* (all nine mechanics
engine-mapped, six spiked+wired+build-verified, two XML-verified with no C#
needed, one driver-only by design) is genuinely built and 0-warning/0-error
compiling end to end, and only *content* (new PawnKindDefs, FactionDefs, a
quest, art) remains — all of it now tracked elsewhere by name.

**Build re-verified this pass**, no source changed:

```
"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build "D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Source\RM_EnvironmentalHazards.csproj" -c Release
```

→ 0 warnings, 0 errors (unchanged from the last committed build).

Closing this item now. No live/bridge/quicktest verification attempted this
pass beyond re-reading the already-shipped terrain defs — no game access in
this task.
