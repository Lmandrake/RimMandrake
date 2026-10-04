"""shader_sway_look.py -- does the OPTIONAL CutoutPlant shader sway visibly move a hanging cord? (2026-10-04)

Evidence tool, NOT a Northstar bar (bars are state reads: validation.py B7b_sway_shader_path proves the shader's
INPUTS -- CutoutPlant material, WindManager registration, _SwayHead advancing, vertex alpha 0 at the pin and under a
roof). What a state read cannot see is the GPU displacement itself, so this takes OS-level captures (the bridge's
own screenshot renders a separate camera pass that skips per-frame Graphics.DrawMesh) of the WALL2 hanging tail
left by `validation.py --live`, two captures N ticks apart per mode, and counts changed pixels:

    off            sway=False                 noise baseline (must be ~0 or the frame is not still)
    cpu            swayMode=CPU               method control (must move, or the capture cannot see motion)
    shader         swayMode=Shader            the question
    shader_roofed  Shader + roof over the tail must NOT move (alpha 0 under a roof)

    python.exe src/RimMandrake/MessyConduit/shader_sway_look.py [--x0 150 --z0 150] [--out Transient/...]

Run from the repo root (python.exe misreads WSL absolute paths), after `validation.py --live`, game in front.
MEASURED 2026-10-04 (rootSize 11, swayAmplitude 2, wind 0.34, 20 ticks between captures, 340 px box): changed px
off 0/0, cpu 13/2, shader 25/23, shader_roofed 0/0 -- the changed pixels sit ON the hanging tail (look_sheet.png),
so the CutoutPlant route DOES move the cord on screen, along screen x (the tail hangs along z, so it reads as a
sideways swing), and a roof stops it. Magnitude is ~1-2 px at that zoom, about the CPU route's. Shipping default
stays CPU (owner card: shader is optional); Shader falls back to CPU by itself when the material is unregistered.
LEARNED: the WALL2 terminal must be DEAD for this (battery 2 at 0%): a live wall terminal throws sparks and a
glow every tick, which would be counted as motion in every mode.
"""
import argparse
import ctypes
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402


def grab(path):
    from PIL import ImageGrab
    im = ImageGrab.grab(all_screens=True)
    im.save(path)
    return im


CROP = None


def game_crop(half=170):
    """A box of +-half px around the centre of the RimWorld window (the camera is centred on the tail)."""
    from ctypes import wintypes
    h = ctypes.windll.user32.FindWindowW(None, "RimWorld by Ludeon Studios")
    r = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(h, ctypes.byref(r))
    cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
    return (cx - half, cy - half, cx + half, cy + half), (r.left, r.top, r.right, r.bottom)


def changed(a, b, thr=24):
    from PIL import ImageChops
    if CROP:
        a, b = a.crop(CROP), b.crop(CROP)
    d = ImageChops.difference(a.convert("RGB"), b.convert("RGB")).convert("L")
    hist = d.histogram()
    return sum(hist[thr:]), d.getbbox()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x0", type=int, default=150)
    ap.add_argument("--z0", type=int, default=150)
    ap.add_argument("--ticks", type=int, default=20)
    ap.add_argument("--out", default=os.path.join("Transient", "mc_shader_sway_look_20261004"))
    a = ap.parse_args()
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:  # noqa: BLE001
        pass
    os.makedirs(a.out, exist_ok=True)
    B = V.Bridge()
    X0, Z0 = a.x0, a.z0
    tail = (X0 + 24, Z0 + 7, 3, 4)                   # west face of WALL2 (x = X0+26), the tail hangs screen-down
    roof = (X0 + 23, Z0 + 7, 5, 5)
    # the WALL2 terminal dead: no sparks / glow in frame
    bats = B.call("jawa/list_things", defName="Battery", limit=10).get("things") or []
    for t in bats:
        B.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=0.0)
    B.ticks(260)
    # LEARNED run 1: rootSize 3 is below the engine's minimum and the whole-screen diff counted the owner's
    # terminals and the map's swaying grass (~2.4k px of noise in EVERY mode): centre on the tail, zoom to the
    # minimum, and count only a box around the game window's centre
    B.call("rimworld/frame_cell_rect", x=X0 + 25, z=Z0 + 8, width=2, height=2, paddingCells=0)
    B.call("rimworld/set_camera_zoom", rootSize=11)
    global CROP
    CROP, win = game_crop()
    B.probe("set:swayAmplitude=2")
    out = {"tail": tail, "ticks": a.ticks, "crop": CROP, "window": win, "camera": B.call("rimworld/get_camera_state"), "swayAmplitude": 2}
    modes = [("off", ["set:sway=False"]), ("cpu", ["set:sway=True", "set:swayMode=CPU"]),
             ("shader", ["set:swayMode=Shader"]), ("shader_roofed", ["set:swayMode=Shader"])]
    for name, cmds in modes:
        if name == "shader_roofed":
            B.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,%d,%d" % roof)
            B.ticks(2)
        for c in cmds:
            B.probe(c)
        time.sleep(1.5)
        m = B.probe("motion")
        im_a = grab(os.path.join(a.out, name + "_a.png"))
        B.ticks(a.ticks)
        time.sleep(1.0)
        im_b = grab(os.path.join(a.out, name + "_b.png"))
        B.ticks(a.ticks)
        time.sleep(1.0)
        im_c = grab(os.path.join(a.out, name + "_c.png"))
        n_ab, bb_ab = changed(im_a, im_b)
        n_bc, bb_bc = changed(im_b, im_c)
        out[name] = {"changedPx_ab": n_ab, "bbox_ab": bb_ab, "changedPx_bc": n_bc, "bbox_bc": bb_bc,
                     "state": {k: m.get(k) for k in ("swayMode", "swayDraws", "shaderLiftedOpen", "shaderLiftedRoofed",
                                                     "shaderAlphaMaxOpen", "plantSwayHead", "windSpeed", "liveWallEnds")}}
        print(name, json.dumps(out[name]))
        if name == "shader_roofed":
            B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % roof)
    B.probe("defaults")
    for t in bats:
        B.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)
    B.ticks(2)
    with open(os.path.join(a.out, "result.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("->", os.path.join(a.out, "result.json"))


if __name__ == "__main__":
    main()
