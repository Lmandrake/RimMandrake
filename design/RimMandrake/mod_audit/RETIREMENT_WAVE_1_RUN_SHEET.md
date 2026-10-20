# RETIREMENT WAVE 1: run sheet for the bridge session

One page. Definition, gates and rollback: `RETIREMENT_WAVE_1.md`. Every command runs from the FOUNDRY clone
`/home/mandrake/rm/foundry` **after** `git fetch origin` and a tree equal to `origin/main` for every path used
(`git diff --quiet origin/main -- <path>`); if the clone cannot be brought level, run Windows-side tools from the
read-only mirror `D:\Luke\dev\RimMandrake`. Bridge calls run under `python.exe` (WSL cannot reach the bridge).
Abbreviations: `U=src/RimMandrake/Utils`, `ML=infrastructure/state/modlists`,
`CFG=/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios`.

## A. Before taking the bridge (game DOWN; offline)

State when this sheet was written (2026-10-10 evening): the game is DOWN, but BENCH still holds the bridge lock with
a live process. Wait for `rimflow bridge who` to show it free; never `take --force` over a live holder. The FOUNDRY
clone's HEAD was also behind origin with uncommitted `modaudit/` edits of another helper: bring it level (or deploy
from a clean tree) before W1, because `deploy_custom_mods.py` deploys the working tree it runs from.

```
rimflow bridge who                                    # must be free or yours; never --force over a live holder
./game                                                # measures; must say NOT RUNNING
python3 $U/preflight_bridge.py --tier wave1 --deep    # WAVE1 manifest (ML/manifest.WAVE1.json); expect GREEN
# under python.exe from D:\Luke\dev\RimMandrake (copy the list to D:\ClaudeWork\rimmandrake\scratch\rw1\ first), after W1 deploys:
python.exe src/RimMandrake/Utils/effective_def_lint.py 'D:\ClaudeWork\rimmandrake\scratch\rw1\ModsConfig.WAVE1_CANDIDATE.xml'
#   expect: crash 0; failed_ops = exactly the 2 AncientsAreRakata.xml rows (pre-existing). Save Windows paths with printf, never zsh echo.
```

**A1 backups** (stat the Saves folder before and after; every copy gets a size line in the progress log):
`ModsConfig.xml` -> `$ML/ModsConfig.LIVE_BACKUP_<ts>_pre_wave1.xml`; `$ML/ModsConfig.FULL.LATEST.xml` ->
`$ML/ModsConfig.FULL.PRE_WAVE1.xml` (commit it); the Cherry Picker config (the swap tool writes a PRESWAP copy);
`CANONICAL_ASHKARR_START_2026-09-12.rws` -> `.rws.bak-pre-wave1-<ts>`.

**A2 deploy the offline fixes** (game down: DLLs cannot be replaced while it runs). Plan first, read the `-` lines:
```
python3 $U/deploy_custom_mods.py --mod <M>            # plan; then the same with --apply
  M = Armoury (durasteel catch-all 67153b072: without it FULL.LATEST NREs in Minify at load), StarWarsPatches,
      ResearchRetag, UtinniPatches, Doctrine, GreentideRaidAnt, LuminousPigment
```

**A3 Cherry Picker** (game down; inert until the next start):
```
cp infrastructure/state/cherrypicker/CherryPicker.SHIP.WAVE1_CANDIDATE.xml infrastructure/state/cherrypicker/CherryPicker.SHIP.xml
src/RimMandrake/Utils/land.sh -m "Cherry Picker SHIP: drop the 140 keys of wave-1 mods" infrastructure/state/cherrypicker/CherryPicker.SHIP.xml
python3 $U/cherrypicker_swap.py --ship ; python3 $U/cherrypicker_swap.py --ship --apply
```
(PLUS_SHELLS variant only if `RETIREMENT_WAVE_1.md` §1 admits the shells.)

**A4 save pre-edit** (offline, on a COPY; never the canonical file in place):
```
python3 $U/modaudit/wave1_save_preedit.py "$CFG/Saves/CANONICAL_ASHKARR_START_2026-09-12.rws" "$CFG/Saves/WAVE1_PREEDIT_<date>.rws"          # plan: must list 11 walls + 2 quests
python3 $U/modaudit/wave1_save_preedit.py ... --apply                              # prints OK, delta = bytes removed
```

**A5 the list**: `cp $ML/ModsConfig.WAVE1_CANDIDATE.xml $ML/ModsConfig.FULL.LATEST.xml` (commit with land.sh),
then `python3 $U/modlist_swap.py --restore` (plan) and `--restore --apply`; `python3 $U/modmanifest.py check --manifest WAVE1`
must exit 0.

## B. The one cold load (take the bridge first)

```
rimflow bridge take --for "retirement wave 1 cold load"
src/RimMandrake/bridgetools/launch_and_wait.sh        # exit 0 READY; ~15 min on ~514 mods
python3 $U/preflight_bridge.py --tier wave1 --live
```

**Player.log at the main menu** (`$CFG/Player.log`; read the FIRST exception, not the loudest):
- PASS needs `Bridge token:` and **no** `Resetting mods config` / `Could not recover` (the 2026-10-10 Minify NRE
  signature; Minify is gone now, and the Armoury durasteel fix is deployed).
- No `Could not resolve cross-reference` naming `AM_Cryptoharmonization` (RimAI prerequisite restored) or any
  `AM_`/`VWE_` weapon (renormalise rows removed); no `Patch operation ... failed` from `WeaponTags_Renormalise.xml`,
  `RUT_ResearchRetag.xml`, `RUT_ResearchTabAssign.xml`, `Bones_CutFuelAndPlasteelRecipes.xml`,
  `BetterInfestations_SilenceOwnEvents.xml`, `BiomeCastEvictions_WildBiomes.xml`.
- Allowed, pre-existing: the two `AncientsAreRakata.xml` op failures; Caravan Adventures logs nothing for its 21 absent
  `AM_` bounty races (it already tolerates 31 absent names).
- Count: `measure count-errors "$CFG/Player.log"` and compare to the last full-list baseline; a new error CLASS stops the wave.

**Load the edited save**: `rimworld/load_game_ready` on `WAVE1_PREEDIT_<date>`. Expect the mod-mismatch dialog
(`Dialog_ModMismatch`: the save's meta lists the retired ids) — dismiss it; a `load_game_ready` behind it reads as
a hang. Expected save-load log: `RETIREMENT_WAVE_1.md` §7 (about 2,000-3,000 `Could not load reference` /
`Null key` lines, ~25 `Could not find class`, 5 `Precept_Relic had null thingDef`, drug-policy, auto-slaughter,
scenario-part and 15 default-stuff lines). Anything outside those classes is new: stop, read it, bisect per §4.

## C. Acceptance (game UP, bridge held; `python.exe` + the rimbridge client)

1. `rimworld/list_colonists`: the six founders present; spot-check one VSE colonist (Wim Ateeka) shows vanilla passions.
2. `jawa/running_mods` == `manifest.WAVE1.json` (`python3 $U/modmanifest.py check --manifest WAVE1 --loaded <ids.json>` exits 0).
3. Raid Fee (A4): `jawa/harmony_patches` names no `RaidEnemy` prefix from `leo.raidprotectionfee`; `jawa/fire_raid` produces a raid (pawns arrive).
4. Bones: inspect a BiofuelRefinery's bill list: no `Make_ChemfuelFromBone` / `MakeBonePlasteel`; `MakeBonePlastic` present.
5. Better Infestations: `jawa/forecast_incidents` / `incident_parms_preview` never offers `BI_SwarmingHorde` / `BI_InsectRaid`.
6. **RSW faces (owner: "check in game first, then fix"; FA config has 156 keys, none `RSW_`; `Transient/foundry_face_check_20261010.md`):**
   on a quicktest map, `jawa/spawn_pawn` 2 Jawa and one pawn of each other RSW_ humanlike xenotype; read each back and
   verify the ACTUAL kind and xenotype (spawn tools substitute silently); take close screenshots
   (`jawa/take_screenshot`, framed on each pawn) into `Transient/foundry_face_check_<date>/`; read face state from the
   log/inspect string; write the proposed exclusion shim (which xenotypes, which FA keys) into the face-check report.
   Ticket `RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM`. No fix is applied in this session.
7. Health (C24): `jawa/tps_report` over ~1,000 warmed ticks, `jawa/time_perf`, process private bytes (tasklist), load
   wall-clock (launch to `Bridge token:`), distinct errors (`measure count-errors`): first row of
   `HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME`.

## D. After

Save under a NEW name (`rimworld/save_game`, then stat Saves: a new file appeared, no keeper changed size); reload
it once: 0 `Could not load reference` lines for wave mods. Owner decides whether it replaces `canon.yml`
`planet.start_savegame`. Then: `python3 $U/modmanifest.py capture FULL --from $ML/ModsConfig.FULL.LATEST.xml`;
re-run `assemble.py`, `merge_checks.py`, `python3 $U/run_selftests.py`; `rimflow bridge release`.
