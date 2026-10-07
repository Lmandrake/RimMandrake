#!/usr/bin/env python3
"""moddefs_lint.py - generic XML <-> C# agreement lint for one mod, no game, no build.

The CreatureBehaviors checker (check_creaturebehaviors_defs.py) proved the idea: RimWorld fails SILENT on this surface and the
build cannot see it, because the XML is not compiled. This module generalises it to any mod: it REUSES that checker's C# parser and
field/enum/ConfigErrors helpers (parse_cs, all_fields, all_required, _bad_value) and adds the checks the Diving lint grew.
Per-mod wrappers (selftest_<mod>_lint.py) only hold a Cfg and a few mod-specific extra checks.

Checks (each finding is `KIND path:line message`, each check prints a count so one that looked at nothing cannot pass):
  UNRESOLVED_CLASS   Class="NS.X" / <compClass>NS.X</compClass> names a class that is not declared in the mod source.
  NOT_COMPILED       the class lives in a .cs that its csproj does not list (EnableDefaultCompileItems false: compiles into nothing).
  UNKNOWN_FIELD      a child of a Class= node (or of an <li> of a List<ourClass> field, recursively) names no field on the class.
  MISSING_REQUIRED   ConfigErrors() rejects a null/empty/<=0 field and the node leaves it unset with no usable default.
  BAD_VALUE          an int/float/bool that does not parse, or an enum value that is no member (also inside nested <li> classes).
  CSPROJ_MISSING     a Source .cs is not in its csproj's Compile list; CSPROJ_DANGLING: a Compile entry names no file.
  STRING_LITERAL     a "RM_/RUT_/RSW_..." literal in C# is neither a defName / <li> tag under src/, a translation key, nor a class/member name.
  TRANSLATE_KEY      "RM_x".Translate() with no key in any Keyed/*.xml (the game shows the raw key).
  SCRIBE_DUP         two Scribe_*.Look calls in one class use the same label (the second overwrites the first in the save).
  DEFOF_MISSING      a [DefOf] static field names a def that no XML under src/ defines (the field is silently null at runtime).
  REFLECTION_NAME    (opt-in) a GetField/GetProperty/GetMethod("x") or `.Name == "X"` string names an identifier that appears nowhere in src/ C# (a rename silently turns the feature off).
  SETTINGS_DRIFT     a settings class's static default, Scribe default, ResetToDefaults value or slider range disagree.
  <extra>            whatever a wrapper's extra() adds.
"""
from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_creaturebehaviors_defs as chk  # noqa: E402  (parser + field/enum helpers, reused not copied)

REPO = chk.REPO
SRC = os.path.join(REPO, "src")
SKIP_DIRS = {"bin", "obj", "__pycache__", "node_modules", ".git", "Textures", "Sounds", "Assemblies", "SelfTest"}
PREFIX_LIT = re.compile(r'"((?:RM|RUT|RSW)_[A-Za-z0-9_]+)"')
TRANSLATE = re.compile(r'"([A-Za-z0-9_.]+)"\s*\.Translate(?:Simple)?\(')
CLASS_VALUED_TAGS = {"compClass", "thingClass", "workerClass", "giverClass", "driverClass", "jobClass", "stateClass", "hediffClass",
                     "inspectorTabsResolved", "stockGeneratorClass", "incidentWorkerClass", "needClass", "tickerType"}


def _walk_ok(d):
    """skip build output, art, and the offline selftest/fuzz projects that sit under Source/"""
    return d not in SKIP_DIRS and not d.endswith(("SelfTest", "Fuzz"))


class Cfg:
    def __init__(self, name, mod_dir, namespaces, sources, settings_classes=(), allow_zero=(), min_probe=None, extra=None, reflection=False, reflection_engine_names=()):
        self.name = name
        self.mod_dir = mod_dir                  # absolute
        self.namespaces = [n if n.endswith(".") else n + "." for n in namespaces]
        self.sources = sources                  # [(source_dir_abs, csproj_abs)]
        self.settings_classes = list(settings_classes)
        self.allow_zero = set(allow_zero)       # count names that may legitimately be 0 for this mod
        self.min_probe = min_probe or {}        # count name -> minimum, so a half-blind lint reads UNMEASURED
        self.extra = extra                      # callable(ctx, add_finding, counts)
        self.reflection = reflection            # check GetField/GetProperty/GetMethod/Name=="X" string lookups against identifiers under src/
        self.reflection_engine_names = set(reflection_engine_names)   # names that live in the engine, not in src/


class Inputs:
    pass


# ───────────────────────── collection ─────────────────────────

def _read(p):
    return open(p, encoding="utf-8-sig", errors="replace").read()


def collect(cfg):
    inp = Inputs()
    inp.cs, inp.cs_dir = {}, {}
    inp.csproj = {}
    for sdir, cproj in cfg.sources:
        inp.csproj[cproj] = _read(cproj)
        for dp, dn, fn in os.walk(sdir):
            dn[:] = [d for d in dn if _walk_ok(d)]
            for f in fn:
                if f.endswith(".cs"):
                    p = os.path.join(dp, f)
                    inp.cs[p] = _read(p)
                    inp.cs_dir[p] = cproj
    inp.xml = {}                                 # every src xml mentioning one of our namespaces
    inp.defnames, inp.keys = set(), set()
    ns_toks = tuple(cfg.namespaces)
    for dp, dn, fn in os.walk(SRC):
        dn[:] = [d for d in dn if _walk_ok(d)]
        for f in fn:
            if not f.endswith(".xml"):
                continue
            p = os.path.join(dp, f)
            t = _read(p)
            inp.defnames.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", t))
            inp.defnames.update(re.findall(r"<li>\s*((?:RM|RUT|RSW)_\w+)\s*</li>", t))
            if "Keyed" in dp:
                inp.keys.update(m for m in re.findall(r"<([A-Za-z0-9_.]+)>", t) if m != "LanguageData")
            if any(n in t for n in ns_toks):
                inp.xml[p] = t
    inp.identifiers = _all_identifiers()      # class / member names too: a literal may name a class (reflection), not a def
    return inp


_IDENT_CACHE = {}


def _all_identifiers():
    """Every identifier token in every src C# file, comments and string literal bodies blanked."""
    if "ids" in _IDENT_CACHE:
        return _IDENT_CACHE["ids"]
    ids = set()
    for dp, dn, fn in os.walk(SRC):
        dn[:] = [d for d in dn if d not in SKIP_DIRS and d not in ("obj", "bin")]
        for f in fn:
            if f.endswith(".cs"):
                ids.update(re.findall(r"[A-Za-z_]\w*", mask(_read(os.path.join(dp, f)), False)))
    _IDENT_CACHE["ids"] = ids
    return ids


# ───────────────────────── checks ─────────────────────────

def mask(text, keep_strings):
    """Same-length copy of C# text: comments become spaces; string/char literal BODIES become spaces unless keep_strings."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        two = text[i:i + 2]
        if two == "//":
            while i < n and text[i] != "\n":
                out[i] = " "
                i += 1
        elif two == "/*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if text[k] != "\n":
                    out[k] = " "
            i = j
        elif c == '"':
            verbatim = i > 0 and text[i - 1] == "@"
            j = i + 1
            while j < n:
                if verbatim:
                    if text[j] == '"':
                        if text[j + 1:j + 2] == '"':
                            j += 2
                            continue
                        break
                else:
                    if text[j] == "\\":
                        j += 2
                        continue
                    if text[j] == '"':
                        break
                j += 1
            if not keep_strings:
                for k in range(i + 1, min(j, n)):
                    if text[k] != "\n":
                        out[k] = " "
            i = j + 1
        elif c == "'":
            j = i + 1
            while j < n and text[j] != "'":
                j += 2 if text[j] == "\\" else 1
            if not keep_strings:
                for k in range(i + 1, min(j, n)):
                    out[k] = " "
            i = j + 1
        else:
            i += 1
    return "".join(out)



def _line(text, pos):
    return text.count("\n", 0, pos) + 1


def _check_node(cfg, path, text, el, ns, classes, fields_of, findings, counts, ln, owner):
    """Check one node known to be an instance of class `owner` (children are loaded by field name)."""
    fields, complete = fields_of
    children = [c for c in el if isinstance(c.tag, str)]
    counts["xml field children"] = counts.get("xml field children", 0) + len(children)
    if complete:
        for c in children:
            if c.tag not in fields and c.tag != "li":
                findings.append(("UNKNOWN_FIELD", path, ln, "%s has no field '%s' (children are loaded by field name)" % (owner, c.tag)))
    present = {c.tag for c in children}
    for fname, why in chk.all_required(classes, owner).items():
        if fname in present or fname not in fields:
            continue
        f = fields.get(fname)
        if f is not None and f[1] is not None and not chk._default_is_empty(f[1], why):
            continue
        findings.append(("MISSING_REQUIRED", path, ln, "%s: ConfigErrors rejects '%s' and the node does not set it" % (owner, why)))
    for c in children:
        f = fields.get(c.tag)
        if f is None:
            continue
        typ = f[0].replace("?", "").strip()
        m = re.fullmatch(r"(?:List|IList|HashSet)<\s*(\w+)\s*>", typ)
        inner = m.group(1) if m else typ
        if len(c):                                   # nested structure: recurse into <li> items / a nested class value
            ci = classes.get(inner)
            if ci is not None and ci.kind == "class":
                items = [x for x in c if isinstance(x.tag, str)] if m else [c]
                for it in items:
                    cls_attr = it.get("Class")
                    target = inner
                    if cls_attr and cls_attr.startswith(ns):
                        target = cls_attr[len(ns):]
                    if target in classes and classes[target].kind == "class":
                        _check_node(cfg, path, text, it, ns, classes, chk.all_fields(classes, target), findings, counts, ln, target)
            elif m and inner in ("int", "float", "double", "bool"):
                for it in c:
                    if isinstance(it.tag, str) and it.text is not None:
                        msg = chk._bad_value(inner, it.text.strip(), classes)
                        if msg:
                            findings.append(("BAD_VALUE", path, ln, "%s.%s item '%s': %s" % (owner, c.tag, it.text.strip(), msg)))
                counts["list items checked"] = counts.get("list items checked", 0) + len([x for x in c if isinstance(x.tag, str)])
            continue
        if c.text is None:
            continue
        val = c.text.strip()
        if m:
            continue
        msg = chk._bad_value(f[0], val, classes)
        if msg:
            findings.append(("BAD_VALUE", path, ln, "%s.%s = '%s': %s" % (owner, c.tag, val, msg)))
        if f[0].replace("?", "").strip() in classes and classes[f[0].replace("?", "").strip()].kind == "enum":
            counts["enum values checked"] = counts.get("enum values checked", 0) + 1
    # list fields whose <li> items are plain enums (e.g. List<MyEnum>)
    for c in children:
        f = fields.get(c.tag)
        if f is None:
            continue
        m = re.fullmatch(r"(?:List|IList|HashSet)<\s*(\w+)\s*>", f[0].replace("?", "").strip())
        if m and m.group(1) in classes and classes[m.group(1)].kind == "enum":
            for it in c:
                if isinstance(it.tag, str) and it.text and it.text.strip() not in classes[m.group(1)].members:
                    findings.append(("BAD_VALUE", path, ln, "%s.%s item '%s' is not a member of %s" % (owner, c.tag, it.text.strip(), m.group(1))))


def check(cfg, inp):
    findings = []
    counts = {}
    classes = chk.parse_cs(inp.cs)
    counts["classes"] = len(classes)
    compiled_by_proj = {}
    for cproj, t in inp.csproj.items():
        incl = re.findall(r'<Compile Include="([^"]+)"', t)
        compiled_by_proj[cproj] = (set(os.path.basename(x.replace("\\", "/")) for x in incl if "*" not in x),
                                   any("*" in x for x in incl))

    def compiled_ok(cs_path):
        names, glob_all = compiled_by_proj[inp.cs_dir[cs_path]]
        return glob_all or os.path.basename(cs_path) in names

    # --- 1/2: XML class refs and field children
    n_refs = 0
    for path, text in sorted(inp.xml.items()):
        try:
            root = ET.fromstring(text.encode("utf-8"))
        except ET.ParseError as e:
            findings.append(("XML_PARSE", path, 0, "does not parse: %s" % e))
            continue
        for ns in cfg.namespaces:
            for m in re.finditer(re.escape(ns) + r"(\w+)", text):
                n_refs += 1
                name = m.group(1)
                ci = classes.get(name)
                ln = _line(text, m.start())
                if ci is None:
                    findings.append(("UNRESOLVED_CLASS", path, ln, "%s%s is not declared in the %s source" % (ns, name, cfg.name)))
                elif ci.path in inp.cs_dir and not compiled_ok(ci.path):
                    findings.append(("NOT_COMPILED", path, ln, "%s is declared in %s, which its csproj does not list" % (name, os.path.basename(ci.path))))
            for el in root.iter():
                cls = el.get("Class")
                if (not cls or not cls.startswith(ns)) and isinstance(el.tag, str) and el.tag.startswith(ns):
                    cls = el.tag                         # a custom Def type written as the element tag: <NS.MyDef>
                if not cls or not cls.startswith(ns):
                    continue
                name = cls[len(ns):]
                if name not in classes or classes[name].kind != "class":
                    continue
                ln = chk._elem_line(text, el, cls)
                counts["Class= nodes"] = counts.get("Class= nodes", 0) + 1
                _check_node(cfg, path, text, el, ns, classes, chk.all_fields(classes, name), findings, counts, ln, name)
    counts["xml class refs"] = n_refs

    # --- 3: csproj <-> source
    n_cs = 0
    for cproj, t in inp.csproj.items():
        names, glob_all = compiled_by_proj[cproj]
        on_disk = {os.path.basename(p) for p, c in inp.cs_dir.items() if c == cproj}
        n_cs += len(on_disk)
        if not glob_all:
            for f in sorted(on_disk - names):
                findings.append(("CSPROJ_MISSING", cproj, 0, "%s is not in the Compile list (compiles into nothing, no error)" % f))
            for f in sorted(names - on_disk):
                findings.append(("CSPROJ_DANGLING", cproj, 0, "Compile entry %s names no file" % f))
    counts["cs files"] = n_cs

    # --- 4/5: string literals and translation keys
    n_lit = n_tr = 0
    for p, raw in inp.cs.items():
        nocom = mask(raw, True)
        for m in PREFIX_LIT.finditer(nocom):
            lit = m.group(1)
            if nocom[max(0, m.start() - 20):m.start()].rstrip().endswith("MakeToil("):
                continue                                  # a toil's debug name, not a def
            n_lit += 1
            if lit not in inp.defnames and lit not in inp.keys and lit not in inp.identifiers:
                findings.append(("STRING_LITERAL", p, _line(nocom, m.start()), '"%s" is neither a defName/<li> tag under src/ nor a translation key' % lit))
        for m in TRANSLATE.finditer(nocom):
            n_tr += 1
            k = m.group(1)
            if re.match(r"(RM|RUT|RSW)_", k) and k not in inp.keys:
                findings.append(("TRANSLATE_KEY", p, _line(nocom, m.start()), '"%s".Translate() has no key in any Keyed/*.xml' % k))
    counts["rm string literals"] = n_lit
    counts["Translate() calls"] = n_tr

    # --- 6: Scribe label duplicates per class
    n_scribe = 0
    for p, raw in inp.cs.items():
        s = mask(raw, False)
        nocom = mask(raw, True)
        for m in chk.DECL.finditer(s):
            if m.group(1) != "class":
                continue
            end = chk.match_brace(s, m.end() - 1)
            body_raw = nocom[m.end():end]
            labels = re.findall(r'Scribe_(?:Values|Defs|References|Collections|Deep)\.Look\w*\s*\(\s*(?:ref\s+)?[\w.\[\]]+\s*,\s*"(\w+)"', body_raw)
            n_scribe += len(labels)
            seen = set()
            for lab in labels:
                if lab in seen:
                    findings.append(("SCRIBE_DUP", p, _line(raw, m.start()), "class %s Scribes label '%s' twice (the second overwrites the first in the save)" % (m.group(2), lab)))
                seen.add(lab)
    counts["Scribe labels"] = n_scribe

    # --- 7: [DefOf] fields
    n_defof = 0
    for p, raw in inp.cs.items():
        for m in re.finditer(r"\[DefOf\]\s*public\s+static\s+class\s+(\w+)\s*\{(.*?)\n\s*\}", raw, re.S):
            for fm in re.finditer(r"public\s+static\s+\w+\s+(\w+)\s*;", m.group(2)):
                n_defof += 1
                name = fm.group(1)
                if re.match(r"(RM|RUT|RSW)_", name) and name not in inp.defnames:
                    findings.append(("DEFOF_MISSING", p, _line(raw, m.start(2) + fm.start()), "[DefOf] %s.%s: no def of that name under src/ (the field stays null)" % (m.group(1), name)))
    counts["DefOf fields"] = n_defof

    # --- 7b: reflection-by-string names
    n_refl = 0
    if cfg.reflection and inp.identifiers is not None:
        for p, raw in inp.cs.items():
            nocom = mask(raw, True)
            for m in re.finditer(r'(?:GetField|GetProperty|GetMethod)\(\s*"(\w+)"|\.Name\s*[=!]=\s*"(\w+)"', nocom):
                name = m.group(1) or m.group(2)
                n_refl += 1
                if name not in inp.identifiers and name not in cfg.reflection_engine_names:
                    findings.append(("REFLECTION_NAME", p, _line(nocom, m.start()), '"%s" is looked up by reflection but no identifier of that name exists in src/ C#' % name))
        counts["reflection names"] = n_refl

    # --- 8: settings classes
    n_set = 0
    for p, raw in inp.cs.items():
        for cname in cfg.settings_classes:
            m = re.search(r"class\s+%s\b[^{]*\{" % re.escape(cname), raw)
            if not m:
                continue
            end = chk.match_brace(raw, m.end() - 1)
            body = raw[m.end():end]
            body_nc = mask(raw, True)[m.end():end]
            statics = {}
            for fm in re.finditer(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);", body_nc):
                statics[fm.group(2)] = (fm.group(1), _norm(fm.group(3)))
            scribes = {}
            for sm in re.finditer(r'Scribe_Values\.Look\(\s*ref\s+(\w+)\s*,\s*"(\w+)"\s*,\s*([^,)]+)', body_nc):
                scribes[sm.group(1)] = (sm.group(2), _norm(sm.group(3)))
            resets = {}
            rm_ = re.search(r"static\s+void\s+ResetToDefaults\s*\(\s*\)\s*\{", body_nc)
            if rm_:
                rend = chk.match_brace(body_nc, rm_.end() - 1)
                for rr in re.finditer(r"(\w+)\s*=\s*([^;]+);", body_nc[rm_.end():rend]):
                    resets[rr.group(1)] = _norm(rr.group(2))
            sliders = {}
            for sl in re.finditer(r"(\w+)\s*=\s*\w+\.Slider\(\s*\1\s*,\s*([-\d.]+)f?\s*,\s*([-\d.]+)f?\s*\)", body_nc):
                sliders[sl.group(1)] = (float(sl.group(2)), float(sl.group(3)))
            for name, (typ, dflt) in statics.items():
                n_set += 1
                if name not in scribes:
                    findings.append(("SETTINGS_DRIFT", p, 0, "%s.%s is never Scribed (the setting is lost on restart)" % (cname, name)))
                else:
                    lab, sd = scribes[name]
                    if lab != name:
                        findings.append(("SETTINGS_DRIFT", p, 0, "%s.%s is Scribed under label '%s'" % (cname, name, lab)))
                    if sd != dflt:
                        findings.append(("SETTINGS_DRIFT", p, 0, "%s.%s defaults to %s but its Scribe default is %s" % (cname, name, dflt, sd)))
                if rm_:
                    if name not in resets:
                        findings.append(("SETTINGS_DRIFT", p, 0, "%s.%s is not restored by ResetToDefaults" % (cname, name)))
                    elif resets[name] != dflt:
                        findings.append(("SETTINGS_DRIFT", p, 0, "%s.%s defaults to %s but ResetToDefaults sets %s" % (cname, name, dflt, resets[name])))
                if name in sliders:
                    lo, hi = sliders[name]
                    try:
                        dv = float(dflt.rstrip("f"))
                        if not (lo <= dv <= hi):
                            findings.append(("SETTINGS_DRIFT", p, 0, "%s.%s default %s is outside its slider range %s..%s" % (cname, name, dflt, lo, hi)))
                    except ValueError:
                        pass
    counts["settings fields"] = n_set

    if cfg.extra:
        cfg.extra(Ctx(cfg, inp, classes), findings, counts)
    return findings, counts


def _norm(v):
    v = v.strip().rstrip("f").rstrip("F")
    try:
        return repr(float(v)) if re.fullmatch(r"-?\d+(\.\d*)?", v) else v
    except ValueError:
        return v


class Ctx:
    def __init__(self, cfg, inp, classes):
        self.cfg, self.inp, self.classes = cfg, inp, classes

    def cs_text(self, basename):
        for p, t in self.inp.cs.items():
            if os.path.basename(p) == basename:
                return p, t
        return None, None

    def xml_files(self, under):
        out = {}
        for dp, dn, fn in os.walk(under):
            dn[:] = [d for d in dn if _walk_ok(d)]
            for f in fn:
                if f.endswith(".xml"):
                    out[os.path.join(dp, f)] = _read(os.path.join(dp, f))
        return out


# ───────────────────────── driver ─────────────────────────

def report(cfg, findings, counts, quiet=False):
    bad = False
    for k in sorted(counts):
        if not quiet:
            print("lint %s: %d" % (k, counts[k]))
    for k, need in cfg.min_probe.items():
        if counts.get(k, 0) < need:
            print("UNMEASURED: check '%s' saw %d, expected at least %d (the lint is half-blind)" % (k, counts.get(k, 0), need))
            bad = True
    for k in ("classes", "xml class refs", "cs files"):
        if counts.get(k, 0) == 0 and k not in cfg.allow_zero:
            print("UNMEASURED: check '%s' looked at nothing" % k)
            bad = True
    for kind, p, ln, msg in findings:
        print("%s %s:%d %s" % (kind, os.path.relpath(p, REPO) if os.path.isabs(p) else p, ln, msg))
    print("%s lint: %s" % (cfg.name.lower(), "OK" if not findings and not bad else "%d FINDINGS%s" % (len(findings), " + UNMEASURED" if bad else "")))
    return 1 if (findings or bad) else 0


def kinds(findings):
    return {k for k, _p, _l, _m in findings}
