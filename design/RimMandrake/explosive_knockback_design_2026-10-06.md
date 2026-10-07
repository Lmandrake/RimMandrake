# Explosive Knockback — design pass (2026-10-06)

Status: DESIGN ONLY, nothing built. Seat: BENCH.

## 1. The owner's words

**What I could find, and its limits.** There is no item, ledger event, commit or design doc named
"Explosive Knockback". The proposal exists in three places, and only two of them are his typed words:

1. **His typed ruling, 2026-10-06 ~09:27 PDT** (question card answer, BENCH session `ecebcb6f`, now item
   `FLOWWORKS_PIT_FALL_ONLY_FORCED_1`):
   > *"You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall.
   > Enemies can fall if the pit is concealed or they are forced/blown in."*
2. **A card BENCH put to him, 2026-10-06 12:01 PDT** (same session, last tool call before it ended). The
   wording is OURS, not his: *"Should explosions be able to knock pawns into pits (a new mechanic)?"* with
   options *"Yes, near the edge (Recommended)"*, *"No, forced entry only"*, *"Later, park it"*. **No answer
   is recorded in any transcript** — the session file ends at the card. His answer, if he gave one, was
   not captured.
3. **His typed instruction, 2026-10-06 18:47 PDT** (this session):
   > *"in the background, do a full design pass on the Explosive Knockback mod I proposed today. Then ask
   > GPT for an evaluation of your design. Ask me questions."*

Older owner text the mechanic must honour (PIT_SUPERDEEP_COLLAPSE_1, 2026-09-17, typed):
> *"Covering the pit allows people to fall into it involuntarily (or if they are somehow pushed or blasted
> into it, something that would move them normally against their will like weapon blowback)."*

And the balance paradigm (`design/RimMandrake/balance_paradigm.md`) already lists **knockback** and
**displace (knockback, gravitic)** among the "new effect = new verb" mechanics worth building.

⇒ He then answered eight question cards (§11, 2026-10-06 19:05): everywhere, explosions only, thrown over
sandbags, everything light thrown (items and corpses), a blast always breaks a pit cover, a carried hose
drops, 3 cells for a mortar beside a human, its own mod. §3–§8 are written to those rulings.

## 2. What exists already

**In our source — the receiving half is BUILT.** FlowWorks already treats any involuntary arrival in an
open pit as a forced fall, regardless of who moved the pawn:
- `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — a per-map tick detector compares each
  pawn's cell with its last cell and with the cell its own path follower walked it into; any arrival on
  D = 4 that was **not** a walked step is forced → `OnForcedDescent` (fall damage, player pawns held like
  jumpers). Comment names "a mod's push" explicitly.
- `RM_PitPathing.cs` — `RM_Patch_PawnFlyer_LandInPit` postfixes `PawnFlyer.RespawnPawn`: a flyer landing in
  an open pit from outside it is a forced descent (a flyer despawns the pawn, so the tick detector cannot
  see it).
- `RM_PitTrapMath.DescentFalls(walkedStep, ontoUsableLadder, playerFaction, captured)` with offline
  selftests (`SelfTest/Program.cs` ~l.874: "colonist blown/forced in: falls").
- `human_review.py` row **F10** "Blast / blowback can knock a pawn into a pit" — status *Partly built*,
  probe `cs:class RM_Patch_\w*(Knockback|Blowback|Stagger)` finds nothing. KEYSHEET says "Still to build:
  an explosion or knockback throwing someone into a pit."
⇒ **This mod mostly only has to MOVE the pawn by an engine-normal route.** For the ordinary case (open
ground → open pit) FlowWorks catches the landing with no change. Two FlowWorks gaps were found by GPT and
confirmed in source (§10 #1, #12): a held colonist's jumper flag is pruned while it is despawned in a
flyer, and a takeoff from a *covered* D = 4 cell is skipped by the flyer postfix.

**Our existing explosion hooks (must coexist):** `FlowWorks RM_Patch_ExplosionLightsLiquid`
(postfix `DamageWorker.ExplosionAffectCell`), `GimmeSomeSlack Patch_GenExplosion_CutSpans` (postfix
`GenExplosion.DoExplosion`, cuts aerial cord spans), `Ninefold Patch_ExplosionOccurred`,
`Scarlands Patch_GenExplosion_DoExplosion` (Totchak). None moves pawns. `ExplosiveGrowth` "burst" applies
"knockdown" (a stun/hediff, not displacement). No `jawa/explosion_at` bridge tool was found by name; the
runner can call `GenExplosion.DoExplosion` through its own C#.

**In installed mods (1,420 About.xml scanned across both roots; sanity probe "gravship" = 43 hits).**
None is active on today's list (ModsConfig holds 10 mods — the minimal tier is swapped in), all installed:
- **JecsTools Unofficial 1.6** (`jecrell.jecstools`, ws 3524247750) — full C# source shipped:
  `Knockback/HediffComp_Knockback.cs` (259 l.). Push direction = instigator→target, distance =
  `knockDistance × absorbedCurve × massCurve(mass − inventory)`, path walked with
  `GenSight.PointsOnLineOfSight`, stops at the previous cell on impassable / closed door / map edge,
  collision → impact damage (configurable DamageDef) + optional stun + thought. Moves the pawn with its own
  AbilityUser FlyingObject. **Best prior art for the collision kernel.** Hediff-triggered (melee/ability),
  not explosion-triggered.
- **Vanilla Expanded Framework** (ws 2023507013, `VEF.dll`) — literal symbols `DamageWorker_PushBackAttackMelee`,
  `TryToKnockBack`, `knockBackDistance`/`pushBackDistance`, `VFEA_AbilityFlyer`, and Harmony patches on
  `PawnFlyer.MakeFlyer`/`RecomputePosition`. A melee pushback DamageWorker; it patches PawnFlyer, which is
  a compatibility point for us. (Literal-string search of the DLL, run with `MEASURE_ALLOW_SCAN=1`; an
  existence check, not a census.)
- **Melee Animation** (ws 2944488802) — `AM_KnockbackFlyer` (a `PawnFlyer` subclass), `MakeKnockbackFlyer`.
  Proves a PawnFlyer subclass is a workable knockback carrier in 1.6.
- Nothing installed applies knockback **to explosions**. The mod is not already built.

**Engine (RimSage, decompiled 1.6):**
- `GenExplosion.DoExplosion` spawns an `Explosion`; `Explosion.Tick` affects cells over several ticks in
  distance order (`GetCellAffectTick`) — a **wave**, not one instant.
- Per cell: `DamageWorker.ExplosionAffectCell` copies the cell's things into `thingsToAffect`, then calls
  `ExplosionDamageThing(explosion, t, damagedThings, ignoredThings, cell)` per thing. That method already
  computes `angle = (t.Position − explosion.Position).AngleFlat`, calls `t.TakeDamage`, and on a wound
  does `pawn.stances.stagger.StaggerFor(95)` (`StaggerExplosionImpactTicks = 95`). **This is our hook.**
  `damagedThings` stops a pawn being hit twice by one explosion.
- `PawnFlyer.MakeFlyer(ThingDef flyingDef, Pawn, IntVec3 destCell, EffecterDef, SoundDef, bool
  flyWithCarriedThing=false, Vector3? overrideStartVec=null, Ability=null, LocalTargetInfo=default)`:
  suspends the current job (`InterruptForced`), captures the job queue, **despawns** the pawn into the
  flyer. Caller must `GenSpawn.Spawn(flyer, pawn.Position, map)`.
- `ThingDefOf.PawnFlyer_Stun` (Core def): `flightSpeed 8`, `flightDurationMin 0.75`, `heightFactor 2`,
  `stunDurationTicksRange 60~180`. Vanilla uses it to throw fleshbeasts out of a pit burrow/gate
  (`PitBurrow`, `FleshbeastUtility`, `CompSpawnPawnsOnDamaged`). It is literally the engine's "thrown pawn".
- `PawnFlyer.RespawnPawn` drops at `destCell` with `ThingPlaceMode.Direct` (no validity check), restores
  drafted/fire-at-will and the job queue, then stuns for `stunDurationTicksRange`. The flyer itself does
  not check walls along its arc — **the destination must be computed and validated by us.**

## 3. The mechanic

**One sentence:** every blast throws everything light near it — pawns, items and corpses — straight
away from its centre, over sandbags and barricades, stopping early against anything solid; pawns take
impact damage for the distance they did not travel and land stunned; a blast that reaches a pit cover
breaks it; anything that lands in an open pit is in the pit, and FlowWorks makes a pawn fall. (Rulings
in §11.)

### 3.1 What triggers a throw
- **Explosions only, by DamageDef** (Q2: *"melee weapons often already have blowback"*). A `DamageDef`
  carries a throw strength through a `DefModExtension` (`RM_KnockbackExtension { float force; }`).
  Shipped: `Bomb` (`DamageDefOf.Bomb`, verified) gets force 1.0. Flame, EMP, Smoke, Extinguish, ToxGas
  (all verified in `DamageDefOf`) get explicit zero-force extensions. Other mods' explosive DamageDefs get
  one by patch, never by guess — the Star Wars tier adds its own (thermal detonators etc.) in `RSW_`
  patches. A setting "unpatched harmful explosions throw at N%" defaults to 0.
- No `requiresWound`: a void postfix cannot see the DamageResult (§10 #3). Every eligible thing the wave
  reaches is thrown, armour or not.
- Decided per thing inside the explosion wave (§4), deduplicated by (explosion, thing).

### 3.2 What moves
| Subject | Moves? | Notes |
|---|---|---|
| Standing / walking pawn (any faction, humans, animals, mechs) | yes | |
| Downed pawn | yes | a body is thrown; how a downed raider ends up in the pit |
| Pawn with bodySize ≥ `immuneBodySize` (default 2.5) | no, vanilla stagger only | big things are events |
| Pawn already on a D = 4 cell | no | §10 #1; "you can't climb out. Period." |
| Pawn carrying a pawn (rescuer, kidnapper) | no, stagger only | §10 #9 |
| Pawn **flying** (1.6 `Pawn.Flying`) | no | flight + flyer stacking untested; flyer live tests need him present |
| Pawn in bed, carried, in a container, not spawned | no | not on the ground |
| **Item stack** (spawned, category Item, total stack mass ≤ `lightMassLimit`) | **yes** | Q4 "everything light" |
| **Corpse** (mass of the dead body ≤ `lightMassLimit`, inner pawn bodySize < immune) | **yes** | Q4 |
| Item on a cell with a storage edifice (shelf, rack) | no | it is in the furniture, not on the floor |
| Minified building, chunk | yes if under the mass limit | they are items |
| Buildings, plants, filth | never | |
`lightMassLimit` default **75 kg** (a human corpse ≈ 60 kg passes; a full 75-stack of steel = 37.5 kg passes;
a stone chunk passes; a minified heavy machine does not). Mass for an item stack is
`GetStatValue(Mass) × stackCount`.

### 3.3 How far
Kernel (pure, Verse-free `RM_KnockbackMath`), same for pawns, items and corpses:
```
falloff   = 1 − clamp01(dist(thing, centre) / radius)            // 1 at centre, 0 at rim
massScale = clamp( (refMass / max(mass, 1))^0.5 , 0.25, 2 )      // refMass 60 kg (≈ human)
cells     = round(baseCells × force × falloff × massScale × globalMultiplier)
cells     = min(cells, maxThrowCells); if cells < 1 → no move
```
**Calibrated to Q7: a mortar shell beside a human throws it 3 cells.** With radius 2.9 at distance 1,
falloff = 0.655, so `baseCells = 4` gives round(2.62) = 3. Consequences of the same numbers: a frag
grenade (radius 1.9) beside a human → 2; a human on the centre cell → 4; a 10 kg item beside a mortar →
round(4 × 0.655 × 2) = 5 (light things fly farther). `maxThrowCells` default 6. Pawn mass is
`StatDefOf.Mass` minus carried inventory (worn gear counts). Direction = centre → thing's cell; a thing on
the centre cell gets a direction from a seeded Rand keyed on (explosion id, thing id).

### 3.4 The path and what stops it
Walk the grid steps of the line from the thing's cell toward the target (`GenSight.PointsOnLineOfSight`),
one cell at a time. Pawns use their own pathing context (`map.pathing.For(pawn).pathGrid`); items and
corpses use `map.pathing.Normal`. Forced movement ignores fog and forbidden zones; roofs do not stop the
low arc.
| Next cell is… | Pawn | Item / corpse |
|---|---|---|
| walkable, empty | continue | continue |
| out of bounds | stop on previous cell, no impact | stop on previous cell |
| impassable (wall, rock, Fillage.Full edifice) | stop on previous cell, **impact** | stop on previous cell |
| closed door (incl. a FlowWorks sluice door) | stop, impact; door takes a small hit | stop |
| **sandbags / barricade** (Fillage.Partial, passable) | **thrown over: continue**, no impact (Q3) | continue |
| occupied by another pawn | stop before; impact split between both (the other does not move) | continue (items pass pawns) |
| an **open FlowWorks pit** (D = 4, uncovered) | **enter it and stop there** — FlowWorks does the fall | enter and stop — it lies on the pit floor |
| a **pit cover** the wave has not yet broken | continue as ground | continue as ground |
| deep water / liquid not walkable for this pawn | stop before (no impact) | stop before |
| fire / burning liquid | continue | continue |
A pit cell that is also occupied or blocked by an edifice counts as blocked. Diagonal steps never cut a
wall corner (both orthogonal neighbours must be passable). If the final cell is a Fillage.Partial edifice
cell, a pawn may land on it (sandbag cells are standable); an item lands on the next free cell back along
the line.

### 3.5 Damage, stun, downed
- Pawn impact: `Blunt` = `impactDamagePerCell (default 4) × cellsNotTravelled × massScale⁻¹ᐟ²`, applied at
  **launch**, instigator = the explosion's instigator; dead/downed/spawned re-checked before the throw.
- Items and corpses take no impact damage (the blast already damaged them).
- Pawn landing: stun 60–120 ticks via the flyer def's `stunDurationTicksRange`. Vanilla's own 95-tick
  explosion stagger still applies on wound.
- No fall damage on flat ground; FlowWorks owns fall damage into pits.

### 3.6 A blast always breaks a pit cover (Q5)
When the wave reaches a cell holding an intact `Building_PitCover`, the whole deck springs at once
(`Building_PitCover.Spring(fallers)` with every pawn standing on the deck, `RM_PitCoverUtility.Deck`).
This is a **FlowWorks** feature, not this mod's: covers are FlowWorks', it already postfixes
`DamageWorker.ExplosionAffectCell` (`RM_Patch_ExplosionLightsLiquid`), and the ruling should hold with the
knockback mod absent. Its trigger set is the same "blast" set (§9 Q-A). Order inside one blast: the cover
breaks when the wave reaches its cell; throws are flushed at the end of that explosion tick, so a thing
thrown onto a cover the wave has already reached lands in an open pit, and one thrown onto a cover the wave
reaches later is in the air when it breaks and lands in the hole. Both end in the pit.

## 4. Engine route and performance

### 4.1 Where to hook
**Prefix + postfix on `DamageWorker.ExplosionDamageThing(Explosion, Thing, List<Thing>, List<Thing>,
IntVec3)`** (protected virtual). The prefix records eligibility (thing not already in `damagedThings`,
not in `ignoredThings`); the postfix **only enqueues** a request carrying immutable data — map, explosion
thingIDNumber, centre, radius, damType, force, instigator, thing, takeoff cell — on a per-map component.
⚠️ Never despawn inside the loop: `ExplosionAffectCell` iterates a cell list and FlowWorks' postfix runs
after it. **Flush** in a postfix on `Explosion.Tick`, from a snapshot of the queue, never reading the
(possibly destroyed) Explosion. A pawn killed by the blast is now a corpse: the request is re-resolved to
the corpse and judged by the corpse rules. Owed before build: one RimSage search for `ExplosionDamageThing`
overrides that skip base.

### 4.2 How pawns move — a `PawnFlyer` of our own def
`RM_PawnFlyer_Knockback` (ParentName `PawnFlyerBase`, thingClass `PawnFlyer`, worker `PawnFlyerWorker`,
copied from Core's `PawnFlyer_Stun` with `flightDurationMin` ~0.3 and `heightFactor` ~0.6). Engine-normal
(the engine's own thrown fleshbeast), visible arc, suspends and restores jobs/drafted/queue, lands with a
stun, saves mid-flight, and FlowWorks' `RM_Patch_PawnFlyer_LandInPit` already catches its landing.
`PawnFlyer.MakeFlyer(def, pawn, destCell, null, landingSound, flyWithCarriedThing: true)` then
`GenSpawn.Spawn(flyer, takeoffCell, map)`.
- ⚠️ Vanilla `CheckDestination` redirects any flyer every 15 ticks to any `ValidJumpTarget` within 3.9
  cells (§10 #5). A Harmony prefix skips it for our def only; our own landing check walks back along the
  travelled line toward takeoff if the destination became invalid; `TryDrop`'s result is checked.
- **A carried hose end is dropped at the takeoff cell before the throw (Q6)** — `HoseCarry` `Interrupt` on
  `Carrying` → `Dropped`; any other carried item rides with the pawn.
- Rejected routes: a position set + `Notify_Teleported` reads as teleporting over 3+ cells; a forced
  "stumble" job is a *walked* step, which FlowWorks treats as pathing (no fall) and `RM_PitPathing`
  refuses pit cells.

### 4.3 How items and corpses move — a NEW path
`PawnFlyer.MakeFlyer` takes a `Pawn`, so items need their own carrier. Two options:
| Route | For | Against | Verdict |
|---|---|---|---|
| **Instant relocate**: `DeSpawn`, then `GenPlace.TryPlaceThing(thing, dest, map, ThingPlaceMode.Direct)`, falling back along the line; a dust fleck at the landing cell | cheapest; no per-thing ticking object; stacks merge by vanilla rules | no visible flight | **v1** |
| `RM_ThrownThing`: a Thing holding a `ThingOwner`, drawn on an arc, landing by `GenPlace` | looks like the pawns | one ticking object per stack; a stockpile hit by a mortar spawns dozens | later, only if he asks for the look |
Forbidden state, ownership and stack identity are preserved by `DeSpawn`/`TryPlaceThing`. An item that
lands in an open pit stays on the pit floor; haulers cannot path in, so it is reachable only by someone in
the pit or via a lowered ladder (§9 Q-B). A corpse thrown into a pit is the same.

### 4.4 Performance — items are the risk
Pawns: a heavy barrage (10 shells × 15 pawns) is ≤ 150 flyers spread over many ticks. **Items are the
real cost:** a mortar into a stockpile can reach ~25 cells × several stacks each, and a barrage multiplies
that. Guards, all in Mod Settings:
- `maxThrowsPerExplosion` (default 40 — pawns first, then corpses, then items nearest the centre).
- `maxItemThrowsPerMapTick` (default 60 across all explosions); the overflow is dropped, not deferred, so
  nothing accumulates.
- The instant item route costs one despawn + one place per stack, no ticking object.
- The hook returns on its first line when the damType's force is 0, and the flush is a single empty check
  when nothing is queued.
- `barrage_perf` (§8.2) measures ms per explosion tick on a stockpile, not only on pawns.

## 5. Mod Settings

Defaults = the owner's rulings (§11); all off = vanilla. Nothing here affects worldgen.
| Setting | Type | Default | Notes |
|---|---|---|---|
| Enable explosive knockback | toggle | on | master |
| Throw strength (global multiplier) | 0–3 | 1.0 | 1.0 = mortar beside a human throws 3 cells (Q7) |
| Maximum throw distance (cells) | 1–10 | 6 | |
| Unpatched harmful explosions throw at | 0–100% | 0% | for mods' DamageDefs with no extension |
| Throw downed pawns | toggle | on | |
| Throw animals | toggle | on | |
| Throw mechanoids | toggle | on | |
| Immune at body size ≥ | 1–5 | 2.5 | |
| Throw items | toggle | on | Q4 |
| Throw corpses | toggle | on | Q4 |
| Light-thing mass limit (kg) | 5–200 | 75 | items and corpses above it stay put |
| Sandbags and barricades stop a throw | toggle | off | Q3: thrown over |
| Impact damage on hitting a wall / pawn | toggle + per-cell 0–15 | on, 4 | pawns only |
| Landing stun (ticks) | range | 60–120 | |
| Doors take impact damage | toggle | on | |
| Throw into FlowWorks pits | toggle | on | off = an open pit cell is a wall for the path |
| Max throws per explosion | 1–200 | 40 | performance |
| Max item throws per map tick | 1–500 | 60 | performance |
| Debug: draw throw vectors | toggle | off | dev mode only |
**In FlowWorks' settings, not this mod's:** "Blasts break pit covers" — toggle, default **on** (Q5).

## 6. Naming

Tier **RimMandrake** — it is a mechanic for any RimWorld game, franchise-free.
- Folder `src/RimMandrake/ExplosiveKnockback/`, packageId **`mandrake.rm.explosiveknockback`**, name
  "RimMandrake: Explosive Knockback".
- C# namespace `RimMandrake.ExplosiveKnockback`; assembly `RimMandrakeExplosiveKnockback.dll`.
- Defs: `RM_PawnFlyer_Knockback` (ThingDef), `RM_KnockbackExtension` (DefModExtension class),
  `RM_KnockbackMath` (pure kernel), `RM_MapComponent_Knockback` (queue),
  **`RM_Patch_DamageWorker_ExplosionKnockback`** — the name deliberately matches FlowWorks review row
  F10's probe regex `RM_Patch_\w*(Knockback|Blowback|Stagger)`, so F10 flips from "partly built" by
  itself. Settings class `RimMandrakeExplosiveKnockbackSettings`.
- Star Wars tier: `RSW_` patches that give Star Wars explosive DamageDefs (and later a Force-push
  ability) an `RM_KnockbackExtension` live in the RimStarWars layer, never in this mod.
- Collision check: no existing `src/*/ExplosiveKnockback` folder; `ExplosiveGrowth` is a different mod.

## 7. Interactions with our mods

**FlowWorks — pits / superdeep (the reason this exists).**
- A pawn landing in an open D = 4 cell from outside: `RM_Patch_PawnFlyer_LandInPit` → `OnForcedDescent` →
  fall damage; a player pawn is added as a jumper (held; a lowered ladder lets them out); a hostile is
  captured. It patches the base `PawnFlyer.RespawnPawn` and our def uses thingClass `PawnFlyer`, so it fires.
- **Two FlowWorks changes are owed** (file for FOUNDRY with the build): (1) `RM_Patch_PawnFlyer_LandInPit`
  skips any superdeep takeoff, so a pawn thrown off a *covered* D = 4 cell into an open pit is missed
  (§10 #12) — skip only when the takeoff was an open pit; (2) **blasts break pit covers** (§3.6, Q5).
- The path stops **in** the first open pit cell: nothing is thrown across a pit. A lowered-ladder cell is
  still a forced fall (`DescentFalls(walkedStep:false, …)` returns true before it reads the ladder).
- A pawn already on a D = 4 cell is never thrown (§3.2).
- Items and corpses in a pit: FlowWorks has no item-fall rule; they lie on the pit floor (§9 Q-B).
- Liquids: burning tar is walkable, so a blast can throw a pawn into it; FlowWorks' explosion-lights-liquid
  postfix may already have lit that cell. Drowning in a liquid-filled pit is FlowWorks' (`RM_PitDrowning`).
- Sluice doors are doors: closed stops the throw with impact.
**Flyers (1.6 flight).** `Pawn.Flying` pawns are not thrown. Proof is a state read (cell before/after,
`Flying` true) — never an unattended live flight hunt (owner, said three times).
**Gimme Some Slack.**
- Aerial cord spans are already cut by explosions (`Patch_GenExplosion_CutSpans`); independent.
- **Hose carry (Q6):** the hose end drops where the carrier stood — dropped at the takeoff cell before
  `MakeFlyer`, through `HoseCarry`'s `Interrupt` (`Carrying` → `Dropped`). The scene asserts the hose end's
  physical cell and holder, not just the table state.
- Laid hoses and cords are not items on the floor in the `Item` category sense; they are not thrown.
  (Verify the hose end's ThingCategory before build.)
**Ninefold / Scarlands (Totchak) / FlowWorks liquid fire** hook the same explosion; they read, we move.
Same-tick ordering against them is irrelevant because we defer moves to the end of the explosion tick;
ordering between two explosions on one tick is not (§10 #6).
**VEF / Melee Animation** patch `PawnFlyer.MakeFlyer`/`RecomputePosition`; inactive today, installed. A
VEF-active run is a ship gate.

## 8. The first functional script

Per `design/RimMandrake/debug_process.md` §2: a modcheck `Suite` in
`src/RimMandrake/ExplosiveKnockback/validation.py`, a walk at
`design/validation_walks/RimMandrake/ExplosiveKnockback.md` with `## must be true` lines and coverage
arrows, every setting in `suite.toggles`, and a `--mock` selftest that exits clean first.

### 8.1 Offline kernel tests (pure C#, `Source/SelfTest`, like FlowWorks' `Program.cs`)
`RM_KnockbackMath` is Verse-free: input a grid fixture (passable / wall / door / partial cover / pawn /
pit / covered pit / deep water / out-of-bounds), centre, radius, force, mass, bodySize, kind (pawn | item |
corpse), settings; output `(destCell, cellsTravelled, impact, stopReason)`.
- K-01 calibration: mortar (r 2.9) at distance 1, 60 kg → 3 cells; frag (r 1.9) → 2; centre → 4.
- K-02 unobstructed distance falls monotonically with distance from centre; 0 at the rim.
- K-03 heavier never travels farther (property test); bodySize ≥ immune → no move; mass > light limit
  (item/corpse) → no move.
- K-04 never ends on an impassable / door / occupied / out-of-bounds cell (property test).
- K-05 never passes through a wall, including diagonal corner-cutting.
- K-06 partial cover is crossed (pawn and item); with the setting on, it stops a pawn before it.
- K-07 wall stop: impact = perCell × cells not travelled × massScale⁻¹ᐟ²; out-of-bounds: 0; items: 0.
- K-08 open pit: stops IN the first pit cell, never beyond; with "throw into pits" off, stops before it.
- K-09 pawn-pawn: impact split, other pawn not moved; item passes a pawn cell.
- K-10 epicentre direction deterministic for (explosion id, thing id).
- K-11 caps: per-explosion priority (pawns, corpses, items-nearest-first); per-map-tick item cap drops
  overflow.
- K-12 dedupe: an ignored thing and a repeat callback for one (explosion, thing) enqueue nothing.

### 8.2 In-game runner scenes
A `jawa/knockback_playtest_*` trio in the style of FlowWorks' `playtest_runner.py` (start → poll → collect
JSONL journal; verdict re-derived from the file; scratch map only). Each scene calls
`GenExplosion.DoExplosion` from C#, ticks, and asserts **journal records** (request, launch, landing cell,
impact amount, stopReason) plus state — and, for every "not moved" assertion, that the wave processed the
thing.
| Scene | Setup | PASS reads |
|---|---|---|
| calibration | human 1 cell from a mortar centre, open field | journal: 3 cells, away from centre; stunned; alive |
| wall_stop | wall 1 cell behind | journal impact > 0, stopReason wall; did not pass the wall |
| door_stop | closed door behind | as above; door HP down by the impact hit |
| over_sandbags | sandbag line between pawn and open ground | pawn landed beyond the sandbags |
| pit_colonist | colonist beside an open pit, blast on the far side | descent count +1 exactly, this pawn, this cell; held as jumper |
| pit_enemy | hostile, same | descent +1; captured |
| cover_breaks | blast reaching a cover with no one on it; and one with a pawn on it | cover sprung both times; the standing pawn fell |
| thrown_onto_cover | pawn thrown toward a cover the wave reaches later | pawn ends in the pit |
| covered_takeoff | pawn on a covered D = 4 cell beside an open pit | after the FlowWorks fix: descent +1 |
| no_cross | 1-wide pit, 4-cell throw | stops inside, never on the far lip |
| items | steel stack, a 10 kg item and a heavy minified building beside a blast | light ones moved per kernel; heavy one did not; stack count unchanged |
| corpse_into_pit | corpse beside a pit | corpse on the pit floor; no exception |
| killed_by_blast | pawn the blast kills | its corpse is thrown by the corpse rule |
| shelf | items on a shelf | not moved |
| heavy / downed / flying_skip / in_pit_skip / carrier_skip | one each | per §3.2; flying by state read only |
| hose_carry | colonist carrying a hose end | hose end on the takeoff cell, not held; state Dropped |
| redirect_guard | destination blocked mid-flight; two pawns to one cell | lands on the line back toward takeoff; never across a wall |
| two_blasts | two explosions on one tick, both orders | no exception; one throw per pawn; recorded |
| save_mid_flight | save with a flyer in the air, reload | save holds the pawn in a flyer; after reload it exists once |
| raid_lord | a real assault raid hit by a mortar | raiders resume their lord's duty after the stun |
| barrage_perf | 10 shells on 15 pawns AND on a full stockpile | ms per explosion tick under budget; launches and item moves counted; no Player.log errors |
| settings_off | master off; items off; corpses off | nothing / no items / no corpses moved; wave processed them |
| vef_active | VEF loaded, calibration + pit_colonist | same results |
`pit_*` scenes close FlowWorks review row F10 and `FLOWWORKS_PIT_FALL_ONLY_FORCED_1`'s forced-entry check.

## 9. Open questions for the owner

All eight original questions are answered (§11). The rulings raised these:

**Q-A. What counts as a "blast" for breaking pit covers and for throwing?**
- (a) Only explosions that throw (Bomb and anything patched with force) *(design)* — fire, EMP, smoke and
  gas never break a cover. Predictable.
- (b) Any explosion that harms health, including incendiary — a fire grenade also opens covers.
- (c) Any explosion at all, even EMP and smoke — simplest rule, but a smoke grenade then defeats a trap.

**Q-B. Items and corpses that land in a pit.**
- (a) They stay on the pit floor; only someone in the pit, or a hauler via a lowered ladder, can reach them
  *(design)*. Cost: blasts near pits can "lose" loot until a ladder is down.
- (b) Haulers may fetch from the lip, like a warden feeding from the lip. Cost: new FlowWorks hauling code.
- (c) Items and corpses are never thrown into pits (they stop at the lip). Cost: corpses-into-pit cleanup
  by mortar goes away.

## 10. GPT evaluation — what I accept, what I reject and why

Full answer: `design/RimMandrake/explosive_knockback_gpt_eval_2026-10-06.md` (gpt-6.1-sol, high effort,
2026-10-06; fed this doc, `RM_PitPathing.cs`, `RM_SuperdeepTrap.cs`, JecsTools' `HediffComp_Knockback.cs`).
Its verdict: *"proceed with a narrow pit-entry prototype."* I re-checked the load-bearing claims in the
decompiled 1.6 source before ruling.

**Accepted — and verified in source:**
- **#5 The flyer redirects its own landing.** CONFIRMED: `PawnFlyer.TickInterval` calls private
  `CheckDestination()` every 15 ticks; if `JumpUtility.ValidJumpTarget` fails it moves `destCell` to any
  valid cell within radius 3.9 — across a wall, onto the far lip of a pit, out of a pit. This breaks §3.4's
  guarantees. Fix: Harmony prefix on `PawnFlyer.CheckDestination` that skips it when
  `__instance.def == RM_PawnFlyer_Knockback`, plus our own landing check along the original segment
  (walk back toward takeoff; if nothing valid, land at takeoff). Keeping flights < 15 ticks is not a fix.
- **#1 Held colonists lose their jumper flag in flight.** CONFIRMED: `RM_SuperdeepTrapState` prunes
  jumpers with `!p.Spawned`. v1: **pawns already on a D = 4 cell are never pushed** (stagger only). That also
  enforces "you can't climb out. Period." without the in-pit path rule.
- **#12 Covered-D4 takeoff into an open pit is missed** by `RM_Patch_PawnFlyer_LandInPit` (it skips any
  superdeep takeoff). Needs a one-line FlowWorks change (skip only if the takeoff cell was an *open* pit) —
  file for FOUNDRY with the build. "No FlowWorks change needed" in §2 is corrected.
- **#2 Dedupe ourselves.** A postfix runs after the base's early returns; `damagedThings` is filled before the
  `ignoredThings` check. Use a prefix to record eligibility (not already in `damagedThings`, not ignored) and
  key requests by (explosion thingIDNumber, pawn).
- **#3 Drop `requiresWound`** (done in §3.1).
- **#4 Capture immutable blast data** (map, explosion id, centre, radius, damType, instigator, takeoff cell)
  at enqueue; the flush never reads the destroyed Explosion.
- **#6 Overlapping explosions:** policy = first explosion to reach a pawn throws it; a pawn in flight is not
  on the map and so is not damaged by later blasts that tick. That IS a combat change; keep flights short
  (~0.3 s) and record it as a known behaviour, measured in `barrage_perf`.
- **#7/#11 Landing and impact contracts:** impact damage is applied at **launch** (then re-check dead /
  downed / spawned before `MakeFlyer`); fallback walks back along the allowed segment; check `TryDrop`'s
  result. Patches are scoped to our def so vanilla jumps and other mods' flyers are untouched.
- **#8/#9 Jobs and carrying:** v1 does not push a pawn **carrying a pawn** (rescuer/kidnapper) — stagger
  only; items ride with `flyWithCarriedThing: true`, and the hose scene asserts the physical holder and cell,
  not just the table state. VEF-active run is a ship gate.
- **#10 Fallback for unpatched explosions defaults to 0%** (done in §5); excluded vanilla defs get explicit
  zero-force extensions.
- **#15 Geometry policies:** forced movement ignores fog and forbidden zones; roofs do not stop the low arc
  (visual only); a pit cell that is also occupied or blocked by an edifice counts as blocked; cell count is
  grid steps of the line, not Euclidean.
- **#16 My worked numbers were wrong** (fixed in §3.3).
- **#17/#18 Test plan:** scenes assert event records (a knockback journal: request, launch, landing cell,
  impact amount, stopReason), exact descent-count deltas and held state, and that the wave actually
  processed the pawn before asserting "not moved". Added scenes, in priority order: ignored pawn / duplicate
  callback; final-tick explosion; two blasts reversed order; covered-D4 takeoff; destination blocked
  mid-flight + two flyers one cell; carrying an item / a pawn; death in flight; save/load before a pit
  landing; one real raid-lord scene; one VEF-active run. These outrank the 10k random-grid property test.
- **#13/#14** downed (before and by the blast), berserk/manhunter, retreating raider, prisoner, forming
  caravan: added as behaviour scenes; no assumption they break.
- **#20** performance counts launches, and the cap counts successful launches per map tick; F10 closes only
  on a recorded blast → displacement → exactly one forced descent, never on the class-name probe.

**Not taken:** **#19 "smallest version first"** (a 1-cell shove into an adjacent pit, no flyer) — the owner
ruled Q1 **everywhere** (§11), so the general mod is the build.

**Rejected:**
- *Position set as the general route* — for multi-cell pushes it reads as teleporting, and every job/stance
  edge becomes ours. Items and corpses do use an instant relocate (§4.3) — they have no jobs or stances to break.
- *Excluding inventory mass is "a balance choice"* — agreed it is a choice; I keep JecsTools' rule (worn
  gear counts, backpack does not) because a loaded hauler should not become immovable. Not a defect.

## 11. Owner decisions, 2026-10-06 19:05 (question cards)

All taken by question card unless quoted.
- Q1 scope: **everywhere** — every blast throws pawns; pits are one consequence.
- Q2 weapons: **explosions only** — owner typed: *"(1) because melee weapons often already have blowback"*.
- Q3 cover: **thrown over sandbags and barricades.**
- Q4 items: **everything light** — items and corpses are thrown too.
- Q5 pit cover: **a blast on a cover always breaks it.**
- Q6 carried hose: **drops where the carrier stood.**
- Q7 strength: **3 cells** for a mortar shell beside a human (a Mod Setting scales it).
- Q8 packaging: **its own mod**, `mandrake.rm.explosiveknockback`.
- Q9 (card 19:11) blasts that break a pit cover: **damaging blasts (bombs, grenades, mortars) AND fire/incendiary**;
  EMP, smoke and stun blasts do not. Owner typed *"1+3"* (the damaging-only and bombs-and-fire options combined).
- Q10 (card 19:11) items/corpses thrown toward a pit: **fall in and stay retrievable** — colonists fetch them the way
  they reach the pit floor now (hauling into pits must be verified).
- Owner, 19:13, typed: *"And when something falls into a covered pit, of course it is no longer covered"* — anything
  that falls through a cover (pawn, item, corpse) leaves the cover broken.
