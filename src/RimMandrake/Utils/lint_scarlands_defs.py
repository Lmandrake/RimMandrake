#!/usr/bin/env python3
"""Offline lint of the Scarlands (Warscar) mod: XML defs/patches against its C# source. No game, no build.

    python3 src/RimMandrake/Utils/lint_scarlands_defs.py [--mod-dir <dir>] [--quiet]

Exit 1 on any ERROR. WARN lines are dead/unwired things worth a look but not necessarily wrong.
Checks (each names itself in the output):
  class-resolves    every RimMandrake.* type named in a Class="" attribute or a *Class element exists as a C# class
                    (bare RM_/RUT_/RSW_ names too); a def naming a missing type is discarded silently by the engine
  fields-match      for a Class="" naming an in-tree type whose base chain ends at CompProperties / DefModExtension /
                    HediffCompProperties / GenStep / StatPart, every child element is a public field of that chain
                    (an unknown child is a load-time "could not find field" error)
  driver-kind       JobDef driverClass is a JobDriver subclass; WorkGiverDef giverClass is a WorkGiver subclass
  getnamed-resolves every GetNamed("RM_*") string in C# names a def that exists in this mod's Defs
  defof-resolves    every [DefOf] field RM_* exists as a def of the matching type
  settings-scribed  every RM_WarscarSettings field is Scribed once, key == name, default == initializer; every use of
                    RM_WarscarSettings.x in code names a declared field; unused fields and fields with no UI are WARNed
  compile-listed    every Source/*.cs is in RM_Warscar.csproj (EnableDefaultCompileItems is false: a missing line
                    compiles into nothing, silently)
  wired             WARN: a JobDriver/WorkGiver/GenStep/comp class no def or typeof() references
  defname-unique    duplicate defName within a def type
  texpath-resolves  texPath whose folder exists in this mod's Textures but whose file does not
"""
import os
import re
import sys
import glob
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src", "RimMandrake")

CLASS_ELEMS = {"compClass", "driverClass", "giverClass", "workerClass", "thingClass", "gameConditionClass", "hediffClass",
               "genStep", "conditionClass", "inspectorTabs", "designatorClass", "soundClass", "overlayClass", "incidentWorkerClass"}
STRICT_ROOTS = {"CompProperties": {"compClass"}, "DefModExtension": set(), "HediffCompProperties": {"compClass"},
                "GenStep": set(), "StatPart": set()}
OUR_PREFIX = ("RM_", "RUT_", "RSW_")


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


class Cls:
    def __init__(self, name, ns, base, abstract, fields, path):
        self.name, self.ns, self.base, self.abstract, self.fields, self.path = name, ns, base, abstract, fields, path


def scan_csharp(root):
    """name -> Cls for every class in every .cs under root (namespace-qualified names also indexed)."""
    classes = {}
    for p in glob.glob(os.path.join(root, "**", "*.cs"), recursive=True):
        if os.sep + "obj" + os.sep in p or os.sep + "bin" + os.sep in p or os.sep + "SelfTest" + os.sep in p:
            continue
        txt = strip_comments(open(p, encoding="utf-8-sig", errors="replace").read())
        ns = re.search(r"\bnamespace\s+([\w.]+)", txt)
        ns = ns.group(1) if ns else ""
        for m in re.finditer(r"\b((?:public|internal|abstract|static|sealed|partial)\s+)*(class|interface)\s+(\w+)(?:\s*:\s*([^{]+?))?\s*(?:where[^{]*)?\{", txt):
            mods = m.group(0)
            name = m.group(3)
            bases = [b.strip().split("<")[0].split(".")[-1] for b in (m.group(4) or "").split(",") if b.strip()]
            # fields = everything declared between this class's opening brace and its end (nested depth tracked)
            body, depth, i = [], 1, m.end()
            while i < len(txt) and depth:
                c = txt[i]
                depth += (c == "{") - (c == "}")
                i += 1
            body = txt[m.end():i - 1]
            fields = set(re.findall(r"\bpublic\s+(?!static\b|const\b|override\b|virtual\b|abstract\b|class\b)[\w<>\[\],.? ]+?\s+(\w+)\s*(?:=[^;]*)?;", body))
            fields |= set(re.findall(r"\bpublic\s+(?!static\b|override\b|virtual\b|abstract\b)[\w<>\[\],.? ]+?\s+(\w+)\s*\{\s*get;\s*(?:private\s+|protected\s+)?set;", body))
            c = Cls(name, ns, bases[0] if bases else None, "abstract" in mods.split("class")[0], fields, p)
            c.bases = bases
            classes.setdefault(name, c)
            if ns:
                classes.setdefault(ns + "." + name, c)
    return classes


def chain(classes, c):
    """Yield c and in-tree ancestors; final element is the first unresolved base name (str) or None."""
    seen = set()
    while True:
        yield c
        if c.base is None:
            yield None
            return
        nxt = classes.get(c.base)
        if nxt is None or nxt.name in seen:
            yield c.base
            return
        seen.add(c.name)
        c = nxt


def issubclass_name(classes, c, target):
    for x in chain(classes, c):
        if isinstance(x, str) and (x == target or x.startswith(target + "_")):
            return True   # a vanilla subclass such as WorkGiver_Scanner / JobDriver_Wait
        if isinstance(x, Cls) and (x.name == target or target in getattr(x, "bases", [])):
            return True
    return False


def main(argv):
    mod = os.path.join(SRC, "Scarlands")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    quiet = "--quiet" in argv
    errs, warns = [], []
    E = lambda chk, msg: errs.append(f"ERROR {chk}: {msg}")
    W = lambda chk, msg: warns.append(f"WARN  {chk}: {msg}")

    our = scan_csharp(os.path.join(mod, "Source"))
    allc = scan_csharp(SRC)
    defs_xml = sorted(glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True))
    patch_xml = sorted(glob.glob(os.path.join(mod, "Patches", "**", "*.xml"), recursive=True))
    sanity = {"xml": len(defs_xml) + len(patch_xml), "classes": len([k for k in our if "." not in k])}
    if sanity["xml"] == 0 or sanity["classes"] == 0:
        print(f"LINT UNMEASURED: found {sanity} - wrong --mod-dir?")
        return 2

    defnames = {}   # (tag, defName) -> file
    referenced = set()
    checked = {"class-refs": 0, "field-checks": 0, "drivers": 0}

    def resolve(name, where):
        short = name.split(".")[-1]
        if name.startswith("RimMandrake.") or short.startswith(OUR_PREFIX):
            checked["class-refs"] += 1
            c = allc.get(name) or (allc.get(short) if "." not in name else None)
            if c is None:
                E("class-resolves", f"{where}: type {name} not found in any RimMandrake C# source")
                return None
            referenced.add(c.name)
            return c
        return None

    for p in defs_xml + patch_xml:
        rel = os.path.relpath(p, mod)
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            E("xml-parses", f"{rel}: {e}")
            continue
        is_patch = p in patch_xml
        if not is_patch:
            for d in root:
                dn = d.findtext("defName")
                if dn:
                    k = (d.tag, dn)
                    if k in defnames:
                        E("defname-unique", f"{d.tag} {dn} in {rel} and {defnames[k]}")
                    defnames[k] = rel
        for el in root.iter():
            cls = el.get("Class")
            if cls:
                c = resolve(cls, f"{rel} <{el.tag}>")
                if c is not None and not is_patch:
                    fields, ok, root_base = set(), True, None
                    for x in chain(allc, c):
                        if isinstance(x, Cls):
                            fields |= x.fields
                        elif isinstance(x, str):
                            root_base = x
                    if root_base in STRICT_ROOTS:
                        fields |= STRICT_ROOTS[root_base]
                        checked["field-checks"] += 1
                        for ch in el:
                            if ch.tag not in fields and ch.tag != "li":
                                E("fields-match", f"{rel}: <{el.tag} Class=\"{cls}\"> has <{ch.tag}> but {c.name} (+bases) has no such public field")
            if el.tag in CLASS_ELEMS and (el.text or "").strip():
                t = el.text.strip()
                c = resolve(t, f"{rel} <{el.tag}>")
                if el.tag == "driverClass":
                    checked["drivers"] += 1
                    if c is not None and not issubclass_name(allc, c, "JobDriver"):
                        E("driver-kind", f"{rel}: driverClass {t} does not derive from JobDriver")
                if el.tag == "giverClass" and c is not None and not issubclass_name(allc, c, "WorkGiver"):
                    E("driver-kind", f"{rel}: giverClass {t} does not derive from WorkGiver")
                if el.tag == "giverClass" and c is None and not t.split(".")[-1].startswith(OUR_PREFIX) and t.split(".")[-1] in our:
                    referenced.add(t.split(".")[-1])
            # every bare text value that names one of OUR classes counts as a reference (e.g. workerClass of a thinktree)
            tx = (el.text or "").strip()
            if tx in our:
                referenced.add(tx)
            if el.tag in ("texPath",) and tx:
                tp = os.path.join(mod, "Textures", *tx.split("/"))
                folder = os.path.dirname(tp)
                if os.path.isdir(folder) and any(part.startswith(OUR_PREFIX) for part in tx.split("/")):
                    stem = os.path.basename(tp)
                    if not (glob.glob(tp + ".png") or glob.glob(os.path.join(folder, stem + "_*.png")) or os.path.isdir(tp)):
                        E("texpath-resolves", f"{rel}: texPath {tx} has no png in {os.path.relpath(folder, mod)}")

    # JobDef/WorkGiverDef sanity: every JobDef has a driverClass that resolved (an empty one is an error)
    for p in defs_xml:
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue   # already reported as xml-parses
        for d in root:
            if d.tag == "JobDef" and not (d.findtext("driverClass") or "").strip():
                E("driver-kind", f"JobDef {d.findtext('defName')} in {os.path.relpath(p, mod)} has no driverClass")

    # ---- C# side ----
    src_files = [f for f in glob.glob(os.path.join(mod, "Source", "**", "*.cs"), recursive=True)
                 if os.sep + "SelfTest" + os.sep not in f and os.sep + "obj" + os.sep not in f]
    csproj = open(os.path.join(mod, "Source", "RM_Warscar.csproj"), encoding="utf-8-sig").read()
    listed = {i.replace("\\", "/") for i in re.findall(r'Compile Include="([^"]+)"', csproj)}
    all_text = {}
    for f in src_files:
        rel = os.path.relpath(f, os.path.join(mod, "Source")).replace(os.sep, "/")
        all_text[rel] = strip_comments(open(f, encoding="utf-8-sig", errors="replace").read())
        if rel not in listed:
            E("compile-listed", f"Source/{rel} is not in RM_Warscar.csproj (compiles into nothing, silently)")
    for i in listed:
        if not os.path.exists(os.path.join(mod, "Source", i.replace("/", os.sep))):
            E("compile-listed", f"csproj lists {i} which does not exist")
    code = "\n".join(all_text.values())

    # references through typeof()/generic arguments/new X() count as wired
    for m in re.finditer(r"typeof\((\w+)\)|new (\w+)\(|<(\w+)>|:\s*(\w+)", code):
        for g in m.groups():
            if g in our:
                referenced.add(g)

    other_defs = None
    for m in re.finditer(r'GetNamed(SilentFail)?\("([^"]+)"', code):
        silent, n = m.group(1), m.group(2)
        checked["class-refs"] += 1
        if n.startswith(OUR_PREFIX) and not any(dn == n for (_, dn) in defnames):
            if other_defs is None:
                other_defs = set()
                for xp in glob.glob(os.path.join(SRC, "*", "Defs", "**", "*.xml"), recursive=True):
                    other_defs |= set(re.findall(r"<defName>([^<]+)</defName>", open(xp, encoding="utf-8-sig", errors="replace").read()))
            where = "another RimMandrake mod" if n in other_defs else "any RimMandrake mod's Defs (may be generated at runtime)"
            if silent and n in other_defs:
                continue
            (W if silent else E)("getnamed-resolves", f'GetNamed{silent or ""}("{n}") has no def in this mod; not in {where}' if n not in other_defs else f'GetNamed("{n}") names a def of another mod, not this one')
    for m in re.finditer(r"\[DefOf\]\s*(?:public\s+)?static\s+class\s+(\w+)\s*\{(.*?)\n\s*static\s+\w+\(\)", code, flags=re.S):
        for fm in re.finditer(r"public static (\w+) (\w+);", m.group(2)):
            typ, nm = fm.groups()
            if nm.startswith(OUR_PREFIX) and (typ, nm) not in defnames:
                E("defof-resolves", f"[DefOf] {m.group(1)}.{nm} ({typ}) has no such def in this mod's Defs")

    # settings
    sp = os.path.join(mod, "Source", "RM_WarscarMod.cs")
    st = strip_comments(open(sp, encoding="utf-8-sig").read())
    sm = re.search(r"class\s+RM_WarscarSettings\b[^{]*\{", st)
    sbody = st[sm.end():] if sm else ""
    decl = {n: (t, v.strip()) for t, n, v in re.findall(r"public static (bool|float|int|string)\s+(\w+)\s*=\s*([^;]+);", sbody)}
    scribed = re.findall(r'Scribe_Values\.Look\(ref\s+(\w+),\s*"(\w+)",\s*([^,)]*)[,)]', sbody)
    if not decl or not scribed:
        print("LINT UNMEASURED: no settings fields or Scribe calls parsed")
        return 2
    seen_keys, seen_fields = {}, {}
    norm = lambda v: v.strip().rstrip("f").lower()
    for fld, key, dflt in scribed:
        if fld not in decl:
            E("settings-scribed", f"Scribe_Values.Look(ref {fld}) names an undeclared field")
            continue
        if fld in seen_fields:
            E("settings-scribed", f"field {fld} is Scribed twice")
        seen_fields[fld] = key
        if key != fld:
            E("settings-scribed", f'field {fld} is saved under key "{key}" (key and field differ)')
        if key in seen_keys and seen_keys[key] != fld:
            E("settings-scribed", f'key "{key}" is used by both {seen_keys[key]} and {fld}')
        seen_keys[key] = fld
        if norm(dflt) != norm(decl[fld][1]):
            E("settings-scribed", f"field {fld} initialises to {decl[fld][1]} but Scribes default {dflt.strip()} (a reset-to-default would change behaviour)")
    for fld in decl:
        if fld not in seen_fields:
            E("settings-scribed", f"settings field {fld} is declared but never Scribed (setting is lost on restart)")
    outside = "\n".join(t for r, t in all_text.items() if r != "RM_WarscarMod.cs")
    ui = sbody.split("DoWindowContents")[1] if "DoWindowContents" in sbody else ""
    for fld in decl:
        pat = r"\b" + fld + r"\b"
        if not re.search(pat, outside) and not re.search(r"RM_WarscarSettings\." + fld + r"\b", st):
            W("settings-scribed", f"settings field {fld} is never read by any code (dead toggle)")
        if not re.search(pat, ui):
            W("settings-scribed", f"settings field {fld} has no control in DoWindowContents")
    for m in sorted(set(re.findall(r"RM_WarscarSettings\.(\w+)", code))):
        if m not in decl and m not in ("DoWindowContents", "ExposeData", "Instance"):
            # may be a method/nested member: only complain if it is lower-camel like a field
            if re.match(r"[a-z]", m):
                E("settings-scribed", f"code reads RM_WarscarSettings.{m} which is not a declared field")

    # wired: classes of the right kind that nothing references
    for name, c in sorted((k, v) for k, v in our.items() if "." not in k):
        if c.abstract or name in referenced:
            continue
        kind = None
        for target in ("JobDriver", "WorkGiver", "GenStep", "ThingComp", "CompProperties", "DefModExtension", "JobGiver", "ThinkNode", "IncidentWorker", "GameCondition", "HediffComp", "StatPart"):
            if issubclass_name(allc, c, target):
                kind = target
                break
        if kind:
            used_in_code = len(re.findall(r"\b" + name + r"\b", code))
            if used_in_code <= 1:
                W("wired", f"{kind} subclass {name} ({os.path.relpath(c.path, mod)}) is referenced by no def, typeof() or other code")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"scarlands lint: {len(defs_xml)} defs + {len(patch_xml)} patch files, {sanity['classes']} classes, "
          f"{checked['class-refs']} class/def refs, {checked['field-checks']} field checks, {checked['drivers']} drivers, "
          f"{len(decl)} settings, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
