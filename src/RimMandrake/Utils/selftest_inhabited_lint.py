#!/usr/bin/env python3
"""Static cross-check of Inhabited: XML defs <-> C# classes/fields/enums, def references, translation keys, Scribe names vs
fields, csproj/kernel purity. No game, no build. Exits 1 with one line per finding.

    python3 src/RimMandrake/Utils/selftest_inhabited_lint.py

Checks (each prints its count so a check that looked at nothing cannot pass silently):
  1. every RimMandrake.Inhabited.X named by a tag, Class=, or *Class element in Defs names a public class in Source
  2. every child of such an element is a public field of that class (the loader ignores/logs an unknown field), Def base fields allowed
  3. a child whose field is an enum declared in Source holds one of its members; a child whose field is a def type
     (InhabitedCastDef, InhabitedPlaceDef, SecurityProfileDef, CharacterDef) names a def that exists
  4. every "Key".Translate() literal and every fate-cause key the kernel can return has a Keyed entry
  5. Scribe names are unique within a class, and every public instance field of the saved classes is Scribed (a field
     missing from ExposeData silently resets on load); DisplacementBook's fields are Scribed under their own names
  6. csproj: default compile items stay ON (a nested SelfTest/ inside Source/ would compile into the mod), no .cs hidden in
     Source subfolders, and the two kernel files carry no Verse/RimWorld/UnityEngine/Harmony using (the selftest build needs that)
  7. every [DefOf] field names a def that exists
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))          # .../src
MOD = os.path.join(SRC, "RimMandrake", "Inhabited")
NS = "RimMandrake.Inhabited."
DEF_BASE = {"defName", "label", "description", "descriptionHyperlinks", "ignoreConfigErrors", "ignoreIllegalLabelCharacterConfigError",
            "modExtensions", "generated", "shortHash", "index", "debugRandomId", "fileName", "modContentPack", "cachedLabelCap"}
fails = []
counts = {}
ZERO_OK = {"def-valued fields"}      # no shipped def sets a def-typed field yet; the check is armed for when one does


def fail(msg):
    fails.append(msg)


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def body_of(txt, start):
    i, depth = start, 1
    while depth and i < len(txt):
        depth += (txt[i] == "{") - (txt[i] == "}")
        i += 1
    return txt[start:i]


cs_files = sorted(glob.glob(os.path.join(MOD, "Source", "*.cs")))
classes = {}      # name -> (file, {field: type}, base)
enums = {}        # name -> members
texts = {}
for f in cs_files:
    txt = strip_comments(open(f, encoding="utf-8").read())
    texts[os.path.basename(f)] = txt
    for m in re.finditer(r"\bpublic\s+enum\s+(\w+)\s*\{", txt):
        enums[m.group(1)] = re.findall(r"\b(\w+)\s*(?:=[^,}]*)?\s*(?:,|$|\n)", body_of(txt, m.end()).rsplit("}", 1)[0])
    for m in re.finditer(r"\bpublic\s+(?:static\s+|abstract\s+|sealed\s+)*(?:class|struct)\s+(\w+)(?:\s*:\s*([\w.<>, ]+))?\s*\{", txt):
        name, base = m.group(1), (m.group(2) or "")
        body = body_of(txt, m.end())
        fields = {}
        for fm in re.finditer(r"\bpublic\s+(?!static\b|const\b|override\b|class\b|void\b|readonly\b|abstract\b)([\w<>\[\],.? ]+?)\s+(\w+)\s*(?:=(?!>)[^;]*)?;", body):
            fields[fm.group(2)] = fm.group(1).strip()
        classes[name] = (os.path.basename(f), fields, base.split(",")[0].strip())


def all_fields(name, seen=()):
    if name not in classes or name in seen:
        return {}
    d = dict(all_fields(classes[name][2], seen + (name,)))
    d.update(classes[name][1])
    return d


# defNames anywhere under src (tags and <li> RM_ names)
defnames = set()
for x in glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True):
    if "/Transient/" in x or "/_rmbuild/" in x:
        continue
    try:
        defnames.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", open(x, encoding="utf-8", errors="replace").read()))
    except OSError:
        pass

# ---------- 1-3 XML
n_refs = n_children = n_enum = n_defref = 0
xmls = glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True)
DEFTYPES = {"InhabitedCastDef", "InhabitedPlaceDef", "SecurityProfileDef", "CharacterDef", "SettlementManifestDef"}
for x in xmls:
    rel = os.path.relpath(x, MOD)
    try:
        root = ET.parse(x).getroot()
    except ET.ParseError as e:
        fail("%s: XML does not parse: %s" % (rel, e)); continue
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        cls = None
        if el.tag.startswith(NS):
            cls = el.tag[len(NS):]
        elif (el.get("Class") or "").startswith(NS):
            cls = el.get("Class")[len(NS):]
        elif el.tag.endswith("Class") and (el.text or "").strip().startswith(NS):
            cls = el.text.strip()[len(NS):]
            n_refs += 1
            if cls not in classes:
                fail("%s: <%s>%s</%s> has no public class in Source/" % (rel, el.tag, NS + cls, el.tag))
            continue
        if cls is None:
            continue
        n_refs += 1
        if cls not in classes:
            fail("%s: %s%s has no public class in Source/" % (rel, NS, cls)); continue
        fmap = all_fields(cls)
        is_def = any(b == "Def" for b in [classes[cls][2]]) or "Def" in cls
        for ch in el:
            if not isinstance(ch.tag, str):
                continue
            n_children += 1
            if ch.tag == "li" or ch.tag.startswith(NS):
                continue
            if ch.tag not in fmap and not (is_def and ch.tag in DEF_BASE):
                fail("%s: <%s> child <%s> is not a public field of %s (the loader ignores it)" % (rel, cls, ch.tag, cls)); continue
            ftype = fmap.get(ch.tag, "")
            val = (ch.text or "").strip()
            if ftype in enums:
                n_enum += 1
                if val and val not in enums[ftype]:
                    fail("%s: <%s>%s</%s> is not a member of enum %s (%s)" % (rel, ch.tag, val, ch.tag, ftype, ", ".join(enums[ftype])))
            elif ftype in DEFTYPES and val:
                n_defref += 1
                if val not in defnames:
                    fail("%s: <%s>%s</%s> names no %s defName under src/" % (rel, ch.tag, val, ch.tag, ftype))
counts["xml class refs"] = n_refs
counts["xml field children"] = n_children
counts["enum-valued fields"] = n_enum
counts["def-valued fields"] = n_defref

# ---------- 4 translate keys
keys = set()
for x in glob.glob(os.path.join(MOD, "Languages", "English", "Keyed", "*.xml")):
    keys.update(m for m in re.findall(r"<([A-Za-z0-9_.]+)>", open(x, encoding="utf-8").read()) if m != "LanguageData")
n_tr = 0
for name, txt in texts.items():
    for m in re.finditer(r'"([A-Za-z0-9_.]+)"\.Translate\(', txt):
        n_tr += 1
        if m.group(1) not in keys:
            fail("%s: \"%s\".Translate() has no Keyed entry (it shows the raw key in game)" % (name, m.group(1)))
for m in re.finditer(r'public const string (Cause\w+) = "(\w+)";', texts["InhabitedFateKernel.cs"]):
    n_tr += 1
    if m.group(2) not in keys:
        fail("InhabitedFateKernel.%s = \"%s\" has no Keyed entry (MapComponent_InhabitedWatch translates it)" % (m.group(1), m.group(2)))
counts["translate keys"] = n_tr

# ---------- 5 scribe
n_scribe = n_saved = 0
SAVED = ["WorldObject_Inhabited", "WorldObject_InhabitedSettlement", "SettlementCasing", "DisplacementBook"]
for name, txt in texts.items():
    for cm in re.finditer(r"\bclass\s+(\w+)[^{;]*\{", txt):
        cname = cm.group(1)
        body = body_of(txt, cm.end())
        scribes = re.findall(r"Scribe_\w+\.Look\(\s*ref\s+([\w.]+)\s*,\s*\"(\w+)\"", body)
        if not scribes:
            continue
        seen = {}
        for ref, sname in scribes:
            n_scribe += 1
            if sname in seen:
                fail("%s: Scribe name \"%s\" used twice in %s (second write overwrites the first)" % (name, sname, cname))
            seen[sname] = ref
        if cname in SAVED:
            for fld in classes[cname][1]:       # own fields: inherited ones are the base class's to Scribe
                n_saved += 1
                if not any(r.split(".")[-1] == fld for r, _ in scribes):
                    fail("%s.%s is a public field that ExposeData never Scribes (it resets on every load)" % (cname, fld))
        if cname == "DisplacedPool":
            for fld in all_fields("DisplacementBook"):
                n_saved += 1
                if (("book." + fld), fld) not in scribes:
                    fail("DisplacedPool does not Scribe DisplacementBook.%s under its own name" % fld)
counts["scribe calls"] = n_scribe
counts["saved fields checked"] = n_saved

# ---------- 6 csproj + kernel purity
proj = open(os.path.join(MOD, "Source", "Inhabited.csproj"), encoding="utf-8").read()
if "EnableDefaultCompileItems" in proj and re.search(r"EnableDefaultCompileItems>\s*false", proj):
    fail("Inhabited.csproj turned default compile items off; every file must then be listed")
nested = [f for f in glob.glob(os.path.join(MOD, "Source", "**", "*.cs"), recursive=True) if os.path.dirname(f) != os.path.join(MOD, "Source")]
for f in nested:
    fail("%s is below Source/ and would compile into the mod (the selftest must live beside Source/, not in it)" % os.path.relpath(f, MOD))
sproj = open(os.path.join(MOD, "SelfTest", "RimMandrakeInhabited.SelfTest.csproj"), encoding="utf-8").read()
inc = re.findall(r'<Compile Include="([^"]+)"', sproj)
for i in inc:
    if not os.path.exists(os.path.normpath(os.path.join(MOD, "SelfTest", i.replace("\\", "/")))):
        fail("selftest csproj includes %s which does not exist" % i)
for k in ("InhabitedCustodyKernel.cs", "InhabitedFateKernel.cs"):
    if not any(i.endswith(k) for i in inc):
        fail("selftest csproj does not compile %s" % k)
    for u in re.findall(r"^\s*using\s+([\w.]+);", open(os.path.join(MOD, "Source", k), encoding="utf-8").read(), re.M):
        if u.split(".")[0] in ("Verse", "RimWorld", "UnityEngine", "HarmonyLib", "Steamworks"):
            fail("%s has `using %s;` - the kernel must stay engine-free" % (k, u))
counts["csproj compile entries"] = len(inc)
counts["cs files"] = len(cs_files)

# ---------- 7 DefOf
n_defof = 0
for name, txt in texts.items():
    for cm in re.finditer(r"\[DefOf\]\s*public static class (\w+)\s*\{", txt):
        for fm in re.finditer(r"public static (\w+) (\w+);", body_of(txt, cm.end())):
            n_defof += 1
            if fm.group(2) not in defnames:
                fail("%s.%s names no defName under src/" % (cm.group(1), fm.group(2)))
counts["DefOf fields"] = n_defof

for k, v in counts.items():
    print("lint %s: %d" % (k, v))
    if v == 0 and k not in ZERO_OK:
        fail("check '%s' looked at nothing" % k)
for m in fails:
    print("FAIL " + m)
print("inhabited lint: %s" % ("OK" if not fails else "%d FINDINGS" % len(fails)))
sys.exit(1 if fails else 0)
