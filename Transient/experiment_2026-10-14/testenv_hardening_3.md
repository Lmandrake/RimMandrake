# Testenv hardening 3 — 2026-10-15 (BENCH, offline)

This follows `testenv_hardening_2.md`. The live evidence is `Transient/bench_live_20261015_r7/SITTING.md` and
`live/{probes,river}/`. Each item file in `infrastructure/state/items/<ID>.md` has the full write-up and the exact live
proof command. No row's measurement was changed. Nothing was deployed and the bridge was not used.

## 1. TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG

**Cause.** The calm's whole-map unfog (`clear_map_fog`) brings hostiles onto the map that its own pre-unfog hostile
check could not list. On calm_probe_2 that was 4 fleshbeasts at the same tick. The check runs before the unfog, so P2c's
advance stopped at arm.

**Guard.** After the unfog, `clear_map_fog` reads hostiles back and runs `destroy_bulk nonColonists` again until the
listing is empty, at most 3 times. It records `releasedByUnfog`, `sweepPasses` and `hostilesAfter`. A map that keeps
releasing is a SITE fault: P2c and P3 FAIL and nothing ticks.

**Offline checks.**
- `selftest_testenv_guards` `test_map_fog`: the unfog alone leaves the beasts (can-fail). The mutant without the re-sweep
  went red on 2 checks.
- `selftest_proof_all` 5e (4 checks).

**Spawner.**
- *Generator, presumed (strong association):* vanilla `SymbolResolver_Interior_AncientTemple`, an ancient shrine.
  - Its threat branch is 50% 2-5 fleshbeasts with `LordJob_FleshbeastAssault` (Anomaly), else 65% a 1-5 mech group,
    else hives. That matches every class seen in r6/r7.
  - Probe 2's only triggers were that shrine's `RectTrigger` + `SignalAction_Letter` warning pair.
- *UNPROVEN:* why those pawns are absent from `AllPawnsSpawned` until the unfog. `SymbolResolver_SinglePawn` spawns them
  at mapgen.
- *RULED OUT:*
  - vanilla `Unfog` / `Notify_Unfogged` / `CellFogChanged` (rimsage 1.6);
  - our src;
  - the tier's VEF, KCSG and Alpha DLLs, searched UTF-8 and UTF-16;
  - the def-dump comps.

## 2. TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA

**Cause.**
- (a) The site test asked only for a current and a fast lane. A river that ends in the sea reaches one map edge, its
  inflow, so the swept row could carry nobody off.
- (b) `set_current_map(mapId=g["mapIndex"])` passed a Find.Maps position where Map.uniqueID is wanted, so every
  candidate was read on the previous map.
- Separately, only scenery rejects dropped their map.

**Guard.**
- `extensions_rivers.moving_edges` and `river_site.river_reject` need 2 or more moving edges. Unreadable edges reject.
- The map tile is read back.
- `generated_map_id` uses `mapId` only.
- Every rejected candidate map is removed.
- `swept` is UNMEASURED SITE "no downstream edge" up front, with no staging and no 1500-tick wait.

**Offline checks.**
- `selftest_river_site` runs pure cases plus `main()` against a fake world whose map uids are not their indexes.
  Mutants went red: mapIndex 7 checks, no edge rule 6, no drops 3.
- `selftest_extensions` checks swept on the sea shape. The mutant read PASS with 3 staged.

## 3. TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ

**Cause.** The swarm landed on map **uid 3**, not the test map (uid 9). The vitals trigger's `map` field is
Map.uniqueID, and vitals watches every map. uid 3 is the candidate river_site left loaded for tile 13722 (rejected,
fast=0), on which nothing was swept or quieted. What generated a fresh swarm there with the storyteller off is UNPROVEN.

**Convention read.**
- prep_site.py and Pyrelands northstar_site.py apply `quiet_site.site_profile_receipt(controls=MAP_ONLY)` at site build.
- GSS applies the full profile.
- Each chain's Watch applies `quiet_world` (storyteller and wild spawner) to the current map.

**Guard.**
- river_site removes every candidate map it made. It lists the loaded maps after choosing the site, removes leftovers and
  reads them back (a leftover is exit 3).
- It applies the MAP_ONLY quiet profile to the site and fails on an UNCLEAN receipt.
- It makes the site current again and reads it back by tile.

**Offline checks.** `selftest_river_site`: `leftover_maps`, main() on a fake world (only home + site stay, MAP_ONLY
applied), and a candidate map that will not go exits 3.

## Offline checks, review, commits

- `run_selftests --only` on 10 tests is GREEN 10/10: testenv_guards, quiet_site, clockgate, bland_world, proof_all,
  river_site, extensions, flowworks_northstar, proof_hose and pyrelands_site.
- All 8 changed files had a full-file review and are marked CLEAN: testenv_guards and its selftest, proof_all and its
  selftest, river_site and its selftest, extensions_rivers, and selftest_extensions.
- The changed FlowWorks and GSS files live under `northstar/`, outside mod_hash, so no recorded proof goes stale.
- Shas are in the commit log and the ledger notes.
