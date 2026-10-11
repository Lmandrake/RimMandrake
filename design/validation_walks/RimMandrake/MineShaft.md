# RimMandrake: Mine Shaft — validation walk
subject: src/RimMandrake/MineShaft  (packageId `mandrake.rm.mineshaft`)
deps: none (Core and the DLCs only); the Star Wars canon bars are `src/RimStarWars/Armoury/Defs/ThingDefs/RSW_MineShaftCanonPolicy.xml`, guarded by `MayRequire="mandrake.rm.mineshaft"`
status-hint: CANON_MATERIALS_BUILD_1 — our replacement for Mines 2.0 (Cain.Mineshaft), per `design/RimMandrake/mines_mod_assessment_20261011.md`; script = `src/RimMandrake/MineShaft/validation.py`, never run live yet

Sources: `About/About.xml`, `Defs/`, `Source/MineShaftMod.cs`, `Source/Kernel/RM_MineShaftKernel.cs`, the assessment.

## must be true
Every line ends in `→ chain.component` (a suite component that reads the state back) or `→ UNCOVERED: why`.
- The mine shaft, its research, its work giver and the base policy resolve in the running game; a nonexistent def reads absent. → defs_resolve.defs_resolve, defs_resolve.probe_can_say_absent
- One "mine for X" bill is generated per mineable resource rock product, steel and gold among them. → bills.bills_generated (offline: `replay()` over the newest DefDump capture)
- No product named by any MineShaftPolicyDef gets a bill: components (base policy), and with the Armoury the canon materials (beskar, durasteel, plasteel, doonium ore, hypertech components). → bills.barred_not_generated (offline: `replay()`)
- With `onlyMapVeins` on, a bill is offered only where the map holds the source rock or a deep deposit of the product. → UNCOVERED: no bridge tool reads RecipeWorker.AvailableOnNow; the rule itself is fuzzed (`selftest_mineshaft_fuzz.py`, family vein) → bills.vein_rule (UNMEASURED)
- With `shaftBills` off the shaft offers no bills. → UNCOVERED: same missing reader as above; the setting round-trips → settings_roundtrip.shaftBills_roundtrip
- All five Mod Settings fields read their shipped defaults, write and restore. → settings_roundtrip.shaftBills_roundtrip, settings_roundtrip.onlyMapVeins_roundtrip, settings_roundtrip.stoneBills_roundtrip, settings_roundtrip.yieldMultiplier_roundtrip, settings_roundtrip.workMultiplier_roundtrip

## the walk
1. [B] Tier: smallest list loading the mod (bridge + all DLCs + `mandrake.rm.mineshaft`, plus the Armoury for the canon bars), quicktest map.
2. [B] `modcheck run MineShaft` (note: `modcheck run` swaps the live mod list; a Charter expensive-list action).
3. [L] Player.log has the line `[MineShaft] N shaft bill(s) made from M rock(s); K barred by policy` and no Config or cross-reference error naming `RM_MineShaft`.
Offline: `python3 src/RimMandrake/MineShaft/validation.py` (static checks + capture replay) and `python3 src/RimMandrake/Utils/selftest_mineshaft_fuzz.py`.

## north star
state: DRAFT
validated-hash:

No owner-ruled experience bars yet; the functional lines above are agent-owned.

## anti-guessing notes
- RULED OUT: "an XML patch can remove a generated shaft recipe" — the recipes are built in C# after patching (StaticConstructorOnStartup), so bars are policy defs read at generation, never patches.
- RULED OUT: "MayRequire on a custom def type's element is ignored" — LoadedModManager.ParseAndProcessXML reads MayRequire on every top-level def node (decompiled 1.6, LoadedModManager.cs:395), whatever its type.
- The capture replay cannot order rocks by hit points (the DefDump has no statBases); it only matters when two rocks yield one product.
