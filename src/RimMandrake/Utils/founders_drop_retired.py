#!/usr/bin/env python3
"""One-shot (owner rulings 19 and 20, 2026-10-19): drop from the founder fragments every def that
the selftest_founders_paint_closure closure does not contain, and re-point the 4 donor backstories to the ported RUT_ ones.
li entries with an outside <def> are removed (genes, hediffs, needs, thoughts, relations); non-li elements with one
(AM.UniqueSkills.*) are removed; outside skill passions become None; face-add-on and favoriteColor elements are removed.
Idempotent. Apply: python3 founders_drop_retired.py --apply
"""
import glob, os, re, sys, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_founders_paint_closure as S

BACKSTORY = {"VBE_ClonedHeir": "RUT_Jawa_FounderClonedHeir", "VBE_Standardbearer": "RUT_Jawa_FounderStandardbearer",
             "VBE_GiftedBurnout": "RUT_Jawa_FounderGiftedBurnout", "VQE_PowerArchitect02": "RUT_Jawa_FounderPowerArchitect"}


def process(root, inside, outside):
    n = {"removed": 0, "passion": 0, "bs": 0}
    gone_ids = set()

    def out(v):
        return v not in inside and (v in outside or re.match(r"^(AG|AS|VSE)_", v) is not None or v in ("AM_Skill_Gilgamesh",))

    def walk(parent):
        for ch in list(parent):
            d = ch.find("def")
            dv = (d.text or "").strip() if d is not None else ""
            tag = ch.tag
            if tag in ("childhood", "adulthood") and (ch.text or "").strip() in BACKSTORY:
                ch.text = BACKSTORY[ch.text.strip()]; n["bs"] += 1
            elif tag.endswith("ControllerComp_faceType") or tag.endswith("ControllerComp_color") or tag.endswith("ControllerComp_secondColor"):
                parent.remove(ch); n["removed"] += 1
            elif tag == "stockEntries":
                ks, vs = ch.find("keys"), ch.find("values")
                for k, v in reversed(list(zip(list(ks), list(vs)))):
                    if (k.text or "").strip() in outside and k.text.strip() not in inside:
                        ks.remove(k); vs.remove(v); n["removed"] += 1
            elif tag == "favoriteColorDef" and (ch.text or "").strip() not in inside:
                parent.remove(ch); n["removed"] += 1
            elif tag == "passion" and (ch.text or "").strip() not in S.ENUMS:
                ch.text = "None"; n["passion"] += 1
            elif dv and dv not in inside and (dv in outside or out(dv)) and parent.tag != "root":
                lid = ch.find("loadID")
                if lid is not None: gone_ids.add(lid.text.strip())
                parent.remove(ch); n["removed"] += 1
            else:
                walk(ch)
    walk(root)
    return n, gone_ids


def main():
    apply = "--apply" in sys.argv
    inside, outside = S.load()
    for f in sorted(glob.glob(os.path.join(S.FOUNDERS, "founder_*.xml"))):
        raw = open(f, encoding="utf-8", newline="").read()
        i = raw.index("\n<li") + 1
        root = ET.fromstring(raw[i:])
        n, gone = process(root, inside, outside)
        ET.indent(root, space="  ")
        new = raw[:i] + ET.tostring(root, encoding="unicode") + ("\n" if raw.endswith("\n") else "")
        dang = sorted(g for g in gone if re.search(r"(Gene|Hediff)_%s\b" % g, new))
        print(os.path.basename(f)[:22], n, "removed loadIDs:", len(gone), "dangling refs:", dang)
        if apply:
            open(f, "w", encoding="utf-8", newline="").write(new)


if __name__ == "__main__":
    main()
