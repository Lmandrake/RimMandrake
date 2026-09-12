# FactionSlate — validation walk
subject: src/RimUtinni/FactionSlate  (packageId: mandrake.rut.factionslate)
deps: none in modDependencies/loadAfter — but 23 packageIds are pinned via `forceLoadAfter` (see must-be-true; this mod's whole purpose only exercises on the full list)
list: full
status-hint: Zeroes `startingCountAtWorldCreation` on 46 non-campaign FactionDefs so the Configure Factions page shows only the campaign's own slate — every Operation is a `PatchOperationConditional` on the def's existence (no `<nomatch>`, deliberately silent on a dropped mod), and `forceLoadAfter` exists specifically so a late-loading mod's faction is still caught.

## must be true

- 46 unique `FactionDef[defName=...]` targets are patched (verified by grep: `AA_BlackHive` through `guy762_KotORFaction_RogueDroids`), each wrapped in an outer `PatchOperationConditional` testing the def's existence, with an inner `PatchOperationSequence` → `PatchOperationConditional` that Replaces `startingCountAtWorldCreation` if present or Adds it if absent — always to `0`.
- None of the campaign's own faction defNames (`Jawa_Junkers`, `Jawa_HuttCartel`, `Jawa_DeepwaterCompact`, `Jawa_FreeDroidEnclaves`, etc.) appear among the 46 patched targets — they are the ones meant to survive un-zeroed.
- `forceLoadAfter` names 23 packageIds, one per mod that owns a patched FactionDef under the current mod list (JAWA_FACTION_SLATE_LOAD_ORDER_1) — Core/DLC packageIds are deliberately absent since they always load first.
- `CAEvilSacrilegHunters` and `CAFriendlyMechanoid` blocks are gone from the file for good (removed 2026-09-04, confirmed dead in Caravan Adventures' current 1.6 XML) — their defNames must NOT reappear as Operation targets.
- `CASacrilegHunters` (the surviving Caravan Adventures defName) is still patched, and `guy762_KotORFaction_Civilians` stays as a correct guarded no-op (real defName, but its owning mod is not currently active).
- On the full mod list, `startingCountAtWorldCreation=0` for every one of the 46 targets whose defining mod is actually active — this is the direct, automatable proof that `forceLoadAfter` fixed the load-order bug (patched even though this mod is not naturally the LAST loader for many of these packageIds).

## the walk

1. [L] Player.log after load contains no `Config error in mandrake.rut.factionslate` and no XML error naming `OnlyOurFactions.xml`
2. [D] def read-back: FactionDef `AA_BlackHive` (sarg.alphaanimals, forceLoadAfter target) exists; startingCountAtWorldCreation=0
3. [D] def read-back: FactionDef `BS_LittlePeople` (redmattis.bigsmall, forceLoadAfter target) exists; startingCountAtWorldCreation=0
4. [D] def read-back: FactionDef `OuterRim_GalacticEmpire` (neronix17.outerrim.galacticempire, forceLoadAfter target) exists; startingCountAtWorldCreation=0
5. [D] def read-back: FactionDef `CASacrilegHunters` (iforgotmysocks.caravanadventures, forceLoadAfter target) exists; startingCountAtWorldCreation=0
6. [D] def read-back: FactionDef `Jawa_Junkers` exists; startingCountAtWorldCreation is unchanged (nonzero) — confirms the campaign's own faction was never a target
7. [D] def read-back: FactionDef `CAEvilSacrilegHunters` and `CAFriendlyMechanoid` — confirm neither is referenced anywhere in `OnlyOurFactions.xml` (grep the file, not the def dump — they may not exist at all on the current mod version)
8. [B] jawa/get_defs {defType: "FactionDef", fields: ["startingCountAtWorldCreation"]} filtered to all 46 patched defNames → every one present on the live mod list reads 0; any absent one is a mod-not-active case, not a failure
9. [B] jawa/list_factions → confirms the frozen campaign world's own generated faction roster contains none of the 46 suppressed defNames (this checks the FROZEN world, not fresh worldgen — the Configure Factions page itself is a UI screen this bridge cannot drive, so a fresh-worldgen re-proof stays a human check)
10. [S] (human pass) open Configure Factions on a NEW world generation and confirm the page lists exactly the campaign's 13 factions (~~14~~ 2026-09-12; 8 ours + 5 vanilla/mod — the Unbound Hive cut landed), none of the 46
