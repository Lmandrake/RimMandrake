# FlowWorks + HugeThings live session: one ordered runbook (BENCH, 2026-10-18)

From "game closed, BENCH holds the bridge" to "both live runs done, owner saves written, FULL list restored".
Written OFFLINE while FOUNDRY held the game: every command below was run only as a plan / `--dry-run` / `--mock`.
Plan behind the rows: `design/RimMandrake/flowworks_live_session_plan_2026-10-18.md`. Paths are repo-relative to
`/home/mandrake/rm/bench` (Windows: seat clone, not `D:\Luke\dev\RimMandrake`).
Durations: **M** = MEASURED (log exists), **E** = ESTIMATED.

## 0. Four things this runbook corrects (read first)

1. **`modlist_swap.py --minimal` is the WRONG list for this session.** MINIMAL (26 mods, md5 `bf2fa439...`) has no
   `mandrake.rm.gimmesomeslack`, no HugeThings, no Biomes, no Large Pawns, and carries the 20-odd-mod worldmap stack
   (alienworlds, outerrim, toolbox, HAR, ionweapons...). `live_session.py` B0 marks `B0_tier_truth` UNMEASURED when more than 40 mods run
   and its verify lines take `--config min-<running count>`. Use the tier builder instead:
   `modset_builder.py --tier flowworks` (11 mods) and `--tier flowworks_hugethings` (15 mods).
2. **MINIMAL still lists retired `sarg.alphabiomes`.** It matters only if someone uses MINIMAL: Alpha Biomes is not
   in the Steam `Mods` folder (checked), so the entry is a missing-mod error, and the `flowworks` tiers explicitly
   FORBID it. It does not matter for this runbook. Fix owed to whoever owns MINIMAL (not edited here).
3. **The `--compose biomes` deploy is no longer 492 files.** Dry-run now: 3 changed files (1 added texture
   `RM_NoothelmPlant_StandIn.png`, `RM_Salvessa.xml`, `RM_TwilightLightPlants.xml`), all donor-free fixes from
   FOUNDRY (`d0e00ddd3a`). NOT part of this runbook unless FOUNDRY agrees (step 1c).
4. `modset_builder.py --tier` text for `fw_gss_sitting` still says Biomes "hard-depends on sarg.alphabiomes". That is
   stale (the 13-mod closure printed above contains no Alpha Biomes). Harmless, but fix the prose.

## 1. Pre-flight (game still FOUNDRY's: dry-runs only)

Recorded 2026-10-18 evening. `H` lines are held by `src/DEPLOY_HOLD.txt` (left as-is in game).

| plan | summary | note |
|---|---|---|
| `deploy_custom_mods.py --mod FlowWorks` | 142 held; 1 add `Patches/Pits/FlowWorks_ClimbingGearRaiders.xml`; 4 changed: `Assemblies/RimMandrakeFlowWorks.dll` + `.srchash`, `Defs/Pits/ThingDefs/RM_SuspensionBridges.xml`, `Languages/English/Keyed/FlowWorks_Keys.xml`. Also "rewrote 5 MayRequire guards in 2 files (deployed copy only)" | BENCH's; DLL is a game-closed write (companion rule: the DLL is locked while the game runs) |
| `--mod HugeThings` | 3 changed: `Assemblies/RM_HugeThings.dll` + `.srchash`, `Languages/English/Keyed/RM_HugeThings.xml` | BENCH's |
| `--mod UtinniPatches` (RimUtinni, climbing-gear Jawa patch) | 10 held; 2 add: `Patches/ClimbingGear_JawaFactions.xml` (BENCH's, owed for FlowWorks raiders) and `Textures/Things/Plant/RUT_LungerFry/RUT_LungerFry_StandIn.png` (FOUNDRY's donor-free fix `d0e00ddd3a`); 1 change `Defs/ThingDefs_Items/RUT_GreentideFish_Items.xml` (FOUNDRY's); 1 `-` `Defs/IdeoSymbolDefs_placeholder` in game, not in repo, kept (no `--prune`) | **Mixed seats.** Apply the whole mod only if FOUNDRY agrees; it is 3 of 4 their files |
| other mods touched today (Abyss ... WeepingStones, 31 folders) | NOT per-mod deployable: they ship composed in `mandrake.rm.biomes`. See `--compose biomes` | FOUNDRY's |
| `--compose biomes` | 3 changed files (item 3 above) | FOUNDRY's; skip |
| `bridgetools/build.py --gm` (companion) | game copy `66d7919a91df`, this build `99da7420edf4` (different commit; deterministic per commit). Needs a shutdown window; session needs it for `jawa/fishing` (B4 fish roll, row 31) and the owner-review kit tools | `--apply` only with the game DOWN |

Offline script checks (all green, 2026-10-18 evening; result lines in section 5).

Anything surprising: none blocking. `git status` shows `JawaBenchPawnKitTools.cs` and the FlowWorks DLL/srchash modified but
uncommitted in this clone at the time of the snapshot: **commit or confirm them before `build.py --gm` / the DLL deploy**
(`build.py` refuses a dirty tree without `--allow-dirty`; the DLL's `.srchash` must match its committed source).

1c. Ask FOUNDRY (one interrupt, only if they are still holding): "BENCH deploys FlowWorks, HugeThings, UtinniPatches
(3 of 4 files yours) and the companion in the next shutdown window; is `--compose biomes` (3 files) yours to apply
at the same time?" Absent an answer, deploy only FlowWorks + HugeThings + companion and leave UtinniPatches and biomes.

## 2. Ordered steps

Wall-time total: **E ~2 h 15 min** (breakdown at the end). Every launch is followed by the Player.log gate (2.L).

### A. Take the game
```
python3 src/RimMandrake/rimflow/cli.py bridge who                      # or: ./bridge   (owner-only to set)
python3 src/RimMandrake/rimflow/cli.py bridge take --for "FlowWorks + HugeThings live sitting"
./game                                                                    # measures; must say the game is down or FOUNDRY has released it
./game --why "FOUNDRY released; BENCH deploying" deploying
```
If the game is still running (it was at 21:30 on 2026-10-18): STOP. Closing it is the owner's / FOUNDRY's call, not a helper's.
Closing the game, then: `./game --why "game closed for deploy window" down`.

### B. Deploy (game DOWN only; each is plan first, then apply)
```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks       # re-read the plan: expect the 5 lines above
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod HugeThings --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod UtinniPatches --apply   # ONLY with FOUNDRY's yes (step 1c)
python3 src/RimMandrake/bridgetools/build.py --gm                        # plan; then:
python3 src/RimMandrake/bridgetools/build.py --gm --apply                # companion DLL; game must be down
```
E 1-2 min total (M: a mod deploy is seconds; the companion build is the long pole, E 60-90 s).
Re-run each plan and require "no drift" for the mod just applied (a held-only listing is fine).

### C. Swap to the FlowWorks tier (NOT `modlist_swap --minimal`)
```
python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks               # plan: 11 mods
python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks --apply      # backs up live (md5), records the restore marker
python3 src/RimMandrake/Utils/modlist_swap.py --status                          # LIVE should now read 11 active, FULL unchanged md5 a40bedf5...
```
(`modset_builder` refuses to write while Player.log is fresh, and requires the bridge in the list; both fine here.)

### D. Launch (Steam), wait, gate
```
powershell.exe -NoProfile -Command "Start-Process 'steam://rungameid/294100'"
./game --why "BENCH launch flowworks tier" loading
```
Wait for `Bridge token:` in Player.log with a log newer than the launch (the previous session's token persists until
the new process truncates it). Cold load: **M 44-70 s** for the tier (plan doc); E up to ~120 s. Then `./game --why "tier loaded" up`.

**2.L Player.log first-exception gate (after EVERY launch):**
`Player.log` = `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`
(`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log`).
Read the FIRST exception (tool_traps.md), not the loudest: `grep -n -m3 -E "Exception|Error while|Could not|Resetting mods config" <Player.log>`.
Stop on any of: `Resetting mods config and trying again` (the 6-mod recovery reset: rewrite the list, do not retry),
a FlowWorks / HugeThings / GSS exception, `Could not resolve cross-reference` naming our mods. Copy the log to
`Transient/live_session/<stamp>/Player.log.copy` for `--player-log` (thirst T1/T7 read it).

### E. Preflight
```
python3 src/RimMandrake/Utils/preflight_bridge.py --tier quicktest --modset flowworks --purpose test --live --all --no-archive
```
Offline form was started 2026-10-18 and is slow (> 2 min; patched-tree lint); `--live` form is not exercised offline. E 2-5 min.
Take a fresh Playing quicktest map: `rimworld/start_debug_game_ready` (readiness `mapData`, pauseIfNeeded; the call
`test_site_saves.py` uses; MEASURED map creation 2-8 s per the plan; timeout 280 s) or load the clean saved calm map
(`python3 src/RimMandrake/Utils/modcheck/test_site_saves.py load calm`). Without a map the driver's B0 reads UNMEASURED.

### F. FlowWorks live run (the one driver)
```
python3 src/RimMandrake/FlowWorks/northstar/live_session.py --dry-run          # last look at plan + zones (offline, 1 s)
python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- \
  python.exe src/RimMandrake/FlowWorks/northstar/live_session.py --player-log <path to Player.log.copy>
```
E **47 min** (`--dry-run`: "ESTIMATED wall for the selected blocks: 2826 s"), +60-70 s for tier load already counted in D.
Block times (E): B0 preflight 1 min; B1 validation_v2 ~4-5 min (M: 209-310 s for 14k ticks); B3 serial scripts
~10 min (M: sprinkler 59 s, proof_hose 526-685 s full / realflow ~147 s); B4 shared clock ~3 min; B5 cold snap ~3 min;
B6 flood ~1.5 min; B7 save+reload ~40 s; B8 raid ~6 min; B9 owner save ~4 min; B10 thirst tail ~7 min.
Outputs: `Transient/live_session/<stamp>/{session.json,verify_lines.txt}` (lines are WRITTEN, not run; read the evidence first).
Emit progress at least every few minutes (600 s silence kill; the driver prints a line per block).
`--only` is a PARTIAL run: never recordable. Do not use for the real run.

### G. Owner save (inside block B9)
`save_guard` wraps the run: it snapshots keepers, requires the current slot to be `none` (a quicktest), and verifies afterwards
that the named save is new and every keeper is unchanged. If it exits 1: name the changed keeper, restore from
`D:\Luke\dev\_rmscratch\save_keepers\<sha256>.rws` via `save_guard.py restore`. Tell the owner the save's complete native path
(`session.json` records it).
Per `thirst_live.py`'s own docstring B10 paints every potable water cell to Soil: **never save the map after B10**.

### H. Thirst T15/T16/T27 on the Biomes tier (`fw_gss_sitting`, 13 mods) -- coordinator addition
These three rows need `mandrake.rm.biomes` (SITE/UNMEASURED on the `flowworks` tier, commit `58e9f914a5`). Needs a second
launch (game down first: end the game, `./game --why "FlowWorks run done" down`).
```
python3 src/RimMandrake/Utils/modset_builder.py --tier fw_gss_sitting --apply
powershell.exe -NoProfile -Command "Start-Process 'steam://rungameid/294100'"        # then gate 2.L
# fresh quicktest / calm map as in E
python.exe src/RimMandrake/FlowWorks/northstar/thirst_live.py Transient/<dir>/thirst_biomes.json --only T15,T16,T27
```
Records as `fw_gss_sitting`, never flowworks-minimal. E: launch M 44-70 s (13 mods; larger Biomes closure, E up to ~3 min) +
thirst rows E ~67 s of game time (4000 ticks) + map ~8 s, ~6 min total. Needs the composed Biomes mod as deployed
(the 3-file `--compose biomes` drift is textures / plant defs, not thirst code).
⚠️ **`thirst_live.py` has no `--dry-run` or `--mock`**: UNEXERCISED OFFLINE (only `--help`). Its own T15/T16/T27 SITE guard was added
in `58e9f914a5`; the first live attempt is its first run.
Alternative to save a launch (not tested): run the whole of F on `flowworks_hugethings` (15 mods, includes Biomes); but then
every FlowWorks row records as `flowworks_hugethings`, not flowworks-minimal, so it is a ruling, not a shortcut.

### I. HugeThings tier
```
python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks_hugethings          # plan: 15 mods (adds Large Pawns, HugeThings, Luminous Pigment, Biomes)
python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks_hugethings --apply   # (game must be down; then gate with step D launch + 2.L)
python3 src/RimMandrake/HugeThings/northstar/walls_slots_live.py --dry-run
python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe src/RimMandrake/HugeThings/northstar/walls_slots_live.py
```
E **25 min** run (`--dry-run`: 1500 s) + launch (E 60-120 s, Biomes in closure) + map. Outputs
`Transient/walls_slots_live/<stamp>/{session.json,verify_lines.txt}`. `--long-restless` waits out the A5 meter
(~27,600 ticks at the mocked rate); default infers it, so A5 breakout stays UNMEASURED/OWED unless asked for. Row `A6_roof_collapse_vanilla`
is OWNER EYES (a joint look; the mid-squeeze save is owed to it).

### J. Restore FULL and release
```
python3 src/RimMandrake/Utils/modlist_swap.py --restore            # plan
python3 src/RimMandrake/Utils/modlist_swap.py --restore --apply
python3 src/RimMandrake/Utils/modlist_swap.py --status             # LIVE md5 must equal FULL md5 (a40bedf57526453008d2269039f9f1cd), 542 active
```
(`modset_builder.py --restore` restores the pre-swap before-copy md5-verified; `--restore-full` writes FULL.LATEST; use
whichever matches; after either, `--status` must say "live currently matches: FULL".) If the md5 differs, STOP and report;
do not hand-edit. Then:
```
./game --why "sitting done, FULL restored" down       # or leave up if the owner wants the game
python3 src/RimMandrake/rimflow/cli.py bridge release
```
The full 542-mod list is a ~15 min cold load; do NOT relaunch it unless asked.

## 3. Time budget

| step | E / M |
|---|---|
| A take + B deploy (+companion) + C swap | 3-5 min (E) |
| D launch (flowworks) | 1-2 min (M 44-70 s) |
| E preflight + map | 3-6 min (E) |
| F live_session | 47 min (E from `--dry-run`) |
| H thirst on `fw_gss_sitting` | ~6 min (E) |
| I HugeThings: swap + launch + run | ~28 min (E) |
| J restore + release | 2 min (E) |
| gates, copying logs, reading verify lines, owner-save message | ~20 min (E) |
| **Total** | **~2 h 05-2 h 20** |

Owner time: the saves are only for his eyes after; nothing here waits on him except closing / launching if FOUNDRY
or he says so.

## 4. Open items for this runbook
- MINIMAL list: add nothing; it is not this session's list. Its dead `sarg.alphabiomes` should come out when someone re-captures MINIMAL.
- `fw_gss_sitting` tier prose is stale about Alpha Biomes.
- `thirst_live.py` has no offline mode.
- Uncommitted FlowWorks DLL / `JawaBenchPawnKitTools.cs` in the tree at snapshot time (see section 1).
- `preflight_bridge.py --live` untested offline; the offline form is slow.

- **Uncommitted suspension-bridge edits in `src/RimMandrake/FlowWorks/Source/Pits/Suspension/*.cs`, `RM_SuspensionMath.cs`, `SuspensionBridgeChecks.cs`** at snapshot time (another window's, not BENCH-helper's): the FlowWorks DLL must be rebuilt from a clean committed HEAD before step B, or the `.srchash` will not match.
- Preflight to rerun for real with `--live` plus `--deep` once the game is the tier; expect O01/O04/O09/O13 to clear after steps B-D, O10 to need `--accept-deps` by a human decision.

## 5. Offline verification results (2026-10-18 evening)
| script | mode | result |
|---|---|---|
| `FlowWorks/northstar/live_session.py` | `--dry-run` | rc 0; "ESTIMATED wall for the selected blocks: 2826 s"; "DRY RUN: no bridge touched." |
| same | `--mock` | rc 0; `DONE 49 rows {'UNMEASURED': 40, 'PASS': 1, 'SKIP': 8}`; B10 thirst_live SKIP ("no --mock in thirst_live.py; live only") |
| `FlowWorks/northstar/selftest_live_session.py` | selftest | `PASS: 0 failure(s)` |
| `HugeThings/northstar/walls_slots_live.py` | `--dry-run` | rc 0; "ESTIMATED wall ... 1500 s"; "Kernel mirror selftest: clean" |
| same | `--mock` | rc 0; `DONE 114 rows {'PASS': 111, 'UNMEASURED': 3}`; "A mock verdict proves the script's paths, never the game." |
| `HugeThings/northstar/selftest_walls_slots_live.py` | selftest | `FAILS: 0` |
| `Utils/selftest_save_guard.py` | selftest | `15/15` |
| `Utils/modset_builder.py --tier flowworks / flowworks_hugethings / fw_gss_sitting` | plan | 11 / 15 / 13 mods, "plan only" |
| `Utils/modlist_swap.py --status / --minimal` | plan | LIVE=FULL 542 active md5 `a40bedf57526453008d2269039f9f1cd`; MINIMAL 26 |
| `bridgetools/build.py --gm` | plan | `closure_scan: clean`; state differs by commit only |
| `deploy_custom_mods.py` FlowWorks / HugeThings / UtinniPatches / `--compose biomes` | plan | drift 5 / 3 / 4 / 3 files (section 1) |
| `FlowWorks/northstar/thirst_live.py` | `--help` only | NO dry-run / mock: UNEXERCISED |
| `Utils/preflight_bridge.py --tier quicktest --modset flowworks --all` | offline (run as seat FOUNDRY label) | VERDICT NO-GO, all expected before the swap: O01 game UP, O04 live list is FULL (542) not the tier, O09 companion deployed `66d7919a91df` != repo `99da7420edf4` (no `.srchash` beside the repo artifact), O11 bridge lint snapshot 3.7 d old (7 companion tools incl. `jawa/fishing`, `liquid_look_*` absent), O13 FlowWorks 8 files differ from deployed (DLL, srchash, `Defs/Machinery/RM_LiquidWorksScatter.xml`, ...: more than the 5 in `deploy_custom_mods` plan, re-plan before applying), O10 `0Harmony.dll` changed since baseline (Steam update; runs not comparable with older ones), O14 effective_def_lint uncached (`--deep`, ~155 s), O12 two `.cs` not in a csproj (`EpRatesProbe.cs`, `ShippedMatrixProbe.cs`: compile into nothing, NOT a load blocker). PASS: bridge lease FREE, list sane (11 ids), disk, wedgers |
