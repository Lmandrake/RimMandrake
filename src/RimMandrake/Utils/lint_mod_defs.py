#!/usr/bin/env python3
"""Offline lint of one RimMandrake mod: XML defs/patches against its C# source. No game, no build. Generalised from
lint_scarlands_defs.py (the helpers are imported from it); the per-mod wrappers are lint_<mod>_defs.py.

    python3 src/RimMandrake/Utils/lint_mod_defs.py <ModFolder> [--mod-dir <dir>] [--quiet]

Exit 1 on any ERROR, 2 if UNMEASURED. WARN lines are dead/unwired things worth a look but not necessarily wrong.
Checks: class-resolves, fields-match, driver-kind, getnamed-resolves, defof-resolves, settings-scribed (key == field,
Scribe default == initializer, Scribed once, dead toggles, no control), compile-listed (EnableDefaultCompileItems is
false: a missing Compile line compiles into nothing, silently), wired, defname-unique, texpath-resolves.
"""
import os
import re
import sys
import glob
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lint_scarlands_defs import (SRC, OUR_PREFIX, CLASS_ELEMS, STRICT_ROOTS, strip_comments, Cls,  # noqa: E402
                                 scan_csharp, chain, issubclass_name)


def run(mod_name, argv, known_missing_art=()):
    mod = os.path.join(SRC, mod_name)
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
                    k = (d.tag.split(".")[-1], dn)   # a namespaced def tag (RimMandrake.X.RM_Def) is the type RM_Def
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
            if el.tag == "li" and re.fullmatch(r"RimMandrake\.[A-Za-z0-9_.]+", tx):   # a class named as list text (placeWorkers, comps ...)
                resolve(tx, f"{rel} <li>")
            if el.tag in ("texPath",) and tx:
                tp = os.path.join(mod, "Textures", *tx.split("/"))
                folder = os.path.dirname(tp)
                if os.path.isdir(folder) and any(part.startswith(OUR_PREFIX) for part in tx.split("/")):
                    stem = os.path.basename(tp)
                    if not (glob.glob(tp + ".png") or glob.glob(os.path.join(folder, stem + "_*.png")) or os.path.isdir(tp)):
                        # art a sibling RimMandrake mod ships (a borrowed render) resolves in the game; art listed by the wrapper as
                        # known-missing is a WARN (filed placeholder), anything else is an ERROR
                        rel_tex = os.path.join("Textures", *tx.split("/"))
                        if glob.glob(os.path.join(SRC, "*", rel_tex + ".png")) or glob.glob(os.path.join(SRC, "*", rel_tex + "_*.png")) or glob.glob(os.path.join(SRC, "*", rel_tex)):
                            continue
                        if tx in known_missing_art:
                            W("texpath-missing-known", f"{rel}: texPath {tx} has no png (known placeholder)")
                            continue
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
    csprojs = [p for p in glob.glob(os.path.join(mod, "Source", "*.csproj"))]
    if len(csprojs) != 1:
        print(f"LINT UNMEASURED: expected one csproj in {mod}/Source, found {csprojs}")
        return 2
    csproj_name = os.path.basename(csprojs[0])
    csproj = open(csprojs[0], encoding="utf-8-sig").read()
    listed = {i.replace("\\", "/") for i in re.findall(r'Compile Include="([^"]+)"', csproj)}
    all_text = {}
    for f in src_files:
        rel = os.path.relpath(f, os.path.join(mod, "Source")).replace(os.sep, "/")
        all_text[rel] = strip_comments(open(f, encoding="utf-8-sig", errors="replace").read())
        if rel not in listed:
            E("compile-listed", f"Source/{rel} is not in {csproj_name} (compiles into nothing, silently)")
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
                if other_defs is None:
                    other_defs = set()
                    for xp in glob.glob(os.path.join(SRC, "*", "Defs", "**", "*.xml"), recursive=True):
                        other_defs |= set(re.findall(r"<defName>([^<]+)</defName>", open(xp, encoding="utf-8-sig", errors="replace").read()))
                if nm in other_defs:   # a declared cross-mod dependency, not a typo: worth knowing, not an error
                    W("defof-resolves", f"[DefOf] {m.group(1)}.{nm} ({typ}) is defined by another RimMandrake mod (a hard dependency of this one)")
                else:
                    E("defof-resolves", f"[DefOf] {m.group(1)}.{nm} ({typ}) has no such def in this mod's Defs or any other RimMandrake mod's")

    # settings: the ModSettings subclass, wherever it lives in Source
    sfile, sname, sbody, st = None, None, "", ""
    for rel, txt in all_text.items():
        sm = re.search(r"class\s+(\w+)\s*:\s*ModSettings\b[^{]*\{", txt)
        if sm:
            sfile, sname, sbody, st = rel, sm.group(1), txt[sm.end():], txt
            break
    if sname is None:
        print("LINT UNMEASURED: no ModSettings subclass found")
        return 2
    decl = {n: (t, v.strip()) for t, n, v in re.findall(r"public static ([\w<>\[\]]+)\s+(\w+)\s*=(?!>)\s*([^;]+);", sbody)}
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
    # array settings are saved through a list: Scribe_Collections.Look(ref list, "<field>", ...) counts as that field's Scribe
    for key in re.findall(r'Scribe_Collections\.Look\(ref\s+\w+,\s*"(\w+)"', sbody):
        if key in decl and decl[key][0].endswith("[]"):
            seen_fields[key] = key
    for fld in decl:
        if fld not in seen_fields:
            E("settings-scribed", f"settings field {fld} is declared but never Scribed (setting is lost on restart)")
    outside = "\n".join(t for r, t in all_text.items() if r != sfile)
    # the settings window may live in the Mod class (any file with DoSettingsWindowContents / DoWindowContents)
    ui = "\n".join(re.sub(r"(public static [\w<>\[\]]+\s+\w+\s*=(?!>)[^;]*;|Scribe_Values\.Look\([^;]*;)", "", t)
                    for t in all_text.values() if re.search(r"DoSettingsWindowContents|DoWindowContents", t))
    # a field read inside an expression-bodied property of the settings class (`public static bool XActive => A && xEnabled;`) is read
    props = " ".join(re.findall(r"public static [\w<>\[\]]+\s+\w+\s*=>\s*([^;]+);", sbody))
    for fld in decl:
        pat = r"\b" + fld + r"\b"
        if not re.search(pat, outside) and not re.search(sname + r"\." + fld + r"\b", st) and not re.search(pat, props):
            W("settings-scribed", f"settings field {fld} is never read by any code (dead toggle)")
        if not re.search(pat, ui):
            W("settings-scribed", f"settings field {fld} has no control in the settings window")
    for m in sorted(set(re.findall(sname + r"\.(\w+)", code))):
        if m not in decl and m not in ("DoWindowContents", "DoSettingsWindowContents", "ExposeData", "Instance"):
            if re.match(r"[a-z]", m):
                E("settings-scribed", f"code reads {sname}.{m} which is not a declared field")

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
    print(f"{mod_name.lower()} lint: {len(defs_xml)} defs + {len(patch_xml)} patch files, {sanity['classes']} classes, "
          f"{checked['class-refs']} class/def refs, {checked['field-checks']} field checks, {checked['drivers']} drivers, "
          f"{len(decl)} settings, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1], sys.argv[2:]))
