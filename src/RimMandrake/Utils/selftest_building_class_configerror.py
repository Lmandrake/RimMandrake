#!/usr/bin/env python3
"""selftest_building_class_configerror.py — ThingDef.ConfigErrors (Verse/ThingDef.cs:1687):
"has building category and is marked as deconstructible, but thing class is not a subclass of
building". Load 13 hit it on RSW_DeepDesertSeep (LOAD13_CONFIGERRORS_TRIAGE_1).

Red on any src ThingDef that DIRECTLY declares <category>Building</category> and a thingClass
from the known non-Building vanilla set, unless it also declares building/deconstructible false.
Defs that inherit either field are not judged (no inheritance resolution here). A sanity probe
demands the seep is seen; mutants must go red.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NON_BUILDING = {"Thing", "ThingWithComps", "Plant", "Filth", "Mote", "MoteThrown", "Skyfaller",
                "Projectile", "Bullet", "Pawn", "Corpse", "Apparel", "Medicine", "Verse.Thing",
                "Verse.ThingWithComps", "RimWorld.Plant", "RimWorld.Filth"}


def findings(root, fname="?"):
    out, seen = [], []
    for td in root.iter("ThingDef"):
        cat = (td.findtext("category") or "").strip()
        cls = (td.findtext("thingClass") or "").strip()
        if cat != "Building" or not cls:
            continue
        seen.append(td.findtext("defName"))
        if cls in NON_BUILDING and (td.findtext("building/deconstructible") or "").strip().lower() != "false":
            out.append(f"{fname}:{td.findtext('defName')} category Building + thingClass {cls} + deconstructible")
    return out, seen


def main():
    fails, seen = [], []
    for p in (ROOT / "src").rglob("*.xml"):
        t = p.read_text(errors="ignore")
        if "<category>Building</category>" not in t or "<thingClass>" not in t:
            continue
        try:
            f, s = findings(ET.fromstring(t.encode()), p.name)
        except ET.ParseError:
            continue
        fails += f
        seen += s
    if "RSW_DeepDesertSeep" not in seen:
        print("UNMEASURED: sanity probe RSW_DeepDesertSeep not seen")
        return 2
    print(f"{len(seen)} Building-category defs with a direct thingClass scanned")
    mut = "<Defs><ThingDef><defName>X</defName><category>Building</category><thingClass>Thing</thingClass></ThingDef></Defs>"
    for name, xml, want_red in [("deconstructible Thing building", mut, True),
                                ("guarded by deconstructible false",
                                 mut.replace("</ThingDef>", "<building><deconstructible>false</deconstructible></building></ThingDef>"), False),
                                ("real Building class", mut.replace(">Thing<", ">Building<"), False)]:
        red = bool(findings(ET.fromstring(xml))[0])
        ok = red == want_red
        print(f"mutant {name}: {'red' if red else 'green'} ({'ok' if ok else 'WRONG'})")
        if not ok:
            fails.append("mutant wrong: " + name)
    print("FAIL" if fails else "PASS", *fails, sep="\n  ")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
