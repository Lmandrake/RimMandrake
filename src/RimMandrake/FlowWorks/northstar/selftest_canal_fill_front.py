#!/usr/bin/env python3
"""CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY: the lessons a machine can check.

1. A dry mouth beside a stocked source is a MOD finding only when pulses actually ran with the engine on
   (`_source_feed_verdict`); an engine left off or a stalled schedule is UNMEASURED, never FAIL -- and a live pulse
   that left the channel dry is still FAIL (the check can fail).
2. A viscous fluid's front needs a window of at least one viscosity stride: tar (ticksPerTile 360, stride 6) in a
   3-pulse window gives on a pulse only half the time, so `0/10 wet` after 3 pulses proved nothing. The helper mirrors
   RM_StockMath.ViscosityStride and the tar constant matches the shipped FluidDef.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_canal_fill_front.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
UTILS = os.path.join(os.path.dirname(MOD), "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import extensions as EXT  # noqa: E402


def _e(on=True, npt=1000, tick=750, step=250):
    return {"success": True, "depthEngineEnabled": on, "nextPulseTick": npt, "pulseIntervalTicks": step,
            "ticksGame": tick}


def main():
    bad = []
    V = EXT._source_feed_verdict
    checks = [
        ("wet mouth passes", V(_e(), _e(npt=1750), 300.0, 299.0, True)[0], "PASS"),
        ("engine off before the window is UNMEASURED", V(_e(on=False), _e(npt=1750), 300.0, 300.0, False)[0],
         "UNMEASURED"),
        ("engine off after the window is UNMEASURED", V(_e(), _e(on=False, npt=1000), 300.0, 300.0, False)[0],
         "UNMEASURED"),
        ("no pulse fired (nextPulseTick stranded ahead) is UNMEASURED",
         V(_e(npt=37000, tick=35311), _e(npt=37000, tick=36061), 300.0, 300.0, False)[0], "UNMEASURED"),
        ("unreadable engine state is UNMEASURED", V({}, _e(), 300.0, 300.0, False)[0], "UNMEASURED"),
        ("pulses ran, stock untouched, mouth dry is FAIL", V(_e(npt=35500), _e(npt=36250), 300.0, 300.0, False)[0],
         "FAIL"),
        ("pulses ran, stock debited, mouth dry is FAIL", V(_e(npt=35500), _e(npt=36250), 300.0, 297.0, False)[0],
         "FAIL"),
        ("never-pulsed (-1) then pulsed counts as fired", V(_e(npt=-1), _e(npt=36250), 300.0, 300.0, False)[0],
         "FAIL"),
    ]
    for name, got, want in checks:
        if got != want:
            bad.append("%s: got %s, want %s" % (name, got, want))
    why = V(_e(npt=35500), _e(npt=36250), 300.0, 300.0, False)[1]
    if "never debited" not in why or "35500" not in why:
        bad.append("a FAIL message must carry the stock and the pulse numbers: %r" % why)

    # 2. stride mirrors the C# and the tar constant is the shipped def's
    cs = open(os.path.join(MOD, "Source", "RM_StockMath.cs"), encoding="utf-8").read()
    if "(ticksPerTile + WaterTicksPerTile / 2) / WaterTicksPerTile" not in cs or "WaterTicksPerTile = 60" not in cs:
        bad.append("RM_StockMath.ViscosityStride changed shape: re-derive extensions._pulses_for_one_move")
    for tpt, stride in ((60, 1), (180, 3), (360, 6), (480, 8)):
        if EXT._pulses_for_one_move(tpt, floor=1) != stride:
            bad.append("_pulses_for_one_move(%d) = %d, C# stride is %d" % (tpt, EXT._pulses_for_one_move(tpt, floor=1),
                                                                          stride))
    fluids = ET.parse(os.path.join(MOD, "Defs", "Canals", "FluidDefs", "FlowWorks_Fluids.xml")).getroot()
    tar = [d.findtext("ticksPerTile") for d in fluids if d.findtext("defName") == "RM_Fluid_Tar"]
    if tar != [str(EXT.TAR_TICKS_PER_TILE)]:
        bad.append("TAR_TICKS_PER_TILE %s != shipped RM_Fluid_Tar ticksPerTile %s" % (EXT.TAR_TICKS_PER_TILE, tar))
    if EXT._pulses_for_one_move(EXT.TAR_TICKS_PER_TILE) < 6:
        bad.append("the tar window is shorter than one viscosity stride")
    # the tar row really waits that window (a revert to the 3-pulse wait re-opens the coin toss)
    src = open(os.path.join(HERE, "extensions.py"), encoding="utf-8").read()
    body = src.split("def _plot_C2_body", 1)[1].split("\ndef ", 1)[0]
    if not re.search(r"_pulses_for_one_move\(TAR_TICKS_PER_TILE\)", body):
        bad.append("plot_C2's tar window no longer spans one viscosity stride")
    if body.count("_expect_source_fed(") != 1:
        bad.append("plot_C2's tar row lost its engine-state verdict")
    c = src.split("def plot_C_limitless_canal", 1)[1].split("\ndef ", 1)[0]
    if "_expect_source_fed(" not in c or "_engine(t)" not in c:
        bad.append("plot_C's canal_fill_front lost its engine-state verdict")

    if bad:
        print("selftest_canal_fill_front: FAIL")
        for b in bad:
            print("  - " + b)
        return 1
    print("selftest_canal_fill_front: PASS -- %d verdict cases, stride mirror, tar window" % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
