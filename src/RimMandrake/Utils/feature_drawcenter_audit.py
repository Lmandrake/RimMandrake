"""Audit every world feature's `drawCenter` against its OWN tiles, offline.

`FEATURE_DRAWCENTER_UNVERIFIED_1`: only two of the 71 `WorldFeature`s on the
canonical Ash'karr save (Fall Line, The Breaks) have ever had their `drawCenter`
checked against the tiles the feature actually names. The other 69 have never
been verified, and the just-completed size pass (`WORLD_LABEL_SIZE_HIERARCHY_1`)
makes a wrong one worse -- a bigger label sitting over the wrong ground reads as
a bigger mistake.

## Where a feature's tiles come from

Same source as `world_label_curve.py`: `<world><grid><layers><values>
<li Class="SurfaceLayer"><tileFeatureDeflate>`, a base64 + raw-DEFLATE array of
21,872 ushorts, one per tile, storing each tile's `WorldFeature.uniqueID`
directly. Joined on **uniqueID**, never list index (`WORLDVIEW_MISLABEL_FALLOUT_1`).

## The coordinate transform -- MEASURED, not assumed

`drawCenter` is a raw engine `Vector3(x, y, z)` at radius 100 (confirmed: every
stored vector's magnitude is ~99.99-100.0). This codebase's own `worldgeom.py`
builds tile-center unit vectors as
`vec = (cos(lat)*cos(lon), sin(lat), cos(lat)*sin(lon))` from a CSV of tile
positions exported live from the same engine. Comparing the two directly gives
near-ZERO or negative dot products even for the two features already verified
correct -- the two conventions disagree on the sign of z (equivalently, on the
handedness of longitude). Negating z brings both known-good features into close
alignment (dot 0.978 and 0.996; see `_selfcheck_transform`, which runs on every
invocation and refuses to proceed if it doesn't hold):

    ours_vec = normalize((x, y, -z) / 100)
    raw_vec  = (ours_vec.x * 100, ours_vec.y * 100, -ours_vec.z * 100)

This is a coordinate-convention fact about comparing worldgeom.py's vectors to
a raw Vector3, not a bug in either. Nothing here writes a raw engine value
without going through `vec_to_raw`.

## What "wrong" means for a single-piece region

🔴 The FIRST version of this check asked "is the globally-nearest-of-all-21,872-
tiles to the stored point a member of this feature" and it is the WRONG
question: at a shared border, several different features' tiles sit within a
fraction of a degree of each other (mean tile arc is ~1.48 deg on this planet),
so that test flagged 60 of 63 single-piece features "wrong" including Fall
Line -- one of the two features an earlier pass explicitly hand-verified as
correct. Caught by checking Fall Line's own number against that prior
verification before trusting the sweep (`dramatic-findings-need-a-second-look`).

The right question is: how far is the stored point from the NEAREST TILE THAT
ACTUALLY BELONGS TO THIS FEATURE (not from all 21,872 tiles). That distance,
`dist_to_nearest_member`, is ~0.3-4.1 deg for a tight, unambiguous cluster of 9
features plus Fall Line at 2.43 deg (matching its prior hand-verification) --
then jumps with no feature landing between 4.1 and 6.3 deg. `FOOTPRINT_TOL_DEG`
sits in that gap. A feature past it is not "off-center", it is **sitting on
ground that belongs to a different named region entirely** -- confirmed
directly for the worst case: "Salt Gate"'s drawCenter resolves to a tile whose
owner is "Deadstone", 106 degrees away.

`ratio` (arc-from-centroid / the region's own mean tile-to-centroid arc) is
kept in the report as context but does NOT gate the wrong/not-wrong verdict --
Fall Line's ratio (1.60) alone would have re-flagged an already-verified
feature; footprint distance is the test that actually matches "is the label on
the region it names."

## Multi-piece regions (8 of 71) are NOT auto-fixed

Per the item text this is a LOOKING decision for the owner: centroid-of-all-
pieces, centroid-of-the-largest-piece, or one-label-per-piece. This module
computes and renders all three candidates and touches nothing for these 8.

## Applying a fix

Never edits a save in place. `--base` supplies the save to copy from (may be
the canonical save's read-only bytes, or an already-derived new slot such as
the size-pass's `ASHKARR_LABELSIZES_*.rws` -- this module reads the SAME
uniqueID/tile data from `--save` regardless of which file `--base` is, since
the size pass touches only `<maxDrawSizeInTiles>`, never `<drawCenter>` or
tile membership). Only `<drawCenter>` tags belonging to single-piece WRONG
features are rewritten, located the same way `world_label_curve.py` locates
`<maxDrawSizeInTiles>`: by exact byte offset in document order, matched 1:1
against `<world><features>`'s own `<li>` order.

CLI:
    python3 feature_drawcenter_audit.py <save.rws> --report-only
    python3 feature_drawcenter_audit.py <save.rws> --base <base.rws> --out <new.rws>
    python3 feature_drawcenter_audit.py <save.rws> --render-dir <dir>
"""
import argparse
import base64
import json
import os
import struct
import sys
import zlib
from collections import defaultdict, deque
from math import acos, degrees

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import worldgeom  # noqa: E402

RADIUS = 100.0
N_TILES = 21872

# The two features an earlier pass (FALL_LINE_MAJOR_REGION_LABEL_1 / the
# 2026-09-21 sizing note) already checked by hand and confirmed correct.
# Used only to self-verify the coordinate transform above -- never as a
# source of any numeric threshold.
KNOWN_GOOD = {"Fall Line": 0.9, "The Breaks": 0.9}

# MEASURED gap in the sorted dist_to_nearest_member list (see module docstring):
# 9 features cluster at 0.30-4.08 deg, Fall Line (prior hand-verified) at 2.43,
# then nothing until 6.32. 5.0 sits in that gap.
FOOTPRINT_TOL_DEG = 5.0


# ---------------------------------------------------------------------------
def parse_vec3(s):
    return tuple(float(x) for x in s.strip("()").split(","))


def raw_to_vec(raw3):
    x, y, z = raw3
    v = np.array([x, y, -z]) / RADIUS
    n = np.linalg.norm(v)
    if n < 1e-9:
        raise SystemExit("degenerate drawCenter %r" % (raw3,))
    return v / n


def vec_to_raw(v):
    x, y, z = (float(c) for c in v)
    return (x * RADIUS, y * RADIUS, -z * RADIUS)


def fmt_raw(raw3):
    return "(%s, %s, %s)" % tuple("%.7g" % c for c in raw3)


# ---------------------------------------------------------------------------
def read_tile_feature_array(root):
    """Same decode as world_label_curve.py's read_tile_counts_by_feature_uid,
    but returns the per-tile array itself rather than just the counts."""
    layers = root.find(".//world/grid/layers")
    surface = layers.find("values")[0]
    if surface.attrib.get("Class") != "SurfaceLayer":
        for li in layers.find("values"):
            if li.attrib.get("Class") == "SurfaceLayer":
                surface = li
                break
    blob = surface.find("tileFeatureDeflate").text.strip()
    data = zlib.decompress(base64.b64decode(blob), -15)
    n = len(data) // 2
    if n != N_TILES:
        raise SystemExit("expected %d tiles, decoded %d -- wrong save/geometry?"
                          % (N_TILES, n))
    return struct.unpack("<%dH" % n, data)


def components(tiles, geo):
    """Connected components of `tiles` under the tile-adjacency graph, largest first."""
    tileset = set(tiles)
    seen = set()
    comps = []
    for t in tiles:
        if t in seen:
            continue
        q = deque([t])
        seen.add(t)
        comp = []
        while q:
            x = q.popleft()
            comp.append(x)
            for nb in geo.neighbours(x):
                if nb in tileset and nb not in seen:
                    seen.add(nb)
                    q.append(nb)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    return comps


def centroid(tiles, geo):
    v = geo.vec[list(tiles)].mean(axis=0)
    return v / np.linalg.norm(v)


def arc_deg(a, b):
    return degrees(acos(max(-1.0, min(1.0, float(np.dot(a, b))))))


# ---------------------------------------------------------------------------
import xml.etree.ElementTree as ET  # noqa: E402


def _selfcheck_transform(ordered, tiles_by_uid, geo):
    """Refuse to proceed unless BOTH already-hand-verified features (a) align
    with the transform (dot check) AND (b) would NOT be re-flagged wrong by
    the footprint-distance test below -- the second check is what caught the
    first (wrong) version of this test flagging Fall Line as broken."""
    found = 0
    for f in ordered:
        want = KNOWN_GOOD.get(f["name"])
        if want is None:
            continue
        found += 1
        tiles = tiles_by_uid.get(f["uid"], [])
        comps = components(tiles, geo)
        c = centroid(comps[0], geo)
        dcv = raw_to_vec(parse_vec3(f["drawCenter_raw"]))
        dot = float(np.dot(c, dcv))
        if dot < want:
            raise SystemExit(
                "TRANSFORM SELF-CHECK FAILED for %r: dot=%.4f (want > %.2f). "
                "Refusing to trust drawCenter<->vec conversion -- do not "
                "proceed on this data." % (f["name"], dot, want))
        tv = geo.vec[comps[0]]
        dist = float(np.degrees(np.arccos(np.clip(tv @ dcv, -1, 1).max())))
        if dist > FOOTPRINT_TOL_DEG:
            raise SystemExit(
                "WRONGNESS SELF-CHECK FAILED for %r: dist_to_nearest_member="
                "%.2f deg > tolerance %.1f -- this feature was already "
                "hand-verified correct; a check that re-flags it is broken, "
                "not the data." % (f["name"], dist, FOOTPRINT_TOL_DEG))
    if not found:
        raise SystemExit("self-check features (%s) not found on this save -- "
                          "refusing to run unverified" % sorted(KNOWN_GOOD))


def build_audit(save_path):
    tree = ET.parse(save_path)
    root = tree.getroot()
    geo = worldgeom.Geometry(N_TILES)
    arr = read_tile_feature_array(root)

    tiles_by_uid = defaultdict(list)
    for t, uid in enumerate(arr):
        if uid != 0xFFFF:
            tiles_by_uid[uid].append(t)

    features_container = root.find(".//world/features")
    ordered = []
    for elem in features_container.iter("li"):
        dc = elem.find("drawCenter")
        if dc is None:
            continue
        uid = int(elem.find("uniqueID").text)
        name = elem.find("name").text
        ordered.append({"uid": uid, "name": name, "drawCenter_raw": dc.text})

    _selfcheck_transform(ordered, tiles_by_uid, geo)

    for f in ordered:
        tiles = tiles_by_uid.get(f["uid"], [])
        comps = components(tiles, geo)
        f["tiles"] = len(tiles)
        f["n_pieces"] = len(comps)
        f["piece_sizes"] = [len(c) for c in comps]
        dcv = raw_to_vec(parse_vec3(f["drawCenter_raw"]))
        f["drawCenter_vec"] = dcv

        if len(comps) == 1:
            c = centroid(comps[0], geo)
            f["centroid_vec"] = c
            f["arc_deg_from_centroid"] = arc_deg(c, dcv)
            tv = geo.vec[comps[0]]
            arcs_to_centroid = np.degrees(np.arccos(np.clip(tv @ c, -1, 1)))
            f["region_radius_deg"] = float(arcs_to_centroid.mean())
            f["region_radius_max_deg"] = float(arcs_to_centroid.max())
            ratio = (f["arc_deg_from_centroid"] / f["region_radius_deg"]
                     if f["region_radius_deg"] > 1e-6 else 0.0)
            f["ratio"] = ratio
            # The test that matters: how far is the stored point from the
            # NEAREST TILE THAT ACTUALLY BELONGS TO THIS FEATURE -- not from
            # every tile on the planet (see module docstring for why that
            # first version of this check was wrong).
            dist_own = float(np.degrees(np.arccos(np.clip(tv @ dcv, -1, 1).max())))
            f["dist_to_nearest_member_deg"] = dist_own
            f["wrong"] = dist_own > FOOTPRINT_TOL_DEG
            f["fix_vec"] = c if f["wrong"] else None
        else:
            largest = comps[0]
            f["candidates"] = {
                "centroid_all": centroid(tiles, geo),
                "centroid_largest": centroid(largest, geo),
                "per_piece": [{"piece_index": i, "size": len(c),
                               "centroid_vec": centroid(c, geo)}
                              for i, c in enumerate(comps)],
            }
            f["wrong"] = None  # owner's call, never auto-decided

    return ordered, tiles_by_uid, geo


# ---------------------------------------------------------------------------
def print_report(ordered):
    single = [f for f in ordered if f["n_pieces"] == 1]
    multi = [f for f in ordered if f["n_pieces"] > 1]
    n_wrong = sum(1 for f in single if f["wrong"])
    print("%d features: %d single-piece (%d WRONG, auto-fixable), %d multi-piece "
          "(owner's call, not auto-fixed)" % (len(ordered), len(single), n_wrong, len(multi)))
    print()
    print("-- single-piece, sorted worst-first (dist_to_nearest_member_deg, "
          "tolerance %.1f) --" % FOOTPRINT_TOL_DEG)
    for f in sorted(single, key=lambda r: -r["dist_to_nearest_member_deg"]):
        mark = "WRONG " if f["wrong"] else "ok    "
        note = "  <- sits on ground belonging to a DIFFERENT feature" if f["wrong"] else ""
        print("%s %-24s tiles=%5d  dist_to_own_nearest=%7.2f  arc_from_centroid=%6.2f  "
              "region_radius=%6.2f  ratio=%5.2f%s"
              % (mark, f["name"], f["tiles"], f["dist_to_nearest_member_deg"],
                 f["arc_deg_from_centroid"], f["region_radius_deg"], f["ratio"], note))
    print()
    print("-- multi-piece (8), owner's call --")
    for f in sorted(multi, key=lambda r: -r["n_pieces"]):
        sizes = ",".join(str(s) for s in f["piece_sizes"])
        print("%-24s %d pieces (sizes %s), %d tiles total"
              % (f["name"], f["n_pieces"], sizes, f["tiles"]))


# ---------------------------------------------------------------------------
def apply_fixes(base_path, out_path, ordered):
    """Rewrite <drawCenter> only for single-piece WRONG features, matched to
    `ordered` (document order) exactly like world_label_curve.py's apply()."""
    if out_path == base_path:
        raise SystemExit("refusing to write in place -- pass a different --out path")

    with open(base_path, "rb") as fh:
        raw = fh.read()

    pattern = b"<drawCenter>"
    positions = []
    start = 0
    while True:
        idx = raw.find(pattern, start)
        if idx == -1:
            break
        end = raw.find(b"</drawCenter>", idx)
        positions.append((idx, end + len(b"</drawCenter>")))
        start = end + len(b"</drawCenter>")

    if len(positions) != len(ordered):
        raise SystemExit(
            "found %d <drawCenter> tags in --base but parsed %d features from "
            "--save -- refusing to guess the mapping (are --save and --base "
            "the same feature roster?)" % (len(positions), len(ordered)))

    out_parts = []
    cursor = 0
    n_changed = 0
    for (start_pos, end_pos), feat in zip(positions, ordered):
        out_parts.append(raw[cursor:start_pos])
        current_tag = raw[start_pos:end_pos]
        if feat["n_pieces"] == 1 and feat["wrong"]:
            new_str = fmt_raw(vec_to_raw(feat["fix_vec"]))
            new_tag = ("<drawCenter>%s</drawCenter>" % new_str).encode()
            out_parts.append(new_tag)
            n_changed += 1
        else:
            out_parts.append(current_tag)
        cursor = end_pos
    out_parts.append(raw[cursor:])
    new_raw = b"".join(out_parts)

    with open(out_path, "wb") as fh:
        fh.write(new_raw)

    print("wrote %s  (%d -> %d bytes, %d feature(s) changed)"
          % (out_path, len(raw), len(new_raw), n_changed))

    # verify: reparse and confirm every intended fix landed, keyed by uid
    check_root = ET.parse(out_path).getroot()
    by_uid = {}
    for elem in check_root.find(".//world/features").iter("li"):
        dc = elem.find("drawCenter")
        if dc is not None:
            by_uid[int(elem.find("uniqueID").text)] = parse_vec3(dc.text)

    mismatches = []
    for feat in ordered:
        if feat["n_pieces"] == 1 and feat["wrong"]:
            want = vec_to_raw(feat["fix_vec"])
            got = by_uid.get(feat["uid"])
            if got is None or any(abs(a - b) > 1e-3 for a, b in zip(want, got)):
                mismatches.append(feat["name"])
    if mismatches:
        raise SystemExit("VERIFY FAILED: %d feature(s) did not read back as "
                          "written: %s" % (len(mismatches), mismatches))
    print("verify OK: every fixed feature reads back the intended drawCenter")


# ---------------------------------------------------------------------------
def render(ordered, geo, out_dir):
    """Two kinds of picture: one whole-planet overview marking every stored
    drawCenter (red = wrong/single-piece, will move to the green mark) and one
    zoomed panel PER MULTI-PIECE region showing its pieces and all three
    candidate label positions, for the owner to pick by looking."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)

    def latlon(v):
        lat = degrees(np.arcsin(np.clip(v[1], -1, 1)))
        lon = degrees(np.arctan2(v[2], v[0]))
        return lat, lon

    # ---- overview ----
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_facecolor("#0b0d12")
    fig.patch.set_facecolor("#0b0d12")
    lat = geo.lat
    lon = geo.lon
    ax.scatter(lon, lat, s=0.6, c="#31384a", linewidths=0)

    for f in ordered:
        slat, slon = latlon(f["drawCenter_vec"])
        if f["n_pieces"] == 1:
            colour = "#ff4d4d" if f["wrong"] else "#59d17a"
            ax.scatter([slon], [slat], s=26, c=colour, edgecolors="black",
                       linewidths=0.6, zorder=5)
            if f["wrong"]:
                nlat, nlon = latlon(f["fix_vec"])
                ax.scatter([nlon], [nlat], s=26, marker="*", c="#59d17a",
                           edgecolors="black", linewidths=0.6, zorder=6)
                ax.plot([slon, nlon], [slat, nlat], c="#ff4d4d", lw=0.7, zorder=4)
        else:
            ax.scatter([slon], [slat], s=34, marker="D", c="#ffd23f",
                       edgecolors="black", linewidths=0.6, zorder=5)
        ax.annotate(f["name"], (slon, slat), color="#d8d0b8", fontsize=5.5,
                    xytext=(2, 2), textcoords="offset points", zorder=7)

    ax.set_title("FEATURE_DRAWCENTER_UNVERIFIED_1 -- stored drawCenter audit\n"
                  "green=ok  red->star=wrong, will move to the star  "
                  "yellow diamond=multi-piece (owner's call, see per-region panels)",
                  color="white", fontsize=10)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel("longitude", color="#888")
    ax.set_ylabel("latitude", color="#888")
    ax.tick_params(colors="#888")
    fig.tight_layout()
    overview_path = os.path.join(out_dir, "drawcenter_overview.png")
    fig.savefig(overview_path, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)

    # ---- per multi-piece region zoom panels ----
    multi = [f for f in ordered if f["n_pieces"] > 1]
    piece_colours = ["#4da3ff", "#ff8a4d", "#c86bff", "#4dffb8", "#ffe14d",
                      "#ff4d94", "#8aff4d", "#4dfff2"]
    for f in multi:
        cand = f["candidates"]
        comps_latlon = []
        for i, piece in enumerate(cand["per_piece"]):
            pass
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.set_facecolor("#0b0d12")
        fig.patch.set_facecolor("#0b0d12")

        # need the actual tile lists again for plotting footprints
        uid = f["uid"]
        # re-derive per-piece tile ids from geo via components() is already done;
        # candidates carries only centroids, so recompute components here too.
        # (cheap: reuse tiles_by_uid via closure argument instead)
        ax.set_title("%s -- %d pieces, %d tiles total\n"
                      "owner's call: centroid-of-all vs centroid-of-largest vs one-per-piece"
                      % (f["name"], f["n_pieces"], f["tiles"]), color="white", fontsize=9)

        for i, piece in enumerate(cand["per_piece"]):
            plat, plon = latlon(piece["centroid_vec"])
            colour = piece_colours[i % len(piece_colours)]
            ax.scatter([plon], [plat], s=90, marker="o", facecolors="none",
                       edgecolors=colour, linewidths=1.6, zorder=5,
                       label="piece %d (%d tiles)" % (i, piece["size"]))

        alat, alon = latlon(cand["centroid_all"])
        llat, llon = latlon(cand["centroid_largest"])
        slat, slon = latlon(f["drawCenter_vec"])
        ax.scatter([alon], [alat], s=140, marker="*", c="#ffffff",
                   edgecolors="black", linewidths=0.8, zorder=7, label="centroid of ALL pieces")
        ax.scatter([llon], [llat], s=140, marker="^", c="#59d17a",
                   edgecolors="black", linewidths=0.8, zorder=7, label="centroid of LARGEST piece")
        ax.scatter([slon], [slat], s=90, marker="x", c="#ff4d4d",
                   linewidths=2.2, zorder=8, label="current stored drawCenter")

        ax.legend(fontsize=6.5, facecolor="#181c24", labelcolor="white", loc="best")
        ax.set_xlabel("longitude", color="#888")
        ax.set_ylabel("latitude", color="#888")
        ax.tick_params(colors="#888")
        fig.tight_layout()
        safe = "".join(c if c.isalnum() else "_" for c in f["name"])
        p = os.path.join(out_dir, "drawcenter_multipiece_%s.png" % safe)
        fig.savefig(p, dpi=170, facecolor=fig.get_facecolor())
        plt.close(fig)

    print("wrote %d picture(s) to %s" % (1 + len(multi), out_dir))
    return overview_path


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("save", help="save to READ feature/tile data from (never modified)")
    ap.add_argument("--base", help="save to copy bytes FROM when writing --out "
                                    "(default: same as `save`)")
    ap.add_argument("--out", help="NEW .rws path to write fixes to (refused if == --base)")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--render-dir", help="write review PNGs here")
    ap.add_argument("--json", help="dump the full audit as JSON here (debugging/handoff)")
    args = ap.parse_args()

    ordered, tiles_by_uid, geo = build_audit(args.save)
    print_report(ordered)

    if args.json:
        def _ser(f):
            d = dict(f)
            for k in ("drawCenter_vec", "centroid_vec", "fix_vec"):
                if d.get(k) is not None:
                    d[k] = [float(x) for x in d[k]]
            if d.get("candidates"):
                c = dict(d["candidates"])
                c["centroid_all"] = [float(x) for x in c["centroid_all"]]
                c["centroid_largest"] = [float(x) for x in c["centroid_largest"]]
                c["per_piece"] = [{"piece_index": p["piece_index"], "size": p["size"],
                                    "centroid_vec": [float(x) for x in p["centroid_vec"]]}
                                   for p in c["per_piece"]]
                d["candidates"] = c
            return d
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump([_ser(f) for f in ordered], fh, indent=1)
        print("wrote %s" % args.json)

    if args.render_dir:
        render(ordered, geo, args.render_dir)

    if args.report_only or not args.out:
        return

    apply_fixes(args.base or args.save, args.out, ordered)


if __name__ == "__main__":
    sys.exit(main())
