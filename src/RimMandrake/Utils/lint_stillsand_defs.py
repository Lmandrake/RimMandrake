#!/usr/bin/env python3
"""Offline lint of the Stillsand mod: XML defs/patches against its C# source (see lint_modpack_defs.py for the generic
checks, run against the events settings class) plus Stillsand-specific data checks:

  stillsand-leviathan  every RM_SandLeviathanExtension (this mod's muurrok incident AND the Utinni krayt attack): the pawnKind
                       is a PawnKindDef somewhere in src, biomes is non-empty, timings are positive, vibrationFactorPerDrill >= 0 and
                       maxVibrationFactor >= 1 (below 1 would CUT the odds), maxStayTicks > hardGroundGiveUpTicks (WARN otherwise: the
                       visit is bored before it can ever give up on hard ground)
  stillsand-gale       the RM_DuneGaleExtension: herald / gale weathers are WeatherDefs of this mod, fractions in [0,1], every range
                       ordered and non-negative, returnAliveChance in [0,1], emergence keys unique with positive weights, every
                       emergence row says something (things, corpses, a skeleton or a cave mouth)
  stillsand-sun        RM_CompProperties_SunPowered: minSunFactor in [0,1], kind is a known RM_SunTableKind, every noSunWeather is a
                       vanilla or this mod's WeatherDef; RM_CompProperties_SolarStill: ticksPerCycle > 0, feeds with positive
                       perCycle / litres, pearlLensDef defined; RM_CompProperties_Thumper: positive intervals and caps
  stillsand-settings   every settings class in Source (any `class X : ModSettings` or `static class *Settings`): each Scribe_Values key
                       is unique across ALL classes (two classes sharing a key clobber each other in the shared settings file), its
                       default equals the field initialiser, its field is declared; every slider range contains its field's default
  stillsand-kernel     every Source/Kernel/*.cs is in the mod csproj AND in the fuzz project (an unlisted kernel is unfuzzed)

    python3 src/RimMandrake/Utils/lint_stillsand_defs.py [--mod-dir <dir>] [--quiet]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_modpack_defs as L  # noqa: E402

SUN_KINDS = ("furnace", "lensBench", "oven", "still")
VANILLA_WEATHERS = {"Clear", "Fog", "Rain", "DryThunderstorm", "RainyThunderstorm", "FoggyRain", "SnowGentle", "SnowHard", "Sandstorm",
                    "Flashstorm", "Eclipse", "Aurora", "Heatwave", "ColdSnap", "VolcanicWinter", "ToxicFallout", "Unnatural"}


def _rng(text):
    m = re.match(r"^\s*(-?[\d.]+)\s*~\s*(-?[\d.]+)\s*$", text or "")
    return (float(m.group(1)), float(m.group(2))) if m else None


def _f(el, tag):
    t = el.findtext(tag)
    try:
        return float(t.strip()) if t is not None else None
    except ValueError:
        return None


def _g(el, tag, default):
    v = _f(el, tag)
    return default if v is None else v


def _all_defnames(kind):
    names = set()
    for xp in glob.glob(os.path.join(L.REPO, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        if os.sep + "obj" + os.sep in xp:
            continue
        try:
            root = ET.parse(xp).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.tag == kind and d.findtext("defName"):
                names.add(d.findtext("defName"))
    return names


def settings_checks(mod, E, W, n):
    keys = {}
    classes = 0
    alldecl = {}   # field -> (type, init) across ALL settings classes: a screen class may draw another class's field
    for p in glob.glob(os.path.join(mod, "Source", "**", "*.cs"), recursive=True):
        if os.sep + "SelfTest" + os.sep in p or os.sep + "obj" + os.sep in p:
            continue
        t0 = L.strip_comments(open(p, encoding="utf-8-sig", errors="replace").read())
        for t, nm, v in re.findall(r"public static (bool|float|int|string)\s+(\w+)\s*=\s*([^;]+);", t0):
            alldecl.setdefault(nm, (t, v.strip()))
    for p in sorted(glob.glob(os.path.join(mod, "Source", "**", "*.cs"), recursive=True)):
        if os.sep + "SelfTest" + os.sep in p or os.sep + "obj" + os.sep in p:
            continue
        txt = L.strip_comments(open(p, encoding="utf-8-sig", errors="replace").read())
        for sm in re.finditer(r"class\s+(\w+Settings)\b[^{]*\{", txt):
            cname = sm.group(1)
            body = txt[sm.end():]
            nxt = re.search(r"\n    (?:public |internal )?(?:static |sealed )?class\s", body)
            if nxt:
                body = body[:nxt.start()]
            decl = {nm: (t, v.strip()) for t, nm, v in re.findall(r"public (?:static )?(bool|float|int|string)\s+(\w+)\s*=\s*([^;]+);", body)}
            scribed = re.findall(r'Scribe_Values\.Look\(\s*ref\s+(\w+)\s*,\s*"(\w+)"\s*,\s*([^,)]*)[,)]', body)
            if not decl and not scribed:
                continue
            classes += 1
            norm = lambda v: v.strip().rstrip("f").lower()
            for fld, key, dflt in scribed:
                n["scribes"] += 1
                if fld not in decl:
                    E("stillsand-settings", f"{cname}: Scribe_Values.Look(ref {fld}) names a field that is not declared in the class")
                    continue
                if key in keys and keys[key] != cname + "." + fld:
                    E("stillsand-settings", f'key "{key}" is Scribed by both {keys[key]} and {cname}.{fld}')
                keys[key] = cname + "." + fld
                if norm(dflt) != norm(decl[fld][1]):
                    E("stillsand-settings", f"{cname}.{fld} initialises to {decl[fld][1]} but Scribes default {dflt.strip()}")
            for fld in decl:
                if fld not in [s[0] for s in scribed] and re.search(r"\b" + fld + r"\b", body.split("Expose")[0] if "Expose" in body else ""):
                    pass
            for m in re.finditer(r"\b(\w+)\s*=\s*(?:\(\w+\))?\s*(?:Mathf\.(?:Round|RoundToInt)\(\s*)?\w+\.Slider\(\s*\1\s*,\s*(-?[\d.]+)f?\s*,\s*(-?[\d.]+)f?\s*\)", body):
                fld, lo, hi = m.group(1), float(m.group(2)), float(m.group(3))
                d = decl.get(fld) or alldecl.get(fld)
                if d and d[0] in ("int", "float"):
                    try:
                        dv = float(d[1].rstrip("f"))
                    except ValueError:
                        continue
                    n["sliders"] += 1
                    if not (lo <= dv <= hi):
                        E("stillsand-settings", f"{cname}.{fld} defaults to {d[1]} but its slider only spans {lo}..{hi}")
    if classes < 5:
        E("stillsand-settings", f"only {classes} settings classes found in Source (expected the 8 the mod ships): the parser is blind")
    return classes


def extra(mod, E, W, defs_xml, patch_xml, defnames, ctx):
    n = {"leviathan": 0, "gale": 0, "sun": 0, "still": 0, "thumper": 0, "scribes": 0, "sliders": 0, "emergences": 0}
    docs = []
    for p in defs_xml + patch_xml + sorted(glob.glob(os.path.join(L.SRC, "..", "RimUtinni", "UtinniPatches", "Defs", "IncidentDefs", "*.xml"))):
        try:
            docs.append((p, ET.parse(p).getroot()))
        except ET.ParseError:
            pass
    kinds = _all_defnames("PawnKindDef")
    biomes = _all_defnames("BiomeDef")
    weathers = _all_defnames("WeatherDef") | VANILLA_WEATHERS
    things = _all_defnames("ThingDef")
    own_weathers = set()
    for p, root in docs:
        if os.sep + "Stillsand" + os.sep in p:
            for d in root:
                if d.tag == "WeatherDef" and d.findtext("defName"):
                    own_weathers.add(d.findtext("defName"))
    for p, root in docs:
        rel = os.path.relpath(p, L.SRC)
        for el in root.iter():
            cls = el.get("Class", "")
            if cls.endswith("RM_SandLeviathanExtension"):
                n["leviathan"] += 1
                pk = (el.findtext("pawnKind") or "").strip()
                if pk not in kinds:
                    E("stillsand-leviathan", f"{rel}: pawnKind {pk!r} is not a PawnKindDef in any mod (the incident can never fire)")
                bl = [b.text.strip() for b in el.findall("biomes/li") if b.text]
                if not bl:
                    E("stillsand-leviathan", f"{rel}: biomes is empty")
                for b in bl:
                    if b not in biomes:
                        W("stillsand-leviathan", f"{rel}: biome {b} is not a BiomeDef in this repo")
                for f in ("warningTicks", "maxStayTicks", "hardGroundGiveUpTicks", "beamCooldownTicks", "breachStaggerTicks"):
                    v = _f(el, f)
                    if v is not None and v <= 0:
                        E("stillsand-leviathan", f"{rel}: {f} = {v} <= 0")
                mv, pd = _f(el, "maxVibrationFactor"), _f(el, "vibrationFactorPerDrill")
                if mv is not None and mv < 1:
                    E("stillsand-leviathan", f"{rel}: maxVibrationFactor {mv} < 1 would CUT the incident odds")
                if pd is not None and pd < 0:
                    E("stillsand-leviathan", f"{rel}: vibrationFactorPerDrill {pd} < 0")
                ms, hg = _g(el, "maxStayTicks", 30000), _g(el, "hardGroundGiveUpTicks", 900)
                if ms <= hg:
                    W("stillsand-leviathan", f"{rel}: maxStayTicks {ms} <= hardGroundGiveUpTicks {hg}: the visit is always bored before it can give up on hard ground")
            if cls.endswith("RM_DuneGaleExtension"):
                n["gale"] += 1
                for f in ("heraldWeather", "galeWeather"):
                    w = (el.findtext(f) or "").strip()
                    if not w:
                        E("stillsand-gale", f"{rel}: {f} is empty")
                    elif w not in own_weathers and w not in weathers:
                        E("stillsand-gale", f"{rel}: {f} {w} is not a WeatherDef")
                for f in ("heraldFraction", "returnAliveChance", "roofStripChancePerSample", "crestDepth"):
                    v = _f(el, f)
                    if v is not None and not (0.0 <= v <= 1.0):
                        E("stillsand-gale", f"{rel}: {f} = {v} outside [0,1]")
                for f in ("abrasionDamage", "structureDamage", "carryCells", "carryBruise", "returnDays", "staticStunTicks", "glasscrustCells", "bloomCells"):
                    t = el.findtext(f)
                    if t is not None:
                        r = _rng(t)
                        if r is None or r[0] < 0 or r[0] > r[1]:
                            E("stillsand-gale", f"{rel}: {f} = {t} is not an ordered non-negative range")
                for f in ("abrasionMtbHours", "structureMtbHours", "carryMtbHours", "staticMtbHours", "wipeDepthDelta", "carryMaxBodySize"):
                    v = _f(el, f)
                    if v is not None and v <= 0:
                        E("stillsand-gale", f"{rel}: {f} = {v} <= 0")
                ek = []
                for em in el.findall("emergences/li"):
                    n["emergences"] += 1
                    key = (em.findtext("key") or "").strip()
                    if not key or key in ek:
                        E("stillsand-gale", f"{rel}: emergence key {key!r} is empty or duplicated (the per-row toggle cannot address it)")
                    ek.append(key)
                    w = _f(em, "weight")
                    if w is not None and w <= 0:
                        E("stillsand-gale", f"{rel}: emergence {key} weight {w} <= 0 (never chosen)")
                    if em.find("things") is None and em.find("corpses") is None and (em.findtext("skeleton") or "").strip().lower() != "true" \
                            and (em.findtext("caveMouth") or "").strip().lower() != "true":
                        E("stillsand-gale", f"{rel}: emergence {key} uncovers nothing")
                    holder = em.find("things")
                    for tg in (list(holder) if holder is not None else []):
                        if tg.tag.startswith(L.OUR_PREFIX) and tg.tag not in things:
                            E("stillsand-gale", f"{rel}: emergence {key} thing {tg.tag} is not a ThingDef of any mod")
            if cls.endswith("RM_CompProperties_SunPowered"):
                n["sun"] += 1
                v = _f(el, "minSunFactor")
                if v is not None and not (0.0 <= v <= 1.0):
                    E("stillsand-sun", f"{rel}: minSunFactor {v} outside [0,1]")
                k = (el.findtext("kind") or "furnace").strip()
                if k not in SUN_KINDS:
                    E("stillsand-sun", f"{rel}: kind {k} is not an RM_SunTableKind")
                for w in el.findall("noSunWeathers/li"):
                    if w.text and w.text.strip() not in weathers:
                        E("stillsand-sun", f"{rel}: noSunWeathers names {w.text.strip()}, not a WeatherDef")
            if cls.endswith("RM_CompProperties_SolarStill"):
                n["still"] += 1
                if _g(el, "ticksPerCycle", 6000) <= 0:
                    E("stillsand-sun", f"{rel}: ticksPerCycle <= 0")
                for fd in el.findall("feeds/li"):
                    if _g(fd, "perCycle", 1) <= 0 or _g(fd, "litres", 2) <= 0:
                        E("stillsand-sun", f"{rel}: a still feed has perCycle or litres <= 0")
                    if not (fd.findtext("defName") or "").strip():
                        E("stillsand-sun", f"{rel}: a still feed names no def")
                pl = (el.findtext("pearlLensDef") or "RM_PearlLens").strip()
                if pl not in things:
                    W("stillsand-sun", f"{rel}: pearlLensDef {pl} is not a ThingDef in this repo (the lens bonus never applies)")
            if cls.endswith("RM_CompProperties_Thumper"):
                n["thumper"] += 1
                for f in ("beatIntervalTicks", "maxCallsPerBeat", "wetTicks"):
                    v = _f(el, f)
                    if v is not None and v <= 0:
                        E("stillsand-sun", f"{rel}: thumper {f} = {v} <= 0")
                v = _f(el, "arriveRadius")
                if v is not None and v < 0:
                    E("stillsand-sun", f"{rel}: thumper arriveRadius {v} < 0")
    for tag, label in (("leviathan", "RM_SandLeviathanExtension"), ("gale", "RM_DuneGaleExtension"), ("sun", "RM_CompProperties_SunPowered"),
                       ("still", "RM_CompProperties_SolarStill"), ("thumper", "RM_CompProperties_Thumper")):
        if n[tag] == 0:
            E("stillsand-" + ("sun" if tag in ("still", "thumper") else tag), f"no {label} found in this mod's defs (wrong --mod-dir, or the lint is blind)")
    classes = settings_checks(mod, E, W, n)
    # kernels: in the mod csproj and in the fuzz project
    kdir = os.path.join(mod, "Source", "Kernel")
    fuzz = os.path.join(mod, "Source", "SelfTest", "Fuzz", "RimMandrakeStillsand.Fuzz.csproj")
    fz = open(fuzz, encoding="utf-8-sig").read() if os.path.exists(fuzz) else ""
    nk = 0
    for k in sorted(glob.glob(os.path.join(kdir, "*.cs"))):
        nk += 1
        base = os.path.basename(k)
        if base not in fz:
            E("stillsand-kernel", f"Kernel/{base} is not in the fuzz project (unfuzzed)")
        txt = open(k, encoding="utf-8-sig").read()
        if re.search(r"^\s*using (Verse|RimWorld|UnityEngine)", txt, flags=re.M):
            E("stillsand-kernel", f"Kernel/{base} references Verse/RimWorld/UnityEngine (a kernel must be engine-free)")
    if nk < 4:
        E("stillsand-kernel", f"only {nk} kernel files found")
    print(f"stillsand data: {n['leviathan']} leviathan ext, {n['gale']} gale ext ({n['emergences']} emergence rows), {n['sun']} sun-powered comps, "
          f"{n['still']} still comps, {n['thumper']} thumper comps, {classes} settings classes ({n['scribes']} scribes, {n['sliders']} sliders), {nk} kernels checked")


class _Glob:
    """lint_modpack_defs treats only a `SelfTest` path component as test code; this mod's older offline test lives in
    `SkeletonSelfTest`, which is test code too (it is not, and must not be, in the mod csproj)."""

    @staticmethod
    def glob(pattern, recursive=False):
        return [p for p in glob.glob(pattern, recursive=recursive) if os.sep + "SkeletonSelfTest" + os.sep not in p]


# Art the owner has ruled owed and that is not on disk yet: reported as WARN, never an ERROR.
OWED_ART = ("RM_Drazzik_Swimming",)  # LONGSHADE_SHEET_STRUCTURAL_RULINGS_1: the beneath-sand-waiting image, owner 2026-10-04


def main(argv):
    import io
    import contextlib
    L.glob = _Glob
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = L.run(argv, "Stillsand", "RM_StillsandEventsSettings", "RM_StillsandEventsMod.cs", "RM_Stillsand.csproj", "stillsand", extra=extra)
    out, errs = [], 0
    seen = set()
    for line in buf.getvalue().splitlines():
        if line.startswith("ERROR") and any(o in line for o in OWED_ART):
            if line in seen:
                continue
            seen.add(line)
            line = "WARN  owed-art:" + line[len("ERROR"):] + "  [art owed by ruling, not a code defect]"
        elif line.startswith("ERROR"):
            errs += 1
        out.append(line)
    summary = [l for l in out if " lint: " in l]
    for l in out:
        if "--quiet" in argv and l.startswith("WARN"):
            continue
        if " lint: " in l:
            continue
        print(l)
    warns = sum(1 for l in out if l.startswith("WARN"))
    if summary:
        head = summary[0].rsplit(",", 2)[0]
        print(f"{head}, {errs} ERROR, {warns} WARN")
    return 1 if errs else (rc if rc == 2 else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
