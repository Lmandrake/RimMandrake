# Broaden — GSS_WATER_STUB_FIX_PASSED_LAST_WEEK (2026-11-11 20:48 -08:00)

Second model: GPT via `src/RimMandrake/Utils/gpt_consult.py` (job consult-20261111-204851-2268463-dc770d).

## The question (verbatim)

> Context: RimWorld mod "Gimme Some Slack" (GSS) hides power conduits and draws slack extension cords between powered buildings and conduit ends. Waterproof conduit laid under deep water is "buried": the cords must end at the two banks ("water stubs") and not cross the water. Bug: with the FlowWorks mod co-loaded, its "deep swim" setting makes WaterDeep path-walkable, and GSS's cord adapter treated walkable as ground before water, so it drew one cord straight across the water (0 stubs). Fix (SnapshotBlock.Of): a cell whose terrain def is impassable water is Water regardless of path-grid walkability.
> 
> Statement to satisfy: on the fw_gss_sitting mod list (FlowWorks + GSS + Biomes + VEF + all DLC, deep swim on) the live matrix scene MX_F60_T15_S0 (battery -> conduit -> 2-cell-wide deep-water canal crossed by waterproof conduit -> consumer) reads stubs 2, cord_edges 2, node_types {battery 1, consumer 1, stub_water 2}, strands [2,2]; cause confirmed vs the 2026-10-23 FAIL on the same list; other matrix scenes do not regress.
> 
> What I tested: two full live runs of proof_all.py --only matrix on that exact 14-mod list (30 scenes + determinism + log budget, 36/36 PASS, offline gate 0 red), F60 row exact counts; tier measured from ModsConfig; deep swim read live = True; GSS DLL sha in repo/game/running assembly all equal and .srchash matches source; screenshot of the board shows cords stopping at both banks; same scene on 2026-10-23 same list read 1 cord across water, 0 stubs. Offline: C# SelfTest WaterStubChecks 772/772 incl. a can-fail old-rule case.
> 
> Question: what would a real player try that I haven't, that could still show the bug (or a sibling bug) in ordinary play? Think: a new player, an experienced player, someone trying to break it, a messy real map (rivers, marsh, moving water, shallow vs deep, ice/freezing, bridges, terrain changing under the conduit, save/load, toggling FlowWorks swim setting mid-game, swimming pawns standing on the conduit). Give the 5 most revealing concrete experiments, ranked, each with what a failure would look like. Be brief.

## The answer (verbatim)

> 1. **Change terrain beneath an existing, powered crossing.** Build/remove a bridge; let water freeze/thaw or flood/recede where supported. Check immediately and after reload, distinguishing an actual terrain-def change from a visual change. **Failure:** cords cross terrain that should remain buried, or water stubs persist after it becomes ground.
> 
> 2. **Toggle deep swim during play.** On the canal scene, switch it off/on with pawns swimming or standing over the conduit; repeat after a full restart if required for the setting to apply. **Failure:** bank endpoints change with walkability or pawn occupancy; the original 0-stub crossing returns.
> 
> 3. **Save/load the crossing at awkward stages.** Save before waterproof conduit finishes, just after completion, and after replacing a bank segment; reload each, including from a fresh game process. **Failure:** loading produces missing, duplicate, or misplaced stubs, or fixes a rendering error that existed before saving.
> 
> 4. **Cross a messy natural river.** Route through deep water, shallow water, marsh, and an island, using an oblique shoreline and any available moving-water terrain. Verify each terrain’s intended burial behavior. **Failure:** a cord skips an intervening bank, spans a buried section, or creates extra stubs inside one continuous buried stretch.
> 
> 5. **Rewire a busy shoreline network incrementally.** Add a second consumer and a waterproof branch along the river; demolish/rebuild bank junctions, disconnect/reconnect power, and finish blueprints in different orders. **Failure:** identical final layouts produce different cords, stale endpoints survive demolition, or one branch reconnects straight across water.

## What I tried and what I saw

First, a check of what a player can actually build: on the live game `jawa/build_check` refuses WaterproofConduit on
vanilla `WaterDeep` ("requires terrain that supports: Waterproof conduit"; WaterDeep's live affordances are `[]`). So the
matrix scene's canal (conduit spawned straight onto WaterDeep) can't be built that way by hand. In real play a buried
crossing comes from water arriving over conduit that is already laid, or from FlowWorks water that does allow
waterproof conduit. So I tried GPT's items 4 (messy real water) and 2 (deep swim toggled mid-game) on the water types
a player really meets. Each was a one-scene copy of the F60 canal with only the water terrain swapped
(`run_live.py --live --scenes full --only XW`, same calm site, same 14-mod list):

| scene | water | swim ON | swim OFF |
|---|---|---|---|
| XW4 | vanilla `WaterDeep` (Impassable) | **stubs 2, cord_edges 2** (PASS) | stubs 2, cord_edges 2 (PASS) |
| XW1 | FlowWorks `RM_Fill_Water_Superdeep` "deep water (2 m or more)", def Standable, WaterproofConduitable | stubs 0, 1 cord **on the water** | same |
| XW2 | FlowWorks `RM_Fill_Water_Brim` "chest-deep (about 1.5 m)", wadeable | stubs 0, 1 cord | same |
| XW3 | vanilla `WaterMovingChestDeep` (river), wadeable | stubs 0, 1 cord | same |

- **The item's scene holds both ways.** WaterDeep gives 2 stubs with deep swim on and off: the fix doesn't depend on
  the swim switch.
- **XW2 and XW3 are not defects.** GSS's rule has always been "a cord lies where a pawn can wade". Before FlowWorks was
  co-loaded, wadeable water drew a cord too.
- **XW1 is a sibling defect, and it isn't caused by the item.** A player can lay waterproof conduit across FlowWorks'
  2 m+ pit water, and GSS draws a cord floating on top of it, because that terrain is def-Standable. FlowWorks itself
  decides swim depth in `RM_Swim.IsDeepSwimIndex` (terrain, or the excavation component's dug depth), and GSS can't
  see that without a cross-mod contract, which is a design decision. I filed it as
  `RIMMANDRAKE_BURY_GSS_CORDS_IN_FW_SUPERDEEP_PIT_WATER` with the readings and the options rather than guess the
  contract. Screenshot: `evidence/sibling_XW1_fw_superdeep_cord_on_water.png` (the cord crosses the blue pit),
  beside `evidence/sibling_XW4_waterdeep_two_stubs.png`.
- **Caveat on the swim-OFF column:** I set `RM_SwimSettings.deepSwimEnabled=false` through
  `jawa/mod_settings_field` (static field). I did not re-read path-grid walkability afterwards, so I can't say whether
  FlowWorks re-closed the deep band on the live map. The column shows only that the cord result didn't change. I set
  the field back to True and read True.

Not tried: GPT's 1 (terrain changing under a powered crossing: bridge build/remove, freeze, flood), 3 (save/load at
awkward stages; proof_all's save block wasn't in this `--only matrix` run) and 5 (incremental rewiring of a busy
shoreline).
