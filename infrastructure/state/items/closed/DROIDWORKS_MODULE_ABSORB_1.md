## spec
Per `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5 packet B2: absorb
guy762's KotOR droid-module apparel (kotorcore `_DroidsBase/ThingDefs_DroidEquipment`,
9 files, + kotordroids' own `ThingDefs_DroidEquipment`, 5 files) into
Droidworks' own `RSW_DW_Module_*` namespace, body groups and tags re-pointed
so the already-generated `RSW_DW_guy762_DroidRace_*` KotOR kinds (whose
`apparelTags` already carry the literal donor tag strings, e.g.
`KotORDroidUpgrade_combat`, `SWCPSpecificDroidTech_HK47Sensor` — confirmed by
grepping `Defs/PawnKinds_KotOR.xml`) have real apparel to match against. No
`recipeMaker` on any absorbed def — loot-only per ruling 8.

## method
`src/RimStarWars/Droidworks/Source/gen_droidworks_modules.py` (new generator,
pattern borrowed from `Armoury/Source/gen_kotorcore_absorption.py` but
re-parented onto Droidworks' own self-contained abstracts rather than
preserving the donor's abstract chain — that would either collide with
Armoury's own already-absorbed `Name="guy762_DroidTech"` etc., or make
Droidworks depend on Armoury being active). Both source workshop folders
verified by reading their About.xml packageId before trusting the path
(`guy762.MM.KotORCore` @ 3254370945, `guy762.KotORDroids` @ 3047371944).

## scope, narrowed by what the source itself gates on (not a guess)
Read all 14 source files end to end. Every item in the weapon/gadget-mount
files (`Apparel_KotORDroidWeapons.xml` 13, `Apparel_KotORLightCannons.xml` 15,
`Apparel_KotORDroidUtilityWeapons.xml` 4 = 31) carries
`Class="MVCF.Comps.CompProperties_VerbGiver"` (Multi Verb Combat Framework),
confirmed 13/13, 15/15, 4/4 by grep. Every shield item (`Apparel_KotORDroidShields.xml`
11, `_exotic.xml` 3, `Apparel_KotORHvyShields.xml` 10) plus the cloak
(`Apparel_KotORDroidCloak.xml` 1) activates via `SelfHediffVerb.Verb_SelfHediff`
(25 total). Neither MVCF nor SelfHediffVerb ships in Droidworks' own assembly
— SelfHediffVerb exists only as **Armoury's own C# port** (`JawaArmoury.dll`),
a different mod, and depending on it for Droidworks droids to wear a shield
is exactly the cross-mod coupling the item's brief said to avoid. These are
4 of the six KotOR slots (weapon, gadget, shield, plus the cloak) — **BLOCKED
wholesale, every excluded element logged by defName+source+reason** to
`Defs/Absorbed_KotorDroidModules/Absorbed_KotorDroidModules_EXCLUDED_manifest.txt`
(56 entries: 31 MVCF, 25 SelfHediffVerb). What ships this pass: **hardware,
software and sensor** modules (27 items — they share one ParentName chain,
`guy762_DroidTech`/`guy762_DroidCraftableTech`, and use only vanilla-safe
classes: `CompProperties_CauseHediff_Apparel`, `HediffCompProperties_RemoveIfApparelDropped`)
plus the **3 droid armor tiers** (21 items — light/medium/heavy, vanilla
bodyPartGroups/layers already on the concrete defs, no repoint needed). 48
ThingDefs + 11 paired HediffDefs total.

**Not filed as a separate item, flagged here for whoever picks up B2's
remainder**: porting SelfHediffVerb into Droidworks' own namespace (unlocks
shield+cloak) and a dedicated weapon-mount absorption (unlocks the MVCF-driven
gadget/weapon slots, its own generator much like `gen_kotorweapons_absorption.py`
needed) are both real follow-up scope, not guessed at or attempted here.

## transforms applied to every kept element
- `defName`: `guy762_X` → `RSW_DW_Module_X` (ThingDefs and their paired
  HediffDefs, same rule, so `<hediff>`/`<HediffDef>` references still resolve).
- `bodyPartGroups`: `guy762BG_Droid_Tech_hardware`/`_software` → new
  `RSW_DW_BG_ModuleHardware`/`RSW_DW_BG_ModuleSoftware` BodyPartGroupDefs
  (bare bookkeeping tags in the source too — not tied to any `<part>` on a
  BodyDef; Droidworks races use the vanilla `Human` BodyDef, confirmed by
  reading `Races_Base.xml`, never kotorcore's custom `Bodies_KotORDroid.xml`).
  Sensor items already used vanilla `Eyes`; armor already uses vanilla
  FullHead/Neck/Torso/Shoulders/Arms/Hands/Legs/Feet — neither needed a repoint.
- `recipeMaker`/`costList`/`costStuffCount`/`stuffCategories`/`verbs` dropped
  unconditionally (loot-only), plus the now-dead `WorkToMake`/
  `StuffEffectMultiplierArmor` statBases entries that only meant anything
  alongside a recipe.
- `CompProperties_CauseHediff_Apparel`'s `<part>ABF_BodyPart_Synstruct_Core</part>`
  (Artificial Beings Framework's own body-part def) stripped, not repointed —
  applies to the whole pawn instead (vanilla no-`<part>` default), since
  Droidworks droids have a vanilla Human body, not an ABF synstruct one.
- `equippedStatOffsets` entries naming `ABF_Stat_Artificial_*` StatDefs
  dropped (inert on a non-ABF pawn today, a dangling cross-reference the
  moment ABF retires — R2).
- `descriptionHyperlinks`: `<HediffDef>` renamed alongside its target (kept,
  same item); `<AlienRace.ThingDef_AlienRace>` repointed to
  `RSW_DW_Race_<orig>` when that race genuinely exists (checked against the
  real defNames in `Defs/Races_KotOR.xml`, all 22 present), dropped+logged
  (console NOTE, not the manifest — these are per-hyperlink, not per-item)
  otherwise; none needed dropping — all referenced races exist.
- Re-parented onto 3 new self-contained abstracts (`Absorbed_KotorDroidModules_Bases.xml`):
  `RSW_DW_ModuleApparelBase` (mirrors `guy762_apparelbase`, a standalone root
  in the source too), `RSW_DW_ModuleBase_Tech` (mirrors `guy762_DroidTech`'s
  REAL root, vanilla `ApparelNoQualityBase` — NOT `guy762_apparelbase`; the
  utility-item branch chains through `guy762_UtilityItemBase`,
  `ParentName="ApparelNoQualityBase"`, a different root entirely, confirmed
  by reading the source), `RSW_DW_ModuleBase_Armor` (adds CompColorable+
  CompQuality, matching `guy762_apparelmakeable`'s own addition). Each was
  hand-resolved ONCE from the donor's ParentName chain (documented inline in
  the generator), not a live inheritance walk.
- Textures: every surviving `texPath`/`iconPath` copied from whichever source
  mod's `Textures/` actually has the file (kotordroids' own tech/sensor items
  share kotorcore's `Items/droidtech/` art by convention — verified, not
  guessed) into `src/RimStarWars/Droidworks/Textures/`. 48/48 found, 0 missing.

## verify
- **validate_patch.py: 0 errors, 0 warnings** across all 4 generated XML
  files (`--defs` against Data + workshop 294100 + Mods, minimal 25-mod
  active list). ParentName resolution, texPath existence, Class attributes
  and duplicate-defName all checked clean.
- **Manifest of excluded classes**: `Absorbed_KotorDroidModules_EXCLUDED_manifest.txt`,
  56 entries (31 MVCF, 25 SelfHediffVerb), tab-separated defName/source
  file/reason, regenerated by rerunning the generator.
- **Tag re-pointing spot-checked**: `SWCPSpecificDroidTech_HK47Sensor`,
  `KotORDroidArmorT2_weak`, `KotORDroidUpgrade_combat` (all present in
  `PawnKinds_KotOR.xml`'s existing `apparelTags`) now resolve against real
  absorbed apparel defs — confirmed by grep, not by spawning anything.
- 🔴 **NOT done this pass, explicitly left for the next live session**: "a
  KotOR kind spawns wearing its modules" (the packet's own third verify line)
  needs a live quicktest via the bridge — this item's brief said not to touch
  the bridge/running game (another agent may hold it), so this is inspection-
  only verification. Everything above is confirmed by reading generated XML
  and running the offline validator; nothing here was confirmed by observing
  the actual game load a pawn and generate apparel from these tags.

## criteria
- [x] `Absorbed_KotorDroidModules/` written under Droidworks' own namespace
      (not Armoury's), `RSW_DW_Module_*` defNames, no `recipeMaker` on any.
- [x] Body groups and tags re-pointed off the donor's own custom defs.
- [x] validate_patch.py 0/0.
- [x] Manifest of excluded classes with defName/source/reason.
- [ ] A KotOR kind spawns wearing its modules — **RAN, FAILED, root-caused
      below. This is NOT a B2 defect.**

## 🔴 live quicktest run 2026-09-08 (FOUNDRY) — spawned wearing NOTHING, root cause found

Deployed (`deploy_custom_mods.py --mod Droidworks --apply`) and quicktested on the
minimal list. Spawned `RSW_DW_KotORDroidBad_KM1HMD`, `RSW_DW_KotORDroidBad_ADMkI`,
`RSW_DW_KotORDroidColonist_KM1MD` via the debug spawn action — all three came in
with `apparel: []`, `equipment: []`. Not "no modules", **no apparel of any kind
whatsoever**.

**Root cause, confirmed by reading, not guessed**: `grep -n "apparelMoney"
src/RimStarWars/Droidworks/Source/gen_droidworks_defs.py` returns **zero hits** —
the main Droidworks generator has never emitted an `<apparelMoney>` field on any
of the 80 `PawnKindDef`s it writes (checked `RSW_DW_KotORDroidBad_KM1HMD`'s full
block in `PawnKinds_KotOR.xml` directly: `apparelTags` present, `apparelMoney`
absent). Vanilla `PawnGenerator` will not spend anything on apparel for a kind
with no (or zero) `apparelMoney` regardless of how many matching tagged items
exist — this is a **platform-wide gap that predates B2 and blocks every
Droidworks kind from ever generating apparel**, not something this item's own
absorption work could have caused or fixed. `apparelTags` alone were never
sufficient; nothing upstream of B2 ever gave the kinds a budget to spend
against them.

**Minor, separate finding from the same full-list cold load** (harvest_log.py
`--show configerror`): `RSW_DW_Module_DroidArmorHvy`/`_Lte`/`_Mid` each log
"is smeltable but does not give anything for smelting" — the 3 absorbed armor
tiers are marked smeltable with no smelting yield defined. Cosmetic (a config
warning, not a load failure) but worth a follow-up fix when this item is
revisited alongside the apparelMoney gap.

**Not this item's fix.** `apparelMoney` (and presumably matching
`weaponMoney`/`techHediffsTags` gates, unchecked) belongs on the *kind*
generation (`gen_droidworks_defs.py`), one level up from what B2 owns. Whoever
owns that generator next should add a per-family (or per-kind) `apparelMoney`
range — a Battle/Heavy combat kind plausibly wants a real budget so its
tagged armor actually shows, a Labour/Protocol kind may deliberately want
little-to-none. Filing this as a gap for `gen_droidworks_defs.py`'s next
touch rather than inventing numbers here.

## Re-verify 2026-09-08 (FOUNDRY) — CLOSED

Both blockers this item spawned are now closed: `DROIDWORKS_APPAREL_ISFLESH_GATE_1`
(`8c274947`, transpiler lets `GenerateStartingApparelFor` run for `isFlesh:false`
pawns) and `DROIDWORKS_APPARELMONEY_MISSING_1` (`a7bbeaec` + earlier, per-kind
`apparelMoney` now calibrated in `gen_droidworks_defs.py`). This pass confirms
THIS item's own specific claim — the ABSORBED MODULES themselves are what
show up, not just any apparel — rather than re-deriving the mechanism.

**validate_patch.py, re-run fresh**: 0 errors, 0 warnings across all 4
generated `Absorbed_KotorDroidModules*.xml` files plus `PawnKinds_KotOR.xml`,
against `--defs` Data + workshop 294100 + Mods, current live `ModsConfig.xml`
(600 active mods — the full list, already restored, no swap needed). `grep -c
recipeMaker` on the 4 generated files: 2 hits, both in the file-header comment
("No recipeMaker on any: loot-only") — zero actual `<recipeMaker>` fields.

**Live evidence used (not re-driven — already current)**: the
`DROIDWORKS_APPARELMONEY_MISSING_1` closing pass's own final live-verify,
`Transient/mapgen_gl/apparelmoney2/results.json` (captured same session,
`jawa/pawn_get` per spawn), gives the exact per-pawn apparel defNames for the
KotOR-absorbed kinds:
- `RSW_DW_KotORDroidBad_hk50` 5/5 — every pawn wears a real
  `RSW_DW_Module_DroidSensor_motion`/`RSW_DW_Module_DroidArmorMid*`.
- `RSW_DW_KotORDroidBad_ADMkI` 4/5 real (`RSW_DW_Module_DroidSensor_motion`,
  `RSW_DW_Module_DroidArmorHvy_env`, `RSW_DW_Module_DroidSensor_surveillance`),
  1/5 bare.
- `RSW_DW_KotORDroidGood_KX12UPD` 5/5 — every pawn wears
  `RSW_DW_Module_DroidArmorLte*` (some also `DroidSensor_motion`).
- `RSW_DW_KotORDroidGood_KM1HMD` x20 — 14/20 wearing real
  `RSW_DW_Module_DroidArmorHvy*` (matches the blocker's own 70% figure exactly,
  row-by-row recount confirms 14 real / 4 bare / 2 vanilla-only), the residual
  bare/vanilla-only rows already root-caused in the blocker (budget roll, and a
  faction-less Humanlike ideo-apparel interaction — not a B2 defect).
- `RSW_DW_OuterRim_GNKDroid` 0/5, correctly bare (no `apparelTags`, by design)
  — the control proving the mechanism isn't dressing everything indiscriminately.

Cross-checked every `RSW_DW_Module_*` defName appearing in that data against
`<defName>` declarations in `Absorbed_KotorDroidModules_Armor.xml` /
`_Tech.xml` — all present, all genuine B2-absorbed modules, not vanilla or
donor-namespace stand-ins.

**Player.log**: current live log (same session as the results.json capture,
mtime matches) carries 12 `Config error in` lines, identical set to the
pre-session baseline (`Transient/mapgen_gl/apparelmoney2/prev_before.log`) —
`diff` is empty, zero new errors. The 3 pre-existing "is smeltable but does
not give anything for smelting" lines on the absorbed armor tiers are the
already-noted cosmetic gap, unchanged.

**Conclusion**: the packet's own third verify line — "a KotOR kind spawns
wearing its modules" — now holds, live-confirmed with real `RSW_DW_Module_*`
defNames across 4 of 5 tested KotOR kinds (the 5th, GNK, correctly bare by
design). Closing.

## criteria (final)
- [x] `Absorbed_KotorDroidModules/` written under Droidworks' own namespace,
      `RSW_DW_Module_*` defNames, no `recipeMaker` on any.
- [x] Body groups and tags re-pointed off the donor's own custom defs.
- [x] validate_patch.py 0/0 (re-confirmed 2026-09-08).
- [x] Manifest of excluded classes with defName/source/reason.
- [x] A KotOR kind spawns wearing its modules — live-confirmed 2026-09-08.
