"""power_lamps.py x,z: a battery there beside the wall-lamp scene's cord, filled, 600 ticks; then the lamps' power reads. python.exe."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA, scene_rows as S
B = VA.A(); x, z = (int(v) for v in sys.argv[1].split(","))
print(str(B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x, z), faction="player", wipeExisting=False))[:300])
B.call("jawa/map_commit"); B.ticks(3); S._fill(B, (x - 4, z - 6, 40, 14)); B.ap("cprocess"); B.probe("rebuild"); B.ticks(600)
print(str(B.ap("net:%d,%d" % (x, z)))[:900])
