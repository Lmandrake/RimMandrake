"""Build the three world-parity fix plans (U1 labels, U2 mutators, U4 river flow), offline.

Causes and numbers: `design/Jawa/worldbuilding/parity_causes_2026-10-20.md`.
Apply (bridge, dry run by default): `world/_parity_apply_2026-10-20.py`.

    python3 parity_fix_plans.py --dev <dev.rws> --canon <canon.rws> --out-dir world/

Reads two saves read-only and writes, under --out-dir:
    ASHKARR_PARITY_U1_labels_2026-10-20_plan.json
    ASHKARR_PARITY_U2_mutators_2026-10-20_plan.json
    ASHKARR_PARITY_U4_riverdist_2026-10-20_plan.json
    ASHKARR_PARITY_U4_links_mouthfirst_2026-10-20.csv   (kind,a,b,def; rivers in lay order, then roads)

U1  label size <- canonical size by name (the approved 2026-10-09 curve); label
    position <- the member tile nearest the centroid of the region's biggest piece
    (single-piece: its only piece; owner ruling 2026-10-09 for multi-piece). The
    dev positions are NOT wrong (engine frame, see feature_drawcenter_audit.py);
    this re-centres them from "the middle row of the CSV" to the region's middle.
U2  every (tile, mutator) on the dev save that the stamp's own input does not
    hold, minus KEEP_DERIVED (geography-derived defs of ours), plus the stamp
    entries that did not land, minus those a KEEP_DERIVED def replaced.
U4  a river lay order that, run through WorldGrid.OverlayRiver's rule
    (to.riverDist = max(to, from + 1), only when the link is NEW), reproduces the
    canonical riverDist on every river tile, one lay per edge.
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

PAINT = os.path.join(REPO, "world", "paint_inputs_2026-10-20")
PORT_MAP = os.path.join(REPO, "design", "RimMandrake", "retired_mutators_port_map.json")
DATE = "2026-10-20"

# Geography-derived mutators of ours that the engine assigns from the stamped
# water: RM_SeaCoast is the drop-in twin of vanilla Coast beside our seas
# (src/RimMandrake/SeaShores/Defs/TileMutatorDefs/RM_SeaCoast.xml). Measured
# 2026-10-20: all 336 dev placements border stamped water, none is water.
KEEP_DERIVED = {"RM_SeaCoast"}


# ---------------------------------------------------------------------------
# U4: river lay order
# ---------------------------------------------------------------------------
# simulate_overlay / river_lay_order live in river_lay.py (numpy-free, so w9_run.py
# can lay the same order at stamp time).
from river_lay import simulate_overlay, river_lay_order  # noqa: E402,F401


# ---------------------------------------------------------------------------
# U2: mutator diff
# ---------------------------------------------------------------------------
def mutator_diff(dev_entries, stamp_entries, keep=KEEP_DERIVED):
    """dev_entries/stamp_entries: iterables of (tile, defName).
    Returns (remove, restore, kept, superseded):
      remove     - on dev, not in the stamp, def not in keep
      restore    - in the stamp, not on dev, and no keep-def took the tile's slot
      kept       - on dev, not in the stamp, def in keep
      superseded - in the stamp, not on dev, but the tile carries a keep-def now."""
    dev = set(dev_entries)
    stamp = set(stamp_entries)
    extra = dev - stamp
    kept = sorted(e for e in extra if e[1] in keep)
    remove = sorted(e for e in extra if e[1] not in keep)
    keep_tiles = set(t for t, _ in kept)
    missing = stamp - dev
    superseded = sorted(e for e in missing if e[0] in keep_tiles and e[1] == "Coast")
    restore = sorted(missing - set(superseded))
    return remove, restore, kept, superseded


def read_stamp_mutators(path, port_map=None):
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        for m in (r.get("mutators") or "").split(";"):
            m = m.strip()
            if not m:
                continue
            if port_map and m in port_map:
                if port_map[m].get("drop") or not port_map[m].get("new"):
                    continue
                m = port_map[m]["new"]
            out.append((int(r["tile"]), m))
    return out


# ---------------------------------------------------------------------------
# U1: labels
# ---------------------------------------------------------------------------
def read_features(save_path):
    import xml.etree.ElementTree as ET
    import feature_drawcenter_audit as A
    root = ET.parse(save_path).getroot()
    arr = np.array(A.read_tile_feature_array(root))
    feats = []
    for li in root.find(".//world/features").iter("li"):
        dc = li.find("drawCenter")
        if dc is None:
            continue
        sz = li.find("maxDrawSizeInTiles")
        uid = int(li.find("uniqueID").text)
        feats.append({"name": li.find("name").text, "uid": uid,
                      "drawCenter": A.parse_vec3(dc.text),
                      "size": float(sz.text) if sz is not None else None,
                      "tiles": [int(t) for t in np.where(arr == uid)[0]]})
    return feats


def label_plan(dev_feats, canon_feats, geo):
    import feature_drawcenter_audit as A
    canon = {f["name"]: f for f in canon_feats}
    rows = []
    for f in dev_feats:
        comps = A.components(f["tiles"], geo)
        if not comps:
            raise SystemExit("U1: feature %r has no tiles on the save" % f["name"])
        big = comps[0]
        c = A.centroid(big, geo)
        tv = geo.vec[big]
        tile = int(big[int(np.argmax(tv @ c))])
        cur = A.raw_to_vec(f["drawCenter"])
        under = int(np.argmax(geo.vec @ cur))
        cf = canon.get(f["name"])
        rows.append({
            "name": f["name"], "uid": f["uid"], "tiles": len(f["tiles"]),
            "pieces": [len(p) for p in comps],
            "before": {"drawCenter": list(f["drawCenter"]), "size": f["size"],
                       "tileUnderLabel": under,
                       "onOwnTile": under in set(f["tiles"]),
                       "onBiggestPiece": under in set(big),
                       "arcFromBigCentroidDeg": round(A.arc_deg(c, cur), 3)},
            "after": {"centerOnTile": tile,
                      "drawCenter": [round(x, 4) for x in A.vec_to_raw(geo.vec[tile])],
                      "size": cf["size"] if cf and cf["size"] is not None else f["size"],
                      "sizeSource": ("canonical by name" if cf and cf["size"] is not None
                                     else "kept (no canonical name or size)")},
        })
    return rows


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dev", required=True)
    ap.add_argument("--canon", required=True)
    ap.add_argument("--out-dir", default=os.path.join(REPO, "world"))
    a = ap.parse_args()
    import worldgeom
    import worldmap
    import worldview
    geo = worldgeom.Geometry(21872)
    od = a.out_dir

    # U1
    rows = label_plan(read_features(a.dev), read_features(a.canon), geo)
    u1 = {"what": "U1 region labels: canonical size by name; label on the member tile nearest "
                  "the biggest piece's centroid. Apply: world/_parity_apply_%s.py u1" % DATE,
          "source": {"dev": os.path.basename(a.dev), "canon": os.path.basename(a.canon)},
          "counts": {"features": len(rows),
                     "sizeChanges": sum(1 for r in rows if r["before"]["size"] is None or r["after"]["size"] is None
                                        or abs(r["after"]["size"] - r["before"]["size"]) > 0.01),
                     "beforeOffOwnTile": sum(1 for r in rows if not r["before"]["onOwnTile"]),
                     "beforeOffBiggestPiece": sum(1 for r in rows if not r["before"]["onBiggestPiece"])},
          "features": rows}
    json.dump(u1, open(os.path.join(od, "ASHKARR_PARITY_U1_labels_%s_plan.json" % DATE), "w"), indent=1)

    # U2
    byh, _ = worldmap.load_hash_table("TileMutatorDef")
    g = worldmap.WorldGrid(a.dev)
    ents = g.mutator_entries()
    unres = [h for _, h in ents if h not in byh]
    if unres:
        raise SystemExit("U2: %d dev mutator entries have no def in the dump -- refusing" % len(unres))
    dev_named = [(int(t), byh[h]) for t, h in ents]
    pm = json.load(open(PORT_MAP, encoding="utf-8"))["TileMutatorDef"]
    stamp = read_stamp_mutators(os.path.join(PAINT, "ASHKARR_WORLDMAP_mutators.csv"), pm)
    remove, restore, kept, superseded = mutator_diff(dev_named, stamp)
    canon_defs = set()
    gc = worldmap.WorldGrid(a.canon)
    for _, h in gc.mutator_entries():
        if h in byh:
            canon_defs.add(byh[h])

    def group(es):
        out = defaultdict(list)
        for t, m in es:
            out[m].append(t)
        return {m: sorted(ts) for m, ts in sorted(out.items())}
    u2 = {"what": "U2 tile mutators: strip the engine-rolled entries the stamp never wrote; "
                  "re-add stamp entries that did not land. Apply: world/_parity_apply_%s.py u2" % DATE,
          "counts": {"devEntries": len(dev_named), "stampEntries": len(set(stamp)),
                     "remove": len(remove), "restore": len(restore), "keptDerived": len(kept),
                     "supersededByKept": len(superseded),
                     "removeDefs": len(set(m for _, m in remove)),
                     "removeDefsNeverOnCanon": sorted(set(m for _, m in remove) - canon_defs),
                     "removeOurPrefix": dict(Counter(m for _, m in remove
                                                     if m.startswith(("RM_", "RSW_", "RUT_"))))},
          "removePerDef": dict(Counter(m for _, m in remove).most_common()),
          "keepDerived": sorted(KEEP_DERIVED),
          "remove": group(remove), "restore": group(restore),
          "kept": group(kept), "superseded": group(superseded)}
    json.dump(u2, open(os.path.join(od, "ASHKARR_PARITY_U2_mutators_%s_plan.json" % DATE), "w"), indent=1)

    # U4
    pv_c = worldview.PlanetView(a.canon)
    pv_d = worldview.PlanetView(a.dev)
    C = worldview.read_river_distances(pv_c.grid)
    D = worldview.read_river_distances(pv_d.grid)
    if C is None or D is None:
        raise SystemExit("U4: a save has no tileRiverDistancesDeflate block")
    ec = {tuple(sorted((o, n))): dfn for o, n, dfn, _ in pv_c.rivers}
    ed = {tuple(sorted((o, n))): dfn for o, n, dfn, _ in pv_d.rivers}
    if ec != ed:
        raise SystemExit("U4: river edge sets/defs differ between saves -- the plan assumes same geometry")
    order, mism = river_lay_order(list(ed), C)
    if mism:
        raise SystemExit("U4: lay order cannot reproduce canonical riverDist on %d tiles: %s" % (len(mism), mism[:5]))
    rtiles = sorted(set(t for e in ed for t in e))
    rset = set(rtiles)
    links_out = os.path.join(od, "ASHKARR_PARITY_U4_links_mouthfirst_%s.csv" % DATE)
    roads = [r for r in csv.DictReader(open(os.path.join(PAINT, "ASHKARR_WORLDMAP_links.csv"), encoding="utf-8"))
             if r["kind"] == "road"]
    with open(links_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["kind", "a", "b", "def"])
        for x, y in order:
            w.writerow(["river", x, y, ed[tuple(sorted((x, y)))]])
        for r in roads:
            w.writerow(["road", r["a"], r["b"], r["def"]])
    u4 = {"what": "U4 river flow: re-lay rivers mouth-first so riverDist equals the canonical "
                  "world on every river tile. Same edges, same defs. Apply: "
                  "world/_parity_apply_%s.py u4 (world_links_import clearFirst)" % DATE,
          "linksCsv": os.path.basename(links_out),
          "counts": {"riverEdges": len(ed), "riverTiles": len(rtiles), "roads": len(roads),
                     "tilesChanging": sum(1 for t in rtiles if C[t] != D[t]),
                     "canonMaxOnRivers": max(C[t] for t in rtiles),
                     "devMaxOnRivers": max(D[t] for t in rtiles),
                     "canonOffRiverNonzero": sum(1 for t in range(len(C)) if C[t] and t not in rset)},
          "before": {str(t): D[t] for t in rtiles},
          "after": {str(t): C[t] for t in rtiles}}
    json.dump(u4, open(os.path.join(od, "ASHKARR_PARITY_U4_riverdist_%s_plan.json" % DATE), "w"), indent=1)
    print("U1 features %(features)d sizeChanges %(sizeChanges)d offOwnTile %(beforeOffOwnTile)d "
          "offBiggestPiece %(beforeOffBiggestPiece)d" % u1["counts"])
    print("U2 remove %(remove)d (%(removeDefs)d defs) restore %(restore)d kept %(keptDerived)d "
          "superseded %(supersededByKept)d" % u2["counts"])
    print("U4 river tiles %(riverTiles)d changing %(tilesChanging)d canon max %(canonMaxOnRivers)d "
          "dev max %(devMaxOnRivers)d" % u4["counts"])


if __name__ == "__main__":
    main()
