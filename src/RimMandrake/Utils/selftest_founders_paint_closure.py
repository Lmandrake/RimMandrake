#!/usr/bin/env python3
"""Selftest: no founder fragment names a def outside the PAINT def closure (owner ruling 19, 2026-10-19).

Closure = every def in the newest def-dump capture whose packageId is in ModsConfig.PAINT.RULED_2026-10-20.xml,
plus defNames authored in src/RimUtinni/PawnFlavor/Defs (the ported RUT_Jawa_Founder* backstories; the dump may predate them).
A fragment value is OUTSIDE when (a) it sits in a def-bearing slot (<def>, *Def, <childhood>, <adulthood>,
<passion> beyond None/Minor/Major, *ControllerComp_faceType) and is not in the closure, or (b) any element text equals
a dump defName that only non-PAINT mods own. Probe: the dump must contain out-of-closure names (instrument can see).
Dump absent => SKIP, exit 0.

    python3 src/RimMandrake/Utils/selftest_founders_paint_closure.py
"""
import glob, json, os, re, sys, xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_paths  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAINT = os.path.join(REPO, "infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml")
FOUNDERS = os.path.join(REPO, "design/Jawa/worldbuilding/founders")
FLAVOR = os.path.join(REPO, "src/RimUtinni/PawnFlavor/Defs")
ENUMS = {"None", "Minor", "Major"}
SLOTS = re.compile(r"^(def|\w*Def|childhood|adulthood|passion|\w+ControllerComp_faceType)$")


def load():
    ids = {li.text.strip().lower() for li in ET.parse(PAINT).getroot().find("activeMods")}
    inside, outside = set(), set()
    ddir = os.path.join(game_paths.DEF_DUMP, "defs")
    for f in os.listdir(ddir):
        try:
            j = json.load(open(os.path.join(ddir, f)))
        except Exception:
            continue
        for d in j.get("defs", []):
            (inside if (d.get("packageId") or "").lower() in ids else outside).add(d["defName"])
    for p in glob.glob(os.path.join(FLAVOR, "**/*.xml"), recursive=True):
        for m in re.finditer(r"<defName>([^<]+)</defName>", open(p, encoding="utf-8").read()):
            inside.add(m.group(1))
    return inside, outside - inside


def violations(path, inside, outside):
    raw = open(path, encoding="utf-8").read()
    root = ET.fromstring(raw[raw.index("\n<li") + 1:])
    bad = set()
    for e in root.iter():
        t = (e.text or "").strip()
        if not t or len(e) or e.tag in ("defName", "label"):
            continue
        if SLOTS.match(e.tag):
            if t not in inside and t not in ENUMS and not (e.tag == "passion" and False):
                bad.add((e.tag, t))
        elif t in outside:
            bad.add((e.tag, t))
    return sorted(bad)


def main():
    try:
        inside, outside = load()
    except (OSError, TypeError) as e:
        print("SKIP  def dump unreadable (%s)" % e)
        return 0
    if "Human" not in inside or len(outside) < 1000:
        print("FAIL  instrument blind: inside=%d outside=%d" % (len(inside), len(outside)))
        return 1
    print("closure: %d defs inside, %d only-outside" % (len(inside), len(outside)))
    fails = 0
    files = sorted(glob.glob(os.path.join(FOUNDERS, "founder_*.xml")))
    if len(files) != 6:
        print("FAIL  expected 6 founder fragments, found %d" % len(files))
        return 1
    for f in files:
        v = violations(f, inside, outside)
        print(("FAIL" if v else "ok  "), os.path.basename(f), v[:6] if v else "")
        fails += bool(v)
    probe = ET.fromstring("<li><def>AG_FrailSkin</def><EyeballControllerComp_faceType>EyeNormal</EyeballControllerComp_faceType></li>")
    # probe: the slot rule must flag a retired-mod def and backstory
    flagged = [e.text for e in probe.iter() if SLOTS.match(e.tag) and e.text not in inside]
    print(("ok  " if len(flagged) == 2 else "FAIL"), "probe: retired defs are flagged", flagged)
    fails += len(flagged) != 2
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
