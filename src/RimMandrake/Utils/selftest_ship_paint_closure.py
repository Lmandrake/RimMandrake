#!/usr/bin/env python3
"""Selftest: the gravship layout the PAINT profile prints names no def outside the PAINT def closure.

Closure = every def in the newest def-dump capture whose packageId is in
infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml (Core/DLC ids are in that list).
Cases: (1) the committed .paint.xml layout is inside the closure; (2) it equals ship_remap(original),
so the table and the file cannot drift; (3) probe: the ORIGINAL layout is NOT inside it (an instrument
that cannot see the loss proves nothing). Dump absent => SKIP, exit 0.

    python3 src/RimMandrake/Utils/selftest_ship_paint_closure.py
"""
import json, os, sys, xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_paths, ship_remap  # noqa: E402

REPO = ship_remap.REPO
PAINT = os.path.join(REPO, "infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml")
EXP = os.path.join(REPO, "design/Jawa/worldbuilding/ship_build/exported")
ORIG = os.path.join(EXP, "Gravship_v2_ring_2026-09-12.xml")
PAINTED = os.path.join(EXP, "Gravship_v2_ring_2026-09-12.paint.xml")


def closure():
    ids = {li.text.strip().lower() for li in ET.parse(PAINT).getroot().find("activeMods")}
    cap = game_paths.DEF_DUMP
    names = set()
    ddir = os.path.join(cap, "defs")
    for f in os.listdir(ddir):
        try:
            j = json.load(open(os.path.join(ddir, f)))
        except Exception:
            continue
        for d in j.get("defs", []):
            if (d.get("packageId") or "").lower() in ids:
                names.add(d["defName"])
    return names, ids


def outside(path, names):
    d = ship_remap.layout_defs(ET.parse(path).getroot())
    return {k: sorted(v - names) for k, v in d.items() if v - names}


def main():
    try:
        names, ids = closure()
    except (OSError, AttributeError, TypeError) as e:
        print("SKIP  def dump unreadable (%s)" % e)
        return 0
    fails = []
    if "Human" not in names or "Substructure" not in names:
        print("FAIL  instrument blind: closure lacks Human/Substructure (%d defs)" % len(names))
        return 1
    print("closure: %d defs from %d PAINT mods" % (len(names), len(ids)))
    out = outside(PAINTED, names)
    print(("FAIL" if out else "ok  "), "painted layout inside closure", out or "")
    if out:
        fails.append(1)
    import tempfile
    t = ET.parse(ORIG)
    ship_remap.remap(t.getroot(), json.load(open(ship_remap.TABLE)))
    ET.indent(t, space="  ")
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tf:
        tmp = tf.name
    t.write(tmp, encoding="utf-8", xml_declaration=True)
    same = open(tmp, "rb").read() == open(PAINTED, "rb").read()
    os.unlink(tmp)
    print(("ok  " if same else "FAIL"), ".paint.xml equals remap(original)")
    if not same:
        fails.append(2)
    raw = outside(ORIG, names)
    print(("ok  " if raw else "FAIL"), "probe: original has defs outside closure", {k: len(v) for k, v in raw.items()})
    if not raw:
        fails.append(3)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
