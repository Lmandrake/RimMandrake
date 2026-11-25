# WB-pipeline-bridge-20261125-192133 state

Worker run 1 on SteveDesktop, 2026-11-25 11:22 AM to about 1:15 PM PST (context 420k at its save). Run 2 (restart 1)
from 1:20 PM PST: context 150k at start, 330k at this save (window 1M, line 500k). Restart from here.

## What the next context must know
- Run live checks as SteveDesktop lane jobs, not by hand: Steve1 and Steve2 are the lane's busy games. Every member
  clause has a committed proof line in `infrastructure/state/live_proofs/<ITEM>.txt`, mostly
  `src/RimMandrake/Utils/modcheck/live_queue/bridge_bundle_proof.py <CLAUSE>` (offline verdicts:
  `selftest_bridge_bundle_proof.py`). Submit from Archmagi with the `submit` verb, never `ask` (ask reads proof files
  from Archmagi's seat clone, which lags, and needs host facts). Never move that clone (lesson 20261125T213419Z):
  `ssh mandrake@archmagi-wsl 'cd ~/rm/bench && git fetch -q origin; python3 src/RimMandrake/Utils/testq/testq.py submit <ITEM> --for-item <ITEM> --sha <published sha> --proofs <A1,..> --profile tier:<tier> --purpose fix --by BENCH --timeout 21600 --deploy <Mod> ...'`.
  Tier mods__base deploys GimmeSomeSlack. Tier ratchet_pilot deploys GimmeSomeSlack FlowWorks HugeThings
  LuminousPigment RimMandrake.Biomes MandrakePatches WeatherSuite SWBestiary UtinniPatches. Tier pyrelands deploys
  RimMandrake.Biomes UtinniPatches SWBestiary MandrakePatches.
  Results: `/mnt/d/RimTest/testq*/attempts/<job>.a1/result.json` and `proof_<clause>.log` (the python3 run fails to
  reach the bridge first, then the python.exe rerun gives the verdict line). Record
  `rimflow verify <ID> --criterion <C> --level <its level> ...` yourself, WITHOUT `--sha`.
- Level L4 = the owner level. FOUNDRY put it on agent checks. A criterion tagged L4 cannot take an L2 verify. AWARENESS
  waits to 2026-12-02 for the Conductor to re-level A1 (a looser bar is his act); BRIDGE_TARGETS, COMPANION_PROFILE and
  TPS_HOOKS carry `REFUSED BY BUNDLE (the L4 level only):` notes, which work_bundle.py reads as refusals since 68f9e2c4c2.
- Raid tests are paused (`src/RimMandrake/rimflow/raid_pause.py show`).
- The Pyrelands review keeper save fixture is staged at `/mnt/d/RimTest/data/fixtures/RM_pyre_review_20261015_r2.rws`
  (a copy from ArchBig's Saves; PEN2 copies it into the lane game's Saves as bundle_pen2_review).
- Evidence of run 1's hand sitting: `/mnt/d/ClaudeWork/rimmandrake/bundles/WB-pipeline-bridge-20261125-192133/`.

## Done
| member | outcome | commit / reading |
|---|---|---|
| (no ticket) SteveDesktop lane: a `python3` proof line could not reach the bridge | fixed, live | aa1f34fac8 |
| (no ticket) map_awareness_proof A1 read HAR's kept kind as FAIL | check repaired | 20e97d2bef |
| (no ticket) rimbridge_client refused the reserved expect* arguments | fixed, live | e7bc9e242e |
| (no ticket) live_queue proofs gave up on a game at the main menu | fixed | e0b6a7f331 |
| (no ticket) VITALS tier makeup count refused the true 19-mod tier | check repaired | 9cffc6f84a |
| (no ticket) work_bundle read `REFUSED BY BUNDLE (qualifier):` as no outcome, so 4 members relaunched | fixed | 68f9e2c4c2, red then green |
| (no ticket) vitals_overhead off reps ran armed (the client's fast path is safe_advance, which auto-arms) and the busy spawn asked 60 of a 50 cap | fixed | 60903e56a9, fake-bridge selftest red then green |
| BRIDGE_CALL_EVIDENCE, NORTHSTAR_GAPS, TILE_TEMP, STATIC_CALL, TPS_REGULAR, FRAME_HIST, VISITOR_DETECTORS | done | run 1 |
| KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES | done | KEEPER clause 4b55f6c56d; lane J20261125T213350Z-5794cc PASS (83 keepers) |
| LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE | done | lane J20261125T213405Z-6be005 PASS (READY pid 11316, receipt, log archived) |
| PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN | done | ORIGIN clause 1e000d6fc9; lane J20261125T213719Z-1266c0 PASS (59 of 59 wild read mapgen > wild-spawner) |
| THING_LOOKUP A4 | PASS | WILDBLOCK clause e47f4fe126; lane J20261125T214000Z-d7ecf6; A2 and A5 REFUSED (no two-pack pawn on any small list; raid pause) |
| AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE | wait to 2026-12-02 | A1 passes at L2; the L4 re-level is the Conductor's act (cbc458cce7) |
| BRIDGE_TARGETS, COMPANION_PROFILE, TPS_HOOKS | REFUSED (L4 level only) | run 1 notes, now read |
| BRIDGE_TPS_CAPTURE_FIXES_1 | REFUSED | C3's overhead half needs the full list (retired until integration) |
| FLYERFRAMES, EXPERIMENT_MANIFEST, HEALTH_METRICS_JUDGE | REFUSED | run 1 |

## Next, in order
1. Read and record the pending lane jobs: VITALS A1 J20261125T213144Z-a67a04 (then REFUSE A2: full list),
   RIMMANDRAKE_PROVE_COMPANION_REFUSALS J20261125T214629Z-889e6f (A1 PLAYTEST, A2 SETTLE, A3 CAMPAIGN; close the item
   with its evidence, naming that refusal (3) is unreachable in vanilla: Pawn_InventoryTracker's ThingOwner has
   maxStacks 999999, so GetCountCanAccept returns the whole count; (4) flight maintain is owner-present only), PEN A2
   J20261125T215320Z-1ff6a7. Class any non-pass (mod, check or scene) and repair.
2. BRIDGE_TPS_REVIEW2_FIXES_1 C3: the controlled interruption matrix, items 1 and 2 of design/RimMandrake/tps_record.md
   §Acceptance (the doc rewrite puts item 3 in C4), read from the record files (tps_record.py, tps_observer.py), with
   jawa/tps_test_block (0.5-120 s main-thread blocks): 2-10 s hitches and 40/90 s blocks as ONE incident each, a save
   as a longevent, a hang plus kill leaving silence rows and an exited-without-shutdown observer row, forced kills near
   segment boundaries. The observer is a Windows scheduled task ("RimMandrake\TPS Observer", Archmagi, every 2 min);
   on SteveDesktop run it by hand (`python.exe src/RimMandrake/Utils/tps_observer.py --print`; under WSL it declares
   no exit). ArchBig was FREE at 1:50 PM PST.
   C4 (full list): REFUSE.
3. Step 4 fresh reader over this run's changes: 68f9e2c4c2 (work_bundle.py), 60903e56a9 (vitals_overhead.py), and the
   bridge_bundle_proof.py clauses KEEPER, ORIGIN, WILDBLOCK, PLAYTEST, CAMPAIGN, SETTLE, PEN2.
4. Polish lines from run 1's fresh reader (one line each, no ticket): the rerun tail mixes the first run's text; mixed
   python.exe/python3 lines rerun their python.exe parts; TPS/FRAME/HOOKS leave the game Paused.
