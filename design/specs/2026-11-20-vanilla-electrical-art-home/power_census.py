#!/usr/bin/env python3
"""power_census.py — every vanilla and DLC ThingDef that uses, makes, stores or carries power, with its texture size today.

    python3 design/specs/2026-11-20-vanilla-electrical-art-home/power_census.py [--official DB] [--live DB] [--out JSON]

Inputs (each built with `measure build --only ThingDef`, never a scan of ThingDef.json):
  --official  the frozen OFFICIAL dump (REGISTRY.jsonl id OFFICIAL-2026-08-29, capture 2026-08-29T13-30-02Z): the def SET.
  --live      the newest capture: drawSize only (the official capture does not serialize Vector2 fields; vanilla drawSize
              is Ludeon's XML, so the live value is the same number unless a mod patched it — each row says which).
Texture pixels: the extracted vanilla art (observed/inventory/bundle_textures, read-only mirror on D:).

A def is in the census when one of its comps is CompProperties_Power / CompProperties_Battery (any compClass), its package
is ludeon.*, and it is a buildable or placed building (not a blueprint, frame or minified thing).
Every row carries an outcome per field: a number, or "UNMEASURED: <why>" — never a silent blank.
"""
import argparse, json, os, re, sqlite3, struct, sys
from collections import defaultdict

BUNDLES = "/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures"
GROUPS = ("lighting", "climate", "production", "research", "turret", "entertainment", "generation", "storage",
          "network", "other")


def png_size(p):
    with open(p, "rb") as fh:
        b = fh.read(24)
    return struct.unpack(">II", b[16:24]) if b[:8] == b"\x89PNG\r\n\x1a\n" else None


def texture_index():
    """stem(lower) -> [(pkg, relpath, w, h)] for core (flat files by m_Name) and full lowercase texPaths for the DLCs."""
    by_stem, by_path = defaultdict(list), {}
    for pkg in sorted(os.listdir(BUNDLES)):
        if not pkg.startswith("ludeon."):
            continue
        root = os.path.join(BUNDLES, pkg)
        for dp, _, fs in os.walk(root):
            for f in fs:
                if not f.lower().endswith(".png"):
                    continue
                p = os.path.join(dp, f)
                wh = png_size(p)
                if not wh:
                    continue
                rel = os.path.relpath(p, root).replace(os.sep, "/")
                by_stem[f[:-4].lower()].append((pkg, rel, wh[0], wh[1]))
                if rel.lower().startswith("textures/"):
                    by_path[rel.lower()[len("textures/"):-4]] = (pkg, rel, wh[0], wh[1])
    return by_stem, by_path


def resolve_tex(tex_path, gclass, by_stem, by_path):
    """-> (w, h, how) of the south (or single) picture, or (None, None, 'UNMEASURED: why')."""
    if not tex_path:
        return None, None, "UNMEASURED: no texPath"
    tp = tex_path.lower()
    multi = "Multi" in (gclass or "")
    rnd = "Random" in (gclass or "") or "Appearances" in (gclass or "")
    cands = [tp + "_south", tp + "_north", tp] if multi else [tp]
    for c in cands:
        if c in by_path:
            pkg, rel, w, h = by_path[c]
            return w, h, "path " + pkg + "/" + rel
    if rnd:
        hits = [v for k, v in by_path.items() if k.startswith(tp + "/")]
        if hits:
            pkg, rel, w, h = sorted(hits)[0]
            return w, h, "random folder, first of %d: %s/%s" % (len(hits), pkg, rel)
    leaf = tp.rsplit("/", 1)[-1]
    for stem in ([leaf + "_south", leaf + "_north", leaf] if multi else [leaf]) + ([leaf + "a", leaf + "_a", leaf + "1"] if rnd else []):
        hits = by_stem.get(stem)
        if hits:
            core = [h for h in hits if h[0] == "ludeon.rimworld.core"] or hits
            pkg, rel, w, h = core[0]
            amb = "" if len(hits) == 1 else " (stem shared by %d files: size of the core one)" % len(hits)
            return w, h, "stem " + pkg + "/" + rel + amb
    return None, None, "UNMEASURED: no extracted vanilla picture named %s (looked for %s)" % (tex_path, ", ".join(cands))


def power_kind(comps):
    kinds = []
    for c in comps or []:
        t, cc = c.get("$type", ""), c.get("compClass", "") or ""
        if t == "CompProperties_Battery" or "Battery" in cc:
            kinds.append(("storage", c))
        elif t == "CompProperties_Power" or t.startswith("CompProperties_Power"):
            if "PowerPlant" in cc:
                kinds.append(("generation", c))
            elif "Transmitter" in cc or "PowerTransmitter" in cc:
                kinds.append(("network", c))
            else:
                kinds.append(("consumer", c))
    return kinds


def group_of(name, f, kinds):
    tc = (f.get("thingClass") or "")
    dc = (f.get("designationCategory") or "")
    ks = {k for k, _ in kinds}
    comps = [c.get("$type", "") for c in f.get("comps") or []]
    lab = (f.get("label") or "").lower()
    if "generation" in ks:
        return "generation"
    if "storage" in ks:
        return "storage"
    if "network" in ks:
        return "network"
    if "Turret" in tc or dc == "Security" and "turret" in lab:
        return "turret"
    if "ResearchBench" in tc or "research" in lab or "multi-analyzer" in lab:
        return "research"
    if "CompProperties_TempControl" in comps or "Cooler" in tc or "Heater" in tc or "cooler" in lab or "heater" in lab:
        return "climate"
    if "WorkTable" in tc or f.get("recipes") or f.get("allRecipesCached"):
        return "production"
    if dc == "Joy" or "television" in lab or "joy" in json.dumps(f.get("building") or {}).lower()[:0]:
        return "entertainment"
    if "CompProperties_Glower" in comps and ("lamp" in lab or "light" in lab or "torch" in lab):
        return "lighting"
    return "other"


def val(x):
    if isinstance(x, dict) and "x" in x:
        return [x.get("x"), x.get("y", x.get("z"))]
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--official", default="/tmp/offdump/defs.sqlite")
    ap.add_argument("--live", default="/tmp/livedump/defs.sqlite")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "power_census.json"))
    a = ap.parse_args()
    for p in (a.official, a.live):
        if not os.path.exists(p):
            sys.exit("UNMEASURED: %s missing; build it with measure --dump <capture> --db %s build --only ThingDef" % (p, p))
    off = sqlite3.connect(a.official)
    live = sqlite3.connect(a.live)
    by_stem, by_path = texture_index()
    rows = []
    for name, pkg, mod, js in off.execute(
            "select def_name, package_id, mod_name, json from defs where package_id like 'ludeon.%' order by package_id, def_name"):
        d = json.loads(js)
        f = d.get("fields") or {}
        isd = d.get("is") or {}
        if isd.get("blueprint") or isd.get("frame") or name.startswith(("Blueprint_", "Frame_", "Minified")):
            continue
        kinds = power_kind(f.get("comps"))
        if not kinds:
            continue
        g = f.get("graphicData") or {}
        tex, gcls = g.get("texPath"), (g.get("graphicClass") or "")
        lr = live.execute("select json, package_id from defs where def_name=? and package_id=?", (name, pkg)).fetchone()
        ds, ds_src, live_tex = None, "UNMEASURED: def absent from the live capture", None
        if lr:
            lg = (json.loads(lr[0]).get("fields") or {}).get("graphicData") or {}
            ds = val(lg.get("drawSize")) if lg.get("drawSize") else None
            ds_src = "live capture" if ds else "UNMEASURED: live capture has no drawSize for it"
            live_tex = lg.get("texPath")
        w, h, how = resolve_tex(tex, gcls, by_stem, by_path)
        ppc = round(w / float(ds[0]), 1) if (w and ds and ds[0]) else None
        pc = [c for k, c in kinds if k in ("consumer", "generation")]
        power = pc[0].get("basePowerConsumption") if pc else None
        rows.append({
            "def": name, "label": f.get("label"), "package": pkg, "group": group_of(name, f, kinds),
            "power_role": sorted({k for k, _ in kinds}), "basePowerConsumption": power,
            "designationCategory": f.get("designationCategory"), "buildable": bool(f.get("designationCategory")),
            "size": val(f.get("size")), "drawSize": ds, "drawSize_source": ds_src,
            "texPath": tex, "graphicClass": gcls.split(".")[-1], "texPath_live": live_tex,
            "texPath_changed_live": (live_tex is not None and live_tex != tex),
            "tex_w": w, "tex_h": h, "tex_source": how, "px_per_cell": ppc,
        })
    out = {"official_db": a.official, "live_db": a.live, "official_id": "OFFICIAL-2026-08-29", "rows": rows}
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    by = defaultdict(list)
    for r in rows:
        by[r["group"]].append(r)
    print("MEASURED %d power defs (ludeon.*) in the official dump -> %s" % (len(rows), a.out))
    for gname in GROUPS:
        rs = by.get(gname, [])
        nb = sum(1 for r in rs if r["buildable"])
        print("  %-13s %3d (%d buildable)" % (gname, len(rs), nb))


if __name__ == "__main__":
    main()
