import os, sys, json
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
out = {}
for tag, (x, z, w, h) in json.loads(sys.argv[1]).items():
    s = B.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=1,
               fileName="v10_" + tag + os.environ.get("CAPSUFFIX", ""), suppressMessage=True) or {}
    out[tag] = s.get("path") or s.get("filePath") or str(s)[:300]
print(json.dumps(out))
