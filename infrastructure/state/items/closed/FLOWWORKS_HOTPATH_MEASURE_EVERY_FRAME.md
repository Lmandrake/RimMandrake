# FLOWWORKS_HOTPATH_MEASURE_EVERY_FRAME

FlowWorks: hot-path perf (feed mesh per frame, World() rebuilds, bottle scans, link scans)

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C1-F6** PLAUSIBLE LOW — Hose-link signature scan copies + walks every reel each queried tick. RM_LiquidNet.cs:964 copies OrderedReels each new tick a query arrives; bath job fail path re-queries. Needs a perf read on a map with many hoses.
- **C2-F8** PLAUSIBLE MEDIUM — Bottle work givers repeat a radial liquid search + CanReach per candidate container. RM_LiquidBottleUtility.TryFindLiquidCell is called from HasJobOnThing for every container. Live: 100 empty bottles on a dry map, time one WorkGiver scan (Prof or stopwatch probe).
- **C7a-F6** PLAUSIBLE MEDIUM — A walking hose carrier rebuilds the whole-map World() snapshot each time its trail changes. DrawCarrying -> t.Pulled(World()) with zero-age cache scans w*h + plants. Live: WorldBuilds counter while 3 carriers walk 10 cells on a 250x250 forest map.
- **C7a-F7** CONFIRMED MEDIUM — Every connected reel builds and destroys a new feed Mesh every rendered frame (also paused). DrawFeed (Hose/RM_MapComponent_Hoses.cs:950-966) calls Ribbon -> new Mesh each frame into frameMeshes; not cached like settled strands.
- **C7a-F8** PLAUSIBLE LOW — Corridor hash walks the hose's whole bounding rectangle (quadratic for diagonal hoses; distant walls invalidate). CorridorHash loops z0-2..z1+2 x x0-2..x1+2. Offline: count sig calls for equal-length straight vs diagonal hoses.
- **C7b-F7** PLAUSIBLE LOW — Carried trail keeps every walked cell (unbounded history; ShortenBy quadratic). HoseCarry.Step appends; length uses PulledLength. Offline: 1600-cell serpentine within 40-cell reach, measure Cells.Count and ShortenBy time.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
