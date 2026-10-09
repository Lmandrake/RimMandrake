#!/usr/bin/env python3
"""lint_harmony_targets.py - every Harmony patch target our mods name must resolve, offline, before a game load.

WHY (HARMONY_PATCH_RESILIENCE_1 / X-5). A game or donor-mod update that renames or re-signs one method makes Harmony
throw at startup. With one PatchAll per mod that kills every patch after it; with the per-class applier
(src/RimMandrake/_Shared/HarmonyResilience/PatchApplier.cs) it kills one feature. Either way the break is only seen in a
game load. This reads the metadata of the installed game DLLs and of our own committed mod DLLs (dnfile, no game run)
and checks every target our C# names.

WHAT IT READS, per .cs under src/**/Source (obj/, bin/, SelfTest/ skipped):
  attr     [HarmonyPatch(typeof(T), nameof(T.M) | "M", MethodType.X, new[] { typeof(A), ... })] on a class; a class
           whose class-level attribute names only the type takes the method from a method-level [HarmonyPatch("M")].
  dynamic  a [HarmonyPatch] class with TargetMethod()/TargetMethods(): its target is computed at runtime. Listed, never
           judged (DYNAMIC).
  reflect  AccessTools.Method / PropertyGetter / PropertySetter / Field (typeof(T), "M") and FieldRefAccess<T, F>("f"):
           the reflection hooks patches lean on, which break the same way.

VERDICTS
  OK              the type is found and has the member (walking base types); for attr with an explicit argument list,
                  some overload has that many parameters.
  MISSING_MEMBER  the type is found, the member is not (renamed, removed, wrong getter/setter).            FAILS the run
  ARITY           the member exists but no overload takes the listed number of parameters.               FAILS the run
  MISSING_TYPE    the type is in no indexed assembly and the file uses no namespace foreign to them.      FAILS the run
  UNRESOLVED      the type is in no indexed assembly, but the file imports a namespace none of them define (a donor
                  mod's): UNMEASURED here, never a pass.
  DYNAMIC         see above.
  NO_FEATURE      (mods that apply Harmony through RimMandrake.Shared.PatchApplier only) a [HarmonyPatch] class
                  without [PatchFeature(...)]: a failure would be reported by class name and switch nothing off.  FAILS
  BAD_FEATURE     a [PatchFeature] naming a settings field that is not a `public static bool` in the mod's source.  FAILS
Overloads are matched by parameter COUNT only (not types). A finding is evidence about FILES, never about the running
game.

INDEXED ASSEMBLIES: the game's Managed/Assembly-CSharp.dll, Assembly-CSharp-firstpass.dll and UnityEngine.CoreModule.dll,
plus every src/**/Assemblies/*.dll (our own, so patches on our own classes resolve). Parsed indexes are cached in
~/.cache/rimmandrake/harmony_lint keyed on path+size+mtime (Assembly-CSharp takes ~12 s to parse over /mnt/c).

USAGE
    python3 src/RimMandrake/Utils/lint_harmony_targets.py [--mod FlowWorks] [--root DIR] [-v]
Exit 0 = no MISSING_MEMBER / ARITY / MISSING_TYPE. The last line is the census:
    HARMONY-LINT targets N | ok K | missing M | arity A | missing-type T | unresolved U | dynamic D | feature-findings F
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GAME_MANAGED = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed"
GAME_DLLS = ("Assembly-CSharp.dll", "Assembly-CSharp-firstpass.dll", "UnityEngine.CoreModule.dll")
CACHE = os.path.expanduser("~/.cache/rimmandrake/harmony_lint")

FAILING = ("MISSING_MEMBER", "ARITY", "MISSING_TYPE", "NO_FEATURE", "BAD_FEATURE")

# ───────────────────────────────────────────────────────────── assembly index ──


def _compressed(b, i):
    x = b[i]
    if x < 0x80:
        return x, i + 1
    if (x & 0xC0) == 0x80:
        return ((x & 0x3F) << 8) | b[i + 1], i + 2
    return ((x & 0x1F) << 24) | (b[i + 1] << 16) | (b[i + 2] << 8) | b[i + 3], i + 4


def _param_count(sig):
    try:
        b = bytes(sig)
        i = 1
        if b[0] & 0x10:                       # GENERIC: a generic-parameter count precedes the parameter count
            _, i = _compressed(b, i)
        n, _ = _compressed(b, i)
        return n
    except Exception:                         # noqa: BLE001 -- an unreadable signature matches any arity
        return -1


def index_dll(path):
    """{fullName: {"ns", "name", "base": fullName|None, "methods": {name: [paramCounts]}, "fields": [names]}}."""
    import dnfile                              # imported here so the parsing half is testable without it
    pe = dnfile.dnPE(path)
    md = pe.net.mdtables
    rows = md.TypeDef.rows if md.TypeDef else []
    enclosing = {}
    if md.NestedClass:
        for n in md.NestedClass.rows:
            enclosing[n.NestedClass.row_index] = n.EnclosingClass.row_index

    def full(ri, seen=0):
        r = rows[ri - 1]
        if ri in enclosing and seen < 8:
            return full(enclosing[ri], seen + 1) + "+" + str(r.TypeName)
        ns = str(r.TypeNamespace or "")
        return (ns + "." if ns else "") + str(r.TypeName)

    out = {}
    for ri, r in enumerate(rows, 1):
        base = None
        ext = r.Extends
        try:
            br = ext.row if ext is not None else None
        except Exception:                     # noqa: BLE001
            br = None
        if br is not None and type(br).__name__ in ("TypeRefRow", "TypeDefRow"):
            ns = str(getattr(br, "TypeNamespace", "") or "")
            base = (ns + "." if ns else "") + str(br.TypeName)
        methods = {}
        for m in (r.MethodList or []):
            mr = m.row
            methods.setdefault(str(mr.Name), []).append(_param_count(mr.Signature.value))
        fields = [str(f.row.Name) for f in (r.FieldList or [])]
        out[full(ri)] = {"ns": str(r.TypeNamespace or ""), "name": str(r.TypeName), "base": base,
                         "methods": methods, "fields": fields}
    return out


def load_index(paths, verbose=False):
    """Merge the per-DLL indexes (cached) into one {fullName: entry} plus a {simpleName: [fullName]} map."""
    os.makedirs(CACHE, exist_ok=True)
    types, missing = {}, []
    for p in paths:
        try:
            st = os.stat(p)
        except OSError:
            missing.append(p)
            continue
        key = re.sub(r"[^A-Za-z0-9]+", "_", p)[-120:] + "_%d_%d.json" % (st.st_size, int(st.st_mtime))
        cp = os.path.join(CACHE, key)
        idx = None
        if os.path.exists(cp):
            try:
                idx = json.load(open(cp, encoding="utf-8"))
            except ValueError:
                idx = None
        if idx is None:
            if verbose:
                print("  parsing %s" % p, file=sys.stderr)
            idx = index_dll(p)
            with open(cp, "w", encoding="utf-8") as f:
                json.dump(idx, f)
        for k, v in idx.items():
            types.setdefault(k, v)
    by_simple = {}
    for k, v in types.items():
        by_simple.setdefault(v["name"], []).append(k)
        if "+" in k:                           # a nested type is also findable by its outer-qualified C# name
            by_simple.setdefault(k.rsplit(".", 1)[-1].replace("+", "."), []).append(k)
    return {"types": types, "by_simple": by_simple, "namespaces": {v["ns"] for v in types.values()},
            "missing": missing}


def default_dlls(root):
    out = [os.path.join(GAME_MANAGED, d) for d in GAME_DLLS]
    out += sorted(glob.glob(os.path.join(root, "src", "**", "Assemblies", "*.dll"), recursive=True))
    return out


def has_member(index, type_full, kind, name, arity=None):
    """('OK'|'MISSING_MEMBER'|'ARITY', detail). kind: method|getter|setter|ctor|field. Walks the base chain."""
    types = index["types"]
    seen = 0
    t = type_full
    counts = []
    while t and t in types and seen < 32:
        e = types[t]
        if kind == "field":
            if name in e["fields"]:
                return "OK", t
        else:
            mname = {"getter": "get_" + name, "setter": "set_" + name, "ctor": ".ctor"}.get(kind, name)
            if mname in e["methods"]:
                cs = e["methods"][mname]
                counts += cs
                if arity is None or arity in cs or -1 in cs:
                    return "OK", t
                if kind == "ctor":            # constructors are not inherited
                    break
        t = e["base"]
        seen += 1
    if counts:
        return "ARITY", "overloads take %s parameter(s), not %d" % (sorted(set(counts)), arity)
    return "MISSING_MEMBER", "no %s %r on %s or its bases" % (kind, name, type_full)


# ─────────────────────────────────────────────────────────────── source parse ──

_TYPEOF = re.compile(r"typeof\(\s*([A-Za-z_][\w.]*)(?:\s*<[^()]*>)?\s*\)")
_NAMEOF = re.compile(r"nameof\(\s*([\w.]+)\s*\)")
_STRING = re.compile(r'"([^"\\]*)"')
_MTYPE = re.compile(r"MethodType\.(\w+)")
_ARRAY = re.compile(r"new\s*(?:Type)?\s*\[\s*\]\s*\{([^{}]*)\}")
_CLASS = re.compile(r"\b(?:class|struct)\s+(\w+)")
_REFLECT = re.compile(r"AccessTools\.(Method|PropertyGetter|PropertySetter|Field|DeclaredMethod)\(\s*typeof\(\s*"
                      r"([A-Za-z_][\w.]*)(?:\s*<[^()]*>)?\s*\)\s*,\s*(?:\"([^\"]+)\"|nameof\(\s*([\w.]+)\s*\))")
_FIELDREF = re.compile(r"FieldRefAccess<\s*([A-Za-z_][\w.]*)\s*,[^>]*>\s*\(\s*\"([^\"]+)\"")
_USING = re.compile(r"^\s*using\s+([A-Za-z_][\w.]*)\s*;", re.M)


def strip_comments(text):
    """C# text with // and /* */ comments blanked (newlines kept, so line numbers hold); strings are left alone, so a
    "//" inside a literal is not a comment. A [HarmonyPatch] mentioned in a doc comment is then never read as code."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"' or (c == '@' and i + 1 < n and text[i + 1] == '"'):
            verb = c == '@'
            j = i + (2 if verb else 1)
            while j < n:
                if verb and text[j] == '"' and j + 1 < n and text[j + 1] == '"':
                    j += 2
                    continue
                if not verb and text[j] == '\\':
                    j += 2
                    continue
                if text[j] == '"' or (not verb and text[j] == "\n"):
                    break
                j += 1
            out.append(text[i:j + 1])
            i = j + 1
        elif c == "'" and i + 2 < n:
            j = i + 1
            while j < n and text[j] != "'" and text[j] != "\n":
                j += 2 if text[j] == '\\' else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in text[i:j]))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _attr_spans(text, start_tok="[HarmonyPatch"):
    """(start, end, inner) for each [HarmonyPatch...] attribute, bracket-balanced (may span lines)."""
    out = []
    i = 0
    while True:
        i = text.find(start_tok, i)
        if i < 0:
            return out
        j = i + len(start_tok)
        if j < len(text) and (text[j].isalnum() or text[j] == "_"):   # HarmonyPatchAll etc.
            i = j
            continue
        depth, k = 0, i
        while k < len(text):
            if text[k] == "[":
                depth += 1
            elif text[k] == "]":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        inner = text[j:k].strip()
        if inner.startswith("("):
            inner = inner[1:-1] if inner.endswith(")") else inner[1:]
        else:
            inner = ""
        out.append((i, k + 1, inner))
        i = k + 1


def parse_attr(inner):
    """{"type", "member", "mtype", "arity"} from one attribute's argument text (any field may be None)."""
    arr = _ARRAY.search(inner)
    arity = None
    rest = inner
    if arr:
        arity = len(_TYPEOF.findall(arr.group(1)))
        rest = inner[:arr.start()] + inner[arr.end():]
    tm = _TYPEOF.search(rest)
    nm = _NAMEOF.search(rest)
    sm = _STRING.search(rest)
    mt = _MTYPE.search(rest)
    member = None
    if nm:
        member = nm.group(1).split(".")[-1]
    elif sm:
        member = sm.group(1)
    return {"type": tm.group(1) if tm else None, "member": member, "mtype": mt.group(1) if mt else None,
            "arity": arity}


def _class_body(text, pos):
    """The {...} body of the first class declared at or after pos, and the class name."""
    m = _CLASS.search(text, pos)
    if not m:
        return None, "", len(text)
    b = text.find("{", m.end())
    if b < 0:
        return m.group(1), "", len(text)
    depth, k = 0, b
    while k < len(text):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    return m.group(1), text[b:k + 1], k + 1


def scan_text(text, path="<text>"):
    """Every target named in one C# file: [{"kind", "cls", "type", "member", "mtype", "arity", "where"}]."""
    targets = []
    consumed = set()
    for s, e, inner in _attr_spans(text):
        if s in consumed:
            continue
        # class-level attributes: those immediately followed (after other attributes/whitespace/comments) by a class
        tail = text[e:e + 400]
        stripped = re.sub(r"^(\s|\[[^\]]*\]|//[^\n]*\n)*", "", tail)
        if not re.match(r"(public|internal|private|protected|static|sealed|partial|\s)*(class|struct)\b", stripped):
            continue
        # merge every stacked class-level attribute
        group = [parse_attr(inner)]
        consumed.add(s)
        for s2, e2, inner2 in _attr_spans(text[e:e + 400]):
            if re.match(r"^\s*$", text[e:e + s2]) or re.match(r"^(\s|\[[^\]]*\])*$", text[e:e + s2]):
                group.append(parse_attr(inner2))
                consumed.add(e + s2)
        cls, body, _ = _class_body(text, e)
        merged = {"type": None, "member": None, "mtype": None, "arity": None}
        for g in group:
            for k, v in g.items():
                if merged[k] is None and v is not None:
                    merged[k] = v
        line = text.count("\n", 0, s) + 1
        where = "%s:%d" % (path, line)
        if re.search(r"\b(TargetMethods?|HarmonyTargetMethods?)\b", body):
            targets.append(dict(merged, kind="dynamic", cls=cls, where=where))
            continue
        if merged["type"] and merged["member"] is None and merged["mtype"] not in ("Constructor", "StaticConstructor"):
            # method-level [HarmonyPatch("M")] inside the class supply the member
            inner_attrs = [parse_attr(i3) for _, _, i3 in _attr_spans(body)]
            members = [a for a in inner_attrs if a["member"] or a["mtype"]]
            for a in members or [{}]:
                t = dict(merged)
                for k, v in a.items():
                    if t.get(k) is None and v is not None:
                        t[k] = v
                targets.append(dict(t, kind="attr", cls=cls, where=where))
            continue
        targets.append(dict(merged, kind="attr", cls=cls, where=where))
    for m in _REFLECT.finditer(text):
        verb, typ, s_name, n_name = m.groups()
        kind = {"PropertyGetter": "getter", "PropertySetter": "setter", "Field": "field"}.get(verb, "method")
        targets.append({"kind": "reflect", "cls": None, "type": typ, "member": s_name or n_name.split(".")[-1],
                        "mtype": kind, "arity": None, "where": "%s:%d" % (path, text.count("\n", 0, m.start()) + 1)})
    for m in _FIELDREF.finditer(text):
        targets.append({"kind": "reflect", "cls": None, "type": m.group(1), "member": m.group(2), "mtype": "field",
                        "arity": None, "where": "%s:%d" % (path, text.count("\n", 0, m.start()) + 1)})
    return targets


def resolve_type(index, name, usings):
    """Full names a C# type reference can mean, best first (namespace from the file's usings)."""
    types, simple = index["types"], index["by_simple"]
    if name in types:
        return [name]
    last = name.split(".")[-1]
    cands = simple.get(last, []) + (simple.get(name, []) if "." in name else [])
    if not cands:
        return []
    pref = [c for c in cands if types[c]["ns"] in usings or c.rsplit(".", 1)[0] in usings]
    return pref + [c for c in cands if c not in pref]


def judge(index, t, usings):
    if t["kind"] == "dynamic":
        return "DYNAMIC", "target computed at runtime (TargetMethod)"
    if not t.get("type"):
        return "DYNAMIC", "no typeof() in the attribute"
    cands = resolve_type(index, t["type"], usings)
    if not cands:
        foreign = [u for u in usings if u not in index["namespaces"]
                   and not u.startswith(("System", "HarmonyLib", "UnityEngine", "Unity", "Mono", "RimMandrake"))]
        if foreign:
            return "UNRESOLVED", "type %s not in any indexed assembly; file imports %s" % (t["type"], foreign[:3])
        return "MISSING_TYPE", "type %s is in no indexed assembly" % t["type"]
    mt = (t.get("mtype") or "").lower()
    kind = {"getter": "getter", "setter": "setter", "constructor": "ctor", "field": "field",
            "method": "method", "normal": "method", "": "method"}.get(mt, "method")
    if kind == "method" and t.get("member") is None:
        return "DYNAMIC", "type only, no member in the attribute"
    best = None
    for c in cands:
        v, d = has_member(index, c, kind, t.get("member") or "", t.get("arity") if t["kind"] == "attr" else None)
        if v == "OK":
            return "OK", c
        if best is None or (best[0] == "MISSING_MEMBER" and v == "ARITY"):
            best = (v, d)
    return best


_FEATURE = re.compile(r"\[(?:RimMandrake\.Shared\.)?PatchFeature\(\s*\"([^\"]*)\"(?:\s*,\s*typeof\(\s*([\w.]+)\s*\)"
                      r"\s*,\s*\"(\w+)\")?\s*\)\]")
_BOOLS = re.compile(r"public\s+static\s+bool\s+(\w+)\s*=")


def _preceding_attrs(text, pos):
    """The attribute list written directly before pos (only whitespace and whole [..] attributes between)."""
    i = pos
    while True:
        j = i
        while j > 0 and text[j - 1].isspace():
            j -= 1
        if j == 0 or text[j - 1] != "]":
            return text[i:pos]
        depth, k = 0, j - 1
        while k >= 0:
            if text[k] == "]":
                depth += 1
            elif text[k] == "[":
                depth -= 1
                if depth == 0:
                    break
            k -= 1
        if k < 0:
            return text[i:pos]
        i = k


def feature_findings(texts):
    """[(verdict, where, detail)] for one mod's {path: text} when it applies Harmony through PatchApplier: every
    class-level [HarmonyPatch] class must carry [PatchFeature], and every field it names must be a public static bool."""
    if not any("PatchApplier.Apply(" in t for t in texts.values()):
        return []
    bools = set()
    for t in texts.values():
        bools.update(_BOOLS.findall(t))
    out = []
    for path, text in sorted(texts.items()):
        for s, e, _ in _attr_spans(text):
            tail = text[e:e + 600]
            m = re.match(r"((?:\s|\[[^\]]*\]|//[^\n]*\n)*)(?:public|internal|static|sealed|partial|\s)*(?:class|struct)\s+(\w+)",
                         tail)
            if not m:
                continue
            block = _preceding_attrs(text, s) + text[s:e] + m.group(1)
            fm = _FEATURE.search(block)
            where = "%s:%d" % (path, text.count("\n", 0, s) + 1)
            if not fm:
                out.append(("NO_FEATURE", where, "class %s has no [PatchFeature]" % m.group(2)))
            elif fm.group(3) and fm.group(3) not in bools:
                out.append(("BAD_FEATURE", where, "class %s names %s.%s, not a public static bool in this mod"
                            % (m.group(2), fm.group(2), fm.group(3))))
    # a stacked class gets one finding per attribute; keep the first per class
    seen, uniq = set(), []
    for v, w, d in out:
        if d not in seen:
            seen.add(d)
            uniq.append((v, w, d))
    return uniq


def source_files(root, mod=None):
    base = os.path.join(root, "src")
    for p in glob.glob(os.path.join(base, "**", "Source", "**", "*.cs"), recursive=True):
        rel = os.path.relpath(p, base)
        parts = rel.split(os.sep)
        if any(x in ("obj", "bin", "SelfTest") for x in parts):
            continue
        if mod and mod not in parts:
            continue
        yield p


def run(root, mod=None, index=None, verbose=False, out=sys.stdout):
    if index is None:
        index = load_index(default_dlls(root), verbose)
    rows = []
    for p in sorted(source_files(root, mod)):
        text = strip_comments(open(p, encoding="utf-8", errors="replace").read())
        if "HarmonyPatch" not in text and "AccessTools." not in text and "FieldRefAccess" not in text:
            continue
        usings = set(_USING.findall(text))
        rel = os.path.relpath(p, root)
        for t in scan_text(text, rel):
            v, d = judge(index, t, usings)
            rows.append((v, t, d))
    by_mod = {}
    for p in source_files(root, mod):
        rel = os.path.relpath(p, os.path.join(root, "src")).split(os.sep)
        key = os.sep.join(rel[:rel.index("Source")]) if "Source" in rel else rel[0]
        by_mod.setdefault(key, {})[os.path.relpath(p, root)] = strip_comments(
            open(p, encoding="utf-8", errors="replace").read())
    for key, texts in sorted(by_mod.items()):
        for v, w, d in feature_findings(texts):
            rows.append((v, {"where": w, "kind": "feature", "type": key, "member": None}, d))
    counts = {}
    for v, t, d in rows:
        counts[v] = counts.get(v, 0) + 1
        if v in FAILING or v == "UNRESOLVED" or verbose:
            print("%-14s %s %s %s.%s%s  %s" % (v, t["where"], t["kind"], t.get("type"), t.get("member"),
                                              "" if t.get("arity") is None else "/%d" % t["arity"], d), file=out)
    if index.get("missing"):
        print("UNMEASURED     indexed assembly not found: %s" % index["missing"][:3], file=out)
    feats = counts.get("NO_FEATURE", 0) + counts.get("BAD_FEATURE", 0)
    print("HARMONY-LINT targets %d | ok %d | missing %d | arity %d | missing-type %d | unresolved %d | dynamic %d"
          " | feature-findings %d"
          % (len(rows) - feats, counts.get("OK", 0), counts.get("MISSING_MEMBER", 0), counts.get("ARITY", 0),
             counts.get("MISSING_TYPE", 0), counts.get("UNRESOLVED", 0), counts.get("DYNAMIC", 0), feats), file=out)
    bad = sum(counts.get(k, 0) for k in FAILING)
    return rows, (1 if bad or any(os.path.basename(m) in GAME_DLLS for m in index.get("missing", [])) else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod", help="only src/**/<mod>/Source")
    ap.add_argument("--root", default=REPO)
    ap.add_argument("-v", action="store_true", help="print every target, not only findings")
    a = ap.parse_args(argv)
    _, code = run(a.root, a.mod, verbose=a.v)
    return code


if __name__ == "__main__":
    sys.exit(main())
