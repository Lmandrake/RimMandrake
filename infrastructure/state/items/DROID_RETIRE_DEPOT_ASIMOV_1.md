# DROID_RETIRE_DEPOT_ASIMOV_1 — wave R3 (`DROID_UNIFIED_FRAMEWORK_DESIGN.md` §2 row D4)

Thin when filed. Spec written from what was measured this pass.

## Real packageIds (measured, not guessed)
- **Droid Depot** = `Neronix17.OuterRim.DroidDepot` (workshop `3096501398`)
- **Asimov** = `Neronix17.Asimov` (workshop `3096481956`)
- **MSEDroidFix** = `mandrake.rsw.msedroidfix` — OUR OWN one-file texture fix
  (`src/RimStarWars/MSEDroidFix/`), not a third-party donor; existed only to
  add Droid Depot's missing MSE-6 north-facing texture.

## Dependent check — whole active list, not just this item's scope
Grepped every active mod's `About.xml` (workshop content dirs matching the
two donor packageIds) for a hard reference, then read the hit in context:
only `FrozenSnowFox.ComplexJobs` (active) names either — a bare `<loadAfter>`
entry in a ~300-mod generic ordering list, no defName cross-reference. Three
other mods reference them (`Joe.MO.Tweaks`, `RimEffectRenegade.Core`,
`niz.xenomorphtype`) but none is active. No other active mod depends on
either donor.

Own-content check (everything in `src/` naming an Asimov/Depot defName):
- **Empire KX kind already repointed** (done under C1
  `DROID_FACTION_LOADOUTS_1`, before this item started):
  `src/RimUtinni/UtinniPatches/Patches/GalacticEmpire.xml` uses
  `RSW_DW_OuterRim_ImperialKXSecurityDroid MayRequire="mandrake.rsw.droidworks"`
  in all three Empire pawnGroupMaker option lists; the raw donor kind
  (`OuterRim_ImperialKXSecurityDroid`) is not referenced anywhere live.
- **4 FDE kinds already on Droidworks races** (C2 `DROID_FDE_KINDS_REPOINT_1`,
  closed `ac7c941f` 2026-09-08): `JawaFactionRoster.xml`'s
  `RUT_Jawa_Droid_{Grunt,Heavy,Specialist,Leader}` all carry
  `RSW_DW_Race_OuterRim_*` races, not Depot's own.
- `JawaFreeDroidEnclaves.xml`'s Depot-owned pawnkind options
  (`OuterRim_KXSecurityDroid` etc.) are `MayRequire="Neronix17.OuterRim.DroidDepot"`
  — silent no-op once Depot is off, correctly gated.
- `RUT_ResearchRetag.xml` / `RUT_ResearchTabAssign.xml`'s `Asimov_WirelessCharging`
  and `OuterRim_ProtocolDroids` rows are each wrapped in an outer
  `PatchOperationConditional` keyed on the def's own existence — self-guarding,
  harmless no-op once the donor def is gone.
- `RUT_AridShrubland.xml` / `RUT_Desert.xml` / `RUT_ExtremeDesert.xml`'s
  `OuterRim_MSEDroid`/`OuterRim_SalvageAssistDroid` wild-animal entries are
  `MayRequire="neronix17.outerrim.droiddepot"`-gated per entry.
- `BiomeCast_Ashkarr.xml`'s three matching blocks (Desert/AridShrubland/
  ExtremeDesert, 7 feral-droid species each) are gated at the `<Operation
  MayRequire="neronix17.outerrim.droiddepot">` level — first read looked
  ungated because the grep context window cut off the Operation tag; the full
  block is correctly gated. **Content consequence, not a bug**: retiring
  Droid Depot removes these 7 feral-droid wildlife spawns (MSE, SalvageAssist,
  DUM, GNK, FX7, Muckraker, Destroyer) from all three desert biomes — expected
  fallout of the retirement, not a new gap.
- `RUT_TradeMootDroids.xml` (C1, 2026-09-08) already anticipated this
  retirement in its own header: it deliberately did NOT use
  `Asimov.StockGenerator_Automatons` (gated on Depot, would die under R3)
  and wrote `RimMandrake.StarWars.Droidworks.StockGenerator_DWDroids` instead,
  with no live Asimov/Depot reference.
- `DROID_ASIMOV_SAVE_SCRUB_1` (closed 2026-09-06) already zeroed
  `Asimov.Need_Energy` on the two current save files; its own note flagged 75/71
  residual `Asimov` occurrences (WorkGiver names, research/blueprint
  registries, one `Asimov.WorldComp_EnergyNeed` world component) for this item
  to check against the load log — **owed to the next cold load**, not
  checkable offline.

No live dependent outside this item's scope was found. Proceeded.

## What was done
1. Backed up live `ModsConfig.xml` (594 mods) to
   `infrastructure/state/modlists/ModsConfig_2026-09-09_pre_depot_asimov_msedroidfix_retire.xml`.
2. Removed `<li>neronix17.outerrim.droiddepot</li>`, `<li>neronix17.asimov</li>`,
   `<li>mandrake.rsw.msedroidfix</li>` from the live `ModsConfig.xml` by
   exact-tag match (594 → 591), confirmed absent by re-grep.
3. Deleted `src/RimUtinni/Doctrine/Patches/NoDroidManufacture.xml` (targeted
   Depot's own `OuterRim_DroidFactory`; dead once Depot is gone).
4. Deleted `src/RimStarWars/StarWarsPatches/Patches/DroidFemaleTexture_Fix.xml`.
   Block 1 (7 ops) targeted Depot's own PawnKindDefs, dead once Depot is gone.
   Block 2 (4 ops, our own FDE kinds) is superseded: the Droidworks races those
   kinds now run on (`RSW_DW_Race_OuterRim_{ProtocolDroid,KXSecurityDroid,...}`)
   set `alienRace.generalSettings.alienPartGenerator.bodyTypes Inherit="False"`
   to `<li>Male</li>` only, with a single non-gendered body graphic path —
   structurally prevents the missing-female-texture bug at the race level,
   independent of any PawnKindDef `fixedGender` patch. Verified this on both
   `RSW_DW_Race_OuterRim_ProtocolDroid` and `RSW_DW_Race_OuterRim_KXSecurityDroid`
   in `Races_OuterRim.xml` before deleting.
5. Edited `src/RimUtinni/Doctrine/Patches/DroidsAreMachines.xml`: removed the
   `PatchOperationFindMod` block gating on `<li>Asimov</li>` (the
   `Asimov_Automaton` `isOrganic=false` operation) — dead once Asimov is off.
   Left the `killathon.artificialbeings.syncore` (ABF) block untouched: ABF/
   SynCore are still active, their retirement is the separate, concurrently-
   worked `DROID_RETIRE_ABF_SYNCORE_1` (wave R2). Added a one-paragraph dated
   note in place of the removed block rather than leaving silent history.
6. Deleted `src/RimStarWars/MSEDroidFix/` entirely (About.xml, LICENSE,
   Source/draw_mse_north.py, Textures/OuterRim/Droid/MSE_north.png) — the fix
   targets a texture path only Depot's own def asked for; matches the
   `BlastDoorFrameAsyncFix` precedent (our-own-fix-mod retirement deletes the
   source, not just the ModsConfig entry).
7. Deployed the two edited/retired custom mods live (config files, game
   running, per Charter's "config files never wait for the game" rule):
   `deploy_custom_mods.py --mod Doctrine --prune --apply` (removed the stale
   deployed `NoDroidManufacture.xml`, deployed the edited `DroidsAreMachines.xml`),
   `deploy_custom_mods.py --mod StarWarsPatches --prune --apply` (removed the
   stale deployed `DroidFemaleTexture_Fix.xml`). Both report VERIFIED in sync.
   Also removed the now-orphaned `Mods/MSEDroidFix/` folder directly from the
   game's Mods directory (no repo source left for the deploy tool to track it).

## Concurrent-item note
`DROID_RETIRE_ABF_SYNCORE_1` (wave R2, sibling item) was claimed and started
in the same window tonight, before this item, and was still `doing`
(un-closed) when this item executed. The design ladder lists R2 as this
item's nominal prerequisite, but the only concrete link between the two waves
is `DroidsAreMachines.xml`'s two independent `PatchOperationFindMod` blocks —
Asimov (this item) and ABF (that item) — which do not interact; removing one
does not affect whether the other's donor mod is safely retirable. Checked
`git status --porcelain` on the shared file before editing: clean, no
concurrent uncommitted changes. Proceeding with R3 did not require R2 to have
landed first.

## Verify (owed to the next cold load — not run; a crash-recovery reboot for
an unrelated item was already in flight when this item started, and this
item's own `ModsConfig.xml` change was not part of that boot)
```
PROVE   full-list cold load, 591 mods, zero NEW `Config error in` /
        `Could not resolve cross-reference` lines against
        infrastructure/state/facts/config_error_baseline_2026-09-06.json
EXPECT  0 lines naming Asimov/OuterRim_*Droid*/OuterRim_DroidFactory/
        OuterRim_MSEDroid; FDE droids (RUT_Jawa_Droid_*) and the Empire KX
        kind (RSW_DW_OuterRim_ImperialKXSecurityDroid) spawn on Droidworks
        races; check the load log for the 75/71 residual Asimov save-roster
        mentions D0 flagged
LIES    trusting a narrow grep context window over a MayRequire/
        PatchOperationConditional-gated block as "ungated" (caught once this
        pass on BiomeCast_Ashkarr.xml, corrected by reading the full
        Operation tag)
```

## criteria
- [x] Real packageIds identified and confirmed live.
- [x] Empire KX kind repoint confirmed already done (C1).
- [x] NoDroidManufacture retired (deleted, dead code).
- [x] Whole active mod list checked for dependents — none outside scope.
- [x] Removed from live `ModsConfig.xml`, backed up first.
- [ ] Cold-load verification — owed to the next natural restart.
