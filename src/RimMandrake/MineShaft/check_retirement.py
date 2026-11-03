"""check_retirement.py -- Mines 2.0 (cain.mineshaft) stays retired and our shaft (mandrake.rm.mineshaft) replaces it.

    python3 src/RimMandrake/MineShaft/check_retirement.py        exit 0 holds, 1 a claim is false

Item MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG (design/RimMandrake/mines_mod_assessment_20261011.md section 6). Offline, read-only:
  * ModsConfig.FULL.LATEST.xml (parsed, never grepped) carries mandrake.rm.mineshaft and neither retired mod;
  * both retired mods are in infrastructure/state/facts/retired_mods.json (through its own reader);
  * no src About.xml names either retired mod in loadAfter / forceLoadAfter / loadBefore;
  * the Mines 2.0 C# gate and its kernel, setting and prove pieces are gone from src (names below);
  * the Armoury canon policy (the single list now) bars the nine products the gate and its extension barred.
Sanity probes keep each read honest: the list parse must see the Armoury, the About scan must see a loadAfter list, and the
name scan must see the policy file it is told to skip.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "src")
FULL = os.path.join(REPO, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
POLICY = os.path.join(SRC, "RimStarWars", "Armoury", "Defs", "ThingDefs", "RSW_MineShaftCanonPolicy.xml")
RETIRED = ("cain.mineshaft", "leutiankane.mines2patchouterrim")
OURS = "mandrake.rm.mineshaft"
GONE_NAMES = ("RSW_MineShaftCanonGate", "MineShaftBanned", "MineShaftPrefixes", "UnlistMineShaft", "IsMineShaftBanned",
              "IsMineShaftRecipe", "mineShaftCanonGateEnabled", "mineshaft_check(kernel")
BARRED = ("KOTOR_IngotBeskar", "KOTOR_RawBeskar", "OuterRim_Beskar", "OuterRim_PureBeskar", "RSW_Durasteel", "KotORChunk_durasteel",
          "Plasteel", "RSW_DooniumOre", "OuterRim_ComponentHypertech")
SELF = os.path.abspath(__file__)


def check_list(path=FULL):
    mods = [li.text for li in ET.parse(path).find("activeMods")]
    if "mandrake.rsw.armoury" not in mods:
        return ["SANITY: FULL.LATEST parse sees no mandrake.rsw.armoury (%d mods): the read is blind" % len(mods)]
    bad = ["FULL.LATEST still loads %s" % m for m in RETIRED if m in mods]
    if OURS not in mods:
        bad.append("FULL.LATEST does not load %s" % OURS)
    elif mods.index(OURS) > mods.index("mandrake.rsw.armoury"):
        bad.append("%s loads after the Armoury, whose policy def uses its class" % OURS)
    return bad


def check_retired_json():
    sys.path.insert(0, os.path.join(SRC, "RimMandrake", "Utils"))
    import retired_mods
    bad = ["retired_mods.json lacks %s" % m for m in RETIRED if not retired_mods.is_retired(m)]
    if retired_mods.is_retired(OURS):
        bad.append("retired_mods.json marks our own %s retired" % OURS)
    return bad


def check_about(root=SRC):
    bad, lists = [], 0
    for dp, _, fs in os.walk(root):
        if os.path.basename(dp) != "About" or "About.xml" not in fs:
            continue
        p = os.path.join(dp, "About.xml")
        try:
            r = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for tag in ("loadAfter", "forceLoadAfter", "loadBefore", "forceLoadBefore"):
            for el in r.findall(tag):
                lists += 1
                for li in el.findall("li"):
                    if (li.text or "").strip().lower() in RETIRED:
                        bad.append("%s %s names %s" % (os.path.relpath(p, REPO), tag, li.text.strip()))
    if lists == 0:
        bad.append("SANITY: no loadAfter list found in any src About.xml: the scan is blind")
    return bad


def check_names(root=SRC):
    bad, seen_policy = [], False
    pat = re.compile("|".join(re.escape(n) for n in GONE_NAMES))
    for dp, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in ("obj", "bin", ".git")]
        for f in fs:
            if not f.endswith((".cs", ".py", ".xml", ".csproj")):
                continue
            p = os.path.abspath(os.path.join(dp, f))
            if p == SELF:
                continue
            if p == os.path.abspath(POLICY):
                seen_policy = True
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in set(pat.findall(t)):
                bad.append("%s still names %s" % (os.path.relpath(p, REPO), m))
    if not seen_policy:
        bad.append("SANITY: the name scan never reached %s: it is blind" % os.path.relpath(POLICY, REPO))
    return bad


def check_policy(path=POLICY):
    r = ET.parse(path).getroot()
    defs = [d for d in r if d.tag == "RimMandrake.MineShaft.MineShaftPolicyDef"]
    if not defs:
        return ["no MineShaftPolicyDef in %s" % os.path.relpath(path, REPO)]
    have = {li.text for d in defs for li in d.findall("bannedProducts/li")}
    bad = ["canon policy does not bar %s" % p for p in BARRED if p not in have]
    bad += ["canon policy %s is not guarded by MayRequire=\"%s\"" % (d.findtext("defName"), OURS) for d in defs if d.get("MayRequire") != OURS]
    return bad


def main():
    bad = []
    for name, fn in (("list", check_list), ("retired_mods", check_retired_json), ("about", check_about),
                     ("names", check_names), ("policy", check_policy)):
        b = fn()
        print("%-13s %s" % (name, "PASS" if not b else "FAIL"))
        for x in b:
            print("    " + x)
        bad += b
    print("RESULT", "PASS" if not bad else "FAIL (%d)" % len(bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
