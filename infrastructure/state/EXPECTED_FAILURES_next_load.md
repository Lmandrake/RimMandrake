# Expected-failure signatures — batch restart, 2026-09-10 (FOUNDRY)

Written BEFORE launch per load-round §2/§3. Owner approved restart now
(question card, "Restart batch" → "Go ahead and restart now"). Two real
code changes ride this load; everything else already loaded clean on the
prior restart (MODLIST_RESTORE_AND_BATCH_DEPLOY_1, 2026-09-09/10).

## What's riding this load

1. **`RimMandrake.Utinni.UtinniPatches.dll`** (`mandrake.rut.patches`, already
   active, deployed this session) — new type `AmbientShrineGuardians.cs`
   (subclass-swap via `PatchOperationAttributeSet` on `Rules_Interior.xml`'s
   `ancientTemple` rule's resolver list, no Harmony). Fails as: an error
   naming `RimMandrake.Utinni.UtinniPatches.AmbientShrineGuardians` /
   `SymbolResolver_Interior_AncientTemple`, or a `PatchOperationAttributeSet`
   miss on `Data/Core/Defs/RuleDefs/Rules_Interior.xml` (validate_patch.py
   already confirmed 1/1 match against the live 576-mod set offline).
2. **`mandrake.rut.scavengerevents`** — first-ever load (mod entry already in
   ModsConfig, never loaded before tonight). Fails as: errors naming
   `RimMandrake.Utinni.ScavengerEvents`, `MO_SurvivalPod`/`ShipBreak`/
   `PodCrash`/`Insects`/`Migration`/`Thanksgiving`/`Stroke` IncidentWorkers,
   or a discarded def in that mod's own Defs/.
3. **Cherry Picker live config** (`Mod_3521312241_Mod_CherryPicker.xml`,
   Config-only, not a repo file) — 141 genuine-reversal keys re-added per the
   owner's ruling on `CHERRYPICKER_SHIP_BASELINE_STALE_1` (see that item: the
   diagnosis doc's own prose said "139" but its enumerated defName lists
   total 141 genuine / 37 self-pruned RBM_/tug.Minotaur — going with the
   enumerated count, independently re-verified that tug.Minotaur is inactive
   and the other three source mods are active). Not a load-failure risk (it's
   a spawn-filter list, not a def), verified separately via
   `cherrypicker.py --source live` after this load, not by a Player.log
   signature.

## Also riding, from tonight's code-review fan-out (4 parallel waves, isolated worktrees)

4. **`Droidworks.dll`** (`mandrake.rsw.droidworks`, already active) — deployed a
   pending Harmony prefix fix (commit `492520c2`, "suppresses sibling-relation-gen
   crash for droids") that was committed but never deployed. Fails as: a
   `HarmonyException` naming `Droidworks`, or the original sibling-relation-gen
   crash recurring (meaning the prefix didn't take).
5. **`RUT_Scarlands.xml`** (UtinniPatches, redeployed) — restored a missing
   `ParentName` that left `extraGenSteps` empty (craters/ruins/junk-cluster
   mapgen never fired). Fails as: a def-inheritance error naming `RUT_Scarlands`,
   or (silently) Scarlands maps generating with no extra genstep content —
   only visible by actually looking at a Scarlands map, not a log line.
6. **`JawaBench.BridgeTools.dll`** (companion, rebuilt+redeployed) — fixed
   `jawa/world_landmark_rename` to match on `PlanetTile` equality (surface vs.
   orbit layer) instead of raw `tileId`. Fails as: `selftest_tool_metadata.py`
   tool-count mismatch (already re-run clean, 317/317) or a bridge tool-list
   discovery error naming `JawaBenchLandmarkNameTool`.

## Everything else already proven on the prior restart, not re-tested here
Oracle, FluidCanals, MovingDunes, Wave-1 retirement (13 mods), JawaBench GM
pair — all confirmed clean on the 2026-09-09/10 restart per
`MODLIST_RESTORE_AND_BATCH_DEPLOY_1`. ManyWaters stays excluded (its own
`thingClass` blocker, unfixed).
