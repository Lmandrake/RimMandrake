#!/usr/bin/env python3
"""Selftest for art_maxzoom_probe.py (ART_RESOLUTION_MEASURE_AT_MAX_ZOOM): the px/cell geometry, the simulation's
round-2 expectations, and every exit of the live half against a stubbed bridge."""
import os
import struct
import sys
import tempfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art_maxzoom_probe as P  # noqa: E402
import live_def_check  # noqa: E402

FAILS = []


def ok(cond, what):
    if not cond:
        FAILS.append(what)
        print("FAIL " + what)


def tiny_png(path, w, h):
    raw = b"".join(b"\x00" + b"\x00\x00\x00" * w for _ in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def geometry():
    ok(abs(P.px_per_cell(1826, 8) - 114.125) < 1e-9, "root 8 at 1826 px -> 114 px/cell (round 2)")
    ok(abs(P.px_per_cell(1826, 11) - 83.0) < 1e-9, "root 11 at 1826 px -> 83 px/cell (round 2)")
    ok(abs(P.px_per_cell(1826, 2) - 456.5) < 1e-9, "root 2 at 1826 px -> 456 px/cell")
    for bad in ((0, 2), (1826, 0), (1826, -1), (None, 2)):
        try:
            P.px_per_cell(*bad)
            ok(False, "px_per_cell%r must refuse" % (bad,))
        except ValueError:
            pass


def check_logic():
    good = {83: {128: 1.0, 256: 0.5}, 114: {128: 1.5, 256: 0.7}, 456: {128: 10.0, 256: 4.0}}
    ok(P.check(good) == [], "a round-2-shaped table passes")
    blind = {83: {128: 0.1, 256: 0.1}, 114: {128: 0.1, 256: 0.1}, 456: {128: 0.1, 256: 0.1}}
    ok(len(P.check(blind)) == 2, "a blind instrument (no difference anywhere) fails at 456 twice")
    loud = {83: {128: 5.0, 256: 3.0}, 114: {128: 7.0, 256: 4.0}, 456: {128: 14.0, 256: 9.0}}
    ok(len(P.check(loud)) == 2, "an instrument that sees a difference at vanilla zoom fails")
    ok(P.verdict(good, 456).startswith("VISIBLE"), "verdict VISIBLE at 456")
    ok(P.verdict(good, 83).startswith("INVISIBLE"), "verdict INVISIBLE at 83")


def sim_on_repo_art():
    table = P.sim([os.path.join(P.REPO, s) for s in P.DEFAULT_SOURCES], [P.VANILLA_PX, P.SCS_PX, P.CAMERAPLUS_PX])
    ok(P.check(table) == [], "sim on the shipped sources meets the round-2 expectations: %r" % (table,))
    ok(table[P.CAMERAPLUS_PX][128] > table[P.SCS_PX][128] > 0, "the difference grows with px/cell and is not zero")


def live_exits():
    tmp = tempfile.mkdtemp()
    frame = os.path.join(tmp, "f.png")
    tiny_png(frame, 64, 40)
    state = {}

    def fake_bridge(tool, params, timeout=60):
        if tool == "rimworld/get_camera_state":
            return {"result": {"rootSize": state["root"], "viewRect": {"width": 3, "height": 2}}}, None
        if tool == "rimworld/set_camera_zoom":
            state["root"] = state["clamp"](params["rootSize"])
            return {"success": True}, None
        if tool == "jawa/take_screenshot":
            return {"result": {"filePath": frame}}, None
        return {"success": True}, None

    real_rm, real_br = live_def_check.call_running_mods, P._bridge
    P._bridge = fake_bridge
    try:
        def run(mods, clamp):
            state.update(root=24.0, clamp=clamp)
            live_def_check.call_running_mods = lambda t: mods
            js = os.path.join(tmp, "o.json")
            code = P.cmd_live(type("A", (), {"json": js})())
            return code, state["root"]
        code, _ = run(None, lambda r: max(r, 2.0))
        ok(code == 1, "no running_mods answer -> exit 1")
        code, _ = run({"ludeon.rimworld"}, lambda r: max(r, 2.0))
        ok(code == 1, "Camera+ absent -> exit 1")
        code, _ = run({P.CAMERAPLUS, "ray1203.simplecamerasetting"}, lambda r: max(r, 2.0))
        ok(code == 1, "a rival camera mod -> exit 1")
        code, _ = run({P.CAMERAPLUS}, lambda r: r)
        ok(code == 1, "nothing clamped the request -> exit 1")
        code, root = run({P.CAMERAPLUS}, lambda r: max(r, 2.0))
        ok(code == 0, "Camera+ clamps to 2 and a frame reads -> exit 0")
        ok(root == 24.0, "the prior rootSize is restored")
        import json
        out = json.load(open(os.path.join(tmp, "o.json")))
        ok(out.get("px_per_cell") == 10.0, "px/cell = 40 / (2*2) from the frame height: %r" % out.get("px_per_cell"))
        ok(out.get("result") == "MEASURED" and "verdict" in out, "the JSON records the measurement and verdict")
    finally:
        live_def_check.call_running_mods, P._bridge = real_rm, real_br


if __name__ == "__main__":
    geometry()
    check_logic()
    sim_on_repo_art()
    live_exits()
    print("selftest_art_maxzoom_probe: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
