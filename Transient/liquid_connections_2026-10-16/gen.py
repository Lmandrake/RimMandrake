#!/usr/bin/env python3
"""gen.py -- HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY mockup art: per look, a heftier pump, a pipe-end flange stub and a
hose-to-pipe saddle coupler, each a codex edit from the look's reference (ref/<Look>_ref.png: that look's tank, reel
and today's pump). Runs every job in parallel, each with its own CODEX_HOME. Re-runnable: skips outputs that exist.
    python3 gen.py [piece ...]
"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

H = os.path.dirname(os.path.abspath(__file__))
CI = os.path.join(H, "../../skills/generating-images/scripts/codex_image.py")
LOOK = {
    "Scrapper": "rusted, riveted salvaged steel with patched plates, flaking orange rust, brass valve wheels and rope lashings, standing on a weathered wooden skid",
    "Industrial": "dark gunmetal-grey heavy steel with bold yellow-and-black hazard stripes, chunky hex bolts and a grey steel skid",
    "Modern": "glossy bright red enamel bodywork with polished silver-white fittings, clean bolts and a white steel base",
    "Futuristic": "glossy white panels with dark grey joints and thin glowing cyan accent lines, sleek and seamless, on a grey base plate",
}
CAMERA = ("Drawn from the SAME camera as the reference buildings: orthographic, about 35 degrees above the horizontal, top faces lit "
          "and fully visible, light from overhead-front, crisp painterly RimWorld-mod sprite style with a thin dark outline. ")
PIECES = {
    "pump": ("Using the attached image only as the style and palette reference (the tank and hose reel show the look; the small pump "
             "at the right is today's pump, which is far too puny), draw ONE new liquid pump as a single game sprite: a heavy, "
             "squat, powerful centrifugal pump station - a big electric motor block coupled to a large round volute pump casing, "
             "all bolted onto a solid skid, visibly as massive as the hose reel. On its LEFT side a large round inlet port ends "
             "in a flat bolted flange facing straight left, and on its RIGHT side an outlet port ends in a matching flat bolted "
             "flange facing straight right; both flanges are the same diameter, about one fifth of the pump's width, sized for a "
             "thick hose. Every fitting terminates flush with the body; nothing trails off. Material: {look}. " + CAMERA +
             "Centred, filling about 85 percent of the canvas width, on a fully transparent background."),
    "flange": ("Using the attached image only as the style and palette reference, draw ONE small pipe fitting as a single game "
               "sprite: a short straight length of rigid pipe running exactly horizontally from the left edge, ending at the "
               "right in a wide round bolted flange collar seen edge-on (a thick disc with a ring of bolt heads), the kind of "
               "flange where a pipe bolts onto the wall of a tank or pump. The pipe is a quarter of the canvas tall; the flange "
               "is about twice the pipe's diameter. Material: {look}. " + CAMERA +
               "On a fully transparent background, the pipe touching the left edge of the canvas."),
    "saddle": ("Using the attached image only as the style and palette reference, draw ONE pipe fitting as a single game sprite: "
               "a short straight section of rigid pipe running exactly horizontally across the whole canvas, with a sturdy "
               "clamped saddle coupler on top of its middle - a bolted band clamp around the pipe carrying a short round "
               "threaded hose spigot that points straight down-and-toward the viewer, where a flexible hose screws on. "
               "Material: {look}. " + CAMERA +
               "On a fully transparent background, the pipe touching both the left and right edges of the canvas."),
}


def job(look, piece):
    out = os.path.join(H, "raw", f"{look}_{piece}.png")
    if os.path.exists(out):
        return out, 0
    home = f"/mnt/d/Luke/dev/_codexhomes/hosejoints_{look}_{piece}"
    r = subprocess.run([sys.executable, CI, "edit", "--image", os.path.join(H, "ref", f"{look}_ref.png"), "--out", out,
                        "--prompt", PIECES[piece].format(look=LOOK[look]), "--codex-home", home, "--timeout", "900", "--model", "gpt-6.1-sol"],
                       capture_output=True, text=True)
    return out, r.returncode if os.path.exists(out) else (r.returncode or 1, (r.stderr or r.stdout)[-300:])


if __name__ == "__main__":
    pieces = sys.argv[1:] or list(PIECES)
    jobs = [(l, p) for p in pieces for l in LOOK]
    with ThreadPoolExecutor(len(jobs)) as ex:
        for res in ex.map(lambda a: job(*a), jobs):
            print(res, flush=True)
