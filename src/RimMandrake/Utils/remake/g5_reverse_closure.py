#!/usr/bin/env python3
"""Gate G5 (runbook 06 §2): REVERSE closure of a creation profile (default PAINT) — which RETAINED mod still
names something only a REMOVED mod provides.

Removed set = the capture's mod set minus the profile. For each retained, non-Ludeon mod, five instruments:
  A  About.xml <modDependencies> (+ <modDependenciesByVersion><v1.6>) naming a removed packageId       -> HARD
  B  mod_facts.jsonl class_ref / hard_dep edges (2026-10-10 audit) to a removed packageId                 -> HARD
  C  Defs XML: a leaf whose whole text is a defName that only removed mods define                       -> REF
  D  Patches XML: a removed-only defName inside an <xpath> (defName="X", text()="X", ...) or a leaf value -> REF
  E  DLLs: a removed-only defName as a UTF-16 string literal (#US heap: GetNamed("X") style)             -> REF
C/D refs under MayRequire/MayRequireAnyOf naming a removed mod, a PatchOperationFindMod <match> branch naming a
removed mod, or a PatchOperationConditional whose <match> xpath / def-exists test names the def are GUARDED
(the guard test is wave3_prep.py's, the one corrected after Wave 2).

"Removed-only defName" = every package that defines it in the dump is removed and no Ludeon package defines it.

What a scan CANNOT see (printed in the output; never read silence as clean):
  * [DefOf] fields: the field NAME is the defName, stored UTF-8 among every other identifier — not attributable.
  * defNames built at runtime (string concatenation, interpolation), reflection on types of removed assemblies,
    Harmony patches targeting removed assemblies' methods by name (only B's class_ref edges cover that).
  * defs Cherry Picker removed before the dump was taken: absent from the dump, so not counted as provided.
  * third-party LoadFolders that point outside the scanned folders; old version folders (1.0-1.5) are skipped.
  * C/D use leaf-whole-text tokens of length >= 4; a reference split across text or attributes is not seen.

Usage: g5_reverse_closure.py [--profile XML] [--dump DIR] [--facts JSONL] [--json OUT] [--max-print N]
Exit 0 PASS (0 unguarded HARD/REF) · 1 FAIL · 2 UNMEASURED (instrument blind).
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

FACTS = os.path.join(common.REPO, "design/RimMandrake/mod_audit/facts/mod_facts.jsonl")
OLD_VER = re.compile(r"^1\.[0-5]$")
TOK = re.compile(r"^[A-Za-z_][A-Za-z0-9_\-]{3,}$")
XTOK = re.compile(r"[\"']([A-Za-z_][A-Za-z0-9_\-]{3,})[\"']")
U16 = re.compile(rb"(?:[A-Za-z0-9_\-]\x00){4,}")
SKIP_TAGS = {"defName", "role", "label", "description", "labelShort", "jobString", "text", "reportString"}


def about_deps(root):
    out = set()
    try:
        r = ET.parse(os.path.join(root, "About", "About.xml")).getroot()
    except Exception:
        return None
    for li in r.findall("modDependencies/li"):
        out.add((li.findtext("packageId") or "").strip().lower())
    for v in r.findall("modDependenciesByVersion"):
        for ver in v:
            if ver.tag == "v1.6":
                out |= {(li.findtext("packageId") or "").strip().lower() for li in ver.findall("li")}
    out.discard("")
    return out


def about_name(root):
    try:
        return (ET.parse(os.path.join(root, "About", "About.xml")).getroot().findtext("name") or "").strip().lower()
    except Exception:
        return ""


def xml_files(root, sub):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not OLD_VER.match(d) and d not in ("Languages", "About", "Textures", "Sounds", "Source")]
        if sub not in dp.replace("\\", "/").split("/"):
            continue
        for f in fn:
            if f.lower().endswith(".xml"):
                yield os.path.join(dp, f)


def inactive_folders(root, active):
    """Folders (abs) a LoadFolders.xml v1.6 entry would NOT load with `active` packageIds (IfModActive = any of,
    IfModActiveAll = all of, IfModNotActive = none of)."""
    out = []
    try:
        r = ET.parse(os.path.join(root, "LoadFolders.xml")).getroot()
    except Exception:
        return out
    for ver in r:
        if ver.tag not in ("v1.6", "default"):
            continue
        for li in ver.findall("li"):
            path = (li.text or "").strip().strip("/\\")
            if not path:
                continue
            ids = lambda k: [x.strip().lower() for x in (li.get(k) or "").split(",") if x.strip()]
            off = False
            if ids("IfModActive") and not any(x in active for x in ids("IfModActive")):
                off = True
            if ids("IfModActiveAll") and not all(x in active for x in ids("IfModActiveAll")):
                off = True
            if ids("IfModNotActive") and any(x in active for x in ids("IfModNotActive")):
                off = True
            if off:
                out.append(os.path.join(root, path.replace("\\", "/")) + "/")
    return out


def def_exists_test(xp, names):
    return any(re.search(r"defName\s*=\s*[\"']%s[\"']\s*\]\s*$" % re.escape(n), xp.strip()) for n in names)


def scan_xml(path, removed_names, removed_pkgs, removed_modnames):
    """[(kind, tag, names, guard|None)] for one XML file."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return [("PARSE_ERROR", "", [], None)]
    hits = []

    def walk(e, stack):
        stack = stack + [e]
        names = set()
        if len(e) == 0 and e.text and e.text.strip():
            t = e.text.strip()
            if e.tag == "xpath":
                names = set(XTOK.findall(t)) & removed_names
            elif (e.tag not in SKIP_TAGS and TOK.match(t) and t in removed_names
                  and not (len(stack) > 1 and stack[-2].tag in ("mods", "modsToCheck"))):  # a FindMod name list is the guard
                names = {t}
        if names:
            why = None
            for i, a in enumerate(stack):
                branch = stack[i + 1].tag if i + 1 < len(stack) else None
                c = a.get("Class") or ""
                if "FindMod" in c and branch == "match" and any(
                        (li.text or "").strip().lower() in removed_modnames for li in a.findall("mods/li")):
                    why = "FindMod"
                if "Conditional" in c:
                    xp = a.findtext("xpath") or ""
                    if branch == "match" and any(n in xp for n in names):
                        why = "Conditional-match"
                    elif def_exists_test(xp, names):
                        why = "Conditional-defexists"
                for at in ("MayRequire", "MayRequireAnyOf"):
                    if a.get(at) and set(re.split(r"[,\s]+", a.get(at).lower())) & removed_pkgs:
                        why = "MayRequire"
            hits.append(("xpath" if e.tag == "xpath" else "value", e.tag, sorted(names), why))
        for c in e:
            walk(c, stack)

    walk(root, [])
    return hits


def dll_literals(root):
    out = set()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not OLD_VER.match(d)]
        if os.path.basename(dp).lower() != "assemblies":
            continue
        for f in fn:
            if f.lower().endswith(".dll"):
                try:
                    b = open(os.path.join(dp, f), "rb").read()
                except OSError:
                    continue
                out |= {m.decode("utf-16le") for m in U16.findall(b)}
    return out


def strong(n):
    """A literal specific enough to be a def reference: has '_' or >= 3 capitals (Material, Trade are words)."""
    return "_" in n or sum(c.isupper() for c in n) >= 3


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", default=common.PAINT_DEFAULT)
    ap.add_argument("--dump", default=common.default_dump())
    ap.add_argument("--facts", default=FACTS)
    ap.add_argument("--json")
    ap.add_argument("--max-print", type=int, default=60)
    a = ap.parse_args(argv)
    profile = common.load_profile(a.profile)
    pset = set(profile)
    man, roots = common.load_capture(a.dump)
    removed = {p for p in roots if p not in pset and not common.is_core(p)}
    retained = [p for p in profile if not common.is_core(p)]
    owners = {}
    for f in common.iter_def_files(a.dump):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        for d in j.get("defs", []):
            owners.setdefault(d["defName"], set()).add((d.get("packageId") or "").lower())
    rnames = {n for n, ps in owners.items() if ps and ps <= removed and len(n) >= 4}
    # the dump attributes an overridden def to the LAST mod that defined it: a Core def a removed mod redefines
    # reads as removed-only. Anything Core or a retained mod defines in its own XML stays provided.
    kept_xml = set()
    defpat = re.compile(r"<defName>\s*([^<\s]+)\s*</defName>")
    for p in profile:
        r = roots.get(p)
        if r and os.path.isdir(r):
            for f in xml_files(r, "Defs"):
                try:
                    kept_xml |= set(defpat.findall(open(f, encoding="utf-8", errors="replace").read()))
                except OSError:
                    pass
    shadowed = rnames & kept_xml
    rnames -= kept_xml
    # sanity probe: the instrument must see a def it knows is provided by a retained mod and one by Core
    if "Human" not in owners or not any(ps & pset - {p for p in ps if common.is_core(p)} for ps in owners.values()):
        print("UNMEASURED sanity probe: dump does not show Core Human or any retained mod's defs")
        return 2
    rmodnames = {about_name(roots[p]) for p in removed if roots.get(p)} - {""}
    cr = {}
    if os.path.isfile(a.facts):
        for line in open(a.facts):
            j = json.loads(line)
            for d in j.get("dependants_detail") or []:
                if {"class_ref", "hard_dep", "hard_dep_v1.6"} & set(d.get("kinds") or []):
                    cr.setdefault(d["packageId"].lower(), set()).add(j["packageId"].lower())
    rows, blind = [], []
    for p in retained:
        r = roots.get(p)
        if not r or not os.path.isdir(r):
            blind.append(p)
            continue
        deps = about_deps(r)
        if deps is None:
            blind.append(p + " (About.xml unreadable)")
            deps = set()
        for q in sorted(deps & removed):
            rows.append({"mod": p, "inst": "A", "kind": "HARD", "ref": q, "file": "About/About.xml", "guard": None})
        for q in sorted(cr.get(p, set()) & removed):
            rows.append({"mod": p, "inst": "B", "kind": "HARD", "ref": q, "file": "mod_facts class_ref/hard_dep", "guard": None})
        off = inactive_folders(r, pset)
        for inst, sub in (("C", "Defs"), ("D", "Patches")):
            for f in xml_files(r, sub):
                if any(f.startswith(o) for o in off):
                    continue  # LoadFolders.xml does not load this folder on the profile
                for kind, tag, names, why in scan_xml(f, rnames, removed, rmodnames):
                    if kind == "PARSE_ERROR":
                        blind.append("%s %s (XML parse error)" % (p, os.path.relpath(f, r)))
                        continue
                    for n in names:
                        rows.append({"mod": p, "inst": inst, "kind": "REF", "ref": n, "tag": tag,
                                     "owner": sorted(owners[n]), "file": os.path.relpath(f, r), "guard": why})
        for n in sorted(dll_literals(r) & rnames):
            rows.append({"mod": p, "inst": "E", "kind": "REF" if strong(n) else "WEAK", "ref": n, "owner": sorted(owners[n]),
                         "file": "Assemblies (UTF-16 literal)", "guard": None})
    weak = [x for x in rows if x["kind"] == "WEAK"]
    bad = [x for x in rows if not x["guard"] and x["kind"] != "WEAK"]
    by = {}
    for x in bad:
        by.setdefault(x["mod"], []).append(x)
    print("profile %s: %d retained (non-Ludeon) · removed %d · removed-only defNames %d · capture %s" % (
        os.path.basename(a.profile), len(retained), len(removed), len(rnames), os.path.basename(a.dump.rstrip("/"))))
    shown = 0
    for m in sorted(by, key=lambda k: -len(by[k])):
        insts = {}
        for x in by[m]:
            insts[x["inst"]] = insts.get(x["inst"], 0) + 1
        print("  %-42s unguarded %4d  %s" % (m, len(by[m]), " ".join("%s=%d" % kv for kv in sorted(insts.items()))))
        for x in by[m][:6]:
            if shown < a.max_print:
                print("      %s %s %s <- %s  %s" % (x["inst"], x["kind"], x["ref"], ",".join(x.get("owner", [])) or "-", x["file"]))
                shown += 1
    print("guarded refs (ignored): %d · WEAK E literals (plain words, advisory): %d · removed-only names shadowed "
          "by a Core/retained <defName> (not counted): %d — all listed in --json" % (
              sum(1 for x in rows if x["guard"]), len(weak), len(shadowed)))
    if blind:
        print("BLIND (not scanned): " + "; ".join(blind))
    print("CANNOT SEE: [DefOf] field names, runtime-built defNames, Harmony targets by name beyond B, "
          "Cherry-Picker-cut defs, LoadFolders outside scanned dirs (see --help)")
    hard = sum(1 for x in bad if x["kind"] == "HARD")
    verdict = "FAIL" if bad else ("UNMEASURED" if blind else "PASS")
    print("G5 %s: unguarded HARD %d · unguarded REF %d (C=%d D=%d E=%d)" % (
        verdict, hard, len(bad) - hard, *(sum(1 for x in bad if x["inst"] == i) for i in "CDE")))
    if a.json:
        json.dump({"verdict": verdict, "removed": sorted(removed), "rows": rows, "blind": blind},
                  open(a.json, "w"), indent=1)
    return {"PASS": 0, "FAIL": 1, "UNMEASURED": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
