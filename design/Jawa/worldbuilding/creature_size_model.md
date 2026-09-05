# Creature size model — bodySize, drawSize, the render, and the review sheet

**Status: DECIDED, 2026-09-05.** Settles how the creature review sheet sizes a creature,
and at what pixel resolution its art is generated. Grounded in RimWorld 1.6 decompiled
source (RimSage) and in the vanilla `Core` defs on disk. Every claim below is tagged
**MEASURED** (read out of source or defs) or **INFERRED** (a judgement built on those).

Source roots used:
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\ThingDefs_Races\`
and the decompiled tree behind `mcp__rimsage__*` (`Source/Verse`, `Source/RimWorld`).

---

## 1. The two fields are unrelated in the engine

### `bodySize` — `RaceProperties.baseBodySize` (`Source/Verse/RaceProperties.cs:188`)

The live value is **MEASURED** at `Source/Verse/Pawn.cs:2499`:

```
public float BodySize => ageTracker.CurLifeStage.bodySizeFactor * RaceProps.baseBodySize;
```

so a life stage multiplies it (`LifeStageDef.bodySizeFactor`, `LifeStageDef.cs:70`).

**It drives (all MEASURED):**

| consumer | where | effect |
|---|---|---|
| **Mass** | `StatPart_BodySize` (`val *= bodySize`), attached to `StatDefOf.Mass` in `Stats_Basics_General.xml` | mass = 1 × bodySize (base 1) |
| **Nutrition** (of the corpse/creature) | same StatPart, `Stats_Basics_General.xml` | |
| **MeatAmount** | same StatPart, `Stats_Pawns_General.xml`, base 140 | butchery yield |
| **LeatherAmount** | same StatPart, `Stats_Pawns_General.xml` | leather yield |
| **CarryingCapacity** | same StatPart, base 75 | what an animal hauls |
| **MaxNutrition** | same StatPart, base 1 | |
| caravan carry capacity | `MassUtility.cs:10,85` — `MassCapacityPerBodySize = 35f`, `p.BodySize * 35f` | |
| **food tank size** | `Need_Food.cs:77` — `MaxLevel = pawn.BodySize * CurLifeStage.foodMaxFactor` | how *long* between meals |
| **ranged hit chance against it** | `ShotReport.cs:129` `factorFromTargetSize = pawn.BodySize`; `ShootTuning.cs` clamps 0.1–2.0 | a bigger animal is easier to shoot |
| stray-bullet interception | `Projectile.cs:367,534` — `0.4f/0.5f * Clamp(BodySize, 0.1, 2)` | |
| bullet stagger immunity | `StaggerHandler.cs:49` — no stagger if `BodySize > stoppingPower` | |
| predation | `RaceProperties.maxPreyBodySize` (`:96`), `FoodUtility.cs:781,791` | who may eat whom, and who wins |
| pen/pasture load | `AnimalPenBalanceCalculator.cs:46-62` | grazing pressure |
| bed fit | `bed_maxBodySize` (`BuildingProperties.cs:178`), `RestUtility.cs:426` | |
| trainability gate | `TrainableDef.minBodySize`, `Pawn_TrainingTracker.cs:128-152` | |
| caravan visibility | `CaravanVisibilityCalculator.cs` | |
| bleed rate, blood on execution, rot stink, drug dose, cell-sharing, footprint/ripple size, herd-migration counts, ideoligion animal-per-capita thoughts | `Pawn_HealthTracker.cs:1222`, `ExecutionUtility.cs:24`, `GasUtility.cs:14,96`, `AddictionUtility.cs:93-95`, `PawnUtility.cs:603-611`, `PawnFootprintMaker.cs:49`, `IncidentWorker_HerdMigration.cs:116`, `ThoughtWorker_Precept_AnimalBodySizePerCapita.cs` | |

**It does NOT drive (MEASURED by absence across the whole `bodySize` source sweep):**

- **Health.** Hit-point scaling is `RaceProperties.baseHealthScale`, a separate field.
  `bodySize` never multiplies health. A `bodySize` 0.2 creature can have `healthScale` 5.
- **Melee damage or melee hit chance.** Melee comes entirely from `tools` (`power`,
  `cooldownTime`) on the ThingDef. `bodySize` appears nowhere in `Verb_MeleeAttack`,
  `DamageWorker_AddInjury` or the melee stat workers. The only combat coupling is that a
  larger creature is **easier to shoot** (`ShotReport`) and **harder to stagger**.
- **Move speed** (`StatDefOf.MoveSpeed`, its own stat), **pain/downed thresholds**
  (`PawnCapacityUtility` + `RaceProperties`), **hunger *rate*** (`Need_Food.BaseHungerRate`
  = `lifeStage.hungerRateFactor * race.baseHungerRate`, `Need_Food.cs:216` — bodySize is
  absent), **combat power** (`PawnKindDef.combatPower`, hand-authored).
- **Anything the renderer draws.** No draw path reads `baseBodySize`.

⇒ **INFERRED, and this is the core finding:** `bodySize` is a *mass/volume/logistics*
number, not a might number. "Physics" here means mass, yield, haul, food tank, and
being-shot-at — not hitting harder.

### `drawSize` — `GraphicData.drawSize` (`Source/Verse/GraphicData.cs:29`)

**MEASURED.** For an animal the rendered size comes from the **PawnKindDef life stage**,
not the ThingDef:

- `PawnRenderNode_AnimalPart.GraphicFor` reads
  `pawn.ageTracker.CurKindLifeStage.bodyGraphicData` (`PawnRenderNode_AnimalPart.cs:25-28`).
- `PawnRenderNode_AnimalPart.MeshSetFor` returns
  `MeshPool.GetMeshSetForSize(graphic.drawSize.x, graphic.drawSize.y)` — **the quad is
  exactly `drawSize` cells, with no `bodySize` term anywhere on the path**
  (`PawnRenderNode_AnimalPart.cs:12-17`).
- `GraphicData.Init` passes `drawSize` straight into `GraphicDatabase.Get`
  (`GraphicData.cs:151`); `Graphic.drawSize` defaults to `Vector2.one` (`Graphic.cs:73`).

**Life stages do NOT scale the animal draw.** Each `lifeStages` entry of the PawnKindDef
carries its **own** `bodyGraphicData/drawSize`, and the renderer uses the current stage's
value verbatim. `bodySizeFactor` scales the *physics* number only. Consequence
(**MEASURED**): reading the **last** life stage's `drawSize` — which is what
`gen_creature_register.py:542` already does — **is** the adult rendered size. Correct as
built.

Two vanilla places multiply a drawSize by `bodySizeFactor`, and neither is the pawn body:
`MoteAttached.cs:52` (mote placement) and `TargetHighlighter.cs:67` (the selection ring).
The highlight ring is therefore mis-sized on any modded animal whose life-stage drawSizes
already encode growth — a vanilla bug, and **not** evidence that the body is scaled.

⇒ **`drawSize` is purely the rendered quad in cells. It feeds no physics, no stat, no
combat, no capacity.** The only non-visual thing it touches is
`Building_MechGestator.cs:249` (does a formed mech fit in the gestator).

---

## 2. How vanilla relates them — MEASURED

66 vanilla animals + mechanoids parsed from `Core/Defs/ThingDefs_Races/Races_*.xml`
(abstract `ParentName` inheritance resolved; `drawSize` from the last life stage of the
matching PawnKindDef; `max(x,y)` where the vector is non-square).

**Fit (log-log least squares):**

```
drawSize  ≈  1.995 · bodySize^0.375           R² = 0.71,  n = 66
```

Scatter is **wide**: geometric σ = 1.22 (±22 %), full residual range 0.63×–1.75×.
Restricted to `bodySize ≥ 1.0` the exponent rises to 0.427 (k = 1.96) — still nowhere near
linear.

The ratio itself tells the story more plainly:

| bodySize | example | drawSize | drawSize / bodySize |
|---|---|---|---|
| 0.20 | Rat / Squirrel / Hare | 1.25 – 1.50 | **6–7.5** |
| 0.32 | Cat | 1.00 | 3.1 |
| 0.75 | Sheep | 1.75 | 2.3 |
| 1.00 | Ostrich / Cougar | 1.80 – 2.18 | ~2.0 |
| 2.40 | Muffalo / Cow / Horse | 2.10 – 3.00 | 0.9–1.25 |
| 4.00 | Elephant / Thrumbo / Megasloth | 3.80 – 4.80 | **0.95–1.2** |

⇒ **INFERRED:** vanilla does **not** treat the two as harmonized in a physical sense, and
that is deliberate. Small animals get **massively inflated** sprites — a rat is drawn ~6×
larger than its mass implies — because a physically honest rat would be a 3-pixel smear
that no player could click. The relationship converges to ~1:1 only above `bodySize` 2.5.
The engine's own implied law is `k ≈ 2.0, p ≈ 0.375` — **flatter** than the `1.5 ×
bodySize^0.6` currently in the sheet, which over-shrinks the small end and over-grows the
large end relative to what the game actually draws.

**Modded population (595-mod register, n = 1163, MEASURED):** `drawSize ≈ 2.15 ·
bodySize^0.439` — the same law, slightly steeper, with far wider scatter (geometric σ =
1.37; only 62 % of creatures land within 2× of the vanilla-implied sprite size).

---

## 3. THE DECISION — what the review sheet shows

🔑 **Show BOTH, and show the mismatch. Do not force one number.**

The honest answer is that these are two different facts about a creature and collapsing
them loses the thing the owner asked to see. So:

### 3a. The sprite is drawn at `drawSize` cells. Always.

```
review_cells  =  max(drawSize.x, drawSize.y)          # adult = LAST life stage
```

**MEASURED-correct by construction:** this is byte-for-byte what
`PawnRenderNode_AnimalPart.MeshSetFor` hands the mesh pool. The sheet then matches the
game pixel for pixel, at any zoom, for every creature — no fitted constant, no tuning, no
drift when a mod updates. The `1.5 · bodySize^0.6` ladder is **retired**: it was a guess
that disagreed with the render, which is the defect this pass exists to close.

Fallbacks, in order, when `drawSize` is absent:
1. `1.995 · bodySize^0.375` (the vanilla law) — a *predicted* render size, badged as such.
2. `SPECIAL_FALLBACK_CELLS` (8.0) for a `bodySize`-less C#-driven special (the SandWorm).

### 3b. Beside it, the physical/mass size — as a NUMBER and a BADGE, not a second sprite.

```
mass_kg        =  bodySize × 1.0        (StatDefOf.Mass base = 1; MEASURED)
physical_cells =  1.995 · bodySize^0.375        # what vanilla WOULD draw at that mass
mismatch       =  review_cells / physical_cells
```

`mismatch` is the one number that answers "does the physics match what I'm looking at":

| mismatch | badge | meaning |
|---|---|---|
| 0.67 – 1.5 | *(none)* | in the vanilla band. 62 % of the register. |
| 1.5 – 2.5 or 0.4 – 0.67 | ⚠️ **oversized / undersized** | outside the vanilla scatter but survivable |
| > 2.5 or < 0.4 | 🔴 **broken** | looks like a different animal than it weighs |

⇒ **Why this harmonizes.** The picture is the truth of the render (3a), so what the owner
sees is what the game shows. The number and badge are the truth of the physics (3b), so
he can see a Spinosaurus that fills 11 cells and weighs 5.75 kg-equivalent and *know* it
in one glance. Neither fact is faked into the other. **The sheet stops being a guess and
becomes two measurements plus one derived flag.**

⚠️ **The mismatch flag is a DIAGNOSIS, never a fix.** Resolving it means editing either
`bodySize` (mass, yield, haul, shootability) or `drawSize` (the sprite alone) in the def —
and which one is wrong is a design call per creature, not a formula.

---

## 4. Art-generation resolution — the formula

Reconciled with `skills/generating-rimworld-sprites/SKILL.md` §"128 px per cell" (owner's
ruling, 2026-08-23) and with §3a above, since **the size the art must serve is
`drawSize`** — never the physical size, and never the sheet's old ladder.

```
target_px      =  ceil_pow2( max(drawSize.x, drawSize.y) × 128 )
generate_px    =  min( target_px, 1024 )        # the generator's real ceiling
achieved_ppc   =  generate_px / max(drawSize.x, drawSize.y)      # RECORD THIS in PLAN.md
```

with a floor of **256 px** — never below, even for a `drawSize` 1.0 creature (owner's
tiebreak: when uncertain, prefer higher resolution; 256 costs nothing and 128 cannot be
repaired later).

| drawSize | 128 px/cell wants | pow-2 | **generate** | achieved px/cell |
|---|---|---|---|---|
| 1.0 | 128 | 128 | **256** | 256 |
| 1.5 | 192 | 256 | **256** | 171 |
| 2.5 | 320 | 512 | **512** | 205 |
| 4.0 | 512 | 512 | **512** | 128 |
| 8.0 | 1024 | 1024 | **1024** | 128 |
| 11.0 (Spinosaurus) | 1408 | 2048 | **1024** | 93 |
| 15.0 (Balloon) | 1920 | 2048 | **1024** | 68 |

**MEASURED constraint** (SKILL.md:29-38): the image model returns ~1.5 MP natively, so a
canvas past ~1024–1280 px is upscaling — a bigger file with no more detail. Above the cap
the rule is: ship 1024 and **state the achieved px/cell** in that creature's `PLAN.md`.
85–96 px/cell on a leviathan is the ceiling, not sloppy work.

🔑 **Resolution is never a reason to touch `drawSize`, and `drawSize` is never a reason to
touch resolution** (SKILL.md:46). They meet only in this formula.

---

## 5. Defect list — the worst bodySize/drawSize disagreements in the 595-mod set

**MEASURED** from `design/Jawa/worldbuilding/review/creature_register_rows.json`
(built 2026-09-05, 595-mod dump, n = 1163 creatures carrying both fields). Deviation is
`drawSize ÷ (1.995 · bodySize^0.375)` — how many times bigger or smaller the sprite is
than vanilla draws an animal of that mass.

**Population health:** 62 % within 2× · 127 creatures beyond 4× · 24 beyond 10×.

### Looks huge, is mechanically tiny (top 15)

| creature | mod | bodySize | drawSize | ds/bs | sprite vs vanilla-for-that-mass |
|---|---|---|---|---|---|
| Balloon | Alpha Vehicles - Neolithic | 5.00 | 15.00 | 3.0 | **4.11× too big** |
| small butterflies | Alpha Animals | 0.01 | 1.40 | 140.0 | **3.95× too big** |
| locusts | Alpha Animals | 0.01 | 1.40 | 140.0 | **3.95× too big** |
| catchicken | Vanilla Genetics Expanded | 0.26 | 3.50 | 13.7 | **2.93× too big** |
| catalope | Vanilla Genetics Expanded | 0.26 | 3.50 | 13.7 | **2.93× too big** |
| Spinosaurus | Jurassic Rimworld - Dinosaurs Only | 5.75 | 11.00 | 1.9 | **2.86× too big** |
| chem snail | Biomes! Caverns | 0.40 | 4.00 | 10.0 | **2.83× too big** |
| catrabbit | Vanilla Genetics Expanded | 0.30 | 3.50 | 11.7 | **2.76× too big** |
| Indominus rex | Jurassic Rimworld - Dinosaurs Only | 5.00 | 10.00 | 2.0 | **2.74× too big** |
| eopie sled | Alpha Vehicles - Neolithic | 2.00 | 7.00 | 3.5 | **2.71× too big** |
| Tyrannosaurus rex | Jurassic Rimworld - Dinosaurs Only | 5.75 | 10.00 | 1.7 | **2.60× too big** |
| Supersaurus | Jurassic Rimworld - Dinosaurs Only | 5.75 | 10.00 | 1.7 | **2.60× too big** |
| Giganotosaurus | Jurassic Rimworld - Dinosaurs Only | 5.75 | 10.00 | 1.7 | **2.60× too big** |
| Camarasaurus | Jurassic Rimworld - Dinosaurs Only | 5.75 | 10.00 | 1.7 | **2.60× too big** |
| Argentinosaurus | Jurassic Rimworld - Dinosaurs Only | 5.75 | 10.00 | 1.7 | **2.60× too big** |

### Looks tiny, is mechanically huge (worst 10)

| creature | mod | bodySize | drawSize | ds/bs | sprite vs vanilla-for-that-mass |
|---|---|---|---|---|---|
| foundry grub | Biomes! Caverns | 1.80 | 1.10 | 0.6 | **0.44× too small** |
| bloodrop larvae | Biomes! Caverns | 0.70 | 0.80 | 1.1 | **0.46× too small** |
| moss grub | Biomes! Caverns | 0.70 | 0.80 | 1.1 | **0.46× too small** |
| astronaut | Vanilla Gravship Expanded | 1.00 | 1.00 | 1.0 | **0.50× too small** |
| bloodrop pupa | Biomes! Caverns | 1.00 | 1.00 | 1.0 | **0.50× too small** |
| crystalback pupa | Biomes! Caverns | 1.00 | 1.00 | 1.0 | **0.50× too small** |
| foundry pupa | Biomes! Caverns | 1.00 | 1.00 | 1.0 | **0.50× too small** |
| jewel pupa | Biomes! Caverns | 1.00 | 1.00 | 1.0 | **0.50× too small** |
| moss pupa | Biomes! Caverns | 1.00 | 1.00 | 1.0 | **0.50× too small** |
| royal rhino pupa | Biomes! Caverns | 1.00 | 1.00 | 1.0 | **0.50× too small** |

**Reading it (INFERRED):**

- The **Jurassic dinosaurs** are one systematic block: the mod picked its own linear
  `drawSize ≈ 1.7–2 × bodySize` convention at the very top of the range where vanilla sits
  at ~1.0. A 10-cell sprite that butchers like an elephant and hauls like an elephant. Fix
  by **raising `bodySize`**, not by shrinking the art — the art is why the mod exists.
- **Alpha Animals' `bodySize` 0.01 swarms** (butterflies, locusts) are mass-zero on
  purpose — massless swarm chaff. Their 1.4-cell sprite is a *visibility* choice.
  **INFERRED: leave alone**; flag as `intentional`, not as a defect.
- **Vanilla Genetics Expanded chimeras** (catchicken, catalope, catrabbit) at `bodySize`
  0.26 with a 3.5-cell sprite are the real bug class: they read as a big animal, butcher
  for 36 meat, and haul 9 kg. Fix by raising `bodySize`.
- **Biomes! Caverns pupae/grubs** are the mirror: `bodySize` 1.0–1.8 at a 1.0-cell sprite —
  a pupa that weighs as much as a human and hauls like one. Likely the mod inheriting an
  adult `bodySize` onto a larval stage. Fix by **lowering `bodySize`**.
- **`astronaut` (Vanilla Gravship Expanded)** at `bodySize` 1.0 / `drawSize` 1.0 is a
  *humanlike* convention, not an animal one, and is a false positive of the animal law.
  **INFERRED: exclude humanlikes from the mismatch badge.**

---

## 6. What was NOT confirmed

- **Not confirmed from source:** whether any of the 595 mods Harmony-patches the draw path
  to reintroduce a `bodySize` term (e.g. a "realistic animal sizes" mod). The decompiled
  tree is vanilla only. If such a patch is live, §3a's identity between sheet and render
  breaks for whatever it touches. Checking it needs a live capture, not source.
- **Not measured:** the register's `drawSize` for creatures whose art is C#-driven rather
  than a `GraphicData` quad (the SandWorm). §3a's fallback 2 covers them by fiat.
- **Not measured:** whether `femaleGraphicData` ever carries a different `drawSize` from
  `bodyGraphicData` in this mod set. The renderer would honour it
  (`PawnRenderNode_AnimalPart.cs:28`); the register reads `bodyGraphicData` only.

---

## Plants do NOT follow the creature rule (measured 2026-09-05, plant register)

`Plant.Print` builds the quad as
`Vector2(drawSize.x * visualSizeRange.Lerp(growth), <same value>)` — so:
- **`drawSize.y` is never read**; the plant quad is always SQUARE.
- Size scales with GROWTH, so a plant's on-screen size changes as it matures.
- **Mature size = `drawSize.x * visualSizeRange.max`** — that, not `max(drawSize)`,
  is the number a plant review sheet must show.
- Multi-mesh plants (4/9/16/25 sub-meshes) are tiled the way the engine tiles them.

⇒ The creature rule (`max(drawSize.x, drawSize.y)`) is WRONG for plants. Each
category must be checked against its own engine draw path rather than inheriting
the animal one — buildings use their `size` footprint, plants use the growth-lerped
square above.
