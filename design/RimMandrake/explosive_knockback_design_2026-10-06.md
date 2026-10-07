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

⇒ So what he has stated: explosions (and, older, weapon blowback) move pawns against their will, and that
is the route by which colonists fall into pits. What he has NOT stated: whether it is its own mod (he
calls it one), whether it applies everywhere or only near pits, its strength, or whether weapons other
than explosions push. Those are §9 questions, not assumptions — §3 is written for the general mod
because he named a mod, with every scope choice exposed as a setting.

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

**One sentence:** when an explosion wounds or reaches a pawn, the pawn is thrown a short distance
straight away from the blast centre, stops early against anything solid (taking impact damage for the
distance it did not travel), and lands stunned — and if it lands in an open pit, FlowWorks makes it fall.

### 3.1 What triggers a push
- **Explosions only, by DamageDef.** A `DamageDef` carries a push strength through a `DefModExtension`
  (`RM_KnockbackExtension { float force; }` — no `requiresWound`: a void postfix cannot see the
DamageResult, GPT #3; v1 pushes every eligible pawn the wave reaches). Shipped: `Bomb` (`DamageDefOf.Bomb`,
  verified) gets one. Flame, EMP, Smoke, Extinguish, ToxGas (all verified in `DamageDefOf`) do **not**
  push by default. Other mods' explosive DamageDefs get one by patch, not by guess — the Star Wars tier
  adds its own (thermal detonators etc.) in `RSW_` patches. A setting "any other explosion that harms
  health pushes at N%" covers unpatched mod explosives.
- **Weapon blowback** (his 2026-09-17 phrase) is NOT in v1 — §9 Q2.
- The push is decided per pawn inside the explosion wave (§4), so a pawn the wave never reaches is never
  pushed, and `damagedThings` already guarantees one push per pawn per explosion.

### 3.2 Who moves
| Subject | v1 | Why |
|---|---|---|
| Standing / walking pawn (any faction, humans, animals, mechs) | yes | the point |
| Downed pawn | yes, at the same force | a body is thrown; this is how a downed raider ends up in the pit |
| Pawn with bodySize ≥ `immuneBodySize` (default 2.5: thrumbo-class, big mechs) | no, stagger only | "mass is menace" — big things are events |
| Pawn in bed, carried, in a flyer/container, not spawned | no | not on the ground |
| Pawn **flying** (1.6 `Pawn.Flying`) | no in v1 | flight + flyer stacking is untested; and flyer live tests need him present (CLAUDE.md) |
| Items, corpses, chunks | no in v1 | cost and chaos; §9 Q4 |
| Buildings | never | |

### 3.3 How far
Kernel (pure, Verse-free `RM_KnockbackMath`):
```
falloff   = 1 − clamp01(dist(pawn, centre) / radius)            // 1 at centre, 0 at rim
massScale = clamp( (refMass / max(mass, 1))^0.5 , 0.25, 2 )     // refMass 60 kg (≈ human)
cells     = maxPushCells × force × falloff × massScale × globalMultiplier
cells     = floor(cells + 0.5); if cells < 1 → no move (vanilla stagger only)
cells     = min(cells, maxPushCells)
```
Mass is `StatDefOf.Mass` minus carried inventory mass (as JecsTools does; armour counts). Defaults:
`maxPushCells 3`, `force(Bomb) 1.0`. Worked (corrected after GPT #16): a human 1 cell from a frag centre
(radius 1.9) gets round(3 × 0.47) = 1 cell; 1 cell from a mortar centre (radius 2.9) gets 2; on the centre
cell, 3. If that reads too weak, the lever is `maxPushCells` or a falloff exponent < 1 (§9 Q7).
Direction = centre → pawn cell. A pawn **on** the centre cell gets a random direction from a seeded Rand
(the engine itself uses a random angle there).

### 3.4 The path and what stops it
Walk the cells of the line from the pawn's cell toward the target (`GenSight.PointsOnLineOfSight`, as
JecsTools does), one cell at a time, using the **pawn's own** pathing context
(`map.pathing.For(pawn).pathGrid`) so a swimmer and a walker differ correctly:
| Next cell is… | Result |
|---|---|
| walkable, empty | continue |
| out of bounds | stop on the previous cell, no impact |
| impassable (wall, rock, Fillage.Full edifice) | stop on previous cell, **impact** |
| closed door (incl. a FlowWorks sluice door) | stop, impact; door takes a small hit |
| partial-fill cover (sandbags, barricade) | stop on it? or before it? — §9 Q3; default: stop **before**, impact halved |
| occupied by another pawn | stop before; impact split between both (the other does not move in v1) |
| an **open FlowWorks pit** (D = 4, uncovered) | **enter it and stop there.** Nothing flies across a pit. FlowWorks does the fall. |
| a **pit cover** | continue as ground; whether the cover gives way is FlowWorks' rule (§7) |
| deep water / deep liquid not walkable for this pawn | stop before (no impact) |
| fire / burning liquid | continue — being thrown into burning tar is a feature |
Diagonal steps never cut a wall corner (both orthogonal neighbours must be passable), the same rule
vanilla pathing uses.

### 3.5 Damage on impact, stun, downed
- Impact: `Blunt` damage = `impactDamagePerCell (default 4) × cellsNotTravelled × sqrt(massScale⁻¹)`,
  applied once, instigator = the explosion's instigator (so kills and goodwill attribute correctly).
- Landing: stun `knockdownStunTicks` (default 60–120) through the flyer def's `stunDurationTicksRange`.
  Vanilla's own 95-tick explosion stagger still applies on wound; we do not add to it.
- A push never downs by itself except through the impact damage, which is ordinary damage.
- No fall damage for flat ground; FlowWorks owns fall damage into pits.

## 4. Engine route and performance

### 4.1 Where to hook
**Postfix `DamageWorker.ExplosionDamageThing(Explosion, Thing, List<Thing>, List<Thing>, IntVec3)`**
(protected virtual; Harmony patches the base, and every subclass that does not override it). It has the
explosion (centre, radius, damType, instigator), the pawn and the cell, and runs at the moment the
wave reaches that pawn. The postfix **only enqueues** a request `(pawn, centre, radius, force, instigator,
tick)` on a per-map component. ⚠️ Do not despawn the pawn inside the loop: `ExplosionAffectCell` is
iterating a cell list, and FlowWorks' own `ExplosionAffectCell` postfix runs after it.
**Flush** in a postfix on `Explosion.Tick` (runs after the tick's cells are affected, even on the tick the
explosion destroys itself) — same tick, after damage, so a pawn killed by the blast is dead and skipped.
Subclasses that override `ExplosionDamageThing` without calling base would not push; RimSage search for
overrides is owed before build (one search).

### 4.2 How to move — three routes considered
| Route | For | Against | Verdict |
|---|---|---|---|
| **A. `PawnFlyer` with our own def** `RM_PawnFlyer_Knockback` (ParentName `PawnFlyerBase`, thingClass `PawnFlyer`, worker `PawnFlyerWorker`, copied from Core's `PawnFlyer_Stun` with a lower `flightDurationMin` ~0.25 and `heightFactor` ~0.6) | Engine-normal: the engine's own "thrown pawn" (fleshbeasts out of pits). Visible arc. Suspends and restores jobs, drafted state, job queue. Lands with a stun. **FlowWorks already catches its landing** (`RM_Patch_PawnFlyer_LandInPit`). Saves mid-flight (it is a Thing with an inner container). | Pawn despawned for the flight (≈ 0.25–0.75 s): untargetable, and anything iterating spawned pawns misses it. VEF patches `MakeFlyer`. `RespawnPawn` drops with `ThingPlaceMode.Direct` — destination must already be valid. | **Chosen.** |
| B. Position set + `Notify_Teleported` | Instant, no despawn | Looks like a teleport; we own every job/stance edge. FlowWorks' tick detector does catch it. | Fallback only, for a setting "instant knockback (performance)" — and not in v1 |
| C. A forced "stumble" job | Pawn stays spawned | It is a *walked* step: FlowWorks reads a walked step into a pit as pathing (no fall) and `RM_PitPathing` refuses pit cells. Contradicts the ruling. | **Rejected.** |

`PawnFlyer.MakeFlyer(def, pawn, destCell, null, landingSound, flyWithCarriedThing: true)` then
`GenSpawn.Spawn(flyer, pawn.Position, map)` (the vanilla pattern in `FleshbeastUtility`). With
`flyWithCarriedThing: true` the carried thing (a hauled item, a carried hose end) is kept. Re-validate
`destCell` at landing time is impossible in vanilla `RespawnPawn` — if a wall is built or a pawn walks into
the cell during the flight, `Direct` still places it. ⚠️ And vanilla `CheckDestination` redirects the flyer itself every
15 ticks (§10 #5) — the guard is a def-scoped prefix that disables it, plus our own fallback that walks
back along the travelled line toward the takeoff cell.

### 4.3 Performance
Per pushed pawn: ≤ `maxPushCells` cell checks + one Thing spawn. A heavy mortar barrage (10 shells ×
15 pawns) is 150 cheap requests across many ticks. Guards: `maxPushesPerExplosion` (default 40), and the
whole hook returns on the first line when the damType has no extension and the global "other explosions"
setting is 0. No per-tick cost when nothing is queued (queue empty check only).

## 5. Mod Settings

Defaults = shipped behaviour; all off = vanilla. Nothing here affects worldgen.
| Setting | Type | Default | Notes |
|---|---|---|---|
| Enable explosive knockback | toggle | on | master |
| Push strength (global multiplier) | 0–3 | 1.0 | |
| Maximum push distance (cells) | 1–8 | 3 | |
| Explosions from other mods push at | 0–100% | 0% | for harmsHealth DamageDefs with no extension; 0 = only patched defs |
| Push downed pawns | toggle | on | |
| Push animals | toggle | on | |
| Push mechanoids | toggle | on | |
| Immune at body size ≥ | 1–5 | 2.5 | |
| Impact damage on hitting a wall / pawn | toggle + per-cell slider 0–15 | on, 4 | |
| Landing stun (ticks) | range | 60–120 | |
| Partial cover stops a push | toggle | on | §9 Q3 |
| Doors take impact damage | toggle | on | |
| Knockback mood thought for humanlikes | toggle | off | JecsTools has one; noise |
| Push into FlowWorks pits | toggle | on | when off, an open pit cell is treated as a wall for the path (no fall) |
| Max pushes per explosion | 1–200 | 40 | performance guard |
| Debug: draw push vectors | toggle | off | dev mode only |
Biome-kit rule: the mechanic is global; no biome gating needed.

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
- Landing in an open D = 4 cell from outside: `RM_Patch_PawnFlyer_LandInPit` → `OnForcedDescent` → fall
  damage; a player pawn is added as a jumper (held; a lowered ladder lets them out); a hostile is captured.
  **No FlowWorks change needed** — the test is whether it fires for our flyer def (it patches the base
  `PawnFlyer.RespawnPawn`, and our def uses thingClass `PawnFlyer`, so it should).
- The path stops **in** the first open pit cell, so nobody is thrown across a pit. Landing on a lowered
  ladder cell still counts as a forced fall (`DescentFalls(walkedStep:false, …)` returns true before it
  reads the ladder) — that is what the ruling says ("blown in → fall").
- Pit covers: a cover is ground. Our pawn lands on it; `CompPitCoverTrigger` sums mass on the deck every
  30 ticks, so a thrown pawn plus those already standing there can spring it. That is emergent and correct;
  a push does not itself break a cover in v1 (§9 Q5).
- A pawn already on a D = 4 cell is **never pushed** in v1 (stagger only; §10 #1) — nobody is blown out of
  a pit or along it, which keeps the owner's "you can't climb out. Period." and FlowWorks' jumper state.
- Liquids: burning tar is walkable, so a blast can throw a pawn into it; FlowWorks' explosion-lights-liquid
  postfix may already have lit that cell. Drowning in a liquid-filled pit is FlowWorks' (`RM_PitDrowning`).
- Sluice doors are doors: closed stops the push with impact.
**Flyers (1.6 flight).** `Pawn.Flying` pawns are skipped in v1. Proof is a state read (the pawn's cell
before/after, `Flying` true) — never an unattended live flight hunt (owner, said three times).
**Gimme Some Slack.**
- Aerial cord spans are already cut by explosions (`Patch_GenExplosion_CutSpans`); independent.
- **Hose carry:** `MakeFlyer` suspends the carrier's job (`InterruptForced`). HoseCarry's table maps
  `Interrupt` on `Carrying` → `Dropped`. Open: the walked-trail rule assumes contiguous steps; a 3-cell
  jump is a gap. Either the hose end drops at the take-off cell (simplest, matches Interrupt), or the trail
  bridges the gap. Needs one runner scene; owner question only if the simple answer looks wrong (§9 Q6).
**Ninefold / Scarlands (Totchak) / FlowWorks liquid fire** hook the same explosion; they read, we move.
Order does not matter because we defer the move to the end of the explosion tick.
**VEF / Melee Animation** patch `PawnFlyer.MakeFlyer`/`RecomputePosition`; both are inactive today but
installed. A load with VEF active is owed before shipping (VEF is in the campaign list in practice).

## 8. The first functional script

Per `design/RimMandrake/debug_process.md` §2: a modcheck `Suite` in
`src/RimMandrake/ExplosiveKnockback/validation.py`, a walk at
`design/validation_walks/RimMandrake/ExplosiveKnockback.md` with `## must be true` lines and coverage
arrows, every setting in `suite.toggles`, and a `--mock` selftest that exits clean first.

### 8.1 Offline kernel tests (pure C#, `Source/SelfTest`, like FlowWorks' `Program.cs`)
`RM_KnockbackMath` is Verse-free: input a small grid fixture (passable / wall / door / partial / pawn /
pit / deep-water / out-of-bounds), centre, radius, force, mass, bodySize, settings; output
`(destCell, cellsTravelled, impact, stopReason)`.
- K-01 distance falls monotonically with distance from centre; 0 at the rim.
- K-02 heavier never travels farther (property test over random masses).
- K-03 bodySize ≥ immune → no move.
- K-04 cells < 1 → no move.
- K-05 never ends on an impassable / door / occupied / out-of-bounds cell (property test, 10k random grids).
- K-06 never passes through a wall, including diagonal corner-cutting.
- K-07 wall stop: impact = perCell × cells not travelled; out-of-bounds stop: impact 0.
- K-08 open pit: stops IN the first pit cell, never beyond; with "push into pits" off, stops before it.
- K-09 held-in-pit pawn never leaves D = 4.
- K-10 epicentre: seeded direction is deterministic for a seed.
- K-11 pawn-pawn: impact split, other pawn not moved.
- K-12 per-explosion cap respected.
Each ruled-out theory from build goes in the walk's `## anti-guessing notes`.

### 8.2 In-game runner scenes
A `jawa/knockback_playtest_*` trio in the style of FlowWorks' `playtest_runner.py`
(start → poll status → collect JSONL journal; verdict re-derived from the file; scratch map only). Each
scene spawns, calls `GenExplosion.DoExplosion` from C#, ticks, reads state:
| Scene | Setup | PASS reads |
|---|---|---|
| open_ground | human 1 cell from a frag centre, open field | moved 1–3 cells away from centre; stunned on landing; alive |
| wall_stop | human with a wall 1 cell behind | did not pass the wall; took Blunt impact (hediff count up) |
| door_stop | closed door behind | same, door HP down |
| pit_colonist | colonist 1 cell from an open D = 4 pit, blast on the far side | in the pit; FlowWorks `RecentDescents` has a forced entry; colonist held (jumper) |
| pit_enemy | hostile, same | in the pit, captured |
| pit_cover | pawn thrown onto a cover rated below its mass | cover springs within 30 ticks |
| no_cross | pit 1 cell wide, 3-cell push | stops inside, never on the far lip |
| heavy | thrumbo-sized animal beside a mortar shell | not moved |
| downed | downed raider beside a blast | moved |
| settings_off | master off | nobody moved; vanilla stagger only |
| flying_skip | a flying pawn (state read `Flying`) | not moved — **state read only**, no screenshot |
| hose_carry | colonist carrying a hose end | hose state = Dropped, no exception |
| save_mid_flight | save while a flyer is in the air, reload | pawn lands once, exists once |
| barrage_perf | 10 shells on 15 pawns | ms per explosion tick under budget; no errors in Player.log |
`pit_*` scenes are the ones that close FlowWorks review row F10 and `FLOWWORKS_PIT_FALL_ONLY_FORCED_1`'s
"forced/blown entry reaches the fall path" check.

## 9. Open questions for the owner

**Q1. Scope: everywhere, or only at pit edges?** The 12:01 card's recommended option was "near the edge";
he later called it a mod. (d) is GPT's staging suggestion (§10).
- (a) **Everywhere** — every blast throws people; pits are one consequence. Biggest change to combat feel;
  needs balance tuning against raids. *(design default)*
- (b) **Only next to pits** — a push happens only if it would end in a pit. Tiny, safe, but "blown back"
  never happens on open ground, which looks odd beside a pit that does it.
- (c) Everywhere but weak (max 1 cell) unless a pit is in the path.
- (d) **Pit-only first, general later** — a 1-cell shove into an adjacent open pit, no flyer, no impact
  damage; ships fast and closes the ruling, then the general mod is a second build.

**Q2. Weapons other than explosions?** His 2026-09-17 words: "weapon blowback".
- (a) Explosions only in v1 *(design default)*; (b) also heavy single shots (a per-weapon extension, e.g.
  shotguns, Star Wars heavy blasters) — more balance work; (c) also melee (hammers, Force push) — VEF
  already has a melee pushback worker we could leave to VEF.

**Q3. Sandbags and barricades.**
- (a) Stop the push, half impact *(default)* — cover protects; (b) pawns are thrown over them — dramatic,
  makes cover worse against explosives; (c) stop and knock the pawn down behind it.

**Q4. Items and corpses.**
- (a) Never *(default)*; (b) corpses only (bodies into pits — cleanup by mortar); (c) everything light —
  most chaos, most cost.

**Q5. Can a blast break a pit cover directly?**
- (a) No, only weight springs it *(default)*; (b) blasts on a cover always break it — makes covers fragile
  against raider grenades; (c) blasts damage covers by HP like any building.

**Q6. Carried hose when the carrier is thrown.**
- (a) The hose end drops where they stood *(default)*; (b) it stays in their hands and the hose stretches
  across the gap.

**Q7. Strength.** A mortar beside a human: (a) 3 cells *(default)*; (b) 1–2 (subtle); (c) 5+ (cinematic).

**Q8. Is it its own mod?** (a) Yes, `mandrake.rm.explosiveknockback` *(default — it works with no pits)*;
(b) a FlowWorks feature — fewer mods, but then it only exists where FlowWorks is loaded.

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

**Accepted as a staging option, put to the owner (Q1):** **#19 smallest version first** — Bomb only,
1-cell outward push, only when that cell is an open pit, by position set + `Notify_Teleported` (the same
route `TryJumpInto` uses, which FlowWorks' tick detector already reads as forced), no flyer, no impact
damage. It sidesteps #5, #6, #8 entirely and closes his stated need. It does not give "blown back" on open
ground.

**Rejected:**
- *"Scope exceeds the demonstrated owner requirement"* as a reason to build only the pit version — he
  called it a mod by name, and balance_paradigm.md already lists knockback as a wanted verb. Scope is his
  call, so it is Q1, not my call either way.
- *Position set as the general route* — for multi-cell pushes it reads as teleporting, and every job/stance
  edge becomes ours. Kept only for the 1-cell staging option.
- *Excluding inventory mass is "a balance choice"* — agreed it is a choice; I keep JecsTools' rule (worn
  gear counts, backpack does not) because a loaded hauler should not become immovable. Not a defect.
