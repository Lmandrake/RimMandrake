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
_pending_

## 3. S1..S6 rerun at shipped settings
_pending_

### Pond fill grids S2/S5/S6
_pending_

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
_pending_

## 5. Bridge permission file
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\companion_profile.json`:
expiresUtc changed 2026-10-17T20:30:00Z -> 2026-10-18T02:00:00Z at 17:58Z. Nothing else in the file was touched.

## 6. Left over
_pending_
