# SUUSH_CAULDRON_DRIFTER_1 — the Suush

## the ask

Owner, at the bench 2026-09-26, verbatim:

> *"Write a ticket in the background for an Aerofleet-like creature (based on its code and
> appearance) that floats around the Cauldron feasting on the strange chemistry of its
> roiling atmosphere and that detonates when you shoot it. Then request the art at high
> priority for a floating spherical entity with hanging "gathering tentacles" like a
> jellyfish. Make it both disturbing and beautiful. Size 2 cells. Docile, tamable,
> bizarre. The Suush."*

**Home biome: the Cauldron** (`RM_PoisonForest`, renamed from "the Poison Forest" by the
owner the same day). Its sheet's own line is that *"'Poison' was a label, not a
mechanism"* — the Suush is a creature that makes the atmosphere the mechanism.

## what it is

A large floating sphere — a gas-filled globe with a curtain of long fine **gathering
tentacles** hanging beneath it, combing the roiling chemical air for the compounds it
lives on. Docile. Tamable. Bizarre. Beautiful and wrong at the same time.

🔑 **The whole creature is one joke with a fuse on it:** it is the least threatening thing
on the map, and it is full of volatile gas. It never attacks. It drifts. And if you shoot
it, it goes off.

## grounding — the real Aerofleet, MEASURED 2026-09-26

He named the Aerofleet as the basis, so this is what it actually is, read off
`Races_Aerofleet.xml` in Alpha Animals (workshop `1541721856`) — not from memory:

| field | Aerofleet |
|---|---|
| label / description | *"A small, floating gelatinous creature. Propelled by the hydrogen it collects from water and various plant matter, these squishy creatures wander the lands, aimlessly bouncing off objects in their path."* |
| `baseBodySize` | 0.2 |
| `wildness` | 0.60 |
| `trainability` | **None** |
| `foodType` | VegetarianRoughAnimal |
| body part | has a literal `tentacles` part |
| comps | `CompProperties_Floating`, `CompProperties_AsexualReproduction`, `CompProperties_AnimalProduct`, `AnimalStatExtension` |

⇒ The shape to copy is **`CompProperties_Floating` + asexual reproduction + an animal
product**, and the fiction to copy is **a creature propelled by gas it collects from its
environment**. The Suush swaps hydrogen-from-plants for the Cauldron's atmospheric
chemistry, and adds the detonation.

🔴 **Those comps are `AnimalBehaviours` / VEF — a DONOR framework.** Two of the three
copies on disk are namespaced `VEF.AnimalBehaviours.*` and one `AnimalBehaviours.*`, so
the namespace differs by mod version — **do not guess it, read the deployed DLL**.
⚠️ And `DONOR_DEFS_PORT_TO_OURS_1` is the standing direction of travel, so prefer **our own
floating comp** over taking a new dependency for a brand-new creature. Check `src/` first:
this project keeps having already built the thing.

## the three things to get right

### 1. It floats
Ours, not borrowed, if we can. See above.

### 2. It feeds on the atmosphere, not on plants
The Aerofleet eats plant matter. The Suush eats the **Cauldron's roiling chemistry** —
that is the point of siting it there and the reason it is full of something explosive.
⇒ Not `VegetarianRoughAnimal`. Whatever food route expresses "grazes the air" is the
design question; the gathering tentacles are the fiction for how.

### 3. It detonates when shot
⚠️ **He said shot, not killed** — and those are different mechanisms. Vanilla's boomalope
uses a death action (`DeathActionWorker_BigExplosion`); "when you shoot it" suggests the
trigger is **damage**, which is `CompExplosive`'s territory. Decide deliberately:
- **death-triggered** is the vanilla-faithful, zero-surprise route (boomalope precedent);
- **damage-triggered** is closer to his words and much nastier, because a stray shot in a
  firefight sets it off.
🔑 Either way the interesting consequence is the same: **a docile tamable animal that a
careless colonist can turn into a bomb.** Do not lose that by making it aggressive.

## fields he specified
- **Size 2 cells** → `drawSize` 2.0. (`baseBodySize` is a separate field and is NOT the
  same thing — the Aerofleet's is 0.2. Set them independently and deliberately.)
- **Docile** — never a manhunter, no attack verbs worth the name.
- **Tamable** — 🔴 the Aerofleet is `trainability: None`; the Suush must not simply copy
  that. **Verify in the engine what taming actually requires before setting it** — read
  the tame designator/recruit path rather than assuming, since `TrainableUtility` governs
  training rather than taming and does not settle it.
- **Bizarre** — the art brief carries this; the def carries it in the description.

## art — QUEUED, high priority, 2026-09-26
Three facings at **priority 20**, ahead of all 320 then-pending jobs (the queue sorts
ascending and nothing else was below 100):

`cauldron_suush_north` · `cauldron_suush_east` · `cauldron_suush_south`

512×512, transparent, drawsize 2.0, `rimflow_item_id` SUUSH_CAULDRON_DRIFTER_1. Brief:
translucent gas-filled globe lit from within, many long fine hanging gathering filaments,
**beautiful and disturbing at once**, no face/eyes/mouth/limbs. Oversize canvas recorded
with its reason — the read depends on filament detail that dies at 256. West mirrors east.
✅ Checked first: **zero** existing Suush art anywhere in `infrastructure/artpipe/`.

## criteria
- [x] Floating mechanism resolved — ours if it exists, donor only with a reason.
- [x] Atmosphere-feeding expressed, not plant grazing.
- [x] Detonation trigger ruled: damage vs death, deliberately, and written down.
- [x] Docile and genuinely tamable, verified against the engine not assumed.
- [x] Cast into the Cauldron's roster; solitary vs group decided.
- [x] Art wired when the three facings land.

## build resolution — FOUNDRY, 2026-09-26

Built, not just designed. `src/RimMandrake/PoisonForest/Defs/ThingDefs_Races/
RM_PoisonForestFauna.xml` (new file, full header comment carries every
citation below) + one line added to `RM_PoisonForest.xml`'s `<wildAnimals>`.

- **Floating: CORE 1.6's own flight system, not VEF's `CompProperties_Floating`
  and not new C#.** `MaxFlightTime` 600 / `FlightCooldown` 1 /
  `flightStartChanceOnJobStart` 1.0 / `canFlyIntoMap` true — the exact fields
  CLAUDE.md's flight section documents, MEASURED against
  `RimWorld/Pawn_FlightTracker.cs` this pass (`Notify_JobStarted` rolls flight
  at every job start; `MaxFlightTicks` from the stat governs how long before a
  forced landing). Reads as continuously airborne at normal play timescales
  without touching render code. `body: Bird` — reused rather than invented,
  because it is the exact body vanilla's own Chicken/Duck/Goose/Sparrow already
  prove compatible with these same flight fields (the Anomaly `Nociosphere`
  body was considered and rejected: built for a `doesntMove=true` stationary
  entity, risking the "Moving" capacity outright).
- **Feeds on atmosphere: `foodType: None`**, not `VegetarianRoughAnimal`.
  `RaceProperties.EatsFood => foodType != FoodTypeFlags.None` (MEASURED) — no
  Food need at all, no foraging, no colonist ever feeds it. Existing vanilla
  pattern, no new mechanic invented.
- **Detonation: damage-triggered, not death-triggered — "shot", per the
  owner's own word.** Vanilla core `CompProperties_Explosive` (no new C#),
  `startWickOnDamageTaken: [Bullet, Bomb]` — ranged/explosive damage starts the
  fuse immediately, before it is anywhere near dead. `explodeOnKilled: true` as
  a backstop so however it actually dies, it goes up regardless.
  `postExplosionGasType: ToxGas` ties the blast back to the fiction (it is
  full of the same chemistry it feeds on). Judgment call, not an owner ruling:
  reversible without ceremony.
- **Tameable: verified against `TameUtility.CanTame` and
  `Pawn_TrainingTracker.CanAssignToTrain`, both MEASURED this pass.** Taming
  gates on `Wildness < 1` + `Animal` + faction null, NOT on `trainability` —
  so `trainability: None` (matching the Aerofleet) does not block taming, only
  trick training. `Wildness` statBase 0.5.
- **Docile: `predator: false`, `manhunterOnDamageChance: 0`,
  `manhunterOnTameFailChance: 0`, no `<tools>` at all** — it cannot attack even
  if it wanted to.
- **Cast: solitary** (`wildGroupSize: 1`, `herdAnimal: false`) at commonality
  0.2 in `RM_PoisonForest.xml`'s inline `<wildAnimals>` (RM tier, no
  `MayRequire`, no Utinni patch layer — Q11a, invented names). This build's own
  call, not an owner ruling.
- **Art: already generated and VALIDATED (pass) before this build started**
  (`infrastructure/artpipe/done/cauldron_suush_{north,east,south}.json` +
  `.manifest.json`, `registry.jsonl` `validated`/`pass` events, timestamped
  2026-09-26T17:35Z, priority 20) — verified myself, not taken on trust.
  Deployed unchanged to
  `src/RimMandrake/PoisonForest/Textures/Things/Pawn/Animal/RM_Suush/
  RM_Suush_{north,east,south}.png`, wired via `Graphic_Multi` (west mirrors
  east). No second art job filed.
- **Not done / left for a later pass:** no dessicated-corpse graphic (omitted,
  same as this biome's other single-facing natives); no bespoke butcher
  product (MeatAmount/LeatherAmount 0, matching the Blue Desert native
  convention); the frozen campaign twin `RUT_PoisonForest` was NOT touched —
  this creature lives only in the standalone `RM_PoisonForest` mod, per the
  item's own "Home biome: RM_PoisonForest" framing; wiring it into the frozen
  campaign world too is a separate future call if the owner wants it there.
