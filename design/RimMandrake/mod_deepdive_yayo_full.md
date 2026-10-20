# Yayo's Combat 3 — the full engine analysis

Owner order, typed 2026-10-10: *"We need a DEEP analysis of what Yayo does spelled out beyond its renormalization.
animations. differing scaling logic / algorithms. Everything. Not to be done lightly. I very much doubt it's just
some normalization."* Offline: no bridge, no game, no mod list changed. Supersedes the depth of
`design/RimMandrake/mod_deepdive_yayo.md` (§11 lists what that one missed). Card: `design/RimMandrake/mod_audit/OWNER_CARDS.md` C14.

Evidence tags: **MEASURED** = read from Yayo's decompiled DLL or its byte-identical source, RimSage's decompiled
1.6, decompiled third-party DLLs, the 2026-10-04 def dump, the mod's XML, or a Player.log; **COMPUTED** = arithmetic
on measured inputs by `design/RimMandrake/mod_deepdive_yayo_full_sim.py`; **INFERRED** = reasoning, said so;
**UNVERIFIED** = not checked.

## 0. Answer

**You were right: the "normalisation" is the smallest part.** Yayo's Combat 3 is three XML lines of balance and a
C# **replacement of RimWorld's shot and injury code**. Everything it does in our game, in one list:

1. **Replaces the injury pipeline** (`DamageWorker_AddInjury.ApplyDamageToPart`) with its own copy and its own
   armour formula: armour that blocks up to 90% of hits outright **while it is in good repair** and loses protection
   as it loses hit points; wear scales with the attacker's AP (0.20-0.70 HP per point, vanilla 0.25).
2. **Turns item quality into a cliff**: in the live game (with Stronger Quality Scaling) a masterwork flak jacket lets
   4% of assault-rifle damage through; clean vanilla lets 53% through.
3. **A one-sided tech rule**: Medieval-or-lower weapons and **every animal bite, fist and mech blade** lose 25-65% of
   their AP against worn apparel; nothing equivalent protects mechs or animals.
4. **Natural armour uses the same model scaled by the pawn's health**: healthy thrumbos and mechs are much tougher,
   wounded ones softer. Plus **mechanoids +30% sharp armour and +30% raid cost** (faction-blind: the player's own
   animals and Biotech mechs get both too).
5. **Changes where blows land**: its injury copy skips every damage type's own hit-part rule, so a melee
   stab (knife, spear, sword point, scyther blade, horn) never gets vanilla's 60% chance to go through to an organ,
   and blunt/cut lose their outside-parts-only rule for non-melee hits.
6. **Replaces shot resolution** (`Verb_LaunchProjectile.TryCastShot`) and **counts Shooting skill twice** in hit
   chance (a level-15 shooter at 25 tiles: 0.64 → 0.78 shooter factor); turrets keep vanilla accuracy but take the
   replaced method.
7. **Bullets ×3 speed** (cap 2 tiles/tick), fused grenades (frag, EMP) and fast thrown weapons too.
8. **Equipped melee weapons swing 43% faster** with no damage cut (the compensation is dead code), with a random
   cooldown every swing.
9. **Gloves/boots coverage**: arm armour covers hands, leg armour covers feet; gloves and boots move to parallel layers.
10. **A player-craftable anti-armour rocket launcher**; ammunition (off in our game).
11. **What it breaks, measured:** vanilla's gun **recoil animation** never plays; mortar crew skill ignored; the
    rocketswarm's even spread lost; `canGoWild false` weapons go wild; turrets lose cover; blasters/arrows never
    headshot; deflect/impact effects inverted; info-card melee DPS is random; **and other mods' code on the same
    methods stops running**: Vanilla Traits Expanded's Drunken Master, VRE Archon's armour strip, part of GiddyUp's
    mount armour, JecsTools partial damage soak, VEF held-shield armour (§8.4). (Vanilla Gravship Expanded saw this
    coming and ships a patch that exempts its gravship guns from Yayo's shot code.)
12. **No animations, no art beyond 11 icons, no sounds**: the animation system left the mod in 1.5.

**Our own design disagrees with it**: the Armoury armour retune is built on the vanilla formula and its three rules
(2.0 = immunity, AP 0 lightsabers, the 5-shot contract) are false under Yayo's; and lightsabers currently run two
different armour engines depending on which def they are.

**Recommendation: remove it and port the ideas** (hand/foot coverage and skill-weighted accuracy now, as XML/small
code; armour wear as a designed `StatPart`, against the Armoury contract), and rule on Stronger Quality Scaling at
the same time (§10). If the owner wants to keep feeling Yayo's armour first, pin its engine off (option B, S) to stop
the collateral damage today.

## 1. Identity, source, licence, what was decompiled

| | |
|---|---|
| mod | Yayo's Combat 3 (Continued), packageId `Mlie.YayosCombat3`, author YAYO, maintainer Mlie |
| on disk | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2854006492`, the only copy; nothing under `…\common\RimWorld\Mods` (MEASURED). 117 files. Its 1.6 load folders are `/`, `1.6`, `Assets` (LoadFolders.xml) |
| code | `1.6\Assemblies\yayoCombat.dll` (80,896 bytes) + `VersionFromManifest.dll` (Mlie's version-label helper, no patches) |
| source | `https://github.com/emipa606/YayosCombat3`, HEAD `4f436d1`, cloned to `/home/mandrake/.seat-tmp/yayo_dd/src`. The repo's `1.6/Assemblies/yayoCombat.dll` is **byte-identical** to the installed DLL (`cmp`, MEASURED) |
| decompile | The installed DLL was also decompiled with ILSpy (`ilspycmd` 8.2) to `D:\ClaudeWork\rimmandrake\scratch\yayo_full\decomp` and its 33 `[HarmonyPatch]` classes, priorities and bodies were checked against the source: same targets, same priorities, same guards (MEASURED). Every statement about behaviour below is from that code. Vanilla bodies are RimSage's decompiled 1.6 |
| licence | `LICENSE.md` in the mod folder and the repo root: **MIT, "Copyright (c) 2020 Mlie"**, the standard MIT text, with no per-folder carve-out, so it covers the whole repository: C#, XML and textures (MEASURED: one licence file, no other licence text in the tree). The copyright line names the maintainer, not YAYO; YAYO's original Workshop page is the only statement from the original author, and it is outside the repo (INFERRED risk: low, MIT is the published grant). Porting code or XML is allowed if the notice is kept |
| hard deps | Harmony only for 1.6 (HugsLib dropped in 1.6.3, `UpdateInfo.xml`); old HugsLib settings are imported once and **deleted from HugsLib's file** on load (`ImportOldHugsLibSettings`) |
| assets | One AssetBundle `Assets\AssetBundles\Mlie_YayosCombat3` holding exactly **11 textures**: the rocket launcher, the news banner and 9 ammo icons (manifest, MEASURED). **No sounds, no shaders, no animation clips.** `LegacyAssets\Textures` holds the same PNGs for ≤1.5 |
| languages | Keyed + DefInjected for English, Chinese, French, German, Korean, Russian. The English keys still describe two settings that no longer exist (`advAni` "combat animations", `ani_twirl` "twirl the weapon") and one that does nothing (`unprotectDmg`) |

**Load evidence from our full list** (`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player-prev.log`,
2026-10-10, 1,639 static constructors): `yayoCombat.YayoCombatCore` constructed; `[YayoCombat] Applying Def patches.`;
`[YayoCombat] Removing ammo recipes. Found 18 ammo recipes.`; its Postfix listed on `PawnGenerator.GenerateGearFor`
(MEASURED). The **current** `ModsConfig.xml` is an 11-mod test list without Yayo's; the full list
(`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`) has it active.

## 2. Every Harmony patch (33 classes, one `PatchAll`)

Harmony id `Mlie.YayosCombat3`, applied in the `Mod` constructor (before defs load). Priority is Harmony's default 400
unless named. "Gate" is the setting that must be on for the patch body to do anything; the Harmony call wrapper runs
regardless. **"Replaces" means a prefix that returns `false`: the vanilla body and every other mod's transpiler on
that method never run** while the gate is on; every other mod's postfix still runs, and a later-registered prefix
still runs only if it cannot affect the original (no bool return, no `ref`/`out` or reference-type argument besides
`__instance`/`__state`); otherwise it is skipped (Harmony 2.4.1, MEASURED from the decompiled `0Harmony.dll`, §8.4).

### 2.1 The combat engine: 7 patches that are live in our game

| # | target | kind | gate (live value) | what it does, against vanilla |
|---|---|---|---|---|
| P1 | `Verse.DamageWorker_AddInjury.ApplyDamageToPart(DamageInfo, Pawn, DamageResult)` | prefix, **replaces** | `advArmor` (**on**) | Re-implements the whole method: hit-part choice, armour, incoming-damage factor, headshot, permanent-injury check, then either its own copy of `FinalizeAndAddInjury` or vanilla's `ApplySpecialEffectsToPart` via reflection. Armour goes through Yayo's own `yayoCombat.ArmorUtility` (§3.1). Every injury to every pawn, from every source with an armour category, runs here. Line-by-line differences in §3.1 and §3.8 |
| P2 | `Verse.Verb_LaunchProjectile.TryCastShot()` | prefix, **replaces** | `advShootAcc` (**on**); pawns always (mechs too, `mechAcc` on; all factions, `colonistAcc` off); turrets via `turretAcc` (**on**) | Re-implements the shot: forced-miss, wild-miss, cover, hit. Differences in §3.3. `Verb_Shoot` and every modded subclass reach it through `base.TryCastShot()`; only overrides that never call base escape |
| P3 | `Verse.ShotReport.HitFactorFromShooter(Thing, float, float?)` | postfix | `advShootAcc` (**on**); pawns only | Throws away vanilla's result and recomputes it with a skill-blended accuracy (§3.2) |
| P4 | `Verse.Projectile.StartingTicksToImpact` (getter) | prefix, **replaces** | none: `bulletSpeed` 3 is applied whenever the projectile qualifies | Flight time ÷3, capped at 2 tiles/tick (§3.4) |
| P5 | `Verse.Tool.AdjustedCooldown(Thing)` | postfix, priority 0 (last) | `meleeDelay` ≠ 1 or `meleeRandom` > 0 (**0.7 / 1.3**) | Melee-weapon cooldown ×0.7 × a fresh random factor each call (§3.5) |
| P6 | `Verse.Thing.TakeDamage(DamageInfo)` | prefix | runs only when `meleeDelay == 1` exactly | Rounds melee-weapon damage to a whole number (the "compensation" for P5, which never fires at 0.7; §3.5) |
| P7 | `Verse.Root_Play.Start()` | prefix | once per session (`patchApplied`) | Runs `ApplyDefPatches`: hand/foot coverage and the `_A` layers (`handProtect`), mech armour and combat-power ×1.3 (`advArmor`), ammo comps or ammo-recipe removal (`ammo`), and clears the rocket's weaponTags (`enemyRocket` off). Def edits, so they last until the game is closed even if a setting is changed (§6.2) |

### 2.2 Ammunition and logistics: 26 patches, all inert in our game

Every one of these early-outs on `ammo == false` (MEASURED: the guard is the first statement), except the four
marked ★, which do something with ammo off but touch nothing in our list (reasons given).

| target | kind, priority | role when `ammo` is on |
|---|---|---|
| `Building_TurretGun.MakeGun` | prefix | gives turret guns their reloadable comp state |
| ★ `CompApparelReloadable.CompTick` | prefix | if `replenishInTicks == -1` on a self-replenishing item with no ammo def, starts the cooldown instead of instantly refilling. **Ungated.** Vanilla 1.6 defines no `replenishAfterCooldown` item (RimSage, MEASURED); our list UNMEASURED but no hit in the static census of §8.4 |
| `CompApparelReloadable.PostExposeData` | prefix, **replaces** when ammo on | saves charges for weapon-borne reloadables |
| `CompApparelVerbOwner_Charged.PostPostMake` | postfix, 0 | new weapons start with `enemyAmmo`% charges |
| `CompApparelVerbOwner.CreateVerbTargetCommand` | prefix | ammo gizmo on weapons |
| ★ `CompApparelVerbOwner.Wearer` (getter) | postfix | **ungated**: if a reloadable comp has no wearer but sits in an equipment tracker, returns the wielder. No vanilla weapon carries a `CompApparelVerbOwner` (they are apparel comps), so a no-op without ammo (INFERRED) |
| `Dialog_ManageDrugPolicies.DoEntryRow` | prefix, replaces | ammo rows in the drug-policy dialog (ammo is carried "as a drug") |
| `DrugPolicy.ExposeData` | prefix, 1000 | saves ammo entries |
| `DrugPolicy.InitializeIfNeeded` | prefix, 0 | adds ammo to every drug policy |
| `JobDriver_Hunt.MakeNewToils` | postfix (toil enumerator) | hunters stop when out of ammo |
| `JobDriver_Reload.MakeNewToils` | postfix | reload job for weapons |
| `JobGiver_MoveDrugsToInventory.FindDrugFor` | prefix | fetch ammo to inventory |
| `PawnGenerator.GenerateGearFor` | postfix, 0 (last) | NPCs spawn with ammo. **Listed in our Player.log** alongside Simple Sidearms, Melee Animation, JecsTools shields and HAR |
| `Pawn_DrugPolicyTracker.AllowedToTakeToInventory` | prefix | ammo counts |
| `Pawn_EquipmentTracker.DropAllEquipment` | prefix | dead NPCs drop their ammo |
| `Pawn.Tick` | postfix, 0 | drafted auto-reload every 60 ticks. **Per pawn per tick**, body is one bool test with ammo off |
| ★ `RecipeDef.AvailableNow` (getter) | postfix | **ungated in effect**: with ammo off it forces `false` for any recipe whose defName contains `yy_ammo` (belt-and-braces with the recipe-user clearing in P7). Runs on every recipe availability check (bills UI, work givers) |
| `ReloadableUtility.FindSomeReloadableComponent` | postfix | weapons count as reloadable |
| `ReloadableUtility.OwnerOf` | postfix | |
| ★ `StatPart_ReloadMarketValue.TransformAndExplain` | prefix | **ungated**: for a ranged weapon carrying `CompApparelReloadable`, prices the loaded ammo instead of vanilla. Only Yayo's ammo comp puts that comp on weapons, so a no-op with ammo off (INFERRED) |
| `ThingFilter.SetFromPreset` | prefix | stockpile presets include ammo |
| `ThingSetMaker_TraderStock.Generate` | **transpiler** | always installed: strips every `ret` and appends a call to `addAmmo(...)` that returns at once with ammo off. The only transpiler in the mod |
| `ThingWithComps.GetFloatMenuOptions` | postfix, 0 | "eject ammo" menu |
| `Pawn_EquipmentTracker.GetGizmos` | postfix (gizmo enumerator) | reload gizmo. **Wraps the gizmo enumerator for every selected pawn even with ammo off** (re-yields the list) |
| `TraderKindDef.WillTrade` | prefix | traders stock ammo |
| `WorkGiver_HunterHunt.HasHuntingWeapon` | postfix | hunting needs ammo |

**What was never in the 1.6 code:** no patch on any renderer, `PawnRenderer`, `DrawEquipmentAiming`, `Pawn_DrawTracker`,
stance drawing, motes or sounds (MEASURED: full patch list above, decompiled). The animation system was removed in
1.5 (the mod's own news entry `YayosCombat3_1_4_3`: *"From 1.5 onwards the advanced animations has been removed from
the mod. The Yayo's Animation-mod can be used for this instead"*), and the 1.5 DLL in the repo has no render patch
either (decompiled, MEASURED). Leftovers in 1.6: a static constructor that detects Dual Wield, Melee Animation,
Show Me Your Hands and HAR by packageId and caches oversized-weapon draw offsets by reflection over every weapon
def; **nothing reads any of it** (`GetOversizedOffset` and `weaponLocations` have no caller, MEASURED). Yayo's
Animation (a separate mod) is not in our list.

## 3. Formulas, with vanilla beside them and worked numbers

All worked numbers come from `design/RimMandrake/mod_deepdive_yayo_full_sim.py` (stdlib, exact expectations, one
seeded run for wear; COMPUTED from the transcribed code). Vanilla ratings are RimSage 1.6 Core.

### 3.1 Armour: `yayoCombat.ArmorUtility` against `Verse.ArmorUtility` (MEASURED, both read in full)

The layer loop is the same in both: worn apparel from outermost (`WornApparel[Count-1]`) inward, only apparel that
covers the hit part, then the pawn's own (natural) armour stat; stop when damage < 0.001. What differs is the
per-layer roll.

```
VANILLA ApplyArmor(dmg, AP, R, apparel):
  if apparel: apparel.TakeDamage(RoundRandom(dmg * 0.25))           # wear, before the roll
  eff = max(R - AP, 0)                                              # R capped at 2 by the stat
  u = Rand.Value
  if   u < eff/2 : dmg = 0                                          # deflect
  elif u < eff   : dmg = RoundRandom(dmg/2); Sharp -> Blunt         # diminish
  else           : unchanged

YAYO applyArmor(dmg, AP, R, apparel, weapon, pawn):
  AP' = AP * techMult(weapon, apparel)                              # apparel only; see table below
  left  = max(R - AP', 0)
  admg  = clamp01((AP' - 0.15*R) * 5)                               # "how much this attack chews armour"
  if apparel: apparel.TakeDamage(RoundRandom(dmg * (0.2 + 0.5*admg)))   # wear, before the roll
  hp    = apparel ? apparel.HitPoints/MaxHitPoints : pawn.SummaryHealthPercent
  defence = max(0.9*R - AP', 0)
  u = Rand.Value
  if u * (1 - armorEf) < defence * hp:                              # armorEf 0.5 -> u < 2*defence*hp
      if Rand.Value < min(left, 0.9): dmg = 0                       # full block, never above 90%
      else: dmg = RoundRandom(dmg * (0.25 + 0.25*admg)) [apparel]   # strong reduction, Sharp -> Blunt
            dmg = RoundRandom(dmg * (0.25 + 0.50*admg)) [natural]
  elif u < left * (0.5 + 0.5*hp): dmg = RoundRandom(dmg/2); Sharp -> Blunt
  else: unchanged
```

The tech multiplier (applied only when the layer is worn apparel and `dinfo.Weapon` is not null):

| armour layer | attacker's `dinfo.Weapon` | multiplier on AP |
|---|---|---|
| Spacer or higher apparel, **or any apparel worn by a mechanoid** | a melee weapon of Medieval or lower | ×0.5 |
| same | anything else of Medieval or lower: bows, pila, slings, **every unarmed and natural attack** (the weapon is then the race def, which `IsMeleeWeapon` false and techLevel Undefined; `Verb_MeleeAttackDamage` passes `CasterPawn.def`, RimSage) | ×0.35 |
| Industrial apparel | a melee weapon of Neolithic or lower | ×0.75 |
| same | anything else of Medieval or lower, including every unarmed and natural attack | ×0.5 |
| Neolithic/Medieval apparel, or natural armour | anything | ×1 |

What the formula means in play:

1. **Armour is a near-wall while healthy.** With armorEf 0.5, the "defend" branch fires with probability
   `2 × (0.9R − AP) × hp`; for R ≥ ~0.6 against an ordinary rifle that is most hits. A fraction `R − AP` of those
   (41% at R 0.6 against AP 0.19, reaching the 90% cap only from R ≈ 1.1) is fully blocked; the rest take 25-50% as
   Blunt. Vanilla's best case at R = 1 against AP 0.19 is a 40% deflect.
2. **Armour degrades in protection, not just in hit points.** `hp` multiplies the defend chance, so a jacket at
   50% HP protects about as well as vanilla, and below that worse than vanilla (table 3.1-B).
3. **Wear depends on AP.** `0.2 + 0.5×admg` per point of incoming damage: 0.20 (low AP, wears *slower* than
   vanilla's 0.25) up to 0.70 (AP ≥ 0.15R + 0.2, wears 2.8× faster). Wear is charged on every hit, blocked or not.
4. **Natural armour scales with the pawn's own health.** Animals and mechs get the same model with `hp =
   SummaryHealthPercent`: a healthy thrumbo or centipede is far harder to hurt than in vanilla, a wounded one
   easier. Baseline humans have natural armour 0, so the branch is a no-op for them; any pawn with nonzero natural armour (alien species, genes, hediff offsets) gets it.
5. **Full block caps at 90%** (`min(left, 0.9)`), so a rating of 2.0 is never immunity; vanilla 2.0 against AP 0 is
   immunity (eff ≥ 2 → u < 1 always deflects).
6. **The tech rule is one-sided.** It discounts attacks *against worn apparel*. Mech natural armour has no
   multiplier at all. So a scyther blade or a thrumbo horn loses 50-65% of its AP against an armoured colonist,
   but a colonist's knife against a mech loses nothing. Net: the player's armoured crew gains against animals,
   tribals and mechanoid melee. (The natural-armour model and the mech ×1.3 below are faction-blind: they also
   apply to the player's tamed animals and Biotech mechs.)

**3.1-A. Assault rifle (11 dmg) against a flak jacket (0.55 sharp, Industrial) at each quality.** "CLEAN VANILLA" is
what the game would do with Yayo's removed (vanilla engine, vanilla AP 0.165, vanilla quality curve). "LIVE" is what
our game does now (Yayo engine, Yayo's AP 0.19, Stronger Quality Scaling's curve). Expected fraction of the 11
damage reaching the body (points in brackets).

| quality | rating, vanilla curve | rating, SQS | CLEAN VANILLA | LIVE, jacket 100% HP | LIVE, jacket 50% HP | Yayo engine, vanilla curve |
|---|---|---|---|---|---|---|
| awful | 0.33 | 0.11 | 0.88 (9.6) | 1.00 (11.0) | 1.00 (11.0) | 0.86 (9.5) |
| poor | 0.44 | 0.33 | 0.79 (8.7) | 0.86 (9.5) | 0.93 (10.3) | 0.71 (7.8) |
| normal | 0.55 | 0.55 | 0.71 (7.8) | 0.54 (5.9) | 0.77 (8.5) | 0.54 (5.9) |
| good | 0.63 | 0.72 | 0.65 (7.1) | 0.25 (2.7) | 0.62 (6.8) | 0.40 (4.4) |
| excellent | 0.72 | 0.88 | 0.59 (6.5) | 0.10 (1.1) | 0.46 (5.0) | 0.25 (2.7) |
| masterwork | 0.80 | 1.04 | 0.53 (5.8) | **0.04 (0.5)** | 0.28 (3.1) | 0.13 (1.5) |
| legendary | 0.99 | 1.29 | 0.38 (4.2) | **0.02 (0.3)** | 0.05 (0.6) | 0.06 (0.7) |

Read across a row: quality in vanilla moves body damage from 88% to 38% (a factor of 2.3); in the live game it moves
it from 100% to 2% (a factor of 50). **Yayo's engine turns quality into a cliff**, and SQS steepens the cliff.

**3.1-B. The wear arc: one colonist in a normal flak jacket (200 HP) taking assault-rifle hits to the torso**
(4,000 seeded runs; the jacket is the only layer; damage per hit reaching the body, and jacket HP left).

| hits | vanilla dmg/hit | vanilla jacket HP | Yayo dmg/hit | Yayo jacket HP |
|---|---|---|---|---|
| 1-5 | 7.9 | 186 | 6.3 | 174 |
| 6-10 | 7.8 | 172 | 7.0 | 148 |
| 11-20 | 7.8 | 145 | 8.0 | 97 |
| 21-30 | 7.8 | 118 | 9.1 | 45 |
| 31-40 | 7.8 | 90 | 9.9 | 0 (destroyed) |

Cumulative body damage after 10 / 20 / 40 hits: vanilla 78 / 157 / 313, Yayo 66 / 146 / 335. (3.1-A's "100% HP" column ignores the first hit's own wear, which the code applies before reading HP: about 2.6% of a normal jacket, a slight optimistic bias for Yayo.) Against a mid-AP rifle
on a normal jacket the totals are close; the *shape* differs: Yayo front-loads protection and then collapses, and
the jacket is destroyed in ~39 hits instead of ~72. Against high quality armour (3.1-A) the front-loading is so strong
that the armour usually outlives the fight.

### 3.2 Hit chance: the shooter factor (MEASURED: `ShotReport_HitFactorFromShooter` postfix)

```
VANILLA HitFactorFromShooter(caster, d):
  a = ShootingAccuracyPawn (pawn) | ShootingAccuracyTurret (building)
  f = a^d × rangeBandFactor(d)        # ShootingAccuracyFactor_Touch/Short/Medium/Long, 1.0 for normal humans
  return max(f, 0.0201)

YAYO (pawns only; acc not supplied):
  a  = ShootingAccuracyPawn
  s  = Shooting level / 20            (pawns with no skills: baseSkill 5 / 20 = 0.25)
  a' = lerp(a, clamp01(a + s × (1 − a)), accEf 0.6)  =  a + 0.6 × s × (1 − a)
  return VANILLA(caster, d, acc = a')  # a second full call, which re-runs every postfix on the method
```

`ShootingAccuracyPawn` already rises with Shooting skill in vanilla (curve on the stat); Yayo applies skill a
**second time**, so skill counts twice. Worked numbers (shooter factor only; weapon accuracy, cover, target size,
weather, lighting multiply on top identically in both):

| Shooting | per-tile vanilla → Yayo | @12 tiles | @25 tiles | @40 tiles |
|---|---|---|---|---|
| 0 | 0.890 → 0.890 | 0.25 → 0.25 | 0.05 → 0.05 | 0.01 → 0.01 |
| 5 | 0.945 → 0.953 | 0.51 → 0.56 | 0.24 → 0.30 | 0.10 → 0.15 |
| 10 | 0.970 → 0.979 | 0.69 → 0.78 | 0.47 → 0.59 | 0.30 → 0.43 |
| 15 | 0.982 → 0.990 | 0.80 → 0.89 | 0.64 → 0.78 | 0.48 → 0.67 |
| 20 | 0.990 → 0.996 | 0.89 → 0.95 | 0.78 → 0.90 | 0.67 → 0.85 |

Mechanoids and animals (no skills) get `baseSkill` 5: per-tile 0.960 → 0.966 against vanilla's no-skill value.
**Turrets: no change** (the postfix returns for non-pawn casters). The `ShotReport` is also what the hit-chance
**tooltip** and AI target scoring read, so the displayed percentage is Yayo's number (consistent, not a lie).

### 3.3 Shot resolution: `TryCastShot` replaced (MEASURED, line-by-line against RimSage 1.6)

Same order as vanilla: forced miss → wild miss → cover → hit. The numbers inside are vanilla's except:

| step | vanilla 1.6 | Yayo's copy | effect |
|---|---|---|---|
| recoil bookkeeping | `lastShotTick = TicksGame` | **omitted** | `EquipmentUtility.Recoil` keys on `LastShotTick`; every gun's recoil kick **never plays** (`ThingDef.recoilPower` defaults to 1, RimSage `ThingDef.cs:365`; our dump has 540 ranged weapons, per-def overrides not checked) for pawns or turrets on this path (§4) |
| forced-miss radius | × `GetForceMissFactorFor` = the manning pawn's `MortarMissRadiusFactor` for mortars | omitted | mortar crew skill (Shooting → miss radius) **ignored** |
| forced-miss target | `GetForcedMissTarget`: even dispersal if `forcedMissEvenDispersal`, else a random radial cell; falls through only if it equals the target cell | a random radial index `Rand.Range(0, max)`; index 0 (the target cell) falls through to a normal aimed shot, as vanilla's does | the rocketswarm launcher (`Gun_RocketswarmLauncher`, the only even-dispersal def in our dump) loses its even spread |
| wild miss | only if `verbProps.canGoWild`; chance `1 − AimOnTargetChance_IgnoringPosture` | always; aim chance clamped to **[0.0201, 0.99]** | 7 defs in our dump set `canGoWild false` (hellsphere cannon ×2, pack turret, disruptor flare, deadlife, hunter packs, archo drone): they now go wild; every shot keeps ≥1% wild-miss even at point blank |
| wild-miss path | `ChangeDestToMissWild(aim, projectile.flyOverhead, map)` | `flyOverhead` hard-coded `false` | only matters for overhead projectiles that reach the wild branch (rare) |
| cover | `Thing.def.CanBenefitFromCover` (pawns **and turrets**) | `category == Pawn` | **turrets lose cover** as targets |
| debug text | `ThrowDebugText` | omitted | none |
| miss-hits-bystander | `Rand.Chance(0.5)` | `Rand.Chance(missBulletHit 0.5)` | same |

No burst, warmup, cooldown or recoil-stat change: Yayo touches none of `VerbProperties`' timings. "Aiming time" is
vanilla.

### 3.4 Projectile flight (MEASURED: `Projectile_StartingTicksToImpact`)

```
VANILLA ticks = distance / (speed/100)
YAYO    if flyOverhead or (speed <= 23 and explosionDelay <= 0): vanilla
        else ticks = distance / min(speed/100 × 3, 2.0)
```

| projectile | speed | tiles/tick vanilla → Yayo | 25 tiles, ticks |
|---|---|---|---|
| assault rifle bullet | 70 | 0.70 → 2.00 (cap) | 36 → 13 |
| pila (thrown) | 26 | 0.26 → 0.78 | 97 → 33 |
| frag / EMP grenade (`explosionDelay` 100) | 12 | 0.12 → 0.36 | 209 → 70 |
| molotov (speed 12, no fuse) | 12 | unchanged | |
| mortar shell | overhead | unchanged | |
| slow non-explosive (≤23, e.g. many thrown rocks/spits) | ≤23 | unchanged | |

Hit or miss is decided at launch (3.3), so flight speed does not change the hit roll. It changes: time for an
intercepting shield or a pawn stepping into the line (the intercept checks run per tick along the segment); how
soon a grenade lands and starts its fuse; and how visible the bullet is. The getter is called every tick **and
every frame** per live projectile (`DistanceCoveredFraction` → `ExactPosition` → `DrawPos`).

### 3.5 Melee (MEASURED: `Tool_AdjustedCooldown`, `Thing_TakeDamage`)

```
VANILLA cooldown(tool, equipment) = tool.cooldownTime × MeleeWeapon_CooldownMultiplier(quality, stuff)
YAYO    if equipment is a melee weapon (not a gun's butt, not a fist, not a bite):
          cooldown × max(0.01, 0.7 × (1 + (Rand.Value − 0.5) × 1.3)),  floored at 0.2 s
```

The factor is uniform on [0.245, 1.155], mean 0.70, drawn **each time the method is called**: per attack, and
also per stat-card readout, per verb-selection evaluation, per AI DPS estimate. Sustained attack rate = 1/E[cooldown]
→ **+43%** swings with the same damage per swing. The "compensating" damage cut (`Thing_TakeDamage`) runs only when
`meleeDelay == 1`, where it multiplies by 1; so it never compensates, and in the one configuration where it runs
it **rounds every melee-weapon hit to a whole number** (a side effect worth knowing if anyone pins meleeDelay 1).
Worked: steel longsword, cooldown 2.6 s → E[1.82 s]; 23.1 → 33.0 swings a minute. Melee skill XP per swing is
scaled by cycle time, so XP per minute is unchanged. Not touched: melee hit chance, dodge, parry, stagger (95 ticks
per landed hit, vanilla), damage randomisation (×0.8-1.2, vanilla).

**3.5-A. Melee and animal attacks per landed hit (armour at 100% HP).**

| attack against armour | tech mult | vanilla E[dmg] | Yayo E[dmg] | Yayo P(no dmg) |
|---|---|---|---|---|
| steel longsword stab 23, AP 0.345, vs flak jacket 0.55 (Industrial) | ×1 | 19.5 | 18.8 | 0.06 |
| steel longsword stab 23 vs recon armour 0.92 (Spacer) | ×0.5 | 13.1 | **1.7** | 0.75 |
| spear stab ~26, AP 0.39 (Neolithic) vs flak jacket | ×0.75 | 22.9 | 19.4 | 0.10 |
| fist 8.2, AP 0.12 vs flak jacket | ×0.5 | 5.6 | 2.0 | 0.42 |
| thrumbo horn 23, AP 0.345, vs flak jacket | ×0.5 | 19.5 | **11.5** | 0.24 |
| thrumbo horn 23 vs recon armour | ×0.35 | 13.1 | **1.2** | 0.80 |
| warg-size bite 15, AP 0.225, vs flak jacket | ×0.5 | 11.3 | 5.4 | 0.33 |

Combine with tempo: a longsword-armed raider against a colonist in recon armour lands 1.43× the hits for 13% of the
vanilla damage each; an animal gets no tempo bonus (natural attacks are not melee weapons).

### 3.6 Mechanoids and animals (MEASURED: `ApplyDefPatches`, `applyArmor` natural path)

- **Every PawnKindDef whose `defaultFactionDef` is Mechanoid** (66 kinds on 66 races, including the player's buildable Biotech mechs such as Militor and Lifter, so it is faction-blind): race `ArmorRating_Sharp` ×1.3 and `combatPower`
  ×1.3, once per session. Blunt and Heat untouched. Lancer 0.40 → 0.52, centipede 0.72 → 0.936. Raid points buy
  1/1.3 = 77% as many mechs.
- **Natural armour uses the durability model with the pawn's health as "HP"** (3.1 point 4).

| target | vanilla E[dmg] | Yayo E[dmg] | Yayo P(no dmg) |
|---|---|---|---|
| assault rifle 11 vs healthy thrumbo (natural 0.60) | 7.4 | 5.6 | 0.29 |
| same, thrumbo at 50% health | 7.4 | **8.3** | 0.14 |
| assault rifle vs lancer (0.40 vanilla / 0.52 Yayo) | 9.1 | 7.1 | 0.18 |
| assault rifle vs centipede (0.72 / 0.936) | 6.4 | **1.0** | 0.75 |
| charge rifle 15, AP 0.35, vs centipede | 10.8 | 4.8 | 0.58 |

The centipede row is the mech buff and the durability model compounding: a healthy centipede shrugs off 75% of
rifle hits outright, then softens as it is damaged. (Vanilla column = clean vanilla: vanilla engine and the rifle's derived AP 0.165; Yayo column = AP 0.19.)

### 3.7 Body-part coverage (MEASURED: `ApplyDefPatches`, `handProtect`)

1. Any apparel def whose `bodyPartGroups` include Arms gains Hands; Legs gains Feet (both only if missing). From
   the 2026-10-04 dump: 108 defs gain Hands, 92 gain Feet (first dive, COMPUTED).
2. Apparel that covers Hands or Feet and none of Torso, FullHead, UpperHead, Shoulders (Arms/Legs may also be present: our Armoury's `guy762_armband_cortosis` is one) is moved from each vanilla
   layer to a parallel layer: OnSkin→`OnSkin_A`, Middle→`Middle_A`, Shell→`Shell_A`, Belt→`Belt_A`,
   Overhead→`Overhead_A` (draw orders 0/100/200/300/400). Gloves and boots then never conflict with a body
   garment on the same layer, so a pawn can wear gloves *and* an arm-covering jacket. 25 defs re-layered.
3. Applied in `Root_Play.Start`, i.e. after the main menu, once per session: info cards opened from the main menu
   show vanilla coverage, and the change survives a settings toggle until restart.

### 3.8 The injury pipeline outside the armour roll (MEASURED, Yayo prefix vs vanilla `ApplyDamageToPart`)

| point | vanilla | Yayo | consequence |
|---|---|---|---|
| headshot flag | any `isRanged` damage to a FullHead part | only `DamageDefOf.Bullet` | blasters, arrows, needles, thrown weapons never register a headshot: no "Headshot" text mote, no `Headshots` record |
| `deflected` on a 0-damage result | always set | set only when a metal layer or the "forced deflect" branch ended it | a cloth/flak/natural full block shows the **diminished** effecter and plays the impact sound instead of the deflect effect and `Notify_DamageDeflected`; melee log reads "hit", not "deflected"; `DamageWorker_Flame` may still ignite |
| `deflected` on a passing hit | never | set when the *natural* layer took the forced-deflect branch | mechs and armoured animals show a metal "ping" and **skip the impact sound** on hits that still wound; flame damage then never ignites them |
| **hit-part choice** | the worker's **virtual `ChooseHitPart`**: Stab sends an outside hit inward with `stabChanceOfForcedInternal` (0.6 for melee Stab and RangedStab); Blunt/Cut/Bite/Scratch force outside parts | always the base `GetRandomNotMissingPart(def, height, depth)` | **melee stabs never reach organs this way** (knives, spears, sword points, scyther blades, horns), and Stab's 0.75/0.4 outer/inner damage split never happens (the outer part takes all of it); ranged blunt/cut can now land on internal parts directly. Fewer heart/lung/liver kills, more surface damage. Any modded worker's `ChooseHitPart` override is ignored the same way (MEASURED: RimSage `DamageWorker_AddInjury.GetExactPartFromDamageInfo`, `DamageWorker_Stab`) |
| non-propagating injuries (`AllowDamagePropagation` false) | `FinalizeAndAddInjury` (protected, patchable) | Yayo's private copy | drops `sourceLabel` (health-tab "by …" text), `sourceToolLabel`, the mutant-attacker label, the **social-fight `destroysBodyParts = false` rule**, and the worker's `additionalHediffsThisPart`; any other mod's patch on `FinalizeAndAddInjury` is skipped for these hits (§8.4) |
| propagating injuries | `ApplySpecialEffectsToPart` (virtual) | same method, called by **uncached reflection** (`GetMethod` + `Invoke` with a boxed array) per call | same result, slower |
| instant-kill protection, permanent-injury check, IncomingDamageFactor | | copies (instant-kill uses `def.lethalSeverity > 0` instead of `IsLethal`) | negligible |

Bleeding, pain, stagger, infection, scarring and organ destruction are computed downstream from the injury severity
by vanilla code that Yayo does not touch. They change only because severities change (more blocks, more
Sharp→Blunt conversions: a blunt bruise does not bleed, so **bleeding falls** while armour is fresh).

## 4. Animations, visuals, UI

**Yayo's adds no animation, art or sound in 1.6, but it removes one vanilla animation and changes several
effects.** Everything below is MEASURED from the code paths named.

| item | what happens | source |
|---|---|---|
| weapon draw / aim / swing / twirl animation | **none.** Removed from the mod in 1.5 (its own news entry); the 1.6 and 1.5 DLLs have no render patch. The settings keys `advAni_*`/`ani_twirl_*` survive only as translations. The separate *Yayo's Animation* mod is not in our list | §2.2 |
| **gun recoil kick (vanilla 1.6)** | **lost** for every pawn and turret shot through Yayo's `TryCastShot` (all of them, with `advShootAcc` and `turretAcc` on): the copy never writes `lastShotTick`, so `EquipmentUtility.Recoil` (pawn weapon draw, `PawnRenderUtility.DrawEquipmentAiming`; turret top, `Building_TurretGun`) sees a shot from tick −999999 and draws no kick. `recoilPower` defaults to 1 on every ThingDef, so every gun is affected | §3.3 |
| bullets | 3× faster, capped at 2 tiles/tick: tracer sprites cross the screen in a third of the time, mostly a streak or invisible at close range. The cap (`maxBulletSpeed` 200) exists "to prevent bullets from becoming too invisible" (its own tooltip) | §3.4 |
| grenades, thrown pila, arrows (speed >23 or fused) | arc 3× faster | §3.4 |
| deflect effecters | full blocks by non-metal armour show the *diminished* effecter instead of *deflect*, and play the flesh impact sound; mechs/armoured animals get a metal "ping" with no impact sound on hits that still wound | §3.8 |
| pawn hit flash / jitter | `Notify_DamageDeflected` (deflect jitter) fires less for cloth/flak blocks, more for natural-armour partial blocks | §3.8 |
| "Headshot" text mote | only for `Bullet` damage; never for blasters, arrows or thrown weapons | §3.8 |
| battle log | melee entries say "hit" instead of "deflected" for non-metal full blocks; injuries from non-propagating damage lose the weapon/tool label in the health tab ("Cut" instead of "Cut (longsword edge)") | §3.8 |
| info card: melee DPS / cooldown | `StatWorker_MeleeAverageDPS` and the cooldown readout call the patched `Tool.AdjustedCooldown`, so an equipped melee weapon's DPS shows a **different random number each time the card redraws** (between ~0.6× and ~2.9× of the true average rate). The def-level card (no Thing) is unpatched and shows vanilla | §3.5 |
| info card: armour | the vanilla `ArmorRating_*` description ("half the armor rating deflects…") still shows; it describes the vanilla formula, which is **not** the one running. Yayo adds no stat, no tooltip and no explanation line for its own model | RimSage StatDef text |
| info card: coverage | after a game is loaded, armour lists Hands/Feet; from the main menu it does not | §3.7 |
| hit-chance tooltip | shows Yayo's skill-weighted number (consistent with what is rolled) | §3.2 |
| mod settings window | one scrolling page: Reset-all button, ammo group, melee, armour/accuracy, shooting accuracy, misc; version label. No in-game stat overlays | §5 |
| news dialog | two `TabulaRasa.UpdateDef` entries (shown by neronix17's Tabula Rasa toolbox) with the 11-texture bundle's banner | §6 |

## 5. Settings

**Our install has no settings file**: there is no `Mod_2854006492_YayoCombatMod.xml` in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config` (MEASURED 2026-10-10), so
`GetSettings` returns the field initialisers, and the Mod constructor pushes them to the static switches
(`ApplySettingsFrom`, with clamps). The log line `[YayoCombat] Removing ammo recipes. Found 18 ammo recipes.`
confirms `ammo = false` was live on the full list (MEASURED 2026-10-10 ~18:40 in `Player-prev.log`; that log has
since rotated, and the later full-list `Player.log` stopped before `Root_Play.Start`, so re-check on the next load). The other switches print nothing; their
live values are the initialisers below (MEASURED from code; no log evidence exists for them).

| setting | live value (= code default) | "Reset all" sets | UI range → clamp | read by | turning it off/vanilla does | restart? |
|---|---|---|---|---|---|---|
| ammo | **false** | **true** | bool | 22 ammo patches, P7 | (already off) on: every ranged weapon above Neolithic needs Yayo ammo; ammo recipes return; traders, drug policies, hunting, AI reload all change | yes (comps added at start) |
| refillMechAmmo | true | true | bool | ammo | nothing while ammo off | |
| ammoGen / maxAmmo | 1 / 1 | 1 / 1 | 0-10000 → ≥0.0001 | ammo | nothing while ammo off | yes |
| enemyAmmo | 70 | 70 | 0-500 | ammo | nothing while ammo off | |
| supplyAmmoDist | 4 | 4 | −1-100 | ammo | nothing while ammo off | |
| meleeDelay | **0.7** | 0.7 | 0.1-5 → 0.2-2 | P5, P6 | 1.0 removes the +43% speed (but turns on P6's integer rounding) | no |
| meleeRandom | **1.3** | 1.3 | 0-3 → 0-1.5 | P5 | 0 removes the jitter; P5 is fully bypassed only when meleeDelay 1 **and** meleeRandom 0 | no |
| handProtect | **true** | true | bool | P7 | off: no Hands/Feet coverage, no `_A` layers | yes |
| advArmor | **true** | true | bool | P1, P7 (mech ×1.3) | off: vanilla armour engine and vanilla injury pipeline; mech buff persists until restart | P1 no, mech buff yes |
| armorEf | **50** | 50 | 0-100 | P1 | 0: defend chance = `defence × hp` (half today's); 100: divide-by-zero guard absent, `u × 0 < …` → defend branch always fires when defence > 0 | no |
| unprotectDmg | 1.1 | 1.1 | 0.1-5 → 0.1-2 | **nothing** (no reader) | nothing | |
| advShootAcc | **true** | true | bool | P2, P3 | off: vanilla shot resolution and accuracy; recoil, mortar skill, even dispersal, `canGoWild`, turret cover all return | no |
| accEf | **60** | 60 | 0-100 | P3 | 0: no skill bonus (P2's other changes remain while advShootAcc on) | no |
| missBulletHit | 50 | 50 | 0-100 | P2 | 50 = vanilla | no |
| mechAcc / turretAcc | **true / true** | true / true | bool | P2, P3 | off: mechs / turrets take the vanilla path | no |
| colonistAcc | **false** | **true** | bool | P2, P3 | on: only colonists get Yayo's path (enemies vanilla) | no |
| baseSkill | 5 | 5 | 0-20 | P3 | skill assumed for skill-less shooters | no |
| bulletSpeed / maxBulletSpeed | **3 / 200** | 3 / 200 | 0.01-100 / 1-10000 | P4 | 1 = vanilla for projectiles up to speed 200 (the 2 tiles/tick cap still clamps faster ones; the prefix still replaces the getter) | no |
| enemyRocket | **false** | **true** | bool | P7 | on: NPC loadouts can include the rocket launcher | yes |

Two traps (MEASURED): **"Reset all" is not the defaults.** It turns ammo ON, enemy rockets ON and accuracy
colonist-only, so one click silently changes three systems. And **def-level switches only apply at
`Root_Play.Start`** (`patchApplied` guard): changing handProtect, advArmor's mech buff, ammo or enemyRocket
mid-session does nothing to defs until the game is restarted, while the formula switches take effect at once.
The settings text also misdescribes three of them: meleeDelay promises damage compensation (dead), unprotectDmg
promises a damage factor (dead), advAni/ani_twirl describe removed features.

## 6. Defs added and patched (MEASURED: parsed XML; sanity probe = the 18-recipe log line matches the 18 parsed RecipeDefs)

**Added (40 defs):**

| type | count | defs |
|---|---|---|
| ThingDef | 13 | 9 ammo items (`yy_ammo_{primitive,industrial,spacer}{,_fire,_emp}`), 2 unfinished ammo, `Gun_AntiArmor_Rocket`, `Bullet_AntiArmor_Rocket` |
| RecipeDef | 18 | ammo recipes; with ammo off their `recipeUsers` are cleared at start and `RecipeDef.AvailableNow` is forced false |
| ApparelLayerDef | 5 | `OnSkin_A`, `Middle_A`, `Shell_A`, `Belt_A`, `Overhead_A` |
| JobDef | 1 | `EjectAmmo` |
| ThingCategoryDef | 1 | ammo category |
| TabulaRasa.UpdateDef | 2 | news entries (load only with `neronix17.toolbox`, which is active) |

The rocket launcher (live): single use, `Bomb` 140 damage, AP 0.9, radius 1, speed 50 (so ×3 → 1.5 tiles/tick),
range 20, warmup 3 s, forced-miss radius 1, manual cast only; craft at the machining table, Gunsmithing, Crafting
10, 20 steel + 30 chemfuel; tagged `RewardStandardLowFreq` (quest rewards) and `ExoticMisc` (exotic traders);
explodes if it burns. With `enemyRocket` off its weaponTags are emptied, so NPCs never carry it, but the player can
craft, buy and be rewarded it. The 9 ammo items still exist with `tradeability None`.

**Patched by XML (3 ops, always applied, not settings-gated):** `PatchOperationReplace` of the whole
`<projectile>` block of `Pilum_Thrown` (dmg 25→22, AP 0.10→0.25), `Bullet_AssaultRifle` (AP derived 0.165→0.19),
`Bullet_BoltActionRifle` (AP derived 0.27→0.17). Whole-block replacement also **erases any other mod's earlier
edits to those three `<projectile>` blocks** (load order: Yayo's at index 375 of 551).

**Patched in C# at game start (P7), from the 2026-10-04 dump (first dive, COMPUTED):** 108 apparel gain Hands, 92
gain Feet, 25 gloves/boots re-layered; 66 mechanoid PawnKindDefs on 66 races get sharp armour and combat power
×1.3; 18 recipes emptied; 9 ammo items untradeable; one weaponTags list cleared.

## 7. Performance

No profiler run exists for this mod (`tps_cost: UNMEASURED` in the audit facts). Costs below are INFERRED from the
code; the call frequencies are MEASURED from where vanilla calls each method.

| hook | how often | per-call cost over vanilla | verdict |
|---|---|---|---|
| `Pawn.Tick` postfix (P-ammo) | every pawn, every tick | Harmony wrapper + one static bool | negligible; the most frequent hook in the mod |
| `Projectile.StartingTicksToImpact` prefix | every live projectile, several times per tick **and per rendered frame** | two field injections, one multiply, one compare | negligible |
| `ShotReport.HitFactorFromShooter` postfix | every shot **and every AI/tooltip hit-chance evaluation** | one extra `GetStatValue(ShootingAccuracyPawn)` plus a **second full call** of the method, which re-runs every other postfix on it (VGE's) and the range-band stat lookups | roughly doubles the method; the likeliest measurable cost, multiplied by CAI-5000's target scoring |
| `Verb_LaunchProjectile.TryCastShot` (replaced) | every shot | about vanilla | negligible |
| `DamageWorker_AddInjury.ApplyDamageToPart` (replaced) | every damaged body part | **uncached `Type.GetMethod` + `MethodInfo.Invoke` with a boxed 4-element array** on the propagating path; a LINQ `All` over not-missing parts when the part is preset | microseconds per hit, event-driven; matters only in big fights |
| `Tool.AdjustedCooldown` postfix | every melee attack, every DPS/cooldown stat readout (per UI frame while a card is open), every melee-verb selection | one `Rand.Value` | cheap, but it **advances the game's RNG from UI and AI paths** (§8.6) |
| `Thing.TakeDamage` prefix | every damage event on any thing | one float compare | negligible |
| `RecipeDef.AvailableNow` postfix | every recipe-availability check (bills UI, work-giver scans) | `string.Contains` on the defName | negligible |
| `Pawn_EquipmentTracker.GetGizmos` postfix | each selected pawn, each frame | re-yields the gizmo enumerator (one iterator allocation) | negligible |
| static constructor | once at startup | if `CompOversizedWeapon` exists (JecsTools defines it), reflects over every weapon def's comps to cache offsets nothing reads | small one-off startup cost, pure waste |
| `Root_Play.Start` def pass | once per session | loops all apparel and PawnKindDefs | one-off |

**Verdict: low (INFERRED).** Nothing heavy runs per tick. TPS is not a reason to keep or cut it. If a number is
ever wanted: profile `HitFactorFromShooter` and `ApplyDamageToPart` on a combat save (`YAYO_TPS_MEASURE_HOOK_COST`).

## 8. Interactions

### 8.1 Our own mods

| ours | relation to Yayo's | evidence |
|---|---|---|
| **Armoury armour retune** (`src/RimStarWars/Armoury/Source/gen_armour_patch.py`) | Built on "THE ENGINE, verified by decompiling Verse.ArmorUtility": *2.0 IS IMMUNITY*, *HIGH AP DEFEATS IMMUNITY* (hence lightsaber AP 0, 99 damage), *a single advanced layer near 0.8-0.9 meets the ~5-shot contract*. **None of the three holds in the live engine**: full block caps at 90% (cortosis 2.0 still lets 10% of lightsaber hits through as reduced damage), a 0.8-0.9 layer at full HP stops most rifle hits outright until it wears (3.1-A), and our blades and every animal/natural attack take the tech penalty against worn apparel. The retune is correct for vanilla and wrong for the game we run | MEASURED, both read |
| **Lightsabers run two different armour engines today** | 8 lightsaber defs re-tooled by Armoury (`guy762_ToolCapacity_Saber*` → `guy762_MeleeDamage_ecut/estab`, `DamageWorker_Cut/Stab`, **Heat** armour) go through Yayo's model. The other 8 `lee.theforce.lightsaber` weapon defs (`Force_Lightsaber_KoTOR`, `_UniqueAnakin`, `_UniqueObi`, `_BuildYourOwn`, `Force_ImbuedBlade`, `Force_Ezra_BlasterLightsaber`, `Force_Protosaber`, `Force_SoulSaber`) still on `Force_SaberSlash/Stab` use `Lightsaber.DamageWorker_LightsaberCut`, which has its **own private `ApplyDamageToPart` calling vanilla `ArmorUtility.GetPostArmorDamage`**, so they use the **vanilla** formula. Same game, same cortosis, two answers | MEASURED: def dump 2026-10-04 + decompiled `Lightsaber.dll` |
| **Ion weapons** | Jawa Ion Blaster: EMP, `harmsHealth` false, no armour category → untouched by either engine. Armoury ion (`guy762_Ionization`, `DamageWorker_Ionize`, `DamageWorker_RaceHediffBase`, `DamageWorker_AllDroids`, all `: DamageWorker_AddInjury`): their injury half runs through Yayo's prefix like any other; the ion hediff lands on `result.parts`, which Yayo fills even on a full block. No ion number assumes Yayo | MEASURED (first dive §5.5, re-checked class bases) |
| `DamageWorker_RM_UV` (Contagion) | subclass of `DamageWorker_AddInjury`, so UV burns use Yayo's pipeline and its headshot/deflect quirks | MEASURED |
| **Weapon register** (`src/RimMandrake/Utils/gen_weapon_register.py`) | reads declared AP from the def dump; `CALIB_PATCHED = {"ar_ap": 0.19}` asserts Yayo's XML value and fails on vanilla's derived 0.165. Only the 3 rewritten projectiles move (10 rows, 9 Cherry-Picker-cut) plus the rocket row. **The register does not model either armour engine, accuracy or melee tempo**, so it is silent about everything in §3 | MEASURED (code on origin/main) |
| **Wrecked Machines** (`src/RimMandrake/WreckedMachines`) | no weapon, armour, PawnKind or combat def; its machines are buildings/items. No interaction beyond Yayo's no-op `Thing.TakeDamage` prefix | MEASURED (git grep) |
| Armoury `loadAfter` Yayo's | the only declared link; no Armoury def names a Yayo def, layer or class | MEASURED (first dive) |

### 8.2 Stronger Quality Scaling (`kas.strongerscaling`, workshop 1206001612, XML only)

It replaces whole vanilla StatDefs with steeper `StatPart_Quality` factors (MEASURED, parsed from its `1.6\Defs`):
armour ×0.20/0.60/1/1.30/1.60/1.90/2.35 (vanilla 0.6/0.8/1/1.15/1.3/1.45/1.8); ranged damage ×0.55…1.70
(vanilla 0.9/1/1/1/1/1.25/1.5); melee damage ×0.55…1.90; accuracy ×0.55…2.1; ranged cooldown ×1.2…0.70;
shield energy ×0.2…3.0; plus market value, deterioration, beauty, comfort, bed rest, joy, surgery, insulation, pack
radius. Its redefined `ArmorRatingBase` carries no `maxValue`, so the vanilla 2.0 cap on armour ratings is probably gone in our game (INFERRED from the XML; check a live `GetStatValue` before relying on "2.0 = immunity" under either engine). It does **not** touch `RangedWeapon_ArmorPenetrationMultiplier` (vanilla ×1.25/×1.5 at masterwork/legendary).

**It compounds with Yayo's on both sides.** Armour: 3.1-A shows the cliff (masterwork flak jacket lets 4% of rifle
damage through live, 53% in clean vanilla). Melee: SQS melee damage ×1.65 masterwork on top of Yayo's +43% swings
is 1.65 × 1.43 ≈ 2.4× a vanilla normal sword's DPS against unarmoured targets, and 1.6× a vanilla masterwork one (vanilla masterwork melee ×1.45). Accuracy: SQS weapon accuracy ×1.75 masterwork
multiplies Yayo's skill bonus. The two must be ruled on together.

### 8.3 The Combat Extended ban (`design/Jawa/mods/forbidden_mods.md`, "Combat overhauls")

The ban covers CE "and equivalent total combat overhauls" for three reasons. Against what Yayo's actually does:

1. *"Enormous compatibility surface; patches essentially every weapon/pawn"*: **applies in kind.** Yayo's has only
   3 XML ops, but it **replaces two core engine methods** (every shot, every injury) and a getter, which silently
   voids other mods' transpilers and some prefixes on them unless they ship an exemption, as VGE does (§8.4), and rewrites every apparel def's coverage and
   every mech kind at game start. CE's surface is wider; Yayo's is the same kind of surface.
2. *"Over-arms the PLAYER as much as the enemy … not a player-power arms race"*: **applies.** The tech rule protects
   worn apparel only (the player's curated crew) against animals, tribals and mech melee; quality armour becomes
   near-immunity (with SQS, a cliff); +43% melee-weapon tempo; skill counted twice for accuracy (the player's
   trained shooters); a player-only rocket launcher. The mech ×1.3 is the one buff that mostly helps the enemy (it also covers a mechanitor's own mechs).
3. *"Risk on frequently regenerated temporary maps"*: not specific to Yayo's.

The ban's chosen route, *"keep base game vanilla-lethal … tuned vanilla Custom difficulty, NOT a lethality
overhaul"*, is what the live armour model departs from. With ammo off, the CE-like headline feature is the one part
**not** running; everything that is running is engine replacement.

### 8.4 Other mods patching the same methods (MEASURED: static census + decompile)

Method: every DLL of the 551 mods in `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (664 DLLs, 1.6 and
version-less folders) was byte-searched for the target names (UTF-8 and UTF-16); sanity probe: Yayo's own DLL hit
14 of 17 names. The 27 hits naming a patched method were decompiled (ILSpy) and read. Harmony here is **2.4.1**
(decompiled `0Harmony.dll`): when a prefix returns false, every later prefix that could affect the original (bool
return, `ref`/`out` or reference-type argument) is **skipped**, all postfixes still run, and the original body
with **all transpilers** never runs. Same-priority prefixes run in registration order: Mod-constructor patchers by
load order, then `[StaticConstructorOnStartup]` patchers.

| vanilla method | other active patcher | kind | outcome while Yayo's is on |
|---|---|---|---|
| `Verb_LaunchProjectile.TryCastShot` | **Vanilla Gravship Expanded** (`vanillaexpanded.gravship`): 3 transpilers (manning pawn as launcher, gravship targeting scatter, muzzle origin), **plus `YayoCombat_CompatibilityPatch`**, a prefix on Yayo's own prefix that makes it return true for `Verb_ShootWithWorldTargeting` and subclasses | transpiler ×3 + compat prefix | **works for VGE's gravship guns**: both gravship turrets in our dump (`VGE_GaussGun`, `VGE_MassDriver`) use `Verb_ShootWithSmoke`, so vanilla `TryCastShot` and the transpilers run for them. A VGE gun on plain `Verb_Shoot` would lose the transpilers; none is in the 2026-10-04 dump (MEASURED). Which of two installed folders sharing this packageId is loaded: UNVERIFIED |
| same | VEF Weapons: `VerbAccuracyUtility.CheckAccuracyEffects` | void prefix (instance only) + finalizer | **works**: not "affects original", runs; its flags are read by VEF's `ShotReport` patches, which Yayo still calls |
| same | VEF Buildings: dual-fuel consumption | postfix | works |
| same | **CAI-5000** (`krkr.rule56`, logs `ISMA: Patched verb type …`): shared-sight shot blocking + "being targeted" notice | bool prefix with `ref __result` + postfix, registered from a `LongEvent` (after every Mod constructor) | the prefix on `Verb_LaunchProjectile.TryCastShot` is **skipped** (registered after Yayo's). CAI also patches `Verb_Shoot.TryCastShot`, the override ordinary guns run first, so for ordinary guns its block and notice still fire there; verbs that reach `Verb_LaunchProjectile.TryCastShot` without a patched override lose them (INFERRED impact: low) |
| `DamageWorker_AddInjury.ApplyDamageToPart` | VEF Storyteller: storyteller `allDamagesMultiplier` (`ref DamageInfo`) | prefix | **works**: VEF patches in its Mod constructor at load index 21, before Yayo's (375), so it runs first and Yayo reads the scaled `dinfo` |
| same | **Vanilla Traits Expanded**: Drunken Master trait (`ref DamageInfo`, melee damage ×(1 + stage/2) when drunk) | prefix | **silently skipped**: VTE patches from a `[StaticConstructorOnStartup]`, i.e. after Yayo's, and its `ref` argument marks it "affects original". The trait does nothing |
| `ArmorUtility.GetPostArmorDamage` / `ApplyArmor` (vanilla) | **JecsTools** damage soak (`Pre_ApplyArmor`, `Post_GetPostArmorDamage`) | prefix / postfix | **never called** for injuries (Yayo uses its own copy). Partial soak lost; soak that fully absorbs still works (it lives in `PreApplyDamage`). And `tempDamageAmount` stays set until some other caller reaches vanilla `ApplyArmor` (Lightsaber's worker, Fortified's plate), where it is applied to the wrong hit. No `HediffComp_DamageSoak` user in our dump today, so latent |
| same | **VEF Apparels**: held-shield armour (prefix on `GetPostArmorDamage`), plus a transpiler on `ApplyArmor` | prefix, transpiler | never called for injuries. No `VEF.Apparels.Apparel_Shield` def in our dump, so latent |
| same | **GiddyUp**: mounted-animal `armorModifier` | `StatPart_Armor` on the armour stats + a postfix on `ApplyArmor` | **half works**: the rating bonus is a stat part, which Yayo reads; the postfix's extra damage ÷modifier and metal flag are lost for `GiantToad`/`KingToad` (`zal.gianttoads`) |
| same | **VRE Archon**: "psychically warped" sets armour to 0 | prefix on `ApplyArmor` | never called: the `VREA_PsychicallyWarped` hediff's armour strip does nothing |
| `DamageWorker_AddInjury.FinalizeAndAddInjury` | Big and Small (`redmattis.betterprerequisites`): bite-devour | patch on the vanilla method | skipped for non-propagating hits only (Yayo's private copy); propagating hits reach vanilla through `ApplySpecialEffectsToPart` |
| `ShotReport.HitFactorFromShooter` | VGE: gravship-turret accuracy | postfix | works; Yayo's postfix exits for non-pawn casters. Note Yayo's nested re-call runs VGE's postfix a second time (harmless: VGE only touches turrets) |
| `Projectile.StartingTicksToImpact` | Vehicle Framework: `StartingTicksFromTurret` | postfix | works, on top of Yayo's ×3 |
| `Tool.AdjustedCooldown(Thing)` | none | | (CaravanAdventures, Big and Small, VEF last-stand/weapon traits, MVCF patch the *different* `VerbProperties.AdjustedCooldown`; they multiply with Yayo's factor) |
| `PawnGenerator.GenerateGearFor` | Simple Sidearms, Melee Animation, JecsTools shields, HAR | postfixes | Yayo's postfix is an ammo no-op |
| Lightsaber `DamageWorker_LightsaberCut`, Fortified `DamageWorker_CountByBodysize` (`FFF_ShapeChargeBullet`), Fortified `CompBulletproofPlate` | their own `ApplyDamageToPart` copies / direct calls to vanilla `ArmorUtility` | not patches | these damage types **bypass Yayo's armour model and use vanilla's** |

### 8.5 Other notable neighbours

- **CAI-5000** (`krkr.rule56`) has its own armour report (raw ratings via `GetStatValue`), not a formula; its target
  scoring calls `ShotReport`, so it sees Yayo's accuracy (consistent) but rates armour as if vanilla (it does not
  know a masterwork jacket is near-immunity). INFERRED from the decompiled `CombatAI.dll` structure.
- **Show Me Your Hands**: its `YayoAdapted`/`YayoAnimation` folders exist only for 1.3 and its 1.6 LoadFolders do
  not reference them, so nothing loads for Yayo's on 1.6 (MEASURED; the first dive said it did).
- **Melee Animation** (`co.uk.epicguru.meleeanimation`) is detected by Yayo's static constructor; nothing reads the
  flag.
- `sihv.rombonesport` patches Yayo's ammo recipes inside a `PatchOperationFindMod` naming "Yayo's Combat 3", which
  never matches the "(Continued)" name (first dive, MEASURED).

### 8.6 Determinism (relevant to our seeded checks)

`Tool.AdjustedCooldown` draws `Rand.Value` whenever a melee weapon's cooldown is *read*, including stat-card
redraws and melee-verb selection, so opening an info card or an AI DPS estimate advances the game RNG. Any seeded
replay or modcheck walk that involves melee weapons is not reproducible while Yayo's melee tempo is on (INFERRED
from the code path; not observed).

## 9. Gameplay delivered vs what the scenario wants

The scenario's pillars as the owner put them for this order: small crew, scarcity, qualitative danger, gear that
matters. Judgement (INFERRED) on each live piece:

| piece (live) | what it delivers in play | small crew | scarcity | qualitative danger | gear that matters | keep the *idea*? |
|---|---|---|---|---|---|---|
| armour durability (F2 core) | armour as a consumable shield: strip it, then kill; repairs and replacements matter; high-AP weapons have a real job (shredding) | + (a few well-armoured crew hold out) | + (armour HP is a resource to repair) | − (fresh quality armour makes ordinary threats harmless) | ++ | **yes, re-tuned** |
| quality cliff (F2 × SQS) | masterwork/legendary armour ≈ immunity to rifles | − | − (once owned, nothing threatens it) | −− | + (too much) | no |
| tech-tier AP rule | primitive weapons, animals, tribal and mech melee bounce off advanced apparel | + for the player | − | −− (desert megafauna and tribal raids stop mattering to an armoured crew) | + | only if symmetric |
| natural armour scales with health | wounded animals and mechs soften; healthy ones are tanks | ~ | ~ | + (big creatures feel big until hurt) | ~ | maybe |
| mech ×1.3 sharp + points | fewer, tougher mechs | + | ~ | + | ~ | owner's call, as plain XML |
| skill-weighted accuracy | a trained shooter is clearly better; skill matters twice | ++ (each colonist's skill counts) | ~ | ~ | ~ | **yes**, cleanly |
| ×3 bullet speed | shots resolve sooner; grenades land fast | ~ | ~ | ~ | ~ | taste |
| hand/foot coverage | gloves and boots stop being the unarmoured hole; a glove and a jacket can be worn together | + | ~ | ~ | + | **yes** |
| +43% melee weapon tempo (bug) | melee weapons out-DPS their own stat cards; jittery rhythm | ~ | ~ | − | − (stat cards lie) | no |
| replaced shot/injury methods | lost recoil animation, melee stabs no longer reach organs, lost trait/soak/Archon effects, lost headshots for blasters | − | ~ | − | − | no |
| rocket launcher (player-only) | a cheap anti-armour one-shot nobody chose | ~ | − | − | ~ | no (or our own item) |
| ammunition (off) | nothing | | (would be +) | | | separate question; not running |

The pieces that serve the scenario are **ideas** (armour wears, skill matters, extremities are covered); the
**implementation** fights it (one-sided protection, quality cliff, engine replacement). That points to porting ideas,
not keeping the mod.

## 10. Options

Effort: S = hours, M = a day or two with tests, L = a week+. All C# goes in an existing mod of ours with Mod Settings
(house rule), MIT notice kept for anything ported.

| | option | effort | gains | costs and risks |
|---|---|---|---|---|
| **A** | **Keep, pin a settings file** (ammo off, enemyRocket off, meleeDelay 1 + meleeRandom 0; rest as live) | S | no recalibration; keeps durability, skill accuracy, speed, coverage | keeps both method replacements and every §8.4/§3.8 casualty (VTE trait, Archon armour strip, recoil animation, blaster headshots, stab-to-organ); Armoury contract must be re-derived for Yayo's engine (M); SQS cliff must be ruled; meleeDelay 1 turns on integer rounding of melee damage; abandoned-upstream risk each RimWorld patch |
| **B** | **Keep, engine off** (advArmor off, advShootAcc off, bulletSpeed 1, meleeDelay 1/meleeRandom 0, ammo off, enemyRocket off; handProtect on) | S | vanilla engine returns, so every §8.4 casualty and every §3.3/§3.8 regression disappears; our armour design becomes true; keeps coverage | carries a 33-patch mod for one feature; `StartingTicksToImpact` still replaced (at ×1), `Thing.TakeDamage` rounding on (meleeDelay 1); mech ×1.3 needs advArmor off to go (it does); the 3 XML projectile numbers stay |
| **C** | **Remove, port chosen ideas into our own code** | S…M per piece | exactly the chosen behaviour, settings-gated, no engine replacement | build/test time; pieces below |
| **D** | **Remove only** | S | simplest; doctrine-consistent | loses hand/foot coverage; a saved `Gun_AntiArmor_Rocket`/ammo item drops on load with a log line |

**The C pieces, each independently choosable:**

| piece | how, without replacing an engine method | effort | risk |
|---|---|---|---|
| C1 hand/foot coverage | startup pass (port of the 40-line block) or XML patches adding Hands/Feet; our own `_A`-style layers for gloves/boots | S | apparel layer defs in saves are new defs (harmless); conflicts with any mod that also re-layers gloves (none found) |
| C2 skill accuracy | XML patch of `ShootingAccuracyPawn`'s skill curve to the §3.2 right column; **zero C#**, tooltips stay true | S | affects all pawns equally (as Yayo does); turrets unchanged |
| C3 armour that wears in *protection* | a `StatPart` on `ArmorRating_Sharp/Blunt/Heat` that scales an apparel's rating by its HP fraction (e.g. ×lerp(0.6, 1, hp)), with an explanation line on the info card; vanilla formula untouched; optional small postfix on vanilla `ApplyArmor` to scale wear by AP | S (StatPart) + S (wear postfix) | must be designed against Armoury's contract (it adds a degraded-state curve, it does not move the fresh numbers); patches vanilla `ApplyArmor`, which JecsTools/VEF/GiddyUp/Archon also patch additively (no replacement) |
| C4 tech-tier AP rule | only if made **symmetric** (mech/animal natural armour vs primitive weapons too, or only weapon-vs-armour, never natural attacks); a prefix adjusting `armorPenetration` in vanilla `ApplyArmor` | M | design question first; as Yayo ships it, it is a player buff |
| C5 mech armour | an XML patch on mech race `ArmorRating_Sharp` with our own number, if wanted | S | raid points shift unless combatPower also patched |
| C6 bullet speed | XML `speed` on projectiles we want faster | S | taste only |
| not ported | melee tempo (bug), `TryCastShot` copy, injury-pipeline copy, Bullet-only headshots, ammunition, the rocket | | |

**What a clean-vanilla recalibration of the weapon register changes** (re-verified against
`design/Jawa/worldbuilding/review/weapon_register_rows.json` on origin/main, 764 rows, MEASURED):

| rows | state | now → on removal |
|---|---|---|
| `Gun_AssaultRifle`, `Gun_AssaultRifle_Unique`, `AM_M4A`, `AM_AK101A`, `MW2_AssaultCarbine`, `VWE_Gun_MakeshiftRifle` | all cut | AP 0.19 → 0.165 (derived: 11 × 0.015) |
| `Gun_BoltActionRifle`, `Gun_BoltActionRifle_Unique`, `MW2_HuntingRifle` | all cut | AP 0.17 → 0.27 (18 × 0.015) |
| `Pila` | **live** | damage 22 → 25, AP 0.25 → 0.10 |
| `Gun_AntiArmor_Rocket` | **live** | row disappears |
| calibration | | `CALIB_PATCHED = {"ar_ap": 0.19}` becomes a `CALIB_MATCH` entry 0.165 (the docstring's "one deliberate divergence" retired) |

The register does not model armour, accuracy or melee tempo, so **none of §3's in-game changes appear in it**; they
are what actually moves on removal (3.1-A "CLEAN VANILLA" column against "LIVE", 3.2, 3.5, 3.6).

**Recommendation.** **C (remove, port C1 + C2 now; C3 as a designed feature, with the Armoury contract written
against it), plus the SQS ruling in the same sitting.** Not A: it keeps two engine replacements that change where blows land
(§3.8) and silence other mods' code (§8.4), and its armour engine makes our own Armoury design false. If the owner wants to keep feel-testing Yayo's before deciding, **B** is a one-file S change that stops
the collateral today while keeping coverage. The fair case for keeping A: Yayo's armour feels decisive and gives a
strip-then-kill rhythm that vanilla lacks; C3 is how we get that rhythm without the cliff and without the
replacements.

Tickets (proposed names; **not filed**): `YAYO_COMBAT_DECIDE_KEEP_OR_PORT` (owner card, options A-D + C pieces +
SQS), `COMBAT_CORE_BUILD_OWN_PORT` (C1/C2, then C3/C4/C5/C6 as ruled), `ARMOUR_WEAR_STATPART_DESIGN` (C3 against the
Armoury contract), `WEAPON_REGISTER_RECONCILE_YAYO_CALIBRATION` (on removal), `YAYO_SETTINGS_ENFORCE_PINNED_FILE`
(for A or B), `YAYO_TPS_MEASURE_HOOK_COST` (optional).

## 11. What the first dive missed or got wrong

`design/RimMandrake/mod_deepdive_yayo.md` (same day) was right that the engine, not the XML, is the story; its
framing still undersold it ("one calibration constant and four numbers"). New here, or corrected:

1. **Collateral on other mods (§8.4), none of it in the first dive.** Harmony 2.4.1's prefix-skip rule (measured from
   the decompiled `0Harmony.dll`) plus a census of all 551 active mods shows: Vanilla Traits Expanded's Drunken
   Master never fires; VRE Archon's psychic armour strip, JecsTools partial damage soak, VEF held-shield armour and
   part of GiddyUp's mount armour are never called for injuries; CAI-5000's inner targeting prefix is skipped.
   Vanilla Gravship Expanded ships its own exemption, so its gravship guns are unaffected.
2b. **Hit-part choice (§3.8)**: Yayo's injury copy ignores every damage worker's `ChooseHitPart`, so melee stabs
   lose their 60% route to internal organs. Neither dive's first draft had this; the adversarial review found it.
2. **Two armour engines for lightsabers.** The 8 `lee.theforce.lightsaber` weapons on `Force_Saber*` use their own
   damage worker calling vanilla armour; the 8 re-tooled by Armoury use Yayo's. The first dive's "lightsaber vs
   cortosis: Yayo 0.03" row holds only for the latter.
3. **Natural armour runs the durability model with the pawn's health** (thrumbo, insects, mechs): healthy big
   creatures are much tougher, wounded ones softer; with the mech ×1.3 a healthy centipede takes 1.0 of 11 rifle
   damage per hit (clean vanilla 6.4). The first dive treated the natural path only as "a no-op for humans".
4. **The quality cliff, quantified per quality** (3.1-A) and the **wear arc over a fight** (3.1-B).
5. **More shot-resolution regressions:** the rocketswarm launcher's even dispersal is lost; 
   **turrets lose cover** as targets (first dive noted the code line,
   not the effect).
6. **Effects inverted both ways (§3.8, §4):** passing hits on mechs/armoured animals show a metal ping, skip the impact
   sound and **cannot ignite**; cloth full blocks can ignite. First dive covered only the missing deflect.
7. **UI and determinism:** the melee DPS on an equipped weapon's info card is a fresh random number each redraw; that
   draw advances the game RNG from UI/AI paths (§8.6); the vanilla armour tooltip describes a formula that is not
   running.
8. **Settings semantics:** def-level switches only take effect at the next game start; armorEf 100 makes the defend
   branch unconditional; pinning meleeDelay 1 (the first dive's fix) switches on integer rounding of melee damage.
9. **Animations:** confirmed absent since 1.5 (the mod's own news entry; 1.5 and 1.6 DLLs decompiled). The first
   dive's "Show Me Your Hands loads a YayoAdapted folder" is wrong for 1.6: those folders exist only for 1.3 and are
   not in its 1.6 LoadFolders.
10. **Rocket launcher** also needs 30 chemfuel and Crafting 10, and is a quest reward and exotic-trader item.
11. **XML whole-block replacement** erases any other mod's earlier edits to those three `<projectile>` blocks.
12. **Licence scope:** one MIT file, copyright Mlie, covering the whole repository including XML and textures.
13. The facts-row folder bug the first dive reported (Harmony's folder) is **already fixed** on origin/main: the row
    now points at `…\294100\2854006492` with Yayo's own DLLs, defs and licence (MEASURED). The **registry** row's
    verdict reason still said "every ranged AP figure … assumes it" and "ammo consumption is resonant"; corrected in
    this change.

## 12. Review disposition

Adversarial review 2026-10-10 by a fresh-context Opus agent (Yayo source + decompile, RimSage 1.6, third-party
decompiles, Harmony 2.4.1 decompile, def dump; the calculator re-run and matched every table). 17 findings, all
re-checked against the code before applying:

- **BLOCKER, VGE gravship turrets "void"**: VALID. VGE ships `YayoCombat_CompatibilityPatch` (a prefix on Yayo's
  prefix) exempting `Verb_ShootWithWorldTargeting` subclasses; both gravship turrets in the dump use one. The census
  searched for vanilla method names only and missed a patch *on Yayo's own method*. Fixed in §0, §8.3, §8.4, §9, §10,
  §11; the collateral argument now rests on the other casualties and on §3.8.
- **BLOCKER, hit-part choice "identical"**: VALID (RimSage `GetExactPartFromDamageInfo` calls virtual `ChooseHitPart`;
  Yayo calls the base body). Added to §0 (item 5), §3.8, §9, §10, §11.
- MAJOR, "90% of defends fully blocked": VALID, §3.1 point 1 rewritten (`min(R−AP, 0.9)`).
- MAJOR, mech ×1.3 and natural model "enemy-side": VALID, now faction-blind in §0, §3.1, §3.6, §8.3.
- MAJOR, §2 Harmony sentence contradicted §8.4: VALID, §2 now states the measured 2.4.1 rule.
- MAJOR, "extra 1-in-N aimed shot": VALID (vanilla does the same), removed from §3.3 and §11.
- MAJOR, GiddyUp mount armour fully lost: VALID, it is half lost (StatPart survives), §0/§8.4/§11 fixed.
- MINOR: virtual/protected and instant-kill wording (fixed); log evidence rotated (tagged with time, §5); sim
  "vanilla" column used AP 0.19 (fixed to 0.165, §3.6 numbers updated); sim read armour HP before wear (fixed, 3.1-B
  updated, 3.1-A bias noted); molotov not sped up and the speed cap at bulletSpeed 1 (fixed); SQS removes the 2.0
  cap (added as INFERRED, §8.2); re-layer rule wording (fixed, §3.7); `Verb_Shoot` reaches the method via base
  (fixed); "humans" → baseline humans (fixed); 540-weapon recoil count unsourced (now cited with its limit).
- Rejected: none.

