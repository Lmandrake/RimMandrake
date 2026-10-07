#!/usr/bin/env python3
"""lint_def_type_refs.py - every C# type an XML def or patch names must resolve, offline, before a game load.

WHY. A def whose `Class="X"` / `<compClass>X</compClass>` names a type that does not exist (renamed, namespace moved,
file never added to an explicit-Compile csproj, source newer than the committed DLL) is DISCARDED WHOLE by the loader,
and a patch carrying one fails its operation - both log one line among thousands and nothing else. That is how a
missing-type bug in the Thurrock content hid. This walks the whole repo and cross-checks.

WHAT IT CHECKS (per reference found in src/**/*.xml):
  UNRESOLVED        the type is nowhere in any .cs under src/ (only names under one of OUR namespace roots, or a bare
                    RM_/RSW_/RUT_ name, are judged; vanilla and donor-mod types cannot be seen from here and are skipped).
  NOT_COMPILED      declared in a .cs that its csproj does not compile (EnableDefaultCompileItems=false and no
                    <Compile Include>), so the build produces nothing and there is no error.
  NOT_IN_DLL        declared and compiled, but the type's name is absent from the mod's committed DLL (source ahead of
                    the build, or a DLL never rebuilt). UNMEASURED when the DLL cannot be found or fails its sanity probe.
  NOT_INSTANTIABLE  Class= names an abstract/static class, interface or enum.
  NO_DEPENDENCY     REAL missing hard dependency: the type lives in another mod's assembly, nothing guards the reference, and the
                    referring mod's modDependencies chain (transitive, through About.xml files in src/) never reaches the
                    owner. A def naming a type from an absent assembly is discarded whole. WARN, never fails the run.
  DIRECTION         the tier rule is broken: RM (mandrake.rm.*) must not need RSW or RUT, RSW must not need RUT. Reported
                    both for type references and for declared hard dependencies. WARN, never auto-fixed.
Cross-mod references that are NOT defects are classified (INFO, shown by -v) instead of warned:
  INTRA_COMPOSITION both mods are folded into the composed mod (Biomes.compose.json, entries with wave <= compose_wave): one mod.
  GUARDED_DEP       the referrer's hard-dependency closure already reaches the owner (a dependency on a folded packageId
                    counts as one on the composed mod).
  GUARDED_XML       behind a PatchOperationFindMod <match> (mods are matched by NAME or packageId), MayRequire on any element
                    EXCEPT <Operation> (the engine ignores it there), or a LoadFolders.xml IfModActive folder.
  GUARDED_COND      inside a PatchOperationConditional <match> whose xpath tests a def the owner mod declares.
  QUERY_ONLY        the name only appears inside a patch <xpath> (a query, matches nothing when the owner is absent).

USAGE
    python3 src/RimMandrake/Utils/lint_def_type_refs.py [--mod EnvironmentalHazards] [--root DIR] [--no-dll] [-q]
Exit 0 = no UNRESOLVED/NOT_COMPILED/NOT_IN_DLL/NOT_INSTANTIABLE; NO_DEPENDENCY never fails the run on its own.
A finding is evidence about FILES, never about the running game.
NOT_IN_DLL is a LITERAL search for the exact type name in the DLL bytes (type names are UTF-8 in the metadata string heap), guarded by a probe that the DLL contains its own assembly name; it answers 'is this one name present', never a count.
"""
import argparse
import fnmatch
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
CLASSES = ("INTRA_COMPOSITION", "GUARDED_DEP", "GUARDED_XML", "GUARDED_COND", "QUERY_ONLY")
BARE_PREFIXES = ("RM_", "RSW_", "RUT_")
SKIP_DIRS = {"obj", "bin", "__pycache__", ".git", "SelfTest"}
TYPE_TEXT = re.compile(r"^[A-Za-z_]\w*(\.\w+)+(\+\w+)*$")
XPATH_CLASS = re.compile(r"""@Class\s*=\s*(?:"([^"]+)"|'([^']+)')""")


# ---- C# declarations ------------------------------------------------------------------------------------------------
def strip_cs(src):
    """Blank comments, strings and chars (keeping newlines) so brace/keyword scanning sees only code."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        two = src[i:i + 2]
        if two == "//":
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif two == "/*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in src[i:j])); i = j
        elif c == '"' or (c in "@$" and src[i + 1:i + 2] in ('"', "$", "@") and '"' in src[i:i + 3]):
            j = i
            verbatim = "@" in src[i:i + 3].split('"')[0]
            while src[j] != '"':
                j += 1
            j += 1
            while j < n:
                if verbatim:
                    if src[j] == '"':
                        if src[j + 1:j + 2] == '"':
                            j += 2; continue
                        break
                else:
                    if src[j] == "\\":
                        j += 2; continue
                    if src[j] == '"':
                        break
                j += 1
            j = min(n, j + 1)
            out.append("".join(ch if ch == "\n" else " " for ch in src[i:j])); i = j
        elif c == "'":
            j = i + 1
            while j < n and src[j] != "'":
                j += 2 if src[j] == "\\" else 1
            j = min(n, j + 1)
            out.append(" " * (j - i)); i = j
        else:
            out.append(c); i += 1
    return "".join(out)


TOKEN = re.compile(r"\{|\}|;|\b(namespace)\s+([\w.]+)|\b(class|struct|interface|enum|record)\s+(\w+)")
MODS = ("abstract", "static", "sealed", "partial", "public", "internal", "private", "protected", "unsafe", "new", "readonly", "ref")


def parse_cs(path):
    """-> [(fullname, kind, modifiers:set)] for every type declared in the file (nested as Ns.Outer+Inner)."""
    try:
        text = strip_cs(open(path, encoding="utf-8-sig", errors="replace").read())
    except OSError:
        return []
    types, stack, file_ns, pending = [], [], "", None
    for m in TOKEN.finditer(text):
        tok = m.group(0)
        if m.group(1):
            pending = ("ns", m.group(2)); continue
        if m.group(3):
            before = text[max(0, m.start() - 120):m.start()]
            tail = re.split(r"[;{}]", before)[-1]
            mods = {w for w in re.findall(r"\w+", tail) if w in MODS}
            pending = ("type", m.group(4), m.group(3), mods); continue
        if tok == "{":
            if pending and pending[0] == "ns":
                stack.append(("ns", pending[1]))
            elif pending and pending[0] == "type":
                outer = [f for f in stack if f[0] in ("ns", "type")]
                if any(f[0] == "other" for f in stack):
                    stack.append(("other", None))
                else:
                    ns = ".".join([file_ns] * bool(file_ns) + [f[1] for f in stack if f[0] == "ns"])
                    chain = [f[1] for f in stack if f[0] == "type"]
                    full = (ns + "." if ns else "") + "+".join(chain + [pending[1]])
                    types.append((full, pending[2], pending[3]))
                    stack.append(("type", pending[1]))
            else:
                stack.append(("other", None))
            pending = None
        elif tok == "}":
            if stack:
                stack.pop()
        elif tok == ";":
            if pending and pending[0] == "ns":
                file_ns = pending[1]
            elif pending and pending[0] == "type" and not any(f[0] == "other" for f in stack):
                ns = ".".join([file_ns] * bool(file_ns) + [f[1] for f in stack if f[0] == "ns"])
                chain = [f[1] for f in stack if f[0] == "type"]
                types.append(((ns + "." if ns else "") + "+".join(chain + [pending[1]]), pending[2], pending[3]))
            pending = None
    return types


# ---- csproj compile sets --------------------------------------------------------------------------------------------
def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        yield dp, fns


def glob_re(pat):
    """MSBuild-style glob (forward slashes) -> compiled regex. `**/` spans directories, `*` stays in one."""
    out, i = "", 0
    while i < len(pat):
        if pat.startswith("**/", i):
            out += "(?:.*/)?"; i += 3
        elif pat.startswith("**", i):
            out += ".*"; i += 2
        elif pat[i] == "*":
            out += "[^/]*"; i += 1
        elif pat[i] == "?":
            out += "[^/]"; i += 1
        else:
            out += re.escape(pat[i]); i += 1
    return re.compile("^" + out + "$")


class Csproj:
    def __init__(self, path):
        self.path = path
        self.dir = os.path.dirname(path)
        text = open(path, encoding="utf-8-sig", errors="replace").read()
        m = re.search(r"<AssemblyName>([^<]+)</AssemblyName>", text)
        self.assembly = m.group(1) if m else os.path.splitext(os.path.basename(path))[0]
        m = re.search(r"<EnableDefaultCompileItems>\s*(\w+)\s*</EnableDefaultCompileItems>", text)
        self.defaults = not (m and m.group(1).lower() == "false")
        # document order matters: `Remove ..\**\*.cs` then `Include *.cs` re-adds the project's own folder
        self.items = [(op, glob_re(self._norm(x))) for op, x in re.findall(r'<Compile\s+(Include|Remove)="([^"]+)"', text)]

    def _norm(self, p):
        return os.path.normpath(os.path.join(self.dir, p.replace("\\", "/"))).replace(os.sep, "/")

    def compiles(self, cs):
        c = os.path.normpath(cs).replace(os.sep, "/")
        here = self.dir.replace(os.sep, "/")
        on = self.defaults and c.startswith(here + "/") and not re.search(r"/(obj|bin)/", c)
        for op, rx in self.items:
            if rx.match(c):
                on = (op == "Include")
        return on


def find_mod_root(path):
    d = os.path.dirname(os.path.abspath(path))
    while d.startswith(SRC) and d != SRC:
        if os.path.isfile(os.path.join(d, "About", "About.xml")):
            return d
        d = os.path.dirname(d)
    return None


def find_mod_name(rel):
    root = find_mod_root(os.path.join(REPO, rel))
    return os.path.basename(root) if root else "?"


def about_info(mod_root):
    p = os.path.join(mod_root, "About", "About.xml")
    try:
        text = open(p, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return None, ""
    m = re.search(r"<packageId>([^<]+)</packageId>", text)
    return (m.group(1).strip().lower() if m else None), text.lower()


# ---- the dependency graph --------------------------------------------------------------------------------------------
BIOMES_PKG = "mandrake.rm.biomes"


def _tier(pkg):
    if pkg and pkg.startswith("mandrake.rm."):
        return 0
    if pkg and pkg.startswith("mandrake.rsw."):
        return 1
    if pkg and pkg.startswith("mandrake.rut."):
        return 2
    return None


class DepGraph:
    """packageId graph from every About.xml under src/. Mods the compose manifest folds in (wave <= compose_wave) are ONE
    node, the composed mod: a reference between two of them is intra-composition, and a dependency on any folded
    packageId is a dependency on the composed mod. A hard dependency closure (modDependencies only: loadAfter alone does
    not keep a def alive when the other mod is absent) decides whether the referrer already pulls the owner in."""
    def __init__(self, src=SRC):
        self.composed_roots = {}     # mod folder basename -> compose key
        self.composed_pkg = BIOMES_PKG
        mf = os.path.join(src, "RimMandrake", "Biomes.compose.json")
        try:
            import json
            m = json.load(open(mf, encoding="utf-8"))
            self.composed_pkg = m.get("about", {}).get("packageId", BIOMES_PKG).lower()
            cw = m.get("compose_wave", 0)
            for e in m.get("entries", []):
                if e.get("wave", 99) <= cw:
                    self.composed_roots[e["source"]] = e["key"]
        except (OSError, ValueError):
            pass
        self.pkg_root = {}           # packageId -> mod root dir
        self.name_pkg = {}           # lower-cased <name> -> packageId (PatchOperationFindMod matches mod NAMES)
        self.raw_deps = {}           # packageId -> [hard dependency packageIds]
        for dp, fns in walk(src):
            if "About.xml" in fns and os.path.basename(dp) == "About":
                root = os.path.dirname(dp)
                try:
                    text = open(os.path.join(dp, "About.xml"), encoding="utf-8-sig", errors="replace").read()
                    et = ET.fromstring(text)
                except (OSError, ET.ParseError):
                    continue
                pkg = (et.findtext("packageId") or "").strip().lower()
                if not pkg:
                    continue
                self.pkg_root[pkg] = root
                nm = (et.findtext("name") or "").strip().lower()
                if nm:
                    self.name_pkg[nm] = pkg
                deps = []
                for li in et.findall("modDependencies/li"):
                    d = (li.findtext("packageId") or "").strip().lower()
                    if d:
                        deps.append(d)
                self.raw_deps[pkg] = deps
        self.node_deps = defaultdict(set)
        for pkg, deps in self.raw_deps.items():
            n = self.node(pkg)
            for d in deps:
                dn = self.node(d)
                if dn != n:
                    self.node_deps[n].add(dn)
        self._clo = {}
        self._lf = {}
        self._dn = {}

    def loadfolder_guards(self, root):
        """-> [(abs folder, frozenset(pkgs))] for LoadFolders.xml entries gated by IfModActive*: the folder only loads with them."""
        if root not in self._lf:
            out = []
            try:
                et = ET.parse(os.path.join(root, "LoadFolders.xml")).getroot()
                for li in et.iter("li"):
                    pk = set()
                    for attr in ("IfModActive", "IfModActiveAll"):
                        pk.update(x.strip().lower() for x in (li.get(attr) or "").split(",") if x.strip())
                    anyof = [x.strip().lower() for x in (li.get("IfModActiveAny") or "").split(",") if x.strip()]
                    if len(anyof) == 1:
                        pk.update(anyof)
                    path = (li.text or "").strip().strip("/")
                    if pk and path:
                        out.append((os.path.normpath(os.path.join(root, path)), frozenset(pk)))
            except (OSError, ET.ParseError):
                pass
            self._lf[root] = out
        return self._lf[root]

    def defnames_in(self, root):
        if root not in self._dn:
            names = set()
            for dp, fns in walk(root):
                for fn in fns:
                    if fn.endswith(".xml"):
                        try:
                            names.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", open(os.path.join(dp, fn), encoding="utf-8-sig", errors="replace").read()))
                        except OSError:
                            pass
            self._dn[root] = names
        return self._dn[root]

    def is_composed_root(self, root):
        return bool(root) and os.path.basename(root) in self.composed_roots and os.path.basename(os.path.dirname(root)) == "RimMandrake"

    def node(self, pkg):
        if not pkg:
            return pkg
        pkg = pkg.lower()
        root = self.pkg_root.get(pkg)
        return self.composed_pkg if root and self.is_composed_root(root) else pkg

    def closure(self, node):
        if node not in self._clo:
            seen, todo = {node}, [node]
            while todo:
                for d in self.node_deps.get(todo.pop(), ()):
                    if d not in seen:
                        seen.add(d)
                        todo.append(d)
            self._clo[node] = seen
        return self._clo[node]


def classify_dependency(graph, ref_pkg, ref_root, owner_pkg, owner_root, guards, weak, ctx=""):
    """-> (class, detail). class in INTRA_COMPOSITION | GUARDED_DEP | GUARDED_XML | GUARDED_COND | QUERY_ONLY | REAL."""
    rn, on = graph.node(ref_pkg), graph.node(owner_pkg)
    if rn == on:
        return "INTRA_COMPOSITION", "both folded into %s" % rn
    if ctx.startswith("@Class in <xpath>"):
        return "QUERY_ONLY", "a type name inside a patch <xpath> is only a query: it matches nothing when %s is absent and never instantiates it" % owner_pkg
    if on in graph.closure(rn):
        return "GUARDED_DEP", "%s hard-depends on %s (transitively)" % (rn, on)
    if {graph.name_pkg.get(g, g) for g in guards} & {owner_pkg.lower(), on}:
        return "GUARDED_XML", "reference is behind a FindMod/MayRequire naming %s" % owner_pkg
    if weak and owner_root:
        owned = graph.defnames_in(owner_root)
        if any(d in owned for xp in weak for d in re.findall(r"defName\s*=\s*[\"']([^\"']+)[\"']", xp)):
            return "GUARDED_COND", "reference is inside a PatchOperationConditional match whose xpath tests a def that %s declares" % owner_pkg
    return "REAL", "type is in %s but %s's About.xml has no hard dependency chain to it" % (owner_pkg, ref_pkg)


# ---- the index ------------------------------------------------------------------------------------------------------
class Index:
    def __init__(self, src=SRC):
        self.csprojs = []
        self.cs_files = []
        for dp, fns in walk(src):
            for fn in fns:
                full = os.path.join(dp, fn)
                if fn.endswith(".csproj") and "SelfTest" not in fn:
                    try:
                        self.csprojs.append(Csproj(full))
                    except OSError:
                        pass
                elif fn.endswith(".cs"):
                    self.cs_files.append(full)
        self.decl = defaultdict(list)       # full name -> [(file, kind, mods)]
        self.short = defaultdict(set)       # short name -> {full}
        self.roots = set()
        for f in self.cs_files:
            for full, kind, mods in parse_cs(f):
                self.decl[full].append((f, kind, mods))
                self.short[full.split("+")[-1].split(".")[-1]].add(full)
                if "." in full and full.split(".")[0] not in ("System", "Verse", "RimWorld", "UnityEngine", "HarmonyLib"):
                    self.roots.add(full.split(".")[0])
        self._owner = {}

    def owning_csproj(self, cs):
        best = None
        for p in self.csprojs:
            if p.compiles(cs):
                if best is None or len(p.dir) > len(best.dir):
                    best = p
        return best

    def candidate_csprojs(self, cs):
        d = os.path.dirname(os.path.abspath(cs))
        out = [p for p in self.csprojs if d.startswith(p.dir + os.sep) or d == p.dir]
        return sorted(out, key=lambda p: -len(p.dir))

    def resolve(self, name):
        n = name.strip()
        for cand in (n, n.replace(".", "+") if False else n):
            if cand in self.decl:
                return cand
        # Ns.Outer.Inner written with dots for a nested type
        parts = n.split(".")
        for i in range(len(parts) - 1, 0, -1):
            cand = ".".join(parts[:i]) + "." + "+".join(parts[i:])
            if cand in self.decl:
                return cand
        return None


# ---- XML refs -------------------------------------------------------------------------------------------------------
def _guards_of(chain):
    """Packages that make a reference harmless when absent, from the element chain root..el.
    MayRequire counts on every element EXCEPT <Operation> (decompiled 1.6 ignores it there); a PatchOperationFindMod
    counts only for refs inside its <match>; a PatchOperationConditional's xpath is recorded for refs inside its <match> (it guards only if the xpath names a def the OWNER mod declares)."""
    pk, weak = set(), []
    for i, a in enumerate(chain):
        if a.tag != "Operation":
            for attr in ("MayRequire", "MayRequireAnyOf"):
                v = a.get(attr)
                if v:
                    pk.update(x.strip().lower() for x in v.split(",") if x.strip())
        cls = a.get("Class")
        if cls in ("PatchOperationFindMod", "PatchOperationConditional") and i + 1 < len(chain) and chain[i + 1].tag == "match":
            if cls == "PatchOperationFindMod":
                mods = a.find("mods")
                if mods is not None:
                    pk.update((li.text or "").strip().lower() for li in mods)
            else:
                weak.append((a.findtext("xpath") or ""))
    return frozenset(x for x in pk if x), tuple(weak)


def xml_refs_g(path):
    """-> [(type string, context, guards frozenset, conditional xpaths tuple)] referenced from one XML file."""
    refs = []
    try:
        raw = open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return refs
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        for m in re.finditer(r'Class\s*=\s*"([^"]+)"', raw):
            refs.append((m.group(1), "Class=", frozenset(), ()))
        return refs
    def walk_el(el, chain):
        chain = chain + [el]
        if isinstance(el.tag, str):
            g, weak = _guards_of(chain)
            def add(n, c):
                refs.append((n, c, g, weak))
            c = el.get("Class")
            if c:
                add(c.strip(), "Class= on <%s>" % el.tag)
            t = (el.text or "").strip()
            if t:
                if TYPE_TEXT.match(t) and not t.endswith((".xml", ".png", ".ogg", ".wav")):
                    add(t, "<%s>" % el.tag)
                elif el.tag.endswith("Class") and re.match(r"^[A-Za-z_][\w+]*$", t):
                    add(t, "<%s>" % el.tag)
                for m in XPATH_CLASS.finditer(t):
                    add((m.group(1) or m.group(2)).strip(), "@Class in <%s>" % el.tag)
            for k, v in el.attrib.items():
                if k != "Class":
                    for m in XPATH_CLASS.finditer(v):
                        add((m.group(1) or m.group(2)).strip(), "@Class in %s=" % k)
        for ch in el:
            walk_el(ch, chain)
    walk_el(root, [])
    return refs


def xml_refs(path):
    """-> [(type string, line-ish context)] referenced from one XML file."""
    return [(n, c) for n, c, _g, _w in xml_refs_g(path)]


_dll_found = {}


def dll_for(csproj, mod_root):
    if not csproj or not mod_root:
        return None
    key = (mod_root, csproj.assembly)
    if key not in _dll_found:
        found = None
        for dp, fns in walk(mod_root):
            if csproj.assembly + ".dll" in fns:
                found = os.path.join(dp, csproj.assembly + ".dll")
                break
        _dll_found[key] = found
    return _dll_found[key]


_dll_cache = {}


def dll_bytes(path):
    if path not in _dll_cache:
        try:
            _dll_cache[path] = open(path, "rb").read()
        except OSError:
            _dll_cache[path] = None
    return _dll_cache[path]


# ---- the check ------------------------------------------------------------------------------------------------------
def judged(name, idx):
    """Only judge names under one of OUR roots (or a bare RM_/RSW_/RUT_ name); skip vanilla/donor types."""
    if "." in name:
        return name.split(".")[0] in idx.roots
    return name.startswith(BARE_PREFIXES)


def all_defnames(src):
    names = set()
    for dp, fns in walk(src):
        for fn in fns:
            if fn.endswith(".xml"):
                try:
                    names.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", open(os.path.join(dp, fn), encoding="utf-8-sig", errors="replace").read()))
                except OSError:
                    pass
    return names


def lint(idx, mod=None, check_dll=True, src=SRC):
    defnames = all_defnames(src)
    graph = DepGraph(src)
    findings = []     # (severity, kind, xml_path, ref, context, detail)
    stats = {"xml": 0, "refs": 0, "judged": 0, "resolved": 0}
    probes = {}
    for dp, fns in walk(src):
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            full = os.path.join(dp, fn)
            if mod and ("/%s/" % mod) not in full.replace(os.sep, "/") + "/":
                continue
            stats["xml"] += 1
            xml_mod = find_mod_root(full)
            xml_pkg, xml_about = about_info(xml_mod) if xml_mod else (None, "")
            lf = graph.loadfolder_guards(xml_mod) if xml_mod else []
            lfg = frozenset().union(*[pk for d, pk in lf if os.path.normpath(full).startswith(d + os.sep)]) if lf else frozenset()
            for name, ctx, guards, weak in xml_refs_g(full):
                guards = guards | lfg
                stats["refs"] += 1
                if not judged(name, idx):
                    continue
                stats["judged"] += 1
                rel = os.path.relpath(full, REPO)
                if "." not in name:
                    cands = [f for f in idx.short.get(name, ())]
                    full_name = cands[0] if len(cands) == 1 else None
                    if len(cands) > 1:
                        findings.append(("WARN", "AMBIGUOUS", rel, name, ctx, "%d types share this bare name: %s" % (len(cands), ", ".join(sorted(cands)[:3]))))
                        continue
                else:
                    full_name = idx.resolve(name)
                if not full_name and "." not in name and name in defnames and not ctx.startswith("Class="):
                    continue  # a bare RM_ name under a *Class tag that is really a def reference (densityClass, viscosityClass)
                if not full_name:
                    findings.append(("FAIL", "UNRESOLVED", rel, name, ctx, "no such type in any .cs under src/"))
                    continue
                stats["resolved"] += 1
                decls = idx.decl[full_name]
                compiled_in = None
                for f, kind, mods in decls:
                    cp = idx.owning_csproj(f)
                    if cp:
                        compiled_in = (f, cp, kind, mods)
                        break
                if not compiled_in:
                    cands = idx.candidate_csprojs(decls[0][0])
                    where = os.path.relpath(cands[0].path, REPO) if cands else "no csproj above it"
                    findings.append(("FAIL", "NOT_COMPILED", rel, name, ctx, "declared in %s but %s does not compile it" % (os.path.relpath(decls[0][0], REPO), where)))
                    continue
                f, cp, kind, mods = compiled_in
                if ctx.startswith("Class=") or ctx.startswith("Class= ") :
                    if kind in ("interface", "enum") or "abstract" in mods or "static" in mods:
                        findings.append(("FAIL", "NOT_INSTANTIABLE", rel, name, ctx, "%s %s is %s" % (kind, full_name, "abstract/static" if kind == "class" else kind)))
                type_mod = find_mod_root(f)
                if check_dll:
                    dll = dll_for(cp, type_mod)
                    short = full_name.split("+")[-1].split(".")[-1].encode()
                    if dll is None:
                        findings.append(("INFO", "UNMEASURED_DLL", rel, name, ctx, "no %s.dll under %s" % (cp.assembly, os.path.relpath(type_mod or cp.dir, REPO))))
                    else:
                        data = dll_bytes(dll)
                        if dll not in probes:
                            probes[dll] = data is not None and cp.assembly.encode() in data
                        if not probes[dll]:
                            findings.append(("INFO", "UNMEASURED_DLL", rel, name, ctx, "%s failed its sanity probe (its own assembly name is not in it)" % os.path.relpath(dll, REPO)))
                        elif short not in data:
                            findings.append(("FAIL", "NOT_IN_DLL", rel, name, ctx, "%s has no type named %s (source ahead of the build?)" % (os.path.relpath(dll, REPO), short.decode())))
                if type_mod and xml_mod and os.path.realpath(type_mod) != os.path.realpath(xml_mod):
                    type_pkg, _ = about_info(type_mod)
                    if type_pkg and xml_pkg:
                        cls, why = classify_dependency(graph, xml_pkg, xml_mod, type_pkg, type_mod, guards, weak, ctx)
                        if cls == "REAL":
                            findings.append(("WARN", "NO_DEPENDENCY", rel, name, ctx, "type is in %s but this mod's About.xml has no hard dependency chain to it" % type_pkg))
                        else:
                            findings.append(("INFO", cls, rel, name, ctx, "type is in %s; %s" % (type_pkg, why)))
                        rt, ot = _tier(xml_pkg), _tier(type_pkg)
                        if rt is not None and ot is not None and rt < ot:
                            findings.append(("WARN", "DIRECTION", rel, name, ctx, "type is in %s (tier %s) but referrer %s is tier %s: a lower tier may not need a higher one" % (type_pkg, "RM RSW RUT".split()[ot], xml_pkg, "RM RSW RUT".split()[rt])))
    return findings, stats


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod")
    ap.add_argument("--no-dll", action="store_true")
    ap.add_argument("-q", action="store_true", help="only the summary and FAIL lines")
    ap.add_argument("-v", action="store_true", help="also list every classified (non-REAL) cross-mod reference: GUARDED_*/INTRA_COMPOSITION pairs")
    a = ap.parse_args(argv)
    idx = Index()
    findings, stats = lint(idx, a.mod, not a.no_dll)
    print("indexed %d .cs, %d types, %d csprojs, roots %s; scanned %d xml, %d refs, %d judged, %d resolved"
          % (len(idx.cs_files), len(idx.decl), len(idx.csprojs), sorted(idx.roots), stats["xml"], stats["refs"], stats["judged"], stats["resolved"]))
    counts = defaultdict(int)
    for f in findings:
        counts[f] += 1
    uniq = sorted(counts)
    by = defaultdict(int)
    for sev, kind, *_ in uniq:
        by[(sev, kind)] += 1
    deps = defaultdict(list)
    cls_pairs = defaultdict(int)
    for f in uniq:
        sev, kind, rel, name, ctx, detail = f
        if kind == "NO_DEPENDENCY":
            deps[(find_mod_name(rel), detail.split()[3])].append(f)
            continue
        if kind == "DIRECTION":
            print("WARN DIRECTION %s: %s (%s) - %s" % (rel, name, ctx, detail))
            continue
        if kind in CLASSES:
            cls_pairs[(kind, find_mod_name(rel), detail.split()[3].rstrip(";"))] += 1
            continue
        if a.q and sev != "FAIL":
            continue
        print("%s %s %s: %s (%s) - %s%s" % (sev, kind, rel, name, ctx, detail, " [x%d]" % counts[f] if counts[f] > 1 else ""))
    for (xm, tm), fl in sorted(deps.items(), key=lambda kv: -len(kv[1])):
        if a.q:
            break
        sev, kind, rel, name, ctx, detail = fl[0]
        print("WARN NO_DEPENDENCY %s uses %s without naming it in About.xml: %d refs, e.g. %s in %s" % (xm, tm, len(fl), name, rel))
    graph = DepGraph()
    declared = [(p_, d_) for p_, ds in sorted(graph.raw_deps.items()) for d_ in ds
                if _tier(p_) is not None and _tier(d_) is not None and _tier(p_) < _tier(d_)]
    for p_, d_ in declared:
        print("WARN DIRECTION declared: %s (tier %s) hard-depends on %s (tier %s)" % (p_, "RM RSW RUT".split()[_tier(p_)], d_, "RM RSW RUT".split()[_tier(d_)]))
    if a.v:
        for (k, xm, tm), n in sorted(cls_pairs.items()):
            print("INFO %s %s -> %s: %d refs" % (k, xm, tm, n))
    cls_tot = defaultdict(int)
    cls_prs = defaultdict(set)
    for (k, xm, tm), n in cls_pairs.items():
        cls_tot[k] += n
        cls_prs[k].add((xm, tm))
    print("classes (distinct refs / mod pairs): " + ", ".join("%s %d/%d" % (k, cls_tot[k], len(cls_prs[k])) for k in CLASSES) + ", REAL(NO_DEPENDENCY) %d/%d" % (sum(len(v) for v in deps.values()), len(deps)))
    print("summary: " + (", ".join("%s %s x%d" % (s_, k, n) for (s_, k), n in sorted(by.items())) or "no findings") + " (distinct refs; NO_DEPENDENCY pairs: %d)" % len(deps))
    if stats["judged"] == 0:
        print("UNMEASURED: nothing judged - a lint that checked nothing is not a pass")
        return 2
    return 1 if any(s == "FAIL" for s, *_ in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
