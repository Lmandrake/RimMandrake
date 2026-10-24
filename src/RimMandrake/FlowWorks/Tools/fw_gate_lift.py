#!/usr/bin/env python3
"""SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS + GRATE_DOOR_REBUILD_LIFTS_LIKE_THE_SLUICE -- the lift-gate art, offline.

Owner 2026-10-24: "There are two copies of the Sluice gate that slide over each other and the whole remains 'closed' in
appearance, there is never a gap. Sluice gates do not open by sliding left/right, they slide 'up' to allow the water
through." Of the grate: "overlapping grates are seen to 'slide apart' to then stand side by side, without any passable
space ... it would still make more sense for them to slide 'up'."

Vanilla's 1x1 door draws its whole texture TWICE (Building_Door.DrawMovers) sliding the copies 0.45 cell apart: two full
gates side by side, so nothing ever opens. A lift gate instead is two layers cut from the approved gate art:
  FRAME  the posts (and the sluice's crank head), fixed;
  PANEL  the boards / bars between the posts, drawn BEHIND the frame and raised by liftCells x OpenPct cells (+z, up on
         screen: RimWorld's oblique view draws height as up).
Building_RM_FlowDoor.DrawAt draws exactly this (frame at the cell, panel at +z); liftCells is read from the def's
RM_FlowDoorExtension (FlowWorks_Doors.xml), never typed here.

  layers(gate, facing)   -> (frame RGBA, panel RGBA) cut from Textures/.../Canals/<gate>_<facing>.png by the masks below
  draw(gate, facing, pct, rule="lift"|"vanilla")  -> the 1-cell sprite as drawn (a 3-cell-tall canvas, cell in the middle)
  passage_cover(img, facing) -> fraction of the passage a pawn crosses that is covered by opaque gate
  scene(...)             -> the gate on its real terrain: the dug canal (vanilla Gravel x RM_Channel_Empty colour, or the
                            water stand-in), soil banks, a vanilla human in or before the gap.

CLI:  fw_gate_lift.py layers OUTDIR     write the 8 layer PNGs (art install takes them from there)
      fw_gate_lift.py sheet OUT.png     closed / half / open, both facings, both gates, dry and wet, at play zoom
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
FW = HERE.parent
TEX = FW / "Textures/Things/Building/FlowWorks/Canals"
DOORS_XML = FW / "Defs/Canals/ThingDefs/FlowWorks_Doors.xml"
TERRAIN_XML = FW / "Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml"
VANILLA_TEX_DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/scratch/vanilla_tex/ludeon.rimworld.core"
GATES = ("RM_Sluice", "RM_SecurityGrateDoor")
FACINGS = ("south", "east")
SRC = 256           # source texture px per cell
TERRAIN_CELLS = 10  # cells one terrain texture repeat spans (fw_scenes_spikes.GRAVEL_CELLS)
SKIN = (0.93, 0.78, 0.62)  # a mid vanilla skin tone for the scale human

# The PANEL mask per gate and facing, in source pixels (x0, y0, x1, y1), y down from the top (north) of the cell. Everything
# opaque outside it is FRAME. Read off the art's alpha profile (posts are the two dense column bands; the panel is between
# them; on the side views the two post blocks are the dense ends, the panel edge the strip between).
PANEL_BOX = {
    ("RM_Sluice", "south"): (46, 66, 210, 226),
    ("RM_Sluice", "east"): (0, 52, 256, 163),
    ("RM_SecurityGrateDoor", "south"): (48, 40, 206, 212),
    ("RM_SecurityGrateDoor", "east"): (0, 44, 256, 165),
}

# The passage a pawn crosses, in cell fractions (x0, y0, x1, y1), y down. South view (leaf spans East-West): pawns walk
# North-South through the middle between the posts, the body drawn over the lower two thirds. Side view (leaf spans
# North-South): pawns walk East-West across the strip through the middle of the cell.
PASSAGE = {"south": (0.30, 0.34, 0.70, 0.98), "east": (0.38, 0.30, 0.62, 0.62)}
OPEN_MAX_COVER = 0.10    # open: at most this much of the passage is gate
CLOSED_MIN_COVER = 0.30  # closed: at least this much is (boards nearly all of it; the grate is bars with air between)


def lift_cells(gate):
    """liftCells of the gate's RM_FlowDoorExtension in FlowWorks_Doors.xml (the C# reads the same field)."""
    for t in ET.parse(DOORS_XML).getroot().iter("ThingDef"):
        if t.findtext("defName") == gate:
            v = t.find("modExtensions/li/liftCells")
            if v is None:
                raise SystemExit("fw_gate_lift: %s has no liftCells in %s" % (gate, DOORS_XML))
            return float(v.text)
    raise SystemExit("fw_gate_lift: no ThingDef %s in %s" % (gate, DOORS_XML))


def source(gate, facing):
    return Image.open(TEX / ("%s_%s.png" % (gate, facing))).convert("RGBA")


def layers(gate, facing):
    """(frame, panel): the source cut by PANEL_BOX. Their alpha sums to the source's exactly (a partition)."""
    a = np.asarray(source(gate, facing)).copy()
    x0, y0, x1, y1 = PANEL_BOX[(gate, facing)]
    m = np.zeros(a.shape[:2], bool)
    m[y0:y1, x0:x1] = True
    panel = a.copy()
    panel[~m, 3] = 0
    frame = a.copy()
    frame[m, 3] = 0
    return Image.fromarray(frame), Image.fromarray(panel)


def layer_name(gate, facing, part):
    """Texture file name of a layer: <gate>_Frame_<facing>.png / <gate>_Panel_<facing>.png (Graphic_Multi paths
    .../<gate>_Frame and .../<gate>_Panel)."""
    return "%s_%s_%s.png" % (gate, part.capitalize(), facing)


def draw(gate, facing, pct, rule="lift", px=SRC, frame=None, panel=None):
    """The gate as drawn at OpenPct pct on a canvas 1 cell wide, 3 cells tall; the gate's own cell is the middle third.
    rule="lift": frame fixed, panel behind it at +liftCells*pct. rule="vanilla": Building_Door.DrawMovers -- the WHOLE
    texture twice, shifted -0.45*pct and +0.45*pct cell sideways (the old behaviour, kept so the check can fail on it)."""
    W, H = px, 3 * px
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    def put(im, dx, dz):
        im = im.resize((px, px), Image.LANCZOS) if im.size != (px, px) else im
        out.alpha_composite(im, (int(round(dx * px)), int(round(px - dz * px))))
    if rule == "vanilla":
        full = source(gate, facing)
        if facing == "south":
            for s in (-1, 1):
                put(full, s * 0.45 * pct, 0)
        else:   # FLOWDOOR_EW_PERSPECTIVE: the side view's movers slide North and South
            for s in (-1, 1):
                put(full, 0, s * 0.45 * pct)
        return out
    if frame is None or panel is None:
        frame, panel = layers(gate, facing)
    put(panel, 0, lift_cells(gate) * pct)
    put(frame, 0, 0)
    return out


def passage_cover(img, facing, alpha_min=128):
    """Opaque fraction of the passage box inside the middle (own) cell of a draw() canvas."""
    a = np.asarray(img)[:, :, 3]
    px = a.shape[1]
    x0, y0, x1, y1 = PASSAGE[facing]
    box = a[px + int(y0 * px): px + int(y1 * px), int(x0 * px): int(x1 * px)]
    return float((box >= alpha_min).mean())


# ── the real ground: dug canal (Gravel x RM_Channel_Empty colour), water stand-in, soil banks ──
def _tex(name, P):
    f = Path(os.environ.get("RM_VANILLA_TEX", VANILLA_TEX_DEFAULT)) / name
    if not f.is_file():
        return None
    side = round(TERRAIN_CELLS * P)
    return np.asarray(Image.open(f).convert("RGB").resize((side, side), Image.LANCZOS), np.float32)


def _channel_tint(defname="RM_Channel_Empty"):
    for t in ET.parse(TERRAIN_XML).getroot().iter("TerrainDef"):
        if t.findtext("defName") == defname:
            c = t.findtext("color")
            if not c:
                return (1.0, 1.0, 1.0)
            return tuple(float(v) for v in re.findall(r"[\d.]+", c)[:3])
    raise SystemExit("fw_gate_lift: no TerrainDef %s" % defname)


def ground(cols, rows, P, canal_cells, wet):
    """cols x rows cells; canal_cells = set of (x, z) (z from the top row) dug; wet = the canal holds water."""
    soil = _tex("Soil.png", P)
    grav = _tex("Gravel.png", P)
    water = _tex("WaterShallowRamp.png", P)
    if soil is None or grav is None:
        raise SystemExit("fw_gate_lift: vanilla Soil.png / Gravel.png not extracted under $RM_VANILLA_TEX (%s)"
                         % os.environ.get("RM_VANILLA_TEX", VANILLA_TEX_DEFAULT))
    tint = np.array(_channel_tint(), np.float32)
    img = np.zeros((rows * P, cols * P, 3), np.float32)
    for z in range(rows):
        for x in range(cols):
            sl = (slice(z * P, (z + 1) * P), slice(x * P, (x + 1) * P))
            src = soil
            mul = np.ones(3, np.float32)
            if (x, z) in canal_cells:
                src, mul = grav, tint
            tile = src[(z * P) % src.shape[0]:(z * P) % src.shape[0] + P, (x * P) % src.shape[1]:(x * P) % src.shape[1] + P]
            img[sl] = tile * mul
            if (x, z) in canal_cells:
                if wet and water is not None:
                    wt = water[(z * P) % water.shape[0]:(z * P) % water.shape[0] + P, (x * P) % water.shape[1]:(x * P) % water.shape[1] + P]
                    img[sl] = img[sl] * 0.35 + wt * 0.65
                # the cut's lip: a darker inner edge where a bank meets the channel
                for (dx, dz, ys, xs) in ((-1, 0, slice(None), slice(0, P // 12)), (1, 0, slice(None), slice(P - P // 12, P)),
                                         (0, -1, slice(0, P // 12), slice(None)), (0, 1, slice(P - P // 12, P), slice(None))):
                    if (x + dx, z + dz) not in canal_cells and 0 <= x + dx < cols and 0 <= z + dz < rows:
                        img[z * P:(z + 1) * P, x * P:(x + 1) * P][ys, xs] *= 0.6
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def human(P, facing="south"):
    """A vanilla human (naked body + average head) at true scale: 1.5-cell body mesh, head 0.34 cell above."""
    d = Path(os.environ.get("RM_VANILLA_TEX", VANILLA_TEX_DEFAULT))
    body = Image.open(d / ("Naked_Male_%s.png" % facing)).convert("RGBA").resize((int(1.5 * P),) * 2, Image.LANCZOS)
    head = Image.open(d / ("Male_Average_Normal_%s.png" % facing)).convert("RGBA").resize((int(1.5 * P),) * 2, Image.LANCZOS)
    out = Image.new("RGBA", (int(1.5 * P), int(1.5 * P) + int(0.34 * P)), (0, 0, 0, 0))
    out.alpha_composite(body, (0, int(0.34 * P)))
    out.alpha_composite(head, (0, 0))
    a = np.asarray(out).astype(np.float32)
    a[:, :, :3] *= np.array(SKIN, np.float32)   # the body and head textures are skin masks: the game tints them
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def scene(gate, facing, pct, wet, P=83, rule="lift", pawn=None):
    """3 x 4 cells (south view: canal runs North-South down the middle column) or 4 x 3 (side view: canal runs East-West
    along the middle row); the gate in the canal; pawn = None | "gap" (standing in the gate cell) | "before" (the cell
    south of / west of the gate)."""
    if facing == "south":
        cols, rows, gx, gz = 3, 4, 1, 1
        canal = {(1, z) for z in range(rows)}
    else:
        cols, rows, gx, gz = 4, 3, 1, 1
        canal = {(x, 1) for x in range(cols)}
    img = ground(cols, rows, P, canal, wet)
    g = draw(gate, facing, pct, rule=rule, px=P)
    hum = human(P, "south" if facing == "south" else "east")
    hx = lambda cx: int(cx * P + P / 2 - hum.size[0] / 2)
    hy = lambda cz: int(cz * P + P / 2 - hum.size[1] / 2 - 0.17 * P)
    if pawn == "before" and facing == "south":
        img.alpha_composite(hum, (hx(gx), hy(gz + 1)))
    img.alpha_composite(g, (gx * P, gz * P - P))
    if pawn == "gap":
        img.alpha_composite(hum, (hx(gx), hy(gz)))
    if pawn == "before" and facing == "east":
        img.alpha_composite(hum, (hx(gx - 1), hy(gz)))
    return img


def sheet(out_path, P=83):
    states = ((0.0, "closed", "before"), (0.5, "half", None), (1.0, "open", None), (1.0, "open, walked", "gap"))
    tiles = []
    for gate in GATES:
        for facing in FACINGS:
            for wet in (False, True):
                row = [(scene(gate, facing, pct, wet, P, pawn=pawn), "%s %s %s %s" % (gate[3:], facing, "wet" if wet else "dry", name))
                       for pct, name, pawn in states]
                tiles.append(row)
    tw = max(im.size[0] for r in tiles for im, _ in r)
    th = max(im.size[1] for r in tiles for im, _ in r) + 14
    S = Image.new("RGBA", (len(states) * (tw + 8) + 8, len(tiles) * (th + 8) + 8), (32, 32, 32, 255))
    d = ImageDraw.Draw(S)
    for r, row in enumerate(tiles):
        for c, (im, label) in enumerate(row):
            x, y = 8 + c * (tw + 8), 8 + r * (th + 8)
            S.alpha_composite(im, (x, y + 14))
            d.text((x, y), label, fill=(230, 230, 230, 255))
    S.save(out_path)
    return S


def check():
    """The regression: every gate and facing, open leaves a gap, closed does not, half is between; and the OLD draw
    (vanilla's two sideways movers) leaves no gap when open -- the instrument can see the defect."""
    fails = []
    for gate in GATES:
        for facing in FACINGS:
            c = passage_cover(draw(gate, facing, 0.0), facing)
            h = passage_cover(draw(gate, facing, 0.5), facing)
            o = passage_cover(draw(gate, facing, 1.0), facing)
            old = passage_cover(draw(gate, facing, 1.0, rule="vanilla"), facing)
            print("  %-22s %-5s closed %.2f half %.2f open %.2f | old-open %.2f" % (gate, facing, c, h, o, old))
            if c < CLOSED_MIN_COVER:
                fails.append("%s %s closed covers only %.2f of the passage" % (gate, facing, c))
            if o > OPEN_MAX_COVER:
                fails.append("%s %s open still covers %.2f of the passage" % (gate, facing, o))
            if not (o <= h <= c):
                fails.append("%s %s half-open %.2f is not between open and closed" % (gate, facing, h))
            if old <= OPEN_MAX_COVER:
                fails.append("can-fail: the old sideways draw of %s %s reads as open (%.2f): the instrument is blind" % (gate, facing, old))
    return fails


def main(argv):
    if len(argv) >= 2 and argv[0] == "layers":
        out = Path(argv[1])
        out.mkdir(parents=True, exist_ok=True)
        for gate in GATES:
            for facing in FACINGS:
                fr, pa = layers(gate, facing)
                fr.save(out / layer_name(gate, facing, "frame"))
                pa.save(out / layer_name(gate, facing, "panel"))
        print("wrote 8 layers to", out)
        return 0
    if len(argv) >= 2 and argv[0] == "sheet":
        sheet(argv[1])
        print("wrote", argv[1])
        return 0
    if argv and argv[0] == "check":
        f = check()
        for x in f:
            print("FAIL", x)
        return 1 if f else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
