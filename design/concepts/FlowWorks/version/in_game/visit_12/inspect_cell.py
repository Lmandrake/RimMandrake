"""inspect_cell.py x z: the inspect strings of every thing on one cell of the live map (visit 12 strange-thing probe)."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6, "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
x, z = int(sys.argv[1]), int(sys.argv[2])
r = B.call("rimworld/get_cell_info", x=x, z=z) or {}
print(json.dumps(r, default=str)[:1500])
