# GSS patch-feature review — commit 52a6a44d20 (independent reviewer)

## Reachability
All 8 changed .cs files are explicit <Compile> items in RimMandrake_GimmeSomeSlack.csproj (EnableDefaultCompileItems=false).
Each had a clean mark from the day before; the only change since each mark was 52a6a44d20.

## Per-file review
- Feature mapping: correct. Each field named exists, is `public static bool`, and is the setting that gates (or fronts) that
  feature. Notes, not bugs: the StylePicker.cs patches (labelled "anchor looks") also serve conduit/lamp styles through the
  shared StyleIndex core, so a failure there also affects conduit looks while switching off only AerialSettings.enabled.
  That follows from one field per class.
- Always-on (3): sound. LampMasterOff IS the master-off path. ExposeComponents_SkipAerial is save hygiene whatever the
  settings. GenTypes_LegacyTypeName is pre-rename save compatibility. None of the three has a field that would make it safer.
- Defaults: unchanged. The attributes change nothing at runtime unless a patch fails.

## Save/load hook safety
- Old settings files: no new keys were added. Missing keys load their Look defaults as before. Without a failure,
  BeforeExpose and AfterExpose do nothing.
- BUG (GimmeSomeSlackMod.cs:475 + AerialSettings.cs:345): PatchApplier.Apply ran inside GimmeSomeSlackMod's constructor.
  AerialLinesMod's GetSettings could run AFTER that, because the order the two Mod classes are constructed in is not fixed.
  If it did, its LoadingVars AfterExpose re-read EVERY forced field as the player's value, including
  GimmeSomeSlackSettings.enabled and hideHookupWires, which a failed patch had just forced false. The next settings write
  would then save them as off for good: the exact corruption these hooks exist to prevent.
- GAP (GimmeSomeSlackMod.DoSettingsWindowContents): the window never called PatchApplier.ReforceOff, so a checkbox or reset
  could turn a failed feature back on for the session, which goes against PatchApplier's contract.

## Fixes
- Harmony is applied by GimmeSomeSlackMod.SettingsLoaded(), which both Mod constructors call (in a finally block) after
  their GetSettings. The second call applies, so no settings file loads after a patch has been forced off.
- ReforceOff() runs after the settings window draws. It does nothing while every patch has applied.
- Not done (a UI change, needs a decision): PatchApplier.DrawNotice, which would show the red "switched off" block in the
  GSS window.
- The root cause is that AfterExpose re-reads every class's forced fields. It sits in _Shared/PatchApplier.cs, which is
  source-linked into about 30 mods, so a fix there would make every committed DLL disagree with its source stamp. It was
  left alone and is reported instead.
- Build: 0 warnings, 0 errors. Selftests selftest_gimmesomeslack and selftest_lint_harmony_targets: GREEN. Harmony lint:
  feature-findings 0.

## Code-review status
All 8 files are CLEAN. 6 had no findings. AerialSettings.cs and GimmeSomeSlackMod.cs were marked clean after the fix commit.
