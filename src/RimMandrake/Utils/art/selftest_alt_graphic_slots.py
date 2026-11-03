#!/usr/bin/env python3
"""selftest_alt_graphic_slots — the art tracker reads a PawnKindDef's alternateGraphics as slots of that creature.

Why (ALT_GRAPHICS_FIX_SIX_SECOND_FACES, from the Gizka frog, 2026-10-15): artledger.scan_def_slots had no role for
`alternateGraphics/li`, so a picture the game draws on most spawns (GizkaW at 80%) showed "(none in our defs)" and
no sheet ruling could bind to it. Now every alternateGraphics/li/texPath is a slot {subject: the kind's defName,
role: "alternate"}, and role_of() names it "alternate".

Checks: (1) a fixture mod — the alternate is a slot of its kind with role alternate, the primary stays body;
(2) the live src/ tree — every PawnKindDef alternateGraphics texPath (parsed XML) has an alternate slot naming that
kind, and the count is not zero (the instrument can see: the five creatures of this item still carrying
alternates are all parsed).
"""
from __future__ import annotations

import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# the item named six; RSW_Hssiss was since ported as RSW_Kinrath with no alternateGraphics, so five remain
SIX = ("RSW_Eopie", "RSW_Falumpaset", "RSW_KowakianMonkeyLizard", "RSW_Worrt", "RM_Gembug")


def fixture(L) -> list[str]:
    fails = []
    with tempfile.TemporaryDirectory() as td:
        mod = Path(td) / "M"
        (mod / "Defs").mkdir(parents=True)
        (mod / "Defs" / "k.xml").write_text(
            "<Defs><PawnKindDef><defName>FX_Beast</defName><race>FX_Beast</race>"
            "<alternateGraphicChance>0.8</alternateGraphicChance><alternateGraphics>"
            "<li><texPath>X/BeastW</texPath></li><li><texPath>X/BeastV</texPath><color>(1,1,1)</color></li>"
            "</alternateGraphics><lifeStages><li><bodyGraphicData><texPath>X/Beast</texPath></bodyGraphicData>"
            "</li></lifeStages></PawnKindDef></Defs>")
        slots = L.scan_def_slots(Path(td))
        for tp in ("X/BeastW", "X/BeastV"):
            ss = slots.get(tp, [])
            if not any(s["subject"] == "FX_Beast" and s["role"] == "alternate" for s in ss):
                fails.append(f"fixture: {tp} should be an alternate slot of FX_Beast, got {ss}")
            if L.role_of(tp, False, slots) != "alternate":
                fails.append(f"fixture: role_of({tp}) should be alternate, got {L.role_of(tp, False, slots)}")
        if [s["role"] for s in slots.get("X/Beast", [])] != ["body"]:
            fails.append(f"fixture: primary X/Beast should stay one body slot, got {slots.get('X/Beast')}")
    return fails


def live(L) -> tuple[list[str], int]:
    fails, n, seen_six = [], 0, set()
    root = L.src_root()
    slots = L.scan_def_slots(root)
    for f in sorted(root.rglob("*.xml")):
        if "/Defs/" not in f.as_posix():
            continue
        try:
            tree = ET.parse(f)
        except (ET.ParseError, OSError):
            continue
        for k in tree.getroot().iter("PawnKindDef"):
            dn = (k.findtext("defName") or "").strip()
            for li in k.findall("alternateGraphics/li"):
                tp = (li.findtext("texPath") or "").strip()
                if not dn or not tp:
                    continue
                n += 1
                if dn in SIX:
                    seen_six.add(dn)
                if not any(s["subject"] == dn and s["role"] == "alternate" for s in slots.get(tp, [])):
                    fails.append(f"live: {dn} alternate {tp} has no alternate slot ({f.relative_to(root)})")
    if n == 0:
        fails.append("live: 0 alternateGraphics texPaths found — the instrument is blind, not the tree empty")
    for dn in sorted(set(SIX) - seen_six):
        fails.append(f"live: sanity probe — {dn} carries alternateGraphics per the item, but none was parsed")
    return fails, n


def main() -> int:
    import artledger as L
    fails = fixture(L)
    lf, n = live(L)
    fails += lf
    print(f"alt_graphic_slots: {n} alternate texPath(s) in src/ PawnKindDefs, {len(fails)} failure(s)")
    for x in fails:
        print("FAIL", x)
    if not fails:
        print("PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
