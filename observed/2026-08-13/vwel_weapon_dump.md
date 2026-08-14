# VWE – Laser: weapon ThingDef dump, by tier

## Provenance

**Read 2026-08-13 from mod source on disk, with the game DOWN.**
This is **not** a live def dump. It reflects **what the mod ships**, not what the
running game holds after VEF, Combat Extended, rebalance patches or any other
mod in the 580-mod stack patches it. Any number here can be overridden at load.

**Mod identity — verified from the ROOT element's direct-child `<packageId>`,**
not from a `<modDependencies>` entry (that file lists three `packageId` nodes;
two are dependencies — `brrainz.harmony` and
`OskarPotocki.VanillaFactionsExpanded.Core`):

| field | value |
|---|---|
| name | Vanilla Weapons Expanded - Laser |
| author | Oskar Potocki |
| root `<packageId>` | `VanillaExpanded.VWEL` |
| `PublishedFileId.txt` | `1989352844` |
| supportedVersions | 1.4, 1.5, 1.6 |
| `LoadFolders.xml` | **absent** — the `1.6/` folder is the whole 1.6 payload |

### Source files read

```
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\About\About.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\About\PublishedFileId.txt
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Defs\ThingDefs_Misc\Weapons\VWEL_Weapons_Ranged_Laser.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Defs\ThingDefs_Misc\Weapons\VWEL_Weapons_Melee_Spacer.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Defs\Motes\VWEL_Abstracts_Laser.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Defs\RecipeDefs\Recipes_Production.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Defs\ResearchProjectDefs\ResearchProjects_Various.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Defs\ResearchProjectDefs\ResearchTabs.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Defs\ThingDefs_Misc\Items_Resource_Manufactured.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Defs\ThingDefs_Misc\Items_Unfinished.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Defs\PawnKindDefs\PawnKinds_Pirate.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Patches\FactionDef_Misc.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\Patches\Ideology.xml
C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.3\Defs\ResearchProjectDefs\ResearchProjects_Various.xml   (historical, see §5)
```

Comparator numbers in §6 were read the same way from
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\ThingDefs_Misc\Weapons\`.

### Enablement status — already done

`vanillaexpanded.vwel` is **already in `<activeMods>`** of
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`,
at index 469 of 580, between `mrhydralisk.voeadditionaloutposts` and
`arcjc007.wallstuff`. VEF core is present. **No ModsConfig edit is needed.**
⚠️ `design/Jawa/worldbuilding/ship_legacy_armoury.md` line 20 still says
"installed and currently inactive" — stale, not mine to fix.

---

## 1. What ships, and the tier split

**12 weapon ThingDefs total: 4 tier-1 "salvaged", 8 tier-2 "ultratech"** (7 ranged
plus the laser sword). Plus 12 projectile ThingDefs (10 distinct; two guns share
one bullet), 1 research project, 1 research tab, 1 recipe, 2 item defs.

The split is expressed in the XML three ways, all consistent:

| | tier 1 — salvaged | tier 2 — ultratech |
|---|---|---|
| abstract parent | `BaseLaserGun` | `VWE_BaseLaserGunUltra` (guns) / `VWE_LaserSwordBase` (sword) |
| `weaponTags` | `SalvagedLaserGun` | `SpacerGun` + `LaserGun` (sword: `UltratechMelee` + `LaserGun`) |
| projectile label | "**unstable** …" | plain |
| projectile `damageDef` | **`Burn`** | `Bullet` (tesla gun: `EMP`) |
| `recipeMaker` | present but `<recipeUsers/>` is **empty** | **none at all** |

⚠️ **`techLevel` is `Ultra` on BOTH tiers, including the salvaged guns.** The only
`Spacer` thing in the mod is the research project. Anything in the stack that keys
off a weapon's `techLevel` (trader stock, tribal/outlander restrictions, ideology
precepts, tech-appropriateness patches) will treat a salvaged laser pistol as
ultratech.

---

## 2. TIER 1 — "salvaged" (4 weapons)

Parent `BaseLaserGun`. All: `techLevel Ultra`, `tradeability All`, `relicChance 2`,
`Flammability 0.5`, `smeltable true`, tradeTag `SpacerGun`, weaponTag
`SalvagedLaserGun`, `generateCommonality 0.1`, `WorkToMake 12500`,
costList **75 Steel / 60 Plasteel / 12 ComponentSpacer** (see §4 — this cost is
never actually paid), `thingSetMakerTags` = `RewardStandardLowFreq`,
`RewardStandardQualitySuper`. All carry `CompQuality` and `CompProperties_Art`
(artistic at Excellent+).

### Weapons

| defName | label | dmg | AP | dmgDef | warmup | cooldown | burst | range | mass | value | tech |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| `VWEL_Gun_SalvagedLaserPistol` | salvaged laser pistol | 12 | **0.60** | Burn | 2.0 | 1.0 | 2 @10t | 19.9 | 1.2 | 1500 | Ultra |
| `VWEL_Gun_SalvagedLaserRifle` | salvaged laser rifle | 13 | **0.56** | Burn | 2.0 | 0.6 | 1 | 31.0 | 2.6 | 1950 | Ultra |
| `VWEL_Gun_SalvagedLaserShotgun` | salvaged laser shotgun | 7 | **0.56** | Burn | 2.2 | 0.6 | 4 @1t | 14.9 | 3.0 | 2050 | Ultra |
| `VWEL_Gun_SalvagedLaserSniperRifle` | salvaged laser sniper rifle | 39 | **1.00** | Burn | 4.6 | 2.2 | 1 | 39.9 | 3.8 | 2200 | Ultra |

### Accuracy by band

| defName | Touch | Short | Medium | Long |
|---|---:|---:|---:|---:|
| `VWEL_Gun_SalvagedLaserPistol` | 0.50 | 0.62 | 0.60 | 0.46 |
| `VWEL_Gun_SalvagedLaserRifle` | 0.60 | 0.73 | 0.76 | 0.62 |
| `VWEL_Gun_SalvagedLaserShotgun` | 0.78 | 0.72 | 0.64 | 0.52 |
| `VWEL_Gun_SalvagedLaserSniperRifle` | 0.54 | 0.75 | 0.82 | 0.78 |

### Projectiles

| bullet defName | label | class | dmgDef | dmg | AP | stopping | speed | causeFire | beamWidth | lifetime |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `VWEL_Bullet_SalvagedLaserPistol` | unstable laser pistol shot | `BaseBullet` (ordinary projectile) | Burn | 12 | 0.60 | 0.5 | **85** | – | – | – |
| `VWEL_Bullet_SalvagedLaserRifle` | unstable laser shot | `VEF.Weapons.LaserBeamDef` | Burn | 13 | 0.56 | 1.5 | 10000 | 0.15 | – | – |
| `VWEL_Bullet_SalvagedLaserShotgun` | unstable laser scatter shot | `VEF.Weapons.LaserBeamDef` | Burn | 7 | 0.56 | 2.0 | 10000 | 0 | 1.3 | 60 |
| `VWEL_Bullet_SalvagedLaserSniperRifle` | unstable precise laser shot | `VEF.Weapons.LaserBeamDef` | Burn | 39 | **1.00** | 3.0 | 10000 | 0.2 | 1.5 | 120 |

`speed 10000` is inherited from the abstract `VWEL_Bullet_LaserGeneric` — beam
projectiles are effectively hitscan. Only the two pistols use a normal
`BaseBullet` with a travel speed of 85.

### Overheat comp (`VEF.Weapons.CompProperties_LaserCapacitor`)

| defName | warmupReduction/shot | overheats | chance | blast dmg | extra dmg | radius | destroys |
|---|---:|---|---:|---|---:|---:|---|
| SalvagedLaserPistol | 0.23 | yes | 0.10 | Burn | 4 | 1.0 | no |
| SalvagedLaserRifle | 0.25 | yes | 0.10 | Burn | 4 | 1.5 | no |
| SalvagedLaserShotgun | 0.30 | yes | 0.10 | Burn | 8 | 1.5 | no |
| SalvagedLaserSniperRifle | **1.50** | yes | 0.10 | Burn | 8 | 1.5 | no |

Melee tools on every salvaged gun: barrel Blunt 5 / cd 1.8, grip Blunt 6 / cd 1.9.

### How obtained

**Not craftable directly.** `BaseLaserGun`'s `recipeMaker` has
`researchPrerequisite VWE_LaserWeapons`, `unfinishedThingDef
UnfinishedSalvagedLaserGun`, `workSkill Intellectual` — but `<recipeUsers/>` is
**empty**, so the generated `Make_` recipe appears at no bench.

The one route is the **random-outcome** chain:

1. Research **`VWE_LaserWeapons`** — label *"salvaged laser weapons"*,
   `baseCost 6000`, `techLevel Spacer`, tab `VanillaExpanded`,
   prerequisite **`ChargedShot`**, requires **HiTechResearchBench + MultiAnalyzer**.
2. Recipe **`Salvage_LaserWeapon`** at **`FabricationBench`** —
   `workAmount 10000`, `workSpeedStat ResearchSpeed`, `workSkill Intellectual`,
   **`Intellectual 10` required**. Ingredients: **6 `ComponentSpacer` + 30 `Plasteel`**.
   Product: 1 × `LaserRandom`.
3. `LaserRandom` ("salvaged laser weapon", `MarketValue 1`, `Mass 0.6`,
   `DeteriorationRate 2.0`, `stackLimit 1`) carries
   `VEF.Things.CompProperties_RandomOutcomeComp` with
   `canProvideTags: SalvagedLaserGun` — it resolves into **one of the four
   salvaged weapons at random**, with quality.

Also obtainable via trade (`tradeability All`, tradeTag `SpacerGun`) and quest
rewards. **No pawnkind in this mod carries the salvaged tier** — see §5.

---

## 3. TIER 2 — "ultratech" (8 weapons)

Guns parent `VWE_BaseLaserGunUltra`; sword parent `VWE_LaserSwordBase`. All:
`techLevel Ultra`, `tradeability All`, `generateCommonality 0.1`, `CompQuality` +
`CompProperties_Art`. Guns: `relicChance 2`, `smeltable true`, weaponTags
`SpacerGun` + `LaserGun`, thingSetMakerTags `RewardStandardLowFreq` /
`RewardStandardQualitySuper`. Sword: `relicChance 3`, `smeltable false`,
thingSetMakerTag **`RewardSpecial`**.

### Ranged weapons

| defName | label | dmg | AP | dmgDef | warmup | cooldown | burst | range | mass | value | WorkToMake | tech |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| `VWEL_Gun_LaserPistol` | laser pistol | 13 | 0.66 | Bullet | 2.0 | 1.0 | 2 @10t | 23.9 | 1.2 | 2000 | 82500 | Ultra |
| `VWEL_Gun_LaserSMG` | laser SMG | 13 | 0.66 | Bullet | 2.0 | 1.9 | 3 @10t | 23.9 | 1.8 | 2400 | 82500 | Ultra |
| `VWEL_Gun_LaserRifle` | laser rifle | 12 | 0.60 | Bullet | 2.0 | 0.6 | 2 @10t | 32.9 | 2.6 | 3000 | 102500 | Ultra |
| `VWEL_Gun_LaserShotgun` | laser shotgun | 11 | 0.56 | Bullet | 2.2 | 0.6 | 4 @1t | 14.9 | 3.0 | 3200 | 102500 | Ultra |
| `VWEL_Gun_LaserSniperRifle` | laser sniper rifle | **48** | **1.00** | Bullet | 4.6 | 2.2 | 1 | **44.9** | 3.8 | 3600 | 120500 | Ultra |
| `VWEL_Gun_LaserMinigun` | laser minigun | 10 | 0.32 | Bullet | 4.0 | **0.2** | **8 @14t** | 29.9 | 12.0 | 4500 | 125000 | Ultra |
| `VWEL_Gun_TeslaGun` | tesla gun | 15 | 0.45 | **EMP** | 2.4 | 1.0 | 1 | 18.9 | 8.0 | 3000 | 125000 | Ultra |

⚠️ **`VWEL_Gun_LaserSMG` fires `VWEL_Bullet_LaserPistol`** — it has no bullet of
its own. Ordinary VE practice, but note it when normalising: retuning the pistol
bullet retunes the SMG.

⚠️ **`VWEL_Gun_TeslaGun` sets `weaponTags Inherit="False"` to `LaserGun` only** —
it drops `SpacerGun`, unlike its six siblings. It still has the `SpacerGun`
*tradeTag* from the parent, so traders stock it; the missing weaponTag only
affects weapon-tag-driven pawn generation.

### Accuracy by band

| defName | Touch | Short | Medium | Long |
|---|---:|---:|---:|---:|
| `VWEL_Gun_LaserPistol` | 0.80 | 0.72 | 0.70 | 0.56 |
| `VWEL_Gun_LaserSMG` | 0.80 | 0.74 | 0.70 | 0.46 |
| `VWEL_Gun_LaserRifle` | 0.70 | 0.83 | 0.86 | 0.72 |
| `VWEL_Gun_LaserShotgun` | 0.88 | 0.82 | 0.74 | 0.62 |
| `VWEL_Gun_LaserSniperRifle` | 0.64 | 0.85 | **0.92** | **0.90** |
| `VWEL_Gun_LaserMinigun` | 0.54 | 0.66 | 0.74 | 0.70 |
| `VWEL_Gun_TeslaGun` | **1.00** | **1.00** | **1.00** | **0.90** |

### Projectiles

| bullet defName | label | class | dmgDef | dmg | AP | stopping | causeFire | beamWidth | lifetime |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| `VWEL_Bullet_LaserPistol` | laser pistol shot | `BaseBullet`, speed **85** | Bullet | 13 | 0.66 | 0.5 | – | – | – |
| `VWEL_Bullet_LaserRifle` | laser shot | `LaserBeamDef` | Bullet | 12 | 0.60 | 1.5 | 0.10 | – | – |
| `VWEL_Bullet_LaserShotgun` | laser scatter shot | `LaserBeamDef` | Bullet | 11 | 0.56 | 2.0 | 0 | 1.3 | 60 |
| `VWEL_Bullet_LaserSniperRifle` | precise laser shot | `LaserBeamDef` | Bullet | **48** | **1.00** | 3.0 | 0.20 | 1.5 | 120 |
| `VWEL_Bullet_LaserMinigun` | laser minigun shot | `LaserBeamDef` | Bullet | 10 | 0.32 | 1.0 | 0 | – | – |
| `VWEL_Bullet_TeslaGun` | tesla shot | `LaserBeamDef`, `Graphic_Flicker` | **EMP** | 15 | 0.45 | 1.0 | 0.05 | **4.0** | 120 |

The tesla shot's **`beamWidth 4`** is the widest in the mod by ~2.7×.

### Overheat comp

| defName | warmupReduction/shot | overheats | chance | blast dmg | extra dmg | radius | MoveSpeed offset |
|---|---:|---|---:|---|---:|---:|---:|
| LaserPistol | 0.30 | yes | 0.05 | Burn | 2 | 1.0 | – |
| LaserSMG | 0.50 | yes | 0.10 | Burn | 2 | 1.5 | – |
| LaserRifle | 0.225 | yes | 0.05 | Burn | 3 | 1.5 | – |
| LaserShotgun | 0.175 | yes | 0.06 | Burn | 3 | 1.5 | – |
| LaserSniperRifle | **1.80** | yes | 0.06 | Burn | 6 | 1.5 | **−0.15** |
| LaserMinigun | 0.55 | yes | 0.06 | **Flame** | 6 | 1.5 | **−0.25** |
| TeslaGun | 0.20 | **no** | 0.08 | Flame | 0 | 3.5 | **−0.25** |

`OverheatDestroys` is `false` on every weapon in the mod — nothing self-destructs.
Melee tools on every tier-2 gun: barrel Blunt 5 / cd 1.8, grip Blunt 6 / cd 1.9.

### Melee — `VWEL_LaserSword`

| field | value |
|---|---|
| defName / label | `VWEL_LaserSword` / laser sword |
| thingClass | `VEF.Graphics.ThingWithFloorGraphic` (on/off blade art via `FloorGraphicExtension`) |
| techLevel | Ultra |
| mass | 1.4 |
| market value | 2000 |
| WorkToMake | 18000 |
| costList | 30 Steel / 100 Plasteel / 10 ComponentSpacer |
| weaponTags | `UltratechMelee`, `LaserGun` |
| weaponClasses | Melee, MeleePiercer (+`Ultratech` with Ideology loaded) |
| relicChance | 3 · thingSetMakerTag `RewardSpecial` · `smeltable false`, `burnableByRecipe true` |

| tool | capacity | power | AP | cooldown | DPS |
|---|---|---:|---:|---:|---:|
| handle | Blunt | 9 | (default) | 2.0 | 4.5 |
| point | **Cut** | **31** | **1.00** | 2.6 | 11.9 |
| blade | **Cut** | **31** | **1.00** | 2.6 | 11.9 |

### How obtained

**Not craftable at all.** `VWE_BaseLaserGunUltra` and `VWE_LaserSwordBase` have
**no `recipeMaker` node**, and no research project in the 1.6 payload unlocks
them. Routes are: trade (tradeTag `SpacerGun`), quest/reward drops
(`RewardStandardLowFreq`, `RewardStandardQualitySuper`, sword `RewardSpecial`),
relics, and **loot from `Mercenary_Marine` pirates** (§5).

The `costList` on tier-2 weapons is therefore never paid — it feeds smelting
yield and value calculations only.

---

## 4. Craftability summary — the load-bearing fact

| tier | research | bench | direct recipe? | actual route |
|---|---|---|---|---|
| salvaged (4) | `VWE_LaserWeapons`, 6000pt, Spacer | FabricationBench | **no** (`recipeUsers` empty) | `Salvage_LaserWeapon` → `LaserRandom` → random 1-of-4 |
| ultratech (8) | **none exists** | **none** | **no** (`recipeMaker` absent) | loot / trade / quest / relic only |

---

## 5. Distribution to other factions — this ships ON by default

`1.6\Defs\PawnKindDefs\PawnKinds_Pirate.xml` defines:

```
PawnKindDef Mercenary_Marine  (ParentName MercenaryEliteTierBase)
  defaultFactionType Pirate      combatPower 300
  weaponMoney 2500~4400          weaponTags Inherit="False" → LaserGun
  apparelMoney 4500~5500         apparelTags → SpacerMilitary
  techHediffsMoney 1000~1200     techHediffsChance 0.65   techHediffsTags Advanced
  combatEnhancingDrugsChance 0.80
```

`1.6\Patches\FactionDef_Misc.xml` then `PatchOperationAdd`s a `Combat` pawn group
maker to `FactionDef[defName="Pirate"]` with **`commonality 10`** and
`Mercenary_Marine: 5`.

🔴 **`weaponTags` is `LaserGun` — the TIER-2 tag.** Salvaged weapons carry
`SalvagedLaserGun` and are therefore **never** generated on these pawns. So as
shipped, **pirates field the full ultratech tier and never the salvaged tier** —
the exact inverse of what
`design/Jawa/worldbuilding/ship_legacy_armoury.md` §"the coherence rule" wants.
That doc's assumption ("the mod's own two-tier split does this for us") does not
hold; the split runs the wrong way round.

⚠️ And because tier 2 has no research and no recipe (§4), **removing
`Mercenary_Marine` from pirate groups removes the main in-game source of the full
tier**, leaving only trade and quest rolls. Cutting distribution and adding a
craft path are one job, not two.

`1.6\Patches\Ideology.xml` (guarded by `PatchOperationFindMod` on Ideology) adds
`weaponClasses`: sword → `Ultratech`; pistols → `RangedLight`; tesla gun and
minigun → `RangedHeavy`; shotgun → `RangedHeavy` + `ShortShots`.

### Historical note — the ultratech research was removed upstream

The second research project **existed in 1.2 and 1.3 and was deleted in 1.4**:

```
1.2 → present   1.3 → present   1.4 → absent   1.5 → absent   1.6 → absent
```

`1.3\Defs\ResearchProjectDefs\ResearchProjects_Various.xml:24` held
`VWE_UltratechLaserWeapons`, label *"ultratech laser weapons"*, `baseCost 12000`,
`techLevel Ultra`, prerequisite `VWE_LaserWeapons`, HiTechResearchBench +
MultiAnalyzer. It is gone from every currently-supported version.

---

## 6. What looks out of line for a mid-tech scavenger campaign

Comparators read from Core this session. Vanilla bullets with no explicit
`armorPenetrationBase` use the engine default `damage × 0.015`; those values are
marked *(derived)*.

| weapon | dmg | AP | range | warmup | cooldown | burst | cycle DPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| vanilla sniper rifle | 25 | 0.375 *(derived)* | 44.9 | 3.5 | 1.5 | 1 | 5.0 |
| vanilla charge lance | 30 | 0.45 *(derived)* | 32.9 | 1.7 | 2.7 | 1 | 6.8 |
| vanilla charge rifle | 16 | 0.35 | 27.9 | 1.0 | 2.0 | 3 | — |
| vanilla monosword (edge) | 25 | 0.90 | melee | – | 2.0 | – | 12.5 |
| **salvaged laser sniper** | 39 | **1.00** | 39.9 | 4.6 | 2.2 | 1 | **5.7** |
| **laser sniper rifle** | **48** | **1.00** | **44.9** | 4.6 | 2.2 | 1 | **7.1** |
| **laser sword (edge)** | 31 | **1.00** | melee | – | 2.6 | – | 11.9 |

Cycle DPS = `burst × damage ÷ (warmup + cooldown + (burst−1) × ticksBetween/60)`,
ignoring accuracy and the capacitor.

**1. 🔴 100% armor penetration appears in TIER ONE.** `VWEL_Bullet_SalvagedLaserSniperRifle`
is 39 damage at **AP 1.00** out to 39.9 tiles. Nothing in vanilla reaches AP 1.00
at range — the charge lance tops out near 0.45. The first "cobbled-together,
half-understood schematic" weapon the clan builds **ignores all armor**, which is
the opposite of what the design fiction says it should feel like. This is the
single worst fit, and it is on the tier the design wants circulating freely on
raiders.

**2. 🔴 The tesla gun cannot miss.** `AccuracyTouch/Short/Medium = 1.00`, Long 0.90,
`Overheats false`, `beamWidth 4`, `damageDef EMP`. Perfect accuracy at three of
four bands plus a 4-wide beam plus EMP is a hard counter to every mechanoid and
every shield-belt user in the stack, with no drawback beyond −0.25 move speed and
18.9 range. It is priced at 3000 — *cheaper than the laser sniper*.

**3. The laser sword beats a monosword on AP and matches it on damage.** 31 Cut at
AP 1.00 vs 25 Cut at AP 0.90, for a market value of 2000. Combined with
`relicChance 3` and `RewardSpecial`, it will show up in quest rolls. This is the
weapon `ship_legacy_armoury.md` already flagged against
`design/Jawa/force_users_build_spec.md` — the numbers say a common laser sword
would out-stat most lightsaber implementations, so that decision is not cosmetic.

**4. The salvaged tier is arguably too *weak* on damage type, not too strong.**
All four salvaged projectiles use **`Burn`** rather than `Bullet`: no bleeding,
and heat-resistant armor applies. Salvaged sniper 39 Burn will underperform its
number badly against armored targets, while its AP 1.00 makes it overperform
against unarmored ones. Swingy in both directions — a normalisation candidate.

**5. Gating is inverted for a scavenger campaign.** The *salvaged* tier —
narratively the early, crude one — sits behind 6000 research points, `ChargedShot`,
a HiTechResearchBench **and** a MultiAnalyzer, then costs 6 `ComponentSpacer` +
30 Plasteel and 10000 work per **random** gun, needing Intellectual 10. That is
late-game. Meanwhile the *ultratech* tier needs no research at all and arrives
free off a dead pirate from the first Mercenary_Marine raid. A mid-tech scavenger
clan will therefore meet tier 2 long before it can make tier 1.

**6. Minor: mass 12 on the laser minigun** (vanilla minigun is 10) with 8-shot
bursts at 0.2s cooldown — 13.7 cycle DPS but only AP 0.32. Not out of line; noted
for completeness.

**7. Caveat on all DPS figures.** `VEF.Weapons.CompProperties_LaserCapacitor`
reduces warmup by `WarmUpReductionPerShot` for each consecutive shot while
standing still, so sustained DPS is **higher** than the table above — materially
so for the snipers (1.8 and 1.5 per shot against a 4.6s warmup). The floor and
exact stacking rule live in the VEF assembly, **not read this session**; treat
sustained numbers as unverified until measured in-game.

---

## 7. Related prior work

`D:\Luke\dev\Rimworld\observed\2026-08-13_vwel_armoury_dump.md` covers the same
mod from the same source and reaches the same conclusions on craftability and the
missing 1.4+ research project. This file supersedes nothing; it adds the full
per-band accuracy, projectile and overheat-comp tables and the vanilla
comparison.
