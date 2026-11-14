#!/usr/bin/env python3
"""art_maxzoom_probe.py -- is stored art resolution above 128 px/cell visible at the closest zoom a player reaches?

Item ART_RESOLUTION_MEASURE_AT_MAX_ZOOM. art_legibility.py resexp answered "no" at vanilla zoom only. The owner's
lists carry Camera+ (brrainz.cameraplus) at its defaults, whose closest zoom is far nearer than vanilla's
(Camera+ Settings.cs: zoomedInPercent 1 -> minimum rootSize 2, read 2026-10-23, Transient/live_batch_20261023
RESULTS_round2.md section 7). Two halves:

  sim   OFFLINE. A >=512 px sprite is stored at 128/256/512 px (LANCZOS, how a mod ships it) and drawn to a
        cell of P screen px the way the GPU does it (minify: box/mip; magnify: bilinear). Prints, per P, the mean
        absolute RGB difference of each stored copy against the 512 copy over the opaque body. --check exits 0
        only when the instrument behaves as measured live-round 2: 128 vs 512 below JND at 83 and 114 px/cell,
        above it at 456, and 256 nearer to 512 than 128 is there.
  live  LIVE (the bridge; run from WSL python3, the client runs under python.exe). Reads the running load
        (jawa/running_mods), asks the camera for a rootSize below any mod's floor, lets the camera driver clamp,
        reads the settled rootSize, shoots one frame for its height and computes px/cell = H / (2 * rootSize)
        (an orthographic camera shows 2*rootSize cells top to bottom). Restores the prior rootSize. Writes JSON
        and prints the verdict from the same simulation at the measured px/cell. Exit 0 = measured with a sane
        instrument (Camera+ in the running load, no rival camera mod, the clamp moved the request, a frame read),
        1 = not measured (the line says why).

px/cell is a measurement of the CAMERA; what the eye sees is the simulation at that px/cell. JND here is a mean
absolute difference of 2.0/255 over opaque pixels (a full-body blur reads at about that level; round 2 saw
<=0.3/255 where the copies were indistinguishable by eye).
"""
import argparse
import json
import os
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFAULT_SOURCES = (
    "src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Aurrok/RM_Aurrok_south.png",
    "src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Vhessk/Vhessk_south.png",
    "src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Megatardi/Megatardi_south.png",
)
STORED = (128, 256, 512)
VANILLA_PX, SCS_PX, CAMERAPLUS_PX = 83, 114, 456     # round 2: root 11 / root 8 / root 2 at a 1826-px render
JND = 2.0
CAMERAPLUS = "brrainz.cameraplus"
RIVAL_CAMERAS = ("ray1203.simplecamerasetting",)
REQUEST_ROOT = 0.5                                     # below every floor; the driver clamps it


def px_per_cell(screen_h, root):
    """Orthographic camera: the frame shows 2*rootSize cells top to bottom."""
    if not screen_h or not root or root <= 0:
        raise ValueError("screen height and rootSize must be positive (got %r, %r)" % (screen_h, root))
    return screen_h / (2.0 * root)


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("%s is not a PNG" % path)
    return struct.unpack(">II", head[16:24])


def draw_cell(stored, px):
    """A stored RGBA sprite drawn into px x px screen pixels as the GPU does: magnify bilinear; minify trilinear over
    a box-filtered mip chain (Unity's default for a mipmapped texture, which RimWorld's are)."""
    import numpy as np
    from PIL import Image
    if px >= stored.width:
        return np.asarray(stored.resize((px, px), Image.BILINEAR), dtype=float)
    import math
    level = math.log2(stored.width / px)
    lo = int(math.floor(level))
    mips = [stored]
    while len(mips) <= lo + 1 and mips[-1].width > 1:
        m = mips[-1]
        mips.append(m.resize((max(1, m.width // 2), max(1, m.height // 2)), Image.BOX))
    a = np.asarray(mips[lo].resize((px, px), Image.BILINEAR), dtype=float)
    if lo + 1 >= len(mips):
        return a
    b = np.asarray(mips[lo + 1].resize((px, px), Image.BILINEAR), dtype=float)
    f = level - lo
    return a * (1 - f) + b * f


def sim(sources, tiers):
    """-> {px: {stored: mean abs RGB diff vs the largest stored copy over opaque pixels}}, averaged over sources."""
    import numpy as np
    from PIL import Image
    big = max(STORED)
    acc = {t: {s: [] for s in STORED if s != big} for t in tiers}
    for f in sources:
        im = Image.open(f).convert("RGBA")
        if max(im.size) < big:
            raise ValueError("%s is %d px, below the largest stored size %d" % (f, max(im.size), big))
        im = im.resize((big, big), Image.LANCZOS) if im.size != (big, big) else im
        copies = {s: im.resize((s, s), Image.LANCZOS) for s in STORED}
        for t in tiers:
            ref = draw_cell(copies[big], t)
            body = ref[..., 3] > 200
            if body.sum() < 10:
                raise ValueError("%s has no opaque body at %d px" % (f, t))
            for s in acc[t]:
                got = draw_cell(copies[s], t)
                acc[t][s].append(float(np.abs(got[..., :3] - ref[..., :3])[body].mean()))
    return {t: {s: sum(v) / len(v) for s, v in row.items()} for t, row in acc.items()}


def check(table):
    """-> list of failed expectations (empty = the instrument behaves as round 2 measured)."""
    bad = []
    for t in (VANILLA_PX, SCS_PX):
        if table[t][128] >= JND:
            bad.append("128 vs 512 at %d px/cell reads %.2f >= JND %.1f" % (t, table[t][128], JND))
    t = CAMERAPLUS_PX
    if table[t][128] < JND:
        bad.append("128 vs 512 at %d px/cell reads %.2f < JND %.1f" % (t, table[t][128], JND))
    if not table[t][256] < table[t][128]:
        bad.append("256 is not nearer 512 than 128 at %d px/cell (%.2f vs %.2f)" % (t, table[t][256], table[t][128]))
    return bad


def verdict(table, px):
    d128, d256 = table[px][128], table[px][256]
    vis = [s for s, d in ((128, d128), (256, d256)) if d >= JND]
    if not vis:
        return "INVISIBLE: at %d px/cell 128 px stored art is indistinguishable from 512 (diff %.2f < %.1f)" % (
            px, d128, JND)
    return "VISIBLE: at %d px/cell stored %s px differ from 512 (128: %.2f, 256: %.2f; JND %.1f)" % (
        px, "/".join(map(str, vis)), d128, d256, JND)


def cmd_sim(a):
    srcs = [os.path.join(REPO, s) if not os.path.isabs(s) else s for s in (a.source or DEFAULT_SOURCES)]
    tiers = sorted({int(t) for t in a.tiers.split(",")} | ({VANILLA_PX, SCS_PX, CAMERAPLUS_PX} if a.check else set()))
    table = sim(srcs, tiers)
    for t in tiers:
        print("px/cell=%4d  " % t + "  ".join("stored %d vs 512: %.2f" % (s, d) for s, d in sorted(table[t].items())))
    if a.check:
        bad = check(table)
        for b in bad:
            print("FAIL " + b)
        print("CHECK %s" % ("FAIL" if bad else "PASS"))
        return 1 if bad else 0
    return 0


def _bridge(tool, params, timeout=60):
    sys.path.insert(0, HERE)
    import live_def_check
    return live_def_check._bridge(tool, params, timeout)


def _res(reply):
    return reply.get("result", reply) if isinstance(reply, dict) else {}


def cmd_live(a):
    out = {"item": "ART_RESOLUTION_MEASURE_AT_MAX_ZOOM", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    def fail(why):
        out["result"] = "NOT_MEASURED"
        out["why"] = why
        _write(a.json, out)
        print("NOT MEASURED: " + why)
        return 1

    sys.path.insert(0, HERE)
    import live_def_check
    running = live_def_check.call_running_mods(60)
    if not running:
        return fail("jawa/running_mods gave no packageIds (bridge down or not that answer)")
    out["running_mods"] = len(running)
    if CAMERAPLUS not in running:
        return fail("%s is not in the running load (%d mods)" % (CAMERAPLUS, len(running)))
    rival = [r for r in RIVAL_CAMERAS if r in running]
    if rival:
        return fail("a rival camera mod is running with Camera+: %s; its clamp would decide" % ", ".join(rival))
    cam0, why = _bridge("rimworld/get_camera_state", {})
    root0 = _res(cam0).get("rootSize") if cam0 else None
    if not root0:
        return fail("get_camera_state gave no rootSize: %s" % (why or json.dumps(cam0)))
    out["root_before"] = root0
    _bridge("rimworld/set_camera_zoom_extension", {"enabled": False})
    _bridge("rimworld/set_camera_zoom", {"rootSize": REQUEST_ROOT})
    time.sleep(2.0)                                  # let CameraDriver.Update (and Camera+'s patch) clamp it
    cam, why = _bridge("rimworld/get_camera_state", {})
    root = _res(cam).get("rootSize") if cam else None
    out["root_requested"], out["root_settled"] = REQUEST_ROOT, root
    out["view_rect"] = _res(cam).get("viewRect") if cam else None
    shot, swhy = _bridge("jawa/take_screenshot", {"fileName": "art_maxzoom_probe"})
    _bridge("rimworld/set_camera_zoom", {"rootSize": root0})
    if not root:
        return fail("no settled rootSize: %s" % (why or json.dumps(cam)))
    if abs(root - REQUEST_ROOT) < 1e-3:
        return fail("rootSize stayed at the requested %.2f: nothing clamped it, so this is not the player's floor"
                    % REQUEST_ROOT)
    path = _res(shot).get("filePath") if shot else None
    if not path:
        return fail("no screenshot: %s" % (swhy or json.dumps(shot)))
    try:
        wpath = subprocess.run(["wslpath", "-u", path], capture_output=True, text=True, timeout=20).stdout.strip()
        w, h = png_size(wpath or path)
    except (OSError, ValueError) as e:
        return fail("cannot read the frame %s: %s" % (path, e))
    px = px_per_cell(h, root)
    out.update(screen=[w, h], frame=path, px_per_cell=round(px, 1))
    table = sim([os.path.join(REPO, s) for s in DEFAULT_SOURCES], [int(round(px))])
    out["sim"] = {str(s): round(d, 2) for s, d in table[int(round(px))].items()}
    out["verdict"] = verdict(table, int(round(px)))
    out["result"] = "MEASURED"
    _write(a.json, out)
    print("MEASURED: Camera+ floor rootSize %.2f at %dx%d -> %.1f px/cell; %s" % (root, w, h, px, out["verdict"]))
    return 0


def _write(path, obj):
    if path:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(obj, fh, indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("sim")
    p.add_argument("--source", action="append")
    p.add_argument("--tiers", default="83,114,228,456")
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_sim)
    p = sub.add_parser("live")
    p.add_argument("--json", default="/mnt/d/ClaudeWork/rimmandrake/scratch/art_maxzoom_probe.json")
    p.set_defaults(fn=cmd_live)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
