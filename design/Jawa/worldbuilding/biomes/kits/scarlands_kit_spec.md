# Scarlands C# mechanics kit spec

Build/spike item: `SCARLANDS_MECHANICS_2` (`SCARLANDS_MECHANICS_1`, filed
2026-09-07, closed 2026-09-11 at spec-only — that ID is permanently closed,
append-only ledger, never reused; see `infrastructure/state/items/
SCARLANDS_MECHANICS_2.md` for the 2026-09-14 spike pass that reconciled §1
and §2 against code shipped elsewhere and resolved the remaining ❓s below).

Engine mapping for the five mechanics fixed in
`design/Jawa/worldbuilding/biomes/the_scarlands.md` (frozen sheet — §4 mynock,
§7b curse currencies, §5/§6 Sentinel rules, §8 pre-sprung dangers). **No new
lore here.** Every engine class named below was verified against the vanilla
1.6/Odyssey source via RimSage on 2026-09-11 unless marked ❓.

Ruled-comp reuse baseline: the six RM_ generic comps ruled IN 2026-09-11
(`design/Jawa/worldbuilding/alpha_family_source_review.md` §4, build item
`ALPHA_MECHANICS_KIT_1`, mod `mandrake.rm.environmentalhazards`). Referenced
below as **RC1–RC6** (RC1 gas family, RC2 periodic area attack, RC3 glow
multiplier, RC4 environmental weather condition, RC5 scaled death explosion +
`RM_GameCondition_ArmLatentHazard`, RC6 targeted hediff ability).

Naming: mechanism classes at **RM_** tier (nothing below is Star-Wars- or
Utinni-specific as a *mechanism*); content defs (mynock tuning, Sentinel
kinds, the mark) at **RSW_/RUT_** per `design/NAMING_SCHEME_PLAN.md`.

---

## 1. Mynock ship-infestation (board / breed / eat / hunt-out) — SHIPPED, see below

**🔴 SCARLANDS_MECHANICS_2 (2026-09-14): this entire mechanic is already
built and closed.** `SHIP_VERMIN_MOD_1` (closed 2026-09-11) and
`WRECKAGE_VERMIN_SPAWN_1` (closed 2026-09-12) shipped board/breed/eat/
hunt-out in full, under different class names than this section originally
drafted, in `mandrake.rm.creaturebehaviors` +
`mandrake.rm.shipvermin` rather than this kit's own mod — an owner ruling
(2026-09-11 card sitting, "gather all the ship-infesting critters into a
single mod") made after this section was first written. **Do not rebuild
any of it.** Real shipped shape:

- **Board** — `RM_SeekTargetExtension` (`seekSubstructure` field, generic
  "walk toward data-tagged terrain") + `RM_JobGiver_SeekMarkedTerrain`
  (`src/RimMandrake/CreatureBehaviors/Source/`), attached to `RSW_Mynock`
  with `seekSubstructure=true` via
  `src/RimMandrake/ShipVermin/Patches/RSW_Mynock_ShipVermin.xml`. Vanilla
  `Gravship.ShouldBringOnGravship`/`ThingDef.bringAlongOnGravship` (default
  `true`) does the actual carry, as this section originally predicted —
  confirmed zero C# for that half.
- **Breed** — `RM_CompVerminBreeder`/`RM_CompProperties_VerminBreeder`,
  lord-free exactly as drafted below, population-capped via the shared
  `RM_MapComponent_VerminPopulation` (soft/hard cap curve, group tag
  `ShipVermin`) rather than a per-race count — a generalization beyond this
  section's own draft, reused by every future ship-vermin species.
- **Eat** — `RM_GnawTargetExtension` + `RM_JobGiver_GnawTargets` +
  `RM_JobDriver_Gnaw` (JobDef `RM_Gnaw`), same building-defName/comp-type/
  floor-terrain data-driven shape drafted below (`PowerConduit`,
  `CompGlower`, `TerrainGrid.RemoveTopLayer`), with bite damage additionally
  scaling with population pressure (the "nuisance unless there are many"
  ruling as an actual curve, not flat).
- **Hunt out** — `RM_Alert_ShipVermin` + `RM_Alert_VerminPopulationBase`;
  mynocks stay ordinary wild pawns, vanilla hunting/shooting ends it.
- **Wreck-anchored spawning** (owner ruling 2026-09-12, not in this
  section's original scope): `RM_CompProperties_VerminNest`/
  `RM_CompVerminNest`, live-verified with an actual observed spawn.
- **`RSW_Mynock`** (`src/RimStarWars/SWBestiary/Defs/ShipVermin/`) is our
  own clone, resolving the ❓ below outright, and already ships
  vacuum-capable (`canBeVacuumBurnt=false`, `canFlyInVacuum=true`,
  `VacuumResistance 1`) — resolving the vacuum ❓ too: `RaceProps` already
  handles it, no per-map special-casing needed.

**❓s below are RESOLVED by the above, kept for the historical record:**
~~whether the donor mynock race def tolerates a patch~~ — moot, `RSW_Mynock`
is our own clone (owner ruling 3, below). ~~whether vacuum movement needs
special-casing~~ — resolved no, `VacuumResistance 1` on the race handles it
with zero new code.

<details>
<summary>Original draft (2026-09-11), superseded by the shipped code above — kept for provenance only</summary>

**Player experience.** Park the gravship in the Scarlands and mynocks start
drifting toward the hull. Any still aboard at launch ride home for free — then
multiply below decks, gnawing conduits dead, stripping floor panels, eating the
lights out one by one, until the colonists sweep the ship compartment by
compartment and shoot them out. The biome follows you home.

**Engine route — four pieces, in order of the loop:**

- **Board (S).** VERIFIED: `Gravship.ShouldBringOnGravship` carries **any**
  Thing standing on a ship cell at launch whose def has
  `bringAlongOnGravship` — and `ThingDef.cs:167` defaults it to `true`. A wild
  mynock standing on substructure when the engine fires travels with the ship;
  the carry itself costs **zero C#**. The only new code is attraction:
  `RM_JobGiver_SeekSubstructure` (a `ThinkNode_JobGiver`, same shape as the
  donor catalog's `JobGiver_Mine`) that paths the pawn toward the nearest cell
  where `map.terrainGrid.FoundationAt(c).IsSubstructure` (VERIFIED:
  `TerrainDef.IsSubstructure`, `SubstructureGrid.cs`). Gate it on
  `map.Biome == Scarlands` so mynocks elsewhere behave normally.
- **Breed (S).** Vanilla hives schedule breeding via `CompSpawnerPawn` /
  `CompProperties_SpawnerPawn` (VERIFIED: `pawnSpawnIntervalDays` default
  0.85–1.15, `maxSpawnedPawnsPoints`, `spawnablePawnKinds`). **Not reusable
  as-is**, stated reason: VERIFIED `CompSpawnerPawn.TrySpawnPawn` always joins
  spawned pawns to a Lord built by `CreateNewLord` via
  `Activator.CreateInstance(lordJobType, SpawnedPawnParams)` — a lord would
  own the mynocks' AI and fight the gnaw think tree, and the comp's parent
  semantics are building-shaped. New comp **`RM_CompVerminBreeder`**
  (`ThingComp` on the race): each interval, count pawns of this kind on the
  same map standing on substructure (or on the Scarlands map at large); below
  cap, spawn one adjacent, lord-free. Borrows `CompSpawnerPawn`'s
  interval/points fields verbatim, drops the lord.
- **Eat (M).** The meat of the kit: `RM_JobGiver_GnawShipSystems` +
  `RM_JobDriver_Gnaw`. Target set is data-driven via a `DefModExtension` on
  the race: buildings by defName list (VERIFIED `ThingDef PowerConduit`
  exists), buildings by comp (`CompGlower` — VERIFIED class — covers every
  lamp without a denylist), and floor terrains by list. Buildings: gnaw toil
  applies bite damage per interval until destroyed, feeding
  `pawn.needs.food` per bite. Floors: VERIFIED
  `TerrainGrid.RemoveTopLayer(c)` (+ `CanRemoveTopLayerAt`) strips the laid
  floor and leaves the substructure foundation intact — exactly "eats the
  flooring, not the hull."
- **Hunt out (S).** Mynocks stay wild pawns, so vanilla hunting/drafted
  shooting already works; the infestation ends when the count hits zero and
  `RM_CompVerminBreeder` naturally stops. New code: one `Alert` subclass
  (`RM_Alert_ShipVermin`, "mynocks aboard: N") plus a one-shot
  `Messages.Message` on first boarding.

**Reuse:** none of RC1–RC6 fits (this is jobs/AI, not hazards) — new comps
justified above, each with its vanilla donor named.

**INVENTED parameters (owner tunes):** boarding MTB while parked (~1 mynock/day
drawn to the hull); breed interval 1.5 days per mynock; population cap 12 per
map; bite damage 8 HP/toil-cycle; nutrition 0.2/bite.

**v1:** board + breed + eat conduits/lights + floor-strip + alert + hunt-out.
**Deferred:** mynock nests as placeable Things, damage-sparks fleck work,
external-hull clinging visuals, mynock-vs-vacuum rules.

**Effort: M** overall (the Gnaw driver is the only M piece; the rest are S).

</details>

---

## 2. The Scarlands mark (hediff — the mind's price)

**Player experience.** Every colonist who walks the Scarlands accumulates the
mark: a mood shadow and bad nights that deepen the longer they stay. It fades
after leaving — but never all the way. A marked pawn is marked for life; the
Jawa were right.

**Engine route.** One `HediffDef` (`RUT_ScarlandsMark`), severity-staged,
**almost entirely XML on top of ruled comp RC4:**

- **Application — RESOLVED, both halves already exist, zero RC4 changes
  needed (SCARLANDS_MECHANICS_2, 2026-09-14).** `EnvironmentalWeatherExtension`
  already carries `hediffToApply`/`hediffSeverityPerInterval` AND
  `carrierHediff`/`carrierHediffSeverity` — added by `MIASMA_MECHANICS_1`'s
  M4 build (after this section was first drafted), which is exactly the
  "extend RC4 with two fields" this section originally asked for. A
  Scarlands mark hediff instance rides `carrierHediff`, matching the
  pattern `RUT_MiasmaExposure` already uses. **Attachment route also
  RESOLVED, and a live shipped example exists to copy**: no `MapComponent`
  is needed at all — `RUT_MiasmaWeatherLock.xml`
  (`src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/`) attaches its
  permanent `GameCondition_EnvironmentalWeather` instance purely via
  `<canBePermanent>true</canBePermanent>` listed in the biome's own
  `<biomeMapConditions>` (`BiomeConditionMapComponent.MapGenerated ->
  GameConditionMaker.MakeConditionPermanent`, decompile-confirmed by that
  pass) — `RUT_ScarlandsMarkLock` copies that file's shape onto
  `RUT_Scarlands.xml`'s own `biomeMapConditions`, pure XML.
- **Mood:** vanilla `ThoughtWorker_Hediff` (VERIFIED class) — a `ThoughtDef`
  keyed to the hediff, stage per severity band. Zero new C#.
- **Nightmares:** vanilla `HediffStage.mentalStateGivers` (VERIFIED:
  `Hediff.cs:463` rolls them every 60 ticks when not already in a state) — the
  upper stages carry a low-MTB `Wander_Sad`/`Berserk`-family giver as "bad
  nights." Zero new C#.
- **Never fully fades — BUILT (SCARLANDS_MECHANICS_2, 2026-09-14):**
  `severityPerDay` negative off-map with a floor — vanilla severity math has
  no floor concept, so the one line of new C# here is `RM_HediffComp_SeverityFloor`
  (+ `HediffCompProperties_SeverityFloor`,
  `src/RimMandrake/EnvironmentalHazards/Source/`), a `HediffComp` clamping
  severity at a configured minimum once `floorTriggerThreshold` was ever
  crossed. Compiles clean, 0 warnings/0 errors; not yet wired onto
  `RUT_ScarlandsMark` (that HediffDef is content, owed to the full build).

**Reuse:** RC4 (extended, 2 fields). New C#: `RM_HediffComp_SeverityFloor`
only.

**INVENTED parameters:** severity +0.2/day on-map; −0.1/day off-map; floor 0.25
once severity ever exceeded 0.5; stage bands 0.25/0.5/0.75 (mood −2/−4/−6,
nightmares from 0.5 up).

**v1:** hediff + mood + nightmares + floor. **Deferred:** trait interactions
(psychopath shrugging the mark), the mark as a social conversation topic,
scars-of-the-mind art overlay.

**STAGED-LORE COUPLING:** the mark's `description` is player-facing text under
the sheet's §6 ban — it ships in §P register only. When the reveal ladder
climbs, the hediff description deepens via **`STAGED_LORE_BUILD_1`'s live
def-description swaps** (Scarlands GM ladder is its first consumer, owner GO
2026-09-11). Do not build a second swap mechanism here; this kit just keeps
the def's text staged-lore-addressable.

**Effort: S.**

---

## 3. Plated-grazer scaria onset ("the madness inevitably comes")

**Player experience.** The armored grazers ignore you — placid, unkillable-
looking, munching crust. Then, days later, one of them snaps into a permanent
killing rage, exactly as the Jawa said it would. Every one of them, eventually.

**Engine route.** The biome already does half of this: VERIFIED
`Scarlands.xml` ships `wildAnimalScariaChance 0.5`, and
`WildAnimalSpawner.SpawnRandomWildAnimalAt` adds `HediffDefOf.Scaria` at spawn
on that roll. But VERIFIED `Hediff_Scaria.TickInterval` **only auto-starts the
rage for humanlikes and FACTIONED animals** — a wild scaria animal stays calm
forever unless harmed (+0.5 revenge chance), then dies 5 days
(`300000` ticks) after rage begins. "Always succumbs in the end" is therefore
NOT vanilla behavior and is the gap this mechanic fills:

- **`RUT_ScariaIncubation` HediffDef — pure XML.** `severityPerDay` climbs; the
  final stage carries `mentalStateGivers` → `ManhunterPermanent` (VERIFIED:
  stage givers fire via `Hediff.cs:463`; `MentalStateDefOf.ManhunterPermanent`
  is what `Hediff_Scaria` itself checks for animals). Once raging, vanilla
  `Hediff_Scaria`'s own 5-day death clock takes over — we add the fuse,
  vanilla burns it.
- **Arming — reuse ruled comp RC5's `RM_GameCondition_ArmLatentHazard`**
  ("add hediff X to every animal on the map periodically", data-driven —
  exactly its donor's `GameCondition_ExplodingAnimals` shape). Configure it to
  apply `RUT_ScariaIncubation` to pawns of the grazer kind that already carry
  `Scaria`. **BUILT (SCARLANDS_MECHANICS_2, 2026-09-14):** the
  `pawnKindFilter`/`requiredHediff` gate (2 fields) on
  `ArmLatentHazardExtension`, wired into `GameCondition_ArmLatentHazard.
  Eligible()` — both optional and additive to the existing `targets`/
  `affects` gates. Compiles clean, 0 warnings/0 errors.

**Reuse:** RC5's arming condition (extended, 2 fields, shipped). New C#:
none further — `RUT_ScariaIncubation` itself is pure XML, owed to the full
build.

**INVENTED parameters:** incubation 4–12 days (severity 0.1–0.25/day,
randomized per pawn); final-stage giver MTB 0.5 days.

**v1:** incubation + inevitable manhunter flip on wild grazers. **Deferred:**
herd sympathy (one flip agitating neighbors), pre-rage tells (twitch fleck,
inspect-string hint), the "worst possible combination" armor/rage stat tuning
(that's the roster pass's creature def, not this kit).

**Owner-card interplay:** vanilla scaria animals can't be tamed, and a
FACTIONED animal with Scaria rages *immediately* (verified above) — so a
"tame the calm one" play self-destructs the moment taming succeeds. Whether
that is the intended cruelty or needs softening is an owner call, not an
engine constraint.

**Effort: S.**

---

## 4. Sentinel defend-only AI bounds (hard ban §6)

**Player experience.** The Forgotten Sentinels hold their ground — old
strongpoints, grave-wards, repair alcoves. Attack them and they fight like
mechanoids; retreat past their lines and they stop, turn, and walk back to
their posts. They never raid, never pursue, never explain.

**Density (owner, legends sitting 2026-09-11)**: SPARSE. The battle-signs and
battlement structures are the ubiquitous dressing; standing warriors are
uncommon — most strongpoints are bones, the manned one is the exception. Lore
alignment: the repair alcove reads as SELF-REPAIR — surface Sentinels are the
Cathedral's lost, self-mending, slowly devolving units, not a garrison being
restocked (`mindstone_arc_legends.md` §Canon corrections). The spawner comp
below is the alcove rebuilding its own few wards at interval, never a
production line — keep `spawnablePawnKinds` counts/points cap at ward scale.

**Engine route.** The sheet's ban is stricter than any vanilla defend lord:

- VERIFIED `LordJob_MechanoidsDefend.CreateGraph` **leaks into
  `LordToil_AssaultColony`** even with `canAssaultColony: false` — transition
  on `TriggerSignalType.MechClusterDefeated`, and (when `!isMechCluster`) on
  `Trigger_AnyThingDamageTaken(things, 1f)`, i.e. destroy the defended thing
  and the "defenders" assault the colony. Using it as-is would violate ban §6.
- VERIFIED `LordJob_DefendPoint` (Verse.AI.Group) is the pure shape — its
  graph is a single `LordToil_DefendPoint`, nothing else — but it lacks the
  `SpawnedPawnParams` ctor that `CompSpawnerPawn.CreateNewLord` instantiates
  lords through (VERIFIED `Activator.CreateInstance(lordJobType,
  SpawnedPawnParams)`), so spawner-driven Sentinel structures can't use it.

**BUILT (SCARLANDS_MECHANICS_2, 2026-09-14):** `RM_LordJob_DefendPerimeter` +
`RM_LordToil_DefendPerimeter`
(`src/RimMandrake/EnvironmentalHazards/Source/RM_LordJob_DefendPerimeter.cs`):
(a) a `SpawnedPawnParams` ctor, (b) never-flee (`AddFleeToil => false`
override), (c) no exit, no assault, ever — a single-toil `CreateGraph` with
no signal handler wired to anything, so there is nothing for a later edit to
accidentally route into an assault toil. Chase bounding: **the ❓ this
section carried is RESOLVED — `LordToil_DefendPoint.UpdateAllDuties()`
(decompile, `Verse.AI.Group/LordToil_DefendPoint.cs`) hardcodes
`new PawnDuty(DutyDefOf.Defend, ...)` directly, no override seam.** The
~10-line subclassed-toil fallback this section already anticipated is what
shipped: `RM_LordToil_DefendPerimeter` overrides `UpdateAllDuties()` to
assign a caller-supplied `DutyDef` instead (defaulting to
`DutyDefOf.Defend` when none given, so the class is a strict superset of
vanilla behavior — never a change by omission). `RUT_SentinelDefend`
(the tightened-radius `DutyDef` clone this section still calls for) is
passed in by whoever spawns the lord — the RM_ class stays content-blind.
Compiles clean, 0 warnings/0 errors; `RUT_SentinelDefend` itself and the
Sentinel PawnKindDef/spawner-building content are pure XML, owed to the
full build.

Sentinel spawning rides existing vanilla plumbing: repair alcoves / grave-wards
as buildings carrying vanilla `CompSpawnerPawn` with
`lordJob = RM_LordJob_DefendPerimeter` — VERIFIED that comp is fully
def-driven (`spawnablePawnKinds`, `defendRadius`, interval, points cap).

**Reuse:** vanilla `CompSpawnerPawn` (as designed); no RC comp applies. New
C#: `RM_LordJob_DefendPerimeter` + `RM_LordToil_DefendPerimeter` (shipped
this pass).

**Parameters (RULED 2026-09-11, owner: "Double them, then accept"):** defend
radius 80, wander radius 24, acquire/keep radii 72/80; spawner points cap per
site still INVENTED. Same ruling allows local reprisal: Sentinels may attack
their structure's destroyer while in range (never the colony) — see the
Owner rulings section.

**v1:** the lord + duty + spawner wiring. **Deferred:** patrol *routes* (multi-
point walks between grave-wards — needs a custom LordToil rotation, M),
repair-alcove healing behavior, Sentinel "no sound" audio suppression.

**STAGED-LORE COUPLING:** Sentinel kind/desc text is §P register
("Forgotten Sentinels", no §GM truth); ladder stage 2 deepens it via
`STAGED_LORE_BUILD_1` description swaps — nothing in this kit.

**Effort: S** (M if patrol routes pulled into v1 — recommend not).

---

## 5. Pre-sprung danger dressing ("all already opened and destroyed")

**Player experience.** Every ancient danger you find is already sprung: vaults
cracked open, mech clusters slagged in place, horrors long spent. The dread
inverts — not "what's inside" but "what did this, and where did it go." (It
tells the §GM story without saying a word: *this is what all that was for.*)

**Engine route — content-heavy, C#-light.** The vanilla vocabulary is all
present (VERIFIED: `PrefabDef`, `GenStepDef AncientMechs`,
`LayoutRoomDef`/`SketchResolverDef AncientMechGestatorRoom`,
`AncientMechDropBeacon` etc. — the Odyssey Scarlands donor already runs ruins
layouts and crater gen-steps, kept whole per the sheet's donor inventory):

- **v1 = prefab/layout content**: `RUT_` PrefabDefs composing *wreck-state*
  things — breached vault walls (spawn walls with a gap, no intact door),
  destroyed mech shells, scorch filth, opened caskets — scattered by a
  GenStep in the biome's map generation. No live threats inside; loot per §6
  ban 4 (stripped surfaces, sealed prizes elsewhere).
- **RESOLVED YES (SCARLANDS_MECHANICS_2, 2026-09-14): `RUT_GenStep_SprungDanger`
  is not needed, the mechanic is zero C#.** `PrefabThingData`
  (decompile, `RimWorld/PrefabThingData.cs` — the per-entry payload
  `PrefabDef.things` is a list of) carries a plain `public int hp` field,
  read straight off the XML via `XmlHelper.ParseElements`. Pre-damaged/
  opened dressing is fully declarative: a `PrefabDef` entry's `<hp>` sets
  the spawned thing's hit points directly. §5 ships entirely as `RUT_`
  PrefabDef content + a scatter GenStep, owed to the full build.

This is map generation for a biome, not planet worldgen — the worldgen ban
(`CLAUDE.md`) does not apply; the frozen world already fixes where Scarlands
tiles are.

**Reuse:** vanilla gen-step/prefab plumbing; no RC comp applies.

**INVENTED parameters:** dressing density (2–4 sprung sites per map),
wreck-loot table (slag, steel scraps, nothing sealed).

**v1:** wreck prefabs + scatter. **Deferred:** the Last Line's *directional*
crater strings (readable battle vector — wants bespoke placement logic, M),
the bastion dungeon itself (its own item — it holds the ladder's final record
and is quest content, not dressing).

**Effort: S** (possibly zero-C#).

---

## Build order

1. **RC extensions first** (they gate two mechanics and belong to
   `ALPHA_MECHANICS_KIT_1`'s mod): RC4 `hediffToApply`/`severityPerInterval`;
   RC5 `pawnKindFilter`/`requiredHediff`. Small, reviewable, reused beyond
   this biome.
2. **Scaria onset** (§3) — pure XML on top of step 1; fastest live proof of
   the kit on a quicktest map.
3. **Scarlands mark** (§2) — RC4 instance + `RM_HediffComp_SeverityFloor` +
   thought/stage XML.
4. **Sentinel lord** (§4) — `RM_LordJob_DefendPerimeter` + DutyDef clone +
   spawner buildings; provable on a quicktest map without the biome.
5. **Mynock infestation** (§1) — largest new-C# surface (seek, breed, gnaw,
   alert); needs a gravship-on-Scarlands test loop, so it goes last, after
   the cheap wins bank.
6. **Pre-sprung dressing** (§5) — content pass; parallelizable with 4–5 once
   the ❓ PrefabDef expressiveness check lands.

Verification per step: quicktest map + bridge (`rimworld-debug-testing`),
never a cold load; the mynock launch-carry claim gets one live gravship
launch test before the boarding JobGiver is tuned.

## Owner rulings (card sitting, 2026-09-11 — all seven cards ruled)

1. **Mod placement — RULED: a separate vermin/behaviors mod, named
   "ShipVermin".** Owner-verbatim: 'gather all the "ship infesting" critters
   together into a single mod "ShipVermin" that allows the mechanics,
   creatures, and future cool ideas to emerge. Some are cute, some are
   hideous, some live inside, some can live outside in vaccuum (the mynock
   for example).' The vermin/AI classes and the mynock land there — NOT in
   `mandrake.rm.environmentalhazards`. Filed as `SHIP_VERMIN_MOD_1`. The
   non-vermin RM_ classes of this kit are unaffected.
2. **Mynock pressure — RULED: "Nuisance unless there are many"** (owner-
   verbatim). Individual pressure low; meanness scales with population. The
   drafted knobs are tuned to that curve, not to a flat tax.
3. **Mynock race — RULED: ship our own `RSW_Mynock` clone** per the
   donor-retirement pattern; no in-place donor patch.
4. **Mark permanence — RULED: both.** A small permanent mood hit AND
   nightmares while on Scarlands maps; leaving the map ends the nightmares,
   never the mark.
5. **Grazer taming cruelty — RULED: keep the trap as-is.** Vanilla scaria
   rage and the taming ban stand; scaria carriers are a lesson, not a pet.
   Does NOT change the mynock-pets register elsewhere.
6. **Sentinel bounds — RULED: local reprisal allowed; radii doubled.**
   (a) Sentinels MAY attack the destroyer of their structure while in range,
   but NEVER march on the colony — the vanilla assault-switch leak
   (`LordToil_AssaultColony` transition) is still deleted by design;
   `RM_LordJob_DefendPerimeter` stands, with reprisal bounded by the chase
   radii. (b) The INVENTED radii are doubled then accepted: **acquire 72 /
   keep 80 / wander 24 / defend 80** (supersedes §4's drafted 36/40/12/40).
   Test: destroy a grave-ward in a quicktest — survivors strike the wrecker
   in range, then walk back; no base assault.
7. **Dressing — RULED: crater-string promoted to v1**; density as drafted.
   The Last Line reads as a directional battle vector in the first playable.
