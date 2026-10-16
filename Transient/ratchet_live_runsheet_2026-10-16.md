# Ratchet release — consolidated live run-sheet (2026-10-16, BENCH)

The live checks still owed by the three ratchet mods (GimmeSomeSlack, FlowWorks, Pyrelands) and the shared fixes landed
today, set out for **one restart**. Do not start until FOUNDRY has released the bridge (`rimflow bridge who`).
Mod source HEAD when this was written: `4d93839d87` (PatchApplier fix plus all 39 sharing DLLs rebuilt; GSS toggles; TribesOrNull).

## 0. Game closed: deploy

Re-run every plan just before applying it, because FlowWorks and Baroque Biomes are changing under other BENCH agents
today. Read each `-` line, and refuse files another seat has in flight. The dry plans from 2026-10-16 08:05 are in
`Transient/ratchet_live_2026-10-16/plan_*.txt`.

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod GimmeSomeSlack --apply      # DLL 5e523c88… (CHANGELOG 1.0.0 repackage line)
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod PyrelandsMechanics --apply  # TribesOrNull fix 037724d140
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply           # only after the walk agents' DLL lands
python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply          # Pyrelands + RustCathedral + kits (29 drift lines at 08:05)
python3 src/RimMandrake/Utils/dll_source_stamp.py check | grep -v ^MATCH              # expect nothing
```

**Companion DLL** (PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK, plus OWN_PRESET_WIDEN_PYRELANDS_JOINS_IN 53595b2d45).
The earlier build failure happened because the export lacked `src/Directory.Build.props` and `src/Directory.Build.targets`.
The fixed command (its item note) is below; run it with the game closed:
```
E=$(mktemp -d); git archive HEAD src/Directory.Build.props src/Directory.Build.targets src/RimMandrake/bridgetools src/RimMandrake/Utils | tar -x -C $E; python3 $E/src/RimMandrake/bridgetools/build.py --gm --apply
```
Then apply the tier with `modset_builder --tier ratchet_pilot --apply`, keeping the owner list backup, and launch via Steam.

## 1. Startup log (Player.log, first load). One read decides three items

| look for | means | item |
|---|---|---|
| `[GimmeSomeSlack] Harmony: patched 23, missing 0` (or the census count, `missing 0`) | every GSS patch class applied | GSS_PATCHES_FIX_TWENTY_THREE_UNLABELLED A1 (first half) |
| no line `Harmony patch failed, feature switched off` for any mod | no shared PatchApplier regression across the 39 rebuilt DLLs | PATCH_APPLIER_FIX_WRONG_SETTINGS_REREAD A1 |
| `[RustCathedral` census with `missing 0`, no red RustCathedral line | the two-settings mod loads with the owner filter | PATCH_APPLIER_FIX_WRONG_SETTINGS_REREAD A1 |
| FIRST exception in the log, not the loudest | standard triage | — |

## 2. Settings windows (L1, a minute each, any map)

1. **GSS, both tabs:** turn each master off, then on. Dependents grey out, clicking them changes nothing, and their
   values come back. Reset all asks first: Cancel changes nothing, Confirm resets both tabs.
   (SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST A2/A3, GSS_PATCHES A1 "masters revert art")
2. **Pyrelands:** the same master/dependent check (SETTINGS_KIT A2).
3. **FlowWorks:** a master off greys its dependents and keeps their values; Reset all asks first (FLOWWORKS_SETTINGS_WIRE_AFTER_TANKS A2).
4. **GSS toggles:** with Overhead lines OFF, select an existing pole and press Copy. No 4-style menu may open and
   there must be no `[GimmeSomeSlack]` error. Turn it back ON, and the pole build button opens the menu
   (GSS_TOGGLES_FIX_OFF_MEANS_OFF A1).

## 3. GSS suite (calm save `RM_TestSite_calm_v1`, ratchet_pilot tier)

```
python.exe "D:\…\GimmeSomeSlack\validation.py" --live      # from a git-archive export of HEAD (the L2 recipe)
```
- The row-set baseline is L2c, 118/119 at 28237fdad2. Expect the same 0 FAIL.
- **B13_hidden_conduit_hookup_not_drawn** (GSS_HOOKUP_CABLE_PROBE_HIDDEN_CONDUIT): read `printed` in the row JSON. It
  was `[null, null]` at L2. If it is still null, the census field `hookupCablesPrinted` is not being returned
  (GimmeSomeSlackProbe.cs:620) and that is a HARNESS fault. If `moved > 0`, the visible cable is real, and that is a
  cosmetic call for the owner.

## 4. Pyrelands (fresh or calm2 site `NS_Pyrelands_site_1_417df172fdb5_calm2`)

```
python.exe "D:\…\Utils\northstar_driver\cli.py" run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains gpt_hunt_plausible
```
Plus these single-row checks (bridge calls; the full criterion text is in each item's `implemented` event, `rimflow show <ID>`):

| item | check | pass |
|---|---|---|
| ASH_TERRAIN_FIX_NO_MEDIUM_GROUND | place a Medium-affordance building and a grave on `RM_FE_Ash_Deep` | both place |
| FIRE_CLOCK_FIX_RAIDS_IGNORE_THE_SWITCH | fireClockEnabled OFF; `jawa/fire_incident` dry-run of RUT_FireRaid and RUT_FlameHarvest on a burning map | CanFireNow false for both |
| FIRE_RITE_FIX_DEFENDERS_MISS_THE_WAR | harm a travelling rite party (it drops to DefendPoint), then set Tribes hostile | lord goes to ExitMap |
| RITE_HARVEST_FIX_PICKS_PAST_FULL | sample harvester jobs during a fire rite | stop at fireRiteCarryPerPawn; no pod beyond FireRiteHarvestRadius of the origin |
| BURN_HISTORY_FIX_ANCHOR_NEVER_AGES | `MapComponent_BurnLine.ProbeBurnHistory` on a map whose last fire is older than BurnHistoryKeepTicks | ago=invalid |
| ASH_FIELD_FIX_FORGETS_THE_WATER | ProbeCell on a drained irrigation cell across save/load; blackRainWaterHours 0 | stays watered until its day runs out; 0 reads watered=False at once |
| ALLOWLIST_DIAGNOSE_BARE_MIXED_PATCHES | on a Pyrelands map with a MixedBiome mutator, log `outPlants` before and after the WildPlantAllowlist postfix at about 20 mixed cells, then count what grows | if the count is 0 after the postfix and the cells stay bare, CONFIRMED (fix: add RM_FE_Plant_EmberGrass / RM_FE_Plant_Quickgrass) |
| TRIBES_LOOKUP_DIAGNOSE_FIRST_ONE_FALLS | after the PyrelandsMechanics deploy: fire-tribe incidents still resolve on the start save (one TribeCivil) | no regression; the two-tribe case is latent |
| PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK | quicktest: pin, release, re-pin; then `human_review.py --release-pens` on `RM_pyre_review_20261015_r2` | `released` == selected with no Wait after it; animals move but stay in their pens; re-pin restores S/E/N/W |

## 5. FlowWorks

The walk fixes landing today belong to other BENCH agents, who own their own live checks (PIT_LIP_FIX_BOAR_HANGS_OUT,
FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY, the litres re-base, hose joints). For the release, after their DLL lands:
`validation_v2 --live` on `RM_TestSite_calm_v1` (baseline 61/61) and river `extension_proof --site river` (baseline 20/0/1).

## 6. After the run

Use `rimflow verify` per suite and `rimflow close` per item with the run's sha, then restore the owner's
ModsConfig. Release packaging: the GSS 1.0.0 CHANGELOG names the packaged DLL hash. **FlowWorks 1.0.0 is stale** (its
DLL has changed many times today); add the same DLL-hash line to `src/RimMandrake/FlowWorks/CHANGELOG.md` once the walk
items settle. Pyrelands ships inside `mandrake.rm.biomes` (compose).
