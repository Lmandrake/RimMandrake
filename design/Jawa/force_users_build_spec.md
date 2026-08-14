# Force users — build spec for Jedi and Sith raid leaders

_Research pass, 2026-08-13. **Read-only.** Nothing was installed, deployed or
modified to produce this document._

**Scope tag: `[v2]`.** `infrastructure/state/V1_SCOPE.md:304` names *"the Homestead
Jedi wiring (U4)"* in the list of things v1 explicitly does not contain, and
`infrastructure/state/TODO_v2.md:1081` carries U4 as an unowned v2 row. This spec is
therefore the **plan**, not a licence to build during v1. It exists so that when U4
is picked up, the author starts from ground truth instead of a guess.

**The two reference mods are on disk and MUST STAY UNINSTALLED.** They were read
for design and def structure only:

- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3557220601` — *Star Wars : The Force Standalone*, `lee.theforce.standalone`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3557220783` — *Star Wars : The Force Factions*, `lee.theforce.factions`

Neither appears in `ModsConfig.xml`. Confirmed against
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`
(575 `<li>` entries across `activeMods` + `knownExpansions`).

---

## 🔴 The four findings that change the shape of the job

Read these before the rest; each one invalidates an assumption the ask was built on.

### 1. `lee.theforce.lightsaber` is ACTIVE in `ModsConfig.xml` and NOT ON DISK

`ModsConfig.xml` line 561 (of the extracted `<li>` list) reads
`lee.theforce.lightsaber`. No folder under
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\` owns that
packageId — every hit for that string is inside another mod's
`<modDependencies>` block. The expected folder `…\294100\3466124712` does not
exist. RimWorld silently ignores an unknown packageId in `ModsConfig.xml`, so
this entry is inert.

It is the mod *Star Wars : The Force — Lightsaber* (Workshop 3466124712, author
JodemLee — the same author as the two reference mods), declared as a **hard
`v1.6` dependency** by *Star Wars KotOR Weapons and Armor*
(`…\294100\2938932438\About\About.xml`).

### 2. Consequence: **the active stack has no lightsaber weapon at all**

*Star Wars KotOR Weapons and Armor* (`guy762.KotORWeapons`, active, position 564)
shipped lightsabers in 1.5 and **delegated them entirely to
`lee.theforce.lightsaber` in 1.6**. Read from
`…\294100\2938932438\LoadFolders.xml`:

```xml
<v1.6>
  ...
  <li IfModActive="lee.theforce.lightsaber">1.6/AdditionalMods/_TheForceLightsabers</li>
  <!-- <li IfModNotActive="lee.theforce.lightsaber">1.6/AdditionalMods/_NO_ForceLightsabers</li> -->
</v1.6>
```

The fallback folder is **commented out** in `v1.6`. So neither branch loads.
`…\2938932438\1.6\Defs\ThingDefs_Weapons\` contains 25 files — vibroblades,
vibroswords, blasters, disruptors — and **zero lightsaber ThingDefs**; the only
saber-named defs in the always-loaded tree are `NamerWeaponLightsaber` and the
colour crystals (`guy762_crystalitem_blue`, `…_red`, `…_purple`, and 12 more, in
`…\1.6\Defs\ThingDefs_Mineables\ThingDefs_UpgradeItems_Lightsaber.xml`).

*Star Wars KotOR Resources and Materials* (`guy762.MM.KotORCore`, active) is the
same story: it ships `guy762_saberpart_lens`, `guy762_saberpart_emitter`,
`guy762_saberpart_pcell` (`…\294100\3254370945\1.6\Defs\ThingDefs_Items\ThingDefs_LightsaberParts.xml`),
a `guy762_lightsaber` ThingCategoryDef, `Sounds_Lightsaber.xml`, and the tool
capacities `guy762_ToolCapacity_SaberSlash` / `guy762_ToolCapacity_SaberStab` —
**a complete lightsaber ecosystem with no lightsaber in it.**

*[JDS] StarWars - Armory* (`…\294100\3511954303`) has no saber defs of any kind:
`grep -i saber` over its whole tree returns nothing.

> **⚠️ This is a live defect, not just a spec input.** An active mod
> (`guy762.KotORWeapons`) declares a `v1.6` `modDependency` that is not
> installed, and the content it gates is silently absent. Whether the mod is
> otherwise safe at 1.6 has **not** been established here. Filing this is
> outside the scope of this research pass — see §6.

### 3. Vanilla Psycasts Expanded is **NOT ACTIVE**, and the whole Force design assumes it

`design/Jawa/mods/required_mods.md:620` records the finalized ruling:

> **⭐ THE FORCE SYSTEM — FINALIZED (user decision 2026-08-06): VPE ONLY, no dedicated Force mod.**

and `:623` calls VPE *"the sole Force substrate"*, specifically because **VPE
ships the enemy-cast AI** that makes NPC casters actually cast.

`VanillaExpanded.VPsycastsE` **does not appear in `ModsConfig.xml`.** The only
match in the whole workshop tree for a VPE-ish packageId is folder `3462136587`,
whose `About.xml` reads `<name>VPE - Anima</name>` — an *addon*, and also not
active. **VPE itself is not installed.**

So every VPE defName in the shopping list at `required_mods.md:638-642`
(`VPE_Bolt`, `VPE_ChainBolt`, `VPE_Thunderbolt`, `VPE_ChaosSkip`,
`VPE_Overshield`, `VPE_PowerLeap`, `VPE_BladeFocus`, …) refers to defs that are
**not in this game**. Any spec that spends them is spending money we do not have.

### 4. Vanilla cannot make an NPC cast a psycast. Verified from shipped files.

- `grep -c aiCanUse` over `…\RimWorld\Data\Royalty\Defs\AbilityDefs\Abilities.xml`
  → **0**. Not one Royalty psycast is flagged AI-usable.
- `JobGiver_AICastAbility` appears in exactly one shipped XML file,
  `…\Data\Biotech\Defs\ThinkTreeDefs\SubTrees_Mech.xml` — mechanoids only.
- `…\Data\Core\Defs\ThinkTreeDefs\SubTrees_Ability.xml` wires **two** abilities
  for non-colonists, both Biotech gene abilities: `AnimalWarcall`
  (`JobGiver_AICastAnimalWarcall`) and `Longjump` (`JobGiver_AIJumpEscapeEnemies`).
- `JobGiver_AIAbilityFight` exists in the assembly but is used only by Anomaly
  entity duties and think trees (`…\Data\Anomaly\Defs\DutyDefs\Duties_Misc.xml`,
  `…\ThinkTreeDefs\Devourer.xml`, `…\Gorehulk.xml`).

**Therefore: giving a raider pawnkind Royalty psycasts produces a pawn that
never uses them.** This is the single hardest constraint on the whole feature and
it is what the reference mods' 516 KB Harmony assembly exists to solve.

---

## 1. What already exists in our active stack

Method: `ModsConfig.xml` was parsed for active packageIds; each was resolved to a
folder by reading the **first** `<packageId>` in that folder's `About/About.xml`
(later ones are `modDependencies` and were a source of false matches on the first
pass). Every def below was read on disk.

### 1a. Force-sensitive xenotypes — **we already have five, and they are good**

| defName | label | source mod (active) | file |
|---|---|---|---|
| `guy762_xenotype_miraluka` | Miraluka | Star Wars Xenotypes | `…\294100\2915192253\1.6\Defs\GeneDefs\XenotypeDefs.xml:941` |
| `guy762_xenotype_sith` | Sith Pureblood | Star Wars Xenotypes | `…\2915192253\1.6\Defs\GeneDefs\XenotypeDefs.xml:1271` |
| `guy762_xenotype_yoder` | (Yoda's species) | Star Wars Xenotypes | `…\2915192253\1.6\Defs\GeneDefs\XenotypeDefs.xml:1650` |
| `BTD_SithK` | Sith Kissai (Pureblood) | [BTD] Xenotype REMIX: Star Wars | `…\294100\3458153185\1.6\Defs\Genes\BTD_Xenotypes.xml:1805` |
| `BTD_SithM` | Sith Massassi (Pureblood) | [BTD] Xenotype REMIX: Star Wars | `…\3458153185\1.6\Defs\Genes\BTD_Xenotypes.xml:1838` |
| `BTD_SithZ` | Sith Zugurak (Pureblood) | [BTD] Xenotype REMIX: Star Wars | `…\3458153185\1.6\Defs\Genes\BTD_Xenotypes.xml:1873` |

`design/Jawa/worldbuilding/faction_stage3_buildable_spec.md:56` already flags the
BTD trio as *"a gift the roster has not spent"* — Kissai as ISB inquisitors,
Massassi as shock troops, Zugurak as rare elites.

The `guy762_*` three are the more mechanically interesting, because of the next
row.

### 1b. ⭐ `guy762_statgene_force` — we already run a Force-sensitivity gene that grants psylink

`…\294100\2915192253\1.6\Defs\GeneDefs\GeneDefs_AbilitiesStats.xml:126`

```xml
<GeneDef>
  <defName>guy762_statgene_force</defName>
  <label>natural force-user</label>
  <description>Carriers of this gene have evolved a natural ability to use the force.</description>
  <biostatCpx>10</biostatCpx>
  <biostatArc>3</biostatArc>
  <selectionWeight>0</selectionWeight>
  <modExtensions>   <!-- PATCHES FOR VPE and PotF REPLACE THIS ENTIRE NODE -->
    <li MayRequire="Ludeon.RimWorld.Royalty" Class="BigAndSmall.PawnExtension">
      <applyPartHediff>
        <li>
          <hediff>PsychicAmplifier</hediff>
          <bodyparts><li>Brain</li></bodyparts>
        </li>
      </applyPartHediff>
    </li>
  </modExtensions>
</GeneDef>
```

- `PsychicAmplifier` is the vanilla psylink hediff —
  `…\RimWorld\Data\Core\Defs\HediffDefs\Hediffs_Psycasts.xml:58`,
  `<hediffClass>Hediff_Psylink</hediffClass>`, `maxSeverity 6`, severity = psylink level.
- `Ludeon.RimWorld.Royalty` is **active**. `redmattis.bigsmall.core` is **active**,
  so the `BigAndSmall.PawnExtension` class resolves.
- The three xenotypes that carry it, gated
  `MayRequireAnyOf="Ludeon.RimWorld.Royalty,lee.theforce.standalone"`, are
  `guy762_xenotype_miraluka`, `guy762_xenotype_sith`, `guy762_xenotype_yoder`.
- `selectionWeight 0` means it never rolls into a random xenogerm — it only
  arrives via a xenotype that lists it.

**So a `guy762_xenotype_sith` pawn already spawns with psylink 1 today.** That is
the substrate. What it does *not* come with is anything to cast (see §4 finding 4).

### 1c. Force abilities that already exist and are AI-flagged

Two AbilityDefs in the **active** *Star Wars Xenotypes*, in the
`1.6/AdditionalMods/Royalty` folder — which loads, because
`…\2915192253\LoadFolders.xml` has `<li IfModActive="Ludeon.RimWorld.Royalty">1.6/AdditionalMods/Royalty</li>`:

| defName | file | notes |
|---|---|---|
| `guy762_GeneAbility_forcesight` | `…\2915192253\1.6\AdditionalMods\Royalty\Defs\AbilityDefs_forcesight.xml:86` | `abilityClass Psycast`, `category Psychic`, `level 1`, `aiCanUse true`, `hostile false`, self-target, grants `guy762_hediff_blindsight` for 500 ticks. Granted by gene `guy762_AbilityGene_forcesight` ("eyeless seer"), whose `<prerequisite>` is `guy762_statgene_force`. |
| `guy762_GeneAbility_defelcloak` | `…\2915192253\1.6\AdditionalMods\Royalty\Defs\AbilityDefs_defelcloaking.xml:76` | paired with `guy762_StealthDeactivate_defel`; `aiCanUse true` |
| `guy762_GeneAbility_jump` | `…\2915192253\1.6\Defs\GeneDefs\GeneDefs_AbilitiesStats.xml:226` | `aiCanUse true` — the closest thing we have to a Force leap |

These are **non-combat / utility** abilities. There is no Force lightning, no
telekinetic throw, no choke anywhere in the active stack. Confirmed by
`grep -c aiCanUse` per mod: Outer Rim Core 0, Galactic Empire 0, BTD REMIX 0, JDS
Armory 0; the only hits are the KotOR/SWX gene abilities above.

### 1d. The psycast framework we actually run

| thing | status |
|---|---|
| `Ludeon.RimWorld.Royalty` | **ACTIVE** — psylink, psyfocus, `PsychicAmplifier`, all Royalty AbilityDefs |
| `VanillaExpanded.VPsycastsE` | **NOT ACTIVE, NOT INSTALLED** — see finding 3 |
| `OskarPotocki.VanillaFactionsExpanded.Core` (VEF) | **ACTIVE** (position 364 / 550) |
| `EBSG.Framework` | **ACTIVE** (position 21). Folder `…\294100\3112549163`. Ships a large ability-comp library (`CompProperties_AbilityAlterGenes`, `…AlterXenotype`, `…ChangeFaction`, `…CreateItems`, `…ToggleHediff`, `CompAbilityLimitedCharges`, `JobDriver_ReloadAbility`, …) plus gene `abilities` / `abilitiesAtSeverities`. **This is our best XML-only ability authoring surface.** |
| `neronix17.toolbox` (Tabula Rasa) | **ACTIVE**. Ships `TabulaRasa.DefModExt_PawnKindExtended` (fields `additionalHediffs` with `hediff` + `severityRange`, `randomAdditionalHediff`, `clearChronicIllness`, `clearAddictions`) and `TabulaRasa.PawnGroupMaker_Temperature`. Verified by `strings …\294100\1660622094\1.6\Assemblies\TabulaRasa.dll`. |
| `bs.xenotypespawncontrol` | **ACTIVE**. Per-pawnkind and per-faction xenotype forcing, but through the **in-game settings window**, not through authorable XML (its only XML surface is `XenotypeSpawnControl.Extension` with `randomGenesChance`/`hybridChance`). Use vanilla `<xenotypeSet>` for anything you want in a file. |
| `thereallemon.factioncontrol`, `boots.sensiblefactions` | **ACTIVE** — the faction-restriction levers `required_mods.md:629` names |

### 1e. Energy-melee weapons we DO have (the lightsaber substitutes)

Since there is no lightsaber (finding 2), these are the honest candidates, all
from Royalty, all active:

| defName | label | weaponTag | file |
|---|---|---|---|
| `MeleeWeapon_PlasmaSword` | plasmasword | `UltratechMelee` | `…\RimWorld\Data\Royalty\Defs\ThingDefs_Misc\Weapons\MeleeUltratech.xml:131` |
| `MeleeWeapon_PlasmaSwordBladelink` | persona plasmasword | `Bladelink` | `…\Weapons\MeleeBladelink.xml:211` |
| `MeleeWeapon_MonoSword` | monosword | `UltratechMelee` | `…\Weapons\MeleeUltratech.xml:42` |
| `MeleeWeapon_MonoSwordBladelink` | persona monosword | `Bladelink` | `…\Weapons\MeleeBladelink.xml:110` |
| `MeleeWeapon_Zeushammer` / `MeleeWeapon_ZeusHammerBladelink` | zeushammer | `UltratechMelee` / `Bladelink` | same two files |

`MeleeWeapon_PlasmaSwordBladelink` is the closest analogue in the game: a
plasma-sheathed blade with an onboard persona that bonds to one wielder and
refuses anyone else. `MarketValue 3000`, `Mass 2`, `smeltable false`, edge and
point at power 23 / cooldown 2 with `Flame 10 @ 0.7` extra damage. That is a
lightsaber in everything but the texture and the name.

`faction_roster_v2.md:229` already anticipates this: *"monosword, persona
monosword, or custom lightsaber"*.

Also in the active stack, from *KotOR Weapons and Armor*, if a non-persona
"vibro" look is preferred: `guy762_vaxe_hutt`, `guy762_vaxe`, `guy762_vglaive`,
`guy762_gamorreanaxe` (already used by `Jawa_Gamorrean_Enforcer`) and the
vibroblade/vibrosword families in `…\2938932438\1.6\Defs\ThingDefs_Weapons\`.

### 1f. The two faction defNames, verified on disk

**Galactic Empire — `OuterRim_GalacticEmpire`.** Confirmed.
`…\294100\2919248699\1.6\Defs\FactionDefs\FactionDefs.xml`. `ParentName="FactionBase"`.
`basicMemberKind OuterRim_ImpStormtrooper` · `leaderTitle Grand Admiral` (already
patched to `Sector Director` by us — see below) · `fixedLeaderKinds` =
`OuterRim_ImpStormCommander` · `leaderForceGenerateNewPawn true` ·
`permanentEnemy false` but `permanentEnemyToEveryoneExceptPlayer true` ·
`settlementGenerationWeight 0.3` · `earliestRaidDays 35` · `techLevel Ultra` ·
`xenotypeSet` = `Baseliner 10.0` only ·
`maxPawnCostPerTotalPointsCurve` = `(0,35) (70,50) (700,100) (1300,150) (100000,10000)`
(the vanilla pirate curve).

⭐ **The Empire already has a Sith slot wired, waiting for a mod we do not have.**
Seven of its twelve `pawnGroupMakers` are
`<li Class="TabulaRasa.PawnGroupMaker_Temperature">`, and five of them plus one
Settlement group carry:

```xml
<OuterRim_SithInquisitor MayRequire="Neronix17.OuterRim.HokeyReligions">0.01</OuterRim_SithInquisitor>
```

with the weight raised to **`0.1` in the "Hot Weather Squad"** (`minTemperature 30`
— i.e. **the group that fires on a desert world**) and `0.05` in the first
Settlement group. `Neronix17.OuterRim.HokeyReligions` is **not installed and not
active**; those options are stripped at load, so the slot is empty. The design
intent, the weight, and the desert-weighting are all already there.

The desert combat group in full (`…\FactionDefs.xml:156-169`):
`OuterRim_SithInquisitor 0.1` · `OuterRim_ImperialOfficer 1` ·
`OuterRim_ImpStormtrooper_Officer 5` · `OuterRim_ImpStormArty 3` ·
`OuterRim_ImpStormIncinerator 6` · `OuterRim_ImpStormScout 10` ·
`OuterRim_ImpStormtrooper_Desert 20`.

Empire pawnkinds and their weapon tags (all `Inherit="false"`), from
`…\2919248699\1.6\Defs\PawnKindDefs\`:
`OuterRim_ImpStormtrooper` cp 100 `ORImperialStandard` ·
`OuterRim_ImpStormtrooper_Desert` cp 100 `ORImperialStandard` ·
`OuterRim_ImpStormScout` cp 120 `ORImperialLight, ORImperialSniper` ·
`OuterRim_ImperialOfficer` cp 175 `ORImperialLight` ·
`OuterRim_ImpISBAgent` cp 200 `ORImperialLight, ORImperialStandard, ORImperialSniper, ORRifleRare` ·
`OuterRim_ImpDeathTrooper` cp 200 `ORImperialDeathTrooper` ·
`OuterRim_ImpStormCommander` cp 200 `ORImperialAny` (`factionLeader true`) ·
`OuterRim_ImperialArmyCommander` cp 200 `ORImperialAny` (`factionLeader true`).
Abstract base: `OuterRim_EMPStormBase`.

Our existing patch on this faction:
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Patches\ImperialDesertDirectorate.xml`
replaces `label`, `fixedName`, `leaderTitle` (→ `Sector Director`), `pawnsPlural`,
`description` and `colorSpectrum`. It is deliberately label-level only.

**Moisture farmers — `OuterRim_MoistureFarmers`.** Confirmed. Ships in **Outer Rim
– Core** (active), not in any Jawa mod:
`…\294100\2919227155\1.6\Defs\FactionDefs\Faction_MoistureFarmers.xml`.
`ParentName="OuterRimDiverseFactionBase"` · label `moisture farmers` ·
`categoryTag Outlander` · `leaderTitle councilman` · `techLevel Ultra` ·
`settlementGenerationWeight 1` (the most numerous faction) · `canSiege true` ·
`allowedCultures Rustican` · `raidLootMaker OutlanderRaidLootMaker` ·
`maxPawnCostPerTotalPointsCurve` = `(0,200) (70,500) (700,1800) (2000,5000) (100000,10000)`
— **far more generous than the Empire's**, so a high-`combatPower` kind is
reachable here much earlier.

Its Combat group (plain vanilla `PawnGroupMaker`, no Tabula Rasa class):
`OuterRim_TownSettler 5` · `OuterRim_TownGuard 10` ·
`OuterRim_Grenadier_Destructive 10` · `OuterRim_Mercenary_Slasher 10` ·
`OuterRim_Mercenary_Gunner 7` · `OuterRim_Mercenary_Elite 10` ·
`OuterRim_TownCouncilman 10`. Weight sum **62**.

Its own pawnkinds (`…\2919227155\1.6\Defs\PawnKindDefs\PawnKinds_MoistureFarmers.xml`):
`OuterRim_TownSettler` cp 145 · `OuterRim_TownGuard` cp 160 ·
`OuterRim_TownTrader` cp 145 · `OuterRim_TownCouncilman` cp 140
(`factionLeader true`).

The campaign dossier for this faction is the **Homestead Defense League**
(`design/Jawa/worldbuilding/faction_roster_v2.md` §3;
`faction_stage3_buildable_spec.md:276` — *"PATCH `OuterRim_MoistureFarmers`"*).

### 1e-bis. More of the same, found on a second sweep

**More Force-flavoured xenotypes, all active.** `PureBlood` ("Pureblood",
`…\294100\3485069256\Defs\XenoType.xml`, mod *Rimwars:Pureblood Xenotype*,
`Sov.Sith`) — cosmetics plus `PsychicAbility_Extreme`, **no** `guy762_statgene_force`,
so no psylink. `BTD_Miraluka` (`…\3458153185\1.6\Defs\Genes\BTD_Xenotypes.xml:1279`,
carries `OuterRim_ForceSight`), `OuterRim_Miraluka` and `OuterRim_Sith`
(`…\294100\2980427615\1.6\Defs\GeneDefs\Xenotype_Miraluka.xml` / `Xenotype_Sith.xml`),
`guy762_xenotype_massassi`, `guy762_xenotype_zabrakDathomiri`.

⚠️ `BTD_SithM` and `BTD_SithZ` carry **no psychic genes at all** — Massassi is a
pure melee bruiser, Zugurak a crafter caste. Only `BTD_SithK` has
`PsychicAbility_Enhanced` + `Turn_Gene_LatentPsychic`, and none of the three has
`guy762_statgene_force`. Use them for flavour, not for psylink.

⚠️ `OuterRim_Sith`'s only Force gene is `OuterRim_ForceAdept`, gated
`MayRequire="Neronix17.OuterRim.HokeyReligions"` — stripped in our stack. Outer
Rim's own Sith therefore have **zero** Force content today.

⚠️ **Duplicate defNames across two active mods:** `Sov.Sith` and
`guy762.StarWarsXenotypes` both ship `Head_Bone`, `GS_Eyes_Yellow`,
`GS_Eyes_Orange`, `Male_HeavyBoneNormal`, `Female_HeavyBoneNormal` and
`NamerPersonPureblood`. Last-loaded wins. Not caused by anything here, but it is
the tree this build sits in.

**Only one xenotype in the whole active stack has a
`factionlessGenerationWeight`:** `BTD_Yoder` at `0.001`. Every Sith and Miraluka
xenotype has none, so **none of them spawns naturally anywhere today.** BTD's own
faction injections for `BTD_SithK/M/Z` are **commented out**
(`…\3458153185\1.6\Patches\FactionPatches.xml:60-62`). This is exactly why the
pawnkind in §3.4 is the necessary piece.

**Two innate-psylink genes exist and are active** — an alternative to §3.3:
`AG_InnatePsylink` (Alpha Genes, `…\294100\2891845502\1.6\Mods\Royalty\Defs\GeneDefs\GeneDefs_Royalty.xml:31`)
and `VRE_InnatePsylink` (VRE-Archon, `…\294100\3067715093\1.6\Defs\GeneDefs\GeneDefs_Archite.xml:20`).
Both Royalty-gated, both load. Adding one to a forked xenotype is cleaner than a
Tabula Rasa hediff injection if a fork is being authored anyway.

⭐ **Five real Force AbilityDefs already exist in the stack — attached to
animals.** *Star Wars Animal Collection* (`mlie.starwarsanimalcollection`,
ACTIVE), all in
`…\294100\3497316713\1.6\Defs\AbilityDefs\SW_Abilities.xml`:
`SW_ForcePush` (:261, launches `SW_ForcePushprojectile`, Blunt 20, AP 1),
`SW_ForceScream` (:625, `Terror` mental state, radius 19.9),
`SW_ForceInvisibility` (:469, grants vanilla `PsychicInvisibility` 20–30 s),
`SW_ForceChaosSkip` (:740, `CompAbilityEffect_Teleport`, Royalty-gated),
`SW_ForceFocus` (:797, + a HediffDef of the same name: +0.25 Consciousness /
Sight / Hearing / Manipulation for 3 h). Each is gated behind a `TrainableDef` of
the same name; there is **no pawn or gene hookup**.

That is a genuine Force Push and Force Scream sitting in our load order. Whether
they can be granted to a humanlike pawnkind via `<abilities>` and whether the
enemy AI would cast them **was not established** — see §7. If they can, option C
in §3.0 gets dramatically cheaper.

**A third framework worth knowing about:** VEF is active and its `VEF.dll`
exports the `VEF.Abilities` AbilityDef system (1.6 merged the old
`VFECore.Abilities` into it). ~320 AbilityDef nodes across the active stack
already use it (`AbilityExtension_Projectile`, `AbilityExtension_Hediff`,
`Ability_ShootProjectile`, `AbilityPawnFlyer`, `PawnKindAbilityExtension`, …).
**This is the best available surface for authoring Force powers that do not need
psylink** — and `PawnKindAbilityExtension` is specifically a pawnkind→ability
hook. Not used by this spec's option A, but it is where option C should start
before anyone reaches for VPE or Harmony.

### 1e-ter. The 39 orphaned KotOR lightsabers — where they really are

> ⚠️ **Correction.** An earlier revision of this document said the KotOR
> lightsaber weapon ThingDefs sit in
> `…\2938932438\1.6\AdditionalMods\_TheForceLightsabers\Defs\`. **That was wrong.**
> That folder holds 47 defs and **every one is a crystal or hilt *part*** —
> `guy762_SWForceLightsabersPartCategory_colorcrystal`,
> `guy762_SWForceLightsabers_CrystalPart_red` … `_white`, plus focusing and power
> crystals — with no weapon among them. Verified by
> `grep -h "<defName>" …\_TheForceLightsabers\Defs\*.xml`.

**The weapons are in the `1.5` tree**, at
`…\294100\2938932438\1.5\Defs\ThingDefs_Weapons\`, and
`…\2938932438\LoadFolders.xml` `<v1.6>` loads only `/`, `1.6` and
`1.6/AdditionalMods/*`. It never loads `1.5`. So there are **two independent
reasons** no lightsaber reaches the game:

1. the 1.5 weapon defs are in a folder 1.6 does not read, and
2. the 1.6 branch's saber content is gated on the missing
   `lee.theforce.lightsaber`.

Fixing only one of them fixes nothing.

**The 39 defNames** (abstract bases in `kotorlightsabers_base.xml`:
`guy762_kotorlightsaber`, `guy762_kotorshortsaber`, `guy762_kotorcurvesaber`,
`guy762_kotorcrosssaber`, `guy762_kotordualsaber`) and the concrete variants —
`SWSaber_KotOR_lightsaber_red|orange|yellow|green|blue|purple|white`,
`SWSaber_KotOR_darksaber`, the `shortsaber_*`, `curvesaber_*` (incl. `pink`),
`crosssaber_*` and `dualsaber_*` colour families, plus named blades
`SWSaber_KotOR_revansaber`, `_malaksaber`, `_nihilussaber`, `_sionsaber`,
`_exilesaber`, `_exarsaber`, `_naddsaber`.

Shared properties of `guy762_kotorlightsaber` (`ParentName="KotORMeleeNoQualityModMake_OneHand"`):
`MarketValue 9000`, `Mass 5`, `WorkToMake 6000`; `equippedStatOffsets`
`PsychicSensitivity 0.1` and `MeditationFocusGain 0.25`; tools hilt Blunt 10,
tip `guy762_ToolCapacity_SaberStab` 24 / cd 2, edge
`guy762_ToolCapacity_SaberSlash` 24 / cd 2; comps
`CompExtraSounds.CompProperties_ExtraSounds`, **`CompDeflector.CompProperties_Deflector`**
and `ModularWeapons.CompProperties_ModularParts`; `researchPrerequisite`
`guy762_ResearchKotOR_lightsabers` (still defined, in
`…\294100\3254370945\1.6\Defs\researchDefs\Czerkatech_Techprint_Research.xml`);
`costList` = the three `guy762_saberpart_*` items + Steel 15 + one colour crystal.

🔴 **If these are ever revived, read `required_mods.md` first.** That file already
audited this exact weapon and rules it acquisition-gated: the balance lever is
not the ~26 edge damage but **`baseDeflectChance` + `deflectRatePerSkillPoint`**
on `CompDeflector`, which makes a high-Melee wielder close to bulletproof against
ranged fire. Loot-only, craft-recipe disabled. Handing one to a raid leader is
also handing it to the player the moment they win the fight.

**Their `weaponTags`** — the pawnkind-selection surface, and the reason the
reference mod's pawnkinds resolve to nothing here. Base tag `KotORLightsaber`;
each concrete variant overrides with `Inherit="False"`, giving families
`KotORLightsaber_anysingle`, `KotORMelee_legendary`; Jedi `OR_jedisaber`,
`OR_jedisaber_padawan`, `OR_jediguardian`, `OR_jedisentinel`, `OR_jediconsular`;
Sith `SE_sithsaber`, `SE_sithsaber_apprentice`, `SE_sithsaber_assassin`,
`SE_sithsaber_sorcerer`, `SE_sithinquisitor`, `SE_sithwarrior`,
`SE_sithmarauder`; plus `SaV_darkjedisaber`, `MNC_mandalore` and the named-hero
tags. **Under 1.6 no loaded ThingDef carries any of these**, so a pawnkind
pointing at `SE_sithsaber` spawns its Sith **barehanded**. That is precisely the
trap §3.2 avoids by using the vanilla `Bladelink` tag.

**Other energy melee in the active stack**, for completeness: VFE Pirates ships a
`warcasket plasma sword` (`…\294100\2723801948\1.6\Defs\ThingDefs_Misc\Weapons\MeleeWarcasket.xml`,
tags `WarcasketMelee` / `WarcasketVeteran`) — **warcasket-only, a normal pawn
cannot equip it**. The Yautja mod's `ABYautja_Gun_PlasmaSpinningBlade` is a
*ranged* weapon despite the name.

⭐ **The cheapest possible lightsaber, if the owner will take one subscription:**
`VWEL_LaserSword` ("laser sword") in *Vanilla Weapons Expanded - Laser*
(`VanillaExpanded.VWEL`, folder 1989352844) — **NOT ACTIVE**; the active list has
`vanillaexpanded.vwe` and `.vwems` only. `techLevel Ultra`, weaponTags
`UltratechMelee` + `LaserGun`, point and blade Cut **31 @ AP 1.0**, cd 2.6,
`MarketValue 2000`, craftable from Steel 30 / Plasteel 100 / ComponentSpacer 10.
It already carries `UltratechMelee`, **so §3.2's pawnkind needs no change at all
if it is enabled** — the Sith would simply start rolling laser swords alongside
plasmaswords. No `CompDeflector`, so it does not reopen the near-invulnerability
problem the KotOR sabers have. This is the single highest-value, lowest-risk
option in the document, and it is a roster decision for the owner, not mine.

### 1g. What does NOT exist in the active stack — stated plainly

- **No lightsaber weapon ThingDef.** Anywhere. (§ finding 2.)
- **No Jedi, Sith or force-user PawnKindDef.** `OuterRim_SithInquisitor` is
  referenced by the Empire but defined only in the uninstalled Hokey Religions
  module — I could not read that mod because it is not on disk, so nothing about
  its contents is asserted here.
- **No Force AbilityDef with combat effect.** Only the three utility gene
  abilities in §1c.
- **No Force HediffDef or TraitDef.** No `Force_*` def of any kind loads.
- **No psycast path / psycaster-progression framework.** Royalty's bare psylink
  only.
- **No NPC psycast AI.** (§ finding 4.)
- **No FactionDef in any Jawa mod.** `grep -rln "<FactionDef"` over
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\` returns zero.
- **No TraitDef for Force sensitivity, and no "midichlorian" anything.** Zero
  hits stack-wide.
- **`guy762.KotORFactions` is NOT active** — so no Jedi Order / Sith Empire
  FactionDef, no Jedi/Sith/Inquisitor PawnKindDef, and
  `…\294100\3254370945\1.6\AdditionalMods\_FactionsBase\` (including
  `Culture_Sith.xml`, `guy762_culture_sith`) does not load. The
  `guy762_NamerPawnKind_MaleInquisitor` / `_FemaleInquisitor` RulePacks that
  *are* loaded name pawnkinds that do not exist.
- **Every Sith/Miraluka "pawnkind" in the stack is a debug stub.**
  `OuterRim_Sith`, `OuterRim_SithTribal`, `OuterRim_Miraluka`,
  `OuterRim_ForceGremlin` are all `ParentName="OuterRimTestColonyPawnKind"` /
  `…TestTribalPawnKind` with no faction, no gear and no combatPower — dev-spawn
  enablers only. Our own
  `…\Mods\Jawa_Patches\Defs\PawnKindDefs\AlienSpawnEnablers.xml:142,148`
  (`Jawa_Spawn_SithK`, `Jawa_Spawn_SithM`) are the same pattern.
- **Dead references left by the missing Hokey Religions module:** gene
  `OuterRim_ForceAdept`; apparel tag `ORForceUser`, dangling in
  `…\294100\2919227155\1.6\Defs\ThingDefs_Apparel\Cloak.xml:24,76`; and orphan
  keyed strings `OuterRim.ForceUser_0Level`…`_7Level` ("Force Sensitive / Force
  User / Force Adept / Force Knight / Force Master") in
  `…\2919227155\Languages\English\Keyed\OuterRimCore.xml:20-24`. Outer Rim was
  built expecting a Force module we do not have.
- **The KotOR lightsabers exist as files and cannot load — for two independent
  reasons.** See §1e-ter, which corrects an earlier version of this line.
- **`SWPotF_hediff_YsalamirForceDampen`**
  (`…\294100\3254370945\1.6\AdditionalMods\VEF\Defs\Ysalamiri.xml:39`,
  `PsychicSensitivity ×0`) loads, but the
  `VEF.AnimalBehaviours.CompProperties_HediffEffecter` that would apply it from
  the ysalamir is commented out — *"MOVED TO OPTIONAL PATCHES"*. The
  Force-dampening animal currently dampens nothing.

---

## 2. What the reference mods actually do

Study notes. **Nothing below is a recommendation** unless §5 says so.

### 2a. *The Force Standalone* (`lee.theforce.standalone`, folder 3557220601)

**Force-user definition: a ThingComp plus a TraitDef, both driven from C#.**

- `TraitDef Force_NeutralSensitivity` —
  `…\3557220601\1.6\Defs\TraitDefs\Traits_Spectrum.xml`. Degrees −1/0/1/2
  ("Dull / Force sensitivity / Medium / Major Force Sensitivity"), granting
  `PsychicSensitivity` +0.2/+0.4/+0.8/+0.8, `conflictingTraits` with vanilla
  `PsychicSensitivity`, carrying `TheForce_Standalone.ModExtension_ForceSensitivity`.
  Companion traits `Force_LightAffinity` and `Force_DarkAffinity`, commonality
  0.002 each.
- The actual capability is `TheForce_Standalone.CompProperties_ForceUser` /
  `CompClass_ForceUser`, **attached in code**, not in XML. The DLL contains
  `InitializeForceUserComp`, `NonForceUserCache`, `get_IsValidForceUser`,
  `TryGiveInitialForceSensitivity`, `ForceSensitivityUtils`, and a `Doorstopper`.
- Discovery: `RecipeDef Force_PerformMidichlorianTest`
  (`workerClass TheForce_Standalone.Generic.Recipe_MidichlorianTest`), added to
  `ThingDef[@Name="Human"]` by the mod's single patch file
  `…\1.6\Patches\Alignment_Patch.xml`; result recorded as `HediffDef Force_TestedMidichlorians`.
- ~20 custom StatDefs carry the economy: `Force_MidichlorianCount`, `Force_FPMax`
  (`StatWorker_ForcePowerMax`), `Force_FPRecovery`, `Force_XPGain`,
  `Force_Darkside_Attunement`, `Force_Lightside_Attunement`, …

**Abilities: plain vanilla `AbilityDef`, no psylink, no VPE.** Organised by
`AbilityCategoryDef` (`Force_Darkside`, `Force_Lightside`, `Force_Neutral`,
`Force_Telekinesis`, `Force_NightsisterMagick`, `Force_JediTraining`,
`Force_SithSorcery`, `Force_MechuDeru`). Abstract bases `Force_SelfCastAbilities`
/ `Force_AllyCastAbilities` (`jobDef CastAbilityOnThingUninterruptible`,
`verbClass Verb_CastAbility`) each add
`TheForce_Standalone.CompProperties_AbilityEffect_ForcePower` and
`TheForce_Standalone.ForceAbilityDefExtension` — that pair is the "is a Force
power" signature. ~74 defNames, e.g. `Force_Lightning`, `Force_ForceChoke`
(`Telekinesis.CompAbilityEffect_ForceChoke`), `Force_ForcePush`, `Force_ForcePull`,
`Force_ThrowItem`, `Force_TelekineticBarrier`, `Force_MindControl`,
`Force_JediMindTrick`, `Force_ForceHealing`, `Force_Leap` (`Verb_CastAbilityJump`),
`Force_Rage`, `Force_Insanity`, `Force_Destruction`, `Force_Apprenticeship`.
Learned in-fiction through `Force_JediHolocron` / `Force_SithHolocron`
(`CompProperties_UseEffect_GainRandomAbility`).

**Genes: 8, all Biotech-gated**
(`…\1.6\Mods\Biotech\Defs\GeneDefs\GeneDefs_Spectrum.xml`) —
`Force_MidichlorianLow/Average/High`, `Force_MidichlorianLight/LightExalted`,
`Force_MidichlorianDark/DarkExalted`, and `Force_Gene_LatentForceUser` (custom
`geneClass TheForce_Standalone.Genes.Gene_LatentForceUser`, activates Force
sensitivity over ~3 years and levels the pawn up). **Zero XenotypeDefs.**

**PawnKinds: 3, none faction-attached** — `Force_Mech_Inquisitor` (Biotech mech,
cp 85, `weaponTags` `Force_InquisitorLightsaber`), `Force_DarksideWraith` (animal,
cp 200), `SithSorcery_Terentatek_PawnKind` (animal, cp 800). No
`defaultFactionType`, no `factionLeader`, no `apparelTags` anywhere in the mod —
faction integration is entirely code-side (`Patch_ForcePawnKind`,
`Patch_GeneratePawns`, `ForcePawnKindDefs`, `UnlockPawnKindAbilities`), i.e. it
**injects Force capability into other mods' pawnkinds at runtime**.

**Weapons: it ships no lightsaber.** Only `Force_SithBladelink` ("Sith Warblade",
`ParentName="BaseWeapon_Bladelink"`, Royalty-gated,
`…\1.6\Mods\SithSorcery\Defs\ThingDefs_Misc\SithArtifact.xml:344`). Three custom
DamageDefs, all `ParentName="Flame"`: `Force_Lightning`, `Force_EnergyBurn`,
`Force_LightBurn`. Lightsabers live in the separate `lee.theforce.lightsaber`.

**C#: `Star Wars The Force - Standalone.dll`, 516,096 bytes, plus a bundled
`0Harmony.dll`.** ~40 Harmony patch classes, including
`PawnGenerator_GenerateTraits_Patch`, `Patch_GeneratePawns`,
`PawnApparelGenerator_PostProcessApparel_Patch`, `Patch_PreApplyDamage`,
`Patch_Projectile_ImpactSomething_Catch`, `Verb_AbilityShoot_TryCastShot_Patch`,
`Faction_TryMakeInitialRelationsWith_Patch`, `Patch_Pawn_GeneTracker_AddGene`,
`Thing_Destroy_Patch`, `Patch_Ideo_SetIcon`, `TendUtility_DoTend_Patch`,
`PeaceTalks_Outcome_Success_Patch`, `ShouldBeMechanitor_Patch`. It also loads a
custom shader asset bundle. **This is a very wide blast radius** — pawn
generation, damage application, projectile impact, apparel generation and faction
relations are all patched.

### 2b. *The Force Factions* (`lee.theforce.factions`, folder 3557220783)

**Ships no DLL at all** — `1.6/Assemblies/` is an empty directory. It is pure XML
on top of Standalone and Lightsaber, both declared as hard `v1.6`
`modDependenciesByVersion`.

**Factions:** `Force_Jedi_Remnant`, `Force_Sith_Order` (plus player variants
`Force_Jedi_RemnantPlayer`, `Force_Sith_OrderPlayer`). Both
`ParentName="FactionBase"`, `categoryTag Outlander`, `permanentEnemy false`,
`settlementGenerationWeight 0.2`, `earliestRaidDays 50`, `techLevel Ultra`, and
the same pirate-shaped `maxPawnCostPerTotalPointsCurve`
`(0,35)(70,50)(700,100)(1300,150)(100000,10000)`.

Hostility is **not** `permanentEnemy` — it is a modExtension:

```xml
<li MayRequire="lee.theforce.standalone" Class="TheForce_Standalone.Generic.ModExtension_FactionExtension">
  <permanentEnemyFactions>
    <li>Force_Sith_Order</li>
    <li MayRequire="neronix17.outerrim.galacticempire">OuterRim_GalacticEmpire</li>
    ...
```

**PawnKinds:** abstract `Jedi_Base` / `SithBase` plus 19 concrete kinds.
Jedi: `Force_Jedi_Padawan` (cp 65), `Force_Jedi_Sentinel`/`Guardian`/`Consular`
(70), `Force_Jedi_Master` (80), `Force_Jedi_Grandmaster` (100,
`factionLeader true`), `Force_Jedi_Trader`, `Force_JediTempleGuard` (70).
Sith: `Force_Sith_Apprentice` (65), `Force_Sith_Assassin`/`Warrior`/`Sorcerer`
(70), `Force_Sith_Lord` (80), `Force_Sith_Darklord` (100, `factionLeader true`),
`Force_Sith_DarklordRage` (100, `factionLeader true`, **in no group maker at
all**), `Force_Sith_Trader`, `Force_Sith_MechuSorcerer` (70, Biotech).

`Jedi_Base` gear shape, worth copying structurally:

```xml
<race>Human</race>
<defaultFactionType>Force_Jedi_Remnant</defaultFactionType>
<royalTitleChance>0</royalTitleChance>
<itemQuality>Normal</itemQuality>
<combatPower>55</combatPower>
<weaponMoney>9000~20000</weaponMoney>
<weaponTags Inherit="True">
   <li MayRequireAnyOf="lee.theforce.lightsaber,lee.theforce.lightsaber_steam">Force_Lightsaber</li>
</weaponTags>
<apparelAllowHeadgearChance>0.2</apparelAllowHeadgearChance>
<apparelMoney>1000~1500</apparelMoney>
<apparelIgnoreSeasons>true</apparelIgnoreSeasons>
<nakedChance>0</nakedChance>
<ignoreIdeoApparelColors>true</ignoreIdeoApparelColors>
```

Force level and powers are set per kind through Standalone modExtensions plus a
`grantRandomAbilities` count drawn from `Force_Lightside`/`Force_Darkside`
categories — i.e. **the whole power layer depends on the Standalone DLL.**

Xenotypes are set at **FactionDef** level, never on the pawnkind: each NPC
faction carries `<xenotypeSet Inherit="False">` with ~50 entries, mostly
`guy762.starwarsxenotypes` species at `0.002` and Galactic Diversity species at
`0.001`; the Sith faction adds `guy762_xenotype_sith` at **0.4**. It defines no
XenotypeDef, GeneDef or HediffDef of its own.

**How it makes a Force user rare, and how it makes one a leader — two different
mechanisms:**

1. **Rarity is `<options>` weight × the cost curve.** In the Jedi baseline
   Combat group the weights are Padawan 15 / Consular 1 / Sentinel 1 / Guardian 2
   / Master 2 / Grandmaster 1 — sum 22, so a Grandmaster is ~4.5 % of picks.
   Sith: Apprentice 5 / Warrior 3 / Sorcerer 3 / Assassin 3 / Lord 0.8 /
   Darklord 0.5 — sum 15.3, Darklord ~3.3 %. On top of that the cost curve gates
   `combatPower 100` out of any raid under ~700 points.
2. **"Leader" is the vanilla `<factionLeader>true</factionLeader>` flag** on
   `Force_Jedi_Grandmaster` and `Force_Sith_Darklord`. There is **no
   `Leaders` pawnGroupMaker kindDef, no `fixedLeaderKinds`**, and — verified —
   **`factionLeaderKinds` is not a real field**: `grep -rn factionLeaderKinds`
   over all of `…\RimWorld\Data\` returns zero, and the string is absent from
   `Assembly-CSharp.dll`. The real field is `fixedLeaderKinds`, used in exactly
   two shipped files (`…\Data\Royalty\Defs\FactionDefs\Faction_Empire.xml`,
   `…\Data\Odyssey\Defs\FactionDefs\Factions_Misc.xml`).

   ⚠️ **`factionLeader` governs the *world faction leader pawn*, not raid
   composition.** The Grandmaster shows up in a raid purely because of its
   `<options>` weight. Royalty's `Empire_Royal_Stellarch` is the counter-example:
   it is the `fixedLeaderKinds` entry and appears in **no** pawnGroupMaker.

Also worth knowing before copying anything from this mod: it re-declares **eight
vanilla `SketchResolverDef` defNames** verbatim (`AncientBarracks`,
`AncientStorageRoom`, `AncientEquipmentRoom`, `AncientPowerRoom`, `AncientLab`,
`AncientArmory`, `AncientUtilityBuilding`, `AncientLandingPad`) — duplicate-def
overrides of Core; it declares `<backstoryFilters>` **twice** on
`Force_Jedi_Remnant`, so the second silently discards the first; its one patch
file adds `<renderSkipFlags>` in **both** the `match` and `nomatch` branch of a
`PatchOperationConditional`, producing a duplicate element when the field already
exists; three of its Def files are empty `<Defs></Defs>` shells; and its
`Languages/English/Keyed/` files are copies of Standalone's keys, so they
duplicate.

---

## 3. The recommended build

**Design being served** (owner, 2026-08-13): the **Jedi** is a rare raid leader
of the moisture-farmer faction; the **Sith** is a rare raid leader of the Galactic
Empire; both are best expressed as a **xenotype with preferential equipment**.
Consistent with `faction_roster_v2.md:229-233` and with `OWNER_DECISIONS.md` row
10 — there is **no separate Imperial Droid Army**; the Directorate fields
stormtroopers, purge units and lightsaber-bearing Sith together.

### 3.0 The one decision that must be made first

**Everything downstream forks on whether the Force user *casts* anything.**

| option | what you get | cost |
|---|---|---|
| **A. Melee duellist (no powers)** | A xenotype with psylink 1 from `guy762_statgene_force`, a persona plasmasword, high Melee, `combatPower` ~200. Reads as a Sith/Jedi on the field. Casts nothing. | **Zero new frameworks. Pure XML. Ships today.** |
| **B. Melee duellist + utility powers** | A, plus `guy762_GeneAbility_forcesight` / `guy762_GeneAbility_jump`, which are `aiCanUse true` and already in the stack. | Still pure XML. Powers are non-combat; a "Force leap" is the only visible one. |
| **C. Real Force combat powers** | Lightning, choke, throw. | Requires either **installing VPE** (a 570-mod load-order change and a re-verification pass) or **authoring AbilityDefs + an NPC-casting think-tree node**, which is C#/Harmony work. See §4. |

**Recommendation: build A, structured so B is a one-line addition and C is a
later swap of the ability list.** A is achievable inside the existing patch mod
with defs that are all verified present; C is a project, not a task.

### 3.1 Xenotypes — use what we have; author nothing

| role | xenotype | why |
|---|---|---|
| **Sith** | `guy762_xenotype_sith` | Already carries `guy762_statgene_force` → `PsychicAmplifier` (psylink 1). Also `PsychicAbility_Extreme`, `Aggression_HyperAggressive`, `MeleeDamage_Strong`, `AptitudeRemarkable_Melee`, red skin, bone head, `combatPowerFactor 1.5`. `nameMaker NamerPersonPureblood`. This is a Sith with no authoring at all. |
| **Sith castes (optional flavour)** | `BTD_SithK` / `BTD_SithM` / `BTD_SithZ` | Kissai priest / Massassi warrior / Zugurak engineer. `BTD_SithK` carries `PsychicAbility_Enhanced` + `Turn_Gene_LatentPsychic`. **No `guy762_statgene_force`, so no psylink** — flavour only unless the psylink is supplied by §3.3. |
| **Jedi** | `guy762_xenotype_miraluka` | Carries `guy762_statgene_force`, `PsychicAbility_Enhanced`, `Aggression_DeadCalm`, `Turn_Gene_Blindness`, and via the Royalty folder gains `guy762_AbilityGene_forcesight` → the `aiCanUse` blindsight ability. `faction_roster_v2.md:14` already places Miraluka as *"rare Homestead seers (~1%)"*. **This is the single best fit in the stack.** |
| **Jedi (human option)** | `guy762_xenotype_mirialan` | Green/yellow-skinned, "more sensitive to the force". ⚠️ Its Force gene line is `<li MayRequire="lee.theforce.standalone">Force_Gene_LatentForceUser</li>` — **stripped in our stack**, so a Mirialan here is a cosmetic Jedi with no psylink. Use Miraluka, or add the gene via §3.3. |

**Do not author a new XenotypeDef unless the owner wants a distinct look.** If one
is wanted later, the house pattern is
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Defs\XenotypeDefs\GamorreanXenotype.xml`
— fork an existing xenotype, document every deliberate change in the header,
confirm every gene against a live dump before writing it.

### 3.2 Weapon

`MeleeWeapon_PlasmaSwordBladelink` (`weaponTag` **`Bladelink`**). One tag, one
line on the pawnkind:

```xml
<weaponTags Inherit="false">
  <li>Bladelink</li>
</weaponTags>
<weaponMoney>3000~3500</weaponMoney>
```

`Bladelink` also admits `MeleeWeapon_MonoSwordBladelink` and
`MeleeWeapon_ZeusHammerBladelink`. If a lightsaber must be the *only* possible
roll, that is not achievable with a tag — use `<apparelRequired>`-style forcing,
which does not exist for weapons; instead set `weaponMoney` tightly and accept the
three-way roll, or gate it with a bespoke tag added by a `PatchOperationAdd` onto
`MeleeWeapon_PlasmaSwordBladelink/weaponTags` (safe: it is a vanilla def, and
adding a tag cannot remove it from existing tables).

**When `lee.theforce.lightsaber` is restored** (see §6), the change is one line —
swap the tag for whatever that mod's lightsaber tag is. Do not write that tag
now: it cannot be verified from disk and this project does not guess defNames.

### 3.3 Psylink, if the xenotype does not carry it

`TabulaRasa.DefModExt_PawnKindExtended` is active and does exactly this. Pattern
read from `…\2919248699\1.6\Defs\PawnKindDefs\PawnKinds_Stormtroopers.xml:486`:

```xml
<modExtensions>
  <li Class="TabulaRasa.DefModExt_PawnKindExtended">
    <additionalHediffs>
      <li>
        <hediff>PsychicAmplifier</hediff>
        <severityRange>3~5</severityRange>
      </li>
    </additionalHediffs>
    <randomAdditionalHediff>false</randomAdditionalHediff>
  </li>
</modExtensions>
```

`PsychicAmplifier` severity **is** the psylink level (`maxSeverity 6`). This gives
the `faction_roster_v2.md` numbers — "Psylink 3–6" for Jedi, "4–6" for Sith —
without touching a gene. ⚠️ **Unverified:** whether `additionalHediffs` applies to
a whole-body hediff as cleanly as to a body-part one. Confirm on a dev-spawned
pawn before relying on it.

### 3.4 The pawnkinds

Two new defs, in the house style of
`…\Mods\Jawa_Patches\Defs\PawnKindDefs\GamorreanPawnKinds.xml` — standalone, no
`ParentName` (see the load-order trap in §4).

```xml
<PawnKindDef>
  <defName>Jawa_Sith_Inquisitor</defName>
  <label>Sith inquisitor</label>
  <labelPlural>Sith inquisitors</labelPlural>
  <race>Human</race>
  <defaultFactionDef>OuterRim_GalacticEmpire</defaultFactionDef>
  <combatPower>220</combatPower>
  <maxPerGroup>1</maxPerGroup>
  <isFighter>true</isFighter>
  <canBeSapper>false</canBeSapper>
  <minGenerationAge>25</minGenerationAge>
  <useFactionXenotypes>false</useFactionXenotypes>
  <xenotypeSet>
    <xenotypeChances>
      <guy762_xenotype_sith>999</guy762_xenotype_sith>
    </xenotypeChances>
  </xenotypeSet>
  <itemQuality>Excellent</itemQuality>
  <gearHealthRange>1~1</gearHealthRange>
  <apparelMoney>2500~4000</apparelMoney>
  <apparelAllowHeadgearChance>0.5</apparelAllowHeadgearChance>
  <apparelIgnoreSeasons>true</apparelIgnoreSeasons>
  <apparelTags>
    <li>ImperialApparel</li>
    <li>ImperialOfficer</li>
  </apparelTags>
  <weaponMoney>3000~3500</weaponMoney>
  <weaponTags Inherit="false">
    <li>Bladelink</li>
  </weaponTags>
  <skills>
    <li><skill>Melee</skill><range>14~20</range></li>
    <li><skill>Social</skill><range>8~14</range></li>
  </skills>
  <requiredWorkTags><li>Violent</li></requiredWorkTags>
  <initialWillRange>8~12</initialWillRange>
  <initialResistanceRange>30~46</initialResistanceRange>
</PawnKindDef>
```

and the Jedi twin — `Jawa_Jedi_Sentinel`, `defaultFactionDef OuterRim_MoistureFarmers`,
`xenotypeChances guy762_xenotype_miraluka 999`, `combatPower 220`,
`maxPerGroup 1`, apparel tags drawn from what the Homestead pawnkinds already
use, **no `factionLeader`**.

Every field above is verified: `<xenotypeSet><xenotypeChances>` + weight `999` +
`<useFactionXenotypes>false</useFactionXenotypes>` is the shipped Biotech idiom
(`…\Data\Biotech\Defs\PawnKindDefs_Humanlikes\PawnKinds_Special.xml:76`,
`SanguophageBase`) and is already used by us in `GamorreanPawnKinds.xml`.
`<maxPerGroup>` is real and shipped — `…\Data\Biotech\Defs\ThingDefs_Races\Races_Mechanoids_SuperHeavy.xml`,
`Mech_Apocriton` etc., all at `3`. ⚠️ **Vanilla only ever uses `maxPerGroup` on
mechanoids**; the enforcing code path (`PawnGroupMakerUtility`,
`<PawnGenOptionValid>g__ChosenKindCount`) is generic, but there is no shipped
humanlike precedent. Verify on a dev-spawned raid.

### 3.5 Making them RARE, and making them read as the leader

**Rarity: `<options>` weight plus `maxPawnCostPerTotalPointsCurve`.** The two
factions need different numbers because their curves differ by an order of
magnitude.

| | Empire | Homestead |
|---|---|---|
| curve at 700 pts | **100** | **1800** |
| curve at 1300 / 2000 pts | 150 | 5000 |
| ⇒ a `combatPower 220` kind is eligible from | **~2000 points** — very late | **~5 points** — i.e. always |

(Empire: 220 falls between the `(1300,150)` and `(100000,10000)` points, ≈ 2001.
Homestead: 220 falls between `(0,200)` and `(70,500)`, ≈ 4.7 — the curve never
gates it at all.)

So the same `combatPower` produces "endgame boss" on the Empire and "shows up
constantly" on the Homestead. **Do not use the same weight on both.**

- **Empire:** weight `0.1` in the *Hot Weather Squad* (the desert group), `0.02`
  elsewhere — i.e. mirror the weights the mod already reserved for
  `OuterRim_SithInquisitor`. Against that group's other weights (sum 45) that is
  ~0.2 % of picks, further gated by the curve to raids above ~2000 points. That
  is genuinely rare and genuinely a boss.
- **Homestead:** weight `0.15` against a Combat weight sum of 62 → ~0.24 % of
  picks. Because the Homestead curve is permissive, **the weight is the only
  throttle here**, so keep it low and rely on `maxPerGroup 1`.

**Leadership: do NOT set `<factionLeader>true</factionLeader>`.** Both factions
already have leader kinds — `OuterRim_ImpStormCommander` (Empire, also named in
`fixedLeaderKinds`) and `OuterRim_TownCouncilman` (Homestead) — and the Empire's
world leader is deliberately the *Sector Director* under
`ImperialDesertDirectorate.xml`. Adding a second `factionLeader` kind would put a
Sith in the pool for that role and undercut a ratified design decision.

"Raid leader" in the owner's sense is achieved by **high `combatPower` + low
weight + `maxPerGroup 1`**: one of them, rarely, obviously the strongest thing on
the field. That is exactly what the reference mod achieves too — its
`factionLeader` flag is doing world-leader work, not raid work.

### 3.6 Files to create or patch

All inside `Jawa_Patches`, which sits at **position 567** in the load order —
after Outer Rim Core (530), Galactic Empire (546), Star Wars Xenotypes (549), BTD
REMIX (562) and KotOR Weapons (564). Every def and faction it needs is already
loaded by then.

| file | action |
|---|---|
| `…\Mods\Jawa_Patches\Defs\PawnKindDefs\ForceUserPawnKinds.xml` | **NEW.** `Jawa_Sith_Inquisitor`, `Jawa_Jedi_Sentinel`. |
| `…\Mods\Jawa_Patches\Patches\ForceUsers_Empire.xml` | **NEW.** `PatchOperationFindMod` on *Outer Rim - Galactic Empire*, wrapping `PatchOperationAdd` ops that insert the option into the Combat groups. |
| `…\Mods\Jawa_Patches\Patches\ForceUsers_Homestead.xml` | **NEW.** Same shape against *Outer Rim - Core*. |
| `…\Mods\Jawa_Patches\Patches\ImperialDesertDirectorate.xml` | **UNCHANGED.** Do not fold Force work into the v1 label patch. |

⚠️ **xpath shape matters.** The Empire's group makers are seven near-identical
`<li Class="TabulaRasa.PawnGroupMaker_Temperature">` siblings; an index-based
xpath (`pawnGroupMakers/li[7]`) will silently retarget if the upstream mod
reorders them. Select by a child instead:

```xml
<xpath>/Defs/FactionDef[defName="OuterRim_GalacticEmpire"]/pawnGroupMakers/li[options/OuterRim_ImpStormtrooper_Desert]/options</xpath>
```

and mirror that for the Homestead:

```xml
<xpath>/Defs/FactionDef[defName="OuterRim_MoistureFarmers"]/pawnGroupMakers/li[kindDef="Combat"]/options</xpath>
```

The repo's own precedent for wrapping everything in `PatchOperationFindMod` so
the file is a silent no-op when the host mod is absent is
`ImperialDesertDirectorate.xml` — follow it.

**And do not deploy from the repo without reading the plan first**
(`skills/rimworld-deploy/SKILL.md`): the game reads
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches`, not
this repo, and `deploy_custom_mods.py --apply` overwrites the game copy with
whatever is in the repo at that moment — including another seat's half-finished
work.

---

## 4. What we author vs what we get free — the honest gap

### Free, verified present, zero authoring

- Both target factions, with working raid tables — `OuterRim_GalacticEmpire`,
  `OuterRim_MoistureFarmers`.
- A Sith xenotype, a Jedi xenotype, and three Sith castes — all six defNames in §1a.
- Force sensitivity **and psylink** — `guy762_statgene_force` → `PsychicAmplifier`.
- Three AI-usable Force-flavoured abilities — `guy762_GeneAbility_forcesight`,
  `guy762_GeneAbility_defelcloak`, `guy762_GeneAbility_jump`.
- A persona energy blade — `MeleeWeapon_PlasmaSwordBladelink`.
- Imperial officer wardrobe, ISB gear, and the whole stormtrooper apparel tag set.
- The per-pawnkind xenotype mechanism (`xenotypeSet` + `useFactionXenotypes`),
  the rarity mechanism (option weight + cost curve), the one-per-raid mechanism
  (`maxPerGroup`), and a hediff injector (`TabulaRasa.DefModExt_PawnKindExtended`).
- A desert-weighted Sith slot the Empire mod already reserved at `0.1`.

### Authored — small, ~2 files, all XML

- Two PawnKindDefs.
- Two patch files adding one `<options>` entry each.
- Optionally a forked XenotypeDef if a distinct look is wanted.

### NOT free, and this is the real gap

- **A lightsaber.** There is none in the stack (§ finding 2). The build ships
  with a persona plasmasword until `lee.theforce.lightsaber` is restored.
- **Force combat powers.** Nothing in the stack does lightning, choke or
  telekinetic throw, and VPE — the ruled substrate — is not installed.
- **NPC casting.** Even given powers, vanilla will not cast them (§ finding 4).
  `guy762_GeneAbility_forcesight` and `_jump` are `aiCanUse true` and therefore
  the only things an enemy Force user will actually *do*, and neither is a combat
  power.
- **Force-user progression, alignment, holocrons, apprenticeship.** All of that
  is Standalone's C#. None of it is reachable.
- **Backstories, culture, names.** `guy762_xenotype_sith` has
  `NamerPersonPureblood`; there is no Jedi/Sith backstory category in the stack.

**So, stated plainly: what ships is a rare, terrifying melee duellist of the
right species carrying the right blade — not a caster.** That is a real and
recognisable Sith on the field. It is not the Force system in
`required_mods.md:620-642`, and that system is currently not buildable at all.

---

## 5. Risks

### 🔴 R1 — The ruled Force design rests on a mod that is not installed

`required_mods.md:620` finalizes *"VPE ONLY"* and `:623` calls VPE the sole
substrate; `faction_roster_v2.md:231` says both Jedi channels *"draw on the same
curated NPC-only VPE ability set"*. **VPE is not in `ModsConfig.xml` and no folder
in the workshop tree owns `VanillaExpanded.VPsycastsE`.**

Either the ruling was never executed, or VPE was removed and the docs were not
updated. **This is not mine to resolve** — it is a mod-roster decision, and
`required_mods.md` is WORLD's file. It must be filed, not silently worked around
(§6). Adding VPE now is a dependency change to a 570-mod order and a full
re-verification, at ~23–30 min per cold load; it is not a side effect of building
a pawnkind.

### 🔴 R2 — Do not adopt the reference mods' architecture

Standalone is a 516 KB Harmony assembly patching pawn generation, trait
generation, apparel generation, damage pre-application, projectile impact,
faction relation creation, gene add/remove, tend, peace talks and mechanitor
eligibility — plus a custom shader bundle and a `Doorstopper`. In a 570-mod order
that is a very large surface for a mod whose reviews already report instability.
The owner's decision to keep both uninstalled is well supported by what is on
disk. **Nothing in this spec requires any of it.**

Specific things **not** to copy even as patterns:
- Redeclaring vanilla defNames (Factions redeclares eight `SketchResolverDef`s).
- Duplicate sibling nodes (`backstoryFilters` twice on `Force_Jedi_Remnant`).
- A `PatchOperationConditional` whose `match` and `nomatch` branches do the same
  `Add` (its `CapePatch.xml`) — that adds a duplicate element.
- Empty `<Defs></Defs>` shells and copied `Keyed` files.
- Licence: Outer Rim is **CC BY-NC-ND 4.0** (`required_mods.md`, retraction
  block). Patching its defs is fine; **copying its defs or textures into a mod of
  ours is a derivative**. The same caution applies to the reference mods — read
  them, do not port them.

### 🟠 R3 — Abstract-parent inheritance is load-order dependent

`skills/rimworld-modding/references/traps-xml-and-defs.md:52` records the cost:
a child `PawnKindDef` whose parent's mod loads *later* does not inherit, and the
result is `Config error … no race`, `has no combatPower`, then
`NullReferenceException` inside `PawnKindDef.ConfigErrors` and cascading nulls in
`BiomeDef.CommonalityOfAnimal` and `ScenPart_StartingAnimal`. It was caused by a
manager re-sort after the defs had worked for days.

`Jawa_Patches` currently loads at 567, after everything it needs — but a re-sort
can move it. **Write the new pawnkinds standalone, with no `ParentName`**, as
`GamorreanPawnKinds.xml` already does and for exactly this reason.

### 🟠 R4 — `maxPerGroup` on a humanlike is unprecedented in shipped content

Real field, real enforcement path, but every vanilla usage is a mechanoid boss.
Verify on a dev-spawned raid before treating "one per raid" as guaranteed.

### 🟠 R5 — Patching another mod's `pawnGroupMakers` by index is brittle

Seven near-identical Tabula Rasa temperature groups on the Empire. Use
child-predicate xpaths (§3.6). A silent xpath miss is the classic
PatchOperation failure mode: the game logs a patch error but keeps running, and
the Sith simply never appears.

### 🟠 R6 — `combatPower` means different things in the two factions

The Homestead's cost curve is ~18× more permissive at 700 points than the
Empire's. A single shared number will make the Jedi common and the Sith
unreachable. Tune per faction (§3.5), and check the result against real raids,
not against the XML.

### 🟡 R7 — Adding a xenotype changes existing saves incompletely

`traps-xml-and-defs.md:85-87`: editing a `XenotypeDef` never rewrites pawns
already in the save. If a forked xenotype is introduced later, `grep` the `.rws`
for the old defNames using `<def>NAME</def>` — a bare grep returns 1 on a world
that does not contain the thing, because of the defName registry.

### 🟡 R8 — `guy762.KotORWeapons` has an unmet hard dependency

It declares `lee.theforce.lightsaber` as a `v1.6` `modDependency`, and the mod is
absent. Beyond the missing lightsabers, nothing else about its 1.6 health has
been checked here.

---

## 6. Things to file (not fixed here — outside this pass's scope)

Per `CLAUDE.md` "Never ignore a problem, especially one that is not yours". None
of these needs the game running, so they belong in `TODO.md`.

0. **`[?]` A one-subscription fix for the missing lightsaber exists:
   `VanillaExpanded.VWEL`** (Vanilla Weapons Expanded - Laser, WS 1989352844,
   on disk at `…\294100\1989352844`, **not active**). Its `VWEL_LaserSword`
   already carries the `UltratechMelee` tag this spec uses, has no
   `CompDeflector`, and is a first-party VE mod rather than a discontinued one.
   Worth putting to the owner as an alternative to chasing
   `lee.theforce.lightsaber`. Roster decision, not mine.
1. **`[?]` `lee.theforce.lightsaber` is active in `ModsConfig.xml` but not on
   disk.** Workshop 3466124712. Result: no lightsaber weapon exists anywhere in
   the active stack, and `guy762.KotORWeapons` (active) has an unmet `v1.6` hard
   dependency. Checked clean: the mod is genuinely absent (full-text sweep of
   every `About/About.xml` in the workshop tree and the local `Mods` folder — the
   only hits are other mods' `modDependencies` blocks); `guy762.KotORWeapons`
   `LoadFolders.xml` has its `_NO_ForceLightsabers` fallback commented out for
   `v1.6`, so nothing substitutes. Either resubscribe the mod or uncomment
   nothing — the fix is upstream, not ours.
2. **`[WORLD]` `VanillaExpanded.VPsycastsE` is not installed, and
   `required_mods.md:620-642` still calls it "the sole Force substrate".** Two
   more docs depend on the same assumption:
   `faction_roster_v2.md:229-231` and `TODO_v2.md:1081` (U4). The VPE defName
   shopping list at `required_mods.md:638-642` currently names defs that are not
   in the game. WORLD owns `required_mods.md`; this needs a roster decision
   (install VPE, or restate the Force design against what we run), not a doc edit
   by a research pass.
3. **`[v2]` U4's premise is now cheaper than it was written.** `TODO_v2.md:1081`
   says the Homestead Jedi wiring needs *"the curated light + telekinesis VPE
   loadout"*. With VPE absent, §3 of this document is the buildable alternative,
   and it needs no new framework.

---

## 7. What could not be established

Stated explicitly rather than filled in.

- **What `OuterRim_SithInquisitor` actually is.** It is referenced six times in
  the Empire's group makers but defined in `Neronix17.OuterRim.HokeyReligions`,
  which is neither installed nor on disk. Its `combatPower`, gear, weapon tags
  and whether it is a `factionLeader` are all unknown. If that module were
  installed, the Sith half of this spec might reduce to zero authoring — **that
  is worth checking before building anything.**
- **The lightsaber defNames and weapon tags in `lee.theforce.lightsaber`.** The
  mod is absent, so `Force_Lightsaber`, `SE_sithsaber`, `SE_sithwarrior`,
  `Force_InquisitorLightsaber` and the `Force_*HiltPart` names are known only as
  *references* made by other mods. None was read from its own def. Do not write
  any of them into a patch.
- **Whether `TabulaRasa.DefModExt_PawnKindExtended.additionalHediffs` applies a
  whole-body hediff like `PsychicAmplifier` correctly.** The field exists
  (`strings` on `TabulaRasa.dll`) and the shipped usage attaches
  `OuterRim_ISBTraining`; the psylink case is inferred, not observed.
- **Whether a psylink-1 NPC with no learned psycasts behaves harmlessly.** It
  should be inert, but this was not tested and `guy762_xenotype_sith` pawns
  presumably already spawn this way today.
- **Whether ~60 packageIds listed active resolve to folders.** A first index pass
  showed false negatives (e.g. `vanillaexpanded.vfepower` resolves to folder
  `2062943477` on a direct grep but was missed by the batch scan), so that list
  is not evidence of missing mods. Only `lee.theforce.lightsaber` and
  `VanillaExpanded.VPsycastsE` were confirmed absent by direct full-text search,
  and those two are asserted here.
- **The `Force_*` xenotype question is moot** — the Standalone mod ships zero
  XenotypeDefs, so there was nothing to compare our xenotypes against.
- **Whether the five `SW_Force*` animal AbilityDefs (§1e-bis) can be granted to a
  humanlike pawnkind and cast by enemy AI.** This is the highest-value open
  question in the document. They are real, loaded AbilityDefs implementing Force
  Push, Scream, Invisibility, Skip and Focus; they are attached to animals via
  `TrainableDef`. Their `aiCanUse` flags, whether `<abilities>` on a humanlike
  PawnKindDef would grant them, and whether any think-tree node would fire them
  were **not checked**. If the answer is yes, option C in §3.0 costs a patch file
  rather than a mod install. **Check this before accepting the "no Force powers"
  conclusion.**
- **Whether `VEF.Abilities.PawnKindAbilityExtension` grants AI-castable abilities
  to a pawnkind.** VEF is active and the extension exists; its behaviour was not
  read. Same reasoning — it may collapse option C.
- ~~The full lightsaber sweep was cut short.~~ **Now settled.** A `<label>` sweep
  across all 620 active mod folders returned only crystals, hilt parts, research
  and category labels, and a separate full census of the workshop tree
  independently reached the same conclusion and cleared each candidate mod by
  name (JDS Armory, Outer Rim Core and all four submodules, KotOR Resources,
  KotOR Droids, Jawa_Armoury). **"There are zero loadable lightsaber ThingDefs in
  the active 1.6 modlist" is now established, not merely supported.**
- **The `lee.theforce.lightsaber` defNames remain references only.** The names
  that mod would supply were harvested from the *xpaths of patches that target
  it* (`…\2938932438\1.6\AdditionalMods\_TheForceLightsabers\Patches\Patch_KotORLightsaberBalancing.xml`)
  and from the reference mod's pawnkinds — `Force_Lightsaber`,
  `Force_Lightsaber_Custom`, `_Curved`, `_Dual`, `_Crossguard`, `_Inquisitor`,
  `_Shoto`, `Force_Broadsaber`, `Force_Darksaber`, and weaponTags
  `Force_LightsaberSingle` / `_Dual` / `_Crossguard` / `_LightsaberCombat`.
  **None was read from its own def, because the mod is absent.** They are
  recorded here as a shopping list for whoever restores it — **not** as defNames
  fit to write into a patch.

---

### Provenance

Every def, field and weight quoted here was read on disk on 2026-08-13 from the
game install, the Steam Workshop tree, or the deployed
`…\RimWorld\Mods\Jawa_Patches`. Nothing was inferred from a mod manager UI, a
Workshop page, or memory. Where a fact could not be read, §7 says so.

---

## ✅ CLOSED — FALSE ALARM. The saber mod IS installed. 2026-08-13

**Checked and fine — recorded rather than deleted, so the next seat does not
re-find it.** `lee.theforce.lightsaber` is **installed at workshop `3466124712`**,
verified against its own `<packageId>` in `About.xml`, and `ModsConfig.xml:575` is
correct. **No startup complaint is coming.** OPS closed the same item on the same
evidence.

**Nothing in the spec below was ever at risk**, and the design consequence I drew
from the alarm — *do not spend the laser sword on the armoury line* — **still
stands on its own merits** (a buildable common laser sword and a rare Sith blade
cannot be the same object), not because of a missing mod.

_Superseded alarm, kept for the trail:_

## ~~🔴 DEPENDENCY ALERT — the saber mod is GONE from disk~~ (WITHDRAWN)

**This spec was written against a gap, not against the mod** (`b5796eb`). OPS has
since established the mod was **real and running**: Workshop `3466124712`,
`lee.theforce.lightsaber`, **333 defs including 14 wieldable lightsabers**, live
in the 10:04 session. Its folder has since been deleted and it is absent from
`appworkshop_294100.acf`. `ModsConfig.xml` still activates it.

⚠️ **The loss is completely silent.** Every surviving saber reference is
`MayRequire`/`IfModActive` gated, so nothing errors — **the Star Wars campaign
simply has zero lightsabers and the log never says so.** No other active mod
defines one: KotOR's 47 `SWSaber_KotOR_*` are 1.5-only.

**Owner action: re-subscribe `3466124712` before the next load.** Fallback if the
Workshop item is delisted: port the KotOR 1.5 saber XML.

**Design consequence, and it is mine:** until this resolves, **do not promote the
`laser sword` from Vanilla Weapons Expanded – Laser into the Force role**
(`worldbuilding/ship_legacy_armoury.md`). A buildable common laser sword and a
rare Sith blade cannot be the same object — if we spend the saber on the armoury
line, the Force users have nothing left that is theirs.

---

## 🔴 OWNER'S RULING 2026-08-13 — Force users are NPC-ONLY, PERMANENTLY

**The player never becomes a Force user. Not late, not rarely, not as a reward.**

**Why this is the right call and should not be relitigated:**

- **The anti-exponential pillar.** A player Force user is the single fastest way
  to break a scarcity campaign. Everything else in this design — water, salvage,
  droid labour, the pursuit — is about *not* snowballing. One lightsaber in the
  player's hands undoes all of it.
- **Rarity is the whole effect.** A Jedi or a Sith is frightening because you
  cannot be one. Make it obtainable and it becomes a build order.
- **It is not the Jawa fantasy.** The clan's fantasy is *taking apart the things
  powerful people leave behind*. **The saber is the trophy, not the class** — and
  a trophy you cannot use is a better story than a weapon you can.

**So Jedi and Sith stay what the spec already makes them: rare raid leaders.**
Jedi for the moisture farmers, Sith for the Empire.

⚠️ **Consequence for whoever builds it:** the xenotype (if we use one) must be
**unrecruitable and unbreedable by the player** — check that capture, recruitment
and gene extraction cannot route around this. That is the actual build work this
ruling creates, and it is easy to miss because the default is permissive.

**What the player CAN get:** the saber, the armour, the corpse, the story. Design
the loot so that beating one feels like the reward, because it is the only reward
there will ever be.
