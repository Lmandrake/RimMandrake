"""Backdrops for the jetty and bridge mockups, cut from the owner's own walk capture of 2026-11-22 (stations 59-60, his full
mod list, about 115 px per cell): a clean 4x3 dry pit (the right half of station 59's pit, mirrored over the jetty), the
same pit turned north/south by splicing (never rotated: the lit north face stays north), and plain ground tiled around it.
RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD."""
from PIL import Image, ImageFilter
import numpy as np

CAPTURE = "/mnt/d/ClaudeWork/rimmandrake/conductor/walk_20261122/flowworks_walk/stations59_60_jetties_two_squares_wood.png"
PIT_INNER = (220, 88, 676, 426)       # inside station 59's black station frame (frame 215-219 / 676-679, 83-87 / 428-432)
GROUND = (690, 60, 1015, 444)        # bare ground between the two stations (station 60's anchor starts at x 1030)


def _cap():
    return Image.open(CAPTURE).convert("RGB")


def pit_ew(ppc):
    """The 4-long, 3-wide pit as an east/west bridge or jetty crosses it: (4*ppc, 3*ppc) RGB."""
    a = np.asarray(_cap().crop(PIT_INNER)).copy()
    w = a.shape[1]
    half = a[:, w // 2:]
    a[:, :w - w // 2] = half[:, ::-1][:, :w - w // 2]
    return Image.fromarray(a).resize((4 * ppc, 3 * ppc), Image.LANCZOS)


def pit_ns(ppc):
    """The same pit 3 wide and 4 long, for a north/south crossing: (3*ppc, 4*ppc). Spliced from pit_ew: its west 1.5 and
    east 1.5 cells side by side, then its north 1.5 and south 1.5 rows with one interior row repeated between them."""
    e = np.asarray(pit_ew(ppc))
    h = int(1.5 * ppc)
    narrow = np.concatenate([e[:, :h], e[:, -h:]], axis=1)                 # 3 cells wide, 3 tall
    mid = narrow[int(1.25 * ppc):int(1.75 * ppc)]                          # half a cell of plain interior
    tall = np.concatenate([narrow[:h], mid, mid, narrow[-h:]], axis=0)     # 4 tall
    return Image.fromarray(tall)


def ground(w, h):
    """Plain ground of any size, tiled from the capture with mirrored tiles so no seam shows."""
    g = np.asarray(_cap().crop(GROUND))
    tile = np.concatenate([np.concatenate([g, g[:, ::-1]], 1), np.concatenate([g[::-1], g[::-1, ::-1]], 1)], 0)
    reps = (h // tile.shape[0] + 1, w // tile.shape[1] + 1, 1)
    return Image.fromarray(np.tile(tile, reps)[:h, :w])


def scene(cols, rows, pit_at, ns, ppc):
    """Ground of cols x rows cells with the pit pasted at cell pit_at (col, row). Returns RGBA."""
    img = ground(cols * ppc, rows * ppc).convert("RGBA")
    pit = pit_ns(ppc) if ns else pit_ew(ppc)
    img.paste(pit.convert("RGBA"), (pit_at[0] * ppc, pit_at[1] * ppc))
    return img
