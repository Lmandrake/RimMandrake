#!/usr/bin/env python3
"""donor_retire_census.py — what still ties OUR content to the donor mods being retired (owner, 2026-10-18:
"Just put in placeholder art for now or donor copies and retire these mods!!! Just get it done.").

    python3 src/RimMandrake/Utils/donor_retire_census.py refs [--json OUT]   live (non-comment) references in src/
    python3 src/RimMandrake/Utils/donor_retire_census.py tex  [--json OUT]   our defs' texPaths the game does NOT serve
                                                                             from a mandrake.* mod
    python3 src/RimMandrake/Utils/donor_retire_census.py deps                active non-mandrake mods that hard-depend on
                                                                             a retiring donor

refs  reads XML as ELEMENTS (comments never count): MayRequire/MayRequireAnyOf attributes, <li> text equal to a
      packageId (FindMod <mods>, About.xml modDependencies/loadAfter/loadBefore), <packageId> in modDependencies;
      .cs/.py/.json by plain string match (they have no comment-free parse here; each hit is listed).
tex   every texPath of a def defined by a mandrake.* mod (ThingDef body/extra + PawnKind bodies from gametex's
      deftex, TerrainDef texturePath, ThingDef uiIconPath — from the gametex DefDump capture) resolved with
      gametex.resolve_res: OURS (winner mandrake.*), DONOR (winner another mod, or only an inactive mod's copy, or a
      donor AssetBundle), VANILLA (ludeon.* loose or base bundles), MISSING (nowhere). UI/ icons are included.
      SANITY: a known-ours texPath must classify OURS, else the run aborts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))

# The retiring set: biome_sprint_kickoff_2026-10-15 §0.5.1 + DONOR_DEFS_PORT_TO_OURS_1's ten smaller donors.
DONORS = [
    "mlie.starwarsanimalcollection", "sarg.alphaanimals", "daria40k.alphaanimalspatchoutposts",
    "sarg.alphabiomes", "sarg.alphamemes", "sarg.alphagenes",
    "oskarpotocki.vfe.insectoid2", "who.vfee.isopodageneline", "mlie.horrors", "biomesteam.biomescaverns",
    "lingluo.cockroach", "regrowth.botr.core", "vanillaexpanded.vgeneticse",
]
# inactive mods whose OWN content paths our defs name (not retextures of base-game art): such a path is missing in game
CONTENT_DONORS = {"vanillaexpanded.vplantsesucculents"}
SKIP_DIRS = ("src/RimMandrake/FlowWorks/",)          # not ours to touch (coordinator, 2026-10-18)
MODSCONFIG = Path("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml")


def _donor_of(text: str):
    low = text.lower()
    return [d for d in DONORS if d in low]


def refs() -> list[dict]:
    out = []
    for p in sorted(SRC.rglob("*")):
        if not p.is_file() or p.suffix not in (".xml", ".cs", ".py", ".json"):
            continue
        rel = p.relative_to(REPO).as_posix()
        skip = rel.startswith(SKIP_DIRS)
        if p.suffix == ".xml":
            try:
                root = ET.parse(p).getroot()
            except ET.ParseError:
                txt = p.read_text(errors="replace")
                for d in _donor_of(txt):
                    out.append({"file": rel, "donor": d, "form": "UNPARSEABLE_XML", "skip": skip})
                continue
            parent = {c: q for q in root.iter() for c in q}
            for el in root.iter():
                for k, v in el.attrib.items():
                    for d in _donor_of(v):
                        out.append({"file": rel, "donor": d, "form": f"attr:{k}", "tag": el.tag,
                                    "value": v, "skip": skip})
                t = (el.text or "").strip()
                if t and len(t) < 120:
                    for d in _donor_of(t):
                        if t.lower() == d or el.tag == "packageId":
                            q = parent.get(el)
                            qq = parent.get(q) if q is not None else None
                            ctx = "/".join(x.tag for x in (qq, q) if x is not None)
                            out.append({"file": rel, "donor": d, "form": f"text:{ctx}/{el.tag}", "skip": skip})
        else:
            for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                for d in _donor_of(line):
                    out.append({"file": rel, "donor": d, "form": f"string{p.suffix}", "line": i,
                                "text": line.strip()[:160], "skip": skip})
    return out


def _texpaths():
    import gametex as G
    dt = G.deftex()
    cap = Path(dt["capture"]) / "defs"
    rows = []
    for dn, v in dt["defs"].items():
        pkg = v.get("packageId") or ""
        if not pkg.startswith("mandrake."):
            continue
        for t in v["tex"]:
            rows.append((dn, "ThingDef", "body", t, v.get("mod")))
        for t, role in (v.get("extra") or {}).items():
            rows.append((dn, "ThingDef", role, t, v.get("mod")))
    for typ, fld, role in (("TerrainDef", "texturePath", "terrain"), ("ThingDef", "uiIconPath", "icon")):
        f = cap / f"{typ}.json"
        for d in json.loads(f.read_text())["defs"]:
            if not (d.get("packageId") or "").startswith("mandrake."):
                continue
            t = (d.get("fields") or {}).get(fld)
            if isinstance(t, str) and t:
                rows.append((d["defName"], typ, role, t, d.get("modName")))
    keyre = re.compile(r"(texPath|texturePath|iconPath|IconPath|GraphicPath|texPathFaction)$")

    def walk(v, dn, typ, mod, path=""):
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(x, str) and x and keyre.search(k):
                    rows.append((dn, typ, f"{path}{k}", x, mod))
                else:
                    walk(x, dn, typ, mod, f"{path}{k}.")
        elif isinstance(v, list):
            for x in v:
                walk(x, dn, typ, mod, path)
    for f in sorted(cap.glob("*.json")):              # every other def type: icons, flecks, motes, hediffs ...
        if f.stem in ("ThingDef", "PawnKindDef", "TerrainDef"):
            continue
        try:
            defs = json.loads(f.read_text()).get("defs") or []
        except (ValueError, OSError):
            continue
        for d in defs:
            if (d.get("packageId") or "").startswith("mandrake."):
                walk(d.get("fields") or {}, d["defName"], f.stem, d.get("modName"))
    return dt["capture"], rows


def classify(res: str, ix) -> dict:
    import gametex as G
    r = G.resolve_res(res, ix)
    win = next((c for c in r["copies"] if c.get("winner")), None)
    if win:
        pkg = (win["packageId"] or "").lower()
        cat = "OURS" if pkg.startswith("mandrake.") else ("VANILLA" if pkg.startswith("ludeon.") else "DONOR")
        if cat == "DONOR":                               # a retexture of a base-game path: vanilla serves it without
            vb = [b for b in G.resolve_res(res, {**ix, "files": {}})["bundle"]   # the donor
                  if (b["source"] or "").lower().startswith("ludeon.")]
            if vb:
                cat = "VANILLA_RETEXTURED"
        return {"cat": cat, "by": pkg, "file": next(iter(win["faces"].values()), None)}
    if not r["bundle"] and r["copies"]:                  # resolve_res fills bundle only when no copy exists
        r["bundle"] = G.resolve_res(res, {**ix, "files": {}})["bundle"]
    if r["bundle"]:
        b = next((x for x in r["bundle"] if (x["source"] or "").lower().startswith("ludeon.")), r["bundle"][0])
        src = (b["source"] or "").lower()
        return {"cat": "VANILLA" if src.startswith("ludeon.") else "DONOR_BUNDLE", "by": src, "file": b["path"]}
    if r["copies"]:                                      # only inactive mods ship it
        c = r["copies"][0]
        pkg = (c["packageId"] or "").lower()
        # a retexture pack shipping a base-game path: Core's art is not fully indexed, so this is vanilla, unproven
        cat = "DONOR_INACTIVE" if pkg in DONORS or pkg in CONTENT_DONORS \
            or not res.startswith(("Things/", "Terrain/", "UI/", "Buildings/")) else "VANILLA_UNINDEXED"
        return {"cat": cat, "by": pkg, "file": next(iter(c["faces"].values()), None)}
    return {"cat": "MISSING", "by": None, "file": None}


def tex() -> dict:
    import gametex as G
    ix = G.index()
    probe = classify("Things/Building/CrawlerRoad/RSW_WreckedSkiff", ix)
    if probe["cat"] != "OURS":
        raise SystemExit(f"SANITY FAIL: known-ours texPath classified {probe} — instrument blind, nothing reported")
    cap, rows = _texpaths()
    out, seen = [], {}
    for dn, typ, role, t, mod in rows:
        if t not in seen:
            seen[t] = classify(t, ix)
        out.append({"def": dn, "type": typ, "role": role, "tex": t, "mod": mod, **seen[t]})
    return {"capture": cap, "index_built": ix.get("built"), "load_order": ix.get("load_order"), "rows": out}


def srctex() -> dict:
    """Today's src/ (not a dump): every texPath our Defs/Patches XML names (placeholder_lint.texpaths, the
    texture_gap_lint walk), resolved first against our own src Textures, then by `classify`."""
    import gametex as G
    import placeholder_lint as PL
    ix = G.index()
    roots = PL.texture_roots()
    out = []
    for tp, files in PL.texpaths().items():
        files = sorted(files) if not isinstance(files, str) else [files]
        if PL.resolve(tp, roots):
            out.append({"tex": tp, "cat": "OURS_SRC", "by": None, "file": None, "files": files})
            continue
        c = classify(tp, ix)
        out.append({"tex": tp, **c, "files": files})
    return {"index_built": ix.get("built"), "load_order": ix.get("load_order"), "rows": out}


def deps():
    """Every installed mod's About.xml (both game roots) — not the texture index, which skips mods with no Textures."""
    active = {l.text.strip().lower() for l in ET.parse(MODSCONFIG).getroot().find("activeMods")}
    roots = [Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"),
             Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")]
    hits, seen = [], 0
    for root in roots:
        for d in root.iterdir():
            about = d / "About" / "About.xml"
            try:
                r = ET.parse(about).getroot()
            except (ET.ParseError, OSError):
                continue
            pkg = (r.findtext("packageId") or "").strip().lower()
            if pkg not in active or pkg.startswith(("mandrake.", "ludeon.")):
                continue
            seen += 1
            md = r.find("modDependencies")
            for el in (md.iter("packageId") if md is not None else []):
                v = (el.text or "").strip().lower()
                if v in DONORS:
                    hits.append((pkg, v, pkg in DONORS))
    print(f"active non-mandrake mods read: {seen}; hard dependencies on a retiring donor: {len(hits)}")
    for pkg, v, internal in hits:
        print(f"   {pkg} -> {v}" + ("   (itself retiring)" if internal else ""))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["refs", "tex", "srctex", "deps"])
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    if a.cmd == "deps":
        deps()
        return 0
    if a.cmd == "refs":
        rs = refs()
        c = Counter((r["donor"], r["form"].split(":")[0] + (":" + r["form"].split(":")[1] if ":" in r["form"] else ""))
                    for r in rs if not r["skip"])
        print(f"live references in src/ (FlowWorks excluded: {sum(1 for r in rs if r['skip'])} there): "
              f"{sum(1 for r in rs if not r['skip'])}")
        for (d, f), n in sorted(c.items()):
            print(f"  {n:4}  {d:36} {f}")
        data = rs
    elif a.cmd == "srctex":
        data = srctex()
        rows = data["rows"]
        print(f"texPaths named by src/ XML: {len(rows)}")
        for cat, n in Counter(r["cat"] for r in rows).most_common():
            print(f"  {cat:18} {n}")
        for (cat, b), n in Counter((r["cat"], r["by"]) for r in rows
                                   if r["cat"] not in ("OURS_SRC", "VANILLA")).most_common(40):
            print(f"    {cat:18} {str(b):45} {n}")
    else:
        data = tex()
        rows = data["rows"]
        print(f"capture {data['capture']}; index {data['index_built']}; {data['load_order']}")
        print(f"texPath slots of mandrake.* defs: {len(rows)} ({len({r['tex'] for r in rows})} distinct texPaths)")
        for cat, n in Counter(r["cat"] for r in rows).most_common():
            print(f"  {cat:15} {n}")
        by = Counter((r["cat"], r["by"]) for r in rows if r["cat"] not in ("OURS",))
        for (cat, b), n in by.most_common(40):
            print(f"    {cat:15} {str(b):45} {n}")
    if a.json:
        Path(a.json).write_text(json.dumps(data, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
