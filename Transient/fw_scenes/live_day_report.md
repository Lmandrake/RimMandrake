# FlowWorks live day report — 2026-10-17 (FOUNDRY live-driver helper)

## 1. Deploy of fe309aefe (level-water fix)
DONE 17:57Z. Live list was already the 11-mod flowworks list (modlist_swap --status: UNRECOGNISED, 11 active;
harmony, core + 5 DLC, rimbridgeserver, simplecamerasetting, gimmesomeslack, flowworks), so no swap was needed.
Game closed (Stop-Process), `deploy_custom_mods.py --mod FlowWorks --apply` (65 files, VERIFIED in sync; the
deployed copy was also behind on 56 weir/bank textures and defs, all committed), relaunched via `steam.exe -applaunch 294100`.
Deployed DLL sha256 ee95273... = repo DLL = the `# dll:` header of the committed `.srchash`; deployed `.srchash`
byte-identical to the repo's; RM_FlowKernel.cs hash in the srchash (080c9580...) = the committed file. Previously
deployed DLL was 82f3943b... (stale).

## 2. water_scenes_walk.py crash fix
Cause FOUND: the lost S4.c/S5 tracebacks were `clockgate.GovernorStop` "starving: food category Starving"
(`D:\Luke\dev\_rmscratch\governor_stops.jsonl`, 16:28:16Z go S4 and 16:28:22Z go S5): the quicktest colonists starved
over the long sitting and the vitals latch stopped `safe_advance`; nothing caught it. Fix (7177eb957, 404760df7):
colonists fed (Food, Rest) at prep and every 5,000 ticks; a GovernorStop is printed and the rest of the step resumed
once; every scene runs inside a handler that prints the full traceback, keeps it at
`Transient/fw_scenes/live/<scene>_traceback_<stamp>.txt`, writes a CRASHED row and carries on; ProofFluidRow failures
print and retry instead of returning None; `--fresh-map` per scene, `--no-wait`; offline `--mock`
(`water_scenes_mock.py`) and `--mock-fail <scene>`. L1 evidence: `Transient/fw_scenes/mock/mock_fail_S4_stdout.txt`.
Live, the latch fired twice more (a dormant hive "threat_structure" at arm, S2 and S3): printed and resumed, no loss.
rimflow verify: WATER_SCENES_WALK_MEND_TRIPS_AFTER_S4 pass L1.

## 3. S1..S6 rerun at shipped settings
fe309aefe DLL, 11-mod list, one fresh quicktest map per scene, pulse 250 ticks, shipped settings except the scene file's
own exceptions (rain fill off, refill off, weather clear). Logs: `Transient/fw_scenes/live/run_S<n>_stdout.txt`; rows
`S<n>_rows.json`; annotated `Transient/fw_scenes/live/annotated/index.html` (S5 still captioned "under redesign").

| scene | result |
|---|---|
| S1 | a MATCHES (all 8 by pulse 8), b, c, d MATCHES |
| S2 | lvl (plan P1 bar) MATCHES, a (p14), b (p13), c, d MATCHES |
| S3 | a MATCHES, b MATCHES (p8), **c DIFFERS** (p9+: lost 6.97, gained 6.00; see below), d MATCHES, e UNMEASURED (not staged), Q1 open |
| S4 | a, b, e, c, d MATCHES; Q1 game today = (a) stays put |
| S5 | a, b, c, d, h, e, f, g MATCHES; **i DIFFERS** (pump G: pond 4 -> 0, canal ends [2,3,4] = 3, hoses 0; 1 level lost at pulse 6 when the hose drained: same shape as S3; canal cell 1, the Outflow end, never wets) |
| S6 | a, b, c MATCHES; Q1: identical pulse by pulse as well |

rimflow verify: WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX partial L2 (S2 level, S6, S5 to the end all met; modcheck
record NOT run: the walk's result has no mod_hash / env fingerprint, so `modcheck record` would refuse it).

### Pond fill grids S2/S5/S6
S2 (dug 2x2 pond, depth 4; west column touches the lake; `[SW SE NW NE]`): p1 [1 0 1 0], p2 [1 1 1 1], p3 [1 2 1 2],
p4 [2 2 2 2] ... p7 [3 4 3 4], p8-p13 [4 4 3 4] (trench filling), p14 on [4 4 4 4]. **Never more than one level
between touching squares: the [4 0 4 0] of the morning is gone.** The pond still rises in alternating half-steps,
not as one surface (expected until P3).
S5 part A and S6 (3x3 WaterDeep pond, 36 levels): per-square `depth/fill` reads 0/4 in all 9 squares at every pulse,
because the excavation grid does not carry a terrain pond's stock; the body reads 36 -> 35. The one lost level shows
as ONE square: the NE corner's terrain turns WaterDeep -> RM_WaterChestDeepStill at pulse 2 and stays; the other 8 stay
WaterDeep. So "0/4/0" on a terrain pond: the drawdown is drawn whole-notch on one square, not spread (P3's job).
S5 B/F/G single-square ponds: B 4 -> 3 (canal cell 1 = 1), F 4 -> 2 with the 2 m canal square at 2, G 4 -> 0.

### S3 mass difference
MEASURED live 18:10Z (`Transient/fw_scenes/live/run_S3_stdout.txt`, ledger line per pulse). Step B: the pump moved
7 levels (`pump.moved` 0 -> 7, 10,000 units each). Pulses 2-8: hoses hold 1.00 level and pond loss = canal + hoses
exactly (no S3.c miss at p0-p8). Pulse 8 the canal is full (6 x 1). Pulse 9-10 the stopped hose drains its 1.00 level
(`net.hoseDrainedUnits` +10,000): **9,748 units SPILLED as filth** (`net.spilledUnits` +9,748, RM_LiquidSpill: the
canal outlet takes whole levels only and it is full) and 252 units went back into the pond (stock 41.0 -> 41.0252).
So 6.9748 lost = 6 canal + 0.9748 spilled to filth. **Not an unaccounted leak and not a pump buffer: the hose-drain
rule (rev 2 §3.7, L8) turns the last hose-full into a filth puddle.** It IS a break of the scene's conservation law
(S3.c names only canal + hoses), a sink the scene doc does not list: a ruling item, not a code bug found here.
Earlier S3 "pulse None" runs: the intake hose was never laid ("no room for the straight lead-out from the nozzle" on
the pond's middle edge square; one square south lays at once). Fixed in the harness by trying the pond's other edge
squares (`intake_alt`).

## 4. PIT_CLIMB live proof
**climb_proof.py, live, fresh map, 11-mod list** (`Transient/fw_scenes/live/climb_stdout_20261017.txt`,
`climb_result_20261017.json`): 12 PASS, 0 FAIL, 3 OWED UNMEASURED. PASS: pond_person_free, pond_person_walks_out,
D3_person_trapped, D3_person_cannot_walk_out, D3_muffalo_free, D2_rat_trapped, ladder_prison_door,
mask_seals_cliff_edge, ramp_walk_out, ramp_frees_and_retraps, step_cost_slow_at_K, rebuild_follows_fill.
OWED: raider_never_crosses_ramped_moat, hauler_fetches_ramped_floor, save_reload_pockets_identical.

**New: `src/RimMandrake/FlowWorks/northstar/raid_trench_proof.py`** (9x9 island with the colonists, ringed by a 2-wide
sheer 2 m trench; a churn cell dug/filled every other 250-tick chunk so the masks rebuild under live path requests).
- RAID_island_sealed PASS (person band, east lip bits 0xCB, derived=True). First read FAILED on an UNDERIVED mask
  (0xFF derived=False): masks derive lazily; the script now only counts a derived=True read (harness fix, not mod).
- Storyteller raid 1 (PirateWaster, AssaultColony, 500 pts, 15,000 ticks): never came within 33 squares; milling.
- Storyteller raid 2 (Neanderthal tribe, StageThenAttack, 30,000 ticks): staged 54+ squares out, never came near.
  A fleshbeast assault (Entities) on that map also put fleshbeasts INSIDE the ring and in the trench (with
  RM_PitExposure + bruises) and downed the colonists: emergence vs crossing not distinguished; uncontrolled, not judged.
- **`--direct` (6 PirateYttakin mercenaries 30 squares east into vanilla LordJob_AssaultColony, storyteller off):
  outcome LEFT + SHOT_ACROSS.** A gunner stood 18 squares out and shot across the trench; first colonist down on the
  island at t+2000 with the nearest hostile 18 away; all 3 colonists down by t+3250; no raider ever entered the trench
  or the island; all 6 left the map alive by t+8500 (canTimeoutOrFlee default). Evidence:
  `Transient/fw_scenes/live/raid_trench_direct_stdout_20261017.txt`, `raid_trench_direct_20261017.json`.
  So under today's rules a sheer trench stops walking raiders but not their guns; whether that is right is
  `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST` (his Q7). Melee raiders (2 slashers) milled 28-40 out and left with the rest.
- MASKSWAP_no_wall_crossing UNMEASURED in every run: no raider came within 15 squares, so the mask swap under
  multithreaded pathing was never exercised against a pawn at the wall. 80-120 mask rebuilds ran with no error.

Still missing for PIT_CLIMB (noted on the item): a mask-swap row that puts pawns AT the wall (e.g. colonists ordered
to path across the island edge while the churn runs, or melee raiders with no ranged option); the three OWED
climb rows; `modcheck record` (climb_proof's result has no mod_hash/env, like the walk).

## 5. Bridge permission file
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\companion_profile.json`:
expiresUtc changed 2026-10-17T20:30:00Z -> 2026-10-18T02:00:00Z at 17:58Z. Nothing else in the file was touched.

## 6. Left over
- S3.c / S5.i: the hose-drain spill to filth breaks the scenes' conservation law (owner ruling: is a filth puddle an
  allowed sink, or must a stopped hose drain back / hold?). Canal cell 1 (the Outflow end) wets last or never.
- Terrain ponds draw a lost level on ONE square (WaterDeep -> ChestDeep); per-square fill is not tracked: P3's job.
- modcheck record for the walk and climb results: their JSON lacks mod_hash/env.running; needs a wrapper.
- PIT_CLIMB: mask-swap row at the wall; three OWED climb rows.
- Bridge released 18:52Z. Game left running on the 11-mod list (quicktest map); storyteller re-enabled by the script.
