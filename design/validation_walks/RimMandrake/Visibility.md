# Visibility — validation walk
subject: src/RimMandrake/Visibility  (packageId mandrake.rm.visibility)
deps: brrainz.harmony (hard modDependency — already in the minimal list)
list: minimal
status-hint: shared 0-100 `GameComponent` "Colony Visibility" dial, read by a five-band ladder (Hidden/Discreet/Noticed/Marked/Exposed) that multiplies hostile-only raid threat-point sizing via a Harmony Prefix on `IncidentWorker.TryExecute`, plus a launch-reset postfix on `GravshipUtility.GenerateGravship`.

## must be true
- `GameComponent_ColonyVisibility.BandFor(v)`: `<20` Hidden, `<40` Discreet, `<60` Noticed, `<80` Marked, else Exposed (`Visibility/Source/GameComponent_ColonyVisibility.cs:78-84`); default `shipVisibility` starts at 10 (Hidden band).
- `ThreatFactor(v)` evaluates the ruled Annex A curve: 0→0.55, 25→0.80, 50→1.00, 75→1.25, 100→1.60, clamped (never extrapolated) outside [0,100] (`GameComponent_ColonyVisibility.cs:145-163`).
- `ColonyVisibilityRaidPatch` Prefixes `IncidentWorker.TryExecute` and multiplies `parms.points` ONLY for hostile worker types — `IncidentWorker_RaidEnemy`, `IncidentWorker_Infestation`, `IncidentWorker_AggressiveAnimals`, `IncidentWorker_MechCluster` — never for benign incidents sharing the same `IncidentCategoryDef`/`needsParmsPoints` shape (`ProblemCauser`, `ThrumboPasses`, `HerdMigration`) (`Visibility/Source/ColonyVisibilityRaidPatch.cs:17-45`).
- `ResetOnLaunch()` multiplies `shipVisibility` by 0.15, clamped to `[5,15]` — wired as a real Harmony postfix on `GravshipUtility.GenerateGravship` (`GameComponent_ColonyVisibility.cs:111-117`, About.xml: "Ta'Baa's launch reset ... is wired").
- If any of the five reflected vanilla members (`IncidentWorker.TryExecute`, `GravshipUtility.GenerateGravship`/`ArriveExistingMap`/`ArriveNewMap`, `Building_GravEngine.GetGizmos`) is not found, the patch logs `Log.Error` and that ONE hook is skipped rather than the whole mod crashing (`ColonyVisibilityRaidPatch.cs:69,81,105,117,140`).
- The dev-mode debug action `"Set Colony Visibility (dev)"` (category `RimMandrake.Visibility`) sets `shipVisibility` directly to a preset {0,25,50,75,100} and logs the before/after band and `ThreatFactor` (`Visibility/Source/DebugActions_Visibility.cs:19-38`).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.visibility" and no XML error naming Visibility's About.xml (mod ships no Defs)   # load-time
2. [L] `python3 src/RimMandrake/Utils/selftest_colony_visibility.py` exits 0 — covers `BandFor`/`ThreatFactor`/`SeasonsAway`/`DecayedTileVisibility`, all pure math with no `Find.*`/Harmony dependency by design (`GameComponent_ColonyVisibility.cs` header comments)
3. [L] Player.log does NOT contain any of the five "not found by reflection" error strings from `ColonyVisibilityRaidPatch.cs` — proves every reflected vanilla member still resolves against the currently-installed RimWorld build
4. [B] start/resume a colony, use the dev action "Set Colony Visibility (dev)" (or `jawa/spawn_mech_cluster`/an equivalent hostile-incident trigger after directly setting `shipVisibility` via `jawa/inspect_string`/save-edit) at each anchor point {0,25,50,75,100}, then trigger a hostile incident (`jawa/spawn_mech_cluster` is a real bridge tool for this) and confirm the resulting threat points scale by the expected multiplier {0.55,0.80,1.00,1.25,1.60} relative to the un-multiplied baseline — the one thing the offline selftest structurally cannot prove (multiplication happens inside a live `IncidentWorker.TryExecute` call)
5. [D] def read-back is not applicable — this mod ships zero Defs; confirm via live RimDefDump that no def carries `modName` "RimMandrake: Colony Visibility"
X. [S] (human pass) none — a GameComponent stat with no rendered UI beyond the dev-mode menu already exercised in step 4
