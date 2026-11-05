#!/usr/bin/env python3
"""gravship_rotation_audit.py -- can every building of ours turn when a gravship turns?

VERSION 1.0 (2026-11-05). Item: GRAVSHIP_ROTATION_AUDIT_EVERY_BUILDING_TURNS.
Owner, 2026-10-22: "All art installable on a gravship MUST be able to rotate when the ship does.
File a ticket at this time to scan through all objects we've created to ensure they can be rotated
as per the needs of a Gravship, then based on the results ticket out Foundry items to fix anything
wrong."

WHAT THE ENGINE DOES (RimWorld 1.6 decompile, RimWorld.Planet.Gravship.GetPlacementValues)
==========================================================================================
When a ship lands turned, every thing's local position is turned about the ship origin, then:
  rotatable def                          -> rotation = shipRotation.Rotated(relativeRotation)
  rotatable=false, square footprint      -> footprint re-centred, rotation = defaultPlacingRot
                                            (the thing never turns: its art, ports and offsets
                                            keep pointing the same world direction)
  rotatable=false, non-square, Building  -> rotation FORCED to shipRotation.Rotated(relative),
                                            a facing the def says it never has
Graphic_Multi (Verse.Graphic_Multi.Init): a missing _north is the _south (or a side) turned; a
missing side is the other side mirrored; NO side at all draws the north picture on the sides.

WHAT IT READS (offline, repo only, deterministic)
================================================
Every concrete ThingDef under src/RimMandrake, src/RimStarWars, src/RimUtinni whose resolved
category is Building and which a player can put on a ship: it has a designationCategory, or it is
minifiable (minifiedDef). ParentName is resolved across our three tiers and then through
gravship_rotation_vanilla.json (the vanilla/DLC abstract parents, snapshotted from the game's Data
folder by --refresh-vanilla, plus its hand-copied "donor_nodes" for a donor framework's parents that
absorbed defs still name, each with its source; a ParentName found in neither is an UNRESOLVED
row and fails --check).
Texture facings are looked up in our Textures folders; a texPath with no file of ours is VANILLA
art (not judged: the base game draws its own facings).

THE CLASSES (one per installable building)
  OK            rotatable, and its graphic has every facing it needs (Multi with a south and a
                side; Single/Random/etc. on a 1x1 or square building turned as a picture; linked)
  FORCED_TURN   rotatable=false and non-square: the engine turns it anyway (defect: make rotatable)
  FIXED_FACING  rotatable=false and square: it never turns, like a vanilla lamp; fine for symmetric
                art (a defect only when its code or comps point somewhere: see DIRECTION_CODE)
  FIXED_BUT_FACED rotatable=false and square, yet our art draws a _north/_east/_west facing: the
                drawn sides can never show, and on a turned ship it keeps its south face (defect)
  (a Door -- thingClass *Door*, or a DoorBase child -- is judged OK: a door takes its facing from
  its walls on every spawn, ship or not)
  MULTI_NO_SIDE Graphic_Multi on our art with no _east and no _west: sides draw the north picture
  MULTI_NO_FRONT Graphic_Multi on our art with no _south: the front is another view
  PICTURE_SPIN  rotatable, NON-square, on one picture (Single-like class): the footprint turns and the
                art is spun as a flat picture (a side-on sprite lies on its side), or with
                drawRotated=false it does not spin and no longer covers its footprint
  CUSTOM_GRAPHIC rotatable, non-square, on a graphic class of our own (not Single-like, Multi or
                linked): this audit cannot judge it, so it is a defect row until a hand verdict in
                row_ok says it turns (a square one is OK)
  UNRESOLVED    a ParentName neither our tree nor the vanilla snapshot knows
Orthogonal flag, on any row:
  DIRECTION_CODE our C# class (thingClass, comp, placeWorker) behind the def names a fixed compass
                direction (Rot4.West, IntVec3.East, ...) in a file that never mentions Rotation:
                a port or offset that may not turn with the ship. Also raised when one of our comps
                carries a vector-valued property (an offset, "(x,y,z)") and its C# file never
                mentions Rotation. Each (class, file) is judged once
                in gravship_rotation_owed.json "reviewed" with a reason, or it fails --check.

--check exits 1 when a defect row (FORCED_TURN, FIXED_BUT_FACED, MULTI_NO_SIDE, MULTI_NO_FRONT,
PICTURE_SPIN, CUSTOM_GRAPHIC, UNRESOLVED, or a DIRECTION_CODE unreviewed or reviewed as a defect) is neither judged
OK by hand in "row_ok" (def -> reason; e.g. top-down floor art, which spins correctly) nor listed
under a group in gravship_rotation_owed.json; when a listed def, a row_ok def or a review is no
longer flagged (STALE); when a review lacks class/file or its verdict is not ok/defect; when a
Defs XML file fails to parse (PARSE_ERROR); or when a group's item id has no `file` event in
infrastructure/state/ledger/events/*.jsonl.
Blind spots: Patches/ operations that rewrite rotatable/graphicClass are not applied; a class
defined in a vanilla/donor assembly is not scanned; a C# file that mentions Rotation anywhere is
trusted whole (a fixed direction beside a turned one is not seen); art symmetry is not judged.

USAGE
    python3 src/RimMandrake/Utils/gravship_rotation_audit.py            # table to stdout
    python3 src/RimMandrake/Utils/gravship_rotation_audit.py --md out.md --json rows.json
    python3 src/RimMandrake/Utils/gravship_rotation_audit.py --check    # the lint gate
    python3 src/RimMandrake/Utils/gravship_rotation_audit.py --refresh-vanilla "<RimWorld Data dir>"
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
OWED_FILE = os.path.join(HERE, "gravship_rotation_owed.json")
VANILLA_FILE = os.path.join(HERE, "gravship_rotation_vanilla.json")
LEDGER_GLOB = os.path.join(REPO, "infrastructure", "state", "ledger", "events", "*.jsonl")
DEFECTS = ("FORCED_TURN", "FIXED_BUT_FACED", "MULTI_NO_SIDE", "MULTI_NO_FRONT", "PICTURE_SPIN",
           "CUSTOM_GRAPHIC", "UNRESOLVED")
VERDICTS = ("ok", "defect")
# Scalar fields read off the def (path under the ThingDef element).
FIELDS = ("category", "thingClass", "rotatable", "size", "designationCategory", "minifiedDef",
          "graphicData/graphicClass", "graphicData/texPath", "graphicData/drawRotated",
          "graphicData/linkType", "graphicData/linkFlags")
LISTS = ("comps", "placeWorkers")
SINGLE_LIKE = {"Graphic_Single", "Graphic_Random", "Graphic_StackCount", "Graphic_Indexed",
               "Graphic_Appearances", "Graphic_RandomRotated", "Graphic_Cluster", "Graphic_Flicker"}
LINKED = {"Graphic_Linked", "Graphic_LinkedCornerFiller", "Graphic_LinkedTransmitter"}
DIR_RE = re.compile(r"\b(?:Rot4|IntVec3)\.(?:North|East|South|West)\b")
VEC_RE = re.compile(r"^\(\s*-?[\d.]+\s*,\s*-?[\d.]+\s*,\s*-?[\d.]+\s*\)$")
CLASS_RE = re.compile(r"^\s*(?:(?:public|internal|private|protected|sealed|static|abstract|partial)\s+)*"
                      r"class\s+(\w+)", re.M)
COMPCLASS_RE = re.compile(r"\bcompClass\s*=\s*typeof\(\s*(?:[\w.]+\.)?(\w+)\s*\)")
ROT_RE = re.compile(r"\bRotation\b|\bRotatedBy\b|\.Rotated\(|\bRot4\s+\w+\s*[=,)]|\bRot4 rot\b")


def _scalars(e):
    out = {}
    for f in FIELDS:
        c = e.find(f)
        if c is not None and c.text and c.text.strip():
            out[f] = c.text.strip()
    return out


def _lists(e):
    out = {}
    for tag in LISTS:
        c = e.find(tag)
        if c is None:
            continue
        vals, vecs = [], []
        for li in c.findall("li"):
            names = [li.get("Class"), (li.findtext("compClass") or "").strip()]
            names = [x for x in names if x] or [(li.text or "").strip()]
            for v in filter(None, names):
                vals.append(v)
                if any(x.text and VEC_RE.match(x.text.strip()) and x.tag != "color"
                       for x in li.iter() if x is not li):
                    vecs.append(v)
        out[tag] = {"vals": vals, "vecs": vecs, "reset": c.get("Inherit", "").lower() == "false"}
    return out


def _node(e):
    return {"parent": e.get("ParentName"), "f": _scalars(e), "l": _lists(e)}


def refresh_vanilla(data_dir, out=VANILLA_FILE):
    """Snapshot every named ThingDef of the game's Data folder (Core + DLC) the resolver needs."""
    nodes = {}
    donor = json.load(open(out)).get("donor_nodes", {}) if os.path.isfile(out) else {}
    for p in sorted(glob.glob(os.path.join(data_dir, "*", "Defs", "**", "*.xml"), recursive=True)):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for e in root:
            if e.tag != "ThingDef":
                continue
            key = e.get("Name") or e.findtext("defName")
            if key:
                nodes[key.strip()] = _node(e)
    with open(out, "w") as fh:
        json.dump({"source": "RimWorld Data/*/Defs ThingDef, by Name or defName", "nodes": nodes,
                   "donor_nodes": donor}, fh, indent=0, sort_keys=True)
        fh.write("\n")
    return len(nodes)


def load(src_root, errors=None):
    """(our named nodes, our concrete defs [(defName,node,path)], our Textures dirs, cs files).
    A Defs XML file that fails to parse is appended to `errors` (its defs would vanish unseen)."""
    named, concrete, tex_dirs, cs = {}, [], [], []
    for tier in TIERS:
        base = os.path.join(src_root, tier)
        for p in sorted(glob.glob(os.path.join(base, "**", "*.xml"), recursive=True)):
            if os.sep + "Defs" + os.sep not in p:
                continue
            try:
                root = ET.parse(p).getroot()
            except ET.ParseError as ex:
                if errors is not None:
                    errors.append("%s: %s" % (os.path.relpath(p, src_root), ex))
                continue
            for e in root:
                if e.tag != "ThingDef":
                    continue
                n = _node(e)
                if e.get("Name"):
                    named[e.get("Name")] = n
                dn = (e.findtext("defName") or "").strip()
                if dn and e.get("Abstract", "").lower() != "true":
                    concrete.append((dn, n, p))
        tex_dirs += sorted(glob.glob(os.path.join(base, "**", "Textures"), recursive=True))
        cs += sorted(p for p in glob.glob(os.path.join(base, "**", "*.cs"), recursive=True)
                     if os.sep + "obj" + os.sep not in p)
    return named, concrete, tex_dirs, cs


def resolve(node, named, vanilla):
    """Merged {scalars, lists} down the ParentName chain; ours shadow vanilla. None if unresolved."""
    chain, cur, seen = [node], node, 0
    while cur.get("parent"):
        pn = cur["parent"]
        nxt = named.get(pn) or vanilla.get(pn)
        if nxt is None or seen > 30:
            return None, pn
        chain.append(nxt)
        cur, seen = nxt, seen + 1
    f, lists, vecs = {}, {t: [] for t in LISTS}, []
    for n in reversed(chain):
        f.update(n["f"])
        for t, v in n["l"].items():
            lists[t] = list(v["vals"]) if v["reset"] else lists[t] + v["vals"]
            if t == "comps":
                vecs = list(v.get("vecs", [])) if v["reset"] else vecs + v.get("vecs", [])
    door = any(x.get("parent") == "DoorBase" for x in chain) or "Door" in _short(f.get("thingClass") or "")
    return {"f": f, "l": lists, "vecs": vecs, "door": door}, None


def facings(tex, tex_dirs):
    found = set()
    for d in tex_dirs:
        for fc in ("north", "east", "south", "west"):
            if os.path.isfile(os.path.join(d, tex + "_" + fc + ".png")):
                found.add(fc)
        if os.path.isfile(os.path.join(d, tex + ".png")) or glob.glob(os.path.join(d, tex, "*.png")):
            found.add("single")
    return found


def _size(s):
    m = re.match(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", s or "")
    return (int(m.group(1)), int(m.group(2))) if m else (1, 1)


def _short(cls):
    return cls.rsplit(".", 1)[-1] if cls else cls


def cs_index(cs_files):
    """class short name -> [files defining it]; also, for a file that sets `compClass = typeof(X)`,
    each class it declares -> X under the key ("comp", class), so a CompProperties named in XML
    leads to the ThingComp that does the work."""
    idx = {}
    for p in cs_files:
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        declared = [m.group(1) for m in CLASS_RE.finditer(txt)]
        comps = COMPCLASS_RE.findall(txt)
        for c in declared:
            idx.setdefault(c, []).append(p)
            for x in comps:
                if x != c:
                    idx.setdefault(("comp", c), []).append(x)
    return idx


def direction_hits(classes, idx, root, vec_classes=()):
    """[(class, relfile, [line numbers])] for our C# files that never mention Rotation and either
    name a compass direction or implement a comp whose XML carries a vector-valued property."""
    out = []
    vec_short = set(_short(x) for x in vec_classes)
    names = set(filter(None, (_short(x) for x in list(classes) + list(vec_classes))))
    for c in list(names):
        for x in idx.get(("comp", c), []):
            names.add(x)
            if c in vec_short:
                vec_short.add(x)
    for c in sorted(names):
        for p in sorted(set(idx.get(c, []))):
            txt = open(p, encoding="utf-8", errors="replace").read()
            if ROT_RE.search(txt):
                continue
            lines = [i + 1 for i, ln in enumerate(txt.splitlines())
                     if DIR_RE.search(ln) and not ln.strip().startswith("//")]
            if not lines and c in vec_short:
                lines = [0]
            if lines:
                out.append((c, os.path.relpath(p, root), lines))
    return out


def audit(src_root=None, vanilla_path=VANILLA_FILE):
    src_root = src_root or os.path.join(REPO, "src")
    vj = json.load(open(vanilla_path)) if os.path.isfile(vanilla_path) else {}
    vanilla = dict(vj.get("nodes", {}))
    vanilla.update({k: v for k, v in vj.get("donor_nodes", {}).items() if not k.startswith("_")})
    errors = []
    named, concrete, tex_dirs, cs = load(src_root, errors)
    idx = cs_index(cs)
    root = os.path.dirname(src_root)
    rows, skipped = [], 0
    for dn, node, path in concrete:
        r, miss = resolve(node, named, vanilla)
        rel = os.path.relpath(path, root)
        if r is None:
            rows.append({"def": dn, "file": rel, "cls": "UNRESOLVED", "why": "ParentName " + miss})
            continue
        f = r["f"]
        if f.get("category") != "Building":
            skipped += 1
            continue
        if not (f.get("designationCategory") or f.get("minifiedDef")):
            skipped += 1
            continue
        rot = f.get("rotatable", "true").lower() != "false"
        sx, sz = _size(f.get("size"))
        square = sx == sz
        gclass = _short(f.get("graphicData/graphicClass")) or "Graphic_Single"
        tex = f.get("graphicData/texPath")
        have = facings(tex, tex_dirs) if tex else set()
        ours = bool(have)
        drawrot = f.get("graphicData/drawRotated", "true").lower() != "false"
        linked = gclass in LINKED or bool(f.get("graphicData/linkType"))
        why = ""
        if r["door"]:
            cls, why = "OK", "a door: faces its walls on every spawn"
        elif not rot and not square:
            cls, why = "FORCED_TURN", "rotatable=false, size %dx%d: the engine turns it anyway" % (sx, sz)
        elif not rot and gclass == "Graphic_Multi" and have & {"north", "east", "west"}:
            cls, why = "FIXED_BUT_FACED", "rotatable=false, square, facings drawn: " + ",".join(sorted(have))
        elif not rot:
            cls, why = "FIXED_FACING", "rotatable=false, square: never turns"
        elif linked or not ours:
            cls, why = "OK", "linked graphic" if linked else "vanilla/DLC art (not judged)"
        elif gclass == "Graphic_Multi":
            if not have & {"east", "west"}:
                cls, why = "MULTI_NO_SIDE", "facings drawn: " + ",".join(sorted(have))
            elif "south" not in have:
                cls, why = "MULTI_NO_FRONT", "facings drawn: " + ",".join(sorted(have))
            else:
                cls, why = "OK", "facings drawn: " + ",".join(sorted(have))
        elif gclass in SINGLE_LIKE:
            if square:
                cls, why = "OK", "%s on a square footprint, spun as a picture" % gclass
            else:
                cls = "PICTURE_SPIN"
                why = "%s, size %dx%d%s" % (gclass, sx, sz,
                                            ", drawRotated=false: art does not cover the turned footprint"
                                            if not drawrot else ": art spun on its side")
        elif square:
            cls, why = "OK", "%s (a graphic class of its own) on a square footprint" % gclass
        else:
            cls, why = "CUSTOM_GRAPHIC", "%s, size %dx%d: a graphic class this audit cannot judge" % (
                gclass, sx, sz)
        classes = [f.get("thingClass")] + r["l"]["comps"] + r["l"]["placeWorkers"]
        hits = direction_hits(classes, idx, root, r["vecs"])
        rows.append({"def": dn, "file": rel, "cls": cls, "why": why, "size": "%dx%d" % (sx, sz),
                     "rotatable": rot, "graphic": gclass, "tex": tex,
                     "direction_code": [{"class": c, "file": p, "lines": ln} for c, p, ln in hits]})
    rows.sort(key=lambda x: (x["cls"], x["def"]))
    return rows, {"defs": len(concrete), "skipped": skipped, "tex_dirs": len(tex_dirs), "cs": len(cs),
                  "parse_errors": errors}


def load_owed(path=OWED_FILE):
    if not os.path.isfile(path):
        return {"groups": [], "reviewed": []}
    return json.load(open(path))


def filed_ids(glob_pat=LEDGER_GLOB):
    ids = set()
    for p in glob.glob(glob_pat):
        for ln in open(p, encoding="utf-8", errors="replace"):
            if '"event": "file"' not in ln and '"event":"file"' not in ln:
                continue
            try:
                ev = json.loads(ln)
            except ValueError:
                continue
            if ev.get("event") == "file" and ev.get("id"):
                ids.add(ev["id"])
    return ids


def defect_keys(rows, owed):
    """{def: reason} for every row that owes a fix, DIRECTION_CODE folded in by review."""
    reviewed = {(x.get("class"), x.get("file")): x for x in owed.get("reviewed", [])}
    row_ok = owed.get("row_ok", {})
    out, unreviewed = {}, []
    for r in rows:
        if r["cls"] in DEFECTS and r["def"] not in row_ok:
            out[r["def"]] = r["cls"]
        for h in r.get("direction_code", []):
            v = reviewed.get((h["class"], h["file"]))
            if v is None:
                unreviewed.append((r["def"], h["class"], h["file"]))
            elif v.get("verdict") == "defect":
                out.setdefault(r["def"], "DIRECTION_CODE")
    return out, unreviewed


def problems(rows, owed, ids=None, parse_errors=()):
    ids = filed_ids() if ids is None else ids
    bad = ["PARSE_ERROR " + e for e in parse_errors]
    for x in owed.get("reviewed", []):
        if not x.get("class") or not x.get("file") or x.get("verdict") not in VERDICTS:
            bad.append("BAD_REVIEW %r: needs class, file and a verdict in %s" % (x, "/".join(VERDICTS)))
    defects, unreviewed = defect_keys(rows, owed)
    for d, c, f in unreviewed:
        bad.append("UNREVIEWED %s: %s in %s names a fixed direction" % (d, c, f))
    listed = {}
    for g in owed.get("groups", []):
        if g.get("item") not in ids:
            bad.append("UNFILED group %s: item %s has no file event" % (g.get("group"), g.get("item")))
        for d in g.get("defs", []):
            listed[d] = g.get("group")
    for d, c in sorted(defects.items()):
        if d not in listed:
            bad.append("UNLISTED %s (%s)" % (d, c))
    for d, g in sorted(listed.items()):
        if d not in defects:
            bad.append("STALE %s listed under %s but no longer a defect" % (d, g))
    cls_of = {r["def"]: r["cls"] for r in rows}
    for d in sorted(owed.get("row_ok", {})):
        if cls_of.get(d) not in DEFECTS:
            bad.append("STALE %s judged OK in row_ok but is no longer a defect row" % d)
    rk = {(h["class"], h["file"]) for r in rows for h in r.get("direction_code", [])}
    for x in owed.get("reviewed", []):
        if (x.get("class"), x.get("file")) not in rk:
            bad.append("STALE review %s %s: no longer flagged" % (x.get("class"), x.get("file")))
    return bad


def table(rows, stats):
    from collections import Counter
    cnt = Counter(r["cls"] for r in rows)
    dc = sum(1 for r in rows if r.get("direction_code"))
    out = ["# Gravship rotation audit", "",
           "%d concrete ThingDefs read, %d not installable (not Building or not placeable), %d installable "
           "buildings judged; %d Textures dirs, %d C# files." % (stats["defs"], stats["skipped"], len(rows),
                                                              stats["tex_dirs"], stats["cs"]), "",
           "Classes: " + ", ".join("%s %d" % kv for kv in sorted(cnt.items())) +
           "; DIRECTION_CODE flags %d." % dc, "",
           "| def | class | size | graphic | why | direction code |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["cls"] == "OK" and not r.get("direction_code"):
            continue
        dcs = "; ".join("%s %s:%s" % (h["class"], h["file"], ",".join(map(str, h["lines"][:4])))
                        for h in r.get("direction_code", []))
        out.append("| %s | %s | %s | %s | %s | %s |" % (r["def"], r["cls"], r.get("size", ""),
                                                      r.get("graphic", ""), r["why"], dcs))
    out.append("")
    out.append("OK rows with no flag are omitted (%d)." % sum(1 for r in rows if r["cls"] == "OK"
                                                            and not r.get("direction_code")))
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--md")
    ap.add_argument("--json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--refresh-vanilla", metavar="DATA_DIR")
    a = ap.parse_args(argv)
    if a.refresh_vanilla:
        print("vanilla nodes: %d -> %s" % (refresh_vanilla(a.refresh_vanilla), VANILLA_FILE))
        return 0
    rows, stats = audit()
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rows, fh, indent=1)
    md = table(rows, stats)
    if a.md:
        with open(a.md, "w") as fh:
            fh.write(md)
    if a.check:
        bad = problems(rows, load_owed(), parse_errors=stats["parse_errors"])
        for b in bad:
            print(b)
        print("gravship_rotation_audit: %d installable buildings, %d problems" % (len(rows), len(bad)))
        return 1 if bad else 0
    if not a.md:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
