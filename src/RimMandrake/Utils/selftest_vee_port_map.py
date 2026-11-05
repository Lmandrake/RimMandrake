#!/usr/bin/env python3
"""Selftest: design/RimMandrake/vee_port_map.json and vee_world_stamp.py (VEE_WORLD_RENAME_ONE_STAMP_AT_END).

Offline, repo only (no save, no capture, no game):
  1. every map row with a `new` has a def of the right element type in src/, in the mod the row names;
  2. each mutator port keeps its donor's categories (recorded in the map from the capture), so the stamp's
     AddMutator displacement is like-for-like (plan s3);
  3. the owner's drop (VEE_DeadlifeVents, card 2026-10-22) has no port and no RM_DeadlifeVents exists;
     the two solar rows are stamp=geometry onto RM_StrongInsolation / RM_Sunless;
  4. no def or patch of ours names a mapped VEE world def (element text, tag or attribute), with a planted
     negative proving the scan can see;
  5. vee_world_stamp's pieces on synthetic data: the raw-hash inference refuses a contested hash, the landmark
     parser reads combo landmarks, the stamp rows paint solar from geometry, and verify() passes a stamped world
     and fails one with a VEE entry, a missing port tile or a lost landmark name left in it.

    python3 src/RimMandrake/Utils/selftest_vee_port_map.py
"""
import base64
import glob
import json
import os
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import vee_world_stamp as vws  # noqa: E402

fails = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def our_defs():
    out = {}
    for p in glob.glob(os.path.join(ROOT, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root:
            n = d.findtext("defName")
            if n:
                out[(d.tag, n)] = (p, d)
    return out


def names_in(root, names):
    hits = set()
    for el in root.iter():
        if el.tag in names:
            hits.add(el.tag)
        if el.text and el.text.strip() in names:
            hits.add(el.text.strip())
        for v in el.attrib.values():
            if v in names:
                hits.add(v)
    return hits


def scan(names, extra=()):
    hits = {}
    files = glob.glob(os.path.join(ROOT, "src", "**", "Defs", "**", "*.xml"), recursive=True) + \
        glob.glob(os.path.join(ROOT, "src", "**", "Patches", "**", "*.xml"), recursive=True)
    roots = []
    for p in files:
        try:
            roots.append((p, ET.parse(p).getroot()))
        except ET.ParseError:
            continue
    for p, txt in extra:
        roots.append((p, ET.fromstring(txt)))
    for p, r in roots:
        h = names_in(r, names)
        if h:
            hits[os.path.relpath(p, ROOT)] = sorted(h)
    return hits


def main():
    m = vws.load_map()
    ours = our_defs()
    tm, lm = m["TileMutatorDef"], m["LandmarkDef"]
    check(len(tm) == vws.EXPECT["vee_defs"] and len(lm) == vws.EXPECT["vee_landmark_defs"],
          "map rows: %d mutators, %d landmarks (plan s1: %d, %d)"
          % (len(tm), len(lm), vws.EXPECT["vee_defs"], vws.EXPECT["vee_landmark_defs"]))
    check(sum(r["r3_entries"] for r in tm.values()) == vws.EXPECT["vee_entries"]
          and sum(r["r3_entries"] for r in lm.values()) == vws.EXPECT["vee_landmarks"],
          "map r3_entries sum to %d / %d" % (vws.EXPECT["vee_entries"], vws.EXPECT["vee_landmarks"]))
    # 1 + 2
    missing, wrongmod, cats = [], [], []
    for kind, rows in (("TileMutatorDef", tm), ("LandmarkDef", lm)):
        for o, r in rows.items():
            if not r.get("new"):
                continue
            hit = ours.get((kind, r["new"]))
            if not hit:
                missing.append(r["new"])
                continue
            if "/%s/" % r["mod"] not in hit[0].replace(os.sep, "/"):
                wrongmod.append(r["new"])
            if kind == "TileMutatorDef":
                c = sorted(li.text for li in hit[1].findall("categories/li"))
                pr = int(hit[1].findtext("priority") or 0)
                if c != r["categories"] or pr != r.get("priority", 0):
                    cats.append("%s %s/p%d vs donor %s/p%s" % (r["new"], c, pr, r["categories"], r.get("priority")))
    check(not missing, "every port exists in src/ as the right def type%s" % (": %s" % missing if missing else ""))
    check(not wrongmod, "every port lives in the mod its row names%s" % (": %s" % wrongmod if wrongmod else ""))
    check(not cats, "every mutator port keeps its donor's categories and priority%s" % (": %s" % cats if cats else ""))
    # 3
    dl = tm.get("VEE_DeadlifeVents", {})
    check(dl.get("drop") is True and dl.get("new") is None and ("TileMutatorDef", "RM_DeadlifeVents") not in ours,
          "VEE_DeadlifeVents is dropped (owner card 2026-10-22), no RM_DeadlifeVents")
    check(tm["VEE_MoreSolarPower"].get("new") == "RM_StrongInsolation" and tm["VEE_LessSolarPower"].get("new") ==
          "RM_Sunless" and all(tm[o].get("stamp") == "geometry" for o in vws.SOLAR),
          "solar rows map to the derived labels and are painted from geometry")
    check(sum(1 for r in tm.values() if r.get("stamp") == "geometry") == 2, "only the two solar rows are geometry")
    # 4
    names = set(tm) | set(lm)
    hits = scan(names)
    check(not hits, "no def or patch of ours names a mapped VEE world def%s" % (": %s" % hits if hits else ""))
    planted = scan(names, [("planted.xml", "<Defs><LandmarkDef><defName>X</defName><mutatorChances>"
                                           "<VEE_Cenotes>1</VEE_Cenotes></mutatorChances></LandmarkDef>"
                                           "<Patch><li Class='x' def='VEE_DryRiver'/></Patch></Defs>")])
    check(planted.get("planted.xml") == ["VEE_Cenotes", "VEE_DryRiver"], "planted negative: the scan sees a tag and "
                                                                         "an attribute (%s)" % planted.get("planted.xml"))
    # 5a raw-hash contest
    try:
        vws.raw_old_hashes(["Lakeshore"], ["Lakeshore", "Crevasse"])
        check(False, "raw_old_hashes refuses a contested hash (Lakeshore/Crevasse share 61)")
    except SystemExit:
        check(True, "raw_old_hashes refuses a contested hash (Lakeshore/Crevasse share 61)")
    # a bump chain from h-2: two names on raw h-2 push the second onto h-1... build one by search
    hv0 = vws.sdr.short_hash_raw
    tgt = hv0("VEE_Cenotes")
    pool = {}
    for i in range(400000):
        nm = "A%d" % i
        pool.setdefault(hv0(nm), []).append(nm)
        if len(pool.get((tgt - 2) & 0xFFFF, [])) >= 2 and pool.get((tgt - 1) & 0xFFFF):
            break
    chain = pool[(tgt - 2) & 0xFFFF][:2] + pool[(tgt - 1) & 0xFFFF][:1]
    try:
        vws.raw_old_hashes(["VEE_Cenotes"], ["VEE_Cenotes"] + chain)
        check(False, "raw_old_hashes refuses a hash a 3-name bump chain from h-2 reaches (%s)" % chain)
    except SystemExit:
        check(True, "raw_old_hashes refuses a hash a 3-name bump chain from h-2 reaches (%s)" % chain)
    h = vws.raw_old_hashes(["VEE_Cenotes"], ["VEE_Cenotes", "Lakeshore"])
    check(h == {"VEE_Cenotes": 55987}, "raw hash of VEE_Cenotes is 55987, the value captures record")
    # 5b parsers on a synthetic save
    def deflate(fmt, vals):
        co = zlib.compressobj(9, zlib.DEFLATED, -15)
        return base64.b64encode(co.compress(struct.pack("<%d%s" % (len(vals), fmt), *vals)) + co.flush())
    hv = vws.sdr.short_hash_raw
    ents = [(5, hv("VEE_Cenotes")), (6, hv("VEE_MoreSolarPower")), (7, hv("Lakeshore"))]
    raw = (b"<w><tileMutatorDefsDeflate>" + deflate("H", [x[1] for x in ents]) + b"</tileMutatorDefsDeflate>"
           b"<tileMutatorTilesDeflate>" + deflate("I", [x[0] for x in ents]) + b"</tileMutatorTilesDeflate>"
           b"<landmarks>\r\n<landmarks><keys><li>5,0</li><li>9,0</li></keys><values>"
           b"<li><def>VEE_Cenotes</def><name>Karst Hollows</name></li>"
           b"<li><def>Chasm</def><name>Toxo Fracture</name><isComboLandmark>True</isComboLandmark></li>"
           b"</values></landmarks>\r\n</landmarks></w>")
    check(vws.mutator_entries(raw) == ents, "mutator_entries decodes the parallel arrays")
    check(vws.landmarks(raw) == [(5, "VEE_Cenotes", "Karst Hollows"), (9, "Chasm", "Toxo Fracture")],
          "landmarks() reads plain and combo landmarks")
    # 5c stamp rows + verify on synthetic state (universe without captures: monkeypatch capture_names)
    vws.capture_names = lambda def_type="TileMutatorDef": {"VEE_Cenotes", "VEE_MoreSolarPower", "Lakeshore"}
    sm = {"TileMutatorDef": {"VEE_Cenotes": {"new": "RM_Cenotes"},
                             "VEE_MoreSolarPower": {"new": "RM_StrongInsolation", "stamp": "geometry"}},
          "LandmarkDef": {"VEE_Cenotes": {"new": "RM_Cenotes"}}}
    geo = {"RM_StrongInsolation": [6, 8], "RM_Sunless": []}
    rows = vws.stamp_rows(sm, vws.saved_vee_tiles(raw, sm), geo)
    check(sorted(rows) == [("VEE_Cenotes", "RM_Cenotes", [5], [5]), ("VEE_MoreSolarPower", "RM_StrongInsolation",
                                                                     [6, 8], [6])],
          "stamp rows: donor tiles for a rename, geometry tiles for solar, remove = the donor's tiles")
    good_m = [(5, "RM_Cenotes"), (6, "RM_StrongInsolation"), (8, "RM_StrongInsolation"), (7, "Lakeshore")]
    good_l = [(5, "RM_Cenotes", "Karst Hollows"), (9, "Chasm", "Toxo Fracture")]
    check(vws.verify(sm, raw, good_m, good_l, geo) == [], "verify passes a stamped world")
    check(len(vws.verify(sm, raw, good_m + [(5, "VEE_Cenotes")], good_l, geo)) == 1, "verify fails a VEE entry left")
    check(len(vws.verify(sm, raw, good_m[:2] + good_m[3:], good_l, geo)) == 1, "verify fails a missing solar tile")
    check(len(vws.verify(sm, raw, good_m, [(5, "RM_Cenotes", "Renamed"), good_l[1]], geo)) == 1,
          "verify fails a landmark that lost its stored name")
    check(len(vws.verify(sm, raw, good_m, [(5, "VEE_Cenotes", "Karst Hollows"), good_l[1]], geo)) == 2,
          "verify fails a VEE landmark left")
    check(len(vws.verify(sm, raw, good_m + [(9, "RM_Cenotes")], good_l, geo)) == 1,
          "verify fails a port on a tile outside its expected set")
    ents2 = ents + [(5, hv("Lakeshore2x"))]
    vws.capture_names = lambda def_type="TileMutatorDef": {"VEE_Cenotes", "VEE_MoreSolarPower", "Lakeshore",
                                                           "Lakeshore2x"}
    raw2 = raw.replace(raw[raw.index(b"<tileMutatorDefsDeflate>"):raw.index(b"<landmarks>")],
                       b"<tileMutatorDefsDeflate>" + deflate("H", [x[1] for x in ents2]) + b"</tileMutatorDefsDeflate>"
                       b"<tileMutatorTilesDeflate>" + deflate("I", [x[0] for x in ents2]) + b"</tileMutatorTilesDeflate>")
    check(vws.verify(sm, raw2, good_m + [(5, "Lakeshore2x")], good_l, geo) == [] and
          len(vws.verify(sm, raw2, good_m, good_l, geo)) == 1,
          "verify fails a non-VEE R3 entry lost from a stamped tile")
    print("RESULT %s: %d failed" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
