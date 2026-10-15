"""TANK_TALL_BUILD_TWICE_THE_DRINK phase 1: gather the south-facing texture of each reference building.
Sizes from the live def dump (defs.sqlite); Core/DLC art from the extracted bundle cache, mod art as loose PNGs.
Writes <out>/refs.json + one PNG per def. Run from the repo root under WSL python3."""
import json, os, sys, glob, shutil, sqlite3
sys.path.insert(0, "src/RimMandrake/Utils/art")
import scale_panel as sp
OUT = sys.argv[1]
CACHE = "/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures"
NAMES = sys.argv[2].split(",")
db = sqlite3.connect(str(sp.DB))
mods = {pid: sp._win2wsl(r) for _l, n, pid, r in db.execute("select load_order,name,package_id,root_dir from mods")}
idx = {}
for line in open(os.path.join(CACHE, "index.csv"), encoding="utf-8").read().splitlines()[1:]:
    k, name, cont, f, w, h = line.split(",")[:6]
    idx.setdefault(name.lower(), []).append((cont.lower(), f))
os.makedirs(OUT, exist_ok=True)
rows = []
for n in NAMES:
    r = db.execute("select json,package_id from defs where def_name=? and def_type='ThingDef'", (n,)).fetchone()
    if not r:
        print("MISS def", n); continue
    f = json.loads(r[0])["fields"]; g = f["graphicData"]; tp = g["texPath"]; leaf = tp.split("/")[-1]
    cands = [leaf + s for s in ("_south", "", "A", "_a")]
    hit = None
    for c in cands if r[1].startswith("ludeon.") else []:  # bundle cache: Ludeon art only, path-aware
        for cont, fp in idx.get(c.lower(), []):
            if not cont or cont.endswith((tp.lower() + c[len(leaf):] + ".png")) or tp.lower().split("/")[-2] in cont:
                hit = os.path.join(CACHE, fp); break
        if hit: break
    if not hit:
        root = mods.get(r[1])
        for c in cands:
            got = glob.glob(os.path.join(glob.escape(root), "**", "Textures", *tp.split("/")[:-1], c + ".png"), recursive=True)
            got = [p for p in got if "Common_Old" not in p]  # stranded pre-1.6 folder
            if got: hit = sorted(got, key=lambda p: ("1.6" not in p, p))[0]; break
    if not hit:
        print("MISS tex", n, tp); continue
    dst = os.path.join(OUT, n + ".png"); shutil.copy(hit, dst)
    sz, ds, off = f.get("size") or {}, g.get("drawSize") or {}, g.get("drawOffset") or {}
    rows.append(dict(defName=n, mod=r[1], src=hit, size=[sz.get("x", 1), sz.get("z", 1)],
                     drawSize=[ds.get("x", 1), ds.get("y", 1)], drawOffsetZ=off.get("z", 0), graphicClass=g.get("graphicClass")))
    print("ok", n, hit[-70:])
json.dump(rows, open(os.path.join(OUT, "refs.json"), "w"), indent=1)
