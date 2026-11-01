#!/usr/bin/env python3
"""twitch_rig_preview.py — draw a Spastic render tree offline, on all four facings, at rest.

Same geometry as the engine (PawnRenderTree.ComputeMatrix): M = T(offset) T(pivot) R S T(-pivot), with
pivot = -(drawData.pivot - 0.5) and the Spastic mesh 1x1 cell. The top row is the rig; the bottom row is the kept
whole-body picture, so a misplaced root reads at a glance. Does not simulate the spasm.

    python3 twitch_rig_preview.py <tree.xml> <body texPath> <drawSize> --mod-textures <dir> --out <png> [--whole <texPath>]
"""
import argparse
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

PPC = 110  # preview pixels per cell
FACES = ("south", "east", "north", "west")


def vec(text):
    return [float(x) for x in re.findall(r"-?\d*\.?\d+", text or "")]


def spastic_nodes(tree_xml):
    """Every Spastic li, document order; the rig parents carry no offset of their own."""
    return [li for li in ET.parse(tree_xml).getroot().iter("li") if li.get("Class") == "PawnRenderNodeProperties_Spastic"]


def face_data(node, face):
    """(offset x, offset z, rotation, flip, layer) for this facing, DrawData's fallbacks applied."""
    dd = node.find("drawData")
    data = dd.find("data" + face.capitalize()) if dd is not None else None
    east = dd.find("dataEast") if dd is not None else None

    def own(tag):
        return data.find(tag).text if data is not None and data.find(tag) is not None else None

    off = own("offset")
    if off is not None:
        o = vec(off)
        ox, oz = o[0], o[2]
    elif face == "west" and east is not None and east.find("offset") is not None:
        o = vec(east.find("offset").text)
        ox, oz = -o[0], o[2]  # DrawData.OffsetForRot mirrors east for west
    else:
        ox, oz = 0.0, 0.0
    layer = own("layer")
    return ox, oz, float(own("rotationOffset") or 0), own("flip") == "true", float(layer if layer else node.findtext("baseLayer") or 0)


def tex(root, path, face):
    """The Graphic_Multi picture for a facing: west is east mirrored unless a _west file exists."""
    p = root / f"{path}_{face}.png"
    if p.is_file():
        return Image.open(p).convert("RGBA")
    if face == "west":
        return Image.open(root / f"{path}_east.png").convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
    raise SystemExit(f"no picture {p}")


def place(canvas, cx, cy, node, root, face):
    ox, oz, rot, flip, _ = face_data(node, face)
    dd = node.find("drawData")
    scale = float(dd.findtext("scale") or 1)
    pz = -(vec(dd.find("defaultData").findtext("pivot"))[1] - 0.5)  # 0.45 above the mesh centre
    im = tex(root, node.findtext("texPath"), "east" if face == "west" else face)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    size = max(1, round(PPC * scale))
    im = im.resize((size, size), Image.LANCZOS)
    # The fixed point, in image pixels from the image centre, then that same point on the canvas.
    root_up = pz * PPC * scale
    a = math.radians(rot)  # engine angle is clockwise seen from above
    rx, ry = cx + ox * PPC, cy - (oz + pz) * PPC
    big = im.rotate(-rot, resample=Image.BICUBIC, expand=True)
    # Mesh centre sits root_up below the root before rotation; rotate that vector clockwise by rot.
    mx = rx + root_up * math.sin(a)
    my = ry + root_up * math.cos(a)
    canvas.alpha_composite(big, (max(0, round(mx - big.width / 2)), max(0, round(my - big.height / 2))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree")
    ap.add_argument("body")
    ap.add_argument("draw_size", type=float)
    ap.add_argument("--mod-textures", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--whole")
    a = ap.parse_args()
    nodes = spastic_nodes(a.tree)
    w = round(PPC * max(4.0, a.draw_size + 2))
    sheet = Image.new("RGBA", (w * 4, w * (2 if a.whole else 1)), (58, 54, 50, 255))
    for col, face in enumerate(FACES):
        cell = Image.new("RGBA", (w, w), (0, 0, 0, 0))
        order = sorted(nodes, key=lambda n: face_data(n, face)[4])
        body = tex(a.mod_textures, a.body, face)
        size = round(PPC * a.draw_size)
        body = body.resize((size, size), Image.LANCZOS)
        drawn = False
        for n in order:
            if not drawn and face_data(n, face)[4] >= 0:
                cell.alpha_composite(body, ((w - size) // 2, (w - size) // 2))
                drawn = True
            place(cell, w / 2, w / 2, n, a.mod_textures, face)
        if not drawn:
            cell.alpha_composite(body, ((w - size) // 2, (w - size) // 2))
        sheet.alpha_composite(cell, (col * w, 0))
        if a.whole:
            whole = tex(a.mod_textures, a.whole, face).resize((size, size), Image.LANCZOS)
            sheet.alpha_composite(whole, (col * w + (w - size) // 2, w + (w - size) // 2))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(a.out)
    print(a.out, sheet.size, "nodes", len(nodes))


if __name__ == "__main__":
    main()
