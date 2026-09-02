<!-- status: DESIGN SPEC (def-level, machine-checkable) — SW_SEA_MONSTERS_ART_1,
     BENCH 2026-09-02. Names + bodySize are the RULED roster
     (sea_beasts_roster.md, owner 2026-08-31) and are FIXED here. Every other
     number is calibrated against a named vanilla def read from the 1.6 install
     XML (Data/Core|Odyssey|Anomaly/Defs/ThingDefs_Races) and the C# source via
     RimSage, and sized under beast_normalization_spec.md Laws 1–4. No XML is
     written by this doc. Tier RimStarWars (mandrake.rsw.*, RSW_). -->
# Sea beasts — def design spec (18 creatures)

**Deliverable of this doc:** for each of the 18 roster creatures, the complete
`ThingDef` (race) + `PawnKindDef` an implementer can type without a decision.
Anything not verified against the source or the install XML is marked
`UNMEASURED`, never guessed into a table.

Mod shape: one mod `mandrake.rsw.seabeasts` at `src/RimStarWars/SeaBeasts/`
(folder already holds the art), namespace `RimMandrake.StarWars.SeaBeasts` if any
C# is ever needed (§4 says when). Parents: `AnimalThingBase` / `AnimalKindBase`
(`Races_Animal_Base.xml`).

---

## 1. What bodySize does and does not do (verified in source, 2026-09-02)

The memory note *"scale ALL attributes cannot include fractions, and bodySize
never scales melee damage"* — checked against the 1.6 C#:

| Claim | Verdict | Where |
|---|---|---|
| `bodySize` scales **melee damage** | **FALSE — never.** Melee damage is `Tool.power × MeleeDamageFactor` and nothing else | `Verse/VerbProperties.cs:336-348 AdjustedMeleeDamageAmount` → `Tool.AdjustedBaseMeleeDamageAmount` (`Verse/Tool.cs`); `RimWorld/Verb_MeleeAttackDamage.cs:14 DamageInfosToApply` (±20 % roll, no size term) |
| `bodySize` scales **health** | **FALSE.** `HealthScale = lifeStage.healthScaleFactor × baseHealthScale` | `Verse/Pawn.cs:2501` |
| `bodySize` scales **Mass** | TRUE — `60 × bs` (`StatPart_BodySize` on a flat 60) | `Defs/Core/Stats/Stats_Basics_General.xml:34`; `Races_Animal_Base.xml` `<Mass>60</Mass>` |
| … **Nutrition** (as food), **MeatAmount** (140×bs), **LeatherAmount** (40×bs on `AnimalThingBase`), **CarryingCapacity** (75×bs), **MaxNutrition** | TRUE — all carry `StatPart_BodySize` | `Stats_Basics_General.xml:293`; `Stats_Pawns_General.xml:312,335,382,527` |
| MoveSpeed, MarketValue, armor, temperature, hunger, wildness | **NOT scaled** — authored per def | (no StatPart on those stats) |
| Live `BodySize` | `lifeStage.bodySizeFactor × baseBodySize` | `Verse/Pawn.cs:2499` |

Other places bodySize is *read* (so the leviathans/colossi inherit them free):
ranged hit-chance factor (`ShotReport.cs:129`; projectile impact clamps bs to
0.1–2, `Projectile.cs:367,534` → **everything above bs 2 is exactly as easy to
hit as a bs-2 animal**), bullet stagger only when `bs ≤ stoppingPower`
(`StaggerHandler.cs:49` → nothing here above bs 1 is ever staggered by
small arms), predator prey check `prey.BodySize > predator.maxPreyBodySize`
(`FoodUtility.cs:781`), food need max (`Need_Food.cs:77`), inventory mass
35×bs (`MassUtility.cs:85`), "big splash" arrival threshold bs > 1.5
(`PawnsArrivalModeWorker_EmergeFromWater.cs:69`).

**Consequence for this spec:** bodySize is one dial with no downstream damage
or health — so *every* combat number below is authored, on the formula in §2.

## 2. The laws, as quoted, and the formulas this spec executes

From `design/Jawa/worldbuilding/beast_normalization_spec.md` (quoted verbatim):

> **Law 1 — bodySize from visual:** `bodySize = (drawSize/1.9)²`, exemptions:
> legibility floor (bs < 0.5 keeps authored size) and the spindly register
> (each exemption a named row with a one-line physical justification).

> **Law 2 — mass rides bodySize** (already definitional). […] ✅ RULED (owner
> card, 2026-08-31): engine scale kept.

> **Law 3 — casual lethality, with counterplay** (arm-3 curve, adopted as
> draft): for bs ≥ 1, **best-hit damage goes linear: ≈ 12–15 × bodySize**
> (muffalo/bull 2.4 → ~30: one hit downs an unarmored pawn; thrumbo-class 4.0
> → 50–60: maims or kills) while **DPS stays sublinear (≈ 8–12·√bs) via 3–4 s
> cooldowns on the big hits** — burst lethality, not shredding; fights are
> survived by not being hit. **Aggression does NOT rise**: the "casual" half
> lives in the revenge knobs (`manhunterOnDamageChance`,
> `manhunterOnTameFailChance`) raised on big herbivores — docile until
> provoked, catastrophic when provoked.

> **Law 4 — the blaster-shrugging hide** […] **Option A — armor absorption —
> ✅ RULED (owner card, 2026-08-31):** `ArmorRating_Heat` on a **thick-hide
> register** of beasts, scaling with bodySize (draft: ~15% × bodySize, capped
> ~75%). […] Register-based like the spindly list: not every big beast
> qualifies (soft-bodied and spindly exempt).

Law 3 was RULED at **K = 15** and shipped in `mandrake.rsw.beastnorm`
(`design/Jawa/worldbuilding/data/beast_norm_manifest.csv`). The manifest's
arithmetic, read back from its rows (KraytDragon bs 12 → 180 / 5.2 s → 34.6
DPS; GreaterKraytDragon bs 15 → 225 / 5.81 s → 38.7; Acklay bs 3 → 45 / 2.6 →
17.3), is exactly:

```
best-hit power      P  = 15 × bs                (bs ≥ 1)
best-hit cooldown   C  = 1.5 × √bs  seconds
nominal DPS         P/C = 10 × √bs
ArmorRating_Heat    H  = min(0.15 × bs, 0.75)   thick-hide register only
drawSize            D  = 1.9 × √bs              (bs ≥ 0.5; legibility floor below)
```

Below bs 1 Law 3 does not apply; those rows are calibrated straight against
the vanilla animal of the same size. Secondary tools (claws, head) are
vanilla-style quick hits at ≤ ⅓ of the best-hit power; they lift real DPS
above the nominal 10·√bs curve — see §6 LIES lines.

**Law 3 saturation (measured, FOUNDRY 2026-08-31, quoted in the spec §4.2):**
a single torso hit of 50–70 already kills an unarmored pawn outright, and the
down/kill transition is bimodal. So a colossus "hitting for 600" is the same
event as hitting for 100. The formula is still applied literally — the
manifest did, at bs 15 — because the number is the *register*, not the
outcome, and armor (Law 4's counterplay) is what makes 600 vs 100 differ
against flak. Rows above bs 5 carry a **"saturated"** note rather than a
different rule.

## 3. Shared def skeleton (every creature)

Fields verified to exist: `RaceProperties` (`Verse/RaceProperties.cs`),
`PawnKindDef` (`Verse/PawnKindDef.cs`), `PawnKindLifeStage`
(`Verse/PawnKindLifeStage.cs`), `Tool` (`Verse/Tool.cs`).

| Field | Value for all 18 | Source |
|---|---|---|
| `ThingDef ParentName` | `AnimalThingBase` | `Races_Animal_Base.xml` |
| `PawnKindDef ParentName` | `AnimalKindBase` | same |
| `race/lifeStageAges` | `AnimalBaby 0` / `AnimalJuvenile 0.1` / `AnimalAdult 0.3333` (vanilla SeaLion pattern; colossi + elder use 0.2 / 0.6) | `Odyssey…Races_Animal_Coastal.xml` SeaLion |
| `race/trainability` | `None` on all 18 (sea life is not colony stock; the only `TrainabilityDef`s are `None`/`Intermediate`/`Advanced`) | `Core/Defs/Misc/TrainabilityDefs/TrainabilityDefs.xml` |
| `race/waterSeeker` | `true` | `RaceProperties.cs:120`; spawner requires water cells on map (`WildAnimalSpawner.cs:118,165`) |
| `race/waterCellCost` | `1` | `RaceProperties.cs:122`; §4 |
| `race/canFishForFood` | `true` on every carnivore (config error if set on a non-meat-eater, `RaceProperties.cs:484`) | `JobGiver_GetFood.cs:79` (Odyssey active: yes, `ludeon.rimworld.odyssey` is in the live list) |
| `race/gestationPeriodDays` | REQUIRED on all (normal flesh without it is a config error, `RaceProperties.ConfigErrors`) | |
| `race/hediffGiverSets` | inherits `OrganicStandard` | base |
| `PawnKindDef/moveSpeedFactorByTerrainTag` | `Water: 2.0` (vanilla Walrus/SeaLion pattern) | `PawnKindDef.cs:69`; `StatPart_TerrainMoveSpeed.cs`; `Pawn_PathFollower.cs:761` |
| `lifeStages[i]/swimmingGraphicData` | same texPath as `bodyGraphicData` (v1: one sprite set; swimming variant is a later art pass) — required or the swim draw path never fires (`Pawn.cs:1688`) | `PawnKindLifeStage.cs:45` |
| `lifeStages[i]/bodyGraphicData/texPath` | `Things/Pawn/Animal/SeaBeasts/<Slug>/<Slug>` — Graphic_Multi, four facings, from `src/RimStarWars/SeaBeasts/art/final/<Slug>/` (only `OpeeSeaKiller` exists today) | roster; art PLAN.md |
| `race/wildBiomes` | `RM_SeafloorBiome` (planned, `depths_build_spec_v1.md` §2 — **does not exist yet**; until it does, spawn only by dev/bridge) — values in §5 | |
| `tradeTags` | none (untradeable wildlife) | |
| `race/canBePredatorPrey` | `false` on leviathans + colossi, default elsewhere | `RaceProperties.cs` |
| `statBases/Wildness` | authored (a **stat**, not a race field — vanilla puts it in `statBases`) | `Races_Animal_CowGroup.xml:227` |

Body defs (all verified present in the active DLC set; part labels read from
`Data/*/Defs/Bodies`): `Crab` (Odyssey: shell, gills, claws, swimming legs —
groups `FrontLeftClaws/FrontRightClaws/HeadAttackTool/Teeth`),
`QuadrupedAnimalWithClawsTailAndJowl` (Core, the alligator body — claws, tail,
jowl), `QuadrupedAnimalWithPawsAndTail` (Core — `FrontLeftPaw/FrontRightPaw/
HeadAttackTool/Teeth`), `Snake` (Core — `HeadAttackTool/Mouth`; parts read
"snake body / snake head / snake mouth" in the health tab — the one cosmetic
compromise), `BeetleLike` (Core, isopod-shaped — `HeadAttackTool/Mouth`),
`Pinniped` (Odyssey — flippers + jaw; groups `FrontLeftPaw/FrontRightPaw/
HeadAttackTool/Teeth`). A dedicated fish body (`RSW_FishBody`, fins + tail
from existing `BodyPartDef`s) is a v2 nicety, not a blocker.

## 4. Aquatic handling — the mechanism, verified

**What RimWorld 1.6 has (Core, no mod):**

1. `RaceProperties.waterCellCost` — `Pawn.WaterCellCost` (`Pawn.cs:1752-1770`;
   flying → 1, Biotech gene, then the race value) overrides the per-cell path
   cost on any `IsWater` terrain (`Pawn_PathFollower.cs:739
   GetPawnCellBaseCostOverride`; `PathFinderCostTuning.For`). Vanilla uses `1`
   on SeaLion/Walrus/Seal/Otter/Hippo/Alligator/Bullfrog/ColossusToad/Penguin
   (Odyssey), Devourer (Anomaly, `Races_Entities_Misc.xml:1031`), `10` on
   bears and megasloth.
2. `RaceProperties.waterSeeker` — spawner only places the kind if the map has
   water; wander targets prefer water (`RCellFinder.cs:395,468`).
3. `PawnKindLifeStage.swimmingGraphicData` — drawn instead of the body sprite
   while on water, only when `WaterCellCost.HasValue` (`Pawn.cs:1684-1692`).
4. `PawnKindDef.moveSpeedFactorByTerrainTag` — `Water` tag × 2.0 on vanilla
   pinnipeds.
5. `RaceProperties.canFishForFood` — Odyssey: a hungry carnivore eats from a
   fish-bearing water body (`JobGiver_GetFood.cs:79`).

**The hard limit:** `WaterDeep` and `WaterOceanDeep` are
`<passability>Impassable</passability>` (`Core/Defs/TerrainDefs/Terrain_Water.xml`,
`WaterDeepBase`, pathCost 300). `PathGrid.CalculatedCostAt` (`Verse/AI/PathGrid.cs:125`)
returns 10000 for impassable terrain unless the pawn is on the **Flying** path
grid AND the terrain sets `forcePassableByFlyingPawns` — which `WaterDeep`
does and `WaterOceanDeep` does **not**. A pawn is on the flying grid only
while `Pawn.Flying` (`Pawn.GetPathContext`, `Pawn.cs:5348`), which needs
`MaxFlightTime > 0` and a job that starts flight (`Pawn_FlightTracker`).
`waterCellCost` never touches passability. **There is no vanilla field that
lets a swimmer enter deep water.** Vanilla "aquatic" animals live in shallow /
chest-deep water (Walkable affordance). The Odyssey `EmergeFromWater` arrival
mode likewise floods only `cell.Walkable` water.

**Mods in the live list (593 active by `<li>` count of `ModsConfig.xml`,
2026-09-02; census by subagent, spot-checked):** see §4.1. Short form:
**nothing installed and active changes deep-water passability for an animal.**

**Verdict and the design choice this spec makes:**

The depths concept already answers this without a swimming mechanism.
`depths_build_spec_v1.md` §2 builds the sea as a **pocket seafloor map**
(`MapGeneratorDef RM_Seafloor`, `BiomeDef RM_SeafloorBiome`, `GenStep_Seafloor`
laying silt/reef/wreck terrain) where the water is the *medium* (Odyssey vacuum
analog), not a terrain. On that map every beast paths over floor terrain like
any animal; the vanilla fields above make them "swim" on the shallow-water
pools the genstep scatters and spawn only where water exists. **All 18 are
specced as seafloor animals: `waterSeeker true`, `waterCellCost 1`,
`moveSpeedFactorByTerrainTag Water 2.0`, `swimmingGraphicData` set — and
nothing else.** That is honest and needs zero C#.

What this does NOT give, stated plainly: none of the 18 can exist on a
*surface* coastal map's `WaterOceanDeep`. The three honest routes if the owner
wants the sando visible from the beach:

| Route | Cost | Note |
|---|---|---|
| A. Custom `PathGridDef` (`workerType` is an open extension point, `Verse/PathGridDef.cs`) + `PathGrid` subclass that treats impassable water as cost 1 for races carrying a `DefModExtension`; Harmony on `Pawn.GetPathContext` | C#, plus the region/reachability system still sees Impassable cells as no-region — a second patch | the real "swimmer" mechanism; own item |
| B. Subscribe `pathfinding.framework` (Pathfinding Framework) and give the 18 an aquatic movement type; BiomesCore + Alpha Animals already carry gated hooks for it | one mod subscription + a cold load; a 594th mod on a 25-minute list | §4.1 — the cheapest real swimmer; owner's call |
| C. A passable deep-water `TerrainDef` on our own sea maps (`RSW_OpenWater`, `Walkable`, high pathCost) | XML only | colonists could walk it too — needs the depths exposure stack to make that lethal, which v1 builds anyway |

Deferred, not decided here. Nothing in §5 changes under any of A–C.

### 4.1 Mod census (live list, 2026-09-02)

| Mod (packageId) | Active | What it has | Evidence | Deep water? |
|---|---|---|---|---|
| Odyssey DLC | yes | `waterSeeker`/`waterCellCost 1`/`canFishForFood`, `swimmingGraphicData`, `moveSpeedFactorByTerrainTag Water 2.0` | `Data/Odyssey/Defs/ThingDefs_Races/Races_Animal_Coastal.xml` | no — walkable water only |
| BiomesCore (`biomesteam.biomescore`) | yes | abstract `BiomesCore_WaterAnimal` race base with the same two vanilla fields; a `BiomesCore_DeepWaterBridgeable.xml` patch whose `passability` removal on `WaterDeepBase` is **commented out** as shipped (only a `BMT_DeepWaterBridgeable` affordance survives — bridges, not animals) | `…/294100/2038000893/1.6/Defs/Animals/BMT_BaseAquaticAnimalDefs.xml`; `…/1.6/Patches/BiomesCore_DeepWaterBridgeable.xml` | no |
| Alpha Animals (`sarg.alphaanimals`, Biomes! Islands submod) | yes | Fangsquid carries a `PathfindingFramework.TerrainTagGraphicExtension` / `PF_TerrainTag_WaterDeep` hook gated `IfModActive="pathfinding.framework"` | `…/1541721856/1.6/Mods/BiomesIslands/Defs/ThingDefs_Races/Races_Fangsquid.xml:148-158` | only via the framework below |
| **Pathfinding Framework (`pathfinding.framework`)** | **not installed, not active** — 0 `About.xml` with that packageId in the 1258-folder workshop index (the one grep hit is Biomes! Polluted Lands *depending* on it); 0 in `ModsConfig.xml` | the movement-type framework that gives an animal genuine deep-water traversal | — | it is THE route-B candidate if the owner wants swimmers on surface maps: one subscription, and BiomesCore/Alpha Animals' hooks light up |
| SWAC (`mlie.starwarsanimalcollection`) | yes | vanilla `waterSeeker`/`waterCellCost` on its aquatics (Yobshrimp etc.) | `…/3497316713/1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml` | no |
| `mandrake.rsw.seaswaterline` (ours) | yes | wildBiomes patches only (Lane 1 waterline cast) | `src/RimStarWars/SeasWaterline/Patches/Waterline_Lane1.xml` | no |

Verdict unchanged: the seafloor-map route (§4) is the v1 answer; route B is
now concrete — `pathfinding.framework` is a known, unsubscribed mod, not a
C# project — and is filed as an owner question, not built here.

## 5. The 18 — full def tables

Column key. **bs** = `baseBodySize` (FIXED). **hs** = `baseHealthScale`.
**hunger** = `baseHungerRate`. **Spd** = `MoveSpeed`. **MV** = `MarketValue`.
**T** = `ComfyTemperatureMin/Max`. **Arm B/S/H** = `ArmorRating_Blunt/Sharp/Heat`.
**Wild** = `Wildness`. **cP** = `combatPower`. **eco** = `ecoSystemWeight`.
**grp** = `wildGroupSize`. **mhD/mhT** = `manhunterOnDamageChance/OnTameFailChance`.
**gest/litter** = `gestationPeriodDays` / `litterSizeCurve` points. **Tools** =
`label: capacity power/cooldownTime [linkedBodyPartsGroup] (chanceFactor)`.
**drawSize** per Law 1. All temps °C. "cal." names the vanilla def the row was
read against, with its numbers in brackets.

### 5.1 Silt ambushers — the opee family (body `Crab`, predators)

Family constants: `predator true`, `foodType CarnivoreAnimal`, `canFishForFood
true`, `herdAnimal false`, `grp 1`, `lifeExpectancy 40`, `gest 10`, litter
default (none), `leatherDef Leather_Lizard` (vanilla Alligator's; a
`Leather_OpeeShell` is v2), thick-hide register: YES (armored).
cal. **Alligator** [bs 1.5, hs 1.2, hunger 0.3, Spd 2.8, MV 350, T −10/60,
predator maxPrey 1.2, mhD 0.5 mhT 0.3, Wild 0.9, claws 12/2 ×2, bite 22/2.6,
head 8/2, cP 120, eco 0.5] and **Tiger** [bs 1.4, hs 1.5, MV 450, mhD 0.75
mhT 0.5, cP 130].

| defName / label | bs | hs | hunger | Spd | MV | T | Arm B/S/H | Wild | maxPrey | mhD/mhT | Tools | cP | eco | drawSize |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `RSW_OpeeSeaKiller` "opee sea killer" | **1.4** | 1.4 | 0.25 | 3.0 | 400 | −5/55 | 0.25/0.45/**0.21** | 0.9 | 1.2 | 0.5/0.3 | bite: Bite **21/1.8** [Teeth]; left claw: Cut 8/2 [FrontLeftClaws]; right claw: Cut 8/2 [FrontRightClaws]; head: Blunt 6/2 [HeadAttackTool] (0.2) | 130 | 0.5 | 2.25 |
| `RSW_CrimsonOpee` "crimson opee" | **1.7** | 1.5 | 0.28 | 3.4 | 450 | 5/60 | 0.20/0.40/**0.26** | 0.9 | 1.4 | **0.75/0.4** | bite: Bite **26/2.0** [Teeth]; adhesive tongue: Blunt 8/1.5 [HeadAttackTool] (0.6); claws 9/2 ×2; head 6/2 (0.2) | 150 | 0.5 | 2.48 |
| `RSW_ShaleGorger` "shale gorger" | **2.0** | 2.2 | 0.32 | **2.2** | 500 | −15/50 | **0.35/0.55/0.30** | 0.95 | 1.6 | 0.4/0.3 | swallowing bite: Bite **30/2.1** [Teeth]; claws 10/2 ×2; head 7/2 (0.2) | 170 | 0.5 | 2.69 |

Descriptions:
- **Opee sea killer** — *A brown-armored ambusher of the Naboo core-seas,
  part crab, part angler. It buries itself in the silt with only its lure
  stalks showing, then takes prey on an adhesive tongue faster than a diver can
  turn. Twenty metres of patience; it has never needed to chase anything.*
- **Crimson opee** — *A warm-shallows morph of the opee, barnacled and rust-red,
  that hunts with its tongue already out. Where the brown opee waits, the
  crimson one provokes — it will strike at a lamp, a splash, a shadow. The
  reef-cut shallows belong to it.*
- **Shale gorger** — *The heavy benthic cousin: slate plates instead of shell,
  eyes long since gone pale in the dark below the silt line. It sits in scree
  and swallows what settles onto it. The slowest thing in the trench, and the
  hardest to kill.*

### 5.2 Harpooners — the colo family (body `QuadrupedAnimalWithClawsTailAndJowl`, predators)

Family constants: `predator true`, `foodType CarnivoreAnimal`, `canFishForFood
true`, `herdAnimal false`, `grp 1~2` (the "pack" of the role is two), `gest
14`, litter default, `lifeExpectancy 60`, `leatherDef Leather_Lizard`,
thick-hide register: **NO** (soft cave-pale hide — Law 4 exempt, named here as
the register requires; Heat stays at the vanilla default 0).
cal. **Rhinoceros** [bs 3.0, hs 3.5, hunger 1.07, Spd 5.0, MV 700, Wild 0.9,
horn 19/2, cP 270, mhD 0.5 mhT 0.3] for size; **Alligator** for the
ambush-predator knobs; manifest **Acklay** [bs 3 → 45 / 2.6 s] for Law 3.

| defName / label | bs | hs | hunger | Spd | MV | T | Arm B/S/H | Wild | maxPrey | mhD/mhT | Tools | cP | eco | drawSize |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `RSW_ColoClawFish` "colo claw fish" | **3.0** | 3.0 | 0.45 | 4.0 | 800 | −10/50 | 0.15/0.25/0 | 0.95 | 2.0 | 0.6/0.4 | bite: Bite **45/2.6** [Teeth]; left claw: Stab 15/2 [FrontLeftClaws]; right claw: Stab 15/2 [FrontRightClaws]; head: Blunt 10/2 (0.2) | 280 | 0.8 | 3.29 |
| `RSW_AbyssalColo` "abyssal colo" | **3.6** | 3.4 | 0.50 | 3.8 | 900 | −20/40 | 0.15/0.25/0 | 0.98 | 2.4 | 0.6/0.4 | bite: Bite **54/2.85** [Teeth]; claws: Stab 16/2 ×2; head 10/2 (0.2) | 320 | 0.8 | 3.60 |
| `RSW_ThornbackColo` "thornback colo" | **2.6** | 2.6 | 0.42 | **4.6** | 700 | 0/55 | 0.15/0.30/0 | 0.95 | 1.8 | 0.75/0.4 | bite: Bite **39/2.4** [Teeth]; claws: Stab 13/1.8 ×2; thorn rake: Cut 10/2 [HeadAttackTool] (0.5) | 250 | 0.8 | 3.06 |

Descriptions:
- **Colo claw fish** — *A pale cave eel of the Naboo underworld, forty metres
  from lure to tail, with a pair of clawed forelimbs it uses to pin what its
  whisker-lures draw in. Its jaw distends to swallow prey larger than itself.
  It hunts from the dark just past the edge of your light.*
- **Abyssal colo** — *A deep-trench morph of the colo, spotted in rows of blue
  bioluminescence that it can dim to nothing. It hunts in full dark below the
  silt line, where a lamp is not a tool but an invitation.*
- **Thornback colo** — *A spined, purple-dark shallows morph, shorter and
  faster than its pale cousin. It ambushes from wreck hulls and reef cuts and
  rakes with the dorsal thorns as it passes. The one you meet on the way down.*

### 5.3 Leviathans — the sando family (body `QuadrupedAnimalWithPawsAndTail`, apex)

Family constants: `predator true`, `maxPreyBodySize 20` (eats colo),
`canBePredatorPrey false`, `foodType CarnivoreAnimal`, `canFishForFood true`,
`herdAnimal false`, `grp 1`, `canArriveManhunter false` (never a manhunter
pack — an *event*, `PawnKindDef.cs`), thick-hide register: YES → Law 4 cap
**0.75** at every size here. `lifeStageAges` 0 / 0.2 / 0.6 (long-lived).
cal. **Thrumbo** [bs 4, hs 8.0, hunger 1.75, Spd 5.5, MV 4000, T −65/50,
Arm 0.40/0.60/0.30, Wild 0.98, mhD 1.0 (mhT unset), horn 23/2, bite 28/2.6,
foot 19/2 ×2, head 17/2, cP 500, eco 1.0, lifeExp 220] and manifest
**KraytDragon** [bs 12 → 180 / 5.2 s]. Health scale is authored at ≈ 0.8 × bs
(thrumbo sits at 2 × bs, elephant at 0.9 × bs; a bs-14 apex at thrumbo's ratio
would be hs 28 — torso 1,120 HP — and a harpoon fight that never ends).

| defName / label | bs | hs | hunger | Spd | MV | T | Arm B/S/H | Wild | mhD/mhT | gest/litter | Tools | cP | eco | drawSize |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `RSW_SandoAquaMonster` "sando aqua monster" | **14** | 11 | 2.6 | 4.5 | 6000 | −20/50 | 0.45/0.65/**0.75** | 0.99 | 1.0/1.0 | 60 / default | bite: Bite **210/5.6** [Teeth]; left claw: Cut 60/3.0 [FrontLeftPaw]; right claw: Cut 60/3.0 [FrontRightPaw]; head: Blunt 30/2.5 (0.2) | 900 | 3.0 | 7.11 (saturated) |
| `RSW_ElderSando` "elder sando" | **20** | 16 | 3.2 | 3.8 | 9000 | −20/50 | 0.50/0.70/**0.75** | 1.0 | 1.0/1.0 | 60 / default, `disableMating true` | bite: Bite **300/6.7** [Teeth]; claws: Cut 80/3.2 ×2; head 40/2.5 (0.2) | 1200 | 3.0 | 8.50 (saturated) |
| `RSW_StormSando` "storm sando" | **12** | 10 | 2.4 | **5.5** | 5000 | −15/45 | 0.40/0.55/**0.75** | 0.99 | 1.0/1.0 | 60 / default | bite: Bite **180/5.2** [Teeth]; claws: Cut 50/2.8 ×2; head 25/2.5 (0.2) | 800 | 3.0 | 6.58 (saturated) |

`lifeExpectancy` 200 / 300 / 150. `Wildness 1.0` on the elder = never tameable
(`manhunterOnTameFailChance` then never fires; kept at 1.0 for the record).

Descriptions:
- **Sando aqua monster** — *The apex of the Naboo core: a grey, lion-faced
  swimming quadruped the length of a cargo hauler, mammalian and warm-blooded
  and utterly unhurried. It takes colo claw fish the way a diver takes a
  ration bar. There is always a bigger fish; this is it.*
- **Elder sando** — *A scarred bull sando, barnacle-crusted, carrying old
  harpoon wounds it has outlived by a century. One per sea, if that. Named by
  every crew that has seen it and survived, which is how it came to have so
  many names.*
- **Storm sando** — *A pelagic morph, blue-striped with bioluminescence and
  finned for open water rather than trench. Faster than the grey, ranging the
  upper column where it attacks from above like weather. Sailors call the
  first sign of one "the sky going out".*

### 5.4 Shoal grazers — the scalefish (body `Snake`, canon Naboo prey fish)

Family constants: `predator false`, `herdAnimal true`, `canBePredatorPrey
true`, `mhD 0 / mhT 0` (prey flees, never turns), `trainability None`,
`lifeStageAges` 0 / 0.05 / 0.15, `gest 4`, litter `(0.5,0)(1,1)(3,1)(4,0)`,
`lifeExpectancy 4`, no leather (`leatherDef` unset → none, vanilla bird
pattern), thick-hide: no. Below bs 1 → Law 3 does not apply; calibrated
straight. **Food, stated honestly:** there is no plant on the seafloor yet
(lightkelp is `depths_concept.md` §6 flora, unbuilt). v1 ships
`foodType None` — `EatsFood` is then false and the pawn gets no food need at
all (`Pawn_NeedsTracker.cs:358`), so a shoal never starves on a bare map.
Flip to `VegetarianRoughAnimal` in the same commit that adds `RSW_Lightkelp`.
Faa is the canon exception (predatory scalefish): `CarnivoreAnimal` +
`canFishForFood true` — it eats from Odyssey water bodies, which the seafloor
genstep provides.
cal. **Bluebird** [bs 0.15, hs 0.1, hunger 0.08, Spd 3.1, MV 30, T −10/–,
claws 1.5/1.5, beak 2.8/2, head 1/1.5, cP 25, eco 0.2, Wild 0.6], **Squirrel**
[bs 0.2, hs 0.25, Spd 5.1, MV 35, cP 33, Wild 0.75], **Iguana** [bs 0.4, hs 0.5,
Spd 3.0, MV 100, T 0/60, claws 8/2 ×2, bite 10/2.6, cP 40, Wild 0.5].

| defName / label | bs | hs | hunger | Spd | MV | T | Wild | foodType | Tools | cP | eco | grp | drawSize |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `RSW_Mee` "mee scalefish" | **0.15** | 0.2 | 0.08 | 4.5 | 25 | 0/50 | 0.9 | None (v1) | nip: Bite 2.5/2 [Mouth]; head: Blunt 1/1.5 [HeadAttackTool] (0.2) | 25 | 0.15 | 6~14 | 1.0 (legibility floor) |
| `RSW_Faa` "faa scalefish" | **0.2** | 0.25 | 0.10 | **5.0** | 30 | 10/60 | 0.9 | CarnivoreAnimal + `canFishForFood` | bite: Bite 3/1.8 [Mouth]; head 1/1.5 (0.2) | 30 | 0.15 | 5~12 | 1.0 (legibility floor) |
| `RSW_Laa` "laa scalefish" | **0.4** | 0.5 | 0.15 | 4.2 | **120** | −5/50 | 0.85 | None (v1) | tail slap: Blunt 4/2 [HeadAttackTool]; bite: Bite 5/2 [Mouth] | 45 | 0.2 | 3~6 | 1.2 (legibility floor) |

`hunger` is authored for the day `foodType` flips; with `None` it is inert.
**Meat:** `mlie.starwarsanimalcollection` (ACTIVE) already ships Odyssey fish
items `swfish_Faa` and `swfish_Laa` (`1.6/Defs/ThingDefs_Items/Items_Resource_swfish.xml`,
`ParentName FishBase`, nutrition 0.5, MV 28) — no `swfish_Mee`. Spec:
`<specificMeatDef MayRequire="mlie.starwarsanimalcollection">swfish_Faa</specificMeatDef>`
(and `swfish_Laa`), so butchering a faa yields *faa*; `MayRequire` is honoured
on any field node (`Verse/DirectXmlToObject.cs:297`). Mee falls back to
generated "mee meat". Label collision with the fish item ("faa" the animal vs
"faa" the fish) is cosmetic and canon-correct.

Descriptions:
- **Mee** — *A silver-blue schooling scalefish with a single line of
  bioluminescent dots along the flank, native to the Naboo shallows and the
  bulk protein of every sea that has them. A shoal scattering is the only
  warning some nights give.*
- **Faa** — *The gold-olive scalefish — "faynaa" to the Gungans — fast,
  small-mouthed and predatory, taking fry and drift-shrimp in the warm water.
  Same dot-line as the mee; a different temper.*
- **Laa** — *The big ornate scalefish: striped, streamer-finned, with eye-spot
  false faces on the tail that turn a strike the wrong way. Prized on every
  table that can get one; hard to net for the same reason it is hard to eat.*

### 5.5 Scavenger swarm — the bottom-feeders (bs ≈ 0.2, in numbers)

Family constants: `herdAnimal true`, `foodType CarnivoreAnimal`
(`CarnivoreAnimal` = `0xB0A` includes the `Corpse` bit, `RimWorld/FoodTypeFlags.cs:12,24`
— they eat what falls), `canFishForFood true`, `trainability None`, `gest 5.661`
(vanilla small-animal constant), litter `(0.5,0)(1,1)(2.5,1)(3,0)`,
`lifeStageAges` 0 / 0.1 / 0.25, `lifeExpectancy 8`, no leather. Below bs 1:
vanilla calibration.
cal. **Megascarab** [bs 0.2, hs 0.4, hunger 0.10, Spd 3.75, MV 100, T 0/60,
Arm 0.18/0.72, mandibles 5/2, head 4/2, cP 40, eco 0.15, Wild 0.2], **StoneCrab**
[bs 0.3, hs 0.6, Spd 2.2, MV 80, Arm 0.25/0.55, claws 9/2 ×2, head 4/2, cP 70,
Wild 0.75], **Cobra** [bs 0.25, hs 0.5, predator maxPrey 0.35, venom-fangs
12/2 ToxicBite, mhD 0.5, cP 65].

| defName / label | body | bs | hs | hunger | Spd | MV | T | Arm B/S/H | Wild | predator/maxPrey | mhD/mhT | Tools | cP | eco | grp | drawSize |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `RSW_Yobshrimp` "pale yobshrimp" | `BeetleLike` | **0.2** | 0.35 | 0.08 | 3.2 | 40 | −5/55 | 0.10/0.20/0 | 0.8 | no | 0.2/0 | mandibles: Bite 4/2 [Mouth]; head: Blunt 2/2 [HeadAttackTool] (0.2) | 30 | 0.15 | 6~12 | 1.0 (floor) |
| `RSW_SiltLamprey` "silt lamprey" | `Snake` | **0.2** | 0.3 | 0.10 | 3.8 | 45 | −10/50 | 0/0/0 | 0.85 | **yes / 0.35** | 0.5/0 | round maw: Bite 6/2 [Mouth]; head 1.5/1.5 (0.2) | 40 | 0.15 | 4~10 | 1.0 (floor) |
| `RSW_RustNipper` "rust nipper" | `Crab` | **0.25** | 0.5 | 0.10 | 2.6 | 70 | 0/60 | **0.25/0.55/0.10** | 0.75 | no | **0.75/0** | left claw: Cut 7/2 [FrontLeftClaws]; right claw: Cut 7/2 [FrontRightClaws]; head 3/2 (0.2) | 60 | 0.2 | 4~9 | 1.0 (floor) |

**Collision, must be decided before authoring:** `mlie.starwarsanimalcollection`
(ACTIVE) already ships a `Yobshrimp` ThingDef/PawnKindDef/BodyDef
(`1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml`: bs **0.4**, hs 0.4, Spd 2.5,
MV 60, Arm 0.08/0.12, Wild 0.2, tools 6/2 ×2 + head 3/2.4, cP 75, eco 0.2,
`waterSeeker`/`waterCellCost 1`, wildBiomes TropicalSwamp 0.6 / Rainforest 0.2).
defNames do not collide (`RSW_` prefix); the **label** "yobshrimp" does, and the
roster's bs 0.2 is FIXED so the two are not the same animal. Default in this
spec: ship `RSW_Yobshrimp` as above and Cherry-Pick or zero-commonality the
SWAC one (`cherrypicker.py`, not a `Remove` patch — see the inherited-`<li>`
lesson). ✅ **OWNER RULED 2026-09-02: "Rename as appropriate."** SWAC's stays; OURS is
renamed. Label is now **"pale yobshrimp"** — it names the trait the art actually
shows (a pale isopod) and the two are different animals anyway (bs 0.2 vs 0.4), so
nothing is cut and no Cherry Picker key is needed. The same ruling renames the three
scalefish to **"mee/faa/laa scalefish"**, because SWAC ships `swfish_Faa`/`swfish_Laa`
as ITEMS whose labels would otherwise read identically to our live creatures.

Descriptions:
- **Yobshrimp** — *A pale, feather-antennaed isopod of the Naboo shallows that
  arrives at a carcass in dozens and leaves a clean frame. Harmless alone;
  the smell of blood is what makes it many.*
- **Silt lamprey** — *A black, round-mawed eel of the silt beds that latches on
  to whatever is bleeding — and, unlike the shrimp, does not wait for it to
  die. The swarm's nasty edge: the wound you took on the way down is the one
  it finds.*
- **Rust nipper** — *A red-shelled spiky crab with faintly glowing eyes,
  armored well enough to ignore a boot. Timid in ones; in a massed crawl over
  a wreck it turns on anything that steps in the middle of it.*

### 5.6 Colossal neutrals — the great filter-feeders (body `Pinniped`, all original)

Family constants: `predator false`, `canBePredatorPrey false`, `herdAnimal
false`, `grp 1`, `canArriveManhunter false`, `Wildness 1.0`,
`disableMating true` (+ nominal `gest 120` so the config check passes),
`lifeStageAges` 0 / 0.2 / 0.6, `lifeExpectancy 500`, thick-hide register: YES
(cap 0.75). **Food:** `foodType None` (they strain plankton the game does not
model; no food need — same mechanism as the scalefish, `Pawn_NeedsTracker.cs:358`).
Law 3's "casual" half is the revenge knob: docile until hurt, then it turns.
cal. **Thrumbo** (above) and **AlphaThrumbo** [bs 5, hs 12, MV 7000, Arm
0.60/0.80/0.30, cP 800]; manifest **GreaterKraytDragon** [bs 15 → 225 / 5.81 s]
for the shape of the line. hs is authored at ≈ 0.6 × bs (a damage sponge that
is still killable by a determined crew: torso 40 × 20 = 800 HP).

| defName / label | bs | hs | Spd | MV | T | Arm B/S/H | mhD/mhT | Tools | cP | eco | drawSize |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `RSW_Reefback` "reefback" | **32** | 20 | 2.0 | 8000 | −30/50 | 0.60/0.70/**0.75** | 0.2/1.0 | tail sweep: Blunt **480/8.5** [HeadAttackTool] ; bulk: Blunt 120/6 [FrontLeftPaw] (0.3) | 2000 | 4.0 | 10.7 (saturated) |
| `RSW_Starmaw` "starmaw" | **36** | 22 | 2.4 | 10000 | −30/50 | 0.60/0.70/**0.75** | 0.2/1.0 | tail sweep: Blunt **540/9.0** [HeadAttackTool]; bulk 130/6 (0.3) | 2200 | 4.0 | 11.4 (saturated) |
| `RSW_Lanternwhale` "lanternwhale" | **40** | 25 | 1.8 | 12000 | −35/45 | 0.65/0.70/**0.75** | 0.2/1.0 | tail sweep: Blunt **600/9.5** [HeadAttackTool]; bulk 150/6 (0.3) | 2500 | 4.0 | 12.0 (saturated) |

drawSize here means a 10–12-cell sprite; Law 1 gives it, and "reads as
terrain" is the role. The `Pinniped` body's `HeadAttackTool` carries the tail
sweep because the body has no tail group; label is cosmetic.

Descriptions:
- **Reefback** — *So old the reef grows on it: coral, kelp, a hundred hangers-on
  that never leave. A moving ecosystem, and the one place in the deep where a
  crew can rest in the light of something else's garden — as long as nobody
  puts a harpoon in the garden.*
- **Starmaw** — *A filter-feeder the size of a hull, spotted in bioluminescent
  patterns that read like a night sky when it rises. Sailors navigate by it,
  and by the crews that vanished trying to.*
- **Lanternwhale** — *Moss-shrouded and trailing blue lantern tendrils that
  draw the plankton it strains, the lanternwhale is the largest living thing in
  the seas. It does not notice you. That is the whole of its character, until
  you make it.*

## 6. PROVE / EXPECT / LIES — per creature

Common harness: minimal mod list (`rimworld-load-round`, ~22 s), quicktest
map, spawn via bridge (`rimbridge`), stats read from the pawn's info card and
`jawa/list_things`. Every line below assumes the def loaded with **zero**
`Config error in` lines in Player.log (grep that first — the validator cannot
see them).

| # | Creature | PROVE | EXPECT | LIES |
|---|---|---|---|---|
| 1 | Opee sea killer | spawn 10; info card; one `jawa/damage`-free melee vs stripped colonist | bs 1.40, hs 1.40, Mass 84, MeatAmount 196; bite listed 21 dmg / 1.8 s; swims onto shallow water at 6.0 c/s | info card shows the bs-scaled Mass and looks "scaled" while damage was never touched — damage is the tool's number only (§1). A pawn that walks water proves `waterCellCost`, not swimming: it is still walking |
| 2 | Crimson opee | same + wound one and watch | 26/2.0 bite; manhunter on damage ≈ 75 % of 10 wounded | one revenge roll is RNG; 10 is the floor (`spawn-many` lesson) |
| 3 | Shale gorger | spawn, shoot with a rifle | armor 35/55/30 absorbs; MoveSpeed 2.2 | 0.30 Heat shows on the card even if no heat weapon was fired — read the burn result, not the number |
| 4 | Colo claw fish | spawn; hostile at 1 colonist | bite 45 / 2.6 s; **Heat 0** on the card (Law 4 exempt) | a bite the 20 % roll lands at 36 still kills; "one hit" is a band, not a value |
| 5 | Abyssal colo | as 4 | 54 / 2.85 s; T −20/40 | temperature comfort is invisible on a temperate quicktest map — force the map temperature or the number is untested |
| 6 | Thornback colo | as 4 + thorn rake logs | 39 / 2.4 s; MoveSpeed 4.6; "thorn rake" appears in the combat log | tool label in the log proves the *tool* fired, not that the `HeadAttackTool` group was the linked part |
| 7 | Sando aqua monster | spawn 1; predator hunt of a spawned colo | hunts and kills a `RSW_ColoClawFish` (maxPrey 20 > 3.0); bite 210/5.6; hit-chance factor shows 2.00 not 14 (`Projectile.cs` clamp) | it does not path onto `WaterOceanDeep` — expected, per §4, and a screenshot of it "swimming" in shallows is not evidence of the deep |
| 8 | Elder sando | spawn 2 of opposite gender; wait a season | no pregnancy (`disableMating`); Wildness 100 % | pregnancy absence over one season is weak evidence; MTB mating is 12 h — two seasons |
| 9 | Storm sando | spawn; race a colonist | MoveSpeed 5.5 (×2 on water = 11) | speed on water reads from `moveSpeedFactorByTerrainTag`, which `StatPart_TerrainMoveSpeed` shows on the card only while standing on water |
| 10 | Mee | spawn 12; wait 3 days | no food need on the needs tab; shoal stays together (`herdAnimal`) | "no starvation" is because there is no need at all — a healthy-looking shoal proves the v1 `foodType None` hack, not an ecology |
| 11 | Faa | spawn on a map with an Odyssey fishable water body | `canFishForFood` job appears in the log when hungry | on a map without a fish population the job never fires and the faa starves — that is a map fact, not a def bug |
| 12 | Laa | butcher one | yields `swfish_Laa` items (with SWAC active) | with SWAC inactive `MayRequire` silently drops the field and it yields "laa meat" — both are "pass" |
| 13 | Yobshrimp | spawn 12 + one corpse | corpse consumed; **two** "yobshrimp" rows in the wildlife tab if SWAC's is not cut | the second row is the collision (§5.5), not a duplicate def |
| 14 | Silt lamprey | spawn 6 + one downed rat | predator hunt on bs ≤ 0.35 prey | a lamprey that ignores a colonist is correct (bs 1 > 0.35), not passive |
| 15 | Rust nipper | spawn 9 and wound one | ≈ 75 % turn manhunter; claws 7/2 | armor 25/55 makes the *wounding* itself fail with a pistol — use a rifle or the revenge test never starts |
| 16 | Reefback | spawn; leave it alone; then wound it | never attacks unprovoked; after damage 20 % chance of revenge; tail 480/8.5 | 480 vs 100 is invisible against an unarmored pawn (saturation, §2) — test the 0.75 Heat against a blaster, that is the number that differs |
| 17 | Starmaw | as 16 | drawSize 11.4 renders — sprite bounds ~11 cells | a Graphic_Multi with a missing facing renders **nothing**, no magenta (`texture-binds-by-texpath` lesson) — check all four rotations |
| 18 | Lanternwhale | as 16 | MoveSpeed 1.8; eco 4.0 keeps map density at ~1 | `ecoSystemWeight` only meters *wild spawning* in `wildBiomes`; a bridge spawn bypasses it entirely |

## 7. UNMEASURED — the honest gaps

| Item | Why |
|---|---|
| What `pathfinding.framework` needs per race (its MovementDef names/fields) | mod not installed; nothing to read. Measured only after a subscription |
| Actual in-game `MeleeDPS` per creature | the stat folds hit chance and multi-tool weighting (`DebugOutputsPawns.MeleeDps` generates a pawn to read it) — read from the card at the quicktest, do not compute |
| Sound defs (`soundCall` etc.) | no vanilla fish/leviathan sounds exist; SWAC ships `Pawn_Yobshrimp_*` only. All 18 ship silent in v1 (optional fields) |
| `RM_SeafloorBiome` wildBiomes commonalities | biome does not exist; the §5 `eco` column is the density dial, commonality is authored with the biome |
| Litter/gestation for the opee (canon: egg-layer) | `CompEggLayer` needs egg ThingDefs — v2 |

## 8. Naming lint (per `design/NAMING_SCHEME_PLAN.md`)

packageId `mandrake.rsw.seabeasts` · defNames `RSW_*` as tabled · folder
`src/RimStarWars/SeaBeasts/` · namespace `RimMandrake.StarWars.SeaBeasts`
(only if route A in §4 is ever taken) · "Jawa"/"Naboo" appear in lore text
only.
