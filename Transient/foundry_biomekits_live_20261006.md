# FOUNDRY biome-kits LIVE run — 2026-10-06

Item: `BIOME_KITS_PUSH_TO_TEST_1`. Bridge taken by FOUNDRY 04:5x PDT ("biome kits live run").
Follows `Transient/foundry_biomekits_overnight_20261006.md` (offline pass).

## setup
- game killed; `deploy_custom_mods.py --compose biomes --apply --prune` = 165 files, VERIFIED in sync (EH, TheForge,
  TerminalBiomes, LanternDeeps, GelatinousSlime DLLs updated; stale RM_BankWorks.xml (moved to FlowWorks) + 2 RotSpore pngs pruned)
- `modset_builder.py --tier builds_biomes --apply` (14 mods); Steam relaunch; bridge up 04:47 (~31 s load)
- load log: only expected minimal-tier cross-ref misses (campaign kinds/terrains absent from tier)
- runner: `python.exe src/RimMandrake/Utils/modcheck/live_queue/situational_rerun.py --mods <M> --bland-world`
  output `Transient/belt_rerun_kits_<M>_20261006.txt`

## per-kit live results
| kit | result | notes |
|---|---|---|
| TheForge | run1 84 PASS / 1 FAIL / 10 UNM | gas_wash_ignites FAIL (mod: random-cell origin missed sparse fuel) -> 9 cycle comps UNM upstream; voices chain aborted by own Rain scald (harness). Both fixed cc741b6e4; rerun owed after redeploy |
| Miasma | 30 PASS / 0 FAIL / 7 UNM | UNM are the script's own named live-Miasma-map placeholders; 2 post-component surprises (spawned corpse-human death, a muffalo) touched no verdict |
| Scarlands | 24 PASS / 1 FAIL / 18 UNM | loosened_panel FAIL = proof never callable (static_call splits '\|' into params): fixed 814597021, rerun after redeploy; UNM = script's named live-Warscar placeholders |
| TheSump | 29 PASS / 0 FAIL / 11 UNM | clean; UNM = generated-Sump-map placeholders. 10-03 deploy-drift notFound gone |
| FeverWood | PARTIAL (killed mid-suite at handoff) | lure_raid a_staked_lure_draws_the_swarm UNM: the awaited Kurreth swarm read as hostile_pawns SURPRISE -> declared in script (this commit, takes effect next run). Other FW surprises to triage: tentacle_ladder hostile, tentacle_lash dmg, tank wildlife, flora_harvest injured (Transient/modcheck/surprises/ newest dir) |
| Greentide | NOT RUN (batch2 killed at handoff) | |
| RustCathedral | NOT RUN (batch2 killed at handoff) | |
| TerminalBiomes (Scald) | NOT RUN (batch2 killed at handoff) | |
| CreatureBehaviors | NOT RUN (batch2 killed at handoff) | |

## fixes
- 1a82be722 modcheck/status.py: python.exe recording over 9p (mkdir mutex) -- every run since 10-02 printed RECORDING FAILED
- 814597021 Scarlands: RM_LoosenedPanelProof.ProofWork(map, sev) two params; script fails loudly on a refused static_call
- cc741b6e4 TheForge: gas-wash origin = unroofed flammable plant, origin always ignites (C#, DLL rebuilt); voices chain wraps hazard damage off

## handoff state (owner said "handoff now")
- batch2 job had already DIED mid-FeverWood: the bridge socket dropped (`'NoneType' object has no attribute 'sendall'` on every later call; every suite crashed out); afterwards ./game read RUNNING with no bridge port in Player.log (game relaunched/reloading by someone else?). Bridge RELEASED. Greentide, RustCathedral, TerminalBiomes, CreatureBehaviors NOT run. NEXT: rerun `--mods FeverWood,Greentide,RustCathedral,TerminalBiomes,CreatureBehaviors --bland-world --retile` after the redeploy below.
- modcheck_status.json: Miasma/Scarlands/TheSump/TheForge records committed LF-normalized (CRLF writer fixed 7c9a20104).
- NEXT: kill game, `deploy_custom_mods.py --compose biomes --apply` (new TheForge + Warscar DLLs) + `--mod FlowWorks --apply` (RM_LiquidKits.xml drift), relaunch, rerun TheForge,Scarlands,FeverWood to confirm cc741b6e4 / 814597021 / lure declare.

## blockers / owner
- modcheck_status.json recording fails from python.exe: PermissionError (pre-existing, every run) -> suite status NOT updated by runs
