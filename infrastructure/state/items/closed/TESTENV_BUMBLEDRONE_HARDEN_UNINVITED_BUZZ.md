# TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ

Filed by BENCH 2026-10-15 (live round 7, ratchet_pilot tier, HEAD 0207ac8fc2). Evidence:
`Transient/bench_live_20261015_r7/live/river/ext_swept_site1_1.log` and `.json`.

What happened:
- FlowWorks `extension_proof --live --site river --chains swept` ran on a `river_site.py` map (tile 60145, on the Pyrelands
  fixture's world).
- The watched wait stopped after 60 of 250 ticks with `GOVERNOR_STOP hostile_arrival: arrived: AA_Bumbledrone AA_Bumbledrone
  (animal)` (vitals seq 107).
- `returns_home` read UNMEASURED "surprise". There was no damage. The row was not counted.

Class: SITE (a threat). A hostile-classified wild animal (Alpha Animals' Bumbledrone) arrived on the map in the middle of a row.
Where it came from is UNPROVEN:
- It may have been a wander-in or a manhunter incident. `river_site.py` does not apply the shared quiet-site profile
  (`quiet_site.site_profile_receipt`: storyteller off, incident queue drained), the way GSS proof_all's P3 does.
- It may have been a map-gen animal that walked in from the edge.

## guard (to build)

- `river_site.py` applies the quiet-site profile and reads its receipt back. It sweeps non-colonists once more right before
  the extension chains run.
- Before guarding, read the `pawn_origin` row of the next such arrival (same session, before any save/load). That separates
  "incident" from "already on the map".

## verify

Run `river_site.py` then `extension_proof --live --site river` (all chains) twice. Expect no hostile_arrival stop and a quiet
receipt in the site log.

## cause, from the evidence (BENCH 2026-10-15, offline)

**Not the test map.** The GOVERNOR_STOP triggers carry `"map": 3`. In `JawaBenchVitals.cs` that is `Map.uniqueID`, and
vitals samples EVERY map in Find.Maps. The test map was uid 9 (river_site `set_current_map(9)`).
- uid 3 was a rejected river_site candidate: the fixture home is uid 1 and the 9 candidates `river_site.log` tried are uids 2..10 (the site, 8th, is uid 9), so uid 3 is the 2nd, tile 13722 (rejected: fast=0). river_site left it loaded because it dropped
  only scenery rejects (TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA).
- Nothing swept or quieted those maps. The chain Watch's `prepare_bland_map` (storyteller off, wild spawner, kill
  hostiles and wildlife) acts on the current map.
- The swarm (AA_BumbledroneQueen + 6 AA_Bumbledrone) had fresh ids 140275+ at one tick, so it was generated then, not
  map-gen. What generated it on that map is UNPROVEN: the storyteller was off.

## guard built (convention read: prep_site.py and Pyrelands northstar_site.py apply `quiet_site.site_profile_receipt(...,
## controls=MAP_ONLY)` at site build; GSS proof_all applies the full profile; every chain's Watch applies quiet_world)

- river_site removes every rejected candidate map it generated. After choosing the site it lists the loaded maps (the
  `set_current_map` refusal's loadedMaps) and removes any leftover candidate. Then it reads them back again: a candidate
  still loaded is a site problem (exit 3). Maps loaded before the run are not touched.
- The site then gets the shared map-only quiet-site profile, read back (an UNCLEAN receipt is exit 3). The site map is
  made current again and read back by tile.
- Offline checks that can go red (`selftest_river_site`):
  - `leftover_maps`.
  - main() on a fake world: only home + site stay loaded, and the site gets MAP_ONLY.
  - A world whose candidate map will not go exits 3.
  - Mutation (no drops): 3 checks red.

## live proof (next round)

```
timeout 900 python.exe src/RimMandrake/FlowWorks/northstar/river_site.py 2>&1 | tr -d '\r' | tee "D:\Luke\dev\_rmscratch\<round>\river_site.log"
timeout 3600 python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river --out "D:\Luke\dev\_rmscratch\<round>\ext_river_<n>.json" 2>&1 | tr -d '\r' | tee "D:\Luke\dev\_rmscratch\<round>\ext_river_<n>.log"
```
Run the extension_proof twice.
- Bar: `loaded maps:` lists only the home map(s) and the site, and the quiet receipt shows no error.
- No `hostile_arrival` stop on any map. If one comes, read `jawa/pawn_origin` for its ids before any save/load.

## live proof r8 (BENCH 2026-10-15, HEAD 22b596181b): PARTIAL, kept open

`Transient/bench_live_20261015_r8/SITTING.md` §3-4, `live/river/river_site_{1,2,3}.log`, `ext_river_{1,2}.json`,
`live/probes/setmap_probe*.txt`, `live/river/vitals_river.json`.
- extension_proof --site river x2 on a fresh river_site (tile 1474): 15 PASS / 6 UNMEASURED / 0 FAIL both, no GOVERNOR_STOP, 0
  hostile triggers on any map all session. Quiet receipt clean (error None). Loaded maps, read independently: home + site only, on
  all three river_site runs. The threat half is met.
- **HARNESS, traced:** `river_site.loaded_maps()` reads `r.get("loadedMaps")`, but `jawa/set_current_map`'s refusal returns it under
  `details`: `{"success": false, "message": "No loaded map has uniqueID -1.", "details": {"loadedMaps": [...]}}`. So it always
  returns None. Every run prints `site problems ['loaded maps unreadable after the site was chosen']` and no `loaded maps:` line, and
  the leftover-candidate drop pass is skipped. The per-reject drops in the loop did the removal. `selftest_river_site`'s fake
  world (L138) puts `loadedMaps` at top level, so the offline check cannot go red on this.
- NEXT: read `(r.get("details") or {}).get("loadedMaps")` (keep top-level as fallback). Make the fake refusal nest it the way the
  tool does. Then re-run river_site once live and expect a `loaded maps:` line with home + site and no site problem.
- Also seen (SITE, not this item): `works/ferry_rope` UNMEASURED "could not find two banks across the current" on the wide
  (size 2.50) river; the rest of `works` is skipped after it.
