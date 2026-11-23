## spec
Child 5 of `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING`. Suspension bridges over natural water. Owner said (Q5):
*"Let's design towards including rivers and oceans and large lakes (non canal pit types) but if we have to we can
backtrack. It seems doable but let's see how it goes."* Design: `design/RimMandrake/flowworks_bridges_design_2026-10-17.md` §3 (natural rows), §7 (floods, current);
`design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md` §1.3 (towers).
- Placement over natural water cells (rivers, large lakes, ocean) as well as dug ones; anchors on solid ground.
- Towers in water: how a builder reaches the floor (wading in shallow, swimming in deep `DEEP_WATER_BUILD_SWIM_OR_SINK`,
  or built from the deck outward) is decided at build and written into `design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md` §1.3.
- River current never carries anyone on a deck (reuse the fords' exemption, `RM_MapComponent_RiverCurrent.NearFord`).
- Floods over a deck: rope and timber take damage per hour awash in moving water (proposal 5% HP); steel/heavy do not.
- Rivers and oceans stay vanilla and limitless (R10): nothing converts their terrain; the deck is a building on top.
- **Backtrack rule:** if ocean or river crossings prove unworkable, record the measured reason on the parent and drop
  only that water type; dug-ground bridges are unaffected.
Dependencies: `SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS`; lake floors (P4 `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD`,
`WATER_NATURAL_DECIDE_ONE_SURFACE` / R10-R11) for tower depth on lakes. Art: tower (art item). ESTIMATE 2 to 3
agent-days + 0.5 day live.

## verify
- L2: a 10-cell steel bridge across a moving river, anchors on both banks: a colonist crosses (path read) and its
  position never shifts downstream while on the deck.
- L2: a 20-cell crossing over a large lake with one tower: two span records, each ≤ the tier length.
- L2: a timber bridge awash in a flood for 2 in-game hours: HP below max (read); a steel one: HP unchanged.
- L2: ocean crossing attempt: either built and crossable, or the backtrack reason recorded on the parent.
