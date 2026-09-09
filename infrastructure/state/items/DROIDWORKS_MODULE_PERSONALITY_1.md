# DROIDWORKS_MODULE_PERSONALITY_1 (packet E3)

Installed modules carry attitudes: `CompModulePersonality` trait-hediffs while worn.
`after: B2` (`DROIDWORKS_MODULE_ABSORB_1`, closed this session, sha `29bc5235`).
Design source: `design/Jawa/droid_system_build_spec.md` unit 12 ("Module
personality: apparel comp granting trait-equivalent hediffs while worn (the
spider-arm changes who you are)" — ThingComp, KotOR slots + ours, size S) and
`design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5 row E3. No §7
contradiction/supersession note names E3 specifically.

## spec

1. A `ThingComp` on a module `ThingDef` adds a personality `HediffDef` to the
   wearer on `Notify_Equipped`, removes it on `Notify_Unequipped`. No Harmony:
   `ThingWithComps.Notify_Equipped/Unequipped` already forwards to every comp
   on worn apparel (confirmed by reading `Verse/ThingWithComps.cs` and
   `RimWorld/Pawn_ApparelTracker.cs` via RimSage — `Pawn_ApparelTracker.
   Notify_ApparelAdded/Removed` call `apparel.Notify_Equipped/Unequipped`,
   which `ThingWithComps` forwards to every `ThingComp`, base class method
   confirmed via `read_csharp_symbol ThingComp`).
2. Mechanism is a Hediff, not a `TraitDef`: vanilla traits are baked in at
   pawn generation with no clean runtime add/remove API; a Hediff already has
   one, and this mod's own house convention (`Effects_Droidworks.xml`,
   packet B4a) already expresses "personality" as stat/capacity-offset
   hediffs.
3. Scope: 3 modules (one per absorbed slot family — hardware, sensor,
   software), not all six KotOR slots, matching unit 12's own "S" size
   estimate.
4. **No literal "spider-arm" module exists.** Grepped every absorbed KotOR
   module (`Absorbed_KotorDroidModules_{Tech,Armor,Bases}.xml` +
   `_EXCLUDED_manifest.txt`) for spider/arm/manipulator/limb — nothing.
   `DROIDWORKS_MODULE_ABSORB_1` absorbed only the hardware/software/sensor
   slots; weapon/gadget/shield (where an arm-mounted device would plausibly
   have lived) were excluded there for framework-dependency reasons (MVCF/
   SelfHediffVerb, neither shipped by Droidworks). **Substitution recorded**:
   `RSW_DW_Module_DroidHardware_agility` ("droid agility upgrade... ties
   directly into a droid's motivators... increase their reaction time") is
   the closest analogue — a hardware-slot actuator/limb-motion module, same
   family as a manipulator arm.

## Built

- `src/RimStarWars/Droidworks/Source/Droidworks/CompModulePersonality.cs` —
  `CompProperties_ModulePersonality` (field: `personalityHediff`) +
  `CompModulePersonality : ThingComp`. `Notify_Equipped` adds the hediff if
  not already present (duplicate guard); `Notify_Unequipped` removes it if
  present. Added to `Droidworks.csproj`'s explicit `<Compile Include>` list.
- `src/RimStarWars/Droidworks/Defs/HediffDefs/Effects_Droidworks_ModulePersonality.xml`
  — 3 `HediffWithComps` defs, same shape as `Effects_Droidworks.xml`
  (`scenarioCanAdd false`, `maxSeverity 1.0`, one stat/capMod stage each):
  - `RSW_DW_ModulePersonality_Twitchy` — "twitchy", `MeleeDodgeChance +0.05`.
    Granted by the spider-arm substitute (`DroidHardware_agility`).
  - `RSW_DW_ModulePersonality_Paranoid` — "hyperaware", `Sight capMod +0.05`.
    Granted by `RSW_DW_Module_DroidSensor_perception` (top-tier sensor).
  - `RSW_DW_ModulePersonality_Pedantic` — "pedantic", `GlobalLearningFactor
    +0.05`. Granted by `RSW_DW_Module_DroidSoftware_lockout`.
  Each offset is a stat/capacity the module's own `equippedStatOffsets`
  does NOT already touch, so the personality effect is visibly attributable
  to the new hediff rather than doubling an existing number.
- `src/RimStarWars/Droidworks/Patches/ModulePersonality_Wiring.xml` — wires
  `CompProperties_ModulePersonality` onto the 3 chosen absorbed-module
  `ThingDef`s via `PatchOperationAdd`, rather than hand-editing the
  generator-owned `Absorbed_KotorDroidModules_*.xml` files. Two targets
  already had a `<comps>` list (append); `RSW_DW_Module_DroidSoftware_lockout`
  had none, so that operation targets the `ThingDef` node itself and adds a
  whole new `<comps>` block (an xpath into a nonexistent `<comps>` would have
  matched nothing and logged nothing — checked before writing the patch).
- Rebuilt `Droidworks.dll`: **0 warnings, 0 errors**
  (`"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build
  'D:\Luke\dev\Rimworld\src\RimStarWars\Droidworks\Source\Droidworks\Droidworks.csproj'
  -c Release`). Checked `git status`/`git log` for the parallel D2 agent's
  csproj/DLL changes before building — none at that time (D2 does not touch
  Droidworks C#, per its own briefing).

## verify

- `validate_patch.py` on the two new files, `--defs` Data + Mods + workshop
  294100 + `src/RimStarWars/Droidworks`: **0 errors, 3 warnings** (all 3:
  "not wrapped in PatchOperationFindMod/Conditional" — advisory and not
  applicable here, since the patch targets this mod's OWN defs, not a
  donor mod's; it can only ever run inside Droidworks itself). All 3
  `PatchOperationAdd` xpaths matched exactly 1 element each — confirmed live,
  not assumed.
- Live "wear spider-arm → trait; remove → gone" quicktest: **NOT DONE.**
  `rimflow bridge who` showed the bridge held by the parallel FOUNDRY
  subagent (`D2 DROID_RETIRE_KOTORDROIDS_1 cold load confirmation`, holder
  since 2026-09-09T00:03:30Z, repeatedly re-checked as still active/idle
  under the 45-minute staleness threshold) for the whole build window.
  `./game` (bare, measuring only) showed RimWorldWin64 actually running.
  Did not take the bridge, did not kill the game, did not deploy
  (`deploy_custom_mods.py --mod Droidworks` plan-only showed drift beyond
  this packet's own files — other in-flight changes to
  `PawnKinds_Primitive.xml` / `DataSpikes_Droidworks.xml` — so `--apply`
  would have pushed a mix of this packet and another agent's unrelated,
  possibly-mid-edit work into the live game folder while its own cold load
  was in progress).
- **Owed**: once the bridge frees and the full-list game is down, deploy
  Droidworks (defs+patch+DLL), spawn a droid, `Wear apparel (selected)...`
  the substitute module (`RSW_DW_Module_DroidHardware_agility`) via the
  rimbridge skill's debug-action pattern, `jawa/pawn_health` confirms
  `RSW_DW_ModulePersonality_Twitchy` present, unequip, confirm gone. Repeat
  for the other two if time allows — the mechanism is identical per-module
  (same comp, same vanilla `Notify_Equipped/Unequipped` hook), so one clean
  pass is sufficient proof of the class; the other two are XML wiring only.

## Assumptions/judgment calls

- **Mechanism**: Hediff via a custom `ThingComp`, not a `TraitDef` add/remove
  and not vanilla's own `CompCauseHediff_Apparel` +
  `HediffCompProperties_RemoveIfApparelDropped` (which already exists and is
  already used on 8 of this mod's own absorbed modules for their stat/
  capacity hediffs, and would have worked identically here with zero new
  C#). Built a distinct named class anyway because the packet's own
  `outputs` column in `DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5 names
  `CompModulePersonality` explicitly, and because keeping "this is a
  personality effect" as a separate, explicitly-named comp from "this is
  the module's raw stat/capacity effect" reads better going forward when a
  later packet (E1/E2, currently unbuilt) wants to reason about personality
  sources specifically. Recorded so a reviewer doesn't mistake this for not
  having noticed the existing vanilla equivalent.
- **Spider-arm substitution**: `RSW_DW_Module_DroidHardware_agility`, per
  the "no literal spider-arm module exists" finding above. If a real
  spider-arm/manipulator module is absorbed later (e.g. if the weapon/
  gadget slot exclusion in `DROIDWORKS_MODULE_ABSORB_1` is ever revisited),
  re-point `RSW_DW_ModulePersonality_Twitchy`'s wiring onto it instead.
- **Which 3 modules / which hediffs**: judgment call, thematically fitted —
  see Built section. Not all 6 KotOR slots: armor modules (the 6th absorbed
  category) were skipped as pure stat-block variants with no "identity"
  flavor text to hang a personality on; the 3 chosen each had descriptive
  text the personality hediff could read as of a piece with.
- **Provenance note, for the record**: this packet's 4 new/changed files
  (`CompModulePersonality.cs`, `Effects_Droidworks_ModulePersonality.xml`,
  `Patches/ModulePersonality_Wiring.xml`, the `Droidworks.csproj` edit) were
  found already committed — under a concurrent agent's unrelated commit
  `0f7da95c` ("Sprint wave B: Armoury extractions...") — by the time this
  item file was written, rather than in a dedicated commit of their own.
  Content matches exactly what is described above (diffed against
  `0f7da95c` before writing this note) and is already pushed
  (`origin/main == HEAD` at the time of writing). Not amended, not
  rewritten — shared, already-pushed history. This item file lands in its
  own commit.
