# WEBWORK_MECHANICS_1 — C# mechanics kit spec (DRAFT for owner review)

Engine mapping for the seven mechanics fixed in
`design/Jawa/worldbuilding/biomes/the_webwork.md` (frozen sheet,
`BIOME_FREEZE_FABLE_REVIEW_1`). **This spec invents no lore** — every player-facing
behavior below is the sheet's, restated only far enough to name the engine route.
All engine class/def names verified live via RimSage against the vanilla+DLC source
and def index on 2026-09-11 unless marked ❓.

Constraints honored:
- **Ruled-comp reuse**: the six RM_ generic comps ruled IN 2026-09-11
  (`design/Jawa/worldbuilding/alpha_family_source_review.md` §4, build item
  `ALPHA_MECHANICS_KIT_1`) are used where they fit; every new C# class states why
  no ruled comp covers it.
- **Naming**: RM_ for mechanisms (no Star Wars/Utinni specificity), RUT_ for
  per-biome content defs, per `design/NAMING_SCHEME_PLAN.md`. One tier question is
  carded (card 6).
- **Shokkweave sole-source** (`the_webwork.md` §6 ban 4, §7, Owed
  `SHOKKWEAVE_SOLE_SOURCE_1`): nothing in this kit creates, yields, or renames
  Shokkweave/hyperweave. All harvest routes, the rename patch, and trader
  stripping belong to `SHOKKWEAVE_SOLE_SOURCE_1` and are NOT respecified here.
  One boundary interaction is carded (card 4).

---

## 0. REQUIRED VERDICT — the UV-sensitivity def

**FOUND — with a load-bearing caveat.**

- The def the owner's pointer names exists: **`GeneDef UVSensitivity_Intense`**
  (label "intense UV sensitivity") and its sibling **`UVSensitivity_Mild`**, parent
  `UVSensitivityBase`, Biotech, `Defs/Biotech/GeneDefs/GeneDefs_Spectrum.xml`.
  Its mechanics, read from the def and source:
  - `conditionalStatAffecters` → `ConditionalStatAffecter_InSunlight`
    (Verse; `Applies` = Biotech active AND `Thing.Position.InSunlight(map)`),
    MoveSpeed ×0.8.
  - `dislikesSunlight = true` → `Pawn_GeneTracker.EnjoysSunlight`, read by
    `JoyGiver` (no outdoor joy) and `RCellFinder` (wander cells avoid sunlight).
  - Mood: `ThoughtDef SunlightSensitivity_Major` via `ThoughtWorker_InSunlight`.
- ⚠️ **The gene cannot ride the Wyyyschokk.** `pawn.genes` is created only inside
  `if (pawn.RaceProps.Humanlike)` (`PawnComponentsUtility.CreateInitialComponents`),
  and `StatWorker` reads `conditionalStatAffecters` only from **genes and
  precepts** — there is no HediffDef carrier for it. An animal race gets none of
  the gene's machinery.
- **The animal-native precedent is also vanilla and verified**: Anomaly's
  **`HediffDef LightExposure`** (`hediffClass Verse.Hediff_LightExposure`,
  `HediffDefOf.LightExposure`) — the mechanism that makes Noctols helpless in
  light. Severity +0.4/s while `glowGrid.PsychGlowAt(pos) != PsychGlow.Dark`,
  −0.25/s in dark; staged MoveSpeed ×0.9/×0.8/×0.5 and MeleeCooldownFactor up to
  ×2. `Hediff_LightExposure.PostAdd` self-removes without Anomaly
  (`ModLister.CheckAnomaly`) — Anomaly is in the owner's active DLC set.
- **Kit resolution** (§4 below): reimplement the *sunlight* variant of that hediff
  shape at RM_ tier, using the same `InSunlight` primitive the UV gene uses
  (`SanguophageUtility.InSunlight`: unroofed AND `skyManager.CurSkyGlow > 0.1`),
  so overcast/night genuinely weakens the moat as the sheet demands. This honors
  the owner's pointer — same mechanism, same primitives — moved to a carrier an
  animal can hold. The sheet itself says "verify the exact def at build, never
  guess it"; this is that verification.

---

## Verified engine anchors (shared by the mechanics below)

| Claim | Where verified |
|---|---|
| `pawn.genes` Humanlike-only | `RimWorld/PawnComponentsUtility.cs` (Humanlike block) |
| `ConditionalStatAffecter_InSunlight` gene/precept-only | `RimWorld/StatWorker.cs`, `Verse/GeneDef.cs`, `RimWorld/PreceptDef.cs` |
| `SanguophageUtility.InSunlight(IntVec3, Map)` = in-bounds, unroofed, `CurSkyGlow > 0.1` | `RimWorld/SanguophageUtility.cs:105` |
| `Hediff_LightExposure` severity/decay behavior | `Verse/Hediff_LightExposure.cs` |
| `CompCanBeDormant` / `CompWakeUpDormant` (proximity wake, LoS radius scan via `wakeUpTargetingParams`, signal-linked group wake) | `RimWorld/CompCanBeDormant.cs`, `CompWakeUpDormant.cs` (`TickRareWorker`) |
| `TunnelHiveSpawner : GroundSpawner`, `PawnGroundSpawner : GroundSpawner, IThingHolder` (timer-based under-ground burst spawn) | `RimWorld/TunnelHiveSpawner.cs`, `PawnGroundSpawner.cs` |
| `HediffComp_Invisibility` exists (Sightstealer-style) | `Verse/HediffComp_Invisibility.cs` |
| `DamageDef.additionalHediffs` (`List<DamageDefAdditionalHediff>`) and `DamageDef.hediff` | `Verse/DamageDef.cs:71,93` |
| `HediffComp_TendDuration.severityPerDayTended`, `HediffComp_SeverityPerDay` | `Verse/HediffCompProperties_TendDuration.cs`, `HediffComp_SeverityPerDay.cs` |
| `PawnCapacityModifier.setMax` / `postFactor` on hediff stages (downed-by-capacity route) | `Verse/PawnCapacityModifier.cs`, `PawnCapacityUtility.cs` |
| `PawnKindDef.startingHediffs` applied at generation | `Verse/PawnKindDef.cs:253`, `PawnGenerator.cs:1269` |
| Manhunter-style target pick = `AttackTargetFinder.BestAttackTarget(searcher, flags, validator, …)` | `Verse/AI/AttackTargetFinder.cs:32`, `RimWorld/JobGiver_Manhunter.FindPawnTarget` |
| Droid predicate = `RaceProps.FleshType == RSW_DW_FleshType_Droid` (`DroidFormatTierUtility.IsDroid`) | `src/RimStarWars/Droidworks/Source/Droidworks/DroidFormatTier.cs:49`, `Defs/Races_Base.xml` |
| Donor biome def `AB_FeraliskInfestedJungle` (Alpha Biomes) is the biome the kit gates on | `the_webwork.md` header (sheet-recorded); ❓ re-confirm defName against live dump at build |
| MapComponents: every subclass is constructed per-map; gate all behavior on `map.Biome` / neighbor check | standard engine behavior (`Map.ConstructComponents`) — ❓ cheap to confirm at build, not re-read this pass |

---

## The mechanics

### 1. Web-sense felt-marks + pack convergence — `RM_MapComponent_SenseWeb`

**Player experience** (sheet §4 web-sense, §5). Touching web anywhere is being
*felt* everywhere nearby: a pawn who crosses silk gets a visible "Felt" mark, and
Wyyyschokk begin converging on them — from well beyond sight range, tracking for
"over a kilometer" (map-scale: from anywhere on the map). The quiet stops being
neutral.

**Engine route.** New `RM_MapComponent_SenseWeb` (mechanism is generic: "a network
of registered Things senses intruders and marks them for a species"):
- Web Things (RUT_ web/anchor/gutter ThingDefs, from the roster item) carry a tiny
  marker comp `RM_CompSenseWebNode` that registers/deregisters their cells with
  the component (spawn/despawn), keeping a cell `HashSet`/bitmap.
- On a scan interval, pawns standing in registered cells (hostile to the web's
  "faction-of-none" — in practice: any non-Wyyyschokk pawn) receive
  **`RUT_Webwork_FeltMark`** (HediffDef, XML): visible, severity decays over
  ❓INVENTED ~1 day via `HediffComp_SeverityPerDay`; no stats, pure targeting data
  + player dread.
- Convergence: **`RM_JobGiver_SenseWebConverge`** (`ThinkNode_JobGiver`) in the
  Wyyyschokk's custom ThinkTreeDef queries the component for marked pawns and
  paths to/attacks the nearest, `JobGiver_Manhunter`-style
  (`AttackTargetFinder.BestAttackTarget` with a felt-mark validator). Because we
  author the race's think tree, **no Harmony is needed**. Pack behavior emerges
  from every spider sharing the same component data; no Lord required for v1.
- Egg-carrier hook (sheet §7 "carrying stolen eggs marks you to every web you
  pass"): the component's mark check also fires on inventory containing
  `RUT_Webwork_Egg` — one `if`, wired now, item lands with the egg-economy item.

**Why no ruled comp**: all six ruled comps are environmental-hazard shaped
(gas/hediff-area/weather/death/ability); none is a sensory-network MapComponent.
**New C#**: `RM_MapComponent_SenseWeb` (M), `RM_CompSenseWebNode` (S, trivial),
`RM_JobGiver_SenseWebConverge` (S). ❓INVENTED: scan interval (~250 ticks), mark
duration, convergence pack size cap. **v1**: all of the above. **Deferred**:
vibration-flavor motes on the line; Lord-driven coordinated multi-prong assaults.
**Effort: M.**

### 2. Concealed-burst ambush — vanilla dormancy, XML-first

**Player experience** (sheet §1, §4, §6 ban 6). A shadow, seconds before it lands.
Ambusher spiders are not on your threat readout until something is close enough —
then they burst from underbrush or underground, already adjacent. No dense-canopy
cell is ever guaranteed safe.

**Engine route.** Vanilla mechanism, XML-attachable, proven on mech clusters:
- Ambusher PawnKinds spawn dormant with **`CompCanBeDormant` +
  `CompWakeUpDormant`** on the race/kind: `TickRareWorker` scans
  `wakeUpCheckRadius` with line-of-sight and `wakeUpTargetingParams`, and
  `Activate` signal-wakes the linked group — "one wakes, the nest wakes" is
  native. ❓INVENTED: radius (~7).
- Underground burst variant: spawn a **`PawnGroundSpawner`** (Anomaly;
  timer-based `GroundSpawner` with dust motes) holding ambushers, placed by the
  ambush incident/mapgen. Timer-based, not proximity-based — v1 uses it only for
  incident arrivals; a proximity-triggered ground burst would need a small
  trigger Thing that spawns the `PawnGroundSpawner` on wake (`RM_CompBurstOnWake`,
  S, deferred).
- Concealment visual: dormant pawns using a web-lump graphic ❓ (render-swap while
  dormant needs checking at build; fallback: hide under a destroyable
  `RUT_Webwork_Lump` Thing). `HediffComp_Invisibility` exists as the heavier
  alternative but reads as *magic* invisibility — not used in v1 (the sheet wants
  concealment, not Sightstealers).

**Why no ruled comp**: dormancy/wake is already vanilla; nothing to build.
**New C#**: none in v1. **v1**: dormant ambushers + group wake + incident ground
spawns. **Deferred**: `RM_CompBurstOnWake` proximity ground-burst; dormant
graphic swap. **Effort: S** (v1 XML) — deferred polish M.

### 3. Shokk-bound hediff — XML only

**Player experience** (sheet §4 mouth-loom). The ranged spit does not wound — it
binds. A hit pawn is near-immobilized for days, helpless, not dying; a doctor can
free them. The spider comes back for bound prey. Terror is the mechanic: rescue
under converging spiders.

**Engine route.** Zero C#:
- **`RUT_ShokkBound`** HediffDef: stages with `capMods` on `Moving`
  (`setMax` ≈ 0.10 at full severity — below the vanilla downed threshold, so the
  pawn goes down helpless, exactly "not damage — helplessness"); lighter early
  stage (Moving `postFactor` ❓~0.3) so a graze slows rather than drops.
  `HediffComp_SeverityPerDay` ❓ −0.2/day untended (≈ "days"), plus
  `HediffComp_TendDuration` with `severityPerDayTended` strongly negative —
  "unless attended medically" is a verified vanilla field, same shape vanilla
  infections use in reverse.
- Application: the spit verb's projectile damage uses a
  **`RUT_Damage_ShokkSpit` DamageDef** with **`additionalHediffs`** →
  `RUT_ShokkBound` (verified `DamageDef` fields). Tiny/zero direct damage.
- **Optional ruled-comp reuse**: if the owner wants a cooldown-gated "web volley"
  distinct from the basic attack verb, **`RM_Ability_TargetedHediffAffliction`**
  (ruled comp 6) already does "add hediff X on cast" — the def would be one
  RUT_ AbilityDef. Not required for v1.
- Commandable-adhesion (sheet Owed list; not in this item's seven): v1 expresses
  it as flavor + the hediff's tend-resistance; a mechanical
  slick-vs-locked web state is **deferred to the roster/web-Things work**, noted
  here so it is not lost.

**Sole-source guard**: the projectile, damage def, and hediff yield nothing;
butcher/harvest yields stay in `SHOKKWEAVE_SOLE_SOURCE_1`.
**New C#**: none. ❓INVENTED: all tuning numbers above. **v1**: hediff + damage
route on the basic spit. **Deferred**: ability-based volley. **Effort: S.**

### 4. Light-moat — `RM_Hediff_SunScald` (the verified UV mechanism, animal carrier)

**Player experience** (sheet §3, §7b). Owners are helpless in direct sunlight: a
cut, burned, kept-open ring of ground is a fortress wall made of light. Overcast
skies and nightfall genuinely weaken it; regrowth and an untrimmed margin erode
it. Fire is architecture.

**Engine route.** Per §0: the gene is Humanlike-only, so the kit ships the same
mechanism on an animal-legal carrier:
- **`RM_Hediff_SunScald`** (Hediff subclass, ~30 lines, mirror of the verified
  `Hediff_LightExposure` tick shape but keyed to
  `SanguophageUtility.InSunlight` — unroofed + `CurSkyGlow > 0.1` — the same
  primitive `ConditionalStatAffecter_InSunlight` uses, so lamps/torches do NOT
  scald and night/overcast genuinely opens the moat, both sheet-required).
  Severity climbs fast in sun, decays in shade ❓ (rates invented; start near
  LightExposure's 0.4/−0.25 per sec and tune hotter — "helpless", not "annoyed").
- **`RUT_Webwork_SunScald`** HediffDef (XML): staged like `LightExposure`
  (verified stages pattern) but ending harder — top stage Moving `setMax` low
  enough to down ❓, plus pain. A downed spider in your moat is loot, not siege.
- Attached via **`PawnKindDef.startingHediffs`** (verified vanilla,
  `PawnGenerator` applies at generation) — no comp, no HediffGiver needed.
- Behavioral aversion ("physically cannot cross open sunlit ground"): the kit's
  targeting JobGivers (§1, §7) refuse targets standing in `InSunlight` cells
  ❓ (validator clause) — spiders stall at the light line, which IS the moat
  fantasy. Mood/joy-style aversion (`dislikesSunlight`) is gene machinery and
  does not apply.
- **Ruled-comp interaction, deliberate NON-use**:
  `RM_HarmonyPatch_BiomeGlowMultiplier` (ruled comp 3) was considered for the
  "dim green gloom" and **rejected for this biome**: `CurCelestialSunGlow` is
  map-wide, so it would dim the clearings too and blunt the light-moat's own
  instrument. Gloom-under-canopy stays art/roofing, not glow math.

**Why new C#**: no ruled comp touches sunlight-keyed severity; the only vanilla
carrier of the *sun* test is a gene (Humanlike-only) and the only animal carrier
(`Hediff_LightExposure`) keys to *any* light including lamps, which would let a
wall-lamp corridor replace the burned ring. **New C#**: `RM_Hediff_SunScald` (S).
**v1**: hediff + startingHediffs + targeting refusal. **Deferred**: true
pathfinding cost for sunlit cells (per-cell path-cost integration is L and not
needed while targeting-refusal holds the line). **Effort: S–M.**

### 5. Beetle anchor-chewing — `RM_JobGiver_ChewAnchors`

**Player experience** (sheet §4b). Anchor-beetles hate the web instinctively:
left alone they chew through anchor lines and slowly undo the network. Lure them
along a route and they cut you a safe corridor — a living tool, not a fighter.

**Engine route.** The §4-review's own precedent (`JobGiver_Mine`, judged "write it
directly, no generalization surface"): **`RM_JobGiver_ChewAnchors`**
(`ThinkNode_JobGiver`, ~30–40 lines) in the beetle's ThinkTreeDef — scan nearby
cells/region for Things whose def carries `RM_ChewableExtension`
(`DefModExtension`, so ANY future mod can mark chewables without touching C#),
issue a melee-attack job against the anchor Thing. Destroying an anchor notifies
`RM_MapComponent_SenseWeb` to deregister its cells (§1) — chewing genuinely blinds
the web locally, which is the corridor.
- Herding v1 = vanilla: beetles are neutral wild animals; players lure with food
  or tame per the roster's wildness settings. No new C# for "herdable".
- Sole-source guard: destroyed-by-beetle web Things drop **nothing** (leavings
  none) — a beetle lawnmower must not become a Shokkweave farm.

**Why no ruled comp**: behavior/job work; the six comps are hazards.
**New C#**: `RM_JobGiver_ChewAnchors` (S), `RM_ChewableExtension` (S, trivial).
❓INVENTED: chew rate = anchor HP vs beetle DPS. **v1**: all. **Deferred**:
mite-trail treasure-map behavior (egg-mites are roster content; their
run-the-silk pathing can ride the SenseWeb registry later). **Effort: S.**

### 6. Margin creep — `RM_MapComponent_FrontCreep` + ruled-comp reuse

**Player experience** (sheet §8 margins). On maps bordering the Webwork, the web
line visibly advances between looks: silk further out, pale flowers tracing new
lines, Webwork flora replacing yours. World map never repaints (frozen map,
sheet-recorded); the dread is map-local.

**Engine route.** New **`RM_MapComponent_FrontCreep`** (generic mechanism: "a
biome's contents advance from a map edge on maps adjacent to that biome"):
- Active only when a neighboring world tile's biome matches a configured
  BiomeDef (world-grid neighbor query; the map itself keeps its own biome — no
  worldgen, no repaint, honoring the no-worldgen ruling).
- On a long interval ❓ (days-scale, invented), advances a front band from the
  corresponding map edge: spawns RUT_ web Things + converts flora.
- **Ruled-comp reuse (firm)**: flora conversion rides **`RM_Gas_Transmuting`**
  (ruled comp 1 family) — the §4/§5 review itself names it "a slow, spreading
  'this ground is being changed' effect… candidate for spread mechanics." The
  creep component seeds transmuting gas puffs along the front; the gas class does
  the species-swap with `Growth` preserved. One mechanism, two biomes' spread
  stories (Greentide's churn can reuse it later, per the review).
- Creep-spawned web registers with `RM_MapComponent_SenseWeb` like any web — the
  advancing line can *feel*, which is the point.
- Sole-source boundary: whether cutting creep-web on a border map is an in-biome
  harvest route is `SHOKKWEAVE_SOLE_SOURCE_1`'s call — **carded (card 4)**, and
  until ruled, creep-web spawns as a no-yield variant.

**New C#**: `RM_MapComponent_FrontCreep` (M). ❓INVENTED: advance rate, band
depth, density. **v1**: front advance + transmuting flora + no-yield web.
**Deferred**: retreat when the player burns the front back (regression logic),
flower-tracing freshness states (roster/art). **Effort: M.**

### 7. Droid-priority targeting — folded into the kit's JobGivers

**Player experience** (sheet §4 🔴). The one terrain where a droid force is a
liability: Wyyyschokk preferentially destroy droids, unexplained. A mixed
column watches its droids die first; the Free Droid Enclaves already know.

**Engine route.** No Harmony, no new mechanic class — a scoring clause in the
kit's own target selection (`RM_JobGiver_SenseWebConverge` §1 and the race's
manhunter-equivalent JobGiver), which we author anyway:
- Target pick is `AttackTargetFinder.BestAttackTarget` with a validator/scorer
  (verified `JobGiver_Manhunter.FindPawnTarget` pattern). Priority: droids first
  within ❓ a generous radius, then normal threat order.
- Droid predicate (verified): `pawn.RaceProps.FleshType` equals the
  **`RSW_DW_FleshType_Droid`** FleshTypeDef (exactly `DroidFormatTierUtility.IsDroid`'s
  test in Droidworks). The kit resolves it **by defName via DefDatabase at
  startup, null-safe** — a soft reference, so the RM_ assembly neither hard-links
  the RSW_ assembly nor breaks when Droidworks is absent. The RM_ mechanism field
  is generic (`priorityFleshTypes` list on a DefModExtension); naming "droid"
  appears only in RUT_/RSW_ XML, keeping the tier grammar clean.

**New C#**: none beyond §1's JobGivers (a scorer clause). ❓INVENTED: priority
weight/radius. **v1**: in. **Deferred**: nothing. **Effort: S** (inside §1's M).

---

## Kit summary

| # | Mechanic | Ruled-comp reuse | New C# | Effort | v1? |
|---|---|---|---|---|---|
| 1 | Web-sense + convergence | — (none fits) | `RM_MapComponent_SenseWeb`, `RM_CompSenseWebNode`, `RM_JobGiver_SenseWebConverge` | M | yes |
| 2 | Concealed-burst ambush | — (vanilla dormancy) | none (v1) | S | yes |
| 3 | Shokk-bound | `RM_Ability_TargetedHediffAffliction` (optional volley) | none | S | yes |
| 4 | Light-moat | `RM_HarmonyPatch_BiomeGlowMultiplier` considered, rejected (reason stated) | `RM_Hediff_SunScald` | S–M | yes |
| 5 | Beetle anchor-chewing | — (review's own "write directly" precedent) | `RM_JobGiver_ChewAnchors`, `RM_ChewableExtension` | S | yes |
| 6 | Margin creep | **`RM_Gas_Transmuting` (firm)** | `RM_MapComponent_FrontCreep` | M | yes |
| 7 | Droid-priority | — (rides #1's JobGivers) | none extra | S | yes |

**Totals**: 7 mechanics · ruled-comp reuse 1 firm + 1 optional (+1 explicit
rejection with reason) · **6 new C# classes** (2 M, 4 S — two of the S are
trivial) · overall **one M-sized FOUNDRY build wave**. All numeric tuning is
❓INVENTED and expects a live-balance pass (quicktest map, not cold loads).

**Proposed home**: the RM_ classes join `ALPHA_MECHANICS_KIT_1`'s proposed mod
(`src/RimMandrake/EnvironmentalHazards/`, packageId
`mandrake.rm.environmentalhazards`, namespace `RimMandrake.EnvironmentalHazards`)
— one assembly for RM_ mechanisms rather than a per-biome DLL (card 5 if the
owner wants it split). RUT_ content defs live with the Webwork's content mod
(roster item's home). Depends on: `ALPHA_MECHANICS_KIT_1` for
`RM_Gas_Transmuting`; the roster item for web/anchor/egg ThingDefs and the
Wyyyschokk/beetle races the ThinkTrees attach to; `SHOKKWEAVE_SOLE_SOURCE_1`
independent (boundary carded).

## Build order

1. **`RM_Hediff_SunScald` + `RUT_Webwork_SunScald` + `RUT_ShokkBound`** — no
   dependencies, XML-heavy, quicktest-provable on any spawned animal. Proves the
   downed-by-capacity and tend-release shapes early.
2. **`RM_MapComponent_SenseWeb` + node comp + placeholder web Thing** — the
   spine; every later piece registers with it.
3. **`RM_JobGiver_SenseWebConverge` + droid-priority scorer + sunlit-target
   refusal** — needs 2 and a stub race ThinkTree; delivers mechanics 1, 7, and
   the behavioral half of 4 in one JobGiver pass.
4. **Ambush XML** (`CompCanBeDormant`/`CompWakeUpDormant` on ambusher kinds;
   `PawnGroundSpawner` incident wiring) — independent after the race exists.
5. **`RM_JobGiver_ChewAnchors` + `RM_ChewableExtension`** — needs 2's
   deregistration hook.
6. **`RM_MapComponent_FrontCreep`** — last; needs `RM_Gas_Transmuting` from
   `ALPHA_MECHANICS_KIT_1` and the web Things, and its sole-source boundary card
   answered (or ships no-yield).

## Owner cards

1. **Light-moat hardness**: should full sun *down* a Wyyyschokk (loot piñata in
   your moat) or only cripple it (MoveSpeed ~×0.3, still crawling for shade)?
   Sheet says "helpless"; downed is the literal reading — confirm before tuning.
2. **Night/overcast moat failure**: v1 makes the moat genuinely OFF at night and
   under heavy overcast (sun-keyed, lamps do nothing — sheet lists overcast as a
   threat). Confirm night assaults are wanted as a core rhythm, since this makes
   the biome markedly harder than the donor's.
3. **Shokk-bound vs. player abuse**: bound pawns are downed-not-dying for days —
   players may deliberately feed a colonist to bait convergence. Accept as
   emergent story, or add a "the spider collects bound prey" behavior (drag to
   nest — M extra, deferred by default)?
4. **Sole-source boundary** (with `SHOKKWEAVE_SOLE_SOURCE_1`): does cutting
   creep-web on a border map count as an in-biome harvest route? Until ruled,
   creep-web is a no-yield variant.
5. **Assembly home**: RM_ classes into `mandrake.rm.environmentalhazards`
   alongside the six ruled comps (default), or a separate RM_ "creature
   behaviors" assembly since half this kit is JobGiver/MapComponent shaped?
6. **Tier of `RUT_ShokkBound` and the spit damage def**: the Wyyyschokk is canon
   Star Wars fauna (sheet §7 amendment) — if the roster lands the species at
   RSW_ tier, these two defs should be RSW_ and move with it. Named RUT_ here per
   this item's instruction; flag for the roster pass.
7. **Ambusher concealment art**: dormant-state graphic swap vs. a destroyable
   web-lump Thing hiding the pawn — small build difference, visible-to-player
   difference; his eye should pick.
