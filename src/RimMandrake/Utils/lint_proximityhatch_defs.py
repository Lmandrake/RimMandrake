#!/usr/bin/env python3
"""Offline lint of ProximityHatch (mandrake.rm.proximityhatch), no game, no build. The mod ships no defs of its own: it is a comp that OTHER
mods' eggs carry, so the lint walks every consumer under src/ and checks what the engine would only say by silently discarding the egg:

  ph-fields       every child of a <... Class="RimMandrake.ProximityHatch.CompProperties_ProximityHatch"> is a public field of that class,
                  parses, triggerRadius > 0 and scanIntervalTicks >= 1 (a zero interval is clamped to every tick; a zero radius to 0.1 cells)
  ph-hatcher      the egg carries a CompProperties_Hatcher (on the def, or on the def a PatchOperationAdd xpath names): without one the comp
                  stays dormant forever and the egg only ever hatches on the vanilla timer
  ph-once         one proximity comp per egg
  ph-gate         a consumer that is not this mod either wraps the type in MayRequire="mandrake.rm.proximityhatch" (a <li> in a def), sits inside
                  PatchOperationFindMod on this mod's display name, or the consumer mod depends on it: otherwise the unresolvable Class= discards the
                  whole file when this mod is off (MayRequire on an <Operation> is inert)
  ph-kernel       the kernel is Verse-free and listed in the mod csproj; the comp calls it
  ph-settings     each static default in RM_ProximityHatchSettings equals its Scribe default and sits inside its slider range

    python3 src/RimMandrake/Utils/lint_proximityhatch_defs.py [--quiet] [--src DIR]
Exit 1 on any ERROR, 2 if UNMEASURED (found no consumer, i.e. the walk is blind).
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
MOD = "RimMandrake/ProximityHatch"
CLS = "RimMandrake.ProximityHatch.CompProperties_ProximityHatch"
PACKAGE = "mandrake.rm.proximityhatch"
SKIP = {"bin", "obj", "__pycache__", "Textures", "Assemblies", "Sounds", "Languages"}


def collect(src=SRC):
    inp = {"xml": {}, "about": {}, "cs": {}, "csproj": {}}
    for dp, dns, fns in os.walk(src):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, src).replace(os.sep, "/")
            if f.endswith(".xml"):
                t = open(p, encoding="utf-8-sig", errors="replace").read()
                if f == "About.xml":
                    inp["about"][rel] = t
                elif "ProximityHatch" in t:
                    inp["xml"][rel] = t
            elif rel.startswith(MOD + "/Source/") and f.endswith(".cs"):
                inp["cs"][rel] = open(p, encoding="utf-8-sig", errors="replace").read()
            elif rel.startswith(MOD + "/Source/") and f.endswith(".csproj") and "SelfTest" not in rel:
                inp["csproj"][rel] = open(p, encoding="utf-8-sig", errors="replace").read()
    # every def anywhere that carries a Hatcher comp, by defName (a patch names its target by xpath)
    inp["hatcher_defs"] = set()
    for dp, dns, fns in os.walk(src):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            if f.endswith(".xml") and f != "About.xml":
                t = open(os.path.join(dp, f), encoding="utf-8-sig", errors="replace").read()
                if "CompProperties_Hatcher" in t:
                    inp["hatcher_defs"] |= hatcher_defnames(t)
    return inp


def hatcher_defnames(text):
    out = set()
    try:
        root = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError:
        return out
    for d in root.iter("ThingDef"):
        n = d.findtext("defName")
        comps = d.find("comps")
        if n and comps is not None and any(li.get("Class") == "CompProperties_Hatcher" for li in comps):
            out.add(n)
    return out


def mod_of(rel):
    parts = rel.split("/")
    return "/".join(parts[:2])


def public_fields(cs_text):
    return set(re.findall(r"public\s+(?:float|int|bool|string)\s+(\w+)\s*(?:=|;)", cs_text))


def parent_map(root):
    return {c: p for p in root.iter() for c in p}


def check(inp):
    errs, counts = [], {"consumers": 0, "fields": 0, "settings": 0}
    E = lambda k, p, m: errs.append("ERROR %s: %s: %s" % (k, p, m))
    props_cs = next((t for p, t in inp["cs"].items() if p.endswith("CompProperties_ProximityHatch.cs")), "")
    allowed = public_fields(props_cs) | {"compClass"}
    if not props_cs:
        E("ph-fields", MOD, "CompProperties_ProximityHatch.cs not found")
    deps = {}
    for p, t in inp["about"].items():
        deps[mod_of(p)] = t
    for rel, text in sorted(inp["xml"].items()):
        try:
            root = ET.fromstring(text.encode("utf-8"))
        except ET.ParseError as e:
            E("xml-parses", rel, str(e))
            continue
        pm = parent_map(root)
        nodes = [li for li in root.iter() if li.get("Class") == CLS]
        by_owner = {}
        for li in nodes:
            counts["consumers"] += 1
            comps = pm.get(li)
            # fields
            for ch in li:
                counts["fields"] += 1
                if ch.tag not in allowed:
                    E("ph-fields", rel, "<%s> is not a field of CompProperties_ProximityHatch (an unknown child discards the egg)" % ch.tag)
            try:
                tr = float(li.findtext("triggerRadius") or "4")
                if not tr > 0:
                    E("ph-fields", rel, "triggerRadius %s must be > 0" % tr)
                elif tr > 30:
                    E("ph-fields", rel, "triggerRadius %s cells is not an ambush any more" % tr)
            except ValueError:
                E("ph-fields", rel, "triggerRadius %r does not parse" % li.findtext("triggerRadius"))
            try:
                si = int(li.findtext("scanIntervalTicks") or "60")
                if si < 1:
                    E("ph-fields", rel, "scanIntervalTicks %d must be >= 1" % si)
            except ValueError:
                E("ph-fields", rel, "scanIntervalTicks %r does not parse" % li.findtext("scanIntervalTicks"))
            # owner: the def, or the def a PatchOperationAdd names
            owner, patched = None, False
            anc = comps
            while anc is not None and anc.tag not in ("ThingDef",):
                anc = pm.get(anc)
            if anc is not None and anc.tag == "ThingDef":
                owner = anc.findtext("defName") or anc.get("Name")
                sib = comps is not None and any(x.get("Class") == "CompProperties_Hatcher" for x in comps)
                if not sib:
                    E("ph-hatcher", rel, "%s carries a proximity comp but no CompProperties_Hatcher: the comp stays dormant" % owner)
            else:
                patched = True
                op = comps
                while op is not None and op.tag != "Operation":
                    op = pm.get(op)
                xp = op.findtext("xpath") if op is not None else None
                if xp is None:
                    # value sits under <match>; the Operation with the xpath is the match element itself
                    m = li
                    while m is not None and m.find("xpath") is None:
                        m = pm.get(m)
                    xp = m.findtext("xpath") if m is not None else None
                mm = re.search(r'defName="([^"]+)"', xp or "")
                owner = mm.group(1) if mm else None
                if owner is None:
                    E("ph-hatcher", rel, "patch xpath %r names no defName: cannot prove the egg has a Hatcher" % xp)
                elif owner not in inp["hatcher_defs"]:
                    E("ph-hatcher", rel, "%s (patched) has no CompProperties_Hatcher anywhere under src/" % owner)
                # gate: PatchOperationFindMod on this mod's display name
                chain, a = [], li
                while a is not None:
                    chain.append(a)
                    a = pm.get(a)
                if not any(x.get("Class") == "PatchOperationFindMod" and "RimMandrake: Proximity Hatch" in ET.tostring(x, encoding="unicode") for x in chain):
                    E("ph-gate", rel, "patch adds the proximity comp without PatchOperationFindMod on 'RimMandrake: Proximity Hatch'")
            key = (rel, owner)
            by_owner[key] = by_owner.get(key, 0) + 1
            # gate for defs of another mod
            if not patched and not rel.startswith(MOD + "/"):
                about = deps.get(mod_of(rel), "")
                hard = re.search(r"<modDependencies>.*?%s.*?</modDependencies>" % re.escape(PACKAGE), about, re.S) is not None
                if li.get("MayRequire") != PACKAGE and not hard:
                    E("ph-gate", rel, "%s uses the comp with neither MayRequire=\"%s\" on the <li> nor a hard modDependency in its About.xml" % (owner, PACKAGE))
        for (r, o), n in by_owner.items():
            if n > 1:
                E("ph-once", r, "%s carries %d proximity comps" % (o, n))
    counts["consumers"] = counts["consumers"]
    # kernel
    kern = next(((p, t) for p, t in inp["cs"].items() if p.endswith("Kernel/RM_ProximityHatchKernel.cs")), None)
    if kern is None:
        E("ph-kernel", MOD, "Kernel/RM_ProximityHatchKernel.cs not found")
    else:
        body = re.sub(r"//[^\n]*", "", kern[1])
        for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
            if bad in body:
                E("ph-kernel", kern[0], "contains '%s': the fuzz project compiles this file on plain net8.0" % bad)
        if not any('Include="Kernel\\RM_ProximityHatchKernel.cs"' in t for t in inp["csproj"].values()):
            E("ph-kernel", MOD, "the mod csproj does not compile Kernel\\RM_ProximityHatchKernel.cs (EnableDefaultCompileItems is false: it would build nothing)")
        comp = next((t for p, t in inp["cs"].items() if p.endswith("CompProximityHatch.cs")), "")
        for fn in ("ScanInterval", "Radius", "CountdownStep", "MayScan", "PickNearest", "IsFreshHatchling", "TicksNow"):
            if "RM_ProximityHatchKernel.%s(" % fn not in comp:
                E("ph-kernel", MOD, "CompProximityHatch no longer calls RM_ProximityHatchKernel.%s: the fuzz would be proving a copy" % fn)
    # settings
    st = next((t for p, t in inp["cs"].items() if p.endswith("RM_ProximityHatchMod.cs")), "")
    sc = re.sub(r"//[^\n]*", "", st)
    inits = dict((n, v) for n, v in re.findall(r"public static (?:bool|float|int) (\w+)\s*=\s*([^;]+);", sc))
    scribes = dict((n, v) for n, v in re.findall(r'Scribe_Values\.Look\(ref (\w+), "\w+", ([^)]+)\)', sc))
    keys = dict((n, k) for n, k in re.findall(r'Scribe_Values\.Look\(ref (\w+), "(\w+)"', sc))
    sliders = dict((n, (float(a), float(b))) for n, a, b in re.findall(r"(\w+) = list\.Slider\(\1, ([-\d.]+)f, ([-\d.]+)f\)", sc))
    for n, v in inits.items():
        counts["settings"] += 1
        if n not in scribes:
            E("ph-settings", MOD, "%s has a static default but is never Scribed (the setting would not persist)" % n)
            continue
        if keys.get(n) != n:
            E("ph-settings", MOD, "%s is Scribed under key %r, not its own name (renaming a key resets it for everyone)" % (n, keys.get(n)))
        if v.strip().rstrip("f") != scribes[n].strip().rstrip("f") and v.strip() != scribes[n].strip():
            E("ph-settings", MOD, "%s: static default %s but Scribe default %s" % (n, v.strip(), scribes[n].strip()))
        if n in sliders:
            lo, hi = sliders[n]
            d = float(v.strip().rstrip("f"))
            if not lo <= d <= hi:
                E("ph-settings", MOD, "%s default %s lies outside its slider range %s..%s" % (n, d, lo, hi))
    return errs, counts


def main(argv):
    inp = collect()
    errs, counts = check(inp)
    if counts["consumers"] == 0 or counts["settings"] < 4:
        print("LINT UNMEASURED: found %s - the walk is blind" % counts)
        return 2
    if "--quiet" not in argv:
        print("proximityhatch lint: %s" % ", ".join("%s=%s" % kv for kv in sorted(counts.items())))
    for e in errs:
        print(e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
