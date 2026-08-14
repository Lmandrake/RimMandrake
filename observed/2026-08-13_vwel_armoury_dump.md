# Vanilla Weapons Expanded – Laser: weapon def dump, two tiers, kept separate

_OPS, 2026-08-13. Offline read of the on-disk defs. Game DOWN, nothing enabled,
disabled or written outside this file. Answers the open questions in
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\ship_legacy_armoury.md`._

---

## Which folder I read, and why

**Read: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\1989352844\1.6\`**

- `About\About.xml` gives `<packageId>VanillaExpanded.VWEL</packageId>` — matches
  `vanillaexpanded.vwel` in `<activeMods>` (line 474 of `ModsConfig.xml`), so the
  folder id is confirmed, not assumed. `<supportedVersions>` = 1.4, 1.5, 1.6.
- **There is no `LoadFolders.xml` anywhere in the mod** —
  `find . -iname "loadfolders.xml"` returns nothing. So RimWorld's default
  versioned-folder resolution applies: root (`About`, `Textures`, `Sounds` — no
  root `Defs`) plus the `1.6` folder only. `1.2`–`1.5` are dead weight under 1.6.
- ⚠️ **This mattered.** `diff -rq 1.5 1.6` reports **four** files differing,
  including `Defs\ThingDefs_Misc\Weapons\VWEL_Weapons_Ranged_Laser.xml` — the
  weapon file itself. Reading `1.5` would have produced wrong numbers.

Files that carry the armoury:

```
1.6\Defs\ThingDefs_Misc\Weapons\VWEL_Weapons_Ranged_Laser.xml   (1193 lines)
1.6\Defs\ThingDefs_Misc\Weapons\VWEL_Weapons_Melee_Spacer.xml   (105 lines)
1.6\Defs\ResearchProjectDefs\ResearchProjects_Various.xml
1.6\Defs\RecipeDefs\Recipes_Production.xml
1.6\Defs\PawnKindDefs\PawnKinds_Pirate.xml
1.6\Patches\FactionDef_Misc.xml
1.6\Patches\Ideology.xml
```

---

## The field I split on

🔴 **`weaponTags`.** Salvaged weapons declare exactly one tag,
`<li>SalvagedLaserGun</li>`; every full-tier weapon declares `<li>LaserGun</li>`
(the ranged ones also `SpacerGun`, the sword also `UltratechMelee`). Both
override with `Inherit="False"`, so no inheritance ambiguity.

Example — `VWEL_Gun_SalvagedLaserRifle`, line 930:

```xml
<weaponTags Inherit="False">
    <li>SalvagedLaserGun</li>
</weaponTags>
```

versus `VWEL_Gun_LaserRifle`, line 304:

```xml
<weaponTags Inherit="False">
    <li>SpacerGun</li>
    <li>LaserGun</li>
</weaponTags>
```

**Three other fields split identically and confirm it** — abstract parent
(`BaseLaserGun` vs `VWE_BaseLaserGunUltra`), `defName` prefix
(`VWEL_Gun_Salvaged*`), and projectile label (every salvaged projectile is
labelled `unstable …`). **The split is clean. Nothing is ambiguous.**

🔴 **`techLevel` does NOT split them — that is the trap.** All eleven guns and the
sword declare `<techLevel>Ultra</techLevel>`, salvaged included. Anyone splitting
on tech level gets one bucket of twelve. (Only the *research project* is
`Spacer`.)

The `damageDef` of the projectile nearly splits too — salvaged all fire `Burn`,
full tier fires `Bullet` — but the tesla gun fires `EMP`, so it is corroborating
evidence, not the discriminator. ⚠️ The mod's own `changelog.txt` claims
"Salvaged laser rifle — Damage type Burn -> Bullet"; **the 1.6 file still says
`Burn`.** Trust the file.

### Counts, with the commands

```
$ cd '.../1989352844/1.6/Defs/ThingDefs_Misc/Weapons'
$ grep -c "defName>VWEL_Gun_"          VWEL_Weapons_Ranged_Laser.xml   -> 11
$ grep -c "defName>VWEL_Gun_Salvaged"  VWEL_Weapons_Ranged_Laser.xml   ->  4
$ grep -c "<li>SalvagedLaserGun</li>"  VWEL_Weapons_Ranged_Laser.xml   ->  4
$ grep -c "defName>VWEL_"              VWEL_Weapons_Melee_Spacer.xml   ->  1
```

**Salvaged tier: 4 weapons. Full/ultratech tier: 8 (7 ranged + 1 melee).
Total 12.**

---

## TIER 1 — SALVAGED (4 weapons, all firing `unstable` projectiles)

Common to all four: `techLevel` Ultra, `WorkToMake` 12500, `costList`
Steel 75 / Plasteel 60 / ComponentSpacer 12, `weaponTags` = `SalvagedLaserGun`,
`generateCommonality` 0.1, `soundInteract` `VWE_Interact_UnstableLaserGun`,
overheat chance 0.10.

| defName | label | dmg | AP | range | warmup | cooldown | burst | mass | value | tech | research | projectile |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `VWEL_Gun_SalvagedLaserPistol` | salvaged laser pistol | **12** `Burn` | 0.60 | 19.9 | 2.0 | 1.0 | 2 | 1.2 | 1500 | Ultra | `VWE_LaserWeapons` † | `VWEL_Bullet_SalvagedLaserPistol` ⚠️ *unstable laser pistol shot* |
| `VWEL_Gun_SalvagedLaserRifle` | salvaged laser rifle | **13** `Burn` | 0.56 | 31.0 | 2.0 | 0.6 | 1 | 2.6 | 1950 | Ultra | `VWE_LaserWeapons` † | `VWEL_Bullet_SalvagedLaserRifle` ⚠️ *unstable laser shot* (fire 15%) |
| `VWEL_Gun_SalvagedLaserShotgun` | salvaged laser shotgun | **7** `Burn` | 0.56 | 14.9 | 2.2 | 0.6 | 4 | 3.0 | 2050 | Ultra | `VWE_LaserWeapons` † | `VWEL_Bullet_SalvagedLaserShotgun` ⚠️ *unstable laser scatter shot* |
| `VWEL_Gun_SalvagedLaserSniperRifle` | salvaged laser sniper rifle | **39** `Burn` | **1.00** | 39.9 | 4.6 | 2.2 | 1 | 3.8 | 2200 | Ultra | `VWE_LaserWeapons` † | `VWEL_Bullet_SalvagedLaserSniperRifle` ⚠️ *unstable precise laser shot* |

† The `researchPrerequisite` sits on the abstract parent `BaseLaserGun`
(line 41) inside a `recipeMaker` whose `<recipeUsers/>` is **empty**. So these
are not directly craftable at any bench. The only route is the recipe
`Salvage_LaserWeapon` (FabricationBench, Intellectual 10, 6 spacer components +
30 plasteel, 10000 work) which yields `LaserRandom` — a dummy carrying
`VEF.Things.CompProperties_RandomOutcomeComp` with
`canProvideTags: SalvagedLaserGun`, i.e. **a random one of these four.**

**Research:** `VWE_LaserWeapons`, label *"salvaged laser weapons"*, baseCost
**6000**, tab `VanillaExpanded`, techLevel **Spacer**, prerequisite
**`ChargedShot`**, requires **HiTechResearchBench + MultiAnalyzer**.

---

## TIER 2 — ULTRATECH / FULL (8 weapons)

Common: `techLevel` Ultra, `weaponTags` `SpacerGun` + `LaserGun` (tesla gun:
`LaserGun` only), `generateCommonality` 0.1, `tradeTags` `SpacerGun`,
`thingSetMakerTags` `RewardStandardLowFreq` + `RewardStandardQualitySuper`.

| defName | label | dmg | AP | range | warmup | cooldown | burst | mass | value | tech | research | projectile |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `VWEL_Gun_LaserPistol` | laser pistol | 13 `Bullet` | 0.66 | 23.9 | 2.0 | 1.0 | 2 | 1.2 | 2000 | Ultra | **none** ‡ | `VWEL_Bullet_LaserPistol` |
| `VWEL_Gun_LaserSMG` | laser SMG | 13 `Bullet` | 0.66 | 23.9 | 2.0 | 1.9 | 3 | 1.8 | 2400 | Ultra | **none** ‡ | `VWEL_Bullet_LaserPistol` ← **shared with the pistol** |
| `VWEL_Gun_LaserRifle` | laser rifle | 12 `Bullet` | 0.60 | 32.9 | 2.0 | 0.6 | 2 | 2.6 | 3000 | Ultra | **none** ‡ | `VWEL_Bullet_LaserRifle` (fire 10%) |
| `VWEL_Gun_LaserShotgun` | laser shotgun | 11 `Bullet` | 0.56 | 14.9 | 2.2 | 0.6 | 4 | 3.0 | 3200 | Ultra | **none** ‡ | `VWEL_Bullet_LaserShotgun` |
| `VWEL_Gun_LaserSniperRifle` | laser sniper rifle | **48** `Bullet` | **1.00** | **44.9** | 4.6 | 2.2 | 1 | 3.8 | 3600 | Ultra | **none** ‡ | `VWEL_Bullet_LaserSniperRifle` (fire 20%) |
| `VWEL_Gun_LaserMinigun` | laser minigun | 10 `Bullet` | 0.32 | 29.9 | 4.0 | 0.2 | **8** | **12.0** | **4500** | Ultra | **none** ‡ | `VWEL_Bullet_LaserMinigun` |
| `VWEL_Gun_TeslaGun` | tesla gun | 15 **`EMP`** | 0.45 | 18.9 | 2.4 | 1.0 | 1 | 8.0 | 3000 | Ultra | **none** ‡ | `VWEL_Bullet_TeslaGun` |
| `VWEL_LaserSword` *(melee)* | laser sword | cut **31** (×2 tools), blunt 9 | **1.00** | melee | — | 2.6 s/swing | — | 1.4 | 2000 | Ultra | **none** ‡ | — |

Drawbacks worth noting: sniper `MoveSpeed −0.15`; minigun and tesla gun
`MoveSpeed −0.25`. All ranged lasers carry
`VEF.Weapons.CompProperties_LaserCapacitor` — warmup shrinks per consecutive
shot while stationary, with an overheat chance (5–10%) that detonates a small
`Burn`/`Flame` blast on the user. The minigun and tesla gun blast `Flame`.

---

## 🔴 ‡ THE FINDING THAT CHANGES THE DESIGN DOC

**There is no second research project. There is no "ultratech laser weapons"
research, and the full tier is not craftable at all.**

```
$ grep -rn "ResearchProjectDef>" 1.2 1.3 1.4 1.5 1.6
  1.2/… (2 projects)   1.3/… (2 projects)   1.4/… (1)   1.5/… (1)   1.6/… (1)
```

The mod had two research projects in **1.2 and 1.3**; from **1.4 onward it has
one**, `VWE_LaserWeapons` ("salvaged laser weapons"). In 1.6:

- `VWE_BaseLaserGunUltra` has **no `recipeMaker` node at all** — the full tier
  cannot be built at any bench, at any research level, ever.
- Only `BaseLaserGun` (the salvaged parent) carries a `recipeMaker`, and its
  `recipeUsers` is empty.
- The full tier's only sources are `thingSetMakerTags` (quest/reward drops),
  `tradeTags: SpacerGun` (traders), and raider corpses.

⚠️ **`ship_legacy_armoury.md` line 24–25 is wrong on this point.** It records a
`ultratech laser weapons` research and a "Full" tier the clan can eventually
build. **On disk under 1.6 that progression does not exist.** The doc's central
beat — *"the moment the ship stops being scrap the clan lives in"* — has **no
mechanical hook in v1 as shipped**: the player researches the salvaged tier,
then waits for a trader.

**So do Y:** if the beat is to survive v1, it needs one small patch we author —
a second `ResearchProjectDef` plus a `recipeMaker` added to the seven full-tier
guns. That is ~40 lines of `PatchOperationAdd`, not a new mod. If v1 cannot
afford it, **amend the doc to say the full tier is loot-only** rather than
shipping a plan the defs do not support.

---

## 🔴 THE COHERENCE RULE IS BACKWARDS IN THE DOC

`ship_legacy_armoury.md` §"The coherence rule" says the *salvaged* tier may
circulate and the full tier is ours alone, and assumes the mod's own split does
that for us. **The defs do the opposite.**

`1.6\Defs\PawnKindDefs\PawnKinds_Pirate.xml` defines `Mercenary_Marine`
(combatPower 300, `defaultFactionType` Pirate) with:

```xml
<weaponTags Inherit="False">
    <li>LaserGun</li>
</weaponTags>
<weaponMoney>2500~4400</weaponMoney>
```

`LaserGun` is the **full-tier** tag. `SalvagedLaserGun` appears in **no**
PawnKindDef at all. And `1.6\Patches\FactionDef_Misc.xml` adds that pawn kind to
the **Pirate** faction's `pawnGroupMakers` at commonality 10, 5 marines a group.

**Result left alone: pirates field the ship's exclusive armoury — pistol, SMG,
rifle, shotgun, sniper, tesla gun and the laser sword all fall inside
2500–4400 (only the 4500 minigun is priced out) — while the salvaged tier, the
one the fiction says should be everywhere, spawns on nobody.**

**So do Y:** one `PatchOperationReplace` on
`PawnKindDef[defName="Mercenary_Marine"]/weaponTags` swapping `LaserGun` for
`SalvagedLaserGun`, and drop `weaponMoney` to ~1400~2300 to cover 1500–2200.
That single op delivers the doc's rule exactly, and is cheaper than the v2
rename it was filed under.

---

## Player-zero read

### Is 4 + 8 a sensible armoury?

**Yes in size, no in distinctness.** Twelve is not a wall of guns — the problem
is that several are the *same* gun.

**Functionally identical pairs, named:**

1. 🔴 **`VWEL_Gun_LaserPistol` and `VWEL_Gun_LaserSMG` — the same weapon.** They
   share **the same projectile def** (`VWEL_Bullet_LaserPistol`), the same range
   (23.9), the same warmup (2.0), the same `AccuracyTouch` (0.80), the same
   `ticksBetweenBurstShots` (10). They differ by burst 2 vs 3 and cooldown 1.0 vs
   1.9 — which almost exactly cancel (2 dmg-events/s vs 1.6). The player cannot
   tell them apart in play; the SMG is a pistol that weighs 0.6 more and costs
   400 more silver.
2. **`…_SalvagedLaserShotgun` vs `…_LaserShotgun`** — identical range 14.9,
   burst 4, warmup 2.2, cooldown 0.6, mass 3.0. Only the damage differs (7 vs 11).
3. **`…_SalvagedLaserSniperRifle` vs `…_LaserSniperRifle`** — identical warmup
   4.6, cooldown 2.2, mass 3.8, AP 1.00, move penalty −0.15. Damage 39 vs 48,
   range 39.9 vs 44.9.
4. **`…_SalvagedLaserPistol` vs `…_LaserPistol`** — damage 12 vs 13, AP 0.60 vs
   0.66, range 19.9 vs 23.9. Everything else matches.

That is deliberate — cross-tier pairs are *supposed* to be the same silhouette
worse — but it means **the salvaged tier is not four weapons, it is four
downgrade-skins of the full tier**, and the pistol/SMG pair is a genuine
duplicate inside one tier.

⚠️ **The tier gap is far smaller than the fiction implies.** Salvaged rifle does
**13 damage; the ultratech rifle does 12.** The salvaged rifle hits *harder per
shot* than the ship-grade article. The full rifle wins only on burst count (2 vs
1) and accuracy. Across the whole set the tier gap is ~10–20% on damage and
~5 cells on range. **The player will not feel the emotional beat the doc is
built on, because the numbers do not deliver one.** If that beat matters, the
salvaged tier should be pushed *down* (or the full tier up) far more than the
mod does.

**Genuinely distinct weapons: the sniper (48/AP 1.00/44.9 — a different job),
the minigun (8-shot burst, 12 kg, 0.2 s cooldown), the tesla gun (EMP), and the
laser sword (melee).** Four real designs; the rest is one gun at five sizes.

**Strongest in each tier:** salvaged — `VWEL_Gun_SalvagedLaserSniperRifle`
(39 dmg, AP 1.00, 39.9 range). Full — `VWEL_Gun_LaserSniperRifle` (48 dmg,
AP 1.00, 44.9 range); the minigun is the highest-value item at 4500 but its
AP 0.32 makes it the weakest per shot in the mod.

### Does anything outclass what the Jawa clan should have at v1?

**Not on the way in.** The salvaged tier is gated behind 6000-point research
with a `ChargedShot` prerequisite and a MultiAnalyzer — that is deep-midgame at
the earliest, and it produces one random gun per 10000-work recipe. A salvager
clan grinding spacer components into a lottery ticket is *exactly* the fiction.

**The fiction problem is the full tier, and it is not that we can build it — it
is that we cannot.** It arrives only as loot, so the clan's "inherited armoury"
will in practice be handed to them by a passing trader for silver. **An
ultratech laser sniper bought off a caravan is a worse fiction than one the clan
never gets at all.** Two clean options: (a) author the missing research +
recipes so the tier is *earned* (my recommendation, ~40 lines), or (b) strip
`<tradeability>All</tradeability>` / `SpacerGun` from the full tier so it can
only be found, never bought.

Second, smaller fiction problem: **AP 1.00 on both sniper rifles**, salvaged
included. A weapon the Jawas cobbled together from a half-understood schematic
ignores all armour perfectly. Consider clipping the salvaged sniper to ~0.7.

### Collisions with `Jawa_Armoury`

**Name collisions: zero.** `grep -rn "VWEL" src\Jawa\Jawa_Armoury\Patches\`
returns nothing (the "Laser" hits are all `OuterRim_Proj_*LaserCannon`). Every
operation is wrapped in `PatchOperationFindMod` naming Core, Outer Rim ×2, KotOR,
JDS StarWars Armory, Yautja and three turret mods — **VWE-Laser is not in any
guard list, so not one op touches it.**

🔴 **Band collision: severe, and live.** `Jawa_Armoury\README.md` says "built,
validated, **NOT YET ENABLED**" — but `mandrake.jawa.armoury` **is** in
`<activeMods>` (line 571 of `ModsConfig.xml`). Its README is stale; the retune is
in the stack. Post-retune bands versus the untouched lasers:

| family | Jawa_Armoury band | VWE-Laser, unpatched |
|---|---|---|
| standard blaster | **24–34** | laser rifle **12**, pistol/SMG **13** |
| slugthrower | **18–36** | laser shotgun **11**, minigun **10** |
| vibro | **35–52** | — |
| lightsaber | **99** (all 15, flat) | laser sword cut **31** |
| turbolaser | 800–2000 | laser sniper **48** |
| ion / EMP / stun | 8, deliberately untouched | tesla gun **15** EMP |

**The ship's ultratech legacy armoury is now the weakest ranged family in the
stack.** A `VWEL_Gun_LaserRifle` at 12 damage sits *below* the retuned median
blaster at 25 and barely above a human fist at 8.2 — the exact defect
`Jawa_Armoury` was written to fix, reintroduced by a mod enabled after it. The
"ultratech" tier the doc calls the emotional payoff is, in the live stack,
strictly worse than a stormtrooper's sidearm.

**So do Y:** add a fifth generated block to `Armoury_RangedDamage.xml` —
`PatchOperationFindMod` on `Vanilla Weapons Expanded - Laser` — placing the full
tier at the top of the personal band (~34–48) and the salvaged tier at the
bottom (~18–24). That both fixes the collision **and** creates the tier gap
section "Player-zero read" says the mod fails to deliver. Regenerate via
`src\Jawa\Jawa_Armoury\Source\gen_armoury_patch.py`; do not hand-edit the XML.

**Resolves the doc's `laser sword` loose thread, in the safe direction.** Post-
retune every lightsaber is 99 cut power; `VWEL_LaserSword` is **31**, under a
third. A common laser sword does **not** cheapen a lightsaber at these numbers —
they are different weapon classes, not the same weapon at two prices. The doc's
"decide when the Force spec is decided" caution can be downgraded: the stat gap
already does the work, provided any future VWEL retune keeps the sword well
under 99.

**One more overlap, minor:** `JawaIon_Blaster`
(`src\Jawa\JawaIonWeapons\Defs\ThingDefs_JawaIonBlaster.xml`) is Industrial, 8
damage `JawaIon_Damage`, range 22, value 420 — non-lethal capture tool. The
**tesla gun** (15 EMP, AP 0.45, range 18.9) occupies the same anti-mech role at
roughly double the punch. No def collision, but once the tesla gun is in reach
the ion blaster's mechanoid niche is gone; its capture/stun-buildup mechanic is
the only thing keeping it distinct. Worth stating deliberately rather than
finding out in a fight.

---

## Everything else the mod ships (for completeness)

- `1.6\Patches\Ideology.xml` — `PatchOperationFindMod` on Ideology, adds
  `weaponClasses` (`Ultratech`, `RangedLight`, `RangedHeavy`, `ShortShots`,
  `LongShots`) to nine of the twelve weapons. **`VWEL_Gun_LaserSMG`,
  `VWEL_Gun_LaserRifle` and `VWEL_Gun_SalvagedLaserRifle` get no weaponClasses**
  — upstream omission, harmless, but it means those three satisfy no Ideology
  weapon precept.
- `1.6\Defs\Motes\VWEL_Abstracts_Laser.xml` — `VWELBeamGraphic` and the abstract
  `VWEL_Bullet_LaserGeneric` (`VEF.Weapons.LaserBeam`, speed 10000).
- `1.6\Defs\ThingDefs_Misc\Items_Unfinished.xml` — `UnfinishedSalvagedLaserGun`.
- Hard dependencies per `About.xml`: `brrainz.harmony` and
  `OskarPotocki.VanillaFactionsExpanded.Core` (VEF). Every weapon's `thingClass`
  is `VEF.Weapons.LaserGun` — **without VEF loaded and loaded first, all twelve
  weapons are dead defs.**
