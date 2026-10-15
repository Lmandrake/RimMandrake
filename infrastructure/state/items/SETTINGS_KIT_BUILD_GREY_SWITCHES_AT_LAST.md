# SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST

Filed by BENCH 2026-10-14. Source: `Transient/experiment_2026-10-14/gss_review.md` §5 (GSS review found the shared
Mod Settings kit could not grey sub-settings under an off master switch, and had no reset-everything button).
Working notes: `Transient/experiment_2026-10-14/settings_kit.md`.

## spec

1. Kit: a way to declare a setting's master switch(es); dependents draw greyed and non-interactive while a master
   is off, values preserved.
2. Kit: a "Reset all to defaults" button that asks for confirmation.
3. Additive: a mod that does not opt in is unchanged (its DLL and .srchash too).
4. Wired into GimmeSomeSlack (both tabs) and Pyrelands. FlowWorks NOT edited (another agent is in it): wiring below.
5. Selftests: a dependent without a declared master, on a mod that declares masters, is flagged.

## built (2026-10-14)

- `src/RimMandrake/_Shared/SettingsKit/SettingsKitMasters.cs` (pure, selftested): `SettingDependencies`
  (`Declare(master, dependents...)`, `Independent(...)`, `Name(key, label)`, chains, several masters per dependent,
  cycles refused), `SettingsKitMasters.IsOn`, `ScopeGreyed`, `ResetAll`, `ResetAllLabel`, `ResetAllConfirmText`.
- `src/RimMandrake/_Shared/SettingsKit/SettingsKitMastersDrawer.cs` (Verse): `ResetAllButton(list, scopeName, onConfirmed)`
  (Dialog_MessageBox.CreateConfirmation, destructive) and `Dependent(list, deps, get, set, keys...)`, an IDisposable
  scope: dead keys are snapshotted and written back, the block is shaded with a "switch on X" tooltip only when no key
  in it is live. No UnityEngine.GUI (many kit users lack IMGUIModule).
- Separate files on purpose: every kit DLL's .srchash hashes the kit files it compiles, so editing SettingsKitCore.cs
  would have forced a rebuild of ~40 mods. Opt-in mods link the two new files.
- Checks: `selftest_settings_kit.py` (new wrapper; the kit C# selftest was never in the suite before),
  `selftest_settings_screens.py` masters_check (opt-in: every grouped setting classified; declared names Scribed;
  drawn dependents inside a scope that lists them; no scope mixes root keys with different masters; Reset-all present;
  csproj links both files) with 5 planted defects per opted-in screen; `settings_audit.py` check (6) notes every mod
  that draws a master switch but declares nothing (14 on 2026-10-14, FlowWorks among them).

## FlowWorks wiring owed (do NOT do while another agent is in FlowWorks C#)

Pattern = GSS/Pyrelands (see `src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs` `Masters` + `Dependent` helper):

1. `src/RimMandrake/FlowWorks/Source/*.csproj`: next to the SettingsKitDrawer.cs Compile Include add
   `SettingsKitMasters.cs` and `SettingsKitMastersDrawer.cs` (same `..\..\_Shared\SettingsKit\` path, `Link="Shared\..."`).
2. In each settings class that draws a master (`RimMandrakeFlowWorksMod.cs` settings class, `Hose/RM_HoseSettings.cs`):
   - `internal static readonly RimMandrake.Shared.SettingDependencies Masters = new ...().Declare(...)...;` placed BEFORE
     the `shippedDefaults` initialiser (it must stay the last static initialiser);
   - `GetField`/`SetField` by reflection on the class's public static fields (return a COPY of any list, e.g.
     `disabledFluids`, like GSS `excludedConduits`);
   - `private static IDisposable Dependent(Listing_Standard list, params string[] keys) =>
     RimMandrake.Shared.SettingsKitMastersDrawer.Dependent(list, Masters, GetField, SetField, keys);`
   - `RimMandrake.Shared.SettingsKitMastersDrawer.ResetAllButton(list, "Flow Works", ResetAllFields)` under the search
     box, `ResetAllFields()` = `ResetFields(all shippedDefaults keys + list-valued settings)`.
3. Candidate masters, each to be CONFIRMED at its read site before declaring (a greyed control that still acts is a lie;
   when unsure, declare `Independent`):
   - Hose: `enabled` ("Flexible hoses (master switch)") -> every other hose setting it gates; `tankModesEnabled` ->
     `tankUnitsPerCycle`; `freeEndRolesEnabled` -> `dumpUnitsPerCycle`.
   - Main: `depthEngineEnabled` (comment item 4: master of the depth/fill grid) -> `digToDepthEnabled` and the fill
     settings it gates; `liquidDrillingEnabled` (comment item 27: master for the whole route) -> its route settings;
     today's hide-when-off blocks become nested scopes: `liquidHeatPushEnabled` (line ~847), `canalFireEnabled` ->
     `explosionIgnitesLiquidEnabled`, `foamSmothersLiquidFireEnabled`, `rainDousesLiquidFireEnabled`;
     `superdeepRoomsEnabled` -> `captureDownEnabled`; `pitDrowningEnabled`, `pitExposureEnabled`, `fallDamageEnabled`,
     `spikesEnabled` (their nested numbers); `excavationWallFacesEnabled` -> `excavationWallMaterialEnabled`,
     `pitOutlineEnabled`; `pitDepthDrawOffsetEnabled` -> `pitLipOcclusionEnabled`, `pitSinkClampEnabled`,
     `pitHidesShadowEnabled`; `pitLipOcclusionEnabled` -> `pitLipOccupantCutEnabled`; `pitScorchEnabled`,
     `liquidBubblesEnabled`, `trapTriggerEnabled` (nested numbers); `digFindsEnabled` -> `digFindsLocalOnly`,
     `digFindLetterEnabled`; `bottleLoopEnabled` -> `bottleDirtyStageEnabled`, `bottleRevertEnabled` (check).
   - The sub-screens (Rivers, Machinery, SluiceGate, Kits, Quarry) the same way where they draw a master.
4. Every setting of an opted-in screen must end up master, dependent or Independent, or
   `selftest_settings_screens.py` fails. NOTE: the main FlowWorks screen draws its sections with its own
   `if (open) DrawSectionReset(...)` shape, not `if (Group(list, ...))`; the masters_check runs on the method body
   either way, but confirm the screen entry in `MODS` still parses after wiring.
5. Rebuild with `winbuild.py` (DLL + .srchash), run `run_selftests.py --only selftest_settings_screens.py
   selftest_settings_kit.py`, review + `code_review_status.py mark-clean`, add a live check line.

## verify

Offline: `selftest_settings_kit.py` PASS, `selftest_settings_screens.py` all ok, both DLLs stamped. Live (owed,
`Transient/experiment_2026-10-14/live_worklist.md`): in the GSS and Pyrelands settings windows, a master off shades its
dependents with the tooltip, clicks and drags on them change nothing, values return when the master is back on, and
Reset all asks before it writes.

## criteria

- A1 L0: selftest_settings_kit.py PASS and selftest_settings_screens.py all ok at the implementing sha; GSS and Pyrelands DLL stamps MATCH.
- A2 L1: in the GSS and Pyrelands settings windows a master off shades its dependents, clicks change nothing, values return with the master on.
- A3 L1: Reset all to defaults asks first; Cancel changes nothing; Confirm resets every setting (GSS both tabs).
