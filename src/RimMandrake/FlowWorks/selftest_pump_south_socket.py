#!/usr/bin/env python3
"""LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB: a pipe on the pump's south covers the drawn cap and leaves the bolted rim visible.

Owner 2026-11-23: "I should not be able to see the capped end when a pipe is connected, right? It should cover the cap but
leave the bolted rim visible just like the other directions show."
Reads the installed art, PumpSouthSocket.cs's table and the draw code; the C# twin (geometry) is PumpSocket_* in PumpSouthSocketChecks.cs.
NOT proven here: the mesh in the game (a live look; see the item).

    python3 src/RimMandrake/FlowWorks/selftest_pump_south_socket.py      # exit 1 on any FAIL
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "art_source", "PumpOblique"))
sys.path.insert(0, os.path.join(HERE, "art_source", "PumpOblique", "v2"))
import check_oblique  # noqa: E402  (its port clause only; its oblique clause passes rejected art)
import joined  # noqa: E402
import south_socket  # noqa: E402
from PIL import Image  # noqa: E402

fails = 0


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, (" -- " + detail) if detail else ""))


def ellipse(cap, n=joined.C):
    cx, cz, rx, rz = cap
    yy, xx = np.mgrid[0:n, 0:n]
    return np.hypot(((xx + .5) / n - cx) / rx, ((1 - (yy + .5) / n) - cz) / rz), (xx + .5) / n - cx, (1 - (yy + .5) / n) - cz


try:
    caps = joined.sockets()
except OSError:
    caps = {}
check("every_look_has_a_measured_cap", set(caps) == set(south_socket.LOOKS), str(sorted(caps)))


def read_cap(look, cap):
    """(share of the cap covered, share of the rim above and beside the cap still visible)."""
    piece = np.array(joined.socket_piece(look))[..., 3] > 128
    e, dx, dz = ellipse(cap)
    rim = (e > 1.12) & (e < 1.32) & (dz > -0.2 * cap[3])
    inner = e < 0.95
    return piece[inner].mean(), 1 - piece[rim].mean()


for look in south_socket.LOOKS:
    if look not in caps:
        continue
    want = south_socket.table()[look]
    check("%s cap matches the installed art" % look, max(abs(a - b) for a, b in zip(caps[look], want)) < 0.002,
          "table %s art %s" % (caps[look], want))
    covered, rim = read_cap(look, caps[look])
    check("%s pipe covers the cap" % look, covered > 0.995, "%.1f%%" % (100 * covered))
    check("%s bolted rim stays visible round it" % look, rim > 0.97, "%.1f%%" % (100 * rim))
    lo, hi = south_socket.pipe_span(look)
    check("%s joined at the edge at the pipe's own width" % look, abs((hi - lo) / 2 - caps[look][2]) < 0.006, "pipe %.4f cap %.4f" % ((hi - lo) / 2, caps[look][2]))
if "Scrapper" in caps:
    cx, cz, rx, rz = caps["Scrapper"]
    real = joined.sockets
    joined.sockets = lambda: {"Scrapper": (cx, cz - 0.08, rx, rz)}
    check("can-fail: a piece that stops below the cap leaves it showing", read_cap("Scrapper", caps["Scrapper"])[0] < 0.9)
    joined.sockets = lambda: {"Scrapper": (cx, cz + 0.02, rx * 1.5, rz * 1.5)}
    check("can-fail: a piece as big as the flange hides the rim", read_cap("Scrapper", caps["Scrapper"])[1] < 0.9)
    joined.sockets = real

for look, p in check_oblique.INSTALLED.items():
    for side, off, gap in check_oblique.ports(np.array(Image.open(p).convert("RGBA")).astype(float)):
        check("%s port %s on its edge centre" % (look, side), off is not None and abs(off) <= check_oblique.REG_TOL and gap <= check_oblique.FACE_TOL,
              "off %s gap %s" % (off, gap))

src = open(os.path.join(HERE, "Source", "Machinery", "RM_LiquidJoins.cs"), encoding="utf-8-sig").read()
check("the pipe layer prints the socket over the pump", "PrintSouthSocket(t, c, b)" in src and "PumpSouthSocket.Quads(" in src)
# live 2026-11-23: printed into the under-runs' mesh (same material, below the pump) the socket drew under the pump
body = src[src.find("private int PrintSouthSocket("):][:1500]
check("the socket has a mesh of its own, over the pump", "SocketMat(StraightMat(pipe, false))" in body and "new Material(pipe)" in src)
check("the socket is at the couplers' altitude", "float y = AltitudeLayer.BuildingOnTop.AltitudeFor();" in body)
check("no loose flange is laid beside the pump's own", "if (RM_LiquidJoins.DrawsOwnFlanges(b)) continue;" in src)

def hose_faults(hoses, coup, joins):
    """What stops a hose on the pump's south from covering the cap as a pipe does: the missing pieces, [] = none."""
    draw = coup[coup.find("public static bool DrawSouthSocket("):] if "public static bool DrawSouthSocket(" in coup else ""
    ends = hoses[hoses.find("private void DrawEnds("):hoses.find("internal bool PortEnd(")]
    port = ends[ends.find("else if (fe.Kind == HoseEndKind.Port)"):ends.find("RelayOf(r) != null")]
    feed = hoses[hoses.find("private void DrawFeed("):hoses.find("private static Mesh PipeStrip(")]
    want = (
        ("a coupled hose end draws the piece", "RM_UnderCouplers.DrawSouthSocket(fe.Port, fe.PortSide.X, fe.PortSide.Z);" in port),
        ("a reel against the pump draws the piece", "RM_UnderCouplers.DrawSouthSocket(r.Port(), r.portSide.X, r.portSide.Z);" in feed),
        ("only at a pump's south, by the rule", "PumpSouthSocket.HoseCovers(RM_LiquidJoins.DrawsOwnFlanges(port), sx, sz)" in draw),
        ("the pipe's own piece", "PumpSouthSocket.Quads(cap)" in draw and "PumpSouthSocket.TryCap(look," in draw),
        ("on the pump look's north-south pipe tile", "RM_LiquidJoins.PipeStraightMat(look, false)" in draw
         and "eastWest ? LiquidJoinRule.LinkLeft | LiquidJoinRule.LinkRight : LiquidJoinRule.LinkUp | LiquidJoinRule.LinkDown" in
         joins[joins.find("Material PipeStraightMat("):][:1400]),
        ("over the pump", "AltitudeLayer.BuildingOnTop.AltitudeFor()" in draw),
        ("on the pump's cell", "port.Position.x" in draw and "port.Position.z" in draw),
    )
    return [n for n, ok in want if not ok]


srcs = [open(os.path.join(HERE, "Source", *p), encoding="utf-8-sig").read() for p in
        (("Hose", "RM_MapComponent_Hoses.cs"), ("Machinery", "RM_UnderCouplers.cs"), ("Machinery", "RM_LiquidJoins.cs"))]
got = hose_faults(*srcs)
check("a hose on the pump's south covers the cap as a pipe does", not got, "; ".join(got))
for k, a, b in ((0, "RM_UnderCouplers.DrawSouthSocket(fe.Port,", "RM_UnderCouplers.NoDraw(fe.Port,"),
                (0, "RM_UnderCouplers.DrawSouthSocket(r.Port(),", "RM_UnderCouplers.NoDraw(r.Port(),"),
                (1, "AltitudeLayer.BuildingOnTop.AltitudeFor()", "AltitudeLayer.Shadows.AltitudeFor()"),
                (1, "RM_LiquidJoins.PipeStraightMat(look, false)", "RM_LiquidJoins.PipeStraightMat(look)"),
                (1, "DrawsOwnFlanges(port), sx, sz)", "DrawsOwnFlanges(port), 0, 1)")):
    planted = list(srcs)
    planted[k] = srcs[k].replace(a, b)
    check("can-fail: %s" % b, planted[k] != srcs[k] and hose_faults(*planted) != got)
# the picture: the hose's end at a pump, composed; with no piece the cap shows
for look in sorted(caps):
    plain, hosed, pump_only = (np.array(joined.hosed(look, p)).astype(int) for p in (False, True, None))
    e, dx, dz = ellipse(caps[look])
    inner, rim = e < 0.95, (e > 1.12) & (e < 1.32) & (dz > -0.2 * caps[look][3])
    on_pump = lambda im: (np.abs(im - pump_only).max(-1) <= 2)[joined.C:2 * joined.C, joined.C:2 * joined.C]  # noqa: E731
    check("%s hose: the cap is covered" % look, on_pump(hosed)[inner].mean() < 0.15, "%.1f%% still cap" % (100 * on_pump(hosed)[inner].mean()))
    check("%s hose: the bolted rim stays visible" % look, on_pump(hosed)[rim].mean() > 0.97, "%.1f%%" % (100 * on_pump(hosed)[rim].mean()))
    check("%s can-fail: with no piece the hose leaves the cap showing" % look, on_pump(plain)[inner].mean() > 0.95)
print("selftest_pump_south_socket.py: %d failure(s)" % fails)
sys.exit(1 if fails else 0)
