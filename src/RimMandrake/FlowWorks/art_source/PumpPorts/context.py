"""Offline before/after context: pump (1x1) with a ground pipe running in under it from the west (atlas straight, girth
0.136 cell) and a flat hose coupled at the east port (Strand_Flat at 0.18 visible, Coupling_Bare at FittingSize 0.4376 cell,
brass face on the port point). OFFLINE composite, not a game capture."""
import sys
from PIL import Image, ImageDraw
T = '/home/mandrake/rm/bench/src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/'
UNDER = True
REACH = 0.299
def scene(pump_png, look, ppc, reach=None):
    global REACH
    if reach is not None: REACH = reach
    W, H = 4 * ppc, 2 * ppc                      # cells x in [-2, 2], z in [-1, 1]
    bg = Image.new('RGBA', (W, H), (176, 150, 112, 255))
    cx, cy = 2 * ppc, ppc
    # pipe: atlas straight E-W of tile (col 2,row 1)
    at = Image.open(T + f'Pipe/{look}/UniversalPipe_Atlas.png').convert('RGBA')
    tile = at.crop((352, 176, 528, 352))
    col = [tile.getpixel((80, y))[3] for y in range(176)]
    ys = [y for y, a in enumerate(col) if a > 128]; y0, y1 = ys[0], ys[-1] + 1
    band = tile.crop((0, y0 - 2, 176, y1 + 2))
    g = 0.136 * ppc / (y1 - y0)
    seg = band.resize((max(1, round(176 * g)), max(1, round(band.height * g))), Image.LANCZOS)
    x = 0
    while x < cx:
        bg.alpha_composite(seg.crop((0, 0, min(seg.width, cx - x), seg.height)), (x, cy - seg.height // 2)); x += seg.width
    # hose under-coupler beneath the pump at the east (hose) port: UnderCouplerGeometry collar 0.140625 x 0.3125, pipe 0.21875
    # wide from mid-collar to the reach (UnderCouplerReach.cs, 0.299 for the redrawn pumps); +u of the sprites points inward
    if UNDER:
        J = T + f'Joins/{look}/'
        port_x = cx + ppc // 2
        reach = REACH
        pl = reach - 0.140625 / 2
        up = Image.open(J + 'UnderPipe.png').convert('RGBA').transpose(Image.FLIP_LEFT_RIGHT)
        up = up.resize((max(1, round(pl * ppc)), round(0.21875 * ppc)), Image.LANCZOS)
        bg.alpha_composite(up, (round(port_x - reach * ppc), cy - up.height // 2))
        uc = Image.open(J + 'UnderCollar.png').convert('RGBA').transpose(Image.FLIP_LEFT_RIGHT)
        uc = uc.resize((round(0.140625 * ppc), round(0.3125 * ppc)), Image.LANCZOS)
        bg.alpha_composite(uc, (round(port_x - 0.140625 * ppc), cy - uc.height // 2))
    # pump
    pump = Image.open(pump_png).convert('RGBA').resize((ppc, ppc), Image.LANCZOS)
    bg.alpha_composite(pump, (cx - ppc // 2, cy - ppc // 2))
    # hose strand from x=+2 to the coupling's hose end
    hs = 'Hose/' if look == 'Scrapper' else f'Hose/Styles/{look}/'
    size = 0.4376
    face = cx + ppc // 2
    cpl_c = face + 0.46 * size * ppc        # flipped: the brass face (+0.46 size in the art) now on the -x side, on the port
    strand = Image.open(T + hs + 'Strand_Flat.png').convert('RGBA')
    sh = round(0.18 / (59 / 64) * ppc)
    sw = round(strand.width * sh / strand.height)
    sseg = strand.resize((sw, sh), Image.LANCZOS)
    x = int(face + 0.3 * size * ppc)
    while x < W:
        bg.alpha_composite(sseg.crop((0, 0, min(sw, W - x), sh)), (x, cy - sh // 2)); x += sw
    c = Image.open(T + hs + 'Coupling_Bare.png').convert('RGBA')
    cs = round(size * ppc)
    c = c.resize((cs, cs), Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)   # +X (face) toward the port (-x here)
    # snap: the coupling's first opaque column (its brass face) sits on the port point, as HoseMath.PortFitting aims it
    import numpy as _np
    fc = int(_np.where((_np.array(c)[:, :, 3] > 128).any(0))[0][0])
    bg.alpha_composite(c, (face - fc, cy - cs // 2))
    return bg
if __name__ == '__main__':
    pump, look, out = sys.argv[1:4]
    scene(pump, look, int(sys.argv[4]) if len(sys.argv) > 4 else 128).save(out)
