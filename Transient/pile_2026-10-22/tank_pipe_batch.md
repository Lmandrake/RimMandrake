# tank_pipe_batch — BENCH helper, 2026-10-22 (offline)
Status: DONE (offline) — ready for a live check
## 1 TANK_FLANGE_FIX_HOVERS_MID_PIPE — fixed f4033cbd6d
Cause MOD: flange printed on the footprint edge; tank art leaves a transparent margin (Scrapper universal tank skid 0.46 above). Fix: TankArtEdges table (16 tank x look, 4 sides x 2 lanes, generated from art by selftest_tank_art_edges.py) -> LiquidJoinRule.FlangeOnArt; ReachStub when under-run off. C# case TankFlange_sits_on_the_drawn_edge_every_tank_look_side_lane.
## 2 TANK_STUB_HUNT_POINTS_AT_NOTHING — built at c750fe9056 (not mine)
Cause MOD (hose layer): the sideways bar was reel o1's pre-fix link (census: port pipe (17,43), side -1,0) running from the pipe along z43.5 and stopping at the reel's edge cell in air. c750fe9056's ReelFeed (nozzle or under-reel) replaced it; r49818_reel.png (20:22) shows the new shape.
## 3 C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE — fixed f4033cbd6d
Cause MOD: the L = CornerStub elbow of the trunk pipe at the tank's SE corner, whose run already joins the tank along the east edge; tall art's margin shows it. Fix: CornerStubWanted (skip when a pipe sits on either cell between). No flange: deployed DLL predates fittings; HEAD puts it on the drawn side (tall: 0.27-0.36 in).
## 4 C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING — built caa3d759b4
SITE: conduits ran along the bank row (z39), the GSS slack loop bulged north over the water. Battery now (19,35), conduits (19,39..37) south of the pump.
## 5 CREEK_STATIONS_REDESIGN_FORDED_A_PUDDLE — built caa3d759b4
SITE: crossings() accepted a sliver of water with the same land mass both sides (z105 inlet). Now both ends on different land components; spacing counts spanning stations' far banks. On save c map R terrain (decoded via StableStringHash%65535): old R1/R2 on the inlet, new 8/8 whole-river crossings. Stone look filed FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE (<color> 128,124,112 halves the texture).
## Tests / shas / live checks owed
stock SelfTest 840/840 (hose 380/380 incl. joints 256/256); selftest_tank_art_edges, selftest_hose_ports, selftest_review_map, selftest_scenarios_map PASS. Shas f4033cbd6d (C#+DLL), caa3d759b4 (builders).
Live owed: deploy HEAD FlowWorks; zoom C3 north flange + reel link; rebuild map R C1 + C11 (scenarios_map --river), capture C1 tank/cord, R1/R2 ford.
DIRTY (small hunks, not full-file reviewed): scenarios_map.py, review_map_rivers.py, selftest_review_map.py.
