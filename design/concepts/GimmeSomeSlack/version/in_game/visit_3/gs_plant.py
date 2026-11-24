"""gs_plant.py: sc_gravship's repaired reads on the landed map that is up, real and planted: the cord set before is true; with the battery gone the same cords must fail; with a bracket's wall not counted as its own the wall read must fail. python.exe."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(GSS, "northstar_matrix"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation_aerial as VA, gravship_scene as GS
B = VA.A(); out = {}
c = B.probe("census"); edges = GS.cord_edges(c)
net = lambda q: GS.cell_net(B.ap("net:%d,%d" % q))
out["cords"] = [e[0] for e in edges]
out["real"] = GS.true_to_grid(edges, net)
an = [q for q in B.ap("census").get("anchors") or []]
own = [B.probe("rect:%d,%d,1,1" % (q["x"], q["z"] + 1)).get("verticesInUnwalkable") for q in an]
t = c.get("verticesInUnwalkable")
out["walls_real"] = [t, own, GS.in_other_walls(t, own)]
out["walls_planted_bracket_wall_not_its_own"] = GS.flight_verdict("off", False, False, 0, [], edges, True, GS.in_other_walls(t, [0] * len(own)))
bat = next(e for e in edges if e[0].startswith("consumer"))[2]
B.call("jawa/destroy_batch", rects="%d,%d,1,2" % bat, categories="Building"); B.ticks(10)
out["planted_battery_gone"] = GS.true_to_grid(edges, net)
out["planted_verdict"] = GS.flight_verdict("off", False, False, 0, out["planted_battery_gone"], edges, True, 0)
print(json.dumps(out, indent=1))
