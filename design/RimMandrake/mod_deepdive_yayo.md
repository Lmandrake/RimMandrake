# Yayo's Combat 3 — deep dive (what it gives beyond normalisation)

Owner order, typed 2026-10-10: *"We need deeper analysis on yayo. What does it offer beyond the annoying
normalization. Deep dive required."* Offline analysis: no bridge, no game, no mod list changed. Audit card
this answers: `design/RimMandrake/mod_audit/OWNER_CARDS.md` C14.

Evidence tags: **MEASURED** = read from the installed mod, its source, the def dump, a Player.log or RimSage's
decompiled 1.6; **COMPUTED** = arithmetic on measured inputs by the scripts named; **INFERRED** = reasoning,
said as such.

## 0. The answer in five lines

1. **Ammunition is OFF in our game** (MEASURED: no settings file exists, so the code default `ammo = false`
   applies, and the 2026-10-10 full-list Player.log prints `[YayoCombat] Removing ammo recipes. Found 18`).
   The audit registry's "ammo consumption is resonant with scarcity" describes a feature we do not run.
2. **The "normalisation" is three projectile rewrites** (assault rifle, bolt-action rifle, pila). Only **one live
   row** of the 764-row weapon register uses them (the pila). The claim that "every ranged AP figure" depends on
   Yayo's is false.
3. **What Yayo's really changes is the combat engine**, through C# that is on by default: a different armour
   model (armour that blocks almost everything until it is worn down), skill-weighted accuracy for every pawn,
   bullets about 3x faster, gloves and boots folded into arm and leg armour, mechanoids +30% sharp armour.
   **Melee weapons hit about 70% harder** because of a bug.
4. **Our own armour retune was designed against the vanilla engine, but the live game runs Yayo's.** Its central
   rule, that an armour rating of 2.0 makes you immune, is false while Yayo's is loaded (§5.3).
5. **Recommendation: remove it and port two small pieces** (hand and foot coverage, plus an optional
   skill-accuracy curve). The cost is one calibration constant, 4 projectile numbers that move 10 register rows
   (9 of them already cut), and one row removed. The armour-durability model is the only piece with real design
   value. Whether to keep it is the owner's call (§8, §9).

## 1. Identity and source

| | |
|---|---|
| name / packageId | Yayo's Combat 3 (Continued), `Mlie.YayosCombat3`, version 1.6.13 (About/Manifest) |
| on disk | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2854006492` (only copy; none under `…\common\RimWorld\Mods`) |
| loads for 1.6 | `/`, `1.6`, `Assets` (LoadFolders.xml); hard dependency Harmony only (HugsLib dropped in 1.6) |
| code | `1.6/Assemblies/yayoCombat.dll` (80,896 bytes, 2026-06-02) |
| source | https://github.com/emipa606/YayosCombat3, HEAD `4f436d1` (2026-06-02). **The DLL in that repo is byte-identical to the installed DLL** (`cmp`), so the source read below is the code that runs (MEASURED) |
| licence | **MIT** (`LICENSE.md`, "Copyright (c) 2020 Mlie"); the original author's description also permits re-uploads. Porting is allowed with the notice kept |
| content | 33 Harmony patch targets, 5 ApparelLayerDefs, 1 JobDef, 18 ammo recipes + ammo ThingDefs, 1 weapon (`Gun_AntiArmor_Rocket`) + its projectile, 1 XML patch file (3 operations) |
| dependants (registry) | `mandrake.rsw.armoury` loadAfter only (About.xml, no def or class reference); `sihv.rombonesport` patches Yayo's ammo recipes inside `PatchOperationFindMod` naming "Yayo's Combat 3". `ModLister.HasActiveModWithName` is an exact `==` (RimSage), and the mod is named "… (Continued)", so **that patch never fires** (MEASURED); `mlie.showmeyourhands` loads a `YayoAdapted` folder when this mod is active; `memegoddess.giddyup` references Yayo's **Animation**, a different mod |

## 2. Feature inventory: what each piece does, live state, effect

Live state = the code default, because there is **no** `Mod_2854006492_YayoCombatMod.xml` in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config` (MEASURED 2026-10-10) and no
`YayoCombat3` node in HugsLib's `ModSettings.xml`. A settings file that is absent means `GetSettings` returns the
field initialisers.

| # | feature | how (source file) | live? | balance effect | feel effect |
|---|---|---|---|---|---|
| F1 | **Ammunition** for every ranged weapon above Neolithic: magazine size from fire rate, 3 ammo tiers × normal/fire/EMP, loadout via drug policy, auto-reload, enemies spawn with 70% | `YayoCombatCore.ApplyDefPatches` adds `CompApparelReloadable`; 22 of the 33 patches serve it | **OFF** (`ammo = false`, log confirms recipes removed) | none now | none now; every ammo hook early-outs on the bool |
| F2 | **Armour model** (`advArmor`): replaces vanilla per-layer armour with a durability model. Armour is near-perfect while healthy and degrades as it takes HP damage. Full block is capped at 90%. Weapons at Medieval tech or below lose 50-65% of their AP against Spacer armour or mechs | prefix on `DamageWorker_AddInjury.ApplyDamageToPart` that **replaces the method** (returns false) + `ArmorUtility.applyArmor` | **ON** | very large; see §5.2 table | armour "pings", then gives out; fights are longer while armour is fresh |
| F3 | **Mechanoid buff**: every PawnKindDef whose `defaultFactionDef` is Mechanoid gets race `ArmorRating_Sharp` ×1.3 and `combatPower` ×1.3 | `ApplyDefPatches`, gated on `advArmor` | **ON** | mechs 30% harder to cut/shoot; raids buy ~23% fewer of them for the same points. 66 kinds on 66 races, none shared, so no compounding (MEASURED, def dump 2026-10-04) | |
| F4 | **Skill-weighted accuracy** (`advShootAcc`, `accEf` 60): per-tile accuracy is blended toward `acc + level/20 × (1 − acc)`. Pawns without skills (mechs, animals) use `baseSkill` 5 | postfix `ShotReport.HitFactorFromShooter` + a **full replacement** of `Verb_LaunchProjectile.TryCastShot` | **ON**, for **all** pawns (`colonistAcc` off) and turrets | skilled shooters gain a lot at range: level 10 hits 0.47→0.59 at 25 tiles, level 20 0.67→0.85 at 40 tiles (§5.4) | sniping becomes a skill fantasy; low-skill pawns unchanged |
| F5 | **Bullet speed** ×3, capped at 2 tiles/tick, for projectiles faster than 23 or with an explosion delay | prefix `Projectile.StartingTicksToImpact` (replaces getter) | **ON** (3, cap 200) | none on hit chance (vanilla resolves hits at launch); explosive projectiles land sooner | bullets almost invisible; assault rifle 0.7 → 2.0 tiles/tick |
| F6 | **Melee tempo**: melee-weapon cooldown × `meleeDelay` 0.7 × a random factor 1 ± 0.65 per attack (floor 0.2 s). The setting text promises damage drops "to maintain balance". **It does not**: the compensating patch `Thing_TakeDamage` returns unless `meleeDelay == 1`, where its multiplier is 1. Dead code (MEASURED; the cooldown half started working with upstream commit `6cc887b`, 2026-05-26) | postfix `Tool.AdjustedCooldown` | **ON** | **equipped melee weapons +70% DPS on average** (E[1/(0.7·U(0.35,1.65))] = 1.70, COMPUTED). Fists, bites and animals unaffected | jittery attack rhythm; `AdjustedCooldown` also feeds the melee-DPS stat readout, so the info card shows a random number |
| F7 | **Hand and foot protection**: anything covering Arms also covers Hands, Legs also Feet. Gloves and boots move to 5 parallel layers (`OnSkin_A`…`Overhead_A`) so they do not collide | `ApplyDefPatches` (`handProtect`) | **ON** | 108 apparel defs gain Hands, 92 gain Feet, 25 gloves/boots re-layered (COMPUTED from the 2026-10-04 dump, which predates `Root_Play.Start`, so it shows the pre-Yayo state) | hands and feet stop being the unarmoured weak point |
| F8 | **AP rewrite** of 3 projectiles (§4) | `1.6/Patches/patch_weapon.xml` | always (XML) | §4 | |
| F9 | **Anti-armour rocket launcher** `Gun_AntiArmor_Rocket`: single use, Bomb 140, AP 0.9, Gunsmithing, machining table, 20 steel | `1.6/Defs/yy_rocket.xml` | weapon **craftable by the player**; enemies never carry it (`enemyRocket` off clears its weaponTags) | a cheap player-only anti-armour item, absent from vanilla | |
| F10 | Miss-shot "physical hit" chance (`missBulletHit` 50%) | inside F4's TryCastShot copy | ON | equals vanilla's hard-coded 0.5, so no change | |
| F11 | `unprotectDmg` 1.1 | shown in settings | **dead** (no reader in the source) | none | |

## 3. Settings: live values, and the ones any decision must name

| setting | code default = **live** | "Reset all" button sets | read by |
|---|---|---|---|
| ammo | **false** | **true** | F1 |
| refillMechAmmo / ammoGen / maxAmmo / enemyAmmo / supplyAmmoDist | true / 1 / 1 / 70 / 4 | same | F1 only |
| meleeDelay / meleeRandom | **0.7 / 1.3** | same | F6 |
| handProtect | **true** | same | F7 (game restart) |
| advArmor / armorEf | **true / 50** | same | F2, F3 |
| unprotectDmg | 1.1 | same | nothing |
| advShootAcc / accEf / missBulletHit | **true / 60 / 50** | same | F4 |
| mechAcc / turretAcc / colonistAcc / baseSkill | true / true / **false** / 5 | true / true / **true** / 5 | F4 |
| bulletSpeed / maxBulletSpeed | **3 / 200** | same | F5 |
| enemyRocket | **false** | **true** | F9 |

🔴 **Trap:** the in-game "Reset all" button does not restore the live state. It turns **ammo ON**,
**enemy rockets ON** and **accuracy colonist-only**. Because no settings file exists, one click in the mod menu
silently changes three systems. Any keep option must write the file (ticket `YAYO_SETTINGS_ENFORCE_PINNED_FILE`).
Our register assumes nothing about settings except that `patch_weapon.xml` applies, and XML patches are not
settings-gated.

## 4. The "normalisation", and what is valuable

**The normalisation.** `1.6/Patches/patch_weapon.xml` is all of Yayo's XML balance, and it is three
`PatchOperationReplace`s of whole `<projectile>` blocks. Vanilla values from RimSage (1.6 Core):

| projectile | vanilla 1.6 | Yayo's | change |
|---|---|---|---|
| `Bullet_AssaultRifle` | dmg 11, no AP declared → derived **0.165**, speed 70 | dmg 11, AP **0.19**, speed 70 | AP +0.025 |
| `Bullet_BoltActionRifle` | dmg 18, stop 1.5, derived AP **0.27**, speed 70 | dmg 18, stop 1.5, AP **0.17** | **AP −0.10 (a nerf)** |
| `Pilum_Thrown` | dmg **25**, stop 2.5, AP **0.10**, speed 26 | dmg **22**, stop 2.5, AP **0.25** | dmg −3, AP +0.15 |

These values are older-era numbers the mod still carries (the same file exists unchanged back to `1.1/`). They
are not a system. They retune three vanilla weapons toward Yayo's taste, and they are the only part of the mod
our weapon register reads.

The owner's phrase could also mean the **tech-level penetration rule** in F2 (Medieval-or-lower weapons lose
50-65% AP against Spacer armour). That reading is INFERRED. Both readings are separable from the rest, so the
options below treat them apart.

**Valuable, in order (judgement):**
1. **F7 hand and foot coverage.** It fixes a real vanilla oddity at near-zero cost and changes nothing else.
   Worth keeping in any outcome.
2. **F2 armour durability.** It is the one idea vanilla lacks. Armour becomes a consumable shield that
   high-AP weapons strip fast (2.8x the vanilla wear rate, §5.2) and low-AP weapons cannot get through while it is
   healthy. That gives tactical texture: focus fire, strip the armour, then finish. **But it fights two of our
   pillars.** (a) "Qualitative danger, not a player-power arms race": with Stronger Quality Scaling, a masterwork
   flak jacket lets **4%** of assault-rifle damage through, against 55% under vanilla (§6.1). (b) Our own armour
   identities (`gen_armour_patch.py`) were built on the vanilla formula (§5.3).
3. **F4 skill accuracy.** It strengthens the "crew composition matters" pillar, because a level-15 shooter is
   clearly better. It can be reproduced with **zero C#** by patching `ShootingAccuracyPawn`'s `postProcessCurve`.
4. **F5 bullet speed.** Taste only. It does not change hit chance.

**Not valuable or harmful:** F6 (a bug that gives melee +70%), F3 (silent mech inflation with a raid-points side
effect), F8 (bolt-action nerf), F9 (a player-craftable anti-armour item nobody chose), F11 (a dead setting).
Also the two method **replacements** (§7), which drop vanilla 1.6 behaviour.

## 5. What our weapon register and our mods depend on

### 5.1 `gen_weapon_register.py` (recomputed, MEASURED from `weapon_register_rows.json` on origin/main)

The register reads **declared** AP from the def dump. Yayo's touches it only through the three projectiles in §4.
Of 764 rows, **10** use them and **9 of those 10 are Cherry-Picker-cut**. One more row exists only because
Yayo's does:

| register row | state | projectile | number now → on vanilla |
|---|---|---|---|
| Gun_AssaultRifle, Gun_AssaultRifle_Unique, AM_M4A, AM_AK101A, MW2_AssaultCarbine, VWE_Gun_MakeshiftRifle | cut | Bullet_AssaultRifle | AP 0.19 → **0.165 (derived)** |
| Gun_BoltActionRifle, Gun_BoltActionRifle_Unique, MW2_HuntingRifle | cut | Bullet_BoltActionRifle | AP 0.17 → **0.27 (derived)** |
| Pila | **live** | Pilum_Thrown | dmg 22 → **25**, AP 0.25 → **0.10**, DPS 3.38 → **3.84** |
| Gun_AntiArmor_Rocket | **live**, craftable | Yayo's own | **row disappears** |
| calibration | — | — | `CALIB_PATCHED = {"ar_ap": 0.19}` becomes a `CALIB_MATCH` entry of **0.165** (the wiki's figure), and the docstring's "one deliberate divergence" is retired |

Nothing else in the register moves. The docstring's "would silently change every ranged AP figure on this sheet"
and card C14's "every weapon re-tuned" overstate it by roughly 750 rows.

### 5.2 The armour model the live game actually runs (COMPUTED, `armor_sim.py`, one layer, normal quality)

| case | vanilla E[dmg] | vanilla P(no dmg) | Yayo E[dmg] armour at 100% HP | Yayo P(no dmg) | Yayo E[dmg] at 50% HP | armour wear per point, vanilla → Yayo |
|---|---|---|---|---|---|---|
| assault rifle (Yayo AP 0.19) vs flak vest 1.00 | 0.39 | 0.40 | 0.06 | 0.81 | 0.33 | 0.25 → 0.30 |
| assault rifle (vanilla AP 0.165) vs flak vest 1.00 | 0.37 | 0.42 | 0.04 | 0.84 | 0.30 | 0.25 → 0.24 |
| assault rifle 0.19 vs flak jacket 0.55 | 0.73 | 0.18 | 0.54 | 0.22 | 0.77 | 0.25 → 0.47 |
| assault rifle 0.19 vs marine armour 1.06 | 0.35 | 0.44 | 0.04 | 0.87 | 0.26 | 0.25 → 0.28 |
| charge rifle 0.35 vs marine armour 1.06 | 0.47 | 0.36 | 0.14 | 0.71 | 0.48 | 0.25 → 0.68 |
| great bow ~0.2 (Neolithic, ×0.35) vs marine 1.06 | 0.35 | 0.43 | 0.02 | 0.90 | 0.14 | 0.25 → 0.20 |
| longsword ~0.3 (Medieval melee, ×0.5) vs marine 1.06 | 0.43 | 0.38 | 0.02 | 0.90 | 0.22 | 0.25 → 0.20 |
| lightsaber AP 0 vs flak vest 1.00 | 0.25 | 0.50 | 0.03 | 0.90 | 0.12 | 0.25 → 0.20 |
| lightsaber AP 0 vs cortosis 2.00 | **0.00** | **1.00** | **0.03** | **0.90** | 0.03 | 0.25 → 0.20 |
| vibro AP 0.90 vs warcasket ~1.06 | 0.88 | 0.08 | 0.91 | 0.02 | 0.94 | 0.25 → 0.70 |
| vibro AP 1.60 vs cortosis 2.00 | 0.70 | 0.20 | 0.72 | 0.16 | 0.81 | 0.25 → 0.70 |
| slug AP 0.85 vs flak vest 1.00 | 0.89 | 0.07 | 0.92 | 0.01 | 0.94 | 0.25 → 0.70 |

Inputs: vanilla `ArmorUtility.ApplyArmor` and Yayo's `applyArmor` transcribed line by line. The ratings are
vanilla 1.6 Core (flak vest 1.00, flak jacket 0.55, marine 1.06; RimSage) and our retune's anchors (cortosis 2.0,
vibro 0.9-1.6, slug 0.85, lightsaber AP 0; `gen_armour_patch.py`). Lightsabers are Ultra tech (MEASURED, all 15
in the dump), so they get no tech penalty. The bow and longsword AP figures are representative, not specific
defs. 200,000 trials per row, seed 1.

The headline: against healthy armour **near or above rating 1.0, Yayo's lets 3-15% of low- and mid-AP damage
through, where vanilla lets 35-47% through**. High-AP weapons (≥0.85) see little difference but shred armour at
2.8x the vanilla wear rate. The AR's 0.19 vs 0.165 is the least of it: 0.06 vs 0.04.

### 5.3 Our Armoury's armour retune assumes the other engine (MEASURED by reading both)

`src/RimStarWars/Armoury/Source/gen_armour_patch.py`'s header says *"THE ENGINE, verified by decompiling
Verse.ArmorUtility"* and builds three consequences on it: "2.0 IS IMMUNITY", "HIGH AP DEFEATS IMMUNITY" (hence
lightsaber AP 0), and "a single advanced layer near 0.8-0.9 meets the ~5-shot contract". Every
`DamageWorker_AddInjury` hit in the live game goes through Yayo's prefix instead, and there:

- **2.0 is not immunity.** Full block is capped at `min(rating − AP, 0.9)`, so a lightsaber still lands 10% of
  swings for 25% damage as blunt against cortosis (≈25 per landing hit of 99).
- **The ~5-shot contract does not hold.** A 0.8-0.9 layer at full HP stops 70-80% of assault-rifle hits outright
  instead of ~40%, until it wears down.
- **The Medieval/Neolithic penalty** applies to any of our blades or primitive weapons with `techLevel` at
  Medieval or below when they hit Spacer armour or a mech.

The retune is consistent with vanilla. **Removing Yayo's `advArmor` makes our own documented design true. Keeping
it obliges a re-derivation** (ticket `ARMOUR_RETUNE_RECONCILE_LIVE_ENGINE`).

### 5.4 Accuracy (COMPUTED, `acc_sim.py`; `ShootingAccuracyPawn` curve from RimSage, healthy sight and manipulation)

| shooter | per-tile vanilla → Yayo | hit factor @12 | @25 | @40 |
|---|---|---|---|---|
| level 0 | 0.890 → 0.890 | 0.25 → 0.25 | 0.05 → 0.05 | 0.01 → 0.01 |
| level 5 | 0.945 → 0.953 | 0.51 → 0.56 | 0.24 → 0.30 | 0.10 → 0.15 |
| level 10 | 0.970 → 0.979 | 0.69 → 0.78 | 0.47 → 0.59 | 0.30 → 0.43 |
| level 15 | 0.982 → 0.990 | 0.80 → 0.89 | 0.63 → 0.78 | 0.48 → 0.67 |
| level 20 | 0.990 → 0.996 | 0.89 → 0.95 | 0.78 → 0.90 | 0.67 → 0.85 |
| mech / animal (vanilla no-skill offset 8; Yayo baseSkill 5) | 0.960 → 0.966 | 0.61 → 0.66 | 0.36 → 0.42 | 0.20 → 0.25 |

(Shooter factor only; weapon accuracy, cover, size and weather multiply on top, identically in both.)

### 5.5 Ion weapons and the rest of our mods

- **Jawa Ion Blaster** (`src/RimStarWars/JawaIonWeapons`): its damage is EMP-based with `harmsHealth` false, and
  EMP has no armour category, so both armour engines pass it through untouched. **No dependency.**
- **KotOR ion weapons** (Armoury `guy762_RangedDamage_ion`, Heat): `DamageWorker_Ionization` derives from
  `DamageWorker_AddInjury` and calls `base.Apply`, so its injury half runs through Yayo's armour prefix like any
  blaster. The ion build-up hediff is applied to `result.parts`, which both engines fill even on a full deflect.
  The ion mechanic therefore behaves the same; only the injury rides F2. **No number in our ion code assumes Yayo.**
- **Armoury's other weapons:** their AP comes from their own defs and `gen_armoury_patch.py`/`gen_armour_patch.py`.
  No Armoury def references a Yayo def, layer or projectile (git grep, MEASURED). The `loadAfter` in Armoury's
  About.xml is the only link.
- **No mod of ours** references `yy_*`, `Gun_AntiArmor_Rocket`, the `_A` layers, or Yayo's classes (MEASURED).

## 6. Interactions

### 6.1 Stronger Quality Scaling (`kas.strongerscaling`, workshop 1206001612)

It is XML only: it replaces the `StatPart_Quality` factors on vanilla StatDefs. Armour rating ×1.90 at
masterwork and ×2.35 at legendary (vanilla ×1.45 / ×1.80); ranged damage ×1.45 / ×1.70 (vanilla ×1.25 / ×1.5);
accuracy ×1.75 / ×2.1 (vanilla ×1.35 / ×1.5); ranged cooldown ×0.79 / ×0.70 (vanilla flat); shields and pack
radius as well. It does **not** touch the AP multiplier. It **compounds with F2**, because Yayo's model rewards
rating above ~0.8 steeply (COMPUTED):

| flak jacket 0.55 vs assault rifle 0.19 | rating | vanilla engine E[dmg] | Yayo engine E[dmg] |
|---|---|---|---|
| normal | 0.55 | 0.73 | 0.54 |
| masterwork, vanilla curve ×1.45 | 0.80 | 0.55 | 0.13 |
| masterwork, SQS ×1.90 | 1.04 | 0.36 | **0.04** |
| legendary, SQS ×2.35 | 1.29 | 0.22 | **0.02** |

So "SQS goes, Yayo stays" (card C14 option A) still leaves masterwork armour 4x stronger than vanilla's curve
would under vanilla rules. The two mods should be ruled on together. The register is unaffected by SQS (it shows
normal quality).

### 6.2 The Combat Extended ban (`design/Jawa/mods/forbidden_mods.md:151-153`)

The ban's three reasons, applied to what Yayo's actually does live:
1. *"Enormous compatibility surface; patches every weapon/pawn"*: **applies partly.** Yayo is 3 XML ops, but it
   replaces two engine methods for every shot and every injury (§7) and rewrites every apparel def's coverage at
   game start. Smaller than CE, but the same kind: it intercepts the pipeline instead of tuning values.
2. *"Over-arms the player as much as the enemy … not a player-power arms race"*: **applies.** F2 + SQS
   (§6.1), the +70% melee bug, the player-craftable rocket and the skill-accuracy gain all favour a curated,
   skilled, well-equipped crew, which is the player.
3. *"Risk on frequently regenerated temporary maps"*: not specific to Yayo's.
The ban's chosen route, *"keep base game vanilla-lethal … tuned vanilla Custom difficulty, NOT a lethality
overhaul"*, is what Yayo's armour model departs from. With ammo off, the CE-like feature (ammo) is the one part
not running.

### 6.3 Other mods

- **CAI-5000** (combat AI) scores targets and cover through `ShotReport`, which carries F4's postfix (INFERRED from
  CAI's design; not traced in its DLL). AI decisions thus see Yayo's accuracy, which is consistent rather than
  conflicting.
- **RunAndGun / GiddyUp** patch the same verb and accuracy pipeline additively (earlier analysis,
  `Transient/GIDDYUP_KEEP_OR_CUT_analysis_2026-09-13.md`). No known conflict.
- **Simple Sidearms** postfixes `PawnGenerator.GenerateGearFor` after Yayo's (Player.log harmony dump). Yayo's
  postfix only acts with ammo on.
- **Melee Animation** is detected, and only changes Yayo's (removed) animation code.

## 7. Harmony hot-path cost

No per-mod TPS has been measured. The audit's `sev_tps 2` has no per-mod measurement behind it; its facts row says
`tps_cost: UNMEASURED`. From the source:

| hook | runs | cost (INFERRED from code) |
|---|---|---|
| `Pawn.Tick` postfix | every pawn, every tick | one static bool check (ammo off), so the Harmony wrapper call is all. Negligible |
| `CompApparelReloadable.CompTick` prefix | each reloadable apparel, every tick | three field reads. Negligible |
| `Projectile.StartingTicksToImpact` prefix (replaces getter) | each projectile, several times per tick and per frame | same arithmetic as vanilla plus one multiply. Negligible |
| `ShotReport.HitFactorFromShooter` postfix | each shot **and every AI hit-chance evaluation** | an extra stat lookup, then a second full call of the method. Roughly doubles that function's cost. The most likely measurable one under CAI-5000 |
| `Verb_LaunchProjectile.TryCastShot` (replaced) | each shot | about vanilla's cost |
| `DamageWorker_AddInjury.ApplyDamageToPart` (replaced) | each damaged body part | **uncached `GetMethod` + `MethodInfo.Invoke` with a boxed argument array per hit**. Slow, but event-driven, not per tick |
| `Tool.AdjustedCooldown` postfix | each melee attack and stat readout | `Rand.Value`. Cheap, but it consumes RNG in UI paths |

TPS verdict: **low** (INFERRED). Nothing heavy runs per tick. Ticket `YAYO_TPS_MEASURE_HOOK_COST` would confirm it
with a profiler on a combat save, if anyone wants a number. TPS is not a reason to keep or cut the mod.

**Fidelity regressions from the two method replacements** (MEASURED against RimSage's 1.6 source; they apply
whenever F2/F4 are on):
- `TryCastShot` copy omits `lastShotTick = TicksGame`. Vanilla 1.6's weapon **recoil animation**
  (`EquipmentUtility.Recoil` keys on `LastShotTick`) never plays for pawns and turrets on Yayo's path.
- It omits `GetForceMissFactorFor`, so the mortar skill stat **`MortarMissRadiusFactor` is ignored**.
- It ignores `verbProps.canGoWild = false` (set by 5 vanilla verbs: Biotech heavy mech gun, Anomaly/Odyssey packs).
- It caps aim-on-target at 99%, so there is always ≥1% wild-miss chance.
- It tests cover via `category == Pawn` instead of `def.CanBenefitFromCover`.
- `ApplyDamageToPart` copy: headshots only count for `DamageDefOf.Bullet` (vanilla: any `isRanged` damage, so
  **blaster headshots never register**). A full block by non-metal armour no longer sets `deflected`, so no
  deflect effect. The non-propagating injury path (Yayo's own `finalizeAndAddInjury`) drops `sourceLabel`,
  `sourceToolLabel`, the mutant-attacker label, the **social-fight no-destroy rule**, and the worker's
  `additionalHediffsThisPart`.

## 8. Options

| | option | what it means | effort | gains | costs and risks |
|---|---|---|---|---|---|
| **A** | **Keep, settings pinned** | write `Mod_2854006492_YayoCombatMod.xml` with every value, recorded in the repo as ours (as C12 did for Bigger Gravships). At minimum: ammo **off**, enemyRocket off, **meleeDelay 1.0 + meleeRandom 0** (kills the +70% bug), the rest as live. Cherry-pick `Gun_AntiArmor_Rocket` unless wanted | **S** | keeps F2/F4/F5/F7; no recalibration | keeps the two method replacements and their regressions; Armoury armour must be re-derived for Yayo's engine (`ARMOUR_RETUNE_RECONCILE_LIVE_ENGINE`, **M**); SQS compounding must be ruled on; abandoned-upstream risk on each RimWorld update |
| **B** | **Keep, engine off** | pin advArmor **off**, advShootAcc **off**, bulletSpeed **1**, meleeDelay 1 / meleeRandom 0, ammo off, enemyRocket off; keep handProtect | **S** | only F7 + the 3 AP patches + the rocket remain; vanilla engine returns, so our armour design becomes true; regressions vanish (both replacements are bypassed when their setting is off) | carries a 33-patch mod for one feature and 3 numbers; the 3 projectile numbers still deviate from vanilla |
| **C** | **Replace with our own small mod** (MIT permits porting) | **C1** hand/foot coverage: a startup pass adding Hands/Feet beside Arms/Legs, gloves/boots moved off the colliding layers (port of 40 lines) — **S**. **C2** skill accuracy: an XML patch of `ShootingAccuracyPawn`'s `postProcessCurve` to the §5.4 right-hand column, no C# — **S**. **C3** bullet speed if wanted: XML projectile speeds or a 10-line prefix — **S**. **C4** armour durability if wanted: a prefix on `ArmorUtility.ApplyArmor` only (not a method replacement), tuned to our ratings, with Mod Settings — **M**, plus a re-derivation of the Armoury contract against it — **M** | S to M+M | exactly the chosen pieces, owned and settings-gated by house rule, no regressions | build and test time; C4 is real design work |
| **D** | **Remove and recalibrate** | drop the mod; register: the §5.1 rows (4 projectile numbers moving 10 rows, 1 row removed, calibration constant). Game: armour back to vanilla, melee weapon DPS back to vanilla (−41% vs now), mechs −30% sharp armour and back to 1.0× combat power, accuracy back to the vanilla column, bullets back to vanilla speed, 108+92 apparel lose hand/foot coverage, 25 gloves/boots back to vanilla layers | **S** (register) | simplest; matches the CE-ban doctrine; our armour design becomes true | loses F7 unless C1 is built; a saved `Gun_AntiArmor_Rocket` item would fail to load (logged, item dropped). Ammo is off and settings-only, so no comp data is saved |

## 9. Recommendation and tickets

**Recommendation: D + C1, with C2 offered.** Remove Yayo's Combat 3, port hand and foot coverage into our own mod,
and offer the skill-accuracy curve as an XML patch if the owner wants skill to bite harder. Leave armour durability
(C4) as an explicit owner question, not a default.
- Most of what Yayo's does live was never chosen: the +70% melee bug, the mech buff, the craftable rocket, the
  regressions in two replaced engine methods, and a "normalisation" that nerfs one rifle.
- What was chosen on paper, ammunition, is off.
- Removal makes our own armour retune correct as written, and costs the register one constant and four numbers.
- If the owner values the armour-durability feel, option C4 delivers it cleanly and on our ratings. Option A
  keeps it at the cost of re-deriving the Armoury contract and living with the regressions.
- Rule on Stronger Quality Scaling in the same sitting (§6.1).

Tickets (names pass `rimflow namecheck`; **not filed**):

| name | what | effort |
|---|---|---|
| `YAYO_COMBAT_DECIDE_KEEP_OR_PORT` | owner card: options A-D above, with C4 (armour durability) and SQS as sub-questions | — |
| `COMBAT_CORE_BUILD_OWN_PORT` | build C1 (+C2/C3/C4 as ruled) in one of our mods, with Mod Settings; MIT notice kept | S (C1-C3), M (C4) |
| `WEAPON_REGISTER_RECONCILE_YAYO_CALIBRATION` | on removal: move `ar_ap` to `CALIB_MATCH` 0.165, regenerate rows, retire the "deliberate divergence" prose | S |
| `ARMOUR_RETUNE_RECONCILE_LIVE_ENGINE` | only if F2 stays: re-derive `gen_armour_patch.py`'s immunity, lightsaber-AP and 5-shot claims against Yayo's formula | M |
| `MELEE_TEMPO_FIX_UNCOMPENSATED_SPEEDUP` | only if Yayo's stays even briefly: pin meleeDelay 1 / meleeRandom 0 now; the +70% is live today | S |
| `YAYO_SETTINGS_ENFORCE_PINNED_FILE` | for A or B: commit the settings file as ours so "Reset all" or a reinstall cannot flip ammo/rockets on | S |
| `MODAUDIT_FACTS_REPAIR_YAYO_FOLDER` | the audit facts row for `mlie.yayoscombat3` (origin/main and the working tree) has `folder` = `…\294100\2009463077`, which is **Harmony's** folder, so its dlls/patch counts describe Harmony; the registry row also says ammo is "resonant" while ammo is off | S |
| `YAYO_TPS_MEASURE_HOOK_COST` | optional: profile `HitFactorFromShooter` and the ApplyDamageToPart reflection on a combat save | S |

Reproduce: the two scripts are kept beside this doc, `design/RimMandrake/mod_deepdive_yayo_armor_sim.py` and
`design/RimMandrake/mod_deepdive_yayo_acc_sim.py` (stdlib, offline, seconds).

## 10. Review disposition

(pending)
