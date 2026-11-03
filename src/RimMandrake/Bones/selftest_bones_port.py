#!/usr/bin/env python3
"""selftest_bones_port.py — offline proof of BONES_LEAN_PORT_BUILD_TREELESS_WORLD.

The owner's card: a lean port of Bones (sihv.rombonesPort) to our own tier — bone as building stuff, our art
and numbers, no fuel or plasteel routes — then retire the donor, and the 204 ancient walls and doors stuffed
BoneChina in the canonical save must keep loading. Each clause below is checked from the files alone:

  A  RM_Bones is a Woody stuff, defined once in src (in this mod), with our own texture;
  B  RM_BoneAmount (StatPart_BodySize) and the butcher postfix exist; the DLL's stamp matches its sources;
     the kernel's gates (off, not flesh, insect, meat <= 1) hold over a swept input space (a Python mirror of the
     gate line, pinned by text; the compiled behaviour is live clause G3, RM_BonesProof.ProofButcher);
  C  RM_BoneFloor is a floor costing RM_Bones;
  D  no recipe anywhere in src turns RM_Bones into chemfuel, plasteel or polymer;
  E  RM_BonesRetireAliases maps BoneChina, BoneItem, Bonecrete, BonePlastic -> RM_Bones and the donor's five
     floors -> RM_BoneFloor, every target defined in our tree, and the floors' saved shortHashes are distinct;
  F  nothing in src still writes the donor's stat or names the donor's packageId (About, MayRequire, FindMod);
  G  the donor is off every ruled tier mod list and on infrastructure/state/facts/retired_mods.json;
  H  Bones is a composed engine entry of mandrake.rm.biomes (so the alias engine is always co-present).

    python3 src/RimMandrake/Bones/selftest_bones_port.py        exit 0 all clauses hold, 1 any fails
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
REPO = os.path.dirname(SRC)
DONOR_ID = "sihv.rombonesport"
DONOR_NAME = "Rim of Madness - Bones Unofficial Fix"
DONOR_STUFF = ("BoneItem", "BoneChina", "Bonecrete", "BonePlastic")
DONOR_FLOORS = ("BoneFloor", "BoneFloor_Blackened", "BoneFloor_Ashen", "BoneFloor_Tile", "BoneChinaFloor")
TIER_LISTS = ("ModsConfig.FULL.LATEST.xml", "ModsConfig.SHIP.RULED_2026-10-20.xml",
              "ModsConfig.TEST.RULED_2026-10-20.xml", "ModsConfig.AUTHORING.RULED_2026-10-20.xml")
FORBIDDEN_PRODUCTS = ("Chemfuel", "Plasteel", "BonePlastic")

fails: list[str] = []
counts: dict[str, int] = {}


def check(ok: bool, what: str) -> None:
    if not ok:
        fails.append(what)


def xml_files(root: str):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "northstar", "obj", "bin")]
        for f in fn:
            if f.endswith(".xml"):
                yield os.path.join(dp, f)


def parse(path: str):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        return None


# ---- one pass over every XML file in src (comments are dropped by ElementTree, so text checks see live XML)
defs_by_name: dict[str, list[tuple[str, ET.Element]]] = {}
abstract_by_name: dict[str, ET.Element] = {}
live_texts: list[tuple[str, str]] = []
n_files = 0
unparsed: list[str] = []
for p in xml_files(SRC):
    r = parse(p)
    if r is None:
        unparsed.append(p)
        raw = open(p, "rb").read().decode("utf-8", "replace").lower()
        if p.startswith(HERE) or "boneamount" in raw or DONOR_ID in raw or "rm_bones" in raw:
            fails.append("sanity: %s does not parse, and it is one this proof must read" % os.path.relpath(p, REPO))
        continue
    n_files += 1
    live_texts.append((p, ET.tostring(r, encoding="unicode")))
    if r.tag == "Defs":
        for d in r:
            if d.get("Name"):
                abstract_by_name[d.get("Name")] = d
            dn = d.findtext("defName")
            if dn:
                defs_by_name.setdefault(dn, []).append((p, d))
counts["xml files parsed"] = n_files
counts["defs indexed"] = len(defs_by_name)
counts["xml files unparsed (ignored unless bone-related)"] = len(unparsed)
check(n_files > 1000 and len(defs_by_name) > 5000, "sanity: the src scan saw only %d files / %d defs" % (n_files, len(defs_by_name)))

rel = lambda p: os.path.relpath(p, REPO)

# ---- A. RM_Bones
bones = defs_by_name.get("RM_Bones", [])
check(len(bones) == 1, "A: RM_Bones defined %d times (want 1): %s" % (len(bones), [rel(p) for p, _ in bones]))
if bones:
    p, d = bones[0]
    check(p.startswith(HERE), "A: RM_Bones lives in %s, not in the Bones mod" % rel(p))
    cats = [li.text for li in d.findall("stuffProps/categories/li")]
    check(cats == ["Woody"], "A: RM_Bones stuff categories %r (want ['Woody'])" % cats)
    tex = d.findtext("graphicData/texPath")
    tdir = os.path.join(HERE, "Textures", *tex.split("/")) if tex else ""
    pngs = [f for f in os.listdir(tdir) if f.endswith(".png")] if tdir and os.path.isdir(tdir) else []
    check(len(pngs) >= 1, "A: RM_Bones texPath %r has no PNG in the Bones mod" % tex)
    counts["RM_Bones textures"] = len(pngs)

# ---- B. stat, postfix, DLL stamp, kernel
stat = defs_by_name.get("RM_BoneAmount", [])
check(len(stat) == 1 and stat[0][1].tag == "StatDef", "B: RM_BoneAmount StatDef defined %d times" % len(stat))
if stat:
    parts = [li.get("Class") for li in stat[0][1].findall("parts/li")]
    check("StatPart_BodySize" in parts, "B: RM_BoneAmount lacks StatPart_BodySize (megafauna yields assume it)")
    check(stat[0][1].findtext("defaultBaseValue") == "50", "B: RM_BoneAmount default is not 50 (gen_megafauna_yield BONE_UNIT)")
cs_dir = os.path.join(HERE, "Source")
patch_cs = open(os.path.join(cs_dir, "RM_Patch_ButcherBones.cs"), encoding="utf-8").read()
check("[HarmonyPatch(typeof(Pawn), nameof(Pawn.ButcherProducts))]" in patch_cs, "B: butcher postfix target missing")
check("RM_BonesKernel.ExpectedBones(" in patch_cs and "GenMath.RoundRandom(expected)" in patch_cs,
      "B: postfix does not route through the kernel and RoundRandom")
kern = open(os.path.join(cs_dir, "Kernel", "RM_BonesKernel.cs"), encoding="utf-8").read()
check("if (!enabled || !isFlesh || isInsect || meatCount <= 1)" in kern, "B: kernel gate line changed; re-mirror it here")
csproj = open(os.path.join(cs_dir, "RM_Bones.csproj"), encoding="utf-8").read()
for dp, dn_, fn in os.walk(cs_dir):
    dn_[:] = [d for d in dn_ if d not in ("obj", "bin")]
    for f in fn:
        if f.endswith(".cs"):
            r_ = os.path.relpath(os.path.join(dp, f), cs_dir).replace("/", "\\")
            check('<Compile Include="%s" />' % r_ in csproj, "B: %s is not compiled (csproj)" % r_)
stamp_p = os.path.join(HERE, "Assemblies", "RimMandrake.Bones.dll.srchash")
dll_p = os.path.join(HERE, "Assemblies", "RimMandrake.Bones.dll")
compiled = {os.path.normpath(os.path.join(cs_dir, c.replace("\\", "/")))
            for c in re.findall(r'<Compile Include="([^"]+)"', csproj)}
if os.path.exists(stamp_p) and os.path.exists(dll_p):
    stamped: set[str] = set()
    dll_headers = 0
    for line in open(stamp_p, encoding="utf-8").read().splitlines():
        if line.startswith("# dll: "):
            dll_headers += 1
            check(hashlib.sha256(open(dll_p, "rb").read()).hexdigest() == line[7:].strip(), "B: DLL bytes differ from its stamp")
        elif line and not line.startswith("#"):
            h, f = line.split(" ", 1)
            fp = os.path.normpath(os.path.join(cs_dir, f))
            ok = os.path.exists(fp) and hashlib.sha256(open(fp, "rb").read()).hexdigest() == h
            check(ok, "B: DLL stamp is stale for %s (rebuild: winbuild.py Bones)" % f)
            check(fp not in stamped, "B: DLL stamp lists %s twice" % f)
            stamped.add(fp)
    counts["stamped sources"] = len(stamped)
    check(dll_headers == 1, "B: DLL stamp has %d '# dll:' headers (want 1)" % dll_headers)
    check(stamped == compiled, "B: DLL stamp covers %d sources, csproj compiles %d (rebuild)" % (len(stamped), len(compiled)))
else:
    fails.append("B: RimMandrake.Bones.dll or its .srchash is missing")


def expected_bones(enabled, is_flesh, is_insect, meat, amount, mult, eff):  # mirror of RM_BonesKernel.ExpectedBones
    if not enabled or not is_flesh or is_insect or meat <= 1:
        return 0.0
    if amount <= 0 or mult <= 0 or eff <= 0:
        return 0.0
    return amount * min(mult, 5.0) * eff


swept = 0
for en in (False, True):
    for fl in (False, True):
        for ins in (False, True):
            for meat in (0, 1, 2, 140, 5000):
                for amt in (0.0, 12.5, 50.0, 2200.0):
                    for mult in (0.0, 1.0, 5.0, 9.0):
                        for eff in (0.0, 0.5, 1.0, 1.3):
                            v = expected_bones(en, fl, ins, meat, amt, mult, eff)
                            swept += 1
                            gated = (not en) or (not fl) or ins or meat <= 1
                            if gated and v != 0:
                                fails.append("B: kernel yields %s through a shut gate" % v)
                            if v < 0 or v > amt * 5.0 * max(eff, 0) + 1e-9:
                                fails.append("B: kernel out of range %s" % v)
counts["kernel cases swept"] = swept
check(expected_bones(True, True, False, 140, 50.0, 1.0, 1.0) == 50.0, "B: human-sized body does not yield 50")

# ---- C. floor
fl = defs_by_name.get("RM_BoneFloor", [])
check(len(fl) == 1 and fl[0][1].tag == "TerrainDef", "C: RM_BoneFloor TerrainDef defined %d times" % len(fl))
if fl:
    check(fl[0][1].find("costList/RM_Bones") is not None, "C: RM_BoneFloor does not cost RM_Bones")

# ---- D. no fuel / plasteel / polymer route from bone
recipes_with_bone = 0
recipe_defs = sum(1 for v in defs_by_name.values() for _, d in v if d.tag == "RecipeDef")
counts["recipe defs seen"] = recipe_defs
check(recipe_defs > 50, "D: sanity: the scan sees only %d RecipeDefs, so 'no bone recipe' proves nothing" % recipe_defs)
def chain(d: ET.Element):  # the def and its ParentName ancestors (within src)
    seen = 0
    while d is not None and seen < 32:
        yield d
        d = abstract_by_name.get(d.get("ParentName") or "")
        seen += 1


for name, rows in defs_by_name.items():
    for p, rd in rows:
        if rd.tag != "RecipeDef":
            continue
        links = list(chain(rd))
        if not any("RM_Bones" in ET.tostring(x, encoding="unicode") for x in links):
            continue
        recipes_with_bone += 1
        prods = {c.tag for x in links for c in x.findall("products/*")}
        bad = sorted(prods & set(FORBIDDEN_PRODUCTS))
        check(not bad, "D: %s turns RM_Bones into %s (%s)" % (name, bad, rel(p)))
for p, text in live_texts:  # any patch that puts bone into a recipe is read by a human, whatever it produces
    if "/Patches/" in p.replace(os.sep, "/") and "RM_Bones" in text and "RecipeDef" in text:
        fails.append("D: %s patches RM_Bones into a RecipeDef; check it adds no fuel/plasteel/polymer route" % rel(p))
counts["recipes naming RM_Bones"] = recipes_with_bone

# ---- E. aliases
alias_defs = defs_by_name.get("RM_BonesRetireAliases", [])
check(len(alias_defs) == 1, "E: RM_BonesRetireAliases defined %d times" % len(alias_defs))
amap: dict[str, tuple[str, str]] = {}
if alias_defs:
    ad = alias_defs[0][1]
    check(ad.tag == "RimMandrake.EnvironmentalHazards.RM_DefAliasDef", "E: alias def class is %s" % ad.tag)
    for li in ad.findall("aliases/li"):
        amap[li.findtext("from")] = (li.findtext("to"), li.findtext("defType") or "")
for n in DONOR_STUFF:
    check(amap.get(n) == ("RM_Bones", "ThingDef"), "E: %s -> %r (want RM_Bones, ThingDef)" % (n, amap.get(n)))
for n in DONOR_FLOORS:
    check(amap.get(n) == ("RM_BoneFloor", "TerrainDef"), "E: %s -> %r (want RM_BoneFloor, TerrainDef)" % (n, amap.get(n)))
for frm, (to, _) in amap.items():
    check(to in defs_by_name, "E: alias target %s is not defined in src" % to)
    check(frm not in defs_by_name, "E: alias source %s is still a live def in src (the alias would never apply)" % frm)
alias_engine = os.path.join(SRC, "RimMandrake", "EnvironmentalHazards", "Source", "RM_DefAliases.cs")
check("class RM_DefAliasDef : Def" in open(alias_engine, encoding="utf-8").read(), "E: RM_DefAliasDef engine missing")


def stable_string_hash(s: str) -> int:  # Verse.GenText.StableStringHash (int32 wraparound)
    num = 23
    for ch in s:
        num = (num * 31 + ord(ch)) & 0xFFFFFFFF
    return num - (1 << 32) if num >= (1 << 31) else num


def saved_hash(s: str) -> int:  # (ushort)(StableStringHash(s) % 65535), C# remainder truncates toward zero
    h = stable_string_hash(s)
    r = abs(h) % 65535 * (1 if h >= 0 else -1)
    return r & 0xFFFF


hashes = {saved_hash(n): n for n in DONOR_FLOORS}
check(len(hashes) == len(DONOR_FLOORS), "E: two donor floors share a saved shortHash: %r" % hashes)
counts["alias rows"] = len(amap)

# ---- F. nothing writes the donor's stat or names the donor
writers = []
for p, text in live_texts:
    low = text.lower()
    if re.search(r"<BoneAmount\b|/BoneAmount\b|\[BoneAmount\]", text):
        writers.append(rel(p) + " writes BoneAmount")
    # the Bones mod's About <description> credits the donor (MIT attribution); its other fields are checked below
    if DONOR_ID in low and not p.startswith(os.path.join(SRC, "Jawa")) and p != os.path.join(HERE, "About", "About.xml"):
        writers.append(rel(p) + " names " + DONOR_ID)
    if DONOR_NAME.lower() in low:
        writers.append(rel(p) + " FindMods the donor")
    for n in DONOR_STUFF + DONOR_FLOORS + ("BoneWall", "BoneRefine", "BoneRefineII"):
        if not (alias_defs and p == alias_defs[0][0]):
            if re.search(r'(>|"|\[defName=")%s(<|"|\])' % re.escape(n), text):
                writers.append(rel(p) + " names donor def " + n)
about = ET.parse(os.path.join(HERE, "About", "About.xml")).getroot()
about.remove(about.find("description"))
if DONOR_ID in ET.tostring(about, encoding="unicode").lower():
    writers.append("Bones About.xml names %s outside its description" % DONOR_ID)
cs_files = 0
donor_lit = re.compile(r'"(%s)"' % "|".join(map(re.escape, DONOR_STUFF + DONOR_FLOORS + ("BoneAmount", "BoneWall"))))
for dp, dn, fn in os.walk(SRC):
    dn[:] = [d for d in dn if d not in (".git", "obj", "bin")]
    for f in fn:
        if f.endswith(".cs"):
            cs_files += 1
            fp = os.path.join(dp, f)
            if fp == os.path.join(HERE, "Source", "RM_BonesProof.cs"):  # names donor defs to prove they are absent
                continue
            t_ = re.sub(r"//[^\n]*|/\*.*?\*/", "", open(fp, encoding="utf-8", errors="replace").read(), flags=re.S)
            if donor_lit.search(t_) or DONOR_ID in t_.lower():
                writers.append(rel(fp) + " names a donor def or the donor in C#")
counts["cs files scanned"] = cs_files
check(cs_files > 300, "F: sanity: only %d C# files scanned" % cs_files)
check(not writers, "F: live donor references: %s" % writers[:12])
counts["donor references"] = len(writers)

# ---- G. retired
for f in TIER_LISTS:
    p = os.path.join(REPO, "infrastructure", "state", "modlists", f)
    ids = [li.text.strip().lower() for li in ET.parse(p).getroot().find("activeMods")]
    check(len(ids) > 100, "G: %s parsed only %d mods (instrument)" % (f, len(ids)))
    check(DONOR_ID not in ids, "G: %s still lists %s" % (f, DONOR_ID))
ret = json.load(open(os.path.join(REPO, "infrastructure", "state", "facts", "retired_mods.json"), encoding="utf-8"))
check(any(r.get("packageId", "").lower() == DONOR_ID for r in ret["retired"]), "G: retired_mods.json lacks %s" % DONOR_ID)

# ---- H. composed
comp = json.load(open(os.path.join(SRC, "RimMandrake", "Biomes.compose.json"), encoding="utf-8"))
ent = [e for e in comp["entries"] if e["key"] == "Bones"]
check(len(ent) == 1 and ent[0]["source"] == "Bones" and ent[0]["wave"] <= comp["compose_wave"],
      "H: Bones is not a composed entry of mandrake.rm.biomes")
keys = [e["key"] for e in comp["entries"]]
eh = [e for e in comp["entries"] if e["key"] == "EnvironmentalHazards"]
check(bool(ent) and len(eh) == 1 and eh[0]["wave"] <= comp["compose_wave"]
      and keys.index("EnvironmentalHazards") < keys.index("Bones"),
      "H: EnvironmentalHazards (the alias engine) is not composed before Bones")

print("counts: " + ", ".join("%s=%d" % kv for kv in counts.items()))
if fails:
    print("FAIL (%d)" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("PASS: BONES_LEAN_PORT_BUILD_TREELESS_WORLD offline clauses A-H hold")
