"""wall_mount_check.py -- offline proof that wall brackets and cord wall plates are mounted ON the wall (round 4, 2026-10-04).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/wall_mount_check.py            # check + proof PNGs, exit 1 on a fault
    python3 src/RimMandrake/Utils/mockups/messy_conduit/wall_mount_check.py --plant    # can-fail: the round-3 rules must FAIL

Owner, typed review 2026-10-04: "Wall plates/rock holes STILL need more perspective bending and shifting into the wall. Check
next time: do they extend OUT of the wall? If so, it's not right. They should look mounted ON the wall." and "North-facing
bracket ... more perspective needed. I took a second screenshot to show what a north-facing torch looks like mounted on the
wall. The connector really should be barely visible at all."

The wall model is MEASURED from his station-9 shot (Transient/mc_owner_shots_r4/20261004162252_1.jpg, 5-cell room = 665 px
displayed = 133 px per cell): a wall cell draws its TOP over its north 0.62 and its visible SOUTH FACE (light band) over its
south 0.38; east/west faces are edge-on (bevel ~0.18); the north face is hidden. The same numbers are Core/WallMount.cs; this
script READS them (and the generated BracketGeometryTable.cs) rather than restating them, then composites the real textures at
133 px/cell against that wall and checks pixels:
  bracket rot North (on the south face):  every plate pixel inside the wall cell and inside the south band
  bracket rot East/West (side faces):     every plate pixel inside the wall cell, within the edge bevel
  bracket rot South (hidden north face):  no plate at all; the art shows at most NORTH_SHOW over the wall's top edge, and
                                          nothing deeper than a sliver into the wall top (the torch rule)
  cord plates (StubWall / StubRock), 4 faces: the printed quad inside the wall cell and inside its face's mount depth
Proofs: Transient/mc_aerial_r4/wall_mount_<Look>.png and torch_compare.png (his torch photo beside the new north-face bracket).
"""
import os
import re
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
MOD = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack")
SRC = os.path.join(MOD, "Source")
TEX = os.path.join(MOD, "Textures", "RimMandrake", "GimmeSomeSlack")
OUT = os.path.join(REPO, "Transient", "mc_aerial_r4")
SHOTS = os.path.join(REPO, "Transient", "mc_owner_shots_r4")
PX = 133                       # px per cell, as in his screenshot
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
ROTS = ("North", "East", "South", "West")
NORMAL = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}       # rot points AT the wall
NORTH_SHOW = 0.25              # cells of art allowed over the wall's top edge for a north-face bracket (torch flame ~0.3)
TOL = 1.5 / PX                 # one-and-a-half pixel tolerance
STUB_STYLE = {"Scrapper": "", "Industrial": "Styles/StarWars/", "Modern": "Styles/ExtCord/", "Futuristic": "Styles/Cybertek/"}


def cs_consts(path):
    """public const double NAME = value pairs from a C# file (several per line allowed)."""
    src = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"const double ([^;]+);", src):
        for part in m.group(1).split(","):
            k, _, v = part.partition("=")
            try:
                out[k.strip()] = float(v.strip())
            except ValueError:
                pass
    return out


def table(name):
    src = open(os.path.join(SRC, "Aerial", "BracketGeometryTable.cs"), encoding="utf-8").read()
    body = src[src.index("Dictionary<string, %s> %s()" % ("P2" if name == "Build" else "double", name)):]
    body = body[:body.index("return d;")]
    d = {}
    for m in re.finditer(r'd\["([^"]+)"\] = (?:new P2\(([-\d.]+), ([-\d.]+)\)|([-\d.]+));', body):
        d[m.group(1)] = (float(m.group(2)), float(m.group(3))) if m.group(2) else float(m.group(4))
    return d


WM = cs_consts(os.path.join(SRC, "Core", "WallMount.cs"))
AM = cs_consts(os.path.join(SRC, "Aerial", "AerialMath.cs"))


def inset(rot, depth, plant=False):
    """Mirror of AerialMath.BracketInset (the C# selftest asserts the same rule on the same table)."""
    if plant:
        return 0.12                                     # the round-3 rule: one inset for every face
    if rot == 2:
        return AM["NorthFaceCutInset"]
    if rot == 0:
        return min(max(0.12, depth + 0.02), WM["SouthBand"] - 0.02)
    return min(max(0.12, depth + 0.01), WM["SideBevel"])


def wall_scene():
    """3x3 cells, the wall in the middle cell; returns (image, wall box in px)."""
    im = Image.new("RGBA", (3 * PX, 3 * PX), (118, 92, 64, 255))
    d = ImageDraw.Draw(im)
    x0, y0 = PX, PX                                       # image y grows DOWN (south)
    band = int(round(WM["SouthBand"] * PX))
    bev = int(round(WM["SideBevel"] * PX))
    d.rectangle([x0, y0, x0 + PX - 1, y0 + PX - 1], fill=(62, 62, 64, 255))
    d.rectangle([x0, y0 + PX - band, x0 + PX - 1, y0 + PX - 1], fill=(112, 112, 114, 255))     # south face band
    d.rectangle([x0, y0, x0 + bev // 3, y0 + PX - band], fill=(78, 78, 80, 255))              # side bevel hints
    d.rectangle([x0 + PX - 1 - bev // 3, y0, x0 + PX - 1, y0 + PX - band], fill=(78, 78, 80, 255))
    d.rectangle([x0, y0, x0 + PX - 1, y0 + PX - 1], outline=(0, 0, 0, 255))
    return im


def to_px(x, z):
    """World (cells, wall cell centre = 0,0; +z north) -> image px."""
    return 1.5 * PX + x * PX, 1.5 * PX - z * PX


def bracket(look, rot, plant=False):
    """Composite one bracket; return (image, faults)."""
    key = "%s/%s" % (look, ROTS[rot])
    edge, depth, ins = EDGE[key], DEPTH[key], INS[key]
    nx, nz = NORMAL[rot]
    d = 0.5 + inset(rot, depth, plant) - edge
    cx, cz = -nx * 1.0 + nx * d, -nz * 1.0 + nz * d        # bracket cell is one cell AWAY from the wall, against the normal
    fac = {0: "north", 1: "east", 2: "south", 3: "east"}[rot]
    sp = Image.open(os.path.join(TEX, "Aerial", "Styles", look, "WallBracket_%s.png" % fac)).convert("RGBA")
    if rot == 3:
        sp = sp.transpose(Image.FLIP_LEFT_RIGHT)              # west mirrors east, as the game does
    sp = sp.resize((PX, PX), Image.LANCZOS)
    im = wall_scene()
    px, pz = to_px(cx, cz)
    im.alpha_composite(sp, (int(round(px - PX / 2)), int(round(pz - PX / 2))))
    faults = []
    a = sp.getchannel("A")
    W = PX
    for j in range(W):
        for i in range(W):
            if a.getpixel((i, j)) < 128:
                continue
            # pixel -> world (cells)
            wx = cx + (i + 0.5) / W - 0.5
            wz = cz + 0.5 - (j + 0.5) / W
            depth_in = (wx * nx + wz * nz) + 0.5                     # 0 at the wall's outer face (-0.5 along n), + into it
            # along-normal distance of this pixel from the art's wall-side extreme (art units = cells)
            from_edge = edge - ((i + 0.5) / W - 0.5) * nx - (0.5 - (j + 0.5) / W) * nz
            in_plate = depth > 0 and from_edge <= depth + 1e-9
            if rot == 2:
                if depth_in > AM["NorthFaceCutInset"] + 0.02 + TOL:
                    faults.append("art %.2f deep into the wall top (hidden face: only the insulator may show)" % depth_in)
                if -depth_in > NORTH_SHOW + TOL:
                    faults.append("art %.2f over the wall's top edge (> %.2f)" % (-depth_in, NORTH_SHOW))
            elif in_plate:
                lim = WM["SouthBand"] if rot == 0 else WM["SideBevel"]
                if depth_in < -TOL:
                    faults.append("plate pixel %.2f OUT of the wall (on the open floor)" % -depth_in)
                elif depth_in > lim + TOL:
                    faults.append("plate pixel %.2f into the wall, past its face (%.2f)" % (depth_in, lim))
    # one line per kind of fault
    seen, out = set(), []
    for f in faults:
        k = f.split(" ")[0] + f.split(" ")[-1]
        if k not in seen:
            seen.add(k); out.append(f)
    return im, out


def stub(look, face, rock=False, plant=False):
    """The cord's wall plate (or rock hole) as CordBuilder prints it via WallMount.EntryDecal, for face in N/S/E/W meaning
    the cord ARRIVES from that side. Returns (image, faults)."""
    into = {"S": (0, 1), "N": (0, -1), "W": (1, 0), "E": (-1, 0)}[face]
    kind = "South" if into[1] > 0.5 else "North" if into[1] < -0.5 else "Side"
    depth = WM["SouthBand"] - 0.06 if kind == "South" else 0.10 if kind == "Side" else 0.06
    maxd = {"South": WM["SouthBand"], "Side": WM["SideBevel"], "North": WM["NorthSliver"]}[kind]
    u0, u1, v0, v1 = (WM["RockU0"], WM["RockU1"], WM["RockV0"], WM["RockV1"]) if rock else (WM["WallU0"], WM["WallU1"], WM["WallV0"], WM["WallV1"])
    if kind != "South":
        u0 = max(u0, WM["EdgeU0"])
    across = WM["PlateAcross"]
    art = Image.open(os.path.join(TEX, STUB_STYLE[look] + ("StubRock.png" if rock else "StubWall.png"))).convert("RGBA")
    n = art.size[0]
    crop = art.crop((int(u0 * n), int((1 - v1) * n), int(u1 * n), int((1 - v0) * n)))
    crop = crop.resize((max(1, int(round(depth * PX))), max(1, int(round(across * PX)))), Image.LANCZOS)   # art X = depth
    ang = {(0, 1): 90, (0, -1): -90, (1, 0): 0, (-1, 0): 180}[into]
    crop = crop.rotate(ang, expand=True)
    face_pt = (-into[0] * 0.5, -into[1] * 0.5)                # the face the cord meets, wall centre = origin
    centre = 0.02 if plant else WM["FaceMargin"] + depth / 2      # plant: the round-3 placement, centred on the face line
    c = (face_pt[0] + into[0] * centre, face_pt[1] + into[1] * centre)
    im = wall_scene()
    dr = ImageDraw.Draw(im)
    # the incoming cord, straight, to the face line
    f0 = to_px(face_pt[0] - into[0] * 1.0, face_pt[1] - into[1] * 1.0)
    f1 = to_px(face_pt[0], face_pt[1])
    dr.line([f0, f1], fill=(28, 26, 24, 255), width=max(3, int(0.09 * PX)))
    px, pz = to_px(*c)
    im.alpha_composite(crop, (int(round(px - crop.size[0] / 2)), int(round(pz - crop.size[1] / 2))))
    near = centre - depth / 2
    far = centre + depth / 2
    faults = []
    if near < -TOL:
        faults.append("%s plate starts %.2f OUT of the wall" % (face, -near))
    if far > maxd + TOL:
        faults.append("%s plate reaches %.2f into the wall, past its %s face (%.2f)" % (face, far, kind, maxd))
    return im, faults


def label(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.size[0], 18], fill=(0, 0, 0, 170))
    d.text((4, 3), text, fill=(255, 235, 190, 255))
    return im


def torch_compare():
    """His torch photo (north-face wall torch beside the round-3 bracket, same 133 px/cell zoom) next to the new rot-South
    bracket composite, every look."""
    shot = os.path.join(SHOTS, "20261004162357_1.jpg")
    tiles = []
    if os.path.exists(shot):
        ph = Image.open(shot).convert("RGBA")
        sc = ph.size[0] / 2000.0                              # the shot is 2516 wide; coordinates read at 2000 display
        # torch at ~(670,450) display, wall top edge at ~472; the round-3 bracket at ~(520,465)
        box = [int(v * sc) for v in (440, 380, 760, 560)]
        t = ph.crop(box)
        t = t.resize((int(t.size[0] * PX / (133 * sc)), int(t.size[1] * PX / (133 * sc))), Image.LANCZOS)
        tiles.append(label(t, "his shot: round-3 bracket (left), vanilla wall torch (right)"))
    for lk in LOOKS:
        im, _ = bracket(lk, 2)
        tiles.append(label(im.crop((0, 0, 3 * PX, int(1.8 * PX))), "round 4 %s north-face bracket" % lk))
    w = sum(t.size[0] for t in tiles) + 10 * len(tiles)
    h = max(t.size[1] for t in tiles)
    sheet = Image.new("RGBA", (w, h), (30, 26, 22, 255))
    x = 0
    for t in tiles:
        sheet.alpha_composite(t, (x, 0)); x += t.size[0] + 10
    return sheet


def main(argv):
    plant = "--plant" in argv
    global EDGE, DEPTH, INS
    EDGE, DEPTH, INS = table("PlateEdge"), table("PlateDepth"), table("Build")
    os.makedirs(OUT, exist_ok=True)
    allf = []
    for lk in LOOKS:
        tiles = []
        for rot in range(4):
            im, f = bracket(lk, rot, plant)
            allf += ["%s bracket rot %s: %s" % (lk, ROTS[rot], x) for x in f]
            tiles.append(label(im, "%s bracket rot %s %s" % (lk, ROTS[rot], "OK" if not f else "FAULT")))
        for face in "SNEW":
            for rock in (False, True):
                im, f = stub(lk, face, rock, plant)
                allf += ["%s %s from %s: %s" % (lk, "rock hole" if rock else "wall plate", face, x) for x in f]
                tiles.append(label(im, "%s %s, cord from %s %s" % (lk, "hole" if rock else "plate", face, "OK" if not f else "FAULT")))
        cols = 4
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGBA", (cols * (3 * PX + 6), rows * (3 * PX + 6)), (30, 26, 22, 255))
        for k, t in enumerate(tiles):
            sheet.alpha_composite(t, ((k % cols) * (3 * PX + 6), (k // cols) * (3 * PX + 6)))
        if not plant:
            sheet.convert("RGB").save(os.path.join(OUT, "wall_mount_%s.png" % lk))
    if not plant:
        torch_compare().convert("RGB").save(os.path.join(OUT, "torch_compare.png"))
    print("\n".join(allf) if allf else "no faults")
    print("%s: %d faults over %d looks x (4 bracket facings + 8 cord plates)" % ("PLANTED round-3 rules" if plant else "wall mounts", len(allf), len(LOOKS)))
    if plant:
        return 0 if allf else 1            # the round-3 rule must be caught
    return 1 if allf else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
