#!/usr/bin/env python3
"""selftest_fw_gate_lift.py -- SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS + GRATE_DOOR_REBUILD_LIFTS_LIKE_THE_SLUICE as
permanent offline checks on fw_gate_lift.py (owner 2026-10-24: "Your art for 'open' is wrong: it never opens. ... they
slide 'up' to allow the water through"; acceptance: open renders a passable gap, closed does not, and the check FAILS on
the old behaviour).

  gap       every gate and facing: closed covers the passage, open leaves it clear, half is between (fw_gate_lift.check)
  can-fail  the OLD draw (vanilla's two full copies sliding 0.45 cell sideways) must read as NOT open, or the gap check
            is blind; fw_gate_lift.check reports that as a failure itself
  installed the shipped _Frame/_Panel layer PNGs are exactly what fw_gate_lift.layers() cuts from the gate art, so the
            game draws what was checked
  defs      each gate's RM_FlowDoorExtension says isSluice (sluice true, grate false) and a liftCells in (0, 1)
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fw_gate_lift as G  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAILS.append(name)


def main():
    f = G.check()
    check("gap: open clears the passage, closed covers it, the old sideways draw fails", not f, f)
    for gate in G.GATES:
        for facing in G.FACINGS:
            fr, pa = G.layers(gate, facing)
            for part, img in (("frame", fr), ("panel", pa)):
                p = G.TEX / G.layer_name(gate, facing, part)
                if not p.exists():
                    check("installed %s" % p.name, False, "missing")
                    continue
                same = np.array_equal(np.asarray(Image.open(p).convert("RGBA")), np.asarray(img.convert("RGBA")))
                check("installed %s == layers()" % p.name, same, "differs: re-run fw_gate_lift.py layers and re-install")
    root = ET.parse(G.DOORS_XML).getroot()
    for d in root.iter("ThingDef"):
        name = d.findtext("defName")
        if name not in G.GATES:
            continue
        ext = [li for li in d.iter("li") if li.get("Class", "").endswith("RM_FlowDoorExtension")]
        sluice = ext[0].findtext("isSluice") if ext else None
        lift = ext[0].findtext("liftCells") if ext else None
        check("def %s isSluice" % name, sluice == ("true" if name == "RM_Sluice" else "false"), sluice)
        check("def %s liftCells in (0,1)" % name, lift is not None and 0.0 < float(lift) < 1.0, lift)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
