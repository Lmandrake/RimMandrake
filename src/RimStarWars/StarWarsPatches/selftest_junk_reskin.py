"""selftest_junk_reskin.py -- STARWARS_JUNK_RESKIN_1: vanilla ancient junk drawn as Star Wars wrecks. L0 (static).

Checks Patches/AncientJunk_StarWarsReskin.xml against the 24 Core defs of the spec
(design/RimMandrake/starwars_junk_reskin_2026-10-03.md section 2), the judge's verdict file
(infrastructure/state/delegated/2026-11-03/STARWARS_JUNK_RESKIN_1.json) and the texture folders:

  * every operation sits inside ONE RSW_PatchOperationStarWarsPatchesSetting gate on `junkReskin`, and that
    setting exists in the C# switch and the settings class (default on);
  * each of the 24 defs gets texPath -> Things/Building/Ruins/RSW_Junk/<def>, a label and a description, and
    graphicClass -> Graphic_Random exactly when Core's is not already Graphic_Random;
  * nothing else is touched (appearance only: no size/drawSize/HP/passability/killedLeavings);
  * every xpath selects exactly one node in Core's own def file (lxml, XPath 1.0 as RimWorld's XmlDocument).
    validate_patch.py cannot do this: it does not descend into a custom PatchOperation class;
  * each folder holds >= 1 PNG, every PNG is a judge-KEEP picture installed from the verdict file (sha256 match),
    RGBA, at the def's canvas; AncientPodCar_00 is the former WreckedLandspeeder.png byte for byte;
  * PodCarIsLandspeeder.xml and WreckedLandspeeder.png are gone (folded in, not duplicated);
  * the committed DLL matches its .srchash (DLL bytes and every compiled source).
Sanity probes prove each instrument can see: a mutated defName must miss in Core, a drawSize xpath must be caught.
"""
import hashlib
import json
import os
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PATCH = os.path.join(HERE, "Patches", "AncientJunk_StarWarsReskin.xml")
TEX = os.path.join(HERE, "Textures", "Things", "Building", "Ruins", "RSW_Junk")
VERDICT = os.path.join(REPO, "infrastructure", "state", "delegated", "2026-11-03", "STARWARS_JUNK_RESKIN_1.json")
SRC = os.path.join(HERE, "Source", "StarWarsPatches")
DLL = os.path.join(HERE, "Assemblies", "RimMandrakeStarWarsPatches.dll")
GATE = "RimMandrake.StarWars.Patches.RSW_PatchOperationStarWarsPatchesSetting"
CORE_FILE = "Core/Defs/ThingDefs_Buildings/Buildings_Ancient_Outdoors.xml"
CORE_ROOTS = [os.environ.get("RIMWORLD_DATA") or "",
              "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"]
POD00_SHA = "99af270dae43cd631d5fc3b1af4b74ada3704a2466e3460b30b7bd26a824a7ae"   # WreckedLandspeeder.png, 2026-08-24

# spec section 2: defName -> drawSize (cells). AncientWheel has none (inherits 1x1).
DEFS = {
    "AncientRustedCar": (2, 4), "AncientRustedCarFrame": (2, 3), "AncientPodCar": (3, 2),
    "AncientRustedEngineBlock": (1, 1), "AncientWheel": (1, 1), "AncientGiantWheel": (2, 2),
    "AncientTankTrap": (2, 2), "AncientAPC": (5, 3), "AncientTank": (5, 3), "AncientRustedJeep": (3, 5),
    "AncientLargeRustedEngineBlock": (2, 1), "AncientWarwalkerClaw": (1, 2), "AncientWarwalkerLeg": (2, 4),
    "AncientWarwalkerFoot": (2, 2), "AncientWarwalkerTorso": (4, 6), "AncientWarwalkerShell": (5, 3),
    "AncientWarspiderRemains": (5, 5), "AncientMiniWarwalkerRemains": (5, 3), "AncientJetEngine": (3, 2),
    "AncientDropshipEngine": (3, 2), "AncientRustedDropship": (6, 5), "AncientMegaCannonBarrel": (1, 2),
    "AncientMegaCannonTripod": (3, 3), "AncientRustedTruck": (2, 4),
}
ALLOWED = {"graphicData/texPath", "graphicData/graphicClass", "label", "description"}
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def canvas(w, h):
    """drawSize x 128 px, doubled until the long side reaches 512 (spec section 5)."""
    w, h = w * 128, h * 128
    while max(w, h) < 512:
        w, h = w * 2, h * 2
    return w, h


def ops_of(root):
    """[(defName, field, value element)] for every Replace in the gate, plus problems with the gate itself."""
    probs, out = [], []
    top = root.findall("Operation")
    if len(top) != 1 or top[0].get("Class") != GATE:
        return ["expected exactly one top-level %s, found %s" % (GATE, [t.get("Class") for t in top])], out
    g = top[0]
    if (g.findtext("setting") or "").strip() != "junkReskin":
        probs.append("gate setting is %r, not 'junkReskin'" % g.findtext("setting"))
    if g.find("nomatch") is not None:
        probs.append("gate has a nomatch branch: off must leave vanilla untouched")
    seq = g.find("match")
    if seq is None or seq.get("Class") != "PatchOperationSequence":
        return probs + ["gate match is not a PatchOperationSequence"], out
    for li in seq.find("operations").findall("li"):
        xp = (li.findtext("xpath") or "").strip()
        if li.get("Class") != "PatchOperationReplace" or li.get("MayRequire"):
            probs.append("op %s is %s (MayRequire=%s), want plain PatchOperationReplace" % (xp, li.get("Class"), li.get("MayRequire")))
        pre = '/Defs/ThingDef[defName="'
        if not xp.startswith(pre) or '"]/' not in xp:
            probs.append("xpath %r is not /Defs/ThingDef[defName=\"X\"]/field" % xp)
            continue
        d, field = xp[len(pre):].split('"]/', 1)
        val = li.find("value")
        out.append((d, field, xp, val))
    return probs, out


def core_doc():
    for r in CORE_ROOTS:
        p = os.path.join(r, CORE_FILE) if r else ""
        if p and os.path.isfile(p):
            return etree.parse(p), p
    return None, None


def main():
    root = etree.parse(PATCH).getroot()
    probs, ops = ops_of(root)
    check("one junkReskin gate wraps every operation, no nomatch, plain Replaces", not probs, probs[:5])

    by_def = {}
    for d, field, xp, val in ops:
        by_def.setdefault(d, {})[field] = (xp, val)
    check("the patch covers exactly the 24 spec defs", set(by_def) == set(DEFS),
          sorted(set(by_def) ^ set(DEFS)))
    extra = sorted("%s/%s" % (d, f) for d, fs in by_def.items() for f in fs if f not in ALLOWED)
    check("appearance only: no field but texPath/graphicClass/label/description", not extra, extra)
    # probe: the same rule must catch a drawSize edit
    check("probe: a drawSize xpath would be caught", "graphicData/drawSize" not in ALLOWED)

    core, core_path = core_doc()
    check("Core's Buildings_Ancient_Outdoors.xml is readable (RIMWORLD_DATA or the Steam path)", core is not None, CORE_ROOTS)
    if core is not None:
        miss = [xp for d, f, xp, v in ops if len(core.xpath(xp)) != 1]
        check("every xpath selects exactly one node in Core", not miss, miss[:5])
        probe = ops[0][2].replace(ops[0][0], ops[0][0] + "ZZ")
        check("probe: a mutated defName selects nothing in Core", len(core.xpath(probe)) == 0, probe)
        for d in DEFS:
            fs = by_def.get(d, {})
            gc = core.xpath('/Defs/ThingDef[defName="%s"]/graphicData/graphicClass/text()' % d)
            need_gc = (gc[0].strip() if gc else "") != "Graphic_Random"
            tp = fs.get("graphicData/texPath")
            ok = (tp is not None and (tp[1].findtext("texPath") or "") == "Things/Building/Ruins/RSW_Junk/" + d
                  and "label" in fs and (fs["label"][1].findtext("label") or "").strip()
                  and "description" in fs and len((fs["description"][1].findtext("description") or "").strip()) > 40
                  and (("graphicData/graphicClass" in fs) == need_gc)
                  and (not need_gc or fs["graphicData/graphicClass"][1].findtext("graphicClass") == "Graphic_Random"))
            check("%s: texPath folder, label, description, graphicClass %s" % (d, "-> Random" if need_gc else "left Random"), ok)

    v = json.load(open(VERDICT))
    keep = {x["picture"] for x in v["verdicts"] if x.get("verdict") == "KEEP"}
    inst = {s["rel"]: s["sha"] for s in v["installed"].values()}
    check("every installed picture is a judge KEEP", all(s in keep for s in inst.values()),
          [r for r, s in inst.items() if s not in keep][:3])
    from PIL import Image
    for d, (w, h) in DEFS.items():
        folder = os.path.join(TEX, d)
        pngs = sorted(f for f in os.listdir(folder) if f.endswith(".png")) if os.path.isdir(folder) else []
        bad = []
        for f in pngs:
            p, rel = os.path.join(folder, f), "Things/Building/Ruins/RSW_Junk/%s/%s" % (d, f)
            s = sha(p)
            im = Image.open(p)
            if f == "RSW_Junk_AncientPodCar_00.png":
                if s != POD00_SHA:
                    bad.append(f + " is not the former WreckedLandspeeder.png")
                continue
            if inst.get(rel) != s:
                bad.append(f + " not installed from the verdict file (sha mismatch or unlisted)")
            if im.mode != "RGBA" or im.size != canvas(w, h):
                bad.append("%s %s %s, want RGBA %s" % (f, im.mode, im.size, canvas(w, h)))
        check("%s: %d variant PNG(s), all judged KEEP, RGBA at canvas" % (d, len(pngs)), pngs and not bad, bad[:3])
    check("every verdict install is on disk", all(os.path.isfile(os.path.join(HERE, "Textures", r)) for r in inst),
          [r for r in inst if not os.path.isfile(os.path.join(HERE, "Textures", r))][:3])
    check("PodCarIsLandspeeder.xml folded in and removed", not os.path.exists(os.path.join(HERE, "Patches", "PodCarIsLandspeeder.xml")))
    check("WreckedLandspeeder.png moved, not duplicated",
          not os.path.exists(os.path.join(HERE, "Textures", "Things", "Building", "Ruins", "WreckedLandspeeder.png")))

    gate_cs = open(os.path.join(SRC, "RSW_PatchOperationStarWarsPatchesSetting.cs")).read()
    set_cs = open(os.path.join(SRC, "RSW_StarWarsPatchesSettings.cs")).read()
    check("C# gate switch knows 'junkReskin'", 'case "junkReskin":' in gate_cs)
    check("settings: junkReskin defaults on and is saved",
          "DefaultJunkReskin = true" in set_cs and 'Scribe_Values.Look(ref junkReskin, "junkReskin", DefaultJunkReskin)' in set_cs)
    stamp = open(DLL + ".srchash").read().splitlines()
    dll_line = [l for l in stamp if l.startswith("# dll:")]
    stale = []
    if not dll_line or dll_line[0].split(":", 1)[1].strip() != sha(DLL):
        stale.append("dll bytes")
    for l in stamp:
        if l and not l.startswith("#"):
            h, rel = l.split(" ", 1)
            p = os.path.normpath(os.path.join(SRC, rel))
            if not os.path.isfile(p) or sha(p) != h:
                stale.append(rel)
    check("DLL matches its .srchash (bytes and every compiled source)", not stale, stale)

    print("%d junk-reskin selftest(s) FAILED" % len(FAILS) if FAILS else "all junk-reskin checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
