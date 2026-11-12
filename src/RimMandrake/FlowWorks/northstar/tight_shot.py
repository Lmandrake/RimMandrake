"""tight_shot.py - a scene capture that is as tight as the engine allows, and says what zoom it really got.

RIMMANDRAKE_FIX_CAPTURE_ZOOM_WONT_TIGHTEN_ON_SCENES (measured 2026-11-12 on the Archmagi game): `rimworld/set_camera_zoom`
CLAMPS rootSize to the engine floor (8.0 on the 13-mod list; `sizeRange.min` of get_camera_state says 0.5 and is not the
floor). A caller asking for root=6.0 got 8.0 with success=true, logged 6.0, and its "tight" capture was the whole 16-cell
screen. Zoom itself works (root 38 -> 8 on the same camera tightens the frame ~4.7x). So:
  * apply_zoom reads the reply's applied rootSize back, so the log carries the truth, not the request;
  * crop_to_rect cuts the full-frame PNG to the wanted rect plus a margin, using the pixel scale the screen implies
    (screen height / (2 * rootSize) px per cell, camera centred on the rect), so a 5x5 look is a 5x5 picture at the
    floor zoom's resolution instead of a 25-cell field with the subject in the middle.
"""
import os


def apply_zoom(call, root):
    """Set the zoom; -> (applied rootSize, clamped?). `call(tool, **kw)` returns the reply dict."""
    r = call("rimworld/set_camera_zoom", rootSize=float(root))
    got = r.get("rootSize")
    if got is None:
        st = call("rimworld/get_camera_state")
        got = st.get("rootSize")
    got = float(got) if got is not None else float(root)
    return got, got - float(root) > 0.01


def crop_box(img_w, img_h, root, rect, margin_cells=1.0):
    """-> (left, top, right, bottom) pixels of rect (x, z, w, h cells) plus a margin, camera centred on the rect."""
    ppc = img_h / (2.0 * root)
    w_px = (rect[2] + 2 * margin_cells) * ppc
    h_px = (rect[3] + 2 * margin_cells) * ppc
    cx, cy = img_w / 2.0, img_h / 2.0
    l, t = max(0, int(round(cx - w_px / 2))), max(0, int(round(cy - h_px / 2)))
    r, b = min(img_w, int(round(cx + w_px / 2))), min(img_h, int(round(cy + h_px / 2)))
    return l, t, r, b


def crop_to_rect(src, dst, root, rect, margin_cells=1.0):
    """Write the tight crop of src to dst; -> the box, or None when PIL is missing or the rect fills the frame anyway."""
    try:
        from PIL import Image
    except ImportError:
        return None
    im = Image.open(src)
    box = crop_box(im.width, im.height, root, rect, margin_cells)
    if box == (0, 0, im.width, im.height):
        return None
    im.crop(box).save(dst)
    return box
