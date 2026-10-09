# HARMONY_PATCH_RESILIENCE_1 — a broken game update switches off one feature, not a whole mod

Source: `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row X-5 (FL-4 and LP-8 are the per-mod halves).

## what
- **Shared applier** `src/RimMandrake/_Shared/HarmonyResilience/PatchApplier.cs`, source-linked like LightLedger
  (internal types, one copy per assembly). Promoted from `HugeThingsCore.PatchNamespace`: applies each `[HarmonyPatch]`
  class alone inside try/catch, logs a red line naming the failed FEATURE and the reason, switches that feature's
  Mod Settings bool off for the session, and prints one census line `[<mod>] Harmony: patched N, missing X`.
  `[PatchFeature("label", typeof(Settings), "field")]` on a patch class names its feature. The player's own value
  is what gets saved (`BeforeExpose`/`AfterExpose`), so the feature comes back by itself once fixed;
  `DrawNotice` puts a red block at the top of the settings screen and `ReforceOff` stops the box being ticked back on.
- **FlowWorks adopted** (its single `PatchAll` is gone): all 30 patch classes carry `[PatchFeature]`; 28 name a
  setting, and 2 have none and are reported by name only (no-sand-swim, pit-cover path cost).
- **Limit:** the setting going off is what makes a feature's OTHER patches inert, so this only isolates a feature
  whose patches gate on their setting. FlowWorks' pit-trap pathing patches gate on it indirectly, through
  `IsHeld` / holders shed when capture is off.
- **Offline lint** `src/RimMandrake/Utils/lint_harmony_targets.py` (+ `selftest_lint_harmony_targets.py`): reads the
  installed game DLLs and our committed DLLs with dnfile and resolves every `[HarmonyPatch]` target plus the
  `AccessTools.Method/Field/PropertyGetter` and `FieldRefAccess` hooks (member, getter, constructor, argument count,
  inherited members). In mods using the applier it also fails a patch class with no `[PatchFeature]`, or one naming
  a field that is not a `public static bool`. MEASURED 2026-10-08 over all of src/: 408 targets, 402 OK, 0 missing,
  4 UNRESOLVED (Vehicle Framework types, not indexed), 2 dynamic.

## follow-up: mods still on one PatchAll
Counts are `[HarmonyPatch]` attribute lines (a rough size, stacked attributes count twice). Ninefold 31,
GimmeSomeSlack 22, LuminousPigment 15 (LP-8), RustCathedral 13, Scarlands 12, DivingInteraction 10,
TerminalBiomes 9, RaidRedesigner 6, Aftermath 6, GizkaStowaway 5, FeverWood 5, ExplosiveGrowth 5, Armoury 4,
LanternDeeps 4, ExplosiveKnockback 4, UnfinishedLine 3, TheForge 3, SolarMirrors 3, SeaShores 3, Inhabited 3,
ShipShields 2, EmpirePursuit 2, KineticArms 2, KeelHoist 2, FloodedCanyon 2, and 1 each in RiverColors,
PropaneLakeMechanics, PlantGrowth, FungalSoilTrade, FallLineArrivals, CathedralPass, SWBestiary, Wreckage,
PlanetPresetPrime, GravshipLanding, Cauldron and Abyss. HugeThings / TitanicCreatures keep their own
`PatchNamespace` loop, which has no catch; move them to `PatchApplier.Apply(h, asm, tag, ns)`. Per mod: link the
file in the csproj, swap the call, put `[PatchFeature]` on each class, wrap ExposeData, call `DrawNotice` and
`ReforceOff`, run the lint, and build.

## criteria
- O1 L0: selftest_lint_harmony_targets passes (each verdict both ways, the FlowWorks sanity probe, and the NO_FEATURE mutation); lint_harmony_targets over src/ exits 0; FlowWorks C# selftest green; winbuild OK
- A1 L1: on the live list Player.log carries `[RimMandrake.FlowWorks] Harmony: patched 30, missing 0`, with no FlowWorks Harmony error
- A2 L1: a test build with one patch target deliberately renamed logs exactly that feature as switched off, every other FlowWorks patch still applies, its settings box cannot be ticked, and settings saved in that session keep the player's own value
