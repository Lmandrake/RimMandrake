# Settings kit: master-switch greying + reset-all (BENCH, 2026-10-14)

Source: Transient/experiment_2026-10-14/gss_review.md §5 (kit gap).

## Item
SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST — spec, built list and the FlowWorks wiring live in
infrastructure/state/items/SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST.md.

## Kit API added (opt-in files; SettingsKitCore.cs / SettingsKitDrawer.cs untouched)
- SettingsKitMasters.cs: SettingDependencies.Declare/Independent/Name, IsLive/OffMasters/Unclassified;
  SettingsKitMasters.IsOn, ScopeGreyed, ResetAll, ResetAllLabel, ResetAllConfirmText.
- SettingsKitMastersDrawer.cs: ResetAllButton (confirmation dialog), Dependent(list, deps, get, set, keys) scope.
- Why separate files: editing SettingsKitCore.cs changes every kit DLL's .srchash (~40 mods) -> pre-push refuses
  until all are rebuilt (first attempt did exactly that; reverted).
- Design trap found and fixed in review: a scope greyed when ANY key was dead locked the sub-switch itself
  (tapEvents off -> its own checkbox greyed, unrecoverable). Now: dead keys always restored; the block is shaded only
  when NO key is live; the screen selftest refuses a scope whose root keys have different masters.

## Mods wired
- GSS Cables: enabled -> all cable settings except style + 4 spark settings (Independent: the Overhead lines tab reads
  them under its own master); tangles -> tangleMin; breakReadout -> whip; sway -> swayMode.
- GSS Overhead lines: enabled -> sag, autoLink, dripLoops, sway, swayStrength, fallen-wire shock/ignite, alert,
  owner-change cut, tapsEnabled; Independent maxSpan, maxStrands, keepWiresOnGravship, explosionsCut, kineticSway;
  chain tapsEnabled -> tapRate, tapEvents -> theftGoodwill -> perDay, sightRange; fallenWireShock -> knockback.
- Pyrelands: pyrelandsEnabled -> mechanics read through PyrelandsMechanicsGate.On; sub-switches replace the old
  hide-when-off blocks (now greyed, visible). Independent: fulgurite, ash-field numbers, regrowth, placement,
  restart-time switches, breakers, shovel.
- Reset all: both screens (GSS resets both tabs).

## FlowWorks wiring owed
In the item file (step list + candidate masters to confirm at read sites).

## Selftests
- selftest_settings_kit.py (new wrapper): PASS; planted ScopeGreyed defect -> 2 FAIL (instrument can see).
- selftest_settings_screens.py: 817/817 (5 new planted defects per opted-in screen).
- settings_audit.py: check (6); 2 declared, 14 drawn-but-undeclared (noted, not failed).
- Trap: after reverting a mutation with cp, the winbuild-staged kit selftest ran a STALE DLL (no recompile, 0.5 s);
  `touch` the source and rerun.

## Builds / shas
(see report)
