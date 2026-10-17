"""Find a w x h rect whose every cell is one of the given terrains (python.exe). args: w h terr1,terr2,..."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
import validation_core as V
import collections
B = V.Bridge()
w, h, ok = int(sys.argv[1]), int(sys.argv[2]), set(sys.argv[3].split(","))
ops = B.call("jawa/get_terrain_batch", rects="0,0,250,250").get("ops")
g = {}
c = collections.Counter()
for op in ops.split(";"):
    d, r = op.split(":"); x, z, ww, hh = map(int, r.split(","))
    c[d] += ww * hh
    for i in range(ww):
        for j in range(hh):
            g[(x + i, z + j)] = d
print(c.most_common(8))
for z in range(20, 230 - h, 3):
    for x in range(20, 230 - w, 3):
        if all(g.get((x + i, z + j)) in ok for i in range(w) for j in range(h)):
            print("rect", x, z); sys.exit(0)
print("none")
