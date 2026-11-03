#!/usr/bin/env python3
"""selftest_sarlacc_seeker_rooting.py -- SARLACC_SEEKER_ROOTING_1: the sarlacc seeker (RM_Gulloth, Stage I) quests for
rich food, then water, then roots -- and roots only in light or extreme desert (owner 2026-10-09: "The lore is that it
converts light desert into extreme desert by absorbing all the water. So either of those two biomes.").

Offline, no game. Checks:
  1. the patch adds CompProperties_SarlaccSwimmer to RM_Gulloth with a kill top-up by body size, a fed threshold,
     seep seeking, dry rooting on, and rootingBiomes == {Desert, ExtremeDesert, RUT_Desert, RUT_ExtremeDesert};
  2. every named biome is a real BiomeDef (vanilla by the Utinni label patch, RUT_ by its own def);
  3. CompSarlaccSwimmer.cs declares each field the patch sets, the biome gate sits before both rooting paths, and the
     bodies of Notify_KilledPawn, KillGain, RootingAllowedHere and SeepRootingAllowed are pinned token for token;
  4. Sarlacc.dll.srchash was built from this CompSarlaccSwimmer.cs;
  5. a Python port of the comp's arithmetic (threshold, kill gain, drain floor, biome gate) over the patch's numbers;
  6. the mod's own validation.py static checks pass.

    python3 src/RimStarWars/Sarlacc/selftest_sarlacc_seeker_rooting.py
"""
import hashlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PATCH = os.path.join(HERE, "Patches", "RSW_SarlaccSeeker_Rooting.xml")
CS = os.path.join(HERE, "Source", "CompSarlaccSwimmer.cs")
SRCHASH = os.path.join(HERE, "Assemblies", "Sarlacc.dll.srchash")
COMP_CLASS = "RimMandrake.StarWars.Sarlacc.CompProperties_SarlaccSwimmer"
DESERTS = {"Desert", "ExtremeDesert", "RUT_Desert", "RUT_ExtremeDesert"}

FAILS = []

# The item's four methods, as they must read. Changing one is a code change that owes this pin a matching edit.
METHOD_BODIES = {
    "public override void Notify_KilledPawn(Pawn pawn)": """
        base.Notify_KilledPawn(pawn);
        if (Props.reserveGainPerKilledBodySize > 0f && pawn != null && pawn.RaceProps != null)
        { reserve += KillGain(pawn.BodySize); }""",
    "public float KillGain(float victimBodySize)": "return Props.reserveGainPerKilledBodySize * victimBodySize;",
    "public bool RootingAllowedHere()": """
        if (Props.rootingBiomes == null || Props.rootingBiomes.Count == 0) { return true; }
        BiomeDef biome = parent.Map?.Biome;
        return biome != null && Props.rootingBiomes.Contains(biome.defName);""",
    "public bool SeepRootingAllowed()":
        "return Props.seepRootMinReserveFraction <= 0f || ReserveFraction >= Props.seepRootMinReserveFraction;",
}


def norm(s):
    """C# text with // and /* */ comments removed and all whitespace dropped."""
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"//[^\n]*", "", s)
    return re.sub(r"\s+", "", s)


def method_body(cs, sig):
    """The brace-matched body of the one method with this signature, normalised; None if absent or not unique."""
    if cs.count(sig) != 1:
        return None
    i = cs.index("{", cs.index(sig))
    depth = 0
    for j in range(i, len(cs)):
        depth += {"{": 1, "}": -1}.get(cs[j], 0)
        if depth == 0:
            return norm(cs[i + 1:j])
    return None


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def patch_comp():
    root = ET.parse(PATCH).getroot()
    for op in root.iter("Operation"):
        xp = op.findtext("xpath") or ""
        if 'defName="RM_Gulloth"' not in xp:
            continue
        for li in op.iter("li"):
            if li.get("Class") == COMP_CLASS:
                return li
    return None


def main():
    li = patch_comp()
    check("patch adds the swimmer comp to RM_Gulloth", li is not None)
    if li is None:
        return
    f = {c.tag: c for c in li}
    num = lambda k: float(f[k].text) if k in f else None  # noqa: E731
    biomes = {x.text for x in f["rootingBiomes"]} if "rootingBiomes" in f else set()
    check("kill top-up by victim body size > 0", (num("reserveGainPerKilledBodySize") or 0) > 0)
    check("fed threshold in (0,1)", 0 < (num("seepRootMinReserveFraction") or 0) < 1)
    check("seeks seeps (radius > detect radius)", (num("seepSeekRadius") or 0) > (num("seepDetectRadius") or 0))
    check("dry rooting on", (f.get("rootWhenReserveRunsOut") is not None and f["rootWhenReserveRunsOut"].text == "true"))
    check("rootingBiomes is exactly light + extreme desert", biomes == DESERTS, sorted(biomes))
    check("anchors into RSW_SarlaccAnchored at RSW_DeepDesertSeep",
          f.get("anchoredDef") is not None and f["anchoredDef"].text == "RSW_SarlaccAnchored"
          and f.get("seepMarkerDef") is not None and f["seepMarkerDef"].text == "RSW_DeepDesertSeep")

    # 2. biome names are real
    names = open(os.path.join(REPO, "src/RimUtinni/UtinniPatches/Patches/BiomeNames_Ashkarr.xml"), encoding="utf-8").read()
    for b in ("Desert", "ExtremeDesert"):
        check("vanilla biome %s is named by the Utinni label patch" % b, 'BiomeDef[defName="%s"]' % b in names)
    for b in ("RUT_Desert", "RUT_ExtremeDesert"):
        p = os.path.join(REPO, "src/RimUtinni/UtinniPatches/Defs/BiomeDefs/%s.xml" % b)
        check("%s is a BiomeDef" % b, os.path.isfile(p) and "<defName>%s</defName>" % b in open(p, encoding="utf-8").read())

    # 3. C# fields and gate order
    cs = open(CS, encoding="utf-8").read()
    for k in f:
        check("comp declares field %s" % k, re.search(r"public [\w<>]+ %s\b" % re.escape(k), cs) is not None)
    tick = cs[cs.index("public override void CompTick()"):cs.index("public bool SeepRootingAllowed()")]
    g = tick.find("RootingAllowedHere()")
    check("biome gate precedes the dry root", 0 <= g < tick.find("RootHere(foundSeep: false)"))
    check("biome gate precedes seep seeking and seep rooting",
          0 <= g < tick.find("SeekSeep();") < tick.find("RootHere(foundSeep: true)"))
    check("empty rootingBiomes means any biome (RSW_SarlaccSwimmer unchanged)",
          "Props.rootingBiomes.Count == 0" in cs)

    # 3b. the bodies of the item's methods, pinned token for token (whitespace and comments ignored): a weakened body --
    # the kill top-up dropped, the biome gate made to answer true, the fed threshold inverted -- goes red here, which the
    # declaration and call-order checks above cannot see (blind check at 8aba11a0, GAP:OTHER).
    for name, want in METHOD_BODIES.items():
        got = method_body(cs, name)
        check("%s body is exactly the item's semantics" % name, got == norm(want), "got %r" % got)
    check("biome gate in CompTick is a plain early return",
          norm("if (!RootingAllowedHere()) { return; }") in norm(tick))
    check("dry root needs an empty reserve and rootWhenReserveRunsOut",
          norm("if (reserve <= 0f && Props.rootWhenReserveRunsOut) { RootHere(foundSeep: false); return; }") in norm(tick))
    check("fed threshold gates seeking and seep rooting in CompTick",
          norm("if (!SeepRootingAllowed()) { return; } SeekSeep();") in norm(tick))
    check("nothing else in the comp writes reserve after a kill (single Notify_KilledPawn)",
          cs.count("Notify_KilledPawn(Pawn pawn)") == 1)

    # 4. srchash matches the source
    want = hashlib.sha256(open(CS, "rb").read()).hexdigest()
    got = [ln.split()[0] for ln in open(SRCHASH, encoding="utf-8") if ln.strip().endswith(" CompSarlaccSwimmer.cs")]
    check("Sarlacc.dll built from this CompSarlaccSwimmer.cs", got == [want], "%s vs %s" % (got, want))

    # 5. arithmetic port, over the patch's own numbers
    top = float(f["startingReserveRange"].text.split("~")[1])
    thr = num("seepRootMinReserveFraction")
    gain = num("reserveGainPerKilledBodySize")

    def frac(r):
        return min(1.0, max(0.0, r / top)) if top > 0 else 0.0

    def seep_ok(r):
        return thr <= 0 or frac(r) >= thr

    def root_ok(biome):
        return not biomes or biome in biomes

    check("hungry seeker does not root at a seep", not seep_ok(top * thr - 1))
    check("fed seeker may root at a seep", seep_ok(top * thr))
    # the gulloth's largest prey is maxPreyBodySize 0.75: one kill helps, but takes a hungry seeker past the threshold only
    # from close below it -- it must feed repeatedly ("quests until it finds rich food")
    check("one max-size kill is less than the fed threshold band", 0 < 0.75 * gain < top * thr)
    r = 10.0
    for _ in range(100000):
        r = max(0.0, r - 1.0 / 60000 * 1.5 * 100)
    check("drain floors at 0, never the -1 re-roll sentinel", r == 0.0)
    for b in ("Desert", "ExtremeDesert", "RUT_Desert", "RUT_ExtremeDesert"):
        check("roots in %s" % b, root_ok(b))
    for b in ("RM_LongShade", "RM_Stillsand", "TemperateForest", "AridShrubland", "RUT_BlueDesert"):
        check("never roots in %s" % b, not root_ok(b))

    # 6. the mod's validation static checks
    sys.path.insert(0, HERE)
    try:
        import validation as V  # noqa: E402
        bad = V.static_checks()
    except Exception as e:  # noqa: BLE001
        bad = ["validation import failed: %r" % e]
    check("validation.py static checks pass", not bad, bad)


if __name__ == "__main__":
    main()
    print("FAILED %d" % len(FAILS) if FAILS else "ALL OK")
    sys.exit(1 if FAILS else 0)
