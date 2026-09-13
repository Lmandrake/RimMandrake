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
- [ ] Pool terrains grant no buildable affordance; marsh grounds never carry
      Heavy; `RUT_StiltPlatform` is the only Heavy route at ground level. —
      engine seam confirmed (`Verse/BuildableDef.cs:52`,
      `RimWorld/GenConstruct.cs:494`); XML audit + `RUT_StiltPlatform`
      TerrainDef not authored this pass (F5 is XML-only, no C# to spike).
- [ ] Ant raid exits with living thornbugs → they are recoverable alive
      (theft, not slaughter), once the raid-back quest ships. —
      `RUT_HaulPawnAndExit` JobDriver built and compiles; the ants'
      FactionDef, LordJob/LordToil wiring, thornbug victim-finder, and the
      raid-back QuestScriptDef are not — see F9 below.

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
