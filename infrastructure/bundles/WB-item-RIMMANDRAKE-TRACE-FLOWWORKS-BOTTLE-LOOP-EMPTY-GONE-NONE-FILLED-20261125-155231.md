# Work bundle WB-item-RIMMANDRAKE-TRACE-FLOWWORKS-BOTTLE-LOOP-EMPTY-GONE-NONE-FILLED-20261125-155231

System: FlowWorks northstar chain `toggle_bottle_loop` (src/RimMandrake/FlowWorks/northstar/extensions.py).

## Members

| member | class | outcome | commit | live reading |
|---|---|---|---|---|
| RIMMANDRAKE_TRACE_FLOWWORKS_BOTTLE_LOOP_EMPTY_GONE_NONE_FILLED | REAL (check wrong: plot-only census; mod fault not yet excluded) | check was wrong; fixed and proven live | 35eb8208a17d (census), e9ff5a54c340 + this publish (accept_live.py, bool-result crash fixed) | ArchBig 2026-11-25 08:17 PST, flowworks_list exact (20 mods): bottle_loop_on PASS, bottle_loop_off PASS; census saw the empty held mid RM_FillBottleJob, then 1 FreshWater (live_20261125T161718Z.json) |

## What the next context needs

- Step 2 red run: done by the earlier detached run (accept_live.py red on the 11-24 run and on a planted map-wide FAIL,
  green on a planted PASS). Item test `list_shape.py holds` reads FAILS on live_bottle_loop_passes only.
- Live command: `python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --chains toggle_bottle_loop`
  on a free game, through `work_bundle.py live`; copy FlowWorks_<stamp>.json to
  design/specs/2026-11-25-bottle-loop-map-wide/live_<stamp>.json and commit; accept_live.py must read MET.
- If bottle_loop_on FAILs: suspect JobDriver_FillBottle / TryDebitTerrain refusing the painted pond (empty left in hand).

## Next, in order

1. Done: step 4 fresh reader (rm-consult, NOTHING SIGNIFICANT; 3 polish lines on design/concepts/FlowWorks/version/polish.md).
2. Done: step 5 live pass on ArchBig (design/specs/2026-11-25-bottle-loop-map-wide/live_sitting.sh).
3. Step 6: close with the sha and the live reading.

## Context size after each group

- after the one group (live pass and close): about 140k of 1M (work_bundle.py context read GO ON at 101808 before the live pass)
