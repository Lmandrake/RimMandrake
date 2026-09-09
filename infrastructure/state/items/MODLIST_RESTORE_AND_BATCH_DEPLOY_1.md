# MODLIST_RESTORE_AND_BATCH_DEPLOY_1

## finding

`DROIDWORKS_PERSONALITY_VERIFY_1`'s agent swapped the live game down to a
minimal list for its own quicktest work, triggered tonight's third reboot at
20:40:54Z ("relaunching via Steam to pick up the droid-donor ModsConfig fix"),
and then went silent — no further ledger activity from it since. The live
`ModsConfig.xml` has been sitting at **6 mods (vanilla + 5 DLC, zero
third-party)** for 80+ minutes, bridge FREE the whole time, nobody restoring
it. The campaign is currently abandoned at a bare vanilla menu, not mid-load.

## spec

Restore the campaign to a real, correct, save-safe state and fold in tonight's
already-vetted new work, in ONE deliberate restart — not several more piecemeal
ones. Order matters; do each step and verify before the next.

1. **Reconstruct the correct target modlist.** Baseline:
   `infrastructure/state/modlists/ModsConfig_before_droid_donor_fix_2026-09-09.xml`
   (587 mods, 13:38 snapshot) — the Wave 1 retirement agent already confirmed
   this matches the campaign save's own `<modIds>` (590) exactly except for
   the 3 mods mid-revert tonight. Per the 20:39:08Z ledger event
   ("Neronix17.Asimov/DroidDepot/mandrake.rsw.msedroidfix restored"), those 3
   should be back IN the target list. Read the save's actual `<modIds>` list
   yourself (don't trust this summary) and confirm the reconstructed target
   set matches it exactly before proceeding. If it doesn't match, STOP and
   report the discrepancy rather than guessing which list is "right" — this
   is the exact class of mistake that cost three reboots tonight.
   ⚠️ Separately, `DROID_REPAIR_FOR_PROFIT_EVENTS_1`'s agent found
   `mandrake.rut.droidrepairjobs` missing from the list too, for unrelated
   reasons predating tonight (count drifted 601→587 over recent days). That is
   a SEPARATE, lower-priority drift — do not try to fix it in this pass unless
   it's trivial; note it if you leave it.

2. **Apply Wave 1 retirement on top of that baseline** — the 13 mods in
   `STAT_NORM_WAVE1_RETIRE_1.md`, already freshly re-verified clean (zero
   dependents beyond two mechanically-inert references, zero placed save
   instances) as of tonight. Remove them from the reconstructed list.

3. **Enable tonight's new own-built mods**, none of which have ever been in
   the live ModsConfig: find each one's real packageId by reading its own
   About.xml (do not guess) —
   - ManyWaters (`MANYWATERS_COLOR_SUPPORT_1`, `src/RimMandrake/ManyWaters/`)
   - Oracle (`ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1`, `src/RimMandrake/Oracle/`)
   - Moving Dunes (`MOVING_DUNES_BUILD_1`, `src/RimMandrake/MovingDunes/`)
   - FluidCanals (`FLUID_CANAL_MECHANIC_1`, `src/RimMandrake/FluidCanals/`)
   Insert each at a sensible load-order position — invoke the
   `rimworld-start-prep` skill for the doctrine on where a patch/content mod
   belongs relative to what it patches. All four are RM-tier and built clean
   tonight (0 warnings/0 errors each, per their own item files) — this is a
   pure addition, no removal risk.

4. **Redeploy what's built but undeployed**, game-down only:
   - The rebuilt JawaBench companion DLL WITH the GM tool pair
     (`BRIDGETOOLS_DLL_GM_DRIFT_1` — already built clean, `--apply` withheld
     tonight only because the game was up).
   - The `WORLD_FEATURE_LABELS_OVERSIZED_1` C# fix's rebuilt DLL (also
     already built clean, undeployed).
   - Any of the four new mods above that also need `deploy_custom_mods.py
     --apply` to actually land in the game's Mods folder (a def existing in
     the repo is not the same as it being deployed — see the
     `rimworld-deploy` skill).
   Do this AFTER shutting the game down for step 5, not while it's up.

5. **Shut the game down properly** (per `launch-rimworld-via-steam-not-bare-exe`
   doctrine — Steam, not a bare exe kill), do the deploys in step 4, write the
   reconstructed ModsConfig (back up the current live one first even though
   it's just the 6-mod list, for the record), then relaunch via
   `./game --said "<owner's standing 2026-09-02 reboot authorization, quoted>"
   up` citing the actual real reason (modlist restore + batch deploy), and
   load the real campaign save — not a quicktest.

6. **Verify.** Once up, run `python3 src/RimMandrake/Utils/harvest_log.py` and
   confirm it does NOT refuse and shows a clean baseline (no new
   cross-reference/config errors versus the last known-good run). This is the
   cold-load proof owed to: Wave 1 retirement, `BRIDGETOOLS_DLL_GM_DRIFT_1`,
   `WORLD_FEATURE_LABELS_OVERSIZED_1`, and the four new mods' first-ever load.
   Close each of those items' outstanding "cold-load proof owed" notes if this
   comes back clean (do not close the items' full criteria if other live-proof
   steps remain beyond just loading — read each one's own remaining bar).

## EXECUTION — FOUNDRY, 2026-09-09 15:30-onward

### 🔴 The premise of this item's "finding" section was WRONG, and that matters

The live list was **not** swapped down to a minimal list by another agent. **RimWorld
reset it itself.** `Player.log` from before anything was touched tonight carries
`Caught exception while loading play data but there are active mods other than Core.
Resetting mods config and trying again.` — the engine's own corrupted-mods recovery,
which writes a 6-mod `ModsConfig.xml` to disk and relaunches. The same reset, with the
**identical** exception fingerprint `[Ref 24E2AAB2]`, is also in
`Player_log_failed_fullload_2026-09-08.log` (2026-09-08 18:30). ⇒ **the full list has
been failing to cold-load since at least 2026-09-08 18:30**, and every "an agent left
it on vanilla" reading tonight was reading the symptom.

### Step 1-2 — modlist reconstruction: MATCHES the save exactly

| reading | value |
|---|---|
| save `CANONICAL_ASHKARR_2026-09-09.rws` `<modIds>` | **590** |
| `ModsConfig_before_droid_donor_fix_2026-09-09.xml` `<activeMods>` | **587** |
| save − 587-list | exactly `neronix17.asimov`, `neronix17.outerrim.droiddepot`, `mandrake.rsw.msedroidfix` |
| 587-list − save | **∅** |

587 + the 3 restored droid mods = **590 = the save's set, exactly.** No mismatch, no
side to pick. Order taken from the 13:38 587-list (the most recent full ordering); the
3 droid mods re-inserted after the same predecessors they had in
`ModsConfig_2026-09-09_pre_depot_asimov_msedroidfix_retire.xml` (13:01) — verified that
the two lists' 586 common ids are in **identical relative order**, so the splice cannot
reorder anything.

Then −13 Wave 1 (`STAT_NORM_WAVE1_RETIRE_1`, all 13 confirmed present first) = **577**.
All 582 target ids resolved against all three install roots
(workshop / `Mods` / `Data`, `About.xml` **direct child** `packageId` only): 0 unresolved.

⚠️ `mandrake.rut.droidrepairjobs` is absent from the save's own 590 too, so it is not
list drift against the save — left alone as this item instructed.

### Step 3 — the 4 new mods' real packageIds, read from their own About.xml

| mod | packageId | placed |
|---|---|---|
| ManyWaters | `mandrake.rm.manywaters` | after `mandrake.rut.fireecology` |
| Moving Dunes | `mandrake.rm.movingdunes` | ″ |
| Fluid Canals | `mandrake.rm.fluidcanals` | ″ |
| Oracle | `mandrake.rm.oracle` | ″ |

All four sit in the existing RM content cluster, **before** `mandrake.rm.rimdefdump`
(which must observe the fully assembled game) and after every `loadAfter` target each
declares (`sarg.alphabiomes` @50, `dubwise.dubsbadhygiene.lite` @127, `brrainz.harmony`
@1, `ludeon.rimworld.odyssey` @9). Their two `Patches/` files validated against the
reconstructed list itself (`validate_patch.py --defs` × 3 roots `--mods-config` target):
**0 errors**, predicted hit counts 2 and 1.

### 🔴 Step 4 — the real defect: SEVEN of our own C# types were missing from the DEPLOYED DLLs

The first launch on the reconstructed list reset again, same `[Ref 24E2AAB2]`. Diffing
today's log against the last clean full load
(`Player_log_before_overnight_restart_2026-09-09.log`, 2026-09-08 23:22) isolated it:
**7 `Could not find type named …` lines that the clean load does not have**, all naming
our own namespaces.

| type | owning mod | in REPO dll | in DEPLOYED dll |
|---|---|---|---|
| `RimMandrake.AnimalTheft.JobGiver_RM_TrainedSteal` | RimProperty | ✅ | ❌ |
| `RimMandrake.AnimalTheft.JobGiver_RM_WildSteal` | RimProperty | ✅ | ❌ |
| `RimMandrake.AnimalTheft.WildTheftExtension` | RimProperty | ✅ | ❌ |
| `RimMandrake.ProximityHatch.CompProperties_ProximityHatch` | ProximityHatch | ✅ | mod NOT DEPLOYED AT ALL |
| `RimMandrake.StarWars.FireEcology.PyrelandsBiomeRanges` | Pyrelands | ✅ | ❌ |
| `RimMandrake.StarWars.Livestock.CompProperties_KilnBelly` | SWBestiary | ✅ | ❌ |
| `RimMandrake.StarWars.Livestock.CompProperties_KilnFeed` | SWBestiary | ✅ | ❌ |

**Every one is in the repo build and absent from the game copy** — the consolidation
rebuild's assemblies were never deployed, because an assembly can only be written in a
game-down window and there has not been one since.

**The causal chain, end to end:**
`ThingDefs_Onnik.xml` carries `CompProperties_KilnBelly`/`KilnFeed` → type absent →
🔴 **the WHOLE ThingDef is discarded** → `PawnKindDefs_Onnik.xml`'s pawnkind is left
with a null `race` → Alpha Genes' `GeneDefGenerator.ImpliedGeneDefs` postfix iterates
pawnkinds and **NullReferences on it** → RimWorld catches it, resets `ModsConfig.xml`
to 6, relaunches. The 2026-09-08 18:30 failure is the same shape one animal earlier
(`[Def Error]: RSW_Karrask`, also SWBestiary).

**Fixed** (game DOWN, verified each type present in the game copy afterwards by byte
scan of the deployed DLL): `RimProperty`, `Pyrelands`, `SWBestiary` assemblies
redeployed; `ProximityHatch` deployed for the first time and **added to the modlist**
immediately before `mandrake.rsw.swbestiary` (whose About already declares
`loadAfter mandrake.rm.proximityhatch`) ⇒ final list is **582**, not 581.

### 🔴 New trap found: `MayRequire` on a `<Operation>` inside a Patch file DOES NOTHING

`SWBestiary/Patches/ProximityHatch/RSW_ProtovermesEgg_ProximityHatch.xml` guards its op
with `MayRequire="mandrake.rm.proximityhatch"` and its own comment says "absent it, this
file is a silent no-op". It is not. Read from the engine source
(`Source/Verse/LoadedModManager.cs`): `ApplyPatches()` runs
`runningMods.SelectMany(rm => rm.Patches)` and calls `item.Apply(xmlDoc)`
**unconditionally** — it never looks at attributes. The `MayRequire` check at line 395
is inside `ParseAndProcessXML()` and applies only to **top-level def nodes in the
unified XML**, never to `<Operation>` elements. `mandrake.rm.proximityhatch` has never
been in any modlist snapshot, and the op applied anyway, discarding
`RSW_ProtovermesEggFertilized`.
⇒ **The only working guard for a patch operation is `PatchOperationFindMod`.**

### Other deploys done in the same window

- `build.py --gm --apply` → `RimWorld/BridgeTools/JawaBench/`. Build 0 warnings /
  0 errors, `selftest_tool_metadata.py` **317 tools, GM pair included**, repo and game
  copies **md5-identical** (`c8a3ca5b…`). Carries the
  `WORLD_FEATURE_LABELS_OVERSIZED_1` fix (`sqrt(count) * 1.35f`, confirmed at
  `JawaBenchWorldTools.cs:4695` in the source that built).
- All four new mods deployed / verified in sync; all four DLLs md5-identical repo↔game.
- Live 6-mod `ModsConfig.xml` archived to
  `infrastructure/state/modlists/ModsConfig_LIVE_6mod_before_restore_20260909_154141.xml`;
  the written list archived as `ModsConfig_RESTORE_582_2026-09-09.xml`.

## verify
Live `ModsConfig.xml` active-mod count matches the reconstructed target
exactly; `harvest_log.py` runs clean against the NEW run (not a stale dump);
the four new mods appear active and error-free in the log; Wave 1's 13 mods
are confirmed absent.

## criteria
Campaign is back to a real, playable, save-safe state with tonight's vetted
new work folded in, verified by one clean cold load — not left sitting on a
bare vanilla list.
