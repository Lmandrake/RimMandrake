#!/usr/bin/env python3
"""Static cross-check of LanternDeeps: XML defs <-> C# classes/fields, csproj <-> source files, and the strings
the C# looks defs and translation keys up by. No game, no build. Exits 1 with one line per finding.

    python3 src/RimMandrake/Utils/selftest_lanterndeeps_lint.py

Checks (each prints its count so a check that looked at nothing cannot pass silently):
  1. every Class="RimMandrake.LanternDeeps.X" / thingClass / compClass / giverClass in Defs+Patches names a class in Source
  2. every child element of such a Class node is a public field of that class (an unknown field is silently ignored by the loader)
  3. every Source/*.cs is in the csproj Compile list and every Compile entry exists
  4. every "RM_/RUT_/RSW_" string literal in Source resolves to a defName or <li> tag somewhere under src/ or to a Keyed translation key
  5. every "...".Translate() key (RM_ prefixed) exists in Languages/English/Keyed
  6. DeepCollapseState's saved fields (due, forced) are Scribed under their own names (released stays transient); no Scribe name is used
     twice in a class; both kernels are in the mod csproj and the selftest csproj and carry no Verse/RimWorld/UnityEngine/Harmony using
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))          # .../src
MOD = os.path.join(SRC, "RimMandrake", "LanternDeeps")
NS = "RimMandrake.LanternDeeps."
fails = []
counts = {}


def fail(msg):
    fails.append(msg)


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


# ---------- C# classes and their public fields
classes = {}      # name -> (file, set(fields), base)
cs_files = sorted(glob.glob(os.path.join(MOD, "Source", "*.cs")))
for f in cs_files:
    txt = strip_comments(open(f, encoding="utf-8").read())
    for m in re.finditer(r"\bpublic\s+(?:static\s+|abstract\s+|sealed\s+)*class\s+(\w+)(?:\s*:\s*([\w.<>, ]+))?\s*\{", txt):
        name, base = m.group(1), (m.group(2) or "")
        # body = brace-matched
        i = m.end(); depth = 1
        while depth and i < len(txt):
            depth += (txt[i] == "{") - (txt[i] == "}")
            i += 1
        body = txt[m.end():i]
        fields = set(re.findall(r"\bpublic\s+(?!static\b|const\b|override\b|class\b|void\b)[\w<>\[\],.? ]+?\s+(\w+)\s*(?:=[^;]*)?;", body))
        classes[name] = (os.path.basename(f), fields, base.split(",")[0].strip())


def has_foreign_base(name, seen=()):
    """True when the class chain ends in a base outside Source/ (a vanilla class) whose public fields we cannot see."""
    if name in seen or name not in classes:
        return False
    b = classes[name][2]
    if not b or b in ("DefModExtension", "object"):
        return False
    return True if b not in classes else has_foreign_base(b, seen + (name,))


def foreign_root(name):
    while name in classes and classes[name][2] in classes:
        name = classes[name][2]
    return classes[name][2] if name in classes else ""


# the XML-settable fields of the vanilla bases these mods derive from (from the decompiled 1.6 source); a base not listed is unverifiable
VANILLA = {
    "CompProperties": {"compClass"},
    "GenStep": set(),
    "DeathActionProperties": {"workerClass"},
    "ThinkNode_JobGiver": {"priority"},
    "GenStep_ScatterGroup": {"allowInWaterBiome", "allowOnWater", "allowRoofed", "clearSpaceSize", "countPer10kCellsRange", "extraNoBuildEdgeDist",
                             "minSpacing", "minSpacingIgnoreTerrain", "nearMapCenter", "neverOnDamagedTerrain", "spotMustBeStandable",
                             "terrainValidationRadius", "terrainValidator", "validators", "warnOnFail", "groups"},
}


def all_fields(name, seen=()):
    if name not in classes or name in seen:
        return set()
    return classes[name][1] | all_fields(classes[name][2], seen + (name,))


# ---------- 1 + 2: XML references
n_refs = 0; n_children = 0
xmls = glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True) + glob.glob(os.path.join(MOD, "Patches", "*.xml"))
for x in xmls:
    try:
        root = ET.parse(x).getroot()
    except ET.ParseError as e:
        fail("%s: XML does not parse: %s" % (os.path.relpath(x, MOD), e)); continue
    rel = os.path.relpath(x, MOD)
    for el in root.iter():
        cls = el.get("Class")
        if cls and cls.startswith(NS):
            n_refs += 1
            short = cls[len(NS):]
            if short not in classes:
                fail("%s: Class=%s has no public class in Source/" % (rel, cls)); continue
            fset = all_fields(short)
            vanilla = None
            if has_foreign_base(short):
                vanilla = VANILLA.get(foreign_root(short))
                if vanilla is None:
                    counts["children of classes with an unlisted vanilla base (unverifiable)"] = counts.get("children of classes with an unlisted vanilla base (unverifiable)", 0) + len(list(el))
                    continue
            for ch in el:
                if not isinstance(ch.tag, str):
                    continue
                n_children += 1
                if vanilla is not None and ch.tag in vanilla:
                    continue
                if ch.tag != "li" and ch.tag not in fset and (fset or vanilla is not None):
                    fail("%s: <%s Class=%s> child <%s> is not a public field of %s (the loader ignores it)" % (rel, el.tag, short, ch.tag, short))
        if el.tag in ("thingClass", "compClass", "giverClass", "workerClass", "jobClass", "driverClass") and el.text and el.text.strip().startswith(NS):
            n_refs += 1
            if el.text.strip()[len(NS):] not in classes:
                fail("%s: <%s>%s</%s> has no public class in Source/" % (rel, el.tag, el.text.strip(), el.tag))
counts["xml class refs"] = n_refs
counts["xml field children"] = n_children

# ---------- 3: csproj
proj = open(os.path.join(MOD, "Source", "RM_LanternDeeps.csproj"), encoding="utf-8").read()
listed = set(re.findall(r'<Compile Include="([^"]+)"', proj))
on_disk = {os.path.basename(f) for f in cs_files}
for f in sorted(on_disk - listed):
    fail("Source/%s is not in RM_LanternDeeps.csproj (EnableDefaultCompileItems is false: it compiles into nothing)" % f)
for f in sorted(listed - on_disk):
    # a linked shared source (the light ledger, LIGHT_LEDGER_ONE_1) is checked where it actually lives
    if f.startswith(".."):
        if not os.path.exists(os.path.normpath(os.path.join(MOD, "Source", f.replace("\\", "/")))):
            fail("csproj links %s but the file does not exist" % f)
        continue
    fail("csproj lists %s but the file does not exist" % f)
counts["cs files"] = len(on_disk)

# ---------- 4 + 5: lookups by string
defnames = set()
for x in glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True):
    if "/Transient/" in x or "/_rmbuild/" in x:
        continue
    try:
        t = open(x, encoding="utf-8", errors="replace").read()
        defnames.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", t))
        defnames.update(re.findall(r"<li>\s*((?:RM|RUT|RSW)_\w+)\s*</li>", t))      # terrain/tag lists
    except OSError:
        pass
classnames = set()
for x in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
    if "/_rmbuild/" in x or "/Transient/" in x:
        continue
    try:
        classnames.update(re.findall(r"\bclass\s+(\w+)", open(x, encoding="utf-8", errors="replace").read()))
    except OSError:
        pass
keys = set()
for x in glob.glob(os.path.join(MOD, "Languages", "English", "Keyed", "*.xml")):
    keys.update(m for m in re.findall(r"<([A-Za-z0-9_.]+)>", open(x, encoding="utf-8").read()) if m != "LanguageData")
# also every other mod's keyed keys: a key may be shared
for x in glob.glob(os.path.join(SRC, "**", "Keyed", "*.xml"), recursive=True):
    keys.update(re.findall(r"<([A-Za-z0-9_.]+)>", open(x, encoding="utf-8", errors="replace").read()))
n_lit = 0; n_tr = 0
for f in cs_files:
    txt = strip_comments(open(f, encoding="utf-8").read())
    for m in re.finditer(r'"((?:RM|RUT|RSW)_[A-Za-z0-9_]+)"', txt):
        n_lit += 1
        lit = m.group(1)
        # a literal may also be a class name compared by GetType().Name, or the prefix of a computed key ("RM_OrunGhalTier" + tier)
        if lit not in defnames and lit not in keys and lit not in classnames and not any(k.startswith(lit) for k in keys | defnames):
            fail("%s: string \"%s\" is neither a defName/tag under src/ nor a translation key" % (os.path.basename(f), lit))
    for m in re.finditer(r'"([A-Za-z0-9_.]+)"\.Translate\(', txt):
        n_tr += 1
        if m.group(1).startswith("RM_") and m.group(1) not in keys:
            fail("%s: \"%s\".Translate() has no key in Keyed/*.xml (it shows the raw key in game)" % (os.path.basename(f), m.group(1)))
counts["rm string literals"] = n_lit
counts["Translate() calls"] = n_tr

# ---------- 6: kernel state <-> Scribe, Scribe-name uniqueness, kernels engine-free
comp = strip_comments(open(os.path.join(MOD, "Source", "RM_AuroraCollapse.cs"), encoding="utf-8").read())
kernel = strip_comments(open(os.path.join(MOD, "Source", "RM_DeepCollapseKernel.cs"), encoding="utf-8").read())
state_body = re.search(r"class DeepCollapseState<T>\s*\{(.*?)public int Pending", kernel, re.S).group(1)
saved = {"due", "forced"}                                  # released is deliberately transient
state_fields = re.findall(r"public\s+(?:Dictionary|HashSet)<[^>]*>\s+(\w+)\s*=", state_body)
scribed = dict((m[0].split(".")[-1], m[1]) for m in re.findall(r'Scribe_Collections\.Look\(ref ([\w.]+), "(\w+)"', comp))
for sf in state_fields:
    if sf in saved and scribed.get(sf) != sf:
        fail("DeepCollapseState.%s is not Scribed under that same name in RM_MapComponent_DeepCollapse (%r)" % (sf, scribed.get(sf)))
    if sf not in saved and sf in scribed:
        fail("DeepCollapseState.%s is transient by design but is now Scribed" % sf)
counts["kernel state fields"] = len(state_fields)
n_scribe = 0
for f in cs_files:
    txt = strip_comments(open(f, encoding="utf-8").read())
    for cm in re.finditer(r"\bclass\s+(\w+)[^{;]*\{", txt):
        i, depth = cm.end(), 1
        while depth and i < len(txt):
            depth += (txt[i] == "{") - (txt[i] == "}")
            i += 1
        names = re.findall(r"Scribe_\w+\.Look\(\s*ref\s+[\w.]+\s*,\s*\"(\w+)\"", txt[cm.end():i])
        n_scribe += len(names)
        for dup in sorted({n for n in names if names.count(n) > 1}):
            fail("%s: Scribe name \"%s\" used twice in %s (second write overwrites the first)" % (os.path.basename(f), dup, cm.group(1)))
counts["scribe calls"] = n_scribe
sproj = open(os.path.join(MOD, "Source", "SelfTest", "RimMandrakeLanternDeeps.SelfTest.csproj"), encoding="utf-8").read()
inc = re.findall(r'<Compile Include="([^"]+)"', sproj)
for k in ("RM_DeepCollapseKernel.cs", "RM_SipperLedgerKernel.cs"):
    if not any(i.endswith(k) for i in inc):
        fail("selftest csproj does not compile %s" % k)
    if k not in listed:
        fail("%s is not in RM_LanternDeeps.csproj" % k)
    for u in re.findall(r"^\s*using\s+([\w.]+);", open(os.path.join(MOD, "Source", k), encoding="utf-8").read(), re.M):
        if u.split(".")[0] in ("Verse", "RimWorld", "UnityEngine", "HarmonyLib"):
            fail("%s has `using %s;` - the kernel must stay engine-free" % (k, u))
for i in inc:
    if not os.path.exists(os.path.normpath(os.path.join(MOD, "Source", "SelfTest", i.replace("\\", "/")))):
        fail("selftest csproj includes %s which does not exist" % i)
counts["selftest compile entries"] = len(inc)

for k, v in counts.items():
    print("lint %s: %d" % (k, v))
    if v == 0:
        fail("check '%s' looked at nothing" % k)
for m in fails:
    print("FAIL " + m)
print("lanterndeeps lint: %s" % ("OK" if not fails else "%d FINDINGS" % len(fails)))
sys.exit(1 if fails else 0)
