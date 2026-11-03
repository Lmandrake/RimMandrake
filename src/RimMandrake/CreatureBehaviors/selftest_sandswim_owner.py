#!/usr/bin/env python3
"""One visibility owner per sand swimmer (STILLSAND_SAND_SWIM_REMAINDER_1 §1 and §3), offline.

Two comps toggling invisibility hediffs on one pawn fight, so every race that hides under the ground
has exactly one owner of that: RM_CompSandSwim (added at startup from RM_SandSwimExtension), or its own
comp (RM_CompDrumLure with a submersionHediff, the Sarlacc mod's CompSarlaccSwimmer). This reads every
ThingDef under src/ and every patch that adds an RM_SandSwimExtension, and checks:

  - no race carries the extension AND its own submersion comp (defs or patches);
  - the decided owners: RM_Qorrax, RM_Vekka, RM_Muurrok -> RM_CompSandSwim; RM_Drazzik -> RM_CompDrumLure;
    RSW_SarlaccSwimmer -> CompSarlaccSwimmer; RM_Duumma -> none (never hidden; RM_SandBuriedGraphicExtension);
  - the C# keeps both halves: RM_SandSwimStartup skips a race with another owner, and TickSubmerged lays the
    wake trough through RM_MapComponent_TrackGrid.RecordPrint from RM_SandSwimKernel.WakeTroughOffsets;
  - a probe: a synthetic def carrying both is flagged (the checker can fail).

    python3 src/RimMandrake/CreatureBehaviors/selftest_sandswim_owner.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "src")
COMP_CS = os.path.join(HERE, "Source", "RM_CompSandSwim.cs")

EXT = "RimMandrake.CreatureBehaviors.RM_SandSwimExtension"
FAILED = []


def expect(label, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", label, (" -- " + detail) if detail and not ok else ""))
    if not ok:
        FAILED.append(label)


def own_owner(thingdef):
    """The race's own submersion comp, or None."""
    comps = thingdef.find("comps")
    if comps is None:
        return None
    for li in comps.findall("li"):
        cls = li.get("Class", "")
        if cls.endswith("RM_CompProperties_DrumLure") and (li.findtext("submersionHediff") or "").strip():
            return "RM_CompDrumLure"
        if cls.endswith("CompProperties_SarlaccSwimmer"):
            return "CompSarlaccSwimmer"
    return None


def has_ext(thingdef):
    me = thingdef.find("modExtensions")
    return me is not None and any(li.get("Class") == EXT for li in me.findall("li"))


def has_buried(thingdef):
    me = thingdef.find("modExtensions")
    return me is not None and any((li.get("Class") or "").endswith("RM_SandBuriedGraphicExtension") for li in me.findall("li"))


def scan_defs(roots):
    """defName -> {"ext": bool, "owner": str|None, "buried": bool, "file": path} for every ThingDef with a race."""
    out = {}
    for root in roots:
        for dp, _, fs in os.walk(root):
            for f in fs:
                if not f.endswith(".xml") or os.sep + "Patches" in dp:
                    continue
                p = os.path.join(dp, f)
                try:
                    tree = ET.parse(p)
                except ET.ParseError:
                    continue
                for td in tree.getroot().iter("ThingDef"):
                    name = (td.findtext("defName") or "").strip()
                    if not name or td.find("race") is None:
                        continue
                    out[name] = {"ext": has_ext(td), "owner": own_owner(td), "buried": has_buried(td), "file": p}
    return out


def scan_patches(roots):
    """(file, xpath) of every patch operation whose value adds an RM_SandSwimExtension."""
    hits = []
    for root in roots:
        for dp, _, fs in os.walk(root):
            if os.sep + "Patches" not in dp + os.sep:
                continue
            for f in fs:
                if not f.endswith(".xml"):
                    continue
                p = os.path.join(dp, f)
                try:
                    tree = ET.parse(p)
                except ET.ParseError:
                    continue
                for op in tree.getroot().iter():
                    xp = op.find("xpath")
                    val = op.find("value")
                    if xp is None or val is None:
                        continue
                    if any(li.get("Class") == EXT for li in val.iter("li")):
                        hits.append((p, (xp.text or "").strip()))
    return hits


def conflicts(defs, patches):
    bad = sorted(n for n, d in defs.items() if d["ext"] and d["owner"])
    owned = {n for n, d in defs.items() if d["owner"]}
    for p, xp in patches:
        for n in owned:
            if re.search(r"\b%s\b" % re.escape(n), xp):
                bad.append("%s (patched in %s)" % (n, os.path.relpath(p, REPO)))
    return bad


def main():
    defs = scan_defs([SRC])
    patches = scan_patches([SRC])
    expect("probe: the scan sees races (>=100)", len(defs) >= 100, "%d" % len(defs))
    swimmers = sorted(n for n, d in defs.items() if d["ext"])
    expect("probe: the scan sees >=3 sand-swim consumers", len(swimmers) >= 3, ", ".join(swimmers))
    bad = conflicts(defs, patches)
    expect("no race has two visibility owners", not bad, ", ".join(bad))

    decided = {"RM_Qorrax": ("ext", None), "RM_Vekka": ("ext", None), "RM_Muurrok": ("ext", None),
               "RM_Drazzik": ("own", "RM_CompDrumLure"), "RSW_SarlaccSwimmer": ("own", "CompSarlaccSwimmer"),
               "RM_Duumma": ("none", None)}
    for name, (kind, owner) in decided.items():
        d = defs.get(name)
        if d is None:
            expect("%s found" % name, False, "no race ThingDef named %s under src/" % name)
            continue
        if kind == "ext":
            ok = d["ext"] and d["owner"] is None
        elif kind == "own":
            ok = (not d["ext"]) and d["owner"] == owner
        else:
            ok = (not d["ext"]) and d["owner"] is None and d["buried"]
        expect("%s owner is %s" % (name, owner or ("RM_CompSandSwim" if kind == "ext" else "none (buried dome)")), ok, str(d))

    # probe: the checker flags a def carrying both
    probe = {"T": {"ext": True, "owner": "RM_CompDrumLure", "buried": False, "file": "probe"}}
    expect("probe: a def with both owners is flagged", conflicts(probe, []) == ["T"])
    probe = {"T": {"ext": False, "owner": "CompSarlaccSwimmer", "buried": False, "file": "probe"}}
    expect("probe: a patch adding the extension to an owned race is flagged",
           len(conflicts(probe, [("x.xml", 'Defs/ThingDef[defName="T"]/modExtensions')])) == 1)

    cs = open(COMP_CS, encoding="utf-8").read()
    start = cs[cs.find("class RM_SandSwimStartup"):]
    expect("startup skips a race whose own comp owns submersion",
           "OtherSubmersionOwner(def)" in start and re.search(r"if \(owner != null\)\s*\{[^}]*continue;", start, re.S) is not None)
    expect("startup knows both other owners",
           "RM_CompProperties_DrumLure" in start and "\"CompProperties_SarlaccSwimmer\"" in start)
    sub = cs[cs.find("private void TickSubmerged"):cs.find("private static Thing CurrentAttackTarget")]
    expect("TickSubmerged lays the wake trough", "RecordWakeTrough(pawn, lastCell)" in sub)
    trough = cs[cs.find("private void RecordWakeTrough"):]
    trough = trough[:trough.find("private static Thing CurrentAttackTarget")]
    expect("the trough goes through the kernel and the shared track grid",
           "RM_SandSwimKernel.WakeTroughOffsets(" in trough and "grid.RecordPrint(c, pawn, surface)" in trough
           and "IsSwimTerrain(c, map, Ext)" in trough and "RM_TrackGridDiag.NotedTrough(pawn)" in trough)
    expect("the trough lays no filth Thing", "FilthMaker" not in trough)

    print("selftest_sandswim_owner: %s" % ("FAILED " + ", ".join(FAILED) if FAILED else "OK"))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
