#!/usr/bin/env python3
"""check_creaturebehaviors_defs.py - do the XML defs that use CreatureBehaviors classes agree with the C# source?

    python3 src/RimMandrake/Utils/check_creaturebehaviors_defs.py [--quiet]

Offline, reads src/**/*.xml and src/RimMandrake/CreatureBehaviors/Source/**/*.cs. Exit 0 clean, 1 findings, 2 could not tell.

WHY. RimWorld fails SILENT on this surface: a `Class="RimMandrake.CreatureBehaviors.RM_Typo"` on a comp or mod
extension discards the whole def (or the extension), a misspelt field is ignored with at worst a log line nobody
reads, and a required reference field left out turns the behaviour off with no error at all. The mod build cannot
see any of it: the XML is not compiled.

CHECKS (each finding is `KIND path:line message`):
  UNRESOLVED_CLASS   a `Class=` attribute or a class-valued element (compClass, driverClass, stateClass ...) names
                     RimMandrake.CreatureBehaviors.X and no class X is declared in the mod source.
  NOT_COMPILED       the class resolves to a .cs that RM_CreatureBehaviors.csproj does not list
                     (EnableDefaultCompileItems is false: such a file compiles into nothing, with no error).
  UNKNOWN_FIELD      a child element of a `Class=` node names no instance field on the class or its bases
                     (checked only when every ancestor is ours or a plain CompProperties/HediffCompProperties/
                     DefModExtension, whose only inherited field this check allows is compClass).
  MISSING_REQUIRED   the class's ConfigErrors() rejects a field being null/empty/<=0 and the field has no usable
                     default, and the node does not set it.
  BAD_VALUE          an int/float/bool field whose text does not parse, or an enum field naming no member.

NOT CHECKED: that a defName named by a field exists (check_refs / the load does that), and fields of classes
whose base is an engine type other than the three above (class resolution is still checked).
"""
from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CB = os.path.join(REPO, "src", "RimMandrake", "CreatureBehaviors")
NS = "RimMandrake.CreatureBehaviors."
ENGINE_BASES = {"CompProperties": {"compClass"}, "HediffCompProperties": {"compClass"}, "DefModExtension": set(),
                "object": set()}
SKIP_DIRS = ("SelfTest", "bin", "obj")


# ───────────────────────── C# side ─────────────────────────

def strip_cs(text):
    """Blank comments and string/char literals (keeps newlines so line numbers survive)."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        two = text[i:i + 2]
        if two == "//":
            while i < n and text[i] != "\n":
                i += 1
        elif two == "/*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j]))
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
            content = text[i + 1:j]
            out.append('"s"' if content else '""')
            out.append(re.sub(r"[^\n]", "", content))
            i = j + 1
        elif c == "'":
            j = i + 1
            while j < n and text[j] != "'":
                j += 2 if text[j] == "\\" else 1
            out.append("' '")
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


DECL = re.compile(r"\b(class|struct|enum|interface)\s+(\w+)(\s*<[^>{]*>)?\s*(?::\s*([^{;]+?))?\s*(?:where\s[^{]+)?\{")


def match_brace(s, open_idx):
    depth = 0
    for k in range(open_idx, len(s)):
        if s[k] == "{":
            depth += 1
        elif s[k] == "}":
            depth -= 1
            if depth == 0:
                return k
    return len(s) - 1


def top_level_statements(body):
    """Statements of a class body at brace depth 0, each as (text, startOffset, braceBody or None)."""
    stmts, buf, start, depth, k = [], [], 0, 0, 0
    while k < len(body):
        c = body[k]
        if c == "{":
            end = match_brace(body, k)
            stmts.append(("".join(buf) + "{}", start, body[k + 1:end]))
            buf, start, k = [], end + 1, end + 1
            continue
        if c == ";":
            stmts.append(("".join(buf), start, None))
            buf, start = [], k + 1
        else:
            if not buf:
                start = k
            buf.append(c)
        k += 1
    return stmts


FIELD = re.compile(r"^\s*(?:\[[^\]]*\]\s*)*((?:(?:public|private|protected|internal|static|readonly|const|new|volatile)\s+)*)"
                   r"([\w.<>,\[\]? ]+?)\s+(\w+)\s*(?:=\s*(.*))?$", re.S)


class ClassInfo:
    def __init__(self, name, kind, bases, path, line):
        self.name, self.kind, self.bases, self.path, self.line = name, kind, bases, path, line
        self.fields = {}      # name -> (type, default or None)
        self.members = []     # enum members
        self.required = {}    # field -> why
        self.config_errors = False


def parse_cs(files):
    """files: {path: text}. Returns {className: ClassInfo} (first declaration wins; partials merge fields)."""
    classes = {}
    for path, raw in files.items():
        s = strip_cs(raw)
        for m in DECL.finditer(s):
            kind, name = m.group(1), m.group(2)
            bases = [b.strip().split("<")[0].split(".")[-1] for b in (m.group(4) or "").split(",") if b.strip()]
            line = s.count("\n", 0, m.start()) + 1
            end = match_brace(s, m.end() - 1)
            body = s[m.end():end]
            ci = classes.get(name) or ClassInfo(name, kind, bases, path, line)
            classes[name] = ci
            if kind == "enum":
                ci.members = [x.split("=")[0].strip() for x in body.split(",") if x.strip()]
                continue
            if kind != "class":
                continue
            for text, _start, sub in top_level_statements(body):
                t = text.strip()
                if "(" in t.split("=")[0] and sub is not None:       # method / ctor / property-with-args
                    if "ConfigErrors" in t:
                        ci.config_errors = True
                        _scan_config_errors(ci, sub)
                    continue
                if sub is not None:                                   # property or nested type
                    continue
                fm = FIELD.match(t)
                if not fm:
                    continue
                mods, typ, fname, default = fm.group(1), fm.group(2).strip(), fm.group(3), fm.group(4)
                if re.search(r"\b(static|const)\b", mods):
                    continue
                ci.fields[fname] = (typ, default.strip() if default else None)
    return classes


COND = re.compile(r"\bif\s*\(([^{;]*?)\)\s*\{?\s*yield\s+return", re.S)


def _scan_config_errors(ci, sub):
    for m in COND.finditer(sub):
        cond = m.group(1)
        for part in re.split(r"\|\|", cond):
            p = part.strip()
            for fm in (re.fullmatch(r"(\w+)\s*==\s*null", p), re.fullmatch(r"(\w+)\.NullOrEmpty\(\)", p),
                       re.fullmatch(r"string\.IsNullOrEmpty\((\w+)\)", p), re.fullmatch(r"(\w+)\.Count\s*==\s*0", p),
                       re.fullmatch(r"(\w+)\s*(?:<=|==)\s*0(?:\.0)?f?", p)):
                if fm:
                    ci.required[fm.group(1)] = p
                    break


def all_fields(classes, name, seen=None):
    """(fields dict, complete) walking bases; complete False when an unknown base is reached."""
    seen = seen or set()
    if name in seen:
        return {}, True
    seen.add(name)
    ci = classes.get(name)
    if ci is None:
        if name in ENGINE_BASES:
            return {f: ("DefRef", None) for f in ENGINE_BASES[name]}, True
        return {}, False
    fields, complete = dict(ci.fields), True
    for b in ci.bases:
        f, c = all_fields(classes, b, seen)
        for k, v in f.items():
            fields.setdefault(k, v)
        if not c and b not in ("IExposable", "IDisposable"):
            if classes.get(b) is not None or not b.startswith("I"):
                complete = False
    return fields, complete


def all_required(classes, name, seen=None):
    seen = seen or set()
    if name in seen or name not in classes:
        return {}
    seen.add(name)
    req = {}
    for b in classes[name].bases:
        req.update(all_required(classes, b, seen))
    req.update(classes[name].required)
    return req


# ───────────────────────── XML side ─────────────────────────

CLASS_TOKEN = re.compile(r"RimMandrake\.CreatureBehaviors\.(\w+)")
STATS = {"nodes": 0, "fields": 0}


def line_of(root_text, needle_pos):
    return root_text.count("\n", 0, needle_pos) + 1


def check_xml(path, text, classes, compiled, findings):
    try:
        root = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError:
        return False
    # class-valued text anywhere (compClass, driverClass, stateClass, workerClass ...) and Class= attributes
    for m in CLASS_TOKEN.finditer(text):
        name = m.group(1)
        ln = line_of(text, m.start())
        ci = classes.get(name)
        if ci is None:
            findings.append(("UNRESOLVED_CLASS", path, ln, "%s%s is not declared in the CreatureBehaviors source" % (NS, name)))
        elif compiled is not None and os.path.basename(ci.path) not in compiled and not ci.path.startswith("<"):
            findings.append(("NOT_COMPILED", path, ln, "%s is declared in %s, which RM_CreatureBehaviors.csproj does not list"
                             % (name, os.path.basename(ci.path))))
    for el in root.iter():
        cls = el.get("Class")
        if not cls or not cls.startswith(NS):
            continue
        name = cls[len(NS):]
        ci = classes.get(name)
        if ci is None:
            continue                                   # already reported as UNRESOLVED_CLASS
        ln = _elem_line(text, el, cls)
        STATS["nodes"] += 1
        fields, complete = all_fields(classes, name)
        children = [c for c in el if isinstance(c.tag, str)]
        STATS["fields"] += len(children)
        if complete:
            for c in children:
                if c.tag not in fields:
                    findings.append(("UNKNOWN_FIELD", path, ln, "%s has no field '%s' (children are loaded by field name)"
                                     % (name, c.tag)))
        present = {c.tag for c in children}
        for fname, why in all_required(classes, name).items():
            if fname in present or fname not in fields:
                continue                               # not a field of this class (a local in ConfigErrors)
            f = fields.get(fname)
            if f is not None and f[1] is not None and not _default_is_empty(f[1], why):
                continue                               # a usable default covers it
            findings.append(("MISSING_REQUIRED", path, ln, "%s: ConfigErrors rejects '%s' and the node does not set it"
                             % (name, why)))
        for c in children:
            f = fields.get(c.tag)
            if f is None or len(c) or c.text is None:
                continue
            msg = _bad_value(f[0], c.text.strip(), classes)
            if msg:
                findings.append(("BAD_VALUE", path, ln, "%s.%s = '%s': %s" % (name, c.tag, c.text.strip(), msg)))
    return True


def _default_is_empty(default, why):
    d = default.replace(" ", "")
    if "<=0" in why.replace(" ", "") or "==0" in why.replace(" ", ""):
        return d in ("0", "0f", "0.0", "0.0f")
    return d in ("null", "default", "string.Empty", '""')


def _elem_line(text, el, cls):
    needle = 'Class="%s"' % cls
    best = text.find(needle)
    pos = best
    # pick the occurrence whose element has the same child set: cheap approximation, first one is good enough for a pointer
    return line_of(text, pos) if pos >= 0 else 0


def _bad_value(typ, val, classes):
    t = typ.replace("?", "").strip()
    try:
        if t == "int":
            int(val)
        elif t in ("float", "double"):
            float(val.rstrip("f"))
        elif t == "bool" and val.lower() not in ("true", "false"):
            return "not a bool"
        elif t in classes and classes[t].kind == "enum" and val not in classes[t].members:
            return "not a member of %s (%s)" % (t, ", ".join(classes[t].members))
    except ValueError:
        return "not a valid %s" % t
    return None


# ───────────────────────── driver ─────────────────────────

def read_tree():
    cs = {}
    for dp, dn, fn in os.walk(os.path.join(CB, "Source")):
        dn[:] = [d for d in dn if not d.startswith(SKIP_DIRS)]
        for f in fn:
            if f.endswith(".cs"):
                p = os.path.join(dp, f)
                cs[p] = open(p, encoding="utf-8-sig", errors="replace").read()
    xml = {}
    for dp, dn, fn in os.walk(os.path.join(REPO, "src")):
        dn[:] = [d for d in dn if d not in ("bin", "obj", "__pycache__", "node_modules", ".git")]
        for f in fn:
            if f.endswith(".xml"):
                p = os.path.join(dp, f)
                t = open(p, encoding="utf-8-sig", errors="replace").read()
                if "RimMandrake.CreatureBehaviors." in t:
                    xml[p] = t
    csproj = open(os.path.join(CB, "Source", "RM_CreatureBehaviors.csproj"), encoding="utf-8").read()
    compiled = set(re.findall(r'<Compile Include="([^"]+)"', csproj))
    return cs, xml, compiled


def run(cs, xml, compiled):
    classes = parse_cs(cs)
    findings, unparsed = [], 0
    for p, t in sorted(xml.items()):
        if not check_xml(p, t, classes, compiled, findings):
            unparsed += 1
    return classes, findings, unparsed


def main(argv):
    quiet = "--quiet" in argv
    cs, xml, compiled = read_tree()
    classes, findings, unparsed = run(cs, xml, compiled)
    # sanity probe: a checker that finds nothing must first prove it can see something
    n_ext = sum(1 for c in classes.values() if c.config_errors)
    if len(classes) < 50 or not xml or n_ext < 5:
        print("UNMEASURED: probe saw %d classes, %d xml files, %d ConfigErrors classes (expected 50+/1+/5+)"
              % (len(classes), len(xml), n_ext))
        return 2
    if not quiet:
        print("probe: %d classes, %d with ConfigErrors, %d xml files use them (%d unparseable, skipped), %d Class= nodes and %d field elements checked"
              % (len(classes), n_ext, len(xml), unparsed, STATS["nodes"], STATS["fields"]))
    for kind, p, ln, msg in findings:
        print("%s %s:%d %s" % (kind, os.path.relpath(p, REPO), ln, msg))
    if not quiet:
        print("check_creaturebehaviors_defs: %s" % ("%d finding(s)" % len(findings) if findings else "clean"))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
