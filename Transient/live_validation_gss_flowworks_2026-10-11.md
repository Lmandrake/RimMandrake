# Live validation: GimmeSomeSlack + FlowWorks (post hose port) — 2026-10-11

Driver: BENCH live-validation subagent. Port commits 6b031841a..c704eec4d.

## Pre-port saves

Made 2026-10-11 ~03:25 on the owner's live list (550 active, ModsConfig md5 ee01dae9…; note this is NOT
FULL.LATEST's md5 1ab545a0…, so the restore target is the pre-swap snapshot) with the PRE-PORT GSS loaded,
on a RM_TheRot map. Keepers (CANONICAL_ASHKARR_START, BLAND_NORTHSTAR_BASE, ASHKARR_*, FOUNDER_*, HUGEFIX, HugeThings,
BAZAAR) backed up first; a stat diff of all 182 save files before/after shows exactly 2 new files, 0 changed.

| fixture | file | state at save | old class in save |
|---|---|---|---|
| PP1 carry | `RM_PREPORT_HOSE_MIDCARRY_20261011.rws` (26.4 MB) | reel (60,120) Carrying, trail 3/26, carrier Jathen, job RM_CarryHoseEnd forced, toil 4, order Deploy (86,120) | `RimMandrake.GimmeSomeSlack.Hose.Jobs.JobDriver_CarryHoseEnd` x1 |
| PP2 retract | `RM_PREPORT_HOSE_MIDRETRACT_20261011.rws` (26.5 MB) | same reel Retracting, wound 0.54 of 26.5 cells, job RM_RetractHose forced, toil 3 | `RimMandrake.GimmeSomeSlack.Hose.Jobs.JobDriver_RetractHose` x1 |

Staging trap (harness, not mod): on this list "Out of Combat ReBoost" walks a colonist ~2 ticks/cell, so a 24-cell carry
finishes inside the proof's 60 post-load ticks and PP1 could never see the job. Slowed the carrier with BadBack + Frail
(jawa/pawn_health) -> ~8 ticks/cell, leaving ~180 ticks of carry after the save point. Mud/shallow water did not help
(path avoided it). Staging scripts were scratch (GSS HoseProbe no longer exists after the port).

## Deploy

Game killed by PID 34672 (`./game going-down` / `down` stamped). The bench clone's main had diverged from origin
(3 local commits already landed as patch-equivalents; origin 10 ahead incl. TheRot Ambrosyx + biomes load-order fix), and
the clone carries peers' dirty Transient files, so nothing was rebased: every mod deployed from a `git archive` export of
origin/main **3fcf2f4b6** (scratch), running that export's own deploy_custom_mods.py.

| target | result |
|---|---|
| GimmeSomeSlack `--apply --prune` | 47 files: +RM_PowerTheft.xml, ~About/DLL/srchash, **43 hose files REMOVED** (Defs/Hose x3, Textures/.../Hose x40); empty Hose dirs deleted; VERIFIED in sync |
| FlowWorks | 51 files (+45 incl. hose defs/textures/DLL, ~6); 14 game-only files kept (old result JSONs, 6 already-deployed untracked Doors/Excavation textures) |
| --compose biomes (TheRot, Ollopom DLL via members) | 35 files |
| UtinniPatches | 15 files |
| SWBestiary | 7 files (3 game-only Khorrak textures kept) |
| JawaBench `build.py --gm --apply` | built from bench f036dd7d9 (bridgetools identical to origin), replaced game copy from 1e7fc0876 |
| `run_selftests.py --tier deployed` | GREEN 2/2 (397 skipped by tier) |


## Load

No iteration tier was used: the live list already WAS the owner's full list (550 active, md5 ee01dae9…), so every proof
ran on it directly and no swap/restore was needed (md5 re-checked at the end). Launched via Steam 03:16, `Bridge token:` at
03:35 (~19 min). First exceptions in Player.log are donor ConfigErrors (CannibalPirate / PirateYttakin NRE in
ConfigErrors, a `-1§Vanilla` KeyNotFound post-long-event) — none names FlowWorks, GimmeSomeSlack or a hose type; no
recovery reset.

## GSS proof

`python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live` (hose-free), full list (550 running), fresh
RM_TheRot quicktest map, 03:36-03:47, wall 640 s, certifiable:
**105/105 PASS, 0 FAIL** — preflight 3, matrix 30, core 33, aerial 21, style 12, save_load 3, Z_log_budget PASS
(0 errors naming GSS; 36 control-noise and 37 site-clear errors excluded by the harness's existing rules).
Result: `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json`.
(Last night's pre-port run had 151 rows: the 46 hose rows — 37 hose/maze/relay/carry/style_hose/SL4 + 9 hose matrix
scenes — now live in FlowWorks' proof_hose.py.)

## FlowWorks + hose proof

### proof_hose, full run 04:20-04:34 (`proof_hose_20261011T042312.json`, DLL before the perf fix)

`python.exe .../proof_hose.py --live --preport-save RM_PREPORT_HOSE_MIDCARRY_20261011,RM_PREPORT_HOSE_MIDRETRACT_20261011`,
full list, offline gate run through WSL (0 red, 137 s), fresh map, certifiable, wall 685 s:
**65 PASS, 0 FAIL, 1 UNMEASURED (NS_external_pipe_is_visual_only, by design)** — preflight 2, matrix_hose 9, hose 6,
maze 8, relay 8, carry 8, style_hose 6, realflow 11+1U, save_load 4, **preport 2 (PP1, PP2 PASS)**, Z 1.

- **PP1** PASS: `RM_PREPORT_HOSE_MIDCARRY_20261011` loaded in 19 s, no "Cleaning up invalid job state", no unresolved
  hose class; the colonist is still on `RM_CarryHoseEnd` 60 ticks after load (old driver class
  `RimMandrake.GimmeSomeSlack.Hose.Jobs.JobDriver_CarryHoseEnd` aliased onto FlowWorks).
- **PP2** PASS: `RM_PREPORT_HOSE_MIDRETRACT_20261011` loaded in 28 s, clean, colonist still on `RM_RetractHose`.
  (Same result in run 1: 17 s / 22 s.)

The perf fix below changed the DLL, so proof_hose was re-run on the new build (section "Final state").

### FlowWorks' own live validation (northstar/validation_v2.py --live --fresh-map) — first full-list run ever

v2 had only ever run on the 15-mod `flowworks` tier (last GREEN 59/59, 2026-10-09). On the full list:

| run | result | finding | class | fix |
|---|---|---|---|---|
| 05:23 (bench clone) | ABORT at L2 | `assembly_identity`: the clone's DLL (bd05a8473, built on older source) ≠ the deployed origin build | HARNESS (my run location) | ran from an origin export whose DLL is byte-identical to the game copy |
| same | L2 `settings_default` drift `hoseSettingsImported=True (ship False)` | the hose port's one-time import flag of the old GSS hose settings is flipped by the mod on every upgraded install; v2 compared it as a player setting (site_spec already lists it in INTERNAL_FLAGS, v2 ignored that), and `--reset-settings` would have re-armed the import | HARNESS | v2 skips INTERNAL_FLAGS in drift and reset |
| 05:24 (export) | 58 PASS, **1 FAIL** P4_ladder_frees, 2 UNMEASURED (P4b, E9) | P4: colonist ordered down the lowered ladder stopped on the lip. Reproduced live by hand: with one colonist standing in the 1-cell pit a second ends at (165,100) ("Something ended the job"); once the pit is empty he climbs in. The pit was occupied by P3f's forced pawn (rows P3f/P4f added by 125c2e298, never run live). P4b UNMEASURED for the same reason | HARNESS (staging) | P4f is read before P4, and the freed forced pawn walks out first (its walk-out is now part of P4f) |
| same | E9 UNMEASURED: the expected `conservation exception` warning not seen | **Verse.Log had hit its 10,000-message cap** ("Reached max messages limit" in Player.log; a chatty conversation mod on the full list). Proven live: a `Log.Warning` via jawa/static_call did not reach the journal; after `Verse.Log.Clear` the next one did. Every log-budget row run after the cap was blind — including the 04:20 proof_hose Z (otherErrors 0 where run 1 saw 77) | HARNESS (instrument blind) | `validation_core.log_revive` (Log.Clear + sentinel) at the start of GSS proof_all, proof_hose and v2; `log_alive` sentinel at Z/E9 — dead journal → UNMEASURED, never PASS (GSS selftest gains a can-fail case) |

Harness commit `2c80f7e29`, published **ec10fae93**. The final runs below were made from an export of origin ec10fae93
(FlowWorks + GSS DLLs byte-identical to the deployed copies).

### More instrument/site faults found by the final runs (05:39-06:33)

| run | result | root cause | class | fix |
|---|---|---|---|---|
| GSS proof_all 05:39 (export ec10fae93, log revived) | 105/105 PASS | — | — | — |
| proof_hose 05:56 (same export) | 58 PASS, **7 FAIL** (style_hose R1-R6, RL6, SL4), 1 UNMEASURED | Inspected the run's own SL save: the style site held 14 `RM_HugeTrunkBlocker` cells and no giant inside the rect. Huge Things re-plans a giant plant's trunk blockers whenever they vanish while the plant stands (`Notify_BlockerGone`), so the site prep's destroy was undone by a giant (the Rot's Agarilux/Witches Oyster, footprints just redeployed) standing OUTSIDE the rect → "CanDesignateCell refused: Space already occupied". Map-wide: 5,000+ blocker cells in 215 16-cell tiles on that RM_TheRot quicktest map. RL6 (relay B stayed Flat) and SL4 (reel 1 gone, rubble at (82,69)) were not individually traced; neither recurred once giants were cleared | SITE (R1-R6 proven; RL6/SL4 presumed, unproven) | `V.clear_huge_plants` before every proof_hose block (every plant within 6 cells of a blocker); `prepare_site` reads a surviving blocker as a SITE block. Commit `2603bf069` → **45dea391f** |
| proof_hose 06:15 | **65 PASS, 0 FAIL, 1 UNMEASURED**; PP1/PP2 PASS; Z alive | — | — | — |
| v2 06:26 | **59 PASS, 0 FAIL**, 2 UNMEASURED (L2 log_clean, E9) | **RimBridge's journal is a ring of the last 1,000 entries of every level**, and an intimacy mod on the full list writes ~0.3 info lines per tick (MEASURED: 176 per 600 ticks, "X cannot currently do lovin'"). E7b's conservation warning had scrolled out before E9 read it ("0 warn+ lines since base"), and the `[RimBridge]` start line L2 looks for had scrolled out too. Every end-of-run log budget on this list (GSS Z, proof_hose Z, v2 E9) only ever saw the last ~3,400 ticks | HARNESS (instrument blind) | `validation_core.LogTap`: polled after every `step_game_ticks` any proof bridge makes and at block ends, keeps warn+, counts entries that scrolled out between polls; `lost > 0` → UNMEASURED. L2 accepts the revive sentinel as its journal proof. Can-fail selftests added. Commit `c3a1a129b` → **ec73383a6** |

### Game crash 07:26 (not ours)

During a GSS rerun RimWorld died natively: a MapModeFramework background task (`MapMode_GrowingPeriod.StartCaching`,
via Worldbuilder's `GenTemperature_SeasonalShiftAmplitudeAt` postfix) called `PlanetLayer.GetTileCenter` (Burst) while the
proof was swapping worlds (new quicktest). Donor-mod race on world churn; no FlowWorks/GSS frame. Player.log copy kept in
scratch. Relaunched 07:27 → bridge 07:45; the one in-flight call (`jawa/mod_settings_field`) reconciled `not-applied`.

## Failures: root cause + fix + sha

### Run 1 (`proof_hose_20261011T034753.json`, full list, 03:47-03:56): 53 PASS, 4 FAIL, 1 UNMEASURED

| row | class | root cause | fix |
|---|---|---|---|
| MATRIX_HOSE_block (9 MX_H0* scenes) | HARNESS | `load_catalog("design")` needs `design_spec` (numpy); under python.exe run_live's import leaves `D = None`. proof_hose's live mode also never ran its offline gate (GSS proof_all runs its gate in WSL and hands the live side a catalog JSON) | gate now writes the catalog JSON (`D:\Luke\dev\_rmscratch\fw_hose_proof\scenes_design.json`); live mode runs the gate through `wsl.exe` like GSS and reads the JSON |
| NS_hose_carries_real_units | HARNESS | flat 260-tick window from the lay is shorter than the design's own contract (FINAL §3.6/G6.4: discover ≤ 60 ticks, transfer by the NEXT 250-tick pump cycle = up to 310). Evidence in the same run: netLink present at +260, 0 units, then the hose plumped at +350 — flow started just after the window. Scene 2 (same geometry, read after 321 ticks) PASSED | bar now reads the contract itself: discovery tick (≤ 60, stepped 5) then units within one cycle (≤ 260) of discovery — stricter per half, not looser |
| NS_hose_far_end_pump | HARNESS | same 260-tick window (route pump→hose→tank discovered, 0 units at +260) | same contract read |
| NS_relay_chain_carries | HARNESS | staging: hose A aimed at the cell WEST of relay B (a free end, not a relay; validation_hose RL3 aims ONTO B's SW footprint cell), and reel A's un-fed west lead-out (~4.4 cells) ran onto the unprepared 2-cell gap between plots → refused "no room for the straight lead-out" | aim A at B's footprint; prepare 6 extra cells west of every plot |
| NS_external_pipe_is_visual_only | UNMEASURED by design | the row is hard-wired UNMEASURED (offline kernel row is its evidence) | none |

### Debug runs (realflow/matrix only, `--only`, 04:06-04:25)

- Run 2 (matrix_hose,realflow): matrix 9/9 PASS from the gate's JSON; realflow all PASS except NS_relay_chain_carries
  (relay now correct, relayTo = B, B discovered at 0, but 0 units in 260 ticks).
- Re-staged the relay scene by hand on a spare plot and traced the pump every 10 ticks: **the pump read powered=false for
  ~130 ticks after build + battery charge** (vanilla's power net switches a new consumer on later), so a pump cycle in that
  gap moved nothing; once powered, the first cycle moved 5 units through A -> B -> tank (credits 1 each, both Plump).
  The chain works — HARNESS again: every real-flow clock started before the pump had power. Fix: `_powered()` waits for the
  pump (pump_scene, scene 3's far pump, scene 5) and the row records `pumpPoweredAfterTicks`.
- Run 3 (realflow): **14 PASS, 1 UNMEASURED (by design)**; power-up measured 140 / 100 / 170 ticks; transfer after
  discovery 50 / 160 / 190 ticks (all <= one 250-tick cycle).

Fixes committed `7c5abdecc`, published **613a7d16e**.

No mod bug found in the realflow rows. One lead, not a measured defect: `Building_LiquidPump.TryDraw` increments `Moved`
and has already taken the channel level when `tank.TryAddLiquid` returns false (the level is then lost); TankToFill should
make that unreachable, but nothing asserts it.


## Perf

Instrument: `jawa/map_comp_timing` (JawaBench, per-MapComponent prefix/finalizer timers over N real ticks at Normal speed).

**Before (old DLL), 04:36**: the PP2 fixture map after its load (RM_TheRot, 23 reels, 11 laid, 2 Plump, 0 pumps/tanks),
1214 ticks: `RM_MapComponent_Hoses` **0.152 ms/tick mean, max 4.6 ms** — 3x the FINAL §3.5 budget (≤ 0.05 ms/tick for
20 reels, 4 pumps, 10 tanks), with no pumps at all. Whole map: 0.64 ms/tick summed over 236 patched components;
the hose component was 2nd (after HugeThings' MapComponent_HugeFootprints 0.308).

**Root cause — MOD BUG (perf):** each laid reel's every-250-tick obstacle check called `CorridorHash(World(), lay)`;
`World()` rebuilds a whole-map CordWorld (62,500 cells + every plant) and is cached only per tick, but every reel runs its
check at its OWN tick (`(now + thingID) % 250`), so the cache never hit: one ~4 ms scan per laid reel per cycle
(11 × ~3.5 ms / 250 ≈ 0.15 ms/tick — matches). It grows linearly with laid hoses. The offline perf model (SelfTest
HoseNetCacheChecks, 0.00105 ms/tick) modelled the net walk and index rebuild, not this snapshot.

**Fix:** `CorridorHashLive` reads the same per-cell rule (`LiveCellSig`) straight off the map for the corridor cells only
(bbox ± 2); World() is now built only when a hose actually re-lays. New probe verb `corridor` compares the live hash with
the snapshot hash for every laid reel (a mismatch would force a re-lay every cycle); census gains `worldBuilds` /
`liveCorridorChecks`. FlowWorks C# SelfTest 175/175 + hose 344/344 on origin + fix. Commit **e64a8af8a** (built on
origin 83aa7c200 incl. FOUNDRY's P6-P14 FlowWorks work; the bench-local bd05a8473 is the same source change).

**After (e64a8af8a deployed, relaunch 04:46-05:06):**

| map | reels / laid / pumps / tanks / pipes | ticks | RM_MapComponent_Hoses ms/tick (max ms) |
|---|---|---|---|
| PP2 fixture map (same scenario as "before") | 23 / 11 / 0 / 0 / 0 | 1203 | **0.024** (0.37) — was 0.152 (4.6) |
| proof map save `RM_fw_hose_proof_20261011051723` | 30 / 18-19 / 6 / 8 / 5 | 1509, 1501 | **0.032 (0.12), 0.037 (0.54)** |

Budget ≤ 0.05 ms/tick: met on a map larger than the budget's 20 reels / 4 pumps / 10 tanks. Probe `corridor`: live hash ==
snapshot hash for 11/11 and 19/19 laid reels (no forced re-lays); stepping 750 ticks paused: worldBuilds +0, relays +0,
liveCorridorChecks +57. (Not covered by this instrument: the pumps' own ThingTick — the net walk runs once per pump cycle,
cached per origin per tick, step 7.) The JawaBench test profile had expired at 12:00Z (05:00 PDT) — `map_comp_timing`
was refused as CAMPAIGN; renewed `companion_profile.json` to expire 15:00Z (same keys, same campaignSaves).

## Lessons

Filed (infrastructure/state/lessons/): `…staggered-check-defeats-per-tick-cache`, `…fresh-pump-power-up-gap`,
`…full-list-log-budgets-are-blind`.

- The owner's "mostly ceremony" verdict is half right again: of 12 distinct live findings, **1 is a mod bug** (the hose
  perf defect, fixed, 6x faster) and the rest are harness/site/instrument faults — but two of those (the Verse.Log cap and
  the 1,000-entry journal ring) mean **every earlier full-list log-budget PASS was partly blind**, including last night's.
- Full-list quicktest maps on the current tile are RM_TheRot: giant fungi with Huge Things footprints cover the map
  (5,000+ trunk-blocker cells); any site prep must clear the giants, not just the rect.
- Proofs that were only ever run on the 15-mod tier (FlowWorks v2) carry tier assumptions (journal start line, settings
  set, pawn staging) that break on the full list; P3f/P4f had never run live at all.

## Final state

Final proofs, all on the owner's full list (550 running), all from an export of origin **ec73383a6+** (harness at
91f23b895 / 4a4978499; FlowWorks DLL e64a8af8a and GSS DLL byte-identical to the deployed copies), journal tap complete
(lost 0) and log sentinel alive in every run:

| proof | result | file |
|---|---|---|
| GSS `proof_all.py --live` 07:47 | **105/105 PASS**, certifiable; Z tap 136 polls, 0 lost | `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T074701.json` |
| FlowWorks `proof_hose.py --live --preport-save …` 08:00 | **65 PASS, 0 FAIL, 1 UNMEASURED** (NS_external_pipe_is_visual_only: hard-wired, needs a VE PipeSystem pipe), certifiable; **PP1 PASS (17 s), PP2 PASS (19 s)**; Z tap 456 polls, 0 lost, 68 foreign errors, 0 naming the hose/FlowWorks | `src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T080050.json` |
| FlowWorks `validation_v2.py --live --fresh-map` 08:10 | **GREEN 61/61** (first full-list GREEN) | `src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T081718.json` |

Perf: RM_MapComponent_Hoses 0.152 → **0.024** ms/tick (same map), **0.032 / 0.037** on a 30-reel/6-pump/8-tank map
(budget 0.05). Mod list never swapped: ModsConfig md5 ee01dae9… before and after. Game left UP on the full list
(PID 20088). JawaBench test profile renewed to expire 17:00Z (it lapses by itself). Pre-port fixtures kept in Saves:
`RM_PREPORT_HOSE_MIDCARRY_20261011.rws`, `RM_PREPORT_HOSE_MIDRETRACT_20261011.rws`. Bridge released after this log lands.

