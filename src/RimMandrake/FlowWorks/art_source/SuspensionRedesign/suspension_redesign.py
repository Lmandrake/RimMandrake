#!/usr/bin/env python3
"""Steel and Heavy suspension bridges as two different bridges (SUSPENSION_BRIDGE_REDRAW_HEAVY_JUST_PAINTED).

Owner 2026-10-24 (owner_review_FW_20261024.md row 8): "the heavy one is just a recolored timber one, and that makes NO sense.
It should look the most rugged and tough. For the Steel: Make a real "suspension bridge" here with raised towers at the
anchor and criss-cross cables holding it all together ... For the Heavy case, it should be even more rigorous". Then, with
reference photos (D:\\ClaudeWork\\rimmandrake\\fw_art_geometry_20261024\\suspension_ref\\):
  Steel: "Nothing in the suspension bridge should have red. ... a real "very short suspension bridge" design. Cement,
          wooden crosswalk, steel rails, steel cables, steel I-bean posts."   (owner_short_suspension_bridge_photo.png)
  Heavy: "Steel construction, paved crossing, no cables, cement base."         (owner_heavy_truss_bridge_photo.png)
  Paint: "These bridges should be made such that the player can paint them, however Rimworld does that."

What is drawn (top-down, the deck tile runs N-S as every deck source does; build_deck_atlas turns it into the Basic-linked
atlas and Building_SuspensionDeck turns it 90 degrees on an E-W bridge):
  STEEL deck   wooden plank crosswalk; in each 28 px side band (the part the atlas shows on an open side) the steel edge
               stringer, I-section rail posts, the steel pipe handrail, the hanger rods and the main steel cable.
  STEEL anchor a cement abutment slab carrying the tower: two steel I-beam posts, top and middle ties and the X brace
               between them (face-on in the N/S pictures, from above in the E one), backstay cables to two cement ground
               blocks, the main cables leaving the post tops at the deck band's cable line.
  HEAVY deck   a paved concrete crossing between two through-truss sides: the top chord with gusset plates in each band,
               an overhead floor strut at every panel point and the overhead X lateral bracing across the road. No cables.
  HEAVY anchor a massive cement abutment with bearing plates, the paved approach and low steel rails, and the truss's portal
               (two heavy end posts, a lattice portal strut). No cables.
  Grated decks the same sides over open steel bar grating.
Colours are plain steel (no paint colour of their own), weathered dark steel for the heavy truss, cement and bare wood:
no red anywhere (no_red() below; the check is pinned by selftest_suspension_redesign.py).

Paint (vanilla's mechanism, read from Core's defs, not guessed): <building><paintable>true</paintable></building> lets the
Paint designator set the building's paint colour, which replaces its DrawColor (colorOne). Under shaderType CutoutComplex
the colour reaches only the mask's red channel (as Core's benches do and our RM_ContainerMaterials do): every piece here is
written with its <name>_m mask, red = steel (towers, posts, cables, rails, truss), black = cement and wood. Unpainted, the
steel draws in its material colour (the def is MadeFromStuff), i.e. the default steel look.

Usage: suspension_redesign.py OUT_DIR       -> OUT_DIR/<texture rel path>.png and _m.png for every piece, plus the deck
                                               atlases (and their masks) built by SuspensionLooks/build_deck_atlas.build.
Installing is a separate, ledgered step; nothing here writes the Textures tree.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
FW = HERE.parents[1]
sys.path.insert(0, str(FW / "art_source/SuspensionLooks"))
import build_deck_atlas as BDA  # noqa: E402

THINGS = "Things/Building/FlowWorks/SuspensionBridge"
N = 256          # texture edge
SS = 4           # supersampling while drawing
BAND = 28        # build_deck_atlas's band for the Steel/Heavy decks (JOBS): side structure lives in x < 28 and x >= 228

# ---- palette: no red (hue within RED_DEG of 0 at sat > RED_SAT) anywhere ----------------------------------------------
STEEL = (132, 138, 144)
STEEL_HI = (186, 192, 198)
STEEL_DK = (78, 83, 89)
STEEL_EDGE = (36, 39, 43)
HVY = (84, 85, 86)            # weathered dark steel (the truss photo's steel, minus its sunset)
HVY_HI = (122, 123, 124)
HVY_DK = (54, 55, 56)
HVY_EDGE = (24, 25, 26)
CEMENT = (176, 174, 168)
CEMENT_DK = (140, 138, 133)
CEMENT_FACE = (118, 116, 112)
CEMENT_EDGE = (70, 69, 67)
PAVE = (150, 150, 147)
WOOD = (150, 126, 96)         # hue 34 deg, sat 0.36: bare weathered plank, well clear of the red band
WOOD_DK = (118, 98, 72)
WOOD_GAP = (46, 40, 34)
CABLE = (98, 102, 106)
CABLE_HI = (160, 164, 168)

RED_DEG, RED_SAT, VAL_MIN, ALPHA_MIN = 25, 0.40, 0.25, 128
MAX_RED_SHARE = 0.005         # at most 0.5% of opaque pixels may fall in the red band (antialiasing noise)


class Pic:
    """A 256 px picture drawn at SS x, with a parallel paint mask (red = steel takes the paint colour)."""

    def __init__(self):
        self.im = Image.new("RGBA", (N * SS, N * SS), (0, 0, 0, 0))
        self.mk = Image.new("L", (N * SS, N * SS), 0)
        self.d = ImageDraw.Draw(self.im)
        self.m = ImageDraw.Draw(self.mk)

    @staticmethod
    def _s(v):
        return [round(c * SS) for c in v]

    def rect(self, x0, y0, x1, y1, col, steel=False, a=255):
        self.d.rectangle(self._s((x0, y0, x1 - 1 / SS, y1 - 1 / SS)), fill=tuple(col) + (a,))
        self.m.rectangle(self._s((x0, y0, x1 - 1 / SS, y1 - 1 / SS)), fill=255 if steel else 0)

    def poly(self, pts, col, steel=False, a=255):
        p = [tuple(self._s(q)) for q in pts]
        self.d.polygon(p, fill=tuple(col) + (a,))
        self.m.polygon(p, fill=255 if steel else 0)

    def line(self, x0, y0, x1, y1, w, col, steel=False, a=255):
        self.d.line(self._s((x0, y0, x1, y1)), fill=tuple(col) + (a,), width=max(1, round(w * SS)))
        self.m.line(self._s((x0, y0, x1, y1)), fill=255 if steel else 0, width=max(1, round(w * SS)))

    def dot(self, x, y, r, col, steel=False):
        self.d.ellipse(self._s((x - r, y - r, x + r, y + r)), fill=tuple(col) + (255,))
        self.m.ellipse(self._s((x - r, y - r, x + r, y + r)), fill=255 if steel else 0)

    def shade(self, x0, y0, x1, y1, a):
        """A translucent dark wash (cast shadow) over what is there; mask unchanged."""
        sh = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle(self._s((x0, y0, x1, y1)), fill=(0, 0, 0, a))
        self.im = Image.alpha_composite(self.im, sh)
        self.d = ImageDraw.Draw(self.im)

    def shade_line(self, x0, y0, x1, y1, w, a):
        sh = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).line(self._s((x0, y0, x1, y1)), fill=(0, 0, 0, a), width=round(w * SS))
        sh = sh.filter(ImageFilter.GaussianBlur(SS * 1.5))
        self.im = Image.alpha_composite(self.im, sh)
        self.d = ImageDraw.Draw(self.im)

    def noise(self, x0, y0, x1, y1, amp, seed, grain=1):
        """Low-amplitude texture over an opaque region (cement, paving, plank grain)."""
        a = np.asarray(self.im, np.float32)
        r0, r1, c0, c1 = round(y0 * SS), round(y1 * SS), round(x0 * SS), round(x1 * SS)
        rng = np.random.default_rng(seed)
        h, w = r1 - r0, c1 - c0
        g = max(1, round(grain * SS))
        n = rng.normal(0, amp, (h // g + 2, w // g + 2, 1))
        n = np.kron(n, np.ones((g, g, 1)))[:h, :w]
        reg = a[r0:r1, c0:c1]
        reg[..., :3] = np.clip(reg[..., :3] + n, 0, 255)
        self.im = Image.fromarray(a.astype(np.uint8), "RGBA")
        self.d = ImageDraw.Draw(self.im)

    def done(self):
        a = np.asarray(self.im, np.float32) / 255
        out = BDA.premul_resize(a, (N, N))
        im = Image.fromarray((out * 255 + .5).astype(np.uint8), "RGBA")
        mk = self.mk.resize((N, N), Image.LANCZOS)
        mask = Image.merge("RGBA", (mk, Image.new("L", (N, N), 0), Image.new("L", (N, N), 0), Image.new("L", (N, N), 255)))
        return im, mask


# ---- decks ------------------------------------------------------------------------------------------------------------
def _mirror_x(p: Pic, draw_band):
    """Draw a side band on the west, then the same band mirrored on the east."""
    draw_band(p, lambda x: x)
    draw_band(p, lambda x: N - x)


def _planks(p: Pic, seed):
    rng = np.random.default_rng(seed)
    for i in range(8):
        y0 = i * 32
        t = rng.uniform(-10, 10)
        col = tuple(int(np.clip(c + t, 0, 255)) for c in WOOD)
        p.rect(BAND, y0, N - BAND, y0 + 32, col)
        p.rect(BAND, y0, N - BAND, y0 + 2, WOOD_GAP)
        for k in range(3):       # grain
            yy = y0 + 7 + k * 8 + rng.uniform(-2, 2)
            p.line(BAND, yy, N - BAND, yy + rng.uniform(-1.5, 1.5), 1.2, WOOD_DK, a=150)
        for xx in (52, 128, N - 52):      # bolts into the floor beams
            p.dot(xx, y0 + 10, 1.8, STEEL_DK, True)
            p.dot(xx, y0 + 24, 1.8, STEEL_DK, True)
    p.noise(BAND, 0, N - BAND, N, 5, seed + 1, grain=2)


def _grating(p: Pic, col, hi, edge):
    """Open steel bar grating: bearing bars across the run every 8 px on cross bars every 32 px; the gaps are open."""
    for x in range(BAND, N - BAND, 32):
        p.rect(x, 0, x + 4, N, edge, True)
        p.rect(x + 1, 0, x + 3, N, col, True)
    for y in range(0, N, 8):
        p.rect(BAND, y, N - BAND, y + 3, edge, True)
        p.rect(BAND, y, N - BAND, y + 2, hi, True)


def _steel_band(p: Pic, X):
    """West band of the steel deck (X maps a west x to this side): stringer, rail posts, pipe handrail, hangers, cable."""
    def r(x0, y0, x1, y1, col, a=255):
        p.rect(min(X(x0), X(x1)), y0, max(X(x0), X(x1)), y1, col, True, a)
    r(20, 0, 28, N, STEEL_EDGE)              # edge stringer (a channel seen from above)
    r(21, 0, 27, N, STEEL)
    r(22, 0, 24, N, STEEL_HI)
    for y in (16, 80, 144, 208):             # I-section rail posts
        r(12, y - 5, 22, y + 5, STEEL_EDGE)
        r(12, y - 5, 22, y - 3, STEEL)
        r(12, y + 3, 22, y + 5, STEEL)
        r(16, y - 3, 18, y + 3, STEEL)
    r(14, 0, 20, N, STEEL_EDGE)              # pipe handrail
    r(15, 0, 19, N, STEEL)
    r(16, 0, 17.5, N, STEEL_HI)
    for y in range(0, N, 32):                # hanger rods: cable down to the stringer
        y0 = y + 16
        p.line(X(5.5), y0, X(20), y0 + 2, 3.0, STEEL_EDGE, True)
        p.line(X(5.5), y0, X(20), y0 + 2, 1.4, STEEL_HI, True)
        p.dot(X(5.5), y0, 3.2, STEEL_DK, True)
    r(1, 0, 10, N, STEEL_EDGE)               # main cable, bold enough to read at play zoom (a twist every 4 px)
    r(2.5, 0, 8.5, N, CABLE)
    for y in range(0, N, 4):
        p.line(X(3.5), y, X(7.5), y + 3, 0.9, CABLE_HI, True)


def steel_deck(grated=False):
    p = Pic()
    if grated:
        _grating(p, STEEL, STEEL_HI, STEEL_EDGE)
    else:
        _planks(p, 11)
    _mirror_x(p, _steel_band)
    return p.done()


def _truss_band(p: Pic, X):
    """West band of the heavy deck: the through truss's top chord with its gusset plates, seen from above."""
    def r(x0, y0, x1, y1, col, steel=True, a=255):
        p.rect(min(X(x0), X(x1)), y0, max(X(x0), X(x1)), y1, col, steel, a)
    r(25, 0, 28, N, CEMENT_EDGE, False)      # the paving's kerb under the chord
    r(2, 0, 26, N, HVY_EDGE)                 # top chord: a riveted box girder
    r(3, 0, 25, N, HVY)
    r(4, 0, 24, 3, HVY_DK)
    r(5, 0, 8, N, HVY_HI)                    # flange highlights
    r(19, 0, 21, N, HVY_DK)
    for y in range(4, N, 10):                # rivet rows
        p.dot(X(6.5), y, 1.1, HVY_DK, True)
        p.dot(X(20), y, 1.1, HVY_DK, True)
    for yc in (0, 128, 256):                 # gusset plates at the panel points (vertical post caps)
        r(0, yc - 14, 28, yc + 14, HVY_EDGE)
        r(1, yc - 13, 27, yc + 13, HVY_HI)
        r(2, yc - 12, 26, yc + 12, HVY)
        for dy in (-8, 0, 8):
            for dx in (6, 14, 22):
                p.dot(X(dx), yc + dy, 1.3, HVY_DK, True)


def heavy_deck(grated=False):
    p = Pic()
    if grated:
        _grating(p, HVY, HVY_HI, HVY_EDGE)
    else:
        p.rect(BAND, 0, N - BAND, N, PAVE)
        p.noise(BAND, 0, N - BAND, N, 7, 21, grain=1)
        p.noise(BAND, 0, N - BAND, N, 4, 22, grain=6)
        p.rect(BAND, 126, N - BAND, 130, (112, 112, 110))         # a slab joint at mid panel
    # the truss walls stand tall beside the road: their shadow and dark inner face (atlas shows the surface from x 38)
    p.shade(38, 0, 50, N, 95)
    p.shade(N - 50, 0, N - 38, N, 95)
    # overhead floor strut at the panel point (the tile seam: half on each end so tiling makes one strut)
    for (y0, y1) in ((0, 6), (N - 6, N)):
        p.rect(BAND - 2, y0, N - BAND + 2, y1, HVY_EDGE, True)
        p.rect(BAND - 2, y0 + (1 if y0 == 0 else 0), N - BAND + 2, y1 - (0 if y0 == 0 else 1), HVY, True)
    if not grated:
        p.shade(BAND, 6, N - BAND, 16, 70)                         # the strut's shadow on the road
        p.shade_line(BAND + 8, 10, N - BAND + 8, N + 10, 7, 90)    # the bracing's shadows (sun to the south-east)
        p.shade_line(N - BAND + 8, 10, BAND + 8, N + 10, 7, 90)
    # overhead X lateral bracing (angle irons) between the two top chords, across the road
    for (a, b) in (((BAND - 2, 2), (N - BAND + 2, N - 2)), ((N - BAND + 2, 2), (BAND - 2, N - 2))):
        p.line(*a, *b, 5, HVY_EDGE, True)
        p.line(*a, *b, 3, HVY, True)
        p.line(a[0], a[1] - 1, b[0], b[1] - 1, 1.5, HVY_HI, True)
    p.rect(121, 121, 135, 135, HVY_EDGE, True)                     # the bracing's centre plate
    p.rect(123, 123, 133, 133, HVY_HI, True)
    _mirror_x(p, _truss_band)
    return p.done()


# ---- anchors ----------------------------------------------------------------------------------------------------------
# facing = the side the deck is on (the anchor's Rotation.FacingCell); west mirrors east. Lateral positions match the
# deck band: the cable at 5.5 px from the edge, the posts/chord centred at 14 px.
def _slab(p, x0, y0, x1, y1, face, seed, col=CEMENT):
    """A cement block seen from above-south: its top, and its south face `face` px tall below it."""
    p.rect(x0, y0, x1, y1 + face, CEMENT_EDGE)
    p.rect(x0 + 1, y0 + 1, x1 - 1, y1, col)
    p.rect(x0 + 1, y1, x1 - 1, y1 + face - 1, CEMENT_FACE)
    p.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 3, (196, 194, 188))
    p.noise(x0 + 1, y0 + 1, x1 - 1, y1 + face - 1, 6, seed, grain=1)


def _ibeam_post(p, x0, x1, y_top, y_base, col=STEEL, hi=STEEL_HI, dk=STEEL_DK, edge=STEEL_EDGE):
    """A steel I-beam post seen face-on: two flanges and the web between them."""
    p.rect(x0, y_top, x1, y_base, edge, True)
    w = x1 - x0
    p.rect(x0 + 1, y_top + 1, x0 + w * .3, y_base - 1, col, True)
    p.rect(x1 - w * .3, y_top + 1, x1 - 1, y_base - 1, col, True)
    p.rect(x0 + w * .3, y_top + 1, x1 - w * .3, y_base - 1, dk, True)
    p.rect(x0 + 1.5, y_top + 1, x0 + 3, y_base - 1, hi, True)
    p.rect(x0 - 2, y_base - 5, x1 + 2, y_base, edge, True)          # base plate
    p.rect(x0 - 1, y_base - 4, x1 + 1, y_base - 1, dk, True)


def _cable(p, x0, y0, x1, y1, w=3.2):
    p.line(x0, y0, x1, y1, w + 1.6, STEEL_EDGE, True)
    p.line(x0, y0, x1, y1, w, CABLE, True)
    p.line(x0, y0, x1, y1, w * .35, CABLE_HI, True)


def _ground_block(p, cx, cy):
    _slab(p, cx - 13, cy - 10, cx + 13, cy + 8, 6, int(cx * 7 + cy))
    p.rect(cx - 5, cy - 4, cx + 5, cy + 4, STEEL_EDGE, True)            # the cable's eye plate
    p.rect(cx - 4, cy - 3, cx + 4, cy + 3, STEEL, True)
    p.dot(cx, cy, 1.8, STEEL_EDGE, True)


def _tower_face(p, y_top, y_mid, y_base):
    """The tower face-on: posts at lateral 14 / 242, a top tie, a middle tie and the X brace between them."""
    for (ya, yb) in ((y_top + 2, y_top + 14), (y_mid, y_mid + 9)):    # the ties' shadows, cast well south: overhead
        p.shade(28, ya + 34, N - 20, yb + 34, 75)
    for (x0, x1) in ((6, 22), (N - 22, N - 6)):
        _ibeam_post(p, x0, x1, y_top, y_base)
    for (ya, yb) in ((y_top + 2, y_top + 14), (y_mid, y_mid + 9)):    # ties (I-beams on their side)
        p.rect(20, ya, N - 20, yb, STEEL_EDGE, True)
        p.rect(20, ya + 1, N - 20, ya + 3, STEEL, True)
        p.rect(20, yb - 3, N - 20, yb - 1, STEEL, True)
        p.rect(20, ya + 3, N - 20, yb - 3, STEEL_DK, True)
        p.rect(20, ya + 1, N - 20, ya + 2, STEEL_HI, True)
    for (a, b) in (((22, y_top + 14), (N - 22, y_mid)), ((N - 22, y_top + 14), (22, y_mid))):
        p.line(*a, *b, 6, STEEL_EDGE, True)
        p.line(*a, *b, 3.6, STEEL, True)
    p.dot(128, (y_top + 14 + y_mid) / 2, 5, STEEL_EDGE, True)
    p.dot(128, (y_top + 14 + y_mid) / 2, 3.5, STEEL_HI, True)
    for x in (14, N - 14):                                             # saddles on the post tops
        p.rect(x - 7, y_top - 6, x + 7, y_top + 2, STEEL_EDGE, True)
        p.rect(x - 6, y_top - 5, x + 6, y_top + 1, STEEL_HI, True)


def steel_anchor(facing):
    p = Pic()
    if facing == "south":           # deck below: the tower stands at the south end, backstays run north to the blocks
        _slab(p, 10, 58, N - 10, 232, 18, 31)
        for x in (40, N - 40):
            _ground_block(p, x, 26)
        y_top, y_mid, y_base = 92, 168, 240
        for x, gx in ((14, 40), (N - 14, N - 40)):
            p.shade_line(x + 6, y_base, gx + 6, 30, 4, 70)
        _tower_face(p, y_top, y_mid, y_base)
        for x, gx in ((14, 40), (N - 14, N - 40)):
            _cable(p, x, y_top - 2, gx, 26)                            # backstay
            dx = 5.5 if x < 128 else N - 5.5
            _cable(p, x, y_top - 2, dx, N)                             # main cable onto the deck band
    elif facing == "north":         # deck above: the tower at the north end, backstays run south to the blocks
        _slab(p, 10, 4, N - 10, 196, 18, 32)
        for x in (40, N - 40):
            _ground_block(p, x, 230)
        y_top, y_mid, y_base = 22, 98, 168
        for x, gx in ((14, 40), (N - 14, N - 40)):
            p.shade_line(x + 6, y_base, gx + 6, 234, 4, 70)
        _tower_face(p, y_top, y_mid, y_base)
        for x, gx in ((14, 40), (N - 14, N - 40)):
            _cable(p, x, y_top - 2, gx, 230)
            dx = 5.5 if x < 128 else N - 5.5
            _cable(p, x, y_top - 2, dx, 0)
    elif facing == "east":          # deck to the right: posts from above at the east end, the tie overhead across the deck
        _slab(p, 4, 8, N, 236, 16, 33)
        for y in (40, N - 40):
            _ground_block(p, 28, y)
        p.shade(206, 26, 222, N - 2, 80)                               # the overhead tie's shadow (sun to the south-east)
        p.rect(194, 14, 208, N - 14, STEEL_EDGE, True)                 # top tie, from above (an I-beam's top flange)
        p.rect(195, 14, 207, N - 14, STEEL, True)
        p.rect(196, 14, 198, N - 14, STEEL_HI, True)
        p.line(201, 30, 201, N - 30, 1.2, STEEL_DK, True)
        for y in (14, N - 14):                                         # the posts from above: I sections with a saddle
            p.rect(190, y - 9, 212, y + 9, STEEL_EDGE, True)
            p.rect(191, y - 8, 211, y - 4, STEEL, True)
            p.rect(191, y + 4, 211, y + 8, STEEL, True)
            p.rect(199, y - 4, 203, y + 4, STEEL_DK, True)
            p.rect(193, y - 6, 209, y - 5, STEEL_HI, True)
        for y, gy in ((14, 40), (N - 14, N - 40)):
            _cable(p, 196, y, 28, gy)                                  # backstays
            dy = 5.5 if y < 128 else N - 5.5
            _cable(p, 206, y, N, dy)                                   # main cable onto the deck band
    else:
        raise ValueError(facing)
    return p.done()


def _portal_face(p, y_top, y_base):
    """The truss portal face-on: two heavy end posts and a latticed portal strut with knee braces. No cables."""
    p.shade(30, y_top + 44, N - 18, y_top + 74, 80)                  # the portal strut's shadow: it is overhead
    for (x0, x1) in ((2, 26), (N - 26, N - 2)):
        _ibeam_post(p, x0, x1, y_top, y_base, HVY, HVY_HI, HVY_DK, HVY_EDGE)
        for y in range(y_top + 6, y_base - 6, 9):
            p.dot(x0 + 4, y, 1.2, HVY_DK, True)
            p.dot(x1 - 4, y, 1.2, HVY_DK, True)
    yb = y_top + 30
    p.rect(24, y_top, N - 24, yb, HVY_EDGE, True)                     # portal strut: two chords and a lattice
    p.rect(24, y_top + 1, N - 24, y_top + 6, HVY, True)
    p.rect(24, y_top + 1, N - 24, y_top + 2.5, HVY_HI, True)
    p.rect(24, yb - 6, N - 24, yb - 1, HVY, True)
    p.rect(24, y_top + 6, N - 24, yb - 6, CEMENT_FACE)            # the abutment seen through the lattice
    for x in range(24, N - 24, 26):
        p.line(x, y_top + 6, x + 26, yb - 6, 3.2, HVY_EDGE, True)
        p.line(x + 26, y_top + 6, x, yb - 6, 3.2, HVY_EDGE, True)
        p.line(x, y_top + 6, x + 26, yb - 6, 1.8, HVY, True)
        p.line(x + 26, y_top + 6, x, yb - 6, 1.8, HVY, True)
    for (x0, s) in ((26, 1), (N - 26, -1)):                             # knee braces
        p.poly([(x0, yb), (x0 + s * 30, yb), (x0, yb + 30)], HVY_EDGE, True)
        p.poly([(x0, yb + 2), (x0 + s * 24, yb + 2), (x0, yb + 26)], HVY, True)
        p.dot(x0 + s * 8, yb + 8, 1.4, HVY_DK, True)


def _approach(p, x0, y0, x1, y1, vertical, seed):
    """The paved approach on the abutment with a low steel rail along each side."""
    p.rect(x0, y0, x1, y1, PAVE)
    p.noise(x0, y0, x1, y1, 7, seed, grain=1)
    if vertical:
        for xr in (x0 + 2, x1 - 6):
            p.rect(xr, y0, xr + 4, y1, STEEL_EDGE, True)
            p.rect(xr + 1, y0, xr + 3, y1, HVY_HI, True)
            for y in range(int(y0) + 8, int(y1), 32):
                p.rect(xr - 1, y - 3, xr + 5, y + 3, HVY_EDGE, True)
    else:
        for yr in (y0 + 2, y1 - 6):
            p.rect(x0, yr, x1, yr + 4, STEEL_EDGE, True)
            p.rect(x0, yr + 1, x1, yr + 3, HVY_HI, True)
            for x in range(int(x0) + 8, int(x1), 32):
                p.rect(x - 3, yr - 1, x + 3, yr + 5, HVY_EDGE, True)


def _bearing(p, cx, cy):
    p.rect(cx - 12, cy - 8, cx + 12, cy + 8, HVY_EDGE, True)
    p.rect(cx - 11, cy - 7, cx + 11, cy + 7, HVY, True)
    p.rect(cx - 11, cy - 7, cx + 11, cy - 5, HVY_HI, True)
    for dx in (-7, 7):
        p.dot(cx + dx, cy, 1.6, HVY_DK, True)


def heavy_anchor(facing):
    p = Pic()
    if facing == "south":
        _slab(p, 2, 30, N - 2, 226, 26, 41)
        for y in range(236, 250, 6):                                    # formwork lines in the face
            p.line(4, y, N - 4, y, 1, CEMENT_EDGE, a=120)
        _approach(p, 28, 34, N - 28, 226, True, 42)
        for x in (14, N - 14):
            _bearing(p, x, 214)
        _portal_face(p, 100, 222)
    elif facing == "north":
        _slab(p, 2, 2, N - 2, 200, 26, 43)
        for y in range(210, 224, 6):
            p.line(4, y, N - 4, y, 1, CEMENT_EDGE, a=120)
        _approach(p, 28, 2, N - 28, 196, True, 44)
        for x in (14, N - 14):
            _bearing(p, x, 16)
        _portal_face(p, 14, 136)
    elif facing == "east":
        _slab(p, 2, 4, N, 228, 24, 45)
        _approach(p, 2, 26, N, 230, False, 46)
        p.shade(218, 20, 236, N - 6, 80)
        for y in (14, N - 14):                                         # the end posts from above, on their bearings
            _bearing(p, 226, y)
            p.rect(212, y - 12, 240, y + 12, HVY_EDGE, True)
            p.rect(213, y - 11, 239, y + 11, HVY, True)
            p.rect(215, y - 9, 237, y - 7, HVY_HI, True)
            for dy in (-4, 4):
                for dx in (218, 226, 234):
                    p.dot(dx, y + dy, 1.3, HVY_DK, True)
        p.rect(214, 26, 238, N - 26, HVY_EDGE, True)                   # the portal strut overhead, latticed
        p.rect(215, 26, 237, N - 26, CEMENT_FACE)
        p.rect(215, 26, 219, N - 26, HVY, True)
        p.rect(233, 26, 237, N - 26, HVY, True)
        for y in range(26, N - 26, 26):
            p.line(219, y, 233, y + 26, 2.6, HVY, True)
            p.line(233, y, 219, y + 26, 2.6, HVY, True)
    else:
        raise ValueError(facing)
    return p.done()


# ---- the set ----------------------------------------------------------------------------------------------------------
FACINGS = ("south", "east", "north")


def pieces():
    """{texture rel path (no .png): (picture, mask)} for every piece this redesign replaces in the base set."""
    out = {
        f"{THINGS}/RM_SuspensionDeck_Steel": steel_deck(False),
        f"{THINGS}/RM_SuspensionDeck_SteelGrated": steel_deck(True),
        f"{THINGS}/RM_SuspensionDeck_Heavy": heavy_deck(False),
        f"{THINGS}/RM_SuspensionDeck_HeavyGrated": heavy_deck(True),
    }
    for f in FACINGS:
        out[f"{THINGS}/RM_SuspensionAnchor_Steel_{f}"] = steel_anchor(f)
        out[f"{THINGS}/RM_SuspensionAnchor_Heavy_{f}"] = heavy_anchor(f)
    return out


def atlases(pcs, tmp):
    """{atlas rel path: (atlas, mask atlas)} for the four decks, built exactly as build_deck_atlas builds the installed ones."""
    out = {}
    tmp = Path(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    for rel, (im, mk) in pcs.items():
        if "/RM_SuspensionDeck_" not in rel:
            continue
        a = tmp / (Path(rel).name + ".png")
        b = tmp / (Path(rel).name + "_m.png")
        im.save(a)
        mk.save(b)
        atlas = BDA.build(a, BAND)
        matlas = BDA.build(b, BAND)
        ma = np.asarray(matlas).copy()
        ma[..., 1:3] = 0
        ma[..., 3] = 255
        out[rel + "_Atlas"] = (atlas, Image.fromarray(ma, "RGBA"))
    return out


# ---- checks -----------------------------------------------------------------------------------------------------------
def red_share(im, alpha_min=ALPHA_MIN):
    """Share of opaque pixels in the red band (hue within RED_DEG of red, sat > RED_SAT, value > VAL_MIN)."""
    a = np.asarray(im.convert("RGBA"), np.float32) / 255
    op = a[..., 3] >= alpha_min / 255
    if not op.any():
        return 0.0
    rgb = a[..., :3][op]
    mx, mn = rgb.max(1), rgb.min(1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    red = (mx > VAL_MIN) & (s > RED_SAT) & (np.minimum(h, 360 - h) < RED_DEG)
    return float(red.mean())


def no_red(im):
    return red_share(im) <= MAX_RED_SHARE


def structure(im, size=64):
    """The picture's light-and-dark structure with colour thrown away: luminance over a neutral backdrop, blurred, edges."""
    a = np.asarray(im.convert("RGBA").resize((size, size), Image.BOX), np.float32) / 255
    lum = (a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114) * a[..., 3] + .5 * (1 - a[..., 3])
    gy, gx = np.gradient(lum)
    return np.hypot(gx, gy).ravel(), lum.ravel()


def structural_similarity(a, b):
    """Pearson correlation of two pictures' edge maps (1 = the same drawing, whatever the colours)."""
    ea, _ = structure(a)
    eb, _ = structure(b)
    ea, eb = ea - ea.mean(), eb - eb.mean()
    den = np.sqrt((ea * ea).sum() * (eb * eb).sum())
    return float((ea * eb).sum() / den) if den > 0 else 1.0


SAME_DRAWING = 0.80    # edge-map correlation at or above this = one drawing recoloured (hue shift), not a distinct design


def distinct(a, b):
    return structural_similarity(a, b) < SAME_DRAWING


def mask_ok(im, mk):
    """A paint mask: same size as its picture, red only where the picture is opaque, some steel and some non-steel."""
    if im.size != mk.size:
        return False
    a = np.asarray(im.convert("RGBA"))[..., 3]
    r = np.asarray(mk.convert("RGBA"))[..., 0]
    steel = r > 128
    return bool(steel.any()) and bool((steel & (a < 8)).sum() <= steel.sum() * 0.02)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        raise SystemExit(__doc__)
    out = Path(argv[0])
    pcs = pieces()
    allp = dict(pcs)
    allp.update(atlases(pcs, out / "_atlas_src"))
    for rel, (im, mk) in allp.items():
        f = out / (rel + ".png")
        f.parent.mkdir(parents=True, exist_ok=True)
        im.save(f)
        mk.save(out / (rel + "_m.png"))
        print("%-80s red %.4f %s" % (rel, red_share(im), "ok" if no_red(im) else "RED"))


if __name__ == "__main__":
    main()
