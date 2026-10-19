## spec
Child 3 of `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING`. The grated deck variant (steel and heavy tiers only).
Design: `design/RimMandrake/flowworks_bridges_design_2026-10-17.md` §4.1-§4.2 (as ruled: Q4 spilled liquid only; Q9 rain falls through every deck, so rain is NOT a grate
difference).
- `RM_FireMath.AttachChance` gains a grated flag: burning liquid below sets pawns on a grate alight at the open-pit
  chance × 0.75 (solid keeps today's `onCover` 0.4 / 0.6). Pawns on a grate over fire take vanilla `Burn` injuries
  over time (one kind of heat: no new hediff).
- Spilled or poured liquid on a grated deck over a wet or dug cell adds its litres to the body below (stock conserved).
  Items do not fall through.
- Slime and fill splash reach pawns on a grate (half the open-pit chance).
- Shots between the deck band and the floor band pass through a grate (blocked by a solid deck) — the band read lands
  with the underpass item; this item only exposes `IsGrated` for it.
- Settings: "Grates pass fire to people above", "Grates drain spills into the hole below".
Dependencies: `SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS`. Art: grated tile with real alpha (in the art item).
ESTIMATE 1.5 to 2 agent-days + 0.5 day live.

## verify
- L1: `RM_FireMath` selftests: grated > solid attach chance; grated chance = open × 0.75.
- L2: steel grate over a 2 m pit of burning fuel, 3 pawns on it, 2,500 ticks: at least one pawn has a `Burn` hediff;
  the same scene with a solid steel deck: fewer (count both).
- L2: pour 50 L onto a grate over a wet canal: the body's stock rises by 50 L (decilitre read), no filth on the deck.
- L2: drop an item on a grate: it stays on the deck cell.
