> **LIVE-DATA OVERRIDE:** `mods/live_mod_inventory.md` (generated 2026-08-09 from the machine) is authoritative for mod identity — existence, Workshop IDs, packageIds, versions. This file keeps the reasoning only. "Faction Filter" never existed; the live equivalents are **Sensible Factions** (3531306011) and **Faction Control** (2882785581).

# Outer Rim → Custom 1.6 Sub-Mod — CHERRY-PICK DEF LIST (Task A)

**Purpose:** the concrete shopping list of which donor defs to lift from the 1.4/1.5 Outer Rim faction modules into a single custom 1.6 sub-mod, plus what each depends on. Follows the triage (`sw_ingredients_inventory.md` ⭐ TRIAGE section): content is ~99% pure XML and the class/base defs it needs already ship in **Outer Rim Core 1.6** and **Droid Depot 1.6** (both installed).

**All defNames below are SRC-verified 2026-08-06** from the extracted mods in `mod_sources/` (not guessed).

---

## 0. The load-bearing fact that makes this cheap

Every donor weapon parents off a **`OuterRimBlasterBase_*`** base (Projectile/Rifle/Pistol/SniperRifle/HeavyWeapon) and uses vanilla **`Verb_Shoot`** — and those base defs live in **Core 1.6** (`grep`-confirmed: `Name="OuterRimBlasterBase_Projectile"` etc.). The **entire turret/laser-cannon line is already in Core 1.6** (`Turrets_01_Light` / `_02_Medium` / `_03_Heavy`, with `researchPrerequisites` = player-buildable). The training-hediff class **`OuterRimCore.Hediff_Training`** + `DefModExt_TrainingCurve` are in Core 1.6. So the sub-mod is mostly: **copy the faction-specific pawnkinds/weapons/apparel XML, keep their `ParentName`/`hediffClass` pointers, and let them resolve against Core 1.6 at load.**

**Hard dependency the sub-mod must declare:** `Neronix17.OuterRim.Core` (1.6). For droid content also `Neronix17.OuterRim.DroidDepot` + `Neronix17.Asimov`. For the VGE gene refs (Republic clones, if adopted) `VanillaGenesExpanded`. Galactic Diversity (bodies) is already in the stack.

---

## 1. GALACTIC EMPIRE — the primary prize (all pure XML, class-free)

**Trooper ladder (PawnKindDefs — lift all, they map to our Act I→III escalation):**
`OuterRim_ImperialArmyTrooper` → `OuterRim_ImperialArmyHeavy` → `OuterRim_ImperialArmyOfficer` → `OuterRim_ImperialArmyCommander` (grey-conscript line); `OuterRim_ImpStormtrooper` (+ `_Desert` ⭐ desert-world fit, `_Snow`, `_Officer`) → `OuterRim_ImpStormScout` / `OuterRim_ImpStormJump` / `OuterRim_ImpStormIncinerator` / `OuterRim_ImpStormArty` → `OuterRim_ImpStormCommander` → `OuterRim_ImpDeathTrooper` → `OuterRim_ImpISBAgent`; support `OuterRim_ImperialGunner`, `OuterRim_ImperialOfficer`. (Skip `OuterRim_ImperialTrader` unless we want Empire caravans.)

**Training hediffs (⭐ pillar-perfect — "elite = earned XP, not stat inflation"):**
`OuterRim_StormtrooperTraining`, `OuterRim_DeathTrooperTraining`, `OuterRim_ISBTraining`. **Dependency:** `hediffClass=OuterRimCore.Hediff_Training` + `DefModExt_TrainingCurve` → both in Core 1.6. Lift XML as-is.
- *Balance note (§19.5):* the cadet stage carries a big NEGATIVE ShootingAccuracy offset that climbs to elite with kills — this is a self-correcting anti-exponential curve; keep it, it's exactly the mechanic we want.

**Blaster library (weapons — all parent off Core bases, `Verb_Shoot`):**
`OuterRim_E11BlasterRifle`, `OuterRim_E11DBlasterRifle`, `OuterRim_E10BlasterRifle`, `OuterRim_E22BlasterRifle`, `OuterRim_DLT19HeavyBlasterRifle`, `OuterRim_DLT19XTargetingBlaster`, `OuterRim_DLT20ABlaster`, `OuterRim_EC17Blaster`, `OuterRim_SE14RBlaster`, `OuterRim_TL50HeavyRepeaterBlaster`, `OuterRim_D72wOppressor` (flame). (Each has a paired `OuterRim_Bullet_*` — lift the bullets too.)

**Apparel (per-tier armor + insignia — lift the sets you field):**
Army: `OuterRim_ImperialArmyUniform/Cuirass/Helmet/Cap/Pauldrons`, `OuterRim_ImperialCadetUniform/Helmet(+Alt)`. Storm: `OuterRim_StormtrooperCuirass/Helmet/Pauldrons` (+ `_Specialist`, `_Pride` optional, pauldron insignia `_Enlisted/_Sergeant/_Officer/_Commander/_Artillery`), `OuterRim_StormtrooperKama`. Specialists: `OuterRim_ScoutTrooper*`, `OuterRim_Snowtrooper*`, `OuterRim_RangeTrooper*`, `OuterRim_DeathTrooper*`, `OuterRim_ISBAgent*`. Officer: `OuterRim_ImperialOfficerUniform/Cap` (+ `_Black`/`_White`). Mobility: `OuterRim_ImperialJetpack(+Jump)`, `OuterRim_ImperialJumpsuit`, `OuterRim_ImperialGunnerHelmet`.

**Scenario/starting defs to SKIP:** `KCSG.ScenPart_AddStartingStructure` refs + `PawnKindDefs_Player/` — those are for playing *as* the Empire; we want them as an NPC faction. Drop the player scenario, keep the NPC pawnkinds.

---

## 2. SEPARATISTS — droid-swarm ladder (pure XML, no code)

**PawnKinds (clean donor for our Free Droid Enclaves / any hostile droid faction):**
`OuterRim_Sep_B1Droid` → `OuterRim_Sep_B2Droid` → `OuterRim_Sep_BXDroid` → `OuterRim_Sep_TacticalDroid` → `OuterRim_Sep_SuperTactical` → `OuterRim_Sep_DestroyerDroid` (droideka) → `OuterRim_Sep_CrabDroid`; `OuterRim_Sep_General`. (Skip `_Trader` unless wanted.)
**Weapons:** `OuterRim_E5Blaster`, `OuterRim_E5sSniperRifle`, `OuterRim_RG4DBlaster`, `OuterRim_BXVibroblade`.
**Building:** `OuterRim_HypertechFabricator_Seperatist` (droid-forge flavor — good for a Geonosian/foundry aesthetic).
**Dependency note:** Separatist droid pawnkinds may reference `Asimov.*` (droid framework) via Droid Depot — confirm the droid `raceDef` resolves; if these are Droid Depot automatons, declare that dep. [confirm at authoring]

---

## 3. OLD REPUBLIC — Sith-elite donor (pure XML, no code)

We're not fielding the Old Republic as a faction, but its **Sith** pawnkinds/apparel are the donor for the **Empire Sith-elite ranks** (per the Force ruling: dark-side → Empire Sith-race elite only).
**PawnKinds:** `OuterRim_SithTrooper`, `OuterRim_SithCaptain`, `OuterRim_SithCommander`, `OuterRim_SithIncinerator`, `OuterRim_SithEmpireOfficer`. (Republic-side `OuterRim_OldRepublic*` = ignore unless we want a Republic faction.)
**Weapons:** `OuterRim_SithBlaster/Rifle/HeavyRifle/Sniper/FlameProjector`.
**Apparel:** `OuterRim_SithTrooperCuirass/Helmet/Pauldrons`, `OuterRim_SithOfficerUniform/Cap`.
*Use:* reskin/relabel to taste (general tweak license) and attach as fixed loadouts to Empire Sith-elite pawnkinds via Sensible Factions (3531306011) / Faction Control (2882785581).

---

## 4. MANDALORE — heraldry + weapons easy; vehicles + Honour Raid = the only real work

**⭐ 16-clan heraldry apparel (ready-made heraldry system — pure XML):**
Helmets: `OuterRim_MandalorianHelmet_{Traditional,Simple,Heavy,NeoCrusader,RetroCrusader,NiteOwl(+Alt),Maul,Imperial,Executioner,Armorer,Powertech,Pilot,Tooka}`. Chest: `OuterRim_MandalorianChest_{Traditional,Simple,Heavy,NeoCrusader,NiteOwl}`. Pauldrons: `OuterRim_MandalorianPauldrons_{Traditional,Simple,Heavy,NeoCrusader,NiteOwl}`. Jetpacks: `OuterRim_SupercommandoJetpack(+Jump)`, `OuterRim_Z6Jetpack(+Jump)`.
**Weapons:** `OuterRim_AmbanSniperRifle`, `OuterRim_WESTAR18/34/35Blaster`, `OuterRim_EE3BlasterCarbine`, `OuterRim_EE13BlasterPistol/Rifle/SniperRifle`, `OuterRim_GALAAR15Blaster`, `OuterRim_IB94BlasterPistol`; melee `OuterRim_MandalorianHammer/Warhammer/Hookblade/Saber`, `OuterRim_MunitkatHalberd`.
**PawnKinds:** `OuterRim_DeathWatch_Trooper/Officer/Leader` (skip `_Trader`).
**⚠️ The two real work items (only if wanted):**
- **`IncidentWorker_HonourRaid`** (135-line C#) — the allied-Mando "Honour Raid" incident. Self-contained port if we want that verb; otherwise omit and Mandos raid normally.
- **Vehicle defs** reference `Vehicles.*` + `SmashTools.*` (Vehicle Framework, separate dep). Mando flyers/launch. **Recommend: drop the vehicle defs** (we already made vehicle decisions separately) — the faction/weapon/heraldry XML works fine without them.

---

## 5. TURRETS / HEAVY WEAPONS — ALREADY IN CORE 1.6, no port at all

The whole laser-cannon line is live in Core 1.6 and player-buildable (has `researchPrerequisites`): light `OuterRim_LightLaserCannon_{Corellia,Coruscant,Tatooine}` + `OuterRim_LightIonCannon` + `OuterRim_PTowerTurret`; medium `OuterRim_MediumLaserCannon` + `OuterRim_Turbolaser` + `OuterRim_ProtonMortar`; heavy `OuterRim_HeavyLaserCannon` + `OuterRim_HeavyTurbolaser` + `OuterRim_HeavyIonCannon` + `OuterRim_HeavyImperialTurbolaser` + `OuterRim_ProtonArtillery` + `OuterRim_AnaxesTurret`. **Action: none — just enable via research.** (§19.5 balance audit of these vs vanilla is a separate open item if we let the player build them.)

---

## 6. RESTRAINT BOLT — already in Droid Depot 1.6

Droid-control mechanic (synergizes with the Jawa "recycle Empire droids → DroidBrains" verb) ships in Droid Depot 1.6: `JobDriver_RestrainDroid` + `Recipe_RemoveBolt` (C#, 1.6). **Action: none — use as-is; also serves as the JobDriver/Recipe template shape for the Carbonite Trophy freeze/thaw bills (Task B).**

---

## Collision / integration checklist (do at authoring, before load)
1. **defName collisions:** since we're reusing the `OuterRim_*` prefix from live Core/Droid Depot, our sub-mod must NOT redefine any defName that already exists in Core 1.6 (e.g. don't re-declare `OuterRimBlasterBase_*`). Lift only the faction-specific pawnkinds/weapons/apparel/hediffs; reference (don't copy) Core bases.
2. **`ParentName` resolution:** confirm each lifted weapon's `ParentName` (e.g. `OuterRimBlasterBase_Projectile`) resolves against Core 1.6 at load (it should — same author, same names).
3. **Texture paths:** the donor mods carry their own `Textures/` — copy the referenced texture folders alongside the defs, or the items load pink.
4. **Faction attachment:** attach these pawnkinds to our authored factions via `pawnGroupMakers` + Sensible Factions (3531306011) / Faction Control (2882785581) (per faction_authoring_mechanism.md), NOT by shipping the donor FactionDefs (which we're re-authoring anyway).
5. **Apply the §19.5 balance pass + anti-exponential review in the same lift** (damage/armor vs vanilla) — cleaner than patching later.
6. **Load-order:** sub-mod loads AFTER Core, Droid Depot, Galactic Diversity, VGE.

## Recommended build order
Empire trooper ladder + blasters + apparel + training hediffs (biggest payoff, zero code) → Sith-elite donor set → Separatist droids → Mandalore heraldry/weapons → (optional) Honour Raid port. Turrets + restraint bolt need no work.
