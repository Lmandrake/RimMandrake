#!/usr/bin/env python3
"""Offline lint of LoreStages (mandrake.rm.lorestages), no game, no build. The mod ships no defs of its own: it is the engine behind
RM_LoreStageTableDef ladders that OTHER mods ship, so the lint walks every ladder under src/ and checks what the engine would only say with a
one-time log line at runtime (or never):

  ls-fields      every element of a table / target / rung is a field of its class; stage and maxStage parse as integers
  ls-rules       the ConfigErrors rules, restated in python: >= 1 target, every target has defType/defName/field and >= 1 rung, no duplicate
                 stage, none negative, none above a positive maxStage, every rung has non-empty text
  ls-target      a target whose defName carries one of our prefixes (RM_/RUT_/RSW_) names a def that exists under src/; its field is a public
                 string field of the engine class named by defType (a typo is "skipped" with one warning, i.e. a ladder that never shows)
  ls-collision   two targets addressing the same (defType, defName, field) across ladders: when both have an applicable rung the later table
                 wins (load order), so the author must know (WARN)
  ls-ladder      table defNames are unique, ladderIds are unique unless deliberately shared (WARN), a ladderId is not blank-and-defName-clashing
  ls-r25         owner ruling R25: no ladder text may name the Assailants or the Rakata (the truth arrives as quest text, never a def description)
  ls-placeholder shipped text carrying a [[PLACEHOLDER marker (WARN: known unfinished rungs, listed so they cannot ship by accident)
  ls-kernel      the kernel is Verse-free, listed in the mod csproj and the SelfTest csproj, and called by the applier / table def / game component

    python3 src/RimMandrake/Utils/lint_lorestages_defs.py [--quiet]
Exit 1 on any ERROR, 2 if UNMEASURED (found no ladder, i.e. the walk is blind).
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
ENGINE = os.environ.get("RIMWORLD_DECOMPILED", "/mnt/d/Luke/dev/reference/rimworld-decompiled")
MOD = "RimMandrake/LoreStages"
TABLE_TAG = "RimMandrake.LoreStages.RM_LoreStageTableDef"
OUR_PREFIXES = ("RM_", "RUT_", "RSW_")
SKIP = {"bin", "obj", "__pycache__", "Textures", "Assemblies", "Sounds", "Languages"}
FORBIDDEN_R25 = ("Rakata", "Assailant")
ENGINE_DIRS = ("RimWorld", "Verse")


def collect(src=SRC):
    inp = {"xml": {}, "defnames": set(), "cs": {}, "csproj": {}}
    for dp, dns, fns in os.walk(src):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, src).replace(os.sep, "/")
            if f.endswith(".xml") and f != "About.xml":
                t = open(p, encoding="utf-8-sig", errors="replace").read()
                for m in re.finditer(r"<defName>([^<]+)</defName>", t):
                    inp["defnames"].add(m.group(1).strip())
                if TABLE_TAG in t:
                    inp["xml"][rel] = t
            elif rel.startswith(MOD + "/Source/") and f.endswith(".cs") and "/SelfTest" not in rel:
                inp["cs"][rel] = open(p, encoding="utf-8-sig", errors="replace").read()
            elif rel.startswith(MOD + "/Source/") and f.endswith(".csproj"):
                inp["csproj"][rel] = open(p, encoding="utf-8-sig", errors="replace").read()
    return inp


def engine_string_fields(def_type):
    """public string fields declared on the engine class (and its Def base), or None if the decompiled tree is not reachable."""
    names = set()
    found = False
    for cls in (def_type, "Def"):
        for d in ENGINE_DIRS:
            p = os.path.join(ENGINE, d, cls + ".cs")
            if os.path.isfile(p):
                found = True
                t = open(p, encoding="utf-8-sig", errors="replace").read()
                names |= set(re.findall(r"public\s+string\s+(\w+)\s*(?:=[^;]*)?;", t))
    return names if found else None


TABLE_FIELDS = {"defName", "ladderId", "maxStage", "targets", "label", "description"}
TARGET_FIELDS = {"defType", "defName", "field", "stages"}
RUNG_FIELDS = {"stage", "text"}


def check(inp, engine=True):
    errs, warns = [], []
    E = lambda k, p, m: errs.append("ERROR ls-%s: %s: %s" % (k, p, m))
    W = lambda k, p, m: warns.append("WARN  ls-%s: %s: %s" % (k, p, m))
    counts = {"tables": 0, "targets": 0, "rungs": 0, "engine fields checked": 0}
    table_names, ladders, addr = {}, {}, {}
    cache = {}
    for rel, text in sorted(inp["xml"].items()):
        try:
            root = ET.fromstring(text.encode("utf-8"))
        except ET.ParseError as e:
            E("fields", rel, "XML does not parse: %s" % e)
            continue
        for t in root.iter(TABLE_TAG):
            counts["tables"] += 1
            name = t.findtext("defName") or "?"
            for ch in t:
                if ch.tag not in TABLE_FIELDS:
                    E("fields", rel, "%s: <%s> is not a field of RM_LoreStageTableDef (an unknown child discards the def)" % (name, ch.tag))
            if name in table_names:
                E("ladder", rel, "table defName %s also defined in %s" % (name, table_names[name]))
            table_names[name] = rel
            lid = (t.findtext("ladderId") or "").strip() or name
            ladders.setdefault(lid, []).append(name)
            try:
                mx = int((t.findtext("maxStage") or "0").strip())
            except ValueError:
                E("fields", rel, "%s: maxStage %r is not an integer" % (name, t.findtext("maxStage")))
                mx = 0
            targets = t.find("targets")
            tl = list(targets) if targets is not None else []
            if not tl:
                E("rules", rel, "%s has no targets: it loads, applies nothing and looks like it works" % name)
            for ti, tg in enumerate(tl):
                counts["targets"] += 1
                for ch in tg:
                    if ch.tag not in TARGET_FIELDS:
                        E("fields", rel, "%s target %d: <%s> is not a field of LoreStageTarget" % (name, ti, ch.tag))
                dt, dn, fld = (tg.findtext("defType") or "").strip(), (tg.findtext("defName") or "").strip(), (tg.findtext("field") or "description").strip()
                if tg.find("field") is not None and not (tg.findtext("field") or "").strip():
                    E("rules", rel, "%s target %d: empty <field>" % (name, ti))
                if not dt:
                    E("rules", rel, "%s target %d: no defType" % (name, ti))
                if not dn:
                    E("rules", rel, "%s target %d: no defName" % (name, ti))
                if dn.startswith(OUR_PREFIXES) and dn not in inp["defnames"]:
                    E("target", rel, "%s target %d: %s %s is not defined anywhere under src/ (the rung would never show)" % (name, ti, dt, dn))
                if engine and dt:
                    if dt not in cache:
                        cache[dt] = engine_string_fields(dt)
                    fields = cache[dt]
                    if fields is not None:
                        counts["engine fields checked"] += 1
                        if fld not in fields:
                            E("target", rel, "%s target %d: %s has no public string field %r in the engine (skipped at runtime with one warning)" % (name, ti, dt, fld))
                addr.setdefault((dt, dn, fld), []).append(name)
                rungs = tg.find("stages")
                rl = list(rungs) if rungs is not None else []
                if not rl:
                    E("rules", rel, "%s target %d (%s.%s): no stages: nothing would ever change" % (name, ti, dn, fld))
                seen = set()
                for ri, r in enumerate(rl):
                    counts["rungs"] += 1
                    for ch in r:
                        if ch.tag not in RUNG_FIELDS:
                            E("fields", rel, "%s target %d rung %d: <%s> is not a field of LoreStageText" % (name, ti, ri, ch.tag))
                    try:
                        st = int((r.findtext("stage") or "").strip())
                    except ValueError:
                        E("fields", rel, "%s target %d rung %d: stage %r is not an integer" % (name, ti, ri, r.findtext("stage")))
                        continue
                    if st in seen:
                        E("rules", rel, "%s target %d (%s.%s): duplicate stage %d: which one wins is load order" % (name, ti, dn, fld, st))
                    seen.add(st)
                    if st < 0:
                        E("rules", rel, "%s target %d (%s.%s): negative stage %d" % (name, ti, dn, fld, st))
                    if mx > 0 and st > mx:
                        E("rules", rel, "%s target %d (%s.%s): stage %d is above maxStage %d and can never be reached" % (name, ti, dn, fld, st, mx))
                    tx = r.findtext("text")
                    if tx is None or not tx.strip():
                        E("rules", rel, "%s target %d (%s.%s): stage %d has no text" % (name, ti, dn, fld, st))
                        continue
                    for bad in FORBIDDEN_R25:
                        if re.search(r"\b%s" % bad, tx):
                            E("r25", rel, "%s target %d (%s.%s) stage %d names %r: owner ruling R25 keeps that truth out of def descriptions" % (name, ti, dn, fld, st, bad))
                    if "[[PLACEHOLDER" in tx:
                        W("placeholder", rel, "%s %s.%s stage %d still carries a [[PLACEHOLDER marker" % (name, dn, fld, st))
    for a, names in addr.items():
        if len(names) > 1:
            W("collision", "%s.%s.%s" % a, "targeted by %d tables (%s): when two apply, the later table wins" % (len(names), ", ".join(names)))
    for lid, names in ladders.items():
        if len(names) > 1:
            W("ladder", lid, "ladder id shared by %s (they advance together)" % ", ".join(names))
    # kernel
    kern = next(((p, t) for p, t in inp["cs"].items() if p.endswith("Kernel/RM_LoreStageKernel.cs")), None)
    if kern is None:
        E("kernel", MOD, "Kernel/RM_LoreStageKernel.cs not found")
    else:
        body = re.sub(r"//[^\n]*", "", kern[1])
        for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
            if bad in body:
                E("kernel", kern[0], "contains '%s': the fuzz project compiles this file on plain code" % bad)
        for cp, t in inp["csproj"].items():
            if "SelfTest" in cp:
                continue
            if 'Include="Kernel\\RM_LoreStageKernel.cs"' not in t:
                E("kernel", cp, "the mod csproj does not compile Kernel\\RM_LoreStageKernel.cs (EnableDefaultCompileItems is false: it would build nothing)")
        for fn, owner in (("ChooseRung", "LoreStageApplier.cs"), ("RungProblems", "RM_LoreStageTableDef.cs"), ("LadderKey", "RM_LoreStageTableDef.cs"),
                          ("ClampStage", "GameComponent_LoreStage.cs"), ("EffectiveStage", "GameComponent_LoreStage.cs")):
            src_text = next((t for p, t in inp["cs"].items() if p.endswith("/" + owner)), "")
            if "RM_LoreStageKernel.%s(" % fn not in src_text:
                E("kernel", MOD, "%s no longer calls RM_LoreStageKernel.%s: the fuzz would be proving a copy" % (owner, fn))
    return errs, warns, counts


def main(argv):
    inp = collect()
    errs, warns, counts = check(inp)
    if counts["tables"] == 0 or counts["rungs"] < 5:
        print("LINT UNMEASURED: found %s - the walk is blind" % counts)
        return 2
    if "--quiet" not in argv:
        print("lorestages lint: %s, %d ERROR, %d WARN" % (", ".join("%s=%s" % kv for kv in sorted(counts.items())), len(errs), len(warns)))
        for w in warns:
            print(w)
    for e in errs:
        print(e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
