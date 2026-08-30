# lee.theforce.lightsaber — black-box behavioral inventory

Prep for `FORCE_SYSTEM_OWNERSHIP_1` step 2. `infrastructure/state/items/FORCE_SYSTEM_OWNERSHIP_1.md`
does not exist yet (queue entry `infrastructure/state/queue/BENCH.md` still reads "no
items/FORCE_SYSTEM_OWNERSHIP_1.md yet") — this file is the evidence step 1 will need, not a
response to prose that hasn't been written.

**No decompilation used.** Sources: mod XML under the 1.6-active LoadFolders, the DLL's own
`AssemblyRef`/`TypeRef`/`TypeDef` metadata tables (parsed by hand, PE/CLI header walk — no
disassembly, no strings/grep on the binary), and a presence-only grep of the frozen world save.

## Where it lives

- Workshop folder: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3466124712`
  (packageId `lee.theforce.lightsaber`, confirmed by `About\About.xml`, matched by scanning
  every folder under `294100` for that packageId case-sensitively against the literal tag —
  two OTHER mods reference it as a dependency/load-after: `guy762.KotORWeapons`
  (`2938932438`) and `lee.theforce.factions` (`3557220783`); neither IS it.)
- `LoadFolders.xml` for `v1.6` loads `/`, `1.6`, then five conditional folders. With our
  current mod set (no KotOR Weapons, no Combat Extended, no MeleeAnimation, no
  `lee.theforce.standalone`) **only `/` (empty — no Defs at root) and `1.6/Defs` load.** The
  richest content — the 8 named lightsaber-form combat abilities — sits in
  `1.6\Mods\TheForce_Standalone\Defs\AbilityDef\LightsaberCombat.xml`, gated
  `IfModActive="lee.theforce.standalone,lee.theforce.standalone_steam"`, and is **inert in our
  current game** (that mod isn't installed/active). Treat that file's content as this mod's
  addon surface, not its base behavior.
- Assembly: `1.6\Assemblies\Lightsaber.dll`.

## XML-vs-C# split (sizes the re-implementation)

| Layer | XML-authorable (free re-skin) | C#-bound (must be reimplemented in our DLL) |
|---|---|---|
| **Lightsaber forms/stances** (7 canonical forms, Shii-Cho→Juyo) | Yes — one `HediffDef` (`Lightsaber_Stance`), 7 severity-gated `stages`, pure `statOffsets`/`capMods` (melee dmg/hit/dodge/cooldown factors, armor pen, a custom `Force_Lightsaber_Deflection` StatDef, optional psychic-entropy hooks under `MayRequireAnyOf`) | The hediff's `hediffClass` is `Lightsaber.Hediff_LightsaberDeflection` (C#) and the switching UI is `Comp_LightsaberStance`/`Gizmo_LightsaberStance`/`Dialog_LightsaberStance` (C#) — the *numbers* are XML, the *deflection mechanic and stance-switch gizmo* are C# |
| **Melee damage** | DamageDef entries (`Force_LightsaberCut`, `Force_SaberSlash/Stab[Sharp]`, `Force_BluntLightsaber`) are plain XML, `ParentName="CutBase"`/`"BluntBase"` | All route through `Lightsaber.DamageWorker_LightsaberCut` (C#) — a custom damage worker, not vanilla `DamageWorker_AddInjury`. Two Harmony patches (`Patch_DamageWorker_AddInjury`, `Patch_DamageWorker_LightsaberParry`) also touch damage resolution — **parry/deflection is a patch on the base damage pipeline, not a self-contained comp** |
| **Blade/weapon itself** | 9 weapon ThingDefs (Custom, Dual, Inquisitor [Biotech-gated], Curved, Shoto, Crossguard, Darksaber, Broadsaber, Ezra blaster-hybrid) — stats, recipes, textures all XML | Blade rendering/ignite state is `Comp_LightsaberBlade`/`CompProperties_LightsaberBlade` (C#); glow is `CompGlower_Options`/`Comp_GlowerProjectile` (C#); weapon draw/holster/orbiting visuals are a custom `PawnRenderNode_*` family (`_Orbiting`, `_AnimatedWeapon`, `_WeaponHolster`, `_PackWeapons` — all C#, all overriding the vanilla render-tree hook) |
| **Crafting** | `RecipeDef`s (`Force_CraftLightsaberSingle/Curved/Shoto/Dual/Crossguard/Broadsaber`, +2 VFE-gated) are plain XML on `Lightsaber_Crafting` abstract parent | Upgrade/repair flow is a real job: `JobDef Force_UpgradeLightsaber` → `JobDriver_UpgradeLightsaber` (C#); hilt-part and kyber-crystal color selection has three dedicated dialog windows (`Dialog_LightsaberCustomization`, `HiltPartSelectionWindow`, `StuffColorSelectionWindow` — all C#) |
| **Kyber crystals** | `Force_KyberCrystal`, `Force_SyntheticCrystal`, `Force_BledCrystal`, `Force_CleansedCrystal` (Sith-corruption / redemption crystal states) are plain ThingDefs; `GenStep_ScatterLightsaberCrystals` is XML-declared (mapgen genstep) | The genstep's placement logic and `ForceCrystal_Formations`/`CrystalMapGenerator` building defs are XML but the scatter *worker* and `CompColorCrystal` (the comp that actually recolors the blade from the socketed crystal) are C# |
| **Dueling** (practice ritual, raid-strategy champion duels) | `RitualPatternDef`/`PreceptDef`/`RitualBehaviorDef`/`RitualOutcomeEffectDef` for `LightsaberPracticeDuel` are XML, **but every one of them carries `MayRequire="Ludeon.RimWorld.Royalty,Ludeon.RimWorld.Ideology"` — this feature is DLC-gated and inert without both DLCs.** The one `AbilityDef` that would trigger it (`Force_LightsaberDuel`) is commented out in the shipped file — dueling currently has no in-game trigger even with both DLCs active except through the ritual UI directly. | `RitualBehavior_LightsaberDuel`, `RitualOutcomeEffectWorker_LightsaberDuel`, `RaidStrategyWorker_Duel` (a full alternate raid strategy — enemies challenge to a duel instead of assaulting), and a `LordJob_Duel`/`LordJob_Champion`/`LordToil_*` state-machine family are all C#. This is the single largest C#-bound subsystem in the mod |
| **8 named combat-form abilities** (Cho Mai/Mok/Sun, Sai Cha/Tok, Mou Kei, Sun Djerm, "LightsaberCombat") | AbilityDefs live entirely in the `TheForce_Standalone`-gated conditional folder (XML), each wired via `CompProperties_AbilityEffect.compClass = Lightsaber.Ability.CompAbilityEffect_Lightsaber*` and costed on two custom stats (`Force_AbilityForcePoolCost`, `Force_AbilityForceEXP`) that **belong to the sibling `lee.theforce.standalone` mod, not this one** | Each `CompAbilityEffect_Lightsaber*` (8 classes, one per form) is C#, shipped in *this* DLL but dormant — unreachable without the standalone mod's Force-pool/XP stat framework also being active |
| **Short-circuit malfunction** | `HediffDef Force_LightsaberShortCircuit` (disables `Violent` work tag, has a `HediffCompProperties_Effecter` state-effecter, self-clears in 350-450 ticks) is XML | **No XML trigger found anywhere in the Defs tree** — nothing gives this hediff on rain/water/EMP contact in any grep of the shipped files. The application condition is C#-bound and UNCERTAIN from XML alone (Comp_LightsaberBlade or a Harmony patch, not confirmed without IL disassembly, which was out of scope here) |
| **Traits** | 7 `TraitDef`s, one per form (`Force_FormI_ShiiCho` … `Force_FormVII` not directly enumerated but pattern holds), each a `degreeDatas`-based "Form Master" trait using `Class="SkillNeed_BaseBonus"` (C# class, but only as a data-driven `WorkGiver`/need modifier, not a novel mechanic) | Minimal — this is close to pure XML, the one custom class involved is a generic bonus-provider also used elsewhere in RimWorld modding |

## Verbs actually in play

- **Blade ignition, glow, holster/orbit rendering** — C#-bound (custom `PawnRenderNode` family).
- **Melee combat with a custom damage type and a Harmony-patched parry/deflection step** —
  C#-bound.
- **Stance/form switching** with 7 real stat-mechanical forms — XML numbers, C# switch
  mechanism.
- **Duels** (practice ritual + a full alternate raid strategy where NPCs challenge to single
  combat) — the deepest C# subsystem, and **DLC-gated** (Royalty + Ideology) in the shipped
  ritual defs.
- **Crafting/upgrading/recoloring** (hilt parts, kyber crystal, stuff color) — three custom
  dialog windows, all C#.
- **No general Force powers** (telekinesis, push, lightning, mind trick) are implemented in
  this mod. Every reference to a Force-power framework (`TheForce_Standalone.CompProperties_AbilityEffect_ForcePower`,
  the Force-pool/XP stats, `TheForce_Psycast.Lightsabers.ModExtension_LinkedSound`) is either
  `MayRequire`-gated to a sibling mod or, in the psycast-sound case, **commented out in the
  shipped XML**. This mod owns the *weapon*, not the *powers* — the "Force" in the powers
  sense is a different mod entirely (`lee.theforce.standalone`, referenced but not bundled;
  `TheForce_Psycast` similarly referenced, never bundled).
- **No XP/leveling system of its own** — `RequiredLevel`/Force-pool costs are consumed from,
  not defined by, this mod.

## jecstools verdict: NOT referenced — resolved from UNCERTAIN

The survey's flag is wrong (or has since been fixed upstream). Checked two ways:

1. **XML**: `grep -rli "jecstools\|jecrell"` across the entire mod folder (both `1.5` and
   `1.6` trees) hits exactly one file — the mod's own `About.xml`, and only inside
   `<loadAfter>` as a load-order hint (`jecrell.jecstools`, `jecrell.StarWarsTheForce`) — never
   a hard dependency, never an XPath target.
2. **DLL metadata** (`AssemblyRef` and `TypeRef` tables of `Lightsaber.dll`, parsed directly
   from the PE/CLI headers — no decompiler): the assembly references exactly nine external
   assemblies — `mscorlib`, `Assembly-CSharp`, `UnityEngine.CoreModule`,
   `UnityEngine.TextRenderingModule`, `System.Core`, `0Harmony`, `UnityEngine.AssetBundleModule`,
   `UnityEngine.IMGUIModule`, `System` — **no JecsTools assembly**, and its 540 `TypeRef` entries
   span only `RimWorld`, `RimWorld.Planet`, `Verse`, `Verse.AI`, `Verse.AI.Group`,
   `Verse.Sound`, `HarmonyLib`, `UnityEngine`, and base `System.*` namespaces — **no JecsTools
   namespace type is imported.**

Confidence: high (metadata-table read, not a string scan — the table walk resolves every row
correctly, verified by cross-checking the AssemblyRef list against the DLL's own declared
0Harmony/Unity dependencies, which match its known Harmony-patch behavior).

## Full C# class roster (192 types defined in Lightsaber.dll; below, the ~90 non-compiler-generated ones by role)

- **Comps/props**: `CompColorCrystal`+Properties, `CompGlower_Options`+Properties,
  `Comp_GlowerProjectile`, `Comp_LightsaberStance`+Properties, `Comp_LightsaberBlade`+Properties,
  `HediffComp_LaunchProjectile`+Properties, `CompCache`, `StatPart_EquippedStatOffsetIncrease`
- **Damage**: `DamageWorker_LightsaberCut`, `DamageDefExtension`
- **Hediffs**: `Hediff_LightsaberDeflection`
- **Jobs**: `JobDriver_AwaitDuel`, `JobDriver_GuardDuel`, `JobDriver_SaberLock`,
  `JobDriver_UpgradeLightsaber`, `JobGiver_AwaitDuel`, `JobGiver_GuardDuel`,
  `JobGiver_LiveDuel`, `JobGiver_LightsaberDuel`, `Job_UpgradeLightsaber`
- **Duel/Lord system**: `LordJob_Champion`, `LordJob_Duel`, `LordJob_Ritual_LightsaberDuel`,
  `LordToilData_GuardDuel`, `LordToil_DuelToil`, `LordToil_GuardDuel`,
  `LordToil_IdleBeforeDuel`, `LordToilLiveDuel`, `RaidStrategyWorker_Duel`,
  `RitualBehavior_LightsaberDuel`, `RitualOutcomeEffectWorker_LightsaberDuel`,
  `Trigger_HostilePawnNearby`, `Trigger_NewHostilePawnNearPoint`, `Trigger_ValidDuelistNear`,
  `Dueling_System.RitualRoleAnyHumanlike`
- **8 combat-form ability effects** (`Lightsaber.Ability` namespace): `CompAbilityEffect_LightsaberChoMai/ChoMok/ChoSun/Combat/MouKei/SaiCha/SaiTok/SunDjerm`
- **Rendering**: `PawnRenderNodeWorker_Orbiting`, `PawnRenderNode_Orbiting`+Properties,
  `PawnRenderNode_PackWeapons`, `PawnRenderNode_AnimatedWeapon`+Worker,
  `PawnRenderNode_WeaponHolster`+Properties+Worker, `LightsaberDrawer`, `Graphic_Hilts`,
  `LightsaberGraphicsUtil`, `LightsaberGlowShaderLoader`, `LightsaberShaderDef`,
  `ShaderPropertyIDAddon`
- **UI/dialogs**: `Dialog_LightsaberCustomization`, `HiltPartSelectionWindow`,
  `StuffColorSelectionWindow`, `Dialog_LightsaberStance`, `Gizmo_LightsaberStance`,
  `DialogOptions`
- **Harmony patches**: `HarmonyPatches`, `Pawn_DraftedPatch`,
  `PawnRenderUtility_CarryWeaponOpenly_Postfix[Ignition]`,
  `Pawn_EquipmentTracker_GetGizmos_Patch`, `Patch_Projectile_ImpactSomething`,
  `Patch_Thing_TrySpawnYield`, `MakeRecipeProducts_Patch`, `MakeSyntheticRecipeProducts_Patch`,
  `Patch_DamageWorker_AddInjury`, `Patch_DamageWorker_LightsaberParry`,
  `PawnRenderTree_Lightsaber_Patch`, `PawnRenderTree_RenderNodePatch`
- **Defs/data**: `HiltDef`, `HiltPartCategoryDef`, `HiltPartDef`, `HiltHediffList`,
  `HiltEffectors`, `LightsaberPresetDef`+`LightsaberPreset`, `LightsaberDefOf`,
  `LightsaberShaderDef`, `DefStanceAngles`, `StanceData`, `ModExtension_Conductive`,
  `ModExtension_LightsaberPresets`, `ModExtension_TraitColor`, `TraitDegreeColorData`,
  `DamageDefExtension`, `HiltManager`, `ForceLightsabers_ModSettings`, `TheForceLightsaber_Mod`
  (the Mod class itself, holds settings)
- **Also shipped but unused in our current 1.6 load**: `TheForce_Psycast.Lightsabers.ModExtension_LinkedSound`
  (only referenced from a commented-out block in `Lightsaber_Ignitions.xml`)

## World-save presence (scan-grade, presence-only, `grep` directly — no hook block hit)

`world/WORLDMAP_V1_original.rws` contains string occurrences of this mod's defNames:

| defName | occurrences |
|---|---|
| `lee.theforce.lightsaber` (packageId, presumably ModsConfig snapshot in the save) | 1 |
| `Force_Lightsaber_BuildYourOwn` | 5 |
| `Force_Lightsaber_Crossguard` | 5 |
| `Force_Lightsaber_Curved` | 5 |
| `Force_Lightsaber_Custom` | 5 |
| `Force_Lightsaber_Dual` | 5 |
| `Force_Lightsaber_Inquisitor` | 5 |
| `Force_Lightsaber_Shoto` | 5 |
| `Force_Lightsaber_UniqueAnakin` | 5 |
| `Force_Lightsaber_UniqueObi` | 5 |
| `Force_LightsaberWhipProjectile` | 1 |
| `Force_KyberCrystal` | 2 |
| `Force_Darksaber` | 5 |
| `Lightsaber_Stance` (the form hediff) | 0 |
| `LightsaberPracticeDuel` (the ritual) | 0 |
| `Force_Champion` (duel raid strategy) | 0 |

`Force_Lightsaber_UniqueAnakin`/`UniqueObi` are not defined anywhere in this mod's own Defs
tree — they trace to `guy762.KotORWeapons`'s bundled `AdditionalMods\_TheForceLightsabers`
compat folder, not to `lee.theforce.lightsaber` itself; flagged here only because they showed
up in the same save grep. **Interpretation, not measured**: several weapon ThingDefs are baked
into the frozen world (Ash'karr) — a re-implementation must ship def-name-compatible (or
save-migrated) replacements for at least those 9 defNames, or the frozen save will fail to
load. The stance hediff and the ritual/duel system show zero hits — nothing currently on the
map depends on those subsystems, which lowers the urgency of reimplementing dueling relative
to the weapon items themselves.

## Bottom line for sizing

Roughly a third of the mod (weapon stat blocks, recipes, the 7-stage stance numbers, kyber
crystal items, traits) is **free to re-author in pure XML**. The rest — custom damage
resolution, the full duel/raid-strategy/ritual state machine, all rendering (blade
glow/holster/orbit), all crafting/customization dialogs, and the malfunction hediff's actual
trigger — is **C#-bound and must be reimplemented** in our own assembly. The combat-form
ability classes are shipped but currently dormant (gated behind a mod we don't run). No
JecsTools dependency exists to inherit or route around.
