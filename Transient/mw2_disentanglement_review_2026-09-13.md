# MW2 disentanglement review — Armoury × ModularWeapons2

Design review for BENCH, 2026-09-13. Question: is `kaitorisenkou.ModularWeapons2` (MW2)
pointless inheritance the Armoury can shed, or load-bearing? Evidence is file:line / defName /
IL; nothing here was deployed, edited or loaded. Transient — shelf life ~14 days; the item that
acts on this is `ARMOURY_MW2_DEP_UNGATED_1` (filed, unassigned, no spec yet).

Paths: Armoury = `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/Armoury`. MW2 install =
`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3497834944`. Donor kotorcore
= `.../294100/3254370945` (`guy762.MM.KotORCore`, STILL ACTIVE in the live ModsConfig). Donor
KotOR Weapons = `.../294100/2938932438` (`guy762.KotORWeapons`, NOT active — absorbed).

---

## 1. SURFACE

### 1a. The 21 root-tag files (defs that are DISCARDED whole if MW2 is absent)

Census of `^  <ModularWeapons2.X` root tags across the 21 files: **207 `ModularPartsDef`** (+1
abstract base) and **44 `ModularPartsMountDef`**. Plus **61 `AbilityDef`s** inside the same files
whose `verbClass` is `ModularWeapons2.Verb_AbilityUseUBGL` (not a root tag, but MW2-only all the
same). The workbench is a 22nd file with an MW2 `thingClass`.

| group | files | parts | mounts | UBGL abilities |
|---|---|---|---|---|
| kotorcore `AdditionalMods/ModularWeapons2` absorption — `Defs/Absorbed_AdditionalMods/kotorcore/ModularWeapons2/` | 5 (`ModularPartDefs_ArmorBasic` 10, `ArmorHvyHatsRobes` 23, `MeleeBasic` 16, `RangedBasic` 14, `ModularPartsMountsBase` 1 abstract + 27 mounts) | 63 + base | 27 | 0 |
| KotOR Weapons absorption — `Defs/Absorbed_KotorWeapons/ModularPartDefs/` | 16 (`HelmetArmorTech` 21, `JetpackMissile` 4, `MeleeTools_*` ×7 @4 each = 28, `RangedVerbs_BowcasterSlugrifles` 11+3m, `LightHeavyRepeaters` 8+2m, `blasterDMG` 16+3m, `disruptorDMG` 15+3m, `ionDMG` 15+3m, `stunDMG` 15+3m, `Wristgun` 10) | 144 | 17 | 61 |
| workbench — `Defs/Absorbed_AdditionalMods/kotorcore/ModularWeapons2/Absorbed_Kotorcore_ModularWeapons2_Building_KotORGunsmithWorkbench.xml:16` | 1 | — | — | `thingClass=ModularWeapons2.Building_GunsmithStation` + its `WorkGiverDef KOTOR_WorkGiver_AratechWorkbench` |

Three sibling files in the same kotorcore folder are NOT MW2-typed but exist only for it:
`..._ThingDefs_UpgradeItems_{Ranged,Melee,Armor}.xml` (450+297+673 lines) — the physical
"upgrade item" ThingDefs (`guy762_scopeitem_accuracy`, `guy762_pcellitem_ion`, …) consumed by
`costList` in each part. Their abstract parent `guy762_upgradebase`
(`Defs/Absorbed_KotorCore/ThingDefs_Items/Absorbed_KotorCore_ThingDefs_UpgradeItemBases.xml:19-44`)
sets `recipeUsers = guy762_KotORWorkbench` and `thingCategories = guy762_weaponmod`.

**What a KotOR part actually is** (samples):

- **Ranged stat part** — `guy762_KotORpartScope_accuracy`
  (`..._ModularPartDefs_RangedBasic.xml:11-29`): `attachedTo guy762_KotORMount_scope`,
  `statOffsets` Mass +0.2, AccuracyTouch/Short/Medium/Long +0.10, `costList guy762_scopeitem_accuracy 1`.
  Siblings: crippling scope (+0.1 `RangedWeapon_DamageMultiplier`), holographic scope (+0.25
  touch/short accuracy, `verbPropsOffset warmupTime −0.2`), power cells, chambers, beam splitter/
  focuser, hair trigger. 14 parts, all `statOffsets`/`verbPropsOffset` only.
- **Ranged fire-mode part** — `guy762_KotORpartPCell_ioncharger`
  (`..._RangedVerbs_blasterDMG.xml:39-61`): Mass +0.4 and `effects.ability` →
  `AbilityDef guy762_MW2WeaponVerbAbility_ioncharger` (`:63-83`, `verbClass
  ModularWeapons2.Verb_AbilityUseUBGL`, 3-shot burst of `KotORBlasterBolt_ioncharger`,
  `maxCharges 1`, `replenishAfterCooldown`, cooldown 300 ticks). Same pattern ×61: power blast /
  sniper shot / rapid fire, each at basic/adv/master tiers per damage family. These are the
  "bounded alternate fire modes" `required_mods.md:723` already audited.
- **Melee part** — `guy762_KotORpartECell_ion_vblade`
  (`..._MeleeTools_Vibroblade.xml:20-67`): +0.3 `MeleeWeapon_AverageArmorPenetration`, and a
  replacement `tools` list (point Stab 22 / edge Cut 18, AP 0.25, +4 `guy762_MeleeDamage_ion`).
- **Armour part** — `Biorestorative underlay`, `Durasteel underlay` etc.
  (`..._ModularPartDefs_ArmorBasic.xml:12-201`): `statOffsets` on apparel (ArmorRating_Sharp +0.3,
  MoveSpeed −0.2, Insulation ±50, InjuryHealingFactor +0.3 …). `HelmetArmorTech` adds visors,
  gyro-stabilizers, exoskeleton, EVA verniers, knee micro-rockets.

**No KotOR part has art.** `grep -c texPath` over all 21 files = 0 in every parts file; the only
`graphicData` is on the abstract base `guy762_KotORModularPartBase` and it is `NullTex`
(`..._ModularPartsMountsBase.xml:199-203`). Contrast MW2's own parts: every `CommonParts_*.xml`
carries 5–12 `texPath`s. So on a KotOR weapon a part is invisible; it changes numbers and gizmos only.

### 1b. The 44 field-level files (defs SURVIVE without MW2, minus the MW2 fields)

`grep -rho 'ModularWeapons2\.[A-Za-z_]+'` over Armoury: **181 `CompProperties_ModularWeapon`**
blocks, **92 `Graphic_UniqueByComp`** graphicClass lines, 1 `Building_GunsmithStation`, 61
`Verb_AbilityUseUBGL`, 414/88 part/mount tag pairs.

- Weapons (25 files in `Defs/Absorbed_KotorWeapons/ThingDefs_Weapons/`): 92 concrete weapon defs
  carry the comp AND `Graphic_UniqueByComp`; ~44 sibling defs in the same files do not (the
  "NoQuality/non-moddable" tiers). Example `guy762_brifle_mandalorian`
  (`..._WeaponRanged_KotORBlasterRifle.xml:219-326`): `graphicData.graphicClass
  ModularWeapons2.Graphic_UniqueByComp` (`:227`); comp at `:302-324` = `baseGraphicData` (same
  texPath, `Graphic_Single`) + three `partsMounts` (`power_blasterDMG`, `chamber`,
  `trigger_blasterDMG`). Every one of these weapons has its own `<verbs>`/`<tools>` and
  `<statBases>` — verified by parsing all 181 comp-bearing concrete defs: **0** are missing both
  verbs/tools and an `<apparel>` block.
- Apparel (19 files): 89 armour/robe/helmet defs carry the comp (mounts `underlay`, `overlay`,
  `armortech`, `helmettech`, `visortech`) but keep their normal `graphicClass` (uniqgfx = 0 in
  every apparel file). Stat-only slots.
- Two gadgets are the exception — see §3a.

**What `CompProperties_ModularWeapon` adds** (fields from the DLL: `baseGraphicData`,
`autoStyledGraphic`, `partsMounts`, `defaultParts`): the slot list a gunsmith dialog offers, and
the runtime `CompModularWeapon` (101 methods) that applies part `statOffsets`/`statFactors`/
`equippedStatOffsets`, overrides `verbProperties`, merges melee `tools`, exposes the part
`ability` as a chargeable gizmo, and saves `attachedParts`.

**What `Graphic_UniqueByComp` does** (6 methods: `MatSingleFor`, `MatAt`, `GetColoredVersion`,
`TryGetAssigned`): per-Thing material = base texture composited with each attached part's
texture via a render camera (`MWCameraRenderer`). With KotOR parts all `NullTex`, its output is
pixel-identical to `Graphic_Single` on the same `texPath`. It buys nothing here.

### 1c. Where the dependency actually sits

- `About/About.xml` lists Harmony, kotorcore, VEF, AdaptiveStorage, EBSG, OuterRim core as
  `modDependencies` (`:39-64`) — MW2 nowhere; no `LoadFolders.xml` in the mod; only 8
  `MayRequire="kaitorisenkou…"` attributes exist, all in three kotorcore apparel files.
- The donor gates it: `3254370945/loadFolders.xml` v1.6 `<li IfModActive="kaitorisenkou.ModularWeapons2">1.6/AdditionalMods/ModularWeapons2</li>`.
  The donor's un-gated weapon defs (`2938932438`) DID hard-reference MW2 — that mod's About
  declared MW2 as a dependency (`design/Jawa/sw_ownership_survey.md:65`). We inherited the
  reference and dropped the declaration.
- `validation.py:43-57` already records this as a REAL dependency: on the min16 test list the
  MW2-typed defs are discarded and a surviving `recipeMaker` NREs the recipe generator.
- The deployed copy (`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Armoury`,
  files dated 2026-09-05) carries all 21 root-tag files and 41 of the 44 field-level files.
  kotorcore is also active and its gated MW2 folder defines the same 207 parts/44 mounts/
  workbench — the last `Player.log` shows zero duplicate-def lines naming `guy762`/`KotOR`
  (RimWorld's XML merge keeps the last loaded; Armoury loads after kotorcore).

---

## 2. EXERCISED?

Graded by what the player sees, not what the comp can do.

**2a. NPC weapons never carry parts — proven from IL and from the canonical save.**
`CompModularWeapon::Notify_Equipped` (IL_0013-002d): on first equip, if the owner is not
player-controlled → `RandomizePartsForPawn`. `RandomizePartsForPawn` (IL_000d-002d) draws from
`get_AvailableGunsmithPresets` (`GunsmithPresetDef`s matching the weapon) and **returns
immediately if there are none**. `grep -rl GunsmithPresetDef` over Armoury, kotorcore and the
KotOR Weapons donor: **zero presets** (MW2 ships exactly one, for its own `MW2_AssaultCarbine`).
Confirmed live: `CANONICAL_ASHKARR_START_2026-09-12.rws` holds 9 MW2-comp things (3
`guy762_vblade`, 3 `guy762_holdout`, 2 `guy762_bpistol`, 1 `guy762_bpistol_onasi` — Jawa
roster pawns draw `SWKotORWeaponCategoryTag_pistol`, `JawaFactionRoster.xml:739`) and **all 9
serialize `<attachedParts />` empty**. Raiders, traders and loot never show the player a modded
KotOR weapon. The passive path — the one that would make modularity "ambient" — is dead.

**2b. The active path exists but is long, unstocked, and ruled out by the owner.**
- Research: `guy762_ResearchKotOR_workbench` (donor
  `1.6/Defs/researchDefs/ResearchProjects_KotORWeapons.xml:251`, prereqs blasters+vibroweapons;
  our retag rewrites it to Industrial / baseCost 1600 —
  `src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag.xml:6106-6125`) → build the Aratech
  workbench (150 `KOTOR_AlloyDurasteel`, 10+5 components, 1 `KOTOR_UltraComponent`,
  `KOTOR_BuildTab`) → `guy762_ResearchKotOR_advupgrade` (`:267`, baseCost 4000, NOT retagged —
  0 hits in the retag patch) → craft upgrade items at the bench (3 components each,
  `recipeMaker` on `guy762_upgradebase`) → install via MW2's dialog. Reachable, five steps deep.
- Trade: the upgrade items' `tradeTags` (`guy762TT_weaponmod_basic` …) are stocked by exactly one
  TraderKindDef in the whole install — the donor's `_FactionsBase/Defs/TraderKind_JawaScavs.xml`,
  loaded only `IfModActive="guy762.KotORFactions"`, which is not active. **No live trader sells
  a part.** Nothing in `src/` references those tags either.
- Owner ruling: MW2 as a standalone is ❌ SKIP (`design/Jawa/mods/required_mods.md:728` —
  "off-theme … decline"), and the KotOR upgrade ladder was neutralised by the **standing
  no-self-upgrade policy** — *"I don't mind simply not upgrading things myself"* (`:723`, `:1551`).
  `:1549`: "ModularWeapons 2 is therefore in the stack as a *dependency*, not as an adoption
  choice". The design corpus has no line asking for weapon modularity; the armoury keeplist
  cuts MW2's own guns ("Metal Pipe / ModularWeapons 2 | 7 | conventional kinetics",
  `design/Jawa/mods/armoury_keeplist.md:73`), and the live Cherry Picker cuts
  `MW2_AssaultCarbine`, `MW2_BattleRifle`, `MW2_HuntingRifle`. The "Jawa are gunsmiths" line
  (`armoury_keeplist.md:130`) is about mines, repair and power cells, not attachments.

**2c. Catalogue depth, for the record.** Per weapon class the offer is real but small: a
blaster rifle has 3 slots (scope 4 options, chamber 4, beam/power/trigger 3–7 incl. fire modes);
a vibroblade 1–2 slots (edge, ecell 3–4 options); armour 2 slots (underlay 5, overlay 5).
Genuine numbers, no visuals, and nobody in the world ever equips them.

**2d. What MW2 costs the live game right now.** The last `Player.log` (2026-09-13 17:08,
12,541 lines): `[MW]patch failed : Patch_SMYHHandDrawer (2)` then `Error in static constructor
of ModularWeapons2.ModularWeapons2` (line 4685, `InvalidProgramException` in the Show Me Your
Hands transpiler) and **10** later `The type initializer for 'ModularWeapons2.ModularWeapons2'
threw an exception` — one of them inside `StatWorker.StatOffsetFromGear` under MW2's own
`Patch_StatOffsetFromGear` transpiler (line 11711-11714). That is the
`SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1` skew; SMYH is absent from the current `ModsConfig.xml`
(next load), but the exposure class remains: MW2's patch class has 51 methods including
transpilers/prefixes into SMYH, Yayo animation, Combat Extended, WeaponRacks, LTO groups and
vanilla `StatWorker`, `VerbTracker`, `Pawn_AbilityTracker`, reload jobs and equipment drawing
(`MW2Mod` detects six external assemblies). Every third-party update on that list is a
potential repeat.

**Verdict on "exercised": NO.** Not thin by intent — the donor built a real catalogue — but
thin in play: invisible parts, no NPC randomisation, no vendor, a five-step player path the
owner has said he will not walk.

---

## 3. LOSS ANALYSIS

### 3a. CUT — ship KotOR weapons as plain

Remove MW2 from the mod list; strip the comp blocks and swap `Graphic_UniqueByComp` →
`Graphic_Single`; delete the 21 root-tag files, the 3 UpgradeItems files, the workbench + its
WorkGiver; drop `recipeUsers`/`guy762_weaponmod` from `guy762_upgradebase` (or delete the base).

What the player loses:
- The Aratech workbench and the ability to install 207 parts. Never seen in play (§2).
- 61 fire-mode abilities. Never seen in play.
- **Two gadgets die outright** — the only defs where a part carries the function:
  - `guy762_wristlauncher` (`Defs/Absorbed_KotorWeapons/ThingDefs_Gadgets/..._KotORModularWristLauncher.xml`): apparel, **no verbs/tools of its own**; its whole function is the 10 `Wristgun` parts' abilities, and its `defaultParts` entry is `MayRequire="guy762.KotORDroids"` (`:92-97`). Without MW2 it is an inert belt. Delete it.
  - `guy762_jetpack_missile` (`..._KotORMissileLauncherJetpack.xml`): keeps its own `Verb_Jump` (`:93-99`) and `CompProperties_ApparelReloadable`; loses the `guy762_KotORpartJetpackMissile_highex` default part (`:126-131`) = the missile. Keep as a jump-only jetpack or delete.
- Bowcaster `defaultParts` (`..._KotORBowcaster.xml:225-230`, `:589-594`) add a charge ability on top of the weapon's own verbs — cosmetic loss.
- Weapon descriptions still say "UPGRADE SLOTS: …" (e.g. `..._KotORBlasterRifle.xml:222`) — a text scrub, optional.

What does NOT break: every weapon and armour piece keeps its own verbs, tools, statBases, art
(the base texPath is the same one `baseGraphicData` names). No stat lives only in a part
(verified: all mounts `allowEmpty true`; the only `defaultParts` are the three above).

Side effects to handle: the 9 saved comp blocks in the canonical start save become orphan XML
(`<attachedParts />`, `<attachHelpers />` … ×9) → Scribe warnings on first load, gone on
resave. The retag rows for `guy762_ResearchKotOR_workbench` / `_exupgrade`
(`RUT_ResearchRetag.xml:5714`, `:6106`) become dead research rows until kotorcore retires (or
Cherry Pick the three research defs now, as the 26 other `guy762_ResearchKotOR_*` cuts already
are). kotorcore's own MW2 folder simply stops loading (`IfModActive`), so no duplicate risk.
`validation.py`'s min16 note inverts. The absorption generators
(`Source/gen_kotorweapons_absorption.py`, `gen_additionalmods_absorption.py`) must do the strip,
not a hand edit of generated files.

### 3b. DIY — reimplement a minimal modular system in `RimMandrake.StarWars.*`

See §4 for scope. Loss vs MW2: presets, decals, tac devices, per-part art, the save/load
preset dialogs, CE/Yayo/SMYH integrations — none used by KotOR content. Gain: no third-party
transpiler exposure. Cost: we own the same fragile hooks MW2 owns today.

### 3c. GATE — keep MW2, declare and gate it (`ARMOURY_MW2_DEP_UNGATED_1` as filed)

Add `kaitorisenkou.ModularWeapons2` to `modDependencies` + `loadAfter`; move the 21 root-tag
files + 3 UpgradeItems + workbench into a `LoadFolders.xml` folder gated
`IfModActive="kaitorisenkou.ModularWeapons2"`; put `MayRequire` on the 181 comp `<li>`s. The 92
`graphicClass` lines cannot be `MayRequire`d (a field, not a node) — they stay hard, meaning the
mod is still not MW2-optional, only honestly declared. Loses nothing, keeps everything in §2d.
Also keeps `MW_GunsmithStation` (MW2's own bench, research-gated in its `Building.xml:73`, not in
the live Cherry Picker) as an off-theme build entry.

---

## 4. REIMPLEMENTATION SCOPE (for 3b)

MW2 DLL measured with ilprobe (`meta_core.py` repointed at
`3497834944/1.6/Assemblies/ModularWeapons2.dll`, 139,264 bytes): **93 type rows, 644 methods,
445 fields.** Load-bearing types: `CompModularWeapon` 101 methods / 29 fields;
`Dialog_Gunsmith` 27 / 46; `ModularWeapons2` (Harmony patches) 51 methods;
`MountAdapterClass` 19; `MW2Mod` 19; `ModularPartsDef` 14 / 11; `MWCameraRenderer` 12;
`Graphic_UniqueByComp` 6; `Verb_AbilityUseUBGL` 6; `Building_GunsmithStation` 3 (a float-menu
hook); plus `JobDriver_UseGunsmithStation`, `JobDriver_ConsumeIngredientsForGunsmith`,
`MWAbilityProperties`, `ModularPartEffects`, `VerbPropsOffset`, `GunsmithPresetDef`,
`MWDecalDef`, `MWTacDevice*`, three save/load/rename dialogs.

A KotOR-sufficient subset (no art, no decals, no tac devices, no presets, no CE/Yayo/SMYH):

| replace | with | why it is not small |
|---|---|---|
| `ModularPartsDef`, `ModularPartsMountDef`, `ModularPartEffects`, `VerbPropsOffset`, `MWAbilityProperties` | 5 Def/data classes | mechanical, ~300 lines |
| `CompProperties_ModularWeapon` + `CompModularWeapon` | comp holding attached parts, exposing stat offsets/factors, equipped offsets, verb-props override, merged melee tools, one chargeable ability, Scribe | the verb override needs a `VerbTracker`/`IVerbOwner` shim and patches on `Pawn_MeleeVerbs`, `CompEquippable.VerbProperties`, `StatWorker.StatOffsetFromGear`/`GearHasCompsThatAffectStat`, `Pawn_AbilityTracker` (temporary abilities), `ReloadableUtility`/`JobDriver_Reload` — the exact hooks MW2 patches (`Patch_MeleeVerbs`, `Postfix_CompEqVerbProperties`, `Patch_StatOffsetFromGear`, `Patch_AbilityTracker`, `Patch_JobReload`, `Patch_ReloadableUtil`). ~1,200-1,800 lines + 6-8 Harmony patches |
| `Verb_AbilityUseUBGL` | verb that fires the weapon's projectile through an ability | ~100 lines |
| `Building_GunsmithStation`, `JobDriver_UseGunsmithStation`, `JobDriver_ConsumeIngredients…`, `Dialog_Gunsmith` | bench float menu, job, a plain install/remove dialog consuming upgrade items | ~600-900 lines; the dialog is the bulk |
| `Graphic_UniqueByComp`, `MWCameraRenderer` | nothing (KotOR parts have no art) | 0 |
| 21 def files | rewritten to `RimMandrake.StarWars.Armoury.*` root tags | generator change |

Realistic total 2,000-3,500 lines of C#, 1-2 weeks including a test bench, for a feature with
no design demand and no in-play exposure. The patch surface (`StatWorker`, `VerbTracker`,
`AbilityTracker`) is the same one six other active transpilers already fight over
(`Player.log:11716-11721`), so this does not remove the fragility, it relocates it to us.

---

## 5. VERDICT + EFFORT

**Primary recommendation: CUT (3a).** The owner's hypothesis holds, and it holds for a stronger
reason than "inherited": MW2 modularity is not merely unwanted, it is **unreachable in play**.
No NPC ever spawns with a part (zero `GunsmithPresetDef`s, `RandomizePartsForPawn` returns at
IL_002d, 9/9 saved comps empty), no trader stocks one, no part has a sprite, and the owner has
ruled he will not upgrade. What remains is 181 comp blocks, 207 invisible parts and a bench
nobody builds — carried by a 139 KB DLL whose static constructor is currently failing in the live
log and whose 51 patch methods transpile five other mods. Cutting it loses two hero gadgets that
were never in a Jawa roster and a set of fire-mode gizmos no one has seen. Gating (3c) is the
honest minimum if the cut is refused, but it keeps every risk and buys only a declared line in
About.xml. DIY (3b) reimplements a system the design does not ask for.

| option | effort | what breaks |
|---|---|---|
| **3a CUT** | **1-2 FOUNDRY days**: generator strip pass (181 comps, 92 graphicClass, delete 21+3+1 files, 2 gadget decisions, description scrub), Cherry Pick or retag-drop 3 research rows, remove MW2 from `ModsConfig.xml`, invert `validation.py`'s min16 note, min-list load + one 15-min cold load, resave canonical start | wrist launcher (delete), jetpack missile (jump stays), 61 fire modes, all armour/weapon parts, Aratech bench; 9 orphan comp blocks in the start save (warnings until resave) |
| 3b DIY | 1-2 weeks: ~2-3.5k lines C# + 6-8 Harmony patches + 21 files re-rooted + live test | same fragile hooks now ours; save format of `attachedParts` changes (resave) |
| 3c GATE | 1-3 hours: About.xml deps/loadAfter, `LoadFolders.xml` gate folder, `MayRequire` on 181 `<li>`s | nothing now; keeps the SMYH-class skew, 10 stat exceptions per session in the current log, `MW_GunsmithStation` in the build menu; still not truly MW2-optional (92 hard `graphicClass` fields) |

**Single most important evidence:** `CompModularWeapon::RandomizePartsForPawn` returns at IL_002d
when `AvailableGunsmithPresets` is empty, and there is no `GunsmithPresetDef` for any KotOR
weapon anywhere on disk — so the only way a modded weapon exists is the player building one
by hand, which the owner ruled out on 2026-08-03. Corroborated by 9/9 `<attachedParts />` in
`CANONICAL_ASHKARR_START_2026-09-12.rws`.

**UNKNOWN — one in-game check would settle "exercised today" beyond doubt (the verdict does not
hinge on it):** with MW2's static constructor throwing (last log), does the Aratech bench's
right-click "customize" (`Building_GunsmithStation.GetFloatMenuOptions` → `Dialog_Gunsmith`)
even open on a KotOR blaster? Dev-spawn `guy762_KotORWorkbench` + a pawn holding
`guy762_brifle`, right-click the bench. If it throws, MW2 is dead weight already; if it opens,
it is a working feature nobody uses.

**Owner input needed:** whether the `guy762_wristlauncher` and the jetpack's missile are worth
keeping (they are the only content that *dies* rather than degrades). If neither is wanted,
the cut has no player-visible cost at all.
