#!/usr/bin/env python3
"""Static cross-check of DivingInteraction: XML defs <-> C# classes/fields, csproj <-> source files, and the strings
the C# looks defs and translation keys up by. No game, no build. Exits 1 with one line per finding.

    python3 src/RimMandrake/Utils/selftest_divinginteraction_lint.py

Checks (each prints its count so a check that looked at nothing cannot pass silently):
  1. every Class="RimMandrake.DivingInteraction.X" / thingClass / compClass / giverClass in Defs+Patches names a class in Source
  2. every child element of such a Class node is a public field of that class (an unknown field is silently ignored by the loader)
  3. every Source/*.cs is in the csproj Compile list and every Compile entry exists
  4. every "RM_/RUT_/RSW_" string literal in Source resolves to a defName or <li> tag somewhere under src/ or to a Keyed translation key
  5. every "...".Translate() key (RM_ prefixed) exists in Languages/English/Keyed
  6. the Scribe names of RM_MapComponent_ChillGardenDefense match the RM_GardenDefenseKernel.State fields (kernel/component drift)
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))          # .../src
MOD = os.path.join(SRC, "RimMandrake", "DivingInteraction")
NS = "RimMandrake.DivingInteraction."
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
            for ch in el:
                if not isinstance(ch.tag, str):
                    continue
                n_children += 1
                if ch.tag != "li" and ch.tag not in fset and fset:
                    fail("%s: <%s Class=%s> child <%s> is not a public field of %s (the loader ignores it)" % (rel, el.tag, short, ch.tag, short))
        if el.tag in ("thingClass", "compClass", "giverClass", "workerClass", "jobClass", "driverClass") and el.text and el.text.strip().startswith(NS):
            n_refs += 1
            if el.text.strip()[len(NS):] not in classes:
                fail("%s: <%s>%s</%s> has no public class in Source/" % (rel, el.tag, el.text.strip(), el.tag))
counts["xml class refs"] = n_refs
counts["xml field children"] = n_children

# ---------- 3: csproj
proj = open(os.path.join(MOD, "Source", "RM_DivingInteraction.csproj"), encoding="utf-8").read()
listed = set(re.findall(r'<Compile Include="([^"]+)"', proj))
on_disk = {os.path.basename(f) for f in cs_files}
for f in sorted(on_disk - listed):
    fail("Source/%s is not in RM_DivingInteraction.csproj (EnableDefaultCompileItems is false: it compiles into nothing)" % f)
for f in sorted(listed - on_disk):
    if f.startswith(".."):   # shared file outside Source/: must exist relative to Source/
        if os.path.exists(os.path.join(MOD, "Source", f.replace("\\", os.sep))):
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
        if lit not in defnames and lit not in keys:
            fail("%s: string \"%s\" is neither a defName/tag under src/ nor a translation key" % (os.path.basename(f), lit))
    for m in re.finditer(r'"([A-Za-z0-9_.]+)"\.Translate\(', txt):
        n_tr += 1
        if m.group(1).startswith("RM_") and m.group(1) not in keys:
            fail("%s: \"%s\".Translate() has no key in Keyed/*.xml (it shows the raw key in game)" % (os.path.basename(f), m.group(1)))
counts["rm string literals"] = n_lit
counts["Translate() calls"] = n_tr

# ---------- 6: kernel state <-> Scribe
comp = open(os.path.join(MOD, "Source", "RM_MapComponent_ChillGardenDefense.cs"), encoding="utf-8").read()
kernel = open(os.path.join(MOD, "Source", "RM_GardenDefenseKernel.cs"), encoding="utf-8").read()
state_fields = re.search(r"public struct State\s*\{(.*?)public static State Fresh", kernel, re.S).group(1)
state_fields = re.findall(r"public\s+(?:float|int)\s+(\w+);", state_fields)
scribed = dict(re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', comp))
for sf in state_fields:
    if scribed.get(sf) != sf:
        fail("kernel State.%s is not Scribed under that same name in RM_MapComponent_ChillGardenDefense (%r)" % (sf, scribed.get(sf)))
counts["kernel state fields"] = len(state_fields)

for k, v in counts.items():
    print("lint %s: %d" % (k, v))
    if v == 0:
        fail("check '%s' looked at nothing" % k)
for m in fails:
    print("FAIL " + m)
print("divinginteraction lint: %s" % ("OK" if not fails else "%d FINDINGS" % len(fails)))
sys.exit(1 if fails else 0)
