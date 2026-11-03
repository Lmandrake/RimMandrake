#!/usr/bin/env python3
"""Offline proof for GUBBRA_GOURD_FIX_WONT_SELECT: the gubbra gourd (RM_Pusmelon) is selectable.

Owner, 2026-10-24: "What the heck are those bladder-like growths on the ground? I couldn't select them."

Cause: Core's PlantBaseNonEdible sets <selectable>False</selectable> (the grass rule) and RM_Pusmelon,
ParentName PlantBase, never overrode it, so the mouse-over readout named it but a click could not select it.
This resolves RM_Pusmelon's effective `selectable` through its ParentName chain (our defs first, then Core's
Plants_Bases.xml when it is on disk, else the recorded Core value) and checks no patch of ours turns it off.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FLORA = HERE / "Defs" / "ThingDefs_Plants" / "RM_RotSporeKit_Flora.xml"
CORE_BASES = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs/ThingDefs_Plants/Plants_Bases.xml")
# Recorded from Core Plants_Bases.xml (RimWorld 1.6): PlantBase -> PlantBaseNonEdible, which sets selectable False.
CORE_FALLBACK = {"PlantBase": ("PlantBaseNonEdible", None), "PlantBaseNonEdible": (None, "False")}
TARGET = "RM_Pusmelon"


def _abstracts(root):
    out = {}
    for d in root.iter("ThingDef"):
        name = d.get("Name")
        if name:
            sel = d.find("selectable")
            out[name] = (d.get("ParentName"), sel.text.strip() if sel is not None else None)
    return out


def effective_selectable(defn, bases):
    sel = defn.find("selectable")
    if sel is not None:
        return sel.text.strip(), "own"
    parent, seen = defn.get("ParentName"), set()
    while parent and parent not in seen:
        seen.add(parent)
        if parent not in bases:
            raise SystemExit(f"FAIL: parent {parent!r} unresolved — instrument cannot see the chain")
        nxt, val = bases[parent]
        if val is not None:
            return val, parent
        parent = nxt
    return "False", "ThingDef default"  # ThingDef.selectable defaults false


def main():
    fails = []
    root = ET.parse(FLORA).getroot()
    bases = dict(CORE_FALLBACK)
    if CORE_BASES.is_file():
        bases.update(_abstracts(ET.parse(CORE_BASES).getroot()))
    bases.update(_abstracts(root))
    # Sanity: the instrument must see the bug it was written for — PlantBase alone resolves to not selectable.
    probe = ET.fromstring('<ThingDef ParentName="PlantBase"><defName>Probe</defName></ThingDef>')
    pv, _ = effective_selectable(probe, bases)
    if pv.lower() != "false":
        fails.append(f"sanity: a bare PlantBase child resolved selectable={pv}; Core changed or chain unread")
    defs = [d for d in root.iter("ThingDef") if (d.findtext("defName") or "").strip() == TARGET]
    if len(defs) != 1:
        fails.append(f"{TARGET}: found {len(defs)} defs in {FLORA.name}, want 1")
    else:
        val, src = effective_selectable(defs[0], bases)
        print(f"{TARGET}: selectable={val} (from {src})")
        if val.lower() != "true":
            fails.append(f"{TARGET} resolves selectable={val} from {src}")
    # No patch of ours may switch it back off.
    for p in sorted((REPO / "src").rglob("*.xml")):
        if "/Patches/" not in p.as_posix():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if TARGET in text and "selectable" in text:
            for op in ET.parse(p).getroot().iter():
                xp = op.findtext("xpath") or ""
                if TARGET in xp and "selectable" in (xp + ET.tostring(op, encoding="unicode")):
                    fails.append(f"patch touches {TARGET} selectable: {p.relative_to(REPO)}")
                    break
    for f in fails:
        print("FAIL:", f)
    print("PASS" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
