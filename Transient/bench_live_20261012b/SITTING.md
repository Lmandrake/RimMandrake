# BENCH live sitting 2026-10-12b (overnight pass 2, owner AFK): Pyrelands split run, FlowWorks witness/canal/weir, GSS regression

Harness: every live script runs from a `git archive` export of **9905d543b3** (src/RimMandrake, infrastructure, Transient/modcheck,
Transient/northstar) at `D:\Luke\dev\_rmscratch\bench_live_20261012b` (claude_sha.txt).

## Deploy
Game was down at start (owner list, md5 ee01dae9 = ModsConfig.owner_before.xml; Prefs autosave 0.25, runInBackground True).
Plans then `--apply` (deploy_plan_* / deploy_apply_*.txt):
| mod | deployed | md5 repo == game |
|---|---|---|
| FlowWorks | DLL + srchash | RimMandrakeFlowWorks.dll a9c8e76bfdb5fccde7ba0a44fd261bca |
| Pyrelands (compose biomes) | FireEcologyHook.dll + srchash, PyrelandsGenSteps.xml, BiomeDefs/Pyrelands.xml (all 0b14ffc5fa) | DLL 0f867dd16b7eaa1bef2d0182df6a13d0; GenSteps c0b5ce92b6f40225d0b3542a2d4a0c38 |
| MandrakePatches | Patches/HeadSetForFA_Revive.xml (FindMod guard) | 17bc9b2ee93533da7663a4065a7506e9 |

Tier: the 2026-10-12 file `ModsConfig.ratchet_pilot_plus_patches.xml` (modset_builder ratchet_pilot still = the same 22, plus
mandrake.rm.patches last = 23). Launched via Steam, bridge token after 120 s.

## Results
### FACE_PATCH_FIX_ADDS_TO_A_GHOST — PASS (noted; item already done)
Startup log (Player.pilot_startup.log): 0 `FaceAdjustmentDef` lines. The error/failed line set vs the 2026-10-12 startup log differs
by exactly that one line, gone.

### Pyrelands
- Site: `northstar_site.py --site 1 --fingerprint a32c5db7c6f1 --tag anima0` rc 0 -> **tile 5**, map 1, save
  NS_Pyrelands_site_1_a32c5db7c6f1_anima0 (pyre_site.log).
- **Tick rate** (tick_rate.json): stepped 58.1 t/s, Ultrafast 451.2 t/s, burst (gss_ticks) 467.8 t/s. Burst ~= Ultrafast, so the
  proposed `jawa/tick_burst` buys nothing; not worth building.
- **Main run** (`--skip-chains embergrass_regrow`, 26 min, Pyrelands_main_20261012b.json, pyre_main.log): component rows
  **PASS 20 / FAIL 2 / UNMEASURED 5** (+ regrow skipped); driver bars PASS 12 / FAIL 0 / UNMEASURED 1, NOT GREEN.
  - PASS now: ruins_scorched, scorch_fruit_seed, scorchfruit_fire_born, scorchfruit_produces, furnacebeast_heats_room,
    animal_distribution_correct, ullai_wired, giant_furnace_beast, burrowers_dive, firehawk, ashfall/cinderfall/blackrain rows.
  - FAIL plant_distribution_correct: gen census perDef **EmberGrass 32251, Quickgrass 21056, Plant_TreeAnima 0** (fresh site,
    block works), but the row fails its own sanity probe: **`jawa/set_plants Plant_Grass` is REJECTED on Pyrelands ground**
    ("terrain or conditions cannot support Plant_Grass", probe pyre_probe.json at (225,225) and (200,200)), so the census never had
    a foreign plant to see. HARNESS: the probe must plant something placeable, or check the set_plants reply.
  - FAIL ground_ash_ladder: map_fire refused 400/400 in 50,180,20,20 mid-run. The diagnostic text (planting reply + rect census)
    was **cut at 300 chars** by the driver's stderr line (cli.py:334 / bars.py:141) and the result JSON keeps no detail, so it is
    lost. Post-run probe on the same map: soil + EmberGrass planted 398/400, map_fire started **400/400**. Unexplained (HARNESS).
  - UNMEASURED: burn_line_present (fixture holds it off), scorchfruit_spoils_fast (sealed doorless room, stack STILL gone by
    day 2.5, whole-map 0), furnacebeast_warmth (no tool), fulgurite_after_lightning (sand fraction 0.0081: expected 0.02 < bar),
    herd_follows_two_day_old_burn (no drive).
- Regrow run: (pending)

### FlowWorks
(pending)

### GimmeSomeSlack
(pending)

## Ledger
- SCORCH_FRUIT_FIX_ROLLS_BEFORE_THE_ASHES A2 verify pass (closed). PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE A2 verify pass (closed).
- ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR: note (Pyrelands fresh census 0; storyteller half still UNMEASURED, so A1 stays partial).
- FACE_PATCH_FIX_ADDS_TO_A_GHOST: note (live PASS).

## New findings
(pending)

## State left
(pending)
