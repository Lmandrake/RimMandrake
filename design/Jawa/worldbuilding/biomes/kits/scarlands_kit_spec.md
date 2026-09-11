# SCARLANDS_MECHANICS_1 — C# mechanics kit spec (DRAFT)

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

## 1. Mynock ship-infestation (board / breed / eat / hunt-out)

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

**❓ Unverified:** whether the donor (Star Wars Animal Collection) mynock race
def tolerates an XML patch swapping `thinkTreeMain` in place, vs. our shipping
an `RSW_Mynock` clone kind — decide at build, rides the roster re-cast pass
the sheet already owes. ❓ whether pawn movement between substructure rooms
mid-flight (vacuum) needs special-casing on Odyssey space maps.

**Effort: M** overall (the Gnaw driver is the only M piece; the rest are S).

---

## 2. The Scarlands mark (hediff — the mind's price)

**Player experience.** Every colonist who walks the Scarlands accumulates the
mark: a mood shadow and bad nights that deepen the longer they stay. It fades
after leaving — but never all the way. A marked pawn is marked for life; the
Jawa were right.

**Engine route.** One `HediffDef` (`RUT_ScarlandsMark`), severity-staged,
**almost entirely XML on top of ruled comp RC4:**

- **Application:** extend **RC4 `RM_GameCondition_EnvironmentalWeather`** with
  two fields — `hediffToApply` + `severityPerInterval` (a natural sibling of
  its existing damage-per-interval field; flagged in the alpha review §5 as
  the kind of one-field broadening RC4 was built for). A permanent instance of
  it runs on Scarlands maps. Attachment route for "permanent condition on this
  biome's maps": simplest is a tiny `MapComponent` that instantiates the
  condition when `map.Biome == Scarlands` — ❓ verify at build whether an
  Odyssey `TileMutatorDef`/GenStep can attach a permanent `GameCondition`
  without C#, which would delete even that.
- **Mood:** vanilla `ThoughtWorker_Hediff` (VERIFIED class) — a `ThoughtDef`
  keyed to the hediff, stage per severity band. Zero new C#.
- **Nightmares:** vanilla `HediffStage.mentalStateGivers` (VERIFIED:
  `Hediff.cs:463` rolls them every 60 ticks when not already in a state) — the
  upper stages carry a low-MTB `Wander_Sad`/`Berserk`-family giver as "bad
  nights." Zero new C#.
- **Never fully fades:** `severityPerDay` negative off-map with a floor —
  vanilla severity math has no floor concept, so the one line of new C# here
  is a trivial `HediffComp` (`RM_HediffComp_SeverityFloor`, S) clamping
  severity at a minimum once a threshold was ever crossed.

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
  `Scaria`. Needs one small extension: a `pawnKindFilter`/`requiredHediff`
  gate (two fields) so it arms only scaria-positive grazers, not every animal.

**Reuse:** RC5's arming condition (extended, 2 fields). New C#: none.

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

**Player experience.** The Forgotten Sentinels hold their ground — patrol
lines, grave-wards, repair alcoves. Attack them and they fight like mechanoids;
retreat past their lines and they stop, turn, and walk back to their posts.
They never raid, never pursue, never explain.

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

New class **`RM_LordJob_DefendPerimeter`** (S): `LordJob_DefendPoint`'s
single-toil graph plus (a) a `SpawnedPawnParams` ctor, (b) never-flee
(`AddFleeToil => false`), (c) no exit, no assault, ever — ~30 lines, the ban
made structural. Chase bounding is then XML: `LordToil_DefendPoint` assigns
`DutyDefOf.Defend`, whose VERIFIED def carries `JobGiver_AIDefendPoint` with
`targetAcquireRadius 65 / targetKeepRadius 72` — clone it as
`RUT_SentinelDefend` DutyDef with tightened radii so Sentinels drop targets
that leave their lines. ❓ One build-time check owed: that
`LordToil_DefendPoint` accepts a custom DutyDef or that the radii can be
bounded another way (the toil may hardcode `DutyDefOf.Defend`; if so the
subclassed toil is another ~10 lines).

Sentinel spawning rides existing vanilla plumbing: repair alcoves / grave-wards
as buildings carrying vanilla `CompSpawnerPawn` with
`lordJob = RM_LordJob_DefendPerimeter` — VERIFIED that comp is fully
def-driven (`spawnablePawnKinds`, `defendRadius`, interval, points cap).

**Reuse:** vanilla `CompSpawnerPawn` (as designed); no RC comp applies. New
C#: `RM_LordJob_DefendPerimeter` (+ possible toil subclass).

**INVENTED parameters:** defend radius 40, wander radius 12, acquire/keep radii
36/40, spawner points cap per site.

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
- **One small C# piece if needed**: `RUT_GenStep_SprungDanger` (S) — only if
  prefab fields can't express "pre-damaged/opened" (❓ verify at build whether
  `PrefabDef` entries can set hit points / opened states declaratively; if
  yes, this class evaporates and the mechanic is **zero C#**).

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

## Owner cards

1. **Mod placement**: fold this kit's RM_ classes into
   `mandrake.rm.environmentalhazards` (one mechanics mod) vs. a separate
   `mandrake.rm.hullvermin` for the vermin/AI classes.
2. **Mynock pressure knobs**: boarding rate, breed interval/cap, gnaw damage —
   all INVENTED above; how mean should the ship tax feel?
3. **Mynock race**: patch the donor mod's mynock in place vs. ship our own
   `RSW_Mynock` clone kind (interacts with the roster re-cast the sheet owes).
4. **Mark permanence**: the never-fades floor value and what a lifelong mark
   does at rest (small permanent mood hit? nightmares gone once off-map?).
5. **Grazer taming cruelty**: verified vanilla makes a tamed scaria animal
   rage instantly and bans taming scaria carriers — keep the trap as-is, or
   soften for the "mynock pets" register the Jawa culture wants elsewhere?
6. **Sentinel bounds numbers**: defend/wander/acquire radii; and the ruling
   that destroying a Sentinel spawner structure must NOT anger survivors
   beyond their lines (the vanilla leak we're deleting — confirm intended).
7. **Dressing density** and whether the directional crater-string (Last Line
   readable battle vector) is promoted into v1 or stays deferred.
