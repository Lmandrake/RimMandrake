"""Size every world feature's label from a CURVE on its tile count, offline.

`WORLD_LABEL_SIZE_HIERARCHY_1`: on the canonical Ash'karr save all 71
`WorldFeature`s sit at `maxDrawSizeInTiles = 10`, the floor of the engine's own
`EffectiveDrawSizeCurve` (`RimWorld/Planet/WorldFeature.cs`:
`10 -> 15   25 -> 40   50 -> 90   100 -> 150   200 -> 200`), so a 1,692-tile sea
letters exactly as large as a 16-tile pocket. This module derives a size PER
FEATURE from its tile count, so a feature authored later gets a sensible size
automatically -- no hand-typed table.

## Where a feature's tile count comes from

`WorldFeature.Tiles` is a runtime property (`worldGrid[i].feature == this`),
not a stored per-feature field. What IS on disk is the tile-to-feature map
itself: `<world><grid><layers><values><li Class="SurfaceLayer">` carries
`<tileFeatureDeflate>`, a base64 + raw-DEFLATE array of **2-byte tile-count
elements**, one per tile (21,872 for Ash'karr; MEASURED, matches the surface
layer's other per-tile grids exactly). Unlike the terrain/roof grids this is
NOT a defName shortHash -- it stores the `WorldFeature.uniqueID` DIRECTLY, and
that was verified here, not assumed: every one of the 71 distinct values in
the decoded array is exactly one of the 71 `<uniqueID>` values under
`<world><features>`, with zero left over on either side, and the counts sum to
exactly the tile total.

## The curve

`maxDrawSizeInTiles = round(max(FLOOR, sqrt(tileCount) * K))`

`K = 1.35` is not invented here -- it is this codebase's own already-vetted
vanilla-equivalent multiplier (`WORLD_FEATURE_LABELS_OVERSIZED_1`, closed
2026-09-10): vanilla's `FeatureWorker.AssignBestDrawPos` sets
`maxDrawSizeInTiles = bestTileDist * 2.4` from a region's inradius; treating a
region of A tiles as a disk of that area gives `bestTileDist ~= sqrt(A/pi)`, so
`2.4 * sqrt(A/pi) == 1.354 * sqrt(A)`. `FLOOR = 10.0` is the engine curve's own
first knot and today's uniform baseline -- nothing SHRINKS below what every
label already draws at; only genuinely large regions grow past it.

## The Fall Line is a documented exception, not a curve output

`FALL_LINE_MAJOR_REGION_LABEL_1` promoted the Fall Line (155 tiles) to 26 on
the owner's explicit "major world region" instruction -- its own spec calls
this "a deliberate PROMOTION, not a computed size" specifically because the
curve gives it only ~17 (38th of 71 by area, unremarkable). This module keeps
that promotion verbatim (`FALL_LINE_OVERRIDE`) rather than resetting it down to
the curve's own number, and every other feature is generic curve output.

## Applying it

Never edits a save in place. Pass `--out` to a NEW slot; the source is opened
"rb", the destination "wb" -- text mode would silently collapse CRLF and
corrupt the file (skill: rimworld-savegame). Only `<maxDrawSizeInTiles>` tags
that actually change are touched, located by exact byte offset in DOCUMENT
ORDER (matched 1:1 against `<world><features>`'s own `<li>` order) so the edit
cannot land on the wrong feature's tag even though every source tag currently
reads the same literal "10".

CLI:
    python3 world_label_curve.py <save.rws> --out <new.rws>   apply
    python3 world_label_curve.py <save.rws> --report-only     just print the table
"""
import argparse
import base64
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
from collections import Counter
from math import sqrt

FLOOR = 10.0
K = 1.35
FALL_LINE_NAME = "Fall Line"
FALL_LINE_OVERRIDE = 26


def curve(tile_count: int) -> int:
    return round(max(FLOOR, sqrt(tile_count) * K))


def read_tile_counts_by_feature_uid(root: ET.Element) -> Counter:
    """Decode the surface layer's tileFeatureDeflate: uniqueID -> tile count."""
    layers = root.find(".//world/grid/layers")
    surface = layers.find("values")[0]
    if surface.attrib.get("Class") != "SurfaceLayer":
        # defensive: find the SurfaceLayer explicitly if layer order ever changes
        for li in layers.find("values"):
            if li.attrib.get("Class") == "SurfaceLayer":
                surface = li
                break
    blob = surface.find("tileFeatureDeflate").text.strip()
    data = zlib.decompress(base64.b64decode(blob), -15)
    n = len(data) // 2
    arr = struct.unpack(f"<{n}H", data)
    return Counter(arr)


def build_plan(save_path: str):
    """Return (ordered_feats, root) where ordered_feats is a list of dicts in
    DOCUMENT ORDER, each {uid, name, current(str), tiles, new(int)}."""
    tree = ET.parse(save_path)
    root = tree.getroot()

    tile_counts = read_tile_counts_by_feature_uid(root)

    features_container = root.find(".//world/features")
    ordered = []
    for elem in features_container.iter("li"):
        md = elem.find("maxDrawSizeInTiles")
        if md is None:
            continue
        uid = int(elem.find("uniqueID").text)
        name = elem.find("name").text
        ordered.append({
            "uid": uid,
            "name": name,
            "current": md.text,
            "tiles": tile_counts.get(uid, 0),
        })

    for f in ordered:
        if f["name"] == FALL_LINE_NAME:
            f["new"] = FALL_LINE_OVERRIDE
            f["exception"] = True
        else:
            f["new"] = curve(f["tiles"])
            f["exception"] = False

    return ordered, root


def print_table(ordered):
    changed = sum(1 for f in ordered if str(f["new"]) != f["current"])
    print(f"{len(ordered)} features, {changed} would change, "
          f"floor={FLOOR} K={K}")
    for f in sorted(ordered, key=lambda r: r["tiles"]):
        tag = "  <- Fall Line exception (owner promotion)" if f["exception"] else ""
        arrow = "->" if str(f["new"]) != f["current"] else "=="
        print(f"{f['tiles']:>6}  {f['name']:<24} {f['current']:>4} {arrow} {f['new']:>4}{tag}")


def apply(save_path: str, out_path: str, ordered):
    if out_path == save_path:
        raise SystemExit("refusing to write in place -- pass a different --out path")

    with open(save_path, "rb") as fh:
        raw = fh.read()

    pattern = b"<maxDrawSizeInTiles>"
    # Locate every <maxDrawSizeInTiles>VALUE</maxDrawSizeInTiles> occurrence in
    # document order and match 1:1 against `ordered` (same document-order walk).
    positions = []
    start = 0
    while True:
        idx = raw.find(pattern, start)
        if idx == -1:
            break
        end = raw.find(b"</maxDrawSizeInTiles>", idx)
        positions.append((idx, end + len(b"</maxDrawSizeInTiles>")))
        start = end + len(b"</maxDrawSizeInTiles>")

    if len(positions) != len(ordered):
        raise SystemExit(
            f"found {len(positions)} <maxDrawSizeInTiles> tags but parsed "
            f"{len(ordered)} features -- refusing to guess the mapping")

    out_parts = []
    cursor = 0
    n_changed = 0
    for (start_pos, end_pos), feat in zip(positions, ordered):
        out_parts.append(raw[cursor:start_pos])
        current_tag = raw[start_pos:end_pos]
        if str(feat["new"]) != feat["current"]:
            new_tag = f"<maxDrawSizeInTiles>{feat['new']}</maxDrawSizeInTiles>".encode()
            out_parts.append(new_tag)
            n_changed += 1
        else:
            out_parts.append(current_tag)
        cursor = end_pos
    out_parts.append(raw[cursor:])
    new_raw = b"".join(out_parts)

    with open(out_path, "wb") as fh:
        fh.write(new_raw)

    print(f"wrote {out_path}  ({len(raw)} -> {len(new_raw)} bytes, "
          f"{n_changed} feature(s) changed)")

    # verify: reparse the output and confirm every intended value landed
    check_tree = ET.parse(out_path)
    check_root = check_tree.getroot()
    features_container = check_root.find(".//world/features")
    by_name = {}
    for elem in features_container.iter("li"):
        md = elem.find("maxDrawSizeInTiles")
        if md is not None:
            by_name[elem.find("name").text] = float(md.text)
    mismatches = [f for f in ordered if by_name.get(f["name"]) != float(f["new"])]
    if mismatches:
        raise SystemExit(f"VERIFY FAILED: {len(mismatches)} feature(s) did not "
                          f"read back as written: {[f['name'] for f in mismatches]}")
    print("verify OK: every feature reads back the intended value")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("save", help="source .rws (never modified)")
    ap.add_argument("--out", help="NEW .rws path to write (refused if == save)")
    ap.add_argument("--report-only", action="store_true",
                     help="print the before/after table and exit; write nothing")
    args = ap.parse_args()

    ordered, _root = build_plan(args.save)
    print_table(ordered)

    if args.report_only or not args.out:
        return

    apply(args.save, args.out, ordered)


if __name__ == "__main__":
    sys.exit(main())
