# Release proximity, 2026-10-22 (FOUNDRY, read-only ranking)

Owner order 2026-10-22: *"Focus on work for the mods closest to release."* This ranks OUR mods (RM_/RSW_/RUT_), not the donor SHIP list.

## What was measured, and what was not

- **The "SHIP list"** (`infrastructure/state/modlists/ModsConfig.SHIP.RULED_2026-10-20.xml`, edited in `1f6930706`) is a list of DONOR mods that stay in the shipped set. It says nothing about readiness of our own mods, so it is not the ranking key.
- **Ranking key** = the SHIPPED-rung acceptance in the `*_SHIP_*` items (code review CLEAN, settings audit, art complete, deploy in sync, modcheck GREEN) plus `modcheck status`.
- DIRTY counts: `code_review_status.py check` over `git ls-files` of each mod's `.cs/.xml/.py` (2026-10-22). Other file kinds (json, png) not counted.
- `modcheck floor --all` did NOT finish inside 100 s (timeout rc=124), so the floor measure is **UNMEASURED**. `modcheck status` was used instead (stored/GREEN-RED state per mod).
- `required_checks.py` not run (hung once under a helper per the 2026-10-22 handoff). Deploy-sync not re-measured (needs a dry run on the Windows side).
- Only 1 mod of ~70 in `modcheck status` is GREEN at its current hash (IshkoDarkLandmarks). Nothing is SHIPPED yet by the ledger's own definition.

## Ranked table

| # | Mod (tier) | Done | Remains: OFFLINE | Remains: NEEDS-LIVE | Remains: NEEDS-OWNER | Items |
|---|---|---|---|---|---|---|
| 1 | GimmeSomeSlack (RM) | 0 of 106 files DIRTY; checklist VALIDATED; last run PASS 113 / FAIL 1 / UNMEASURED 5 (`gss_proof_all_1.json`) | Re-read the one FAIL `S12a_D1_legacy_run_one_look`; deploy dry run (DLL rebuilt 2026-10-22 and undeployed) | Re-run proof at the CURRENT hash (stored run is at a STALE hash; modcheck RED); 5 UNMEASURED rows (B12, B13, A8, S12c, S12d); `CORD_GRAPH_TOPOLOGY_REVISION_1` (built) proof | `PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES` decision of which master switch owns pipe poles | `CORD_GRAPH_TOPOLOGY_REVISION_1`, `PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES`, `GRAVSHIP_WIRES_SURVIVE_LAUNCH_1`, `FALLEN_WIRE_SHOCK_1`, `NORTHSTAR_PROCESS_RETRO_1` |
| 2 | IshkoDarkLandmarks (RUT) | modcheck GREEN at current hash (PASS 8); 1 of 4 files DIRTY | Review the 1 DIRTY file; add checklist (status says "no checklist") | none known | Whether a landmarks art mod counts as a release unit | `NORTHSTAR_ISHKO_PILOT_1` (pilot only; no SHIP item exists) |
| 3 | Pyrelands (RM, ships inside composed `mandrake.rm.biomes`) | All `PYRELANDS_SHIP_READINESS_1` boxes ticked except FireHawk line, and `FIREHAWK_FLIGHT_BEHAVIOR_1` is now `done` in the ledger (box is probably stale); art, settings audit and composed deploy (3374 files in sync on 2026-10-11) done; checklist VALIDATED (20 lines); 4 of 86 DIRTY | Review the 4 DIRTY (`Pyrelands.xml` changed since mark, `RM_RetiredMutatorPorts_Pyrelands.xml`, `RM_StruckGlassRing.xml`, `struck_glass_live.py`); tick the FireHawk box if the ledger closure covers it; re-deploy composite after Wave-1 migration | `PYRELANDS_GREEN_MINIMAL_1`, `PYRELANDS_GREEN_FULL_1` (both built; modcheck RED "last run failed") | Wave-4 / paint-once is expected zero-tile (not a gap) | `PYRELANDS_SHIP_READINESS_1`, `PYRELANDS_NORTHSTAR_TRIAL_1`, `PYRELANDS_GREEN_MINIMAL_1`, `PYRELANDS_GREEN_FULL_1`, `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` |
| 4 | Graffiti (RM) | 7 of 36 DIRTY; `GRAFFITI_NORTHSTAR_SHIP_1` gate list written; GREEN-minimal built | Review 7 DIRTY (`RM_GraffitiKernel.cs`, `MapComponent_GraffitiOrders.cs`, `GraffitiFuzz.cs`, `SelfTest/Program.cs`, `northstar_plan.py`, `northstar_site.py`, `sigil_coverage.py`); `dll_source_stamp.py check`; deploy dry run; settings re-measure of `viewerReactionEnabled` | `GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1` run; `GRAFFITI_NORTHSTAR_GREEN_FULL_1` (needs full-list driver mode) | Re-validation of hashed prose (plan 5.7) on his word; `GRAFFITI_DESIGNATOR_MARK_CHOICE_1` / `GRAFFITI_SIGIL_FRAMES_ART_1` scope for v1 | `GRAFFITI_NORTHSTAR_SHIP_1`, `GRAFFITI_NORTHSTAR_TRIAL_1`, `GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1`, `GRAFFITI_NORTHSTAR_GREEN_FULL_1` |
| 5 | FlowWorks (RM) | Owner's current focus; large validated suite (PASS 61 on `v2_run1.json`); settings grouped, all-off chain added | 158 of 689 DIRTY (to re-verify; the 2026-10-22 review loop was still running); 12 screens lack Reset (`FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING`); 97 of 100 def texture refs borrow vanilla/foreign art (2026-10-05 audit; may have moved); three filed C# fixes (`FLOWWORKS_RIVERCOLOR_FIX_DICT_SELF_ENUM`, `_CONVERTER_FIX_BLOCKED_STARVES_REST`, `_REACTOR_FIX_STUCK_ENDS_SHIFT`) | modcheck REFUSED (step 4 extension_proof UNMEASURED); `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1`, `_GREEN_FULL_1`; `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` in flight; `PIT_SUPERDEEP_COLLAPSE_1` doing | `RM_Ladder` art pick; reset-screen item is marked needs-owner | `FLOWWORKS_NORTHSTAR_SHIP_1`, `FLOWWORKS_NORTHSTAR_TRIAL_1`, `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1`, `FLOWWORKS_NORTHSTAR_GREEN_FULL_1`, `FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING` |

Next tier, not ranked in detail: ExplosiveGrowth (7 of 31 DIRTY, PASS 54 / UNMEASURED 5, no checklist), Cauldron (25 of 65 DIRTY, PASS 4 / UNMEASURED 88), LeaningScrub (30 of 95 DIRTY, PASS 77 / UNMEASURED 8), Contagion (25 of 97 DIRTY, FAIL 1), GravshipLanding (6 of 9 DIRTY, DRAFT-CHECKLIST), TheForge (52 of 63 DIRTY), Abyss (72 of 74 DIRTY).

## Concrete next OFFLINE actions, top 5

1. **GimmeSomeSlack**: read `Transient/bench_live_20261015_l2/live/gss_proof_all_1.json` row `S12a_D1_legacy_run_one_look` and decide code-bug vs site-bug; run `deploy_custom_mods.py --mod GimmeSomeSlack` dry run and list the diff; write the pre-registered Player.log strings for the 5 UNMEASURED rows so the next bridge sitting is one load.
2. **IshkoDarkLandmarks**: `code_review_status.py check` the 4 tracked files, review the one DIRTY file, `mark-clean` only on a clean full-file read; then ask the owner whether it is a release unit.
3. **Pyrelands**: full-file review of the 4 DIRTY files; confirm `FIREHAWK_FLIGHT_BEHAVIOR_1` closure satisfies the last box of `PYRELANDS_SHIP_READINESS_1` (read its closing note) and tick it; run `deploy_custom_mods.py --compose biomes` dry run after the Wave-1 migration to confirm sync.
4. **Graffiti**: review the 7 DIRTY files (SelfTest and python helpers first, they are cheap); run `dll_source_stamp.py check`; deploy dry run; re-measure the consumer of `viewerReactionEnabled` with a grep of `Source/` and label or delete the setting.
5. **FlowWorks**: re-measure the 158 DIRTY (list to a file, split by kind); build the shared Reset helper for the 12 screens (`FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING`); fix the three filed C# bugs with offline kernel tests (run SelfTest from `bin/Release/net8.0`, not the staged folder).

## Flagged uncertainty

- "Closest to release" has no single instrument. The ranking is a judgement from DIRTY counts, modcheck state and open SHIP acceptance; ranks 1-3 are close and could reorder.
- The owner's standing 2026-10-11 priority (GimmeSomeSlack and FlowWorks above all else) is why FlowWorks is listed at all; by gate distance it is the FARTHEST of the five.
- Every top-5 mod shows modcheck RED or STALE: the stored runs are at old hashes, so none can be called GREEN until a live run at the current hash.
- DIRTY counts for FlowWorks may already be falling (review loop active 2026-10-22); re-measure before acting.
- `modcheck floor --all` UNMEASURED (timeout). The `FLOWWORKS_NORTHSTAR_SHIP_1` item prose predates tonight's review wave.
- Tier of Ishko is RUT (path `src/RimUtinni/`); tier of the others from `About.xml` packageId (`mandrake.rm.*`).
