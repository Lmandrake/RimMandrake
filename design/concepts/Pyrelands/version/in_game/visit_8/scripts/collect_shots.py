#!/usr/bin/env python3
"""Copy every screenshot the pv8_*.json results name into screenshots/<label>__<name>.png when under 1 MB; a larger one
is saved there as a reduced JPEG (long side 1600) and its full path printed."""
import glob, json, os, shutil
H = os.path.dirname(os.path.abspath(__file__)); V = os.path.dirname(H)
out = os.path.join(V, "screenshots"); os.makedirs(out, exist_ok=True)
for p in sorted(glob.glob(os.path.join(V, "evidence", "pv8_*.json"))):
    lab = os.path.basename(p)[4:-5]
    for c in json.load(open(p)).get("components", []):
        for s in c.get("screenshots") or []:
            w = s.get("path") if isinstance(s, dict) else s
            if not w:
                continue
            if w[1:3] == ":\\":
                src = "/mnt/" + w[0].lower() + "/" + w[3:].replace("\\", "/")
            elif w.startswith("C:\\"):
                src = "/mnt/c/" + w[3:].replace("\\", "/")
            else:
                src = w.replace("\\\\wsl.localhost\\Ubuntu", "").replace("\\", "/")
            src = os.path.normpath(src)
            if not os.path.exists(src):
                print("MISSING", lab, src); continue
            dst = os.path.join(out, "%s__%s" % (lab, os.path.basename(src)))
            if os.path.getsize(src) < 1000000:   # the brief: under 1 MB
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
            else:   # a reduced JPEG copy (long side 1600) to look at; the full file stays where the game wrote it
                dst = os.path.splitext(dst)[0] + ".jpg"
                if not os.path.exists(dst):
                    from PIL import Image
                    im = Image.open(src).convert("RGB"); im.thumbnail((1600, 1600)); im.save(dst, quality=80)
                print("REDUCED", os.path.getsize(src), w)
print(len(os.listdir(out)), "shots in", out)
