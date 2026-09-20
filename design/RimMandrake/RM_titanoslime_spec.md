<!-- status: design spec — nothing here is built. Item: TITANOSLIME_SLIME_BIOME_1 (BENCH, kind design;
     a FOUNDRY build pass closes it). Every engine claim is MEASURED from the RimWorld 1.6 decompile
     via RimSage on 2026-09-20 unless tagged [INVENTED] (a number chosen here, tune at build) or
     [VERIFY AT BUILD] (a seam named here that the build must read once before wiring). -->
# The Titanoslime — `RM_Titanoslime`, the Slime's own mouth

_Design spec, 2026-09-20, Fable pass backgrounded from BENCH. Answers every decision point in
`infrastructure/state/items/TITANOSLIME_SLIME_BIOME_1.md` so that a FOUNDRY build needs
implementation decisions only. Format precedent: `RM_gelatinous_slime_mod.md` (the mod this
creature joins) and `design/Jawa/worldbuilding/creatures/RUT_hydrocarbon_ecology_commission.md`._

**The ask (owner, verbatim, 2026-09-20):** *"For the slime biome, I am now enchanted by the idea
of a titanic green slime. So make one of those too as its own custom creature. The Titanoslime. It
should have the devoured ability to swallow pawns whole of nearly any size. And I have a question.
Is it possible to have a creature that gets larger as it eats?"* — Yes, and the route chosen below
is cheaper and safer than the one the item sketched: **no Harmony patch at all.**

## 0. The one-paragraph version

A titanoslime is a hill of glassy green jelly that hunts by rolling over things. It is a wild
predator of the Slime biome, rare (one or two per map over a season), placid until it is hungry or
hurt, and it grows in five visible stages — from a 2×2 mound the size of a thrumbo to a 4×4
colossus forty times a human's mass — by absorbing what it swallows. **Growth is the vanilla
life-stage system with the stage index locked by our comp** (`Pawn_AgeTracker.LockCurrentLifeStageIndex`,
public, scribed): each stage is a `LifeStageDef` carrying its own `bodySizeFactor`,
`healthScaleFactor`, `meleeDamageFactor`, `foodMaxFactor` and a `PawnKindDef` life-stage
`drawSize`, so mass, health, damage, hunger, sprite, RimMandrake Titanic tier, Large Pawns
footprint and the T3 corpse-site all follow one number. **Swallowing is a melee tool** whose
`ManeuverDef` runs our `Verb_MeleeAttack` subclass: on a hit that passes the size gate the target
is despawned into the slime's `IThingHolder` container (the `CompDevourer` hold shape, rewritten
so it needs no Anomaly defs, holds several things, and feeds the growth counter). A held pawn is
digested on a timer scaled by its body size, drops out stunned and acid-burned if the slime is
downed or killed first, and is **absorbed — no corpse, gear regurgitated — when the timer ends.**
The slime's own mass leaks away when it starves, when it leaves slime terrain, and when it is hurt
(it sheds gelatids), so the ladder runs both ways and nothing is one-way permanent.

## 1. Identity and home

| surface | value |
|---|---|
| tier | **RimMandrake** — a titanic slime has nothing Star Wars in it; passes the tier test in `design/NAMING_SCHEME_PLAN.md` |
| mod | `mandrake.rm.gelatinousslime` — `src/RimMandrake/GelatinousSlime/` (this is the universal Slime biome mod; the creature is part of that biome) |
| defNames | ThingDef + PawnKindDef `RM_Titanoslime`; LifeStageDefs `RM_TitanoslimeStage1`…`5`; BodyDef `RM_AmorphousBody`; ToolCapacityDef + ManeuverDef `RM_Engulf`; comp `RM_CompEngulfer` / `RM_CompProperties_Engulfer`; verb `RM_Verb_MeleeEngulf` |
| C# namespace | `RimMandrake.GelatinousSlime` (same assembly as `SlimeExposure.cs`; reuses `SlimeUtility`, `SlimeDefs`, `SlimeSettings`) |
| label | *titanoslime* — stage labels in §3 |
| campaign wiring | `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml` `wildAnimals` + `design/Jawa/worldbuilding/biomes/rosters/the_slime.json` (§6) |
| DLC | none. ⛔ Do NOT reuse vanilla `CompDevourer`/`ConsumeLeap_Devourer`/`DevourerDigest`/`DevourerDigesting`: the class is in the core assembly but every def it references (`JobDefOf.DevourerDigest`, `AnimationDefOf.DevourerDigesting`, `AbilityDefOf.ConsumeLeap_Devourer`, `PawnFlyer_ConsumeLeap`) is `Defs/Anomaly/` content — MEASURED. The mod is base-game and stays so. §4 is the rewrite. |
| ecosystem | rides `mandrake.rm.titaniccreatures` (tier/wake/corpse-site) and `neku.largepawns` (footprint) **when present**, by construction: both key off `pawn.BodySize` at runtime (`TitanicTierUtility.GetTier` reads `pawn.BodySize`; Large Pawns' `GetSize` reads `pawn.BodySize` once `bodySizeFactor > 1`, per `research/large_pawns_decompile_2026-09-09.md` §resolution-order). Absent either, it degrades to a single-cell pawn with a big sprite. No reference to either assembly. |

**Why it belongs in the biome sheet's world.** `the_slime.md` §1 names the body's imperative —
*"forever seeking to ingest, analyze, recombine, store, and multiply"* — and §4 evicted the
Harvester because *"a healthy-looking apex violates the reading-body identity."* The titanoslime is
not a foreign apex that happens to live here: it is **a lobe of the body that has learned to go
and fetch entries.** Nothing it swallows is eaten in the animal sense; it is read, and what is
read is returned to the flow. That is why absorption leaves no corpse (§4.4), why the released
carry slimification (§4.5), why it sheds gelatids when cut (§3.4), and why it is *resistant by
identity* (`SlimeResistantExtension`, like the gelatid). Hard bans honoured: no sentience (it is an
animal on the vanilla think tree with no intent beyond hunger — ban 1), no re-arming (a predator
is not weapon generation — ban 7), resistant resident (ban 5).

## 2. Growth — the mechanism, exactly

### 2.1 The engine seam (MEASURED, `Verse/Pawn_AgeTracker.cs`)

- `public void LockCurrentLifeStageIndex(int index)` sets `lockedLifeStageIndex` and calls
  `RecalculateLifeStageIndex()`. While locked, `RecalculateLifeStageIndex` uses the locked index
  in place of the growth/age lookup, and `AgeTickInterval` **returns early** after ticking raw
  age — no natural growth, no `BirthdayBiological`, no age-reversal demand. `lockedLifeStageIndex`
  is scribed (`ExposeData`: `Scribe_Values.Look(ref lockedLifeStageIndex, "lockedLifeStageIndex", -1)`),
  and on `PostLoadInit` the cached index is reset to `-1`, so the locked stage survives save/load
  with no work from us.
- On a stage change `RecalculateLifeStageIndex` itself calls `pawn.Drawer.renderer.SetAllGraphicsDirty()`
  (new `drawSize`/texture take effect), `CurLifeStage.Worker.Notify_LifeStageStarted`, and
  `PawnComponentsUtility.AddAndRemoveDynamicComponents`.
- `Pawn.BodySize => ageTracker.CurLifeStage.bodySizeFactor * RaceProps.baseBodySize` (item's own
  measurement) — so the locked stage IS the body size.
- `PawnRenderNode_AnimalPart` draws `pawn.ageTracker.CurKindLifeStage.bodyGraphicData` at that
  stage's `drawSize` verbatim (`creature_size_model.md` §1, MEASURED) — so the locked stage IS the
  sprite size. `CurKindLifeStage` indexes `kindDef.lifeStages[CurLifeStageIndex]`: the PawnKindDef
  MUST carry exactly five `lifeStages` in the same order as the race's five `lifeStageAges`.
- `LifeStageDef` fields available per stage (MEASURED, `RimWorld/LifeStageDef.cs`): `bodySizeFactor`,
  `healthScaleFactor`, `hungerRateFactor`, `foodMaxFactor`, `meleeDamageFactor`, `marketValueFactor`,
  `statOffsets`, `statFactors`, `bodyWidth`, `voxPitch`, `developmentalStage`, `reproductive`.
  [VERIFY AT BUILD] that `StatWorker.GetValueUnfinalized` applies `CurLifeStage.statFactors` for
  `MoveSpeed` (expected: yes, this is the baby-crawl mechanism); if it does not, the per-stage
  MoveSpeed factor moves into a per-stage hediff and nothing else changes.
- Spawn: `PawnGenerator.GenerateRandomAge` rolls an age from the race curve, but the comp's
  `PostSpawnSetup(respawningAfterLoad: false)` locks the stage from its own state (§2.3) before
  the first tick, so generated age is irrelevant. Set `lifeStageAges` minAges to 0 / 100 / 200 /
  300 / 400 years and `lifeExpectancy` 1000 so nothing age-driven ever fires even if a lock were
  lost; while locked, birthdays do not fire at all.

### 2.2 The ladder — five stages, one number

`baseBodySize` **6**, `baseHealthScale` **6** [INVENTED]. Titanic tier thresholds are the live
`RM_TitanicTiers_Default` (T1 ≥ 4, T2 ≥ 8, T3 ≥ 20). `drawSize` is the honest render for each mass
by `creature_size_model.md` §2's vanilla law (`1.995·bs^0.375`), rounded up a little because a
slime is wider than it is tall — every stage sits inside the 0.67–1.5 "no badge" band.

| stage | label | `bodySizeFactor` | BodySize | `healthScaleFactor` (→ scale) | `meleeDamageFactor` | MoveSpeed factor | `foodMaxFactor` | `drawSize` | tier | Large Pawns |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | young titanoslime | 1.00 | 6 | 1.0 (6) | 1.0 | 1.00 | 1.0 | 4.0 | T1 | 2×2 |
| 2 | titanoslime | 1.67 | 10 | 1.5 (9) | 1.25 | 0.90 | 1.5 | 5.0 | T2 | 3×3 |
| 3 | great titanoslime | 2.67 | 16 | 2.2 (13.2) | 1.5 | 0.80 | 2.2 | 6.0 | T2 | 3×3 |
| 4 | elder titanoslime | 4.00 | 24 | 3.0 (18) | 1.8 | 0.70 | 3.0 | 7.5 | T3 | 4×4 |
| 5 | titanoslime colossus | 6.67 | 40 | 4.0 (24) | 2.2 | 0.60 | 4.0 | 9.0 | T3 | 4×4 |

All factors [INVENTED]; the *shape* (mass ×6.7 across the ladder, health ×4, damage ×2.2, speed
÷1.7) is the design: bigger is much harder to kill and hits harder but is slower, and the T3 line
at stage 4 is where the destruction wake and the corpse-site begin — a stage-4 titanoslime
walking through a wall is the Titanic Creatures mod doing exactly what it was built for.
Stage-1 BodySize 6 is chosen so that the smallest titanoslime already qualifies as titanic
(`TitanicTierUtility.DefQualifies` reads `race.baseBodySize >= 4` at def load to attach the wake
comp — MEASURED — and would silently skip the race if the base were below 4).

### 2.3 The growth counter — `absorbedMass` (float, scribed on the comp)

Stage is a pure function of `absorbedMass`, evaluated whenever it changes:

| to reach stage | `absorbedMass` ≥ | drops back below |
|---|---|---|
| 2 | 4 | 3 |
| 3 | 12 | 11 |
| 4 | 28 | 27 |
| 5 | 60 | 59 |

(1-unit hysteresis so a single shed cannot flip a stage twice; clamp at **80** so a colossus can
lose a fight's worth of mass before dropping.) All thresholds [INVENTED]; the shape is geometric —
four humans make a stage-2, a stage-5 has eaten the mass of ten thrumbos. **Mod setting
`titanoslimeMaxStage` (1–5, default 5)** caps the evaluation. Units are body-size units (1.0 = an
adult human), the same scale as `Pawn.BodySize`.

Sources, all in the comp, no patches:

| source | change | mechanism |
|---|---|---|
| **absorbed a held pawn** (§4.4) | `+ prey.BodySize` | direct, on completion |
| **ordinary eating** — corpses, raw slime, slime-grass, anything it grazes | `+ 0.25 × nutrition` [INVENTED] | poll `pawn.records.GetValue(RecordDefOf.NutritionEaten)` every 250 ticks and add the delta; the record is vanilla, scribed, and incremented by every ingestion path — no ingestion hook needed |
| **starving** (`pawn.needs.food.CurCategory == HungerCategory.Starving`) | `− 1.0 per day` (accrued per 2500 ticks) [INVENTED] | it lives off itself |
| **off the body** — no slime terrain (`SlimeDefs.SlimeRich`/`SlimeGrass`/`SlimeLiquid` or the campaign's `AB_*` slime terrains via a def list in props) within 3 cells, continuously for > 1 day | `− 0.5 per day` [INVENTED] | the same law as §4 of the mod spec: it cannot live dry. A titanoslime that wanders off the biome edge or is lured onto a stone floor slowly deflates |
| **shedding** (§3.4) | `− 1.0 per gelatid` | on damage |

Wild spawn rolls a starting `absorbedMass` in `PostSpawnSetup(!respawningAfterLoad)`: 60 % → 0
(stage 1), 30 % → 4 (stage 2), 10 % → 12 (stage 3), never 4–5 [INVENTED]. Stages 4 and 5 are only
ever *earned on the player's map*, so the player has watched it happen.

On stage-up: `Messages.Message` ThreatSmall for stage 2–3 (*"The titanoslime has grown."*, only
if it is within the colony's view); `LetterDefOf.ThreatBig` for stage 4 and 5 (*"An elder
titanoslime"* / *"A titanoslime colossus"*, with the growth fleck `FleckDefOf.PsycastAreaEffect`-class
green pulse [VERIFY AT BUILD — pick any Core fleck; never gate on Anomaly]). On stage-down: no
message; the inspect string (§5) carries the state.

## 3. The body

### 3.1 Race (`ThingDef RM_Titanoslime`, `ParentName="AnimalThingBase"`)

| field | value | why |
|---|---|---|
| `race.body` | `RM_AmorphousBody` (§3.2) | no organs to fail; a nucleus to kill |
| `race.baseBodySize` / `baseHealthScale` | 6 / 6 | §2.2 |
| `race.baseHungerRate` | 2.0 [INVENTED] | a big eater (thrumbo 1.75) — hunger drives the hunt |
| `race.foodType` | `OmnivoreAnimal` [VERIFY AT BUILD the flag set includes `Corpse`; if not, `OmnivoreAnimal, CarnivoreAnimal`] | grazes slime-grass and raw slime between hunts, eats corpses it finds |
| `race.predator` / `maxPreyBodySize` | true / **20** | `FoodUtility.IsAcceptablePreyFor` gates on this static field (MEASURED); the live gate is the engulf verb's (§4.2) |
| `race.canBePredatorPrey` | false | nothing hunts it |
| `race.manhunterOnDamageChance` | 1.0 | hurt it and it comes for you — the thrumbo posture, and the route by which colonists become prey on difficulties where `predatorsHuntHumanlikes` is false (§6) |
| `race.wildness` (`statBases.Wildness`) / `trainability` | 1.0 / `None` | never tamed, never a pet |
| `race.herdAnimal` / `wildGroupSize` | false / `1~1` | solitary |
| `race.hasGenders` | false | it buds, it does not breed — no gestation, no litter curve |
| `race.lifeExpectancy` / `lifeStageAges` | 1000 / five entries, minAge 0 / 100 / 200 / 300 / 400 | §2.1 |
| `race.hediffGiverSets` | (none) | no age or organ hediffs |
| `race.bloodDef` | `RM_SlimeSmear` (the mod's `SlimeDefs.SlimeSmear`) [VERIFY AT BUILD it is a filth def; else `Filth_Slime`] | it leaks |
| `race.specificMeatDef` | `RM_RawSlime` | **verified vanilla shape**: `Devourer` sets `specificMeatDef Meat_Twisted` (MEASURED). ⚠️ This overturns the comment in `Defs/ThingDefs_Races/Gelatid.xml` claiming *"no vanilla animal sets meatDef to a hand-authored def"* — that comment is false and the build fixes it while there |
| `race.leatherDef` | (none) — `LeatherAmount` 0 | |
| `statBases` | `MoveSpeed` 2.4 [INVENTED]; `ComfyTemperatureMin` **5**, `ComfyTemperatureMax` 45; `Flammability` 0.15; `ArmorRating_Sharp` 0.45, `ArmorRating_Blunt` 0.15, `ArmorRating_Heat` 0; `MarketValue` 0; `MeatAmount` 300 (raw slime from a stage-1 corpse; ×BodySize via `StatPart_BodySize`) | slow and cold-soft: blades slide through jelly, clubs and cold work. Nights in the Slime (p10 3 °C) push it below comfort — it slows and takes hypothermia, the biome's own leash on it. Not flammable-wet, but fire is not its counter |
| `comps` | `RM_CompProperties_Engulfer` (§4); `RM_TitanicExtension` NOT needed (auto by bodySize) | |
| `modExtensions` | `RimMandrake.GelatinousSlime.SlimeResistantExtension` | resistant by identity, like the gelatid |
| `tools` | §3.3 | |
| sounds | `soundCall` none (the biome is silent by ruling — sheet §9); `soundWounded`/`soundDeath` `Pawn_Tortoise_*` (the gelatid's, Core); melee `Pawn_Melee_BigBash_*` | never `Pawn_Devourer_*` (Anomaly) |
| `uiIconScale` | 2.0 | |
| `tradeTags` | (none); `tradeability None` | |

### 3.2 `BodyDef RM_AmorphousBody`

Three parts, no limbs to lose [VERIFY AT BUILD against a simple Core body such as
`Bodies_Animal_Insect.xml`'s megascarab for the exact `BodyPartRecord` shape]:

- `RM_SlimeMass` — core, coverage 1.0, `BodyPartDef` with `hitPoints` 80, groups `Torso`,
  `RM_Maw` (the engulf tool links here, `ensureLinkedBodyPartsGroupAlwaysUsable`).
  - `RM_Nucleus` — coverage 0.12, `hitPoints` 40, tag `BloodPumpingSource` **and**
    `ConsciousnessSource` so its destruction kills the pawn (the one vital); `depth Inside`.
  - `RM_Pseudopod` ×2 — coverage 0.16 each, `hitPoints` 40, group `RM_Pseudopods`, `depth Outside`;
    destroying one halves melee output (both slam tools link here) but does not down it.
- No `SightSource`, no `HearingSource`, no `Legs` group: the biome's art law says never eyes, and a
  body with no eyes must not carry a sight part. `MoveSpeed` is unaffected by part loss.

### 3.3 Melee tools (`tools`)

| label | capacity | power | cooldown | AP | linked group | chanceFactor | note |
|---|---|---|---|---|---|---|---|
| engulfing mass | `RM_Engulf` | 12 (fallback slam when the gate fails) | 3.0 | 0.1 | `RM_Maw` | 1.0 | **the swallow** — §4 |
| left pseudopod | `Blunt` | 14 | 2.2 | 0.15 | `RM_Pseudopods` | 0.7 | |
| right pseudopod | `Blunt` | 14 | 2.2 | 0.15 | `RM_Pseudopods` | 0.7 | |

All [INVENTED]; scaled per stage by `meleeDamageFactor` (§2.2), so a colossus slams for ~31.
`ToolCapacityDef RM_Engulf` + `ManeuverDef RM_Engulf` copy the vanilla `KickMaterialInEyes` /
`Verb_MeleeApplyHediff` shape (MEASURED, `Defs/Core/Maneuvers/Maneuvers.xml`): `requiredCapacity`
`RM_Engulf`, `verb.verbClass` `RimMandrake.GelatinousSlime.RM_Verb_MeleeEngulf`, `logEntryDef`
`MeleeAttack`, and the four `combatLogRules*` pointing at our own tiny `RulePackDef`s
(*"engulfs"*, *"slides off"*, *"misses"*, *"is dodged by"*) — or, if RulePack authoring is not
worth the hour, at `Maneuver_Bite_*` verbatim; the log wording is not load-bearing.

### 3.4 Shedding — the release valve

While at stage ≥ 2, track damage taken (`PostPostApplyDamage`, the seam `RM_CompGrappler` already
uses); every time the running total crosses another **12 % of `MaxHitPoints`** [INVENTED]: spawn one
wild `RM_Gelatid` on a free adjacent cell (`GenSpawn.Spawn`, faction null), throw a green burst
fleck, subtract 1.0 `absorbedMass`. Reset the running total on each shed. The colossus you are
fighting comes apart into the herd animals of the biome as you cut it — and loses a stage every
few gelatids. Mod setting `titanoslimeSheds` (default on). Never sheds while held things are
inside and it is below 25 % health (the fight is nearly won; don't spawn clutter on the drop).

## 4. The swallow — `RM_CompEngulfer` + `RM_Verb_MeleeEngulf`

**What carries over from the Sarlacc spec's `CompDevourer` reading, and what does not:**

| Sarlacc / vanilla Devourer | Titanoslime |
|---|---|
| despawn + `IThingHolder` container, `LookMode.Deep`, `removeContentsIfDestroyed: false`, `Scribe_Deep` — the hold pattern | **carried verbatim** (it is the correct save-safe shape) |
| one held thing | **N held things** — capacity `max(1, floor(BodySize / 4))`: 1 / 2 / 4 / 6 / 10 by stage |
| triggered by an `AbilityDef` leap (`Verb_CastAbilityJump` + `PawnFlyer`) chosen by `JobGiver_AIAbilityFight` on an always-violent entity | **triggered by a melee tool** through the ordinary predator hunt and ordinary fights (§4.1) — no ability, no flyer, no custom think tree |
| the devourer sits in a `DevourerDigest` job and plays `DevourerDigesting` for the whole hold | **no job** — digestion runs in `CompTick`; the slime keeps hunting, fleeing or wandering with its cargo, and the player chases it |
| `maxBodySize` 2.5 static gate | **relative gate** `prey.BodySize ≤ own BodySize × 0.5` (§4.2) — "nearly any size" is earned by growing |
| completion = 200 AcidBurn then regurgitate (usually a corpse) | completion = **absorption**: killed, corpse destroyed, gear dropped, mass gained (§4.4) |
| hold is same-map, rescue by killing the holder | **carried**, plus downed; plus §4.3 struggle and burst-out |
| "being swallowed is a route in" to a pocket map | **does not transfer** — there is no pocket map; the item flagged this and it is confirmed dropped |

### 4.1 Who gets swallowed, and when — the AI stays vanilla

The titanoslime uses the vanilla `Animal` think tree. Two paths reach the engulf tool:

1. **Hunting.** As a `predator`, when hungry it runs `JobGiver_PredatorHunt` → `JobDriver_PredatorHunt`,
   whose hit toil calls `pawn.meleeVerbs.TryMeleeAttack(prey, …)` (MEASURED). Melee verb
   selection weights tools by `chanceFactor`; when the engulf tool is picked and hits, the verb
   swallows instead of damaging. Prey selection is vanilla `FoodUtility.IsAcceptablePreyFor`:
   `canBePredatorPrey`, `IsFlesh`, `BodySize ≤ maxPreyBodySize (20)`, `prey.combatPower ≤ 2 ×
   predator.combatPower`, and the `combatPower × health × BodySize` comparison — with
   `combatPower` 900 [INVENTED] on the kind, every wild animal and every colonist passes.
   ⚠️ `Find.Storyteller.difficulty.predatorsHuntHumanlikes` is respected (MEASURED gate) — on
   difficulties where it is false the slime hunts animals only; colonists become prey through
   path 2. This is left as vanilla behaviour deliberately: it is the player's own setting.
2. **Fighting.** Manhunter (100 % on damage), `JobGiver_ReactToCloseMeleeThreat`, and any melee
   exchange use the same tool set. Attack it in melee and it swallows the attacker; shoot it and
   it charges and swallows the shooter. This is where *"swallow pawns whole"* is felt.

`RM_Verb_MeleeEngulf : Verb_MeleeAttack` overrides `ApplyMeleeDamageToTarget(LocalTargetInfo)`
[VERIFY AT BUILD the exact override name/signature against `Verb_MeleeAttackDamage` /
`Verb_MeleeApplyHediff`; both are ~30-line subclasses and one of them is the template]. If the
target is a `Pawn` and `comp.CanEngulf(target)` → `comp.Engulf(target)`, return an empty
`DamageWorker.DamageResult`; else → deal the tool's 12 Blunt exactly as `Verb_MeleeAttackDamage`
would (the fallback slam).

### 4.2 `CanEngulf(Pawn p)` — the gate

All must hold: `titanoslimeEngulfs` setting on · `p.Spawned && !p.Dead` · `p.RaceProps.IsFlesh`
(mechanoids are slammed, never swallowed) · `p.BodySize ≤ self.BodySize × 0.5` · held count <
capacity · `p` not already held by anyone · `p` is not another `RM_Titanoslime` at the same or
higher stage (a colossus may absorb a young one — the database reabsorbs its experiments — but
equals cannot eat each other).

What that means at the table: stage 1 (bs 6) swallows anything up to bs 3 — every humanlike,
muffalo, boomalope; stage 3 (bs 16) swallows up to bs 8 — elephants, thrumbos, megasloths; stage 5
(bs 40) swallows up to bs 20 — the Krayt (bs 12), the war wyrm (bs 15), an elder titanoslime.
*Nearly any size*, and the ladder is the reason to let one grow.

### 4.3 Inside — hold, struggle, burst

`Engulf(p)`: notify `p`'s lord (`Notify_PawnDamaged` with a 99 AcidBurn `DamageInfo`, the
Devourer's trick so raid lords react — MEASURED), remember `drafter.Drafted`, `p.DeSpawn()`,
`innerContainer.TryAdd(p)`, push `ticksHeld = 0` and `digestTicks = ceil(bodySizeDigestTimeCurve
.Evaluate(p.BodySize) × 60)` onto the parallel lists (scribed), set food need to max, throw the
engulf sound (`Pawn_Melee_BigBash_HitPawn`), and if `p.Faction == Faction.OfPlayer` message
NegativeEvent *"{PAWN} was swallowed whole by the titanoslime! Down it before it finishes."*

`bodySizeDigestTimeCurve` [INVENTED], seconds: (0.2 → 20) (1 → 75) (2.5 → 150) (5 → 240) (10 → 400).
A colonist has 75 s ≈ 4500 ticks ≈ 1.8 in-game hours: a real rescue window against a stage-1's
6-scale health, a hard one against a stage-4.

Every 120 ticks, per held pawn `h` that is alive and not downed:

- **struggle**: `self.TakeDamage(Blunt, 2 + meleeSkill/4 (humanlike) or 2 × h.BodySize (animal),
  armorPenetration 1.0, instigator h, hitPart RM_SlimeMass)` — thrashing inside counts as damage,
  feeds §3.4 shedding, and a swallowed squad can burst a young titanoslime from within;
- **burst-out roll**: `chance = clamp((h.BodySize / self.BodySize − 0.15) × 0.25, 0, 0.10)` per
  round [INVENTED]: a human inside a stage-1 has 0.4 %/round (~14 % over a full digestion); a
  muffalo inside a stage-1 has 6 %/round and is usually out within a minute; nothing bursts out of
  a colossus. On burst: release (§4.5) with the acid damage for time held.

Held things do not tick (the Devourer's hold does not tick contents either — MEASURED by
absence): needs freeze, bleeding freezes, so a swallowed colonist neither starves nor bleeds out
inside — the acid on exit is the whole cost of time.

### 4.4 Completion — absorbed

When `ticksHeld ≥ digestTicks`: drop the pawn's apparel and equipment on the slime's cell
(`apparel.DropAll`, `equipment.DropAllEquipment` — the plasteel armour is not digestible; the
reader is), `h.Kill(DamageInfo AcidBurn 9999, instigator self)`, then `h.Corpse.Destroy()` (no
corpse — *returned to the flow*, exactly the mod's stage-4 slimification outcome), spawn one
`RM_SlimeSmear` filth, `absorbedMass += h.BodySize`, re-evaluate stage (§2.3). If `h.Faction ==
Faction.OfPlayer`: `LetterDefOf.Death`-class letter *"{PAWN} was absorbed by the titanoslime.
There is nothing to bury."* Colonist death handling (thoughts, relations) is vanilla `Kill`.

### 4.5 Release — downed, killed, burst, or the setting turned off

`Notify_Downed` and `Notify_Killed(prevMap)` (both `ThingComp` overrides the Devourer uses —
MEASURED) → `ReleaseAll(map)`: for each held thing, `innerContainer.TryDrop(…, PositionHeld, map,
ThingPlaceMode.Near)` with the Devourer's fallback to `RCellFinder.TryFindRandomCellNearWith` +
`GenSpawn.Spawn`; then `stances.stunner.StunFor(60)`, restore `Drafted`, apply AcidBurn
`timeDamageCurve.Evaluate(ticksHeld / 60)` with `SetApplyAllDamage(true)`; `timeDamageCurve`
[INVENTED] (0 s → 4) (60 s → 24) (150 s → 45). Then, unless the pawn carries
`SlimeResistantExtension`, bump `RM_Slimification` severity by **+0.15** through `SlimeUtility`
(it was inside the body; stage 1 → stage 2 of the ladder, which no longer self-reverses — the
mod's own clock is now running on the rescued). Message NeutralEvent *"{PAWN} emerged from the
titanoslime"* / *"…from the titanoslime's remains"*. Stage-4/5 death converts to a Titanic
corpse-site; `Notify_Killed` runs before that conversion (it runs on the pawn's death, the
conversion patches the corpse) — [VERIFY AT BUILD by reading `Patch_CorpseSiteConversion.cs`'s
hook point; the release must land on the map before the corpse becomes a building].

Also: `PostSwapMap` → nothing (no job to restart); a titanoslime carried on a gravship is not a
case to support — it is untameable and unhaulable.

## 5. Player surface

- **Inspect string** (`CompInspectStringExtra`): `Stage 3 of 5 — great titanoslime · mass 14.2 /
  28 to grow` and, per held pawn, `Digesting Ana: 51 s left`. Dev mode adds `absorbedMass` raw.
- **Description** (ThingDef): *"A hill of green jelly that has learned to go and fetch. Titanoslimes
  are lobes of the body itself, glassy and slow, and they read the way the body reads: by taking
  a thing in whole. Shapes drift inside them — a shell, a jawbone, a tool haft — entries not yet
  filed. What a titanoslime finishes reading it returns to the flow, and there is nothing left to
  bury. Cut one and it leaks gelatids. Starve one, or lead it off the body onto dry ground, and it
  shrinks. Let one eat, and it does not stop growing."*
- **Mod Settings** (added to `SlimeSettings`, all with the mod's existing Mod Settings page):
  `titanoslimeSpawnFactor` slider 0–3 (default 1; applied by rewriting the loaded `BiomeDef.
  wildAnimals` record's commonality for `RM_Titanoslime` at startup and on settings change — the
  same loaded-def edit Large Pawns performs on its table; no Harmony), `titanoslimeEngulfs` (bool,
  default on; off → the engulf tool always slams), `titanoslimeGrows` (bool, default on; off →
  `absorbedMass` frozen at spawn value), `titanoslimeMaxStage` (1–5, default 5),
  `titanoslimeSheds` (bool, default on). All-off degrades to a slow, big, slam-only predator that
  still works.

## 6. Roster placement

| where | entry |
|---|---|
| `RM_GelatinousSlime` BiomeDef (`GelatinousSlime/Defs/BiomeDefs/GelatinousSlime.xml`) `wildAnimals` | `<RM_Titanoslime>0.12</RM_Titanoslime>` beside `RM_Gelatid 3.0` |
| `RUT_Slime` BiomeDef (`UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml`) `wildAnimals` | `<RM_Titanoslime MayRequire="mandrake.rm.gelatinousslime">0.12</RM_Titanoslime>` |
| `rosters/the_slime.json` `fauna` | `{ "action": "new-def", "band": "apex-native", "commonality": 0.12, "def": "RM_Titanoslime", "law": "owner ask 2026-09-20 (TITANOSLIME_SLIME_BIOME_1): a titanic green slime that swallows pawns whole and grows as it eats; §1 the body's own imperative (ingest, analyze, store), resistant by identity; distinct from the Harvester eviction because it IS the body, not a foreign apex", "note": "spec design/RimMandrake/RM_titanoslime_spec.md" }` and a matching `new_defs` row |
| PawnKindDef | `combatPower` 900 [INVENTED]; `ecoSystemWeight` **6** [INVENTED] — `WildAnimalSpawner` sums `kindDef.ecoSystemWeight` of spawned wild pawns against the density budget (MEASURED), so one titanoslime costs the biome what six gelatids would and the spawner stops adding animals while it lives; `wildGroupSize 1~1`; `canArriveManhunter false`; `lifeStages` ×5 (§2.2 drawSizes, all pointing at the one texture set, §7) |

Commonality 0.12 against the campaign roster's 2.375 total ≈ 4.5 % of spawn rolls — with the
ecosystem weight, that is one titanoslime on a map most seasons and rarely two [INVENTED — the
first number to tune after a live look]. Hostility posture, stated once: **a wild predator,
placid when fed, hunts when hungry (animals by default, colonists too if the difficulty allows),
always manhunts when hurt.** Not always-violent, not an entity, not an event — a resident.

**Titans-elsewhere ruling honoured** (`TITANIC_CREATURES_MOD_1` card 5): it roams only where
rostered; no incident spawns it elsewhere in v1.

## 7. Art brief

- **No canon entry** — this is not Star Wars; the target is `the_slime.md` §9 (*"a body the size
  of a country, reading everything that touches it"*: translucent greens and ambers, membrane
  pinks at the deepest core, everything specular — the one biome that shines) and the mod spec's
  art law: **film, tint, drip — never eyes, never buds, never new limbs.**
- **Existing art checked 2026-09-20** (`infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl`,
  `art_status.json`, `Transient/*.decisions.json`): nothing for a titan slime. The nearest is
  **Oozemaw** (`oozemaw_v1_{south,east,north}`, `ART_REGEN_WAVE10_QUEUE_1`, the reimagining of
  `AA_AcanthamoebaGiganteaLarge`): *"semi-translucent gelatinous mass with a faintly visible
  internal organ silhouette, thick pseudopod limbs … mottled sickly green-grey with darker sludge
  streaks … a slow, unnerving amorphous hunter."* ⛔ Not reusable and must be visibly distinct:
  the Oozemaw is an animal that is made of ooze; the titanoslime is **a piece of the landscape that
  moves.**
- **One texture set, three facings** (`RM_Titanoslime_south/east/north`; west mirrors east),
  reused at every stage through `drawSize` — the Thrumbo precedent (one texPath, three drawSizes,
  MEASURED). Generate at **1024 px** (`creature_size_model.md` §4: drawSize 9 → cap 1024, achieved
  ~114 px/cell at stage 5, 256 px/cell at stage 1 — record the achieved figure in `PLAN.md`).
- **Silhouette**: a broad low dome, ~1.4× wider than tall from the south, edges pooling into two or
  three fat pseudopod lobes spread forward along the ground; the east view is a long shallow mound
  with the lobes leading. It must read as a *hill* of jelly, not a blob monster: no face, no
  mouth, no eyes, no limbs with joints, nothing symmetrical.
- **Material**: clean, bright, glassy green (not the Oozemaw's grey-green), with a heavier darker
  core mass off-centre (the `RM_Nucleus`) and a strong specular rim. Inside, faint and
  half-dissolved: a curved rib, a shell, the haft of something — two or three "entries", drawn at
  maybe 20 % opacity so they read at the stage-3 size and vanish at stage 1. Amber lights in the
  thick parts; a membrane-pink glow at the very core.
- **Outline**: heavy clean black outline on the whole silhouette and the major interior lines
  (the standing outline ruling from the wave-10 art item), painterly vanilla animal style.
- **Not in v1**: per-stage variant art (a colossus with more entries inside would be lovely; it is
  three more sheets and the drawSize ladder already sells the growth), a dessicated set (point
  `dessicatedBodyGraphicData` at the same texture with a pale tint — a dried titanoslime is a
  smaller, paler one), and any flying/animated frames.
- **Queue as** an ordinary `fill_queue.py` job on this item's id, `reference=null` (a restyle
  reference would trigger reskin-validate — memory note), three facings, 1024 canvas.

## 8. Build list, sized, with gates

Per the spike doctrine (prove on one def, measure, report). Everything below is inside
`src/RimMandrake/GelatinousSlime/`.

| # | piece | size | gate (quicktest, minimal list + GelatinousSlime + TitanicCreatures + Large Pawns + **all five DLC**) |
|---|---|---|---|
| 1 | XML: race, kind ×5 stages, 5 LifeStageDefs, BodyDef, ToolCapacityDef, ManeuverDef, two biome `wildAnimals` lines, roster JSON row | S | `measure count ThingDef` shows `RM_Titanoslime`; `jawa/spawn_pawn` places one; `jawa/list_things` reports BodySize 6 |
| 2 | `RM_CompEngulfer` growth half (lock stage from `absorbedMass`, records poll, starve/dry decay, stage messages) | M | dev-set `absorbedMass` 12 via a debug gizmo → BodySize 16, drawSize 6, Titanic tier T2, Large Pawns 3×3 (wait 60 ticks — its cache); save, reload, all four unchanged |
| 3 | `RM_Verb_MeleeEngulf` + hold/digest/release/absorb | M | spawn one stage-1 + 4 drafted colonists in melee: a colonist is swallowed within 60 s; inspect shows the countdown; downing the slime drops the colonist stunned with acid burns and `RM_Slimification` +0.15; letting the timer run absorbs (no corpse, gear on the ground, `absorbedMass` +1, food full) |
| 4 | struggle + burst-out + shedding | S | a muffalo swallowed by a stage-1 bursts out inside ~1 min most runs (spawn 10 — one run is RNG); cutting a stage-2 to 50 % health sheds ≥ 3 gelatids and drops it to stage 1 |
| 5 | Mod Settings five knobs | S | each toggle observed live; `titanoslimeMaxStage 2` refuses stage 3 at `absorbedMass` 12 |
| 6 | corpse-site at stage 4 | S | kill a dev-grown stage-4 → `RM_TitanicCorpseSite` building, held pawn released *before* conversion |
| 7 | art (§7) | — | judged at display size on the quicktest map at stages 1 and 5, south/east/north |

**LIES to expect** (from this repo's own record): a placement log's `thingsSpawned` is a net
count; a stage that "grew" only on screen — assert `BodySize` through the bridge, not the sprite;
Large Pawns' footprint lags its 60-tick cache; one pawn's burst-out is pure RNG — spawn many;
`modcheck run` rewrites the live `ModsConfig.xml`; and a def that loaded clean with a
`SlimeResistantExtension` typo on it is silently discarded (memory: missing modExtension eats
the def) — `measure count` before believing the spawn.

## 9. What was NOT decided here (build's, not the owner's)

The exact override signature in `Verb_MeleeAttack` (§4.1), whether `statFactors` on
`LifeStageDef` reaches `MoveSpeed` (§2.1), the `BodyPartDef` boilerplate (§3.2), the fleck and
sound picks, and whether GelatinousSlime is on the campaign's full mod list right now
(UNMEASURED this pass: the newest snapshot in `infrastructure/state/modlists/` lists only
`mandrake.rm.weathersuite` among `mandrake.rm.*` entries, and the live `ModsConfig.xml` is on a
15-mod test list — measure before assuming the campaign biome will ever roll one).

## 10. Sources read

`infrastructure/state/items/TITANOSLIME_SLIME_BIOME_1.md` · `design/Jawa/worldbuilding/biomes/the_slime.md`
(FROZEN) · `biomes/rosters/the_slime.json` · `design/RimMandrake/RM_gelatinous_slime_mod.md` ·
`design/Jawa/worldbuilding/sarlacc_spec.md` · `design/Jawa/worldbuilding/creature_size_model.md` ·
`src/RimMandrake/GelatinousSlime/` (About, `Gelatid.xml`, `SlimeBiome.cs`, `SlimeMod.cs`) ·
`src/RimMandrake/TitanicCreatures/` (About, `RM_TitanicTierDef.xml`, `TitanicTierUtility.cs`,
`RM_TitanicExtension.cs`, `Patch_CorpseSiteConversion.cs`) · `research/large_pawns_decompile_2026-09-09.md`
· `src/RimMandrake/CreatureBehaviors/Source/RM_CompGrappler.cs`, `RM_CompAquaticAmbusher.cs` ·
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml` · decompile (RimSage): `CompDevourer.cs`,
`CompProperties_Devourer.cs`, `CompAbilityEffect_ConsumeLeap.cs`, `Devourer` ThingDef +
`ConsumeLeap_Devourer` + `ThinkTreeDefs/Devourer.xml`, `Pawn_AgeTracker.cs`, `LifeStageDef.cs`,
`FoodUtility.IsAcceptablePreyFor`/`BestPawnToHuntForPredator`, `JobDriver_PredatorHunt.cs`,
`WildAnimalSpawner.cs`, `PawnGenerator.GenerateRandomAge`, `Maneuvers.xml`, `Thrumbo` ThingDef +
PawnKindDef · `infrastructure/artpipe/` (done, registry, art_status) and `Transient/*.decisions.json`
for prior art.
