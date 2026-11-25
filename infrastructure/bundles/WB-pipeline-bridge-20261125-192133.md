# WB-pipeline-bridge-20261125-192133 state

Worker run 1 on SteveDesktop, 2026-11-25 11:22 AM to about 1:15 PM PST (context 420k at its save). Run 2 (restart 1)
from 1:20 PM PST: context 150k at start, 330k at the first save, about 420k at the second (window 1M, line 500k). Run 3 (restart 2) from 2:29 PM PST. Restart from here.

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
- PEN2's fixture is the Pyrelands site save `/mnt/d/RimTest/data/fixtures/NS_Pyrelands_site_1_417df172fdb5_visit5.rws`
  (its mods are inside tier ratchet_pilot). The 2026-10-15 review keeper records VFE, Alpha Biomes/Animals and
  Pyrelands Mechanics, which no small list loads, so PEN2 builds its own keeper (human_review.py --build --save).
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
| VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL | A1 PASS, A2 REFUSED | lane J20261125T213144Z-a67a04 MEASURED within 10% on every workload; A2 needs the full list |
| RIMMANDRAKE_PROVE_COMPANION_REFUSALS_THE_MINIMAL_LIST_CANNOT | done | PLAYTEST J20261125T220551Z-9be74a, SETTLE and CAMPAIGN J20261125T214629Z-889e6f PASS; full-inventory refusal unreachable (ThingOwner maxStacks 999999); flight remainder RIMMANDRAKE_PROVE_FLIGHT_MAINTAIN_HOLDS_ONLY_STARTED_PAWNS (owner act 1) |
| step 4 fresh reader (run 2) | done | 1 significant finding fixed (89136970f9); nits done in 6ca2e748c0 and 80ede465f9 |
| (no ticket) PLAYTEST scene: the FlowWorks 'fluids' run ended in 4 frames, before the cross-call | scene repaired | 80ede465f9 |
| BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID | done (run 3) | A1 live on Steve1 by hand (a live `claude`-named holder, then this session): refused naming the driver lock, who shows the holder pid, FREE on exit; a99e90a41d (a held --host take exits 75, not 2; an unreachable guard is not called held), 955d54f81c (4 lock selftests were red on SteveDesktop: they now pin RM_HOST=archmagi) |
| PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK | done (run 3) | heat theory refuted (lane J20261125T224621Z-837802: all inside comfortable range); cause RM_JobGiver_ShadeHop rests penned animals 600-1500 ticks by design. b931622136: pen_release counts only a giverless Wait as pinned, census job rows carry startTick/expiry/giver, PEN2 proves its pin reading on the pinned state and reads moves at 600 and 9000 ticks. Lane J20261125T225920Z-f8bd9f PASS (65 released, givers ShadeHop 57, wander 8; 47 moved by 9000) |

## Next, in order
1. Fresh reader (role step 4) of run 3's fixes: a99e90a41d (cli.py --host take exit), b931622136 (JawaBenchPenTools.cs, JawaBenchSituationalTools.cs census, bridge_bundle_proof.py PEN2).
2. BRIDGE_TPS_REVIEW2_FIXES_1 C3: the controlled interruption matrix, items 1 and 2 of design/RimMandrake/tps_record.md
   §Acceptance (the doc rewrite puts item 3 in C4), read from the record files (tps_record.py, tps_observer.py), with
   jawa/tps_test_block (0.5-120 s main-thread blocks): 2-10 s hitches and 40/90 s blocks as ONE incident each, a save
   as a longevent, a hang plus kill leaving silence rows and an exited-without-shutdown observer row, forced kills near
   segment boundaries. The observer is a Windows scheduled task ("RimMandrake\TPS Observer", Archmagi, every 2 min);
   on SteveDesktop run it by hand (`python.exe src/RimMandrake/Utils/tps_observer.py --print`; under WSL it declares
   no exit). C4 (full list): REFUSE.
3. Polish lines from run 1's fresh reader (one line each, no ticket): the rerun tail mixes the first run's text; mixed
   python.exe/python3 lines rerun their python.exe parts; TPS/FRAME/HOOKS leave the game Paused.
