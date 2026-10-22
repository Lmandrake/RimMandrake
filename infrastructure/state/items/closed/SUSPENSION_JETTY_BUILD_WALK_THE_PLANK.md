## spec
Child 6 of `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING`. The ruled cantilever: a short **jetty** (`design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md` §3, owner card:
"short jetty, 1-2 squares", against the none-in-v1 recommendation).
- Starts from an anchor on solid ground at deck height (its own or a bridge's); 1 to 2 cells out over a hole or water;
  no far end. Steel or heavy tier only.
- Railed on its three open sides by default; the same railing switch and open-edge rules as a bridge.
- Load capped at one person's weight (proposal 120 kg × load multiplier), shown in the inspect pane.
- Fails at the root: the whole overhang drops at once (descent for those on it; roof-collapse hit below once the
  underpass item has landed). Losing its anchor drops it.
- Uses: push a prisoner from (open edge), fish from, pour from.
Dependencies: `SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS`. Art: jetty `Graphic_Multi` ×4 styles (art item).
ESTIMATE 1.5 agent-days + 0.25 day live.

## verify
- L2: place a 2-cell steel jetty from a bank over a 4 m pit: accepted; a 3-cell one: refused with the reason.
- L2: one 70 kg colonist on the jetty: stands; add a second: inspect reads over 120 kg and the whole jetty drops
  (both jetty things gone in the same tick; both pawns on the pit floor).
- L2: railings off: a pawn can be ordered to drop off the open edge into the pit (position read after the job).
