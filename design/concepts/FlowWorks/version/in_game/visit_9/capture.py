import os, sys, json
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
out = {}
for tag, (x, z, r) in {"walk_pond": (63, 55, 14)}.items():
    s = B.call("rimworld/screenshot_cell_rect", x=x - r, z=z - r, width=2 * r + 1, height=2 * r + 1, paddingCells=1,
               fileName="v7_" + tag + os.environ.get("CAPSUFFIX", ""), suppressMessage=True) or {}
    out[tag] = s.get("path") or s.get("filePath") or str(s)[:300]
print(json.dumps(out))
