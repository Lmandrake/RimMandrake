# JAWA_FACTION_SLATE_LOAD_ORDER_1 — a real load-order guarantee for JawaFactionSlate

Filed 2026-08-29, FOUNDRY, while beating down Player.log errors during a game-up
window. `mandrake.jawafactionslate`'s About.xml carried `<loadBottom>true</loadBottom>`
— a fabricated field, not part of RimWorld's real `ModMetaDataInternal`
(`Verse/ModMetaData.cs`) schema, which only has `loadBefore`/`loadAfter`/
`forceLoadBefore`/`forceLoadAfter` (each a specific packageId list — there is no
"always load last" flag). It threw an XML error every single load and did nothing.
Removed 2026-08-29, deployed.

## Spec
The real problem the fake tag was trying to solve is still open, per the mod's own
description: measured 2026-08-20 after a RimSort re-sort put this mod at 184 of 577,
**24 of the 48 factions it patches were defined by mods loading AFTER it** — so
half the intended slate could still leak onto the Configure Factions page depending
on load order, on any list that isn't the exact one measured that day.

The real fix: a `<forceLoadAfter>` list in About.xml naming the packageId of every
mod that owns one of the 48 patched `FactionDef`s. That requires:
1. Read the 48 `PatchOperationConditional` targets in this mod's patch XML — each
   names a FactionDef by defName.
2. For each, find which mod's `Defs/FactionDefs/` actually declares that def (the
   live def dump's per-def source-mod attribution, or a defName grep across
   `vendor/mod_sources/` / the deployed Mods folder).
3. Map defName → owning mod → packageId, dedupe, write as `<forceLoadAfter>`.

## Verify
After the list ships: a RimSort re-sort (any order) should not change which
factions are hidden — every one of the 48 patches applies regardless of where
RimSort places other mods, because `forceLoadAfter` is meant to survive a re-sort
(unlike bare `loadAfter`, which RimSort's topological sort can still satisfy in
more than one relative position). Confirm on the next cold load: the Configure
Factions page shows only the intended slate, no matter today's exact mod order.

## criteria
- [x] Fake `<loadBottom>` field removed, deployed - the every-load XML error stops.
- [x] `forceLoadAfter` list built from the real defName-to-mod mapping, not guessed.
      Built 2026-08-29 (game DOWN) from the 2026-08-29T20-07-29Z def dump's per-def
      `modName`/`packageId` attribution — 45 of the 48 patched FactionDefs resolved
      to 24 unique non-core packageIds (`ludeon.rimworld*` omitted: Core/DLC load
      before any Workshop/local mod unconditionally, can never be the late arrival).
      3 targets (`CAEvilSacrilegHunters`, `CAFriendlyMechanoid`,
      `guy762_KotORFaction_Civilians`) resolve against nothing under the CURRENT mod
      versions — checked on disk: Caravan Adventures' 1.6 FactionDefs.xml no longer
      ships the first two (present only in its 1.2-1.5 folders); guy762 KotOR's
      `_FactionsBase` folder holding the third is never referenced by that mod's own
      `v1.6` `LoadFolders.xml`. Permanently-unmatched `PatchOperationConditional`
      targets, not a load-order bug — harmless by this mod's own no-`<nomatch>`
      design. `About/About.xml` deployed, `deploy_custom_mods.py --mod
      JawaFactionSlate --apply` verified in sync.
- [ ] Verified stable across a RimSort re-sort, not just today's order. Needs the
      next cold load — the owner playing is the default validation per CHARTER; not
      forcing a dedicated restart to prove it.

--- history ---
