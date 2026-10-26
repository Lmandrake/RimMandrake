## spec
Build the ruled crossing rules for lines: `design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md`
§Ruled design P1-P5, P7-P9 (levelling P6 is `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL`). Summary:
- A **def-level line tag** (rigid pipe / rigid conduit / flex cord / hose), never style or `isPowerConduit`: GSS
  restyles vanilla `PowerConduit`, so a restyled conduit is still rigid (review answer 5).
- One crossing policy (P2 table) at placement, frame completion and rebuild: rigid pipe and conduit **never** on an
  excavated square, a cover or any deck; cords and hoses on **any** deck incl. rope (narrow exception, no general `Light`
  on rope); covers carry nothing; hoses into pits only by ramp or ladder.
- **Pipe poles**: GSS aerial mechanics, thicker, less sag (proposal 3 %, max span 12, sliders), the four pipe looks;
  supports on solid ground only (not deck, cover or dug square); not walking ground, not a deck, not in pawn topology.
  Liquid net gains one long-range edge: caps applied after the join, one logical edge, one port per pump side.
- **Digging breaks lines** at terrain commit (not designation); a hose re-plans or is cut. Deck collapse destroys its
  cords and hoses (live cord = fallen wire). Support-owned, idempotent teardown. No old-save migration (owner: *"Can't
  happen. We don't have any."*).
- Hose transitions lip↔ramp↔floor and lip↔ladder↔floor, band-aware endpoint reach; a raised ladder leaves the hose
  hanging. Hoses and cords on a drawbridge leaf disconnect while raised.
- Readout distinguishes deck cord, pole span, ladder/ramp hose, disconnected segment.
Dependencies: **no pole art before `LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED`** (owner answer 8); the cord def is
`POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS`. Shared aerial code location (Shared lib vs mod dependency) decided at
build. ESTIMATE 7 to 10.5 agent-days plus art. Open owner questions: design doc (submerged cord; 1 m canal).

## verify
- L1: selftests — policy table for every line kind × surface; style change does not change permission; aerial edge joins
  two 60%-cap components and is refused/accepted correctly; ring of two pole routes cut in turn; dig cancel breaks nothing;
  dig commit breaks once.
- L2 (live): pipe on a rope deck refused, cord and hose accepted; pipe across a pit on poles carries liquid; dig under a
  pipe splits the net; collapse a decked span carrying a cord (fallen-wire shock, net split exactly once); drain a pit
  through a ladder hose, then raise the ladder (hose stays).
